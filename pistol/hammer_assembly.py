# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the thumb-hammer mechanism inside the Skaven look.

pistol/hammer_layout.py's mechanism (v1.1 valve, lock pusher, block, pawl
sector, slider, detent, hammer, one-stage trigger) with 200 mm barrels,
dressed as pistol_assembly.py (the lever variant):

    frame ..... the v12 silhouette: a drum O85 running straight to the
                block and closing in a ball tail over the hammer set (the
                cage's discs trim flush, the axle's ends read as rivets);
                a narrow slab under it carries the trigger, and its rear
                column holds the vent valve standing vertical in a socket
                (stage 2: the trigger's rear lug lifts its plunger); the
                QEV cap crosses the slab in its own window, a right cheek
                shrouds the slider's bracket; the spur comes out of the
                ball's top through a slot over its swing
    grip ...... the rag-wrapped wooden grip, warpstone pommel with the
                hose; it butts the slab's underside

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
import time as _t
_T0 = _t.time()
def _tick(msg):
    print("[%6.1fs] %s" % (_t.time() - _T0, msg), flush=True)

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
try:
    BARREL_TUBE                                 # or set before exec
except NameError:
    BARREL_TUBE = 200.0                         # barrel tube as cut (13 mm of it in the hub)
try:
    VALVE                                       # 'v11' or 'v13', see mech_layout.py
except NameError:
    VALVE = "v13"
try:
    CHECKS                                      # set before exec: False = build + document only, skip the
except NameError:                               # long validation pass (fast look runs; commit on True runs)
    CHECKS = True
HUB_T_HAMMER = 14.0                             # the block's rear disc (hammer_layout.py)
STUB = BARREL_TUBE - (HUB_T_HAMMER - 9.0)       # the tube from the rear disc's seat (9 deep) to the muzzle
exec(open(os.path.join(REPO, "pistol", "hammer_layout.py")).read())
_tick('layout built')

NAME = "pistol_hammer_assembly"
random.seed(7)

# ---------------------------------------------------------------- parameters
FRAME = dict(x=(HAMMER_PIVOT.x - HAMMER_R - 8.0, -1.0), y=(-45.0, 45.0), z=(-76.0, 31.0))   # the plan the v12 silhouette hangs on
DRUM_R, DRUM_X0 = 42.5, -65.5       # the v12 drum: O85 straight to the block, a ball tail to x -108
SLAB = dict(x=(-108.0, -1.0), y=23.0, z=(-70.0, -5.0))          # the narrow body under the drum
CHEEK = dict(x=(-96.0, -5.0), y=(23.0, 43.0), z=(-70.0, 18.5))  # 0.5 proud of the drum: its outer face is the frame's bed face
EVA_T = 3.0                         # the frame's look: an EVA skin this thick over a printed cage
CAGE_T = 3.0
CAGE_WINDOWS = dict(side=((-40.0, -16.0), (-60.0, 12.0)), top=((-50.0, -18.0), 24.0), bottom=((-40.0, -10.0), 24.0))
try:
    STANDOFFS                       # set before exec (the zigzag study moves the left one off the push-rod's height)
except NameError:
    STANDOFFS = ((-48.0, -5.0, (-1,)),)   # x, z, sides: the side plate's peg to the QEV body's flank
                                           # (below z -34 the slab's own mass holds the body: no pegs there)
# The whole left side opens: one plate carries the drum's and the ball's flank band (where the room's
# wall bosses stand) and the slab's left wall with the trigger's slot in it; the mechanism, the trigger
# on its cheeks (they sit in the core, not the wall) and the valve's socket all open with it off.
SIDE_BOSSES = ((-50.0, 22.0), (-10.0, 22.0), (-30.0, 30.0), (-70.0, 30.0), (-90.0, 6.0))   # x, z: clear of the QEV stack and the hammer's swing
BOSS_D, BOSS_L = 8.0, 10.0
TRIGGER_CHEEKS = dict(x=(-84.0, -76.0), y=(3.3, 7.0))          # the trigger's pivot (an M3 screw and nut) between them
GRIP_SCREWS = ((-104.0, 18.0), (-104.0, -18.0))   # x, y: down through the slab's floor into 24 mm of grip wood
VALVE_BOX_Y = 33.0                  # the tang is a box under the frame round the vent valve and its fittings
GUARD_TAB = dict(x=(-9.0, -5.0), y=5.0, t=11.0)   # the guard's front tab, under the slab's floor
SPUR_SLOT = dict(a=(58.0, 210.0), r=SPUR[1] + 10.0, y=6.5)    # the spur's swing out of the top rear
FRAME_FILLET = 12.0

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
# The v12 silhouette: a drum O85 that runs straight to the block and closes in a ball tail over the
# hammer set; under it a narrow slab +-23 carries the trigger and the vent valve; a right cheek shrouds
# the slider's bracket and the crank's swing. The QEV cap crosses the slab in its own window (the wall
# is cut with the stack's imprint); nothing sticks out past the block's O85 but the cheek's corner.
fx, fy, fz = FRAME["x"], FRAME["y"], FRAME["z"]
P_ = HAMMER_PIVOT
HEEL_X = fx[0] - 7.0                # the plan's back face (the jaw's, the discs' and the collar's)
FIN = dict(x=(DRUM_X0 - DRUM_R + 2.5, fx[0] + 4.3), y=14.0, z=(P_.z - 6.0, P_.z + 18.0))
_drum = Part.makeCylinder(DRUM_R, fx[1] - DRUM_X0, V(DRUM_X0, 0, 0), XA)
_ball = Part.makeSphere(DRUM_R, V(DRUM_X0, 0, 0))                  # the tail: a shell round the hammer set, tip x -108
_bore = Part.makeCylinder(DRUM_R - 3.0, fx[1] - DRUM_X0, V(DRUM_X0, 0, 0), XA)   # the straight room, a 3 mm wall; behind the
                                                                   # equator the tail's room is the sphere's own bore
_ball_bore = Part.makeSphere(DRUM_R - 3.0, V(DRUM_X0, 0, 0))       # the tail's own hollow;
                                                              # behind x -104.5 the tip is solid, and the pilot's
                                                              # G1/8 fitting comes through it
_slab = box(SLAB["x"][0], SLAB["x"][1], -SLAB["y"], SLAB["y"], SLAB["z"][0], SLAB["z"][1])
_cheek = box(CHEEK["x"][0], CHEEK["x"][1], CHEEK["y"][0], CHEEK["y"][1], CHEEK["z"][0], CHEEK["z"][1])
# The hammer's axle sockets in two end discs of the cage (y +-39.5..42.5); trimmed common with the drum
# and the ball they sit flush in the silhouette, their rims print bare, the shaft's ends stand out as
# rivets. The crank, its pin, the slider bracket and the valve cap all cross the open room between them.
WHEEL_R = 22.5                      # the discs' radius; their rims print bare
_disc = lambda y0: Part.makeCylinder(WHEEL_R, 3.0, V(P_.x, y0, P_.z), YA)
_cage = (_disc(-42.5).fuse(_disc(39.5))
         .common(_drum.fuse(_ball))
         .common(Part.makeCylinder(41.3, 200.0, V(-200, 0, 0), XA)))   # rims flush under the cheek: it is the bed face
_fin = box(FIN["x"][0], FIN["x"][1], -FIN["y"], FIN["y"], FIN["z"][0], FIN["z"][1])
_room = _bore.fuse(_ball_bore)      # the slab and the cheek butt the room, never enter it
outer = (_drum.fuse(_ball).fuse(_slab).fuse(_cheek).fuse(_cage).fuse(_fin)).cut(_room).removeSplitter()
# The mainsprings' fixed legs rest on a rib reaching x -97, where the ball's taper would pinch them:
# a local notch in the flank opens the shelf's zone (cut here, while the body is still simple).
outer = outer.cut(box(-99.0, -90.5, -33.0, -25.5, -27.0, -15.0))   # open the shelf's zone, keep a bond strip for the rib at x -90.5..-88
# The slider rides outside the slab, the cheek its printed shroud: the body's tunnel (up its rod
# sleeve's travel) and the bracket arm's tunnel are plain boxes over their swept zones, and the crank
# with its pin crosses the cheek's inner band - cut here for the same reason (simple body, fast and
# robust booleans); the worst-case checks verify the cover over the stroke.
outer = outer.cut(box(-59.5, -4.4, 22.4, 38.8, -65.1, 19.0))     # the slider's tunnel, body to bracket arm
outer = outer.cut(box(-90.5, -44.0, 28.5, 39.0, -26.0, 18.0))   # the crank and its pin past the cheek's inner face
_tick('outer built')
frame = outer                                       # the pockets and the sweeps cut below shape it
skin = Part.makeCompound([])                                    # no EVA on the frame: the drum is the look
def _room_wall(x_, z_):
    """The radius of the room's wall at this x, z: the drum's bore, or the ball's behind the drum."""
    if x_ < DRUM_X0:
        r2 = (DRUM_R - 3.0) ** 2 - (DRUM_X0 - x_) ** 2 - z_ ** 2
    else:
        r2 = (DRUM_R - 3.0) ** 2 - min(abs(z_), DRUM_R - 3.5) ** 2
    return math.sqrt(max(r2, 4.0))


def _standoffs(sign):
    out = []
    for x_, z_, sides in STANDOFFS:
        if sign in sides:
            _b = sign * (_room_wall(x_, z_) + 0.5)
            s_ = Part.makeCylinder(5.0, abs(_b) - 13.5 + 1.0, V(x_, _b + sign * 1.0, z_), V(0, -sign, 0)).cut(valve_body)
            out.append(max(s_.Solids, key=lambda q: q.Volume))          # up to the valve's face, no crumbs past it
    return out


standoffs = Part.makeCompound(_standoffs(1) + _standoffs(-1))
if _standoffs(1):
    frame = frame.fuse(Part.makeCompound(_standoffs(1))).removeSplitter()  # the right ones, if any, stay on the frame
# (The old rear-stop pillar behind the valve cap is gone: the vent valve's socket pierces the floor
# right under it, so it never had a footing in any build - the cap is held by the block's straps fit.)
# The trigger's slot through the slab's mass: one opening from the rear lug (under the valve) to the
# blade's claw, through the floor into the open air below; the cheeks fuse in after, the hub rides between
t_slot = box(-95.0, -40.5, -4.5, 4.5, -71.0, -56.0)
frame, skin = frame.cut(t_slot), skin.cut(t_slot)
_tick('trigger slot cut')
# Slot in the top rear for the spur: a pie over its swing, round the pivot
H_ = HAMMER_PIVOT
pie = [V(H_.x, -SPUR_SLOT["y"], H_.z)] + [V(H_.x + SPUR_SLOT["r"] * math.cos(math.radians(q)), -SPUR_SLOT["y"],
                                            H_.z + SPUR_SLOT["r"] * math.sin(math.radians(q)))
                                          for q in [SPUR_SLOT["a"][0] + (SPUR_SLOT["a"][1] - SPUR_SLOT["a"][0]) * k / 12 for k in range(13)]]
spur_slot = Part.Face(Part.makePolygon(pie + [pie[0]])).extrude(V(0, 2 * SPUR_SLOT["y"], 0))
frame, skin = frame.cut(spur_slot), skin.cut(spur_slot)
pilot_hole = cyl_x(16, fx[0] - 9.0, fx[0] + EVA_T + CAGE_T + 1, 0, Z_FIRE)   # the cap's G1/8 fitting, through the tail's solid tip
frame, skin = frame.cut(pilot_hole), skin.cut(pilot_hole)

# ---------------------------------------------------------------- grip, trigger valves
a = math.radians(GRIP_ANGLE)
gd = V(-math.cos(a), 0, -math.sin(a))
gn = V(-math.sin(a), 0, math.cos(a))
grip = Part.makeLoft([Part.Wire(Part.Ellipse(GRIP_START + gd * (GRIP_LEN * t) + gn * (h / 2),
                                             GRIP_START + gd * (GRIP_LEN * t) + YA * (w / 2),
                                             GRIP_START + gd * (GRIP_LEN * t)).toShape()) for t, h, w in GRIP_SECTIONS],
                     True, False)
grip = grip.cut(outer)                          # the frame's foot covers its top
mini_valves = valves                            # hammer_layout's AirTAC vent valve
_a = AIRTAC
_vv = (box(VENT_X - _a["W"] / 2 - 0.5, VENT_X + _a["W"] / 2 + 0.5, VENT_Y0 - 0.5, VENT_Y0 + _a["T"] + 0.5,
           VENT_Z0, VENT_Z0 + _a["L"] + 0.5)                    # the valve's socket, its floor at the body's face
       .fuse(box(-96.0, -86.5, 2.5, 21.0, SLAB["z"][0] - 0.5, VENT_Z0 + 0.5))   # the plunger's and the pad's swing (overlaps the socket: no coplanar seam)
       .fuse(valve_bodies))                     # the elbows and the silencer carve their own ways out
frame, skin = frame.cut(_vv), skin.cut(_vv)
# The socket's own floor is the valve's seat: the pad's swing box carves the floor's middle away, and
# what remains at either side of it are the two feet the valve stands on - no extra fuses needed.
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
# ---------------------------------------------------------------- air: supply up the grip, pilot to the cap, a tee to the gauge
# Supply (6/4 hose from the receiver) in through the pommel, up the grip's channel, out under the slab's
# rear and up its right side outside to the vent valve's R elbow (which turns rear toward it). Pilot
# (4/2.5 PU) from the A elbow forward into the room, along it to the cap's G1/8 push-in - no printed
# channels: the tubes run in the air, crossing only the shell (an open groove) and the side plate's notch.
# The tee on the pilot feeds the gauge, out through the drum's upper-left flank, where the shooter sees it.
r_end, _ = vent_port("R")
a_end, _ = vent_port("A")
supply_pts = [c_end + gd * 70, c_end + gd * 15, GRIP_START + gd * (GRIP_LEN * 0.6), GRIP_START + gd * (GRIP_LEN * 0.3),
              V(-104, 8, -76), V(-106, 20, -72), V(-106, 30, -62), V(-103, 33, -50),
              V(r_end.x - 2, r_end.y, r_end.z), V(r_end.x, r_end.y, r_end.z)]
supply_line = pipe_along(supply_pts, 3.0)
pilot_pts = [V(a_end.x + 0.5, a_end.y, a_end.z), V(-84, -1, -36), V(-78, -3, -32),
             V(-80, -2, -28), V(-82, 0, Z_FIRE)]
pilot_line = pipe_along(pilot_pts, 2.0)
TEE = V(-78, -3, -32)
gauge_pts = [TEE, V(-76, -20, -28), V(-75, -34, -20), V(-63, -38, -10), V(-52, -38, -2), V(-34, -36, 10), V(-30, -37, 15)]
gauge_line = pipe_along(gauge_pts, 2.0)
tee = Part.makeSphere(4.0, TEE)
hose = supply_line
air_cut = pipe_along(supply_pts, 3.6).fuse(pipe_along(pilot_pts, 2.6)).fuse(pipe_along(gauge_pts, 2.6)).fuse(Part.makeSphere(5.0, TEE))

# ---------------------------------------------------------------- trigger guard: the old flat band, back by demand
# A flat band (ellipse GUARD_SECTION, wide across) swept along a teardrop that leaves the slab's floor
# going down and forward and runs into the grip's front along it - as before the v12 port.
GUARD = [V(-7, 0, -71), V(-11, 0, -87), V(-20, 0, -104), V(-38, 0, -114), V(-58, 0, -113), V(-76, 0, -100),
         V(-90, 0, -90), V(-97, 0, -85)]
GUARD_SECTION = (3.2, 2.2)                      # half-width across (y), half-thickness in the loop's plane
_gc = Part.BSplineCurve()
_gc.interpolate(GUARD)
_t0 = _gc.tangent(_gc.FirstParameter)[0]
_n0 = _t0.cross(YA).normalize()
_prof = Part.Ellipse(GUARD[0] + YA * GUARD_SECTION[0], GUARD[0] + _n0 * GUARD_SECTION[1], GUARD[0])
guard = Part.Wire(_gc.toShape()).makePipeShell([Part.Wire(_prof.toShape())], True, True)   # Frenet: no twist in a plane
guard = Part.Solid(guard) if guard.ShapeType != "Solid" else guard
guard = guard.cut(outer)                                 # the arms rise to the slab's floor, the rear runs into the grip
_gt = GUARD_TAB
guard = guard.fuse(box(_gt["x"][0], _gt["x"][1], -_gt["y"], _gt["y"], SLAB["z"][0] - _gt["t"], SLAB["z"][0]))    # its front tab, under the floor
guard = guard.cut(Part.makeCylinder(1.25, _gt["t"] + 1, V(sum(_gt["x"]) / 2, 0, SLAB["z"][0] - _gt["t"] - 0.5), ZA)).removeSplitter()
_tick('chin + guard built')

# ---------------------------------------------------------------- detent housing
detent_box = turned(box(HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2,
                        -HUB_R - 24, -HUB_R - 1.5), DETENT_ANGLE + 90)
detent_box = detent_box.cut(Part.makeCompound([bolt_shape(0.0), bolt_shape(30.0)])).cut(detent_spring_pocket())
_db = detent_box.BoundBox                       # a bracket from the cage's left side forward to it, clear of the block
# Its bracket is part of it and bolts to a flat pad on the drum's left (2 x M3 x 20 + nuts): the pad
# reaches from the detent's box in over the drum's flank (the slab is too narrow to butt).
detent_bracket = box(fx[1] - 8, _db.XMin + 0.9, _db.YMin + 2, -44.5, _db.ZMax - 10, _db.ZMax)
detent_bracket = detent_bracket.cut(cyl_x(2 * 47.6, HUB_X0, 50)).cut(detent_box)
detent_bolts = Part.makeCompound([Part.makeCylinder(1.7, 30, V(fx[1] - 5.0, -fy[1] - 10, z_), YA)
                                  for z_ in (_db.ZMax - 2.5, _db.ZMax - 7.5)])
detent_box = detent_box.fuse(detent_bracket).cut(detent_bolts).removeSplitter()
_tick('detent built')

# ---------------------------------------------------------------- the cage: open on the left, a side plate on screws
def _boss_base(x_, z_):
    """The y of the room's wall at this boss: the drum's bore, or the ball's behind the drum."""
    return -(_room_wall(x_, z_) + 0.5)
bosses = Part.makeCompound([Part.makeCylinder(BOSS_D / 2, BOSS_L, V(x_, _boss_base(x_, z_), z_), YA) for x_, z_ in SIDE_BOSSES])
frame = frame.fuse(bosses).fuse(box(-60, -8, -44.5, -31, _db.ZMax - 10, _db.ZMax - 3)).cut(detent_bolts)   # the detent's pad, on the drum's flank
tc = TRIGGER_CHEEKS
_tick('bosses + detent pad fused')
cheek_top = TRIGGER_PIVOT.z + 3.5
cheeks = Part.makeCompound([box(tc["x"][0], tc["x"][1], sg * tc["y"][0] if sg > 0 else -tc["y"][1],
                                tc["y"][1] if sg > 0 else -tc["y"][0], fz[0] + EVA_T + CAGE_T - 0.5, cheek_top)
                            for sg in (1, -1)])
cheeks = cheeks.cut(Part.makeCylinder(1.6, 2 * tc["y"][1] + 2, V(TRIGGER_PIVOT.x, -tc["y"][1] - 1, TRIGGER_PIVOT.z), YA))
frame = frame.fuse(cheeks)
_tick('cheeks fused')
# The slider's top meets a stop on the drum's ceiling at full cock: the hammer's back stop. The stop
# grows up to the drum's wall (its top is clipped to r 40, 0.5 mm into the 3 mm shell) and hangs a
# nook print from it. The guide rod anchors at it: the rod runs to the stop pad, not to the old flat cage.
z_sl_top = slider_z(1.0) + 6.0
_stop_prism = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], z_sl_top + 0.05, 44.0)
slider_stop = _stop_prism.common(Part.makeCylinder(40.0, 96.0, V(-96, 0, 0), XA))   # keep the top 0.5 into the 3 mm shell
# The mainsprings' fixed legs rest on a rib off the cage's rear wall, below and behind the hammer's hub.
spring_rib = box(fx[0] + 3.0, HAMMER_PIVOT.x - 6.0, MAINSPRING["y"][0][0] - 1.0, -6.0,
                 HAMMER_PIVOT.z - 15.0, HAMMER_PIVOT.z - 10.5)   # its x0 reaches the ball's shell (a small blister if it pokes)
