# -*- coding: utf-8 -*-
"""
Ratling pistol (hammer variant): the build guide's pictures, one per step.

Builds pistol/hammer_assembly.py, then renders each step's parts in a
scratch document: small sub-assemblies exploded along the way they go
together (in that order), the parts already in place behind them in
translucent grey, the springs as coils. Writes exports/pistol_build/guide/
stepNN.jpg, trimmed to the parts.

Run inside FreeCAD (GUI); about a minute:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/guide_renders.py').read())
"""

import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PIL import Image, ImageChops

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

GUIDE = os.path.join(REPO, "exports", "pistol_build", "guide")
os.makedirs(GUIDE, exist_ok=True)

PRINT, PRINT2, PRINT3 = (0.93, 0.55, 0.18), (0.80, 0.40, 0.14), (0.95, 0.72, 0.30)
METAL, SPRING, RUBBER = (0.70, 0.72, 0.75), (0.86, 0.86, 0.90), (0.12, 0.12, 0.14)
TUBE, HOSE, BRASS, AIRTAC = (0.25, 0.48, 0.88), (0.10, 0.10, 0.12), (0.78, 0.62, 0.25), (0.88, 0.89, 0.92)
CONTEXT = (0.74, 0.76, 0.74)
LEFT, LEFT_UP, FRONT_LEFT, RIGHT_FRONT = (0.15, 1.0, -0.42), (0.2, 1.0, -0.7), (-0.55, 0.72, -0.42), (-0.5, -0.8, -0.4)


def coil(p0, direction, length, d_out, wire=0.6, turns=6):
    """A coil spring from p0 along direction."""
    r = d_out / 2 - wire / 2
    h = Part.makeHelix(length / turns, length, r)
    prof = Part.Wire(Part.makeCircle(wire / 2, V(r, 0, 0), V(0, 1, 0)))
    s = Part.Wire(h).makePipeShell([prof], True, True)
    rot = App.Rotation(ZA, V(direction))
    s = s.copy()
    s.rotate(V(0, 0, 0), rot.Axis, math.degrees(rot.Angle))
    s.translate(p0)
    return s


def nut(centre, axis, af=5.5, t=2.4, hole=3.0):
    r = af / 2 / math.cos(math.radians(30))
    pts = [V(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k)), 0) for k in range(7)]
    n = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, t)).cut(Part.makeCylinder(hole / 2, t + 2, V(0, 0, -1)))
    rot = App.Rotation(ZA, V(axis))
    n.rotate(V(0, 0, 0), rot.Axis, math.degrees(rot.Angle))
    n.translate(centre)
    return n


def screw(head_at, axis, length, d=3.0):
    a = V(axis).normalize()
    return Part.makeCylinder(d * 0.9, d * 0.6, head_at - a * d * 0.6, a).fuse(Part.makeCylinder(d / 2, length, head_at, a))


# ---------------------------------------------------------------- parts at rest
sleeve_r = lock_sleeve(1.0)
pusher_r = pusher_shape(1.0)
oring_sleeve = Part.makeTorus(SLEEVE_BORE / 2 - 1.6, 1.6, V(HUB_X0 - 0.1 - 12.5, 0, Z_FIRE), XA)
sl_r, sl_pin = slider_h(0.0)
hammer_r = hammer_shape(0.0)
nut_m6 = _hex.cut(cyl_x(6.0, X_AXLE_END - 10, X_AXLE_END + 1, 0, 0))
_ax = App.Rotation(XA, PAWL_A0 - 90 + sector_turn(0.0))
pawl_r = turned(pawl_tooth, sector_turn(0.0))
sector_r = turned(sector_base, sector_turn(0.0))
pawl_c = pawl_r.BoundBox.Center
pawl_spring = coil(V(PAWL_BOSS_X0 + 1.4, pawl_c.y, pawl_c.z), XA, 7.0, 2.8, 0.4, 7)
_out = App.Rotation(XA, DETENT_ANGLE + 90).multVec(V(0, 0, -1))           # the detent's outward direction
bolt_r = bolt_shape(0.0)
_bc = bolt_r.BoundBox.Center
det_spring = coil(_bc + _out * (BOLT_LEN / 2 + 0.2), _out, 14.0, 4.0, 0.5, 8)
trig_r = trigger_h(0.0)
pivot_screw = screw(V(TRIGGER_PIVOT.x, -TRIGGER_CHEEKS["y"][1] - 0.5, TRIGGER_PIVOT.z), YA, 16.0)
pivot_nut = nut(V(TRIGGER_PIVOT.x, TRIGGER_CHEEKS["y"][1] + 0.5, TRIGGER_PIVOT.z), YA)
fittings = sorted(vent_fittings.Solids, key=lambda q: q.BoundBox.Center.y)
mech = [(sleeve_r, METAL), (pusher_r, PRINT), (sector_r, PRINT2), (pawl_r, PRINT), (sl_r, PRINT3), (sl_pin, METAL),
        (guide_rod, METAL), (hammer_r, PRINT2), (shaft, METAL), (mainsprings, SPRING), (trig_r, PRINT)]
