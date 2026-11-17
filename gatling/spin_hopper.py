# -*- coding: utf-8 -*-
"""
Gravity hopper seated on the rotating gatling pack. Sketch, not a freeze.

The bench feeder times its two fingers from one carriage stroke. On the pack
the station under the mouth is already fully open for the whole LOAD shelf
(120–240°), so that stroke does not move and cannot meter balls. The fingers
are timed from pack angle: each station carries a wedge lug, and a stationary
follower on the hopper rocker rides it. A return spring shuts the lower finger
between stations — the stations only pass one way, unlike the bench linkage.

The hopper hangs from two neck ears on a fixed saddle (±36° at r 96–104),
aft of the feed. The pack (R 66, six stations) spins under it. One rigid
Ø23.8 sphere is placed in the trough of the station at the top of the window.
Throat Ø25.4, same cone and cup as the bench. A fixed retainer closes the
radial hole past the top until the fitting has pushed the ball's centre to
the breech face.

This does not prove a soft ball: the probes are rigid spheres, the throat
radial clearance is 0.8 mm, and fall time is not modelled.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/spin_hopper.py').read())"

Pack R / station length may still move. Not a print. Exports nothing.
"""
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

V = App.Vector
NAME = "gatling_spin_hopper"

# Short barrels: this view is the breech. The station file is unchanged.
GATLING_LINEAR_BREECH_LIBRARY = True
GATLING_FAT_COAX_LIBRARY = True
BARREL_SHOW = 120.0
SHOW_OPEN = True
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
NAME = "gatling_spin_hopper"

# ---------------------------------------------------------------- pack law (same as breech_mechanism; R is the sketch value, not a freeze)
N = 6
R_PACK = 66.0
LOAD_A, LOAD_B = 120.0, 240.0
MOUTH = 180.0
FLIP_Z = 180.0
BALL_R = PELLET_D / 2.0
FEED_BORE = 25.4
BORE_R = FEED_BORE / 2.0
WALL = 3.0
FINGER_R = 2.75
ROLLER_R = 4.0
REST_ANG, OPEN_ANG = -19.0, 19.0
DWELL, RAMP = 4.0, 4.0          # degrees of pack angle, release then cosine return
CONE_H, CUP_H = 50.0, 40.0
CUP_ID, CUP_OD = 74.0, 80.0
RETAINER_CLEAR = 1.5
SPRING_NOTE = "return spring between stations; the lug is one-way"


def cam_u(phi_deg):
    phi = phi_deg % 360.0
    if phi >= 330.0 or phi <= 30.0:
        return 0.0
    if 30.0 < phi < 120.0:
        t = (phi - 30.0) / 90.0
        return 0.5 * (1.0 - math.cos(math.pi * t))
    if 120.0 <= phi <= 240.0:
        return 1.0
    if 240.0 < phi < 330.0:
        t = (phi - 240.0) / 90.0
        return 0.5 * (1.0 + math.cos(math.pi * t))
    return 0.0


def cam_dz(phi_deg):
    return -STROKE * cam_u(phi_deg)


def theta_of_delta(delta_deg):
    """Rocker angle. delta = 0 when this station is on the mouth."""
    d = abs(delta_deg)
    if d <= DWELL:
        return OPEN_ANG
    if d >= DWELL + RAMP:
        return REST_ANG
    t = (d - DWELL) / RAMP
    s = 0.5 * (1.0 - math.cos(math.pi * t))
    return OPEN_ANG + (REST_ANG - OPEN_ANG) * s


def place_shape(shape, R, ang_deg):
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(ux, uy)))
    s.translate(V(R * ux, R * uy, 0))
    return s


def flip_up(shape):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), FLIP_Z)
    return s


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cone_y(r0, r1, y0, h, x=0.0, z=0.0):
    return Part.makeCone(r0, r1, h, V(x, y0, z), V(0, 1, 0))


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


# ---------------------------------------------------------------- seat the rigid ball on the open cradle
_cover_open = qev_open["Front_cover"]
_lo, _hi = -2.0, 24.0
for _ in range(28):
    _mid = 0.5 * (_lo + _hi)
    if Part.makeSphere(BALL_R, V(0, _mid, pellet_z)).common(_cover_open).Volume > 0.02:
        _lo = _mid
    else:
        _hi = _mid
Y_SEAT = _hi
# Capture: ball centre reaches the breech face while the tip pushes it.
_u_cap = (FIT_INSERT + BALL_R) / STROKE
_c = max(-1.0, min(1.0, 2.0 * _u_cap - 1.0))
PHI_CAPTURE = 240.0 + math.acos(_c) / math.pi * 90.0
# Retainer starts once the mouth cheeks no longer cover the ball, ends after capture.
RETAINER_A = MOUTH + 12.0
RETAINER_B = PHI_CAPTURE + 8.0

