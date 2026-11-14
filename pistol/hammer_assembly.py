# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: the thumb-hammer mechanism inside the Skaven look.

pistol/hammer_layout.py's mechanism (v1.1 valve, lock pusher, block, pawl
sector, slider, detent, hammer, one-stage trigger) with 200 mm barrels,
dressed as archive/pistol_assembly.py (the lever variant):

    frame ..... the v12 silhouette: a drum O85 running straight to the
                block and closing in a ball tail over the hammer set (the
                cage's discs trim flush, the axle's ends read as rivets);
                a narrow slab under it carries the trigger, and its rear
                column holds the vent valve standing vertical in a socket
                (stage 2: the trigger's rear lug lifts its plunger); the
                QEV cap crosses the slab in its own window - cut to the
                stack's envelope +3.5 mm radially, the cap's rear +1.5 mm.
                Past the body's face only the M4 tips, Ø4.0, on toward the
                barrel. The tie rods' and lock bolts'
                pockets cast in;
                a right cheek shrouds the slider's bracket; the spur comes
                out of the ball's top through a slot over its swing; the
                frame splits at z = 8 into a lower and an upper half, and
                the four printed parts (the halves, the right plate, and the
                left flank band; the slab wall stays integral with the halves). The halves
                and the plates register on tongue/groove pairs, including one
                on the crown seam at x -32; the band takes the ball's
                semicircle above the slab
    grip ...... the rag-wrapped wooden grip, warpstone pommel with the
                hose; the halves bolt together (2 x M3 x 25 through, dowels locate)
                and the pair seats under the tray on a forward shoulder and four tongues

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
    CHECKS                                      # stays off until the owner asks for the check run.
except NameError:                               # Then set True before exec. Not at the end of a draft.
    CHECKS = False
HUB_T_HAMMER = 14.0                             # the block's rear disc (hammer_layout.py)
STUB = BARREL_TUBE - (HUB_T_HAMMER - 9.0)       # the tube from the rear disc's seat (9 deep) to the muzzle
HAMMER_RIGHT_FACE = 45.0                       # shared by the cover, printed journal and steel axle
exec(open(os.path.join(REPO, "pistol", "hammer_layout.py")).read())
_tick('layout built')

NAME = "pistol_hammer_assembly"
random.seed(7)

# ---------------------------------------------------------------- parameters
FRAME = dict(x=(HAMMER_PIVOT.x - HAMMER_R - 8.0, -1.0), y=(-45.0, 45.0), z=(-76.0, 31.0))   # the plan the v12 silhouette hangs on
DRUM_R, DRUM_X0 = 42.5, -65.5       # the v12 drum: O85 straight to the block, a ball tail to x -108
SLAB = dict(x=(-108.0, -1.0), y=23.0, z=(-70.0, -5.0))          # the narrow body under the drum
CHEEK = dict(x=(-96.0, -5.0), y=(23.0, HAMMER_RIGHT_FACE), z=(-70.0, 18.5))  # +2 mm outwards; outer flat face is the print bed face
EVA_T = 3.0                         # the frame's look: an EVA skin this thick over a printed cage
CAGE_T = 3.0
CAGE_WINDOWS = dict(side=((-40.0, -16.0), (-60.0, 12.0)), top=((-50.0, -18.0), 24.0), bottom=((-40.0, -10.0), 24.0))
try:
    STANDOFFS                       # set before exec (the zigzag study moves the left one off the push-rod's height)
except NameError:
    STANDOFFS = ((-48.0, -5.0, (-1,)),)   # x, z, sides: the side plate's peg to the QEV body's flank
                                           # (below z -34 the slab's own mass holds the body: no pegs there)
# The left flank band opens at the drum and ball; the slab wall belongs to the tray and lid.
# The mechanism remains accessible with the band, lid and right cover removed.
SIDE_BOSSES = ((-18.0, 30.0), (-66.0, 32.0))   # x, z: full-width bolt paths, clear of the moving parts
SHELL_BOLT_D = 3.4                 # M3 through-bolts, recessed heads and externally loaded captive nuts
BOSS_D, BOSS_L = 8.0, 10.0
TRIGGER_CHEEKS = dict(x=(-84.0, -76.0), y=(3.3, 7.0))          # the trigger's pivot (an M3 screw and nut) between them
TRIGGER_AXLE_D = 3.2                 # M3 stud through the lower frame and right cover, on the trigger's existing axis
# The grip registers under the slab. Its halves bolt together (GRIP_BOLTS), and a
# transverse M3 x 30 secures them to an internal saddle integral with the lower frame.
VALVE_BOX_Y = 33.0                  # the tang is a box under the frame round the vent valve and its fittings
GUARD_TAB = dict(x=(-58.0, -48.0), y=5.0, t=7.5)   # the guard's front tab, under the slab's floor
SPUR_SLOT = dict(a=(58.0, 240.0), r=SPUR[1] + 10.0, y=6.5)    # the lowered thumb handle's swing at the rear
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


# ---------------------------------------------------------------- the QEV socket: envelope + VALVE_SOCK
# The built valve is sealed over its seam and rod washers. The exact imprint would grow four pillars
# inside the rod holes (the imprint is the body/cap solids, whose own holes are already cut out of
# them), so the window is the stack's cross-section plus VALVE_SOCK all round. That 2 mm was the
# coat; the coat came out uneven and thicker, so the radial room is 3.5 mm. The cap's rear is
# open another 1.5 mm. The body's face stays the stop: past it the only holes are the rod tips.
# The lock housing's pocket stays the seat. The tie rods and the lock bolts carve their own pockets.
# The M4 tips stick 4.7 mm out of the body's face, past the nut. The hole there is the thread
# itself, Ø4.0, and runs on toward the barrel to x -10 so the tip does not bottom out.
VALVE_SOCK = 3.5
SOCK_AXIAL = 1.5
TIP_PAST_FACE = 4.7
TIP_POCKET_EXTRA = 13.0                         # tip at x -23.3, pocket ends at x -10.3
TIP_POCKET_D = 4.0
_B, _r2 = BODY_R + VALVE_SOCK, TUBE_OD / 2 + 1.5 + VALVE_SOCK
_phi = math.acos((_B - _r2) / chamber_x)     # the hull's tangent angle: the +VALVE_SOCK cancels in the numerator
_x_cap0 = X_BODY_TOP - BODY_H - CAP_T - SOCK_AXIAL
_x_body1 = X_BODY_TOP                              # the body's face stays the stop; no big mouth past it
sock_cap = cyl_x(2 * _B, _x_cap0, X_BODY_TOP - BODY_H, 0, Z_FIRE)
sock_body = (cyl_x(2 * _B, X_BODY_TOP - BODY_H, _x_body1, 0, Z_FIRE)
             .fuse(cyl_x(2 * _r2, X_BODY_TOP - BODY_H, _x_body1, 0, Z_FIRE + chamber_x))
             .fuse(prism_x([(-_B * math.sin(_phi), _B * math.cos(_phi) + Z_FIRE),
                            (-_r2 * math.sin(_phi), chamber_x + _r2 * math.cos(_phi) + Z_FIRE),
                            (_r2 * math.sin(_phi), chamber_x + _r2 * math.cos(_phi) + Z_FIRE),
                            (_B * math.sin(_phi), _B * math.cos(_phi) + Z_FIRE)],
                           X_BODY_TOP - BODY_H, _x_body1))
             .fuse(Part.makeCompound([cyl_x(TIP_POCKET_D, X_BODY_TOP,
                                           X_BODY_TOP + TIP_PAST_FACE + TIP_POCKET_EXTRA,
                                           -_p.y, Z_FIRE + _p.x) for _p in rod_pts])))


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
# Outboard of the room (y > 32) the bracket and the crank top out at z 14.5 at full cock: the tunnels stop
# at z 15.2, so the cheek keeps a 3.3 mm roof under its top (z 18.5) and the cover is closed - no hood.
# Inboard the slider's body rises to z 22.5, but that is the drum's room already.
TUNNEL_Z1 = 15.2
RIGHT_INNER_PLANE = 39.0            # one flat inner cheek wall; 6 mm to the outside face at y 45
outer = outer.cut(box(-64.0, CHEEK["x"][1], 22.4, RIGHT_INNER_PLANE, -65.1, TUNNEL_Z1))  # the slider's tunnel, body to bracket arm.
                                                                          # It stops on the cheek's front face (x -5): the
                                                                          # plate ends there, and the cut does not enter the drum.
# Mouth plug on the right cover: solid from the cheek front (x -5) out to
# SLAB x[1] (-1), up to SLAB z -5. The slider's face (x -5) keeps 0.4 mm of air
# in front of it. The pin and the sector's arm cross the plug (x -3.6..-0.4) on
# their way up: an arch round the axle, r 36.1,
# down to z -26.2 for the reinforced sector arm and recessed washer lane. The block hides it.
_LIP_X1 = SLAB["x"][1]                      # -1: flush with the tray's front face
_LIP_Z1 = SLAB["z"][1]                      # -5
_lip = box(CHEEK["x"][1] - 0.4, _LIP_X1, CHEEK["y"][0], CHEEK["y"][1], CHEEK["z"][0], _LIP_Z1)
_lip = _lip.cut(box(CHEEK["x"][1] - 0.5, CHEEK["x"][1] + 0.4, 22.4, 38.8, -65.1, _LIP_Z1 + 0.1))
_lip = _lip.cut(Part.makeCylinder(36.1, 6.0, V(CHEEK["x"][1] - 0.6, 0, 0), XA)
                .common(box(CHEEK["x"][1] - 0.6, _LIP_X1 + 0.5, 22.4, CHEEK["y"][1], -26.2, _LIP_Z1 + 0.1)))
outer = outer.fuse(_lip)
outer = outer.cut(box(-93.5, CHEEK["x"][1], 20.0, RIGHT_INNER_PLANE, -26.0, TUNNEL_Z1))  # one continuous flat pocket behind crank and slider
# Clearance behind the moving M3 x 6 cylindrical head, leaving 4.2 mm of the right outer wall.
outer = outer.cut(box(min(xs) - 4, max(xs) + 4, RIGHT_INNER_PLANE - 0.1,
                       DRIVE_CRANK_HEAD_Y + DRIVE_HEAD_H + 0.4,
                       H.z + slider_z(0) - 4, H.z + slider_z(1) + 4))
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
            s_ = Part.makeCylinder(5.0, abs(_b) - 13.5 + 1.0, V(x_, _b + sign * 1.0, z_), V(0, -sign, 0)).cut(sock_body)
            out.append(max(s_.Solids, key=lambda q: q.Volume))    # up to the socket's envelope: the sealed body bears on it
    return out


standoffs = Part.makeCompound(_standoffs(1) + _standoffs(-1))
if _standoffs(1):
    frame = frame.fuse(Part.makeCompound(_standoffs(1))).removeSplitter()  # the right ones, if any, stay on the frame
# (The old rear-stop pillar behind the valve cap is gone: the vent valve's socket pierces the floor
# right under it, so it never had a footing in any build - the cap is held by the block's straps fit.)
# The trigger's slot through the slab's mass: one opening from the rear lug (under the valve) to the
# blade's claw, through the floor into the open air below; the cheeks fuse in after, the hub rides between
t_slot = box(-95.2, -40.5, -4.8, 4.8, -81.0, -56.0)
frame, skin = frame.cut(t_slot), skin.cut(t_slot)
_tick('trigger slot cut')
# Slot in the top rear for the spur: a pie over its swing, round the pivot
H_ = HAMMER_PIVOT
pie = [V(H_.x, -SPUR_SLOT["y"], H_.z)] + [V(H_.x + SPUR_SLOT["r"] * math.cos(math.radians(q)), -SPUR_SLOT["y"],
                                            H_.z + SPUR_SLOT["r"] * math.sin(math.radians(q)))
                                          for q in [SPUR_SLOT["a"][0] + (SPUR_SLOT["a"][1] - SPUR_SLOT["a"][0]) * k / 12 for k in range(13)]]
spur_slot = Part.Face(Part.makePolygon(pie + [pie[0]])).extrude(V(0, 2 * SPUR_SLOT["y"], 0))
frame, skin = frame.cut(spur_slot), skin.cut(spur_slot)
pilot_hole = cyl_x(16, fx[0] - 9.0, DRUM_X0 - math.sqrt((DRUM_R - 3.0) ** 2 - Z_FIRE ** 2) + 2.5,
                   0, Z_FIRE)   # the cap's G1/8 fitting, through the tail's solid tip to the room's wall at the
                                 # pilot's line (the front end is bore-anchored, not fx[0]-anchored: fx[0] moved
                                 # with the hammer's pivot, the fitting did not)
frame, skin = frame.cut(pilot_hole), skin.cut(pilot_hole)

# ---------------------------------------------------------------- grip, trigger valves
a = math.radians(GRIP_ANGLE)
gd = V(-math.cos(a), 0, -math.sin(a))
gn = V(-math.sin(a), 0, math.cos(a))
_grip_sections = ((-0.20, GRIP_SECTIONS[0][1], GRIP_SECTIONS[0][2]),) + GRIP_SECTIONS
grip = Part.makeLoft([Part.Wire(Part.Ellipse(GRIP_START + gd * (GRIP_LEN * t) + gn * (h / 2),
                                             GRIP_START + gd * (GRIP_LEN * t) + YA * (w / 2),
                                             GRIP_START + gd * (GRIP_LEN * t)).toShape()) for t, h, w in _grip_sections],
                     True, False)
_grip_blank = grip.copy()                       # continuous loft, retained for the final mating cut
grip = grip.cut(outer)                          # the frame's foot covers its top
mini_valves = valves                            # hammer_layout's AirTAC vent valve
_a = AIRTAC
_vv = (box(VENT_X - _a["W"] / 2 - 0.5, VENT_X + _a["W"] / 2 + 0.5, VENT_Y0 - 0.5, VENT_Y0 + _a["T"] + 0.5,
           VENT_Z0, VENT_Z0 + _a["L"] + 0.5)                    # the valve's socket, its floor at the body's face
       .fuse(box(-95.2, -85.5, 2.5, 28.0, -81.0, VENT_Z0 + 0.5))   # through-bottom clearance for the rigid 8 mm trigger pad
       .fuse(valve_bodies))                     # the straight fittings and the silencer carve their own ways out
# The push-ins carry a brass hex, 12 across flats (13.9 over the corners), at the valve's face; A sticks
# out 20, R 22. Both pockets are plain round Ø14.6 bores (the hex's circumscribed circle + 0.35 a side)
# the whole way: A out to 2 mm past the tip, R all the way out through the right cover, so the hex
# passes and the collet can be reached. No step: the nut can be turned with a spanner at any depth.
FIT_HEX_AF = 12.0
_hex_r = FIT_HEX_AF / math.sqrt(3.0) + 0.35
_za, _zr = VENT_Z0 + _a["ports"]["A"], VENT_Z0 + _a["ports"]["R"]
fit_pockets = Part.makeCompound([
    Part.makeCylinder(_hex_r, _a["straight"]["A"][1] + 2.5, V(VENT_X, VENT_Y0 + 0.5, _za), V(0, -1, 0)),
    Part.makeCylinder(_hex_r, 30.0, V(VENT_X, VENT_Y0 + _a["T"] - 0.5, _zr), V(0, 1, 0))])
_vv = _vv.fuse(fit_pockets)
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
# Supply (6/4 hose from the receiver) in through the pommel, up the grip, out to the right and into
# the straight R1/8 on R along its axis. The silencer on P is the straight fitting above it. Pilot
# (4/2.5 PU) leaves the straight R1/8 on A to the left, straight out through the left wall in its own
# Ø5 hole (the push-in's tip is 10.5 mm short of the outer face: no room to bend inside), back round
# the tail and in through the Ø16 pilot hole in the rear to the cap's G1/8 push-in. No printed
# grooves in the shell: the tubes are soft and will not find a groove. The grip keeps the supply
# channel (the halves close on it). Rigid fittings still cut their own exits.
# The tee on the pilot, inside behind the cap, feeds the gauge, out past the drum's upper-left flank.
r_end, r_dir = vent_port("R")
a_end, a_dir = vent_port("A")
pilot_exit = Part.makeCylinder(2.5, 20.0, a_end - a_dir * 0.5, a_dir)   # y -12 .. -32: tray lid, wall, dress pad
frame = frame.cut(pilot_exit)
supply_pts = [c_end + gd * 70, c_end + gd * 15, GRIP_START + gd * (GRIP_LEN * 0.6), GRIP_START + gd * (GRIP_LEN * 0.3),
              V(-104, 8, -76), V(-108, 30, -72), V(r_end.x, r_end.y + 28, r_end.z - 18),
              r_end + r_dir * 16, r_end]
def _supply_pipe(r):
    # Keep the grip's groove straight; the external bend must not bow it off the seam.
    points = [supply_pts[0]] + supply_pts[3:]
    edges, last = [], points[0]
    for a, b, c in zip(points, points[1:], points[2:]):
        u, v = (b - a).normalize(), (c - b).normalize()
        angle = math.acos(max(-1.0, min(1.0, u.dot(v))))
        setback = min(10.0, (b - a).Length * 0.3, (c - b).Length * 0.3)
        radius = setback / math.tan(angle / 2)
        start, end = b - u * setback, b + v * setback
        center = start + (v - u * math.cos(angle)).normalize() * radius
        middle = center + (b - center).normalize() * radius
        edges.extend([Part.makeLine(last, start), Part.Arc(start, middle, end).toShape()])
        last = end
    edges.append(Part.makeLine(last, points[-1]))
    path = Part.Wire(edges)
    return path.makePipeShell([Part.Wire(Part.makeCircle(r, supply_pts[0], -gd))], True, False)


supply_line = _supply_pipe(3.0)
TEE = V(-86, 0, -27.3)                              # in the room: under the spring rib (z -23), beside the vent valve (y 7.5)
pilot_pts = [a_end, a_end + a_dir * 8.0, a_end + a_dir * 16.0, V(-93.5, -33.5, -38.5), V(-101, -36, -36),
             V(-110, -36, -32), V(-118, -25, -28.5), V(-113, -12, -27), V(-100, -12, -26.5),
             V(-92, -10, -26.5), TEE, V(-82, 0, Z_FIRE)]


def _pilot_pipe(radius):
    # Side bypass clears the lowered thumb handle; tangent arcs avoid spline loops at the tee.
    pts = []
    for p in pilot_pts:
        pts.append(p)
        while len(pts) >= 3:
            u, v = (pts[-2] - pts[-3]).normalize(), (pts[-1] - pts[-2]).normalize()
            if u.dot(v) > 1 - 1e-9:
                pts.pop(-2)
            else:
                break
    edges, last = [], pts[0]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        u, v = (b - a).normalize(), (c - b).normalize()
        angle = math.acos(max(-1.0, min(1.0, u.dot(v))))
        setback = min(10.0, (b - a).Length * 0.45, (c - b).Length * 0.45)
        bend_r = setback / math.tan(angle / 2)
        if bend_r <= radius:
            raise ValueError("pilot tube bend radius must exceed its section radius")
        start, end = b - u * setback, b + v * setback
        center = start + (v - u * math.cos(angle)).normalize() * bend_r
        middle = center + (b - center).normalize() * bend_r
        edges.extend([Part.makeLine(last, start), Part.Arc(start, middle, end).toShape()])
        last = end
    edges.append(Part.makeLine(last, pts[-1]))
    return Part.Wire(edges).makePipeShell([Part.Wire(Part.makeCircle(radius, pts[0], (pts[1] - pts[0]).normalize()))], True, False)


pilot_line = _pilot_pipe(2.0)
gauge_pts = [TEE, V(-82, -12, -28), V(-76, -20, -28), V(-75, -34, -20), V(-63, -38, -10), V(-52, -38, -2), V(-34, -36, 10), V(-30, -37, 15)]
gauge_line = pipe_along(gauge_pts, 2.0)
tee = Part.makeSphere(4.0, TEE)
hose = supply_line
air_cut = _supply_pipe(3.6).fuse(_pilot_pipe(2.6)).fuse(pipe_along(gauge_pts, 2.6)).fuse(Part.makeSphere(5.0, TEE))
pilot_return_port = box(HEEL_X - 3, HEEL_X + 13, -17, 0, Z_FIRE - 3.5, Z_FIRE + 3.5)
frame = frame.cut(pilot_return_port).removeSplitter()

# ---------------------------------------------------------------- trigger guard: a continuous flat ribbon
# Offset the centreline in its own plane, then extrude across y: no Frenet-frame flips or gaps.
GUARD = [V(-54, 0, -71), V(-51, 0, -77), V(-51, 0, -87), V(-57, 0, -97), V(-69, 0, -104),
         V(-81, 0, -103), V(-90, 0, -96), V(-96, 0, -88), V(-97, 0, -84)]
GUARD_SECTION = (5.0, 1.6)                      # 10 mm wide ribbon, 3.2 mm thick in the loop's plane
_gc = Part.BSplineCurve()
_gc.interpolate(GUARD)
_guard_inner, _guard_outer = [], []
for _i in range(121):
    _u = _gc.FirstParameter + (_gc.LastParameter - _gc.FirstParameter) * _i / 120.0
    _p = _gc.value(_u)
    _n = _gc.tangent(_u)[0].cross(YA).normalize()
    _guard_inner.append(_p + _n * GUARD_SECTION[1])
    _guard_outer.append(_p - _n * GUARD_SECTION[1])
_guard_ci, _guard_co = Part.BSplineCurve(), Part.BSplineCurve()
_guard_ci.interpolate(_guard_inner)
_guard_co.interpolate(list(reversed(_guard_outer)))
_guard_wire = Part.Wire([_guard_ci.toShape(), Part.makeLine(_guard_inner[-1], _guard_outer[-1]),
                         _guard_co.toShape(), Part.makeLine(_guard_outer[0], _guard_inner[0])])
guard = Part.Face(_guard_wire).extrude(YA * (2 * GUARD_SECTION[0]))
guard.translate(YA * -GUARD_SECTION[0])
guard = guard.cut(outer)                                 # the arms rise to the slab's floor, the rear runs into the grip
_gt = GUARD_TAB
GUARD_FRONT_X, GUARD_FRONT_YS = -53.0, (-16.0, 16.0)
GUARD_REAR_X, GUARD_REAR_Z = -97.0, -85.0
# A broad flange and two locating keys take bending; the screws only clamp the joint.
guard = guard.fuse(box(_gt["x"][0], _gt["x"][1], -20.5, 20.5, -77.5, -70))
for _gy in GUARD_FRONT_YS:
    guard = guard.fuse(box(-56, -50, _gy - 3, _gy + 3, -70.2, -67.5))
    guard = guard.cut(Part.makeCylinder(1.7, 20, V(GUARD_FRONT_X, _gy, -85), ZA))
    guard = guard.cut(Part.makeCylinder(3.2, 10.5, V(GUARD_FRONT_X, _gy, -85), ZA))
guard = guard.fuse(Part.makeCylinder(4, 10, V(GUARD_REAR_X, -5, GUARD_REAR_Z), YA))
_guard_rear_shaft = Part.makeCylinder(1.7, 60, V(GUARD_REAR_X, -30, GUARD_REAR_Z), YA)
guard = guard.cut(_guard_rear_shaft).removeSplitter()
_tick('chin + guard built')

# ---------------------------------------------------------------- detent housing
# The locating rail and outer mounting ear are integral with Frame_side_band.
def _detent_service_parts():
    core = turned(box(HUB_X0 + BOLT_X0 - 2, HUB_X0 + BOLT_X0 + BOLT[0] + 2, -BOLT[1] / 2 - 2, BOLT[1] / 2 + 2,
                      -HUB_R - 24, -HUB_R - 1.5), DETENT_ANGLE + 90)
    core = core.cut(Part.makeCompound([bolt_shape(0), bolt_shape(30)])).cut(detent_spring_pocket())
    db = core.BoundBox
    cx, cz = fx[1] - 5, db.ZMax - 5
    foot = box(fx[1] - 8, db.XMin + 0.9, -63.5, -44.5, db.ZMax - 10, db.ZMax)
    foot = foot.cut(cyl_x(2 * 47.6, HUB_X0, 50)).cut(core)
    housing = core.fuse(foot)
    mount = box(-12.5, -2, -48.5, -43.8, cz - 6, cz + 6).fuse(box(-12.5, -9, -63.5, -44.5, cz - 6, cz + 6))
    housing = housing.cut(box(-13, -1.8, -48.7, -44.3, cz - 6.2, cz + 6.2))
    # Keep this open root relief compatible with the previous removable housing.
    housing = housing.cut(box(cx - 3.2, cx + 3.2, -52, -44.3, db.ZMax - 5.7, db.ZMax + 2))
    outward = turned(Part.Vertex(V(0, 0, -1)), DETENT_ANGLE + 90).Vertexes[0].Point
    across = V(0, -outward.z, outward.y)

    def rail(x0, x1, d0, d1, half_w):
        c = V(x0, -52, cz - 2.4)
        points = [c + outward * d + across * t for d, t in ((d0, -half_w), (d1, -half_w), (d1, half_w), (d0, half_w))]
        return Part.Face(Part.makePolygon(points + [points[0]])).extrude(V(x1 - x0, 0, 0))

    mount = mount.fuse(rail(-9.2, -7.6, -2.5, 2.5, 1.0))
    housing = housing.cut(rail(-9.01, -7.4, -25, 2.7, 1.2))
    service_shaft = Part.makeCylinder(1.7, 40, V(-20, -58.5, cz), XA)
    housing = housing.cut(service_shaft).cut(_drive_hex_x(-58.5, cz, -2.5, 15, 5.9)).removeSplitter()
    mount = mount.cut(service_shaft).removeSplitter()
    service_bolt = Part.makeCylinder(1.5, 16, V(-12.5, -58.5, cz), XA).fuse(Part.makeCylinder(2.75, 3, V(-15.5, -58.5, cz), XA))
    service_nut = _drive_hex_x(-58.5, cz, -2.5, -0.1, 5.5).cut(service_shaft)
    return housing, mount, Part.makeCompound([service_bolt, service_nut]), outward, db, foot


detent_box, detent_mount, detent_service_fastener, DETENT_REMOVE_DIRECTION, _db, detent_bracket = _detent_service_parts()
_tick('detent built')

# ---------------------------------------------------------------- the cage: open on the left, a side plate on screws
def _boss_base(x_, z_):
    """The y of the room's wall at this boss: the drum's bore, or the ball's behind the drum."""
    return -(_room_wall(x_, z_) + 0.5)
bosses = Part.makeCompound([Part.makeCylinder(BOSS_D / 2, BOSS_L, V(x_, _boss_base(x_, z_), z_), YA) for x_, z_ in SIDE_BOSSES])
frame = frame.fuse(bosses).fuse(box(-60, fx[1], -44.5, -31, _db.ZMax - 10, _db.ZMax))   # solid seat for the integral left-shell detent mount
tc = TRIGGER_CHEEKS
_tick('bosses + detent pad fused')
cheek_top = TRIGGER_PIVOT.z + 3.5
cheeks = Part.makeCompound([box(tc["x"][0], tc["x"][1], sg * tc["y"][0] if sg > 0 else -tc["y"][1],
                                tc["y"][1] if sg > 0 else -tc["y"][0], fz[0] + EVA_T + CAGE_T - 0.5, cheek_top)
                            for sg in (1, -1)])
cheeks = cheeks.cut(Part.makeCylinder(TRIGGER_AXLE_D / 2, 2 * tc["y"][1] + 2, V(TRIGGER_PIVOT.x, -tc["y"][1] - 1, TRIGGER_PIVOT.z), YA))
# The taller pad root clears the rear inside corner; keep the axle's bearing area and outer cheek intact.
cheeks = cheeks.cut(box(TRIGGER_PIVOT.x - 4.3, TRIGGER_PIVOT.x - 1.5, 2.8, 4.4, TRIGGER_PIVOT.z - 7, TRIGGER_PIVOT.z + 3.7))
frame = frame.fuse(cheeks)
_tick('cheeks fused')
# The slider's top meets a stop on the drum's ceiling at full cock: the hammer's back stop. The stop
# grows up to the drum's wall (its top is clipped to r 40, 0.5 mm into the 3 mm shell) and hangs a
# nook print from it. The guide rod anchors at it: the rod runs to the stop pad, not to the old flat cage.
z_sl_top = slider_z(1.0) + 6.0
_stop_prism = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], z_sl_top + 0.05, 44.0)
slider_stop = _stop_prism.common(Part.makeCylinder(40.0, 96.0, V(-96, 0, 0), XA))   # keep the top 0.5 into the 3 mm shell
# The mainsprings' fixed legs rest on a rib off the cage's rear wall, below and behind the hammer's hub.
spring_rib = box(-92.0, -85.0, MAINSPRING["y"][0][0] - 1.0, -5.0,
                 HAMMER_PIVOT.z - 15.0, HAMMER_PIVOT.z - 10.5).cut(box(-93.0, -91.0, -20.5, -18.5, -24.0, -20.5))
