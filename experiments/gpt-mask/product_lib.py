# -*- coding: utf-8 -*-
"""Load product profiles for the Mechanismus pipe. Pure Python."""

from __future__ import print_function

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
PRODUCTS_DIR = os.path.join(HERE, "products")


def default_work_dir(product_id):
    """External work tree: $MECHANISMUS/<id> or <repo-parent>/mechanismus/<id>."""
    base = os.environ.get("MECHANISMUS", "").strip()
    if base:
        root = os.path.abspath(os.path.expanduser(base))
    else:
        root = os.path.abspath(os.path.join(REPO_ROOT, os.pardir, "mechanismus"))
    return os.path.join(root, product_id)


def list_products():
    return sorted(n[:-5] for n in os.listdir(PRODUCTS_DIR) if n.endswith(".json"))


def load_product(product_id):
    path = os.path.join(PRODUCTS_DIR, product_id + ".json")
    if not os.path.isfile(path):
        raise KeyError("unknown product %r (have: %s)" % (product_id, ", ".join(list_products())))
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    parent_id = data.get("extends")
    if parent_id:
        merged = dict(load_product(parent_id))
        merged.update({k: v for k, v in data.items() if k != "extends"})
        merged["extends"] = parent_id
        data = merged
    data["id"] = product_id
    data.setdefault("build_pre", {})
    data["work_dir"] = default_work_dir(product_id)
    return data
