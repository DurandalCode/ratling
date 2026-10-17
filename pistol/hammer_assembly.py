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
standoffs = Part.makeCompound([Part.makeCylinder(5.0, y_in - 20 + 0.5, V(x_, sg * (y_in + 0.5), z_), V(0, -sg, 0)).cut(valve_body)
                               for x_, z_, sides in STANDOFFS for sg in sides])
frame = frame.fuse(standoffs).removeSplitter()
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
mini_valves = valves                            # mech_layout's trigger valves
_vv = Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z) for y, tip in MINI_VALVES])
frame, skin = frame.cut(_vv), skin.cut(_vv)                              # through the frame's rear wall
# Tang: the frame runs on back under the valve cap into the grip, round the trigger valves
pod = box(min(t for _, t in MINI_VALVES) - MINI_VALVE[1] - 4, max(t for _, t in MINI_VALVES) - 4.5, -19, 19,
          MINI_Z - 9, MINI_Z + 10)
# Backstrap: closes the gap between the frame's rear wall and the grip's top, over the tang
strap = box(GRIP_START.x - 14, fx[0] + 4, -19, 19, fz[0] - 4, Z_FIRE - 4)
strap = strap.makeFillet(min(8.0, strap.BoundBox.XLength / 2 - 1), strap.Edges)
pod = pod.makeFillet(5.0, pod.Edges).fuse(strap).cut(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z)
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
guard = guard.cut(inner).removeSplitter()

# ---------------------------------------------------------------- detent housing
detent_box = turned(box(HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2,
                        -HUB_R - 24, -HUB_R - 1.5), DETENT_ANGLE + 90)
detent_box = detent_box.cut(Part.makeCompound([bolt_shape(0.0), bolt_shape(30.0)]))
_db = detent_box.BoundBox                       # a bracket from the cage's left side forward to it, clear of the block
detent_bracket = box(fx[1] - 8, _db.XMin + 0.9, _db.YMin + 2, -(fy[1] - EVA_T - CAGE_T) + 0.5, _db.ZMax - 10, _db.ZMax)
detent_bracket = detent_bracket.cut(cyl_x(2 * 47.6, HUB_X0, 50)).cut(detent_box)

# ---------------------------------------------------------------- dress: block straps, frame plates, crest, hammer, vial, gauge, pilot pipe
block_d = 2 * HUB_R
straps, spikes, strap_rivets = [], [], []
for x0, w, tilt in ((HUB_X0 + 2, 12, 0), ((HUB_X0 + HUB_T + STUB) / 2, 8, 4), (HUB_X0 + HUB_T + STUB - 14, 10, -3)):
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
gp = V(fx[0] + 50, fy[1] + 18, Z_FIRE + 30)
gauge = Part.makeCylinder(12, 8, gp, YA).fuse(Part.makeCylinder(3, 16, gp - V(0, 15, 0), YA))
gauge_glass = Part.makeCylinder(10.5, 1, gp + V(0, 8, 0), YA)
needle = box(gp.x, gp.x + 9, gp.y + 9, gp.y + 9.8, gp.z - 0.6, gp.z + 0.6)
needle.rotate(gp, YA, -35)
pilot_pipe = pipe_along([V(fx[0] - 6, 0, Z_FIRE), V(fx[0] - 16, -22, Z_FIRE - 14), V(fx[0] - 14, -26, MINI_Z - 2),
                         V(fx[0] + 2, -FRAME["y"][1] + 2, MINI_Z)], 2.6)
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
nose = cyl_x(NOSE_OD, X_MUZZLE + WASHER_T, X_AXLE_END, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE, X_AXLE_END + 1, 0, 0))
washer = cyl_x(NOSE_OD, X_MUZZLE, X_MUZZLE + WASHER_T, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE - 1, X_MUZZLE + 2, 0, 0))
axle_cap = Part.makeCylinder(3.0, 14, V(X_AXLE_END - 4, 0, 0), XA).fuse(        # M6 stud and a cap nut
    Part.makeCone(8, 5, 9, V(X_AXLE_END + s_t, 0, 0), XA))
strap_rivets += [V(x_, 0, STRAP["z"][1] + 0.3) for x_ in range(int(STRAP["x0"]) + 8, int(X_AXLE_END), 24)]
spikes += [spike(V(x_, 0, STRAP["z"][1] - 1), V(0.25, 0, 1), 14, 3.5) for x_ in (X_MUZZLE * 0.3, X_MUZZLE * 0.7)]
spikes += [spike(V(X_AXLE_END + s_t / 2, sd_ * s_w, STRAP["z"][1] - 8), V(0.3, sd_ * 1, 0.4), 14, 3.0) for sd_ in (-1, 1)]

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
            for other_name, other in (("frame", frame), ("skin", skin), ("grip", grip), ("tang", pod), ("detent box", detent_box),
                                      ("bracket", detent_bracket), ("guard", guard),
                                      ("vent valve", valve_bodies), ("crest", crest)):
                if n == "Bolt" and other_name == "detent box":
                    continue                     # it slides in it
                v_ = hit(st[n], other)
                worst[(n, other_name)] = max(worst.get((n, other_name), 0.0), v_)
