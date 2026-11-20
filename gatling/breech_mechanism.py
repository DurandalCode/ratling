# -*- coding: utf-8 -*-
"""
Gatling breech mechanism (not a freeze).

Stroke from linear_breech (65.8 mm) -> angle->stroke law -> outboard cam liner ->
six phases -> AirTAC on each carriage, fixed firing ramp -> star feed geared
to the pack (rim on the breech clamps + fixed train) with a gate in the neck ->
helical guard -> side crank, carry, strap -> air: hollow axle, bearings, MQR,
hose from the receiver through a dead-man -> flintlock grip with one
two-stage lever (air, then balls) for the left hand.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism.py').read())"

The full-turn clearance sweep (every station part against every fixed part,
every 3 deg; neighbours every 5 deg of phase) is a separate run in parallel
freecadcmd workers, ~4.5 min:

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism_sweep.py').read())"

Pack R / casing may move if parts will not seat. No wheeled carriage; no
full-length tube. Exports: exports/gatling_breech_mechanism/

The model is built in its final pose: hopper and star on +X (top), firing
sector at the bottom (-X), crank on +Y (the shooter's right; it was on -Y
until 2026-11-20). Pack angle phi (0 = FIRE) sits at
world angle phi + 180.

2026-11-20 (owner's choice of the three layouts in docs/gatling.md, plan
questions 2-4):
- The AirTAC rides its carriage on a bracket behind the bridge, plunger aft,
  fittings to the sides. Its line A to the pilot is short and rigid (as on the
  bench); the supply line R flexes with the stroke. The six valves no longer
  meet at the axis (the old hub overlap was 11.3 cm3 per pair at any R).
- A fixed ramp on the firing sector presses the plungers at the closed
  position: touch 332 -> 28 deg, 2.5 mm full press on 340..20. The
  trigger pulls the ramp forward into reach; let go, a spring takes it 4 mm
  aft and no plunger is pressed. The press pushes the QEV onto its stop.
  (Since the controls moved to the rear grip the ramp is fixed: below.)
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
- No buffer tank. The Ø80 x 150 tank (0.75 L) gave ~0.15 L at a 0.2 bar
  droop, under one shot (two chamber volumes of free air, 0.2..0.4 L), so the
  burst was held by the source and hose anyway. A thick hose from the
  receiver comes in on -Y, through the dead-man inline on the supply stub,
  into the MQR stator.

2026-11-20, pack drive from the crank: the crank shaft runs across the
barrels on +Y (the shooter's right) at the middle of the closed QEVs (x 0,
z 75). It is drawn on -Y and mirrored (CRANK_SIDE): the frame is symmetric
and the rim maps onto itself, so the meshes hold. A bevel pair
20:20 m 2 turns it onto a lay shaft parallel to the axle at r 135, outside
the frame (the stations sweep r <= 96.3 there and the frame spar on that side takes
r 100..108); a gear 60 (m 1.5) on that shaft meshes the star-drive rim 120.
One crank turn = 60 / 120 = 0.5 pack turn, so 60 rpm gives 3 shots/s; the
top of the crank goes aft, towards the shooter. The first draft (crank at
z 302 ahead of the clamps, bevel 48:16, pinion 20 at r 105) moved here at the
owner's request; at r 105 the long shaft would cut the spar and front ring.
Shafts Ø8 on 608s: the pair's bracket (two plates) sits on the spar, the
rim-gear boss on the front ring. The bevels use gears.bevel_gear(back_cone=
True) (full-height teeth; the planar form is half height at 45 deg and gave a
16:48 pair 0.2 mm teeth). Tooth counts are a draft until the bench measures
the torque. The crank arm and knob are not drawn; a reference body (knob
orbit R 80, fist R 45 x 100) keeps room for the hand.

2026-11-20, controls at the rear (stage 6; owner: balls and air from one
hand, behind, an old flintlock look). The firing ramp stays in the press
position on a block inside the liner (2 x M3 into heat-set inserts, blind
holes): every station on 330..30 fires while the air is on. A wooden grip
curls down behind a rear plate like a flintlock pistol's, with a brass pommel;
the plate (R 50) also carries the MQR stator, four struts tie it to the rear
bearing disk's rim (the plate used to float). One big lever (a 14 x 24 blade,
91 mm) follows the grip's front like a fire extinguisher's, pivoted at the top
behind the plate, 15 deg to the grip (22 mm at its free end by the pommel).
Stage 1, 0..5 deg: the lever presses the dead-man in the grip through a pusher
with an over-travel spring (3 mm valve stroke at 5 deg, 8 mm over-travel by
15); the pusher is placed by the real contact (its end meets the tilted blade
at its edge first). Stage 2, 5..15 deg: the lever's short tail inside the
grip's root takes up 3 mm of cable slack and then draws the gate pin 6 mm out
of the feed neck (Bowden 654 mm, along the top on the left, through the
plate); let go and a spring puts the pin 5 mm across the Ø25.4 neck. The
receiver's hose comes into the pommel, the valve's outlet runs up the grip and
through the plate into the stator's rear port. The trigger under the liner,
the D-grip with bails and the musket stock drawn earlier the same day are
gone. The gun is 1222 x 330 x 418 (the hose hanging from the pommel sets the
height).
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

# ============================================================ firing ramp (fixed)
# The ramp stays in the press position: the air is switched by the dead-man on the
# grip (left hand, lever stage 1), so every station on 330..30 fires while it is held.
RAMP_GAP, RAMP_PRESS, RAMP_RISE = 1.0, 2.5, 10.0
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
# Flat back on the mount block: 6 thick at the ends, 9.5 on the flat.
z_ramp_back = z_ramp_low - RAMP_DEPTH
_lift = RAMP_GAP + RAMP_PRESS
ramp = _rf.extrude(V(0, 0, -(_lift + RAMP_DEPTH + 1.0))).common(
    Part.makeBox(400, 400, _lift + RAMP_DEPTH + 2.0, V(-200, -200, z_ramp_back)))
ramp_body = ramp.removeSplitter()

# --- mount: a block on the liner's inner wall behind the ramp (2 x M3 into heat-set
# inserts, blind holes); 2 x M3 from its aft face into inserts in the ramp at psi +/-20.
# Only stations closed at FIRE pass it (|psi| <= 30).
MOUNT_PSI, BLK_L = 20.0, 10.0
z_blk1 = z_ramp_back
z_blk0 = z_blk1 - BLK_L
BLK_R0, BLK_HALF = R_TIP - 7.5, MOUNT_PSI + 4.0
BLK_SCREW_PSI = 8.0
INSERT_D, INSERT_DEPTH = 4.0, 5.0                 # M3 heat-set insert holes in the liner wall
_wedge = Part.makeCylinder(cam_id / 2 + 1.0, BLK_L, V(0, 0, z_blk0), ZA, 2.0 * BLK_HALF)
_wedge.rotate(O, ZA, wdeg(-BLK_HALF))
guide_block = tube(cam_id, 2.0 * BLK_R0, z_blk0, z_blk1).common(_wedge)
for _s in (-1, 1):
    _p = polar(R_TIP, _s * MOUNT_PSI)
    guide_block = guide_block.cut(Part.makeCylinder(1.7, BLK_L + 2.0, V(_p.x, _p.y, z_blk0 - 1.0)))
    guide_block = guide_block.cut(Part.makeCylinder(3.0, 3.0, V(_p.x, _p.y, z_blk0 - 1.0)))   # head
_z_blk_mid = 0.5 * (z_blk0 + z_blk1)
insert_holes = []
for _s in (-1, 1):
    _d = polar(1.0, _s * BLK_SCREW_PSI)
    _p0 = polar(BLK_R0 - 0.5, _s * BLK_SCREW_PSI, _z_blk_mid)
    guide_block = guide_block.cut(Part.makeCylinder(1.7, cam_id / 2 - BLK_R0 + 1.0, _p0, _d))
    guide_block = guide_block.cut(Part.makeCylinder(3.0, 3.5, _p0, _d))
    insert_holes.append(Part.makeCylinder(INSERT_D / 2, INSERT_DEPTH + 0.5,
                                          polar(cam_id / 2 - 0.5, _s * BLK_SCREW_PSI, _z_blk_mid), _d))
guide_block = guide_block.removeSplitter()
for _h in insert_holes:
    cam = cam.cut(_h)
ramp_fire = ramp_body
ramp_seated = gap(ramp_body, guide_block)
# Not through the liner: a probe from each insert hole's bottom to the outer face stays in it.
_wall_left = (cam_od - cam_id) / 2.0 - INSERT_DEPTH
insert_blind = True
for _h in insert_holes:
    _ax = _h.BoundBox.Center
    _dir = V(_ax.x, _ax.y, 0)
    _dir.normalize()
    _a, _b = cam_id / 2 + INSERT_DEPTH, cam_od / 2
    _pr = Part.makeCylinder(0.5, _b - _a - 0.1, V(_dir.x * (_a + 0.05), _dir.y * (_a + 0.05), _ax.z), _dir)
    insert_blind = insert_blind and _pr.common(cam).Volume > 0.99 * _pr.Volume
liner_one = len(cam.Solids) == 1
groove_vs_mount = gap(Part.makeCompound(_balls), Part.makeCompound([guide_block] + insert_holes), pad=5.0)


def press_at(psi, ramp_shape, plunger_local=None):
    """Depth (mm) the ramp reaches into the free plunger of a station at psi."""
    pl = place(valve_plunger, psi, cam_dz(psi))
    c = pl.common(ramp_shape)
    if c.Volume < 1e-6:
        return 0.0
    return c.optimalBoundingBox().ZMax - z_tip_free


print("ramp sweep…", flush=True)
press_rows, press_out, body_ramp = [], 0.0, 99.0
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
SUPPLY_HOSE_OD, SUPPLY_HOSE_L = 14.0, 60.0     # end of the thick hose from the receiver (3/8")
DEADMAN_R, DEADMAN_L = 12.0, 28.0
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
# Supply: thick hose from the receiver -> pommel -> dead-man in the grip -> stator's rear port
# (drawn in "controls" below). No buffer tank.
z_supply = z_stator0 + 20.0

# ============================================================ pack drive from the crank
# Crank shaft across the barrels (Y), drawn on -Y and mirrored to CRANK_SIDE, at the middle of the closed QEVs ->
# bevel pair 20:20 m 2 -> lay shaft parallel to the axle, outside the frame (r 135)
# -> gear 60 in the star-drive rim 120 (plane 1). One crank turn = 60 / 120 = 0.5
# pack turn. Along the QEVs the stations sweep r <= 96.3 and the frame spar on
# -Y takes r 100..108, so the shaft runs at r 135: its rim gear is then 60 (not
# a pinion 20, whose shaft at r 105 would cut the spar and the front ring) and
# the pair is 1:1. Tooth counts are a draft; the bench measures the torque.
CP_Z = 60                         # gear in the rim (m GEAR_M)
CB_M, CB_ZS, CB_ZB = 2.0, 20, 20  # bevel pair: lay shaft, crank shaft
CB_FACE, CB_BACKLASH = 9.0, 0.2
CRANK_ANG = -90.0                 # lay shaft as drawn (-Y); the crank axis is world Y
CRANK_SIDE = +1                   # +1: mirrored onto +Y (the shooter's right), -1: as drawn
CBRG_OD, CBRG_W = 22.0, 7.0       # 608
CBOSS_OD = CBRG_OD + 8.0
R_CP = GEAR_M * CP_Z / 2.0
CP_C = V((R_RIM + R_CP) * math.cos(math.radians(CRANK_ANG)),
         (R_RIM + R_CP) * math.sin(math.radians(CRANK_ANG)), 0)
CB_DS = math.degrees(math.atan2(CB_ZS, CB_ZB))             # pitch cone angles, shafts at 90 deg
CB_DB = 90.0 - CB_DS
CB_RS = CB_M * CB_ZS / 2.0
_chamber = qev_closed["Chamber_tube"].BoundBox
Z_CRANK = 0.5 * (_chamber.ZMin + _chamber.ZMax)           # crank axis = cone apex: middle of the closed QEV
APEX = V(CP_C.x, CP_C.y, Z_CRANK)
crank_gear = spur(CP_Z, follow_phase(O, Z_RIM, PH_RIM, CP_C, CP_Z), CP_C, P1_Z0, SHAFT_D + 0.2)

# Local frame: apex at the origin, axes as the world (+Z muzzle, -Y out); the lay
# shaft is the local Z axis, the crank shaft the local Y axis.
# Lay-shaft bevel: body ahead of the apex (+Z), a tooth at local -Y (the mesh side).
# back_cone: full-height teeth (the plain planar form makes them half height at 45 deg).
bevel_small, CB_INFO_S = GR.bevel_gear(CB_M, CB_ZS, CB_FACE, 16.0, 3.0, SHAFT_D + 0.2, CB_BACKLASH,
                                       delta_deg=CB_DS, phase_deg=-90.0, back_cone=True)
# Crank bevel: local +Z -> world -Y (90 deg about X); its gap at local +Y -> world +Z.
bevel_big, CB_INFO_B = GR.bevel_gear(CB_M, CB_ZB, CB_FACE, 24.0, 10.0, SHAFT_D + 0.2, CB_BACKLASH,
                                     delta_deg=CB_DB, phase_deg=90.0 + 180.0 / CB_ZB, back_cone=True)
bevel_big.rotate(O, V(1, 0, 0), 90.0)
bevel_small.translate(APEX)
bevel_big.translate(APEX)


def to_drive(s):
    m = s.copy()
    m.translate(APEX)
    return m


def _rz(zw):
    return zw - Z_CRANK                                   # world z -> local


# Lay shaft: from the bevel's small end to ahead of the rim gear.
_ls0 = CB_INFO_S["small_end_z"] - 1.0
_ls1 = _rz(P1_Z1 + 2.0)
pin_shaft = to_drive(Part.makeCylinder(SHAFT_D / 2, _ls1 - _ls0, V(0, 0, _ls0)))
# Crank shaft on two 608 in a boss outboard of the crank bevel; the outer end is
# left for the crank arm (drawn later).
CRANK_STUB = 22.0
y_cb0 = CB_INFO_B["mount"] + 3.0                          # boss, from the apex outward
y_cb1 = y_cb0 + 2 * CBRG_W + 14.0
crank_shaft = to_drive(Part.makeCylinder(SHAFT_D / 2, y_cb1 + CRANK_STUB - CB_INFO_B["small_end_z"] + 1.0,
                                         V(0, -(CB_INFO_B["small_end_z"] - 1.0), 0), V(0, -1, 0)))
# Bracket 1 (at the pair): plate A across the lay shaft ahead of its bevel (608),
# plate B outboard of the crank bevel with the crank boss (2 x 608); plate A
# reaches in onto the frame spar (at 270, mirrored 90). Bracket 2: a boss behind the rim gear
# (608) on a foot on the front frame ring.
_tip = CB_RS + CB_M + 1.0                                 # bevel tip radius + 1
PL_T = CBRG_W + 2.0
z_pa0 = CB_INFO_S["mount"] + 1.0
_pa_in = -APEX.y - (_spar_rc + 1.0)                       # plate A inner edge: 1 mm past the spar axis
y_pb0 = CB_INFO_B["mount"] + 3.0
_br = [Part.makeBox(2 * _tip, _pa_in + y_pb0 + PL_T, PL_T, V(-_tip, -(y_pb0 + PL_T), z_pa0)),
       Part.makeBox(2 * _tip, PL_T, z_pa0 + PL_T + _tip + 4.0, V(-_tip, -(y_pb0 + PL_T), -_tip - 4.0)),
       Part.makeCylinder(CBOSS_OD / 2, y_cb1 - y_cb0, V(0, -y_cb0, 0), V(0, -1, 0))]
bracket_pair = G.fuse_all(_br)
bracket_pair = bracket_pair.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, 0, z_pa0 + 1.0)))
bracket_pair = bracket_pair.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 60, V(0, 0, z_pa0 - 20)))
for yb in (y_cb0 + 1.0, y_cb1 - 1.0 - CBRG_W):
    bracket_pair = bracket_pair.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, -yb, 0), V(0, -1, 0)))
bracket_pair = bracket_pair.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 300, V(0, 50, 0), V(0, -1, 0)))
z_cboss_r0, z_cboss_r1 = P1_Z0 - 1.0 - PL_T, P1_Z0 - 1.0
_ring_in = -APEX.y - (r_case_od - 2.0)                    # local y 2 mm into the front ring
_b2 = [Part.makeCylinder(CBOSS_OD / 2, PL_T, V(0, 0, _rz(z_cboss_r0))),
       Part.makeBox(16.0, _ring_in, z_cboss_r1 - (Z_FRING1 - 1.0), V(-8.0, 0.0, _rz(Z_FRING1 - 1.0)))]
bracket_rim = G.fuse_all(_b2)
bracket_rim = bracket_rim.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, 0, _rz(z_cboss_r0) + 1.0)))
bracket_rim = bracket_rim.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 60, V(0, 0, _rz(z_cboss_r0) - 20)))
crank_bracket = to_drive(Part.makeCompound([bracket_pair.removeSplitter(), bracket_rim.removeSplitter()]))
crank_bearings = to_drive(Part.makeCompound(
    [tube(CBRG_OD, SHAFT_D, z_pa0 + 1.0, z_pa0 + 1.0 + CBRG_W),
     tube(CBRG_OD, SHAFT_D, _rz(z_cboss_r0) + 1.0, _rz(z_cboss_r0) + 1.0 + CBRG_W)]
    + [Part.makeCylinder(CBRG_OD / 2, CBRG_W, V(0, -yb, 0), V(0, -1, 0)).cut(
        Part.makeCylinder(SHAFT_D / 2, CBRG_W, V(0, -yb, 0), V(0, -1, 0)))
       for yb in (y_cb0 + 1.0, y_cb1 - 1.0 - CBRG_W)]))
# Room for the hand (reference, not a part): knob orbit CRANK_ARM_R, fist
# HAND_R round the knob, HAND_W wide, outboard of the arm.
CRANK_ARM_R, HAND_R, HAND_W, ARM_T = 80.0, 45.0, 100.0, 10.0
y_arm0 = y_cb1 + CRANK_STUB - ARM_T - 2.0                 # arm on the shaft end
hand_space = to_drive(Part.makeCylinder(CRANK_ARM_R + HAND_R, ARM_T + 2.0 + HAND_W,
                                        V(0, -y_arm0, 0), V(0, -1, 0)))
drive_parts = [("crank gear (meshes the rim)", crank_gear), ("lay shaft", pin_shaft),
               ("lay bevel", bevel_small), ("crank bevel", bevel_big), ("crank shaft", crank_shaft),
               ("crank brackets", crank_bracket), ("crank bearings", crank_bearings)]


def _rot_axis(s, deg, c, ax):
    m = s.copy()
    m.rotate(c, ax, deg)
    return m


def to_side(s):
    """Drawn (-Y) -> the crank side: mirror y if CRANK_SIDE is +1."""
    return s.mirror(O, V(0, 1, 0)) if CRANK_SIDE > 0 else s.copy()


_drawn = {"gear": crank_gear, "lay": bevel_small, "crank": bevel_big}
crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket, crank_bearings, hand_space = [
    to_side(x_) for x_ in (crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket,
                           crank_bearings, hand_space)]
drive_parts = [(n_, to_side(s_)) for n_, s_ in drive_parts]


def drive_pose(alpha):
    """Pack turned by alpha: rim; rim gear and lay bevel (-Z_RIM/CP_Z); crank bevel.

    As drawn (-Y) the mesh is at local (0, -RS, +RS): v = 20 w_lay x = 20 w_crank x,
    so the crank bevel turns as the lay shaft, about +Y. Mirrored, pack +alpha is
    the drawn drive at -alpha (the rim maps onto itself).
    """
    a = alpha if CRANK_SIDE < 0 else -alpha
    wl = -Z_RIM / float(CP_Z)
    wc = wl * CB_ZS / float(CB_ZB)
    return (rot(rim_gear, alpha), to_side(rot(_drawn["gear"], wl * a, CP_C)),
            to_side(rot(_drawn["lay"], wl * a, CP_C)), to_side(_rot_axis(_drawn["crank"], wc * a, APEX, V(0, 1, 0))))


crank_mesh_worst = 0.0
for _al in (0.0, 0.6, 1.2, 1.8, 2.4):
    r_, p_, _, _ = drive_pose(_al)
    crank_mesh_worst = max(crank_mesh_worst, r_.common(p_).Volume)
bevel_mesh_worst = 0.0
_bsp = 360.0 / CB_ZS / (Z_RIM / float(CP_Z))       # pack angle per lay-bevel tooth
for _i in range(6):
    _, _, s_, b_ = drive_pose(_bsp * _i / 6.0)
    bevel_mesh_worst = max(bevel_mesh_worst, s_.common(b_).Volume)
PACK_PER_CRANK = (CB_ZB / float(CB_ZS)) * (CP_Z / float(Z_RIM))
CRANK_RPM = 60.0
SHOTS_PER_S = CRANK_RPM / 60.0 * PACK_PER_CRANK * N
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

# ============================================================ controls: flintlock grip, one two-stage lever, feed gate
# The left hand holds a grip that curls down behind the rear plate like a flintlock
# pistol's, with a brass pommel. One big lever runs along its front following its
# curve, as on a fire extinguisher, pivoted at the top behind the plate; the hand
# squeezes it to the grip.
# Stage 1 (0..5 deg) = air: the lever presses the dead-man valve in the grip through
# a pusher with an over-travel spring; the valve is fully open at 5 deg. Stage 2
# (5..15 deg) = balls: the lever's short tail, inside the grip's root, takes up the
# cable's slack by 5 deg and then draws the gate pin 6 mm out of the feed neck. Let go: the
# gate pin's spring shuts the neck, the valve's spring shuts the air, a torsion spring
# on the pivot opens the lever. The rear plate carries the MQR stator and the grip;
# four struts tie it to the rear bearing disk's rim. The valve's outlet runs inside
# the grip, through the plate, into the stator's rear port.
RP_R = 50.0
STRUT_ANGLES = (45.0, 135.0, 225.0, 315.0)
# Grip centreline (x, z) from the plate's aft face (x 0): aft, then curling down.
GRIP_PTS = [(0.0, 0.0), (-2.0, -14.0), (-10.0, -36.0), (-30.0, -64.0), (-62.0, -88.0), (-100.0, -102.0),
            (-128.0, -106.0)]
GRIP_KEYS = [(0.0, 32.0, 24.0), (0.17, 19.0, 15.5), (0.45, 21.0, 16.0), (0.75, 24.0, 18.0), (1.0, 27.0, 20.0)]
POMMEL = (16.0, 31.0, 23.0)                      # brass cap: along the end, in the plane, across
LEV_W, LEV_T, LEV_HUB_R = 14.0, 24.0, 6.0      # a broad blade, like an extinguisher's lever
LEV_ANG, STAGE1 = 15.0, 5.0
S_PIV, S_END, PIV_OFF = 0.12, 0.86, 13.0           # pivot at the top (behind the plate), free end by the pommel
LEV_GAP_PIV = 7.0                                # blade off the grip by the pivot
LEV_GAP_TOP = 26.0                               # ... and at its free end
LUG_T, LUG_GAP, LEV_PIN_D = 4.0, 0.3, 5.0
TAIL_W, TAIL_T = 6.0, 5.0
PUSH_D, PUSH_GAP, OVERTRAVEL_MAX = 5.0, 0.5, 9.0
DM_D, DM_L, DM_STROKE = 14.0, 18.0, 3.0           # dead-man valve body in the grip
GATE_PIN_D, GATE_IN, GATE_CLEAR = 6.0, 5.0, 1.0
GATE_TRAVEL = GATE_IN + GATE_CLEAR
CABLE_OD = 5.0
HOSE_OUT_OD = 8.0                                # dead-man -> stator
SUP_IN_D = 8.0                                   # the receiver hose's fitting, inside the pommel
WIRE_FREE = 14.0                                 # wire from its stop to the tail at rest
CABLE_HOLE = (28.0, -5.0)                        # cable through the plate (outside the stator, inside the grip root)
YA = V(0, 1, 0)


def bar_y(a, b, w, t):
    """Flat bar in the XZ plane from a to b ((x, z)), width w, thickness t along Y, round ends."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dz)
    nx, nz = -dz / ln * w / 2, dx / ln * w / 2
    pts = [V(a[0] + nx, -t / 2, a[1] + nz), V(b[0] + nx, -t / 2, b[1] + nz),
           V(b[0] - nx, -t / 2, b[1] - nz), V(a[0] - nx, -t / 2, a[1] - nz)]
    s_ = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, t, 0))
    for q in (a, b):
        s_ = s_.fuse(Part.makeCylinder(w / 2, t, V(q[0], -t / 2, q[1]), V(0, 1, 0)))
    return s_.removeSplitter()


