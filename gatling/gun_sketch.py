# -*- coding: utf-8 -*-
"""
Gatling finished-product silhouette (not a bench).

Reads as an assembled gun: 6 QEV stations on R68, front/rear spiders, breech
casing over hub+MQR, top pellet hopper, rear hand crank, light field carriage
(wheels + trail + trunnions). Warm = spins with the pack, cool = stays on the
carriage. Block sketch only — no full station CAD, hoses, or chronograph.

Visual cues (refs, not copies):
  Civil War / 1862–83 Gatling — barrel cluster on shaft, breech casing, top
  feed, rear crank, wheeled carriage with trail.
  Modern M134 — compact 6-barrel clamp + enclosed receiver at the breech.
  Our kit — fat-coax chambers Ø50×130, barrels Ø25×180, MQR air only.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/gun_sketch.py').read())"

Exports: exports/gatling_gun_sketch/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_gun_sketch")
NAME = "gatling_gun_sketch"

# ---------------------------------------------------------------- pack (mm)
N = 6
R = 68.0                     # PACK_PITCH
BARREL_OD, BARREL_ID = 25.0, 23.8
BARREL_L = 180.0
CH_OD, CH_L = 50.0, 130.0
QEV_GAP = 8.0

AXLE_OD, AXLE_ID = 16.0, 10.0
HUB_OD, HUB_T = 50.0, 18.0
ROTOR_OD, ROTOR_L = 46.0, 29.0
STATOR_OD, STATOR_L = 46.0, 53.0
STATOR_HUB_OD, STATOR_HUB_L = 20.0, 8.0
THROUGH = 6.0
MQR_GAP = 2.0
BRG_OD, BRG_T = 36.0, 14.0

PLATE_T = 10.0
PLATE_OD = 2 * R + BARREL_OD + 12.0
CLAMP_OD = 2 * R + BARREL_OD + 8.0   # modern-style front barrel clamp ring

# +Z toward muzzle.
z_muzzle = 0.0
z_plate0 = 0.0
z_plate1 = PLATE_T
z_clamp0 = 55.0
z_clamp1 = z_clamp0 + 8.0
z_breech = BARREL_L
z_ch0 = z_breech
z_ch1 = z_ch0 + CH_L
z_qev_aft = z_ch1 + QEV_GAP

z_hub1 = z_qev_aft + 20.0
z_hub0 = z_hub1 - HUB_T
z_axle0 = z_plate0 - 6.0
z_axle1 = z_hub1
z_brg_f0 = z_plate1 + 6.0
z_brg_f1 = z_brg_f0 + BRG_T
z_brg_r1 = z_hub0 - 8.0
z_brg_r0 = z_brg_r1 - BRG_T
z_rotor0 = z_hub1 + MQR_GAP
z_rotor1 = z_rotor0 + ROTOR_L
z_stator0 = z_rotor1
z_stator1 = z_stator0 + STATOR_L
z_stub1 = z_stator1 + STATOR_HUB_L

AXLE_L = z_axle1 - z_axle0
PACK_R = R + CH_OD / 2 + 6.0

# Carriage / product frame (cool). Machine frame: +X up, +Y left (crank), +Z muzzle
# (see ratling/fcview.py VIEW_ROT).
CASE_OD = 2 * PACK_R + 28.0          # breech casing around rear cluster
CASE_T = 4.0
HOPPER_W, HOPPER_D, HOPPER_H = 70.0, 55.0, 85.0
CRANK_ARM, CRANK_GRIP = 100.0, 55.0
WHEEL_OD, WHEEL_T = 220.0, 28.0
TRAIL_L, TRAIL_W, TRAIL_T = 380.0, 36.0, 22.0
CHEEK_T = 12.0

z_carriage = (z_ch0 + z_ch1) / 2
# Ground is −X; carriage axle across ±Y.
x_axle_car = -(PACK_R + 55.0)
x_ground = x_axle_car - WHEEL_OD / 2

V = App.Vector


def tube(od, idd, z_a, z_b, x=0.0, y=0.0):
    return G.cyl(od, z_a, z_b, x, y).cut(G.cyl(idd, z_a - 1, z_b + 1, x, y))


def station(x, y):
    barrel = tube(BARREL_OD, BARREL_ID, z_muzzle, z_breech)
    chamber = tube(CH_OD, CH_OD - 6.0, z_ch0, z_ch1)
    rxy = math.hypot(x, y) or 1.0
    ux, uy = x / rxy, y / rxy
    rail_y = -(CH_OD / 2 + 5.0)
    r1 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 15, -12.0, rail_y)
    r2 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 15, 12.0, rail_y)
    local = G.fuse_all([barrel, chamber, r1, r2]).removeSplitter()
    ang = math.degrees(math.atan2(ux, uy))
    local.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
    local.translate(V(x, y, 0))
    return local


def spider(z0, z1, od, hole_od):
    disc = G.cyl(od, z0, z1).cut(G.cyl(AXLE_OD + 0.3, z0 - 1, z1 + 1))
    for k in range(N):
        a = math.radians(k * 60.0)
        disc = disc.cut(G.cyl(hole_od, z0 - 1, z1 + 1,
                              R * math.cos(a), R * math.sin(a)))
    return disc.removeSplitter()


def bearing(z_a, z_b):
    return tube(BRG_OD, AXLE_OD + 0.3, z_a, z_b)


# ---------------------------------------------------------------- spinning pack
stations = []
for k in range(N):
    a = math.radians(k * 60.0)
    stations.append(station(R * math.cos(a), R * math.sin(a)))
pack = G.fuse_all(stations)

front_spider = spider(z_plate0, z_plate1, PLATE_OD, BARREL_OD + 0.4)
front_clamp = spider(z_clamp0, z_clamp1, CLAMP_OD, BARREL_OD + 0.3)
axle = tube(AXLE_OD, AXLE_ID, z_axle0, z_axle1)
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

# ---------------------------------------------------------------- cool product body
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

brg_f = bearing(z_brg_f0, z_brg_f1)
brg_r = bearing(z_brg_r0, z_brg_r1)

# Breech casing — classic enclosed receiver over hub/MQR (Bulldog / 1870s cue).
z_case0 = z_hub0 - 15.0
z_case1 = z_stub1 + 10.0
casing = G.cyl(CASE_OD, z_case0, z_case1).cut(
    G.cyl(CASE_OD - 2 * CASE_T, z_case0 - 1, z_case1 + 1))
casing = casing.cut(G.cyl(2 * PACK_R + 4.0, z_case0 - 2, z_hub0 + 2))
# Top (+X) slot for hopper feed.
casing = casing.cut(Part.makeBox(CASE_OD, HOPPER_W + 10.0, 45.0,
                                 V(10.0, -(HOPPER_W + 10.0) / 2, z_hub0 - 5.0)))
rear_disk = G.cyl(CASE_OD, z_stub1, z_stub1 + 8.0).cut(
    G.cyl(STATOR_HUB_OD + 0.5, z_stub1 - 1, z_stub1 + 10))
casing = casing.fuse(rear_disk).removeSplitter()

# Cheek plates on ±Y + trunnion pins (carry the gun on the carriage).
cheek_z0 = z_case0 - 5.0
cheek_z1 = z_case1 + 5.0
cheeks = []
for sy in (-1.0, 1.0):
    y0 = (-CASE_OD / 2 - CHEEK_T - 2.0) if sy < 0 else (CASE_OD / 2 + 2.0)
    cheek = Part.makeBox(CASE_OD * 0.42, CHEEK_T, cheek_z1 - cheek_z0,
                         V(-CASE_OD * 0.18, y0, cheek_z0))
    pin = Part.makeCylinder(10.0, 20.0,
                            V(0, y0 + (CHEEK_T if sy > 0 else 0), z_carriage),
                            V(0, sy, 0))
    cheeks.append(cheek.fuse(pin))
cheeks_s = G.fuse_all(cheeks).removeSplitter()

# Top hopper on +X (gravity feed — Civil War cue; pellets for us).
hopper_x0 = PACK_R + 5.0
hopper = Part.makeBox(HOPPER_H, HOPPER_W, HOPPER_D,
                      V(hopper_x0, -HOPPER_W / 2, z_hub0 - 5.0))
mouth = Part.makeBox(45.0, 40.0, 50.0,
                     V(hopper_x0 - 25.0, -20.0, z_hub0))
hopper = hopper.fuse(mouth).removeSplitter()

# Rear hand crank on +Y (left when looking at the muzzle — classic cue).
crank_z = z_stub1 + 2.0
crank_hub = Part.makeCylinder(16.0, 22.0, V(0, CASE_OD / 2 - 5.0, crank_z), V(0, 1, 0))
arm = Part.makeBox(12.0, CRANK_ARM, 12.0,
                   V(-6.0, CASE_OD / 2 + 8.0, crank_z - 6.0))
grip = Part.makeCylinder(8.0, CRANK_GRIP,
                         V(0, CASE_OD / 2 + CRANK_ARM + 5.0, crank_z),
                         V(0, 1, 0))
crank = crank_hub.fuse(arm).fuse(grip).removeSplitter()

# Field carriage: axle along Y, wheels at ±Y, trail aft (+Z).
track = CASE_OD / 2 + 55.0
car_axle = Part.makeCylinder(10.0, 2 * track + 40.0,
                             V(x_axle_car, -track - 20.0, z_carriage),
                             V(0, 1, 0))
wheels = []
for sy in (-1.0, 1.0):
    wy = sy * track
    tire = Part.makeCylinder(WHEEL_OD / 2, WHEEL_T,
                             V(x_axle_car, wy - sy * WHEEL_T / 2, z_carriage),
                             V(0, sy, 0))
    tire = tire.cut(Part.makeCylinder(
        WHEEL_OD / 2 - 16.0, WHEEL_T + 4,
        V(x_axle_car, wy - sy * (WHEEL_T / 2 + 1), z_carriage), V(0, sy, 0)))
    hub_w = Part.makeCylinder(22.0, WHEEL_T + 6,
                              V(x_axle_car, wy - sy * (WHEEL_T / 2 + 1), z_carriage),
                              V(0, sy, 0))
    spokes = []
    for ang in (0.0, 45.0, 90.0, 135.0):
        sp = Part.makeBox(WHEEL_OD - 40.0, WHEEL_T - 6.0, 8.0,
                          V(x_axle_car - (WHEEL_OD - 40.0) / 2,
                            wy - sy * (WHEEL_T / 2 - 3),
                            z_carriage - 4.0))
        sp.rotate(V(x_axle_car, wy, z_carriage), V(0, 1, 0), ang)
        spokes.append(sp)
    wheels.append(G.fuse_all([tire, hub_w] + spokes))
trail = Part.makeBox(TRAIL_T, TRAIL_W, TRAIL_L,
                     V(x_axle_car - 8.0, -TRAIL_W / 2, z_carriage + 10.0))
uprights = []
for sy in (-1.0, 1.0):
    up = Part.makeBox(abs(x_axle_car) + 10.0, 16.0, 28.0,
                      V(x_axle_car,
                        sy * (CASE_OD / 2 + 8.0) - 8.0,
                        z_carriage - 14.0))
    uprights.append(up)
carriage = Part.makeCompound([car_axle, trail] + uprights + wheels)

cheeks_s = cheeks_s.cut(pack).removeSplitter()
casing = casing.cut(pack).removeSplitter()

# ---------------------------------------------------------------- checks
checks = [
    ("six stations", len(stations) == 6),
    ("axle solid", G.single_solid(axle)),
    ("hub solid", G.single_solid(hub)),
    ("casing solid", G.single_solid(casing)),
    ("hopper solid", G.single_solid(hopper)),
    ("crank solid", G.single_solid(crank)),
    ("carriage present", carriage.Volume > 1e5),
    ("axle spans pack (%.0f)" % AXLE_L, AXLE_L >= (z_qev_aft - z_muzzle)),
    ("axle out of MQR bore",
     axle.common(G.cyl(THROUGH + 0.5, z_rotor0, z_stub1)).Volume < 1.0),
    ("pack clears casing (vol %.1f)" % pack.common(casing).Volume,
     pack.common(casing).Volume < 1.0),
    ("pack clears carriage (vol %.1f)" % pack.common(carriage).Volume,
     pack.common(carriage).Volume < 1.0),
    ("hub/rotor gap", abs((z_rotor0 - z_hub1) - MQR_GAP) < 1e-6),
]
report = [
    NAME,
    "  sketch                 : finished gatling product (not a bench)",
    "  rotates (warm)         : stations, spiders/clamp, axle, hub, MQR rotor",
    "  fixed (cool)           : breech casing, hopper, crank, cheeks, carriage, MQR stator",
    "  pack                   : 6@R%.0f, barrel Ø%.0f×%.0f + chamber Ø%.0f×%.0f"
    % (R, BARREL_OD, BARREL_L, CH_OD, CH_L),
    "  axle                   : Ø%.0f/%.0f × %.0f mm (nose→hub)" % (AXLE_OD, AXLE_ID, AXLE_L),
    "  product cues           : casing + hopper + crank + wheeled trail carriage",
    "  refs                   : 1862–83 Gatling carriage/feed/crank; M134 6-barrel clamp",
    "  not drawn              : hoses, AirTAC detail, chronograph, full station CAD",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["spin"] = ((0.92, 0.48, 0.16), 40)
FV.STYLES["spin_hub"] = ((0.85, 0.70, 0.20), 20)
FV.STYLES["spin_st"] = ((0.90, 0.55, 0.28), 55)
FV.STYLES["spin_plate"] = ((0.80, 0.45, 0.18), 30)
FV.STYLES["fixed"] = ((0.40, 0.62, 0.88), 35)
FV.STYLES["fixed_case"] = ((0.55, 0.48, 0.38), 40)   # bronze-ish breech casing
FV.STYLES["fixed_wood"] = ((0.55, 0.38, 0.22), 25)  # trail / carriage wood
FV.STYLES["fixed_iron"] = ((0.45, 0.48, 0.52), 30)
FV.STYLES["fixed_hop"] = ((0.35, 0.55, 0.40), 35)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Spins", "Station_%d" % (i + 1), st, "spin_st")
sc.add("Spins", "Spider_front", front_spider, "spin_plate")
sc.add("Spins", "Clamp_front", front_clamp, "spin_plate")
sc.add("Spins", "Axle", axle, "spin")
sc.add("Spins", "Hub", hub, "spin_hub")
sc.add("Spins", "MQR_rotor", rotor, "spin")
sc.add("Fixed", "Bearing_front", brg_f, "fixed")
sc.add("Fixed", "Bearing_rear", brg_r, "fixed")
sc.add("Fixed", "MQR_stator", stator, "fixed")
sc.add("Fixed", "Breech_casing", casing, "fixed_case")
sc.add("Fixed", "Hopper", hopper, "fixed_hop")
sc.add("Fixed", "Crank", crank, "fixed_iron")
sc.add("Fixed", "Cheeks", cheeks_s, "fixed_iron")
sc.add("Fixed", "Carriage", carriage, "fixed_wood")

for text, pos in [
    ("6 стволов R%.0f (QEV)" % R, (30, R + 50, z_ch0)),
    ("бункер пульки", (hopper_x0 + HOPPER_H + 15, 0, z_hub0 + 20)),
    ("казённый кожух + MQR", (0, CASE_OD / 2 + 35, (z_case0 + z_case1) / 2)),
    ("рукоять", (20, CASE_OD / 2 + CRANK_ARM + 30, crank_z)),
    ("лафет", (x_ground + 30, 0, z_carriage + TRAIL_L * 0.55)),
    ("дуло →", (20, R + 25, 30)),
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
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.2, AngularDeflection=0.3).write(
        os.path.join(OUT_DIR, name + ".stl"))


write(pack, "stations")
for n, s in (("axle", axle), ("hub", hub), ("mqr_rotor", rotor), ("mqr_stator", stator),
             ("breech_casing", casing), ("hopper", hopper), ("crank", crank),
             ("carriage", carriage), ("cheeks", cheeks_s),
             ("spider_front", front_spider), ("clamp_front", front_clamp)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling gun sketch has [FAIL] checks")
