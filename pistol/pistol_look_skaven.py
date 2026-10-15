# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the Skaven look, over concept A ("Nagant").

Same layout as pistol_look.py (v1.1 valve behind the bottom barrel inside
the lock, chamber tube as the block's axle, trigger valve in the grip, hose
out of the butt), dressed as Clan Skryre work: rusty iron, barrels of odd
lengths, riveted straps with spikes, plates bolted on crooked, a jagged
crest and a claw hammer, a serrated blade under the barrels, rag-wrapped
grip, glowing warpstone in the pommel and in a caged vial on the lock, and
the pilot line run outside as a copper pipe past a pressure gauge (a real
gauge would earn its place there).

Not parts: shapes for the look and the proportions only.
Frame: x forward (muzzle at +x), z up, y to the side.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/pistol_look_skaven.py').read())
"""

import math
import random

import FreeCAD as App
import Part

NAME = "pistol_look_skaven"
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
O = V(0, 0, 0)
random.seed(7)                  # the same crooked pistol every run

R_RING = 27.0
BARREL_D = 25.0
BARREL_LENS = (184.0, 166.0, 176.0, 190.0, 160.0, 172.0)    # odd lengths, bottom first, anticlockwise
FLARED = (1, 4)                 # barrels with a bell mouth
CHAMBER_LEN = 200.0
SPACER = 12.0
VALVE_D, BODY_H, CAP_T = 62.0, 27.0, 16.0
GRIP_ANGLE = 36.0
GRIP_LEN = 128.0

RUST = (0.40, 0.24, 0.14)
BARREL_TONES = ((0.34, 0.30, 0.27), (0.42, 0.27, 0.17), (0.30, 0.29, 0.28),
                (0.38, 0.31, 0.24), (0.45, 0.28, 0.16), (0.33, 0.31, 0.29))   # iron, rust, iron...
IRON = (0.24, 0.23, 0.22)
DIRTY_STEEL = (0.45, 0.43, 0.40)
COPPER = (0.30, 0.55, 0.44)      # verdigris
BRASS = (0.55, 0.45, 0.22)
WOOD = (0.26, 0.16, 0.09)
RAG = (0.48, 0.42, 0.30)
WARP = (0.35, 0.95, 0.20)
GLASS = (0.70, 0.85, 0.75)


def cyl_x(d, x0, x1, y=0.0, z=0.0):
    return Part.makeCylinder(d / 2, x1 - x0, V(x0, y, z), X)


def ring_yz(n=6, r=R_RING, a0=-90.0):
    return [(r * math.cos(math.radians(a0 + 360.0 / n * i)), r * math.sin(math.radians(a0 + 360.0 / n * i)))
            for i in range(n)]


def spike(base, direction, length, r):
    return Part.makeCone(r, 0, length, base, direction)


def crystal(center, axis, length, r):
    """An elongated octahedron: a warpstone shard."""
    axis = V(axis).normalize()
    side = axis.cross(Z if abs(axis.z) < 0.9 else X).normalize()
    up = axis.cross(side).normalize()
    tip0, tip1 = center - axis * (length * 0.35), center + axis * (length * 0.65)
    ring = [center + side * r, center + up * r, center - side * r * 0.8, center - up * r * 0.9]
    faces = []
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        faces.append(Part.Face(Part.makePolygon([tip1, a, b, tip1])))
        faces.append(Part.Face(Part.makePolygon([tip0, b, a, tip0])))
    return Part.Solid(Part.Shell(faces))


def rivets(points, r=1.6):
    return Part.makeCompound([Part.makeSphere(r, p) for p in points])


def pipe_along(points, r):
    curve = Part.BSplineCurve()
    curve.interpolate(points)
    path = Part.Wire(curve.toShape())
    t0 = curve.tangent(curve.FirstParameter)[0]
    prof = Part.Wire(Part.makeCircle(r, points[0], t0))
    return path.makePipeShell([prof], True, True)


# ---------------------------------------------------------------- barrels
barrel_list = []
for (y, z), L, i in zip(ring_yz(), BARREL_LENS, range(6)):
    b = cyl_x(BARREL_D, 0, L, y, z).cut(cyl_x(23.8, -1, L + 1, y, z))
    if i in FLARED:
        bell = Part.makeCone(BARREL_D / 2, BARREL_D / 2 + 4, 14, V(L - 2, y, z), X).cut(
            Part.makeCone(23.8 / 2, 23.8 / 2 + 4, 14.1, V(L - 2.05, y, z), X))
        b = b.fuse(bell)
    barrel_list.append(b)
barrels = Part.makeCompound(barrel_list)
block_d = 2 * R_RING + BARREL_D

straps, spikes, strap_rivets = [], [], []
for x0, w, tilt in ((0, 14, 0), (70, 8, 4), (150, 10, -3)):
    s = cyl_x(block_d + 5, x0, x0 + w).cut(cyl_x(block_d - 1, x0 - 1, x0 + w + 1))
    s.rotate(V(x0 + w / 2, 0, 0), Y, tilt)
    straps.append(s)
    for k in range(7):
        a = math.radians(360.0 / 7 * k + random.uniform(-10, 10))
        strap_rivets.append(V(x0 + w / 2, (block_d / 2 + 2.6) * math.cos(a), (block_d / 2 + 2.6) * math.sin(a)))
    for a_deg in ((30, 150, 250) if x0 == 0 else (90, 210) if x0 == 150 else ()):
        a = math.radians(a_deg)
        dirv = V(0, math.cos(a), math.sin(a))
        spikes.append(spike(V(x0 + w / 2, 0, 0) + dirv * (block_d / 2 + 2), dirv + V(0.3, 0, 0), 16, 4))
# Rear face of the block, round the breeches (the strap at x 0..14 holds them)
axle = cyl_x(BARREL_D, -SPACER, -SPACER + CHAMBER_LEN).fuse(cyl_x(27, -SPACER + CHAMBER_LEN, -SPACER + CHAMBER_LEN + 5))
axle_cap = Part.makeCone(9, 3, 10, V(-SPACER + CHAMBER_LEN + 5, 0, 0), X)

# serrated blade under the block, hung from the middle strap
teeth = [(70, -R_RING - 14)]
x = 70
while x < 230:
    teeth += [(x + 6, -R_RING - 30 - random.uniform(0, 5)), (x + 12, -R_RING - 24)]
    x += 12
teeth += [(250, -R_RING - 20), (150, -R_RING - 12)]
blade = Part.Face(Part.makePolygon([V(px, -1.5, pz) for px, pz in teeth] + [V(teeth[0][0], -1.5, teeth[0][1])])).extrude(V(0, 3, 0))

# ---------------------------------------------------------------- lock round the v1.1 valve
z_valve = -R_RING
x_cap = -SPACER - BODY_H - CAP_T
housing = Part.makeBox(-x_cap + 6, VALVE_D + 8, VALVE_D + 22, V(x_cap - 6, -(VALVE_D + 8) / 2, z_valve - VALVE_D / 2 - 4))
housing = housing.makeFillet(18.0, housing.Edges)
housing = housing.fuse(cyl_x(VALVE_D + 10, -SPACER - 4, 0, 0, z_valve))
plates, plate_rivets = [], []
for side, rot, dx, dz in ((1, 7, 4, 6), (-1, -5, -2, -4)):
    p = Part.makeBox(42, 3, 34, V(x_cap + 4 + dx, side * (VALVE_D + 8) / 2 - (0 if side > 0 else 3), z_valve - 12 + dz))
    p.rotate(V(x_cap + 25, 0, z_valve), Y, rot)
    plates.append(p)
    yb = side * ((VALVE_D + 8) / 2 + (3 if side > 0 else 0)) + side * 0.5
    for px, pz in ((6, 4), (36, 6), (5, 30), (37, 28)):
        q = V(x_cap + 4 + dx + px, yb, z_valve - 12 + dz + pz)
        plate_rivets.append(q)
crest_pts = [(x_cap - 2, 0)]
for k in range(6):
    crest_pts += [(x_cap + 4 + k * 9, 14 + random.uniform(0, 6)), (x_cap + 9 + k * 9, 3)]
crest_pts += [(-6, 0)]
z_top = z_valve + VALVE_D / 2 + 18
crest = Part.Face(Part.makePolygon([V(px, -1.5, z_top - 2 + pz) for px, pz in crest_pts]
                                   + [V(crest_pts[0][0], -1.5, z_top - 2)])).extrude(V(0, 3, 0))

# claw hammer: pivot at the top rear, curled spur
hp = V(x_cap + 2, 0, z_top - 4)
hammer = Part.makeCylinder(7, 12, hp - V(0, 6, 0), Y)
claw = Part.makeTorus(11, 3.2, hp + V(-11, 0, 0), Y).common(Part.makeBox(30, 20, 30, hp + V(-30, -10, 0)))
hammer = hammer.fuse(claw).fuse(spike(hp + V(-22, 0, 0), V(0.2, 0, -1), 10, 3))

# warpstone vial in a cage on the lock's top front
vc = V(-24, 0, z_top + 4)
vial = Part.makeCylinder(8, 30, vc, Z)
vial_caps = Part.makeCylinder(10, 4, vc - V(0, 0, 2), Z).fuse(Part.makeCylinder(10, 4, vc + V(0, 0, 29), Z))
cage = Part.makeCompound([Part.makeCylinder(1.2, 32, vc + V(10 * math.cos(math.radians(a)), 10 * math.sin(math.radians(a)), 0), Z)
                          for a in (0, 120, 240)])
vial_stone = crystal(vc + V(0, 0, 14), V(0.2, 0.1, 1), 24, 5)

# pressure gauge on the lock's right side, on a copper stub
gp = V(x_cap + 20, (VALVE_D + 8) / 2 + 18, z_valve + 22)
gauge = Part.makeCylinder(12, 8, gp, Y).fuse(Part.makeCylinder(3, 16, gp - V(0, 15, 0), Y))
gauge_glass = Part.makeCylinder(10.5, 1, gp + V(0, 8, 0), Y)
needle = Part.makeBox(9, 0.8, 1.2, gp + V(0, 9, -0.6))
needle.rotate(gp, Y, -35)

# ---------------------------------------------------------------- grip
a = math.radians(GRIP_ANGLE)
d = V(-math.cos(a), 0, -math.sin(a))
n = V(-math.sin(a), 0, math.cos(a))
start = V(x_cap + 14, 0, z_valve - 8)
sections = [(0.0, 44, 30), (0.4, 38, 27), (0.8, 42, 30), (1.0, 46, 33)]
grip = Part.makeLoft([Part.Wire(Part.Ellipse(start + d * (GRIP_LEN * t) + n * (h / 2),
                                             start + d * (GRIP_LEN * t) + Y * (w / 2),
                                             start + d * (GRIP_LEN * t)).toShape()) for t, h, w in sections], True, False)
rags = []
for t, tw in ((0.18, 9), (0.42, 12), (0.66, 8), (0.86, 10)):
    c = start + d * (GRIP_LEN * t)
    h, w = 44 - 6 * t + 3, 30 - 3 * t + 3
    e0 = Part.Wire(Part.Ellipse(c + n * (h / 2), c + Y * (w / 2), c).toShape())
    c1 = c + d * tw
    e1 = Part.Wire(Part.Ellipse(c1 + n * (h / 2 + random.uniform(-1, 1)), c1 + Y * (w / 2), c1).toShape())
    r = Part.makeLoft([e0, e1], True, False)
    r.rotate(c, d, random.uniform(-15, 15))
    rags.append(r)
c_end = start + d * GRIP_LEN
pommel = Part.makeCone(18, 10, 10, c_end, d)
claws = [spike(c_end + d * 4 + V(math.sin(math.radians(k)) * 0, math.cos(math.radians(k)) * 14, math.sin(math.radians(k)) * 14 * n.z),
               d + V(0, math.cos(math.radians(k)) * 0.8, math.sin(math.radians(k)) * 0.8), 14, 2.2)
         for k in (0, 120, 240)]
warp_pommel = Part.makeCompound([crystal(c_end + d * 14, d + V(0.2, 0.3, 0.1), 40, 11),
                                 crystal(c_end + d * 11 + V(0, 8, 5), d + V(-0.2, 0.8, 0.5), 28, 7),
                                 crystal(c_end + d * 11 + V(0, -8, -3), d + V(0.3, -0.7, -0.3), 24, 6)])
hose = Part.makeCylinder(3, 70, c_end + d * 20, d)

# pilot line: copper pipe from the trigger valve in the grip, outside, round to the valve cap behind
pilot = pipe_along([start + d * 40 + V(0, 16, 0), start + d * 30 + V(0, 22, 18), V(x_cap - 14, 24, z_valve + 4),
                    V(x_cap - 10, 0, z_valve)], 2.6)

# ---------------------------------------------------------------- guard, trigger
z_guard = z_valve - VALVE_D / 2 - 4
gc = V(x_cap + 52, 0, z_guard - 2)
guard = Part.makeTorus(17, 2.8, gc, Y).common(Part.makeBox(60, 20, 30, gc + V(-30, -10, -30)))
guard = guard.fuse(spike(gc + V(17, 0, -4), V(0.6, 0, -1), 14, 2.6))
trigger = Part.makeTorus(14, 2.2, gc + V(12, 0, -2), Y).common(Part.makeBox(16, 20, 16, gc + V(-2, -10, -18)))

# ---------------------------------------------------------------- document
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
parts = [(f"Barrel_{i}", b, BARREL_TONES[i]) for i, b in enumerate(barrel_list)] + [("Straps", Part.makeCompound(straps), IRON),
         ("Strap_rivets", rivets(strap_rivets), DIRTY_STEEL), ("Spikes", Part.makeCompound(spikes), DIRTY_STEEL),
         ("Chamber_axle", axle, RUST), ("Axle_cap", axle_cap, IRON), ("Blade", blade, DIRTY_STEEL),
         ("Lock_housing", housing, IRON), ("Plates", Part.makeCompound(plates), RUST),
         ("Plate_rivets", rivets(plate_rivets), DIRTY_STEEL), ("Crest", crest, DIRTY_STEEL),
         ("Hammer", hammer, IRON), ("Vial_glass", vial, GLASS), ("Vial_caps", vial_caps, BRASS),
         ("Vial_cage", cage, IRON), ("Warpstone_vial", vial_stone, WARP),
         ("Gauge", gauge, BRASS), ("Gauge_glass", gauge_glass, (0.9, 0.9, 0.85)), ("Gauge_needle", needle, (0.6, 0.05, 0.05)),
         ("Grip", grip, WOOD), ("Rags", Part.makeCompound(rags), RAG), ("Pommel", pommel, IRON),
         ("Pommel_claws", Part.makeCompound(claws), DIRTY_STEEL), ("Warpstone_pommel", warp_pommel, WARP),
         ("Hose", hose, (0.08, 0.08, 0.08)), ("Pilot_pipe", pilot, COPPER),
         ("Trigger_guard", guard, IRON), ("Trigger", trigger, RUST)]
for name, s, col in parts:
    o = doc.addObject("Part::Feature", name)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = col
        if name.startswith("Vial_glass"):
            o.ViewObject.Transparency = 65
        if name.startswith("Warpstone"):
            try:
                m = App.Material()
                m.DiffuseColor = WARP
                m.EmissiveColor = (0.25, 0.8, 0.1)
                o.ViewObject.ShapeAppearance = [m]
            except Exception:
                pass
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewFront()
    Gui.SendMsgToActiveView("ViewFit")
print(NAME, ": block Ø%.0f, barrels %.0f..%.0f mm" % (block_d, min(BARREL_LENS), max(BARREL_LENS)))