# Throat: straight Ø25.4 long enough for two balls, then the bench cone and cup.
Y_LIP = Y_SEAT + BALL_R + 2.0
Y_LO = Y_LIP + BALL_R + 1.0          # lower ball centre, 1 mm of ball still inside the lip
Y_HI = Y_LO + PELLET_D               # next ball
Y_STRAIGHT = Y_HI + BALL_R + 6.0
Y_CONE = Y_STRAIGHT
Y_CUP = Y_CONE + CONE_H
Y_TOP = Y_CUP + CUP_H
PIV_X, PIV_Y = 36.0, 0.5 * (Y_LO + Y_HI)
FOL_ARM = 32.0


def finger_x(side, theta):
    """side −1 lower (inboard), +1 upper. Same gate as the bench: X only."""
    return 12.0 - side * BALL_R * math.tan(math.radians(theta))


def finger_y(side):
    return Y_LO if side < 0 else Y_HI


def follower_xy(theta):
    """Roller centre. Arm along +X at theta 0, so the swing is mostly radial (Y)."""
    th = math.radians(theta)
    return (PIV_X + FOL_ARM * math.cos(th), PIV_Y + FOL_ARM * math.sin(th))


def finger_pad(side, theta):
    x, y = finger_x(side, theta), finger_y(side)
    head = Part.makeCylinder(FINGER_R, 12.0, V(x, y, pellet_z - 6.0), V(0, 0, 1))
    tail = Part.makeBox(16.0, 5.0, 6.0, V(x, y - 2.5, pellet_z - 3.0))
    # Drive peg the rocker meets, outside the neck.
    peg = Part.makeCylinder(2.2, 8.0, V(x + 14.0, y, pellet_z - 4.0), V(0, 0, 1))
    return head.fuse(tail).fuse(peg).removeSplitter()


def rocker_at(theta):
    """Hub, arm to the cam roller, and a finger that reaches each drive peg."""
    hub = Part.makeCylinder(6.0, 4.0, V(PIV_X, PIV_Y, pellet_z + 6.5), V(0, 0, 1))
    hub = hub.cut(Part.makeCylinder(2.2, 6.0, V(PIV_X, PIV_Y, pellet_z + 5.5), V(0, 0, 1)))
    fx, fy = follower_xy(theta)
    arm = Part.makeBox(FOL_ARM + 6.0, 6.0, 4.0, V(PIV_X - 3.0, PIV_Y - 3.0, pellet_z + 6.5))
    arm.rotate(V(PIV_X, PIV_Y, pellet_z), V(0, 0, 1), theta)
    roller = Part.makeCylinder(ROLLER_R, 8.0, V(fx, fy, pellet_z + 2.0), V(0, 0, 1))
    parts = [hub, arm, roller]
    for side in (-1, 1):
        px, py = finger_x(side, theta) + 14.0, finger_y(side)
        # Bar from the hub plane down to the peg. Rebuilt at this angle.
        bar = Part.makeBox(3.5, 3.5, 8.0, V(px - 1.75, py - 1.75, pellet_z + 2.5))
        web = Part.makeBox(
            abs(px - PIV_X) + 3.0, 3.5, 3.0,
            V(min(px, PIV_X) - 1.0, PIV_Y - 1.75, pellet_z + 7.0))
        parts.append(bar)
        parts.append(web)
    try:
        return G.fuse_all(parts).removeSplitter()
    except Exception:
        return Part.makeCompound(parts)


def cam_lug():
    """Wedge beside the cradle, on a fin that grows out of the barrel.

    The feed plane itself has no metal out at the roller, so the fin is
    rooted on the barrel just ahead of the breech and reaches aft to the wedge.
    """
    fx, fy_open = follower_xy(OPEN_ANG)
    _fx, fy_rest = follower_xy(REST_ANG)
    y_crest = fy_open - ROLLER_R - 0.4
    y_base = fy_rest - ROLLER_R - 1.2
    z0, z1 = pellet_z - 5.0, pellet_z + 5.0
    pts = [
        (fx - 18.0, y_base),
        (fx - 3.0, y_crest),
        (fx + 3.0, y_crest),
        (fx + 18.0, y_base),
        (fx + 18.0, y_base - 8.0),
        (fx - 18.0, y_base - 8.0),
    ]
    poly = [V(x, y, z0) for x, y in pts]
    poly.append(poly[0])
    bump = Part.Face(Part.makePolygon(poly)).extrude(V(0, 0, z1 - z0))
    # Root: a pad on the barrel wall, +X side, just ahead of the breech face.
    root = Part.makeBox(10.0, 16.0, 16.0, V(BARREL_OD / 2.0 - 1.0, -8.0, z_stop + 1.0))
    # Out along +X, then aft to the wedge.
    outrigger = Part.makeBox(fx - BARREL_OD / 2.0, 8.0, 8.0,
                            V(BARREL_OD / 2.0, 2.0, z_stop + 4.0))
    riser = Part.makeBox(8.0, max(8.0, y_base - 2.0), (z_stop + 8.0) - z0,
                         V(fx - 4.0, 2.0, z0))
    try:
        return bump.fuse(root).fuse(outrigger).fuse(riser).removeSplitter()
    except Exception:
        return Part.makeCompound([bump, root, outrigger, riser])


