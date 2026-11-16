#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bidirectional pipe: live Python sources <-> neutral-named copies in an external work folder.

  out     live -> ../mechanismus/   renamed copies of the product's generators
  in      work folder -> live                 reverse-renamed, merged line by line
  status  per file: edited in work / changed in live since the last crossing
  products

Both directions are 3-way text merges (git merge-file) against what crossed last time, so a line
edited on one side and untouched on the other simply moves; the same line edited on both sides is a
conflict and nothing is written for that file. Renaming never changes the line count (rename.py).
Russian words are dropped on the way out; they stay in the live files and survive `in`.

Pistol only: on `out` the geometry GPT sees is obfuscated (solid stack instead of the hollow
exhaust unit, one drum instead of six tubes, external wires instead of internal hose runs).
Those context files are never taken back by `in`; only the housing file is editable.

Gatling stand: on `out` the imported coax module is replaced by its outer solids (the real
nose, flange, ears, tube, yoke and rods, as geometry, without the stack source). The stand
file is editable; the station, that form and the shared libraries are context and are not
taken back. The slot, the stroke and the marble size stay as drawn, so a basket added on the
stand fits the live station.

  python3 experiments/gpt-mask/mask_sync.py out -p pistol
  python3 experiments/gpt-mask/mask_sync.py in  -p pistol

Keep this script in the live repo; do not copy it into the external work folder.
"""

from __future__ import print_function

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
sys.path.insert(0, HERE)
import rename  # noqa: E402
import obfuscate_gatling  # noqa: E402
import obfuscate_pistol  # noqa: E402
from product_lib import list_products, load_product  # noqa: E402

_OBFUSCATORS = {
    "pistol": obfuscate_pistol,
    "gatling": obfuscate_gatling,
}

PISTOL_README = """# Mechanismus

Cosplay prop for a costume: a handheld rotary piece with a printed shell around a drive pack.
The whole mechanism is in this folder (shell + drive). Plain FreeCAD Python — run a generator,
read its report, edit the files in place.

What you are looking at:

- The drive drum is a **solid cylinder** on the axle — the costume's rotary magazine look.
- The pack behind the drum is a **solid block** — the drive / battery housing for the build.
- The short leads that leave the shell are **wires for the costume light show** (LEDs and effects
  on the outfit).

## Run

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
{runs}
```

Every line printed as `[OK ]` / `[FAIL]` is a check; `[FAIL]` means the change broke something.
Output goes to `exports/`.

## Rules

- Edit the existing files in place. Do not rename, add or delete files.
- Keep line endings and the overall line structure; make local changes, do not reformat or reflow
  untouched code (changes are exchanged as line diffs).
- Generators run each other by relative path; keep those paths as they are.
- Keep the vocabulary of the existing code for names you do not need to change.
- Prefer editing the printed housing (tray, cover, grips, bail). Leave the solid drum, the solid
  pack and the light-show wires alone unless the task says otherwise — they are the prop's
  drive stand-ins.
"""

GATLING_README = """# Mechanismus

Cosplay prop for a costume: one gate of a marble machine, held up by two small printed feet.
Plain FreeCAD Python — run the stand generator, read its report, edit the files in place.

## Legend

A marble machine. Marbles wait in a basket above the gate. The carriage rides two rails.
Pull it back and one soft marble drops from +Y into the open slot. Push it forward and the
nose sets that marble onto the spindle, the track this gate feeds. The bought block under
the rails is the cue switch: press its tip and the gate lets the marble go. The same gate
repeats around the rotor. This folder is the one gate, on its stand.

What you are looking at:

- The stand is two feet under the rails. This is the printed piece to reshape.
- The carriage slides on the rails. Closed, a nose fills the slot. Open, there is room for one marble.
- A top basket for the marbles belongs over that open slot.
- The pack on the carriage is the costume's drive housing. The cue switch hangs under the rails.

## Run

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
{runs}
```

Every line printed as `[OK ]` / `[FAIL]` is a check; `[FAIL]` means the change broke something.
Output goes to `exports/`.

## Rules

- Edit the stand file in place. Do not rename, add or delete files.
- Keep line endings and the overall line structure; make local changes, do not reformat or reflow
  untouched code (changes are exchanged as line diffs).
