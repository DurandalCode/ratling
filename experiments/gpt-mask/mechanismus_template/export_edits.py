# -*- coding: utf-8 -*-
"""
Write Shell_* solids back to parts/<stem>.brep.

    freecadcmd -c "HERE='$PWD'; exec(open('export_edits.py').read())"
"""

import os

import FreeCAD as App

try:
    HERE
except NameError:
    HERE = os.getcwd()

SHELL = (
    ("Shell_tray", "tray"),
    ("Shell_cover", "lid"),
    ("Cover_left_wall", "left_wall"),
    ("Cover_left_band", "left_band"),
    ("Cover_right", "right_cover"),
    ("Grip_left", "grip_l"),
    ("Grip_right", "grip_r"),
    ("Bail", "bail"),
    ("Index_box", "index_box"),
)

DOC_NAME = "mechanismus"
parts_dir = os.path.join(HERE, "parts")
exp_dir = os.path.join(HERE, "exports")
os.makedirs(parts_dir, exist_ok=True)
os.makedirs(exp_dir, exist_ok=True)

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
    print("[OK ] %s → parts/%s.brep" % (name, stem))
    n += 1

if not n:
    raise SystemExit("no Shell_* parts found in document")
print("export_edits: %d shell parts written" % n)
