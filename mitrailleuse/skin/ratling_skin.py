# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse skin: a skaven "ratling gun" look over concept A. A skin, not parts (docs/skin.md).

Builds mitrailleuse_concepts.py as it is (its geometry untouched), recolours the chosen variant as forged
iron, brass and copper, and adds decor round it as masses: nothing here is a part yet, and nothing moves or
cuts a part of the concept. Choose before exec (or as environment variables of the same names):

    BARRELS = 16 | 19                                       pack: A16 (rings 4 + 12) or A19 (hex)
    TOP     = "concept" | "post" | "arch" | "triangle" | "tiller" | "loop" | "cross"   the carry handle over the CoG
    GRIP    = "concept" | "butt" | "spades" | "down" | "side"       the control grip with the trigger
    INLET   = "concept" | "back" | "left" | "right" | "bottom"  where the supply hose and flexible shaft come in
    DRIVE   = "flex" | "crank" | "both"                      the flexible shaft to the second crew member, or a crank
                                                            on the drum, or both
    SHIELD  = "none" | "round" | "gear" | "spiked" | "kite" | "triangle"   a shield between the drum and the pack
    DEPTH   = 70.0                                          mm the drum is drawn deeper than the concept's casing
    GRIP_ROLL = 0.0                                         deg the grip is turned round the gun's axis (+ towards the
                                                            gunner's left, - towards the right), e.g. for firing from the hip
    TOP_ROLL = 0.0                                          deg the carry handle is turned round the gun's axis (+ towards
                                                            the gunner's left), e.g. 90 to carry it on the hip
    SIGHT   = "none" | "iron" | "ring" | "warp" | "scope"   sights over the drum and the sleeve band
    SCALE   = True                                          a 0.5 l beer bottle and a 1 m ruler on the ground beside it
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
left side with an upright grip, the concept's top handle kept; loop, the big pointed-oval loop of the art
(Ratling_Guns), 210 x 140 mm, standing over the CoG, its top wrapped in leather as the grip; cross, the
concept's handle turned across the gun, a bar over the eye band on two posts standing on it. Grips Ø32 x 115, 30 mm or more clear (checked).

