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
STUB = BARREL_TUBE - 13.0
exec(open(os.path.join(REPO, "pistol", "hammer_layout.py")).read())

NAME = "pistol_hammer_assembly"
random.seed(7)

# ---------------------------------------------------------------- parameters
FRAME = dict(x=(HAMMER_PIVOT.x - HAMMER_R - 8.0, -1.0), y=(-43.0, 43.0), z=(-76.0, 28.0))   # round the hammer and the raised slider
SPUR_SLOT = dict(a=(68.0, 190.0), r=SPUR[1] + 10.0, y=6.5)    # the spur's swing out of the top rear
FRAME_WALL = 3.0
FRAME_FILLET = 12.0
REAR = dict(x=-60.0, top=12.0)      # behind this the frame steps down: the hammer stands up out of it

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
outer_f = box(REAR["x"] - 2, fx[1], fy[0], fy[1], fz[0], fz[1])
outer_r = box(fx[0], REAR["x"] + 10, fy[0], fy[1], fz[0], REAR["top"])
outer = outer_f.makeFillet(FRAME_FILLET, outer_f.Edges).fuse(outer_r.makeFillet(FRAME_FILLET, outer_r.Edges)).removeSplitter()
inner = (box(REAR["x"] + 1, fx[1] + 10, fy[0] + FRAME_WALL, fy[1] - FRAME_WALL, fz[0] + FRAME_WALL, fz[1] - FRAME_WALL)
         .fuse(box(fx[0] + FRAME_WALL, REAR["x"] + 10, fy[0] + FRAME_WALL, fy[1] - FRAME_WALL, fz[0] + FRAME_WALL,
                   REAR["top"] - FRAME_WALL)))
frame = outer.cut(inner)
# Slot in the bottom wall for the trigger over its stroke
slab = box(fx[0], fx[1], -16, 16, fz[0] - 1, fz[0] + FRAME_WALL + 1)
xs = []
for tg in (0.0, 0.5, 1.0):
    c_ = trigger_h(tg).common(slab)
    if c_.Volume > 1e-3:
        xs += [c_.BoundBox.XMin, c_.BoundBox.XMax]
if xs:
    frame = frame.cut(box(min(xs) - 1.5, max(xs) + 1.5, -5, 5, fz[0] - 1, fz[0] + FRAME_WALL + 1))
# Slot in the top rear for the spur: a pie over its swing, round the pivot
H_ = HAMMER_PIVOT
pie = [V(H_.x, -SPUR_SLOT["y"], H_.z)] + [V(H_.x + SPUR_SLOT["r"] * math.cos(math.radians(q)), -SPUR_SLOT["y"],
                                            H_.z + SPUR_SLOT["r"] * math.sin(math.radians(q)))
                                          for q in [SPUR_SLOT["a"][0] + (SPUR_SLOT["a"][1] - SPUR_SLOT["a"][0]) * k / 12 for k in range(13)]]
spur_slot = Part.Face(Part.makePolygon(pie + [pie[0]])).extrude(V(0, 2 * SPUR_SLOT["y"], 0))
frame = frame.cut(spur_slot)
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
mini_valves = valves                            # mech_layout's trigger valves
frame = frame.cut(Part.makeCompound([cyl_x(MINI_VALVE[0] + 1, tip - MINI_VALVE[1] - 1, tip + 1, y, MINI_Z)
                                     for y, tip in MINI_VALVES]))         # through the frame's rear wall
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
GUARD = [V(-24, 0, fz[0] + 3), V(-22, 0, -90), V(-30, 0, -104), V(-48, 0, -111), V(-68, 0, -107), V(-84, 0, -97),
         V(-95, 0, -87)]                        # a round loop through these
guard = pipe_along(GUARD, 2.6)
guard = Part.Solid(guard) if guard.ShapeType != "Solid" else guard
guard = guard.cut(inner).removeSplitter()

# ---------------------------------------------------------------- detent housing
detent_box = turned(box(HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2,
                        -HUB_R - 24, -HUB_R - 1.5), DETENT_ANGLE + 90)
detent_box = detent_box.cut(Part.makeCompound([bolt_shape(0.0), bolt_shape(30.0)]))

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
            for other_name, other in (("frame", frame), ("grip", grip), ("tang", pod), ("detent box", detent_box), ("guard", guard),
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
                     ("Vent_valve", mini_valves, (0.3, 0.3, 0.8), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame", frame, IRON, 0), ("Tang", pod, IRON, 0), ("Trigger_guard", guard, IRON, 0),
                     ("Detent_housing", detent_box, IRON, 0), ("Grip", grip, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
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
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
