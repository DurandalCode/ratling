# -*- coding: utf-8 -*-
"""
Barrel pack layouts at 1:1 (mm) for paper mock-ups: pitch 40, module/tube Ø38.
Writes exports/pack_layouts/*.svg (one per layout, real size), index.html
(one A3 page per layout, print at 100 %) and overview.svg (common scale).
Circle-packing coordinates come from pack_opt.py (mitrailleuse/circle_opt.json, in pitches).
Run: python3 mitrailleuse/pack_layouts.py
"""
import json
import math
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "exports", "pack_layouts")
P = 40.0
D = 38.0
S3 = math.sqrt(3) / 2


def square(c, r):
    return [((i - (c - 1) / 2) * P, (j - (r - 1) / 2) * P) for i in range(c) for j in range(r)]


def offset_rows(counts):
    """Rows with the given counts, hex-packed, each row centred."""
    pts = []
    for j, c in enumerate(counts):
        y = (j - (len(counts) - 1) / 2) * P * S3
        shift = P / 4 if j % 2 else -P / 4
        for i in range(c):
            pts.append(((i - (c - 1) / 2) * P + shift, y))
    return pts


def offset_cols(counts):
    return [(y, x) for x, y in offset_rows(counts)]


def hexagon(side):
    n = side - 1
    return [(P * (q + r / 2), P * S3 * r) for q in range(-n, n + 1) for r in range(-n, n + 1)
            if abs(q) <= n and abs(r) <= n and abs(q + r) <= n]


def rings(*specs):
    """Concentric rings, each (count, radius, phase in degrees)."""
    return [(r * math.cos(math.radians(ph) + 2 * math.pi * i / n), r * math.sin(math.radians(ph) + 2 * math.pi * i / n))
            for n, r, ph in specs for i in range(n)]


def circle_opt(n):
    data = json.load(open(os.path.join(REPO, "mitrailleuse", "circle_opt.json")))
    return [(x * P, y * P) for x, y in data[str(n)][1]]


def ring_r(n):
    """Smallest radius of a ring of n at pitch P."""
    return P / 2 / math.sin(math.pi / n)


def outer_r(r1, n, dphi):
    """Outer ring of n turned dphi degrees off the inner ring at r1: pitch P inside it and to the inner ring."""
    c = math.cos(math.radians(dphi))
    return max(ring_r(n), r1 * c + math.sqrt(P * P - (r1 * math.sin(math.radians(dphi))) ** 2))


R4, R5, R12 = ring_r(4), ring_r(5), ring_r(12)
R10 = outer_r(R5, 10, 18)

LAYOUTS = [
    ("a_square_5x5", "A. Квадрат 5x5, 25", 25, square(5, 5), None),
    ("b_rows_5x5", "B. 5x5 вразбежку, 25", 25, offset_rows([5] * 5), None),
    ("c_circle_25", "C. 25 в круг", 25, circle_opt(25), "circle"),
    ("d_circle_24", "D. 24 в круг", 24, circle_opt(24), "circle"),
    ("e_rows_6x4_tall", "E. 6x4 вразбежку, 24", 24, offset_rows([4] * 6), None),
    ("f_rows_4x6_wide", "F. 4x6 вразбежку, 24", 24, offset_rows([6] * 4), None),
    ("g_hex_19", "G. Соты 19", 19, hexagon(3), "circle"),
    ("h_hex_37", "H. Соты 37 (Монтиньи)", 37, hexagon(4), "circle"),
    ("i_square_5x5_round", "I. Квадрат 5x5, 25, кожух", 25, square(5, 5), "circle"),
    # symmetric rings at pitch P, see docs/pack.md (ring radii, tie-rod turns)
    ("j_rings_4_12", "J. Кольца 4+12, 16", 16, rings((4, R4, 45), (12, R12, 0)), "circle"),
    ("k_rings_5_10", "K. Кольца 5+10, 15", 15, rings((5, R5, 0), (10, R10, 18)), "circle"),
    ("l_rings_1_4_12", "L. Кольца 1+4+12, 17", 17, rings((1, 0, 0), (4, P, 0), (12, R12, 15)), "circle"),
    ("m_rings_6_12", "M. Кольца 6+12, 18", 18, rings((6, P, 0), (12, R12, 15)), "circle"),
    ("n_rings_1_6_12", "N. Кольца 1+6+12, 19", 19, rings((1, 0, 0), (6, P, 0), (12, R12, 15)), "circle"),
]


