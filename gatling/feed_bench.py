# -*- coding: utf-8 -*-
"""
Feed bench for the gatling: a hand-cranked pack mock fed by a star geared to it, no air.

Six front_cover_feed chutes (the station's own gutter, taken from
gatling/linear_breech.py as a library) ride a disk at the pack radius. A
three-pocket star turns twice per disk turn (spur 58/29, module 2.5) on an
axis parallel to the pack shaft. The pocket centres sit on half the radius of
the ball centres in the chutes and the axes are that sum apart, so star and
pack roll on each other like a gear pair: at the handoff a pocket and a chute
move at the same speed, and the ball is set down on the gutter instead of
being dropped into a moving target (docs/gatling.md, plan, question 6; chosen
2026-11-19). The pockets are generated, not drawn: the star blank is cut by
the ball at every pose of the mesh, the way a hob cuts a gear, so the ball
leaves its pocket along its own relative path and no lobe tip sweeps through it.

The star is filled at its top from a cup through a neck. The neck's
downstream wall is the strike-off: it ends on the shroud radius, so the ball
in a pocket passes under it while the next one, resting on a lobe, meets it
below its centre. A TPU strip on that edge reaches into the pocket ball's path
and bends; its length is the bench's tuning knob for soft balls. The shroud
keeps the ball in its pocket on the way down; the guard keeps it on the
gutter until the fitting tip would have caught it; a kicker throws it into a
tray so a run can be counted.

A rigid ball rests on the open gutter's inner rims, BALL_LIFT (≈5.6 mm) above
the barrel axis: the star, the guard and the checks use that radius.

Stationary frame: a base plate under the pack and a front plate ahead of the
chutes that carries the pack shaft's front bearing, the star shaft's bearing,
the seat ring with the neck and shroud, and the guard. The pack shaft runs in
two 6000 behind the disk and one in the front plate. Base and front plate are
plate stock (plywood / MDF), the rest prints.

From branch cursor/gatling-feed-bench-2946 (2026-11-13/14): disk, chutes,
guard, kicker, tray, cup and crank. Its auger (A1) and finger escapement (A4)
meters and its gravity-drop star stay in that branch.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/feed_bench.py').read())"

PELLET_D (default 23.8) can be set before exec. Exports: exports/gatling_feed_bench/
Library: set FEED_BENCH_LIBRARY = True before exec (checks only, no scene or export).
"""
import math
import os
import sys
import time

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
import importlib
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
for _m in (G, FV, GR):
    importlib.reload(_m)

try:
    PELLET_D
except NameError:
    PELLET_D = 23.8
try:
    FEED_BENCH_LIBRARY
except NameError:
    FEED_BENCH_LIBRARY = False
# 2026-11-22: the ball lies in the breech's fixed trough (linear_breech BREECH_TRAY), not on a
# gutter on the QEV's nose; the chutes here are the troughs, moved by the stroke into this
# bench's frame (ball at the closed tip). False builds the old gutter chutes.
try:
    BREECH_TRAY
except NameError:
    BREECH_TRAY = True
_T0 = time.time()


def _progress(text):
    print("feed bench %5.1f s: %s" % (time.time() - _T0, text), flush=True)

OUT_DIR = os.path.join(REPO, "exports", "gatling_feed_bench")
NAME = "gatling_feed_bench"

# ---------------------------------------------------------------- station gutter (library)
_lib = {"REPO": REPO, "GATLING_LINEAR_BREECH_LIBRARY": True, "SHOW_OPEN": False, "BREECH_TRAY": BREECH_TRAY,
        "TRAY_PACK_R": 67.0}                     # = PACK_R below
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), _lib)
front_cover_feed = _lib["feed_chute"]             # the name stays: the gutter on the cover, or the trough
z_tip = _lib["z_tip"]
FIT_INSERT = _lib["FIT_IN_BARREL"]                # the fitting's run inside the barrel, closed
STROKE = _lib["STROKE"]
LIB_PELLET = _lib["PELLET_D"]
FEED_ID = _lib["feed_id"]
FEED_OD = _lib["feed_od"]
CRADLE_Y_TOP = _lib["CRADLE_Y_TOP"]
del _lib

PACK_R = 67.0                    # = breech_pack / breech_mechanism (2026-11-19)
N_STATION = 6
# Station 0 sits under the star. phi 180 is +X (up); phi 90 is +Y (crank side).
STATION_PHI = [180.0 + i * (360.0 / N_STATION) for i in range(N_STATION)]
Z_BALL = z_tip + PELLET_D / 2.0  # ball against the fitting tip, on the gutter
# A rigid ball rests on the inner rims of the open gutter (cut at CRADLE_Y_TOP), or, in a
# trough wider than its rims, on the bottom (0.05 under the axis in the Ø23.9 trough).
_rim_x2 = (FEED_ID / 2.0) ** 2 - CRADLE_Y_TOP ** 2
BALL_LIFT = max(CRADLE_Y_TOP + math.sqrt(max(0.0, (PELLET_D / 2.0) ** 2 - _rim_x2)),
                -(FEED_ID - PELLET_D) / 2.0)
R_BALL = PACK_R + BALL_LIFT

# 6000: 10 x 26 x 8 on the pack shaft; 608: 8 x 22 x 7 on the star shaft.
SHAFT_D = 10.0
BRG_OD, BRG_W = 26.0, 8.0
BRG_BORE = SHAFT_D + 0.3          # drawing gap so the fit is not a boolean clash
HOUSE_BORE = BRG_OD + 0.3
STAR_SHAFT_D = 8.0
SBRG_OD, SBRG_W = 22.0, 7.0

