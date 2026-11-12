# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: mechanism layout, thumb-hammer variant.

The lever variant (pistol/mech_layout.py) needs both hands; this one is
worked by one: the thumb pulls a hammer back and lets it go, the trigger
fires. The block, its ratchet, detent and the v1.1 valve come from
mech_layout.py unchanged; only what drives them is new. No air is spent on
anything but the shot.

LOCKLESS (default True): no lock at all. The lock housing carries the
sleeve's nose as one print, a plain Ø16 through bore ending 0.3 mm off the
hub, so the block turns freely and the shot leaks only through that slit
(it shot well on the bench). There is no sleeve, no pusher, no cam slot in the
slider and no lug slot; the text below that talks of the lock is the old
LOCKLESS = False variant, kept for the history.

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

try:
    FLEX_PAWL                       # True: the pawl is a flexure tongue in the sector; False: a plunger on a steel spring
except NameError:
    FLEX_PAWL = False
HAMMER_SWING = 56.0                 # deg, down .. cocked
SECTOR_SWING = 68.0                 # 60 for the block + the notch's lost motion
LOST_DEG = SECTOR_SWING - 60.0
try:
    HUB_T_HAMMER                    # the rear disc: set before exec (hammer_assembly.py needs it for the barrels)
except NameError:
    HUB_T_HAMMER = 14.0
# Block: two discs and the bought tubes. The rear disc: breech seats (9 deep, O-ring faces, pawl notches, detent
# notches in its rim) and 5 mm sockets the barrels are glued into; the front disc 6 mm.
# The plunger pawl's tooth is rigid and wide (TOOTH_W): the ramp is in the disc's notch, not on the tooth. The notch keeps its
# drive wall; its floor is the idle gap + the tooth + 0.2 mm either side, then a 45 deg ramp (3 mm) up to the face: 9.7 mm in
# all, of ~12 mm free between the barrels' O-rings at R 16.5.
try:
    RAMP_IN_DISC                    # False: the disc as printed (square notches): the tooth is a rigid blank, the ramp is filed in the disc by hand
except NameError:
    RAMP_IN_DISC = False
TOOTH_W, RAMP_L = (4.0, 3.0) if RAMP_IN_DISC else (3.6, 0.0)
TOOTH_RAMP = not RAMP_IN_DISC            # the disc as printed (square notches): the ramp is on the tooth's trailing face
TOOTH_RAMP_RUN = 2.4                    # its length along the arc (the rise is the tip's height): ~1.2 N of drag on the disc per N of spring
# The pawl at rest sits LOST_DEG (2.3 mm at R 16.5) off the notch's centre line, so its centre is at y = 2.3 in the notch's frame:
# its leading face reaches the drive wall (y = -2.0) after exactly the idle, its trailing face is 0.45 mm short of the ramp's foot (the arcs of the sector against the planes of the notch).
NOTCH_RAMP = None if (FLEX_PAWL or not RAMP_IN_DISC) else (16.5 * math.radians(LOST_DEG) + TOOTH_W / 2 + 0.45, RAMP_L, 0.15)   # the drive wall 0.15 mm back: arcs against planes
MECH_OVERRIDES = dict(ARM_A0=SECTOR_SWING / 2, PIN_R0=24.5 / math.cos(math.radians(SECTOR_SWING / 2)), ARM_R=33.0,
                      NOTCH_SLACK=16.5 * math.radians(LOST_DEG), HUB_T=HUB_T_HAMMER, FRONT_T=6.0, NOTCH_RAMP=NOTCH_RAMP,
                      SLIDER_Y=(23.0, 31.5))             # thicker round its guide rod
MECH_LIBRARY = True
exec(open(os.path.join(REPO, "pistol", "mech_layout.py")).read())
MECH_LIBRARY = False
NAME = "pistol_hammer_layout"

# Stage 2 (2026-11-05): the vent valve stands vertical in the frame's rear column (hammer_assembly.py),
# so the trigger's pivot moves back under it - the blade still reaches the old place under the guard, and
# a rear lug with a wide pad lifts the plunger from below. The sketch: exports/body_visual_study/trigger_link.html.
TRIGGER_PIVOT = V(-80.0, 0, -64.0)    # the trigger's pivot: 2 mm lower with the vent valve (2026-11-08, the
                                       # real body is 46.5 tall), so the pad's gap to the plunger is unchanged