rod_boss = Part.makeCylinder(4.0, 4.0, V(GUIDE_ROD["x"], GUIDE_ROD["y"], fz[0] + EVA_T + CAGE_T - 0.5), ZA)   # the guide rod's foot
# The spring rib is NOT fused into the frame: its inner reach (y -23..-6) hangs in the room's air and
# would be a floating island once the side band is cut away - the side plate carries it as a cantilever.
frame = frame.fuse(slider_stop).fuse(rod_boss)
_tick('stop + rib + rod fused')
frame = frame.cut(Part.makeCylinder(GUIDE_ROD["d"] / 2, GUIDE_ROD["z"][1] - GUIDE_ROD["z"][0], V(GUIDE_ROD["x"], GUIDE_ROD["y"], GUIDE_ROD["z"][0]), ZA))
shaft_holes = Part.makeCylinder(4.0, 2 * fy[1], V(HAMMER_PIVOT.x, -fy[1], HAMMER_PIVOT.z), YA)   # the axle: a press fit
frame = frame.cut(shaft_holes)
_tick('shaft holes cut')
side_cut = box(HEEL_X - 1, fx[1] + 1, -fy[1] - 1, -(SLAB["y"] - 3.0), SLAB["z"][0] - 1, fz[1] + 1)   # the flank band plus the slab's left wall: the whole side opens
side_plate = frame.common(side_cut).fuse(Part.makeCompound(_standoffs(-1))).fuse(spring_rib).cut(detent_bolts)   # + the spring shelf
if len(side_plate.Solids) > 1:          # OCCT leaves face-sliver crumbs in the cuts' windows: keep the real body
    side_plate = Part.makeCompound([s_ for s_ in side_plate.Solids if s_.Volume > 50.0])
