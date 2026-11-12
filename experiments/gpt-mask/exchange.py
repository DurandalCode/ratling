# -*- coding: utf-8 -*-
"""
Interchange helpers for the Mechanismus pipe. Pure Python; FreeCAD is spawned only to convert STEP.

The work folder may carry each shell part as .brep or .step/.stp (the GPT side can write either).
For every live part the newest file wins, so a model that writes parts/<stem>.step is not shadowed
by an older exports/<Label>.brep.
"""

from __future__ import print_function

import hashlib
import json
import os
import shutil
import subprocess

FORMATS = (".brep", ".step", ".stp")

_CONVERT = (
    "import json, os, Part\n"
    "for src, dst in json.loads(os.environ['MASK_CONVERT']):\n"
    "    s = Part.Shape()\n"
    "    s.read(src)\n"
    "    if not s.Solids:\n"
    "        raise SystemExit('no solids in ' + src)\n"
    "    s.exportBrep(dst)\n"
    "    print('converted %s -> %s' % (src, dst))\n"
)


def _stems_for(product, live):
    stem = None
    labels = []
    for p in product["shell"]:
        if p["live"] == live:
            stem = p["stem"]
            labels.append(p["label"])
    return stem, labels


def work_candidates(work, product, live):
    """Every existing file of any format that may carry `live` in the work folder."""
    stem, labels = _stems_for(product, live)
    bases = []
    for lab in labels:
        bases.append(os.path.join(work, "exports", lab))
        bases.append(os.path.join(work, lab))
    if stem:
        bases.append(os.path.join(work, "parts", stem))
    bases.append(os.path.join(work, "parts", live))
    bases.append(os.path.join(work, live))
    out = []
    for b in bases:
        for ext in FORMATS:
            p = b + ext
            if os.path.isfile(p) and p not in out:
                out.append(p)
    return out


def newest(paths):
    return max(paths, key=lambda p: os.stat(p).st_mtime_ns) if paths else None


def find_work_shell(work, product, live):
    return newest(work_candidates(work, product, live))


def is_brep(path):
    return path.lower().endswith(".brep")


def same_bytes(a, b):
    try:
        if os.stat(a).st_size != os.stat(b).st_size:
            return False
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def to_brep(pairs):
    """Make each (src, dst) a .brep at dst: copy a .brep, convert STEP through freecadcmd in one call."""
    steps = []
    for src, dst in pairs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if is_brep(src):
            shutil.copy2(src, dst)
        else:
            steps.append((src, dst))
    if not steps:
        return
    env = os.environ.copy()
    env.setdefault("LANG", "C.UTF-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env["MASK_CONVERT"] = json.dumps(steps)
    r = subprocess.call(["freecadcmd", "-c", _CONVERT], env=env)
    if r != 0:
        raise RuntimeError("freecadcmd STEP -> BREP conversion failed (exit %d)" % r)
    for src, dst in steps:
        if not os.path.isfile(dst):
            raise RuntimeError("conversion produced no %s" % dst)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def ledger_path(cache_dir):
    return os.path.join(cache_dir, "ledger.json")


def load_ledger(cache_dir):
    try:
        with open(ledger_path(cache_dir), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def record(cache_dir, live, path):
    """Remember that this exact file content has crossed the pipe (out or in), per live part."""
    led = load_ledger(cache_dir)
    seen = led.setdefault(live, [])
    digest = sha(path)
    if digest not in seen:
        seen.append(digest)
    os.makedirs(cache_dir, exist_ok=True)
    with open(ledger_path(cache_dir), "w", encoding="utf-8") as f:
        json.dump(led, f, indent=2, sort_keys=True)
        f.write("\n")


def part_state(work, product, live, cache_dir, ledger=None):
    """How the newest work-folder file for `live` relates to what already crossed the pipe.

    Returns (path, state): 'absent' (nothing in work), 'synced' (its content was written by `out`
    or already taken by `in`) or 'edited' (a change that has not gone through `in` yet).
    """
    path = find_work_shell(work, product, live)
    if not path:
        return None, "absent"
    led = load_ledger(cache_dir) if ledger is None else ledger
    return path, ("synced" if sha(path) in led.get(live, ()) else "edited")


def edit_files(directory):
    """{stem: path} of the edits/<stem>.py files in a directory."""
    out = {}
    if os.path.isdir(directory):
        for name in sorted(os.listdir(directory)):
            if name.endswith(".py"):
                out[name[:-3]] = os.path.join(directory, name)
    return out


def edit_state(work, stem, cache_dir, ledger=None):
    """'absent', 'synced' or 'edited' for work/edits/<stem>.py, by the same ledger as the solids."""
    path = os.path.join(work, "edits", stem + ".py")
    if not os.path.isfile(path):
        return None, "absent"
    led = load_ledger(cache_dir) if ledger is None else ledger
    return path, ("synced" if sha(path) in led.get("edit:" + stem, ()) else "edited")