# x fixed at the springs' rear legs: in the room's air (NOT pivot-following: 3 mm back with the pivot
# it ploughed into the tail's shell and the slab's rear); the inner-bottom-left corner is cut off:
# it clipped the ball's shell at (x -92, y -20, z -23)
rod_boss = Part.makeCylinder(4.0, 4.0, V(GUIDE_ROD["x"], GUIDE_ROD["y"], fz[0] + EVA_T + CAGE_T + 0.1), ZA)   # the guide rod's foot, inside the floor: the old -0.5 stuck a peg out of the underside
# The spring rib is NOT fused into the frame: its inner reach (y -23..-6) hangs in the room's air and
# would be a floating island once the side band is cut away - the side plate carries it as a cantilever.
frame = frame.fuse(slider_stop).fuse(rod_boss)
_tick('stop + rib + rod fused')
# One coaxial Ø3.3 passage through both ends of the shell; follow the current guide axis.
# Recut after the registration tongues and bolt supports so neither end can close again.
_guide_rod_hole = Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.15, 200.0,
                                   V(GUIDE_ROD["x"], GUIDE_ROD["y"], -100.0), ZA)
frame = frame.cut(_guide_rod_hole)
shaft_holes = Part.makeCylinder(4.0, 2 * fy[1], V(HAMMER_PIVOT.x, -fy[1], HAMMER_PIVOT.z), YA)   # the axle: a press fit
frame = frame.cut(shaft_holes)
_tick('shaft holes cut')
side_cut = box(HEEL_X - 1, fx[1] + 1, -fy[1] - 1, -(SLAB["y"] - 3.0), SLAB["z"][0] - 1, fz[1] + 1)   # the flank band plus the slab's left wall: the whole side opens
# Keep the slab's left wall integral with the tray and lid; only the flank band opens.
side_cut = side_cut.cut(box(HEEL_X - 2, fx[1] + 2, -SLAB["y"], 100, SLAB["z"][0] - 2, -5.0))
side_plate = frame.common(side_cut).fuse(Part.makeCompound(_standoffs(-1))).fuse(spring_rib)   # + the spring shelf
if len(side_plate.Solids) > 1:          # OCCT leaves face-sliver crumbs in the cuts' windows: keep the real body
    side_plate = Part.makeCompound([s_ for s_ in side_plate.Solids if s_.Volume > 50.0])
