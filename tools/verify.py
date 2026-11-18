#!/usr/bin/env python3
"""Judge one ticket: scope of the diff, generator report, measured bodies.

A ticket (tasks/NNN-*.md) starts with a small header between '---' lines:

    ---
    id: 001
    title: Thicken the upper shell along the hammer slot
    allowed:                      # files the worker may change (globs)
      - pistol/hammer_assembly.py
    run: pistol/hammer_assembly.py  # generator to execute in freecadcmd (optional)
    pre:                          # Python lines run before the generator (optional)
      - CHECKS = False
    expect:                       # substrings the output must contain (optional)
      - "[OK ] upper shell wall"
    measure:                      # bodies to measure; 'Name: lo..hi' bounds volume, mm^3
      - Frame_upper: 41000..45000
      - Frame_lower
    solids:                       # expected solid count per body (optional)
      - Frame_upper: 1
    ---

Run from the repository root:

    python3 tools/verify.py tasks/001-upper-shell.md            # full check
    python3 tools/verify.py tasks/001-upper-shell.md --baseline # also build HEAD, print deltas
    python3 tools/verify.py tasks/001-upper-shell.md --scope    # diff scope only, no FreeCAD

Prints one verdict line at the end: 'VERDICT: PASS' or 'VERDICT: FAIL (<reasons>)',
exit code 0 / 1. Log of the generator run goes to exports/verify/<id>.log.
Plain python3; FreeCAD is only called as a subprocess.
"""

import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALWAYS_FORBIDDEN = ["archive/*", "archive/**", "mitrailleuse/*", "mitrailleuse/**"]
ALWAYS_ALLOWED = ["tasks/*", "tasks/**"]          # the worker's own report
MAC_FC = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
MARK = "VERIFY_MEASURE "


