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
importlib.reload(P)

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

Z = App.Vector(0, 0, 1)
O = App.Vector(0, 0, 0)


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, App.Vector(x, y, z0), Z)


def cone(d0, z0, d1, z1, x=0.0, y=0.0):
    """Cone from Ø d0 at z0 to Ø d1 at z1 (z1 > z0)."""
    return Part.makeCone(d0 / 2, d1 / 2, z1 - z0, App.Vector(x, y, z0), Z)


def fuse_all(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s


def strip(z0, z1):
    box = Part.makeBox(STRIP_X1 - STRIP_X0, STRIP_W, z1 - z0,
                       App.Vector(STRIP_X0, -STRIP_W / 2, z0))
    vertical = [e for e in box.Edges
                if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6]
    return box.makeFillet(STRIP_CORNER_R, vertical)


def port_xy(a_deg):
    a = math.radians(a_deg)
    return P.PORT_R * math.cos(a), P.PORT_R * math.sin(a)


def bolt_holes(z0, z1):
    return fuse_all([cyl(BOLT_D, z0 - 1, z1 + 1, x, y) for x, y in BOLTS])


def teardrop_x(d, x0, x1, z):
    """Horizontal channel along X, 45 deg roof pointing +Z (prints unsupported)."""
    r = d / 2
    c = Part.makeCylinder(r, x1 - x0, App.Vector(x0, 0, z), App.Vector(1, 0, 0))
    roof = Part.makeBox(x1 - x0, r, r, App.Vector(x0, 0, 0))
    roof.rotate(O, App.Vector(1, 0, 0), 45)
    roof.translate(App.Vector(0, 0, z))
    return c.fuse(roof)


# ---------------------------------------------------------------- stator
def stator_cut_tools(face_z):
    """Holes of the stator; face_z is where the printed material starts."""
    t = P.stator_t
    tools = [
        # centre: lead chamfer, spigot bore, 45 deg roof, inlet, tap
        cone(P.spigot_bore_d + 2 * P.LEAD_CHAMFER, face_z - 0.01,
             P.spigot_bore_d, face_z + P.LEAD_CHAMFER),
        cyl(P.spigot_bore_d, face_z - 1, P.spigot_bore_depth),
        cone(P.spigot_bore_d, P.spigot_bore_depth,
             P.PORT_D, P.spigot_bore_depth + P.spigot_cone_h),
        cyl(P.PORT_D, 0, t + 1),
        cyl(P.G18_TAP_DRILL, t - P.G18_TAP_DEPTH, t + 1),
        bolt_holes(0, t),
    ]
    for a in PORT_ANGLES:
        x, y = port_xy(a)
        tools += [cyl(P.PORT_D, -1, t + 1, x, y),
                  cyl(P.G18_TAP_DRILL, t - P.G18_TAP_DEPTH, t + 1, x, y)]
    return fuse_all(tools)


def port_chamfers(z):
    """Chamfer on the sealing face at z, so the shoe does not catch."""
    c = P.PORT_CHAMFER
    return fuse_all([cone(P.PORT_D + 2 * c + 0.02, z - 0.01, P.PORT_D, z + c, *port_xy(a))
                     for a in PORT_ANGLES])


def make_stator_printed():
    s = strip(0, P.stator_t)
    s = s.cut(stator_cut_tools(0)).cut(port_chamfers(0))
    return s.removeSplitter()


def make_stator_plate_variant():
    body = strip(P.PLATE_T, P.stator_t)
    glands = fuse_all([cyl(P.plate_gland_od, P.PLATE_T - 1, P.PLATE_T + P.plate_gland_depth,
                           *port_xy(a)) for a in PORT_ANGLES])
    body = body.cut(stator_cut_tools(P.PLATE_T)).cut(glands).removeSplitter()

    plate = strip(0, P.PLATE_T)
    holes = [cyl(P.spigot_bore_d + 1.0, -1, P.PLATE_T + 1), bolt_holes(0, P.PLATE_T)]
    holes += [cyl(P.PORT_D, -1, P.PLATE_T + 1, *port_xy(a)) for a in PORT_ANGLES]
    plate = plate.cut(fuse_all(holes)).cut(port_chamfers(0)).removeSplitter()
    return body, plate


# ---------------------------------------------------------------- rotor
def make_rotor():
    zf, zb = P.rotor_face_z, P.rotor_back_z
    body = strip(zb, zf)
    bosses = [cyl(BOSS_D, zf - 0.01, 0, x, y) for x, y in BOLTS]

    tip = P.SPIGOT_TIP_Z
    lc = P.LEAD_CHAMFER
    spigot = cyl(P.spigot_d, zf - 0.01, tip - lc).fuse(
        cone(P.spigot_d, tip - lc, P.spigot_d - 2 * lc, tip))
    groove = cyl(P.spigot_d + 2, P.SPIGOT_GROOVE_Z - P.groove_w / 2,
                 P.SPIGOT_GROOVE_Z + P.groove_w / 2).cut(
        cyl(P.oring_root_d, P.SPIGOT_GROOVE_Z - P.groove_w / 2 - 1,
            P.SPIGOT_GROOVE_Z + P.groove_w / 2 + 1))
    spigot = spigot.cut(groove)

    rotor = fuse_all([body, spigot] + bosses)

    r = P.PORT_D / 2
    sx = P.PORT_R
    passages = fuse_all([
        cyl(P.PORT_D, P.channel_z - r, tip + 1),                    # spigot axis
        teardrop_x(P.CHANNEL_D, 0, sx, P.channel_z),                # radial channel
        cyl(P.PORT_D, P.channel_z - r, P.shoe_floor_z + 0.01, sx),  # down from shoe bore
        cyl(P.shoe_bore_d, P.shoe_floor_z, zf + 1, sx),             # shoe bore
        cone(P.shoe_bore_d, zf - 0.5, P.shoe_bore_d + 1.0, zf + 0.01, sx),  # mouth chamfer
        bolt_holes(zb, 0),
    ])
    return rotor.cut(passages).removeSplitter()


# ---------------------------------------------------------------- shoe
def make_shoe():
    """Shoe in its installed position: face at z = 0, on the aligned port."""
    L = P.SHOE_LEN
    ch = P.SHOE_FACE_CHAMFER
    zb = -L
    shoe = fuse_all([
        cone(P.shoe_d - 2 * ch, zb, P.shoe_d, zb + ch),
        cyl(P.shoe_d, zb + ch, -ch),
        cone(P.shoe_d, -ch, P.shoe_land_d, 0),
    ])
    gz = zb + P.SHOE_GROOVE_FROM_BACK
    groove = cyl(P.shoe_d + 2, gz - P.groove_w / 2, gz + P.groove_w / 2).cut(
        cyl(P.oring_root_d, gz - P.groove_w / 2 - 1, gz + P.groove_w / 2 + 1))
    shoe = shoe.cut(groove).cut(cyl(P.PORT_D, zb - 1, 1)).cut(
        cyl(P.SHOE_SPRING_SEAT_D, zb - 1, zb + P.SHOE_SPRING_SEAT_DEPTH))
    shoe.translate(App.Vector(P.PORT_R, 0, 0))
    return shoe.removeSplitter()


# ---------------------------------------------------------------- build
stator_a = make_stator_printed()
stator_b, plate_b = make_stator_plate_variant()
rotor = make_rotor()
shoe = make_shoe()


# ---------------------------------------------------------------- checks
def single_solid(s):
    return s.isValid() and len(s.Solids) == 1


def no_overlap(a, b):
    return a.common(b).Volume < 1e-3


def open_along(solid, pts):
    """True if none of the points lies inside the solid (air path is open)."""
    return not any(solid.isInside(App.Vector(*p), 1e-4, True) for p in pts)


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


geo_checks = [
    ("all parts valid single solids",
     all(single_solid(s) for s in (stator_a, stator_b, plate_b, rotor, shoe))),
    ("A: stator / rotor no interference", no_overlap(stator_a, rotor)),
    ("A: stator / shoe no interference", no_overlap(stator_a, shoe)),
    ("rotor / shoe no interference", no_overlap(rotor, shoe)),
    ("B: body / plate / rotor / shoe no interference",
     all(no_overlap(a, b) for a, b in ((stator_b, plate_b), (stator_b, rotor),
                                       (plate_b, rotor), (plate_b, shoe), (stator_b, shoe)))),
    ("shoe face on the stator face (z = 0)", abs(shoe.BoundBox.ZMax) < 1e-6),
    ("air path open through rotor", open_along(rotor, air_path) and open_along(shoe, [(sx, 0, -1)])),
    ("air path open through stator A", open_along(stator_a, stator_path)),
    ("air path open through stator B",
     open_along(stator_b, stator_path) and open_along(plate_b, [(0, 0, 1), (sx, 0, 1)])),
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
HOSE_D = 6.0
HOSE_LEN = 60.0
SHAFT_D = 10.0
SHAFT_LEN = 55.0
CRANK_Y = 90.0             # crank on the side: machine +Y = left in the view
X = App.Vector(1, 0, 0)


def hex_prism(af, z0, z1, x=0.0, y=0.0):
    r = af / math.sqrt(3)
    pts = [App.Vector(x + r * math.cos(math.radians(60 * i)),
                      y + r * math.sin(math.radians(60 * i)), z0) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, z1 - z0))


def push_in_fitting(x, y):
    """Generic G1/8 - 6 mm straight push-in: thread in the tap, hex, body, collet."""
    t = P.stator_t
    return fuse_all([cyl(9.7, t - 6, t, x, y), hex_prism(P.FITTING_HEX, t, t + 5, x, y),
                     cyl(12.0, t + 5, t + 15, x, y), cyl(10.0, t + 15, t + 18, x, y)])


def oring(d_root, cs, z, x=0.0):
    """Torus seated on a groove root Ø d_root (radial gland)."""
    return Part.makeTorus(d_root / 2 + cs / 2, cs / 2, App.Vector(x, 0, z), Z)


def spring(x, z0, z1, od=6.0, wire=0.5, coils=5):
    r = od / 2 - wire / 2
    try:
        helix = Part.makeHelix((z1 - z0) / coils, z1 - z0, r)
        helix.translate(App.Vector(x, 0, z0))
        prof = Part.Wire(Part.makeCircle(wire / 2, App.Vector(x + r, 0, z0), App.Vector(0, 1, 0)))
        return Part.Wire(helix.Edges).makePipeShell([prof], True, True)
    except Exception:
        return cyl(od, z0, z1, x).cut(cyl(od - 2 * wire, z0 - 1, z1 + 1, x))


def bolt(x, y):
    zb, t = P.rotor_back_z, P.stator_t
    return fuse_all([cyl(4.0, zb - 4, t + 3.2, x, y),
                     cyl(7.0, t, t + 2.8, x, y),               # head on the stator side
                     hex_prism(7.0, zb - 3.2, zb, x, y)])     # nut on the rotor back


def flow_path():
    """Air path as a red line with arrow heads: in at the centre, out at the port."""
    t, cz, sx = P.stator_t, P.channel_z, P.PORT_R
    top = t + HOSE_LEN
    pts = [App.Vector(0, 0, top), App.Vector(0, 0, cz), App.Vector(sx, 0, cz), App.Vector(sx, 0, top)]
    segs = []
    for a, b in zip(pts, pts[1:]):
        d = b - a
        segs.append(Part.makeCylinder(1.0, d.Length, a, d))
        mid = a + d * 0.5
        segs.append(Part.makeCone(3.0, 0, 7.0, mid, d))
    segs += [Part.makeSphere(1.0, p) for p in pts[1:-1]]
    return fuse_all(segs)


def ghost_selector():
    """The full 25-port stator and rotor this strip is cut from, plus the drive."""
    t, zb = P.stator_t, P.rotor_back_z
    stator_d = 2 * P.PORT_R + P.fitting_corners + 6
    disc = cyl(stator_d, 0, t).cut(fuse_all(
        [cyl(P.PORT_D, -1, t + 1, *port_xy(i * P.INDEX_DEG)) for i in range(P.N_PORTS)]))
    rotor_disc = cyl(2 * P.PORT_R + 20, zb, P.rotor_face_z)
    z_shaft_end = zb - SHAFT_LEN
    zc = z_shaft_end - 8                                                        # crank axis
    Y = App.Vector(0, 1, 0)
    drive = fuse_all([
        cyl(SHAFT_D, z_shaft_end, zb),                                          # rotor shaft
        cone(30.0, z_shaft_end, 16.0, z_shaft_end + 8),                         # bevel on shaft
        Part.makeCone(15.0, 8.0, 8, App.Vector(0, 8, zc), Y),                   # bevel on crank
        Part.makeCylinder(4.0, CRANK_Y - 8, App.Vector(0, 8, zc), Y),           # crank shaft
        Part.makeBox(50, 6, 8, App.Vector(-50, CRANK_Y, zc - 4)),               # crank arm
        Part.makeCylinder(5.0, 30, App.Vector(-46, CRANK_Y + 6, zc), Y),        # handle
    ])
    return disc, rotor_disc, drive


def references(variant):
    """Fittings, hoses, bolts, O-rings and spring for one variant, in its own frame."""
    t, sx = P.stator_t, P.PORT_R
    ports = [(0.0, 0.0)] + [port_xy(a) for a in PORT_ANGLES]
    fittings = fuse_all([push_in_fitting(x, y) for x, y in ports])
    hoses = fuse_all([cyl(HOSE_D, t + 6, t + HOSE_LEN, x, y) for x, y in ports])
    bolts = fuse_all([bolt(x, y) for x, y in BOLTS])
    gz = -P.SHOE_LEN + P.SHOE_GROOVE_FROM_BACK
    rings = [oring(P.oring_root_d, P.ORING_CS, P.SPIGOT_GROOVE_Z),
             oring(P.oring_root_d, P.ORING_CS, gz, sx)]
    if variant == "B":
        rings += [Part.makeTorus(P.plate_gland_od / 2 - P.PLATE_ORING_CS / 2, P.PLATE_ORING_CS / 2,
                                 App.Vector(x, y, P.PLATE_T + P.PLATE_ORING_CS / 2 * 0.75), Z)
                  for x, y in map(port_xy, PORT_ANGLES)]
    spr = spring(sx, P.shoe_floor_z, -P.SHOE_LEN + P.SHOE_SPRING_SEAT_DEPTH)
    return {"Fittings": fittings, "Hoses": hoses, "Bolts": bolts,
            "ORings": fuse_all(rings), "Spring": spr}


LABELS = [
    ("ВХОД: воздух от 3/2-клапана", (-14, 0, P.stator_t + HOSE_LEN)),
    ("ВЫХОДЫ: совмещённый + 2 соседних", (P.PORT_R + 14, 0, P.stator_t + HOSE_LEN)),
    ("СТАТОР (неподвижный, лицом вперёд)", (STRIP_X1 + 8, 0, P.stator_t)),
    ("РОТОР (вращается за статором)", (STRIP_X0 - 12, 0, P.rotor_back_z)),
    ("БАШМАК: прижат к статору", (P.PORT_R, 0, P.rotor_back_z - 12)),
    ("ВАЛ -> коническая пара -> рукоятка сбоку", (-60, CRANK_Y, P.rotor_back_z - SHAFT_LEN - 10)),
    ("ВАРИАНТ B: корпус + пластина", (STRIP_X1 + 8, VARIANT_B_OFFSET.y, P.stator_t)),
]

# ---------------------------------------------------------------- output
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)