_tick('side plate common')
frame = frame.cut(side_cut)
if len(frame.Solids) > 1:            # OCCT sometimes leaves a face-sliver crumb beside the main body
    frame = max(frame.Solids, key=lambda q: q.Volume)
# The right cover carries the slab wall, cheek and flank band as one part.
# Its rear lower fastening shares the full-width M3 through-bolt at COVER_SCREW.
COVER_SCREW = (-103.5, -65.5)
side_cut_r = box(HEEL_X - 1, _LIP_X1 + 0.1, SLAB["y"] - 3.0, fy[1] + 3.0, SLAB["z"][0] - 1, fz[1] + 1)  # includes the outer mouth lip
side_plate_r = (frame.common(side_cut_r).cut(sock_cap).cut(sock_body).cut(lock_housing_h)
                .cut(valve_rods_cut).cut(lock_bolts_cut)
                .cut(Part.makeCylinder(1.7, 4.0, V(COVER_SCREW[0], 23.5, COVER_SCREW[1]), V(0, -1, 0))))
if len(side_plate_r.Solids) > 1:
    side_plate_r = Part.makeCompound([s_ for s_ in side_plate_r.Solids if s_.Volume > 50.0])
# The printed sleeve enters a running-fit journal seat; leave the outer Ø8 axle-bearing land intact.
_journal_y0 = CRANK_Y[1] - 0.1
_hammer_journal_seat = Part.makeCylinder(SLEEVE_R + HAMMER_BEARING_CLEAR,
                                         HAMMER_RIGHT_FACE - HAMMER_BEARING_WALL - _journal_y0,
                                         V(HAMMER_PIVOT.x, _journal_y0, HAMMER_PIVOT.z), YA)
side_plate_r = side_plate_r.cut(_hammer_journal_seat).removeSplitter()
frame = frame.cut(side_cut_r)
frame = frame.cut(Part.makeCylinder(SHELL_BOLT_D / 2, 120.0, V(COVER_SCREW[0], -60.0, COVER_SCREW[1]), YA))
if len(frame.Solids) > 1:
    frame = max(frame.Solids, key=lambda q: q.Volume)
_tick('side cut done')
pilots = Part.makeCompound([Part.makeCylinder(SHELL_BOLT_D / 2, 120.0, V(x_, -60.0, z_), YA) for x_, z_ in SIDE_BOSSES])
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
# bottom in a pocket, and through the slab it cuts its own window - cut to the stack's envelope +
# VALVE_SOCK (a 10 mm bridge under it ties the front and rear together with the drum above). The lock
# seats in the slab's front, flush with its sides; the tie rods and the lock bolts carve their pockets.
frame = frame.cut(sock_cap).cut(sock_body).cut(lock_housing_h).cut(valve_rods_cut).cut(lock_bolts_cut)
_sp_cut = [Part.makeCylinder(1.7, 10, V(x_, -fy[1] - 1, z_), YA) for x_, z_ in SIDE_BOSSES]
_sp_cut += [Part.makeCylinder(1.7, 16, V(x_, -fy[1] - 16, z_), YA) for x_, z_ in SIDE_BOSSES]   # out through any slag past the plate
side_plate = side_plate.cut(sock_cap).cut(sock_body).cut(lock_housing_h).cut(valve_rods_cut).cut(lock_bolts_cut).cut(
    Part.makeCompound(_sp_cut))   # the flank band covers the QEV stack's rim: cut the socket's imprint too (no splitter: it splits the plate)
if len(side_plate.Solids) > 1:            # and the crumbs it used to leave: keep the real body
    side_plate = Part.makeCompound([s_ for s_ in side_plate.Solids if s_.Volume > 50.0])
_tick('side plate cut')
skin = skin.cut(shaft_holes).cut(detent_box)

# ---------------------------------------------------------------- the guard's tab
# The vent valve needs no fasteners: it drops into its socket from the room
# (side plate off) and stands on the two feet. The guard's front tab takes one ST2.9 down through the
# floor; its rear end glues into the grip's wood.
floor_holes = Part.makeCompound([Part.makeCylinder(1.7, 12.0, V(GUARD_FRONT_X, y_, -71), ZA) for y_ in GUARD_FRONT_YS])
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
    return seg.cut(sock_cap).cut(sock_body)
plates.append(_flank_shell(-59.0, -48.0, -1))
plates.append(_flank_shell(-59.0, -5.0, +1))
# The slab's sides and the cheek's outer face: flat riveted armor; the left side's dress all rides
# on the removable side plate (glued), with a window over the spring shelf's notch.
plates.append(box(SLAB["x"][0], SLAB["x"][1], SLAB["y"], SLAB["y"] + 3.0, SLAB["z"][0], SLAB["z"][1])
              .cut(_vv).cut(sock_cap).cut(sock_body).cut(valve_rods_cut))
plates.append(box(SLAB["x"][0], SLAB["x"][1], -SLAB["y"] - 3.0, -SLAB["y"], SLAB["z"][0], SLAB["z"][1])
              .cut(sock_cap).cut(sock_body).cut(valve_rods_cut).cut(box(-99.0, -87.0, -33.0, -25.5, -27.0, -15.0)).cut(pilot_exit))
plates.append(box(-90.0, -8.0, CHEEK["y"][1], CHEEK["y"][1] + 3.0, -60.0, 12.0).cut(fit_pockets))
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

grip = grip.cut(air_cut)            # the shell is not grooved: a soft tube will not sit in a printed channel
# The rear right 3 mm tongue clears the supply hose; two front shoulder tongues follow below.
# The former rear left tongue is replaced by the frame's internal saddle and transverse bolt.
GRIP_TONGUES = ((-98.0, 12.0, 3.0),)    # x, y on the floor's underside, width
for _x, _y, _w in GRIP_TONGUES:
    grip = grip.fuse(box(_x - _w / 2, _x + _w / 2, _y - _w / 2, _y + _w / 2, -73.0, -67.0))
    frame = frame.cut(box(_x - _w / 2 - 0.2, _x + _w / 2 + 0.2, _y - _w / 2 - 0.2, _y + _w / 2 + 0.2, -70.3, -66.8))
if len(frame.Solids) > 1:            # crumbs from the earlier cuts: keep only the body
    frame = max(frame.Solids, key=lambda q: q.Volume)
grip = max(grip.Solids, key=lambda q: q.Volume) if len(grip.Solids) > 1 else grip
# The grip prints as two halves split on y = 0, each flat on its cut face: the hose lies in the open channel.
# Two Ø3 dowels (6 mm into each half) locate the halves and slide out along y. Two M3 x 25 clamp
# them straight through: head in a seat on the right outer face, nut in a pocket on the left outer
# face. The bolts sit off the hose, which runs on the grip's axis, on the palm side of the section.
GRIP_DOWELS = [GRIP_START + gd * (GRIP_LEN * t) + gn * 13.0 for t in (0.3, 0.75)]
dowels = Part.makeCompound([Part.makeCylinder(1.6, 12.0, V(p_.x, -6.0, p_.z), YA) for p_ in GRIP_DOWELS])
grip = grip.cut(dowels)
_tick('grip split')
grip_left = grip.common(box(-400, 100, -100, 0, -400, 100)).removeSplitter()
grip_right = grip.common(box(-400, 100, 0, 100, -400, 100)).removeSplitter()
for _g in (grip_left, grip_right):
    if not _g.isValid():
        _g.fix(0.01, 0.001, 0.1)                 # the split leaves a sliver edge on the loft: heal it
# (x, z) on the grip. Ø3.4 runs through both halves. The head seat (Ø6.2, floor y 10.6) opens
# the right face, about y 14. The nut pocket (2.7 mm, AF 5.7) opens the left face, about y -14.
# M3 x 25: the tip ends in that pocket, about flush with the left skin.
GRIP_BOLTS = tuple(GRIP_START + gd * (GRIP_LEN * _t) + gn * -10.0 for _t in (0.42, 0.70))


def _grip_hex(x_, z_, y0, y1, af):
    r_ = af / math.sqrt(3.0)
    pts = [V(x_ + r_ * math.cos(math.radians(30 + 60 * k)), y0, z_ + r_ * math.sin(math.radians(30 + 60 * k)))
           for k in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, y1 - y0, 0))


