#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bidirectional pipe: live product ↔ external Mechanismus folder.

  out   live → ../mechanismus/<product>/
  in    work folder → <product>/mask_overlays/
  status / products

  python3 experiments/gpt-mask/mask_sync.py out --product pistol --rebuild
  python3 experiments/gpt-mask/mask_sync.py out --product mitrailleuse --rebuild
  python3 experiments/gpt-mask/mask_sync.py out --product gatling --rebuild
  python3 experiments/gpt-mask/mask_sync.py in --product pistol

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
from mask_map import MECHANISMUS_TEMPLATE_FILES  # noqa: E402
from product_lib import (  # noqa: E402
    label_to_live,
    list_products,
    live_to_stem,
    load_product,
)


TEMPLATE_SRC = os.path.join(HERE, "mechanismus_template")


def die(msg, code=1):
    sys.stderr.write("mask_sync: %s\n" % msg)
    sys.exit(code)


def cache_parts(product_id):
    return os.path.join(HERE, "cache", product_id, "parts")


def cache_manifest(product_id):
    return os.path.join(HERE, "cache", product_id, "manifest.json")


def rebuild_parts(product_id):
    env = os.environ.copy()
    env.setdefault("LANG", "C.UTF-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env["MASK_PRODUCT"] = product_id
    cmd = [
        "freecadcmd",
        "-c",
        "REPO=%r; PRODUCT=%r; exec(open(%r).read())"
        % (REPO, product_id, os.path.join(HERE, "pull_product.py")),
    ]
    print("mask_sync: rebuilding %s via freecadcmd…" % product_id, flush=True)
    r = subprocess.call(cmd, cwd=REPO, env=env)
    if r != 0:
        die("freecadcmd pull_product failed (exit %d)" % r)


def cmd_out(product_id, dest, rebuild):
    product = load_product(product_id)
    dest = os.path.abspath(dest or product["work_dir"])
    if os.path.abspath(dest) == REPO or dest.startswith(REPO + os.sep):
        die("refusing to write the work tree inside the live repo (%s)" % dest)
    if rebuild:
        rebuild_parts(product_id)
    parts_src = cache_parts(product_id)
    man_src = cache_manifest(product_id)
    # Profiles that extends another may reuse the parent's cache when not rebuilt yet.
    if (not os.path.isdir(parts_src) or not os.listdir(parts_src)) and product.get("extends"):
        parts_src = cache_parts(product["extends"])
        man_src = cache_manifest(product["extends"])
    if not os.path.isdir(parts_src) or not os.listdir(parts_src):
        die("no cache/%s/parts — run with --rebuild first" % product_id)
    if not os.path.isfile(man_src):
        die("missing cache manifest — run with --rebuild")

    if os.path.isdir(dest):
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

    with open(man_src, "r", encoding="utf-8") as f:
        import json as _json
        man = _json.load(f)
    man["product"] = product_id
    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as f:
        _json.dump(man, f, indent=2)
        f.write("\n")
    dest_parts = os.path.join(dest, "parts")
    shutil.copytree(parts_src, dest_parts)
    n = len([f for f in os.listdir(dest_parts) if f.endswith(".brep")])
    print("mask_sync out [%s] → %s  (%d parts)" % (product_id, dest, n))
    print("Open ONLY that folder as the GPT workspace.")


def _find_shell_brep(src, product, live_var):
    stem = live_to_stem(product).get(live_var)
    labels = [lab for lab, live in label_to_live(product).items() if live == live_var]
    candidates = []
    for lab in labels:
        candidates.append(os.path.join(src, "exports", lab + ".brep"))
        candidates.append(os.path.join(src, lab + ".brep"))
    if stem:
        candidates.append(os.path.join(src, "parts", stem + ".brep"))
    candidates.append(os.path.join(src, "parts", live_var + ".brep"))
    candidates.append(os.path.join(src, live_var + ".brep"))
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def cmd_in(product_id, src, only=None):
    product = load_product(product_id)
    src = os.path.abspath(src or product["work_dir"])
    if not os.path.isdir(src):
        die("work folder not found: %s" % src)
    overlay_dir = product["overlay_dir"]
    os.makedirs(overlay_dir, exist_ok=True)
    lives = tuple(p["live"] for p in product["shell"] if isinstance(p["live"], str))
    wanted = set(only) if only else set(lives)
    unknown = wanted - set(lives)
    if unknown:
        die("unknown live vars for %s: %s" % (product_id, ", ".join(sorted(unknown))))

    copied = []
    missing = []
    for live_var in lives:
        if live_var not in wanted:
            continue
        src_path = _find_shell_brep(src, product, live_var)
        if not src_path:
            missing.append(live_var)
            continue
        dst = os.path.join(overlay_dir, live_var + ".brep")
        shutil.copy2(src_path, dst)
        copied.append(live_var)
        print("  %s ← %s" % (live_var + ".brep", src_path))

    if not copied:
        die("no shell .brep found under %s" % src)

    print("mask_sync in [%s] → %s  (%d overlays)" % (product_id, overlay_dir, len(copied)))
    if missing:
        print("  unchanged: %s" % ", ".join(missing))
    print("Rebuild live model:")
    print("  MASK_PRODUCT=%s freecadcmd -c \"REPO='$PWD'; exec(open(%r).read())\""
          % (product_id, os.path.relpath(product["build_script"], REPO)))


def cmd_status(product_id):
    product = load_product(product_id)
    print("product: %s" % product_id)
    print("work: %s" % product["work_dir"])
    print("overlays: %s" % product["overlay_dir"])
    if os.path.isdir(product["overlay_dir"]):
        found = [f for f in sorted(os.listdir(product["overlay_dir"])) if f.endswith(".brep")]
        print("  %s" % (", ".join(found) if found else "(empty)"))
    else:
        print("  (missing)")
    parts = cache_parts(product_id)
    n = len([f for f in os.listdir(parts) if f.endswith(".brep")]) if os.path.isdir(parts) else 0
    print("cache parts: %d" % n)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    _products = list_products() or ["pistol", "mitrailleuse", "gatling"]

    def add_product_arg(sp):
        sp.add_argument(
            "--product", "-p",
            default=os.environ.get("MASK_PRODUCT", "pistol"),
            choices=_products,
            help="product profile (default: pistol or $MASK_PRODUCT)",
        )

    p_out = sub.add_parser("out", help="live → external Mechanismus folder")
    add_product_arg(p_out)
    p_out.add_argument("dest", nargs="?", default=None, help="override work folder")
    p_out.add_argument("--rebuild", action="store_true", help="run pull_product.py first")

    p_in = sub.add_parser("in", help="external folder → product mask_overlays")
    add_product_arg(p_in)
    p_in.add_argument("src", nargs="?", default=None)
    p_in.add_argument("--only", nargs="+", metavar="VAR")

    p_st = sub.add_parser("status", help="show work dir / overlays / cache")
    add_product_arg(p_st)

    sub.add_parser("products", help="list product ids")

    args = p.parse_args(argv)
    if args.cmd == "products":
        for pid in list_products():
            print(pid)
        return
    if args.cmd == "out":
        cmd_out(args.product, args.dest, args.rebuild)
    elif args.cmd == "in":
        cmd_in(args.product, args.src, args.only)
    elif args.cmd == "status":
        cmd_status(args.product)
    else:
        die("unknown command")


if __name__ == "__main__":
    main()