# ---------------------------------------------------------------- pawl and detent: their springs
# The pawl is a plunger: it slides in a boss on the sector's back, a Ø3 pen spring behind it pushing it into the
# notches; the boss swings over the lock housing's flat top. The detent bolt is 12 long, with a Ø4 pen spring
# in a pocket behind it in its housing.
PAWL_X0 = -6.5                      # the plunger's back at rest (its front in the notch, as mech_layout's tooth)
PAWL_BOSS_X0 = -14.2                # the boss's back wall
BOLT_LEN = 12.0
_pw, _ph, _pr0 = NOTCH_W - 0.8, NOTCH_R[1] - SECTOR_R[1] - 0.5, SECTOR_R[1] - 0.5
TIP_RISE = 2.7                                          # the pawl tooth's tip stands this far past the hub's face (notch depth 3.0)
if not FLEX_PAWL:
    # The pawl is a plunger in a boss on the sector's back, on a steel compression spring from the 304 assortment kit:
    # 0.5 x 6 x 10 mm, 8 coils, ~0.55 N/mm (G = 70 GPa), solid height 4.0 mm: 1.4 N at rest, 2.9 N at full travel. Its tooth
    # is rigid and wide (TOOTH_W = 4.0 x 3.4 mm, no ramp of its own): the 45 deg ramp is in the disc's notch (NOTCH_RAMP), so
    # on the return the notch's ramp lifts the tooth out against the spring; the drive wall is vertical and the drive
    # pushes the tooth squarely. The body is a Ø6 plunger in a Ø6.4 channel in a boss on a tab of the ring's full thickness.
    # Built at the pawl's place at the "top" (+z), turned by PAWL_A0 - 90 at the end.
    TIP_RISE = 2.5                                      # the tooth's tip 2.5 mm past the face, 0.5 above the notch floor (3.0)
    SPRING = dict(wire=0.5, od=6.0, free=10.0, coils=8, solid=4.0, k=0.55)      # k in N/mm
    PL_AXIS_Z = 17.6                                    # the plunger's axis, radially (the tooth is its lower part)
    PL_BODY_R, PL_CH_R = 3.0, 3.2                       # body and channel radii: 0.2 mm of play
    PL_STEP_X = SECTOR_X[1] - 1.3                       # the body's front face rests on the channel's front wall (1.3 thick)
    PL_BODY_L = 3.0
    PL_PLUG_L = 2.0
    PL_SPRING_L = 7.4                                   # the spring's length with the pawl at rest: 2.6 mm of preload
    PL_REAR_X = SECTOR_X[1] - 1.3 - PL_BODY_L - PL_SPRING_L - PL_PLUG_L      # the boss's back face; the plug closes it
    PAWL_BACK = TIP_RISE + 0.1                          # travel: the spring is then 4.8 mm long, 0.8 over its solid height
    _r_t = (NOTCH_R[0] + 0.6, NOTCH_R[1] - 0.5)         # the tooth radially: 15.1 .. 18.0 (notch 14.5 .. 18.5): the sector's arc against the notch's planes needs 0.5 mm
    _x_tip = HUB_X0 + TIP_RISE
    _sh = V(0, 0, 0)                                    # the tooth's centre is the pawl's own y = 0
    if TOOTH_RAMP:      # flat leading face (towards the drive, y < 0), the trailing face (y > 0) a ramp from the face level up to the tip
        _pts = [(-TOOTH_W / 2, PL_STEP_X - 0.2), (TOOTH_W / 2, PL_STEP_X - 0.2), (TOOTH_W / 2, HUB_X0 - 0.3),
                (TOOTH_W / 2 - TOOTH_RAMP_RUN, _x_tip), (-TOOTH_W / 2, _x_tip)]
    else:
        _pts = [(-TOOTH_W / 2, PL_STEP_X - 0.2), (TOOTH_W / 2, PL_STEP_X - 0.2), (TOOTH_W / 2, _x_tip), (-TOOTH_W / 2, _x_tip)]
    _poly = [V(x, y, _r_t[0]) for y, x in _pts]
    _nose = Part.Face(Part.makePolygon(_poly + [_poly[0]])).extrude(V(0, 0, _r_t[1] - _r_t[0]))
    _body = Part.makeCylinder(PL_BODY_R, PL_BODY_L, V(PL_STEP_X - PL_BODY_L, 0, PL_AXIS_Z), XA)
    _plunger = _nose.fuse(_body).removeSplitter().translated(_sh)
    _channel = Part.makeCylinder(PL_CH_R, PL_STEP_X - PL_REAR_X + 0.5, V(PL_REAR_X - 0.5, 0, PL_AXIS_Z), XA).translated(_sh)
    _window = box(PL_STEP_X - PAWL_BACK - 0.8, SECTOR_X[1] + 0.5, -TOOTH_W / 2 - 0.25, TOOTH_W / 2 + 0.25, _r_t[0] - 0.2, _r_t[1] + 0.2).translated(_sh)
    _tab = box(SECTOR_X[0], SECTOR_X[1], -4.8, 4.8, SECTOR_R[0] + 0.1, PL_AXIS_Z + PL_CH_R + 1.6).translated(_sh)   # the ring, grown out under the boss
    _boss = box(PL_REAR_X, SECTOR_X[0] + 0.01, -4.8, 4.8, SECTOR_R[0] + 0.1, PL_AXIS_Z + PL_CH_R + 1.6).translated(_sh)
    _plug = Part.makeCylinder(PL_CH_R - 0.05, PL_PLUG_L, V(PL_REAR_X, 0, PL_AXIS_Z), XA).translated(_sh)  # pressed and glued in the boss's rear
    sector_base = (sector_base.fuse(turned(_tab, PAWL_A0 - 90)).fuse(turned(_boss, PAWL_A0 - 90))
                   .cut(turned(_channel, PAWL_A0 - 90)).cut(turned(_window, PAWL_A0 - 90)).removeSplitter())
    pawl_tooth = turned(_plunger, PAWL_A0 - 90)         # nose and body, the moving part
    PAWL_MOVER = pawl_tooth
    PAWL_PLUG = turned(_plug, PAWL_A0 - 90)
