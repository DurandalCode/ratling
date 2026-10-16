# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, the combined variant.

The barrel block stands still along its axis and turns free; the shot is
sealed by a lock: a sleeve in the valve face, driven onto the breech of the
bottom barrel by its own small piston (lock pressure from the first stage
of a two-stage trigger), then pushed harder by the shot itself. The second
stage vents the v1.1 valve's pilot.

    trigger travel:  bolt down ─ block turns 60 deg ─ bolt in ─ lock ─ fire
    release:         vent shut (pilot recharges) ─ lock off ─ pawl back

Indexing: six notches in the hub's rear face between the barrels, a pawl
sector turning round the axle (the chamber tube) in the 4 mm space between
the lock housing and the hub, driven by a slider on the right side through
a radial slot in its arm. Stop: a spring bolt under the hub enters a notch
in the hub's rim under the firing barrel.

Plain masses at their sizes, posed along the trigger travel (0..1):
groups Pose_00 .. Pose_100, Pose_00 shown. Frame: x forward (muzzle), y to
the right seen from behind, z up; block axis on x; the firing barrel at the
bottom. Not parts yet.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/mech_layout.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
STAGE3_LIBRARY = True
exec(open(os.path.join(REPO, "module", "stage3_qev.py")).read())      # v1.1 body, cap
STAGE3_LIBRARY = False

NAME = "pistol_mech_layout"
V = App.Vector
XA, YA, ZA = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

# ---------------------------------------------------------------- parameters
R_RING = 27.0                       # barrel ring = v1's chamber-to-seat distance
Z_FIRE = -R_RING
BARREL_OD = 25.0
HUB_R, HUB_X0, HUB_T = 42.5, 0.5, 22.0      # hub rear face at x = HUB_X0
STUB = 60.0                         # barrel stubs for the mock-up
GAP = 4.0                           # lock housing face at x = -GAP: room for the pawl sector
LOCK_H = 24.0                       # lock housing length
X_BODY_TOP = -GAP - LOCK_H
LOCK_PISTON_D = 28.1                # 24 x 2 O-ring on the sleeve's flange
SLEEVE_BORE = 23.5                  # 11/16 x 1/8 O-ring on the sleeve
NOSE_D = 19.0

NOTCH_R = (14.5, 18.5)              # pawl notches in the hub's rear face, between barrels
NOTCH_DEPTH = 3.0
NOTCH_W = 4.0                       # tangential
SECTOR_R = (12.9, 15.3)             # ring round the axle
SECTOR_X = (-GAP + 0.4, -0.4)
ARM_R = 31.0                        # drive arm, radial slot 26..31
PIN_R0 = 28.3                       # slider pin radius at the ends of the stroke: y = 24.5
ARM_A0 = 30.0                       # arm angle at rest; turns to -30
PAWL_A0 = 60.0                      # pawl in the notch at 60 deg at rest, drives it to 0
SLIDER_Y = (23.0, 30.0)
SLIDER_X = (-9.0, -5.0)             # behind the sector, right of the lock housing (y > 23)

BOLT = (5.0, 6.0)                   # x, y section
BOLT_X0 = 3.0
BOLT_DEPTH = 6.0                    # into the rim notch
RIM_NOTCH = (2.5, 8.5)              # x range of the rim notches (behind the barrel sockets)

TRIGGER_PIVOT = V(-46, 0, -66)
VALVE_BOX = (22.0, 24.0, 52.0)      # M3R110, rough envelope (to be measured)

TRAVEL = (0.0, 0.25, 0.5, 0.75, 1.0)