# The document shows the unit as it stands: FreeCAD "Front" looks at the
# machine's front (machine +Z towards the viewer), the strip points up, the
# crank is on the left. Only the document objects are turned; exports and
# checks stay in the machine frame of ratling/params.py.
VIEW_ROT = App.Placement(App.Matrix(0, -1, 0, 0,
                                    0, 0, -1, 0,
                                    1, 0, 0, 0,
                                    0, 0, 0, 1))

STEEL = (0.7, 0.7, 0.72)
# name: (colour, transparency)
STYLE = {
    "Stator": ((0.55, 0.75, 0.95), 65), "Body": ((0.55, 0.75, 0.95), 65),
    "Plate": ((0.85, 0.9, 0.95), 55), "Rotor": ((0.95, 0.55, 0.15), 40),
    "Shoe": ((0.15, 0.15, 0.15), 0), "Fittings": (STEEL, 0), "Hoses": ((0.3, 0.55, 0.9), 30),
    "Bolts": (STEEL, 50), "ORings": ((0.85, 0.1, 0.1), 0), "Spring": (STEEL, 0),
    "Flow": ((1.0, 0.0, 0.0), 0), "Ghost": ((0.6, 0.6, 0.6), 88), "Drive": ((0.5, 0.5, 0.55), 40),
}