for _p in GRIP_BOLTS:
    _bore = Part.makeCylinder(1.7, 33.0, V(_p.x, -16.5, _p.z), YA)
    grip_left = grip_left.cut(_bore)
    grip_right = grip_right.cut(_bore)
    grip_right = grip_right.cut(Part.makeCylinder(3.1, 4.2, V(_p.x, 10.6, _p.z), YA))
    grip_left = grip_left.cut(_grip_hex(_p.x, _p.z, -16.2, -11.0, 5.7))
grip_left = max(grip_left.Solids, key=lambda q: q.Volume)
grip_right = max(grip_right.Solids, key=lambda q: q.Volume)

# ---------------------------------------------------------------- the frame in two halves, tongue/groove joints
# The frame splits at z = SPLIT_Z into a bottom tray and a top cover, stepped at the front: the front
# slab's wall (x >= -28) belongs to the tray entirely, else its band above the tray would hang in the
# room's air, detached from the drum's arch. The QEV, the vent and the lock drop into the tray from
# above (its floor keeps the front and back joined under the QEV window). Small tongue/groove pairs at
# the joints so the printed parts self-register before bolting: the tongues on the tray's top face and on
# the plates' inner faces (they print up, clean), the grooves on the mating parts, TG_CLEAR a side.
# The plates' grooves are cut before the split, the halves' joints after it.
SPLIT_Z = -45.0
TG_W, TG_H, TG_CLEAR = 3.0, 3.0, 0.20


def tg_box(x_, y_, z_, wx, wy, h_):
    return box(x_ - wx / 2, x_ + wx / 2, y_ - wy / 2, y_ + wy / 2, z_, z_ + h_)


# x, z on the frame's side faces (y = +-20): on the slab's wall, clear of the QEV window, the vent's
# socket, the lock's pocket and the trigger's slot. The right side differs: the vent's socket owns
# (x -90, z -25) there, so the rear pair moves to (-75, -35).
# x, z, width, depth. Each tongue is as big as its seat allows: the groove keeps the wall it had at 3 x 3
# (1 mm round it). The floor pairs (z -62) sit in solid slab and take 6 x 4; the rear pairs beside the
# vent's socket and the QEV window stay 3 x 3.
PLATE_JOINTS = dict(right=((-75.0, -35.0, 3.0, 3.0), (-60.0, -62.0, 6.0, 4.0), (-15.0, -62.0, 6.0, 4.0)))
for x_, z_, w_, h_ in PLATE_JOINTS["right"]:
    side_plate_r = side_plate_r.fuse(box(x_ - w_ / 2, x_ + w_ / 2, 20.0 - h_, 20.0, z_ - w_ / 2, z_ + w_ / 2))
    frame = frame.cut(box(x_ - w_ / 2 - TG_CLEAR, x_ + w_ / 2 + TG_CLEAR,
                          20.0 - h_ - 0.3, 20.0 + 0.1, z_ - w_ / 2 - TG_CLEAR, z_ + w_ / 2 + TG_CLEAR))

# The left slab wall belongs to the frame halves; the removable side is the flank band.
side_band = side_plate


def _biggest(sh, vmin=40.0):
    bits = [s for s in sh.Solids if s.Volume > vmin]
    if len(bits) == 1:
        return bits[0]
    return Part.makeCompound(bits) if bits else sh


def _cut(shape, tool):
    """A cut that survives OCCT 1.1 (the Mac bundle): a cut across faces left split by
    earlier booleans returns a null shape there. The plain cut runs first, so FreeCAD
    1.0.2 (the cloud) keeps its exact path; only a null result retries over
    removeSplitter, which merges those faces and cuts the same volume."""
    try:
        r = shape.cut(tool)
        if not r.isNull():
            return r
    except Exception:
        pass
    r = shape.removeSplitter().cut(tool)
    if r.isNull():
        raise ValueError("cut failed even through removeSplitter")
    return r


side_band = _biggest(side_band)
side_plate = side_band                                      # the removable left side
_tick('side band ready')

frame_lower = frame.common(box(-400, 100, -100, 100, -400, SPLIT_Z))
frame_upper = frame.common(box(-400, 100, -100, 100, SPLIT_Z, 400))
# The split's pairs on the slab's top face at z = SPLIT_Z: the rear column (behind the QEV window and
# the vent's socket) and the centre. No front pairs: the front slab's wall is the tray's, and the
# tongues there would rise into the lock housing's rear-bottom corner.
# The centre pair used to sit at (-90, 0) and (-90, 5), under the valve. They sit at y -12, clear of
# the straight fitting on A (it leaves the left face along -y).
# The three remaining tongues stand 5 tall; the pair at y -12 is 4 wide, the right tongue is 3.
# The former left-front peg at (-82, -17.2) is replaced by a stronger annular locating shoulder
# around the independent frame assembly screw; its old place was too close to the new screw support.
# The rear one at y -12 moved from x -100 to -103.5: the full-length round pocket cut its seat.
SPLIT_JOINTS = ((-103.5, -12.0, 4.0), (-80.0, -12.0, 4.0), (-75.0, 12.0, 3.0))   # the former left-front peg is replaced by the assembly screw's locating shoulder
SPLIT_TG_H = 5.0
for x_, y_, w_ in SPLIT_JOINTS:
    frame_lower = frame_lower.fuse(tg_box(x_, y_, SPLIT_Z, w_, w_, SPLIT_TG_H))
    frame_upper = frame_upper.cut(tg_box(x_, y_, SPLIT_Z - 0.1, w_ + 2 * TG_CLEAR, w_ + 2 * TG_CLEAR, SPLIT_TG_H + 0.4))
frame_upper = frame_upper.cut(box(-28.0, 100, -100, 100, SPLIT_Z, -5.0))
# The side assemblies come off. The left slab wall stays integral with the frame;
# the right cover is already one piece. Both bolt to the centre, they are not glued
# to it. The tongues stay as locators, 0.2 mm a side, and slide off along y.
# One tongue a side on the ball's rear shell (x -100, z 12), and one more forward
# on the crown's seam (x -32, z 29..32), where the lid sits on the sides. The left
# lid already has a wall beside the band there. The right shell sits further out,
# so a pad hangs off the lid's shoulder and the tongue enters that. Both slide off
# along y, 0.2 mm clear, same as the rear pair.
for _side, _x, _z in (("left", -100.0, 12.0), ("right", -100.0, 12.0)):
    if _side == "left":
        side_band = side_band.fuse(box(_x - TG_W / 2, _x + TG_W / 2, -20.0, -17.0, _z - TG_W / 2, _z + TG_W / 2))
        frame_upper = _cut(frame_upper, box(_x - TG_W / 2 - TG_CLEAR, _x + TG_W / 2 + TG_CLEAR,
                                            -20.1, -20.0 + TG_H + 0.3, _z - TG_W / 2 - TG_CLEAR, _z + TG_W / 2 + TG_CLEAR))
    else:
        side_plate_r = side_plate_r.fuse(box(_x - TG_W / 2, _x + TG_W / 2, 17.0, 20.0, _z - TG_W / 2, _z + TG_W / 2))
        frame_upper = _cut(frame_upper, box(_x - TG_W / 2 - TG_CLEAR, _x + TG_W / 2 + TG_CLEAR,
                                            20.0 - TG_H - 0.3, 20.1, _z - TG_W / 2 - TG_CLEAR, _z + TG_W / 2 + TG_CLEAR))
# The crown tongues are 5 long along the seam (the shell runs on in x); their height stays 2.6, the shell's.
_CX, _CW = -32.0, 5.0
frame_upper = frame_upper.fuse(box(_CX - _CW / 2 - 1.7, _CX + _CW / 2 + 1.7, 19.2, 23.2, 28.6, 34.8))
side_plate_r = side_plate_r.fuse(box(_CX - _CW / 2, _CX + _CW / 2, 20.2, 27.0, 29.4, 32.0))
frame_upper = _cut(frame_upper, box(_CX - _CW / 2 - 0.2, _CX + _CW / 2 + 0.2, 20.0, 23.6, 29.2, 32.05))
side_band = side_band.fuse(box(_CX - _CW / 2, _CX + _CW / 2, -28.0, -17.4, 29.4, 32.0))   # root reaches the native curved wall independently of bolt bosses
frame_upper = _cut(frame_upper, box(_CX - _CW / 2 - 0.2, _CX + _CW / 2 + 0.2, -20.05, -17.2, 29.2, 32.05))
# Recessed through-fasteners: x, z, head bearing y, nut bearing y, bolt length, access radius, boss radius.
# M3 nuts load from outside and seat in a shallow anti-rotation hex at the bottom of each round well.
SHELL_BOLT_SEATS = tuple((x_, z_, -22.0, 22.0, 50.0, 4.1, 5.5) for x_, z_ in SIDE_BOSSES) + (
    (-76.0, -58.0, -8.0, 39.0, 50.0, 4.1, 5.5),
    (-20.0, -62.0, -8.0, 39.0, 50.0, 4.1, 5.5),
    (COVER_SCREW[0], COVER_SCREW[1], -17.0, 19.0, 40.0, 3.7, 4.8))