else:
    # The pawl is a flexure printed in the sector: a tongue cut out of the ring along its arc (root on the drive side, so
    # the drive loads it in tension) with a ramped tooth on its free end. On the return the notch's corner slides up the
    # tooth's ramp and the tongue bends back 2 mm: no plunger, no spring, no boss. The old square tooth could not leave a
    # square notch at all; the ramp rises 2.0 mm over about 1.5 mm of travel (checked in tools/ against the disc as it is).
    # Built at the pawl's place at the "top" (+z); theta runs from +z towards -y, the drive direction.
    TONGUE_L, TONGUE_T = 14.0, 0.95                     # along the arc, thick in x (the bending direction); 12 x 1.0 pushed back too hard, 15 x 0.9 too soft
    TONGUE_X = (SECTOR_X[0], SECTOR_X[0] + TONGUE_T)    # the tongue is the back layer of the ring
    R_T = (SECTOR_R[1] - 0.3, NOTCH_R[1] - 0.3)         # tongue and tooth radially: 15.0 .. 18.2 (notch 14.5 .. 18.5)
    TH_ROOT = math.degrees(TONGUE_L / (sum(R_T) / 2))   # the root, from the tooth's centre
    TH_FREE = -math.degrees(2.0 / (sum(R_T) / 2))       # the free end, a little past the tooth's ramp side

    def _arc_prism(r0, r1, th0, th1, x0, x1):
        n = max(2, int(abs(th1 - th0) / 6) + 1)
        pts = [V(x0, 0, 0)] + [V(x0, -60 * math.sin(math.radians(th0 + (th1 - th0) * i / n)),
                                 60 * math.cos(math.radians(th0 + (th1 - th0) * i / n))) for i in range(n + 1)]
        wedge = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(x1 - x0, 0, 0))
        return wedge.common(cyl_x(2 * r1, x0 - 1, x1 + 1, 0, 0).cut(cyl_x(2 * r0, x0 - 2, x1 + 2, 0, 0)))

    _tongue = _arc_prism(R_T[0], R_T[1], TH_FREE, TH_ROOT + 1.0, *TONGUE_X)
    _root = _arc_prism(R_T[0] - 0.2, R_T[1] + 0.6, TH_ROOT, TH_ROOT + 22.0, SECTOR_X[0], SECTOR_X[1])
    # The slit round the tongue is 0.6 mm inside and 0.5 mm outside: 0.2-0.3 mm slits fuse shut in a 0.4 nozzle print and
    # the tongue was then glued to the ring (stiff, uneven).
    _pocket = _arc_prism(R_T[0] - 0.6, R_T[1] + 0.5, TH_FREE - 3.0, TH_ROOT, SECTOR_X[0] - 0.3, SECTOR_X[1] + 0.3)
    _x_face, _x_tip = HUB_X0 - 0.3, HUB_X0 + TIP_RISE
    _pts = [(-1.6, TONGUE_X[0] + 0.4), (1.6, TONGUE_X[0] + 0.4), (1.6, _x_face), (0.0, _x_tip), (-1.6, _x_tip)]
    _poly = [V(x, y, R_T[0]) for y, x in _pts]
    _tooth = Part.Face(Part.makePolygon(_poly + [_poly[0]])).extrude(V(0, 0, R_T[1] - R_T[0]))
    PAWL_FLEX = turned(_tongue.fuse(_tooth).removeSplitter(), PAWL_A0 - 90)       # for the clash check: tongue bent back
    pawl_tooth = turned(_tooth, PAWL_A0 - 90)
    PAWL_BACK = TIP_RISE + 0.1                          # tongue travel: to clear the face and 0.1 spare
    PAWL_MOVER = PAWL_FLEX
    _pb = [V(x, y, R_T[0]) for y, x in [(-1.6, TONGUE_X[0] + 0.4), (1.6, TONGUE_X[0] + 0.4), (1.6, _x_tip), (-1.6, _x_tip)]]
    _tooth_blank = Part.Face(Part.makePolygon(_pb + [_pb[0]])).extrude(V(0, 0, R_T[1] - R_T[0]))
    RING_POCKETED = sector_base.cut(turned(_pocket, PAWL_A0 - 90))                 # for the slit check
    PAWL_FLEX_FREE = turned(_arc_prism(R_T[0], R_T[1], TH_FREE, TH_ROOT - 3.0, *TONGUE_X).fuse(_tooth), PAWL_A0 - 90)
    _sector_cut = RING_POCKETED.fuse(turned(_root, PAWL_A0 - 90))
    sector_base = _sector_cut.fuse(PAWL_FLEX).removeSplitter()
    sector_base_blank = _sector_cut.fuse(turned(_tongue.fuse(_tooth_blank), PAWL_A0 - 90)).removeSplitter()   # a square tooth to file by hand

# A thin thrust ring on the sector's front face (Ø28.8 x 0.8, inside the pawl's radius): it keeps the ring 0.1 mm off the
# hub's rear face and, on the indexer stand, is what the disc rests on, so the disc sits where the model puts it.
SECTOR_FRONT_T = 0.8
_thrust = cyl_x(28.8, SECTOR_X[1] - 0.01, SECTOR_X[1] + SECTOR_FRONT_T, 0, 0).cut(cyl_x(2 * SECTOR_R[0], SECTOR_X[1] - 1, SECTOR_X[1] + 2, 0, 0))
sector_base = sector_base.fuse(_thrust).removeSplitter()
if FLEX_PAWL:
    sector_base_blank = sector_base_blank.fuse(_thrust).removeSplitter()

