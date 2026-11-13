# -*- coding: utf-8 -*-
"""
Feed bench for the gatling: a hand-cranked pack mock, no air.

Prove which meter drops one soft pellet into each passing chute. The disk
stands in for the pack at R 66 (not frozen). Six chutes are the station's
front_cover_feed from gatling/linear_breech.py, taken through exec as a
library, so the pellet sees the same gutter as the real breech. A Ø10 shaft
in two 6000 bearings (10 x 26 x 8) carries the disk; the crank sits at
phi 90. A stationary guard follows the motion law from just before the
drop (170 deg) until the fitting tip is half a pellet inside the bore.
Under the chutes a kicker dumps the pellet into a tray at that close angle
so a run can be counted. The hopper is a low cup on a ring held by two
posts, not a rod.

One seat, three meters. Set METER before exec ("A1", "A2" or "A4"); default
A1.

  A1  auger x6. Bevel 20/20 (1:1) plus a compound spur 2 x 3. One
      stage of x6 would be a wheel about 240 mm across, because the layshaft
      has to sit aft of the front bearing; two stages keep the blanks
      printable. Single start, pitch 30 mm, tube ID 28, gate 22 x 3 mm
      every pitch (clear pocket 27 mm) joined by a peripheral rib. The
      drive shaft enters through the cup, past the last gate, so the outlet
      and the working pockets stay clear of a core. A continuous diametral
      helicoid fills the axis, and a Ø23.8 ball in a Ø28 tube always covers
      the axis, so that helicoid cannot leave a pocket; the gates are the
      wall the plan asked for (one ball fits, two do not).
  A2  three-pocket star, axis parallel to the pack shaft, spur 2:1, TPU lip
      on the inlet. 3 pockets x 2 turns = 6 drops.
  A4  two-finger escapement. A six-lobe cam on the disk times the fingers.
      6 lobes on the disk = 6 drops.

PELLET_D defaults to 23.8 and can be set before exec. The chute shape stays
the library gutter (barrel ID 23.8) until the measured batch moves it.
Forward crank rotation is +phi (stations climb 120 -> 180 -> 240). Index
the mesh so that direction drives pellets toward the chutes; reverse lifts
them back. Pack radius, shroud and length stay a sketch.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/feed_bench.py').read())"
    METER='A2'  # or A4, set in the same dict before exec

Exports: exports/gatling_feed_bench/
Library: set FEED_BENCH_LIBRARY = True before exec.
"""
import math
import os
import sys

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
import importlib
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
for _m in (G, FV, GR):
    importlib.reload(_m)

try:
    METER
except NameError:
    METER = "A1"
try:
    PELLET_D
except NameError:
    PELLET_D = 23.8
try:
    FEED_BENCH_LIBRARY
except NameError:
    FEED_BENCH_LIBRARY = False

OUT_DIR = os.path.join(REPO, "exports", "gatling_feed_bench")
NAME = "gatling_feed_bench"

# ---------------------------------------------------------------- station gutter (library)
_lib = {"REPO": REPO, "GATLING_LINEAR_BREECH_LIBRARY": True, "SHOW_OPEN": False}
exec(open(os.path.join(REPO, "gatling", "linear_breech.py")).read(), _lib)
front_cover_feed = _lib["front_cover_feed"]
z_tip = _lib["z_tip"]
FIT_INSERT = _lib["FIT_INSERT"]
STROKE = _lib["STROKE"]
LIB_PELLET = _lib["PELLET_D"]
del _lib

PACK_R = 66.0
N_STATION = 6
# Station 0 sits under the hopper. phi 180 is +X (up); phi 90 is +Y (crank).
STATION_PHI = [180.0 + i * (360.0 / N_STATION) for i in range(N_STATION)]
Z_BALL = z_tip + LIB_PELLET / 2.0          # pellet centre in the library gutter

# 6000: 10 x 26 x 8. Shaft is the Ø10 the bearing is made for.
SHAFT_D = 10.0
BRG_OD, BRG_W = 26.0, 8.0
BRG_BORE = SHAFT_D + 0.3                    # drawing gap so the fit is not a boolean clash
HOUSE_BORE = BRG_OD + 0.3

GUARD_PHI0 = 170.0                          # a little before the drop at 180
GUARD_GAP = 1.5                             # pellet surface to guard inner face
GUARD_WALL = 3.2
GUARD_HZ = 26.0                             # half-height of the shell, along Z
PORT_HY, PORT_HZ = 20.0, 17.0               # feed window at phi 180

# Auger, from the hopper plan (start numbers, not a freeze).
AUG_PITCH = 30.0
AUG_THICK = 3.0                             # gate thickness along the tube
AUG_WIDTH = 22.0                            # diametral bar; side gap (28-22)/2 = 3
AUG_TUBE_ID = 28.0
AUG_TUBE_OD = 34.0
AUG_POCKET = AUG_PITCH - AUG_THICK          # 27 mm: one ball, not two
AUG_TURNS = 3                               # working turns in the tube
AUG_TAIL = 1                                # one more turn stirring the cup
SPUR_M = 1.5
BEVEL_M, BEVEL_Z, BEVEL_FACE = 2.0, 20, 8.0

# Star (A2) and escapement (A4).
STAR_POCKET_D = PELLET_D + 1.2              # one ball, not two across
STAR_POCKET_L = PELLET_D + 1.0              # axial length of the cavity
LIP_T = 1.4                                 # TPU wiper
ESC_TUBE_ID = PELLET_D + 3.0                # 26.8: one across, not two
ESC_GAP = PELLET_D + 1.2                    # clear distance between the fingers
CAM_LOBES = 6

# Cup. Void is checked against 30..50 balls at sphere packing 0.55 and 0.64.
CUP_ID = 92.0
CUP_WALL = 3.5
CUP_H = 76.0
CUP_FLOOR = 4.0
PACK_LO, PACK_HI = 0.55, 0.64

X = App.Vector(1, 0, 0)
Y = App.Vector(0, 1, 0)
Z = App.Vector(0, 0, 1)
V = App.Vector
O = V(0, 0, 0)


def polar(phi, radius, z=0.0):
    """Point at pack angle phi (180 = +X up, 90 = +Y)."""
    a = math.radians(phi)
    return V(-radius * math.cos(a), radius * math.sin(a), z)


def chute_matrix(phi):
    """Map the station frame onto pack angle phi. Local +Y is radial out, +Z is the barrel."""
    a = math.radians(phi)
    c, s = math.cos(a), math.sin(a)
    return App.Matrix(s, -c, 0, -PACK_R * c,
                      c, s, 0, PACK_R * s,
                      0, 0, 1, 0,
                      0, 0, 0, 1)


