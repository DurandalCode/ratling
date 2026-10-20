# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: the pack's frame, two printed plates on four aluminium rails (FreeCAD 1.0).

The first real part of concept A (mitrailleuse_concepts.py draws it as masses). It holds the v4.4 modules
(module/stage3v4_coaxial_chamber.py, built here as a library and placed in the pack) at 16 (rings 4 + 12,
layout J) and at 19 (hex, layout G). The rails are the same for both; only the two plates change.
Frame as in mitrailleuse_concepts.py: z along the barrels (+z to the muzzle), y up, x to the gunner's left.

    rear plate .. round the modules' rear plugs. Its rear face is the rear plug's back face, so the rear
                  yoke's ears (outside the Ø38 tube) land on it: a module cannot move forward.
    front plate . round the front plugs' flanges. Its front face is the front plug's flange, so the front
                  yoke's ears land on it: a module cannot move back.
                  The plates are stops beside the module's own stack (nut - yoke - plug), never in it: the
                  yoke still sits on its plug, the rods and nuts are the module's, nothing changes in v4.4.
                  Per module a Ø38 + 2 HOLE_CLEAR hole with a notch at each rod (the rod is 0.5 mm off the
                  tube's hole, so the two are one cut), turned as the pack turns its rods (docs/pack.md). A
                  lug round each rail.
    rails ....... 4 aluminium tubes 12 x 1 at RAIL_R, 45 deg off the axes, from the head plate's
                  back face (RAIL_Z0, rear_frame.py) to the front plate's face. Clear of every yoke ear, nut and fitting at 16 and 19.
    set screws .. one M3 x 8 grub screw per lug, radial onto the rail through a nut dropped into a pocket on
                  the plate's top face: the plates slide on the rails until they are set.

Assembly: plates loose on the rails. Each module's core (plugs, tube, seat ring, barrel) goes in from the
front, through the front plate and the rear plate, until the rear plug's back face is level with the rear
plate's. Then the module is finished in place as in its own docstring: rear yoke over the fitting, front
yoke over the front plug's sleeve, muzzle ring, rods from the front through the yokes, both plates and the
ring, nuts. Last, push the plates out onto the yokes and set the grub screws. Cut all chamber tubes to one
length in one stop: their spread is the play a module has between the plates.

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/pack_frame.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/pack_frame/ (STEP, STL in print orientation,
FCStd).
"""

import importlib
import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
try:
    PACK_FRAME_LIBRARY
except NameError:
    PACK_FRAME_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

_ns = {"__file__": os.path.join(REPO, "mitrailleuse", "pack_layouts.py")}
exec(open(_ns["__file__"], encoding="utf-8").read().rsplit("\nmain()", 1)[0], _ns)
LAYOUT = {k: pts for k, _, _, pts, _ in _ns["LAYOUTS"]}
# the module, parts only (no report, no export)
M = {"REPO": REPO, "STAGE3V4_LIBRARY": True}
exec(open(os.path.join(REPO, "module", "stage3v4_coaxial_chamber.py"), encoding="utf-8").read(), M)

NAME = "pack_frame"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector
X, Z = V(1, 0, 0), V(0, 0, 1)
cyl = G.cyl

# ---------------------------------------------------------------- parameters
KEYS = (("A16", "j_rings_4_12"), ("A19", "g_hex_19"))
TURNS = {"j_rings_4_12": ((4, 0.0), (12, 40.0))}    # rods per ring, off the module's radius (docs/pack.md)
PLATE_T = 10.0
HOLE_CLEAR = 0.3            # per side round the Ø38 tube and plugs
ROD_HOLE = 3.6              # notch round the M3 rod
RIM = 2.5                   # outside the outermost hole
RAIL = (12.0, 1.0)          # aluminium tube, OD x wall
RAIL_R = 104.0              # rail axes off the pack's axis, the same at 16 and 19 (J is the tighter: 4.7 mm)
RAIL_ANGLES = (45.0, 135.0, 225.0, 315.0)
RAIL_HOLE = 12.3
RAIL_Z0 = -238.0            # rear end: the head plate's back face (rear_frame.py, Z0 - HP_T)
LUG_R = 12.5                # round the rail
RAIL_CLEAR = 1.0            # rail to any module part, along its whole length
GRUB = (3.4, 8.0)           # M3 grub screw: hole, length
NUT_AF, NUT_T = 5.5, 2.4
WEB_MIN = 1.2               # thinnest web between two cuts in a plate
BED = 256.0
# rails: a side load at mid-span between the plates, shared by all four (the handle itself goes on plates of
# its own into the modules, carry_mount.py)
GUN_KG, G_LOAD = 10.0, 3.0  # the gun without the receiver (mitrailleuse_concepts.py: 9.0 kg at 19), 3 g
RAIL_YIELD = 150.0          # MPa, 6060 / АД31 T5-T6 tube, the usual hardware-store aluminium
DENSITY = {"solid": 1.27, "printed": 0.6, "alu": 2.70}   # PETG solid; concept's printed average; aluminium

z_rp, z_fs = M["z_rp"], M["z_fs"]            # rear plug's back face, front plug's flange (module frame)
TIE_R, TIE_A0 = M["TIE_R"], M["TIE_ANGLES"][0]
CH_OD = M["CH_OD"]
HOLE_D = CH_OD + 2 * HOLE_CLEAR
PLATES = {"rear": (z_rp, z_rp + PLATE_T, +1), "front": (z_fs - PLATE_T, z_fs, -1)}   # z0, z1, top face side


def polar(r, a):
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


def rod_angles(key, pts):
    """First rod's direction (deg) per module: 30 deg, or the ring's turn off the module's radius."""
    if key not in TURNS:
        return [TIE_A0] * len(pts)
    turns = [t for n, t in TURNS[key] for _ in range(n)]
    assert len(turns) == len(pts), key
    return [math.degrees(math.atan2(y, x)) + t for (x, y), t in zip(pts, turns)]


def place(shape, x, y, a):
    s = shape.copy()
    s.rotate(V(0, 0, 0), Z, a - TIE_A0)
    s.translate(V(x, y, 0))
    return s


def module_parts(key):
    """The v4.4 parts of every module in the pack, placed: [{name: shape}] in layout order."""
    pts = LAYOUT[key]
    names = ("rp", "fp", "chamber", "barrel", "sr", "rear_yoke", "front_yoke", "muzzle_ring", "hardware", "fitting")
    return [{n: place(M[n], x, y, a) for n in names} for (x, y), a in zip(pts, rod_angles(key, pts))]


def rods_xy(key):
    pts = LAYOUT[key]
    return [[(x + px, y + py) for px, py in (polar(TIE_R, a), polar(TIE_R, a + 180))]
            for (x, y), a in zip(pts, rod_angles(key, pts))]


def bottom(solid, z):
    """The face of a prism at z: plates are cut in 2D and extruded (a 3D cut of 60 holes takes minutes)."""
    return [f for f in solid.Faces if abs(f.BoundBox.ZMax - z) < 1e-6 and abs(f.BoundBox.ZMin - z) < 1e-6][0]


def disc(r, x=0.0, y=0.0, z=0.0):
    return Part.Face(Part.Wire(Part.makeCircle(r, V(x, y, z))))


def module_cut(x, y, a, z):
    """Tube hole and its two rod notches, as faces at z."""
    cut = [disc(HOLE_D / 2, x, y, z)]
    for b in (a, a + 180):
        rx, ry = polar(TIE_R, b)
        k = (HOLE_D / 2 - 1) / TIE_R
        cut.append(bottom(M["hull_prism"]([(x + rx, y + ry, ROD_HOLE / 2), (x + rx * k, y + ry * k, ROD_HOLE / 2)],
                                          z, z + 1), z))
    return cut


def plate(key, side, extra=(), extra_holes=()):
    """A plate at PLATES[side]; extra: solids added to its outline (tabs), extra_holes: faces at z0 cut through."""
    z0, z1, up = PLATES[side]
    pts = LAYOUT[key]
    r_disc = max(max(math.hypot(x, y) for x, y in pts) + HOLE_D / 2,
                 max(math.hypot(*p) for m in rods_xy(key) for p in m) + ROD_HOLE / 2) + RIM
    outline = G.fuse_all([cyl(2 * r_disc, z0, z1)] + [M["hull_prism"](                  # rail lugs, necked in
        [(*polar(RAIL_R, a), LUG_R), (*polar(r_disc - 12, a), LUG_R + 4)], z0, z1) for a in RAIL_ANGLES] + list(extra)).removeSplitter()
    face = bottom(outline, z0)
    holes = [disc(RAIL_HOLE / 2, *polar(RAIL_R, a), z=z0) for a in RAIL_ANGLES] + list(extra_holes)
    for (x, y), a in zip(pts, rod_angles(key, pts)):
        holes += module_cut(x, y, a, z0)
    s = face.cut(holes).extrude(V(0, 0, z1 - z0))
    zm = (z0 + z1) / 2
    cuts = []
    for a in RAIL_ANGLES:
        rx, ry = polar(RAIL_R, a)
        # grub screw radially onto the rail, through a nut dropped in from the top face
        cuts.append(Part.makeCylinder(GRUB[0] / 2, LUG_R + 2, V(rx, ry, zm), V(*polar(1, a), 0)))
        u0 = RAIL_HOLE / 2 + 1.2
        nut = Part.makeBox(NUT_T + 0.4, NUT_AF + 0.3, PLATE_T, V(u0, -(NUT_AF + 0.3) / 2, 0))
        z_nut = zm - (NUT_AF / math.sqrt(3) + 0.3) if up > 0 else zm + (NUT_AF / math.sqrt(3) + 0.3) - PLATE_T
        nut.translate(V(0, 0, z_nut))
        nut.rotate(V(0, 0, 0), Z, a)
        nut.translate(V(rx, ry, 0))
        cuts.append(nut)
    return s.cut(cuts).removeSplitter(), r_disc


def rails():
    return [G.cyl(RAIL[0], RAIL_Z0, z_fs, *polar(RAIL_R, a)).cut(G.cyl(RAIL[0] - 2 * RAIL[1], RAIL_Z0 - 1, z_fs + 1,
                                                                      *polar(RAIL_R, a))) for a in RAIL_ANGLES]


def webs(key):
    """Thinnest web between two cuts of a plate (tube holes, rod notches, rail holes) and to its rim."""
    pts = LAYOUT[key]
    circles = [(x, y, HOLE_D / 2, i) for i, (x, y) in enumerate(pts)]
    circles += [(x, y, ROD_HOLE / 2, i) for i, m in enumerate(rods_xy(key)) for x, y in m]
    circles += [(*polar(RAIL_R, a), RAIL_HOLE / 2, -1 - k) for k, a in enumerate(RAIL_ANGLES)]
    w = min(math.hypot(a[0] - b[0], a[1] - b[1]) - a[2] - b[2]
            for i, a in enumerate(circles) for b in circles[i + 1:] if a[3] != b[3])
    return w


# ---------------------------------------------------------------- build
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
built = {}
rail_parts = rails()
for tag, key in KEYS:
    mods = module_parts(key)
    plates = {side: plate(key, side) for side in PLATES}
    built[tag] = (key, mods, plates)

# ---------------------------------------------------------------- checks
rail_area = math.pi / 4 * (RAIL[0] ** 2 - (RAIL[0] - 2 * RAIL[1]) ** 2)
rail_w = math.pi / 32 * (RAIL[0] ** 4 - (RAIL[0] - 2 * RAIL[1]) ** 4) / RAIL[0]
span = (z_fs - PLATE_T) - (z_rp + PLATE_T)
f_load = GUN_KG * 9.81 * G_LOAD
sigma4 = (f_load / 4) * span / 4 / rail_w        # shared by all four rails, load at mid-span
lines = []
for tag, (key, mods, plates) in built.items():
    n = len(mods)
    for side, (s, r_disc) in plates.items():
        bb = s.BoundBox
        check(G.single_solid(s) and len(s.Faces) > 100 and s.common(G.fuse_all(rail_parts)).Volume < 1e-3
              and all(s.isInside(V(*polar(RAIL_R, a), 0) + V(*polar(RAIL_HOLE / 2 + 1, a + sx * 90), sum(PLATES[side][:2]) / 2),
                               1e-3, True) for a in RAIL_ANGLES for sx in (-1, 1)), "%s %s plate one solid, round every rail" % (tag, side))
        check(max(bb.XLength, bb.YLength) <= BED - 4, "%s %s plate %.0f x %.0f x %.0f fits the %.0f bed"
              % (tag, side, bb.XLength, bb.YLength, bb.ZLength, BED))
        near = ("rp", "chamber", "hardware", "rear_yoke") if side == "rear" else ("fp", "chamber", "hardware",
                                                                                   "front_yoke")
        sample = mods[:2] + mods[len(mods) // 2:len(mods) // 2 + 1] + mods[-2:]      # a 3D cut per module is slow
        worst = max(s.common(m[p]).Volume for m in sample for p in near)
        check(worst < 1e-2, "%s %s plate clear of the modules' plugs, tubes, rods and yokes (worst %.3f mm3)"
              % (tag, side, worst))
        # the yoke's ears land on the plate's face: contact area per module
        yoke = "rear_yoke" if side == "rear" else "front_yoke"
        dz = 0.05 if side == "rear" else -0.05          # the yoke pushed into the plate by dz: area = volume / dz
        land = min(s.common(m[yoke].translated(V(0, 0, dz))).Volume / abs(dz) for m in sample)
        check(land >= 20.0, "%s %s plate: each %s lands on it over %.0f mm2" % (tag, side, yoke.replace("_", " "),
                                                                                 land))
        lines.append("  %s %s plate: Ø%.0f + 4 rail lugs, %.0f mm, %.0f cm3 (%.0f-%.0f g)"
                     % (tag, side, 2 * r_disc, PLATE_T, s.Volume / 1000, s.Volume / 1000 * DENSITY["printed"],
                        s.Volume / 1000 * DENSITY["solid"]))
    w = webs(key)
    check(w >= WEB_MIN, "%s plates: thinnest web %.1f mm between cuts (>= %.1f)" % (tag, w, WEB_MIN))
    # rails clear of every module part along their whole length
    d_rail = 1e9
    for r in rail_parts:
        c = r.BoundBox.Center
        for (x, y), m in zip(LAYOUT[key], mods):
            if math.hypot(c.x - x, c.y - y) > 60:
                continue
            for p in ("rp", "fp", "chamber", "rear_yoke", "front_yoke", "muzzle_ring", "hardware", "fitting"):
                d_rail = min(d_rail, r.distToShape(m[p])[0])
    check(d_rail >= RAIL_CLEAR, "%s: rails %.1f mm clear of every yoke ear, nut, plug and fitting" % (tag, d_rail))
    lines.append("  %s: %d modules, play between plates = spread of the chamber tubes' length" % (tag, n))
check(sigma4 <= RAIL_YIELD / 2, "rails 12 x 1 over %.0f mm, %.0f kg at %.0f g at mid-span, shared by all four:"
      " %.0f MPa (<= half of %.0f)" % (span, GUN_KG, G_LOAD, sigma4, RAIL_YIELD))
rail_len = z_fs - RAIL_Z0
report = [
    "Mitrailleuse concept A: pack frame (two plates on four rails), v4.4 modules",
    "  rear plate z %.1f..%.1f (rear yoke's ears on its back), front plate z %.1f..%.1f (front yoke's ears on its"
    " face), %.1f apart" % (z_rp, z_rp + PLATE_T, z_fs - PLATE_T, z_fs, z_fs - z_rp),
    "  rails: 4 x alu tube %g x %g on R %.0f at %s deg, z %.0f..%.1f, %.0f mm each (%.0f g the set)"
    % (RAIL + (RAIL_R, "/".join("%.0f" % a for a in RAIL_ANGLES), RAIL_Z0, z_fs, rail_len,
               4 * rail_area * rail_len / 1000 * DENSITY["alu"])),
    "  holes Ø%.1f round the tube, rod notches Ø%.1f; set by 8 M3 x %.0f grub screws and nuts (4 a plate)"
    % (HOLE_D, ROD_HOLE, GRUB[1]),
] + lines + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
if not PACK_FRAME_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- document and exports
if not PACK_FRAME_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    dx = {"A16": -140.0, "A19": 140.0}
    FV.STYLES.setdefault("alu", ((0.80, 0.82, 0.86), 0))
    FV.STYLES.setdefault("barrel", ((0.45, 0.46, 0.50), 0))
    for tag, (key, mods, plates) in built.items():
        grp = tag
        for side, (s, _) in plates.items():
            sc.add(grp + "_frame", "%s_%s_plate" % (tag, side), s, "frame", offset=V(2 * dx[tag], 0, 0))
        sc.add(grp + "_frame", tag + "_rails", Part.makeCompound(rail_parts), "alu", offset=V(2 * dx[tag], 0, 0))
        for style, names in (("stator", ("rp", "fp", "rear_yoke", "front_yoke", "muzzle_ring", "sr")),
                             ("ghost", ("chamber",)), ("barrel", ("barrel",)), ("steel", ("hardware", "fitting"))):
            sc.add(grp + "_modules", "%s_%s" % (tag, "_".join(names)), Part.makeCompound([m[n] for m in mods for n in names]),
                   style, offset=V(2 * dx[tag], 0, 0))
    sc.finish()
    sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for tag, (key, mods, plates) in built.items():
        # contact face on the bed: the rear plate's back, the front plate's face
        write(plates["rear"][0], "%s_rear_plate" % tag.lower(), False)
        write(plates["front"][0], "%s_front_plate" % tag.lower(), True)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
