# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v4.1: the chamber is a bought tube round the barrel.

v4.1 (after v4 leaked into the barrel while the pilot filled): the seat ring
was held only by the barrel, so the pilot pushed it (and the barrel) ~110 N
forward off the diaphragm until the chamber came up. Now the seat ring is
screwed to the chamber tube by four ST2.2 through lugs on its clamp ring,
drilled in place through a jig that sits on the rear plug and its screw
heads; the barrel only seals in its socket. The seat stands SEAT_PROUD
above the clamp face for a surer seal. No stop pins: a lip on the seat ring
round the diaphragm lands on the rear plug and sets the squeeze; the struts
stand clear of the diaphragm, so the bleed hole can sit at any angle. Rear plug, diaphragm, front plug and
tubes are v4's.

v1-v3 fed the barrel through a Ø11 seat, 21 % of its bore, and put the
chamber behind it (the module was ~590 mm long). Here a 38 x 1.2 tube is the
chamber; the barrel runs inside it, and the valve sits at its rear end, all
inside the tube:

    rear plug ─┬─ diaphragm ─┬─ seat ring ─── barrel (25 x 0.6) ──────> muzzle
    pilot G1/8 │  (pocket)   │  seat Ø16, socket for the barrel
       (axial) │             └── struts: chamber air from the annulus round
               │                 the barrel comes in over the seat
    chamber tube 38 x 1.2 ─────────────────────────────── front plug ┘

    pilot up: the diaphragm sits on the seat and the chamber charges from the
    pilot through a bleed hole in it. Pilot vented: chamber pressure on the
    annulus outside the seat lifts it into the pocket, and the chamber dumps
    straight into the barrel.

Parts, each exported in its print orientation (lowest point at z = 0):

    rear plug ... rear face on the bed: flange (= tube OD), spigot into the
                  chamber tube on a 30 x 3 O-ring, pilot pocket (= lift) on the
                  front face with floor grooves and a sealing bead (v4.1: no stop pins),
                  G1/8 pilot port from the bed side.
    seat ring ... seat face on the bed: clamp ring with four screw lugs
                  (0/90/180/270 deg), Ø16 seat, struts, 45 deg flare out to
                  the barrel socket (24 x 2 O-ring in it), a stop lip round
                  the diaphragm that sets the squeeze; four ST2.2 through the
                  chamber tube into the lugs hold it there.
    O-ring cone . a funnel slipped over either end of the chamber tube: the
                  30 x 3 rings close down its taper and come off it a little
                  under the tube's bore, clear of the cut edge. Grease them.
    screw jig ... collar over the tube's rear end: its lip on the rear
                  plug's back face, slots over the rear plug's screw heads,
                  a Ø1.8 drill guide at each of the seat ring's lugs.
    front plug .. sleeve end on the bed: closes the chamber round the barrel
                  (30 x 3 O-ring in the tube, 24 x 2 on the barrel) and holds
                  the barrel with screws through the sleeve.
    diaphragm ... Ø31 disc of rubber sheet with one bleed hole (v4.1: no pin holes).

Assembly: diaphragm on the rear plug's face (the bead inside it), seat ring on
top (its stop lip round the diaphragm, on the plug's face), plug into the
tube's rear end and screwed. Barrel in
from the front into the socket and pushed home: it holds the seat ring
down on the plug's face. Jig on, drill Ø1.8 through each of the four guides (tube
and lug), jig off, ST2.2 x 9.5 into each. Then the front plug, drill and screw its
sleeve to the barrel.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3v4_coaxial_chamber.py').read())
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
    STAGE3V4_LIBRARY
except NameError:
    STAGE3V4_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

OUT_DIR = os.path.join(REPO, "exports", "stage3v4_coaxial_chamber")
NAME = "stage3v4_coaxial_chamber"

# ---------------------------------------------------------------- parameters
P_WORK_BAR, P_MAX_BAR = 2.0, 5.0
CHAMBER_V = 100.0           # cm3 target

BARREL_ID, BARREL_WALL = 23.8, 0.59
BARREL_OD = BARREL_ID + 2 * BARREL_WALL
BARREL_LEN = 300.0
CH_OD, CH_WALL = 38.0, 1.2  # bought chamber tube
CH_ID = CH_OD - 2 * CH_WALL

