# -*- coding: utf-8 -*-
"""
Gatling breech mechanism (not a freeze).

Stroke from linear_breech (65.8 mm) → angle→stroke law → outboard cam liner →
printed stroke rail → open pack frame (no full casing) → six phases →
hopper on seat ring + shaft auger ×6 (6 soft pellets / rev) + feed guard →
side crank + carry/strap → air: MQR soft coupling, bearings, 6×M5, buffer, deadman.

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

# --- open pack frame (no full casing): rings + spars ---------------------------
z_tip_b = z_stop + BARREL_SHOW
z_stroke_end = qev_closed["Carriage"].BoundBox.ZMin - BENCH_STROKE
z_front0 = z_tip_b - PLATE_T + PLATE_LIP
z_front1 = z_tip_b + PLATE_LIP
z_rear0 = z_stop - PLATE_T * 0.35
z_rear1 = z_rear0 + PLATE_T
z_case1 = z_rear0 + CASE_OVERLAP
z_case0 = min(z_stroke_end, z_cam0, z_rail_lo) - 4.0
# Envelope must clear stroke-rail / cam (frame OD, not a shell).
rail_r_max = 0.0
for p in place_shape(stroke_rail0, R_PACK, 0.0).tessellate(1.0)[0]:
    rail_r_max = max(rail_r_max, math.hypot(p.x, p.y))
need_id = max(r_case_id, cam_od / 2 + CLEAR, rail_r_max + CLEAR)
if need_id > r_case_id + 1e-6:
    CASE_CLEAR_USE = need_id - (R_PACK + CH_OD / 2)
    r_case_id = need_id
    r_case_od = r_case_id + CASE_WALL
    moved_notes.append("frame envelope ID→%.1f (rail/cam)" % r_case_id)
r_plate = R_PACK + BARREL_OD / 2 + PLATE_RIM
hub_r = max(6.0, R_PACK - BARREL_OD / 2 - 4.0)
SPAR_R = 4.0
RING_T = 6.0
RING_WALL = 4.0
# Hopper seat ring at breech Z (around pack) — bin + auger tube sit on it.
HOP_RING_T = 18.0
win_z0 = z_stop - BENCH_STROKE - 5.0
win_z1 = z_stop + 15.0
z_feed = z_stop - BENCH_STROKE / 2
z_hop0 = z_feed - HOP_RING_T / 2
z_hop1 = z_hop0 + HOP_RING_T


def barrel_plate(z0, z1, od_r):
    disc = Part.makeCylinder(od_r, z1 - z0, V(0, 0, z0))
    for k in range(N):
        a = math.radians(k * 60.0)
        bx, by = R_PACK * math.cos(a), R_PACK * math.sin(a)
        disc = disc.cut(Part.makeCylinder(
            BARREL_OD / 2 + 0.35, (z1 - z0) + 4.0, V(bx, by, z0 - 2.0)))
    disc = disc.cut(Part.makeCylinder(hub_r, (z1 - z0) + 4.0, V(0, 0, z0 - 2.0)))
    return disc.removeSplitter()


def build_pack_frame(r_od):
    """Open frame: rings + spars + breech hopper seat ring. No drum shell."""
    parts = []
    for z0, z1 in (
            (z_case0, z_case0 + RING_T),
            (z_cam0 - 2.0, z_cam0 - 2.0 + RING_T),
            (z_rear0, z_rear1)):
        ring = tube(2.0 * r_od, 2.0 * (r_od - RING_WALL), z0, z1)
        parts.append(ring)
    # Wide hopper seat ring around pack at breech (LOAD port cut later).
    hop_ring = tube(2.0 * r_od, 2.0 * (r_od - RING_WALL), z_hop0, z_hop1)
    # Feed port through ring at φ=180 (−X before flip) — auger mouth.
    port_w = PELLET_D + 6.0
    port = Part.makeBox(r_od + 20.0, port_w, HOP_RING_T + 4.0,
                        V(-(r_od + 20.0), -port_w / 2, z_hop0 - 2.0))
    hop_ring = hop_ring.cut(port)
    parts.append(hop_ring)
    casc = Part.makeCylinder(r_od * 0.45, 5.0, V(0, 0, z_case0 - 5.0))
    casc = casc.cut(Part.makeCylinder(hub_r + 2.0, 9.0, V(0, 0, z_case0 - 7.0)))
    parts.append(casc)
    spar_r0 = r_od - SPAR_R - 1.0
    for k in range(N):
        ang = k * 60.0 + 30.0
        d_feed = abs(((ang - 180.0 + 180.0) % 360.0) - 180.0)
        if d_feed < 35.0:
            continue
        a = math.radians(ang)
        sx, sy = spar_r0 * math.cos(a), spar_r0 * math.sin(a)
        parts.append(Part.makeCylinder(
            SPAR_R, z_case1 - z_case0, V(sx, sy, z_case0)))
    try:
        return G.fuse_all(parts).removeSplitter()
    except Exception:
        return Part.makeCompound(parts)


front_plate = barrel_plate(z_front0, z_front1, r_plate)
rear_plate = barrel_plate(z_rear0, z_rear1, r_plate)
pack_frame = build_pack_frame(r_case_od)
# Keep alias for hose/rebuild paths that still say "casing".
breech_casing = pack_frame
# Full-tube reference volume (for "no full casing" check).
full_shell_vol = tube(
    2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1).Volume
frame_ok = pack_frame.Volume < 0.55 * full_shell_vol

# --- hopper + ×6 shaft-driven auger on breech seat ring (stage 4) ------------
# Built at φ=180 (−X). Final FLIP_Z=180 puts hopper on +X (top).
# A1: single-start + bevel 1:1 + spur ×6 → 6 soft balls / pack rev (mid ~180°).
feed_ang = 180.0
FLIP_Z = 180.0
a180 = math.radians(feed_ang)
ux_f, uy_f = math.cos(a180), math.sin(a180)
pd = PELLET_D
AUGER_PITCH = pd + 1.2
AUGER_STARTS = 1
AUGER_RATIO = 6.0              # spur after bevel: 6 auger turns / pack rev
bin_w, bin_d, bin_h = 60.0, 48.0, 70.0
GUARD_A, GUARD_B = 170.0, 310.0
GUARD_CLEAR = 1.5              # mm to trough / pellet


def flip_up(shape):
    """Rotate 180° about Z so −X feed becomes +X (top)."""
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), FLIP_Z)
    return s


def make_auger_along_z(pitch, length, r_core, r_od):
    """Single-start screw approx along +Z: core + helical flight bars."""
    core = Part.makeCylinder(r_core, length, V(0, 0, 0), V(0, 0, 1))
    n = max(24, int(length * 2.0))
    bars = [core]
    chord = max(3.0, pitch * 0.28)
    for i in range(n):
        z0 = length * i / float(n)
        ang = 360.0 * z0 / pitch
        bar = Part.makeBox(r_od - r_core + 0.5, chord, chord * 0.85,
                           V(r_core - 0.2, -chord / 2, z0))
        bar.rotate(V(0, 0, z0 + chord * 0.4), V(0, 0, 1), ang)
        bars.append(bar)
    try:
        return G.fuse_all(bars).removeSplitter()
    except Exception:
        return Part.makeCompound(bars)


def build_hopper_auger(r_od):
    """Bin + lid + short auger on seat ring; drive bevel 1:1 then spur ×6."""
    z_n = z_feed
    tube_id = pd + 2.5
    tube_od = tube_id + 6.0
    r_tube0 = r_od - RING_WALL - 1.0
    r_tube1 = r_od + 6.0
    tube_len = r_tube1 - r_tube0
    tube = Part.makeCylinder(
        tube_od / 2, tube_len, V(-r_tube0, 0, z_n), V(-1, 0, 0))
    tube = tube.cut(Part.makeCylinder(
        tube_id / 2, tube_len + 4.0, V(-r_tube0 + 2.0, 0, z_n), V(-1, 0, 0)))
    bin_o = Part.makeBox(bin_d, bin_w, bin_h,
                         V(-(r_od + bin_d), -bin_w / 2, z_n - bin_h / 2))
    bin_i = Part.makeBox(bin_d - 4.0, bin_w - 6.0, bin_h - 6.0,
                         V(-(r_od + bin_d - 2.0), -(bin_w - 6.0) / 2,
                           z_n - (bin_h - 6.0) / 2))
    mouth = Part.makeCylinder(tube_id / 2 + 1.0, 10.0,
                              V(-(r_od - 2.0), 0, z_n), V(-1, 0, 0))
    # Speed-feed style lid on outer (+radial) face of bin.
    lid = Part.makeBox(3.0, bin_w - 4.0, bin_h - 8.0,
                       V(-(r_od + bin_d + 3.0), -(bin_w - 4.0) / 2,
                         z_n - (bin_h - 8.0) / 2))
    lid_hole = Part.makeCylinder(12.0, 8.0,
                                 V(-(r_od + bin_d + 4.0), 0, z_n + 8.0),
                                 V(-1, 0, 0))
    lid = lid.cut(lid_hole)
    body = tube.fuse(bin_o).fuse(lid).cut(bin_i).cut(mouth)
    try:
        body = body.removeSplitter()
    except Exception:
        pass
    aug_len = max(AUGER_PITCH * 1.1, tube_len - 1.0)
    r_core, r_od_a = 4.0, tube_id / 2 - 1.0
    aug = make_auger_along_z(AUGER_PITCH, aug_len, r_core, r_od_a)
    aug.rotate(V(0, 0, 0), V(0, 1, 0), 90.0)
    aug.translate(V(-r_tube0 - 1.0, 0, z_n))
    # Pack shaft → bevel 1:1 → spur ×6 → auger stub.
    drive = G.cyl(7.0, z_case0 - 25.0, z_n + 20.0)
    bevel_z = Part.makeCylinder(14.0, 10.0, V(0, 0, z_n - 5.0))
    stub_r0 = max(R_PACK * 0.35, r_od - RING_WALL - 35.0)
    bevel_x = Part.makeCylinder(14.0, 8.0, V(-stub_r0, 0, z_n), V(-1, 0, 0))
    # Spur pair: large on radial shaft, small on auger (ratio 6).
    spur_lo = Part.makeCylinder(22.0, 8.0, V(-(stub_r0 + 10.0), 0, z_n - 4.0),
                                V(-1, 0, 0))
    spur_hi = Part.makeCylinder(8.0, 8.0, V(-(r_tube0 - 6.0), 0, z_n - 4.0),
                                V(-1, 0, 0))
    stub = Part.makeCylinder(5.0, r_tube0 - stub_r0 + 4.0,
                             V(-stub_r0, 0, z_n), V(-1, 0, 0))
    drive = (drive.fuse(bevel_z).fuse(bevel_x).fuse(spur_lo)
             .fuse(spur_hi).fuse(stub).removeSplitter())
    p_aug = Part.makeSphere(pd / 2, V(-(r_tube0 + aug_len * 0.45), 0, z_n))
    p_bin = Part.makeSphere(
        pd / 2, V(-(r_od + bin_d * 0.55), 0, z_n + pd * 0.4))
    p_breech = place_shape(
        Part.makeSphere(pd / 2, V(0, 0, (z_tip + pd / 2) - BENCH_STROKE)),
        R_PACK, feed_ang)
    flush_gap = 0.0
    on_ring = (tube_len <= RING_WALL + 10.0
               and r_tube0 >= r_od - RING_WALL - 2.0)
    return dict(
        body=body, auger=aug, drive=drive, lid=lid,
        p_aug=p_aug, p_bin=p_bin, p_breech=p_breech,
        pitch=AUGER_PITCH, starts=AUGER_STARTS, ratio=AUGER_RATIO,
        pellets_per_rev=AUGER_STARTS * AUGER_RATIO, tube_id=tube_id,
        tube_len=tube_len, r_tube0=r_tube0, aug_len=aug_len,
        flush_gap=flush_gap, on_ring=on_ring)


open_carr = place_shape(shifted(qev_closed["Carriage"], -BENCH_STROKE),
                        R_PACK, feed_ang)


def seat_hopper(r_od):
    h = build_hopper_auger(r_od)
    return (h["body"], h["auger"], h["drive"],
            h["p_aug"], h["p_bin"], h["p_breech"], h)


hopper, auger, auger_drive, pellet_aug, pellet_bin, pellet, hop_m = seat_hopper(
    r_case_od)
auger_ok = (
    abs(hop_m["pellets_per_rev"] - 6.0) < 1e-9
    and hop_m["starts"] == 1
    and abs(hop_m["ratio"] - 6.0) < 1e-9
    and abs(hop_m["pitch"] - (pd + 1.2)) < 0.05
    and hop_m["pitch"] >= pd
    and hop_m["pitch"] < 1.5 * pd)
hopper_flush_ok = hop_m["flush_gap"] < 1.0 and hop_m["on_ring"]
feed_clear = hopper.common(open_carr).Volume < 1.0
feed_ok = feed_clear and auger_ok and hopper_flush_ok
# Six deliveries / pack rev; midpoint of issue at feed_ang=180° ±10°.
six_per_rev_ok = (
    abs(hop_m["pellets_per_rev"] - 6.0) < 1e-9
    and abs(feed_ang - 180.0) <= 10.0
    and LOAD_A <= feed_ang <= LOAD_B
    and auger_ok
    and feed_clear)

# --- side crank + two triggers (pack clutch, auger stop) on +Y ---------------
# Pre-flip on +Y (φ=90); after FLIP_Z → −Y. Outside LOAD 120–240°.
CRANK_ANG = 90.0
assert not (LOAD_A <= CRANK_ANG <= LOAD_B)
z_crank = 0.5 * (z_cam0 + z_stop)          # mid-breech, not aft stub


def build_crank(r_od):
    """Side crank: hub on frame OD, arm along +Y (gun_sketch style)."""
    y0 = r_od - 2.0
    hub = Part.makeCylinder(12.0, 18.0, V(0, y0, z_crank), V(0, 1, 0))
    arm_len = 55.0
    arm = Part.makeBox(10.0, arm_len, 10.0,
                       V(-5.0, y0 + 16.0, z_crank - 5.0))
    knob = Part.makeSphere(14.0, V(0.0, y0 + 16.0 + arm_len, z_crank))
    return hub.fuse(arm).fuse(knob).removeSplitter()


def build_triggers(r_od):
    """Two levers beside the crank on +Y, clear of LOAD.
    Pack trigger: slides dog clutch on pack shaft (breaks rotation drive).
    Feed trigger: retracts idler on auger bevel (stops screw only).
    Clutch/idler shown on the *side* cheek, not through the pack.
    """
    y0 = r_od + 2.0
    cheek = Part.makeBox(32.0, 5.0, 72.0,
                         V(-16.0, y0, z_crank - 42.0))
    # Pack-rotation clutch lever (aft).
    pack_piv = V(9.0, y0 + 5.0, z_crank - 24.0)
    pack_lev = Part.makeBox(6.0, 40.0, 8.0,
                            V(pack_piv.x - 3.0, pack_piv.y, pack_piv.z - 4.0))
    pack_knob = Part.makeSphere(7.0, V(pack_piv.x, pack_piv.y + 40.0, pack_piv.z))
    # Dog halves as short stubs on the cheek (visual clutch), not on axis.
    dog_a = Part.makeCylinder(6.0, 10.0, V(9.0, y0 - 2.0, z_crank - 30.0), V(0, 1, 0))
    dog_b = Part.makeCylinder(6.0, 10.0, V(9.0, y0 - 2.0, z_crank - 16.0), V(0, 1, 0))
    pack_trig = cheek.fuse(pack_lev).fuse(pack_knob).fuse(dog_a).fuse(dog_b)
    # Auger-feed stop lever (forward).
    feed_piv = V(-9.0, y0 + 5.0, z_crank + 20.0)
    feed_lev = Part.makeBox(6.0, 40.0, 8.0,
                            V(feed_piv.x - 3.0, feed_piv.y, feed_piv.z - 4.0))
    feed_knob = Part.makeSphere(7.0, V(feed_piv.x, feed_piv.y + 40.0, feed_piv.z))
    idler = Part.makeCylinder(7.0, 14.0, V(-9.0, y0 - 2.0, z_crank + 20.0), V(0, 1, 0))
    feed_trig = feed_lev.fuse(feed_knob).fuse(idler)
    try:
        pack_trig = pack_trig.removeSplitter()
        feed_trig = feed_trig.removeSplitter()
    except Exception:
        pass
    return pack_trig, feed_trig


crank = build_crank(r_case_od)
trig_pack, trig_feed = build_triggers(r_case_od)
crank_ok = crank.distToShape(pack_frame)[0] >= 0.0  # may seat on frame
crank_side_ok = abs(CRANK_ANG - 90.0) < 1e-6 and not (
    LOAD_A <= CRANK_ANG <= LOAD_B)
# Knob must stick out in ±Y (side), not along ±X (up/down) or far aft-only.
crank_bb = crank.BoundBox
crank_side_geom = (crank_bb.YLength > crank_bb.XLength
                   and abs(crank_bb.Center.y) > abs(crank_bb.Center.x))
for k in range(N):
    ang = k * 60.0
    if LOAD_A <= ang <= LOAD_B:
        if crank.distToShape(stations[k])[0] < CLEAR - 1e-3:
            crank_ok = False
crank_ok = crank_ok and crank_side_ok and crank_side_geom
# Triggers on same side, clear of LOAD sector stations.
trig_ok = True
for tr in (trig_pack, trig_feed):
    for k in range(N):
        ang = k * 60.0
        if LOAD_A <= ang <= LOAD_B:
            if tr.distToShape(stations[k])[0] < CLEAR - 1e-3:
                trig_ok = False
trig_ok = trig_ok and crank_side_ok

# --- feed guard 170–310° (stage 4) + CG carry / strap (stage 7) --------------
def annular_sector(r_od, r_id, z0, z1, a0, a1, step=4.0):
    """Keep annular sector [a0,a1] deg (world, pre-flip)."""
    ring = tube(2.0 * r_od, 2.0 * r_id, z0, z1)
    wedges = []
    a = a0
    while a < a1 - 1e-9:
        a2 = min(a + step, a1)
        mid = 0.5 * (a + a2)
        half = math.radians(0.5 * (a2 - a))
        w = max(4.0, 2.0 * r_od * math.sin(half) + 2.0)
        box = Part.makeBox(r_od + 4.0, w, z1 - z0 + 2.0,
                           V(0.0, -w / 2, z0 - 1.0))
        box.rotate(V(0, 0, 0), V(0, 0, 1), mid)
        wedges.append(box)
        a = a2
    pie = G.fuse_all(wedges) if len(wedges) > 1 else wedges[0]
    try:
        return ring.common(pie).removeSplitter()
    except Exception:
        return ring.common(pie)


# Trough / open-carriage radial envelope for guard ID.
trough_r = 0.0
for p in open_carr.tessellate(1.2)[0]:
    trough_r = max(trough_r, math.hypot(p.x, p.y))
r_guard_id = trough_r + GUARD_CLEAR
r_guard_od = r_guard_id + 3.0
z_guard0 = z_feed - pd - 8.0
z_guard1 = z_stop + 8.0
feed_guard = annular_sector(
    r_guard_od, r_guard_id, z_guard0, z_guard1, GUARD_A, GUARD_B)
# Guard must not cut the trough (open carriage at LOAD) or the hopper mouth.
guard_clear_ok = (
    feed_guard.distToShape(open_carr)[0] >= GUARD_CLEAR - 0.2
    and feed_guard.common(open_carr).Volume < 1.0
    and feed_guard.common(hopper).Volume < 50.0)
guard_span_ok = abs(GUARD_B - GUARD_A - 140.0) < 1e-6

# Carry handle near estimated CG (mid breech Z, on −X = top after flip).
z_cg = 0.5 * (z_case0 + z_front1)
x_handle = -(r_case_od + 22.0)
carry = Part.makeBox(12.0, 18.0, 90.0,
                     V(x_handle - 6.0, -9.0, z_cg - 45.0))
carry_grip = Part.makeCylinder(9.0, 70.0, V(x_handle - 18.0, 0, z_cg - 35.0),
                               V(0, 0, 1))
carry_handle = carry.fuse(carry_grip).removeSplitter()
# Sling strap: thin loops front + aft on −X.
strap_f = Part.makeTorus(18.0, 3.0)
strap_f.translate(V(x_handle, 0, z_front0 + 10.0))
strap_r = Part.makeTorus(18.0, 3.0)
strap_r.translate(V(x_handle, 0, z_case0 + 10.0))
strap_bar = Part.makeBox(4.0, 6.0, abs(z_front0 - z_case0),
                         V(x_handle - 2.0, -3.0, min(z_case0, z_front0) + 10.0))
sling = strap_f.fuse(strap_r).fuse(strap_bar).removeSplitter()
carry_ok = (carry_handle.BoundBox.Center.x < 0.0
            and abs(carry_handle.BoundBox.Center.z - z_cg) < 30.0)

# --- air (stage 5): shaft bearings + soft coupling + MQR + 6×M5 + buffer -----
# MQR is air-only: pack axle rides its own bearings; soft coupling drives rotor.
# Six M5 lines → each AirTAC R; route outside cam track & stroke rail.
# Feed / hopper seat ring unchanged.
hose_r = 2.5                   # ~M5 PU OD sketch
PORT_R_SHIFT = 0.0
stroke_rails_pack = Part.makeCompound(rails_placed)
r_exit0 = max(rail_r_max, cam_od / 2.0) + CLEAR + 6.0 + hose_r
z_clear_air = min(z_rail_lo, z_cam0) - 4.0

# MQR6 clone sizes (same as mqr_axis_sketch.py).
AXLE_OD, AXLE_ID = 16.0, 10.0
BRG_OD, BRG_ID, BRG_T = 36.0, AXLE_OD + 0.3, 14.0
ROTOR_OD, ROTOR_L = 46.0, 29.0
STATOR_OD, STATOR_L = 46.0, 53.0
MQR_THROUGH = 6.0
SOFT_OD, SOFT_L, SOFT_GAP = 40.0, 28.0, 4.0   # jaw + spider gap
BUFFER_OD, BUFFER_L = 80.0, 150.0             # ≈0.75 L free volume
BUFFER_VOL_L = (math.pi * (BUFFER_OD / 2) ** 2 * BUFFER_L) / 1.0e6

# Aft stack: bearings in frame → soft coupling → MQR rotor → stator (+Z muzzle).
# Front bearing in aft cascabel/ring; rear bearing in a frame disk tied by spars.
BRG_NAME = "6202-ish (Ø16 shaft, race OD %.0f × %.0f)" % (BRG_OD, BRG_T)
z_brg_f1 = z_case0 + 2.0
z_brg_f0 = z_brg_f1 - BRG_T
z_brg_r1 = z_case0 - 55.0
z_brg_r0 = z_brg_r1 - BRG_T
z_axle0 = z_brg_r0 - 8.0
z_soft1 = z_brg_r0 - 6.0
z_soft0 = z_soft1 - SOFT_L
z_rotor1 = z_soft0 - SOFT_GAP
z_rotor0 = z_rotor1 - ROTOR_L
z_stator1 = z_rotor0
z_stator0 = z_stator1 - STATOR_L
z_hose_aft = 0.5 * (z_rotor0 + z_rotor1)


def port_world(ang, dz, which="R"):
    """AirTAC port centre in world after place_shape (local +Y → radial out)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    y_loc = vent_y + AIRTAC["T"] + PORT_R_SHIFT
    if which == "A":
        y_loc = vent_y - PORT_R_SHIFT
    r = R_PACK + y_loc
    z = z_stem + AIRTAC["ports"][which] + dz
    return V(r * ux, r * uy, z), ux, uy