# Star geared to the pack. Pitch radii of the gears are the ball radius and the
# pocket radius, so the pocket and the chute roll on each other.
# 2026-11-22, the trough: the ball circle came in to R 66.95, and a 2:1 star (on 1.5 x R = 100.4) put
# its drive into the pack's hub; 4 pockets at 1.5 turns stand it on 1.667 x R = 111.6, out past
# the old 108.75. Pockets x turns = 6 balls per pack turn either way.
STAR_POCKETS, STAR_TURNS = (4, 1.5) if BREECH_TRAY else (3, 2)
GEAR_M = 2.5
GEAR_FACE = 8.0
GEAR_BACKLASH = 0.40
_pin0 = R_BALL * (1.0 + 1.0 / STAR_TURNS) / (GEAR_M * (1 + STAR_TURNS) / 2.0)
STAR_PIN = min((p_ for p_ in range(int(_pin0) - 3, int(_pin0) + 4) if abs(STAR_TURNS * p_ - round(STAR_TURNS * p_)) < 1e-9),
               key=lambda p_: abs(p_ - _pin0))      # the wheel's teeth STAR_TURNS x the pin's, whole
STAR_WHEEL = int(round(STAR_TURNS * STAR_PIN))
# 2026-11-22: the star stands where pocket and ball speeds match exactly, and the printed bench
# gears take the module that fits (2.48 for the trough's R_BALL 66.95; m 2.5 left 2.5 % slip).
X_STAR = R_BALL * (1.0 + 1.0 / STAR_TURNS)          # centre distance, star axis on +X
GEAR_M = 2.0 * X_STAR / (STAR_PIN + STAR_WHEEL)
POCKET_R = X_STAR - R_BALL                           # pocket centres on the star
SPEED_RATIO = STAR_TURNS * POCKET_R / R_BALL          # pocket / ball speed at the handoff
POCKET_CLEAR = 0.6                # ball to pocket wall
STAR_R = POCKET_R + 4.0           # lobe radius
STAR_T = 16.0                     # along Z, centred on the ball (it pokes 3.9 out of each face)
MESH_SPAN = 26.0                  # pack degrees each side of the handoff cut into the star
MESH_STEP = 1.0
SHROUD_GAP = 1.0                  # ball in a pocket to the shroud
SHROUD_WALL = 3.0
SHROUD_SIDE = 3.0
SHROUD_END = 130.0                # star angle (0 = up, handoff at 180) where the shroud stops
SHROUD_WEB_END = 120.0            # the shroud's tie to the front plate stops here
NECK_ID = PELLET_D + 1.6          # 25.4, the bench feeder's throat
NECK_WALL = 3.0
NECK_H = 30.0                     # neck above the lobes: one ball waits in it
LIP_T, LIP_REACH, LIP_W = 1.4, 2.0, 16.0   # TPU strip on the strike-off edge

SHROUD_R_IN = POCKET_R + PELLET_D / 2.0 + SHROUD_GAP
SHROUD_R_OUT = SHROUD_R_IN + SHROUD_WALL
SIDE_Z0 = NECK_ID / 2.0           # side walls of the shroud: outside the star, beside the ball
SIDE_Z1 = SIDE_Z0 + SHROUD_SIDE

# Low wide cup (from the branch): 30..50 balls without a tall tower.
CUP_ID = 124.0
CUP_WALL = 3.2
CUP_H = 36.0
CUP_FLOOR = 3.0
PACK_LO, PACK_HI = 0.55, 0.64
RING_OD, RING_ID, RING_T = 80.0, 42.0, 6.0

GUARD_GAP = 1.5                   # ball on the gutter to the guard
GUARD_WALL = 3.2
GUARD_HZ = PELLET_D / 2.0 + 2.0   # over the ball band only; the cover flange is lower
GUARD_R_IN = R_BALL + PELLET_D / 2.0 + GUARD_GAP
GUARD_R_OUT = GUARD_R_IN + GUARD_WALL

DISK_T = 8.0
CRANK_R = 80.0                    # knob clears the base plate (R + knob < 103)
BASE_T = 10.0
FRONT_T = 8.0

X = App.Vector(1, 0, 0)
Y = App.Vector(0, 1, 0)
Z = App.Vector(0, 0, 1)
V = App.Vector
O = V(0, 0, 0)


def polar(phi, radius, z=0.0):
    """Point at pack angle phi (180 = +X up, 90 = +Y)."""
    a = math.radians(phi)
    return V(-radius * math.cos(a), radius * math.sin(a), z)


def chute_matrix(phi):
    """Rigid map of the station frame onto pack angle phi. Local +Y is radial out, +Z the barrel."""
    a = math.radians(phi)
    c, s = math.cos(a), math.sin(a)
    return App.Matrix(s, -c, 0, -PACK_R * c,
                      c, s, 0, PACK_R * s,
                      0, 0, 1, 0,
                      0, 0, 0, 1)


def place(shape, phi):
    s = shape.copy()
    s.transformShape(chute_matrix(phi))
    return s


def tube_x(od, idd, x0, x1, y=0.0, z=0.0):
    h = x1 - x0
    outer = Part.makeCylinder(od / 2.0, h, V(x0, y, z), X)
    inner = Part.makeCylinder(idd / 2.0, h + 4.0, V(x0 - 2.0, y, z), X)
    return outer.cut(inner)


def sector(r_in, r_out, a0, a1, z0, z1, cx=0.0, cy=0.0):
    """Annular sector about an axis along Z through (cx, cy); math angles a0 < a1 in degrees."""
    s = Part.makeCylinder(r_out, z1 - z0, V(cx, cy, z0), Z, a1 - a0)
    s.rotate(V(cx, cy, 0), Z, a0)
    if r_in > 0.0:
        s = s.cut(Part.makeCylinder(r_in, z1 - z0 + 2.0, V(cx, cy, z0 - 1.0)))
    return s


def spur_z(teeth, module, face, bore, phase_deg=0.0):
    """Spur gear, axis +Z from z = 0, tooth 0 at phase_deg."""
    outline = GR.tooth_outline(teeth, module, 1.0, GEAR_BACKLASH)
    pts = [V(x, y, 0) for x, y in outline]
    pts.append(pts[0])
    g = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, face))
    g = g.cut(Part.makeCylinder(bore / 2.0, face + 4.0, V(0, 0, -2.0)))
    if phase_deg:
        g.rotate(O, Z, phase_deg)
    return g


