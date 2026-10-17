# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, single-action hammer variant.

The lever variant (pistol/mech_layout.py) needs both hands; this one is
worked by one: the thumb cocks a hammer, the trigger does the rest. The
block, its ratchet, detent, lock sleeve and the v1.1 valve come from
mech_layout.py unchanged; only what drives them is new.

    cock (thumb, 56 deg): the hammer's crank lifts the slider through a
        bracket behind it (a Scotch yoke). Its first 3 mm pull the lock
        pusher back off the sleeve's flange (cam slot in the slider): the
        lock opens. Then the pawl, idle across the notch's lost motion,
        meets the notch wall and turns the block 60 deg; the detent
        clicks. The sear catches the hammer's tooth.
    trigger, stage 1: the trigger's tail lifts the trigger bar, which
        tips the sear off the tooth; the mainspring throws the hammer
        forward, the slider drops (the pawl skips back to the next notch)
        and in its last 3 mm the cam drives the pusher onto the flange:
        the lock closes, held by the mainspring.
    trigger, stage 2: the trigger's back pushes the vent valve: the shot.
        Let go: vent shut, the chamber recharges; the lock stays shut
        until the next cock.

Lock: a ring behind the sleeve's flange, in its bore, with a lug out
through the housing's right side and a pin into a cam slot in the
slider's rear cheek. The shot itself pushes the sleeve forward, so the
pusher only has to seat it.

Plain masses at their sizes, as mech_layout.py. pose(st) for a state
dict (cock 0 down .. 1 cocked, block deg, pawl bend, trig 0..1, sear
0 engaged .. 1 tripped); the document shows the rest pose and the hammer
cocked.

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
TOOTH = (250.0, 10.5, 15.0, 4.0)    # sear tooth at rest: direction, r from .. to, width (outside the hub)
CRANK_Y = (32.0, 35.0)              # the crank on the right, outside the valve body (y 31)
BRACKET_Y = (35.2, 38.2)            # the slider's bracket, outside the crank
SLIDER_REACH = 48.0                 # slider body: from its pin this far down (the cam slot)
CHEEK_X = (-14.5, -7.0)             # slider's rear cheek with the cam slot
PUSHER_T = 3.0
CAM_RISE = 3.0                      # slider rise that opens the lock
SEAR_PIVOT_R = 14.0                 # sear pivot this far from its nose, behind it
SEAR_TRIP = 5.5                     # nose moves this far out to clear the tooth
SEAR_TAIL = 10.0
SEAR_Y = (5.5, 9.5)                 # the sear's arm beside the hammer's hub (y +-5)
TAIL_Y = (-12.0, -8.0)              # trigger tail, trigger bar and the sear's tail: left of the vent valve (y +-7)
TAIL_Z = (-70.0, -66.0)             # under the cap with room for the tail's rise
TRIG_TAIL_X = -101.0                # trigger's tail reaches back under the trigger bar
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
tooth = Part.makeBox(TOOTH[2] - TOOTH[1], TOOTH[3], TOOTH[3], V(H.x + TOOTH[1], -TOOTH[3] / 2, H.z - TOOTH[3] / 2))
tooth = _rot_y(tooth, H, -TOOTH[0])
c_tip0 = _at(H, crank_angle(0.0), HAMMER_ARM)
crank = _rod(H, c_tip0, 8.0, CRANK_Y[0], CRANK_Y[1] - CRANK_Y[0])
crank_pin = Part.makeCylinder(1.5, BRACKET_Y[1] + 0.5 - CRANK_Y[0], V(c_tip0.x, CRANK_Y[0], c_tip0.z), YA)
shaft = Part.makeCylinder(4.0, CRANK_Y[1] + 6.0, V(H.x, -6.0, H.z), YA)
HAMMER = Part.makeCompound([hub_h.fuse(spur).fuse(tooth), crank, crank_pin, shaft])


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

# ---------------------------------------------------------------- sear (rocker behind the hammer) and trigger with its bar
t_cock = TOOTH[0] - hammer_rot(1.0)                   # tooth's direction when cocked
r_nose = (TOOTH[1] + TOOTH[2]) / 2
a_nose = t_cock - math.degrees((TOOTH[3] / 2 + 3.0) / r_nose)        # just ahead of it in its fall
N = _at(H, a_nose, r_nose)
u = V(math.cos(math.radians(a_nose)), 0, math.sin(math.radians(a_nose)))   # radial out: the way it trips
perp = V(u.z, 0, -u.x)
if perp.x > 0:
    perp = perp * -1