_tick('side plate common')
frame = frame.cut(side_cut)
if len(frame.Solids) > 1:            # OCCT sometimes leaves a face-sliver crumb beside the main body
    frame = max(frame.Solids, key=lambda q: q.Volume)
# The right cover: the slab's right wall, the cheek and the flank band with the slider's tunnels, one
# plate mirroring the left - both sides open, the mechanism lays in from either side, the valve's
# socket becomes a through channel. It rides the Ø8 hammer axle (its flank band is the right bearing)
# and two M3 into the rear wall's strips below and above the socket.
side_cut_r = box(HEEL_X - 1, fx[1] + 1, SLAB["y"] - 3.0, fy[1] + 3.0, SLAB["z"][0] - 1, fz[1] + 1)
side_plate_r = (frame.common(side_cut_r).cut(valve_cap).cut(valve_body).cut(lock_housing_h)
                .cut(Part.makeCompound([Part.makeCylinder(1.7, 8.0, V(HEEL_X + 1.0, 21.5, z_), XA)
                                        for z_ in (-65.0, -11.0)])))           # 2 x M3 into the rear wall's strips
if len(side_plate_r.Solids) > 1:
    side_plate_r = Part.makeCompound([s_ for s_ in side_plate_r.Solids if s_.Volume > 50.0])
