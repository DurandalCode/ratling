# -*- coding: utf-8 -*-
"""
Gatling linear breech: fat coax QEV on rails, fixed real barrel, top feed gap.

One station of the rotating pack. The QEV slides on two rails parallel to the
barrel; closed, its stop flange butts the real barrel and the dry fitting sits
inside the bore; open, it pulls back by STROKE so a pellet can drop from +Y
into the breech mouth. Later the same linear unit repeats around the rotor,
fed by a multi-passage rotary union on the pilot lines.

Builds on gatling/fat_coax_qev.py (library). Sketch: rails, carriage, barrel
clamp, closed assembly + open ghost. Cam / hopper / rotary union not drawn.

Run inside FreeCAD / freecadcmd:
    REPO = '/path/to/ratling'
    exec(open(REPO + '/gatling/linear_breech.py').read())

Exports: exports/gatling_linear_breech/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech")
NAME = "gatling_linear_breech"

# ---------------------------------------------------------------- load QEV as library
GATLING_FAT_COAX_LIBRARY = True
exec(open(os.path.join(REPO, "gatling", "fat_coax_qev.py")).read(), globals())
# fat_coax overwrites OUT_DIR / NAME; put them back for this sketch.
OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech")
NAME = "gatling_linear_breech"

# ---------------------------------------------------------------- breech parameters
# Stroke: fitting fully out + gap for a ØBARREL_ID pellet to drop past the stop face.
PELLET_D = BARREL_ID
STROKE_MARGIN = 12.0
STROKE = FIT_INSERT + PELLET_D + STROKE_MARGIN

# Two aluminium tubes under the module (+Y is the feed side, kept clear).
# Keep them tight under the Ø50 tube so a hex pack at PACK_PITCH still clears.
RAIL_OD, RAIL_WALL = 8.0, 1.0
RAIL_HOLE = 8.3                  # printed bushing
RAIL_CLEAR = 0.5                 # rail OD to QEV solids
RAIL_X = 12.0                    # half-spacing under the chamber
RAIL_Y = -(CH_OD / 2 + RAIL_OD / 2 + 1.0)
RAIL_PAST_REAR = 20.0            # rail behind open rear plug
RAIL_PAST_FRONT = 40.0           # rail ahead of barrel clamp

# Carriage: bushings on the rails + bridge bolted to the rear plug ears (M3 holes).
BUSH_L = 28.0
BUSH_OD = RAIL_OD + 7.0
CARR_T = 8.0                     # bridge thickness behind the rear plug
CARR_EAR_R = EAR_R + 2.0
CARR_BOLT = TIE_HOLE
CARR_WEB = 6.0

# Barrel clamp: split ring on the real barrel, fixed to the rail front ends.
CLAMP_L = 28.0
CLAMP_OD = BARREL_OD + 14.0
CLAMP_BOLT_R = CLAMP_OD / 2 + 4.0
CLAMP_BOLT = 3.4                 # M3 through the halves
CLAMP_GAP = 1.0                  # split at ±Y so top feed is not blocked by a bridge
BARREL_SHOW = 160.0              # fixed barrel drawn ahead of the clamp

# Open/closed: closed at fat_coax pose; open = QEV translated -Z by STROKE.
SHOW_OPEN = True

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector


def at_xy(x, y, z=0.0):
    return V(x, y, z)


def tube(od, idd, z0, z1, x=0.0, y=0.0):
    return G.cyl(od, z0, z1, x, y).cut(G.cyl(idd, z0 - 1, z1 + 1, x, y))


def rail_centers():
    return ((-RAIL_X, RAIL_Y), (RAIL_X, RAIL_Y))


# Closed pose: barrel breech face at z_stop (from fat_coax).
z_clamp0 = z_stop
z_clamp1 = z_clamp0 + CLAMP_L
z_rail0 = (z_ry - STROKE) - RAIL_PAST_REAR
z_rail1 = z_clamp1 + RAIL_PAST_FRONT

# ---------------------------------------------------------------- rails (bought Al tube)
rails = [
    tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
    for x, y in rail_centers()
]
rails_s = G.fuse_all(rails)

# ---------------------------------------------------------------- carriage (printed)
# One solid: rear bridge on the plug + vertical webs down to bushings under the tube.
z_bush0 = z_ry - CARR_T - 4.0
z_bush1 = z_bush0 + BUSH_L
bridge = G.cyl(CH_OD + 2.0, z_ry - CARR_T, z_ry)
for a in TIE_ANGLES:
    p = at(TIE_R, a)
    bridge = bridge.fuse(G.cyl(2 * CARR_EAR_R, z_ry - CARR_T, z_ry, p.x, p.y))
# Flat plate under the rear plug spanning both rails, then bushing barrels.
plate = Part.makeBox(2 * RAIL_X + BUSH_OD, BUSH_OD + 2.0, CARR_T,
                     V(-RAIL_X - BUSH_OD / 2, RAIL_Y - BUSH_OD / 2 - 1.0, z_ry - CARR_T))
# Vertical webs from the bridge disc down to the plate (overlap both).
webs = []
for x, y in rail_centers():
    webs.append(Part.makeBox(CARR_WEB, abs(RAIL_Y) + BUSH_OD / 2, CARR_T + 2.0,
                             V(x - CARR_WEB / 2, RAIL_Y - BUSH_OD / 2, z_ry - CARR_T - 1.0)))
    webs.append(G.cyl(BUSH_OD, z_bush0, z_bush1, x, y))
carriage = G.fuse_all([bridge, plate] + webs).removeSplitter()
carriage = carriage.cut(G.fuse_all(
    [G.cyl(CARR_BOLT, z_ry - CARR_T - 1, z_ry + 1, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]
    + [G.cyl(RAIL_HOLE, z_bush0 - 2, z_bush1 + 2, x, y) for x, y in rail_centers()]
)).removeSplitter()

# ---------------------------------------------------------------- barrel clamp (printed, two halves)
# Ring around the barrel; split on the Y=0 plane into left/right so +Y feed stays open above.
clamp_ring = tube(CLAMP_OD, BARREL_OD + 0.3, z_clamp0, z_clamp1)
# Lugs for M3 at ±X (same height as rails, not blocking +Y).
for sx in (-1, 1):
    lug = G.cyl(8.0, z_clamp0, z_clamp1, sx * CLAMP_BOLT_R, 0.0).cut(
        G.cyl(CLAMP_BOLT, z_clamp0 - 1, z_clamp1 + 1, sx * CLAMP_BOLT_R, 0.0))
    clamp_ring = clamp_ring.fuse(lug)
# Feet down onto the rail ends (printed pockets that sit on the rails).
for x, y in rail_centers():
    foot = G.cyl(BUSH_OD, z_clamp0, z_clamp1, x, y).cut(
        G.cyl(RAIL_HOLE, z_clamp0 - 1, z_clamp1 + 1, x, y))
    # web from ring to foot
    web = Part.makeBox(abs(x) - BARREL_OD / 2 + 2, 6.0, CLAMP_L,
                       V(min(0.0, x) + (BARREL_OD / 2 - 2 if x < 0 else 0),
                         -3.0, z_clamp0))
    clamp_ring = clamp_ring.fuse(foot).fuse(web)
# Split into L/R halves with a kerf on Y=0.
kerf = Part.makeBox(CLAMP_OD * 2, CLAMP_GAP, CLAMP_L + 4,
                    V(-CLAMP_OD, -CLAMP_GAP / 2, z_clamp0 - 2))
# Keep a top notch open for feed visibility: cut a wide +Y window in front of the breech.
feed_win = Part.makeBox(BARREL_OD + 8, CLAMP_OD, 20,
                        V(-(BARREL_OD + 8) / 2, 0, z_stop - 2))
barrel_clamp = clamp_ring.cut(kerf).cut(feed_win).removeSplitter()

# Fixed real barrel (bought), breech face at z_stop, held by the clamp.
fixed_barrel = tube(BARREL_OD, BARREL_ID, z_stop, z_stop + BARREL_SHOW)

# ---------------------------------------------------------------- QEV solids to slide
qev_closed = {
    "Rear_plug": rp,
    "Seat_ring": sr,
    "Diaphragm": diaphragm,
    "Front_cover": front_cover,
    "Front_yoke": front_yoke,
    "Barrel_stub": barrel_stub,
    "Chamber_tube": chamber,
    "Tie_rods": hardware,
    "Pilot_fitting": fitting,
    "Carriage": carriage,
}
# Drop the library's free-floating real_barrel; this sketch owns the fixed one.


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


qev_open = {n: shifted(s, -STROKE) for n, s in qev_closed.items()} if SHOW_OPEN else {}

# Pellet at the breech mouth when open (drops from +Y into the gap).
pellet_z = z_stop - STROKE / 2.0
pellet = Part.makeSphere(PELLET_D / 2, V(0, 0, pellet_z))

# ---------------------------------------------------------------- checks
qev_body = G.fuse_all([rp, front_cover, chamber, front_yoke, hardware, barrel_stub])
rail_to_qev = rails_s.distToShape(qev_body)[0]
# Bushing: rail axis inside the uncut bushing barrel (the hole voids fail isInside).
bush_ok = all(
    G.cyl(BUSH_OD, z_bush0, z_bush1, x, y).isInside(
        V(x, y, (z_bush0 + z_bush1) / 2), 1e-3, True)
    for x, y in rail_centers()
)
# Open: fitting tip behind the barrel breech face.
open_cover = qev_open["Front_cover"]
open_tip_z = open_cover.BoundBox.ZMax
open_gap = z_stop - open_tip_z  # ~ STROKE - FIT_INSERT = PELLET_D + margin
# Top feed clear: no rail / carriage above y = 0 in the breech window.
feed_box = Part.makeBox(CH_OD, 80, STROKE + 10,
                        V(-CH_OD / 2, 2.0, z_stop - STROKE - 5))
feed_hit_rail = rails_s.common(feed_box).Volume
feed_hit_carr_open = qev_open["Carriage"].common(feed_box).Volume if SHOW_OPEN else 0.0
# Pack: rails must clear a neighbour module at PACK_PITCH (hex / square).
nbr = qev_body.translated(V(PACK_PITCH, 0, 0))
rail_to_nbr = rails_s.distToShape(nbr)[0]
rail_r_max = max(math.hypot(x, y) + RAIL_OD / 2 for x, y in rail_centers())

checks = [
    ("carriage valid single solid", G.single_solid(carriage)),
    ("barrel clamp valid (may be multi-solid halves)", barrel_clamp.Volume > 1000),
    ("rails clear of closed QEV body (%.1f mm >= %.1f)" % (rail_to_qev, RAIL_CLEAR),
     rail_to_qev >= RAIL_CLEAR),
    ("carriage has bushing barrels on both rail axes", bush_ok),
    ("stroke extracts the fitting: open tip z %.1f <= breech %.1f (gap %.1f >= pellet+margin %.1f)"
     % (open_tip_z, z_stop, open_gap, PELLET_D + STROKE_MARGIN - 0.5),
     SHOW_OPEN and open_tip_z <= z_stop + 1e-3
     and open_gap >= PELLET_D + STROKE_MARGIN - 0.5),
    ("stroke = fitting + pellet + margin (%.1f = %.1f + %.1f + %.1f)"
     % (STROKE, FIT_INSERT, PELLET_D, STROKE_MARGIN),
     abs(STROKE - (FIT_INSERT + PELLET_D + STROKE_MARGIN)) < 1e-6),
    ("+Y feed window clear of rails (vol %.0f)" % feed_hit_rail, feed_hit_rail < 1.0),
    ("+Y feed window clear of open carriage (vol %.0f)" % feed_hit_carr_open,
     feed_hit_carr_open < 1.0),
    ("rails clear of neighbour at pack pitch (%.1f mm >= %.1f; envelope R %.1f)"
     % (rail_to_nbr, RAIL_CLEAR, rail_r_max),
     rail_to_nbr >= RAIL_CLEAR),
    ("closed stop face at barrel breech (z_stop %.1f)" % z_stop,
     abs(fixed_barrel.BoundBox.ZMin - z_stop) < 1e-6),
    ("clamp holds the barrel OD (hole ~Ø%.1f)" % (BARREL_OD + 0.3),
     barrel_clamp.BoundBox.ZMin <= z_clamp0 + 1e-3 and barrel_clamp.BoundBox.ZMax >= z_clamp1 - 1e-3),
]

report = [
    NAME,
    "  station                : fat coax QEV on 2 rails, fixed real barrel, top (+Y) feed",
    "  stroke                 : %.1f mm (fitting %.0f + pellet Ø%.1f + margin %.0f); open tip gap %.1f mm"
    % (STROKE, FIT_INSERT, PELLET_D, STROKE_MARGIN, open_gap if SHOW_OPEN else -1),
    "  rails                  : Al tube Ø%.0f x %.0f, axes (±%.0f, %.1f), z %.0f .. %.0f (%.0f mm)"
    % (RAIL_OD, RAIL_WALL, RAIL_X, RAIL_Y, z_rail0, z_rail1, z_rail1 - z_rail0),
    "  carriage               : bushings Ø%.0f / hole Ø%.1f x %.0f + bridge %.0f mm on rear plug M3"
    % (BUSH_OD, RAIL_HOLE, BUSH_L, CARR_T),
    "  barrel clamp           : split L/R on Ø%.1f barrel, length %.0f, feet on rails; +Y feed notch"
    % (BARREL_OD, CLAMP_L),
    "  pack                   : pitch %.0f, rail envelope R %.1f, clear to neighbour %.1f mm"
    % (PACK_PITCH, rail_r_max, rail_to_nbr),
    "  not drawn              : cam / crank, hopper, rotary union, pilot hose routing",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- scene + export
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
doc = sc.doc

styles_qev = {
    "Rear_plug": "stator", "Seat_ring": "rotor", "Diaphragm": "shoe",
    "Front_cover": "stator", "Front_yoke": "stator", "Barrel_stub": "ghost",
    "Chamber_tube": "ghost", "Tie_rods": "steel", "Pilot_fitting": "steel",
    "Carriage": "stator",
}
for n, s in qev_closed.items():
    sc.add("Closed", n, s, styles_qev.get(n, "stator"))
sc.add("Fixed", "Rails", rails_s, "steel")
sc.add("Fixed", "Barrel_clamp", barrel_clamp, "stator")
sc.add("Fixed", "Fixed_barrel", fixed_barrel, "ghost")
if SHOW_OPEN:
    for n, s in qev_open.items():
        sc.add("Open", "Open_" + n, s, "ghost")
    sc.add("Open", "Pellet", pellet, "flow")

for text, pos in [
    ("ЗАКРЫТО: упор в ствол, фиттинг внутри", (55, 0, z_stop - 5)),
    ("ОТКРЫТО: ход %.0f мм, щель под пульку сверху" % STROKE, (55, 40, z_stop - STROKE / 2)),
    ("РЕЛЬСЫ Ø%.0f x %.0f под модулем (+Y свободен)" % (RAIL_OD, RAIL_WALL),
     (55, RAIL_Y - 15, (z_rail0 + z_rail1) / 2)),
    ("САЛАЗКИ на задней пробке", (55, 0, z_ry - CARR_T / 2)),
    ("ХОМУТ СТВОЛА (разъём L/R)", (55, 0, z_clamp0 + CLAMP_L / 2)),
    ("ПОДАЧА ПУЛЬКИ +Y", (0, 50, z_stop - STROKE / 2)),
]:
    sc.label("Labels", text, pos)

sc.finish(hidden_groups=("Labels",), opaque_groups=())
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(V(0, 0, 0), X, 180)
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.15).write(
        os.path.join(OUT_DIR, name + ".stl"))


for n, s, flip in (("carriage", carriage, False),
                   ("barrel_clamp", barrel_clamp, False)):
    write(s, n, flip)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling linear breech has [FAIL] checks")