RADIAL_CLEAR = 0.20
CH_ORING = (30.0, 3.0)      # ID x CS, in the chamber tube (rear and front plug)
BR_ORING = (24.0, 2.0)      # ID x CS, on the barrel (seat ring socket, front plug)
ORING_SQUEEZE = 0.15
GROOVE_W = 1.3              # x CS
LEAD_CHAMFER = 1.0
SCREW_PILOT_D, SCREW_DEPTH, SCREW_L = 2.5, 3.8, 4.5   # ST2.9 x 4.5 through the tubes
SCREW_FROM_TUBE_END = 6.0
SCREW_ANGLES = (0.0, 120.0, 240.0)

# Valve
SEAT_D = 16.0
SEAT_LAND = 1.5
MOUTH_R = 12.3              # free diaphragm Ø = 2 * MOUTH_R
MOUTH_CHAMFER = 1.0         # pocket edge, rear plug side
LIFT = 2.9                  # the free annulus is narrow: more stretches the rubber > 30 %
DIA_T = 1.5
DIA_SQUEEZE = 0.20          # set by the seat ring's stop lip
DIA_R = 15.5                # v4.1: inside the seat ring's stop lip (v4: 17.4, on pins)
BEAD_R = 13.2
BEAD_W = (0.9, 0.4)         # base, top
BEAD_H = 0.4
# v4.1: no stop pins. The seat ring's stop lip, outside the diaphragm, lands on the rear plug's face and sets
# the squeeze all round; it also centres the diaphragm. (On a v4 rear plug, cut the four pins off.)
STOP_LIP_R0 = DIA_R + 0.3
STRUT_RELIEF = 0.6          # struts stand this far off the clamp face over the free diaphragm: the bleed may sit anywhere
BLEED_D, BLEED_R, BLEED_ANGLE = 0.8, 10.9, 0.0
GROOVE_N, GROOVE_WIDTH, GROOVE_DEPTH = 4, 2.0, 0.6     # pocket floor

# Seat ring
RING_T = 3.0                # clamp ring height
SEAT_PROUD = 0.3            # the seat stands this far above the clamp face, into the diaphragm (v4.1)
LUG_ANGLES = (0.0, 90.0, 180.0, 270.0)   # seat ring screw lugs (v4.1): midway between the struts
LUG_W, LUG_H, LUG_R0 = 5.0, 7.0, 13.5
LUG_SCREW_Z, LUG_PILOT_D, LUG_PILOT_DEPTH = 3.5, 1.8, 5.0       # ST2.2 x 9.5, radial
JIG_LIP_T, JIG_WALL, JIG_FITTING_D = 3.0, 3.0, 20.0
# O-ring cone: a funnel over the tube's end. The 30 x 3 rings close down its smooth taper and leave it a
# little under the tube's bore, so they never touch the tube's cut edge. Off again after assembly.
CONE_LEN, CONE_SLEEVE, CONE_WALL, CONE_STEP = 25.0, 10.0, 2.0, 0.05   # step: under the bore, over the plug spigots
SEAT_TUBE_H = 6.0           # straight seat tube before the 45 deg flare
STRUT_N, STRUT_W, STRUT_H = 4, 2.5, 11.5
SOCKET_WALL = 1.2           # outside the barrel O-ring groove
SOCKET_LEN = 15.0
SHOULDER_WALL = 1.5

# Rear plug
RP_SPIGOT = 24.0            # inside the chamber tube
RP_GROOVE_WALL = 15.0       # groove's rear (square) wall behind the front face
RP_FLANGE_T = 4.0
G18_TAP_D, G18_TAP_DEPTH = 8.8, 8.0
PILOT_D = 4.0

# Front plug
FP_SPIGOT = 20.0
FP_GROOVE_WALL = 8.0        # groove's front (square) wall ahead of the spigot tip
FP_FLANGE_T = 2.0
FP_SLEEVE = 12.0
BARREL_SCREW_FROM_END = 6.0
BARREL_SCREW_HOLE = 3.2

PACK_PITCH = 40.0

# Drilling template: a disc of the diaphragm's own Ø with a guide for each
# hole. Rubber on a scrap board, template on top, drill, cut round it.
JIG_GUIDE_CLEAR = 0.15
JIG_GUIDE_T = 3.0