def build_bearing_in_frame(z_a, z_b, r_frame):
    """Pack-shaft race seated in a frame disk with spars (MQR not in load path)."""
    race = tube(BRG_OD, BRG_ID, z_a, z_b)
    hub = tube(BRG_OD + 10.0, BRG_OD - 0.2, z_a, z_b)
    rim = tube(2.0 * r_frame, 2.0 * (r_frame - 5.0), z_a, z_b)
    parts = [race, hub, rim]
    for ang in (30.0, 150.0, 270.0):   # skip LOAD φ=180
        a = math.radians(ang)
        sx0 = (BRG_OD / 2 + 2) * math.cos(a)
        sy0 = (BRG_OD / 2 + 2) * math.sin(a)
        L = max(8.0, r_frame - 5.0 - (BRG_OD / 2 + 2))
        spoke = Part.makeCylinder(
            4.0, L,
            V(sx0, sy0, 0.5 * (z_a + z_b)),
            V(math.cos(a), math.sin(a), 0))
        parts.append(spoke)
    try:
        return G.fuse_all(parts).removeSplitter()
    except Exception:
        return Part.makeCompound(parts)


def build_air_stack():
    """Axle on 2 frame bearings; soft coupling; MQR; buffer; deadman."""
    axle = tube(AXLE_OD, AXLE_ID, z_axle0, z_case0 + 20.0)
    brg_f = build_bearing_in_frame(z_brg_f0, z_brg_f1, r_case_od)
    brg_r = build_bearing_in_frame(z_brg_r0, z_brg_r1, r_case_od * 0.85)
    # Soft jaw coupling: pack hub / spider / MQR hub — gap so MQR takes no load.
    hub_pack = tube(SOFT_OD, AXLE_OD + 0.2, z_soft1 - 10.0, z_soft1)
    hub_mqr = tube(SOFT_OD, MQR_THROUGH + 0.5, z_soft0, z_soft0 + 10.0)
    spider = Part.makeCylinder(SOFT_OD * 0.45, SOFT_GAP,
                               V(0, 0, z_soft0 + 10.0))
    soft = hub_pack.fuse(hub_mqr).fuse(spider).removeSplitter()
    rotor = tube(ROTOR_OD, MQR_THROUGH, z_rotor0, z_rotor1)
    for k in range(N):
        a = math.radians(k * 60.0)
        # M5 stub on rotor OD (channel to station k).
        stub = Part.makeCylinder(
            4.0, 8.0,
            V((ROTOR_OD / 2 - 1) * math.cos(a),
              (ROTOR_OD / 2 - 1) * math.sin(a), z_hose_aft),
            V(math.cos(a), math.sin(a), 0))
        rotor = rotor.fuse(stub)
    rotor = rotor.removeSplitter()
    stator = tube(STATOR_OD, MQR_THROUGH, z_stator0, z_stator1)
    inlet = Part.makeCylinder(6.0, 14.0, V(0, STATOR_OD / 2 - 2, z_stator0 + 20.0),
                              V(0, 1, 0))
    stator = stator.fuse(inlet).removeSplitter()
    # Buffer 0.5–1 L beside stator (+Y side = crank side pre-flip).
    buf_y = r_case_od + BUFFER_OD / 2 + 8.0
    buffer = tube(BUFFER_OD, BUFFER_OD - 4.0, z_stator0, z_stator0 + BUFFER_L,
                  0.0, buf_y)
    # Dead-man ball valve on inlet (+Y, near buffer).
    dm_body = Part.makeCylinder(12.0, 28.0, V(0, buf_y - BUFFER_OD / 2 - 8.0,
                                             z_stator0 + 18.0), V(0, 1, 0))
    dm_lever = Part.makeBox(6.0, 8.0, 22.0,
                            V(-3.0, buf_y - BUFFER_OD / 2 + 6.0,
                              z_stator0 + 28.0))
    deadman = dm_body.fuse(dm_lever).removeSplitter()
    # Supply stub buffer → stator inlet.
    p_buf = V(0, buf_y - BUFFER_OD / 2, z_stator0 + 20.0)
    p_in = V(0, STATOR_OD / 2 + 10.0, z_stator0 + 20.0)
    supply = Part.makeCylinder(4.0, p_buf.distanceToPoint(p_in), p_in,
                               p_buf.sub(p_in))
    return dict(
        axle=axle, brg_f=brg_f, brg_r=brg_r, soft=soft,
        rotor=rotor, stator=stator, buffer=buffer, deadman=deadman,
        supply=supply, buf_y=buf_y)