valve_stack = [valve_body, valve_cap, lock_housing_h]
cage_all = [frame] + [m for m, _ in mech] + valve_stack + [axle]

# step: (file, [(shape, colour, explode offset)], [context shapes], view)
STEPS = [
    ("step01", [(valve_body, PRINT, V(0, 0, 0)), (valve_cap, PRINT2, V(-30, 0, 0))], [], FRONT_LEFT),
    ("step02", [(sleeve_r, PRINT3, V(0, 0, 0)), (oring_sleeve, RUBBER, V(-14, 0, 0)), (pusher_r, PRINT, V(-30, 0, 0))],
     [], RIGHT_FRONT),
    ("step03", [(lock_housing_h, PRINT, V(30, 0, 0)), (sleeve_r.fuse(pusher_r), PRINT3, V(60, 0, 0))], [valve_body, valve_cap],
     RIGHT_FRONT),
    ("step04", [(axle_plug, PRINT, V(0, 0, 0)), (nut_m6, METAL, V(14, 0, 0)), (axle_cap, METAL, V(32, 0, 0))],
     [axle.common(cyl_x(30, X_AXLE_END - 40, X_AXLE_END + 1, 0, 0))], FRONT_LEFT),
    ("step05", [(axle, METAL, V(40, 0, 0)), (axle_plug, PRINT, V(80, 0, 0))], valve_stack, FRONT_LEFT),
    ("step06", [(hub, PRINT, V(-30, 0, 0)), (barrels, TUBE, V(0, 0, 0)), (front_plate, PRINT2, V(30, 0, 0)),
                (oring_faces, RUBBER, V(-55, 0, 0))], [axle], FRONT_LEFT),
    ("step07", [(sector_r, PRINT2, V(0, 0, 0)), (pawl_spring, SPRING, V(12, 0, 0)), (pawl_r, PRINT, V(26, 0, 0))], [],
     (-0.45, 0.55, -0.7)),
    ("step08", [(sl_r, PRINT3, V(0, 0, 0)), (guide_rod, METAL, V(0, 0, -40)), (sl_pin, METAL, V(22, 0, 0))],
     [sector_r], RIGHT_FRONT),
    ("step09", [(hammer_r, PRINT2, V(0, 0, 0)), (mainsprings, SPRING, V(0, -28, 0)), (shaft, METAL, V(0, 60, 0)),
                (crank_pin.copy(), METAL, V(0, 22, 0))], [], LEFT_UP),
    ("step10", [(trig_r, PRINT, V(0, 0, 0)), (pivot_screw, METAL, V(0, -18, 0)), (pivot_nut, METAL, V(0, 16, 0))],
     [], LEFT),
    ("step11", [(frame, PRINT, V(0, 0, 0))] + [(m, c, V(0, 0, 0)) for m, c in mech],
     valve_stack + [axle], LEFT),
    ("step12", [(block, TUBE, V(0, 0, 0)), (washer, RUBBER, V(14, 0, 0)), (nose, PRINT2, V(28, 0, 0)),
                (top_strap, PRINT, V(0, 0, 30)), (axle_cap, METAL, V(70, 0, 0))], cage_all, LEFT),
    ("step13", [(detent_box, PRINT, V(0, 0, 0)), (det_spring, SPRING, _out * -16), (bolt_r, PRINT3, _out * -32)], [],
     (-1.0, 0.25, -0.35)),
    ("step14", [(side_plate, PRINT, V(0, -45, 0)), (detent_box, PRINT2, V(0, -45, 0)), (bolt_r, PRINT3, V(0, -45, 0))],
     cage_all + [block, top_strap], LEFT),
    ("step15", [(vent_body.fuse(vent_plunger), AIRTAC, V(0, 0, 0))] +
     [(f, BRASS, V(0, (-16 if f.BoundBox.Center.y < 0 else 16), 0)) for f in fittings], [], (0.35, 0.55, -0.75)),
    ("step16", [(valves, AIRTAC, V(0, 0, 0)), (pilot_line, TUBE, V(0, 0, 0)), (gauge_line, TUBE, V(0, 0, 0)),
                (tee, BRASS, V(0, 0, 0)), (supply_line, HOSE, V(0, 0, 0)), (gauge, BRASS, V(0, 0, 0)),
                (gauge_glass, (0.95, 0.95, 0.9), V(0, 0, 0))], [valve_body, valve_cap, frame, grip], LEFT),
    ("step17", [(grip_left, PRINT, V(0, 0, 0)), (valves, AIRTAC, V(0, 0, 0)), (supply_line, HOSE, V(0, 0, 0)),
                (dowels, METAL, V(0, 22, 0)), (grip_right, PRINT2, V(0, 50, 0))], [], (0.25, -1.0, -0.45)),
    ("step18", [(grip, PRINT, V(0, 0, -30)), (guard, PRINT2, V(0, 0, -50))],
     cage_all + [block, top_strap, side_plate, detent_box, valves], LEFT),
]


