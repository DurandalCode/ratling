# -*- coding: utf-8 -*-
"""
Apply Mechanismus shell overlays and part edits into a FreeCAD generator namespace.

Called from live generators after shell solids exist:

    MASK_PRODUCT = "pistol"   # optional; or env MASK_PRODUCT
    exec(open(os.path.join(REPO, "tools", "mask_overlays.py")).read())
    apply_mask_overlays(REPO, globals())

Reads experiments/gpt-mask/products/<id>.json, then per shell part:
  1. <overlay_dir>/<live>.brep replaces the solid (BREP fallback);
  2. <edits_dir>/<stem>.py edits it (edit(part, ctx), see mechanismus_template/edit_runner.py).
MASK_EDITS=0 skips step 2 (pull_product uses it to export the unedited base).
Sets ns["MASK_HOOK_STEMS"]: stems of the parts present here, i.e. what an edit's ctx can hold.
"""

from __future__ import print_function

import importlib.util
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
    return ns.get("MASK_PRODUCT") or "pistol"


def _load_runner(REPO):
    path = os.path.join(REPO, "experiments", "gpt-mask", "mechanismus_template", "edit_runner.py")
    spec = importlib.util.spec_from_file_location("mask_edit_runner", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply_mask_overlays(REPO, ns, product_id=None):
    import Part

    pid = product_id or _product_id(ns)
    path = os.path.join(REPO, "experiments", "gpt-mask", "products", pid + ".json")
    ns["MASK_HOOK_STEMS"] = []
    if not os.path.isfile(path):
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
    shell = data.get("shell") or []
    drive = data.get("drive") or []

    applied = []
    overlay_dir = os.path.join(REPO, data["overlay_dir"])
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

    parts = {}
    live_of = {}
    for part in shell + drive:
        live = part.get("live")
        if isinstance(live, str) and isinstance(ns.get(live), Part.Shape):
            parts[part["stem"]] = ns[live]
            live_of[part["stem"]] = live
    ns["MASK_HOOK_STEMS"] = sorted(parts)

    edits_dir = os.path.join(REPO, data["edits_dir"]) if data.get("edits_dir") else None
    if os.environ.get("MASK_EDITS", "1") != "0" and edits_dir and os.path.isdir(edits_dir):
        runner = _load_runner(REPO)
        editable = {p["stem"] for p in shell}
        edited, report = runner.apply(edits_dir, parts, editable=editable)
        for line in report:
            print("  [mask] %s" % line, flush=True)
        for stem, shape in edited.items():
            ns[live_of[stem]] = shape
            if live_of[stem] not in applied:
                applied.append(live_of[stem])
    return applied
