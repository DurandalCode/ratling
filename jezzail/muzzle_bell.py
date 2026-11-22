# -*- coding: utf-8 -*-
"""
Jezzail muzzle bell, V1.2 (curved trumpet, printed rim down).

Side project: a spring-and-plunger launcher that throws a tennis ball. This is
its first part, the flared muzzle (a long-rifle bell with a rolled lip and two
beads behind it). The bell slips over the barrel tube and doubles as the
loading funnel: the ball goes in at the mouth and the bore never narrows below
the barrel bore.

Model axis z up from the socket end (as it sits on the barrel, muzzle up):

    z = 0 ........ socket end. Socket slips over the barrel OD,
                   3 radial pilot holes for self-tapping screws.
    stop cone .... the barrel end stops against its root; the bore steps from
                   the socket to the throat.
    neck ......... straight bore, Ø THROAT, the ball seat: RAIL_N guide rails
                   along the bore centre the ball and hold it by a light
                   squeeze of the felt (tip circle under the smallest ball),
                   so it stays put muzzle-down until the plunger pushes it.
                   Rails meet the wall at 40 deg on the barrel side and at
                   30 deg from the axis on the mouth side (loading lead-in).
                   Outside: base bead and neck bead.
    horn ......... a trumpet bell, curved on the outside: the skin follows
                   r = r_out + dR * f(t), f(t) = (a t / (1 - a t)) / (a / (1 - a))
                   with a = BELL_CURL, flat at the neck and nearly flat out at
                   the lip (v1.1 kept it a 45 deg cone, it read as straight).
                   The bore is a funnel inside it: it follows the skin one
                   WALL in, but never steeper than BORE_END_DEG from the axis,
                   so the lip ends in a thick flat rim.
    lip .......... vertical band LIP_FLAT tall, flat rim face at the mouth.

Print mouth down (the STL is exported flipped, rim on the bed). That is what
lets the skin curve: in this orientation it faces up at any angle, and the
45 deg limit falls on the bore and the bead tops, drawn at 40-43 deg (an exact
45 tessellates a hair past tools/orient_check.py). No supports.

BARREL_OD / BARREL_ID are a guess from photos until the tube is measured
(docs/human-todo.md). Set the prefixed names before exec to try another tube:
    JEZZAIL_BARREL_OD = 75.0; JEZZAIL_BARREL_ID = 71.2
    exec(open(REPO + '/jezzail/muzzle_bell.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")

# ---------------------------------------------------------------- parameters
# Tennis ball, ITF: 65.41 .. 68.58 mm. Worn and fuzzy balls sit near the top.
BALL_D_MIN = 65.41
BALL_D_MAX = 68.58
BALL_CLEAR = 1.0        # per side at the narrowest bore, on the largest ball

# Prefixed overrides: a FreeCAD session shares globals between generators, and
# the gatling leaves BARREL_ID = 23.8 behind (a GUI run here picked it up).
try:
    BARREL_OD = JEZZAIL_BARREL_OD
except NameError:
    BARREL_OD = 80.0    # GUESS from the photos of the green tube; measure
try:
    BARREL_ID = JEZZAIL_BARREL_ID
except NameError:
    BARREL_ID = 75.0    # GUESS; bore clear of the inner ribs, not the wall
try:
    BARREL_LEN = JEZZAIL_BARREL_LEN
except NameError:
    BARREL_LEN = 400.0  # the green tube, owner 2026-11-22

SOCKET_CLEAR = 0.25     # per side, PETG slip fit, the screws hold it
SOCKET_LEN = 35.0
WALL = 3.0              # shell, measured radially

SCREW_N = 3
SCREW_PILOT_D = 2.5     # ST2.9 self-tapping
SCREW_Z = 15.0          # from the socket end

# Guide rails (the ribs of the reference tube): radial plates along the bore.
RAIL_N = 6
RAIL_T = 2.4            # plate thickness, tangential
RAIL_TIP_D = BALL_D_MIN - 1.2   # tip circle: squeezes every ball (0.6 .. 2.2 mm per side)
RAIL_FULL = 30.0        # full-depth length of the rail
RAIL_LEAD_DEG = 30.0    # mouth-side lead-in, from the axis
RAIL_GAP = 2.0          # bore left clear below and above the rails
RAIL_WALL_OVERLAP = 0.5 # rail root sunk into the wall: one solid after the fuse
RAIL_SQUEEZE_MAX = 2.5  # per side on the largest ball: still goes in by thumb
LIP_D = 1.75 * BARREL_OD     # outside of the rim; the reference picture reads ~1.6-1.8 x barrel
HORN_LEN = 80.0         # neck to rim face
BELL_CURL = 0.85        # 0 = cone; 0.85: slope at the lip ~45x the slope at the neck
BORE_END_DEG = 43.0     # steepest bore, from the axis: faces down in print, 45 is the limit
K = 1.0 / math.tan(math.radians(40))   # dz per dr of every chamfer: 40 deg from vertical

BEAD = 3.5              # radial height of the decorative beads
BEAD_FLAT = 4.0         # vertical band of a bead
LIP_FLAT = 5.0          # vertical band of the rim
LIP_TOP_CHAMFER = 1.0   # inside edge of the rim face; within the first layers in print

BED = 256.0             # Bambu P2S

NAME = "jezzail_muzzle_bell"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- derived
r_sock = BARREL_OD / 2 + SOCKET_CLEAR
r_out = r_sock + WALL                     # outer skin of socket and neck
r_throat = BARREL_ID / 2                  # flush with the barrel bore: no step for the ball
z_stop = SOCKET_LEN                       # barrel end face
z_cone = z_stop + K * (r_sock - r_throat)  # stop cone top
rail_depth = r_throat - RAIL_TIP_D / 2
z_rail0 = z_cone + RAIL_GAP                     # root at the wall, barrel side
z_rail1 = z_rail0 + K * rail_depth              # full depth from here
z_rail2 = z_rail1 + RAIL_FULL
z_rail3 = z_rail2 + rail_depth / math.tan(math.radians(RAIL_LEAD_DEG))   # back at the wall
NECK_LEN = z_rail3 + RAIL_GAP - z_cone          # straight bore above the stop cone
z_horn = z_cone + NECK_LEN
z_ball_seat = (z_rail1 + z_rail2) / 2           # ball centre where it rests on the rails
z_mouth = z_horn + HORN_LEN
z_band = z_mouth - LIP_FLAT              # skin reaches the rim radius here
r_lip = LIP_D / 2
dR = r_lip - r_out
bore_slope_max = math.tan(math.radians(BORE_END_DEG))
_fn = BELL_CURL / (1 - BELL_CURL)


def skin_r(z):
    """Outer skin of the horn, z_horn .. z_band."""
    t = min(max((z - z_horn) / (z_band - z_horn), 0.0), 1.0)
    return r_out + dR * (BELL_CURL * t / (1 - BELL_CURL * t)) / _fn


def skin_slope(z):
    t = min(max((z - z_horn) / (z_band - z_horn), 0.0), 1.0)
    return dR * (BELL_CURL / (1 - BELL_CURL * t) ** 2) / _fn / (z_band - z_horn)


def V(r, z):
    return App.Vector(r, 0, z)


def bead(r0, z0):
    """Bead on a vertical skin r0 from z0 up: 45 out, flat, 40-from-vertical back in
    (the top chamfer is the underside in print)."""
    return [V(r0, z0), V(r0 + BEAD, z0 + BEAD), V(r0 + BEAD, z0 + BEAD + BEAD_FLAT),
            V(r0, z0 + BEAD + BEAD_FLAT + K * BEAD)]


N = 160
zs = [z_horn + (z_band - z_horn) * i / N for i in range(N + 1)]
outer_horn = [V(skin_r(z), z) for z in zs]
# Bore: one WALL (normal) inside the skin, slope capped, never under the throat.
zb = [z_horn + (z_mouth - z_horn) * i / N for i in range(N + 1)]
inner_horn = [V(r_throat, z_horn)]
for z in zb[1:]:
    target = skin_r(z) - WALL * math.sqrt(1 + skin_slope(z) ** 2) if z <= z_band else r_lip - WALL
    prev = inner_horn[-1]
    inner_horn.append(V(max(r_throat, min(target, prev.x + bore_slope_max * (z - prev.z))), z))
r_mouth = inner_horn[-1].x
MOUTH_D = 2 * r_mouth
bore_slopes = [(b.x - a.x) / (b.z - a.z) for a, b in zip(inner_horn, inner_horn[1:])]


def wall_at(p):
    """Shortest distance from a bore point to the outer skin polyline (2D)."""
    best = 1e9
    for a, b in zip(outer_horn, outer_horn[1:]):
        ax, az, bx, bz = a.x, a.z, b.x, b.z
        dx, dz = bx - ax, bz - az
        u = max(0.0, min(1.0, ((p.x - ax) * dx + (p.z - az) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(p.x - ax - u * dx, p.z - az - u * dz))
    return min(best, r_lip - p.x)


min_wall_horn = min(wall_at(p) for p in inner_horn[1:] if p.z <= z_mouth - LIP_TOP_CHAMFER)

z_bead1 = 3.0                         # base bead, at the socket end
z_bead2 = z_horn - (K + 1) * BEAD - BEAD_FLAT - 1.0   # neck bead, just under the flare

outer = ([V(r_sock, 0), V(r_out, 0)]
         + bead(r_out, z_bead1)
         + bead(r_out, z_bead2)
         + outer_horn
         + [V(r_lip, z_mouth)])
inner = ([V(r_mouth + LIP_TOP_CHAMFER, z_mouth), V(r_mouth, z_mouth - LIP_TOP_CHAMFER)]
         + [p for p in reversed(inner_horn) if p.z < z_mouth - LIP_TOP_CHAMFER - 0.2]
         + [V(r_throat, z_cone), V(r_sock, z_stop), V(r_sock, 0)])


def edges(pts):
    return [Part.LineSegment(a, b).toShape() for a, b in zip(pts, pts[1:])]


wire = Part.Wire(edges(outer + inner))
face = Part.Face(wire)
bell = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
bell = Part.Solid(Part.Shell(bell.Faces)) if bell.ShapeType != "Solid" else bell

for i in range(SCREW_N):
    a = 2 * math.pi * (i + 0.5) / SCREW_N
    d = App.Vector(math.cos(a), math.sin(a), 0)
    start = App.Vector(d.x * (r_out + 1), d.y * (r_out + 1), SCREW_Z)
    bell = bell.cut(Part.makeCylinder(SCREW_PILOT_D / 2, WALL + 3, start, -d))
bell_shell = bell
rail_profile = Part.Face(Part.makePolygon([
    App.Vector(r_throat + RAIL_WALL_OVERLAP, 0, z_rail0 - RAIL_WALL_OVERLAP * K),
    App.Vector(RAIL_TIP_D / 2, 0, z_rail1), App.Vector(RAIL_TIP_D / 2, 0, z_rail2),
    App.Vector(r_throat + RAIL_WALL_OVERLAP, 0,
               z_rail3 + RAIL_WALL_OVERLAP / math.tan(math.radians(RAIL_LEAD_DEG))),
    App.Vector(r_throat + RAIL_WALL_OVERLAP, 0, z_rail0 - RAIL_WALL_OVERLAP * K)]))
rail = rail_profile.extrude(App.Vector(0, RAIL_T, 0))
rail.translate(App.Vector(0, -RAIL_T / 2, 0))
rails = []
for i in range(RAIL_N):
    r = rail.copy()
    r.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0 * i / RAIL_N)
    rails.append(r)
bell = bell.fuse(rails).removeSplitter()
bell = Part.Solid(bell.Shells[0]) if bell.ShapeType != "Solid" and len(bell.Solids) == 1 else bell

# ---------------------------------------------------------------- reference
barrel_len = BARREL_LEN
barrel = Part.makeCylinder(BARREL_OD / 2, barrel_len, App.Vector(0, 0, z_stop - barrel_len)).cut(
    Part.makeCylinder(BARREL_ID / 2, barrel_len + 2, App.Vector(0, 0, z_stop - barrel_len - 1)))
ball_max = Part.makeSphere(BALL_D_MAX / 2, App.Vector(0, 0, z_ball_seat))
ball_min = Part.makeSphere(BALL_D_MIN / 2, App.Vector(0, 0, z_ball_seat))
ball_mouth = Part.makeSphere(BALL_D_MIN / 2, App.Vector(0, 0, z_mouth - BALL_D_MIN / 4))

# ---------------------------------------------------------------- checks
bb = bell.BoundBox
# print: flipped, rim face on the bed
bell_print = bell.copy()
bell_print.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
bell_print.translate(App.Vector(0, 0, -bell_print.BoundBox.ZMin))
pb = bell_print.BoundBox
bed_ring = math.pi * (r_lip ** 2 - (r_mouth + LIP_TOP_CHAMFER) ** 2)
checks = {
    "bell valid single solid": bell.isValid() and len(bell.Solids) == 1,
    "bell / barrel no interference": bell.common(barrel).Volume < 1e-3,
    "largest ball clears the throat by >= %.1f mm per side" % BALL_CLEAR:
        r_throat - BALL_D_MAX / 2 >= BALL_CLEAR - 1e-9,
    "seated ball touches the rails only, not the bore": bell_shell.common(ball_max).Volume < 1e-3,
    "rails squeeze the smallest ball >= 0.3 mm per side": BALL_D_MIN / 2 - RAIL_TIP_D / 2 >= 0.3,
    "rails squeeze the largest ball <= %.1f mm per side" % RAIL_SQUEEZE_MAX:
        BALL_D_MAX / 2 - RAIL_TIP_D / 2 <= RAIL_SQUEEZE_MAX,
    "smallest ball seated in the rails touches all %d" % RAIL_N:
        all(ball_min.common(r).Volume > 1e-3 for r in rails),
    "rails end below the flare": z_rail3 + RAIL_GAP <= z_horn + 1e-9,
    "barrel bore passes the largest ball": BARREL_ID >= BALL_D_MAX + 2 * BALL_CLEAR,
    "bore never steeper than 45 deg (faces down in print)": max(bore_slopes) <= 1.0,
    "bore never narrower than the throat": min(p.x for p in inner_horn) >= r_throat - 1e-9,
    "smallest ball enters the mouth": MOUTH_D >= BALL_D_MAX + 10,
    "horn wall, normal to the skin, >= 2.5 mm": min_wall_horn >= 2.5,
    "skin curls out: slope at the lip >= 5 x at the neck":
        skin_slope(z_band) >= 5 * max(skin_slope(z_horn), 1e-9),
    "neck bead clears the base bead": z_bead2 > z_bead1 + (K + 1) * BEAD + BEAD_FLAT + 2,
    "screw pilots below the stop": SCREW_Z + SCREW_PILOT_D / 2 < z_stop - 5,
    "fits the P2S bed": max(pb.XLength, pb.YLength, pb.ZLength) <= BED - 10,
    "print STL: lowest point at z = 0": abs(pb.ZMin) < 1e-6,
}
report = [
    NAME,
    "  barrel OD / ID / length : %.2f / %.2f / %.0f   (OD, ID: GUESS until measured)"
    % (BARREL_OD, BARREL_ID, BARREL_LEN),
    "  barrel + bell overall   : %.0f (tube end seated on the stop cone)" % (BARREL_LEN + z_mouth - z_stop),
    "  tennis ball Ø           : %.2f .. %.2f" % (BALL_D_MIN, BALL_D_MAX),
    "  socket bore / depth     : Ø%.2f / %.1f, wall %.1f" % (2 * r_sock, SOCKET_LEN, WALL),
    "  rails                   : %d x %.1f thick, tip Ø%.1f, %.1f deep, full %.0f mm (z %.1f..%.1f)"
    % (RAIL_N, RAIL_T, RAIL_TIP_D, rail_depth, RAIL_FULL, z_rail1, z_rail2),
    "  squeeze on the ball     : %.2f .. %.2f mm per side (smallest .. largest)"
    % (BALL_D_MIN / 2 - RAIL_TIP_D / 2, BALL_D_MAX / 2 - RAIL_TIP_D / 2),
    "  plunger head            : <= Ø%.1f past z %.1f, or %d slots for the rails"
    % (RAIL_TIP_D - 2, z_rail0, RAIL_N),
    "  throat / mouth bore     : Ø%.1f / Ø%.1f, rim face %.1f wide" % (2 * r_throat, MOUTH_D, r_lip - r_mouth),
    "  ball clearance at throat: %.2f mm per side (largest ball)" % (r_throat - BALL_D_MAX / 2),
    "  horn                    : %.1f long, curl %.2f: skin %.0f deg at the neck -> %.0f deg at the lip"
    % (HORN_LEN, BELL_CURL, math.degrees(math.atan(skin_slope(z_horn))),
       math.degrees(math.atan(skin_slope(z_band)))),
    "  bore                    : steepest %.1f deg from axis; thinnest horn wall %.2f"
    % (math.degrees(math.atan(max(bore_slopes))), min_wall_horn),
    "  rim outer Ø             : %.1f (%.2f x barrel OD); bed ring %.0f mm2 in print"
    % (LIP_D, LIP_D / BARREL_OD, bed_ring),
    "  overall                 : Ø%.1f x %.1f" % (bb.XLength, bb.ZLength),
    "  volume                  : %.1f cm3 (~%.0f g PETG solid; less at 4 walls / 30 %%)"
    % (bell.Volume / 1000, bell.Volume / 1000 * 1.27),
]
for k, v in checks.items():
    report.append("  [%s] %s" % ("OK " if v else "FAIL", k))
print("\n".join(report))

# ---------------------------------------------------------------- output
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
g_print = doc.addObject("App::DocumentObjectGroup", "Print")
g_ref = doc.addObject("App::DocumentObjectGroup", "Reference")
p = doc.addObject("Part::Feature", "Muzzle_bell")
p.Shape = bell
g_print.addObject(p)
refs = []
for nm, shp in (("Ref_barrel", barrel), ("Ref_ball_max_seated", ball_max), ("Ref_ball_min_mouth", ball_mouth)):
    o = doc.addObject("Part::Feature", nm)
    o.Shape = shp
    g_ref.addObject(o)
    refs.append(o)
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    p.ViewObject.ShapeColor = (0.45, 0.42, 0.38)
    refs[0].ViewObject.ShapeColor = (0.33, 0.40, 0.22)
    refs[0].ViewObject.Transparency = 50
    for o in refs[1:]:
        o.ViewObject.ShapeColor = (0.80, 0.90, 0.20)
        o.ViewObject.Transparency = 40
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
Part.export([p], os.path.join(OUT_DIR, NAME + ".step"))
import MeshPart
mesh = MeshPart.meshFromShape(Shape=bell_print, LinearDeflection=0.02, AngularDeflection=0.1)
mesh.write(os.path.join(OUT_DIR, NAME + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