# ---------------------------------------------------------------- hopper body (local frame of the top station: +Y radial out)
def build_hopper():
    neck_r = BORE_R + WALL
    neck = cyl_y(neck_r, Y_LIP, Y_STRAIGHT + 0.2, 0.0, pellet_z)
    cone = cone_y(neck_r, CUP_OD / 2.0, Y_CONE, CONE_H, 0.0, pellet_z)
    cup = cyl_y(CUP_OD / 2.0, Y_CUP - 0.1, Y_TOP, 0.0, pellet_z)
    body = neck.fuse(cone).fuse(cup)
    # Cheeks continue the bore walls down beside the ball, but only over the
    # gutter. Further aft the fitting tip is a full cylinder and it sweeps
    # through anything that reaches down beside it.
    y_cheek = Y_SEAT - 1.0
    z_cheek0 = pellet_z - 8.0
    z_cheek1 = pellet_z + BALL_R + 2.2
    for s in (-1, 1):
        x0 = s * (BORE_R + 0.4) if s > 0 else -(BORE_R + 0.4) - WALL
        cheek = Part.makeBox(WALL, (Y_LIP + 4.0) - y_cheek, z_cheek1 - z_cheek0,
                             V(x0, y_cheek, z_cheek0))
        body = body.fuse(cheek)
    # Forward fence, above the gutter so a sweeping cradle tip passes under it.
    # Overlaps the cheeks so the mouth stays one solid. The cover blocks the aft side.
    fence = Part.makeBox(FEED_BORE + 2.0, 14.0, 2.4,
                         V(-(BORE_R + 1.0), Y_SEAT - 1.0, pellet_z + BALL_R + 0.9))
    body = body.fuse(fence)
    # Pivot ear and finger guides, outside the neck.
    # Pivot ear bridges out from the neck wall (neck OD reaches x ≈ 16).
    ear = Part.makeBox(30.0, 28.0, 8.0, V(14.0, PIV_Y - 14.0, pellet_z + 6.0))
    body = body.fuse(ear)
    # Two mount ears at the top of the straight neck, one each side.
    for s in (1, -1):
        x0 = 12.0 if s > 0 else -34.0
        body = body.fuse(Part.makeBox(
            22.0, 16.0, 12.0, V(x0, Y_STRAIGHT - 14.0, pellet_z - 4.0)))
    for side in (-1, 1):
        y = finger_y(side)
        guide = Part.makeBox(28.0, 10.0, 14.0, V(14.0, y - 5.0, pellet_z - 7.0))
        body = body.fuse(guide)
    void = cyl_y(BORE_R, Y_LIP - 1.0, Y_CONE + 0.2, 0.0, pellet_z)
    void = void.fuse(cone_y(BORE_R, CUP_ID / 2.0, Y_CONE, CONE_H, 0.0, pellet_z))
    void = void.fuse(cyl_y(CUP_ID / 2.0, Y_CUP - 0.2, Y_TOP + 1.0, 0.0, pellet_z))
    # Rim chamfer so the cup lip is not a knife in the picture.
    body = body.cut(void)
    # Slots the finger tails slide in. Long enough for −19° and +19°.
    for side in (-1, 1):
        y = finger_y(side)
        slot = Part.makeBox(26.0, 6.2, 8.0, V(6.0, y - 3.1, pellet_z - 4.0))
        body = body.cut(slot)
    # Pivot hole.
    body = body.cut(Part.makeCylinder(2.4, 12.0, V(PIV_X, PIV_Y, pellet_z + 2.0), V(0, 0, 1)))
    try:
        return body.removeSplitter()
    except Exception:
        return body