# ---------------------------------------------------------------- timing (trigger travel t = 0..1)
def ramp(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else 0.5 - 0.5 * math.cos(math.pi * (t - a) / (b - a))


def bolt_down(t):           # 1 = fully out of the rim
    return ramp(t, 0.03, 0.12) * (1 - ramp(t, 0.66, 0.72))


def turn(t):                # block / sector turn, 0..1 of 60 deg
    return ramp(t, 0.14, 0.64)


def lock(t):
    return ramp(t, 0.76, 0.84)


def fire(t):
    return ramp(t, 0.92, 0.98)


# ---------------------------------------------------------------- helpers
def cyl_x(d, x0, x1, y=0.0, z=0.0):
    return Part.makeCylinder(d / 2, x1 - x0, V(x0, y, z), XA)


def polar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def turned(shape, deg):
    s = shape.copy()
    s.rotate(V(0, 0, 0), XA, deg)
    return s


def body_frame_to_pistol(shape):
    """v1.1 body frame (x to the chamber, z out of the barrel face) -> pistol frame."""
    m = App.Matrix(0, 0, 1, X_BODY_TOP - BODY_H,
                   0, -1, 0, 0,
                   1, 0, 0, Z_FIRE,
                   0, 0, 0, 1)
    return shape.transformGeometry(m)


# ---------------------------------------------------------------- fixed: valve, lock, axle
valve_body = body_frame_to_pistol(body)
valve_cap = body_frame_to_pistol(cap_a)
lock_housing = (cyl_x(BREECH_FLANGE_D, -GAP - LOCK_H, -GAP, 0, Z_FIRE)
                .common(box(-GAP - LOCK_H - 1, -GAP + 1, -30, 30, Z_FIRE - 30, Z_FIRE + BREECH_FLAT_X))
                .cut(cyl_x(LOCK_PISTON_D, -GAP - 12, -GAP + 1, 0, Z_FIRE))
                .cut(cyl_x(SEAT_D, -GAP - LOCK_H - 1, -GAP + 1, 0, Z_FIRE)))
lock_port = cyl_x(6, 0, 10, 0, 0)
lock_port.rotate(V(0, 0, 0), ZA, 90)
lock_port.translate(V(-GAP - 8, -BREECH_FLANGE_D / 2 + 2, Z_FIRE))
axle = cyl_x(BARREL_OD, X_BODY_TOP, HUB_X0 + HUB_T + STUB + 20).cut(cyl_x(23.8, X_BODY_TOP - 1, 200))


def lock_sleeve(t):
    x_nose = -GAP + 0.2 + lock(t) * (GAP + HUB_X0 - 0.2 - 0.1)     # nose face: rest -> on the breech
    s = cyl_x(LOCK_PISTON_D - 0.4, x_nose - 9, x_nose - 6, 0, Z_FIRE)
    s = s.fuse(cyl_x(SLEEVE_BORE - 0.2, x_nose - 16, x_nose - 6, 0, Z_FIRE))
    s = s.fuse(cyl_x(NOSE_D, x_nose - 6, x_nose, 0, Z_FIRE))
    return s.cut(cyl_x(SEAT_D, x_nose - 20, x_nose + 1, 0, Z_FIRE))


# ---------------------------------------------------------------- block (turns)
hub = cyl_x(2 * HUB_R, HUB_X0, HUB_X0 + HUB_T)
for i in range(6):
    y, z = polar(R_RING, -90 + 60 * i)
    hub = hub.cut(cyl_x(SEAT_D, HUB_X0 - 1, HUB_X0 + 10, y, z)).cut(cyl_x(BARREL_OD + 0.3, HUB_X0 + 9, HUB_X0 + HUB_T + 1, y, z))
    rn = Part.makeBox(RIM_NOTCH[1] - RIM_NOTCH[0], BOLT[1] + 1, BOLT_DEPTH + 1,
                      V(HUB_X0 + RIM_NOTCH[0], -(BOLT[1] + 1) / 2, -HUB_R - 1))
    hub = hub.cut(turned(rn, 60 * i))
    a = 60 * i                                          # pawl notches between the barrels
    n = Part.makeBox(NOTCH_DEPTH + 1, NOTCH_W, NOTCH_R[1] - NOTCH_R[0], V(HUB_X0 - 1, -NOTCH_W / 2, NOTCH_R[0]))
    hub = hub.cut(turned(n, a - 90))
hub = hub.cut(cyl_x(BARREL_OD + 0.6, HUB_X0 - 1, HUB_X0 + HUB_T + 1))
barrels = Part.makeCompound([cyl_x(BARREL_OD, HUB_X0 + 9, HUB_X0 + HUB_T + STUB, *polar(R_RING, -90 + 60 * i))
                             .cut(cyl_x(23.8, 0, 300, *polar(R_RING, -90 + 60 * i))) for i in range(6)])
oring_faces = Part.makeCompound([cyl_x(23.8, HUB_X0 - 0.6, HUB_X0, *polar(R_RING, -90 + 60 * i))
                                 .cut(cyl_x(16.2, -5, 5, *polar(R_RING, -90 + 60 * i))) for i in range(6)])
front_plate = cyl_x(2 * HUB_R - 6, HUB_X0 + HUB_T + STUB - 8, HUB_X0 + HUB_T + STUB).cut(
    cyl_x(BARREL_OD + 0.6, 0, 300))
for i in range(6):
    front_plate = front_plate.cut(cyl_x(BARREL_OD + 0.3, 0, 300, *polar(R_RING, -90 + 60 * i)))
block = Part.makeCompound([hub, barrels, front_plate])

# ---------------------------------------------------------------- pawl sector (turns round the axle)
sector0 = cyl_x(2 * SECTOR_R[1], *SECTOR_X).cut(cyl_x(2 * SECTOR_R[0], SECTOR_X[0] - 1, SECTOR_X[1] + 1))
arm = Part.makeBox(SECTOR_X[1] - SECTOR_X[0], ARM_R - SECTOR_R[0], 8, V(SECTOR_X[0], SECTOR_R[0], -4))
slot_r = (PIN_R0 * math.cos(math.radians(30)) - 2.0, PIN_R0 + 1.5)       # pin runs 24.5 .. 28.3 out
arm = arm.cut(Part.makeBox(10, slot_r[1] - slot_r[0], 3.4, V(SECTOR_X[0] - 1, slot_r[0], -1.7)))
sector0 = sector0.fuse(turned(arm, ARM_A0))                               # built along +y = 0 deg
pawl = Part.makeBox(SECTOR_X[1] - SECTOR_X[0] + HUB_X0 + 2.0, NOTCH_W - 0.8, NOTCH_R[1] - SECTOR_R[1] - 0.5,
                    V(SECTOR_X[0], -(NOTCH_W - 0.8) / 2, SECTOR_R[1] - 0.5))
sector0 = sector0.fuse(turned(pawl, PAWL_A0 - 90))


def sector_at(t):
    return turned(sector0, -60 * turn(t))


def slider_pin(t):
    """The pin is fixed in the slider, which runs on a vertical line; it slides out along the arm's slot."""
    a = ARM_A0 - 60 * turn(t)
    y = PIN_R0 * math.cos(math.radians(ARM_A0))
    return V((SLIDER_X[0] + SLIDER_X[1]) / 2, y, y * math.tan(math.radians(a)))


def slider_at(t):
    p = slider_pin(t)
    s = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], p.z - 70, p.z + 6)
    pin = cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], p.y, p.z)
    return s, pin