def render(file, items, context, view, scratch):
    for o in scratch.Objects:
        scratch.removeObject(o.Name)
    for k, sh in enumerate(context):
        o = scratch.addObject("Part::Feature", "C%d" % k)
        o.Shape = sh
        o.ViewObject.ShapeColor, o.ViewObject.Transparency = CONTEXT, 60
    for k, (sh, col, off) in enumerate(items):
        s = sh.copy()
        s.translate(off)
        o = scratch.addObject("Part::Feature", "P%d" % k)
        o.Shape = s
        o.ViewObject.ShapeColor, o.ViewObject.Transparency = col, 0
        if off.Length > 1e-6:                                    # a faint line back to where it goes
            c = sh.BoundBox.Center
            ln = scratch.addObject("Part::Feature", "L%d" % k)
            ln.Shape = Part.makeCylinder(0.35, off.Length, c, off)
            ln.ViewObject.ShapeColor = (0.55, 0.58, 0.56)
    scratch.recompute()
    v = Gui.getDocument(scratch.Name).activeView()
    v.setCameraType("Orthographic")
    v.setViewDirection(view)
    Gui.updateGui()
    v.fitAll()
    Gui.updateGui()
    tmp = os.path.join(GUIDE, "_tmp.png")
    v.saveImage(tmp, 1400, 1050, "White")
    im = Image.open(tmp).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    bb = (max(bb[0] - 24, 0), max(bb[1] - 24, 0), min(bb[2] + 24, im.width), min(bb[3] + 24, im.height))
    c = im.crop(bb)
    if c.width > 1000:
        c = c.resize((1000, int(c.height * 1000 / c.width)), Image.LANCZOS)
    c.save(os.path.join(GUIDE, file + ".jpg"), quality=86)
    os.remove(tmp)
    return c.size


if "guide_render" in App.listDocuments():
    App.closeDocument("guide_render")
scratch = App.newDocument("guide_render")
Gui.ActiveDocument = Gui.getDocument("guide_render")
pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
anim = pv.GetBool("UseNavigationAnimations", True)
pv.SetBool("UseNavigationAnimations", False)
sizes = {}
try:
    for file, items, context, view in STEPS:
        sizes[file] = render(file, items, context, view, scratch)
finally:
    pv.SetBool("UseNavigationAnimations", anim)
print("guide renders:", ", ".join("%s %dx%d" % (k, w, h) for k, (w, h) in sizes.items()))
