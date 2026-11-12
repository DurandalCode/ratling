# -*- coding: utf-8 -*-
"""
Fixture B — same shell geometry as A, firearm-adjacent lexicon.

Frame / hammer / trigger / cylinder naming only. Still no fluid system
and no six-bore rotor. Run from this folder:

    export LANG=C.UTF-8 LC_ALL=C.UTF-8
    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import os

import FreeCAD as App

try:
    HERE
except NameError:
    HERE = os.getcwd()
WITH_ROTOR = False
GEOM_LIBRARY = True
exec(open(os.path.join(HERE, "geometry.py")).read())
PARTS = build_parts()

NAMES = {
    "shell_lower": "Frame_lower",
    "shell_upper": "Frame_upper",
    "side_left": "Frame_side",
    "side_right": "Frame_right",
    "grip_left": "Grip_left",
    "grip_right": "Grip_right",
    "bail": "Trigger_guard",
}

COLORS = {
    "Frame_lower": (0.24, 0.23, 0.22),
    "Frame_upper": (0.28, 0.27, 0.26),
    "Frame_side": (0.30, 0.29, 0.28),
    "Frame_right": (0.32, 0.31, 0.30),
    "Grip_left": (0.26, 0.16, 0.09),
    "Grip_right": (0.26, 0.16, 0.09),
    "Trigger_guard": (0.24, 0.23, 0.22),
}

doc = App.newDocument("frame_hammer")
group = doc.addObject("App::DocumentObjectGroup", "Print")

for key, shape in PARTS.items():
    name = NAMES[key]
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    group.addObject(obj)
    if App.GuiUp:
        obj.ViewObject.ShapeColor = COLORS.get(name, (0.6, 0.6, 0.6))
    print("[OK ] %s  vol=%.0f" % (name, sum(s.Volume for s in shape.Solids)))

doc.recompute()
out = os.path.join(HERE, "exports")
os.makedirs(out, exist_ok=True)
for obj in group.Group:
    path = os.path.join(out, obj.Name + ".stl")
    obj.Shape.exportStl(path)
    print("wrote", path)
doc.saveAs(os.path.join(out, "frame_hammer.FCStd"))
print("done: fixture B")
