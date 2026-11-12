# -*- coding: utf-8 -*-
"""
Apply Mechanismus shell overlays into a FreeCAD generator namespace.

Called from live generators after shell solids exist:

    MASK_PRODUCT = "pistol"   # optional; or env MASK_PRODUCT
    exec(open(os.path.join(REPO, "tools", "mask_overlays.py")).read())
    apply_mask_overlays(REPO, globals())

Reads experiments/gpt-mask/products/<id>.json and <overlay_dir>/<live>.brep.
"""

from __future__ import print_function

import json
import os


def _product_id(ns):
    try:
        return MASK_PRODUCT  # noqa: F821 — set by caller before exec
    except NameError:
        pass
    env = os.environ.get("MASK_PRODUCT", "").strip()
    if env:
        return env
    # Heuristic from script path in REPO-relative generators
    return ns.get("MASK_PRODUCT") or "pistol"


def apply_mask_overlays(REPO, ns, product_id=None):
    import Part

    pid = product_id or _product_id(ns)
    path = os.path.join(REPO, "experiments", "gpt-mask", "products", pid + ".json")
    if not os.path.isfile(path):
        # try extends target for gatling → still has own file
        print("  [mask] no product profile %s — skip overlays" % pid, flush=True)
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("extends") and "overlay_dir" not in data:
        parent = os.path.join(REPO, "experiments", "gpt-mask", "products", data["extends"] + ".json")
        with open(parent, "r", encoding="utf-8") as f:
            parent_data = json.load(f)
        for k, v in parent_data.items():
            data.setdefault(k, v)
    overlay_dir = os.path.join(REPO, data["overlay_dir"])
    if not os.path.isdir(overlay_dir):
        return []
    shell = data.get("shell") or []
    applied = []
    for part in shell:
        live = part.get("live")
        if not isinstance(live, str):
            continue
        brep = os.path.join(overlay_dir, live + ".brep")
        if not os.path.isfile(brep):
            continue
        if live not in ns:
            print("  [mask] overlay %s.brep but no var %s in namespace" % (live, live), flush=True)
            continue
        shape = Part.Shape()
        shape.read(brep)
        ns[live] = shape
        applied.append(live)
    if applied:
        print("  [mask] %s overlays: %s" % (pid, ", ".join(applied)), flush=True)
    return applied