SHELL_BOLTS = tuple((x_, z_) for x_, z_, *_ in SHELL_BOLT_SEATS)
SHELL_SEAT_FLOOR, SHELL_NUT_AF, SHELL_NUT_DEPTH = 3.0, 5.9, 2.8
_shell_hull = _drum.fuse(_ball).fuse(_slab).fuse(_cheek).fuse(_lip)
_shell_hull = _shell_hull.cut(_vv).cut(sock_cap).cut(sock_body).cut(lock_housing_h).cut(valve_rods_cut).cut(lock_bolts_cut)
_shell_hull = _shell_hull.cut(air_cut)   # inward sleeves must leave the existing hose route open
_shell_shafts, _shell_wells, _shell_receivers, _shell_cutters = [], [], [], []
for _i, (_x, _z, _hy, _ny, _length, _access_r, _boss_r) in enumerate(SHELL_BOLT_SEATS):
    # Upper fasteners need inward tubes: a recess alone would remove their thin curved shell.
    if _i < len(SIDE_BOSSES):
        _left_boss = Part.makeCylinder(_boss_r, 60 + _hy + SHELL_SEAT_FLOOR, V(_x, -60, _z), YA).common(_shell_hull)
        side_band = side_band.removeSplitter().fuse(_left_boss).removeSplitter()
        _shell_receivers.append(Part.makeCylinder(_boss_r + 0.2, 60 + _hy + SHELL_SEAT_FLOOR + 0.2, V(_x, -60, _z), YA))
    _right_boss = Part.makeCylinder(_boss_r, 60 - (_ny - SHELL_SEAT_FLOOR), V(_x, _ny - SHELL_SEAT_FLOOR, _z), YA).common(_shell_hull)
    side_plate_r = side_plate_r.removeSplitter().fuse(_right_boss).removeSplitter()
    _shell_receivers.append(Part.makeCylinder(_boss_r + 0.2, 60 - (_ny - SHELL_SEAT_FLOOR - 0.2), V(_x, _ny - SHELL_SEAT_FLOOR - 0.2, _z), YA))
    _shell_shafts.append(Part.makeCylinder(SHELL_BOLT_D / 2, 120.0, V(_x, -60, _z), YA))
    _shell_wells.append(Part.makeCylinder(_access_r, 60 + _hy, V(_x, -60, _z), YA))
    _hex_r = SHELL_NUT_AF / math.sqrt(3.0)
    _hex_pts = [V(_x + _hex_r * math.cos(math.radians(30 + 60 * k)), _ny,
                  _z + _hex_r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    _shell_wells.append(Part.Face(Part.makePolygon(_hex_pts + [_hex_pts[0]])).extrude(YA * SHELL_NUT_DEPTH))
    _shell_wells.append(Part.makeCylinder(_access_r, 60 - _ny - SHELL_NUT_DEPTH, V(_x, _ny + SHELL_NUT_DEPTH, _z), YA))
    _bolt_cutter = _shell_shafts[-1]
    for _well in _shell_wells[-3:]:
        _bolt_cutter = _bolt_cutter.fuse(_well)
    _shell_cutters.append(_bolt_cutter.removeSplitter())
_shell_bolt_holes = Part.makeCompound(_shell_shafts)
_shell_access_cuts = Part.makeCompound(_shell_cutters)   # overlapping shaft/well tools must be fused first
_shell_receiver_cuts = Part.makeCompound(_shell_receivers)


def _shell_cut_tools(shape_, tools_):
    for tool_ in tools_:
        a_, b_ = shape_.BoundBox, tool_.BoundBox
        if a_.XMax < b_.XMin or a_.XMin > b_.XMax or a_.YMax < b_.YMin or a_.YMin > b_.YMax or a_.ZMax < b_.ZMin or a_.ZMin > b_.ZMax:
            continue
        shape_ = _cut(shape_.removeSplitter(), tool_).removeSplitter()
    return shape_


frame_lower = _shell_cut_tools(frame_lower, _shell_receivers + _shell_cutters)
frame_upper = _shell_cut_tools(frame_upper, _shell_receivers + _shell_cutters)
side_band = _shell_cut_tools(side_band, _shell_cutters)
side_plate_r = _shell_cut_tools(side_plate_r, _shell_cutters).cut(air_cut).removeSplitter()
# Preserve outside access through the EVA dress too.
_shell_tool_holes = Part.makeCompound([Part.makeCylinder(4.1, 120.0, V(x_, -60.0, z_), YA)
                                        for x_, z_ in SHELL_BOLTS])
plates = [p_.cut(_shell_tool_holes) for p_ in plates]
side_band = _biggest(side_band)
side_plate_r = _biggest(side_plate_r)
# Round only the tray's left underside toward the bail; keep the right-cover wall straight.
TRAY_BOTTOM_Y = GUARD_TAB["y"]
TRAY_GRIP_Y = max(w for _, _, w in GRIP_SECTIONS) / 2 + 0.5


def _tray_profile(x_, w_):
    p_ = lambda y_, z_: V(x_, y_, z_)
    z_ = SLAB["z"][0] + 0.5
    l_ = Part.BezierCurve()
    l_.setPoles([p_(-w_, z_), p_(-SLAB["y"], z_), p_(-SLAB["y"], SPLIT_Z)])
    return Part.Wire([Part.makeLine(p_(-SLAB["y"], SPLIT_Z), p_(SLAB["y"], SPLIT_Z)),
                      Part.makeLine(p_(SLAB["y"], SPLIT_Z), p_(SLAB["y"], z_ - 2)),
                      Part.makeLine(p_(SLAB["y"], z_ - 2), p_(-w_, z_ - 2)),
                      Part.makeLine(p_(-w_, z_ - 2), p_(-w_, z_)), l_.toShape()])


_tx0, _tx1 = -104.0, -76.0
_sections = [_tray_profile(SLAB["x"][0] - 1, TRAY_GRIP_Y)]
for _i in range(15):
    _u = _i / 14.0
    _w = TRAY_GRIP_Y + (TRAY_BOTTOM_Y - TRAY_GRIP_Y) * _u * _u * (3 - 2 * _u)
    _sections.append(_tray_profile(_tx0 + (_tx1 - _tx0) * _u, _w))
_tray_envelope = Part.makeLoft(_sections, True, True)
_tray_envelope = _tray_envelope.fuse(Part.Face(_tray_profile(_tx1, TRAY_BOTTOM_Y)).extrude(V(SLAB["x"][1] - _tx1 + 1, 0, 0)))
_tray_envelope = _tray_envelope.fuse(box(-400, 100, -100, 100, SPLIT_Z - 0.01, 400))
frame_lower = frame_lower.common(_tray_envelope).removeSplitter()
# Continue the existing trigger pivot bore through the case for insertion of the stud.
_trigger_axle_hole = Part.makeCylinder(TRIGGER_AXLE_D / 2, 2 * (CHEEK["y"][1] + 1),
                                    V(TRIGGER_PIVOT.x, -CHEEK["y"][1] - 1, TRIGGER_PIVOT.z), YA)
frame_lower = frame_lower.cut(_trigger_axle_hole).removeSplitter()
side_plate_r = side_plate_r.cut(_trigger_axle_hole).removeSplitter()
frame_lower = frame_lower.cut(_guide_rod_hole).removeSplitter()
frame_upper = frame_upper.cut(_guide_rod_hole).removeSplitter()
side_plate_r = side_plate_r.cut(_guide_rod_hole).removeSplitter()
frame_lower = _biggest(frame_lower, vmin=1000.0)
frame_upper = _biggest(frame_upper, vmin=1000.0)
# The band's inboard supports keep their seats in the now integral left wall.
frame_upper = frame_upper.cut(side_band).removeSplitter()
# The guide belongs to the fixed core: the right cover must slide off along y without it.
_gx, _gy = GUIDE_ROD["x"], GUIDE_ROD["y"]
_guide_foot = box(_gx - 4, _gx + 4, 17, _gy + 4, -69.9, -65.9).cut(_guide_rod_hole)
frame_lower = frame_lower.fuse(_guide_foot).removeSplitter()
_guide_roof = Part.makeCylinder(41.5, 12, V(-15, 0, 0), XA)
_guide_upper = slider_stop.fuse(box(-13.7, -5, 16, 32, 30, 40).common(_guide_roof))
_guide_upper = _guide_upper.fuse(Part.makeCylinder(4, 18, V(_gx, _gy, z_sl_top + 0.05), ZA).common(_guide_roof))
_guide_upper = _guide_upper.cut(_guide_rod_hole).removeSplitter()
frame_upper = frame_upper.fuse(_guide_upper).removeSplitter()
_foot_clear = box(_gx - 4.2, _gx + 4.2, 15.8, _gy + 4.2, -70.1, -65.7)
_stop_clear = box(-13.9, -4.8, 15.8, 32.8, z_sl_top - 0.15, 40.2).common(
    Part.makeCylinder(41.7, 12, V(-15, 0, 0), XA))
_rod_release = box(_gx - 1.85, _gx + 1.85, 15.8, _gy + 1.85, GUIDE_ROD["z"][0] - 0.2, GUIDE_ROD["z"][1] + 0.2)
_cz0, _cz1 = sorted((slider_z(0), slider_z(1)))
_slider_entry = box(_gx - 3.5, SLIDER_X[1] + 0.3, 15.8, SLIDER_Y[0] - 0.4,
                       _cz0 - SLIDER_REACH - 0.3, _cz1 + 6.3)
_cc = SLIDER_CAP_CENTRE
_cap_head_clear = box(_cc.x - 3.1, _cc.x + 3.1, _cc.y - 0.1, _cc.y + 3.4, _cz0 + _cc.z - 3.1, _cz1 + _cc.z + 3.1)
side_plate_r = side_plate_r.cut(_foot_clear).cut(_stop_clear).cut(_rod_release).cut(_slider_entry).cut(_cap_head_clear).removeSplitter()
# Remove a zero-thickness pinch where the guide pocket meets its neighbouring curved face.
# Without a real gap its STL has four triangles sharing one edge despite Shape.isValid().
_guide_pinch_relief = box(-14.2, -13.8, 24.6, 29.2, 29.6, 30.4)
side_plate_r = side_plate_r.cut(_guide_pinch_relief).removeSplitter()
# Keep the button valve from rising with the trigger before its spool has moved.
_vent_top = VENT_Z0 + AIRTAC["L"]
vent_top_keeper = box(HEEL_X + 0.5, VENT_X - 5.5, 8, 14, _vent_top + 0.2, _vent_top + 3.2)
frame_upper = frame_upper.fuse(vent_top_keeper).removeSplitter()
# Removable top clamp for the main valve. Two broad feet bear on the case shoulders,
# leaving the upper tube clear; the nuts belong to the fixed upper frame, not the right cover.
VALVE_CLAMP_X, VALVE_CLAMP_BOLTS = (-46.0, -36.0), (-52.0, -30.0)
VALVE_CLAMP_PLANE, VALVE_CLAMP_T = DRUM_R, 4.0


def _valve_clamp_envelope(extra):
    br, sr = BODY_R + extra, TUBE_OD / 2 + 1.5 + extra
    p = math.acos((br - sr) / chamber_x)
    x0, x1 = VALVE_CLAMP_X[0] - 1, VALVE_CLAMP_X[1] + 1
    poly = [(-br * math.sin(p), Z_FIRE + br * math.cos(p)),
            (-sr * math.sin(p), Z_FIRE + chamber_x + sr * math.cos(p)),
            (sr * math.sin(p), Z_FIRE + chamber_x + sr * math.cos(p)),
            (br * math.sin(p), Z_FIRE + br * math.cos(p))]
    return (cyl_x(2 * br, x0, x1, 0, Z_FIRE)
            .fuse(cyl_x(2 * sr, x0, x1, 0, Z_FIRE + chamber_x)).fuse(prism_x(poly, x0, x1)).removeSplitter())


def _valve_clamp_hex(x, z0, z1, af):
    r = af / math.sqrt(3)
    pts = [V(x + r * math.cos(math.radians(30 + 60 * i)), r * math.sin(math.radians(30 + 60 * i)), z0) for i in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, z1 - z0))


_rcz, (_rcx0, _rcx1) = VALVE_CLAMP_PLANE, VALVE_CLAMP_X
valve_clamp = box(VALVE_CLAMP_BOLTS[0] - 4, VALVE_CLAMP_BOLTS[1] + 4, -5, 5, _rcz, _rcz + VALVE_CLAMP_T)
valve_clamp = valve_clamp.fuse(box(_rcx0, _rcx1, -20, 20, _rcz, _rcz + VALVE_CLAMP_T))
_rc_feet, _rc_slots = [], []
for _sg in (-1, 1):
    _ya, _yb = sorted((_sg * 14, _sg * 18))
    _rc_feet.append(box(_rcx0, _rcx1, _ya, _yb, -4, _rcz))
    valve_clamp = valve_clamp.fuse(_rc_feet[-1])
    _rc_slots.append(box(_rcx0 - 0.2, _rcx1 + 0.2, _ya - 0.2, _yb + 0.2, -4.2, _rcz + 1.5))
_rc_inner = _valve_clamp_envelope(0.7)
valve_clamp = valve_clamp.cut(_rc_inner).removeSplitter()
valve_clamp_liner = _rc_inner.cut(_valve_clamp_envelope(0.2)).common(Part.makeCompound(_rc_feet))
_rc_hardware = []
for _x in VALVE_CLAMP_BOLTS:
    frame_upper = frame_upper.fuse(Part.makeCylinder(4, 7, V(_x, 0, _rcz - 7), ZA)).removeSplitter()
    _hole = Part.makeCylinder(1.7, 40, V(_x, 0, _rcz - 22.5), ZA)
    # Retained, side-loaded nuts: the upper floor carries clamping load, the lower lip retains the nut.
    frame_upper = frame_upper.cut(_hole).cut(_valve_clamp_hex(_x, _rcz - 6.1, _rcz - 3.5, 5.9))
    frame_upper = frame_upper.cut(box(_x - 3.1, _x + 3.1, -12, 0, _rcz - 6.1, _rcz - 3.5)).removeSplitter()
    valve_clamp = valve_clamp.cut(_hole).removeSplitter()
    _head_z = _rcz + VALVE_CLAMP_T
    _screw = Part.makeCylinder(1.5, 16, V(_x, 0, _head_z - 16), ZA).fuse(Part.makeCylinder(2.75, 3, V(_x, 0, _head_z), ZA))
    _nut = _valve_clamp_hex(_x, _rcz - 5.9, _rcz - 3.5, 5.5).cut(_hole)
    _rc_hardware.extend((_screw, _nut))
frame_upper = _shell_cut_tools(frame_upper, _rc_slots)
valve_clamp_fasteners = Part.makeCompound(_rc_hardware)
# Independent lower/upper assembly screw, accessible before the right cover is installed.
FRAME_JOIN_X, FRAME_JOIN_Y = -84.5, -19.0
_jx, _jy = FRAME_JOIN_X, FRAME_JOIN_Y
_join_lower = Part.makeCylinder(5.5, 25, V(_jx, _jy, -70), ZA)
_join_lower = _join_lower.cut(_grip_blank).cut(_vv).cut(sock_cap).cut(sock_body).cut(air_cut)
_join_upper = Part.makeCylinder(4.2, 9, V(_jx, _jy, SPLIT_Z), ZA).cut(_vv).cut(sock_cap).cut(sock_body)
frame_lower = frame_lower.fuse(_join_lower).fuse(Part.makeCylinder(3.5, 2.2, V(_jx, _jy, SPLIT_Z), ZA)).removeSplitter()
frame_upper = frame_upper.fuse(_join_upper).removeSplitter()
frame_upper = frame_upper.cut(Part.makeCylinder(3.7, 2.6, V(_jx, _jy, SPLIT_Z - 0.2), ZA))
_join_shaft = Part.makeCylinder(1.7, 60, V(_jx, _jy, -90), ZA)
_join_head = Part.makeCylinder(4.1, 23.5, V(_jx, _jy, -90), ZA)
_join_nut = _valve_clamp_hex(_jx, -39.3, -36.5, 5.9).translated(V(0, _jy, 0))
_join_nut = _join_nut.fuse(box(_jx - 3.1, _jx + 3.1, -26, _jy, -39.3, -36.5))
frame_lower = _shell_cut_tools(frame_lower.cut(_join_shaft).cut(_join_head).cut(_trigger_axle_hole), _shell_cutters)
frame_lower = frame_lower.removeSplitter()   # its added support was already cut to the valve and grip envelopes
frame_upper = _shell_cut_tools(frame_upper.cut(_join_shaft).cut(_join_nut), _shell_cutters).removeSplitter()
_join_bolt = Part.makeCylinder(1.5, 30, V(_jx, _jy, -66.5), ZA).fuse(Part.makeCylinder(2.75, 3, V(_jx, _jy, -69.5), ZA))
_join_nut_actual = _valve_clamp_hex(_jx, -39.3, -36.9, 5.5).translated(V(0, _jy, 0)).cut(_join_shaft)
frame_join_fastener = Part.makeCompound([_join_bolt, _join_nut_actual])
# Continue the grip's elliptical loft up to the tray, without a separate flat-sided shoulder.
_grip_keep = box(-400, SLAB["x"][0], -100, 100, -400, 100).fuse(box(-400, 100, -100, 100, -400, SLAB["z"][0] + 5))
grip = _grip_blank.common(_grip_keep).cut(frame_lower).cut(frame_upper).cut(side_plate_r).cut(side_band)
grip = grip.cut(air_cut).cut(_vv).cut(_trigger_axle_hole)
grip = grip.cut(box(-95, -40.5, -4.5, 4.5, -110, -60)).cut(guard).cut(dowels).cut(spur_slot)
# Two additional 4 mm tongues on the extended neck; sockets are 0.2 mm clear on each side.
GRIP_SHOULDER_TONGUES = ((-80.0, -9.0, 4.0), (-80.0, 9.0, 4.0))
for _x, _y, _w in GRIP_TONGUES + GRIP_SHOULDER_TONGUES:
    grip = grip.fuse(box(_x - _w / 2, _x + _w / 2, _y - _w / 2, _y + _w / 2, -73.0, -67.0))
    if (_x, _y, _w) in GRIP_SHOULDER_TONGUES:
        frame_lower = frame_lower.cut(box(_x - _w / 2 - 0.2, _x + _w / 2 + 0.2,
                                          _y - _w / 2 - 0.2, _y + _w / 2 + 0.2, -73.2, -66.8)).removeSplitter()
grip_left = grip.common(box(-400, 100, -100, 0, -400, 100)).removeSplitter()
grip_right = grip.common(box(-400, 100, 0, 100, -400, 100)).removeSplitter()
for _p in GRIP_BOLTS:
    _bore = Part.makeCylinder(1.7, 33.0, V(_p.x, -16.5, _p.z), YA)
    grip_left = grip_left.cut(_bore).cut(_grip_hex(_p.x, _p.z, -16.2, -11.0, 5.7))
    grip_right = grip_right.cut(_bore).cut(Part.makeCylinder(3.1, 4.2, V(_p.x, 10.6, _p.z), YA))
grip_left = _shell_cut_tools(grip_left.cut(air_cut), _shell_cutters)
grip_right = _shell_cut_tools(grip_right.cut(air_cut), _shell_cutters)
grip_left = max(grip_left.Solids, key=lambda q: q.Volume)
grip_right = max(grip_right.Solids, key=lambda q: q.Volume)
# Positive grip attachment with external head/nut access; the central hose route stays open.
GRIP_MOUNT_X, GRIP_MOUNT_Z = -107.0, -85.5


def _grip_mount_xz(points, y0, y1):
    pts = [V(x, y0, z) for x, z in points]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, y1 - y0, 0))


