# -*- coding: utf-8 -*-
"""
Fixture A — thick mask, neutral lexicon.

Handheld rotary-actuator cover: shell halves, side covers, grip, bail.
No rotor, no fluid system. Run from this folder:

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
    "shell_lower": "Shell_tray",
    "shell_upper": "Shell_cover",
    "side_left": "Cover_left",
    "side_right": "Cover_right",
    "grip_left": "Grip_left",
    "grip_right": "Grip_right",
    "bail": "Bail",
}

COLORS = {
    "Shell_tray": (0.55, 0.55, 0.52),
    "Shell_cover": (0.62, 0.60, 0.55),
    "Cover_left": (0.50, 0.52, 0.55),
    "Cover_right": (0.50, 0.52, 0.55),
    "Grip_left": (0.35, 0.22, 0.12),
    "Grip_right": (0.35, 0.22, 0.12),
    "Bail": (0.40, 0.40, 0.38),
}

doc = App.newDocument("actuator_shell")
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
doc.saveAs(os.path.join(out, "actuator_shell.FCStd"))
print("done: fixture A")
