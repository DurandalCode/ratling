# -*- coding: utf-8 -*-
"""
Gatling breech mechanism (not a freeze).

Stroke from linear_breech (65.8 mm) -> angle->stroke law -> outboard cam liner ->
six phases -> AirTAC on each carriage, fixed firing ramp -> star feed geared
to the pack (rim on the breech clamps + fixed train) with a gate in the neck ->
helical guard -> side crank with arm and knob -> air: MQR in the pack's tail on a
61812, hose from the receiver through a dead-man -> flintlock grip with one
two-stage lever (air, then balls) for the left hand -> mass and centre of
gravity -> chainsaw-style wrap handle in its plane, strap lugs either side, tripod socket under it.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism.py').read())"

The full-turn clearance sweep (every station part against every fixed part,
every 3 deg; neighbours every 5 deg of phase) and the joint audit are separate
runs in parallel freecadcmd workers; since 2026-11-22 they read the bodies from
the cache this build writes at the end of its checks (gatling/breech_cache.py,
+14 s) and remember their results by the bodies' BREP hashes: ~2.7 and ~1.5 min
from scratch, seconds again:

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism_sweep.py').read())"
    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_joints.py').read())"

Pack R / casing may move if parts will not seat. No wheeled carriage; no
full-length tube. Exports: exports/gatling_breech_mechanism/

The model is built in its final pose: hopper and star on +X (top), firing
sector at the bottom (-X), crank on +Y (the shooter's right; it was on -Y
until 2026-11-20). Pack angle phi (0 = FIRE) sits at
world angle phi + 180.

2026-11-20 (owner's choice of the three layouts in docs/gatling.md, plan
questions 2-4):
- The AirTAC rides its carriage on a bracket behind the bridge, plunger aft,
  fittings to the sides. Its line A to the pilot is short and rigid (as on the
  bench); the supply line R flexes with the stroke. The six valves no longer
  meet at the axis (the old hub overlap was 11.3 cm3 per pair at any R).
- A fixed ramp on the firing sector presses the plungers at the closed
  position: touch 332 -> 28 deg, 2.5 mm full press on 340..20. The
  trigger pulls the ramp forward into reach; let go, a spring takes it 4 mm
  aft and no plunger is pressed. The press pushes the QEV onto its stop.
  (Since the controls moved to the rear grip the ramp is fixed: below.)
- The star of feed_bench.py replaces the auger. A geared rim on the breech
  clamps (it is the rear barrel-plate, ahead of the clamps; the old plate
  overlapped the closed QEVs by 22 cm3) drives it through a fixed train
  120 -> 40 | 18 -> 18 -> 27: three external meshes, -2. A shaft from behind
  the pack cannot reach the star: the liner and the fingers take r 101.5..107.
- The guard follows the ball while the station closes (202..279 deg) and
  stays inside the breech clamp's feed notch.
- The carriage and the nose guide ride the bought Al tubes, as on the bench:
  the printed stroke-rail cage sat on their bores (1745 / 2312 mm3) and is
  gone. The tubes end in a rear disk on the axle.
- The liner groove is blind (the groove used to cut through the wall and
  split the drum in two rings); the liner is the frame around the cam, and
  the spars start ahead of it, off the fingers' orbit.
- Hollow axle Al 38 x 1.5 on two 6808 (40 x 52 x 7, 1 mm shim); the six
  1/8" (6 mm) supply lines run inside it to the MQR rotor, so no rotating
  line crosses a fixed part (the old lines cut the bearing disk, buffer and
  frame).
- No buffer tank. The Ø80 x 150 tank (0.75 L) gave ~0.15 L at a 0.2 bar
  droop, under one shot (two chamber volumes of free air, 0.2..0.4 L), so the
  burst was held by the source and hose anyway. A thick hose from the
  receiver comes in on -Y, through the dead-man inline on the supply stub,
  into the MQR stator.

2026-11-20, pack drive from the crank: the crank shaft runs across the
barrels on +Y (the shooter's right) at the middle of the closed QEVs (x 0,
z 75). It is drawn on -Y and mirrored (CRANK_SIDE): the frame is symmetric
and the rim maps onto itself, so the meshes hold. A bevel pair
20:20 m 2 turns it onto a lay shaft parallel to the axle at r 135, outside
the frame (the stations sweep r <= 96.3 there and the frame spar on that side takes
r 100..108); a gear 60 (m 1.5) on that shaft meshes the star-drive rim 120.
One crank turn = 60 / 120 = 0.5 pack turn, so 60 rpm gives 3 shots/s; the
top of the crank went aft, towards the shooter (turned forward since: below). The first draft (crank at
z 302 ahead of the clamps, bevel 48:16, pinion 20 at r 105) moved here at the
owner's request; at r 105 the long shaft would cut the spar and front ring.
Shafts Ø8 on 608s: the pair's bracket (two plates) sits on the spar, the
rim-gear boss on the front ring. The bevels use gears.bevel_gear(back_cone=
True) (full-height teeth; the planar form is half height at 45 deg and gave a
16:48 pair 0.2 mm teeth). Tooth counts are a draft until the bench measures
the torque. A reference body (knob orbit R 80, fist R 45 x 100) keeps room
for the hand; the arm and knob are drawn in it (stage 6, below).

2026-11-20, controls at the rear (stage 6; owner: balls and air from one
hand, behind, an old flintlock look). The firing ramp stays in the press
position on a block inside the liner (2 x M3 into heat-set inserts, blind
holes): every station on 330..30 fires while the air is on. A wooden grip
curls down behind a rear plate like a flintlock pistol's, with a brass pommel;
the plate (R 50) also carries the MQR stator, four struts tie it to the rear
bearing disk's rim (the plate used to float). One big lever (a 14 x 24 blade,
91 mm) follows the grip's front like a fire extinguisher's, pivoted at the top
behind the plate, 15 deg to the grip (22 mm at its free end by the pommel).
Stage 1, 0..5 deg: the lever presses the dead-man in the grip through a pusher
with an over-travel spring (3 mm valve stroke at 5 deg, 8 mm over-travel by
15); the pusher is placed by the real contact (its end meets the tilted blade
at its edge first). Stage 2, 5..15 deg: the lever's short tail inside the
grip's root takes up 3 mm of cable slack and then draws the gate pin 6 mm out
of the feed neck (Bowden 654 mm, along the top on the left, through the
plate); let go and a spring puts the pin 5 mm across the Ø25.4 neck. The
receiver's hose comes into the pommel, the valve's outlet runs up the grip and
through the plate into the stator's rear port. The trigger under the liner,
the D-grip with bails and the musket stock drawn earlier the same day are
gone. The gun was 1222 x 330 x 418 then (the hose hanging from the pommel set
the height).

2026-11-20, stage 6 closed, stage 7 (centre of gravity, carry, strap):
- Crank arm R 80 on the shaft end: a hub Ø22 on the Ø8 shaft (M4 set screw onto
  a flat), 8 mm off the bearing boss; the knob Ø26 x 92 is a sleeve on its own
  Ø6 steel pin (head inboard of the arm, nut outboard, 1 mm each end, bore
  0.25 a side), so it turns in the hand. It lies inside the hand's reference
  body; over a crank turn (10 deg steps) it is > 5 mm from everything fixed and
  from the pack, and the sweep meets every crank pose with every pack pose.
- Mass by body: printed PETG as a solid skin plus the profile's infill (skin =
  V (1 - exp(-A t / V)), t 1.9, fitted to tools/print_mass.py on 19 of these
  bodies: 6 % a body, 1 % the sum); airtight QEV parts 100 %, flow 1.05;
  steel barrels, stubs, shafts, rods; Al chambers, rails, axle; a wooden grip;
  bought parts by catalogue or estimate (MS_EST). 8.28 kg with the handle and
  the tripod pad, CG (8, 7, 95) (8.30 with the longer lay shaft, below): z 95 is the middle of the closed QEVs, 20 mm
  ahead of the crank axis. Balls, skin, bolts and the receiver hose are not
  counted.
- The hopper's cup stands on top just ahead of the CG (z 115..246), and the
  only fixed parts on top are the liner and the star-drive gearbox, so the
  carry handle is a bridge: posts on the liner (z -65) and on the gearbox
  (z 256, a tab down its front face), CG +- 160, bar Ø24 at x 261 so the fist
  round it clears the cup by 5 mm. A steel ring round each post takes the
  strap, so the strap points are either side of the CG at the same distance.
  The old handle at a fixed z (the middle of liner and front plate) and the
  loops on nothing are gone. The gun is now 1222 x 426 x 467: the knob sets
  the width (y +314), the handle the height.
- Tripod pad (owner: the tripod is not chosen, a socket for a 5 cm ball): a
  keel 30 x 15 along the bottom from the liner (z -68) to the front ring
  (z 214), outside the liner's radius, and a boss Ø70 on it under the CG with a
  spherical socket for a Ø50 ball, 15 deep (mouth Ø46, 0.25 clearance): the
  ball sits in it below its equator and the tripod's clamp holds it. The
  ball with a post tilted 20 deg either way clears the gun by > 5 mm. 195 g.
- The crank turns clockwise seen from its knob, its top forward (owner): the
  forward way of a drill or a flexible shaft on the shaft end (many flexible
  shafts run one way only), the way the Gatling's right-hand crank turned, and
  the faster way for a right hand. The lay bevel moved behind the apex, teeth
  forward; the lay shaft runs forward 8.6 mm past the crank bevel and shaft,
  and plate A with its 608 sits behind the lay bevel. The mesh check catches
  a wrong sign (88.7 mm3 overlap against 0). 8.30 kg, CG (8, 7.5, 94.5).

2026-11-23, shorter tail (owner: the enclosed part was longer than the barrels): the hollow
axle, both 6808 and their disks are gone. The MQR's rotor sits in the rear rail disk on a TPU
pad, its radial ports feed the six R lines directly; the stator stands behind it on the rear
plate, ports as on the drawing (a helix, 60 deg apart, not a row). The pack's tail runs in a
floating 61812 on the disk's sleeve round the MQR, in a printed cage on four legs off the
spider. The front 61836 became a printed slide ring round the hub's journal, PTFE tape on the
journal (owner: no big bought bearing); FRONT_BRG_NAME = "KA070XP0" or "61836" brings a bearing back.

2026-11-21, fasteners (owner: every printed part held to its neighbour with M3 x 6 /
20 / 50 and nuts, no inserts or glue; the frame on bare M6 studs). The joint audit
(gatling/breech_joints.py) found the parts standing on each other, and more:
- The pack hung on the two 6808 at the rear: even on a stiff hub the rim sagged
  0.58 mm at 1 g (1.75 at 3 g) against the m 1.5 mesh's 0.375 root clearance. A
  61836 (180 x 225 x 22) now carries its front, ahead of the star-drive box (behind
  the rim lie the guard and the front ring, in the rim's planes gears A and 60). The
  hub is one print: the rim, the lower halves of the six breech clamps, a tube
  forward inside the box, the bearing's seat. The upper clamp halves bolt on (2 x M3
  x 20 on lugs). The rails end in blind sockets in the hub's clamp feet and in the
  rear disk (16 thick; its line R slots used to cut it in six), the forward collars
  are gone from the pack, the muzzle plate pinches the barrels.
- The frame: bare M6 studs at r 118.5 with a nut either side of every element (6808
  disks -> liner; liner -> front ring -> bearing housing; front ring -> box; inclined
  struts to the rear plate); the printed spars and struts are gone. The liner is two
  halves split at 0 / 180 (the fingers go in with the stations): M3 x 20 lug pairs at
  its rear end, the carry base and the keel across it at the front.
- The groove is one channel swept along the law and open to the bore (it was 36
  dimples, their mouth Ø3.3 under the Ø5 finger). The finger is a pin in a blind hole
  in the valve bracket's boss, captured by the groove's floor; the bracket sits on
  both tie studs behind the bridge (it hung on one, 1 mm off the carriage) and holds
  the AirTAC by 2 x M3 x 20 through its holes (18 mm body: 2.0 of the nut's 2.4 mm of
  thread, the one fastener short of its window).
- Ramp on ears outside the plungers' track, block through the liner wall, on nuts.
  Carry handle: front post on the bearing housing (the CG moved forward), bases bolted.
  Keel, guard (two webs to the front ring), feed head (a boss on its web), cup and gate
  housing (one pair of bolts), star-shaft collar, gears A + B one cluster on a fixed pin,
  the idler's pin out of gear A's plane (it ran 2 mm into it), the crank arm across its
  hub (was an M4 set screw), the gear-60 bracket's foot, the front 6808's retainer and
  the axle's collars, the coupling, the grip's root in a cup on the rear plate, the MQR's
  own M4s. The axle's windows follow the lines (they crossed its wall, 293 mm3).
80 x M3 x 20, 15 M6 studs (2.64 m, 74 nuts), 6 x M4; 11.25 kg, CG (5.0, 4.5, 96.4).

2026-11-21, fasteners, second pass (joints that were only declared now hold; the joint audit
pushes every part on a shaft along its axis, AXIAL in breech_joints.py, limit 1 mm):
- The feed head had dropped out of the model in the first pass: removeSplitter() on its cut
  for the cup's bolts gave a broken shape and the fuse with its web boss kept 1 cm3 of 57. The
  fastener cuts go through cut_fast() now (refined, unrefined, one cutter at a time: the first
  sound result; a check lists each). The box stood on two nut stacks in one 8.4 mm gap: it is on
  bosses now. The front ring was cut through at the top by the star shaft's hole.
- Star shaft: a pad closes the front ring at the top and takes the locating 608 (cover on
  2 x M3 x 20); the star is pinned to the shaft by its hub (the old collar), the hub's spigot, a
  steel spacer and the collar ahead of the pad clamp the inner race (0.15 float); a second 608
  floats in the box's rear plate. Star gear: hub and boss 0.3 off the box (was 3.0 loose between
  the faces of the turning hub). A + B: bosses 0.3 off the plates, the pin in a blind hole and
  0.5 under the 61836's retainer. Idler: on a tube 6 x 1 clamped by an M3 x 20 from inside (head
  in a recess of the idler, nut in a boss ahead of the box).
- Lay shaft: a collar behind plate A and gear 60 pinned on a hub, each on a 608's inner race
  through a spigot; the lay bevel's thrust on plate A's 608. Crank shaft: the bevel pinned, its
  thrust on the inner 608, a spacer between the outer 608 and the arm's hub (it could be pulled
  out through its 608s). The 608s of the crank side are trapped in their pockets by 1 mm lips.
- 6808s: the races are bodies; each outer race between a lip of its disk and a retainer's spigot
  (the front retainer stood 5.5 off its race, the rear race was held by its press alone).
- Grip: two halves split at y 0 (the dead-man, the cable and the hoses lie between them), 2 x M3
  x 20 across where they clear every channel; the lever's pivot is a brass tube clamped by an
  M3 x 50 in 12 mm lugs (a bare pin in 4 mm lugs); the wire ends in a barrel nipple across the
  tail; the Bowden housing sits 5 mm deep in a seat under the gate.
- Collector 1 -> 6 (owner): a bought manifold on a tab of the rear plate, six hoses to the
  stator's M5 ports (their row on +y is assumed until the MQR6 arrives).

2026-11-22, EVA skin (owner: a skin that closes the whole pack, then: on to the grip, no cone at
the back, a cylinder to the MQR; contact glue, no fixing points):
- A tube of EVA 5 mm, bore r 127 on the stud lugs' tips, from the rear plate's aft face to the
  front bearing housing's front face (658 mm), the seam under the keel; 0.51 m2, ~256 g; an EVA end
  cap on the rear plate's aft face, R 54..132, its bore clear of the grip and the lever's squeeze.
- The rear frame is a cylinder: the four inclined studs from the rear 6808 disk to the plate R 50
  are gone; the bay-1 studs run on straight to the rear plate, now a spider Ø254 (the hub R 50,
  four spokes to the studs' lugs, a rim for the skin). M6 studs 11, 2479 mm. The inclined studs
  were counted twice in the mass (steel in the fasteners and PETG "struts"); not any more.
- It is glued on printed lands: a 2 mm hoop on ribs in the liner's two lug bands (the rear one
  open 30 deg either side of the split, where the key to the halves' bolts comes in), on both 6808
  disks and on the front ring (open on top for the box and the feed head), the spider's rim, and
  the bearing housing and its retainer, Ø250 -> Ø254. All of them stay within Ø254 for the P2S bed.
- The handle and the tripod socket are placed by the CG with the skin on (a plain tube and cap
  estimate): 0.28 kg aft moved it 5.5 mm. The rear post moved 11 mm aft and its base gives way
  round the liner's split lug on top (it ran 1 mm into it).
- Whatever crosses the tube gets a window (its footprint, 2 mm round it; turning parts by their
  sweep): the box and the feed head on top, the crank drive on the right (plate A, the lay shaft in
  an 11 mm slot, gear 60), the rear carry post with its bolts' keys (the handle goes on after the
  skin), the gate cable, the tripod boss. EVA narrower than
  12 mm between windows or to an edge goes with them; a closed window round a part that will not
  thread through gets a slit to the nearest edge. The pattern, 1:1 seen from outside:
  eva_skin_pattern.svg.
- Around it: the gate cable's run over the liner 6 mm lower (it reached r 128.1); the rear strap
  ring lies on the skin; the keel's corners 0.3 off the hoops; the front ring's hoop gives way where
  a bolt or its key passes (the guard webs, the keel).
"""
import importlib
import math
import os
import sys
import time

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
import ratling.fasteners as FA
for _m in (G, FV, GR, FA):
    importlib.reload(_m)

try:
    BREECH_MECH_LIBRARY
except NameError:
    BREECH_MECH_LIBRARY = False     # True: build + fast checks only (breech_mechanism_sweep.py)

OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
V = App.Vector
O = V(0, 0, 0)
ZA = V(0, 0, 1)

TARGET_L = 750.0                # closed station, rear plug to muzzle, without the breech trough
BARREL_SHOW_DEFAULT = 160.0
N = 6
R_PACK = 67.00                  # = breech_pack PINNED_R; rail feet need >= 66.3
CASE_OD_START = 218.0           # previous frame envelope (2026-11-19)
L_START = 1033.0                # previous overall length
CLEAR = 0.5
PLATE_T, PLATE_LIP, PLATE_RIM = 14.0, 1.5, 3.0

CAM_WALL_IN = 2.5               # liner wall inside the groove centre (as before)
GROOVE_FLOOR = 2.0              # material behind the groove bottom (blind groove)
FOLLOWER_OD = 5.0
FOLLOWER_CLEAR = 0.5
CAM_Z_PAD = 8.0
CAM_CLEAR_Z = 2.0
EAR_ENV = 33.0

FIRE_A, FIRE_B = 330.0, 30.0
OPEN_A, OPEN_B = 30.0, 120.0
LOAD_A, LOAD_B = 120.0, 240.0
CLOSE_A, CLOSE_B = 240.0, 330.0

_T0 = time.time()


def _tick(msg):
    print("[%5.0f s] %s" % (time.time() - _T0, msg), flush=True)


_tick("load linear_breech…")
GATLING_LINEAR_BREECH_LIBRARY = True
PACK_STATION = True
# 2026-11-22 (the owner): the pellet lies in a fixed trough on each breech clamp, not on the QEV's
# nose; the trough adds TRAY_L between the QEV's stop and the barrel, the barrel keeps its length.
BREECH_TRAY = True
TRAY_PACK_R = R_PACK
SHOW_OPEN = False
BARREL_SHOW = BARREL_SHOW_DEFAULT
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
TARGET_L = 750.0 + TRAY_L
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin
BARREL_SHOW = TARGET_L - (z_bf - Z_AFT_CLIP)
assert BARREL_SHOW > 50.0
print("reload BARREL_SHOW=%.1f…" % BARREL_SHOW, flush=True)
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), globals())
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
NAME = "gatling_breech_mechanism"
Z_AFT_CLIP = qev_closed["Rear_plug"].BoundBox.ZMin

BENCH_STROKE = STROKE
assert abs(BENCH_STROKE - (FIT_IN_BARREL + PELLET_D + STROKE_MARGIN)) < 1e-6
print("STROKE=%.1f" % BENCH_STROKE, flush=True)


def shifted(shape, dz):
    s = shape.copy()
    s.translate(V(0, 0, dz))
    return s


def tube(od, idd, z0, z1, x=0.0, y=0.0):
    return G.cyl(od, z0, z1, x, y).cut(G.cyl(idd, z0 - 1, z1 + 1, x, y))


def cam_u(phi_deg):
    phi = phi_deg % 360.0
    if phi >= FIRE_A or phi <= FIRE_B:
        return 0.0
    if OPEN_A < phi < OPEN_B:
        t = (phi - OPEN_A) / (OPEN_B - OPEN_A)
        return 0.5 * (1.0 - math.cos(math.pi * t))
    if LOAD_A <= phi <= LOAD_B:
        return 1.0
    if CLOSE_A < phi < CLOSE_B:
        t = (phi - CLOSE_A) / (CLOSE_B - CLOSE_A)
        return 0.5 * (1.0 + math.cos(math.pi * t))
    return 0.0


def cam_dz(phi_deg):
    return -BENCH_STROKE * cam_u(phi_deg)


def phase_name(phi_deg):
    phi = phi_deg % 360.0
    if phi >= FIRE_A or phi <= FIRE_B:
        return "FIRE"
    if OPEN_A < phi < OPEN_B:
        return "OPEN"
    if LOAD_A <= phi <= LOAD_B:
        return "LOAD"
    if CLOSE_A < phi < CLOSE_B:
        return "CLOSE"
    return "?"


def wdeg(phi_deg):
    """World angle (deg, from +X) of pack angle phi: FIRE at the bottom (-X)."""
    return phi_deg + 180.0


def polar(r, phi_deg, z=0.0):
    a = math.radians(wdeg(phi_deg))
    return V(r * math.cos(a), r * math.sin(a), z)


def place(shape, phi_deg, dz=0.0):
    """Station-local shape (+Y radial out, +Z muzzle) at pack angle phi."""
    s = shape.copy()
    if dz:
        s.translate(V(0, 0, dz))
    a = wdeg(phi_deg)
    s.rotate(O, ZA, a - 90.0)
    s.translate(V(R_PACK * math.cos(math.radians(a)), R_PACK * math.sin(math.radians(a)), 0))
    return s


def rot(shape, deg, centre=O):
    s = shape.copy()
    s.rotate(centre, ZA, deg)
    return s


def _near(ba, bb_, pad):
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad,
                       ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    return ba2.intersect(bb_)


GAP_BOX_MARGIN = 1.5


