# -*- coding: utf-8 -*-
"""
Dense pack of the real gatling linear-breech station (not a block silhouette).

Loads gatling/linear_breech.py as a library (closed pose) and places six copies
on a ring. Rails / AirTAC point radial **in** (feed +Y out) so the barrel-end
transverse shrinks below the mitrailleuse pack circles (J Ø192.5 / G Ø198).
Carriage / rails / AirTAC may duplicate near the hub — only the core
(chamber + plugs + yoke + barrel clamps) must clear CLEAR between neighbours.

Overall station length is pinned to TARGET_L: clip everything aft of the
rear-plug face (open-stroke rail stubs, carriage thumb, AirTAC overhang) and
set BARREL_SHOW so the barrel tip lands at station ZMin + TARGET_L. Then add a
muzzle adapter at the barrel tips and a translucent provisional shroud from
that adapter aft to the open-stroke end of the QEV. Pack Ø at the barrels must
stay ~171.6 aside from the thin muzzle/shroud wall.

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
RAILS_IN_BARREL_OD = 171.6
BARREL_OD_SLACK = 1.0
L_SLACK = 0.6                 # BoundBox / clip tolerance around TARGET_L


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


# Core must clear; rails / carriage / AirTAC may overlap at the hub.
CORE_KEYS = [k for k in qev_closed if k != "Carriage"]
_core_raw = [qev_closed[k] for k in CORE_KEYS] + [
    barrel_clamp, barrel_collar, fixed_barrel,
]
_rail_raw = [
    qev_closed["Carriage"], rails_s, cradle,
    vent_body, vent_fittings, vent_plunger,
]
_core_parts = clip_list(_core_raw, Z_AFT_CLIP)
_rail_parts = clip_list(_rail_raw, Z_AFT_CLIP)
_station_parts = _core_parts + _rail_parts
core0 = Part.makeCompound([p.copy() for p in _core_parts])
station0 = Part.makeCompound([p.copy() for p in _station_parts])
barrel0 = Part.makeCompound(clip_list(
    [barrel_clamp, barrel_collar, fixed_barrel], Z_AFT_CLIP))
st0_bb = station0.BoundBox
aft_trim = abs(min(p.BoundBox.ZMin for p in _core_raw + _rail_raw) - Z_AFT_CLIP)


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
    SEARCH_R = False
PINNED_R = 66.29
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

# --- muzzle adapter at barrel tips + translucent shroud to open QEV stroke end
MUZZLE_L = 24.0               # axial length of muzzle plate
MUZZLE_LIP = 2.0              # plate sits this far past the barrel tip
SHROUD_WALL = 2.0
SHROUD_CLEAR = 1.5            # radial clear over barrel-pack Ø
# Outer radius: clear the measured barrel-zone pack, then + wall (muzzle need).
r_pack = 0.5 * barrel_od
r_shroud_id = r_pack + SHROUD_CLEAR
r_shroud_od = r_shroud_id + SHROUD_WALL
z_tip = z_stop + BARREL_SHOW
z_muzzle0 = z_tip - MUZZLE_L + MUZZLE_LIP   # aft face of muzzle (shroud meets here)
z_muzzle1 = z_tip + MUZZLE_LIP             # forward face
# Open-stroke aft of the sliding carriage (unclipped library solid).
z_stroke_end = qev_closed["Carriage"].BoundBox.ZMin - STROKE

muzzle = Part.makeCylinder(r_shroud_od, z_muzzle1 - z_muzzle0, V(0, 0, z_muzzle0))
# Bore for each barrel + lightening through the hub.
for k in range(N):
    a = math.radians(k * 60.0)
    bx, by = R_PACK * math.cos(a), R_PACK * math.sin(a)
    muzzle = muzzle.cut(Part.makeCylinder(
        BARREL_OD / 2 + 0.35, (z_muzzle1 - z_muzzle0) + 4.0,
        V(bx, by, z_muzzle0 - 2.0)))
hub_r = max(8.0, R_PACK - BARREL_OD / 2 - 3.0)
muzzle = muzzle.cut(Part.makeCylinder(
    hub_r, (z_muzzle1 - z_muzzle0) + 4.0, V(0, 0, z_muzzle0 - 2.0)))
muzzle = muzzle.removeSplitter()

# Provisional casing: thin tube from muzzle aft face back to open QEV stroke end.
shroud = tube(2.0 * r_shroud_od, 2.0 * r_shroud_id, z_stroke_end, z_muzzle0)
shroud = shroud.removeSplitter()

assembly = Part.makeCompound([pack, muzzle, shroud])
bb = assembly.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
shroud_od = 2.0 * r_shroud_od
station_L = bb_stations.ZLength

checks = [
    ("six stations", len(stations) == 6),
    ("core neighbour gap %.2f mm >= %.2f" % (gap_core, CLEAR),
     gap_core >= CLEAR - 1e-6),
    ("pack volume", pack.Volume > 1e5),
    ("station L %.1f ≈ %.0f (±%.1f)" % (station_L, TARGET_L, L_SLACK),
     abs(station_L - TARGET_L) <= L_SLACK),
    ("aft clipped at rear plug (ZMin≈%.1f)" % Z_AFT_CLIP,
     abs(st0_bb.ZMin - Z_AFT_CLIP) <= 0.6),
    ("barrel Ø %.1f ≈ rails-in Ø%.1f (≤ +%.1f)"
     % (barrel_od, RAILS_IN_BARREL_OD, BARREL_OD_SLACK),
     barrel_od <= RAILS_IN_BARREL_OD + BARREL_OD_SLACK + 1e-6),
    ("muzzle solid", muzzle.Volume > 1e3),
    ("shroud solid", shroud.Volume > 1e3),
    ("shroud from muzzle aft (%.1f) to stroke end (%.1f)"
     % (z_muzzle0, z_stroke_end),
     abs(shroud.BoundBox.ZMax - z_muzzle0) <= 0.6
     and abs(shroud.BoundBox.ZMin - z_stroke_end) <= 0.6),
    ("shroud Ø %.1f ≈ barrel Ø + clear + wall (≤ %.1f)"
     % (shroud_od, barrel_od + 2.0 * (SHROUD_CLEAR + SHROUD_WALL) + 0.5),
     shroud_od <= barrel_od + 2.0 * (SHROUD_CLEAR + SHROUD_WALL) + 0.5),
]
report = [
    NAME,
    "  sketch                 : dense pack of REAL linear_breech stations (closed)",
    "  source                 : gatling/linear_breech.py + fat_coax_qev.py",
    "  stations               : %d closed; no bench feet / no wheeled carriage" % N,
    "  orientation            : rails/AirTAC radial IN, feed OUT "
    "(barrel end narrower; rail duplicates at QEV OK)",
    "  aft trim               : clip Z < rear-plug face (%.1f); cut ≈%.0f mm "
    "(open-stroke rails / thumb / AirTAC overhang)"
    % (Z_AFT_CLIP, aft_trim),
    "  design PACK_PITCH      : %.1f mm" % DESIGN_R,
    "  dense pack R           : %.2f mm (core gap %.2f mm; rail gap %.2f mm)"
    % (R_PACK, gap_core, gap_rails),
    "  barrel length (show)   : %.1f mm (station L=%.0f)"
    % (barrel_len, TARGET_L),
    "  muzzle adapter         : L=%.0f mm at tip; Ø%.1f (hub + 6× bore)"
    % (z_muzzle1 - z_muzzle0, shroud_od),
    "  shroud (provisional)   : Z %.1f → %.1f (open QEV stroke end → muzzle aft); "
    "Ø%.1f ID%.1f wall %.1f; translucent"
    % (z_stroke_end, z_muzzle0, shroud_od, 2.0 * r_shroud_id, SHROUD_WALL),
    "  station bbox           : %.0f x %.0f x %.0f mm (X x Y x Z)"
    % (st0_bb.XLength, st0_bb.YLength, st0_bb.ZLength),
    "  overall LxWxH          : %.0f x %.0f x %.0f mm (Z x Y x X, with shroud/muzzle)"
    % (gun_L, gun_W, gun_H),
    "  station-only L         : %.0f mm (TARGET_L)" % station_L,
    "  full pack Ø (tess)     : %.1f mm" % full_od,
    "  width at barrels       : Ø%.1f mm (barrel-Z tess; hw-only Ø%.1f)"
    % (barrel_od, barrel_od_hw),
    "  was (rails out)        : barrel Ø%.1f @ R%.2f → now −%.1f mm"
    % (PREV_BARREL_OD, PREV_R, barrel_vs_prev),
    "  vs mitrailleuse        : J Ø%.1f (−%.1f); G Ø%.1f (−%.1f)"
    % (MITRA_J_OD, barrel_vs_j, MITRA_G_OD, barrel_vs_g),
    "  not drawn              : hopper, MQR, crank, open ghost, bench feet",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
print("\n".join(report))

FV.STYLES["st_a"] = ((0.92, 0.50, 0.20), 40)
FV.STYLES["st_b"] = ((0.80, 0.55, 0.28), 48)
FV.STYLES["st_c"] = ((0.70, 0.48, 0.32), 55)
FV.STYLES["muzzle"] = ((0.45, 0.48, 0.52), 15)
FV.STYLES["shroud"] = ((0.75, 0.82, 0.90), 78)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Pack", "Station_%d" % (i + 1), st, ("st_a", "st_b", "st_c")[i % 3])
sc.add("Skin", "Muzzle_adapter", muzzle, "muzzle")
sc.add("Skin", "Shroud", shroud, "shroud")

for text, pos in [
    ("6x rails-IN + shroud, barrel %.0f" % barrel_len,
     (0, bb.YMax + 25, bb.ZMin + 50)),
    ("shroud Z %.0f→%.0f" % (z_stroke_end, z_muzzle0),
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