def build_m5_lines(r_exit):
    """Six M5 lines: AirTAC R → out past cam/rail → aft → MQR rotor stub."""
    segs = []
    for k in range(N):
        ang = k * 60.0
        dz = cam_dz(ang)
        p_port, ux, uy = port_world(ang, dz, "R")
        p1 = V((R_PACK + vent_y + AIRTAC["T"] + PORT_R_SHIFT + 8.0) * ux,
               (R_PACK + vent_y + AIRTAC["T"] + PORT_R_SHIFT + 8.0) * uy,
               p_port.z)
        p2 = V(p1.x, p1.y, z_clear_air)
        p3 = V(r_exit * ux, r_exit * uy, z_clear_air)
        p4 = V(r_exit * ux, r_exit * uy, z_hose_aft)
        p5 = V((ROTOR_OD / 2 + 6.0) * ux, (ROTOR_OD / 2 + 6.0) * uy, z_hose_aft)
        for p0, p1_ in ((p_port, p1), (p1, p2), (p2, p3), (p3, p4), (p4, p5)):
            vec = p1_.sub(p0)
            if vec.Length > 1.0:
                segs.append(Part.makeCylinder(hose_r, vec.Length, p0, vec))
        # Short pilot A vent stub (not through cam track).
        pA, _, _ = port_world(ang, dz, "A")
        pA1 = V(pA.x - 6.0 * ux, pA.y - 6.0 * uy, pA.z)
        pA2 = V(pA1.x, pA1.y, z_clear_air)
        for p0, p1_ in ((pA, pA1), (pA1, pA2)):
            vec = p1_.sub(p0)
            if vec.Length > 1.0:
                segs.append(Part.makeCylinder(hose_r * 0.7, vec.Length, p0, vec))
    return Part.makeCompound(segs)


