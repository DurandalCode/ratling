# -*- coding: utf-8 -*-
"""
Gatling breech mechanism (not a freeze).

Stroke from linear_breech (65.8 mm) -> angle->stroke law -> outboard cam liner ->
six phases -> AirTAC on each carriage, fixed firing ramp and trigger -> star
feed geared to the pack (rim on the breech clamps + fixed train) -> helical
guard -> side crank, carry, strap -> air: hollow axle, bearings, MQR, buffer.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism.py').read())"

The full-turn clearance sweep (every station part against every fixed part,
every 3 deg; neighbours every 5 deg of phase) is a separate run in parallel
freecadcmd workers, ~4.5 min:

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism_sweep.py').read())"

Pack R / casing may move if parts will not seat. No wheeled carriage; no
full-length tube. Exports: exports/gatling_breech_mechanism/

The model is built in its final pose: hopper and star on +X (top), firing
sector at the bottom (-X), crank on -Y. Pack angle phi (0 = FIRE) sits at
world angle phi + 180.

2026-11-20 (owner's choice of the three layouts in docs/gatling.md, plan
questions 2-4):
- The AirTAC rides its carriage on a bracket behind the bridge, plunger aft,
  fittings to the sides. Its line A to the pilot is short and rigid (as on the
  bench); the supply line R flexes with the stroke. The six valves no longer
  meet at the axis (the old hub overlap was 11.3 cm3 per pair at any R).
- A fixed ramp on the firing sector presses the plungers at the closed
  position: touch 331.6 -> 28.4 deg, 2.5 mm full press on 338..22. The
  trigger pulls the ramp forward into reach; let go, a spring takes it 4 mm
  aft and no plunger is pressed. The press pushes the QEV onto its stop.
- The star of feed_bench.py replaces the auger. A geared rim on the breech
  clamps (it is the rear barrel-plate, ahead of the clamps; the old plate
  overlapped the closed QEVs by 22 cm3) drives it through a fixed train
  120 -> 40 | 18 -> 18 -> 27: three external meshes, -2. A shaft from behind
  the pack cannot reach the star: the liner and the fingers take r 101.5..107.
- The guard follows the ball while the station closes (202..279 deg) and
  stays inside the breech clamp's feed notch.
- The carriage and the nose guide ride the bought Al tubes, as on the bench:
  the printed stroke-rail cage sat on their bores (1745 / 2312 mm3) and is
  gone. The tubes end in a rear disk on the axle.
- The liner groove is blind (the groove used to cut through the wall and
  split the drum in two rings); the liner is the frame around the cam, and
  the spars start ahead of it, off the fingers' orbit.
- Hollow axle Al 38 x 1.5 on two 6808 (40 x 52 x 7, 1 mm shim); the six
  1/8" (6 mm) supply lines run inside it to the MQR rotor, so no rotating
  line crosses a fixed part (the old lines cut the bearing disk, buffer and
  frame).
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
import ratling.gears as GR
for _m in (G, FV, GR):
    importlib.reload(_m)

try:
    BREECH_MECH_LIBRARY
except NameError:
    BREECH_MECH_LIBRARY = False     # True: build + fast checks only (breech_mechanism_sweep.py)

OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
V = App.Vector
O = V(0, 0, 0)
ZA = V(0, 0, 1)

TARGET_L = 750.0
BARREL_SHOW_DEFAULT = 160.0
N = 6
R_PACK = 67.00                  # = breech_pack PINNED_R; rail feet need >= 66.3
CASE_OD_START = 218.0           # previous frame envelope (2026-11-19)
L_START = 1033.0                # previous overall length
CLEAR = 0.5
PLATE_T, PLATE_LIP, PLATE_RIM = 14.0, 1.5, 3.0

CAM_WALL_IN = 2.5               # liner wall inside the groove centre (as before)
GROOVE_FLOOR = 2.0              # material behind the groove bottom (blind groove)
FOLLOWER_OD = 5.0
FOLLOWER_CLEAR = 0.5
CAM_Z_PAD = 8.0
CAM_CLEAR_Z = 2.0
EAR_ENV = 33.0

FIRE_A, FIRE_B = 330.0, 30.0
OPEN_A, OPEN_B = 30.0, 120.0
LOAD_A, LOAD_B = 120.0, 240.0
CLOSE_A, CLOSE_B = 240.0, 330.0

print("load linear_breech…", flush=True)
GATLING_LINEAR_BREECH_LIBRARY = True
PACK_STATION = True
SHOW_OPEN = False
BARREL_SHOW = BARREL_SHOW_DEFAULT
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin
BARREL_SHOW = TARGET_L - (z_stop - Z_AFT_CLIP)
assert BARREL_SHOW > 50.0
print("reload BARREL_SHOW=%.1f…" % BARREL_SHOW, flush=True)
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin

BENCH_STROKE = STROKE
assert abs(BENCH_STROKE - (FIT_INSERT + PELLET_D + STROKE_MARGIN)) < 1e-6
print("STROKE=%.1f" % BENCH_STROKE, flush=True)


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


def tube(od, idd, z0, z1, x=0.0, y=0.0):
    return G.cyl(od, z0, z1, x, y).cut(G.cyl(idd, z0 - 1, z1 + 1, x, y))


def cam_u(phi_deg):
    phi = phi_deg % 360.0
    if phi >= FIRE_A or phi <= FIRE_B:
        return 0.0
    if OPEN_A < phi < OPEN_B:
        t = (phi - OPEN_A) / (OPEN_B - OPEN_A)
        return 0.5 * (1.0 - math.cos(math.pi * t))
    if LOAD_A <= phi <= LOAD_B:
        return 1.0
    if CLOSE_A < phi < CLOSE_B:
        t = (phi - CLOSE_A) / (CLOSE_B - CLOSE_A)
        return 0.5 * (1.0 + math.cos(math.pi * t))
    return 0.0


def cam_dz(phi_deg):
    return -BENCH_STROKE * cam_u(phi_deg)


def phase_name(phi_deg):
    phi = phi_deg % 360.0
    if phi >= FIRE_A or phi <= FIRE_B:
        return "FIRE"
    if OPEN_A < phi < OPEN_B:
        return "OPEN"
    if LOAD_A <= phi <= LOAD_B:
        return "LOAD"
    if CLOSE_A < phi < CLOSE_B:
        return "CLOSE"
    return "?"


def wdeg(phi_deg):
    """World angle (deg, from +X) of pack angle phi: FIRE at the bottom (-X)."""
    return phi_deg + 180.0


def polar(r, phi_deg, z=0.0):
    a = math.radians(wdeg(phi_deg))
    return V(r * math.cos(a), r * math.sin(a), z)


def place(shape, phi_deg, dz=0.0):
    """Station-local shape (+Y radial out, +Z muzzle) at pack angle phi."""
    s = shape.copy()
    if dz:
        s.translate(V(0, 0, dz))
    a = wdeg(phi_deg)
    s.rotate(O, ZA, a - 90.0)
    s.translate(V(R_PACK * math.cos(math.radians(a)), R_PACK * math.sin(math.radians(a)), 0))
    return s


def rot(shape, deg, centre=O):
    s = shape.copy()
    s.rotate(centre, ZA, deg)
    return s


def _near(ba, bb_, pad):
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad,
                       ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    return ba2.intersect(bb_)


def gap(a, b, pad=2.0):
    """Min distance, solid by solid with a bounding-box shortcut (99 = far apart)."""
    if not _near(a.BoundBox, b.BoundBox, pad):
        return 99.0
    sa = a.Solids or [a]
    sb = b.Solids or [b]
    g = 99.0
    for x in sa:
        bx = x.BoundBox
        if not _near(bx, b.BoundBox, pad):
            continue
        for y in sb:
            if _near(bx, y.BoundBox, pad):
                g = min(g, x.distToShape(y)[0])
    return g


def gap_solids(a_list, b_list, pad=2.0):
    """Min gap between two lists of solids, pairwise with bbox prefilter."""
    g = 99.0
    for a in a_list:
        for b in b_list:
            g = min(g, gap(a, b, pad))
    return g


def r_max(shape, defl=0.5):
    pts = shape.tessellate(defl)[0]
    return max(math.hypot(p.x, p.y) for p in pts) if pts else 0.0


def tube_path(points, r):
    """Hose as straight cylinders through the points (sketch of the route)."""
    segs = []
    for p0, p1 in zip(points[:-1], points[1:]):
        v = p1.sub(p0)
        if v.Length > 0.5:
            segs.append(Part.makeCylinder(r, v.Length, p0, v))
            segs.append(Part.makeSphere(r, p1))
    return Part.makeCompound(segs)


def path_len(points):
    return sum((b - a).Length for a, b in zip(points[:-1], points[1:]))


# ============================================================ station (pack variant)
# Rails: bought Al tubes, from the rear disk to the muzzle. The carriage and the
# nose guide ride them through plain bores (feet), as on the bench.
REAR_DISK_Z0, REAR_DISK_Z1 = -127.0, -121.0     # behind the open carriage and pilot fitting
REAR_DISK_R = 46.0
rails_pack = rails_s.common(Part.makeBox(400, 400, 2000, V(-200, -200, REAR_DISK_Z0)))
qev_slide = [qev_closed[k].copy() for k in qev_closed]
fixed_station = [rails_pack, barrel_clamp, barrel_collar, fixed_barrel]

# --- AirTAC M3R110 on the carriage: bracket on the bridge's aft face, plunger aft,
# T (27) across the station, fittings to the sides (A to -x, R and P to +x).
A_W, A_T, A_L = AIRTAC["W"], AIRTAC["T"], AIRTAC["L"]
PL_D, PL_L = AIRTAC["plunger"]
VALVE_Y = 16.5                  # body y 7.5..25.5: 1.0 off the pilot fitting and the finger
BRACKET_T = 3.0
z_carr_aft = qev_closed["Carriage"].BoundBox.ZMin
z_valve1 = z_carr_aft - BRACKET_T
z_valve0 = z_valve1 - A_L               # stem face
z_tip_free = z_valve0 - PL_L            # plunger tip, free, station closed
valve_body = Part.makeBox(A_T, A_W, A_L, V(-A_T / 2, VALVE_Y - A_W / 2, z_valve0))
valve_fit = Part.makeCompound([
    Part.makeCylinder(AIRTAC["straight"]["A"][0] / 2, AIRTAC["straight"]["A"][1],
                      V(-A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["A"]), V(-1, 0, 0)),
    Part.makeCylinder(AIRTAC["straight"]["R"][0] / 2, AIRTAC["straight"]["R"][1],
                      V(A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["R"]), V(1, 0, 0)),
    Part.makeCylinder(AIRTAC["silencer"][0] / 2, AIRTAC["silencer"][1],
                      V(A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["P"]), V(1, 0, 0))])
valve_plunger = Part.makeCylinder(PL_D / 2, PL_L, V(0, VALVE_Y, z_tip_free))
# Bracket: a plate between the bridge and the body, out to the bridge ear at 30 deg
# (M3 on the QEV tie stud); its own bolt pattern is set at fitting.
_ear = at(TIE_R, TIE_ANGLES[0])
valve_bracket = Part.makeBox(A_T, A_W, BRACKET_T, V(-A_T / 2, VALVE_Y - A_W / 2, z_valve1))
valve_bracket = valve_bracket.fuse(Part.makeBox(_ear.x + 6.0 - A_T / 2, 12.0, BRACKET_T,
                                                V(A_T / 2 - 0.5, _ear.y - 6.0, z_valve1)))
valve_bracket = valve_bracket.fuse(G.cyl(2 * CARR_EAR_R, z_valve1, z_carr_aft, _ear.x, _ear.y))
valve_bracket = valve_bracket.cut(G.cyl(TIE_HOLE, z_valve1 - 1, z_carr_aft + 1, _ear.x, _ear.y)).removeSplitter()

# --- line A (1/8" = 6 mm tube), A port -> pilot fitting: rigid, moves with the carriage.
HOSE_OD, HOSE_ID = 6.0, 4.0
_pf = qev_closed["Pilot_fitting"].BoundBox
_a_end = V(-A_T / 2 - AIRTAC["straight"]["A"][1], VALVE_Y, z_valve0 + AIRTAC["ports"]["A"])
line_a_pts = [_a_end, V(_a_end.x + 4.0, 3.0, _a_end.z + 3.0), V(-6.0, 0.0, _pf.ZMin - 7.0),
              V(0.0, 0.0, _pf.ZMin - 3.0), V(0.0, 0.0, _pf.ZMin)]
line_a = tube_path(line_a_pts, HOSE_OD / 2)
LINE_A_L = path_len(line_a_pts)
LINE_A_V = math.pi * (HOSE_ID / 2) ** 2 * LINE_A_L / 1000.0

valve_group = Part.makeCompound([valve_body, valve_fit, valve_bracket, line_a])
slide0 = Part.makeCompound(qev_slide + [valve_group])     # + follower, set after the cam

# --- line R (supply), R port -> axle window: flexes with the stroke (route is a sketch).
_r_end = V(A_T / 2 + AIRTAC["straight"]["R"][1], VALVE_Y, z_valve0 + AIRTAC["ports"]["R"])
AXLE_OD, AXLE_ID = 38.0, 34.6     # Al 38 x 1.5 from the mitrailleuse bench (measured ID ~34.6)
Z_AXLE_WIN = -110.0               # axle windows the six lines enter, inside the pack hub
R_BUNDLE = 6.5                    # line centres inside the axle


def line_r_pts(dz):
    """R line in station-local coordinates for carriage offset dz."""
    z = _r_end.z + dz
    return [V(_r_end.x, _r_end.y, z),
            V(A_T / 2 + 2.5 + HOSE_OD / 2, VALVE_Y, z - 3.0),     # turn down beside the body
            V(A_T / 2 + 2.5 + HOSE_OD / 2, 1.5, z - 6.0),
            V(0.0, 1.5, z - 10.0),                                # under the body, onto the station's plane
            V(0.0, -42.0, Z_AXLE_WIN + 8.0),                      # between its own rails (slot in the rear disk)
            V(0.0, -R_PACK + AXLE_OD / 2 + 2.0, Z_AXLE_WIN - 2.0),
            V(0.0, -R_PACK + R_BUNDLE, Z_AXLE_WIN - 10.0)]


def line_r(dz):
    return tube_path(line_r_pts(dz), HOSE_OD / 2)


# ============================================================ cam liner + follower
z_cam1 = z_carr_aft - CAM_CLEAR_Z
z_tip0 = z_cam1 - CAM_Z_PAD * 0.5
z_cam0 = z_tip0 - BENCH_STROKE - CAM_Z_PAD
CAM_R = R_PACK + EAR_ENV + CLEAR + CAM_WALL_IN + 1.0       # groove centre radius (104)
groove_r = FOLLOWER_OD / 2 + FOLLOWER_CLEAR
cam_id = 2.0 * (CAM_R - CAM_WALL_IN)
cam_od = 2.0 * (CAM_R + groove_r + GROOVE_FLOOR)
y_tip = CAM_R - R_PACK
y_root = CH_OD / 2 + 2.0
follower = Part.makeCylinder(FOLLOWER_OD / 2, max(6.0, y_tip - y_root), V(0, y_root, z_tip0), V(0, 1, 0))
follower = follower.fuse(Part.makeSphere(FOLLOWER_OD / 2 + 0.2, V(0, y_tip, z_tip0))).removeSplitter()
_stem_z1 = z_ry - CARR_T
if _stem_z1 > z_tip0 + 2.0:
    follower = follower.fuse(Part.makeCylinder(FOLLOWER_OD / 2, _stem_z1 - z_tip0,
                                               V(0, y_root + 2.0, z_tip0), ZA)).removeSplitter()
drum = tube(cam_od, cam_id, z_cam0, z_cam1)
_balls = []
for _i in range(36):
    _ang = 360.0 * _i / 36.0
    _balls.append(Part.makeSphere(groove_r, polar(CAM_R, _ang, z_tip0 + cam_dz(_ang))))
cam = drum.cut(Part.makeCompound(_balls))
try:
    cam = cam.removeSplitter()
except Exception:
    pass


def follower_on_track(phi):
    tip = place(Part.makeSphere(FOLLOWER_OD / 2, V(0, y_tip, z_tip0)), phi, cam_dz(phi))
    ideal = Part.makeSphere(0.5, polar(CAM_R, phi, z_tip0 + cam_dz(phi)))
    return tip.distToShape(ideal)[0] <= FOLLOWER_CLEAR + 0.3


slide0 = Part.makeCompound(qev_slide + [valve_group, follower])
fixed0 = Part.makeCompound(fixed_station)


def station(phi):
    """(moving, fixed, plunger, line R) of the station at pack angle phi."""
    dz = cam_dz(phi)
    return (place(slide0, phi, dz), place(fixed0, phi), place(valve_plunger, phi, dz),
            place(line_r(dz), phi))


# ============================================================ six phases, neighbour gaps
print("pack R=%.2f liner groove R=%.1f Ø%.1f" % (R_PACK, CAM_R, cam_od), flush=True)
phases = []
stations = []
for k in range(N):
    ang = k * 60.0
    mv, fx, pl, lr = station(ang)
    stations.append(Part.makeCompound([mv, fx, pl, lr]))
    phases.append((k + 1, ang, cam_u(ang), cam_dz(ang), phase_name(ang)))
# Core (QEV + guides) on the six phases, as before.
_cores = [place(Part.makeCompound(qev_slide), k * 60.0, cam_dz(k * 60.0)) for k in range(N)]
gap_core = min(_cores[k].distToShape(_cores[(k + 1) % N])[0] for k in range(N))
# Whole stations incl. the valve group and both lines, on the six phases (every
# 5 deg in breech_mechanism_sweep.py).
gap_nbr = min(gap(stations[k], stations[(k + 1) % N]) for k in range(N))
# Own station: valve group vs its fixed parts, line R vs its QEV and guides.
gap_own = 99.0
for k in range(N):
    p = k * 60.0
    gap_own = min(gap_own, gap(place(valve_group, p, cam_dz(p)), place(fixed0, p)),
                  gap(place(line_r(cam_dz(p)), p), place(Part.makeCompound(qev_slide), p, cam_dz(p))))
print("core gap %.2f, station gap (with valves) %.2f, valve/line to own %.2f" % (gap_core, gap_nbr, gap_own), flush=True)

# ============================================================ firing ramp + trigger
RAMP_GAP, RAMP_PRESS, RAMP_RISE, RAMP_RETRACT = 1.0, 2.5, 10.0, 4.0
SWITCH = 2.0                    # AirTAC switches at ~2.0 of plunger travel (pistol bench)
RAMP_HW, RAMP_DEPTH = 4.0, 6.0
R_TIP = R_PACK + VALVE_Y
z_ramp_low = z_tip_free - RAMP_GAP


def ramp_h(psi):
    """Ramp face above its low level at pack angle psi (deg, symmetric about 0)."""
    a = abs(((psi + 180.0) % 360.0) - 180.0)
    if a >= 30.0:
        return 0.0
    if a <= 30.0 - RAMP_RISE:
        return RAMP_GAP + RAMP_PRESS
    t = (30.0 - a) / RAMP_RISE
    return (RAMP_GAP + RAMP_PRESS) * 0.5 * (1.0 - math.cos(math.pi * t))


def _ramp_curve(r):
    pts = [polar(r, q, z_ramp_low + ramp_h(q)) for q in [x - 30.0 for x in range(61)]]
    c = Part.BSplineCurve()
    c.interpolate(pts)
    return c.toShape()


_rf = Part.makeRuledSurface(_ramp_curve(R_TIP - RAMP_HW), _ramp_curve(R_TIP + RAMP_HW))
_rf = _rf.Faces[0] if hasattr(_rf, "Faces") else _rf
ramp = _rf.extrude(V(0, 0, -RAMP_DEPTH))
# Arm through a slot in the liner's aft part to the trigger under the pack.
_arm_z0, _arm_z1 = z_ramp_low - RAMP_DEPTH, z_ramp_low - 1.0
TRIG_R1 = cam_od / 2 + 32.0
_arm = Part.makeBox(TRIG_R1 - (R_TIP + RAMP_HW - 1.0), 8.0, _arm_z1 - _arm_z0,
                    V(R_TIP + RAMP_HW - 1.0, -4.0, _arm_z0))
_finger = Part.makeBox(10.0, 14.0, 40.0, V(TRIG_R1 - 10.0, -7.0, _arm_z0 + 5.0))
trigger = _arm.fuse(_finger).removeSplitter()
trigger.rotate(O, ZA, wdeg(0.0))
ramp_fire = ramp.fuse(trigger)
ramp_safe = shifted(ramp_fire, -RAMP_RETRACT)
# Slot in the liner for the arm (clear of the groove: at FIRE it is at z_tip0).
_slot = Part.makeBox(cam_od / 2 + 4.0 - (cam_id / 2 - 2.0), 10.0,
                     (_arm_z1 + 1.0) - (_arm_z0 - RAMP_RETRACT - 1.0),
                     V(cam_id / 2 - 2.0, -5.0, _arm_z0 - RAMP_RETRACT - 1.0))
_slot.rotate(O, ZA, wdeg(0.0))
cam = cam.cut(_slot)
slot_vs_groove = (z_tip0 - groove_r) - (_arm_z1 + 1.0)


def press_at(psi, ramp_shape, plunger_local=None):
    """Depth (mm) the ramp reaches into the free plunger of a station at psi."""
    pl = place(valve_plunger, psi, cam_dz(psi))
    c = pl.common(ramp_shape)
    if c.Volume < 1e-6:
        return 0.0
    return c.optimalBoundingBox().ZMax - z_tip_free


print("ramp sweep…", flush=True)
press_rows, press_out, body_ramp, safe_gap = [], 0.0, 99.0, 99.0
first_touch, last_touch, sw_on, sw_off = None, None, None, None
for _i in range(0, 241):
    psi = -60.0 + 0.5 * _i
    d = press_at(psi, ramp_fire)
    if abs(psi) > 30.0 + 1e-6:
        press_out = max(press_out, d)
    if d > 1e-3:
        first_touch = psi if first_touch is None else first_touch
        last_touch = psi
    if d >= SWITCH:
        sw_on = psi if sw_on is None else sw_on
        sw_off = psi
    if _i % 2 == 0:
        press_rows.append((psi, d))
        mvb = place(Part.makeCompound([valve_body, valve_fit, valve_bracket]), psi, cam_dz(psi))
        body_ramp = min(body_ramp, gap(mvb, ramp_fire))
        safe_gap = min(safe_gap, gap(Part.makeCompound([mvb, place(valve_plunger, psi, cam_dz(psi))]), ramp_safe))
press_max = max(d for _, d in press_rows)
press_flat = min(d for p, d in press_rows if abs(p) <= 30.0 - RAMP_RISE)
print("press max %.2f flat %.2f outside %.3f" % (press_max, press_flat, press_out), flush=True)

# ============================================================ star feed (feed_bench as library)
print("load feed_bench (star)…", flush=True)
_fb = {"REPO": REPO, "FEED_BENCH_LIBRARY": True, "PELLET_D": PELLET_D}
_fb_ok = False
try:
    exec(open(os.path.join(REPO, "gatling", "feed_bench.py")).read(), _fb)
except SystemExit as _e:
    _fb_ok = (_e.code in (0, None))
FB_CHECKS = [(t, ok) for t, ok in _fb.get("checks", [])]
X_STAR, POCKET_R, R_BALL, STAR_R = _fb["X_STAR"], _fb["POCKET_R"], _fb["R_BALL"], _fb["STAR_R"]
STAR_T, STAR_TURNS = _fb["STAR_T"], _fb["STAR_TURNS"]
GUARD_R_IN, GUARD_R_OUT, GUARD_HZ = _fb["GUARD_R_IN"], _fb["GUARD_R_OUT"], _fb["GUARD_HZ"]
GUARD_PHI0 = _fb["GUARD_PHI0"]
Z_BALL_CLOSED = _fb["Z_BALL"]
Z_BALL_OPEN = Z_BALL_CLOSED - BENCH_STROKE
SPEED_RATIO = _fb["SPEED_RATIO"]


def to_pack(s):
    """Bench frame -> this model: the bench turns the other way (mirror y), ball at the open breech."""
    m = s.mirror(O, V(0, 1, 0))
    m.translate(V(0, 0, -BENCH_STROKE))
    return m


def star_at(d):
    """Star when the station nearest the top is at pack angle 180 + d."""
    return to_pack(_fb["star_turn"](_fb["star"], STAR_TURNS * d))


feed_head = to_pack(_fb["feed_head"])
feed_lip = to_pack(_fb["lip"])
feed_cup = to_pack(_fb["cup"])
star0 = star_at(0.0)
_handoff_err = (to_pack(Part.Vertex(_fb["pocket_center"](180.0))).Point
                - polar(R_BALL, 180.0, Z_BALL_OPEN)).Length


def ball_z(phi):
    return Z_BALL_CLOSED + cam_dz(phi)


def ball_at(phi):
    return Part.makeSphere(PELLET_D / 2.0, polar(R_BALL, phi, ball_z(phi)))


# --- guard: follows the ball on the close ramp, inside the breech clamp's feed notch
Z_GUARD_MAX = barrel_clamp.BoundBox.ZMax - 10.5
GUARD_END = 240.0
while GUARD_END < 330.0 and ball_z(GUARD_END) < z_stop + 2.0:
    GUARD_END += 0.25
_w = []
_p = GUARD_PHI0
while _p < GUARD_END - 1e-6:
    _q = min(_p + 2.0, GUARD_END)
    _zc = ball_z(0.5 * (_p + _q))
    _z0, _z1 = _zc - GUARD_HZ, min(_zc + GUARD_HZ, Z_GUARD_MAX)
    if _z1 > _z0 + 1.0:
        w = Part.makeCylinder(GUARD_R_OUT, _z1 - _z0, V(0, 0, _z0), ZA, _q - _p + 0.05)
        w = w.cut(Part.makeCylinder(GUARD_R_IN, _z1 - _z0 + 2, V(0, 0, _z0 - 1)))
        w.rotate(O, ZA, wdeg(_p))
        _w.append(w)
    _p = _q
feed_guard = G.fuse_all(_w)
guard_ball = 99.0
_p = GUARD_PHI0
while _p <= GUARD_END:
    guard_ball = min(guard_ball, gap(ball_at(_p), feed_guard))
    _p += 2.0

# ============================================================ star drive: breech rim + fixed train
GEAR_M, GEAR_FACE, GEAR_BACKLASH = 1.5, 8.0, 0.3
Z_RIM, Z_A, Z_B, Z_I, Z_S = 120, 40, 18, 18, 27
R_RIM, R_A, R_B, R_I, R_S = [GEAR_M * z / 2.0 for z in (Z_RIM, Z_A, Z_B, Z_I, Z_S)]
TRAIN_RATIO = -(R_RIM / R_A) * (R_B / R_S)          # star turns per pack turn (sign: 3 external meshes)
P1_Z0 = barrel_clamp.BoundBox.ZMax + 0.6
P1_Z1 = P1_Z0 + GEAR_FACE
P2_Z0 = P1_Z1 + 2.0
P2_Z1 = P2_Z0 + GEAR_FACE
L_ANG = -20.0                     # layshaft toward the crank side; the guard is on +Y
L_C = V((R_RIM + R_A) * math.cos(math.radians(L_ANG)), (R_RIM + R_A) * math.sin(math.radians(L_ANG)), 0)
S_C = V(X_STAR, 0, 0)
_dls = (S_C - L_C).Length
_a = ((R_B + R_I) ** 2 - (R_I + R_S) ** 2 + _dls ** 2) / (2 * _dls)
_h = math.sqrt(max(0.0, (R_B + R_I) ** 2 - _a ** 2))
_u = (S_C - L_C) * (1.0 / _dls)
_c1 = L_C + _u * _a + V(-_u.y, _u.x, 0) * _h
_c2 = L_C + _u * _a - V(-_u.y, _u.x, 0) * _h
I_C = _c1 if _c1.Length > _c2.Length else _c2


def spur(z, phase, centre, z0, bore):
    pts = [V(x, y, 0) for x, y in GR.tooth_outline(z, GEAR_M, 1.0, GEAR_BACKLASH)]
    pts.append(pts[0])
    g = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, GEAR_FACE))
    g = g.cut(Part.makeCylinder(bore / 2.0, GEAR_FACE + 4, V(0, 0, -2)))
    g.rotate(O, ZA, phase)
    g.translate(V(centre.x, centre.y, z0))
    return g


def follow_phase(c_d, z_d, ph_d, c_f, z_f):
    """Phase of a follower gear so a gap of it meets the driver's nearest tooth."""
    u = math.degrees(math.atan2(c_f.y - c_d.y, c_f.x - c_d.x))
    pitch = 360.0 / z_d
    e = ((u - ph_d + pitch / 2.0) % pitch) - pitch / 2.0
    return u + 180.0 + 180.0 / z_f + e * z_d / z_f