def bolt_at(t):
    top = -HUB_R + BOLT_DEPTH - bolt_down(t) * (BOLT_DEPTH + 1)
    return box(HUB_X0 + BOLT_X0, HUB_X0 + BOLT_X0 + BOLT[0], -BOLT[1] / 2, BOLT[1] / 2, top - 22, top)


# ---------------------------------------------------------------- trigger and its valves (rough)
def trigger_at(t):
    phi = -38.0 * t                                     # pulled back: turns clockwise seen from +y
    blade = box(-4, 6, -3, 3, -32, 0).fuse(box(-6, 40, -3, 3, -4, 4))      # finger blade + forward cam arm
    blade.translate(TRIGGER_PIVOT)
    blade.rotate(TRIGGER_PIVOT, YA, -phi)
    return blade


valves = Part.makeCompound([box(-82, -82 + VALVE_BOX[0], -VALVE_BOX[1] / 2, VALVE_BOX[1] / 2, z0, z0 + VALVE_BOX[2] / 2)
                            for z0 in (-125, -100)])
rollers = Part.makeCompound([Part.makeCylinder(5, 8, V(-60 + dx, -4, z), YA) for dx, z in ((0, -112), (-3, -88))])

# ---------------------------------------------------------------- checks along the travel
report = [NAME]
for t in TRAVEL:
    sec, (sl, pin), bt = sector_at(t), slider_at(t), bolt_at(t)
    blk = turned(block, -60 * turn(t))
    p = slider_pin(t)
    report.append("  t=%.2f  turn %4.1f deg  slider pin z %+6.1f  bolt %s  lock %s  fire %s  | hits: sector/lock %.1f, slider/lock %.1f, slider/hub %.1f, bolt/hub %.1f"
                  % (t, 60 * turn(t), p.z, "in " if bolt_down(t) < 0.5 else "out", "on " if lock(t) > 0.5 else "off",
                     "yes" if fire(t) > 0.5 else "no ", sec.common(lock_housing).Volume, sl.common(lock_housing).Volume,
                     sl.common(blk).Volume, bt.common(blk).Volume))
