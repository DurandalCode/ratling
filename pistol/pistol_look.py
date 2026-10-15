# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the look, over concept A ("Nagant").

A pepperbox in the manner of the Vermintide repeater handgun: six barrels
nearly touching, brass bands at the breech and the muzzle, a rounded lock
housing with a hammer on top, a curved wooden grip flaring to a metal butt
cap. Everything sits where concept A's parts are (pistol_concepts.py): the
v1.1 valve (body and cap, Ø62) behind the bottom barrel inside the lock
housing, its cap under the round boss on the side; the chamber tube as the
block's axle; the trigger valve in the grip; the hose out through a brass
"gem" in the butt cap.

Not parts: shapes for the look and the proportions only.
Frame: x forward (muzzle at +x), z up, y to the side.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/pistol_look.py').read())
"""

import math

import FreeCAD as App
import Part

NAME = "pistol_look"
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

R_RING = 27.0               # barrel ring = v1's chamber-to-seat distance
BARREL_D = 25.0
BARREL_LEN = 180.0
CHAMBER_LEN = 200.0         # from the valve body's top face (x = -SPACER)
SPACER = 12.0
VALVE_D, BODY_H, CAP_T = 62.0, 27.0, 16.0
GRIP_ANGLE = 32.0           # below the barrel axis, going back
GRIP_LEN = 135.0

WOOD = (0.45, 0.24, 0.14)
STEEL = (0.58, 0.58, 0.62)
IRON = (0.32, 0.32, 0.35)
BRASS = (0.78, 0.62, 0.26)
GEM = (0.15, 0.6, 0.35)


def cyl_x(d, x0, x1, y=0.0, z=0.0):
    return Part.makeCylinder(d / 2, x1 - x0, V(x0, y, z), X)


def ring_yz(n=6, r=R_RING, a0=-90.0):
    return [(r * math.cos(math.radians(a0 + 360.0 / n * i)), r * math.sin(math.radians(a0 + 360.0 / n * i)))
            for i in range(n)]


def band(x0, x1, d, grooves=2):
    b = cyl_x(d, x0, x1)
    w = (x1 - x0) / (2 * grooves + 1)
    for i in range(grooves):
        g0 = x0 + w * (2 * i + 1)
        b = b.cut(cyl_x(d + 2, g0, g0 + w * 0.6).cut(cyl_x(d - 1.6, g0 - 1, g0 + w + 1)))
    return b


def arc_rod(center, r_bend, r_rod, a0, a1):
    """A rod bent round `center` in the x-z plane, from angle a0 to a1 (deg)."""
    t = Part.makeTorus(r_bend, r_rod, center, Y, 0, 360, a1 - a0)
    t.rotate(center, Y, -a0)
    return t


# ---------------------------------------------------------------- barrel block
barrels = Part.makeCompound([cyl_x(BARREL_D, 0, BARREL_LEN, y, z).cut(cyl_x(23.8, -1, BARREL_LEN + 1, y, z))
                             for y, z in ring_yz()])
fill = cyl_x(2 * R_RING + 4, 14, BARREL_LEN - 10).cut(
    Part.makeCompound([cyl_x(BARREL_D + 0.2, 0, BARREL_LEN, y, z) for y, z in ring_yz()]))
fill = fill.cut(cyl_x(BARREL_D + 0.5, 0, BARREL_LEN + 1))     # dark core between the barrels
block_d = 2 * R_RING + BARREL_D
rear_band = band(0, 16, block_d + 4, 2)
front_band = band(BARREL_LEN - 10, BARREL_LEN, block_d + 3, 1)
for y, z in ring_yz():
    rear_band = rear_band.cut(cyl_x(23.8, -1, 17, y, z))
    front_band = front_band.cut(cyl_x(23.8, BARREL_LEN - 11, BARREL_LEN + 1, y, z))
rear_band = rear_band.cut(cyl_x(BARREL_D + 0.5, -1, 17))
front_band = front_band.cut(cyl_x(BARREL_D + 0.5, BARREL_LEN - 11, BARREL_LEN + 1))
axle = cyl_x(BARREL_D, -SPACER, -SPACER + CHAMBER_LEN).fuse(cyl_x(27, -SPACER + CHAMBER_LEN, -SPACER + CHAMBER_LEN + 5))
axle_nut = cyl_x(14, -SPACER + CHAMBER_LEN + 5, -SPACER + CHAMBER_LEN + 9)

# ---------------------------------------------------------------- lock housing round the v1.1 valve
z_valve = -R_RING                            # bottom barrel
x_cap = -SPACER - BODY_H - CAP_T
housing = Part.makeBox(-x_cap + 6, VALVE_D + 8, VALVE_D + 22, V(x_cap - 6, -(VALVE_D + 8) / 2, z_valve - VALVE_D / 2 - 4))
housing = housing.makeFillet(22.0, housing.Edges)
housing = housing.fuse(cyl_x(VALVE_D + 10, -SPACER - 4, 0, 0, z_valve))       # collar under the rear band
bosses = Part.makeCompound([Part.makeCylinder(23, 3, V(x_cap + 22, s * (VALVE_D + 8) / 2 - (3 if s > 0 else 0), z_valve), Y)
                            for s in (1, -1)])
boss_rims = Part.makeCompound([Part.makeTorus(23, 1.6, V(x_cap + 22, s * ((VALVE_D + 8) / 2 + 1.5), z_valve), Y)
                               for s in (1, -1)])
valve = cyl_x(VALVE_D, x_cap, -SPACER, 0, z_valve)                            # hidden inside

# hammer: pivot on the top rear, spur back
hp = V(x_cap + 8, 0, z_valve + VALVE_D / 2 + 18)
hammer = Part.makeCylinder(7, 12, hp - V(0, 6, 0), Y)
neck = Part.makeBox(9, 8, 22, hp + V(-4.5, -4, 0))
neck.rotate(hp, Y, 25)
spur = Part.makeBox(16, 8, 5, hp + V(-14, -4, 18))
spur.rotate(hp, Y, 25)
hammer = hammer.fuse(neck).fuse(spur)

# ---------------------------------------------------------------- grip
a = math.radians(GRIP_ANGLE)
d = V(-math.cos(a), 0, -math.sin(a))         # down and back
n = V(-math.sin(a), 0, math.cos(a))          # across the grip, in the side plane
start = V(x_cap + 14, 0, z_valve - 8)
sections = [(0.0, 46, 30), (0.35, 40, 28), (0.75, 46, 32), (0.93, 60, 38), (1.0, 64, 40)]
wires = []
for t, h, w in sections:
    c = start + d * (GRIP_LEN * t)
    e = Part.Ellipse(c + n * (h / 2), c + Y * (w / 2), c)
    wires.append(Part.Wire(e.toShape()))
grip = Part.makeLoft(wires, True, False)
c_end = start + d * GRIP_LEN
cap_wires = [wires[-1]]
for k, (dt, s) in enumerate(((5, 1.04), (9, 0.92))):
    c = c_end + d * dt
    e = Part.Ellipse(c + n * (64 * s / 2), c + Y * (40 * s / 2), c)
    cap_wires.append(Part.Wire(e.toShape()))
butt_cap = Part.makeLoft(cap_wires, True, False)
gem = Part.makeSphere(7, c_end + d * 10)
hose = Part.makeCylinder(3, 60, c_end + d * 12, d)
grip_collar = Part.makeLoft([Part.Wire(Part.Ellipse(start + d * 2 + n * 25, start + d * 2 + Y * 17, start + d * 2).toShape()),
                             Part.Wire(Part.Ellipse(start + d * 10 + n * 24, start + d * 10 + Y * 16.5, start + d * 10).toShape())],
                            True, False)

# ---------------------------------------------------------------- trigger guard and trigger
z_guard = z_valve - VALVE_D / 2 - 4          # housing bottom
gc = V(x_cap + 52, 0, z_guard - 2)
guard = Part.makeTorus(17, 2.6, gc, Y).common(Part.makeBox(60, 20, 30, gc + V(-30, -10, -30)))   # lower half
spur_g = Part.makeTorus(9, 2.2, gc + V(-24, 0, -20), Y).common(Part.makeBox(30, 20, 20, gc + V(-40, -10, -40)))
trigger = Part.makeTorus(14, 2.0, gc + V(12, 0, -2), Y).common(Part.makeBox(16, 20, 16, gc + V(-2, -10, -18)))

# ---------------------------------------------------------------- document
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
parts = [("Barrels", barrels, STEEL), ("Barrel_fill", fill, IRON), ("Rear_band", rear_band, BRASS),
         ("Front_band", front_band, BRASS), ("Chamber_axle", axle, STEEL), ("Axle_nut", axle_nut, BRASS),
         ("Lock_housing", housing, IRON), ("Bosses", bosses, IRON), ("Boss_rims", boss_rims, BRASS),
         ("Hammer", hammer, IRON), ("Grip", grip, WOOD), ("Grip_collar", grip_collar, BRASS),
         ("Butt_cap", butt_cap, STEEL), ("Gem_inlet", gem, GEM), ("Hose", hose, (0.1, 0.1, 0.1)),
         ("Trigger_guard", guard.fuse(spur_g), BRASS), ("Trigger", trigger, IRON),
         ("Valve_v11_inside", valve, (0.4, 0.6, 0.85))]
for n_, s, col in parts:
    o = doc.addObject("Part::Feature", n_)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = col
        if n_ == "Valve_v11_inside":
            o.ViewObject.Visibility = False
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewFront()
    Gui.SendMsgToActiveView("ViewFit")
length = (-SPACER + CHAMBER_LEN + 9) - (c_end + d * 9).x
print(NAME, ": block Ø%.0f, length ~%.0f mm (axle nut to butt cap)" % (block_d + 4, length))
