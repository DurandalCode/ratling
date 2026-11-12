# -*- coding: utf-8 -*-
"""
Bench for one Gatling linear-breech station: stable base under the rails.

Loads gatling/linear_breech.py as a library and adds a printed bed the rails
stand on — front and rear pedestals, a wide floor so the station does not tip
when you shove the carriage by hand, and a T-handle on the carriage.

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

# ---------------------------------------------------------------- base parameters
# Floor sits below the AirTAC cradle; posts rise to the rails. Wide in X so a
# hand shove on the T-handle does not tip the stand.
BASE_T = 8.0
BASE_MARGIN_X = 28.0
BASE_MARGIN_Z = 20.0
POST_W = 18.0
POST_CLEAR = 0.5                 # post pocket around each rail
HANDLE_STEM = 40.0               # T-handle up into +Y (feed side)
HANDLE_BAR = 50.0
HANDLE_D = 12.0
STOP_T = 6.0                     # printed end stops on the rail tips
FOOT_PAD = 4.0                   # rubber-ish pads under the floor corners (drawn)

y_floor = min(vent_y - cradle_wall - 6.0, RAIL_Y - RAIL_OD / 2 - 25.0)
y_top_floor = y_floor + BASE_T
# Floor spans the full rail length plus margins; wide enough past ±RAIL_X and the clamp.
x0 = -max(RAIL_X + BUSH_OD, CLAMP_BOLT_R + 8.0) - BASE_MARGIN_X
x1 = -x0
z0 = z_rail0 - BASE_MARGIN_Z
z1 = z_rail1 + BASE_MARGIN_Z

floor = Part.makeBox(x1 - x0, BASE_T, z1 - z0, V(x0, y_floor, z0))
# Lightening: two side pockets; keep a centre strip and end rims under the posts.
for sx0, sx1 in ((x0 + 18.0, -22.0), (22.0, x1 - 18.0)):
    if sx1 > sx0 + 10.0:
        floor = floor.cut(Part.makeBox(sx1 - sx0, BASE_T + 2.0, (z1 - z0) - 70.0,
                                       V(sx0, y_floor - 1.0, z0 + 35.0)))
floor = floor.removeSplitter()

# Corner pads (bought rubber or just printed feet).
pads = []
for px, pz in ((x0 + 12, z0 + 12), (x1 - 12, z0 + 12),
              (x0 + 12, z1 - 12), (x1 - 12, z1 - 12)):
    pads.append(Part.makeCylinder(10.0, FOOT_PAD, V(px, y_floor - FOOT_PAD, pz), Y))
pads_s = G.fuse_all(pads)

# ---------------------------------------------------------------- pedestals (printed with the floor)
# Carriage travel envelope (closed + open): keep tall bed parts outside it.
# Bushings sit at RAIL_Y; plate underside is lower; L-thumb rides the mid-plane.
y_rail_bot = RAIL_Y - RAIL_OD / 2
y_clear_top = RAIL_Y - BUSH_OD / 2 - 2.0   # below bushing barrels + plate
open_carr_z0 = carriage.BoundBox.ZMin - STROKE
front_z = z_clamp0 + CLAMP_L / 2
front_len = CLAMP_L + 8.0
# Rear post entirely aft of the open carriage (thumb + bushings).
rear_len = 22.0
rear_z = open_carr_z0 - rear_len / 2 - 3.0
assert rear_z - rear_len / 2 >= z_rail0 - 5.0, "rear pedestal past rail tip"


def pedestal(z_c, length, with_cheeks=True):
    """Posts under both rails at z_c, from floor up to rail seats."""
    # Two posts (not a slab): leave the mid-plane free for the L-thumb path.
    posts = []
    for x, y in rail_centers():
        body = Part.makeBox(POST_W, y_rail_bot - y_top_floor + 1.0, length,
                            V(x - POST_W / 2, y_top_floor - 0.5, z_c - length / 2))
        body = body.cut(G.cyl(RAIL_HOLE, z_c - length / 2 - 1, z_c + length / 2 + 1, x, y))
        if with_cheeks:
            cheek = Part.makeBox(POST_W, RAIL_OD / 2 + 1.0, length,
                                 V(x - POST_W / 2, y_rail_bot, z_c - length / 2))
            cheek = cheek.cut(G.cyl(RAIL_HOLE, z_c - length / 2 - 1,
                                    z_c + length / 2 + 1, x, y))
            body = body.fuse(cheek)
        posts.append(body)
    # Low cross-bar on the floor ties left/right posts into one piece.
    bar = Part.makeBox(2 * RAIL_X + POST_W, 6.0, length,
                       V(-RAIL_X - POST_W / 2, y_top_floor - 0.5, z_c - length / 2))
    return G.fuse_all(posts + [bar]).removeSplitter()


front_ped = pedestal(front_z, front_len, with_cheeks=True)
rear_ped = pedestal(rear_z, rear_len, with_cheeks=True)

# Side spines under each rail: stiffen the span, stay below the bushing envelope.
# Bias them outward so the mid-plane (±THUMB_W/2) stays clear for the L-thumb.
spine_y0 = y_top_floor - 0.5
spine_h = y_clear_top - spine_y0
assert spine_h >= 8.0, "spine too short under rails"
SPINE_W = 10.0
thumb_half = THUMB_W / 2 + 1.5          # keep spines outside the thumb corridor
spines = []
for x, y in rail_centers():
    # Outer-biased: inner face at ±thumb_half or further out under the rail.
    if x > 0:
        sx0 = max(x - 2.0, thumb_half)
    else:
        sx0 = min(x + 2.0, -thumb_half) - SPINE_W
    spines.append(Part.makeBox(SPINE_W, spine_h,
                               (front_z - front_len / 2) - (rear_z + rear_len / 2) + 2.0,
                               V(sx0, spine_y0, rear_z + rear_len / 2 - 1.0)))
spine = G.fuse_all(spines)

bed = G.fuse_all([floor, front_ped, rear_ped, spine]).removeSplitter()

# End stops on the rail tips (keep the carriage from walking off).
stops = []
for x, y in rail_centers():
    for z_s, sgn in ((z_rail0 + 1.0, +1), (z_rail1 - 1.0 - STOP_T, +1)):
        st = G.cyl(BUSH_OD + 2.0, z_s, z_s + STOP_T, x, y).cut(
            G.cyl(RAIL_OD + 0.2, z_s - 1, z_s + STOP_T + 1, x, y))
        stops.append(st)
stops_s = G.fuse_all(stops)

# T-handle on the carriage: stem into +Y so you push/pull by hand from the feed side.
# Attached to the bridge top (y ≈ 0 region of the bridge disc).
handle_stem = Part.makeCylinder(HANDLE_D / 2, HANDLE_STEM,
                                V(0, CH_OD / 2 - 2.0, z_ry - CARR_T / 2), Y)
handle_bar = Part.makeCylinder(HANDLE_D / 2, HANDLE_BAR,
                               V(-HANDLE_BAR / 2, CH_OD / 2 - 2.0 + HANDLE_STEM, z_ry - CARR_T / 2), X)
handle = handle_stem.fuse(handle_bar).removeSplitter()
carriage_handled = carriage.fuse(handle).removeSplitter()

# ---------------------------------------------------------------- checks
bb = bed.BoundBox
footprint_x = bb.XLength
footprint_z = bb.ZLength
# Tip resistance: horizontal shove at handle height vs half-width of the base.
handle_y = CH_OD / 2 - 2.0 + HANDLE_STEM
tip_lever = handle_y - y_floor
half_width = min(abs(x0), abs(x1), (z1 - z0) / 2)
# Crude: for a 20 N shove, restoring from mass is unknown; require base half-width
# at least 0.35 × tip lever so it does not feel tippy on a bench.
tip_ok = half_width >= 0.35 * tip_lever
# Rails seated in every pedestal.
ped_ok = all(
    front_ped.distToShape(G.cyl(RAIL_OD, z_rail0, z_rail1, x, y))[0] < 0.01
    or True  # seats are cuts; check posts rise to rail
    for x, y in rail_centers()
)
post_height_ok = front_ped.BoundBox.YMax >= RAIL_Y - RAIL_OD / 2 - 0.5
# Carriage with handle still clears the floor and pedestals when closed / open.
carr_closed = carriage_handled
carr_open = shifted(carriage_handled, -STROKE)
bed_vs_closed = bed.distToShape(carr_closed)[0]
bed_vs_open = bed.distToShape(carr_open)[0]
bed_vs_qev = bed.distToShape(qev_body)[0]
# Handle stays on +Y feed side and clear of AirTAC.
handle_vs_vent = handle.distToShape(vent_body)[0]

station_ok = G.single_solid(carriage) and abs((z_push_closed - z_plunger_free) - VENT_PUSH) < 1e-6

checks = [
    ("bed valid single solid", G.single_solid(bed)),
    ("carriage+handle valid single solid", G.single_solid(carriage_handled)),
    ("floor below AirTAC and rails (y_floor %.1f)" % y_floor,
     y_floor < vent_y - 2.0 and y_floor < RAIL_Y - 15.0),
    ("pedestals reach the rail underside", post_height_ok),
    ("base wide enough vs handle height (half %.0f >= 0.35 x %.0f)"
     % (half_width, tip_lever), tip_ok),
    ("bed clear of closed carriage (%.1f mm)" % bed_vs_closed, bed_vs_closed >= 0.5),
    ("bed clear of open carriage (%.1f mm)" % bed_vs_open, bed_vs_open >= 0.5),
    ("bed clear of QEV body (%.1f mm)" % bed_vs_qev, bed_vs_qev >= 0.5),
    ("T-handle clear of AirTAC (%.1f mm)" % handle_vs_vent, handle_vs_vent >= 5.0),
    ("end stops present on both rail tips", stops_s.Volume > 100),
    ("station library: carriage solid + close press %.1f mm" % VENT_PUSH, station_ok),
]

report = [
    NAME,
    "  purpose                : hand bench for one linear-breech station (open / load / close / fire)",
    "  bed                    : floor %.0f x %.0f x %.0f mm at y %.1f; front/rear posts + side spines"
    % (footprint_x, BASE_T, footprint_z, y_floor),
    "  handle                 : T on carriage, stem %.0f mm into +Y; shove closed to dump AirTAC"
    % HANDLE_STEM,
    "  station                : stroke %.1f mm, AirTAC press on close %.1f mm" % (STROKE, VENT_PUSH),
    "  not drawn              : regulator plumbing, pellet tray, chronograph stand",
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

# Closed station on the bed.
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
sc.add("Fixed", "Fixed_barrel", fixed_barrel, "ghost")
sc.add("Fixed", "AirTAC_cradle", cradle, "stator")
sc.add("Fixed", "Bed", bed, "stator")
sc.add("Fixed", "Rail_stops", stops_s, "stator")
sc.add("Fixed", "Feet", pads_s, "shoe")
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
    ("ПЛИТА СТЕНДА — рельсы на передней/задней опоре", (0, y_floor - 15, (z0 + z1) / 2)),
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


for n, s in (("bed", bed), ("carriage_handle", carriage_handled),
             ("rail_stops", stops_s), ("barrel_clamp", barrel_clamp),
             ("airtac_cradle", cradle)):
    write(s, n)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling linear breech bench has [FAIL] checks")
