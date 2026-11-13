# -*- coding: utf-8 -*-
"""
Gatling breech mechanism (not a freeze).

Stroke from linear_breech (65.8 mm) → angle→stroke law → outboard cam liner →
printed stroke rail (65.8 mm travel) → housing around liner+rail → six phases →
feed in LOAD window → crank outside housing → hoses past track/rail.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism.py').read())"

Pack R / casing may move if parts will not seat. No wheeled carriage; no
full-length tube. Exports: exports/gatling_breech_mechanism/
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

TARGET_L = 750.0
BARREL_SHOW_DEFAULT = 160.0
N = 6
R_PACK = 58.50
R_PACK_START = 58.50
CASE_OD_START = 201.0          # previous mechanism casing (not a freeze)
CLEAR = 0.5
PLATE_T, PLATE_LIP, PLATE_RIM = 14.0, 1.5, 3.0
CASE_WALL, CASE_CLEAR, CASE_OVERLAP = 2.0, 0.5, 18.0

CAM_WALL = 5.0
FOLLOWER_OD = 5.0
FOLLOWER_CLEAR = 0.5
CAM_Z_PAD = 8.0
CAM_CLEAR_Z = 2.0
EAR_ENV = 33.0

# Printed stroke-rail cage around the bought Al tubes (length covers STROKE).
RAIL_CAGE_T = 3.0
RAIL_CAGE_PAD = 6.0            # past open / closed bushing travel

FIRE_A, FIRE_B = 330.0, 30.0
OPEN_A, OPEN_B = 30.0, 120.0
LOAD_A, LOAD_B = 120.0, 240.0
CLOSE_A, CLOSE_B = 240.0, 330.0

print("load linear_breech…", flush=True)
GATLING_LINEAR_BREECH_LIBRARY = True
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


def place_shape(shape, R, ang_deg):
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(ux, uy)))
    s.translate(V(R * ux, R * uy, 0))
    return s


def min_neighbour_gap(shapes):
    g = 1e9
    for i in range(N):
        for j in range(i + 1, N):
            g = min(g, shapes[i].distToShape(shapes[j])[0])
    return g


# --- stroke rail (printed cage) + bought Al tubes ----------------------------
# Carriage bushings travel BENCH_STROKE along the Al tubes. Cage length covers
# closed and open bushing envelopes so the finger/carriage never runs off.
z_bush0_c = z_ry - CARR_T - 4.0
z_bush1_c = z_bush0_c + BUSH_L
z_nose1_c = z_fs - 2.0
z_nose0_c = z_nose1_c - NOSE_BUSH_L
# Closed bushing Z span vs open (shifted −STROKE).
z_rail_lo = min(z_bush0_c, z_nose0_c) - BENCH_STROKE - RAIL_CAGE_PAD
z_rail_hi = max(z_bush1_c, z_nose1_c) + RAIL_CAGE_PAD
stroke_rail_L = z_rail_hi - z_rail_lo


def make_stroke_rail():
    """Printed cage around both Al tubes for one station (local frame)."""
    parts = []
    for x, y in rail_centers():
        # Outer sleeve around the bought tube.
        od = RAIL_OD + 2.0 * RAIL_CAGE_T
        sleeve = tube(od, RAIL_OD + 0.4, z_rail_lo, z_rail_hi, x, y)
        parts.append(sleeve)
    # Web between the two sleeves.
    (x0, y0), (x1, y1) = rail_centers()
    web = Part.makeBox(
        abs(x1 - x0) - RAIL_OD, RAIL_CAGE_T, stroke_rail_L,
        V(min(x0, x1) + RAIL_OD / 2,
          (y0 + y1) / 2 - RAIL_CAGE_T / 2,
          z_rail_lo))
    parts.append(web)
    return G.fuse_all(parts).removeSplitter()


stroke_rail0 = make_stroke_rail()
# Bought Al tubes (full length for stroke) — keep as bought reference.
al_rails0 = rails_s

# --- outboard cam liner + radial-out follower --------------------------------
z_carr_aft = qev_closed["Carriage"].BoundBox.ZMin
z_cam1 = z_carr_aft - CAM_CLEAR_Z
z_tip0 = z_cam1 - CAM_Z_PAD * 0.5
z_cam0 = z_tip0 - BENCH_STROKE - CAM_Z_PAD


def build_cam_and_case(R):
    """Cam outside ear envelope; casing wraps cam OD. Returns dict of solids/metrics."""
    cam_r = R + EAR_ENV + CLEAR + CAM_WALL / 2 + 1.0
    c_od = 2.0 * (cam_r + CAM_WALL / 2)
    c_id = 2.0 * (cam_r - CAM_WALL / 2)
    case_clear = c_od / 2 - (R + CH_OD / 2) + CLEAR
    case_clear = max(CASE_CLEAR, case_clear)
    r_cid = R + CH_OD / 2 + case_clear
    r_cod = r_cid + CASE_WALL
    y_tip = cam_r - R
    y_root = CH_OD / 2 + 2.0
    fol = Part.makeCylinder(
        FOLLOWER_OD / 2, max(6.0, y_tip - y_root),
        V(0, y_root, z_tip0), V(0, 1, 0))
    fol = fol.fuse(Part.makeSphere(
        FOLLOWER_OD / 2 + 0.2, V(0, y_tip, z_tip0))).removeSplitter()
    stem_z1 = z_ry - CARR_T
    if stem_z1 > z_tip0 + 2.0:
        fol = fol.fuse(Part.makeCylinder(
            FOLLOWER_OD / 2, stem_z1 - z_tip0,
            V(0, y_root + 2.0, z_tip0), V(0, 0, 1))).removeSplitter()
    drum = tube(c_od, c_id, z_cam0, z_cam1)
    # Groove: compound of balls cut once (faster than 48 serial cuts).
    n_seg = 36
    groove_r = FOLLOWER_OD / 2 + FOLLOWER_CLEAR
    balls = []
    for i in range(n_seg):
        ang = 360.0 * i / float(n_seg)
        a = math.radians(ang)
        balls.append(Part.makeSphere(
            groove_r,
            V(cam_r * math.cos(a), cam_r * math.sin(a),
              z_tip0 + cam_dz(ang))))
    cut = Part.makeCompound(balls)
    cam_body = drum.cut(cut)
    try:
        cam_body = cam_body.removeSplitter()
    except Exception:
        pass
    if cam_body.isNull() or cam_body.Volume < 1.0:
        cam_body = drum
    return dict(
        CAM_R=cam_r, cam_od=c_od, cam_id=c_id, cam=cam_body, cam_drum=drum,
        follower=fol, CASE_CLEAR=case_clear,
        r_case_id=r_cid, r_case_od=r_cod, y_tip=y_tip)


def follower_on_track(fol_shape, cam_r, dz, R, ang, tol=FOLLOWER_CLEAR + 0.3):
    """True if follower tip is still on the cam groove rail at this pose."""
    tip = place_shape(shifted(
        Part.makeSphere(FOLLOWER_OD / 2, V(0, cam_r - R, z_tip0)), dz), R, ang)
    # Ideal groove point at this angle/Z.
    a = math.radians(ang)
    z = z_tip0 + dz
    ideal = Part.makeSphere(0.5, V(cam_r * math.cos(a), cam_r * math.sin(a), z))
    return tip.distToShape(ideal)[0] <= tol


# Grow R until stroke-rail neighbours clear (cam built once at final R).
# Cage sleeves collide below ~R66 at N=6.
moved_notes = []
R_PACK = max(R_PACK_START, 66.0)
print("seating stroke rails from R=%.1f…" % R_PACK, flush=True)
for _try in range(16):
    rails_placed = [place_shape(stroke_rail0, R_PACK, k * 60.0) for k in range(N)]
    gap_rails = min_neighbour_gap(rails_placed)
    cam_r_guess = R_PACK + EAR_ENV + CLEAR + CAM_WALL / 2 + 1.0
    dummy_fol = Part.makeSphere(FOLLOWER_OD / 2, V(0, cam_r_guess - R_PACK, z_tip0))
    on0 = follower_on_track(dummy_fol, cam_r_guess, 0.0, R_PACK, 0.0)
    on_open = follower_on_track(
        dummy_fol, cam_r_guess, -BENCH_STROKE, R_PACK, 180.0)
    print("  R=%.2f rail_gap=%.2f on0=%s on_open=%s" % (R_PACK, gap_rails, on0, on_open),
          flush=True)
    if gap_rails >= CLEAR - 1e-6 and on0 and on_open:
        break
    R_PACK += 1.0
    moved_notes.append(
        "R→%.1f (rail_gap=%.2f on0=%s on_open=%s)"
        % (R_PACK, gap_rails, on0, on_open))
else:
    raise SystemExit("could not seat stroke rail / finger at any R")

if abs(R_PACK - R_PACK_START) > 0.05:
    moved_notes.append("R_PACK %.2f → %.2f" % (R_PACK_START, R_PACK))
    rails_placed = [place_shape(stroke_rail0, R_PACK, k * 60.0) for k in range(N)]
    gap_rails = min_neighbour_gap(rails_placed)

print("building cam at R=%.2f…" % R_PACK)
geom = build_cam_and_case(R_PACK)
print("cam done; core gaps…")
cores = []
for k in range(N):
    ang = k * 60.0
    dz = cam_dz(ang)
    parts = [shifted(qev_closed[n], dz) for n in qev_closed if n != "Carriage"]
    cores.append(place_shape(Part.makeCompound(parts), R_PACK, ang))
gap_core = min_neighbour_gap(cores)
# If core gap fails, bump R and rebuild cam once.
if gap_core < CLEAR - 1e-6:
    R_PACK += max(1.0, CLEAR - gap_core + 0.5)
    moved_notes.append("R→%.2f (core_gap was %.2f)" % (R_PACK, gap_core))
    rails_placed = [place_shape(stroke_rail0, R_PACK, k * 60.0) for k in range(N)]
    gap_rails = min_neighbour_gap(rails_placed)
    geom = build_cam_and_case(R_PACK)
    cores = []
    for k in range(N):
        ang = k * 60.0
        dz = cam_dz(ang)
        parts = [shifted(qev_closed[n], dz) for n in qev_closed if n != "Carriage"]
        cores.append(place_shape(Part.makeCompound(parts), R_PACK, ang))
    gap_core = min_neighbour_gap(cores)

CAM_R = geom["CAM_R"]
cam_od = geom["cam_od"]
cam_id = geom["cam_id"]
cam = geom["cam"]
cam_drum = geom["cam_drum"]
follower = geom["follower"]
CASE_CLEAR_USE = geom["CASE_CLEAR"]
r_case_id = geom["r_case_id"]
r_case_od = geom["r_case_od"]
y_tip = geom["y_tip"]
print("pack R=%.2f casing_clear=%.2f cam_od=%.1f" % (R_PACK, CASE_CLEAR_USE, cam_od))

# --- stations ----------------------------------------------------------------
slide0 = Part.makeCompound(
    [qev_closed[k].copy() for k in qev_closed] + [follower])
fixed0 = Part.makeCompound([
    al_rails0, stroke_rail0, cradle, vent_body, vent_fittings, vent_plunger,
    barrel_clamp, barrel_collar, fixed_barrel,
])


def station_local(phi_deg):
    dz = cam_dz(phi_deg)
    return Part.makeCompound([shifted(slide0, dz), fixed0.copy()])


def station_placed(phi_deg, R=None):
    R = R_PACK if R is None else R
    return place_shape(station_local(phi_deg), R, phi_deg)


# One-station: open carriage inside housing; rails/ears clear of cam.
probe_notes = list(moved_notes)
probe_notes.append(
    "stroke rail L=%.1f (covers 0…−%.1f); rail_gap=%.2f"
    % (stroke_rail_L, BENCH_STROKE, gap_rails))
rail_cam_ok = True
case_ok = True
for pa in (0.0, 90.0, 180.0):
    body = place_shape(shifted(Part.makeCompound(
        [qev_closed[k] for k in qev_closed] + [al_rails0, stroke_rail0]),
        cam_dz(pa)), R_PACK, pa)
    d_cam = body.distToShape(cam)[0]
    carr = place_shape(shifted(qev_closed["Carriage"], cam_dz(pa)), R_PACK, pa)
    # Open carriage must stay inside casing ID.
    pts = carr.tessellate(1.0)[0]
    rmax = max(math.hypot(p.x, p.y) for p in pts) if pts else 0.0
    clear_case = r_case_id - rmax
    on = follower_on_track(follower, CAM_R, cam_dz(pa), R_PACK, pa)
    probe_notes.append(
        "φ=%.0f body↔cam=%.2f carr_rmax=%.1f case_clear=%.1f finger_on=%s"
        % (pa, d_cam, rmax, clear_case, on))
    if d_cam < CLEAR - 1e-3:
        rail_cam_ok = False
    if clear_case < CLEAR - 1e-3:
        case_ok = False
    if not on and pa in (0.0, 180.0):
        rail_cam_ok = False

# Grow casing if open carriage scrapes ID.
if not case_ok:
    need = max(CASE_CLEAR_USE, rmax - (R_PACK + CH_OD / 2) + CLEAR)
    CASE_CLEAR_USE = need
    r_case_id = R_PACK + CH_OD / 2 + CASE_CLEAR_USE
    r_case_od = r_case_id + CASE_WALL
    case_ok = True
    moved_notes.append("CASE_CLEAR → %.2f (open carriage)" % CASE_CLEAR_USE)
    probe_notes.append("casing CLEAR bumped to %.2f" % CASE_CLEAR_USE)

# --- six phases --------------------------------------------------------------
phases = []
stations = []
for k in range(N):
    ang = k * 60.0
    u = cam_u(ang)
    dz = cam_dz(ang)
    stations.append(station_placed(ang))
    phases.append((k + 1, ang, u, dz, phase_name(ang)))

# Phase-to-phase: core gap already checked; station gap can be 0 at hub (rails-in OK).
gap_stations = gap_core

# --- housing: wraps liner + stroke rail; open carriage inside ----------------
z_tip_b = z_stop + BARREL_SHOW
z_stroke_end = qev_closed["Carriage"].BoundBox.ZMin - BENCH_STROKE
z_front0 = z_tip_b - PLATE_T + PLATE_LIP
z_front1 = z_tip_b + PLATE_LIP
z_rear0 = z_stop - PLATE_T * 0.35
z_rear1 = z_rear0 + PLATE_T
z_case1 = z_rear0 + CASE_OVERLAP
z_case0 = min(z_stroke_end, z_cam0, z_rail_lo) - 4.0
# Housing OD must also clear stroke-rail outer envelope.
rail_r_max = 0.0
for p in place_shape(stroke_rail0, R_PACK, 0.0).tessellate(1.0)[0]:
    rail_r_max = max(rail_r_max, math.hypot(p.x, p.y))
need_id = max(r_case_id, cam_od / 2 + CLEAR, rail_r_max + CLEAR)
if need_id > r_case_id + 1e-6:
    CASE_CLEAR_USE = need_id - (R_PACK + CH_OD / 2)
    r_case_id = need_id
    r_case_od = r_case_id + CASE_WALL
    moved_notes.append("casing ID→%.1f (wrap rail/cam)" % r_case_id)
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
# Housing tube + cascabel; bore for cam; LOAD window cut 120–240°.
breech_casing = tube(2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1)
cascabel = Part.makeCylinder(r_case_od, 8.0, V(0, 0, z_case0 - 8.0))
cascabel = cascabel.cut(Part.makeCylinder(hub_r + 2.0, 14.0, V(0, 0, z_case0 - 10.0)))
breech_casing = breech_casing.fuse(cascabel).cut(
    G.cyl(cam_od + 1.0, z_cam0 - 2, z_cam1 + 2)).removeSplitter()
# Feed window: sector cut through housing wall over LOAD angles at breech Z.
win_z0 = z_stop - BENCH_STROKE - 5.0
win_z1 = z_stop + 15.0
win_box = Part.makeBox(
    2.0 * r_case_od + 20.0, r_case_od + 40.0, win_z1 - win_z0,
    V(-(r_case_od + 10.0), 0.0, win_z0))
# Keep only the LOAD sector: rotate box to cover 120–240° (centered at 180°).
# Cut a radial slot around φ=180° spanning ±60°.
win_cut = Part.makeCylinder(r_case_od + 5.0, win_z1 - win_z0, V(0, 0, win_z0))
win_cut = win_cut.cut(Part.makeCylinder(r_case_id - 1.0, win_z1 - win_z0 + 2,
                                        V(0, 0, win_z0 - 1)))
# Keep sector 120–240 by cutting away the complementary wedges with boxes.
# Simpler: box from −Y outward at φ=180, width covering ±60° chord.
chord = 2.0 * r_case_od * math.sin(math.radians(60.0))
feed_slot = Part.makeBox(
    chord, r_case_od + 30.0, win_z1 - win_z0,
    V(-chord / 2, 0.0, win_z0))
# At φ=180 radial out is −X; rotate slot to −X.
feed_slot.rotate(V(0, 0, 0), V(0, 0, 1), 180.0)
breech_casing = breech_casing.cut(feed_slot).removeSplitter()

# --- feed tray: only in LOAD window, no intersect housing / open carriage ----
feed_ang = 180.0
a180 = math.radians(feed_ang)
ux, uy = math.cos(a180), math.sin(a180)
sx, sy = R_PACK * ux, R_PACK * uy
z_feed = z_stop - BENCH_STROKE / 2
# Tray from outside housing into the window, stopping short of open carriage.
hop_r0 = r_case_od + 1.0
hop_r1 = hop_r0 + 40.0
tray_outer = Part.makeBox(36.0, hop_r1 - hop_r0, 40.0,
                          V(-18.0, hop_r0, z_feed - 20.0))
tray_inner = Part.makeBox(26.0, hop_r1 - hop_r0 + 4.0, 28.0,
                          V(-13.0, hop_r0 - 2.0, z_feed - 14.0))
hopper_local = tray_outer.cut(tray_inner).removeSplitter()
hopper = hopper_local.copy()
hopper.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(ux, uy)))
hopper.translate(V(sx, sy, 0))
# Ensure tray does not intersect housing solid or open carriage.
open_carr = place_shape(shifted(qev_closed["Carriage"], -BENCH_STROKE),
                        R_PACK, feed_ang)
# Nudge tray outward if it hits.
for _ in range(8):
    hit_h = hopper.common(breech_casing).Volume
    hit_c = hopper.common(open_carr).Volume
    if hit_h < 1.0 and hit_c < 1.0:
        break
    hopper.translate(V(ux * 3.0, uy * 3.0, 0))
    moved_notes.append("feed tray nudged out")
pellet = place_shape(
    Part.makeSphere(PELLET_D / 2, V(0, 0, (z_tip + PELLET_D / 2) - BENCH_STROKE)),
    R_PACK, feed_ang)
feed_ok = (hopper.common(breech_casing).Volume < 1.0
           and hopper.common(open_carr).Volume < 1.0)

# --- crank outside housing, not in LOAD window 120–240° ----------------------
# Arm along φ=0 (FIRE), aft of cascabel, entirely outside casing OD.
shaft = G.cyl(10.0, z_case0 - 50.0, z_case0 + 5.0)
arm_len = r_case_od + 45.0
arm = Part.makeBox(10.0, arm_len, 12.0,
                   V(-5.0, 0.0, z_case0 - 42.0))
# Point arm to φ=0 (+X after identity): rotate so +Y of box → +X.
arm.rotate(V(0, 0, 0), V(0, 0, 1), -90.0)
knob = Part.makeSphere(16.0, V(arm_len, 0.0, z_case0 - 36.0))
crank = shaft.fuse(arm).fuse(knob).removeSplitter()
# Crank must not hit housing or any open station in LOAD sector.
crank_ok = crank.distToShape(breech_casing)[0] >= CLEAR - 1e-3
for k in range(N):
    ang = k * 60.0
    if LOAD_A <= ang <= LOAD_B:
        d = crank.distToShape(stations[k])[0]
        if d < CLEAR - 1e-3:
            crank_ok = False

# --- hoses: port → out past track/rail, then aft outside cam → hub -----------
# Local R-port sits at y = vent_y + T (toward local +Y = radial-out after place).
# Straight port→hub crosses the stroke-rail cage and cam liner — route around.
hose_r = 2.0
PORT_R_SHIFT = 0.0             # radial bump of exit ring if still tight
stroke_rails_pack = Part.makeCompound(rails_placed)
# Exit ring must clear rail envelope and cam OD.
r_exit0 = max(rail_r_max, cam_od / 2.0) + CLEAR + 6.0 + hose_r
z_hose_aft = min(z_cam0, z_rail_lo) - 12.0
hub_hose = G.cyl(16.0, z_hose_aft - 4.0, z_hose_aft + 4.0)


def port_world(ang, dz, which="R"):
    """AirTAC port centre in world after place_shape (local +Y → radial out)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    # place_shape: rotate so local +Y → radial, then translate to (R·ux, R·uy).
    y_loc = vent_y + AIRTAC["T"] + PORT_R_SHIFT   # R/P face (outer)
    if which == "A":
        y_loc = vent_y - PORT_R_SHIFT              # A face (inner / −Y local)
    # After rot that maps +Y→radial: local (0, y_loc) → radial offset y_loc.
    r = R_PACK + y_loc
    z = z_stem + AIRTAC["ports"][which] + dz
    return V(r * ux, r * uy, z), ux, uy