def cyl_y(x, z, r, t, y0=None):
    return Part.makeCylinder(r, t, V(x, -t / 2 if y0 is None else y0, z), YA)


def turn_y(shape, c, deg):
    s_ = shape.copy()
    s_.rotate(V(c.x, 0, c.z), YA, deg)
    return s_


def turn_pt(pt, c, deg):
    v_ = Part.Vertex(pt)
    v_.rotate(V(c.x, 0, c.z), YA, deg)
    return v_.Point


# --- rear plate (carries the MQR stator and the grip) + struts to the rear bearing disk
mqr_plate = Part.makeCylinder(RP_R, z_mqr_plate1 - z_mqr_plate0, V(0, 0, z_mqr_plate0))
_st = []
for w in STRUT_ANGLES:
    a = math.radians(w)
    p0 = V(106.5 * math.cos(a), 106.5 * math.sin(a), z_brg_r0 + 4.0)
    p1 = V((RP_R - 5.0) * math.cos(a), (RP_R - 5.0) * math.sin(a), z_mqr_plate0 + 3.0)
    _st.append(Part.makeCylinder(SPAR_R, (p1 - p0).Length, p0, p1 - p0))
rear_struts = Part.makeCompound(_st)

# --- grip: a loft through ellipses square to a curved centreline (30 sections)
_gc = Part.BSplineCurve()
_gc.interpolate([V(x_, 0, z_mqr_plate0 + z_) for x_, z_ in GRIP_PTS])
GRIP_LEN = _gc.length()