SEAR_PIVOT = N + perp * SEAR_PIVOT_R                  # behind the nose
SEAR_SWING = math.degrees(SEAR_TRIP / SEAR_PIVOT_R)
nose = Part.makeBox(4.0, SEAR_Y[1] + 2, 4.0, V(N.x - 2, -2, N.z - 2))
sear_tail_tip = V(SEAR_PIVOT.x - SEAR_TAIL, 0, SEAR_PIVOT.z)
SEAR = Part.makeCompound([_rod(SEAR_PIVOT, N, 5.0, SEAR_Y[0], SEAR_Y[1] - SEAR_Y[0]).fuse(nose),
                          _rod(SEAR_PIVOT, sear_tail_tip, 5.0, TAIL_Y[0], TAIL_Y[1] - TAIL_Y[0]),
                          Part.makeCylinder(2.0, SEAR_Y[1] - TAIL_Y[0], V(SEAR_PIVOT.x, TAIL_Y[0], SEAR_PIVOT.z), YA)])


def sear_rot():                     # sign: the nose goes out along u
    for sgn in (1, -1):
        n2 = N - SEAR_PIVOT
        n2 = App.Rotation(YA, sgn * SEAR_SWING).multVec(n2) + SEAR_PIVOT
        if (n2 - N).dot(u) > 0:
            return sgn * SEAR_SWING


SEAR_ROT = sear_rot()


def sear_shape(sr):
    return _rot_y(SEAR, SEAR_PIVOT, SEAR_ROT * sr)


T = TRIGGER_PIVOT
TAIL_TOP = V(TRIG_TAIL_X, 0, TAIL_Z[1])
BAR_GAP = 0.5                       # bar's lower rod to the sear's tail, hammer down


def tail_lift(trig):
    p = App.Rotation(YA, TRIGGER_TRAVEL * trig).multVec(TAIL_TOP - T) + T
    return p.z - TAIL_TOP.z


TRIP_LIFT = SEAR_TAIL * math.sin(math.radians(abs(SEAR_ROT))) + BAR_GAP
STAGE1 = next(i / 400 for i in range(401) if tail_lift(i / 400) >= TRIP_LIFT)


def sear_of(trig):
    return min(max((tail_lift(trig) - BAR_GAP) / (TRIP_LIFT - BAR_GAP), 0.0), 1.0)


def trigger_h(trig):
    blade = box(-4, 6, -3, 3, -28, 0).translated(T)
    tail = box(TRIG_TAIL_X - 3, T.x - 2, TAIL_Y[0], TAIL_Y[1], TAIL_Z[0], TAIL_Z[1])    # back beside the vent valve
    tail = tail.fuse(box(T.x - 4, T.x + 2, TAIL_Y[0], 3, TAIL_Z[0], T.z + 1))               # joined to the blade at the pivot
    return _rot_y(blade.fuse(tail), T, TRIGGER_TRAVEL * trig)


def trig_bar(trig, sr):
    """Lower rod on the trigger's tail, upper rod under the sear's tail; a spring between takes the overtravel."""
    p = App.Rotation(YA, TRIGGER_TRAVEL * trig).multVec(TAIL_TOP - T) + T
    q = App.Rotation(YA, SEAR_ROT * sr).multVec(sear_tail_tip - SEAR_PIVOT) + SEAR_PIVOT
    y = sum(TAIL_Y) / 2
    lower = Part.makeCylinder(2.5, 14, V(p.x, y, p.z), ZA).cut(Part.makeCylinder(1.6, 15, V(p.x, y, p.z + 2), ZA))
    upper = Part.makeCylinder(1.5, max(q.z - 2.5 - BAR_GAP * (1 - sr) - (p.z + 4), 1.0), V(p.x, y, p.z + 4), ZA)
    return lower.fuse(upper)