GRIP (rear_grips()): butt, a flintlock pistol's butt out of the cap's lower half, lofted through oval
sections along a curve from 12 to 62 deg down, swelling from a 34 x 28 wrist into a brass-capped pommel,
the trigger in a brass bow under its root; spades, two upright grips behind the cap with a butterfly
trigger (Maxim); down, a straight grip under the drum in a riveted D-bow, on the concept's grip axis from
where it leaves the drum (the concept's trigger sits under the drum); side, a grip along the drum's upper
left flank with a thumb lever. Each with 20 mm or more for the fingers, outside the drum (checked).

INLET (inlet()): a riveted brass boss on the drum with the hose's union and the shaft's collar side by side,
both lines leaving it down and back for 240 mm, the hose corrugated, the shaft in a ribbed sheath: on the
cap (back), low on either flank (left, clear of the claws; right, ahead of the crank's sweep) or under the
drum (bottom); concept keeps the concept's hose and input. Checked 10 mm off the chosen handle and grip,
the crank's sweep and the decor: some pairs clash (bottom with down), the check says so.

SHIELD (shield()): a 5 mm plate round the drum's front end, ahead of its strap and behind the rear hoop
(z -46.5 to -41.5), on the drum (bore R 114.5, so nothing inside passes it): round (R 165, rolled rim,
rivets), gear (14 teeth, R 150 to 172), spiked (R 150 and eight spikes out to R 205), kite (a heater
shield, 340 wide, its point 230 down) and triangle (380 wide, point down, three claw slots). Checked 3 mm
off the handle, the grip, the inlet's lines and the crank's sweep.

DRIVE (body_crank()): with crank the flexible shaft goes and a crank comes out of the drum's right side on
the layshaft's axis: a riveted boss, a forged 82 mm arm turning 14 mm off the drum, a wooden knob with a brass
cap. The concept's own crank (its arm inside the casing) is hidden either way. The knob's sweep is checked
off the drum, the handle, the grip and the inlet.

Prints [OK ] / [FAIL]. Writes exports/ratling_skin/A<n>_<top>_<grip>_<inlet>_<drive>/<view>.jpg, and with SHEETS
exports/ratling_skin/sheets/A<n>_tops.jpg, A<n>_grips.jpg, A<n>_inlets.jpg and each variant's views.

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
INLET = _param("INLET", "back")
DRIVE = _param("DRIVE", "flex")
GRIP_ROLL = _param("GRIP_ROLL", 0.0, float)
TOP_ROLL = _param("TOP_ROLL", 0.0, float)
CROSS_Y = 157.0                                    # cross handle's grip axis: 30 mm for the fingers over the eye band
SIGHT = _param("SIGHT", "none")
SIGHTS = ("none", "iron", "ring", "warp", "scope")
assert SIGHT in SIGHTS, "SIGHT: one of %s" % (SIGHTS,)
SCALE = _param("SCALE", True, lambda v: str(v).lower() in ("1", "true", "yes"))
SHEETS = _param("SHEETS", False, lambda v: str(v).lower() in ("1", "true", "yes"))
TOPS = ("concept", "post", "arch", "triangle", "tiller", "loop", "cross")
GRIP_KINDS = ("concept", "butt", "spades", "down", "side")
INLETS = ("concept", "back", "left", "right", "bottom")
assert INLET in INLETS, "INLET: one of %s" % (INLETS,)
DRIVES = ("flex", "crank", "both")
assert DRIVE in DRIVES, "DRIVE: one of %s" % (DRIVES,)
FLEX = DRIVE in ("flex", "both")
SHIELD = _param("SHIELD", "none")
SHIELDS = ("none", "round", "gear", "spiked", "kite", "triangle")
assert SHIELD in SHIELDS, "SHIELD: one of %s" % (SHIELDS,)
assert BARRELS in (16, 19), "BARRELS: 16 or 19"
assert TOP in TOPS, "TOP: one of %s" % (TOPS,)
assert GRIP_KIND in GRIP_KINDS, "GRIP: one of %s" % (GRIP_KINDS,)

exec(open(os.path.join(REPO, "mitrailleuse", "mitrailleuse_concepts.py"), encoding="utf-8").read())

SKIN = "ratling_skin"
TAG = "A%d" % BARRELS
VI = [t for t, _, _, _ in VARIANTS].index(TAG)
_, GROUP, _, KEY = VARIANTS[VI]
OFF = V(0, -X_OFF * VI, 0)
OUT = os.path.join(REPO, "exports", SKIN, "%s_%s%s_%s%s_%s_%s_%s%s" % (
    TAG, TOP, "" if not TOP_ROLL else "%+.0f" % TOP_ROLL, GRIP_KIND, "" if not GRIP_ROLL else "%+.0f" % GRIP_ROLL, INLET, DRIVE, SHIELD,
    "" if SIGHT == "none" else "_" + SIGHT))
OUT_SHEETS = os.path.join(REPO, "exports", SKIN, "sheets")
os.makedirs(OUT, exist_ok=True)

# forged look: (colour, transparency)
FV.STYLES.update({
    "iron": ((0.20, 0.19, 0.18), 0), "iron_dark": ((0.13, 0.12, 0.12), 0), "rust": ((0.38, 0.23, 0.14), 0),
    "brass": ((0.78, 0.60, 0.28), 0), "copper": ((0.74, 0.38, 0.19), 0), "bronze": ((0.52, 0.37, 0.20), 0),
    "warp": ((0.35, 0.95, 0.25), 20), "leather": ((0.33, 0.20, 0.11), 0), "wood": ((0.40, 0.24, 0.12), 0),
    "rubber": ((0.16, 0.15, 0.13), 0), "glass": ((0.36, 0.17, 0.04), 25), "label": ((0.92, 0.88, 0.74), 0),
    "cap": ((0.85, 0.72, 0.30), 0), "ruler_dark": ((0.12, 0.12, 0.12), 0), "ruler_light": ((0.95, 0.80, 0.15), 0),
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


def bent_wire(dia, pts, n=24, sweep=True):
    """A round bar swept along a smooth curve through pts (a B-spline); short rods and balls if the sweep fails."""
    c = Part.BSplineCurve()
    c.interpolate([V(*q) for q in pts])
    try:
        if not sweep:
            raise ValueError
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
    cap = cyl(2 * CASE[0] + 8, BACK - 5, BACK).fuse(cyl(70, BACK - 12, BACK - 5))
    if FLEX and INLET in ("concept", "back"):       # the flexible shaft's input through the cap
        cap = cap.cut(cyl(24, BACK - 13, BACK + 1, 0, GEAR_C))
    s["End_cap"] = (cap, "iron")
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
    # loop: the art's big pointed oval, standing over the CoG on a saddle, its top wrapped as the grip
    hl, wl, bar = 210.0, 140.0, 14.0
    rv_ = (hl * hl / 4 + wl * wl / 4) / wl                 # the arcs' radius
    off_ = rv_ - wl / 2
    yb_ = yt + 8
    ym_ = yb_ + hl / 2

    def lens(shrink, x0, x1):
        a_ = rod(2 * (rv_ - shrink), (x0, ym_, zc + off_), (x1, ym_, zc + off_))
        b_ = rod(2 * (rv_ - shrink), (x0, ym_, zc - off_), (x1, ym_, zc - off_))
        return a_.common(b_)

    ring = lens(0, -6, 6).cut(lens(bar, -7, 7))
    wrap = lens(-3, -9, 9).cut(lens(bar + 3, -10, 10)).common(box(-12, 12, ym_ + 55, yb_ + hl + 5, zc - 90, zc + 90))
    h["loop"] = {"Loop": (ring, "iron"), "Grip": (wrap, "leather"),
                 "Saddle": (box(-10, 10, yt - 4, yt + 8, zc - 80, zc + 80), "iron"),
                 "Foot": (rod(34, (0, yt + 2, zc), (0, yb_ + 10, zc)), "brass"),
                 "Tip_spike": (cone_from((0, yb_ + hl - 6, zc), (0, yb_ + hl + 34, zc), 14), "iron_dark"),
                 "Rivets": (compound([Part.makeSphere(RIVET / 2, V(6, ym_ + dy, zc + sz * (wl / 2 - bar / 2 - 2)))
                                      for dy in (-30, 0, 30) for sz in (-1, 1)]), "brass")}
    h["concept"] = {"Grip": (p["Carry_handle"][0].copy(), "leather"), "Posts": (p["Carry_posts"][0].copy(), "iron")}
    # cross: the concept's handle turned across the gun, a bar over the eye band on two posts standing on it
    yx, xp = CROSS_Y, GRIP[1] / 2
    g, rg = leather_grip((-xp, yx, zc), (xp, yx, zc))
    h["cross"] = {"Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                  "Posts": (compound([box(sx * xp, sx * (xp + 12), 70, yx + 8, zc - 6, zc + 6).cut(
                      cyl(2 * A_RAIL_R + 11, zc - 7, zc + 7)) if sx > 0 else
                      box(sx * (xp + 12), sx * xp, 70, yx + 8, zc - 6, zc + 6).cut(cyl(2 * A_RAIL_R + 11, zc - 7, zc + 7))
                      for sx in (-1, 1)]), "iron"),
                  "Caps": (compound([Part.makeSphere(9, V(sx * (xp + 6), yx + 10, zc)) for sx in (-1, 1)]), "brass")}
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


