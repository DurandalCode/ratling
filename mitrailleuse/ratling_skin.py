# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse: a skaven "ratling gun" skin over concept A, at 16 and 19 barrels. Sketches only.

Builds mitrailleuse_concepts.py as it is (its geometry untouched), recolours A16 and A19 as forged iron,
brass and copper, and adds decor around them as masses: nothing here is a part yet, and nothing moves or
cuts a part of the concept. What is added, and where:

- copper bands on every muzzle sleeve (Ø36 x 10 at z 335 and 415) and a crown at its tip (Ø36, the last
  14 mm, a Ø37 lip): sleeves are on a 40 mm pitch, so 4 / 3 mm between neighbours (checked);
- riveted brass hoops round the rails at the front plate and the rear plate (Ø222 / Ø238), and rivets on
  the sling-eye band;
- the rear casing as a riveted iron drum: two copper straps at its ends, a seam of rivets on top and a
  crest of spikes on its rear rim at the top (clear of the flexible shaft input and the crank);
- a raised brass triangle with three claw slots on the upper left of the casing (gunner's left), and a
  round green "warp" lens on a brass gauge ahead of the supply hose;
- a green glass vial in two brass clamps along the top of the casing;
- a forged spike under the muzzles, on a lug from the sleeve band, 40 mm past the tips;
- brass ribs on the supply hose, as a corrugated hose;
- the drum DEPTH (70 mm) deeper than the concept's casing, to z -300, under a riveted cap; the flexible
  shaft's input brought out through it (the rear block is not final, this only sets the look);
- four handles for A16 to choose from, after the miniature (handles(), each in its own group): an upright
  post with a knob, a riveted arch from hoop to hoop, an inverted spiked triangle, and a tiller off the
  drum's left side; the grips Ø32 x 115 with 30 mm or more for the fingers (checked).
- four layouts of the control grip with the trigger for A16 (rear_grips()): an old pistol's butt out of the
  cap (the miniature), spade grips behind the cap, a grip down from the drum in a D-bow (on the concept's
  axis, from where it leaves the drum: the concept's trigger sits under the drum), a grip along the flank.

Prints [OK ] / [FAIL] for the clearances it relies on. Writes exports/ratling_skin/<tag>_<view>.jpg, A16_handle<n>_<name>_<view>.jpg, A16_handles_side.jpg,
A16_grip<n>_<name>_<view>.jpg and A16_grips.jpg.

Run inside FreeCAD (GUI):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/ratling_skin.py').read())
"""

import math
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PIL import Image, ImageChops

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "mitrailleuse", "mitrailleuse_concepts.py"), encoding="utf-8").read())

SKIN = "ratling_skin"
OUT = os.path.join(REPO, "exports", SKIN)
os.makedirs(OUT, exist_ok=True)

# forged look: (colour, transparency)
FV.STYLES.update({
    "iron": ((0.20, 0.19, 0.18), 0), "iron_dark": ((0.13, 0.12, 0.12), 0), "rust": ((0.38, 0.23, 0.14), 0),
    "brass": ((0.78, 0.60, 0.28), 0), "copper": ((0.74, 0.38, 0.19), 0), "bronze": ((0.52, 0.37, 0.20), 0),
    "warp": ((0.35, 0.95, 0.25), 20), "leather": ((0.33, 0.20, 0.11), 0), "wood": ((0.45, 0.29, 0.15), 0),
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
DEPTH = 70.0                                    # the drum drawn this much deeper than the concept's casing, capped
BACK = CASE[1] - DEPTH
BAND = (36.0, 10.0, (335.0, 415.0))             # sleeve bands: OD, length, z
CROWN = (36.0, 14.0)
HOOP = (222.0, 238.0, 18.0)                     # ID, OD, width
RIVET = 5.0


def compound(shapes):
    return Part.makeCompound(list(shapes))


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


def claw_triangle(r_case, z_mid, a, side=110.0):
    """A raised triangle on the casing at angle a, point forward, with three claw slots, hugging the drum."""
    h = side * math.sqrt(3) / 2
    # in the plate's own frame: u along z, w across (tangential)
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


def skin(tag, key, p):
    pts = LAYOUT[key]
    s = {}
    # sleeves: bands and crowns, copper
    bands = []
    for x, y in pts:
        for z in BAND[2]:
            bands.append(tube(BAND[0], (BAND[0] - SLEEVE[0]) / 2, z, z + BAND[1], x, y))
        bands.append(tube(CROWN[0], (CROWN[0] - SLEEVE[0]) / 2, Z_TIP - CROWN[1], Z_TIP, x, y))
        bands.append(tube(CROWN[0] + 1, 3.0, Z_TIP - 4, Z_TIP, x, y))
    s["Sleeve_bands"] = (compound(bands), "copper")
    # hoops round the rails at the plates, riveted
    hoops, rv = [], []
    for z0 in (A_PLATES[1][0] - 4, A_PLATES[0][0] - 10):
        hoops.append(tube(HOOP[1], (HOOP[1] - HOOP[0]) / 2, z0, z0 + HOOP[2]))
        rv.append(rivets_round(HOOP[1] / 2, z0 + HOOP[2] / 2, 15.0))
    zc = p["Eye_band"][0].BoundBox.Center.z
    rv.append(rivets_round(A_RAIL_R + 6, zc, 15.0, skip=(0, 90, 180) + tuple(range(225, 316, 15))))
    s["Hoops"] = (compound(hoops), "brass")
    # casing: DEPTH deeper, capped; straps at its ends and on the joint, a seam on top, spikes on the rear rim
    s["Casing_extension"] = (tube(2 * CASE[0], 2.0, BACK, CASE[1] + 1), "iron")
    cap = cyl(2 * CASE[0] + 8, BACK - 5, BACK).fuse(cyl(70, BACK - 12, BACK - 5)).cut(cyl(24, BACK - 13, BACK + 1,
                                                                                           0, GEAR_C))
    s["End_cap"] = (cap, "iron")
    s["Flex_collar"] = (tube(32, 5, BACK - 16, BACK - 5, 0, GEAR_C), "brass")
    s["Flex_extension"] = (cyl(12, BACK - 16, -260, 0, GEAR_C), "iron")       # the input brought out through the cap
    rv_hoops, rv = rv, []                        # the drum's own rivets apart, for close views of the rear
    rv.append(compound([Part.makeSphere(RIVET / 2, V(*polar(CASE[0] - 2, 15 * i), BACK - 5)) for i in range(24)]))
    straps = [tube(2 * CASE[0] + 8, 4, z, z + 12) for z in (BACK + 2, CASE[1] - 6, CASE[2] - 14)]
    for z in (BACK + 8, CASE[1], CASE[2] - 8):
        rv.append(rivets_round(CASE[0] + 4, z, 12.0))
    for i in range(int((CASE[2] - BACK - 40) / 11.5) + 1):
        z = BACK + 20 + i * 11.5
        rv.append(compound([Part.makeSphere(RIVET / 2, V(*polar(CASE[0], a), z)) for a in (78, 102)]))
    s["Casing_straps"] = (compound(straps), "copper")
    s["Rivets"] = (compound(rv_hoops), "brass")
    s["Drum_rivets"] = (compound(rv), "brass")
    spikes = []
    for a in (55, 75, 90, 105, 125):
        x, y = polar(CASE[0] + 2, a)
        tx, ty = polar(CASE[0] + 30, a)
        spikes.append(cone_from((x, y, BACK + 6), (tx, ty, BACK - 34), 16))
    # under the muzzles: a lug from the sleeve band and a forged spike
    y_s = -(_ns["shroud_r"](LAYOUT[key]) + 2.0 + 9.0)
    lug = box(-7, 7, y_s, y_s + 12, Z_TIP - 34, Z_TIP - 22)
    s["Spikes"] = (compound(spikes), "iron_dark")
    s["Muzzle_spike"] = (cone_from((0, y_s + 3, Z_TIP - 40), (0, y_s + 3, Z_TIP + 40), 18), "iron_dark")
    s["Spike_lug"] = (lug, "iron")
    # the claw triangle and the warp gauge, gunner's left (+x), and a vial along the top
    s["Claw_plate"] = (claw_triangle(CASE[0], -135.0, 40.0), "brass")
    zg, ag = -80.0, 0.0
    gauge = radial(40, CASE[0] - 2, CASE[0] + 10, ag, zg)
    s["Warp_gauge"] = (gauge, "brass")
    s["Warp_lens"] = (radial(30, CASE[0] + 10, CASE[0] + 13, ag, zg), "warp")
    yv = CASE[0] + 16
    s["Warp_vial"] = (cyl(22, -260, -80, 0, yv).fuse(Part.makeSphere(11, V(0, yv, -80)))
                      .fuse(Part.makeSphere(11, V(0, yv, -260))), "warp")
    clamps = [tube(30, 4, z, z + 10, 0, yv).fuse(box(-5, 5, CASE[0] - 2, yv - 12, z, z + 10)) for z in (-245, -105)]
    s["Vial_clamps"] = (compound(clamps), "brass")
    # supply hose ribs
    xv = HEAD[1] + 12
    a, b = V(xv + 24, 0, -143.0 + 15), V(xv + 89, -60, -143.0 + 15 - 60)
    d = b - a
    ribs = []
    for i in range(1, int(d.Length / 7)):
        c = a + d * (i * 7 / d.Length)
        ribs.append(Part.makeTorus(4.6, 1.3, c, d))
    s["Hose_ribs"] = (compound(ribs), "brass")
    return s


def clear(a, b):
    return a.distToShape(b)[0]


SKINS = {}
SKIN_NAMES = set()
for i, (tag, group, fn, key) in enumerate(VARIANTS[:2]):
    p = BUILT[tag]
    s = skin(tag, key, p)
    SKINS[tag] = s
    off = V(0, -X_OFF * i, 0)
    for n, (shape, style) in s.items():
        SKIN_NAMES.add("%s_%s" % (tag, n))
        sc.add(tag + "_skin", "%s_%s" % (tag, n), to_view(shape), style, offset=off)
    # checks: sleeve bands between neighbours, decor off the parts it must not touch
    pts = LAYOUT[key]
    gap = min(math.dist(u, w) for j, u in enumerate(pts) for w in pts[j + 1:]) - CROWN[0] - 1
    check(gap >= 2.0, "%s: sleeve crowns Ø%.0f, %.1f mm between neighbours (bands Ø%.0f: %.1f)"
          % (tag, CROWN[0] + 1, gap, BAND[0], gap + CROWN[0] + 1 - BAND[0]))
    for dn, pn in (("Hoops", "Carry_posts"), ("Hoops", "Sling_eyes"), ("Spikes", "Flex_shaft_input"),
                   ("Spikes", "Crank_knob"), ("Drum_rivets", "Crank_knob"), ("Claw_plate", "Supply_hose"), ("Warp_gauge", "Supply_hose"),
                   ("Rivets", "Carry_posts"), ("Rivets", "Tripod_pad")):
        c = clear(s[dn][0], p[pn][0])
        check(c >= 2.0, "%s: %s clear of %s by %.1f mm" % (tag, dn.lower(), pn, c))
    reach = max(s[n][0].BoundBox.ZMax for n in s)
    print("      %s: decor reaches z %.0f (sleeve tips %.0f), %.0f g if printed solid in PLA"
          % (tag, reach, Z_TIP, sum(sh.Volume for sh, _ in s.values()) / 1000 * 1.27))
# ---------------------------------------------------------------- handle variants (A16), after the miniature
GRIP = (32.0, 115.0)                            # leather grip: Ø, length (a gloved hand: 30-34 x 110+)


def leather_grip(p, q):
    g = rod(GRIP[0], p, q)
    d = V(*q) - V(*p)
    rings = compound([Part.makeTorus(GRIP[0] / 2, 1.6, V(*p) + d * t, d) for t in (0.04, 0.96)])
    return g, rings


def handles(p):
    """Four ways to hold A16 from the top, each in its own group; the concept's carry handle hidden for 1-3.

    post:     an upright grip with a knob, on a bar over the concept's posts (miniature: the hand on a post)
    arch:     a riveted strap from the front hoop to the rear one, a grip on it over the CoG
    triangle: an inverted riveted triangle on the sling-eye band, its top bar the grip, spikes at the corners
    tiller:   a bar off the drum's left side, back past the cap, with an upright grip and a trigger lever
              (miniature: the crew's bar at the back); the concept's top handle stays
    """
    zc = p["Eye_band"][0].BoundBox.Center.z
    yt = p["Carry_posts"][0].BoundBox.YMax
    h = {}
    # 1. post
    g, rg = leather_grip((0, yt + 22, zc), (0, yt + 22 + GRIP[1], zc))
    bar = box(-10, 10, yt - 4, yt + 8, zc - 80, zc + 80)
    h["post"] = {"Grip": (g, "leather"), "Grip_rings": (rg, "copper"), "Saddle": (bar, "iron"),
                 "Collar": (rod(44, (0, yt + 8, zc), (0, yt + 22, zc)), "brass"),
                 "Knob": (Part.makeSphere(23, V(0, yt + 22 + GRIP[1] + 14, zc)), "brass"),
                 "Knob_spike": (cone_from((0, yt + 22 + GRIP[1] + 30, zc), (0, yt + 22 + GRIP[1] + 62, zc), 14),
                                "iron_dark"),
                 "Rivets": (compound([Part.makeSphere(RIVET / 2, V(0, yt + 8, z)) for z in
                                      (zc - 70, zc - 50, zc + 50, zc + 70)]), "brass")}
    # 2. arch: legs on the hoops' tops, a strap over them, the grip on the strap at the CoG
    zf, zr = A_PLATES[1][0] - 4, A_PLATES[0][0] - 10           # the hoops' front faces, as in skin()
    y0, ys = HOOP[1] / 2 - 2, 172.0
    legs = [box(-14, 14, y0, ys, z, z + 14) for z in (zf + 2, zr + 2)]
    strap = box(-14, 14, ys - 9, ys, zr + 2, zf + 16)
    g, rg = leather_grip((0, ys - 4.5, zc - GRIP[1] / 2), (0, ys - 4.5, zc + GRIP[1] / 2))
    rvs = [Part.makeSphere(RIVET / 2, V(sx * 8, ys, z)) for sx in (-1, 1)
           for z in range(int(zr + 10), int(zf + 10), 20) if abs(z - zc) > GRIP[1] / 2 + 6]
    h["arch"] = {"Strap": (compound(legs + [strap]), "iron"), "Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                 "Rivets": (compound(rvs), "brass")}
    # 3. triangle, apex down on the eye band, the top bar is the grip
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
    # 4. tiller off the drum's left side, behind the cap
    xt, zb, zt = CASE[0] + 40, -270.0, BACK - 60
    arm = rod(22, (CASE[0] - 4, 20, zb), (xt, 20, zb)).fuse(rod(22, (xt, 20, zb), (xt, 20, zt)))
    foot = box(CASE[0] - 6, CASE[0] + 6, 0, 40, zb - 20, zb + 20)
    g, rg = leather_grip((xt, 20 - 12, zt), (xt, 20 - 12 - GRIP[1], zt))
    lever = box(xt - 4, xt + 4, -20, -2, zt + 14, zt + 30)
    h["tiller"] = {"Arm": (arm, "iron"), "Foot": (foot, "brass"), "Grip": (g, "leather"), "Grip_rings": (rg, "copper"),
                   "Knob": (Part.makeSphere(19, V(xt, 20 - 12 - GRIP[1] - 10, zt)), "brass"),
                   "Trigger_lever": (lever, "brass")}
    return h


HANDLES = handles(BUILT["A16"])
p16, s16 = BUILT["A16"], SKINS["A16"]
others = compound([p16[n][0] for n in ("Eye_band", "Rails", "Sling_eyes", "Rear_casing", "Supply_hose")] +
                  [s16[n][0] for n in ("Hoops", "Warp_vial", "Vial_clamps", "Casing_extension", "End_cap", "Spikes",
                                       "Claw_plate", "Warp_gauge", "Flex_collar")])
for hn, parts in HANDLES.items():
    for n, (shape, style) in parts.items():
        nm = "A16_h_%s_%s" % (hn, n)
        SKIN_NAMES.add(nm)
        sc.add("A16_h_" + hn, nm, to_view(shape), style)
    g = parts["Grip"][0]
    c = clear(g, others)
    check(c >= 30.0, "handle %s: grip Ø%.0f x %.0f, %.0f mm from the nearest part for the fingers"
          % (hn, GRIP[0], GRIP[1], c))
    print("      handle %s: top at y %.0f (the pack's top rails at %.0f), %.0f g if printed solid in PLA"
          % (hn, max(sh.BoundBox.YMax for sh, _ in parts.values()), A_RAIL_R * 0.72,
             sum(sh.Volume for sh, _ in parts.values()) / 1000 * 1.27))


# ---------------------------------------------------------------- rear grip variants (A16), with the trigger
def rear_grips(p):
    """Four layouts of the control grip with the trigger for A16, each in its own group.

    The concept's grip leans 20 deg back from (0, -75, -200), so its top and its trigger sit under the drum;
    "down" keeps that axis and starts where it leaves the drum.

    butt:   an old pistol's butt out of the cap's lower half (the miniature): 25 then 50 deg down, a brass
            pommel with a spike, the trigger under its root in a guard
    spades: two upright grips behind the cap on a cross bar, a butterfly trigger between them (Maxim)
    down:   a straight grip under the drum inside a riveted D-bow (a knuckle guard), a spike on the bow
    side:   a grip along the drum's upper left flank on two brackets, a thumb lever on its front end
    """
    d = V(0, -math.sin(math.radians(70)), -math.cos(math.radians(70)))
    n = V(0, -d.z, d.y) * -1                               # across the grip, forward
    t0 = (CASE[0] - A_RAIL_R * 0.72) / -d.y
    o = V(0, -A_RAIL_R * 0.72, -200) + d * t0               # where the concept's grip leaves the drum

    def P(t, u):
        q = o + d * t + n * u
        return (q.x, q.y, q.z)

    def chain(dia, *pts):
        return G.fuse_all([rod(dia, a, b) for a, b in zip(pts, pts[1:])] +
                          [Part.makeSphere(dia / 2, V(*q)) for q in pts[1:-1]])

    def ray(p0, deg, length):
        return (p0[0], p0[1] - length * math.sin(math.radians(deg)), p0[2] - length * math.cos(math.radians(deg)))

    g = {}
    # butt, out of the cap
    r0 = (0.0, -55.0, BACK - 10)
    r1 = ray(r0, 25, 75)
    r2 = ray(r1, 50, 62)
    y_g = -124.0                                           # the guard's bottom bar
    g["butt"] = {"Flange": (rod(50, (0, -55, BACK - 1), (0, -55, BACK - 17)), "brass"),
                 "Grip": (chain(GRIP[0], r0, r1, r2), "wood"),
                 "Grip_rings": (compound([Part.makeTorus(GRIP[0] / 2, 1.6, V(*ray(r0, 25, t)), V(0, -0.42, -0.91))
                                          for t in (22, 66)]), "copper"),
                 "Pommel": (Part.makeSphere(23, V(*ray(r2, 50, 10))).fuse(rod(40, ray(r1, 50, 50), ray(r1, 50, 58))),
                            "brass"),
                 "Pommel_spike": (cone_from(ray(r2, 50, 26), ray(r2, 30, 56), 14), "iron_dark"),
                 "Trigger": (chain(7, (0, -66, BACK - 22), (0, -86, BACK - 26), (0, -100, BACK - 22)), "brass"),
                 "Guard": (chain(6, (0, -72, BACK - 5), (0, y_g, BACK - 8), (0, y_g, BACK - 50),
                                 (0, -92, BACK - 52)), "iron")}
    # spades behind the cap
    zb, yb, xs = BACK - 50, -60.0, 95.0
    arms = [rod(16, (sx * 60, yb, BACK - 5), (sx * 60, yb, zb)) for sx in (-1, 1)]
    bar = rod(20, (-xs, yb, zb), (xs, yb, zb))
    grips, rings, knobs = [], [], []
    for sx in (-1, 1):
        gg, rr = leather_grip((sx * xs, yb + 58, zb), (sx * xs, yb + 58 - GRIP[1], zb))
        grips.append(gg)
        rings.append(rr)
        knobs += [Part.makeSphere(18, V(sx * xs, yb + 66, zb)), Part.makeSphere(18, V(sx * xs, yb + 50 - GRIP[1], zb))]
    g["spades"] = {"Arms": (compound(arms + [bar]), "iron"), "Grip": (compound(grips), "wood"),
                   "Grip_rings": (compound(rings), "copper"), "Knobs": (compound(knobs), "brass"),
                   "Trigger": (box(-26, 26, yb + 8, yb + 40, zb + 6, zb + 12).fuse(rod(8, (0, yb + 8, zb + 9),
                                                                                     (0, yb, zb + 9))), "brass")}
    # down, in a D-bow
    flange = rod(46, P(-6, 0), P(8, 0))
    gr2, rg2 = leather_grip(P(8, 0), P(8 + GRIP[1], 0))
    bow = chain(12, P(-26, 64), P(129, 64), P(129, 0)).fuse(rod(40, P(8 + GRIP[1], 0), P(8 + GRIP[1] + 12, 0)))
    g["down"] = {"Flange": (flange, "brass"), "Grip": (gr2, "wood"), "Grip_rings": (rg2, "copper"),
                 "Bow": (bow, "iron"), "Bow_spike": (cone_from(P(70, 68), P(70, 112), 16), "iron_dark"),
                 "Rivets": (compound([Part.makeSphere(RIVET / 2, V(*P(t, 70))) for t in (0, 40, 100)]), "brass"),
                 "Trigger": (chain(8, P(16, 18), P(30, 26), P(46, 24)), "brass")}
    # side, upper left flank; the brackets leave the drum below the claw triangle
    xg, yg, zg0 = CASE[0] + 40, 40.0, -280.0
    zg1 = zg0 + GRIP[1]
    gr4, rg4 = leather_grip((xg, yg, zg0), (xg, yg, zg1))
    brackets = [rod(14, polar(CASE[0] - 2, 5) + (z,), (xg, yg, z)) for z in (zg0 - 10, zg1 + 10)]
    g["side"] = {"Grip": (gr4, "wood"), "Grip_rings": (rg4, "copper"), "Brackets": (compound(brackets), "iron"),
                 "Knobs": (compound([Part.makeSphere(15, V(xg, yg, z)) for z in (zg0 - 18, zg1 + 18)]), "brass"),
                 "Trigger": (box(xg - 5, xg + 5, yg + 14, yg + 30, zg1 - 22, zg1 - 8)
                             .fuse(rod(6, (xg - 9, yg + 18, zg1 - 8), (xg + 9, yg + 18, zg1 - 8))), "brass")}
    return g, o, d, n


GRIPS, G_O, G_D, G_N = rear_grips(BUILT["A16"])
P_GRIP = lambda t: tuple(G_O + G_D * t)
drum = cyl(2 * CASE[0], BACK, CASE[2])
for gn, parts in GRIPS.items():
    for n, (shape, style) in parts.items():
        nm = "A16_g_%s_%s" % (gn, n)
        SKIN_NAMES.add(nm)
        sc.add("A16_g_" + gn, nm, to_view(shape), style)
    trig = parts["Trigger"][0]
    inside = parts["Grip"][0].common(drum).Volume + trig.common(drum).Volume
    if gn == "spades":                             # the fingers between the grips' axis and the cap
        room = min(clear(rod(1, (sx * 95, -20, BACK - 50), (sx * 95, -100, BACK - 50)), s16["End_cap"][0])
                   for sx in (-1, 1)) - GRIP[0] / 2
    elif gn == "butt":                             # the grip's underside to the guard's bottom bar
        room = clear(parts["Grip"][0], box(-3, 3, -127, -121, BACK - 48, BACK - 10))
    elif gn == "down":                             # from the grip to the bow's bar along it, at mid-grip
        room = clear(rod(1, P_GRIP(60), tuple(G_O + G_D * 60 + G_N * 57)), parts["Bow"][0]) + 57 - GRIP[0] / 2
    else:                                          # the fingers under the grip: drum, claw plate, supply hose
        room = clear(parts["Grip"][0], compound([drum, s16["Claw_plate"][0], s16["Warp_gauge"][0],
                                                 p16["Supply_hose"][0]]))
    check(inside < 1.0 and room >= 20.0, "rear grip %s: grip and trigger outside the drum (%.0f mm3 in), %.0f mm"
          " for the fingers" % (gn, inside, room))
print("      note: the concept's rear grip leaves the drum %.0f mm down its axis, and its trigger (y %.0f to %.0f) is"
      " under the drum (R %.0f): the grips here start at (y %.0f, z %.0f)"
      % ((G_O - V(0, -A_RAIL_R * 0.72, -200)).Length, p16["Trigger"][0].BoundBox.YMin, p16["Trigger"][0].BoundBox.YMax,
         CASE[0], G_O.y, G_O.z))

# crank: the concept draws its arm inside the casing, the knob through its wall
p16 = BUILT["A16"]
k = p16["Crank_knob"][0].BoundBox
r_arm = max(math.hypot(v.X, v.Y) for v in p16["Crank_arm"][0].Vertexes)
print("      note: the concept's crank arm reaches R %.0f inside the casing (R %.0f), its knob goes through the"
      " wall (x %.0f to %.0f): the casing needs a slot there, or the crank outside it" % (r_arm, CASE[0], k.XMax, k.XMin))

sc.finish()
if App.GuiUp:
    for o in doc.Objects:
        for tag in ("A16", "A19"):
            st = RESTYLE.get(o.Name[len(tag) + 1:]) if o.Name.startswith(tag + "_") else None
            if st:
                o.ViewObject.ShapeColor, o.ViewObject.Transparency = FV.STYLES[st]
            elif o.Name.startswith(tag + "_") and hasattr(o.ViewObject, "ShapeColor") \
                    and o.Name not in SKIN_NAMES:
                o.ViewObject.ShapeColor, o.ViewObject.Transparency = FV.STYLES["bronze"]

# ---------------------------------------------------------------- pictures, as in concepts_renders.py
SHOT = App.Placement(App.Matrix(0, 0, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1))
for o in doc.Objects:
    if o.Name in sc.src:
        sh = sc.src[o.Name].copy()
        sh.Placement = SHOT.multiply(sh.Placement)
        o.Shape = sh
doc.recompute()
VIEWS = {"rear": (0.62, 0.62, -0.48), "front": (-0.62, -0.62, -0.42),
         "side": (0.0, 1.0, 0.0), "left": (0.0, -1.0, 0.0), "low": (-0.55, 0.75, 0.30)}


def camera(direction):
    d = App.Vector(*direction).normalize()
    zc_ = d.negative()
    up = App.Vector(0, 0, 1)
    if abs(zc_.dot(up)) > 0.99:
        up = App.Vector(0, 1, 0)
    xc = up.cross(zc_).normalize()
    yc = zc_.cross(xc)
    return App.Rotation(App.Matrix(xc.x, yc.x, zc_.x, 0, xc.y, yc.y, zc_.y, 0, xc.z, yc.z, zc_.z, 0, 0, 0, 0, 1))


def snap(file, view, width=1300):
    v = Gui.getDocument(doc.Name).activeView()
    v.setCameraType("Orthographic")
    v.setCameraOrientation(camera(view))
    Gui.updateGui()
    v.fitAll()
    Gui.updateGui()
    tmp = os.path.join(OUT, "_tmp.png")
    v.saveImage(tmp, 2000, 1500, "White")
    im = Image.open(tmp).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    bb = (max(bb[0] - 24, 0), max(bb[1] - 24, 0), min(bb[2] + 24, im.width), min(bb[3] + 24, im.height))
    c = im.crop(bb)
    if c.width > width:
        c = c.resize((width, int(c.height * width / c.width)), Image.LANCZOS)
    c.save(os.path.join(OUT, file + ".jpg"), quality=88)
    os.remove(tmp)


if App.GuiUp:
    for tag, group, _, _ in VARIANTS[:2]:
        sc.show_only([group, tag + "_skin"])
        for vn in VIEWS:
            snap("%s_%s" % (tag, vn), VIEWS[vn])
    sc.show_only(["A_Montigny_16", "A16_skin", "A_Montigny_19", "A19_skin"])
    snap("both_front", VIEWS["front"], 1800)
    sheet = []
    for i, hn in enumerate(HANDLES):
        keep = ["A16_Carry_handle", "A16_Carry_posts"] if hn == "tiller" else []
        sc.show_only(["A_Montigny_16", "A16_skin", "A16_h_" + hn],
                     hide=[n for n in ("A16_Carry_handle", "A16_Carry_posts") if n not in keep])
        for vn in ("front", "side", "rear"):
            snap("A16_handle%d_%s_%s" % (i + 1, hn, vn), VIEWS[vn])
        sheet.append(os.path.join(OUT, "A16_handle%d_%s_side.jpg" % (i + 1, hn)))
    # the four side views on one sheet, numbered
    from PIL import ImageDraw
    ims = [Image.open(f) for f in sheet]
    w, hh = max(i.width for i in ims), max(i.height for i in ims)
    out = Image.new("RGB", (2 * w, 2 * hh), "white")
    for i, im in enumerate(ims):
        x, y = (i % 2) * w, (i // 2) * hh
        out.paste(im, (x, y))
        ImageDraw.Draw(out).text((x + 20, y + 14), "%d" % (i + 1), fill=(0, 0, 0))
    out.save(os.path.join(OUT, "A16_handles_side.jpg"), quality=88)
    # rear grips: the rear block alone, close
    front = ["A16_" + n for n in ("Modules_barrel", "Modules_chamber", "Modules_printed", "Modules_steel",
                                  "Muzzle_sleeves", "Sleeve_band", "Front_plate", "Rails", "Eye_band", "Sling_eyes",
                                  "Tripod_pad", "Carry_handle", "Carry_posts", "Sleeve_bands", "Muzzle_spike", "Spike_lug",
                                  "Hoops", "Rivets")]
    concept_grip = ["A16_Rear_grip", "A16_Trigger", "A16_Trigger_rod"]
    sheet = []
    for i, gn in enumerate(GRIPS):
        sc.show_only(["A_Montigny_16", "A16_skin", "A16_g_" + gn], hide=front + concept_grip)
        for vn, dv in (("close", (0.50, 0.72, -0.10)), ("closeside", (0.0, 1.0, 0.0)), ("closeback", (0.85, -0.35, -0.2))):
            snap("A16_grip%d_%s_%s" % (i + 1, gn, vn), dv, 1000)
        sheet.append(os.path.join(OUT, "A16_grip%d_%s_%s.jpg" % (i + 1, gn, "closeback" if gn == "side" else "close")))
    ims = [Image.open(f) for f in sheet]
    w, hh = max(i.width for i in ims), max(i.height for i in ims)
    out = Image.new("RGB", (2 * w, 2 * hh), "white")
    for i, im in enumerate(ims):
        x, y = (i % 2) * w, (i // 2) * hh
        out.paste(im, (x, y))
        ImageDraw.Draw(out).text((x + 20, y + 14), "%d" % (i + 1), fill=(0, 0, 0))
    out.save(os.path.join(OUT, "A16_grips.jpg"), quality=88)
    print("renders written to", OUT)
