# -*- coding: utf-8 -*-
"""
Ratling Stage 1 test article: rotor/stator interface on a pivot.

A strip of the real stator (centre to port track, the aligned port and both
neighbours) and the real rotor arm, carried the way Stage 2 carries it: hub,
Ø8 shaft, two 608 bearings in a rear bridge on four columns. No gears, no cam;
the rotor is turned by hand and locked by a pin:

    stator ...... strip with the centre inlet bore and three ports, G1/8
                  tapped from the front, on a plate that takes the columns
                  and an index sector. Two variants:
                    A  printed face (one part),
                    B  printed body + 3 mm face plate (acrylic / POM / alu) in
                       a pocket, one small O-ring per port between them, four
                       countersunk M3 screws.
    rotor ....... Stage 2 arm (spigot, channel, shoe bore) run out to the
                  index rows; a plain hub replaces the cam hub.
    shoe ........ floating piston, radial O-ring, flat face on the stator,
                  pen-type spring behind it.
    bridge ...... Stage 2 bearing boss (2 x 608) on four arms and printed
                  spacers; a shaft collar behind the rear bearing.

Index: a Ø3 pin through the rotor arm into the sector holds the rotor at whole
degrees from -16 to +16 and at +-14.4 (the neighbours). Holes 1 deg apart do
not fit side by side, so degree k sits in row k mod 3; the arm has a hole for
each row. Shims between hub and front bearing set the gap, as in Stage 2.

All numbers come from ratling/params.py; the frame is described there.
Stator, rotor, spacers and collar print as modelled (+Z up: stator face and
rotor back on the bed). Hub, bridge and shoe print flipped (hub flange,
bridge front, shoe face on the bed); their STLs are turned accordingly.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/selector/stage1_interface.py').read())
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
import ratling.params as P
import ratling.geom as G
import ratling.fcview as V
for _m in (P, G, V):
    importlib.reload(_m)
from ratling.geom import cyl, fuse_all, port_xy

# ---------------------------------------------------------------- layout
STRIP_X0 = -22.0
STRIP_X1 = P.PORT_R + 22.0
STRIP_W = 50.0
STRIP_CORNER_R = 5.0

PORT_ANGLES = [0.0, P.INDEX_DEG, -P.INDEX_DEG]   # aligned port first

# Rotor travel and the pin index.
TURN_MAX = 16.0                 # deg each way, past both neighbours
INDEX_RS = (92.0, 98.0, 104.0)  # pin rows, outside the strip at any angle
INDEX_ANGLES = sorted([float(k) for k in range(-int(TURN_MAX), int(TURN_MAX) + 1)
                       if abs(k) != round(P.INDEX_DEG)] + [P.INDEX_DEG, -P.INDEX_DEG])
INDEX_DEPTH = 8.0               # blind, into the stator plate
SECTOR_R = INDEX_RS[-1] + 5.0
SECTOR_HALF = TURN_MAX + 2.5

# Rear bridge on four columns, clear of the arm over the whole travel.
COL_R = 40.0
COL_ANGLES = (60.0, 120.0, 240.0, 300.0)
COLUMNS = [port_xy(a, COL_R) for a in COL_ANGLES]
CENTRE_PLATE_D = 2 * (COL_R + P.FRAME_COL_D / 2 + 4)
COL_HEAD_R = 4.5                # M5 head / washer
MID_BORE_D = 12.0               # between the two bearings, as Stage 2
COLLAR_D = 16.0
COLLAR_L = 8.0
COLLAR_SHIM = 0.5               # 8 x 14 shim between collar and rear bearing

# Gap: shims (DIN 988 8 x 14) between hub and front bearing. More shim moves
# the rotor towards the stator. Below 0.5 the hub boss would touch the outer race.
SHIM_STEPS = (0.5, 1.0, 1.5, 2.0)

# Variant B: face plate in a pocket, held by countersunk M3 screws.
PLATE_SCREWS = [(-12.0, 17.0), (-12.0, -17.0), (P.PORT_R + 14.0, 17.0), (P.PORT_R + 14.0, -17.0)]
PLATE_SCREW_D = 3.4
PLATE_SCREW_HEAD_D = 6.5
PLATE_SCREW_PILOT = 2.5
PLATE_SCREW_DEPTH = 10.0
POCKET_CLEAR = 0.2

VARIANT_B_OFFSET = App.Vector(0, -260, 0)        # shown beside variant A, away from nothing

OUT_DIR = os.path.join(REPO, "exports", "stage1_interface")
NAME = "stage1_interface"

zf_bridge = P.spider_front_z
zb_arm = zf_bridge - P.FRAME_ARM_T
W = P.BEARING_W


def index_row(a):
    return int(round(a)) % 3


def gap(shim):
    return P.GAP + P.SHIM - shim


def ycyl(d, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(d / 2, y1 - y0, App.Vector(x, y0, z), G.Y)


def bar(angle, r0, r1, w, z0, z1):
    """Radial bar from r0 to r1 at angle (deg), width w."""
    b = Part.makeBox(r1 - r0, w, z1 - z0, App.Vector(r0, -w / 2, z0))
    b.rotate(G.O, G.Z, angle)
    return b


def turned(s, deg):
    s = s.copy()
    s.rotate(G.O, G.Z, deg)
    return s


def strip(z0, z1, grow=0.0):
    box = Part.makeBox(STRIP_X1 - STRIP_X0 + 2 * grow, STRIP_W + 2 * grow, z1 - z0,
                       App.Vector(STRIP_X0 - grow, -STRIP_W / 2 - grow, z0))
    vertical = [e for e in box.Edges
                if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6]
    return box.makeFillet(STRIP_CORNER_R + grow, vertical)


def stator_plate(z0, z1):
    """Centre plate for the columns plus the index sector."""
    sector = Part.makeCylinder(SECTOR_R, z1 - z0, App.Vector(0, 0, z0), G.Z, 2 * SECTOR_HALF)
    sector.rotate(G.O, G.Z, -SECTOR_HALF)
    return cyl(CENTRE_PLATE_D, z0, z1).fuse(sector)


def index_holes(z0, z1):
    return fuse_all([cyl(P.HUB_PIN_HOLE, z0, z1, *port_xy(a, INDEX_RS[index_row(a)]))
                     for a in INDEX_ANGLES])


def column_holes(z0, z1):
    return fuse_all([cyl(P.FRAME_BOLT_D, z0, z1, x, y) for x, y in COLUMNS])


# ---------------------------------------------------------------- parts
def make_stator_printed():
    t = P.stator_t
    body = strip(0, t).fuse(stator_plate(0, P.STATOR_PLATE_T))
    tools = fuse_all([G.centre_inlet_tools(0, t), G.port_tools(PORT_ANGLES, t),
                      column_holes(-1, t + 1), index_holes(-1, INDEX_DEPTH)])
    return body.cut(tools).cut(G.port_chamfers(PORT_ANGLES)).removeSplitter()


def make_stator_plate_variant():
    t = P.stator_t
    glands = fuse_all([cyl(P.plate_gland_od, P.PLATE_T - 1, P.PLATE_T + P.plate_gland_depth,
                           *port_xy(a)) for a in PORT_ANGLES])
    pilots = fuse_all([cyl(PLATE_SCREW_PILOT, P.PLATE_T - 1, P.PLATE_T + PLATE_SCREW_DEPTH, x, y)
                       for x, y in PLATE_SCREWS])
    body = strip(0, t).fuse(stator_plate(0, P.STATOR_PLATE_T))
    tools = fuse_all([strip(-1, P.PLATE_T, POCKET_CLEAR), G.centre_inlet_tools(P.PLATE_T, t),
                      G.port_tools(PORT_ANGLES, t), glands, pilots,
                      column_holes(-1, t + 1), index_holes(-1, INDEX_DEPTH)])
    body = body.cut(tools).removeSplitter()

    plate = strip(0, P.PLATE_T)
    holes = [cyl(P.spigot_bore_d + 1.0, -1, P.PLATE_T + 1)]
    holes += [cyl(P.PORT_D, -1, P.PLATE_T + 1, *port_xy(a)) for a in PORT_ANGLES]
    holes += [cyl(PLATE_SCREW_D, -1, P.PLATE_T + 1, x, y).fuse(
              G.cone(PLATE_SCREW_HEAD_D + 0.02, -0.01, PLATE_SCREW_D, (PLATE_SCREW_HEAD_D - PLATE_SCREW_D) / 2,
                     x, y)) for x, y in PLATE_SCREWS]
    plate = plate.cut(fuse_all(holes)).cut(G.port_chamfers(PORT_ANGLES)).removeSplitter()
    return body, plate


def make_rotor():
    """Stage 2 arm run out to the index rows, a pin hole for each row."""
    zf, zb = P.rotor_face_z, P.rotor_back_z
    w = P.ROTOR_ARM_W
    r_end = INDEX_RS[-1]
    arm = fuse_all([cyl(P.ROTOR_CENTRE_D, zb, zf),
                    Part.makeBox(r_end, w, zf - zb, App.Vector(0, -w / 2, zb)),
                    cyl(w, zb, zf, r_end), G.spigot()])
    holes = fuse_all([G.rotor_passages(),
                      G.hub_screws(P.HUB_SCREW_PILOT, zb - 1, zb + P.HUB_SCREW_DEPTH),
                      cyl(P.HUB_PIN_HOLE, zb - 1, zb + P.HUB_PIN_DEPTH, *port_xy(P.HUB_PIN_ANGLE, P.HUB_PIN_R))]
                     + [cyl(P.HUB_PIN_HOLE, zb - 1, zf + 1, r) for r in INDEX_RS])
    return arm.cut(holes).removeSplitter()


def make_hub():
    """Stage 2 hub with a plain flange instead of the cam."""
    zb = P.rotor_back_z
    z_fl = zb - P.HUB_FLANGE_T
    hub = cyl(P.ROTOR_CENTRE_D, z_fl, zb).fuse(cyl(P.HUB_BOSS_D, P.hub_back_z, z_fl + 0.01))
    z_set = (P.hub_back_z + z_fl) / 2
    holes = fuse_all([cyl(P.SHAFT_BORE_D, P.hub_back_z - 1, zb + 1),
                      G.hub_screws(3.4, z_fl - 1, zb + 1),
                      cyl(P.HUB_PIN_HOLE, z_fl - 1, zb + 1, *port_xy(P.HUB_PIN_ANGLE, P.HUB_PIN_R)),
                      ycyl(P.SET_SCREW_PILOT, 0, P.HUB_BOSS_D, 0, z_set)])
    return hub.cut(holes).removeSplitter()


def make_bridge():
    """Stage 2 bearing boss on four arms to the columns."""
    body = fuse_all([cyl(P.BEARING_BOSS_D, P.boss_back_z, zf_bridge)]
                    + [bar(a, 0, COL_R, P.FRAME_ARM_W, zb_arm, zf_bridge) for a in COL_ANGLES]
                    + [cyl(P.FRAME_COL_D + 4, zb_arm, zf_bridge, x, y) for x, y in COLUMNS])
    holes = fuse_all([cyl(P.BEARING_SEAT_D, zf_bridge - W, zf_bridge + 1),
                      cyl(MID_BORE_D, P.boss_back_z - 1, zf_bridge + 1),
                      cyl(P.BEARING_SEAT_D, P.boss_back_z - 1, P.boss_back_z + W),
                      column_holes(zb_arm - 1, zf_bridge + 1)])
    return body.cut(holes).removeSplitter()


def make_spacer(x=0.0, y=0.0):
    return cyl(P.FRAME_COL_D, zf_bridge, 0, x, y).cut(cyl(P.FRAME_BOLT_D, zf_bridge - 1, 1, x, y))


collar_z1 = P.boss_back_z - COLLAR_SHIM
collar_z0 = collar_z1 - COLLAR_L


def make_collar():
    return cyl(COLLAR_D, collar_z0, collar_z1).cut(
        cyl(P.SHAFT_BORE_D, collar_z0 - 1, collar_z1 + 1)).cut(
        ycyl(P.SET_SCREW_PILOT, 0, COLLAR_D, 0, (collar_z0 + collar_z1) / 2)).removeSplitter()


stator_a = make_stator_printed()
stator_b, plate_b = make_stator_plate_variant()
rotor = make_rotor()
hub = make_hub()
shoe = G.shoe()
bridge = make_bridge()
spacers = [make_spacer(x, y) for x, y in COLUMNS]
collar = make_collar()

# ---------------------------------------------------------------- bought parts
def bearing(z0):
    return cyl(P.BEARING_OD, z0, z0 + W).cut(cyl(P.SHAFT_D, z0 - 1, z0 + W + 1))


def shim_ring(z0, z1):
    return cyl(14.0, z0, z1).cut(cyl(P.SHAFT_D, z0 - 1, z1 + 1))


shaft_z0 = collar_z0 - 2.0
shaft = cyl(P.SHAFT_D, shaft_z0, P.rotor_back_z)
bearings = bearing(zf_bridge - W).fuse(bearing(P.boss_back_z))
shims = shim_ring(zf_bridge, P.hub_back_z).fuse(shim_ring(collar_z1, P.boss_back_z))
pin = cyl(P.HUB_PIN_D, P.rotor_back_z - 4, INDEX_DEPTH - 0.5, INDEX_RS[0])
col_bolt_len = P.STATOR_PLATE_T - zb_arm

# ---------------------------------------------------------------- checks
sx = P.PORT_R
air_path = ([(0, 0, z) for z in (P.channel_z, P.rotor_face_z, 0.0, P.SPIGOT_TIP_Z - 0.5)]
            + [(x, 0, P.channel_z) for x in (5, 20, 40, sx - 5)]
            + [(sx, 0, z) for z in (P.channel_z, P.shoe_floor_z + 0.5, -P.SHOE_LEN - 1)])
stator_path = [(0, 0, z) for z in (1, P.spigot_bore_depth + 1, P.stator_t - 1)] + \
              [(sx, 0, z) for z in (0.2, P.stator_t / 2, P.stator_t - 1)]


def columns_clear_of_fittings():
    lim = P.fitting_corners / 2 + COL_HEAD_R + 1.0
    fittings = [(0.0, 0.0)] + [port_xy(a) for a in PORT_ANGLES]
    return min(math.hypot(cx - fx, cy - fy) for cx, cy in COLUMNS for fx, fy in fittings) >= lim


def index_wall():
    """Thinnest wall between two pin holes of the stator."""
    pts = [port_xy(a, INDEX_RS[index_row(a)]) for a in INDEX_ANGLES]
    d = min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
    return d - P.HUB_PIN_HOLE


def pin_lands(a):
    """With the rotor at a, its hole for that row lies over the stator hole."""
    x, y = port_xy(a, INDEX_RS[index_row(a)])
    return (G.open_along(stator_a, [(x, y, INDEX_DEPTH - 1)])
            and G.open_along(turned(rotor, a), [(x, y, (P.rotor_face_z + P.rotor_back_z) / 2)]))


no_overlap = G.no_overlap
moving = [rotor, hub, shoe]
fixed_a = [stator_a, bridge] + spacers
fixed_b = [stator_b, plate_b]
turn_ok = all(no_overlap(f, turned(m, a))
              for a in (-TURN_MAX, -P.INDEX_DEG, P.INDEX_DEG, TURN_MAX)
              for m in moving for f in fixed_a + fixed_b)
shoe_groove_top = P.SHOE_GROOVE_FROM_BACK + P.groove_w / 2
parts = [stator_a, stator_b, plate_b, rotor, hub, shoe, bridge, collar] + spacers
geo_checks = [
    ("all parts valid single solids", all(G.single_solid(s) for s in parts)),
    ("A: stator / rotor / shoe / hub no interference",
     all(no_overlap(a, b) for a, b in ((stator_a, rotor), (stator_a, shoe), (rotor, shoe),
                                       (rotor, hub), (stator_a, hub)))),
    ("B: body / plate / rotor / shoe no interference",
     all(no_overlap(a, b) for a, b in ((stator_b, plate_b), (stator_b, rotor),
                                       (plate_b, rotor), (plate_b, shoe), (stator_b, shoe)))),
    ("bridge, spacers, collar clear of hub, shaft and each other",
     all(no_overlap(a, b) for a in [bridge, collar] + spacers for b in (hub, shaft))
     and no_overlap(bridge, collar) and all(no_overlap(bridge, s) for s in spacers)),
    ("rotor, hub, shoe clear at 0, +-14.4, +-%g deg" % TURN_MAX, turn_ok),
    ("shoe face on the stator face (z = 0)", abs(shoe.BoundBox.ZMax) < 1e-6),
    ("air path open through rotor",
     G.open_along(rotor, air_path) and G.open_along(shoe, [(sx, 0, -1)])),
    ("air path open through stator A", G.open_along(stator_a, stator_path)),
    ("air path open through stator B",
     G.open_along(stator_b, stator_path) and G.open_along(plate_b, [(0, 0, 1), (sx, 0, 1)])),
    ("pin finds its hole at every index angle", all(pin_lands(a) for a in INDEX_ANGLES)),
    ("wall between index holes >= 1 mm", index_wall() >= 1.0),
    ("index holes outside the strip (B: not under the plate)",
     all(not strip(-1, 1, POCKET_CLEAR + P.HUB_PIN_HOLE / 2).isInside(
         App.Vector(*port_xy(a, INDEX_RS[index_row(a)]), 0), 1e-4, True) for a in INDEX_ANGLES)),
    ("column bolt heads clear of fittings", columns_clear_of_fittings()),
    ("thickest shim stack: rotor face clear of the stator", gap(SHIM_STEPS[-1]) > 0.3),
    ("thinnest shim stack: shoe O-ring stays in its bore",
     shoe_groove_top <= P.SHOE_LEN - gap(SHIM_STEPS[0]) - 0.5),
]

lines = [P.report(), "", NAME]
lines += ["  stator                 : strip %.0f x %.0f, t %.1f; plate Ø%.0f + index sector R%.0f, t %.1f"
          % (STRIP_X1 - STRIP_X0, STRIP_W, P.stator_t, CENTRE_PLATE_D, SECTOR_R, P.STATOR_PLATE_T)]
lines += ["  volumes cm3            : stator A %.1f, body B %.1f, plate B %.1f, rotor %.1f, hub %.1f,"
          " bridge %.1f, shoe %.2f"
          % tuple(s.Volume / 1000 for s in (stator_a, stator_b, plate_b, rotor, hub, bridge, shoe))]
lines += ["  index                  : pin Ø%g, holes Ø%.2f at R %s (row = degree mod 3), %d positions"
          " %+g..%+g deg + neighbours +-%.1f; wall %.1f"
          % (P.HUB_PIN_D, P.HUB_PIN_HOLE, "/".join("%g" % r for r in INDEX_RS), len(INDEX_ANGLES),
             -TURN_MAX, TURN_MAX, P.INDEX_DEG, index_wall())]
lines += ["  shoe vs angle          : port at the land edge +-%.1f deg, MIN_LAND kept to +-%.1f"
          % (P.shoe_seal_window_deg, P.shoe_misalign_deg)]
lines += ["  gap by shim (hub/brg)  : %s"
          % ", ".join("%.1f -> %.1f%s" % (s, gap(s), " nominal" if abs(s - P.SHIM) < 1e-9 else "")
                      for s in SHIM_STEPS)]
lines += ["  bought                 : shaft Ø8 x %.0f, 2 x 608ZZ, shims 8x14 (DIN 988), 4 x M5 x %.0f+"
          " with nuts, Ø3 pin, 2 x M3 set screw" % (P.rotor_back_z - shaft_z0, col_bolt_len)]
lines += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in geo_checks]
report = "\n".join(lines)
print(report)

# ---------------------------------------------------------------- references
# Shown in the FreeCAD document only; not exported.
HOSE_LEN = 60.0


def col_bolts():
    t = P.STATOR_PLATE_T
    return fuse_all([fuse_all([cyl(5.0, zb_arm - 4, t + 3.5, x, y), cyl(8.5, t, t + 3.5, x, y),
                               G.hex_prism(8.0, zb_arm - 4, zb_arm, x, y)]) for x, y in COLUMNS])


def plate_screws():
    return fuse_all([cyl(3.0, 0, PLATE_SCREW_DEPTH, x, y).fuse(
        G.cone(PLATE_SCREW_HEAD_D - 0.2, 0, 3.0, (PLATE_SCREW_HEAD_D - 3.2) / 2, x, y))
        for x, y in PLATE_SCREWS])


def references(variant):
    """Fittings, hoses, O-rings, spring, drive hardware and the pin for one variant."""
    t = P.stator_t
    ports = [(0.0, 0.0)] + [port_xy(a) for a in PORT_ANGLES]
    rings = [G.rotor_orings()]
    refs = {}
    if variant == "B":
        rings += [Part.makeTorus(P.plate_gland_od / 2 - P.PLATE_ORING_CS / 2, P.PLATE_ORING_CS / 2,
                                 App.Vector(x, y, P.PLATE_T + P.PLATE_ORING_CS / 2 * 0.75), G.Z)
                  for x, y in map(port_xy, PORT_ANGLES)]
        refs["PlateScrews"] = (plate_screws(), "steel")
    refs.update({
        "Fittings": (fuse_all([G.push_in_fitting(x, y, t) for x, y in ports]), "steel"),
        "Hoses": (fuse_all([G.hose(x, y, t, HOSE_LEN) for x, y in ports]), "hose"),
        "ORings": (fuse_all(rings), "oring"),
        "Spring": (G.shoe_spring(), "steel"),
        "Shaft": (shaft, "steel"),
        "Bearings": (bearings, "steel"),
        "Shims": (shims, "steel"),
        "ColumnBolts": (col_bolts(), "steel_ghost"),
        "Pin": (pin, "steel"),
    })
    return refs


def ghost_stator():
    """The full 25-port stator this strip is cut from."""
    t = P.stator_t
    return cyl(2 * P.PORT_R + P.fitting_corners + 6, 0, t).cut(fuse_all(
        [cyl(P.PORT_D, -1, t + 1, *port_xy(i * P.INDEX_DEG)) for i in range(P.N_PORTS)]))


LABELS = [
    ("ВХОД: воздух от 3/2-клапана", (-14, 0, P.stator_t + HOSE_LEN)),
    ("ВЫХОДЫ: совмещённый + 2 соседних", (P.PORT_R + 14, 0, P.stator_t + HOSE_LEN)),
    ("СТАТОР (неподвижный, лицом вперёд)", (SECTOR_R + 8, 0, P.stator_t)),
    ("РОТОР: поворот рукой ±%g°" % TURN_MAX, (SECTOR_R + 18, 0, P.rotor_back_z)),
    ("ШТИФТ Ø3: фиксирует угол, ряд = градус mod 3", (INDEX_RS[0], 30, P.rotor_back_z - 10)),
    ("БАШМАК: прижат к статору", (P.PORT_R, 0, P.rotor_back_z - 12)),
    ("МОСТ: 2 x 608, как в Stage 2", (0, 60, P.boss_back_z)),
    ("ШАЙБЫ 8x14 между хабом и подшипником: зазор", (-60, 0, zf_bridge)),
    ("ВАРИАНТ B: корпус + пластина", (SECTOR_R + 8, VARIANT_B_OFFSET.y, P.stator_t)),
]
EXPLODE = {"fittings": 70, "stator": 40, "ring_spigot": 10, "shoe": 12, "spring": -8, "rotor": -40,
           "pin": -55, "hub": -70, "shims": -85, "bearings": -100, "bridge": -115, "collar": -130}

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
sc = V.Scene(NAME)
doc = sc.doc
for v, off, st in (("A", None, [("Stator_A", stator_a, "stator")]),
                   ("B", VARIANT_B_OFFSET, [("Body_B", stator_b, "stator"), ("Plate_B", plate_b, "plate")])):
    for n, s, style in st + [("Rotor_" + v, rotor, "rotor"), ("Hub_" + v, hub, "rotor"),
                             ("Shoe_" + v, shoe, "shoe"), ("Bridge_" + v, bridge, "frame"),
                             ("Collar_" + v, collar, "printed")]:
        sc.add("Variant_" + v, n, s, style, off)
    for i, s in enumerate(spacers):
        sc.add("Variant_" + v, "Spacer%d_%s" % (i, v), s, "printed", off)
    sc.add("Refs_" + v, "Flow_" + v, G.flow_path(P.stator_t, HOSE_LEN), "flow", off)
    for n, (s, style) in references(v).items():
        sc.add("Refs_" + v, n + "_" + v, s, style, off)
sc.add("Ghost_selector", "Ghost_stator_25", ghost_stator(), "ghost")
for a in (-TURN_MAX, TURN_MAX):
    sc.add("Travel", "Rotor_at_%+g" % a, turned(rotor, a), "ghost")

half = Part.makeBox(400, 200, 400, App.Vector(-200, -200, -200))     # machine y < 0
for n, style in (("Stator_A", "stator"), ("Rotor_A", "rotor"), ("Hub_A", "rotor"), ("Shoe_A", "shoe"),
                 ("Bridge_A", "frame"), ("Collar_A", "printed"), ("ORings_A", "oring"),
                 ("Spring_A", "steel"), ("Fittings_A", "steel"), ("Hoses_A", "hose"),
                 ("Shaft_A", "steel"), ("Bearings_A", "steel"), ("Shims_A", "steel"), ("Pin_A", "steel")):
    sc.add("Section_A", "Sec" + n, sc.src[n].cut(half), style)

refs_a = references("A")
explode = [
    ("fittings", refs_a["Fittings"][0], "steel", "6. Штуцеры 6 мм (покупные), 4 шт."),
    ("stator", stator_a, "stator", "1. СТАТОР: печать, неподвижный"),
    ("ring_spigot", G.oring(P.oring_root_d, P.ORING_CS, P.SPIGOT_GROOVE_Z), "oring",
     "5. Кольца 8x1.5: хвостовик и башмак"),
    ("shoe", shoe.fuse(G.oring(P.oring_root_d, P.ORING_CS,
                               -P.SHOE_LEN + P.SHOE_GROOVE_FROM_BACK, P.PORT_R)), "shoe",
     "3. БАШМАК: печать или POM, плавающий"),
    ("spring", refs_a["Spring"][0], "steel", "7. Пружинка от ручки"),
    ("rotor", rotor, "rotor", "2. РОТОР: печать, поворачивается"),
    ("pin", pin, "steel", "8. Штифт Ø3"),
    ("hub", hub, "rotor", "4. ХАБ: печать, 3 x M3 + штифт к ротору"),
    ("shims", shims, "steel", "9. Шайбы 8x14: зазор"),
    ("bearings", bearings.fuse(shaft), "steel", "10. Вал Ø8 + 2 x 608ZZ"),
    ("bridge", bridge.fuse(fuse_all(spacers)), "frame", "11. МОСТ + 4 стойки: печать, M5"),
    ("collar", collar, "printed", "12. Кольцо на вал: печать, M3"),
]
for key, s, style, text in explode:
    off = App.Vector(0, 0, EXPLODE[key])
    sc.add("Exploded", "Ex_" + key, s, style, off)
    bb = sc.src["Ex_" + key].BoundBox
    sc.label("Exploded", text, (bb.XMax + 8, -30, (bb.ZMin + bb.ZMax) / 2))

for text, pos in LABELS:
    sc.label("Labels", text, pos)
sc.finish(hidden_groups=("Section_A", "Exploded", "Travel"), opaque_groups=("Section_A", "Exploded"))
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

# ---------------------------------------------------------------- exports
import MeshPart


def write_stl(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(G.O, G.X, 180)
    s.translate(App.Vector(0, 0, -s.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1)
    m.write(os.path.join(OUT_DIR, name + ".stl"))


for f in os.listdir(OUT_DIR):
    if f.endswith((".stl", ".step")):
        os.remove(os.path.join(OUT_DIR, f))
for n, s, flip in (("stator_A", stator_a, False), ("body_B", stator_b, False), ("plate_B", plate_b, None),
                   ("rotor", rotor, False), ("hub", hub, True), ("shoe", shoe, True),
                   ("bridge", bridge, True), ("spacer", spacers[0], False), ("collar", collar, False)):
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    if flip is not None:
        write_stl(s, n, flip)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write(report + "\n")
print("written to", OUT_DIR)