def grip_frame(f):
    """(centre, tangent, front normal, half height, half width) at fraction f of the grip's length."""
    u_ = _gc.parameterAtDistance(f * GRIP_LEN, _gc.FirstParameter)
    c_ = _gc.value(u_)
    t_ = _gc.tangent(u_)[0]
    t_.normalize()
    n_ = V(t_.z, 0, -t_.x)                       # in the plane, the finger side (down at the root)
    for (f0, h0, w0), (f1, h1, w1) in zip(GRIP_KEYS[:-1], GRIP_KEYS[1:]):
        if f0 <= f <= f1:
            k_ = (f - f0) / (f1 - f0)
            k_ = k_ * k_ * (3.0 - 2.0 * k_)
            return c_, t_, n_, h0 + k_ * (h1 - h0), w0 + k_ * (w1 - w0)
    return c_, t_, n_, GRIP_KEYS[-1][1], GRIP_KEYS[-1][2]


def _gsec(f):
    c_, t_, n_, h_, w_ = grip_frame(f)
    return Part.Wire(Part.Ellipse(c_ + n_ * h_, c_ + YA * w_, c_).toShape())


grip_full = Part.makeLoft([_gsec(i / 29.0) for i in range(30)], True, False)
_ce, _te, _ne, _he, _we = grip_frame(1.0)
_sph = Part.makeSphere(1.0)
_m = App.Matrix(_te.x * POMMEL[0], _ne.x * POMMEL[1], 0, _ce.x + _te.x * 2.0,
                _te.y * POMMEL[0], _ne.y * POMMEL[1], POMMEL[2], 0,
                _te.z * POMMEL[0], _ne.z * POMMEL[1], 0, _ce.z + _te.z * 2.0,
                0, 0, 0, 1)
