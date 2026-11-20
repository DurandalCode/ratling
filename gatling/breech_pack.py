# -*- coding: utf-8 -*-
"""
Dense pack of the real gatling linear-breech station (not a block silhouette).

Loads gatling/linear_breech.py as a library (closed pose, PACK_STATION: guides
on round rail feet, rails end at the muzzle) and places six copies on a ring.
Rails / AirTAC point radial **in** (feed +Y out) so the barrel-end transverse
shrinks below the mitrailleuse pack circles (J Ø192.5 / G Ø198). Every station
part clears its neighbours by CLEAR. Barrel-clamp rings stay inside CLAMP_OD
(flush M3, no external bolt lugs).

2026-11-19: re-laid for the 200 mm chamber station. R 58.5 (pneumatic core
alone) let the guide plates, rails and clamp feet of neighbours overlap; the
rail feet now set the floor (~66.3) and R is pinned to breech_mechanism's 67.

2026-11-20: the AirTAC rides its carriage behind the rear plug (breech_mechanism,
plan question 3), so it is cut off with everything aft of the plug face; the
station's under-rail cradle is no longer drawn. The rear barrel-plate moves
ahead of the breech clamps (it overlapped the closed QEVs by ~22 cm3); in the
mechanism it carries the rim gear of the star drive.

Overall station length is pinned to TARGET_L: clip everything aft of the
rear-plug face (open-stroke rail stubs, carriage thumb, AirTAC overhang) and
set BARREL_SHOW so the barrel tip lands at station ZMin + TARGET_L. Product
skin follows classic Gatling (1862–80s): front barrel-plate at the muzzles,
rear barrel-plate at the breech faces, barrels bare between them, translucent
breech casing only over the QEV travel — not a full-length tube (M134 contrast:
multi mid-clamps + enclosed receiver, not used here).

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_pack.py').read())"

Exports: exports/gatling_breech_pack/
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

OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_pack")
NAME = "gatling_breech_pack"

TARGET_L = 750.0              # overall pack length (Z), mm — via BARREL_SHOW only
BARREL_SHOW_DEFAULT = 160.0   # linear_breech default
BARREL_SHOW_L500 = 328.1      # previous pack at TARGET_L=500 (aft-clipped)
V = App.Vector

GATLING_LINEAR_BREECH_LIBRARY = True
PACK_STATION = True
SHOW_OPEN = False
# Probe once for z_stop / rear-plug face, then set BARREL_SHOW for TARGET_L.
BARREL_SHOW = BARREL_SHOW_DEFAULT
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin
# After clipping aft of the rear plug: L = (z_stop + BARREL_SHOW) - Z_AFT_CLIP.
BARREL_SHOW = TARGET_L - (z_stop - Z_AFT_CLIP)
assert BARREL_SHOW > 50.0, "BARREL_SHOW too short for TARGET_L"
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_pack")
NAME = "gatling_breech_pack"
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin

N = 6
CLEAR = 0.5
DESIGN_R = PACK_PITCH
MITRA_J_OD = 192.5
MITRA_G_OD = 198.0
PREV_R = 61.51
PREV_BARREL_OD = 199.6
BARREL_OD_SLACK = 2.0
L_SLACK = 0.6                 # BoundBox / clip tolerance around TARGET_L
PREV_SKIN_W = 172.0           # skin W at R 58.5 (2026-11-16, hub parts overlapping)


def clip_aft(shape, z_min):
    """Drop everything strictly behind the rear-plug face (keep Z >= z_min)."""
    if shape is None or shape.isNull():
        return shape
    bb = shape.BoundBox
    if bb.ZMin >= z_min - 1e-6:
        return shape
    # Huge box covering Z < z_min; cut it away.
    cut = Part.makeBox(4000, 4000, 4000, V(-2000, -2000, z_min - 4000))
    out = shape.cut(cut)
    if out.isNull() or out.Volume <= 1e-6:
        return None
    return out.removeSplitter()


def clip_list(parts, z_min):
    out = []
    for p in parts:
        c = clip_aft(p.copy(), z_min)
        if c is not None:
            out.append(c)
    return out


# Every station part must clear the neighbours (CLEAR). The AirTAC sits on the
# carriage behind the rear plug (breech_mechanism) and is cut off here.
_core_raw = [qev_closed[k] for k in qev_closed] + [
    fixed_barrel, rails_s, barrel_clamp, barrel_collar]
_core_parts = clip_list(_core_raw, Z_AFT_CLIP)
_station_parts = list(_core_parts)
core0 = Part.makeCompound([p.copy() for p in _core_parts])
station0 = Part.makeCompound([p.copy() for p in _station_parts])
barrel0 = Part.makeCompound(clip_list(
    [barrel_clamp, barrel_collar, fixed_barrel], Z_AFT_CLIP))
st0_bb = station0.BoundBox
aft_trim = abs(min(p.BoundBox.ZMin for p in _core_raw) - Z_AFT_CLIP)


def place_shape(shape, R, ang_deg):
    """Rails / AirTAC (−Y) toward pack axis; feed (+Y) radial out."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = shape.copy()
    tx, ty = ux, uy
    s.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(tx, ty)))
    s.translate(V(R * ux, R * uy, 0))
    return s


