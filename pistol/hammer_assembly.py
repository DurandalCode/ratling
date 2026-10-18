# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the thumb-hammer mechanism inside the Skaven look.

pistol/hammer_layout.py's mechanism (v1.1 valve, lock pusher, block, pawl
sector, slider, detent, hammer, one-stage trigger) with 200 mm barrels,
dressed as pistol_assembly.py (the lever variant):

    frame ..... a rounded shell round the valve, the lock, the slider with
                its bracket and the hammer behind the cap; wide enough for
                the hammer's crank and the bracket on the right; the spur
                comes out of the top rear through a slot over its swing,
                the trigger through the bottom
    grip ...... the rag-wrapped wooden grip, warpstone pommel with the
                hose; the vent valve sits at its top, behind the trigger

Shapes for the look and for checking that the mechanism fits; not parts.
Frame: x forward, y to the right seen from behind, z up.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/hammer_assembly.py').read())
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
try:
    BARREL_TUBE                                 # or set before exec
except NameError:
    BARREL_TUBE = 200.0                         # barrel tube as cut (13 mm of it in the hub)
try:
    VALVE                                       # 'v11' or 'v13', see mech_layout.py
except NameError:
    VALVE = "v13"
HUB_T_HAMMER = 14.0                             # the block's rear disc (hammer_layout.py)
STUB = BARREL_TUBE - (HUB_T_HAMMER - 9.0)       # the tube from the rear disc's seat (9 deep) to the muzzle
exec(open(os.path.join(REPO, "pistol", "hammer_layout.py")).read())

NAME = "pistol_hammer_assembly"
random.seed(7)

# ---------------------------------------------------------------- parameters
FRAME = dict(x=(HAMMER_PIVOT.x - HAMMER_R - 8.0, -1.0), y=(-45.0, 45.0), z=(-76.0, 31.0))   # round the hammer and the raised slider
EVA_T = 3.0                         # the frame's look: an EVA skin this thick over a printed cage
CAGE_T = 3.0
CAGE_WINDOWS = dict(side=((-40.0, -16.0), (-60.0, 12.0)), top=((-50.0, -18.0), 24.0), bottom=((-40.0, -10.0), 24.0))
STANDOFFS = ((-48.0, -45.0, (1, -1)), (-48.0, -5.0, (-1,)))   # x, z, sides: the cage to the valve body (not where the crank runs)
# The cage opens on the left: the mechanism goes in from that side, and a side plate closes it on six ST2.9
# into bosses on the cage's top and bottom walls. The plate is also the hammer shaft's left bearing and
# carries the detent's bracket.
SIDE_BOSSES = ((-50.0, 22.0), (-10.0, 22.0), (-90.0, 6.0), (-90.0, -67.0), (-50.0, -67.0), (-10.0, -67.0))   # x, z: 1 mm into the walls
BOSS_D, BOSS_L = 8.0, 10.0
TRIGGER_CHEEKS = dict(x=(-56.0, -48.0), y=(3.3, 7.0))          # the trigger's pivot (an M3 screw and nut) between them
GRIP_SCREWS = ((-96.0, 29.0), (-96.0, -29.0), (-64.0, 29.0), (-64.0, -29.0))   # x, y: grip/tang to the cage's floor, outside the valve
VALVE_BOX_Y = 33.0                  # the tang is a box under the frame round the vent valve and its fittings
GUARD_TAB = dict(x=(-27.0, -13.0), y=5.0, t=3.0)                # the guard's front tab under the floor
SPUR_SLOT = dict(a=(58.0, 210.0), r=SPUR[1] + 10.0, y=6.5)    # the spur's swing out of the top rear
FRAME_FILLET = 12.0
REAR = dict(x=-60.0, top=15.0)      # behind this the frame steps down: the hammer stands up out of it

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
def envelope(i, open_front=False):
    """The frame's outline shrunk by i: tall in front, stepped down behind REAR. open_front: as a cavity, run on
    forward into the block and square (it is cut away)."""
    if open_front:
        return (box(REAR["x"] + 1, fx[1] + 10, fy[0] + i, fy[1] - i, fz[0] + i, fz[1] - i)
                .fuse(box(fx[0] + i, REAR["x"] + 10, fy[0] + i, fy[1] - i, fz[0] + i, REAR["top"] - i)))
    f_ = box(REAR["x"] - 2, fx[1], fy[0] + i, fy[1] - i, fz[0] + i, fz[1] - i)
    r_ = box(fx[0] + i, REAR["x"] + 10, fy[0] + i, fy[1] - i, fz[0] + i, REAR["top"] - i)
    r = max(FRAME_FILLET - i, 1.0)
    return f_.makeFillet(r, f_.Edges).fuse(r_.makeFillet(r, r_.Edges)).removeSplitter()


