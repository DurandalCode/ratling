# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, thumb-hammer variant.

The lever variant (pistol/mech_layout.py) needs both hands; this one is
worked by one: the thumb pulls a hammer back and lets it go, the trigger
fires. The block, its ratchet, detent, lock sleeve and the v1.1 valve come
from mech_layout.py unchanged; only what drives them is new. No air is
spent on anything but the shot.

    thumb back (56 deg): the hammer's crank lifts the slider through a
        bracket behind it (a Scotch yoke). Its first 3 mm pull the lock
        pusher back off the sleeve's flange (cam slot in the slider): the
        lock opens. Then the pawl, idle across the notch's lost motion,
        meets the notch wall and turns the block 60 deg; the detent
        clicks.
    thumb off: the mainspring brings the hammer forward, the slider drops
        (the pawl skips back to the next notch) and in its last 3 mm the
        cam drives the pusher onto the flange: the lock closes, held by
        the mainspring. Ready.
    trigger: one stage, it pushes the vent valve: the shot. Let go: vent
        shut, the chamber recharges.

Nothing holds the hammer back: it is a thumb lever that clicks there and
back, not a cocked hammer. Let go half way and the block stops between
barrels; the lock then rests on the web and does not seal: no shot, no
harm; pull it again to the click.

Lock: a ring behind the sleeve's flange, in its bore, with a lug out
through the housing's right side and a pin into a cam slot in the
slider's rear cheek. The ring is glued to the flange (or printed with
it), so the cam pulls the sleeve back as well as pushing it: no return
spring, and the lug keeps the sleeve from turning. The shot itself pushes
the sleeve forward, so the pusher only has to seat it.

Springs (sized in the report):
    mainspring .. two torsion springs on the hammer's shaft, one each
                  side of its hub, one leg on the frame, one on the hammer;
                  they bring the hammer forward and hold the lock shut
    pawl ........ the tooth is a plunger in the sector, a pen spring
                  behind it; it rides out of the notch over its sloped
                  back wall on the way back
    detent ...... a pen spring behind the V bolt
    trigger ..... none: the vent valve's own spring returns it

Plain masses at their sizes, as mech_layout.py. pose(st) for a state
dict (cock 0 forward .. 1 back, block deg, pawl bend, trig 0..1); the
document shows the rest pose and the hammer held back.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/hammer_layout.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")

HAMMER_SWING = 56.0                 # deg, down .. cocked
SECTOR_SWING = 68.0                 # 60 for the block + the notch's lost motion
LOST_DEG = SECTOR_SWING - 60.0
try:
    HUB_T_HAMMER                    # the rear disc: set before exec (hammer_assembly.py needs it for the barrels)
except NameError:
    HUB_T_HAMMER = 14.0
# Block: two discs and the bought tubes. The rear disc: breech seats (9 deep, O-ring faces, pawl notches, detent
# notches in its rim) and 5 mm sockets the barrels are glued into; the front disc 6 mm.
MECH_OVERRIDES = dict(ARM_A0=SECTOR_SWING / 2, PIN_R0=24.5 / math.cos(math.radians(SECTOR_SWING / 2)), ARM_R=33.0,
                      NOTCH_SLACK=16.5 * math.radians(LOST_DEG), HUB_T=HUB_T_HAMMER, FRONT_T=6.0,
                      SLIDER_Y=(23.0, 31.5))             # thicker round its guide rod
MECH_LIBRARY = True
exec(open(os.path.join(REPO, "pistol", "mech_layout.py")).read())
MECH_LIBRARY = False
NAME = "pistol_hammer_layout"

