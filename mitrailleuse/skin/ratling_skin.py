# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse skin: a skaven "ratling gun" look over concept A. A skin, not parts (docs/skin.md).

Builds mitrailleuse_concepts.py as it is (its geometry untouched), recolours the chosen variant as forged
iron, brass and copper, and adds decor round it as masses: nothing here is a part yet, and nothing moves or
cuts a part of the concept. Choose before exec (or as environment variables of the same names):

    BARRELS = 16 | 19                                       pack: A16 (rings 4 + 12) or A19 (hex)
    TOP     = "concept" | "post" | "arch" | "triangle" | "tiller"   the carry handle over the CoG
    GRIP    = "concept" | "butt" | "spades" | "down" | "side"       the control grip with the trigger
    DEPTH   = 70.0                                          mm the drum is drawn deeper than the concept's casing
    SHEETS  = False                                         also render every TOP and every GRIP side by side

Always there (the skin itself):
- copper bands on every muzzle sleeve (Ø36 x 10 at z 335 and 415) and a crown at its tip (Ø36, the last
  14 mm, a Ø37 lip): sleeves are on a 40 mm pitch, so 4 / 3 mm between neighbours (checked);
- riveted brass hoops round the rails at the front plate and the rear plate (Ø222 / Ø238), and rivets on
  the sling-eye band;
- the rear casing as a riveted iron drum, DEPTH deeper (to z -300 at 70) under a riveted cap with the
  flexible shaft's input brought out through it; copper straps, a seam of rivets on top, a crest of spikes
  on its rear rim (the rear block is not final: this sets the look only);
- a raised brass triangle with three claw slots on the drum's upper left, a green "warp" lens on a brass
  gauge ahead of the supply hose, a green glass vial in two brass clamps along the top;
- a forged spike under the muzzles, on a lug from the sleeve band, 40 mm past the tips;
- brass ribs on the supply hose, as a corrugated hose.

TOP (handles()): post, an upright grip with a knob; arch, a riveted strap from hoop to hoop with the grip
over the CoG; triangle, an inverted spiked triangle whose top bar is the grip; tiller, a bar off the drum's
left side with an upright grip, the concept's top handle kept. Grips Ø32 x 115, 30 mm or more clear (checked).