# The sector's rear stop: a plain spacer washer on the chamber tube between the lock housing's front
# face and the sector's ring - the LOWER half only: the pawl's boss rides the ring's back at the top
# and sweeps 2..90 deg as the sector turns, so a full ring would hit it. The housing's face is an
# annulus round the valve's axis, so the washer's lower part does the butting. In the model the gap
# is 0.4 (the ring stops GAP+0.4, the housing at GAP); printed stacks sit wider - SPACER_L is one
# number to tune to the bench.
SPACER_L = 0.25                     # the model's gap less clearances: 0.1 off the ring, 0.05 off the housing
sector_spacer = (cyl_x(31.0, -GAP + 0.05, -GAP + 0.05 + SPACER_L, 0, 0)
                 .cut(cyl_x(25.6, -GAP - 1.0, -GAP + 2.0, 0, 0))    # bore over the tube, past the housing's nose
                 .cut(box(-GAP - 2.0, -GAP + 3.0, -50.0, 50.0, 0.0, 50.0)))   # the top half away for the pawl's boss


def bolt_shape(block_deg):
    top = -HUB_R + bolt_depth(block_deg)
    return turned(bolt_prism(top, BOLT_LEN), DETENT_ANGLE + 90)


# The bolt as printed: BOLT_CLEAR smaller a side than the channel cut from it in the housing (the tip keeps its flat and 45 deg flanks).
BOLT_CLEAR = 0.25
_hw, _tw, _top = BOLT[1] / 2 - BOLT_CLEAR, BOLT_TIP / 2, -HUB_R + BOLT_DEPTH
detent_bolt_print = prism_x([(-_hw, _top - BOLT_LEN), (_hw, _top - BOLT_LEN), (_hw, _top - (_hw - _tw)), (_tw, _top), (-_tw, _top),
                             (-_hw, _top - (_hw - _tw))], HUB_X0 + BOLT_X0 + BOLT_CLEAR, HUB_X0 + BOLT_X0 + BOLT[0] - BOLT_CLEAR)


def detent_spring_pocket():
    c = Part.makeCylinder(2.15, 10.5, V(HUB_X0 + BOLT_X0 + BOLT[0] / 2, 0, -HUB_R - BOLT_LEN - 10.5), ZA)
    return turned(c, DETENT_ANGLE + 90)


# ---------------------------------------------------------------- parameters
PIN_Y = PIN_R0 * math.cos(math.radians(ARM_A0))                     # slider pin's y (24.5)
HAMMER_PIVOT = V(-85.0, 0, -8.0)    # behind the v1.1 cap, above the grip. 3 mm further back since 2026-11-08: the
                                    # upper M4 tie-rod heads (6.3 mm off the cap's back face, on the diagonals at
                                    # the pivot's height) then pass outside the sleeve's and the coils' O14
HAMMER_ARM = PIN_Y * math.tan(math.radians(SECTOR_SWING / 2)) / math.sin(math.radians(HAMMER_SWING / 2))
HAMMER_R = 10.0                     # its hub
SPUR_AXIS = 95.0                    # the hammer's outline is drawn along this direction at rest (deg from +x)
# Outline, (along the axis, back from it) in mm: a Colt-like neck sweeping back to a chequered comb, a claw
# hooked forward over the top, a lightening hole in the neck.
SPUR_OUTLINE = [(5, -8), (14, -8), (24, -6.5), (31, -5), (37, -6), (43, -9), (44, -6.5), (41, -2), (40.5, 2),
                (41, 7), (40, 12), (37.5, 17), (33.5, 21), (29, 22), (27, 19), (24, 14), (17, 10.5), (9, 9.5), (4, 8)]
SPUR_COMB = [(40.6, 3), (40.6, 7.5), (39.7, 12), (37.4, 16.3), (34, 19.8)]     # teeth along the comb
SPUR_HOLE = (17.0, 1.5, 3.2)        # along, back, radius
SPUR_STRETCH = 1.25                 # stage 2: the spur rides longer out of the ball, more for the thumb to press
SPUR = (95.0 + math.degrees(math.atan2(12.0, 38.0)), math.hypot(38.0, 12.0) * SPUR_STRETCH)   # where the thumb sits: direction, radius
CRANK_Y = (32.0, 35.0)              # the crank on the right, outside the valve body (y 31)
BRACKET_Y = (35.2, 38.2)            # the slider's bracket, outside the crank
SLIDER_REACH = 48.0                 # slider body: from its pin this far down (the cam slot)
try:
    LOCKLESS                        # False: the old lock (sleeve, pusher, cam slot in the slider), set before exec
except NameError:
    LOCKLESS = True
NOSE_GAP = 0.3                      # LOCKLESS: the housing's nose face to the hub's rear face (the sleeve's was 0.1 locked)
CHEEK_X = (-14.5, -7.0)             # slider's rear cheek with the cam slot (LOCKLESS: none, the bracket starts at the slider)
PUSHER_T = 3.0
CAM_RISE = 3.0                      # slider rise that opens the lock
TRIGGER_TRAVEL = 23.0               # deg; reset below: the pull that brings the trigger onto the vent valve's face
LOCK_SEAT_N = 20.0                  # sleeve onto the breech's O-ring before the shot (the shot adds ~41 N): bench it
MAINSPRING = dict(d=1.6, od=14.0, coils=6, y=((-27.5, -16.7), (-16.3, -5.6)))   # music wire torsion springs, x2, both left.
# 2026-11-08: with the pivot at -85 the ball's shell pinches at the coils' rear corner, so the pair sits
# ~2.7 further in and each spring's pitch closes ~0.9 (still 6 coils each: the pair's rate is unchanged).
SPRING_PEG = (45.0, 9.5, 1.5)       # on the hammer's hub, left face: direction at rest, radius, pin radius (the springs' legs);
                                    # 45 deg since 2026-11-08: at 30 the peg's rim grazed the upper-left rod head's washer