def place_chute(phi):
    return front_cover_feed.transformGeometry(chute_matrix(phi))


def spur_x(teeth, module, face, bore, phase_deg=0.0):
    """Spur gear, axis along +X, tooth at phase_deg, centred on the origin."""
    outline = GR.tooth_outline(teeth, module, 1.0, 0.40)
    pts = [V(x, y, -face / 2.0) for x, y in outline]
    pts.append(pts[0])
    g = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, face))
    g = g.cut(Part.makeCylinder(bore / 2.0, face + 4.0, V(0, 0, -face / 2.0 - 2.0)))
    if phase_deg:
        g.rotate(O, Z, phase_deg)
    g.rotate(O, Y, 90)
    return g


def tube_x(od, idd, x0, x1, y=0.0, z=0.0):
    h = x1 - x0
    outer = Part.makeCylinder(od / 2.0, h, V(x0, y, z), X)
    inner = Part.makeCylinder(idd / 2.0, h + 4.0, V(x0 - 2.0, y, z), X)
    return outer.cut(inner)


def open_fraction(phi):
    """Breech open fraction, cosine ramps. 0 closed, 1 fully open."""
    p = phi % 360.0
    if 30.0 <= p < 120.0:
        u = (p - 30.0) / 90.0
        return 0.5 * (1.0 - math.cos(math.pi * u))
    if 120.0 <= p < 240.0:
        return 1.0
    if 240.0 <= p < 330.0:
        u = (p - 240.0) / 90.0
        return 0.5 * (1.0 + math.cos(math.pi * u))
    return 0.0


def tip_insertion(phi):
    """Millimetres the fitting tip is inside the bore. Negative: still behind the face."""
    return FIT_INSERT - open_fraction(phi) * STROKE


def close_capture_phi(depth):
    """First close angle at which the tip has entered the bore by `depth` mm."""
    phi = 240.0
    while phi < 330.0 and tip_insertion(phi) < depth:
        phi += 0.05
    return phi


# Guard ends when the tip is half a pellet inside the bore (the bore and the
# nose together cage the ball). That is the close point for the kicker too.
GUARD_PHI1 = close_capture_phi(PELLET_D / 2.0)
DUMP_PHI = GUARD_PHI1 + 6.0

# ---------------------------------------------------------------- six chutes, disk, shaft
chutes = [place_chute(phi) for phi in STATION_PHI]
cover_bb = chutes[0].BoundBox
# All six are the same shape; the top one sets the radial envelope.
X_COVER_MAX = max(c.BoundBox.XMax for c in chutes)
Z_COVER_MIN = min(c.BoundBox.ZMin for c in chutes)
Z_COVER_MAX = max(c.BoundBox.ZMax for c in chutes)

# Disk plane first. The bevel has to finish aft of the front bearing, and the
# spur stack has to reach from that layshaft up to the auger at Z_BALL.
DISK_R = PACK_R + 40.0
DISK_T = 8.0
z_disk1 = Z_COVER_MIN - 1.2
z_disk0 = z_disk1 - DISK_T
z_brg_f1 = z_disk0 - 3.0
z_brg_f0 = z_brg_f1 - BRG_W

# Bevel 1:1, 45 deg. Apex at the origin of the gear, teeth toward +Z, hub
# behind the big end. Reach is apex -> back of the hub.
_delta = math.radians(45.0)
_Re = (BEVEL_M * BEVEL_Z) / (2.0 * math.sin(_delta))
BEVEL_AE = _Re * math.cos(_delta)
BEVEL_HUB_L = 18.0
BEVEL_REACH = BEVEL_AE + BEVEL_HUB_L

# Compound spur, 2 x 3 = 6. One 6:1 pair across this span is a ~240 mm wheel.
S1_PIN, S1_WHEEL = 32, 64                       # layshaft -> mid shaft
S2_PIN, S2_WHEEL = 28, 84                       # mid shaft -> auger
CD1 = SPUR_M * (S1_PIN + S1_WHEEL) / 2.0
CD2 = SPUR_M * (S2_PIN + S2_WHEEL) / 2.0
SPUR_RATIO = (S1_WHEEL / float(S1_PIN)) * (S2_WHEEL / float(S2_PIN))
z_apex = Z_BALL - (CD1 + CD2)
Z_LAY = z_apex
Z_MID = Z_LAY + CD1

# Outlet just past the cover, then three pitches of tube. The seat is the
# top of that tube. The cup stands on the seat; the pinion is past the cup
# so the shaft that drives the screw never crosses a working pocket.
X_LIP = PACK_R + PELLET_D / 2.0 + 2.2
X_TUBE0 = X_LIP + PELLET_D + 10.0               # one ball fits in the throat
X_TUBE1 = X_TUBE0 + AUG_TURNS * AUG_PITCH
X_SEAT = X_TUBE1
RING_T = 8.0
X_CUP_END = X_SEAT + RING_T + 0.15 + CUP_FLOOR + CUP_H
PIN_TIP = SPUR_M * (S2_PIN + 2) / 2.0
X_MESH2 = X_CUP_END + PIN_TIP + 6.0             # auger pinion, past the cup
X_MESH = X_MESH2 - 14.0                         # first stage beside it
GUIDE_LEN = X_TUBE0 - X_LIP

# Rear bearing and crank aft of the bevel apex (the teeth are all on +Z).
z_brg_r1 = z_apex - 12.0
z_brg_r0 = z_brg_r1 - BRG_W
z_crank0 = z_brg_r0 - 14.0

disk = Part.makeCylinder(DISK_R, DISK_T, V(0, 0, z_disk0))
# Boss on the muzzle face. The aft face stays clear of the front bearing.
hub = Part.makeCylinder(16.0, 6.0, V(0, 0, z_disk1 - 2.0))
disk = disk.fuse(hub)
disk = disk.cut(Part.makeCylinder(SHAFT_D / 2.0 + 0.15, 80.0, V(0, 0, z_brg_f0 - 2.0)))
# Six pads the chutes sit on (0.4 mm shy of the cover, so the print is a separate part).
for phi in STATION_PHI:
    c = polar(phi, PACK_R, 0.0)
    pad = Part.makeCylinder(16.0, 4.0, V(c.x, c.y, z_disk1 - 0.4))
    disk = disk.fuse(pad)
disk = disk.removeSplitter()

shaft = Part.makeCylinder(SHAFT_D / 2.0, z_disk1 - z_crank0 + 6.0, V(0, 0, z_crank0 - 4.0))


