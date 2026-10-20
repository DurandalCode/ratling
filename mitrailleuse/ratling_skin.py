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
- brass ribs on the supply hose, as a corrugated hose.

Prints [OK ] / [FAIL] for the clearances it relies on. Writes exports/ratling_skin/<tag>_<view>.jpg.

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
    # casing: straps at its ends, a seam on top, spikes on the rear rim at the top
    straps = [tube(2 * CASE[0] + 8, 4, z, z + 12) for z in (CASE[1] + 2, CASE[2] - 14)]
    for z in (CASE[1] + 8, CASE[2] - 8):
        rv.append(rivets_round(CASE[0] + 4, z, 12.0))
    for i in range(14):
        z = CASE[1] + 20 + i * 11.5
        rv.append(compound([Part.makeSphere(RIVET / 2, V(*polar(CASE[0], a), z)) for a in (78, 102)]))
    s["Casing_straps"] = (compound(straps), "copper")
    s["Rivets"] = (compound(rv), "brass")
    spikes = []
    for a in (55, 75, 90, 105, 125):
        x, y = polar(CASE[0] + 2, a)
        tx, ty = polar(CASE[0] + 30, a)
        spikes.append(cone_from((x, y, CASE[1] + 6), (tx, ty, CASE[1] - 34), 16))
    # under the muzzles: a lug from the sleeve band and a forged spike
    y_s = -(_ns["shroud_r"](LAYOUT[key]) + 2.0 + 9.0)
    lug = box(-7, 7, y_s, y_s + 12, Z_TIP - 34, Z_TIP - 22)
    spikes.append(cone_from((0, y_s + 3, Z_TIP - 40), (0, y_s + 3, Z_TIP + 40), 18))
    s["Spikes"] = (compound(spikes), "iron_dark")
    s["Spike_lug"] = (lug, "iron")
    # the claw triangle and the warp gauge, gunner's left (+x), and a vial along the top
    s["Claw_plate"] = (claw_triangle(CASE[0], -135.0, 40.0), "brass")
    zg, ag = -80.0, 0.0
    gauge = radial(40, CASE[0] - 2, CASE[0] + 10, ag, zg)
    s["Warp_gauge"] = (gauge, "brass")
    s["Warp_lens"] = (radial(30, CASE[0] + 10, CASE[0] + 13, ag, zg), "warp")
    yv = CASE[0] + 16
    s["Warp_vial"] = (cyl(22, -200, -80, 0, yv).fuse(Part.makeSphere(11, V(0, yv, -80)))
                      .fuse(Part.makeSphere(11, V(0, yv, -200))), "warp")
    clamps = [tube(30, 4, z, z + 10, 0, yv).fuse(box(-5, 5, CASE[0] - 2, yv - 12, z, z + 10)) for z in (-185, -105)]
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
                   ("Spikes", "Crank_knob"), ("Claw_plate", "Supply_hose"), ("Warp_gauge", "Supply_hose"),
                   ("Rivets", "Carry_posts"), ("Rivets", "Tripod_pad")):
        c = clear(s[dn][0], p[pn][0])
        check(c >= 2.0, "%s: %s clear of %s by %.1f mm" % (tag, dn.lower(), pn, c))
    reach = max(s[n][0].BoundBox.ZMax for n in s)
    print("      %s: decor reaches z %.0f (sleeve tips %.0f), %.0f g if printed solid in PLA"
          % (tag, reach, Z_TIP, sum(sh.Volume for sh, _ in s.values()) / 1000 * 1.27))
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
    print("renders written to", OUT)
