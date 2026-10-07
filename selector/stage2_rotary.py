# -*- coding: utf-8 -*-
"""
Ratling Stage 2 test article: single-channel rotating interface.

The real selector geometry, turning, with one working flow path:

    stator ...... full disc, all 25 ports tapped G1/8 from the front, centre
                  inlet; thick only in the port ring and the centre boss.
    rotor ....... an arm (not a disc yet) carrying the spigot, the internal
                  channel and the floating shoe of Stage 1.
    hub ......... flanged, screwed to the rotor back, set screw on the shaft.
    frame ....... rear spider: bearing boss for the rotor shaft (2 x 608) and,
                  on the left, the boss for the crank shaft (2 x 608), so the
                  bevel mesh depends on one printed part.
    spacers ..... 4 columns between stator and frame, M5 through.
    bevel pair .. printed 1:1 straight bevel gears (ratling/gears.py), set
                  screws on the shafts; the mesh is checked for interference.
    crank arm ... on the crank shaft, handle on an M6 bolt.

Bought: 2 shafts Ø8, 4 x 608ZZ, M5/M3 screws.
No detent or valve cam yet (Stage 3); ports are found by eye.

Assembly note: tighten the column bolts with the rotor in place, so the
spigot in its bore centres the frame; the bolt holes leave room for that.

All numbers come from ratling/params.py; the frame is described there.
Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/selector/stage2_rotary.py').read())
"""

import importlib
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
import ratling.params as P
import ratling.geom as G
import ratling.fcview as V
import ratling.gears as GR
for _m in (P, G, V, GR):
    importlib.reload(_m)
from ratling.geom import cyl, fuse_all, port_xy

OUT_DIR = os.path.join(REPO, "exports", "stage2_rotary")
NAME = "stage2_rotary"

ALL_PORTS = [i * P.INDEX_DEG for i in range(P.N_PORTS)]
FITTED_PORTS = [0.0]                    # fittings installed for the test
HOSE_LEN = 60.0
MID_BORE_D = 12.0                       # between the two bearings of a boss
COLUMNS = [port_xy(a, P.FRAME_COL_R) for a in P.column_angles]
PIN_XY = port_xy(P.HUB_PIN_ANGLE, P.HUB_PIN_R)
t = P.stator_t
apex = P.bevel_apex_z