_gm_outline = [(-112, -66.5), (-100, -66.5), (-100, -81), (-104, -91), (-112, -91)]
_gm_tang = _grip_mount_xz(_gm_outline, -9.5, -5.5).fuse(_grip_mount_xz(_gm_outline, 5.5, 9.5))
_gm_tang = _gm_tang.fuse(box(-112, -104, -9.5, 9.5, -91, -87)).cut(air_cut).removeSplitter()
_gm_tang = _shell_cut_tools(_gm_tang, _shell_cutters)
_gm_pocket = _grip_mount_xz([(-112.2, 0), (-99.8, 0), (-99.8, -81.1), (-103.85, -91.2), (-112.2, -91.2)], -9.7, 9.7)   # open mouth permits downward withdrawal
_gmx, _gmz = GRIP_MOUNT_X, GRIP_MOUNT_Z
_gm_shaft = Part.makeCylinder(1.7, 60, V(_gmx, -30, _gmz), YA)
_gm_head = Part.makeCylinder(4.1, 15.5, V(_gmx, -30, _gmz), YA)
_gm_nut = _drive_hex_y(_gmx, _gmz, 13, 15.8, 5.9).fuse(Part.makeCylinder(4.1, 14.2, V(_gmx, 15.8, _gmz), YA))
frame_lower = frame_lower.fuse(_gm_tang).removeSplitter().cut(_gm_shaft).removeSplitter()
grip_left = grip_left.fuse(Part.makeCylinder(5.5, 8, V(_gmx, -18, _gmz), YA)).cut(_gm_pocket)
grip_left = grip_left.cut(_gm_shaft).cut(_gm_head).removeSplitter()
grip_right = grip_right.fuse(Part.makeCylinder(5.5, 8, V(_gmx, 10, _gmz), YA)).cut(_gm_pocket)
grip_right = grip_right.cut(_gm_shaft).cut(_gm_nut).removeSplitter()
# Release the small wraps around the existing frame-joint and rear shell-bolt pockets.
# The original glued grip imprint had undercuts here; the bolted grip must withdraw downward.
_gm_release_left = box(-90, -79.8, -17, -14, -71, 0)
_gm_release_right = box(-108.5, -98, 15.6, 17.4, -71, 0)
grip_left = grip_left.cut(_gm_release_left).removeSplitter()
grip_right = grip_right.cut(_gm_release_right).removeSplitter()
_gm_bolt = Part.makeCylinder(1.5, 30, V(_gmx, -14.5, _gmz), YA).fuse(Part.makeCylinder(2.75, 3, V(_gmx, -17.5, _gmz), YA))
_gm_nut_actual = _drive_hex_y(_gmx, _gmz, 13, 15.4, 5.5).cut(_gm_shaft)
grip_mount_fastener = Part.makeCompound([_gm_bolt, _gm_nut_actual])
# Independent guard fasteners: two upward M3 x 12, one transverse M3 x 20.
def _guard_hex_z(x, y, z0, z1, af):
    h = _drive_hex_y(0, 0, z0, z1, af)
    h.rotate(V(0, 0, 0), XA, 90)
    h.translate(V(x, y, 0))
    return h


_guard_fasteners = []
for _gy in GUARD_FRONT_YS:
    _gb = Part.makeCylinder(4.5, 7.8, V(GUARD_FRONT_X, _gy, -70), ZA)
    _gb = _gb.common(box(-56.7, -48, -20, 20, -71, -62))
    _gs = Part.makeCylinder(1.7, 20, V(GUARD_FRONT_X, _gy, -80), ZA)
    _gn = _guard_hex_z(GUARD_FRONT_X, _gy, -65, -62.2, 5.9)
    _gn = _gn.fuse(box(-55.95, -50.05, min(_gy, _gy * 2.5), max(_gy, _gy * 2.5), -65, -62.2))   # slide the nut in from the open side before fitting the side cover
    _gkey = box(-56.2, -49.8, _gy - 3.2, _gy + 3.2, -70.2, -67.3)
    frame_lower = frame_lower.fuse(_gb).removeSplitter().cut(_gs).cut(_gn).cut(_gkey).removeSplitter()
    _guard_fasteners.extend([Part.makeCylinder(1.5, 12, V(GUARD_FRONT_X, _gy, -74.5), ZA).fuse(
        Part.makeCylinder(2.75, 3, V(GUARD_FRONT_X, _gy, -77.5), ZA)),
        _guard_hex_z(GUARD_FRONT_X, _gy, -65, -62.6, 5.5).cut(_gs)])
# Open below: the guard can be inserted after the grip and removed without undoing its mount.
_guard_rear_clear = box(-101.2, -92.8, -5.2, 5, -110, -80.8)
_guard_rear_head = Part.makeCylinder(3.2, 25, V(GUARD_REAR_X, -30, GUARD_REAR_Z), YA)
_guard_rear_nut = _drive_hex_y(GUARD_REAR_X, GUARD_REAR_Z, 12.5, 15.3, 5.9).fuse(
    Part.makeCylinder(4.1, 14.7, V(GUARD_REAR_X, 15.3, GUARD_REAR_Z), YA))
_guard_rear_boss = Part.makeCylinder(5.5, 10, V(GUARD_REAR_X, 8, GUARD_REAR_Z), YA).cut(_gm_pocket)
grip_left = grip_left.cut(_guard_rear_clear).cut(_guard_rear_shaft).cut(_guard_rear_head).removeSplitter()
grip_right = grip_right.fuse(_guard_rear_boss).cut(_guard_rear_clear).cut(_guard_rear_shaft).cut(_guard_rear_nut).removeSplitter()
_guard_fasteners.extend([Part.makeCylinder(1.5, 20, V(GUARD_REAR_X, -5, GUARD_REAR_Z), YA).fuse(
    Part.makeCylinder(2.75, 3, V(GUARD_REAR_X, -8, GUARD_REAR_Z), YA)),
    _drive_hex_y(GUARD_REAR_X, GUARD_REAR_Z, 12.5, 14.9, 5.5).cut(_guard_rear_shaft)])
guard_fasteners = Part.makeCompound(_guard_fasteners)
# A small annular continuation of the rear window clears the short finger hook at full travel.
# It stops at R53 / 260 degrees, clear of the trigger bearing and the grip saddle.
_hh_pts = [V(H.x, -5.2, H.z)] + [V(H.x + 53 * math.cos(math.radians(a_)), -5.2,
                                    H.z + 53 * math.sin(math.radians(a_))) for a_ in range(238, 261, 2)]