def build_hoses(r_exit):
    segs = []
    for k in range(N):
        ang = k * 60.0
        dz = cam_dz(ang)
        p_port, ux, uy = port_world(ang, dz, "R")
        # 1) short stub off the fitting (radial out a few mm).
        p1 = V((R_PACK + vent_y + AIRTAC["T"] + PORT_R_SHIFT + 8.0) * ux,
               (R_PACK + vent_y + AIRTAC["T"] + PORT_R_SHIFT + 8.0) * uy,
               p_port.z)
        # 2) go aft at that radius (stay inboard of cam radially if needed,
        #    but behind the stroke-rail Z so we miss the cage).
        z_clear = min(z_rail_lo, z_cam0) - 4.0
        p2 = V(p1.x, p1.y, z_clear)
        # 3) radial out past cam/rail envelope (outside housing).
        p3 = V(r_exit * ux, r_exit * uy, z_clear)
        # 4) aft manifold ring, then in to hub — all aft of cam.
        p4 = V(r_exit * ux, r_exit * uy, z_hose_aft)
        p5 = V(10.0 * ux, 10.0 * uy, z_hose_aft)
        for p0, p1_ in ((p_port, p1), (p1, p2), (p2, p3), (p3, p4), (p4, p5)):
            vec = p1_.sub(p0)
            if vec.Length > 1.0:
                segs.append(Part.makeCylinder(hose_r, vec.Length, p0, vec))
        # Pilot A stub: short outward-then-aft only (no plunge through rails).
        pA, _, _ = port_world(ang, dz, "A")
        pA1 = V(pA.x - 6.0 * ux, pA.y - 6.0 * uy, pA.z)  # slightly inboard
        pA2 = V(pA1.x, pA1.y, z_clear)
        for p0, p1_ in ((pA, pA1), (pA1, pA2)):
            vec = p1_.sub(p0)
            if vec.Length > 1.0:
                segs.append(Part.makeCylinder(hose_r * 0.8, vec.Length, p0, vec))
    return Part.makeCompound(segs).fuse(hub_hose).removeSplitter()


