# -*- coding: utf-8 -*-
"""
Dry-run candidate edits against the cached base parts before `in` accepts them.

    freecadcmd -c "REPO='$PWD'; PRODUCT='pistol'; EDITS='/path/to/edits'; exec(open('experiments/gpt-mask/check_edits.py').read())"

Exits non-zero on the first invalid edit. Monorepo only.
"""

from __future__ import print_function

import json
import os
import sys

import Part

sys.path.insert(0, os.path.join(REPO, "experiments", "gpt-mask"))  # noqa: F821
sys.path.insert(0, os.path.join(REPO, "experiments", "gpt-mask", "mechanismus_template"))  # noqa: F821
import edit_runner  # noqa: E402
from product_lib import load_product  # noqa: E402

product = load_product(PRODUCT)  # noqa: F821
cache = os.path.join(REPO, "experiments", "gpt-mask", "cache", product["id"])  # noqa: F821
if not os.path.isdir(os.path.join(cache, "parts")) and product.get("extends"):
    cache = os.path.join(REPO, "experiments", "gpt-mask", "cache", product["extends"])  # noqa: F821
with open(os.path.join(cache, "manifest.json"), "r", encoding="utf-8") as f:
    rows = json.load(f)["parts"]

base = {}
for row in rows:
    path = os.path.join(cache, "parts", row["stem"] + ".brep")
    if os.path.isfile(path):
        shape = Part.Shape()
        shape.read(path)
        base[row["stem"]] = shape
sees = {row["stem"]: row["sees"] for row in rows if "sees" in row}
shell = {p["stem"] for p in product["shell"]}

try:
    _, report = edit_runner.apply(EDITS, base, sees=sees, editable=shell)  # noqa: F821
except edit_runner.EditError as e:
    print("[FAIL] %s" % e, flush=True)
    sys.exit(1)
for line in report:
    print(("[OK ] " if line.startswith("edit") else "[--] ") + line, flush=True)
