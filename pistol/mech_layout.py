# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, lever-action variant.

The barrel block stands still along its axis and turns free; the shot is
sealed by a lock: a sleeve in the valve face, pushed 1 mm onto the breech
of the bottom barrel by a wedge that the lever lifts in the last degrees of
its closing stroke, then pushed harder by the shot itself. The trigger has
one job: it vents the v1.1 valve's pilot through one push-button valve.

The block is turned by a Winchester-style lever, pivoted at the front
under the block, round the trigger and with a finger loop along the grip:

    lever open (down):  slider down, pawl sector swings back, its tooth
                        bent back out of the notch, into the next one; the
                        detent holds the block
    lever closed (up):  slider up, sector turns the block 60 deg; the
                        spring detent rides out of its rim notch and
                        clicks into the next; in the last ~5 deg the
                        lever's bar lifts the wedge and the lock closes
    trigger:            fire; release: vent shut (the chamber recharges)

Indexing: six notches in the hub's rear face between the barrels, a pawl
sector round the axle (the chamber tube) in the 4 mm space in front of the
lock housing, a slider on the right pinned into a radial slot in its arm,
and the lever's short arm, pointing back from its pivot, in a horizontal
slot at the slider's foot (a Scotch yoke). Detent: a spring bolt with a V
tip under the lower left barrel. Trigger valve: one mini 3/2 push-button
valve right behind the trigger.

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
try:
    VALVE                           # 'v11' (the valve as built) or 'v13' (module/stage3_v13.py: Ø16 seat), set before exec
except NameError:
    VALVE = "v11"
if VALVE == "v13":
    # No tube screws and no rod: the chamber plug rests on the front strap (hammer_assembly.py), which is tied to the
    # cage and the valve body, so the tube only seals. Face ring 20 x 2 on the hub: 22 x 2.5 would not fit between barrels.
    OVERRIDE = dict(TUBE_SCREWS=False, SEAT_D=16.0, ORING_ID=19.0, ORING_CS=2.5, FACE_ORING_ID=20.0, FACE_ORING_CS=2.0,
                    GROOVE_WALL_MIN=1.5)
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
HUB_SEAT = 9.0                      # the breech seat's depth in the hub; the barrel sockets from there
FRONT_T = 8.0                       # front plate
try:
    STUB                            # barrels past the hub: stubs for the mock-up, or set before exec
except NameError:
    STUB = 60.0
GAP = 4.0                           # lock housing face at x = -GAP: room for the pawl sector
LOCK_H = 24.0                       # lock housing length
X_BODY_TOP = -GAP - LOCK_H
LOCK_PISTON_D = 28.1                # bore for the sleeve's flange
LOCK_STROKE = 1.0                   # nose: this far off the breech at rest
WEDGE_X = (-13.0, -9.6)             # fixed rear face; front face at the flange (rest)
WEDGE_ANGLE = 15.0                  # front face slope: lift x tan -> sleeve stroke
WEDGE_LIFT = LOCK_STROKE / math.tan(math.radians(WEDGE_ANGLE))
WEDGE_SLOT = 4.9                    # wedge slot depth (x) in the housing, from its rear face
SLEEVE_BORE = 23.5                  # 11/16 x 1/8 O-ring on the sleeve
NOSE_D = 19.0 if SEAT_D < 14.0 else 22.0     # the sleeve's nose must reach over the face ring (mid-ring Ø = 2 x (groove out + in) / 2)

NOTCH_R = (14.5, 18.5)              # pawl notches in the hub's rear face, between barrels
NOTCH_DEPTH = 3.0
NOTCH_W = 4.0                       # tangential
NOTCH_SLACK = 0.0                   # notch made this much wider behind the pawl: lost motion before it drives
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

TRIGGER_PIVOT = V(-52, 0, -62)
# Trigger valves: two mini 3/2 push-button valves side by side behind the trigger, plungers
# forward; a bar across the trigger's back meets stage 1 (lock) before stage 2 (fire). Envelope.
MINI_VALVE = (14.0, 36.0)           # Ø, length
MINI_VALVES = ((0.0, -60.0),)                   # y, plunger tip x (plunger 4.5 long): one valve, fire
MINI_Z = TRIGGER_PIVOT.z - 12.0