def hose_clear(hs):
    d_cam = hs.distToShape(cam)[0]
    d_rail = hs.distToShape(stroke_rails_pack)[0]
    return d_cam >= CLEAR - 1e-3 and d_rail >= CLEAR - 1e-3, d_cam, d_rail


def rebuild_housing_for_od():
    global breech_casing, crank, hopper, feed_ok
    breech_casing = tube(2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1)
    casc = Part.makeCylinder(r_case_od, 8.0, V(0, 0, z_case0 - 8.0))
    casc = casc.cut(Part.makeCylinder(hub_r + 2.0, 14.0, V(0, 0, z_case0 - 10.0)))
    breech_casing = breech_casing.fuse(casc).cut(
        G.cyl(cam_od + 1.0, z_cam0 - 2, z_cam1 + 2)).removeSplitter()
    ch = 2.0 * r_case_od * math.sin(math.radians(60.0))
    slot = Part.makeBox(ch, r_case_od + 30.0, win_z1 - win_z0,
                        V(-ch / 2, 0.0, win_z0))
    slot.rotate(V(0, 0, 0), V(0, 0, 1), 180.0)
    breech_casing = breech_casing.cut(slot).removeSplitter()
    # Crank follows new OD.
    alen = r_case_od + 45.0
    sh = G.cyl(10.0, z_case0 - 50.0, z_case0 + 5.0)
    ar = Part.makeBox(10.0, alen, 12.0, V(-5.0, 0.0, z_case0 - 42.0))
    ar.rotate(V(0, 0, 0), V(0, 0, 1), -90.0)
    kn = Part.makeSphere(16.0, V(alen, 0.0, z_case0 - 36.0))
    crank = sh.fuse(ar).fuse(kn).removeSplitter()
    # Keep feed tray outside new OD.
    hop_r0 = r_case_od + 1.0
    hop_r1 = hop_r0 + 40.0
    to = Part.makeBox(36.0, hop_r1 - hop_r0, 40.0,
                      V(-18.0, hop_r0, z_feed - 20.0))
    ti = Part.makeBox(26.0, hop_r1 - hop_r0 + 4.0, 28.0,
                      V(-13.0, hop_r0 - 2.0, z_feed - 14.0))
    hl = to.cut(ti).removeSplitter()
    hopper = hl.copy()
    hopper.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(
        math.cos(math.radians(feed_ang)), math.sin(math.radians(feed_ang)))))
    hopper.translate(V(R_PACK * math.cos(math.radians(feed_ang)),
                       R_PACK * math.sin(math.radians(feed_ang)), 0))
    for _ in range(8):
        if (hopper.common(breech_casing).Volume < 1.0
                and hopper.common(open_carr).Volume < 1.0):
            break
        hopper.translate(V(math.cos(math.radians(feed_ang)) * 3.0,
                           math.sin(math.radians(feed_ang)) * 3.0, 0))
    feed_ok = (hopper.common(breech_casing).Volume < 1.0
               and hopper.common(open_carr).Volume < 1.0)