outer = envelope(0.0)
skin_in = envelope(EVA_T)
inner = envelope(EVA_T + CAGE_T, open_front=True)
skin = outer.cut(envelope(EVA_T, open_front=True))           # EVA, glued over the cage
frame = skin_in.cut(inner)                                    # the printed cage, windows cut below
y_in = fy[1] - EVA_T - CAGE_T
(wx, wz), (tx, ty), (bx, by) = CAGE_WINDOWS["side"], CAGE_WINDOWS["top"], CAGE_WINDOWS["bottom"]
win = box(wx[0], wx[1], fy[0] - 1, fy[1] + 1, wz[0], wz[1])
win = win.makeFillet(6.0, [e for e in win.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[-1].Point.y) > 1])
frame = frame.cut(win.common(box(fx[0], fx[1], -100, -y_in + 0.5, -200, 200).fuse(box(fx[0], fx[1], y_in - 0.5, 100, -200, 200))))
frame = frame.cut(box(tx[0], tx[1], -ty, ty, fz[1] - 10, fz[1] + 1)).cut(box(bx[0], bx[1], -by, by, fz[0] - 1, fz[0] + 10))
def _standoffs(sign):
    out = []
    for x_, z_, sides in STANDOFFS:
        if sign in sides:
            s_ = Part.makeCylinder(5.0, y_in - 20 + 0.5, V(x_, sign * (y_in + 0.5), z_), V(0, -sign, 0)).cut(valve_body)
            out.append(max(s_.Solids, key=lambda q: q.Volume))          # up to the valve's face, no crumbs past it
    return out


standoffs = Part.makeCompound(_standoffs(1) + _standoffs(-1))
frame = frame.fuse(Part.makeCompound(_standoffs(1))).removeSplitter()      # the left ones go on the side plate
# Slot in the bottom wall for the trigger over its stroke
slab = box(fx[0], fx[1], -16, 16, fz[0] - 1, fz[0] + EVA_T + CAGE_T + 1)
xs = []
for tg in (0.0, 0.5, 1.0):
    c_ = trigger_h(tg).common(slab)
    if c_.Volume > 1e-3:
        xs += [c_.BoundBox.XMin, c_.BoundBox.XMax]
if xs:
    t_slot = box(min(xs) - 1.5, max(xs) + 1.5, -5, 5, fz[0] - 1, fz[0] + EVA_T + CAGE_T + 1)
    frame, skin = frame.cut(t_slot), skin.cut(t_slot)
# Slot in the top rear for the spur: a pie over its swing, round the pivot
H_ = HAMMER_PIVOT
pie = [V(H_.x, -SPUR_SLOT["y"], H_.z)] + [V(H_.x + SPUR_SLOT["r"] * math.cos(math.radians(q)), -SPUR_SLOT["y"],
                                            H_.z + SPUR_SLOT["r"] * math.sin(math.radians(q)))
                                          for q in [SPUR_SLOT["a"][0] + (SPUR_SLOT["a"][1] - SPUR_SLOT["a"][0]) * k / 12 for k in range(13)]]
spur_slot = Part.Face(Part.makePolygon(pie + [pie[0]])).extrude(V(0, 2 * SPUR_SLOT["y"], 0))
frame, skin = frame.cut(spur_slot), skin.cut(spur_slot)
pilot_hole = cyl_x(16, fx[0] - 1, fx[0] + EVA_T + CAGE_T + 1, 0, Z_FIRE)          # the cap's G1/8 fitting
frame, skin = frame.cut(pilot_hole), skin.cut(pilot_hole)

# ---------------------------------------------------------------- grip, trigger valves
a = math.radians(GRIP_ANGLE)
gd = V(-math.cos(a), 0, -math.sin(a))
gn = V(-math.sin(a), 0, math.cos(a))
grip = Part.makeLoft([Part.Wire(Part.Ellipse(GRIP_START + gd * (GRIP_LEN * t) + gn * (h / 2),
                                             GRIP_START + gd * (GRIP_LEN * t) + YA * (w / 2),
                                             GRIP_START + gd * (GRIP_LEN * t)).toShape()) for t, h, w in GRIP_SECTIONS],
                     True, False)
grip = grip.cut(outer)                          # the frame's foot covers its top
mini_valves = valves                            # hammer_layout's AirTAC vent valve
_a = AIRTAC
_vv = box(VENT_FRONT - _a["L"] - 0.5, VENT_FRONT + 0.5, -_a["W"] / 2 - _a["elbow"][1] - _a["elbow"][0] / 2 - 0.5,
          _a["W"] / 2 + _a["elbow"][1] + _a["elbow"][0] / 2 + 0.5, MINI_Z - _a["T"] / 2 - 0.5, MINI_Z + _a["T"] / 2 + 0.5)
_vv = _vv.fuse(valve_bodies)                    # the valve pokes up through the cage's floor, its A elbow higher
frame, skin = frame.cut(_vv), skin.cut(_vv)
# Tang: the frame runs on back under the valve cap into the grip, round the trigger valves
pod = box(VENT_FRONT - _a["L"] - 3.0, VENT_FRONT - 2.0, -VALVE_BOX_Y, VALVE_BOX_Y,
          MINI_Z - _a["T"] / 2 - 7.0, fz[0] + 1.0)