def parse_ticket(path):
    """Read the '---' header: 'key: value' and '  - item' lists, '#' comments."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\s*---\n(.*?)\n---", text, re.S)
    if not m:
        sys.exit("ticket %s has no '---' header" % path)
    data, key = {}, None
    for raw in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", raw).rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"\s+-\s+(.*)$", line)
        if item and key:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(item.group(1).strip().strip('"').strip("'"))
            continue
        kv = re.match(r"([A-Za-z_]+):\s*(.*)$", line)
        if not kv:
            sys.exit("ticket header: cannot read line %r" % raw)
        key, val = kv.group(1), kv.group(2).strip().strip('"').strip("'")
        data[key] = val if val else []
    return data


def name_bounds(items):
    """'Name: lo..hi' / 'Name: n' / 'Name' -> {name: (lo, hi) or None}."""
    out = {}
    for it in items or []:
        name, _, rest = it.partition(":")
        rest = rest.strip()
        if not rest:
            out[name.strip()] = None
        elif ".." in rest:
            lo, hi = rest.split("..")
            out[name.strip()] = (float(lo), float(hi))
        else:
            out[name.strip()] = (float(rest), float(rest))
    return out


def changed_files():
    out = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    files = []
    for line in out.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ")[1]
        files.append(path.strip('"'))
    return files


def matches(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def check_scope(ticket):
    allowed = ticket.get("allowed") or []
    if isinstance(allowed, str):
        allowed = [allowed]
    problems = []
    files = changed_files()
    for f in files:
        if matches(f, ALWAYS_FORBIDDEN):
            problems.append("touched forbidden %s" % f)
        elif not matches(f, allowed + ALWAYS_ALLOWED):
            problems.append("touched %s (not in allowed)" % f)
    print("changed files: %s" % (", ".join(files) or "none"))
    return problems


def find_freecadcmd():
    for cand in (os.environ.get("FREECADCMD"), shutil.which("freecadcmd"), MAC_FC,
                 "/usr/local/bin/freecadcmd"):
        if cand and os.path.exists(cand):
            return cand
    return None


def build_script(repo, ticket, names):
    pre = ticket.get("pre") or []
    if isinstance(pre, str):
        pre = [pre]
    return "\n".join([
        "import json, traceback",
        "import FreeCAD as App",
        "REPO = %r" % repo,
        *pre,
        "_status = 'ok'",
        "try:",
        "    exec(open(REPO + '/' + %r).read())" % ticket["run"],
        "except SystemExit as e:",
        "    _status = 'exit %s' % e",
        "except Exception:",
        "    traceback.print_exc()",
        "    _status = 'error'",
        "def _find(n):",
        "    for d in App.listDocuments().values():",
        "        o = d.getObject(n) or (d.getObjectsByLabel(n) or [None])[0]",
        "        if o is not None and hasattr(o, 'Shape'):",
        "            return o",
        "_m = {'_status': _status}",
        "for n in %r:" % list(names),
        "    o = _find(n)",
        "    if o is None:",
        "        _m[n] = None; continue",
        "    s = o.Shape",
        "    b = s.BoundBox",
        "    _m[n] = dict(volume=round(s.Volume, 1), solids=len(s.Solids), valid=s.isValid(),",
        "                 bbox=[round(v, 2) for v in (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)])",
        "print(%r + json.dumps(_m), flush=True)" % MARK,
    ])


def run_generator(fc, repo, ticket, names, log_path):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(build_script(repo, ticket, names))
        script = f.name
    env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")
    try:
        proc = subprocess.run([fc, "-c", "exec(open(%r).read())" % script], cwd=repo, env=env,
                              capture_output=True, text=True, timeout=1800)
    finally:
        os.unlink(script)
    out = proc.stdout + proc.stderr
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    open(log_path, "w", encoding="utf-8").write(out)
    meas = None
    for line in out.splitlines():
        if line.startswith(MARK):
            meas = json.loads(line[len(MARK):])
    return out, meas


def baseline(fc, ticket, names):
    """Build the same ticket on a clean checkout of HEAD; return its measurements."""
    tmp = tempfile.mkdtemp(prefix="ratling-head-")
    wt = os.path.join(tmp, "repo")
    subprocess.run(["git", "worktree", "add", "--detach", wt, "HEAD"], cwd=ROOT,
                   capture_output=True, check=True)
    try:
        _, meas = run_generator(fc, wt, ticket, names,
                                os.path.join(ROOT, "exports", "verify", "%s.head.log" % ticket.get("id", "x")))
        return meas
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ticket = parse_ticket(argv[0])
    tid = ticket.get("id", os.path.splitext(os.path.basename(argv[0]))[0])
    print("ticket %s: %s" % (tid, ticket.get("title", "")))
    problems = check_scope(ticket)

    if "--scope" in argv or not ticket.get("run"):
        if not ticket.get("run"):
            print("no 'run:' in ticket, FreeCAD part skipped")
        return verdict(problems)

    fc = find_freecadcmd()
    if not fc:
        problems.append("freecadcmd not found (sh tools/install_freecad.sh, or set FREECADCMD)")
        return verdict(problems)

    volumes = name_bounds(ticket.get("measure"))
    solids = name_bounds(ticket.get("solids"))
    names = list(dict.fromkeys(list(volumes) + list(solids)))
    log_path = os.path.join(ROOT, "exports", "verify", "%s.log" % tid)
    print("running %s in %s ..." % (ticket["run"], fc), flush=True)
    out, meas = run_generator(fc, ROOT, ticket, names, log_path)
    print("log: %s" % os.path.relpath(log_path, ROOT))

    fails = [l.strip() for l in out.splitlines() if "[FAIL]" in l]
    for l in fails[:20]:
        print("  " + l)
    if fails:
        problems.append("%d [FAIL] lines in report" % len(fails))
    if meas is None:
        problems.append("generator crashed before measuring (see log tail below)")
        print("\n".join(out.splitlines()[-25:]))
        return verdict(problems)
    if meas["_status"] != "ok":
        problems.append("generator ended with %s" % meas["_status"])
        if meas["_status"] == "error":
            print("\n".join(l for l in out.splitlines() if l.strip())[-3000:])
    for exp in ticket.get("expect") or []:
        if exp not in out:
            problems.append("missing expected output %r" % exp)

    head = baseline(fc, ticket, names) if "--baseline" in argv else None
    for n in names:
        m = meas.get(n)
        if m is None:
            problems.append("body %s not found in the document" % n)
            continue
        line = "  %-24s V=%10.1f mm3  solids=%d  valid=%s  bbox=%s" % (
            n, m["volume"], m["solids"], m["valid"], m["bbox"])
        if head and head.get(n):
            dv = m["volume"] - head[n]["volume"]
            line += "  dV=%+.1f (HEAD %.1f, solids %d)" % (dv, head[n]["volume"], head[n]["solids"])
        print(line)
        if not m["valid"]:
            problems.append("%s shape is not valid" % n)
        b = volumes.get(n)
        if b and not (b[0] <= m["volume"] <= b[1]):
            problems.append("%s volume %.1f outside %g..%g" % (n, m["volume"], b[0], b[1]))
        b = solids.get(n)
        if b and not (b[0] <= m["solids"] <= b[1]):
            problems.append("%s has %d solids, expected %g..%g" % (n, m["solids"], b[0], b[1]))
    return verdict(problems)


def verdict(problems):
    if problems:
        print("VERDICT: FAIL (%s)" % "; ".join(problems))
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