pommel_full = _sph.transformGeometry(_m)

# --- the lever: pivot low at the front, free end at the top 28 off the grip
_cp, _tp_, _np, _hp, _wp = grip_frame(S_PIV)
P_LEV = _cp + _np * (_hp + PIV_OFF)
# Blade: follows the grip's front down to the pommel, its gap growing towards the free end.
LEV_PTS = [P_LEV]
for _i in range(1, 9):
    _f = S_PIV + (S_END - S_PIV) * _i / 8.0
    _c, _t, _n, _h, _w = grip_frame(_f)
    _g = LEV_GAP_PIV + (LEV_GAP_TOP - LEV_GAP_PIV) * (_i / 8.0)
    LEV_PTS.append(_c + _n * (_h + _g + LEV_W / 2))
E_LEV = LEV_PTS[-1]
LEV_L = sum((b_ - a_).Length for a_, b_ in zip(LEV_PTS[:-1], LEV_PTS[1:]))
_ne_end = grip_frame(S_END)[2]
_v = Part.Vertex(E_LEV)
_v.rotate(V(P_LEV.x, 0, P_LEV.z), YA, 5.0)
SQ = 1.0 if (_v.Point - E_LEV).dot(_ne_end) < 0 else -1.0     # squeeze: the free end goes to the grip


def lever_pt(pt, deg):
    return turn_pt(pt, P_LEV, SQ * deg)


# Tail: from the pivot into the grip's root; solve its length so the wire draws
# GATE_TRAVEL between the stages (the wire's stop sits behind the tip's motion).
TAIL_DIR = _np * -1.0
_mdir = lever_pt(P_LEV + TAIL_DIR * 30.0, 1.0) - (P_LEV + TAIL_DIR * 30.0)
_mdir.normalize()                                # tail tip's motion on squeezing


def _wire(L_):
    tip0 = P_LEV + TAIL_DIR * L_
    stop_ = tip0 - _mdir * WIRE_FREE
    d_ = [(lever_pt(tip0, a_) - stop_).Length - WIRE_FREE for a_ in (STAGE1, LEV_ANG)]
    return d_[0], d_[1] - d_[0], stop_


_L0, _L1 = 20.0, 40.0
for _i in range(30):
    _p0, _p1 = _wire(_L0)[1] - GATE_TRAVEL, _wire(_L1)[1] - GATE_TRAVEL
    if abs(_p1 - _p0) < 1e-12:
        break
    _L0, _L1 = _L1, _L1 - _p1 * (_L1 - _L0) / (_p1 - _p0)
TAIL_L = _L1
WIRE_SLACK, wire_travel, P_STOP = _wire(TAIL_L)
TAIL_TIP = P_LEV + TAIL_DIR * TAIL_L
# One smooth outline (a spline through the blade's centre points, offset either side).
_bc = Part.BSplineCurve()
_bc.interpolate(LEV_PTS)
_side_a, _side_b = [], []
for _i in range(41):
    _u = _bc.FirstParameter + (_bc.LastParameter - _bc.FirstParameter) * _i / 40.0
    _p = _bc.value(_u)
    _tg = _bc.tangent(_u)[0]
    _nn = V(_tg.z, 0, -_tg.x)
    _nn.normalize()
    _side_a.append(_p + _nn * (LEV_W / 2) + V(0, -LEV_T / 2, 0))
    _side_b.append(_p - _nn * (LEV_W / 2) + V(0, -LEV_T / 2, 0))
_outline = _side_a + list(reversed(_side_b))
lever_blade = Part.Face(Part.makePolygon(_outline + [_outline[0]])).extrude(V(0, LEV_T, 0))
lever_blade = lever_blade.fuse(cyl_y(E_LEV.x, E_LEV.z, LEV_W / 2, LEV_T)).removeSplitter()
lever_0 = G.fuse_all([lever_blade, cyl_y(P_LEV.x, P_LEV.z, LEV_HUB_R, LEV_T),
                      bar_y((P_LEV.x, P_LEV.z), (TAIL_TIP.x, TAIL_TIP.z), TAIL_W, TAIL_T)])
lever_0 = lever_0.cut(cyl_y(P_LEV.x, P_LEV.z, LEV_PIN_D / 2 + 0.1, LEV_T + 2))


def lever_at(deg):
    return turn_y(lever_0, P_LEV, SQ * deg)


finger_travel = (lever_pt(E_LEV, LEV_ANG) - E_LEV).Length
stage1_travel = (lever_pt(E_LEV, STAGE1) - E_LEV).Length
# Lugs on the grip each side of the lever, pin through them.
_lugs = []
for _sy in (-1, 1):
    _y0 = LEV_T / 2 + LUG_GAP if _sy > 0 else -(LEV_T / 2 + LUG_GAP + LUG_T)
    _lug = bar_y((P_LEV.x, P_LEV.z), (_cp.x, _cp.z), 2 * LEV_HUB_R + 2.0, LUG_T)
    _lug.translate(V(0, _y0 + LUG_T / 2, 0))
    _lugs.append(_lug)