# Backstrap: closes the gap between the frame's rear wall and the grip's top, over the tang
strap = box(GRIP_START.x - 14, fx[0] + 4, -19, 19, fz[0] - 4, Z_FIRE - 4)
strap = strap.makeFillet(min(8.0, strap.BoundBox.XLength / 2 - 1), strap.Edges)
pod = pod.makeFillet(5.0, pod.Edges).fuse(strap).cut(_vv).cut(inner)
pod = pod.cut(Part.makeCompound([trigger_h(i / 6).translated(V(dx_, 0, 0)) for i in range(7) for dx_ in (-1.0, 0.0)]))   # the trigger's swing
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
# ---------------------------------------------------------------- air: supply up the grip, pilot to the cap, a tee to the gauge
# Supply (6/4 hose from the receiver) in through the pommel, up a channel in the grip to the vent valve's R
# port. Pilot (4/2.5 PU) from its A port back, up a channel in the backstrap, in through the cage's rear wall
# to the cap's G1/8 push-in. The pilot is the chamber's pressure once charged: a tee on it feeds the gauge,
# out through the side plate on the left, where the shooter sees it.
r_end, _ = vent_port("R")
a_end, _ = vent_port("A")
supply_pts = [c_end + gd * 70, c_end + gd * 15, GRIP_START + gd * (GRIP_LEN * 0.6), GRIP_START + gd * (GRIP_LEN * 0.3),
              V(-104, 6, -89), V(r_end.x - 10, r_end.y - 2, r_end.z - 3), V(r_end.x, r_end.y, r_end.z - 0.5)]
supply_line = pipe_along(supply_pts, 3.0)
pilot_pts = [V(a_end.x, a_end.y, a_end.z + 0.5), V(a_end.x, a_end.y, -50), V(-82, -14, -38), V(-82, -5, -31), V(-82, 0, Z_FIRE)]
pilot_line = pipe_along(pilot_pts, 2.0)
TEE = V(-82, -14, -38)
gauge_pts = [TEE, V(-83, -24, -40), V(-84, -fy[1] + 1, -40), V(-84, -fy[1] - 2, -40)]
gauge_line = pipe_along(gauge_pts, 2.0)
tee = Part.makeSphere(4.0, TEE)
hose = supply_line
air_cut = pipe_along(supply_pts, 3.6).fuse(pipe_along(pilot_pts, 2.6)).fuse(pipe_along(gauge_pts, 2.6)).fuse(Part.makeSphere(5.0, TEE))

# ---------------------------------------------------------------- trigger guard: from the frame's foot round the trigger into the grip
# A flat band (ellipse GUARD_SECTION, wide across) swept along a teardrop that leaves the frame's foot
# going down and forward and runs into the grip's front along it.
GUARD = [V(-20, 0, fz[0] + 5), V(-18, 0, -86), V(-23, 0, -100), V(-38, 0, -110), V(-58, 0, -109), V(-76, 0, -100),
         V(-90, 0, -90), V(-97, 0, -85)]
GUARD_SECTION = (3.2, 2.2)                      # half-width across (y), half-thickness in the loop's plane
_gc = Part.BSplineCurve()
_gc.interpolate(GUARD)
_t0 = _gc.tangent(_gc.FirstParameter)[0]
_n0 = _t0.cross(YA).normalize()
_prof = Part.Ellipse(GUARD[0] + YA * GUARD_SECTION[0], GUARD[0] + _n0 * GUARD_SECTION[1], GUARD[0])
guard = Part.Wire(_gc.toShape()).makePipeShell([Part.Wire(_prof.toShape())], True, True)   # Frenet: no twist in a plane
guard = Part.Solid(guard) if guard.ShapeType != "Solid" else guard
guard = guard.cut(outer)
_gt = GUARD_TAB
guard = guard.fuse(box(_gt["x"][0], _gt["x"][1], -_gt["y"], _gt["y"], fz[0] - _gt["t"], fz[0]))            # its front tab, under the skin
guard = guard.cut(Part.makeCylinder(1.25, _gt["t"] + 1, V(sum(_gt["x"]) / 2, 0, fz[0] - _gt["t"] - 0.5), ZA)).removeSplitter()

# ---------------------------------------------------------------- detent housing
detent_box = turned(box(HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2,
                        -HUB_R - 24, -HUB_R - 1.5), DETENT_ANGLE + 90)
detent_box = detent_box.cut(Part.makeCompound([bolt_shape(0.0), bolt_shape(30.0)])).cut(detent_spring_pocket())
_db = detent_box.BoundBox                       # a bracket from the cage's left side forward to it, clear of the block
# Its bracket is part of it and bolts to the side plate's outer face (2 x M3 x 12 + nuts): the plate prints flat.
detent_bracket = box(fx[1] - 8, _db.XMin + 0.9, _db.YMin + 2, -(fy[1] - EVA_T), _db.ZMax - 10, _db.ZMax)
detent_bracket = detent_bracket.cut(cyl_x(2 * 47.6, HUB_X0, 50)).cut(detent_box)
detent_bolts = Part.makeCompound([Part.makeCylinder(1.7, 30, V(fx[1] - 5.0, -fy[1] - 10, z_), YA)
                                  for z_ in (_db.ZMax - 2.5, _db.ZMax - 7.5)])
detent_box = detent_box.fuse(detent_bracket).cut(detent_bolts).removeSplitter()

# ---------------------------------------------------------------- the cage: open on the left, a side plate on screws
yi = fy[1] - EVA_T - CAGE_T                         # the cage walls' inner faces at y = +-yi
bosses = Part.makeCompound([Part.makeCylinder(BOSS_D / 2, BOSS_L, V(x_, -yi - 0.5, z_), YA) for x_, z_ in SIDE_BOSSES])
frame = frame.fuse(bosses)
tc = TRIGGER_CHEEKS
cheek_top = TRIGGER_PIVOT.z + 3.5
cheeks = Part.makeCompound([box(tc["x"][0], tc["x"][1], sg * tc["y"][0] if sg > 0 else -tc["y"][1],
                                tc["y"][1] if sg > 0 else -tc["y"][0], fz[0] + EVA_T + CAGE_T - 0.5, cheek_top)
                            for sg in (1, -1)])