def _box_dist(a, b):
    dx = max(0.0, a.XMin - b.XMax, b.XMin - a.XMax)
    dy = max(0.0, a.YMin - b.YMax, b.YMin - a.YMax)
    dz = max(0.0, a.ZMin - b.ZMax, b.ZMin - a.ZMax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def gap(a, b, pad=2.0):
    """Min distance, solid by solid with a bounding-box shortcut (99 = far apart)."""
    if not _near(a.BoundBox, b.BoundBox, pad):
        return 99.0
    sa = a.Solids or [a]
    sb = [(y, y.BoundBox) for y in (b.Solids or [b])]
    bb_b = b.BoundBox
    cand = []
    for x in sa:
        bx = x.BoundBox
        if not _near(bx, bb_b, pad):
            continue
        for y, by in sb:
            if _near(bx, by, pad):
                cand.append((_box_dist(bx, by), x, y))
    # 2026-11-22: nearest boxes first; a pair whose boxes are farther apart than the best gap so
    # far (by GAP_BOX_MARGIN: a box from a 0.5 mm tessellation may sit inside its shape) cannot
    # lower it and is not measured. Same result, fewer distToShape.
    cand.sort(key=lambda c_: c_[0])
    g = 99.0
    for bd, x, y in cand:
        if bd - GAP_BOX_MARGIN >= g:
            break
        g = min(g, x.distToShape(y)[0])
    return g


def gap_solids(a_list, b_list, pad=2.0):
    """Min gap between two lists of solids, pairwise with bbox prefilter."""
    g = 99.0
    for a in a_list:
        for b in b_list:
            g = min(g, gap(a, b, pad))
    return g


def r_max(shape, defl=0.5):
    pts = shape.tessellate(defl)[0]
    return max(math.hypot(p.x, p.y) for p in pts) if pts else 0.0


def tube_path(points, r):
    """Hose as straight cylinders through the points (sketch of the route)."""
    segs = []
    for p0, p1 in zip(points[:-1], points[1:]):
        v = p1.sub(p0)
        if v.Length > 0.5:
            segs.append(Part.makeCylinder(r, v.Length, p0, v))
            segs.append(Part.makeSphere(r, p1))
    return Part.makeCompound(segs)


def path_len(points):
    return sum((b - a).Length for a, b in zip(points[:-1], points[1:]))


CUT_LOG = []                    # (part, volume before, after, ok, how): fastener cuts and the fuses after them


def _sound(s, lo, hi):
    return s.isValid() and len(s.Solids) >= 1 and lo <= s.Volume <= hi


def cut_fast(shape, cutters, what, split=True):
    """shape minus the fastener cutters (shapes or Fasteners), checked.

    The cut must stay valid and lose no more than the cutters hold. 2026-11-21: the feed head
    came out of its cut sound, but removeSplitter() on it gave an empty or invalid shape, and
    the next fuse kept a 1 cm3 boss of its 59 cm3 (the neck, the shroud and the cup's ring were
    gone from the model). So: the compound cut refined, then unrefined, then one cutter at a
    time, refined and not; the first sound one is kept.
    """
    cs = [getattr(c, "cutter", c) for c in cutters]
    v0 = shape.Volume
    lo, hi = v0 - sum(c.Volume for c in cs) - 1e-3, v0 + 1e-3
    raw = shape.cut(Part.makeCompound(cs))
    tries = [("refined", lambda: raw.removeSplitter()), ("unrefined", lambda: raw)] if split else [("unrefined", lambda: raw)]
    seq = []

    def _seq():
        if not seq:
            t_ = shape
            for c in cs:
                t_ = t_.cut(c)
            seq.append(t_)
        return seq[0]
    if split:
        tries.append(("one by one, refined", lambda: _seq().removeSplitter()))
    tries.append(("one by one", _seq))
    for how, f in tries:
        out = f()
        if _sound(out, lo, hi):
            CUT_LOG.append((what, v0, out.Volume, True, how))
            return out
    CUT_LOG.append((what, v0, out.Volume, False, how))
    return out


def fuse_sound(shape, other, what):
    """shape fused with other, refined if refining keeps it sound (as cut_fast)."""
    v0 = shape.Volume
    raw = shape.fuse(other)
    for how, out in (("refined", raw.removeSplitter()), ("unrefined", raw)):
        if _sound(out, v0 - 1e-3, v0 + other.Volume + 1e-3):
            CUT_LOG.append((what, v0, out.Volume, True, how))
            return out
    CUT_LOG.append((what, v0, out.Volume, False, how))
    return out


# ============================================================ station (pack variant)
# Fasteners (2026-11-21, docs/gatling.md "Крепёж"): M3 x 6 / 20 / 50 with nuts in hex
# sockets, M6 studs for the frame; ratling/fasteners.py. Station-local ones are kept
# local and placed per station: ST_FAST move with the carriage, PK_FAST stay with the pack.
ST_FAST, PK_FAST = [], []
# The rails end in blind sockets: in the rear disk and in the feet of the hub's breech
# clamp halves (until 2026-11-21 they ran to the muzzle through plain bores in a 6 mm disk
# that the line R slots cut in six). The forward collars only held the barrels to the
# rails and are gone from the pack: the hub and the front plate hold the barrels.
REAR_DISK_Z0, REAR_DISK_Z1 = -137.0, -121.0     # behind the open carriage and pilot fitting
REAR_DISK_R = 46.0
RAIL_SOCKET = 10.0                              # rail end in the rear disk
# 2026-11-23: the MQR's rotor sits in the rear disk (docs/gatling.md, "Короткий хвост"). Face 9 mm
# behind the disk's front: a 6 mm web and a 3 mm TPU pad. Its radial M5 ports lie on the disk's
# aft face; the fittings reach r 35, inside the race-side lip of the rear bearing's cage.
Z_ROTOR1 = REAR_DISK_Z1 - 9.0
MQR_PORT_Z = 7.0                                # rotor ports from the rotor face (drawing)
Z_ROTOR_PORT = Z_ROTOR1 - MQR_PORT_Z
ROTOR_FIT_D, ROTOR_FIT_L = 12.0, 12.0           # M5 push-in for the 6 mm line, est.
R_ROTOR_FIT = 23.0 + ROTOR_FIT_L
HUB_RAIL_SOCKET = 20.0                          # rail end in a clamp foot of the hub
z_rail_pk0 = REAR_DISK_Z1 - RAIL_SOCKET
z_rail_pk1 = z_clamp0 + HUB_RAIL_SOCKET
rails_pack = rails_s.common(Part.makeBox(400, 400, z_rail_pk1 - z_rail_pk0, V(-200, -200, z_rail_pk0)))
# The valve bracket goes on both tie studs behind the carriage bridge: the rear washers
# and nuts move aft by its plate, the studs get that much longer.
BRACKET_T = 5.0
z_carr_aft = qev_closed["Carriage"].BoundBox.ZMin
assert abs(z_carr_aft - (z_ry - CARR_T)) < 1e-6, "pack carriage: webs flush with the bridge"
_hw = qev_closed["Tie_rods"]
_hw_aft = _hw.common(Part.makeBox(100, 100, 100, V(-50, -50, z_carr_aft - 100)))
_hw_aft.translate(V(0, 0, -BRACKET_T))
qev_closed["Tie_rods"] = G.fuse_all([_hw_aft, _hw.common(Part.makeBox(100, 100, 400, V(-50, -50, z_carr_aft)))]
                                    + [G.cyl(TIE_D, z_carr_aft - BRACKET_T - 0.1, z_carr_aft + 0.1, *at(TIE_R, a)[:2])
                                       for a in TIE_ANGLES]).removeSplitter()
STUD_L_PACK = STUD_L + BRACKET_T
# Breech clamp: the lower half (toward the axle) is printed with the rim (the hub, below);
# the upper half bolts onto it, 2 x M3 x 20 across the split on lugs at the old bolt
# lines (the old flush holes went through a crescent of wall with no seat for a head).
_cl = sorted(barrel_clamp.Solids, key=lambda s_: s_.BoundBox.Center.y)
clamp_lower, clamp_upper = _cl[0], _cl[1]
CLAMP_LUG_X, CLAMP_LUG_Y = (CLAMP_BOLT_X - 3.2, CLAMP_BOLT_X + 4.4), 12.5
z_clamp_lug0 = z_clamp0 + 18.0                  # the feed notch takes the upper half's first 18 mm
z_clamp_bolt = z_clamp1 - 5.0
for _sx in (-1, 1):
    _x0, _x1 = sorted((_sx * CLAMP_LUG_X[0], _sx * CLAMP_LUG_X[1]))
    clamp_upper = clamp_upper.fuse(Part.makeBox(_x1 - _x0, CLAMP_LUG_Y - CLAMP_GAP / 2, z_clamp1 - z_clamp_lug0,
                                                V(_x0, CLAMP_GAP / 2, z_clamp_lug0)))
    clamp_lower = clamp_lower.fuse(Part.makeBox(_x1 - _x0, CLAMP_LUG_Y - CLAMP_GAP / 2, z_clamp1 - z_clamp_lug0,
                                                V(_x0, -CLAMP_LUG_Y, z_clamp_lug0)))
_bore = G.cyl(BARREL_OD + 0.3, z_clamp0 - 1, z_clamp1 + 1)
clamp_upper, clamp_lower = clamp_upper.cut(_bore).removeSplitter(), clamp_lower.cut(_bore).removeSplitter()
for _sx in (-1, 1):
    _f = FA.m3("breech clamp", V(_sx * CLAMP_BOLT_X, 0, z_clamp_bolt), V(0, -1, 0), [clamp_upper, clamp_lower],
              clip=(-CLAMP_LUG_Y - 1.0, CLAMP_LUG_Y + 0.01))
    clamp_upper, clamp_lower = clamp_upper.cut(_f.cutter).removeSplitter(), clamp_lower.cut(_f.cutter).removeSplitter()
    PK_FAST.append(_f)
# Rail sockets in the lower half's feet: blind from behind, HUB_RAIL_SOCKET deep.
for x, y in rail_centers():
    clamp_lower = clamp_lower.fuse(G.cyl(RAIL_HOLE + 0.4, z_rail_pk1, z_clamp1, x, y))
clamp_lower = clamp_lower.removeSplitter()
# Nose clamp: the same, 2 x M3 x 20 on lugs either side, head on the outer (upper) half.
NOSE_LUG_X, NOSE_LUG_Y = (_nose_bolt_r - 3.2, _nose_bolt_r + 3.6), 9.5
_nl, _nu = nose_lower, nose_upper
for _sx in (-1, 1):
    _x0, _x1 = sorted((_sx * NOSE_LUG_X[0], _sx * NOSE_LUG_X[1]))
    _nu = _nu.fuse(Part.makeBox(_x1 - _x0, NOSE_LUG_Y - NOSE_GAP / 2, z_nose1 - z_nose0 - 12.0,
                                V(_x0, NOSE_GAP / 2, z_nose0 + 6.0)))
    _nl = _nl.fuse(Part.makeBox(_x1 - _x0, NOSE_LUG_Y - NOSE_GAP / 2, z_nose1 - z_nose0 - 12.0,
                                V(_x0, -NOSE_LUG_Y, z_nose0 + 6.0)))
_nbore = G.cyl(CH_OD + 0.5, z_nose0 - 2, z_nose1 + 2)
_nu, _nl = _nu.cut(_nbore).cut(nose_rod_cut).removeSplitter(), _nl.cut(_nbore).cut(nose_rod_cut).removeSplitter()
for _sx in (-1, 1):
    _f = FA.m3("nose clamp", V(_sx * _nose_bolt_r, 0, z_mid), V(0, -1, 0), [_nu, _nl],
              clip=(-NOSE_LUG_Y - 1.0, NOSE_LUG_Y + 0.01))
    _nu, _nl = _nu.cut(_f.cutter).removeSplitter(), _nl.cut(_f.cutter).removeSplitter()
    ST_FAST.append(_f)
nose_upper, nose_lower = _nu, _nl
qev_closed["Nose_clamp"] = Part.makeCompound([nose_lower, nose_upper])
qev_slide = [qev_closed[k].copy() for k in qev_closed]
fixed_station = [rails_pack, clamp_upper, fixed_barrel]

# --- AirTAC M3R110 on the carriage: bracket on the bridge's aft face, plunger aft,
# T (27) across the station, fittings to the sides (A to -x, R and P to +x).
A_W, A_T, A_L = AIRTAC["W"], AIRTAC["T"], AIRTAC["L"]
PL_D, PL_L = AIRTAC["plunger"]
VALVE_Y = 16.5                  # body y 7.5..25.5: 1.0 off the pilot fitting and the finger
z_valve1 = z_carr_aft - BRACKET_T
z_valve0 = z_valve1 - A_L               # stem face
z_tip_free = z_valve0 - PL_L            # plunger tip, free, station closed
valve_body = Part.makeBox(A_T, A_W, A_L, V(-A_T / 2, VALVE_Y - A_W / 2, z_valve0))
valve_fit = Part.makeCompound([
    Part.makeCylinder(AIRTAC["straight"]["A"][0] / 2, AIRTAC["straight"]["A"][1],
                      V(-A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["A"]), V(-1, 0, 0)),
    Part.makeCylinder(AIRTAC["straight"]["R"][0] / 2, AIRTAC["straight"]["R"][1],
                      V(A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["R"]), V(1, 0, 0)),
    Part.makeCylinder(AIRTAC["silencer"][0] / 2, AIRTAC["silencer"][1],
                      V(A_T / 2, VALVE_Y, z_valve0 + AIRTAC["ports"]["P"]), V(1, 0, 0))])
valve_plunger = Part.makeCylinder(PL_D / 2, PL_L, V(0, VALVE_Y, z_tip_free))
# Bracket (2026-11-21): a plate on both tie studs behind the bridge (it used to hang on
# the 30 deg stud alone, 1 mm off the carriage), an outer wall along the valve's wide
# face with the nut sockets for two of its three Ø3.3 holes, and the finger's boss.
# Valve holes (catalogue M3B110, pistol/hammer_layout.py): across the 27 face at x -9 /
# +9 31 mm from the plunger face and x 0 at 15; the -9 one is skipped, line A runs under
# it. The body is 18 thick: M3 x 20 from the inner face, the nut on the outer face in
# its socket, 2.0 of its 2.4 mm of thread taken (no stocked length fits 18 + a nut).
VALVE_HOLES = [(9.0, 31.0), (0.0, 15.0)]
WALL_T = FA.SOCKET_T + FA.FLOOR_MIN
y_wall0, y_wall1 = VALVE_Y + A_W / 2, VALVE_Y + A_W / 2 + WALL_T
z_wall0 = z_valve0 + min(h for _, h in VALVE_HOLES) - 6.0
FINGER_BOSS_W, FINGER_BOSS_Y1, FINGER_BOSS_L = 19.0, 32.0, 11.0
z_cam1 = z_carr_aft - CAM_CLEAR_Z
z_tip0 = z_cam1 - CAM_Z_PAD * 0.5
_plate = G.fuse_all([G.cyl(CH_OD + 2.0, z_valve1, z_carr_aft)]
                    + [G.cyl(2 * CARR_EAR_R, z_valve1, z_carr_aft, *at(TIE_R, a)[:2]) for a in TIE_ANGLES]
                    + [Part.makeBox(A_T + 2.0, y_wall1 - (VALVE_Y - A_W / 2 - 1.0), BRACKET_T,
                                    V(-A_T / 2 - 1.0, VALVE_Y - A_W / 2 - 1.0, z_valve1))])
_plate = _plate.cut(G.cyl(PILOT_PASS_D, z_valve1 - 1, z_carr_aft + 1))
for a in TIE_ANGLES:
    _plate = _plate.cut(G.cyl(TIE_HOLE, z_valve1 - 1, z_carr_aft + 1, *at(TIE_R, a)[:2]))
_wall = Part.makeBox(A_T, WALL_T, z_valve1 - z_wall0, V(-A_T / 2, y_wall0, z_wall0))
_fboss = Part.makeBox(FINGER_BOSS_W, FINGER_BOSS_Y1 - y_wall0, FINGER_BOSS_L,
                      V(-FINGER_BOSS_W / 2, y_wall0, z_carr_aft - FINGER_BOSS_L))
valve_bracket = G.fuse_all([_plate, _wall, _fboss]).removeSplitter()
for _hx, _hz in VALVE_HOLES:
    _f = FA.m3_at("AirTAC to its bracket", V(_hx, VALVE_Y - A_W / 2, z_valve0 + _hz), V(0, 1, 0), 0.0, A_W, 20.0,
                  exception="AirTAC body 18 mm: nut on the body's face, 2.0 of 2.4 mm thread")
    valve_bracket = valve_bracket.cut(_f.cutter.common(Part.makeBox(60, 60, 60, V(-30, y_wall0 - 0.01, _hz + z_valve0 - 30))))
    ST_FAST.append(_f)
valve_bracket = valve_bracket.removeSplitter()

# --- line A (1/8" = 6 mm tube), A port -> pilot fitting: rigid, moves with the carriage.
HOSE_OD, HOSE_ID = 6.0, 4.0
_pf = qev_closed["Pilot_fitting"].BoundBox
_a_end = V(-A_T / 2 - AIRTAC["straight"]["A"][1], VALVE_Y, z_valve0 + AIRTAC["ports"]["A"])
line_a_pts = [_a_end, V(_a_end.x + 4.0, 3.0, _a_end.z + 3.0), V(-6.0, 0.0, _pf.ZMin - 7.0),
              V(0.0, 0.0, _pf.ZMin - 3.0), V(0.0, 0.0, _pf.ZMin)]
line_a = tube_path(line_a_pts, HOSE_OD / 2)
LINE_A_L = path_len(line_a_pts)
LINE_A_V = math.pi * (HOSE_ID / 2) ** 2 * LINE_A_L / 1000.0

valve_group = Part.makeCompound([valve_body, valve_fit, valve_bracket, line_a])
slide0 = Part.makeCompound(qev_slide + [valve_group])     # + follower, set after the cam

# --- line R (supply), R port -> the MQR rotor's port: flexes with the stroke (route is a sketch).
_r_end = V(A_T / 2 + AIRTAC["straight"]["R"][1], VALVE_Y, z_valve0 + AIRTAC["ports"]["R"])


def line_r_pts(dz):
    """R line in station-local coordinates for carriage offset dz."""
    z = _r_end.z + dz
    return [V(_r_end.x, _r_end.y, z),
            V(A_T / 2 + 2.5 + HOSE_OD / 2, VALVE_Y, z - 3.0),     # turn down beside the body
            V(A_T / 2 + 2.5 + HOSE_OD / 2, 1.5, z - 6.0),
            V(0.0, 1.5, z - 10.0),                                # under the body, onto the station's plane
            V(0.0, -8.0, Z_ROTOR_PORT - 0.5),                     # r 59: outside the bearing cage's ring
            V(0.0, -R_PACK + R_ROTOR_FIT + 3.0, Z_ROTOR_PORT),    # through its notch in the rear disk
            V(0.0, -R_PACK + R_ROTOR_FIT - 1.0, Z_ROTOR_PORT)]


def line_r(dz):
    return tube_path(line_r_pts(dz), HOSE_OD / 2)


# ============================================================ cam liner + follower
z_cam1 = z_carr_aft - CAM_CLEAR_Z
z_tip0 = z_cam1 - CAM_Z_PAD * 0.5
z_cam0 = z_tip0 - BENCH_STROKE - CAM_Z_PAD
CAM_R = R_PACK + EAR_ENV + CLEAR + CAM_WALL_IN + 1.0       # groove centre radius (104)
groove_r = FOLLOWER_OD / 2 + FOLLOWER_CLEAR
cam_id = 2.0 * (CAM_R - CAM_WALL_IN)
cam_od = 2.0 * (CAM_R + groove_r + GROOVE_FLOOR)
y_tip = CAM_R - R_PACK
y_root = VALVE_Y + A_W / 2 + 0.5                   # pin bottom, 0.5 over the valve's outer face
# The finger: a Ø5 steel pin in a blind hole in the bracket's boss (2026-11-21: its old
# stem ran forward to the carriage past the bridge and held on nothing). The groove's
# floor 0.3 mm past its tip keeps it in once the liner is on.
follower = Part.makeCylinder(FOLLOWER_OD / 2, max(6.0, y_tip - y_root), V(0, y_root, z_tip0), V(0, 1, 0))
follower = follower.fuse(Part.makeSphere(FOLLOWER_OD / 2 + 0.2, V(0, y_tip, z_tip0))).removeSplitter()
valve_bracket = valve_bracket.cut(Part.makeCylinder(FOLLOWER_OD / 2, FINGER_BOSS_Y1 + 1.0 - y_root,
                                                    V(0, y_root, z_tip0), V(0, 1, 0))).removeSplitter()
valve_group = Part.makeCompound([valve_body, valve_fit, valve_bracket, line_a])
drum = tube(cam_od, cam_id, z_cam0, z_cam1)
# The groove (2026-11-21): one channel swept along the law, open to the bore so the Ø5
# finger passes (it was 36 spherical dimples 10 deg apart, their mouth at the bore Ø3.3).
GROOVE_R_IN, GROOVE_R_OUT = cam_id / 2.0 - 1.0, CAM_R + groove_r


def _cam_curve(r, dzo, n=144):
    pts = [polar(r, 360.0 * i / n, z_tip0 + cam_dz(360.0 * i / n) + dzo) for i in range(n)]
    c = Part.BSplineCurve()
    c.interpolate(pts, PeriodicFlag=True)
    return c.toShape()


_ct, _cto = _cam_curve(GROOVE_R_IN, groove_r), _cam_curve(GROOVE_R_OUT, groove_r)
_cb, _cbo = _cam_curve(GROOVE_R_IN, -groove_r), _cam_curve(GROOVE_R_OUT, -groove_r)
_gf = []
for _e0, _e1 in ((_ct, _cto), (_cb, _cbo), (_ct, _cb), (_cto, _cbo)):
    _rs = Part.makeRuledSurface(_e0, _e1)
    _gf += _rs.Faces if hasattr(_rs, "Faces") else [_rs]
_gs = Part.Shell(_gf)
_gs.sewShape()
groove_solid = Part.Solid(Part.Shell(_gs.Faces))
if groove_solid.Volume < 0:
    groove_solid.reverse()
cam = drum.cut(groove_solid)
try:
    cam = cam.removeSplitter()
except Exception:
    pass
# Seen from outside (r >= its OD) the liner is the plain drum: distances to parts round it
# are taken to the drum, the groove's spline faces make them minutes long.
cam_outside = drum
_tick("liner and groove")


def follower_on_track(phi):
    tip = place(Part.makeSphere(FOLLOWER_OD / 2, V(0, y_tip, z_tip0)), phi, cam_dz(phi))
    ideal = Part.makeSphere(0.5, polar(CAM_R, phi, z_tip0 + cam_dz(phi)))
    return tip.distToShape(ideal)[0] <= FOLLOWER_CLEAR + 0.3


slide0 = Part.makeCompound(qev_slide + [valve_group, follower] + [f_.body for f_ in ST_FAST])
fixed0 = Part.makeCompound(fixed_station + [f_.body for f_ in PK_FAST])


def station(phi):
    """(moving, fixed, plunger, line R) of the station at pack angle phi."""
    dz = cam_dz(phi)
    return (place(slide0, phi, dz), place(fixed0, phi), place(valve_plunger, phi, dz),
            place(line_r(dz), phi))


# ============================================================ six phases, neighbour gaps
print("pack R=%.2f liner groove R=%.1f Ø%.1f" % (R_PACK, CAM_R, cam_od), flush=True)
phases = []
stations = []
for k in range(N):
    ang = k * 60.0
    mv, fx, pl, lr = station(ang)
    stations.append(Part.makeCompound([mv, fx, pl, lr]))
    phases.append((k + 1, ang, cam_u(ang), cam_dz(ang), phase_name(ang)))
# Core (QEV + guides) on the six phases, as before.
_cores = [place(Part.makeCompound(qev_slide), k * 60.0, cam_dz(k * 60.0)) for k in range(N)]
gap_core = min(_cores[k].distToShape(_cores[(k + 1) % N])[0] for k in range(N))
# Whole stations incl. the valve group and both lines, on the six phases (every
# 5 deg in breech_mechanism_sweep.py).
gap_nbr = min(gap(stations[k], stations[(k + 1) % N]) for k in range(N))
# Own station: valve group vs its fixed parts, line R vs its QEV and guides.
gap_own = 99.0
for k in range(N):
    p = k * 60.0
    gap_own = min(gap_own, gap(place(valve_group, p, cam_dz(p)), place(fixed0, p)),
                  gap(place(line_r(cam_dz(p)), p), place(Part.makeCompound(qev_slide), p, cam_dz(p))))
print("core gap %.2f, station gap (with valves) %.2f, valve/line to own %.2f" % (gap_core, gap_nbr, gap_own), flush=True)

# ============================================================ firing ramp (fixed)
# The ramp stays in the press position: the air is switched by the dead-man on the
# grip (left hand, lever stage 1), so every station on 330..30 fires while it is held.
RAMP_GAP, RAMP_PRESS, RAMP_RISE = 1.0, 2.5, 10.0
SWITCH = 2.0                    # AirTAC switches at ~2.0 of plunger travel (pistol bench)
RAMP_HW, RAMP_DEPTH = 4.0, 6.0
R_TIP = R_PACK + VALVE_Y
z_ramp_low = z_tip_free - RAMP_GAP


def ramp_h(psi):
    """Ramp face above its low level at pack angle psi (deg, symmetric about 0)."""
    a = abs(((psi + 180.0) % 360.0) - 180.0)
    if a >= 30.0:
        return 0.0
    if a <= 30.0 - RAMP_RISE:
        return RAMP_GAP + RAMP_PRESS
    t = (30.0 - a) / RAMP_RISE
    return (RAMP_GAP + RAMP_PRESS) * 0.5 * (1.0 - math.cos(math.pi * t))


def _ramp_curve(r):
    pts = [polar(r, q, z_ramp_low + ramp_h(q)) for q in [x - 30.0 for x in range(61)]]
    c = Part.BSplineCurve()
    c.interpolate(pts)
    return c.toShape()


_rf = Part.makeRuledSurface(_ramp_curve(R_TIP - RAMP_HW), _ramp_curve(R_TIP + RAMP_HW))
_rf = _rf.Faces[0] if hasattr(_rf, "Faces") else _rf
# Flat back on the mount block: 6 thick at the ends, 9.5 on the flat.
z_ramp_back = z_ramp_low - RAMP_DEPTH
_lift = RAMP_GAP + RAMP_PRESS
ramp = _rf.extrude(V(0, 0, -(_lift + RAMP_DEPTH + 1.0))).common(
    Part.makeBox(400, 400, _lift + RAMP_DEPTH + 2.0, V(-200, -200, z_ramp_back)))
ramp_body = ramp.removeSplitter()

# --- mount (2026-11-21: on nuts, no inserts): a block on the liner's inner wall behind the
# ramp, 2 x M3 x 20 radially through it and the liner wall (heads sunk in the block, nuts in
# sockets on the liner's outer face; one bolt in each liner half). The ramp has ears outside
# the plungers' track at psi +/-20: 2 x M3 x 20 down through the ears and the block, heads
# 0.5 under the ramp's face (a valve body passes 1.0 over them), nuts in the block's aft face.
MOUNT_PSI, BLK_L = 20.0, 13.0
z_blk1 = z_ramp_back
z_blk0 = z_blk1 - BLK_L
BLK_R0, BLK_HALF = R_TIP - 7.5, MOUNT_PSI + 4.0
BLK_SCREW_PSI = 8.0
EAR_R0, EAR_R1, EAR_HALF = R_TIP + RAMP_HW - 1.0, cam_id / 2.0 - 1.0, 4.0   # 1 into the band, 3.5 under its face
z_ear1 = z_ramp_low + RAMP_GAP + RAMP_PRESS - FA.HEAD_T - 0.5     # head tops 0.5 under the full-press face
_wedge = Part.makeCylinder(cam_id / 2 + 1.0, BLK_L, V(0, 0, z_blk0), ZA, 2.0 * BLK_HALF)
_wedge.rotate(O, ZA, wdeg(-BLK_HALF))
guide_block = tube(cam_id, 2.0 * BLK_R0, z_blk0, z_blk1).common(_wedge).removeSplitter()
for _s in (-1, 1):
    _ew = Part.makeCylinder(EAR_R1, z_ear1 - z_ramp_back, V(0, 0, z_ramp_back), ZA, 2.0 * EAR_HALF)
    _ew = _ew.cut(Part.makeCylinder(EAR_R0, 50.0, V(0, 0, z_ramp_back - 10.0)))
    _ew.rotate(O, ZA, wdeg(_s * MOUNT_PSI - EAR_HALF))
    ramp_body = ramp_body.fuse(_ew)
ramp_body = ramp_body.removeSplitter()
RAMP_FAST = []
for _s in (-1, 1):
    _p = polar(0.5 * (EAR_R0 + EAR_R1), _s * MOUNT_PSI, z_ear1)
    RAMP_FAST.append(FA.m3("ramp ear to its block", _p, V(0, 0, -1), [ramp_body, guide_block], head_on_face=True,
                           clip=(-0.01, z_ear1 - z_blk0 + 0.01)))
_z_blk_mid = 0.5 * (z_blk0 + z_blk1)
for _s in (-1, 1):
    _d = polar(1.0, _s * BLK_SCREW_PSI)
    RAMP_FAST.append(FA.m3("ramp block to the liner", polar(BLK_R0 + 2.0, _s * BLK_SCREW_PSI, _z_blk_mid), _d,
                           [guide_block, cam], clip=(-3.0, 60.0)))
ramp_body, guide_block = cut_fast(ramp_body, RAMP_FAST, "ramp"), cut_fast(guide_block, RAMP_FAST, "ramp block")
cam, cam_outside = cut_fast(cam, RAMP_FAST, "liner", split=False), cut_fast(cam_outside, RAMP_FAST, "liner outside", split=False)
insert_holes = [f_.cutter for f_ in RAMP_FAST if f_.name == "ramp block to the liner"]
ramp_fire = ramp_body
ramp_seated = gap(ramp_body, guide_block)
# The block's bolts go through the liner wall: clear of the groove, the liner one piece.
_wall_left = min(f_.floor_nut for f_ in RAMP_FAST if f_.name == "ramp block to the liner")
insert_blind = gap(Part.makeCompound(insert_holes), groove_solid, pad=5.0) >= 2.0
liner_one = len(cam.Solids) == 1
groove_vs_mount = gap(groove_solid, Part.makeCompound([guide_block] + insert_holes), pad=5.0)


def press_at(psi, ramp_shape, plunger_local=None):
    """Depth (mm) the ramp reaches into the free plunger of a station at psi."""
    pl = place(valve_plunger, psi, cam_dz(psi))
    c = pl.common(ramp_shape)
    if c.Volume < 1e-6:
        return 0.0
    return c.optimalBoundingBox().ZMax - z_tip_free


_tick("ramp sweep…")
press_rows, press_out, body_ramp = [], 0.0, 99.0
first_touch, last_touch, sw_on, sw_off = None, None, None, None
for _i in range(0, 241):
    psi = -60.0 + 0.5 * _i
    d = press_at(psi, ramp_fire)
    if abs(psi) > 30.0 + 1e-6:
        press_out = max(press_out, d)
    if d > 1e-3:
        first_touch = psi if first_touch is None else first_touch
        last_touch = psi
    if d >= SWITCH:
        sw_on = psi if sw_on is None else sw_on
        sw_off = psi
    if _i % 2 == 0:
        press_rows.append((psi, d))
        mvb = place(Part.makeCompound([valve_body, valve_fit, valve_bracket]), psi, cam_dz(psi))
        body_ramp = min(body_ramp, gap(mvb, ramp_fire))
press_max = max(d for _, d in press_rows)
press_flat = min(d for p, d in press_rows if abs(p) <= 30.0 - RAMP_RISE)
print("press max %.2f flat %.2f outside %.3f" % (press_max, press_flat, press_out), flush=True)

# ============================================================ star feed (feed_bench as library)
_tick("load feed_bench (star)…")
_fb = {"REPO": REPO, "FEED_BENCH_LIBRARY": True, "PELLET_D": PELLET_D, "BREECH_TRAY": BREECH_TRAY,
       "TRAY_PACK_R": R_PACK}
_fb_ok = False
try:
    exec(open(os.path.join(REPO, "gatling", "feed_bench.py")).read(), _fb)
except SystemExit as _e:
    _fb_ok = (_e.code in (0, None))
FB_CHECKS = [(t, ok) for t, ok in _fb.get("checks", [])]
X_STAR, POCKET_R, R_BALL, STAR_R = _fb["X_STAR"], _fb["POCKET_R"], _fb["R_BALL"], _fb["STAR_R"]
STAR_T, STAR_TURNS = _fb["STAR_T"], _fb["STAR_TURNS"]
GUARD_R_IN, GUARD_R_OUT, GUARD_HZ = _fb["GUARD_R_IN"], _fb["GUARD_R_OUT"], _fb["GUARD_HZ"]
GUARD_PHI0 = _fb["GUARD_PHI0"]
Z_BALL_CLOSED = _fb["Z_BALL"]
Z_BALL_OPEN = Z_BALL_CLOSED - BENCH_STROKE
SPEED_RATIO = _fb["SPEED_RATIO"]


def to_pack(s):
    """Bench frame -> this model: the bench turns the other way (mirror y), ball at the open breech."""
    m = s.mirror(O, V(0, 1, 0))
    m.translate(V(0, 0, -BENCH_STROKE))
    return m


STAR_HUB_BODY = None              # the star's hub with its bolt (feed section below): round, it turns with the star


def star_at(d):
    """Star when the station nearest the top is at pack angle 180 + d (with its hub once drawn)."""
    st_ = to_pack(_fb["star_turn"](_fb["star"], STAR_TURNS * d))
    return st_ if STAR_HUB_BODY is None else Part.makeCompound([st_, STAR_HUB_BODY])


feed_head = to_pack(_fb["feed_head"])
feed_lip = to_pack(_fb["lip"])
# The TPU lip sits in a pocket in the strike-off wall (it used to overlap the head, 90 mm3).
feed_head = feed_head.cut(feed_lip)
feed_cup = to_pack(_fb["cup"])
star0 = star_at(0.0)
_handoff_err = (to_pack(Part.Vertex(_fb["pocket_center"](180.0))).Point
                - polar(R_BALL, 180.0, Z_BALL_OPEN)).Length


def ball_z(phi):
    return Z_BALL_CLOSED + cam_dz(phi)


def ball_at(phi):
    return Part.makeSphere(PELLET_D / 2.0, polar(R_BALL, phi, ball_z(phi)))


# --- guard: follows the ball on the close ramp, inside the breech clamp's feed notch
Z_GUARD_MAX = barrel_clamp.BoundBox.ZMax - 10.5
GUARD_END = 240.0
while GUARD_END < 330.0 and ball_z(GUARD_END) < z_bf + 2.0:
    GUARD_END += 0.25
_w = []
_p = GUARD_PHI0
while _p < GUARD_END - 1e-6:
    _q = min(_p + 2.0, GUARD_END)
    _zc = ball_z(0.5 * (_p + _q))
    _z0, _z1 = _zc - GUARD_HZ, min(_zc + GUARD_HZ, Z_GUARD_MAX)
    if _z1 > _z0 + 1.0:
        w = Part.makeCylinder(GUARD_R_OUT, _z1 - _z0, V(0, 0, _z0), ZA, _q - _p + 0.05)
        w = w.cut(Part.makeCylinder(GUARD_R_IN, _z1 - _z0 + 2, V(0, 0, _z0 - 1)))
        w.rotate(O, ZA, wdeg(_p))
        _w.append(w)
    _p = _q
feed_guard = G.fuse_all(_w)
guard_ball = 99.0
_p = GUARD_PHI0
while _p <= GUARD_END:
    guard_ball = min(guard_ball, gap(ball_at(_p), feed_guard))
    _p += 2.0

# ============================================================ star drive: breech rim + fixed train
GEAR_M, GEAR_FACE, GEAR_BACKLASH = 1.5, 8.0, 0.3
Z_RIM, Z_A, Z_B, Z_I, Z_S = 120, 40, 14, 18, 28    # 2026-11-22: 18 | 27 -> 14 | 28: the star turns 1.5 per
                                                   # pack turn (4 pockets, feed_bench), on X 111.6 (was 108.75)
R_RIM, R_A, R_B, R_I, R_S = [GEAR_M * z / 2.0 for z in (Z_RIM, Z_A, Z_B, Z_I, Z_S)]
TRAIN_RATIO = -(R_RIM / R_A) * (R_B / R_S)          # star turns per pack turn (sign: 3 external meshes)
P1_Z0 = z_clamp1                  # on the breech clamps: one print with their lower halves (the hub)
P1_Z1 = P1_Z0 + GEAR_FACE
P2_Z0 = P1_Z1 + 2.0
P2_Z1 = P2_Z0 + GEAR_FACE
L_ANG = -20.0                     # layshaft toward the crank side; the guard is on +Y
L_C = V((R_RIM + R_A) * math.cos(math.radians(L_ANG)), (R_RIM + R_A) * math.sin(math.radians(L_ANG)), 0)
S_C = V(X_STAR, 0, 0)
_dls = (S_C - L_C).Length
_a = ((R_B + R_I) ** 2 - (R_I + R_S) ** 2 + _dls ** 2) / (2 * _dls)
_h = math.sqrt(max(0.0, (R_B + R_I) ** 2 - _a ** 2))
_u = (S_C - L_C) * (1.0 / _dls)
_c1 = L_C + _u * _a + V(-_u.y, _u.x, 0) * _h
_c2 = L_C + _u * _a - V(-_u.y, _u.x, 0) * _h
I_C = _c1 if _c1.Length > _c2.Length else _c2


def spur(z, phase, centre, z0, bore):
    pts = [V(x, y, 0) for x, y in GR.tooth_outline(z, GEAR_M, 1.0, GEAR_BACKLASH)]
    pts.append(pts[0])
    g = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, GEAR_FACE))
    g = g.cut(Part.makeCylinder(bore / 2.0, GEAR_FACE + 4, V(0, 0, -2)))
    g.rotate(O, ZA, phase)
    g.translate(V(centre.x, centre.y, z0))
    return g


def follow_phase(c_d, z_d, ph_d, c_f, z_f):
    """Phase of a follower gear so a gap of it meets the driver's nearest tooth."""
    u = math.degrees(math.atan2(c_f.y - c_d.y, c_f.x - c_d.x))
    pitch = 360.0 / z_d
    e = ((u - ph_d + pitch / 2.0) % pitch) - pitch / 2.0
    return u + 180.0 + 180.0 / z_f + e * z_d / z_f


PH_RIM = 0.0
PH_A = follow_phase(O, Z_RIM, PH_RIM, L_C, Z_A)
PH_B = 0.0
PH_I = follow_phase(L_C, Z_B, PH_B, I_C, Z_I)
PH_S = follow_phase(I_C, Z_I, PH_I, S_C, Z_S)
rim_gear = spur(Z_RIM, PH_RIM, O, P1_Z0, 2 * 30.0)
for k in range(N):
    c = polar(R_PACK, k * 60.0)
    rim_gear = rim_gear.cut(Part.makeCylinder(BARREL_OD / 2 + 0.35, 20, V(c.x, c.y, P1_Z0 - 5)))
rim_gear = rim_gear.removeSplitter()
SHAFT_D = 8.0
gear_a = spur(Z_A, PH_A, L_C, P1_Z0, SHAFT_D + 0.2)
gear_b = spur(Z_B, PH_B, L_C, P2_Z0, SHAFT_D + 0.2)
gear_i = spur(Z_I, PH_I, I_C, P2_Z0, 6.2)
gear_s = spur(Z_S, PH_S, S_C, P2_Z0, SHAFT_D + 0.2)
# Gearbox: rear plate behind the rim, front plate ahead of the second plane, outer wall;
# open toward the rim, which turns inside it.
BOX_R0, BOX_R1 = 93.0, max(L_C.Length + R_A, I_C.Length + R_I) + GEAR_M + 4.0
BOX_A0, BOX_A1 = -45.0, 16.0
BOX_Z0, BOX_Z1 = P1_Z0 - 10.5, P2_Z1 + 5.5
_sec = Part.makeCylinder(BOX_R1 + 2.5, BOX_Z1 - BOX_Z0, V(0, 0, BOX_Z0), ZA, BOX_A1 - BOX_A0)
_sec = _sec.cut(Part.makeCylinder(BOX_R0, BOX_Z1 - BOX_Z0 + 2, V(0, 0, BOX_Z0 - 1)))
_sec.rotate(O, ZA, BOX_A0)
_cav = Part.makeCylinder(BOX_R1, P2_Z1 + 1.5 - (P1_Z0 - 1.0), V(0, 0, P1_Z0 - 1.0), ZA, BOX_A1 - BOX_A0 - 4.0)
_cav = _cav.cut(Part.makeCylinder(60.0, 200, V(0, 0, P1_Z0 - 50)))
_cav.rotate(O, ZA, BOX_A0 + 2.0)
_cav = _cav.fuse(Part.makeCylinder(BOX_R0 + 1.0, P2_Z1 + 1.5 - (P1_Z0 - 1.0), V(0, 0, P1_Z0 - 1.0)))
gearbox = _sec.cut(_cav)
# Shafts and pins in the box (2026-11-21; they were bare pins and journals in printed holes,
# held along their axes by "the walls": the star gear 3.0 loose between the hub's faces, A + B
# 2.5, the idler 3.5 with gear A's face as its rear stop, the A + B pin free to slide out aft).
# - Star shaft: in from the front ring's pad (feed section below); here a floating 608 in the
#   rear plate, in from behind, its floor ahead; the front plate only lets the shaft through.
# - A + B pin: a blind hole in the rear plate (2 mm floor), its front end PIN_STOP under the
#   61836's rear retainer.
# - Idler: on a steel tube 6 x 1 clamped by an M3 x 20 from inside: the head in a recess of the
#   idler's rear face, the tube, the front plate, the nut in a boss ahead of the plate. The
#   idler turns on the tube between the head and the plate.
# The gears' bosses and hubs reach the plates TRAIN_GAP short.
TRAIN_GAP = 0.3
SB_OD, SB_W = 22.0, 7.0                              # 608 for the star shaft
PIN_STOP = 0.5
_cav_r, _cav_f = P1_Z0 - 1.0, P2_Z1 + 1.5             # the cavity's rear and front faces
gearbox = gearbox.cut(Part.makeCylinder(SHAFT_D / 2 + 0.2, _cav_f + 10.0 - (BOX_Z0 + 2.0), V(L_C.x, L_C.y, BOX_Z0 + 2.0)))
gearbox = gearbox.cut(Part.makeCylinder(SB_OD / 2 + 0.1, SB_W + 1.0, V(S_C.x, S_C.y, BOX_Z0 - 1.0)))
gearbox = gearbox.cut(Part.makeCylinder(5.0, 200, V(S_C.x, S_C.y, BOX_Z0 - 50)))
star_brg_box = tube(SB_OD, SHAFT_D, BOX_Z0, BOX_Z0 + SB_W, S_C.x, S_C.y)
z_star0 = Z_BALL_OPEN - STAR_T / 2.0
star_shaft = Part.makeCylinder(SHAFT_D / 2, BOX_Z1 + 1.0 - (z_star0 - 2.0), V(S_C.x, S_C.y, z_star0 - 2.0))
lay_shaft = Part.makeCylinder(SHAFT_D / 2, BOX_Z1 + 2.0 - PIN_STOP - (BOX_Z0 + 2.0), V(L_C.x, L_C.y, BOX_Z0 + 2.0))
# The head (Ø5.5) would pass the idler's bore (6.2): a washer Ø9 x 0.8 (DIN 9021) under it
# holds the idler; washer and head sit in the recess.
IDL_TUBE_OD, IDL_TUBE_ID, IDL_WASHER = 6.0, 4.0, (9.0, 0.8)
IDL_HEAD_REC = IDL_WASHER[0] + 0.6
_ih0 = P2_Z0 + 0.2                                   # the bolt head, 0.2 inside the idler's rear face
_iw0 = _ih0 + FA.HEAD_T                              # its bearing face on the washer
_it0 = _iw0 + IDL_WASHER[1]                          # the tube's rear end
_it1 = _cav_f + 1.0                                  # the tube 1 mm into the front plate
idl_shaft = tube(IDL_TUBE_OD, IDL_TUBE_ID, _it0, _it1, I_C.x, I_C.y).fuse(
    tube(IDL_WASHER[0], FA.M3_HOLE, _iw0, _it0, I_C.x, I_C.y)).removeSplitter()
IDL_FAST = FA.m3_at("idler: its tube clamped to the box's front plate", V(I_C.x, I_C.y, _iw0), ZA, 0.0,
                    20.0 - FA.NUT_T - 1.0, 20.0, floor_nut=20.0 - FA.NUT_T - 1.0 - (_it1 - _iw0))
_iblk1 = _iw0 + IDL_FAST.grip + FA.SOCKET_T
gearbox = gearbox.fuse(Part.makeCylinder(7.0, _iblk1 - BOX_Z1 + 0.5, V(I_C.x, I_C.y, BOX_Z1 - 0.5)))
gearbox = gearbox.cut(Part.makeCylinder(IDL_TUBE_OD / 2 + 0.1, _it1 - _cav_f + 0.5, V(I_C.x, I_C.y, _cav_f - 0.5)))
gearbox = cut_fast(gearbox, [IDL_FAST], "gearbox")
gear_i = gear_i.cut(Part.makeCylinder(IDL_HEAD_REC / 2, _it0 + 0.2 - (P2_Z0 - 1.0), V(I_C.x, I_C.y, P2_Z0 - 1.0)))
gear_i = gear_i.fuse(tube(12.0, 6.2, P2_Z1 - 0.1, _cav_f - TRAIN_GAP, I_C.x, I_C.y)).removeSplitter()
# The star gear: a hub back through plane 1 to the floor of the 608's pocket (gear A's tips
# pass it by STAR_HUB_CLEAR) and a boss ahead to the front plate.
STAR_HUB_D = 2.0 * ((S_C - L_C).Length - (R_A + GEAR_M)) - 1.4
gear_s = G.fuse_all([gear_s, tube(STAR_HUB_D, SHAFT_D + 0.2, _cav_r + TRAIN_GAP, P2_Z0 + 0.1, S_C.x, S_C.y),
                     tube(16.0, SHAFT_D + 0.2, P2_Z1 - 0.1, _cav_f - TRAIN_GAP, S_C.x, S_C.y)]).removeSplitter()
STAR_HUB_CLEAR = (S_C - L_C).Length - (R_A + GEAR_M) - STAR_HUB_D / 2.0
train_parts = [("gear A (meshes the rim)", gear_a), ("gear B", gear_b), ("idler", gear_i),
               ("star gear", gear_s), ("star shaft", star_shaft), ("layshaft", lay_shaft),
               ("idler shaft", idl_shaft), ("gearbox", gearbox)]


def train_pose(alpha):
    """Rim turned by alpha (deg, = pack turn); every gear turned by its ratio."""
    wa = -Z_RIM / float(Z_A)
    wi = -wa * Z_B / float(Z_I)
    ws = -wi * Z_I / float(Z_S)
    return (rot(rim_gear, alpha), rot(gear_a, wa * alpha, L_C), rot(gear_b, wa * alpha, L_C),
            rot(gear_i, wi * alpha, I_C), rot(gear_s, ws * alpha, S_C))


mesh_worst = 0.0
for _al in (0.0, 0.6, 1.2, 1.8, 2.4):
    r_, a_, b_, i_, s_ = train_pose(_al)
    mesh_worst = max(mesh_worst, r_.common(a_).Volume, b_.common(i_).Volume, i_.common(s_).Volume)
_wa = -Z_RIM / float(Z_A)
train_star_turns = (-(-_wa * Z_B / float(Z_I)) * Z_I / float(Z_S))
centre_err = max(abs(L_C.Length - (R_RIM + R_A)), abs((I_C - L_C).Length - (R_B + R_I)),
                 abs((S_C - I_C).Length - (R_I + R_S)))

# ============================================================ front hub and its bearing (2026-11-21)
# The pack hung on the two 6808 at the rear: 0.58 mm at the rim at 1 g even on a stiff
# hub (docs/gatling.md, "Консоль пакета"). A 61836 ahead of the star-drive box carries
# its front. The hub is one print: the rim 120, the lower halves of the six breech clamps
# behind it (the rails end in blind sockets in their feet) and a tube forward inside the
# box (barrels inside, r 79.5; the star gear outside, r 87) to the bearing's seat. The
# inner race sits on a shoulder and under a front retainer (6 x M3 x 20 into the seat,
# nuts slid in from inside between the barrels); the outer race in a housing with a lip,
# its rear retainer clamped by the housing's M6 studs (frame, below).
# 2026-11-23: a printed slide ring by default, in the KA070XP0's envelope (16 mm shorter and ~1.7 kg
# lighter than the 61836; the thin bearing costs $120..1800). It stands clamped in the housing, the
# hub's journal turns in it, 0.2 radial, and the hub's shoulder and retainer locate the pack along
# the axis, 0.1 each side. FRONT_BRG_NAME = "KA070XP0" / "61836" before exec brings a bearing back.
# d1 / D1: shoulders (a bearing's races; here the hub's thrust shoulder and the housing's lip).
FRONT_BEARINGS = {"slide": dict(name="slide ring", d=177.8, bore=178.2, D=190.5, B=6.35, d1=184.0, D1=187.3, ret_t=6.0,
                                ret_ri=0.2, bolt_r=83.2, axial=0.1, mat="strong"),
                  "KA070XP0": dict(name="KA070XP0", d=177.8, D=190.5, B=6.35, d1=181.0, D1=187.3, ret_t=6.0, ret_ri=0.2, bolt_r=83.2),
                  "61836": dict(name="61836", d=180.0, D=225.0, B=22.0, d1=187.0, D1=218.0, ret_t=4.0, ret_ri=1.0, bolt_r=None)}
try:
    FRONT_BRG_NAME
except NameError:
    FRONT_BRG_NAME = "slide"
FRONT_BRG = FRONT_BEARINGS[FRONT_BRG_NAME]
HUB_TUBE_RI, HUB_TUBE_RO = 80.0, 85.5
RET_T = FRONT_BRG["ret_t"]
FRONT_AX = FRONT_BRG.get("axial", 0.0)           # the slide ring's running play along the axis, each side
z_brg0 = BOX_Z1 + 5.0                            # shaft ends at BOX_Z1 + 1, the rear retainer from BOX_Z1 + 2
z_brg1 = z_brg0 + FRONT_BRG["B"]
z_seat0 = P2_Z1 + 1.0
# EVA skin over the pack (2026-11-22, "EVA skin" below): its bore lies on the tips of the frame's
# stud lugs (STUD_R + STUD_LUG_D / 2, checked there); printed glue lands reach it.
SKIN_T = 5.0                                     # EVA sheet
SKIN_R_IN = cam_od / 2.0 + 18.0                  # 127
SKIN_CLEAR = 2.0                                 # a window round whatever crosses the skin
SKIN_WEB = 12.0                                  # narrower EVA between windows (or a window and an edge) goes
LAND_T, LAND_RIB_T = 2.0, 3.0                    # glue land: a hoop out to SKIN_R_IN on radial ribs
LAND_RIB_ANGLES = [15.0 + 30.0 * k_ for k_ in range(12)]
BED = 256.0                                      # Bambu P2S
HOUS_RO = SKIN_R_IN                              # 125 until 2026-11-22: the skin is glued on the housing
_hub = [rim_gear] + [place(clamp_lower, k * 60.0) for k in range(N)] + [
    tube(2 * HUB_TUBE_RO, 2 * HUB_TUBE_RI, P1_Z1 - 0.5, z_seat0 + 0.5),
    tube(FRONT_BRG["d"], 2 * HUB_TUBE_RI, z_seat0, z_brg1 + FRONT_AX),
    tube(FRONT_BRG["d1"], 2 * HUB_TUBE_RI, z_brg0 - 2.0, z_brg0 - FRONT_AX)]
pack_hub = G.fuse_all(_hub).removeSplitter()
front_bearing = tube(FRONT_BRG["D"], FRONT_BRG.get("bore", FRONT_BRG["d"]), z_brg0, z_brg1)
brg_ret_in = tube(FRONT_BRG["d1"] + 1.0, 2 * (HUB_TUBE_RI + FRONT_BRG["ret_ri"]), z_brg1 + FRONT_AX, z_brg1 + FRONT_AX + RET_T)
brg_housing = tube(2 * HOUS_RO, FRONT_BRG["D"] + 0.2, z_brg0, z_brg1).fuse(
    tube(2 * HOUS_RO, FRONT_BRG["D1"], z_brg1, z_brg1 + 3.0)).removeSplitter()
brg_ret_out = tube(2 * HOUS_RO, FRONT_BRG["D1"], z_brg0 - 3.0, z_brg0)
HUB_FAST = []
_r_ret = FRONT_BRG["bolt_r"] or 0.5 * (HUB_TUBE_RI + 1.0 + 0.5 * FRONT_BRG["d"])
for k in range(N):
    _a = k * 60.0 + 30.0
    _o = polar(_r_ret, _a, z_brg1 + FRONT_AX + RET_T)
    HUB_FAST.append(FA.m3_at("hub: inner race retainer", _o, V(0, 0, -1), 0.0, 20.0 - FA.NUT_T - 1.0, 20.0,
                             nut_slot=(polar(-1.0, _a), _r_ret - HUB_TUBE_RI + 1.0)))