hopper_local = build_hopper()
lug_local = cam_lug()
rocker = rocker_at(OPEN_ANG)
pad_lo = finger_pad(-1, OPEN_ANG)
pad_hi = finger_pad(1, OPEN_ANG)
roller = Part.makeCylinder(
    ROLLER_R, 8.0,
    V(follower_xy(OPEN_ANG)[0], follower_xy(OPEN_ANG)[1], pellet_z + 2.0),
    V(0, 0, 1))
# Visual return spring on the pivot. Not a rate.
spring = Part.makeTorus(5.5, 1.1, V(PIV_X, PIV_Y, pellet_z + 12.5), V(0, 0, 1))

# Balls. Rigid probes, also shown.
ball_seat = Part.makeSphere(BALL_R, V(0.0, Y_SEAT, pellet_z))
ball_held = Part.makeSphere(BALL_R, V(0.0, Y_HI, pellet_z))
ball_cup = Part.makeSphere(BALL_R, V(0.0, Y_CUP + 12.0, pellet_z))

# ---------------------------------------------------------------- fixed mount: ring + two struts + screws. Not on a station.
# Ring sits aft of the feed, outside the open chamber flange.
z_ring = pellet_z - 36.0
r_ring_i, r_ring_o = 96.0, 104.0
_ring_full = Part.makeCylinder(r_ring_o, 8.0, V(0, 0, z_ring)).cut(
    Part.makeCylinder(r_ring_i, 12.0, V(0, 0, z_ring - 2.0)))
frame_ring = None  # sector is cut once _sector_keep exists


def strut_at(x_ear):
    """Bar from a neck ear down into the saddle. The foot is buried in the ring."""
    y0 = Y_STRAIGHT - 8.0
    p0 = V(x_ear, y0, pellet_z + 2.0)
    y_land = 0.5 * (r_ring_i + r_ring_o) - R_PACK
    p1 = V(x_ear * 0.2, y_land, z_ring + 4.0)
    direction = p1 - p0
    rod = Part.makeCylinder(4.0, direction.Length + 8.0, p0, direction)
    foot = Part.makeBox(16.0, 16.0, 12.0, V(p1.x - 8.0, y_land - 8.0, z_ring - 2.0))
    return rod.fuse(foot).removeSplitter()


strut_p = strut_at(24.0)
strut_m = strut_at(-24.0)

# ---------------------------------------------------------------- retainer: fixed arc outside the ball, mouth cut out
_r_ball_out = R_PACK + Y_SEAT + BALL_R
_r_in = _r_ball_out + RETAINER_CLEAR
_r_out = _r_in + 4.5
_z_ret0 = pellet_z - BALL_R - 2.0
_z_ret1 = z_stop + 4.0


def _sector_keep(shape, a0, a1, r_out):
    """Keep the wedge a0..a1 degrees (world, pre-flip)."""
    boxes = []
    a = a0
    step = 6.0
    while a < a1 - 1e-9:
        a2 = min(a + step, a1)
        mid = 0.5 * (a + a2)
        half = math.radians(0.5 * (a2 - a) + 0.4)
        w = 2.0 * (r_out + 8.0) * math.sin(half) + 4.0
        box = Part.makeBox(r_out + 12.0, w, shape.BoundBox.ZLength + 8.0,
                           V(0.0, -w / 2.0, shape.BoundBox.ZMin - 4.0))
        box.rotate(V(0, 0, 0), V(0, 0, 1), mid)
        boxes.append(box)
        a = a2
    pie = G.fuse_all(boxes) if len(boxes) > 1 else boxes[0]
    try:
        return shape.common(pie).removeSplitter()
    except Exception:
        return shape.common(pie)


# A saddle under the mouth, not a hoop around the whole pack.
frame_ring = _sector_keep(_ring_full, MOUTH - 36.0, MOUTH + 36.0, r_ring_o)

_shell = Part.makeCylinder(_r_out, _z_ret1 - _z_ret0, V(0, 0, _z_ret0)).cut(
    Part.makeCylinder(_r_in, _z_ret1 - _z_ret0 + 4.0, V(0, 0, _z_ret0 - 2.0)))
retainer = _sector_keep(_shell, RETAINER_A, RETAINER_B, _r_out)

# ---------------------------------------------------------------- stations
def station_parts(phi):
    dz = cam_dz(phi)
    cover = place_shape(shifted(qev_closed["Front_cover"], dz), R_PACK, phi)
    chamber = place_shape(shifted(qev_closed["Chamber_tube"], dz), R_PACK, phi)
    barrel = place_shape(fixed_barrel, R_PACK, phi)
    nose = place_shape(shifted(qev_closed["Nose_clamp"], dz), R_PACK, phi)
    lug = place_shape(lug_local, R_PACK, phi)
    return cover, chamber, barrel, nose, lug


