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
slider's rear cheek. The shot itself pushes the sleeve forward, so the
pusher only has to seat it.

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
MECH_OVERRIDES = dict(ARM_A0=SECTOR_SWING / 2, PIN_R0=24.5 / math.cos(math.radians(SECTOR_SWING / 2)), ARM_R=33.0,
                      NOTCH_SLACK=16.5 * math.radians(LOST_DEG))
MECH_LIBRARY = True
exec(open(os.path.join(REPO, "pistol", "mech_layout.py")).read())
MECH_LIBRARY = False
NAME = "pistol_hammer_layout"

# ---------------------------------------------------------------- parameters
PIN_Y = PIN_R0 * math.cos(math.radians(ARM_A0))                     # slider pin's y (24.5)
HAMMER_PIVOT = V(-82.0, 0, -8.0)    # behind the v1.1 cap, above the grip
HAMMER_ARM = PIN_Y * math.tan(math.radians(SECTOR_SWING / 2)) / math.sin(math.radians(HAMMER_SWING / 2))
HAMMER_R = 10.0                     # its hub
SPUR = (95.0, 36.0)                 # spur direction at rest (deg from +x, up = 90), length
CRANK_Y = (32.0, 35.0)              # the crank on the right, outside the valve body (y 31)
BRACKET_Y = (35.2, 38.2)            # the slider's bracket, outside the crank
SLIDER_REACH = 48.0                 # slider body: from its pin this far down (the cam slot)
CHEEK_X = (-14.5, -7.0)             # slider's rear cheek with the cam slot
PUSHER_T = 3.0
CAM_RISE = 3.0                      # slider rise that opens the lock
TRIGGER_TRAVEL = 22.0               # deg


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
spur = _rod(H, spur_tip, 9.0, -4.0, 8.0)
spur = spur.fuse(_rod(_at(H, SPUR[0], SPUR[1] - 6), _at(H, SPUR[0] + 25, SPUR[1] - 2), 6.0, -5.0, 10.0))   # thumb piece
c_tip0 = _at(H, crank_angle(0.0), HAMMER_ARM)
crank = _rod(H, c_tip0, 8.0, CRANK_Y[0], CRANK_Y[1] - CRANK_Y[0])
crank_pin = Part.makeCylinder(1.5, BRACKET_Y[1] + 0.5 - CRANK_Y[0], V(c_tip0.x, CRANK_Y[0], c_tip0.z), YA)
shaft = Part.makeCylinder(4.0, CRANK_Y[1] + 6.0, V(H.x, -6.0, H.z), YA)
HAMMER = Part.makeCompound([hub_h.fuse(spur), crank, crank_pin, shaft])


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
            .fuse(box(CHEEK_X[0], CHEEK_X[1], SLIDER_Y[0], SLIDER_Y[1], -SLIDER_REACH, -6))
            .fuse(box(CHEEK_X[0], SLIDER_X[1], SLIDER_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .fuse(box(min(xs) - 8, CHEEK_X[0] + 0.01, BRACKET_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .cut(box(min(xs) - 2, max(xs) + 2, BRACKET_Y[0] - 1, BRACKET_Y[1] + 1, D_YOKE - 1.7, D_YOKE + 1.7))
            .cut(cam_slot()))


def slider_h(c):
    z = slider_z(c)
    return SLIDER_H.translated(V(0, 0, z)), cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], PIN_Y, z)


# ---------------------------------------------------------------- lock pusher (ring in the flange's bore, lug and pin to the cam)
ring = cyl_x(LOCK_PISTON_D - 0.4, -PUSHER_T / 2, PUSHER_T / 2, 0, Z_FIRE).cut(
    cyl_x(SLEEVE_BORE + 0.6, -5, 5, 0, Z_FIRE))
lug = box(-PUSHER_T / 2, PUSHER_T / 2, (SLEEVE_BORE + 1) / 2, SLIDER_Y[0] - 0.5, Z_FIRE - 3, Z_FIRE + 3)
cam_pin = Part.makeCylinder(1.5, SLIDER_Y[1] - SLIDER_Y[0] + 2.5, V(0, SLIDER_Y[0] - 2.5, Z_FIRE), YA)
PUSHER = ring.fuse(lug).fuse(cam_pin)


def pusher_shape(lk):
    return PUSHER.translated(V(X_OPEN + LOCK_STROKE * lk, 0, 0))


lock_housing_h = lock_housing.cut(box(X_OPEN - PUSHER_T / 2 - 0.4, X_LOCKED + PUSHER_T / 2 + 0.4,
                                      (SLEEVE_BORE + 1) / 2 - 1, 30, Z_FIRE - 3.5, Z_FIRE + 3.5))

# ---------------------------------------------------------------- trigger: one stage, straight onto the vent valve
def trigger_h(trig):
    return _rot_y(box(-4, 6, -3, 3, -28, 0).translated(TRIGGER_PIVOT), TRIGGER_PIVOT, TRIGGER_TRAVEL * trig)


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
FIXED = {"body": valve_body, "cap": valve_cap, "lock": lock_housing_h, "axle": axle, "vent": valve_bodies}
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
F_seat = 40.0
F_sl = F_seat * math.tan(math.radians(cam_a) + math.atan(mu))
torque = F_sl * HAMMER_ARM * math.cos(math.radians(crank_angle(0.0))) / 1000
report.append("  lock: cam %.0f deg, opens in the first %.1f deg of the cock; %0.f N on the flange needs %.0f N on the slider"
              " = %.2f N*m from the mainspring (%.0f N at the spur)"
              % (cam_a, next(HAMMER_SWING * i / 400 for i in range(401) if lock_h(i / 400) <= 0.0), F_seat, F_sl, torque,
                 torque * 1000 / SPUR[1]))
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
                      ("Vent_valve", valves, (0.3, 0.3, 0.8), 40)):
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