pack_hub, brg_ret_in = cut_fast(pack_hub, HUB_FAST, "hub"), cut_fast(brg_ret_in, HUB_FAST, "inner race retainer")
hub_one = len(pack_hub.Solids) == 1
# The tube and the seat against the box and its train (the rim's teeth: in the sweep).
_hub_core = G.fuse_all(_hub[-3:])
hub_vs_box = min(gap(_hub_core, _p) for _p in (gearbox, gear_b, gear_i, gear_s, star_shaft, lay_shaft, idl_shaft))
hub_vs_housing = min(gap(pack_hub, brg_housing), gap(pack_hub, brg_ret_out), gap(brg_ret_in, brg_housing))
_tick("front hub and bearing")

# ============================================================ frame: liner + rings on M6 studs
# 2026-11-21: the printed spars (Ø8 cylinders) are bare M6 studs with a nut either side of
# every ring, lug and disk they pass ("Каркас на шпильках" below, after the drive and the
# controls, when every frame element is built). Here: the front ring, the muzzle plate.
SPAR_R = 4.0                           # old printed spar radius (the bearing disks' spokes keep it)
RING_T = 6.0
RING_WALL = 4.0
r_case_od = cam_od / 2.0
r_case_id = r_case_od - RING_WALL
z_tip_b = z_bf + BARREL_SHOW
z_front0 = z_tip_b - PLATE_T + PLATE_LIP
z_front1 = z_tip_b + PLATE_LIP
Z_FRING0, Z_FRING1 = z_bf - PLATE_T * 0.35, z_bf - PLATE_T * 0.35 + PLATE_T   # front frame ring (barrel's breech)
_fol_zmax = follower.BoundBox.ZMax
z_spar0 = z_cam1                       # bay 2 studs start on the liner's front lugs
z_case1 = Z_FRING1
STUD_R = r_case_od + 9.5               # M6 studs outside the liner and the rings (nut AF 10: 3.7 off the liner)
STUD_LUG_D = 17.0
# Muzzle plate: each barrel pinched by an M3 x 20 across a slit (it used to slide on them).
r_plate = R_PACK + BARREL_OD / 2 + PLATE_RIM + 7.5


def barrel_plate(z0, z1, od_r):
    disc = Part.makeCylinder(od_r, z1 - z0, V(0, 0, z0))
    for k in range(N):
        c = polar(R_PACK, k * 60.0)
        disc = disc.cut(Part.makeCylinder(BARREL_OD / 2 + 0.35, (z1 - z0) + 4.0, V(c.x, c.y, z0 - 2.0)))
    disc = disc.cut(Part.makeCylinder(max(6.0, R_PACK - BARREL_OD / 2 - 4.0), (z1 - z0) + 4.0, V(0, 0, z0 - 2.0)))
    return disc.removeSplitter()


front_plate = barrel_plate(z_front0, z_front1, r_plate)
PLATE_FAST = []
for k in range(N):
    _sl = Part.makeBox(r_plate - R_PACK + 2.0, 1.2, PLATE_T + 4.0, V(R_PACK, -0.6, z_front0 - 2.0))
    _sl.rotate(O, ZA, wdeg(k * 60.0))
    front_plate = front_plate.cut(_sl)
    _rb = 0.5 * (R_PACK + BARREL_OD / 2 + 0.35 + r_plate)
    PLATE_FAST.append(FA.m3("muzzle plate pinch", polar(_rb, k * 60.0, 0.5 * (z_front0 + z_front1)),
                            polar(1.0, k * 60.0 + 90.0) * -1.0, [front_plate, front_plate], clip=(-11.0, 11.0)))
front_plate = cut_fast(front_plate, PLATE_FAST, "muzzle plate")
SPAR_ANGLES = [w for w in (30.0, 90.0, 150.0, 210.0, 270.0, 330.0)
               if abs(((w + 180.0) % 360.0) - 180.0) > 35.0]       # none under the feed (world 0)
pack_frame = tube(2 * r_case_od, 2 * r_case_id, Z_FRING0, Z_FRING1)
# The feed head bears on the front ring, the star shaft runs through it.
pack_frame = pack_frame.cut(feed_head).cut(Part.makeCylinder(SHAFT_D / 2 + 0.3, 400, V(S_C.x, S_C.y, -100)))
breech_casing = pack_frame
full_shell_vol = tube(2.0 * r_case_od, 2.0 * r_case_id, z_cam0 - RING_T, z_case1).Volume
frame_ok = True                        # open frame: rings and studs (checked again with the studs)

# ============================================================ air: MQR in the pack's tail, rear bearing
# 2026-11-23 (docs/gatling.md, "Короткий хвост"): the hollow axle on two 6808 took 206 mm behind
# the stations. Now the rotor sits in the rear rail disk and the stator behind it on the rear
# plate, so the MQR overlaps the valves' stroke. The disk's sleeve round the MQR runs in a 61812;
# its outer race is held in a cage off the rear plate, the inner race floats on the sleeve (the
# front bearing locates the pack along the axis). The MQR carries no load: a TPU pad under the rotor.
MQR_D, MQR_ROTOR_L, MQR_STATOR_L, MQR_SPIGOT = 46.0, 15.0, 72.0, 3.0
SOFT_T = 3.0                                    # TPU pad between the rotor's face and the disk's web
SUPPLY_HOSE_OD, SUPPLY_HOSE_L = 14.0, 60.0     # end of the thick hose from the receiver (3/8")
DEADMAN_R, DEADMAN_L = 12.0, 28.0
RBRG = dict(name="61812", d=60.0, D=78.0, B=10.0, D1=73.0)     # D1: the outer race's shoulder, lip and retainer bear inside it
_rot_min = min(Part.makeCompound(list(station(p))).BoundBox.ZMin for p in (0.0, 180.0))
z_rotor1 = Z_ROTOR1
z_rotor0 = z_rotor1 - MQR_ROTOR_L
z_stator1 = z_rotor0
z_stator0 = z_stator1 - MQR_STATOR_L
z_mqr_plate1 = z_stator0 - MQR_SPIGOT
z_mqr_plate0 = z_mqr_plate1 - 6.0
z_web0 = z_rotor1 + SOFT_T
z_rb1 = Z_ROTOR_PORT - ROTOR_FIT_D / 2.0 - 0.4  # the bearing's front face, just behind the rotor's fittings
z_rb0 = z_rb1 - RBRG["B"]
ROTOR_BORE = MQR_D + 1.2
# Rear disk (2026-11-21): the rails end in blind sockets from its front face. 2026-11-23: it holds
# the rotor in a bore and runs on as a sleeve to the 61812. The notches for the rotor's fittings
# and the lines are open aft only: the web ahead of them keeps the disk one piece.
REAR_NOTCH_W = ROTOR_FIT_D + 0.4
z_notch0, z_notch1 = z_rb1 + 0.3, Z_ROTOR_PORT + ROTOR_FIT_D / 2.0 + 0.4
rear_disk = Part.makeCylinder(REAR_DISK_R, REAR_DISK_Z1 - REAR_DISK_Z0, V(0, 0, REAR_DISK_Z0)).fuse(
    Part.makeCylinder(RBRG["d"] / 2.0, REAR_DISK_Z0 - (z_rb0 - 0.2) + 0.5, V(0, 0, z_rb0 - 0.2)))
rear_disk = rear_disk.cut(Part.makeCylinder(ROTOR_BORE / 2.0, z_web0 - (z_rb0 - 2.0), V(0, 0, z_rb0 - 2.0)))
for k in range(N):
    for x, y in rail_centers():
        rc = place(Part.Vertex(V(x, y, 0)), k * 60.0).Point
        rear_disk = rear_disk.cut(Part.makeCylinder(RAIL_HOLE / 2, RAIL_SOCKET + 1.0, V(rc.x, rc.y, z_rail_pk0)))
    _sl = Part.makeBox(REAR_NOTCH_W, 40.0, z_notch1 - z_notch0, V(-REAR_NOTCH_W / 2, -R_PACK + 22.0, z_notch0))
    rear_disk = rear_disk.cut(place(_sl, k * 60.0))
AIR_FAST = []
M4_EXC = []                      # bought parts' own M4 threads: (name, body)
soft_coup = tube(MQR_D, 6.0, z_rotor1, z_web0)
for _k in range(2):
    _p = polar(19.0, 90.0 + 180.0 * _k, 0.0)
    _h = Part.makeCylinder(2.2, 30.0, V(_p.x, _p.y, z_rotor1 - 5.0))
    rear_disk, soft_coup = rear_disk.cut(_h), soft_coup.cut(_h)
    M4_EXC.append(("M4 x 16: MQR rotor in the rear disk, through its TPU pad (its M4 DP10)",
                   Part.makeCylinder(2.0, 16.0, V(_p.x, _p.y, REAR_DISK_Z1 - 16.0)).fuse(
                       Part.makeCylinder(3.5, 4.0, V(_p.x, _p.y, REAR_DISK_Z1)))))
rear_disk, soft_coup = rear_disk.removeSplitter(), soft_coup.removeSplitter()
rear_disk_one = len(rear_disk.Solids) == 1
mqr_rotor = tube(MQR_D, 6.0, z_rotor0, z_rotor1)
mqr_stator = tube(MQR_D, 6.0, z_stator0, z_stator1).fuse(Part.makeCylinder(10.0, MQR_SPIGOT, V(0, 0, z_stator0 - MQR_SPIGOT)))
mqr_plate = Part.makeCylinder(32.0, 6.0, V(0, 0, z_mqr_plate0))
rear_bearing = tube(RBRG["D"], RBRG["d"], z_rb0, z_rb1)
rotor_fittings = Part.makeCompound([place(Part.makeCylinder(ROTOR_FIT_D / 2.0, ROTOR_FIT_L, V(0, -R_PACK + 23.0, Z_ROTOR_PORT), V(0, 1, 0)),
                                          k * 60.0) for k in range(N)])
_tick("air: rear disk, MQR, 61812")
# Supply: thick hose from the receiver -> pommel -> dead-man in the grip -> the 1 -> 6 collector
# -> the stator's six ports (drawn in "controls" below). No buffer tank.
z_supply = z_stator0 + 20.0

# ============================================================ pack drive from the crank
# Crank shaft across the barrels (Y), drawn on -Y and mirrored to CRANK_SIDE, at the middle of the closed QEVs ->
# bevel pair 20:20 m 2 -> lay shaft parallel to the axle, outside the frame (r 135)
# -> gear 60 in the star-drive rim 120 (plane 1). One crank turn = 60 / 120 = 0.5
# pack turn. Along the QEVs the stations sweep r <= 96.3 and the frame spar on
# -Y takes r 100..108, so the shaft runs at r 135: its rim gear is then 60 (not
# a pinion 20, whose shaft at r 105 would cut the spar and the front ring) and
# the pair is 1:1. Tooth counts are a draft; the bench measures the torque.
CP_Z = 60                         # gear in the rim (m GEAR_M)
CB_M, CB_ZS, CB_ZB = 2.0, 20, 20  # bevel pair: lay shaft, crank shaft
CB_FACE, CB_BACKLASH = 9.0, 0.2
CRANK_ANG = -90.0                 # lay shaft as drawn (-Y); the crank axis is world Y
CRANK_SIDE = +1                   # +1: mirrored onto +Y (the shooter's right), -1: as drawn
CBRG_OD, CBRG_W = 22.0, 7.0       # 608
CBOSS_OD = CBRG_OD + 8.0
R_CP = GEAR_M * CP_Z / 2.0
CP_C = V((R_RIM + R_CP) * math.cos(math.radians(CRANK_ANG)),
         (R_RIM + R_CP) * math.sin(math.radians(CRANK_ANG)), 0)
CB_DS = math.degrees(math.atan2(CB_ZS, CB_ZB))             # pitch cone angles, shafts at 90 deg
CB_DB = 90.0 - CB_DS
CB_RS = CB_M * CB_ZS / 2.0
_chamber = qev_closed["Chamber_tube"].BoundBox
Z_CRANK = 0.5 * (_chamber.ZMin + _chamber.ZMax)           # crank axis = cone apex: middle of the closed QEV
APEX = V(CP_C.x, CP_C.y, Z_CRANK)
crank_gear = spur(CP_Z, follow_phase(O, Z_RIM, PH_RIM, CP_C, CP_Z), CP_C, P1_Z0, SHAFT_D + 0.2)

# Local frame: apex at the origin, axes as the world (+Z muzzle, -Y out); the lay
# shaft is the local Z axis, the crank shaft the local Y axis.
# Lay-shaft bevel behind the apex (-Z), teeth facing forward, meshing the crank bevel
# below its axis; the lay shaft runs forward past the crank bevel's inner face (the
# crank shaft stops outboard of the apex). With the bevel ahead of the apex the crank
# turned the other way: its top went aft. Now it turns clockwise seen from its knob
# (top forward), as a drill or a flexible shaft drives it, and as the Gatling's crank
# on the right turned. CB_SENSE is the crank bevel's turn per lay-bevel turn sign.
# back_cone: full-height teeth (the plain planar form makes them half height at 45 deg).
CB_SENSE = -1.0
bevel_small, CB_INFO_S = GR.bevel_gear(CB_M, CB_ZS, CB_FACE, 16.0, 3.0, SHAFT_D + 0.2, CB_BACKLASH,
                                       delta_deg=CB_DS, phase_deg=90.0, back_cone=True)
bevel_small.rotate(O, V(1, 0, 0), 180.0)                  # axis +Z -> -Z; its tooth at local +Y -> -Y
# Crank bevel: local +Z -> world -Y (90 deg about X); its gap at local -Y -> world -Z.
bevel_big, CB_INFO_B = GR.bevel_gear(CB_M, CB_ZB, CB_FACE, 24.0, 10.0, SHAFT_D + 0.2, CB_BACKLASH,
                                     delta_deg=CB_DB, phase_deg=-90.0 + 180.0 / CB_ZB, back_cone=True)
bevel_big.rotate(O, V(1, 0, 0), 90.0)
bevel_small.translate(APEX)
bevel_big.translate(APEX)


def to_drive(s):
    m = s.copy()
    m.translate(APEX)
    return m


def _rz(zw):
    return zw - Z_CRANK                                   # world z -> local


# Lay shaft: from behind plate A (its 608) through the bevel and past the apex to
# ahead of the rim gear.
# 2026-11-21: the lay shaft runs on behind plate A into a collar and ahead of gear 60 into its hub.
LAY_COL_L, G60_HUB_L, DRV_SPIGOT_D = 8.0, 10.0, 9.6
_ls0 = -(CB_INFO_S["mount"] + 1.0 + (CBRG_W + 2.0) + 0.3 + LAY_COL_L)
_ls1 = _rz(P1_Z1 + G60_HUB_L)
pin_shaft = to_drive(Part.makeCylinder(SHAFT_D / 2, _ls1 - _ls0, V(0, 0, _ls0)))
# Crank shaft on two 608 in a boss outboard of the crank bevel; the outer end is
# left for the crank arm (drawn later).
CRANK_STUB = 22.0
y_cb0 = CB_INFO_B["mount"] + 3.0                          # boss, from the apex outward
y_cb1 = y_cb0 + 2 * CBRG_W + 14.0
crank_shaft = to_drive(Part.makeCylinder(SHAFT_D / 2, y_cb1 + CRANK_STUB - CB_INFO_B["small_end_z"] + 1.0,
                                         V(0, -(CB_INFO_B["small_end_z"] - 1.0), 0), V(0, -1, 0)))
# Bracket 1 (at the pair): plate A across the lay shaft behind its bevel (608),
# plate B outboard of the crank bevel with the crank boss (2 x 608); plate A
# reaches in onto the frame spar (at 270, mirrored 90). Bracket 2: a boss behind the rim gear
# (608) on a foot on the front frame ring.
_tip = CB_RS + CB_M + 1.0                                 # bevel tip radius + 1
PL_T = CBRG_W + 2.0
z_pa0 = CB_INFO_S["mount"] + 1.0
_pa_in = -APEX.y - (STUD_R - 8.0)                         # plate A inner edge: 8 mm past its M6 stud (90 deg)
y_pb0 = CB_INFO_B["mount"] + 3.0
_br = [Part.makeBox(2 * _tip, _pa_in + y_pb0 + PL_T, PL_T, V(-_tip, -(y_pb0 + PL_T), z_pa0)),
       Part.makeBox(2 * _tip, PL_T, z_pa0 + PL_T + _tip + 4.0, V(-_tip, -(y_pb0 + PL_T), -_tip - 4.0)),
       Part.makeCylinder(CBOSS_OD / 2, y_cb1 - y_cb0, V(0, -y_cb0, 0), V(0, -1, 0))]
bracket_pair = G.fuse_all(_br)
bracket_pair = bracket_pair.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, 0, z_pa0 + 1.0)))
bracket_pair = bracket_pair.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 60, V(0, 0, z_pa0 - 20)))
for yb in (y_cb0 + 1.0, y_cb1 - 1.0 - CBRG_W):
    bracket_pair = bracket_pair.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, -yb, 0), V(0, -1, 0)))
bracket_pair = bracket_pair.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 300, V(0, 50, 0), V(0, -1, 0)))
bracket_pair = bracket_pair.mirror(O, V(0, 0, 1))         # drawn with plate A ahead; the lay bevel is behind the apex
z_cboss_r0, z_cboss_r1 = P1_Z0 - 1.0 - PL_T, P1_Z0 - 1.0
_ring_in = -APEX.y - (r_case_od - 2.0)                    # local y 2 mm into the front ring
_b2 = [Part.makeCylinder(CBOSS_OD / 2, PL_T, V(0, 0, _rz(z_cboss_r0))),
       Part.makeBox(16.0, _ring_in, z_cboss_r1 - Z_FRING1, V(-8.0, 0.0, _rz(Z_FRING1)))]   # on the ring, not 1 mm into it
bracket_rim = G.fuse_all(_b2)
bracket_rim = bracket_rim.cut(Part.makeCylinder(CBRG_OD / 2 + 0.1, CBRG_W, V(0, 0, _rz(z_cboss_r0) + 1.0)))
bracket_rim = bracket_rim.cut(Part.makeCylinder(SHAFT_D / 2 + 1.0, 60, V(0, 0, _rz(z_cboss_r0) - 20)))
crank_bracket = to_drive(Part.makeCompound([bracket_pair.removeSplitter(), bracket_rim.removeSplitter()]))
crank_bearings = to_drive(Part.makeCompound(
    [tube(CBRG_OD, SHAFT_D, -(z_pa0 + 1.0 + CBRG_W), -(z_pa0 + 1.0)),
     tube(CBRG_OD, SHAFT_D, _rz(z_cboss_r0) + 1.0, _rz(z_cboss_r0) + 1.0 + CBRG_W)]
    + [Part.makeCylinder(CBRG_OD / 2, CBRG_W, V(0, -yb, 0), V(0, -1, 0)).cut(
        Part.makeCylinder(SHAFT_D / 2, CBRG_W, V(0, -yb, 0), V(0, -1, 0)))
       for yb in (y_cb0 + 1.0, y_cb1 - 1.0 - CBRG_W)]))
# Room for the hand (reference, not a part): knob orbit CRANK_ARM_R, fist
# HAND_R round the knob, HAND_W wide, outboard of the arm.
CRANK_ARM_R, HAND_R, HAND_W, ARM_T = 80.0, 45.0, 100.0, 10.0
y_arm0 = y_cb1 + CRANK_STUB - ARM_T - 2.0                 # arm on the shaft end
hand_space = to_drive(Part.makeCylinder(CRANK_ARM_R + HAND_R, ARM_T + 2.0 + HAND_W,
                                        V(0, -y_arm0, 0), V(0, -1, 0)))
# Crank arm and knob (stage 6, the shooter's right hand). The arm's hub takes the
# shaft end (Ø8, M4 set screw onto a flat), the arm reaches CRANK_ARM_R; the knob
# is a sleeve on its own steel pin (head inboard of the arm, washer and nut
# outboard), so it turns in the hand. Rest pose: arm up (+X). It all lies inside
# hand_space, which is round about the crank axis, so one pose shows that.
CK_HUB_D, CK_W0, CK_W1 = 22.0, 20.0, 16.0          # hub Ø; arm width at the hub, at the knob
CK_KNOB_OD, CK_KNOB_L, CK_PIN_D, CK_BORE = 26.0, 92.0, 6.0, 6.5
CK_WASHER, CK_HEAD_D, CK_HEAD_T, CK_NUT_T = 1.0, 10.0, 3.0, 4.0
ck_y_in = y_arm0                                    # arm's inboard face (local -y)
ck_y_out = y_arm0 + ARM_T
ck_y_shaft = y_cb1 + CRANK_STUB                     # shaft end = the hub's outer face
ck_y_hub0 = ck_y_in - 2.0                           # hub stands 2 proud of the arm inboard
_ck_prof = Part.makePolygon([V(0, 0, -CK_W0 / 2), V(CRANK_ARM_R, 0, -CK_W1 / 2), V(CRANK_ARM_R, 0, CK_W1 / 2),
                             V(0, 0, CK_W0 / 2), V(0, 0, -CK_W0 / 2)])
_ck_arm = Part.Face(_ck_prof).extrude(V(0, -ARM_T, 0))
_ck_arm.translate(V(0, -ck_y_in, 0))
_ck_arm = G.fuse_all([_ck_arm,
                      Part.makeCylinder(CK_HUB_D / 2, ck_y_shaft - ck_y_hub0, V(0, -ck_y_hub0, 0), V(0, -1, 0)),
                      Part.makeCylinder(CK_W1 / 2 + 1.0, ARM_T, V(CRANK_ARM_R, -ck_y_in, 0), V(0, -1, 0))])
_ck_arm = _ck_arm.cut(Part.makeCylinder(SHAFT_D / 2, 60.0, V(0, -ck_y_hub0 + 1.0, 0), V(0, -1, 0)))
_ck_arm = _ck_arm.cut(Part.makeCylinder(CK_PIN_D / 2 + 0.1, ARM_T + 2.0, V(CRANK_ARM_R, -ck_y_in + 1.0, 0), V(0, -1, 0)))
# The hub on the shaft (2026-11-21, was an M4 set screw): an M3 x 20 across the hub and the
# shaft (drilled Ø3.2), in local coordinates; placed with the arm.
_ck_f = FA.m3("crank arm on its shaft", V(0, -0.5 * (ck_y_hub0 + ck_y_shaft), 0), V(0, 0, -1), [_ck_arm, _ck_arm],
              clip=(-CK_HUB_D / 2 - 1.0, CK_HUB_D / 2 + 1.0))
_ck_arm = _ck_arm.cut(_ck_f.cutter)
crank_arm = to_drive(_ck_arm.removeSplitter())
_ck_shaft_hole = to_drive(Part.makeCylinder(1.6, CK_HUB_D + 4.0, V(0, -0.5 * (ck_y_hub0 + ck_y_shaft), CK_HUB_D / 2 + 2.0), V(0, 0, -1)))
ck_y_knob0 = ck_y_out + CK_WASHER
ck_y_knob1 = ck_y_knob0 + CK_KNOB_L
crank_knob = to_drive(Part.makeCylinder(CK_KNOB_OD / 2, CK_KNOB_L, V(CRANK_ARM_R, -ck_y_knob0, 0), V(0, -1, 0)).cut(
    Part.makeCylinder(CK_BORE / 2, CK_KNOB_L + 2.0, V(CRANK_ARM_R, -ck_y_knob0 + 1.0, 0), V(0, -1, 0))))
crank_knob_pin = to_drive(G.fuse_all([
    Part.makeCylinder(CK_PIN_D / 2, ck_y_knob1 + CK_WASHER + CK_NUT_T - ck_y_in, V(CRANK_ARM_R, -ck_y_in, 0), V(0, -1, 0)),
    Part.makeCylinder(CK_HEAD_D / 2, CK_HEAD_T, V(CRANK_ARM_R, -(ck_y_in - CK_HEAD_T), 0), V(0, -1, 0)),
    Part.makeCylinder(CK_HEAD_D / 2, CK_NUT_T, V(CRANK_ARM_R, -(ck_y_knob1 + CK_WASHER), 0), V(0, -1, 0))]))
drive_parts = [("crank gear (meshes the rim)", crank_gear), ("lay shaft", pin_shaft),
               ("lay bevel", bevel_small), ("crank bevel", bevel_big), ("crank shaft", crank_shaft),
               ("crank brackets", crank_bracket), ("crank bearings", crank_bearings)]


def _rot_axis(s, deg, c, ax):
    m = s.copy()
    m.rotate(c, ax, deg)
    return m


def to_side(s):
    """Drawn (-Y) -> the crank side: mirror y if CRANK_SIDE is +1."""
    return s.mirror(O, V(0, 1, 0)) if CRANK_SIDE > 0 else s.copy()


# Along their axes (2026-11-21; they sat on D-flats between "the walls": gear 60 had 11 mm free
# ahead and 2 mm of shaft past it, the lay shaft and the crank shaft nothing stopping them, the
# crank's pull took the shaft out through its 608s). The 608s are trapped in their pockets by
# 1 mm lips either side; every thrust goes to an inner race through a spigot DRV_SPIGOT_D that
# passes a lip:
# - lay shaft: a collar behind plate A (M3 x 20 across it and the shaft) on plate A's 608, and
#   gear 60 (M3 x 20 across a hub ahead of it) on the rim boss's 608: DRV_GAP float each;
# - lay bevel: on the shaft's D-flat; its thrust (away from the apex) on plate A's 608, ahead of
#   it the mesh;
# - crank shaft: the crank bevel pinned (M3 x 20 across its hub), its thrust outboard onto the
#   inner 608; a printed spacer between the outer 608 and the arm's hub takes the push inward.
DRV_GAP = 0.15
_gears_plain = [crank_gear, bevel_small, bevel_big]                       # without hubs and spigots (bracket clearance)
_z608a = (Z_CRANK - (z_pa0 + 1.0 + CBRG_W), Z_CRANK - (z_pa0 + 1.0))       # plate A's 608 (drawn = world z)
_z608r = (z_cboss_r0 + 1.0, z_cboss_r0 + 1.0 + CBRG_W)                    # the rim boss's 608
_g60 = G.fuse_all([crank_gear, tube(22.0, SHAFT_D + 0.2, P1_Z1 - 0.1, P1_Z1 + G60_HUB_L, CP_C.x, CP_C.y),
                   tube(DRV_SPIGOT_D, SHAFT_D + 0.2, _z608r[1] + DRV_GAP, P1_Z0 + 0.1, CP_C.x, CP_C.y)]).removeSplitter()
_f60 = FA.m3("gear 60 on the lay shaft (hub)", V(CP_C.x, CP_C.y, P1_Z1 + 0.5 * G60_HUB_L), V(-1, 0, 0), [_g60, _g60],
             clip=(-12.0, 12.0))
crank_gear = cut_fast(_g60, [_f60], "gear 60")
_zlc1 = _z608a[0] - 1.0 - 0.3                                            # the collar's front face, 0.3 off plate A
lay_collar = G.fuse_all([tube(20.0, SHAFT_D + 0.1, _zlc1 - LAY_COL_L, _zlc1, CP_C.x, CP_C.y),
                         tube(DRV_SPIGOT_D, SHAFT_D + 0.1, _zlc1 - 0.1, _z608a[0] - DRV_GAP, CP_C.x, CP_C.y)]).removeSplitter()
_flc = FA.m3("lay shaft collar behind plate A", V(CP_C.x, CP_C.y, _zlc1 - 0.5 * LAY_COL_L), V(-1, 0, 0),
             [lay_collar, lay_collar], clip=(-11.0, 11.0))
lay_collar = cut_fast(lay_collar, [_flc], "lay shaft collar")
bevel_small = G.fuse_all([bevel_small, tube(DRV_SPIGOT_D, SHAFT_D + 0.2, _z608a[1] + DRV_GAP, Z_CRANK - CB_INFO_S["mount"] + 0.1,
                                            CP_C.x, CP_C.y)]).removeSplitter()
pin_shaft = pin_shaft.cut(Part.makeCompound([Part.makeCylinder(1.6, 30.0, V(CP_C.x + 15.0, CP_C.y, z_), V(-1, 0, 0))
                                             for z_ in (P1_Z1 + 0.5 * G60_HUB_L, _zlc1 - 0.5 * LAY_COL_L)]))
_ycb_in = APEX.y - y_cb0                                                  # drawn: the boss's inner face
_bb = G.fuse_all([bevel_big, Part.makeCylinder(DRV_SPIGOT_D / 2, (y_cb0 + 1.0 - DRV_GAP) - CB_INFO_B["mount"] + 0.1,
                                               V(APEX.x, APEX.y - CB_INFO_B["mount"] + 0.1, Z_CRANK), V(0, -1, 0))])
_bb = _bb.cut(Part.makeCylinder(SHAFT_D / 2 + 0.1, 40.0, V(APEX.x, APEX.y - CB_INFO_B["mount"] + 5.0, Z_CRANK), V(0, -1, 0)))
_fcb = FA.m3("crank bevel on its shaft (hub)", V(APEX.x, APEX.y - CB_INFO_B["big_end_z"] - 0.5 * (CB_INFO_B["mount"] - CB_INFO_B["big_end_z"]),
                                                  Z_CRANK), V(-1, 0, 0), [_bb, _bb], clip=(-13.0, 13.0))
bevel_big = cut_fast(_bb.removeSplitter(), [_fcb], "crank bevel")
crank_spacer = G.fuse_all([Part.makeCylinder(8.0, ck_y_hub0 - (y_cb1 + 0.3), V(APEX.x, APEX.y - (y_cb1 + 0.3), Z_CRANK), V(0, -1, 0)),
                           Part.makeCylinder(DRV_SPIGOT_D / 2, 1.4, V(APEX.x, APEX.y - (y_cb1 - 1.0), Z_CRANK), V(0, -1, 0))])
crank_spacer = crank_spacer.cut(Part.makeCylinder(SHAFT_D / 2 + 0.2, 40.0, V(APEX.x, APEX.y - (y_cb1 - 5.0), Z_CRANK), V(0, -1, 0))).removeSplitter()
crank_shaft = crank_shaft.cut(Part.makeCylinder(1.6, 30.0, V(APEX.x + 15.0, _fcb.p.y, Z_CRANK), V(-1, 0, 0)))
DRIVE_AXIAL_FAST = [_f60, _flc, _fcb]
_drawn = {"gear": crank_gear, "lay": bevel_small, "crank": bevel_big}
(crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket, crank_bearings, hand_space,
 crank_arm, crank_knob, crank_knob_pin, lay_collar, crank_spacer) = [
    to_side(x_) for x_ in (crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket,
                           crank_bearings, hand_space, crank_arm, crank_knob, crank_knob_pin, lay_collar, crank_spacer)]
crank_parts = [("crank arm", crank_arm), ("knob", crank_knob), ("knob pin", crank_knob_pin)]
CRANK_ARM_FAST = [FA.moved(_ck_f, lambda s_: to_side(to_drive(s_)))] + [FA.moved(f_, to_side) for f_ in DRIVE_AXIAL_FAST]
_gears_plain = [to_side(x_) for x_ in _gears_plain]
crank_shaft = crank_shaft.cut(to_side(_ck_shaft_hole))


def crank_at(deg):
    """Crank arm, knob and pin turned by deg about the crank axis (world Y through z Z_CRANK)."""
    return [_rot_axis(s_, deg, V(0, 0, Z_CRANK), V(0, 1, 0)) for _, s_ in crank_parts]
drive_parts = [("crank gear (meshes the rim)", crank_gear), ("lay shaft", pin_shaft), ("lay bevel", bevel_small),
               ("crank bevel", bevel_big), ("crank shaft", crank_shaft), ("crank brackets", crank_bracket),
               ("crank bearings", crank_bearings), ("lay shaft collar", lay_collar), ("crank spacer", crank_spacer)]


def drive_pose(alpha):
    """Pack turned by alpha: rim; rim gear and lay bevel (-Z_RIM/CP_Z); crank bevel.

    As drawn (-Y) the mesh is at local (0, -RS, -RS) (the lay bevel behind the
    apex), so the crank bevel turns against the lay shaft (CB_SENSE), about +Y;
    the bevel mesh check below catches a wrong sign. Mirrored, pack +alpha is
    the drawn drive at -alpha (the rim maps onto itself).
    """
    a = alpha if CRANK_SIDE < 0 else -alpha
    wl = -Z_RIM / float(CP_Z)
    wc = CB_SENSE * wl * CB_ZS / float(CB_ZB)
    return (rot(rim_gear, alpha), to_side(rot(_drawn["gear"], wl * a, CP_C)),
            to_side(rot(_drawn["lay"], wl * a, CP_C)), to_side(_rot_axis(_drawn["crank"], wc * a, APEX, V(0, 1, 0))))


crank_mesh_worst = 0.0
for _al in (0.0, 0.6, 1.2, 1.8, 2.4):
    r_, p_, _, _ = drive_pose(_al)
    crank_mesh_worst = max(crank_mesh_worst, r_.common(p_).Volume)
bevel_mesh_worst = 0.0
_bsp = 360.0 / CB_ZS / (Z_RIM / float(CP_Z))       # pack angle per lay-bevel tooth
for _i in range(6):
    _, _, s_, b_ = drive_pose(_bsp * _i / 6.0)
    bevel_mesh_worst = max(bevel_mesh_worst, s_.common(b_).Volume)


def _crank_top_dz(sense):
    """z travel of the crank's top (+X of its axis) as the pack turns 1 deg its running way (+)."""
    a_ = 1.0 if CRANK_SIDE < 0 else -1.0
    wc_ = sense * (-Z_RIM / float(CP_Z)) * CB_ZS / float(CB_ZB)
    p0_ = Part.Vertex(APEX + V(40.0, 0, 0))
    p1_ = Part.Vertex(APEX + V(40.0, 0, 0))
    p1_.rotate(APEX, V(0, 1, 0), wc_ * a_)
    return to_side(p1_).Point.z - to_side(p0_).Point.z


CRANK_TOP_DZ = _crank_top_dz(CB_SENSE)
# Clockwise seen from the knob: on the right (+Y) that is the top going forward (+Z).
CRANK_CW = CRANK_TOP_DZ * CRANK_SIDE > 0
PACK_PER_CRANK = (CB_ZB / float(CB_ZS)) * (CP_Z / float(Z_RIM))
CRANK_RPM = 60.0
SHOTS_PER_S = CRANK_RPM / 60.0 * PACK_PER_CRANK * N

# ============================================================ controls: flintlock grip, one two-stage lever, feed gate
# The left hand holds a grip that curls down behind the rear plate like a flintlock
# pistol's, with a brass pommel. One big lever runs along its front following its
# curve, as on a fire extinguisher, pivoted at the top behind the plate; the hand
# squeezes it to the grip.
# Stage 1 (0..5 deg) = air: the lever presses the dead-man valve in the grip through
# a pusher with an over-travel spring; the valve is fully open at 5 deg. Stage 2
# (5..15 deg) = balls: the lever's short tail, inside the grip's root, takes up the
# cable's slack by 5 deg and then draws the gate pin 6 mm out of the feed neck. Let go: the
# gate pin's spring shuts the neck, the valve's spring shuts the air, a torsion spring
# on the pivot opens the lever. The rear plate carries the MQR stator and the grip;
# four struts tied it to the rear bearing disk's rim (2026-11-22: it is a spider on the
# bay-1 studs, straight from the liner; "frame on M6 studs"). The valve's outlet runs inside
# the grip, through the plate, into the stator's rear port.
RP_R = 50.0
STRUT_ANGLES = (45.0, 135.0, 225.0, 315.0)         # = BAY1: the rear plate's studs
SPIDER_SPOKE_W, SPIDER_SPOKE_H, SPIDER_LUG_L, SPIDER_RIM_L = 18.0, 12.0, 16.0, 12.0   # forward of its aft face
# Grip centreline (x, z) from the plate's aft face (x 0): aft, then curling down.
GRIP_PTS = [(0.0, 0.0), (-2.0, -14.0), (-10.0, -36.0), (-30.0, -64.0), (-62.0, -88.0), (-100.0, -102.0),
            (-128.0, -106.0)]
GRIP_KEYS = [(0.0, 32.0, 24.0), (0.17, 19.0, 15.5), (0.45, 21.0, 16.0), (0.75, 24.0, 18.0), (1.0, 27.0, 20.0)]
POMMEL = (16.0, 31.0, 23.0)                      # brass cap: along the end, in the plane, across
LEV_W, LEV_T, LEV_HUB_R = 14.0, 24.0, 6.0      # a broad blade, like an extinguisher's lever
LEV_ANG, STAGE1 = 15.0, 5.0
S_PIV, S_END, PIV_OFF = 0.12, 0.86, 13.0           # pivot at the top (behind the plate), free end by the pommel
LEV_GAP_PIV = 7.0                                # blade off the grip by the pivot
LEV_GAP_TOP = 26.0                               # ... and at its free end
# The pivot (2026-11-21, it was a bare Ø5 pin pressed in 4 mm lugs): a brass tube 5 x 0.45 with
# its ends 3 mm into counterbores in the lugs, an M3 x 50 through it clamping the lugs (and the
# grip's two halves) onto its ends; the lever turns on the tube. 12 mm lugs give the 48.6 mm
# stack the 50 mm bolt needs (45.6..47.6 between head and nut) with its nut in a socket.
GRIP_LUG_T, LUG_GAP, LEV_PIN_D = 12.0, 0.3, 5.0
LEV_TUBE_ID, LEV_TUBE_IN = 4.1, 3.0
TAIL_W, TAIL_T = 6.0, 5.0
# The wire's end (2026-11-21, it was only drawn into the tail): a barrel nipple Ø4 across the
# tail's tip, as on a brake lever, in a boss with a slot toward the wire.
NIP_D, NIP_BOSS_R, NIP_SLOT = 4.0, 5.0, 1.6
PUSH_D, PUSH_GAP, OVERTRAVEL_MAX = 5.0, 0.5, 9.0
DM_D, DM_L, DM_STROKE = 14.0, 18.0, 3.0           # dead-man valve body in the grip
GATE_PIN_D, GATE_IN, GATE_CLEAR = 6.0, 5.0, 1.0
GATE_TRAVEL = GATE_IN + GATE_CLEAR
CABLE_OD = 5.0
HOSE_OUT_OD = 8.0                                # dead-man -> stator
SUP_IN_D = 8.0                                   # the receiver hose's fitting, inside the pommel
WIRE_FREE = 14.0                                 # wire from its stop to the tail at rest
CABLE_HOLE = (28.0, -5.0)                        # cable through the plate (outside the stator, inside the grip root)
YA = V(0, 1, 0)