# ---------------------------------------------------------------- INLET: where the supply hose and the flexible shaft come in
def ribbed(dia, pts, rib_style_pitch, n=40):
    """A tube swept along a curve through pts, with rings round it every pitch mm, and a ferrule at its end."""
    c = Part.BSplineCurve()
    c.interpolate([V(*q) for q in pts])
    body = bent_wire(dia, pts, n, sweep=False)            # the sweep leaves gaps on these long bends
    rings, L, u0, u1 = [], c.length(), c.FirstParameter, c.LastParameter
    k = int(L / rib_style_pitch)
    for i in range(1, k):
        u = c.parameterAtDistance(i * rib_style_pitch, u0)
        rings.append(Part.makeTorus(dia / 2, 1.4, c.value(u), c.tangent(u)[0]))
    tip, tt = c.value(u1), c.tangent(u1)[0]
    ferrule = Part.makeCylinder(dia / 2 + 2.5, 14, tip - tt * 12, tt)
    return body, compound(rings), ferrule


MOUNTS = {
    # side: mount centre, outward normal, the axis the two inputs sit along, the way the lines leave
    "back": (V(20, GEAR_C, BACK - 5), V(0, 0, -1), V(1, 0, 0), V(0.5, -0.7, -0.5)),
    "left": (V(*polar(CASE[0], -25), -250), V(*polar(1, -25), 0), V(0, 0, 1), V(0.3, -0.7, -0.65)),
    "right": (V(*polar(CASE[0], 225), -95), V(*polar(1, 225), 0), V(0, 0, 1), V(-0.3, -0.75, -0.55)),
    "bottom": (V(0, -CASE[0], -120), V(0, -1, 0), V(1, 0, 0), V(0, -0.5, -0.85)),
}


def inlet(side):
    """A riveted brass boss on the drum with the supply hose's union and the flexible shaft's collar side by
    side, both lines leaving it down and back for 240 mm: the hose corrugated, the shaft in a ribbed sheath."""
    if side == "concept":
        xv = HEAD[1] + 12                           # the supply hose, as concept_a draws it
        a, b = V(xv + 24, 0, -143.0 + 15), V(xv + 89, -60, -143.0 + 15 - 60)
        d = b - a
        parts = {"Hose_ribs": (compound([Part.makeTorus(4.6, 1.3, a + d * (i * 7 / d.Length), d)
                                         for i in range(1, int(d.Length / 7))]), "brass")}
        if FLEX:
            parts["Flex_collar"] = (tube(32, 5, BACK - 16, BACK - 5, 0, GEAR_C), "brass")
            parts["Flex_extension"] = (cyl(12, BACK - 16, -260, 0, GEAR_C), "iron")
        return parts
    c, nrm, a, out = MOUNTS[side]
    out = out.normalize()
    b = nrm.cross(a)
    parts = {"Boss": (rod(84, tuple(c - nrm * 4), tuple(c + nrm * 7)), "brass"),
             "Boss_rivets": (compound([Part.makeSphere(RIVET / 2, c + nrm * 7 + (a * math.cos(t) + b * math.sin(t)) * 36)
                                       for t in [i * math.pi / 4 for i in range(8)]]), "brass")}
    hose_p, flex_p = (c + a * 20, c - a * 20) if FLEX else (c, None)
    union = rod(26, tuple(hose_p + nrm * 7), tuple(hose_p + nrm * 17)).fuse(
        rod(18, tuple(hose_p + nrm * 17), tuple(hose_p + nrm * 28)))
    parts["Hose_union"] = (union, "brass")
    if FLEX:
        parts["Flex_collar"] = (rod(34, tuple(flex_p + nrm * 7), tuple(flex_p + nrm * 20)).fuse(
            rod(24, tuple(flex_p + nrm * 20), tuple(flex_p + nrm * 28))), "brass")
    lines = {}
    for nm, p, dia, pitch in (("Hose", hose_p, 16.0, 10.0), ("Flex", flex_p, 18.0, 6.0)):
        if p is None:
            continue
        s0 = p + nrm * 28
        pts = [s0, s0 + nrm * 30, s0 + nrm * 55 + out * 70, s0 + nrm * 70 + out * 240]
        body, rings, ferrule = ribbed(dia, [tuple(q) for q in pts], pitch)
        lines[nm] = (body, rings, ferrule)
    parts["Hose"] = (lines["Hose"][0], "rubber")
    parts["Hose_ribs"] = (lines["Hose"][1], "brass")
    if FLEX:
        parts["Flex_sheath"] = (lines["Flex"][0], "iron")
        parts["Flex_ribs"] = (lines["Flex"][1], "copper")
    parts["Ferrules"] = (compound([ln[2] for ln in lines.values()]), "brass")
    if FLEX and side == "back":                              # the concept's input is behind the bevel box: bring it to the cap
        parts["Flex_extension"] = (cyl(12, BACK - 5, -260, 0, GEAR_C), "iron")
    return parts


