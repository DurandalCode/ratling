# -*- coding: utf-8 -*-
"""
Dense pack of the real gatling linear-breech station (not a block silhouette).

Loads gatling/linear_breech.py as a library (closed pose) and places six copies
on the smallest ring that still clears. Orientation: feed (+Y) radial **in**,
AirTAC/rails radial **out** — denser than feed-out (AirTAC would fight at the
axis). Real solids only; no gun_sketch blocks, bench feet, or carriage.

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
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_pack")
NAME = "gatling_breech_pack"

V = App.Vector
N = 6
CLEAR = 0.5
DESIGN_R = PACK_PITCH
# Pin densest orientation from survey: feed in / AirTAC out clears at R<=68.
MODE = "in"

_station_parts = list(qev_closed.values()) + [
    rails_s, barrel_clamp, barrel_collar, fixed_barrel, cradle,
    vent_body, vent_fittings, vent_plunger,
]
station0 = Part.makeCompound([p.copy() for p in _station_parts])
st0_bb = station0.BoundBox


def place_station(R, ang_deg):
    """Feed (+Y) toward pack axis; AirTAC hangs outward."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    s = station0.copy()
    # +Y → inward (−radial)
    tx, ty = -ux, -uy
    s.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(math.atan2(tx, ty)))
    s.translate(V(R * ux, R * uy, 0))
    return s


def pack_at(R):
    return [place_station(R, k * 60.0) for k in range(N)]


def min_neighbour_gap(stations):
    g = 1e9
    for i in range(N):
        for j in range(i + 1, N):
            d = stations[i].distToShape(stations[j])[0]
            if d < g:
                g = d
    return g


# Densest R (feed-in / AirTAC-out). Pin after search so re-renders stay fast.
# Search once: set SEARCH_R = True (or leave unset); result cached below.
try:
    SEARCH_R
except NameError:
    SEARCH_R = False
PINNED_R = 61.51             # from SEARCH_R run (gap ≈ 0.51 mm)
if SEARCH_R:
    r_lo, r_hi = 55.0, DESIGN_R
    assert min_neighbour_gap(pack_at(r_hi)) >= CLEAR, "design R not clear in feed-in pose"
    for _ in range(10):
        mid = 0.5 * (r_lo + r_hi)
        if min_neighbour_gap(pack_at(mid)) >= CLEAR:
            r_hi = mid
        else:
            r_lo = mid
    R_PACK = r_hi
else:
    R_PACK = PINNED_R
stations = pack_at(R_PACK)
gap = min_neighbour_gap(stations)

pack = Part.makeCompound(stations)
bb = pack.BoundBox
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength

checks = [
    ("six stations", len(stations) == 6),
    ("neighbour gap %.2f mm >= %.2f" % (gap, CLEAR), gap >= CLEAR - 1e-6),
    ("pack volume", pack.Volume > 1e5),
    ("R <= design PACK_PITCH (%.2f <= %.1f)" % (R_PACK, DESIGN_R),
     R_PACK <= DESIGN_R + 1e-6),
]
report = [
    NAME,
    "  sketch                 : dense pack of REAL linear_breech stations (closed)",
    "  source                 : gatling/linear_breech.py + fat_coax_qev.py",
    "  stations               : %d closed; no bench feet / no wheeled carriage" % N,
    "  orientation            : feed radial IN, AirTAC/rails OUT (densest clear pose)",
    "  design PACK_PITCH      : %.1f mm" % DESIGN_R,
    "  dense pack R           : %.2f mm (neighbour gap %.2f mm)" % (R_PACK, gap),
    "  tightened              : R %.1f → %.2f mm (Δ %.1f); clear %.1f mm"
    % (DESIGN_R, R_PACK, DESIGN_R - R_PACK, CLEAR),
    "  station bbox           : %.0f x %.0f x %.0f mm (X x Y x Z)"
    % (st0_bb.XLength, st0_bb.YLength, st0_bb.ZLength),
    "  overall LxWxH          : %.0f x %.0f x %.0f mm (Z x Y x X)"
    % (gun_L, gun_W, gun_H),
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
    ("6x linear_breech @ R%.1f" % R_PACK, (0, bb.YMax + 25, bb.ZMin + 50)),
    ("R %.0f→%.1f mm, gap %.1f" % (DESIGN_R, R_PACK, gap),
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
