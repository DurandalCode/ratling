# -*- coding: utf-8 -*-
"""
Mechanismus — shell + drive solids from parts/*.brep (see manifest.json).

    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import json
import os

import FreeCAD as App
import Part

try:
    HERE
except NameError:
    HERE = os.getcwd()

DOC_NAME = "mechanismus"
PARTS_DIR = os.path.join(HERE, "parts")
MANIFEST = os.path.join(HERE, "manifest.json")

if not os.path.isdir(PARTS_DIR):
    raise SystemExit("missing parts/")
if not os.path.isfile(MANIFEST):
    raise SystemExit("missing manifest.json")

with open(MANIFEST, "r", encoding="utf-8") as f:
    meta = json.load(f)
PARTS = meta["parts"]

if DOC_NAME in App.listDocuments():
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)
g_shell = doc.addObject("App::DocumentObjectGroup", "Shell")
g_drive = doc.addObject("App::DocumentObjectGroup", "Drive")

for row in PARTS:
    stem, name, group = row["stem"], row["label"], row.get("group", "Shell")
    path = os.path.join(PARTS_DIR, stem + ".brep")
    if not os.path.isfile(path):
        print("[skip] %s (no %s.brep)" % (name, stem))
        continue
    shape = Part.Shape()
    shape.read(path)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if group == "Shell":
        g_shell.addObject(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = (0.45, 0.45, 0.42)
    else:
        g_drive.addObject(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = (0.55, 0.62, 0.70)
    print("[OK ] %s  vol=%.0f" % (name, sum(s.Volume for s in shape.Solids)))

doc.recompute()
out = os.path.join(HERE, "exports")
os.makedirs(out, exist_ok=True)
doc.saveAs(os.path.join(out, DOC_NAME + ".FCStd"))
print("done: mechanismus (%s)" % meta.get("product", "?"))