def open_fraction(phi):
    """Breech open fraction on the cam law, cosine ramps. 0 closed, 1 fully open."""
    p = phi % 360.0
    if 30.0 <= p < 120.0:
        u = (p - 30.0) / 90.0
        return 0.5 * (1.0 - math.cos(math.pi * u))
    if 120.0 <= p < 240.0:
        return 1.0
    if 240.0 <= p < 330.0:
        u = (p - 240.0) / 90.0
        return 0.5 * (1.0 + math.cos(math.pi * u))
    return 0.0


def tip_insertion(phi):
    """Millimetres the fitting tip is inside the bore. Negative: still behind the face."""
    return FIT_INSERT - open_fraction(phi) * STROKE


def close_capture_phi(depth):
    """First close angle at which the tip has entered the bore by `depth` mm."""
    phi = 240.0
    while phi < 330.0 and tip_insertion(phi) < depth:
        phi += 0.05
    return phi


def ball_rest(phi, radius=None):
    return Part.makeSphere(PELLET_D / 2.0 if radius is None else radius, polar(phi, R_BALL, Z_BALL))


def star_turn(shape, deg):
    s = shape.copy()
    s.rotate(V(X_STAR, 0, 0), Z, deg)
    return s


def pocket_center(theta):
    a = math.radians(theta)
    return V(X_STAR + POCKET_R * math.cos(a), POCKET_R * math.sin(a), Z_BALL)


# The guard ends when the tip is half a pellet inside the bore (bore and nose
# then cage the ball). The kicker works just past it.
GUARD_PHI1 = close_capture_phi(PELLET_D / 2.0)
DUMP_PHI = GUARD_PHI1 + 6.0

# ---------------------------------------------------------------- six chutes, disk, shaft
chutes = [place(front_cover_feed, phi) for phi in STATION_PHI]
Z_COVER_MIN = front_cover_feed.BoundBox.ZMin
Z_COVER_MAX = front_cover_feed.BoundBox.ZMax
# The chute above the cover flange: what the guard, star and kicker can meet.
chute_hi =front_cover_feed.common(Part.makeBox(200, 200, Z_COVER_MAX + 1.0 - (Z_BALL - 18.0),
                                                V(-100, -100, Z_BALL - 18.0)))

DISK_R = PACK_R + 40.0
z_disk1 = Z_COVER_MIN - 1.2
z_disk0 = z_disk1 - DISK_T
z_brg_f1 = z_disk0 - 3.0
z_brg_f0 = z_brg_f1 - BRG_W
z_brg_r1 = z_brg_f0 - 14.0
z_brg_r0 = z_brg_r1 - BRG_W
z_crank0 = z_brg_r0 - 14.0
# Gears just ahead of the chutes, the front plate just ahead of the gears.
Z_GEAR0 = Z_COVER_MAX + 3.0
Z_GEAR1 = Z_GEAR0 + GEAR_FACE
Z_FRONT0 = Z_GEAR1 + 4.0
Z_FRONT1 = Z_FRONT0 + FRONT_T

disk = Part.makeCylinder(DISK_R, DISK_T, V(0, 0, z_disk0))
disk = disk.fuse(Part.makeCylinder(16.0, 4.0, V(0, 0, z_disk1 - 4.0)))
disk = disk.cut(Part.makeCylinder(SHAFT_D / 2.0 + 0.15, 80.0, V(0, 0, z_brg_f0 - 2.0)))
for phi in STATION_PHI:
    c = polar(phi, PACK_R, 0.0)
    # Pads the chutes sit on, 0.4 mm shy of the cover so the print is a separate part.
    disk = disk.fuse(Part.makeCylinder(16.0, 4.0, V(c.x, c.y, z_disk1 - 0.4)))
disk = disk.removeSplitter()

shaft = Part.makeCylinder(SHAFT_D / 2.0, Z_FRONT1 + 3.0 - (z_crank0 - 4.0), V(0, 0, z_crank0 - 4.0))


def bearing_at(z0, od=BRG_OD, bore=BRG_BORE, w=BRG_W, x=0.0):
    return Part.makeCylinder(od / 2.0, w, V(x, 0, z0)).cut(
        Part.makeCylinder(bore / 2.0, w + 2.0, V(x, 0, z0 - 1.0)))


brg_front = bearing_at(z_brg_f0)
brg_rear = bearing_at(z_brg_r0)
brg_nose = bearing_at(Z_FRONT0, w=FRONT_T)
brg_star = bearing_at(Z_FRONT0 + (FRONT_T - SBRG_W) / 2.0, SBRG_OD, STAR_SHAFT_D + 0.3, SBRG_W, X_STAR)

# Base plate under the pack (normal to X), long enough for the front plate.
BASE_TOP = -(PACK_R + 36.0)
base = Part.makeBox(BASE_T, 200.0, Z_FRONT1 - (z_crank0 - 16.0),
                    V(BASE_TOP - BASE_T, -100.0, z_crank0 - 16.0))


def housing(z0):
    """Pillow block: feet on the base, bore on the shaft."""
    block = Part.makeBox(28.0, 44.0, BRG_W + 5.0, V(-14.0, -22.0, z0 - 4.0))
    body = Part.makeBox(14.0 - BASE_TOP, 44.0, BRG_W + 5.0, V(BASE_TOP, -22.0, z0 - 4.0))
    body = body.fuse(block)
    body = body.cut(Part.makeCylinder(HOUSE_BORE / 2.0, BRG_W + 14.0, V(0, 0, z0 - 7.0)))
    for sy in (-16.0, 16.0):
        body = body.cut(Part.makeCylinder(2.7, 30.0, V(BASE_TOP - 2.0, sy, z0 + BRG_W / 2.0), X))
    return body.removeSplitter()


house_front = housing(z_brg_f0)
house_rear = housing(z_brg_r0)

# Crank at phi 90 (+Y), aft of the rear bearing; the knob points aft, away from the block.
crank_hub = Part.makeCylinder(14.0, 8.0, V(0, 0, z_crank0))
crank_hub = crank_hub.cut(Part.makeCylinder(SHAFT_D / 2.0 + 0.15, 12.0, V(0, 0, z_crank0 - 2.0)))
arm = Part.makeBox(14.0, CRANK_R, 8.0, V(-7.0, 6.0, z_crank0))
knob = Part.makeCylinder(11.0, 30.0, V(0, CRANK_R, z_crank0 - 28.0))
crank = crank_hub.fuse(arm).fuse(knob).removeSplitter()

