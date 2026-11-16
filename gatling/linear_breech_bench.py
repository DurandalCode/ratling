# -*- coding: utf-8 -*-
"""
Bench for one Gatling linear-breech station: small feet under the rails.

Loads gatling/linear_breech.py as a library. The aluminium rails are the beam;
print only two feet (front under the barrel clamp, rear aft of the open
carriage); the carriage is pushed by hand on the QEV / bridge disc. No handle,
no long floor slab.

Prove on the bench: open → drop a pellet from +Y → close → press the AirTAC
tip → module fires. Crank / hopper / rotary union stay off this stand.
The tree separates printable parts from non-printable hardware; transparent
open-position copies remain nested under their matching category.

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
# on the QEV does not tip; short in Z (print volume, not a giant frame).
FOOT_PAD_X = 76.0                # full width of each foot pad
FOOT_PAD_Z = 16.0                # short: open carriage leaves ~20 mm at the rail tip
FOOT_T = 6.0                     # pad thickness
POST_W = 16.0
STOP_T = 6.0                     # printed end stops on the rail tips
SCREW_D = 4.2                    # M4 clearance through pads → clamp to table
SCREW_R = 30.0                   # hole centres from foot mid-plane X=0

y_rail_bot = RAIL_Y - RAIL_OD / 2
y_pad_top = y_rail_bot - 18.0    # short posts; AirTAC hangs free above the table
y_floor = y_pad_top - FOOT_T

open_carr_z0 = carriage.BoundBox.ZMin - STROKE
# Front foot under the forward barrel collar (longer stance than the breech clamp).
front_z = (z_clamp2_0 + z_clamp2_1) / 2
# Rear foot on the rail tip, entirely aft of the open carriage (thumb + rail bores).
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

# No handle: you push/pull the carriage by the QEV / bridge disc itself.
# Tip: foot half-width in X vs the push height on the QEV; Z stance is the rail span between feet.
push_y = CH_OD / 2
tip_lever = push_y - y_floor
half_width = FOOT_PAD_X / 2
stance_z = (front_z - FOOT_PAD_Z / 2) - (rear_z + FOOT_PAD_Z / 2)
tip_ok = half_width >= 0.30 * tip_lever and stance_z >= 0.8 * tip_lever
post_height_ok = (front_foot.BoundBox.YMax >= y_rail_bot - 0.5
                  and rear_foot.BoundBox.YMax >= y_rail_bot - 0.5)

# The moving station set: rear pusher + the nose clamp.
moving_closed = [carriage, nose]
moving_open = [shifted(carriage, -STROKE), shifted(nose, -STROKE)]
# Clearance vs each foot (compound distToShape can be flaky on multi-solid).
def min_clear(parts, sh):
    return min(p.distToShape(sh)[0] for p in parts)

feet = [front_foot, rear_foot]
bed_vs_closed = min(min_clear(moving_closed, f) for f in feet)
bed_vs_open = min(min_clear(moving_open, f) for f in feet)
bed_vs_qev = min_clear(feet, qev_body)

# Print budget: both feet together should stay well under a long slab (~150 cm³).
vol_ok = bed_vol < 80e3   # mm³

station_ok = G.single_solid(carriage)

checks = [
    ("front foot valid single solid", G.single_solid(front_foot)),
    ("rear foot valid single solid", G.single_solid(rear_foot)),
    ("pads below rails, AirTAC hangs free (y_floor %.1f)" % y_floor,
     y_floor < RAIL_Y - 15.0 and min_clear(feet, vent_body) >= 0.5),
    ("feet reach the rail underside", post_height_ok),
    ("stance vs tip (halfX %.0f >= 0.30 x %.0f; Z span %.0f)"
     % (half_width, tip_lever, stance_z), tip_ok),
    ("print volume both feet %.0f cm3 < 80" % (bed_vol / 1000.0), vol_ok),
    ("feet clear of closed carriage (%.1f mm)" % bed_vs_closed, bed_vs_closed >= 0.5),
    ("feet clear of open carriage (%.1f mm)" % bed_vs_open, bed_vs_open >= 0.5),
    ("feet clear of QEV body (%.1f mm)" % bed_vs_qev, bed_vs_qev >= 0.5),
    ("end stops present on both rail tips", stops_s.Volume > 100),
    ("station library: carriage solid", station_ok),
]

report = [
    NAME,
    "  purpose                : hand bench for one linear-breech station (open / load / close / fire)",
    "  feet                   : 2x pad %.0fx%.0fx%.0f mm at y %.1f; rails are the beam (no long slab)"
    % (FOOT_PAD_X, FOOT_T, FOOT_PAD_Z, y_floor),
    "  volume                 : %.0f cm3 both feet; front z %.0f, rear z %.0f, stance %.0f mm"
    % (bed_vol / 1000.0, front_z, rear_z, stance_z),
    "  station                : stroke %.1f mm; AirTAC tip unpressed - dump the pilot by hand"
    % STROKE,
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

PRINTABLE_PARTS = {
    "Rear_plug", "Seat_ring", "Diaphragm", "Front_cover", "Front_yoke",
    "Carriage", "Nose_clamp", "Barrel_clamp", "Barrel_collar",
    "AirTAC_cradle", "Foot_front", "Foot_rear", "Rail_stops",
}
NONPRINTABLE_PARTS = {
    "Barrel_stub", "Chamber_tube", "Tie_rods", "Pilot_fitting",
    "Rails", "Fixed_barrel", "AirTAC_body", "AirTAC_fittings",
    "AirTAC_plunger", "Pellet",
}
PART_GROUP = {
    **dict.fromkeys(PRINTABLE_PARTS, "Printable"),
    **dict.fromkeys(NONPRINTABLE_PARTS, "NonPrintable"),
}
SCENE_PARTS = set(qev_closed) | {
    "Rails", "Barrel_clamp", "Barrel_collar", "Fixed_barrel",
    "AirTAC_cradle", "Foot_front", "Foot_rear", "Rail_stops",
    "AirTAC_body", "AirTAC_fittings", "AirTAC_plunger", "Pellet",
}
assert set(PART_GROUP) == SCENE_PARTS

printable_group = sc.group("Printable")
printable_group.Label = "Печатное"
nonprintable_group = sc.group("NonPrintable")
nonprintable_group.Label = "Непечатное"
printable_open_group = sc.group("PrintableOpen")
printable_open_group.Label = "Открытый вид: печатные копии"
printable_group.addObject(printable_open_group)
nonprintable_open_group = sc.group("NonPrintableOpen")
nonprintable_open_group.Label = "Открытый вид: непечатные элементы"
nonprintable_group.addObject(nonprintable_open_group)

for n, s in qev_closed.items():
    if n == "Carriage":
        continue
    sc.add(PART_GROUP[n], n, s, styles_qev.get(n, "stator"))
sc.add(PART_GROUP["Carriage"], "Carriage", carriage, "stator")
for n, s, style in (
    ("Rails", rails_s, "steel"),
    ("Barrel_clamp", barrel_clamp, "stator"),
    ("Barrel_collar", barrel_collar, "stator"),
    ("Fixed_barrel", fixed_barrel, "ghost"),
    ("AirTAC_cradle", cradle, "stator"),
    ("Foot_front", front_foot, "stator"),
    ("Foot_rear", rear_foot, "stator"),
    ("Rail_stops", stops_s, "stator"),
    ("AirTAC_body", vent_body, "steel"),
    ("AirTAC_fittings", vent_fittings, "ghost"),
    ("AirTAC_plunger", vent_plunger, "shoe"),
):
    sc.add(PART_GROUP[n], n, s, style)
if SHOW_OPEN:
    for n, s in qev_open.items():
        sc.add(PART_GROUP[n] + "Open", "Open_" + n, s, "ghost")
    sc.add(PART_GROUP["Pellet"] + "Open", "Pellet", pellet, "flow")

for text, pos in [
    ("ДВЕ ОПОРЫ — рельсы сами балка", (0, y_floor - 12, (front_z + rear_z) / 2)),
    ("РУКАМИ: открыть / закрыть, толкать за QEV", (0, push_y + 10, z_ry - CARR_T / 2)),
    ("ЗАКРЫТО → AirTAC сброс → выстрел", (60, 0, z_stop)),
    ("ОТКРЫТО → пулька сверху (+Y)", (60, 40, z_stop - STROKE / 2)),
]:
    sc.label("Labels", text, pos)
sc.group("Labels").Label = "Справка"

sc.finish(hidden_groups=("Labels", "PrintableOpen", "NonPrintableOpen"), opaque_groups=())
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, flip=False, lay=None):
    """Export in print orientation (z = 0 on the bed). lay='pad': put the foot pad down."""
    s = shape.copy()
    if lay == "pad":
        s.rotate(V(0, 0, 0), X, 90)    # assembly -Y (pad) -> -Z
    if flip:
        s.rotate(V(0, 0, 0), X, 180)
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.2).write(
        os.path.join(OUT_DIR, name + ".stl"))


# One rail-stop ring (four copies on the plate); feet pad-down; clamps/cradle tip-up.
write(front_foot, "foot_front", lay="pad")
write(rear_foot, "foot_rear", lay="pad")
write(nose, "nose_clamp")
write(stops[0], "rail_stop")
write(barrel_clamp, "barrel_clamp", flip=True)
write(barrel_collar, "barrel_collar", flip=True)
write(cradle, "airtac_cradle", flip=True)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling linear breech bench has [FAIL] checks")