_pin_l = LEV_T + 2 * (LUG_GAP + LUG_T + 0.7)
lever_pin = cyl_y(P_LEV.x, P_LEV.z, LEV_PIN_D / 2, _pin_l)

# --- dead-man: a pusher on the blade's grip side, along its motion, where 5 deg of squeeze
# makes 3 mm + 0.5 gap; checked with a probe line through the real (curved) blade.
def _blade_face(r_):
    """Point on the blade's grip-side face about r_ from the pivot, and the motion direction there."""
    best = None
    for a_, b_ in zip(LEV_PTS[:-1], LEV_PTS[1:]):
        for k_ in range(21):
            q_ = a_ + (b_ - a_) * (k_ / 20.0)
            if best is None or abs((q_ - P_LEV).Length - r_) < abs((best - P_LEV).Length - r_):
                best = q_
    d_ = lever_pt(best, 1.0) - best              # its motion on squeezing: towards the grip
    d_.normalize()
    return best + d_ * (LEV_W / 2), d_


def _probe_face(org, d_, deg):
    """Distance along d_ from org to the rotated blade's grip-side face (probe line)."""
    seg = Part.LineSegment(org - d_ * 30.0, org + d_ * 30.0).toShape().common(lever_at(deg))
    return max((v_.Point - org).dot(d_) for v_ in seg.Vertexes)


def _press(r_, deg):
    """(axis point on the blade's centre line, direction, rest face, press at deg) for a pusher at r_."""
    q_, d_ = _blade_face(r_)
    q_ = q_ - d_ * (LEV_W / 2)
    t0_ = _probe_face(q_, d_, 0.0)
    return q_, d_, t0_, _probe_face(q_, d_, deg) - t0_ - PUSH_GAP


_ra, _rb = 30.0, 50.0
for _i in range(12):
    _pa, _pb = _press(_ra, STAGE1)[3] - DM_STROKE, _press(_rb, STAGE1)[3] - DM_STROKE
    if abs(_pb - _pa) < 1e-9:
        break
    _ra, _rb = _rb, _rb - _pb * (_rb - _ra) / (_pb - _pa)
R_PUSH = _rb
Q_PUSH, _face_n0, _push_t0, _ = _press(R_PUSH, STAGE1)
_tip = Q_PUSH + _face_n0 * (_push_t0 + PUSH_GAP)


def _pusher_at(tip_, len_=12.0):
    return Part.makeCylinder(PUSH_D / 2, len_, tip_, _face_n0)


def push_depth(tip_, deg):
    """How far the blade at deg pushes a free pusher whose tip is at tip_ (shift it until clear)."""
    lv_ = lever_at(deg)
    if lv_.common(_pusher_at(tip_)).Volume < 1e-6:
        return -gap(lv_, _pusher_at(tip_), pad=5.0)
    lo_, hi_ = 0.0, 20.0
    for _k in range(20):
        mid_ = 0.5 * (lo_ + hi_)
        if lv_.common(_pusher_at(tip_ + _face_n0 * mid_)).Volume > 1e-6:
            lo_ = mid_
        else:
            hi_ = mid_
    return hi_


# The pusher's end meets the tilted blade at its edge first: set the real gap, then
# correct the radius until 5 deg pushes the valve exactly its stroke.
for _it in range(12):
    _tip = Q_PUSH + _face_n0 * (_push_t0 + PUSH_GAP)
    _tip = _tip + _face_n0 * (PUSH_GAP + push_depth(_tip, 0.0))
    _p1 = push_depth(_tip, STAGE1) - PUSH_GAP
    if abs(_p1 - DM_STROKE) < 0.03:
        break
    R_PUSH *= (DM_STROKE / _p1) ** 0.5
    Q_PUSH, _face_n0, _push_t0, _ = _press(R_PUSH, STAGE1)
_ray = Part.LineSegment(_tip, _tip + _face_n0 * 80.0).toShape().common(grip_full)
_entry = min((v_.Point for v_ in _ray.Vertexes), key=lambda p_: (p_ - _tip).Length)
_body0 = _entry + _face_n0 * 8.0                 # the over-travel sleeve, then the valve body
dm_pusher = Part.makeCylinder(PUSH_D / 2, (_body0 - _tip).Length, _tip, _face_n0)
deadman = Part.makeCylinder(DM_D / 2, DM_L, _body0, _face_n0).fuse(
    Part.makeCylinder(4.0, 8.0, _entry, _face_n0)).removeSplitter()
press_s1 = push_depth(_tip, STAGE1) - PUSH_GAP
overtravel = push_depth(_tip, LEV_ANG) - PUSH_GAP - DM_STROKE
_dm_end = _body0 + _face_n0 * DM_L

# --- channels in the grip: cable (plate -> stop in the pommel, along the back), outlet
# (valve -> along the back -> the stator's rear port), supply (pommel tip -> valve).
_back = []
for f_ in (0.08, 0.3, 0.55):
    c_, t_, n_, h_, w_ = grip_frame(f_)
    _back.append((c_, n_, h_))
_cab_in = [V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate0 + 3.0), V(CABLE_HOLE[0] - 6.0, -8.0, z_mqr_plate0 - 10.0),
           P_STOP - _mdir * 12.0 + V(0, -4.0, 0), P_STOP]
_out_in = [_dm_end + V(0, 5.0, 0)] + [c_ - n_ * (0.2 * h_) + V(0, 8.0, 0) for c_, n_, h_ in reversed(_back)] + \
          [V(0, 8.0, z_mqr_plate0 - 4.0), V(0, 8.0, z_mqr_plate0 + 2.0)]
_tip_p = _ce + _te * (POMMEL[0] + 2.0)
_c85, _t85, _n85, _h85, _w85 = grip_frame(0.88)
_c70, _t70, _n70, _h70, _w70 = grip_frame(0.70)
_sup_in = [_tip_p, _ce - _ne * 10.0, _c85 - _n85 * (0.5 * _h85), _c70 - _n70 * (0.3 * _h70) + V(0, -5.0, 0),
           _dm_end + V(0, -5.0, 0)]
cable_in = tube_path(_cab_in, CABLE_OD / 2)
air_supply = tube_path(_out_in, HOSE_OUT_OD / 2)
supply_hose = Part.makeCompound([tube_path(_sup_in, SUP_IN_D / 2),
                                 Part.makeCylinder(SUPPLY_HOSE_OD / 2, 50.0, _tip_p - _te * 2.0, _te)])
gate_wire = Part.makeCylinder(0.6, (TAIL_TIP - P_STOP).Length, P_STOP, TAIL_TIP - P_STOP)
_channels = [tube_path(_cab_in, CABLE_OD / 2 + 0.3), tube_path(_out_in, HOSE_OUT_OD / 2 + 0.3),
             tube_path(_sup_in, SUP_IN_D / 2 + 0.3),
             Part.makeCylinder(1.5, (TAIL_TIP - P_STOP).Length + 2.0, P_STOP, TAIL_TIP - P_STOP)]
# Slot for the tail (its swept volume + 0.5 all round).
_tail_sw = G.fuse_all([bar_y((P_LEV.x, P_LEV.z), (lever_pt(TAIL_TIP, a_).x, lever_pt(TAIL_TIP, a_).z),
                             TAIL_W + 1.0, TAIL_T + 1.0) for a_ in [LEV_ANG * i / 6.0 for i in range(7)]])
grip = grip_full.fuse(_lugs)
pommel = pommel_full.cut(grip_full)
for _c in _channels + [_tail_sw, lever_pin]:
    grip = grip.cut(_c)
    pommel = pommel.cut(_c)