def bearing_at(z0):
    return Part.makeCylinder(BRG_OD / 2.0, BRG_W, V(0, 0, z0)).cut(
        Part.makeCylinder(BRG_BORE / 2.0, BRG_W + 2.0, V(0, 0, z0 - 1.0)))


brg_front = bearing_at(z_brg_f0)
brg_rear = bearing_at(z_brg_r0)

# Housings from the base up around each bearing. Base is below the lowest chute.
BASE_TOP = -(PACK_R + 36.0)
BASE_T = 10.0
base = Part.makeBox(360.0, 280.0, BASE_T, V(-180.0, -140.0, 0.0))
# The base lies in the machine XY? No: down is -X, the shaft is along Z.
# Rebuild the base as a plate normal to X, under the pack.
base = Part.makeBox(BASE_T, 300.0, z_disk1 - z_crank0 + 30.0,
                    V(BASE_TOP - BASE_T, -150.0, z_crank0 - 20.0))


def housing(z0):
    """Pillow block: feet on the base, bore on the shaft."""
    # Stop 1 mm short of the disk (disk starts 11 mm above z_brg_f0). The
    # same block on the rear bearing is clear of everything either way.
    block = Part.makeBox(28.0, 44.0, BRG_W + 5.0,
                         V(-14.0, -22.0, z0 - 4.0))
    body = Part.makeBox(14.0 - BASE_TOP, 44.0, BRG_W + 5.0,
                        V(BASE_TOP, -22.0, z0 - 4.0))
    body = body.fuse(block)
    body = body.cut(Part.makeCylinder(HOUSE_BORE / 2.0, BRG_W + 14.0, V(0, 0, z0 - 7.0)))
    # Two M5 holes in the ears, along X, so it bolts to the base.
    for sy in (-16.0, 16.0):
        body = body.cut(Part.makeCylinder(2.7, 30.0, V(BASE_TOP - 2.0, sy, z0 + BRG_W / 2.0), X))
    return body.removeSplitter()


house_front = housing(z_brg_f0)
house_rear = housing(z_brg_r0)

# Crank at phi 90 (+Y), aft of the rear bearing.
CRANK_R = 100.0
crank_hub = Part.makeCylinder(14.0, 12.0, V(0, 0, z_crank0))
crank_hub = crank_hub.cut(Part.makeCylinder(SHAFT_D / 2.0 + 0.15, 16.0, V(0, 0, z_crank0 - 2.0)))
arm = Part.makeBox(14.0, CRANK_R, 8.0, V(-7.0, 6.0, z_crank0 + 2.0))
knob = Part.makeCylinder(11.0, 28.0, V(0, CRANK_R, z_crank0 - 8.0))
crank = crank_hub.fuse(arm).fuse(knob).removeSplitter()

# ---------------------------------------------------------------- guard
GUARD_R_IN = PACK_R + PELLET_D / 2.0 + GUARD_GAP
GUARD_R_OUT = GUARD_R_IN + GUARD_WALL


def pie(radius, phi0, phi1, z0, z1, n=72):
    pts = [V(0, 0, z0)]
    for i in range(n + 1):
        phi = phi0 + (phi1 - phi0) * i / float(n)
        p = polar(phi, radius, z0)
        pts.append(p)
    pts.append(V(0, 0, z0))
    face = Part.Face(Part.makePolygon(pts))
    return face.extrude(V(0, 0, z1 - z0))


guard = pie(GUARD_R_OUT, GUARD_PHI0, GUARD_PHI1, Z_BALL - GUARD_HZ, Z_BALL + GUARD_HZ)
guard = guard.cut(pie(GUARD_R_IN, GUARD_PHI0 - 1.0, GUARD_PHI1 + 1.0,
                      Z_BALL - GUARD_HZ - 2.0, Z_BALL + GUARD_HZ + 2.0))
# Feed window on the +X axis so the meter reaches the chute. The shell still
# starts at 170 deg above and below the window.
port = Part.makeBox(40.0, 2 * PORT_HY, 2 * PORT_HZ,
                    V(GUARD_R_IN - 4.0, -PORT_HY, Z_BALL - PORT_HZ))
guard = guard.cut(port).removeSplitter()

# ---------------------------------------------------------------- seat ring, two posts, cup
# The ring is the one seat. Posts stand either side of the pack and a yoke
# grips the ring; nothing spikes through the bore.
RING_OD = 88.0
RING_ID = 44.0
BOLT_PCD = 70.0
BOLT_D = 4.4
POST_Y = 155.0


def bolt_centers():
    pts = []
    for i in range(3):
        a = math.radians(90.0 + i * 120.0)     # one bolt on +Z so the pattern is stable
        pts.append(( (BOLT_PCD / 2.0) * math.cos(a),
                     Z_BALL + (BOLT_PCD / 2.0) * math.sin(a)))
    return pts


ring = tube_x(RING_OD, RING_ID, X_SEAT, X_SEAT + RING_T, 0.0, Z_BALL)
for by, bz in bolt_centers():
    ring = ring.cut(Part.makeCylinder(BOLT_D / 2.0, RING_T + 4.0,
                                      V(X_SEAT - 2.0, by, bz), X))
ring = ring.removeSplitter()

posts = []
yoke = []
for sy in (-1.0, 1.0):
    # Post from the base up to the seat, outside the swept chutes.
    post = Part.makeBox(X_SEAT + RING_T - BASE_TOP, 16.0, 16.0,
                        V(BASE_TOP, sy * POST_Y - 8.0, Z_BALL - 8.0))
    posts.append(post)
    # Arm from the post to the ring OD, not across the bore.
    y_near = sy * (RING_OD / 2.0 - 1.0)
    y0, y1 = (y_near, sy * POST_Y) if sy > 0 else (sy * POST_Y, y_near)
    arm = Part.makeBox(RING_T, y1 - y0, 14.0,
                       V(X_SEAT, y0, Z_BALL - 7.0))
    yoke.append(arm)
frame_top = ring
for p in posts + yoke:
    frame_top = frame_top.fuse(p)
frame_top = frame_top.removeSplitter()

# 0.15 mm shoulder gap so the cup rests on the ring without a boolean clash.
_cup0 = X_SEAT + RING_T + 0.15
cup_outer = Part.makeCylinder(CUP_ID / 2.0 + CUP_WALL, CUP_H + CUP_FLOOR,
                              V(_cup0, 0, Z_BALL), X)
cup_void_shape = Part.makeCylinder(CUP_ID / 2.0, CUP_H + 2.0,
                                   V(_cup0 + CUP_FLOOR, 0, Z_BALL), X)
# Throat through the floor into the seat bore. Steep cup, no funnel.
throat = Part.makeCylinder(RING_ID / 2.0 - 1.0, CUP_FLOOR + 4.0,
                           V(_cup0 - 2.0, 0, Z_BALL), X)
