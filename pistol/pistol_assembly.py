# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the lever-action mechanism inside the Skaven look.

pistol/mech_layout.py's mechanism (v1.1 valve, lock, block, pawl sector,
slider, detent, lever, trigger) with full-length barrels, dressed after
pistol_look_skaven.py and fitted round it:

    frame ..... a rounded shell round the valve, the lock, the slider and
                the lever's pivot, open towards the block; slots for the
                trigger and the lever are cut by sweeping them through it
    grip ...... the rag-wrapped wooden grip from the frame's rear foot,
                warpstone pommel with the hose; the two trigger valves sit
                at its top, behind the trigger (mini 3/2 push-button
                valves here: two M3R110 do not fit a grip)
    lever ..... the trigger guard is the lever (no separate finger loop:
                it would run into the grip)

Shapes for the look and for checking that the mechanism fits; not parts.
Frame: x forward, y to the right seen from behind, z up.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/pistol_assembly.py').read())
"""

import math
import os
import random

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
STUB = 160.0                                    # full-length barrels
exec(open(os.path.join(REPO, "pistol", "mech_layout.py")).read())

NAME = "pistol_assembly"
random.seed(7)

# ---------------------------------------------------------------- parameters
FRAME = dict(x=(X_BODY_TOP - BODY_H - CAP_T - 3.0, -1.0), y=(-37.0, 37.0), z=(-88.0, 24.0))
FRAME_WALL = 3.0
FRAME_FILLET = 12.0
GRIP_START = V(FRAME["x"][0] - 12, 0, -64)      # grip axis: its front edge clears the trigger and the lever
GRIP_ANGLE = 36.0
GRIP_LEN = 118.0
GRIP_SECTIONS = ((0.0, 48, 34), (0.4, 40, 31), (0.8, 44, 33), (1.0, 48, 36))   # t, depth, width
MINI_VALVE = (14.0, 36.0)                       # Ø, length: 3/2 push-button valve, envelope
MINI_VALVES = ((-8.5, -58.0), (8.5, -60.0))     # y, plunger tip x: stage 1 (lock) meets the blade first
MINI_Z = -82.0

RUST, IRON, DIRTY = (0.40, 0.24, 0.14), (0.24, 0.23, 0.22), (0.45, 0.43, 0.40)
COPPER, BRASS, WOOD, RAG = (0.30, 0.55, 0.44), (0.55, 0.45, 0.22), (0.26, 0.16, 0.09), (0.48, 0.42, 0.30)
WARP, GLASS = (0.35, 0.95, 0.20), (0.70, 0.85, 0.75)


def spike(base, direction, length, r):
    return Part.makeCone(r, 0, length, base, direction)


def crystal(center, axis, length, r):
    axis = V(axis).normalize()
    side = axis.cross(ZA if abs(axis.z) < 0.9 else XA).normalize()
    up = axis.cross(side).normalize()
    tip0, tip1 = center - axis * (length * 0.35), center + axis * (length * 0.65)
    ring = [center + side * r, center + up * r, center - side * r * 0.8, center - up * r * 0.9]
    faces = []
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        faces += [Part.Face(Part.makePolygon([tip1, a, b, tip1])), Part.Face(Part.makePolygon([tip0, b, a, tip0]))]
    return Part.Solid(Part.Shell(faces))


def rivets(points, r=1.6):
    return Part.makeCompound([Part.makeSphere(r, p) for p in points])


def pipe_along(points, r):
    c = Part.BSplineCurve()
    c.interpolate(points)
    t0 = c.tangent(c.FirstParameter)[0]
    return Part.Wire(c.toShape()).makePipeShell([Part.Wire(Part.makeCircle(r, points[0], t0))], True, True)


# ---------------------------------------------------------------- frame shell
fx, fy, fz = FRAME["x"], FRAME["y"], FRAME["z"]
outer = box(fx[0], fx[1], fy[0], fy[1], fz[0], fz[1])
outer = outer.makeFillet(FRAME_FILLET, outer.Edges)
inner = box(fx[0] + FRAME_WALL, fx[1] + 10, fy[0] + FRAME_WALL, fy[1] - FRAME_WALL, fz[0] + FRAME_WALL, fz[1] - FRAME_WALL)
frame = outer.cut(inner)
# Slot in the bottom wall where the lever's strut and the trigger pass, over their whole strokes
sweep = [pose(dict(lever=lv, block=0.0, bend=0.0, trig=tg)) for lv in (0.0, 0.25, 0.5, 0.75, 1.0) for tg in (0.0, 1.0)]
slab = box(fx[0], fx[1], -10, 10, fz[0] - 1, fz[0] + FRAME_WALL + 1)
xs = []
for st_ in sweep:
    for n_ in ("Lever", "Trigger"):
        c_ = st_[n_].common(slab)
        if c_.Volume > 1e-3:
            xs += [c_.BoundBox.XMin, c_.BoundBox.XMax]
frame = frame.cut(box(min(xs) - 1.5, max(xs) + 1.5, -4.5, 4.5, fz[0] - 1, fz[0] + FRAME_WALL + 1))
pilot_hole = cyl_x(16, fx[0] - 1, fx[0] + FRAME_WALL + 1, 0, Z_FIRE)          # the cap's G1/8 fitting
frame = frame.cut(pilot_hole)

# ---------------------------------------------------------------- grip, trigger valves
a = math.radians(GRIP_ANGLE)
gd = V(-math.cos(a), 0, -math.sin(a))
gn = V(-math.sin(a), 0, math.cos(a))
grip = Part.makeLoft([Part.Wire(Part.Ellipse(GRIP_START + gd * (GRIP_LEN * t) + gn * (h / 2),
                                             GRIP_START + gd * (GRIP_LEN * t) + YA * (w / 2),
                                             GRIP_START + gd * (GRIP_LEN * t)).toShape()) for t, h, w in GRIP_SECTIONS],
                     True, False)
grip = grip.cut(outer)                          # the frame's foot covers its top
mini_valves = Part.makeCompound([cyl_x(MINI_VALVE[0], tip - MINI_VALVE[1], tip - 3, y, MINI_Z)
                                 .fuse(cyl_x(5, tip - 3.01, tip, y, MINI_Z)) for y, tip in MINI_VALVES])
frame = frame.cut(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z)
                                     for y, tip in MINI_VALVES]))         # through the frame's rear wall
# Tang: the frame runs on back under the valve cap into the grip, round the trigger valves
pod = box(min(t for _, t in MINI_VALVES) - MINI_VALVE[1] - 4, fx[0] + 6, -19, 19, MINI_Z - 9, MINI_Z + 10)
pod = pod.makeFillet(5.0, pod.Edges).cut(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z)
                                                             for y, tip in MINI_VALVES])).cut(inner)
rags = []
for t, tw in ((0.22, 9), (0.45, 12), (0.68, 8), (0.88, 10)):
    c = GRIP_START + gd * (GRIP_LEN * t)
    h, w = 44 - 4 * t + 3, 33 + 3
    r = Part.makeLoft([Part.Wire(Part.Ellipse(c + gn * (h / 2), c + YA * (w / 2), c).toShape()),
                       Part.Wire(Part.Ellipse(c + gd * tw + gn * (h / 2), c + gd * tw + YA * (w / 2), c + gd * tw).toShape())],
                      True, False)
    r.rotate(c, gd, random.uniform(-15, 15))
    rags.append(r.cut(outer))
c_end = GRIP_START + gd * GRIP_LEN
pommel = Part.makeCone(20, 11, 10, c_end, gd)
claws = [spike(c_end + gd * 4 + V(0, 15 * math.cos(math.radians(k)), 15 * math.sin(math.radians(k))),
               gd + V(0, 0.8 * math.cos(math.radians(k)), 0.8 * math.sin(math.radians(k))), 14, 2.2) for k in (0, 120, 240)]
warp_pommel = Part.makeCompound([crystal(c_end + gd * 14, gd + V(0.2, 0.3, 0.1), 40, 11),
                                 crystal(c_end + gd * 11 + V(0, 8, 5), gd + V(-0.2, 0.8, 0.5), 28, 7),
                                 crystal(c_end + gd * 11 + V(0, -8, -3), gd + V(0.3, -0.7, -0.3), 24, 6)])
hose = Part.makeCylinder(3, 70, c_end + gd * 20, gd)

# ---------------------------------------------------------------- dress: block straps, frame plates, crest, hammer, vial, gauge, pilot pipe
block_d = 2 * HUB_R
straps, spikes, strap_rivets = [], [], []
for x0, w, tilt in ((HUB_X0 + 2, 12, 0), (95, 8, 4), (HUB_X0 + HUB_T + STUB - 14, 10, -3)):
    s = cyl_x(block_d + 5, x0, x0 + w).cut(cyl_x(block_d - 1, x0 - 1, x0 + w + 1))
    s.rotate(V(x0 + w / 2, 0, 0), YA, tilt)
    straps.append(s)
    for k in range(7):
        q = math.radians(360.0 / 7 * k + random.uniform(-10, 10))
        strap_rivets.append(V(x0 + w / 2, (block_d / 2 + 2.6) * math.cos(q), (block_d / 2 + 2.6) * math.sin(q)))
    for a_deg in ((30, 150) if x0 < 20 else (90, 210) if x0 > 100 else ()):
        q = math.radians(a_deg)
        dv = V(0, math.cos(q), math.sin(q))
        spikes.append(spike(V(x0 + w / 2, 0, 0) + dv * (block_d / 2 + 2), dv + V(0.3, 0, 0), 16, 4))
plates, plate_rivets = [], []
for side, rot, dx, dz in ((1, 7, 4, 6), (-1, -5, -2, -4)):
    y0 = fy[1] if side > 0 else fy[0] - 3
    p_ = box(fx[0] + 14 + dx, fx[0] + 56 + dx, y0, y0 + 3, Z_FIRE - 16 + dz, Z_FIRE + 22 + dz)
    p_.rotate(V(fx[0] + 35, 0, Z_FIRE), YA, rot)
    plates.append(p_)
    yb = y0 + (3.5 if side > 0 else -0.5)
    plate_rivets += [V(fx[0] + 14 + dx + px, yb, Z_FIRE - 16 + dz + pz) for px, pz in ((5, 4), (37, 6), (5, 34), (37, 32))]
crest_pts = [(fx[0] + 6, 0)]
for k in range(7):
    crest_pts += [(fx[0] + 12 + k * 8.5, 13 + random.uniform(0, 6)), (fx[0] + 16 + k * 8.5, 3)]
crest_pts += [(fx[1] - 14, 0)]
crest = Part.Face(Part.makePolygon([V(px, -1.5, fz[1] - 1 + pz) for px, pz in crest_pts]
                                   + [V(crest_pts[0][0], -1.5, fz[1] - 1)])).extrude(V(0, 3, 0))
hp = V(fx[0] + 6, 0, fz[1] - 4)
hammer = Part.makeCylinder(7, 12, hp - V(0, 6, 0), YA)
claw = Part.makeTorus(11, 3.2, hp + V(-11, 0, 0), YA).common(box(hp.x - 30, hp.x, -10, 10, hp.z, hp.z + 30))
hammer = hammer.fuse(claw).fuse(spike(hp + V(-22, 0, 0), V(0.2, 0, -1), 10, 3))
vc = V(fx[1] - 22, -16, fz[1] - 1)
vial = Part.makeCylinder(8, 30, vc, ZA)
vial_caps = Part.makeCylinder(10, 4, vc - V(0, 0, 2), ZA).fuse(Part.makeCylinder(10, 4, vc + V(0, 0, 29), ZA))
cage = Part.makeCompound([Part.makeCylinder(1.2, 32, vc + V(10 * math.cos(math.radians(q)), 10 * math.sin(math.radians(q)), 0), ZA)
                          for q in (0, 120, 240)])
vial_stone = crystal(vc + V(0, 0, 14), V(0.2, 0.1, 1), 24, 5)
gp = V(fx[0] + 30, fy[1] + 18, Z_FIRE + 30)
gauge = Part.makeCylinder(12, 8, gp, YA).fuse(Part.makeCylinder(3, 16, gp - V(0, 15, 0), YA))
gauge_glass = Part.makeCylinder(10.5, 1, gp + V(0, 8, 0), YA)
needle = box(gp.x, gp.x + 9, gp.y + 9, gp.y + 9.8, gp.z - 0.6, gp.z + 0.6)
needle.rotate(gp, YA, -35)
pilot_pipe = pipe_along([V(fx[0] - 6, 0, Z_FIRE), V(fx[0] - 16, -22, Z_FIRE - 14), V(fx[0] - 14, -26, MINI_Z - 2),
                         V(fx[0] + 2, -FRAME["y"][1] + 2, MINI_Z)], 2.6)
axle_cap = Part.makeCone(9, 3, 10, V(HUB_X0 + HUB_T + STUB + 20, 0, 0), XA)

# ---------------------------------------------------------------- checks
rest = pose(REST)
moving = ("Sector", "Pawl", "Slider", "Pin", "Bolt", "Lever", "Sleeve", "Trigger")
worst = {}
for lv in (0.0, 0.25, 0.5, 0.75, 1.0):
    for tg in (0.0, 1.0):
        st = pose(dict(lever=lv, block=sector_turn(lv), bend=0.0, trig=tg))
        for n in moving:
            for other_name, other in (("frame", frame), ("grip", grip), ("tang", pod), ("mini valves", mini_valves)):
                if n == "Trigger" and other_name == "mini valves":
                    continue                     # it presses their plungers by design
                v_ = st[n].common(other).Volume
                worst[(n, other_name)] = max(worst.get((n, other_name), 0.0), v_)
fixed_hits = {"valve/frame": valve_body.common(frame).Volume + valve_cap.common(frame).Volume,
              "lock/frame": lock_housing.common(frame).Volume, "mini valves/frame": mini_valves.common(frame).Volume}
inside = mini_valves.common(grip.fuse(outer).fuse(pod.fuse(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z) for y, tip in MINI_VALVES])))).Volume / mini_valves.Volume
blade_back = lambda tg: pose(dict(lever=1.0, block=0.0, bend=0.0, trig=tg))["Trigger"].common(
    box(-200, TRIGGER_PIVOT.x - 3, -10, 10, MINI_Z - 8, MINI_Z + 8)).BoundBox.XMin
report = [NAME, "  mechanism vs dress (worst over lever and trigger strokes, mm3):"]
report += ["    %-8s / %-11s %.1f" % (k[0], k[1], v_) for k, v_ in sorted(worst.items()) if v_ > 0.05] or ["    none"]
report += ["  fixed: " + ", ".join("%s %.1f" % kv for kv in fixed_hits.items()),
           "  trigger valves inside grip/frame: %.0f %%" % (inside * 100),
           "  trigger blade back at the valves' height: rest x %.1f, pulled x %.1f; plungers at %s"
           % (blade_back(0.0), blade_back(1.0), " / ".join("%.0f" % t for _, t in MINI_VALVES)),
           "  overall: %.0f mm long (pommel to muzzle), %.0f mm high, block Ø%.0f"
           % (HUB_X0 + HUB_T + STUB + 30 - (c_end + gd * 30).x, fz[1] + 30 - (c_end + gd * 30).z, block_d)]
print("\n".join(report))

# ---------------------------------------------------------------- document
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)


def add(group, name, shape, col, transp=0):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    group.addObject(o)
    if App.GuiUp:
        o.ViewObject.ShapeColor = col
        o.ViewObject.Transparency = transp
    return o


g_mech = doc.addObject("App::DocumentObjectGroup", "Mechanism")
for n, s_, c, tr in (("Valve_body_v11", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap_v11", valve_cap, (0.45, 0.65, 0.85), 0),
                     ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 0), ("Chamber_axle", axle, (0.7, 0.7, 0.7), 0),
                     ("Trigger_valves", mini_valves, (0.3, 0.3, 0.8), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame", frame, IRON, 0), ("Tang", pod, IRON, 0), ("Grip", grip, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
                     ("Pommel", pommel, IRON, 0), ("Pommel_claws", Part.makeCompound(claws), DIRTY, 0),
                     ("Warpstone_pommel", warp_pommel, WARP, 0), ("Hose", hose, (0.08, 0.08, 0.08), 0),
                     ("Straps", Part.makeCompound(straps), IRON, 0), ("Strap_rivets", rivets(strap_rivets), DIRTY, 0),
                     ("Spikes", Part.makeCompound(spikes), DIRTY, 0), ("Plates", Part.makeCompound(plates), RUST, 0),
                     ("Plate_rivets", rivets(plate_rivets), DIRTY, 0), ("Crest", crest, DIRTY, 0), ("Hammer", hammer, IRON, 0),
                     ("Vial_glass", vial, GLASS, 65), ("Vial_caps", vial_caps, BRASS, 0), ("Vial_cage", cage, IRON, 0),
                     ("Warpstone_vial", vial_stone, WARP, 0), ("Gauge", gauge, BRASS, 0), ("Gauge_glass", gauge_glass, (0.9, 0.9, 0.85), 0),
                     ("Gauge_needle", needle, (0.6, 0.05, 0.05), 0), ("Pilot_pipe", pilot_pipe, COPPER, 0),
                     ("Axle_cap", axle_cap, IRON, 0)):
    add(g_dress, n, s_, c, tr)
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
