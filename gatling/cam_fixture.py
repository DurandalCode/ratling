# -*- coding: utf-8 -*-
"""
Gatling cam fixture: the stroke cam laid flat over the one-station bench (stage 3).

On the pack the liner stands still and the station turns inside it, its finger
in the liner's groove (R 104 from the pack axis). On the bench the station
stands still, the pack axis is 22 mm over the table, and a Ø218 ring would turn
87 mm into it. So the groove is unrolled: a flat plate carries the same groove
z(s) at s = R 104 * angle, and is pushed across the bench (X) by hand. The
finger meets the same wall slope (pressure angle) as on the liner; the force
on the plate times 0.104 m is the torque one station needs from the crank.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/cam_fixture.py').read())"

The bench stays as built. The fixture adds:
- a half ring on the carriage's aft face, clamped under the nuts of the two QEV
  tie studs (needs ~5 mm more thread behind the carriage), with the finger
  Ø5 at the top, where the pack's follower is (r 37 from the station axis);
- the cam plate (groove from 22 to 128 deg of the law: FIRE flat, OPEN ramp,
  LOAD flat; pushed back it runs the CLOSE ramp, the mirror image). The groove
  ends are the travel stops; ticks every 10 deg on its top;
- a portal on the table around the bench: two side frames, a top plate and
  four 623 rollers on the plate's edges at x = ±18, beside the finger, so the
  axial reaction goes into rollers, not into sliding friction. The frames sit
  in M4 slots (±4 mm along the barrel) to set the FIRE flat on the seated QEV.

Loosen the bench's closed stops for the test: the cam sets the closed position.

Exports: exports/gatling_cam_fixture/ (STEP, STL in print orientation, FCStd).
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_cam_fixture")
NAME = "gatling_cam_fixture"
V = App.Vector
O = V(0, 0, 0)
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

# ---------------------------------------------------------------- bench as library
print("load linear_breech_bench…", flush=True)
B = {"REPO": REPO, "LINEAR_BREECH_BENCH_LIBRARY": True}
try:
    exec(open(os.path.join(REPO, "gatling", "linear_breech_bench.py")).read(), B)
except SystemExit as _e:
    bench_ok = _e.code in (0, None)
else:
    bench_ok = True
STROKE = B["STROKE"]
CH_OD = B["CH_OD"]
y_floor = B["y_floor"]
z_aft = B["z_ry"] - B["CARR_T"]              # carriage bridge aft face (closed)
carriage = B["carriage"]
qev_closed = B["qev_closed"]

# ---------------------------------------------------------------- law and cam radius (as breech_mechanism.py)
R_PACK = 67.0
EAR_ENV, CLEAR, CAM_WALL_IN = 33.0, 0.5, 2.5
CAM_R = R_PACK + EAR_ENV + CLEAR + CAM_WALL_IN + 1.0     # groove centre radius, 104
FIRE_A, FIRE_B = 330.0, 30.0
OPEN_A, OPEN_B = 30.0, 120.0
LOAD_A, LOAD_B = 120.0, 240.0
CLOSE_A, CLOSE_B = 240.0, 330.0


def cam_u(phi_deg):
    """Same law as breech_mechanism.cam_u: half-cosine ramps between dwell flats."""
    phi = phi_deg % 360.0
    if phi >= FIRE_A or phi <= FIRE_B:
        return 0.0
    if OPEN_A < phi < OPEN_B:
        return 0.5 * (1.0 - math.cos(math.pi * (phi - OPEN_A) / (OPEN_B - OPEN_A)))
    if LOAD_A <= phi <= LOAD_B:
        return 1.0
    if CLOSE_A < phi < CLOSE_B:
        return 0.5 * (1.0 + math.cos(math.pi * (phi - CLOSE_A) / (CLOSE_B - CLOSE_A)))
    return 0.0


def cam_dz(phi_deg):
    return -STROKE * cam_u(phi_deg)


# ---------------------------------------------------------------- parameters
PSI0, PSI1 = 22.0, 128.0        # groove span on the plate: 8 deg of each flat around the OPEN ramp
FOLLOWER_OD = 5.0
FOLLOWER_CLEAR = 0.5
G_R = FOLLOWER_OD / 2 + FOLLOWER_CLEAR      # groove half-width, 3.0
Y_TIP = CAM_R - R_PACK                       # finger tip, r 37 from the station axis (as the pack)
Y_PB = CAM_R - CAM_WALL_IN - R_PACK          # plate underside = liner bore, 34.5
PLATE_T = 10.0
Y_PT = Y_PB + PLATE_T
Y_FLOOR = Y_TIP + FOLLOWER_OD / 2 + 0.8      # groove bottom, 0.8 over the finger tip
EDGE = 6.0                                   # strip outside the groove: roller face + ledge
BRK_T = FOLLOWER_OD                          # bracket = finger thickness: flat on the bed
BRK_R0, BRK_R1 = 12.0, 31.0
BOSS_Y1 = 32.0
TIE_R, TIE_ANGLES, TIE_HOLE = B["TIE_R"], B["TIE_ANGLES"], B["TIE_HOLE"]
EAR_R = 5.5
# The half ring goes on the studs between the bridge and the washers: with the fixture
# on, the stud washers and nuts sit BRK_T further aft and the studs are BRK_T longer
# (since 2026-11-21 the bench draws them behind the bridge, where the ring is).
_hw = qev_closed["Tie_rods"]
_hw_aft = _hw.common(Part.makeBox(100, 100, 100, V(-50, -50, z_aft - 100)))
_hw_aft.translate(V(0, 0, -BRK_T))
qev_closed = dict(qev_closed)
qev_closed["Tie_rods"] = G.fuse_all([_hw_aft, _hw.common(Part.makeBox(100, 100, 400, V(-50, -50, z_aft)))]
                                    + [G.cyl(B["TIE_D"], z_aft - BRK_T - 0.1, z_aft + 0.1, *B["at"](TIE_R, a)[:2])
                                       for a in TIE_ANGLES]).removeSplitter()
STUD_L_FIXTURE = B["STUD_L"] + BRK_T
# Rollers: 623ZZ (3 x 10 x 4) on M3 axles, rim 0.1 off the plate edge.
BRG_OD, BRG_ID, BRG_W = 10.0, 3.0, 4.0
XR = 18.0                       # roller pairs at x = ±XR, beside the finger
R_GAP = 0.1
ARM_W, ARM_D = 12.0, 13.0       # arm block across X / out from the plate edge
LEDGE_IN, LEDGE_T, LEDGE_GAP = 3.0, 2.5, 0.3
TOP_GAP, TOP_T = 9.5, 6.0
FRAME_X0, FRAME_T = 46.0, 6.0    # side frames' inner face, thickness
POST_W, BAR_T = 10.0, 8.0
PAD_W, PAD_T, SLOT_D, SLOT_L = 30.0, 6.0, 4.4, 8.0
M_END = XR + BRG_OD / 2 + 3.0    # plate past the groove ends: always over both roller pairs
HOOK_D = 6.0
BED = 256.0

z_f = z_aft - BRK_T / 2          # finger centre, closed
T_GROOVE = CAM_R * math.radians(PSI1 - PSI0)
z_hi = z_f + G_R + EDGE          # plate front edge (toward the muzzle)
z_lo = z_f - STROKE - G_R - EDGE
z_mid = 0.5 * (z_hi + z_lo)
y_mid = 0.5 * (Y_PB + Y_PT)


def u_of(psi):
    """Plate-local x of the groove point at law angle psi."""
    return CAM_R * math.radians(psi - PSI0)


def x_plate(psi):
    """Plate offset that puts the groove point psi over the finger (x = 0)."""
    return -u_of(psi)


def moved(shape, dx=0.0, dz=0.0):
    s = shape.copy()
    s.translate(V(dx, 0, dz))
    return s


def gap(a, b, pad=2.0):
    """Min distance, solid by solid, with a bounding-box shortcut (99 = far apart)."""
    ba, bb_ = a.BoundBox, b.BoundBox
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad, ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    if not ba2.intersect(bb_):
        return 99.0
    g = 99.0
    for x in (a.Solids or [a]):
        bx = x.BoundBox
        bx2 = App.BoundBox(bx.XMin - pad, bx.YMin - pad, bx.ZMin - pad, bx.XMax + pad, bx.YMax + pad, bx.ZMax + pad)
        for y in (b.Solids or [b]):
            if bx2.intersect(y.BoundBox):
                g = min(g, x.distToShape(y)[0])
    return g


# ---------------------------------------------------------------- finger bracket (rides the carriage)
_sector = Part.makeCylinder(BRK_R1, BRK_T, V(0, 0, z_aft - BRK_T), Z, 180.0)
_sector = _sector.cut(Part.makeCylinder(BRK_R0, BRK_T + 2, V(0, 0, z_aft - BRK_T - 1)))
_sector.rotate(O, Z, TIE_ANGLES[0])          # 30 -> 210 deg over the top
_ears = [G.cyl(2 * EAR_R, z_aft - BRK_T, z_aft, *B["at"](TIE_R, a)[:2]) for a in TIE_ANGLES]
_boss = Part.makeBox(10.0, BOSS_Y1 - (BRK_R1 - 6.0), BRK_T, V(-5.0, BRK_R1 - 6.0, z_aft - BRK_T))
finger = Part.makeCylinder(FOLLOWER_OD / 2, Y_TIP - (BOSS_Y1 - 1.0), V(0, BOSS_Y1 - 1.0, z_f), Y)
finger = finger.fuse(Part.makeSphere(FOLLOWER_OD / 2, V(0, Y_TIP, z_f))).removeSplitter()
bracket = G.fuse_all([_sector, _boss, finger] + _ears)
bracket = bracket.cut(G.fuse_all([G.cyl(TIE_HOLE, z_aft - BRK_T - 1, z_aft + 1, *B["at"](TIE_R, a)[:2])
                                  for a in TIE_ANGLES]))
bracket = bracket.cut(carriage).removeSplitter()     # the carriage webs stand 1 mm proud aft
tip = Part.makeSphere(FOLLOWER_OD / 2, V(0, Y_TIP, z_f))

# ---------------------------------------------------------------- cam plate (unrolled groove)
# Slot outline: the centreline offset by ±G_R along its normal (centreline radius >= 82 mm,
# so the offsets stay clean), round ends.
_n = int(round((PSI1 - PSI0) / 0.5))
_y0 = Y_PB - 1.0
_cl = []
for i in range(_n + 1):
    psi = PSI0 + (PSI1 - PSI0) * i / _n
    h = 0.01
    tx = CAM_R * math.radians(2 * h)
    tz = cam_dz(psi + h) - cam_dz(psi - h)
    tl = math.hypot(tx, tz)
    _cl.append((u_of(psi), z_f + cam_dz(psi), -tz / tl, tx / tl))      # point, unit normal in XZ


def _side(sgn):
    c = Part.BSplineCurve()
    c.interpolate([V(x + sgn * G_R * nx, _y0, z + sgn * G_R * nz) for x, z, nx, nz in _cl])
    return c.toShape()


_up, _dn = _side(+1), _side(-1)
_e0 = Part.LineSegment(_dn.Vertexes[0].Point, _up.Vertexes[0].Point).toShape()
_e1 = Part.LineSegment(_up.Vertexes[-1].Point, _dn.Vertexes[-1].Point).toShape()
_slot2d = Part.Wire([_up, _e1, _dn, _e0])
groove = Part.Face(_slot2d).extrude(V(0, Y_FLOOR - _y0, 0))
for x, z, nx, nz in (_cl[0], _cl[-1]):
    groove = groove.fuse(Part.makeCylinder(G_R, Y_FLOOR - _y0, V(x, _y0, z), Y))
groove = groove.removeSplitter()
plate = Part.makeBox(T_GROOVE + 2 * M_END, PLATE_T, z_hi - z_lo, V(-M_END, Y_PB, z_lo))
plate = plate.cut(groove)
for xh in (-M_END + 9.0, T_GROOVE + M_END - 9.0):
    plate = plate.cut(Part.makeCylinder(HOOK_D / 2, PLATE_T + 2, V(xh, Y_PB - 1, z_mid), Y))
ticks = []
for k in range(3, 13):
    psi = 10.0 * k
    long_ = psi in (30.0, 120.0)
    L = 30.0 if long_ else 16.0
    ticks.append(Part.makeBox(0.8, 0.6 + 1.0, L, V(u_of(psi) - 0.4, Y_PT - 0.6, z_mid - L / 2)))
plate = plate.cut(G.fuse_all(ticks)).removeSplitter()
plate = plate.Solids[0] if len(plate.Solids) == 1 else plate

# ---------------------------------------------------------------- portal: rollers, arms, top plate, side frames
y_ledge0 = Y_PB - LEDGE_GAP - LEDGE_T
y_top0 = Y_PT + TOP_GAP
y_top1 = y_top0 + TOP_T
rollers, axles, arms = [], [], []
for side in (+1, -1):                       # +1: front edge (z_hi), -1: rear edge (z_lo)
    ze = z_hi if side > 0 else z_lo
    zc = ze + side * (BRG_OD / 2 + R_GAP)
    for xs in (-XR, XR):
        r = Part.makeCylinder(BRG_OD / 2, BRG_W, V(xs, y_mid - BRG_W / 2, zc), Y)
        r = r.cut(Part.makeCylinder(BRG_ID / 2, BRG_W + 2, V(xs, y_mid - BRG_W / 2 - 1, zc), Y))
        rollers.append(r)
        axles.append(Part.makeCylinder(1.5, y_top1 - y_ledge0 + 4.0, V(xs, y_ledge0 - 2.5, zc), Y))
        z0, z1 = (ze + 0.6, ze + ARM_D) if side > 0 else (ze - ARM_D, ze - 0.6)
        blk = Part.makeBox(ARM_W, y_top0 - y_ledge0, z1 - z0, V(xs - ARM_W / 2, y_ledge0, z0))
        lz0, lz1 = (ze - LEDGE_IN, ze + 0.6) if side > 0 else (ze - 0.6, ze + LEDGE_IN)
        blk = blk.fuse(Part.makeBox(ARM_W, LEDGE_T, lz1 - lz0, V(xs - ARM_W / 2, y_ledge0, lz0)))
        blk = blk.cut(Part.makeCylinder(BRG_OD / 2 + 0.5, BRG_W + 0.6, V(xs, y_mid - BRG_W / 2 - 0.3, zc), Y))
        arms.append(blk)
z_post_f0 = z_hi + ARM_D + 1.0
z_post_r1 = z_lo - ARM_D - 1.0
z_frame0, z_frame1 = z_post_r1 - POST_W, z_post_f0 + POST_W
top = Part.makeBox(2 * (FRAME_X0 + FRAME_T), TOP_T, z_frame1 - z_frame0,
                   V(-(FRAME_X0 + FRAME_T), y_top0, z_frame0))
top = G.fuse_all([top] + arms)
for a in axles:
    top = top.cut(Part.makeCylinder(1.6, 200, V(a.BoundBox.Center.x, y_ledge0 - 50, a.BoundBox.Center.z), Y))
# Rear axles in slots along Z (±1 mm): set the rollers on the plate without play.
for xs in (-XR, XR):
    zc = z_lo - (BRG_OD / 2 + R_GAP)
    top = top.cut(Part.makeBox(3.2, 200, 2.0, V(xs - 1.6, y_ledge0 - 50, zc - 1.0)))
    for dz in (-1.0, 1.0):
        top = top.cut(Part.makeCylinder(1.6, 200, V(xs, y_ledge0 - 50, zc + dz), Y))
# Sight window over the ticks, index edge on x = 0.
top = top.cut(Part.makeBox(6.0, 50, 40.0, V(0.0, y_top0 - 10, z_mid - 20.0)))
FRAME_BOLT_Z = (z_frame0 + POST_W / 2, z_frame1 - POST_W / 2)
for sx in (-1, 1):
    for zb in FRAME_BOLT_Z:
        top = top.cut(Part.makeCylinder(1.7, 50, V(sx * (FRAME_X0 + FRAME_T / 2), y_top0 - 20, zb), Y))  # M3 clearance
top = top.removeSplitter()


def side_frame(sx):
    """Plate in the YZ plane at x = sx*(46..52): web below the cam plate, two posts and a bar above."""
    x0 = FRAME_X0 if sx > 0 else -(FRAME_X0 + FRAME_T)
    y_web1 = Y_PB - 1.0
    web = Part.makeBox(FRAME_T, y_web1 - y_floor, z_frame1 - z_frame0, V(x0, y_floor, z_frame0))
    # lighten: a window with one diagonal
    m = 12.0
    win = Part.makeBox(FRAME_T + 2, y_web1 - y_floor - PAD_T - 2 * m, z_frame1 - z_frame0 - 2 * m,
                       V(x0 - 1, y_floor + PAD_T + m, z_frame0 + m))
    w_h, w_l = win.BoundBox.YLength, win.BoundBox.ZLength
    diag = Part.makeBox(FRAME_T + 4, 10.0, math.hypot(w_h, w_l) + 20,
                        V(x0 - 2, -5.0, -10.0))
    diag.rotate(O, X, -math.degrees(math.atan2(w_h, w_l)))
    diag.translate(V(0, win.BoundBox.YMin, win.BoundBox.ZMin))
    web = web.cut(win.cut(diag))
    posts = [Part.makeBox(FRAME_T, y_top0 - y_web1 + 0.01, POST_W, V(x0, y_web1, zp))
             for zp in (z_frame0, z_frame1 - POST_W)]
    bar = Part.makeBox(FRAME_T, BAR_T, z_frame1 - z_frame0, V(x0, y_top0 - BAR_T, z_frame0))
    px0 = FRAME_X0 if sx > 0 else -(FRAME_X0 + PAD_W)
    pad = Part.makeBox(PAD_W, PAD_T, z_frame1 - z_frame0, V(px0, y_floor, z_frame0))
    f = G.fuse_all([web, bar, pad] + posts)
    xs = sx * (FRAME_X0 + FRAME_T + (PAD_W - FRAME_T) / 2)
    for zs in (z_frame0 + 15.0, z_frame1 - 15.0):
        sl = Part.makeCylinder(SLOT_D / 2, PAD_T + 2, V(xs, y_floor - 1, zs - SLOT_L / 2), Y).fuse(
            Part.makeCylinder(SLOT_D / 2, PAD_T + 2, V(xs, y_floor - 1, zs + SLOT_L / 2), Y)).fuse(
            Part.makeBox(SLOT_D, PAD_T + 2, SLOT_L, V(xs - SLOT_D / 2, y_floor - 1, zs - SLOT_L / 2)))
        f = f.cut(sl)
    for zb in FRAME_BOLT_Z:
        f = f.cut(Part.makeCylinder(1.3, 20, V(sx * (FRAME_X0 + FRAME_T / 2), y_top0 - 18, zb), Y))  # M3 self-tapping
    return f.removeSplitter()


frame_r = side_frame(+1)
frame_l = side_frame(-1)
portal_printed = [top, frame_r, frame_l]
portal_all = portal_printed + rollers + axles

# ---------------------------------------------------------------- bench parts the fixture must miss
bench_fixed = [B["rails_s"], B["front_foot"], B["rear_foot"], B["stops_s"], B["cradle"], B["vent_body"],
               B["vent_fittings"], B["vent_plunger"], B["barrel_clamp"], B["barrel_collar"], B["fixed_barrel"],
               B["link_input"], B["link_crank"], B["link_output"]] + list(B["feeder_parts"].values())
bench_moving = [s for n, s in qev_closed.items() if n not in ("Tie_rods",)]   # hardware is the fat-coax stack


def table_hit(shape):
    return shape.BoundBox.YMin < y_floor - 1e-6


# ---------------------------------------------------------------- checks
print("sweep…", flush=True)
psis = [PSI0 + 0.5 + i * 1.0 for i in range(int(PSI1 - PSI0))]
track_over, track_near, track_far, plate_bench, plate_portal, roll_min, roll_max = 0.0, 99.0, 0.0, 99.0, 99.0, 99.0, 0.0
bracket_portal = 99.0
for i, psi in enumerate(psis):
    xp, dz = x_plate(psi), cam_dz(psi)
    pl = moved(plate, xp)
    t = moved(tip, 0.0, dz)
    track_over = max(track_over, pl.common(t).Volume)
    d_wall = pl.distToShape(t)[0]          # tip to the nearest groove wall
    track_near = min(track_near, d_wall)
    track_far = max(track_far, d_wall)
    if i % 3 == 0:
        mv = [moved(s, 0.0, dz) for s in bench_moving] + [moved(bracket.cut(Part.makeCylinder(
            FOLLOWER_OD / 2 + 0.01, 30, V(0, BOSS_Y1 + 0.5, z_f), Y)), 0.0, dz)]
        for s in mv + bench_fixed:
            plate_bench = min(plate_bench, gap(pl, s))
        for s in portal_printed:
            plate_portal = min(plate_portal, gap(pl, s))
        for r in rollers:
            d = gap(pl, r)
            roll_min, roll_max = min(roll_min, d), max(roll_max, d)
        bracket_portal = min(bracket_portal, min(gap(moved(bracket, 0.0, dz), s) for s in portal_all))
# groove ends stop the finger
end0 = moved(plate, x_plate(PSI0)).distToShape(moved(tip, 0.0, cam_dz(PSI0)))[0]
end1 = moved(plate, x_plate(PSI1)).distToShape(moved(tip, 0.0, cam_dz(PSI1)))[0]
# the finger hits the groove end a little past PSI0 / PSI1: how far past
stop_over = []
for psi_end, sgn in ((PSI0, -1.0), (PSI1, 1.0)):
    d = 0.0
    while d < 10.0:
        if moved(plate, x_plate(psi_end + sgn * d)).common(moved(tip, 0.0, cam_dz(psi_end))).Volume > 1e-4:
            break
        d += 0.1
    stop_over.append(d)
# portal vs bench, all carriage positions
portal_bench = 99.0
for k in range(0, 12):
    dz = -STROKE * k / 11.0
    for s in [moved(s, 0.0, dz) for s in bench_moving + [bracket]] + bench_fixed:
        for p in portal_all:
            portal_bench = min(portal_bench, gap(p, s))
bracket_on_carr = bracket.distToShape(carriage)[0]
bracket_overlap = bracket.common(carriage).Volume
bracket_pilot = bracket.distToShape(qev_closed["Pilot_fitting"])[0]
stud_ok = all(not bracket.isInside(V(*B["at"](TIE_R, a)[:2], z_aft - BRK_T / 2), 1e-3, True) for a in TIE_ANGLES)
cover_ok = (-M_END + x_plate(PSI0) <= -(XR + BRG_OD / 2) and T_GROOVE + M_END + x_plate(PSI1) >= XR + BRG_OD / 2)
_slopes = [abs(cam_dz(p + 0.05) - cam_dz(p - 0.05)) / (CAM_R * math.radians(0.1)) for p in psis]
alpha_max = math.degrees(math.atan(max(_slopes)))
alpha_th = math.degrees(math.atan(math.pi / 2 * STROKE / (CAM_R * math.radians(OPEN_B - OPEN_A))))


def print_shape(name):
    """Part in print orientation (z = 0 on the bed)."""
    s = {"cam_plate": plate, "finger_bracket": bracket, "portal_top": top,
         "side_frame_right": frame_r, "side_frame_left": frame_l}[name].copy()
    if name in ("cam_plate", "portal_top"):
        s.rotate(O, X, -90.0)          # top face down: groove / arms up
    elif name == "side_frame_right":
        s.rotate(O, Y, -90.0)          # inner face (x = 46) down, pad up
    elif name == "side_frame_left":
        s.rotate(O, Y, 90.0)
    # finger_bracket: aft face down as it is (finger lies in the plane)
    s.translate(V(-s.BoundBox.XMin, -s.BoundBox.YMin, -s.BoundBox.ZMin))
    return s


PRINT_NAMES = ("cam_plate", "finger_bracket", "portal_top", "side_frame_right", "side_frame_left")
prints = {n: print_shape(n) for n in PRINT_NAMES}
bed_ok = all(max(p.BoundBox.XLength, p.BoundBox.YLength) <= BED - 6 and p.BoundBox.ZLength <= BED
             for p in prints.values())
solids_ok = all(G.single_solid(s) for s in (plate, bracket, top, frame_r, frame_l))
frame_low_ok = abs(frame_r.BoundBox.YMin - y_floor) < 1e-6 and abs(frame_l.BoundBox.YMin - y_floor) < 1e-6
nothing_under = not any(table_hit(s) for s in [plate, bracket, top] + rollers + axles)

checks = [
    ("bench as library [OK]", bench_ok),
    ("law: groove %.0f..%.0f deg = %.1f mm of liner at R %.0f; stroke %.1f" % (PSI0, PSI1, T_GROOVE, CAM_R, STROKE),
     abs(CAM_R - 104.0) < 1e-6 and abs(STROKE - 65.8) < 0.05),
    ("finger rides the groove, every 1 deg: overlap %.4f mm3, wall %.2f..%.2f mm (clearance %.1f)"
     % (track_over, track_near, track_far, FOLLOWER_CLEAR),
     track_over < 1e-3 and track_near >= FOLLOWER_CLEAR - 0.05 and track_far <= FOLLOWER_CLEAR + 0.05),
    ("groove ends stop the finger %.1f / %.1f deg past the span (tip %.2f / %.2f off the ends)"
     % (stop_over[0], stop_over[1], end0, end1), max(stop_over) <= 1.0 and max(end0, end1) <= FOLLOWER_CLEAR + 0.05),
    ("pressure angle max %.1f deg (half-cosine over 90 deg at R 104: %.1f)" % (alpha_max, alpha_th),
     abs(alpha_max - alpha_th) < 0.3),
    ("plate clear of the bench, station and bracket at every pose: %.2f >= 1.0" % plate_bench, plate_bench >= 1.0),
    ("plate clear of the portal (frames, arms, top): %.2f >= 0.3" % plate_portal, plate_portal >= 0.3 - 1e-6),
    ("rollers on the plate edges: %.2f..%.2f mm" % (roll_min, roll_max), 0.05 <= roll_min and roll_max <= 0.15),
    ("plate always over both roller pairs (x ±%.0f)" % XR, cover_ok),
    ("portal clear of the bench at every carriage position: %.2f >= 1.0" % portal_bench, portal_bench >= 1.0),
    ("bracket clear of the portal at every pose: %.2f >= 1.0" % bracket_portal, bracket_portal >= 1.0),
    ("bracket on the carriage aft face: gap %.3f, overlap %.4f mm3" % (bracket_on_carr, bracket_overlap),
     bracket_on_carr < 0.05 and bracket_overlap < 1e-3),
    ("bracket holes on both tie studs; pilot fitting clear %.2f" % bracket_pilot, stud_ok and bracket_pilot >= 1.0),
    ("half ring ahead of the stud washers and nuts (%.2f mm3): studs 2 x M3 x %.0f with the fixture on"
     % (bracket.common(qev_closed["Tie_rods"]).Volume, STUD_L_FIXTURE), bracket.common(qev_closed["Tie_rods"]).Volume < 0.01),
    ("finger at r %.0f, plate underside at the liner bore r %.1f (as the pack)" % (Y_TIP + R_PACK, Y_PB + R_PACK),
     abs(Y_TIP - 37.0) < 1e-6 and abs(Y_PB - 34.5) < 1e-6),
    ("side frames stand on the table (y %.0f), nothing else below it" % y_floor, frame_low_ok and nothing_under),
    ("printed parts single solids", solids_ok),
    ("printed parts fit the %.0f bed" % BED, bed_ok),
]

report = [
    NAME,
    "  idea                   : liner groove unrolled flat at R %.0f; plate pushed across the bench (X)" % CAM_R,
    "  groove                 : %.0f..%.0f deg = %.1f mm; FIRE flat to %.0f, OPEN to %.0f, LOAD flat;"
    " back = CLOSE" % (PSI0, PSI1, T_GROOVE, OPEN_A, OPEN_B),
    "  cam plate              : %.1f x %.0f x %.0f mm (X x Z x Y), underside at y %.1f, groove %.0f wide, %.1f deep"
    % (T_GROOVE + 2 * M_END, z_hi - z_lo, PLATE_T, Y_PB, 2 * G_R, Y_FLOOR - Y_PB),
    "  finger                 : Ø%.0f at r %.0f, on a half ring under the tie-stud nuts (%.0f mm: studs"
    " 2 x M3 x %.0f with it on, %.0f on the bench)" % (FOLLOWER_OD, Y_TIP, BRK_T, STUD_L_FIXTURE, B["STUD_L"]),
    "  rollers                : 4 x 623ZZ at x ±%.0f on the plate edges (rear pair on ±1 mm slots)" % XR,
    "  portal                 : side frames at x ±%.0f..%.0f, top plate y %.1f..%.1f; frames on M4 slots ±%.0f mm"
    % (FRAME_X0, FRAME_X0 + FRAME_T, y_top0, y_top1, SLOT_L / 2),
    "  pressure angle         : %.1f deg max; plate force F -> one station's torque F x %.3f m" % (alpha_max, CAM_R / 1000),
    "  hardware               : 4 x 623ZZ, 4 x M3x30 + nuts (axles), 4 x M3x20 self-tapping (top plate to frames),"
    " 4 x M4 (or wood screws) to the table, luggage scale + string",
    "  plate travel -> stroke (plate moved from the FIRE end; carriage aft of closed):",
]
for k in range(2, 13):
    psi = 10.0 * k + (2.0 if k == 2 else 0.0)
    if psi > PSI1:
        break
    report.append("    %5.0f deg  plate %6.1f mm   carriage %5.1f mm  %s"
                  % (psi, u_of(psi), -cam_dz(psi), "FIRE" if psi <= OPEN_A else ("LOAD" if psi >= OPEN_B else "OPEN")))
report.append("  volumes cm3            : " + ", ".join("%s %.1f" % (n, prints[n].Volume / 1000.0) for n in PRINT_NAMES))
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

try:
    CAM_FIXTURE_LIBRARY
except NameError:
    CAM_FIXTURE_LIBRARY = False
if CAM_FIXTURE_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

# ---------------------------------------------------------------- scene + export
PSI_SHOW = 75.0
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
dz_show, xp_show = cam_dz(PSI_SHOW), x_plate(PSI_SHOW)
sc.add("Fixture", "Cam_plate", moved(plate, xp_show), "rotor")
sc.add("Fixture", "Finger_bracket", moved(bracket, 0.0, dz_show), "rotor")
sc.add("Fixture", "Portal_top", top, "printed")
sc.add("Fixture", "Side_frame_right", frame_r, "printed")
sc.add("Fixture", "Side_frame_left", frame_l, "printed")
sc.add("Hardware", "Rollers_623", Part.makeCompound(rollers), "steel")
sc.add("Hardware", "Roller_axles_M3", Part.makeCompound(axles), "steel")
for n, s in qev_closed.items():
    sc.add("Bench", "Bench_" + n, moved(s, 0.0, dz_show), "ghost")
for n, s in (("Rails", B["rails_s"]), ("Foot_front", B["front_foot"]), ("Foot_rear", B["rear_foot"]),
             ("Rail_stops", B["stops_s"]), ("AirTAC_cradle", B["cradle"]), ("AirTAC_body", B["vent_body"]),
             ("Barrel_clamp", B["barrel_clamp"]), ("Barrel_collar", B["barrel_collar"]),
             ("Fixed_barrel", B["fixed_barrel"])):
    sc.add("Bench", "Bench_" + n, s, "ghost")
for n, s in B["feeder_parts"].items():
    sc.add("Bench", "Bench_" + n, s, "ghost")
sc.label("Labels", "ПЛАСТИНА КУЛАЧКА: толкать поперёк (X), безмен за отверстие", (0, Y_PT + 30, z_hi + 30))
sc.label("Labels", "ПАЛЕЦ Ø5 на салазках (полукольцо под гайки шпилек)", (0, Y_TIP, z_f + dz_show - 30))
sc.group("Fixture").Label = "Приспособление (печать)"
sc.group("Hardware").Label = "Покупное"
sc.group("Bench").Label = "Стенд (справка)"
sc.group("Labels").Label = "Подписи"
bench_view = App.Placement(V(0, 0, 0), App.Rotation(Y, 90))
for obj in sc.doc.Objects:
    if obj.TypeId == "Part::Feature":
        obj.Placement = bench_view.multiply(obj.Placement)
sc.finish(hidden_groups=("Labels",), opaque_groups=("Fixture",))
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart
for n, s in prints.items():
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.2).write(
        os.path.join(OUT_DIR, n + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("exported:", OUT_DIR)
