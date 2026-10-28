# -*- coding: utf-8 -*-
"""
Ratling pistol bench, a try: no lock at all, the sleeve printed into the housing.

The lock exists to close the 4 mm gap between the lock housing and the hub while the shot goes and to open it for
the turn. If the sleeve is a fixed ring that stops NOSE_GAP short of the hub, the block turns without touching it
and the shot leaks only through that slit. So the housing is a plain block with a through SEAT_D bore that ends in the sleeve's nose (NOSE_D out) as one
print, without the pockets for the flange and tube: no sleeve, no pusher, no O-ring, no lugs or slots, no lock screw, no cam, no fit to tune.

Only the lock is built here: valve, the housing with the nose, the housing screws, the block, the axle. Writes
exports/pistol_bench_fixed_nose/ and leaves pistol_bench/ alone.

Run inside FreeCAD (it builds pistol/hammer_assembly.py first):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/bench_fixed_nose.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
VALVE = "v13"
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

NAME = "pistol_bench_fixed_nose"
OUT_DIR = os.path.join(REPO, "exports", NAME)
try:
    NOSE_GAP
except NameError:
    NOSE_GAP = 0.3                  # nose face to the hub's rear face (the sleeve's was 0.1 locked, 1.1 open)

# ---------------------------------------------------------------- housing with the nose
x_nose = HUB_X0 - NOSE_GAP
nose = cyl_x(NOSE_D, -GAP - 1.0, x_nose, 0, Z_FIRE).cut(cyl_x(SEAT_D, -GAP - 2.0, x_nose + 1.0, 0, Z_FIRE))
# lock_housing_plain minus the pockets for the sleeve's flange and tube: here the bore is a plain through channel
housing = (cyl_x(BREECH_FLANGE_D, -GAP - LOCK_H, -GAP, 0, Z_FIRE)
           .common(box(-GAP - LOCK_H - 1, -GAP + 1, -30, 30, Z_FIRE - 30, Z_FIRE + BREECH_FLAT_X))
           .fuse(nose)
           .cut(cyl_x(SEAT_D, -GAP - LOCK_H - 1, x_nose + 1.0, 0, Z_FIRE))
           .cut(Part.makeCompound([cyl_x(BREECH_BOLT_HOLE, -GAP - LOCK_H - 1, -GAP + 1,
                                         -BREECH_BOLT_R * math.sin(math.radians(a)),
                                         Z_FIRE + BREECH_BOLT_R * math.cos(math.radians(a))) for a in LOCK_BOLTS]))
           .removeSplitter())

screws = {}
for n_, a_ in enumerate(LOCK_BOLTS, 1):
    y_, z_ = -BREECH_BOLT_R * math.sin(math.radians(a_)), Z_FIRE + BREECH_BOLT_R * math.cos(math.radians(a_))
    screws["Lock_housing_screw_M3x30_%d" % n_] = (cyl_x(3.0, -GAP - 30.0, -GAP, y_, z_)
                                                  .fuse(cyl_x(5.5, -GAP, -GAP + 3.0, y_, z_)))

# ---------------------------------------------------------------- checks
turns = [turned(block, a_) for a_ in (0.0, 15.0, 30.0, 45.0, 60.0)]
hits = {
    "nose / block, turned 0..60": max(hit(turned(block, a_), nose) for a_ in range(0, 61, 5)),
    "nose / sector": max(hit(turned(sector_base, sector_turn(c_)), nose) for c_ in (0.0, 0.25, 0.5, 0.75, 1.0)),
    "housing / axle": hit(axle, housing),
    "housing / valve body and cap": max(hit(s_, housing) for s_ in (valve_body, valve_cap)),
    "housing screws / housing": max(hit(s_, housing) for s_ in screws.values()),
}
print(NAME)
for k_, v_ in hits.items():
    print("  [%s] %s: %.1f mm3" % ("OK " if v_ < 0.05 else "FAIL", k_, v_))
gap_ok = abs(block.BoundBox.XMin - 0) < 50 and nose.BoundBox.XMax < HUB_X0
print("  [%s] nose face x = %.2f, hub rear face x = %.2f (gap %.2f mm)" % ("OK " if gap_ok else "FAIL", nose.BoundBox.XMax, HUB_X0, HUB_X0 - nose.BoundBox.XMax))
print("  nose length past the housing face: %.1f mm, OD %.1f, bore %.1f" % (x_nose + GAP, NOSE_D, SEAT_D))

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
GREEN, GREY, STEEL_C = (0.30, 0.70, 0.35), (0.55, 0.62, 0.72), (0.70, 0.72, 0.75)
items = [("Valve_body", valve_body, GREY, 75), ("Valve_cap", valve_cap, GREY, 75), ("Lock_housing_with_nose", housing, GREEN, 55),
         ("Chamber_axle", axle, STEEL_C, 70), ("Block", block, STEEL_C, 80)]
items += [(k_, s_, STEEL_C, 50) for k_, s_ in screws.items()]
for n, s, c, t in items:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = t
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

# The one changed part, in print orientation as in export_parts.py (the -x face on the bed).
import MeshPart
os.makedirs(os.path.join(OUT_DIR, "stl"), exist_ok=True)
s_ = housing.copy()
rot_ = App.Rotation(V(-1, 0, 0), V(0, 0, -1))
s_.rotate(V(0, 0, 0), rot_.Axis, math.degrees(rot_.Angle))
bb_ = s_.BoundBox
s_.translate(V(-(bb_.XMin + bb_.XMax) / 2, -(bb_.YMin + bb_.YMax) / 2, -bb_.ZMin))
MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "stl", "lock_housing_nose.stl"))
print("  stl lock_housing_nose airtight  %.0f x %.0f x %.0f mm, %.1f cm3, valid %s" % (
    s_.BoundBox.XLength, s_.BoundBox.YLength, s_.BoundBox.ZLength, s_.Volume / 1000, s_.isValid()))
print("written to", OUT_DIR)