GRIP (rear_grips()): butt, a flintlock pistol's butt out of the cap's lower half, lofted through oval
sections along a curve from 12 to 62 deg down, swelling from a 34 x 28 wrist into a brass-capped pommel,
the trigger in a brass bow under its root; spades, two upright grips behind the cap with a butterfly
trigger (Maxim); down, a straight grip under the drum in a riveted D-bow, on the concept's grip axis from
where it leaves the drum (the concept's trigger sits under the drum); side, a grip along the drum's upper
left flank with a thumb lever. Each with 20 mm or more for the fingers, outside the drum (checked).

Prints [OK ] / [FAIL]. Writes exports/ratling_skin/A<n>_<top>_<grip>/<view>.jpg, and with SHEETS
exports/ratling_skin/sheets/A<n>_tops.jpg, A<n>_grips.jpg and each variant's views.

Run inside FreeCAD (GUI):
    REPO = '/Users/<you>/ratling'
    BARRELS, TOP, GRIP = 16, "arch", "butt"
    exec(open(REPO + '/mitrailleuse/skin/ratling_skin.py').read())
On a VM: mitrailleuse/skin/run_skin.py (docs/skin.md).
"""

import math
import os

import FreeCAD as App
import Part
from PIL import Image, ImageChops, ImageDraw

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")


def _param(name, default, kind=str):
    v = globals().get(name)
    if v is None:
        v = os.environ.get(name)
    return default if v is None else kind(v)


BARRELS = _param("BARRELS", 16, int)
TOP = _param("TOP", "arch")
GRIP_KIND = _param("GRIP", "butt")
DEPTH = _param("DEPTH", 70.0, float)
SHEETS = _param("SHEETS", False, lambda v: str(v).lower() in ("1", "true", "yes"))
TOPS = ("concept", "post", "arch", "triangle", "tiller")
GRIP_KINDS = ("concept", "butt", "spades", "down", "side")
assert BARRELS in (16, 19), "BARRELS: 16 or 19"
assert TOP in TOPS, "TOP: one of %s" % (TOPS,)
assert GRIP_KIND in GRIP_KINDS, "GRIP: one of %s" % (GRIP_KINDS,)

exec(open(os.path.join(REPO, "mitrailleuse", "mitrailleuse_concepts.py"), encoding="utf-8").read())

SKIN = "ratling_skin"
TAG = "A%d" % BARRELS
VI = [t for t, _, _, _ in VARIANTS].index(TAG)
_, GROUP, _, KEY = VARIANTS[VI]
OFF = V(0, -X_OFF * VI, 0)
OUT = os.path.join(REPO, "exports", SKIN, "%s_%s_%s" % (TAG, TOP, GRIP_KIND))
OUT_SHEETS = os.path.join(REPO, "exports", SKIN, "sheets")
os.makedirs(OUT, exist_ok=True)

# forged look: (colour, transparency)
FV.STYLES.update({
    "iron": ((0.20, 0.19, 0.18), 0), "iron_dark": ((0.13, 0.12, 0.12), 0), "rust": ((0.38, 0.23, 0.14), 0),
    "brass": ((0.78, 0.60, 0.28), 0), "copper": ((0.74, 0.38, 0.19), 0), "bronze": ((0.52, 0.37, 0.20), 0),
    "warp": ((0.35, 0.95, 0.25), 20), "leather": ((0.33, 0.20, 0.11), 0), "wood": ((0.40, 0.24, 0.12), 0),
    "rubber": ((0.16, 0.15, 0.13), 0),
})
RESTYLE = {"Modules_barrel": "iron", "Modules_chamber": "brass", "Modules_printed": "bronze",
           "Modules_steel": "iron", "Front_plate": "rust", "Rear_plate": "rust", "Rails": "iron",
           "Rear_casing": "iron", "Muzzle_sleeves": "iron_dark", "Sleeve_band": "copper", "Carry_handle": "leather",
           "Carry_posts": "iron", "Eye_band": "brass", "Sling_eyes": "iron", "Tripod_pad": "iron",
           "Rear_grip": "wood", "Crank_knob": "wood", "Crank_arm": "iron", "Crank_shaft": "iron",
           "Supply_hose": "rubber", "Flex_shaft_input": "brass", "Bevel_box": "iron", "Rear_frame": "iron"}

Z_TIP = 310.7 + SLEEVE[2]
CASE = (A_RAIL_R + 10.0, -230.0, -45.0)         # the rear casing's outer radius and ends, as drawn in concept_a
BACK = CASE[1] - DEPTH
BAND = (36.0, 10.0, (335.0, 415.0))             # sleeve bands: OD, length, z
CROWN = (36.0, 14.0)
HOOP = (222.0, 238.0, 18.0)                     # ID, OD, width
RIVET = 5.0
GRIP = (32.0, 115.0)                            # straight grips: Ø, length (a gloved hand: 30-34 x 110+)


def compound(shapes):
    return Part.makeCompound(list(shapes))


def clear(a, b):
    return a.distToShape(b)[0]


def rivets_round(r, z, step, skip=()):
    out = []
    for i in range(int(round(360 / step))):
        a = i * step
        if any(abs((a - s + 180) % 360 - 180) < step * 0.6 for s in skip):
            continue
        out.append(Part.makeSphere(RIVET / 2, V(*polar(r, a), z)))
    return compound(out)


def radial(d, r0, r1, a, z):
    """A cylinder along the radius at angle a (deg), from r0 to r1, at z."""
    return rod(d, polar(r0, a) + (z,), polar(r1, a) + (z,))


def cone_from(p, q, d0):
    p, q = V(*p), V(*q)
    return Part.makeCone(d0 / 2, 0.0, (q - p).Length, p, q - p)


def chain(dia, *pts):
    """Rods through the points, with a ball at each bend."""
    return G.fuse_all([rod(dia, a, b) for a, b in zip(pts, pts[1:])] +
                      [Part.makeSphere(dia / 2, V(*q)) for q in pts[1:-1]])


def bent_wire(dia, pts, n=24):
    """A round bar swept along a smooth curve through pts (a B-spline); short rods and balls if the sweep fails."""
    c = Part.BSplineCurve()
    c.interpolate([V(*q) for q in pts])
    try:
        p0, t0 = c.value(c.FirstParameter), c.tangent(c.FirstParameter)[0]
        prof = Part.Wire(Part.makeCircle(dia / 2, p0, t0))
        bar = Part.Wire(c.toShape()).makePipeShell([prof], True, True)
        if bar.isValid() and bar.Volume > 0:
            return bar
    except Exception:
        pass
    samples = [c.value(c.FirstParameter + (c.LastParameter - c.FirstParameter) * i / n) for i in range(n + 1)]
    return chain(dia, *[(q.x, q.y, q.z) for q in samples])


def leather_grip(p, q):
    g = rod(GRIP[0], p, q)
    d = V(*q) - V(*p)
    rings = compound([Part.makeTorus(GRIP[0] / 2, 1.6, V(*p) + d * t, d) for t in (0.04, 0.96)])
    return g, rings


def claw_triangle(r_case, z_mid, a, side=110.0):
    """A raised triangle on the casing at angle a, point forward, with three claw slots, hugging the drum."""
    h = side * math.sqrt(3) / 2
    tri = [(z_mid + h * 2 / 3, 0.0), (z_mid - h / 3, side / 2), (z_mid - h / 3, -side / 2)]
    f = Part.Face(Part.makePolygon([V(0, w, u) for u, w in tri] + [V(0, tri[0][1], tri[0][0])]))
    plate = f.extrude(V(r_case + 4, 0, 0))
    plate = plate.common(cyl(2 * (r_case + 4), z_mid - side, z_mid + side)).cut(cyl(2 * r_case - 2, z_mid - side,
                                                                                     z_mid + side))
    for k in (-1, 0, 1):                         # three slanted slots, as a rat's claw marks
        slot = Part.makeBox(46, 5, 30, V(r_case - 10, -2.5, -23))
        slot.rotate(V(0, 0, 0), V(1, 0, 0), 25)
        slot.translate(V(0, 16 * k, z_mid - 6))
        plate = plate.cut(slot)
    plate.rotate(V(0, 0, 0), Z, a)
    return plate


# ---------------------------------------------------------------- the skin
def skin(key, p):
    pts = LAYOUT[key]
    s = {}
    bands = []
    for x, y in pts:
        for z in BAND[2]:
            bands.append(tube(BAND[0], (BAND[0] - SLEEVE[0]) / 2, z, z + BAND[1], x, y))
        bands.append(tube(CROWN[0], (CROWN[0] - SLEEVE[0]) / 2, Z_TIP - CROWN[1], Z_TIP, x, y))
        bands.append(tube(CROWN[0] + 1, 3.0, Z_TIP - 4, Z_TIP, x, y))
    s["Sleeve_bands"] = (compound(bands), "copper")
    hoops, rv = [], []
    for z0 in (A_PLATES[1][0] - 4, A_PLATES[0][0] - 10):
        hoops.append(tube(HOOP[1], (HOOP[1] - HOOP[0]) / 2, z0, z0 + HOOP[2]))
        rv.append(rivets_round(HOOP[1] / 2, z0 + HOOP[2] / 2, 15.0))
    zc = p["Eye_band"][0].BoundBox.Center.z
    rv.append(rivets_round(A_RAIL_R + 6, zc, 15.0, skip=(0, 90, 180) + tuple(range(225, 316, 15))))
    s["Hoops"] = (compound(hoops), "brass")
    s["Rivets"] = (compound(rv), "brass")
    # the drum: DEPTH deeper, capped; straps at its ends and on the joint, a seam on top, spikes on the rear rim
    s["Casing_extension"] = (tube(2 * CASE[0], 2.0, BACK, CASE[1] + 1), "iron")
    cap = cyl(2 * CASE[0] + 8, BACK - 5, BACK).fuse(cyl(70, BACK - 12, BACK - 5)).cut(cyl(24, BACK - 13, BACK + 1,
                                                                                           0, GEAR_C))
    s["End_cap"] = (cap, "iron")
    s["Flex_collar"] = (tube(32, 5, BACK - 16, BACK - 5, 0, GEAR_C), "brass")
    s["Flex_extension"] = (cyl(12, BACK - 16, -260, 0, GEAR_C), "iron")       # the input brought out through the cap
    rv = [compound([Part.makeSphere(RIVET / 2, V(*polar(CASE[0] - 2, 15 * i), BACK - 5)) for i in range(24)])]
    straps = [tube(2 * CASE[0] + 8, 4, z, z + 12) for z in (BACK + 2, CASE[1] - 6, CASE[2] - 14)]
    for z in (BACK + 8, CASE[1], CASE[2] - 8):
        rv.append(rivets_round(CASE[0] + 4, z, 12.0))
    for i in range(int((CASE[2] - BACK - 40) / 11.5) + 1):
        z = BACK + 20 + i * 11.5
        rv.append(compound([Part.makeSphere(RIVET / 2, V(*polar(CASE[0], a), z)) for a in (78, 102)]))
    s["Casing_straps"] = (compound(straps), "copper")
    s["Drum_rivets"] = (compound(rv), "brass")
    spikes = []
    for a in (55, 75, 90, 105, 125):
        x, y = polar(CASE[0] + 2, a)
        tx, ty = polar(CASE[0] + 30, a)
        spikes.append(cone_from((x, y, BACK + 6), (tx, ty, BACK - 34), 16))
    s["Spikes"] = (compound(spikes), "iron_dark")
    y_s = -(_ns["shroud_r"](LAYOUT[key]) + 2.0 + 9.0)
    s["Muzzle_spike"] = (cone_from((0, y_s + 3, Z_TIP - 40), (0, y_s + 3, Z_TIP + 40), 18), "iron_dark")
    s["Spike_lug"] = (box(-7, 7, y_s, y_s + 12, Z_TIP - 34, Z_TIP - 22), "iron")
    s["Claw_plate"] = (claw_triangle(CASE[0], -135.0, 40.0), "brass")
    zg, ag = -80.0, 0.0
    s["Warp_gauge"] = (radial(40, CASE[0] - 2, CASE[0] + 10, ag, zg), "brass")
    s["Warp_lens"] = (radial(30, CASE[0] + 10, CASE[0] + 13, ag, zg), "warp")
    yv = CASE[0] + 16
    s["Warp_vial"] = (cyl(22, -260, -80, 0, yv).fuse(Part.makeSphere(11, V(0, yv, -80)))
                      .fuse(Part.makeSphere(11, V(0, yv, -260))), "warp")
    clamps = [tube(30, 4, z, z + 10, 0, yv).fuse(box(-5, 5, CASE[0] - 2, yv - 12, z, z + 10)) for z in (-245, -105)]
    s["Vial_clamps"] = (compound(clamps), "brass")
    xv = HEAD[1] + 12                               # the supply hose, as concept_a draws it
    a, b = V(xv + 24, 0, -143.0 + 15), V(xv + 89, -60, -143.0 + 15 - 60)
    d = b - a
    s["Hose_ribs"] = (compound([Part.makeTorus(4.6, 1.3, a + d * (i * 7 / d.Length), d)
                                for i in range(1, int(d.Length / 7))]), "brass")
    return s


# ---------------------------------------------------------------- TOP: carry handles over the CoG
def handles(p):
    """post / arch / triangle / tiller (module docstring); the concept's handle is hidden for all but tiller."""
    zc = p["Eye_band"][0].BoundBox.Center.z
    yt = p["Carry_posts"][0].BoundBox.YMax
    h = {}
    g, rg = leather_grip((0, yt + 22, zc), (0, yt + 22 + GRIP[1], zc))
    h["post"] = {"Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                 "Saddle": (box(-10, 10, yt - 4, yt + 8, zc - 80, zc + 80), "iron"),
                 "Collar": (rod(44, (0, yt + 8, zc), (0, yt + 22, zc)), "brass"),
                 "Knob": (Part.makeSphere(23, V(0, yt + 22 + GRIP[1] + 14, zc)), "brass"),
                 "Knob_spike": (cone_from((0, yt + 22 + GRIP[1] + 30, zc), (0, yt + 22 + GRIP[1] + 62, zc), 14),
                                "iron_dark"),
                 "Rivets": (compound([Part.makeSphere(RIVET / 2, V(0, yt + 8, z)) for z in
                                      (zc - 70, zc - 50, zc + 50, zc + 70)]), "brass")}
    zf, zr = A_PLATES[1][0] - 4, A_PLATES[0][0] - 10           # the hoops' front faces, as in skin()
    y0, ys = HOOP[1] / 2 - 2, 172.0
    legs = [box(-14, 14, y0, ys, z, z + 14) for z in (zf + 2, zr + 2)]
    strap = box(-14, 14, ys - 9, ys, zr + 2, zf + 16)
    g, rg = leather_grip((0, ys - 4.5, zc - GRIP[1] / 2), (0, ys - 4.5, zc + GRIP[1] / 2))
    rvs = [Part.makeSphere(RIVET / 2, V(sx * 8, ys, z)) for sx in (-1, 1)
           for z in range(int(zr + 10), int(zf + 10), 20) if abs(z - zc) > GRIP[1] / 2 + 6]
    h["arch"] = {"Strap": (compound(legs + [strap]), "iron"), "Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                 "Rivets": (compound(rvs), "brass")}
    yb, ytop, half, t = A_RAIL_R + 6, 238.0, 92.0, 14.0
    outer = [V(0, yb, zc), V(0, ytop, zc - half), V(0, ytop, zc + half), V(0, yb, zc)]
    tri = Part.Face(Part.makePolygon(outer)).extrude(V(10, 0, 0))
    tri.translate(V(-5, 0, 0))
    k = 1 - t * 2.6 / (ytop - yb)                      # the opening, a smaller triangle round the same centroid
    cy, cz = (yb + 2 * ytop) / 3, zc
    inner = [V(0, cy + (y - cy) * k, cz + (z - cz) * k) for y, z in ((yb, zc), (ytop, zc - half), (ytop, zc + half))]
    hole = Part.Face(Part.makePolygon(inner + [inner[0]])).extrude(V(12, 0, 0))
    hole.translate(V(-6, 0, 0))
    frame = tri.cut(hole).fuse(box(-12, 12, yb - 2, yb + 10, zc - 22, zc + 22))
    yg = ytop - GRIP[0] / 2 + 2
    g, rg = leather_grip((0, yg, zc - GRIP[1] / 2), (0, yg, zc + GRIP[1] / 2))
    corner = [cone_from((0, ytop - 6, zc + sz * (half - 8)), (0, ytop + 22, zc + sz * (half + 26)), 16) for sz in (-1, 1)]
    rvt = [Part.makeSphere(RIVET / 2, V(5, cy + (y - cy) * (1 + k) / 2, cz + (z - cz) * (1 + k) / 2))
           for y, z in ((yb, zc), (ytop, zc - half), (ytop, zc + half))]
    h["triangle"] = {"Frame": (frame, "iron"), "Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                     "Spikes": (compound(corner), "iron_dark"), "Rivets": (compound(rvt), "brass")}
    xt, zb, zt = CASE[0] + 40, -270.0, BACK - 60
    arm = rod(22, (CASE[0] - 4, 20, zb), (xt, 20, zb)).fuse(rod(22, (xt, 20, zb), (xt, 20, zt)))
    g, rg = leather_grip((xt, 20 - 12, zt), (xt, 20 - 12 - GRIP[1], zt))
    h["tiller"] = {"Arm": (arm, "iron"), "Foot": (box(CASE[0] - 6, CASE[0] + 6, 0, 40, zb - 20, zb + 20), "brass"),
                   "Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                   "Knob": (Part.makeSphere(19, V(xt, 20 - 12 - GRIP[1] - 10, zt)), "brass"),
                   "Trigger_lever": (box(xt - 4, xt + 4, -20, -2, zt + 14, zt + 30), "brass")}
    return h


# ---------------------------------------------------------------- GRIP: the control grip with the trigger
BUTT = {"root": (0.0, -55.0), "turn": (12.0, 62.0), "length": 150.0,
        # (s along the curve, half-height in the side view, half-width): wrist 34 x 28, swelling to the pommel
        "sections": ((0, 23, 17), (16, 19, 15), (38, 17, 14), (62, 18, 14.5), (88, 21, 16), (112, 25, 18),
                     (132, 29, 21), (150, 31, 22))}


def butt_frame(s):
    """Point, tangent and side-view normal of the butt's curve at s mm from its root on the cap."""
    L, (a0, a1) = BUTT["length"], BUTT["turn"]
    th = lambda u: math.radians(a0 + (a1 - a0) * (u / L) ** 1.3)
    y, z, u, du = BUTT["root"][1], BACK - 8, 0.0, 1.0
    while u < s - 1e-9:
        step = min(du, s - u)
        a = th(u + step / 2)
        y, z, u = y - step * math.sin(a), z - step * math.cos(a), u + step
    a = th(s)
    return V(0, y, z), V(0, -math.sin(a), -math.cos(a)), V(0, math.cos(a), -math.sin(a))


def ellipsoid(c, axes):
    """An ellipsoid at c with semi-axes given as vectors (each its direction times its length)."""
    e = Part.makeSphere(1.0)
    m = App.Matrix(axes[0].x, axes[1].x, axes[2].x, c.x, axes[0].y, axes[1].y, axes[2].y, c.y,
                   axes[0].z, axes[1].z, axes[2].z, c.z, 0, 0, 0, 1)
    return e.transformGeometry(m)


BUTT_BOW = []


def flintlock_butt():
    """The butt lofted through oval sections, its brass pommel cap and spur, the trigger and its bow."""
    X = V(1, 0, 0)
    wires = []
    for s, a, b in BUTT["sections"]:
        c, t, m = butt_frame(s)
        wires.append(Part.Wire(Part.Ellipse(c + m * a, c + X * b, c).toShape()))
    wood = Part.makeLoft(wires, True, False)
    c, t, m = butt_frame(BUTT["length"] - 6)
    cap = ellipsoid(c + t * 4, (t * 20, m * 33, X * 24))
    collar = Part.Wire(Part.Ellipse(c + m * 32, c + X * 23, c).toShape())
    ring = Part.Face(collar).extrude(t * 5).cut(Part.Face(Part.Wire(
        Part.Ellipse(c + m * 26, c + X * 18, c).toShape())).extrude(t * 6))
    spur = cone_from(tuple(c + t * 18 - m * 8), tuple(c + t * 44 - m * 22), 14)
    root = rod(52, (0, BUTT["root"][1], BACK - 1), (0, BUTT["root"][1], BACK - 16))
    # trigger just behind the cap, under the root; the bow from the cap round under it to the wrist's underside
    c55, _, m55 = butt_frame(55)
    under = c55 - m55 * 18
    trig = bent_wire(7, [(0, -70, BACK - 18), (0, -86, BACK - 26), (0, -100, BACK - 22)], 12)
    bow_pts = [(0, -76, BACK - 4), (0, -104, BACK - 8), (0, -122, BACK - 24), (0, -124, BACK - 44),
               (under.x, under.y - 2, under.z)]
    BUTT_BOW[:] = bow_pts
    bow = bent_wire(7, bow_pts)
    nails = compound([Part.makeSphere(2.2, butt_frame(s)[0] + X * (BUTT["sections"][i][2] - 0.5))
                      for i, s in ((2, 38), (5, 112))])
    return {"Grip": (wood, "wood"), "Pommel": (cap, "brass"), "Pommel_ring": (ring, "brass"),
            "Pommel_spike": (spur, "iron_dark"), "Flange": (root, "brass"), "Trigger": (trig, "brass"),
            "Guard": (bow, "brass"), "Nails": (nails, "brass")}


def rear_grips():
    """butt / spades / down / side (module docstring)."""
    d = V(0, -math.sin(math.radians(70)), -math.cos(math.radians(70)))
    n = V(0, -d.z, d.y) * -1                               # across the grip, forward
    t0 = (CASE[0] - A_RAIL_R * 0.72) / -d.y
    o = V(0, -A_RAIL_R * 0.72, -200) + d * t0               # where the concept's grip leaves the drum

    def P(t, u):
        q = o + d * t + n * u
        return (q.x, q.y, q.z)

    g = {"butt": flintlock_butt()}
    zb, yb, xs = BACK - 50, -60.0, 95.0
    arms = [rod(16, (sx * 60, yb, BACK - 5), (sx * 60, yb, zb)) for sx in (-1, 1)]
    grips, rings, knobs = [], [], []
    for sx in (-1, 1):
        gg, rr = leather_grip((sx * xs, yb + 58, zb), (sx * xs, yb + 58 - GRIP[1], zb))
        grips.append(gg)
        rings.append(rr)
        knobs += [Part.makeSphere(18, V(sx * xs, yb + 66, zb)), Part.makeSphere(18, V(sx * xs, yb + 50 - GRIP[1], zb))]
    g["spades"] = {"Arms": (compound(arms + [rod(20, (-xs, yb, zb), (xs, yb, zb))]), "iron"),
                   "Grip": (compound(grips), "wood"), "Grip_rings": (compound(rings), "copper"),
                   "Knobs": (compound(knobs), "brass"),
                   "Trigger": (box(-26, 26, yb + 8, yb + 40, zb + 6, zb + 12).fuse(rod(8, (0, yb + 8, zb + 9),
                                                                                     (0, yb, zb + 9))), "brass")}
    gr, rg = leather_grip(P(8, 0), P(8 + GRIP[1], 0))
    bow = chain(12, P(-26, 64), P(129, 64), P(129, 0)).fuse(rod(40, P(8 + GRIP[1], 0), P(8 + GRIP[1] + 12, 0)))
    g["down"] = {"Flange": (rod(46, P(-6, 0), P(8, 0)), "brass"), "Grip": (gr, "wood"), "Grip_rings": (rg, "copper"),
                 "Bow": (bow, "iron"), "Bow_spike": (cone_from(P(70, 68), P(70, 112), 16), "iron_dark"),
                 "Rivets": (compound([Part.makeSphere(RIVET / 2, V(*P(t, 70))) for t in (0, 40, 100)]), "brass"),
                 "Trigger": (chain(8, P(16, 18), P(30, 26), P(46, 24)), "brass")}
    xg, yg, zg0 = CASE[0] + 40, 40.0, -280.0               # upper left flank; brackets leave the drum below the claws
    zg1 = zg0 + GRIP[1]
    gr, rg = leather_grip((xg, yg, zg0), (xg, yg, zg1))
    g["side"] = {"Grip": (gr, "wood"), "Grip_rings": (rg, "copper"),
                 "Brackets": (compound([rod(14, polar(CASE[0] - 2, 5) + (z,), (xg, yg, z)) for z in (zg0 - 10, zg1 + 10)]),
                              "iron"),
                 "Knobs": (compound([Part.makeSphere(15, V(xg, yg, z)) for z in (zg0 - 18, zg1 + 18)]), "brass"),
                 "Trigger": (box(xg - 5, xg + 5, yg + 14, yg + 30, zg1 - 22, zg1 - 8)
                             .fuse(rod(6, (xg - 9, yg + 18, zg1 - 8), (xg + 9, yg + 18, zg1 - 8))), "brass")}
    return g, (o, d, n)


# ---------------------------------------------------------------- build and check
P_A = BUILT[TAG]
SK = skin(KEY, P_A)
SKIN_NAMES = set()


def add_all(group, prefix, parts):
    for n, (shape, style) in parts.items():
        nm = "%s_%s" % (prefix, n)
        SKIN_NAMES.add(nm)
        sc.add(group, nm, to_view(shape), style, offset=OFF)


add_all(TAG + "_skin", TAG, SK)
pts = LAYOUT[KEY]
gap = min(math.dist(u, w) for j, u in enumerate(pts) for w in pts[j + 1:]) - CROWN[0] - 1
check(gap >= 2.0, "%s: sleeve crowns Ø%.0f, %.1f mm between neighbours (bands Ø%.0f: %.1f)"
      % (TAG, CROWN[0] + 1, gap, BAND[0], gap + CROWN[0] + 1 - BAND[0]))
for dn, pn in (("Hoops", "Carry_posts"), ("Hoops", "Sling_eyes"), ("Spikes", "Flex_shaft_input"),
               ("Spikes", "Crank_knob"), ("Drum_rivets", "Crank_knob"), ("Claw_plate", "Supply_hose"),
               ("Warp_gauge", "Supply_hose"), ("Rivets", "Carry_posts"), ("Rivets", "Tripod_pad")):
    c = clear(SK[dn][0], P_A[pn][0])
    check(c >= 2.0, "%s: %s clear of %s by %.1f mm" % (TAG, dn.lower(), pn, c))
print("      %s: skin reaches z %.0f (sleeve tips %.0f), the drum to z %.0f; %.0f g if printed solid in PLA"
      % (TAG, max(s_[0].BoundBox.ZMax for s_ in SK.values()), Z_TIP, BACK - 5,
         sum(s_[0].Volume for s_ in SK.values()) / 1000 * 1.27))

HANDLES = handles(P_A)
others = compound([P_A[n][0] for n in ("Eye_band", "Rails", "Sling_eyes", "Rear_casing", "Supply_hose")] +
                  [SK[n][0] for n in ("Hoops", "Warp_vial", "Vial_clamps", "Casing_extension", "End_cap", "Spikes",
                                      "Claw_plate", "Warp_gauge", "Flex_collar")])
for hn, parts in HANDLES.items():
    if hn != TOP and not SHEETS:
        continue
    add_all("%s_h_%s" % (TAG, hn), "%s_h_%s" % (TAG, hn), parts)
    c = clear(parts["Grip"][0], others)
    check(c >= 30.0, "%s top %s: grip Ø%.0f x %.0f, %.0f mm from the nearest part for the fingers"
          % (TAG, hn, GRIP[0], GRIP[1], c))

GRIPS, (G_O, G_D, G_N) = rear_grips()
drum = cyl(2 * CASE[0], BACK, CASE[2])
for gn, parts in GRIPS.items():
    if gn != GRIP_KIND and not SHEETS:
        continue
    add_all("%s_g_%s" % (TAG, gn), "%s_g_%s" % (TAG, gn), parts)
    inside = parts["Grip"][0].common(drum).Volume + parts["Trigger"][0].common(drum).Volume
    if gn == "spades":                             # the fingers between the grips' axis and the cap
        room = min(clear(rod(1, (sx * 95, -20, BACK - 50), (sx * 95, -100, BACK - 50)), SK["End_cap"][0])
                   for sx in (-1, 1)) - GRIP[0] / 2
    elif gn == "butt":                             # the wrist's underside to the bow's bottom
        room = min(clear(parts["Grip"][0], Part.Vertex(V(*q))) for q in BUTT_BOW[2:4]) - 3.5
        print("      butt: %.0f mm long, wrist %.0f x %.0f, pommel %.0f x %.0f; pommel at y %.0f z %.0f"
              % (BUTT["length"], 2 * BUTT["sections"][2][1], 2 * BUTT["sections"][2][2], 66, 48,
                 butt_frame(BUTT["length"])[0].y, butt_frame(BUTT["length"])[0].z))
    elif gn == "down":                             # from the grip to the bow's bar along it, at mid-grip
        mid = G_O + G_D * 60
        room = clear(rod(1, tuple(mid), tuple(mid + G_N * 57)), parts["Bow"][0]) + 57 - GRIP[0] / 2
    else:                                          # under the grip: drum, claw plate, supply hose
        room = clear(parts["Grip"][0], compound([drum, SK["Claw_plate"][0], SK["Warp_gauge"][0],
                                                 P_A["Supply_hose"][0]]))
    check(inside < 1.0 and room >= 20.0, "%s grip %s: grip and trigger outside the drum (%.0f mm3 in), %.0f mm"
          " for the fingers" % (TAG, gn, inside, room))
print("      note: the concept's rear grip leaves the drum %.0f mm down its axis, and its trigger (y %.0f to %.0f) is"
      " under the drum (R %.0f)" % ((G_O - V(0, -A_RAIL_R * 0.72, -200)).Length, P_A["Trigger"][0].BoundBox.YMin,
                                    P_A["Trigger"][0].BoundBox.YMax, CASE[0]))
k = P_A["Crank_knob"][0].BoundBox
r_arm = max(math.hypot(v.X, v.Y) for v in P_A["Crank_arm"][0].Vertexes)
print("      note: the concept's crank arm reaches R %.0f inside the casing (R %.0f), its knob goes through the"
      " wall (x %.0f to %.0f): the casing needs a slot there, or the crank outside it" % (r_arm, CASE[0], k.XMax, k.XMin))

sc.finish()

# ---------------------------------------------------------------- pictures, as in concepts_renders.py
if App.GuiUp:
    import FreeCADGui as Gui
    for o in doc.Objects:
        if not o.Name.startswith(TAG + "_") or not hasattr(o.ViewObject, "ShapeColor") or o.Name in SKIN_NAMES:
            continue
        st = RESTYLE.get(o.Name[len(TAG) + 1:], "bronze")
        o.ViewObject.ShapeColor, o.ViewObject.Transparency = FV.STYLES[st]
    SHOT = App.Placement(App.Matrix(0, 0, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1))
    for o in doc.Objects:
        if o.Name in sc.src:
            sh = sc.src[o.Name].copy()
            sh.Placement = SHOT.multiply(sh.Placement)
            o.Shape = sh
    doc.recompute()
    VIEWS = {"front": (-0.62, -0.62, -0.42), "rear": (0.62, 0.62, -0.48), "side": (0.0, 1.0, 0.0),
             "left": (0.0, -1.0, 0.0), "low": (-0.55, 0.75, 0.30)}
    CLOSE = {"close": (0.50, 0.72, -0.10), "closeside": (0.0, 1.0, 0.0), "closeback": (0.85, -0.35, -0.2)}
    CONCEPT_TOP = [TAG + "_Carry_handle", TAG + "_Carry_posts"]
    CONCEPT_GRIP = [TAG + "_Rear_grip", TAG + "_Trigger", TAG + "_Trigger_rod"]
    FRONT = [TAG + "_" + n for n in ("Modules_barrel", "Modules_chamber", "Modules_printed", "Modules_steel",
                                     "Muzzle_sleeves", "Sleeve_band", "Front_plate", "Rails", "Eye_band", "Sling_eyes",
                                     "Tripod_pad", "Sleeve_bands", "Muzzle_spike", "Spike_lug", "Hoops", "Rivets")]

    def camera(direction):
        d = App.Vector(*direction).normalize()
        zc_ = d.negative()
        up = App.Vector(0, 0, 1)
        if abs(zc_.dot(up)) > 0.99:
            up = App.Vector(0, 1, 0)
        xc = up.cross(zc_).normalize()
        yc = zc_.cross(xc)
        return App.Rotation(App.Matrix(xc.x, yc.x, zc_.x, 0, xc.y, yc.y, zc_.y, 0, xc.z, yc.z, zc_.z, 0, 0, 0, 0, 1))

    def snap(path, view, width=1300):
        v = Gui.getDocument(doc.Name).activeView()
        v.setCameraType("Orthographic")
        v.setCameraOrientation(camera(view))
        Gui.updateGui()
        v.fitAll()
        Gui.updateGui()
        tmp = path + "_tmp.png"
        v.saveImage(tmp, 2000, 1500, "White")
        im = Image.open(tmp).convert("RGB")
        bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        bb = (max(bb[0] - 24, 0), max(bb[1] - 24, 0), min(bb[2] + 24, im.width), min(bb[3] + 24, im.height))
        c = im.crop(bb)
        if c.width > width:
            c = c.resize((width, int(c.height * width / c.width)), Image.LANCZOS)
        c.save(path + ".jpg", quality=88)
        os.remove(tmp)
        return path + ".jpg"

    def show(top, grip, close=False):
        groups = [GROUP, TAG + "_skin"] + (["%s_h_%s" % (TAG, top)] if top != "concept" and not close else []) + \
                 (["%s_g_%s" % (TAG, grip)] if grip != "concept" else [])
        hide = ([] if top in ("concept", "tiller") else CONCEPT_TOP) + ([] if grip == "concept" else CONCEPT_GRIP)
        sc.show_only(groups, hide=hide + (FRONT + CONCEPT_TOP if close else []))

    def sheet(files, path):
        ims = [Image.open(f) for f in files]
        w, hh = max(i.width for i in ims), max(i.height for i in ims)
        cols = 2
        out = Image.new("RGB", (cols * w, -(-len(ims) // cols) * hh), "white")
        for i, im in enumerate(ims):
            x, y = (i % cols) * w, (i // cols) * hh
            out.paste(im, (x, y))
            ImageDraw.Draw(out).text((x + 20, y + 14), "%d" % (i + 1), fill=(0, 0, 0))
        out.save(path, quality=88)

    show(TOP, GRIP_KIND)
    for vn, dv in VIEWS.items():
        snap(os.path.join(OUT, vn), dv)
    if GRIP_KIND != "concept":
        show(TOP, GRIP_KIND, close=True)
        for vn, dv in CLOSE.items():
            snap(os.path.join(OUT, "grip_" + vn), dv, 1000)
    if SHEETS:
        os.makedirs(OUT_SHEETS, exist_ok=True)
        files = []
        for i, hn in enumerate(HANDLES):
            show(hn, GRIP_KIND)
            for vn in ("front", "side"):
                f = snap(os.path.join(OUT_SHEETS, "%s_top%d_%s_%s" % (TAG, i + 1, hn, vn)), VIEWS[vn])
            files.append(f)
        sheet(files, os.path.join(OUT_SHEETS, "%s_tops.jpg" % TAG))
        files = []
        for i, gn in enumerate(GRIPS):
            show(TOP, gn, close=True)
            for vn, dv in CLOSE.items():
                f = snap(os.path.join(OUT_SHEETS, "%s_grip%d_%s_%s" % (TAG, i + 1, gn, vn)), dv, 1000)
                if vn == ("closeback" if gn == "side" else "close"):
                    files.append(f)
        sheet(files, os.path.join(OUT_SHEETS, "%s_grips.jpg" % TAG))
    print("renders written to", OUT)