SLEEVE_R = 7.0                      # the hammer's sleeve on the axle, hub to crank: one printed part
GUIDE_ROD = dict(x=-8.5, y=28.6, d=3.0, z=(-68.5, 25.5))   # Ø3 rod, 94 mm: drops in from the ceiling and
                                                             # stops 1.2 mm short of the underside (z -70)


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
    return V(H.x, y, H.z) + _e1 * (a * SPUR_STRETCH) + _e2 * b


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
# The Ø3 crank pin rides the slider's bracket slot: give the arm a hole to glue it into (as the
# slider's pin, same bug there) - it had none, the drawn pin just overlapped solid plastic.
hammer_body = (hub_h.fuse(spur).fuse(sleeve).fuse(crank).fuse(peg)
               .cut(Part.makeCylinder(4.15, 100, V(H.x, -50, H.z), YA))
               .cut(Part.makeCylinder(1.5, CRANK_Y[1] - CRANK_Y[0] + 2.0, V(c_tip0.x, CRANK_Y[0] - 1.0, c_tip0.z), YA))
               .removeSplitter())
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
_cx0 = SLIDER_X[0] if LOCKLESS else CHEEK_X[0]           # where the bracket leaves the slider
SLIDER_H = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], -SLIDER_REACH, 6)
if not LOCKLESS:
    SLIDER_H = SLIDER_H.fuse(box(CHEEK_X[0], CHEEK_X[1], SLIDER_Y[0], SLIDER_Y[1], -SLIDER_REACH, 6))
else:
    # The guide rod (x = -8.5) is only 0.5 mm from the plate's back face (x = -9): without the old cheek its Ø3.3 hole was
    # an open groove and the slider just lay on the rod. A boss behind the plate gives the hole a 1.5 mm wall all round.
    SLIDER_H = SLIDER_H.fuse(box(GUIDE_ROD["x"] - 3.2, SLIDER_X[0] + 0.01, GUIDE_ROD["y"] - 3.2, GUIDE_ROD["y"] + 3.2,
                                 -SLIDER_REACH, 6))
SLIDER_H = (SLIDER_H.fuse(box(_cx0, SLIDER_X[1], SLIDER_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .fuse(box(min(xs) - 8, _cx0 + 0.01, BRACKET_Y[0], BRACKET_Y[1], D_YOKE - 6, D_YOKE + 6))
            .cut(box(min(xs) - 2, max(xs) + 2, BRACKET_Y[0] - 1, BRACKET_Y[1] + 1, D_YOKE - 1.7, D_YOKE + 1.7)))
if not LOCKLESS:
    SLIDER_H = SLIDER_H.cut(cam_slot())
SLIDER_H = SLIDER_H.cut(Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.15, 200, V(GUIDE_ROD["x"], GUIDE_ROD["y"], -100), ZA))
# The Ø3 steel pin that drives the sector sits in a hole through the slider's plate (glued; it had no hole at all, the
# drawn pin just overlapped solid plastic): the slider's pin height is z = 0 in its own frame, y = PIN_Y.
SLIDER_H = SLIDER_H.cut(Part.makeCylinder(1.5, SLIDER_X[1] - SLIDER_X[0] + 2.0, V(SLIDER_X[0] - 1.0, PIN_Y, 0), XA))


def slider_h(c):
    z = slider_z(c)
    return SLIDER_H.translated(V(0, 0, z)), cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], PIN_Y, z)


# ---------------------------------------------------------------- lock pusher (ring in the flange's bore, lug and pin to the cam)
ring = cyl_x(LOCK_PISTON_D - 0.4, -PUSHER_T / 2, PUSHER_T / 2, 0, Z_FIRE).cut(
    cyl_x(SLEEVE_BORE + 0.6, -5, 5, 0, Z_FIRE))
lug = box(-PUSHER_T / 2, PUSHER_T / 2, (SLEEVE_BORE + 1) / 2, SLIDER_Y[0] - 0.5, Z_FIRE - 3, Z_FIRE + 3)
cam_pin = Part.makeCylinder(1.5, 2.5 + 3.0, V(0, SLIDER_Y[0] - 2.5, Z_FIRE), YA)      # 3 mm into the cheek, short of the guide rod
PUSHER = ring.fuse(lug.fuse(cam_pin))          # one lug, on the right where the slider is


def pusher_shape(lk):
    return PUSHER.translated(V(X_OPEN + LOCK_STROKE * lk, 0, 0))


_lug_slot = box(X_OPEN - PUSHER_T / 2 - 0.4, X_LOCKED + PUSHER_T / 2 + 0.4,
                (SLEEVE_BORE + 1) / 2 - 1, 30, Z_FIRE - 3.5, Z_FIRE + 3.5)
lock_housing_h = lock_housing_plain.cut(_lug_slot)

