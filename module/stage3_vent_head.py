# -*- coding: utf-8 -*-
"""
Ratling Stage 3 vent head: dump the pilot right at the valve cap.

On the bench the pilot is vented through the M3R110 at the end of a hose,
and the hose's own volume (a 6/4 hose holds ~1.3 cm3 per 10 cm) adds to the
pocket the diaphragm must push out before it opens. This head plugs
straight into the push-in fitting on the v1.1 cap and vents the pilot
there, through a Ø SEAT_D seat; the pilot is fed from the supply through a
jet, all the time. For the six-barrel pistol the same poppet sits at the
cap and the trigger pushes its stem through a rod. Built to be compared on
the bench against the M3R110 (option A).

    supply hose ─> barb ─> jet Ø JET_D ─┐
                                        ├─ chamber (= pilot) ─> spigot Ø6 ─> cap fitting
         poppet (6 x 1.5 O-ring face) ──┘   seat Ø SEAT_D ─> out (down)
         stem through the seat: push it up and the pilot dumps

The pilot pressure itself holds the poppet on its seat (plus a light
spring), so the head is shut whenever the stem is let go.

Parts, each exported in its print orientation (lowest point at z = 0):
    body ..... floor (seat) on the bed, chamber open at the top, a face
               O-ring groove round it; 4 pilot holes for ST2.9.
    lid ...... flat plate on the bed, the pilot spigot and the barb up.
    poppet ... upside down: spring boss on the bed, stem up.

Bought: O-rings 6 x 1.5 (poppet) and 18 x 2 (lid face), a pen spring
Ø ~4.5 cut to ~8 mm, ST2.9 x 9.5 x 4; the jet is a Ø1.2 hole (drill it
true after printing, or glue in a cut needle).

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_vent_head.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")

NAME = "stage3_vent_head"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector

# ---------------------------------------------------------------- parameters
P_BAR = 2.0
BLOCK = 30.0                        # square, x and y
FLOOR = 3.0
CHAMBER_D = 15.0
Z_TOP = 18.0                        # body top = the lid's underside
LID_T = 4.0
LID_ORING = (18.0, 2.0)
LID_GROOVE = (18.0, 22.4, 1.5)      # face groove ID, OD, depth (25 % squeeze)
SEAT_D = 5.0                        # vent orifice
SEAT_LIP = (6.2, 8.4, 0.8)          # lip ID, OD, height on the chamber floor
POPPET_D = 11.0
POPPET_T = 4.0
POPPET_ORING = (6.0, 1.5)
POPPET_GROOVE = (6.0, 9.8, 1.15)    # groove ID, OD, depth (in its face)
STEM_D = 2.5
STEM_OUT = 6.0                      # below the body when shut
LIFT = 1.6
SPRING_BOSS = (3.6, 2.0)            # Ø, height on the poppet's top (inside the spring)
SPRING = (4.6, 3.8)                 # OD, ID
PORT_X = 4.8                        # pilot port at -x, jet at +x
PILOT_SPIGOT = (6.0, 4.0, 14.0)     # OD, ID, length: into the cap's push-in fitting (6 mm collet)
BARB = (6.4, 7.2, 2.8, 12.0)        # shank, ridge, bore, length: 6/4 supply hose
JET_D, JET_LEN = 1.2, 5.0
SCREW_PILOT, SCREW_HOLE = 2.5, 3.2
SCREW_AT = 11.0                     # screws at (+-, +-) this

# ---------------------------------------------------------------- helpers
def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rounded_block(z0, z1):
    b = BLOCK / 2
    s = box(-b, b, -b, b, z0, z1)
    return s.makeFillet(3.0, [e for e in s.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1])


SCREWS = [(sx * SCREW_AT, sy * SCREW_AT) for sx in (-1, 1) for sy in (-1, 1)]

# ---------------------------------------------------------------- body (floor on the bed)
body = rounded_block(0, Z_TOP).cut(cyl(CHAMBER_D, FLOOR, Z_TOP + 1))
body = body.cut(cyl(SEAT_D, -1, FLOOR + 1))
body = body.fuse(cyl(SEAT_LIP[1], FLOOR - 0.01, FLOOR + SEAT_LIP[2]).cut(cyl(SEAT_LIP[0], 0, FLOOR + 2)))
body = body.cut(cyl(LID_GROOVE[1], Z_TOP - LID_GROOVE[2], Z_TOP + 1).cut(cyl(LID_GROOVE[0], 0, 100)))
for x, y in SCREWS:
    body = body.cut(cyl(SCREW_PILOT, Z_TOP - 10, Z_TOP + 1, x, y))
body = body.removeSplitter()

# ---------------------------------------------------------------- poppet (shut, body frame)
z_p0 = FLOOR + SEAT_LIP[2] - (POPPET_ORING[1] - POPPET_GROOVE[2])       # its face: the ring sits on the lip
z_p1 = z_p0 + POPPET_T
poppet = cyl(POPPET_D, z_p0, z_p1).fuse(cyl(SPRING_BOSS[0], z_p1 - 0.01, z_p1 + SPRING_BOSS[1]))
poppet = poppet.cut(cyl(POPPET_GROOVE[1], z_p0 - 1, z_p0 + POPPET_GROOVE[2]).cut(cyl(POPPET_GROOVE[0], z_p0 - 2, z_p0 + 2)))
poppet = poppet.fuse(cyl(STEM_D, -STEM_OUT, z_p0 + 0.01)).removeSplitter()
poppet_ring = Part.makeTorus((POPPET_GROOVE[0] + POPPET_GROOVE[1]) / 4, POPPET_ORING[1] / 2,
                             V(0, 0, z_p0 + POPPET_GROOVE[2] - POPPET_ORING[1] / 2))
spring = cyl(SPRING[0], z_p1, Z_TOP).cut(cyl(SPRING[1], 0, 100))

# ---------------------------------------------------------------- lid (body frame: plate on the body's top)
z_l1 = Z_TOP + LID_T
lid = rounded_block(Z_TOP, z_l1)
lid = lid.fuse(cyl(PILOT_SPIGOT[0], z_l1 - 0.01, z_l1 + PILOT_SPIGOT[2], -PORT_X))
lid = lid.fuse(cyl(BARB[0], z_l1 - 0.01, z_l1 + BARB[3], PORT_X))
zb = z_l1 + BARB[3]
lid = lid.fuse(Part.makeCone(BARB[1] / 2, BARB[0] / 2 - 0.3, 3.0, V(PORT_X, 0, zb - 6.0)))         # ridge
lid = lid.cut(cyl(PILOT_SPIGOT[1], Z_TOP - 1, z_l1 + PILOT_SPIGOT[2] + 1, -PORT_X))
lid = lid.cut(cyl(BARB[2], z_l1 + JET_LEN - 2, zb + 1, PORT_X))
lid = lid.cut(cyl(JET_D, Z_TOP - 1, z_l1 + JET_LEN - 1.99, PORT_X))
for x, y in SCREWS:
    lid = lid.cut(cyl(SCREW_HOLE, Z_TOP - 1, z_l1 + 1, x, y))
lid = lid.removeSplitter()
lid_ring = Part.makeTorus((LID_GROOVE[0] + LID_GROOVE[1]) / 4, LID_ORING[1] / 2, V(0, 0, Z_TOP - LID_ORING[1] / 2 + 0.5))

# ---------------------------------------------------------------- numbers and checks
area = lambda d: math.pi * d * d / 4
seal_d = (POPPET_GROOVE[0] + POPPET_GROOVE[1]) / 2                   # where the ring meets the lip
F_shut = P_BAR * 0.1 * area(seal_d)
A_vent = min(math.pi * SEAT_D * LIFT, area(SEAT_D) - area(STEM_D))
A_jet = area(JET_D)
spring_len = Z_TOP - z_p1
fill = (math.pi * POPPET_ORING[1] ** 2 / 4) / ((POPPET_GROOVE[1] - POPPET_GROOVE[0]) / 2 * POPPET_GROOVE[2])
port_clear = PORT_X - PILOT_SPIGOT[1] / 2 - SPRING[0] / 2
checks = {
    "body, lid, poppet valid single solids": all(s.isValid() and len(s.Solids) == 1 for s in (body, lid, poppet)),
    "poppet clear of body and lid, shut and open": all(
        p.common(body).Volume < 1e-3 and p.common(lid).Volume < 1e-3
        for p in (poppet, poppet.translated(V(0, 0, LIFT)))),
    "lid clear of the body": lid.common(body).Volume < 1e-3,
    "O-ring meets the seat lip (lip OD within the ring)": POPPET_GROOVE[0] < SEAT_LIP[1] < POPPET_GROOVE[1],
    "poppet groove fill <= 85 %%: %.0f %%" % (fill * 100): fill <= 0.85,
    "vent area >= the cap's pilot channel Ø4 (%.0f mm2)" % A_vent: A_vent >= area(4.0),
    "vent area >= 10 x the jet": A_vent >= 10 * A_jet,
    "spring room >= 5 mm at full lift (%.1f)" % (spring_len - SPRING_BOSS[1] - LIFT):
        spring_len - SPRING_BOSS[1] - LIFT >= 5.0,
    "ports clear of the spring (%.1f mm)" % port_clear: port_clear >= 0.3,
    "ports inside the chamber": PORT_X + PILOT_SPIGOT[1] / 2 <= CHAMBER_D / 2 - 0.5,
    "screw holes clear of the face groove": SCREW_AT * math.sqrt(2) - SCREW_PILOT / 2 >= LID_GROOVE[1] / 2 + 1.0,
}
print(NAME)
print("  vent: seat Ø%.0f, lift %.1f -> %.0f mm2 (cap channel Ø4 = %.0f); jet Ø%.1f = %.1f mm2"
      % (SEAT_D, LIFT, A_vent, area(4.0), JET_D, A_jet))
print("  held shut by %.1f N at %.0f bar (+ spring): the stem needs that to fire" % (F_shut, P_BAR))
for k, v in checks.items():
    print("  [%s] %s" % ("OK " if v else "FAIL", k))

# ---------------------------------------------------------------- document and export
if App.GuiUp:
    if NAME in App.listDocuments():
        App.closeDocument(NAME)
    doc = App.newDocument(NAME)
    for n, s_, c, tr in (("Body", body, (0.45, 0.65, 0.85), 50), ("Lid", lid, (0.8, 0.5, 0.2), 40),
                         ("Poppet", poppet, (0.9, 0.8, 0.2), 0), ("Poppet_ring", poppet_ring, (0.8, 0.1, 0.1), 0),
                         ("Lid_ring", lid_ring, (0.8, 0.1, 0.1), 0), ("Spring", spring, (0.6, 0.6, 0.6), 0)):
        o = doc.addObject("Part::Feature", n)
        o.Shape = s_
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = tr
    doc.recompute()

import MeshPart
os.makedirs(OUT_DIR, exist_ok=True)
poppet_print = poppet.copy()
poppet_print.rotate(V(0, 0, 0), V(1, 0, 0), 180)                     # boss on the bed, stem up
for n, s_ in (("body", body), ("lid", lid), ("poppet", poppet_print)):
    s_ = s_.copy()
    s_.translate(V(0, 0, -s_.BoundBox.ZMin))
    s_.exportStep(os.path.join(OUT_DIR, n + ".step"))
    MeshPart.meshFromShape(Shape=s_, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, n + ".stl"))
print("  written to", OUT_DIR)
