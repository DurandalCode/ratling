# -*- coding: utf-8 -*-
"""
Fixture D — full drive assembly, names translated to neutral actuator lexicon.

Solids are the live mechanism (stack, coupler, rotor, lever, yoke, wiring…).
Only the labels are rewritten. Regenerate parts from the monorepo:

    freecadcmd -c "REPO='$PWD'; exec(open('experiments/gpt-mask/pull_real_shell.py').read())"

Open this folder alone:

    freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
"""

import os

import FreeCAD as App
import Part

try:
    HERE
except NameError:
    HERE = os.getcwd()

DOC_NAME = "drive_assembly"

# brep stem → FreeCAD object name (no gun / fluid vocabulary)
NAMES = (
    ("tray", "Shell_tray"),
    ("lid", "Shell_cover"),
    ("left_wall", "Cover_left_wall"),
    ("left_band", "Cover_left_band"),
    ("right_cover", "Cover_right"),
    ("grip_l", "Grip_left"),
    ("grip_r", "Grip_right"),
    ("bail", "Bail"),
    ("index_box", "Index_box"),
    ("stack_body", "Stack_body"),
    ("stack_cap", "Stack_cap"),
    ("coupler", "Coupler"),
    ("spindle", "Spindle"),
    ("rotor", "Rotor"),
    ("sector", "Sector"),
    ("yoke", "Yoke"),
    ("lever", "Thumb_lever"),
    ("pedal", "Pedal"),
    ("click_tooth", "Click_tooth"),
    ("yoke_pin", "Yoke_pin"),
    ("index_bolt", "Index_bolt"),
    ("limit_switch", "Limit_switch"),
    ("return_springs", "Return_springs"),
    ("lever_axle", "Lever_axle"),
    ("yoke_rod", "Yoke_rod"),
    ("cable", "Cable"),
    ("signal_wire", "Signal_wire"),
    ("sense_wire", "Sense_wire"),
    ("wire_tee", "Wire_tee"),
    ("stack_ties", "Stack_ties"),
    ("coupler_screws", "Coupler_screws"),
    ("sector_ring", "Sector_ring"),
    ("rotor_strap", "Rotor_strap"),
    ("spindle_nose", "Spindle_nose"),
    ("spindle_plug", "Spindle_plug"),
    ("thrust_washer", "Thrust_washer"),
)

SHELL = {
    "Shell_tray", "Shell_cover", "Cover_left_wall", "Cover_left_band",
    "Cover_right", "Grip_left", "Grip_right", "Bail", "Index_box",
}
DRIVE = {
    "Stack_body", "Stack_cap", "Coupler", "Spindle", "Rotor", "Sector", "Yoke",
    "Thumb_lever", "Pedal", "Click_tooth", "Yoke_pin", "Index_bolt",
    "Limit_switch", "Return_springs", "Lever_axle", "Yoke_rod", "Cable",
    "Signal_wire", "Sense_wire", "Wire_tee", "Stack_ties", "Coupler_screws",
    "Sector_ring", "Rotor_strap", "Spindle_nose", "Spindle_plug", "Thrust_washer",
}

PARTS_DIR = os.path.join(HERE, "parts")
if not os.path.isdir(PARTS_DIR):
    raise SystemExit("missing parts/ — run experiments/gpt-mask/pull_real_shell.py in the monorepo")

if DOC_NAME in App.listDocuments():
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)
g_shell = doc.addObject("App::DocumentObjectGroup", "Shell")
g_drive = doc.addObject("App::DocumentObjectGroup", "Drive")

for stem, name in NAMES:
    path = os.path.join(PARTS_DIR, stem + ".brep")
    if not os.path.isfile(path):
        print("[skip] %s (no %s.brep)" % (name, stem))
        continue
    shape = Part.Shape()
    shape.read(path)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if name in SHELL:
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
print("done: fixture D (full mech, renamed)")
