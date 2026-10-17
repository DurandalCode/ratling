# -*- coding: utf-8 -*-
"""
Toggle the active FreeCAD document between its look and colours by material.

Parts carry a Material property (print / eva / buy), set by
pistol/hammer_assembly.py. Run once: printed parts orange, EVA green,
bought blue, and anything unsorted magenta. Run again: the look comes back.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/material_view.py').read())
"""

import FreeCAD as App

COLOURS = {"print": (0.95, 0.55, 0.10), "eva": (0.35, 0.75, 0.35), "buy": (0.30, 0.45, 0.90)}

doc = App.ActiveDocument
parts = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "ViewObject")]
on = not any(getattr(o, "LookColour", None) for o in parts)
for o in parts:
    if on:
        if not hasattr(o, "LookColour"):
            o.addProperty("App::PropertyColor", "LookColour", "Ratling", "the look's colour, kept while shown by material")
            o.addProperty("App::PropertyInteger", "LookTransparency", "Ratling")
        o.LookColour = o.ViewObject.ShapeColor
        o.LookTransparency = o.ViewObject.Transparency
        o.ViewObject.ShapeColor = COLOURS.get(getattr(o, "Material", ""), (1.0, 0.0, 1.0))
        o.ViewObject.Transparency = 0
    elif hasattr(o, "LookColour"):
        o.ViewObject.ShapeColor = o.LookColour[:3]
        o.ViewObject.Transparency = o.LookTransparency
        o.removeProperty("LookColour")
        o.removeProperty("LookTransparency")
print("by material: print orange, EVA green, bought blue" if on else "the look is back")