def ycyl(d, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(d / 2, y1 - y0, App.Vector(x, y0, z), G.Y)


def teardrop_y(d, y0, y1, z, cap=1.5):
    """Hole along Y with a 45 deg roof towards -Z (up when the frame prints
    front face down), roof cut flat cap mm above the circle."""
    r = d / 2
    roof = Part.makeBox(r, y1 - y0, r, App.Vector(0, 0, 0))
    roof.rotate(G.O, G.Y, 135)
    roof.translate(App.Vector(0, y0, z))
    limit = Part.makeBox(2 * r + 2, y1 - y0 + 2, 2 * r + cap, App.Vector(-r - 1, y0 - 1, z - r - cap))
    return ycyl(d, y0, y1, 0, z).fuse(roof.common(limit))


def bar(angle, r0, r1, w, z0, z1):
    """Radial bar from r0 to r1 at angle (deg), width w."""
    b = Part.makeBox(r1 - r0, w, z1 - z0, App.Vector(r0, -w / 2, z0))
    b.rotate(G.O, G.Z, angle)
    return b


# ---------------------------------------------------------------- parts
def make_stator():
    r_in, r_out = P.PORT_R - P.PORT_RING_W / 2, P.PORT_R + P.PORT_RING_W / 2
    body = fuse_all([cyl(P.stator_d, 0, P.STATOR_PLATE_T),
                     cyl(2 * r_out, 0, t).cut(cyl(2 * r_in, -1, t + 1)),
                     cyl(P.CENTRE_BOSS_D, 0, t)])
    tools = fuse_all([G.centre_inlet_tools(0, t), G.port_tools(ALL_PORTS, t)]
                     + [cyl(P.FRAME_BOLT_D, -1, t + 1, x, y) for x, y in COLUMNS])
    return body.cut(tools).cut(G.port_chamfers(ALL_PORTS)).removeSplitter()


def hub_screws(d, z0, z1):
    return fuse_all([cyl(d, z0, z1, *port_xy(a, P.HUB_SCREW_R)) for a in (60, 180, 300)])


def make_rotor():
    zf, zb = P.rotor_face_z, P.rotor_back_z
    w = P.ROTOR_ARM_W
    arm = fuse_all([cyl(P.ROTOR_CENTRE_D, zb, zf),
                    Part.makeBox(P.PORT_R, w, zf - zb, App.Vector(0, -w / 2, zb)),
                    cyl(w, zb, zf, P.PORT_R), G.spigot()])
    holes = fuse_all([G.rotor_passages(),
                      hub_screws(P.HUB_SCREW_PILOT, zb - 1, zb + P.HUB_SCREW_DEPTH),
                      cyl(P.HUB_PIN_HOLE, zb - 1, zb + P.HUB_PIN_DEPTH, *PIN_XY)])
    return arm.cut(holes).removeSplitter()


def cam_face(z0, z1):
    """Cam rim: the pitch curve offset inwards by the follower radius."""
    pts, _, _ = P.cam_profile(600)
    n = len(pts)
    rf = P.FOLLOWER_D / 2
    rim = []
    for i in range(n):
        (xa, ya), (x, y), (xb, yb) = pts[i - 1], pts[i], pts[(i + 1) % n]
        tx, ty = xb - xa, yb - ya
        L = math.hypot(tx, ty)
        rim.append(App.Vector(x - rf * ty / L, y + rf * tx / L, z0))
    bs = Part.BSplineCurve()
    bs.interpolate(rim, PeriodicFlag=True)
    return Part.Face(Part.Wire(bs.toShape())).extrude(App.Vector(0, 0, z1 - z0))


def make_hub():
    """Hub whose flange is the cam: 25 lobes, phased to the rotor by a dowel."""
    zb = P.rotor_back_z
    z_fl = zb - P.HUB_FLANGE_T
    hub = cam_face(z_fl, zb).fuse(cyl(P.HUB_BOSS_D, P.hub_back_z, z_fl + 0.01))
    z_set = (P.hub_back_z + z_fl) / 2
    holes = fuse_all([cyl(P.SHAFT_BORE_D, P.hub_back_z - 1, zb + 1),
                      hub_screws(3.4, z_fl - 1, zb + 1),
                      cyl(P.HUB_PIN_HOLE, z_fl - 1, zb + 1, *PIN_XY),
                      ycyl(P.SET_SCREW_PILOT, 0, P.HUB_BOSS_D, 0, z_set)])
    return hub.cut(holes).removeSplitter()


# ---------------------------------------------------------------- valve and detent
# Each station is drawn in a local frame (u radial, v tangential, z axial) and
# turned to its angle. A lever pivots on an M3 bolt with a printed spacer; its
# 623 follower rolls on the cam; its far end (2 x L1 from the pivot) carries an
# M3 adjusting screw that presses the valve roller, or takes the detent spring.
CAM_BACK = P.rotor_back_z - P.HUB_FLANGE_T
CAM_MID = (P.rotor_back_z + CAM_BACK) / 2
LEVER_FRONT = CAM_BACK - 0.5
LEVER_BACK = LEVER_FRONT - P.LEVER_T
L1, LW = P.LEVER_L1, P.LEVER_W
ZF = P.spider_front_z
ZB_ARM = ZF - P.FRAME_ARM_T


def turned(shape, angle):
    s = shape.copy()
    s.rotate(G.O, G.Z, angle)
    return s


def box_uv(u0, u1, v0, v1, z0, z1):
    return Part.makeBox(u1 - u0, v1 - v0, z1 - z0, App.Vector(u0, v0, z0))


def ucyl(d, u0, u1, v, z):
    return Part.makeCylinder(d / 2, u1 - u0, App.Vector(u0, v, z), G.X)


def make_lever(u_f):
    """Lever in the local frame: pivot at v = -L1, follower at 0, far end at +L1."""
    lever = fuse_all([box_uv(u_f - LW / 2, u_f + LW / 2, -L1, L1, LEVER_BACK, LEVER_FRONT),
                      cyl(LW, LEVER_BACK, LEVER_FRONT, u_f, -L1),
                      cyl(LW + 2, LEVER_BACK, LEVER_FRONT, u_f, L1)])
    zm = (LEVER_BACK + LEVER_FRONT) / 2
    holes = fuse_all([cyl(3.4, LEVER_BACK - 1, LEVER_FRONT + 1, u_f, -L1),
                      cyl(2.5, LEVER_BACK - 1, LEVER_FRONT + 1, u_f, 0),
                      ucyl(2.5, u_f - LW, u_f + LW, L1, zm)])
    return lever.cut(holes).removeSplitter()


def station_common(u_f):
    """Frame additions, parts and refs shared by both stations (local frame)."""
    frame_add = [box_uv(u_f - 6, u_f + 6, -L1 - 6, 0, ZB_ARM, ZF),
                 cyl(12, ZB_ARM, ZF, u_f, -L1)]
    frame_holes = [cyl(3.4, ZB_ARM - 1, ZF + 1, u_f, -L1)]
    spacer = cyl(7, ZF, LEVER_BACK, u_f, -L1).cut(cyl(3.4, ZF - 1, LEVER_BACK + 1, u_f, -L1))
    follower = cyl(P.FOLLOWER_D, CAM_MID - P.FOLLOWER_W / 2, CAM_MID + P.FOLLOWER_W / 2, u_f, 0).cut(
        cyl(3, CAM_MID - 5, CAM_MID + 5, u_f, 0))
    screws = fuse_all([cyl(3, ZB_ARM - 3, LEVER_FRONT + 2, u_f, -L1),          # pivot bolt
                       cyl(3, LEVER_BACK - 2, CAM_MID + P.FOLLOWER_W / 2 + 2, u_f, 0)])  # axle
    return frame_add, frame_holes, spacer, follower, screws


def valve_station():
    a = P.VALVE_ANGLE
    u_f = P.cam_pitch_r(a)                       # on a lobe: aligned, valve pressed
    u_edge = u_f + LW / 2
    u_r = u_edge + P.ADJUST_GAP + P.VALVE_ROLLER_D / 2
    u_top = u_r + P.VALVE_ROLLER_H - P.VALVE_TRAVEL[1]
    u_bot = u_top + P.VALVE_D
    v_c = L1 + P.VALVE_ROLLER_TO_BODY
    A, B = P.VALVE_A, P.VALVE_B
    zm = ZF + B / 2
    holes_uv = [(u_bot - P.VALVE_KB, v_c - P.VALVE_KA / 2),
                (u_bot - P.VALVE_KB - P.VALVE_KC, v_c - P.VALVE_KA / 2),
                (u_bot - P.VALVE_KB - P.VALVE_KC / 2, v_c + P.VALVE_KA / 2)]
    frame_add, frame_holes, spacer, follower, screws = station_common(u_f)
    frame_add += [bar(0, 0, u_bot + 2, P.FRAME_ARM_W, ZB_ARM, ZF),
                  box_uv(u_top - 2, u_bot + 2, -P.FRAME_ARM_W / 2, v_c + A / 2 + 2, ZB_ARM, ZF)]
    frame_holes += [cyl(2.5, ZB_ARM - 1, ZF + 1, u, v) for u, v in holes_uv]
    body = box_uv(u_top, u_bot, v_c - A / 2, v_c + A / 2, ZF, ZF + B).cut(
        fuse_all([cyl(P.VALVE_HOLE_D, ZF - 1, ZF + B + 1, u, v) for u, v in holes_uv]))
    roller = cyl(P.VALVE_ROLLER_D, zm - P.VALVE_ROLLER_W / 2, zm + P.VALVE_ROLLER_W / 2, u_r, L1)
    head = box_uv(u_r + 3, u_top, L1 - 4, v_c + A / 2, zm - 6.5, zm + 6.5)   # its lever and cover
    valve = fuse_all([body, roller, head])
    screws = screws.fuse(ucyl(3, u_edge - LW - 2, u_edge + P.ADJUST_GAP, L1, (LEVER_BACK + LEVER_FRONT) / 2))

    def side_fitting(u, v_face, sign):
        f = G.push_in_fitting(0, 0, 0)
        f.rotate(G.O, G.X, -90 * sign)          # +Z -> +v (sign 1) or -v (sign -1)
        f.translate(App.Vector(u, v_face, zm))
        return f
    v_a = v_c - A / 2                          # A faces the centre side
    u_a = u_bot - P.VALVE_PORT_A
    fittings = fuse_all([side_fitting(u_a, v_a, -1)]
                        + [side_fitting(u_bot - h, v_c + A / 2, 1) for h in P.VALVE_PORTS_PR])
    # inlet hose from port A to the stator centre: out of the fitting, straight
    # forward past the stator rim, in over the front face between two output
    # hoses (half a step from the nearest ports), down into the centre fitting
    rot = App.Rotation(G.Z, a)
    half_step = P.INDEX_DEG * (math.floor((a + P.INDEX_DEG / 2) / P.INDEX_DEG) - 0.5) - a
    hx, hy = port_xy(half_step)
    way = [(u_a, v_a - 6, zm), (u_a, v_a - 20, zm + 2), (u_a, v_a - 26, zm + 15),
           (u_a, v_a - 26, t + 5), (u_a - 15, hy - 1, t + 26),
           (hx, hy, t + 32), (15.0, 0.0, t + 36), (0.0, 0.0, t + 28), (0.0, 0.0, t + 6)]
    path = [rot.multVec(App.Vector(*w)) for w in way]
    return {k: turned(v, a) for k, v in dict(
        frame_add=fuse_all(frame_add), frame_holes=fuse_all(frame_holes), spacer=spacer,
        follower=follower, screws=screws, valve=valve, lever=make_lever(u_f),
        fittings=fittings).items()}, make_lever(u_f), path


def detent_station():
    a = P.DETENT_ANGLE
    u_f = P.cam_pitch_r(a)                       # in a valley: aligned
    u_edge = u_f + LW / 2
    u_pad = u_edge + P.DETENT_SPRING_LEN
    frame_add, frame_holes, spacer, follower, screws = station_common(u_f)
    block_v = (L1 - 8, L1 + 8)
    frame_add += [bar(0, 0, u_pad + 10, P.FRAME_ARM_W, ZB_ARM, ZF),
                  box_uv(u_pad - 1, u_pad + 10, -P.FRAME_ARM_W / 2, block_v[1], ZB_ARM, ZF)]
    block_screws = [(u_pad + 5, block_v[0] + 3), (u_pad + 5, block_v[1] - 3)]
    frame_holes += [cyl(2.5, ZB_ARM - 1, ZF + 1, u, v) for u, v in block_screws]
    zm = (LEVER_BACK + LEVER_FRONT) / 2
    block = box_uv(u_pad, u_pad + 10, block_v[0], block_v[1], ZF, LEVER_FRONT).cut(fuse_all(
        [cyl(3.4, ZF - 1, LEVER_FRONT + 1, u, v) for u, v in block_screws]
        + [ucyl(7, u_pad - 1, u_pad + 3, L1, zm)]))                         # spring pocket
    spring = ucyl(6, u_edge, u_pad + 3, L1, zm).cut(ucyl(5, u_edge - 1, u_pad + 4, L1, zm))
    return {k: turned(v, a) for k, v in dict(
        frame_add=fuse_all(frame_add), frame_holes=fuse_all(frame_holes), spacer=spacer,
        follower=follower, screws=screws, block=block, spring=spring,
        lever=make_lever(u_f)).items()}, block


VALVE_ST, LEVER_PRINT, INLET_PATH = valve_station()


def inlet_hose():
    """6 mm hose along INLET_PATH; returns (shape, length mm, inner volume cm3)."""
    bs = Part.BSplineCurve()
    bs.interpolate(INLET_PATH)
    edge = bs.toShape()
    start, tangent = INLET_PATH[0], bs.tangent(bs.FirstParameter)[0]
    prof = Part.Wire(Part.makeCircle(G.HOSE_D / 2, start, tangent))
    hose_shape = Part.Wire(edge).makePipeShell([prof], True, False)
    L = edge.Length
    return hose_shape, L, math.pi * (G.HOSE_D / 2 - 1) ** 2 * L / 1000


INLET_HOSE, INLET_LEN, INLET_VOL = inlet_hose()
DETENT_ST, BLOCK_PRINT = detent_station()


def make_frame():
    zf = P.spider_front_z
    zb_arm = zf - P.FRAME_ARM_T
    y0, y1 = P.crank_boss_y0, P.crank_boss_y1
    half = P.BEARING_BOSS_D / 2 - 1
    body = fuse_all(
        [cyl(P.BEARING_BOSS_D, P.boss_back_z, zf)]
        + [bar(a, 0, P.FRAME_COL_R, P.FRAME_ARM_W, zb_arm, zf) for a in P.column_angles]
        + [cyl(P.FRAME_COL_D + 4, zb_arm, zf, x, y) for x, y in COLUMNS]
        + [Part.makeBox(2 * half, y1, P.FRAME_ARM_T, App.Vector(-half, 0, zb_arm)),     # arm to the crank side
           Part.makeBox(2 * half, y1 - y0, zb_arm - apex + 0.01, App.Vector(-half, y0, apex)),  # web
           ycyl(P.BEARING_BOSS_D, y0, y1, 0, apex),                                  # crank boss
           VALVE_ST["frame_add"], DETENT_ST["frame_add"]])
    W = P.BEARING_W
    holes = fuse_all(
        [cyl(P.BEARING_SEAT_D, zf - W, zf + 1), cyl(MID_BORE_D, P.boss_back_z - 1, zf + 1),
         cyl(P.BEARING_SEAT_D, P.boss_back_z - 1, P.boss_back_z + W),
         teardrop_y(P.BEARING_SEAT_D, y0 - 1, y0 + W, apex),
         teardrop_y(MID_BORE_D, y0, y1, apex),
         teardrop_y(P.BEARING_SEAT_D, y1 - W, y1 + 1, apex)]
        + [cyl(P.FRAME_BOLT_D, zb_arm - 1, zf + 1, x, y) for x, y in COLUMNS]
        + [VALVE_ST["frame_holes"], DETENT_ST["frame_holes"]])
    return body.cut(holes).removeSplitter()


def make_spacer(x=0.0, y=0.0):
    return cyl(P.FRAME_COL_D, P.spider_front_z, 0, x, y).cut(
        cyl(P.FRAME_BOLT_D, P.spider_front_z - 1, 1, x, y))


def make_crank_arm():
    """Crank arm at rest pointing down (machine -X), plate on the outer side."""
    y_hub0 = P.crank_arm_y
    y_out = y_hub0 + P.CRANK_HUB_L
    plate_t = 8.0
    a = P.CRANK_ARM
    arm = fuse_all([
        ycyl(P.CRANK_HUB_D, y_hub0, y_out, 0, apex),
        Part.makeBox(a, plate_t, P.CRANK_HUB_D, App.Vector(-a, y_out - plate_t, apex - P.CRANK_HUB_D / 2)),
        ycyl(P.CRANK_HUB_D, y_out - plate_t, y_out, -a, apex),
    ])
    holes = fuse_all([ycyl(P.SHAFT_BORE_D, y_hub0 - 1, y_out + 1, 0, apex),
                      ycyl(6.5, y_out - plate_t - 1, y_out + 1, -a, apex),
                      cyl(P.SET_SCREW_PILOT, apex, apex + P.CRANK_HUB_D, 0, (y_hub0 + y_out - plate_t) / 2)])
    return arm.cut(holes).removeSplitter()


stator = make_stator()
rotor = make_rotor()
hub = make_hub()
shoe = G.shoe()
frame = make_frame()
spacers = [make_spacer(x, y) for x, y in COLUMNS]
crank_arm = make_crank_arm()


# ---------------------------------------------------------------- bevel pair
def make_gear(phase_deg=0.0):
    """Printed bevel gear, apex at the origin, hub towards +Z, set screw in the hub.

    Built in its print orientation: small end on the bed.
    """
    g, info = GR.bevel_gear(P.BEVEL_MODULE, P.BEVEL_TEETH, P.BEVEL_FACE, P.BEVEL_HUB_D,
                            P.BEVEL_HUB_L, P.SHAFT_BORE_D, P.BEVEL_BACKLASH, phase_deg=phase_deg)
    z_set = info["big_end_z"] + P.BEVEL_HUB_L / 2
    g = g.cut(Part.makeCylinder(P.SET_SCREW_PILOT / 2, P.BEVEL_HUB_D, App.Vector(0, 0, z_set), G.X))
    return g.removeSplitter(), info


gear_print, gear_info = make_gear()
gear_rotor = gear_print.copy()
gear_rotor.translate(App.Vector(0, 0, apex))
# the crank gear turned half a tooth so the teeth fall into the gaps
gear_crank, _ = make_gear(180.0 / P.BEVEL_TEETH)
gear_crank.rotate(G.O, G.X, -90)
gear_crank.translate(App.Vector(0, 0, apex))


# ---------------------------------------------------------------- bought parts
def bearing(axis, pos):
    b = Part.makeCylinder(P.BEARING_OD / 2, P.BEARING_W, pos, axis).cut(
        Part.makeCylinder(P.SHAFT_D / 2, P.BEARING_W, pos, axis))
    return b


shaft_rotor = cyl(P.SHAFT_D, P.rotor_shaft[1], P.rotor_shaft[0])
shaft_crank = ycyl(P.SHAFT_D, P.crank_shaft[0], P.crank_shaft[1], 0, apex)
W = P.BEARING_W
bearings = fuse_all([
    bearing(G.Z, App.Vector(0, 0, P.spider_front_z - W)),
    bearing(G.Z, App.Vector(0, 0, P.boss_back_z)),
    bearing(G.Y, App.Vector(0, P.crank_boss_y0, apex)),
    bearing(G.Y, App.Vector(0, P.crank_boss_y1 - W, apex)),
])
handle_y0 = P.crank_arm_y + P.CRANK_HUB_L
handle = ycyl(P.CRANK_HANDLE_D, handle_y0, handle_y0 + P.CRANK_HANDLE_LEN, -P.CRANK_ARM, apex)

# ---------------------------------------------------------------- checks
printed = {"stator": stator, "rotor": rotor, "hub": hub, "shoe": shoe, "frame": frame,
           "crank_arm": crank_arm, "bevel (rotor)": gear_rotor, "bevel (crank)": gear_crank,
           "lever (valve)": VALVE_ST["lever"], "lever (detent)": DETENT_ST["lever"],
           "pivot spacer (valve)": VALVE_ST["spacer"], "pivot spacer (detent)": DETENT_ST["spacer"],
           "detent block": DETENT_ST["block"]}
printed.update({"spacer%d" % i: s for i, s in enumerate(spacers)})
bought = {"rotor shaft": shaft_rotor, "crank shaft": shaft_crank, "bearings": bearings,
          "handle": handle, "valve": VALVE_ST["valve"], "follower (valve)": VALVE_ST["follower"],
          "follower (detent)": DETENT_ST["follower"], "detent spring": DETENT_ST["spring"]}
everything = dict(printed, **bought)
names = list(everything)
# Pairs that touch by design: shafts in their bores, followers rolling on the
# cam, the valve on its pad and its roller on the adjusting screw, the spring
# on lever and block. Screws are not in the check at all (they are threaded
# into pilot holes). The two gears are checked: their teeth must not overlap.
TOUCHING = [{"rotor shaft", "bevel (rotor)"}, {"crank shaft", "bevel (crank)"},
            {"rotor shaft", "bearings"}, {"crank shaft", "bearings"},
            {"rotor shaft", "hub"}, {"crank shaft", "crank_arm"},
            {"follower (valve)", "hub"}, {"follower (detent)", "hub"},
            {"valve", "frame"}, {"detent spring", "lever (detent)"},
            {"detent spring", "detent block"}]
clashes = ["%s / %s" % (a, b) for i, a in enumerate(names) for b in names[i + 1:]
           if {a, b} not in TOUCHING and not G.no_overlap(everything[a], everything[b])]

rotor_sweep = cyl(2 * P.rotor_sweep_r, P.rotor_back_z, P.rotor_face_z)
crank_sweep = ycyl(2 * (P.CRANK_ARM + P.CRANK_HANDLE_D / 2 + 2), P.crank_arm_y,
                   handle_y0 + P.CRANK_HANDLE_LEN, 0, apex)
sx = P.PORT_R
air_path = ([(0, 0, z) for z in (P.channel_z, P.rotor_face_z, 0.0, P.SPIGOT_TIP_Z - 0.5)]
            + [(x, 0, P.channel_z) for x in (5, 20, 40, sx - 5)]
            + [(sx, 0, z) for z in (P.channel_z, P.shoe_floor_z + 0.5, -P.SHOE_LEN - 1)])
stator_path = [(0, 0, z) for z in (1, P.spigot_bore_depth + 1, t - 1)] + \
              [(x, y, z) for a in ALL_PORTS for x, y in [port_xy(a)] for z in (0.2, t / 2, t - 1)]

geo_checks = [
    ("all printed parts valid single solids", all(G.single_solid(s) for s in printed.values())),
    ("no interference between parts" + ("" if not clashes else ": " + ", ".join(clashes)),
     not clashes),
    ("rotor sweep clear of frame and spacers",
     all(G.no_overlap(rotor_sweep, s) for s in [frame] + spacers)),
    ("crank sweep clear of frame, stator, spacers",
     all(G.no_overlap(crank_sweep, s) for s in [frame, stator] + spacers)),
    ("shoe face on the stator face (z = 0)", abs(shoe.BoundBox.ZMax) < 1e-6),
    ("air path open through rotor", G.open_along(rotor, air_path) and G.open_along(shoe, [(sx, 0, -1)])),
    ("all 25 ports and the inlet open through the stator", G.open_along(stator, stator_path)),
    ("bevel teeth mesh without interference (backlash %.2f)" % P.BEVEL_BACKLASH,
     G.no_overlap(gear_rotor, gear_crank)),
    ("followers roll on the cam (no gap, no overlap > 0.05 mm)",
     all(abs(f.distToShape(hub)[0]) < 0.05 and f.common(hub).Volume < 0.5
         for f in (VALVE_ST["follower"], DETENT_ST["follower"]))),
    ("levers clear of the rotor sweep", all(G.no_overlap(rotor_sweep, VALVE_ST[k]) and
                                            G.no_overlap(rotor_sweep, DETENT_ST[k])
                                            for k in ("lever", "spacer"))),
    ("inlet hose clear of stator, frame, spacers, valve, output hoses",
     all(G.no_overlap(INLET_HOSE, s) for s in [stator, frame, VALVE_ST["valve"]] + spacers
         + [G.hose(x, y, t, HOSE_LEN) for x, y in (port_xy(a) for a in ALL_PORTS)])),
    ("rotor shaft long enough for the hub and the gear",
     P.rotor_shaft[0] >= P.rotor_back_z - 0.01 and P.rotor_shaft[1] <= apex + P.BEVEL_MOUNT - P.BEVEL_LEN + 3),
]

vols = {k: v.Volume / 1000 for k, v in printed.items()}
lines = [P.report(), "", NAME,
         "  printed cm3            : " + ", ".join("%s %.1f" % (k, v) for k, v in vols.items()
                                                    if not k.startswith("spacer") or k == "spacer0"),
         "  print                  : stator face down; rotor back down; hub (cam) flange down;"
         " frame front down; shoe face down; crank arm, levers flat; gears small end down",
         "  bevel pair             : m%g z%d, pitch Ø%.1f, OD Ø%.1f, face %.1f, mount %.1f;"
         " print small end down" % (P.BEVEL_MODULE, P.BEVEL_TEETH, P.bevel_pitch_d, gear_info["od"],
                                    P.BEVEL_FACE, P.BEVEL_MOUNT),
         "  bought                 : shafts Ø%g x %.0f + %.0f mm, 4 x 608ZZ,"
         % (P.SHAFT_D, P.rotor_shaft[0] - P.rotor_shaft[1], P.crank_shaft[1] - P.crank_shaft[0]),
         "                           4 x M5 x %.0f, 3 x M3 x 10 (hub), 4 x M3 set screws, M6 handle bolt,"
         % (math.ceil((P.column_len + P.STATOR_PLATE_T + P.FRAME_ARM_T + 6) / 5) * 5),
         "                           2 x O-ring 8x1.5, pen spring, G1/8-6 fittings x %d" % (4 + len(FITTED_PORTS)),
         "  inlet hose A -> centre : %.0f mm of 6/4, %.1f cm3; + %.1f cm3 inside stator and rotor"
         % (INLET_LEN, INLET_VOL, G.rotor_passages().Volume / 1000),
         "                           valve Airtac M3R110-06G, 2 x 623ZZ, Ø3 dowel x %.0f,"
         % (P.HUB_FLANGE_T + P.HUB_PIN_DEPTH),
         "                           M3: 2 pivot bolts x 30, 2 axles x 16, adjusting screw x 12,"
         " 3 valve screws x 25, 2 block screws x 20; detent spring Ø6, ~%.0f N at %.0f mm"
         % (P.detent_spring_force, P.DETENT_SPRING_LEN),
         ]
lines += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in geo_checks]
report = "\n".join(lines)
print(report)

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
sc = V.Scene(NAME)
doc = sc.doc
sc.add("Printed", "Stator", stator, "stator")
sc.add("Printed", "Rotor", rotor, "rotor")
sc.add("Printed", "Shoe", shoe, "shoe")
sc.add("Printed", "Hub", hub, "printed")
sc.add("Printed", "Frame", frame, "frame")
for i, s in enumerate(spacers):
    sc.add("Printed", "Spacer%d" % i, s, "printed")
