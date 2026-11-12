# -*- coding: utf-8 -*-
"""
Mechanismus — shell + drive solids from parts/<stem>.brep or .step (see manifest.json),
with the Python edits from edits/<stem>.py applied to the Shell parts (see README.md).

    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import json
import os
import sys

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

def part_file(stem):
    found = [os.path.join(PARTS_DIR, stem + ext) for ext in (".brep", ".step", ".stp")]
    found = [p for p in found if os.path.isfile(p)]
    return max(found, key=os.path.getmtime) if found else None


base = {}
for row in PARTS:
    path = part_file(row["stem"])
    if not path:
        print("[skip] %s (no %s.brep / .step)" % (row["label"], row["stem"]))
        continue
    shape = Part.Shape()
    shape.read(path)
    base[row["stem"]] = shape

sees = {row["stem"]: row["sees"] for row in PARTS if "sees" in row}
shell_stems = {row["stem"] for row in PARTS if row.get("group", "Shell") == "Shell"}
sys.path.insert(0, HERE)
import edit_runner  # noqa: E402

try:
    edited, report = edit_runner.apply(os.path.join(HERE, "edits"), base, sees=sees, editable=shell_stems)
except edit_runner.EditError as e:
    print("[FAIL] %s" % e, flush=True)
    sys.exit(1)
for line in report:
    print("[edit] %s" % line)

for row in PARTS:
    stem, name, group = row["stem"], row["label"], row.get("group", "Shell")
    if stem not in base:
        continue
    shape = edited.get(stem, base[stem])
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
    print("[OK ] %s  vol=%.0f%s" % (name, sum(s.Volume for s in shape.Solids), "  (edited)" if stem in edited else ""))

doc.recompute()
out = os.path.join(HERE, "exports")
os.makedirs(out, exist_ok=True)
doc.saveAs(os.path.join(out, DOC_NAME + ".FCStd"))
print("done: mechanismus (%s)" % meta.get("product", "?"))