# ---------------------------------------------------------------- gears
_pin_phase = 0.0 if STAR_PIN % 2 else 180.0 / STAR_PIN   # gap of the pinion faces the wheel
pack_gear = spur_z(STAR_WHEEL, GEAR_M, GEAR_FACE, SHAFT_D + 0.4)
pack_gear.translate(V(0, 0, Z_GEAR0))
star_gear = spur_z(STAR_PIN, GEAR_M, GEAR_FACE, STAR_SHAFT_D + 0.4, _pin_phase)
star_gear.translate(V(X_STAR, 0, Z_GEAR0))
STAR_GEAR_RA = GEAR_M * (STAR_PIN + 2) / 2.0
PACK_GEAR_RA = GEAR_M * (STAR_WHEEL + 2) / 2.0
star_shaft = Part.makeCylinder(STAR_SHAFT_D / 2.0, Z_FRONT1 + 3.0 - (Z_BALL - STAR_T / 2.0 - 2.0),
                               V(X_STAR, 0, Z_BALL - STAR_T / 2.0 - 2.0))

# ---------------------------------------------------------------- star, cut by the ball along the mesh
z_star0, z_star1 = Z_BALL - STAR_T / 2.0, Z_BALL + STAR_T / 2.0
star_blank = Part.makeCylinder(STAR_R, STAR_T, V(X_STAR, 0, z_star0))
star_blank = star_blank.cut(Part.makeCylinder((STAR_SHAFT_D + 0.4) / 2.0, STAR_T + 4.0,
                                              V(X_STAR, 0, z_star0 - 2.0)))
# The star is a prism and holds the ball by its equator, so each pose cuts a
# cylinder of the ball's equator radius through the whole thickness (parallel
# cylinders cut cheaply; a fan of spheres does not).
_progress("cutting the star along the mesh")
_cut0 = []
_rc = PELLET_D / 2.0 + POCKET_CLEAR
_n = int(round(2.0 * MESH_SPAN / MESH_STEP))
for _i in range(_n + 1):
    _d = -MESH_SPAN + _i * MESH_STEP
    _p = polar(180.0 + _d, R_BALL)
    # Pack at 180 + d turns the star by STAR_TURNS * d; bring the ball into the star's frame.
    _a = math.radians(-STAR_TURNS * _d)
    _qx = X_STAR + (_p.x - X_STAR) * math.cos(_a) - _p.y * math.sin(_a)
    _qy = (_p.x - X_STAR) * math.sin(_a) + _p.y * math.cos(_a)
    if math.hypot(_qx - X_STAR, _qy) - _rc < STAR_R:
        _cut0.append(Part.Face(Part.Wire(Part.makeCircle(_rc, V(_qx, _qy, z_star0 - 2.0)))))
# Union of the circles in the plane, then one prism per pocket.
_pocket2d = _cut0[0].fuse(_cut0[1:]).removeSplitter()
_prisms = [f.extrude(V(0, 0, STAR_T + 4.0)) for f in _pocket2d.Faces]
_pocket_prism = _prisms[0] if len(_prisms) == 1 else G.fuse_all(_prisms).removeSplitter()
star_cutters = [star_turn(_pocket_prism, _k * 360.0 / STAR_POCKETS) for _k in range(STAR_POCKETS)]
star = star_blank.cut(star_cutters).removeSplitter()
_progress("star cut with %d poses per pocket" % len(_cut0))

# ---------------------------------------------------------------- neck, strike-off, shroud, seat ring
X_SEAT = X_STAR + STAR_R + NECK_H
_x_neck0 = X_STAR + STAR_R - 8.0
# Solid neck with a funnel head, bored once (a second coincident bore breaks the boolean).
_fun_h = 12.0
neck = Part.makeCylinder(NECK_ID / 2.0 + NECK_WALL, X_SEAT - _x_neck0, V(_x_neck0, 0, Z_BALL), X)
neck = neck.fuse(Part.makeCylinder(RING_ID / 2.0 + 3.0, _fun_h, V(X_SEAT - _fun_h, 0, Z_BALL), X))
_bore = Part.makeCylinder(NECK_ID / 2.0, X_SEAT - _fun_h - _x_neck0 + 4.0, V(_x_neck0 - 2.0, 0, Z_BALL), X)
_bore = _bore.fuse(Part.makeCone(NECK_ID / 2.0, RING_ID / 2.0, _fun_h, V(X_SEAT - _fun_h, 0, Z_BALL), X))
_bore = _bore.fuse(Part.makeCylinder(RING_ID / 2.0, 2.0, V(X_SEAT, 0, Z_BALL), X))
neck = neck.cut(_bore)
_zb0, _zb1 = Z_BALL - SIDE_Z1 - 6.0, Z_BALL + SIDE_Z1 + 6.0
# Upstream: the neck follows the lobes 0.6 mm off.
neck = neck.cut(Part.makeCylinder(STAR_R + 0.6, _zb1 - _zb0, V(X_STAR, 0, _zb0)))
# Downstream half (+Y) inside the ball's band: the strike-off ends on the
# shroud radius, so the carried ball passes under it. Outside the band the
# neck's side walls run on down as guides, like the shroud's side walls.
_strike = Part.makeCylinder(SHROUD_R_IN, 2.0 * SIDE_Z0, V(X_STAR, 0, Z_BALL - SIDE_Z0)).common(
    Part.makeBox(60.0, 60.0, 2.0 * SIDE_Z0 + 2.0, V(X_STAR, 0.0, Z_BALL - SIDE_Z0 - 1.0)))
neck = neck.cut(_strike).removeSplitter()
X_STRIKE = X_STAR + math.sqrt(SHROUD_R_IN ** 2 - (NECK_ID / 2.0) ** 2)
THETA_STRIKE = math.degrees(math.asin((NECK_ID / 2.0) / SHROUD_R_IN))