stations = []
for k in range(N):
    phi = (MOUTH + k * 60.0) % 360.0
    stations.append((phi, ) + station_parts(phi))

# Fixed hopper parts, placed once at the mouth.
hopper = place_shape(hopper_local, R_PACK, MOUTH)
rocker_w = place_shape(rocker, R_PACK, MOUTH)
pad_lo_w = place_shape(pad_lo, R_PACK, MOUTH)
pad_hi_w = place_shape(pad_hi, R_PACK, MOUTH)
spring_w = place_shape(spring, R_PACK, MOUTH)
ball_seat_w = place_shape(ball_seat, R_PACK, MOUTH)
ball_held_w = place_shape(ball_held, R_PACK, MOUTH)
ball_cup_w = place_shape(ball_cup, R_PACK, MOUTH)
strut_p_w = place_shape(strut_p, R_PACK, MOUTH)
strut_m_w = place_shape(strut_m, R_PACK, MOUTH)
mount = frame_ring.fuse(strut_p_w).fuse(strut_m_w)
try:
    mount = mount.removeSplitter()
except Exception:
    mount = Part.makeCompound([frame_ring, strut_p_w, strut_m_w])

# Rest-pose pads and roller, for checks only (not drawn).
pad_lo_rest = place_shape(finger_pad(-1, REST_ANG), R_PACK, MOUTH)
pad_hi_rest = place_shape(finger_pad(1, REST_ANG), R_PACK, MOUTH)
roller_rest = place_shape(
    Part.makeCylinder(ROLLER_R, 8.0,
                      V(follower_xy(REST_ANG)[0], follower_xy(REST_ANG)[1], pellet_z + 2.0),
                      V(0, 0, 1)),
    R_PACK, MOUTH)
roller_open = place_shape(roller, R_PACK, MOUTH)
lug_top = stations[0][5]


def ball_at(phi, outward=0.0, z_extra=0.0):
    """Rigid ball on that station's cradle. outward > 0 moves it off the pack."""
    z = pellet_z + z_extra
    # While closing, the tip pushes the ball forward. Open pose matches pellet_z.
    z_push = z_tip + cam_dz(phi) + BALL_R
    if z_extra == 0.0:
        z = max(pellet_z, z_push)
    b = Part.makeSphere(BALL_R, V(0.0, Y_SEAT + outward, z if z_extra or True else pellet_z))
    # The local Y shift is radial only when outward is applied before placement
    # and the ball stays at local X = 0. Re-seat Z in the station frame.
    b = Part.makeSphere(BALL_R, V(0.0, Y_SEAT, z))
    if outward:
        b.translate(V(0, outward, 0))
    return place_shape(b, R_PACK, phi)


def _vol(a, b):
    try:
        return a.common(b).Volume
    except Exception:
        return 1e9


def _dist(a, b):
    try:
        return a.distToShape(b)[0]
    except Exception:
        return -1.0


# ---------------------------------------------------------------- checks
checks = []
checks.append(("working pressure unchanged (%.0f / %.0f bar)" % (P_WORK_BAR, P_MAX_BAR),
               abs(P_WORK_BAR - 2.0) < 1e-9 and abs(P_MAX_BAR - 5.0) < 1e-9))
checks.append(("stroke still 65.8 mm", abs(STROKE - 65.8) < 1e-6))
checks.append(("throat bore is 25.4 mm", abs(FEED_BORE - 25.4) < 1e-9))

# Narrowest section: a Ø25.4 cylinder along the whole hopper must miss the metal.
# Built in the local frame, where the bore is a straight Y axis.
_probe_lo = Y_LIP - 0.5
_probe = cyl_y(BORE_R, _probe_lo, Y_TOP + 0.5, 0.0, pellet_z)
_probe_narrow = cyl_y(12.55, _probe_lo, Y_TOP + 0.5, 0.0, pellet_z)  # Ø25.1
checks.append(("Ø25.4 cylinder misses hopper metal (vol %.3f)" % _vol(_probe, hopper_local),
               _vol(_probe, hopper_local) < 0.05))
checks.append(("Ø25.1 cylinder also misses (throat not under drawing)",
               _vol(_probe_narrow, hopper_local) < 0.05))
checks.append(("hopper is one solid", G.single_solid(hopper_local)))
checks.append(("retainer is one solid", G.single_solid(retainer)))
checks.append(("top cam lug is one solid", G.single_solid(lug_local)))