frame = frame.cut(side_cut_r)
if len(frame.Solids) > 1:
    frame = max(frame.Solids, key=lambda q: q.Volume)
_tick('side cut done')
pilots = Part.makeCompound([Part.makeCylinder(1.25, BOSS_L + 2, V(x_, _boss_base(x_, z_) - 1.0, z_), YA) for x_, z_ in SIDE_BOSSES])
frame = frame.cut(pilots)          # no removeSplitter here: it has collapsed this body once
_tick('pilots cut')
# The slider rides outside the slab, the cheek its printed shroud: the body's tunnel (up its rod
# sleeve's travel), the bracket arm's tunnel and the crank pin's stub through the cheek's inner band
# are plain boxes over their swept zones - the worst-case checks verify the cover over the stroke.
# (The hammer's own sweep needs no cut on the big solids: the room and the spur's pie clear it -
# the probes behind this measured 0.0 on the fin, the bosses and the spring rib - which keeps the
# build fast.)
_tick('sweeps + notch cut')
# The vent valve's stack (cap disc O62) is taller than the drum's bore: its rim crosses the drum's wall
# bottom in a pocket, and through the slab it cuts its own window (a 12 mm bridge under it ties the front
# and rear together with the drum above). The lock seats in the slab's front, flush with its sides.
frame = frame.cut(valve_cap).cut(valve_body).cut(lock_housing_h)
_sp_cut = [Part.makeCylinder(1.7, 10, V(x_, -fy[1] - 1, z_), YA) for x_, z_ in SIDE_BOSSES]
_sp_cut += [Part.makeCylinder(1.7, 16, V(x_, -fy[1] - 16, z_), YA) for x_, z_ in SIDE_BOSSES]   # out through any slag past the plate
side_plate = side_plate.cut(valve_cap).cut(valve_body).cut(lock_housing_h).cut(
    Part.makeCompound(_sp_cut))   # the flank band covers the QEV stack's rim: cut its imprint too (no splitter: it splits the plate)
if len(side_plate.Solids) > 1:            # and the crumbs it used to leave: keep the real body
    side_plate = Part.makeCompound([s_ for s_ in side_plate.Solids if s_.Volume > 50.0])
_tick('side plate cut')
skin = skin.cut(shaft_holes).cut(detent_box)

# ---------------------------------------------------------------- grip on screws; the guard's tab
# The grip butts the slab's underside, held by two ST2.9 down through the slab's floor into 24 mm of
# wood, plus the glue faces. The vent valve needs no fasteners: it drops into its socket from the room
# (side plate off) and stands on the two feet. The guard's front tab takes one ST2.9 down through the
# floor; its rear end glues into the grip's wood.
grip_pilots = Part.makeCompound([Part.makeCylinder(1.25, 9.0, V(x_, y_, fz[0] - 9.0), ZA) for x_, y_ in GRIP_SCREWS])
floor_holes = Part.makeCompound([Part.makeCylinder(1.7, 6.0, V(x_, y_, SLAB["z"][0] - 1.0), ZA)
                                 for x_, y_ in GRIP_SCREWS + ((sum(GUARD_TAB["x"]) / 2, 0.0),)])
grip = grip.cut(grip_pilots)
frame, skin = frame.cut(floor_holes), skin.cut(floor_holes)


# ---------------------------------------------------------------- dress: block straps, frame plates, crest, hammer, vial, gauge, pilot pipe
block_d = 2 * HUB_R
straps, spikes, strap_rivets = [], [], []
for x0, w, tilt in ((HUB_X0 + 12, 12, 0), ((HUB_X0 + HUB_T + STUB) / 2, 8, 4), (HUB_X0 + HUB_T + STUB - 14, 10, -3)):
    s = cyl_x(block_d + 5, x0, x0 + w).cut(cyl_x(block_d - 1, x0 - 1, x0 + w + 1))
    s.rotate(V(x0 + w / 2, 0, 0), YA, tilt)
    straps.append(s)
    for k in range(7):
        q = math.radians(360.0 / 7 * k + random.uniform(-10, 10))
        strap_rivets.append(V(x0 + w / 2, (block_d / 2 + 2.6) * math.cos(q), (block_d / 2 + 2.6) * math.sin(q)))
plates, plate_rivets = [], []
# The drum's upper flanks: curved shells hugging the body (r 42.5..46), above the QEV window and
# under the vial; the left one sits behind the gauge and rides on the removable side plate, the
# right one is clipped by the cheek's top band.
def _flank_shell(x0, x1, sign):
    ring = Part.makeCylinder(46.0, x1 - x0, V(x0, 0, 0), XA).cut(
        Part.makeCylinder(DRUM_R, x1 - x0 + 2.0, V(x0 - 1.0, 0, 0), XA))
    y_lo, y_hi = sorted((sign * 21.0, sign * 46.0))
    seg = ring.common(box(x0, x1, y_lo, y_hi, 5.0, 38.0))
    if sign > 0:
        seg = seg.cut(box(CHEEK["x"][0] - 0.3, CHEEK["x"][1] + 0.3, CHEEK["y"][0] - 0.3, CHEEK["y"][1] + 0.3,
                          CHEEK["z"][0] - 0.3, CHEEK["z"][1] + 0.3))
    return seg.cut(valve_cap).cut(valve_body)
plates.append(_flank_shell(-59.0, -48.0, -1))
plates.append(_flank_shell(-59.0, -5.0, +1))
# The slab's sides and the cheek's outer face: flat riveted armor; the left side's dress all rides
# on the removable side plate (glued), with a window over the spring shelf's notch.
plates.append(box(SLAB["x"][0], SLAB["x"][1], SLAB["y"], SLAB["y"] + 3.0, SLAB["z"][0], SLAB["z"][1])
              .cut(_vv).cut(valve_cap).cut(valve_body))
plates.append(box(SLAB["x"][0], SLAB["x"][1], -SLAB["y"] - 3.0, -SLAB["y"], SLAB["z"][0], SLAB["z"][1])
              .cut(valve_cap).cut(valve_body).cut(box(-99.0, -87.0, -33.0, -25.5, -27.0, -15.0)))