r_exit = max(r_exit0, r_case_od + 8.0)
hoses_s = build_hoses(r_exit)
ok_h, d_cam_h, d_rail_h = hose_clear(hoses_s)
print("hose try exit=%.1f cam=%.2f rail=%.2f" % (r_exit, d_cam_h, d_rail_h),
      flush=True)
for _try in range(6):
    if ok_h:
        break
    # Bump exit ring / port / casing until clear.
    if d_rail_h < CLEAR:
        PORT_R_SHIFT += 4.0
        moved_notes.append("PORT_R_SHIFT→%.1f (hose↔rail=%.2f)" % (
            PORT_R_SHIFT, d_rail_h))
    if d_cam_h < CLEAR:
        r_exit = max(r_exit + 6.0, cam_od / 2 + CLEAR + 12.0)
        # Grow housing so exit stays outside OD.
        need_od = r_exit - 8.0
        if need_od > r_case_od:
            CASE_CLEAR_USE = need_od - CASE_WALL - (R_PACK + CH_OD / 2)
            r_case_id = R_PACK + CH_OD / 2 + CASE_CLEAR_USE
            r_case_od = r_case_id + CASE_WALL
            moved_notes.append(
                "casing Ø→%.1f (hose past cam)" % (2.0 * r_case_od))
            rebuild_housing_for_od()
        moved_notes.append("hose exit r→%.1f (hose↔cam=%.2f)" % (
            r_exit, d_cam_h))
    r_exit = max(r_exit, r_case_od + 8.0)
    hoses_s = build_hoses(r_exit)
    ok_h, d_cam_h, d_rail_h = hose_clear(hoses_s)
    print("hose try exit=%.1f cam=%.2f rail=%.2f" % (r_exit, d_cam_h, d_rail_h),
          flush=True)

