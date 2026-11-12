# -*- coding: utf-8 -*-
"""Load product profiles for the Mechanismus pipe. Pure Python."""

from __future__ import print_function

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
PRODUCTS_DIR = os.path.join(HERE, "products")

PRODUCT_IDS = ("pistol", "mitrailleuse", "gatling")


def default_work_dir(product_id):
    """External work tree: $MECHANISMUS/<id> or <repo-parent>/mechanismus/<id>."""
    base = os.environ.get("MECHANISMUS", "").strip()
    if base:
        root = os.path.abspath(os.path.expanduser(base))
    else:
        root = os.path.abspath(os.path.join(REPO_ROOT, os.pardir, "mechanismus"))
    return os.path.join(root, product_id)


def list_products():
    out = []
    for name in sorted(os.listdir(PRODUCTS_DIR)):
        if name.endswith(".json"):
            out.append(name[:-5])
    return out


def load_product(product_id):
    path = os.path.join(PRODUCTS_DIR, product_id + ".json")
    if not os.path.isfile(path):
        raise KeyError("unknown product %r (have: %s)" % (product_id, ", ".join(list_products())))
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    parent_id = data.get("extends")
    if parent_id:
        parent = load_product(parent_id)
        merged = dict(parent)
        merged.update({k: v for k, v in data.items() if k != "extends"})
        # child shell/drive replace parent if provided
        if "shell" not in data:
            merged["shell"] = parent["shell"]
        if "drive" not in data:
            merged["drive"] = parent.get("drive", [])
        if "build_script" not in data:
            merged["build_script"] = parent["build_script"]
        if "build_pre" not in data:
            merged["build_pre"] = parent.get("build_pre", {})
        if "pull_close_docs" not in data:
            merged["pull_close_docs"] = parent.get("pull_close_docs", [])
        data = merged
        data["extends"] = parent_id
    data["id"] = product_id
    data.setdefault("drive", [])
    data.setdefault("build_pre", {})
    data.setdefault("pull_close_docs", [])
    data["overlay_dir"] = os.path.join(REPO_ROOT, data["overlay_dir"])
    data["edits_dir"] = os.path.join(REPO_ROOT, data.get("edits_dir") or data["overlay_dir"][:-len("overlays")] + "edits")
    data["build_script"] = os.path.join(REPO_ROOT, data["build_script"])
    data["work_dir"] = default_work_dir(product_id)
    return data


def shell_live_vars(product):
    return tuple(p["live"] if isinstance(p["live"], str) else p["stem"] for p in product["shell"])


def live_to_stem(product):
    out = {}
    for p in product["shell"]:
        live = p["live"]
        if not isinstance(live, str):
            continue
        out[live] = p["stem"]
    return out


def label_to_live(product):
    return {p["label"]: p["live"] for p in product["shell"] if isinstance(p["live"], str)}


def manifest_parts(product):
    """List for mechanismus_template build.py / export_edits.py."""
    rows = []
    for p in product["shell"] + product.get("drive", []):
        rows.append({"stem": p["stem"], "label": p["label"], "group": "Shell" if p in product["shell"] else "Drive"})
    return rows