# Lever (Winchester): pivot at the front, under the block; its short arm runs back to a
# horizontal slot in the slider's foot (Scotch yoke); closing the lever (rear up) drives.
LEVER_ARM = PIN_R0 * math.sin(math.radians(30)) / math.sin(math.radians(25))   # +-25 deg -> slider +-14.1
LEVER_SWING = (-25.0, 25.0)         # short arm elevation (it points back): open .. closed
YOKE_DROP = 52.0                    # slider foot slot this far under the slider pin
LEVER_PIVOT = V((SLIDER_X[0] + SLIDER_X[1]) / 2 + LEVER_ARM * (1 + math.cos(math.radians(25))) / 2, 0, -YOKE_DROP)
LEVER_ARM_Y = (SLIDER_Y[1], SLIDER_Y[1] + 3.0)
LEVER_BAR_Z = -82.0                 # the lever's bar runs back under the frame at this height
DETENT_HALF = 6.0                   # deg either side of a notch where the V tip still sits in it
DETENT_ANGLE = -150.0               # under the lower left barrel: the lever's bar has the bottom

# Grip (shared with pistol_assembly.py; the lever's finger loop follows its front)
GRIP_START = V(-92.0, 0, -62.0)
GRIP_ANGLE = 36.0
GRIP_LEN = 118.0
GRIP_SECTIONS = ((0.0, 48, 34), (0.4, 40, 31), (0.8, 44, 33), (1.0, 48, 36))   # t, depth, width
LOOP = dict(t=(0.12, 0.62), gap=4.0, inner=24.0, rod=6.0)   # finger loop along the grip front
# Lever latch: a spring ball in the grip's front drops into a dimple in the loop's rear strap.
# The 15 deg wedge is self-locking (PLA on PLA), so the shot does not load the lever: the latch
# only keeps it from falling open.
LATCH = dict(t=0.32, ball=5.0, into=1.5)

try:
    globals().update(MECH_OVERRIDES)  # a variant (pistol/hammer_layout.py) sets its own before exec
except NameError:
    pass
try:
    MECH_LIBRARY                    # True: shapes and functions only, no lever checks or document
except NameError:
    MECH_LIBRARY = False


def ramp(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else 0.5 - 0.5 * math.cos(math.pi * (t - a) / (b - a))


def fire(trig):
    return ramp(trig, 0.55, 0.75)


def lever_angle(lv):                # lv: 0 open .. 1 closed
    return LEVER_SWING[0] + (LEVER_SWING[1] - LEVER_SWING[0]) * lv


def slider_z(lv):                   # slider pin height (pin on the sector arm's slot)
    return LEVER_ARM * math.sin(math.radians(lever_angle(lv)))


def sector_turn(lv):                # -60 open .. 0 closed
    y = PIN_R0 * math.cos(math.radians(ARM_A0))
    return math.degrees(math.atan2(slider_z(lv), y)) - ARM_A0


def block_drive(lv):                # block turn on the closing stroke: 0 open .. +60 closed
    return sector_turn(lv) - sector_turn(0.0)


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
                .cut(cyl_x(SLEEVE_BORE, -GAP - 17, -GAP - 11.9, 0, Z_FIRE))              # the sleeve's tube
                .cut(cyl_x(SEAT_D, -GAP - LOCK_H - 1, -GAP + 1, 0, Z_FIRE))
                .cut(box(WEDGE_X[0] - 0.3, WEDGE_X[0] + WEDGE_SLOT, -4.5, 4.5, Z_FIRE - 30, Z_FIRE - 10))   # wedge slot
                .cut(cyl_x(LOCK_PISTON_D, WEDGE_X[0] - 0.3, WEDGE_X[0] + WEDGE_SLOT, 0, Z_FIRE - WEDGE_LIFT)))  # its fork, dropped