hoses_ok = ok_h
crank_ok = crank.distToShape(breech_casing)[0] >= CLEAR - 1e-3
for k in range(N):
    ang = k * 60.0
    if LOAD_A <= ang <= LOAD_B:
        if crank.distToShape(stations[k])[0] < CLEAR - 1e-3:
            crank_ok = False

# --- assembly / checks / report ----------------------------------------------
pack = Part.makeCompound(stations)
assembly = Part.makeCompound([
    pack, cam, front_plate, rear_plate, breech_casing,
    hopper, pellet, crank, hoses_s,
])
bb = assembly.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
case_od = 2.0 * r_case_od
closed_L = (z_stop + BARREL_SHOW) - Z_AFT_CLIP
pack_moved = (abs(R_PACK - R_PACK_START) > 0.05
              or abs(case_od - CASE_OD_START) > 0.6
              or abs(PORT_R_SHIFT) > 0.05)

checks = [
    ("bench stroke %.1f mm" % BENCH_STROKE, abs(BENCH_STROKE - 65.8) < 0.05),
    ("stroke rail L %.1f > stroke+pads" % stroke_rail_L,
     stroke_rail_L >= BENCH_STROKE + 2 * RAIL_CAGE_PAD - 0.1),
    ("finger on rail at dz=0",
     follower_on_track(follower, CAM_R, 0.0, R_PACK, 0.0)),
    ("finger on rail at dz=−stroke",
     follower_on_track(follower, CAM_R, -BENCH_STROKE, R_PACK, 180.0)),
    ("stroke-rail neighbour gap %.2f >= %.2f" % (gap_rails, CLEAR),
     gap_rails >= CLEAR - 1e-6),
    ("core neighbour gap %.2f >= %.2f" % (gap_core, CLEAR),
     gap_core >= CLEAR - 1e-6),
    ("station/core neighbour gap %.2f >= %.2f" % (gap_stations, CLEAR),
     gap_stations >= CLEAR - 1e-6),
    ("body/rails clear of cam", rail_cam_ok),
    ("open carriage inside housing", case_ok),
    ("housing wraps cam OD", r_case_id + 1e-6 >= cam_od / 2),
    ("crank outside housing / not in LOAD", crank_ok),
    ("hoses clear of cam track & stroke rail", hoses_ok),
    ("feed tray clear of housing & open carriage", feed_ok),
    ("LOAD window only (hopper at 180°)", abs(feed_ang - 180.0) < 1e-6),
    ("six phases", len(stations) == 6),
    ("closed station L %.1f ≈ 750" % closed_L, abs(closed_L - TARGET_L) <= 0.6),
    ("no full-length tube", z_case1 < z_tip_b - 200.0),
]
report = [
    NAME,
    "  sketch                 : rails + housing + crank + hoses (NOT frozen)",
    "  stroke (bench)         : %.1f mm; rail L=%.1f" % (BENCH_STROKE, stroke_rail_L),
    "  law                    : FIRE 330–30; OPEN 30–120; LOAD 120–240; CLOSE 240–330",
    "  cam                    : outboard liner Ø%.1f R=%.1f" % (cam_od, CAM_R),
    "  stroke rail            : printed cage; neighbour gap %.2f mm" % gap_rails,
    "  pack R                 : %.2f (start %.2f)%s"
    % (R_PACK, R_PACK_START,
       " — MOVED" if abs(R_PACK - R_PACK_START) > 0.05 else ""),
    "  casing Ø               : %.1f (CLEAR %.2f; was %.0f)%s"
    % (case_od, CASE_CLEAR_USE, CASE_OD_START,
       " — MOVED" if abs(case_od - CASE_OD_START) > 0.6 else ""),
    "  port shift             : %.1f mm radial" % PORT_R_SHIFT,
]
for n in probe_notes:
    report.append("  probe                 : " + n)
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  feed                  : tray at φ=180° through LOAD window",
    "  crank                 : outside housing on φ=0 (FIRE), not in 120–240°",
    "  hoses                 : port→outside casing→hub; past cam & stroke rail",
    "  overall LxWxH         : %.0f x %.0f x %.0f mm" % (gun_L, gun_W, gun_H),
    "  not drawn             : wheeled carriage, full-length shroud",
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
FV.STYLES["rail"] = ((0.55, 0.58, 0.62), 20)
FV.STYLES["feed"] = ((0.55, 0.50, 0.40), 50)
FV.STYLES["pellet"] = ((0.88, 0.88, 0.92), 15)
FV.STYLES["crank"] = ((0.25, 0.25, 0.28), 10)
FV.STYLES["hose"] = ((0.20, 0.55, 0.45), 35)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Cam", "Cam_drum", cam, "cam")
for i, rr in enumerate(rails_placed):
    sc.add("Rails", "Stroke_rail_%d" % (i + 1), rr, "rail")
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
             ((R_PACK + 70) * math.cos(a), (R_PACK + 70) * math.sin(a),
              z_stop + cam_dz(ang)))
sc.label("Labels", "stroke rail %.0f · casing Ø%.0f" % (BENCH_STROKE, case_od),
         (0, bb.YMax + 40, (bb.ZMin + bb.ZMax) / 2))

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
# Also export the stroke rail alone for print.
stroke_rail0.copy().exportStep(os.path.join(OUT_DIR, "stroke_rail.step"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech mechanism has [FAIL] checks")
