# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v3: coaxial diaphragm valve, chamber behind, barrel ahead.

The valve of Stage 3 (a rubber diaphragm, pilot behind it, no sliding seal),
folded onto one axis. Stage 3 v2's piston leaked past its seat and was given
up; this keeps v1's physics and its sheet rubber:

    chamber tube ──> cap spigot ──> slanted channels ──> passage ring (holes
    through cap, diaphragm and body face) ──> gallery round the seat ──> seat
    (Ø SEAT_D, on the axis) ──> barrel spigot ──> barrel tube

    pilot (cap pocket, behind the diaphragm) up: the diaphragm sits on the seat
    and the chamber charges from the pilot through a bleed hole in it.
    pilot vented: chamber pressure on the annulus outside the seat lifts the
    diaphragm into the pocket, and the chamber dumps straight into the barrel.

Parts, each exported in its print orientation (lowest point at z = 0):

    body ........ clamp face on the bed, barrel spigot up. Seat land, clamp
                  face and the ribs that carry the diaphragm while the pilot
                  is up and the chamber empty are the bed face. The passage
                  holes open into the gallery above the clamp ring; 45 deg
                  roof; pillars round the tie rods; M3 nut pockets on top.
    cap ......... clamp face up, chamber spigot down: pilot pocket (= lift)
                  with floor grooves, sealing beads and stop pins on the face,
                  slanted passage channels from the spigot bore out to the
                  ring, G1/8 pilot port in the side (spot face at 45 deg),
                  45 deg underside with countersunk seats for the rod heads.
    diaphragm ... one disc of rubber sheet (DIA_T, NBR/EPDM ~60 A): valve
                  membrane in the middle, gasket for the passage ring round
                  it. Holes: passages, tie rods (tight, they seal), stop pins,
                  bleed. The STL is the punching template.
    chamber plug  blind, closes the chamber's far end (Stage 3's).

The diaphragm's squeeze is set by the stop pins (DIA_SQUEEZE); the two beads
sink further into it on the inner and outer clamp rings (the v1 fix). The tie
rods pass through the passage ring and are sealed by the rubber round them.
Print PETG or PLA (<= 2 bar), 100 % infill.