PH_RIM = 0.0
PH_A = follow_phase(O, Z_RIM, PH_RIM, L_C, Z_A)
PH_B = 0.0
PH_I = follow_phase(L_C, Z_B, PH_B, I_C, Z_I)
PH_S = follow_phase(I_C, Z_I, PH_I, S_C, Z_S)
rim_gear = spur(Z_RIM, PH_RIM, O, P1_Z0, 2 * 30.0)
for k in range(N):
    c = polar(R_PACK, k * 60.0)
    rim_gear = rim_gear.cut(Part.makeCylinder(BARREL_OD / 2 + 0.35, 20, V(c.x, c.y, P1_Z0 - 5)))
    for x, y in rail_centers():
        rc = place(Part.Vertex(V(x, y, 0)), k * 60.0).Point
        rim_gear = rim_gear.cut(Part.makeCylinder(RAIL_HOLE / 2, 20, V(rc.x, rc.y, P1_Z0 - 5)))
rim_gear = rim_gear.removeSplitter()
SHAFT_D = 8.0
gear_a = spur(Z_A, PH_A, L_C, P1_Z0, SHAFT_D + 0.2)
gear_b = spur(Z_B, PH_B, L_C, P2_Z0, SHAFT_D + 0.2)
gear_i = spur(Z_I, PH_I, I_C, P2_Z0, 6.2)
gear_s = spur(Z_S, PH_S, S_C, P2_Z0, SHAFT_D + 0.2)
# Gearbox: rear plate behind the rim, front plate ahead of the second plane, outer wall;
# open toward the rim, which turns inside it.
BOX_R0, BOX_R1 = 93.0, max(L_C.Length + R_A, I_C.Length + R_I) + GEAR_M + 4.0
BOX_A0, BOX_A1 = -45.0, 16.0
BOX_Z0, BOX_Z1 = P1_Z0 - 10.5, P2_Z1 + 5.5
_sec = Part.makeCylinder(BOX_R1 + 2.5, BOX_Z1 - BOX_Z0, V(0, 0, BOX_Z0), ZA, BOX_A1 - BOX_A0)
_sec = _sec.cut(Part.makeCylinder(BOX_R0, BOX_Z1 - BOX_Z0 + 2, V(0, 0, BOX_Z0 - 1)))
_sec.rotate(O, ZA, BOX_A0)
_cav = Part.makeCylinder(BOX_R1, P2_Z1 + 1.5 - (P1_Z0 - 1.0), V(0, 0, P1_Z0 - 1.0), ZA, BOX_A1 - BOX_A0 - 4.0)
_cav = _cav.cut(Part.makeCylinder(60.0, 200, V(0, 0, P1_Z0 - 50)))
_cav.rotate(O, ZA, BOX_A0 + 2.0)
_cav = _cav.fuse(Part.makeCylinder(BOX_R0 + 1.0, P2_Z1 + 1.5 - (P1_Z0 - 1.0), V(0, 0, P1_Z0 - 1.0)))
gearbox = _sec.cut(_cav)
for c, d in ((L_C, SHAFT_D), (I_C, 6.0), (S_C, SHAFT_D)):
    gearbox = gearbox.cut(Part.makeCylinder(d / 2 + 0.2, 200, V(c.x, c.y, BOX_Z0 - 50)))
