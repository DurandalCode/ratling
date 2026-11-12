#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bidirectional pipe: live pistol ↔ GPT mask folder (fixture D layout).

  out   live → work folder (rebuild parts optional)
  in    work folder → pistol/mask_overlays/*.brep
  status  show overlays and whether work folder is stale

Examples:

  python3 experiments/gpt-mask/mask_sync.py out              # → ../mechanismus (or $MECHANISMUS)
  python3 experiments/gpt-mask/mask_sync.py out --rebuild
  python3 experiments/gpt-mask/mask_sync.py in
  freecadcmd -c "REPO='$PWD'; exec(open('pistol/hammer_assembly.py').read())"

Keep this script in the live repo — do not copy it into the external work folder.
"""

from __future__ import print_function

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
sys.path.insert(0, HERE)
from mask_map import (  # noqa: E402
    D_NAME_TO_LIVE,
    LIVE_TO_D_STEM,
    MECHANISMUS_TEMPLATE_FILES,
    SHELL_OVERLAY_VARS,
    default_mask_dir,
)

D_SRC = os.path.join(HERE, "D_full_mech")
TEMPLATE_SRC = os.path.join(HERE, "mechanismus_template")
OVERLAY_DIR = os.path.join(REPO, "pistol", "mask_overlays")


def die(msg, code=1):
    sys.stderr.write("mask_sync: %s\n" % msg)
    sys.exit(code)


def rebuild_parts():
    env = os.environ.copy()
    env.setdefault("LANG", "C.UTF-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    cmd = [
        "freecadcmd",
        "-c",
        "REPO=%r; exec(open(%r).read())" % (REPO, os.path.join(HERE, "pull_real_shell.py")),
    ]
    print("mask_sync: rebuilding parts via freecadcmd…", flush=True)
    r = subprocess.call(cmd, cwd=REPO, env=env)
    if r != 0:
        die("freecadcmd pull_real_shell failed (exit %d)" % r)


def cmd_out(dest, rebuild):
    dest = os.path.abspath(dest or default_mask_dir())
    if os.path.abspath(dest) == os.path.abspath(REPO) or dest.startswith(os.path.abspath(REPO) + os.sep):
        die("refusing to write the work tree inside the live repo (%s)" % dest)
    if rebuild:
        rebuild_parts()
    parts_src = os.path.join(D_SRC, "parts")
    if not os.path.isdir(parts_src) or not os.listdir(parts_src):
        die("no D_full_mech/parts — run with --rebuild first")

    if os.path.isdir(dest):
        # Replace contents but keep dest path (user may have the folder open)
        for name in os.listdir(dest):
            if name in (".", ".."):
                continue
            p = os.path.join(dest, name)
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    else:
        os.makedirs(dest)

    for name in MECHANISMUS_TEMPLATE_FILES:
        src = os.path.join(TEMPLATE_SRC, name)
        if not os.path.isfile(src):
            die("missing template file: %s" % src)
        shutil.copy2(src, os.path.join(dest, name))

    dest_parts = os.path.join(dest, "parts")
    shutil.copytree(parts_src, dest_parts)
    n = len([f for f in os.listdir(dest_parts) if f.endswith(".brep")])
    print("mask_sync out → %s  (%d parts + mechanismus template)" % (dest, n))
    print("Open ONLY that folder as the GPT workspace.")


def _find_shell_brep(src, live_var):
    """Return path to an edited shell solid for live_var, or None."""
    stem = LIVE_TO_D_STEM[live_var]
    # Prefer FreeCAD export names, then parts/ stems, then overlay-style live names
    d_names = [n for n, v in D_NAME_TO_LIVE.items() if v == live_var]
    candidates = []
    for n in d_names:
        candidates.append(os.path.join(src, "exports", n + ".brep"))
        candidates.append(os.path.join(src, n + ".brep"))
    candidates.append(os.path.join(src, "parts", stem + ".brep"))
    candidates.append(os.path.join(src, "parts", live_var + ".brep"))
    candidates.append(os.path.join(src, live_var + ".brep"))
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def cmd_in(src, only=None):
    src = os.path.abspath(src or default_mask_dir())
    if not os.path.isdir(src):
        die("work folder not found: %s" % src)
    os.makedirs(OVERLAY_DIR, exist_ok=True)
    wanted = set(only) if only else set(SHELL_OVERLAY_VARS)
    unknown = wanted - set(SHELL_OVERLAY_VARS)
    if unknown:
        die("unknown live vars: %s" % ", ".join(sorted(unknown)))

    copied = []
    missing = []
    for live_var in SHELL_OVERLAY_VARS:
        if live_var not in wanted:
            continue
        src_path = _find_shell_brep(src, live_var)
        if not src_path:
            missing.append(live_var)
            continue
        dst = os.path.join(OVERLAY_DIR, live_var + ".brep")
        shutil.copy2(src_path, dst)
        copied.append((live_var, src_path, dst))
        print("  %s ← %s" % (live_var + ".brep", src_path))

    if not copied:
        die(
            "no shell .brep found under %s\n"
            "After GPT edits, export Shell_tray (etc.) to exports/*.brep "
            "or overwrite parts/tray.brep" % src
        )

    print("mask_sync in → %s  (%d overlays)" % (OVERLAY_DIR, len(copied)))
    if missing and only:
        print("  missing: %s" % ", ".join(missing))
    elif missing:
        print("  unchanged (no file in work folder): %s" % ", ".join(missing))
    print("Rebuild live model to apply:")
    print("  freecadcmd -c \"REPO='$PWD'; CHECKS=False; exec(open('pistol/hammer_assembly.py').read())\"")


def cmd_status():
    print("mechanismus: %s" % default_mask_dir())
    print("  ($MECHANISMUS or <repo-parent>/mechanismus)")
    print("overlays: %s" % OVERLAY_DIR)
    if not os.path.isdir(OVERLAY_DIR):
        print("  (none)")
    else:
        found = [f for f in sorted(os.listdir(OVERLAY_DIR)) if f.endswith(".brep")]
        if not found:
            print("  (empty)")
        for f in found:
            print("  %s" % f)
    parts = os.path.join(D_SRC, "parts")
    n = len([f for f in os.listdir(parts) if f.endswith(".brep")]) if os.path.isdir(parts) else 0
    print("D_full_mech/parts: %d brep" % n)
    ext = default_mask_dir()
    if os.path.isdir(os.path.join(ext, "parts")):
        en = len([f for f in os.listdir(os.path.join(ext, "parts")) if f.endswith(".brep")])
        print("external parts: %d brep (%s)" % (en, ext))
    else:
        print("external parts: (missing — run: mask_sync out [--rebuild])")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_out = sub.add_parser("out", help="live → external Mechanismus folder")
    p_out.add_argument(
        "dest",
        nargs="?",
        default=None,
        help="work folder (default: $MECHANISMUS or <repo-parent>/mechanismus)",
    )
    p_out.add_argument("--rebuild", action="store_true", help="run pull_real_shell.py first")

    p_in = sub.add_parser("in", help="external GPT folder → pistol/mask_overlays")
    p_in.add_argument(
        "src",
        nargs="?",
        default=None,
        help="work folder (default: same as out)",
    )
    p_in.add_argument(
        "--only",
        nargs="+",
        metavar="VAR",
        help="limit to live vars, e.g. frame_lower grip_left",
    )

    sub.add_parser("status", help="list overlays and default mask dir")

    args = p.parse_args(argv)
    if args.cmd == "out":
        cmd_out(args.dest, args.rebuild)
    elif args.cmd == "in":
        cmd_in(args.src, args.only)
    elif args.cmd == "status":
        cmd_status()
    else:
        die("unknown command")


if __name__ == "__main__":
    main()
