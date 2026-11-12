# -*- coding: utf-8 -*-
"""
Fixture A — real housing solids, neutral names.

Loads parts/*.brep (live housing with all pockets). Open this folder alone:

    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import os

import FreeCAD as App
import Part

try:
    HERE
except NameError:
    HERE = os.getcwd()

DOC_NAME = "actuator_shell"
NAMES = (
    ("shell_lower", "Shell_tray"),
    ("shell_upper", "Shell_cover"),
    ("side_left_wall", "Cover_left_wall"),
    ("side_left_band", "Cover_left_band"),
    ("side_right", "Cover_right"),
    ("grip_left", "Grip_left"),
    ("grip_right", "Grip_right"),
    ("bail", "Bail"),
    ("detent_box", "Latch_box"),
)
COLORS = {
    "Shell_tray": (0.55, 0.55, 0.52),
    "Shell_cover": (0.62, 0.60, 0.55),
    "Cover_left_wall": (0.50, 0.52, 0.55),
    "Cover_left_band": (0.48, 0.50, 0.53),
    "Cover_right": (0.50, 0.52, 0.55),
    "Grip_left": (0.35, 0.22, 0.12),
    "Grip_right": (0.35, 0.22, 0.12),
    "Bail": (0.40, 0.40, 0.38),
    "Latch_box": (0.45, 0.45, 0.42),
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
print("done: fixture A (real shell)")
