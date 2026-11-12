# -*- coding: utf-8 -*-
"""
Fixture C — real housing solids plus six-tube Rotor as Cylinder.

    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import os

import FreeCAD as App
import Part

try:
    HERE
except NameError:
    HERE = os.getcwd()

DOC_NAME = "six_rotor"
NAMES = (
    ("shell_lower", "Frame_lower"),
    ("shell_upper", "Frame_upper"),
    ("side_left_wall", "Frame_side"),
    ("side_left_band", "Frame_side_band"),
    ("side_right", "Frame_right"),
    ("grip_left", "Grip_left"),
    ("grip_right", "Grip_right"),
    ("bail", "Trigger_guard"),
    ("detent_box", "Detent_housing"),
    ("rotor_hub", "Cylinder"),
)
COLORS = {
    "Frame_lower": (0.24, 0.23, 0.22),
    "Frame_upper": (0.28, 0.27, 0.26),
    "Frame_side": (0.30, 0.29, 0.28),
    "Frame_side_band": (0.28, 0.27, 0.26),
    "Frame_right": (0.32, 0.31, 0.30),
    "Grip_left": (0.26, 0.16, 0.09),
    "Grip_right": (0.26, 0.16, 0.09),
    "Trigger_guard": (0.24, 0.23, 0.22),
    "Detent_housing": (0.24, 0.23, 0.22),
    "Cylinder": (0.70, 0.70, 0.72),
}

PARTS_DIR = os.path.join(HERE, "parts")
if not os.path.isdir(PARTS_DIR):
    raise SystemExit("missing parts/ — run experiments/gpt-mask/pull_real_shell.py in the monorepo")

if DOC_NAME in App.listDocuments():
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)
group = doc.addObject("App::DocumentObjectGroup", "Print")

for stem, name in NAMES:
    path = os.path.join(PARTS_DIR, stem + ".brep")
    shape = Part.Shape()
    shape.read(path)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    group.addObject(obj)
    if App.GuiUp:
        obj.ViewObject.ShapeColor = COLORS.get(name, (0.6, 0.6, 0.6))
    print("[OK ] %s  vol=%.0f" % (name, sum(s.Volume for s in shape.Solids)))

doc.recompute()
out = os.path.join(HERE, "exports")
os.makedirs(out, exist_ok=True)
doc.saveAs(os.path.join(out, DOC_NAME + ".FCStd"))
print("done: fixture C (real shell + block)")