ring = tube_x(RING_OD, RING_ID, X_SEAT, X_SEAT + RING_T, 0.0, Z_BALL)

shroud_outer = sector(SHROUD_R_IN, SHROUD_R_OUT, THETA_STRIKE, SHROUD_END,
                      Z_BALL - SIDE_Z1, Z_BALL + SIDE_Z1, X_STAR, 0.0)
shroud_side_a = sector(STAR_R + 1.0, SHROUD_R_OUT, 0.0, SHROUD_END,
                       Z_BALL + SIDE_Z0, Z_BALL + SIDE_Z1, X_STAR, 0.0)
shroud_side_b = sector(STAR_R + 1.0, SHROUD_R_OUT, 0.0, SHROUD_END,
                       Z_BALL - SIDE_Z1, Z_BALL - SIDE_Z0, X_STAR, 0.0)
# Tie to the front plate, outside the star gear and the pack gear.
shroud_web = sector(SHROUD_R_IN, SHROUD_R_OUT, THETA_STRIKE, SHROUD_WEB_END,
                    Z_BALL + SIDE_Z1 - 0.5, Z_FRONT0, X_STAR, 0.0)
# No removeSplitter here: on this fuse it returns an invalid solid (and, sharing
# sub-shapes, spoils the neck it was built from).
feed_head = G.fuse_all([ring, neck, shroud_outer, shroud_side_a, shroud_side_b, shroud_web])

# TPU strip on the strike-off, on the inner face of the downstream wall.
lip = Part.makeBox(LIP_REACH + 8.0, LIP_T, LIP_W,
                   V(X_STRIKE - LIP_REACH, NECK_ID / 2.0 - LIP_T, Z_BALL - LIP_W / 2.0))

# Cup on the ring: shoulder 0.15 mm off, spigot in the bore.
_cup0 = X_SEAT + RING_T + 0.15
cup_outer = Part.makeCylinder(CUP_ID / 2.0 + CUP_WALL, CUP_H + CUP_FLOOR, V(_cup0, 0, Z_BALL), X)
cup_void_shape = Part.makeCylinder(CUP_ID / 2.0, CUP_H + 2.0, V(_cup0 + CUP_FLOOR, 0, Z_BALL), X)
throat = Part.makeCylinder(RING_ID / 2.0 - 1.0, CUP_FLOOR + 4.0, V(_cup0 - 2.0, 0, Z_BALL), X)
cup = cup_outer.cut(cup_void_shape).cut(throat)
spigot = Part.makeCylinder((RING_ID - 0.5) / 2.0, 5.0, V(_cup0 - 5.0, 0, Z_BALL), X)
spigot = spigot.cut(Part.makeCylinder(RING_ID / 2.0 - 1.0, 8.0, V(_cup0 - 6.0, 0, Z_BALL), X))
cup = cup.fuse(spigot).removeSplitter()
CUP_VOID = math.pi * (CUP_ID / 2.0) ** 2 * CUP_H
BALL_VOL = 4.0 / 3.0 * math.pi * (PELLET_D / 2.0) ** 3

# ---------------------------------------------------------------- guard
# Starts where the star (lobes, gear) has left the guard circle on the way out.
_rho = max(STAR_R, STAR_GEAR_RA) + 1.0
_xg = (X_STAR ** 2 + GUARD_R_IN ** 2 - _rho ** 2) / (2.0 * X_STAR)
GUARD_PHI0 = 180.0 + math.degrees(math.atan2(math.sqrt(max(0.0, GUARD_R_IN ** 2 - _xg ** 2)), _xg)) + 2.0
guard = sector(GUARD_R_IN, GUARD_R_OUT, 180.0 - GUARD_PHI1, 180.0 - GUARD_PHI0,
               Z_BALL - GUARD_HZ, Z_FRONT0).removeSplitter()

# ---------------------------------------------------------------- front plate
_fy0 = -(GUARD_R_OUT + 8.0)
_fy1 = max(SHROUD_R_OUT + 8.0, 40.0)
front_plate = Part.makeBox(X_SEAT + RING_T - (BASE_TOP - BASE_T), _fy1 - _fy0, FRONT_T,
                           V(BASE_TOP - BASE_T, _fy0, Z_FRONT0))
front_plate = front_plate.cut(Part.makeCylinder(HOUSE_BORE / 2.0, FRONT_T + 4.0, V(0, 0, Z_FRONT0 - 2.0)))
front_plate = front_plate.cut(Part.makeCylinder((SBRG_OD + 0.3) / 2.0, FRONT_T + 4.0,
                                                V(X_STAR, 0, Z_FRONT0 - 2.0)))
front_plate = front_plate.removeSplitter()

# ---------------------------------------------------------------- kicker and tray at the dump angle
# Station frame: +Y radial out, +X toward increasing phi, +Z barrel. The gutter
# metal is at local Y <= CRADLE_Y_TOP, so a blade in +Y only meets the ball.
kicker_local = Part.makeBox(8.0, 16.0, 12.0, V(-4.0, PELLET_D / 2.0 - 8.0, Z_BALL - 6.0))
ramp_local = Part.makeBox(10.0, 22.0, 14.0, V(2.0, PELLET_D / 2.0 - 2.0, Z_BALL - 7.0))
tray_local = Part.makeBox(28.0, 24.0, 18.0, V(8.0, PELLET_D / 2.0 + 4.0, Z_BALL - 16.0))
tray_local = tray_local.cut(Part.makeBox(22.0, 18.0, 14.0, V(8.0, PELLET_D / 2.0 + 7.0, Z_BALL - 14.0)))
kicker_tray = place(kicker_local.fuse(ramp_local).fuse(tray_local), DUMP_PHI)
_tb = kicker_tray.BoundBox
_leg = Part.makeBox(_tb.XMin + 4.0 - BASE_TOP, 8.0, 8.0,
                    V(BASE_TOP, (_tb.YMin + _tb.YMax) / 2.0 - 4.0, (_tb.ZMin + _tb.ZMax) / 2.0 - 4.0))
kicker_tray = kicker_tray.fuse(_leg).removeSplitter()