# ---------------------------------------------------------------- pawl and detent: their springs
# The pawl is a plunger: it slides in a boss on the sector's back, a Ø3 pen spring behind it pushing it into the
# notches; the boss swings over the lock housing's flat top. The detent bolt is 12 long, with a Ø4 pen spring
# in a pocket behind it in its housing.
PAWL_X0 = -6.5                      # the plunger's back at rest (its front in the notch, as mech_layout's tooth)
PAWL_BOSS_X0 = -14.2                # the boss's back wall
BOLT_LEN = 12.0
_pw, _ph, _pr0 = NOTCH_W - 0.8, NOTCH_R[1] - SECTOR_R[1] - 0.5, SECTOR_R[1] - 0.5
pawl_tooth = turned(Part.makeBox(HUB_X0 + 2.0 - PAWL_X0, _pw, _ph, V(PAWL_X0, -_pw / 2, _pr0)), PAWL_A0 - 90)
_boss = Part.makeBox(SECTOR_X[0] + 0.01 - PAWL_BOSS_X0, _pw + 2.4, _ph + 2.4, V(PAWL_BOSS_X0, -_pw / 2 - 1.2, _pr0 - 1.2))
_bore = Part.makeBox(SECTOR_X[1] + 1 - (PAWL_BOSS_X0 + 1.2), _pw + 0.3, _ph + 0.3, V(PAWL_BOSS_X0 + 1.2, -_pw / 2 - 0.15, _pr0 - 0.15))
sector_base = sector_base.fuse(turned(_boss, PAWL_A0 - 90)).cut(turned(_bore, PAWL_A0 - 90)).removeSplitter()


def bolt_shape(block_deg):
    top = -HUB_R + bolt_depth(block_deg)
    return turned(box(HUB_X0 + BOLT_X0, HUB_X0 + BOLT_X0 + BOLT[0], -BOLT[1] / 2, BOLT[1] / 2, top - BOLT_LEN, top),
                  DETENT_ANGLE + 90)


def detent_spring_pocket():
    c = Part.makeCylinder(2.15, 10.5, V(HUB_X0 + BOLT_X0 + BOLT[0] / 2, 0, -HUB_R - BOLT_LEN - 10.5), ZA)
    return turned(c, DETENT_ANGLE + 90)


# ---------------------------------------------------------------- parameters
PIN_Y = PIN_R0 * math.cos(math.radians(ARM_A0))                     # slider pin's y (24.5)
HAMMER_PIVOT = V(-82.0, 0, -8.0)    # behind the v1.1 cap, above the grip
HAMMER_ARM = PIN_Y * math.tan(math.radians(SECTOR_SWING / 2)) / math.sin(math.radians(HAMMER_SWING / 2))
HAMMER_R = 10.0                     # its hub
SPUR_AXIS = 95.0                    # the hammer's outline is drawn along this direction at rest (deg from +x)
# Outline, (along the axis, back from it) in mm: a Colt-like neck sweeping back to a chequered comb, a claw
# hooked forward over the top, a lightening hole in the neck.
SPUR_OUTLINE = [(5, -8), (14, -8), (24, -6.5), (31, -5), (37, -6), (43, -9), (44, -6.5), (41, -2), (40.5, 2),
                (41, 7), (40, 12), (37.5, 17), (33.5, 21), (29, 22), (27, 19), (24, 14), (17, 10.5), (9, 9.5), (4, 8)]
SPUR_COMB = [(40.6, 3), (40.6, 7.5), (39.7, 12), (37.4, 16.3), (34, 19.8)]     # teeth along the comb
SPUR_HOLE = (17.0, 1.5, 3.2)        # along, back, radius
SPUR = (95.0 + math.degrees(math.atan2(12.0, 38.0)), math.hypot(38.0, 12.0))   # where the thumb sits: direction, radius
CRANK_Y = (32.0, 35.0)              # the crank on the right, outside the valve body (y 31)
BRACKET_Y = (35.2, 38.2)            # the slider's bracket, outside the crank
SLIDER_REACH = 48.0                 # slider body: from its pin this far down (the cam slot)
CHEEK_X = (-14.5, -7.0)             # slider's rear cheek with the cam slot
PUSHER_T = 3.0
CAM_RISE = 3.0                      # slider rise that opens the lock
TRIGGER_TRAVEL = 23.0               # deg; reset below: the pull that brings the trigger onto the vent valve's face
LOCK_SEAT_N = 20.0                  # sleeve onto the breech's O-ring before the shot (the shot adds ~41 N): bench it
MAINSPRING = dict(d=1.6, od=14.0, coils=6, y=((-30.2, -18.6), (-18.2, -6.6)))   # music wire torsion springs, x2, both left
SPRING_PEG = (30.0, 9.5, 1.5)       # on the hammer's hub, left face: direction at rest, radius, pin radius (the springs' legs)
SLEEVE_R = 7.0                      # the hammer's sleeve on the axle, hub to crank: one printed part
GUIDE_ROD = dict(x=-8.5, y=28.6, d=3.0, z=(-70.5, 25.5))   # the slider runs on a fixed Ø3 steel rod, floor to ceiling


