# -*- coding: utf-8 -*-
"""
Ratling Stage 3: barrel module with a printed diaphragm quick-exhaust valve.

One barrel of the mitrailleuse. Chamber and barrel are cut from the 25 mm
metal tube and run side by side, both pointing forward, out of one printed
body; the valve sits behind the barrel axis:

    chamber tube ──> chamber spigot ──> window ──> gallery (around the seat)
                                                     │  diaphragm lifts into
                                                     ▼  the cap pocket
    barrel tube  <── barrel breech ║ flat face <── seat (Ø SEAT_D, on the barrel axis)

v1.1: the barrel meets the valve at a flat face, as it would in a six-barrel
pistol with one valve and a turning barrel block. The breech piece carries
an O-ring on its face and is held by three M3 screws; washers on them set a
gap to see what a turning block would cost.

    pilot (cap pocket) pressurized: the diaphragm sits on the seat and the
    chamber charges from the pilot through a bleed hole in the diaphragm.
    pilot vented: chamber pressure on the annulus outside the seat lifts the
    diaphragm into the pocket, and the chamber dumps straight into the barrel.

Parts, each exported in its print orientation (lowest point at z = 0):

    body ........ clamp face on the bed, chamber spigot up. The seat land and
                  the clamp face are the bed face (flat). Gallery ceiling is
                  a 45 deg cone; short radial ribs at the clamp plane carry
                  the diaphragm while the pilot is up and the chamber empty.
                  M4 nut pockets in the top face, between the tubes: the rods
                  are turned from the cap side, which is clear; a rubber
                  washer under each nut seals its rod hole. Flat valve face
                  round the seat bore on top, with three M3 pilots for the
                  barrel breech. 45 deg fillet at the chamber spigot root
                  (the first, 15 %-infill body broke there).
    cap ......... clamp face up: recess that locates the diaphragm and sets
                  its squeeze, pocket (= lift), radial grooves in the pocket
                  floor, G1/8 pilot port from the bed side, M4 rod heads
                  on rubber washers on its back face.
    barrel breech face (O-ring groove) on the bed, spigot up into the barrel;
                  flange cut flat on the chamber tube's side.
    tube clip ... ties the chamber tube to the barrel near the chamber plug,
                  with an ear to clamp to the bench: the chamber tube must not
                  hang on its spigot.
    diaphragm ... Ø DIA_D disc cut from rubber sheet (NBR/EPDM, ~60 A); the
                  STL is for a TPU try or as a cutting template. Bleed hole
                  Ø BLEED_D at BLEED_R, pierced/drilled after cutting.
    chamber plug  blind, closes the chamber's far end; flange on the bed, the
                  same gland and screws as the body spigots. Once charged the
                  chamber is at supply pressure, so the compressor gauge
                  reads it; no port here.

Spigot glands are connectors/tube_plug_v1's, proven fit.
4 x M4 tie rods carry the cap load, so the printed layers stay in
compression. Print PETG, 100 % infill; water-test to 1.5-2 x P_MAX before air.

Bench hookup with the AirTAC M3R110 (inverted): supply -> R, A -> cap pilot
port, P open. At rest R->A pressurizes the pilot; pressing the roller vents
it (A->P) and the module fires.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_qev.py').read())
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
    STAGE3_LIBRARY
except NameError:
    STAGE3_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

# ---------------------------------------------------------------- parameters
P_WORK_BAR = 2.0
P_MAX_BAR = 5.0         # parts rated for this; relief valve set below it

TUBE_ID = 23.8          # measured
TUBE_WALL = 0.59
TUBE_OD = TUBE_ID + 2 * TUBE_WALL
TUBE_GAP = 2.0          # chamber tube to barrel tube, side by side
BARREL_LEN = 300.0      # first cut; shortened on the bench

# Spigot gland = connectors/tube_plug_v1 (fit confirmed in PLA).
RADIAL_CLEAR = 0.20
ORING_ID = 11 / 16 * 25.4
ORING_CS = 1 / 8 * 25.4
ORING_SQUEEZE = 0.12
GROOVE_ROOT_W = 1.1 * ORING_CS
GROOVE_WALL_FROM_TIP = 9.0
LEAD_CHAMFER = 1.0
BARREL_SPIGOT_LEN = 24.0    # short: its bore is dead volume behind the ball
CHAMBER_SPIGOT_LEN = 30.0
SCREW_N = 3
SCREW_PILOT_D = 2.5     # ST2.9 self-tapping, through the tube wall
SCREW_DEPTH = 3.8
SCREW_L = 4.5           # ST2.9 x 4.5 pan head: longer ones reach the bore
SCREW_FROM_TUBE_END = 8.0

# Flow path: one diameter from chamber to barrel.
SEAT_D = 13.0           # seat bore = spigot bores
SEAT_LAND = 2.0         # seat lip width (seat tube wall)
GALLERY_R = 18.0        # gallery and pocket radius at the clamp plane
MOUTH_CHAMFER = 1.0     # 45 deg, both mouths; free diaphragm Ø = 2 * (GALLERY_R + MOUTH_CHAMFER)
GALLERY_H = 14.0        # straight part; 45 deg cone above it
WINDOW_Z0 = 3.0         # chamber bore floor
RIB_N = 8               # at half steps of the 90 deg rod pattern: the bleed hole,
                        # on the cap mark, clears them however the cap is turned
RIB_W = 1.5
RIB_H = 3.0

BODY_R = 31.0
BODY_H = 27.0

# Diaphragm and cap
DIA_D = 46.0
DIA_T = 1.5
DIA_SQUEEZE = 0.20
RECESS_CLEAR = 0.25     # radial, diaphragm in the cap recess
# Sealing bead on the recess floor: flat on flat, the 0.3 mm squeeze was lost to
# the printed top face and the sheet's tolerance, and the clamp seam leaked.
BEAD_R = 21.0           # mid clamped strip (free edge Ø38 .. disc Ø46)
BEAD_W = (1.2, 0.4)     # base, top
BEAD_H = 0.4            # two layers; adds to DIA_SQUEEZE under the bead
LIFT = 4.0              # pocket depth below the diaphragm
GROOVE_N = 4            # pocket floor grooves, so the diaphragm cannot seal the port
GROOVE_W = 2.0
GROOVE_DEPTH = 1.0
GROOVE_LEN = 15.0
BLEED_D = 1.0           # was 0.8: faster recharge between shots; the pilot still dumps far faster
BLEED_R = 13.0
BLEED_ANGLE = 0.0       # cap mark; any multiple of 90 deg works
MARK_W = 4.0            # V notch on the cap's clamp face, outside the diaphragm
MARK_DEPTH = 0.6

# Cutting jig: rubber square in the base pocket, ring on top guides the knife
# round Ø DIA_D into a groove in the base; the puck holds the disc down and
# guides the needle for the bleed hole into a relief ring in the base.
JIG_BLANK = 48.0        # rough-cut rubber square
JIG_POCKET_CLEAR = 0.3  # per side
JIG_WALL = 4.0
JIG_FLOOR = 4.0
JIG_POCKET_DEPTH = 3.0
JIG_RING_T = 6.0
JIG_BLADE_GROOVE_W = 1.2
JIG_BLADE_GROOVE_DEPTH = 1.5
JIG_RELIEF_W = 3.5      # covers the puck's play
JIG_RELIEF_DEPTH = 2.0
JIG_PUCK_CLEAR = 1.0    # radial, puck in the ring's hole
JIG_PUCK_T = 6.0
JIG_KNOB_D = 16.0
JIG_KNOB_H = 15.0
JIG_GUIDE_D = 1.0       # for a 0.8 drill or a needle
JIG_NOTCH_W = 12.0      # finger notches to lift the ring out
CAP_T = 16.0
TAP_DRILL_D = 8.8       # G1/8, pilot port from the bed side
TAP_DEPTH = 8.0
PILOT_D = 4.0

ROD_N = 4
ROD_R = 26.5
ROD_ANGLE0 = 45.0
ROD_HOLE_D = 4.4        # M4
NUT_AF = 7.0
NUT_POCKET_CLEAR = 0.2
NUT_POCKET_DEPTH = 3.5 + 1.1    # nut on a 1.5 mm rubber washer (Ø7, fits the hex) that seals the rod hole
ROD_HEAD_D = 7.0        # M4 socket head
ROD_HEAD_H = 4.0
NUT_T = 3.2
WASHERS_UNDER_HEAD = 2.3        # rubber 1.5 + steel 0.8 under each rod head on the cap

# Barrel breech (v1.1): flat valve face on the body top, O-ring on the breech face
BREECH_FLANGE_D = 46.0
BREECH_FLANGE_T = 5.0
BREECH_FLAT_X = 14.0            # flange cut flat here, clear of the chamber tube (its edge at 14.5)
BREECH_BOLT_R = 20.0
BREECH_BOLT_ANGLES = (90.0, 180.0, 270.0)
BREECH_BOLT_HOLE = 3.4
BREECH_PILOT_D, BREECH_PILOT_DEPTH = 2.6, 10.0  # M3 x 14 self-tapping into the body
FACE_SQUEEZE = 0.20             # O-ring on the breech face, flanges touching
FACE_GROOVE_W = 1.2             # x CS
SPIGOT_ROOT_FILLET = 0.8        # 45 deg at the chamber spigot root; deburr the tube's inner edge to match

# Tube clip: rings round both tubes near the chamber plug, ear for a bench clamp
CLIP_H = 10.0
CLIP_WALL = 2.5
CLIP_CLEAR = 0.3
CLIP_EAR = (14.0, 4.4)          # ear length beyond the rings, M4 hole
CLIP_FROM_PLUG = 20.0           # clip's centre ahead of the chamber plug flange

CHAMBER_V = 100.0       # cm3, target
PLUG_INSERT_LEN = 30.0  # chamber plug, inside the tube
PLUG_FLANGE_T = 5.0
PLUG_FLANGE_D = TUBE_OD + 2.0   # stays clear of the barrel tube beside it

# v1.3 switches (defaults = v1.1 as built): no screws through the tubes, a yoke on the chamber plug
# held by two long rods, a bigger seat on a thinner O-ring. See PRESET_V13 in the docstring.
TUBE_SCREWS = True
PLUG_YOKE = False
FACE_ORING_ID = None        # None: same ring as the spigots
FACE_ORING_CS = None
GROOVE_WALL_MIN = 2.0       # groove root -> bore
FACE_WALL_MIN = 1.5         # face groove -> bore
# Central tie rod (for the pistol, where nothing can run beside the tube): an M3 threaded rod down the chamber
# tube's axis, a nut on a rubber washer under the body's floor (in a pocket in the cap's clamp face), a nut on a
# rubber and a steel washer on the plug's outer face. The tube then only seals.
PLUG_ROD = False
ROD3_HOLE = 3.4
ROD3_NUT_AF, ROD3_NUT_T = 5.5, 2.4
ROD3_RUBBER, ROD3_STEEL = 0.8, 0.5
YOKE_T = 8.0
YOKE_EAR_R = 5.5
YOKE_NUT_T = 3.2

# Variants: set OVERRIDE = {"SEAT_D": 15.0, "NAME": "stage3_qev_d15", ...} before exec to replace any
# parameter above (those derived from it below follow).
OUT_DIR = os.path.join(REPO, "exports", "stage3_qev")
NAME = "stage3_qev"
try:
    globals().update(OVERRIDE)
except NameError:
    pass
if NAME != "stage3_qev":
    OUT_DIR = os.path.join(REPO, "exports", NAME)
TUBE_OD = TUBE_ID + 2 * TUBE_WALL          # re-derived: the override may have changed their inputs
GROOVE_ROOT_W = 1.1 * ORING_CS
PLUG_FLANGE_D = TUBE_OD + 2.0
if FACE_ORING_ID is None:
    FACE_ORING_ID, FACE_ORING_CS = ORING_ID, ORING_CS

# ---------------------------------------------------------------- derived
seat_r = SEAT_D / 2
seat_out_r = seat_r + SEAT_LAND
mouth_r = GALLERY_R + MOUTH_CHAMFER
cone_top = GALLERY_H + (GALLERY_R - seat_out_r)
chamber_x = TUBE_OD + TUBE_GAP
spigot_r = TUBE_ID / 2 - RADIAL_CLEAR
groove_depth = ORING_CS * (1 - ORING_SQUEEZE)
root_r = TUBE_ID / 2 - groove_depth
dia_t_clamped = DIA_T * (1 - DIA_SQUEEZE)
recess_r = DIA_D / 2 + RECESS_CLEAR
z_recess = CAP_T - dia_t_clamped
z_floor = z_recess - LIFT
tap_roof = TAP_DEPTH + (TAP_DRILL_D - PILOT_D) / 2
window_top = GALLERY_H + seat_r     # gable apex

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)


def V(x, y, z=0.0):
    return App.Vector(x, y, z)


def revolve(rz, at=V(0, 0)):
    """Solid of revolution about the vertical axis through `at`; rz = [(r, z)]."""
    pts = [V(at.x + r, at.y, z) for r, z in rz]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    s = face.revolve(at, Z, 360)
    return Part.Solid(s) if s.ShapeType != "Solid" else s


def prism(xy, z0, z1):
    pts = [V(x, y, z0) for x, y in xy]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, z1 - z0))


def cyl(r, z0, z1, at=V(0, 0)):
    return Part.makeCylinder(r, z1 - z0, V(at.x, at.y, z0))


def spigot(z0, length, at):
    """Tube plug gland: body, trapezoid O-ring groove, lead chamfer."""
    tip = z0 + length
    g0 = tip - GROOVE_WALL_FROM_TIP
    g1 = g0 + GROOVE_ROOT_W
    g2 = g1 + (spigot_r - root_r)
    return revolve([(0, z0 - 0.5), (spigot_r, z0 - 0.5), (spigot_r, g0), (root_r, g0),
                    (root_r, g1), (spigot_r, g2), (spigot_r, tip - LEAD_CHAMFER),
                    (spigot_r - LEAD_CHAMFER, tip), (0, tip)], at), g0, g2


def screw_pilots(at, z, angles):
    out = []
    if not TUBE_SCREWS:
        return out
    for a in angles:
        d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        start = V(at.x + d.x * (spigot_r + 1), at.y + d.y * (spigot_r + 1), z)
        out.append(Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_DEPTH + 1, start, -d))
    return out


rod_pts = [V(ROD_R * math.cos(math.radians(ROD_ANGLE0 + 360.0 * i / ROD_N)),
             ROD_R * math.sin(math.radians(ROD_ANGLE0 + 360.0 * i / ROD_N))) for i in range(ROD_N)]
barrel_screw_angles = (120.0, 180.0, 240.0)    # away from the chamber tube, reachable
chamber_screw_angles = (-60.0, 0.0, 60.0)
C = V(chamber_x, 0)

# ---------------------------------------------------------------- body
# outline: hull of the valve disc and the chamber tube's stop face
r2 = TUBE_OD / 2 + 1.5
phi = math.acos((BODY_R - r2) / chamber_x)
hull = prism([(BODY_R * math.cos(phi), BODY_R * math.sin(phi)),
              (chamber_x + r2 * math.cos(phi), r2 * math.sin(phi)),
              (chamber_x + r2 * math.cos(phi), -r2 * math.sin(phi)),
              (BODY_R * math.cos(phi), -BODY_R * math.sin(phi))], 0, BODY_H)
body = cyl(BODY_R, 0, BODY_H).fuse(cyl(r2, 0, BODY_H, C)).fuse(hull)

chamber_spigot, cg0, cg2 = spigot(BODY_H, CHAMBER_SPIGOT_LEN, C)
root_fillet = revolve([(spigot_r - 0.01, BODY_H - 0.01), (spigot_r + SPIGOT_ROOT_FILLET, BODY_H - 0.01),
                       (spigot_r - 0.01, BODY_H + SPIGOT_ROOT_FILLET)], C)
body = body.fuse(chamber_spigot).fuse(root_fillet)

gallery = revolve([(seat_out_r, -1), (mouth_r + 1, -1), (GALLERY_R, MOUTH_CHAMFER),
                   (GALLERY_R, GALLERY_H), (seat_out_r, cone_top)])
window = Part.makeBox(chamber_x - GALLERY_R + 2, SEAT_D, GALLERY_H - WINDOW_Z0,
                      V(GALLERY_R - 4, -seat_r, WINDOW_Z0))
gable = Part.Face(Part.makePolygon([V(GALLERY_R - 4, -seat_r, GALLERY_H), V(GALLERY_R - 4, seat_r, GALLERY_H),
                                    V(GALLERY_R - 4, 0, window_top), V(GALLERY_R - 4, -seat_r, GALLERY_H)])
                  ).extrude(V(chamber_x - GALLERY_R + 2, 0, 0))
cuts = [gallery, window, gable,
        cyl(seat_r, -1, BODY_H + 1),
        cyl(seat_r, WINDOW_Z0, BODY_H + CHAMBER_SPIGOT_LEN + 1, C)]
hex_r = (NUT_AF + 2 * NUT_POCKET_CLEAR) / math.sqrt(3)
nut_pockets = [prism([(p.x + hex_r * math.cos(math.radians(60 * k)), p.y + hex_r * math.sin(math.radians(60 * k)))
                      for k in range(6)], BODY_H - NUT_POCKET_DEPTH, BODY_H + 1) for p in rod_pts]
cuts += [cyl(ROD_HOLE_D / 2, -1, BODY_H + 1, p) for p in rod_pts] + nut_pockets
cuts += screw_pilots(C, BODY_H + SCREW_FROM_TUBE_END, chamber_screw_angles)
breech_bolts = [V(BREECH_BOLT_R * math.cos(math.radians(a)), BREECH_BOLT_R * math.sin(math.radians(a)))
                for a in BREECH_BOLT_ANGLES]
cuts += [cyl(BREECH_PILOT_D / 2, BODY_H - BREECH_PILOT_DEPTH, BODY_H + 1, p) for p in breech_bolts]
if PLUG_ROD:
    cuts.append(cyl(ROD3_HOLE / 2, -1, WINDOW_Z0 + 1, C))
for c in cuts:
    body = body.cut(c)

ribs = []
for i in range(RIB_N):
    a = math.radians(360.0 / RIB_N * (i + 0.5))          # none at the bleed / cap mark angles
    rib = Part.makeBox(GALLERY_R - seat_out_r + 1.0, RIB_W, RIB_H, V(seat_out_r - 0.5, -RIB_W / 2, 0))
    rib.rotate(V(0, 0), Z, math.degrees(a))
    ribs.append(rib)
for rib in ribs:
    body = body.fuse(rib)
body = body.removeSplitter()

# ---------------------------------------------------------------- cap
cap = cyl(BODY_R, 0, CAP_T)
pocket = revolve([(0, z_floor), (GALLERY_R, z_floor), (GALLERY_R, z_recess - MOUTH_CHAMFER),
                  (mouth_r, z_recess), (mouth_r, z_recess + 0.5), (0, z_recess + 0.5)])
cuts = [cyl(recess_r, z_recess, CAP_T + 1), pocket,
        cyl(PILOT_D / 2, -1, z_floor + 0.5),
        cyl(TAP_DRILL_D / 2, -1, TAP_DEPTH),
        Part.makeCone(TAP_DRILL_D / 2, PILOT_D / 2, tap_roof - TAP_DEPTH, V(0, 0, TAP_DEPTH))]
for i in range(GROOVE_N):
    g = Part.makeBox(GROOVE_LEN, GROOVE_W, GROOVE_DEPTH + 0.5, V(0, -GROOVE_W / 2, z_floor - GROOVE_DEPTH))
    g.rotate(V(0, 0), Z, 360.0 / GROOVE_N * i)
    cuts.append(g)
for p in rod_pts:
    cuts.append(cyl(ROD_HOLE_D / 2, -1, CAP_T + 1, p))
hex3_r = (ROD3_NUT_AF + 0.4) / math.sqrt(3)
nut3_depth = ROD3_NUT_T + ROD3_RUBBER + 0.3
if PLUG_ROD:           # flats facing along x (the cap's edge side), corners along y
    cuts.append(prism([(C.x + hex3_r * math.cos(math.radians(30 + 60 * k)), C.y + hex3_r * math.sin(math.radians(30 + 60 * k)))
                       for k in range(6)], CAP_T - nut3_depth, CAP_T + 1))
mark = prism([(recess_r + 0.8, 0), (BODY_R + 1, MARK_W / 2), (BODY_R + 1, -MARK_W / 2)],
             CAP_T - MARK_DEPTH, CAP_T + 1)
mark.rotate(V(0, 0), Z, BLEED_ANGLE)
cuts.append(mark)
for c in cuts:
    cap = cap.cut(c)
bead = revolve([(BEAD_R - BEAD_W[0] / 2, z_recess - 0.01), (BEAD_R + BEAD_W[0] / 2, z_recess - 0.01),
                (BEAD_R + BEAD_W[1] / 2, z_recess + BEAD_H), (BEAD_R - BEAD_W[1] / 2, z_recess + BEAD_H)])
cap_flat = cap.removeSplitter()          # for the stack check: the bead is meant to sink into the rubber
cap = cap.fuse(bead).removeSplitter()

# ---------------------------------------------------------------- chamber plug (print frame)
plug_print = revolve([(0, 0), (PLUG_FLANGE_D / 2 - 0.5, 0), (PLUG_FLANGE_D / 2, 0.5),
                      (PLUG_FLANGE_D / 2, PLUG_FLANGE_T), (0, PLUG_FLANGE_T)])
plug_spigot, pg0, _ = spigot(PLUG_FLANGE_T, PLUG_INSERT_LEN, V(0, 0))
plug_print = plug_print.fuse(plug_spigot)
for c in screw_pilots(V(0, 0), PLUG_FLANGE_T + SCREW_FROM_TUBE_END, chamber_screw_angles):
    plug_print = plug_print.cut(c)
if PLUG_ROD:
    plug_print = plug_print.cut(cyl(ROD3_HOLE / 2, -1, PLUG_FLANGE_T + PLUG_INSERT_LEN + 1))
plug_print = plug_print.removeSplitter()

# ---------------------------------------------------------------- barrel breech (print frame: face at z = 0)
face_groove_depth = FACE_ORING_CS * (1 - FACE_SQUEEZE)
face_groove_out = FACE_ORING_ID / 2 + FACE_ORING_CS        # pressure inside: the ring bears on the outer wall
face_groove_in = face_groove_out - FACE_GROOVE_W * FACE_ORING_CS
breech = cyl(BREECH_FLANGE_D / 2, 0, BREECH_FLANGE_T).common(
    Part.makeBox(BREECH_FLAT_X + BREECH_FLANGE_D / 2, BREECH_FLANGE_D, BREECH_FLANGE_T + 1,
                 V(-BREECH_FLANGE_D / 2, -BREECH_FLANGE_D / 2, -0.5)))
breech_spigot, bg0, bg2 = spigot(BREECH_FLANGE_T, BARREL_SPIGOT_LEN, V(0, 0))
breech = breech.fuse(breech_spigot)
cuts = [cyl(seat_r, -1, BREECH_FLANGE_T + BARREL_SPIGOT_LEN + 1),
        cyl(face_groove_out, -1, face_groove_depth).cut(cyl(face_groove_in, -2, face_groove_depth + 1))]
cuts += [cyl(BREECH_BOLT_HOLE / 2, -1, BREECH_FLANGE_T + 1, p) for p in breech_bolts]
cuts += screw_pilots(V(0, 0), BREECH_FLANGE_T + SCREW_FROM_TUBE_END, barrel_screw_angles)
for c in cuts:
    breech = breech.cut(c)
breech = breech.removeSplitter()

# ---------------------------------------------------------------- tube clip (print frame)
clip_r = TUBE_OD / 2 + CLIP_CLEAR
clip = cyl(clip_r + CLIP_WALL, 0, CLIP_H).fuse(cyl(clip_r + CLIP_WALL, 0, CLIP_H, C)).fuse(
    Part.makeBox(chamber_x, 2 * (clip_r + CLIP_WALL) - 4, CLIP_H, V(0, -(clip_r + CLIP_WALL) + 2, 0)))
ear_y = clip_r + CLIP_WALL + CLIP_EAR[0] / 2
if not PLUG_YOKE:       # with the yoke rods the ear would hit the rod at 315 deg
    clip = clip.fuse(Part.makeBox(CLIP_EAR[0], CLIP_EAR[0] + 2, CLIP_H, V(chamber_x / 2 - CLIP_EAR[0] / 2, -ear_y - CLIP_EAR[0] / 2, 0)))
clip = clip.cut(cyl(clip_r, -1, CLIP_H + 1)).cut(cyl(clip_r, -1, CLIP_H + 1, C))
if not PLUG_YOKE:
    clip = clip.cut(cyl(CLIP_EAR[1] / 2, -1, CLIP_H + 1, V(chamber_x / 2, -ear_y)))
clip = clip.removeSplitter()

# ---------------------------------------------------------------- plug yoke (print frame: bearing face on the bed)
# Rods 0 and 3 (45 / 315 deg) run on past the body, along the chamber tube, to this plate on the plug's end:
# chamber pressure pushes the plug onto it, the rods pull it back to the cap (the clamp gets that much tighter).
yoke_rods = (0, 3)
yoke_pts = [rod_pts[i] for i in yoke_rods]


def hull2d(pts):
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    def half(seq):
        h = []
        for q in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (q[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (q[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(q)
        return h[:-1]
    return half(pts) + half(pts[::-1])


yoke = None
if PLUG_YOKE:
    ring = lambda c, r: [(c.x + r * math.cos(math.radians(a)), c.y + r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    outline = hull2d(ring(C, PLUG_FLANGE_D / 2) + sum((ring(p, YOKE_EAR_R) for p in yoke_pts), []))
    yoke = prism(outline, 0, YOKE_T)
    for p in yoke_pts:
        yoke = yoke.cut(cyl(ROD_HOLE_D / 2, -1, YOKE_T + 1, p))
    yoke = yoke.removeSplitter()

# ---------------------------------------------------------------- diaphragm
bleed_at = V(BLEED_R * math.cos(math.radians(BLEED_ANGLE)), BLEED_R * math.sin(math.radians(BLEED_ANGLE)))
diaphragm = cyl(DIA_D / 2, 0, DIA_T).cut(cyl(BLEED_D / 2, -1, DIA_T + 1, bleed_at))

# ---------------------------------------------------------------- diaphragm cutting jig (print frame)
jig_pocket = JIG_BLANK + 2 * JIG_POCKET_CLEAR
jig_side = jig_pocket + 2 * JIG_WALL
jig_h = JIG_FLOOR + JIG_POCKET_DEPTH
sq = lambda a: [(-a / 2, -a / 2), (a / 2, -a / 2), (a / 2, a / 2), (-a / 2, a / 2)]
ring_side = jig_pocket - 2 * 0.2
jig_base = prism(sq(jig_side), 0, jig_h).cut(prism(sq(jig_pocket), JIG_FLOOR, jig_h + 1))
for r, w, depth in ((DIA_D / 2, JIG_BLADE_GROOVE_W, JIG_BLADE_GROOVE_DEPTH),
                    (BLEED_R, JIG_RELIEF_W, JIG_RELIEF_DEPTH)):
    jig_base = jig_base.cut(cyl(r + w / 2, JIG_FLOOR - depth, JIG_FLOOR + 1).cut(
        cyl(r - w / 2, JIG_FLOOR - depth - 1, JIG_FLOOR + 2)))
for a in (0, 180):
    n = Part.makeBox(JIG_WALL + 2, JIG_NOTCH_W, JIG_POCKET_DEPTH + 1,
                     V(jig_pocket / 2 - 1, -JIG_NOTCH_W / 2, JIG_FLOOR))
    n.rotate(V(0, 0), Z, a)
    jig_base = jig_base.cut(n)
jig_base = jig_base.removeSplitter()
jig_ring = prism(sq(ring_side), 0, JIG_RING_T).cut(cyl(DIA_D / 2, -1, JIG_RING_T + 1)).removeSplitter()
puck_r = DIA_D / 2 - JIG_PUCK_CLEAR
jig_puck = cyl(puck_r, 0, JIG_PUCK_T).fuse(cyl(JIG_KNOB_D / 2, JIG_PUCK_T - 0.5, JIG_PUCK_T + JIG_KNOB_H))
jig_puck = jig_puck.cut(cyl(JIG_GUIDE_D / 2, -1, JIG_PUCK_T + 1, V(BLEED_R, 0))).removeSplitter()

# ---------------------------------------------------------------- assembly (body frame)
area = lambda d: math.pi * d * d / 4
A_seat = area(SEAT_D)
chamber_extra_v = (A_seat * (BODY_H + CHAMBER_SPIGOT_LEN - WINDOW_Z0)) / 1000 \
    + (area(2 * GALLERY_R) - A_seat) * GALLERY_H / 1000
chamber_tube_len = (CHAMBER_V - chamber_extra_v) * 1000 / area(TUBE_ID) + CHAMBER_SPIGOT_LEN + PLUG_INSERT_LEN
rod_len = 5 * math.ceil((WASHERS_UNDER_HEAD + CAP_T + BODY_H - NUT_POCKET_DEPTH + 1.1 + NUT_T + 1.0) / 5)

cap_a = cap.copy()
cap_a.translate(V(0, 0, -CAP_T))           # cap top face meets the body bed face
dia_a = cyl(DIA_D / 2, -dia_t_clamped, 0)  # clamped
z_barrel = BODY_H + BREECH_FLANGE_T                  # barrel tube's rear end, on the breech flange
tubes = [cyl(TUBE_OD / 2, z0, z0 + L, at).cut(cyl(TUBE_ID / 2, z0 - 1, z0 + L + 1, at))
         for at, z0, L in ((V(0, 0), z_barrel, BARREL_LEN), (C, BODY_H, chamber_tube_len))]
breech_a = breech.translated(V(0, 0, BODY_H))
tube_end = BODY_H + chamber_tube_len
plug = plug_print.copy()                  # turned tip-down, stop face on the tube end
plug.rotate(V(0, 0), X, 180)
plug.translate(V(C.x, C.y, tube_end + PLUG_FLANGE_T))
clip_a = clip.translated(V(0, 0, tube_end - CLIP_FROM_PLUG - CLIP_H / 2))
yoke_z = tube_end + PLUG_FLANGE_T
yoke_a = yoke.translated(V(0, 0, yoke_z)) if PLUG_YOKE else None
rod3_len = 5 * math.ceil((nut3_depth + tube_end + PLUG_FLANGE_T + ROD3_RUBBER + ROD3_STEEL + ROD3_NUT_T + 2.0) / 5)
yoke_rod_len = 5 * math.ceil((WASHERS_UNDER_HEAD + CAP_T + yoke_z + YOKE_T + 1.1 + YOKE_NUT_T + 1.5) / 5)

# ---------------------------------------------------------------- numbers
A_seat_eff = area(SEAT_D + SEAT_LAND)          # to the middle of the land
A_dia = area(2 * mouth_r)
A_curtain = math.pi * SEAT_D * LIFT
A_window = SEAT_D * (GALLERY_H - WINDOW_Z0) + SEAT_D * seat_r / 2 - (3.0 * (GALLERY_H - WINDOW_Z0) if PLUG_ROD else 0.0)
A_gallery = 2 * (GALLERY_R - seat_out_r) * GALLERY_H
open_ratio = 1 - A_seat_eff / A_dia                # pilot/chamber (gauge) below which it opens
F_cap = P_MAX_BAR * 0.1 * area(2 * mouth_r)
F_spigot = P_MAX_BAR * 0.1 * area(TUBE_ID)
pocket_v = (area(2 * GALLERY_R) * LIFT + area(2 * mouth_r) * dia_t_clamped) / 1000
dead_v = A_seat * (BODY_H + BREECH_FLANGE_T + BARREL_SPIGOT_LEN) / 1000
oring_stretch = 2 * root_r / ORING_ID - 1


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


checks = {
    "body valid single solid": body.isValid() and len(body.Solids) == 1,
    "cap valid single solid": cap.isValid() and len(cap.Solids) == 1,
    "chamber plug valid single solid": plug_print.isValid() and len(plug_print.Solids) == 1,
    "chamber plug/tube no interference": plug.common(tubes[1]).Volume < 1e-3,
    "chamber plug flange clears the barrel tube": chamber_x - PLUG_FLANGE_D / 2 - TUBE_OD / 2 >= 0.5,
    "chamber plug screws outboard of its O-ring":
        not TUBE_SCREWS or PLUG_FLANGE_T + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < pg0 - 1.0,
    "body/tubes no interference (the root fillet meets the tube's deburred edge)":
        all(body.common(t).Volume < root_fillet.common(t).Volume + 1e-3 for t in tubes),
    "breech valid single solid; clear of the body, the chamber tube and the rod tips":
        G.single_solid(breech) and G.no_overlap(breech_a, body) and G.no_overlap(breech_a, tubes[1])
        and ROD_R - 2.0 - BREECH_FLANGE_D / 2 >= 0.5,
    "breech face groove clear of the bore and the bolts":
        face_groove_in - seat_r >= FACE_WALL_MIN and BREECH_BOLT_R - BREECH_BOLT_HOLE / 2 - face_groove_out >= 1.5,
    "breech face O-ring stands >= 0.5 mm proud (gap tests up to 0.3)": FACE_ORING_CS - face_groove_depth >= 0.5 - 1e-9,
    "breech face groove fill <= 85 %":
        (math.pi * FACE_ORING_CS ** 2 / 4) / ((face_groove_out - face_groove_in) * face_groove_depth) <= 0.85,
    "breech bolt pilots clear of the gallery roof (>= 2 mm)":
        BREECH_BOLT_R - BREECH_PILOT_D / 2 - (GALLERY_R - max(0.0, BODY_H - BREECH_PILOT_DEPTH - GALLERY_H)) >= 2.0,
    "breech bolts inside the flange, clear of the flat":
        BREECH_BOLT_R + BREECH_BOLT_HOLE / 2 + 1.0 <= BREECH_FLANGE_D / 2
        and all(p.x + BREECH_BOLT_HOLE / 2 + 1.0 <= BREECH_FLAT_X for p in breech_bolts),
    "yoke: single solid, clear of the barrel tube (>= 0.5), plug flange bears on it":
        not PLUG_YOKE or (G.single_solid(yoke) and all(
            math.hypot(x, y) - TUBE_OD / 2 >= 0.5 for x, y in outline) and G.no_overlap(yoke_a, tubes[0])),
    "yoke rods clear of the breech flange, the barrel tube and the chamber tube":
        not PLUG_YOKE or all(math.hypot(p.x, p.y) - ROD_HOLE_D / 2 - BREECH_FLANGE_D / 2 >= 0.5
                             and dist(C, p) - TUBE_OD / 2 - 2.0 >= 1.0 for p in yoke_pts),
    "central rod: cap nut pocket keeps >= 0.7 mm to the diaphragm recess and to the rim":
        not PLUG_ROD or (C.x - ROD3_NUT_AF / 2 - 0.2 - recess_r >= 0.7 and BODY_R - (C.x + ROD3_NUT_AF / 2 + 0.2) >= 0.7),
    "central rod: nut pocket clear of the cap's mark (turn BLEED_ANGLE away from +x) and rod holes":
        not PLUG_ROD or (all(dist(C, p) - hex3_r - ROD_HOLE_D / 2 >= 1.5 for p in rod_pts)
                         and math.cos(math.radians(BLEED_ANGLE)) < 0.5),
    "tube clip valid single solid, clear of both tubes":
        G.single_solid(clip) and all(G.no_overlap(clip_a, t) for t in tubes),
    "rod reaches through the nut": -CAP_T - WASHERS_UNDER_HEAD + rod_len >= BODY_H - NUT_POCKET_DEPTH + 1.1 + NUT_T,
    "body/cap/diaphragm stack no interference (bead aside)":
        body.common(cap_a).Volume < 1e-3 and body.common(dia_a).Volume < 1e-3
        and cap_flat.translated(V(0, 0, -CAP_T)).common(dia_a).Volume < 1e-3,
    "bead inside the clamped strip, >= 1 mm from both edges":
        BEAD_R - BEAD_W[0] / 2 >= mouth_r + 1.0 and BEAD_R + BEAD_W[0] / 2 <= DIA_D / 2 - 1.0,
    "squeeze under the bead 30..50 %": 0.30 <= (DIA_T - dia_t_clamped + BEAD_H) / DIA_T <= 0.50,
    "seat curtain >= seat area (lift >= SEAT_D/4)": A_curtain >= A_seat,
    "window >= seat area": A_window >= A_seat,
    "gallery (both ways round) >= seat area": A_gallery >= A_seat,
    "opens after the pilot loses <= 25 %": open_ratio >= 0.75,
    "diaphragm clamped >= 3 mm wide": DIA_D / 2 - mouth_r >= 3.0,
    "rods outside the diaphragm": ROD_R - ROD_HOLE_D / 2 > recess_r + 1.0,
    "bleed hole over the gallery, clear of seat and mouth": seat_out_r + 2 < BLEED_R < GALLERY_R - 2,
    "bleed hole clear of the ribs, cap turned any 90 deg":
        min(abs(BLEED_R * math.radians(((BLEED_ANGLE + 90 * k) - 360.0 / RIB_N * (i + 0.5) + 180) % 360 - 180))
            for k in range(4) for i in range(RIB_N)) >= RIB_W / 2 + BLEED_D / 2 + 1.0,
    "cap mark clear of the rod holes":
        min(abs(-p.x * math.sin(math.radians(BLEED_ANGLE)) + p.y * math.cos(math.radians(BLEED_ANGLE)))
            for p in rod_pts) >= ROD_HOLE_D / 2 + MARK_W / 2 + 1.0,
    "jig: puck guide lands on the relief ring, puck turned any way":
        JIG_RELIEF_W / 2 >= JIG_PUCK_CLEAR + JIG_GUIDE_D / 2,
    "jig: blade groove and relief inside the pocket floor":
        DIA_D / 2 + JIG_BLADE_GROOVE_W / 2 < JIG_BLANK / 2 and JIG_RELIEF_DEPTH < JIG_FLOOR - 1,
    "jig: ring clamps >= 1 mm of the blank outside the cut": (JIG_BLANK - DIA_D) / 2 >= 1.0,
    "tap roof below the pocket floor grooves": tap_roof <= z_floor,
    "wall gallery -> rod hole >= 3 mm": ROD_R - ROD_HOLE_D / 2 - mouth_r >= 3.0,
    "wall chamber bore -> rod hole >= 3 mm":
        min(dist(C, p) for p in rod_pts) - seat_r - ROD_HOLE_D / 2 >= 3.0,
    "nut pockets and rod tips clear of both tubes":
        all(G.no_overlap(n, t) for n in nut_pockets for t in tubes)
        and min(dist(C, p) for p in rod_pts) - TUBE_OD / 2 - hex_r >= 1.0
        and ROD_R - TUBE_OD / 2 - hex_r >= 1.0,
    "wall nut pocket -> gallery mouth / chamber bore >= 2 mm":
        ROD_R - hex_r - mouth_r >= 2.0 and min(dist(C, p) for p in rod_pts) - hex_r - seat_r >= 2.0,
    "wall groove root -> bore >= GROOVE_WALL_MIN": root_r - seat_r >= GROOVE_WALL_MIN,
    "screw tip inside its pilot": not TUBE_SCREWS or TUBE_OD / 2 - SCREW_L >= spigot_r - SCREW_DEPTH,
    "wall screw pilot -> bore >= 1.4 mm": not TUBE_SCREWS or spigot_r - SCREW_DEPTH - seat_r >= 1.4 - 1e-9,
    "screws outboard of the O-rings": not TUBE_SCREWS or BODY_H + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < cg0 - 1.0
        and BREECH_FLANGE_T + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < bg0 - 1.0,
    "O-ring stretch 0..6 %": 0 <= oring_stretch <= 0.06,
    "cone roof >= 2 mm under the body top": BODY_H - cone_top >= 2.0,
    "gable stays under the body top": window_top <= BODY_H - 2.0,
}
report = [
    NAME,
    "  flow path              : seat/spigots Ø%.1f (%.0f mm2), curtain %.0f mm2 at lift %.1f, window %.0f, gallery %.0f"
    % (SEAT_D, A_seat, A_curtain, LIFT, A_window, A_gallery),
    "  diaphragm              : Ø%.0f x %.1f, free Ø%.0f, squeeze %.0f %%, bleed Ø%.1f at R%.0f"
    % (DIA_D, DIA_T, 2 * mouth_r, DIA_SQUEEZE * 100, BLEED_D, BLEED_R),
    "  sealing bead           : R%.1f, %.1f high, squeeze under it %.0f %%"
    % (BEAD_R, BEAD_H, (DIA_T - dia_t_clamped + BEAD_H) / DIA_T * 100),
    "  opens when pilot < %.0f %% of chamber pressure (gauge)" % (open_ratio * 100),
    "  pilot volume (pocket)  : %.1f cm3" % pocket_v,
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  chamber %.0f cm3        : tube %.0f mm long (spigot %.0f + plug %.0f inside it; body adds %.1f cm3)"
    % (CHAMBER_V, chamber_tube_len, CHAMBER_SPIGOT_LEN, PLUG_INSERT_LEN, chamber_extra_v),
    "  chamber/barrel axes    : %.1f mm apart" % chamber_x,
    "  @ %.0f bar               : cap %.0f N (%.0f N per M4), chamber tube blow-off %.0f N"
    % (P_MAX_BAR, F_cap, F_cap / ROD_N, F_spigot),
    "  tie rods               : %d x M4 x %d socket head + nut, rubber washer under each head and nut"
    % (ROD_N, rod_len),
    "  barrel breech          : flange Ø%.0f, face O-ring %g x %g (%.2f proud), %d x M3 x 14 into the body"
    % (BREECH_FLANGE_D, FACE_ORING_ID, FACE_ORING_CS, FACE_ORING_CS - face_groove_depth, len(BREECH_BOLT_ANGLES)),
    "  tube retention         : %s" % ("2 long M4 rods x %d to a yoke on the plug, no screws" % yoke_rod_len
                                        if PLUG_YOKE else "one M3 rod x %d down the chamber axis, no screws" % rod3_len
                                        if PLUG_ROD else ("%d x ST2.9 per tube end" % SCREW_N if TUBE_SCREWS else "none")),
    "  body / cap volume      : %.1f / %.1f cm3" % (body.Volume / 1000, cap.Volume / 1000),
]
for k, v in checks.items():
    report.append("  [%s] %s" % ("OK " if v else "FAIL", k))
if not STAGE3_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- references
# Bought parts, for the FreeCAD document only; not exported. Thread overlap
# (screws in their pilots, fitting in its tap) is intended.
SCREW_HEAD_D = 5.6
SCREW_HEAD_H = 2.0
BALL_D = 23.8           # Rival ball, tight in the tube


def flipped(shape, z):
    """Turned upside down (about X) and lifted to z."""
    s = shape.copy()
    s.rotate(V(0, 0), X, 180)
    s.translate(V(0, 0, z))
    return s


def tie_rods():
    rods = []
    for i, p in enumerate(rod_pts):
        long_rod = PLUG_YOKE and i in yoke_rods
        rods += [cyl(ROD_HEAD_D / 2, -CAP_T - ROD_HEAD_H, -CAP_T, p),
                 cyl(2.0, -CAP_T, -CAP_T + (yoke_rod_len if long_rod else rod_len), p),
                 *([G.hex_prism(NUT_AF, yoke_z + YOKE_T, yoke_z + YOKE_T + YOKE_NUT_T, p.x, p.y)] if long_rod else []),
                 G.hex_prism(NUT_AF, BODY_H - NUT_POCKET_DEPTH, BODY_H - NUT_POCKET_DEPTH + NUT_T, p.x, p.y)]
    return G.fuse_all(rods)


def tube_screws():
    out = []
    for at, angles, z in ((V(0, 0), barrel_screw_angles, z_barrel + SCREW_FROM_TUBE_END),
                          (C, chamber_screw_angles, BODY_H + SCREW_FROM_TUBE_END),
                          (C, chamber_screw_angles, tube_end - SCREW_FROM_TUBE_END)):
        for a in angles:
            d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
            o = V(at.x + d.x * TUBE_OD / 2, at.y + d.y * TUBE_OD / 2, z)
            out.append(Part.makeCylinder(1.45, SCREW_L, o, -d))
            out.append(Part.makeCylinder(SCREW_HEAD_D / 2, SCREW_HEAD_H, o, d))
    return G.fuse_all(out)


plug_ring_z = tube_end - (30.0 - GROOVE_WALL_FROM_TIP + GROOVE_ROOT_W / 2)

ring_z = lambda length: BODY_H + length - GROOVE_WALL_FROM_TIP + GROOVE_ROOT_W / 2
orings = G.fuse_all([G.oring(2 * root_r, ORING_CS, ring_z(BREECH_FLANGE_T + BARREL_SPIGOT_LEN)),
                     Part.makeTorus(face_groove_out - FACE_ORING_CS / 2, face_groove_depth / 2,
                                    V(0, 0, BODY_H + face_groove_depth / 2), Z),          # squeezed
                     G.oring(2 * root_r, ORING_CS, ring_z(CHAMBER_SPIGOT_LEN), C.x, C.y),
                     G.oring(2 * root_r, ORING_CS, plug_ring_z, C.x, C.y)])


rod3 = cyl(1.5, -nut3_depth, tube_end + PLUG_FLANGE_T + ROD3_RUBBER + ROD3_STEEL + ROD3_NUT_T + 2.0, C) if PLUG_ROD else None
pilot_fitting = flipped(G.push_in_fitting(0, 0, 0), -CAP_T)
pilot_hose = flipped(G.hose(0, 0, 0, 80), -CAP_T)
ball = Part.makeSphere(BALL_D / 2, V(0, 0, z_barrel + BARREL_SPIGOT_LEN + BALL_D / 2))

# ---------------------------------------------------------------- output
# Skipped when another stage loads this file for its shapes (STAGE3_LIBRARY).
if not STAGE3_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Body", body, "rotor"), ("Cap", cap_a, "stator"), ("Diaphragm", dia_a, "shoe"),
                        ("Chamber_plug", plug, "rotor"), ("Barrel_breech", breech_a, "stator"),
                        ("Tube_clip", clip_a, "rotor"), *([("Plug_yoke", yoke_a, "stator")] if PLUG_YOKE else [])):
        sc.add("Printed", n, s, style)
    bought = [("Barrel_tube", tubes[0], "ghost"), ("Chamber_tube", tubes[1], "ghost"),
              ("Tie_rods", tie_rods(), "steel"),
              *([("Tube_screws", tube_screws(), "steel")] if TUBE_SCREWS else []),
              *([("Central_rod", rod3, "steel")] if PLUG_ROD else []),
              ("ORings", orings, "oring"), ("Pilot_fitting", pilot_fitting, "steel"),
              ("Pilot_hose", pilot_hose, "hose"), ("Ball", ball, "flow")]
    for n, s, style in bought:
        sc.add("Bought", n, s, style)

    half = Part.makeBox(400, 200, 800, V(-200, -200, -100))     # y < 0
    for n in ("Body", "Cap", "Diaphragm", "Chamber_plug", "Barrel_breech", "Barrel_tube", "Chamber_tube", "ORings",
              "Ball", "Pilot_fitting"):
        style = dict(Body="rotor", Chamber_plug="rotor", Cap="stator", Diaphragm="shoe", ORings="oring", Ball="flow",
                     Pilot_fitting="steel", Barrel_breech="stator").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)

    for text, pos in [
        ("СТВОЛ: труба %.0f мм (подрезать)" % BARREL_LEN, (-25, 0, BODY_H + BARREL_LEN)),
        ("КАМЕРА %.0f см3: труба %.0f мм" % (CHAMBER_V, chamber_tube_len), (C.x + 25, 0, tube_end - 40)),
        ("ЗАГЛУШКА камеры (глухая, PETG)", (C.x + 25, 0, tube_end + 10)),
        ("ШАРИК Rival", (-25, 0, z_barrel + BARREL_SPIGOT_LEN + BALL_D)),
        ("КАЗЁННИК: кольцо на торце, 3 x M3x14", (-BREECH_FLANGE_D / 2 - 10, 0, BODY_H + 3)),
        ("ХОМУТ труб: к стенду", (C.x + 25, 0, tube_end - CLIP_FROM_PLUG)),
        ("КОРПУС QEV (PETG 100 %)", (BODY_R + 10, 0, BODY_H / 2)),
        ("МЕМБРАНА 1,5 мм, Ø%.0f" % DIA_D, (-BODY_R - 10, 0, 0)),
        ("КРЫШКА: пилот G1/8 -> M3R110 A", (-BODY_R - 10, 0, -CAP_T / 2)),
        ("ШПИЛЬКИ M4 x %d x4 + гайки" % rod_len, (rod_pts[1].x, rod_pts[1].y, BODY_H + 10)),
        *([("САМОРЕЗЫ ST2.9 x %.1f x9" % SCREW_L, (-TUBE_OD, 0, z_barrel + SCREW_FROM_TUBE_END))] if TUBE_SCREWS else
          [("ЯРМО заглушки: 2 шпильки M4 x %d (45/315°) + гайки" % yoke_rod_len, (C.x + 25, 0, yoke_z + YOKE_T + 10))]
          if PLUG_YOKE else []),
    ]:
        sc.label("Labels", text, pos)
    JIG_AT = V(-BODY_R - jig_side, 0, -CAP_T)           # beside the module, stacked as used
    blank = Part.makeBox(JIG_BLANK, JIG_BLANK, DIA_T, V(-JIG_BLANK / 2, -JIG_BLANK / 2, JIG_FLOOR))
    for n, s, z, style in (("Jig_base", jig_base, 0, "frame"), ("Jig_blank", blank, 0, "shoe"),
                           ("Jig_ring", jig_ring, JIG_FLOOR + DIA_T, "printed"),
                           ("Jig_puck", jig_puck, JIG_FLOOR + DIA_T, "stator")):
        sc.add("Jig", n, s, style, offset=V(JIG_AT.x, JIG_AT.y, JIG_AT.z + z))
    sc.label("Labels", "КОНДУКТОР мембраны: основание, резина, рамка, прижим", (JIG_AT.x, 0, JIG_AT.z + 40))
    sc.finish(hidden_groups=("Section",), opaque_groups=("Section",))
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart
    for n, s in (("body", body), ("cap", cap), ("chamber_plug", plug_print), ("diaphragm", diaphragm),
                 ("barrel_breech", breech), ("tube_clip", clip), *([("plug_yoke", yoke)] if PLUG_YOKE else []),
                 ("jig_base", jig_base), ("jig_ring", jig_ring), ("jig_puck", jig_puck)):
        s.exportStep(os.path.join(OUT_DIR, n + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, n + ".stl"))
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