# Fingers are not on any nose clamp. The lug is not the nose clamp either.
_noses = [st[4] for st in stations]
_finger_bits = [rocker_w, pad_lo_w, pad_hi_w, spring_w]
_min_nose = min(_dist(bit, nose) for bit in _finger_bits for nose in _noses)
checks.append(("fingers / rocker clear of every nose clamp (%.1f mm)" % _min_nose,
               _min_nose > 5.0))
_lug_nose = min(_dist(st[5], st[4]) for st in stations)
checks.append(("cam lug is not the nose clamp (%.1f mm)" % _lug_nose, _lug_nose > 8.0))

# Six lugs, one per station, and only the aligned one meets the roller.
checks.append(("six stations, six lugs", len(stations) == 6))
_on_lug = _dist(roller_open, lug_top)
checks.append(("release roller on the aligned lug (gap %.2f mm)" % _on_lug,
               _on_lug < 0.8 and _vol(roller_open, lug_top) < 0.05))
# Rest pose is inside the crest: the lug forces the finger open. Spring alone can't stay shut.
checks.append(("lug crest occupies the shut-roller pose (it does push)",
               _vol(roller_rest, lug_top) > 1.0))
_far = min(_dist(roller_rest, st[5]) for st in stations[1:])
checks.append(("shut roller clear of the other five lugs (%.1f mm)" % _far, _far > 15.0))

# Gate. Same question as the bench: one ball, the next one held.
_drop = Part.makeSphere(BALL_R, V(0.0, Y_LO, pellet_z))
_drop_far = Part.makeSphere(BALL_R, V(-0.8, Y_LO, pellet_z))  # away from the +X finger
_next = Part.makeSphere(BALL_R, V(0.0, Y_HI, pellet_z))
_lo_open = finger_pad(-1, OPEN_ANG)
_hi_open = finger_pad(1, OPEN_ANG)
_lo_shut = finger_pad(-1, REST_ANG)
checks.append(("shut lower finger stops a centred ball", _vol(_lo_shut, _drop) > 1.0))
checks.append(("shut lower finger still stops a ball on the far wall",
               _vol(_lo_shut, _drop_far) > 1.0))
checks.append(("open lower finger lets both of those balls past",
               _vol(_lo_open, _drop) < 0.05 and _vol(_lo_open, _drop_far) < 0.05))
checks.append(("open upper finger holds the next ball", _vol(_hi_open, _next) > 1.0))
checks.append(("open upper finger is the only gate (lower misses the next ball)",
               _vol(_lo_open, _next) < 0.05))

# Seated ball touches the cradle and misses the hopper, fingers and retainer.
_top_cover = stations[0][1]
checks.append(("seated ball touches the open cradle",
               _dist(ball_seat_w, _top_cover) < 0.2 and _vol(ball_seat_w, _top_cover) < 1.0))
_seat_clear = min(_dist(ball_seat_w, sh) for sh in (hopper, pad_lo_w, pad_hi_w, retainer, mount))
checks.append(("seated ball clear of hopper, fingers, retainer, mount (%.2f mm)" % _seat_clear,
               _seat_clear > 0.4 and _vol(ball_seat_w, hopper) < 0.05))

# Aft of the seat the cover is a wall. Forward, the fence is.
_ball_aft = place_shape(Part.makeSphere(BALL_R, V(0.0, Y_SEAT, pellet_z - 3.0)), R_PACK, MOUTH)
checks.append(("3 mm aft of the seat the cover blocks the ball",
               _vol(_ball_aft, _top_cover) > 1.0))
_fence_z = pellet_z + BALL_R + 0.9
_fence_hit = place_shape(
    Part.makeSphere(BALL_R, V(0.0, Y_SEAT, _fence_z + 0.4)),
    R_PACK, MOUTH)
checks.append(("forward fence stops a ball that has left the cradle tip",
               _vol(_fence_hit, hopper) > 1.0))

# Side cheeks: a ball shifted off the valley, still above the cradle, hits a cheek.
_ball_side = place_shape(Part.makeSphere(BALL_R, V(10.0, Y_SEAT + 2.0, pellet_z)), R_PACK, MOUTH)
checks.append(("cheek stops a ball shifted 10 mm off the valley",
               _vol(_ball_side, hopper) > 1.0))

# Hopper and mount miss every station, including the three that are fully open.
_fixed = [hopper, mount, rocker_w, pad_lo_w, pad_hi_w]
_worst = 1e9
_worst_name = ""
for phi, cover, chamber, barrel, nose, lug in stations:
    for sh in _fixed:
        for part, tag in ((cover, "cover"), (chamber, "chamber"), (barrel, "barrel"), (nose, "nose")):
            d = _dist(sh, part)
            if d < _worst:
                _worst = d
                _worst_name = "%s @ %.0f vs %s" % (tag, phi, d)
