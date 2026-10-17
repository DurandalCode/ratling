# -*- coding: utf-8 -*-
"""
Flat print mock-ups of the barrel pack layouts (pack_layouts.LAYOUTS) for a
256 x 256 bed: a Ø38 disc per barrel (Ø4 axis hole), thin bridges between
neighbours so each layout prints as one sheet. Writes exports/pack_layouts/stl/*.stl.
Run: python3 mitrailleuse/pack_mockup.py [layers]   (0.2 mm layers, default 8)
"""
import math
import os
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv, _argv = sys.argv[:1], sys.argv
LAYER = 0.2
LAYERS = int(_argv[1]) if len(_argv) > 1 else 8
BED = 256.0
BRIDGE_W = 4.0
HOLE_R = 2.0
SEG = 90

_src = open(os.path.join(REPO, "mitrailleuse", "pack_layouts.py")).read()
_ns = {"__file__": os.path.join(REPO, "mitrailleuse", "pack_layouts.py")}
exec(_src.rsplit("\nmain()", 1)[0], _ns)
P, D, LAYOUTS, bbox = _ns["P"], _ns["D"], _ns["LAYOUTS"], _ns["bbox"]


def quad(tris, a, b, c, d):
    tris += [(a, b, c), (a, c, d)]


def annulus(tris, cx, cy, h):
    ro, ri = D / 2, HOLE_R
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG
        o0 = (cx + ro * math.cos(a0), cy + ro * math.sin(a0))
        o1 = (cx + ro * math.cos(a1), cy + ro * math.sin(a1))
        i0 = (cx + ri * math.cos(a0), cy + ri * math.sin(a0))
        i1 = (cx + ri * math.cos(a1), cy + ri * math.sin(a1))
        quad(tris, o0 + (0,), o1 + (0,), o1 + (h,), o0 + (h,))      # outer wall
        quad(tris, i1 + (0,), i0 + (0,), i0 + (h,), i1 + (h,))      # hole wall
        quad(tris, o0 + (h,), o1 + (h,), i1 + (h,), i0 + (h,))      # top
        quad(tris, o1 + (0,), o0 + (0,), i0 + (0,), i1 + (0,))      # bottom


def bridge(tris, p, q, h):
    d = math.dist(p, q)
    ux, uy = (q[0] - p[0]) / d, (q[1] - p[1]) / d
    nx, ny = -uy * BRIDGE_W / 2, ux * BRIDGE_W / 2
    s, e = D / 2 - 2, d - D / 2 + 2
    A = (p[0] + ux * s + nx, p[1] + uy * s + ny)
    B = (p[0] + ux * e + nx, p[1] + uy * e + ny)
    C = (p[0] + ux * e - nx, p[1] + uy * e - ny)
    E = (p[0] + ux * s - nx, p[1] + uy * s - ny)
    quad(tris, A + (h,), B + (h,), C + (h,), E + (h,))
    quad(tris, E + (0,), C + (0,), B + (0,), A + (0,))
    for u, v in ((A, B), (B, C), (C, E), (E, A)):
        quad(tris, u + (0,), v + (0,), v + (h,), u + (h,))


def edges(pts):
    for thr in (41, 44, 48):
        es = [(i, j) for i in range(len(pts)) for j in range(i + 1, len(pts))
              if math.dist(pts[i], pts[j]) <= thr]
        seen, todo = {0}, [0]
        while todo:
            a = todo.pop()
            for i, j in es:
                for u, v in ((i, j), (j, i)):
                    if u == a and v not in seen:
                        seen.add(v)
                        todo.append(v)
        if len(seen) == len(pts):
            return es
    raise SystemExit("layout not connected")


def write_stl(path, tris):
    with open(path, "wb") as f:
        f.write(b"ratling pack mockup".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - a[i] for i in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            m = math.sqrt(sum(x * x for x in n)) or 1
            f.write(struct.pack("<12fH", *[x / m for x in n], *a, *b, *c, 0))


def main():
    out = os.path.join(REPO, "exports", "pack_layouts", "stl")
    os.makedirs(out, exist_ok=True)
    h = LAYERS * LAYER
    for key, name, n, pts, outline in LAYOUTS:
        x0, x1, y0, y1 = bbox(pts)
        w, hh = x1 - x0, y1 - y0
        if key == "i_square_5x5_round":
            continue
        if max(w, hh) > BED:
            print("%-20s %.0f x %.0f  does not fit the bed" % (key, w, hh))
            continue
        tris = []
        for x, y in pts:
            annulus(tris, x, y, h)
        for i, j in edges(pts):
            bridge(tris, pts[i], pts[j], h)
        write_stl(os.path.join(out, key + ".stl"), tris)
        print("%-20s %.0f x %.0f  %d discs, %.1f mm (%d layers)" % (key, w, hh, n, h, LAYERS))


main()