gearbox = gearbox.removeSplitter()
z_star0 = Z_BALL_OPEN - STAR_T / 2.0
star_shaft = Part.makeCylinder(SHAFT_D / 2, BOX_Z1 + 1.0 - (z_star0 - 2.0), V(S_C.x, S_C.y, z_star0 - 2.0))
lay_shaft = Part.makeCylinder(SHAFT_D / 2, BOX_Z1 + 1.0 - (BOX_Z0 - 1.0), V(L_C.x, L_C.y, BOX_Z0 - 1.0))
idl_shaft = Part.makeCylinder(3.0, BOX_Z1 + 1.0 - (P2_Z0 - 4.0), V(I_C.x, I_C.y, P2_Z0 - 4.0))
train_parts = [("gear A (meshes the rim)", gear_a), ("gear B", gear_b), ("idler", gear_i),
               ("star gear", gear_s), ("star shaft", star_shaft), ("layshaft", lay_shaft),
               ("idler shaft", idl_shaft), ("gearbox", gearbox)]


def train_pose(alpha):
    """Rim turned by alpha (deg, = pack turn); every gear turned by its ratio."""
    wa = -Z_RIM / float(Z_A)
    wi = -wa * Z_B / float(Z_I)
    ws = -wi * Z_I / float(Z_S)
    return (rot(rim_gear, alpha), rot(gear_a, wa * alpha, L_C), rot(gear_b, wa * alpha, L_C),
            rot(gear_i, wi * alpha, I_C), rot(gear_s, ws * alpha, S_C))


