# -*- coding: utf-8 -*-
"""
Jezzail muzzle bell, V4 (the v2.1 swept bell on a plug for the 40 mm tube).

Side project: a spring-and-plunger launcher that throws a tennis ball. This is
its muzzle, two printed parts:

  bell ... a long-rifle bell whose skin is one trumpet curve from the collar to
           the rim (v2.1). Its Ø63 socket takes the plug, not the tube.
  plug ... a reducer: OD 63 in the bell's socket, the 40 mm barrel tube inside.
           It sticks out under the bell as a collar, because the tube end has to
           sit below the smallest ball's lower cap.

The ball (60 .. 72 mm, tennis is 65.4 .. 68.6) is far wider than the tube: it
sits in the bell on six guide rails, and the plunger comes out of the tube,
through the plug's stop lip, and knocks it forward.

Model axis z up from the bell's socket end (as it sits on the barrel, muzzle up):

    z < 0 ........ plug collar under the bell; 3 pilot holes for screws into
                   the tube (drill the tube).
    z = 0 ........ bell socket end, collar bead, 3 pilot holes for screws into
                   the plug.
    z = SOCKET ... plug top face. It stops against the flat bottom ends of the
                   rails. A spherical recess in it, one BALL_BORE_CLEAR over the
                   smallest ball, takes that ball's lower cap. Under the recess:
                   lip bore Ø LIP_D (the plunger passes), a 40 deg chamfer the
                   tube end stops on, the tube bore.
    chamber ...... RAIL_N radial rails whose tips taper from Ø RAIL_TIP_BOT at
                   the plug to Ø RAIL_TIP_TOP: any ball from BALL_RANGE wedges
                   where the tips close to its size. The taper is shallower than
                   the felt's friction angle, so a ball pushed in by thumb stays
                   put muzzle-down. The bore cones with the tips (a bigger ball
                   sits higher), which is what lets the skin be one curve.
    skin ......... r = r_s + dR * f(t), f(t) = (a t / (1 - a t)) / (a / (1 - a)),
                   a = BELL_CURL, from the collar to the rim; as curled as the
                   wall over the top of the rails allows (0.66 -> 2.7 mm).
    funnel ....... above the rails the bore opens inside the skin, one WALL
                   in, never steeper than BORE_END_DEG from the axis.
    rim .......... vertical band LIP_FLAT tall, flat rim face at the mouth.

Print: the bell mouth down (exported flipped, rim on the bed): the skin, the
rail tips and rail bottoms face up; the chamber cone (9 deg from the axis), the
funnel (43 deg), the rail lead-in (30 deg) and the bead top (40 deg from
vertical) face down. The plug tube end down, as modelled: the recess and the
socket face up, the stop chamfer (40 deg) down. No supports.

TUBE_ID is a guess until the tube is measured (docs/human-todo.md). Overrides
are prefixed, a FreeCAD session shares globals between generators:
    JEZZAIL_TUBE_OD = 40.0; JEZZAIL_TUBE_ID = 36.0; JEZZAIL_TUBE_LEN = 400.0
    exec(open(REPO + '/jezzail/muzzle_bell.py').read())

History (kept for reference, not live):
  v1   (2026-11-22) socket on a guessed 80/75 tube, the ball went through the
       tube bore; trumpet bore p = 2.2 inside a 45 deg skin, printed socket
       down. Read as a plain cone.
  v1.1 six straight rails, tip Ø64.2, held a tennis ball by 0.6-2.2 mm squeeze;
       bore p = 4, 105 mm horn. Still straight outside.
  v1.2 skin curled out (3 -> 67 deg), printed rim down; Ø140 x 168, too big.
       The 80 mm tube was a misreading: the barrel is a 63 mm tube.
  v2   63 mm socket, tapered rails in a Ø78 cylinder chamber, Ø112 x 120.5;
       skin in steps (socket, chamber, neck bead, 40 mm trumpet).
  v2.1 63 mm socket, the bore coned with the rails, one-curve skin, curl 0.66.
  v3   socket for a 40 mm tube in the bell itself: stop lip, then a 40 deg
       shoulder out to the rails; the skin kinked over the shoulder. The owner
       asked for the v2.1 bell without the kink and a plug instead (v4).
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
BALL_RANGE = (60.0, 72.0)      # balls the rails take; tennis (ITF) is 65.41 .. 68.58
BALLS_SHOWN = (60.0, 65.41, 68.58, 72.0)
FELT_MU = 0.5                  # felt on PLA, rough; self-locking taper needs tan(a) < mu

try:
    TUBE_OD = JEZZAIL_TUBE_OD
except NameError:
    TUBE_OD = 40.0             # owner 2026-11-22
try:
    TUBE_ID = JEZZAIL_TUBE_ID
except NameError:
    TUBE_ID = 36.0             # GUESS (40 x 2); measure
try:
    TUBE_LEN = JEZZAIL_TUBE_LEN
except NameError:
    TUBE_LEN = 400.0           # owner 2026-11-22

FIT = 0.25                     # per side, every slip fit (bell/plug, plug/tube)
PLUG_OD = 63.0                 # bell socket = PLUG_OD + 2 FIT
SOCKET_LEN = 25.0              # bell socket depth
WALL = 3.0

LIP_D = 36.0                   # plug lip bore: the plunger passes
LIP_MIN = 1.5                  # straight lip bore between the stop chamfer and the recess
TUBE_IN = 25.0                 # tube engagement in the plug
PLUG_CHAMFER = 1.0             # outer bottom edge of the plug collar

SCREW_N = 3
SCREW_PILOT_D = 2.5            # ST2.9 self-tapping
SCREW_Z = 11.0                 # bell -> plug, from the bell's socket end
PLUG_SCREW_FROM_BOTTOM = 10.0  # plug -> tube

RAIL_N = 6
RAIL_T = 2.4                   # plate thickness, tangential
RAIL_TIP_BOT = 58.0            # tip circle at the plug: under the smallest ball
RAIL_TIP_TOP = 74.0            # tip circle at the top: over the biggest ball
RAIL_LEN = 50.0                # taper length (9 deg half angle)
RAIL_DEPTH_TOP = 3.0           # rail height at the top; the bore cones with the tips
RAIL_LEAD_DEG = 30.0           # mouth-side lead-in, from the axis
RAIL_WALL_OVERLAP = 0.5        # rail root sunk into the wall: one solid after the fuse
PLUNGER_CLEAR = 1.0            # per side, plunger head vs the lip and the tube bore
BALL_BORE_CLEAR = 1.0          # every seated ball vs the bore and the plug, per side

LIP_RIM_D = 112.0              # outside of the rim
MOUTH_Z = 110.0                # bell socket end -> rim face
BELL_CURL = 0.66               # 0 = cone; 0.70 leaves 2.2 mm over the rail tops
BORE_END_DEG = 43.0            # steepest funnel, from the axis: faces down in print, 45 is the limit
GAP = 2.0                      # plain bore between the rail lead-in and the funnel
K = 1.0 / math.tan(math.radians(40))   # dz per dr of a downward face in print, 40 deg from the axis

BEAD = 3.0                     # radial height of the collar bead at the socket end
BEAD_FLAT = 3.5
LIP_FLAT = 4.0                 # vertical band of the rim
LIP_TOP_CHAMFER = 1.0          # inside edge of the rim face; within the first layers in print

BED = 256.0                    # Bambu P2S

NAME = "jezzail_muzzle_bell"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- derived: bell
r_sock = PLUG_OD / 2 + FIT
r_out_s = r_sock + WALL                  # skin over the socket
z_stop = SOCKET_LEN                      # plug top face, on the rail ends
r_tip0 = RAIL_TIP_BOT / 2
r_tip1 = RAIL_TIP_TOP / 2
tan_a = (r_tip1 - r_tip0) / RAIL_LEN     # rail taper, half angle
cos_a = math.cos(math.atan(tan_a))
z_rail_top = z_stop + RAIL_LEN
r_ch = r_tip1 + RAIL_DEPTH_TOP           # bore at the rail tops; cones down to the socket
ch_slope = (r_ch - r_sock) / RAIL_LEN
z_rail_end = z_rail_top + RAIL_DEPTH_TOP / math.tan(math.radians(RAIL_LEAD_DEG))
z_horn = z_rail_end + GAP                # funnel starts
z_mouth = MOUTH_Z
z_band = z_mouth - LIP_FLAT
r_lip = LIP_RIM_D / 2
z_bead1 = 2.5
z_skin0 = z_bead1 + BEAD + BEAD_FLAT + K * BEAD   # the curve leaves the collar here
dR = r_lip - r_out_s
bore_slope_max = math.tan(math.radians(BORE_END_DEG))
_fn = BELL_CURL / (1 - BELL_CURL)


def seat(d):
    """Ball centre z and contact z when a ball of Ø d rests on the tapered rail tips."""
    R = d / 2
    zc = z_stop + (R / cos_a - r_tip0) / tan_a
    return zc, zc - R * math.sin(math.atan(tan_a))


def skin_r(z):
    t = min(max((z - z_skin0) / (z_band - z_skin0), 0.0), 1.0)
    return r_out_s + dR * (BELL_CURL * t / (1 - BELL_CURL * t)) / _fn


def skin_slope(z):
    t = min(max((z - z_skin0) / (z_band - z_skin0), 0.0), 1.0)
    return dR * (BELL_CURL / (1 - BELL_CURL * t) ** 2) / _fn / (z_band - z_skin0)


# ---------------------------------------------------------------- derived: plug
r_po = PLUG_OD / 2
r_pt = TUBE_OD / 2 + FIT                 # tube bore of the plug
r_pl = LIP_D / 2
zc_min, _ = seat(BALL_RANGE[0])          # the smallest ball dips deepest
r_rec = BALL_RANGE[0] / 2 + BALL_BORE_CLEAR
z_rec_lip = zc_min - math.sqrt(r_rec ** 2 - r_pl ** 2)       # recess meets the lip bore
r_rec_top = math.sqrt(max(r_rec ** 2 - (zc_min - z_stop) ** 2, 0.0))   # recess opening at the top face
z_lip_bot = z_rec_lip - LIP_MIN
z_tube_end = z_lip_bot - K * (r_pt - r_pl)   # 40 deg chamfer: the tube end stops on it
z_plug_bot = z_tube_end - TUBE_IN


def V(r, z):
    return App.Vector(r, 0, z)


def bead(r0, z0):
    """Bead on a vertical skin r0 from z0 up: 45 out, flat, 40-from-vertical back in
    (the top chamfer is the underside in print)."""
    return [V(r0, z0), V(r0 + BEAD, z0 + BEAD), V(r0 + BEAD, z0 + BEAD + BEAD_FLAT),
            V(r0, z0 + BEAD + BEAD_FLAT + K * BEAD)]


def edges(pts):
    return [Part.LineSegment(a, b).toShape() for a, b in zip(pts, pts[1:])]


def revolve(pts):
    s = Part.Face(Part.Wire(edges(pts))).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
    return Part.Solid(Part.Shell(s.Faces)) if s.ShapeType != "Solid" else s


def radial_pilots(shape, r_from, depth, z, phase):
    for i in range(SCREW_N):
        a = 2 * math.pi * (i + phase) / SCREW_N
        d = App.Vector(math.cos(a), math.sin(a), 0)
        start = App.Vector(d.x * r_from, d.y * r_from, z)
        shape = shape.cut(Part.makeCylinder(SCREW_PILOT_D / 2, depth, start, -d))
    return shape


# ---------------------------------------------------------------- bell
N = 160
zs = [z_skin0 + (z_band - z_skin0) * i / N for i in range(N + 1)]
outer_curve = [V(skin_r(z), z) for z in zs]
inner_ch = [V(r_sock + ch_slope * (z - z_stop), z) for z in
            [z_stop + RAIL_LEN * i / 40 for i in range(41)]]
zb = [z_horn + (z_mouth - z_horn) * i / N for i in range(N + 1)]
inner_horn = [V(r_ch, z_horn)]
for z in zb[1:]:
    target = skin_r(z) - WALL * math.sqrt(1 + skin_slope(z) ** 2) if z <= z_band else r_lip - WALL
    prev = inner_horn[-1]
    inner_horn.append(V(max(r_ch, min(target, prev.x + bore_slope_max * (z - prev.z))), z))
r_mouth = inner_horn[-1].x
bore_slopes = [(b.x - a.x) / (b.z - a.z) for a, b in zip(inner_horn, inner_horn[1:])]


def wall_at(p):
    best = 1e9
    for a, b in zip(outer_curve, outer_curve[1:]):
        dx, dz = b.x - a.x, b.z - a.z
        u = max(0.0, min(1.0, ((p.x - a.x) * dx + (p.z - a.z) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(p.x - a.x - u * dx, p.z - a.z - u * dz))
    return min(best, r_lip - p.x)


min_wall = min(wall_at(p) for p in inner_ch + inner_horn if p.z <= z_mouth - LIP_TOP_CHAMFER)

outer = ([V(r_sock, 0), V(r_out_s, 0)]
         + bead(r_out_s, z_bead1)[:-1]
         + [V(outer_curve[0].x, z_skin0)]
         + outer_curve[1:]
         + [V(r_lip, z_mouth)])
inner = ([V(r_mouth + LIP_TOP_CHAMFER, z_mouth), V(r_mouth, z_mouth - LIP_TOP_CHAMFER)]
         + [p for p in reversed(inner_horn) if p.z < z_mouth - LIP_TOP_CHAMFER - 0.2]
         + list(reversed(inner_ch))
         + [V(r_sock, 0)])
bell = revolve(outer + inner)
bell = radial_pilots(bell, r_out_s + BEAD + 1, WALL + BEAD + 3, SCREW_Z, 0.5)
bell_shell = bell

ov = RAIL_WALL_OVERLAP
rail_profile = Part.Face(Part.makePolygon([
    V(r_sock + ov, z_stop), V(r_tip0, z_stop), V(r_tip1, z_rail_top),
    V(r_ch + ov, z_rail_end + ov / math.tan(math.radians(RAIL_LEAD_DEG))),
    V(r_ch + ov, z_rail_top), V(r_sock + ov, z_stop)]))
rail = rail_profile.extrude(App.Vector(0, RAIL_T, 0))
rail.translate(App.Vector(0, -RAIL_T / 2, 0))
rails = []
for i in range(RAIL_N):
    r = rail.copy()
    r.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0 * i / RAIL_N)
    rails.append(r)
bell = bell.fuse(rails).removeSplitter()
bell = Part.Solid(bell.Shells[0]) if bell.ShapeType != "Solid" and len(bell.Solids) == 1 else bell

# ---------------------------------------------------------------- plug
plug = revolve([V(r_pt + PLUG_CHAMFER, z_plug_bot), V(r_po - PLUG_CHAMFER, z_plug_bot),
                V(r_po, z_plug_bot + PLUG_CHAMFER), V(r_po, z_stop), V(r_pl, z_stop),
                V(r_pl, z_lip_bot), V(r_pt, z_tube_end), V(r_pt, z_plug_bot + PLUG_CHAMFER),
                V(r_pt + PLUG_CHAMFER, z_plug_bot)])
plug = plug.cut(Part.makeSphere(r_rec, App.Vector(0, 0, zc_min)))
plug = radial_pilots(plug, r_po + 1, r_po - r_pt + 2, z_plug_bot + PLUG_SCREW_FROM_BOTTOM, 0.0)
plug = plug.removeSplitter()

# print orientations
bell_print = bell.copy()
bell_print.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
bell_print.translate(App.Vector(0, 0, -bell_print.BoundBox.ZMin))
plug_print = plug.copy()
plug_print.translate(App.Vector(0, 0, -plug_print.BoundBox.ZMin))

# ---------------------------------------------------------------- reference
tube = Part.makeCylinder(TUBE_OD / 2, TUBE_LEN, App.Vector(0, 0, z_tube_end - TUBE_LEN)).cut(
    Part.makeCylinder(TUBE_ID / 2, TUBE_LEN + 2, App.Vector(0, 0, z_tube_end - TUBE_LEN - 1)))
balls = []
for d in BALLS_SHOWN:
    zc, zcon = seat(d)
    balls.append((d, zc, zcon, Part.makeSphere(d / 2, App.Vector(0, 0, zc))))


def ball_checks(d, zc, zcon):
    R = d / 2
    snug = Part.makeSphere(R + 0.3, App.Vector(0, 0, zc))      # a hair bigger: must touch every rail
    loose = Part.makeSphere(R - 0.3, App.Vector(0, 0, zc))     # a hair smaller: must touch nothing
    clear = Part.makeSphere(R + BALL_BORE_CLEAR - 0.05, App.Vector(0, 0, zc))
    return {
        "seats on the taper": z_stop < zcon < z_rail_top,
        "rests on all rails": all(snug.common(r).Volume > 1e-3 for r in rails),
        "clear of the bore by %.1f" % BALL_BORE_CLEAR:
            bell_shell.common(clear).Volume < 1e-3 and bell.common(loose).Volume < 1e-3,
        "clear of the plug by %.1f" % BALL_BORE_CLEAR: plug.common(clear).Volume < 1e-3,
        "clear of the tube": tube.common(snug).Volume < 1e-3,
    }


# ---------------------------------------------------------------- checks
plunger_d = min(LIP_D, TUBE_ID) - 2 * PLUNGER_CLEAR
bb = bell.BoundBox
checks = {
    "bell valid single solid": bell.isValid() and len(bell.Solids) == 1,
    "plug valid single solid": plug.isValid() and len(plug.Solids) == 1,
    "bell / plug no interference": bell.common(plug).Volume < 1e-3,
    "plug / tube no interference": plug.common(tube).Volume < 1e-3,
    "bell / tube no interference": bell.common(tube).Volume < 1e-3,
    "plug top rests on the rail ends (>= 1 mm ring under them)": r_rec_top <= r_sock - 1.0 and r_rec_top > r_tip0 - 2,
    "tube end stops on the plug chamfer (lip under the tube bore)": LIP_D <= TUBE_OD - 2.0,
    "lip bore >= 1 mm long under the recess": z_rec_lip - z_lip_bot >= 1.0 - 1e-9,
    "plunger head passes the lip and the tube bore": plunger_d > 0 and LIP_D >= TUBE_ID - 1e-9,
    "plug wall over the tube >= 3 mm": r_po - r_pt >= 3.0,
    "taper self-locks on felt (tan a < mu)": tan_a < FELT_MU,
    "range fits the taper": seat(BALL_RANGE[0])[1] > z_stop and seat(BALL_RANGE[1])[1] < z_rail_top,
    "biggest ball enters the mouth": 2 * r_mouth >= BALL_RANGE[1] + 6,
    "funnel never steeper than 45 deg (faces down in print)": max(bore_slopes) <= 1.0,
    "chamber cone printable (<= 40 deg from the axis)": ch_slope <= 1 / K,
    "bell wall, normal to the skin, >= 2.5 mm": min_wall >= 2.5,
    "skin curls out: slope at the rim >= 4 x at the collar":
        skin_slope(z_band) >= 4 * max(skin_slope(z_skin0), 1e-9),
    "funnel starts above the rail ends": z_horn > z_rail_end,
    "bell screw pilots land in the plug": SCREW_Z + SCREW_PILOT_D / 2 < z_stop - 4,
    "plug screw pilots under the bell": z_plug_bot + PLUG_SCREW_FROM_BOTTOM + SCREW_PILOT_D / 2 < -2,
    "fits the P2S bed": max(bell_print.BoundBox.XLength, bell_print.BoundBox.ZLength) <= BED - 10,
    "print STLs: lowest point at z = 0": abs(bell_print.BoundBox.ZMin) < 1e-6 and abs(plug_print.BoundBox.ZMin) < 1e-6,
}
for d, zc, zcon, _ in balls:
    for k, v in ball_checks(d, zc, zcon).items():
        checks["ball Ø%.2f %s" % (d, k)] = v
report = [
    NAME,
    "  tube OD / ID / length   : %.2f / %.2f / %.0f   (ID: GUESS until measured)" % (TUBE_OD, TUBE_ID, TUBE_LEN),
    "  bell socket             : Ø%.2f x %.1f for the plug, wall %.1f" % (2 * r_sock, SOCKET_LEN, WALL),
    "  plug                    : OD %.1f, %.1f long (%.1f under the bell); tube bore Ø%.2f x %.1f, lip Ø%.1f"
    % (PLUG_OD, z_stop - z_plug_bot, -z_plug_bot, 2 * r_pt, TUBE_IN, LIP_D),
    "  plug recess             : sphere Ø%.1f round the smallest ball, opening Ø%.1f at the top face"
    % (2 * r_rec, 2 * r_rec_top),
    "  chamber bore            : cone Ø%.1f -> Ø%.1f with the rail tips" % (2 * r_sock, 2 * r_ch),
    "  rails                   : %d x %.1f, tips Ø%.1f -> Ø%.1f over %.0f mm (half angle %.1f deg)"
    % (RAIL_N, RAIL_T, RAIL_TIP_BOT, RAIL_TIP_TOP, RAIL_LEN, math.degrees(math.atan(tan_a))),
]
for d, zc, zcon, _ in balls:
    report.append("    ball Ø%-6.2f          : centre +%.1f, contact +%.1f above the plug top"
                  % (d, zc - z_stop, zcon - z_stop))
report += [
    "  plunger head            : <= Ø%.1f" % plunger_d,
    "  skin                    : one curve z %.1f -> %.1f, curl %.2f: %.0f deg at the collar -> %.0f deg at the rim"
    % (z_skin0, z_band, BELL_CURL, math.degrees(math.atan(skin_slope(z_skin0))),
       math.degrees(math.atan(skin_slope(z_band)))),
    "  funnel                  : Ø%.1f -> Ø%.1f, steepest %.1f deg; thinnest bell wall %.2f"
    % (2 * r_ch, 2 * r_mouth, math.degrees(math.atan(max(bore_slopes))), min_wall),
    "  bell overall            : Ø%.1f x %.1f; plug + bell %.1f; tube + muzzle %.0f"
    % (bb.XLength, bb.ZLength, z_mouth - z_plug_bot, TUBE_LEN + z_mouth - z_tube_end),
    "  volume                  : bell %.1f cm3, plug %.1f cm3 (~%.0f g PLA solid together)"
    % (bell.Volume / 1000, plug.Volume / 1000, (bell.Volume + plug.Volume) / 1000 * 1.24),
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
p_bell = doc.addObject("Part::Feature", "Muzzle_bell")
p_bell.Shape = bell
p_plug = doc.addObject("Part::Feature", "Tube_plug")
p_plug.Shape = plug
g_print.addObject(p_bell)
g_print.addObject(p_plug)
refs = []
o = doc.addObject("Part::Feature", "Ref_tube")
o.Shape = tube
g_ref.addObject(o)
refs.append(o)
for d, zc, zcon, shp in balls:
    o = doc.addObject("Part::Feature", "Ref_ball_%d" % round(d * 100))
    o.Label = "Ref_ball_%.2f" % d
    o.Shape = shp
    g_ref.addObject(o)
    refs.append(o)
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    p_bell.ViewObject.ShapeColor = (0.45, 0.42, 0.38)
    p_plug.ViewObject.ShapeColor = (0.85, 0.45, 0.15)
    refs[0].ViewObject.ShapeColor = (0.33, 0.40, 0.22)
    refs[0].ViewObject.Transparency = 50
    for o in refs[1:]:
        o.ViewObject.ShapeColor = (0.80, 0.90, 0.20)
        o.ViewObject.Transparency = 60
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
Part.export([p_bell, p_plug], os.path.join(OUT_DIR, NAME + ".step"))
import MeshPart
for shp, fn in ((bell_print, NAME + ".stl"), (plug_print, "jezzail_tube_plug.stl")):
    MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.02, AngularDeflection=0.1).write(
        os.path.join(OUT_DIR, fn))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