def pack_of(shape, R):
    return [place_shape(shape, R, k * 60.0) for k in range(N)]


def min_neighbour_gap(shapes):
    g = 1e9
    for i in range(N):
        for j in range(i + 1, N):
            d = shapes[i].distToShape(shapes[j])[0]
            if d < g:
                g = d
    return g


def tess_max_r(shape, defl=1.0):
    pts = shape.tessellate(defl)[0]
    return max(math.hypot(p.x, p.y) for p in pts)


def zone_max_r(shapes, z0, z1, defl=1.0):
    r = 0.0
    slab = Part.makeBox(4000, 4000, z1 - z0, V(-2000, -2000, z0))
    for s in shapes:
        c = s.common(slab)
        if c.Volume <= 1e-6:
            continue
        pts = c.tessellate(defl)[0]
        if not pts:
            continue
        r = max(r, max(math.hypot(p.x, p.y) for p in pts))
    return r


try:
    SEARCH_R
except NameError:
    SEARCH_R = False         # set True to re-binsearch the floor over core0
# Floor 66.3: the Ø15 rail feet of the guides and barrel clamps (core alone: 58.5).
# Pinned to breech_mechanism's R (its 1 mm steps from 66 land on 67), so the cam
# liner and this view describe one pack.
PINNED_R = 67.00
if SEARCH_R:
    r_lo, r_hi = 50.0, DESIGN_R + 10.0
    assert min_neighbour_gap(pack_of(core0, r_hi)) >= CLEAR, "hi R not clear for core"
    for _ in range(14):
        mid = 0.5 * (r_lo + r_hi)
        if min_neighbour_gap(pack_of(core0, mid)) >= CLEAR:
            r_hi = mid
        else:
            r_lo = mid
    R_PACK = r_hi
else:
    R_PACK = PINNED_R

cores = pack_of(core0, R_PACK)
stations = pack_of(station0, R_PACK)
barrels = pack_of(barrel0, R_PACK)
gap_core = min_neighbour_gap(cores)
# Rails may be clipped to stubs; still report neighbour gap of clipped rails.
_rails_clipped = clip_aft(rails_s.copy(), Z_AFT_CLIP)
gap_rails = (min_neighbour_gap(pack_of(_rails_clipped, R_PACK))
             if _rails_clipped is not None else float("nan"))

pack = Part.makeCompound(stations)
bb_stations = pack.BoundBox

z_b0, z_b1 = z_stop, z_stop + BARREL_SHOW
barrel_od = 2.0 * zone_max_r(stations, z_b0, z_b1)
barrel_od_hw = 2.0 * zone_max_r(barrels, z_b0, z_b1)
full_od = 2.0 * tess_max_r(pack)
barrel_vs_prev = PREV_BARREL_OD - barrel_od
barrel_vs_j = MITRA_J_OD - barrel_od
barrel_vs_g = MITRA_G_OD - barrel_od
barrel_len = BARREL_SHOW

