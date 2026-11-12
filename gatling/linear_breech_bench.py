# -*- coding: utf-8 -*-
"""
Bench for one Gatling linear-breech station: small feet under the rails.

Loads gatling/linear_breech.py as a library. The aluminium rails are the beam;
print only two feet (front under the barrel clamp, rear aft of the open
carriage) plus a T-handle on the carriage. No long floor slab.

Prove on the bench: open → drop a pellet from +Y → close (AirTAC dumps) →
module fires. Crank / hopper / rotary union stay off this stand.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech_bench.py').read())"

Exports: exports/gatling_linear_breech_bench/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech_bench")
NAME = "gatling_linear_breech_bench"

# ---------------------------------------------------------------- station as library
GATLING_LINEAR_BREECH_LIBRARY = True
SHOW_OPEN = True
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech_bench")
NAME = "gatling_linear_breech_bench"

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector

# ---------------------------------------------------------------- feet parameters
# Two discrete feet — rails span between them. Wide enough in X so a hand shove
# on the T-handle does not tip; short in Z (print volume, not a giant frame).
FOOT_PAD_X = 76.0                # full width of each foot pad
FOOT_PAD_Z = 16.0                # short: open carriage leaves ~20 mm at the rail tip
FOOT_T = 6.0                     # pad thickness
POST_W = 16.0
HANDLE_STEM = 40.0               # T-handle up into +Y (feed side)
HANDLE_BAR = 50.0
HANDLE_D = 12.0
STOP_T = 6.0                     # printed end stops on the rail tips
SCREW_D = 4.2                    # M4 clearance through pads → clamp to table
SCREW_R = 30.0                   # hole centres from foot mid-plane X=0

y_rail_bot = RAIL_Y - RAIL_OD / 2
y_pad_top = y_rail_bot - 18.0    # short posts; AirTAC hangs free above the table
y_floor = y_pad_top - FOOT_T

open_carr_z0 = carriage.BoundBox.ZMin - STROKE
# Front foot under the forward barrel collar (longer stance than the breech clamp).
front_z = (z_clamp2_0 + z_clamp2_1) / 2
# Rear foot on the rail tip, entirely aft of the open carriage (thumb + bushings).
rear_z = z_rail0 + FOOT_PAD_Z / 2
assert rear_z + FOOT_PAD_Z / 2 <= open_carr_z0 - 2.0, "rear foot into open carriage"


def foot(z_c):
    """One printable foot: pad + two rail seats. Mid-plane open for the L-thumb."""
    pad = Part.makeBox(FOOT_PAD_X, FOOT_T, FOOT_PAD_Z,
                       V(-FOOT_PAD_X / 2, y_floor, z_c - FOOT_PAD_Z / 2))
    # Table clamp holes (M4 through the pad into the bench).
    for sx in (-SCREW_R, SCREW_R):
        pad = pad.cut(Part.makeCylinder(SCREW_D / 2, FOOT_T + 2.0,
                                        V(sx, y_floor - 1.0, z_c), Y))
    posts = []
    for x, y in rail_centers():
        body = Part.makeBox(POST_W, y_rail_bot - y_pad_top + 1.0, FOOT_PAD_Z - 4.0,
                            V(x - POST_W / 2, y_pad_top - 0.5, z_c - (FOOT_PAD_Z - 4.0) / 2))
        body = body.cut(G.cyl(RAIL_HOLE, z_c - FOOT_PAD_Z / 2 - 1,
                              z_c + FOOT_PAD_Z / 2 + 1, x, y))
        cheek = Part.makeBox(POST_W, RAIL_OD / 2 + 1.0, FOOT_PAD_Z - 4.0,
                             V(x - POST_W / 2, y_rail_bot,
                               z_c - (FOOT_PAD_Z - 4.0) / 2))
        cheek = cheek.cut(G.cyl(RAIL_HOLE, z_c - FOOT_PAD_Z / 2 - 1,
                                z_c + FOOT_PAD_Z / 2 + 1, x, y))
        posts.append(body.fuse(cheek))
    # Low cross-bar ties left/right posts to the pad (still below the thumb path).
    bar = Part.makeBox(2 * RAIL_X + POST_W, 5.0, FOOT_PAD_Z - 4.0,
                       V(-RAIL_X - POST_W / 2, y_pad_top - 0.5,
                         z_c - (FOOT_PAD_Z - 4.0) / 2))
    return G.fuse_all([pad, bar] + posts).removeSplitter()


front_foot = foot(front_z)
rear_foot = foot(rear_z)
# Compound for the scene; exported as two STLs so the print is two small parts.
bed = Part.makeCompound([front_foot, rear_foot])
bed_vol = front_foot.Volume + rear_foot.Volume

# End stops on the rail tips (keep the carriage from walking off).
stops = []
for x, y in rail_centers():
    for z_s in (z_rail0 + 1.0, z_rail1 - 1.0 - STOP_T):
        st = G.cyl(BUSH_OD + 2.0, z_s, z_s + STOP_T, x, y).cut(
            G.cyl(RAIL_OD + 0.2, z_s - 1, z_s + STOP_T + 1, x, y))
        stops.append(st)
stops_s = G.fuse_all(stops)

# T-handle on the carriage: stem into +Y so you push/pull by hand from the feed side.
handle_stem = Part.makeCylinder(HANDLE_D / 2, HANDLE_STEM,
                                V(0, CH_OD / 2 - 2.0, z_ry - CARR_T / 2), Y)
handle_bar = Part.makeCylinder(HANDLE_D / 2, HANDLE_BAR,
                               V(-HANDLE_BAR / 2, CH_OD / 2 - 2.0 + HANDLE_STEM,
                                 z_ry - CARR_T / 2), X)
handle = handle_stem.fuse(handle_bar).removeSplitter()
carriage_handled = carriage.fuse(handle).removeSplitter()

# ---------------------------------------------------------------- checks
# Tip: foot half-width in X vs handle height; Z stance is the rail span between feet.
handle_y = CH_OD / 2 - 2.0 + HANDLE_STEM
tip_lever = handle_y - y_floor
half_width = FOOT_PAD_X / 2
stance_z = (front_z - FOOT_PAD_Z / 2) - (rear_z + FOOT_PAD_Z / 2)
tip_ok = half_width >= 0.30 * tip_lever and stance_z >= 0.8 * tip_lever
post_height_ok = (front_foot.BoundBox.YMax >= y_rail_bot - 0.5
                  and rear_foot.BoundBox.YMax >= y_rail_bot - 0.5)

carr_closed = carriage_handled
carr_open = shifted(carriage_handled, -STROKE)
# Clearance vs each foot (compound distToShape can be flaky on multi-solid).
def min_clear(parts, sh):
    return min(p.distToShape(sh)[0] for p in parts)

feet = [front_foot, rear_foot]
bed_vs_closed = min_clear(feet, carr_closed)
bed_vs_open = min_clear(feet, carr_open)
bed_vs_qev = min_clear(feet, qev_body)
handle_vs_vent = handle.distToShape(vent_body)[0]

# Print budget: both feet together should stay well under a long slab (~150 cm³).
vol_ok = bed_vol < 80e3   # mm³

station_ok = G.single_solid(carriage) and abs((z_push_closed - z_plunger_free) - VENT_PUSH) < 1e-6

checks = [
    ("front foot valid single solid", G.single_solid(front_foot)),
    ("rear foot valid single solid", G.single_solid(rear_foot)),
    ("carriage+handle valid single solid", G.single_solid(carriage_handled)),
    ("pads below rails, AirTAC hangs free (y_floor %.1f)" % y_floor,
     y_floor < RAIL_Y - 15.0 and min_clear(feet, vent_body) >= 0.5),
    ("feet reach the rail underside", post_height_ok),
    ("stance vs tip (halfX %.0f >= 0.30 x %.0f; Z span %.0f)"
     % (half_width, tip_lever, stance_z), tip_ok),
    ("print volume both feet %.0f cm3 < 80" % (bed_vol / 1000.0), vol_ok),
    ("feet clear of closed carriage (%.1f mm)" % bed_vs_closed, bed_vs_closed >= 0.5),
    ("feet clear of open carriage (%.1f mm)" % bed_vs_open, bed_vs_open >= 0.5),
    ("feet clear of QEV body (%.1f mm)" % bed_vs_qev, bed_vs_qev >= 0.5),
    ("T-handle clear of AirTAC (%.1f mm)" % handle_vs_vent, handle_vs_vent >= 5.0),
    ("end stops present on both rail tips", stops_s.Volume > 100),
    ("station library: carriage solid + close press %.1f mm" % VENT_PUSH, station_ok),
]

report = [
    NAME,
    "  purpose                : hand bench for one linear-breech station (open / load / close / fire)",
    "  feet                   : 2x pad %.0fx%.0fx%.0f mm at y %.1f; rails are the beam (no long slab)"
    % (FOOT_PAD_X, FOOT_T, FOOT_PAD_Z, y_floor),
    "  volume                 : %.0f cm3 both feet; front z %.0f, rear z %.0f, stance %.0f mm"
    % (bed_vol / 1000.0, front_z, rear_z, stance_z),
    "  handle                 : T on carriage, stem %.0f mm into +Y; shove closed to dump AirTAC"
    % HANDLE_STEM,
    "  station                : stroke %.1f mm, AirTAC press on close %.1f mm" % (STROKE, VENT_PUSH),
    "  not drawn              : regulator plumbing, chronograph stand",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

try:
    LINEAR_BREECH_BENCH_LIBRARY
except NameError:
    LINEAR_BREECH_BENCH_LIBRARY = False
if LINEAR_BREECH_BENCH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

# ---------------------------------------------------------------- scene + export
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
doc = sc.doc

styles_qev = {
    "Rear_plug": "stator", "Seat_ring": "rotor", "Diaphragm": "shoe",
    "Front_cover": "stator", "Front_yoke": "stator", "Barrel_stub": "ghost",
    "Chamber_tube": "ghost", "Tie_rods": "steel", "Pilot_fitting": "steel",
}
for n, s in qev_closed.items():
    if n == "Carriage":
        continue
    sc.add("Closed", n, s, styles_qev.get(n, "stator"))
sc.add("Closed", "Carriage", carriage_handled, "stator")
sc.add("Fixed", "Rails", rails_s, "steel")
sc.add("Fixed", "Barrel_clamp", barrel_clamp, "stator")
sc.add("Fixed", "Barrel_collar", barrel_collar, "stator")
sc.add("Fixed", "Fixed_barrel", fixed_barrel, "ghost")
sc.add("Fixed", "AirTAC_cradle", cradle, "stator")
sc.add("Fixed", "Foot_front", front_foot, "stator")
sc.add("Fixed", "Foot_rear", rear_foot, "stator")
sc.add("Fixed", "Rail_stops", stops_s, "stator")
sc.add("Bought", "AirTAC_body", vent_body, "steel")
sc.add("Bought", "AirTAC_fittings", vent_fittings, "ghost")
sc.add("Bought", "AirTAC_plunger", vent_plunger, "shoe")
if SHOW_OPEN:
    for n, s in qev_open.items():
        if n == "Carriage":
            sc.add("Open", "Open_Carriage", shifted(carriage_handled, -STROKE), "ghost")
        else:
            sc.add("Open", "Open_" + n, s, "ghost")
    sc.add("Open", "Pellet", pellet, "flow")

for text, pos in [
    ("ДВЕ ОПОРЫ — рельсы сами балка", (0, y_floor - 12, (front_z + rear_z) / 2)),
    ("РУЧКА: руками открыть / закрыть", (0, handle_y + 10, z_ry - CARR_T / 2)),
    ("ЗАКРЫТО → AirTAC сброс → выстрел", (60, 0, z_stop)),
    ("ОТКРЫТО → пулька сверху (+Y)", (60, 40, z_stop - STROKE / 2)),
]:
    sc.label("Labels", text, pos)

sc.finish(hidden_groups=("Labels", "Open"), opaque_groups=())
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(V(0, 0, 0), X, 180)
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.2).write(
        os.path.join(OUT_DIR, name + ".stl"))


for n, s in (("foot_front", front_foot), ("foot_rear", rear_foot),
             ("carriage_handle", carriage_handled),
             ("rail_stops", stops_s), ("barrel_clamp", barrel_clamp),
             ("barrel_collar", barrel_collar),
             ("airtac_cradle", cradle)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling linear breech bench has [FAIL] checks")
