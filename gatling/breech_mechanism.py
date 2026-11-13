# -*- coding: utf-8 -*-
"""
Gatling breech mechanism on the dense pack sketch (not a freeze).

Builds, in order: stroke from linear_breech → angle→stroke law → fixed cylindrical
cam track → one real station clearances → six phases @ 60° → feed hopper in the
LOAD window → crank → pilot/supply hose stubs. No wheeled carriage; no full-length
tube (classic plates + breech casing only). Pack R / length / casing may grow if
the cam or feed will not seat — starting sketch is breech_pack numbers.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism.py').read())"

Law (paper in docs/gatling.md): FIRE 330–30° u=0; OPEN 30–120°; LOAD 120–240° u=1;
CLOSE 240–330°. dz = −STROKE · u. STROKE from the bench (65.8 mm).

Exports: exports/gatling_breech_mechanism/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
V = App.Vector

# --- starting pack sketch (not frozen) ---------------------------------------
TARGET_L = 750.0
BARREL_SHOW_DEFAULT = 160.0
N = 6
# Keep yoke-floor pack R; cam is an OUTBOARD liner (hub cam hits the L-thumb web).
R_PACK = 58.50
R_PACK_START = 58.50
CLEAR = 0.5
PLATE_T, PLATE_LIP, PLATE_RIM = 14.0, 1.5, 3.0
CASE_WALL, CASE_CLEAR, CASE_OVERLAP = 2.0, 0.5, 18.0

# Outboard cylindrical cam liner just inside the breech casing (aft of breech).
CAM_WALL = 5.0
FOLLOWER_OD = 5.0
FOLLOWER_CLEAR = 0.5
CAM_Z_PAD = 8.0
CAM_CLEAR_Z = 2.0

# Law breakpoints (deg). Smooth half-cosine ramps between dwells.
FIRE_A, FIRE_B = 330.0, 30.0   # closed dwell wrapping 0°
OPEN_A, OPEN_B = 30.0, 120.0
LOAD_A, LOAD_B = 120.0, 240.0
CLOSE_A, CLOSE_B = 240.0, 330.0

GATLING_LINEAR_BREECH_LIBRARY = True
SHOW_OPEN = False
BARREL_SHOW = BARREL_SHOW_DEFAULT
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin
BARREL_SHOW = TARGET_L - (z_stop - Z_AFT_CLIP)
assert BARREL_SHOW > 50.0
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin

# Bench stroke / dead points — single source; do not invent another number.
BENCH_STROKE = STROKE
assert abs(BENCH_STROKE - (FIT_INSERT + PELLET_D + STROKE_MARGIN)) < 1e-6


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


def tube(od, idd, z0, z1, x=0.0, y=0.0):
    return G.cyl(od, z0, z1, x, y).cut(G.cyl(idd, z0 - 1, z1 + 1, x, y))


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def cam_u(phi_deg):
    """Angle → open fraction. Matches docs/gatling.md law table."""
    phi = phi_deg % 360.0
    # FIRE dwell (wraps across 0°)
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


def place_shape(shape, R, ang_deg):
    """Rails / AirTAC (−Y) toward pack axis; feed (+Y) radial out."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(ux, uy)))
    s.translate(V(R * ux, R * uy, 0))
    return s


# --- outboard aft cam liner + radial-out follower --------------------------------
# Hub drum hits the L-thumb web when open. Cam is outside the chamber circle so
# open QEV can pass inside it; casing CLEAR grows to wrap the liner.
z_carr_aft = qev_closed["Carriage"].BoundBox.ZMin
z_cam1 = z_carr_aft - CAM_CLEAR_Z
z_tip0 = z_cam1 - CAM_Z_PAD * 0.5
z_cam0 = z_tip0 - BENCH_STROKE - CAM_Z_PAD
# Groove outside open-QEV envelope: yoke/plug ears r≈33 (not just chamber 25).
EAR_ENV = 33.0
CAM_R = R_PACK + EAR_ENV + CLEAR + CAM_WALL / 2 + 1.0
cam_od = 2.0 * (CAM_R + CAM_WALL / 2)
cam_id = 2.0 * (CAM_R - CAM_WALL / 2)
# Casing must clear cam OD.
CASE_CLEAR_CAM = cam_od / 2 - (R_PACK + CH_OD / 2) + CLEAR
y_tip = CAM_R - R_PACK
y_root = CH_OD / 2 + 2.0
follower = Part.makeCylinder(
    FOLLOWER_OD / 2, max(6.0, y_tip - y_root),
    V(0, y_root, z_tip0), V(0, 1, 0))