# ---------------------------------------------------------------- derived
X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector
t_c = DIA_T * (1 - DIA_SQUEEZE)             # diaphragm z in [-t_c, 0], seat face at z = 0
spigot_r = CH_ID / 2 - RADIAL_CLEAR
ch_root_r = CH_ID / 2 - CH_ORING[1] * (1 - ORING_SQUEEZE)
ch_stretch = 2 * ch_root_r / CH_ORING[0] - 1
sock_r = BARREL_OD / 2 + RADIAL_CLEAR
br_root_r = BARREL_OD / 2 + BR_ORING[1] * (1 - ORING_SQUEEZE)   # housing groove: outer root
br_stretch = BARREL_OD / BR_ORING[0] - 1
sock_out_r = br_root_r + SOCKET_WALL
seat_r = SEAT_D / 2
seat_out_r = seat_r + SEAT_LAND
ring_out_r = CH_ID / 2 - 0.5
z_flare = SEAT_TUBE_H
z_flare_end = z_flare + (sock_out_r - seat_out_r)
z_sh = z_flare + (sock_r + SHOULDER_WALL - seat_out_r)    # barrel stop: shoulder in the seat ring
z_sock = z_sh + SOCKET_LEN
z_f = -t_c                                   # rear plug front face
z_te = z_f - RP_SPIGOT                       # chamber tube rear end
z_rp = z_te - RP_FLANGE_T                    # rear plug back face
z_floor = z_f - LIFT


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


def shaft_groove(z_sq, toward):
    """Outer O-ring groove in a spigot inside the chamber tube: square wall at
    z_sq, 45 deg wall on the `toward` side (+1 / -1), which prints as a ceiling."""
    w = GROOVE_W * CH_ORING[1]
    z1 = z_sq + toward * w
    z2 = z1 + toward * (spigot_r - ch_root_r)
    return revolve([(ch_root_r, z_sq), (spigot_r + 1, z_sq), (spigot_r + 1, z2 + toward * 1), (ch_root_r, z1)]), \
        (min(z_sq, z2), max(z_sq, z2))


def bore_groove(z_sq, toward):
    """Inner O-ring groove round the barrel: square wall at z_sq, 45 deg wall
    on the `toward` side."""
    w = GROOVE_W * BR_ORING[1]
    z1 = z_sq + toward * w
    z2 = z1 + toward * (br_root_r - sock_r)
    return revolve([(sock_r - 1, z_sq), (br_root_r, z_sq), (br_root_r, z1), (sock_r - 1, z2 + toward * 1)]), \
        (min(z_sq, z2), max(z_sq, z2))


def screw_pilots(z, angles, r_out=None):
    r_out = spigot_r if r_out is None else r_out
    out = []
    for a in angles:
        d = at(1, a)
        out.append(Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_DEPTH + 1, d * (r_out + 1) + V(0, 0, z), -d))
    return out


# ---------------------------------------------------------------- rear plug
rp = cyl(CH_OD, z_rp, z_te).fuse(revolve([(0, z_te - 0.5), (spigot_r, z_te - 0.5), (spigot_r, z_f - 0.5),
                                          (spigot_r - 0.5, z_f), (0, z_f)]))
rp = rp.fuse(revolve([(BEAD_R - BEAD_W[0] / 2, z_f - 0.01), (BEAD_R + BEAD_W[0] / 2, z_f - 0.01),
                      (BEAD_R + BEAD_W[1] / 2, z_f + BEAD_H), (BEAD_R - BEAD_W[1] / 2, z_f + BEAD_H)]))
rp_groove, rp_groove_z = shaft_groove(z_f - RP_GROOVE_WALL, +1)     # chamber in front: rear wall square
pilot_cuts = [revolve([(0, z_floor), (MOUTH_R - MOUTH_CHAMFER, z_floor), (MOUTH_R - MOUTH_CHAMFER, z_f - MOUTH_CHAMFER),
                       (MOUTH_R, z_f), (MOUTH_R, z_f + 1), (0, z_f + 1)]),
              cyl(PILOT_D, z_rp + G18_TAP_DEPTH, z_floor + 0.01),
              cyl(G18_TAP_D, z_rp - 1, z_rp + G18_TAP_DEPTH),
              Part.makeCone(G18_TAP_D / 2, PILOT_D / 2, (G18_TAP_D - PILOT_D) / 2, V(0, 0, z_rp + G18_TAP_DEPTH))]
for i in range(GROOVE_N):
    g = Part.makeBox(MOUTH_R - 2, GROOVE_WIDTH, GROOVE_DEPTH + 0.5, V(0, -GROOVE_WIDTH / 2, z_floor - GROOVE_DEPTH))
    g.rotate(V(0, 0, 0), Z, 360.0 / GROOVE_N * i + 45)
    pilot_cuts.append(g)
