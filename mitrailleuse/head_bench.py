# -*- coding: utf-8 -*-
"""
Mitrailleuse firing head, bench B: one barrel's head on a hand slider (FreeCAD 1.0).

One port of concept A's firing head (rotor_timing.py, docs/rotor.md), unrolled flat, to run a v4.4 module
by hand before anything round is printed: does the chamber charge through a valve core, does the vent core
let the pilot down fast enough for a clean shot, does the charge pusher's O-ring hold, does the quiet dump
work. Bench frame: x along the slider, y across it, z up; the block's bottom face z = 0.

    head block ... printed, bottom face on the bed. Two tyre valve cores (5V1, screwed in from below, pins
                   down) on the rotor's radial line: the charge core at +ROW_Y (R60 on the rotor), the vent
                   core at -ROW_Y (R42), 18 apart as there. Inside, all channels printed in:
                     supply: G1/8 on the +y side -> the charge core's tyre side;
                     pilot:  the charge core's pin side (the cavity under it) -> a riser -> G1/8 on top (hose
                             to the module's pilot) and across to the vent core's tyre side -> G1/8 on the -x end
                             (a gauge);
                     exhaust: the vent core's pin side -> out of the -y side, Ø EXH_D.
                   The charge cavity is closed by an O-ring 3 x 1.5 round the pusher pin, in a gland at the
                   bottom face (the guide plate under it is its floor); the vent cavity needs none.
    guide plate .. printed, under the block (4 x M3 through both into the base): guides both pusher pins.
    pushers ...... a Ø3 steel pin each, through the plate up to the core's pin, held in a printed follower by
                   an M3 grub screw: slide the pin to set its gap under the core's pin (REST_GAP), so a core's
                   scatter is set by hand here (the gun's sprung nose is left out). A return spring between
                   plate and follower keeps the follower on the slider (rotor_timing.RETURN).
    slider ....... printed, under the followers in the base's channel, pushed along x by hand. Its two cam
                   strips are the rotor's: rotor_timing.height() for the charge arc and the vent arc, laid on
                   one bench pitch PITCH (the 16's vent pitch, so the charge ramps are as steep as the vent's
                   there, 26 deg; the rotor's charge ramps are 19). Notches on its side and a printed spring
                   tongue in the base's wall stop it at X_STOPS (the port's x in pitches, as in rotor_timing):
                   idle, charging, charging, both shut, venting, done.
    base ......... printed, floor and walls round the slider, posts under the plate.

Use (docs/test-plan.md, "Mitrailleuse head, bench B"): supply on the side through a tee with the dump valve
(a G1/8 ball valve into a plug drilled Ø0.5), the pilot G1/8 on top to the module's pilot port by a 4 mm
hose, a gauge on the end. Stop by stop: hold at a charging stop for a measured time, push through "both
shut" (does the module hold?) to "venting" (does it fire?).
Core numbers are typical (as in stage4v2_schrader.py), not measured: the grub screw is there for that.

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/head_bench.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/head_bench/ (STEP, STL, FCStd).
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
try:
    HEAD_BENCH_LIBRARY
except NameError:
    HEAD_BENCH_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

_rt = {"__name__": "rotor_timing"}
exec(open(os.path.join(REPO, "mitrailleuse", "rotor_timing.py"), encoding="utf-8").read(), _rt)

NAME = "head_bench"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
cyl = G.cyl

# ---------------------------------------------------------------- parameters
PITCH = 16.5                # bench pitch, mm: the 16's vent pitch, both strips laid on it
ROW_Y = 9.0                 # charge core at +ROW_Y, vent core at -ROW_Y (rotor: R60 / R42)
X_STOPS = ((2.5, "ждёт"), (1.5, "зарядка"), (0.5, "зарядка"), (0.0, "оба закрыты"), (-0.5, "сброс"),
           (-1.5, "выстрелил"))
X_HOME = X_STOPS[0][0]

# tyre valve core, 5V1 (typical, as in stage4v2_schrader.py)
TAP_5V1_D, TAP_5V1_LEN = 4.5, 4.0
CORE_SEAT = (4.5, 3.4, 0.6)
CORE_BORE_D, CORE_BELOW_SEAT = 3.4, 9.0
CORE_PIN_OUT = 1.2
CORE_THREAD_D = 5.3
CAV_D, CAV_TOP = 5.6, 4.9   # pin-side cavity (the thread goes in through it); the core's top end at CAV_TOP
STEM_ORING = (3.0, 1.5)     # ID x CS round the charge pin
GLAND = (6.2, 1.3)          # its gland at the block's bottom face: Ø, depth (13 % squeeze on the plate)
PIN_D, PIN_HOLE = 3.0, 3.2
REST_GAP = 0.5              # pin under the core's pin at rest, set with the grub screw

CH_D, SUP_D, EXH_D = 2.5, 3.0, 4.0      # pilot channels, supply, exhaust
G18_TAP_D, G18_TAP_DEPTH = 8.8, 8.0     # as the module's pilot port
BLOCK = (34.0, 46.0, 34.0)              # x, y, z
Z_SUP, Z_PIL, Z_LINK, Z_EXH = 20.0, 24.0, 3.2, 3.0
RISER_X = 7.0               # the pilot riser beside the charge core
BOLT_XY, BOLT_HOLE, BOLT_PILOT = (13.0, 20.5), 3.4, 2.7

PLATE_T = 6.0
SPRING = (6.0, 0.6, 12.0, 1.2)          # return spring: OD, wire, free length, rate N/mm
SPRING_REST = 8.0           # plate to follower at rest
FOLLOWER_D, FOLLOWER_H = 8.0, 8.0       # domed foot, radius FOLLOWER_D / 2
PIN_IN_FOLLOWER = 6.0

SLIDER_W, SLIDER_T, STRIP_W = 34.0, 8.0, 10.0
SIDE_CLEAR = 0.2
WALL_T, FLOOR_T = 7.8, 4.0
NOTCH_D = 1.2               # detent notch depth; the tongue's bump goes 0.8 in
HANDLE = (16.0, 8.0, 20.0)  # handle neck: width, height, length

TRAVEL = _rt["TRAVEL"]
PIN_OPEN, PIN_MAX = _rt["PIN_OPEN"], _rt["PIN_MAX"]
height = _rt["height"]
k16 = _rt["cams"](16)
TOP_C, TOP_V = k16["top_c"], _rt["VENT_TOP"]

# ---------------------------------------------------------------- derived levels
z_pin = CAV_TOP - CORE_PIN_OUT                      # the core's pin end
z_tap1 = CAV_TOP + TAP_5V1_LEN
z_seat1 = z_tap1 + CORE_SEAT[2]
z_bore1 = z_seat1 + CORE_BELOW_SEAT                 # the core's tyre end
z_plate = -PLATE_T
z_ftop = z_plate - SPRING_REST                      # follower's top at rest
z_cam0 = z_ftop - FOLLOWER_H                        # cam base = follower's foot at rest
z_slider0 = z_cam0 - SLIDER_T
z_floor0 = z_slider0 - FLOOR_T
z_pin_top = z_pin - REST_GAP
z_pin_bot = z_ftop - PIN_IN_FOLLOWER
y_wall = SLIDER_W / 2 + SIDE_CLEAR
bx, by, bz = BLOCK[0] / 2, BLOCK[1] / 2, BLOCK[2]
u_max = (X_HOME - X_STOPS[-1][0]) * PITCH           # slider travel
s0, s1 = -u_max - FOLLOWER_D - 2.0, FOLLOWER_D + 2.0  # slider body, its own frame (port at s = -u)
base_x = (s0 - 2.0, s1 + u_max + 2.0)


def rod(d, a, b):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(d / 2, (b - a).Length, a, b - a)


def tap(x, y, z, axis):
    """G1/8 tap Ø8.8 x 8 from a face at (x, y, z) inwards along axis (unit, into the block)."""
    a = V(*axis)
    return Part.makeCylinder(G18_TAP_D / 2, G18_TAP_DEPTH + 0.01, V(x, y, z) - a * 0.01, a)


# ---------------------------------------------------------------- head block
core_hole = lambda y: G.fuse_all([cyl(CAV_D, -1, CAV_TOP, 0, y), cyl(TAP_5V1_D, CAV_TOP - 0.01, z_tap1, 0, y),
                                  Part.makeCone(CORE_SEAT[0] / 2, CORE_SEAT[1] / 2, CORE_SEAT[2], V(0, y, z_tap1)),
                                  cyl(CORE_BORE_D, z_seat1 - 0.01, z_bore1, 0, y)])
charge_hole = core_hole(ROW_Y).fuse(cyl(GLAND[0], -1, GLAND[1], 0, ROW_Y))
vent_hole = core_hole(-ROW_Y)
net = {
    "supply": G.fuse_all([cyl(CORE_BORE_D, z_bore1 - 0.1, Z_SUP + SUP_D / 2, 0, ROW_Y),
                          rod(SUP_D, (0, ROW_Y, Z_SUP), (0, by - G18_TAP_DEPTH + 0.5, Z_SUP)),
                          tap(0, by, Z_SUP, (0, -1, 0))]),
    "pilot": G.fuse_all([rod(CH_D, (1.0, ROW_Y, Z_LINK), (RISER_X, ROW_Y, Z_LINK)),
                         cyl(CH_D, Z_LINK - CH_D / 2, bz - G18_TAP_DEPTH + 0.5, RISER_X, ROW_Y),
                         tap(RISER_X, ROW_Y, bz, (0, 0, -1)),
                         rod(CH_D, (RISER_X, ROW_Y, Z_PIL), (0, -ROW_Y, Z_PIL)),
                         cyl(CORE_BORE_D, z_bore1 - 0.1, Z_PIL + CH_D / 2, 0, -ROW_Y),
                         rod(CH_D, (0, -ROW_Y, Z_PIL), (-bx + G18_TAP_DEPTH - 0.5, -ROW_Y, Z_PIL)),
                         tap(-bx, -ROW_Y, Z_PIL, (1, 0, 0))]),
    "exhaust": rod(EXH_D, (0, -ROW_Y, Z_EXH), (0, -by - 1, Z_EXH)),
}
bolts = G.fuse_all([cyl(BOLT_HOLE, z_plate - 1, bz + 1, sx * BOLT_XY[0], sy * BOLT_XY[1])
                    for sx in (-1, 1) for sy in (-1, 1)])
block = Part.makeBox(BLOCK[0], BLOCK[1], bz, V(-bx, -by, 0))
for s in (charge_hole, vent_hole, net["supply"], net["pilot"], net["exhaust"], bolts):
    block = block.cut(s)

plate = Part.makeBox(BLOCK[0], BLOCK[1], PLATE_T, V(-bx, -by, z_plate)).cut(bolts)
for y in (ROW_Y, -ROW_Y):
    plate = plate.cut(cyl(PIN_HOLE, z_plate - 1, 1, 0, y))


# ---------------------------------------------------------------- pushers
def follower(y):
    r = FOLLOWER_D / 2
    body = cyl(FOLLOWER_D, z_cam0 + r, z_ftop, 0, y)
    foot = Part.makeSphere(r, V(0, y, z_cam0 + r)).common(Part.makeBox(FOLLOWER_D, FOLLOWER_D, r,
                                                                       V(-r, y - r, z_cam0)))
    f = body.fuse(foot).removeSplitter()
    f = f.cut(cyl(PIN_D + 0.1, z_pin_bot, z_ftop + 1, 0, y))
    return f.cut(rod(2.6, (0, y, z_ftop - 2.5), (r + 1, y, z_ftop - 2.5)))      # M3 grub, self-tapped


followers = {y: follower(y) for y in (ROW_Y, -ROW_Y)}
pins = G.fuse_all([cyl(PIN_D, z_pin_bot, z_pin_top, 0, y) for y in (ROW_Y, -ROW_Y)])
springs = []
for y in (ROW_Y, -ROW_Y):
    s = G.spring(0, z_ftop, z_plate, SPRING[0], SPRING[1], 4)
    s.translate(V(0, y, 0))
    springs.append(s)
springs = G.fuse_all(springs)


# ---------------------------------------------------------------- slider (its own frame: port at s = -u)
def strip(y, top):
    pts = []
    n = int((s1 - s0) / 0.5)
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        pts.append(V(s, 0, z_cam0 + TRAVEL * height(X_HOME + s / PITCH, top)))
    pts = [V(s1, 0, z_cam0 - 1), V(s0, 0, z_cam0 - 1)] + pts
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    sh = face.extrude(V(0, STRIP_W, 0))
    sh.translate(V(0, y - STRIP_W / 2, 0))
    return sh


stops_s = [(x - X_HOME) * PITCH for x, _ in X_STOPS]
slider = Part.makeBox(s1 - s0, SLIDER_W, SLIDER_T, V(s0, -SLIDER_W / 2, z_slider0))
slider = slider.fuse(strip(ROW_Y, TOP_C)).fuse(strip(-ROW_Y, TOP_V))
slider = slider.fuse(Part.makeBox(HANDLE[2], HANDLE[0], HANDLE[1], V(s0 - HANDLE[2], -HANDLE[0] / 2, z_slider0)))
slider = slider.fuse(cyl(22, z_slider0, z_slider0 + 26, s0 - HANDLE[2] - 6, 0))          # knob
for s in stops_s:
    tri = Part.Face(Part.makePolygon([V(s - 2.0, SLIDER_W / 2 + 0.5, 0), V(s, SLIDER_W / 2 - NOTCH_D, 0),
                                      V(s + 2.0, SLIDER_W / 2 + 0.5, 0), V(s - 2.0, SLIDER_W / 2 + 0.5, 0)]))
    notch = tri.extrude(V(0, 0, SLIDER_T + 1.0))
    notch.translate(V(0, 0, z_slider0 - 0.5))
    slider = slider.cut(notch)
slider = slider.removeSplitter()

# ---------------------------------------------------------------- base
x0b, x1b = base_x
base = Part.makeBox(x1b - x0b, 2 * (y_wall + WALL_T), FLOOR_T, V(x0b, -y_wall - WALL_T, z_floor0))
z_low = z_cam0 + 3.0                                               # low walls: guide the slider only
for sy in (-1, 1):
    y0 = y_wall if sy > 0 else -y_wall - WALL_T
    base = base.fuse(Part.makeBox(x1b - x0b, WALL_T, z_low - z_slider0, V(x0b, y0, z_slider0)))
    base = base.fuse(Part.makeBox(BLOCK[0], WALL_T, z_plate - z_slider0, V(-bx, y0, z_slider0)))   # posts
base = base.cut(G.fuse_all([cyl(BOLT_PILOT, z_plate - 14, z_plate + 1, sx * BOLT_XY[0], sy * BOLT_XY[1])
                            for sx in (-1, 1) for sy in (-1, 1)]))
# detent: a tongue cut in the +y wall at x = 0, rooted in the floor, a bump on its inner face
tw, th, tt = 8.0, z_low - 1.0 - z_slider0, 1.8
cut = Part.makeBox(tw + 2.0, WALL_T + 2, th + 1.0, V(-tw / 2 - 1.0, y_wall - 1, z_slider0))
cut = cut.cut(Part.makeBox(tw, tt, th, V(-tw / 2, y_wall, z_slider0)))
base = base.cut(cut)
base = base.fuse(Part.makeCylinder(1.2, th - 2.0, V(0, y_wall + 0.2, z_slider0 + 1.0), Z)).removeSplitter()


# ---------------------------------------------------------------- bought parts, for the picture
def core(y):
    return G.fuse_all([cyl(CORE_THREAD_D, CAV_TOP, z_tap1, 0, y), cyl(4.4, z_tap1, z_seat1 + 1, 0, y),
                       cyl(2.6, z_seat1 + 1, z_bore1 - 1, 0, y), cyl(1.0, z_pin, CAV_TOP, 0, y)])


cores = core(ROW_Y).fuse(core(-ROW_Y))
oring = Part.makeTorus(STEM_ORING[0] / 2 + STEM_ORING[1] / 2, STEM_ORING[1] / 2, V(0, ROW_Y, GLAND[1] / 2), Z)
fit_top = G.push_in_fitting(RISER_X, ROW_Y, bz)
fit_sup = G.push_in_fitting(0, 0, 0)
fit_sup.rotate(V(0, 0, 0), X, -90)
fit_sup.translate(V(0, by, Z_SUP))
gauge = G.fuse_all([rod(9.7, (-bx + G18_TAP_DEPTH, -ROW_Y, Z_PIL), (-bx - 12, -ROW_Y, Z_PIL)),
                    rod(40.0, (-bx - 12, -ROW_Y, Z_PIL), (-bx - 27, -ROW_Y, Z_PIL))])
screws = G.fuse_all([cyl(3.0, z_plate - 12, bz, sx * BOLT_XY[0], sy * BOLT_XY[1])
                     .fuse(cyl(5.5, bz, bz + 3, sx * BOLT_XY[0], sy * BOLT_XY[1]))
                     for sx in (-1, 1) for sy in (-1, 1)])


# ---------------------------------------------------------------- checks
def pin_at(x, top):
    """Pin travel into the core at port x: the cam lifts the follower, minus the rest gap."""
    return max(0.0, TRAVEL * height(x, top) - REST_GAP)


checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
wall = lambda a, b: a.distToShape(b)[0]
d_sp = wall(net["supply"], net["pilot"])
d_se = wall(net["supply"], net["exhaust"])
d_pe = wall(net["pilot"], net["exhaust"])
d_cross = min(wall(net["supply"], vent_hole), wall(net["pilot"].cut(cyl(CORE_BORE_D + 0.2, 0, bz, 0, -ROW_Y)),
                                                    cyl(CAV_D, -1, CAV_TOP, 0, -ROW_Y)))
d_bolt = min(wall(bolts, s) for s in (net["supply"], net["pilot"], net["exhaust"], charge_hole, vent_hole))
check(min(d_sp, d_se, d_pe) >= 1.2, "head block: supply / pilot / exhaust walls >= %.1f mm (%.1f / %.1f / %.1f)"
      % (min(d_sp, d_se, d_pe), d_sp, d_se, d_pe))
check(d_cross >= 1.2, "head block: supply clear of the vent core, pilot clear of the vent cavity (%.1f mm)" % d_cross)
check(d_bolt >= 1.2, "head block: bolts %.1f mm clear of every channel" % d_bolt)
links = (("supply reaches the charge core's tyre side", net["supply"], cyl(CORE_BORE_D, z_seat1, z_bore1, 0, ROW_Y)),
         ("pilot reaches the charge core's pin cavity", net["pilot"], cyl(CAV_D, GLAND[1], CAV_TOP, 0, ROW_Y)),
         ("pilot reaches the vent core's tyre side", net["pilot"], cyl(CORE_BORE_D, z_seat1, z_bore1, 0, -ROW_Y)),
         ("exhaust reaches the vent core's pin cavity", net["exhaust"], cyl(CAV_D, 0, CAV_TOP, 0, -ROW_Y)))
for text, a, b in links:
    check(a.common(b).Volume > 0.5, "head block: " + text)
check(G.single_solid(block) and G.single_solid(plate) and G.single_solid(slider) and G.single_solid(base),
      "block, plate, slider, base each one solid")
for y in (ROW_Y, -ROW_Y):
    check(G.single_solid(followers[y]), "follower at y %+.0f one solid" % y)
check(base.common(slider).Volume < 1e-3 and plate.common(block).Volume < 1e-3
      and slider.common(followers[ROW_Y]).Volume < 0.5 and pins.common(plate).Volume < 1e-3,
      "nothing overlaps at rest (slider in the base, pins in the plate)")
rows = []
ok_stops = True
for (x, name), s in zip(X_STOPS, stops_s):
    hc, hv = height(x, TOP_C), height(x, TOP_V)
    pc, pv = pin_at(x, TOP_C), pin_at(x, TOP_V)
    on_ramp = 0.0 < hc < 1.0 or 0.0 < hv < 1.0
    want_c = name == "зарядка"
    want_v = name == "сброс"
    good = (not on_ramp and (pc >= PIN_OPEN) == want_c and (pv >= PIN_OPEN) == want_v
            and pc <= PIN_MAX and pv <= PIN_MAX and (want_c or pc == 0) and (want_v or pv == 0))
    ok_stops &= good
    rows.append("    x %+.1f  slider %5.1f mm  %-12s charge pin %.1f  vent pin %.1f%s"
                % (x, -s, name, pc, pv, "" if good else "  <-- wrong"))
check(ok_stops, "slider stops: the right core pressed %.1f mm (opens at %.1f, bottoms at %.1f), none on a ramp"
      % (TRAVEL - REST_GAP, PIN_OPEN, PIN_MAX))
f_rest = SPRING[3] * (SPRING[2] - SPRING_REST)
f_in = SPRING[3] * (SPRING[2] - SPRING_REST + TRAVEL)
check(f_rest >= 2 * _rt["BUTTON_ORING_N"] and SPRING[2] - SPRING_REST + TRAVEL < SPRING[2] - 4 * SPRING[1] * 1.5,
      "return springs %.1f-%.1f N, over twice the O-ring's %.0f N; not coil-bound" % (f_rest, f_in,
                                                                                     _rt["BUTTON_ORING_N"]))
ramp_c = math.degrees(math.atan(TRAVEL / (_rt["RAMP"] * PITCH)))
check(ramp_c <= 32.0, "ramps %.0f deg on the bench pitch %.1f (rotor: %.0f / %.0f at 16, %.0f / %.0f at 19)"
      % (ramp_c, PITCH, k16["ramp_c"], k16["ramp_v"], _rt["cams"](19)["ramp_c"], _rt["cams"](19)["ramp_v"]))
a_exh = math.pi * EXH_D ** 2 / 4
check(a_exh >= math.pi * CORE_BORE_D ** 2 / 4, "exhaust Ø%.1f: %.1f mm2, over the core's bore Ø%.1f"
      % (EXH_D, a_exh, CORE_BORE_D))
pil_v = (net["pilot"].Volume - 2 * math.pi * G18_TAP_D ** 2 / 4 * G18_TAP_DEPTH) / 1000 \
    + math.pi * (CAV_D ** 2 / 4) * (CAV_TOP - GLAND[1]) / 1000
hose_v = math.pi * 2.5 ** 2 / 4 * 110 / 1000
gl_sq = (STEM_ORING[1] - GLAND[1]) / STEM_ORING[1]
check(0.08 <= gl_sq <= 0.25 and GLAND[0] >= STEM_ORING[0] + 2 * STEM_ORING[1] and CAV_D < STEM_ORING[0] + 2 *
      STEM_ORING[1], "stem O-ring %g x %g: %.0f %% squeeze on the plate, Ø%.1f gland, kept in by the Ø%.1f cavity"
      % (STEM_ORING + (gl_sq * 100, GLAND[0], CAV_D)))

report = [
    "Mitrailleuse head, bench B: one barrel's head on a hand slider",
    "  head block %.0f x %.0f x %.0f, %.1f cm3; cores 5V1 at y %+.0f (charge) / %+.0f (vent), pins down"
    % (BLOCK + (block.Volume / 1000, ROW_Y, -ROW_Y)),
    "  ports: supply G1/8 on +y, pilot G1/8 on top (hose 4 mm to the module), gauge G1/8 on -x, exhaust Ø%.1f on -y"
    % EXH_D,
    "  pilot volume in the block %.2f cm3, + %.2f cm3 in 110 mm of 4 x 2.5 hose" % (pil_v, hose_v),
    "  pushers: Ø%.0f pins, gap %.1f under the core's pin at rest (grub screw), stroke %.1f, pitch %.1f"
    % (PIN_D, REST_GAP, TRAVEL, PITCH),
    "  slider travel %.0f mm, stops:" % u_max,
] + rows + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
if not HEAD_BENCH_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- document and exports
if not HEAD_BENCH_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    undo = FV.VIEW_ROT.inverse()

    def add(group, name, shape, style):
        s = shape.copy()
        s.Placement = undo.multiply(s.Placement)
        sc.add(group, name, s, style)

    for n, s, st in (("Head_block", block, "stator"), ("Guide_plate", plate, "plate"),
                     ("Follower_charge", followers[ROW_Y], "printed"), ("Follower_vent", followers[-ROW_Y], "printed"),
                     ("Slider", slider, "rotor"), ("Base", base, "frame")):
        add("Printed", n, s, st)
    for n, s, st in (("Valve_cores", cores, "steel"), ("Pins", pins, "steel"), ("Return_springs", springs, "steel"),
                     ("Stem_oring", oring, "oring"), ("Pilot_fitting", fit_top, "steel"),
                     ("Supply_fitting", fit_sup, "steel"), ("Gauge", gauge, "steel_ghost"), ("Screws", screws, "steel")):
        add("Bought", n, s, st)
    half = Part.makeBox(200, 200, 200, V(0, -100, -100))
    add("Section", "Sec_block", block.cut(half), "stator")
    add("Section", "Sec_plate", plate.cut(half), "plate")
    add("Channels", "Supply", net["supply"], "flow")
    add("Channels", "Pilot", net["pilot"], "hose")
    add("Channels", "Exhaust", net["exhaust"], "drive")
    sc.finish(hidden_groups=("Section", "Channels"), opaque_groups=("Section",))
    sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for n, s, flip in (("head_block", block, False), ("guide_plate", plate, False),
                       ("follower", followers[ROW_Y], True), ("slider", slider, False), ("base", base, False)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