# Bolts into the body's breech pilots (body frame (x, y) -> pistol (y, z) = (-y, Z_FIRE + x)). Two of the three:
# the hammer variant's pusher lug runs where the one at 270 deg would go.
LOCK_BOLTS = (90.0, 180.0)
lock_housing = lock_housing.cut(Part.makeCompound([
    cyl_x(BREECH_BOLT_HOLE, -GAP - LOCK_H - 1, -GAP + 1, -BREECH_BOLT_R * math.sin(math.radians(a)),
          Z_FIRE + BREECH_BOLT_R * math.cos(math.radians(a))) for a in LOCK_BOLTS]))
lock_port = cyl_x(6, 0, 10, 0, 0)
lock_port.rotate(V(0, 0, 0), ZA, 90)
lock_port.translate(V(-GAP - 8, -BREECH_FLANGE_D / 2 + 2, Z_FIRE))
axle = cyl_x(BARREL_OD, X_BODY_TOP, HUB_X0 + HUB_T + STUB + 20).cut(cyl_x(23.8, X_BODY_TOP - 1, HUB_X0 + HUB_T + STUB + 21))


def lock_sleeve(lk):
    x_nose = HUB_X0 - 0.1 - LOCK_STROKE * (1 - lk)                  # nose face: 1 mm off -> on the breech
    s = cyl_x(LOCK_PISTON_D - 0.4, x_nose - 9, x_nose - 6, 0, Z_FIRE)
    s = s.fuse(cyl_x(SLEEVE_BORE - 0.2, x_nose - 16, x_nose - 6, 0, Z_FIRE))
    s = s.fuse(cyl_x(NOSE_D, x_nose - 6, x_nose, 0, Z_FIRE))
    return s.cut(cyl_x(SEAT_D, x_nose - 20, x_nose + 1, 0, Z_FIRE))


def wedge_shape(lift):
    """Rear face on the housing, front face sloping back as it rises: lift pushes the flange."""
    t = math.tan(math.radians(WEDGE_ANGLE))
    z_c = Z_FIRE - (LOCK_PISTON_D - 0.4) / 2              # where it bears: the flange's bottom edge
    th = lambda z: (WEDGE_X[1] - WEDGE_X[0] - 0.1) + (z_c - z) * t   # thickness at height z (wedge at rest)
    z_top, z_bot = Z_FIRE + 2.0, -82.6
    th_max, th_min = WEDGE_SLOT - 0.3, 1.2                # the slope only where it can bear on the flange
    z_max, z_min = z_c - (th_max - th(z_c)) / t, z_c + (th(z_c) - th_min) / t
    x0 = WEDGE_X[0]
    prof = Part.Face(Part.makePolygon([V(x0, 0, z_bot), V(x0 + th_max, 0, z_bot), V(x0 + th_max, 0, z_max),
                                       V(x0 + th_min, 0, z_min), V(x0 + th_min, 0, z_top), V(x0, 0, z_top),
                                       V(x0, 0, z_bot)]))
    fork = prof.extrude(V(0, 28, 0)).translated(V(0, -14, 0))
    dz = WEDGE_LIFT                                       # stays inside the bore and clear of the tube when lifted
    fork = fork.common(cyl_x(LOCK_PISTON_D - 0.4, -30, 0, 0, Z_FIRE - dz).fuse(box(-30, 0, -4, 4, -200, Z_FIRE - 10)))
    fork = fork.cut(cyl_x(SLEEVE_BORE + 0.6, -30, 0, 0, Z_FIRE)).cut(cyl_x(SLEEVE_BORE + 0.6, -30, 0, 0, Z_FIRE - dz))
    fork = fork.cut(box(-30, 0, -(SLEEVE_BORE + 0.6) / 2, (SLEEVE_BORE + 0.6) / 2, Z_FIRE - dz, Z_FIRE))
    return fork.translated(V(0, 0, lift))