# ---------------------------------------------------------------- SHIELD: between the drum and the pack
SH_Z = (CASE[2] - 1.5, CASE[2] + 3.5)           # ahead of the drum's front strap, behind the rear hoop


def outline_rivets(pts, inset, step=36.0, z=None):
    """Rivets along a closed polygon, inset towards its centroid."""
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        L = math.hypot(x1 - x0, y1 - y0)
        for i in range(max(1, int(L / step))):
            t = (i + 0.5) / max(1, int(L / step))
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            k = inset / max(math.hypot(x - cx, y - cy), 1.0)
            out.append(Part.makeSphere(RIVET / 2, V(x - (x - cx) * k, y - (y - cy) * k, z)))
    return compound(out)


def shield(kind):
    z0, z1 = SH_Z
    hole = cyl(2 * CASE[0] + 1, z0 - 1, z1 + 1)
    zf = z0                                      # rivets on the back face, seen by the gunner
    if kind in ("round", "spiked"):
        R = 165.0 if kind == "round" else 150.0
        plate = cyl(2 * R, z0, z1)
        rim = Part.makeTorus(R - 1, 3.5, V(0, 0, (z0 + z1) / 2), Z)
        rv = rivets_round(R - 14, zf, 15.0)
        parts = {"Shield": (plate.fuse(rim).cut(hole), "iron"), "Shield_rivets": (rv, "brass")}
        if kind == "spiked":
            parts["Shield_spikes"] = (compound([cone_from(polar(R - 4, a) + ((z0 + z1) / 2,),
                                                          polar(205, a) + ((z0 + z1) / 2,), 18)
                                                for a in (22.5 + 45 * k for k in range(8))]), "iron_dark")
            parts["Shield"] = (parts["Shield"][0], "copper")
        return parts
    if kind == "gear":
        n, r0, r1, pts = 14, 150.0, 172.0, []
        for i in range(n):
            a = 360.0 / n * i
            for da, rr in ((-0.30, r0), (-0.18, r1), (0.18, r1), (0.30, r0)):
                pts.append(polar(rr, a + da * 360.0 / n))
        plate = Part.Face(Part.makePolygon([V(x, y, z0) for x, y in pts + pts[:1]])).extrude(V(0, 0, z1 - z0))
        return {"Shield": (plate.cut(hole), "brass"), "Shield_rivets": (rivets_round(136, zf, 360.0 / n), "iron_dark")}
    if kind == "kite":
        pts = [(-170, 150), (170, 150), (160, 20), (100, -130), (0, -230), (-100, -130), (-160, 20)]
    else:
        pts = [(-190, 150), (190, 150), (0, -230)]
    plate = Part.Face(Part.makePolygon([V(x, y, z0) for x, y in pts + pts[:1]])).extrude(V(0, 0, z1 - z0)).cut(hole)
    if kind == "triangle":
        for k in (-1, 0, 1):                       # three claw slots in the upper corners and the point
            for cxy in ((-120, 105), (120, 105), (0, -170)):
                slot = Part.makeBox(5, 34, z1 - z0 + 2, V(-2.5, -17, z0 - 1))
                slot.rotate(V(0, 0, 0), Z, 20)
                slot.translate(V(cxy[0] + 11 * k, cxy[1], 0))
                plate = plate.cut(slot)
    return {"Shield": (plate, "rust" if kind == "kite" else "brass"),
            "Shield_rivets": (outline_rivets(pts, 12.0, z=zf), "brass")}


# ---------------------------------------------------------------- DRIVE: the flexible shaft, or a crank on the drum
CRANK = (82.0, 14.0)                           # skin crank: arm (axis to knob), how far out of the drum its arm turns