src = {}                                   # machine-frame shapes of the objects


def add(group, name, shape, offset=None):
    if offset is not None:
        shape = shape.copy()
        shape.translate(offset)
    src[name] = shape
    shown = shape.copy()
    shown.Placement = VIEW_ROT.multiply(shown.Placement)
    o = doc.addObject("Part::Feature", name)
    o.Shape = shown
    group.addObject(o)
    return o


groups = {g: doc.addObject("App::DocumentObjectGroup", g)
          for g in ("Variant_A", "Variant_B", "Refs_A", "Refs_B", "Ghost_selector", "Labels")}
objs = [
    add(groups["Variant_A"], "Stator_A", stator_a),
    add(groups["Variant_A"], "Rotor_A", rotor),
    add(groups["Variant_A"], "Shoe_A", shoe),
    add(groups["Variant_B"], "Body_B", stator_b, VARIANT_B_OFFSET),
    add(groups["Variant_B"], "Plate_B", plate_b, VARIANT_B_OFFSET),
    add(groups["Variant_B"], "Rotor_B", rotor, VARIANT_B_OFFSET),
    add(groups["Variant_B"], "Shoe_B", shoe, VARIANT_B_OFFSET),
    add(groups["Refs_A"], "Flow_A", flow_path()),
    add(groups["Refs_B"], "Flow_B", flow_path(), VARIANT_B_OFFSET),
]
for v, off in (("A", None), ("B", VARIANT_B_OFFSET)):
    for n, s in references(v).items():
        objs.append(add(groups["Refs_" + v], n + "_" + v, s, off))