grip = grip.cut(Part.makeCylinder(DM_D / 2 + 0.3, DM_L + 0.3, _body0, _face_n0))
grip = grip.cut(Part.makeCylinder(4.3, 8.3, _entry - _face_n0 * 0.3, _face_n0))
grip = grip.cut(Part.makeCylinder(PUSH_D / 2 + 0.3, 30.0, _entry - _face_n0 * 10.0, _face_n0))
grip = grip.removeSplitter()
pommel = pommel.removeSplitter()
mqr_plate = mqr_plate.cut(Part.makeCylinder(CABLE_OD / 2 + 0.5, 20.0, V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate0 - 5.0)))
mqr_plate = mqr_plate.cut(Part.makeCylinder(HOSE_OUT_OD / 2 + 0.3, 20.0, V(0, 8.0, z_mqr_plate0 - 5.0)))   # into the stator's rear port
lever = lever_at(0.0)
hand_left = tube_path([grip_frame(f_)[0] for f_ in (0.32, 0.5, 0.66, 0.78)], 36.0)

# --- feed gate: a pin across the neck from aft, spring-closed, pulled out by the cable
Z_NECK = Z_BALL_OPEN
NECK_R = _fb["NECK_ID"] / 2.0
NECK_OR = NECK_R + _fb["NECK_WALL"]
x_gate = X_STAR + STAR_R + 0.5 + GATE_PIN_D / 2 + 1.0
z_neck_aft = Z_NECK - NECK_OR                      # neck's outer face, aft side, at y 0
z_pin_tip = Z_NECK - NECK_R + GATE_IN              # closed
GATE_HW, GATE_L = 8.0, 26.0
z_gh0 = z_neck_aft - GATE_L
gate_housing = Part.makeBox(2 * GATE_HW, 2 * GATE_HW, GATE_L + 10.0, V(x_gate - GATE_HW, -GATE_HW, z_gh0)).cut(
    Part.makeCylinder(NECK_OR, 60.0, V(x_gate - 30.0, 0, Z_NECK), V(1, 0, 0)))
_cav0, _cav1 = z_gh0 + 3.0, z_neck_aft - 2.0
gate_housing = gate_housing.cut(Part.makeCylinder(5.0, _cav1 - _cav0, V(x_gate, 0, _cav0)))
gate_housing = gate_housing.cut(Part.makeCylinder(GATE_PIN_D / 2 + 0.15, 10.0, V(x_gate, 0, _cav1 - 1.0)))
gate_housing = gate_housing.cut(Part.makeCylinder(1.0, 5.0, V(x_gate, 0, z_gh0 - 1.0))).removeSplitter()
feed_head = feed_head.cut(Part.makeCylinder(GATE_PIN_D / 2 + 0.15, NECK_OR - NECK_R + 2.0,
                                            V(x_gate, 0, z_neck_aft - 1.0)))
# The housing is glued onto the neck and the shroud's side wall below it: it takes
# their shape (the side wall runs down past the neck on the aft side).
gate_housing = gate_housing.cut(feed_head).removeSplitter()
gate_housing = Part.makeCompound([s_ for s_ in gate_housing.Solids if s_.Volume > 50.0]) \
    if len(gate_housing.Solids) > 1 else gate_housing


def gate_at(open_):
    """(pin with collar, spring) closed (False) or pulled open (True)."""
    dz_ = -GATE_TRAVEL if open_ else 0.0
    c0 = _cav1 - 2.0 + dz_
    pin = Part.makeCylinder(GATE_PIN_D / 2, z_pin_tip + dz_ - c0, V(x_gate, 0, c0)).fuse(
        Part.makeCylinder(4.5, 2.0, V(x_gate, 0, c0))).removeSplitter()
    spring = tube(8.0, 6.8, _cav0, c0, x_gate, 0.0)
    return pin, spring, c0 - _cav0


gate_pin, gate_spring, gate_spring_closed = gate_at(False)
gate_pin_open, gate_spring_open, gate_spring_opened = gate_at(True)
# Cable: housing from the gate along the top, left of the strap loop, round the rear
# bearing disk, through the rear plate (outside the stator) into the grip, down its
# back to the stop in the pommel; the wire runs to the lever's tail.
_cab_ex = [V(x_gate, 0, z_gh0), V(x_gate, 0, z_gh0 - 15.0), V(128.0, -30.0, z_gh0 - 70.0),
           V(122.0, -30.0, -120.0), V(122.0, -30.0, z_brg_r0 - 20.0), V(92.0, -18.0, z_mqr_plate1 + 25.0),
           V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate1 + 10.0), _cab_in[0]]
cable_ex = tube_path(_cab_ex, CABLE_OD / 2)
gate_cable = Part.makeCompound([cable_ex, cable_in])
CABLE_LEN = path_len(_cab_ex) + path_len(_cab_in)
gate_parts = Part.makeCompound([gate_housing, gate_pin, gate_spring])

# --- control checks
print("controls…", flush=True)
_lev_hit, _lev_worst = 0.0, "-"
for _i in range(7):
    _a = LEV_ANG * _i / 6.0
    _l = lever_at(_a)
    for _fn, _fx in (("grip", grip), ("pommel", pommel), ("pin", lever_pin), ("plate", mqr_plate),
                     ("cable", cable_in), ("hoses", Part.makeCompound([air_supply, supply_hose])),
                     ("valve", deadman)):
        if not _near(_l.BoundBox, _fx.BoundBox, 0.1):
            continue
        _v = _l.common(_fx).Volume
        if _v > _lev_hit:
            _lev_hit, _lev_worst = _v, "%s at %.1f deg" % (_fn, _a)
lever_closed = gap(turn_y(lever_blade, P_LEV, SQ * LEV_ANG), grip_full)   # the blade; the tail lives in its slot
push_released = gap(lever_at(0.0), dm_pusher)
grip_on_plate = gap(grip, mqr_plate)
grip_one = len(grip.Solids) == 1
_skin = Part.makeCompound([f_ for f_ in grip_full.Faces if f_.Surface.__class__.__name__ != "Plane"])
_walls = [(n_, tube_path(pts_, r_).distToShape(_skin)[0])
          for n_, pts_, r_ in (("cable", _cab_in[1:], CABLE_OD / 2 + 0.3), ("outlet", _out_in[1:-2], HOSE_OUT_OD / 2 + 0.3),
                               ("valve", [_body0, _dm_end], DM_D / 2 + 0.3))]
chan_wall = min(w_ for _, w_ in _walls)
_wall_worst = min(_walls, key=lambda x_: x_[1])[0]
stop_in_pommel = Part.makeSphere(CABLE_OD / 2, P_STOP).common(Part.makeCompound([pommel_full, grip_full])).Volume \
    > 0.99 * (4.0 / 3.0 * math.pi * (CABLE_OD / 2) ** 3)
# Gate: a ball in the neck at the pin, on the axis and pushed to either wall.
_gate_block, _gate_free = 99.0, 99.0
for _off in (-(NECK_R - PELLET_D / 2), 0.0, NECK_R - PELLET_D / 2):
    _b = Part.makeSphere(PELLET_D / 2, V(x_gate, 0, Z_NECK + _off))
    _gate_block = min(_gate_block, _b.common(gate_pin).Volume)
    _gate_free = min(_gate_free, gap(_b, gate_pin_open))
gate_head = max(gate_housing.common(feed_head).Volume, gate_pin.common(feed_head).Volume,
                gate_pin_open.common(feed_head).Volume)
gate_star = min(gap(Part.makeCompound([gate_housing, gate_pin, gate_pin_open]), star_at(d_))
                for d_ in [-30.0 + 5.0 * i for i in range(13)])
gate_lip = gap(gate_parts, feed_lip)
# Struts against what turns behind the pack (the lines, coupling and rotor are 6-fold).
strut_turn = 99.0
for _a in range(0, 60, 5):
    for _r in (lines_inner, soft_coup, mqr_rotor):
        strut_turn = min(strut_turn, gap(rot(_r, float(_a)), rear_struts, pad=5.0))
strut_on = min(gap(rear_struts, brg_r), gap(rear_struts, mqr_plate))
_cable_fixed = [("liner", cam), ("frame", pack_frame), ("bearing disks", Part.makeCompound([brg_f, brg_r])),
                ("strap", sling), ("struts", rear_struts), ("stator", mqr_stator), ("star train box", gearbox),
                ("feed cup", feed_cup), ("star", star0)]
cable_gap, cable_near = min((gap(cable_ex, s_, pad=5.0), n_) for n_, s_ in _cable_fixed)
_hand_l_gun = [("plate", mqr_plate), ("struts", rear_struts), ("stator", mqr_stator), ("cable", cable_ex),
               ("bearing disk", brg_r), ("receiver hose", supply_hose.Solids[-1])]
