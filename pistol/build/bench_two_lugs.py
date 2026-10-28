# -*- coding: utf-8 -*-
"""
Ratling pistol bench, a try: the lock pusher with a lug and a pin on each side of the ring.

One lug pushed from one side tilts the sleeve in its bore (the force is 15-20 mm off the axis, the guide is
only about 12 mm long). Two lugs opposite each other put the force back on the axis. They cannot sit at 3 and
9 o'clock: the housing's self-tapping screw at 90 deg runs through the left one's path. At 45 and 225 deg they are
45 deg from both screws (at 90 and 180 deg), so this file puts them there.

Only the lock is built here: valve, housing with a slot for each lug, sleeve, the pusher with its two pins, the
two housing screws, the block, the axle. No frame: the screws that would push the pins need new arms
(not drawn). Writes exports/pistol_bench_two_lugs/ and leaves pistol_bench/ alone.

Run inside FreeCAD (it builds pistol/hammer_assembly.py first):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/bench_two_lugs.py').read())
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
LOCKLESS = False                 # this bench is about the old lock (sleeve, pusher)
LOCK_LUG_ANGLES = (45.0, 225.0)
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

NAME = "pistol_bench_two_lugs"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- the housing screws, as in bench_frame.py
screws = {}
for n_, a_ in enumerate(LOCK_BOLTS, 1):
    y_, z_ = -BREECH_BOLT_R * math.sin(math.radians(a_)), Z_FIRE + BREECH_BOLT_R * math.cos(math.radians(a_))
    screws["Lock_housing_screw_M3x30_%d" % n_] = (cyl_x(3.0, -GAP - 30.0, -GAP, y_, z_)
                                                  .fuse(cyl_x(5.5, -GAP, -GAP + 3.0, y_, z_)))

# ---------------------------------------------------------------- checks
moving_block = [turned(block, a_) for a_ in (0.0, 15.0, 30.0, 45.0, 60.0)]
pins = [about_lock_axis(cam_pin, a_).translated(V(X_OPEN, 0, 0)) for a_ in LOCK_LUG_ANGLES]
hits = {
    "pusher / housing, open": hit(pusher_shape(0.0), lock_housing_h),
    "pusher / housing, locked": hit(pusher_shape(1.0), lock_housing_h),
    "pusher / housing screws": max(hit(pusher_shape(l_), s_) for l_ in (0.0, 1.0) for s_ in screws.values()),
    "pusher / valve body and cap": max(hit(pusher_shape(l_), s_) for l_ in (0.0, 1.0) for s_ in (valve_body, valve_cap)),
    "pusher / block, turned 0..60": max(hit(pusher_shape(l_), s_) for l_ in (0.0, 1.0) for s_ in moving_block),
    "pusher / sector": max(hit(pusher_shape(l_), turned(sector_base, sector_turn(c_))) for l_ in (0.0, 1.0)
                           for c_ in (0.0, 0.5, 1.0)),
    "housing screws / housing": max(hit(s_, lock_housing_h) for s_ in screws.values()),
}
# the pusher's ring is inside the sleeve's flange pocket: it is glued to the flange, so it overlaps the sleeve there
hits["pusher / sleeve (glued on the flange)"] = hit(pusher_shape(1.0), lock_sleeve(1.0))
fine = ("pusher / sleeve (glued on the flange)",)
print(NAME)
print("  lug angles %s deg (screws at 90 and 180 deg)" % (LOCK_LUG_ANGLES,))
for k_, v_ in hits.items():
    ok = k_ in fine or v_ < 0.05
    print("  [%s] %s: %.1f mm3" % ("OK " if ok else "FAIL", k_, v_))
for i_, p_ in enumerate(pins, 1):
    b_ = p_.BoundBox
    print("  pin %d at y %.1f..%.1f z %.1f..%.1f (the screw that pushes it goes there)" % (i_, b_.YMin, b_.YMax, b_.ZMin, b_.ZMax))

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
GREEN, GREY, STEEL_C, NEW = (0.30, 0.70, 0.35), (0.55, 0.62, 0.72), (0.70, 0.72, 0.75), (0.93, 0.55, 0.18)
items = [("Valve_body", valve_body, GREY, 75), ("Valve_cap", valve_cap, GREY, 75), ("Lock_housing", lock_housing_h, GREEN, 65),
         ("Lock_sleeve", lock_sleeve(1.0), GREEN, 55), ("Lock_pusher_two_lugs", pusher_shape(1.0), NEW, 45),
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

# The two parts that change, in print orientation as in export_parts.py (the -x face on the bed).
import MeshPart
os.makedirs(os.path.join(OUT_DIR, "stl"), exist_ok=True)
for name_, shape_, profile_ in (("lock_housing", lock_housing_h, "airtight"), ("lock_pusher", pusher_shape(1.0), "strong")):
    s_ = shape_.copy()
    rot_ = App.Rotation(V(-1, 0, 0), V(0, 0, -1))
    s_.rotate(V(0, 0, 0), rot_.Axis, math.degrees(rot_.Angle))
    bb_ = s_.BoundBox
    s_.translate(V(-(bb_.XMin + bb_.XMax) / 2, -(bb_.YMin + bb_.YMax) / 2, -bb_.ZMin))
    MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "stl", name_ + ".stl"))
    print("  stl %-13s %-9s %.0f x %.0f x %.0f mm, %.1f cm3, valid %s" % (
        name_, profile_, s_.BoundBox.XLength, s_.BoundBox.YLength, s_.BoundBox.ZLength, s_.Volume / 1000, s_.isValid()))
print("written to", OUT_DIR)