cup = cup_outer.cut(cup_void_shape).cut(throat)
# Spigot into the ring, 0.25 mm radial clearance.
spigot = Part.makeCylinder((RING_ID - 0.5) / 2.0, 5.0,
                           V(_cup0 - 5.0, 0, Z_BALL), X)
spigot = spigot.cut(Part.makeCylinder(RING_ID / 2.0 - 1.0, 8.0,
                                      V(_cup0 - 6.0, 0, Z_BALL), X))
cup = cup.fuse(spigot).removeSplitter()
CUP_VOID = math.pi * (CUP_ID / 2.0) ** 2 * CUP_H
BALL_VOL = 4.0 / 3.0 * math.pi * (PELLET_D / 2.0) ** 3

# ---------------------------------------------------------------- meters
meter_parts = []          # mounted solids
pocket_solid = None       # solid the pocket probe is cut from
pocket_center = None
pocket_axis = X           # direction of the second ball that must NOT fit
pocket_radial = Y
meter_note = ""
deliveries = 0
ratio_txt = ""
gear_pairs = []           # (a, b) that must mesh without overlap


def flange_at(x_face):
    """Bolt flange just under the seat, same three holes."""
    fl = Part.makeCylinder(RING_OD / 2.0, 6.0, V(x_face - 6.2, 0, Z_BALL), X)
    fl = fl.cut(Part.makeCylinder(AUG_TUBE_OD / 2.0 + 0.4, 10.0, V(x_face - 8.0, 0, Z_BALL), X))
    for by, bz in bolt_centers():
        fl = fl.cut(Part.makeCylinder(BOLT_D / 2.0, 10.0, V(x_face - 8.0, by, bz), X))
    return fl


if METER == "A1":
    # Gates every pitch, 22 mm across, plus a peripheral rib so the screw is
    # one piece. Local frame: +Z along the tube toward the hopper, origin at
    # the outlet gate. A spoke at each gate joins the 22 mm bar to the rib;
    # the rib itself stays outside the ball (r 13 > 11.9).
    def _gate(z_c):
        bar = Part.makeBox(AUG_WIDTH, AUG_THICK, AUG_THICK,
                           V(-AUG_WIDTH / 2.0, -AUG_THICK / 2.0, z_c - AUG_THICK / 2.0))
        spoke = Part.makeBox(4.2, AUG_THICK, AUG_THICK,
                             V(AUG_WIDTH / 2.0 - 1.2, -AUG_THICK / 2.0, z_c - AUG_THICK / 2.0))
        return bar.fuse(spoke)

    def _rib(z0, z1):
        # Left-hand about local +Z. Right-hand rotation about +Z (which is
        # +X toward the hopper) then drives a pellet toward -Z, the outlet.
        wires = []
        n = 16
        r_rib = 13.0
        for i in range(n + 1):
            u = i / float(n)
            th = -2.0 * math.pi * u
            z = z0 + (z1 - z0) * u
            c, s = math.cos(th), math.sin(th)
            pts = []
            for dr, dz in ((-0.7, -0.9), (0.7, -0.9), (0.7, 0.9), (-0.7, 0.9), (-0.7, -0.9)):
                pts.append(V((r_rib + dr) * c, (r_rib + dr) * s, z + dz))
            wires.append(Part.makePolygon(pts))
        return Part.makeLoft(wires, True)

    bits = []
    n_gates = AUG_TURNS + AUG_TAIL + 1
    for k in range(n_gates):
        bits.append(_gate(k * AUG_PITCH))
    for k in range(n_gates - 1):
        bits.append(_rib(k * AUG_PITCH + AUG_THICK / 2.0 - 1.0,
                         (k + 1) * AUG_PITCH - AUG_THICK / 2.0 + 1.0))
    screw_local = bits[0]
    for b in bits[1:]:
        screw_local = screw_local.fuse(b)
    screw_local = screw_local.removeSplitter()
    # Local +Z -> world +X. First gate is the outlet wall.
    screw_m = App.Matrix(0, 0, 1, X_TUBE0,
                         0, 1, 0, 0,
                         -1, 0, 0, Z_BALL,
                         0, 0, 0, 1)
    screw = screw_local.transformGeometry(screw_m)
    auger_tube = tube_x(AUG_TUBE_OD, AUG_TUBE_ID, X_TUBE0, X_TUBE1, 0.0, Z_BALL)
    guide = tube_x(AUG_TUBE_ID + 4.4, AUG_TUBE_ID, X_LIP, X_TUBE0 + 2.0, 0.0, Z_BALL)
    guide = guide.cut(Part.makeBox(GUIDE_LEN + 6.0, AUG_TUBE_ID, 20.0,
                                  V(X_LIP - 2.0, -AUG_TUBE_ID / 2.0, Z_BALL + 2.0)))
    fl = flange_at(X_SEAT)
    # Shaft from the last gate (in the cup) out through the open top to the
    # pinion. It does not enter the working pockets or the outlet throat.
    x_last = X_TUBE0 + (n_gates - 1) * AUG_PITCH
    stub = Part.makeCylinder(4.0, X_MESH2 + 6.0 - (x_last - 2.0),
                             V(x_last - 2.0, 0, Z_BALL), X)
    g_s1w = spur_x(S1_WHEEL, SPUR_M, 8.0, 8.4, 0.0)
    g_s1w.translate(V(X_MESH, 0, Z_LAY))
    g_s1p = spur_x(S1_PIN, SPUR_M, 8.0, 8.4, 180.0 / S1_PIN)
    g_s1p.translate(V(X_MESH, 0, Z_MID))
    g_s2w = spur_x(S2_WHEEL, SPUR_M, 8.0, 8.4, 0.0)
    g_s2w.translate(V(X_MESH2, 0, Z_MID))
    g_s2p = spur_x(S2_PIN, SPUR_M, 8.0, 8.4, 180.0 / S2_PIN)
    g_s2p.translate(V(X_MESH2, 0, Z_BALL))
    lay = Part.makeCylinder(4.0, X_MESH + 6.0 - 40.0, V(40.0, 0, Z_LAY), X)
    mid = Part.makeCylinder(4.0, X_MESH2 - X_MESH + 12.0, V(X_MESH - 6.0, 0, Z_MID), X)
    g_pack, _bv = GR.bevel_gear(BEVEL_M, BEVEL_Z, BEVEL_FACE, 18.0, BEVEL_HUB_L, SHAFT_D + 0.4,
                                backlash=0.30, phase_deg=0.0)
    g_lay, _bv2 = GR.bevel_gear(BEVEL_M, BEVEL_Z, BEVEL_FACE, 16.0, 12.0, 8.4,
                                backlash=0.30, phase_deg=180.0 / BEVEL_Z)
    g_lay.rotate(O, Y, 90)
    g_pack.translate(V(0, 0, z_apex))
    g_lay.translate(V(0, 0, z_apex))
    meter_parts = [screw, auger_tube, guide, fl, stub, g_s1w, g_s1p, g_s2w, g_s2p,
                   lay, mid, g_pack, g_lay]
    gear_pairs = [(g_s1w, g_s1p), (g_s2w, g_s2p), (g_pack, g_lay)]
    pocket_center = screw_m.multiply(V(0, 0, AUG_PITCH / 2.0))
    pocket_solid = screw.fuse(auger_tube)
    pocket_axis = X
    pocket_radial = Y
    deliveries = int(round((BEVEL_Z / float(BEVEL_Z)) * SPUR_RATIO))
    ratio_txt = "bevel %d/%d (1:1) x spur %d/%d x %d/%d = %.0f" % (
        BEVEL_Z, BEVEL_Z, S1_WHEEL, S1_PIN, S2_WHEEL, S2_PIN, SPUR_RATIO)
    meter_note = "A1 auger, tube ID %.0f, pitch %.0f, pocket %.0f, %d turns + %d in the cup" % (
        AUG_TUBE_ID, AUG_PITCH, AUG_POCKET, AUG_TURNS, AUG_TAIL)
    check_screw_solids = len(screw.Solids)