cheeks = cheeks.cut(Part.makeCylinder(1.6, 2 * tc["y"][1] + 2, V(TRIGGER_PIVOT.x, -tc["y"][1] - 1, TRIGGER_PIVOT.z), YA))
frame = frame.fuse(cheeks)
# The slider's top meets a pad on the cage's ceiling at full cock: the hammer's back stop.
z_sl_top = slider_z(1.0) + 6.0
slider_stop = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], z_sl_top + 0.05, fz[1] - EVA_T - CAGE_T + 0.5)
# The mainsprings' fixed legs rest on a rib off the cage's rear wall, below and behind the hammer's hub.
spring_rib = box(fx[0] + EVA_T + CAGE_T - 0.5, HAMMER_PIVOT.x - 6.0, MAINSPRING["y"][0][0] - 1.0, -6.0,
                 HAMMER_PIVOT.z - 15.0, HAMMER_PIVOT.z - 10.5)
rod_boss = Part.makeCylinder(4.0, 4.0, V(GUIDE_ROD["x"], GUIDE_ROD["y"], fz[0] + EVA_T + CAGE_T - 0.5), ZA)   # the guide rod's foot
frame = frame.fuse(slider_stop).fuse(spring_rib).fuse(rod_boss)
frame = frame.cut(Part.makeCylinder(GUIDE_ROD["d"] / 2, GUIDE_ROD["z"][1] - GUIDE_ROD["z"][0], V(GUIDE_ROD["x"], GUIDE_ROD["y"], GUIDE_ROD["z"][0]), ZA))
shaft_holes = Part.makeCylinder(4.0, 2 * fy[1], V(HAMMER_PIVOT.x, -fy[1], HAMMER_PIVOT.z), YA)   # the axle: a press fit
frame = frame.cut(shaft_holes)
side_cut = box(fx[0] - 1, fx[1] + 1, -fy[1] - 1, -yi, fz[0] - 1, fz[1] + 1)
side_plate = frame.common(side_cut).fuse(Part.makeCompound(_standoffs(-1))).cut(detent_bolts)
frame = frame.cut(side_cut)
pilots = Part.makeCompound([Part.makeCylinder(1.25, BOSS_L - 1, V(x_, -yi, z_), YA) for x_, z_ in SIDE_BOSSES])
frame = frame.cut(pilots).removeSplitter()
side_plate = side_plate.cut(Part.makeCompound([Part.makeCylinder(1.7, 10, V(x_, -fy[1] - 1, z_), YA)
                                              for x_, z_ in SIDE_BOSSES])).removeSplitter()
skin = skin.cut(shaft_holes).cut(detent_box)

# ---------------------------------------------------------------- grip with the tang, on screws; the guard's tab
# The tang is part of the grip: one print, under the cage's floor, four ST2.9 down through the floor from
# inside the cage (side plate off). An ST2.9 from below holds the vent valve in its bore. The guard's front
# tab takes one ST2.9 down through the floor; its rear end is glued in a socket in the grip.
z_floor_top = fz[0] + EVA_T + CAGE_T
pod = pod.cut(outer)                                     # the tang sits under the skin
grip = grip.fuse(pod).removeSplitter()
grip_pilots = Part.makeCompound([Part.makeCylinder(1.25, 9.0, V(x_, y_, fz[0] - 9.0), ZA) for x_, y_ in GRIP_SCREWS])
floor_holes = Part.makeCompound([Part.makeCylinder(1.7, EVA_T + CAGE_T + 2, V(x_, y_, fz[0] - 1), ZA)
                                 for x_, y_ in GRIP_SCREWS + ((sum(GUARD_TAB["x"]) / 2, 0.0),)])
vent_screw = Part.makeCompound([Part.makeCylinder(1.6, 30.0, V(VENT_FRONT - d_, y_, MINI_Z - 20.0), ZA)
                                for d_, y_ in AIRTAC["holes"]])         # 3 x M3 x 30 through the valve into the tang, nuts below
grip = grip.cut(grip_pilots).cut(vent_screw)
frame, skin = frame.cut(floor_holes), skin.cut(floor_holes)

# ---------------------------------------------------------------- dress: block straps, frame plates, crest, hammer, vial, gauge, pilot pipe
block_d = 2 * HUB_R
straps, spikes, strap_rivets = [], [], []
for x0, w, tilt in ((HUB_X0 + 12, 12, 0), ((HUB_X0 + HUB_T + STUB) / 2, 8, 4), (HUB_X0 + HUB_T + STUB - 14, 10, -3)):
    s = cyl_x(block_d + 5, x0, x0 + w).cut(cyl_x(block_d - 1, x0 - 1, x0 + w + 1))
    s.rotate(V(x0 + w / 2, 0, 0), YA, tilt)
    straps.append(s)
    for k in range(7):
        q = math.radians(360.0 / 7 * k + random.uniform(-10, 10))
        strap_rivets.append(V(x0 + w / 2, (block_d / 2 + 2.6) * math.cos(q), (block_d / 2 + 2.6) * math.sin(q)))
