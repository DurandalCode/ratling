# -*- coding: utf-8 -*-
"""
Printed mass of STL parts without a slicer: a rough slicer of our own, for docs/weights.md (plain Python).

Each 0.2 mm layer is cut from the mesh: walls (WALLS loops of LW) and the solid skins (where the layer is not
covered TOP layers above and BOT below) count solid, the rest at the infill fraction. Matches Bambu Studio
within ~1 % on the pistol (489 g against 485) and reproduces the v4.4 module's 74.1 g.

    pip install trimesh shapely
    python3 tools/print_mass.py WALLS INFILL FLOW part.stl ...     # e.g. 5 0.6 1.0 (strong), 6 1.0 1.05 (airtight)
Prints one JSON line per part: volume, grams, solid and infill cm3 (PETG 1.27 g/cm3).
"""
import json, sys
import numpy as np
import trimesh
from shapely.ops import unary_union

LW, H, TOP, BOT, RHO = 0.43, 0.2, 5, 3, 1.27


def layers(path):
    m = trimesh.load(path)
    z0, z1 = m.bounds[0][2], m.bounds[1][2]
    n = int(round((z1 - z0) / H))
    hs = [H * (i + 0.5) for i in range(n)]
    secs = m.section_multiplane([0, 0, z0], [0, 0, 1], hs)
    out = []
    for s in secs:
        try:
            out.append(unary_union(s.polygons_full).buffer(0) if s is not None and len(s.polygons_full) else None)
        except ValueError:                   # a broken section: take the layer below
            out.append(out[-1] if out else None)
    return m, out


def mass(path, walls, infill, flow=1.0):
    m, L = layers(path)
    n = len(L)
    solid = inf = 0.0
    for i, f in enumerate(L):
        if f is None or f.is_empty:
            continue
        core = f.buffer(-walls * LW, join_style=2)
        cov = core
        for j in (i + TOP, i - BOT):
            g = L[j] if 0 <= j < n else None
            cov = cov.intersection(g) if g is not None else cov.intersection(core.buffer(-1e6))
        a = cov.area if not cov.is_empty else 0.0
        solid += (f.area - a) * H
        inf += a * H
    return {"part": path.rsplit("/", 1)[-1], "V_cm3": round(m.volume / 1000, 1),
            "g": round((solid + infill * inf) / 1000 * RHO * flow, 1),
            "solid_cm3": round(solid / 1000, 1), "infill_cm3": round(inf / 1000, 1)}


walls, infill, flow = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
for p in sys.argv[4:]:
    print(json.dumps(mass(p, walls, infill, flow)), flush=True)
