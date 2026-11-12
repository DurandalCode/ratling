# -*- coding: utf-8 -*-
"""
Build a product and dump shell (+ optional drive) solids into
experiments/gpt-mask/cache/<product>/parts/*.brep and write manifest.json.

    freecadcmd -c "REPO='$PWD'; PRODUCT='pistol'; exec(open('experiments/gpt-mask/pull_product.py').read())"

Monorepo only.
"""

from __future__ import print_function

import json
import os
import shutil
import sys

import FreeCAD as App

try:
    REPO
except NameError:
    REPO = os.getcwd()
try:
    PRODUCT
except NameError:
    PRODUCT = os.environ.get("MASK_PRODUCT", "pistol")

sys.path.insert(0, os.path.join(REPO, "experiments", "gpt-mask"))
from product_lib import load_product, manifest_parts  # noqa: E402

product = load_product(PRODUCT)
CACHE = os.path.join(REPO, "experiments", "gpt-mask", "cache", product["id"])
PARTS = os.path.join(CACHE, "parts")
if os.path.isdir(PARTS):
    shutil.rmtree(PARTS)
os.makedirs(PARTS)


def resolve(ns, live):
    if isinstance(live, list):
        cur = ns
        for key in live:
            if key not in cur:
                return None
            cur = cur[key]
        return cur
    return ns.get(live)


def write_brep(shape, stem):
    path = os.path.join(PARTS, stem + ".brep")
    shape.exportBrep(path)
    vol = sum(s.Volume for s in shape.Solids) if shape.Solids else 0.0
    print("  %s.brep  vol=%.0f" % (stem, vol), flush=True)
    return path


def exec_script(rel, pre=None):
    g = {"REPO": REPO}
    if pre:
        g.update(pre)
    # FreeCAD scripts often expect CHECKS etc. in globals of exec
    path = os.path.join(REPO, rel)
    print("pull_product: exec %s %s" % (rel, pre or {}), flush=True)
    exec(open(path).read(), g)
    return g


shapes = {}  # live -> shape
pid = product["id"]
base_id = product.get("extends") or pid

if base_id == "pistol":
    pre = dict(product.get("build_pre") or {})
    pre["MASK_PRODUCT"] = pid
    g = exec_script("pistol/hammer_assembly.py", pre)
    for part in product["shell"] + product.get("drive", []):
        sh = resolve(g, part["live"])
        if sh is None:
            print("  skip %s" % part["stem"], flush=True)
            continue
        key = part["live"] if isinstance(part["live"], str) else part["stem"]
        shapes[key] = sh
        write_brep(sh, part["stem"])
    for name in product.get("pull_close_docs", []):
        if name in App.listDocuments():
            App.closeDocument(name)

elif base_id == "mitrailleuse":
    # pack_frame → plates
    g = exec_script("mitrailleuse/pack_frame.py", {"MASK_PRODUCT": "mitrailleuse"})
    built = g["built"]
    for tag in ("A16", "A19"):
        plates = built[tag][2]
        for side in ("rear", "front"):
            live = "%s_%s_plate" % (tag.lower(), side)
            shapes[live] = plates[side][0]
            stem = [p["stem"] for p in product["shell"] if p["live"] == live][0]
            write_brep(shapes[live], stem)
    if "pack_frame" in App.listDocuments():
        App.closeDocument("pack_frame")

    # rear_frame HEAD_N=16
    g2 = exec_script("mitrailleuse/rear_frame.py", {"HEAD_N": 16, "MASK_PRODUCT": "mitrailleuse"})
    mapping = {
        "head_plate": g2["hp"],
        "trigger_arm": g2["arm"],
        "bevel_box": g2["drive_box_b"],
    }
    for live, sh in mapping.items():
        shapes[live] = sh
        stem = [p["stem"] for p in product["shell"] if p["live"] == live][0]
        write_brep(sh, stem)
    for name in ("rear_frame", "rear_frame19"):
        if name in App.listDocuments():
            App.closeDocument(name)

    # carry_mount
    g3 = exec_script("mitrailleuse/carry_mount.py", {"MASK_PRODUCT": "mitrailleuse"})
    shapes["handle"] = g3["grip_part"]
    shapes["tripod_pad"] = g3["pad_part"]
    write_brep(shapes["handle"], "carry_handle")
    write_brep(shapes["tripod_pad"], "foot_pad")
    for tag, (key, mods, plates) in g3["built"].items():
        live = "%s_cg_plate" % tag.lower()
        shapes[live] = plates["cg_rear"][0]
        stems = [p["stem"] for p in product["shell"] if p["live"] == live]
        if stems:
            write_brep(shapes[live], stems[0])
    if "carry_mount" in App.listDocuments():
        App.closeDocument("carry_mount")

else:
    raise SystemExit("no pull recipe for product %r" % product["id"])

manifest = {
    "product": product["id"],
    "parts": manifest_parts(product),
}
with open(os.path.join(CACHE, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print("pull_product: wrote %s (%d files)" % (PARTS, len(os.listdir(PARTS))))
