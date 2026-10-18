# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v1.1 bench: the pictures for the bench guide, one per step.

Builds the v1.1 valve (module/stage3_qev.py), the floating seal (module/stage3_floating_seal.py) and the vent
head (module/stage3_vent_head.py), and renders each assembly step exploded along the way it goes together:
the parts of the step tinted, those already in place in translucent grey, a faint line from each part to
where it goes. Writes exports/stage3_qev/guide/*.jpg.

Run inside FreeCAD (GUI); about a minute:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_qev_bench_renders.py').read())
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


def load(rel, **pre):
    ns = {"REPO": REPO, "__name__": "bench_" + os.path.basename(rel)}
    ns.update(pre)
    exec(open(os.path.join(REPO, rel)).read(), ns)
    return ns


q = load("module/stage3_qev.py", STAGE3_LIBRARY=True)
f = load("module/stage3_floating_seal.py")
vh = load("module/stage3_vent_head.py")
if "stage3_vent_head" in App.listDocuments():
    App.closeDocument("stage3_vent_head")

GUIDE = os.path.join(REPO, "exports", "stage3_qev", "guide")
os.makedirs(GUIDE, exist_ok=True)
V = App.Vector
O = V(0, 0, 0)

PRINT, PRINT2, PRINT3 = (0.93, 0.55, 0.18), (0.80, 0.40, 0.14), (0.95, 0.72, 0.30)
METAL, RUBBER, TUBE, BRASS = (0.70, 0.72, 0.75), (0.12, 0.12, 0.14), (0.25, 0.48, 0.88), (0.78, 0.62, 0.25)
ORING_C, BALL_C, HOSE_C = (0.80, 0.12, 0.12), (0.95, 0.85, 0.20), (0.10, 0.10, 0.12)
CONTEXT = (0.74, 0.76, 0.74)
FROM_BELOW = (0.62, 0.62, 0.48)     # camera looks up a little: the cap side of the stack
OBLIQUE = (0.62, 0.62, -0.48)
SIDE = (0.0, 1.0, -0.12)


def tint(c):
    return tuple(min(1.0, 0.55 * x + 0.45 * y) for x, y in zip(c, (0.35, 0.85, 0.35)))


def coil(p0, length, d_out, wire=0.5, turns=6):
    r = d_out / 2 - wire / 2
    h = Part.makeHelix(length / turns, length, r)
    prof = Part.Wire(Part.makeCircle(wire / 2, V(r, 0, 0), V(0, 1, 0)))
    s = Part.Wire(h).makePipeShell([prof], True, True)
    s.translate(p0)
    return s


def washer(p, z, od=7.0, idd=3.2, t=0.5):
    return Part.makeCylinder(od / 2, t, V(p.x, p.y, z)).cut(Part.makeCylinder(idd / 2, t + 2, V(p.x, p.y, z - 1)))


def render(file, items, context, view, scratch, turn=0):
    """items: [(shape, colour, offset, tinted)]; turn: rotate the picture (deg, counter-clockwise)."""
    for o in scratch.Objects:
        scratch.removeObject(o.Name)
    for k, sh in enumerate(context):
        o = scratch.addObject("Part::Feature", "C%d" % k)
        o.Shape = sh
        o.ViewObject.ShapeColor, o.ViewObject.Transparency = CONTEXT, 60
    for k, (sh, col, off, hot) in enumerate(items):
        s = sh.copy()
        s.translate(off)
        o = scratch.addObject("Part::Feature", "P%d" % k)
        o.Shape = s
        o.ViewObject.ShapeColor, o.ViewObject.Transparency = (tint(col) if hot else col), 0
        if off.Length > 1e-6:
            ln = scratch.addObject("Part::Feature", "L%d" % k)
            ln.Shape = Part.makeCylinder(0.3, off.Length, sh.BoundBox.Center, off)
            ln.ViewObject.ShapeColor = (0.55, 0.58, 0.56)
    scratch.recompute()
    v = Gui.getDocument(scratch.Name).activeView()
    v.setCameraType("Orthographic")
    v.setViewDirection(view)
    Gui.updateGui()
    v.fitAll()
    Gui.updateGui()
    tmp = os.path.join(GUIDE, "_tmp.png")
    v.saveImage(tmp, 1400, 1400, "White")
    im = Image.open(tmp).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    bb = (max(bb[0] - 24, 0), max(bb[1] - 24, 0), min(bb[2] + 24, im.width), min(bb[3] + 24, im.height))
    c = im.crop(bb)
    if turn:
        c = c.rotate(turn, expand=True, fillcolor="white")
    if max(c.size) > 1000:
        k = 1000 / max(c.size)
        c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
    c.save(os.path.join(GUIDE, file + ".jpg"), quality=86)
    os.remove(tmp)


# ---------------------------------------------------------------- v1.1 parts in place (body frame)
BODY_H, CAP_T, C = q["BODY_H"], q["CAP_T"], q["C"]
body, cap, dia, breech, plug, clip = q["body"], q["cap_a"], q["dia_a"], q["breech_a"], q["plug"], q["clip_a"]
barrel, chamber = q["tubes"]
rods = q["tie_rods"]()
screws = q["tube_screws"]()
fitting, hose, ball = q["pilot_fitting"], q["pilot_hose"], q["ball"]
root_r, cs = q["root_r"], q["ORING_CS"]
ring_z = q["ring_z"]
ring_barrel = q["G"].oring(2 * root_r, cs, ring_z(q["BREECH_FLANGE_T"] + q["BARREL_SPIGOT_LEN"]))
ring_chamber = q["G"].oring(2 * root_r, cs, ring_z(q["CHAMBER_SPIGOT_LEN"]), C.x, C.y)
ring_plug = q["G"].oring(2 * root_r, cs, q["plug_ring_z"], C.x, C.y)
fg_out, fg_d, fcs = q["face_groove_out"], q["face_groove_depth"], q["FACE_ORING_CS"]
ring_face = Part.makeTorus(fg_out - fcs / 2, fcs / 2, V(0, 0, BODY_H + fcs / 2), V(0, 0, 1))
bolts = q["breech_bolts"]
breech_screws = q["G"].fuse_all([Part.makeCylinder(1.5, 14, V(p.x, p.y, BODY_H + q["BREECH_FLANGE_T"] + 2 - 14))
                                 .fuse(Part.makeCylinder(2.75, 3, V(p.x, p.y, BODY_H + q["BREECH_FLANGE_T"] + 2)))
                                 for p in bolts])
gap_washers = q["G"].fuse_all([washer(p, BODY_H) for p in bolts])
# rods: heads under the cap, nuts in the body's pockets; draw the rods and the nuts apart
rod_shafts = q["G"].fuse_all([Part.makeCylinder(2.0, q["rod_len"], V(p.x, p.y, -CAP_T - q["WASHERS_UNDER_HEAD"]))
                              .fuse(Part.makeCylinder(3.5, 4.0, V(p.x, p.y, -CAP_T - q["WASHERS_UNDER_HEAD"] - 4.0)))
                              for p in q["rod_pts"]])
rod_nuts = q["G"].fuse_all([q["G"].hex_prism(q["NUT_AF"], BODY_H - q["NUT_POCKET_DEPTH"],
                                             BODY_H - q["NUT_POCKET_DEPTH"] + q["NUT_T"], p.x, p.y) for p in q["rod_pts"]])
rod_washers = q["G"].fuse_all([washer(p, -CAP_T - q["WASHERS_UNDER_HEAD"], 9.0, 4.3, q["WASHERS_UNDER_HEAD"])
                               for p in q["rod_pts"]])

doc = App.newDocument("bench_guide")
Gui.ActiveDocument = Gui.getDocument(doc.Name)
Z = lambda d: V(0, 0, d)

# 1. valve: diaphragm into the cap, body on it, four M4 from the cap side
render("s1_valve", [(body, PRINT, O, False), (dia, RUBBER, Z(-22), True), (cap, PRINT2, Z(-45), True),
                    (rod_washers, RUBBER, Z(-80), True), (rod_shafts, METAL, Z(-95), True),
                    (rod_nuts, METAL, Z(30), True), (fitting, BRASS, Z(-120), True)],
       [], FROM_BELOW, doc)
valve = [body, cap, dia, rods, fitting]
# 2. chamber: O-ring on the spigot, tube over it, screws; plug into the far end
L = q["chamber_tube_len"]
render("s2_chamber", [(ring_chamber, ORING_C, Z(8), True), (chamber, TUBE, Z(60), True),
                      (ring_plug, ORING_C, Z(130), True), (plug, PRINT, Z(150), True),
                      (screws, METAL, O, True)],
       valve, OBLIQUE, doc)
# 3. barrel: gap washers on the bolts, face O-ring, breech with its spigot ring, barrel tube
render("s3_breech", [(gap_washers, METAL, Z(10), True), (ring_face, ORING_C, Z(22), True),
                     (breech, PRINT3, Z(40), True), (ring_barrel, ORING_C, Z(70), True),
                     (barrel.common(Part.makeCylinder(30, 90, V(0, 0, 0))), TUBE, Z(110), True),
                     (breech_screws, METAL, Z(70), True)],
       valve + [chamber.common(Part.makeBox(200, 200, 120, V(-100, -100, 0)))], OBLIQUE, doc)
# 4. all together on the bench: clip by the plug, ball in the barrel, pilot hose
render("s4_bench", [(body, PRINT, O, False), (cap, PRINT2, O, False), (rods, METAL, O, False),
                    (breech, PRINT3, O, False), (barrel, TUBE, O, False), (chamber, TUBE, O, False),
                    (plug, PRINT, O, False), (screws, METAL, O, False), (fitting, BRASS, O, False),
                    (hose, HOSE_C, O, False), (clip, PRINT2, O, True)],
       [], SIDE, doc, turn=-90)
# 4b. section through both tubes: the air path
half = Part.makeBox(400, 200, 800, V(-200, 0, -200))
sec = [(s.cut(half), col) for s, col in ((body, PRINT), (cap, PRINT2), (dia, RUBBER), (breech, PRINT3),
                                            (barrel.common(Part.makeCylinder(30, 110)), TUBE),
                                            (chamber.common(Part.makeBox(200, 200, 110, V(-100, -100, 0))), TUBE),
                                            (fitting, BRASS),
                                            (ring_barrel.fuse(ring_chamber).fuse(ring_face), ORING_C))]
render("s4_section", [(s, col, O, False) for s, col in sec] + [(ball, BALL_C, O, False)], [], (0, -1, 0), doc, turn=-90)

# 5. floating seal: housing, sleeve with its O-ring, springs, collar, gap washers, breech without its face ring
fs = lambda s: s.translated(Z(BODY_H))
springs = q["G"].fuse_all([coil(V(f["SPRING_R"] * math.cos(math.radians(a)), f["SPRING_R"] * math.sin(math.radians(a)),
                                    BODY_H + f["z2"] + f["FLANGE_T"]), f["TRAVEL_ROOM"] + 3.0, 4.5)
                           for a in f["SPRING_ANGLES"]])
stack_top = BODY_H + f["z_collar_top"]
render("s5_floating", [(fs(f["housing"]), PRINT, Z(15), True), (fs(f["sleeve"]), PRINT3, Z(45), True),
                       (springs, METAL, Z(65), True), (fs(f["collar"]), PRINT2, Z(85), True),
                       (gap_washers.translated(Z(stack_top - BODY_H)), METAL, Z(100), True),
                       (breech.translated(Z(stack_top - BODY_H)), PRINT3, Z(120), True)],
       valve, OBLIQUE, doc)

# 6. vent head: poppet with its O-ring and spring into the body, lid with its O-ring on top
render("s6_vent", [(vh["body"], PRINT, O, False), (vh["poppet"].fuse(vh["poppet_ring"]), PRINT3, Z(30), True),
                   (vh["spring"], METAL, Z(50), True), (vh["lid_ring"], ORING_C, Z(62), True),
                   (vh["lid"], PRINT2, Z(80), True)],
       [], OBLIQUE, doc)

App.closeDocument(doc.Name)
print("written to", GUIDE, sorted(os.listdir(GUIDE)))
