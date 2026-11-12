# -*- coding: utf-8 -*-
"""
Gatling MQR6 on pack axis — rough 3D block sketch.

Load path: axle sits in two frame bearings; hub (and later the pack) rides on
the axle. MQR rotor bolts to the hub face for air only — the valve is not the
shaft. Colours: warm = rotates with the pack, cool = stays on the frame.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/mqr_axis_sketch.py').read())"

Exports: exports/gatling_mqr_axis_sketch/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_mqr_axis_sketch")
NAME = "gatling_mqr_axis_sketch"

# ---------------------------------------------------------------- numbers (mm)
AXLE_OD = 16.0
AXLE_ID = 10.0
AXLE_L = 220.0

HUB_OD = 50.0
HUB_T = 18.0
HUB_BORE = AXLE_OD + 0.2

BRG_OD = 36.0                # plain ring race (fixed)
BRG_ID = AXLE_OD + 0.3       # clearance on axle
BRG_T = 14.0
BRG_FOOT_W = 28.0            # small pad under each race — no chassis rail

# MQR6 clone (docs/img/mqr6_dims.png), simplified
ROTOR_OD = 46.0
ROTOR_L = 29.0
STATOR_OD = 46.0
STATOR_L = 53.0
HUB_STATOR_OD = 20.0
HUB_STATOR_L = 8.0
THROUGH = 6.0
MQR_GAP = 2.0                # visual air gap hub face → rotor (bolts span it)

# +Z toward the frame. Axle ends in the hub — never enters MQR Ø6.
z0 = 0.0
z_brg_f0 = z0 + 12.0
z_brg_f1 = z_brg_f0 + BRG_T
z_hub0 = z0 + AXLE_L - HUB_T
z_hub1 = z_hub0 + HUB_T
z_axle1 = z_hub1
z_brg_r1 = z_hub0 - 8.0
z_brg_r0 = z_brg_r1 - BRG_T
z_rotor0 = z_hub1 + MQR_GAP
z_rotor1 = z_rotor0 + ROTOR_L
z_stator0 = z_rotor1
z_stator1 = z_stator0 + STATOR_L
z_stub0 = z_stator1
z_stub1 = z_stub0 + HUB_STATOR_L

V = App.Vector


def tube(od, idd, z_a, z_b, x=0.0, y=0.0):
    return G.cyl(od, z_a, z_b, x, y).cut(G.cyl(idd, z_a - 1, z_b + 1, x, y))


def bearing(z_a, z_b):
    """Fixed outer race + tiny pad below — separate stands, not a long frame."""
    race = tube(BRG_OD, BRG_ID, z_a, z_b)
    y_top = -BRG_OD / 2 + 1.5
    foot = Part.makeBox(BRG_FOOT_W, 10.0, z_b - z_a,
                        V(-BRG_FOOT_W / 2, y_top - 10.0, z_a))
    return race.fuse(foot).removeSplitter()


# ---------------------------------------------------------------- spinning
axle = tube(AXLE_OD, AXLE_ID, z0, z_axle1)
hub = tube(HUB_OD, HUB_BORE, z_hub0, z_hub1)
for ang in (30.0, 210.0):
    a = math.radians(ang)
    # bolt markers toward the rotor (span the MQR_GAP)
    hub = hub.fuse(G.cyl(5.0, z_hub1 - 2, z_rotor0 + 3,
                         19.0 * math.cos(a), 19.0 * math.sin(a)))
hub = hub.removeSplitter()

rotor = tube(ROTOR_OD, THROUGH, z_rotor0, z_rotor1)
for k in range(6):
    a = math.radians(k * 60.0)
    rotor = rotor.fuse(G.cyl(5.0, z_rotor0 - 4, z_rotor0,
                             19.0 * math.cos(a), 19.0 * math.sin(a)))
rotor = rotor.removeSplitter()

# ---------------------------------------------------------------- fixed
brg_f = bearing(z_brg_f0, z_brg_f1)
brg_r = bearing(z_brg_r0, z_brg_r1)

stator = tube(STATOR_OD, THROUGH, z_stator0, z_stator1)
for k in range(6):
    a = math.radians(k * 60.0 + 15.0)
    z_p = z_stator0 + 8.0 + k * 7.0
    stub = Part.makeCylinder(
        4.0, 10.0,
        V((STATOR_OD / 2 - 2) * math.cos(a),
          (STATOR_OD / 2 - 2) * math.sin(a), z_p),
        V(math.cos(a), math.sin(a), 0))
    stator = stator.fuse(stub)
stator = stator.fuse(G.cyl(HUB_STATOR_OD, z_stub0, z_stub1)).removeSplitter()

# Stator bracket only: small plate on the Ø20 hub. No rail between bearings.
bracket = Part.makeBox(40.0, 40.0, 6.0, V(-20.0, -20.0, z_stub1))
bracket = bracket.cut(G.cyl(HUB_STATOR_OD + 0.4, z_stub1 - 1, z_stub1 + 8))
bracket = bracket.removeSplitter()

# ---------------------------------------------------------------- checks
checks = [
    ("axle single solid", G.single_solid(axle)),
    ("hub single solid", G.single_solid(hub)),
    ("rotor single solid", G.single_solid(rotor)),
    ("stator single solid", G.single_solid(stator)),
    ("front bearing single solid", G.single_solid(brg_f)),
    ("rear bearing single solid", G.single_solid(brg_r)),
    ("stator bracket single solid", G.single_solid(bracket)),
    ("axle clears front bearing race (%.2f mm)" % axle.distToShape(brg_f)[0],
     axle.distToShape(brg_f)[0] >= 0.1),
    ("axle clears rear bearing race (%.2f mm)" % axle.distToShape(brg_r)[0],
     axle.distToShape(brg_r)[0] >= 0.1),
    ("hub clear of rear bearing (%.1f mm)" % hub.distToShape(brg_r)[0],
     hub.distToShape(brg_r)[0] >= 5.0),
    ("hub/rotor faces spaced %.1f mm (bolts may bridge)" % (z_rotor0 - z_hub1),
     abs((z_rotor0 - z_hub1) - MQR_GAP) < 1e-6),
    ("rotor butts stator", rotor.distToShape(stator)[0] <= 0.05),
    ("axle does not enter MQR bore",
     axle.common(G.cyl(THROUGH + 0.5, z_rotor0, z_stub1)).Volume < 1.0),
    ("stator bracket present", bracket.Volume > 1000),
]
report = [
    NAME,
    "  sketch                 : axle on 2 tiny stands; hub; MQR; small stator plate",
    "  rotates (warm)         : axle, hub, MQR rotor",
    "  fixed (cool)           : 2 bearing stands, MQR stator, stator bracket",
    "  load path              : pack/hub -> axle -> 2 bearings (MQR not in path)",
    "  axle                   : Ø%.0f/%.0f x %.0f; stops in hub; MQR through Ø%.0f unused"
    % (AXLE_OD, AXLE_ID, AXLE_L, THROUGH),
    "  bearings               : 2x Ø%.0f x %.0f, span %.0f mm (no chassis rail)"
    % (BRG_OD, BRG_T, z_brg_r0 - z_brg_f1),
    "  hub / MQR gap          : %.0f mm (2xM4 markers span it)" % MQR_GAP,
    "  MQR                    : rotor L %.0f + stator L %.0f, OD %.0f"
    % (ROTOR_L, STATOR_L, STATOR_OD),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["spin"] = ((0.95, 0.45, 0.12), 25)
FV.STYLES["spin_hub"] = ((0.85, 0.70, 0.20), 20)
FV.STYLES["fixed"] = ((0.45, 0.70, 0.95), 40)
FV.STYLES["fixed_brg"] = ((0.35, 0.55, 0.85), 30)
FV.STYLES["fixed_frame"] = ((0.55, 0.60, 0.70), 45)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
sc.add("Spins", "Axle", axle, "spin")
sc.add("Spins", "Hub", hub, "spin_hub")
sc.add("Spins", "MQR_rotor", rotor, "spin")
sc.add("Fixed", "Bearing_front", brg_f, "fixed_brg")
sc.add("Fixed", "Bearing_rear", brg_r, "fixed_brg")
sc.add("Fixed", "MQR_stator", stator, "fixed")
sc.add("Fixed", "Stator_bracket", bracket, "fixed_frame")

for text, pos in [
    ("КРУТИТСЯ: вал + ступица + ротор", (55, 0, (z_hub0 + z_rotor1) / 2)),
    ("СТОИТ: 2 опоры + статор + пластина", (55, 0, (z_stator0 + z_stub1) / 2)),
    ("опора = 2 подшипника, не MQR", (50, -40, (z_brg_f1 + z_brg_r0) / 2)),
    ("MQR только воздух (зазор %.0f мм)" % MQR_GAP, (50, 30, z_rotor0)),
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
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.1, AngularDeflection=0.2).write(
        os.path.join(OUT_DIR, name + ".stl"))


for n, s in (("axle", axle), ("hub", hub), ("mqr_rotor", rotor),
             ("mqr_stator", stator), ("bearing_front", brg_f),
             ("bearing_rear", brg_r), ("stator_bracket", bracket)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling mqr axis sketch has [FAIL] checks")