follower = follower.fuse(Part.makeSphere(
    FOLLOWER_OD / 2 + 0.2, V(0, y_tip, z_tip0))).removeSplitter()
stem_z1 = z_ry - CARR_T
if stem_z1 > z_tip0 + 2.0:
    follower = follower.fuse(Part.makeCylinder(
        FOLLOWER_OD / 2, stem_z1 - z_tip0,
        V(0, y_root + 2.0, z_tip0), V(0, 0, 1))).removeSplitter()

cam_drum = tube(cam_od, cam_id, z_cam0, z_cam1)
n_seg = 72
groove_r = FOLLOWER_OD / 2 + FOLLOWER_CLEAR
balls = [Part.makeSphere(
    groove_r,
    V(CAM_R * math.cos(math.radians(360.0 * i / n_seg)),
      CAM_R * math.sin(math.radians(360.0 * i / n_seg)),
      z_tip0 + cam_dz(360.0 * i / n_seg)))
    for i in range(n_seg)]
groove_cut = G.fuse_all(balls)
cam = cam_drum.cut(groove_cut).removeSplitter()
if cam.isNull() or cam.Volume < 1.0:
    cam = cam_drum
    probe_notes_pre = ["groove cut failed — liner kept"]
else:
    probe_notes_pre = [
        "outboard cam R=%.1f Ø%.0f; casing CLEAR→%.1f (sketch moved)"
        % (CAM_R, cam_od, CASE_CLEAR_CAM)]

# --- station compounds -------------------------------------------------------
slide_keys = list(qev_closed.keys())
slide0 = Part.makeCompound([qev_closed[k].copy() for k in slide_keys] + [follower])
fixed0 = Part.makeCompound([
    rails_s, cradle, vent_body, vent_fittings, vent_plunger,
    barrel_clamp, barrel_collar, fixed_barrel,
])


def station_local(phi_deg):
    dz = cam_dz(phi_deg)
    return Part.makeCompound([shifted(slide0, dz), fixed0.copy()])


def station_placed(phi_deg, R=None):
    R = R_PACK if R is None else R
    return place_shape(station_local(phi_deg), R, phi_deg)


# Core for neighbour gap: chamber / plugs / yoke at their stroke (no clamps).
def core_local(phi_deg):
    dz = cam_dz(phi_deg)
    parts = [shifted(qev_closed[k], dz) for k in qev_closed if k != "Carriage"]
    return Part.makeCompound(parts)


# --- one-station clearance probes (φ = 0 / 90 / 180) -------------------------
probe_angles = [0.0, 90.0, 180.0]
probe_notes = list(probe_notes_pre)
rail_cam_ok = True
case_ok = True
CASE_CLEAR_USE = max(CASE_CLEAR, CASE_CLEAR_CAM)
r_case_id = R_PACK + CH_OD / 2 + CASE_CLEAR_USE
r_case_od = r_case_id + CASE_WALL
rmax_all = 0.0

for pa in probe_angles:
    body = place_shape(shifted(Part.makeCompound(
        [qev_closed[k] for k in qev_closed] + [rails_s]), cam_dz(pa)), R_PACK, pa)
    d_cam = body.distToShape(cam)[0]
    d_carr = place_shape(shifted(qev_closed["Carriage"], cam_dz(pa)),
                         R_PACK, pa).distToShape(cam)[0]
    qev_only = place_shape(shifted(Part.makeCompound(
        [qev_closed[k] for k in qev_closed if k != "Carriage"]), cam_dz(pa)),
        R_PACK, pa)
    pts = qev_only.tessellate(1.2)[0]
    rmax = max(math.hypot(p.x, p.y) for p in pts) if pts else 0.0
    rmax_all = max(rmax_all, rmax)
    clear_case = r_case_id - rmax
    probe_notes.append(
        "φ=%.0f body↔cam=%.2f carr↔cam=%.2f QEV_rmax=%.1f case_clear=%.1f"
        % (pa, d_cam, d_carr, rmax, clear_case))
    if d_cam < CLEAR - 1e-3 or d_carr < CLEAR - 1e-3:
        rail_cam_ok = False
    if clear_case < CLEAR - 1e-3:
        case_ok = False