rp = rp.cut(G.fuse_all([rp_groove] + pilot_cuts + screw_pilots(z_te + SCREW_FROM_TUBE_END, SCREW_ANGLES)))
rp = rp.removeSplitter()

# ---------------------------------------------------------------- seat ring
sr = revolve([(MOUTH_R, 0), (ring_out_r, 0), (ring_out_r, RING_T), (MOUTH_R, RING_T)])
sr = sr.fuse(revolve([(seat_r, -SEAT_PROUD), (seat_out_r, -SEAT_PROUD), (seat_out_r, z_flare), (sock_out_r, z_flare_end),
                      (sock_out_r, z_sock), (seat_r, z_sock)]))
for a in LUG_ANGLES:                                                 # screw lugs on the clamp ring
    lug = Part.makeBox(ring_out_r - LUG_R0, LUG_W, LUG_H, V(LUG_R0, -LUG_W / 2, 0))
    lug = lug.common(cyl(2 * ring_out_r, 0, LUG_H))
    lug.rotate(V(0, 0, 0), Z, a)
    sr = sr.fuse(lug)
for i in range(STRUT_N):
    s = Part.makeBox(ring_out_r - seat_out_r + 0.5, STRUT_W, STRUT_H, V(seat_out_r - 0.5, -STRUT_W / 2, 0))
    s = s.cut(Part.makeBox(MOUTH_R - seat_out_r, STRUT_W + 2, STRUT_RELIEF, V(seat_out_r, -STRUT_W / 2 - 1, -0.01)))
    s.rotate(V(0, 0, 0), Z, 360.0 / STRUT_N * (i + 0.5))
    sr = sr.fuse(s)
sr = sr.fuse(revolve([(STOP_LIP_R0, -t_c), (ring_out_r, -t_c), (ring_out_r, 0.01), (STOP_LIP_R0, 0.01)]))   # stop lip
sr_groove, sr_groove_z = bore_groove(z_sh + 3.0, +1)                # barrel side behind: rear wall square
sr_cuts = [revolve([(0, -1), (seat_r, -1), (seat_r, z_sh), (sock_r, z_sh),
                    (sock_r, z_sock - LEAD_CHAMFER), (sock_r + LEAD_CHAMFER, z_sock + 0.01),
                    (sock_r + LEAD_CHAMFER, z_sock + 1), (0, z_sock + 1)]),
           sr_groove]
sr = sr.cut(G.fuse_all(sr_cuts)).removeSplitter()
# Screw jig (v4.1): over the tube's rear end, lip on the rear plug's back face
jig_r_in = CH_OD / 2 + 0.15
z_jig0 = z_rp - JIG_LIP_T
jig = cyl(CH_OD + 2 * (0.15 + JIG_WALL), z_jig0, LUG_SCREW_Z + 8).cut(cyl(2 * jig_r_in, z_rp, LUG_SCREW_Z + 9))
jig = jig.cut(cyl(JIG_FITTING_D, z_jig0 - 1, z_rp + 1))
for a in SCREW_ANGLES:                                               # slots over the rear plug's screw heads: index it
    sl = Part.makeBox(CH_OD, 6.0, (z_te + SCREW_FROM_TUBE_END + 4) - z_rp + 1, V(0, -3.0, z_rp - 0.5))
    sl.rotate(V(0, 0, 0), Z, a)
    jig = jig.cut(sl)
lug_holes = []
for a in LUG_ANGLES:
    d = at(1, a)
    lug_holes.append(Part.makeCylinder(LUG_PILOT_D / 2, CH_OD / 2 + JIG_WALL + 2 - (ring_out_r - LUG_PILOT_DEPTH),
                                       d * (ring_out_r - LUG_PILOT_DEPTH) + V(0, 0, LUG_SCREW_Z), d))
jig = jig.cut(G.fuse_all(lug_holes)).removeSplitter()
# O-ring cone: sleeve over the tube's end, its face on the tube's end, taper in front (printed taper up)
_o_free = 2 * ch_root_r + 2 * CH_ORING[1]           # the ring's OD as it sits in its groove, unsqueezed
_cone_in = max(_o_free + 1.0, CH_OD)                # mouth: the ring goes in free
_cone_out = CH_ID - 2 * CONE_STEP                   # exit: a little under the tube's bore
oring_cone = revolve([(_cone_out / 2, 0), (CH_OD / 2 + 0.15, 0), (CH_OD / 2 + 0.15, -CONE_SLEEVE),
                      (CH_OD / 2 + 0.15 + CONE_WALL, -CONE_SLEEVE), (CH_OD / 2 + 0.15 + CONE_WALL, CONE_LEN),
                      (_cone_in / 2, CONE_LEN)])

