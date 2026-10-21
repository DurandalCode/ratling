# -*- coding: utf-8 -*-
"""
Ratling pistol: the bench for the final scheme, from the pistol's own parts and one frame.

What it tests: the v1.3 valve, the lock (housing, plain sleeve, pusher), the turning block on the chamber
axle, its thrust into the top strap. What it leaves out: the cage, the side plate, the hammer and its
springs, the slider, the sector and pawl, the trigger, the grip, the vent valve. The pistol's parts go on
it as they are (pistol/build/export_parts.py), and one printed frame does what the cage did:

    rear plate .. behind the valve cap, on the four tie rods (M4 x 60 instead of x 50: through the plate,
                  the cap and the body to the nuts in its pockets), a hole for the pilot fitting;
                  a keel under it for the vice
    top beam .... over the valve and the axle to the top strap's foot: the strap's two M3 x 40 go into it
                  as into the cage's top, so the strap holds the axle on the spigot and takes the block's
                  thrust, as in the pistol
    lock screw .. an arm on the right to a nut block behind the pusher's pin: an M3 screw pushes the pin
                  forward and seats the sleeve on the breech (the hammer's cam does it in the pistol);
                  backed off, the pin is pushed back by a finger and the block turns free
    detent ...... an arm on the left carries the pistol's detent box: its V bolt and Ø4 pen spring click
                  the block into each of the six barrels when it is turned by hand

Writes exports/pistol_bench/bench_frame.stl (rear plate on the bed) and a document with the bench.

Run inside FreeCAD (it builds pistol/hammer_assembly.py first, about two minutes):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/bench_frame.py').read())
"""

import math
import os

import FreeCAD as App
import MeshPart
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
VALVE = "v13"
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

NAME = "pistol_bench"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- parameters (pistol frame: x forward, z up)
X_CAP = valve_cap.BoundBox.XMin             # the cap's back face
PLATE_T = 8.0
PLATE_Y = 31.0 + 0.6 + 8.0                  # half width: the cap and the side arms (BODY_R + CLEAR + ARM t)
PLATE_Z = (-58.0, 30.0)
FITTING_HOLE = 22.0                         # the cap's G1/8 push-in passes through
ROD_HOLE = 4.4
KEEL = dict(y=20.0, z=-95.0)                # under the plate, in the plane of the plate: the vice grips it
BEAM = dict(y=12.0, z=(16.0, fz[1] - 2.0))  # top face = the cage's top, where the strap's foot sits
ARM = dict(t=8.0, z=(Z_FIRE - 6.0, Z_FIRE + 6.0))   # side arms, outside the body (|y| > BODY_R)
PIN_R = 1.5                                 # the pusher's pin (Ø3 steel)
SCREW = dict(d=3.4, nut_af=5.5, nut_t=2.4, y=24.5)  # M3 along x, its tip on the pin's back, outside the lock (r 23)
NUT_BLOCK_X = (-27.0, -14.0)               # from the body's top face to 1.4 mm behind the pin (open)
CLEAR = 0.6

y_pin = SCREW["y"]
rod_yz = [(-p.y, Z_FIRE + p.x) for p in rod_pts]          # body frame (x, y) -> pistol (y, z) = (-y, Z_FIRE + x)

# ---------------------------------------------------------------- rear plate and keel
x0, x1 = X_CAP - PLATE_T, X_CAP
plate = box(x0, x1, -PLATE_Y, PLATE_Y, PLATE_Z[0], PLATE_Z[1])
plate = plate.fuse(box(x0, x1, -KEEL["y"], KEEL["y"], KEEL["z"], PLATE_Z[0] + 1))
plate = plate.cut(cyl_x(FITTING_HOLE, x0 - 1, x1 + 1, 0, Z_FIRE))
for y_, z_ in rod_yz:
    plate = plate.cut(cyl_x(ROD_HOLE, x0 - 1, x1 + 1, y_, z_))

# ---------------------------------------------------------------- top beam to the strap's foot
foot_x1 = HUB_X0 - 2.5                      # the strap's foot ends here (hammer_assembly.py)
beam = box(x0, foot_x1, -BEAM["y"], BEAM["y"], BEAM["z"][0], BEAM["z"][1])
strap_pilots = Part.makeCompound([Part.makeCylinder(1.25, BEAM["z"][1] - BEAM["z"][0] + 2, V(x_, 0, BEAM["z"][0] - 1), ZA)
                                  for x_ in STRAP_BOLTS])