def bar_y(a, b, w, t):
    """Flat bar in the XZ plane from a to b ((x, z)), width w, thickness t along Y, round ends."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dz)
    nx, nz = -dz / ln * w / 2, dx / ln * w / 2
    pts = [V(a[0] + nx, -t / 2, a[1] + nz), V(b[0] + nx, -t / 2, b[1] + nz),
           V(b[0] - nx, -t / 2, b[1] - nz), V(a[0] - nx, -t / 2, a[1] - nz)]
    s_ = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, t, 0))
    for q in (a, b):
        s_ = s_.fuse(Part.makeCylinder(w / 2, t, V(q[0], -t / 2, q[1]), V(0, 1, 0)))
    return s_.removeSplitter()


def cyl_y(x, z, r, t, y0=None):
    return Part.makeCylinder(r, t, V(x, -t / 2 if y0 is None else y0, z), YA)


def turn_y(shape, c, deg):
    s_ = shape.copy()
    s_.rotate(V(c.x, 0, c.z), YA, deg)
    return s_


def turn_pt(pt, c, deg):
    v_ = Part.Vertex(pt)
    v_.rotate(V(c.x, 0, c.z), YA, deg)
    return v_.Point


# --- rear plate (carries the MQR stator and the grip); its spokes, rim and studs: frame section
mqr_plate = Part.makeCylinder(RP_R, z_mqr_plate1 - z_mqr_plate0, V(0, 0, z_mqr_plate0))
_st = []
for w in STRUT_ANGLES:                  # until the studs are placed: the bay-1 stud runs behind the disks
    a = math.radians(w)
    p0 = V(118.5 * math.cos(a), 118.5 * math.sin(a), z_cam0)
    _st.append(Part.makeCylinder(SPAR_R, z_cam0 - z_mqr_plate0, V(p0.x, p0.y, z_mqr_plate0)))
rear_struts = Part.makeCompound(_st)

# --- grip: a loft through ellipses square to a curved centreline (30 sections)
_gc = Part.BSplineCurve()
_gc.interpolate([V(x_, 0, z_mqr_plate0 + z_) for x_, z_ in GRIP_PTS])
GRIP_LEN = _gc.length()


def grip_frame(f):
    """(centre, tangent, front normal, half height, half width) at fraction f of the grip's length."""
    u_ = _gc.parameterAtDistance(f * GRIP_LEN, _gc.FirstParameter)
    c_ = _gc.value(u_)
    t_ = _gc.tangent(u_)[0]
    t_.normalize()
    n_ = V(t_.z, 0, -t_.x)                       # in the plane, the finger side (down at the root)
    for (f0, h0, w0), (f1, h1, w1) in zip(GRIP_KEYS[:-1], GRIP_KEYS[1:]):
        if f0 <= f <= f1:
            k_ = (f - f0) / (f1 - f0)
            k_ = k_ * k_ * (3.0 - 2.0 * k_)
            return c_, t_, n_, h0 + k_ * (h1 - h0), w0 + k_ * (w1 - w0)
    return c_, t_, n_, GRIP_KEYS[-1][1], GRIP_KEYS[-1][2]


def _gsec(f):
    c_, t_, n_, h_, w_ = grip_frame(f)
    return Part.Wire(Part.Ellipse(c_ + n_ * h_, c_ + YA * w_, c_).toShape())


grip_full = Part.makeLoft([_gsec(i / 29.0) for i in range(30)], True, False)
_ce, _te, _ne, _he, _we = grip_frame(1.0)
_sph = Part.makeSphere(1.0)
_m = App.Matrix(_te.x * POMMEL[0], _ne.x * POMMEL[1], 0, _ce.x + _te.x * 2.0,
                _te.y * POMMEL[0], _ne.y * POMMEL[1], POMMEL[2], 0,
                _te.z * POMMEL[0], _ne.z * POMMEL[1], 0, _ce.z + _te.z * 2.0,
                0, 0, 0, 1)
pommel_full = _sph.transformGeometry(_m)

# --- the lever: pivot low at the front, free end at the top 28 off the grip
_cp, _tp_, _np, _hp, _wp = grip_frame(S_PIV)
P_LEV = _cp + _np * (_hp + PIV_OFF)
# Blade: follows the grip's front down to the pommel, its gap growing towards the free end.
LEV_PTS = [P_LEV]
for _i in range(1, 9):
    _f = S_PIV + (S_END - S_PIV) * _i / 8.0
    _c, _t, _n, _h, _w = grip_frame(_f)
    _g = LEV_GAP_PIV + (LEV_GAP_TOP - LEV_GAP_PIV) * (_i / 8.0)
    LEV_PTS.append(_c + _n * (_h + _g + LEV_W / 2))
E_LEV = LEV_PTS[-1]
LEV_L = sum((b_ - a_).Length for a_, b_ in zip(LEV_PTS[:-1], LEV_PTS[1:]))
_ne_end = grip_frame(S_END)[2]
_v = Part.Vertex(E_LEV)
_v.rotate(V(P_LEV.x, 0, P_LEV.z), YA, 5.0)
SQ = 1.0 if (_v.Point - E_LEV).dot(_ne_end) < 0 else -1.0     # squeeze: the free end goes to the grip


def lever_pt(pt, deg):
    return turn_pt(pt, P_LEV, SQ * deg)


# Tail: from the pivot into the grip's root; solve its length so the wire draws
# GATE_TRAVEL between the stages (the wire's stop sits behind the tip's motion).
TAIL_DIR = _np * -1.0
_mdir = lever_pt(P_LEV + TAIL_DIR * 30.0, 1.0) - (P_LEV + TAIL_DIR * 30.0)
_mdir.normalize()                                # tail tip's motion on squeezing


def _wire(L_):
    tip0 = P_LEV + TAIL_DIR * L_
    stop_ = tip0 - _mdir * WIRE_FREE
    d_ = [(lever_pt(tip0, a_) - stop_).Length - WIRE_FREE for a_ in (STAGE1, LEV_ANG)]
    return d_[0], d_[1] - d_[0], stop_


_L0, _L1 = 20.0, 40.0
for _i in range(30):
    _p0, _p1 = _wire(_L0)[1] - GATE_TRAVEL, _wire(_L1)[1] - GATE_TRAVEL
    if abs(_p1 - _p0) < 1e-12:
        break
    _L0, _L1 = _L1, _L1 - _p1 * (_L1 - _L0) / (_p1 - _p0)
TAIL_L = _L1
WIRE_SLACK, wire_travel, P_STOP = _wire(TAIL_L)
TAIL_TIP = P_LEV + TAIL_DIR * TAIL_L
# One smooth outline (a spline through the blade's centre points, offset either side).
_bc = Part.BSplineCurve()
_bc.interpolate(LEV_PTS)
_side_a, _side_b = [], []
for _i in range(41):
    _u = _bc.FirstParameter + (_bc.LastParameter - _bc.FirstParameter) * _i / 40.0
    _p = _bc.value(_u)
    _tg = _bc.tangent(_u)[0]
    _nn = V(_tg.z, 0, -_tg.x)
    _nn.normalize()
    _side_a.append(_p + _nn * (LEV_W / 2) + V(0, -LEV_T / 2, 0))
    _side_b.append(_p - _nn * (LEV_W / 2) + V(0, -LEV_T / 2, 0))
_outline = _side_a + list(reversed(_side_b))
lever_blade = Part.Face(Part.makePolygon(_outline + [_outline[0]])).extrude(V(0, LEV_T, 0))
lever_blade = lever_blade.fuse(cyl_y(E_LEV.x, E_LEV.z, LEV_W / 2, LEV_T)).removeSplitter()
lever_0 = G.fuse_all([lever_blade, cyl_y(P_LEV.x, P_LEV.z, LEV_HUB_R, LEV_T),
                      bar_y((P_LEV.x, P_LEV.z), (TAIL_TIP.x, TAIL_TIP.z), TAIL_W, TAIL_T)])
lever_0 = lever_0.cut(cyl_y(P_LEV.x, P_LEV.z, LEV_PIN_D / 2 + 0.1, LEV_T + 2))
_nip_dir = P_STOP - TAIL_TIP
_nip_dir.normalize()
_nip_slot = Part.makeBox(NIP_BOSS_R + 2.0, TAIL_T + 2.0, NIP_SLOT, V(0, -TAIL_T / 2 - 1.0, -NIP_SLOT / 2))
_nip_slot.rotate(O, YA, -math.degrees(math.atan2(_nip_dir.z, _nip_dir.x)))
_nip_slot.translate(V(TAIL_TIP.x, 0, TAIL_TIP.z))
lever_0 = lever_0.fuse(cyl_y(TAIL_TIP.x, TAIL_TIP.z, NIP_BOSS_R, TAIL_T)).cut(
    cyl_y(TAIL_TIP.x, TAIL_TIP.z, NIP_D / 2 + 0.1, TAIL_T + 2.0)).cut(_nip_slot).removeSplitter()
gate_nipple = cyl_y(TAIL_TIP.x, TAIL_TIP.z, NIP_D / 2, TAIL_T)
nip_wall = NIP_BOSS_R - NIP_D / 2 - 0.1


def lever_at(deg):
    return turn_y(lever_0, P_LEV, SQ * deg)


finger_travel = (lever_pt(E_LEV, LEV_ANG) - E_LEV).Length
stage1_travel = (lever_pt(E_LEV, STAGE1) - E_LEV).Length
# Lugs on the grip each side of the lever, pin through them.
_lugs = []
for _sy in (-1, 1):
    _y0 = LEV_T / 2 + LUG_GAP if _sy > 0 else -(LEV_T / 2 + LUG_GAP + GRIP_LUG_T)
    _lug = bar_y((P_LEV.x, P_LEV.z), (_cp.x, _cp.z), 2 * LEV_HUB_R + 2.0, GRIP_LUG_T)
    _lug.translate(V(0, _y0 + GRIP_LUG_T / 2, 0))
    _lugs.append(_lug)
_pin_l = LEV_T + 2 * (LUG_GAP + LEV_TUBE_IN)
_pin_bore = cyl_y(P_LEV.x, P_LEV.z, LEV_PIN_D / 2, _pin_l)          # the tube's counterbores and the lever's bore
lever_pin = _pin_bore.cut(cyl_y(P_LEV.x, P_LEV.z, LEV_TUBE_ID / 2, _pin_l + 2.0))

# --- dead-man: a pusher on the blade's grip side, along its motion, where 5 deg of squeeze
# makes 3 mm + 0.5 gap; checked with a probe line through the real (curved) blade.
def _blade_face(r_):
    """Point on the blade's grip-side face about r_ from the pivot, and the motion direction there."""
    best = None
    for a_, b_ in zip(LEV_PTS[:-1], LEV_PTS[1:]):
        for k_ in range(21):
            q_ = a_ + (b_ - a_) * (k_ / 20.0)
            if best is None or abs((q_ - P_LEV).Length - r_) < abs((best - P_LEV).Length - r_):
                best = q_
    d_ = lever_pt(best, 1.0) - best              # its motion on squeezing: towards the grip
    d_.normalize()
    return best + d_ * (LEV_W / 2), d_


def _probe_face(org, d_, deg):
    """Distance along d_ from org to the rotated blade's grip-side face (probe line)."""
    seg = Part.LineSegment(org - d_ * 30.0, org + d_ * 30.0).toShape().common(lever_at(deg))
    return max((v_.Point - org).dot(d_) for v_ in seg.Vertexes)


def _press(r_, deg):
    """(axis point on the blade's centre line, direction, rest face, press at deg) for a pusher at r_."""
    q_, d_ = _blade_face(r_)
    q_ = q_ - d_ * (LEV_W / 2)
    t0_ = _probe_face(q_, d_, 0.0)
    return q_, d_, t0_, _probe_face(q_, d_, deg) - t0_ - PUSH_GAP


_ra, _rb = 30.0, 50.0
for _i in range(12):
    _pa, _pb = _press(_ra, STAGE1)[3] - DM_STROKE, _press(_rb, STAGE1)[3] - DM_STROKE
    if abs(_pb - _pa) < 1e-9:
        break
    _ra, _rb = _rb, _rb - _pb * (_rb - _ra) / (_pb - _pa)
R_PUSH = _rb
Q_PUSH, _face_n0, _push_t0, _ = _press(R_PUSH, STAGE1)
_tip = Q_PUSH + _face_n0 * (_push_t0 + PUSH_GAP)


def _pusher_at(tip_, len_=12.0):
    return Part.makeCylinder(PUSH_D / 2, len_, tip_, _face_n0)


def push_depth(tip_, deg):
    """How far the blade at deg pushes a free pusher whose tip is at tip_ (shift it until clear)."""
    lv_ = lever_at(deg)
    if lv_.common(_pusher_at(tip_)).Volume < 1e-6:
        return -gap(lv_, _pusher_at(tip_), pad=5.0)
    lo_, hi_ = 0.0, 20.0
    for _k in range(20):
        mid_ = 0.5 * (lo_ + hi_)
        if lv_.common(_pusher_at(tip_ + _face_n0 * mid_)).Volume > 1e-6:
            lo_ = mid_
        else:
            hi_ = mid_
    return hi_


# The pusher's end meets the tilted blade at its edge first: set the real gap, then
# correct the radius until 5 deg pushes the valve exactly its stroke.
for _it in range(12):
    _tip = Q_PUSH + _face_n0 * (_push_t0 + PUSH_GAP)
    _tip = _tip + _face_n0 * (PUSH_GAP + push_depth(_tip, 0.0))
    _p1 = push_depth(_tip, STAGE1) - PUSH_GAP
    if abs(_p1 - DM_STROKE) < 0.03:
        break
    R_PUSH *= (DM_STROKE / _p1) ** 0.5
    Q_PUSH, _face_n0, _push_t0, _ = _press(R_PUSH, STAGE1)
_ray = Part.LineSegment(_tip, _tip + _face_n0 * 80.0).toShape().common(grip_full)
_entry = min((v_.Point for v_ in _ray.Vertexes), key=lambda p_: (p_ - _tip).Length)
_body0 = _entry + _face_n0 * 8.0                 # the over-travel sleeve, then the valve body
dm_pusher = Part.makeCylinder(PUSH_D / 2, (_body0 - _tip).Length, _tip, _face_n0)
deadman = Part.makeCylinder(DM_D / 2, DM_L, _body0, _face_n0).fuse(
    Part.makeCylinder(4.0, 8.0, _entry, _face_n0)).removeSplitter()
press_s1 = push_depth(_tip, STAGE1) - PUSH_GAP
overtravel = push_depth(_tip, LEV_ANG) - PUSH_GAP - DM_STROKE
_dm_end = _body0 + _face_n0 * DM_L

# --- channels in the grip: cable (plate -> stop in the pommel, along the back), outlet
# (valve -> along the back -> the stator's rear port), supply (pommel tip -> valve).
_back = []
for f_ in (0.08, 0.3, 0.55):
    c_, t_, n_, h_, w_ = grip_frame(f_)
    _back.append((c_, n_, h_))
_cab_in = [V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate0 + 3.0), V(CABLE_HOLE[0] - 6.0, -8.0, z_mqr_plate0 - 10.0),
           P_STOP - _mdir * 12.0 + V(0, -4.0, 0), P_STOP]
# The outlet leaves the grip's root on +y and goes up through the plate into the 1 -> 6
# collector beside the stator (2026-11-21; it ended in a rear port the MQR does not have).
COLL_INLET = V(0, 43.0, 0)
_out_grip = [_dm_end + V(0, 5.0, 0)] + [c_ - n_ * (0.2 * h_) + V(0, 8.0, 0) for c_, n_, h_ in reversed(_back)]
_out_in = _out_grip + [V(0, 20.0, z_mqr_plate0 - 8.0), V(COLL_INLET.x, COLL_INLET.y, z_mqr_plate0 - 8.0),
                       V(COLL_INLET.x, COLL_INLET.y, z_mqr_plate1 + 1.0)]
_tip_p = _ce + _te * (POMMEL[0] + 2.0)
_c85, _t85, _n85, _h85, _w85 = grip_frame(0.88)
_c70, _t70, _n70, _h70, _w70 = grip_frame(0.70)
_sup_in = [_tip_p, _ce - _ne * 10.0, _c85 - _n85 * (0.5 * _h85), _c70 - _n70 * (0.3 * _h70) + V(0, -5.0, 0),
           _dm_end + V(0, -5.0, 0)]
cable_in = tube_path(_cab_in, CABLE_OD / 2)
air_supply = tube_path(_out_in, HOSE_OUT_OD / 2)
supply_hose = Part.makeCompound([tube_path(_sup_in, SUP_IN_D / 2),
                                 Part.makeCylinder(SUPPLY_HOSE_OD / 2, 50.0, _tip_p - _te * 2.0, _te)])
gate_wire = Part.makeCylinder(0.6, (TAIL_TIP - P_STOP).Length, P_STOP, TAIL_TIP - P_STOP).fuse(gate_nipple).removeSplitter()
_channels = [tube_path(_cab_in, CABLE_OD / 2 + 0.3), tube_path(_out_in, HOSE_OUT_OD / 2 + 0.3),
             tube_path(_sup_in, SUP_IN_D / 2 + 0.3),
             Part.makeCylinder(1.5, (TAIL_TIP - P_STOP).Length + 2.0, P_STOP, TAIL_TIP - P_STOP)]
# Slot for the tail (its swept volume + 0.5 all round).
_tail_sw = G.fuse_all([bar_y((P_LEV.x, P_LEV.z), (lever_pt(TAIL_TIP, a_).x, lever_pt(TAIL_TIP, a_).z),
                             TAIL_W + 1.0, TAIL_T + 1.0) for a_ in [LEV_ANG * i / 6.0 for i in range(7)]]
                       + [cyl_y(lever_pt(TAIL_TIP, a_).x, lever_pt(TAIL_TIP, a_).z, NIP_BOSS_R + 0.5, TAIL_T + 1.0)
                          for a_ in [LEV_ANG * i / 6.0 for i in range(7)]])
grip = grip_full.fuse(_lugs)
pommel = pommel_full.cut(grip_full)
for _c in _channels + [_tail_sw, _pin_bore]:
    grip = grip.cut(_c)
    pommel = pommel.cut(_c)
grip = grip.cut(Part.makeCylinder(DM_D / 2 + 0.3, DM_L + 0.3, _body0, _face_n0))
grip = grip.cut(Part.makeCylinder(4.3, 8.3, _entry - _face_n0 * 0.3, _face_n0))
grip = grip.cut(Part.makeCylinder(PUSH_D / 2 + 0.3, 30.0, _entry - _face_n0 * 10.0, _face_n0))
grip = grip.removeSplitter()
pommel = pommel.removeSplitter()
mqr_plate = mqr_plate.cut(Part.makeCylinder(CABLE_OD / 2 + 0.5, 20.0, V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate0 - 5.0)))
mqr_plate = mqr_plate.cut(Part.makeCylinder(HOSE_OUT_OD / 2 + 0.3, 20.0, V(COLL_INLET.x, COLL_INLET.y, z_mqr_plate0 - 5.0)))   # into the collector
# The grip (2026-11-21: it stood on the plate and ran 913 mm3 into it): its root in a cup
# on the plate, an M3 x 50 across the cup and the wood (nut in a socket in the cup's wall).
GRIP_CUP_L, GRIP_CUP_WALL = 10.0, 4.0
grip = grip.cut(mqr_plate).removeSplitter()
_cup = Part.makeBox(2 * (GRIP_KEYS[0][1] + GRIP_CUP_WALL), 2 * (GRIP_KEYS[0][2] + GRIP_CUP_WALL), GRIP_CUP_L + 0.5,
                    V(-(GRIP_KEYS[0][1] + GRIP_CUP_WALL), -(GRIP_KEYS[0][2] + GRIP_CUP_WALL), z_mqr_plate0 - GRIP_CUP_L))
_cup = _cup.cut(grip_full).cut(Part.makeCompound(_channels))
# no wall on the finger side: the lever swings there (its hub is 13 off the grip)
_cup = _cup.cut(Part.makeBox(100, 200, 50, V(-100 - 14.0, -100, z_mqr_plate0 - 40.0))).removeSplitter()
mqr_plate = mqr_plate.fuse(_cup).removeSplitter()
CONTROL_FAST = []
for _sy in (-1, 1):
    _yo = _sy * (GRIP_KEYS[0][2] + GRIP_CUP_WALL)
    CONTROL_FAST.append(FA.m3_at("grip root in the rear plate's cup", V(12.0, _yo, z_mqr_plate0 - GRIP_CUP_L / 2), V(0, -_sy, 0),
                                 0.0, 20.0 - FA.NUT_T - 1.0, 20.0, nut_slot=(ZA, GRIP_CUP_L / 2 + 1.0)))
_lug_out = LEV_T / 2 + LUG_GAP + GRIP_LUG_T
CONTROL_FAST.append(FA.m3("lever pivot: through its tube and the grip's lugs", V(P_LEV.x, 0, P_LEV.z), V(0, -1, 0),
                          [grip, grip], clip=(-_lug_out - 1.0, _lug_out + 1.0)))
# The grip is two halves split at y 0 (2026-11-21): the dead-man, the cable and the hoses lie in
# the channels between them, which one piece of wood could not take. The pivot's bolt and an
# M3 x 20 across the grip in its upper and its lower half (each where its wells clear every
# channel by GRIP_BOLT_CLEAR) clamp the halves.
GRIP_BOLT_CLEAR = 1.5
_gch = Part.makeCompound(_channels + [_tail_sw, Part.makeCylinder(DM_D / 2 + 0.3, DM_L + 0.3, _body0, _face_n0),
                                      Part.makeCylinder(PUSH_D / 2 + 0.3, 30.0, _entry - _face_n0 * 10.0, _face_n0)])
GRIP_BOLTS = []
for _band in ((0.30, 0.36, 0.42, 0.48), (0.62, 0.68, 0.74, 0.80)):
    _best = None
    for _f in _band:
        _c, _t, _n, _h, _w = grip_frame(_f)
        for _k in (-0.45, -0.3, -0.15, 0.0, 0.15, 0.3, 0.45):
            try:
                _gb = FA.m3("grip halves", _c + _n * (_k * _h), V(0, -1, 0), [grip, grip], L=20.0, clip=(-_w - 2.0, _w + 2.0))
            except ValueError:
                continue
            _d = _gb.cutter.distToShape(_gch)[0]
            if _best is None or _d > _best[0]:
                _best = (_d, _f, _k, _gb)
    GRIP_BOLTS.append(_best)
CONTROL_FAST += [b_[3] for b_ in GRIP_BOLTS]
grip_bolt_clear = min(b_[0] for b_ in GRIP_BOLTS)
mqr_plate, grip = cut_fast(mqr_plate, CONTROL_FAST, "rear plate"), cut_fast(grip, CONTROL_FAST, "grip")
_gy = Part.makeBox(600, 300, 800, V(-300, 0, z_mqr_plate0 - 700))
grip_r = grip.common(_gy).removeSplitter()
_gy.translate(V(0, -300, 0))
grip_l = grip.common(_gy).removeSplitter()
grip = Part.makeCompound([grip_r, grip_l])
# MQR stator on the plate: its own 4 x M4 DP10 on Ø38 (bought thread), through the plate.
for _k in range(4):
    _p = polar(19.0, 45.0 + 90.0 * _k, z_mqr_plate0)
    mqr_plate = mqr_plate.cut(Part.makeCylinder(2.2, 20.0, V(_p.x, _p.y, z_mqr_plate0 - 10.0)))
    M4_EXC.append(("M4 x 12: MQR stator on the rear plate (its M4 DP10)",
                   Part.makeCylinder(2.0, 12.0, V(_p.x, _p.y, z_mqr_plate0)).fuse(
                       Part.makeCylinder(3.5, 4.0, V(_p.x, _p.y, z_mqr_plate0 - 4.0)))))
mqr_plate = mqr_plate.removeSplitter()
lever = lever_at(0.0)
# --- collector 1 -> 6 (2026-11-21, owner): the MQR6's stator has six M5 ports and no common
# one. A bought aluminium manifold (G1/8 in from below, six M5 out on top, est. 64 x 16 x 10)
# on a tab of the rear plate on +y, 2 x M3 x 20 through its own holes (nuts on the tab's rear
# face). PU 4 x 2.5 hoses run to M5 push-in fittings in the stator's ports. The ports, from the
# drawing (docs/img/mqr6_dims.png): 29 + 8.2 k from the rotor's face, 60 deg apart round the body
# (a helix, 2026-11-23; it was assumed a row on +y). Each hose runs in its own plane round r 58,
# outside the bearing cage's legs; the ones nearest the plate take the outer outlets, so none crosses.
COLL_X, COLL_Y0, COLL_Y1, COLL_H = 24.0, 35.0, 51.0, 10.0
COLL_PITCH, COLL_OUT_Y, COLL_FIT_D, COLL_FIT_H = 7.0, 40.0, 7.0, 8.0
MQR_PORT_PITCH, MQR_FIT_D, MQR_FIT_L, COLL_HOSE_OD = 8.2, 7.0, 10.0, 4.0
_zc0, _zc1 = z_mqr_plate1, z_mqr_plate1 + COLL_H
coll_tab = Part.makeBox(2 * COLL_X, COLL_Y1 + 7.0 - 40.0, z_mqr_plate1 - z_mqr_plate0, V(-COLL_X, 40.0, z_mqr_plate0))
mqr_plate = mqr_plate.fuse(coll_tab).cut(Part.makeCylinder(HOSE_OUT_OD / 2 + 0.3, 20.0, V(COLL_INLET.x, COLL_INLET.y,
                                                                                       z_mqr_plate0 - 5.0))).removeSplitter()
collector = Part.makeBox(2 * COLL_X, COLL_Y1 - COLL_Y0, COLL_H, V(-COLL_X, COLL_Y0, _zc0))
MQR_PORT_W = (90.0, 30.0, -30.0, -90.0, -150.0, 150.0)        # world angle of port 1..6
COLL_ARC_R = 58.0
_xo = [COLL_PITCH * 0.5, COLL_PITCH * 1.5, COLL_PITCH * 2.5, -COLL_PITCH * 0.5, -COLL_PITCH * 1.5, -COLL_PITCH * 2.5]   # by port
_zp = [z_rotor1 - 29.0 - k_ * MQR_PORT_PITCH for k_ in range(N)]
_zh = list(_zp)
_zh[0] = _zp[0] - 1.5                                         # port 1's run: off the 61812's retainer
_zh[5] = _zp[5] + 2.0                                         # port 6's run: over the outlets' tops


def _wp(r_, w_, z_=0.0):
    return V(r_ * math.cos(math.radians(w_)), r_ * math.sin(math.radians(w_)), z_)


_fits = [Part.makeCylinder(COLL_FIT_D / 2, COLL_FIT_H, V(x_, COLL_OUT_Y, _zc1)) for x_ in _xo]
_fits += [Part.makeCylinder(MQR_FIT_D / 2, MQR_FIT_L, _wp(MQR_D / 2 - 1.0, w_, z_), _wp(1.0, w_)) for w_, z_ in zip(MQR_PORT_W, _zp)]
coll_fittings = Part.makeCompound(_fits)
_hz0 = _zc1 + COLL_FIT_H - 1.0
coll_hoses = []
for x_, w_, z_, zh_ in zip(_xo, MQR_PORT_W, _zp, _zh):
    _y_e = math.sqrt(COLL_ARC_R ** 2 - x_ ** 2)
    _we = math.degrees(math.atan2(_y_e, x_))
    _w0 = w_ % 360.0 if x_ < 0 else w_                        # the left ones go round by -x
    _pts = [_wp(MQR_D / 2 - 1.0 + MQR_FIT_L - 1.0, w_, z_), _wp(42.0, w_, zh_)]
    if abs(_w0 - _we) > 10.0:
        _n = int(math.ceil(abs(_we - _w0) / 15.0))
        _pts += [_wp(COLL_ARC_R, _w0 + (_we - _w0) * i_ / float(_n), zh_) for i_ in range(_n + 1)]
    _pts += [V(x_, 46.0, zh_), V(x_, COLL_OUT_Y, max(zh_ - 2.0, _hz0 + 1.0)), V(x_, COLL_OUT_Y, _hz0)]
    coll_hoses.append(G.fuse_all(tube_path(_pts, COLL_HOSE_OD / 2).Solids).removeSplitter())
coll_hoses = Part.makeCompound(coll_hoses)
COLL_FAST = [FA.m3("collector on the rear plate's tab", V(s_ * 10.5, 47.5, _zc1 + 1.0), V(0, 0, -1), [collector, mqr_plate],
                   head_on_face=True, nut_on_face=True, clip=(0.5, COLL_H + 7.5)) for s_ in (-1, 1)]
collector, mqr_plate = cut_fast(collector, COLL_FAST, "collector"), cut_fast(mqr_plate, COLL_FAST, "rear plate")
CONTROL_FAST += COLL_FAST
coll_hose_gap = min(gap(a_, b_) for i_, a_ in enumerate(coll_hoses.Solids) for b_ in coll_hoses.Solids[i_ + 1:])
hand_left = tube_path([grip_frame(f_)[0] for f_ in (0.32, 0.5, 0.66, 0.78)], 36.0)

# --- feed gate: a pin across the neck from aft, spring-closed, pulled out by the cable
Z_NECK = Z_BALL_OPEN
NECK_R = _fb["NECK_ID"] / 2.0
NECK_OR = NECK_R + _fb["NECK_WALL"]
x_gate = X_STAR + STAR_R + 0.5 + GATE_PIN_D / 2 + 1.0
z_neck_aft = Z_NECK - NECK_OR                      # neck's outer face, aft side, at y 0
z_pin_tip = Z_NECK - NECK_R + GATE_IN              # closed
GATE_HW, GATE_L = 8.0, 26.0
z_gh0 = z_neck_aft - GATE_L
gate_housing = Part.makeBox(2 * GATE_HW, 2 * GATE_HW, GATE_L + 10.0, V(x_gate - GATE_HW, -GATE_HW, z_gh0)).cut(
    Part.makeCylinder(NECK_OR, 60.0, V(x_gate - 30.0, 0, Z_NECK), V(1, 0, 0)))
_cav0, _cav1 = z_gh0 + 3.0, z_neck_aft - 2.0
gate_housing = gate_housing.cut(Part.makeCylinder(5.0, _cav1 - _cav0, V(x_gate, 0, _cav0)))
gate_housing = gate_housing.cut(Part.makeCylinder(GATE_PIN_D / 2 + 0.15, 10.0, V(x_gate, 0, _cav1 - 1.0)))
gate_housing = gate_housing.cut(Part.makeCylinder(1.0, 5.0, V(x_gate, 0, z_gh0 - 1.0))).removeSplitter()
# The Bowden housing's end (2026-11-21, it stood on the housing's flat bottom): a seat GATE_SEAT
# deep in a boss under the housing. The other end sits on the channel's shoulder at the stop in
# the grip, so the housing lies between two seats and cannot leave either.
GATE_SEAT = 5.0
gate_housing = gate_housing.fuse(Part.makeBox(2 * GATE_HW - 4.0, 2 * GATE_HW - 4.0, GATE_SEAT + 1.0,
                                              V(x_gate - GATE_HW + 2.0, -GATE_HW + 2.0, z_gh0 - GATE_SEAT - 1.0)))
gate_housing = gate_housing.cut(Part.makeCylinder(CABLE_OD / 2 + 0.2, GATE_SEAT + 1.0, V(x_gate, 0, z_gh0 - GATE_SEAT - 2.0)))
gate_housing = gate_housing.cut(Part.makeCylinder(1.0, 5.0, V(x_gate, 0, z_gh0 - 2.0))).removeSplitter()
feed_head = feed_head.cut(Part.makeCylinder(GATE_PIN_D / 2 + 0.15, NECK_OR - NECK_R + 2.0,
                                            V(x_gate, 0, z_neck_aft - 1.0)))
# The housing is glued onto the neck and the shroud's side wall below it: it takes
# their shape (the side wall runs down past the neck on the aft side).
CUP_BOLT_R = 0.5 * (_fb["RING_ID"] / 2.0 + _fb["RING_OD"] / 2.0)
X_RING0 = _fb["X_SEAT"]
gate_housing = gate_housing.fuse(Part.makeBox(X_RING0 - (x_gate + GATE_HW) + 0.5, 2 * GATE_HW, 16.0,
                                              V(x_gate + GATE_HW - 0.5, -GATE_HW, Z_NECK - CUP_BOLT_R - 8.0)))
_cup_boss = Part.makeBox(7.5, 2 * GATE_HW, 16.0, V(X_RING0 - 7.0, -GATE_HW, Z_NECK + CUP_BOLT_R - 8.0))
feed_head = feed_head.fuse(_cup_boss.cut(Part.makeCylinder(NECK_OR + 0.01, 80.0, V(X_RING0 - 40.0, 0, Z_NECK), V(1, 0, 0))))
gate_housing = gate_housing.cut(feed_head).removeSplitter()
_cupf = X_RING0 + _fb["RING_T"] + 0.15 + _fb["CUP_FLOOR"]           # the cup floor's inner face
CUP_FAST = [FA.m3_at("cup on the feed head, through the gate housing", V(_cupf, 0, Z_NECK - CUP_BOLT_R), V(-1, 0, 0),
                     0.0, 20.0 - FA.NUT_T - 1.0, 20.0, nut_slot=(V(0, 1, 0), GATE_HW + 1.0)),
            FA.m3("cup on the feed head", V(_cupf, 0, Z_NECK + CUP_BOLT_R), V(-1, 0, 0), [feed_cup, feed_head],
                  head_on_face=True, nut_on_face=True, clip=(-0.01, 25.0))]
feed_cup, feed_head, gate_housing = [cut_fast(x_, CUP_FAST, n_) for x_, n_ in
                                     ((feed_cup, "cup"), (feed_head, "feed head"), (gate_housing, "gate housing"))]
gate_housing = Part.makeCompound([s_ for s_ in gate_housing.Solids if s_.Volume > 50.0]) \
    if len(gate_housing.Solids) > 1 else gate_housing


def gate_at(open_):
    """(pin with collar, spring) closed (False) or pulled open (True)."""
    dz_ = -GATE_TRAVEL if open_ else 0.0
    c0 = _cav1 - 2.0 + dz_
    pin = Part.makeCylinder(GATE_PIN_D / 2, z_pin_tip + dz_ - c0, V(x_gate, 0, c0)).fuse(
        Part.makeCylinder(4.5, 2.0, V(x_gate, 0, c0))).removeSplitter()
    spring = tube(8.0, 6.8, _cav0, c0, x_gate, 0.0)
    return pin, spring, c0 - _cav0


gate_pin, gate_spring, gate_spring_closed = gate_at(False)
gate_pin_open, gate_spring_open, gate_spring_opened = gate_at(True)
# Cable: housing from the gate along the top, left of the strap loop, round the rear
# bearing disk, through the rear plate (outside the stator) into the grip, down its
# back to the stop in the pommel; the wire runs to the lever's tail. 2026-11-22: the run over
# the liner went 6 mm lower (x 122 -> 116): it lies under the EVA skin and the liner's glue lands
# (it reached r 128.1 against the skin's bore 127) and comes out through a window to the gate.
CABLE_X, CABLE_Y = 116.0, -30.0
CABLE_W = math.degrees(math.atan2(CABLE_Y, CABLE_X))
_cab_ex = [V(x_gate, 0, z_gh0 - 1.0), V(x_gate, 0, z_gh0 - 15.0), V(CABLE_X, CABLE_Y, z_gh0 - 70.0),
           V(CABLE_X, CABLE_Y, -120.0), V(CABLE_X, CABLE_Y, z_mqr_plate1 + 55.0), V(92.0, -18.0, z_mqr_plate1 + 25.0),
           V(CABLE_HOLE[0], CABLE_HOLE[1], z_mqr_plate1 + 10.0), _cab_in[0]]
cable_ex = tube_path(_cab_ex, CABLE_OD / 2)
gate_cable = Part.makeCompound([cable_ex, cable_in])
CABLE_LEN = path_len(_cab_ex) + path_len(_cab_in)
gate_parts = Part.makeCompound([gate_housing, gate_pin, gate_spring])

# ============================================================ frame on M6 studs (2026-11-21)
# Bare M6 studs, a nut and a washer on either face of every element they pass, at
# STUD_R outside the liner and the rings. Bays (world angles):
#   1: rear 6808 disk -> front 6808 disk -> the liner's rear lugs, at 45/135/225/315;
#   2: the liner's front lugs -> crank bracket plate A at 97.5 (it stops in plate A, behind the
#      lay bevel; the gear-60 bracket's foot has its own 2 x M3 into the front ring) and
#      the liner's front lugs -> front ring at 150/210/270, which run on
#      to the front bearing's housing (and clamp its rear retainer), with 300;
#   box: front ring -> star-drive box's rear plate at -39 / 13 (nut sunk in its front face);
#   struts: rear 6808 disk -> rear plate, four inclined studs (bosses square to them).
# The liner is two halves split at 0 / 180 deg (the fingers go in with the stations and
# no ring goes over them): M3 x 20 across lug pairs at its rear end, top and bottom; at the
# front the carry post's base (top) and the keel (bottom) bridge the split, so does the ramp block.
W90 = 97.5                             # the crank side's stud: 22.5 off the lay bevel's axis, clear of plate A's 608
BAY1, BAY2, BAY3 = (45.0, 135.0, 225.0, 315.0), (W90, 150.0, 210.0, 270.0), (150.0, 210.0, 270.0, 300.0)
BOX_TIES = (BOX_A0 + 6.0, BOX_A1 - 3.0)
LUG_T = 10.0
NUT_STACK = FA.M6_WASHER_T + FA.M6_NUT_T


def wpt(r, w, z=0.0):
    a = math.radians(w)
    return V(r * math.cos(a), r * math.sin(a), z)


