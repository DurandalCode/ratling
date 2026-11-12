# -*- coding: utf-8 -*-
"""
Gatling MQR6 on pack axis — very rough 3D block sketch.

Four solids only: load axle, pack hub, MQR rotor, MQR stator (+ tiny
frame lug). Colours: warm = rotates with the pack, cool = stays on the frame.
No stations, no hoses, no bearings detail. Numbers from the MQR6 clone drawing
and PACK_PITCH = 68 (hub OD just under the station ring).

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
AXLE_L = 220.0               # stub through pack + past hub

HUB_OD = 50.0                # under station ring at R68
HUB_T = 18.0
HUB_BORE = AXLE_OD + 0.2

# MQR6 clone (docs/img/mqr6_dims.png), simplified to cylinders
ROTOR_OD = 46.0
ROTOR_L = 29.0               # rotor-side length on the drawing
STATOR_OD = 46.0
STATOR_L = 53.0              # body remaining after rotor (~82-29)
HUB_STATOR_OD = 20.0         # stator protruding hub
HUB_STATOR_L = 8.0
THROUGH = 6.0                # unused for load axle

# Lay along +Z: muzzle left (small z), frame right (large z).
# Axle ends in the hub — it does NOT enter the MQR through-hole Ø6.
z0 = 0.0
z_hub0 = z0 + AXLE_L - HUB_T
z_hub1 = z_hub0 + HUB_T                  # = z0 + AXLE_L
z_axle1 = z_hub1                         # axle stops at hub aft face
z_rotor0 = z_hub1
z_rotor1 = z_rotor0 + ROTOR_L
z_stator0 = z_rotor1
z_stator1 = z_stator0 + STATOR_L
z_stub0 = z_stator1
z_stub1 = z_stub0 + HUB_STATOR_L

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def tube(od, idd, z_a, z_b):
    return G.cyl(od, z_a, z_b).cut(G.cyl(idd, z_a - 1, z_b + 1))


# ---------------------------------------------------------------- solids
axle = tube(AXLE_OD, AXLE_ID, z0, z_axle1)
hub = tube(HUB_OD, HUB_BORE, z_hub0, z_hub1)
# two M4 bosses on hub face toward rotor (PCD 38) — just markers
for ang in (30.0, 210.0):
    a = math.radians(ang)
    hub = hub.fuse(G.cyl(6.0, z_hub1 - 2, z_hub1 + 4,
                         19.0 * math.cos(a), 19.0 * math.sin(a)))
hub = hub.removeSplitter()

rotor = tube(ROTOR_OD, THROUGH, z_rotor0, z_rotor1)
# six M5 port stubs on rotor face (PCD 38), facing -Z toward hub gap — markers on +Z face
for k in range(6):
    a = math.radians(k * 60.0)
    rotor = rotor.fuse(G.cyl(5.0, z_rotor0 - 6, z_rotor0,
                             19.0 * math.cos(a), 19.0 * math.sin(a)))
rotor = rotor.removeSplitter()

stator = tube(STATOR_OD, THROUGH, z_stator0, z_stator1)
# six M5 stubs on OD (staggered along Z like the drawing)
for k in range(6):
    a = math.radians(k * 60.0 + 15.0)
    z_p = z_stator0 + 8.0 + k * 7.0
    stub = Part.makeCylinder(4.0, 8.0,
                             V(STATOR_OD / 2 - 1, 0, z_p),
                             V(math.cos(a), math.sin(a), 0))
    # place around OD
    stub = Part.makeCylinder(4.0, 10.0,
                             V((STATOR_OD / 2 - 2) * math.cos(a),
                               (STATOR_OD / 2 - 2) * math.sin(a), z_p),
                             V(math.cos(a), math.sin(a), 0))
    stator = stator.fuse(stub)
stator_hub = G.cyl(HUB_STATOR_OD, z_stub0, z_stub1)
stator = stator.fuse(stator_hub).removeSplitter()

# Frame lug: flat plate behind stator, cool/fixed
frame = Part.makeBox(70.0, 70.0, 8.0, V(-35.0, -35.0, z_stub1))
frame = frame.cut(G.cyl(HUB_STATOR_OD + 0.4, z_stub1 - 1, z_stub1 + 10))
frame = frame.removeSplitter()

# ---------------------------------------------------------------- checks (sanity only)
checks = [
    ("axle single solid", G.single_solid(axle)),
    ("hub single solid", G.single_solid(hub)),
    ("rotor single solid", G.single_solid(rotor)),
    ("stator single solid", G.single_solid(stator)),
    ("hub clear of rotor face (touch ok)", hub.distToShape(rotor)[0] <= 0.05),
    ("rotor butts stator", rotor.distToShape(stator)[0] <= 0.05),
    ("axle does not enter MQR bore",
     axle.common(G.cyl(THROUGH + 0.5, z_rotor0, z_stub1)).Volume < 1.0),
]
report = [
    NAME,
    "  sketch                 : axle + hub + MQR rotor + MQR stator (block colours)",
    "  rotates (warm)         : axle, hub, rotor",
    "  fixed (cool)           : stator, frame lug",
    "  axle                   : Ø%.0f/%.0f x %.0f; stops before MQR (through Ø%.0f unused)"
    % (AXLE_OD, AXLE_ID, AXLE_L, THROUGH),
    "  hub                    : Ø%.0f x %.0f, 2xM4 markers on PCD 38" % (HUB_OD, HUB_T),
    "  MQR                    : rotor L %.0f + stator L %.0f, OD %.0f"
    % (ROTOR_L, STATOR_L, STATOR_OD),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

# Extra styles: warm = pack spin, cool = frame
FV.STYLES["spin"] = ((0.95, 0.45, 0.12), 25)      # orange — rotates
FV.STYLES["spin_hub"] = ((0.85, 0.70, 0.20), 20)  # amber hub
FV.STYLES["fixed"] = ((0.45, 0.70, 0.95), 35)     # blue — stays
FV.STYLES["fixed_frame"] = ((0.55, 0.60, 0.70), 40)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
sc.add("Spins", "Axle", axle, "spin")
sc.add("Spins", "Hub", hub, "spin_hub")
sc.add("Spins", "MQR_rotor", rotor, "spin")
sc.add("Fixed", "MQR_stator", stator, "fixed")
sc.add("Fixed", "Frame_lug", frame, "fixed_frame")

for text, pos in [
    ("КРУТИТСЯ: вал + ступица + ротор MQR", (40, 0, (z_hub0 + z_rotor1) / 2)),
    ("СТОИТ: статор MQR + кронштейн рамы", (40, 0, (z_stator0 + z_stub1) / 2)),
    ("вал НЕ в Ø6 MQR", (30, 25, z_rotor0 + 5)),
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
             ("mqr_stator", stator), ("frame_lug", frame)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling mqr axis sketch has [FAIL] checks")