elif METER == "A2":
    # Star axis parallel to the pack shaft. Ø80, just outside the guard.
    # 2:1 spur, three pockets. Fill and discharge are 120 deg apart, so the
    # cup feeds the pocket at 60 deg and the chute takes the one at 180.
    m_star = 2.0
    STAR_R = 40.0
    # CD = m*(z + 2z)/2 = 3*z for m = 2. Snap up so the rim clears the guard.
    STAR_PIN = max(18, int(math.ceil((GUARD_R_OUT + 3.0 + STAR_R) / 3.0)))
    STAR_WHEEL = 2 * STAR_PIN
    X_STAR = m_star * (STAR_PIN + STAR_WHEEL) / 2.0
    pocket_r = STAR_R - PELLET_D / 2.0 + 2.2
    star_len = STAR_POCKET_L + 6.0
    star = Part.makeCylinder(STAR_R, star_len, V(X_STAR, 0, Z_BALL - star_len / 2.0))
    star = star.cut(Part.makeCylinder(4.4, star_len + 4.0,
                                      V(X_STAR, 0, Z_BALL - star_len / 2.0 - 2.0)))
    for k in range(3):
        ang = math.radians(180.0 + k * 120.0)
        px = X_STAR + pocket_r * math.cos(ang)
        py = pocket_r * math.sin(ang)
        hole = Part.makeCylinder(STAR_POCKET_D / 2.0, STAR_POCKET_L,
                                 V(px, py, Z_BALL - STAR_POCKET_L / 2.0))
        star = star.cut(hole)
    star = star.removeSplitter()
    pocket_center = V(X_STAR - pocket_r, 0.0, Z_BALL)
    pocket_solid = star
    pocket_axis = Z
    pocket_radial = Y
    # TPU lip just outside the rim, over the fill pocket.
    lip = Part.makeBox(LIP_T, 16.0, STAR_POCKET_L - 1.0,
                       V(STAR_R + 0.5, -8.0, -(STAR_POCKET_L - 1.0) / 2.0))
    lip.translate(V(X_STAR, 0, Z_BALL))
    lip.rotate(V(X_STAR, 0, Z_BALL), Z, 18.0)

    def spur_z(teeth, module, face, bore, phase_deg=0.0):
        outline = GR.tooth_outline(teeth, module, 1.0, 0.40)
        pts = [V(x, y, 0) for x, y in outline]
        pts.append(pts[0])
        g = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, face))
        g = g.cut(Part.makeCylinder(bore / 2.0, face + 4.0, V(0, 0, -2.0)))
        if phase_deg:
            g.rotate(O, Z, phase_deg)
        return g

    # Gears aft of the front bearing. Shafts along Z.
    z_gear = z_brg_f0 - 12.0
    g_pack = spur_z(STAR_WHEEL, m_star, 8.0, SHAFT_D + 0.4, 0.0)
    g_pack.translate(V(0, 0, z_gear))
    g_star = spur_z(STAR_PIN, m_star, 8.0, 8.4, 180.0 / STAR_PIN)
    g_star.translate(V(X_STAR, 0, z_gear))
    star_shaft = Part.makeCylinder(4.0, (Z_BALL - star_len / 2.0) - (z_gear + 7.0),
                                  V(X_STAR, 0, z_gear + 7.0))
    funnel = tube_x(ESC_TUBE_ID + 6.0, ESC_TUBE_ID, X_LIP, X_STAR - STAR_R + 1.5, 0.0, Z_BALL)
    fl = flange_at(X_SEAT)
    # Port on the fill pocket, then a trough back to the ring. The bore of
    # the ring stays the cup's throat; this neck joins it from the side.
    fill = math.radians(60.0)
    port_dir = V(math.cos(fill), math.sin(fill), 0)
    port = Part.makeCylinder(14.0, 18.0, V(X_STAR, 0, Z_BALL) + port_dir * (STAR_R + 0.8), port_dir)
    port = port.cut(Part.makeCylinder(11.5, 22.0,
                                      V(X_STAR, 0, Z_BALL) + port_dir * (STAR_R - 1.0), port_dir))
    y_port = (STAR_R + 18.0) * math.sin(fill)
    x_port = X_STAR + (STAR_R + 18.0) * math.cos(fill)
    trough = tube_x(28.0, 23.0, x_port, X_SEAT - 4.0, y_port, Z_BALL)
    span = max(4.0, y_port - 6.0)
    cross = Part.makeCylinder(14.0, span, V(X_SEAT - 4.0, 6.0, Z_BALL), Y)
    cross = cross.cut(Part.makeCylinder(11.5, span + 4.0, V(X_SEAT - 4.0, 4.0, Z_BALL), Y))
    # Arm from the seat to a pad over the star shaft, off to +Y so the
    # fill port stays open. Same three bolts, via the flange.
    arm_len = X_SEAT - (X_STAR + 8.0)
    bridge = Part.makeBox(arm_len, 12.0, 10.0,
                          V(X_STAR + 8.0, 16.0, Z_BALL + star_len / 2.0 + 1.0))
    meter_parts = [star, lip, g_pack, g_star, star_shaft, funnel, fl, port, trough, cross, bridge]
    gear_pairs = [(g_pack, g_star)]
    deliveries = int(round((STAR_WHEEL / float(STAR_PIN)) * 3))
    ratio_txt = "spur %d/%d = %.0f:1, 3 pockets, %d drops/rev" % (
        STAR_WHEEL, STAR_PIN, STAR_WHEEL / float(STAR_PIN), deliveries)
    meter_note = "A2 star R %.1f at x %.1f, pocket Ø%.1f x %.1f, TPU lip %.1f mm" % (
        STAR_R, X_STAR, STAR_POCKET_D, STAR_POCKET_L, LIP_T)