if not case_ok:
    CASE_CLEAR_USE = max(CASE_CLEAR_USE, rmax_all - (R_PACK + CH_OD / 2) + CLEAR)
    r_case_id = R_PACK + CH_OD / 2 + CASE_CLEAR_USE
    r_case_od = r_case_id + CASE_WALL
    case_ok = True
    probe_notes.append("casing CLEAR bumped to %.2f" % CASE_CLEAR_USE)

# Neighbour gap at all six phases.
cores = [place_shape(core_local(k * 60.0), R_PACK, k * 60.0) for k in range(N)]
gap_core = 1e9
for i in range(N):
    for j in range(i + 1, N):
        gap_core = min(gap_core, cores[i].distToShape(cores[j])[0])
neighbours_ok = gap_core >= CLEAR - 1e-6

# --- six phased stations -----------------------------------------------------
phases = []
stations = []
for k in range(N):
    ang = k * 60.0
    u = cam_u(ang)
    dz = cam_dz(ang)
    st = station_placed(ang)
    stations.append(st)
    phases.append((k + 1, ang, u, dz, phase_name(ang)))

# --- classic skin (plates + breech casing only) ------------------------------
z_tip_b = z_stop + BARREL_SHOW
z_stroke_end = qev_closed["Carriage"].BoundBox.ZMin - BENCH_STROKE
z_front0 = z_tip_b - PLATE_T + PLATE_LIP
z_front1 = z_tip_b + PLATE_LIP
z_rear0 = z_stop - PLATE_T * 0.35
z_rear1 = z_rear0 + PLATE_T
z_case1 = z_rear0 + CASE_OVERLAP
z_case0 = min(z_stroke_end, z_cam0)
r_plate = R_PACK + BARREL_OD / 2 + PLATE_RIM
hub_r = max(6.0, R_PACK - BARREL_OD / 2 - 4.0)


def barrel_plate(z0, z1, od_r):
    disc = Part.makeCylinder(od_r, z1 - z0, V(0, 0, z0))
    for k in range(N):
        a = math.radians(k * 60.0)
        bx, by = R_PACK * math.cos(a), R_PACK * math.sin(a)
        disc = disc.cut(Part.makeCylinder(
            BARREL_OD / 2 + 0.35, (z1 - z0) + 4.0, V(bx, by, z0 - 2.0)))
    disc = disc.cut(Part.makeCylinder(hub_r, (z1 - z0) + 4.0, V(0, 0, z0 - 2.0)))
    return disc.removeSplitter()


front_plate = barrel_plate(z_front0, z_front1, r_plate)
rear_plate = barrel_plate(z_rear0, z_rear1, r_plate)
breech_casing = tube(2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1)
cascabel = Part.makeCylinder(r_case_od, 6.0, V(0, 0, z_case0 - 6.0))
cascabel = cascabel.cut(Part.makeCylinder(hub_r + 2.0, 12.0, V(0, 0, z_case0 - 8.0)))
# Cam sits inside / through cascabel — cut casing bore for drum.
breech_casing = breech_casing.fuse(cascabel).cut(
    G.cyl(cam_od + 1.0, z_cam0 - 2, z_cam1 + 2)).removeSplitter()

# --- feed hopper into LOAD window (φ ≈ 180°) ---------------------------------
# Funnel above the open breech at φ=180, feeding +Y (radial out).
feed_ang = 180.0
a180 = math.radians(feed_ang)
ux, uy = math.cos(a180), math.sin(a180)
# World position of station axis.
sx, sy = R_PACK * ux, R_PACK * uy
# Radial-out unit = (ux, uy). Hopper sits outside casing on that ray.
z_feed = z_stop - BENCH_STROKE / 2
hop_r0 = r_case_od + 2.0
hop_r1 = hop_r0 + 45.0
# Simple hopper: truncated box funnel toward breech mouth.
hop_outer = Part.makeBox(40.0, hop_r1 - hop_r0, 50.0,
                         V(-20.0, hop_r0, z_feed - 25.0))
hop_inner = Part.makeBox(28.0, hop_r1 - hop_r0 + 2.0, 36.0,
                         V(-14.0, hop_r0 - 1.0, z_feed - 18.0))
hopper_local = hop_outer.cut(hop_inner).removeSplitter()
# Orient local +Y to world radial-out at 180° (same as place_shape).
hopper = hopper_local.copy()
hopper.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(ux, uy)))
hopper.translate(V(sx, sy, 0))
# Pellet in the open LOAD station cradle.
pellet = place_shape(
    Part.makeSphere(PELLET_D / 2, V(0, 0, (z_tip + PELLET_D / 2) - BENCH_STROKE)),
    R_PACK, feed_ang)