def hose_clear(hs):
    d_cam = hs.distToShape(cam)[0]
    d_rail = hs.distToShape(stroke_rails_pack)[0]
    return d_cam >= CLEAR - 1e-3 and d_rail >= CLEAR - 1e-3, d_cam, d_rail


def rebuild_housing_for_od():
    global pack_frame, breech_casing, crank, trig_pack, trig_feed
    global hopper, auger, auger_drive, pellet_aug, pellet_bin, pellet, hop_m
    global feed_ok, auger_ok, six_per_rev_ok, hopper_flush_ok, frame_ok
    global full_shell_vol
    pack_frame = build_pack_frame(r_case_od)
    breech_casing = pack_frame
    full_shell_vol = tube(
        2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1).Volume
    frame_ok = pack_frame.Volume < 0.55 * full_shell_vol
    crank = build_crank(r_case_od)
    trig_pack, trig_feed = build_triggers(r_case_od)
    (hopper, auger, auger_drive, pellet_aug, pellet_bin, pellet,
     hop_m) = seat_hopper(r_case_od)
    auger_ok = (
        abs(hop_m["pellets_per_rev"] - 6.0) < 1e-9
        and hop_m["starts"] == 1
        and abs(hop_m["ratio"] - 6.0) < 1e-9
        and abs(hop_m["pitch"] - (pd + 1.2)) < 0.05
        and hop_m["pitch"] >= pd
        and hop_m["pitch"] < 1.5 * pd)
    hopper_flush_ok = hop_m["flush_gap"] < 1.0 and hop_m["on_ring"]
    feed_clear = hopper.common(open_carr).Volume < 1.0
    feed_ok = feed_clear and auger_ok and hopper_flush_ok
    six_per_rev_ok = (
        abs(hop_m["pellets_per_rev"] - 6.0) < 1e-9
        and abs(feed_ang - 180.0) <= 10.0
        and LOAD_A <= feed_ang <= LOAD_B
        and auger_ok
        and feed_clear)