sc.add("Printed", "Crank_arm", crank_arm, "printed")
sc.add("Printed", "Bevel_rotor", gear_rotor, "drive")
sc.add("Printed", "Bevel_crank", gear_crank, "drive")
sc.add("Printed", "Lever_valve", VALVE_ST["lever"], "printed")
sc.add("Printed", "Lever_detent", DETENT_ST["lever"], "printed")
sc.add("Printed", "Pivot_spacers", VALVE_ST["spacer"].fuse(DETENT_ST["spacer"]), "printed")
sc.add("Printed", "Detent_block", DETENT_ST["block"], "printed")

zb_arm = P.spider_front_z - P.FRAME_ARM_T
bolts = fuse_all([cyl(5.0, zb_arm - 6, P.STATOR_PLATE_T + 3.5, x, y)
                  .fuse(cyl(8.5, P.STATOR_PLATE_T, P.STATOR_PLATE_T + 3.5, x, y))
                  .fuse(G.hex_prism(8.0, zb_arm - 4, zb_arm, x, y)) for x, y in COLUMNS])
ports_fitted = [(0.0, 0.0)] + [port_xy(a) for a in FITTED_PORTS]
ports_hosed = [port_xy(a) for a in FITTED_PORTS]
for n, s, style in (
        ("Shaft_rotor", shaft_rotor, "steel"), ("Shaft_crank", shaft_crank, "steel"),
        ("Bearings", bearings, "steel"), ("Handle", handle, "drive"),
        ("Bolts", bolts, "steel_ghost"),
        ("Fittings", fuse_all([G.push_in_fitting(x, y, t) for x, y in ports_fitted]), "steel"),
        ("Hoses", fuse_all([G.hose(x, y, t, HOSE_LEN) for x, y in ports_hosed]
                           + [INLET_HOSE]), "hose"),
        ("Valve_fittings", VALVE_ST["fittings"], "steel"),
        ("ORings", G.rotor_orings(), "oring"), ("Spring", G.shoe_spring(), "steel"),
        ("Flow", G.flow_path(t, HOSE_LEN), "flow"),
        ("Valve", VALVE_ST["valve"], "drive"),
        ("Followers", VALVE_ST["follower"].fuse(DETENT_ST["follower"]), "steel"),
        ("Station_screws", VALVE_ST["screws"].fuse(DETENT_ST["screws"]), "steel"),
        ("Detent_spring", DETENT_ST["spring"], "steel")):
    sc.add("Bought", n, s, style)

