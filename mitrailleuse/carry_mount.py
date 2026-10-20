# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: carried at its centre of gravity, a handle on top, sling eyes, a tripod pad (FreeCAD 1.0).

The supports sit on two plates of their own in the pack frame (pack_frame.py), CG_SPAN apart round Z_CG, so the
load goes straight into the modules' chamber tubes (stiff, 38 x 1.5 aluminium) and from them into the frame's
rear and front plates; the rails carry none of it. Concept A (mitrailleuse_concepts.py) puts the centre of
gravity at z 86 (16) / 92 (19), with the head and the muzzle sleeves; both CG plates are set by their grub
screws, so the pair slides along the rails when the gun's balance changes.

    CG plates ... as the frame's plates (holes round the chamber tubes, rod notches, rail lugs, grub screws),
                  per pack, plus four tabs the same at 16 and 19: on top and underneath one M4 hole each for the
                  handle's and the pad's feet, at the sides a Ø SLING_HOLE eye for a sling's snap hook.
    handle ...... printed, common: a grip GRIP long between two feet. Each foot is a block with a pocket that
                  takes a top tab from above (its sides in x keep the foot from turning), an M4 x 25 across it
                  through the tab, the nut in a pocket on the foot's face. The grip stands HAND_ROOM over
                  everything under it.
    tripod pad .. printed, common: the same two feet on the bottom tabs and a flat beam between them, a 3/8"-16
                  nut (the heavy tripod head's screw) in a pocket on top of the beam, the screw from below.

Assembly: both CG plates go on the rails with the frame's plates, before the modules. Handle and pad on their
tabs once the pack is built: slide the feet on, bolts through.

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/carry_mount.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/carry_mount/ (STEP, STL in print orientation,
FCStd).
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
# the frame's parameters and functions, without its build, checks and export
PACK_FRAME_LIBRARY = True
exec(open(os.path.join(REPO, "mitrailleuse", "pack_frame.py"), encoding="utf-8").read()
     .split("\n# ---------------------------------------------------------------- build")[0])

NAME = "carry_mount"
OUT_DIR = os.path.join(REPO, "exports", NAME)
Y = V(0, 1, 0)

# ---------------------------------------------------------------- parameters
Z_CG = 90.0                 # mitrailleuse_concepts.py: 86 at 16, 92 at 19
CONCEPT_CG = {"A16": 86.0, "A19": 92.0}
CG_SPAN = 130.0             # between the two CG plates' mid-planes: a hand between the feet
TAB_W = 36.0                # top and bottom tabs, across x
TAB_TOP = 123.0             # their outer edge off the axis
BOLT_Y = 115.0              # M4 across the tab
BOLT, BOLT_NUT = 4.4, (7.0, 3.2)                   # M4: hole, nut AF x thickness
SIDE_TAB = (24.0, 120.0)    # sling tabs at the sides: width in y, outer edge off the axis
SLING_HOLE, SLING_AT = 10.0, 112.0
FOOT_WALL, CHEEK = 6.0, 6.0  # round the tab in x, in z either side of it
POCKET_CLEAR = 0.2
FOOT_Y0 = 109.0             # foot's lower face off the axis (the tab's root is lower)
GRIP = (28.0, 30.0)         # across x, in y
GRIP_R = 8.0                # its edges along z
HAND_ROOM = 32.0            # grip's underside over anything under it
HAND_LEN = 100.0            # grip's clear length between the feet
PAD_T = 20.0                # tripod beam, in y
TRIPOD_NUT = (14.6, 8.6, 9.9)                      # 3/8"-16 nut: AF + clearance, depth, screw hole
GAP_MIN = 2.0               # handle and pad to modules and rails
TAB_STRESS_MAX = 10.0       # MPa, PETG bearing under the bolt at G_LOAD

zc = {"rear": Z_CG - CG_SPAN / 2, "front": Z_CG + CG_SPAN / 2}
PLATES.update({"cg_" + k: (z - PLATE_T / 2, z + PLATE_T / 2, +1) for k, z in zc.items()})


def tabs(z0, z1, r_disc):
    """Top and bottom tabs (bolt holes) and the side sling tabs (eyes): solids at z0..z1 and holes at z0."""
    solids = [box_xy(-TAB_W / 2, TAB_W / 2, sy * (r_disc - 10), sy * TAB_TOP, z0, z1) for sy in (1, -1)]
    solids += [box_xy(sx * (r_disc - 10), sx * SIDE_TAB[1], -SIDE_TAB[0] / 2, SIDE_TAB[0] / 2, z0, z1)
               for sx in (1, -1)]
    holes = [disc(BOLT / 2, 0, sy * BOLT_Y, z0) for sy in (1, -1)]
    holes += [disc(SLING_HOLE / 2, sx * SLING_AT, 0, z0) for sx in (1, -1)]
    return solids, holes


def box_xy(x0, x1, y0, y1, z0, z1):
    x0, x1, y0, y1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def foot(z, sy):
    """A foot on the tab at plate mid-plane z, over the top (sy = +1) or under the bottom (sy = -1)."""
    hz = PLATE_T / 2 + CHEEK
    y_out = TAB_TOP + 12.0
    b = box_xy(-TAB_W / 2 - FOOT_WALL, TAB_W / 2 + FOOT_WALL, sy * FOOT_Y0, sy * y_out, z - hz, z + hz)
    pocket = box_xy(-TAB_W / 2 - POCKET_CLEAR, TAB_W / 2 + POCKET_CLEAR, sy * (FOOT_Y0 - 1), sy * (TAB_TOP + POCKET_CLEAR),
                    z - PLATE_T / 2 - POCKET_CLEAR, z + PLATE_T / 2 + POCKET_CLEAR)
    bolt = cyl(BOLT, z - hz - 1, z + hz + 1, 0, sy * BOLT_Y)
    nut = G.hex_prism(BOLT_NUT[0] + 0.3, z + hz - BOLT_NUT[1] - 0.3, z + hz + 1, 0, sy * BOLT_Y)
    head = cyl(8.0, z - hz - 1, z - hz + 3.0, 0, sy * BOLT_Y)
    return b.cut(G.fuse_all([pocket, bolt, nut, head])), y_out


def handle():
    za, zb = zc["rear"], zc["front"]
    hz = PLATE_T / 2 + CHEEK
    fa, y_out = foot(za, 1)
    fb, _ = foot(zb, 1)
    grip = box_xy(-GRIP[0] / 2, GRIP[0] / 2, y_out, y_out + GRIP[1], za - hz, zb + hz)
    grip = grip.makeFillet(GRIP_R, [e for e in grip.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99])
    return G.fuse_all([grip, fa, fb]).removeSplitter(), y_out


def pad():
    za, zb = zc["rear"], zc["front"]
    hz = PLATE_T / 2 + CHEEK
    fa, y_out = foot(za, -1)
    fb, _ = foot(zb, -1)
    beam = box_xy(-TAB_W / 2 - FOOT_WALL, TAB_W / 2 + FOOT_WALL, -y_out, -y_out - PAD_T, za - hz, zb + hz)
    zm = (za + zb) / 2
    nut = G.hex_prism(TRIPOD_NUT[0], 0, TRIPOD_NUT[1], 0, 0)
    nut.rotate(V(0, 0, 0), X, 90)              # its axis along y, top face on the beam's top
    nut.translate(V(0, -y_out, zm))
    hole = Part.makeCylinder(TRIPOD_NUT[2] / 2, PAD_T + 2, V(0, -y_out - PAD_T - 1, zm), Y)
    # the beam's top is open between the feet: the nut drops in from above
    return G.fuse_all([beam, fa, fb]).cut(G.fuse_all([nut, hole])).removeSplitter()


# ---------------------------------------------------------------- build
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
rail_parts = rails()
grip_part, y_grip = handle()
pad_part = pad()
built = {}
for tag, key in KEYS:
    mods = module_parts(key)
    plates = {}
    for side in ("cg_rear", "cg_front"):
        z0, z1, _ = PLATES[side]
        pts = LAYOUT[key]
        r_disc = max(max(math.hypot(x, y) for x, y in pts) + HOLE_D / 2,
                     max(math.hypot(*p) for m in rods_xy(key) for p in m) + ROD_HOLE / 2) + RIM
        sol, hol = tabs(z0, z1, r_disc)
        plates[side] = plate(key, side, sol, hol)
    built[tag] = (key, mods, plates)

# ---------------------------------------------------------------- checks
lines = []
near = ("chamber", "hardware")
for tag, (key, mods, plates) in built.items():
    sample = mods[:2] + mods[len(mods) // 2:len(mods) // 2 + 1] + mods[-2:]
    for side, (s, r_disc) in plates.items():
        z0, z1, _ = PLATES[side]
        bb = s.BoundBox
        check(G.single_solid(s), "%s %s plate one solid" % (tag, side))
        check(max(bb.XLength, bb.YLength) <= BED - 4, "%s %s plate %.0f x %.0f fits the %.0f bed"
              % (tag, side, bb.XLength, bb.YLength, BED))
        worst = max(s.common(m[p]).Volume for m in sample for p in near)
        check(worst < 1e-2 and s.common(G.fuse_all(rail_parts)).Volume < 1e-3,
              "%s %s plate clear of the chamber tubes, rods and rails (worst %.3f mm3)" % (tag, side, worst))
        lines.append("  %s %s plate: z %.0f..%.0f, %.0f cm3 (%.0f-%.0f g)" % (tag, side, z0, z1, s.Volume / 1000,
                     s.Volume / 1000 * DENSITY["printed"], s.Volume / 1000 * DENSITY["solid"]))
    both = plates["cg_rear"][0].fuse(plates["cg_front"][0])
    for name, part in (("handle", grip_part), ("tripod pad", pad_part)):
        check(part.common(both).Volume < 1e-3, "%s: %s clear of the plates' tabs (pocket %.1f all round)"
              % (tag, name, POCKET_CLEAR))
        d = min(part.distToShape(m[p])[0] for m in mods for p in ("chamber", "hardware", "fp", "rp")
                if abs(m["chamber"].BoundBox.Center.x) < 60)
        d = min([d] + [part.distToShape(r)[0] for r in rail_parts])
        check(d >= GAP_MIN, "%s: %s %.1f mm clear of the modules and rails" % (tag, name, d))
    # room for the hand: under the grip, between the feet
    hz = PLATE_T / 2 + CHEEK
    z_a, z_b = zc["rear"] + hz, zc["front"] - hz
    probe = box_xy(-GRIP[0] / 2, GRIP[0] / 2, 0, y_grip, z_a, z_b)
    top = max([m[p].common(probe).BoundBox.YMax for m in mods for p in ("chamber", "hardware")
               if m[p].common(probe).Volume > 1e-3] + [0.0])
    check(y_grip - top >= HAND_ROOM and z_b - z_a >= HAND_LEN,
          "%s: hand room under the grip %.0f mm (>= %.0f), %.0f mm long (>= %.0f)"
          % (tag, y_grip - top, HAND_ROOM, z_b - z_a, HAND_LEN))
    check(zc["rear"] < CONCEPT_CG[tag] < zc["front"] and abs(CONCEPT_CG[tag] - Z_CG) <= 10.0,
          "%s: centre of gravity z %.0f between the CG plates (z %.0f / %.0f), %.0f off the handle's middle"
          % (tag, CONCEPT_CG[tag], zc["rear"], zc["front"], abs(CONCEPT_CG[tag] - Z_CG)))
    # carried at G_LOAD: shared by the chamber tubes, two loads on each between the frame's plates
    n = len(mods)
    f_tube = GUN_KG * 9.81 * G_LOAD / n
    L = z_fs - z_rp
    a = min(zc["rear"] - z_rp, z_fs - zc["front"])
    w_tube = math.pi / 32 * (CH_OD ** 4 - (CH_OD - 2 * M["CH_WALL"]) ** 4) / CH_OD
    lines.append("  %s: carried at %.0f g, %.1f N a chamber tube, %.1f MPa in it (%.0f mm span)"
                 % (tag, G_LOAD, f_tube, f_tube / 2 * a / w_tube, L))
for name, part in (("handle", grip_part), ("tripod pad", pad_part)):
    bb = part.BoundBox
    check(G.single_solid(part) and max(bb.XLength, bb.YLength, bb.ZLength) <= BED - 4,
          "%s one solid, %.0f x %.0f x %.0f" % (name, bb.XLength, bb.YLength, bb.ZLength))
f_bolt = GUN_KG * 9.81 * G_LOAD / 2
bearing = f_bolt / (BOLT * PLATE_T)
edge = TAB_TOP - BOLT_Y - BOLT / 2
check(bearing <= TAB_STRESS_MAX and f_bolt / (2 * edge * PLATE_T) <= TAB_STRESS_MAX / 2,
      "tabs: %.0f kg at %.0f g on two M4: %.0f N each, %.1f MPa bearing, %.1f MPa tear-out over %.1f mm"
      % (GUN_KG, G_LOAD, f_bolt, bearing, f_bolt / (2 * edge * PLATE_T), edge))

report = [
    "Mitrailleuse concept A: carried at the centre of gravity (handle, sling eyes, tripod pad)",
    "  CG plates at z %.0f and %.0f (round Z_CG %.0f), tabs: M4 at y +-%.0f, sling eyes Ø%.0f at x +-%.0f"
    % (zc["rear"], zc["front"], Z_CG, BOLT_Y, SLING_HOLE, SLING_AT),
    "  handle: grip %.0f x %.0f, its underside at y %.0f; %.0f cm3 (%.0f-%.0f g)"
    % (GRIP + (y_grip, grip_part.Volume / 1000, grip_part.Volume / 1000 * DENSITY["printed"],
               grip_part.Volume / 1000 * DENSITY["solid"])),
    "  tripod pad: underside at y %.0f, 3/8\"-16 nut; %.0f cm3 (%.0f-%.0f g)"
    % (pad_part.BoundBox.YMin, pad_part.Volume / 1000, pad_part.Volume / 1000 * DENSITY["printed"],
       pad_part.Volume / 1000 * DENSITY["solid"]),
    "  bought: 4 x M4 x 25 + nuts, a 3/8\"-16 nut, a sling with two snap hooks",
] + lines + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- document and exports
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
FV.STYLES.setdefault("alu", ((0.80, 0.82, 0.86), 0))
FV.STYLES.setdefault("barrel", ((0.45, 0.46, 0.50), 0))
dx = {"A16": -140.0, "A19": 140.0}
for tag, (key, mods, plates) in built.items():
    off = V(2 * dx[tag], 0, 0)
    for side, (s, _) in plates.items():
        sc.add(tag + "_carry", "%s_%s_plate" % (tag, side), s, "rotor", offset=off)
    sc.add(tag + "_carry", tag + "_handle", grip_part, "printed", offset=off)
    sc.add(tag + "_carry", tag + "_tripod_pad", pad_part, "printed", offset=off)
    sc.add(tag + "_frame", tag + "_rails", Part.makeCompound(rail_parts), "alu", offset=off)
    for side in ("rear", "front"):
        sc.add(tag + "_frame", "%s_%s_plate" % (tag, side), plate(key, side)[0], "frame", offset=off)
    for style, names in (("stator", ("rp", "fp", "rear_yoke", "front_yoke", "muzzle_ring")), ("ghost", ("chamber",)),
                         ("barrel", ("barrel",)), ("steel", ("hardware", "fitting"))):
        sc.add(tag + "_modules", "%s_%s" % (tag, "_".join(names)), Part.makeCompound([m[n] for m in mods for n in names]),
               style, offset=off)
sc.finish()
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write(shape, name, rot=None):
    s = shape.copy()
    if rot is not None:
        s.rotate(V(0, 0, 0), *rot)
    s.translate(V(-s.BoundBox.Center.x, -s.BoundBox.Center.y, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
        os.path.join(OUT_DIR, name + ".stl"))


for tag, (key, mods, plates) in built.items():
    write(plates["cg_rear"][0], "%s_cg_plate" % tag.lower())          # print two
write(grip_part, "handle", (Y, 90))                                       # on its side: the pockets' roofs are short bridges
write(pad_part, "tripod_pad", (Y, 90))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
