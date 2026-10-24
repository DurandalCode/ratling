# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v4.4: the chamber is a bought tube round the barrel.

v4.4 bore: the aluminium tube that came is ~Ø34.6 inside, not 38 - 2 x 1.5 = Ø35: the bare Ø34.6 spigots of the
plugs went in only just, and with the 29 x 3 rings (~22 % squeeze there) not at all. CH_ID is the measured bore now,
not derived from the wall. The spigots go Ø34.4 (0.1 per side, CH_CLEAR), the rings stay 29 x 3 at 18 % squeeze
(groove Ø29.9 -> 29.7). The seat ring (Ø34.0, it fits) and the diaphragm do not change. The chamber grows a few mm
for the same 100 cm3; the rods stay 358 mm.

v4.4 muzzle: the muzzle clamp is the default now (MUZZLE_CLAMP = True; it was an option for the long barrel).
The seat ring's push goes from the barrel into a collar squeezed on it over a wrap of tape, not into the lip of
a ring on the barrel's end, so the barrel's cut end and its length no longer set the stack. The collar is two
identical halves split through the axis and both rod ears, two M3 x 12 across the seam in each ear (four in all):
both sides squeeze alike, nothing has to bend shut, one part printed twice. (The first clamp was one piece split
through one ear, the other ear short.) The muzzle ring stays as an option (MUZZLE_CLAMP = False), still exported.

v4.4 (lighter): the chamber tube is aluminium 38 x 1.5 (was steel 38 x 1.2): bore Ø35.0, so the chamber
O-rings go 30 x 3 -> 29 x 3 and the chamber grows to ~270 mm for the same 100 cm3. The narrower bore left
only ~169 mm2 of chamber air round the seat ring's socket (its 24 x 2.5 O-ring groove and wall sat in the
way), 1.16 x the curtain. So the barrel no longer seals in the socket: a short spigot on the shoulder goes
into the barrel's bore and seals there on a 20 x 2 O-ring (bore through it Ø18, still over the Ø16 seat).
The barrel's end bottoms on the flat shoulder round the spigot as before. The socket is a plain locating
sleeve now, 2.2 mm thinner. (A face O-ring under the barrel's end was tried and dropped: a 0.6 wall cannot
both press the ring and land on a stop, so the nuts would set the squeeze and the edge would cut the ring.)
The cut end need not be very square any more; deburr its inside edge. The front plug keeps its 24 x 2.5.

v4.3 (in v4.2 the glue held the pressure): no glue and no screws. Two M3 threaded rods outside the tube, at
30 / 210 deg, hold the stack. A rear yoke behind the rear plug, a front yoke on the front plug's flange, and a muzzle
ring on the barrel's front end each take the rods through their ears, with a nut and a washer:

    rear nut ─ rear yoke ─ rear plug ─ tube ─ front plug ─ front yoke ─ front nut
                           rear plug ─ seat ring ─ barrel ─────────────── muzzle ring ─ muzzle nut

The chamber's push on both plugs ends in the rods (the tube only seals, between the plugs' flanges). The pilot's
push on the seat ring goes into the barrel's rear end, along the barrel in compression to the muzzle ring,
and from there into the rods. The barrel is only located by its O-rings: nothing is screwed into it. The plugs
stay round (Ø38) so the O-ring cone still slides over them; the yokes go on afterwards. At 30 / 210 deg each
rod sits alone in a gap between three tubes of a hex pack at PACK_PITCH (each module owns one up and one down
gap); a square pack has room to spare. Modules go into a pack all turned the same way. The assembly press is
gone: the rods do its job and stay on.

v4.2 (kept below for history; its glue bands, socket band and barrel screws are gone in v4.3).

v4.2 (the bought tube is too hard to drill): nothing is drilled through it any more. The rear plug and the
front plug are glued into the tube on a close-fitting band (0.1 mm per side, two grip grooves, a relief groove
between the band and the O-ring that catches the squeezed-out glue). The seat ring is not screwed to the tube
any more: its socket is glued to the barrel on a band at its mouth, the barrel is glued in the front plug's sleeve
(the barrel screws stay), so the pilot's push on the seat ring goes seat ring -> barrel -> front plug -> tube ->
rear plug through glue only. The screw lugs and the screw jig are gone. Thin CA or 5-minute epoxy; keep it off
the O-rings. To take it apart: acetone on the CA joints, or cut the tube (it cuts, it just does not drill).

The barrel O-rings are 24 x 2.5 now (were 24 x 2, too thin): the annulus round the socket drops to ~200 mm2,
still over the valve's curtain (146); 24 x 3 would not (158).

v4.1 (kept below for history).