def body_crank():
    """The crank brought out of the drum's right side on the concept's layshaft axis (y GEAR_C, z -210): a riveted
    boss, the shaft through the wall, a forged arm turning CRANK[1] mm off the drum, a wooden knob with a brass
    cap; drawn pointing down. Replaces the concept's crank, whose arm turns inside the casing."""
    zc_, yc_ = -210.0, GEAR_C
    x0 = -(CASE[0] - 6)
    xa = -(CASE[0] + CRANK[1])                     # the arm's inner face
    b = rod(64, (x0, yc_, zc_), (-(CASE[0] + 6), yc_, zc_))
    rv = compound([Part.makeSphere(RIVET / 2, V(-(CASE[0] + 6), yc_ + 26 * math.cos(t), zc_ + 26 * math.sin(t)))
                   for t in [i * math.pi / 3 for i in range(6)]])
    shaft = rod(14, (x0, yc_, zc_), (xa - 12, yc_, zc_))
    hub = rod(30, (xa, yc_, zc_), (xa - 12, yc_, zc_))
    yk = yc_ - CRANK[0]
    arm = box(xa - 10, xa, yk, yc_, zc_ - 8, zc_ + 8).fuse(rod(22, (xa, yk, zc_), (xa - 10, yk, zc_)))
    knob = rod(26, (xa - 10, yk, zc_), (xa - 90, yk, zc_))
    cap = Part.makeSphere(15, V(xa - 92, yk, zc_))
    sweep = rod(2 * (CRANK[0] + 16), (xa + 2, yc_, zc_), (xa - 108, yc_, zc_))
    return {"Crank_boss": (b, "brass"), "Crank_rivets": (rv, "brass"), "Crank_shaft": (shaft.fuse(hub), "iron"),
            "Crank_arm": (arm, "iron"), "Crank_knob": (knob, "wood"), "Crank_cap": (cap, "brass")}, sweep


# ---------------------------------------------------------------- SIGHT: over the drum and the sleeve band
SIGHT_Z = (-55.0, Z_TIP - 32)                    # the rear sight on the drum's front, the front one on the sleeve band


def sights(kind, y_line):
    """Sights for a line of sight at y_line over the gun's axis (x 0); the scope sits on the drum's right."""
    zr, zf = SIGHT_Z
    y_top = CASE[0]                                # the drum's top
    y_band = REAR_R + 2                            # the sleeve band's top
    p = {}
    if kind in ("iron", "ring", "warp"):
        p["Front_post"] = (box(-3, 3, y_band - 4, y_line - (0 if kind == "iron" else 0), zf - 3, zf + 3)
                           .fuse(box(-8, 8, y_band - 4, y_band + 6, zf - 8, zf + 8)), "iron")
        p["Rear_post"] = (box(-6, 6, y_top - 4, y_line - 12, zr - 4, zr + 4)
                          .fuse(box(-16, 16, y_top - 4, y_top + 4, zr - 8, zr + 8)), "iron")
    if kind == "iron":                             # a blade and a V-notch leaf
        leaf = box(-30, 30, y_line - 14, y_line + 10, zr - 2, zr + 2)
        notch = Part.Face(Part.makePolygon([V(-7, y_line + 11, zr - 3), V(7, y_line + 11, zr - 3),
                                            V(0, y_line, zr - 3), V(-7, y_line + 11, zr - 3)])).extrude(V(0, 0, 6))
        p["Rear_leaf"] = (leaf.cut(notch), "brass")
        p["Front_blade"] = (box(-1.5, 1.5, y_line - 2, y_line + 4, zf - 6, zf + 6), "brass")
    elif kind == "ring":                           # an AA ring with a cross, and a peep
        ring = Part.makeTorus(40, 2.2, V(0, y_line, zf), Z)
        cross = compound([rod(3, (0, y_line - 40, zf), (0, y_line + 40, zf)), rod(3, (-40, y_line, zf), (40, y_line, zf))])
        p["Front_ring"] = (compound([ring, cross]), "brass")
        p["Peep"] = (Part.makeTorus(8, 2.5, V(0, y_line, zr), Z), "brass")
    elif kind == "warp":                           # a brass frame round a green glass pane, a green bead in front
        frame = box(-30, 30, y_line - 22, y_line + 22, zr - 3, zr + 3).cut(box(-24, 24, y_line - 16, y_line + 16, zr - 4, zr + 4))
        p["Reflex_frame"] = (frame, "brass")
        p["Reflex_pane"] = (box(-24, 24, y_line - 16, y_line + 16, zr - 0.5, zr + 0.5), "warp")
        p["Front_bead"] = (Part.makeSphere(4, V(0, y_line, zf)), "warp")
    elif kind == "scope":                          # a brass telescope on the drum's upper right
        xs, ys, z0, z1 = -50.0, y_line, -235.0, 70.0
        y_d = math.sqrt(CASE[0] ** 2 - xs ** 2)
        body = rod(30, (xs, ys, z0), (xs, ys, z1)).fuse(rod(40, (xs, ys, z1 - 60), (xs, ys, z1))) \
            .fuse(rod(36, (xs, ys, z0), (xs, ys, z0 + 40)))
        p["Scope"] = (body, "brass")
        p["Scope_bands"] = (compound([Part.makeTorus(15.5, 1.6, V(xs, ys, z), Z) for z in (-150, -100, -20)]), "copper")
        p["Scope_lenses"] = (compound([rod(34, (xs, ys, z1 - 1), (xs, ys, z1)), rod(30, (xs, ys, z0), (xs, ys, z0 + 1))]),
                             "warp")
        p["Scope_mounts"] = (compound([box(xs - 6, xs + 6, y_d - 6, ys - 12, z - 6, z + 6).fuse(
            Part.makeTorus(16.5, 3, V(xs, ys, z), Z)) for z in (-205, -95)]), "iron")
    return p