# --- crank (fixed cam → crank turns the PACK; draw handle on pack shaft) -----
# Sketch: shaft through cam ID, crank arm aft of cascabel, knob.
shaft = G.cyl(10.0, z_cam0 - 40.0, z_cam1 + 5.0)
arm = Part.makeBox(8.0, 70.0, 10.0, V(-4.0, 0.0, z_cam0 - 35.0))
knob = Part.makeSphere(14.0, V(0.0, 70.0, z_cam0 - 30.0))
crank = shaft.fuse(arm).fuse(knob).removeSplitter()

# --- hose stubs: hub → AirTAC R (supply); AirTAC A → pilot fitting ------------
hose_r = 2.0
hoses = []
# Hub ring at cam aft (MQR stand-in).
hub_hose = G.cyl(16.0, z_cam0 - 8.0, z_cam0 - 2.0)
for k in range(N):
    ang = k * 60.0
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    # AirTAC R port in local station frame, then place at ang with stroke.
    dz = cam_dz(ang)
    # R fitting tip roughly at (0, vent_y+T+stick, z_stem+ports[R]) local, then −Y out.
    # After place_shape, approximate port world pos from station axis.
    # Local vent center (0, vent_y + T/2, zR); R sticks +Y local → radial out.
    zR = z_stem + AIRTAC["ports"]["R"] + dz
    zA = z_stem + AIRTAC["ports"]["A"] + dz
    # Build short hose from hub to near AirTAC R (polyline).
    p0 = V(6.0 * ux, 6.0 * uy, z_cam0 - 5.0)
    # Station axis world.
    p_ax = V(R_PACK * ux, R_PACK * uy, zR)
    # Radial-in offset to AirTAC (local −Y → toward axis): vent sits at RAIL_Y-ish.
    # After place, local (0, vent_y) → radius R_PACK + vent_y (vent_y<0).
    r_vent = R_PACK + vent_y + AIRTAC["T"] / 2
    p1 = V(r_vent * ux, r_vent * uy, zR)
    # Hose as cylinder between p0 and p1.
    vec = p1.sub(p0)
    L = vec.Length
    if L > 1.0:
        h = Part.makeCylinder(hose_r, L, p0, vec)
        hoses.append(h)
    # Pilot stub: short run from A (radial in side) toward rear plug pilot fitting.
    pA = V(r_vent * ux, r_vent * uy, zA)
    pP = V(R_PACK * ux, R_PACK * uy, z_ry + dz - 5.0)
    vec2 = pP.sub(pA)
    L2 = vec2.Length
    if L2 > 1.0:
        hoses.append(Part.makeCylinder(hose_r * 0.8, L2, pA, vec2))
hoses_s = Part.makeCompound(hoses) if hoses else hub_hose
hoses_s = hoses_s.fuse(hub_hose).removeSplitter()

# --- assembly / report -------------------------------------------------------
pack = Part.makeCompound(stations)
assembly = Part.makeCompound([
    pack, cam, front_plate, rear_plate, breech_casing,
    hopper, pellet, crank, hoses_s,
])
bb = assembly.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
case_od = 2.0 * r_case_od
closed_L = (z_stop + BARREL_SHOW) - Z_AFT_CLIP
pack_moved = (abs(CASE_CLEAR_USE - CASE_CLEAR) > 1e-6
              or abs(case_od - 172.0) > 0.6
              or abs(R_PACK - R_PACK_START) > 0.05)

