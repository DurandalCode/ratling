# -*- coding: utf-8 -*-
"""
Ratling Stage 1 test article: static rotor/stator interface.

Two strips that carry the real selector geometry from the centre to the port
track, bolted together at the working gap, no rotation:

    stator ...... centre inlet bore + the aligned port and both neighbours,
                  G1/8 tapped from the front. Two variants:
                    A  printed face (one part),
                    B  printed body + 3 mm face plate (acrylic / POM / alu),
                       one small O-ring per port between them.
    rotor ....... spigot with a radial O-ring in the centre bore, internal
                  channel to the port radius, bore for the floating shoe,
                  standoff bosses that set the gap.
    shoe ........ floating piston, radial O-ring, flat face on the stator,
                  pen-type spring behind it.

All numbers come from ratling/params.py; the frame is described there.
Stator and rotor print as modelled (+Z up: stator face and rotor back on the
bed). The shoe prints face down; its STL is flipped accordingly.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/selector/stage1_interface.py').read())
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
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.params as P
import ratling.geom as G
import ratling.fcview as V
for _m in (P, G, V):
    importlib.reload(_m)
from ratling.geom import cyl, fuse_all, port_xy

# ---------------------------------------------------------------- strip layout
STRIP_X0 = -22.0
STRIP_X1 = P.PORT_R + 22.0
STRIP_W = 50.0
STRIP_CORNER_R = 5.0
BOLT_D = 4.5                    # M4 through
BOLT_HEAD_R = 4.0               # head / nut / washer footprint
BOLTS = [(-12.0, 17.0), (-12.0, -17.0), (P.PORT_R + 14.0, 17.0), (P.PORT_R + 14.0, -17.0)]
BOSS_D = 10.0                   # rotor standoffs around the bolts

PORT_ANGLES = [0.0, P.INDEX_DEG, -P.INDEX_DEG]   # aligned port first

VARIANT_B_OFFSET = App.Vector(0, -90, 0)         # shown beside variant A, away from the crank

OUT_DIR = os.path.join(REPO, "exports", "stage1_interface")
NAME = "stage1_interface"


def strip(z0, z1):
    box = Part.makeBox(STRIP_X1 - STRIP_X0, STRIP_W, z1 - z0,
                       App.Vector(STRIP_X0, -STRIP_W / 2, z0))
    vertical = [e for e in box.Edges
                if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6]
    return box.makeFillet(STRIP_CORNER_R, vertical)


def bolt_holes(z0, z1):
    return fuse_all([cyl(BOLT_D, z0 - 1, z1 + 1, x, y) for x, y in BOLTS])


# ---------------------------------------------------------------- parts
def make_stator_printed():
    t = P.stator_t
    tools = fuse_all([G.centre_inlet_tools(0, t), G.port_tools(PORT_ANGLES, t), bolt_holes(0, t)])
    return strip(0, t).cut(tools).cut(G.port_chamfers(PORT_ANGLES)).removeSplitter()


def make_stator_plate_variant():
    t = P.stator_t
    glands = fuse_all([cyl(P.plate_gland_od, P.PLATE_T - 1, P.PLATE_T + P.plate_gland_depth,
                           *port_xy(a)) for a in PORT_ANGLES])
    tools = fuse_all([G.centre_inlet_tools(P.PLATE_T, t), G.port_tools(PORT_ANGLES, t),
                      bolt_holes(0, t), glands])
    body = strip(P.PLATE_T, t).cut(tools).removeSplitter()

    plate = strip(0, P.PLATE_T)
    holes = [cyl(P.spigot_bore_d + 1.0, -1, P.PLATE_T + 1), bolt_holes(0, P.PLATE_T)]
    holes += [cyl(P.PORT_D, -1, P.PLATE_T + 1, *port_xy(a)) for a in PORT_ANGLES]
    plate = plate.cut(fuse_all(holes)).cut(G.port_chamfers(PORT_ANGLES)).removeSplitter()
    return body, plate


def make_rotor():
    zf, zb = P.rotor_face_z, P.rotor_back_z
    bosses = [cyl(BOSS_D, zf - 0.01, 0, x, y) for x, y in BOLTS]
    rotor = fuse_all([strip(zb, zf), G.spigot()] + bosses)
    return rotor.cut(G.rotor_passages().fuse(bolt_holes(zb, 0))).removeSplitter()


stator_a = make_stator_printed()
stator_b, plate_b = make_stator_plate_variant()
rotor = make_rotor()
shoe = G.shoe()

# ---------------------------------------------------------------- checks
sx = P.PORT_R
air_path = ([(0, 0, z) for z in (P.channel_z, P.rotor_face_z, 0.0, P.SPIGOT_TIP_Z - 0.5)]
            + [(x, 0, P.channel_z) for x in (5, 20, 40, sx - 5)]
            + [(sx, 0, z) for z in (P.channel_z, P.shoe_floor_z + 0.5, -P.SHOE_LEN - 1)])
stator_path = [(0, 0, z) for z in (1, P.spigot_bore_depth + 1, P.stator_t - 1)] + \
              [(sx, 0, z) for z in (0.2, P.stator_t / 2, P.stator_t - 1)]


def bolt_clear_of_fittings():
    lim = P.fitting_corners / 2 + BOLT_HEAD_R + 1.0
    return min(math.hypot(bx - px, by - py)
               for bx, by in BOLTS for px, py in map(port_xy, PORT_ANGLES)) >= lim


no_overlap = G.no_overlap
geo_checks = [
    ("all parts valid single solids",
     all(G.single_solid(s) for s in (stator_a, stator_b, plate_b, rotor, shoe))),
    ("A: stator / rotor no interference", no_overlap(stator_a, rotor)),
    ("A: stator / shoe no interference", no_overlap(stator_a, shoe)),
    ("rotor / shoe no interference", no_overlap(rotor, shoe)),
    ("B: body / plate / rotor / shoe no interference",
     all(no_overlap(a, b) for a, b in ((stator_b, plate_b), (stator_b, rotor),
                                       (plate_b, rotor), (plate_b, shoe), (stator_b, shoe)))),
    ("shoe face on the stator face (z = 0)", abs(shoe.BoundBox.ZMax) < 1e-6),
    ("air path open through rotor",
     G.open_along(rotor, air_path) and G.open_along(shoe, [(sx, 0, -1)])),
    ("air path open through stator A", G.open_along(stator_a, stator_path)),
    ("air path open through stator B",
     G.open_along(stator_b, stator_path) and G.open_along(plate_b, [(0, 0, 1), (sx, 0, 1)])),
    ("bolt heads clear of fittings", bolt_clear_of_fittings()),
]

lines = [P.report(), "", NAME]
lines += ["  strip                  : %.0f x %.0f, stator t %.1f, rotor t %.1f"
          % (STRIP_X1 - STRIP_X0, STRIP_W, P.stator_t, P.rotor_t)]
lines += ["  volumes cm3            : stator A %.1f, body B %.1f, plate B %.1f, rotor %.1f, shoe %.2f"
          % tuple(s.Volume / 1000 for s in (stator_a, stator_b, plate_b, rotor, shoe))]
lines += ["  plate holes (x, y)     : centre Ø%.2f; ports Ø%.1f at %s; bolts Ø%.1f at %s"
          % (P.spigot_bore_d + 1.0, P.PORT_D,
             ", ".join("(%.2f, %.2f)" % port_xy(a) for a in PORT_ANGLES),
             BOLT_D, ", ".join("(%.0f, %.0f)" % b for b in BOLTS))]
lines += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in geo_checks]
report = "\n".join(lines)
print(report)

# ---------------------------------------------------------------- references
# Shown in the FreeCAD document only; not exported, not checked.
HOSE_LEN = 60.0
SHAFT_D = 10.0
SHAFT_LEN = 55.0
CRANK_Y = 90.0             # crank on the side: machine +Y = left in the view
EXPLODE = {"fittings": 70, "stator": 40, "ring_spigot": 10, "shoe": 12, "spring": -8, "rotor": -40}


def bolt(x, y):
    zb, t = P.rotor_back_z, P.stator_t
    return fuse_all([cyl(4.0, zb - 4, t + 3.2, x, y),
                     cyl(7.0, t, t + 2.8, x, y),                 # head on the stator side
                     G.hex_prism(7.0, zb - 3.2, zb, x, y)])     # nut on the rotor back


def references(variant):
    """Fittings, hoses, bolts, O-rings and spring for one variant."""
    t = P.stator_t
    ports = [(0.0, 0.0)] + [port_xy(a) for a in PORT_ANGLES]
    rings = [G.rotor_orings()]
    if variant == "B":
        rings += [Part.makeTorus(P.plate_gland_od / 2 - P.PLATE_ORING_CS / 2, P.PLATE_ORING_CS / 2,
                                 App.Vector(x, y, P.PLATE_T + P.PLATE_ORING_CS / 2 * 0.75), G.Z)
                  for x, y in map(port_xy, PORT_ANGLES)]
    return {
        "Fittings": (fuse_all([G.push_in_fitting(x, y, t) for x, y in ports]), "steel"),
        "Hoses": (fuse_all([G.hose(x, y, t, HOSE_LEN) for x, y in ports]), "hose"),
        "Bolts": (fuse_all([bolt(x, y) for x, y in BOLTS]), "steel_ghost"),
        "ORings": (fuse_all(rings), "oring"),
        "Spring": (G.shoe_spring(), "steel"),
    }


def ghost_selector():
    """The full 25-port stator and rotor this strip is cut from, plus the drive."""
    t, zb = P.stator_t, P.rotor_back_z
    stator_d = 2 * P.PORT_R + P.fitting_corners + 6
    disc = cyl(stator_d, 0, t).cut(fuse_all(
        [cyl(P.PORT_D, -1, t + 1, *port_xy(i * P.INDEX_DEG)) for i in range(P.N_PORTS)]))
    rotor_disc = cyl(2 * P.PORT_R + 20, zb, P.rotor_face_z)
    z_shaft_end = zb - SHAFT_LEN
    zc = z_shaft_end - 8                                                        # crank axis
    drive = fuse_all([
        cyl(SHAFT_D, z_shaft_end, zb),                                          # rotor shaft
        G.cone(30.0, z_shaft_end, 16.0, z_shaft_end + 8),                       # bevel on shaft
        Part.makeCone(15.0, 8.0, 8, App.Vector(0, 8, zc), G.Y),                 # bevel on crank
        Part.makeCylinder(4.0, CRANK_Y - 8, App.Vector(0, 8, zc), G.Y),         # crank shaft
        Part.makeBox(50, 6, 8, App.Vector(-50, CRANK_Y, zc - 4)),               # crank arm
        Part.makeCylinder(5.0, 30, App.Vector(-46, CRANK_Y + 6, zc), G.Y),      # handle
    ])
    return disc, rotor_disc, drive


LABELS = [
    ("ВХОД: воздух от 3/2-клапана", (-14, 0, P.stator_t + HOSE_LEN)),
    ("ВЫХОДЫ: совмещённый + 2 соседних", (P.PORT_R + 14, 0, P.stator_t + HOSE_LEN)),
    ("СТАТОР (неподвижный, лицом вперёд)", (STRIP_X1 + 8, 0, P.stator_t)),
    ("РОТОР (вращается за статором)", (STRIP_X0 - 12, 0, P.rotor_back_z)),
    ("БАШМАК: прижат к статору", (P.PORT_R, 0, P.rotor_back_z - 12)),
    ("ВАЛ -> коническая пара -> рукоятка сбоку", (-60, CRANK_Y, P.rotor_back_z - SHAFT_LEN - 10)),
    ("ВАРИАНТ B: корпус + пластина", (STRIP_X1 + 8, VARIANT_B_OFFSET.y, P.stator_t)),
]

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
sc = V.Scene(NAME)
doc = sc.doc
sc.add("Variant_A", "Stator_A", stator_a, "stator")
sc.add("Variant_A", "Rotor_A", rotor, "rotor")
sc.add("Variant_A", "Shoe_A", shoe, "shoe")
sc.add("Variant_B", "Body_B", stator_b, "stator", VARIANT_B_OFFSET)
sc.add("Variant_B", "Plate_B", plate_b, "plate", VARIANT_B_OFFSET)
sc.add("Variant_B", "Rotor_B", rotor, "rotor", VARIANT_B_OFFSET)
sc.add("Variant_B", "Shoe_B", shoe, "shoe", VARIANT_B_OFFSET)
for v, off in (("A", None), ("B", VARIANT_B_OFFSET)):
    sc.add("Refs_" + v, "Flow_" + v, G.flow_path(P.stator_t, HOSE_LEN), "flow", off)
    for n, (s, style) in references(v).items():
        sc.add("Refs_" + v, n + "_" + v, s, style, off)
g_disc, g_rotor, g_drive = ghost_selector()
sc.add("Ghost_selector", "Ghost_stator_25", g_disc, "ghost")
sc.add("Ghost_selector", "Ghost_rotor", g_rotor, "ghost")
sc.add("Ghost_selector", "Drive", g_drive, "drive")

half = Part.makeBox(400, 200, 400, App.Vector(-200, -200, -200))     # machine y < 0
for n, style in (("Stator_A", "stator"), ("Rotor_A", "rotor"), ("Shoe_A", "shoe"),
                 ("ORings_A", "oring"), ("Spring_A", "steel"), ("Fittings_A", "steel"),
                 ("Hoses_A", "hose")):
    sc.add("Section_A", "Sec" + n, sc.src[n].cut(half), style)

refs_a = references("A")
explode = [
    ("fittings", refs_a["Fittings"][0], "steel", "5. Штуцеры 6 мм (покупные), 4 шт."),
    ("stator", stator_a, "stator", "1. СТАТОР: печать, неподвижный"),
    ("ring_spigot", G.oring(P.oring_root_d, P.ORING_CS, P.SPIGOT_GROOVE_Z), "oring",
     "4. Кольца 8x1.5: хвостовик и башмак"),
    ("shoe", shoe.fuse(G.oring(P.oring_root_d, P.ORING_CS,
                               -P.SHOE_LEN + P.SHOE_GROOVE_FROM_BACK, P.PORT_R)), "shoe",
     "3. БАШМАК: печать или POM, плавающий"),
    ("spring", refs_a["Spring"][0], "steel", "6. Пружинка от ручки"),
    ("rotor", rotor, "rotor", "2. РОТОР: печать, вращается"),
]
for key, s, style, text in explode:
    off = App.Vector(0, 0, EXPLODE[key])
    sc.add("Exploded", "Ex_" + key, s, style, off)
    bb = sc.src["Ex_" + key].BoundBox
    sc.label("Exploded", text, (bb.XMax + 8, -30, (bb.ZMin + bb.ZMax) / 2))

for text, pos in LABELS:
    sc.label("Labels", text, pos)
sc.finish(hidden_groups=("Section_A", "Exploded"), opaque_groups=("Section_A", "Exploded"))
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

# ---------------------------------------------------------------- exports
import MeshPart


def write_stl(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(G.O, G.X, 180)
    s.translate(App.Vector(0, 0, -s.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1)
    m.write(os.path.join(OUT_DIR, name + ".stl"))


for n, s in (("stator_A", stator_a), ("body_B", stator_b), ("plate_B", plate_b),
             ("rotor", rotor), ("shoe", shoe)):
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
for n, s, flip in (("stator_A", stator_a, False), ("body_B", stator_b, False),
                   ("rotor", rotor, False), ("shoe", shoe, True)):
    write_stl(s, n, flip)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write(report + "\n")
print("written to", OUT_DIR)