def hammer_rot(c):                  # rotation about +y: cocking turns the spur back (negative)
    return -HAMMER_SWING * c


def crank_angle(c):                 # crank elevation from +x, deg
    return -HAMMER_SWING / 2 + HAMMER_SWING * c


def slider_z(c):                    # replaces mech_layout's: the slider pin height
    return HAMMER_ARM * math.sin(math.radians(crank_angle(c)))


def sector_turn(c):                 # -68 hammer down .. 0 cocked
    return math.degrees(math.atan2(slider_z(c), PIN_Y)) - ARM_A0


def block_drive(c):                 # the pawl crosses the notch's slack first
    return min(max(sector_turn(c) - sector_turn(0.0) - LOST_DEG, 0.0), 60.0)


def lock_h(c):                      # 1 = pusher on the flange
    return 1.0 - min(max((slider_z(c) - slider_z(0.0)) / CAM_RISE, 0.0), 1.0)


def _at(p, deg, r):
    return V(p.x + r * math.cos(math.radians(deg)), 0, p.z + r * math.sin(math.radians(deg)))


def _rot_y(shape, centre, deg):
    s = shape.copy()
    s.rotate(V(centre.x, 0, centre.z), YA, deg)
    return s


# ---------------------------------------------------------------- hammer (drawn down, turned about its pivot)
H = HAMMER_PIVOT
hub_h = Part.makeCylinder(HAMMER_R, 10, V(H.x, -5, H.z), YA)
spur_tip = _at(H, SPUR[0], SPUR[1])
_e1 = V(math.cos(math.radians(SPUR_AXIS)), 0, math.sin(math.radians(SPUR_AXIS)))
_e2 = V(math.cos(math.radians(SPUR_AXIS + 90)), 0, math.sin(math.radians(SPUR_AXIS + 90)))   # back, at rest


def _sp(a, b, y=0.0):
    return V(H.x, y, H.z) + _e1 * a + _e2 * b


spur = Part.Face(Part.makePolygon([_sp(a, b, -4.0) for a, b in SPUR_OUTLINE] + [_sp(*SPUR_OUTLINE[0], y=-4.0)])).extrude(V(0, 8, 0))
spur = spur.cut(Part.makeCylinder(SPUR_HOLE[2], 10, _sp(SPUR_HOLE[0], SPUR_HOLE[1], -5.0), YA))
for (a0, b0), (a1, b1) in zip(SPUR_COMB, SPUR_COMB[1:]):                      # chequering: grooves across the comb
    c_ = _sp((a0 + a1) / 2, (b0 + b1) / 2, -6.0)
    t_ = (_sp(a1, b1) - _sp(a0, b0)).normalize()                                  # along the comb
    g = Part.makeBox(1.2, 12, 1.2, V(-0.6, 0, -0.6))
    g.rotate(V(0, 0, 0), YA, -math.degrees(math.atan2(t_.z, t_.x)))
    spur = spur.cut(g.translated(c_))