hand_l_gap, hand_l_near = min((gap(hand_left, s_, pad=5.0), n_) for n_, s_ in _hand_l_gun)

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
lines_fixed = min(gap(lines_inner, s) for s in (brg_f, brg_r, mqr_stator, air_supply, mqr_plate, rear_struts))
bundle_fit = (AXLE_ID / 2.0) - BUNDLE_R
bearings_on_axle = (gap(pack_axle, brg_f) < 1.5 and gap(pack_axle, brg_r) < 1.5
                    and brg_f.BoundBox.ZMin > z_axle0 and brg_r.BoundBox.ZMin > z_axle0)
mqr_free = gap(pack_axle, mqr_rotor) > 1.0 and gap(pack_axle, mqr_stator) > 1.0
rim_vs_closed = min(gap(rim_gear, place(Part.makeCompound(qev_slide), k * 60.0)) for k in range(N))
star_top = star_vs_stations = min(gap(star0, s) for s in stations)
# Pack drive: every drive part vs the stations (six phases; full turn in the sweep),
# vs the fixed parts round it, its gears vs its own bracket, the hand vs everything.
_drv = [s for _, s in drive_parts]
DRIVE_PAD = 5.0                   # bbox prefilter: a real distance only when it is below this
drive_vs_stations = min(gap(d, st, pad=DRIVE_PAD) for d in _drv for st in stations)
drive_vs_rim = min(gap(rim_gear, d) for n, d in drive_parts if not n.startswith("crank gear"))
_near_fixed = [gearbox, gear_a, gear_b, gear_i, gear_s, lay_shaft, idl_shaft, star_shaft, star0,
               feed_head, feed_cup, feed_lip, feed_guard, front_plate, carry_handle, sling]
drive_vs_fixed = min(gap(d, f, pad=DRIVE_PAD) for d in _drv for f in _near_fixed)


def far(g, pad=DRIVE_PAD):
    return ("> %.0f" % pad) if g >= 99.0 else ("%.2f" % g)
drive_vs_frame = min(gap(d, pack_frame) for n, d in drive_parts if n != "crank brackets")
bracket_on_ring = all(gap(b_, pack_frame) < 0.05 for b_ in crank_bracket.Solids) and len(crank_bracket.Solids) == 2
gears_vs_bracket = min(gap(g, crank_bracket) for g in (crank_gear, bevel_small, bevel_big))
bevels_apart = gap(bevel_small, crank_gear)
# The hand against the gun (not its own drive); the arm stands off the boss by design.
_hand_gun = [("star-drive box", gearbox), ("star train", Part.makeCompound([gear_a, gear_b, gear_i, gear_s])),
             ("feed head", feed_head), ("cup", feed_cup), ("guard", feed_guard), ("carry handle", carry_handle),
             ("strap loops", sling), ("frame", pack_frame), ("liner", cam), ("front plate", front_plate),
             ("ramp", ramp_fire),
             ("bearing disks", Part.makeCompound([brg_f, brg_r])),
             ("dead-man and hose", Part.makeCompound([deadman, air_supply, supply_hose])),
             ("pack (six phases)", Part.makeCompound(stations)), ("rim", rim_gear)]
hand_gap, hand_near = min((gap(hand_space, s_, pad=150.0), n_) for n_, s_ in _hand_gun)
hand_own = min(gap(hand_space, s_, pad=20.0) for n_, s_ in drive_parts if n_ != "crank shaft")
# Ramp mount block vs the stations, six phases (full turn in the sweep).
mount_vs_stations = min(gap(guide_block, st) for st in stations)
print("fast checks done", flush=True)