# ---------------------------------------------------------------- block (turns)
hub = cyl_x(2 * HUB_R, HUB_X0, HUB_X0 + HUB_T)
for i in range(6):
    y, z = polar(R_RING, -90 + 60 * i)
    hub = hub.cut(cyl_x(SEAT_D, HUB_X0 - 1, HUB_X0 + HUB_SEAT + 1, y, z)).cut(
        cyl_x(BARREL_OD + 0.3, HUB_X0 + HUB_SEAT, HUB_X0 + HUB_T + 1, y, z))
    rn = Part.makeBox(RIM_NOTCH[1] - RIM_NOTCH[0], BOLT[1] + 1, BOLT_DEPTH + 1,
                      V(HUB_X0 + RIM_NOTCH[0], -(BOLT[1] + 1) / 2, -HUB_R - 1))
    hub = hub.cut(turned(rn, 60 * i))
    a = 60 * i                                          # pawl notches between the barrels
    n = Part.makeBox(NOTCH_DEPTH + 1, NOTCH_W + NOTCH_SLACK, NOTCH_R[1] - NOTCH_R[0], V(HUB_X0 - 1, -NOTCH_W / 2, NOTCH_R[0]))
    hub = hub.cut(turned(n, a - 90))
hub = hub.cut(cyl_x(BARREL_OD + 0.6, HUB_X0 - 1, HUB_X0 + HUB_T + 1))
barrels = Part.makeCompound([cyl_x(BARREL_OD, HUB_X0 + HUB_SEAT, HUB_X0 + HUB_T + STUB, *polar(R_RING, -90 + 60 * i))
                             .cut(cyl_x(23.8, 0, 300, *polar(R_RING, -90 + 60 * i))) for i in range(6)])
oring_faces = Part.makeCompound([cyl_x(2 * face_groove_out, HUB_X0 - 0.6, HUB_X0, *polar(R_RING, -90 + 60 * i))
                                 .cut(cyl_x(2 * face_groove_in, -5, 5, *polar(R_RING, -90 + 60 * i))) for i in range(6)])