spur = spur.fuse(Part.makeCylinder(4.0, 10, _sp(28.5, 19.5, -5.0), YA))          # a knuckle at the comb's heel, wider
c_tip0 = _at(H, crank_angle(0.0), HAMMER_ARM)
crank = _rod(H, c_tip0, 8.0, CRANK_Y[0], CRANK_Y[1] - CRANK_Y[0])
crank_pin = Part.makeCylinder(1.5, BRACKET_Y[1] + 0.5 - CRANK_Y[0], V(c_tip0.x, CRANK_Y[0], c_tip0.z), YA)
SHAFT_Y = (-42.0, CRANK_Y[1] + 6.0)  # a fixed Ø8 steel axle through both walls of the cage; the hammer turns on it
shaft = Part.makeCylinder(4.0, SHAFT_Y[1] - SHAFT_Y[0], V(H.x, SHAFT_Y[0], H.z), YA)
sleeve = Part.makeCylinder(SLEEVE_R, CRANK_Y[0] - 4.9, V(H.x, 4.9, H.z), YA)          # hub to crank: one part
peg_at = _at(H, SPRING_PEG[0], SPRING_PEG[1])
peg = Part.makeCylinder(SPRING_PEG[2], -4.9 - MAINSPRING["y"][0][0], V(peg_at.x, MAINSPRING["y"][0][0], peg_at.z), YA)
hammer_body = hub_h.fuse(spur).fuse(sleeve).fuse(crank).fuse(peg).cut(
    Part.makeCylinder(4.15, 100, V(H.x, -50, H.z), YA)).removeSplitter()
HAMMER = Part.makeCompound([hammer_body, crank_pin])


def hammer_shape(c):
    return _rot_y(HAMMER, H, hammer_rot(c))


def crank_tip(c):
    return _at(H, crank_angle(c), HAMMER_ARM)


# ---------------------------------------------------------------- slider: pin on the sector arm, bracket back to the crank, cam cheek
X_LOCKED = HUB_X0 - 0.1 - 9.0 - PUSHER_T / 2          # pusher centre when the sleeve is on the breech
X_OPEN = X_LOCKED - LOCK_STROKE
D_YOKE = H.z                                          # bracket slot this far above the slider pin


def cam_slot():
    """In the slider's frame (its pin at z = 0): the path of the pusher's pin."""
    r0 = Z_FIRE - slider_z(0.0)                       # pin's height on the slider, hammer down
    pts = [V(X_LOCKED, 0, r0 + 2.0), V(X_LOCKED, 0, r0), V(X_OPEN, 0, r0 - CAM_RISE),
           V(X_OPEN, 0, Z_FIRE - slider_z(1.0) - 2.0)]
    s = None
    for a, b in zip(pts, pts[1:]):
        seg = _rod(a, b, 3.4, SLIDER_Y[0] - 1, SLIDER_Y[1] - SLIDER_Y[0] + 2)
        s = seg if s is None else s.fuse(seg)
    return s


xs = [crank_tip(i / 20).x for i in range(21)]
SLIDER_H = (box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], -SLIDER_REACH, 6)
            .fuse(box(CHEEK_X[0], CHEEK_X[1], SLIDER_Y[0], SLIDER_Y[1], -SLIDER_REACH, 6))
            .fuse(box(CHEEK_X[0], SLIDER_X[1], SLIDER_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .fuse(box(min(xs) - 8, CHEEK_X[0] + 0.01, BRACKET_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .cut(box(min(xs) - 2, max(xs) + 2, BRACKET_Y[0] - 1, BRACKET_Y[1] + 1, D_YOKE - 1.7, D_YOKE + 1.7))
            .cut(cam_slot())
            .cut(Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.15, 200, V(GUIDE_ROD["x"], GUIDE_ROD["y"], -100), ZA)))


def slider_h(c):
    z = slider_z(c)
    return SLIDER_H.translated(V(0, 0, z)), cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], PIN_Y, z)


# ---------------------------------------------------------------- lock pusher (ring in the flange's bore, lug and pin to the cam)
ring = cyl_x(LOCK_PISTON_D - 0.4, -PUSHER_T / 2, PUSHER_T / 2, 0, Z_FIRE).cut(
    cyl_x(SLEEVE_BORE + 0.6, -5, 5, 0, Z_FIRE))