g_disc, g_rotor, g_drive = ghost_selector()
objs += [add(groups["Ghost_selector"], "Ghost_stator_25", g_disc),
         add(groups["Ghost_selector"], "Ghost_rotor", g_rotor),
         add(groups["Ghost_selector"], "Drive", g_drive)]
half = Part.makeBox(400, 200, 400, App.Vector(-200, -200, -200))     # machine y < 0
groups["Section_A"] = doc.addObject("App::DocumentObjectGroup", "Section_A")
for n in ("Stator_A", "Rotor_A", "Shoe_A", "ORings_A", "Spring_A", "Fittings_A", "Hoses_A"):
    objs.append(add(groups["Section_A"], "Sec" + n, src[n].cut(half)))
for i, (text, pos) in enumerate(LABELS):
    a = doc.addObject("App::Annotation", "Label%d" % i)
    a.LabelText = [text]
    a.Position = VIEW_ROT.multVec(App.Vector(*pos))
    groups["Labels"].addObject(a)
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    for o in objs:
        colour, transp = STYLE[o.Name.split("_")[0].replace("Sec", "")]
        o.ViewObject.ShapeColor = colour
        o.ViewObject.Transparency = transp
    for a in groups["Labels"].Group:
        a.ViewObject.FontSize = 14
        a.ViewObject.TextColor = (0.1, 0.1, 0.1)
    for o in groups["Section_A"].Group:          # opaque cut-away, off by default
        o.ViewObject.Transparency = 0
        o.ViewObject.Visibility = False
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart


def write_stl(shape, name, flip=False):
    s = shape.copy()
    if flip:
        s.rotate(O, App.Vector(1, 0, 0), 180)
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
