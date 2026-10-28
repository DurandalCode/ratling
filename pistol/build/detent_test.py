# -*- coding: utf-8 -*-
"""
Ratling pistol, a quick test of the V-wedge detent without printing the block (or a PETG part).

Two thin sectors cut from the rear disc's rim, each with two V notches 60 deg apart (the block's index), on an
arm with a pivot hole; a jig with the detent housing in place (a peg for the sectors, the housing under it, as under
the block) and the detent bolt. Put the Ø4 pen spring in the housing's pocket, the bolt on it, the sector on the
peg, and turn it by hand: the bolt must ride out of one notch and drop into the next, with a click at 0 and 60 deg.

  sector A: the notches as in the block (NOTCH_RIM_W wide at the rim, 45 deg flanks)
  sector B: the same, NOTCH_EXTRA wider: a looser seat, for a print that comes out fat

Everything is drawn with the notch at the bottom (the housing is turned DETENT_ANGLE + 90 in the pistol; here it
is not). Writes exports/pistol_detent_test/ (STL in print orientation, FCStd).

Run inside FreeCAD (it builds pistol/hammer_assembly.py first):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/detent_test.py').read())
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

NAME = "pistol_detent_test"
OUT_DIR = os.path.join(REPO, "exports", NAME)
NOTCH_EXTRA = 0.4               # sector B's notch is this much wider at the rim
BAND_R0 = 36.0                  # the sector's rim band: HUB_R down to here
BAND_X1 = HUB_X0 + 11.0         # ... and as thick as the notch needs (notch x 3..9 on the disc)
ARM_W, ARM_T = 10.0, 4.0
PEG_D, HOLE_D = 4.6, 5.0        # a slip fit: print the peg and the hole as they are, ream the hole if tight
BASE_X0 = -3.0                  # the jig's back; the sector sits on the peg from HUB_X0

# ---------------------------------------------------------------- sectors
def notch_prism(extra):
    rw = (NOTCH_RIM_W + extra) / 2
    return prism_x([(-rw - 1, -HUB_R - 1), (rw + 1, -HUB_R - 1), (rw - NOTCH_V_DEPTH, -HUB_R + NOTCH_V_DEPTH),
                    (-rw + NOTCH_V_DEPTH, -HUB_R + NOTCH_V_DEPTH)], HUB_X0 + RIM_NOTCH[0], HUB_X0 + RIM_NOTCH[1])


def sector(extra):
    a0, a1 = -15.0, 75.0                                 # notches at 0 and 60 deg, 15 deg of rim each side
    ring = cyl_x(2 * HUB_R, HUB_X0, BAND_X1).cut(cyl_x(2 * BAND_R0, HUB_X0 - 1, BAND_X1 + 1))
    wedge = Part.Face(Part.makePolygon([V(0, 0, 0)] + [V(0, -80 * math.sin(math.radians(a)), -80 * math.cos(math.radians(a)))
                                                         for a in (a0, (a0 + a1) / 2, a1)] + [V(0, 0, 0)])).extrude(V(BAND_X1 + 1, 0, 0))
    wedge.translate(V(-1, 0, 0))
    s = ring.common(wedge)
    mid = (a0 + a1) / 2
    arm = turned(box(HUB_X0, HUB_X0 + ARM_T, -ARM_W / 2, ARM_W / 2, -BAND_R0 - 1, 0), -mid)    # from the pivot to the band
    boss = cyl_x(14, HUB_X0, HUB_X0 + ARM_T, 0, 0)
    s = s.fuse(arm).fuse(boss).cut(cyl_x(HOLE_D, HUB_X0 - 1, HUB_X0 + ARM_T + 1, 0, 0))
    for i in (0, 1):
        s = s.cut(turned(notch_prism(extra), 60 * i))
    return s.removeSplitter()


sec_a, sec_b = sector(0.0), sector(NOTCH_EXTRA)

# ---------------------------------------------------------------- jig: base strip, peg, the detent housing under it
bx0, bx1 = HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2
z_top, z_bot = -HUB_R - 1.5, -HUB_R - 24
housing = box(bx0, bx1, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2, z_bot, z_top)
channel = bolt_prism(-HUB_R + BOLT_DEPTH, BOLT_LEN).fuse(bolt_prism(-HUB_R, BOLT_LEN)).fuse(
    bolt_prism(-HUB_R, BOLT_LEN + 2).translated(V(0, 0, 3.0)))          # tip in the notch .. out, and room to push in
spring = Part.makeCylinder(2.15, 10.5, V(HUB_X0 + BOLT_X0 + BOLT[0] / 2, 0, -HUB_R - BOLT_LEN - 10.5), ZA)
strip_w = 8.0
base = box(BASE_X0, 0.0, -strip_w, strip_w, z_bot, 9.0)
tie = box(0.0, bx0 + 0.01, -strip_w, strip_w, z_bot, z_top)                  # the strip to the housing, behind the sector
peg = cyl_x(PEG_D, BASE_X0, HUB_X0 + ARM_T + 1.0, 0, 0).fuse(cyl_x(PEG_D + 3, BASE_X0, 0.0, 0, 0))
jig = base.fuse(tie).fuse(housing).fuse(peg).cut(channel).cut(spring).removeSplitter()
bolt = bolt_prism(-HUB_R + BOLT_DEPTH, BOLT_LEN)

# ---------------------------------------------------------------- checks
turns = [turned(sec_a, a_) for a_ in range(0, 61, 5)]
hits = {
    "sector A / jig, turned 0..60": max(hit(turned(sec_a, -a_), jig) for a_ in range(0, 61, 5)),
    "sector B / jig, turned 0..60": max(hit(turned(sec_b, -a_), jig) for a_ in range(0, 61, 5)),
    "bolt / jig (it moves in its channel)": max(hit(bolt.translated(V(0, 0, dz_)), jig) for dz_ in (0.0, -BOLT_DEPTH)),
    "bolt in the notch / sector A": hit(bolt, sec_a),
    "bolt in the notch / sector B": hit(bolt, sec_b),
}
print(NAME)
for k_, v_ in hits.items():
    print("  [%s] %s: %.2f mm3" % ("OK " if v_ < 0.05 else "FAIL", k_, v_))
rest = bolt.BoundBox
print("  bolt tip rests %.1f mm into the notch (V %.1f deep), stroke %.1f mm" % (BOLT_DEPTH, NOTCH_V_DEPTH, BOLT_DEPTH))
print("  peg Ø%.1f in hole Ø%.1f; spring pocket Ø4.3 x 10.5; PLA: %.1f + %.1f + %.1f cm3" % (
    PEG_D, HOLE_D, sec_a.Volume / 1000, sec_b.Volume / 1000, jig.Volume / 1000))

# ---------------------------------------------------------------- document and STL, printed with the -x face down
os.makedirs(os.path.join(OUT_DIR, "stl"), exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
for n, s, c in (("Sector_A", sec_a, (0.3, 0.7, 0.35)), ("Sector_B", sec_b, (0.9, 0.6, 0.2)), ("Jig", jig, (0.55, 0.62, 0.72)),
                ("Detent_bolt", bolt, (0.7, 0.72, 0.75))):
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart
for name_, shape_ in (("sector_a", sec_a), ("sector_b", sec_b), ("jig", jig), ("detent_bolt", bolt)):
    s_ = shape_.copy()
    rot_ = App.Rotation(V(-1, 0, 0), V(0, 0, -1))
    s_.rotate(V(0, 0, 0), rot_.Axis, math.degrees(rot_.Angle))
    bb_ = s_.BoundBox
    s_.translate(V(-bb_.XMin, -bb_.YMin, -bb_.ZMin))
    MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, "stl", name_ + ".stl"))
    print("  stl %-12s %.0f x %.0f x %.0f mm, valid %s" % (name_, s_.BoundBox.XLength, s_.BoundBox.YLength, s_.BoundBox.ZLength, s_.isValid()))
print("written to", OUT_DIR)