lug = box(-PUSHER_T / 2, PUSHER_T / 2, (SLEEVE_BORE + 1) / 2, SLIDER_Y[0] - 0.5, Z_FIRE - 3, Z_FIRE + 3)
cam_pin = Part.makeCylinder(1.5, 2.5 + 3.0, V(0, SLIDER_Y[0] - 2.5, Z_FIRE), YA)      # 3 mm into the cheek, short of the guide rod
PUSHER = ring.fuse(lug).fuse(cam_pin)


def pusher_shape(lk):
    return PUSHER.translated(V(X_OPEN + LOCK_STROKE * lk, 0, 0))


lock_housing_h = lock_housing_plain.cut(box(X_OPEN - PUSHER_T / 2 - 0.4, X_LOCKED + PUSHER_T / 2 + 0.4,
                                      (SLEEVE_BORE + 1) / 2 - 1, 30, Z_FIRE - 3.5, Z_FIRE + 3.5))

# ---------------------------------------------------------------- trigger: one stage, straight onto the vent valve
# A crescent: concave finger face in front, the tip curled forward like a claw, grooves across the finger face.
# Its back at the vent valve's height (12 under the pivot) stays at x -4 from it, where the old blade's was.
TRIGGER_OUTLINE = [(4.6, 0.5), (5.5, -4.0), (4.0, -11.0), (3.0, -17.0), (3.2, -22.0), (4.6, -26.5), (7.0, -30.0),
                   (9.5, -31.5), (8.5, -33.5), (5.0, -33.5), (1.5, -31.0), (-1.2, -26.0), (-3.0, -19.0), (-4.0, -12.0),
                   (-4.0, -4.0), (-3.0, 1.5), (0.5, 3.3)]       # under the valve body: r <= 3.6 round the pivot
TRIGGER_WIDTH = 6.0


def _trigger_blank():
    pts = [V(x, -TRIGGER_WIDTH / 2, z) for x, z in TRIGGER_OUTLINE]
    c = Part.BSplineCurve()
    c.interpolate(pts, PeriodicFlag=True)
    t = Part.Face(Part.Wire(c.toShape())).extrude(V(0, TRIGGER_WIDTH, 0))
    t = t.fuse(Part.makeCylinder(3.6, TRIGGER_WIDTH, V(0, -TRIGGER_WIDTH / 2, 0), YA))          # round the pivot pin
    for z_ in (-15.0, -18.0, -21.0):                                                            # finger grooves
        g = Part.makeCylinder(0.8, TRIGGER_WIDTH + 2, V(3.0 + 0.1 * (z_ + 18) ** 2 / 3, -TRIGGER_WIDTH / 2 - 1, z_), YA)
        t = t.cut(g)
    return t.cut(Part.makeCylinder(1.6, TRIGGER_WIDTH + 2, V(0, -TRIGGER_WIDTH / 2 - 1, 0), YA)).removeSplitter()


TRIGGER = _trigger_blank()

# ---------------------------------------------------------------- vent valve: an AirTAC M3R110-06 without its roller
# Body 42.5 (plunger axis) x 27 x 18.5, lying: the plunger forward on the trigger's back, 27 across the pistol.
# Ports on the 18.5 x 42.5 faces: A left (elbow up: the pilot line straight up to the cap), R right (elbow down:
# the supply from the grip), P right (a silencer: the exhaust). Its spool shifts in the plunger's 2..3 mm: the
# trigger pushes it 3 mm, its back meeting the body's face, which is the trigger's stop. Three M3 through it.
AIRTAC = dict(L=42.5, W=27.0, T=18.5, plunger=(6.0, 3.0), elbow=(11.0, 6.5, 12.0),
              ports={"A": (21.0, -1, +1), "R": (14.0, +1, -1)}, P=(27.0, +1), holes=((14.0, -10.0), (28.0, -10.0), (21.0, 5.8)))