plates, plate_rivets = [], []
for side, rot, dx, dz in ((1, 7, 4, 6), (-1, -5, -2, -4)):
    y0 = fy[1] if side > 0 else fy[0] - 3
    p_ = box(REAR["x"] + 2 + dx, REAR["x"] + 44 + dx, y0, y0 + 3, Z_FIRE - 16 + dz, Z_FIRE + 22 + dz)
    p_.rotate(V(REAR["x"] + 23, 0, Z_FIRE), YA, rot)
    plates.append(p_)
    yb = y0 + (3.5 if side > 0 else -0.5)
    plate_rivets += [V(REAR["x"] + 2 + dx + px, yb, Z_FIRE - 16 + dz + pz) for px, pz in ((5, 4), (37, 6), (5, 34), (37, 32))]
cx0 = H_.x + SPUR_SLOT["r"] * 0.35 + 8                 # the crest starts in front of the spur's slot
crest_pts = [(cx0, 0)]
for k in range(int((fx[1] - 14 - cx0 - 8) // 8.5)):
    crest_pts += [(cx0 + 6 + k * 8.5, 13 + random.uniform(0, 6)), (cx0 + 10 + k * 8.5, 3)]
crest_pts += [(fx[1] - 14, 0)]
crest = Part.Face(Part.makePolygon([V(px, -1.5, fz[1] - 1 + pz) for px, pz in crest_pts]
                                   + [V(crest_pts[0][0], -1.5, fz[1] - 1)])).extrude(V(0, 3, 0))
vc = V(fx[1] - 22, -16, fz[1] - 1)
vial = Part.makeCylinder(8, 30, vc, ZA)
vial_caps = Part.makeCylinder(10, 4, vc - V(0, 0, 2), ZA).fuse(Part.makeCylinder(10, 4, vc + V(0, 0, 29), ZA))
cage = Part.makeCompound([Part.makeCylinder(1.2, 32, vc + V(10 * math.cos(math.radians(q)), 10 * math.sin(math.radians(q)), 0), ZA)
                          for q in (0, 120, 240)])
vial_stone = crystal(vc + V(0, 0, 14), V(0.2, 0.1, 1), 24, 5)
gp = V(-84, -fy[1] - 4, -40)                    # the gauge on the left side, facing the shooter's side
gauge = Part.makeCylinder(12.5, 8, gp, -YA).fuse(Part.makeCylinder(3, 6, gp + V(0, 2, 0), -YA))
gauge_glass = Part.makeCylinder(11, 1, gp - V(0, 8, 0), -YA)
needle = box(gp.x, gp.x + 9, gp.y - 9.8, gp.y - 9, gp.z - 0.6, gp.z + 0.6)
needle.rotate(gp, YA, -35)
pilot_pipe = pilot_line
# ---------------------------------------------------------------- block supports: top strap to the axle's front end
# The block turns on the axle (hub bore at the back, the front plate's bore at the front). The axle is held
# by the valve alone, and the lock pushes the block forward at the shot: a top strap from the frame, over the
# block, down in front of the muzzles (over the top barrel only: the bottom one fires) to a plug glued in the
# axle's end with an M6 stud. A sleeve on the axle from the strap back to the front plate takes the thrust,
# through a washer.
X_MUZZLE = HUB_X0 + HUB_T + STUB
X_AXLE_END = X_MUZZLE + 20.0
STRAP = dict(w=10.0, t=6.0, z=(50.0, 56.0), x0=-12.0)
NOSE_OD = 28.0                                  # under the firing barrel's bore (r 15.1 from the axis)
WASHER_T = 1.0
s_w, s_t = STRAP["w"] / 2, STRAP["t"]
top_strap = (box(STRAP["x0"], X_AXLE_END + s_t, -s_w, s_w, STRAP["z"][0], STRAP["z"][1])
             .fuse(box(X_AXLE_END, X_AXLE_END + s_t, -s_w, s_w, 0, STRAP["z"][1]))
             .fuse(Part.makeCylinder(NOSE_OD / 2, s_t, V(X_AXLE_END, 0, 0), XA))
             .fuse(box(STRAP["x0"], HUB_X0 - 2.5, -s_w, s_w, fz[1] - 2, STRAP["z"][1])))   # its foot on the frame, short of the hub
top_strap = top_strap.cut(Part.makeCylinder(3.2, 20, V(X_AXLE_END - 1, 0, 0), XA))                 # the stud
STRAP_BOLTS = (-9.0, -5.0)          # x: 2 x M3 x 40 down through the foot into the cage's top, nuts inside
strap_bolts = Part.makeCompound([Part.makeCylinder(1.7, STRAP["z"][1] - fz[1] + 12, V(x_, 0, fz[1] - 10), ZA) for x_ in STRAP_BOLTS])
top_strap, frame, skin = top_strap.cut(strap_bolts), frame.cut(strap_bolts), skin.cut(strap_bolts)
nose = cyl_x(NOSE_OD, X_MUZZLE + WASHER_T, X_AXLE_END, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE, X_AXLE_END + 1, 0, 0))
washer = cyl_x(NOSE_OD, X_MUZZLE, X_MUZZLE + WASHER_T, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE - 1, X_MUZZLE + 2, 0, 0))
# The axle's front plug: glued flush into the tube (it closes the chamber), an M6 nut glued into a hex pocket in
# its face, the stud's hole behind it blind, so no air leaks along the thread.
PLUG_L, PLUG_HOLE = 20.0, 14.0
axle_plug = cyl_x(23.8 - 0.3, X_AXLE_END - PLUG_L, X_AXLE_END, 0, 0)
_hexr = 10.0 / 2 / math.cos(math.radians(30)) + 0.15                  # M6 nut, 10 across flats
_hex = Part.Face(Part.makePolygon([V(X_AXLE_END - 5.2, _hexr * math.cos(math.radians(60 * k)), _hexr * math.sin(math.radians(60 * k)))
                                   for k in range(7)])).extrude(V(5.3, 0, 0))