# ---------------------------------------------------------------- diaphragm (clamped, in place)
dcuts = [cyl(BLEED_D, -t_c - 1, 1, *at(BLEED_R, BLEED_ANGLE)[:2])]
diaphragm = cyl(2 * DIA_R, -t_c, 0).cut(G.fuse_all(dcuts))
diaphragm_free = cyl(2 * DIA_R, 0, DIA_T).cut(G.fuse_all(dcuts))
jig_holes = [(BLEED_R, BLEED_ANGLE, BLEED_D)]
jig_guide = cyl(2 * DIA_R, 0, JIG_GUIDE_T).cut(
    G.fuse_all([cyl(d + JIG_GUIDE_CLEAR, -1, JIG_GUIDE_T + 1, *at(r, a)[:2]) for r, a, d in jig_holes])).removeSplitter()

# ---------------------------------------------------------------- chamber length, front plug
area = lambda d: math.pi * d * d / 4
A_annulus = area(CH_ID) - area(BARREL_OD)
probe_end = z_sock + 20.0
probe = cyl(CH_ID, 0, probe_end).cut(sr).cut(cyl(SEAT_D, -1, z_sh)).cut(cyl(2 * sock_r, z_sh, probe_end + 1))
v_probe = probe.Volume                        # air from the seat face to probe_end
z_fp_tip = probe_end + (CHAMBER_V * 1000 - v_probe) / A_annulus        # front plug spigot tip
z_tf = z_fp_tip + FP_SPIGOT                  # chamber tube front end
chamber_len = z_tf - z_te
z_fs = z_tf + FP_FLANGE_T                    # flange front -> 45 deg -> sleeve
z_fp_end = z_fs + (CH_OD / 2 - sock_out_r) + FP_SLEEVE

fp = revolve([(sock_r, z_fp_tip), (spigot_r - LEAD_CHAMFER, z_fp_tip), (spigot_r, z_fp_tip + LEAD_CHAMFER),
              (spigot_r, z_tf), (CH_OD / 2, z_tf), (CH_OD / 2, z_fs), (sock_out_r, z_fs + (CH_OD / 2 - sock_out_r)),
              (sock_out_r, z_fp_end), (sock_r, z_fp_end)])
fp_groove, fp_groove_z = shaft_groove(z_fp_tip + FP_GROOVE_WALL, -1)  # chamber behind: front wall square
fp_bgroove, fp_bgroove_z = bore_groove(z_fp_tip + FP_GROOVE_WALL, -1)
fp_cuts = [fp_groove, fp_bgroove] + screw_pilots(z_tf - SCREW_FROM_TUBE_END, SCREW_ANGLES)
z_bs = z_fp_end - BARREL_SCREW_FROM_END
for a in (60.0, 180.0, 300.0):
    d = at(1, a)
    fp_cuts.append(Part.makeCylinder(BARREL_SCREW_HOLE / 2, sock_out_r - sock_r + 2, d * (sock_r - 0.5) + V(0, 0, z_bs), d))
fp = fp.cut(G.fuse_all(fp_cuts)).removeSplitter()

# ---------------------------------------------------------------- tubes
tube = lambda od, idd, z0, z1: cyl(od, z0, z1).cut(cyl(idd, z0 - 1, z1 + 1))
barrel = tube(BARREL_OD, BARREL_ID, z_sh, z_sh + BARREL_LEN)
chamber = tube(CH_OD, CH_ID, z_te, z_tf)
chamber_air = (cyl(CH_ID, 0, z_fp_tip).cut(sr).cut(cyl(SEAT_D, -1, z_sh)).cut(cyl(BARREL_OD, z_sh, z_fp_tip + 1)))
chamber_v = chamber_air.Volume / 1000

# ---------------------------------------------------------------- numbers
A_bore = area(BARREL_ID)
A_seat = area(SEAT_D)
A_seat_eff = area(SEAT_D + SEAT_LAND)
A_dia = area(2 * MOUTH_R)
A_curtain = math.pi * SEAT_D * LIFT
A_sock_annulus = area(CH_ID) - area(2 * sock_out_r)
z_entry_top = z_flare + (MOUTH_R - seat_out_r)              # flare height at the gallery's outer radius
A_entry = 2 * math.pi * MOUTH_R * (z_entry_top - RING_T) - STRUT_N * STRUT_W * (z_entry_top - RING_T)
z_lug_top = z_flare + (LUG_R0 - seat_out_r)                  # flare height over the lugs' inner edge (v4.1)
A_entry_lugs = (2 * math.pi * LUG_R0 - STRUT_N * STRUT_W - len(LUG_ANGLES) * LUG_W) * (z_lug_top - RING_T) \
    + len(LUG_ANGLES) * LUG_W * (z_lug_top - LUG_H)          # and past the lugs, further out