# Reference balls (not printed, not in the clearance checks unless named there).
ball_next = Part.makeSphere(PELLET_D / 2.0, V(X_STAR + STAR_R + PELLET_D / 2.0, 0, Z_BALL))
ball_carried = Part.makeSphere(PELLET_D / 2.0, pocket_center(70.0))
ball_handoff = ball_rest(180.0)
ball_on_gutter = ball_rest(240.0)

# ---------------------------------------------------------------- checks
_progress("checks")
checks = []


def check(ok, text):
    checks.append((text, bool(ok)))


def gap(a, b):
    return a.distToShape(b)[0]


# Six chutes on the pack radius, 60 deg apart.
radii = [math.hypot(chute_matrix(p).multiply(V(0, 0, Z_BALL)).x,
                    chute_matrix(p).multiply(V(0, 0, Z_BALL)).y) for p in STATION_PHI]
check(all(abs(r - PACK_R) < 0.05 for r in radii), "6 chutes on R %.1f" % PACK_R)
_cb = chutes[0].BoundBox
check(abs(_cb.ZMax - Z_COVER_MAX) < 0.01 and _cb.XMax < PACK_R + 26.0,
      "chutes placed rigidly (top chute reaches x %.1f, cover r 25)" % _cb.XMax)
# Ball on the open gutter: on the rims, not through them.
_ball0 = ball_rest(180.0)
_rest_hit = chutes[0].common(_ball0).Volume
_rest_low = chutes[0].common(Part.makeSphere(PELLET_D / 2.0, polar(180.0, R_BALL - 0.3, Z_BALL))).Volume
check(_rest_hit < 0.5 and _rest_low > 0.05,
      "ball rests on the gutter rims %.2f mm above the barrel axis (clear %.2f mm3, 0.3 lower hits %.2f)"
      % (BALL_LIFT, _rest_hit, _rest_low))

# Kinematics: pitch radii, speed match, handoff point, six balls per turn.
check(abs(GEAR_M * STAR_WHEEL / 2.0 + GEAR_M * STAR_PIN / 2.0 - X_STAR) < 1e-6
      and STAR_POCKETS * STAR_TURNS == N_STATION,
      "gears %d/%d m%.3f, centre distance %.2f; %d pockets x %g turns = %g balls per pack turn"
      % (STAR_WHEEL, STAR_PIN, GEAR_M, X_STAR, STAR_POCKETS, STAR_TURNS, STAR_POCKETS * STAR_TURNS))
check(abs(SPEED_RATIO - 1.0) <= 0.02,
      "pocket / chute speed at the handoff %.3f (pocket R %.2f x %d, ball R %.2f)"
      % (SPEED_RATIO, POCKET_R, STAR_TURNS, R_BALL))
_handoff = (pocket_center(180.0) - polar(180.0, R_BALL, Z_BALL)).Length
check(_handoff < 0.3, "pocket centre on the gutter's ball seat at the handoff (%.2f mm)" % _handoff)

# Gear mesh at a few poses.
_mesh_ov = 0.0
for _d in (0.0, 1.7, 3.1, 4.6):
    _pg = pack_gear.copy()
    _pg.rotate(O, Z, -_d)
    _sg = star_turn(star_gear, STAR_TURNS * _d)
    _mesh_ov = max(_mesh_ov, _pg.common(_sg).Volume)
check(_mesh_ov < 1.0, "gears mesh without overlap over a tooth (worst %.2f mm3)" % _mesh_ov)

# Star: one solid, three pockets each holding one ball.
check(G.single_solid(star), "star one solid (%.0f mm3)" % star.Volume)
# Unturned star: pockets at 180, 300 and 60 deg; probe the one under the shroud.
# The pocket under the shroud (60 deg with 3 pockets, 90 with 4).
_PA = next(a_ % 360.0 for a_ in (180.0 + k_ * 360.0 / STAR_POCKETS for k_ in range(STAR_POCKETS))
           if 15.0 < a_ % 360.0 < SHROUD_END)
_pc = pocket_center(_PA)
_one = Part.makeSphere(PELLET_D / 2.0, _pc)
_two_side = Part.makeSphere(PELLET_D / 2.0, pocket_center(_PA + math.degrees(PELLET_D / POCKET_R)))
_two_out = Part.makeSphere(PELLET_D / 2.0, V(X_STAR + (POCKET_R + PELLET_D) * math.cos(math.radians(_PA)),
                                             (POCKET_R + PELLET_D) * math.sin(math.radians(_PA)), Z_BALL))
_hit_one = star.common(_one).Volume
_hit_side = star.common(_two_side).Volume
_hit_out = feed_head.common(_two_out).Volume
check(_hit_one < 0.5 and _hit_side > 80.0 and _hit_out > 80.0,
      "a pocket holds one ball (clear %.2f mm3); a second beside it hits the star (%.0f), outside it the shroud (%.0f)"
      % (_hit_one, _hit_side, _hit_out))

# Mesh sweep between the generation poses: star vs the gutter, vs the ball
# after the handoff; the carried ball vs the gutter before it.
_progress("mesh sweep")
_band = chute_hi
_worst_gut, _worst_ball, _worst_in = 99.0, 99.0, 0.0
_d = -MESH_SPAN - 2.5
while _d <= MESH_SPAN + 2.6:
    _st = star_turn(star, STAR_TURNS * _d)
    _ch = place(_band, 180.0 + _d)
    _worst_gut = min(_worst_gut, gap(_st, _ch))
    if _d > 0.0:
        _worst_ball = min(_worst_ball, gap(_st, ball_rest(180.0 + _d)))
    elif _d < -0.6:
        _carried = Part.makeSphere(PELLET_D / 2.0, pocket_center(180.0 + STAR_TURNS * _d))
        _worst_in = max(_worst_in, _carried.common(_ch).Volume)
    _d += 1.0
check(_worst_gut >= 0.4, "star clears the passing gutter by %.2f mm (pack +/-%.0f deg)"
      % (_worst_gut, MESH_SPAN + 2.5))
check(_worst_ball >= 0.3, "star lets go of the ball after the handoff (clear %.2f mm)" % _worst_ball)
check(_worst_in < 0.05, "carried ball comes down onto the gutter without cutting it (worst %.3f mm3)"
      % _worst_in)