# ---------------------------------------------------------------- right arm: the lock screw
yr0 = BODY_R + CLEAR
arm_r = box(x0, NUT_BLOCK_X[1], yr0, yr0 + ARM["t"], ARM["z"][0], ARM["z"][1])
nut_block = box(NUT_BLOCK_X[0], NUT_BLOCK_X[1], 23.0 + CLEAR, yr0 + ARM["t"], ARM["z"][0], ARM["z"][1])
screw_hole = cyl_x(SCREW["d"], NUT_BLOCK_X[0] - 1, NUT_BLOCK_X[1] + 1, y_pin, Z_FIRE)
nut_r = SCREW["nut_af"] / 2 / math.cos(math.radians(30)) + 0.15
nx = NUT_BLOCK_X[1] - 2.5                  # the nut near the front, in the block's full section
nut_trap = Part.Face(Part.makePolygon([V(nx - SCREW["nut_t"] / 2 - 0.1, y_pin + nut_r * math.cos(math.radians(60 * k)),
                                         Z_FIRE + nut_r * math.sin(math.radians(60 * k))) for k in range(7)]))
nut_trap = nut_trap.extrude(V(SCREW["nut_t"] + 0.2, 0, 0)).fuse(
    box(nx - SCREW["nut_t"] / 2 - 0.1, nx + SCREW["nut_t"] / 2 + 0.1, y_pin - SCREW["nut_af"] / 2 - 0.15,
        y_pin + SCREW["nut_af"] / 2 + 0.15, Z_FIRE, ARM["z"][1] + 1))          # slid in from the top
# Printed rear plate down: whatever stands out past an arm, inward or outward, gets a 45 deg ramp under it.
def ramp(x_top, y_far, y_arm, z0, z1):
    """Under a ledge whose underside is at x_top, reaching from the arm (y_arm) out to y_far: 45 deg back to x."""
    d = abs(y_far - y_arm)
    tri = Part.Face(Part.makePolygon([V(x_top + 0.01, y_far, z0), V(x_top + 0.01, y_arm, z0), V(x_top - d, y_arm, z0),
                                      V(x_top + 0.01, y_far, z0)]))
    return tri.extrude(V(0, 0, z1 - z0))


# The block reaches 8 mm in from the arm over the body's top face, with nothing under it as printed: its underside
# rises at 45 deg from the arm, so it is whole only from 8 mm up, where the nut sits; behind that the screw runs in
# an open groove.
d_in = yr0 - (23.0 + CLEAR)
nut_block = nut_block.cut(Part.Face(Part.makePolygon([V(NUT_BLOCK_X[0] - 0.01, yr0 + 0.01, 0), V(NUT_BLOCK_X[0] - 0.01, 22.0, 0),
                                                     V(NUT_BLOCK_X[0] + d_in + 2.0, 22.0, 0), V(NUT_BLOCK_X[0] - 0.01, yr0 + 0.01, 0)]))
                          .extrude(V(0, 0, 100)).translated(V(0, 0, -50)))
arm_r = arm_r.fuse(nut_block)
arm_r = arm_r.cut(screw_hole).cut(nut_trap)

# ---------------------------------------------------------------- left arm: the detent box
db = detent_box.BoundBox
arm_l = box(x0, db.XMin + 1.0, -(yr0 + ARM["t"]), -yr0, ARM["z"][0], ARM["z"][1])
arm_l = arm_l.fuse(box(db.XMin - 6.0, db.XMin + 1.0, db.YMin, -yr0, db.ZMin, db.ZMax))
arm_l = arm_l.fuse(ramp(db.XMin - 6.0, db.YMin, -(yr0 + ARM["t"]), db.ZMin, db.ZMax))
arm_l = arm_l.fuse(box(x0, db.XMin + 1.0, -(yr0 + ARM["t"]), -yr0, ARM["z"][1] - 0.01, db.ZMax)
                   .common(box(db.XMin - 6.0 - (db.ZMax - ARM["z"][1]), db.XMin + 1.0, -100, 0, -100, 100)))
x_box = HUB_X0 + BOLT_X0 - 2                # the detent box proper starts here (hammer_assembly.py), beside the hub
arm_l = arm_l.fuse(box(db.XMin - 6.0, x_box + 0.01, db.YMin, -yr0, db.ZMin, db.ZMax)       # under it, clear of the hub
                   .cut(cyl_x(2 * (HUB_R + 1.0), HUB_X0 - 1.0, x_box + 1, 0, 0)))
arm_l = arm_l.cut(Part.makeCompound([bolt_shape(a_) for a_ in (0.0, 30.0)]))

frame_b = plate.fuse(beam).fuse(arm_r).fuse(arm_l).fuse(detent_box)
frame_b = frame_b.cut(strap_pilots).removeSplitter()
for y_, z_ in rod_yz:                       # the rods through the plate only, not the arms
    frame_b = frame_b.cut(cyl_x(ROD_HOLE, x0 - 1, x1 + 1, y_, z_))

# ---------------------------------------------------------------- checks
moving = {}
for i in range(7):
    a_ = 10.0 * i
    for k_, s_ in (("block", turned(block, a_)), ("bolt", bolt_shape(a_))):
        moving[(k_, a_)] = s_