front_plate = cyl_x(2 * HUB_R - 6, HUB_X0 + HUB_T + STUB - FRONT_T, HUB_X0 + HUB_T + STUB).cut(
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
    return turned(box(HUB_X0 + BOLT_X0, HUB_X0 + BOLT_X0 + BOLT[0], -BOLT[1] / 2, BOLT[1] / 2, top - 22, top),
                  DETENT_ANGLE + 90)


# ---------------------------------------------------------------- lever (drawn closed, turned about its pivot)
def _rod(p0, p1, w=6.0, y0=-3.0, t=6.0):
    d = V(p1.x - p0.x, 0, p1.z - p0.z)
    r = Part.makeBox(d.Length, t, w, V(p0.x, y0, p0.z - w / 2))
    r.rotate(V(p0.x, 0, p0.z), YA, -math.degrees(math.atan2(d.z, d.x)))
    return r.fuse(Part.makeCylinder(w / 2, t, V(p0.x, y0, p0.z), YA)).fuse(Part.makeCylinder(w / 2, t, V(p1.x, y0, p1.z), YA))


def _stadium(c0, c1, r, y0=-3.0, t=6.0):
    """Solid stadium (two discs joined) in the x-z plane, extruded along y."""
    return _rod(c0, c1, 2 * r, y0, t)


def grip_frame():
    a = math.radians(GRIP_ANGLE)
    gd = V(-math.cos(a), 0, -math.sin(a))       # down the grip
    f = V(math.sin(a), 0, -math.cos(a))         # its front, square to it
    return gd, f


def latch_point():
    """Ball centre: in front of the grip, sunk LATCH['into'] into the loop's rear strap."""
    gd, f = grip_frame()
    h0 = GRIP_SECTIONS[0][1]
    strap_face = h0 / 2 + LOOP["gap"]                    # the rear strap's face towards the grip
    return GRIP_START + gd * (GRIP_LEN * LATCH["t"]) + f * (strap_face + LATCH["into"] - LATCH["ball"] / 2)


def lever_closed():
    P = LEVER_PIVOT
    a = math.radians(LEVER_SWING[1])
    tip = V(P.x - LEVER_ARM * math.cos(a), 0, P.z + LEVER_ARM * math.sin(a))
    short = _rod(P, tip, 7.0, LEVER_ARM_Y[0], LEVER_ARM_Y[1] - LEVER_ARM_Y[0])
    pin = Part.makeCylinder(1.5, LEVER_ARM_Y[1] - SLIDER_Y[0] + 1, V(tip.x, SLIDER_Y[0] - 1, tip.z), YA)
    shaft = Part.makeCylinder(4, LEVER_ARM_Y[1] + 3, V(P.x, -3, P.z), YA)
    boss = Part.makeCylinder(7, 6, V(P.x, -3, P.z), YA)
    gc = V(TRIGGER_PIVOT.x - 2, 0, TRIGGER_PIVOT.z - 24)                # trigger guard: a U, open on top
    guard = Part.makeCylinder(23, 6, gc - V(0, 3, 0), YA).cut(Part.makeCylinder(17, 8, gc - V(0, 4, 0), YA))
    guard = guard.cut(box(gc.x - 24, gc.x + 24, -10, 10, gc.z, gc.z + 30))
    drop = V(P.x - 6, 0, LEVER_BAR_Z)                                   # bar: down from the pivot, back under the frame
    g_front = V(gc.x + 20, 0, gc.z)
    bar = _rod(P, drop).fuse(_rod(drop, V(g_front.x, 0, LEVER_BAR_Z))).fuse(_rod(V(g_front.x, 0, LEVER_BAR_Z), g_front))
    gd, f = grip_frame()                                                # finger loop along the grip front
    h0 = GRIP_SECTIONS[0][1]
    rear0 = GRIP_START + gd * (GRIP_LEN * LOOP["t"][0]) + f * (h0 / 2 + LOOP["gap"] + LOOP["rod"] + LOOP["inner"] / 2)
    rear1 = GRIP_START + gd * (GRIP_LEN * LOOP["t"][1]) + f * (h0 / 2 + LOOP["gap"] + LOOP["rod"] + LOOP["inner"] / 2)
    loop = _stadium(rear0, rear1, LOOP["inner"] / 2 + LOOP["rod"]).cut(
        _stadium(rear0, rear1, LOOP["inner"] / 2, -5.0, 10.0))
    g_rear = V(gc.x - 20, 0, gc.z)
    join = _rod(g_rear, rear0 - gd * ((LOOP["inner"] + LOOP["rod"]) / 2))   # guard's rear end -> top of the loop
    hand = guard.fuse(bar).fuse(loop).fuse(join).cut(Part.makeSphere(LATCH["ball"] / 2 + 0.1, latch_point()))  # latch dimple
    return Part.makeCompound([short, pin, shaft, boss, hand])


LEVER_CLOSED = lever_closed()


def lever_shape(lv):
    """Drawn closed; opening drops the rear (the short arm goes down with it)."""
    s = LEVER_CLOSED.copy()
    s.rotate(V(LEVER_PIVOT.x, 0, LEVER_PIVOT.z), YA, lever_angle(lv) - LEVER_SWING[1])
    return s


def wedge_lift(lv):
    """The lever's bar meets the wedge's foot in the last degrees of closing and lifts it."""
    px, pz = LEVER_PIVOT.x, LEVER_PIVOT.z
    x0, z0 = sum(WEDGE_X) / 2, LEVER_BAR_Z + 3.0                       # bar top under the wedge, closed
    d = math.radians(lever_angle(lv) - LEVER_SWING[1])
    z = pz - (x0 - px) * math.sin(d) + (z0 - pz) * math.cos(d)
    return min(max(z - (z0 - WEDGE_LIFT), 0.0), WEDGE_LIFT)


def lock_of(lv):
    return wedge_lift(lv) / WEDGE_LIFT


def trigger_at(trig):
    blade = box(-4, 6, -3, 3, -28, 0)
    t = blade
    t.translate(TRIGGER_PIVOT)
    t.rotate(TRIGGER_PIVOT, YA, 22.0 * trig)                           # pulled back
    return t


def pose(st):
    """Moving shapes for a state: lever (0 open..1 closed), block (deg), bend (pawl, 0..1), trig (0..1)."""
    lv, trig = st["lever"], st["trig"]
    sl, pin = slider_parts(lv)
    sec = sector_turn(lv)                       # the sector follows the slider
    tooth = pawl_tooth.translated(V(-PAWL_BACK * st["bend"], 0, 0))
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, sec), "Pawl": turned(tooth, sec),
            "Slider": sl, "Pin": pin, "Bolt": bolt_shape(st["block"]), "Lever": lever_shape(lv),
            "Sleeve": lock_sleeve(lock_of(lv)), "Wedge": wedge_shape(wedge_lift(lv)), "Trigger": trigger_at(trig)}