axle_plug = axle_plug.cut(_hex).cut(cyl_x(6.5, X_AXLE_END - PLUG_HOLE, X_AXLE_END, 0, 0))
axle_cap = Part.makeCylinder(3.0, PLUG_HOLE - 1 + s_t + 6, V(X_AXLE_END - PLUG_HOLE + 1, 0, 0), XA).fuse(   # M6 stud and a cap nut
    Part.makeCone(8, 5, 9, V(X_AXLE_END + s_t, 0, 0), XA))
strap_rivets += [V(x_, 0, STRAP["z"][1] + 0.3) for x_ in range(int(STRAP["x0"]) + 8, int(X_AXLE_END), 24)]
spikes += [spike(V(x_, 0, STRAP["z"][1] - 1), V(0.25, 0, 1), 14, 3.5) for x_ in (X_MUZZLE * 0.3, X_MUZZLE * 0.7)]
spikes += [spike(V(X_AXLE_END + s_t / 2, sd_ * s_w, STRAP["z"][1] - 8), V(0.3, sd_ * 1, 0.4), 14, 3.0) for sd_ in (-1, 1)]

grip, frame, side_plate, skin = grip.cut(air_cut), frame.cut(air_cut), side_plate.cut(air_cut), skin.cut(air_cut)
grip = max(grip.Solids, key=lambda q: q.Volume) if len(grip.Solids) > 1 else grip
# The grip prints as two halves split on y = 0, each flat on its cut face: the hose lies in the open channel,
# the halves close on it and on the vent valve, glued on three Ø3 steel dowels (6 mm into each half).
GRIP_DOWELS = [GRIP_START + gd * (GRIP_LEN * t) + gn * 13.0 for t in (0.3, 0.75)] + [V(VENT_FRONT - 36.0, 0, MINI_Z - 13.5)]
dowels = Part.makeCompound([Part.makeCylinder(1.6, 12.0, V(p_.x, -6.0, p_.z), YA) for p_ in GRIP_DOWELS])
grip = grip.cut(dowels)
grip_left = grip.common(box(-400, 100, -100, 0, -400, 100)).removeSplitter()
grip_right = grip.common(box(-400, 100, 0, 100, -400, 100)).removeSplitter()
for _g in (grip_left, grip_right):
    if not _g.isValid():
        _g.fix(0.01, 0.001, 0.1)                 # the split leaves a sliver edge on the loft: heal it

# ---------------------------------------------------------------- checks
def hit(a, b):
    try:
        return a.common(b).Volume
    except ValueError:                           # OCCT gives up on touching faces: nudge it
        return a.translated(V(0, 0.01, 0.01)).common(b).Volume


rest = pose(REST)
moving = ("Sector", "Pawl", "Slider", "Pin", "Bolt", "Hammer", "Sleeve", "Pusher", "Trigger")
worst = {}
for c in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
    for tg in (0.0, 1.0):
        st = pose(dict(cock=c, block=block_drive(c), bend=0.0, trig=tg))
        for n in moving:
            for other_name, other in (("frame", frame), ("side plate", side_plate), ("skin", skin), ("grip", grip),
                                      ("detent box", detent_box), ("guard", guard),
                                      ("air lines", Part.makeCompound([supply_line, pilot_line, gauge_line, tee])),
                                      ("vent valve", valve_bodies), ("crest", crest)):
                if n == "Bolt" and other_name == "detent box":
                    continue                     # it slides in it
                v_ = hit(st[n], other)
                worst[(n, other_name)] = max(worst.get((n, other_name), 0.0), v_)
sup = top_strap.fuse(nose).fuse(washer)
blk_hit = max(hit(turned(block, a_), sup) + hit(turned(Part.makeCompound(straps), a_), top_strap) for a_ in (0.0, 15.0, 30.0, 45.0))
fixed_hits = {"air lines/valve": hit(Part.makeCompound([pilot_line, gauge_line, tee]), valve_body)
              + hit(Part.makeCompound([pilot_line, gauge_line, tee]), valve_cap)
              + hit(Part.makeCompound([pilot_line, gauge_line, tee, supply_line]), vent_body),   # (their ends sit in the fittings)
              "air lines/springs+rib": hit(Part.makeCompound([pilot_line, gauge_line, tee]), mainsprings.fuse(spring_rib)),
              "slider/stop at full cock": hit(slider_h(1.0)[0], slider_stop.translated(V(0, 0, -0.1))),
              "side plate/valve": hit(side_plate, valve_body) + hit(side_plate, valve_cap) + hit(side_plate, lock_housing_h),
              "bosses/valve": hit(bosses, valve_body) + hit(bosses, valve_cap),
              "cheeks/valve": hit(cheeks, valve_body) + hit(cheeks, mini_valves),
              "block/supports": blk_hit, "strap/vial": hit(top_strap, vial.fuse(cage)) + hit(top_strap, crest),
              "valve/frame": valve_body.common(frame).Volume + valve_cap.common(frame).Volume,
              "lock/frame": lock_housing_h.common(frame).Volume, "vent valve/frame": mini_valves.common(frame).Volume}