# Fill and transport: the carried ball under the strike-off and inside the shroud.
_progress("fill and transport")
_head_nolip = feed_head
_worst_carry = 99.0
for _t in range(0, int(SHROUD_END) + 1, 5):
    _worst_carry = min(_worst_carry, gap(Part.makeSphere(PELLET_D / 2.0, pocket_center(float(_t))), _head_nolip))
check(_worst_carry >= 0.4, "carried ball clears the neck and the shroud from fill to %.0f deg (%.2f mm)"
      % (SHROUD_END, _worst_carry))
_hold = (X_STAR + STAR_R + PELLET_D / 2.0) - X_STRIKE
check(_hold >= 3.0, "next ball on a lobe meets the strike-off %.1f mm below its centre" % _hold)
_lip_flex = 0.0
for _t in range(0, 41, 2):
    _ov = lip.common(Part.makeSphere(PELLET_D / 2.0, pocket_center(float(_t))))
    if _ov.Volume > 1e-4:
        _bb = _ov.BoundBox
        _lip_flex = max(_lip_flex, _bb.XLength)
check(0.0 < _lip_flex <= LIP_REACH + 0.5,
      "TPU lip brushes the carried ball and bends up to %.1f mm" % _lip_flex)
_worst_star_head = 99.0
for _t in range(0, 121, 6):
    _worst_star_head = min(_worst_star_head, gap(star_turn(star, float(_t)), feed_head))
check(_worst_star_head >= 0.5, "star turns clear of the neck and shroud (%.2f mm)" % _worst_star_head)
check(gap(star_gear, feed_head) >= 1.0 and gap(pack_gear, feed_head) >= 1.0,
      "gears clear the shroud tie (star %.1f, pack %.1f mm)"
      % (gap(star_gear, feed_head), gap(pack_gear, feed_head)))

# Guard on the lifted ball, from the star to the close angle.
_ins_end = tip_insertion(GUARD_PHI1)
check(280.0 < GUARD_PHI1 < 320.0 and abs(_ins_end - PELLET_D / 2.0) < 0.15,
      "guard %.1f..%.1f deg, tip %.2f mm inside the bore at its end" % (GUARD_PHI0, GUARD_PHI1, _ins_end))
_g240 = gap(guard, ball_rest(240.0))
check(1.0 <= _g240 <= 2.0, "guard gap to the ball on the gutter %.2f mm (want 1..2)" % _g240)
_star_guard = min(gap(star_turn(star, float(_t)), guard) for _t in range(0, 121, 10))
check(_star_guard >= 0.5 and gap(star_gear, guard) >= 0.5,
      "star and its gear clear the guard (%.2f / %.2f mm)" % (_star_guard, gap(star_gear, guard)))

# Kicker meets the ball and misses the gutter.
_kick_hit = kicker_tray.common(ball_rest(DUMP_PHI)).Volume
check(_kick_hit > 150.0, "kicker at %.1f deg meets the ball (%.0f mm3)" % (DUMP_PHI, _kick_hit))

# Chute sweep past every stationary part over one station pitch.
_progress("chute sweep")
_stat = [("guard", guard), ("feed head", feed_head), ("lip", lip), ("kicker+tray", kicker_tray),
         ("front plate", front_plate)]
_worst_stat = {}
for _s in range(0, 60, 6):
    _ring = Part.makeCompound([place(chute_hi, p + _s) for p in STATION_PHI])
    for _nm, _part in _stat:
        _worst_stat[_nm] = min(_worst_stat.get(_nm, 99.0), gap(_ring, _part))
check(all(v >= 0.4 for v in _worst_stat.values()),
      "chutes sweep clear of " + ", ".join("%s %.2f" % (k, v) for k, v in _worst_stat.items()))
check(gap(pack_gear, Part.makeCompound(chutes)) >= 2.0 and gap(star_gear, Part.makeCompound(chutes)) >= 2.0,
      "gears ahead of the chutes (%.1f / %.1f mm)"
      % (gap(pack_gear, Part.makeCompound(chutes)), gap(star_gear, Part.makeCompound(chutes))))

# Frame: every stationary part bears on the plates.
_progress("frame")
check(gap(guard, front_plate) < 0.05 and gap(feed_head, front_plate) < 0.05
      and gap(front_plate, base) < 0.05 and gap(kicker_tray, base) < 0.05
      and gap(house_front, base) < 0.05 and gap(house_rear, base) < 0.05,
      "guard, head and front plate on the base; kicker and housings on the base")
check(0.05 <= gap(cup, ring) <= 0.4, "cup sits on the ring (gap %.2f mm)" % gap(cup, ring))
_n_lo = CUP_VOID / BALL_VOL * PACK_LO
_n_hi = CUP_VOID / BALL_VOL * PACK_HI
check(30.0 <= _n_lo and _n_hi <= 50.0,
      "cup %.0f cm3 holds %.0f..%.0f balls" % (CUP_VOID / 1000.0, _n_lo, _n_hi))

# Shafts and bearings.
check(gap(brg_front, shaft) < 0.25 and gap(brg_rear, shaft) < 0.25 and gap(brg_nose, shaft) < 0.25,
      "pack shaft Ø%.0f in three 6000 (two behind the disk, one in the front plate)" % SHAFT_D)
check(gap(brg_star, star_shaft) < 0.25 and gap(star, star_shaft) < 0.3 and gap(star_gear, star_shaft) < 0.3,
      "star and its gear on a Ø%.0f shaft in a 608" % STAR_SHAFT_D)
check(gap(disk, shaft) < 0.3 and gap(disk, house_front) >= 0.4 and gap(disk, front_plate) >= 0.4,
      "disk on the shaft, clear of the front housing and the front plate")
_crank_worst = 99.0
for _a in range(0, 360, 30):
    _ck = crank.copy()
    _ck.rotate(O, Z, float(_a))
    _crank_worst = min(_crank_worst, gap(_ck, base), gap(_ck, house_rear))
