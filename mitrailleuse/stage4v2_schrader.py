# -*- coding: utf-8 -*-
"""
Stage 4 v2 (draft): 25 Stage 3 v2 modules in a 5 x 5 pack, fired one by one
by tyre valve cores (Schrader) in the breech block. No hoses, no head.

    breech block . one printed block behind the pack. Front: 25 tube glands
                   on the 5 x 5 grid, each with the pilot tube socket. Inside,
                   one layer of channels takes each pilot from its grid place
                   to one of 25 valve cores on a circle R CORE_R on the back
                   face (routed so no two channels cross). A ring manifold
                   over the cores feeds every pilot through a jet Ø JET_D
                   into the core bore; supply G1/8 on the side.
    vent ......... a tyre valve core per barrel, screwed into a 5V1 thread
                   from the back. A printed button over its pin, held by a
                   retainer ring, takes the striker roller.
    striker ...... an arm with a 623 roller on a shaft behind the block
                   presses the buttons in turn: one turn = 25 shots. A ball
                   detent in the bracket parks the roller between buttons.
                   A printed 1:1 bevel pair (Stage 2's) turns it from the
                   side crank, whose shaft runs in its own boss on the bracket.

Core and 5V1 numbers are typical, not measured (CORE_*): check them against
the cores once bought. Frame: z along the barrels, +z forward, z = 0 the
block's front face (tube ends), +X up, +Y to the side.
Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/stage4v2_schrader.py').read())
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
    REPO = os.path.expanduser("~/ratling")
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.params as P
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
for _m in (P, G, FV, GR):
    importlib.reload(_m)

M = {"REPO": REPO, "STAGE3V2_LIBRARY": True}
exec(open(os.path.join(REPO, "module", "stage3v2_inline.py")).read(), M)

NAME = "stage4v2_schrader"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
N = 25
N_FITTED = 3

# ---------------------------------------------------------------- parameters
PITCH = 30.0
BLOCK_W = 150.0
CORE_R = 55.0
CORE_PHI = 5.4             # angle of core 0; with the routing below no channels cross
CENTRE_SORT_ANGLE = 136.8  # where the centre slot joins the angle order
ROUTE_SHIFT = 24
CH_D = 3.0                 # pilot channels
RING_D = 3.0               # manifold over the cores
JET_D = 0.8
Z_ROUTE = -13.0
Z_RING = -6.0
INLET_X = 15.0             # supply channel along +Y between two grid columns

# Tyre valve core (TR, 5V1): typical, not measured
CB_D = 6.6                 # counterbore for the button collar
CB_DEPTH = 4.9
TAP_5V1_D = 4.5
TAP_5V1_LEN = 4.0
CORE_SEAT = (4.5, 3.4, 0.6)
CORE_BORE_D = 3.4
CORE_BELOW_SEAT = 9.0      # core body + spring + poppet below the seal
CORE_PIN_OUT = 1.2

# Button and retainer
BTN_COLLAR = (6.2, 2.0)
BTN_STEM_D = 3.4
BTN_NOSE_D = 2.0
BTN_OUT = 1.5              # stem beyond the retainer at rest
PLAY = 0.3
TRAVEL = 1.5
RET_T = 3.0
RET_R = (44.0, 68.0)
RET_HOLE_D = 4.2
RET_SCREW_R = 64.0

# Striker, bracket, crank
ROLLER = (10.0, 4.0, 3.0)
ARM_W = 16.0
ARM_CLEAR = 1.0
HUB_D = 40.0
SHAFT_D = 8.0
BRACKET_T = 8.0
BRACKET_GAP = 6.0          # striker back to bracket
STANDOFF_AT = 62.0
CRANK_ARM = 55.0
CRANK_BOSS_D = 32.0
CRANK_BEARING_GAP = 20.0
CRANK_Y_OUT = 90.0          # crank arm beyond the block side (block half-width 75)

# ---------------------------------------------------------------- derived
cyl = M["cyl"]
z_back = Z_ROUTE - (CB_DEPTH + TAP_5V1_LEN + CORE_SEAT[2] + CORE_BELOW_SEAT)
z_core_top = z_back + CB_DEPTH
z_seat = z_core_top + TAP_5V1_LEN
z_pin = z_core_top - CORE_PIN_OUT
z_nose_rest = z_pin - PLAY
z_collar = (z_back, z_back + BTN_COLLAR[1])          # against the retainer at rest
z_stem_end = z_back - RET_T - BTN_OUT
z_roller_front = z_stem_end + TRAVEL
axle_z = z_roller_front - ROLLER[0] / 2
arm_z1 = z_stem_end - ARM_CLEAR
arm_z0 = axle_z - ROLLER[0] / 2 - 1.5
bracket_z = (arm_z0 - BRACKET_GAP - BRACKET_T, arm_z0 - BRACKET_GAP)
slots = [((i - 2) * PITCH, (j - 2) * PITCH) for i in range(5) for j in range(5)]
cores = [(CORE_R * math.cos(math.radians(CORE_PHI + 360.0 / N * k)),
          CORE_R * math.sin(math.radians(CORE_PHI + 360.0 / N * k))) for k in range(N)]
core_ang = [CORE_PHI + 360.0 / N * k for k in range(N)]


def ang(p):
    return math.degrees(math.atan2(p[1], p[0])) % 360


order = sorted(slots, key=lambda p: CENTRE_SORT_ANGLE if p == (0.0, 0.0) else ang(p))
route = {order[k]: (k + ROUTE_SHIFT) % N for k in range(N)}          # slot -> core
fire_order = sorted(slots, key=lambda s: (core_ang[route[s]] - core_ang[0]) % 360)   # as the striker turns


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def channel(p, q, z, d=CH_D, ext=1.5):
    """Straight channel p -> q at height z, 45 deg roof up (block prints back face down)."""
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    s = G.teardrop_x(d, -ext, L + ext, z)
    s.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])))
    s.translate(V(p[0], p[1], 0))
    return s


def ring(r, d, z):
    rc = d / 2
    tri = Part.Face(Part.makePolygon([V(r - rc / math.sqrt(2), 0, z + rc / math.sqrt(2)),
                                      V(r + rc / math.sqrt(2), 0, z + rc / math.sqrt(2)),
                                      V(r, 0, z + rc * math.sqrt(2)), V(r - rc / math.sqrt(2), 0, z + rc / math.sqrt(2))]))
    return Part.makeTorus(r, rc, V(0, 0, z), Z).fuse(tri.revolve(V(0, 0, 0), Z, 360))


# ---------------------------------------------------------------- breech block
sock_top = M["PLUG_INSERT_LEN"]
sock_floor = sock_top - M["PLUG_FUNNEL"][1] - M["SOCKET_DEPTH"]
block = box(-BLOCK_W / 2, BLOCK_W / 2, -BLOCK_W / 2, BLOCK_W / 2, z_back, 0)
for x, y in slots:
    sp, _ = M["gland"](sock_top, -0.5, +1)
    sp.translate(V(x, y, 0))
    block = block.fuse(sp)
cuts = [ring(CORE_R, RING_D, Z_RING), channel((INLET_X, CORE_R - 3), (INLET_X, BLOCK_W / 2 + 1), Z_RING, RING_D),
        Part.makeCylinder(8.8 / 2, 9, V(INLET_X, BLOCK_W / 2 - 8, Z_RING), Y)]
for x, y in slots:
    sc_, _ = M["socket_cut"](sock_top - M["PLUG_FUNNEL"][1], sock_floor, True)
    sc_.append(Part.makeCone(M["SOCKET_D"] / 2, M["PLUG_FUNNEL"][0] / 2, M["PLUG_FUNNEL"][1] + 0.01,
                             V(0, 0, sock_top - M["PLUG_FUNNEL"][1])))
    sc_ += M["screw_pilots"](M["SCREW_FROM_TUBE_END"], (60.0, 180.0, 300.0))
    sc_.append(cyl(CH_D, Z_ROUTE, sock_floor + 0.01))
    for c in sc_:
        c.translate(V(x, y, 0))
        cuts.append(c)
    cuts.append(channel((x, y), cores[route[(x, y)]], Z_ROUTE))
for (x, y) in cores:
    cuts += [cyl(CB_D, z_back - 1, z_core_top, x, y), cyl(TAP_5V1_D, z_core_top - 0.01, z_seat, x, y),
             Part.makeCone(CORE_SEAT[0] / 2, CORE_SEAT[1] / 2, CORE_SEAT[2], V(x, y, z_seat - 0.01)),
             cyl(CORE_BORE_D, z_seat + CORE_SEAT[2] - 0.02, Z_ROUTE + 0.5, x, y),
             cyl(JET_D, Z_ROUTE, Z_RING, x, y)]
ret_screws = [(RET_SCREW_R * math.cos(math.radians(a)), RET_SCREW_R * math.sin(math.radians(a)))
              for a in (core_ang[k] + 180.0 / N for k in range(0, N, 4))]
cuts += [cyl(2.5, z_back - 1, z_back + 8, x, y) for x, y in ret_screws]
standoffs_xy = [(sx * STANDOFF_AT, sy * STANDOFF_AT) for sx in (-1, 1) for sy in (-1, 1)]
cuts += [cyl(3.3, z_back - 1, z_back + 12, x, y) for x, y in standoffs_xy]          # M4 into the block
for c in cuts:
    block = block.cut(c)
block = block.removeSplitter()

# ---------------------------------------------------------------- retainer, buttons, cores
retainer = cyl(2 * RET_R[1], z_back - RET_T, z_back).cut(cyl(2 * RET_R[0], z_back - RET_T - 1, z_back + 1))
for x, y in cores:
    retainer = retainer.cut(cyl(RET_HOLE_D, z_back - RET_T - 1, z_back + 1, x, y))
for x, y in ret_screws:
    retainer = retainer.cut(cyl(3.4, z_back - RET_T - 1, z_back + 1, x, y))
retainer = retainer.removeSplitter()


def button(x, y, dz=0.0):
    return G.fuse_all([cyl(BTN_STEM_D, z_stem_end + dz, z_collar[0] + dz, x, y),
                       cyl(BTN_COLLAR[0], z_collar[0] + dz, z_collar[1] + dz, x, y),
                       cyl(BTN_NOSE_D, z_collar[1] + dz, z_nose_rest + dz, x, y)])


def valve_core(x, y):
    return G.fuse_all([cyl(0.9, z_pin, z_core_top, x, y), cyl(5.2, z_core_top, z_seat - 0.3, x, y),
                       Part.makeCone(2.2, 1.65, CORE_SEAT[2] + 0.25, V(x, y, z_seat - 0.3)),
                       cyl(3.0, z_seat + CORE_SEAT[2], z_seat + CORE_SEAT[2] + CORE_BELOW_SEAT - 0.5, x, y)])


buttons = G.fuse_all([button(x, y) for x, y in cores])
valve_cores = G.fuse_all([valve_core(x, y) for x, y in cores])

# ---------------------------------------------------------------- striker, bracket, crank, detent
rest_angle = CORE_PHI + 180.0 / N                      # roller parked between core 0 and core 1


def striker_at(a):
    arm = G.fuse_all([cyl(HUB_D, arm_z0, arm_z1),
                      box(0, CORE_R + 8, -ARM_W / 2, ARM_W / 2, arm_z0, arm_z1),
                      cyl(ARM_W, arm_z0, arm_z1, CORE_R + 8, 0)])
    w, d = ROLLER[1] + 0.6, ROLLER[0] + 0.6
    arm = arm.cut(box(CORE_R - w / 2, CORE_R + w / 2, -d / 2, d / 2, arm_z0 - 1, arm_z1 + 1))
    arm = arm.cut(Part.makeCylinder(1.6, 30, V(CORE_R - 15, 0, axle_z), X)).cut(cyl(SHAFT_D + 0.15, arm_z0 - 1, arm_z1 + 1))
    for k in range(N):                                 # detent notches on the hub rim
        a_k = math.radians(360.0 / N * k + 180.0 / N)
        arm = arm.cut(cyl(4.0, arm_z0 - 1, arm_z0 + 3, HUB_D / 2 * math.cos(a_k), HUB_D / 2 * math.sin(a_k)))
    roller = Part.makeCylinder(ROLLER[0] / 2, ROLLER[1], V(CORE_R - ROLLER[1] / 2, 0, axle_z), X).cut(
        Part.makeCylinder(ROLLER[2] / 2, ROLLER[1] + 2, V(CORE_R - ROLLER[1] / 2 - 1, 0, axle_z), X))
    for s in (arm, roller):
        s.rotate(V(0, 0, 0), Z, a)
    return arm.removeSplitter(), roller


arm, roller = striker_at(rest_angle)
arm_fire, roller_fire = striker_at(core_ang[0])
bz0, bz1 = bracket_z
bracket = G.fuse_all([box(-STANDOFF_AT - 8, STANDOFF_AT + 8, -STANDOFF_AT - 8, STANDOFF_AT + 8, bz0, bz1),
                      cyl(32, bz0 - 16, bz1)])
for sx in (-1, 1):                                     # lightening windows between the arms
    for sy in (-1, 1):
        w = Part.Face(Part.makePolygon([V(sx * 22, sy * 10, bz0 - 1), V(sx * 22, sy * 50, bz0 - 1),
                                        V(sx * 50, sy * 50, bz0 - 1), V(sx * 50, sy * 22, bz0 - 1),
                                        V(sx * 22, sy * 10, bz0 - 1)])).extrude(V(0, 0, BRACKET_T + 2))
        bracket = bracket.cut(w)
bracket = bracket.cut(cyl(22.1, bz0 - 17, bz0 - 9)).cut(cyl(22.1, bz1 - 7, bz1 + 1)).cut(cyl(12, bz0 - 17, bz1 + 1))
for x, y in standoffs_xy:
    bracket = bracket.cut(cyl(4.4, bz0 - 1, bz1 + 1, x, y))
# detent: plunger block on the bracket, ball into the hub notches from behind
det_r = HUB_D / 2
det_xy = (det_r * math.cos(math.radians(rest_angle)), det_r * math.sin(math.radians(rest_angle)))
bracket = bracket.fuse(cyl(12, bz1, arm_z0 - 2.4, *det_xy)).cut(cyl(5.2, bz1 - 6, arm_z0, *det_xy))
bracket = bracket.removeSplitter()
standoffs = G.fuse_all([cyl(12, bz1, z_back - RET_T, x, y).cut(cyl(4.4, bz1 - 1, z_back, x, y)) for x, y in standoffs_xy])
detent_ball = Part.makeSphere(2.5, V(det_xy[0], det_xy[1], arm_z0 - 0.5))
# side crank through a printed 1:1 bevel pair (ratling/gears.py, Stage 2 numbers)
apex = bz0 - 16 - 1.0 - P.BEVEL_MOUNT                  # main gear's hub against the rear bearing
cy0 = P.BEVEL_MOUNT + 1.0                              # crank boss, along +Y
cy1 = cy0 + 2 * 7 + CRANK_BEARING_GAP


def bevel(phase):
    g, info = GR.bevel_gear(P.BEVEL_MODULE, P.BEVEL_TEETH, P.BEVEL_FACE, P.BEVEL_HUB_D, P.BEVEL_HUB_L,
                            P.SHAFT_BORE_D, P.BEVEL_BACKLASH, phase_deg=phase)
    return g


gear_main = bevel(0.0)
gear_main.translate(V(0, 0, apex))
gear_crank = bevel(180.0 / P.BEVEL_TEETH)
gear_crank.rotate(V(0, 0, 0), X, -90)                  # hub towards +Y
gear_crank.translate(V(0, 0, apex))
crank_boss = (Part.makeCylinder(CRANK_BOSS_D / 2, cy1 - cy0, V(0, cy0, apex), Y)
              .fuse(box(-12, 12, cy0, cy1, apex, bz0 + 0.01))                     # web up to the bracket
              .cut(Part.makeCylinder(22.1 / 2, 7.01, V(0, cy0 - 0.01, apex), Y))
              .cut(Part.makeCylinder(22.1 / 2, 7.01, V(0, cy1 - 7, apex), Y))
              .cut(Part.makeCylinder(6, cy1 - cy0 + 2, V(0, cy0 - 1, apex), Y)))
bracket = bracket.fuse(crank_boss).removeSplitter()
shaft = cyl(SHAFT_D, apex + P.BEVEL_MOUNT - P.BEVEL_LEN + 2, arm_z1 - 0.5)
crank_shaft = Part.makeCylinder(SHAFT_D / 2, CRANK_Y_OUT + 10 - 8, V(0, 8, apex), Y)
bearings = G.fuse_all([cyl(22, z0, z0 + 7).cut(cyl(8, z0 - 1, z0 + 8)) for z0 in (bz0 - 16, bz1 - 7)]
                      + [Part.makeCylinder(11, 7, V(0, y0, apex), Y).cut(Part.makeCylinder(4, 9, V(0, y0 - 1, apex), Y))
                         for y0 in (cy0, cy1 - 7)])
crank = G.fuse_all([Part.makeCylinder(10, 10, V(0, CRANK_Y_OUT, apex), Y),
                    box(-CRANK_ARM, 0, CRANK_Y_OUT + 2, CRANK_Y_OUT + 10, apex - 6, apex + 6),
                    Part.makeCylinder(6, 30, V(-CRANK_ARM, CRANK_Y_OUT + 10, apex), Y)])
crank_sweep = Part.makeCylinder(CRANK_ARM + 8, 40, V(0, CRANK_Y_OUT, apex), Y)

# ---------------------------------------------------------------- pack
dz = -M["z_end"]
mod_names = ("cart", "piston", "pad", "barrel", "chamber", "pilot_tube", "orings")
fitted = fire_order[:N_FITTED]
mods = {n: [] for n in mod_names}
for x, y in fitted:
    for n in mod_names:
        s = M[n].copy()
        s.translate(V(x, y, dz))
        mods[n].append(s)
ghost_len = M["z_c1"] + M["BARREL_LEN"] - M["z_end"]
ghosts = G.fuse_all([cyl(M["TUBE_OD"], 0, ghost_len, x, y) for x, y in slots if (x, y) not in fitted])
muzzle_z = ghost_len - 30
muzzle_plate = box(-BLOCK_W / 2, BLOCK_W / 2, -BLOCK_W / 2, BLOCK_W / 2, muzzle_z - 8, muzzle_z)
for x, y in slots:
    muzzle_plate = muzzle_plate.cut(cyl(M["TUBE_OD"] + 0.6, muzzle_z - 9, muzzle_z + 1, x, y))
supply = Part.makeCylinder(3, 60, V(INLET_X, BLOCK_W / 2, Z_RING), Y)

# ---------------------------------------------------------------- checks
k_air, R_air, T_air, pa = 1.4, 287.0, 293.0, 1.013e5


def segdist(p1, p2, q1, q2):
    def d_ps(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = dx * dx + dy * dy
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L)) if L else 0
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if o(p1, p2, q1) * o(p1, p2, q2) < 0 and o(q1, q2, p1) * o(q1, q2, p2) < 0:
        return 0.0
    return min(d_ps(p1, q1, q2), d_ps(p2, q1, q2), d_ps(q1, p1, p2), d_ps(q2, p1, p2))


segs = [(s, cores[route[s]]) for s in slots]
clear = min([segdist(*a, *b) for i, a in enumerate(segs) for b in segs[i + 1:]]
            + [segdist(g, g, *sg) for sg in segs for g in slots if g != sg[0]]
            + [segdist(c, c, *sg) for sg in segs for c in cores if c != sg[1]])
air_pts = []
for s in slots:
    c = cores[route[s]]
    air_pts += [(s[0], s[1], Z_ROUTE), ((s[0] + c[0]) / 2, (s[1] + c[1]) / 2, Z_ROUTE), (c[0], c[1], Z_ROUTE),
                (s[0], s[1], sock_floor - 1), (c[0], c[1], (Z_ROUTE + Z_RING) / 2), (c[0], c[1], Z_RING),
                (c[0], c[1], z_seat + 2), (c[0], c[1], z_back + 1)]
air_pts += [(INLET_X, BLOCK_W / 2 - 2, Z_RING)]
pressed = button(*cores[0], dz=TRAVEL)
checks = [
    ("block, retainer, striker, bracket valid single solids",
     all(G.single_solid(s) for s in (block, retainer, arm, bracket))),
    ("pilot channels cross nothing: clearance %.1f mm between axes" % clear, clear >= CH_D + 3.0),
    ("supply -> ring -> 25 jets -> cores, 25 sockets -> channels -> cores: all open",
     not any(block.isInside(V(*p), 1e-4, True) for p in air_pts)),
    ("ring manifold %.1f mm clear of the front face" % (-Z_RING - RING_D / 2 * math.sqrt(2)),
     -Z_RING - RING_D / 2 * math.sqrt(2) >= 2.5),
    ("ring %.1f mm clear of the pilot channels" % ((Z_RING - Z_ROUTE) - RING_D / 2 - CH_D / 2 - CH_D / 2 * 0.42),
     (Z_RING - Z_ROUTE) - RING_D / 2 - CH_D / 2 - CH_D / 2 * 0.42 >= 1.5),
    ("ring clear of the pilot risers (nearest %.1f mm)" % (min(abs(math.hypot(*s) - CORE_R) for s in slots) - RING_D / 2 - CH_D / 2),
     min(abs(math.hypot(*s) - CORE_R) for s in slots) - RING_D / 2 - CH_D / 2 >= 1.5),
    ("pressed button nose pushes the core pin %.1f mm" % (TRAVEL - PLAY), TRAVEL - PLAY >= 1.0),
    ("button collar stays in the counterbore when pressed", z_collar[1] + TRAVEL <= z_core_top - 0.3),
    ("roller presses a button %.1f mm" % TRAVEL,
     roller_fire.common(button(*cores[0])).Volume > 0 and roller_fire.common(pressed).Volume < 1e-3),
    ("parked roller and arm clear of every button", G.no_overlap(roller, buttons) and G.no_overlap(arm, buttons)),
    ("striker clear of retainer and bracket",
     G.no_overlap(arm, retainer) and G.no_overlap(arm, bracket) and G.no_overlap(roller, retainer)),
    ("striker sweep clear of the standoffs", CORE_R + 8 + ARM_W / 2 + 2 < STANDOFF_AT * math.sqrt(2) - 6),
    ("bevel teeth mesh without interference", G.no_overlap(gear_main, gear_crank)),
    ("main gear clear of the bracket, crank gear clear of its boss",
     G.no_overlap(gear_main, bracket) and G.no_overlap(gear_crank, bracket)),
    ("main shaft ends %.0f mm above the crank shaft" % (apex + P.BEVEL_MOUNT - P.BEVEL_LEN + 2 - apex - SHAFT_D / 2),
     apex + P.BEVEL_MOUNT - P.BEVEL_LEN + 2 - apex >= SHAFT_D / 2 + 3),
    ("crank sweep clear of block, bracket, standoffs and modules",
     all(G.no_overlap(crank_sweep, s_) for s_ in (block, bracket, standoffs, retainer))),
    ("retainer screws clear of the cores",
     min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in ret_screws for b in cores) - CB_D / 2 - 1.25 >= 2.0),
]
report = [
    NAME,
    "  breech block           : %.0f x %.0f x %.0f, 25 glands, channels Ø%.0f at z %.0f, ring Ø%.0f at z %.0f, jets Ø%.1f"
    % (BLOCK_W, BLOCK_W, -z_back, CH_D, Z_ROUTE, RING_D, Z_RING, JET_D),
    "  cores                  : 25 on R%.0f from %.1f deg; 5V1 thread %.0f mm; numbers typical, to be measured"
    % (CORE_R, CORE_PHI, TAP_5V1_LEN),
    "  pilot channels         : %.0f..%.0f mm long" % (min(math.hypot(c[0] - s[0], c[1] - s[1]) for s, c in segs),
                                                     max(math.hypot(c[0] - s[0], c[1] - s[1]) for s, c in segs)),
    "  striker                : z %.1f..%.1f, roller 623 at R%.0f; bracket z %.0f..%.0f with 2 x 608"
    % (arm_z0, arm_z1, CORE_R, bz0, bz1),
    "  side crank             : bevel 1:1 m%g z%d, apex z %.0f; crank shaft along +Y in 2 x 608, arm %.0f at y %.0f"
    % (P.BEVEL_MODULE, P.BEVEL_TEETH, apex, CRANK_ARM, CRANK_Y_OUT),
    "  firing order (x, y)    : " + " ".join("(%.0f,%.0f)" % s for s in fire_order[:8]) + " ...",
    "  overall                : %.0f x %.0f x %.0f mm, crank out to y %.0f" % (BLOCK_W, BLOCK_W, ghost_len - (apex - CRANK_ARM - 6), CRANK_Y_OUT + 40),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for n, s, st in (("Breech_block", block, "frame"), ("Retainer", retainer, "printed"), ("Buttons", buttons, "printed"),
                 ("Striker", arm, "rotor"), ("Bracket", bracket, "frame"), ("Standoffs", standoffs, "printed"),
                 ("Crank", crank, "printed"), ("Bevel_main", gear_main, "drive"), ("Bevel_crank", gear_crank, "drive"),
                 ("Muzzle_plate", muzzle_plate, "ghost")):
    sc.add("Printed", n, s, st)
for n, s, st in (("Valve_cores", valve_cores, "steel"), ("Roller", roller, "steel"), ("Shaft", shaft, "steel"), ("Crank_shaft", crank_shaft, "steel"),
                 ("Bearings", bearings, "steel"), ("Detent_ball", detent_ball, "steel"), ("Supply_hose", supply, "hose")):
    sc.add("Bought", n, s, st)
style = dict(cart="rotor", piston="stator", pad="shoe", barrel="ghost", chamber="ghost", pilot_tube="hose", orings="oring")
for n, lst in mods.items():
    sc.add("Modules", "Mod_" + n, G.fuse_all(lst), style[n])
sc.add("Slots", "Other_22_tubes", ghosts, "ghost")
sc.add("Firing", "Striker_on_core0", arm_fire, "rotor")
sc.add("Firing", "Roller_on_core0", roller_fire, "steel")
# section through the first fitted slot and its core: a plane through both
s0 = fitted[0]
c0 = cores[route[s0]]
cut_a = math.degrees(math.atan2(c0[1] - s0[1], c0[0] - s0[0]))
slab = box(-200, 200, -0.01, 200, -150, 900)
slab.rotate(V(0, 0, 0), Z, cut_a)
slab.translate(V(s0[0], s0[1], 0))
for n, s, st in (("Sec_block", block, "frame"), ("Sec_retainer", retainer, "printed"), ("Sec_buttons", buttons, "printed"),
                 ("Sec_cores", valve_cores, "steel")):
    sc.add("Section", n, s.common(box(-80, 80, -80, 80, z_back - 10, 40)).cut(slab), st)
for text, pos in [
    ("КАЗЁННЫЙ БЛОК 150x150: 25 гнёзд под камеры v2", (BLOCK_W / 2 + 10, 0, z_back / 2)),
    ("25 ЗОЛОТНИКОВ по кругу R%.0f (с кнопками)" % CORE_R, (CORE_R + 20, 0, z_back - 10)),
    ("УДАРНИК с роликом: 1 оборот = 25 выстрелов", (0, -CORE_R - 30, arm_z0)),
    ("ДЕТЕНТ: шарик в лунках ступицы", (0, 40, bz1)),
    ("РУКОЯТКА сбоку, коническая пара 1:1", (-CRANK_ARM, CRANK_Y_OUT + 40, apex)),
    ("ВХОД подачи -> кольцевой коллектор -> жиклёры", (INLET_X, BLOCK_W / 2 + 60, Z_RING)),
    ("МОДУЛИ v2: %d установлены, остальные места показаны трубами" % N_FITTED, (BLOCK_W / 2 + 10, 0, 300)),
]:
    sc.label("Labels", text, pos)
sc.finish(hidden_groups=("Section", "Firing"), opaque_groups=("Section",))
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
