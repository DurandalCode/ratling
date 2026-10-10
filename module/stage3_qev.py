# -*- coding: utf-8 -*-
"""
Ratling Stage 3: barrel module with a printed diaphragm quick-exhaust valve.

One barrel of the mitrailleuse. Chamber and barrel are cut from the 25 mm
metal tube and run side by side, both pointing forward, out of one printed
body; the valve sits behind the barrel axis:

    chamber tube ──> chamber spigot ──> window ──> gallery (around the seat)
                                                     │  diaphragm lifts into
                                                     ▼  the cap pocket
    barrel tube  <── barrel spigot  <── seat (Ø SEAT_D, on the barrel axis)

    pilot (cap pocket) pressurized: the diaphragm sits on the seat and the
    chamber charges from the pilot through a bleed hole in the diaphragm.
    pilot vented: chamber pressure on the annulus outside the seat lifts the
    diaphragm into the pocket, and the chamber dumps straight into the barrel.

Parts, each exported in its print orientation (lowest point at z = 0):

    body ........ clamp face on the bed, both spigots up. The seat land and
                  the clamp face are the bed face (flat). Gallery ceiling is
                  a 45 deg cone; short radial ribs at the clamp plane carry
                  the diaphragm while the pilot is up and the chamber empty.
    cap ......... clamp face up: recess that locates the diaphragm and sets
                  its squeeze, pocket (= lift), radial grooves in the pocket
                  floor, G1/8 pilot port from the bed side, M4 nut pockets.
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
LIFT = 4.0              # pocket depth below the diaphragm
GROOVE_N = 4            # pocket floor grooves, so the diaphragm cannot seal the port
GROOVE_W = 2.0
GROOVE_DEPTH = 1.0
GROOVE_LEN = 15.0
BLEED_D = 0.8
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
NUT_POCKET_DEPTH = 3.5
ROD_HEAD_D = 7.0        # M4 socket head
ROD_HEAD_H = 4.0
NUT_T = 3.2

CHAMBER_V = 100.0       # cm3, target
PLUG_INSERT_LEN = 30.0  # chamber plug, inside the tube
PLUG_FLANGE_T = 5.0
PLUG_FLANGE_D = TUBE_OD + 2.0   # stays clear of the barrel tube beside it

OUT_DIR = os.path.join(REPO, "exports", "stage3_qev")
NAME = "stage3_qev"

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

barrel_spigot, bg0, bg2 = spigot(BODY_H, BARREL_SPIGOT_LEN, V(0, 0))
chamber_spigot, cg0, cg2 = spigot(BODY_H, CHAMBER_SPIGOT_LEN, C)
body = body.fuse(barrel_spigot).fuse(chamber_spigot)

gallery = revolve([(seat_out_r, -1), (mouth_r + 1, -1), (GALLERY_R, MOUTH_CHAMFER),
                   (GALLERY_R, GALLERY_H), (seat_out_r, cone_top)])
window = Part.makeBox(chamber_x - GALLERY_R + 2, SEAT_D, GALLERY_H - WINDOW_Z0,
                      V(GALLERY_R - 4, -seat_r, WINDOW_Z0))
gable = Part.Face(Part.makePolygon([V(GALLERY_R - 4, -seat_r, GALLERY_H), V(GALLERY_R - 4, seat_r, GALLERY_H),
                                    V(GALLERY_R - 4, 0, window_top), V(GALLERY_R - 4, -seat_r, GALLERY_H)])
                  ).extrude(V(chamber_x - GALLERY_R + 2, 0, 0))
cuts = [gallery, window, gable,
        cyl(seat_r, -1, BODY_H + BARREL_SPIGOT_LEN + 1),
        cyl(seat_r, WINDOW_Z0, BODY_H + CHAMBER_SPIGOT_LEN + 1, C)]
cuts += [cyl(ROD_HOLE_D / 2, -1, BODY_H + 1, p) for p in rod_pts]
cuts += screw_pilots(V(0, 0), BODY_H + SCREW_FROM_TUBE_END, barrel_screw_angles)
cuts += screw_pilots(C, BODY_H + SCREW_FROM_TUBE_END, chamber_screw_angles)
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
hex_r = (NUT_AF + 2 * NUT_POCKET_CLEAR) / math.sqrt(3)
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
    cuts.append(prism([(p.x + hex_r * math.cos(math.radians(60 * k)), p.y + hex_r * math.sin(math.radians(60 * k)))
                       for k in range(6)], -1, NUT_POCKET_DEPTH))
mark = prism([(recess_r + 0.8, 0), (BODY_R + 1, MARK_W / 2), (BODY_R + 1, -MARK_W / 2)],
             CAP_T - MARK_DEPTH, CAP_T + 1)
mark.rotate(V(0, 0), Z, BLEED_ANGLE)
cuts.append(mark)
for c in cuts:
    cap = cap.cut(c)
cap = cap.removeSplitter()

# ---------------------------------------------------------------- chamber plug (print frame)
plug_print = revolve([(0, 0), (PLUG_FLANGE_D / 2 - 0.5, 0), (PLUG_FLANGE_D / 2, 0.5),
                      (PLUG_FLANGE_D / 2, PLUG_FLANGE_T), (0, PLUG_FLANGE_T)])
plug_spigot, pg0, _ = spigot(PLUG_FLANGE_T, PLUG_INSERT_LEN, V(0, 0))
plug_print = plug_print.fuse(plug_spigot)
for c in screw_pilots(V(0, 0), PLUG_FLANGE_T + SCREW_FROM_TUBE_END, chamber_screw_angles):
    plug_print = plug_print.cut(c)
plug_print = plug_print.removeSplitter()

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
rod_len = 5 * math.ceil((BODY_H + CAP_T) / 5)   # reaches through the nut in its pocket

cap_a = cap.copy()
cap_a.translate(V(0, 0, -CAP_T))           # cap top face meets the body bed face
dia_a = cyl(DIA_D / 2, -dia_t_clamped, 0)  # clamped
tubes = [cyl(TUBE_OD / 2, BODY_H, BODY_H + L, at).cut(cyl(TUBE_ID / 2, BODY_H - 1, BODY_H + L + 1, at))
         for at, L in ((V(0, 0), BARREL_LEN), (C, chamber_tube_len))]
tube_end = BODY_H + chamber_tube_len
plug = plug_print.copy()                  # turned tip-down, stop face on the tube end
plug.rotate(V(0, 0), X, 180)
plug.translate(V(C.x, C.y, tube_end + PLUG_FLANGE_T))

# ---------------------------------------------------------------- numbers
A_seat_eff = area(SEAT_D + SEAT_LAND)          # to the middle of the land
A_dia = area(2 * mouth_r)
A_curtain = math.pi * SEAT_D * LIFT
A_window = SEAT_D * (GALLERY_H - WINDOW_Z0) + SEAT_D * seat_r / 2
A_gallery = 2 * (GALLERY_R - seat_out_r) * GALLERY_H
open_ratio = 1 - A_seat_eff / A_dia                # pilot/chamber (gauge) below which it opens
F_cap = P_MAX_BAR * 0.1 * area(2 * mouth_r)
F_spigot = P_MAX_BAR * 0.1 * area(TUBE_ID)
pocket_v = (area(2 * GALLERY_R) * LIFT + area(2 * mouth_r) * dia_t_clamped) / 1000
dead_v = A_seat * (BODY_H + BARREL_SPIGOT_LEN) / 1000
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
        PLUG_FLANGE_T + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < pg0 - 1.0,
    "body/tubes no interference": all(body.common(t).Volume < 1e-3 for t in tubes),
    "body/cap/diaphragm stack no interference":
        body.common(cap_a).Volume < 1e-3 and body.common(dia_a).Volume < 1e-3 and cap_a.common(dia_a).Volume < 1e-3,
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
    "rod heads clear of both tubes":
        min(dist(C, p) for p in rod_pts) - TUBE_OD / 2 - ROD_HEAD_D / 2 >= 1.0
        and ROD_R - TUBE_OD / 2 - ROD_HEAD_D / 2 >= 1.0,
    "wall groove root -> bore >= 2 mm": root_r - seat_r >= 2.0,
    "screw tip inside its pilot": TUBE_OD / 2 - SCREW_L >= spigot_r - SCREW_DEPTH,
    "wall screw pilot -> bore >= 1.4 mm": spigot_r - SCREW_DEPTH - seat_r >= 1.4 - 1e-9,
    "screws outboard of the O-rings": BODY_H + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < min(bg0, cg0) - 1.0,
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
    "  opens when pilot < %.0f %% of chamber pressure (gauge)" % (open_ratio * 100),
    "  pilot volume (pocket)  : %.1f cm3" % pocket_v,
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  chamber %.0f cm3        : tube %.0f mm long (spigot %.0f + plug %.0f inside it; body adds %.1f cm3)"
    % (CHAMBER_V, chamber_tube_len, CHAMBER_SPIGOT_LEN, PLUG_INSERT_LEN, chamber_extra_v),
    "  chamber/barrel axes    : %.1f mm apart" % chamber_x,
    "  @ %.0f bar               : cap %.0f N (%.0f N per M4), chamber tube blow-off %.0f N"
    % (P_MAX_BAR, F_cap, F_cap / ROD_N, F_spigot),
    "  tie rods               : %d x M4 x %d socket head + nut (body + cap %.0f mm)"
    % (ROD_N, rod_len, BODY_H + CAP_T),
    "  body / cap volume      : %.1f / %.1f cm3" % (body.Volume / 1000, cap.Volume / 1000),
]
for k, v in checks.items():
    report.append("  [%s] %s" % ("OK " if v else "FAIL", k))
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
    for p in rod_pts:
        rods += [cyl(ROD_HEAD_D / 2, BODY_H, BODY_H + ROD_HEAD_H, p),
                 cyl(2.0, BODY_H - rod_len, BODY_H, p),
                 G.hex_prism(NUT_AF, -CAP_T, -CAP_T + NUT_T, p.x, p.y)]
    return G.fuse_all(rods)


def tube_screws():
    out = []
    for at, angles, z in ((V(0, 0), barrel_screw_angles, BODY_H + SCREW_FROM_TUBE_END),
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
orings = G.fuse_all([G.oring(2 * root_r, ORING_CS, ring_z(BARREL_SPIGOT_LEN)),
                     G.oring(2 * root_r, ORING_CS, ring_z(CHAMBER_SPIGOT_LEN), C.x, C.y),
                     G.oring(2 * root_r, ORING_CS, plug_ring_z, C.x, C.y)])


pilot_fitting = flipped(G.push_in_fitting(0, 0, 0), -CAP_T)
pilot_hose = flipped(G.hose(0, 0, 0, 80), -CAP_T)
ball = Part.makeSphere(BALL_D / 2, V(0, 0, BODY_H + BARREL_SPIGOT_LEN + BALL_D / 2))

# ---------------------------------------------------------------- output
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
doc = sc.doc
for n, s, style in (("Body", body, "rotor"), ("Cap", cap_a, "stator"), ("Diaphragm", dia_a, "shoe"),
                    ("Chamber_plug", plug, "rotor")):
    sc.add("Printed", n, s, style)
bought = [("Barrel_tube", tubes[0], "ghost"), ("Chamber_tube", tubes[1], "ghost"),
          ("Tie_rods", tie_rods(), "steel"), ("Tube_screws", tube_screws(), "steel"),
          ("ORings", orings, "oring"), ("Pilot_fitting", pilot_fitting, "steel"),
          ("Pilot_hose", pilot_hose, "hose"), ("Ball", ball, "flow")]
for n, s, style in bought:
    sc.add("Bought", n, s, style)

half = Part.makeBox(400, 200, 800, V(-200, -200, -100))     # y < 0
for n in ("Body", "Cap", "Diaphragm", "Chamber_plug", "Barrel_tube", "Chamber_tube", "ORings", "Ball", "Pilot_fitting"):
    style = dict(Body="rotor", Chamber_plug="rotor", Cap="stator", Diaphragm="shoe", ORings="oring", Ball="flow",
                 Pilot_fitting="steel").get(n, "ghost")
    sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)

for text, pos in [
    ("СТВОЛ: труба %.0f мм (подрезать)" % BARREL_LEN, (-25, 0, BODY_H + BARREL_LEN)),
    ("КАМЕРА %.0f см3: труба %.0f мм" % (CHAMBER_V, chamber_tube_len), (C.x + 25, 0, tube_end - 40)),
    ("ЗАГЛУШКА камеры (глухая, PETG)", (C.x + 25, 0, tube_end + 10)),
    ("ШАРИК Rival", (-25, 0, BODY_H + BARREL_SPIGOT_LEN + BALL_D)),
    ("КОРПУС QEV (PETG 100 %)", (BODY_R + 10, 0, BODY_H / 2)),
    ("МЕМБРАНА 1,5 мм, Ø%.0f" % DIA_D, (-BODY_R - 10, 0, 0)),
    ("КРЫШКА: пилот G1/8 -> M3R110 A", (-BODY_R - 10, 0, -CAP_T / 2)),
    ("ШПИЛЬКИ M4 x %d x4 + гайки" % rod_len, (rod_pts[1].x, rod_pts[1].y, BODY_H + 10)),
    ("САМОРЕЗЫ ST2.9 x %.1f x6" % SCREW_L, (-TUBE_OD, 0, BODY_H + SCREW_FROM_TUBE_END)),
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
             ("jig_base", jig_base), ("jig_ring", jig_ring), ("jig_puck", jig_puck)):
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
        os.path.join(OUT_DIR, n + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