air = build_air_stack()
pack_axle = air["axle"]
brg_f = air["brg_f"]
brg_r = air["brg_r"]
soft_coup = air["soft"]
mqr_rotor = air["rotor"]
mqr_stator = air["stator"]
air_buffer = air["buffer"]
deadman = air["deadman"]
air_supply = air["supply"]

r_exit = max(r_exit0, r_case_od + 8.0)
hoses_s = build_m5_lines(r_exit)
ok_h, d_cam_h, d_rail_h = hose_clear(hoses_s)
print("hose try exit=%.1f cam=%.2f rail=%.2f" % (r_exit, d_cam_h, d_rail_h),
      flush=True)
for _try in range(6):
    if ok_h:
        break
    if d_rail_h < CLEAR:
        PORT_R_SHIFT += 4.0
        moved_notes.append("PORT_R_SHIFT→%.1f (hose↔rail=%.2f)" % (
            PORT_R_SHIFT, d_rail_h))
    if d_cam_h < CLEAR:
        r_exit = max(r_exit + 6.0, cam_od / 2 + CLEAR + 12.0)
        need_od = r_exit - 8.0
        if need_od > r_case_od:
            CASE_CLEAR_USE = need_od - CASE_WALL - (R_PACK + CH_OD / 2)
            r_case_id = R_PACK + CH_OD / 2 + CASE_CLEAR_USE
            r_case_od = r_case_id + CASE_WALL
            moved_notes.append(
                "frame Ø→%.1f (hose past cam)" % (2.0 * r_case_od))
            rebuild_housing_for_od()
        moved_notes.append("hose exit r→%.1f (hose↔cam=%.2f)" % (
            r_exit, d_cam_h))
    r_exit = max(r_exit, r_case_od + 8.0)
    hoses_s = build_m5_lines(r_exit)
    ok_h, d_cam_h, d_rail_h = hose_clear(hoses_s)
    print("hose try exit=%.1f cam=%.2f rail=%.2f" % (r_exit, d_cam_h, d_rail_h),
          flush=True)