mesh_worst = 0.0
for _al in (0.0, 0.6, 1.2, 1.8, 2.4):
    r_, a_, b_, i_, s_ = train_pose(_al)
    mesh_worst = max(mesh_worst, r_.common(a_).Volume, b_.common(i_).Volume, i_.common(s_).Volume)
_wa = -Z_RIM / float(Z_A)
train_star_turns = (-(-_wa * Z_B / float(Z_I)) * Z_I / float(Z_S))
centre_err = max(abs(L_C.Length - (R_RIM + R_A)), abs((I_C - L_C).Length - (R_B + R_I)),
                 abs((S_C - I_C).Length - (R_I + R_S)))

# ============================================================ frame: liner + rings + spars
SPAR_R = 4.0
RING_T = 6.0
RING_WALL = 4.0
r_case_od = cam_od / 2.0
r_case_id = r_case_od - RING_WALL
z_tip_b = z_stop + BARREL_SHOW
z_front0 = z_tip_b - PLATE_T + PLATE_LIP
z_front1 = z_tip_b + PLATE_LIP
Z_FRING0, Z_FRING1 = z_stop - PLATE_T * 0.35, z_stop - PLATE_T * 0.35 + PLATE_T   # front frame ring (breech)
_fol_zmax = follower.BoundBox.ZMax
z_spar0 = z_cam1                       # spars start on the liner's front face
z_case1 = Z_FRING0 + 18.0
r_plate = R_PACK + BARREL_OD / 2 + PLATE_RIM


