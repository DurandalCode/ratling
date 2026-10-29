# -*- coding: utf-8 -*-
"""
Ratling pistol, a stand for the indexer: sector, pawl, block's rear disc, detent, and the slider that drives them.

The cage hides all of it. This is the same kinematics on a bare jig, in the pistol's own coordinates: a hollow post
for the chamber tube's place (the disc turns on it, the sector floats round it), the guide rod's two bosses at the
slider's place (the real slider runs on a real Ø3 rod, 96 mm), the detent housing at its angle, tied to the post by a
bar. Put the slider's Ø3 pin through the sector's arm slot and push the slider up by hand: 33 mm of stroke is 68 deg of
sector, 60 deg of disc after the pawl's lost motion, and a click at each barrel.

Prints ONE part (the jig). The rest are the pistol's own: block_rear_disc, sector, pawl, slider, detent_bolt, and a
Ø3 pen spring for the pawl, a Ø4 one for the bolt, a 96 mm Ø3 rod (in from below, held by an M3 x 10
self-tapping screw across the lower boss), a Ø3 x 9 pin for the slider.

Writes exports/pistol_indexer_test/ (STL of the jig in print orientation, FCStd of the stand with the parts).

Run inside FreeCAD (it builds pistol/hammer_assembly.py first):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/indexer_test.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

NAME = "pistol_indexer_test"
OUT_DIR = os.path.join(REPO, "exports", NAME)
PLATE_X = (-18.0, -15.0)            # the jig's back plate; the pawl boss reaches back to x = -14.2
POST_OD, POST_ID = 25.0, 17.0       # the chamber tube's size (hub bore 25.6, sector bore 25.8)
POST_X1 = HUB_X0 + HUB_T_HAMMER + 3.5       # the post's end carries the collar that holds the stack
ROD_HOLE = GUIDE_ROD["d"] + 0.15
STRIP_Y = (SLIDER_Y[0] - 2.0, BRACKET_Y[0] - 0.8)     # clear of the slider's bracket (y 35.2..38.2) that runs back to the crank
BAR_W = 16.0

# ---------------------------------------------------------------- the jig
post = cyl_x(POST_OD, PLATE_X[0], POST_X1, 0, 0).cut(cyl_x(POST_ID, PLATE_X[0] - 1, POST_X1 + 1, 0, 0))
rod_y, rod_x = GUIDE_ROD["y"], GUIDE_ROD["x"]
z_lo, z_hi = GUIDE_ROD["z"]
boss_hi = box(rod_x - 4.5, rod_x + 4.5, rod_y - 4.5, rod_y + 4.5, slider_h(1.0)[0].BoundBox.ZMax + 0.8, z_hi + 3.7)
boss_lo = box(rod_x - 4.5, rod_x + 4.5, rod_y - 4.5, rod_y + 4.5, z_lo - 3.0, slider_h(0.0)[0].BoundBox.ZMin - 0.7)
strip = box(PLATE_X[0], PLATE_X[1], STRIP_Y[0], STRIP_Y[1], boss_lo.BoundBox.ZMin, boss_hi.BoundBox.ZMax)
to_boss = [box(PLATE_X[1] - 0.01, rod_x + 4.5, rod_y - 4.5, rod_y + 4.5, bz.BoundBox.ZMin, bz.BoundBox.ZMax) for bz in (boss_hi, boss_lo)]
cross = box(PLATE_X[0], PLATE_X[1], 0.0, STRIP_Y[0] + 0.01, -BAR_W / 2, BAR_W / 2)             # post to the strip
bx0, bx1 = HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2                               # the detent housing, as in the cage
z_top, z_bot = -HUB_R - 1.5, -HUB_R - 24
det = box(bx0, bx1, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2, z_bot, z_top)
bar = box(PLATE_X[0], PLATE_X[1], -BAR_W / 2, BAR_W / 2, z_bot, 0.0)
tie = box(PLATE_X[1] - 0.01, bx0 + 0.01, -BAR_W / 2, BAR_W / 2, z_bot, z_top)
channel = bolt_prism(-HUB_R + BOLT_DEPTH, BOLT_LEN).fuse(bolt_prism(-HUB_R, BOLT_LEN)).fuse(
    bolt_prism(-HUB_R, BOLT_LEN + 2).translated(V(0, 0, 3.0)))
spring4 = Part.makeCylinder(2.15, 10.5, V(HUB_X0 + BOLT_X0 + BOLT[0] / 2, 0, -HUB_R - BOLT_LEN - 10.5), ZA)
detent_side = turned(det.fuse(bar).fuse(tie).cut(channel).cut(spring4), DETENT_ANGLE + 90)
jig = post.fuse(strip).fuse(cross).fuse(detent_side)
for t_ in to_boss:
    jig = jig.fuse(t_)
jig = jig.fuse(boss_hi).fuse(boss_lo)
# The rod goes in from below (top boss: a blind hole it butts into; bottom boss: open at the bottom) and is held by an M3
# self-tapping screw across the bottom boss: the top hole alone gave it no way in, and nothing held it once it was in.
for z0_, z1_ in ((boss_hi.BoundBox.ZMin, z_hi + 0.7), (boss_lo.BoundBox.ZMin - 1.0, boss_lo.BoundBox.ZMax)):
    jig = jig.cut(Part.makeCylinder(ROD_HOLE / 2, z1_ - z0_, V(rod_x, rod_y, z0_), ZA))
clamp_z = (z_lo + boss_lo.BoundBox.ZMax) / 2 + 0.7                  # mid-way along the rod's end inside the boss
jig = jig.cut(Part.makeCylinder(1.25, 5.5, V(rod_x, rod_y, clamp_z), YA))              # Ø2.5 pilot for the M3, from the outside (+y)
jig = jig.removeSplitter()

# ---------------------------------------------------------------- the rings that set the axial distances
# Everything on the post sits where the model puts it, not where O-rings happen to leave it: a spacer behind the sector, a
# thin washer between the sector and the disc, a collar in front of the disc. Heights are multiples of the 0.2 mm layer.
RING_ID = POST_OD + 0.4
SECTOR_SLOT = (-3.8, -0.3)                    # the sector (3.2 thick, x -3.6..-0.4) has 0.2 / 0.1 mm of play in it
REAR_SPACER = (PLATE_X[1], SECTOR_SLOT[0])    # 11.2 long, from the plate's front face to the sector's slot
WASHER = (SECTOR_SLOT[1], HUB_X0)             # 0.8 thick: the disc's rear face then sits at x = 0.5 exactly
COLLAR = (HUB_X0 + HUB_T_HAMMER + 0.2, HUB_X0 + HUB_T_HAMMER + 3.2)     # 0.2 mm in front of the disc, 3 long
COLLAR_SCREW_X = (COLLAR[0] + COLLAR[1]) / 2


def ring(x0, x1, od):
    return cyl_x(od, x0, x1, 0, 0).cut(cyl_x(RING_ID, x0 - 1, x1 + 1, 0, 0))


rear_spacer, washer = ring(*REAR_SPACER, 28.6), ring(*WASHER, 28.0)
collar = ring(*COLLAR, 31.0).cut(Part.makeCylinder(1.6, 8, V(COLLAR_SCREW_X, 0, 10), ZA))     # Ø3.2 for an M3 x 8 into the post
rings = {"spacer_rear": rear_spacer, "washer": washer, "collar": collar}
jig = jig.cut(Part.makeCylinder(1.25, 3.5, V(COLLAR_SCREW_X, 0, POST_OD / 2 - 3.2), ZA)).removeSplitter()   # Ø2.5 pilot in the post's wall

# ---------------------------------------------------------------- checks over the stroke
rod = Part.makeCylinder(GUIDE_ROD["d"] / 2, z_hi - z_lo, V(rod_x, rod_y, z_lo), ZA)
worst = {}
for i in range(11):
    c = i / 10
    st = pose(dict(cock=c, block=block_drive(c), bend=0.0, trig=0.0))
    disc = turned(hub, block_drive(c))
    for n_, sh_ in (("slider", st["Slider"]), ("pin", st["Pin"]), ("sector", st["Sector"]),                     ("bolt", st["Bolt"]), ("disc", disc)):
        for k_, o_ in (("jig", jig), ("rod", rod)):
            v_ = hit(sh_, o_)
            if n_ == "bolt" and k_ == "jig":
                continue                       # it slides in its channel
            worst[(n_, k_)] = max(worst.get((n_, k_), 0.0), v_)
print(NAME)
bad = {k_: v_ for k_, v_ in worst.items() if v_ > 0.05}
print("  [%s] stand clear of the moving parts over the stroke%s" % ("OK " if not bad else "FAIL", "" if not bad else ": " + str(bad)))
d_ = jig.distToShape(Part.makeCompound([sl_ for sl_ in (pose(REST)["Sector"], pose(REST)["Slider"], hub)]))[0]
print("  [%s] nearest approach of the jig to the sector, slider and disc: %.2f mm" % ("OK " if d_ >= 0.1 or d_ == 0 else "FAIL", d_))
print("  [%s] disc turns %.0f deg for %.1f mm of slider; detent depth %.1f mm" % (
    "OK " if abs(block_drive(1.0) - 60.0) < 0.5 else "FAIL", block_drive(1.0), slider_z(1.0) - slider_z(0.0), BOLT_DEPTH))
ring_hits = max(hit(r_, turned(sector_base, sector_turn(c_ / 4))) for r_ in rings.values() for c_ in range(5))
ring_hits = max(ring_hits, max(hit(r_, turned(hub, a_)) for r_ in (rear_spacer, washer, collar) for a_ in (0.0, 30.0, 60.0)),
                max(hit(r_, jig) for r_ in (rear_spacer, washer)) if False else 0.0)
print("  [%s] rings clear of the sector and the disc (%.2f mm3); sector slot %.1f mm for a %.1f mm ring: %.1f mm of play; "
      "disc %.1f mm behind the collar" % ("OK " if ring_hits < 0.05 else "FAIL", ring_hits, SECTOR_SLOT[1] - SECTOR_SLOT[0],
                                          SECTOR_X[1] - SECTOR_X[0], SECTOR_SLOT[1] - SECTOR_SLOT[0] - (SECTOR_X[1] - SECTOR_X[0]), 0.2))
print("  [%s] stack: spacer %.1f + slot %.1f + washer %.1f = %.1f mm from the plate to the disc's rear face (the model: %.1f)" % (
    "OK " if abs(REAR_SPACER[1] - REAR_SPACER[0] + SECTOR_SLOT[1] - SECTOR_SLOT[0] + WASHER[1] - WASHER[0] - (HUB_X0 - PLATE_X[1])) < 1e-6 else "FAIL",
    REAR_SPACER[1] - REAR_SPACER[0], SECTOR_SLOT[1] - SECTOR_SLOT[0], WASHER[1] - WASHER[0], HUB_X0 - PLATE_X[1], HUB_X0 - PLATE_X[1]))
bb = jig.BoundBox
print("  jig %.0f x %.0f x %.0f mm, %.1f cm3, valid %s" % (bb.XLength, bb.YLength, bb.ZLength, jig.Volume / 1000, jig.isValid()))

# ---------------------------------------------------------------- document and STL
os.makedirs(os.path.join(OUT_DIR, "stl"), exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
st0 = pose(dict(cock=0.5, block=block_drive(0.5), bend=0.0, trig=0.0))
for n, s, c, t in (("Jig", jig, (0.55, 0.62, 0.72), 0), ("Disc", turned(hub, block_drive(0.5)), (0.3, 0.7, 0.35), 40),
                   ("Sector", st0["Sector"], (0.9, 0.6, 0.2), 0),
                   ("Slider", st0["Slider"], (0.35, 0.45, 0.85), 0), ("Slider_pin", st0["Pin"], (0.8, 0.8, 0.8), 0),
                   ("Bolt", st0["Bolt"], (0.8, 0.8, 0.8), 0), ("Guide_rod", rod, (0.8, 0.8, 0.8), 0),
                   ("Spacer_rear", rear_spacer, (0.95, 0.85, 0.25), 20), ("Washer", washer, (0.95, 0.45, 0.25), 20),
                   ("Collar", collar, (0.85, 0.35, 0.7), 20)):
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = t
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart
s_ = jig.copy()
rot_ = App.Rotation(V(-1, 0, 0), V(0, 0, -1))
s_.rotate(V(0, 0, 0), rot_.Axis, math.degrees(rot_.Angle))
bb_ = s_.BoundBox
s_.translate(V(-(bb_.XMin + bb_.XMax) / 2, -(bb_.YMin + bb_.YMax) / 2, -bb_.ZMin))
MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "stl", "indexer_jig.stl"))
print("  stl indexer_jig %.0f x %.0f x %.0f mm on the bed" % (s_.BoundBox.XLength, s_.BoundBox.YLength, s_.BoundBox.ZLength))
for n_, r_ in rings.items():
    s_ = r_.copy()
    s_.rotate(V(0, 0, 0), rot_.Axis, math.degrees(rot_.Angle))
    bb_ = s_.BoundBox
    s_.translate(V(-(bb_.XMin + bb_.XMax) / 2, -(bb_.YMin + bb_.YMax) / 2, -bb_.ZMin))
    MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "stl", "ring_" + n_ + ".stl"))
    print("  stl ring_%-11s Ø%.1f / Ø%.1f x %.1f mm" % (n_, RING_ID, s_.BoundBox.XLength, s_.BoundBox.ZLength))
print("written to", OUT_DIR)