# ---------------------------------------------------------------- SCALE: things everyone knows the size of
BOTTLE = ((0, 0), (33, 0), (33, 165), (30, 180), (16, 205), (13, 215), (13, 243), (0, 243))   # 0.5 l, Ø66 x 250


def scale_refs(y0, z0):
    """A 0.5 l beer bottle standing on the ground (y0) and a 1 m ruler lying on it along the gun from z0, both on
    the gunner's left: ten 100 mm bars, a tick every 10 mm, a long one every 50."""
    xr = CASE[0] + 110
    bars = {"ruler_dark": [], "ruler_light": []}
    for i in range(10):
        bars["ruler_dark" if i % 2 else "ruler_light"].append(box(xr, xr + 40, y0 - 3, y0, z0 + 100 * i, z0 + 100 * i + 100))
    ticks = [box(xr, xr + (16 if k % 5 else 26), y0, y0 + 0.8, z0 + 10 * k - 0.6, z0 + 10 * k + 0.6)
             for k in range(101) if k % 10]
    prof = Part.makePolygon([V(x, y, 0) for x, y in BOTTLE + BOTTLE[:1]])
    glass = Part.Face(prof).revolve(V(0, 0, 0), V(0, 1, 0), 360)
    lab = Part.makeCylinder(33.4, 75, V(0, 45, 0), V(0, 1, 0)).cut(Part.makeCylinder(32.9, 77, V(0, 44, 0), V(0, 1, 0)))
    cap = Part.makeCylinder(14.5, 7, V(0, 243, 0), V(0, 1, 0))
    at = V(xr + 110, y0, z0 + 500)
    for sh in (glass, lab, cap):
        sh.translate(at)
    return {"Ruler_dark": (compound(bars["ruler_dark"]), "ruler_dark"),
            "Ruler_light": (compound(bars["ruler_light"] + []), "ruler_light"),
            "Ruler_ticks": (compound(ticks), "ruler_dark"),
            "Bottle": (glass, "glass"), "Bottle_label": (lab, "label"), "Bottle_cap": (cap, "cap")}


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

INLET_PARTS = {side: inlet(side) for side in INLETS if side == INLET or SHEETS}
for side, parts in INLET_PARTS.items():
    add_all("%s_i_%s" % (TAG, side), "%s_i_%s" % (TAG, side), parts)
IN_A = compound([sh for sh, _ in INLET_PARTS[INLET].values()] +
                ([P_A["Supply_hose"][0], P_A["Flex_shaft_input"][0]] if INLET == "concept" else []))
CRANK_SWEEP = None
if DRIVE != "flex":
    CRANK_PARTS, CRANK_SWEEP = body_crank()
    add_all(TAG + "_drive", TAG + "_drive", CRANK_PARTS)
    c = clear(CRANK_SWEEP, cyl(2 * CASE[0] + 8, BACK - 5, CASE[2]))      # the drum over its straps
    check(c >= 2.0, "%s crank on the drum: arm %.0f mm, its sweep %.0f mm off the drum's straps, the knob's circle"
          " from y %.0f to %.0f" % (TAG, CRANK[0], c, GEAR_C - CRANK[0], GEAR_C + CRANK[0]))

HANDLES = handles(P_A)
# a handle rolled onto the side takes that side's sling eye's place (the sling hooks on its posts): keep the other eye
EYES, EYE_SIDE = P_A["Sling_eyes"][0], 0
if abs(math.sin(math.radians(TOP_ROLL))) > 0.5 and TOP != "tiller":
    EYE_SIDE = 1 if TOP_ROLL > 0 else -1
    EYES = EYES.common(box(-1000, 0, -1000, 1000, -2000, 2000) if EYE_SIDE > 0 else box(0, 1000, -1000, 1000, -2000, 2000))
    add_all(TAG + "_eye", TAG, {"Sling_eye": (EYES, "iron")})
others = compound([P_A[n][0] for n in ("Eye_band", "Rails", "Rear_casing")] + [EYES] + [IN_A] +
                  [SK[n][0] for n in ("Hoops", "Warp_vial", "Vial_clamps", "Casing_extension", "End_cap", "Spikes",
                                      "Claw_plate", "Warp_gauge")])
others_ne = compound([P_A[n][0] for n in ("Rails", "Rear_casing")] + [EYES] + [IN_A] +
                     [SK[n][0] for n in ("Hoops", "Warp_vial", "Vial_clamps", "Casing_extension", "End_cap", "Spikes",
                                         "Claw_plate", "Warp_gauge")])
