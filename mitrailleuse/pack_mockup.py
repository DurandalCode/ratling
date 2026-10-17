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


def cylinder(tris, cx, cy, r, z0, z1):
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        quad(tris, p0 + (z0,), p1 + (z0,), p1 + (z1,), p0 + (z1,))
        tris.append(((cx, cy, z1), p0 + (z1,), p1 + (z1,)))
        tris.append(((cx, cy, z0), p1 + (z0,), p0 + (z0,)))


def box(tris, A, B, C, E, z0, z1):
    quad(tris, A + (z1,), B + (z1,), C + (z1,), E + (z1,))
    quad(tris, E + (z0,), C + (z0,), B + (z0,), A + (z0,))
    for u, v in ((A, B), (B, C), (C, E), (E, A)):
        quad(tris, u + (z0,), v + (z0,), v + (z1,), u + (z1,))


def sector(tris, cx, cy, r0, r1, a0, a1, h):
    n = 60
    for k in range(n):
        t0, t1 = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
        o0 = (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0))
        o1 = (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1))
        i0 = (cx + r0 * math.cos(t0), cy + r0 * math.sin(t0))
        i1 = (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1))
        quad(tris, o0 + (0,), o1 + (0,), o1 + (h,), o0 + (h,))
        quad(tris, i1 + (0,), i0 + (0,), i0 + (h,), i1 + (h,))
        quad(tris, o0 + (h,), o1 + (h,), i1 + (h,), i0 + (h,))
        quad(tris, o1 + (0,), o0 + (0,), i0 + (0,), i1 + (0,))
    for a, rr in ((a0, 1), (a1, -1)):
        ca, sa = math.cos(a), math.sin(a)
        A, B = (cx + r0 * ca, cy + r0 * sa), (cx + r1 * ca, cy + r1 * sa)
        if rr > 0:
            quad(tris, A + (0,), B + (0,), B + (h,), A + (h,))
        else:
            quad(tris, B + (0,), A + (0,), A + (h,), B + (h,))


def sheet(pts, h):
    tris = []
    for x, y in pts:
        annulus(tris, x, y, h)
    for i, j in edges(pts):
        bridge(tris, pts[i], pts[j], h)
    return tris


def split_hex37(out, h):
    """Zigzag cut down the middle (no disc cut) + three splints with pegs."""
    pts = _ns["hexagon"](4)
    def left(x, y):
        if abs(x) > 1:
            return x < 0
        return y <= 1  # centre-column discs: rows r <= 0 left, r = +2 right
    L = [p for p in pts if left(*p)]
    R = [p for p in pts if not left(*p)]
    for nm, g in (("h_hex_37_left", L), ("h_hex_37_right", R)):
        write_stl(os.path.join(out, nm + ".stl"), sheet(g, h))
        x0, x1, y0, y1 = bbox(g)
        print("%-20s %.0f x %.0f  %d discs" % (nm, x1 - x0, y1 - y0, len(g)))
    seam = sorted([(a, b) for a in L for b in R if math.dist(a, b) <= 41], key=lambda t: t[0][1])
    pick = [seam[0], seam[len(seam) // 2], seam[-1]]
    tris, bar_t, peg_h, w = [], 1.0, h, 8.0
    for k, (a, b) in enumerate(pick):
        oy = k * 16.0
        d = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        # lay the splint along +X at y = oy, a at x = 0
        A, B = (0.0, oy - w / 2), (d, oy - w / 2)
        C, E = (d, oy + w / 2), (0.0, oy + w / 2)
        box(tris, A, B, C, E, 0, bar_t)
        for cx in (0.0, d):
            cylinder(tris, cx, oy, w / 2, 0, bar_t)
            cylinder(tris, cx, oy, HOLE_R - 0.15, bar_t, bar_t + peg_h)
    write_stl(os.path.join(out, "h_hex_37_splints.stl"), tris)
    print("h_hex_37_splints     3 pieces, bar %.1f mm + pegs %.1f mm (print pegs up)" % (bar_t, peg_h))


def ring_arcs(out, h):
    """Round shroud Ø264 does not fit the bed: three 120 deg arcs, 4 mm wide."""
    tris, R = [], 132.0
    for k in range(3):
        sector(tris, 0.0, k * 80.0, R - 4, R, math.radians(30), math.radians(150), h)
    write_stl(os.path.join(out, "i_shroud_ring_3arcs.stl"), tris)
    print("i_shroud_ring_3arcs  3 arcs 120 deg, 229 x 66 each (O264 shroud)")


def main():
    out = os.path.join(REPO, "exports", "pack_layouts", "stl")
    os.makedirs(out, exist_ok=True)
    h = LAYERS * LAYER
    ring_arcs(out, h)
    for key, name, n, pts, outline in LAYOUTS:
        x0, x1, y0, y1 = bbox(pts)
        w, hh = x1 - x0, y1 - y0
        if key == "i_square_5x5_round":
            continue
        if key == "h_hex_37":
            split_hex37(out, h)
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