# ============================================================ assembly / checks / report
pack = Part.makeCompound(stations)
assembly = Part.makeCompound([
    pack, cam, front_plate, pack_frame, rear_disk, rim_gear, gear_a, gear_b, gear_i, gear_s,
    star_shaft, lay_shaft, idl_shaft, gearbox, star0, feed_head, feed_lip, feed_cup, feed_guard,
    ramp_fire, guide_block, rear_struts, grip, pommel, lever, lever_pin, dm_pusher, gate_wire, gate_cable,
    gate_housing, gate_pin, gate_spring, crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket, crank_bearings,
    carry_handle, sling, pack_axle, brg_f, brg_r, soft_coup, mqr_rotor, mqr_stator,
    mqr_plate, lines_inner, deadman, air_supply, supply_hose,
])
bb = assembly.optimalBoundingBox()
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
    ("ramp fixed in the press position, seated on its mount block (%.2f)" % ramp_seated, ramp_seated < 0.01),
    ("liner not cut through: insert holes blind (%.1f wall left), one solid" % _wall_left, insert_blind and liner_one),
    ("ramp mount block and insert holes clear of the groove (%s), stations six phases (%s)"
     % (far(groove_vs_mount), far(mount_vs_stations, 2.0)), groove_vs_mount >= 2.0 and mount_vs_stations >= CLEAR),
    ("rear plate on %d struts from the rear bearing disk (%.2f), grip on the plate (%.2f); struts vs lines,"
     " coupling, rotor over a turn %s" % (len(STRUT_ANGLES), strut_on, grip_on_plate, far(strut_turn)),
     strut_on < 0.05 and grip_on_plate < 0.05 and strut_turn >= 2.0),
    ("grip one solid; cable, outlet and valve inside it (wall %.1f at the %s); cable stop inside the grip"
     % (chan_wall, _wall_worst), grip_one and chan_wall >= 1.5 and stop_in_pommel),
    ("lever 0..%.0f deg in 6 steps: no overlap with the grip, pommel, pin, plate, cable, hoses, valve (%.3f mm3 %s);"
     " closed %.2f off the grip" % (LEV_ANG, _lev_hit, _lev_worst, lever_closed), _lev_hit < 0.01 and lever_closed >= 1.0),
    ("stage 1 (0..%.0f deg, free end %.1f mm): dead-man pressed %.2f of %.1f, pusher %.2f off released;"
     " over-travel %.1f by %.0f deg (<= %.0f)" % (STAGE1, stage1_travel, press_s1, DM_STROKE, push_released, overtravel,
                                                 LEV_ANG, OVERTRAVEL_MAX),
     abs(press_s1 - DM_STROKE) < 0.05 and push_released >= PUSH_GAP - 0.05 and 0.0 < overtravel <= OVERTRAVEL_MAX),
    ("stage 2 (%.0f..%.0f deg): the tail takes up %.1f mm of slack, then pulls the wire %.2f = gate travel %.1f"
     % (STAGE1, LEV_ANG, WIRE_SLACK, wire_travel, GATE_TRAVEL), abs(wire_travel - GATE_TRAVEL) < 0.05 and WIRE_SLACK > 0.5),
    ("gate closed stops a ball anywhere across the neck (%.0f mm3), open lets it by (%.2f)"
     % (_gate_block, _gate_free), _gate_block > 1.0 and _gate_free >= 0.5),
    ("gate housing glued on the neck (%d solid), pin through its own hole (%.3f mm3 into the feed head);"
     " clear of the star over its turn (%.2f) and the lip (%s)"
     % (len(gate_housing.Solids), gate_head, gate_star, far(gate_lip)),
     len(gate_housing.Solids) == 1 and gate_head < 0.01 and gate_star >= CLEAR and gate_lip >= CLEAR),
    ("gate cable %.0f mm (through the rear plate into the grip) clear of the liner, frame, disks, strap,"
     " struts, stator, box, cup, star (%.2f, %s)"
     % (CABLE_LEN, cable_gap, cable_near), cable_gap >= 2.0),
    ("left hand round the grip (R 36) %s to the gun (%s)" % (far(hand_l_gap), hand_l_near), hand_l_gap >= 5.0),
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
    ("carry handle on top, crank on the side", carry_handle.BoundBox.Center.x > 0.0
     and abs(crank_shaft.BoundBox.Center.y) > abs(crank_shaft.BoundBox.Center.x)),
    ("pack drive %d:%d bevel (m%.0f) -> gear %d in rim %d: %.3f pack turn per crank turn, %.0f rpm -> %.1f shots/s"
     % (CB_ZB, CB_ZS, CB_M, CP_Z, Z_RIM, PACK_PER_CRANK, CRANK_RPM, SHOTS_PER_S),
     abs(PACK_PER_CRANK - 0.5) < 1e-9 and abs(SHOTS_PER_S - 3.0) < 1e-9),
    ("crank gear on the rim: centre %.3f on the pitch sum, mesh overlap %.2f mm3 over a rim tooth"
     % (abs(CP_C.Length - (R_RIM + R_CP)), crank_mesh_worst),
     abs(CP_C.Length - (R_RIM + R_CP)) < 1e-6 and crank_mesh_worst < 1.0),
    ("bevel pair %d:%d, cones %.1f/%.1f deg: mesh overlap %.2f mm3 over a tooth"
     % (CB_ZS, CB_ZB, CB_DS, CB_DB, bevel_mesh_worst), bevel_mesh_worst < 1.0),
    ("drive vs stations, six phases %s >= %.2f" % (far(drive_vs_stations), CLEAR), drive_vs_stations >= CLEAR),
    ("drive vs rim (all but its gear) %s, star train / feed / handle %s, frame %s"
     % (far(drive_vs_rim, 2.0), far(drive_vs_fixed), far(drive_vs_frame, 2.0)),
     min(drive_vs_rim, drive_vs_fixed, drive_vs_frame) >= CLEAR),
    ("crank brackets stand on the frame (spar, front ring); gears clear them by %.2f" % gears_vs_bracket,
     bracket_on_ring and gears_vs_bracket >= CLEAR and bevels_apart >= CLEAR),
    ("room for the hand (crank R %.0f, fist R %.0f x %.0f): %.1f to the gun (%s), %.1f to its own boss"
     % (CRANK_ARM_R, HAND_R, HAND_W, hand_gap, hand_near, hand_own), hand_gap >= 20.0 and hand_own >= 5.0),
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
    "  ramp                   : fixed in the press position on a block in the liner (z %.1f..%.1f, 2 x M3 inserts);"
    " air is switched by the dead-man" % (z_blk0, z_blk1),
    "  controls               : flintlock grip behind the rear plate (%.0f long, brass pommel); one lever along its"
    " front, %.0f long, pivot at the top behind the plate, %.0f deg; stage 1 to %.0f deg = air (dead-man, %.1f mm at the free end),"
    " stage 2 = balls (Bowden %.0f mm, slack %.1f, gate pin %.1f); free end %.1f mm"
    % (GRIP_LEN, LEV_L, LEV_ANG, STAGE1, stage1_travel, CABLE_LEN, WIRE_SLACK, GATE_TRAVEL, finger_travel),
    "  rear frame             : plate R %.0f carries the MQR stator and the grip; %d struts Ø%.0f to the rear bearing"
    " disk" % (RP_R, len(STRUT_ANGLES), 2 * SPAR_R),
    "  feed                   : feed_bench star (3 pockets, 2:1) at the top; handoff 180°;"
    " guard %.0f–%.0f° following the close" % (GUARD_PHI0, GUARD_END),
    "  star drive             : rim %d on the breech clamps (z %.1f..%.1f) -> %d | %d -> %d -> %d;"
    " layshaft R %.0f at %.0f°" % (Z_RIM, P1_Z0, P1_Z1, Z_A, Z_B, Z_I, Z_S, L_C.Length, L_ANG),
    "  frame envelope Ø       : %.0f (liner); was %.0f" % (case_od, CASE_OD_START),
    "  air                    : axle Al %.0f x %.1f, %s; 6 lines 1/8\" inside; MQR rotor z %.0f..%.0f"
    % (AXLE_OD, (AXLE_OD - AXLE_ID) / 2.0, BRG_NAME, z_rotor0, z_rotor1),
    "  air supply             : no buffer; Ø%.0f hose from the receiver -> pommel -> dead-man in the grip -> stator's rear port (z %.0f)"
    % (SUPPLY_HOSE_OD, z_supply),
    "  pack drive             : crank axis across the barrels (%s) at z %.0f (middle of the closed QEV);"
    " bevel %d:%d m%.0f -> lay shaft at r %.0f -> gear %d in rim %d; %.2f pack turn per crank turn"
    % ("+Y, right" if CRANK_SIDE > 0 else "−Y, left", Z_CRANK, CB_ZB, CB_ZS, CB_M, CP_C.Length, CP_Z, Z_RIM,
       PACK_PER_CRANK),
    "  crank turn             : top of the crank goes %s; shaft stub to |y| %.0f, arm and knob not drawn"
    % ("forward" if (Z_RIM / float(CP_Z)) * CB_ZS / float(CB_ZB) * -CRANK_SIDE > 0 else "aft (towards the shooter)",
       max(abs(crank_shaft.BoundBox.YMin), abs(crank_shaft.BoundBox.YMax))),
    "  rate                   : %.0f rpm on the crank -> %.1f shots/s" % (CRANK_RPM, SHOTS_PER_S),
    "  room for the hand      : y %.0f..%.0f, r %.0f round the crank axis; %.1f mm to the gun (%s)"
    % (hand_space.BoundBox.YMin, hand_space.BoundBox.YMax, CRANK_ARM_R + HAND_R, hand_gap, hand_near),
    "  carry                  : handle on top ahead of the gearbox; strap loops front/aft",
]
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  overall LxWxH         : %.0f x %.0f x %.0f mm (was %.0f long)" % (gun_L, gun_W, gun_H, L_START),
    "  not drawn             : valve bracket bolts,"
    " 1→6 manifold on the stator, crank arm and knob, wheeled carriage, freeze",
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
FV.STYLES["deadman"] = ((0.75, 0.25, 0.20), 15)
FV.STYLES["guard"] = ((0.60, 0.30, 0.75), 40)
FV.STYLES["carry"] = ((0.28, 0.28, 0.30), 15)
FV.STYLES["hand"] = ((0.95, 0.75, 0.60), 80)
FV.STYLES["wood"] = ((0.45, 0.27, 0.13), 0)
FV.STYLES["brass"] = ((0.80, 0.63, 0.28), 0)

if BREECH_MECH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Cam", "Cam_liner", cam, "cam")
sc.add("Fire", "Firing_ramp", ramp_body, "ramp")
sc.add("Fire", "Ramp_mount_block", guide_block, "frame")
sc.add("Controls", "Grip", grip, "wood")
sc.add("Controls", "Pommel", pommel, "brass")
sc.add("Controls", "Lever", lever, "ramp")
sc.add("Controls", "Lever_pin", lever_pin, "drive")
sc.add("Controls", "Deadman_pusher", dm_pusher, "drive")
sc.add("Controls", "Gate_cable", gate_cable, "drive")
sc.add("Controls", "Gate_wire", gate_wire, "drive")
sc.add("Controls", "Gate_housing", gate_housing, "feed")
sc.add("Controls", "Gate_pin", gate_pin, "ramp")
sc.add("Controls", "Gate_spring", gate_spring, "brg")
sc.add("Reference", "Left_hand_on_grip", hand_left, "hand")
sc.add("Air", "Rear_struts", rear_struts, "frame")
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
sc.add("Drive", "Crank_rim_gear_60", crank_gear, "gear")
sc.add("Drive", "Lay_shaft", pin_shaft, "drive")
sc.add("Drive", "Bevel_lay", bevel_small, "gear")
sc.add("Drive", "Bevel_crank", bevel_big, "gear")
sc.add("Drive", "Crank_shaft", crank_shaft, "drive")
sc.add("Drive", "Crank_bracket", crank_bracket, "frame")
sc.add("Drive", "Crank_bearings_608", crank_bearings, "brg")
sc.add("Reference", "Hand_space", hand_space, "hand")
sc.add("Carry", "Carry_handle", carry_handle, "carry")
sc.add("Carry", "Sling_loops", sling, "carry")
sc.add("Air", "Pack_axle", pack_axle, "drive")
sc.add("Air", "Bearing_front", brg_f, "brg")
sc.add("Air", "Bearing_rear", brg_r, "brg")
sc.add("Air", "Soft_coupling", soft_coup, "drive")
sc.add("Air", "MQR_rotor", mqr_rotor, "mqr")
sc.add("Air", "MQR_stator", mqr_stator, "mqr")
sc.add("Air", "Rear_plate", mqr_plate, "frame")
sc.add("Air", "Lines_in_axle", lines_inner, "hose")
sc.add("Air", "Deadman_valve", deadman, "deadman")
sc.add("Air", "Supply_stub", air_supply, "hose")
sc.add("Air", "Supply_hose_end", supply_hose, "hose")
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
