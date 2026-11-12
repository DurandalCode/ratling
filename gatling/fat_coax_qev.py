# -*- coding: utf-8 -*-
"""
Gatling fat-coaxial QEV: thick short chamber + stub into the real barrel.

Standalone generator in gatling/ (does not exec module/stage3v4). Same coaxial
dump physics as v4.4 (seat Ø16, diaphragm, rear plug, chamber seals), but the
module has no long barrel and no muzzle clamp: a short stub through the chamber
bottoms in the front cover, which turns into a flat stop and a self-centering
fitting into the real projectile tube (25 x 0.6).

    CH_OD x CH_WALL = 50 x 1.5 aluminium (nominal ID 47 until measured)
    CHAMBER_V       = 100 cm3
    TIE_R           = 29, PACK_PITCH = 68 (six around)
    Force path      : seat ring -> stub -> lip in front cover -> yoke -> rods

Run inside FreeCAD / freecadcmd:
    REPO = '/path/to/ratling'
    exec(open(REPO + '/gatling/fat_coax_qev.py').read())

Exports: exports/gatling_fat_coax_qev/
Library: set GATLING_FAT_COAX_LIBRARY = True before exec.
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
    GATLING_FAT_COAX_LIBRARY
except NameError:
    GATLING_FAT_COAX_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

OUT_DIR = os.path.join(REPO, "exports", "gatling_fat_coax_qev")
NAME = "gatling_fat_coax_qev"

# ---------------------------------------------------------------- parameters
P_WORK_BAR, P_MAX_BAR = 2.0, 5.0
CHAMBER_V = 100.0           # cm3 target

BARREL_ID, BARREL_WALL = 23.8, 0.59
BARREL_OD = BARREL_ID + 2 * BARREL_WALL
BARREL_LEN = 116.0  # stub through chamber; rebuilt exactly below
CH_OD, CH_WALL = 50.0, 1.5  # gatling fat coax aluminium (nominal until measured)
CH_ID = CH_OD - 2 * CH_WALL  # 47.0 nominal; measure and override like v4.4 when a tube arrives

RADIAL_CLEAR = 0.20
CH_CLEAR = 0.10             # plugs' spigots in the chamber tube, per side: Ø34.4 in the Ø34.6 bore
CH_ORING = (42.0, 3.0)      # ID x CS @ ~18 % squeeze in ID 47
BR_ORING = (24.0, 2.5)      # ID x CS, on the barrel (front plug; v4.4: no longer in the seat ring's socket)
SP_ORING = (20.0, 2.0)      # ID x CS, v4.4: on the seat ring's spigot, inside the barrel's bore
ORING_SQUEEZE = 0.18        # chamber O-rings; 18 % at Ø34.6 (was 15 % at Ø35: in the Ø34.6 tube ~22 %, very tight)
BR_SQUEEZE = 0.12           # v4.1: the barrel's 24 x 2 a little easier, it was cut by the barrel's edge going in
GROOVE_W = 1.3              # x CS
LEAD_CHAMFER = 1.0
# v4.3: two M3 threaded rods outside the tube hold the stack (no glue, nothing drilled through the tube).
TIE_D, TIE_HOLE, TIE_STRESS_A = 3.0, 3.4, 5.03     # M3: stress area mm2
TIE_R, TIE_ANGLES = 29.0, (30.0, 210.0)            # clears Ø50; each alone in a hex pack gap
EAR_R = 4.0                 # ear round the rod
EAR_ROOT_R = 14.0           # ears are the hull of this circle round the axis and the ear circle
WASHER_D, WASHER_T, NUT_AF, NUT_T = 7.0, 0.5, 5.5, 2.4
YOKE_T = 8.0                # front yoke, and the rear plug's ears behind its flange (v4.4 rear)
YOKE_CLEAR = 0.2
# Real barrel the module plugs into (bought 25 x 0.6); shown ahead of the stop.
REAL_BARREL_SHOW = 200.0
# Plain self-centering nose into that bore. No O-ring: the real barrel only locates.
FIT_RADIAL_CLEAR = 0.25
FIT_INSERT = 30.0
FIT_LEAD_LEN = 8.0
FIT_LEAD_UNDER = 1.2
FIT_FLANGE_T = 4.0
FIT_FLANGE_OVER_BARREL = 3.0
FIT_FLANGE_OVER_SLEEVE = 2.5
FIT_BORE = 18.0
STUB_LIP_T = 3.0
STUB_PAST_SLEEVE = 1.0
BED_H = 256.0
PACK_CLEAR = 0.5            # footprint to neighbours' footprints in a hex / square pack at PACK_PITCH

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
BLEED_D, BLEED_R, BLEED_ANGLE = 1.0, 10.9, 0.0     # was 0.8: as v1.1's, ~0.5 s to charge on the bench
GROOVE_N, GROOVE_WIDTH, GROOVE_DEPTH = 4, 2.0, 0.6     # pocket floor

# Seat ring
RING_T = 3.0                # clamp ring height
SEAT_PROUD = 0.3            # the seat stands this far above the clamp face, into the diaphragm (v4.1)
# O-ring cone: a funnel over the tube's end. The 30 x 3 rings close down its smooth taper and leave it a
# little under the tube's bore, so they never touch the tube's cut edge. Off again after assembly.
CONE_LEN, CONE_SLEEVE, CONE_WALL, CONE_STEP = 25.0, 10.0, 2.0, 0.05   # step: under the bore, over the plugs' spigots
SEAT_TUBE_H = 6.0           # straight seat tube before the 45 deg flare
STRUT_N, STRUT_W, STRUT_H = 4, 2.5, 11.5
SOCKET_WALL = 1.2           # v4.4: a plain locating sleeve round the barrel
SOCKET_LEN = 20.0
SHOULDER_WALL = 1.5
# v4.4: spigot into the barrel's bore, from the shoulder: land, 45 deg (prints as a floor), root, square wall
# on the bore side (the low-pressure side: chamber air comes round the barrel's end), land, lead-in.
SP_BORE = 18.0              # through the spigot (seat Ø16)
SP_LAND0, SP_LAND1 = 1.0, 2.5

# Rear plug
RP_SPIGOT = 24.0            # inside the chamber tube
RP_GROOVE_WALL = 15.0       # groove's rear (square) wall behind the front face
RP_FLANGE_T = 4.0
G18_TAP_D, G18_TAP_DEPTH = 8.8, 8.0
PILOT_D = 4.0

# Front plug
FP_SPIGOT = 20.0
FP_GROOVE_WALL = 8.0        # barrel groove's front (square) wall ahead of the spigot tip
FP_CH_GROOVE_WALL = 16.0    # v4.4: the chamber groove ahead of it (side by side the 29 x 3 left a 0.3 mm wall between)
FP_FLANGE_T = 2.0
FP_SLEEVE = 12.0

PACK_PITCH = 68.0            # six around

# Drilling template: a disc of the diaphragm's own Ø with a guide for each
# hole. Rubber on a scrap board, template on top, drill, cut round it.
JIG_GUIDE_CLEAR = 0.15
JIG_GUIDE_T = 3.0

# Optional: set OVERRIDE = {...} before exec to replace any parameter above.
try:
    globals().update(OVERRIDE)
except NameError:
    pass

# ---------------------------------------------------------------- derived
X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector
t_c = DIA_T * (1 - DIA_SQUEEZE)             # diaphragm z in [-t_c, 0], seat face at z = 0
spigot_r = CH_ID / 2 - CH_CLEAR
ch_root_r = CH_ID / 2 - CH_ORING[1] * (1 - ORING_SQUEEZE)
ch_stretch = 2 * ch_root_r / CH_ORING[0] - 1
sock_r = BARREL_OD / 2 + RADIAL_CLEAR
br_root_r = BARREL_OD / 2 + BR_ORING[1] * (1 - BR_SQUEEZE)      # housing groove: outer root
br_stretch = BARREL_OD / BR_ORING[0] - 1
sock_out_r = sock_r + SOCKET_WALL
fp_out_r = br_root_r + SOCKET_WALL                       # front plug's sleeve, round its barrel O-ring
sp_r = BARREL_ID / 2 - RADIAL_CLEAR                     # spigot in the barrel's bore
sp_root_r = BARREL_ID / 2 - SP_ORING[1] * (1 - ORING_SQUEEZE)
sp_stretch = 2 * sp_root_r / SP_ORING[0] - 1
seat_r = SEAT_D / 2
seat_out_r = seat_r + SEAT_LAND
ring_out_r = CH_ID / 2 - 0.3              # Ø34.0, as printed before the bore was measured: it fits
z_flare = SEAT_TUBE_H
z_flare_end = z_flare + (sock_out_r - seat_out_r)
z_sh = z_flare + (sock_r + SHOULDER_WALL - seat_out_r)    # barrel stop: shoulder in the seat ring
z_sock = z_sh + SOCKET_LEN
z_spg0 = z_sh + SP_LAND0                                 # spigot groove: 45 deg from the OD down to the root
z_spg1 = z_spg0 + (sp_r - sp_root_r)
z_spg2 = z_spg1 + GROOVE_W * SP_ORING[1]                 # square wall
z_sp = z_spg2 + SP_LAND1 + LEAD_CHAMFER                  # spigot tip
z_f = -t_c                                   # rear plug front face
z_te = z_f - RP_SPIGOT                       # chamber tube rear end
z_rp = z_te - RP_FLANGE_T                    # rear plug's flange back face: the ears' front face, the pack plate's
z_ry = z_rp - YOKE_T                         # rear plug's back face, behind the ears (the rear yoke until v4.4 rear)
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


def hull_prism(circles, z0, z1, n=72):
    """Prism z0..z1 over the convex hull of circles (x, y, r)."""
    pts = sorted({(round(x + r * math.cos(2 * math.pi * k / n), 6), round(y + r * math.sin(2 * math.pi * k / n), 6))
                  for x, y, r in circles for k in range(n)})
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for seq, h in ((pts, lo), (pts[::-1], hi)):
        for p in seq:
            while len(h) >= 2 and cross(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
    ring = lo[:-1] + hi[:-1]
    return Part.Face(Part.makePolygon([V(x, y, z0) for x, y in ring + ring[:1]])).extrude(V(0, 0, z1 - z0))


def ears(z0, z1):
    """The two rod ears: each the hull of a circle round the axis and the ear round its rod."""
    return [hull_prism([(0, 0, EAR_ROOT_R), (*at(TIE_R, a)[:2], EAR_R)], z0, z1) for a in TIE_ANGLES]


def tie_plate(core_r, z0, z1):
    """A disc with the two rod ears and their holes."""
    plate = G.fuse_all([cyl(2 * core_r, z0, z1)] + ears(z0, z1))
    return plate.cut(G.fuse_all([cyl(TIE_HOLE, z0 - 1, z1 + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]))


# ---------------------------------------------------------------- rear plug
rp = G.fuse_all([cyl(CH_OD, z_ry, z_te)] + ears(z_ry, z_rp)).fuse(revolve([(0, z_te - 0.5), (spigot_r, z_te - 0.5), (spigot_r, z_f - 0.5),
                                          (spigot_r - 0.5, z_f), (0, z_f)]))
rp = rp.fuse(revolve([(BEAD_R - BEAD_W[0] / 2, z_f - 0.01), (BEAD_R + BEAD_W[0] / 2, z_f - 0.01),
                      (BEAD_R + BEAD_W[1] / 2, z_f + BEAD_H), (BEAD_R - BEAD_W[1] / 2, z_f + BEAD_H)]))
rp_groove, rp_groove_z = shaft_groove(z_f - RP_GROOVE_WALL, +1)     # chamber in front: rear wall square
pilot_cuts = [revolve([(0, z_floor), (MOUTH_R - MOUTH_CHAMFER, z_floor), (MOUTH_R - MOUTH_CHAMFER, z_f - MOUTH_CHAMFER),
                       (MOUTH_R, z_f), (MOUTH_R, z_f + 1), (0, z_f + 1)]),
              cyl(PILOT_D, z_ry + G18_TAP_DEPTH, z_floor + 0.01),
              cyl(G18_TAP_D, z_ry - 1, z_ry + G18_TAP_DEPTH),
              Part.makeCone(G18_TAP_D / 2, PILOT_D / 2, (G18_TAP_D - PILOT_D) / 2, V(0, 0, z_ry + G18_TAP_DEPTH))]
for i in range(GROOVE_N):
    g = Part.makeBox(MOUTH_R - 2, GROOVE_WIDTH, GROOVE_DEPTH + 0.5, V(0, -GROOVE_WIDTH / 2, z_floor - GROOVE_DEPTH))
    g.rotate(V(0, 0, 0), Z, 360.0 / GROOVE_N * i + 45)
    pilot_cuts.append(g)
pilot_cuts += [cyl(TIE_HOLE, z_ry - 1, z_rp + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]
rp = rp.cut(G.fuse_all([rp_groove] + pilot_cuts))
rp = rp.removeSplitter()

# ---------------------------------------------------------------- seat ring
sr = revolve([(MOUTH_R, 0), (ring_out_r, 0), (ring_out_r, RING_T), (MOUTH_R, RING_T)])
sr = sr.fuse(revolve([(seat_r, -SEAT_PROUD), (seat_out_r, -SEAT_PROUD), (seat_out_r, z_flare), (sock_out_r, z_flare_end),
                      (sock_out_r, z_sock), (seat_r, z_sock)]))
for i in range(STRUT_N):
    s = Part.makeBox(ring_out_r - seat_out_r + 0.5, STRUT_W, STRUT_H, V(seat_out_r - 0.5, -STRUT_W / 2, 0))
    s = s.cut(Part.makeBox(MOUTH_R - seat_out_r, STRUT_W + 2, STRUT_RELIEF, V(seat_out_r, -STRUT_W / 2 - 1, -0.01)))
    s.rotate(V(0, 0, 0), Z, 360.0 / STRUT_N * (i + 0.5))
    sr = sr.fuse(s)
sr = sr.fuse(revolve([(STOP_LIP_R0, -t_c), (ring_out_r, -t_c), (ring_out_r, 0.01), (STOP_LIP_R0, 0.01)]))   # stop lip
# v4.4: the socket round the barrel, and inside it the spigot (O-ring groove) that goes into the barrel's bore
sr_cuts = [revolve([(0, -1), (seat_r, -1), (seat_r, z_sh), (SP_BORE / 2, z_sh), (SP_BORE / 2, z_sock + 1), (0, z_sock + 1)]),
           revolve([(sp_r, z_sh), (sock_r, z_sh), (sock_r, z_sock - LEAD_CHAMFER), (sock_r + LEAD_CHAMFER, z_sock + 0.01),
                    (sock_r + LEAD_CHAMFER, z_sock + 1), (SP_BORE / 2 - 0.01, z_sock + 1), (SP_BORE / 2 - 0.01, z_sp),
                    (sp_r - LEAD_CHAMFER, z_sp), (sp_r, z_sp - LEAD_CHAMFER), (sp_r, z_spg2), (sp_root_r, z_spg2),
                    (sp_root_r, z_spg1), (sp_r, z_spg0)])]
sr = sr.cut(G.fuse_all(sr_cuts)).removeSplitter()
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


# ---------------------------------------------------------------- chamber length, front cover (upper lid)
area = lambda d: math.pi * d * d / 4
A_annulus = area(CH_ID) - area(BARREL_OD)
probe_end = z_sock + 20.0
probe = cyl(CH_ID, 0, probe_end).cut(sr).cut(cyl(SEAT_D, -1, z_sh)).cut(cyl(2 * sock_r, z_sh, probe_end + 1))
v_probe = probe.Volume
z_fp_tip = probe_end + (CHAMBER_V * 1000 - v_probe) / A_annulus
z_tf = z_fp_tip + FP_SPIGOT
chamber_len = z_tf - z_te
z_fs = z_tf + FP_FLANGE_T
z_fp_end = z_fs + (CH_OD / 2 - fp_out_r) + FP_SLEEVE

fit_body_r = BARREL_ID / 2 - FIT_RADIAL_CLEAR
fit_tip_r = fit_body_r - FIT_LEAD_UNDER
fit_flange_r = max(BARREL_OD / 2 + FIT_FLANGE_OVER_BARREL, fp_out_r + FIT_FLANGE_OVER_SLEEVE)
lip_r = BARREL_ID / 2 + 0.2
fit_lead_catch = BARREL_ID / 2 - fit_tip_r
fit_lead_deg = math.degrees(math.atan2(FIT_LEAD_UNDER, FIT_LEAD_LEN))

z_stub_end = z_fp_end - STUB_PAST_SLEEVE
z_lip1 = z_stub_end + STUB_LIP_T
BARREL_STUB_LEN = z_stub_end - z_sh
z_flange0 = max(z_fp_end, z_lip1) + 0.5
z_stop = z_flange0 + FIT_FLANGE_T
z_fit1 = z_stop + FIT_INSERT
z_fit_cyl1 = z_fit1 - FIT_LEAD_LEN

fp_groove, fp_groove_z = shaft_groove(z_fp_tip + FP_CH_GROOVE_WALL, -1)
fp_bgroove, fp_bgroove_z = bore_groove(z_fp_tip + FP_GROOVE_WALL, -1)

# Front cover: chamber plug + stub lip + stop disc + self-centering fitting (no muzzle part).
front_cover = revolve([
    (sock_r, z_fp_tip), (spigot_r - LEAD_CHAMFER, z_fp_tip), (spigot_r, z_fp_tip + LEAD_CHAMFER),
    (spigot_r, z_tf), (CH_OD / 2, z_tf), (CH_OD / 2, z_fs),
    (fp_out_r, z_fs + (CH_OD / 2 - fp_out_r)), (fp_out_r, z_fp_end),
    (fit_flange_r, z_fp_end), (fit_flange_r, z_stop),
    (fit_body_r, z_stop), (fit_body_r, z_fit_cyl1),
    (fit_tip_r, z_fit1), (0, z_fit1),
    (0, z_fp_tip), (sock_r, z_fp_tip),
]).removeSplitter()
front_cover = front_cover.cut(G.fuse_all([
    cyl(2 * sock_r, z_fp_tip - 1, z_stub_end + 0.01),
    cyl(2 * lip_r, z_stub_end - 0.01, z_lip1 + 0.01),
    cyl(FIT_BORE, z_lip1 - 0.01, z_fit1 + 1),
]))
front_cover = front_cover.cut(G.fuse_all([fp_groove, fp_bgroove])).removeSplitter()

_dz = YOKE_CLEAR * math.sqrt(2)
_r0 = CH_OD / 2 + 0.3
z_fy1 = z_fs + YOKE_T
front_yoke = tie_plate(CH_OD / 2, z_fs, z_fy1).cut(revolve(
    [(0, z_fs - 1), (_r0, z_fs - 1), (_r0, z_fs + _dz - 0.3),
     (fp_out_r + YOKE_CLEAR, z_fs + _dz + CH_OD / 2 - fp_out_r - YOKE_CLEAR),
     (fp_out_r + YOKE_CLEAR, z_fy1 + 1), (0, z_fy1 + 1)])).removeSplitter()

_stick = WASHER_T + NUT_T + 2.0
z_front = z_fy1
z_rod0, z_rod1 = z_ry - _stick, z_front + _stick
tie_len = z_rod1 - z_rod0


def rods_yoke():
    """Both tie rods with a washer and a nut on the rear plug and the front yoke."""
    hw = []
    for a in TIE_ANGLES:
        x, y = at(TIE_R, a)[:2]
        hw.append(cyl(TIE_D, z_rod0, z_rod1, x, y))
        for zf, sgn in ((z_ry, -1), (z_fy1, +1)):
            zw = zf + sgn * WASHER_T
            hw.append(cyl(WASHER_D, min(zf, zw), max(zf, zw), x, y).cut(cyl(TIE_HOLE, zf - 2, zf + 2, x, y)))
            zn = zw + sgn * NUT_T
            hw.append(G.hex_prism(NUT_AF, min(zw, zn), max(zw, zn), x, y).cut(cyl(TIE_D, zw - 4, zw + 4, x, y)))
    return G.fuse_all(hw)


hardware = rods_yoke()

# pack footprint
_fp2d = G.fuse_all([cyl(CH_OD, 0, 1)] + ears(0, 1) + [cyl(WASHER_D, 0, 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES])
_nbrs = {"hex": [at(PACK_PITCH, 60 * k) for k in range(6)],
         "square": [at(PACK_PITCH * (math.sqrt(2) if k % 2 else 1), 45 * k) for k in range(8)]}
pack_gap = {k: min(_fp2d.distToShape(_fp2d.translated(c))[0] for c in cs) for k, cs in _nbrs.items()}
pack_grow = TIE_R + EAR_R - CH_OD / 2

tube = lambda od, idd, z0, z1: cyl(od, z0, z1).cut(cyl(idd, z0 - 1, z1 + 1))
barrel_stub = tube(BARREL_OD, BARREL_ID, z_sh, z_stub_end)
real_barrel = tube(BARREL_OD, BARREL_ID, z_stop, z_stop + REAL_BARREL_SHOW)
chamber = tube(CH_OD, CH_ID, z_te, z_tf)
chamber_air = (cyl(CH_ID, 0, z_fp_tip).cut(sr).cut(cyl(SEAT_D, -1, z_sh)).cut(cyl(BARREL_OD, z_sh, z_fp_tip + 1)))
chamber_v = chamber_air.Volume / 1000

A_bore = area(BARREL_ID)
A_seat = area(SEAT_D)
A_seat_eff = area(SEAT_D + SEAT_LAND)
A_dia = area(2 * MOUTH_R)
A_curtain = math.pi * SEAT_D * LIFT
A_sock_annulus = area(CH_ID) - area(2 * sock_out_r)
z_entry_top = z_flare + (MOUTH_R - seat_out_r)
A_entry = 2 * math.pi * MOUTH_R * (z_entry_top - RING_T) - STRUT_N * STRUT_W * (z_entry_top - RING_T)
open_ratio = 1 - A_seat_eff / A_dia
annulus_w = MOUTH_R - (seat_r + SEAT_LAND / 2)
dia_strain = math.hypot(annulus_w, LIFT) / annulus_w - 1
pocket_v = (A_dia * LIFT + area(PILOT_D) * (z_floor - z_ry - G18_TAP_DEPTH)) / 1000
dead_v = (A_seat * z_sh + area(SP_BORE) * (z_sp - z_sh)) / 1000
F_rp = P_MAX_BAR * 0.1 * area(CH_ID)
F_ring = P_MAX_BAR * 0.1 * A_dia
F_open = P_WORK_BAR * 0.1 * A_dia
TIE_SIGMA = (F_rp + F_ring) / len(TIE_ANGLES) / TIE_STRESS_A
YOKE_SIGMA = 6 * F_rp / 2 * (TIE_R - 4 * CH_OD / 2 / (3 * math.pi)) / ((CH_OD - G18_TAP_D) * YOKE_T ** 2)

fitting = G.push_in_fitting(0, 0, 0)
fitting.rotate(V(0, 0, 0), X, 180)
fitting.translate(V(0, 0, z_ry))

ball = Part.makeSphere(BARREL_ID / 2, V(0, 0, z_fit1 + BARREL_ID / 2 + 0.5))
torus = lambda rc, cs, z: Part.makeTorus(rc, cs / 2, V(0, 0, z), Z)
orings_g = G.fuse_all([
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], rp_groove_z[0] + GROOVE_W * CH_ORING[1] / 2),
    torus(ch_root_r + CH_ORING[1] / 2, CH_ORING[1], fp_groove_z[1] - GROOVE_W * CH_ORING[1] / 2),
    torus(sp_root_r + SP_ORING[1] / 2, SP_ORING[1], z_spg2 - GROOVE_W * SP_ORING[1] / 2),
    torus(br_root_r - BR_ORING[1] / 2, BR_ORING[1], fp_bgroove_z[1] - GROOVE_W * BR_ORING[1] / 2),
])

F_stub = F_ring
lip_bearing = F_stub / max(math.pi * (sock_r ** 2 - lip_r ** 2), 1e-6)
fit_wall = fit_body_r - FIT_BORE / 2
module_len = z_fit1 - z_ry

checks = [
    ("rear plug, seat ring, front cover valid single solids",
     all(G.single_solid(s) for s in (rp, sr, front_cover))),
    ("rear plug / diaphragm / seat ring clear (bead and the proud seat aside)",
     G.no_overlap(sr.cut(cyl(2 * seat_out_r + 0.2, -1, 0)), diaphragm) and G.no_overlap(sr, rp) and
     G.no_overlap(rp.cut(cyl(CH_ID + 2, z_f, 1)), diaphragm)),
    ("stop lip lands on the rear plug's face (squeeze %.0f %%)" % (DIA_SQUEEZE * 100),
     abs(sr.BoundBox.ZMin - z_f) < 1e-6 and G.no_overlap(sr, rp.cut(cyl(2 * BEAD_R + 2, z_f, 1)))),
    ("seat %.0f %% of the barrel bore" % (A_seat / A_bore * 100), A_seat >= 0.4 * A_bore),
    ("seat curtain >= 0.7 x seat (lift %.1f: %.0f mm2)" % (LIFT, A_curtain), A_curtain >= 0.7 * A_seat),
    ("chamber annulus round the socket >= 1.3 x the curtain (%.0f vs %.0f mm2)" % (A_sock_annulus, A_curtain),
     A_sock_annulus >= 1.3 * A_curtain),
    ("gallery entry over the clamp ring >= 1.5 x seat (%.0f mm2)" % A_entry, A_entry >= 1.5 * A_seat),
    ("opens after the pilot loses <= 55 %% (%.0f %%)" % (open_ratio * 100), open_ratio >= 0.45),
    ("diaphragm stretch at full lift <= 30 %% (%.0f %%)" % (dia_strain * 100), dia_strain <= 0.30),
    ("chamber %.0f cm3 within 3 %% of target" % chamber_v, abs(chamber_v - CHAMBER_V) <= 0.03 * CHAMBER_V),
    ("tie rods: M3 at %.0f MPa with rear plug and seat ring pushing at once (%.0f + %.0f N at %.0f bar)"
     % (TIE_SIGMA, F_rp, F_ring, P_MAX_BAR), TIE_SIGMA <= 150.0),
    ("rear plug's ears bend at <= 20 MPa at %.0f bar (%.0f)" % (P_MAX_BAR, YOKE_SIGMA), YOKE_SIGMA <= 20.0),
    ("front yoke on the front cover's flange, clear of the cover", abs(front_yoke.BoundBox.ZMin - z_fs) < 1e-6
     and z_fy1 <= z_fp_end and G.no_overlap(front_yoke, front_cover)),
    ("tie rods clear of the tube and the plugs",
     TIE_R - TIE_HOLE / 2 >= CH_OD / 2 + 0.3 and G.no_overlap(hardware, G.fuse_all([chamber, rp, front_cover]))),
    ("pack: footprint >= %.1f mm off the neighbours' (hex %.1f, square %.1f)"
     % (PACK_CLEAR, pack_gap["hex"], pack_gap["square"]), min(pack_gap.values()) >= PACK_CLEAR),
    ("chamber O-ring stretch 0..6 %% (%.1f %%)" % (ch_stretch * 100), 0 <= ch_stretch <= 0.06),
    ("barrel O-ring stretch 0..6 %% (%.1f %%)" % (br_stretch * 100), 0 <= br_stretch <= 0.06),
    ("spigot O-ring stretch 0..6 %% (%.1f %%)" % (sp_stretch * 100), 0 <= sp_stretch <= 0.06),
    ("front plug: >= 1.2 mm between its two grooves, chamber groove inside the spigot",
     fp_groove_z[0] >= fp_bgroove_z[1] + 1.2 and fp_groove_z[1] <= z_tf - 2.0),
    ("stub bottoms on the cover lip, clear of the seat ring",
     abs(barrel_stub.BoundBox.ZMax - z_stub_end) < 1e-6 and G.no_overlap(sr, barrel_stub)),
    ("stub lip covers the tube wall (%.2f mm radial), bearing <= 25 MPa at %.0f bar (%.1f)"
     % (sock_r - lip_r, P_MAX_BAR, lip_bearing),
     sock_r - lip_r >= BARREL_WALL - 0.05 and lip_bearing <= 25.0),
    ("fitting: plain (no O-ring), wall >= 1.5 mm, insert %.0f mm, bore >= seat" % FIT_INSERT,
     fit_wall >= 1.5 and FIT_INSERT >= 20.0 and FIT_BORE >= SEAT_D),
    ("fitting lead cone: %.0f mm, tip wall >= 1.2 mm, catch >= 1.0 mm radial (%.1f mm, tip wall %.1f)"
     % (FIT_LEAD_LEN, fit_lead_catch, fit_tip_r - FIT_BORE / 2),
     FIT_LEAD_LEN >= 6.0 and FIT_LEAD_LEN <= FIT_INSERT - 10.0
     and fit_tip_r - FIT_BORE / 2 >= 1.2 and fit_lead_catch >= 1.0
     and z_fit_cyl1 > z_stop + 10.0),
    ("fitting clear of the stub; stop disc clear of the real barrel OD",
     z_stop >= z_stub_end and G.no_overlap(front_cover, barrel_stub)
     and G.no_overlap(front_cover.common(cyl(2 * fit_flange_r + 2, z_flange0 - 0.5, z_stop + 0.01)),
                      real_barrel)),
    ("real barrel butts on the stop face (land %.1f past tube, rim %.1f past sleeve), fitting inside"
     % (fit_flange_r - BARREL_OD / 2, fit_flange_r - fp_out_r),
     abs(real_barrel.BoundBox.ZMin - z_stop) < 1e-6
     and fit_flange_r >= BARREL_OD / 2 + FIT_FLANGE_OVER_BARREL - 1e-9
     and fit_flange_r >= fp_out_r + FIT_FLANGE_OVER_SLEEVE - 1e-9
     and front_cover.BoundBox.ZMax <= z_fit1 + 1e-6
     and abs((front_cover.BoundBox.ZMax - z_stop) - FIT_INSERT) < 1e-3),
    ("no muzzle part: rods end on the front yoke (z_front = z_fy1)", abs(z_front - z_fy1) < 1e-9),
    ("pilot fitting's hex and body clear of the rear plug behind its back face",
     G.no_overlap(fitting.common(cyl(100, z_ry - 50, z_ry)), rp) and fitting.BoundBox.ZMax <= z_ry + G18_TAP_DEPTH),
    ("drilling template valid single solid", G.single_solid(jig_guide)),
    ("O-ring cone: mouth over the free ring (Ø%.1f > %.1f), exit under the bore (Ø%.1f < %.1f), taper <= 10 deg"
     % (_cone_in, _o_free, _cone_out, CH_ID),
     G.single_solid(oring_cone) and _cone_in > _o_free and 2 * spigot_r + 0.05 <= _cone_out < CH_ID
     and math.degrees(math.atan2((_cone_in - _cone_out) / 2, CONE_LEN)) <= 10.0),
    ("seat proud of the clamp face, < half the diaphragm", 0 < SEAT_PROUD < DIA_T / 2),
]

report = [
    NAME,
    "  flow path              : seat Ø%.0f (%.0f mm2 = %.0f %% of the Ø%.1f bore), curtain %.0f at lift %.1f,"
    " annulus round the socket %.0f, gallery entry %.0f"
    % (SEAT_D, A_seat, A_seat / A_bore * 100, BARREL_ID, A_curtain, LIFT, A_sock_annulus, A_entry),
    "  diaphragm              : Ø%.1f x %.1f, free Ø%.1f, squeeze %.0f %% (stop lip), stretch %.0f %% at full lift"
    % (2 * DIA_R, DIA_T, 2 * MOUTH_R, DIA_SQUEEZE * 100, dia_strain * 100),
    "  chamber                : %.0f cm3, tube %.0f x %.1f aluminium, %.0f mm long, %.0f g"
    % (chamber_v, CH_OD, CH_WALL, chamber_len, (area(CH_OD) - area(CH_ID)) * chamber_len * 2.70e-3),
    "  module                 : Ø%.0f (ears %.0f across), %.0f mm long rear plug to fitting tip; stub %.0f mm;"
    " no muzzle clamp" % (CH_OD, 2 * (TIE_R + EAR_R), module_len, BARREL_STUB_LEN),
    "  force path             : seat ring -> stub -> lip in front cover -> front yoke -> rods;"
    " seat push %.0f N at %.0f bar" % (F_stub, P_MAX_BAR),
    "  stub / real barrel     : stub 25 x 0.6 x %.0f through the chamber, bottoms in the cover;"
    " flat stop Ø%.1f (tube butts), fitting Ø%.1f x %.0f + lead cone %.0f mm to Ø%.1f"
    " (catch %.1f mm radial, %.0f deg; bore Ø%.0f, no O-ring)"
    % (BARREL_STUB_LEN, 2 * fit_flange_r, 2 * fit_body_r, FIT_INSERT, FIT_LEAD_LEN,
       2 * fit_tip_r, fit_lead_catch, fit_lead_deg, FIT_BORE),
    "  tie rods               : 2 x M3 x %.0f at R%.1f, %.0f / %.0f deg; nuts on rear plug and front yoke only"
    % (tie_len, TIE_R, *TIE_ANGLES),
    "  pack                   : pitch %.0f; %.1f mm to neighbours (hex), %.1f (square); ears stand %.1f mm out of Ø%.0f"
    % (PACK_PITCH, pack_gap["hex"], pack_gap["square"], pack_grow, CH_OD),
    "  O-rings                : 2 x %g x %g (chamber), 1 x %g x %g (stub in cover), 1 x %g x %g (seat spigot);"
    " fitting dry" % (CH_ORING + BR_ORING + SP_ORING),
    "  rear plug / seat ring / front cover: %.1f / %.1f / %.1f cm3"
    % (rp.Volume / 1000, sr.Volume / 1000, front_cover.Volume / 1000),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]

if not GATLING_FAT_COAX_LIBRARY:
    print("\n".join(report))
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Rear_plug", rp, "stator"), ("Seat_ring", sr, "rotor"), ("Diaphragm", diaphragm, "shoe"),
                        ("Front_cover", front_cover, "stator"), ("Front_yoke", front_yoke, "stator")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_stub", barrel_stub, "ghost"), ("Real_barrel", real_barrel, "ghost"),
                        ("Chamber_tube", chamber, "ghost"), ("ORings", orings_g, "oring"),
                        ("Pilot_fitting", fitting, "steel"), ("Ball", ball, "flow"),
                        ("Tie_rods", hardware, "steel")):
        sc.add("Bought", n, s, style)
    half = Part.makeBox(120, 60, 1200, V(-60, -60, -600))
    for n in ("Rear_plug", "Seat_ring", "Diaphragm", "Front_cover", "Barrel_stub", "Real_barrel",
              "Chamber_tube", "ORings", "Ball", "Pilot_fitting", "Front_yoke", "Tie_rods"):
        style = dict(Rear_plug="stator", Seat_ring="rotor", Diaphragm="shoe", Front_cover="stator",
                     ORings="oring", Ball="flow", Pilot_fitting="steel", Front_yoke="stator",
                     Tie_rods="steel").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("ОБРЕЗОК 25x0,6, %.0f мм" % BARREL_STUB_LEN, (-45, 0, z_sh + BARREL_STUB_LEN * 0.55)),
        ("КАМЕРА: труба %.0fx%.1f, %.0f мм, %.0f см3" % (CH_OD, CH_WALL, chamber_len, chamber_v),
         (45, 0, z_tf * 0.5)),
        ("КРЫШКА: упор обрезка + упор ствола", (45, 0, z_tf + 8)),
        ("УПОР СТВОЛА Ø%.1f" % (2 * fit_flange_r), (45, 0, z_stop - FIT_FLANGE_T / 2)),
        ("ФИТТИНГ Ø%.1f + конус -> Ø%.1f (самоцентр.)" % (2 * fit_body_r, 2 * fit_tip_r),
         (45, 0, z_stop + FIT_INSERT * 0.45)),
        ("СТВОЛ (снаряд) 25x0,6", (45, 0, z_stop + REAL_BARREL_SHOW * 0.55)),
        ("КОЛЬЦО СЕДЛА: седло Ø%.0f" % SEAT_D, (45, 0, 10)),
        ("МЕМБРАНА Ø%.1f" % (2 * DIA_R), (45, 0, 0)),
        ("ЗАДНЯЯ ПРОБКА с ушами: пилот G1/8 -> M3R110 A", (45, 0, z_rp)),
        ("2 шпильки M3 x %.0f (до ярма крышки)" % tie_len, (45, 0, z_ry - 5)),
    ]:
        sc.label("Labels", text, pos)
    sc.add("Jig", "Jig_guide", jig_guide, "stator", offset=V(-3 * CH_OD, 0, z_rp))
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

    for n, s, flip in (("rear_plug", rp, False), ("seat_ring", sr, False), ("front_cover", front_cover, True),
                       ("diaphragm", diaphragm_free, False), ("jig_guide", jig_guide, False),
                       ("front_yoke", front_yoke, True), ("oring_cone", oring_cone, True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