open_ratio = 1 - A_seat_eff / A_dia
annulus_w = MOUTH_R - (seat_r + SEAT_LAND / 2)
dia_strain = math.hypot(annulus_w, LIFT) / annulus_w - 1
pocket_v = (A_dia * LIFT + area(PILOT_D) * (z_floor - z_rp - G18_TAP_DEPTH)) / 1000
dead_v = A_seat * z_sh / 1000
F_rp = P_MAX_BAR * 0.1 * area(CH_ID)
F_open = P_WORK_BAR * 0.1 * A_dia                            # pilot up, chamber empty: on the seat ring / barrel

checks = [
    ("rear plug, seat ring, front plug valid single solids", all(G.single_solid(s) for s in (rp, sr, fp))),
    ("rear plug / diaphragm / seat ring clear (bead and the proud seat aside)",
     G.no_overlap(sr.cut(cyl(2 * seat_out_r + 0.2, -1, 0)), diaphragm) and G.no_overlap(sr, rp) and
     G.no_overlap(rp.cut(cyl(CH_ID + 2, z_f, 1)), diaphragm)),
    ("stop lip lands on the rear plug's face (squeeze %.0f %%)" % (DIA_SQUEEZE * 100),
     abs(sr.BoundBox.ZMin - z_f) < 1e-6 and G.no_overlap(sr, rp.cut(cyl(2 * BEAD_R + 2, z_f, 1)))),
    ("seat %.0f %% of the barrel bore" % (A_seat / A_bore * 100), A_seat >= 0.4 * A_bore),
    ("seat curtain >= 0.7 x seat (lift %.1f: %.0f mm2)" % (LIFT, A_curtain), A_curtain >= 0.7 * A_seat),
    ("chamber annulus round the socket >= 1.2 x seat (%.0f mm2)" % A_sock_annulus, A_sock_annulus >= 1.2 * A_seat),
    ("gallery entry over the clamp ring >= 1.5 x seat (%.0f mm2)" % A_entry, A_entry >= 1.5 * A_seat),
    ("opens after the pilot loses <= 55 %% (%.0f %%)" % (open_ratio * 100), open_ratio >= 0.45),
    ("diaphragm stretch at full lift <= 30 %% (%.0f %%)" % (dia_strain * 100), dia_strain <= 0.30),
    ("bead inside the clamp ring, >= 0.3 mm from the mouth, 1 mm in from the edge",
     BEAD_R - BEAD_W[0] / 2 >= MOUTH_R + 0.3 and BEAD_R + BEAD_W[0] / 2 <= DIA_R - 1.0),
    ("squeeze under the bead 30..50 %", 0.30 <= (DIA_T - t_c + BEAD_H) / DIA_T <= 0.50),
    ("stop lip outside the diaphragm, >= 1 mm wide", STOP_LIP_R0 > DIA_R and ring_out_r - STOP_LIP_R0 >= 1.0),
    ("struts clear of the free diaphragm (bleed hole at any angle)", STRUT_RELIEF >= DIA_T - t_c + 0.2),
    ("bleed hole over the gallery, clear of seat and mouth", seat_out_r + 1.0 <= BLEED_R <= MOUTH_R - 1.0),
    ("seat ring clear of the chamber tube", ring_out_r <= CH_ID / 2 - 0.3 and sock_out_r <= CH_ID / 2 - 1.0),
    ("socket wall >= 1.2 mm, shoulder wall >= 1.5 mm", SOCKET_WALL >= 1.2 and SHOULDER_WALL >= 1.5),
    ("socket groove ahead of the shoulder", sr_groove_z[0] >= z_sh + 2.0),
    ("pilot pocket floor grooves above the G1/8 tap", z_floor - GROOVE_DEPTH - (z_rp + G18_TAP_DEPTH + 2.4) >= 2.0),
    ("rear plug groove behind the pocket, screws behind the groove",
     rp_groove_z[1] <= z_floor - 2.0 and z_te + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 <= rp_groove_z[0] - 1.0),
    ("front plug screws ahead of its groove",
     z_tf - SCREW_FROM_TUBE_END - SCREW_PILOT_D / 2 >= max(fp_groove_z[1], fp_bgroove_z[1]) + 1.0),
    ("barrel screws in the sleeve, ahead of the barrel groove", z_bs - BARREL_SCREW_HOLE / 2 >= z_fs + 1.0),
    ("chamber O-ring stretch 0..6 %% (%.1f %%)" % (ch_stretch * 100), 0 <= ch_stretch <= 0.06),
    ("barrel O-ring stretch 0..6 %% (%.1f %%)" % (br_stretch * 100), 0 <= br_stretch <= 0.06),
    ("chamber %.0f cm3 within 3 %% of target" % chamber_v, abs(chamber_v - CHAMBER_V) <= 0.03 * CHAMBER_V),
    ("barrel longer than the chamber", z_sh + BARREL_LEN >= z_fp_end + 20),
    ("nothing wider than the chamber tube", max(rp.BoundBox.XMax, fp.BoundBox.XMax) <= CH_OD / 2 + 1e-6),
    ("drilling template valid single solid", G.single_solid(jig_guide)),
    ("screw jig valid single solid", G.single_solid(jig)),
    ("O-ring cone: mouth over the free ring (Ø%.1f > %.1f), exit under the bore (Ø%.1f < %.1f), taper <= 10 deg"
     % (_cone_in, _o_free, _cone_out, CH_ID),
     G.single_solid(oring_cone) and _cone_in > _o_free and 2 * spigot_r + 0.2 <= _cone_out < CH_ID
     and math.degrees(math.atan2((_cone_in - _cone_out) / 2, CONE_LEN)) <= 10.0),
    ("lugs clear of the struts and the bleed hole",
     all(min(abs(((a - 360.0 / STRUT_N * (i + 0.5)) + 180) % 360 - 180) for i in range(STRUT_N)) * math.pi / 180 * LUG_R0
         >= LUG_W / 2 + STRUT_W / 2 for a in LUG_ANGLES)),
    ("gallery past the lugs >= 1.5 x seat (%.0f mm2)" % A_entry_lugs, A_entry_lugs >= 1.5 * A_seat),
    ("lug screws well ahead of the rear plug's (%.0f mm)" % (LUG_SCREW_Z - z_te - SCREW_FROM_TUBE_END),
     LUG_SCREW_Z - (z_te + SCREW_FROM_TUBE_END) >= 15.0),
    ("lug screw plane under the flare", LUG_SCREW_Z + LUG_PILOT_D / 2 + 1.0 <= LUG_H <= z_flare + (LUG_R0 - seat_out_r)),
    ("seat proud of the clamp face, < half the diaphragm", 0 < SEAT_PROUD < DIA_T / 2),
]