VENT_GAP = 0.3                      # trigger's back to the plunger at rest
VENT_SWITCH = 2.0                   # measured on the bench M3R110: it clicks over ~2 mm into the plunger's travel
_band = lambda h: box(-200, TRIGGER_PIVOT.x, -4, 4, MINI_Z - h, MINI_Z + h)


def _back_x(travel, h):
    return _rot_y(TRIGGER.translated(TRIGGER_PIVOT), TRIGGER_PIVOT, travel).common(_band(h)).BoundBox.XMin


VENT_TIP = _back_x(0.0, 1.5) - VENT_GAP
VENT_FRONT = VENT_TIP - AIRTAC["plunger"][1]
_lo, _hi = 5.0, 40.0                # the pull that brings the trigger's back to the body's face
for _ in range(14):
    _mid = (_lo + _hi) / 2
    if _back_x(_mid, AIRTAC["T"] / 2) > VENT_FRONT:
        _lo = _mid
    else:
        _hi = _mid
TRIGGER_TRAVEL = _lo
VENT_PUSH = VENT_TIP - _back_x(TRIGGER_TRAVEL, 1.5)


def vent_port(name):
    """Where the tube goes into the port's fitting, and which way (unit vector, out of the fitting)."""
    d, side, up = AIRTAC["ports"][name]
    e = AIRTAC["elbow"]
    return V(VENT_FRONT - d, side * (AIRTAC["W"] / 2 + e[1]), MINI_Z + up * e[2]), V(0, 0, up)


def _vent_valve():
    a, e = AIRTAC, AIRTAC["elbow"]
    body = box(VENT_FRONT - a["L"], VENT_FRONT, -a["W"] / 2, a["W"] / 2, MINI_Z - a["T"] / 2, MINI_Z + a["T"] / 2)
    for d, y in a["holes"]:
        body = body.cut(Part.makeCylinder(1.6, a["T"] + 2, V(VENT_FRONT - d, y, MINI_Z - a["T"] / 2 - 1), ZA))
    fit = []
    for name, (d, side, up) in a["ports"].items():
        x_ = VENT_FRONT - d
        fit.append(Part.makeCylinder(e[0] / 2, e[1] + e[0] / 2, V(x_, side * a["W"] / 2, MINI_Z), V(0, side, 0)))
        fit.append(Part.makeCylinder(e[0] / 2, e[2], V(x_, side * (a["W"] / 2 + e[1]), MINI_Z), V(0, 0, up)))
    d, side = a["P"]
    fit.append(Part.makeCylinder(4.0, 10.0, V(VENT_FRONT - d, side * a["W"] / 2, MINI_Z), V(0, side, 0)))   # silencer
    plunger = cyl_x(a["plunger"][0], VENT_FRONT - 0.01, VENT_TIP, 0, MINI_Z)
    return body, Part.makeCompound(fit), plunger


vent_body, vent_fittings, vent_plunger = _vent_valve()
valve_bodies = Part.makeCompound([vent_body, vent_fittings])          # for clearance (the plunger is pushed)
valves = Part.makeCompound([vent_body, vent_fittings, vent_plunger])


def trigger_h(trig):
    return _rot_y(TRIGGER.translated(TRIGGER_PIVOT), TRIGGER_PIVOT, TRIGGER_TRAVEL * trig)


def pose(st):
    """Moving shapes: cock (0 forward..1 back), block (deg), bend (pawl 0..1), trig (0..1)."""
    c = st["cock"]
    sl, pin = slider_h(c)
    sec = sector_turn(c)
    tooth_ = pawl_tooth.translated(V(-PAWL_BACK * st["bend"], 0, 0))
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, sec), "Pawl": turned(tooth_, sec),
            "Slider": sl, "Pin": pin, "Bolt": bolt_shape(st["block"]), "Hammer": hammer_shape(c),
            "Sleeve": lock_sleeve(lock_h(c)), "Pusher": pusher_shape(lock_h(c)), "Trigger": trigger_h(st["trig"])}