def barrel_plate(z0, z1, od_r):
    disc = Part.makeCylinder(od_r, z1 - z0, V(0, 0, z0))
    for k in range(N):
        c = polar(R_PACK, k * 60.0)
        disc = disc.cut(Part.makeCylinder(BARREL_OD / 2 + 0.35, (z1 - z0) + 4.0, V(c.x, c.y, z0 - 2.0)))
    disc = disc.cut(Part.makeCylinder(max(6.0, R_PACK - BARREL_OD / 2 - 4.0), (z1 - z0) + 4.0, V(0, 0, z0 - 2.0)))
    return disc.removeSplitter()


front_plate = barrel_plate(z_front0, z_front1, r_plate)
SPAR_ANGLES = [w for w in (30.0, 90.0, 150.0, 210.0, 270.0, 330.0)
               if abs(((w + 180.0) % 360.0) - 180.0) > 35.0]       # none under the feed (world 0)
_fr = [tube(2 * r_case_od, 2 * r_case_id, z_cam0 - RING_T, z_cam0),
       tube(2 * r_case_od, 2 * r_case_id, Z_FRING0, Z_FRING1)]
_spar_rc = r_case_od - SPAR_R - 1.0
for w in SPAR_ANGLES:
    a = math.radians(w)
    _fr.append(Part.makeCylinder(SPAR_R, z_case1 - z_spar0,
                                 V(_spar_rc * math.cos(a), _spar_rc * math.sin(a), z_spar0)))
pack_frame = G.fuse_all(_fr)
# The feed head bears on the front ring, the star shaft runs through it.
pack_frame = pack_frame.cut(feed_head).cut(Part.makeCylinder(SHAFT_D / 2 + 0.3, 400, V(S_C.x, S_C.y, -100)))
# Struts from the front ring to the gearbox.
for w in (BOX_A0 + 6.0, BOX_A1 - 3.0):
    a = math.radians(w)
    pack_frame = pack_frame.fuse(Part.makeCylinder(SPAR_R, BOX_Z0 + 1.0 - (Z_FRING1 - 1.0),
                                                   V(_spar_rc * math.cos(a), _spar_rc * math.sin(a), Z_FRING1 - 1.0)))
breech_casing = pack_frame
full_shell_vol = tube(2.0 * r_case_od, 2.0 * r_case_id, z_cam0 - RING_T, z_case1).Volume
frame_ok = pack_frame.Volume < 0.55 * full_shell_vol

# ============================================================ air: hollow axle, bearings, MQR
BRG_OD, BRG_BORE, BRG_T = 52.0, 40.0, 7.0      # 6808, on a 1 mm shim over the Ø38 tube
BRG_NAME = "6808 (40 x 52 x 7) on a 1 mm shim"
DISK_T = 10.0
MQR_D, MQR_ROTOR_L, MQR_STATOR_L, MQR_SPIGOT = 46.0, 15.0, 72.0, 3.0
MQR_PORT_Z = 7.0                # rotor ports from the rotor face
SOFT_OD, SOFT_L, SOFT_GAP = 56.0, 24.0, 4.0
BUFFER_OD, BUFFER_L = 80.0, 150.0
BUFFER_VOL_L = (math.pi * (BUFFER_OD / 2) ** 2 * BUFFER_L) / 1.0e6
_rot_min = min(Part.makeCompound(list(station(p))).BoundBox.ZMin for p in (0.0, 180.0))
z_brg_f1 = min(_rot_min, z_cam0 - RING_T) - 1.0
z_brg_f0 = z_brg_f1 - DISK_T
BRG_SPACING = 57.0
z_brg_r1 = z_brg_f1 - BRG_SPACING
z_brg_r0 = z_brg_r1 - DISK_T
z_axle1 = Z_AXLE_WIN + 12.0
z_axle0 = z_brg_r0 - 24.0
z_axle_exit = z_axle0 + 15.0          # lines leave the axle between the coupling and the rear bearing
z_soft1 = z_axle0 + 10.0
z_soft0 = z_soft1 - SOFT_L
z_rotor1 = z_soft0 - SOFT_GAP
z_rotor0 = z_rotor1 - MQR_ROTOR_L
z_stator1 = z_rotor0
z_stator0 = z_stator1 - MQR_STATOR_L
z_mqr_plate1 = z_stator0 - MQR_SPIGOT
z_mqr_plate0 = z_mqr_plate1 - 6.0


def bearing_disk(z_a, z_b, r_frame):
    race = tube(BRG_OD, BRG_BORE + 0.3, z_a + (DISK_T - BRG_T) / 2, z_b - (DISK_T - BRG_T) / 2)
    hub = tube(BRG_OD + 12.0, BRG_OD - 0.2, z_a, z_b)
    rim = tube(2.0 * r_frame, 2.0 * (r_frame - 5.0), z_a, z_b)
    parts = [race, hub, rim]
    for w in SPAR_ANGLES:
        a = math.radians(w)
        r0 = BRG_OD / 2 + 4.0
        parts.append(Part.makeCylinder(4.0, max(8.0, r_frame - 5.0 - r0),
                                       V(r0 * math.cos(a), r0 * math.sin(a), 0.5 * (z_a + z_b)),
                                       V(math.cos(a), math.sin(a), 0)))
    return G.fuse_all(parts)