elif METER == "A4":
    # Two fingers, gap = one ball. The picture shows the release pose (lower
    # finger out). The pocket gauge pushes the lower finger in.
    esc_od = ESC_TUBE_ID + 5.0
    finger_w, finger_t = 16.0, 4.0
    x_lower0 = X_LIP + 8.0
    x_lower1 = x_lower0 + finger_t
    x_upper = x_lower1 + ESC_GAP
    queue = tube_x(esc_od, ESC_TUBE_ID, X_LIP, X_SEAT, 0.0, Z_BALL)

    def slot(x0):
        return Part.makeBox(finger_t + 0.8, 72.0, finger_w + 0.8,
                            V(x0 - 0.4, -22.0, Z_BALL - (finger_w + 0.8) / 2.0))

    queue = queue.cut(slot(x_lower0)).cut(slot(x_upper)).removeSplitter()

    def finger(x0, y0, y1):
        return Part.makeBox(finger_t, y1 - y0, finger_w, V(x0, y0, Z_BALL - finger_w / 2.0))

    upper = finger(x_upper, -16.0, 8.0)
    lower_in = finger(x_lower0, -16.0, 8.0)
    lower_out = finger(x_lower0, 30.0, 48.0)
    pocket_solid = queue.fuse(upper).fuse(lower_in)
    pocket_center = V((x_lower1 + x_upper) / 2.0, 0.0, Z_BALL)
    pocket_axis = X
    pocket_radial = Y
    # Six-lobe cam aft of the disk and of the hub. A lobe faces +X when a
    # station is at 180, which is when that station is under the hopper.
    CAM_R = 34.0
    CAM_T = 8.0
    z_cam1 = z_disk0 - 7.0
    z_cam0 = z_cam1 - CAM_T
    cam = Part.makeCylinder(CAM_R, CAM_T, V(0, 0, z_cam0))
    cam = cam.cut(Part.makeCylinder(6.5, CAM_T + 4.0, V(0, 0, z_cam0 - 2.0)))
    for i in range(CAM_LOBES):
        phi = 180.0 + i * (360.0 / CAM_LOBES)
        c = polar(phi, CAM_R - 2.0, z_cam0)
        cam = cam.fuse(Part.makeCylinder(6.5, CAM_T, V(c.x, c.y, z_cam0)))
    cam = cam.removeSplitter()
    lobe_peak = CAM_R - 2.0 + 6.5
    follow = Part.makeCylinder(4.5, 10.0, V(lobe_peak + 6.0, 0, z_cam0 - 1.0))
    # Link runs under the disk, rises outside the posts, comes back past the cover.
    y_out = 128.0
    x_in = X_LIP + 36.0
    x_rod = lobe_peak + 2.0
    rod1 = Part.makeBox(8.0, y_out, 8.0, V(x_rod, 0.0, z_cam0))
    rod2 = Part.makeBox(8.0, 8.0, Z_BALL - z_cam0, V(x_rod, y_out - 8.0, z_cam0))
    rod3 = Part.makeBox(x_in - x_rod, 8.0, 8.0, V(x_rod, y_out - 8.0, Z_BALL - 4.0))
    rod4 = Part.makeBox(8.0, y_out - 20.0, 8.0, V(x_in, 12.0, Z_BALL - 4.0))
    fl = flange_at(X_SEAT)
    meter_parts = [queue, upper, lower_out, cam, follow, rod1, rod2, rod3, rod4, fl]
    deliveries = CAM_LOBES
    ratio_txt = "cam %d lobes on the disk, 1:1, %d drops/rev" % (CAM_LOBES, CAM_LOBES)
    meter_note = "A4 escapement, tube ID %.1f, finger gap %.1f, %d-lobe cam" % (
        ESC_TUBE_ID, ESC_GAP, CAM_LOBES)
else:
    raise SystemExit("METER must be A1, A2 or A4, got %r" % (METER,))

# ---------------------------------------------------------------- kicker and tray at the close angle
# Local station frame: +Y radial out, +X toward increasing phi, +Z barrel.
# The gutter metal is at local Y <= -2, so a blade in +Y only meets the pellet.
dump_m = chute_matrix(DUMP_PHI)
kicker_local = Part.makeBox(8.0, 16.0, 12.0, V(-4.0, PELLET_D / 2.0 - 8.0, Z_BALL - 6.0))
# Ramp outward into the tray.
ramp_local = Part.makeBox(10.0, 22.0, 14.0, V(2.0, PELLET_D / 2.0 - 2.0, Z_BALL - 7.0))
kicker = kicker_local.fuse(ramp_local).transformGeometry(dump_m)
# Tray ahead of the dump, open toward the station (local -X face missing).
tray_local = Part.makeBox(28.0, 24.0, 18.0, V(8.0, PELLET_D / 2.0 + 4.0, Z_BALL - 16.0))
tray_local = tray_local.cut(Part.makeBox(22.0, 18.0, 14.0,
                                        V(8.0, PELLET_D / 2.0 + 7.0, Z_BALL - 14.0)))
# Leg down to the base. Local -Y is toward the pack; down in the machine is -X,
# which is not one local axis at this phi, so the leg is added in world axes.
tray = tray_local.transformGeometry(dump_m)
tray_bb = tray.BoundBox
leg = Part.makeBox(tray_bb.XMin - BASE_TOP, 8.0, 8.0,
                   V(BASE_TOP, (tray_bb.YMin + tray_bb.YMax) / 2.0 - 4.0,
                     (tray_bb.ZMin + tray_bb.ZMax) / 2.0 - 4.0))
tray = tray.fuse(leg).removeSplitter()

# Reference pellets (not part of the print, not part of the clearance checks).
pellet_drop = Part.makeSphere(PELLET_D / 2.0, polar(180.0, PACK_R, Z_BALL))
pellet_held = Part.makeSphere(PELLET_D / 2.0, polar(240.0, PACK_R, Z_BALL))
pellet_pocket = Part.makeSphere(PELLET_D / 2.0, pocket_center)