if LOCKLESS:
    # A plain block with a Ø SEAT_D through bore that ends in the sleeve's nose (NOSE_D out), NOSE_GAP short of the hub.
    # lock_housing_plain minus the pockets for the flange and the tube, as the bench try proved (0.3 mm off the hub, it shot well).
    x_nose = HUB_X0 - NOSE_GAP
    nose_ring = cyl_x(NOSE_D, -GAP - 1.0, x_nose, 0, Z_FIRE)
    lock_housing_h = (cyl_x(BREECH_FLANGE_D, -GAP - LOCK_H, -GAP, 0, Z_FIRE)
                      .common(box(-GAP - LOCK_H - 1, -GAP + 1, -30, 30, Z_FIRE - 30, Z_FIRE + BREECH_FLAT_X))
                      .fuse(nose_ring)
                      .cut(cyl_x(SEAT_D, -GAP - LOCK_H - 1, x_nose + 1.0, 0, Z_FIRE))
                      .cut(Part.makeCompound([cyl_x(BREECH_BOLT_HOLE, -GAP - LOCK_H - 1, -GAP + 1,
                                                    -BREECH_BOLT_R * math.sin(math.radians(a)),
                                                    Z_FIRE + BREECH_BOLT_R * math.cos(math.radians(a))) for a in LOCK_BOLTS]))
                      .removeSplitter())