v4.1 (after v4 leaked into the barrel while the pilot filled): the seat ring
was held only by the barrel, so the pilot pushed it (and the barrel) ~110 N
forward off the diaphragm until the chamber came up. Now the seat ring is
screwed to the chamber tube by four ST2.2 through lugs on its clamp ring (gone in v4.2). The seat stands SEAT_PROUD
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
    seat ring ... seat face on the bed: clamp ring, Ø16 seat, struts, 45 deg
                  flare out to the barrel socket (v4.4: a spigot in the barrel's
                  bore with a 20 x 2 O-ring on it), a stop lip round the
                  diaphragm that sets the squeeze.
    O-ring cone . a funnel slipped over either end of the chamber tube: the
                  30 x 3 rings close down its taper and come off it a little
                  under the tube's bore, clear of the cut edge. Grease them.
    front plug .. sleeve end on the bed: closes the chamber round the barrel
                  (30 x 3 O-ring in the tube, 24 x 2.5 on the barrel).
    rear yoke ... a plate behind the rear plug with the two rod ears; the pilot
                  fitting goes through its hole.
    front yoke .. a plate over the front plug's sleeve, seated on its 45 deg
                  flange, with the two rod ears. Front face on the bed: the 45 deg seat opens
                  upward, no overhang.
    muzzle clamp  a collar 20 mm long on the barrel, 300 mm from its shoulder (flush with the 300 mm barrel's end),
                  two identical halves split through both ears, 4 x M3 x 12 across the seam, over a wrap of tape
                  (default). Flange end on the bed, print two.
    muzzle ring . (option, MUZZLE_CLAMP = False) on the barrel's front end (in a counterbore), with the two
                  rod ears.
    muzzle sleeve (option, in place of the muzzle ring; not in the module, a bench test for the
                  mitrailleuse's length): the muzzle ring with a Ø32 sleeve SLEEVE_LEN ahead of the barrel,
                  bore Ø30 (3.1 mm round the ball), the barrel's end on the same lip as in the ring, located
                  in a SLEEVE_SOCKET socket behind it; four slots at its root let the air out, so it does
                  not push the ball down the sleeve. Same rods and nuts. Socket end on the bed, a 45 deg
                  skirt under the ears.
    diaphragm ... Ø31 disc of rubber sheet with one bleed hole (v4.1: no pin holes).

Assembly (v4.4): no glue. Deburr the barrel's rear end inside. Pilot fitting into the rear plug. Diaphragm
on the rear plug's face (the bead inside it), seat ring on top (its stop lip round the diaphragm, on the
plug's face). 20 x 2 O-ring on the spigot (grease), barrel into the socket over it, pushed home on the
shoulder. Tube over the seat ring and barrel with the O-ring cone onto the rear plug, in to
its flange. Front plug onto the barrel and into the tube (cone again), in to its flange. Rear yoke over the
fitting, front yoke over the sleeve, tape round the barrel and the muzzle clamp over it (screws loose), the rods
through all three ears. Nuts
snug at the rear and on the front yoke, then the muzzle nuts until the seat ring's stop lip sits on the rear
plug (it does not take much: the lip sets the squeeze, the nuts only hold it there). Then tighten the muzzle
clamp's two screws (snug, not cranked: the 0.6 wall must stay round).

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3v4_coaxial_chamber.py').read())
Bench test of the length (docs/test-plan.md, Stage 3 v4.4 length): the same module three ways, bare
300 mm barrel, the muzzle sleeve on it, and a long barrel. The long barrel is a variant:
    OVERRIDE = {"BARREL_LEN": 535.0, "MUZZLE_CLAMP": True, "NAME": "stage3v4_long_barrel"}
before exec: the muzzle clamp stays 300 mm from the shoulder, so the rods are the same 358 mm for any barrel
(the clamp's own rods; without MUZZLE_CLAMP the muzzle ring goes on the long barrel's end and the rods grow).
    muzzle clamp (default, MUZZLE_CLAMP; the muzzle ring in its place when False): a collar squeezed on the barrel in two
                  halves, 4 x M3 x 12 across the seam, over a wrap of tape. Wrap the tape, put the halves round it
                  with the screws loose, rods and nuts as for the ring (the nuts set the seat ring's lip), then
                  tighten the four screws evenly until the halves meet (a hard stop: the bore is round, 0.25 mm under the
                  taped barrel, so the tape is crushed all round; if the halves meet with no grip, add a wrap).
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
CH_OD, CH_WALL = 38.0, 1.5  # bought chamber tube, v4.4: aluminium (v4-v4.3: steel 38 x 1.2)
CH_ID = 34.6                # measured bore, not OD - 2 x wall (35.0): the Ø34.6 spigots of the tube that came went in only just

RADIAL_CLEAR = 0.20
CH_CLEAR = 0.10             # plugs' spigots in the chamber tube, per side: Ø34.4 in the Ø34.6 bore
CH_ORING = (29.0, 3.0)      # ID x CS, in the chamber tube (rear and front plug); v4.4: 30 x 3 would sit slack in Ø35
BR_ORING = (24.0, 2.5)      # ID x CS, on the barrel (front plug; v4.4: no longer in the seat ring's socket)
SP_ORING = (20.0, 2.0)      # ID x CS, v4.4: on the seat ring's spigot, inside the barrel's bore
ORING_SQUEEZE = 0.18        # chamber O-rings; 18 % at Ø34.6 (was 15 % at Ø35: in the Ø34.6 tube ~22 %, very tight)
BR_SQUEEZE = 0.12           # v4.1: the barrel's 24 x 2 a little easier, it was cut by the barrel's edge going in
GROOVE_W = 1.3              # x CS
LEAD_CHAMFER = 1.0
# v4.3: two M3 threaded rods outside the tube hold the stack (no glue, nothing drilled through the tube).
TIE_D, TIE_HOLE, TIE_STRESS_A = 3.0, 3.4, 5.03     # M3: stress area mm2
TIE_R, TIE_ANGLES = 21.5, (30.0, 210.0)            # each alone in its gap of a hex pack
EAR_R = 4.0                 # ear round the rod
EAR_ROOT_R = 14.0           # ears are the hull of this circle round the axis and the ear circle
WASHER_D, WASHER_T, NUT_AF, NUT_T = 7.0, 0.5, 5.5, 2.4
YOKE_T = 8.0                # rear and front yoke (the rear one spans the fitting's hole like a beam)
YOKE_CLEAR = 0.2
FITTING_HOLE_D = 16.5       # rear yoke, over the pilot fitting's hex (13 AF)
MUZZLE_T, MUZZLE_CB = 8.0, 4.0                     # muzzle ring, its counterbore over the barrel's end
# muzzle clamp (default, MUZZLE_CLAMP): the muzzle ring as a collar squeezed on the barrel by its own four M3
# screws, CLAMP_AT from the barrel's shoulder whatever the barrel's length, so the rods stay the same and a
# longer barrel runs through it. In a hex pack every gap holds a rod, so there is no room for a lug: the collar
# is split in two through the axis and both ears (both run the collar's length), and in each ear two screws
# cross the seam between the bore and the rod. A wrap of tape (or thin rubber) lines it: grip, and an even
# squeeze, so the 0.6 wall is not pinched oval (the ball fits the bore tight).
MUZZLE_CLAMP = True         # default since v4.4 muzzle; False: the muzzle ring on the barrel's end
CLAMP_AT, CLAMP_W = 300.0, 20.0
CLAMP_LINER = 0.5           # tape round the barrel
CLAMP_CRUSH = 0.25          # the tape is crushed this much (radially) when the halves meet: the bore is cut that much under the lined barrel
CLAMP_GAP = 0.8             # the seam between the two halves; the screws close it to zero, a hard stop (the halves' bores are offset by half of it each, so closed they are one round bore)
CLAMP_SCREW_R = 16.6        # the screws' axis off the barrel's axis
CLAMP_SCREW_T, CLAMP_MU = 300.0, 0.4               # N per M3 screw in PETG (snug, not cranked), tape on steel
# muzzle sleeve (option): bore, and how far ahead of the barrel's end; the socket locates it on the barrel
SLEEVE_OD, SLEEVE_BORE, SLEEVE_LEN = 32.0, 30.0, 215.0
SLEEVE_SOCKET, SLEEVE_CLEAR = 25.0, 0.1
SLEEVE_VENTS = (4, 6.0, 24.0, 75.0)                 # slots: count, width, length, first angle (between the rods)
SLEEVE_BOW = 0.2                                    # a printed tube's own bow over its length
BALL_EXIT_MRAD = 5.0                                # sideways scatter of the ball leaving the barrel: assumed, not measured
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

PACK_PITCH = 40.0

# Drilling template: a disc of the diaphragm's own Ø with a guide for each
# hole. Rubber on a scrap board, template on top, drill, cut round it.
JIG_GUIDE_CLEAR = 0.15
JIG_GUIDE_T = 3.0

# Variants: set OVERRIDE = {"BARREL_LEN": 535.0, "NAME": "stage3v4_long_barrel"} before exec to replace any
# parameter above (those derived from it below follow).
try:
    globals().update(OVERRIDE)
except NameError:
    pass
if NAME != "stage3v4_coaxial_chamber":
    OUT_DIR = os.path.join(REPO, "exports", NAME)

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
z_fp_end = z_fs + (CH_OD / 2 - fp_out_r) + FP_SLEEVE

fp = revolve([(sock_r, z_fp_tip), (spigot_r - LEAD_CHAMFER, z_fp_tip), (spigot_r, z_fp_tip + LEAD_CHAMFER),
              (spigot_r, z_tf), (CH_OD / 2, z_tf), (CH_OD / 2, z_fs), (fp_out_r, z_fs + (CH_OD / 2 - fp_out_r)),
              (fp_out_r, z_fp_end), (sock_r, z_fp_end)])
fp_groove, fp_groove_z = shaft_groove(z_fp_tip + FP_CH_GROOVE_WALL, -1)  # chamber behind: front wall square
fp_bgroove, fp_bgroove_z = bore_groove(z_fp_tip + FP_GROOVE_WALL, -1)
fp = fp.cut(G.fuse_all([fp_groove, fp_bgroove])).removeSplitter()

# ---------------------------------------------------------------- tie rods: yokes, muzzle ring, rods
z_ry = z_rp - YOKE_T                         # rear yoke behind the rear plug
rear_yoke = tie_plate(CH_OD / 2, z_ry, z_rp).cut(cyl(FITTING_HOLE_D, z_ry - 1, z_rp + 1)).removeSplitter()
_dz = YOKE_CLEAR * math.sqrt(2)              # front yoke: on the front plug's 45 deg flange, round its sleeve
_r0 = CH_OD / 2 + 0.3
z_fy1 = z_fs + YOKE_T
front_yoke = tie_plate(CH_OD / 2, z_fs, z_fy1).cut(revolve(
    [(0, z_fs - 1), (_r0, z_fs - 1), (_r0, z_fs + _dz - 0.3),
     (fp_out_r + YOKE_CLEAR, z_fs + _dz + CH_OD / 2 - fp_out_r - YOKE_CLEAR),
     (fp_out_r + YOKE_CLEAR, z_fy1 + 1), (0, z_fy1 + 1)])).removeSplitter()
z_m0 = z_sh + BARREL_LEN - MUZZLE_CB         # muzzle ring: the barrel's end in its counterbore
z_m1 = z_m0 + MUZZLE_T
z_c1 = z_sh + CLAMP_AT                       # muzzle clamp: its front face, the ears along it
z_c0 = z_c1 - CLAMP_W
muzzle_ring = tie_plate(BARREL_OD / 2 + YOKE_CLEAR + 2.0, z_m0, z_m1).cut(G.fuse_all([
    cyl(BARREL_OD + 2 * YOKE_CLEAR, z_m0 - 1, z_m0 + MUZZLE_CB),
    revolve([(0, z_m0), (BARREL_ID / 2 + 0.2, z_m0), (BARREL_ID / 2 + 0.2, z_m1 - 1.0), (BARREL_ID / 2 + 1.2, z_m1 + 0.01),
             (BARREL_ID / 2 + 1.2, z_m1 + 1), (0, z_m1 + 1)])])).removeSplitter()
_stick = WASHER_T + NUT_T + 2.0              # washer, nut and a couple of threads past it
z_front = z_c1 if MUZZLE_CLAMP else z_m1     # the rods' front ear
z_rod0, z_rod1 = z_ry - _stick, z_front + _stick
tie_len = z_rod1 - z_rod0
tie_len_ring = z_m1 + _stick - z_rod0        # the muzzle ring's or the sleeve's rods (their ear is at z_m1)


def rods(z_ear):
    """Both tie rods with a washer and a nut on each ear: rear yoke, front yoke and the muzzle ear at z_ear."""
    hw = []
    for a in TIE_ANGLES:
        x, y = at(TIE_R, a)[:2]
        hw.append(cyl(TIE_D, z_rod0, z_ear + _stick, x, y))
        for zf, sgn in ((z_ry, -1), (z_fy1, +1), (z_ear, +1)):          # washer on the ear, nut beyond it
            zw = zf + sgn * WASHER_T
            hw.append(cyl(WASHER_D, min(zf, zw), max(zf, zw), x, y).cut(cyl(TIE_HOLE, zf - 2, zf + 2, x, y)))
            zn = zw + sgn * NUT_T
            hw.append(G.hex_prism(NUT_AF, min(zw, zn), max(zw, zn), x, y).cut(cyl(TIE_D, zw - 4, zw + 4, x, y)))
    return G.fuse_all(hw)


hardware = rods(z_front)
hardware_ring = hardware if z_front == z_m1 else rods(z_m1)

# ---------------------------------------------------------------- muzzle clamp (option, in place of the muzzle ring)
_cb_r = BARREL_OD / 2 + CLAMP_LINER - CLAMP_CRUSH     # bore, closed: under the lined barrel, so it bites the tape all round
_co_r = EAR_ROOT_R + 3.0
_sa = TIE_ANGLES[0]
_ears_long = [hull_prism([(0, 0, EAR_ROOT_R), (*at(TIE_R, a)[:2], EAR_R)], z_c0, z_c1) for a in TIE_ANGLES]
_rr = TIE_R + EAR_R + 2
_cuts = []
for xs in (CLAMP_SCREW_R, -CLAMP_SCREW_R):          # two M3 x 12 across the seam in each ear; head and nut swap
    hy = -16 if xs > 0 else 6                       # sides, so the halves are one part turned 180 deg
    for zs in (z_c0 + 5, z_c1 - 5):
        _cuts += [Part.makeCylinder(1.7, 30, V(xs, -15, zs), Y),                                     # M3 x 12
                  Part.makeCylinder(3.1, 10, V(xs, hy, zs), Y),                                      # head
                  Part.makeCylinder(3.4, 10, V(xs, -10 - hy, zs), Y)]                                # nut
for c in _cuts:
    c.rotate(V(0, 0, 0), Z, _sa)
_whole = G.fuse_all([tie_plate(_co_r, z_c1 - MUZZLE_T, z_c1), cyl(2 * _co_r, z_c0, z_c1)] + _ears_long).cut(
    G.fuse_all(_cuts + [cyl(TIE_HOLE, z_c0 - 1, z_c1 + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]))
_halves, _closed = [], []
for sg in (1, -1):                                  # each side of the seam
    h = Part.makeBox(2 * _rr, 2 * _rr, CLAMP_W + 4, V(-_rr, CLAMP_GAP / 2 if sg > 0 else -CLAMP_GAP / 2 - 2 * _rr, z_c0 - 2))
    bore = cyl(2 * _cb_r, z_c0 - 1, z_c1 + 1, 0, sg * CLAMP_GAP / 2)   # centred on the axis once this half is moved in
    for c in (h, bore):
        c.rotate(V(0, 0, 0), Z, _sa)
    _halves.append(_whole.common(h).cut(bore).removeSplitter())
    _closed.append(_halves[-1].translated(App.Rotation(Z, _sa).multVec(V(0, -sg * CLAMP_GAP / 2, 0))))
muzzle_clamp_half = _halves[0]                      # printed twice: the other half is this one turned 180 deg
muzzle_clamp = Part.makeCompound(_halves)
cl_walls = (CLAMP_SCREW_R - 1.7 - _cb_r, TIE_R - TIE_HOLE / 2 - CLAMP_SCREW_R - 1.7)   # screw hole to bore, to rod
cl_liner = cyl(BARREL_OD + 2 * CLAMP_LINER, z_c0, z_c1).cut(cyl(BARREL_OD, z_c0 - 1, z_c1 + 1))   # the tape, for the model
cl_bare = cyl(BARREL_OD, z_c0 - 1, z_c1 + 1)                                  # the steel: the closed halves stop short of it, on the tape
muzzle = muzzle_clamp if MUZZLE_CLAMP else muzzle_ring     # the module's muzzle part (pack_frame & co. take this)
cl_hold = CLAMP_MU * 2 * math.pi * 2 * CLAMP_SCREW_T            # hoop tension = the two screws at a seam; x 2 pi
cl_p = 2 * CLAMP_SCREW_T / ((BARREL_OD / 2) * CLAMP_W)          # MPa on the barrel, evened by the liner
cl_hoop = cl_p * (BARREL_OD / 2) / BARREL_WALL
_clfp = G.fuse_all([cyl(2 * _co_r, 0, 1)] + ears(0, 1) + [cyl(WASHER_D, 0, 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES])

# ---------------------------------------------------------------- muzzle sleeve (option, in place of the muzzle ring)
z_end = z_sh + BARREL_LEN
z_sl0, z_sl1 = z_end - SLEEVE_SOCKET, z_end + SLEEVE_LEN
_ear_out = TIE_R + EAR_R
_skirt_h = _ear_out - SLEEVE_OD / 2                   # 45 deg under the ears, socket end down on the bed
_skirt = Part.makeCone(SLEEVE_OD / 2, _ear_out, _skirt_h, V(0, 0, z_m0 - _skirt_h)).common(
    G.fuse_all(ears(z_m0 - _skirt_h - 1, z_m0)))
_lip_r = BARREL_ID / 2 + 0.2                          # the barrel's end lands on it, as in the muzzle ring
_flare_end = z_end + 1.5 + (SLEEVE_BORE / 2 - _lip_r)
_vents = []
for k in range(SLEEVE_VENTS[0]):
    v = Part.makeBox(SLEEVE_OD, SLEEVE_VENTS[1], SLEEVE_VENTS[2], V(0, -SLEEVE_VENTS[1] / 2, z_m1 + 1.0))
    v.rotate(V(0, 0, 0), Z, SLEEVE_VENTS[3] + 360.0 / SLEEVE_VENTS[0] * k)
    _vents.append(v)
muzzle_sleeve = G.fuse_all([cyl(SLEEVE_OD, z_sl0, z_sl1), tie_plate(SLEEVE_OD / 2, z_m0, z_m1), _skirt]).cut(G.fuse_all(
    [cyl(BARREL_OD + 2 * SLEEVE_CLEAR, z_sl0 - 1, z_end),
     revolve([(0, z_end - 0.01), (_lip_r, z_end - 0.01), (_lip_r, z_end + 1.5), (SLEEVE_BORE / 2, _flare_end),
               (SLEEVE_BORE / 2, z_sl1 + 1), (0, z_sl1 + 1)])]
    + [cyl(TIE_HOLE, z_m0 - _skirt_h - 2, z_m1 + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES] + _vents)).removeSplitter()
sl_gap = (SLEEVE_BORE - BARREL_ID) / 2
sl_tilt = 2 * SLEEVE_CLEAR / SLEEVE_SOCKET * 1000     # mrad, the socket's play
sl_safe = (sl_gap - SLEEVE_CLEAR - SLEEVE_BOW) / ((sl_tilt + BALL_EXIT_MRAD) / 1000)
sl_vent_a = SLEEVE_VENTS[0] * SLEEVE_VENTS[1] * SLEEVE_VENTS[2]

# pack footprint: tube, ears, washers and nuts, against the neighbours' in a hex and a square pack
_fp2d = G.fuse_all([cyl(CH_OD, 0, 1)] + ears(0, 1) + [cyl(WASHER_D, 0, 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES])
_nbrs = {"hex": [at(PACK_PITCH, 60 * k) for k in range(6)],
         "square": [at(PACK_PITCH * (math.sqrt(2) if k % 2 else 1), 45 * k) for k in range(8)]}
pack_gap = {k: min(_fp2d.distToShape(_fp2d.translated(c))[0] for c in cs) for k, cs in _nbrs.items()}
pack_grow = TIE_R + EAR_R - CH_OD / 2
clamp_gap = min(_clfp.distToShape(_clfp.translated(c))[0] for c in _nbrs["hex"])

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
open_ratio = 1 - A_seat_eff / A_dia
annulus_w = MOUTH_R - (seat_r + SEAT_LAND / 2)
dia_strain = math.hypot(annulus_w, LIFT) / annulus_w - 1
pocket_v = (A_dia * LIFT + area(PILOT_D) * (z_floor - z_rp - G18_TAP_DEPTH)) / 1000
dead_v = (A_seat * z_sh + area(SP_BORE) * (z_sp - z_sh)) / 1000
F_rp = P_MAX_BAR * 0.1 * area(CH_ID)
F_ring = P_MAX_BAR * 0.1 * A_dia                            # pilot up at the top pressure, chamber empty
F_open = P_WORK_BAR * 0.1 * A_dia                            # pilot up, chamber empty: on the seat ring / barrel
TIE_SIGMA = (F_rp + F_ring) / len(TIE_ANGLES) / TIE_STRESS_A                # both at once, on the rear nuts: a bound
# rear yoke as a beam between the rods, the plug's push spread over its flange, the fitting's hole out of the section
YOKE_SIGMA = 6 * F_rp / 2 * (TIE_R - 4 * CH_OD / 2 / (3 * math.pi)) / ((CH_OD - FITTING_HOLE_D) * YOKE_T ** 2)

checks = [
    ("rear plug, seat ring, front plug valid single solids", all(G.single_solid(s) for s in (rp, sr, fp))),
    ("rear plug / diaphragm / seat ring clear (bead and the proud seat aside)",
     G.no_overlap(sr.cut(cyl(2 * seat_out_r + 0.2, -1, 0)), diaphragm) and G.no_overlap(sr, rp) and
     G.no_overlap(rp.cut(cyl(CH_ID + 2, z_f, 1)), diaphragm)),
    ("stop lip lands on the rear plug's face (squeeze %.0f %%)" % (DIA_SQUEEZE * 100),
     abs(sr.BoundBox.ZMin - z_f) < 1e-6 and G.no_overlap(sr, rp.cut(cyl(2 * BEAD_R + 2, z_f, 1)))),
    ("seat %.0f %% of the barrel bore" % (A_seat / A_bore * 100), A_seat >= 0.4 * A_bore),
    ("seat curtain >= 0.7 x seat (lift %.1f: %.0f mm2)" % (LIFT, A_curtain), A_curtain >= 0.7 * A_seat),
    ("chamber annulus round the socket >= 1.3 x the curtain, the real bottleneck (%.0f vs %.0f mm2)" % (A_sock_annulus, A_curtain),
     A_sock_annulus >= 1.3 * A_curtain),
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
    ("spigot: wall under its groove >= 1.2 mm, its bore over the seat", sp_root_r - SP_BORE / 2 >= 1.2 and SP_BORE >= SEAT_D),
    ("pilot pocket floor grooves above the G1/8 tap", z_floor - GROOVE_DEPTH - (z_rp + G18_TAP_DEPTH + 2.4) >= 2.0),
    ("rear plug groove behind the pocket, ahead of the flange", rp_groove_z[1] <= z_floor - 2.0 and rp_groove_z[0] >= z_te + 2.0),
    ("spigot inside the socket, clear of its lead-in", z_sp + 2.0 <= z_sock - LEAD_CHAMFER),
    ("barrel on the shoulder, clear of the spigot and the socket", G.no_overlap(sr, barrel) and z_spg0 > z_sh),
    ("tie rods: M3 at %.0f MPa with rear plug and seat ring pushing at once (%.0f + %.0f N at %.0f bar)"
     % (TIE_SIGMA, F_rp, F_ring, P_MAX_BAR), TIE_SIGMA <= 150.0),
    ("rear yoke bends at <= 20 MPa at %.0f bar (%.0f)" % (P_MAX_BAR, YOKE_SIGMA), YOKE_SIGMA <= 20.0),
    ("tie rods clear of the tube and the plugs",
     TIE_R - TIE_HOLE / 2 >= CH_OD / 2 + 0.3 and G.no_overlap(hardware, G.fuse_all([chamber, rp, fp]))),
    ("yokes and muzzle ring valid single solids, clear of plugs and barrel",
     all(G.single_solid(s) for s in (rear_yoke, front_yoke, muzzle_ring))
     and G.no_overlap(rear_yoke, rp) and G.no_overlap(front_yoke, fp) and G.no_overlap(muzzle_ring, barrel)),
    ("front yoke on the front plug's flange, inside the sleeve's length", abs(front_yoke.BoundBox.ZMin - z_fs) < 1e-6
     and z_fy1 <= z_fp_end),
    ("pack: footprint >= %.1f mm off the neighbours' (hex %.1f, square %.1f)" % (PACK_CLEAR, pack_gap["hex"], pack_gap["square"]),
     min(pack_gap.values()) >= PACK_CLEAR),
    ("chamber O-ring stretch 0..6 %% (%.1f %%)" % (ch_stretch * 100), 0 <= ch_stretch <= 0.06),
    ("barrel O-ring stretch 0..6 %% (%.1f %%)" % (br_stretch * 100), 0 <= br_stretch <= 0.06),
    ("front plug: >= 1.2 mm between its two grooves, chamber groove inside the spigot",
     fp_groove_z[0] >= fp_bgroove_z[1] + 1.2 and fp_groove_z[1] <= z_tf - 2.0),
    ("spigot O-ring stretch 0..6 %% (%.1f %%)" % (sp_stretch * 100), 0 <= sp_stretch <= 0.06),
    ("chamber %.0f cm3 within 3 %% of target" % chamber_v, abs(chamber_v - CHAMBER_V) <= 0.03 * CHAMBER_V),
    ("barrel longer than the chamber", z_sh + BARREL_LEN >= z_fp_end + 20),
    ("muzzle clamp: screw holes %.1f mm off the bore, %.1f off the rod hole" % cl_walls, min(cl_walls) >= 1.0),
    ("muzzle clamp valid single solid, closed one round bore clear of the bare barrel (tape in between), clear of the rods and the nuts",
     all(G.single_solid(h) for h in _halves) and G.no_overlap(_halves[0], _halves[1])
     and abs(_halves[0].Volume - _halves[1].Volume) < 1e-3 * _halves[0].Volume
     and all(G.no_overlap(h, cl_bare) for h in _closed) and G.no_overlap(_closed[0], _closed[1])
     and (G.no_overlap(muzzle_clamp, hardware) if MUZZLE_CLAMP else True)),
    ("muzzle clamp holds >= 3 x the seat ring's push (%.0f N vs %.0f N at %.0f bar; 2 x M3 a seam at %.0f N, mu %.1f)"
     % (cl_hold, F_ring, P_MAX_BAR, CLAMP_SCREW_T, CLAMP_MU), cl_hold >= 3 * F_ring),
    ("muzzle clamp squeezes the barrel at %.1f MPa: hoop %.0f MPa << yield, under the long-tube collapse %.1f MPa"
     % (cl_p, cl_hoop, 2 * 200e3 / 0.91 * (BARREL_WALL / BARREL_OD) ** 3),
     cl_hoop <= 60 and cl_p <= 0.5 * 2 * 200e3 / 0.91 * (BARREL_WALL / BARREL_OD) ** 3),
    ("muzzle clamp: on the barrel%s, >= %.1f mm off its neighbours' in a hex pack (%.1f)"
     % (" (runs %.0f mm past it)" % (BARREL_LEN - CLAMP_AT) if BARREL_LEN > CLAMP_AT else "", PACK_CLEAR, clamp_gap),
     CLAMP_AT <= BARREL_LEN and z_c0 >= z_fy1 + WASHER_T + NUT_T + 2.0 and clamp_gap >= PACK_CLEAR),
    ("muzzle sleeve valid single solid, clear of the barrel, the rods and the nuts",
     G.single_solid(muzzle_sleeve) and G.no_overlap(muzzle_sleeve, barrel) and G.no_overlap(muzzle_sleeve, hardware_ring)),
    ("muzzle sleeve: ball %.1f mm off its bore, %.0f mm ahead of the barrel <= safe %.0f (socket %.0f mrad, exit %.0f mrad)"
     % (sl_gap, SLEEVE_LEN, sl_safe, sl_tilt, BALL_EXIT_MRAD), sl_gap >= 3.0 and SLEEVE_LEN <= sl_safe),
    ("muzzle sleeve: vents %.0f mm2 >= the bore %.0f" % (sl_vent_a, area(BARREL_ID)), sl_vent_a >= area(BARREL_ID)),
    ("muzzle sleeve prints standing, %.0f mm on a %.0f bed" % (z_sl1 - z_sl0, BED_H), z_sl1 - z_sl0 <= BED_H - 6),
    ("muzzle sleeve clear of the front yoke's nuts, Ø%.0f in a pack at pitch %.0f" % (SLEEVE_OD, PACK_PITCH),
     z_m0 - _skirt_h >= z_fy1 + WASHER_T + NUT_T + 2.0 and SLEEVE_OD <= PACK_PITCH - 4.0),
    ("plugs no wider than the chamber tube (the O-ring cone goes over them)",
     max(rp.BoundBox.XMax, fp.BoundBox.XMax) <= CH_OD / 2 + 1e-6),
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
    "  diaphragm              : Ø%.1f x %.1f, free Ø%.1f, squeeze %.0f %% (stop lip), %.0f %% under the bead,"
    " stretch %.0f %% at full lift"
    % (2 * DIA_R, DIA_T, 2 * MOUTH_R, DIA_SQUEEZE * 100, (DIA_T - t_c + BEAD_H) / DIA_T * 100, dia_strain * 100),
    "  diaphragm              : a plain disc, one bleed Ø%.1f at R%.1f (any angle); the stop lip centres it"
    % (BLEED_D, BLEED_R),
    "  opens when pilot < %.0f %% of chamber pressure (gauge)" % (open_ratio * 100),
    "  pilot volume           : %.1f cm3, G1/8 axial in the rear plug" % pocket_v,
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  chamber                : %.0f cm3, tube %.0f x %.1f aluminium, %.0f mm long, %.0f g"
    % (chamber_v, CH_OD, CH_WALL, chamber_len, (area(CH_OD) - area(CH_ID)) * chamber_len * 2.70e-3),
    "  module                 : Ø%.0f (ears %.0f across), %.0f mm long with a %.0f mm barrel, yoke to the muzzle %s"
    % (CH_OD, 2 * (TIE_R + EAR_R), max(z_front, z_sh + BARREL_LEN) - z_ry, BARREL_LEN,
       "clamp" if MUZZLE_CLAMP else "ring"),
    "  @ %.0f bar               : rear plug %.0f N back, front plug %.0f N forward, both on the rods; pilot pushes the"
    " seat ring %.0f N forward at %.0f bar (%.0f at %.0f), seat ring -> barrel -> muzzle %s -> rods"
    % (P_MAX_BAR, F_rp, P_MAX_BAR * 0.1 * A_annulus, F_open, P_WORK_BAR, F_ring, P_MAX_BAR,
       "clamp" if MUZZLE_CLAMP else "ring"),
    "  tie rods               : 2 x M3 threaded rod %.0f mm at R%.1f, %.0f / %.0f deg; 6 nuts, 6 washers Ø%.0f;"
    " no glue, nothing screwed into the barrel or drilled through the tube" % (tie_len, TIE_R, *TIE_ANGLES, WASHER_D),
    "  yokes, muzzle ring     : rear yoke %.0f thick behind the rear plug (hole Ø%.1f for the fitting), front yoke %.0f"
    " on the front plug's flange, muzzle ring %.0f (counterbore %.0f over the barrel's end)"
    % (YOKE_T, FITTING_HOLE_D, YOKE_T, MUZZLE_T, MUZZLE_CB - 0),
    "  muzzle clamp           : collar %.0f long at %.0f from the shoulder, Ø%.1f bore closed over %.1f mm of tape, two"
    " halves split at %.0f / %.0f deg, 4 x M3 x 12 across the seam; holds %.0f N, squeezes %.1f MPa%s"
    % (CLAMP_W, CLAMP_AT, 2 * _cb_r, CLAMP_LINER, _sa, _sa + 180, cl_hold, cl_p,
       ", in the model (default)" if MUZZLE_CLAMP else ", option"),
    "  muzzle sleeve (option) : Ø%.0f, bore Ø%.0f, %.0f mm ahead of the barrel (overall %.0f), socket %.0f over the"
    " barrel, %d vents %.0f x %.0f; %.1f cm3; the muzzle ring's rods, %.0f mm"
    % (SLEEVE_OD, SLEEVE_BORE, SLEEVE_LEN, z_sl1 - z_sl0, SLEEVE_SOCKET, SLEEVE_VENTS[0], SLEEVE_VENTS[1],
       SLEEVE_VENTS[2], muzzle_sleeve.Volume / 1000, tie_len_ring),
    "  pack                   : pitch %.0f unchanged, each rod alone in its gap of a hex pack; %.1f mm to the"
    " neighbours (hex), %.1f (square); the ears stand %.1f mm out of the Ø%.0f on the pack's edge"
    % (PACK_PITCH, pack_gap["hex"], pack_gap["square"], pack_grow, CH_OD),
    "  O-rings                : 2 x %g x %g (chamber tube), 1 x %g x %g (barrel, front plug), 1 x %g x %g (seat ring's"
    " spigot in the barrel's bore)" % (CH_ORING + BR_ORING + SP_ORING),
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
    torus(sp_root_r + SP_ORING[1] / 2, SP_ORING[1], z_spg2 - GROOVE_W * SP_ORING[1] / 2),
    torus(br_root_r - BR_ORING[1] / 2, BR_ORING[1], fp_bgroove_z[1] - GROOVE_W * BR_ORING[1] / 2),
])
fitting = G.push_in_fitting(0, 0, 0)
fitting.rotate(V(0, 0, 0), X, 180)
fitting.translate(V(0, 0, z_rp))
ball = Part.makeSphere(BARREL_ID / 2, V(0, 0, z_sp + math.sqrt((BARREL_ID / 2) ** 2 - (SP_BORE / 2) ** 2)))   # on the spigot's tip

# ---------------------------------------------------------------- document
if not STAGE3V4_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Rear_plug", rp, "stator"), ("Seat_ring", sr, "rotor"), ("Diaphragm", diaphragm, "shoe"),
                        ("Front_plug", fp, "stator"), ("Rear_yoke", rear_yoke, "stator"),
                        ("Front_yoke", front_yoke, "stator"),
                        ("Muzzle_ring", muzzle_clamp if MUZZLE_CLAMP else muzzle_ring, "stator")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_tube", barrel, "ghost"), ("Chamber_tube", chamber, "ghost"),
                        ("ORings", orings, "oring"), ("Pilot_fitting", fitting, "steel"), ("Ball", ball, "flow"),
                        ("Tie_rods", hardware, "steel")):
        sc.add("Bought", n, s, style)
    half = Part.makeBox(100, 50, 1200, V(-50, -50, -600))
    for n in ("Rear_plug", "Seat_ring", "Diaphragm", "Front_plug", "Barrel_tube", "Chamber_tube", "ORings", "Ball",
              "Pilot_fitting", "Rear_yoke", "Front_yoke", "Muzzle_ring", "Tie_rods"):
        style = dict(Rear_plug="stator", Seat_ring="rotor", Diaphragm="shoe", Front_plug="stator", ORings="oring",
                     Ball="flow", Pilot_fitting="steel", Rear_yoke="stator", Front_yoke="stator", Muzzle_ring="stator",
                     Tie_rods="steel").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("СТВОЛ 25x0,6, %.0f мм" % BARREL_LEN, (-40, 0, z_sh + BARREL_LEN * 0.8)),
        ("КАМЕРА: труба %.0fx%.1f, %.0f мм, %.0f см3" % (CH_OD, CH_WALL, chamber_len, chamber_v), (40, 0, z_tf * 0.5)),
        ("ПЕРЕДНЯЯ ПРОБКА", (40, 0, z_tf + 5)),
        ("КОЛЬЦО СЕДЛА: седло Ø%.0f" % SEAT_D, (40, 0, 10)),
        ("МЕМБРАНА Ø%.1f" % (2 * DIA_R), (40, 0, 0)),
        ("ЗАДНЯЯ ПРОБКА: пилот G1/8 -> M3R110 A", (40, 0, z_rp)),
        ("ЯРМО + 2 шпильки M3 x %.0f" % tie_len, (40, 0, z_ry - 5)),
        ("ДУЛЬНЫЙ ХОМУТ: 2 половинки, 4 x M3 x 12 поверх изоленты" if MUZZLE_CLAMP else "ДУЛЬНОЕ КОЛЬЦО",
         (40, 0, max(z_front, z_m1) + 5)),
    ]:
        sc.label("Labels", text, pos)
    sc.add("Sleeve_option", "Muzzle_sleeve", muzzle_sleeve, "stator")
    if MUZZLE_CLAMP:
        sc.add("Bought", "Clamp_liner", cl_liner, "shoe")
    else:
        sc.add("Clamp_option", "Muzzle_clamp", muzzle_clamp, "stator")
        sc.add("Clamp_option", "Clamp_liner", cl_liner, "shoe")
    sc.label("Labels", "ДУЛЬНАЯ НАСАДКА (вместо кольца, скрыта)", (40, 0, z_sl1))
    sc.add("Jig", "Jig_guide", jig_guide, "stator", offset=V(-3 * CH_OD, 0, z_rp))
    sc.label("Labels", "ШАБЛОН для сверления мембраны", (-3 * CH_OD, 0, z_rp + 15))
    sc.finish(hidden_groups=("Section", "Sleeve_option", "Clamp_option"), opaque_groups=("Section",))
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
                       ("diaphragm", diaphragm_free, False), ("jig_guide", jig_guide, False), ("rear_yoke", rear_yoke, False), ("front_yoke", front_yoke, True),
                       ("muzzle_ring", muzzle_ring, True), ("muzzle_sleeve", muzzle_sleeve, False),
                       ("muzzle_clamp_half", muzzle_clamp_half, True),
                       ("oring_cone", oring_cone, True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