check(_crank_worst >= 0.5, "crank turns clear of the base and the rear housing (%.1f mm)" % _crank_worst)

_singles = [("disk", disk), ("star", star), ("star gear", star_gear), ("pack gear", pack_gear),
            ("guard", guard), ("feed head", feed_head), ("cup", cup), ("kicker+tray", kicker_tray),
            ("crank", crank), ("front plate", front_plate)]
_bad = [n for n, s in _singles if not G.single_solid(s)]
check(not _bad, "printed parts are single solids%s" % ((" (not: %s)" % ", ".join(_bad)) if _bad else ""))

report = [
    NAME,
    "  idea                   : star geared to the pack; pocket and chute roll on each other",
    "  pack                   : R %.0f, %d chutes = front_cover_feed, ball Ø%.1f on the rims (+%.2f mm), "
    "ball circle R %.2f" % (PACK_R, N_STATION, PELLET_D, BALL_LIFT, R_BALL),
    "  star                   : %d pockets on R %.2f, lobes R %.2f, %.0f thick; cut by the ball over "
    "+/-%.0f deg of pack turn in %.0f deg steps" % (STAR_POCKETS, POCKET_R, STAR_R, STAR_T, MESH_SPAN, MESH_STEP),
    "  gears                  : %d/%d m%.2f, centre distance %.2f, star %g turns per pack turn; "
    "speed match %.3f" % (STAR_WHEEL, STAR_PIN, GEAR_M, X_STAR, STAR_TURNS, SPEED_RATIO),
    "  fill                   : neck ID %.1f above the star top; strike-off at R %.2f (x %.1f), "
    "next ball held %.1f mm below its centre; TPU lip %.1f x %.0f, bends %.1f mm"
    % (NECK_ID, SHROUD_R_IN, X_STRIKE, _hold, LIP_T, LIP_W, _lip_flex),
    "  shroud                 : %.0f..%.0f deg of the star, R %.2f..%.2f, side walls at +/-%.1f"
    % (THETA_STRIKE, SHROUD_END, SHROUD_R_IN, SHROUD_R_OUT, SIDE_Z0),
    "  guard                  : %.1f..%.1f deg, R %.2f..%.2f; kicker at %.1f deg"
    % (GUARD_PHI0, GUARD_PHI1, GUARD_R_IN, GUARD_R_OUT, DUMP_PHI),
    "  frame                  : base and front plate (plate stock), shaft Ø%.0f in 3x 6000, "
    "star shaft Ø%.0f in a 608, crank R %.0f" % (SHAFT_D, STAR_SHAFT_D, CRANK_R),
    "  hopper                 : cup ID %.0f x %.0f, %.0f..%.0f balls, ring at x %.1f"
    % (CUP_ID, CUP_H, _n_lo, _n_hi, X_SEAT),
    "  not drawn              : set screws of the star and gears on their shafts, chute screws "
    "to the disk pads",
    "  not proven             : soft balls, fill at speed, lip length — bench work; pack drive is "
    "not this bench's gear pair",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", text) for text, ok in checks]
print("\n".join(report))
sys.stdout.flush()
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if FEED_BENCH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

# ---------------------------------------------------------------- scene + export
sc = FV.Scene(NAME)
for i, ch in enumerate(chutes):
    sc.add("Pack", "Chute_%d" % i, ch, "stator")
sc.add("Pack", "Disk", disk, "plate")
sc.add("Pack", "Shaft", shaft, "steel")
sc.add("Pack", "Pack_gear", pack_gear, "rotor")
sc.add("Pack", "Crank", crank, "printed")
sc.add("Star", "Star", star, "rotor")
sc.add("Star", "Star_gear", star_gear, "rotor")
sc.add("Star", "Star_shaft", star_shaft, "steel")
sc.add("Frame", "Base", base, "frame")
sc.add("Frame", "Front_plate", front_plate, "frame")
sc.add("Frame", "Housing_front", house_front, "printed")
sc.add("Frame", "Housing_rear", house_rear, "printed")
for nm, b in (("Bearing_front", brg_front), ("Bearing_rear", brg_rear), ("Bearing_nose", brg_nose),
              ("Bearing_star", brg_star)):
    sc.add("Frame", nm, b, "steel")
sc.add("Feed", "Feed_head", feed_head, "stator")
sc.add("Feed", "Lip_TPU", lip, "shoe")
sc.add("Feed", "Cup", cup, "printed")
sc.add("Feed", "Guard", guard, "stator")
sc.add("Trap", "Kicker_tray", kicker_tray, "printed")
for nm, b in (("Ball_next", ball_next), ("Ball_carried", ball_carried), ("Ball_handoff", ball_handoff),
              ("Ball_on_gutter", ball_on_gutter)):
    sc.add("Reference", nm, b, "flow")
sc.label("Labels", "Стенд подачи: звёздочка 2:1, R %.0f" % PACK_R, (0, 0, Z_BALL + 60))
sc.finish(hidden_groups=("Labels",), opaque_groups=())
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

if all(ok for _, ok in checks) and os.environ.get("SKIP_EXPORT") != "1":
    import MeshPart

    def write(shape, fname, rot_y=0.0):
        s = shape.copy()
        if rot_y:
            s.rotate(O, Y, rot_y)
        s.translate(V(-s.BoundBox.Center.x, -s.BoundBox.Center.y, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, fname + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.1,
                               AngularDeflection=0.3).write(os.path.join(OUT_DIR, fname + ".stl"))

    write(front_cover_feed, "chute")        # x6, plain PLA (not airtight)
    write(disk, "disk")
    write(star, "star")
    write(star_gear, "star_gear")
    write(pack_gear, "pack_gear")
    write(guard, "guard")
    write(feed_head, "feed_head", 90.0)     # ring on the bed
    write(cup, "hopper", -90.0)             # floor on the bed
    write(kicker_tray, "kicker_tray")
    write(crank, "crank")
    write(house_front, "housing")           # x2
    write(front_plate, "front_plate")       # plate stock: STEP for cutting
    write(base, "base")                     # plate stock

if not all(ok for _, ok in checks):
    raise SystemExit("gatling feed bench has [FAIL] checks")