# --- classic Gatling skin (1862–80s): front/rear barrel-plates + breech casing
# Refs: US36836 / 1878 Ordnance — front & rear barrel-plates on the shaft;
# breech-casing over lock/carrier only; barrels bare between plates.
# Contrast M134: multi mid-clamps + full enclosed receiver — not drawn.
PLATE_T = 14.0                # front / rear barrel-plate thickness
PLATE_LIP = 1.5               # front plate past barrel tip
PLATE_RIM = 3.0               # radial past barrel OD at R_PACK (tight)
CASE_WALL = 2.0               # min printable casing wall
CASE_CLEAR = 0.5              # radial clear over chamber pack (was 2.0)
CASE_OVERLAP = 18.0           # casing overlaps rear plate slightly forward
z_tip = z_stop + BARREL_SHOW
z_stroke_end = qev_closed["Carriage"].BoundBox.ZMin - STROKE
# Front barrel-plate (muzzle clamp / front disk).
z_front0 = z_tip - PLATE_T + PLATE_LIP
z_front1 = z_tip + PLATE_LIP
# Rear barrel-plate just ahead of the breech clamps (on the barrels and rails);
# in breech_mechanism it is the rim gear of the star drive (R 90 pitch, m 1.5).
REAR_PLATE_T = 8.0
REAR_PLATE_R = 91.5
z_rear0 = barrel_clamp.BoundBox.ZMax + 0.6
z_rear1 = z_rear0 + REAR_PLATE_T
# Breech casing: only over QEV / open-stroke, not along the barrels.
z_case1 = z_stop - PLATE_T * 0.35 + CASE_OVERLAP
z_case0 = z_stroke_end

r_plate = R_PACK + BARREL_OD / 2 + PLATE_RIM
# Casing must clear fat chambers on the ring (not just bare barrels).
r_case_id = max(0.5 * barrel_od, R_PACK + CH_OD / 2) + CASE_CLEAR
r_case_od = r_case_id + CASE_WALL
hub_r = max(6.0, R_PACK - BARREL_OD / 2 - 4.0)


def barrel_plate(z0, z1, od_r):
    """Classic circular barrel-plate: 6 bores + hub lightening."""
    disc = Part.makeCylinder(od_r, z1 - z0, V(0, 0, z0))
    for k in range(N):
        a = math.radians(k * 60.0)
        bx, by = R_PACK * math.cos(a), R_PACK * math.sin(a)
        disc = disc.cut(Part.makeCylinder(
            BARREL_OD / 2 + 0.35, (z1 - z0) + 4.0, V(bx, by, z0 - 2.0)))
    disc = disc.cut(Part.makeCylinder(hub_r, (z1 - z0) + 4.0, V(0, 0, z0 - 2.0)))
    return disc.removeSplitter()


front_plate = barrel_plate(z_front0, z_front1, r_plate)
rear_plate = barrel_plate(z_rear0, z_rear1, REAR_PLATE_R)
for _k in range(N):
    for _x, _y in rail_centers():
        _rc = place_shape(Part.Vertex(V(_x, _y, 0)), R_PACK, _k * 60.0).Point
        rear_plate = rear_plate.cut(Part.makeCylinder(RAIL_HOLE / 2, 30, V(_rc.x, _rc.y, z_rear0 - 5)))
rear_plate = rear_plate.removeSplitter()
# The plate holds the barrels and rails in its bores; clearance is to the rest.
_qev_clamps = Part.makeCompound(clip_list([qev_closed[k] for k in qev_closed] + [barrel_clamp, barrel_collar], Z_AFT_CLIP))
rear_plate_gap = min(rear_plate.distToShape(s)[0] for s in pack_of(_qev_clamps, R_PACK))
# Translucent breech casing + cascabel disk (1878 breech-casing cue).
breech_casing = tube(2.0 * r_case_od, 2.0 * r_case_id, z_case0, z_case1)
cascabel = Part.makeCylinder(r_case_od, 6.0, V(0, 0, z_case0 - 6.0))
cascabel = cascabel.cut(Part.makeCylinder(hub_r + 2.0, 10.0, V(0, 0, z_case0 - 8.0)))
breech_casing = breech_casing.fuse(cascabel).removeSplitter()