brg_f = bearing_disk(z_brg_f0, z_brg_f1, r_case_od)
brg_r = bearing_disk(z_brg_r0, z_brg_r1, r_case_od)
# Rear spars: rear frame ring -> both bearing disks (outside the valves' sweep).
for w in SPAR_ANGLES:
    a = math.radians(w)
    brg_r = brg_r.fuse(Part.makeCylinder(SPAR_R, (z_cam0 - RING_T) - z_brg_r0,
                                         V(_spar_rc * math.cos(a), _spar_rc * math.sin(a), z_brg_r0)))
pack_axle = tube(AXLE_OD, AXLE_ID, z_axle0, z_axle1)
for k in range(N):
    for zw in (Z_AXLE_WIN - 5.0, z_axle_exit - 5.0):
        w = Part.makeCylinder(HOSE_OD / 2 + 0.5, 10.0, polar(AXLE_OD / 2 - 3.0, k * 60.0, zw), polar(1.0, k * 60.0))
        pack_axle = pack_axle.cut(w)
rear_disk = Part.makeCylinder(REAR_DISK_R, REAR_DISK_Z1 - REAR_DISK_Z0, V(0, 0, REAR_DISK_Z0))
rear_disk = rear_disk.cut(Part.makeCylinder(AXLE_OD / 2 + 0.2, 30, V(0, 0, REAR_DISK_Z0 - 5)))
for k in range(N):
    for x, y in rail_centers():
        rc = place(Part.Vertex(V(x, y, 0)), k * 60.0).Point
        rear_disk = rear_disk.cut(Part.makeCylinder(RAIL_HOLE / 2, 30, V(rc.x, rc.y, REAR_DISK_Z0 - 5)))
    # slot between the station's rails for its line R (it crosses the disk when open)
    _sl = Part.makeBox(9.0, 34.0, 30.0, V(-4.5, -R_PACK + 18.0, REAR_DISK_Z0 - 5))
    rear_disk = rear_disk.cut(place(_sl, k * 60.0))
rear_disk = rear_disk.removeSplitter()
soft_coup = tube(SOFT_OD, AXLE_OD + 0.2, z_soft1 - 10.0, z_soft1).fuse(
    tube(SOFT_OD * 0.7, 6.5, z_soft0, z_soft0 + 10.0)).fuse(
    Part.makeCylinder(SOFT_OD * 0.35, SOFT_GAP + 0.01, V(0, 0, z_soft0 + 10.0))).removeSplitter()
mqr_rotor = tube(MQR_D, 6.0, z_rotor0, z_rotor1)
mqr_stator = tube(MQR_D, 6.0, z_stator0, z_stator1).fuse(Part.makeCylinder(10.0, MQR_SPIGOT, V(0, 0, z_stator0 - MQR_SPIGOT)))
mqr_plate = Part.makeCylinder(32.0, 6.0, V(0, 0, z_mqr_plate0))
# Lines inside the axle and out to the rotor ports (all of it turns with the pack).
_inner = []
for k in range(N):
    p_in = polar(R_BUNDLE, k * 60.0, Z_AXLE_WIN - 10.0)
    p_out = polar(R_BUNDLE, k * 60.0, z_axle_exit + 4.0)
    p_ex = polar(SOFT_OD / 2 + HOSE_OD / 2 + 1.0, k * 60.0, z_axle_exit)
    p_port = polar(MQR_D / 2 + 6.0, k * 60.0, z_rotor1 - MQR_PORT_Z)
    _inner += [tube_path([p_in, p_out, p_ex, V(p_ex.x, p_ex.y, p_port.z + 4.0), p_port], HOSE_OD / 2)]
lines_inner = Part.makeCompound(_inner)
BUNDLE_R = R_BUNDLE + HOSE_OD / 2
buf_y = -(r_case_od + BUFFER_OD / 2 + 8.0)
air_buffer = tube(BUFFER_OD, BUFFER_OD - 4.0, z_mqr_plate0, z_mqr_plate0 + BUFFER_L, 0.0, buf_y)
deadman = Part.makeCylinder(12.0, 28.0, V(0, buf_y + BUFFER_OD / 2 + 8.0, z_mqr_plate0 + 18.0), V(0, -1, 0)).fuse(
    Part.makeBox(6.0, 8.0, 22.0, V(-3.0, buf_y + BUFFER_OD / 2 - 14.0, z_mqr_plate0 + 28.0))).removeSplitter()
_p_buf = V(0, buf_y + BUFFER_OD / 2, z_stator0 + 20.0)
_p_in = V(0, -(MQR_D / 2 + 10.0), z_stator0 + 20.0)
air_supply = Part.makeCylinder(4.0, _p_buf.distanceToPoint(_p_in), _p_in, _p_buf.sub(_p_in))

# ============================================================ crank, carry, strap
z_crank = 0.5 * (z_cam0 + z_stop)
_y0 = -(r_case_od - 2.0)
crank = Part.makeCylinder(12.0, 18.0, V(0, _y0, z_crank), V(0, -1, 0)).fuse(
    Part.makeBox(10.0, 55.0, 10.0, V(-5.0, _y0 - 16.0 - 55.0, z_crank - 5.0))).fuse(
    Part.makeSphere(14.0, V(0.0, _y0 - 16.0 - 55.0, z_crank))).removeSplitter()
z_cg = 0.5 * (z_cam0 + z_front1)
z_carry = max(z_cg, BOX_Z1 + 50.0)
x_handle = r_case_od + 22.0
carry_handle = Part.makeBox(12.0, 18.0, 90.0, V(x_handle - 6.0, -9.0, z_carry - 45.0)).fuse(
    Part.makeCylinder(9.0, 70.0, V(x_handle + 18.0, 0, z_carry - 35.0))).removeSplitter()
_sf = Part.makeTorus(18.0, 3.0)
_sf.translate(V(x_handle, 0, z_front0 + 10.0))
_sr = Part.makeTorus(18.0, 3.0)
_sr.translate(V(x_handle, 0, z_cam0 - RING_T - 12.0))
sling = _sf.fuse(_sr)

# ============================================================ fast checks (the full turn: breech_mechanism_sweep.py)
# Fingers vs frame: only the finger tip reaches past the spars' inner radius,
# and it stays behind the liner's front face, where the spars start.
_fp = follower.tessellate(0.3)[0]
_fol_r = [(math.hypot(q.x, R_PACK + q.y), q.z) for q in _fp]
_fol_z_out = max([z for r, z in _fol_r if r > _spar_rc - SPAR_R - CLEAR] or [-1e9])
fingers_vs_spars = z_spar0 - _fol_z_out
# Rear disk vs the parts that slide past it, every 5 deg of phase. The disk turns
# with the pack, so a station keeps its angle to it (station 0 at 0) and only
# its stroke changes with the phase.
rear_disk_gap = 99.0
for _i in range(72):
    p = _i * 5.0
    rear_disk_gap = min(rear_disk_gap, gap(place(Part.makeCompound(qev_slide + [valve_group]), 0.0, cam_dz(p)), rear_disk),
                        gap(place(line_r(cam_dz(p)), 0.0), rear_disk))
rot_all = Part.makeCompound([s for k in range(N) for s in station(k * 60.0)])
r_rot_max = r_max(Part.makeCompound([place(Part.makeCompound(qev_slide + [valve_group]), k * 60.0, cam_dz(k * 60.0))
                                     for k in range(N)] + [place(fixed0, k * 60.0) for k in range(N)]
                                    + [place(line_r(cam_dz(k * 60.0)), k * 60.0) for k in range(N)]))