for hn, parts in HANDLES.items():
    if hn != TOP and not SHEETS:
        continue
    if TOP_ROLL and hn != "tiller":                # turned round the gun's axis; the tiller stays on the drum
        for n_, (sh, st) in list(parts.items()):
            sh = sh.copy()
            sh.rotate(V(0, 0, 0), Z, -TOP_ROLL)        # + is towards the gunner's left (+x)
            parts[n_] = (sh, st)
    add_all("%s_h_%s" % (TAG, hn), "%s_h_%s" % (TAG, hn), parts)
    c = clear(parts["Grip"][0], others if hn != "concept" else others_ne)    # it sits on the eye band
    size = "loop 210 x 140, bar 14" if hn == "loop" else "grip Ø%.0f x %.0f" % GRIP
    check(c >= 30.0, "%s top %s: %s, %.0f mm from the nearest part for the fingers" % (TAG, hn, size, c))

GRIPS, (G_O, G_D, G_N) = rear_grips()
drum = cyl(2 * CASE[0], BACK, CASE[2])
for gn, parts in GRIPS.items():
    if gn != GRIP_KIND and not SHEETS:
        continue
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
        room = clear(parts["Grip"][0], compound([drum, SK["Claw_plate"][0], SK["Warp_gauge"][0], IN_A]))
    check(inside < 1.0 and room >= 20.0, "%s grip %s: grip and trigger outside the drum (%.0f mm3 in), %.0f mm"
          " for the fingers" % (TAG, gn, inside, room))
    if GRIP_ROLL:                                  # turned round the drum's axis: the checks above still hold
        for n_, (sh, st) in list(parts.items()):
            sh = sh.copy()
            sh.rotate(V(0, 0, 0), Z, -GRIP_ROLL)       # + is towards the gunner's left (+x)
            parts[n_] = (sh, st)
    add_all("%s_g_%s" % (TAG, gn), "%s_g_%s" % (TAG, gn), parts)
# the inlet against the chosen handle and grip, the crank's sweep and the decor
near = {"claw plate": SK["Claw_plate"][0], "warp gauge": SK["Warp_gauge"][0],
        "spikes": SK["Spikes"][0], "tripod pad": P_A["Tripod_pad"][0]}
if TOP != "concept" or TOP_ROLL:
    near["top " + TOP] = compound([sh for sh, _ in HANDLES[TOP].values()])
if CRANK_SWEEP is not None:
    near["crank's sweep"] = CRANK_SWEEP
near["grip " + GRIP_KIND] = compound([sh for sh, _ in GRIPS[GRIP_KIND].values()]) if GRIP_KIND != "concept" else \
    compound([P_A[n][0] for n in ("Rear_grip", "Trigger")])
if CRANK_SWEEP is not None:
    for nm in [n for n in near if n.startswith(("top", "grip"))]:
        c = clear(CRANK_SWEEP, near[nm])
        check(c >= 10.0, "%s crank: the knob's sweep %.0f mm from the %s" % (TAG, c, nm))
for side, parts in INLET_PARTS.items():
    if side == "concept":
        continue
    lines = compound([sh for sh, _ in parts.values()])
    worst = min((clear(lines, sh), nm) for nm, sh in near.items())
    check(worst[0] >= 10.0, "%s inlet %s: hose and shaft %.0f mm from the nearest (%s)" % (TAG, side, worst[0], worst[1]))
SHIELD_PARTS = {k: shield(k) for k in SHIELDS[1:] if k == SHIELD or SHEETS}
for k, parts in SHIELD_PARTS.items():
    add_all("%s_s_%s" % (TAG, k), "%s_s_%s" % (TAG, k), parts)
    sh_ = compound([p_ for p_, _ in parts.values()])
    worst = min([(clear(sh_, near[nm]), nm) for nm in near if nm.startswith(("top", "grip", "crank"))] +
                [(clear(sh_, IN_A), "inlet " + INLET)])
    bb = sh_.BoundBox
    check(worst[0] >= 3.0, "%s shield %s: %.0f x %.0f mm, %.0f mm from the nearest (%s)"
          % (TAG, k, bb.XLength, bb.YLength, worst[0], worst[1]))
SIGHT_PARTS = {}
if SIGHT != "none" or SHEETS:
    # the line of sight: 10 mm over whatever is shown along the gun's top centre between the sights
    band = box(-15, 15, 0, 600, SIGHT_Z[0] + 8, SIGHT_Z[1] - 8)
    tops = [P_A[n][0] for n in P_A if n not in ("Carry_handle", "Carry_posts") or TOP == "tiller"] + \
           [sh for sh, _ in SK.values()]
    for grp in (HANDLES.get(TOP), SHIELD_PARTS.get(SHIELD)):
        tops += [sh for sh, _ in (grp or {}).values()]
    y_line = max([c_.BoundBox.YMax for c_ in (t.common(band) for t in tops if t.BoundBox.intersect(band.BoundBox))
                  if c_.Volume > 1e-6] + [0]) + 10
    for k in SIGHTS[1:]:
        if k != SIGHT and not SHEETS:
            continue
        SIGHT_PARTS[k] = sights(k, 175.0 if k == "scope" else y_line)
        add_all("%s_v_%s" % (TAG, k), "%s_v_%s" % (TAG, k), SIGHT_PARTS[k])
        sh_ = compound([p_ for p_, _ in SIGHT_PARTS[k].values()])
        worst = min([(clear(sh_, near[nm]), nm) for nm in near if nm.startswith(("top", "grip", "crank"))] +
                    [(clear(sh_, SK["Warp_vial"][0]), "vial"), (clear(sh_, SK["Spikes"][0]), "spikes")])
        check(worst[0] >= 3.0, "%s sight %s: line of sight at y %.0f (%.0f over the drum), %.0f mm from the nearest (%s)"
              % (TAG, k, 175.0 if k == "scope" else y_line, (175.0 if k == "scope" else y_line) - CASE[0],
                 worst[0], worst[1]))