travel_slider = slider_pin(0).z - slider_pin(1).z
report.append("  slider stroke %.1f mm for 60 deg; pin slides %.1f..%.1f out along the arm"
              % (travel_slider, slider_pin(0.4).y, PIN_R0))
report.append("  lock: piston Ø%.1f round the Ø%.1f sleeve: %.0f N at %.0f bar; shot adds %.0f N"
              % (LOCK_PISTON_D, SLEEVE_BORE, P_WORK_BAR * 0.1 * math.pi / 4 * (LOCK_PISTON_D ** 2 - SLEEVE_BORE ** 2),
                 P_WORK_BAR, P_WORK_BAR * 0.1 * math.pi / 4 * (SLEEVE_BORE ** 2 - 17.0 ** 2)))
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


fixed = doc.addObject("App::DocumentObjectGroup", "Fixed")
for n, s, c, tr in (("Valve_body_v11", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap_v11", valve_cap, (0.45, 0.65, 0.85), 0),
                    ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 30), ("Lock_port", lock_port, (0.7, 0.7, 0.7), 0),
                    ("Chamber_axle", axle, (0.7, 0.7, 0.7), 60), ("Trigger_valves_M3R110", valves, (0.3, 0.3, 0.8), 40),
                    ("Valve_rollers", rollers, (0.2, 0.2, 0.2), 0)):
    add(fixed, n, s, c, tr)
for t in TRAVEL:
    g = doc.addObject("App::DocumentObjectGroup", "Pose_%03d" % int(round(t * 100)))
    sl, pin = slider_at(t)
    for n, s, c, tr in (("Block", turned(block, -60 * turn(t)), (0.55, 0.55, 0.6), 50),
                        ("Breech_orings", turned(oring_faces, -60 * turn(t)), (0.8, 0.1, 0.1), 0),
                        ("Pawl_sector", sector_at(t), (0.9, 0.6, 0.1), 0), ("Slider", sl, (0.9, 0.8, 0.2), 0),
                        ("Slider_pin", pin, (0.2, 0.2, 0.2), 0), ("Bolt", bolt_at(t), (0.8, 0.2, 0.2), 0),
                        ("Lock_sleeve", lock_sleeve(t), (0.2, 0.7, 0.3), 0), ("Trigger", trigger_at(t), (0.3, 0.3, 0.3), 0)):
        add(g, "%s_%03d" % (n, int(round(t * 100))), s, c, tr)
    if App.GuiUp and t > 0:
        for o in g.Group:
            o.ViewObject.Visibility = False
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewRear()
    Gui.SendMsgToActiveView("ViewFit")
