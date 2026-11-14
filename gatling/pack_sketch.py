# -*- coding: utf-8 -*-
"""
Gatling pack — readable 3D block sketch on a bench stand.

Six breech stations on a hex at PACK_PITCH, full-length axle, front spider
plate, hub + MQR, two bearing posts on a table slab. Warm = spins with the
pack, cool = stays on the bench. No crank, hopper, or hoses — silhouette only
so the layout and how the gun sits on the stand both read.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/pack_sketch.py').read())"

Exports: exports/gatling_pack_sketch/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_pack_sketch")
NAME = "gatling_pack_sketch"

# ---------------------------------------------------------------- pack / station (mm)
N = 6
PACK_PITCH = 68.0            # station axis radius (= pitch for hex of 6)
R = PACK_PITCH

BARREL_OD, BARREL_ID = 25.0, 23.8
BARREL_L = 180.0
CH_OD, CH_L = 50.0, 130.0    # fat coax chamber block (matches fat_coax / breech bench)
QEV_GAP = 8.0                # rear plug ears / carriage lump behind chamber

AXLE_OD, AXLE_ID = 16.0, 10.0
BRG_OD, BRG_T = 36.0, 14.0
HUB_OD, HUB_T = 50.0, 18.0
ROTOR_OD, ROTOR_L = 46.0, 29.0
STATOR_OD, STATOR_L = 46.0, 53.0
STATOR_HUB_OD, STATOR_HUB_L = 20.0, 8.0
THROUGH = 6.0
MQR_GAP = 2.0

PLATE_T = 12.0               # front spider (spins with barrels)
PLATE_OD = 2 * R + BARREL_OD + 16.0

# Bench stand (cool) — table + two end plates with spokes in the station gaps.
TABLE_T = 12.0
FRAME_T = 12.0
SPOKE_W = 8.0
SPOKE_T = 10.0
# End-plate OD outside chamber ring; cutout clears chambers + margin.
FRAME_OD = 2 * (R + CH_OD / 2 + 24.0)
FRAME_ID = BRG_OD + 8.0                 # central boss around each race
PACK_CLEAR_R = R + CH_OD / 2 + 10.0     # outer rim stays outside this radius

# +Z toward muzzle. Hub/MQR sit behind the QEV ring.
z_muzzle = 0.0
z_plate0 = z_muzzle
z_plate1 = z_plate0 + PLATE_T
z_breech = BARREL_L
z_ch0 = z_breech
z_ch1 = z_ch0 + CH_L
z_qev_aft = z_ch1 + QEV_GAP

z_hub1 = z_qev_aft + 25.0
z_hub0 = z_hub1 - HUB_T
# Full axle: nose through the spider → ends in the hub (never into MQR Ø6).
z_axle0 = z_plate0 - 8.0
z_axle1 = z_hub1
# Bearings span the pack mass: front just aft of spider, rear just before hub.
z_brg_f0 = z_plate1 + 8.0
z_brg_f1 = z_brg_f0 + BRG_T
z_brg_r1 = z_hub0 - 10.0
z_brg_r0 = z_brg_r1 - BRG_T
z_rotor0 = z_hub1 + MQR_GAP
z_rotor1 = z_rotor0 + ROTOR_L
z_stator0 = z_rotor1
z_stator1 = z_stator0 + STATOR_L
z_stub1 = z_stator1 + STATOR_HUB_L

AXLE_L = z_axle1 - z_axle0
BRG_SPAN = (z_brg_r0 + z_brg_r1) / 2 - (z_brg_f0 + z_brg_f1) / 2
STATION_L = z_qev_aft - z_muzzle

# Pack OD clears axle; table sits below the lowest chamber OD.
y_pack_bot = -(R + CH_OD / 2)
y_table_top = y_pack_bot - 45.0
y_floor = y_table_top - TABLE_T

V = App.Vector


def tube(od, idd, z_a, z_b, x=0.0, y=0.0):
    return G.cyl(od, z_a, z_b, x, y).cut(G.cyl(idd, z_a - 1, z_b + 1, x, y))


def station(x, y):
    """One closed-pose station silhouette: barrel + chamber + rail stubs + AirTAC lump."""
    barrel = tube(BARREL_OD, BARREL_ID, z_muzzle, z_breech)
    chamber = tube(CH_OD, CH_OD - 6.0, z_ch0, z_ch1)
    rxy = math.hypot(x, y) or 1.0
    ux, uy = x / rxy, y / rxy
    rail_y = -(CH_OD / 2 + 5.0)
    r1 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 20, -12.0, rail_y)
    r2 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 20, 12.0, rail_y)
    vent = Part.makeBox(18.0, 14.0, 30.0, V(-9.0, rail_y - 20.0, z_ch0 + 40.0))
    local = G.fuse_all([barrel, chamber, r1, r2, vent]).removeSplitter()
    ang = math.degrees(math.atan2(ux, uy))
    local.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
    local.translate(V(x, y, 0))
    return local


def bearing_race(z_a, z_b):
    """Outer race only — held by the cool end-plate boss."""
    return tube(BRG_OD, AXLE_OD + 0.3, z_a, z_b)


def spider_plate():
    """Front plate that spins with the barrels (classic Gatling spider)."""
    disc = G.cyl(PLATE_OD, z_plate0, z_plate1)
    disc = disc.cut(G.cyl(AXLE_OD + 0.3, z_plate0 - 1, z_plate1 + 1))
    for k in range(N):
        a = math.radians(k * 60.0)
        disc = disc.cut(G.cyl(BARREL_OD + 0.4, z_plate0 - 1, z_plate1 + 1,
                              R * math.cos(a), R * math.sin(a)))
    return disc.removeSplitter()


def end_frame(z_a, z_b):
    """Cool end plate: outer ring + boss around the race + thin spokes in gaps."""
    z0 = min(z_a, z_b) - (FRAME_T - (z_b - z_a)) / 2
    z1 = z0 + FRAME_T
    ring = G.cyl(FRAME_OD, z0, z1).cut(G.cyl(2 * PACK_CLEAR_R, z0 - 1, z1 + 1))
    boss = G.cyl(FRAME_ID, z0, z1).cut(G.cyl(BRG_OD / 2 + 0.3, z0 - 1, z1 + 1))
    # Thin spokes at 30° + k·60° (between stations) from boss to outer rim.
    spokes = []
    for k in range(N):
        a = math.radians(30.0 + k * 60.0)
        spoke = Part.makeBox(FRAME_OD / 2 - 2.0, SPOKE_W, SPOKE_T,
                             V(2.0, -SPOKE_W / 2, (z0 + z1) / 2 - SPOKE_T / 2))
        spoke.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(a))
        spoke = spoke.common(
            G.cyl(FRAME_OD - 2.0, z0 - 2, z1 + 2).cut(
                G.cyl(FRAME_ID - 2.0, z0 - 3, z1 + 3)))
        spokes.append(spoke)
    legs = []
    for sx in (-1.0, 1.0):
        h = FRAME_OD / 2 - 8.0 - y_table_top
        post = Part.makeBox(22.0, h, FRAME_T,
                            V(sx * (FRAME_OD / 2 - 14.0) - 11.0,
                              y_table_top - 1.0, z0))
        legs.append(post)
    return G.fuse_all([ring, boss] + spokes + legs).removeSplitter()


def bench_stand(pack_shape):
    """Cool frame: table + front/rear end plates + rear stator post.

    Notch frames where a spoke would hit a station (sketch only — cut the pack
    silhouette out of the stand).
    """
    z0 = z_axle0 - 25.0
    z1 = z_stub1 + 25.0
    table = Part.makeBox(FRAME_OD + 40.0, TABLE_T, z1 - z0,
                         V(-(FRAME_OD + 40.0) / 2, y_floor, z0))
    front = end_frame(z_brg_f0, z_brg_f1)
    rear = end_frame(z_brg_r0, z_brg_r1)
    rear_h = -16.0 - y_table_top
    stator_post = Part.makeBox(40.0, rear_h, 18.0,
                               V(-20.0, y_table_top - 1.0, z_stub1 - 4.0))
    stand = G.fuse_all([table, front, rear, stator_post]).removeSplitter()
    stand = stand.cut(pack_shape)
    return stand.removeSplitter()


# ---------------------------------------------------------------- solids
stations = []
for k in range(N):
    a = math.radians(k * 60.0)
    stations.append(station(R * math.cos(a), R * math.sin(a)))

axle = tube(AXLE_OD, AXLE_ID, z_axle0, z_axle1)
plate = spider_plate()
hub = tube(HUB_OD, AXLE_OD + 0.2, z_hub0, z_hub1)
for ang in (30.0, 210.0):
    a = math.radians(ang)
    hub = hub.fuse(G.cyl(5.0, z_hub1 - 2, z_rotor0 + 3,
                         19.0 * math.cos(a), 19.0 * math.sin(a)))
hub = hub.removeSplitter()

rotor = tube(ROTOR_OD, THROUGH, z_rotor0, z_rotor1)
for k in range(N):
    a = math.radians(k * 60.0)
    rotor = rotor.fuse(G.cyl(4.5, z_rotor0 - 3, z_rotor0,
                             19.0 * math.cos(a), 19.0 * math.sin(a)))
rotor = rotor.removeSplitter()

stator = tube(STATOR_OD, THROUGH, z_stator0, z_stator1)
for k in range(N):
    a = math.radians(k * 60.0 + 15.0)
    z_p = z_stator0 + 8.0 + k * 6.5
    stub = Part.makeCylinder(
        3.5, 8.0,
        V((STATOR_OD / 2 - 2) * math.cos(a),
          (STATOR_OD / 2 - 2) * math.sin(a), z_p),
        V(math.cos(a), math.sin(a), 0))
    stator = stator.fuse(stub)
stator = stator.fuse(G.cyl(STATOR_HUB_OD, z_stator1, z_stub1)).removeSplitter()

brg_f = bearing_race(z_brg_f0, z_brg_f1)
brg_r = bearing_race(z_brg_r0, z_brg_r1)
bracket = Part.makeBox(40.0, 40.0, 6.0, V(-20.0, -20.0, z_stub1))
bracket = bracket.cut(G.cyl(STATOR_HUB_OD + 0.4, z_stub1 - 1, z_stub1 + 8)).removeSplitter()

# ---------------------------------------------------------------- checks
pack = G.fuse_all(stations)
stand = bench_stand(pack)
checks = [
    ("six stations", len(stations) == 6),
    ("axle solid", G.single_solid(axle)),
    ("spider solid", G.single_solid(plate)),
    ("hub solid", G.single_solid(hub)),
    ("rotor solid", G.single_solid(rotor)),
    ("stator solid", G.single_solid(stator)),
    ("front bearing solid", G.single_solid(brg_f)),
    ("rear bearing solid", G.single_solid(brg_r)),
    ("stand solid", G.single_solid(stand)),
    ("axle clears front brg (%.2f)" % axle.distToShape(brg_f)[0],
     axle.distToShape(brg_f)[0] >= 0.1),
    ("axle clears rear brg (%.2f)" % axle.distToShape(brg_r)[0],
     axle.distToShape(brg_r)[0] >= 0.1),
    ("axle out of MQR bore",
     axle.common(G.cyl(THROUGH + 0.5, z_rotor0, z_stub1)).Volume < 1.0),
    ("hub/rotor gap %.1f mm" % (z_rotor0 - z_hub1),
     abs((z_rotor0 - z_hub1) - MQR_GAP) < 1e-6),
    ("axle spans pack (%.0f >= station %.0f)" % (AXLE_L, STATION_L),
     AXLE_L >= STATION_L),
    ("bearing span %.0f mm" % BRG_SPAN, BRG_SPAN >= 150.0),
    ("stations clear axle (%.1f mm)" % pack.distToShape(axle)[0],
     pack.distToShape(axle)[0] >= 5.0),
    ("stations clear hub (%.1f mm)" % pack.distToShape(hub)[0],
     pack.distToShape(hub)[0] >= 0.5),
    ("pack clears stand (common vol %.1f)" % pack.common(stand).Volume,
     pack.common(stand).Volume < 1.0),
]
report = [
    NAME,
    "  sketch                 : 6@R%.0f on bench; full axle + spider + hub + MQR" % R,
    "  rotates (warm)         : stations, spider, axle, hub, MQR rotor",
    "  fixed (cool)           : bench stand, 2 bearings, MQR stator, bracket",
    "  station                : barrel Ø%.0f x %.0f + chamber Ø%.0f x %.0f (≈ breech bench)"
    % (BARREL_OD, BARREL_L, CH_OD, CH_L),
    "  axle                   : Ø%.0f/%.0f x %.0f (nose→hub); bearing span %.0f"
    % (AXLE_OD, AXLE_ID, AXLE_L, BRG_SPAN),
    "  load path              : pack/spider -> axle -> bearings -> bench (MQR air only)",
    "  not drawn              : crank, hopper, hoses, chronograph, full station CAD",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["spin"] = ((0.95, 0.45, 0.12), 35)
FV.STYLES["spin_hub"] = ((0.85, 0.70, 0.20), 20)
FV.STYLES["spin_st"] = ((0.95, 0.55, 0.25), 60)
FV.STYLES["spin_plate"] = ((0.90, 0.50, 0.15), 30)
FV.STYLES["fixed"] = ((0.45, 0.70, 0.95), 35)
FV.STYLES["fixed_brg"] = ((0.30, 0.50, 0.80), 20)
FV.STYLES["fixed_frame"] = ((0.55, 0.60, 0.70), 35)
FV.STYLES["bench"] = ((0.50, 0.55, 0.60), 25)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Spins", "Station_%d" % (i + 1), st, "spin_st")
sc.add("Spins", "Spider", plate, "spin_plate")
sc.add("Spins", "Axle", axle, "spin")
sc.add("Spins", "Hub", hub, "spin_hub")
sc.add("Spins", "MQR_rotor", rotor, "spin")
sc.add("Fixed", "Bearing_front", brg_f, "fixed_brg")
sc.add("Fixed", "Bearing_rear", brg_r, "fixed_brg")
sc.add("Fixed", "MQR_stator", stator, "fixed")
sc.add("Fixed", "Stator_bracket", bracket, "fixed_frame")
sc.add("Fixed", "Bench_stand", stand, "bench")

for text, pos in [
    ("6 станций R%.0f (как на breech-стенде)" % R, (R + 45, 10, z_ch0 + 30)),
    ("передняя плита + вал %.0f мм" % AXLE_L, (R + 30, -20, 40)),
    ("подшипники → стойки стенда", (55, y_table_top + 30, (z_brg_f0 + z_brg_r1) / 2)),
    ("MQR только воздух", (50, 35, (z_rotor0 + z_stator1) / 2)),
    ("стол стенда", (0, y_floor - 15, (z_ch0 + z_ch1) / 2)),
    ("дуло →", (R + 25, 0, 25)),
]:
    sc.label("Labels", text, pos)

sc.finish(hidden_groups=("Labels",), opaque_groups=())
doc = sc.doc
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name):
    s = shape.copy()
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.15, AngularDeflection=0.25).write(
        os.path.join(OUT_DIR, name + ".stl"))


write(pack, "stations")
for n, s in (("spider", plate), ("axle", axle), ("hub", hub), ("mqr_rotor", rotor),
             ("mqr_stator", stator), ("bearing_front", brg_f),
             ("bearing_rear", brg_r), ("stator_bracket", bracket),
             ("bench_stand", stand)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling pack sketch has [FAIL] checks")