if SCALE:
    shown = [sh for sh, _ in P_A.values()] + [sh for sh, _ in SK.values()] + [IN_A]
    for grp in (HANDLES.get(TOP), GRIPS.get(GRIP_KIND), SHIELD_PARTS.get(SHIELD), SIGHT_PARTS.get(SIGHT),
                CRANK_PARTS if DRIVE != "flex" else None):
        shown += [sh for sh, _ in (grp or {}).values()]
    lo = min(sh.BoundBox.YMin for sh in shown)
    z_back = min(sh.BoundBox.ZMin for sh in shown)
    z_front = max(sh.BoundBox.ZMax for sh in shown)
    add_all(TAG + "_scale", TAG + "_scale", scale_refs(lo - 10, z_back))
    print("      scale: the gun %.0f mm long (z %.0f to %.0f), %.0f mm high; ruler 1000 mm from its back, bottle 0.5 l"
          " (Ø66 x 250)" % (z_front - z_back, z_back, z_front, max(sh.BoundBox.YMax for sh in shown) - lo))
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
             "left": (0.0, -1.0, 0.0), "low": (-0.55, 0.75, 0.30), "top": (0.0, 0.0, -1.0),
             "back": (1.0, 0.0, 0.0), "front_low": (-0.70, 0.55, 0.30), "rear_left": (0.62, -0.62, -0.40)}
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

    def show(top, grip, close=False, side=None, shield_=None, sight_=None):
        side = side or INLET
        groups = [GROUP, TAG + "_skin", "%s_i_%s" % (TAG, side)] + \
                 (["%s_h_%s" % (TAG, top)] if not close else []) + \
                 (["%s_g_%s" % (TAG, grip)] if grip != "concept" else [])
        hide = ([] if top == "tiller" else CONCEPT_TOP) + ([] if grip == "concept" else CONCEPT_GRIP) + \
               ([] if side == "concept" else [TAG + "_Supply_hose", TAG + "_Flex_shaft_input"]) + \
               [TAG + "_Crank_shaft", TAG + "_Crank_arm", TAG + "_Crank_knob"] + \
               ([] if FLEX else [TAG + "_Flex_shaft_input"])
        if DRIVE != "flex":
            groups.append(TAG + "_drive")
        if EYE_SIDE and not close:
            groups.append(TAG + "_eye")
            hide.append(TAG + "_Sling_eyes")
        if (sight_ or SIGHT) != "none":
            groups.append("%s_v_%s" % (TAG, sight_ or SIGHT))
        if SCALE and not close:
            groups.append(TAG + "_scale")
        if (shield_ or SHIELD) != "none":
            groups.append("%s_s_%s" % (TAG, shield_ or SHIELD))
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
        files = []
        for i, side in enumerate(INLETS[1:]):
            show(TOP, GRIP_KIND, close=True, side=side)
            seen = (0.85, -0.35, -0.2) if side == "left" else VIEWS["rear"]       # the left flank from its side
            for vn, dv in (("rear", seen), ("low", (0.45, 0.60, 0.30))):
                f = snap(os.path.join(OUT_SHEETS, "%s_inlet%d_%s_%s" % (TAG, i + 1, side, vn)), dv, 1000)
                if vn == "rear":
                    files.append(f)
        sheet(files, os.path.join(OUT_SHEETS, "%s_inlets.jpg" % TAG))
        files = []
        for i, k in enumerate(SHIELDS[1:]):
            show(TOP, GRIP_KIND, shield_=k)
            for vn in ("rear", "front"):
                f = snap(os.path.join(OUT_SHEETS, "%s_shield%d_%s_%s" % (TAG, i + 1, k, vn)), VIEWS[vn])
                if vn == "rear":
                    files.append(f)
        sheet(files, os.path.join(OUT_SHEETS, "%s_shields.jpg" % TAG))
        files = []
        for i, k in enumerate(SIGHTS[1:]):
            show(TOP, GRIP_KIND, shield_=SHIELD, sight_=k)
            for vn in ("side", "rear"):
                f = snap(os.path.join(OUT_SHEETS, "%s_sight%d_%s_%s" % (TAG, i + 1, k, vn)), VIEWS[vn])
                if vn == "rear":
                    files.append(f)
        sheet(files, os.path.join(OUT_SHEETS, "%s_sights.jpg" % TAG))
    print("renders written to", OUT)