sup = top_strap.fuse(nose).fuse(washer)
blk_hit = max(hit(turned(block, a_), sup) + hit(turned(Part.makeCompound(straps), a_), top_strap) for a_ in (0.0, 15.0, 30.0, 45.0))
fixed_hits = {"block/supports": blk_hit, "strap/vial": hit(top_strap, vial.fuse(cage)) + hit(top_strap, crest),
              "valve/frame": valve_body.common(frame).Volume + valve_cap.common(frame).Volume,
              "lock/frame": lock_housing_h.common(frame).Volume, "vent valve/frame": mini_valves.common(frame).Volume}
inside = mini_valves.common(grip.fuse(outer).fuse(pod.fuse(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z) for y, tip in MINI_VALVES])))).Volume / mini_valves.Volume
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
                     ("Vent_valve", mini_valves, (0.3, 0.3, 0.8), 0), ("Mainsprings", mainsprings, (0.6, 0.6, 0.65), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame", frame, IRON, 0), ("Frame_skin", skin, IRON, 0), ("Tang", pod, IRON, 0), ("Trigger_guard", guard, IRON, 0),
                     ("Detent_housing", detent_box, IRON, 0), ("Detent_bracket", detent_bracket, IRON, 0), ("Grip", grip, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
                     ("Pommel", pommel, IRON, 0), ("Pommel_claws", Part.makeCompound(claws), DIRTY, 0),
                     ("Warpstone_pommel", warp_pommel, WARP, 0), ("Hose", hose, (0.08, 0.08, 0.08), 0),
                     ("Straps", Part.makeCompound(straps), IRON, 0), ("Strap_rivets", rivets(strap_rivets), DIRTY, 0),
                     ("Spikes", Part.makeCompound(spikes), DIRTY, 0), ("Plates", Part.makeCompound(plates), RUST, 0),
                     ("Plate_rivets", rivets(plate_rivets), DIRTY, 0), ("Crest", crest, DIRTY, 0),
                     ("Vial_glass", vial, GLASS, 65), ("Vial_caps", vial_caps, BRASS, 0), ("Vial_cage", cage, IRON, 0),
                     ("Warpstone_vial", vial_stone, WARP, 0), ("Gauge", gauge, BRASS, 0), ("Gauge_glass", gauge_glass, (0.9, 0.9, 0.85), 0),
                     ("Gauge_needle", needle, (0.6, 0.05, 0.05), 0), ("Pilot_pipe", pilot_pipe, COPPER, 0),
                     ("Axle_cap", axle_cap, IRON, 0), ("Top_strap", top_strap, IRON, 0), ("Nose_sleeve", nose, IRON, 0),
                     ("Thrust_washer", washer, (0.85, 0.85, 0.8), 0)):
    add(g_dress, n, s_, c, tr)
doc.recompute()

# ---------------------------------------------------------------- what is printed, cut from EVA, or bought
# Print only what carries load or moves; the look is EVA foam; tubes, springs, valves, fasteners are bought.
MATERIAL = {
    "print": ("Valve_body_v11", "Valve_cap_v11", "Lock_housing", "Block", "Sector", "Pawl", "Slider", "Bolt", "Hammer",
              "Sleeve", "Pusher", "Trigger", "Frame", "Tang", "Detent_housing", "Detent_bracket", "Grip", "Top_strap",
              "Nose_sleeve"),
    "eva": ("Frame_skin", "Rags", "Pommel", "Pommel_claws", "Warpstone_pommel", "Straps", "Strap_rivets", "Spikes", "Plates",
            "Plate_rivets", "Crest", "Vial_caps", "Vial_cage", "Warpstone_vial"),
    "buy": ("Chamber_axle", "Vent_valve", "Pin", "Mainsprings", "Hose", "Vial_glass", "Gauge", "Gauge_glass",
            "Gauge_needle", "Pilot_pipe", "Axle_cap", "Thrust_washer", "Trigger_guard"),
}
BUY_NOTE = {"Chamber_axle": "tube Ø25 x 0.6, 258 mm (the chamber)", "Block": "+ 6 barrel tubes Ø25 x 0.6, %.0f mm" % BARREL_TUBE,
            "Vent_valve": "mini 3/2 push-button valve, or module/stage3_vent_head.py", "Pin": "steel pin Ø3",
            "Mainsprings": "2 torsion springs, wire Ø1.6, OD 14, 6 coils", "Hose": "6/4 hose to the receiver",
            "Vial_glass": "a test tube Ø16", "Gauge": "a Ø25 0-4 bar gauge (a real one: it reads the chamber)",
            "Pilot_pipe": "copper or PU tube Ø4-5: the pilot line, cap to vent valve", "Axle_cap": "M6 stud + cap nut",
            "Thrust_washer": "nylon / PTFE washer 25 x 28 x 1", "Trigger_guard": "Ø5 steel or aluminium rod, bent"}
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