# The sector's rear stop: a FULL ring on the chamber tube, from the sector's ring back to the QEV
# body's face (x -28), with the sector's road carved through it as one revolved wedge - its swept
# footprint in polar: the angles the pawl's boss covers over the stroke (the rest at -68 deg with its
# own spread, to the cocked 0), from the bore out past the boss's outer corner. One revolve, no
# pose-compound scallops; the plunger's retraction rides the same wedge. Bore slips the tube; the QEV
# body's nose and the lock housing's flange (both centred 27 below the axis) carve their passages at
# the rear; the ring's rear face and the body's face are its stops, so the sector's axial float is
# the two 0.05 gaps. The length is the model's ring-to-body span - file to fit on a printed stack.
SECTOR_SPACER = dict(x_rear=X_BODY_TOP + 0.05, x_front=SECTOR_X[0] - 0.05, od=31.0, bore=25.6)
_ROAD_A0, _ROAD_A1, _ROAD_R = -92.0, 80.0, 24.5     # the boss's angular road: -44 at rest to 73 at full cock, with margins
def _pol(r, a):
    return V(0, r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
_road_pts = ([V(0, 0, 0)]
             + [_pol(_ROAD_R, a) for a in [_ROAD_A0 + (_ROAD_A1 - _ROAD_A0) * k / 16.0 for k in range(17)]])
_road = Part.Face(Part.makePolygon(_road_pts + [_road_pts[0]])).extrude(
    V(SECTOR_SPACER["x_front"] - SECTOR_SPACER["x_rear"] + 2.0, 0, 0)).translate(
    V(SECTOR_SPACER["x_rear"] - 1.0, 0, 0))
sector_spacer = (cyl_x(SECTOR_SPACER["od"], SECTOR_SPACER["x_rear"], SECTOR_SPACER["x_front"], 0, 0)
                 .cut(cyl_x(SECTOR_SPACER["bore"], SECTOR_SPACER["x_rear"] - 1.0, SECTOR_SPACER["x_front"] + 1.0, 0, 0))
                 .cut(_road)                                # the sector's road: one revolved wedge, its polar footprint
                 .cut(valve_body).cut(lock_housing_h)       # their noses carve their own passages
                 .cut(valve_rods_cut))                     # and the tie rods' tips (M4 x 50 run 4.7 mm past the body's face):
                                                            # the top pair crosses the ring at r 20.5 off the axle, past the road

# ---------------------------------------------------------------- trigger: one stage, onto the vertical vent valve
# A sickle lever hanging down off the back-set pivot at rest: the finger face hollowed (the pad sits
# in it), the claw curling forward at the end. Behind the hub a lug whose top edge (local z -1.0) is
# the stop that meets the valve's bottom face, 0.5 above the wide pad's face under the plunger. The
# pull lifts the pad ~2.8 mm - the first 0.3 closes the gap, ~2.5 pushes (the click is at 2.0).
TRIGGER_WIDTH = 6.0
TRIGGER_OUTLINE = [(0.0, 3.3), (9.0, 1.8), (17.0, 0.5), (25.0, 1.5), (32.6, 0.5), (33.5, -4.0), (32.0, -11.0),
                   (31.0, -17.0), (31.2, -22.0), (32.6, -26.5), (35.0, -30.0), (37.5, -31.5), (36.5, -33.5),
                   (33.0, -33.5), (29.5, -31.0), (26.8, -26.0), (25.0, -19.0), (24.0, -12.0), (24.0, -4.0),
                   (16.0, -4.5), (8.0, -5.2), (1.5, -4.6)]   # the spine reaches forward; face and claw at the old spot


def _trigger_blank():
    t = Part.makeCylinder(3.6, TRIGGER_WIDTH, V(0, -TRIGGER_WIDTH / 2, 0), YA)          # round the pivot pin
    pts = [V(x, -TRIGGER_WIDTH / 2, z) for x, z in TRIGGER_OUTLINE]
    c = Part.BSplineCurve()
    c.interpolate(pts, PeriodicFlag=True)
    t = t.fuse(Part.Face(Part.Wire(c.toShape())).extrude(V(0, TRIGGER_WIDTH, 0)))       # the sickle blade
    t = t.fuse(box(-13.0, -2.0, -TRIGGER_WIDTH / 2, TRIGGER_WIDTH / 2, -5.0, -1.0))     # the rear lug, its top = the stop
    t = t.fuse(box(-14.0, -7.0, 2.8, 26.0, -5.0, -1.5))                                 # the wide pad under the plunger (y 21)
    for z_ in (-15.0, -18.0, -21.0):                                                    # finger grooves in the hollow
        g = Part.makeCylinder(0.8, TRIGGER_WIDTH + 2, V(28.0 + 3.0 + 0.1 * (z_ + 18) ** 2 / 3, -TRIGGER_WIDTH / 2 - 1, z_), YA)
        t = t.cut(g)
    return t.cut(Part.makeCylinder(1.6, TRIGGER_WIDTH + 2, V(0, -TRIGGER_WIDTH / 2 - 1, 0), YA)).removeSplitter()


TRIGGER = _trigger_blank()

# ---------------------------------------------------------------- vent valve: an AirTAC M3R110-06 without its roller
# Catalog drawing of the M3B110-06 body (the R head is only the roller), stem end up on the sheet:
# A 27 wide, B 18 thick, D 46.5 the rectangle, C 52 out to the stem boss. Three PT1/8 ports, and they
# are on the narrow faces (width B), not on the wide faces:
#   one narrow face carries two, PB = 15.5 from the end opposite the stem up to the lower centre and
#   PA = 16 between centres, so the upper centre is 31.5. That upper port is the exhaust: the catalog
#   puts the exhaust over the body so a silencer screws on there.
#   the opposite narrow face carries one, PC = 23.5 from the same end.
# The owner's valve (roller already off) is stamped: R is the hole next to the stem, P the far hole
# on that same narrow face, A the single hole on the opposite face. The sticker's symbol is the
# closed one (at rest A–R, pressed P–A). Supply and exhaust are swapped, so the valve is normally
# open: the receiver feeds R and the silencer sits on P. The pilot on A is charged at rest and dumps
# when the plunger is pushed.
# Stood plunger-down, the catalog's stem end is z = VENT_Z0, so a catalog height h sits D - h above
# the plunger face: R 15.0, P 31.0, A 23.0.
# The ports are on the narrow faces (the face is B = 18 wide); the wide face (A = 27) has the three
# Ø3.3 holes. The fittings are straight R1/8 push-ins (thread inside the port): Ø10 x 20 on A for the
# 4 mm pilot, Ø12 x 22 on R for the 6 mm supply. The silencer on P is straight too. An elbow on the
# forward face would meet the QEV cap 7 mm ahead of it, so the valve is turned about the plunger and
# the narrow faces point left and right: along x the body is the 18 mm thickness, along y the 27 mm
# width. A leaves straight to the left, P and R straight to the right (P above R). The left face stays
# at y = VENT_Y0, clear of the hammer, so the plunger sits at y 21 and the trigger's pad reaches y 26.
# The holes run through the 18 mm thickness (KA 18, KB 15.5, KC 16): the pair 18 apart across the
# width, one on the centre. The valve is not screwed down. It drops into a close-fit socket (side
# plate off) and stands on two printed feet. The spool shifts in the plunger's 2..3 mm; the lug's
# shoulder on the valve's bottom face is the trigger's stop.
AIRTAC = dict(L=46.5, W=18.0, T=27.0, plunger=(6.0, 3.0),
              straight={"A": (10.0, 20.0), "R": (12.0, 22.0)},   # (od, stick-out) of a straight R1/8 push-in
              silencer=(8.0, 14.0),
              ports={"A": 23.0, "R": 15.0, "P": 31.0},
              holes=((-9.0, 31.0), (9.0, 31.0), (0.0, 15.0)))   # (offset across the width, height from the plunger face)
VENT_X, VENT_Y0, VENT_Z0 = -91.5, 7.5, -62.2     # the body: x centre, y min, bottom face (standing on its feet).
# 1 mm further back since 2026-11-08: the AirTAC's front face was 0.3 mm into the bottom-right tie-rod
# head's pocket (the head stands 6.3 mm off the cap's back face at y +18.7, z -45.7). And 2 mm lower:
# the real body is 46.5 tall (the catalog's D) - at -60.2 its top-right corner sat inside the sleeve's
# bottom segment; a notch there would not survive the swing (the sleeve's material rotates into it).
# At -62.2 the valve's top (-15.7) is below the sleeve's bottom (-15) over the whole swing.
# Turned about the plunger (2026-11-09) the body is 18 along x, so the front face sits at x -82.5,
# 4.5 mm further from that tie-rod head than the 27 mm body was.
VENT_GAP = 0.3                      # the pad's face to the plunger's tip at rest
VENT_SWITCH = 2.0                   # measured on the bench M3R110: it clicks over ~2 mm into the plunger's travel


_LUG_X, _LUG_Z = -13.0, -1.0       # the shoulder's stop edge (local): the lug's flat top, rear corner
_z_at = lambda deg: TRIGGER_PIVOT.z - _LUG_X * math.sin(math.radians(deg)) + _LUG_Z * math.cos(math.radians(deg))
_lo, _hi = 5.0, 40.0                # the pull that brings the lug's shoulder onto the valve's bottom face
for _ in range(20):
    _mid = (_lo + _hi) / 2
    if _z_at(_mid) < VENT_Z0:
        _lo = _mid
    else:
        _hi = _mid
TRIGGER_TRAVEL = _lo
VENT_PUSH = _z_at(TRIGGER_TRAVEL) - _z_at(0.0) - VENT_GAP      # the shoulder's rise less the gap it closes first


def vent_port(name):
    """Where the tube leaves the straight fitting, and which way (unit vector, out of the fitting)."""
    a = AIRTAC
    z = VENT_Z0 + a["ports"][name]
    y0, y1 = VENT_Y0, VENT_Y0 + a["T"]
    if name == "A":                                          # left face, the push-in points left
        return V(VENT_X, y0 - a["straight"]["A"][1], z), V(0, -1, 0)
    if name == "R":                                          # right face, the push-in points right
        return V(VENT_X, y1 + a["straight"]["R"][1], z), V(0, 1, 0)
    return V(VENT_X, y1 + a["silencer"][1], z), V(0, 1, 0)   # the silencer, straight out


def _vent_valve():
    a = AIRTAC
    x0, x1 = VENT_X - a["W"] / 2, VENT_X + a["W"] / 2
    y0, y1 = VENT_Y0, VENT_Y0 + a["T"]
    yc = (y0 + y1) / 2
    body = box(x0, x1, y0, y1, VENT_Z0, VENT_Z0 + a["L"])
    for hy, hz in a["holes"]:                                # Ø3.3 through the 18 mm thickness
        body = body.cut(Part.makeCylinder(1.65, a["W"] + 2, V(x0 - 1, yc + hy, VENT_Z0 + hz), XA))
    fit = []
    od, stick = a["straight"]["A"]
    za = VENT_Z0 + a["ports"]["A"]
    fit.append(Part.makeCylinder(od / 2, stick, V(VENT_X, y0, za), V(0, -1, 0)))
    od, stick = a["straight"]["R"]
    zr = VENT_Z0 + a["ports"]["R"]
    fit.append(Part.makeCylinder(od / 2, stick, V(VENT_X, y1, zr), V(0, 1, 0)))
    zp = VENT_Z0 + a["ports"]["P"]
    fit.append(Part.makeCylinder(a["silencer"][0] / 2, a["silencer"][1], V(VENT_X, y1, zp), V(0, 1, 0)))
    plunger = Part.makeCylinder(a["plunger"][0] / 2, a["plunger"][1] + 0.01,
                                V(VENT_X, yc, VENT_Z0), V(0, 0, -1))   # pointing down at the pad
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
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, sec),
            "Slider": sl, "Pin": pin, "Bolt": bolt_shape(st["block"]), "Hammer": hammer_shape(c),
            "Trigger": trigger_h(st["trig"])} | ({} if FLEX_PAWL else {"Pawl": turned(tooth_, sec)}) \
        | ({} if LOCKLESS else {"Sleeve": lock_sleeve(lock_h(c)), "Pusher": pusher_shape(lock_h(c))})


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
         "mainsprings": mainsprings,
         "tie rods": valve_rods, "lock bolts": lock_bolts}   # the valve's own fasteners, drawn since 2026-11-08: every
                                                             # moving part is checked against them over the stroke
