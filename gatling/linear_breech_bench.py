# -*- coding: utf-8 -*-
"""
Bench for one Gatling linear-breech station: small feet under the rails.

Loads gatling/linear_breech.py as a library. The aluminium rails are the beam;
two feet support it (front under the barrel clamp, rear aft of the open
carriage); the carriage is pushed by hand on the QEV / bridge disc. No handle,
no long floor slab.

Prove on the bench: open → straight hammer releases the gravity feeder → close resets the lever.
The carriage-operated hopper fixed portal clamps to both rails; crank / rotary union remain absent.
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
PACK_STATION = False             # bench guides (plates); a console may still hold True
SHOW_OPEN = True
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_linear_breech_bench")
NAME = "gatling_linear_breech_bench"
station_checks = list(checks)

X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector

# ---------------------------------------------------------------- feet parameters
# Two discrete feet — rails span between them. Wide enough in X so a hand shove
# on the QEV does not tip; short in Z (print volume, not a giant frame).
FOOT_PAD_X = 76.0                # full width of each foot pad
FOOT_PAD_Z = 16.0                # short: open carriage leaves ~20 mm at the rail tip
FOOT_T = 6.0                     # pad thickness
POST_W = 16.0
STOP_T = 7.0                     # axial width of adjustable split rail stops
SCREW_D = 4.2                    # M4 clearance through pads → clamp to table
SCREW_R = 30.0                   # hole centres from foot mid-plane X=0

y_rail_bot = RAIL_Y - RAIL_OD / 2
y_floor = min(vent_body.BoundBox.YMin, vent_fittings.BoundBox.YMin,
              cradle.BoundBox.YMin, vent_plunger.BoundBox.YMin) - 5.0
y_pad_top = y_floor + FOOT_T

# Reserve room behind the open carriage for a clamped stop and tool access.
z_rail0 -= 12.0
rails = [tube(RAIL_OD, RAIL_OD - 2 * RAIL_WALL, z_rail0, z_rail1, x, y)
         for x, y in rail_centers()]
rails_s = G.fuse_all(rails)
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

# Four adjustable split collars arrest the rear carriage at the exact stroke endpoints.
# Ears face outwards; M3 bolts close the slit without set screws denting the Al tubes.
STOP_BORE = RAIL_OD + 0.3
STOP_SLIT = 1.0
stop_open_z = open_carr_z0 - STOP_T
stop_closed_z = carriage.BoundBox.ZMax
stops, stop_bolts, stops_open, stops_closed = [], [], [], []
for x, y in rail_centers():
    side = 1 if x > 0 else -1
    for index, z_s in enumerate((stop_open_z, stop_closed_z)):
        st = G.cyl(14, z_s, z_s + STOP_T, x, y)
        ear_x = x + 5 if side > 0 else x - 15
        st = st.fuse(Part.makeBox(10, 14, STOP_T, V(ear_x, y - 7, z_s)))
        st = st.cut(G.cyl(STOP_BORE, z_s - 1, z_s + STOP_T + 1, x, y))
        slit_x = x if side > 0 else x - 16
        st = st.cut(Part.makeBox(16, STOP_SLIT, STOP_T + 2,
                                V(slit_x, y - STOP_SLIT / 2, z_s - 1)))
        bx, bz = x + side * 12, z_s + STOP_T / 2
        st = st.cut(Part.makeCylinder(1.7, 18, V(bx, y - 9, bz), Y)).removeSplitter()
        stops.append(st)
        (stops_open if index == 0 else stops_closed).append(st)
        bolt = Part.makeCylinder(1.5, 20, V(bx, y - 13, bz), Y)
        head = Part.makeCylinder(2.75, 3, V(bx, y + 7, bz), Y)
        nut = G.hex_prism(5.5, 0, 2.4)
        nut.rotate(V(0, 0, 0), X, 90)
        nut.translate(V(bx, y - 7, bz))
        stop_bolts.append(Part.makeCompound([bolt, head, nut]))
stops_s = Part.makeCompound(stops)
stop_hardware = Part.makeCompound(stop_bolts)
stop_checks = [('rail stop %d valid single solid' % i, G.single_solid(st)) for i, st in enumerate(stops)]
for label, parts, carr, overrun in [('open', stops_open, shifted(carriage, -STROKE), -0.5),
                                    ('closed', stops_closed, carriage, 0.5)]:
    for i, st in enumerate(parts):
        stop_checks.append(('%s stop %d contacts carriage without overlap' % (label, i),
                            st.distToShape(carr)[0] < 1e-6 and G.no_overlap(st, carr)))
        stop_checks.append(('%s stop %d blocks overtravel' % (label, i),
                            st.common(shifted(carr, overrun)).Volume > 0.1))
for name, fixed in [('rails', rails_s), ('rear foot', rear_foot), ('front foot', front_foot),
                    ('valve cradle', cradle), ('valve body', vent_body), ('valve fittings', vent_fittings)]:
    stop_checks.append(('rail stops clear ' + name, G.no_overlap(stops_s, fixed)))
for i in range(11):
    dz = -STROKE * i / 10
    stop_checks.append(('rail stops clear moving station %d/10' % i,
                        all(G.no_overlap(stops_s, shifted(sh, dz)) for sh in qev_closed.values())))

# ---------------------------------------------------------------- gravity feeder (compact two-finger rocker)
# Manual prototype: rock to release one ball, return to refill the lower stop.
BALL_D = 23.8
FEED_BORE = BALL_D + 1.6
TUNNEL_CLEAR = 1.0
TUNNEL_ROOF = 3.0
FEED_Y = CH_OD / 2 + TUNNEL_CLEAR + TUNNEL_ROOF
FEED_Z = pellet_z + 6.0  # release only after the moving tip clears the ball
PIVOT_X, PIVOT_Y = 25.0, FEED_Y + 21.9
ROCKER_ANGLE = 20.0
REST_ANGLE = -19.0  # margin to the mechanical end stop
FINGER_R = 2.75                 # M3 socket-head diameter 5.5 mm


def feed_bore(x, y0, y1, diameter=FEED_BORE):
    return Part.makeCylinder(diameter / 2, y1 - y0, V(x, y0, FEED_Z), Y)


def finger_center(side, angle):
    py = PIVOT_Y + side * BALL_D / 2
    return (PIVOT_X - side * BALL_D / 2 * math.tan(math.radians(angle)) - 13, py)


def m3x6(px, py, root_z, direction=1):
    # Nominal M3x6 socket-head screw: 6 mm under-head length, head 5.5 x 3 mm.
    shaft = Part.makeCylinder(1.5, 6, V(px, py, root_z), V(0, 0, direction))
    head = Part.makeCylinder(2.75, 3, V(px, py, root_z), V(0, 0, -direction))
    socket = G.hex_prism(2.5, 0, 1.5)
    if direction > 0:
        socket.translate(V(px, py, root_z - 3))
    else:
        socket.translate(V(px, py, root_z + 1.5))
    return shaft.fuse(head.cut(socket)).removeSplitter()


def finger_at(side, angle):
    px, py = finger_center(side, angle)
    # Printed carrier only; the contact head and follower fastener are bought M3x6.
    tip_boss = G.cyl(5, FEED_Z + 1.5, FEED_Z + 8.5, px, py)
    tail = Part.makeBox(14, 4, 6, V(px + 2, py - 2, FEED_Z + 1.5))
    end = 18.0 if side == -1 else 17.7
    follower_boss = G.cyl(4.5, FEED_Z + 1.5, FEED_Z + end, px + 13, py)
    if side == -1:
        follower_boss = follower_boss.fuse(G.cyl(6, FEED_Z+16.5, FEED_Z+18, px+13,py))
        follower_boss = follower_boss.fuse(G.cyl(4, FEED_Z+18, FEED_Z+20.9, px+13,py))
    sh = G.fuse_all([tip_boss, tail, follower_boss])
    sh = sh.cut(G.cyl(2.5, FEED_Z + 1.4, FEED_Z + 7.7, px, py))
    sh = sh.cut(G.cyl(2.5, FEED_Z + (14.7 if side == -1 else 11.5), FEED_Z + (21.0 if side == -1 else 17.8), px + 13, py))
    return sh.removeSplitter()


def finger_bolts(side, angle):
    px, py = finger_center(side, angle)
    return Part.makeCompound([m3x6(px, py, FEED_Z + 1.5),
                              m3x6(px + 13, py, FEED_Z + (20.9 if side == -1 else 17.7), -1)])


def finger_assembly(side, angle):
    return Part.makeCompound([finger_at(side, angle), finger_bolts(side, angle)])


def rocker_at(angle):
    # 2.5 mm lever; shoulders stand 0.2 mm proud so tightened screws cannot pinch it.
    sh = Part.makeBox(8, 34, 2.5, V(PIVOT_X - 4, PIVOT_Y - 17, FEED_Z + 11))
    sh = sh.fuse(Part.makeBox(16, 5, 2.5, V(PIVOT_X, PIVOT_Y - 2.5, FEED_Z + 11)))
    sh = sh.fuse(G.cyl(8, FEED_Z + 11, FEED_Z + 13.5, PIVOT_X + 16, PIVOT_Y))
    sh = sh.cut(G.cyl(4.8, FEED_Z + 10, FEED_Z + 15, PIVOT_X, PIVOT_Y))
    for py in (PIVOT_Y - 15.3, PIVOT_Y + 8.7):
        sh = sh.cut(Part.makeBox(4.8, 6.6, 5, V(PIVOT_X - 2.4, py, FEED_Z + 10)))
    sh.rotate(V(PIVOT_X, PIVOT_Y, FEED_Z), Z, angle)
    return sh.removeSplitter()


# Fixed portal on both rails, just ahead of the moving nose guide.
# The lower clamp bar is removable; nothing attaches to Barrel_clamp.
FEED_RAIL_Z0, FEED_RAIL_Z1 = FEED_Z - 5.0, FEED_Z + 7.0
base = Part.makeBox(76, 4, 40, V(-38, FEED_Y - 4, FEED_Z - 20))
base = base.cut(feed_bore(0, FEED_Y - 5, FEED_Y + 1))
# Curved underside follows the moving chamber; enlarge locally for its nose clamp.
chamber_tunnel = G.cyl(CH_OD + 2 * TUNNEL_CLEAR, FEED_Z - 22, FEED_Z + 22)
nose_tunnel = G.cyl(CH_OD + 6 + 2 * (TUNNEL_CLEAR + 0.2),
                    z_nose0 + 6 - STROKE - TUNNEL_CLEAR, z_nose1 - 6 + TUNNEL_CLEAR)
base = base.cut(chamber_tunnel).cut(nose_tunnel)
frame = base
feeder_rail_cap = Part.makeBox(76, 8, 12, V(-38, RAIL_Y - 13, FEED_RAIL_Z0))
feed_mount_bolts = []
for x, y in rail_centers():
    side = 1 if x > 0 else -1
    ring = tube(14, RAIL_HOLE, FEED_RAIL_Z0, FEED_RAIL_Z1, x, y)
    upper_ring = ring.common(Part.makeBox(80, 30, 14, V(-40, y + 0.5, FEED_RAIL_Z0 - 1)))
    lower_ring = ring.common(Part.makeBox(80, 30, 14, V(-40, y - 30.5, FEED_RAIL_Z0 - 1)))
    lug_x = 17 if side > 0 else -27
    upper_lug = Part.makeBox(10, 8.5, 12, V(lug_x, y + 0.5, FEED_RAIL_Z0))
    lower_lug = Part.makeBox(10, 8.5, 12, V(lug_x, y - 9, FEED_RAIL_Z0))
    arm = Part.makeBox(14, 4, 12, V(24 if side > 0 else -38, y + 5, FEED_RAIL_Z0))
    post = Part.makeBox(8, FEED_Y - (y + 5), 12,
                        V(30 if side > 0 else -38, y + 5, FEED_RAIL_Z0))
    frame = G.fuse_all([frame, upper_ring, upper_lug, arm, post])
    feeder_rail_cap = G.fuse_all([feeder_rail_cap, lower_ring, lower_lug])
    bx, bz = side * 24.0, (FEED_RAIL_Z0 + FEED_RAIL_Z1) / 2
    bolt_hole = Part.makeCylinder(1.7, 40, V(bx, y - 20, bz), Y)
    frame = frame.cut(bolt_hole).cut(Part.makeCylinder(2.9, 3.3, V(bx, y + 5.8, bz), Y))
    feeder_rail_cap = feeder_rail_cap.cut(bolt_hole)
    bolt = Part.makeCylinder(1.5, 25, V(bx, y - 19, bz), Y)
    head = Part.makeCylinder(2.75, 3, V(bx, y + 6, bz), Y)
    nut = G.hex_prism(5.5, 0, 2.4)
    nut.rotate(V(0, 0, 0), X, 90)
    nut.translate(V(bx, y - 13, bz))
    feed_mount_bolts.append(Part.makeCompound([bolt, head, nut]))
feeder_frame = frame.removeSplitter()
feeder_rail_cap = feeder_rail_cap.removeSplitter()
feeder_mount_hardware = Part.makeCompound(feed_mount_bolts)
# Larger open hopper above the unchanged single-file escapement throat.
HOPPER_ID, HOPPER_WALL = 74.0, 3.0
HOPPER_NECK_Y, HOPPER_CONE_H, HOPPER_CUP_H = FEED_Y + 45.0, 50.0, 40.0
HOPPER_SHOULDER_Y = HOPPER_NECK_Y + HOPPER_CONE_H
HOPPER_TOP_Y = HOPPER_SHOULDER_Y + HOPPER_CUP_H
magazine = feed_bore(0, FEED_Y, HOPPER_NECK_Y + 1, FEED_BORE + 6)
magazine = magazine.fuse(feed_bore(0, FEED_Y, FEED_Y + 4, 44))
magazine = magazine.fuse(Part.makeCone(FEED_BORE / 2 + HOPPER_WALL,
                                     HOPPER_ID / 2 + HOPPER_WALL, HOPPER_CONE_H,
                                     V(0, HOPPER_NECK_Y, FEED_Z), Y))
magazine = magazine.fuse(feed_bore(0, HOPPER_SHOULDER_Y - 0.1, HOPPER_TOP_Y, HOPPER_ID + 2 * HOPPER_WALL))
hopper_void = Part.makeCone(FEED_BORE / 2, HOPPER_ID / 2, HOPPER_CONE_H,
                            V(0, HOPPER_NECK_Y, FEED_Z), Y)
hopper_void = hopper_void.fuse(feed_bore(0, HOPPER_SHOULDER_Y - 0.01, HOPPER_TOP_Y + 1, HOPPER_ID))
magazine = magazine.cut(hopper_void)
# Guide blocks constrain the two fingers; open roof slots clear their follower pegs.
for side in (-1, 1):
    py = PIVOT_Y + side * BALL_D / 2
    guide = Part.makeBox(24, 9, 13.5, V(10, py - 4.5, FEED_Z - 3))
    magazine = magazine.fuse(guide)
magazine = magazine.cut(feed_bore(0, FEED_Y - 1, HOPPER_NECK_Y + 0.01))
for side in (-1, 1):
    py = PIVOT_Y + side * BALL_D / 2
    magazine = magazine.cut(Part.makeBox(37, 6.1, 10.6, V(0, py - 3.05, FEED_Z - 1.8)))
    magazine = magazine.cut(Part.makeBox(18, 5.1, 3, V(18, py - 2.55, FEED_Z + 8.8)))
# Front pivot plate is outside the moving lever and carries the two angular stops.
ear = Part.makeBox(24, 8, 4, V(5, PIVOT_Y - 4, FEED_Z + 14))
for side in (-1, 1):
    t = math.radians(side * ROCKER_ANGLE)
    dx = 16 * math.cos(t) - side * 6.75 * math.sin(t)
    dy = 16 * math.sin(t) + side * 6.75 * math.cos(t)
    rib = Part.makeBox(math.hypot(dx, dy), 5, 4,
                       V(PIVOT_X, PIVOT_Y - 2.5, FEED_Z + 14))
    rib.rotate(V(PIVOT_X, PIVOT_Y, FEED_Z), Z, math.degrees(math.atan2(dy, dx)))
    ear = ear.fuse(rib)
ear = ear.fuse(G.cyl(4.5, FEED_Z + 10.8, FEED_Z + 14.1, PIVOT_X, PIVOT_Y))
ear = ear.cut(G.cyl(2.5, FEED_Z + 10.7, FEED_Z + 17, PIVOT_X, PIVOT_Y))
magazine = magazine.fuse(ear).cut(feed_bore(0, FEED_Y - 1, HOPPER_NECK_Y + 0.01))
magazine = magazine.cut(Part.makeCone(HOPPER_ID / 2, HOPPER_ID / 2 + 1, 2,
                                      V(0, HOPPER_TOP_Y - 2, FEED_Z), Y))
for side in (-1, 1):
    t = math.radians(side * ROCKER_ANGLE)
    stop_x = PIVOT_X + 16 * math.cos(t) - side * 6.75 * math.sin(t)
    stop_y = PIVOT_Y + 16 * math.sin(t) + side * 6.75 * math.cos(t)
    stop_boss = G.cyl(8, FEED_Z + 14, FEED_Z + 21, stop_x, stop_y)
    magazine = magazine.fuse(stop_boss).cut(G.cyl(2.5, FEED_Z + 13.9, FEED_Z + 20.2, stop_x, stop_y))
for x in (-18.5, 18.5):
    d=13 if x>0 else -13
    magazine = magazine.cut(Part.makeCylinder(1.7, 6, V(d, FEED_Y - 1, FEED_Z+d), Y))
    feeder_frame = feeder_frame.cut(Part.makeCylinder(1.25, 4.5, V(d, FEED_Y - 4, FEED_Z-d), Y))
feeder_frame = feeder_frame.removeSplitter()
feeder_magazine = magazine.removeSplitter()
feeder_rocker = rocker_at(REST_ANGLE)
feeder_lower = finger_at(-1, REST_ANGLE)
feeder_upper = finger_at(1, REST_ANGLE)
feeder_release = Part.makeCompound([rocker_at(ROCKER_ANGLE), finger_assembly(-1, ROCKER_ANGLE), finger_assembly(1, ROCKER_ANGLE)])
feeder_axle = m3x6(PIVOT_X, PIVOT_Y, FEED_Z + 10.8)
feeder_stop_bolts = []
for side in (-1, 1):
    t = math.radians(side * ROCKER_ANGLE)
    sx = PIVOT_X + 16 * math.cos(t) - side * 6.75 * math.sin(t)
    sy = PIVOT_Y + 16 * math.sin(t) + side * 6.75 * math.cos(t)
    feeder_stop_bolts.append(m3x6(sx, sy, FEED_Z + 14))
feeder_pin_bolts = Part.makeCompound(feeder_stop_bolts + [finger_bolts(-1, REST_ANGLE), finger_bolts(1, REST_ANGLE)])
# Removable loading guards: side screens, lower catch tray and end screens.
# End apertures clear the moving chamber/nose guide and rail-mounted barrel supports.
GUARD_T = 1.5
GUARD_X = 38.5
GUARD_BOTTOM, GUARD_TOP = RAIL_Y - 16.0, 22.0
GUARD_Z0, GUARD_Z1 = nose.BoundBox.ZMax + 1.5, z_stop + 4.0
shield = Part.makeBox(2 * (GUARD_X + GUARD_T), GUARD_T, GUARD_Z1 - GUARD_Z0,
                      V(-GUARD_X - GUARD_T, GUARD_BOTTOM, GUARD_Z0))
for side in (-1, 1):
    sx = GUARD_X if side > 0 else -GUARD_X - GUARD_T
    shield = shield.fuse(Part.makeBox(GUARD_T, GUARD_TOP - GUARD_BOTTOM, GUARD_Z1 - GUARD_Z0,
                                     V(sx, GUARD_BOTTOM, GUARD_Z0)))
for z in (GUARD_Z0, GUARD_Z1 - GUARD_T):
    end = Part.makeBox(2 * (GUARD_X + GUARD_T), GUARD_TOP - GUARD_BOTTOM, GUARD_T,
                      V(-GUARD_X - GUARD_T, GUARD_BOTTOM, z))
    end = end.cut(G.cyl(CH_OD + 18.0, z - 1, z + GUARD_T + 1))
    for x, y in rail_centers():
        end = end.cut(G.cyl(BUSH_OD + 3.0, z - 1, z + GUARD_T + 1, x, y))
    shield = shield.fuse(end)
# Centre seam lets each half be removed without taking the rails apart.
shield = shield.cut(Part.makeBox(0.6, 100, GUARD_Z1 - GUARD_Z0 + 2,
                                V(-0.3, GUARD_BOTTOM - 1, GUARD_Z0 - 1)))
for side in (-1, 1):
    for z in (FEED_RAIL_Z0 + 3, FEED_RAIL_Z1 - 3):
        axis = V(side, 0, 0)
        shield = shield.cut(Part.makeCylinder(1.7, 4, V(side * 37, -5, z), axis))
        feeder_frame = feeder_frame.cut(Part.makeCylinder(1.25, 8.2, V(side * 29.9, -5, z), axis))
feeder_frame = feeder_frame.removeSplitter()
feeder_guard_left = shield.common(Part.makeBox(50, 100, 100, V(-50, GUARD_BOTTOM - 1, GUARD_Z0 - 1))).removeSplitter()
feeder_guard_right = shield.common(Part.makeBox(50, 100, 100, V(0, GUARD_BOTTOM - 1, GUARD_Z0 - 1))).removeSplitter()
# Two pinned rods and a fixed bellcrank, all axes parallel to machine X.
DRIVE_ANGLE=19.0
LINK_A_Z=(z_nose0+z_nose1)/2-4
LINK_A_Y=18.0
LINK_O_Z,LINK_O_Y=179.4,52.8
LINK_R1,LINK_L1=34.7,63.1
LINK_PHASE=math.radians(-69.88)
LINK_B_Y=PIVOT_Y-BALL_D/2

def link_theta(stroke):
    dz,dy=LINK_A_Z-stroke-LINK_O_Z,LINK_A_Y-LINK_O_Y
    d=math.hypot(dz,dy)
    return math.atan2(dy,dz)-math.acos((d*d+LINK_R1**2-LINK_L1**2)/(2*d*LINK_R1))

_b0=FEED_Z-finger_center(-1,REST_ANGLE)[0]-13
_b1=FEED_Z-finger_center(-1,DRIVE_ANGLE)[0]-13
_t0,_t1=link_theta(0),link_theta(STROKE)
_e0=(math.cos(_t0+LINK_PHASE),math.sin(_t0+LINK_PHASE))
_e1=(math.cos(_t1+LINK_PHASE),math.sin(_t1+LINK_PHASE))
_w0=(_b0-LINK_O_Z,LINK_B_Y-LINK_O_Y)
_w1=(_b1-LINK_O_Z,LINK_B_Y-LINK_O_Y)
LINK_R2=(sum(v*v for v in _w0)-sum(v*v for v in _w1))/(2*(sum(a*b for a,b in zip(_w0,_e0))-sum(a*b for a,b in zip(_w1,_e1))))
LINK_L2=math.hypot(_w0[0]-LINK_R2*_e0[0],_w0[1]-LINK_R2*_e0[1])

def link_points(stroke):
    t=link_theta(stroke)
    a=(LINK_A_Z-stroke,LINK_A_Y)
    o=(LINK_O_Z,LINK_O_Y)
    p=(o[0]+LINK_R1*math.cos(t),o[1]+LINK_R1*math.sin(t))
    c=(o[0]+LINK_R2*math.cos(t+LINK_PHASE),o[1]+LINK_R2*math.sin(t+LINK_PHASE))
    b=(c[0]-math.sqrt(LINK_L2**2-(LINK_B_Y-c[1])**2),LINK_B_Y)
    return a,o,p,c,b

def feed_angle(stroke):
    b=link_points(stroke)[4]
    return math.degrees(math.atan((FEED_Z-b[0]-13-12)/11.9))

# Input journal on the chamber clamp; no longitudinal hammer remains.
nose_upper=nose_upper.fuse(Part.makeBox(6,10,10,V(22,13,LINK_A_Z-5)))
nose_upper=nose_upper.fuse(Part.makeCylinder(2,3,V(28,LINK_A_Y,LINK_A_Z),X))
nose_upper=nose_upper.cut(Part.makeCylinder(1.25,6.2,V(24.9,LINK_A_Y,LINK_A_Z),X)).removeSplitter()
# The journal sits on the 30 deg tie stud: keep the stud's channel open through it (2026-11-21).
nose_upper=nose_upper.cut(nose_rod_cut).removeSplitter()
nose=Part.makeCompound([nose_lower,nose_upper])
qev_closed['Nose_clamp']=nose

qev_open['Nose_clamp']=shifted(nose,-STROKE)
def bolt_x(x,y,z,direction=1):
    bolt=m3x6(0,0,0)
    bolt.rotate(V(0,0,0),Y,90 if direction==1 else -90)
    bolt.translate(V(x,y,z))
    return bolt

def bar_yz(a,b,x0,x1,width=8):
    dz,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dz,dy)
    nz,ny=-dy/length*width/2,dz/length*width/2
    pts=[V(x0,a[1]+ny,a[0]+nz),V(x0,b[1]+ny,b[0]+nz),
         V(x0,b[1]-ny,b[0]-nz),V(x0,a[1]-ny,a[0]-nz)]
    body=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(x1-x0,0,0))
    for z,y in (a,b):body=body.fuse(Part.makeCylinder(width/2,x1-x0,V(x0,y,z),X))
    return body.removeSplitter()

def link_rod(a,b,x0,x1):
    body=bar_yz(a,b,x0,x1)
    for z,y in (a,b):body=body.cut(Part.makeCylinder(2.15,x1-x0+2,V(x0-1,y,z),X))
    return body.removeSplitter()

def linkage_at(stroke):
    a,o,p,c,b=link_points(stroke)
    input_rod=link_rod(a,p,28.3,30.8)
    output_rod=link_rod(c,b,18.2,20.7)
    crank=bar_yz(o,p,25,28).fuse(bar_yz(o,c,25,28))
    # Triangular web makes the two arms a rigid bellcrank.
    pts=[V(25,q[1],q[0]) for q in (o,p,c)]
    crank=crank.fuse(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(3,0,0)))
    crank=crank.cut(Part.makeCylinder(2.15,5,V(24,o[1],o[0]),X))
    crank=crank.fuse(Part.makeCylinder(2,3,V(28,p[1],p[0]),X))
    crank=crank.cut(Part.makeCylinder(1.25,6.2,V(24.9,p[1],p[0]),X))
    crank=crank.fuse(Part.makeCylinder(3,4.1,V(21,c[1],c[0]),X))
    crank=crank.fuse(Part.makeCylinder(2,3,V(18,c[1],c[0]),X))
    crank=crank.cut(Part.makeCylinder(1.25,6.2,V(17.9,c[1],c[0]),X)).removeSplitter()
    bolts=Part.makeCompound([bolt_x(31,a[1],a[0],-1),bolt_x(31,p[1],p[0],-1),
                            bolt_x(18,c[1],c[0]),bolt_x(24.8,o[1],o[0])])
    return input_rod,crank,output_rod,bolts

link_bracket=Part.makeBox(9,3,18,V(25,FEED_Y,176))
link_bracket=link_bracket.fuse(bar_yz((185,FEED_Y+1),(LINK_O_Z,LINK_O_Y),28.2,32,12))
link_bracket=link_bracket.fuse(Part.makeCylinder(2,3.4,V(24.8,LINK_O_Y,LINK_O_Z),X))
link_bracket=link_bracket.cut(Part.makeCylinder(1.25,6.2,V(24.7,LINK_O_Y,LINK_O_Z),X))
link_bracket=link_bracket.cut(Part.makeBox(20,30,40,V(20,FEED_Y-30,165)))
link_bracket_bolts=[]
for z in (180,190):
    link_bracket=link_bracket.cut(Part.makeCylinder(1.7,5,V(29,FEED_Y-1,z),Y))
    feeder_frame=feeder_frame.cut(Part.makeCylinder(1.25,3.2,V(29,FEED_Y-3.1,z),Y))
    bolt=m3x6(0,0,0);bolt.rotate(V(0,0,0),X,90);bolt.translate(V(29,FEED_Y+3,z))
    link_bracket_bolts.append(bolt)
link_bracket=link_bracket.removeSplitter()
feeder_frame=feeder_frame.removeSplitter()
link_input,link_crank,link_output,link_bolts=linkage_at(0)
link_bracket_hardware=Part.makeCompound(link_bracket_bolts)

feeder_parts = {'Link_bracket':link_bracket, 'Feeder_frame': feeder_frame, 'Feeder_rail_cap': feeder_rail_cap,
                'Guard_left': feeder_guard_left, 'Guard_right': feeder_guard_right,
                'Feeder_rocker': feeder_rocker,
                'Feeder_lower': feeder_lower, 'Feeder_upper': feeder_upper,
                'Feeder_magazine': feeder_magazine}
# Keep local geometry functions for dimensions; place the entire escapement around Y.
def turn_feeder(shape):
    result=shape.copy()
    result.rotate(V(0,0,FEED_Z),Y,90)
    return result

def turned_function(fn):
    return lambda *args: turn_feeder(fn(*args))

for name in ('Feeder_rocker','Feeder_lower','Feeder_upper','Feeder_magazine'):
    feeder_parts[name]=turn_feeder(feeder_parts[name])
feeder_rocker=feeder_parts['Feeder_rocker']
feeder_lower=feeder_parts['Feeder_lower']
feeder_upper=feeder_parts['Feeder_upper']
feeder_magazine=feeder_parts['Feeder_magazine']
feeder_release=turn_feeder(feeder_release)
feeder_axle=turn_feeder(feeder_axle)
feeder_stop_bolts=[turn_feeder(sh) for sh in feeder_stop_bolts]
feeder_pin_bolts=turn_feeder(feeder_pin_bolts)
# Each assembly calls the now-transformed primitive functions exactly once.
finger_at=turned_function(finger_at)
finger_bolts=turned_function(finger_bolts)
rocker_at=turned_function(rocker_at)

# Clearance pocket for the output-joint socket head; keep at least 2 mm of neck wall.
head_pockets=[]
for i in range(17):
    c=link_points(STROKE*i/16)[3]
    head_pockets.append(Part.makeCylinder(3.05,5,V(14.7,c[1],c[0]),X))
feeder_magazine=feeder_magazine.cut(G.fuse_all(head_pockets)).removeSplitter()
feeder_parts['Feeder_magazine']=feeder_magazine

feeder_checks = [(n + ' valid single solid', G.single_solid(sh)) for n, sh in feeder_parts.items()]
# Quasi-static rigid-ball probes: model the gravity hand-off between the two stops.
# These are geometry checks, not a soft-body/friction simulation; probes stay out of exports.
for i in range(17):
    angle = -ROCKER_ANGLE + 2 * ROCKER_ANGLE * i / 16
    lever = rocker_at(angle)
    lower, upper = finger_assembly(-1, angle), finger_assembly(1, angle)
    moving = Part.makeCompound([lever, lower, upper])
    feeder_checks.append(('rocker/fingers travel %d/16 clear' % i,
                         G.no_overlap(moving, feeder_frame) and G.no_overlap(moving, feeder_magazine)
                         and G.no_overlap(lever, lower) and G.no_overlap(lever, upper)
                         and all(G.no_overlap(lever, bolt) for bolt in [feeder_axle] + feeder_stop_bolts)))
    supports = []
    for side in (-1, 1):
        px, py = finger_center(side, angle)
        supports.append(py + math.sqrt((BALL_D / 2 + FINGER_R) ** 2 - px ** 2)
                        if px < BALL_D / 2 + FINGER_R else None)
    # Even a ball shifted to the far side of the bore must meet at least one stop.
    feeder_checks.append(('at least one finger retains stack %d/16' % i,
                         min(finger_center(side, angle)[0] for side in (-1, 1))
                         < BALL_D / 2 + FINGER_R - (FEED_BORE - BALL_D) / 2))
    if supports[0] is not None:
        ball_y = supports[0]
        probe = Part.makeSphere(BALL_D / 2, V(0, ball_y, FEED_Z))
        feeder_checks.append(('lower ball clearance %d/16' % i, G.no_overlap(probe, moving)))
        next_y = max(ball_y + BALL_D, supports[1] if supports[1] is not None else -1e9)
    else:
        next_y = supports[1]
    probe = Part.makeSphere(BALL_D / 2, V(0, next_y, FEED_Z))
    feeder_checks.append(('next ball clearance %d/16' % i, G.no_overlap(probe, moving)))
for n, sh in dict(feeder_parts, Feeder_release=feeder_release).items():
    for pose, shapes in [('closed', qev_closed), ('open', qev_open)]:
        feeder_checks.append((n + ' clears station ' + pose,
                              all(G.no_overlap(sh, obj) for obj in shapes.values())))

# Check the tunnel against the whole translating station, including intermediate poses.
for i in range(11):
    moving_shapes = [shifted(sh, -STROKE * i / 10) for sh in qev_closed.values()]
    feeder_checks.append(('low feeder tunnel clears moving station %d/10' % i,
                         all(G.no_overlap(feeder_frame, sh) and G.no_overlap(feeder_magazine, sh)
                             for sh in moving_shapes)))

# Include the fixed parts omitted from the moving-station dictionary.
for n, sh in feeder_parts.items():
    for fixed_name, fixed_shape in [('barrel', fixed_barrel), ('rear clamp', barrel_clamp),
                                    ('front collar', barrel_collar), ('rails', rails_s)]:
        feeder_checks.append((n + ' clears fixed ' + fixed_name, G.no_overlap(sh, fixed_shape)))
feeder_checks += [
    ('Barrel_clamp valid two halves', barrel_clamp.isValid() and len(barrel_clamp.Solids) == 2),
    ('Barrel_clamp clears barrel', G.no_overlap(barrel_clamp, fixed_barrel)),
    ('rail clamp upper/lower halves separated', G.no_overlap(feeder_frame, feeder_rail_cap)),
    ('fixed feeder portal ahead of nose travel', FEED_RAIL_Z0 > nose.BoundBox.ZMax + 0.5),
    ('hopper throat unchanged', abs(FEED_BORE - 25.4) < 1e-6),
]

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
     min(s.BoundBox.YMin for s in (vent_body, vent_fittings, cradle, vent_plunger))
     >= y_floor + 5.0 - 1e-6 and min_clear(feet, vent_body) >= 0.5),
    ("feet reach the rail underside", post_height_ok),
    ("stance vs tip (halfX %.0f >= 0.30 x %.0f; Z span %.0f)"
     % (half_width, tip_lever, stance_z), tip_ok),
    ("print volume both feet %.0f cm3 < 80" % (bed_vol / 1000.0), vol_ok),
    ("feet clear of closed carriage (%.1f mm)" % bed_vs_closed, bed_vs_closed >= 0.5),
    ("feet clear of open carriage (%.1f mm)" % bed_vs_open, bed_vs_open >= 0.5),
    ("feet clear of QEV body (%.1f mm)" % bed_vs_qev, bed_vs_qev >= 0.5),
    ("four adjustable rail stops present", len(stops) == 4),
    ("station library: all geometry checks", all(ok for _, ok in station_checks)),
]

guard_checks = []
for name, guard in [('left', feeder_guard_left), ('right', feeder_guard_right)]:
    for fixed_name, fixed in [('portal', feeder_frame), ('rail cap', feeder_rail_cap), ('hopper', feeder_magazine)]:
        guard_checks.append((name + ' guard clears ' + fixed_name, G.no_overlap(guard, fixed)))
    for i in range(11):
        guard_checks.append((name + ' guard clears moving station %d/10' % i,
                             all(G.no_overlap(guard, shifted(sh, -STROKE * i / 10)) for sh in qev_closed.values())))
checks += feeder_checks + stop_checks + guard_checks

# Integrated motion: both rods remain pinned throughout the full carriage stroke.
def link_clear(a,b):
    aa,bb=a.BoundBox,b.BoundBox
    if (aa.XMax<=bb.XMin or bb.XMax<=aa.XMin or aa.YMax<=bb.YMin or
        bb.YMax<=aa.YMin or aa.ZMax<=bb.ZMin or bb.ZMax<=aa.ZMin):
        return True
    return G.no_overlap(a,b)

actuation_checks=[('output screw pocket leaves 2 mm neck wall',14.7-FEED_BORE/2>=2-1e-6),
                  ('upper nose half valid',G.single_solid(nose_upper)),
                  ('nose halves separated',link_clear(nose_lower,nose_upper))]
# Since 2026-11-21 the rear washers and nuts sit behind the carriage bridge (studs 2 x M3 x STUD_L).
_stud_hw_gap=min(shifted(hardware,dz_).distToShape(s_)[0] for dz_ in (0.0,-STROKE) for s_ in (front_foot,rear_foot,stops_s,cradle))
actuation_checks+=[('nose clamp clear of the tie studs (%.2f mm3)'%nose.common(hardware).Volume,nose.common(hardware).Volume<0.01),
                   ('stud nuts behind the bridge clear of feet, stops and valve cradle, open and closed (%.1f)'%_stud_hw_gap,_stud_hw_gap>=0.5)]
release_angle=math.degrees(math.atan((BALL_D/2+FINGER_R-(FEED_BORE-BALL_D)/2-12)/11.9))
release_stroke=next(STROKE*i/10000 for i in range(10001) if feed_angle(STROKE*i/10000)>=release_angle)
clear_stroke=z_tip-(FEED_Z-BALL_D/2)
actuation_checks.append(('ball release after tip clears loading space',release_stroke>clear_stroke+.5))
for i in range(33):
    stroke=STROKE*i/32;angle=feed_angle(stroke)
    rods=linkage_at(stroke);inp,crank,out,bolts=rods
    moving_feeder=Part.makeCompound([rocker_at(angle),finger_assembly(-1,angle),finger_assembly(1,angle)])
    fixed=[sh for n,sh in feeder_parts.items() if n not in ('Feeder_rocker','Feeder_lower','Feeder_upper')]+[fixed_barrel,rails_s,barrel_clamp,barrel_collar]
    actuation_checks.append(('linkage valid solids %d/32'%i,all(G.single_solid(sh) for sh in rods[:3])))
    actuation_checks.append(('linkage clears fixed parts %d/32'%i,all(link_clear(sh,f) for sh in rods[:3] for f in fixed)))
    actuation_checks.append(('linkage clears moving station %d/32'%i,all(link_clear(sh,shifted(m,-stroke)) for sh in rods[:3] for m in qev_closed.values())))
    actuation_checks.append(('linkage self clearance %d/32'%i,all(link_clear(rods[j],rods[k]) for j in range(3) for k in range(j+1,3))))
    actuation_checks.append(('linkage clears feeder %d/32'%i,all(link_clear(sh,moving_feeder) for sh in rods[:3])))
    actuation_checks.append(('link bracket clears moving feeder %d/32'%i,link_clear(link_bracket,moving_feeder)))
    actuation_checks.append(('link screws clear surrounding parts %d/32'%i,
        all(link_clear(bolts,sh) for sh in [feeder_magazine,feeder_frame,moving_feeder]+[shifted(sh,-stroke) for n,sh in qev_closed.items() if n!='Nose_clamp'])))
    a,o,p,c,b=link_points(stroke)
    actuation_checks.append(('both rod lengths close %d/32'%i,abs(math.dist(a,p)-LINK_L1)<1e-7 and abs(math.dist(c,b)-LINK_L2)<1e-7))
    actuation_checks.append(('output journal matches follower %d/32'%i,abs(b[0]-(FEED_Z-finger_center(-1,angle)[0]-13))<1e-7))
    actuation_checks.append(('output away from toggle %d/32'%i,abs(b[0]-c[0])/LINK_L2>.5))
actuation_checks += [
    ('linkage endpoint margins to hard stops',feed_angle(0)>-ROCKER_ANGLE+.5 and feed_angle(STROKE)<ROCKER_ANGLE-.5),
]
checks+=actuation_checks

report = [
    NAME,
    "  purpose                : hand bench for one linear-breech station (open / load / close / fire)",
    "  feet                   : 2x pad %.0fx%.0fx%.0f mm at y %.1f; rails are the beam (no long slab)"
    % (FOOT_PAD_X, FOOT_T, FOOT_PAD_Z, y_floor),
    "  volume                 : %.0f cm3 both feet; front z %.0f, rear z %.0f, stance %.0f mm"
    % (bed_vol / 1000.0, front_z, rear_z, stance_z),
    "  lengths                : Chamber_tube %.1f mm; Fixed_barrel %.1f mm; rails %.1f mm"
    % (chamber.BoundBox.ZLength, fixed_barrel.BoundBox.ZLength, z_rail1 - z_rail0),
    "  station                : stroke %.1f mm; AirTAC tip unpressed - dump the pilot by hand"
    % STROKE,
    "  rail stops             : 4 split collars, 4x M3x20 + nuts, stroke %.1f mm; rails extended rearwards 12 mm" % STROKE,
    "  feeder                 : gravity, soft ball 23.8 mm, bore 25.4 mm, two-finger rocker +/-20 deg",
    "  hopper                 : mouth ID 74 mm, OD 80 mm, 50 mm taper + 40 mm cup; fixed portal clamps to both rails",
    "  feeder orientation     : escapement rotated 90 deg; fixed bellcrank with two positively connected rods",
    "  linkage centre lengths : input %.2f mm; output %.2f mm; crank radii %.2f / %.2f mm" % (LINK_L1,LINK_L2,LINK_R1,LINK_R2),
    "  feeder sequence        : pinned linkage releases at %.2f mm withdrawal; linkage returns feeder on closing; no return spring" % release_stroke,
    "  feeder limitation      : verify soft-ball singulation, joint backlash and friction on bench",
    "  finger prints          : feeder_finger_lower and feeder_finger_upper differ; old feeder_finger is obsolete",
    "  linkage hardware       : M3x6 retained shoulder journals; 4 new pivot screws + 2 bracket screws; existing lower follower screw reused",
    "  feeder height          : seat %.1f mm, top %.1f mm; chamber tunnel radial clearance %.1f mm, crown wall %.1f mm"
    % (FEED_Y, HOPPER_TOP_Y, TUNNEL_CLEAR, TUNNEL_ROOF),
    "  guards                 : two removable side screens with catch tray and end screens; 4x M3x10 screws",
    "  feeder joint           : fixed two-rail portal, removable lower clamp bar, independent of barrel clamp",
    "  feeder hardware        : 2x M3x8 flange screws; 7x M3x6 socket-head screws replace all escapement pins (axis, followers, contacts, stops); 2x M3x25 rail-clamp bolts + nuts",
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
    "Carriage", "Nose_clamp", "Barrel_clamp", "Barrel_collar", "Link_input", "Link_crank", "Link_output", "Link_bracket",
    "AirTAC_cradle", "Foot_front", "Foot_rear", "Rail_stops",
    "Feeder_frame", "Feeder_rail_cap", "Guard_left", "Guard_right", "Feeder_rocker", "Feeder_lower", "Feeder_upper", "Feeder_magazine",
}
NONPRINTABLE_PARTS = {
    "Barrel_stub", "Chamber_tube", "Tie_rods", "Pilot_fitting", "Link_bolts", "Link_bracket_hardware",
    "Rails", "Fixed_barrel", "AirTAC_body", "AirTAC_fittings",
    "AirTAC_plunger", "Feeder_axle", "Feeder_pin_bolts", "Rail_stop_hardware", "Feeder_mount_hardware",
}
PART_GROUP = {
    **dict.fromkeys(PRINTABLE_PARTS, "Printable"),
    **dict.fromkeys(NONPRINTABLE_PARTS, "NonPrintable"),
}
SCENE_PARTS = set(qev_closed) | {"Link_input", "Link_crank", "Link_output", "Link_bracket", "Link_bolts", "Link_bracket_hardware",
    "Rails", "Barrel_clamp", "Barrel_collar", "Fixed_barrel",
    "AirTAC_cradle", "Foot_front", "Foot_rear", "Rail_stops",
    "Feeder_frame", "Feeder_rail_cap", "Guard_left", "Guard_right", "Feeder_rocker", "Feeder_lower", "Feeder_upper", "Feeder_magazine",
    "AirTAC_body", "AirTAC_fittings", "AirTAC_plunger", "Feeder_axle", "Feeder_pin_bolts", "Rail_stop_hardware", "Feeder_mount_hardware",
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
    ("Rail_stops", stops_s, "rotor"),
    ("AirTAC_body", vent_body, "steel"),
    ("AirTAC_fittings", vent_fittings, "ghost"),
    ("AirTAC_plunger", vent_plunger, "shoe"),
):
    sc.add(PART_GROUP[n], n, s, style)
for n,shape in [('Link_input',link_input),('Link_crank',link_crank),('Link_output',link_output)]:
    sc.add('Printable',n,shape,'rotor')
sc.add('NonPrintable','Link_bolts',link_bolts,'steel')
sc.add('NonPrintable','Link_bracket_hardware',link_bracket_hardware,'steel')
sc.add("NonPrintable", "Feeder_mount_hardware", feeder_mount_hardware, "steel")
sc.add("NonPrintable", "Feeder_axle", feeder_axle, "steel")
sc.add("NonPrintable", "Feeder_pin_bolts", feeder_pin_bolts, "steel")
sc.add("NonPrintable", "Rail_stop_hardware", stop_hardware, "steel")
for n, shape in feeder_parts.items():
    obj = sc.add("Printable", n, shape, "stator" if n.startswith("Guard_") else
                 ("rotor" if n == "Feeder_rocker" else "printed"))
if SHOW_OPEN:
    for n, s in qev_open.items():
        sc.add(PART_GROUP[n] + "Open", "Open_" + n, s, "ghost")

for text, pos in [
    ("ДВЕ ОПОРЫ — рельсы сами балка", (0, y_floor - 12, (front_z + rear_z) / 2)),
    ("РУКАМИ: открыть / закрыть, толкать за QEV", (0, push_y + 10, z_ry - CARR_T / 2)),
    ("ЗАКРЫТО → AirTAC сброс → выстрел", (60, 0, z_stop)),
    ("ОТКРЫТО → пулька сверху (+Y)", (60, 40, z_stop - STROKE / 2)),
]:
    sc.label("Labels", text, pos)
sc.group("Labels").Label = "Справка"

# The shared rotor view maps gravity sideways; orient this bench with +Y upward.
bench_view = App.Placement(V(0, 0, 0), App.Rotation(Y, 90))
for obj in sc.doc.Objects:
    if obj.TypeId == "Part::Feature":
        obj.Placement = bench_view.multiply(obj.Placement)
sc.finish(hidden_groups=("Labels", "PrintableOpen", "NonPrintableOpen"), opaque_groups=())
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, flip=False, lay=None):
    """Export in print orientation (z = 0 on the bed). lay='pad': put the foot pad down."""
    s = shape.copy()
    if lay == "pad":
        s.rotate(V(0, 0, 0), X, 90)    # assembly -Y (pad) -> -Z
    if lay == "side":
        s.rotate(V(0, 0, 0), Y, 90)
    if flip:
        s.rotate(V(0, 0, 0), X, 180)
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.2).write(
        os.path.join(OUT_DIR, name + ".stl"))


# Each stop is used twice; left/right have mirrored outward clamp ears.
write(front_foot, "foot_front", lay="pad")
write(rear_foot, "foot_rear", lay="pad")
write(nose, "nose_clamp")
write(link_input,"link_input",lay="side")
write(link_crank,"link_crank",lay="side")
write(link_output,"link_output",lay="side")
write(link_bracket,"link_bracket")
write(stops[0], "rail_stop_left")
write(stops[2], "rail_stop_right")
write(barrel_clamp, "barrel_clamp", flip=True)
write(barrel_collar, "barrel_collar", flip=True)
write(cradle, "airtac_cradle", flip=True)
write(feeder_frame, "feeder_frame")
write(feeder_rail_cap, "feeder_rail_cap")
write(feeder_guard_left, "feeder_guard_left")
write(feeder_guard_right, "feeder_guard_right")
write(feeder_rocker, "feeder_rocker")
write(feeder_lower, "feeder_finger_lower")
write(feeder_upper, "feeder_finger_upper")
write(feeder_magazine, "feeder_magazine", lay="pad")
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling linear breech bench has [FAIL] checks")