plates.append(box(-90.0, -8.0, CHEEK["y"][1], CHEEK["y"][1] + 3.0, -60.0, 12.0))
plate_rivets += [V(x_, CHEEK["y"][1] + 3.0, z_) for x_ in (-84.0, -46.0, -14.0) for z_ in (-52.0, 2.0)]   # the cheek pad
plate_rivets += [V(x_, -(SLAB["y"] + 3.0), z_) for x_ in (-100.0, -64.0, -30.0) for z_ in (-62.0, -14.0)]   # the left pad
plate_rivets += [V(x_, SLAB["y"] + 3.0, z_) for x_, z_ in ((-64.0, -62.0), (-30.0, -62.0), (-30.0, -14.0), (-12.0, -62.0), (-12.0, -14.0))]
plate_rivets += [V(x_, 44.0, 12.0) for x_ in (-50.0, -28.0, -8.0)] + [V(x_, 34.0, 30.0) for x_ in (-50.0, -28.0, -8.0)]   # the right shell
plate_rivets += [V(-54.0, -44.0, 12.0), V(-54.0, -34.0, 30.0)]                                           # the left shell
cx0 = H_.x + SPUR_SLOT["r"] * 0.35 + 8                 # the crest starts in front of the spur's slot
crest_pts = [(cx0, 0)]
for k in range(int((fx[1] - 14 - cx0 - 8) // 8.5)):
    crest_pts += [(cx0 + 6 + k * 8.5, 13 + random.uniform(0, 6)), (cx0 + 10 + k * 8.5, 3)]
crest_pts += [(fx[1] - 14, 0)]
crest = Part.Face(Part.makePolygon([V(px, -1.5, 41.0 + pz) for px, pz in crest_pts]
                                   + [V(crest_pts[0][0], -1.5, 41.0)])).extrude(V(0, 3, 0))
vc = V(fx[1] - 22, -16, 41.0)                      # the vial on the drum's top, clear of the crest
vial = Part.makeCylinder(8, 30, vc, ZA)
vial_caps = Part.makeCylinder(10, 4, vc - V(0, 0, 2), ZA).fuse(Part.makeCylinder(10, 4, vc + V(0, 0, 29), ZA))
cage = Part.makeCompound([Part.makeCylinder(1.2, 32, vc + V(10 * math.cos(math.radians(q)), 10 * math.sin(math.radians(q)), 0), ZA)
                          for q in (0, 120, 240)])
vial_stone = crystal(vc + V(0, 0, 14), V(0.2, 0.1, 1), 24, 5)
gp = V(-30.0, -38.0, 15.0)                 # the gauge on the drum's upper-left flank (below it the wall over the QEV body is 1.4 mm)
gauge = Part.makeCylinder(12.5, 8, gp, -YA).fuse(Part.makeCylinder(3, 6, gp + V(0, 2, 0), -YA))
gauge_glass = Part.makeCylinder(11, 1, gp - V(0, 8, 0), -YA)
needle = box(gp.x, gp.x + 9, gp.y - 9.8, gp.y - 9, gp.z - 0.6, gp.z + 0.6)
needle.rotate(gp, YA, -35)
pilot_pipe = pilot_line
_tick('dress built')
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
             .fuse(box(STRAP["x0"], HUB_X0 - 2.5, -s_w, s_w, fz[1], STRAP["z"][1])))   # its foot on the skin, short of the hub
top_strap = top_strap.cut(Part.makeCylinder(3.2, 20, V(X_AXLE_END - 1, 0, 0), XA))                 # the stud
STRAP_BOLTS = (-9.0, -5.0)          # x: 2 x M3 x 40 down through the foot into the cage's top, nuts inside
strap_bolts = Part.makeCompound([Part.makeCylinder(1.7, STRAP["z"][1] - fz[1] + 12, V(x_, 0, fz[1] - 10), ZA) for x_ in STRAP_BOLTS])
top_strap, frame, skin = top_strap.cut(strap_bolts), frame.cut(strap_bolts), skin.cut(strap_bolts)
nose = cyl_x(NOSE_OD, X_MUZZLE + WASHER_T, X_AXLE_END, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE, X_AXLE_END + 1, 0, 0))
washer = cyl_x(NOSE_OD, X_MUZZLE, X_MUZZLE + WASHER_T, 0, 0).cut(cyl_x(BARREL_OD + 0.4, X_MUZZLE - 1, X_MUZZLE + 2, 0, 0))
# The axle's front plug: on a 19 x 2.5 O-ring in the tube (the valve spigot's ring, same bore), not glued, so it
# comes out. A flange Ø25 x 2 on its face takes the tube's front end (the tube is 2 mm shorter for it), so the tube
# sits between the valve's shoulder and the flange; the flange runs in the nose sleeve's bore. An M6 nut glued into
# a hex pocket in its face, the stud's hole behind it blind, so no air leaks along the thread. The chamber's push on
# the plug goes stud -> strap as before. Prints flange down; the groove's square wall faces the flange (the ring is
# pushed onto it), its rear wall is 45 deg (a ceiling as printed).
PLUG_L, PLUG_HOLE, PLUG_FLANGE = 24.0, 14.0, 2.0
PLUG_ORING, PLUG_SQUEEZE = (19.0, 2.5), 0.12     # as the valve spigot's (module/stage3_qev.py ORING_SQUEEZE)
_pr, _gr = (23.8 - 0.3) / 2, 23.8 / 2 - PLUG_ORING[1] * (1 - PLUG_SQUEEZE)    # plug, groove root
_gx = X_AXLE_END - 15.0                          # square wall
_gw = 1.3 * PLUG_ORING[1]
axle_plug = Part.Face(Part.makePolygon([V(x_, 0, r_) for x_, r_ in (
    (X_AXLE_END - PLUG_L, 0), (X_AXLE_END - PLUG_L, _pr - 0.8), (X_AXLE_END - PLUG_L + 0.8, _pr),
    (_gx - _gw - (_pr - _gr), _pr), (_gx - _gw, _gr), (_gx, _gr), (_gx, _pr),
    (X_AXLE_END - PLUG_FLANGE, _pr), (X_AXLE_END - PLUG_FLANGE, BARREL_OD / 2), (X_AXLE_END, BARREL_OD / 2),
    (X_AXLE_END, 0), (X_AXLE_END - PLUG_L, 0))])).revolve(V(0, 0, 0), XA, 360)
plug_stretch = 2 * _gr / PLUG_ORING[0] - 1
axle = axle.cut(cyl_x(BARREL_OD + 1, X_AXLE_END - PLUG_FLANGE, X_AXLE_END + 1, 0, 0))     # its end on the flange
_hexr = 10.0 / 2 / math.cos(math.radians(30)) + 0.15                  # M6 nut, 10 across flats
_hex = Part.Face(Part.makePolygon([V(X_AXLE_END - 5.2, _hexr * math.cos(math.radians(60 * k)), _hexr * math.sin(math.radians(60 * k)))
                                   for k in range(7)])).extrude(V(5.3, 0, 0))
axle_plug = axle_plug.cut(_hex).cut(cyl_x(6.5, X_AXLE_END - PLUG_HOLE, X_AXLE_END, 0, 0))
axle_cap = Part.makeCylinder(3.0, PLUG_HOLE - 1 + s_t + 6, V(X_AXLE_END - PLUG_HOLE + 1, 0, 0), XA).fuse(   # M6 stud and a cap nut
    Part.makeCone(8, 5, 9, V(X_AXLE_END + s_t, 0, 0), XA))