half = Part.makeBox(400, 200, 400, App.Vector(-200, -200, -200))     # machine y < 0
for n in ("Stator", "Rotor", "Shoe", "Hub", "Frame", "Shaft_rotor", "Bevel_rotor", "Bearings",
          "ORings", "Spring", "Fittings", "Hoses"):
    style = dict(Stator="stator", Rotor="rotor", Shoe="shoe", Hub="printed", Frame="frame",
                 ORings="oring", Hoses="hose", Bevel_rotor="drive").get(n, "steel")
    sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)

for text, pos in [
    ("ВХОД", (-14, 0, t + HOSE_LEN)),
    ("ВЫХОД 1 (совмещён)", (P.PORT_R + 14, 0, t + HOSE_LEN)),
    ("СТАТОР: 25 портов", (P.stator_d / 2 + 5, 0, t)),
    ("РОТОР-рычаг + башмак", (P.PORT_R + 20, 0, P.rotor_back_z)),
    ("СТУПИЦА = КУЛАЧОК (25 выступов)", (-30, 0, P.hub_back_z)),
    ("КЛАПАН M3R110 (импульс)", (60, -P.cam_pitch_r(P.VALVE_ANGLE) - 60, P.spider_front_z)),
    ("ФИКСАТОР (пружина)", (P.CAM_PITCH_R + 40, 20, P.spider_front_z)),
    ("РАМА: подшипники вала и рукоятки", (-40, 0, P.boss_back_z - 5)),
    ("КОНИЧЕСКАЯ ПАРА 1:1", (25, 0, apex - 10)),
    ("РУКОЯТКА", (-P.CRANK_ARM - 10, handle_y0 + P.CRANK_HANDLE_LEN, apex)),
    ("СТОЙКИ x4", (COLUMNS[3][0] + 12, COLUMNS[3][1], P.spider_front_z / 2)),
]:
    sc.label("Labels", text, pos)
sc.finish(hidden_groups=("Section",), opaque_groups=("Section",))
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

# ---------------------------------------------------------------- exports
import MeshPart


def write_stl(shape, name, rot=None):
    s = shape.copy()
    if rot is not None:
        s.rotate(G.O, rot[0], rot[1])
    s.translate(App.Vector(-s.BoundBox.Center.x, -s.BoundBox.Center.y, -s.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1)
    m.write(os.path.join(OUT_DIR, name + ".stl"))


FLIP = (G.X, 180)
for n, s, rot in (("stator", stator, None), ("rotor", rotor, None), ("hub", hub, FLIP),
                  ("shoe", shoe, FLIP), ("frame", frame, FLIP), ("spacer", spacers[0], None),
                  ("crank_arm", crank_arm, (G.X, -90)), ("bevel_gear", gear_print, None),
                  ("lever", LEVER_PRINT, None), ("detent_block", BLOCK_PRINT, None),
                  ("pivot_spacer", VALVE_ST["spacer"], None)):
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    write_stl(s, n, rot)
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write(report + "\n")
print("written to", OUT_DIR)