report = [
    NAME,
    "  flow path              : seat Ø%.0f (%.0f mm2 = %.0f %% of the Ø%.1f bore), curtain %.0f at lift %.1f,"
    " annulus round the socket %.0f, gallery entry %.0f"
    % (SEAT_D, A_seat, A_seat / A_bore * 100, BARREL_ID, A_curtain, LIFT, A_sock_annulus, A_entry),
    "  diaphragm              : Ø%.1f x %.1f, free Ø%.1f, squeeze %.0f %% (stop lip), %.0f %% under the bead,"
    " stretch %.0f %% at full lift"
    % (2 * DIA_R, DIA_T, 2 * MOUTH_R, DIA_SQUEEZE * 100, (DIA_T - t_c + BEAD_H) / DIA_T * 100, dia_strain * 100),
    "  diaphragm              : a plain disc, one bleed Ø%.1f at R%.1f (any angle); the stop lip centres it"
    % (BLEED_D, BLEED_R),
    "  opens when pilot < %.0f %% of chamber pressure (gauge)" % (open_ratio * 100),
    "  pilot volume           : %.1f cm3, G1/8 axial in the rear plug" % pocket_v,
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  chamber                : %.0f cm3, tube %.0f x %.1f, %.0f mm long" % (chamber_v, CH_OD, CH_WALL, chamber_len),
    "  module                 : Ø%.0f, %.0f mm long with a %.0f mm barrel; pack pitch %.0f"
    % (CH_OD, z_sh + BARREL_LEN - z_rp, BARREL_LEN, PACK_PITCH),
    "  @ %.0f bar               : rear plug %.0f N back (3 screws); pilot pushes the seat ring %.0f N forward at %.0f bar,"
    " now on its ST2.2 in the tube, not the barrel" % (P_MAX_BAR, F_rp, F_open, P_WORK_BAR),
    "  seat ring screws       : %d x ST2.2 x 9.5 at %s deg, %.1f mm ahead of the seat face (%.1f mm from the tube's rear end);"
    " drill Ø%.1f through the jig" % (len(LUG_ANGLES), "/".join("%.0f" % a for a in LUG_ANGLES), LUG_SCREW_Z, LUG_SCREW_Z - z_te, LUG_PILOT_D),
    "  O-rings                : 2 x %g x %g (chamber tube), 2 x %g x %g (barrel)" % (CH_ORING + BR_ORING),
    "  rear plug / seat ring / front plug: %.1f / %.1f / %.1f cm3" % (rp.Volume / 1000, sr.Volume / 1000, fp.Volume / 1000),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
if not STAGE3V4_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- references
torus = lambda rc, cs, z: Part.makeTorus(rc, cs / 2, V(0, 0, z), Z)
orings = G.fuse_all([
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], rp_groove_z[0] + GROOVE_W * CH_ORING[1] / 2),
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], fp_groove_z[1] - GROOVE_W * CH_ORING[1] / 2),
    torus(br_root_r - BR_ORING[1] / 2, BR_ORING[1], sr_groove_z[0] + GROOVE_W * BR_ORING[1] / 2),
    torus(br_root_r - BR_ORING[1] / 2, BR_ORING[1], fp_bgroove_z[1] - GROOVE_W * BR_ORING[1] / 2),
])
fitting = G.push_in_fitting(0, 0, 0)
fitting.rotate(V(0, 0, 0), X, 180)
fitting.translate(V(0, 0, z_rp))
ball = Part.makeSphere(BARREL_ID / 2, V(0, 0, z_sh + math.sqrt((BARREL_ID / 2) ** 2 - seat_r ** 2) - 0.0))