def bbox(pts):
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    return min(xs) - D / 2, max(xs) + D / 2, min(ys) - D / 2, max(ys) + D / 2


def shroud_r(pts):
    return max(math.hypot(x, y) for x, y in pts) + D / 2


def shapes(pts, outline):
    """SVG body centred on (0, 0), y down; mm units."""
    out = []
    x0, x1, y0, y1 = bbox(pts)
    if outline == "circle":
        # centre the enclosing circle (optimal packings are already centred)
        out.append('<circle r="%.1f" fill="none" stroke="#c00" stroke-dasharray="4 3"/>' % shroud_r(pts))
    else:
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#c00" stroke-dasharray="4 3"/>'
                   % (x0, -y1, x1 - x0, y1 - y0))
    for x, y in pts:
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#cfe6ff" fill-opacity=".5" stroke="#000" stroke-width=".4"/>' % (x, -y, D / 2))
        out.append('<path d="M%.1f %.1fh6M%.1f %.1fv6M%.1f %.1fh-6M%.1f %.1fv-6" stroke="#000" stroke-width=".3"/>'
                   % (x - 3, -y, x, -y - 3, x + 3, -y, x, -y + 3))
    return "".join(out)


def label(name, n, pts, outline):
    x0, x1, y0, y1 = bbox(pts)
    t = "%s: %.0f x %.0f" % (name, x1 - x0, y1 - y0)
    if outline == "circle":
        t = "%s: круг O%.0f" % (name, 2 * shroud_r(pts))
    return t


def main():
    os.makedirs(OUT, exist_ok=True)
    cells, pages = [], []
    for key, name, n, pts, outline in LAYOUTS:
        if key == "i_square_5x5_round":
            pass
        lab = label(name, n, pts, outline)
        w, h = 297.0, 420.0  # A3 portrait, 1:1
        ruler = '<path d="M-148.5 190h100M-148.5 185v10M-48.5 185v10" stroke="#000"/><text x="-148" y="182" font-size="6">линейка 100 мм (проверьте печать)</text>'
        body = shapes(pts, outline)
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%dmm" height="%dmm" viewBox="%g %g %g %g" font-family="Helvetica">'
               '<text x="%g" y="%g" font-size="7">%s</text>%s%s</svg>'
               % (w, h, -w / 2, -h / 2, w, h, -w / 2 + 6, -h / 2 + 14, lab, body, ruler))
        open(os.path.join(OUT, key + ".svg"), "w").write(svg)
        pages.append('<section>%s</section>' % svg)
        cells.append((lab, pts, outline))
    open(os.path.join(OUT, "index.html"), "w").write(
        '<!doctype html><meta charset="utf-8"><style>@page{size:297mm 420mm;margin:0}body{margin:0}'
        'section{width:297mm;height:420mm;page-break-after:always;overflow:hidden}svg{display:block}</style>'
        + "".join(pages))
    # overview, common scale: 3 columns
    ch = 330.0
    cw = (3 * (ch + 30) + 20) / 3
    svg = []
    for i, (lab, pts, outline) in enumerate(cells):
        ox, oy = (i % 3) * cw + cw / 2, (i // 3) * (ch + 30) + ch / 2 + 30
        svg.append('<g transform="translate(%g %g)">%s</g>' % (ox, oy, shapes(pts, outline)))
        svg.append('<text x="%g" y="%g" font-size="8.5">%s</text>' % (ox - cw / 2 + 4, oy - ch / 2 - 4, lab))
    rows = (len(cells) + 2) // 3
    open(os.path.join(OUT, "overview.svg"), "w").write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" font-family="Helvetica"><rect width="100%%" height="100%%" fill="#fff"/>%s</svg>'
        % (3 * cw, rows * (ch + 30) + 20, "".join(svg)))


main()