liner_clear = cam_id / 2.0 - r_rot_max
spar_clear = (_spar_rc - SPAR_R) - r_rot_max
aft_clear = brg_f.BoundBox.ZMax - _rot_min          # >0 would be overlap; we want negative
aft_gap = _rot_min - brg_f.BoundBox.ZMax
lines_fixed = min(gap(lines_inner, s) for s in (brg_f, brg_r, mqr_stator, air_buffer, deadman, air_supply, mqr_plate))
bundle_fit = (AXLE_ID / 2.0) - BUNDLE_R
bearings_on_axle = (gap(pack_axle, brg_f) < 1.5 and gap(pack_axle, brg_r) < 1.5
                    and brg_f.BoundBox.ZMin > z_axle0 and brg_r.BoundBox.ZMin > z_axle0)
mqr_free = gap(pack_axle, mqr_rotor) > 1.0 and gap(pack_axle, mqr_stator) > 1.0
rim_vs_closed = min(gap(rim_gear, place(Part.makeCompound(qev_slide), k * 60.0)) for k in range(N))
star_top = star_vs_stations = min(gap(star0, s) for s in stations)
print("fast checks done", flush=True)

# ============================================================ assembly / checks / report
pack = Part.makeCompound(stations)
assembly = Part.makeCompound([
    pack, cam, front_plate, pack_frame, rear_disk, rim_gear, gear_a, gear_b, gear_i, gear_s,
    star_shaft, lay_shaft, idl_shaft, gearbox, star0, feed_head, feed_lip, feed_cup, feed_guard,
    ramp_fire, crank, carry_handle, sling, pack_axle, brg_f, brg_r, soft_coup, mqr_rotor, mqr_stator,
    mqr_plate, lines_inner, air_buffer, deadman, air_supply,
])
bb = assembly.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
case_od = 2.0 * r_case_od
closed_L = (z_stop + BARREL_SHOW) - Z_AFT_CLIP
fb_n_ok = sum(1 for _, ok in FB_CHECKS if ok)

checks = [
    ("bench stroke %.1f mm" % BENCH_STROKE, abs(BENCH_STROKE - 65.8) < 0.05),
    ("finger on the groove closed and open", follower_on_track(0.0) and follower_on_track(180.0)),
    ("liner groove blind: %.1f mm behind its bottom, liner Ø%.0f" % (GROOVE_FLOOR, cam_od),
     cam_od / 2.0 - (CAM_R + groove_r) >= GROOVE_FLOOR - 1e-6),
    ("rotating parts inside the liner (all but fingers) %.2f >= %.2f" % (liner_clear, CLEAR), liner_clear >= CLEAR),
    ("frame spars clear of fingers (start %.2f ahead of them) and stations (%.2f)" % (fingers_vs_spars, spar_clear),
     fingers_vs_spars >= CLEAR and spar_clear >= CLEAR),
    ("moving-part neighbour gap %.2f >= %.2f (QEV + guides, six phases)" % (gap_core, CLEAR), gap_core >= CLEAR - 1e-6),
    ("hub: whole stations incl. AirTAC and lines, six phases %.2f >= %.2f" % (gap_nbr, CLEAR), gap_nbr >= CLEAR - 1e-6),
    ("AirTAC group and line R clear of own station (%.2f)" % gap_own, gap_own >= CLEAR - 1e-6),
    ("rails: carriage and nose ride the Al tubes (plain bores, %.2f mm3)" % (
        rails_pack.common(qev_closed["Carriage"]).Volume + rails_pack.common(qev_closed["Nose_clamp"]).Volume),
     rails_pack.common(qev_closed["Carriage"]).Volume + rails_pack.common(qev_closed["Nose_clamp"]).Volume < 0.01),
    ("rails end in the rear disk; disk clear of moving parts and lines (%.2f)" % rear_disk_gap,
     abs(rails_pack.BoundBox.ZMin - REAR_DISK_Z0) < 0.05 and rear_disk_gap >= CLEAR),
    ("ramp presses only on 330..30 (outside %.3f mm)" % press_out, press_out < 0.01),
    ("ramp touches %.1f..%.1f, switch (>= %.1f) %.1f..%.1f deg" % (
        first_touch % 360.0, last_touch, SWITCH, sw_on % 360.0, sw_off),
     first_touch >= -30.0 and last_touch <= 30.0 and sw_on is not None),
    ("plunger stroke: full press %.2f, max %.2f (%.1f + %.1f gap)" % (press_flat, press_max, RAMP_PRESS, RAMP_GAP),
     abs(press_flat - RAMP_PRESS) < 0.05 and press_max <= RAMP_PRESS + 0.05),
    ("valve body clear of the ramp at FIRE (%.2f: plunger sticks out %.1f, press %.1f)" % (body_ramp, PL_L, RAMP_PRESS),
     body_ramp >= PL_L - RAMP_PRESS - 0.05),
    ("trigger released: plungers and bodies clear by %.2f" % safe_gap, safe_gap >= 1.0),
    ("trigger arm slot clear of the groove (%.1f mm)" % slot_vs_groove, slot_vs_groove >= 2.0),
    ("feed bench as library: %d of %d [OK]" % (fb_n_ok, len(FB_CHECKS)), _fb_ok and fb_n_ok == len(FB_CHECKS)),
    ("handoff at 180 (LOAD): pocket on the ball seat %.2f mm, speed %.3f" % (_handoff_err, SPEED_RATIO),
     _handoff_err < 0.3 and LOAD_A <= 180.0 <= LOAD_B and abs(SPEED_RATIO - 1.0) <= 0.02),
    ("star vs whole stations, six phases (%.2f)" % star_top, star_top >= CLEAR),
    ("guard %.1f..%.1f deg: ball gap %.2f (1..2)" % (GUARD_PHI0, GUARD_END, guard_ball), 1.0 <= guard_ball <= 2.0),
    ("star drive %d -> %d | %d -> %d -> %d (m%.1f): star %.3f turns per pack turn"
     % (Z_RIM, Z_A, Z_B, Z_I, Z_S, GEAR_M, train_star_turns), abs(train_star_turns + STAR_TURNS) < 1e-9),
    ("train centres on pitch sums (%.3f) and meshes without overlap (%.2f mm3)" % (centre_err, mesh_worst),
     centre_err < 1e-6 and mesh_worst < 1.0),
    ("rim (rear barrel-plate) clear of the closed QEVs (%.2f)" % rim_vs_closed, rim_vs_closed >= CLEAR),
    ("air: lines inside the axle, ID %.1f vs bundle Ø%.0f; no line crosses a fixed part (%.2f)"
     % (AXLE_ID, 2 * BUNDLE_R, lines_fixed), bundle_fit >= 1.0 and lines_fixed >= CLEAR),
    ("air: axle Ø%.0f on two %s, MQR off the axle" % (AXLE_OD, BRG_NAME.split(" ")[0]), bearings_on_axle and mqr_free),
    ("valves' sweep ahead of the front bearing disk (%.2f)" % aft_gap, aft_gap >= CLEAR),
    ("buffer %.2f L in 0.5–1 L" % BUFFER_VOL_L, 0.5 <= BUFFER_VOL_L <= 1.0 + 1e-6),
    ("carry handle on top, crank on the side", carry_handle.BoundBox.Center.x > 0.0
     and abs(crank.BoundBox.Center.y) > abs(crank.BoundBox.Center.x)),
    ("open frame (not full casing)", frame_ok),
    ("six phases", len(stations) == 6),
    ("closed station L %.1f ≈ 750" % closed_L, abs(closed_L - TARGET_L) <= 0.6),
    ("no full-length tube", z_case1 < z_tip_b - 200.0),
]
report = [
    NAME,
    "  sketch                 : full mechanism sketch (stages 4+5+6+7; NOT frozen)",
    "  stroke (bench)         : %.1f mm" % BENCH_STROKE,
    "  law                    : FIRE 330–30; OPEN 30–120; LOAD 120–240; CLOSE 240–330",
    "  pack R                 : %.2f (pinned = breech_pack; rail feet floor 66.3)" % R_PACK,
    "  cam                    : liner Ø%.0f (groove R %.0f, blind, %.0f mm floor); it is the frame here"
    % (cam_od, CAM_R, GROOVE_FLOOR),
    "  rails                  : carriage + nose ride the Al tubes; rear disk R %.0f at z %.0f..%.0f"
    % (REAR_DISK_R, REAR_DISK_Z0, REAR_DISK_Z1),
    "  hub                    : closed — AirTAC on each carriage (bracket on the 30° ear), body r %.1f..%.1f;"
    " station gap with valves %.2f mm" % (R_PACK + VALVE_Y - A_W / 2, R_PACK + VALVE_Y + A_W / 2, gap_nbr),
    "  line A                 : rigid, %.0f mm of 6x4 tube (%.2f cm3; pilot pocket %.2f cm3)"
    % (LINE_A_L, LINE_A_V, pocket_v),
    "  line R                 : flexes %.1f with the carriage, into the hollow axle at z %.0f"
    % (BENCH_STROKE, Z_AXLE_WIN),
    "  firing ramp            : r %.1f, low z %.1f; touch %.1f..%.1f, switch %.1f..%.1f, full %.0f..%.0f deg;"
    " press %.2f" % (R_TIP, z_ramp_low, first_touch % 360, last_touch, sw_on % 360, sw_off,
                     (-(30 - RAMP_RISE)) % 360, 30 - RAMP_RISE, press_flat),
    "  trigger                : finger under the pack pulls the ramp forward; spring back %.0f mm = safe"
    % RAMP_RETRACT,
    "  feed                   : feed_bench star (3 pockets, 2:1) at the top; handoff 180°;"
    " guard %.0f–%.0f° following the close" % (GUARD_PHI0, GUARD_END),
    "  star drive             : rim %d on the breech clamps (z %.1f..%.1f) -> %d | %d -> %d -> %d;"
    " layshaft R %.0f at %.0f°" % (Z_RIM, P1_Z0, P1_Z1, Z_A, Z_B, Z_I, Z_S, L_C.Length, L_ANG),
    "  frame envelope Ø       : %.0f (liner); was %.0f" % (case_od, CASE_OD_START),
    "  air                    : axle Al %.0f x %.1f, %s; 6 lines 1/8\" inside; MQR rotor z %.0f..%.0f"
    % (AXLE_OD, (AXLE_OD - AXLE_ID) / 2.0, BRG_NAME, z_rotor0, z_rotor1),
    "  air buffer             : Ø%.0f×%.0f ≈ %.2f L; dead-man on inlet" % (BUFFER_OD, BUFFER_L, BUFFER_VOL_L),
    "  crank                  : side hub on the frame (−Y)",
    "  carry                  : handle on top ahead of the gearbox; strap loops front/aft",
]
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  overall LxWxH         : %.0f x %.0f x %.0f mm (was %.0f long)" % (gun_L, gun_W, gun_H, L_START),
    "  not drawn             : ramp guide pins + spring + trigger pivot, valve bracket bolts,"
    " 1→6 manifold on the stator, crank drive to the pack, wheeled carriage, freeze",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