valves = Part.makeCompound([cyl_x(MINI_VALVE[0], tip - MINI_VALVE[1], tip - 4.5, y, MINI_Z)
                            .fuse(cyl_x(5, tip - 4.51, tip, y, MINI_Z)) for y, tip in MINI_VALVES])
valve_bodies = Part.makeCompound([cyl_x(MINI_VALVE[0], tip - MINI_VALVE[1], tip - 4.5, y, MINI_Z)
                                  for y, tip in MINI_VALVES])           # without the plungers, for clearance checks
rollers = Part.makeCompound([cyl_x(4.6, tip - 0.5, tip, y, MINI_Z) for y, tip in MINI_VALVES])     # plunger tips

STYLE = {"Block": ((0.55, 0.55, 0.6), 50), "Sector": ((0.9, 0.6, 0.1), 0), "Pawl": ((0.95, 0.35, 0.05), 0),
         "Slider": ((0.9, 0.8, 0.2), 0), "Pin": ((0.2, 0.2, 0.2), 0), "Bolt": ((0.8, 0.2, 0.2), 0),
         "Lever": ((0.35, 0.25, 0.2), 0), "Sleeve": ((0.2, 0.7, 0.3), 0), "Wedge": ((0.75, 0.45, 0.85), 0),
         "Trigger": ((0.3, 0.3, 0.3), 0)}
REST = dict(lever=1.0, block=0.0, bend=0.0, trig=0.0)
if not MECH_LIBRARY:
    # ---------------------------------------------------------------- checks along the lever stroke
    report = [NAME]
    for lv in (0.0, 0.25, 0.5, 0.75, 1.0):
        st = dict(lever=lv, block=block_drive(lv), bend=0.0, trig=0.0)          # closing stroke, pawl driving
        sh = pose(st)
        report.append("  lever %.2f  short arm %+5.1f deg  slider pin z %+6.1f  block %+5.1f deg  detent %.1f mm in"
                      "  | hits: sector/lock %.1f slider/lock %.1f slider/block %.1f lever/body %.1f lever/block %.1f wedge/lock %.1f wedge/sleeve %.1f"
                      % (lv, lever_angle(lv), slider_z(lv), st["block"], bolt_depth(st["block"]),
                         sh["Sector"].common(lock_housing).Volume, sh["Slider"].common(lock_housing).Volume,
                         sh["Slider"].common(sh["Block"]).Volume, sh["Lever"].common(valve_body).Volume,
                         sh["Lever"].common(sh["Block"]).Volume, sh["Wedge"].common(lock_housing).Volume,
                         sh["Wedge"].common(sh["Sleeve"]).Volume))
    report.append("  lever short arm %.1f mm, swing %.0f deg; slider stroke %.1f mm for 60 deg"
                  % (LEVER_ARM, LEVER_SWING[0] - LEVER_SWING[1], slider_z(0) - slider_z(1)))
    report.append("  lock: wedge %.0f deg, lifted %.1f mm by the lever's last %.1f deg -> sleeve %.1f mm; the shot adds %.0f N"
                  % (WEDGE_ANGLE, WEDGE_LIFT, LEVER_SWING[1] - min(lever_angle(i / 200) for i in range(201) if lock_of(i / 200) > 0),
                     LOCK_STROKE, P_WORK_BAR * 0.1 * math.pi / 4 * (SLEEVE_BORE ** 2 - 17.0 ** 2)))
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
    for n, s_, c, tr in (("Valve_body_v11", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap_v11", valve_cap, (0.45, 0.65, 0.85), 0),
                         ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 30),
                         ("Chamber_axle", axle, (0.7, 0.7, 0.7), 60), ("Trigger_valves", valves, (0.3, 0.3, 0.8), 40),
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