STYLE = dict(STYLE)
STYLE.update({"Hammer": ((0.35, 0.25, 0.2), 0), "Pusher": ((0.75, 0.45, 0.85), 0)})
for k in ("Lever", "Wedge"):
    STYLE.pop(k, None)
REST = dict(cock=0.0, block=0.0, bend=0.0, trig=0.0)

# ---------------------------------------------------------------- checks
mainsprings = Part.makeCompound([Part.makeCylinder(MAINSPRING["od"] / 2, y1 - y0, V(H.x, y0, H.z), YA).cut(
    Part.makeCylinder(MAINSPRING["od"] / 2 - MAINSPRING["d"], y1 - y0 + 2, V(H.x, y0 - 1, H.z), YA))
    for y0, y1 in MAINSPRING["y"]])
guide_rod = Part.makeCylinder(GUIDE_ROD["d"] / 2, GUIDE_ROD["z"][1] - GUIDE_ROD["z"][0],
                              V(GUIDE_ROD["x"], GUIDE_ROD["y"], GUIDE_ROD["z"][0]), ZA)
FIXED = {"body": valve_body, "cap": valve_cap, "lock": lock_housing_h, "axle": axle, "vent": valve_bodies, "hammer axle": shaft,
         "guide rod": guide_rod,
         "mainsprings": mainsprings}
report = [NAME]
worst = {}
for i in range(11):
    c = i / 10
    st = dict(cock=c, block=block_drive(c), bend=0.0, trig=0.0)
    sh = pose(st)
    for mv_ in ("Hammer", "Slider", "Pusher", "Sector", "Sleeve", "Trigger", "Pin"):
        for fx_, s_ in FIXED.items():
            v_ = sh[mv_].common(s_).Volume
            worst[(mv_, fx_)] = max(worst.get((mv_, fx_), 0.0), v_)
    for a_, b_ in (("Hammer", "Slider"), ("Slider", "Block"), ("Pusher", "Sleeve"), ("Hammer", "Trigger"),
                   ("Slider", "Sector"), ("Pusher", "Slider")):
        v_ = sh[a_].common(sh[b_]).Volume
        worst[(a_, b_)] = max(worst.get((a_, b_), 0.0), v_)
    if i % 2 == 0:
        report.append("  cock %.1f  hammer %+5.1f deg  slider pin z %+6.1f  sector %+5.1f  block %+5.1f deg  lock %.2f"
                      % (c, hammer_rot(c), slider_z(c), sector_turn(c), block_drive(c), lock_h(c)))
for tg in (0.0, 0.5, 1.0):                       # trigger stroke with the hammer down
    sh = pose(dict(cock=0.0, block=0.0, bend=0.0, trig=tg))
    for a_ in ("Trigger",):
        for fx_, s_ in FIXED.items():
            worst[(a_, fx_)] = max(worst.get((a_, fx_), 0.0), sh[a_].common(s_).Volume)
        worst[(a_, "Hammer")] = max(worst.get((a_, "Hammer"), 0.0), sh[a_].common(sh["Hammer"]).Volume)
hits = ["%s/%s %.1f" % (k[0], k[1], v_) for k, v_ in sorted(worst.items(), key=lambda kv: -kv[1]) if v_ > 0.05]
report.append("  clashes over the cock and the trigger (mm3): " + (", ".join(hits) if hits else "none"))
report.append("  hammer: crank %.1f mm, swing %.0f deg -> slider %.1f mm, sector %.0f deg (%.0f lost, 60 for the block)"
              % (HAMMER_ARM, HAMMER_SWING, slider_z(1) - slider_z(0), SECTOR_SWING, LOST_DEG))
spur_c = _at(H, SPUR[0] - hammer_rot(1.0), SPUR[1])
report.append("  spur tip: forward (%.0f, %.0f), back (%.0f, %.0f): thumb travel %.0f mm"
              % (spur_tip.x, spur_tip.z, spur_c.x, spur_c.z, (spur_c - spur_tip).Length))