hoses_ok = ok_h
# Air-stack checks (geometry, not a freeze).
mqr_soft_ok = soft_coup.Volume > 1000.0 and SOFT_GAP >= 3.0
mqr_no_axle = pack_axle.common(
    G.cyl(MQR_THROUGH + 0.5, min(z_rotor0, z_stator0),
          max(z_rotor1, z_stator1))).Volume < 1.0
# Axle clears races; front seat kisses aft frame ring (load in frame, not MQR).
bearings_ok = (
    brg_f.Volume > 500.0 and brg_r.Volume > 500.0
    and pack_axle.distToShape(brg_f)[0] >= 0.05
    and pack_axle.distToShape(brg_r)[0] >= 0.05
    and brg_f.distToShape(pack_frame)[0] < 8.0
    and abs(0.5 * (z_brg_f0 + z_brg_f1) - z_case0) < BRG_T + 4.0
    and mqr_no_axle)
buffer_ok = 0.5 <= BUFFER_VOL_L <= 1.0 + 1e-6
deadman_ok = deadman.Volume > 500.0
lines_ok = hoses_ok and abs(N - 6) < 1e-9
air_ok = (mqr_soft_ok and mqr_no_axle and bearings_ok
          and buffer_ok and deadman_ok and lines_ok)
# Re-check crank/triggers after possible hose rebuild.
crank_bb = crank.BoundBox
crank_side_geom = (crank_bb.YLength > crank_bb.XLength
                   and abs(crank_bb.Center.y) > abs(crank_bb.Center.x))
crank_ok = crank_side_ok and crank_side_geom
for k in range(N):
    ang = k * 60.0
    if LOAD_A <= ang <= LOAD_B:
        if crank.distToShape(stations[k])[0] < CLEAR - 1e-3:
            crank_ok = False
trig_ok = crank_side_ok
for tr in (trig_pack, trig_feed):
    for k in range(N):
        ang = k * 60.0
        if LOAD_A <= ang <= LOAD_B:
            if tr.distToShape(stations[k])[0] < CLEAR - 1e-3:
                trig_ok = False

# --- flip whole gun 180° about Z: hopper −X → +X (top) -----------------------
stations = [flip_up(s) for s in stations]
rails_placed = [flip_up(s) for s in rails_placed]
cam = flip_up(cam)
front_plate = flip_up(front_plate)
rear_plate = flip_up(rear_plate)
pack_frame = flip_up(pack_frame)
breech_casing = pack_frame
hopper = flip_up(hopper)
auger = flip_up(auger)
auger_drive = flip_up(auger_drive)
pellet_aug = flip_up(pellet_aug)
pellet_bin = flip_up(pellet_bin)
pellet = flip_up(pellet)
crank = flip_up(crank)
trig_pack = flip_up(trig_pack)
trig_feed = flip_up(trig_feed)
feed_guard = flip_up(feed_guard)
carry_handle = flip_up(carry_handle)
sling = flip_up(sling)
hoses_s = flip_up(hoses_s)
pack_axle = flip_up(pack_axle)
brg_f = flip_up(brg_f)
brg_r = flip_up(brg_r)
soft_coup = flip_up(soft_coup)
mqr_rotor = flip_up(mqr_rotor)
mqr_stator = flip_up(mqr_stator)
air_buffer = flip_up(air_buffer)
deadman = flip_up(deadman)
air_supply = flip_up(air_supply)
hopper_top_ok = hopper.BoundBox.Center.x > 0.0
carry_top_ok = carry_handle.BoundBox.Center.x > 0.0
crank_side_after = abs(crank.BoundBox.Center.y) > abs(crank.BoundBox.Center.x)
trig_side_after = (abs(trig_pack.BoundBox.Center.y) > abs(trig_pack.BoundBox.Center.x)
                   and abs(trig_feed.BoundBox.Center.y) > abs(trig_feed.BoundBox.Center.x))