def stud_lug(r_in, w, z0, z1, r=STUD_R, d=STUD_LUG_D):
    """A lug from radius r_in out round a stud at (r, w), z0..z1."""
    c = Part.makeCylinder(d / 2, z1 - z0, wpt(r, w, z0))
    b = Part.makeBox(r - r_in + 1.0, d, z1 - z0, V(r_in - 1.0, -d / 2, z0))
    b.rotate(O, ZA, w)
    return c.fuse(b).removeSplitter()


def _wdiff(a, b):
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def skin_land(z0, z1, skip=(), open_=()):
    """Glue land for the EVA skin (2026-11-22) in a band of lugs z0..z1: a hoop LAND_T thick out to
    SKIN_R_IN on radial ribs every 30 deg (none within skip = [(angle, half width)]); open_ =
    [(a0, a1), ...]: no land on those sectors, a rib at either end of the hoop."""
    ribs_ = [w for w in LAND_RIB_ANGLES if all(_wdiff(w, a_) >= h_ for a_, h_ in skip)]
    for a0_, a1_ in open_:
        ribs_ = [w for w in ribs_ if _wdiff(w, 0.5 * (a0_ + a1_)) > 0.5 * (a1_ - a0_) + 6.0] + [a1_ + 2.5, a0_ - 2.5]
    parts_ = [tube(2.0 * SKIN_R_IN, 2.0 * (SKIN_R_IN - LAND_T), z0, z1)]
    for w in ribs_:
        b_ = Part.makeBox(SKIN_R_IN - LAND_T + 0.5 - (r_case_od - 1.0), LAND_RIB_T, z1 - z0,
                          V(r_case_od - 1.0, -LAND_RIB_T / 2.0, z0))
        b_.rotate(O, ZA, w)
        parts_.append(b_)
    land_ = G.fuse_all(parts_)
    for a0_, a1_ in open_:
        wedge_ = Part.makeCylinder(SKIN_R_IN + 5.0, z1 - z0 + 2.0, V(0, 0, z0 - 1.0), ZA, a1_ - a0_)
        wedge_.rotate(O, ZA, a0_)
        land_ = land_.cut(wedge_)
    return land_.removeSplitter()


# --- the liner: lugs for bays 1 and 2, split-lug pairs, the halves
z_lr0, z_lr1 = z_cam0, z_cam0 + LUG_T
z_lf0, z_lf1 = z_cam1 - LUG_T, z_cam1
FRING_LAND_OPEN = (BOX_A0 - 5.0, BOX_A1 + 5.0)         # the box and the feed head on top of the front ring
# Rear band: no land within 30 deg of the split (0 / 180): the key to the halves' M3 x 20 comes
# in there along the split lugs, and its way grazed the hoop's bore (a cut there left the right
# half 5.6 mm3 short of its cutters).
LINER_LAND_OPEN = [(-30.0, 30.0), (150.0, 210.0)]
# 2026-11-23: the wrap handle's two rails run under the lands at these world angles, both between
# ribs: low on the left and high on the right, the handle goes round the top from one to the other.
CARRY_W = (240.0, 60.0)
SKIN_LANDS = [skin_land(z_lr0, z_lr1, skip=[(CABLE_W, 8.0)], open_=LINER_LAND_OPEN),
              skin_land(z_lf0, z_lf1, skip=[(CABLE_W, 8.0)]),
              skin_land(Z_FRING0, Z_FRING1, open_=[FRING_LAND_OPEN])]
SKIN_LANDS_Z = [(z_lr0, z_lr1, "liner, rear lugs"), (z_lf0, z_lf1, "liner, front lugs"), (Z_FRING0, Z_FRING1, "front ring")]
_ll = [stud_lug(r_case_od, w, z_lr0, z_lr1) for w in BAY1] + [stud_lug(r_case_od, w, z_lf0, z_lf1) for w in BAY2]
_ll += SKIN_LANDS[:2]
SPLIT_LUG_H, SPLIT_LUG_W = 13.0, 19.0
_split_bands = [(0.0, z_lr0, z_lr1), (180.0, z_lr0, z_lr1)]     # the front: the carry base (top), the keel (bottom)
for w, za, zb in _split_bands:
    _b = Part.makeBox(SPLIT_LUG_H + 1.0, SPLIT_LUG_W, zb - za, V(r_case_od - 1.0, -SPLIT_LUG_W / 2, za))
    _b.rotate(O, ZA, w)
    _ll.append(_b)
cam = cam.fuse(Part.makeCompound(_ll)).removeSplitter()
cam_outside = cam_outside.fuse(Part.makeCompound(_ll)).removeSplitter()
_half = Part.makeBox(600, 300, 1000, V(-300, 0, -500))
cam_r = cam.common(_half)
_halfm = _half.copy()
_halfm.translate(V(0, -300, 0))
cam_l = cam.common(_halfm)
LINER_FAST = []
for w, za, zb in _split_bands:
    _p = wpt(r_case_od + SPLIT_LUG_H / 2, w, 0.5 * (za + zb))
    LINER_FAST.append(FA.m3("liner halves", _p, V(0, -1, 0), [cam_r, cam_l], clip=(-SPLIT_LUG_W / 2 - 1, SPLIT_LUG_W / 2 + 1)))
cam_r, cam_l = cut_fast(cam_r, LINER_FAST, "liner right"), cut_fast(cam_l, LINER_FAST, "liner left")
cam = cut_fast(cam, LINER_FAST, "liner")
liner_halves_ok = len(cam_r.Solids) == 1 and len(cam_l.Solids) == 1

# --- front ring, bearing disks, the housing, the box: lugs
pack_frame = pack_frame.fuse(Part.makeCompound([stud_lug(r_case_od, w, Z_FRING0, Z_FRING1)
                                                for w in sorted(set((90.0,) + BAY2[1:] + BAY3 + BOX_TIES))]
                                               + [SKIN_LANDS[2]])).cut(feed_head).removeSplitter()
# --- the guard (2026-11-21: it stood on nothing): two webs out to the front ring's inner
# face, an M3 x 20 each, radially from the ring's outer face, the nut slid into the web.
# z set by hand for the front ring at 202.3; since 2026-11-22 (the breech trough) it stands TRAY_L further
# forward with the barrel, and the webs and the head's boss with it.
_DZ_RING = Z_FRING0 - 202.31
GUARD_WEBS = ((30.0, 188.0 + _DZ_RING, 206.0 + _DZ_RING), (84.0, 195.0 + _DZ_RING, 213.0 + _DZ_RING))   # world angle, z0, z1
FEED_FAST = []
for w, za, zb in GUARD_WEBS:
    _wb = Part.makeBox(r_case_id - 0.05 - (GUARD_R_OUT - 0.7), 9.0, zb - za, V(GUARD_R_OUT - 0.7, -4.5, za))
    _wb.rotate(O, ZA, w)
    feed_guard = feed_guard.fuse(_wb)
    _zb = 0.5 * (max(za, Z_FRING0) + min(zb, Z_FRING1))
    FEED_FAST.append(FA.m3_at("guard web on the front ring", wpt(r_case_od, w, _zb), wpt(-1.0, w), 0.0,
                              20.0 - FA.NUT_T - 1.0, 20.0, nut_slot=(wpt(1.0, w + 90.0), 6.5)))
feed_guard, pack_frame = cut_fast(feed_guard.removeSplitter(), FEED_FAST, "guard"), cut_fast(pack_frame, FEED_FAST, "front ring")
feed_guard = feed_guard.cut(tube(2 * r_case_od + 2.0, 2 * r_case_id, Z_FRING0 - 1.0, Z_FRING1 + 1.0)).removeSplitter()   # webs' corners off the ring
# --- the feed head (2026-11-21: it stood in a notch of the front ring): a boss on its web
# where the web crosses the ring (-26 deg), an M3 x 20 radially from the ring's outer face.
# On the shroud's web where it crosses the ring, 4 deg short of its end (-26 set by hand until 2026-11-22;
# the 4-pocket star stands further out and its web crosses the ring at -32).
_a_web = math.radians(_fb["SHROUD_WEB_END"] - 4.0)
_r_web = 0.5 * (_fb["SHROUD_R_IN"] + _fb["SHROUD_R_OUT"])
HEAD_WEB_W = -math.degrees(math.atan2(_r_web * math.sin(_a_web), X_STAR + _r_web * math.cos(_a_web)))
_hb = Part.makeBox(r_case_id - 0.05 - 90.0, 9.0, 8.0, V(90.0, -4.5, 200.0 + _DZ_RING))
_hb.rotate(O, ZA, HEAD_WEB_W)
feed_head = fuse_sound(feed_head, _hb.cut(tube(2 * r_case_od + 2.0, 2 * r_case_id, Z_FRING0 - 1.0, Z_FRING1 + 1.0)),
                       "feed head + its web boss (fuse)")
FEED_FAST.append(FA.m3_at("feed head web on the front ring", wpt(r_case_od, HEAD_WEB_W, 204.0 + _DZ_RING), wpt(-1.0, HEAD_WEB_W),
                          0.0, 20.0 - FA.NUT_T - 1.0, 20.0, nut_slot=(wpt(1.0, HEAD_WEB_W + 90.0), 6.0)))
feed_head, pack_frame = cut_fast(feed_head, FEED_FAST[-1:], "feed head"), cut_fast(pack_frame, FEED_FAST[-1:], "front ring")
# --- the star's shaft (2026-11-21). It turned in printed holes and in a slot through the front
# ring (the shaft's hole was wider than the ring's 4 mm wall: the ring was cut through at the
# top), nothing stopped it aft, and the star was 7 mm loose on its D-flat. Now a pad closes the
# ring at the top and takes the locating 608: in from behind, the pad's floor ahead, a cover
# behind on 2 x M3 x 20 (heads on the cover, nuts on the pad's front face). The star is pinned
# to the shaft by an M3 x 20 across its hub (the old collar, one print with the star); the
# hub's spigot and a steel spacer 10 x 1 through the floor clamp the 608's inner race with a
# collar ahead of the pad (M3 x 20 across it and the shaft), STAR_SPIGOT_GAP of float. The
# other 608 floats in the box's rear plate (train section).
COVER_T, STAR_SPIGOT_GAP = 3.0, 0.15
PAD_X0, PAD_X1, PAD_Y = 95.0, 124.0, 19.0
z_sf = star0.BoundBox.ZMax                                     # the star's front face
z_hub1 = Z_FRING0 - COVER_T - TRAIN_GAP
z_scol0, z_scol1 = Z_FRING1 + TRAIN_GAP, BOX_Z0 - TRAIN_GAP     # the collar, between the pad and the box
_pad = Part.makeBox(PAD_X1 - PAD_X0, 2 * PAD_Y, Z_FRING1 - Z_FRING0, V(PAD_X0, -PAD_Y, Z_FRING0))
pack_frame = pack_frame.fuse(_pad).cut(feed_head).removeSplitter()
pack_frame = pack_frame.cut(Part.makeCylinder(SB_OD / 2 + 0.1, SB_W + 1.0, V(S_C.x, S_C.y, Z_FRING0 - 1.0)))
pack_frame = pack_frame.cut(Part.makeCylinder(5.5, 40.0, V(S_C.x, S_C.y, Z_FRING0 - 10.0))).removeSplitter()
star_brg_pad = tube(SB_OD, SHAFT_D, Z_FRING0, Z_FRING0 + SB_W, S_C.x, S_C.y)
star_bearings = Part.makeCompound([star_brg_pad, star_brg_box])
star_spacer = tube(10.0, SHAFT_D, Z_FRING0 + SB_W, z_scol0, S_C.x, S_C.y)
_cov_b = [V(S_C.x + 7.5, s_ * 13.0, 0) for s_ in (-1, 1)]
star_cover = G.fuse_all([Part.makeCylinder(12.0, COVER_T, V(S_C.x, S_C.y, Z_FRING0 - COVER_T)),
                         Part.makeBox(7.5, 26.0, COVER_T, V(S_C.x, -13.0, Z_FRING0 - COVER_T))]
                        + [Part.makeCylinder(5.0, COVER_T, V(q_.x, q_.y, Z_FRING0 - COVER_T)) for q_ in _cov_b])
star_cover = star_cover.cut(Part.makeCylinder(7.5, 10.0, V(S_C.x, S_C.y, Z_FRING0 - 5.0))).removeSplitter()
STAR_FAST = [FA.m3("star bearing cover on the front ring's pad", V(q_.x, q_.y, Z_FRING0 - COVER_T - 1.0), ZA,
                   [star_cover, pack_frame], head_on_face=True, nut_on_face=True, clip=(0.5, COVER_T + 14.0 + 1.5))
             for q_ in _cov_b]
star_cover, pack_frame = cut_fast(star_cover, STAR_FAST, "star bearing cover"), cut_fast(pack_frame, STAR_FAST, "front ring")
star_hub = G.fuse_all([tube(20.0, SHAFT_D + 0.2, z_sf - 0.1, z_hub1, S_C.x, S_C.y),
                       tube(10.0, SHAFT_D + 0.2, z_hub1 - 0.1, Z_FRING0 - STAR_SPIGOT_GAP, S_C.x, S_C.y)]).removeSplitter()
STAR_FAST.append(FA.m3("star on its shaft (hub)", V(S_C.x, S_C.y + 10.0, 0.5 * (z_sf + z_hub1)), V(0, -1, 0),
                       [star_hub, star_hub], clip=(-0.01, 20.01)))
star_hub = cut_fast(star_hub, STAR_FAST[-1:], "star hub")
STAR_HUB_BODY = Part.makeCompound([star_hub, STAR_FAST[-1].body])
star0 = fuse_sound(star0, star_hub, "star + its hub")
star_collar = Part.makeCylinder(10.0, z_scol1 - z_scol0, V(S_C.x, S_C.y, z_scol0)).cut(
    Part.makeCylinder(SHAFT_D / 2 + 0.1, 50.0, V(S_C.x, S_C.y, z_scol0 - 10.0)))
STAR_FAST.append(FA.m3("star shaft collar", V(S_C.x, S_C.y + 10.0, 0.5 * (z_scol0 + z_scol1)), V(0, -1, 0),
                       [star_collar, star_collar], clip=(-0.01, 20.01)))
star_collar = cut_fast(star_collar, STAR_FAST[-1:], "star shaft collar")
for _zc in (0.5 * (z_sf + z_hub1), 0.5 * (z_scol0 + z_scol1)):
    star_shaft = star_shaft.cut(Part.makeCylinder(1.6, 24.0, V(S_C.x, S_C.y + 12.0, _zc), V(0, -1, 0)))
FEED_FAST += STAR_FAST
# --- gears A and B are one print (the cluster turns on a fixed layshaft pin)
# Its hub ahead of A stays inside B's root circle: the idler's tips reach down to it (2026-11-22: B 14
# has its roots on r 8.6, the Ø20 hub took 0.67 mm3 of the idler).
_ab_hub_d = min(20.0, 2.0 * (R_B - 1.25 * GEAR_M) - 1.0)
gear_ab = G.fuse_all([gear_a, gear_b, tube(_ab_hub_d, SHAFT_D + 0.2, P1_Z1 - 0.5, P2_Z0 + 0.5, L_C.x, L_C.y),
                      tube(20.0, SHAFT_D + 0.2, _cav_r + TRAIN_GAP, P1_Z0 + 0.1, L_C.x, L_C.y),
                      tube(_ab_hub_d, SHAFT_D + 0.2, P2_Z1 - 0.1, _cav_f - TRAIN_GAP, L_C.x, L_C.y)]).removeSplitter()
_ec = {"liner_r": (z_lr0, z_lr1),
       "liner_f": (z_lf0, z_lf1), "fring": (Z_FRING0, Z_FRING1), "housing": (z_brg0 - 3.0, z_brg1 + 3.0),
       "box": (BOX_Z0, P1_Z0 - 1.0)}


def stud_through(name, w, elems, nuts=None):
    """M6 stud along z at (STUD_R, w) through elems (keys of _ec), a nut on either face of each."""
    faces = [_ec[e] for e in elems]
    if nuts is None:
        nuts = [(f[0], -1) for f in faces] + [(f[1], +1) for f in faces]
    z0 = min(z for z, sd in nuts if sd < 0) - NUT_STACK - 2.0
    z1 = max(z for z, sd in nuts if sd > 0) + NUT_STACK + 2.0
    return FA.m6_stud(name, wpt(STUD_R, w, z0), wpt(STUD_R, w, z1), [(z - z0, sd) for z, sd in nuts])


FRAME_STUDS = []
# 2026-11-22: the bay-1 studs run on straight back to the rear plate (a nut either side of its
# lug): the frame is a cylinder to the MQR, and the EVA skin goes on round it to the grip. Four
# inclined studs from the rear 6808 disk to a plate R 50 (a cone) did that until then.
for w in BAY1:
    _fc = [_ec["liner_r"]]
    FRAME_STUDS.append(stud_through("bay 1 (rear plate, liner rear) %.0f" % w, w, [],
                                    nuts=[(f_[0], -1) for f_ in _fc] + [(f_[1], +1) for f_ in _fc]
                                    + [(z_mqr_plate0, -1), (z_mqr_plate0 + SPIDER_LUG_L, +1)]))
# plate A of the crank bracket on the W90 stud: a boss behind it, the front nut sunk in plate A
# (the lay bevel is just ahead of it); the gear-60 bracket's foot on the front ring: 2 x M3 x 20.
_cbs = sorted(crank_bracket.Solids, key=lambda s_: s_.BoundBox.ZMin)
_pa, _prm = _cbs[0], _cbs[1]            # plate A with the crank boss; the gear-60 bracket on the front ring
_iv = [iv for iv in FA.intervals(_pa, wpt(STUD_R, W90), ZA) if iv[1] - iv[0] > 2.0]
assert _iv, "crank plate A misses its stud: %s" % _iv
_pa_z0, _pa_z1 = _iv[0][0], _iv[-1][1]
PA_BOSS_L = 16.0
_pa = _pa.fuse(Part.makeCylinder(STUD_LUG_D / 2, PA_BOSS_L + 0.5, wpt(STUD_R, W90, _pa_z0 - PA_BOSS_L))).removeSplitter()
_pa_nut = _pa_z1 - NUT_STACK - 2.5
FRAME_STUDS.append(stud_through("bay 2 %.1f (liner front, crank plate A)" % W90, W90, ["liner_f"],
                                nuts=[(z_lf0, -1), (z_lf1, +1), (_pa_z0 - PA_BOSS_L, -1), (_pa_nut, +1)]))
_pa = _pa.cut(Part.makeCylinder(FA.M6_WASHER_D / 2 + 0.8, NUT_STACK + 4.0, wpt(STUD_R, W90, _pa_nut))).removeSplitter()
CRANK_FAST = []
for _sx in (-4.5, 4.5):
    _p = V(_sx, 111.0 * CRANK_SIDE, z_cboss_r1)
    CRANK_FAST.append(FA.m3("gear-60 bracket foot on the front ring", _p, V(0, 0, -1), [_prm, pack_frame],
                            clip=(-0.01, z_cboss_r1 - Z_FRING0 + 0.01)))
_prm, pack_frame = cut_fast(_prm, CRANK_FAST, "gear-60 bracket"), cut_fast(pack_frame, CRANK_FAST, "front ring")
for w in (150.0, 210.0, 270.0):
    FRAME_STUDS.append(stud_through("bay 2+3 %.0f (liner front, front ring, bearing housing)" % w, w,
                                    ["liner_f", "fring", "housing"]))
FRAME_STUDS.append(stud_through("bay 3 300 (front ring, bearing housing)", 300.0, ["fring", "housing"]))
# The box stands on the front ring on a boss round each tie: the ring and the box are clamped
# between the ring's rear nut and the nut sunk in the box. Until 2026-11-21 a nut and washer sat
# on either face of the 8.4 mm gap between them: two stacks of 6.6 in one place, 4.8 mm deep in
# each other.
_box_sock = []
for w in BOX_TIES:
    _zf = P1_Z0 - 1.0
    FRAME_STUDS.append(stud_through("front ring to the star-drive box %.0f" % w, w, ["fring", "box"],
                                    nuts=[(Z_FRING0, -1), (_zf - NUT_STACK - 0.5, +1)]))
    _box_sock.append(Part.makeCylinder(FA.M6_WASHER_D / 2 + 0.8, NUT_STACK + 2.0, wpt(STUD_R, w, _zf - NUT_STACK - 0.5)))
gearbox = gearbox.fuse(Part.makeCompound([Part.makeCylinder(STUD_LUG_D / 2, BOX_Z0 - Z_FRING1 + 0.5, wpt(STUD_R, w, Z_FRING1))
                                          for w in BOX_TIES])).removeSplitter()
gearbox = gearbox.cut(Part.makeCompound(_box_sock)).removeSplitter()
box_tie_gap = BOX_Z0 - Z_FRING1
# rear plate -> a spider (2026-11-22): spokes from the hub (R 50: the MQR stator, the grip, the
# collector) out to a lug on each bay-1 stud, and a rim out to SKIN_R_IN the EVA skin is glued on
# (the skin's aft land; Ø254 fits the P2S bed). The spokes and the rim stand forward of the
# plate's aft face, where the EVA end cap is glued.
_sp = []
for w in STRUT_ANGLES:
    _b = Part.makeBox(STUD_R - (RP_R - 3.0), SPIDER_SPOKE_W, SPIDER_SPOKE_H, V(RP_R - 3.0, -SPIDER_SPOKE_W / 2, z_mqr_plate0))
    _b.rotate(O, ZA, w)
    _sp += [_b, Part.makeCylinder(STUD_LUG_D / 2, SPIDER_LUG_L, wpt(STUD_R, w, z_mqr_plate0))]
_sp.append(tube(2.0 * SKIN_R_IN, 2.0 * (SKIN_R_IN - LAND_T), z_mqr_plate0, z_mqr_plate0 + SPIDER_RIM_L))
_spider = G.fuse_all(_sp)
# The spokes keep off the hub's own bolts (the grip's root, the collector): their seats, nuts and keys.
_spider = _spider.cut(Part.makeCompound([x_ for f_ in CONTROL_FAST + AIR_FAST if f_.kind == "M3"
                                         for x_ in (f_.cutter, f_.body, f_.access)]))
mqr_plate = mqr_plate.fuse(_spider).removeSplitter()
# --- the 61812's cage (2026-11-23): a ring round the outer race with a lip ahead of it, on four legs
# between the stator's ports to the spider's spokes, a foot and an M3 x 20 each. Printed ring-down.
# A retainer ring behind the race, 3 x M3 x 6 into nuts slid into the ring from outside.
RC_RO, RC_LEG_R0, RC_LEG_W, RC_FOOT_R1, RC_FOOT_T, RC_LIP = 54.0, 47.5, 14.0, 63.0, 8.0, 1.2
RR_RO, RR_T, RR_BOLT_R = 47.2, 3.0, 44.0
RR_BOLT_W = (0.0, 120.0, 240.0)                 # clear of the legs and the stator's port hoses
z_leg0 = z_mqr_plate0 + SPIDER_SPOKE_H
rear_cage = tube(2.0 * RC_RO, RBRG["D"] + 0.2, z_rb0, z_rb1).fuse(tube(2.0 * RC_RO, RBRG["D1"], z_rb1, z_rb1 + RC_LIP))
rear_ret = tube(2.0 * RR_RO, RBRG["D1"], z_rb0 - RR_T, z_rb0)
RCAGE_FAST = [FA.m3_at("rear bearing retainer", wpt(RR_BOLT_R, w, z_rb0 - RR_T), ZA, 0.0, RR_T + 0.4, 6.0,
                       nut_slot=(wpt(1.0, w), RC_RO - RR_BOLT_R + 2.0)) for w in RR_BOLT_W]
rear_cage, rear_ret = cut_fast(rear_cage, RCAGE_FAST, "rear bearing cage"), cut_fast(rear_ret, RCAGE_FAST, "rear bearing retainer")
_legs = []
for w in STRUT_ANGLES:
    _b = Part.makeBox(RC_RO - RC_LEG_R0, RC_LEG_W, z_rb0 + 0.5 - z_leg0, V(RC_LEG_R0, -RC_LEG_W / 2, z_leg0))
    _f = Part.makeBox(RC_FOOT_R1 - RC_LEG_R0, RC_LEG_W, RC_FOOT_T, V(RC_LEG_R0, -RC_LEG_W / 2, z_leg0))
    _b.rotate(O, ZA, w)
    _f.rotate(O, ZA, w)
    _legs += [_b, _f]
rear_cage = rear_cage.fuse(Part.makeCompound(_legs)).removeSplitter()
_cf = [FA.m3("rear bearing cage on the spider", wpt(0.5 * (RC_LEG_R0 + RC_FOOT_R1) + 2.0, w, z_leg0 + RC_FOOT_T), V(0, 0, -1),
             [rear_cage, mqr_plate], clip=(-0.01, RC_FOOT_T + SPIDER_SPOKE_H + 0.01)) for w in STRUT_ANGLES]
rear_cage, mqr_plate = cut_fast(rear_cage, _cf, "rear bearing cage"), cut_fast(mqr_plate, _cf, "rear plate")
RCAGE_FAST += _cf
AIR_FAST += RCAGE_FAST
rear_struts = Part.makeCompound([f_.body for f_ in FRAME_STUDS if f_.name.startswith("bay 1")])
cam, cam_r, cam_l, cam_outside = [cut_fast(x_, FRAME_STUDS, n_) for x_, n_ in
                                   ((cam, "liner"), (cam_r, "liner right"), (cam_l, "liner left"), (cam_outside, "liner outside"))]
pack_frame, mqr_plate = [cut_fast(x_, FRAME_STUDS, n_) for x_, n_ in ((pack_frame, "front ring"), (mqr_plate, "rear plate"))]
brg_housing, brg_ret_out, gearbox = [cut_fast(x_, FRAME_STUDS, n_) for x_, n_ in
                                     ((brg_housing, "bearing housing"), (brg_ret_out, "outer race retainer"), (gearbox, "gearbox"))]
_pa, _prm = cut_fast(_pa, FRAME_STUDS, "crank plate A"), cut_fast(_prm, FRAME_STUDS, "gear-60 bracket")
crank_bracket = Part.makeCompound([_pa, _prm])
drive_parts = [(n_, crank_bracket if n_ == "crank brackets" else s_) for n_, s_ in drive_parts]
frame_studs = Part.makeCompound([f_.body for f_ in FRAME_STUDS])
frame_all = Part.makeCompound([pack_frame, frame_studs])
# EVA skin's extent (2026-11-22; built in "EVA skin" below): the rear plate's aft face to the
# bearing housing's front face; an EVA end cap on the plate's aft face, round the grip's root.
SKIN_Z0, SKIN_Z1 = z_mqr_plate0, z_brg1 + 3.0
SKIN_R_OUT = SKIN_R_IN + SKIN_T
SKIN_R_MID = SKIN_R_IN + 0.5 * SKIN_T
SKIN_L = 2.0 * math.pi * SKIN_R_MID
SKIN_LANDS_Z.append((z_mqr_plate0, z_mqr_plate0 + SPIDER_RIM_L, "rear plate's rim"))
CAP_R_IN_EST = RP_R + 4.0
STUD_ENVELOPE = STUD_R - FA.M6_NUT_AF / math.sqrt(3.0)        # nut corners toward the axis
_tick("frame on M6 studs")

# ============================================================ mass and centre of gravity (stage 7)
# Printed PETG (1.27 g/cm3): a solid skin, the rest at the profile's infill. The
# skin is V (1 - exp(-A t / V)) with t = PRINT_SKIN_T, fitted to tools/print_mass.py
# on 19 bodies of this model (5 walls, 60 %: within 6 % a body, the sum within 1 %);
# airtight (6 walls, 100 %, flow 1.05) is V x 1.27 x 1.05. Metal, wood and hoses by
# volume; bought parts by catalogue or an estimate ("est."). The carry handle and
# the strap loops are placed by this centre of gravity, then added to it.
MS_RHO = {"PETG": 1.27, "steel": 7.85, "Al": 2.70, "PU": 1.20, "TPU": 1.21, "wood": 0.70, "brass": 8.50,
          "rubber": 1.30, "EVA": 0.10}                     # EVA: cosplay sheet, est.
PRINT_SKIN_T = 1.9
PRINT_PROFILE = {"strong": (0.60, 1.00), "airtight": (1.00, 1.05)}
MS_EST = {"AirTAC M3R110": 60.0, "AirTAC fittings (2 straight + silencer)": 17.0, "pilot fitting G1/8": 8.0,
          "O-rings, M3 nuts and washers": 7.0, "61812": 109.0, "608": 12.0, "MQR6 clone (Ø46 x 90 Al)": 350.0,
          "dead-man 2/2 NC": 20.0, "brass pommel (cast shell ~1.5 mm)": 80.0,
          "61836": 1750.0, "KA070XP0": 141.0, "collector 1->6 (Al 64 x 16 x 10)": 30.0,
          "push-in fittings M5 x 12": 36.0}
MS_BOWDEN_G_PER_M = 25.0                         # 5 mm bicycle brake housing, est.
QEV_MAT = {"Rear_plug": "airtight", "Seat_ring": "airtight", "Front_cover": "airtight", "Diaphragm": "rubber",
           "Front_yoke": "strong", "Barrel_stub": "steel", "Chamber_tube": "Al", "Tie_rods": "steel",
           "Pilot_fitting": "pilot fitting G1/8", "Carriage": "strong", "Nose_clamp": "strong"}
assert set(QEV_MAT) == set(qev_closed), "new QEV part without a material: %s" % (set(qev_closed) ^ set(QEV_MAT))
mass_rows = []                                   # (group, name, grams, centre, basis)


def ms_com(shape_):
    sols_ = shape_.Solids
    if not sols_:
        return shape_.BoundBox.Center
    vt_ = sum(s_.Volume for s_ in sols_)
    c_ = V(0, 0, 0)
    for s_ in sols_:
        c_ = c_ + s_.CenterOfMass * (s_.Volume / vt_)
    return c_


def ms_add(group_, name_, shape_, mat_, frac_=1.0):
    """One body: mat_ is a print profile, a material in MS_RHO, or a key of MS_EST (bought)."""
    if mat_ in PRINT_PROFILE:
        f_, flow_ = PRINT_PROFILE[mat_]
        v_, a_ = shape_.Volume, shape_.Area
        skin_ = v_ * (1.0 - math.exp(-a_ * PRINT_SKIN_T / v_))
        g_, basis_ = MS_RHO["PETG"] * flow_ * (skin_ + f_ * (v_ - skin_)) / 1000.0, "PETG " + mat_
    elif mat_ in MS_RHO:
        g_, basis_ = MS_RHO[mat_] * shape_.Volume * frac_ / 1000.0, mat_
    else:
        g_, basis_ = MS_EST[mat_], "est. " + mat_
    mass_rows.append((group_, name_, g_, ms_com(shape_), basis_))


def ms_hose(group_, name_, shape_, od_, id_):
    ms_add(group_, name_, shape_, "PU", 1.0 - (id_ / od_) ** 2)


_tick("mass…")
for _mk in range(N):
    _mp = _mk * 60.0
    _mdz = cam_dz(_mp)
    for _mn, _ms in qev_closed.items():
        ms_add("stations", _mn, place(_ms, _mp, _mdz), QEV_MAT[_mn])
    ms_add("stations", "O-rings, nuts", place(qev_closed["Chamber_tube"], _mp, _mdz), "O-rings, M3 nuts and washers")
    ms_add("stations", "AirTAC", place(valve_body, _mp, _mdz), "AirTAC M3R110")
    ms_add("stations", "AirTAC fittings", place(valve_fit, _mp, _mdz), "AirTAC fittings (2 straight + silencer)")
    ms_add("stations", "valve bracket", place(valve_bracket, _mp, _mdz), "strong")
    ms_add("stations", "finger", place(follower, _mp, _mdz), "steel")
    ms_hose("stations", "line A", place(line_a, _mp, _mdz), HOSE_OD, HOSE_ID)
    ms_hose("stations", "line R", place(line_r(_mdz), _mp), HOSE_OD, HOSE_ID)
    ms_add("stations", "rails Al 8 x 1", place(rails_pack, _mp), "Al")
    ms_add("stations", "breech clamp, upper half", place(clamp_upper, _mp), "strong")
    ms_add("stations", "barrel", place(fixed_barrel, _mp), "steel")
for _mn, _ms, _mm in (("liner", cam, "strong"), ("frame (rings, spars)", pack_frame, "strong"),
                      ("front barrel plate", front_plate, "strong"), ("rear rail disk", rear_disk, "strong"),
                      ("firing ramp", ramp_fire, "strong"), ("ramp block", guide_block, "strong")):
    ms_add("frame", _mn, _ms, _mm)
for _mn, _ms, _mm in (("star", star0, "strong"), ("feed head", feed_head, "strong"), ("cup", feed_cup, "strong"),
                      ("TPU lip", feed_lip, "TPU"), ("guard", feed_guard, "strong"),
                      ("gate housing", gate_housing, "strong"), ("gate pin", gate_pin, "steel"),
                      ("gate spring", gate_spring, "steel")):
    ms_add("feed", _mn, _ms, _mm)
for _mn, _ms, _mm in (("hub: rim 120, lower clamp halves, bearing seat", pack_hub, "strong"),
                      ("front support " + FRONT_BRG["name"], front_bearing, FRONT_BRG.get("mat", FRONT_BRG["name"])),
                      ("bearing housing", brg_housing, "strong"), ("bearing retainers", Part.makeCompound([brg_ret_in, brg_ret_out]), "strong"),
                      ("gear A", gear_a, "strong"), ("gear B", gear_b, "strong"),
                      ("idler", gear_i, "strong"), ("star gear", gear_s, "strong"), ("gearbox", gearbox, "strong"),
                      ("star shaft", star_shaft, "steel"), ("layshaft", lay_shaft, "steel"),
                      ("idler shaft", idl_shaft, "steel")):
    ms_add("star drive", _mn, _ms, _mm)
for _mn, _ms, _mm in (("gear 60", crank_gear, "strong"), ("lay bevel", bevel_small, "strong"),
                      ("crank bevel", bevel_big, "strong"), ("lay shaft", pin_shaft, "steel"),
                      ("crank shaft", crank_shaft, "steel"), ("crank brackets", crank_bracket, "strong"),
                      ("crank arm", crank_arm, "strong"), ("knob", crank_knob, "strong"),
                      ("knob pin, head, nut", crank_knob_pin, "steel")):
    ms_add("pack drive", _mn, _ms, _mm)
for _ms in crank_bearings.Solids:
    ms_add("pack drive", "608", _ms, "608")
for _mn, _ms, _mm in (("lay shaft collar", lay_collar, "strong"), ("crank spacer", crank_spacer, "strong")):
    ms_add("pack drive", _mn, _ms, _mm)
for _ms in star_bearings.Solids:
    ms_add("star drive", "608", _ms, "608")
for _mn, _ms, _mm in (("star bearing cover", star_cover, "strong"), ("star shaft collar", star_collar, "strong"),
                      ("star shaft spacer 10 x 1", star_spacer, "steel")):
    ms_add("star drive", _mn, _ms, _mm)
ms_add("air", "rear bearing 61812", rear_bearing, "61812")
for _mn, _ms, _mm in (("rear bearing cage", rear_cage, "strong"), ("rear bearing retainer", rear_ret, "strong"),
                      ("TPU pad under the rotor", soft_coup, "TPU"), ("rear plate (spider)", mqr_plate, "strong")):
    ms_add("air", _mn, _ms, _mm)
ms_add("air", "MQR6", Part.makeCompound([mqr_rotor, mqr_stator]), "MQR6 clone (Ø46 x 90 Al)")
ms_add("air", "collector 1->6", collector, "collector 1->6 (Al 64 x 16 x 10)")
ms_add("air", "collector fittings", coll_fittings, "push-in fittings M5 x 12")
ms_add("air", "rotor fittings", rotor_fittings, "push-in fittings M5 x 12")
ms_hose("air", "collector hoses 4 x 2.5", coll_hoses, COLL_HOSE_OD, 2.5)
for _mn, _ms, _mm in (("grip (wood)", grip, "wood"), ("lever", lever, "strong"), ("lever pivot tube 5 x 0.45", lever_pin, "brass"),
                      ("pusher", dm_pusher, "steel"), ("gate wire", gate_wire, "steel")):
    ms_add("controls", _mn, _ms, _mm)
ms_add("controls", "pommel", pommel, "brass pommel (cast shell ~1.5 mm)")
ms_add("controls", "dead-man", deadman, "dead-man 2/2 NC")
ms_hose("controls", "outlet hose 8 x 6", air_supply, HOSE_OUT_OD, HOSE_OUT_OD - 2.0)
ms_hose("controls", "supply hose (in the grip, stub)", supply_hose, SUP_IN_D, SUP_IN_D - 2.0)
mass_rows.append(("controls", "Bowden housing", MS_BOWDEN_G_PER_M * CABLE_LEN / 1000.0, ms_com(gate_cable),
                  "est. %.0f g/m" % MS_BOWDEN_G_PER_M))


def ms_sum(rows_):
    m_ = sum(r_[2] for r_ in rows_)
    c_ = V(0, 0, 0)
    for r_ in rows_:
        c_ = c_ + r_[3] * (r_[2] / m_)
    return m_, c_


# --- every fastener, placed (2026-11-21); the carry handle's and the keel's are added below
FASTENERS = ([FA.moved(f_, (lambda k_: (lambda s_: place(s_, k_ * 60.0, cam_dz(k_ * 60.0))))(k), "%s, st %d" % (f_.name, k + 1))
              for k in range(N) for f_ in ST_FAST]
             + [FA.moved(f_, (lambda k_: (lambda s_: place(s_, k_ * 60.0)))(k), "%s, st %d" % (f_.name, k + 1))
                for k in range(N) for f_ in PK_FAST]
             + HUB_FAST + AIR_FAST + PLATE_FAST + LINER_FAST + RAMP_FAST + FEED_FAST + CRANK_FAST + CRANK_ARM_FAST
             + CUP_FAST + CONTROL_FAST + [IDL_FAST] + FRAME_STUDS)
for f_ in FASTENERS:
    mass_rows.append(("fasteners", f_.name, f_.mass, ms_com(f_.body), "steel"))
for n_, b_ in M4_EXC:
    ms_add("fasteners", n_, b_, "steel")