inside = mini_valves.common(grip.fuse(outer).fuse(pod).fuse(_vv)).Volume / mini_valves.Volume
spur_out = lambda c: hammer_shape(c).cut(outer).Volume
report = [NAME, "  mechanism vs dress (worst over the hammer and trigger strokes, mm3):"]
report += ["    %-8s / %-11s %.1f" % (k[0], k[1], v_) for k, v_ in sorted(worst.items()) if v_ > 0.05] or ["    none"]
report += ["  fixed: " + ", ".join("%s %.1f" % kv for kv in fixed_hits.items()),
           "  vent valve inside grip/frame: %.0f %%" % (inside * 100),
           "  trigger guard: %.0f mm from the trigger at rest, %.0f pulled; loop %.0f x %.0f mm inside"
           % (trigger_h(0.0).distToShape(guard)[0], trigger_h(1.0).distToShape(guard)[0],
              max(p_.x for p_ in GUARD[:2]) - min(p_.x for p_ in GUARD) - 5.2, fz[0] - min(p_.z for p_ in GUARD) - 2.6),
           "  hammer outside the frame: %.0f mm3 forward, %.0f back" % (spur_out(0.0), spur_out(1.0)),
           "  overall: %.0f mm long (pommel to muzzle), %.0f mm high, block Ø%.0f"
           % (X_AXLE_END + s_t + 9 - min((c_end + gd * 30).x, spur_c.x), STRAP["z"][1] + 14 - (c_end + gd * 30).z, block_d),
           "  front support: strap %.0f x %.0f over the block (%.1f mm clear of its straps), down %.0f mm ahead of the muzzles;"
           " nose Ø%.0f clears the firing bore by %.1f mm"
           % (STRAP["w"], STRAP["t"], STRAP["z"][0] - (block_d / 2 + 2.5), X_AXLE_END - X_MUZZLE,
              NOSE_OD, R_RING - 23.8 / 2 - NOSE_OD / 2),
           "  barrels: tube %.0f, breech face to muzzle %.0f; chamber (the axle) %.0f mm of tube, ~%.0f cm3"
           % (BARREL_TUBE, HUB_T + STUB, axle.BoundBox.XLength,
              19.6 + (axle.BoundBox.XLength - 60) * math.pi / 4 * 23.8 ** 2 / 1000)]
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
                     ("Lock_housing", lock_housing_h, (0.5, 0.7, 0.5), 0), ("Chamber_axle", axle, (0.7, 0.7, 0.7), 0),
                     ("Vent_valve", mini_valves, (0.3, 0.3, 0.8), 0), ("Mainsprings", mainsprings, (0.6, 0.6, 0.65), 0),
                     ("Hammer_axle", shaft, (0.75, 0.75, 0.78), 0), ("Guide_rod", guide_rod, (0.75, 0.75, 0.78), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame", frame, IRON, 0), ("Frame_side", side_plate, (0.3, 0.29, 0.28), 0), ("Frame_skin", skin, IRON, 0), ("Trigger_guard", guard, IRON, 0),
                     ("Detent_housing", detent_box, IRON, 0), ("Grip_left", grip_left, WOOD, 0), ("Grip_right", grip_right, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
                     ("Pommel", pommel, IRON, 0), ("Pommel_claws", Part.makeCompound(claws), DIRTY, 0),
                     ("Warpstone_pommel", warp_pommel, WARP, 0), ("Hose", hose, (0.08, 0.08, 0.08), 0), ("Gauge_line", gauge_line, (0.15, 0.4, 0.8), 0),
                     ("Tee", tee, BRASS, 0),
                     ("Straps", Part.makeCompound(straps), IRON, 0), ("Strap_rivets", rivets(strap_rivets), DIRTY, 0),
                     ("Spikes", Part.makeCompound(spikes), DIRTY, 0), ("Plates", Part.makeCompound(plates), RUST, 0),
                     ("Plate_rivets", rivets(plate_rivets), DIRTY, 0), ("Crest", crest, DIRTY, 0),
                     ("Vial_glass", vial, GLASS, 65), ("Vial_caps", vial_caps, BRASS, 0), ("Vial_cage", cage, IRON, 0),
                     ("Warpstone_vial", vial_stone, WARP, 0), ("Gauge", gauge, BRASS, 0), ("Gauge_glass", gauge_glass, (0.9, 0.9, 0.85), 0),
                     ("Gauge_needle", needle, (0.6, 0.05, 0.05), 0), ("Pilot_pipe", pilot_pipe, (0.15, 0.4, 0.8), 0),
                     ("Axle_cap", axle_cap, IRON, 0), ("Axle_plug", axle_plug, (0.5, 0.5, 0.55), 0), ("Top_strap", top_strap, IRON, 0), ("Nose_sleeve", nose, IRON, 0),
                     ("Thrust_washer", washer, (0.85, 0.85, 0.8), 0)):
    add(g_dress, n, s_, c, tr)
doc.recompute()

# ---------------------------------------------------------------- what is printed, cut from EVA, or bought
# Print only what carries load or moves; the look is EVA foam; tubes, springs, valves, fasteners are bought.
MATERIAL = {
    "print": ("Valve_body_v11", "Valve_cap_v11", "Lock_housing", "Block", "Sector", "Pawl", "Slider", "Bolt", "Hammer",
              "Sleeve", "Pusher", "Trigger", "Frame", "Frame_side", "Detent_housing", "Grip_left", "Grip_right", "Trigger_guard",
              "Top_strap", "Axle_plug",
              "Nose_sleeve"),
    "eva": ("Frame_skin", "Rags", "Pommel", "Pommel_claws", "Warpstone_pommel", "Straps", "Strap_rivets", "Spikes", "Plates",
            "Plate_rivets", "Crest", "Vial_caps", "Vial_cage", "Warpstone_vial"),
    "buy": ("Chamber_axle", "Vent_valve", "Pin", "Mainsprings", "Hammer_axle", "Guide_rod", "Hose", "Vial_glass", "Gauge", "Gauge_glass",
            "Gauge_needle", "Pilot_pipe", "Gauge_line", "Tee", "Axle_cap", "Thrust_washer"),
}
BUY_NOTE = {"Chamber_axle": "tube Ø25 x 0.6, 258 mm (the chamber)", "Block": "+ 6 barrel tubes Ø25 x 0.6, %.0f mm" % BARREL_TUBE,
            "Vent_valve": "AirTAC M3R110-06 with its roller off (or M3PP110-06): G1/8 elbows for A (4 mm) and R (6 mm), a G1/8 silencer on P", "Pin": "steel pin Ø3",
            "Mainsprings": "2 torsion springs, wire Ø1.6, OD 14, 6 coils", "Hose": "6/4 hose from the receiver, up the grip to the vent valve's R port",
            "Vial_glass": "a test tube Ø16", "Gauge": "a Ø25 0-4 bar gauge with a 4 mm push-in (it reads the chamber, through the pilot)",
            "Pilot_pipe": "PU tube 4/2.5: vent valve A -> cap G1/8 push-in, up the backstrap",
            "Gauge_line": "PU tube 4/2.5, tee to the gauge", "Tee": "push-in tee for 4 mm tube", "Axle_cap": "M6 x 25 stud (or a headless bolt) + cap nut; an M6 nut glued in the plug",
            "Axle_plug": "glued flush into the axle's front end with epoxy: it closes the chamber",
            "Top_strap": "2 x M3 x 40 + nuts down through its foot into the cage's top",
            "Thrust_washer": "nylon / PTFE washer 25 x 28 x 1",
            "Trigger_guard": "printed flat; ST2.9 x 13 through the floor into its tab, rear end glued in the grip",
            "Grip_left": "half, with the valve box: glued to the right on 3 x Ø3 x 12 dowels; 2 x ST2.9 x 13 down through the floor",
            "Grip_right": "half: the vent valve on 3 x M3 x 30 + nuts through both; 2 x ST2.9 x 13 down through the floor",
            "Detent_housing": "with its bracket: 2 x M3 x 12 + nuts to the side plate's outer face",
            "Frame_side": "6 x ST2.9 x 13 into the cage's bosses",
            "Hammer_axle": "steel rod Ø8 x 84 (or an M8 bolt's shank), pressed through both walls",
            "Guide_rod": "steel rod Ø3 x 96: the slider's guide, floor to the stop pad", "Trigger": "pivot: M3 x 16 screw + nylock nut"}
FILL = {"Valve_body_v11": 0.8, "Valve_cap_v11": 0.8}               # airtight; the rest ~45 % (walls + infill)
mat_of = {n: m for m, ns in MATERIAL.items() for n in ns}
lines, grams = [], 0.0
for o in doc.Objects:
    if o.TypeId != "Part::Feature":
        continue
    m = mat_of.get(o.Name, "?")
    o.addProperty("App::PropertyString", "Material", "Ratling", "print / eva / buy")
    o.Material = m
    if m == "print":
        vol = o.Shape.Volume - (barrels.Volume if o.Name == "Block" else 0.0)
        g_ = vol / 1000 * 1.24 * FILL.get(o.Name, 0.45)
        grams += g_
        lines.append("    print  %-16s %5.0f g%s" % (o.Name, g_, ("   " + BUY_NOTE[o.Name]) if o.Name in BUY_NOTE else ""))
lines += ["    buy    %-16s %s" % (n, BUY_NOTE.get(n, "")) for n in MATERIAL["buy"]]
lines.append("    eva    " + ", ".join(MATERIAL["eva"]))
unsorted = [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in mat_of]
# The tree by material: hide a group to see the rest (pistol/material_view.py colours by it)
for gname, label in (("Print", "Печать"), ("EVA", "EVA"), ("Buy", "Покупное")):
    g = doc.addObject("App::DocumentObjectGroup", gname)
    g.Label = label
    for o in [o for o in doc.Objects if o.TypeId == "Part::Feature" and getattr(o, "Material", "") == gname.lower()]:
        for parent in o.InList:
            if parent.TypeId == "App::DocumentObjectGroup":
                parent.removeObject(o)
        g.addObject(o)
for old in (g_mech, g_dress):
    if not old.Group:
        doc.removeObject(old.Name)
doc.recompute()
print("  parts by material (print at ~45 %% fill, valve 80 %%): ~%.0f g of filament%s\n%s"
      % (grams, ("; NOT SORTED: " + ", ".join(unsorted)) if unsorted else "", "\n".join(lines)))

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
