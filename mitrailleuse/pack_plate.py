# -*- coding: utf-8 -*-
"""
Negative of the pack layouts: a flat plate (outline = the layout's red contour
+ WALL) with a Ø25.4 hole per barrel (barrel Ø25 coaxial with the Ø38 tube), for 256 x 256 beds. A plate wider than the
bed is cut at x = 0 into two halves, joined by straps: a bar with two Ø3.8 pegs
that go into Ø4 holes drilled in the web between barrel holes on either side.
For the v4.3 module (module/stage3v4_coaxial_chamber.py) each barrel also gets its two M3 tie-rod
holes (R21.5 at 30 / 210 deg, all modules turned the same way); the outline grows to take them.
Run inside FreeCAD (the layouts come from pack_layouts.py; LAYERS = 0.2 mm layers, default 8):
    REPO = '/Users/<you>/ratling'
    LAYERS = 5
    exec(open(REPO + '/mitrailleuse/pack_plate.py').read())
Writes exports/pack_layouts/stl/plate_*.stl.
"""
import math
import os

import FreeCAD as App
import Mesh
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
_ns = {"__file__": os.path.join(REPO, "mitrailleuse", "pack_layouts.py")}
exec(open(_ns["__file__"]).read().rsplit("\nmain()", 1)[0], _ns)
D, LAYOUTS, shroud_r, bbox = _ns["D"], _ns["LAYOUTS"], _ns["shroud_r"], _ns["bbox"]

V = App.Vector
try:
    LAYERS
except NameError:
    LAYERS = 8
H = LAYERS * 0.2
BED = 256.0
WALL = 4.0
HOLE_R = 12.7        # barrel Ø25 + 0.4, coaxial with the Ø38 module
PEG_HOLE_R = 2.0
TIE_R, TIE_ANGLES, TIE_HOLE_R = 21.5, (30.0, 210.0), 1.7   # v4.3: M3 rods, hole Ø3.4
TARGETS = ("g_hex_19", "h_hex_37", "i_square_5x5_round")
PEG_R = 1.85
STRAP_W = 8.0
STRAP_T = 1.0
OUT = os.path.join(REPO, "exports", "pack_layouts", "stl")


def cyl(x, y, r, h, z=0.0):
    return Part.makeCylinder(r, h, V(x, y, z))


def box(x0, y0, x1, y1, h):
    return Part.makeBox(x1 - x0, y1 - y0, h, V(x0, y0, 0))


def rods(pts):
    return [(x + TIE_R * math.cos(math.radians(a)), y + TIE_R * math.sin(math.radians(a)))
            for x, y in pts for a in TIE_ANGLES]


def outline_solid(pts, kind):
    x0, x1, y0, y1 = bbox(pts)
    if kind == "circle":
        R = max(shroud_r(pts) + WALL, max(math.hypot(x, y) for x, y in rods(pts)) + TIE_HOLE_R + 3.0)
        s = cyl(0, 0, R, H)
        if 2 * R <= BED:                     # a full circle when it fits the bed
            return s
        top = y1 + WALL                      # flats so the plate fits the bed in y
        if 2 * top > BED:
            top = BED / 2 - 1
        if top < R:
            s = s.common(box(-R, -top, R, top, H))
        return s
    return box(x0 - WALL, y0 - WALL, x1 + WALL, y1 + WALL, H)


def free_pairs(pts, plate_solid, a_min=12, a_max=40):
    """Mirror pairs of peg-hole sites (-a, y), (a, y) in the web away from every hole."""
    rd = rods(pts)

    def inside(x, y):
        return all(plate_solid.isInside(V(x + dx, y + dy, H / 2), 0.01, True)
                   for dx, dy in ((0, 0), (5, 0), (-5, 0), (0, 5), (0, -5)))
    def ok(x, y):
        return (all(math.hypot(x - px, y - py) >= HOLE_R + PEG_HOLE_R + 1.5 for px, py in pts)
                and all(math.hypot(x - rx, y - ry) >= TIE_HOLE_R + PEG_HOLE_R + 1.5 for rx, ry in rd)
                and inside(x, y))
    found = []
    for y in range(-130, 131):
        for a in range(a_min, a_max):
            if ok(-a, y) and ok(a, y):
                found.append((a, y))
                break
    return found


def strap(a, oy):
    g = box(-a - STRAP_W / 2, oy - STRAP_W / 2, a + STRAP_W / 2, oy + STRAP_W / 2, STRAP_T)
    for sx in (-a, a):
        g = g.fuse(cyl(sx, oy, STRAP_W / 2, STRAP_T))
        g = g.fuse(cyl(sx, oy, PEG_R, H, STRAP_T))
    return g


def export(shape, name):
    shape = shape.removeSplitter()
    mesh = Mesh.Mesh(shape.tessellate(0.05))
    mesh.write(os.path.join(OUT, name + ".stl"))


def plate(key, pts, kind):
    s = outline_solid(pts, kind)
    for x, y in pts:
        s = s.cut(cyl(x, y, HOLE_R, H))
    for x, y in rods(pts):
        s = s.cut(cyl(x, y, TIE_HOLE_R, H))
    x0, x1, y0, y1 = s.BoundBox.XMin, s.BoundBox.XMax, s.BoundBox.YMin, s.BoundBox.YMax
    if x1 - x0 <= BED:
        export(s, "plate_" + key)
        return "%s  %.0f x %.0f  one piece" % (key, x1 - x0, y1 - y0)
    pairs = free_pairs(pts, s)
    picks = [pairs[0], pairs[len(pairs) // 2], pairs[-1]]
    for a, y in picks:
        for sx in (-a, a):
            s = s.cut(cyl(sx, y, PEG_HOLE_R, H))
    R = x1 + 1
    export(s.common(box(-R, -R, 0, R, H)), "plate_%s_left" % key)
    export(s.common(box(0, -R, R, R, H)), "plate_%s_right" % key)
    st = None
    for k, (a, y) in enumerate(picks):
        g = strap(a, 0)
        g.translate(V(0, k * (STRAP_W + 6), 0))
        st = g if st is None else st.fuse(g)
    export(st, "plate_%s_straps" % key)
    return "%s  %.0f x %.0f  two halves, straps a=%s" % (key, x1 - x0, y1 - y0, [p[0] for p in picks])


os.makedirs(OUT, exist_ok=True)
for key, name, n, pts, outline in LAYOUTS:
    if key in TARGETS:
        print(plate(key, pts, outline))