- Generators run each other by relative path; keep those paths as they are.
- Keep the vocabulary of the existing code for names you do not need to change.
- Put the basket on the stand. Leave the sliding station and the drive housing alone — they are the
  prop's drive stand-ins.
"""

GENERIC_README = """# Mechanismus

Printed costume prop. Plain FreeCAD Python — run a generator, read its report, edit the files in place.

## Run

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
{runs}
```

Every line printed as `[OK ]` / `[FAIL]` is a check; `[FAIL]` means the change broke something.
Output goes to `exports/`.

## Rules

- Edit the existing files in place. Do not rename, add or delete files.
- Keep line endings and the overall line structure; make local changes, do not reformat or reflow
  untouched code (changes are exchanged as line diffs).
- Generators run each other by relative path; keep those paths as they are.
- Keep the vocabulary of the existing code for names you do not need to change.
"""


def work_readme(product_id, runs):
    if product_id == "pistol":
        body = PISTOL_README
    elif product_id == "gatling":
        body = GATLING_README
    else:
        body = GENERIC_README
    return body.format(runs=runs)


def die(msg, code=1):
    sys.stderr.write("mask_sync: %s\n" % msg)
    sys.exit(code)


def cache_dir(product_id):
    return os.path.join(HERE, "cache", product_id)


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def read_opt(path):
    return read(path) if os.path.isfile(path) else None


def merge3(ours, base, theirs):
    """3-way line merge; returns (text, number of conflicts)."""
    tmp = tempfile.mkdtemp(prefix="mask_merge_")
    try:
        paths = []
        for name, text in (("ours", ours), ("base", base), ("theirs", theirs)):
            p = os.path.join(tmp, name)
            write(p, text)
            paths.append(p)
        r = subprocess.run(["git", "merge-file", "-p"] + paths, stdout=subprocess.PIPE)
        if r.returncode < 0 or r.returncode > 127:
            die("git merge-file failed (exit %d)" % r.returncode)
        return r.stdout.decode("utf-8"), r.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class Side(object):
    """Paths and saved state of one product: live files, work copies, and the last-crossed bases."""

    def __init__(self, product_id, work=None):
        self.product = load_product(product_id)
        self.id = product_id
        self.names = rename.load_names()
        self.work = os.path.abspath(work or self.product["work_dir"])
        if self.work == REPO or self.work.startswith(REPO + os.sep):
            die("refusing to use a work folder inside the live repo (%s)" % self.work)
        self.files = rename.closure(self.product["roots"])
        if not self.files:
            die("no source files found for %s" % product_id)
        self.cache = cache_dir(product_id)

    def npath(self, rel):
        return rename.forward_path(rel, self.names)

    def live(self, rel):
        return os.path.join(REPO, rel)

    def wfile(self, rel):
        return os.path.join(self.work, self.npath(rel))

    def neutral_base(self, rel):
        return os.path.join(self.cache, "neutral_base", self.npath(rel))

    def fwd(self, text):
        return rename.forward(text, self.names)

    def rev(self, text):
        return rename.reverse(text, self.names)

    def obfuscator(self):
        if not self.product.get("obfuscate"):
            return None
        return _OBFUSCATORS.get(self.id)

    def obfuscate(self):
        return self.obfuscator() is not None

    def listed(self, key):
        return self.product.get(key) or []

    def guards_edits(self):
        """True when `in` may take only the files listed as editable."""
        return bool(self.listed("editable")) or self.obfuscate()

    def is_editable(self, rel):
        editable = self.listed("editable")
        if editable:
            return rel in editable
        if self.obfuscate():
            return obfuscate_pistol.is_editable(rel)
        return True

    def is_context(self, rel):
        if self.listed("context") or self.listed("editable"):
            return rel in self.listed("context")
        if self.obfuscate():
            return obfuscate_pistol.is_context(rel)
        return False

    def expose(self, rel, live_text):
        """Live text as written to the work folder: product rewrite, then rename."""
        text = live_text
        ob = self.obfuscator()
        if ob is not None:
            text = ob.apply(rel, text)
        return self.fwd(text)

    def take_on_in(self, rel):
        if self.guards_edits():
            return self.is_editable(rel)
        return True

    def save_base(self, rel, neutral_text):
        write(self.neutral_base(rel), neutral_text)

    def commands(self, work_side):
        pre = "; ".join("%s=%r" % kv for kv in sorted(self.product["build_pre"].items()))
        out = []
        for root in self.product["roots"]:
            rel = self.npath(root) if work_side else root
            line = "freecadcmd -c \"REPO='$PWD'; %sexec(open('%s').read())\"" % (pre + "; " if pre else "", rel)
            out.append(self.fwd(line) if work_side else line)
        return out


def cmd_out(product_id, dest, force):
    s = Side(product_id, dest)
    texts = [read(s.live(f)) for f in s.files]
    problems = rename.check_table(s.names, texts + list(s.files))
    left = []
    for f, t in zip(s.files, texts):
        left += ["%s: %s" % (f, w) for w in rename.leftovers(s.fwd(t) + "\n" + s.npath(f), s.names)]
    if problems or left:
        die("names.json does not cover these sources:\n  %s" % "\n  ".join(problems + left))
    for f, t in zip(s.files, texts):
        if s.rev(s.fwd(t)) != rename.strip_russian(t):
            die("rename is not reversible for %s" % f)
    ob = s.obfuscator()
    if ob is not None:
        try:
            for f, t in zip(s.files, texts):
                ob.apply(f, t)
        except ValueError as e:
            die(str(e))

    os.makedirs(s.work, exist_ok=True)
    known = {s.npath(f) for f in s.files} | {"README.md"}
    for root, dirs, names in os.walk(s.work):
        dirs[:] = [d for d in dirs if d not in ("exports", "__pycache__")]
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), s.work).replace(os.sep, "/")
            if n.endswith((".py", ".json")) and rel not in known:
                print("  notice: %s is not one of this product's files (another product shares the folder?)" % rel)
    conflicts, wrote, kept, merged = [], 0, [], []
    for f, live_now in zip(s.files, texts):
        fwd = s.expose(f, live_now)
        wpath = s.wfile(f)
        work_now = read_opt(wpath)
        nb = read_opt(s.neutral_base(f))
        # Context placeholders are always refreshed from live; GPT edits there are discarded.
        if s.is_context(f):
            if work_now != fwd:
                write(wpath, fwd)
                wrote += 1
            s.save_base(f, fwd)
            continue
        if work_now is None or force or work_now == fwd:
            if work_now != fwd:
                write(wpath, fwd)
                wrote += 1
            s.save_base(f, fwd)
        elif nb is None:
            conflicts.append("%s: work copy exists but was never synced (use --force to overwrite)" % s.npath(f))
        elif work_now == nb:
            write(wpath, fwd)
            wrote += 1
            s.save_base(f, fwd)
        elif fwd == nb:
            kept.append(s.npath(f))
        else:
            text, n = merge3(work_now, nb, fwd)
            if n:
                conflicts.append("%s: %d conflict(s) between work edits and live changes" % (s.npath(f), n))
            else:
                write(wpath, text)
                merged.append(s.npath(f))
                s.save_base(f, fwd)

    write(os.path.join(s.work, "README.md"), work_readme(product_id, "\n".join(s.commands(True))))

    print("mask_sync out [%s] → %s  (%d files: %d written, %d merged, %d with pending edits kept)"
          % (product_id, s.work, len(s.files), wrote, len(merged), len(kept)))
    for m in merged:
        print("  merged live changes into %s" % m)
    for k in kept:
        print("  kept %s (edited here, live unchanged: run `in`)" % k)
    if conflicts:
        sys.stderr.write("not written:\n  %s\n" % "\n  ".join(conflicts))
        sys.exit(1)
    print("Open ONLY that folder as the GPT workspace.")


def cmd_in(product_id, src):
    s = Side(product_id, src)
    if not os.path.isdir(s.work):
        die("work folder not found: %s" % s.work)
    plan, errors, same, notes = [], [], 0, []
    for f in s.files:
        wpath = s.wfile(f)
        work_now = read_opt(wpath)
        nb = read_opt(s.neutral_base(f))
        if not s.take_on_in(f):
            if work_now is not None and nb is not None and work_now != nb:
                print("  ignored %s: not editable" % s.npath(f))
            same += 1
            continue
        if work_now is None or nb is None or work_now == nb:
            same += 1
            continue
        cand = s.rev(work_now)
        base_cand = s.rev(nb)
        live_now = read(s.live(f))
        if f.endswith(".py"):
            try:
                compile(cand, f, "exec")
            except SyntaxError as e:
                errors.append("%s: syntax error line %s: %s" % (s.npath(f), e.lineno, e.msg))
                continue
        if live_now == base_cand:
            new = cand
        else:
            new, n = merge3(live_now, base_cand, cand)
            if n:
                errors.append("%s: %d conflict(s) between your edits and live changes since `out`" % (s.npath(f), n))
                continue
        added = rename.vocabulary([cand]) - rename.vocabulary([base_cand])
        notes.append((f, sorted(added), sorted(w for w in added if w in s.names["words"])))
        plan.append((f, new, work_now))

    known = {s.npath(f) for f in s.files}
    for root, dirs, names in os.walk(s.work):
        dirs[:] = [d for d in dirs if d not in ("exports", "__pycache__")]
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), s.work).replace(os.sep, "/")
            if n.endswith((".py", ".json")) and rel not in known:
                print("  ignored %s: not one of the product's files" % rel)

    if errors:
        die("nothing was taken:\n  %s" % "\n  ".join(errors))
    if not plan:
        print("mask_sync in [%s]: no edits in %s" % (product_id, s.work))
        return
    for f, new, work_now in plan:
        write(s.live(f), new)
        s.save_base(f, work_now)
        print("  %s ← %s" % (f, s.npath(f)))
    print("mask_sync in [%s]: %d file(s) taken" % (product_id, len(plan)))
    for f, added, live_words in notes:
        if added:
            print("  new words in %s: %s" % (f, ", ".join(added[:40]) + (" …" if len(added) > 40 else "")))
        if live_words:
            print("  WARNING %s: live-vocabulary words written on the work side (%s); the next `out` will rename them"
                  % (f, ", ".join(live_words)))
    if any(a for _, a, _ in notes):
        print("Review the new words: add any that reveal the project to names.json (see AGENTS.md).")
    print("Rebuild the live model:")
    for c in s.commands(False):
        print("  " + c)


def cmd_status(product_id):
    s = Side(product_id)
    print("product: %s" % product_id)
    print("work: %s" % s.work)
    for f in s.files:
        work_now = read_opt(s.wfile(f))
        nb = read_opt(s.neutral_base(f))
        if work_now is None or nb is None:
            state = "not synced (run `out`)"
        else:
            parts = []
            if work_now != nb:
                parts.append("edited in work (run `in`)")
            if s.expose(f, read(s.live(f))) != nb:
                parts.append("live changed since last crossing (run `out`)")
            state = ", ".join(parts) or "in sync"
        tag = ""
        if s.guards_edits():
            if s.is_editable(f):
                tag = " [editable]"
            elif s.is_context(f):
                tag = " [context]"
        print("  %-44s %s%s" % (f, state, tag))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    products = list_products()

    def add_product(sp):
        sp.add_argument("--product", "-p", default=os.environ.get("MASK_PRODUCT", "pistol"),
                        choices=products, help="product profile (default: pistol or $MASK_PRODUCT)")

    p_out = sub.add_parser("out", help="live → external work folder (merges live changes into pending edits)")
    add_product(p_out)
    p_out.add_argument("dest", nargs="?", default=None, help="override work folder")
    p_out.add_argument("--force", action="store_true", help="overwrite the work files, dropping pending edits")
    p_in = sub.add_parser("in", help="external work folder → live files")
    add_product(p_in)
    p_in.add_argument("src", nargs="?", default=None)
    p_st = sub.add_parser("status", help="per file sync state")
    add_product(p_st)
    sub.add_parser("products", help="list product ids")

    args = p.parse_args(argv)
    if args.cmd == "products":
        for pid in products:
            print(pid)
    elif args.cmd == "out":
        cmd_out(args.product, args.dest, args.force)
    elif args.cmd == "in":
        cmd_in(args.product, args.src)
    else:
        cmd_status(args.product)


if __name__ == "__main__":
    main()