# The handle and the tripod socket go under / over the CG with the EVA skin on (2026-11-22: the
# skin runs to the rear plate; its 0.25 kg at z ~ -50 moved the CG 3 mm aft of the handle's
# middle): a plain tube and end cap here, the real ones with their windows in "EVA skin".
_skin_est = [("skin", "EVA skin (est.)", MS_RHO["EVA"] * math.pi * (SKIN_R_OUT ** 2 - SKIN_R_IN ** 2) * (SKIN_Z1 - SKIN_Z0) / 1000.0,
              V(0, 0, 0.5 * (SKIN_Z0 + SKIN_Z1)), "EVA"),
             ("skin", "EVA end cap (est.)", MS_RHO["EVA"] * math.pi * (SKIN_R_OUT ** 2 - CAP_R_IN_EST ** 2) * SKIN_T / 1000.0,
              V(0, 0, SKIN_Z0 - 0.5 * SKIN_T), "EVA")]
# 2026-11-23: the side handle is off the axis and pulls the CG towards it, so the strap lugs and the
# tripod socket are placed with an estimate of it (hoop and two rails; checked against the real CG).
_carry_est = [("carry", "PVC tube (est.)", 116.0, V(89.0, -51.5, 104.0), "PVC"),
              ("carry", "feet, rails and bolts (est.)", 365.0, V(0.5, 0.5, 0.5 * (z_cam1 - 42.0 + Z_FRING1)), "PETG")]
MASS_GUN0, CG0 = ms_sum(mass_rows + _skin_est + _carry_est)   # with the handle estimated, without the strap lugs
print("mass %.0f g, CG (%.1f, %.1f, %.1f) before the handle" % (MASS_GUN0, CG0.x, CG0.y, CG0.z), flush=True)

# ============================================================ carry: wrap handle at the CG, strap lugs
# 2026-11-23 (owner: a big handle like a chainsaw's, to the side and up, so nothing stands over the
# hopper). A half-circle across the barrels in the CG's plane: from low on the left, up the side,
# over the top behind the cup and under its floor, to high on the right (the crank is lower on the
# right). Held on top the CG hangs under the hand. Between the liner and the front ring there are
# only M6 studs, which would sag 1.7 mm at 1 g under the gun, so its feet stand on two printed rails
# under the skin, liner to front ring (like the keel), at CARRY_W. The handle is a bought PVC tube
# in one bend round a former (R 172, about 7 x its diameter: a heat gun, no sand), its ends in two
# printed feet, an M3 x 50 across each. The strap keeps its two points either side of the CG on low
# lugs where the bridge's posts stood: the rear one still closes the liner's split.
CARRY_TUBE_OD, CARRY_TUBE_WALL = 25.0, 2.0        # PVC, to be measured when bought
CARRY_SOCKET_CLEAR, CARRY_SOCKET_L = 0.2, 36.0    # bore over the tube; the tube's run in a foot
CARRY_HEAD_HW, CARRY_NECK_HT, CARRY_HEAD_HT = 16.5, 12.0, 20.0  # foot: half width along z, half widths along the arc
CARRY_PIN_HL, CARRY_PIN_R = 25.0, 6.0             # the boss for the M3 x 50 across the tube
CARRY_FIST_R, CARRY_GRIP_L = 32.0, 100.0
CARRY_R = 172.0                                   # the tube's centreline round the axis
CARRY_FIST_W = (270.0, 300.0, 330.0, 0.0, 30.0)   # where a hand may hold it
CARRY_FLANGE_T, CARRY_FLANGE_L, CARRY_BOLT_Z = 8.0, 54.0, 21.0
CARRY_RAIL_W = 24.0
CARRY_RAIL_R = SKIN_R_IN - LAND_T - 0.3           # the rail's outer face, under the glue lands
CARRY_POST_W, CARRY_POST_T = 24.0, 10.0
CARRY_CLEAR = 5.0                                 # the fist off the skin
SLING_WIRE = 2.5
SLING_R = math.hypot(CARRY_POST_W / 2, CARRY_POST_T / 2) + 0.5 + SLING_WIRE
SLING_EYE_R = 4.0                                 # the ring's wire is curved through the lug's 10 mm
R_BOX_OUT = BOX_R1 + 2.5                          # gearbox outer wall
y_carry, z_carry = CG0.y, CG0.z
# Strap lugs: front on the front bearing housing, flush with its lip; rear the same distance aft.
# 2026-11-23: the thin front bearing's housing ends 16 mm sooner, under the star-drive box's front:
# the lug stays ahead of the box (its ring swings over it) on a tab of the housing, r 108..127.
z_post_f = max(z_brg1 + 3.0 - CARRY_POST_T / 2, gearbox.BoundBox.ZMax + 16.0)
d_carry = z_post_f - z_carry
# The rear lug's bolts must miss the cam groove, which runs on the LOAD dwell under the top of the liner.
z_post_r = max(z_carry - d_carry, z_tip0 - BENCH_STROKE + 7.0)
CARRY_BASE_T, CARRY_BASE_W, CARRY_BASE_L, CARRY_BOLT_Y = 11.0, 42.0, 18.0, 15.5
x_eye = HOUS_RO + CARRY_BASE_T + 8.0              # the ring lies flat just over the front base and the skin
x_lug_top = x_eye + SLING_EYE_R + 5.0


def carry_post(zc, r_seat):
    """Low strap lug from a saddle base on a cylinder of radius r_seat, an eye along the barrels."""
    p_ = Part.makeBox(x_lug_top - (r_seat - 10.0), CARRY_POST_W, CARRY_POST_T,
                      V(r_seat - 10.0, y_carry - CARRY_POST_W / 2, zc - CARRY_POST_T / 2))
    b_ = Part.makeBox(CARRY_BASE_T + 10.0, CARRY_BASE_W, CARRY_BASE_L,
                      V(r_seat - 10.0, y_carry - CARRY_BASE_W / 2, zc - CARRY_BASE_L / 2))
    e_ = Part.makeCylinder(SLING_EYE_R, CARRY_POST_T + 2.0, V(x_eye, y_carry, zc - CARRY_POST_T / 2 - 1.0), ZA)
    return p_.fuse(b_).cut(Part.makeCylinder(r_seat, 400.0, V(0, 0, zc - 200.0))).cut(e_).removeSplitter()


z_lug_tab1 = max(z_brg1 + 3.0, z_post_f + CARRY_POST_T / 2)
if z_lug_tab1 > z_brg1 + 3.0 + 1e-6:
    _tab = Part.makeBox(HOUS_RO - 108.0, 46.0, z_lug_tab1 - (z_brg1 + 2.0), V(108.0, y_carry - 23.0, z_brg1 + 2.0)).common(
        Part.makeCylinder(HOUS_RO, 200.0, V(0, 0, z_brg1)))
    brg_housing = brg_housing.fuse(_tab).removeSplitter()
lug_r, lug_f = carry_post(z_post_r, r_case_od), carry_post(z_post_f, HOUS_RO)
# 2026-11-22: the rear base gives way round the liner's split lug on top, 0.5 off.
_lug_clear = []
for w, za, zb in _split_bands:
    _b = Part.makeBox(SPLIT_LUG_H + 2.0, SPLIT_LUG_W + 1.0, zb - za + 1.0, V(r_case_od - 1.5, -SPLIT_LUG_W / 2 - 0.5, za - 0.5))
    _b.rotate(O, ZA, w)
    _lug_clear.append(_b)
lug_r = lug_r.cut(Part.makeCompound(_lug_clear)).removeSplitter()
# Bolts: the rear base 2 x M3 x 20 into the liner (one in each half: it closes the split at the top
# front); the front base 2 x M3 x 20 into the bearing housing's wall, nuts slid in from its front.
LUG_FAST_R, LUG_FAST_F = [], []
for _sy in (-1, 1):
    _yb = y_carry + _sy * CARRY_BOLT_Y
    LUG_FAST_R.append(FA.m3("strap lug on the liner", V(r_case_od + CARRY_BASE_T, _yb, z_post_r), V(-1, 0, 0), [lug_r, cam],
                            head_on_face=True, clip=(-0.01, 60.0)))
    _g = 20.0 - FA.NUT_T - 1.0
    LUG_FAST_F.append(FA.m3_at("strap lug on the bearing housing", V(HOUS_RO + CARRY_BASE_T, _yb, z_post_f), V(-1, 0, 0), 0.0, _g, 20.0,
                               nut_slot=(V(0, 0, 1), z_lug_tab1 - z_post_f + 1.0)))
lug_r, lug_f = cut_fast(lug_r, LUG_FAST_R, "rear strap lug"), cut_fast(lug_f, LUG_FAST_F, "front strap lug")
strap_lugs = Part.makeCompound([lug_r, lug_f])

# --- the two rails, liner to front ring, under the skin's glue lands
z_rail0, z_rail1 = z_cam1 - 42.0, Z_FRING1
Z_RAIL_LINER = z_cam1 - 34.0                      # aft of the lug band's glue land, clear of the groove at 240 and 285


def carry_rail(w):
    r_ = Part.makeBox(CARRY_RAIL_R - r_case_od + 10.0, CARRY_RAIL_W, z_rail1 - z_rail0,
                      V(r_case_od - 10.0, -CARRY_RAIL_W / 2, z_rail0))
    r_.rotate(O, ZA, w)
    r_ = r_.cut(Part.makeCylinder(r_case_od, 2000.0, V(0, 0, -1000.0)))
    return r_.cut(Part.makeCompound([tube(2.0 * SKIN_R_IN + 20.0, 2.0 * CARRY_RAIL_R, z0_ - 0.3, z1_ + 0.3)
                                     for z0_, z1_, _ in SKIN_LANDS_Z])).removeSplitter()


def _carry_pt(w, r, along, z):
    """A point on the rail at world angle w: radius r, offset along the tangent, height z."""
    a_ = math.radians(w)
    return V(r * math.cos(a_) - along * math.sin(a_), r * math.sin(a_) + along * math.cos(a_), z)


_rails = [carry_rail(w) for w in CARRY_W]
RAIL_FAST = []
for i_, w in enumerate(CARRY_W):
    _in = wpt(-1.0, w)
    for _sa in (-1, 1):
        RAIL_FAST.append(FA.m3("side rail on the liner", _carry_pt(w, CARRY_RAIL_R, _sa * 6.5, Z_RAIL_LINER), _in, [_rails[i_], cam],
                               clip=(-0.01, 60.0)))
        RAIL_FAST.append(FA.m3("side rail on the front ring", _carry_pt(w, CARRY_RAIL_R, _sa * 6.5, 0.5 * (Z_FRING0 + Z_FRING1)), _in,
                               [_rails[i_], pack_frame], nut_on_face=True, clip=(-0.01, 40.0)))

# --- the wrap handle: one PVC tube bent round the axis, its ends in two printed feet on the rails
_w0, _w1 = CARRY_W[0], CARRY_W[1] + 360.0
CARRY_MID_W = 0.5 * (_w0 + _w1)                   # 330: the middle of the arc
_end_deg = math.degrees((CARRY_SOCKET_L - CARRY_HEAD_HT) / CARRY_R)   # the tube's end past the foot's centre


def _ring_sweep(face_, a0, a1):
    """A section in the plane at angle 0 swept round the axis from a0 to a1 (deg)."""
    f_ = face_.copy()
    f_.rotate(O, ZA, a0)
    return f_.revolve(O, ZA, a1 - a0)


_c0 = V(CARRY_R, 0, z_carry)
_bore_f = Part.Face(Part.Wire(Part.makeCircle(CARRY_TUBE_OD / 2 + CARRY_SOCKET_CLEAR, _c0, V(0, 1, 0))))
_tube_f = Part.makeFace([Part.Wire(Part.makeCircle(CARRY_TUBE_OD / 2, _c0, V(0, 1, 0))),
                         Part.Wire(Part.makeCircle(CARRY_TUBE_OD / 2 - CARRY_TUBE_WALL, _c0, V(0, 1, 0)))], "Part::FaceMakerBullseye")
carry_tube = _ring_sweep(_tube_f, _w0 - _end_deg + 0.1, _w1 + _end_deg - 0.1)
CARRY_TUBE_L = math.radians(_w1 - _w0 + 2.0 * _end_deg - 0.2) * CARRY_R


def carry_foot(w, sgn):
    """A foot at world angle w, the tube coming in from the side sgn (+1: from larger angles)."""
    _zc = z_carry
    p_ = [Part.makeBox(CARRY_FLANGE_T, 2 * CARRY_NECK_HT, CARRY_FLANGE_L,
                       V(CARRY_RAIL_R, -CARRY_NECK_HT, _zc - CARRY_FLANGE_L / 2)),
          Part.makeBox(CARRY_R - CARRY_RAIL_R, 2 * CARRY_NECK_HT, 2 * CARRY_HEAD_HW,
                       V(CARRY_RAIL_R + 1.0, -CARRY_NECK_HT, _zc - CARRY_HEAD_HW)),
          Part.makeBox(2 * CARRY_HEAD_HW, 2 * CARRY_HEAD_HT, 2 * CARRY_HEAD_HW,
                       V(CARRY_R - CARRY_HEAD_HW, -CARRY_HEAD_HT, _zc - CARRY_HEAD_HW)),
          Part.makeCylinder(CARRY_PIN_R, 2 * CARRY_PIN_HL, V(CARRY_R, 0, _zc - CARRY_PIN_HL), ZA)]
    f_ = G.fuse_all(p_).removeSplitter()
    a0_, a1_ = (-_end_deg, 14.0) if sgn > 0 else (-14.0, _end_deg)
    f_ = f_.cut(_ring_sweep(_bore_f, a0_, a1_)).removeSplitter()
    f_.rotate(O, ZA, w)
    return f_


foot_l, foot_r = carry_foot(CARRY_W[0], 1), carry_foot(CARRY_W[1], -1)
_feet = [foot_l, foot_r]
HOOP_FAST = []
for i_, w in enumerate(CARRY_W):
    for _sz in (-1, 1):
        HOOP_FAST.append(FA.m3("wrap handle's foot on its rail", wpt(CARRY_RAIL_R + CARRY_FLANGE_T, w, z_carry + _sz * CARRY_BOLT_Z), wpt(-1.0, w),
                               [_feet[i_], _rails[i_]], head_on_face=True, clip=(-0.01, CARRY_FLANGE_T + CARRY_RAIL_R - r_case_od + 0.5)))
PIN_FAST = [FA.m3("PVC tube pinned in its foot", wpt(CARRY_R, w, z_carry + CARRY_PIN_HL), V(0, 0, -1), [_feet[i_], _feet[i_]],
                  head_on_face=True, clip=(-0.01, 2.0 * CARRY_PIN_HL + 0.01)) for i_, w in enumerate(CARRY_W)]
foot_l = cut_fast(foot_l, HOOP_FAST[:2] + PIN_FAST[:1], "wrap handle's left foot")
foot_r = cut_fast(foot_r, HOOP_FAST[2:] + PIN_FAST[1:], "wrap handle's right foot")
carry_tube = cut_fast(carry_tube, PIN_FAST, "PVC tube")
carry_feet = Part.makeCompound([foot_l, foot_r])
carry_handle = Part.makeCompound([foot_l, foot_r, carry_tube])
_rails = [cut_fast(r_, RAIL_FAST[4 * i_:4 * i_ + 4] + HOOP_FAST[2 * i_:2 * i_ + 2], "side rail") for i_, r_ in enumerate(_rails)]
carry_rails = Part.makeCompound(_rails)
# CARRY_KEY_FAST: the bolts put in after the skin (a key through its windows); the rails' go in before it.
CARRY_KEY_FAST = LUG_FAST_R + LUG_FAST_F + HOOP_FAST
CARRY_FAST = CARRY_KEY_FAST + RAIL_FAST + PIN_FAST
_liner_cut = LUG_FAST_R + RAIL_FAST
cam, cam_r, cam_l, cam_outside = [cut_fast(x_, [f_ for f_ in _liner_cut if f_.name != "side rail on the front ring"], n_) for x_, n_ in
                                   ((cam, "liner"), (cam_r, "liner right"), (cam_l, "liner left"), (cam_outside, "liner outside"))]
pack_frame = cut_fast(pack_frame, [f_ for f_ in RAIL_FAST if f_.name == "side rail on the front ring"], "front ring")
brg_housing = cut_fast(brg_housing, LUG_FAST_F, "bearing housing")
_sl = []
for _zs in (z_post_r, z_post_f):                  # flat over the skin, through the lug's eye
    _t = Part.makeTorus(SLING_R, SLING_WIRE)
    _t.rotate(O, V(0, 1, 0), 90.0)                # axis along X
    _t.translate(V(x_eye, y_carry + SLING_R, _zs))
    _sl.append(_t)
sling = Part.makeCompound(_sl)


def carry_fist(w):
    """The fist round the handle at world angle w: a cylinder on the arc's tangent there."""
    a_ = math.radians(w)
    t_ = V(-math.sin(a_), math.cos(a_), 0)
    return Part.makeCylinder(CARRY_FIST_R, CARRY_GRIP_L, wpt(CARRY_R, w, z_carry) - t_ * (CARRY_GRIP_L / 2), t_)


carry_hand = carry_fist(CARRY_MID_W)

# ============================================================ tripod pad under the CG
# The tripod is not chosen yet: a socket for a Ø50 ball under the CG. Below the pack
# nothing fixed runs between the liner and the front ring (only the spars at 150 and
# 210 deg), so a keel bridges them along the bottom (-X), outside the liner's radius,
# and a boss on it under the CG carries a shallow spherical socket (the ball sits in
# it, below its equator; the tripod's clamp holds it). A reference ball with a post
# shows the tripod and is tilted 20 deg each way.
TRIPOD_BALL_D, TRIPOD_SOCKET_CLEAR, TRIPOD_SOCKET_DEPTH = 50.0, 0.25, 15.0
TRIPOD_KEEL_W, TRIPOD_KEEL_T = 30.0, 15.0           # across (y), down (x)
TRIPOD_BOSS_D, TRIPOD_BOSS_H = 70.0, 25.0
TRIPOD_FOOT_L = 20.0                                # keel foot on the liner (its front end)
TRIPOD_POST_D, TRIPOD_POST_L, TRIPOD_TILT = 25.0, 120.0, 20.0
y_tripod, z_tripod = CG0.y, CG0.z
z_keel0 = z_cam1 - TRIPOD_FOOT_L                    # on the liner, ahead of the ramp block's inserts
z_keel1 = Z_FRING1                                  # over the front ring's width
x_keel_out = -(r_case_od + TRIPOD_KEEL_T)
_keel = Part.makeBox(TRIPOD_KEEL_T + 10.0, TRIPOD_KEEL_W, z_keel1 - z_keel0,
                     V(x_keel_out, y_tripod - TRIPOD_KEEL_W / 2, z_keel0))
_keel = _keel.cut(Part.makeCylinder(r_case_od, 2000.0, V(0, 0, -1000.0)))
# 2026-11-22: the glue lands of the liner's front lugs and of the front ring pass over the keel's
# corners (r 124.9..125.6 against the hoop's bore 125): the corners give way, 0.3 off.
_keel = _keel.cut(Part.makeCompound([tube(2.0 * SKIN_R_IN + 20.0, 2.0 * (SKIN_R_IN - LAND_T - 0.3), z0_ - 0.3, z1_ + 0.3)
                                     for z0_, z1_, _ in SKIN_LANDS_Z]))
x_socket_face = x_keel_out - TRIPOD_BOSS_H
_boss = Part.makeCylinder(TRIPOD_BOSS_D / 2, TRIPOD_BOSS_H + 1.0, V(x_socket_face, y_tripod, z_tripod), V(1, 0, 0))
TRIPOD_SOCKET_R = TRIPOD_BALL_D / 2 + TRIPOD_SOCKET_CLEAR
P_BALL = V(x_socket_face - (TRIPOD_SOCKET_R - TRIPOD_SOCKET_DEPTH), y_tripod, z_tripod)
tripod_pad = G.fuse_all([_keel, _boss]).cut(Part.makeSphere(TRIPOD_SOCKET_R, P_BALL)).removeSplitter()
# Bolts (2026-11-21): 2 x M3 x 20 at its foot into the liner (one in each half: the keel
# closes the split at the bottom front; 4 mm aft of the groove's FIRE band) and 2 at its
# front end into the front ring (nuts on the ring's inner face); heads sunk from below.
TRIPOD_FAST = []
_z_kr = z_keel0 + 5.0
for _sy in (-1, 1):
    _yb = y_tripod + _sy * 9.0
    TRIPOD_FAST.append(FA.m3("keel foot on the liner", V(x_keel_out, _yb, _z_kr), V(1, 0, 0), [tripod_pad, cam],
                             clip=(-0.01, 60.0)))
    TRIPOD_FAST.append(FA.m3("keel on the front ring", V(x_keel_out, _yb, 0.5 * (Z_FRING0 + Z_FRING1)), V(1, 0, 0),
                             [tripod_pad, pack_frame], nut_on_face=True, clip=(-0.01, 40.0)))
tripod_pad = cut_fast(tripod_pad, TRIPOD_FAST, "keel")
cam, cam_r, cam_l, cam_outside = [cut_fast(x_, TRIPOD_FAST, n_) for x_, n_ in
                                   ((cam, "liner"), (cam_r, "liner right"), (cam_l, "liner left"), (cam_outside, "liner outside"))]
pack_frame = cut_fast(pack_frame, TRIPOD_FAST, "front ring")
frame_all = Part.makeCompound([pack_frame, frame_studs])
TRIPOD_MOUTH_D = 2.0 * math.sqrt(TRIPOD_SOCKET_R ** 2 - (TRIPOD_SOCKET_R - TRIPOD_SOCKET_DEPTH) ** 2)
_tb = Part.makeSphere(TRIPOD_BALL_D / 2, P_BALL).fuse(
    Part.makeCylinder(TRIPOD_POST_D / 2, TRIPOD_POST_L, P_BALL, V(-1, 0, 0))).removeSplitter()
tripod_ball = _tb


def tripod_at(tilt_deg, axis_):
    return _rot_axis(tripod_ball, tilt_deg, P_BALL, axis_)


MS_RHO.setdefault("PVC", 1.40)
ms_add("carry", "PVC tube", carry_tube, "PVC")
ms_add("carry", "wrap handle's foot", foot_l, "strong")
ms_add("carry", "wrap handle's foot", foot_r, "strong")
for _s in carry_rails.Solids:
    ms_add("carry", "side rail", _s, "strong")
for _s in strap_lugs.Solids:
    ms_add("carry", "strap lug", _s, "strong")
for _s in sling.Solids:
    ms_add("carry", "strap ring", _s, "steel")
ms_add("tripod", "keel and socket", tripod_pad, "strong")
for f_ in CARRY_FAST + TRIPOD_FAST:
    mass_rows.append(("fasteners", f_.name, f_.mass, ms_com(f_.body), "steel"))
FASTENERS += CARRY_FAST + TRIPOD_FAST

# ============================================================ EVA skin over the pack (2026-11-22)
# Owner: an EVA skin that closes the whole pack, contact glue, no fixing points (2026-11-21).
# A tube of EVA SKIN_T thick from the liner's rear face to the front bearing housing's front
# face, its bore on the lug tips (r 127). It is glued on the lands (a hoop on ribs in the
# liner's two lug bands and on the front ring, built with them above) and on the bearing
# housing, whose OD went 250 -> 254 for it. Whatever crosses the tube gets a window: its
# footprint in the tube (angle x z) and SKIN_CLEAR round it. EVA narrower than SKIN_WEB between
# two windows, or between a window and an edge or the seam, goes with them. The pattern is the
# tube unrolled at its mid radius, the seam at the bottom (under the keel); a closed window round
# a part that cannot thread through it gets a slit to the nearest edge (glued shut after).
_tick("EVA skin…")
SKIN_SEAM = 180.0                                 # world angle of the seam: the bottom
SKIN_LANDS_Z.append((z_brg0 - 3.0, SKIN_Z1, "bearing housing and its retainer"))
# The lands must not hide a bolt: where a land lies on an M3's seat, its body or its key's way
# in (FA access), the land gives way (the guard webs' and the keel's bolts in the front ring).
_land_of = ["liner", "liner", "front ring"]
_land_cut = {k_: [] for k_ in set(_land_of)}
SKIN_LAND_ACCESS = []
for f_ in FASTENERS:
    if f_.kind != "M3":
        continue
    for i_, l_ in enumerate(SKIN_LANDS):
        for k_ in ("access", "cutter", "body"):
            s_ = getattr(f_, k_)
            if not _near(s_.BoundBox, l_.BoundBox, 0.0):
                continue
            c_ = s_.common(l_)
            if c_.Volume > 1e-3:
                _land_cut[_land_of[i_]].append(c_)
                SKIN_LAND_ACCESS.append(f_.name.split(",")[0])
if _land_cut["liner"]:
    cam, cam_r, cam_l, cam_outside = [cut_fast(x_, _land_cut["liner"], n_ + ": glue lands round bolts")
                                      for x_, n_ in ((cam, "liner"), (cam_r, "liner right"), (cam_l, "liner left"),
                                                     (cam_outside, "liner outside"))]
if _land_cut["front ring"]:
    pack_frame = cut_fast(pack_frame, _land_cut["front ring"], "front ring: glue land round bolts")
SKIN_LAND_ACCESS = sorted(set(SKIN_LAND_ACCESS))


def _side(p):
    return V(p.x, -p.y, p.z) if CRANK_SIDE > 0 else V(p)


def swept(shape, c, axis):
    """The cylinder a part sweeps turning about an axis through c along Z or Y."""
    pts = shape.tessellate(0.2)[0] + [v_.Point for v_ in shape.Vertexes]
    bb_ = shape.BoundBox
    if axis == "Z":
        r_ = max(math.hypot(p.x - c.x, p.y - c.y) for p in pts)
        return Part.makeCylinder(r_, bb_.ZLength, V(c.x, c.y, bb_.ZMin))
    r_ = max(math.hypot(p.x - c.x, p.z - c.z) for p in pts)
    return Part.makeCylinder(r_, bb_.YLength, V(c.x, bb_.YMin, c.z), V(0, 1, 0))


# What may cross the tube: every body round the pack (turning ones by their sweep). A part
# that only rests on the bore (r SKIN_R_IN) gets no window; the strap rings lie on the skin.
SKIN_OBST = [
    ("feed head", feed_head), ("TPU lip", feed_lip), ("cup", feed_cup), ("guard", feed_guard),
    ("feed gate", Part.makeCompound([gate_housing, gate_pin, gate_pin_open, gate_spring])), ("gate cable", cable_ex),
    ("star (its sweep)", swept(star0, S_C, "Z")),
    ("star shaft, 608s, cover, spacer, collar", Part.makeCompound([star_shaft, star_bearings, star_cover, star_spacer,
                                                                    star_collar])),
    ("star-drive box", gearbox), ("gears A + B (sweep)", swept(gear_ab, L_C, "Z")), ("idler (sweep)", swept(gear_i, I_C, "Z")),
    ("star gear (sweep)", swept(gear_s, S_C, "Z")), ("A + B pin, idler tube", Part.makeCompound([lay_shaft, idl_shaft])),
    ("gear 60 (sweep)", swept(crank_gear, _side(CP_C), "Z")), ("lay shaft", pin_shaft), ("lay shaft collar", lay_collar),
    ("lay bevel (sweep)", swept(bevel_small, _side(APEX), "Z")), ("crank bevel (sweep)", swept(bevel_big, _side(APEX), "Y")),
    ("crank shaft and spacer", Part.makeCompound([crank_shaft, crank_spacer])), ("crank brackets", crank_bracket),
    ("crank 608s", crank_bearings), ("crank arm and knob", Part.makeCompound([crank_arm, crank_knob, crank_knob_pin])),
    ("carry handle", carry_handle), ("strap lugs", strap_lugs), ("keel and tripod boss", tripod_pad),
    ("carry post bolts (key)", Part.makeCompound([f_.access for f_ in CARRY_KEY_FAST])),
    ("frame M6 studs", frame_studs),
    ("fasteners", Part.makeCompound([f_.body for f_ in FASTENERS if not any(f_ is h_ for h_ in HOOP_FAST)] + [b_ for _, b_ in M4_EXC])),
    ("ramp and its block", Part.makeCompound([ramp_fire, guide_block])), ("pack (six phases)", Part.makeCompound(stations)),
    ("hub", pack_hub), ("front bearing and its inner retainer", Part.makeCompound([front_bearing, brg_ret_in])),
    ("MQR, its pad and fittings, the 61812 and its cage", Part.makeCompound([soft_coup, mqr_rotor, mqr_stator, rotor_fittings,
                                                                             rear_bearing, rear_cage, rear_ret])),
    ("collector and its hoses", Part.makeCompound([collector, coll_fittings, coll_hoses])), ("rear rail disk", rear_disk),
]
# What stands behind the rear plate round the grip's root: the end cap's bore clears it (the lever
# in every pose of its squeeze).
CAP_NEAR = [("grip", grip), ("pommel", pommel), ("lever pin", lever_pin), ("dead-man and pusher", Part.makeCompound([deadman, dm_pusher])),
            ("hoses", Part.makeCompound([air_supply, supply_hose])), ("cable and wire", Part.makeCompound([cable_in, gate_wire]))] + [
    ("lever at %.1f deg" % (LEV_ANG * i_ / 6.0), lever_at(LEV_ANG * i_ / 6.0)) for i_ in range(7)]
# The skin rests on these without a window: the tips of their stud bosses lie at r SKIN_R_IN.
SKIN_RESTS = ("crank brackets", "star-drive box")
# No slit round these: the cable threads through its window; the carry handle comes off and goes on
# after the skin, the key to its rear base's bolts through the post's window.
SKIN_THREADS = {"gate cable": "threads through", "carry handle": "goes on after the skin",
                "strap lugs": "go on after the skin",
                "carry post bolts (key)": "goes on after the skin"}
_skin_ann = tube(2.0 * (SKIN_R_OUT + SKIN_CLEAR), 2.0 * SKIN_R_IN + 0.02, SKIN_Z0, SKIN_Z1)


def _ang_rel(p):
    return (math.degrees(math.atan2(p.y, p.x)) - SKIN_SEAM) % 360.0


SKIN_RECTS = []                                       # [s0, s1, z0, z1, {name: area}] on the pattern, s from the seam
for n_, sh_ in SKIN_OBST:
    for sol_ in (sh_.Solids or [sh_]):
        bb_ = sol_.BoundBox
        if bb_.ZMax < SKIN_Z0 or bb_.ZMin > SKIN_Z1:
            continue
        if math.hypot(max(abs(bb_.XMin), abs(bb_.XMax)), max(abs(bb_.YMin), abs(bb_.YMax))) < SKIN_R_IN:
            continue
        for c_ in sol_.common(_skin_ann).Solids:
            if c_.Volume < 1e-3:
                continue
            pts_ = c_.tessellate(0.2)[0] + [v_.Point for v_ in c_.Vertexes]
            ref_ = _ang_rel(c_.CenterOfMass)
            rel_ = [((_ang_rel(p) - ref_ + 180.0) % 360.0) - 180.0 for p in pts_]
            s0_ = math.radians(ref_ + min(rel_)) * SKIN_R_MID - SKIN_CLEAR
            s1_ = math.radians(ref_ + max(rel_)) * SKIN_R_MID + SKIN_CLEAR
            z0_ = min(p.z for p in pts_) - SKIN_CLEAR
            z1_ = max(p.z for p in pts_) + SKIN_CLEAR
            for k_ in (-1, 0, 1):                     # across the seam: a piece on either end
                lo_, hi_ = s0_ + k_ * SKIN_L, s1_ + k_ * SKIN_L
                if hi_ > 0.0 and lo_ < SKIN_L:
                    SKIN_RECTS.append([max(lo_, 0.0), min(hi_, SKIN_L), z0_, z1_, {n_: (s1_ - s0_) * (z1_ - z0_)}])


def _skin_tidy(rs):
    """Open onto an edge or the seam the windows within SKIN_WEB of it; bridge two windows facing
    each other across EVA narrower than SKIN_WEB; drop the windows inside others."""
    rs = [list(r_) for r_ in rs]
    for r_ in rs:
        if r_[2] - SKIN_Z0 < SKIN_WEB:
            r_[2] = SKIN_Z0 - 1.0
        if SKIN_Z1 - r_[3] < SKIN_WEB:
            r_[3] = SKIN_Z1 + 1.0
        if r_[0] < SKIN_WEB:
            r_[0] = 0.0
        if SKIN_L - r_[1] < SKIN_WEB:
            r_[1] = SKIN_L

    def inside(q_, o_):
        return o_[0] <= q_[0] + 1e-6 and q_[1] <= o_[1] + 1e-6 and o_[2] <= q_[2] + 1e-6 and q_[3] <= o_[3] + 1e-6

    def prune(rs_):
        out_ = []
        for r_ in sorted(rs_, key=lambda q_: -(q_[1] - q_[0]) * (q_[3] - q_[2])):
            big_ = next((o_ for o_ in out_ if inside(r_, o_)), None)
            if big_ is None:
                out_.append(r_)
                continue
            for k_, v_ in r_[4].items():
                big_[4][k_] = max(big_[4].get(k_, 0.0), v_)
        return out_

    rs = prune(rs)
    for _ in range(50):
        new_ = []
        for i_, a_ in enumerate(rs):
            for b_ in rs[i_ + 1:]:
                for p_, q_ in ((a_, b_), (b_, a_)):
                    zo_ = (max(p_[2], q_[2]), min(p_[3], q_[3]))
                    so_ = (max(p_[0], q_[0]), min(p_[1], q_[1]))
                    br_ = None
                    if zo_[1] > zo_[0] and 0.0 < q_[0] - p_[1] < SKIN_WEB:
                        br_ = [p_[1], q_[0], zo_[0], zo_[1], {}]
                    elif so_[1] > so_[0] and 0.0 < q_[2] - p_[3] < SKIN_WEB:
                        br_ = [so_[0], so_[1], p_[3], q_[2], {}]
                    if br_ is not None and not any(inside(br_, o_) for o_ in rs + new_):
                        new_.append(br_)
        if not new_:
            return rs
        rs = prune(rs + new_)
    raise RuntimeError("EVA skin: window bridging did not settle")


SKIN_RECTS = _skin_tidy(SKIN_RECTS)


def _skin_clusters():
    """Windows that overlap or touch: one hole in the sheet each. (rects, open to an edge or the seam)"""
    grp_ = list(range(len(SKIN_RECTS)))

    def root(i_):
        while grp_[i_] != i_:
            i_ = grp_[i_]
        return i_
    for i_, a_ in enumerate(SKIN_RECTS):
        for j_, b_ in enumerate(SKIN_RECTS[:i_]):
            if min(a_[1], b_[1]) >= max(a_[0], b_[0]) and min(a_[3], b_[3]) >= max(a_[2], b_[2]):
                grp_[root(i_)] = root(j_)
    cl_ = {}
    for i_, r_ in enumerate(SKIN_RECTS):
        cl_.setdefault(root(i_), []).append(r_)
    return [(rs_, any(r_[2] < SKIN_Z0 or r_[3] > SKIN_Z1 or r_[0] <= 0.0 or r_[1] >= SKIN_L for r_ in rs_))
            for rs_ in cl_.values()]


def _skin_name(rs_):
    a_ = {}
    for r_ in rs_:
        for k_, v_ in r_[4].items():
            a_[k_] = a_.get(k_, 0.0) + v_
    return max(a_, key=a_.get) if a_ else "?"


SKIN_HOLES = []                                       # (name, open, slit (s0, z0, s1, z1) or None, rects)
for rs_, open_ in _skin_clusters():
    names_ = set(k_ for r_ in rs_ for k_ in r_[4])
    slit_ = None
    if not open_ and not names_ <= set(SKIN_THREADS):
        cands_ = []
        for r_ in rs_:
            sm_, zm_ = 0.5 * (r_[0] + r_[1]), 0.5 * (r_[2] + r_[3])
            cands_ += [(r_[2] - SKIN_Z0, (sm_, r_[2], sm_, SKIN_Z0)), (SKIN_Z1 - r_[3], (sm_, r_[3], sm_, SKIN_Z1)),
                       (r_[0], (r_[0], zm_, 0.0, zm_)), (SKIN_L - r_[1], (r_[1], zm_, SKIN_L, zm_))]
        slit_ = min(cands_)[1]
    SKIN_HOLES.append((_skin_name(rs_), open_, slit_, rs_))
SKIN_HOLES.sort(key=lambda h_: min(r_[0] for r_ in h_[3]))


def _skin_cutter(r_):
    a0_ = SKIN_SEAM + math.degrees(r_[0] / SKIN_R_MID)
    da_ = math.degrees((r_[1] - r_[0]) / SKIN_R_MID)
    c_ = Part.makeCylinder(SKIN_R_OUT + 5.0, r_[3] - r_[2], V(0, 0, r_[2]), ZA, da_)
    c_.rotate(O, ZA, a0_)
    return c_


skin_tube = tube(2.0 * SKIN_R_OUT, 2.0 * SKIN_R_IN, SKIN_Z0, SKIN_Z1)
skin = cut_fast(skin_tube, [_skin_cutter(r_) for r_ in SKIN_RECTS], "EVA skin")
SKIN_AREA = skin.Volume / SKIN_T                      # one face, mm2
ms_add("skin", "EVA skin %.0f mm" % SKIN_T, skin, "EVA")
# End cap: an EVA ring on the rear plate's aft face, from round the grip's root out over the
# tube's end; its bore clears whatever stands behind the plate near the axis by SKIN_CLEAR, a
# hole round each nut of the bay-1 studs (they stand proud of the plate's aft face).
_cap_slab = Part.makeCylinder(SKIN_R_OUT + 5.0, SKIN_T + SKIN_CLEAR, V(0, 0, SKIN_Z0 - SKIN_T - SKIN_CLEAR))
CAP_R_IN = RP_R
for n_, sh_ in CAP_NEAR + [("M3 bolts", Part.makeCompound([f_.body for f_ in FASTENERS if f_.kind == "M3"]))]:
    for sol_ in (sh_.Solids or [sh_]):
        if not _near(sol_.BoundBox, _cap_slab.BoundBox, 0.0):
            continue
        c_ = sol_.common(_cap_slab)
        if c_.Volume > 1e-3:
            CAP_R_IN = max(CAP_R_IN, r_max(c_, 0.2))