report = [NAME]
worst = {}
for i in range(11):
    c = i / 10
    st = dict(cock=c, block=block_drive(c), bend=0.0, trig=0.0)
    sh = pose(st)
    for mv_ in [m_ for m_ in ("Hammer", "Slider", "Pusher", "Sector", "Sleeve", "Trigger", "Pin") if m_ in sh]:
        for fx_, s_ in FIXED.items():
            v_ = sh[mv_].common(s_).Volume
            worst[(mv_, fx_)] = max(worst.get((mv_, fx_), 0.0), v_)
    for a_, b_ in [p_ for p_ in (("Hammer", "Slider"), ("Slider", "Block"), ("Pusher", "Sleeve"), ("Hammer", "Trigger"),
                                 ("Slider", "Sector"), ("Pusher", "Slider")) if p_[0] in sh and p_[1] in sh]:
        v_ = sh[a_].common(sh[b_]).Volume
        worst[(a_, b_)] = max(worst.get((a_, b_), 0.0), v_)
    if i % 2 == 0:
        report.append("  cock %.1f  hammer %+5.1f deg  slider pin z %+6.1f  sector %+5.1f  block %+5.1f deg%s"
                      % (c, hammer_rot(c), slider_z(c), sector_turn(c), block_drive(c), "" if LOCKLESS else "  lock %.2f" % lock_h(c)))
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
if LOCKLESS:
    report.append("  no lock: housing with the nose %.1f mm off the hub, one print; the mainspring is as sized for the lock "
                  "(%.2f N*m at rest), softer is enough now" % (NOSE_GAP, torque))
else:
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
report.append("  vent valve: AirTAC M3R110-06 standing at (%.1f, y %.1f..%.0f, bottom z %.1f); trigger pull %.1f deg"
              " lifts its plunger %.1f mm (it clicks at %.1f: %.1f to spare), the lug's shoulder stopping on the body"
              % (VENT_X, VENT_Y0, VENT_Y0 + AIRTAC["T"], VENT_Z0, TRIGGER_TRAVEL, VENT_PUSH, VENT_SWITCH, VENT_PUSH - VENT_SWITCH))
if FLEX_PAWL:
    _I = (R_T[1] - R_T[0]) * TONGUE_T ** 3 / 12
    report.append("  pawl tongue %.0f x %.1f x %.1f mm: ~%.2f N (PETG) / %.2f N (PLA) at %.1f mm of deflection, strain ~%.1f %%  (a straight-beam estimate)"
                  % (TONGUE_L, TONGUE_T, R_T[1] - R_T[0], 3 * 1900 * _I * PAWL_BACK / TONGUE_L ** 3, 3 * 3300 * _I * PAWL_BACK / TONGUE_L ** 3,
                     PAWL_BACK, 150 * TONGUE_T * PAWL_BACK / TONGUE_L ** 2))
report.append(("  pawl idles %.1f deg of the hammer before it drives" + ("" if LOCKLESS else ": the lock is open by then"))
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