mu = 0.25
cam_a = math.degrees(math.atan2(LOCK_STROKE, CAM_RISE))
F_sl = LOCK_SEAT_N * math.tan(math.radians(cam_a) + math.atan(mu))
torque = F_sl * HAMMER_ARM * math.cos(math.radians(crank_angle(0.0))) / 1000
report.append("  lock: cam %.0f deg, opens in the first %.1f deg of the cock; %0.f N on the flange needs %.0f N on the slider"
              " = %.2f N*m from the mainspring at rest"
              % (cam_a, next(HAMMER_SWING * i / 400 for i in range(401) if lock_h(i / 400) <= 0.0), LOCK_SEAT_N, F_sl, torque))
ms = MAINSPRING
D_ms = ms["od"] - ms["d"]
k_ms = 200000.0 * ms["d"] ** 4 / (64 * D_ms * ms["coils"]) * math.pi / 180       # N*mm per deg, each
C_ms = D_ms / ms["d"]
Ki = (4 * C_ms ** 2 - C_ms - 1) / (4 * C_ms * (C_ms - 1))
pre = torque * 1000 / 2 / k_ms                                                     # preload angle, deg
T_back = 2 * k_ms * (pre + HAMMER_SWING) / 1000
stress = 32 * T_back * 1000 / 2 * Ki / (math.pi * ms["d"] ** 3)
report.append("  mainspring: 2 x torsion, wire Ø%.1f, OD %.0f, %d coils: %.1f N*mm/deg each; wound %.0f deg at rest "
              "(%.2f N*m), %.0f deg back (%.2f N*m); %.0f MPa (music wire < ~1400); thumb on the spur %.0f N"
              % (ms["d"], ms["od"], ms["coils"], k_ms, pre, torque, pre + HAMMER_SWING, T_back, stress, T_back * 1000 / SPUR[1]))
report.append("  pawl plunger: pen spring Ø3, ~2 N in the notch; detent: pen spring Ø4, ~6 N on the V (holds the block, "
              "clicks under the thumb)")
report.append("  vent valve: AirTAC M3R110-06 body %.1f x %.0f x %.1f, front at x %.1f; trigger pull %.1f deg pushes its plunger"
              " %.1f mm (it clicks at %.1f: %.1f to spare), its back stopping on the body"
              % (AIRTAC["L"], AIRTAC["W"], AIRTAC["T"], VENT_FRONT, TRIGGER_TRAVEL, VENT_PUSH, VENT_SWITCH, VENT_PUSH - VENT_SWITCH))
report.append("  pawl idles %.1f deg of the hammer before it drives: the lock is open by then"
              % next(HAMMER_SWING * i / 400 for i in range(401) if block_drive(i / 400) > 0.0))
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
for n, s_, c_, tr in (("Valve_body_v11", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap_v11", valve_cap, (0.45, 0.65, 0.85), 0),
                      ("Lock_housing", lock_housing_h, (0.5, 0.7, 0.5), 30), ("Chamber_axle", axle, (0.7, 0.7, 0.7), 60),
                      ("Vent_valve", valves, (0.3, 0.3, 0.8), 40), ("Mainsprings", mainsprings, (0.6, 0.6, 0.65), 0),
                      ("Hammer_axle", shaft, (0.75, 0.75, 0.78), 0), ("Guide_rod", guide_rod, (0.75, 0.75, 0.78), 0)):
    add(fixed, n, s_, c_, tr)
for gname, st in (("Rest", REST), ("Hammer_back", dict(cock=1.0, block=60.0, bend=0.0, trig=0.0))):
    g = doc.addObject("App::DocumentObjectGroup", gname)
    for n, s_ in pose(st).items():
        add(g, "%s_%s" % (n, gname), s_, *STYLE[n])
    if App.GuiUp and gname != "Rest":
        for o in g.Group:
            o.ViewObject.Visibility = False
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewRear()
    Gui.SendMsgToActiveView("ViewFit")
