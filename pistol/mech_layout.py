# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, lever-action variant.

The barrel block stands still along its axis and turns free; the shot is
sealed by a lock: a sleeve in the valve face, driven onto the breech of the
bottom barrel by its own small piston (lock pressure from the first stage
of a two-stage trigger), then pushed harder by the shot itself. The second
stage vents the v1.1 valve's pilot. The trigger does nothing else.

The block is turned by a Winchester-style lever round the trigger:

    lever open (down):  slider up, pawl sector swings back, its tooth bent
                        back out of the notch, into the next one; the
                        detent holds the block
    lever closed (up):  slider down, sector turns the block 60 deg; the
                        spring detent rides out of its rim notch and
                        clicks into the next
    trigger:            lock on, then fire; release: vent shut, lock off

Indexing: six notches in the hub's rear face between the barrels, a pawl
sector round the axle (the chamber tube) in the 4 mm space in front of the
lock housing, a slider on the right pinned into a radial slot in its arm,
and the lever's short arm in a horizontal slot at the slider's foot (a
Scotch yoke). Detent: a spring bolt under the hub with a V tip.

Plain masses at their sizes. pose(state) gives every moving shape for a
state dict (lever 0 open .. 1 closed, block angle, pawl bend, trigger,
lock, fire); the document shows the closed rest pose and the lever open.
Frame: x forward (muzzle), y to the right seen from behind, z up; block
axis on x; the firing barrel at the bottom. Not parts yet.

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

TRIGGER_PIVOT = V(-52, 0, -70)     # low enough that its tail clears the valve cap
VALVE_BOX = (22.0, 24.0, 52.0)      # M3R110, rough envelope (to be measured)

# Lever: short arm in a horizontal slot at the slider's foot (Scotch yoke)
LEVER_ARM = PIN_R0 * math.sin(math.radians(30)) / math.sin(math.radians(25))   # +-25 deg -> slider +-14.1
LEVER_SWING = (25.0, -25.0)         # short arm angle: open .. closed (up is positive)
YOKE_DROP = 64.0                    # slider foot slot this far under the slider pin
LEVER_PIVOT = V((SLIDER_X[0] + SLIDER_X[1]) / 2 - LEVER_ARM * (1 + math.cos(math.radians(25))) / 2, 0, -YOKE_DROP)
LEVER_ARM_Y = (SLIDER_Y[1], SLIDER_Y[1] + 3.0)
DETENT_HALF = 6.0                   # deg either side of a notch where the V tip still sits in it


def ramp(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else 0.5 - 0.5 * math.cos(math.pi * (t - a) / (b - a))


def lock(trig):
    return ramp(trig, 0.35, 0.6)


def fire(trig):
    return ramp(trig, 0.85, 0.97)


def lever_angle(lv):                # lv: 0 open .. 1 closed
    return LEVER_SWING[0] + (LEVER_SWING[1] - LEVER_SWING[0]) * lv


def slider_z(lv):                   # slider pin height (pin on the sector arm's slot)
    return LEVER_ARM * math.sin(math.radians(lever_angle(lv)))


def sector_turn(lv):                # 0 open .. -60 closed
    y = PIN_R0 * math.cos(math.radians(ARM_A0))
    return math.degrees(math.atan2(slider_z(lv), y)) - ARM_A0


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


def lock_sleeve(lk):
    x_nose = -GAP + 0.2 + lk * (GAP + HUB_X0 - 0.2 - 0.1)          # nose face: rest -> on the breech
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
sector_base = cyl_x(2 * SECTOR_R[1], *SECTOR_X).cut(cyl_x(2 * SECTOR_R[0], SECTOR_X[0] - 1, SECTOR_X[1] + 1))
arm = Part.makeBox(SECTOR_X[1] - SECTOR_X[0], ARM_R - SECTOR_R[0], 8, V(SECTOR_X[0], SECTOR_R[0], -4))
slot_r = (PIN_R0 * math.cos(math.radians(30)) - 2.0, PIN_R0 + 1.5)       # pin runs 24.5 .. 28.3 out
arm = arm.cut(Part.makeBox(10, slot_r[1] - slot_r[0], 3.4, V(SECTOR_X[0] - 1, slot_r[0], -1.7)))
sector_base = sector_base.fuse(turned(arm, ARM_A0))                       # built along +y = 0 deg
pawl = Part.makeBox(SECTOR_X[1] - SECTOR_X[0] + HUB_X0 + 2.0, NOTCH_W - 0.8, NOTCH_R[1] - SECTOR_R[1] - 0.5,
                    V(SECTOR_X[0], -(NOTCH_W - 0.8) / 2, SECTOR_R[1] - 0.5))
pawl_tooth = turned(pawl, PAWL_A0 - 90)
PAWL_BACK = HUB_X0 + 2.6            # tooth bent back this far: clear of the hub's face


def slider_parts(lv):
    z = slider_z(lv)
    y = PIN_R0 * math.cos(math.radians(ARM_A0))
    xc, zf = (SLIDER_X[0] + SLIDER_X[1]) / 2, z - YOKE_DROP
    s = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], zf, z + 6)
    s = s.fuse(box(xc - 7, xc + 7, SLIDER_Y[0], SLIDER_Y[1], zf - 6, zf + 6))          # foot with the yoke slot
    s = s.cut(box(xc - 3.6, xc + 3.6, SLIDER_Y[0] - 1, SLIDER_Y[1] + 1, zf - 1.7, zf + 1.7))
    return s, cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], y, z)