assembly = Part.makeCompound([pack, front_plate, rear_plate, breech_casing])
bb = assembly.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
plate_od = 2.0 * r_plate
case_od = 2.0 * r_case_od
station_L = bb_stations.ZLength
bare_barrel_L = z_front0 - z_rear1

clamp_ring_od = 2.0 * (R_PACK + CLAMP_OD / 2)
checks = [
    ("six stations", len(stations) == 6),
    ("station neighbour gap %.2f mm >= %.2f (all parts)" % (gap_core, CLEAR),
     gap_core >= CLEAR - 1e-6),
    ("pack volume", pack.Volume > 1e5),
    ("station L %.1f ≈ %.0f (±%.1f)" % (station_L, TARGET_L, L_SLACK),
     abs(station_L - TARGET_L) <= L_SLACK),
    ("aft clipped at rear plug (ZMin≈%.1f)" % Z_AFT_CLIP,
     abs(st0_bb.ZMin - Z_AFT_CLIP) <= 0.6),
    ("barrel Ø %.1f within clamp rings Ø%.1f (≤ +%.1f)"
     % (barrel_od, clamp_ring_od, BARREL_OD_SLACK),
     barrel_od <= clamp_ring_od + BARREL_OD_SLACK + 1e-6),
    ("front barrel-plate solid", front_plate.Volume > 500),
    ("rear barrel-plate solid", rear_plate.Volume > 500),
    ("rear barrel-plate ahead of the breech clamps, clear of QEVs and clamps (%.2f)" % rear_plate_gap,
     rear_plate_gap >= CLEAR - 1e-6),
    ("breech casing solid", breech_casing.Volume > 1e3),
    ("barrels bare between plates (%.0f mm > 200)" % bare_barrel_L,
     bare_barrel_L > 200.0),
    ("casing starts at breech, not muzzle (case ZMax %.0f << tip %.0f)"
     % (z_case1, z_tip),
     z_case1 < z_tip - 200.0),
    ("casing covers open stroke (ZMin≈%.1f)" % z_stroke_end,
     abs(breech_casing.BoundBox.ZMin - (z_case0 - 6.0)) <= 1.0),
]
report = [
    NAME,
    "  sketch                 : dense pack of REAL linear_breech stations (closed)",
    "  source                 : gatling/linear_breech.py + fat_coax_qev.py",
    "  stations               : %d closed; no bench feet / no wheeled carriage" % N,
    "  orientation            : rails radial IN, feed OUT (barrel end narrower; guides on rail feet)",
    "  aft trim               : clip Z < rear-plug face (%.1f); cut ≈%.0f mm "
    "(open-stroke rails / thumb / AirTAC overhang)"
    % (Z_AFT_CLIP, aft_trim),
    "  product skin           : classic Gatling 1862–80s (front+rear barrel-plates, "
    "bare barrels, breech casing only) — not full-length tube; not M134 mid-clamps",
    "  refs                   : US36836 / 1878 Ordnance Gatling description",
    "  design PACK_PITCH      : %.1f mm" % DESIGN_R,
    "  pack R                 : %.2f mm (%s; station gap %.2f mm; rail gap %.2f mm)"
    % (R_PACK, "searched floor" if SEARCH_R else "pinned = breech_mechanism",
       gap_core, gap_rails),
    "  R floor                : rail feet Ø%.0f of guides + barrel clamps ≈66.3; "
    "pneumatic core alone 58.5 (yoke/plug ears r≈33)" % BUSH_OD,
    "  hub                    : AirTAC rides the carriage behind the rear plug (breech_mechanism);"
    " cut off here",
    "  was skin W (R 58.5)    : %.0f → now %.0f x %.0f"
    % (PREV_SKIN_W, gun_W, gun_H),
    "  barrel length (show)   : %.1f mm (station L=%.0f)"
    % (barrel_len, TARGET_L),
    "  front barrel-plate     : Z %.1f…%.1f; Ø%.1f (muzzle)"
    % (z_front0, z_front1, plate_od),
    "  rear barrel-plate      : Z %.1f…%.1f; Ø%.1f (ahead of the breech clamps; rim gear in the mechanism)"
    % (z_rear0, z_rear1, 2 * REAR_PLATE_R),
    "  bare barrels           : %.0f mm between plates" % bare_barrel_L,
    "  breech casing          : Z %.1f…%.1f; Ø%.1f wall %.1f; translucent "
    "(open QEV stroke → rear plate)"
    % (z_case0 - 6.0, z_case1, case_od, CASE_WALL),
    "  station bbox           : %.0f x %.0f x %.0f mm (X x Y x Z)"
    % (st0_bb.XLength, st0_bb.YLength, st0_bb.ZLength),
    "  overall LxWxH          : %.0f x %.0f x %.0f mm (Z x Y x X, with skin)"
    % (gun_L, gun_W, gun_H),
    "  station-only L         : %.0f mm (TARGET_L)" % station_L,
    "  full pack Ø (tess)     : %.1f mm" % full_od,
    "  width at barrels       : Ø%.1f mm (barrel-Z tess; hw-only Ø%.1f)"
    % (barrel_od, barrel_od_hw),
    "  was (rails out)        : barrel Ø%.1f @ R%.2f → now −%.1f mm"
    % (PREV_BARREL_OD, PREV_R, barrel_vs_prev),
    "  vs mitrailleuse        : J Ø%.1f (−%.1f); G Ø%.1f (−%.1f)"
    % (MITRA_J_OD, barrel_vs_j, MITRA_G_OD, barrel_vs_g),
    "  not drawn              : hopper, MQR, crank, open ghost, bench feet, carriage",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["st_a"] = ((0.92, 0.50, 0.20), 40)
FV.STYLES["st_b"] = ((0.80, 0.55, 0.28), 48)
FV.STYLES["st_c"] = ((0.70, 0.48, 0.32), 55)
FV.STYLES["plate"] = ((0.42, 0.44, 0.48), 8)
FV.STYLES["casing"] = ((0.78, 0.72, 0.55), 72)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Pack", "Station_%d" % (i + 1), st, ("st_a", "st_b", "st_c")[i % 3])
sc.add("Skin", "Front_barrel_plate", front_plate, "plate")
sc.add("Skin", "Rear_barrel_plate", rear_plate, "plate")
sc.add("Skin", "Breech_casing", breech_casing, "casing")

for text, pos in [
    ("classic Gatling skin, barrel %.0f" % barrel_len,
     (0, bb.YMax + 25, bb.ZMin + 50)),
    ("plates + breech casing; barrels bare %.0f mm" % bare_barrel_L,
     (0, bb.YMax + 25, (bb.ZMin + bb.ZMax) / 2)),
    ("L≈%.0f W≈%.0f H≈%.0f" % (gun_L, gun_W, gun_H),
     (bb.XMax + 20, 0, (bb.ZMin + bb.ZMax) / 2)),
    ("дуло →", (0, bb.YMax + 15, bb.ZMax - 40)),
]:
    sc.label("Labels", text, pos)

sc.finish(hidden_groups=("Labels",), opaque_groups=())
doc = sc.doc
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart

pack_mesh = assembly.copy()
pack_mesh.translate(V(0, 0, -pack_mesh.BoundBox.ZMin))
pack_mesh.exportStep(os.path.join(OUT_DIR, "breech_pack.step"))
MeshPart.meshFromShape(Shape=pack_mesh, LinearDeflection=0.3, AngularDeflection=0.4).write(
    os.path.join(OUT_DIR, "breech_pack.stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech pack has [FAIL] checks")