# ---------------------------------------------------------------- checks
def ang_phi(v):
    return math.degrees(math.atan2(v.y, -v.x)) % 360.0


def near(a, b, tol=0.5):
    return abs(a - b) <= tol


checks = []


def check(ok, text):
    checks.append((text, bool(ok)))


# Six chutes on R 66, 60 deg apart, gutter axis inside the solid.
radii = []
phis = []
for phi in STATION_PHI:
    p = chute_matrix(phi).multiply(V(0, 0, Z_BALL))
    radii.append(math.hypot(p.x, p.y))
    phis.append(ang_phi(p))
check(all(abs(r - PACK_R) < 0.05 for r in radii),
      "6 chutes on R %.1f (spread %.3f mm)" % (PACK_R, max(radii) - min(radii)))
sep = sorted((phis[i] - phis[0]) % 360.0 for i in range(N_STATION))
check(all(abs(sep[i] - i * 60.0) < 0.2 for i in range(N_STATION)),
      "chute step 60 deg (%s)" % ", ".join("%.1f" % s for s in sep))
# The bore is empty; the wall under the pellet (local y = -10) is the gutter metal.
check(all(chutes[i].isInside(chute_matrix(STATION_PHI[i]).multiply(V(0, -10.0, Z_BALL)),
                             0.3, True) for i in range(N_STATION)),
      "gutter wall under the pellet lies inside each chute")

# Motion-law guard.
ins_end = tip_insertion(GUARD_PHI1)
check(GUARD_PHI0 == 170.0 and 280.0 < GUARD_PHI1 < 320.0 and abs(ins_end - PELLET_D / 2.0) < 0.15,
      "guard %.1f..%.1f deg, tip insertion at the end %.2f mm (half pellet %.2f)"
      % (GUARD_PHI0, GUARD_PHI1, ins_end, PELLET_D / 2.0))
shell_r = (GUARD_R_IN + GUARD_R_OUT) / 2.0
check(guard.isInside(polar(220.0, shell_r, Z_BALL), 0.2, True)
      and guard.isInside(polar(260.0, shell_r, Z_BALL), 0.2, True)
      and not guard.isInside(polar(150.0, shell_r, Z_BALL), 0.2, True)
      and not guard.isInside(polar(GUARD_PHI1 + 4.0, shell_r, Z_BALL), 0.2, True),
      "guard shell covers 220 and 260, open before 170 and past the close angle")
check(not guard.isInside(polar(180.0, shell_r, Z_BALL), 0.2, True)
      and guard.isInside(polar(180.0, shell_r, Z_BALL + PORT_HZ + 4.0), 0.2, True),
      "feed window at 180 deg, shell continues above it (guard still starts at 170)")
ball_240 = Part.makeSphere(PELLET_D / 2.0, polar(240.0, PACK_R, Z_BALL))
guard_gap = guard.distToShape(ball_240)[0]
check(1.0 <= guard_gap <= 2.0,
      "guard gap at 240 deg %.2f mm (want 1..2)" % guard_gap)

# Deliveries: six per turn, the one under the hopper centred at 180 +/- 10.
mids = sorted((180.0 + i * (360.0 / deliveries)) % 360.0 for i in range(deliveries))
def ang_dist(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)
check(deliveries == 6,
      "6 drops per pack turn (%d), %s" % (deliveries, ratio_txt))
check(any(ang_dist(m, 180.0) <= 10.0 for m in mids),
      "a drop midpoint within 180 +/- 10 deg (%s)" % ", ".join("%.1f" % m for m in mids))

# Pocket: one ball clear, a second along the pocket axis and a side-by-side both hit metal.
one = Part.makeSphere(PELLET_D / 2.0, pocket_center)
two_ax = Part.makeSphere(PELLET_D / 2.0, pocket_center + pocket_axis * PELLET_D)
two_rd = Part.makeSphere(PELLET_D / 2.0, pocket_center + pocket_radial * PELLET_D)
hit_one = pocket_solid.common(one).Volume
hit_ax = pocket_solid.common(two_ax).Volume
hit_rd = pocket_solid.common(two_rd).Volume
check(hit_one < 30.0 and hit_ax > 80.0 and hit_rd > 80.0,
      "pocket takes one Ø%.1f (hit %.0f mm3) and not two (axial %.0f, side %.0f)"
      % (PELLET_D, hit_one, hit_ax, hit_rd))

# Gear meshes that this meter actually has.
for i, (ga, gb) in enumerate(gear_pairs):
    ov = ga.common(gb).Volume
    check(ov < 1.0, "gear pair %d meshes without overlap (common %.1f mm3)" % (i + 1, ov))

# The outlet throat holds one ball and no drive shaft. A1 only: the other
# meters' throats are the funnel and the finger gap, already probed above.
if METER == "A1":
    check(check_screw_solids == 1, "auger screw is one solid (%d)" % check_screw_solids)
    throat = Part.makeSphere(PELLET_D / 2.0, V(X_LIP + PELLET_D / 2.0 + 1.5, 0.0, Z_BALL))
    throat_hit = screw.common(throat).Volume + stub.common(throat).Volume
    check(throat_hit < 5.0,
          "outlet throat clear of the screw and the shaft (hit %.0f mm3)" % throat_hit)

# Cup capacity across the loose-to-close sphere packing band.
n_lo = CUP_VOID / BALL_VOL * PACK_LO
n_hi = CUP_VOID / BALL_VOL * PACK_HI
check(30.0 <= n_lo and n_hi <= 50.0,
      "cup void %.0f cm3 holds %.0f..%.0f balls at packing %.2f..%.2f (inside 30..50)"
      % (CUP_VOID / 1000.0, n_lo, n_hi, PACK_LO, PACK_HI))
# Shoulder over the ring, spigot in the bore: the cup is carried by the ring.
check(0.05 <= cup.distToShape(ring)[0] <= 0.4,
      "cup sits on the ring (gap %.2f mm), not on a rod" % cup.distToShape(ring)[0])
check(frame_top.BoundBox.YLength > 200.0,
      "seat yoke spans %.0f mm (two posts)" % frame_top.BoundBox.YLength)

# Kicker meets the pellet and misses the chute and the guard.
dump_ball = Part.makeSphere(PELLET_D / 2.0, polar(DUMP_PHI, PACK_R, Z_BALL))
dump_chute = place_chute(DUMP_PHI)
kick_hit = kicker.common(dump_ball).Volume
kick_chute = kicker.distToShape(dump_chute)[0]
kick_guard = kicker.distToShape(guard)[0]
check(kick_hit > 150.0 and kick_chute >= 0.4 and kick_guard >= 0.4,
      "kicker at %.1f deg hits the pellet (%.0f mm3), clears chute %.2f and guard %.2f"
      % (DUMP_PHI, kick_hit, kick_chute, kick_guard))

