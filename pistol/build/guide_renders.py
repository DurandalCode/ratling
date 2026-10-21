# -*- coding: utf-8 -*-
"""
Ratling pistol (hammer variant): the build guide's pictures, one per step.

Builds pistol/hammer_assembly.py, then renders each sub-step of the guide
in a scratch document, one frame per checkbox: the sub-assembly starts
exploded along the way it goes together, and each checkbox moves its
parts into place (tinted green in its frame); the parts already in place
around it in translucent grey, springs as coils. Writes
exports/pistol_build/guide/sNN_K.jpg and frames.json (the files of each
sub-step's frames, frame 0 first), which the HTML guide uses.

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
TUBE, HOSE, BRASS, VALVE_C = (0.25, 0.48, 0.88), (0.10, 0.10, 0.12), (0.78, 0.62, 0.25), (0.88, 0.89, 0.92)
CONTEXT = (0.74, 0.76, 0.74)
LEFT, LEFT_UP, FRONT_LEFT, RIGHT_FRONT = (0.15, 1.0, -0.42), (0.2, 1.0, -0.7), (-0.55, 0.72, -0.42), (-0.5, -0.8, -0.4)
OBLIQUE = (0.72, 0.58, -0.42)       # from behind-left: a part pulled out sideways (y) reads as pulled out


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

# Each sub-step of the guide: parts (a part is one shape or a list of (shape, colour), with its starting offset:
# a vector, or None for "not there yet"), context shapes in translucent grey, the view, and one move per
# checkbox of that sub-step: {part index: new offset (V(0,0,0) = in place), or "show"}. Frame 0 is the start;
# frame k shows the state after the k-th checkbox. The parts a move touches are tinted green in its frame.
O = V(0, 0, 0)
_pin_at = V(X_OPEN + LOCK_STROKE, 0, 0)
pusher_body = ring.fuse(lug).translated(_pin_at)
pusher_pin = cam_pin.translated(_pin_at)
_fx = {"A": VENT_FRONT - AIRTAC["ports"]["A"][0], "R": VENT_FRONT - AIRTAC["ports"]["R"][0], "P": VENT_FRONT - AIRTAC["P"][0]}
fit = {k: Part.makeCompound([f for f in vent_fittings.Solids if abs(f.BoundBox.Center.x - x_) < 3.0]) for k, x_ in _fx.items()}
stack = [(valve_body, PRINT), (valve_cap, PRINT2), (lock_housing_h, PRINT), (sleeve_r, PRINT3), (pusher_r, PRINT), (axle, METAL),
         (axle_plug, PRINT2)]
SUBS = [
    dict(id="s01", view=FRONT_LEFT, context=[],
         parts=[(valve_body, PRINT, O), (valve_cap, PRINT2, V(-30, 0, 0))],
         moves=[{1: O}, {}, {}]),
    dict(id="s02", view=RIGHT_FRONT, context=[],
         parts=[(sleeve_r, PRINT3, O), (pusher_body, PRINT, V(-30, 0, 0)), (pusher_pin, METAL, V(-30, 18, 0))],
         moves=[{}, {1: O, 2: V(0, 18, 0)}, {2: O}]),           # the sleeve goes in plain: no O-ring (bench, 2026-10-21)
    dict(id="s03", view=RIGHT_FRONT, context=[valve_body, valve_cap],
         parts=[(lock_housing_h, PRINT, V(30, 0, 0)), ([(sleeve_r, PRINT3), (pusher_r, PRINT)], None, V(65, 0, 0))],
         moves=[{1: V(30, 0, 0)}, {0: O, 1: O}, {}]),
    dict(id="s04", view=FRONT_LEFT, context=[axle.common(cyl_x(30, X_AXLE_END - 40, X_AXLE_END + 1, 0, 0))],
         parts=[(axle_plug, PRINT, O), (nut_m6, METAL, V(14, 0, 0)), (axle_cap, METAL, V(32, 0, 0))],
         moves=[{1: O}, {2: O}]),
    dict(id="s05", view=FRONT_LEFT, context=valve_stack,
         parts=[(axle, METAL, V(40, 0, 0)), ([(axle_plug, PRINT), (axle_cap, METAL)], None, V(80, 0, 0))],
         moves=[{}, {0: O}, {1: O}, {}]),
    dict(id="s06", view=FRONT_LEFT, context=[axle],
         parts=[(hub, PRINT, V(-30, 0, 0)), (barrels, TUBE, V(0, 0, 0)), (front_plate, PRINT2, V(30, 0, 0)),
                (oring_faces, RUBBER, V(-55, 0, 0))],
         moves=[{}, {0: O, 2: O}, {}, {3: O}, {}]),
    dict(id="s07", view=(-0.45, 0.55, -0.7), context=[],
         parts=[(sector_r, PRINT2, O), (pawl_spring, SPRING, V(12, 0, 0)), (pawl_r, PRINT, V(26, 0, 0))],
         moves=[{1: O}, {2: O}]),
    dict(id="s08", view=RIGHT_FRONT, context=[sector_r],
         parts=[(sl_r, PRINT3, O), (guide_rod, METAL, V(0, 0, -40)), (sl_pin, METAL, V(22, 0, 0))],
         moves=[{2: O}, {1: O}]),
    dict(id="s09", view=OBLIQUE, context=[],
         parts=[(hammer_r, PRINT2, O), (mainsprings, SPRING, V(0, -28, 0)), (shaft, METAL, V(0, 60, 0)),
                (crank_pin.copy(), METAL, V(0, 22, 0))],
         moves=[{1: O}, {3: O}, {}]),
    dict(id="s10", view=OBLIQUE, context=[frame.common(box(TRIGGER_CHEEKS["x"][0] - 8, TRIGGER_CHEEKS["x"][1] + 8, -12, 12,
                                                       fz[0], TRIGGER_PIVOT.z + 6))],
         parts=[(trig_r, PRINT, O), (pivot_screw, METAL, V(0, -18, 0)), (pivot_nut, METAL, V(0, 16, 0))],
         moves=[{1: O, 2: O}]),
    dict(id="s11", view=OBLIQUE, context=[],
         parts=[(frame, PRINT, O), (stack, None, V(0, -80, 0)), ([(sl_r, PRINT3), (sl_pin, METAL), (guide_rod, METAL)], None, V(0, -70, 0)),
                ([(sector_r, PRINT2), (pawl_r, PRINT)], None, V(0, -70, 0)), ([(hammer_r, PRINT2), (mainsprings, SPRING)], None, V(0, -70, 0)),
                (shaft, METAL, V(0, 70, 0)), (trig_r, PRINT, O)],
         moves=[{1: O}, {2: O}, {3: O}, {4: O, 5: O}, {}, {}]),
    dict(id="s12", view=LEFT, context=cage_all,
         parts=[(block, TUBE, V(80, 0, 0)), (washer, RUBBER, V(95, 0, 0)), (nose, PRINT2, V(110, 0, 0)),
                (top_strap, PRINT, V(0, 0, 35)), (axle_cap, METAL, V(140, 0, 0))],
         moves=[{0: O, 1: O, 2: O}, {3: O}, {4: O}, {}]),
    dict(id="s13", view=(-1.0, 0.25, -0.35), context=[],
         parts=[(detent_box, PRINT, O), (det_spring, SPRING, _out * -16), (bolt_r, PRINT3, _out * -32)],
         moves=[{1: O}, {2: O}]),
    dict(id="s14", view=OBLIQUE, context=cage_all + [block, top_strap],
         parts=[(side_plate, PRINT, V(0, -45, 0)), ([(detent_box, PRINT2), (bolt_r, PRINT3)], None, V(0, -45, -30))],
         moves=[{1: V(0, -45, 0)}, {0: O, 1: O}, {}]),
    dict(id="s15", view=(0.35, 0.55, -0.75), context=[],
         parts=[(vent_body.fuse(vent_plunger), VALVE_C, O), (fit["A"], BRASS, V(0, -16, 0)), (fit["R"], BRASS, V(0, 16, 0)),
                (fit["P"], BRASS, V(0, 16, 0))],
         moves=[{}, {1: O}, {2: O}, {3: O}]),
    dict(id="s16", view=LEFT, context=[valve_body, valve_cap, frame, grip],
         parts=[(valves, VALVE_C, O), (pilot_line, TUBE, None), (gauge_line, TUBE, None), (tee, BRASS, None),
                (supply_line, HOSE, None), ([(gauge, BRASS), (gauge_glass, (0.95, 0.95, 0.9))], None, None)],
         moves=[{1: "show", 3: "show"}, {2: "show", 5: "show"}, {4: "show"}]),
    dict(id="s17", view=(0.72, -0.5, -0.48), context=[],
         parts=[(grip_left, PRINT, O), (valves, VALVE_C, V(0, 0, 35)), (supply_line, HOSE, None), (dowels, METAL, V(0, 22, 0)),
                (grip_right, PRINT2, V(0, 50, 0))],
         moves=[{2: "show"}, {1: O, 3: O}, {4: O}]),
    dict(id="s18", view=LEFT, context=cage_all + [block, top_strap, side_plate, detent_box, valves],
         parts=[(grip, PRINT, V(0, 0, -30)), (guard, PRINT2, V(0, 0, -50))],
         moves=[{0: O}, {1: O}, {}]),
]


def tint(c):
    return tuple(0.55 * x + 0.45 * g for x, g in zip(c, (0.25, 0.85, 0.2)))


def render(file, items, context, view, scratch):
    """items: [(shape, colour, offset, tinted)]; a None offset is not drawn."""
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
        if off.Length > 1e-6:                                    # a faint line back to where it goes
            ln = scratch.addObject("Part::Feature", "L%d" % k)
            ln.Shape = Part.makeCylinder(0.35, off.Length, sh.BoundBox.Center, off)
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
    c.save(os.path.join(GUIDE, file + ".jpg"), quality=84)
    os.remove(tmp)


def frames_of(sub):
    """The file of each frame: frame 0, then one per checkbox (a move that changes nothing reuses the last)."""
    offs = [p[2] for p in sub["parts"]]
    states, hots = [list(offs)], [set()]
    for mv in sub["moves"]:
        st = list(states[-1])
        for i, to in mv.items():
            st[i] = O if to == "show" else to
        states.append(st)
        hots.append(set(mv))
    files, last = [], None
    for f, (st, hot) in enumerate(zip(states, hots)):
        if f > 0 and not hot:
            files.append(last)
            continue
        name = "%s_%d" % (sub["id"], f)
        items = []
        for (shape, col, _), off, i in zip(sub["parts"], st, range(len(st))):
            if off is None:
                continue
            for sh, c in (shape if isinstance(shape, list) else [(shape, col)]):
                items.append((sh, c, off, i in hot))
        render(name, items, sub["context"], sub["view"], scratch)
        files.append(name)
        last = name
    return files


if "guide_render" in App.listDocuments():
    App.closeDocument("guide_render")
scratch = App.newDocument("guide_render")
Gui.ActiveDocument = Gui.getDocument("guide_render")
pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
anim = pv.GetBool("UseNavigationAnimations", True)
pv.SetBool("UseNavigationAnimations", False)
manifest = {}
try:
    for sub in SUBS:
        manifest[sub["id"]] = ["g/%s.jpg" % f for f in frames_of(sub)]
finally:
    pv.SetBool("UseNavigationAnimations", anim)
import json
with open(os.path.join(GUIDE, "frames.json"), "w") as f_:
    json.dump(manifest, f_, indent=1)
print("guide renders: %d sub-steps, %d frames" % (len(manifest), len({x for v_ in manifest.values() for x in v_})))
