#!/usr/bin/env python3
"""Check how an STL lies on the bed before it is sliced.

    tools/orient_check.py [--support] [--search] STL [STL ...]     (--search: the three best of six faces to put down)

The generators export every part in its print orientation (lowest point at z = 0), and a wrong face on the bed
slices without any complaint: the ring that hung on its boss, the bracket in the air. This reads the mesh and
says, per part:

  FAIL  overhang: area of faces steeper than 45 deg from the vertical above the first layers, more than
        max(OVERHANG_MM2, OVERHANG_FRAC of the bed contact), with no supports asked for
  WARN  bed contact under SMALL_BED_MM2: a tall part on a tiny footprint (it may snap off or wobble); or the
        STL floats off z = 0 (Bambu Studio drops it on the bed, the checks are made from its lowest point)
  OK    otherwise; with supports the overhang is only reported

Plain Python, no FreeCAD: binary or ASCII STL. print_plate.py runs it on every part it lays out.
"""

import re
import struct
import sys

BED_Z = 0.3             # faces this close to z = 0 are the first layer's contact
OVERHANG_COS = 0.7071   # a downward face steeper than 45 deg prints in the air
OVERHANG_MM2 = 300.0
OVERHANG_FRAC = 0.08
SMALL_BED_MM2 = 30.0
Z_TOL = 0.05


def triangles(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        v = [tuple(map(float, m)) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
        return [v[i:i + 3] for i in range(0, len(v) - 2, 3)]
    n = struct.unpack("<I", data[80:84])[0]
    out = []
    for i in range(n):
        f = struct.unpack("<12f", data[84 + 50 * i:84 + 50 * i + 48])
        out.append([f[3:6], f[6:9], f[9:12]])
    return out


def measure(path):
    tris = triangles(path)
    zmin = min(v[2] for t in tris for v in t)
    zmax = max(v[2] for t in tris for v in t)
    bed = over = 0.0
    for a, b, c in tris:
        ux, uy, uz = (b[i] - a[i] for i in range(3))
        vx, vy, vz = (c[i] - a[i] for i in range(3))
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        ln = (nx * nx + ny * ny + nz * nz) ** 0.5
        if ln < 1e-12:
            continue
        area, cz = ln / 2, nz / ln
        if cz < -OVERHANG_COS:
            if max(a[2], b[2], c[2]) - zmin <= BED_Z:
                bed += area
            else:
                over += area
    return {"zmin": zmin, "height": zmax - zmin, "bed_mm2": bed, "overhang_mm2": over}


AXES = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1)}


def measure_down(path, d):
    """The same numbers with the part's direction `d` (a unit axis) turned onto the bed: its face with normal d down."""
    tris = triangles(path)
    h = lambda v: -(v[0] * d[0] + v[1] * d[1] + v[2] * d[2])
    zmin = min(h(v) for t in tris for v in t)
    zmax = max(h(v) for t in tris for v in t)
    bed = over = 0.0
    for a, b, c in tris:
        ux, uy, uz = (b[i] - a[i] for i in range(3))
        vx, vy, vz = (c[i] - a[i] for i in range(3))
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        ln = (nx * nx + ny * ny + nz * nz) ** 0.5
        if ln < 1e-12:
            continue
        if (nx * d[0] + ny * d[1] + nz * d[2]) / ln > OVERHANG_COS:
            if max(h(a), h(b), h(c)) - zmin <= BED_Z:
                bed += ln / 2
            else:
                over += ln / 2
    return {"zmin": 0.0, "height": zmax - zmin, "bed_mm2": bed, "overhang_mm2": over}


def search(path, support=False):
    """All six axis directions, best first: [(score, name, measures)]; fewest overhang, credit for bed contact up to 500 mm2."""
    rows = []
    for name, d in AXES.items():
        m = measure_down(path, d)
        rows.append((m["overhang_mm2"] - 0.3 * min(m["bed_mm2"], 500.0), name, m))
    return sorted(rows, key=lambda r: r[0])


def verdict(m, support=False):
    """(OK / WARN / FAIL, why)."""
    limit = max(OVERHANG_MM2, OVERHANG_FRAC * m["bed_mm2"])
    if m["overhang_mm2"] > limit and not support:
        return "FAIL", "%.0f mm2 of overhang (limit %.0f) and no supports: turn it over or ask for supports" % (m["overhang_mm2"], limit)
    if m["bed_mm2"] < SMALL_BED_MM2:
        return "WARN", "only %.0f mm2 on the bed for a %.0f mm tall part" % (m["bed_mm2"], m["height"])
    if abs(m["zmin"]) > Z_TOL:
        return "WARN", "the STL floats at z = %.2f (bed %.0f mm2, overhang %.0f mm2)" % (m["zmin"], m["bed_mm2"], m["overhang_mm2"])
    return "OK", "bed %.0f mm2, overhang %.0f mm2%s" % (m["bed_mm2"], m["overhang_mm2"], " (supports)" if support else "")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    support = "--support" in args
    paths = [a for a in args if not a.startswith("--")]
    worst = 0
    if "--search" in args:
        for p in paths:
            print(p)
            for _, name, m in search(p, support)[:3]:
                print("   down %s: overhang %.0f mm2, bed %.0f mm2, %.0f mm tall" % (name, m["overhang_mm2"], m["bed_mm2"], m["height"]))
        return 0
    for p in paths:
        v, why = verdict(measure(p), support)
        print("  [%s] %s: %s" % ({"OK": "OK ", "WARN": "WARN", "FAIL": "FAIL"}[v], p, why))
        worst = max(worst, {"OK": 0, "WARN": 0, "FAIL": 1}[v])
    return worst


if __name__ == "__main__":
    sys.exit(main())