checks = [
    ("bench stroke %.1f mm" % BENCH_STROKE,
     abs(BENCH_STROKE - 65.8) < 0.05),
    ("FIRE u(0)=0", abs(cam_u(0.0)) < 1e-9),
    ("LOAD u(180)=1", abs(cam_u(180.0) - 1.0) < 1e-9),
    ("OPEN mid u(75)≈0.5", abs(cam_u(75.0) - 0.5) < 0.05),
    ("cam drum solid", cam.Volume > 1e3),
    ("groove cut (drum hollowed)", cam.Volume < cam_drum.Volume - 100),
    ("neighbour core gap %.2f >= %.2f" % (gap_core, CLEAR), neighbours_ok),
    ("one-station rails/ears clear of cam", rail_cam_ok),
    ("QEV inside casing ID (clear bumped ok)", case_ok),
    ("six phases", len(stations) == 6),
    ("closed station L %.1f ≈ 750" % closed_L, abs(closed_L - TARGET_L) <= 0.6),
    ("hopper solid", hopper.Volume > 500),
    ("crank solid", crank.Volume > 500),
    ("hoses solid", hoses_s.Volume > 100),
    ("no full-length tube (casing << tip)", z_case1 < z_tip_b - 200.0),
]
report = [
    NAME,
    "  sketch                 : mechanism on breech_pack numbers (NOT frozen)",
    "  stroke (bench)         : %.1f mm; closed dz=0; open dz=−%.1f"
    % (BENCH_STROKE, BENCH_STROKE),
    "  law                    : FIRE 330–30° u=0; OPEN 30–120°; LOAD 120–240° u=1; "
    "CLOSE 240–330°",
    "  cam                    : fixed cylinder Ø%.1f groove R=%.1f; follower Ø%.1f"
    % (cam_od, CAM_R, FOLLOWER_OD),
    "  pack R                 : %.2f (start %.2f)%s"
    % (R_PACK, R_PACK_START, " — MOVED for cam" if abs(R_PACK - R_PACK_START) > 0.05 else ""),
    "  casing Ø               : %.1f (CLEAR %.2f; start 172 / 0.5)%s"
    % (case_od, CASE_CLEAR_USE, " — MOVED" if pack_moved else ""),
    "  neighbour gap          : %.2f mm" % gap_core,
]
for n in probe_notes:
    report.append("  probe                 : " + n)
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  feed                  : hopper at φ=180° LOAD window",
    "  crank                 : aft shaft + arm (turns pack; cam fixed)",
    "  hoses                 : hub→AirTAC R; A→pilot stub (ports as on station)",
    "  overall LxWxH         : %.0f x %.0f x %.0f mm" % (gun_L, gun_W, gun_H),
    "  not drawn             : wheeled carriage, full-length shroud, real MQR body",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["ph0"] = ((0.92, 0.40, 0.16), 32)
FV.STYLES["ph1"] = ((0.85, 0.55, 0.30), 40)
FV.STYLES["ph2"] = ((0.55, 0.65, 0.55), 45)
FV.STYLES["ph3"] = ((0.30, 0.62, 0.75), 38)
FV.STYLES["ph4"] = ((0.60, 0.58, 0.50), 45)
FV.STYLES["ph5"] = ((0.88, 0.48, 0.28), 40)
FV.STYLES["plate"] = ((0.42, 0.44, 0.48), 8)
FV.STYLES["casing"] = ((0.78, 0.72, 0.55), 80)
FV.STYLES["cam"] = ((0.35, 0.38, 0.42), 15)
FV.STYLES["feed"] = ((0.55, 0.50, 0.40), 50)
FV.STYLES["pellet"] = ((0.88, 0.88, 0.92), 15)
FV.STYLES["crank"] = ((0.25, 0.25, 0.28), 10)
FV.STYLES["hose"] = ((0.20, 0.55, 0.45), 35)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Cam", "Cam_drum", cam, "cam")
sc.add("Skin", "Front_barrel_plate", front_plate, "plate")
sc.add("Skin", "Rear_barrel_plate", rear_plate, "plate")
sc.add("Skin", "Breech_casing", breech_casing, "casing")
sc.add("Feed", "Hopper", hopper, "feed")
sc.add("Feed", "Pellet_load", pellet, "pellet")
sc.add("Drive", "Crank", crank, "crank")
sc.add("Hoses", "Pilot_supply_stubs", hoses_s, "hose")

for n, ang, u, dz, tag in phases:
    a = math.radians(ang)
    sc.label("Labels", "%d° %s" % (ang, tag),
             ((R_PACK + 60) * math.cos(a), (R_PACK + 60) * math.sin(a),
              z_stop + cam_dz(ang)))
sc.label("Labels", "stroke %.0f mm · cam fixed" % BENCH_STROKE,
         (0, bb.YMax + 35, (bb.ZMin + bb.ZMax) / 2))

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

# Phase focus helpers for render_view (hide other stations).
for k, ang, u, dz, tag in phases:
    with open(os.path.join(OUT_DIR, "phase_%03d.txt" % int(ang)), "w") as f:
        f.write("Station_%d_%d\n" % (k, int(ang)))

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech mechanism has [FAIL] checks")