strap_rivets += [V(x_, 0, STRAP["z"][1] + 0.3) for x_ in range(int(STRAP["x0"]) + 8, int(X_AXLE_END), 24)]
spikes += [spike(V(x_, 0, STRAP["z"][1] - 1), V(0.25, 0, 1), 14, 3.5) for x_ in (X_MUZZLE * 0.3, X_MUZZLE * 0.7)]
spikes += [spike(V(X_AXLE_END + s_t / 2, sd_ * s_w, STRAP["z"][1] - 8), V(0.3, sd_ * 1, 0.4), 14, 3.0) for sd_ in (-1, 1)]
_tick('supports built')

grip, frame, side_plate, side_plate_r, skin = (grip.cut(air_cut), frame.cut(air_cut), side_plate.cut(air_cut),
                                               side_plate_r.cut(air_cut), skin.cut(air_cut))
if len(frame.Solids) > 1:            # and again after the air lines: keep only the body, drop the crumbs
    frame = max(frame.Solids, key=lambda q: q.Volume)
grip = max(grip.Solids, key=lambda q: q.Volume) if len(grip.Solids) > 1 else grip
# The grip prints as two halves split on y = 0, each flat on its cut face: the hose lies in the open channel,
# the halves close on it, glued on two Ø3 steel dowels (6 mm into each half).
GRIP_DOWELS = [GRIP_START + gd * (GRIP_LEN * t) + gn * 13.0 for t in (0.3, 0.75)]
dowels = Part.makeCompound([Part.makeCylinder(1.6, 12.0, V(p_.x, -6.0, p_.z), YA) for p_ in GRIP_DOWELS])
grip = grip.cut(dowels)
_tick('grip split')
grip_left = grip.common(box(-400, 100, -100, 0, -400, 100)).removeSplitter()
grip_right = grip.common(box(-400, 100, 0, 100, -400, 100)).removeSplitter()
for _g in (grip_left, grip_right):
    if not _g.isValid():
        _g.fix(0.01, 0.001, 0.1)                 # the split leaves a sliver edge on the loft: heal it

# ---------------------------------------------------------------- checks
def hit(a, b):
    try:
        ba, bb = a.BoundBox, b.BoundBox
        if ba.XMax < bb.XMin or bb.XMax < ba.XMin or ba.YMax < bb.YMin or bb.YMax < ba.YMin \
                or ba.ZMax < bb.ZMin or bb.ZMax < ba.ZMin:
            return 0.0                           # disjoint boxes cannot share a volume: skip the common
        return a.common(b).Volume
    except ValueError:                           # OCCT gives up on touching faces: nudge it
        return a.translated(V(0, 0.01, 0.01)).common(b).Volume


rest = pose(REST)
if CHECKS:
    moving = tuple(n_ for n_ in ("Sector", "Pawl", "Slider", "Pin", "Bolt", "Hammer", "Sleeve", "Pusher", "Trigger") if n_ in rest)
    worst = {}
    for c in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        for tg in (0.0, 1.0):
            st = pose(dict(cock=c, block=block_drive(c), bend=0.0, trig=tg))
            for n in moving:
                for other_name, other in (("frame", frame), ("side plate", side_plate), ("right plate", side_plate_r), ("skin", skin), ("grip", grip),
                                          ("detent box", detent_box), ("guard", guard), ("spacer", sector_spacer),
                                          ("air lines", Part.makeCompound([supply_line, pilot_line, gauge_line, tee])),
                                          ("vent valve", valve_bodies), ("crest", crest)):
                    if n == "Bolt" and other_name == "detent box":
                        continue                     # it slides in it
                    v_ = hit(st[n], other)
                    worst[(n, other_name)] = max(worst.get((n, other_name), 0.0), v_)
    sup = top_strap.fuse(nose).fuse(washer)
    blk_hit = max(hit(turned(block, a_), sup) + hit(turned(Part.makeCompound(straps), a_), top_strap) for a_ in (0.0, 15.0, 30.0, 45.0))
    fixed_hits = {"air lines/valve": hit(Part.makeCompound([pilot_line, gauge_line, tee]), valve_body)
                  + hit(Part.makeCompound([pilot_line, gauge_line, tee]), valve_cap)
                  + hit(Part.makeCompound([pilot_line, gauge_line, tee, supply_line]), vent_body),   # (their ends sit in the fittings)
                  "air lines/springs+rib": hit(Part.makeCompound([pilot_line, gauge_line, tee]), mainsprings.fuse(spring_rib)),
                  "slider/stop at full cock": hit(slider_h(1.0)[0], slider_stop.translated(V(0, 0, -0.1))),
                  "side plate/valve": hit(side_plate, valve_body) + hit(side_plate, valve_cap) + hit(side_plate, lock_housing_h),
                  "bosses/valve": hit(bosses, valve_body) + hit(bosses, valve_cap),
                  "cheeks/valve": hit(cheeks, valve_body) + hit(cheeks, mini_valves),
                  "block/supports": blk_hit, "strap/vial": hit(top_strap, vial.fuse(cage)) + hit(top_strap, crest),
                  "valve/frame": valve_body.common(frame).Volume + valve_cap.common(frame).Volume,
                  "lock/frame": lock_housing_h.common(frame).Volume, "vent valve/frame": mini_valves.common(frame).Volume,
                  "springs/frame": hit(mainsprings, frame),   # the ball's taper is tighter than the old drum ever was
                  "plug/axle+nose+strap": hit(axle_plug, axle) + hit(axle_plug, nose) + hit(axle_plug, top_strap)}
    inside = mini_valves.common(grip.fuse(outer).fuse(_vv)).Volume / mini_valves.Volume
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
                  19.6 + (axle.BoundBox.XLength - 60) * math.pi / 4 * 23.8 ** 2 / 1000),
               "  axle plug: %d x %.1f O-ring, groove Ø%.1f (stretch %.1f %%, squeeze %.0f %%), flange Ø%.1f x %.0f on the tube's end"
               % (PLUG_ORING + (2 * _gr, plug_stretch * 100, PLUG_SQUEEZE * 100, BARREL_OD, PLUG_FLANGE))]
    print("\n".join(report))
else:
    report = [NAME, "  fast run: CHECKS off - geometry, document and weights only"]
    print("\n".join(report))