report.append("  full turn             : breech_mechanism_sweep.py (separate run)")
print("\n".join(report))

FV.STYLES["ph0"] = ((0.92, 0.40, 0.16), 32)
FV.STYLES["ph1"] = ((0.85, 0.55, 0.30), 40)
FV.STYLES["ph2"] = ((0.55, 0.65, 0.55), 45)
FV.STYLES["ph3"] = ((0.30, 0.62, 0.75), 38)
FV.STYLES["ph4"] = ((0.60, 0.58, 0.50), 45)
FV.STYLES["ph5"] = ((0.88, 0.48, 0.28), 40)
FV.STYLES["plate"] = ((0.42, 0.44, 0.48), 8)
FV.STYLES["frame"] = ((0.72, 0.68, 0.55), 40)
FV.STYLES["cam"] = ((0.35, 0.38, 0.42), 60)
FV.STYLES["rail"] = ((0.55, 0.58, 0.62), 20)
FV.STYLES["feed"] = ((0.55, 0.50, 0.40), 50)
FV.STYLES["star"] = ((0.95, 0.80, 0.10), 0)
FV.STYLES["gear"] = ((0.20, 0.62, 0.35), 0)
FV.STYLES["ramp"] = ((0.85, 0.12, 0.12), 0)
FV.STYLES["drive"] = ((0.30, 0.32, 0.36), 15)
FV.STYLES["pellet"] = ((0.88, 0.88, 0.92), 15)
FV.STYLES["crank"] = ((0.25, 0.25, 0.28), 10)
FV.STYLES["hose"] = ((0.20, 0.55, 0.45), 35)
FV.STYLES["mqr"] = ((0.45, 0.70, 0.95), 25)
FV.STYLES["brg"] = ((0.35, 0.55, 0.85), 20)
FV.STYLES["buffer"] = ((0.55, 0.60, 0.65), 40)
FV.STYLES["deadman"] = ((0.75, 0.25, 0.20), 15)
FV.STYLES["guard"] = ((0.60, 0.30, 0.75), 40)
FV.STYLES["carry"] = ((0.28, 0.28, 0.30), 15)

if BREECH_MECH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Cam", "Cam_liner", cam, "cam")
sc.add("Fire", "Firing_ramp_and_trigger", ramp_fire, "ramp")
sc.add("Skin", "Front_barrel_plate", front_plate, "plate")
sc.add("Skin", "Pack_frame", pack_frame, "frame")
sc.add("Skin", "Rear_rail_disk", rear_disk, "plate")
sc.add("Feed", "Star", star0, "star")
sc.add("Feed", "Feed_head", feed_head, "feed")
sc.add("Feed", "Lip_TPU", feed_lip, "deadman")
sc.add("Feed", "Cup", feed_cup, "feed")
sc.add("Feed", "Feed_guard", feed_guard, "guard")
sc.add("Feed", "Ball_handoff", ball_at(180.0), "pellet")
sc.add("Feed", "Ball_closing", ball_at(260.0), "pellet")
sc.add("Star_drive", "Rim_gear", rim_gear, "gear")
sc.add("Star_drive", "Gear_A", gear_a, "gear")
sc.add("Star_drive", "Gear_B", gear_b, "gear")
sc.add("Star_drive", "Idler", gear_i, "gear")
sc.add("Star_drive", "Star_gear", gear_s, "gear")
sc.add("Star_drive", "Star_shaft", star_shaft, "drive")
sc.add("Star_drive", "Layshaft", lay_shaft, "drive")
sc.add("Star_drive", "Idler_shaft", idl_shaft, "drive")
sc.add("Star_drive", "Gearbox", gearbox, "frame")
sc.add("Drive", "Crank", crank, "crank")
sc.add("Carry", "Carry_handle", carry_handle, "carry")
sc.add("Carry", "Sling_loops", sling, "carry")
sc.add("Air", "Pack_axle", pack_axle, "drive")
sc.add("Air", "Bearing_front", brg_f, "brg")
sc.add("Air", "Bearing_rear", brg_r, "brg")
sc.add("Air", "Soft_coupling", soft_coup, "drive")
sc.add("Air", "MQR_rotor", mqr_rotor, "mqr")
sc.add("Air", "MQR_stator", mqr_stator, "mqr")
sc.add("Air", "MQR_plate", mqr_plate, "frame")
sc.add("Air", "Lines_in_axle", lines_inner, "hose")
sc.add("Air", "Buffer_tank", air_buffer, "buffer")
sc.add("Air", "Deadman_valve", deadman, "deadman")
sc.add("Air", "Supply_stub", air_supply, "hose")
for n, ang, u, dz, tag in phases:
    p = polar(R_PACK + 70, ang, z_stop + dz)
    sc.label("Labels", "%d° %s" % (ang, tag), (p.x, p.y, p.z))
sc.finish(hidden_groups=("Labels",), opaque_groups=())
doc = sc.doc
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart
mesh_shape = assembly.copy()
mesh_shape.translate(V(0, 0, -mesh_shape.BoundBox.ZMin))
mesh_shape.exportStep(os.path.join(OUT_DIR, "breech_mechanism.step"))
MeshPart.meshFromShape(
    Shape=mesh_shape, LinearDeflection=0.4, AngularDeflection=0.5).write(
    os.path.join(OUT_DIR, "breech_mechanism.stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech mechanism has [FAIL] checks")