fixed_parts = {"valve body": valve_body, "valve cap": valve_cap, "lock housing": lock_housing_h, "axle": axle,
               "strap": top_strap}
pin_open = cam_pin.translated(V(X_OPEN, 0, 0))
pin_locked = cam_pin.translated(V(X_OPEN + LOCK_STROKE, 0, 0))
pb = pin_open.BoundBox
hits = {n: hit(frame_b, s) for n, s in fixed_parts.items()}
hits["pusher open/locked"] = max(hit(frame_b, pusher_shape(l_)) for l_ in (0.0, 1.0))
hits["sleeve open/locked"] = max(hit(frame_b, lock_sleeve(l_)) for l_ in (0.0, 1.0))
hits["block, turned 0..60"] = max(hit(frame_b, s) for (k_, a_), s in moving.items() if k_ == "block")
screw_tip_gap = pb.XMin - NUT_BLOCK_X[1]
checks = {
    "frame valid single solid": frame_b.isValid() and len(frame_b.Solids) == 1,
    "frame clear of the valve, the lock, the axle and the strap": all(v_ < 0.05 for k_, v_ in hits.items()
                                                                     if k_ not in ("pusher open/locked", "sleeve open/locked", "block, turned 0..60")),
    "frame clear of the pusher and the sleeve, open and locked": hits["pusher open/locked"] < 0.05 and hits["sleeve open/locked"] < 0.05,
    "frame clear of the block turning": hits["block, turned 0..60"] < 0.05,
    "screw axis on the pin (y %.1f in %.1f..%.1f)" % (y_pin, pb.YMin, pb.YMax): pb.YMin + 1.0 <= y_pin <= pb.YMax - 1.0,
    "nut block behind the pin, open (%.1f mm)" % screw_tip_gap: screw_tip_gap > 0.5,
    "strap foot lands on the beam's top":
        abs(top_strap.common(box(x0, foot_x1, -50, 50, -100, 100)).BoundBox.ZMin - BEAM["z"][1]) < 0.01,
    "beam over the axle and the body (>= 1 mm)": BEAM["z"][0] - max(axle.BoundBox.ZMax, valve_body.BoundBox.ZMax) >= 1.0,
}
rod_new = rod_len + PLATE_T
print(NAME)
print("  frame: plate %.0f x %.0f x %.0f, beam to x %.1f, volume %.0f cm3" % (
    PLATE_T, 2 * PLATE_Y, PLATE_Z[1] - KEEL["z"], foot_x1, frame_b.Volume / 1000))
print("  tie rods: the cap's %d mm + the plate %.0f -> M4 x %d" % (rod_len, PLATE_T, 5 * math.ceil(rod_new / 5)))
print("  lock screw: M3 along x at y %.1f; nut block ends %.1f mm behind the pin (open), %.1f locked; "
      "screw past the block's face: %.1f .. %.1f mm" % (y_pin, screw_tip_gap, screw_tip_gap + LOCK_STROKE,
                                                        screw_tip_gap, screw_tip_gap + LOCK_STROKE))
print("  hits (mm3): " + ", ".join("%s %.1f" % kv for kv in hits.items()))
for k_, v_ in checks.items():
    print("  [%s] %s" % ("OK " if v_ else "FAIL", k_))

# ---------------------------------------------------------------- output
os.makedirs(OUT_DIR, exist_ok=True)
s_ = frame_b.copy()
s_.rotate(V(0, 0, 0), YA, -90)              # rear plate (x = x0, facing -x) down on the bed
s_.translate(V(0, 0, -s_.BoundBox.ZMin))
MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "bench_frame.stl"))
s_.exportStep(os.path.join(OUT_DIR, "bench_frame.step"))

if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
GREEN, GREY, STEEL_C, NEW = (0.30, 0.70, 0.35), (0.55, 0.62, 0.72), (0.70, 0.72, 0.75), (0.93, 0.55, 0.18)
for n, s, c, t in (("Bench_frame", frame_b, NEW, 0), ("Valve_body", valve_body, GREY, 0), ("Valve_cap", valve_cap, GREY, 0),
                   ("Lock_housing", lock_housing_h, GREEN, 0), ("Lock_sleeve", lock_sleeve(1.0), GREEN, 0),
                   ("Lock_pusher", pusher_shape(1.0), GREEN, 0), ("Pusher_pin", pin_locked, STEEL_C, 0),
                   ("Chamber_axle", axle, STEEL_C, 50), ("Block", block, STEEL_C, 30), ("Top_strap", top_strap, GREEN, 0),
                   ("Nose_sleeve", nose, GREEN, 0), ("Axle_plug", axle_plug, GREEN, 0), ("Detent_bolt", bolt_shape(0.0), GREEN, 0)):
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = t
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
print("written to", OUT_DIR)