spur_hook_relief = Part.Face(Part.makePolygon(_hh_pts + [_hh_pts[0]])).extrude(V(0, 10.4, 0))
spur_hook_relief = spur_hook_relief.cut(Part.makeCylinder(36, 12, V(H.x, -6, H.z), YA))
frame_lower = frame_lower.cut(spur_hook_relief).removeSplitter()
frame_upper = frame_upper.cut(spur_hook_relief).removeSplitter()
grip = Part.makeCompound([grip_left, grip_right])
# Fuse with overlap into the native pad; no buried detent-mount nuts or legacy through-holes.
side_band = side_band.fuse(detent_mount).removeSplitter()
# The unprinted left shell also needs clearance for the existing gauge tube route.
side_band = side_band.cut(air_cut).removeSplitter()
side_plate = side_band                                      # tongues and bolt holes included
frame = Part.makeCompound([frame_lower, frame_upper])          # for the checks; the parts print separately

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
    moving = tuple(n_ for n_ in ("Sector", "Pawl", "Slider", "Slider_cap", "Slider_cap_fastener", "Pin", "Bolt", "Hammer", "Crank_fastener", "Sleeve", "Pusher", "Trigger", "Trigger_pad", "Trigger_pad_fastener", "Trigger_pin") if n_ in rest)
    worst = {}
    for c in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        for tg in (0.0, 1.0):
            st = pose(dict(cock=c, block=block_drive(c), bend=0.0, trig=tg))
            for n in moving:
                for other_name, other in (("frame", Part.makeCompound([frame_lower, frame_upper])), ("side plate", side_plate), ("right plate", side_plate_r), ("skin", skin), ("grip", grip),
                                          ("detent box", detent_box), ("detent service screw", detent_service_fastener), ("guard", guard), ("spacer", sector_spacer),
                                          ("air lines", Part.makeCompound([supply_line, pilot_line, gauge_line, tee])),
                                          ("vent valve", valve_bodies), ("crest", crest),
                                          ("valve clamp", Part.makeCompound([valve_clamp, valve_clamp_liner, valve_clamp_fasteners])),
                                          ("frame assembly screw", frame_join_fastener),
                                          ("grip mount screw", grip_mount_fastener),
                                          ("guard screws", guard_fasteners),
                                      ("tie rods", valve_rods), ("lock bolts", lock_bolts)):
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
                  "spring rib/frame": hit(spring_rib, frame),   # the rib is a cantilever on the left plate, in the room's air
                  "tie rods/frame+plates": hit(valve_rods, frame) + hit(valve_rods, side_plate) + hit(valve_rods, side_plate_r),
                  "lock bolts/frame+plates": hit(lock_bolts, frame) + hit(lock_bolts, side_plate) + hit(lock_bolts, side_plate_r),
                  "tie rods/springs": hit(valve_rods, mainsprings),   # the coils sit outside the heads' reach now
                  "tie rods/housing+spacer": hit(valve_rods, lock_housing_h) + hit(valve_rods, sector_spacer),
                  "plug/axle+nose+strap": hit(axle_plug, axle) + hit(axle_plug, nose) + hit(axle_plug, top_strap)}
    inside = mini_valves.common(grip.fuse(outer).fuse(_vv)).Volume / mini_valves.Volume
    spur_out = lambda c: hammer_shape(c).cut(outer).Volume
    report = [NAME, "  mechanism vs dress (worst over the hammer and trigger strokes, mm3):"]
    report += ["    %-8s / %-11s %.1f" % (k[0], k[1], v_) for k, v_ in sorted(worst.items()) if v_ > 0.05] or ["    none"]
    report += ["  fixed: " + ", ".join("%s %.1f" % kv for kv in fixed_hits.items()),
               "  QEV socket: +%.1f mm round the stack (the sealed valve drops in); the tie rods' heads %.1f mm off the cap's rear face"
               % (VALVE_SOCK, WASHERS_UNDER_HEAD + ROD_HEAD_H),
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
    report = [NAME, "  geometry, document and weights (CHECKS stays off until the owner asks; then set it True before exec)"]
    print("\n".join(report))

if CHECKS:
    # ---------------------------------------------------------------- checks: pass or fail, not only numbers
    checks = {}
    checks["frame lower half is one sound solid (%.0f mm3, valid %s)" % (frame_lower.Volume, frame_lower.isValid())] = \
        frame_lower.isValid() and len(frame_lower.Solids) == 1 and frame_lower.Volume > 50000   # rounded tray, with the rear grip seat retained
    checks["frame upper half is one sound solid (%.0f mm3, valid %s)" % (frame_upper.Volume, frame_upper.isValid())] = \
        frame_upper.isValid() and len(frame_upper.Solids) == 1 and frame_upper.Volume > 10000
    checks["the frame's halves do not overlap when assembled (%.2f mm3)" % hit(frame_lower, frame_upper)] = \
        hit(frame_lower, frame_upper) < 0.05
    checks["the plates' tongues clear the frame's grooves (%.2f mm3)" % (hit(frame, side_plate) + hit(frame, side_plate_r))] = \
        hit(frame, side_plate) + hit(frame, side_plate_r) < 0.05
    checks["side band is one sound solid (%.0f mm3, %d solids)" % (side_band.Volume, len(side_band.Solids))] = \
        side_band.isValid() and len(side_band.Solids) == 1 and side_band.Volume > 15000
    checks["right plate is one sound solid (%.0f mm3, %d solids)" % (side_plate_r.Volume, len(side_plate_r.Solids))] = \
        side_plate_r.isValid() and len(side_plate_r.Solids) == 1 and side_plate_r.Volume > 15000
    _tip_r = side_plate_r.common(box(_CX - _CW / 2, _CX + _CW / 2, 19.8, 23.2, 29.4, 32.0))
    _tip_l = side_band.common(box(_CX - _CW / 2, _CX + _CW / 2, -20.0, -17.4, 29.4, 32.0))
    checks["crown tongues seat in the lid (R %.1f, L %.1f mm3) and clear it (%.3f)" % (
        _tip_r.Volume, _tip_l.Volume, hit(_tip_r, frame_upper) + hit(_tip_l, frame_upper))] = \
        _tip_r.Volume > 8 and _tip_l.Volume > 8 and hit(_tip_r, frame_upper) + hit(_tip_l, frame_upper) < 0.05
    checks["crown tongues slide off along y (%.3f mm3)" % (
        hit(_tip_r.translated(V(0, 6, 0)), frame_upper) + hit(_tip_l.translated(V(0, -6, 0)), frame_upper))] = \
        hit(_tip_r.translated(V(0, 6, 0)), frame_upper) + hit(_tip_l.translated(V(0, -6, 0)), frame_upper) < 0.05
    checks["crown tongues locate along x (%.1f mm3)" % (
        hit(_tip_r.translated(V(1.5, 0, 0)), frame_upper) + hit(_tip_l.translated(V(1.5, 0, 0)), frame_upper))] = \
        hit(_tip_r.translated(V(1.5, 0, 0)), frame_upper) > 2 and hit(_tip_l.translated(V(1.5, 0, 0)), frame_upper) > 2
    _gL = grip_left.common(box(-104.5, -99.5, -12.5, -7.5, -70.05, -67.0))
    _gR = grip_right.common(box(-99.5, -96.5, 10.5, 13.5, -70.05, -67.0))
    checks["grip tongues seat in the tray (L %.1f, R %.1f mm3) and clear it (%.3f)" % (
        _gL.Volume, _gR.Volume, hit(_gL, frame_lower) + hit(_gR, frame_lower))] = \
        _gL.Volume > 15 and _gR.Volume > 15 and hit(_gL, frame_lower) + hit(_gR, frame_lower) < 0.05
    checks["grip tongues lift off downward (%.3f mm3)" % (
        hit(_gL.translated(V(0, 0, -4)), frame_lower) + hit(_gR.translated(V(0, 0, -4)), frame_lower))] = \
        hit(_gL.translated(V(0, 0, -4)), frame_lower) + hit(_gR.translated(V(0, 0, -4)), frame_lower) < 0.05
    # The right tongue is open forward: the valve socket starts just ahead of it.
    # The left one stops the bolted pair both ways.
    _lx = hit(_gL.translated(V(1.5, 0, 0)), frame_lower) + hit(_gL.translated(V(-1.5, 0, 0)), frame_lower)
    _rx = hit(_gR.translated(V(-1.5, 0, 0)), frame_lower)
    checks["grip tongues locate along x (left %.1f both ways, right %.1f rearward)" % (_lx, _rx)] = _lx > 8 and _rx > 2
    checks["grip halves are one solid each (%d, %d)" % (len(grip_left.Solids), len(grip_right.Solids))] = \
        grip_left.isValid() and grip_right.isValid() and len(grip_left.Solids) == 1 and len(grip_right.Solids) == 1
    _bh = _bn = _bo = _bd = _bw = 0.0
    for _p in GRIP_BOLTS:
        _shank = Part.makeCylinder(1.7, 26.0, V(_p.x, -12.0, _p.z), YA)
        _nutv = Part.makeCylinder(2.2, 2.2, V(_p.x, -13.4, _p.z), YA)
        _open = Part.makeCylinder(2.0, 2.0, V(_p.x, 13.6, _p.z), YA)
        _wide = Part.makeCylinder(3.4, 36.0, V(_p.x, -18.0, _p.z), YA)
        _wall = Part.makeCylinder(4.2, 1.4, V(_p.x, -12.6, _p.z), YA)
        _bh += hit(_shank, air_cut) + hit(_nutv, air_cut)
        _bn += hit(_nutv, grip_left) + hit(_shank, grip_left) + hit(_shank, grip_right)
        _bo += hit(_open, grip_right)
        _bd += hit(_wide, dowels)
        _bw += hit(_wall, grip_left)
    checks["grip bolts miss the hose (%.2f) and run through, nut pocket open (%.2f)" % (_bh, _bn)] = _bh < 0.05 and _bn < 0.05
    checks["grip bolt heads open the right face (%.2f), miss the dowels (%.2f), nut keeps a wall (%.1f)" % (_bo, _bd, _bw)] = \
        _bo < 0.05 and _bd < 0.05 and _bw > 8.0
    _gap = VALVE_SOCK - 0.2
    checks["QEV socket: the stack meets nothing %.1f mm off its seat sideways (room for the sealant)" % _gap] = \
        all(v_ < 0.05 for v_ in (valve_cap.translated(V(0, _gap, 0)).common(frame).Volume,
                                 valve_cap.translated(V(0, -_gap, 0)).common(frame).Volume,
                                 valve_cap.translated(V(0, 0, _gap)).common(frame).Volume,
                                 valve_cap.translated(V(0, 0, -_gap)).common(frame).Volume,
                                 valve_body.translated(V(0, _gap, 0)).common(frame).Volume,
                                 valve_body.translated(V(0, -_gap, 0)).common(frame).Volume,
                                 valve_body.translated(V(0, 0, _gap)).common(frame).Volume,
                                 valve_body.translated(V(0, 0, -_gap)).common(frame).Volume))
    checks["mechanism clears the dress over the hammer and trigger strokes"] = not [v_ for (n_, o_), v_ in worst.items()
                                                                                      if v_ > (0.0001 if n_ in ("Trigger", "Trigger_pad", "Trigger_pad_fastener", "Trigger_pin") else 0.05) and not (o_ == "spacer" and v_ < 5.0)]   # the spacer touches by design; OCCT's common of its 0.1-gap faces returns junk (the bbox falls outside both parts)
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
    # Check the finished parts: later supports must not close either end of the guide passage.
    _bore = Part.makeCylinder(GUIDE_ROD["d"] / 2 + 0.10, 200.0, V(GUIDE_ROD["x"], GUIDE_ROD["y"], -100.0), ZA)
    _left = sum(hit(_bore, s_) for s_ in (frame_lower, frame_upper, side_plate_r))
    checks["guide rod hole through ceiling and floor (%.1f mm3 left in the bore)" % _left] = _left < 0.05
    # The slider's steel pin must have a hole to sit in: drawn over solid plastic it only looked fixed.
    _sl0, _pin0 = slider_h(0.5)
    checks["slider pin sits in its hole (%.1f mm3 of it inside solid plastic)" % hit(_sl0, _pin0)] = hit(_sl0, _pin0) < 0.05
    # Check assembly paths, not only the final pose: the old return lip trapped the slider.
    _cover_hit, _cap_hit = 0.0, 0.0
    for _c in (0.0, 0.5, 1.0):
        _ps = pose(dict(cock=_c, block=block_drive(_c), bend=0.0, trig=0.0))
        _installed = Part.makeCompound(list(_ps.values()) + [frame_lower, frame_upper, side_band, guide_rod, shaft,
            valve_clamp, valve_clamp_liner, valve_clamp_fasteners, frame_join_fastener, grip_mount_fastener, grip_left, grip_right,
            valve_bodies, valve_body, valve_cap, lock_housing_h, detent_box, sector_spacer, axle, mainsprings])
        for _dy in (0.0, 0.2, 1.0, 3.0, 6.0, 12.0, 24.0, 40.0):
            _cover_hit = max(_cover_hit, hit(side_plate_r.translated(V(0, _dy, 0)), _installed))
        _targets = Part.makeCompound([_ps[n_] for n_ in ("Slider", "Hammer", "Crank_fastener")])
        for _dx, _dz in ((0, 0), (1, 0), (2, 0), (3.2, 0), (3.2, 1), (3.2, 3), (3.2, 6), (3.2, 10)):
            _cap_hit = max(_cap_hit, hit(SLIDER_CAP.translated(V(_dx, 0, slider_z(_c) + _dz)), _targets))
    checks["right cover closes last along y (%.3f mm3 interference)" % _cover_hit] = _cover_hit < 0.05
    checks["slider cap opens with crank already installed (%.3f mm3 interference)" % _cap_hit] = _cap_hit < 0.05
    _grip_withdraw_hit = max(hit(grip.translated(V(0, 0, -dz_)), frame_lower) for dz_ in (0, 0.2, 1, 3, 6, 12, 24, 30))
    checks["bolted grip withdraws down off the lower frame (%.3f mm3 interference)" % _grip_withdraw_hit] = _grip_withdraw_hit < 0.05
    checks["grip mount bolt and nut clear the hose and printed parts"] = \
        hit(grip_mount_fastener, air_cut) + sum(hit(grip_mount_fastener, s_) for s_ in (frame_lower, grip_left, grip_right)) < 0.05
    checks["guard is one valid solid"] = guard.isValid() and len(guard.Solids) == 1
    _guard_out = max(sum(hit(guard.translated(V(0, 0, -dz_)), s_) for s_ in (frame_lower, grip_left, grip_right))
                     for dz_ in (0, 0.2, 1, 3, 6, 12, 24, 40))
    checks["guard withdraws down independently (%.3f mm3 interference)" % _guard_out] = _guard_out < 0.05
    _guard_nuts = max(hit(_guard_hex_z(GUARD_FRONT_X, y_ + math.copysign(dy_, y_), -65, -62.6, 5.5), frame_lower)
                      for y_ in GUARD_FRONT_YS for dy_ in (0, 0.2, 1, 3, 6, 12, 24))
    checks["guard front nuts slide in from the open sides (%.3f mm3 interference)" % _guard_nuts] = _guard_nuts < 0.05
    checks["guard hardware clears the printed parts and wiring"] = \
        sum(hit(guard_fasteners, s_) for s_ in (guard, frame_lower, grip_left, grip_right, air_cut, side_plate_r)) < 0.05
    # Printability and the trigger's loaded joint are stricter than a solid-volume clash threshold.
    import MeshPart
    for _name, _part in (("Frame_lower", frame_lower), ("Frame_upper", frame_upper), ("Frame_right", side_plate_r),
                         ("Trigger", TRIGGER_BODY), ("Trigger_pad", TRIGGER_PAD), ("Detent_housing", detent_box), ("Frame_side_band", side_band)):
        _mesh = MeshPart.meshFromShape(Shape=_part, LinearDeflection=0.05, AngularDeflection=0.15, Relative=False)
        checks["%s has a closed manifold print mesh" % _name] = _mesh.isSolid() and not _mesh.hasNonManifolds()
    _pad_tilt = TRIGGER_PAD.copy()
    _pad_tilt.rotate(V(-9.5, 3, -7), XA, -0.25)
    checks["pad mating face removes free rocking before bolt preload"] = hit(_pad_tilt, TRIGGER_BODY) > 0.01
    checks["pad seats along y without interference"] = max(hit(TRIGGER_PAD.translated(V(0, d_, 0)), TRIGGER_BODY)
                                                        for d_ in (0, 0.2, 1, 3, 6, 12)) < 0.0001
    checks["trigger steel pin clears its carrier and bolt"] = sum(hit(TRIGGER_PIN, s_) for s_ in (TRIGGER_BODY, TRIGGER_PAD, TRIGGER_PAD_FASTENER)) < 0.0001
    checks["trigger steel pin is captured at both ends"] = all(sum(hit(TRIGGER_PIN.translated(V(0, dy_, 0)), s_)
                                                               for s_ in (TRIGGER_BODY, TRIGGER_PAD)) > 0.01 for dy_ in (-0.2, 0.2))
    _trig_reserve = max(hit(_rot_y(s_.translated(TRIGGER_PIVOT), TRIGGER_PIVOT, a_), fixed_)
                       for a_ in (TRIGGER_TRAVEL, TRIGGER_TRAVEL + 1, TRIGGER_TRAVEL + 2)
                       for s_ in (TRIGGER_BODY, TRIGGER_PAD, TRIGGER_PAD_FASTENER, TRIGGER_PIN)
                       for fixed_ in (frame_lower, frame_upper, side_plate_r, grip_left, grip_right, guard))
    checks["trigger has 2 deg of case clearance beyond nominal valve stop (%.6f mm3)" % _trig_reserve] = _trig_reserve < 0.0001
    _detent_out = Part.makeCompound([detent_box, turned(detent_bolt_print, DETENT_ANGLE + 90)])
    _detent_fixed = (frame_lower, frame_upper, side_band, side_plate_r,
                     rest["Block"], valve_body, valve_cap, lock_housing_h, axle)
    _detent_remove_hit = max(hit(_detent_out.translated(DETENT_REMOVE_DIRECTION * d_), s_)
                            for d_ in (0, 0.2, 1, 2, 4, 8, 12, 20) for s_ in _detent_fixed)
    checks["detent housing and plunger withdraw without opening shell (%.6f mm3)" % _detent_remove_hit] = _detent_remove_hit < 0.0001
    checks["detent service screw clears integral shell mount"] = sum(
        hit(hw_, s_) for hw_ in (detent_service_fastener,)
        for s_ in (detent_box, frame_lower, frame_upper, side_band, side_plate_r)) < 0.0001
    checks["left shell clears the existing supply, pilot and gauge tube routes"] = sum(
        hit(side_band, s_) for s_ in (supply_line, pilot_line, gauge_line, tee)) < 0.0001
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
                     ("Sector_spacer", sector_spacer, (0.8, 0.8, 0.82), 0),
                     ("Tie_rods", valve_rods, (0.72, 0.72, 0.75), 0), ("Lock_bolts", lock_bolts, (0.72, 0.72, 0.75), 0)):
    add(g_mech, n, s_, c, tr)
