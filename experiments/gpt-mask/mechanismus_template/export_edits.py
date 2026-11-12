# -*- coding: utf-8 -*-
"""
Write Shell_* solids back to parts/<stem>.brep and .step using manifest.json.

    freecadcmd -c "HERE='$PWD'; exec(open('export_edits.py').read())"
"""

import json
import os

import FreeCAD as App

try:
    HERE
except NameError:
    HERE = os.getcwd()

DOC_NAME = "mechanismus"
parts_dir = os.path.join(HERE, "parts")
exp_dir = os.path.join(HERE, "exports")
manifest_path = os.path.join(HERE, "manifest.json")
os.makedirs(parts_dir, exist_ok=True)
os.makedirs(exp_dir, exist_ok=True)

with open(manifest_path, "r", encoding="utf-8") as f:
    meta = json.load(f)
SHELL = [(p["label"], p["stem"]) for p in meta["parts"] if p.get("group", "Shell") == "Shell"]

if DOC_NAME not in App.listDocuments():
    fc = os.path.join(exp_dir, DOC_NAME + ".FCStd")
    if os.path.isfile(fc):
        App.open(fc)
    else:
        raise SystemExit("no open document and no exports/%s.FCStd — run build.py first" % DOC_NAME)

doc = App.getDocument(DOC_NAME)
by_name = {o.Name: o for o in doc.Objects if o.TypeId == "Part::Feature"}

n = 0
for name, stem in SHELL:
    obj = by_name.get(name)
    if obj is None:
        continue
    shape = obj.Shape
    shape.exportBrep(os.path.join(parts_dir, stem + ".brep"))
    shape.exportBrep(os.path.join(exp_dir, name + ".brep"))
    shape.exportStep(os.path.join(parts_dir, stem + ".step"))
    print("[OK ] %s → parts/%s.brep + .step" % (name, stem))
    n += 1

if not n:
    raise SystemExit("no Shell_* parts found in document")
print("export_edits: %d shell parts written" % n)