def bolt_depth(block_deg):
    off = (-block_deg) % 60.0
    off = min(off, 60.0 - off)
    return BOLT_DEPTH * max(0.0, 1.0 - off / DETENT_HALF)


def bolt_shape(block_deg):
    top = -HUB_R + bolt_depth(block_deg)
    return box(HUB_X0 + BOLT_X0, HUB_X0 + BOLT_X0 + BOLT[0], -BOLT[1] / 2, BOLT[1] / 2, top - 22, top)


# ---------------------------------------------------------------- lever (drawn closed, turned about its pivot)
def lever_closed():
    P = LEVER_PIVOT
    a = math.radians(LEVER_SWING[1])
    tip = V(P.x + LEVER_ARM * math.cos(a), 0, P.z + LEVER_ARM * math.sin(a))
    short = Part.makeCylinder(4, LEVER_ARM_Y[1] - LEVER_ARM_Y[0], V(P.x, LEVER_ARM_Y[0], P.z), YA)
    link = Part.makeBox(LEVER_ARM, LEVER_ARM_Y[1] - LEVER_ARM_Y[0], 7, V(P.x, LEVER_ARM_Y[0], P.z - 3.5))
    link.rotate(V(P.x, 0, P.z), YA, -LEVER_SWING[1])
    pin = Part.makeCylinder(1.5, LEVER_ARM_Y[1] - SLIDER_Y[0] + 1, V(tip.x, SLIDER_Y[0] - 1, tip.z), YA)
    shaft = Part.makeCylinder(4, LEVER_ARM_Y[1] + 3, V(P.x, -3, P.z), YA)
    ring_c = V(TRIGGER_PIVOT.x + 2, -3, TRIGGER_PIVOT.z - 24)          # guard round the trigger: a U, open on
    guard = Part.makeCylinder(22, 6, ring_c, YA).cut(Part.makeCylinder(16, 8, ring_c - V(0, 1, 0), YA))   # top, so the
    guard = guard.cut(box(ring_c.x - 23, ring_c.x + 5, -10, 10, ring_c.z, ring_c.z + 30))             # trigger hangs in it
    loop_c = V(ring_c.x - 34, -3, ring_c.z - 8)                         # finger loop behind it
    loop = Part.makeCylinder(15, 6, loop_c, YA).cut(Part.makeCylinder(10, 8, loop_c - V(0, 1, 0), YA))
    front = V(ring_c.x + 19, -3, ring_c.z)                              # strut: pivot -> the U's front end,
    d = V(front.x - P.x, 0, front.z - P.z)                             # clear in front of the trigger
    bar = Part.makeBox(d.Length, 6, 6, V(P.x, -3, P.z - 3))
    bar.rotate(V(P.x, 0, P.z), YA, -math.degrees(math.atan2(d.z, d.x)))
    return Part.makeCompound([short, link, pin, shaft, guard.fuse(loop).fuse(bar)])


LEVER_CLOSED = lever_closed()


def lever_shape(lv):
    s = LEVER_CLOSED.copy()
    s.rotate(V(LEVER_PIVOT.x, 0, LEVER_PIVOT.z), YA, -(lever_angle(lv) - LEVER_SWING[1]))
    return s


def trigger_at(trig):
    blade = box(-4, 6, -3, 3, -28, 0).fuse(box(-16, 4, -3, 3, -4, 4))     # finger blade + tail to the valves
    blade.translate(TRIGGER_PIVOT)
    blade.rotate(TRIGGER_PIVOT, YA, 22.0 * trig)                       # pulled back
    return blade