def pose(st):
    """Moving shapes: cock (0 down..1 cocked), block (deg), bend (pawl 0..1), trig (0..1), sear (0..1)."""
    c = st["cock"]
    sl, pin = slider_h(c)
    sec = sector_turn(c)
    tooth_ = pawl_tooth.translated(V(-PAWL_BACK * st["bend"], 0, 0))
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, sec), "Pawl": turned(tooth_, sec),
            "Slider": sl, "Pin": pin, "Bolt": bolt_shape(st["block"]), "Hammer": hammer_shape(c),
            "Sleeve": lock_sleeve(lock_h(c)), "Pusher": pusher_shape(lock_h(c)), "Sear": sear_shape(st["sear"]),
            "Trigger": trigger_h(st["trig"]), "Trigger_bar": trig_bar(st["trig"], st["sear"])}


STYLE = dict(STYLE)
STYLE.update({"Hammer": ((0.35, 0.25, 0.2), 0), "Pusher": ((0.75, 0.45, 0.85), 0), "Sear": ((0.8, 0.2, 0.5), 0),
              "Trigger_bar": ((0.4, 0.4, 0.45), 0)})
for k in ("Lever", "Wedge"):
    STYLE.pop(k, None)
REST = dict(cock=0.0, block=0.0, bend=0.0, trig=0.0, sear=0.0)

# ---------------------------------------------------------------- checks
FIXED = {"body": valve_body, "cap": valve_cap, "lock": lock_housing_h, "axle": axle, "vent": valve_bodies}
report = [NAME]
worst = {}
for i in range(11):
    c = i / 10
    st = dict(cock=c, block=block_drive(c), bend=0.0, trig=0.0, sear=0.0)
    sh = pose(st)
    for mv_ in ("Hammer", "Slider", "Pusher", "Sector", "Sleeve", "Sear", "Trigger", "Trigger_bar", "Pin"):
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
    sh = pose(dict(cock=0.0, block=0.0, bend=0.0, trig=tg, sear=sear_of(tg)))
    for a_ in ("Trigger", "Trigger_bar", "Sear"):
        for fx_, s_ in FIXED.items():
            worst[(a_, fx_)] = max(worst.get((a_, fx_), 0.0), sh[a_].common(s_).Volume)
        worst[(a_, "Hammer")] = max(worst.get((a_, "Hammer"), 0.0), sh[a_].common(sh["Hammer"]).Volume)
hits = ["%s/%s %.1f" % (k[0], k[1], v_) for k, v_ in sorted(worst.items(), key=lambda kv: -kv[1]) if v_ > 0.05]
report.append("  clashes over the cock and the trigger (mm3): " + (", ".join(hits) if hits else "none"))
sh_c = pose(dict(cock=1.0, block=60.0, bend=0.0, trig=0.0, sear=0.0))
report.append("  sear: swing %.1f deg trips it (nose out %.1f mm); the bar lifts %.1f mm by trigger %.2f (stage 1), "
              "%.1f at full pull (a spring in the bar takes the rest); vent pushed at %.2f..%.2f (stage 2)"
              % (SEAR_SWING, SEAR_TRIP, TRIP_LIFT, STAGE1, tail_lift(1.0), 0.55, 0.75))
report.append("  hammer: crank %.1f mm, swing %.0f deg -> slider %.1f mm, sector %.0f deg (%.0f lost, 60 for the block)"
              % (HAMMER_ARM, HAMMER_SWING, slider_z(1) - slider_z(0), SECTOR_SWING, LOST_DEG))
spur_c = _at(H, SPUR[0] - hammer_rot(1.0), SPUR[1])
report.append("  spur tip: down (%.0f, %.0f), cocked (%.0f, %.0f): thumb travel %.0f mm"
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
for gname, st in (("Rest_down", REST), ("Cocked", dict(cock=1.0, block=60.0, bend=0.0, trig=0.0, sear=0.0))):
    g = doc.addObject("App::DocumentObjectGroup", gname)
    for n, s_ in pose(st).items():
        add(g, "%s_%s" % (n, gname), s_, *STYLE[n])
    if App.GuiUp and gname != "Rest_down":
        for o in g.Group:
            o.ViewObject.Visibility = False
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewRear()
    Gui.SendMsgToActiveView("ViewFit")