# ---------------------------------------------------------------- document
if not STAGE3V4_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Rear_plug", rp, "stator"), ("Seat_ring", sr, "rotor"), ("Diaphragm", diaphragm, "shoe"),
                        ("Front_plug", fp, "stator")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_tube", barrel, "ghost"), ("Chamber_tube", chamber, "ghost"),
                        ("ORings", orings, "oring"), ("Pilot_fitting", fitting, "steel"), ("Ball", ball, "flow")):
        sc.add("Bought", n, s, style)
    half = Part.makeBox(100, 50, 1200, V(-50, -50, -600))
    for n in ("Rear_plug", "Seat_ring", "Diaphragm", "Front_plug", "Barrel_tube", "Chamber_tube", "ORings", "Ball",
              "Pilot_fitting"):
        style = dict(Rear_plug="stator", Seat_ring="rotor", Diaphragm="shoe", Front_plug="stator", ORings="oring",
                     Ball="flow", Pilot_fitting="steel").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("СТВОЛ 25x0,6, %.0f мм" % BARREL_LEN, (-40, 0, z_sh + BARREL_LEN * 0.8)),
        ("КАМЕРА: труба %.0fx%.1f, %.0f мм, %.0f см3" % (CH_OD, CH_WALL, chamber_len, chamber_v), (40, 0, z_tf * 0.5)),
        ("ПЕРЕДНЯЯ ПРОБКА", (40, 0, z_tf + 5)),
        ("КОЛЬЦО СЕДЛА: седло Ø%.0f" % SEAT_D, (40, 0, 10)),
        ("МЕМБРАНА Ø%.1f" % (2 * DIA_R), (40, 0, 0)),
        ("ЗАДНЯЯ ПРОБКА: пилот G1/8 -> M3R110 A", (40, 0, z_rp)),
    ]:
        sc.label("Labels", text, pos)
    sc.add("Jig", "Jig_guide", jig_guide, "stator", offset=V(-3 * CH_OD, 0, z_rp))
    sc.add("Jig", "Screw_jig", jig, "ghost")
    sc.label("Labels", "ШАБЛОН для сверления мембраны", (-3 * CH_OD, 0, z_rp + 15))
    sc.finish(hidden_groups=("Section",), opaque_groups=("Section",))
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for n, s, flip in (("rear_plug", rp, False), ("seat_ring", sr, False), ("front_plug", fp, True),
                       ("diaphragm", diaphragm_free, False), ("jig_guide", jig_guide, False), ("screw_jig", jig, False),
                       ("oring_cone", oring_cone, True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
