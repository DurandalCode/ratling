# -*- coding: utf-8 -*-
"""
Gatling pack — rough 3D block sketch of the whole gun.

Six breech stations on a hex at PACK_PITCH, common axle on two bearing stands,
hub, MQR rotor/stator. Warm = spins with the pack, cool = stays on the frame.
No crank, hopper, or hoses — just the silhouette so the layout reads.

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
CH_OD, CH_L = 50.0, 130.0    # fat coax chamber block
QEV_GAP = 8.0                # rear plug ears / carriage lump behind chamber

AXLE_OD, AXLE_ID = 16.0, 10.0
BRG_OD, BRG_T = 36.0, 14.0
BRG_PAD = 28.0
HUB_OD, HUB_T = 50.0, 18.0
ROTOR_OD, ROTOR_L = 46.0, 29.0
STATOR_OD, STATOR_L = 46.0, 53.0
STATOR_HUB_OD, STATOR_HUB_L = 20.0, 8.0
THROUGH = 6.0
MQR_GAP = 2.0

# +Z toward muzzle. Hub/MQR sit behind the QEV ring.
z_muzzle = 0.0
z_breech = BARREL_L
z_ch0 = z_breech
z_ch1 = z_ch0 + CH_L
z_qev_aft = z_ch1 + QEV_GAP

z_hub1 = z_qev_aft + 25.0
z_hub0 = z_hub1 - HUB_T
z_axle0 = z_breech - 40.0          # axle starts under the barrels
z_axle1 = z_hub1
z_brg_f0 = z_axle0 + 10.0
z_brg_f1 = z_brg_f0 + BRG_T
z_brg_r1 = z_hub0 - 10.0
z_brg_r0 = z_brg_r1 - BRG_T
z_rotor0 = z_hub1 + MQR_GAP
z_rotor1 = z_rotor0 + ROTOR_L
z_stator0 = z_rotor1
z_stator1 = z_stator0 + STATOR_L
z_stub1 = z_stator1 + STATOR_HUB_L

V = App.Vector


def tube(od, idd, z_a, z_b, x=0.0, y=0.0):
    return G.cyl(od, z_a, z_b, x, y).cut(G.cyl(idd, z_a - 1, z_b + 1, x, y))


def placed(shape, x, y):
    s = shape.copy()
    s.translate(V(x, y, 0))
    return s


def station(x, y):
    """One closed-pose station: barrel + chamber + two rail stubs + AirTAC lump."""
    barrel = tube(BARREL_OD, BARREL_ID, z_muzzle, z_breech)
    chamber = tube(CH_OD, CH_OD - 6.0, z_ch0, z_ch1)
    # rails under chamber, toward pack axis (local -radial ≈ toward origin)
    # local frame: station at (x,y); "down to axis" is -radial
    rxy = math.hypot(x, y) or 1.0
    ux, uy = x / rxy, y / rxy
    # local +Y feed away from axis = +radial; rails at local -Y
    rail_y = -(CH_OD / 2 + 5.0)
    # build rails in station-local then rotate into pack
    r1 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 20, -12.0, rail_y)
    r2 = G.cyl(8.0, z_ch0 - 10, z_ch1 + 20, 12.0, rail_y)
    vent = Part.makeBox(18.0, 14.0, 30.0, V(-9.0, rail_y - 20.0, z_ch0 + 40.0))
    local = G.fuse_all([barrel, chamber, r1, r2, vent]).removeSplitter()
    # rotate so local +Y (feed) points outward (+radial), local -Y toward axis
    # default local Y is global Y; need local Y → radial direction (ux,uy)
    # angle from +Y to radial: atan2(ux, uy) ... Placement rotate around Z
    ang = math.degrees(math.atan2(ux, uy))  # +Y → radial
    local.rotate(V(0, 0, 0), V(0, 0, 1), -ang)
    local.translate(V(x, y, 0))
    return local


def bearing(z_a, z_b):
    race = tube(BRG_OD, AXLE_OD + 0.3, z_a, z_b)
    y_top = -BRG_OD / 2 + 1.5
    foot = Part.makeBox(BRG_PAD, 10.0, z_b - z_a,
                        V(-BRG_PAD / 2, y_top - 10.0, z_a))
    return race.fuse(foot).removeSplitter()


# ---------------------------------------------------------------- solids
stations = []
for k in range(N):
    a = math.radians(k * 60.0)
    stations.append(station(R * math.cos(a), R * math.sin(a)))

axle = tube(AXLE_OD, AXLE_ID, z_axle0, z_axle1)
hub = tube(HUB_OD, AXLE_OD + 0.2, z_hub0, z_hub1)
for ang in (30.0, 210.0):
    a = math.radians(ang)
    hub = hub.fuse(G.cyl(5.0, z_hub1 - 2, z_rotor0 + 3,
                         19.0 * math.cos(a), 19.0 * math.sin(a)))
hub = hub.removeSplitter()

rotor = tube(ROTOR_OD, THROUGH, z_rotor0, z_rotor1)
for k in range(6):
    a = math.radians(k * 60.0)
    rotor = rotor.fuse(G.cyl(4.5, z_rotor0 - 3, z_rotor0,
                             19.0 * math.cos(a), 19.0 * math.sin(a)))
rotor = rotor.removeSplitter()

stator = tube(STATOR_OD, THROUGH, z_stator0, z_stator1)
for k in range(6):
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
bracket = Part.makeBox(40.0, 40.0, 6.0, V(-20.0, -20.0, z_stub1))
bracket = bracket.cut(G.cyl(STATOR_HUB_OD + 0.4, z_stub1 - 1, z_stub1 + 8)).removeSplitter()

# ---------------------------------------------------------------- checks
pack = G.fuse_all(stations)
checks = [
    ("six stations", len(stations) == 6),
    ("axle solid", G.single_solid(axle)),
    ("hub solid", G.single_solid(hub)),
    ("rotor solid", G.single_solid(rotor)),
    ("stator solid", G.single_solid(stator)),
    ("front bearing solid", G.single_solid(brg_f)),
    ("rear bearing solid", G.single_solid(brg_r)),
    ("axle clears front brg (%.2f)" % axle.distToShape(brg_f)[0],
     axle.distToShape(brg_f)[0] >= 0.1),
    ("axle clears rear brg (%.2f)" % axle.distToShape(brg_r)[0],
     axle.distToShape(brg_r)[0] >= 0.1),
    ("axle out of MQR bore",
     axle.common(G.cyl(THROUGH + 0.5, z_rotor0, z_stub1)).Volume < 1.0),
    ("hub/rotor gap %.1f mm" % (z_rotor0 - z_hub1),
     abs((z_rotor0 - z_hub1) - MQR_GAP) < 1e-6),
    ("stations clear axle (%.1f mm)" % pack.distToShape(axle)[0],
     pack.distToShape(axle)[0] >= 5.0),
    ("stations clear hub (%.1f mm)" % pack.distToShape(hub)[0],
     pack.distToShape(hub)[0] >= 0.5),
]
report = [
    NAME,
    "  sketch                 : 6 stations @ R%.0f + axle on 2 stands + hub + MQR" % R,
    "  rotates (warm)         : stations, axle, hub, MQR rotor",
    "  fixed (cool)           : 2 bearing stands, MQR stator, stator bracket",
    "  station                : barrel Ø%.0f x %.0f + chamber Ø%.0f x %.0f"
    % (BARREL_OD, BARREL_L, CH_OD, CH_L),
    "  load path              : pack -> hub -> axle -> bearings (MQR air only)",
    "  not drawn              : crank, hopper, hoses, chronograph",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["spin"] = ((0.95, 0.45, 0.12), 35)
FV.STYLES["spin_hub"] = ((0.85, 0.70, 0.20), 25)
FV.STYLES["spin_st"] = ((0.95, 0.55, 0.25), 55)   # stations — lighter so axis reads
FV.STYLES["fixed"] = ((0.45, 0.70, 0.95), 40)
FV.STYLES["fixed_brg"] = ((0.35, 0.55, 0.85), 25)
FV.STYLES["fixed_frame"] = ((0.55, 0.60, 0.70), 40)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Spins", "Station_%d" % (i + 1), st, "spin_st")
sc.add("Spins", "Axle", axle, "spin")
sc.add("Spins", "Hub", hub, "spin_hub")
sc.add("Spins", "MQR_rotor", rotor, "spin")
sc.add("Fixed", "Bearing_front", brg_f, "fixed_brg")
sc.add("Fixed", "Bearing_rear", brg_r, "fixed_brg")
sc.add("Fixed", "MQR_stator", stator, "fixed")
sc.add("Fixed", "Stator_bracket", bracket, "fixed_frame")

for text, pos in [
    ("6 станций R%.0f (крутятся)" % R, (R + 40, 0, z_ch0 + 40)),
    ("вал на 2 опорах — не на MQR", (40, -50, (z_brg_f0 + z_brg_r1) / 2)),
    ("MQR: только воздух", (40, 40, (z_rotor0 + z_stator1) / 2)),
    ("дуло →", (R + 20, 0, 40)),
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
for n, s in (("axle", axle), ("hub", hub), ("mqr_rotor", rotor),
             ("mqr_stator", stator), ("bearing_front", brg_f),
             ("bearing_rear", brg_r), ("stator_bracket", bracket)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling pack sketch has [FAIL] checks")