def pose(st):
    """Moving shapes for a state: lever (0 open..1 closed), block (deg), bend (pawl, 0..1), trig (0..1)."""
    lv, trig = st["lever"], st["trig"]
    sl, pin = slider_parts(lv)
    sec = sector_turn(lv)
    tooth = pawl_tooth.translated(V(-PAWL_BACK * st["bend"], 0, 0))
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, sec), "Pawl": turned(tooth, sec),
            "Slider": sl, "Pin": pin, "Bolt": bolt_shape(st["block"]), "Lever": lever_shape(lv),
            "Sleeve": lock_sleeve(lock(trig)), "Trigger": trigger_at(trig)}


# Two M3R110 side by side behind the valve cap (in the grip), long axis along x; the trigger's
# rear tail lifts their rollers, stage 1 (lock) a little before stage 2 (fire). Envelope only.
VALVES_X = (X_BODY_TOP - BODY_H - CAP_T - 3 - VALVE_BOX[2], X_BODY_TOP - BODY_H - CAP_T - 3)
valves = Part.makeCompound([box(VALVES_X[0], VALVES_X[1], y0, y0 + VALVE_BOX[1], -56, -56 + VALVE_BOX[0])
                            for y0 in (-VALVE_BOX[1] - 1, 1)])
rollers = Part.makeCompound([Part.makeCylinder(4, 8, V(VALVES_X[1] - 6, y0, z), YA)       # tail lifts them 3.5 / 2 mm
                             for y0, z in ((-VALVE_BOX[1] / 2 - 4, -60.0), (VALVE_BOX[1] / 2 - 4, -58.5))])

# ---------------------------------------------------------------- checks along the lever stroke
REST = dict(lever=1.0, block=0.0, bend=0.0, trig=0.0)
report = [NAME]
for lv in (0.0, 0.25, 0.5, 0.75, 1.0):
    st = dict(lever=lv, block=sector_turn(lv), bend=0.0, trig=0.0)          # closing stroke, pawl driving
    sh = pose(st)
    report.append("  lever %.2f  short arm %+5.1f deg  slider pin z %+6.1f  block %+5.1f deg  detent %.1f mm in"
                  "  | hits: sector/lock %.1f slider/lock %.1f slider/block %.1f lever/body %.1f lever/block %.1f"
                  % (lv, lever_angle(lv), slider_z(lv), st["block"], bolt_depth(st["block"]),
                     sh["Sector"].common(lock_housing).Volume, sh["Slider"].common(lock_housing).Volume,
                     sh["Slider"].common(sh["Block"]).Volume, sh["Lever"].common(valve_body).Volume,
                     sh["Lever"].common(sh["Block"]).Volume))
report.append("  lever short arm %.1f mm, swing %.0f deg; slider stroke %.1f mm for 60 deg"
              % (LEVER_ARM, LEVER_SWING[0] - LEVER_SWING[1], slider_z(0) - slider_z(1)))
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


STYLE = {"Block": ((0.55, 0.55, 0.6), 50), "Sector": ((0.9, 0.6, 0.1), 0), "Pawl": ((0.95, 0.35, 0.05), 0),
         "Slider": ((0.9, 0.8, 0.2), 0), "Pin": ((0.2, 0.2, 0.2), 0), "Bolt": ((0.8, 0.2, 0.2), 0),
         "Lever": ((0.35, 0.25, 0.2), 0), "Sleeve": ((0.2, 0.7, 0.3), 0), "Trigger": ((0.3, 0.3, 0.3), 0)}
fixed = doc.addObject("App::DocumentObjectGroup", "Fixed")
for n, s_, c, tr in (("Valve_body_v11", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap_v11", valve_cap, (0.45, 0.65, 0.85), 0),
                     ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 30), ("Lock_port", lock_port, (0.7, 0.7, 0.7), 0),
                     ("Chamber_axle", axle, (0.7, 0.7, 0.7), 60), ("Trigger_valves_M3R110", valves, (0.3, 0.3, 0.8), 40),
                     ("Valve_rollers", rollers, (0.2, 0.2, 0.2), 0)):
    add(fixed, n, s_, c, tr)
for gname, st in (("Rest_closed", REST), ("Lever_open", dict(lever=0.0, block=0.0, bend=0.0, trig=0.0))):
    g = doc.addObject("App::DocumentObjectGroup", gname)
    for n, s_ in pose(st).items():
        add(g, "%s_%s" % (n, gname), s_, *STYLE[n])
    if App.GuiUp and gname != "Rest_closed":
        for o in g.Group:
            o.ViewObject.Visibility = False
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewRear()
    Gui.SendMsgToActiveView("ViewFit")