checks.append(("hopper / mount / fingers clear of all six stations (%.2f mm)" % _worst,
               _worst > 0.6))

# Retainer: past the top an outward ball hits it, and without it that ball hits nothing.
_bare_out = None
_ret_hold = None
_ret_clear = 1e9
_ret_touch = 1e9
for deg in (20.0, 40.0, 60.0, 80.0):
    phi = MOUTH + deg
    if phi > RETAINER_B - 2.0:
        continue
    held = ball_at(phi, outward=0.0)
    escaped = ball_at(phi, outward=3.0)
    d_hold = _dist(held, retainer)
    _ret_clear = min(_ret_clear, d_hold)
    if _vol(escaped, retainer) < 0.5:
        _ret_hold = deg
    # The hole: the outward ball should miss this station's cover.
    cover = None
    for st in stations:
        if abs(((st[0] - phi + 180.0) % 360.0) - 180.0) < 1.0:
            cover = st[1]
    if cover is None:
        # Station isn't one of the six drawn poses; build the cover.
        cover = place_shape(shifted(qev_closed["Front_cover"], cam_dz(phi)), R_PACK, phi)
    if _vol(escaped, cover) > 0.5 and _bare_out is None:
        _bare_out = deg
    d_cov = _dist(retainer, cover)
    _ret_touch = min(_ret_touch, d_cov)
checks.append(("retainer stays off the ball on the cradle (%.2f mm)" % _ret_clear,
               _ret_clear > 0.8))
checks.append(("3 mm outward, the ball hits the retainer",
               _ret_hold is None))
checks.append(("without the retainer that outward ball hits no cover",
               _bare_out is None))
checks.append(("retainer clear of those cradles (%.2f mm)" % _ret_touch,
               _ret_touch > 0.6))

# Mouth vs a sweeping cradle: the cheeks must let the open trough pass.
_sweep = 1e9
for deg in (-12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0):
    phi = MOUTH + deg
    cover = place_shape(shifted(qev_closed["Front_cover"], cam_dz(phi)), R_PACK, phi)
    _sweep = min(_sweep, _dist(hopper, cover))
checks.append(("mouth cheeks clear the cradle through the release window (%.2f mm)" % _sweep,
               _sweep > 0.8))

# Release window is one station wide.
_arc = math.radians(DWELL) * (R_PACK + Y_SEAT)
checks.append(("release dwell ±%.0f° is %.1f mm of arc, inside the cradle half-width"
               % (DWELL, _arc),
               _arc < 11.0))
checks.append(("neighbour trough is not under the throat",
               _dist(stations[1][1], hopper) > 5.0 and _dist(stations[5][1], hopper) > 5.0))

# Lug rides beside the open breech; it must not be buried in the cover.
checks.append(("cam lug clear of the open cover",
               _vol(lug_local, qev_open["Front_cover"]) < 0.05))
checks.append(("cam lug is rooted on its barrel",
               _vol(lug_local, fixed_barrel) > 5.0))
checks.append(("top cam lug clear of the hopper (%.2f mm)" % _dist(stations[0][5], hopper),
               _dist(stations[0][5], hopper) > 0.6))
_lug_gap = 1e9
for i, st in enumerate(stations):
    for j, other in enumerate(stations):
        if i == j:
            continue
        for part in other[1:5]:
            _lug_gap = min(_lug_gap, _dist(st[5], part))
checks.append(("cam lugs clear the other stations (%.1f mm)" % _lug_gap, _lug_gap > 1.0))
checks.append(("each strut grows out of a neck ear",
               _vol(strut_p_w, hopper) > 10.0 and _vol(strut_m_w, hopper) > 10.0))
checks.append(("each strut lands in the saddle",
               _vol(strut_p_w, frame_ring) > 20.0 and _vol(strut_m_w, frame_ring) > 20.0))
checks.append(("mount saddle is one solid", G.single_solid(mount)))
checks.append(("sketch R is 66 (not grown, pack not reseated)", abs(R_PACK - 66.0) < 1e-9))