for n, s_ in rest.items():
    add(g_mech, n, s_, *STYLE[n])
g_dress = doc.addObject("App::DocumentObjectGroup", "Dress")
for n, s_, c, tr in (("Frame_lower", frame_lower, IRON, 0), ("Frame_upper", frame_upper, IRON, 0),
                      ("Valve_clamp", valve_clamp, IRON, 0), ("Valve_clamp_liner", valve_clamp_liner, (0.15, 0.15, 0.15), 0),
                      ("Valve_clamp_fasteners", valve_clamp_fasteners, (0.75, 0.75, 0.78), 0),
                      ("Frame_join_fastener", frame_join_fastener, (0.75, 0.75, 0.78), 0),
                      ("Grip_mount_fastener", grip_mount_fastener, (0.75, 0.75, 0.78), 0),
                      ("Guard_fasteners", guard_fasteners, (0.75, 0.75, 0.78), 0),
                      ("Frame_side_band", side_band, (0.28, 0.27, 0.26), 0),
                      ("Frame_right", side_plate_r, (0.32, 0.31, 0.30), 0), ("Frame_skin", skin, IRON, 0), ("Trigger_guard", guard, IRON, 0),
                     ("Detent_housing", detent_box, IRON, 0), 
                     ("Detent_service_fastener", detent_service_fastener, (0.75, 0.75, 0.78), 0),
                     ("Grip_left", grip_left, WOOD, 0), ("Grip_right", grip_right, WOOD, 0), ("Rags", Part.makeCompound(rags), RAG, 0),
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
    "print": ("Valve_body_v11", "Valve_cap_v11", "Lock_housing", "Block", "Sector", "Pawl", "Slider", "Slider_cap", "Bolt", "Hammer",
              "Sleeve", "Pusher", "Trigger", "Trigger_pad", "Frame_lower", "Frame_upper", "Valve_clamp", "Frame_side_band", "Frame_right", "Detent_housing", "Grip_left", "Grip_right", "Trigger_guard",
              "Top_strap", "Axle_plug", "Sector_spacer",
              "Nose_sleeve"),
    "eva": ("Frame_skin", "Valve_clamp_liner", "Rags", "Pommel", "Pommel_claws", "Warpstone_pommel", "Straps", "Strap_rivets", "Spikes", "Plates",
            "Plate_rivets", "Crest", "Vial_caps", "Vial_cage", "Warpstone_vial"),
    "buy": ("Chamber_axle", "Vent_valve", "Detent_service_fastener", "Pin", "Crank_fastener", "Slider_cap_fastener", "Trigger_pad_fastener", "Trigger_pin", "Valve_clamp_fasteners", "Frame_join_fastener", "Grip_mount_fastener", "Guard_fasteners", "Mainsprings", "Hammer_axle", "Guide_rod", "Hose", "Vial_glass", "Gauge", "Gauge_glass",
            "Gauge_needle", "Pilot_pipe", "Gauge_line", "Tee", "Axle_cap", "Thrust_washer", "Tie_rods", "Lock_bolts"),
}
BUY_NOTE = {"Chamber_axle": "tube Ø25 x 0.6, %.0f mm (the chamber)" % axle.BoundBox.XLength, "Block": "+ 6 barrel tubes Ø25 x 0.6, %.0f mm" % BARREL_TUBE,
            "Vent_valve": "AirTAC M3R110-06, roller off. Straight R1/8 push-ins (a G body is the same holes): Ø10 x 20 on A for the 4 mm pilot, Ø12 x 22 on R for the 6 mm supply, a silencer on P. Stamped R next to the stem, P at the far end of that face, A opposite. Supply and exhaust are swapped, so it is normally open. Turned plunger-down, narrow faces sideways (A left, P above R on the right). Drops into its socket from the room (side plate off), stands on two feet - no fasteners", "Pin": "slider/sector: M3 x 6 cylindrical-head bolt, standard M3 nut and Ø7 x 0.5 washer; side-loaded nut, printed shoulder sets 0.2 mm running play",
            "Crank_fastener": "hammer/slider: M3 x 6 cylindrical-head bolt, standard M3 nut and Ø7 x 0.5 washer; captive nut and printed shoulder, 0.2 mm running play",
            "Slider": "open-top crank yoke with removable Slider_cap: engage the mounted crank before closing the window; guide rod stays on the fixed frame when the right cover comes off",
            "Slider_cap": "slide 3.2 mm toward positive x to release the left locating tongue, then lift in z; reverse to install over the crank collar and washer",
            "Slider_cap_fastener": "1 x M3 x 6 cylindrical-head bolt + M3 nut, no washer; cap seats against its post before tightening. Install before closing Frame_right",
            "Valve_clamp": "PETG top clamp: two broad shoulder feet, 4 mm bridge; print upside down on the flat top. Install after seating the main valve, before closing Frame_right. Tighten alternately only until the valve is held; a gap above the frame pads accommodates the sealant (0..6 mm)",
            "Valve_clamp_liner": "two 0.5 mm rubber/EVA contact strips, cut to the feet; no hard screw tip against the valve",
            "Valve_clamp_fasteners": "2 x M3 x 16 cylindrical-head bolts + 2 ordinary M3 nuts retained in Frame_upper; full nut engagement throughout 0..6 mm clamp lift",
            "Frame_join_fastener": "M3 x 30 cylindrical-head bolt from below + M3 nut loaded from the left into Frame_upper. Join the lower and upper frames before closing Frame_right; an annular shoulder locates the joint",
            "Grip_mount_fastener": "M3 x 30 cylindrical-head bolt from the left + ordinary M3 nut loaded from the right; recessed external seats, 3 mm bearing floors. Fastens the grip to the lower frame's internal saddle, independent of Frame_right",
            "Frame_lower": "open-bottom trigger clearance; independent M3 x 30 joint to Frame_upper from below. Internal U-shaped grip saddle with a separate transverse M3 x 30 mount; hose passage through the saddle",
            "Frame_upper": "independent guide support, main valve clamp mounts, and a 0.2 mm top keeper for the button valve; retained nut for the lower/upper frame assembly screw",
            "Trigger_pad_fastener": "M3 x 12 cylindrical-head bolt along +y + standard M3 nut, no washer; seat the pad against the lever broad y=3 face, slide nut into its open side pocket from positive x, tighten from negative y",
            "Trigger_pad": "PETG carrier for smooth steel pin 3 x 24; 3.2 mm root bore, open contact channel and distal axial stop. Print on broad x=-6 side",
            "Trigger_pin": "smooth steel pin diameter 3 x 24 mm; captured between blind root and carrier end lip, 0.3 mm total end play. Remove the carrier to withdraw the pin",
            "Mainsprings": "2 torsion springs, wire Ø1.6, OD 14, 6 coils", "Hose": "6/4 hose from the receiver, up the grip to the vent valve's R port",
            "Hammer": "one printed piece; thumb handle 30 mm lower at rest with a short rounded downward finger hook (about 22 mm below the heel including the R3.2 tip, 8 mm thick). Internal crank and sleeve retain their axes; teardrop spring-stop rib, Ø9 root boss; M3 x 6 crank fastener with captive nut",
            "Vial_glass": "a test tube Ø16", "Gauge": "a Ø25 0-4 bar gauge with a 4 mm push-in (it reads the chamber, through the pilot)",
            "Pilot_pipe": "PU tube 4/2.5: vent valve A, straight out of the left wall (Ø5 hole at x -91.5, z -39.2), back round the tail and in through the Ø16 hole in its rear to a tee behind the cap, then the cap's G1/8 push-in",
            "Gauge_line": "PU tube 4/2.5, tee to the gauge", "Tee": "push-in tee for 4 mm tube", "Axle_cap": "M6 x 25 stud (or a headless bolt) + cap nut; an M6 nut glued in the plug",
            "Axle_plug": "in the axle's front end on a 19 x 2.5 O-ring, its flange on the tube's end: it closes the chamber",
            "Top_strap": "2 x M3 x 40 + nuts down through its foot into the cage's top",
            "Thrust_washer": "nylon / PTFE washer 25 x 28 x 1",
            "Trigger_guard": "compact 10 x 3.2 mm ribbon; front keyed flange with 2 x M3 x 12 bolts from below and ordinary nuts slid into side slots before fitting the side covers; rear eye with independent M3 x 20 and nut accessible from outside the grip; inserts upward without glue",
            "Guard_fasteners": "2 x M3 x 12 cylindrical-head bolts + ordinary M3 nuts at the floor, 1 x M3 x 20 + ordinary M3 nut at the grip; independent of the grip mount",
            "Grip_left": "half: 2 x M3 x 25 and Ø3 x 12 dowels join the pair; extra M3 x 30 attaches it to Frame_lower. External recessed head, internal saddle pocket 0.2 mm clear. Front 4 mm tongue at x -80, y -9 retained",
            "Grip_right": "half: M3 x 25 pair bolts, extra M3 x 30 frame mount with an external M3 nut seat 5 mm deep. Rear 3 mm tongue at x -98, y 12 and front 4 mm tongue at x -80, y 9 retained; internal trigger and hose clearance",
            "Detent_housing": "removable from the integral left-shell mount: undo only external M3 x 16 and slide along the detent axis. Same housing as the separate-adapter version; plunger channel unchanged",
            "Frame_side_band": "left shell with integral detent locating rail and outer mounting ear; no separate adapter, internal mounting nut or M3 x 20. Legacy detent holes removed; existing gauge tube channel cleared",
            "Detent_service_fastener": "M3 x 16 cylindrical head + ordinary M3 nut, axis x; both ends outside the shell. Remove for housing service; integral mount stays on the left shell",
            "Frame_side_band": "left flank band: 2 x M3 x 50 through-bolts, recessed heads with optional thin washers on the left, standard M3 nuts in AF 5.9 anti-rotation sockets loaded from the right; round access wells, 3 mm seat floors, no printed threads",
            "Frame_right": "close last, sliding inward along negative y: guide supports stay on Frame_lower/Frame_upper, slider return lip relieved. 2 x M3 x 50 upper, 2 x M3 x 50 lower-middle/front, 1 x M3 x 40 lower-rear. Lower nut seats 6 mm deep (rear 4 mm); turn bolts from the left",
            "Sector_spacer": "a full ring on the chamber tube with the sector's own sweep carved through (the pawl boss's road), from the sector's ring to the QEV body's face: fixes its seat; the length is the model's span - file to fit on a printed stack",
            "Hammer_axle": "steel rod Ø8 x %.1f (or an M8 bolt's shank), supported by both walls; right end 0.5 mm below the outside face" % (SHAFT_Y[1] - SHAFT_Y[0]),
            "Guide_rod": "steel rod Ø3 x 94: the slider's guide. Coaxial Ø3.3 passage open through both ceiling and floor", "Trigger": "PETG lever; finger face 24 mm toward the grip, in the middle of the guard. Print on its broad negative-y side; separate rigid pin carrier clamped against a broad face by M3 x 12 + nut. Pivot: M3 stud",
            "Tie_rods": "4 x M4 x 50 socket head + nut, rubber O7 x 1.5 + steel O9 x 0.8 washer under each head (as v1.1); the heads stand 6.3 mm off the cap's back face - the frame's pockets are cast for them",
            "Lock_bolts": "2 x M3 x 30 self-tappers into the body's face pilots, heads in the frame's front pockets (drawn as a O5.5 x 3 envelope)"}
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