if CHECKS:
    # ---------------------------------------------------------------- checks: pass or fail, not only numbers
    checks = {}
    checks["frame is one sound solid (%.0f mm3, valid %s)" % (frame.Volume, frame.isValid())] = \
        frame.isValid() and len(frame.Solids) == 1 and frame.Volume > 80000   # both sides gave their bands to the plates
    checks["side plate is one sound solid (%.0f mm3, %d solids)" % (side_plate.Volume, len(side_plate.Solids))] = \
        side_plate.isValid() and len(side_plate.Solids) == 1 and side_plate.Volume > 15000
    checks["right plate is one sound solid (%.0f mm3, %d solids)" % (side_plate_r.Volume, len(side_plate_r.Solids))] = \
        side_plate_r.isValid() and len(side_plate_r.Solids) == 1 and side_plate_r.Volume > 15000
    checks["mechanism clears the dress over the hammer and trigger strokes"] = not [v_ for (n_, o_), v_ in worst.items()
                                                                                      if v_ > 0.05 and not (o_ == "spacer" and v_ < 5.0)]   # the spacer touches by design; OCCT's common of its 0.1-gap faces returns junk (the bbox falls outside both parts)
    for k_, v_ in fixed_hits.items():
        checks["fixed: %s (%.1f mm3)" % (k_, v_)] = v_ < (2.0 if k_.startswith("slider/stop") else 0.05)   # the stop pad is meant to touch
    # Sliding fits need air: a part cut to its neighbour's exact size will not go in once printed (the detent bolt did not).
    for label_, a_, b_ in (("detent bolt in its channel", turned(detent_bolt_print, DETENT_ANGLE + 90), detent_box), ("slider on the guide rod", rest["Slider"], guide_rod),
                           ("hammer on its axle", rest["Hammer"], shaft), ("sector on the chamber tube", rest["Sector"], axle),
                           ("block on the chamber tube", block, axle)):
        d_ = a_.distToShape(b_)[0]
        checks["clearance %s: %.2f mm (>= 0.10)" % (label_, d_)] = d_ >= 0.10
    # Retention: the valve stack (body, cap, lock housing) must not slide a couple of mm any way without meeting the cage, the
    # side plate, the strap, the chamber tube or the block. A direction with nothing to stop it is a part left to the glue.
    stack = Part.makeCompound([valve_body, valve_cap, lock_housing_h])
    around = Part.makeCompound([frame, side_plate, side_plate_r, top_strap, axle, nose, axle_plug, block])
    for label_, d_ in (("forward", V(2, 0, 0)), ("back", V(-2, 0, 0)), ("left", V(0, -2, 0)), ("right", V(0, 2, 0)),
                       ("up", V(0, 0, 2)), ("down", V(0, 0, -2))):
        v_ = hit(stack.translated(d_), around)
        checks["valve stack stopped when pushed 2 mm %s (%.0f mm3)" % (label_, v_)] = v_ > 0.5
    if not globals().get("NO_PAWL", False):          # the zigzag study has no pawl at all
        # The pawl (a flexure in the sector, or a plunger in its boss on a steel spring): one solid; no clash with the disc over the drive; the return needs at most the
        # tongue's travel (PAWL_BACK) of retraction at the tooth; and that travel, plus a margin, is free behind the tongue.
        checks["sector is one valid solid (%d solids)" % len(sector_base.Solids)] = len(sector_base.Solids) == 1 and sector_base.isValid()
        _sec_all = sector_base if FLEX_PAWL else sector_base.fuse(pawl_tooth)       # the plunger rides in the sector
        _w = max(hit(turned(_sec_all, sector_turn(i_ / 20)), turned(hub, block_drive(i_ / 20))) for i_ in range(21))
        if not FLEX_PAWL:
            _d = pawl_tooth.translated(V(-0.5, 0, 0)).distToShape(sector_base)[0]            # 0.5 mm off its stop: the radial play
            checks["pawl: plunger in its channel: %.2f mm of play (>= 0.10), spring %.1f long at rest, %.1f at full travel (solid %.1f)"
                   % (_d, PL_SPRING_L, PL_SPRING_L - PAWL_BACK, SPRING["solid"])] = _d >= 0.10 and PL_SPRING_L - PAWL_BACK >= SPRING["solid"] + 0.3
        checks["pawl: no clash with the disc over the drive (%.2f mm3)" % _w] = _w < 0.05
        def _need(a_, blk_):
            lo_, hi_ = 0.0, PAWL_BACK + 0.3
            if hit(turned(pawl_tooth.translated(V(-hi_, 0, 0)), a_), turned(hub, blk_)) > 0.05:
                return 9.9
            if hit(turned(pawl_tooth, a_), turned(hub, blk_)) <= 0.05:
                return 0.0
            for _ in range(12):
                m_ = (lo_ + hi_) / 2
                lo_, hi_ = (m_, hi_) if hit(turned(pawl_tooth.translated(V(-m_, 0, 0)), a_), turned(hub, blk_)) > 0.05 else (lo_, m_)
            return hi_
        if FLEX_PAWL or RAMP_IN_DISC or TOOTH_RAMP:
            _n = max(_need(-a_, 60.0) for a_ in range(0, 69, 4))
            checks["pawl: the return needs %.2f mm of retraction (tongue travel %.1f mm)" % (_n, PAWL_BACK)] = _n <= PAWL_BACK + 0.1
        else:
            print("  [n/a] pawl return: the disc's notches are square, the ramp is filed in by hand; the rigid tooth is a blank (%.1f wide, tip %.1f past the face)"
                  % (TOOTH_W, TIP_RISE))
        _back = PAWL_MOVER.translated(V(-(PAWL_BACK + 0.3), 0, 0))
        _bh = max(hit(turned(_back, sector_turn(c_ / 4)), o_) for c_ in range(5)
                  for o_ in (lock_housing_h, valve_body, valve_cap, frame, side_plate, slider_h(c_ / 4)[0], slider_h(c_ / 4)[1], axle))
        if FLEX_PAWL:
            _gap = PAWL_FLEX_FREE.distToShape(RING_POCKETED)[0]
            checks["pawl: the tongue is %.2f mm clear of the ring all round (>= 0.5, a narrower slit fuses shut in print)" % _gap] = _gap >= 0.5
        checks["pawl: room behind it for %.1f mm of travel (%.2f mm3 hit)" % (PAWL_BACK + 0.3, _bh)] = _bh < 0.05
    # The slider must wrap its guide rod, not lie in a groove on it: a ring 1 mm thick round the rod's hole must be solid.
    _ring = Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.15 + 1.0, 40, V(GUIDE_ROD["x"], GUIDE_ROD["y"], -40), ZA).cut(
        Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.15, 40, V(GUIDE_ROD["x"], GUIDE_ROD["y"], -40), ZA))
    _wrap = SLIDER_H.common(_ring).Volume / _ring.Volume
    checks["slider wraps its guide rod: %.0f %% of a 1 mm ring round the hole is solid (>= 98)" % (_wrap * 100)] = _wrap >= 0.98
    # The slider's steel pin must have a hole to sit in: drawn over solid plastic it only looked fixed.
    _sl0, _pin0 = slider_h(0.5)
    checks["slider pin sits in its hole (%.1f mm3 of it inside solid plastic)" % hit(_sl0, _pin0)] = hit(_sl0, _pin0) < 0.05
    for k_, ok_ in checks.items():
        print("  [%s] %s" % ("OK " if ok_ else "FAIL", k_))
    print("  valve stack rear face x %.1f, cage rear wall inside x %.1f (%.1f mm between)"
          % (stack.BoundBox.XMin, fx[0] + EVA_T + CAGE_T, stack.BoundBox.XMin - (fx[0] + EVA_T + CAGE_T)))

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
                     ("Vent_valve", mini_valves, (0.3, 0.3, 0.8), 0), ("Mainsprings", mainsprings, (0.6, 0.6, 0.65), 0),
                     ("Hammer_axle", shaft, (0.75, 0.75, 0.78), 0), ("Guide_rod", guide_rod, (0.75, 0.75, 0.78), 0),
                     ("Sector_spacer", sector_spacer, (0.8, 0.8, 0.82), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame", frame, IRON, 0), ("Frame_side", side_plate, (0.3, 0.29, 0.28), 0),
                      ("Frame_right", side_plate_r, (0.32, 0.31, 0.30), 0), ("Frame_skin", skin, IRON, 0), ("Trigger_guard", guard, IRON, 0),
                     ("Detent_housing", detent_box, IRON, 0), ("Grip_left", grip_left, WOOD, 0), ("Grip_right", grip_right, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
                     ("Pommel", pommel, IRON, 0), ("Pommel_claws", Part.makeCompound(claws), DIRTY, 0),
                     ("Warpstone_pommel", warp_pommel, WARP, 0), ("Hose", hose, (0.08, 0.08, 0.08), 0), ("Gauge_line", gauge_line, (0.15, 0.4, 0.8), 0),
                     ("Tee", tee, BRASS, 0),
                     ("Straps", Part.makeCompound(straps), IRON, 0), ("Strap_rivets", rivets(strap_rivets), DIRTY, 0),
                     ("Spikes", Part.makeCompound(spikes), DIRTY, 0), ("Plates", Part.makeCompound(plates), RUST, 0),
                     ("Plate_rivets", rivets(plate_rivets), DIRTY, 0), ("Crest", crest, DIRTY, 0),
                     ("Vial_glass", vial, GLASS, 65), ("Vial_caps", vial_caps, BRASS, 0), ("Vial_cage", cage, IRON, 0),
                     ("Warpstone_vial", vial_stone, WARP, 0), ("Gauge", gauge, BRASS, 0), ("Gauge_glass", gauge_glass, (0.9, 0.9, 0.85), 0),
                     ("Gauge_needle", needle, (0.6, 0.05, 0.05), 0), ("Pilot_pipe", pilot_pipe, (0.15, 0.4, 0.8), 0),
                     ("Axle_cap", axle_cap, IRON, 0), ("Axle_plug", axle_plug, (0.5, 0.5, 0.55), 0), ("Top_strap", top_strap, IRON, 0), ("Nose_sleeve", nose, IRON, 0),
                     ("Thrust_washer", washer, (0.85, 0.85, 0.8), 0)):
    add(g_dress, n, s_, c, tr)
doc.recompute()
_tick('doc built')

# ---------------------------------------------------------------- what is printed, cut from EVA, or bought
# Print only what carries load or moves; the look is EVA foam; tubes, springs, valves, fasteners are bought.
MATERIAL = {
    "print": ("Valve_body_v11", "Valve_cap_v11", "Lock_housing", "Block", "Sector", "Pawl", "Slider", "Bolt", "Hammer",
              "Sleeve", "Pusher", "Trigger", "Frame", "Frame_side", "Frame_right", "Detent_housing", "Grip_left", "Grip_right", "Trigger_guard",
              "Top_strap", "Axle_plug", "Sector_spacer",
              "Nose_sleeve"),
    "eva": ("Frame_skin", "Rags", "Pommel", "Pommel_claws", "Warpstone_pommel", "Straps", "Strap_rivets", "Spikes", "Plates",
            "Plate_rivets", "Crest", "Vial_caps", "Vial_cage", "Warpstone_vial"),
    "buy": ("Chamber_axle", "Vent_valve", "Pin", "Mainsprings", "Hammer_axle", "Guide_rod", "Hose", "Vial_glass", "Gauge", "Gauge_glass",
            "Gauge_needle", "Pilot_pipe", "Gauge_line", "Tee", "Axle_cap", "Thrust_washer"),
}
BUY_NOTE = {"Chamber_axle": "tube Ø25 x 0.6, %.0f mm (the chamber)" % axle.BoundBox.XLength, "Block": "+ 6 barrel tubes Ø25 x 0.6, %.0f mm" % BARREL_TUBE,
            "Vent_valve": "AirTAC M3R110-06 with its roller off (or M3PP110-06): G1/8 elbows for A (4 mm) and R (6 mm), a G1/8 silencer on P; drops into its socket in the rear column from the room (side plate off), stands on two feet - no fasteners", "Pin": "steel pin Ø3",
            "Mainsprings": "2 torsion springs, wire Ø1.6, OD 14, 6 coils", "Hose": "6/4 hose from the receiver, up the grip to the vent valve's R port",
            "Vial_glass": "a test tube Ø16", "Gauge": "a Ø25 0-4 bar gauge with a 4 mm push-in (it reads the chamber, through the pilot)",
            "Pilot_pipe": "PU tube 4/2.5: vent valve A -> cap G1/8 push-in, up the backstrap",
            "Gauge_line": "PU tube 4/2.5, tee to the gauge", "Tee": "push-in tee for 4 mm tube", "Axle_cap": "M6 x 25 stud (or a headless bolt) + cap nut; an M6 nut glued in the plug",
            "Axle_plug": "in the axle's front end on a 19 x 2.5 O-ring, its flange on the tube's end: it closes the chamber",
            "Top_strap": "2 x M3 x 40 + nuts down through its foot into the cage's top",
            "Thrust_washer": "nylon / PTFE washer 25 x 28 x 1",
            "Trigger_guard": "printed flat; ST2.9 x 13 through the floor into its front tab, rear end glued into the grip's wood",
            "Grip_left": "half: glued to the right on 2 x Ø3 x 12 dowels",
            "Grip_right": "half: 2 x ST2.9 x 13 down through the slab's floor into the wood",
            "Detent_housing": "with its bracket: 2 x M3 x 20 + nuts to the side plate's outer face",
            "Frame_side": "the whole side in one plate (the flank band and the slab's wall): 5 x ST2.9 x 16 into the flank's bosses",
            "Frame_right": "the right cover (the slab's wall, the cheek with the slider's tunnels, the flank band): on the Ø8 axle + 2 x M3 x 10 into the rear wall's strips",
            "Sector_spacer": "a full ring on the chamber tube with the sector's own sweep carved through (the pawl boss's road), from the sector's ring to the QEV body's face: fixes its seat; the length is the model's span - file to fit on a printed stack",
            "Hammer_axle": "steel rod Ø8 x 84 (or an M8 bolt's shank), pressed through both walls",
            "Guide_rod": "steel rod Ø3 x 96: the slider's guide, floor to the stop pad", "Trigger": "pivot: M3 x 16 screw + nylock nut"}
FILL = {"Valve_body_v11": 0.8, "Valve_cap_v11": 0.8}               # airtight; the rest ~45 % (walls + infill)
mat_of = {n: m for m, ns in MATERIAL.items() for n in ns}
lines, grams = [], 0.0
for o in doc.Objects:
    if o.TypeId != "Part::Feature":
        continue
    m = mat_of.get(o.Name, "?")
    o.addProperty("App::PropertyString", "Material", "Ratling", "print / eva / buy")
    o.Material = m
    if m == "print":
        vol = o.Shape.Volume - (barrels.Volume if o.Name == "Block" else 0.0)
        g_ = vol / 1000 * 1.24 * FILL.get(o.Name, 0.45)
        grams += g_
        lines.append("    print  %-16s %5.0f g%s" % (o.Name, g_, ("   " + BUY_NOTE[o.Name]) if o.Name in BUY_NOTE else ""))
lines += ["    buy    %-16s %s" % (n, BUY_NOTE.get(n, "")) for n in MATERIAL["buy"]]
lines.append("    eva    " + ", ".join(MATERIAL["eva"]))
unsorted = [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in mat_of]
# The tree by material: hide a group to see the rest (pistol/material_view.py colours by it)
for gname, label in (("Print", "Печать"), ("EVA", "EVA"), ("Buy", "Покупное")):
    g = doc.addObject("App::DocumentObjectGroup", gname)
    g.Label = label
    for o in [o for o in doc.Objects if o.TypeId == "Part::Feature" and getattr(o, "Material", "") == gname.lower()]:
        for parent in o.InList:
            if parent.TypeId == "App::DocumentObjectGroup":
                parent.removeObject(o)
        g.addObject(o)
for old in (g_mech, g_dress):
    if not old.Group:
        doc.removeObject(old.Name)
doc.recompute()
print("  parts by material (print at ~45 %% fill, valve 80 %%): ~%.0f g of filament%s\n%s"
      % (grams, ("; NOT SORTED: " + ", ".join(unsorted)) if unsorted else "", "\n".join(lines)))

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
