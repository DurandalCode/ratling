# -*- coding: utf-8 -*-
"""
Dense pack of the real gatling linear-breech station (not a block silhouette).

Loads gatling/linear_breech.py as a library (closed pose) and places six copies
on a ring. Rails / AirTAC point radial **in** (feed +Y out) so the barrel-end
transverse shrinks below the mitrailleuse pack circles (J Ø192.5 / G Ø198).
Carriage / rails / AirTAC may duplicate near the hub — only the core
(chamber + plugs + yoke + barrel clamps) must clear CLEAR between neighbours.
Barrel drawn length is 2× the station default (`BARREL_SHOW` 320 vs 160) — pack
Ø at the barrels must stay ~171.6. Real solids only; no gun_sketch blocks,
bench feet, or carriage.

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

GATLING_LINEAR_BREECH_LIBRARY = True
SHOW_OPEN = False
BARREL_SHOW_DEFAULT = 160.0   # linear_breech default (ahead of breech face)
BARREL_SHOW = 2.0 * BARREL_SHOW_DEFAULT
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_pack")
NAME = "gatling_breech_pack"

V = App.Vector
N = 6
CLEAR = 0.5
DESIGN_R = PACK_PITCH
# Mitrailleuse live pack circles (chamber circumscribed, docs/pack.md).
MITRA_J_OD = 192.5            # layout J, 16 barrels
MITRA_G_OD = 198.0            # layout G, 19 barrels
# Previous rails-out pack (feed in) for delta reporting.
PREV_R = 61.51
PREV_BARREL_OD = 199.6        # barrel-Z tess Ø, rails-out @ PREV_R
# Rails-in short-barrel pack (BARREL_SHOW 160) — Ø ceiling to keep.
RAILS_IN_BARREL_OD = 171.6
BARREL_OD_SLACK = 1.0         # allow tess noise; must not inflate past mitrailleuse

# Core must clear; rails / carriage / AirTAC may overlap at the hub.
CORE_KEYS = [k for k in qev_closed if k != "Carriage"]
_core_parts = [qev_closed[k] for k in CORE_KEYS] + [
    barrel_clamp, barrel_collar, fixed_barrel,
]
_rail_parts = [
    qev_closed["Carriage"], rails_s, cradle,
    vent_body, vent_fittings, vent_plunger,
]
_station_parts = _core_parts + _rail_parts
core0 = Part.makeCompound([p.copy() for p in _core_parts])
station0 = Part.makeCompound([p.copy() for p in _station_parts])
barrel0 = Part.makeCompound([
    barrel_clamp.copy(), barrel_collar.copy(), fixed_barrel.copy(),
])
st0_bb = station0.BoundBox


def place_shape(shape, R, ang_deg):
    """Rails / AirTAC (−Y) toward pack axis; feed (+Y) radial out."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = shape.copy()
    # +Y → outward (+radial); −Y (rails) → inward
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
    """Farthest XY radius of solids clipped to [z0, z1]."""
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


# Densest R: binary search on CORE clearance (rails may duplicate).
try:
    SEARCH_R
except NameError:
    SEARCH_R = False
PINNED_R = 66.29              # from SEARCH_R (core gap ≈ 0.50 mm)
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
gap_rails = min_neighbour_gap(pack_of(rails_s, R_PACK))

pack = Part.makeCompound(stations)
bb = pack.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength

# Width at barrels: tess Ø of all station solids in the barrel Z window.
z_b0, z_b1 = z_stop, z_stop + BARREL_SHOW
barrel_od = 2.0 * zone_max_r(stations, z_b0, z_b1)
barrel_od_hw = 2.0 * zone_max_r(barrels, z_b0, z_b1)
full_od = 2.0 * tess_max_r(pack)
# Mitrailleuse ceiling = smaller live pack (J).
mitra_ceil = MITRA_J_OD
barrel_vs_prev = PREV_BARREL_OD - barrel_od
barrel_vs_j = MITRA_J_OD - barrel_od
barrel_vs_g = MITRA_G_OD - barrel_od
barrel_len = BARREL_SHOW
barrel_len_was = BARREL_SHOW_DEFAULT

checks = [
    ("six stations", len(stations) == 6),
    ("core neighbour gap %.2f mm >= %.2f" % (gap_core, CLEAR),
     gap_core >= CLEAR - 1e-6),
    ("pack volume", pack.Volume > 1e5),
    ("barrel show 2x (%.0f == 2×%.0f)" % (barrel_len, barrel_len_was),
     abs(barrel_len - 2.0 * barrel_len_was) < 1e-6),
    ("barrel Ø %.1f ≈ rails-in Ø%.1f (≤ +%.1f)"
     % (barrel_od, RAILS_IN_BARREL_OD, BARREL_OD_SLACK),
     barrel_od <= RAILS_IN_BARREL_OD + BARREL_OD_SLACK + 1e-6),
    ("barrel Ø %.1f < mitrailleuse J Ø%.1f" % (barrel_od, MITRA_J_OD),
     barrel_od < MITRA_J_OD - 1e-6),
    ("barrel Ø %.1f < mitrailleuse G Ø%.1f" % (barrel_od, MITRA_G_OD),
     barrel_od < MITRA_G_OD - 1e-6),
]
report = [
    NAME,
    "  sketch                 : dense pack of REAL linear_breech stations (closed)",
    "  source                 : gatling/linear_breech.py + fat_coax_qev.py",
    "  stations               : %d closed; no bench feet / no wheeled carriage" % N,
    "  orientation            : rails/AirTAC radial IN, feed OUT "
    "(barrel end narrower; rail duplicates at QEV OK)",
    "  design PACK_PITCH      : %.1f mm" % DESIGN_R,
    "  dense pack R           : %.2f mm (core gap %.2f mm; rail gap %.2f mm)"
    % (R_PACK, gap_core, gap_rails),
    "  tightened vs design    : R %.1f → %.2f mm" % (DESIGN_R, R_PACK),
    "  barrel length (show)   : %.0f → %.0f mm (2× ahead of breech face)"
    % (barrel_len_was, barrel_len),
    "  station bbox           : %.0f x %.0f x %.0f mm (X x Y x Z)"
    % (st0_bb.XLength, st0_bb.YLength, st0_bb.ZLength),
    "  overall LxWxH          : %.0f x %.0f x %.0f mm (Z x Y x X)"
    % (gun_L, gun_W, gun_H),
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

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Pack", "Station_%d" % (i + 1), st, ("st_a", "st_b", "st_c")[i % 3])

for text, pos in [
    ("6x rails-IN @ R%.1f, barrel %.0f→%.0f"
     % (R_PACK, barrel_len_was, barrel_len),
     (0, bb.YMax + 25, bb.ZMin + 50)),
    ("barrel Ø%.0f (keep ~%.0f)" % (barrel_od, RAILS_IN_BARREL_OD),
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

pack_mesh = pack.copy()
pack_mesh.translate(V(0, 0, -pack_mesh.BoundBox.ZMin))
pack_mesh.exportStep(os.path.join(OUT_DIR, "breech_pack.step"))
MeshPart.meshFromShape(Shape=pack_mesh, LinearDeflection=0.3, AngularDeflection=0.4).write(
    os.path.join(OUT_DIR, "breech_pack.stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech pack has [FAIL] checks")