CAP_R_IN += SKIN_CLEAR
skin_cap = tube(2.0 * SKIN_R_OUT, 2.0 * CAP_R_IN, SKIN_Z0 - SKIN_T, SKIN_Z0)
CAP_HOLES = []
for f_ in FRAME_STUDS:
    for sol_ in f_.body.Solids:
        if _near(sol_.BoundBox, skin_cap.BoundBox, 0.0) and sol_.common(skin_cap).Volume > 1e-3:
            bb_ = sol_.BoundBox
            CAP_HOLES.append((V(bb_.Center.x, bb_.Center.y, 0), 0.5 * max(bb_.XLength, bb_.YLength) + SKIN_CLEAR))
CAP_HOLES = [h_ for i_, h_ in enumerate(CAP_HOLES)
             if all((h_[0] - g_[0]).Length > 1.0 or g_[1] < h_[1] for g_ in CAP_HOLES[:i_] + CAP_HOLES[i_ + 1:])]
if CAP_HOLES:
    skin_cap = skin_cap.cut(Part.makeCompound([Part.makeCylinder(r_, SKIN_T + 2.0, V(c_.x, c_.y, SKIN_Z0 - SKIN_T - 1.0))
                                               for c_, r_ in CAP_HOLES])).removeSplitter()
ms_add("skin", "EVA end cap %.0f mm" % SKIN_T, skin_cap, "EVA")
# Bolts the skin covers (their key's way in crosses it): the skin goes on last.
SKIN_COVERS = sorted(set(f_.name.split(",")[0] for f_ in FASTENERS if f_.kind == "M3"
                         and _near(f_.access.BoundBox, skin.BoundBox, 0.0) and f_.access.common(skin).Volume > 1e-3))
print("EVA skin: %d windows in %d holes, %.2f m2, %.0f g" % (len(SKIN_RECTS), len(SKIN_HOLES), SKIN_AREA / 1e6,
                                                             MS_RHO["EVA"] * skin.Volume / 1000.0), flush=True)


def skin_pattern_svg(path):
    """The pattern 1:1 in mm, seen from outside: the sheet minus the windows, the glue lands, the slits."""
    sheet_ = Part.Face(Part.makePolygon([V(0, SKIN_Z0, 0), V(SKIN_L, SKIN_Z0, 0), V(SKIN_L, SKIN_Z1, 0),
                                         V(0, SKIN_Z1, 0), V(0, SKIN_Z0, 0)]))
    holes_ = [Part.Face(Part.makePolygon([V(r_[0], r_[2], 0), V(r_[1], r_[2], 0), V(r_[1], r_[3], 0),
                                          V(r_[0], r_[3], 0), V(r_[0], r_[2], 0)])) for r_ in SKIN_RECTS]
    flat_ = sheet_.cut(Part.makeCompound(holes_)).removeSplitter()
    W_, H_, M_ = SKIN_L, SKIN_Z1 - SKIN_Z0, 12.0
    WT_, HT_ = W_ + 2 * M_ + 2.0 * SKIN_R_OUT + 16.0, max(H_, 2.0 * SKIN_R_OUT + 16.0) + 2 * M_ + 20

    def xy(s_, z_):
        return "%.2f,%.2f" % (s_, SKIN_Z1 - z_)

    paths_ = []
    for f_ in flat_.Faces:
        for w_ in f_.Wires:
            paths_.append("M " + " L ".join(xy(v_.Point.x, v_.Point.y) for v_ in w_.OrderedVertexes) + " Z")
    out_ = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" height="%.1fmm" viewBox="%.1f %.1f %.1f %.1f">'
            % (WT_, HT_, -M_, -M_ - 20, WT_, HT_),
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="white"/>' % (-M_, -M_ - 20, WT_, HT_)]
    for z0_, z1_, n_ in SKIN_LANDS_Z:
        out_.append('<rect x="0" y="%.2f" width="%.2f" height="%.2f" fill="#f2d58a"/>' % (SKIN_Z1 - z1_, W_, z1_ - z0_))
        out_.append('<text x="4" y="%.2f" font-size="5" font-family="sans-serif">glue land: %s</text>'
                    % (SKIN_Z1 - 0.5 * (z0_ + z1_) + 1.8, n_))
    out_.append('<path d="%s" fill="none" stroke="black" stroke-width="0.35" fill-rule="evenodd"/>' % " ".join(paths_))
    for n_, open_, slit_, rs_ in SKIN_HOLES:
        r_ = max(rs_, key=lambda q_: (q_[1] - q_[0]) * (q_[3] - q_[2]))
        out_.append('<text x="%.2f" y="%.2f" font-size="4.5" font-family="sans-serif" fill="#555">%s</text>'
                    % (r_[0] + 1.5, SKIN_Z1 - min(r_[3], SKIN_Z1) + 6.0, n_))
        if slit_ is not None:
            out_.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#c00" stroke-width="0.5" stroke-dasharray="3,2"/>'
                        % (slit_[0], SKIN_Z1 - slit_[1], slit_[2], SKIN_Z1 - slit_[3]))
    for a_, t_ in ((90.0, "right (crank)"), (0.0, "top"), (270.0, "left")):
        x_ = math.radians((a_ - SKIN_SEAM) % 360.0) * SKIN_R_MID
        out_.append('<line x1="%.2f" y1="-3" x2="%.2f" y2="0" stroke="black" stroke-width="0.3"/>' % (x_, x_))
        out_.append('<text x="%.2f" y="-4" font-size="5" font-family="sans-serif" text-anchor="middle">%s</text>' % (x_, t_))
    out_.append('<text x="0" y="-14" font-size="6" font-family="sans-serif">EVA %.0f mm, %.0f x %.0f mm, 1:1, seen from'
                ' outside (unrolled at R %.1f). Left and right edges: the seam, under the keel; top edge: the muzzle side.'
                ' Yellow: glue lands under it. Red dashes: slits to put it on round a part, glued shut after.'
                ' Window corners: punch r 2-3.</text>' % (SKIN_T, W_, H_, SKIN_R_MID))
    cx_, cy_ = W_ + M_ + SKIN_R_OUT + 8.0, SKIN_R_OUT
    out_.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="black" stroke-width="0.35"/>' % (cx_, cy_, SKIN_R_OUT))
    out_.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="black" stroke-width="0.35"/>' % (cx_, cy_, CAP_R_IN))
    for c_, r_ in CAP_HOLES:
        # seen from behind (outside, the shooter's view): the gun's +y (crank side) on the right, the top up
        out_.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="black" stroke-width="0.35"/>'
                    % (cx_ + c_.y, cy_ - c_.x, r_))
    out_.append('<text x="%.2f" y="%.2f" font-size="6" font-family="sans-serif" text-anchor="middle">end cap, EVA %.0f mm,'
                ' seen from behind (top up, crank side right)</text>' % (cx_, cy_ + SKIN_R_OUT + 10.0, SKIN_T))
    out_.append('</svg>')
    with open(path, "w") as f_:
        f_.write("\n".join(out_) + "\n")

MASS_GUN, CG = ms_sum(mass_rows)
mass_groups = []
for _g in ("stations", "frame", "feed", "star drive", "pack drive", "air", "controls", "carry", "tripod", "skin",
           "fasteners"):
    _gm, _gc = ms_sum([r_ for r_ in mass_rows if r_[0] == _g])
    mass_groups.append((_g, _gm, _gc))
mass_by = {}
for r_ in mass_rows:
    _k = "bought (est.)" if r_[4].startswith("est.") else ("printed" if r_[4].startswith("PETG") else r_[4])
    mass_by[_k] = mass_by.get(_k, 0.0) + r_[2]
print("mass %.0f g, CG (%.1f, %.1f, %.1f) with the handle" % (MASS_GUN, CG.x, CG.y, CG.z), flush=True)

# --- control checks
_tick("controls…")
_lev_hit, _lev_worst = 0.0, "-"
for _i in range(7):
    _a = LEV_ANG * _i / 6.0
    _l = lever_at(_a)
    for _fn, _fx in (("grip", grip), ("pommel", pommel), ("pin", lever_pin), ("plate", mqr_plate),
                     ("cable", cable_in), ("hoses", Part.makeCompound([air_supply, supply_hose])),
                     ("valve", deadman)):
        if not _near(_l.BoundBox, _fx.BoundBox, 0.1):
            continue
        _v = _l.common(_fx).Volume
        if _v > _lev_hit:
            _lev_hit, _lev_worst = _v, "%s at %.1f deg" % (_fn, _a)
lever_closed = gap(turn_y(lever_blade, P_LEV, SQ * LEV_ANG), grip_full)   # the blade; the tail lives in its slot
push_released = gap(lever_at(0.0), dm_pusher)
grip_on_plate = gap(grip, mqr_plate)
grip_one = len(grip.Solids) == 2 and all(s_.isValid() for s_ in grip.Solids)      # two halves
_skin = Part.makeCompound([f_ for f_ in grip_full.Faces if f_.Surface.__class__.__name__ != "Plane"])
_walls = [(n_, tube_path(pts_, r_).distToShape(_skin)[0])
          for n_, pts_, r_ in (("cable", _cab_in[1:], CABLE_OD / 2 + 0.3), ("outlet", _out_grip[1:], HOSE_OUT_OD / 2 + 0.3),
                               ("valve", [_body0, _dm_end], DM_D / 2 + 0.3))]
chan_wall = min(w_ for _, w_ in _walls)
_wall_worst = min(_walls, key=lambda x_: x_[1])[0]
stop_in_pommel = Part.makeSphere(CABLE_OD / 2, P_STOP).common(Part.makeCompound([pommel_full, grip_full])).Volume \
    > 0.99 * (4.0 / 3.0 * math.pi * (CABLE_OD / 2) ** 3)
# Gate: a ball in the neck at the pin, on the axis and pushed to either wall.
_gate_block, _gate_free = 99.0, 99.0
for _off in (-(NECK_R - PELLET_D / 2), 0.0, NECK_R - PELLET_D / 2):
    _b = Part.makeSphere(PELLET_D / 2, V(x_gate, 0, Z_NECK + _off))
    _gate_block = min(_gate_block, _b.common(gate_pin).Volume)
    _gate_free = min(_gate_free, gap(_b, gate_pin_open))
gate_head = max(gate_housing.common(feed_head).Volume, gate_pin.common(feed_head).Volume,
                gate_pin_open.common(feed_head).Volume)
gate_star = min(gap(Part.makeCompound([gate_housing, gate_pin, gate_pin_open]), star_at(d_))
                for d_ in [-30.0 + 5.0 * i for i in range(13)])
gate_lip = gap(gate_parts, feed_lip)
# Struts against what turns behind the pack (the lines, coupling and rotor are 6-fold).
strut_turn = 99.0
for _a in range(0, 60, 5):
    for _r in (rear_disk, rotor_fittings, mqr_rotor):
        strut_turn = min(strut_turn, gap(rot(_r, float(_a)), rear_struts, pad=5.0))
strut_on = gap(rear_struts, mqr_plate)
_cable_fixed = [("liner", cam_outside), ("frame", frame_all), ("rear bearing cage", rear_cage),
                ("strap", sling), ("struts", rear_struts), ("stator", mqr_stator), ("star train box", gearbox),
                ("feed cup", feed_cup), ("star", star0)]
cable_gap, cable_near = min((gap(cable_ex, s_, pad=5.0), n_) for n_, s_ in _cable_fixed)
_hand_l_gun = [("plate", mqr_plate), ("EVA end cap", skin_cap), ("struts", rear_struts), ("stator", mqr_stator), ("cable", cable_ex),
               ("rear bearing cage", rear_cage), ("receiver hose", supply_hose.Solids[-1]),
               ("collector and its hoses", Part.makeCompound([collector, coll_fittings, coll_hoses]))]
# The collector and its hoses against what stands and turns round the stator, and the lever's swing.
_coll = Part.makeCompound([collector, coll_fittings, coll_hoses])
coll_gap, coll_near = min((gap(_coll, s_, pad=5.0), n_) for n_, s_ in (
    ("struts", rear_struts), ("cable", gate_cable), ("rotor", mqr_rotor), ("rear disk's sleeve", rear_disk),
    ("the 61812's cage", rear_cage), ("its retainer", rear_ret),
    ("grip", grip), ("lever, squeezed", lever_at(LEV_ANG)), ("lever", lever)))
coll_stator = gap(Part.makeCompound([collector, coll_hoses]), mqr_stator)
coll_seated = gap(collector, mqr_plate) < 0.05 and max(gap(f_, mqr_stator) for f_ in coll_fittings.Solids[N:]) < 0.05
hand_l_gap, hand_l_near = min((gap(hand_left, s_, pad=5.0), n_) for n_, s_ in _hand_l_gun)

# ============================================================ fast checks (the full turn: breech_mechanism_sweep.py)
# Fingers vs frame: only the finger tip reaches past the spars' inner radius,
# and it stays behind the liner's front face, where the spars start.
_fp = follower.tessellate(0.3)[0]
_fol_r = [(math.hypot(q.x, R_PACK + q.y), q.z) for q in _fp]
fingers_vs_spars = STUD_ENVELOPE - max(r for r, z in _fol_r)     # radial: the studs stand outside the liner
# Rear disk vs the parts that slide past it, every 5 deg of phase. The disk turns
# with the pack, so a station keeps its angle to it (station 0 at 0) and only
# its stroke changes with the phase.
_tick("fast checks: rear disk…")
rear_disk_gap, rear_disk_near = 99.0, "-"
for _i in range(72):
    p = _i * 5.0
    for _rn, _rs in [(n_, place(s_, 0.0, cam_dz(p))) for n_, s_ in list(qev_closed.items()) + [("valve group", valve_group)]] \
            + [("line R", place(line_r(cam_dz(p)), 0.0))]:
        _g = gap(_rs, rear_disk)
        if _g < rear_disk_gap:
            rear_disk_gap, rear_disk_near = _g, "%s at %.0f deg" % (_rn, p)
rot_all = Part.makeCompound([s for k in range(N) for s in station(k * 60.0)])
r_rot_max = r_max(Part.makeCompound([place(Part.makeCompound(qev_slide + [valve_group]), k * 60.0, cam_dz(k * 60.0))
                                     for k in range(N)] + [place(fixed0, k * 60.0) for k in range(N)]
                                    + [place(line_r(cam_dz(k * 60.0)), k * 60.0) for k in range(N)]))
liner_clear = cam_id / 2.0 - r_rot_max
spar_clear = STUD_ENVELOPE - r_rot_max
# What turns behind the pack against what stands there (2026-11-23): the sleeve and rotor's fittings
# against the stator, its port fittings and hoses, the cage; the six lines over the stroke.
_tail_fixed = [("stator", mqr_stator), ("stator's fittings and hoses", Part.makeCompound([coll_fittings, coll_hoses])),
               ("61812's cage", rear_cage), ("its retainer", rear_ret), ("rear plate", mqr_plate), ("studs", rear_struts)]
_tail_turn = Part.makeCompound([s_ for s_ in rear_disk.Solids] + rotor_fittings.Solids)
tail_gap, tail_near = 99.0, "-"
for _a in range(0, 60, 10):
    _t_ = rot(_tail_turn, float(_a))
    for n_, f_ in _tail_fixed:
        _g = gap(_t_, f_, pad=5.0)
        if _g < tail_gap:
            tail_gap, tail_near = _g, n_
lines_fixed, lines_near = 99.0, "-"
for _i in range(0, 72, 3):
    _p = _i * 5.0
    _lr = place(line_r(cam_dz(_p)), _p)
    for n_, f_ in _tail_fixed:
        _g = gap(_lr, f_, pad=5.0)
        if _g < lines_fixed:
            lines_fixed, lines_near = _g, n_
aft_gap = gap(Part.makeCompound(stations), Part.makeCompound([rear_cage, rear_ret]), pad=5.0)
front_held = max(gap(front_bearing, brg_housing), gap(front_bearing, brg_ret_out))
front_run = min(gap(front_bearing, pack_hub), gap(front_bearing, brg_ret_in))
rear_race_held = max(gap(rear_bearing, rear_cage), gap(rear_bearing, rear_ret))
rear_race_on_sleeve = gap(rear_bearing, rear_disk)
rotor_on_pad = max(gap(mqr_rotor, soft_coup), gap(soft_coup, rear_disk))
stator_on_plate = gap(mqr_stator, mqr_plate)
rim_vs_closed = min(gap(rim_gear, place(Part.makeCompound(qev_slide), k * 60.0)) for k in range(N))
star_top = star_vs_stations = min(gap(star0, s) for s in stations)
# Pack drive: every drive part vs the stations (six phases; full turn in the sweep),
# vs the fixed parts round it, its gears vs its own bracket, the hand vs everything.
_drv = [s for _, s in drive_parts]
DRIVE_PAD = 5.0                   # bbox prefilter: a real distance only when it is below this
_tick("fast checks: drive…")
drive_vs_stations = min(gap(d, st, pad=DRIVE_PAD) for d in _drv for st in stations)
drive_vs_rim = min(gap(rim_gear, d) for n, d in drive_parts if not n.startswith("crank gear"))
_near_fixed = [gearbox, gear_a, gear_b, gear_i, gear_s, lay_shaft, idl_shaft, star_shaft, star0,
               feed_head, feed_cup, feed_lip, feed_guard, front_plate, carry_handle, carry_rails, strap_lugs, sling]
drive_vs_fixed = min(gap(d, f, pad=DRIVE_PAD) for d in _drv for f in _near_fixed)


def far(g, pad=DRIVE_PAD):
    return ("> %.0f" % pad) if g >= 99.0 else ("%.2f" % g)
drive_vs_frame = min(gap(d, frame_all) for n, d in drive_parts if n != "crank brackets")
bracket_on_ring = all(gap(b_, frame_all) < 0.05 for b_ in crank_bracket.Solids) and len(crank_bracket.Solids) == 2
gears_vs_bracket = min(gap(g, crank_bracket) for g in _gears_plain)     # the spigots pass the 608 lips by 0.2
bevels_apart = gap(bevel_small, crank_gear)
# The hand against the gun (not its own drive); the arm stands off the boss by design.
_hand_gun = [("star-drive box", gearbox), ("star train", Part.makeCompound([gear_a, gear_b, gear_i, gear_s])),
             ("feed head", feed_head), ("cup", feed_cup), ("guard", feed_guard), ("carry handle", carry_handle),
             ("carry rails", carry_rails), ("strap lugs", strap_lugs), ("strap loops", sling), ("frame", frame_all), ("liner", cam_outside), ("front plate", front_plate),
             ("ramp", ramp_fire),
             ("rear bearing cage", rear_cage),
             ("dead-man and hose", Part.makeCompound([deadman, air_supply, supply_hose])),
             ("pack (six phases)", Part.makeCompound(stations)), ("rim", rim_gear)]
hand_gap, hand_near = min((gap(hand_space, s_, pad=150.0), n_) for n_, s_ in _hand_gun)
hand_own = min(gap(hand_space, s_, pad=20.0) for n_, s_ in drive_parts if n_ not in ("crank shaft", "crank spacer"))
# Crank arm and knob: a full crank turn in CK_STEP steps against everything fixed round
# it (the pack on its six phases; every 3 deg of pack in the sweep); the knob on its own
# pin; the hub on the shaft end.
CK_STEP = 10.0
crank_poses = [crank_at(CK_STEP * i_) for i_ in range(int(round(360.0 / CK_STEP)))]
_ck_fixed = _hand_gun + [("crank brackets", crank_bracket), ("crank bearings", crank_bearings),
                         ("lay bevel", bevel_small), ("gear 60", crank_gear), ("lay shaft", pin_shaft)]
crank_gap, crank_near = min((gap(s_, f_, pad=DRIVE_PAD), n_) for pose_ in crank_poses for s_ in pose_
                            for n_, f_ in _ck_fixed)
crank_boss = gap(crank_arm, crank_bracket, pad=20.0)
crank_seated = gap(crank_arm, crank_shaft) < 0.05
knob_pin_gap = gap(crank_knob, crank_knob_pin)
knob_arm_gap = gap(crank_knob, crank_arm)
knob_in_room = crank_knob.common(hand_space).Volume / crank_knob.Volume
# Carry: the posts stand on the liner and the gearbox; handle, rings and the fist clear the rest.
_tick("fast checks: carry, tripod…")
carry_seat_r = gap(lug_r, cam_outside)
carry_in_liner = strap_lugs.common(cam).Volume + carry_rails.common(cam).Volume
carry_seat_f = gap(lug_f, brg_housing)
carry_rear_on_liner = z_cam0 <= z_post_r - CARRY_POST_T / 2 and z_post_r + CARRY_POST_T / 2 <= z_cam1
rail_on_liner = max(gap(r_, cam_outside) for r_ in carry_rails.Solids)
rail_on_ring = max(gap(r_, pack_frame) for r_ in carry_rails.Solids)
hoop_on_rails = max(gap(carry_feet, r_) for r_ in carry_rails.Solids)
hoop_one = (len(foot_l.Solids) == 1 and len(foot_r.Solids) == 1 and len(carry_tube.Solids) == 1 and foot_l.isValid()
            and foot_r.isValid() and carry_tube.isValid() and all(r_.isValid() for r_ in carry_rails.Solids))
tube_in_feet = carry_tube.common(carry_feet).Volume
tube_socket_gap = gap(carry_tube, carry_feet)
rail_groove = gap(Part.makeCompound([f_.cutter for f_ in RAIL_FAST if "liner" in f_.name]), groove_solid, pad=8.0)
_carry_near = [("cup", feed_cup), ("feed head", feed_head), ("gate", Part.makeCompound([gate_housing, gate_pin, gate_pin_open])),
               ("gate cable", gate_cable), ("star", star0), ("guard", feed_guard), ("frame", frame_all),
               ("star train", Part.makeCompound([gear_a, gear_b, gear_i, gear_s, star_shaft, lay_shaft, idl_shaft])),
               ("rim", rim_gear), ("pack (six phases)", Part.makeCompound(stations)),
               ("pack drive", Part.makeCompound([s_ for _, s_ in drive_parts]))]
carry_gap, carry_near = min((gap(carry_handle, f_, pad=DRIVE_PAD), n_) for n_, f_ in _carry_near)
_rail_near = [(n_, f_) for n_, f_ in _carry_near if n_ != "frame"] + [("frame studs", frame_studs)]
rail_gap, rail_near = min((gap(carry_rails, f_, pad=DRIVE_PAD), n_) for n_, f_ in _rail_near)
ring_gap, ring_near = min((gap(sling, f_, pad=DRIVE_PAD), n_) for n_, f_ in
                          _carry_near + [("liner", cam_outside), ("gearbox", gearbox), ("strap lugs", strap_lugs),
                                         ("EVA skin", skin)])
fist_gap, fist_near = min((gap(carry_fist(w_), f_, pad=DRIVE_PAD), "%s, hand at %.0f deg" % (n_, w_)) for w_ in CARRY_FIST_W for n_, f_ in
                          _carry_near + [("liner", cam_outside), ("gearbox", gearbox), ("strap rings", sling), ("strap lugs", strap_lugs),
                                         ("EVA skin", skin), ("crank room", hand_space)])
carry_top = max(carry_handle.optimalBoundingBox().XMax, strap_lugs.optimalBoundingBox().XMax)   # plain BoundBox overshoots on the bend
cup_floor = feed_cup.optimalBoundingBox().XMin
hopper_free = carry_top < cup_floor
CG_OFF_Z, CG_OFF_Y, CG_UP = CG.z - z_carry, CG.y - y_carry, CG.x - CG0.x   # against the estimate the lugs were placed by
# Tripod pad: the keel stands on the liner and the front ring, the socket is under the
# CG; keel, boss and the tilted tripod clear the rest.
tripod_seat_r = gap(tripod_pad, cam_outside)
tripod_seat_f = gap(tripod_pad, pack_frame)
tripod_on_liner = z_cam0 <= z_keel0 and z_keel1 <= Z_FRING1 + 1e-6
_tripod_near = [("pack (six phases)", Part.makeCompound(stations)), ("ramp and block", Part.makeCompound([ramp_fire, guide_block])),
                ("rim", rim_gear), ("pack drive", Part.makeCompound([s_ for _, s_ in drive_parts])),
                ("rear bearing cage", rear_cage), ("strap rings", sling), ("hoses and grip", Part.makeCompound([supply_hose, grip, pommel]))]
tripod_gap, tripod_near = min((gap(tripod_pad, f_, pad=DRIVE_PAD), n_) for n_, f_ in _tripod_near)
_tripod_gun = _tripod_near + [("liner", cam_outside), ("frame", frame_all), ("EVA skin", skin)]
tripod_tilt_gap, tripod_tilt_near = 99.0, "nothing nearer"
for _ta in (V(0, 1, 0), V(0, 0, 1)):
    for _td in (-TRIPOD_TILT, 0.0, TRIPOD_TILT):
        for n_, f_ in _tripod_gun:
            g_ = gap(tripod_at(_td, _ta), f_, pad=DRIVE_PAD)
            if g_ < tripod_tilt_gap:
                tripod_tilt_gap, tripod_tilt_near = g_, n_
tripod_ball_seat = gap(Part.makeSphere(TRIPOD_BALL_D / 2, P_BALL), tripod_pad)
TRIPOD_OFF_Z, TRIPOD_OFF_Y = CG.z - z_tripod, CG.y - y_tripod
# Ramp mount block vs the stations, six phases (full turn in the sweep).
mount_vs_stations = min(gap(guide_block, st) for st in stations)
_tick("fast checks done")

# --- fasteners (2026-11-21): stocked lengths, seats, clearances; printed parts one solid each
FAST_BOM = FA.bom(FASTENERS)
_m3 = [f_ for f_ in FASTENERS if f_.kind == "M3"]
m3_bad = [f_.name for f_ in _m3 if not FA.m3_ok(f_)]
m3_exc = sorted(set("%s: %s" % (f_.name.split(",")[0], f_.exception) for f_ in _m3 if getattr(f_, "exception", None)))
fast_vs_stations = min(gap(Part.makeCompound([f_.body for f_ in FASTENERS
                                              if f_ in FRAME_STUDS or f_ in RAMP_FAST or f_ in FEED_FAST or f_ in LINER_FAST
                                              or f_ in CARRY_FAST or f_ in TRIPOD_FAST or f_ in CRANK_FAST]), st) for st in stations)
fast_vs_hub = min(gap(rot(Part.makeCompound([_hub_core] + [f_.body for f_ in HUB_FAST]), a_), Part.makeCompound(
    [f_.body for f_ in FRAME_STUDS + FEED_FAST + CRANK_FAST + TRIPOD_FAST])) for a_ in (0.0, 20.0, 40.0))
PRINTED_ONE = [("liner (two halves)", cam_r), ("liner (two halves)", cam_l), ("front ring", pack_frame), ("hub", pack_hub),
               ("bearing housing", brg_housing), ("inner race retainer", brg_ret_in), ("outer race retainer", brg_ret_out),
               ("rear bearing cage", rear_cage), ("rear bearing retainer", rear_ret), ("front support", front_bearing),
               ("rear rail disk", rear_disk),
               ("ramp", ramp_body), ("ramp block", guide_block), ("muzzle plate", front_plate), ("gearbox", gearbox),
               ("feed head", feed_head), ("cup", feed_cup), ("guard", feed_guard), ("gate housing", gate_housing),
               ("star collar", star_collar), ("gears A+B", gear_ab), ("rear plate", mqr_plate), ("wrap handle foot", foot_l), ("wrap handle foot", foot_r),
               ("keel", tripod_pad), ("crank arm", crank_arm), ("TPU pad under the rotor", soft_coup),
               ("star with its hub", star0), ("star gear", gear_s), ("idler", gear_i), ("star bearing cover", star_cover),
               ("lay shaft collar", lay_collar), ("crank spacer", crank_spacer),
               ("gear 60", crank_gear), ("lay bevel", bevel_small), ("crank bevel", bevel_big), ("lever", lever)] + [
    ("crank bracket", s_) for s_ in crank_bracket.Solids] + [
    ("valve bracket", valve_bracket), ("breech clamp, upper", clamp_upper), ("nose clamp, upper", nose_upper),
    ("nose clamp, lower", nose_lower)]
printed_bad = sorted(set(n_ for n_, s_ in PRINTED_ONE if len(s_.Solids) != 1 or not s_.isValid()))
cut_bad = sorted(set(w_ for w_, v0_, v1_, ok_, how_ in CUT_LOG if not ok_))
cut_one = sorted(set("%s (%s)" % (w_, how_) for w_, v0_, v1_, ok_, how_ in CUT_LOG if ok_ and how_ != "refined"))
# Nuts and washers of one stud must not sit in each other (two stacks in one gap).
stud_self = max([0.0] + [a_.common(b_).Volume for f_ in FRAME_STUDS
                         for i_, a_ in enumerate(f_.hardware.Solids) for b_ in f_.hardware.Solids[i_ + 1:]
                         if _near(a_.BoundBox, b_.BoundBox, 0.01)])
_tick("fasteners checked")
# EVA skin: on the lug tips, glued on the lands, clear of whatever crosses it or lies under it.
_tick("EVA skin checks…")
skin_one = len(skin.Solids) == 1 and skin.isValid()
skin_on_lugs = abs(SKIN_R_IN - (STUD_R + STUD_LUG_D / 2.0)) < 1e-6
SKIN_CARRIERS = [("liner right", cam_r), ("liner left", cam_l), ("front ring", pack_frame), ("bearing housing", brg_housing),
                 ("rear plate", mqr_plate),
                 ("outer race retainer", brg_ret_out)]
skin_glued = max(gap(skin, s_) for n_, s_ in SKIN_CARRIERS[:-1])
cap_one = len(skin_cap.Solids) == 1 and skin_cap.isValid()
cap_glued = max(gap(skin_cap, mqr_plate), gap(skin_cap, skin))
cap_gap, cap_near = min((gap(skin_cap, s_, pad=3.0), n_) for n_, s_ in CAP_NEAR + [("frame studs", frame_studs)])
_glue_shell = tube(2.0 * SKIN_R_IN, 2.0 * SKIN_R_IN - 1.0, SKIN_Z0, SKIN_Z1)
SKIN_GLUE = Part.makeCompound([s_ for _, s_ in SKIN_CARRIERS]).common(_glue_shell).cut(
    Part.makeCompound([_skin_cutter(r_) for r_ in SKIN_RECTS])).Volume / 0.5          # mm2 of land under the skin


def skin_gap(s_, pad=3.0, far=5.0):
    """gap(skin, s_), but a part that stays more than `far` inside the skin's bore (r_max from a 0.5 mm
    tessellation, less its deflection) gets that radial bound: the thin, windowed skin makes
    distToShape slow (2026-11-22: 69 of the build's 282 s went here)."""
    rb = SKIN_R_IN - r_max(s_) - 0.5
    return rb if rb > far else gap(skin, s_, pad=pad)


skin_gaps = sorted((skin_gap(s_), n_) for n_, s_ in SKIN_OBST)
skin_near = [(g_, n_) for g_, n_ in skin_gaps if n_ not in SKIN_RESTS]
skin_rest = [(g_, n_) for g_, n_ in skin_gaps if n_ in SKIN_RESTS]
SKIN_PACK_R = max(r_max(st_) for st_ in stations)
skin_crank = min(gap(skin, Part.makeCompound(list(pose_)), pad=DRIVE_PAD) for pose_ in crank_poses)
SKIN_BED = [(n_, max(s_.BoundBox.XLength, s_.BoundBox.YLength)) for n_, s_ in SKIN_CARRIERS]

# ============================================================ assembly / checks / report
pack = Part.makeCompound(stations)
assembly = Part.makeCompound([
    pack, cam, front_plate, pack_frame, rear_disk, pack_hub, front_bearing, brg_housing, brg_ret_in, brg_ret_out,
    rear_bearing, rear_cage, rear_ret, rotor_fittings, star_collar, Part.makeCompound([f_.body for f_ in FASTENERS] + [b_ for _, b_ in M4_EXC]),
    gear_ab, gear_i, gear_s,
    star_shaft, lay_shaft, idl_shaft, gearbox, star0, feed_head, feed_lip, feed_cup, feed_guard,
    ramp_fire, guide_block, rear_struts, grip, pommel, lever, lever_pin, dm_pusher, gate_wire, gate_cable,
    gate_housing, gate_pin, gate_spring, crank_gear, pin_shaft, bevel_small, bevel_big, crank_shaft, crank_bracket, crank_bearings,
    crank_arm, crank_knob, crank_knob_pin, carry_handle, carry_rails, strap_lugs, tripod_pad, sling, soft_coup, mqr_rotor, mqr_stator,
    mqr_plate, deadman, air_supply, supply_hose, star_bearings, star_cover,
    star_spacer, lay_collar, crank_spacer, collector, coll_fittings, coll_hoses, skin, skin_cap,
])
bb = assembly.optimalBoundingBox()
gun_L, gun_W, gun_H = bb.ZLength, bb.YLength, bb.XLength
case_od = 2.0 * r_case_od
closed_L = (z_bf + BARREL_SHOW) - Z_AFT_CLIP
fb_n_ok = sum(1 for _, ok in FB_CHECKS if ok)