Bench hookup with the AirTAC M3R110 (inverted): supply -> R, A -> pilot port
on the cap, P open. Pressing the roller vents the pilot and the module fires.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3v3_coaxial.py').read())
"""

import importlib
import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
try:
    STAGE3V3_LIBRARY
except NameError:
    STAGE3V3_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

OUT_DIR = os.path.join(REPO, "exports", "stage3v3_coaxial")
NAME = "stage3v3_coaxial"

# ---------------------------------------------------------------- parameters
P_WORK_BAR, P_MAX_BAR = 2.0, 5.0

TUBE_ID = 23.8
TUBE_WALL = 0.59
TUBE_OD = TUBE_ID + 2 * TUBE_WALL
BARREL_LEN = 300.0
CHAMBER_V = 100.0           # cm3 target

# Tube gland = connectors/tube_plug_v1 (fit confirmed)
RADIAL_CLEAR = 0.20
ORING_ID, ORING_CS = 11 / 16 * 25.4, 1 / 8 * 25.4
ORING_SQUEEZE = 0.12
GROOVE_ROOT_W = 1.1 * ORING_CS
GROOVE_WALL_FROM_TIP = 9.0
LEAD_CHAMFER = 1.0
SPIGOT_LEN = 24.0
SCREW_PILOT_D, SCREW_DEPTH, SCREW_L = 2.5, 3.8, 4.5   # ST2.9 x 4.5
SCREW_FROM_TUBE_END = 6.0

# Valve, radii from the axis
BODY_R = 23.0
SEAT_D = 11.0               # = barrel spigot bore
SEAT_LAND = 1.5
GALLERY_R = 11.5            # pocket and gallery radius under the mouth chamfer
MOUTH_CHAMFER = 1.0         # free diaphragm Ø = 2 * (GALLERY_R + MOUTH_CHAMFER)
RING_R = 17.5               # passage ring: holes, tie rods, stop pins
PASS_D = 5.0                # passage holes (punch Ø5 in the diaphragm)
PASS_ANGLES = (112.5, 157.5, 202.5, 247.5, 292.5, 337.5)  # none in the pilot quadrant
ROD_ANGLES = (0.0, 90.0, 180.0, 270.0)
PIN_ANGLES = (45.0, 135.0, 225.0, 315.0)
PIN_D = 2.0
PIN_HOLE_D = 3.5            # in the diaphragm
ROD_HOLE_D = 3.4            # M3
ROD_DIA_HOLE_D = 3.0        # in the diaphragm: tight on the rod, it seals there
PILLAR_D = 7.0              # round the rods through the body gallery
NUT_AF, NUT_CLEAR, NUT_T, NUT_POCKET = 5.5, 0.2, 2.4, 2.6
# Countersunk M3 (DIN 7991): its 90 deg seat prints with no bridge from below
HEAD_D, HEAD_H, HEAD_CB_D = 6.0, 1.7, 6.4

# Diaphragm
DIA_T = 1.5
DIA_SQUEEZE = 0.20          # stop pins
DIA_R = BODY_R - 0.75
BEAD_W = (1.2, 0.4)         # base, top
BEAD_H = 0.4
# A bead ring round each tie rod too: on the v1 bench the air found its way
# out along the rods. Here they stand in chamber air, so the rubber must close
# round each one.
ROD_BEAD_R = 2.85
BLEED_D = 0.8
BLEED_R = 9.5
BLEED_ANGLE = 0.0           # ribs at half steps clear it

# Body
RING_H = 2.5                # clamp ring under the gallery's widening
GALLERY_H = 3.0             # straight part above it; 45 deg roof above that
ROOF_T = 2.5
RIB_N, RIB_W, RIB_H = 8, 1.5, 3.0

# Cap
LIFT = 4.0                  # pocket depth
GROOVE_N, GROOVE_W, GROOVE_DEPTH, GROOVE_LEN = 4, 2.0, 0.6, 10.0
CHAN_D = 4.5                # slanted passage channels
CHAN_AXIAL = 4.0            # straight down from the face before turning in
CHAN_END_R = 5.0
SPIGOT_BORE_D = 13.0
CAP_SIDE_H = 14.0           # cylindrical side; 45 deg underside below it
# The 45 deg underside starts at the spigot root; the chamber tube's end stops
# on it (a flat land there was an overhang Bambu Studio flagged).
PILOT_Z = -7.2
PILOT_ANGLE = 45.0
G18_TAP_D, G18_TAP_DEPTH = 8.8, 8.0
SPOT_FACE_R = 22.0          # flat for the fitting's seal
PILOT_CH_D = 3.0
PILOT_UP_D = 3.5

# Drilling template for the diaphragm: the rubber lies on a base whose two pins
# (at two rod holes) pierce it; a guide disc of the diaphragm's own Ø goes on
# the same pins. Drill through the guides, cut the outline round the disc.
JIG_GUIDE_CLEAR = 0.15      # guide hole over the drill
JIG_RELIEF = 1.0            # base relief hole over the drill
JIG_GUIDE_T = 5.0
JIG_BASE_T = 4.0
JIG_BASE_SIDE = 2 * DIA_R + 14.0
JIG_PIN_D = 2.9
JIG_PIN_ANGLES = (0.0, 180.0)

# Chamber plug (Stage 3's)
PLUG_INSERT_LEN = 30.0
PLUG_FLANGE_T = 5.0
PLUG_FLANGE_D = TUBE_OD + 2.0

# ---------------------------------------------------------------- derived
X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector
spigot_r = TUBE_ID / 2 - RADIAL_CLEAR
groove_depth = ORING_CS * (1 - ORING_SQUEEZE)
root_r = TUBE_ID / 2 - groove_depth
oring_stretch = 2 * root_r / ORING_ID - 1
seat_r = SEAT_D / 2
seat_out_r = seat_r + SEAT_LAND
mouth_r = GALLERY_R + MOUTH_CHAMFER
t_c = DIA_T * (1 - DIA_SQUEEZE)             # clamped diaphragm; body face at z = t_c
pass_out_r = RING_R + PASS_D / 2
pass_in_r = RING_R - PASS_D / 2
bead_in_r = (mouth_r + pass_in_r) / 2
bead_out_r = (pass_out_r + DIA_R) / 2
z_ring = t_c + RING_H
z_gal = z_ring + GALLERY_H
roof_in_r = seat_out_r
z_roof = z_gal + (pass_out_r - roof_in_r)   # roof apex at the seat tube
z_bt = z_roof + ROOF_T                      # body top
z_tip = z_bt + SPIGOT_LEN                   # barrel spigot tip = ball stop
z_a = -CHAN_AXIAL
z_ce = z_a - (RING_R - CHAN_END_R)          # channel end in the spigot bore
z_bc = z_ce - (SPIGOT_BORE_D / 2 - CHAN_END_R)   # bore cone base (r = bore)
z_oc = -CAP_SIDE_H
z_cb = z_oc - (BODY_R - spigot_r)           # spigot root; the tube end stops on the cone just behind it
z_ctip = z_cb - SPIGOT_LEN
z_head = -16.0                              # top of the countersunk rod heads


def P2(r, z):
    return V(r, 0, z)


def revolve(rz):
    pts = [P2(r, z) for r, z in rz]
    s = Part.Face(Part.makePolygon(pts + [pts[0]])).revolve(V(0, 0, 0), Z, 360)
    return Part.Solid(s) if s.ShapeType != "Solid" else s


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def at(r, a_deg, z=0.0):
    a = math.radians(a_deg)
    return V(r * math.cos(a), r * math.sin(a), z)


def rod_between(p0, p1, d):
    """Cylinder Ø d from p0 to p1 with ball ends, for channels with a bend."""
    v = p1 - p0
    return Part.makeCylinder(d / 2, v.Length, p0, v).fuse(Part.makeSphere(d / 2, p1)).fuse(
        Part.makeSphere(d / 2, p0))


def spigot_up(z_root, z_tip_):
    """Tube gland, tip at larger z, printed tip up: square groove wall below
    (floor), 45 deg wall above (ceiling)."""
    g0 = z_tip_ - GROOVE_WALL_FROM_TIP
    g1 = g0 + GROOVE_ROOT_W
    g2 = g1 + (spigot_r - root_r)
    return revolve([(0, z_root), (spigot_r, z_root), (spigot_r, g0), (root_r, g0), (root_r, g1), (spigot_r, g2),
                    (spigot_r, z_tip_ - LEAD_CHAMFER), (spigot_r - LEAD_CHAMFER, z_tip_), (0, z_tip_)]), (g0, g2)


def spigot_down(z_root, z_tip_):
    """Tube gland, tip at smaller z, printed tip down: square groove wall at
    the tip side (floor), 45 deg wall at the root side (ceiling)."""
    g0 = z_tip_ + GROOVE_WALL_FROM_TIP
    g1 = g0 + GROOVE_ROOT_W
    g2 = g1 + (spigot_r - root_r)
    return revolve([(0, z_tip_), (spigot_r - LEAD_CHAMFER, z_tip_), (spigot_r, z_tip_ + LEAD_CHAMFER),
                    (spigot_r, g0), (root_r, g0), (root_r, g1), (spigot_r, g2), (spigot_r, z_root),
                    (0, z_root)]), (g0, g2)


def screw_pilots(z, angles):
    out = []
    for a in angles:
        d = at(1, a)
        out.append(Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_DEPTH + 1, d * (spigot_r + 1) + V(0, 0, z), -d))
    return out


def nut_pocket(a, z0, z1):
    r = (NUT_AF + 2 * NUT_CLEAR) / math.sqrt(3)
    c = at(RING_R, a)
    pts = [V(c.x + r * math.cos(math.radians(a + 30 + 60 * k)), c.y + r * math.sin(math.radians(a + 30 + 60 * k)), z0)
           for k in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))   # a flat faces outward


# ---------------------------------------------------------------- body
body = cyl(2 * BODY_R, t_c, z_bt)
barrel_sp, front_groove = spigot_up(z_bt - 0.5, z_tip)
body = body.fuse(barrel_sp)
gallery = revolve([(seat_out_r, t_c - 1), (mouth_r + 1, t_c - 1), (GALLERY_R, t_c + MOUTH_CHAMFER),
                   (GALLERY_R, z_ring), (pass_out_r, z_ring), (pass_out_r, z_gal), (roof_in_r, z_roof)])
cuts = [gallery, cyl(SEAT_D, t_c - 1, z_tip + 1)]
cuts += [cyl(PASS_D, t_c - 1, z_ring + 0.01, *at(RING_R, a)[:2]) for a in PASS_ANGLES]
body = body.cut(G.fuse_all(cuts))
for a in ROD_ANGLES:
    body = body.fuse(cyl(PILLAR_D, z_ring - 0.01, z_roof, *at(RING_R, a)[:2]).common(cyl(2 * BODY_R, t_c, z_bt)))
for i in range(RIB_N):
    rib = Part.makeBox(GALLERY_R - seat_out_r + 1.0, RIB_W, RIB_H, V(seat_out_r - 0.5, -RIB_W / 2, t_c))
    rib.rotate(V(0, 0, 0), Z, 360.0 / RIB_N * (i + 0.5))
    body = body.fuse(rib)
cuts = [cyl(ROD_HOLE_D, t_c - 1, z_bt + 1, *at(RING_R, a)[:2]) for a in ROD_ANGLES]
cuts += [nut_pocket(a, z_bt - NUT_POCKET, z_bt + 1) for a in ROD_ANGLES]
cuts += screw_pilots(z_bt + SCREW_FROM_TUBE_END, (60.0, 180.0, 300.0))
body = body.cut(G.fuse_all(cuts))           # removeSplitter() leaves it invalid here

# ---------------------------------------------------------------- cap
cap = revolve([(0, z_cb), (spigot_r, z_cb), (BODY_R, z_oc), (BODY_R, 0), (0, 0)])
chamber_sp, rear_groove = spigot_down(z_cb + 0.5, z_ctip)
cap = cap.fuse(chamber_sp)
for r in (bead_in_r, bead_out_r):
    cap = cap.fuse(revolve([(r - BEAD_W[0] / 2, -0.01), (r + BEAD_W[0] / 2, -0.01),
                            (r + BEAD_W[1] / 2, BEAD_H), (r - BEAD_W[1] / 2, BEAD_H)]))
for a in ROD_ANGLES:
    c = at(RING_R, a)
    b = revolve([(ROD_BEAD_R - BEAD_W[0] / 2, -0.01), (ROD_BEAD_R + BEAD_W[0] / 2, -0.01),
                 (ROD_BEAD_R + BEAD_W[1] / 2, BEAD_H), (ROD_BEAD_R - BEAD_W[1] / 2, BEAD_H)])
    b.translate(c)
    cap = cap.fuse(b)
for a in PIN_ANGLES:
    cap = cap.fuse(cyl(PIN_D, -0.01, t_c, *at(RING_R, a)[:2]))
# chamber side: spigot bore, its 45 deg roof, the slanted channels
chamber_cuts = [revolve([(0, z_ctip - 1), (SPIGOT_BORE_D / 2, z_ctip - 1), (SPIGOT_BORE_D / 2, z_bc),
                         (0, z_bc + SPIGOT_BORE_D / 2)])]
for a in PASS_ANGLES:
    p_face, p_bend, p_end = at(RING_R, a, 0.5), at(RING_R, a, z_a), at(CHAN_END_R, a, z_ce)
    chamber_cuts.append(cyl(CHAN_D, z_a, 0.5, p_face.x, p_face.y).fuse(rod_between(p_bend, p_end, CHAN_D)))
# pilot side: pocket with mouth chamfer and floor grooves, centre hole, radial channel, G1/8 tap, spot face
pilot_cuts = [revolve([(0, -LIFT), (GALLERY_R, -LIFT), (GALLERY_R, -MOUTH_CHAMFER), (mouth_r, 0),
                       (mouth_r, 1), (0, 1)]),
              cyl(PILOT_UP_D, PILOT_Z, -LIFT + 0.01)]
for i in range(GROOVE_N):
    g = Part.makeBox(GROOVE_LEN, GROOVE_W, GROOVE_DEPTH + 0.5, V(0, -GROOVE_W / 2, -LIFT - GROOVE_DEPTH))
    g.rotate(V(0, 0, 0), Z, 360.0 / GROOVE_N * i + PILOT_ANGLE)
    pilot_cuts.append(g)
tap_in_r = SPOT_FACE_R - G18_TAP_DEPTH
for d, x0, x1 in ((PILOT_CH_D, 0.0, tap_in_r + 0.5), (G18_TAP_D, tap_in_r, BODY_R + 1)):
    t = G.teardrop_x(d, x0, x1, PILOT_Z)
    t.rotate(V(0, 0, 0), Z, PILOT_ANGLE)
    pilot_cuts.append(t)
spot = Part.makeBox(BODY_R, 2 * BODY_R, 2 * BODY_R, V(SPOT_FACE_R, -BODY_R, PILOT_Z - BODY_R))
spot.rotate(V(0, 0, 0), Z, PILOT_ANGLE)
pilot_cuts.append(spot)
rod_cuts = []
for a in ROD_ANGLES:
    c = at(RING_R, a)
    rod_cuts += [cyl(ROD_HOLE_D, z_head - 1, 1, c.x, c.y),
                 cyl(HEAD_CB_D, z_cb - 1, z_head, c.x, c.y).fuse(
                     Part.makeCone(HEAD_CB_D / 2, ROD_HOLE_D / 2, (HEAD_CB_D - ROD_HOLE_D) / 2, V(c.x, c.y, z_head)))]
rod_cuts += screw_pilots(z_cb - SCREW_FROM_TUBE_END, (0.0, 120.0, 240.0))
cap_solid = cap
cap = cap.cut(G.fuse_all(chamber_cuts + pilot_cuts + rod_cuts)).removeSplitter()

# ---------------------------------------------------------------- diaphragm (clamped, in place)
diaphragm = cyl(2 * DIA_R, 0, t_c)
dcuts = [cyl(PASS_D, -1, t_c + 1, *at(RING_R, a)[:2]) for a in PASS_ANGLES]
dcuts += [cyl(ROD_DIA_HOLE_D, -1, t_c + 1, *at(RING_R, a)[:2]) for a in ROD_ANGLES]
dcuts += [cyl(PIN_HOLE_D, -1, t_c + 1, *at(RING_R, a)[:2]) for a in PIN_ANGLES]
dcuts.append(cyl(BLEED_D, -1, t_c + 1, *at(BLEED_R, BLEED_ANGLE)[:2]))
diaphragm = diaphragm.cut(G.fuse_all(dcuts))
diaphragm_free = cyl(2 * DIA_R, 0, DIA_T).cut(G.fuse_all(dcuts))     # template, uncompressed

# ---------------------------------------------------------------- chamber plug (print frame)
plug_print = revolve([(0, 0), (PLUG_FLANGE_D / 2 - 0.5, 0), (PLUG_FLANGE_D / 2, 0.5),
                      (PLUG_FLANGE_D / 2, PLUG_FLANGE_T), (0, PLUG_FLANGE_T)])
plug_sp, plug_groove = spigot_up(PLUG_FLANGE_T - 0.5, PLUG_FLANGE_T + PLUG_INSERT_LEN)
plug_print = plug_print.fuse(plug_sp)
plug_print = plug_print.cut(G.fuse_all(screw_pilots(PLUG_FLANGE_T + SCREW_FROM_TUBE_END, (0.0, 120.0, 240.0))))
plug_print = plug_print.removeSplitter()

# ---------------------------------------------------------------- diaphragm drilling template (print frames)
jig_holes = ([(RING_R, a, PASS_D) for a in PASS_ANGLES] + [(RING_R, a, ROD_DIA_HOLE_D) for a in ROD_ANGLES]
             + [(RING_R, a, PIN_HOLE_D) for a in PIN_ANGLES] + [(BLEED_R, BLEED_ANGLE, BLEED_D)])
jig_base = Part.makeBox(JIG_BASE_SIDE, JIG_BASE_SIDE, JIG_BASE_T, V(-JIG_BASE_SIDE / 2, -JIG_BASE_SIDE / 2, 0))
jig_base = jig_base.cut(G.fuse_all([cyl(d + JIG_RELIEF, -1, JIG_BASE_T + 1, *at(r, a)[:2]) for r, a, d in jig_holes
                                    if not (r == RING_R and a in JIG_PIN_ANGLES and d == ROD_DIA_HOLE_D)]))
for a in JIG_PIN_ANGLES:
    c = at(RING_R, a)
    pin_top = JIG_BASE_T + DIA_T + JIG_GUIDE_T - 1.0
    jig_base = jig_base.fuse(cyl(JIG_PIN_D, JIG_BASE_T - 0.01, pin_top - 0.8, c.x, c.y))
    jig_base = jig_base.fuse(Part.makeCone(JIG_PIN_D / 2, 0.6, 0.8, V(c.x, c.y, pin_top - 0.81)))   # point pierces
jig_base = jig_base.removeSplitter()
jig_guide = cyl(2 * DIA_R, 0, JIG_GUIDE_T).cut(G.fuse_all([cyl(d + JIG_GUIDE_CLEAR, -1, JIG_GUIDE_T + 1, *at(r, a)[:2]) for r, a, d in jig_holes]))
mark = Part.makeCone(0, 1.2, 1.2, V(*at(DIA_R - 2.0, PILOT_ANGLE)[:2], JIG_GUIDE_T - 1.19))   # dimple: pilot quadrant
jig_guide = jig_guide.cut(mark).removeSplitter()

# ---------------------------------------------------------------- module assembly
area = lambda d: math.pi * d * d / 4
A_tube = area(TUBE_ID)
chamber_extra_v = (G.fuse_all(chamber_cuts).common(cap_solid).Volume
                   + G.fuse_all([gallery] + [cyl(PASS_D, t_c - 1, z_ring + 0.01, *at(RING_R, a)[:2])
                                             for a in PASS_ANGLES]).common(cyl(2 * BODY_R, t_c, z_bt)).Volume
                   + sum(area(PASS_D) * t_c for _ in PASS_ANGLES)) / 1000
chamber_tube_len = (CHAMBER_V - chamber_extra_v) * 1000 / A_tube + SPIGOT_LEN + PLUG_INSERT_LEN
z_end = z_cb - chamber_tube_len
tube_wall = lambda z0, z1: cyl(TUBE_OD, z0, z1).cut(cyl(TUBE_ID, z0 - 1, z1 + 1))
barrel = tube_wall(z_bt, z_bt + BARREL_LEN)
chamber = tube_wall(z_end, z_cb)
plug_a = plug_print.copy()                  # spigot forward into the tube, flange on its end
plug_a.translate(V(0, 0, z_end - PLUG_FLANGE_T))
rod_len = 5 * math.ceil((z_bt - NUT_POCKET + NUT_T - z_head) / 5)

# ---------------------------------------------------------------- numbers
A_seat = area(SEAT_D)
A_seat_eff = area(SEAT_D + SEAT_LAND)
A_dia = area(2 * mouth_r)
A_curtain = math.pi * SEAT_D * LIFT
A_pass = len(PASS_ANGLES) * area(PASS_D)
A_mouth_gal = 2 * math.pi * mouth_r * GALLERY_H          # inward over the clamp ring
open_ratio = 1 - A_seat_eff / A_dia
pocket_v = (area(2 * GALLERY_R) * LIFT + area(PILOT_UP_D) * (-PILOT_Z - LIFT) + area(PILOT_CH_D) * tap_in_r) / 1000
dead_v = A_seat * (z_tip - t_c) / 1000
A_seal_out = area(2 * bead_out_r)
F_clamp = P_MAX_BAR * 0.1 * A_seal_out
rod_pts = [at(RING_R, a) for a in ROD_ANGLES]
hex_r = (NUT_AF + 2 * NUT_CLEAR) / math.sqrt(3)
hex_flat = NUT_AF / 2 + NUT_CLEAR


def chord(a1, a2, r=RING_R):
    return 2 * r * abs(math.sin(math.radians((a1 - a2) / 2)))


ring_items = [(a, PASS_D / 2) for a in PASS_ANGLES] + [(a, ROD_HOLE_D / 2) for a in ROD_ANGLES] + \
             [(a, PIN_HOLE_D / 2) for a in PIN_ANGLES]
ring_gap = min(chord(a1, a2) - r1 - r2 for i, (a1, r1) in enumerate(ring_items) for a2, r2 in ring_items[i + 1:])
pilot_clear = min(chord(PILOT_ANGLE, a, tap_in_r) - G18_TAP_D / 2 - PASS_D / 2 for a in PASS_ANGLES)

checks = [
    ("body, cap, chamber plug valid single solids", all(G.single_solid(s) for s in (body, cap, plug_print))),
    ("cap / diaphragm / body clear (beads and pins aside)",
     G.no_overlap(body, diaphragm) and G.no_overlap(cap.cut(cyl(2 * BODY_R + 2, -0.02, t_c + 1)), diaphragm)
     and G.no_overlap(body, cap)),
    ("stop pins reach the body face", abs(cap.BoundBox.ZMax - t_c) < 1e-6),
    ("seat curtain >= seat area (lift %.1f)" % LIFT, A_curtain >= A_seat),
    ("passages >= 1.2 x seat (%.0f mm2)" % A_pass, A_pass >= 1.2 * A_seat),
    ("gallery over the clamp ring >= 1.5 x seat (%.0f mm2)" % A_mouth_gal, A_mouth_gal >= 1.5 * A_seat),
    ("opens after the pilot loses <= 30 %% (%.0f %%)" % (open_ratio * 100), open_ratio >= 0.70),
    ("inner clamp ring >= 2 mm (%.1f)" % (pass_in_r - mouth_r), pass_in_r - mouth_r >= 2.0),
    ("outer clamp ring >= 1.5 mm (%.1f)" % (DIA_R - pass_out_r), DIA_R - pass_out_r >= 1.5),
    ("beads inside their rings, >= 0.3 mm from the edges",
     bead_in_r - BEAD_W[0] / 2 >= mouth_r + 0.3 and bead_in_r + BEAD_W[0] / 2 <= pass_in_r - 0.3
     and bead_out_r - BEAD_W[0] / 2 >= pass_out_r + 0.3 and bead_out_r + BEAD_W[0] / 2 <= DIA_R - 0.3),
    ("rod beads clear of the rod hole and the next holes by >= 0.5 mm",
     ROD_BEAD_R - BEAD_W[0] / 2 >= ROD_HOLE_D / 2 + 0.5
     and min(chord(r, p) for r in ROD_ANGLES for p in PASS_ANGLES) - PASS_D / 2 >= ROD_BEAD_R + BEAD_W[0] / 2 + 0.5
     and min(chord(r, p) for r in ROD_ANGLES for p in PIN_ANGLES) - PIN_HOLE_D / 2 >= ROD_BEAD_R + BEAD_W[0] / 2 + 0.5),
    ("squeeze under the beads 30..50 %", 0.30 <= (DIA_T - t_c + BEAD_H) / DIA_T <= 0.50),
    ("holes on the ring >= 1.5 mm apart (%.1f)" % ring_gap, ring_gap >= 1.5),
    ("bleed hole over the gallery, clear of seat and mouth", seat_out_r + 2 <= BLEED_R <= mouth_r - 2),
    ("bleed hole clear of the ribs",
     min(abs(BLEED_R * math.radians(((BLEED_ANGLE - 360.0 / RIB_N * (i + 0.5)) + 180) % 360 - 180))
         for i in range(RIB_N)) >= RIB_W / 2 + BLEED_D / 2 + 1.0),
    ("G1/8 tap clear of the passage channels (%.1f)" % pilot_clear, pilot_clear >= 1.5),
    ("G1/8 tap below the clamp face >= 2 mm", -PILOT_Z - G18_TAP_D / 2 >= 2.0),
    ("G1/8 tap above the 45 deg underside", PILOT_Z - G18_TAP_D / 2 >= z_oc + 1.0),
    ("tap clear of the pocket", tap_in_r >= mouth_r + 1.0),
    ("pilot channel >= 1 mm under the pocket floor grooves",
     -LIFT - GROOVE_DEPTH - (PILOT_Z + PILOT_CH_D / 2) >= 1.0),
    ("pilot channel >= 1.5 mm above the spigot bore roof",
     PILOT_Z - PILOT_CH_D / 2 - (z_bc + SPIGOT_BORE_D / 2) >= 1.5),
    ("pilot side clear of the chamber side", G.no_overlap(G.fuse_all(pilot_cuts[:-1]), G.fuse_all(chamber_cuts))),
    ("channels >= 1.5 mm under the pocket",
     all(G.fuse_all(pilot_cuts[:1]).distToShape(c)[0] >= 1.5 for c in chamber_cuts[1:])),
    ("rod holes clear of the channels and the tap",
     all(G.no_overlap(r, c) for r in rod_cuts[:2 * len(ROD_ANGLES)] for c in chamber_cuts + pilot_cuts[:-1])),
    ("nut pockets inside the body (wall >= 0.8) and clear of the barrel tube",
     BODY_R - (RING_R + hex_flat) >= 0.8 and RING_R - hex_r - TUBE_OD / 2 >= 1.0),
    ("rod heads clear of the chamber tube", RING_R - HEAD_CB_D / 2 - TUBE_OD / 2 >= 1.0),
    ("chamber tube end stops on the underside <= 1 mm behind the spigot root", TUBE_OD / 2 - spigot_r <= 1.0),
    ("wall groove root -> bore >= 2 mm", root_r - max(SEAT_D, SPIGOT_BORE_D) / 2 >= 2.0),
    ("wall screw pilot -> bore >= 1.4 mm", spigot_r - SCREW_DEPTH - SPIGOT_BORE_D / 2 >= 1.4 - 1e-9),
    ("screw tip inside its pilot", TUBE_OD / 2 - SCREW_L >= spigot_r - SCREW_DEPTH),
    ("barrel screws outboard of the O-ring", z_bt + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < front_groove[0] - 1.0),
    ("chamber screws outboard of the O-ring", z_cb - SCREW_FROM_TUBE_END - SCREW_PILOT_D / 2 > rear_groove[1] + 1.0),
    ("plug screws outboard of its O-ring",
     PLUG_FLANGE_T + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < plug_groove[0] - 1.0),
    ("tube O-ring stretch 0..6 %", 0 <= oring_stretch <= 0.06),
    ("drilling template: base and guide valid single solids", G.single_solid(jig_base) and G.single_solid(jig_guide)),
    ("drilling template: pins go into the guide, >= 1 mm short of its top",
     JIG_PIN_D < ROD_DIA_HOLE_D + JIG_GUIDE_CLEAR and jig_base.BoundBox.ZMax <= JIG_BASE_T + DIA_T + JIG_GUIDE_T - 1.0 + 1e-6),
    ("rod reaches through the nut, tip clear of the barrel screws",
     z_head + rod_len >= z_bt - NUT_POCKET + NUT_T and z_head + rod_len <= z_bt + 3.0),
]

report = [
    NAME,
    "  flow path              : seat Ø%.0f (%.0f mm2), curtain %.0f at lift %.1f, passages %d x Ø%.0f = %.0f, gallery %.0f"
    % (SEAT_D, A_seat, A_curtain, LIFT, len(PASS_ANGLES), PASS_D, A_pass, A_mouth_gal),
    "  diaphragm              : Ø%.1f x %.1f, free Ø%.0f, squeeze %.0f %% (pins), %.0f %% under the beads"
    % (2 * DIA_R, DIA_T, 2 * mouth_r, DIA_SQUEEZE * 100, (DIA_T - t_c + BEAD_H) / DIA_T * 100),
    "  diaphragm holes        : %d x Ø%.0f passages, %d x Ø%.0f rods (tight), %d x Ø%.1f pins on R%.1f; bleed Ø%.1f at R%.1f"
    % (len(PASS_ANGLES), PASS_D, len(ROD_ANGLES), ROD_DIA_HOLE_D, len(PIN_ANGLES), PIN_HOLE_D, RING_R,
       BLEED_D, BLEED_R),
    "  opens when pilot < %.0f %% of chamber pressure (gauge)" % (open_ratio * 100),
    "  pilot volume           : %.1f cm3 (pocket and channels), G1/8 in the cap side at %.0f deg"
    % (pocket_v, PILOT_ANGLE),
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  chamber %.0f cm3        : tube %.0f mm (cap adds %.1f cm3)" % (CHAMBER_V, chamber_tube_len, chamber_extra_v),
    "  valve                  : Ø%.0f, %.0f mm from chamber tube end to barrel tube end"
    % (2 * BODY_R, z_bt - z_cb),
    "  module                 : %.0f mm long with a %.0f mm barrel" % (z_bt + BARREL_LEN - z_end, BARREL_LEN),
    "  @ %.0f bar               : cap %.0f N (%.0f N per M3)" % (P_MAX_BAR, F_clamp, F_clamp / len(ROD_ANGLES)),
    "  tie rods               : %d x M3 x %d countersunk (DIN 7991, heads in the cap) + nut in the body"
    % (len(ROD_ANGLES), rod_len),
    "  body / cap / plug      : %.1f / %.1f / %.1f cm3" % (body.Volume / 1000, cap.Volume / 1000,
                                                          plug_print.Volume / 1000),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
if not STAGE3V3_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- references
orings = G.fuse_all([
    G.oring(2 * root_r, ORING_CS, front_groove[0] + GROOVE_ROOT_W / 2),
    G.oring(2 * root_r, ORING_CS, rear_groove[0] + GROOVE_ROOT_W / 2),
    G.oring(2 * root_r, ORING_CS, z_end - PLUG_FLANGE_T + plug_groove[0] + GROOVE_ROOT_W / 2),
])
screws = []
for z, angles in ((z_cb - SCREW_FROM_TUBE_END, (0, 120, 240)), (z_bt + SCREW_FROM_TUBE_END, (60, 180, 300)),
                  (z_end + SCREW_FROM_TUBE_END, (0, 120, 240))):
    for a in angles:
        d = at(1, a)
        o = d * (TUBE_OD / 2) + V(0, 0, z)
        screws += [Part.makeCylinder(1.45, SCREW_L, o, -d), Part.makeCylinder(2.8, 2.0, o, d)]
rods = []
for c in rod_pts:
    rods += [Part.makeCone(HEAD_D / 2, 1.5, HEAD_H, V(c.x, c.y, z_head)), cyl(3.0, z_head, z_head + rod_len, c.x, c.y),
             G.hex_prism(NUT_AF, z_bt - NUT_POCKET, z_bt - NUT_POCKET + NUT_T, c.x, c.y)]
fitting = G.push_in_fitting(0, 0, 0)
fitting.rotate(V(0, 0, 0), Y, 90)
fitting.translate(V(SPOT_FACE_R, 0, PILOT_Z))
fitting.rotate(V(0, 0, 0), Z, PILOT_ANGLE)
ball = Part.makeSphere(TUBE_ID / 2, V(0, 0, z_tip + TUBE_ID / 2))

# ---------------------------------------------------------------- document
if not STAGE3V3_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Body", body, "rotor"), ("Cap", cap, "stator"), ("Diaphragm", diaphragm, "shoe"),
                        ("Chamber_plug", plug_a, "rotor")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_tube", barrel, "ghost"), ("Chamber_tube", chamber, "ghost"),
                        ("ORings", orings, "oring"), ("Tube_screws", G.fuse_all(screws), "steel"),
                        ("Tie_rods", G.fuse_all(rods), "steel"), ("Pilot_fitting", fitting, "steel"),
                        ("Ball", ball, "flow")):
        sc.add("Bought", n, s, style)
    half = Part.makeBox(100, 50, 1200, V(-50, -50, -800))
    half.rotate(V(0, 0, 0), Z, PASS_ANGLES[1] - 90.0)      # cut through a passage, keep the pilot port
    for n in ("Body", "Cap", "Diaphragm", "Chamber_plug", "Barrel_tube", "Chamber_tube", "ORings", "Ball",
              "Tie_rods", "Pilot_fitting"):
        style = dict(Body="rotor", Cap="stator", Diaphragm="shoe", Chamber_plug="rotor", ORings="oring",
                     Ball="flow", Tie_rods="steel", Pilot_fitting="steel").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("СТВОЛ %.0f мм" % BARREL_LEN, (-35, 0, z_bt + BARREL_LEN * 0.6)),
        ("ШАРИК на упоре", (-35, 0, z_tip + 15)),
        ("КОРПУС: седло Ø%.0f, галерея, гайки M3" % SEAT_D, (40, 0, z_bt - 5)),
        ("МЕМБРАНА %.1f мм, Ø%.1f, с отверстиями" % (DIA_T, 2 * DIA_R), (40, 0, 0)),
        ("КРЫШКА: пилот G1/8 -> M3R110 A", (40, 0, z_oc)),
        ("КАМЕРА %.0f см3: труба %.0f мм" % (CHAMBER_V, chamber_tube_len), (40, 0, (z_end + z_cb) / 2)),
        ("ЗАГЛУШКА камеры", (40, 0, z_end - 10)),
    ]:
        sc.label("Labels", text, pos)
    JIG_AT = V(-2 * BODY_R - JIG_BASE_SIDE / 2, 0, -JIG_BASE_T - DIA_T)    # beside the module, stacked as used
    sc.add("Jig", "Jig_base", jig_base, "frame", offset=JIG_AT)
    sc.add("Jig", "Jig_rubber", diaphragm_free, "shoe", offset=JIG_AT + V(0, 0, JIG_BASE_T))
    sc.add("Jig", "Jig_guide", jig_guide, "stator", offset=JIG_AT + V(0, 0, JIG_BASE_T + DIA_T))
    sc.label("Labels", "ШАБЛОН мембраны: основание со штырьками, резина, накладка", (JIG_AT.x, 0, JIG_AT.z + 30))
    sc.finish(hidden_groups=("Section",), opaque_groups=("Section",))
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name):
        s = shape.copy()
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for n, s in (("body", body), ("cap", cap), ("diaphragm", diaphragm_free), ("chamber_plug", plug_print),
                 ("jig_base", jig_base), ("jig_guide", jig_guide)):
        write(s, n)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