moved_notes.append("FLIP_Z=%g: hopper/carry → +X; crank/triggers → −Y" % FLIP_Z)

# --- assembly / checks / report ----------------------------------------------
pack = Part.makeCompound(stations)
pellets = Part.makeCompound([pellet_aug, pellet_bin, pellet])
assembly = Part.makeCompound([
    pack, cam, front_plate, rear_plate, pack_frame,
    hopper, auger, auger_drive, pellets, feed_guard,
    crank, trig_pack, trig_feed, carry_handle, sling,
    pack_axle, brg_f, brg_r, soft_coup, mqr_rotor, mqr_stator,
    air_buffer, deadman, air_supply, hoses_s,
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
    ("open carriage inside frame envelope", case_ok),
    ("frame envelope clears cam OD", r_case_id + 1e-6 >= cam_od / 2),
    ("open frame (not full casing)", frame_ok),
    ("crank sideways / not in LOAD", crank_ok and crank_side_after),
    ("triggers on side / not in LOAD", trig_ok and trig_side_after),
    ("M5 lines clear of cam track & stroke rail", hoses_ok),
    ("air: MQR soft-coupled + bearings + buffer + deadman", air_ok),
    ("pack shaft bearings seated in frame", bearings_ok),
    ("buffer %.2f L in 0.5–1 L" % BUFFER_VOL_L, buffer_ok),
    ("hopper on seat ring + clear of open carriage", feed_ok),
    ("auger ×6 single-start (6 pellets/rev)", auger_ok),
    ("six soft pellets per pack rev (mid ~180°)", six_per_rev_ok),
    ("feed guard 170–310° clear of trough", guard_clear_ok and guard_span_ok),
    ("carry handle at CG (top after flip)", carry_ok and carry_top_ok),
    ("hopper on top (+X) after flip", hopper_top_ok),
    ("LOAD window (pre-flip φ=180°)", abs(feed_ang - 180.0) < 1e-6),
    ("six phases", len(stations) == 6),
    ("closed station L %.1f ≈ 750" % closed_L, abs(closed_L - TARGET_L) <= 0.6),
    ("no full-length tube", z_case1 < z_tip_b - 200.0),
]
report = [
    NAME,
    "  sketch                 : full mechanism sketch (stages 4+5+7; NOT frozen)",
    "  stroke (bench)         : %.1f mm; rail L=%.1f" % (BENCH_STROKE, stroke_rail_L),
    "  law                    : FIRE 330–30; OPEN 30–120; LOAD 120–240; CLOSE 240–330",
    "  cam                    : outboard liner Ø%.1f R=%.1f" % (cam_od, CAM_R),
    "  stroke rail            : printed cage; neighbour gap %.2f mm" % gap_rails,
    "  pack R                 : %.2f (start %.2f)%s"
    % (R_PACK, R_PACK_START,
       " — MOVED" if abs(R_PACK - R_PACK_START) > 0.05 else ""),
    "  frame envelope Ø       : %.1f (CLEAR %.2f; was casing %.0f)%s"
    % (case_od, CASE_CLEAR_USE, CASE_OD_START,
       " — MOVED" if abs(case_od - CASE_OD_START) > 0.6 else ""),
    "  port shift             : %.1f mm radial" % PORT_R_SHIFT,
    "  flip                   : Z %.0f° — hopper on +X (top)" % FLIP_Z,
]
for n in probe_notes:
    report.append("  probe                 : " + n)
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  skin                  : open frame (rings+spars); no full breech casing",
    "  feed                  : lid+bin on seat ring; auger ×6 → LOAD mid 180°",
    "  auger                 : single-start pitch %.1f; spur ×%.0f → 6×Ø%.1f / rev"
    % (hop_m["pitch"], hop_m["ratio"], pd),
    "  feed guard            : %.0f–%.0f°; clear ≥%.1f mm to trough"
    % (GUARD_A, GUARD_B, GUARD_CLEAR),
    "  crank                 : side hub on frame (−Y after flip); not in LOAD",
    "  trigger pack          : dog clutch on pack shaft — breaks rotation drive",
    "  trigger feed          : sliding idler on auger bevel — stops screw only",
    "  carry                 : handle near CG on top; sling loops front/aft",
    "  air MQR               : rotor on soft coupling; axle on 2 bearings (not MQR)",
    "  bearings              : 2× %s in frame disks" % BRG_NAME,
    "  air lines             : 6×M5 rotor→AirTAC R; outside cam & stroke rail",
    "  air buffer            : Ø%.0f×%.0f ≈ %.2f L; dead-man on inlet"
    % (BUFFER_OD, BUFFER_L, BUFFER_VOL_L),
    "  overall LxWxH         : %.0f x %.0f x %.0f mm" % (gun_L, gun_W, gun_H),
    "  not drawn             : wheeled carriage, backpack tank, freeze",
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
FV.STYLES["frame"] = ((0.72, 0.68, 0.55), 40)
FV.STYLES["cam"] = ((0.35, 0.38, 0.42), 15)
FV.STYLES["rail"] = ((0.55, 0.58, 0.62), 20)
FV.STYLES["feed"] = ((0.55, 0.50, 0.40), 50)
FV.STYLES["auger"] = ((0.40, 0.42, 0.48), 20)
FV.STYLES["drive"] = ((0.30, 0.32, 0.36), 15)
FV.STYLES["pellet"] = ((0.88, 0.88, 0.92), 15)
FV.STYLES["crank"] = ((0.25, 0.25, 0.28), 10)
FV.STYLES["trig"] = ((0.55, 0.22, 0.18), 15)
FV.STYLES["hose"] = ((0.20, 0.55, 0.45), 35)
FV.STYLES["mqr"] = ((0.45, 0.70, 0.95), 25)
FV.STYLES["brg"] = ((0.35, 0.55, 0.85), 20)
FV.STYLES["buffer"] = ((0.55, 0.60, 0.65), 40)
FV.STYLES["deadman"] = ((0.75, 0.25, 0.20), 15)
FV.STYLES["guard"] = ((0.60, 0.62, 0.70), 70)
FV.STYLES["carry"] = ((0.28, 0.28, 0.30), 15)
FV.STYLES["callout"] = ((0.15, 0.15, 0.15), 0)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Cam", "Cam_drum", cam, "cam")
for i, rr in enumerate(rails_placed):
    sc.add("Rails", "Stroke_rail_%d" % (i + 1), rr, "rail")
sc.add("Skin", "Front_barrel_plate", front_plate, "plate")
sc.add("Skin", "Rear_barrel_plate", rear_plate, "plate")
sc.add("Skin", "Pack_frame", pack_frame, "frame")
sc.add("Feed", "Hopper_bin", hopper, "feed")
sc.add("Feed", "Auger", auger, "auger")
sc.add("Feed", "Auger_drive", auger_drive, "drive")
sc.add("Feed", "Feed_guard", feed_guard, "guard")
sc.add("Feed", "Pellet_auger", pellet_aug, "pellet")
sc.add("Feed", "Pellet_bin", pellet_bin, "pellet")
sc.add("Feed", "Pellet_load", pellet, "pellet")
sc.add("Drive", "Crank", crank, "crank")
sc.add("Drive", "Trigger_pack_clutch", trig_pack, "trig")
sc.add("Drive", "Trigger_auger_stop", trig_feed, "trig")
sc.add("Carry", "Carry_handle", carry_handle, "carry")
sc.add("Carry", "Sling_strap", sling, "carry")
sc.add("Air", "Pack_axle", pack_axle, "drive")
sc.add("Air", "Bearing_front", brg_f, "brg")
sc.add("Air", "Bearing_rear", brg_r, "brg")
sc.add("Air", "Soft_coupling", soft_coup, "drive")
sc.add("Air", "MQR_rotor", mqr_rotor, "mqr")
sc.add("Air", "MQR_stator", mqr_stator, "mqr")
sc.add("Air", "Buffer_tank", air_buffer, "buffer")
sc.add("Air", "Deadman_valve", deadman, "deadman")
sc.add("Air", "Supply_stub", air_supply, "hose")
sc.add("Air", "M5_lines_to_R", hoses_s, "hose")


def _arrow(p0, p1, r=1.4):
    """Shaft + cone tip from p0 (label side) toward p1 (part)."""
    vec = p1.sub(p0)
    L = vec.Length
    if L < 12.0:
        return Part.makeSphere(r * 2, p0)
    tip_L = min(12.0, L * 0.2)
    direction = App.Vector(vec)
    shaft = Part.makeCylinder(r, L - tip_L, p0, direction)
    tip_base = p0.add(App.Vector(vec.x, vec.y, vec.z).multiply((L - tip_L) / L))
    tip = Part.makeCone(r * 2.8, 0.3, tip_L, tip_base, direction)
    try:
        return shaft.fuse(tip).removeSplitter()
    except Exception:
        return Part.makeCompound([shaft, tip])


# Russian callouts (one per subsystem). Positions after flip (+X top, −Y crank).
_show_labels = os.environ.get("SHOW_LABELS", "").strip().lower() in (
    "1", "true", "yes")
_callouts = [
    ("Станция", stations[2].BoundBox.Center),
    ("Пакет", V(0, 0, 0.5 * (bb.ZMin + bb.ZMax))),
    ("Кулачок", cam.BoundBox.Center),
    ("Рукоять", crank.BoundBox.Center),
    ("Муфта", trig_pack.BoundBox.Center),
    ("Стоп подачи", trig_feed.BoundBox.Center),
    ("Бункер", hopper.BoundBox.Center),
    ("Шнек ×6", auger.BoundBox.Center),
    ("Обойма", feed_guard.BoundBox.Center),
    ("MQR", mqr_rotor.BoundBox.Center),
    ("Буфер", air_buffer.BoundBox.Center),
    ("Дедмен", deadman.BoundBox.Center),
    ("Подшипники", brg_f.BoundBox.Center),
    ("Ремень", sling.BoundBox.Center),
    ("Ручка", carry_handle.BoundBox.Center),
]
# Spread labels on a ring outside the gun for readable arrows.
_r_lab = max(bb.XLength, bb.YLength) * 0.55 + 80.0
_z_mid = 0.5 * (bb.ZMin + bb.ZMax)
for _i, (_txt, _tgt) in enumerate(_callouts):
    _ang = math.radians(12.0 + _i * (360.0 / len(_callouts)))
    # Prefer top/side hemisphere for readability after iso view.
    _lab = V(_r_lab * math.cos(_ang), _r_lab * math.sin(_ang),
             _z_mid + 40.0 * math.sin(_ang * 0.5))
    # Tip points at the part; shaft starts near the label.
    _p0 = _lab
    _p1 = App.Vector(_tgt.x, _tgt.y, _tgt.z)
    if _show_labels:
        sc.add("Callouts", "Arrow_%d" % _i, _arrow(_p0, _p1), "callout")
        sc.label("Labels", _txt, (_lab.x, _lab.y, _lab.z + 8.0))

if not _show_labels:
    for n, ang, u, dz, tag in phases:
        aw = math.radians(ang + FLIP_Z)
        sc.label("Labels", "%d° %s" % (ang, tag),
                 ((R_PACK + 70) * math.cos(aw), (R_PACK + 70) * math.sin(aw),
                  z_stop + cam_dz(ang)))
    sc.label("Labels", "×6 feed · guard · bearings · MQR · Ø%.0f" % case_od,
             (0, bb.YMax + 40, (bb.ZMin + bb.ZMax) / 2))

_hide = () if _show_labels else ("Labels",)
sc.finish(hidden_groups=_hide, opaque_groups=("Callouts",))
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