checks = [
    ("bench stroke %.1f mm" % BENCH_STROKE, abs(BENCH_STROKE - 65.8) < 0.05),
    ("finger on the groove closed and open", follower_on_track(0.0) and follower_on_track(180.0)),
    ("liner groove blind: %.1f mm behind its bottom, liner Ø%.0f" % (GROOVE_FLOOR, cam_od),
     cam_od / 2.0 - (CAM_R + groove_r) >= GROOVE_FLOOR - 1e-6),
    ("rotating parts inside the liner (all but fingers) %.2f >= %.2f" % (liner_clear, CLEAR), liner_clear >= CLEAR),
    ("frame M6 studs at r %.1f (nut corners r %.1f) clear of the fingers (%.2f) and the stations (%.2f)"
     % (STUD_R, STUD_ENVELOPE, fingers_vs_spars, spar_clear),
     fingers_vs_spars >= CLEAR and spar_clear >= CLEAR),
    ("moving-part neighbour gap %.2f >= %.2f (QEV + guides, six phases)" % (gap_core, CLEAR), gap_core >= CLEAR - 1e-6),
    ("hub: whole stations incl. AirTAC and lines, six phases %.2f >= %.2f" % (gap_nbr, CLEAR), gap_nbr >= CLEAR - 1e-6),
    ("AirTAC group and line R clear of own station (%.2f)" % gap_own, gap_own >= CLEAR - 1e-6),
    ("rails: carriage and nose ride the Al tubes (plain bores, %.2f mm3)" % (
        rails_pack.common(qev_closed["Carriage"]).Volume + rails_pack.common(qev_closed["Nose_clamp"]).Volume),
     rails_pack.common(qev_closed["Carriage"]).Volume + rails_pack.common(qev_closed["Nose_clamp"]).Volume < 0.01),
    ("rails end in the rear disk; disk clear of moving parts and lines (%.2f, %s)" % (rear_disk_gap, rear_disk_near),
     abs(rails_pack.BoundBox.ZMin - z_rail_pk0) < 0.05 and rear_disk_gap >= CLEAR),
    ("ramp presses only on 330..30 (outside %.3f mm)" % press_out, press_out < 0.01),
    ("ramp touches %.1f..%.1f, switch (>= %.1f) %.1f..%.1f deg" % (
        first_touch % 360.0, last_touch, SWITCH, sw_on % 360.0, sw_off),
     first_touch >= -30.0 and last_touch <= 30.0 and sw_on is not None),
    ("plunger stroke: full press %.2f, max %.2f (%.1f + %.1f gap)" % (press_flat, press_max, RAMP_PRESS, RAMP_GAP),
     abs(press_flat - RAMP_PRESS) < 0.05 and press_max <= RAMP_PRESS + 0.05),
    ("valve body clear of the ramp at FIRE (%.2f: plunger sticks out %.1f, press %.1f)" % (body_ramp, PL_L, RAMP_PRESS),
     body_ramp >= PL_L - RAMP_PRESS - 0.05),
    ("ramp fixed in the press position, seated on its mount block (%.2f)" % ramp_seated, ramp_seated < 0.01),
    ("ramp block on the liner: 2 x M3 through its wall clear of the groove (nut floor %.1f), liner one solid"
     % _wall_left, insert_blind and liner_one),
    ("ramp mount block and insert holes clear of the groove (%s), stations six phases (%s)"
     % (far(groove_vs_mount), far(mount_vs_stations, 2.0)), groove_vs_mount >= 2.0 and mount_vs_stations >= CLEAR),
    ("rear plate (a spider Ø%.0f) on the %d bay-1 studs straight from the liner (%.2f), grip on"
     " the plate (%.2f); studs vs the rear disk, rotor and its fittings over a turn %s"
     % (2.0 * SKIN_R_IN, len(STRUT_ANGLES), strut_on, grip_on_plate, far(strut_turn)),
     strut_on < 0.05 and grip_on_plate < 0.05 and strut_turn >= 2.0),
    ("grip two halves split at y 0 (the channels between them); cable, outlet and valve inside (wall %.1f at the %s);"
     " cable stop inside the grip; %d x M3 x 20 across the halves clear of every channel by %.1f, the pivot an M3 x 50"
     % (chan_wall, _wall_worst, len(GRIP_BOLTS), grip_bolt_clear),
     grip_one and chan_wall >= 1.5 and stop_in_pommel and grip_bolt_clear >= GRIP_BOLT_CLEAR),
    ("lever's wire: barrel nipple Ø%.0f across the tail's tip (boss wall %.1f); Bowden housing %.0f mm deep in its seat"
     " under the gate, on the channel's shoulder in the grip" % (NIP_D, nip_wall, GATE_SEAT), nip_wall >= 1.5 and GATE_SEAT >= 4.0),
    ("collector 1 -> 6 on the rear plate's tab (seated %s), %d hoses %.2f apart, %s off the stator body; clear of the struts,"
     " cable, rotor, coupling, lines, grip, lever (%s, %s)"
     % ("yes" if coll_seated else "NO", N, coll_hose_gap, far(coll_stator), far(coll_gap), coll_near),
     coll_seated and coll_hose_gap >= 0.5 and coll_stator >= 0.5 and coll_gap >= 1.0),
    ("star shaft: located in the front ring pad's 608 (star hub's spigot, spacer, collar: %.2f float); the other 608"
     " floats in the box; star gear's hub %.2f off gear A's tips; cover on 2 x M3 x 20" % (STAR_SPIGOT_GAP, STAR_HUB_CLEAR),
     STAR_HUB_CLEAR >= 0.5),
    ("front support, %s: held in the housing under its lip and retainer (%.2f); off the hub's journal, shoulder and"
     " retainer by %.2f" % (FRONT_BRG["name"], front_held, front_run),
     front_held < 0.05 and (0.05 <= front_run <= 0.25 if FRONT_AX else front_run < 0.05)),
    ("61812: outer race between the cage's lip and its retainer (%.2f), inner race on the disk's sleeve (%.2f, floats)"
     % (rear_race_held, rear_race_on_sleeve), rear_race_held < 0.05 and rear_race_on_sleeve < 0.05),
    ("MQR: rotor on its TPU pad in the rear disk (%.2f), stator on the rear plate (%.2f)" % (rotor_on_pad, stator_on_plate),
     rotor_on_pad < 0.05 and stator_on_plate < 0.05),
    ("what turns in the tail (disk, sleeve, rotor's fittings) clear of what stands (%.2f, %s)" % (tail_gap, tail_near), tail_gap >= CLEAR),
    ("lever 0..%.0f deg in 6 steps: no overlap with the grip, pommel, pin, plate, cable, hoses, valve (%.3f mm3 %s);"
     " closed %.2f off the grip" % (LEV_ANG, _lev_hit, _lev_worst, lever_closed), _lev_hit < 0.01 and lever_closed >= 1.0),
    ("stage 1 (0..%.0f deg, free end %.1f mm): dead-man pressed %.2f of %.1f, pusher %.2f off released;"
     " over-travel %.1f by %.0f deg (<= %.0f)" % (STAGE1, stage1_travel, press_s1, DM_STROKE, push_released, overtravel,
                                                 LEV_ANG, OVERTRAVEL_MAX),
     abs(press_s1 - DM_STROKE) < 0.05 and push_released >= PUSH_GAP - 0.05 and 0.0 < overtravel <= OVERTRAVEL_MAX),
    ("stage 2 (%.0f..%.0f deg): the tail takes up %.1f mm of slack, then pulls the wire %.2f = gate travel %.1f"
     % (STAGE1, LEV_ANG, WIRE_SLACK, wire_travel, GATE_TRAVEL), abs(wire_travel - GATE_TRAVEL) < 0.05 and WIRE_SLACK > 0.5),
    ("gate closed stops a ball anywhere across the neck (%.0f mm3), open lets it by (%.2f)"
     % (_gate_block, _gate_free), _gate_block > 1.0 and _gate_free >= 0.5),
    ("gate housing glued on the neck (%d solid), pin through its own hole (%.3f mm3 into the feed head);"
     " clear of the star over its turn (%.2f) and the lip (%s)"
     % (len(gate_housing.Solids), gate_head, gate_star, far(gate_lip)),
     len(gate_housing.Solids) == 1 and gate_head < 0.01 and gate_star >= CLEAR and gate_lip >= CLEAR),
    ("gate cable %.0f mm (through the rear plate into the grip) clear of the liner, frame, disks, strap,"
     " struts, stator, box, cup, star (%.2f, %s)"
     % (CABLE_LEN, cable_gap, cable_near), cable_gap >= 2.0),
    ("left hand round the grip (R 36) %s to the gun (%s)" % (far(hand_l_gap), hand_l_near), hand_l_gap >= 5.0),
    ("feed bench as library: %d of %d [OK]" % (fb_n_ok, len(FB_CHECKS)), _fb_ok and fb_n_ok == len(FB_CHECKS)),
    ("handoff at 180 (LOAD): pocket on the ball seat %.2f mm, speed %.3f" % (_handoff_err, SPEED_RATIO),
     _handoff_err < 0.3 and LOAD_A <= 180.0 <= LOAD_B and abs(SPEED_RATIO - 1.0) <= 0.02),
    ("star vs whole stations, six phases (%.2f)" % star_top, star_top >= CLEAR),
    ("guard %.1f..%.1f deg: ball gap %.2f (1..2)" % (GUARD_PHI0, GUARD_END, guard_ball), 1.0 <= guard_ball <= 2.0),
    ("star drive %d -> %d | %d -> %d -> %d (m%.1f): star %.3f turns per pack turn"
     % (Z_RIM, Z_A, Z_B, Z_I, Z_S, GEAR_M, train_star_turns), abs(train_star_turns + STAR_TURNS) < 1e-9),
    ("train centres on pitch sums (%.3f) and meshes without overlap (%.2f mm3)" % (centre_err, mesh_worst),
     centre_err < 1e-6 and mesh_worst < 1.0),
    ("rim (rear barrel-plate) clear of the closed QEVs (%.2f)" % rim_vs_closed, rim_vs_closed >= CLEAR),
    ("air: the six R lines over the stroke clear of the stator, its hoses, the 61812's cage, the plate (%.2f, %s)"
     % (lines_fixed, lines_near), lines_fixed >= CLEAR),
    ("stations (six phases) clear of the 61812's cage and retainer (%s)" % far(aft_gap), aft_gap >= CLEAR),
    ("wrap handle from the left over the top, crank on the right", math.sin(math.radians(CARRY_W[0])) * crank_shaft.BoundBox.Center.y < 0.0
     and carry_handle.BoundBox.XMax > SKIN_R_OUT
     and abs(crank_shaft.BoundBox.Center.y) > abs(crank_shaft.BoundBox.Center.x)),
    ("pack drive %d:%d bevel (m%.0f) -> gear %d in rim %d: %.3f pack turn per crank turn, %.0f rpm -> %.1f shots/s"
     % (CB_ZB, CB_ZS, CB_M, CP_Z, Z_RIM, PACK_PER_CRANK, CRANK_RPM, SHOTS_PER_S),
     abs(PACK_PER_CRANK - 0.5) < 1e-9 and abs(SHOTS_PER_S - 3.0) < 1e-9),
    ("crank gear on the rim: centre %.3f on the pitch sum, mesh overlap %.2f mm3 over a rim tooth"
     % (abs(CP_C.Length - (R_RIM + R_CP)), crank_mesh_worst),
     abs(CP_C.Length - (R_RIM + R_CP)) < 1e-6 and crank_mesh_worst < 1.0),
    ("bevel pair %d:%d, cones %.1f/%.1f deg: mesh overlap %.2f mm3 over a tooth"
     % (CB_ZS, CB_ZB, CB_DS, CB_DB, bevel_mesh_worst), bevel_mesh_worst < 1.0),
    ("drive vs stations, six phases %s >= %.2f" % (far(drive_vs_stations), CLEAR), drive_vs_stations >= CLEAR),
    ("drive vs rim (all but its gear) %s, star train / feed / handle %s, frame %s"
     % (far(drive_vs_rim, 2.0), far(drive_vs_fixed), far(drive_vs_frame, 2.0)),
     min(drive_vs_rim, drive_vs_fixed, drive_vs_frame) >= CLEAR),
    ("crank brackets stand on the frame (spar, front ring); gears clear them by %.2f" % gears_vs_bracket,
     bracket_on_ring and gears_vs_bracket >= CLEAR and bevels_apart >= CLEAR),
    ("room for the hand (crank R %.0f, fist R %.0f x %.0f): %.1f to the gun (%s), %.1f to its own boss"
     % (CRANK_ARM_R, HAND_R, HAND_W, hand_gap, hand_near, hand_own), hand_gap >= 20.0 and hand_own >= 5.0),
    ("crank arm R %.0f and knob Ø%.0f x %.0f over a crank turn (%d steps of %.0f deg): %s to the gun (%s);"
     " hub on the shaft end, %.1f off its boss"
     % (CRANK_ARM_R, CK_KNOB_OD, CK_KNOB_L, len(crank_poses), CK_STEP, far(crank_gap),
        crank_near if crank_gap < 99.0 else "nothing nearer", crank_boss),
     crank_gap >= DRIVE_PAD and crank_seated and crank_boss >= 5.0),
    ("crank turns clockwise seen from its knob (top %s), the forward way of a drill or a flexible shaft;"
     " bevel pair with the lay bevel behind the apex" % ("forward" if CRANK_TOP_DZ > 0 else "aft"), CRANK_CW),
    ("knob turns on its own pin (bore %.2f, %.1f off the arm), inside the room for the hand (%.1f %%)"
     % (knob_pin_gap, knob_arm_gap, 100.0 * knob_in_room),
     knob_pin_gap >= 0.15 and knob_arm_gap >= 0.5 and knob_in_room > 0.999),
    ("wrap handle in the CG's plane (z %.0f, CG %.1f off) on two rails at %.0f / %.0f deg: rails on the liner (%.2f) and the"
     " front ring (%.2f), handle on the rails (%.2f), %.2f mm3 in the liner, liner bolts %.2f off the groove"
     % (z_carry, CG_OFF_Z, CARRY_W[0], CARRY_W[1], rail_on_liner, rail_on_ring, hoop_on_rails, carry_in_liner, rail_groove),
     rail_on_liner < 0.05 and rail_on_ring < 0.05 and hoop_on_rails < 0.05 and carry_in_liner < 0.01 and rail_groove >= 1.0
     and abs(CG_OFF_Z) < 2.0 and hoop_one),
    ("PVC tube Ø%.0f x %.0f, %.0f mm long, one bend R %.0f (%.1f x its Ø), in two printed feet (%.2f off the sockets, %.3f mm3"
     " in them), an M3 x 50 across each" % (CARRY_TUBE_OD, CARRY_TUBE_WALL, CARRY_TUBE_L, CARRY_R, CARRY_R / CARRY_TUBE_OD,
                                           tube_socket_gap, tube_in_feet),
     tube_in_feet < 0.01 and 0.05 <= tube_socket_gap <= 0.4 and CARRY_R >= 5.0 * CARRY_TUBE_OD and all(f_.L == 50.0 for f_ in PIN_FAST)),
    ("strap lugs either side of the CG (+%.0f / -%.0f, y %.1f off): on the liner (%.2f) and the bearing housing (%.2f); the handle's"
     " top at x %.1f, under the cup's floor at %.1f" % (z_post_f - z_carry, z_carry - z_post_r, CG_OFF_Y, carry_seat_r, carry_seat_f, carry_top, cup_floor),
     carry_seat_r < 0.05 and carry_seat_f < 0.05 and carry_rear_on_liner and abs(CG_OFF_Y) < 1.0 and hopper_free),
    ("handle clear of the cup, feed head, gate and cable, star train, frame, pack (%s, %s); rails (%s, %s); strap rings"
     " through the lugs' eyes at z %.0f / %.0f (%s, %s)"
     % (far(carry_gap), carry_near, far(rail_gap), rail_near, z_post_r, z_post_f, far(ring_gap), ring_near),
     carry_gap >= 2.0 and rail_gap >= 0.5 and ring_gap >= 0.3),
    ("fist anywhere on the handle, 270..30 deg (R %.0f x %.0f round it), %s from the gun (%s)"
     % (CARRY_FIST_R, CARRY_GRIP_L, far(fist_gap), fist_near), fist_gap >= CARRY_CLEAR - 0.05),
    ("tripod pad under the CG: socket for a Ø%.0f ball at z %.0f, y %.0f (CG %.1f / %.1f off), %.0f below it;"
     " keel on the liner (%.2f) and the front ring (%.2f)"
     % (TRIPOD_BALL_D, z_tripod, y_tripod, TRIPOD_OFF_Z, TRIPOD_OFF_Y, CG.x - P_BALL.x, tripod_seat_r, tripod_seat_f),
     tripod_seat_r < 0.05 and tripod_seat_f < 0.05 and tripod_on_liner and abs(TRIPOD_OFF_Z) < 2.0
     and abs(TRIPOD_OFF_Y) < 1.0),
    ("tripod socket depth %.0f, mouth Ø%.1f, ball seated %.2f; keel and boss clear of the pack, ramp, rim, drive (%s, %s);"
     " ball and post tilted ±%.0f deg %s from the gun (%s)"
     % (TRIPOD_SOCKET_DEPTH, TRIPOD_MOUTH_D, tripod_ball_seat, far(tripod_gap), tripod_near, TRIPOD_TILT,
        far(tripod_tilt_gap), tripod_tilt_near),
     tripod_ball_seat <= TRIPOD_SOCKET_CLEAR + 0.01 and tripod_gap >= 2.0 and tripod_tilt_gap >= 5.0),
    ("open frame (not full casing)", frame_ok),
    ("six phases", len(stations) == 6),
    ("closed station L %.1f ≈ %.1f (750 + trough %.1f)" % (closed_L, TARGET_L, TRAY_L), abs(closed_L - TARGET_L) <= 0.6),
    ("no full-length tube", z_case1 < z_tip_b - 200.0),
    ("fasteners: %s; every M3 fits 6/20/50 with its nut and 3 mm under head and nut (%s)"
     % (", ".join("%s %s" % (k_, ("%.0f" % v_) if isinstance(v_, float) else v_) for k_, v_ in sorted(FAST_BOM.items())),
        ", ".join(m3_bad) or "all"), not m3_bad),
    ("fasteners known short of their window: %s" % ("; ".join(m3_exc) or "none"), True),
    ("frame studs, ramp, feed, liner, carry, keel and bracket fasteners clear of the stations, six phases (%s);"
     " of the hub and its fasteners (%s)" % (far(fast_vs_stations), far(fast_vs_hub)),
     fast_vs_stations >= CLEAR and fast_vs_hub >= CLEAR),
    ("printed parts one valid solid each (%d parts%s)" % (len(PRINTED_ONE), (": not " + ", ".join(printed_bad)) if printed_bad else ""),
     not printed_bad),
    ("fastener cuts and fuses (%d): every part valid and lost no more than its cutters (%s); not refined: %s;"
     " feed head %.0f cm3" % (len(CUT_LOG), ", ".join(cut_bad) or "all", ", ".join(cut_one) or "none", feed_head.Volume / 1000.0),
     not cut_bad and feed_head.Volume > 30000.0),
    ("M6 studs: no nut or washer in another (%.2f mm3); box on the front ring on bosses over the %.1f mm gap"
     % (stud_self, box_tie_gap), stud_self < 0.01),
    ("front hub one solid, clear of the star-drive box and its train (%.2f) and of the bearing housing (%.2f)"
     % (hub_vs_box, hub_vs_housing), hub_one and hub_vs_box >= CLEAR and hub_vs_housing >= CLEAR),
    ("rear rail disk one solid (the rotor's notches open aft, a web of %.1f ahead), liner halves one solid each" % (REAR_DISK_Z1 - z_notch1),
     rear_disk_one and liner_halves_ok),
    ("EVA skin %.0f mm one solid on the lug tips (bore r %.1f = stud r %.1f + lug %.1f), z %.0f..%.0f, %d holes"
     % (SKIN_T, SKIN_R_IN, STUD_R, STUD_LUG_D / 2.0, SKIN_Z0, SKIN_Z1, len(SKIN_HOLES)), skin_one and skin_on_lugs),
    ("EVA skin glued: on the liner's two lands, the front ring's, the rear plate's rim and the bearing"
     " housing (%.2f); %.0f cm2 of land under it" % (skin_glued, SKIN_GLUE / 100.0), skin_glued < 0.01 and SKIN_GLUE > 20000.0),
    ("EVA end cap one solid on the rear plate's aft face, edge to edge with the skin (%.2f): R %.1f..%.0f, %d nut holes;"
     " clear of the grip, the lever over its squeeze, the hoses, the cable, the studs (%.2f, %s)"
     % (cap_glued, CAP_R_IN, SKIN_R_OUT, len(CAP_HOLES), cap_gap, cap_near),
     cap_one and cap_glued < 0.01 and cap_gap >= 1.0 and SKIN_R_OUT - CAP_R_IN >= 40.0),
    ("EVA skin clear of what crosses it or lies under it (%.2f, %s; rests on %s), of the pack (r %.1f to its bore %.1f)"
     " and the crank over a turn (%s)"
     % (skin_near[0][0], skin_near[0][1], ", ".join("%s %.2f" % (n_, g_) for g_, n_ in skin_rest) or "nothing",
        SKIN_PACK_R, SKIN_R_IN, far(skin_crank)),
     skin_near[0][0] >= 0.5 and all(g_ > -1e-6 for g_, _ in skin_rest) and SKIN_R_IN - SKIN_PACK_R >= 5.0
     and skin_crank >= DRIVE_PAD),
    ("glue lands on the P2S bed (%.0f): %s; cut round %d bolts (%s)"
     % (BED, ", ".join("%s %.1f" % (n_, w_) for n_, w_ in SKIN_BED), len(SKIN_LAND_ACCESS),
        "; ".join(SKIN_LAND_ACCESS) or "none"), all(w_ <= BED - 1.0 for _, w_ in SKIN_BED)),
]
report = [
    NAME,
    "  sketch                 : full mechanism sketch (stages 4+5+6+7; NOT frozen)",
    "  stroke (bench)         : %.1f mm" % BENCH_STROKE,
    "  law                    : FIRE 330–30; OPEN 30–120; LOAD 120–240; CLOSE 240–330",
    "  pack R                 : %.2f (pinned = breech_pack; rail feet floor 66.3)" % R_PACK,
    "  cam                    : liner Ø%.0f (groove R %.0f, blind, %.0f mm floor); it is the frame here"
    % (cam_od, CAM_R, GROOVE_FLOOR),
    "  rails                  : carriage + nose ride the Al tubes; rear disk R %.0f at z %.0f..%.0f"
    % (REAR_DISK_R, REAR_DISK_Z0, REAR_DISK_Z1),
    "  hub                    : closed — AirTAC on each carriage (bracket on the 30° ear), body r %.1f..%.1f;"
    " station gap with valves %.2f mm" % (R_PACK + VALVE_Y - A_W / 2, R_PACK + VALVE_Y + A_W / 2, gap_nbr),
    "  line A                 : rigid, %.0f mm of 6x4 tube (%.2f cm3; pilot pocket %.2f cm3)"
    % (LINE_A_L, LINE_A_V, pocket_v),
    "  line R                 : flexes %.1f with the carriage, to the MQR rotor's port at z %.0f"
    % (BENCH_STROKE, Z_ROTOR_PORT),
    "  firing ramp            : r %.1f, low z %.1f; touch %.1f..%.1f, switch %.1f..%.1f, full %.0f..%.0f deg;"
    " press %.2f" % (R_TIP, z_ramp_low, first_touch % 360, last_touch, sw_on % 360, sw_off,
                     (-(30 - RAMP_RISE)) % 360, 30 - RAMP_RISE, press_flat),
    "  ramp                   : fixed in the press position on a block in the liner (z %.1f..%.1f, M3 x 20 on nuts);"
    " air is switched by the dead-man" % (z_blk0, z_blk1),
    "  controls               : flintlock grip behind the rear plate (%.0f long, brass pommel); one lever along its"
    " front, %.0f long, pivot at the top behind the plate, %.0f deg; stage 1 to %.0f deg = air (dead-man, %.1f mm at the free end),"
    " stage 2 = balls (Bowden %.0f mm, slack %.1f, gate pin %.1f); free end %.1f mm"
    % (GRIP_LEN, LEV_L, LEV_ANG, STAGE1, stage1_travel, CABLE_LEN, WIRE_SLACK, GATE_TRAVEL, finger_travel),
    "  rear frame             : plate R %.0f carries the MQR stator and the grip; a spider out to Ø%.0f on the %d bay-1"
    " M6 studs, straight from the liner (a cylinder to the MQR)" % (RP_R, 2.0 * SKIN_R_IN, len(STRUT_ANGLES)),
    "  feed                   : feed_bench star (3 pockets, 2:1) at the top; handoff 180°;"
    " guard %.0f–%.0f° following the close" % (GUARD_PHI0, GUARD_END),
    "  star drive             : rim %d on the breech clamps (z %.1f..%.1f) -> %d | %d -> %d -> %d;"
    " layshaft R %.0f at %.0f°" % (Z_RIM, P1_Z0, P1_Z1, Z_A, Z_B, Z_I, Z_S, L_C.Length, L_ANG),
    "  frame envelope Ø       : %.0f (liner); was %.0f" % (case_od, CASE_OD_START),
    "  air                    : MQR rotor in the rear disk z %.0f..%.0f, stator to z %.0f; the disk's sleeve in a floating %s (%.0f x %.0f x %.0f) at z %.1f..%.1f, cage on 4 legs off the spider"
    % (z_rotor0, z_rotor1, z_stator0, RBRG["name"], RBRG["d"], RBRG["D"], RBRG["B"], z_rb0, z_rb1),
    "  air supply             : no buffer; Ø%.0f hose from the receiver -> pommel -> dead-man in the grip -> 1→6 collector"
    " on the rear plate -> six M5 ports of the stator (a helix as on the drawing, z %.0f..%.0f)" % (SUPPLY_HOSE_OD, _zp[0], _zp[-1]),
    "  pack drive             : crank axis across the barrels (%s) at z %.0f (middle of the closed QEV);"
    " bevel %d:%d m%.0f -> lay shaft at r %.0f -> gear %d in rim %d; %.2f pack turn per crank turn"
    % ("+Y, right" if CRANK_SIDE > 0 else "−Y, left", Z_CRANK, CB_ZB, CB_ZS, CB_M, CP_C.Length, CP_Z, Z_RIM,
       PACK_PER_CRANK),
    "  crank                  : top of the crank goes %s; arm R %.0f on the shaft end (|y| %.0f), knob Ø%.0f x %.0f"
    " on its own pin Ø%.0f"
    % ("forward, clockwise seen from the knob" if CRANK_CW else "aft, anticlockwise seen from the knob",
       CRANK_ARM_R, max(abs(crank_shaft.BoundBox.YMin), abs(crank_shaft.BoundBox.YMax)), CK_KNOB_OD, CK_KNOB_L,
       CK_PIN_D),
    "  rate                   : %.0f rpm on the crank -> %.1f shots/s" % (CRANK_RPM, SHOTS_PER_S),
    "  room for the hand      : y %.0f..%.0f, r %.0f round the crank axis; %.1f mm to the gun (%s)"
    % (hand_space.BoundBox.YMin, hand_space.BoundBox.YMax, CRANK_ARM_R + HAND_R, hand_gap, hand_near),
    "  mass                   : %.2f kg — printed %.2f, steel %.2f, Al %.2f, wood %.2f, EVA %.2f, bought (est.) %.2f,"
    " other %.2f; balls, the receiver hose not counted (bolts, studs and nuts are)"
    % (MASS_GUN / 1000.0, mass_by.get("printed", 0) / 1000.0, mass_by.get("steel", 0) / 1000.0,
       mass_by.get("Al", 0) / 1000.0, mass_by.get("wood", 0) / 1000.0, mass_by.get("EVA", 0) / 1000.0,
       mass_by.get("bought (est.)", 0) / 1000.0,
       sum(v_ for k_, v_ in mass_by.items() if k_ not in ("printed", "steel", "Al", "wood", "EVA", "bought (est.)")) / 1000.0),
    "  centre of gravity      : x %.1f  y %.1f  z %.1f (z %.0f from the crank axis, %.0f ahead of the liner's rear face)"
    % (CG.x, CG.y, CG.z, CG.z - Z_CRANK, CG.z - z_cam0),
    "  mass by unit           : " + ", ".join("%s %.0f g (z %.0f)" % (g_, m_, c_.z) for g_, m_, c_ in mass_groups),
    "  carry                  : wrap handle, PVC tube Ø%.0f x %.0f x %.0f, R %.0f round the axis from low left over the top to"
    " high right, in the CG's plane (z %.0f); two printed feet on two rails at %.0f / %.0f deg (liner to front ring); strap lugs"
    " at z %.0f / %.0f (CG +%.0f / -%.0f)"
    % (CARRY_TUBE_OD, CARRY_TUBE_WALL, CARRY_TUBE_L, CARRY_R, z_carry, CARRY_W[0], CARRY_W[1], z_post_r, z_post_f,
       z_post_f - z_carry, z_carry - z_post_r),
    "  tripod                 : keel under the frame z %.0f..%.0f (liner to front ring), socket for a Ø%.0f ball"
    " %.0f deep under the CG, ball centre x %.0f" % (z_keel0, z_keel1, TRIPOD_BALL_D, TRIPOD_SOCKET_DEPTH, P_BALL.x),
]
report.append("  phases:")
for n, ang, u, dz, tag in phases:
    report.append("    %d @ %3.0f°  u=%.2f  dz=%6.1f  %s" % (n, ang, u, dz, tag))
report += [
    "  overall LxWxH         : %.0f x %.0f x %.0f mm (was %.0f long)" % (gun_L, gun_W, gun_H, L_START),
    "  not drawn             : wheeled carriage, freeze",
    "  fasteners             : " + ", ".join("%s %s" % (k_, ("%.0f" % v_) if isinstance(v_, float) else v_)
                                            for k_, v_ in sorted(FAST_BOM.items()))
    + "; tie studs 2 x M3 x %.0f per station; bought threads: %d x M4" % (STUD_L_PACK, len(M4_EXC)),
    "  M6 studs (cut to)     : " + ", ".join("%d x %.0f" % (n_, l_) for l_, n_ in sorted(
        {L_: sum(1 for f_ in FRAME_STUDS if 5.0 * math.ceil(f_.L / 5.0) == L_)
         for L_ in set(5.0 * math.ceil(f_.L / 5.0) for f_ in FRAME_STUDS)}.items())) + " mm",
    "  front support         : %s (%.1f x %.1f x %.2f) at z %.1f..%.1f on the hub's seat; housing to the front ring on M6 studs"
    % (FRONT_BRG["name"], FRONT_BRG["d"], FRONT_BRG["D"], FRONT_BRG["B"], z_brg0, z_brg1),
    "  EVA skin              : %.0f mm, r %.0f..%.0f, z %.0f..%.0f (the rear plate's aft face to the bearing housing's front),"
    " %.2f m2, %.0f g; sheet %.0f x %.0f (unrolled at R %.1f, the seam under the keel); contact glue on %.0f cm2 of"
    " lands: hoops on ribs in the liner's two lug bands (the rear one open 30 deg either side of the split), and"
    " on the front ring (open %.0f..%.0f deg on top), the rear plate's rim, the bearing housing (Ø%.0f);"
    " pattern eva_skin_pattern.svg"
    % (SKIN_T, SKIN_R_IN, SKIN_R_OUT, SKIN_Z0, SKIN_Z1, SKIN_AREA / 1e6, MS_RHO["EVA"] * skin.Volume / 1000.0, SKIN_L,
       SKIN_Z1 - SKIN_Z0, SKIN_R_MID, SKIN_GLUE / 100.0, FRING_LAND_OPEN[0], FRING_LAND_OPEN[1], 2.0 * HOUS_RO),
    "  EVA end cap           : %.0f mm on the rear plate's aft face, R %.1f..%.0f, %d holes round the studs' nuts, %.0f g"
    % (SKIN_T, CAP_R_IN, SKIN_R_OUT, len(CAP_HOLES), MS_RHO["EVA"] * skin_cap.Volume / 1000.0),
    "  EVA skin holes        : " + "; ".join(
        "%s (%s)" % (n_, "open to an edge" if open_ else ("slit %.0f mm" % math.hypot(sl_[2] - sl_[0], sl_[3] - sl_[1])
                                                          if sl_ else SKIN_THREADS.get(n_, "no slit")))
        for n_, open_, sl_, _ in SKIN_HOLES),
    "  under the EVA skin    : the frame's stud nuts, M3 of " + ", ".join(SKIN_COVERS) + " (the skin goes on last)",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
report.append("  full turn             : breech_mechanism_sweep.py (separate run)")
print("\n".join(report))

FV.STYLES["ph0"] = ((0.92, 0.40, 0.16), 32)
FV.STYLES["ph1"] = ((0.85, 0.55, 0.30), 40)
FV.STYLES["ph2"] = ((0.55, 0.65, 0.55), 45)
FV.STYLES["ph3"] = ((0.30, 0.62, 0.75), 38)
FV.STYLES["ph4"] = ((0.60, 0.58, 0.50), 45)
FV.STYLES["ph5"] = ((0.88, 0.48, 0.28), 40)
FV.STYLES["plate"] = ((0.42, 0.44, 0.48), 8)
FV.STYLES["frame"] = ((0.72, 0.68, 0.55), 40)
FV.STYLES["cam"] = ((0.35, 0.38, 0.42), 60)
FV.STYLES["rail"] = ((0.55, 0.58, 0.62), 20)
FV.STYLES["feed"] = ((0.55, 0.50, 0.40), 50)
FV.STYLES["star"] = ((0.95, 0.80, 0.10), 0)
FV.STYLES["gear"] = ((0.20, 0.62, 0.35), 0)
FV.STYLES["ramp"] = ((0.85, 0.12, 0.12), 0)
FV.STYLES["drive"] = ((0.30, 0.32, 0.36), 15)
FV.STYLES["pellet"] = ((0.88, 0.88, 0.92), 15)
FV.STYLES["crank"] = ((0.25, 0.25, 0.28), 10)
FV.STYLES["hose"] = ((0.20, 0.55, 0.45), 35)
FV.STYLES["mqr"] = ((0.45, 0.70, 0.95), 25)
FV.STYLES["brg"] = ((0.35, 0.55, 0.85), 20)
FV.STYLES["deadman"] = ((0.75, 0.25, 0.20), 15)
FV.STYLES["guard"] = ((0.60, 0.30, 0.75), 40)
FV.STYLES["carry"] = ((0.28, 0.28, 0.30), 15)
FV.STYLES["hand"] = ((0.95, 0.75, 0.60), 80)
FV.STYLES["wood"] = ((0.45, 0.27, 0.13), 0)
FV.STYLES["brass"] = ((0.80, 0.63, 0.28), 0)
FV.STYLES["eva"] = ((0.34, 0.25, 0.18), 30)

# 2026-11-22: the full-turn sweep and the joint audit read their bodies from this cache (keyed by
# the sources) instead of building the mechanism again each (~3.5 min apiece).
exec(open(os.path.join(REPO, "gatling", "breech_cache.py")).read(), globals())
_tick("cache for the sweep and the joint audit…")
bc_write(all(ok for _, ok in checks))
_tick("cache written: " + BC_WRITTEN)

if BREECH_MECH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, st in enumerate(stations):
    sc.add("Phases", "Station_%d_%d" % (i + 1, int(phases[i][1])), st, "ph%d" % i)
sc.add("Fire", "Firing_ramp", ramp_body, "ramp")
sc.add("Fire", "Ramp_mount_block", guide_block, "frame")
sc.add("Controls", "Grip", grip, "wood")
sc.add("Controls", "Pommel", pommel, "brass")
sc.add("Controls", "Lever", lever, "ramp")
sc.add("Controls", "Lever_pin", lever_pin, "drive")
sc.add("Controls", "Deadman_pusher", dm_pusher, "drive")
sc.add("Controls", "Gate_cable", gate_cable, "drive")
sc.add("Controls", "Gate_wire", gate_wire, "drive")
sc.add("Controls", "Gate_housing", gate_housing, "feed")
sc.add("Controls", "Gate_pin", gate_pin, "ramp")
sc.add("Controls", "Gate_spring", gate_spring, "brg")
sc.add("Reference", "Left_hand_on_grip", hand_left, "hand")
sc.add("Air", "Rear_struts", rear_struts, "frame")
sc.add("Skin", "Front_barrel_plate", front_plate, "plate")
sc.add("Skin", "Pack_frame", pack_frame, "frame")
sc.add("Skin", "Rear_rail_disk", rear_disk, "plate")
sc.add("Feed", "Star", star0, "star")
sc.add("Feed", "Feed_head", feed_head, "feed")
sc.add("Feed", "Lip_TPU", feed_lip, "deadman")
sc.add("Feed", "Cup", feed_cup, "feed")
sc.add("Feed", "Feed_guard", feed_guard, "guard")
sc.add("Feed", "Ball_handoff", ball_at(180.0), "pellet")
sc.add("Feed", "Ball_closing", ball_at(260.0), "pellet")
sc.add("Star_drive", "Idler", gear_i, "gear")
sc.add("Star_drive", "Star_gear", gear_s, "gear")
sc.add("Star_drive", "Star_shaft", star_shaft, "drive")
sc.add("Star_drive", "Layshaft", lay_shaft, "drive")
sc.add("Star_drive", "Idler_shaft", idl_shaft, "drive")
sc.add("Star_drive", "Gearbox", gearbox, "frame")
sc.add("Drive", "Crank_rim_gear_60", crank_gear, "gear")
sc.add("Drive", "Lay_shaft", pin_shaft, "drive")
sc.add("Drive", "Bevel_lay", bevel_small, "gear")
sc.add("Drive", "Bevel_crank", bevel_big, "gear")
sc.add("Drive", "Crank_shaft", crank_shaft, "drive")
sc.add("Drive", "Crank_bracket", crank_bracket, "frame")
sc.add("Drive", "Crank_bearings_608", crank_bearings, "brg")
sc.add("Drive", "Crank_arm", crank_arm, "crank")
sc.add("Drive", "Crank_knob", crank_knob, "wood")
sc.add("Drive", "Crank_knob_pin", crank_knob_pin, "drive")
sc.add("Reference", "Hand_space", hand_space, "hand")
sc.add("Reference", "Carry_hand", carry_hand, "hand")
sc.add("Carry", "Tripod_pad", tripod_pad, "frame")
sc.add("Reference", "Tripod_ball_50", tripod_ball, "brg")
sc.add("Carry", "Carry_tube_PVC", carry_tube, "carry")
sc.add("Carry", "Carry_feet", carry_feet, "frame")
sc.add("Carry", "Carry_rails", carry_rails, "carry")
sc.add("Carry", "Strap_lugs", strap_lugs, "carry")
sc.add("Carry", "Sling_loops", sling, "carry")
sc.add("Air", "Rear_bearing_61812", rear_bearing, "brg")
sc.add("Air", "Rear_bearing_cage", rear_cage, "frame")
sc.add("Air", "Rear_bearing_retainer", rear_ret, "frame")
sc.add("Air", "Rotor_pad_TPU", soft_coup, "drive")
sc.add("Air", "Rotor_fittings", rotor_fittings, "drive")
sc.add("Air", "MQR_rotor", mqr_rotor, "mqr")
sc.add("Air", "MQR_stator", mqr_stator, "mqr")
sc.add("Air", "Rear_plate", mqr_plate, "frame")
sc.add("Air", "Deadman_valve", deadman, "deadman")
sc.add("Air", "Supply_stub", air_supply, "hose")
sc.add("Air", "Supply_hose_end", supply_hose, "hose")
sc.add("Air", "Collector_1to6", collector, "mqr")
sc.add("Air", "Collector_fittings", coll_fittings, "drive")
sc.add("Air", "Collector_hoses", coll_hoses, "hose")
sc.add("Star_drive", "Star_bearings_608", star_bearings, "brg")
sc.add("Star_drive", "Star_bearing_cover", star_cover, "frame")
sc.add("Star_drive", "Star_spacer", star_spacer, "drive")
sc.add("Drive", "Lay_shaft_collar", lay_collar, "frame")
sc.add("Drive", "Crank_spacer", crank_spacer, "frame")
sc.add("Pack", "Pack_hub", pack_hub, "gear")
sc.add("Pack", "Front_bearing", front_bearing, "brg")
sc.add("Pack", "Inner_race_retainer", brg_ret_in, "gear")
sc.add("Skin", "Bearing_housing", brg_housing, "frame")
sc.add("Skin", "Outer_race_retainer", brg_ret_out, "frame")
sc.add("Skin", "Liner_half_right", cam_r, "cam")
sc.add("Skin", "Liner_half_left", cam_l, "cam")
sc.add("EVA", "EVA_skin", skin, "eva")
sc.add("EVA", "EVA_end_cap", skin_cap, "eva")
sc.add("Feed", "Star_collar", star_collar, "frame")
sc.add("Star_drive", "Gears_A_B", gear_ab, "gear")
sc.add("Fasteners", "Frame_studs_M6", Part.makeCompound([f_.body for f_ in FRAME_STUDS]), "drive")
sc.add("Fasteners", "Bolts_M3", Part.makeCompound([f_.body for f_ in FASTENERS if f_.kind == "M3"]), "drive")
sc.add("Fasteners", "Bought_threads_M4", Part.makeCompound([b_ for _, b_ in M4_EXC]), "drive")
for n, ang, u, dz, tag in phases:
    p = polar(R_PACK + 70, ang, z_bf + dz)
    sc.label("Labels", "%d° %s" % (ang, tag), (p.x, p.y, p.z))
sc.finish(hidden_groups=("Labels",), opaque_groups=())
doc = sc.doc
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

import MeshPart
mesh_shape = assembly.copy()
mesh_shape.translate(V(0, 0, -mesh_shape.BoundBox.ZMin))
mesh_shape.exportStep(os.path.join(OUT_DIR, "breech_mechanism.step"))
MeshPart.meshFromShape(
    Shape=mesh_shape, LinearDeflection=0.4, AngularDeflection=0.5).write(
    os.path.join(OUT_DIR, "breech_mechanism.stl"))
skin_pattern_svg(os.path.join(OUT_DIR, "eva_skin_pattern.svg"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
with open(os.path.join(OUT_DIR, NAME + "_mass.txt"), "w") as f:
    f.write("%s — mass by body (g), centre (x, y, z mm); total %.0f g, CG (%.1f, %.1f, %.1f)\n"
            % (NAME, MASS_GUN, CG.x, CG.y, CG.z))
    for r_ in mass_rows:
        f.write("%-11s %-34s %8.1f  %-44s %7.1f %7.1f %7.1f\n" % (r_[0], r_[1], r_[2], r_[4], r_[3].x, r_[3].y, r_[3].z))

if not all(ok for _, ok in checks):
    raise SystemExit("gatling breech mechanism has [FAIL] checks")