n_fail = sum(1 for _, ok in checks if not ok)
report = [
    NAME,
    "  purpose                : stationary gravity hopper on the spinning pack (NOT a freeze)",
    "  pack                   : %d stations, R %.1f (sketch value), LOAD %.0f–%.0f°, mouth %.0f°"
    % (N, R_PACK, LOAD_A, LOAD_B, MOUTH),
    "  barrels in this view   : %.0f mm (station file still draws its own length)" % BARREL_SHOW,
    "  seat                   : rigid ball centre local Y %.2f mm (%.2f mm above the bore axis)"
    % (Y_SEAT, Y_SEAT),
    "  throat                 : Ø%.1f straight, then cone %.0f mm to ID %.0f, cup %.0f mm OD %.0f"
    % (FEED_BORE, CONE_H, CUP_ID, CUP_H, CUP_OD),
    "  fingers                : two pads, ±%.0f°, bore gate as on the bench; NOT driven by a nose clamp"
    % OPEN_ANG,
    "  cam                    : one wedge lug per station, follower on the rocker; %s" % SPRING_NOTE,
    "  release window         : ±%.0f° dwell + %.0f° ramp (%.1f mm of arc at the seat)"
    % (DWELL, RAMP, _arc),
    "  retainer               : %.0f–%.0f° pre-flip, ID at ball crown + %.1f mm; capture φ %.1f°"
    % (RETAINER_A, RETAINER_B, RETAINER_CLEAR, PHI_CAPTURE),
    "  mount                  : two struts from the neck to a saddle ±36° at r %.0f–%.0f, aft of the feed"
    % (r_ring_i, r_ring_o),
    "  pack core              : not remeasured here; breech_mechanism still reports 0.00 and is not frozen",
    "  pressure               : %.0f bar work / %.0f bar design, unchanged" % (P_WORK_BAR, P_MAX_BAR),
    "  soft ball              : NOT proven (rigid Ø%.1f, throat radial gap %.1f mm, no fall time)"
    % (PELLET_D, (FEED_BORE - PELLET_D) / 2.0),
    "  not drawn              : stroke cam, hoses, crank, auger; those stay in breech_mechanism.py",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))
print("CHECKS %d ok, %d fail" % (len(checks) - n_fail, n_fail))

try:
    SPIN_HOPPER_LIBRARY
except NameError:
    SPIN_HOPPER_LIBRARY = False
if SPIN_HOPPER_LIBRARY:
    raise SystemExit(0 if n_fail == 0 else 1)
if n_fail:
    raise SystemExit("gatling spin hopper has [FAIL] checks")

# ---------------------------------------------------------------- scene (flipped so the hopper is on top, +X)
FV.STYLES["feed"] = ((0.72, 0.58, 0.34), 12)
FV.STYLES["finger"] = ((0.86, 0.42, 0.18), 0)
FV.STYLES["cam"] = ((0.22, 0.24, 0.28), 8)
FV.STYLES["guard"] = ((0.42, 0.52, 0.66), 28)
FV.STYLES["ball"] = ((0.93, 0.93, 0.95), 8)
FV.STYLES["frame"] = ((0.55, 0.58, 0.52), 18)
FV.STYLES["spring"] = ((0.75, 0.75, 0.78), 0)
for i, col in enumerate((
        (0.86, 0.45, 0.18),
        (0.45, 0.58, 0.72),
        (0.55, 0.58, 0.52),
        (0.40, 0.42, 0.46),
        (0.55, 0.58, 0.52),
        (0.45, 0.58, 0.72),
)):
    FV.STYLES["ph%d" % i] = (col, 18 if i else 8)

sc = FV.Scene(NAME)
for i, (phi, cover, chamber, barrel, nose, lug) in enumerate(stations):
    tag = "ph%d" % i
    sc.add("Pack", "Cover_%d" % i, flip_up(cover), tag)
    sc.add("Pack", "Chamber_%d" % i, flip_up(chamber), tag)
    sc.add("Pack", "Barrel_%d" % i, flip_up(barrel), "steel_ghost")
    sc.add("Pack", "Nose_%d" % i, flip_up(nose), tag)
    sc.add("Pack", "Lug_%d" % i, flip_up(lug), "cam")
sc.add("Hopper", "Hopper", flip_up(hopper), "feed")
sc.add("Hopper", "Mount", flip_up(mount), "frame")
sc.add("Hopper", "Rocker", flip_up(rocker_w), "finger")
sc.add("Hopper", "Finger_lower", flip_up(pad_lo_w), "finger")
sc.add("Hopper", "Finger_upper", flip_up(pad_hi_w), "finger")
sc.add("Hopper", "Spring", flip_up(spring_w), "spring")
sc.add("Hopper", "Retainer", flip_up(retainer), "guard")
sc.add("Balls", "Ball_trough", flip_up(ball_seat_w), "ball")
sc.add("Balls", "Ball_held", flip_up(ball_held_w), "ball")
sc.add("Balls", "Ball_cup", flip_up(ball_cup_w), "ball")
sc.finish()