# Chute sweep past the guard, the kicker and whichever meter parts can
# reach a chute. Gears aft of the covers, and blanks out past the hopper
# axis, are checked against the disk instead.
def _meets_chute(part):
    bb = part.BoundBox
    if bb.ZMax < Z_COVER_MIN - 2.0 or bb.ZMin > Z_COVER_MAX + 2.0:
        return False
    if bb.XMin > 140.0 or bb.XMax < -140.0 or bb.YMin > 140.0 or bb.YMax < -140.0:
        return False
    return True


near_parts = [part for part in meter_parts if _meets_chute(part)] or meter_parts[:1]
sweep_phis = []
p = GUARD_PHI0
while p <= DUMP_PHI + 1.0:
    sweep_phis.append(p)
    p += 22.0
if DUMP_PHI not in sweep_phis:
    sweep_phis.append(DUMP_PHI)
worst_g, worst_k, worst_m = 99.0, 99.0, 99.0
for phi in sweep_phis:
    ch = place_chute(phi)
    worst_g = min(worst_g, ch.distToShape(guard)[0])
    worst_k = min(worst_k, ch.distToShape(kicker)[0])
    worst_m = min(worst_m, min(ch.distToShape(part)[0] for part in near_parts))
check(worst_g >= 0.4 and worst_k >= 0.3 and worst_m >= 0.3,
      "chute sweep clears guard %.2f, kicker %.2f, meter %.2f mm"
      % (worst_g, worst_k, worst_m))

# Shaft, two bearings, disk.
check(brg_front.distToShape(shaft)[0] < 0.25 and brg_rear.distToShape(shaft)[0] < 0.25,
      "shaft Ø%.0f seated in two 6000 bores" % SHAFT_D)
check(house_front.distToShape(brg_front)[0] > 0.05 and house_rear.distToShape(brg_rear)[0] > 0.05,
      "housings clear the bearing OD")
check(disk.distToShape(shaft)[0] < 0.3 and abs(ang_phi(V(0, CRANK_R, 0)) - 90.0) < 1.0,
      "disk on the shaft, crank at phi 90")
disk_gap = min(disk.distToShape(p)[0] for p in meter_parts)
check(disk_gap >= 0.4, "meter clears the disk by %.2f mm" % disk_gap)
check(disk.distToShape(house_front)[0] >= 0.4 and disk.distToShape(house_rear)[0] >= 0.4,
      "housings clear the disk (front %.2f, rear %.2f)"
      % (disk.distToShape(house_front)[0], disk.distToShape(house_rear)[0]))
check(G.single_solid(disk) and G.single_solid(guard) and G.single_solid(cup)
      and G.single_solid(crank),
      "disk, guard, cup and crank each a single solid")

report = [
    NAME,
    "  meter                  : %s" % meter_note,
    "  pack                   : R %.0f, %d chutes = front_cover_feed, pellet Ø%.1f (library Ø%.1f)"
    % (PACK_R, N_STATION, PELLET_D, LIB_PELLET),
    "  motion                 : stroke %.1f, guard %.1f..%.1f deg, dump %.1f, tip in %.2f mm at the end"
    % (STROKE, GUARD_PHI0, GUARD_PHI1, DUMP_PHI, ins_end),
    "  drive                  : %s; shaft Ø%.0f in 2x 6000; crank R %.0f at phi 90"
    % (ratio_txt, SHAFT_D, CRANK_R),
    "  hopper                 : cup ID %.0f x %.0f, void %.0f cm3, %.0f..%.0f balls, ring at x %.0f"
    % (CUP_ID, CUP_H, CUP_VOID / 1000.0, n_lo, n_hi, X_SEAT),
    "  guide                  : lip x %.1f, tube %.1f..%.1f, length %.1f mm"
    % (X_LIP, X_TUBE0, X_TUBE1, GUIDE_LEN),
    "  not frozen             : pack R, shroud, length; PELLET_D waits on a 20-ball measure",
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", text) for text, ok in checks]
print("\n".join(report))
sys.stdout.flush()
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "checks_%s.txt" % METER), "w") as f:
    f.write("\n".join(report) + "\n")

if FEED_BENCH_LIBRARY:
    raise SystemExit(0 if all(ok for _, ok in checks) else 1)

# ---------------------------------------------------------------- scene + export
os.makedirs(OUT_DIR, exist_ok=True)
sc = FV.Scene(NAME)
for i, ch in enumerate(chutes):
    sc.add("Pack", "Chute_%d" % i, ch, "stator")
sc.add("Pack", "Disk", disk, "plate")
sc.add("Pack", "Shaft", shaft, "steel")
sc.add("Frame", "Bearing_front", brg_front, "steel")
sc.add("Frame", "Bearing_rear", brg_rear, "steel")
sc.add("Frame", "Housing_front", house_front, "printed")
sc.add("Frame", "Housing_rear", house_rear, "printed")
sc.add("Frame", "Base", base, "frame")
sc.add("Frame", "Crank", crank, "printed")
sc.add("Frame", "Seat", frame_top, "frame")
sc.add("Guard", "Guard", guard, "stator")
sc.add("Hopper", "Cup", cup, "printed")
for i, part in enumerate(meter_parts):
    sc.add("Meter", "Meter_%d" % i, part, "rotor" if i == 0 else "printed")
sc.add("Trap", "Kicker", kicker, "shoe")
sc.add("Trap", "Tray", tray, "printed")
sc.add("Reference", "Pellet_drop", pellet_drop, "flow")
sc.add("Reference", "Pellet_held", pellet_held, "flow")
sc.add("Reference", "Pellet_pocket", pellet_pocket, "flow")
sc.label("Labels", "Стенд подачи  %s  R %.0f" % (METER, PACK_R), (0, 0, Z_BALL + 40))
sc.finish(hidden_groups=("Labels",), opaque_groups=())
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

if all(ok for _, ok in checks) and os.environ.get("SKIP_EXPORT") != "1":
    import MeshPart

    def write(shape, fname):
        s = shape.copy()
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, fname + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.18,
                              AngularDeflection=0.4).write(os.path.join(OUT_DIR, fname + ".stl"))

    write(chutes[0], "chute")
    write(disk, "disk")
    write(guard, "guard")
    write(crank, "crank")
    write(cup, "hopper")
    write(kicker, "kicker")
    write(tray, "tray")
    write(frame_top, "seat")
    write(meter_parts[0], "meter_main")
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")

if not all(ok for _, ok in checks):
    raise SystemExit("gatling feed bench has [FAIL] checks")
