# -*- coding: utf-8 -*-
"""
Mitrailleuse firing head, bench C: the real 16-barrel rotor under a quarter of the core block, cranked by
hand through the gun's own drive (FreeCAD 1.0).

Bench B (head_bench.py) tries the pneumatics of one port on a flat slider. This one turns the gun's own
rotor (rotor_timing.py, 16 barrels) under one quarter of the core block (four ports), through a 5:1 spur
pair, a slip clutch and a 1:1 bevel pair from a horizontal crank, to try what B cannot: the crank force,
the rotor's thrust, and stopping it on a step when the trigger is let go. Frame: z up along the rotor's
axis (towards the barrels), z = 0 the base's top; stator angle from +x.

v2: built from the head's own parts, so that what passes here goes into the gun as it is. Only the base,
the trigger lever and the bevel box are the bench's; everything else is a part of the final head:

    shaft housing  printed flanged tube with the rotor shaft's two 608s; the stack sits on the upper one's
                   inner race (the pushers push the rotor down). The gun bolts the same part to its frame.
    rotor stack .. on a Ø8 steel shaft with a flat, each part keyed by a D bore, hub on hub: stop disc
                   (16 notches), 75-tooth gear, rotor (both cam arcs, ramps lofted). All three for the gun.
    quarter block  one of the head's four core blocks (stator 0..90 deg, R30..86, ports at 11.25 + k * 22.5),
                   with its guide plate: charge core on R60, vent core on R42, pins down, as in bench B; a
                   supply gallery over the charge cores (G1/8 on top at 45 deg), each pilot on its own G1/8
                   on top and across to its vent core, each vent core's exhaust inwards and down through the
                   plate. Three M4 at R78 through block and plate; the gun takes four of each.
    pushers ...... bench B's: Ø3 pin in a printed follower, set by a grub screw, return spring.
    stop ......... a steel pin Ø4 drops into the stop disc's notches and stops the rotor on the step, every
                   pusher off the ramps; here it sits in a lever on the base pressed by hand (the bench's).
    slip clutch .. the layshaft is an M8 stud; the 15-tooth pinion is free on it, squeezed between two
                   rubber washers by a spring and a nut. Stopped by the pin, the rotor holds and the crank
                   slips (SLIP x the rotor's torque); the nut sets it.
    drive ........ a 1:1 bevel pair (ratling.params, the selector's) on top of the layshaft turns it from a
                   horizontal crank shaft in two 608s. The bench's bevel box holds those and the layshaft's
                   upper 608; the gun's frame will hold the same bearings.

This replaces concept A's dog clutch and ratchet detent: the detent is far too weak to finish a step
against the pushers (docs/rotor.md), and a dog clutch that only lets go on a step either jams or lets go
anywhere.

19 barrels: ROTOR_N = 19 before exec. The rotor and stop disc are the 19's, the bench's block is still four ports
(75.8 deg). The gun's head takes BLOCK_PORTS blocks round the stator: four quarters at 16, three blocks of five and
the bench's block of four at 19 (19 is prime), three posts in each, a supply fitting on each. GUN holds that head
for rear_frame.py; exports/rotor_bench19/ has every block. The drive, housing, stop and gears are the 16's.

v1 (kept below for history): a three-port sector block with the shaft's upper 608 in its hub, the shaft's
lower 608 in the base, the crank arm straight on the layshaft's top. Replaced because none of it fit the
gun's head.

Use: docs/test-plan.md, "Mitrailleuse head, bench C".
Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/rotor_bench.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/rotor_bench/ (STEP, STL, FCStd).
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
try:
    ROTOR_BENCH_LIBRARY
except NameError:
    ROTOR_BENCH_LIBRARY = False
try:
    ROTOR_N                          # barrels: 16 or 19
except NameError:
    ROTOR_N = 16
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
import ratling.params as P
for _m in (G, FV, GR, P):
    importlib.reload(_m)

_rt = {"__name__": "rotor_timing"}
exec(open(os.path.join(REPO, "mitrailleuse", "rotor_timing.py"), encoding="utf-8").read(), _rt)
HB = {"REPO": REPO, "HEAD_BENCH_LIBRARY": True}
exec(open(os.path.join(REPO, "mitrailleuse", "head_bench.py"), encoding="utf-8").read(), HB)

NAME = "rotor_bench" if ROTOR_N == 16 else "rotor_bench%d" % ROTOR_N
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
O = V(0, 0, 0)
cyl = G.cyl

# ---------------------------------------------------------------- parameters
N = ROTOR_N
P_ANG = 360.0 / N
BLOCK_PORTS = {16: (4, 4, 4, 4), 19: (5, 5, 5, 4)}[N]   # the gun's blocks round the stator from 0 deg, ports each
PORTS = (0, 1, 2, 3)                 # stator angles (j + 0.5) * P_ANG: the bench's block of four
QUARTER = (0.0, len(PORTS) * P_ANG)  # its sector (a quarter at 16)
BLOCK_R = (30.0, 86.0)               # quarter block: inner, outer R
VENT_R, CHARGE_R = _rt["VENT_R"], _rt["CHARGE_R"]
TOP_C, TOP_V = _rt["cams"](N)["top_c"], _rt["VENT_TOP"]
TRAVEL, RAMP = _rt["TRAVEL"], _rt["RAMP"]
STRIP_W = 10.0
RISER_DR = 7.0                       # pilot riser outside the charge core
Z_SUP, Z_PIL, Z_LINK, Z_EXH = 20.0, 25.0, 3.2, 3.0
EXH_R = 35.0                         # exhaust goes in to here, then down through the plate
SUP_IN_ANG = 2 * P_ANG               # supply inlet between ports 1 and 2 of every block
POST_R, POST_D = 78.0, 12.0
POST_ANGS = tuple(k * P_ANG for k in (1, 2, 3))   # between a block's first four ports

SHAFT_D = 8.0
BRG = (22.0, 8.0, 7.0)               # 608: OD, bore, width
D_FLAT = 7.2                         # the shaft's flat: 0.8 off
HOUSING = (32.0, 60.0, 4.0, 34.0)    # shaft housing: tube Ø, flange Ø, flange thickness, height
HOUSING_BOLT = (24.0, (90.0, 210.0, 330.0))
SHIM = 1.0                           # 8 x 12 shim between a 608's inner race and what turns on it
Z_BOSS = 9.0                         # the layshaft's base boss: its lower 608's top
STOP = (30.0, 25.0, 6.0)             # stop disc: rim R, notch floor R, thickness
NOTCH_W = 4.8                        # mm at the pin's radius: the pin + room to drop in at full speed
PIN = (4.0, 27.0, 33.0)              # stop pin Ø, centre R in a notch, centre R on the rim
LEVER = (30.0, 70.0, 8.0, 6.0)       # pivot to pin, pivot to trigger, width, thickness
GEAR_M, GEAR_Z = 1.75, (15, 75)
GEAR_FACE = 8.0
ROTOR_R, ROTOR_T = 70.0, 8.0
BLOCK_T, PLATE_T = 34.0, 6.0
SPRING_REST, FOLLOWER_H = HB["SPRING_REST"], HB["FOLLOWER_H"]
CRANK_R = _rt["CRANK_R"]
SLIP = 1.3                           # slip torque over the most the rotor needs
MU_RUBBER = 0.4
SLIP_WASHER = (9.0, 22.0)            # rubber washers: ID, OD
SLIP_SPRING = (14.0, 12.0)           # its spring: OD, length
BEVEL_BORE = 8.15
BOX_W = 32.0                         # bevel box, along y

# ---------------------------------------------------------------- levels
z_hs = HOUSING[3]                                     # housing top = upper 608's top
z_stop0 = z_hs + SHIM                                 # stop disc and its hub, flat bottom
z_gear0 = z_stop0 + 10.0                              # gear teeth flush with its hub's bottom
z_rotor0 = z_gear0 + GEAR_FACE + 6.0
z_cam0 = z_rotor0 + ROTOR_T                           # followers' feet at rest
z_ftop = z_cam0 + FOLLOWER_H
z_plate0 = z_ftop + SPRING_REST
z_block0 = z_plate0 + PLATE_T
z_top = z_block0 + BLOCK_T
c_gear = GEAR_M * sum(GEAR_Z) / 2                     # layshaft distance
LAY = (-c_gear, 0.0)                                  # layshaft at 180 deg
z_lev1 = z_hs                                         # the lever just under the stop disc
z_lev0 = z_lev1 - LEVER[3]


def polar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def rod(d, a, b):
    a, b = V(*a), V(*b)
    return Part.makeCylinder(d / 2, (b - a).Length, a, b - a)


def sector(r0, r1, z0, z1, a0, a1):
    s = Part.makeCylinder(r1, z1 - z0, V(0, 0, z0), Z, a1 - a0)
    if r0 > 0:
        s = s.cut(Part.makeCylinder(r0, z1 - z0 + 2, V(0, 0, z0 - 1), Z, a1 - a0))
    s.rotate(V(0, 0, 0), Z, a0)
    return s


def d_tool(z0, z1, play=0.1):
    """Cutter for a D bore: Ø8 + play with the flat at D_FLAT from the far side."""
    c = cyl(SHAFT_D + play, z0, z1)
    keep = Part.makeBox(D_FLAT + play / 2, SHAFT_D + 2, z1 - z0 + 2, V(-SHAFT_D / 2 - play / 2, -SHAFT_D / 2 - 1, z0 - 1))
    return c.common(keep)


def spur(z, z0, phase=0.0):
    pts = GR.tooth_outline(z, GEAR_M, 1.0, 0.15)
    w = Part.makePolygon([V(x, y, 0) for x, y in pts] + [V(pts[0][0], pts[0][1], 0)])
    g = Part.Face(w).extrude(V(0, 0, GEAR_FACE))
    g.rotate(V(0, 0, 0), Z, phase)
    g.translate(V(0, 0, z0))
    return g


def ring(od, idia, a, b):
    """Bearing or washer between points a and b."""
    return rod(od, a, b).cut(rod(idia, a, b))


# ---------------------------------------------------------------- shaft housing
housing = cyl(HOUSING[0], 0, z_hs).fuse(cyl(HOUSING[1], 0, HOUSING[2]))
housing = housing.cut(cyl(BRG[0] + 0.2, -1, BRG[2])).cut(cyl(BRG[0] + 0.2, z_hs - BRG[2], z_hs + 1))
housing = housing.cut(cyl(14.0, -1, z_hs + 1))        # clears the inner races
hb_xy = [polar(HOUSING_BOLT[0], a) for a in HOUSING_BOLT[1]]
for p in hb_xy:
    housing = housing.cut(cyl(4.5, -1, HOUSING[2] + 1, *p))
housing = housing.removeSplitter()

# ---------------------------------------------------------------- rotor (x -> rotor angle x * P_ANG)
ang = lambda x: x * P_ANG


def ramp(r, top, x0, x1, n=12):
    """Lofted ramp on the circle r between port x0 and x1 (pitches), heights from rotor_timing.height()."""
    wires = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        h = max(0.02, TRAVEL * _rt["height"](x, top))
        a = math.radians(ang(x))
        c, s = math.cos(a), math.sin(a)
        pts = [V((r - STRIP_W / 2) * c, (r - STRIP_W / 2) * s, z_cam0 - 1),
               V((r + STRIP_W / 2) * c, (r + STRIP_W / 2) * s, z_cam0 - 1),
               V((r + STRIP_W / 2) * c, (r + STRIP_W / 2) * s, z_cam0 + h),
               V((r - STRIP_W / 2) * c, (r - STRIP_W / 2) * s, z_cam0 + h)]
        wires.append(Part.makePolygon(pts + [pts[0]]))
    return Part.makeLoft(wires, True, True)


rotor = cyl(2 * ROTOR_R, z_rotor0, z_cam0).fuse(cyl(20.0, z_rotor0 - 0.0, z_cam0))
cams = []
for r, (a, b) in ((CHARGE_R, TOP_C), (VENT_R, TOP_V)):
    cams.append(ramp(r, (a, b), a - RAMP, a))
    cams.append(sector(r - STRIP_W / 2, r + STRIP_W / 2, z_cam0 - 1, z_cam0 + TRAVEL, ang(a), ang(b)))
    cams.append(ramp(r, (a, b), b, b + RAMP))
rotor = rotor.fuse(G.fuse_all(cams)).removeSplitter().cut(d_tool(z_rotor0 - 1, z_cam0 + 1))

# stop disc: notches whose low-angle face stops the pin when the ports sit at x = j + 0.5
pin_ang = 270.0
d_pin = math.degrees((PIN[0] / 2) / PIN[1])
w_notch = math.degrees(NOTCH_W / PIN[1])
stop_disc = cyl(2 * STOP[0], z_stop0, z_stop0 + STOP[2]).fuse(cyl(16.0, z_stop0, z_gear0))
for i in range(N):
    lo = pin_ang - d_pin + i * P_ANG                 # the trailing (low) face catches the pin
    stop_disc = stop_disc.cut(sector(STOP[1], STOP[0] + 1, z_stop0 - 1, z_stop0 + STOP[2] + 1, lo, lo + w_notch))
stop_disc = stop_disc.cut(d_tool(z_stop0 - 1, z_gear0 + 1)).removeSplitter()

gear = spur(GEAR_Z[1], z_gear0).fuse(cyl(24.0, z_gear0, z_rotor0)).cut(d_tool(z_gear0 - 1, z_rotor0 + 1))
pinion = spur(GEAR_Z[0], z_gear0).cut(cyl(8.4, z_gear0 - 1, z_gear0 + GEAR_FACE + 1))
pinion.translate(V(LAY[0], LAY[1], 0))


# ---------------------------------------------------------------- quarter block, guide plate
def core_hole(x, y, gland):
    s = G.fuse_all([cyl(HB["CAV_D"], -1, HB["CAV_TOP"], x, y),
                    cyl(HB["TAP_5V1_D"], HB["CAV_TOP"] - 0.01, HB["z_tap1"], x, y),
                    Part.makeCone(HB["CORE_SEAT"][0] / 2, HB["CORE_SEAT"][1] / 2, HB["CORE_SEAT"][2], V(x, y, HB["z_tap1"])),
                    cyl(HB["CORE_BORE_D"], HB["z_seat1"] - 0.01, HB["z_bore1"], x, y)])
    if gland:
        s = s.fuse(cyl(HB["GLAND"][0], -1, HB["GLAND"][1], x, y))
    return s


def g18(x, y):
    return cyl(HB["G18_TAP_D"], BLOCK_T - HB["G18_TAP_DEPTH"], BLOCK_T + 1, x, y)


port_ang = lambda j: (j + 0.5) * P_ANG
CH, SUP, EXH = HB["CH_D"], HB["SUP_D"], HB["EXH_D"]
zb1 = HB["z_bore1"]


def make_block(n):
    """A block of n ports, stator 0 .. n x P_ANG, and its guide plate (block's bottom at z = 0)."""
    ports = tuple(range(n))
    net = {"supply": [], "exhaust": []}
    pil, holes = {}, []
    for j in ports:
        a = port_ang(j)
        c, v, rr = polar(CHARGE_R, a), polar(VENT_R, a), polar(CHARGE_R + RISER_DR, a)
        holes += [core_hole(c[0], c[1], True), core_hole(v[0], v[1], False)]
        net["supply"].append(cyl(HB["CORE_BORE_D"], zb1 - 0.1, Z_SUP + SUP / 2, *c))
        pil[j] = G.fuse_all([rod(CH, polar(CHARGE_R + 1.5, a) + (Z_LINK,), rr + (Z_LINK,)),
                             cyl(CH, Z_LINK - CH / 2, BLOCK_T - HB["G18_TAP_DEPTH"] + 0.5, *rr), g18(*rr),
                             rod(CH, rr + (Z_PIL,), v + (Z_PIL,)),
                             cyl(HB["CORE_BORE_D"], zb1 - 0.1, Z_PIL + CH / 2, *v)])
        net["exhaust"].append(G.fuse_all([rod(EXH, v + (Z_EXH,), polar(EXH_R, a) + (Z_EXH,)),
                                          cyl(EXH, -1, Z_EXH + EXH / 2, *polar(EXH_R, a))]))
    for j0, j1 in zip(ports, ports[1:]):
        net["supply"].append(rod(SUP, polar(CHARGE_R, port_ang(j0)) + (Z_SUP,), polar(CHARGE_R, port_ang(j1)) + (Z_SUP,)))
    sup = polar(CHARGE_R * math.cos(math.radians(P_ANG / 2)), SUP_IN_ANG)
    net["supply"] += [cyl(SUP, Z_SUP - SUP / 2, BLOCK_T - HB["G18_TAP_DEPTH"] + 0.5, *sup), g18(*sup)]
    net["supply"] = G.fuse_all(net["supply"])
    net["exhaust"] = G.fuse_all(net["exhaust"])
    posts = [polar(POST_R, a) for a in POST_ANGS]
    tool = lambda d, z0, z1: G.fuse_all([cyl(d, z0, z1, *p) for p in posts])
    sec = (0.0, n * P_ANG)
    blk = sector(BLOCK_R[0], BLOCK_R[1], 0, BLOCK_T, *sec)
    for s in holes + [net["supply"], net["exhaust"]] + list(pil.values()):
        blk = blk.cut(s)
    blk = blk.cut(tool(4.5, -1, BLOCK_T + 1))
    pl = sector(BLOCK_R[0], BLOCK_R[1], -PLATE_T, 0, *sec)
    for j in ports:
        for r in (CHARGE_R, VENT_R):
            pl = pl.cut(cyl(HB["PIN_HOLE"], -PLATE_T - 1, 1, *polar(r, port_ang(j))))
        pl = pl.cut(cyl(EXH, -PLATE_T - 1, 1, *polar(EXH_R, port_ang(j))))
    pl = pl.cut(tool(4.5, -PLATE_T - 1, 1))
    return {"n": n, "ports": ports, "sector": sec, "blk": blk, "pl": pl, "net": net, "pil": pil, "holes": holes,
            "posts_xy": posts, "sup_in": sup, "bolt_tool": tool}


BLOCKS = {n: make_block(n) for n in sorted(set(BLOCK_PORTS) | {len(PORTS)})}
_b = BLOCKS[len(PORTS)]                                  # the bench's block: one of the gun's
net, pil, holes, posts_xy, sup_in, bolt_tool = (_b[k] for k in ("net", "pil", "holes", "posts_xy", "sup_in", "bolt_tool"))
blk = _b["blk"]
block = blk.translated(V(0, 0, z_block0))
plate = _b["pl"].translated(V(0, 0, z_block0))


# ---------------------------------------------------------------- pushers at rest (rotor parked, psi = 0)
def lift(x, top):
    return TRAVEL * _rt["height"](x, top)


def follower(x, y, up):
    r = HB["FOLLOWER_D"] / 2
    z0 = z_cam0 + up
    body = cyl(HB["FOLLOWER_D"], z0 + r, z0 + FOLLOWER_H, x, y)
    foot = Part.makeSphere(r, V(x, y, z0 + r)).common(Part.makeBox(2 * r, 2 * r, r, V(x - r, y - r, z0)))
    f = body.fuse(foot).removeSplitter()
    f = f.cut(cyl(HB["PIN_D"] + 0.1, z0 + FOLLOWER_H - HB["PIN_IN_FOLLOWER"], z0 + FOLLOWER_H + 1, x, y))
    return f.cut(rod(2.6, (x, y, z0 + FOLLOWER_H - 2.5), (x + r + 1, y, z0 + FOLLOWER_H - 2.5)))


z_core_pin = z_block0 + HB["z_pin"]


def pushers(ports):
    """Followers, pins and return springs of these ports, the rotor parked at psi = 0."""
    followers, pins, springs = [], [], []
    for j in ports:
        for r, top in ((CHARGE_R, TOP_C), (VENT_R, TOP_V)):
            x_port = (j + 0.5 + N / 2) % N - N / 2          # the rotor is round: the ports past 180 deg come before 0
            up = lift(x_port, top)
            xy = polar(r, port_ang(j))
            followers.append(follower(xy[0], xy[1], up))
            pins.append(cyl(HB["PIN_D"], z_ftop + up - HB["PIN_IN_FOLLOWER"], z_core_pin - HB["REST_GAP"] + up, *xy))
            s = G.spring(0, z_ftop + up, z_plate0, HB["SPRING"][0], HB["SPRING"][1], 4)
            s.translate(V(xy[0], xy[1], 0))
            springs.append(s)
    return G.fuse_all(followers), G.fuse_all(pins), G.fuse_all(springs)


followers, pins, springs = pushers(PORTS)

# ---------------------------------------------------------------- layshaft, slip clutch
z_p1 = z_gear0 + GEAR_FACE
sl = [z_gear0 - 1.5 - 5.0, z_gear0 - 1.5]                                       # lock nut under the pinion
z_ss = (z_p1 + 2.5, z_p1 + 2.5 + SLIP_SPRING[1])                               # spring over it
z_nut1 = z_ss[1] + 1.0 + 6.5                                                   # top of the nut that sets it
slip = G.fuse_all([cyl(12.0, Z_BOSS, sl[0], *LAY).cut(cyl(8.2, Z_BOSS - 1, sl[0] + 1, *LAY)),   # spacer tube
                   cyl(13.0, sl[0], sl[1], *LAY),
                   cyl(SLIP_WASHER[1], sl[1], z_gear0, *LAY),
                   cyl(SLIP_WASHER[1], z_p1, z_p1 + 1.5, *LAY),
                   cyl(16.0, z_p1 + 1.5, z_ss[0], *LAY),
                   cyl(SLIP_SPRING[0], z_ss[0], z_ss[1], *LAY).cut(cyl(SLIP_SPRING[0] - 4, z_ss[0] - 1, z_ss[1] + 1, *LAY)),
                   cyl(16.0, z_ss[1], z_ss[1] + 1.0, *LAY), cyl(13.0, z_ss[1] + 1.0, z_nut1, *LAY)])
z_lb = z_nut1 + 5.0                                     # the layshaft's upper 608, in the bevel box's floor
z_floor = (z_lb - 2.0, z_lb + BRG[2])

# ---------------------------------------------------------------- bevel pair, crank
def bevel(phase=0.0):
    """The selector's printed bevel gear (ratling.params), apex at the origin, hub towards +Z, grub screw."""
    g, info = GR.bevel_gear(P.BEVEL_MODULE, P.BEVEL_TEETH, P.BEVEL_FACE, P.BEVEL_HUB_D, P.BEVEL_HUB_L, BEVEL_BORE,
                            P.BEVEL_BACKLASH, phase_deg=phase)
    z_set = info["big_end_z"] + P.BEVEL_HUB_L / 2
    return g.cut(rod(2.5, (0, 0, z_set), (P.BEVEL_HUB_D, 0, z_set))).removeSplitter(), info


bevel_print, BI = bevel()
z_apex = z_floor[1] + 0.5 + BI["mount"]                 # layshaft gear's hub on a shim on the 608
bev_lay = bevel_print.copy()
bev_lay.rotate(O, X, 180)
bev_lay.translate(V(LAY[0], LAY[1], z_apex))
bev_crank = bevel(180.0 / P.BEVEL_TEETH)[0]             # half a tooth: the teeth fall into the gaps
bev_crank.rotate(O, Y, -90)
bev_crank.translate(V(LAY[0], LAY[1], z_apex))
x_hub = LAY[0] - BI["mount"]                            # crank gear's hub back
x_b1 = (x_hub - 0.5 - BRG[2], x_hub - 0.5)              # inner crank 608, from the gear's side
x_w1 = (x_b1[0] - 5.0, x_b1[1])
x_w2 = (x_w1[0] - 22.0, x_w1[0] - 11.0)
x_b2 = (x_w2[0], x_w2[0] + BRG[2])                      # outer crank 608, from outside
x_arm = (x_w2[0] - 0.5 - 8.0, x_w2[0] - 0.5)

z_knob = z_apex - CRANK_R
crank = G.fuse_all([Part.makeBox(8.0, 18.0, CRANK_R, V(x_arm[0], -9.0, z_knob)),
                    rod(18.0, (x_arm[0], 0, z_apex), (x_arm[1], 0, z_apex)),
                    rod(18.0, (x_arm[0], 0, z_knob), (x_arm[1], 0, z_knob)),
                    rod(16.0, (x_arm[0] - 45.0, 0, z_knob), (x_arm[1] - 1.0, 0, z_knob))])     # printed: arm and knob
xm = (x_arm[0] + x_arm[1]) / 2
crank = crank.cut(rod(BEVEL_BORE, (x_arm[0] - 1, 0, z_apex), (x_arm[1] + 1, 0, z_apex))).cut(
    rod(2.5, (xm, 0, z_apex), (xm, 0, z_apex + 10)))

# bevel box (the bench's): floor with the layshaft's upper 608, two walls with the crank shaft's 608s,
# two columns to the base. A profile in x-z, extruded along y: printed on its side.
y0b = -BOX_W / 2
box = G.fuse_all([Part.makeBox(LAY[0] + 17.0 - x_w2[0], BOX_W, z_floor[1] - z_floor[0], V(x_w2[0], y0b, z_floor[0])),
                  Part.makeBox(x_w1[1] - x_w1[0], BOX_W, z_apex + 18.0 - z_floor[0], V(x_w1[0], y0b, z_floor[0])),
                  Part.makeBox(x_w2[1] - x_w2[0], BOX_W, z_apex + 18.0 - z_floor[0], V(x_w2[0], y0b, z_floor[0]))])
cols_x = ((x_w2[0] + 10.0, x_w2[0] + 22.0), (LAY[0] - 33.0, LAY[0] - 21.0))
for c0, c1 in cols_x:
    box = box.fuse(Part.makeBox(c1 - c0, BOX_W, z_floor[0], V(c0, y0b, 0)))
box = box.cut(cyl(BRG[0] + 0.2, z_lb, z_floor[1] + 1, *LAY)).cut(cyl(16.0, z_floor[0] - 1, z_lb + 0.01, *LAY))
box = box.cut(rod(BRG[0] + 0.2, (x_b1[0], 0, z_apex), (x_b1[1] + 1, 0, z_apex))).cut(
    rod(BRG[0] + 0.2, (x_b2[0] - 1, 0, z_apex), (x_b2[1], 0, z_apex)))
box = box.cut(rod(12.0, (x_w2[0] - 1, 0, z_apex), (x_w1[1] + 1, 0, z_apex)))
col_bolts = [((c0 + c1) / 2, 0.0) for c0, c1 in cols_x]
for p in col_bolts:
    box = box.cut(cyl(3.6, -1, 16.0, *p))
box = box.removeSplitter()

# ---------------------------------------------------------------- stop lever, trigger
pin_xy = polar(PIN[1], pin_ang)                  # (0, -27) engaged
pivot = (pin_xy[0] + LEVER[0], pin_xy[1])
lever = G.fuse_all([Part.makeBox(LEVER[0] + LEVER[1] + 6, LEVER[2], LEVER[3],
                                 V(pin_xy[0] - 4, pin_xy[1] - LEVER[2] / 2, z_lev0)),
                    cyl(12.0, z_lev0, z_lev1, *pivot), cyl(10.0, z_lev0, z_lev1, *pin_xy)])
lever = lever.cut(cyl(4.3, z_lev0 - 1, z_lev1 + 1, *pivot)).cut(cyl(PIN[0] - 0.1, z_lev0 - 1, z_lev1 + 1, *pin_xy))
stop_pin = cyl(PIN[0], z_lev0, z_stop0 + STOP[2], *pin_xy)
trig_xy = (pivot[0] + LEVER[1], pivot[1])
lever = lever.fuse(Part.makeBox(10, 4, 22, V(trig_xy[0] - 5, trig_xy[1] - LEVER[2] / 2 - 4, z_lev0)))   # finger pad

# ---------------------------------------------------------------- base (the bench's)
X0, X1, Y0, Y1 = x_w2[0] + 8.0, trig_xy[0] + 10.0, -45.0, 86.0
base = Part.makeBox(X1 - X0, Y1 - Y0, 6.0, V(X0, Y0, -6.0))
base = base.cut(cyl(16.0, -7, 1))                                               # the shaft's e-clip
for p in hb_xy:                                                                 # housing: M4, nuts below
    base = base.cut(cyl(4.5, -7, 1, *p)).cut(G.hex_prism(7.2, -7, -3.0, *p))
base = base.fuse(cyl(32.0, 0, Z_BOSS, *LAY)).cut(cyl(BRG[0] + 0.2, Z_BOSS - BRG[2], Z_BOSS + 1, *LAY)).cut(
    cyl(12.0, -7, 1, *LAY))
for p in posts_xy:
    base = base.fuse(cyl(POST_D, 0, z_plate0, *p))
base = base.cut(bolt_tool(3.6, z_plate0 - 16, z_plate0 + 1))
base = base.fuse(cyl(12.0, 0, z_lev0 - 0.5, *pivot)).cut(cyl(3.4, z_lev0 - 16, z_lev0, *pivot))   # pivot: M4 from the top
# spring post: the lever's spring pushes the trigger towards -y, the pin into the disc
sp_xy = (pivot[0] + 40.0, pivot[1] + LEVER[2] / 2 + 14.0)
base = base.fuse(Part.makeBox(10, 6, z_lev1 + 4, V(sp_xy[0] - 5, sp_xy[1], 0)))
for p in col_bolts:                                                             # bevel box: M4 from below
    base = base.cut(cyl(4.5, -7, 1, *p)).cut(cyl(8.0, -7, -3.0, *p))
base = base.removeSplitter()

# ---------------------------------------------------------------- bought / steel, for the picture
shaft = cyl(SHAFT_D, -2.0, z_cam0 + 1.0)
layshaft = cyl(8.0, 2.0, z_apex - BI["small_end_z"] - 1.0, *LAY)
crank_shaft = rod(SHAFT_D, (x_arm[0] + 1.0, 0, z_apex), (x_hub + BI["mount"] - BI["big_end_z"] - 2.0, 0, z_apex))
brgs = G.fuse_all([cyl(BRG[0], 0, BRG[2]), cyl(BRG[0], z_hs - BRG[2], z_hs),
                   cyl(BRG[0], Z_BOSS - BRG[2], Z_BOSS, *LAY), cyl(BRG[0], z_lb, z_lb + BRG[2], *LAY)]).cut(
    G.fuse_all([cyl(BRG[1], -1, z_hs + 1), cyl(BRG[1], -1, z_lb + 9, *LAY)]))
brgs = brgs.fuse(ring(BRG[0], BRG[1], (x_b1[0], 0, z_apex), (x_b1[1], 0, z_apex))).fuse(
    ring(BRG[0], BRG[1], (x_b2[0], 0, z_apex), (x_b2[1], 0, z_apex)))
def valve_cores(ports):
    cores = []
    for j in ports:
        for r in (CHARGE_R, VENT_R):
            x, y = polar(r, port_ang(j))
            zc = z_block0
            cores.append(G.fuse_all([cyl(HB["CORE_THREAD_D"], zc + HB["CAV_TOP"], zc + HB["z_tap1"], x, y),
                                     cyl(4.4, zc + HB["z_tap1"], zc + HB["z_seat1"] + 1, x, y),
                                     cyl(2.6, zc + HB["z_seat1"] + 1, zc + zb1 - 1, x, y),
                                     cyl(1.0, zc + HB["z_pin"], zc + HB["CAV_TOP"], x, y)]))
    return G.fuse_all(cores)


def push_ins(ports, sup_xy):
    return G.fuse_all([G.push_in_fitting(xy[0], xy[1], z_top)
                       for xy in [polar(CHARGE_R + RISER_DR, port_ang(j)) for j in ports] + list(sup_xy)])


cores = valve_cores(PORTS)
fittings = push_ins(PORTS, [sup_in])


# ---------------------------------------------------------------- the gun's head: BLOCK_PORTS blocks round the stator
def turn_xy(p, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


GUN = {"blocks": [], "guide_plates": [], "post_xy": [], "sup_xy": [], "block_at": []}
_j0 = 0
for _n in BLOCK_PORTS:
    _a = _j0 * P_ANG
    GUN["blocks"].append(BLOCKS[_n]["blk"].translated(V(0, 0, z_block0)).rotated(O, Z, _a))
    GUN["guide_plates"].append(BLOCKS[_n]["pl"].translated(V(0, 0, z_block0)).rotated(O, Z, _a))
    GUN["post_xy"] += [turn_xy(p, _a) for p in BLOCKS[_n]["posts_xy"]]
    GUN["sup_xy"].append(turn_xy(BLOCKS[_n]["sup_in"], _a))
    GUN["block_at"].append((_n, _a))
    _j0 += _n
GUN["blocks"], GUN["guide_plates"] = G.fuse_all(GUN["blocks"]), G.fuse_all(GUN["guide_plates"])
GUN["followers"], GUN["pins"], GUN["springs"] = pushers(range(N))
GUN["cores"] = valve_cores(range(N))
GUN["fittings"] = push_ins(range(N), GUN["sup_xy"])

# ---------------------------------------------------------------- checks
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
wall = lambda a, b: a.distToShape(b)[0]
pil_all = G.fuse_all(list(pil.values()))
for _n, _bk in BLOCKS.items():
    _pa = G.fuse_all(list(_bk["pil"].values()))
    _ns = _bk["net"]
    d_sp, d_se, d_pe = wall(_ns["supply"], _pa), wall(_ns["supply"], _ns["exhaust"]), wall(_pa, _ns["exhaust"])
    d_pp = min(wall(_bk["pil"][a], _bk["pil"][b]) for a, b in zip(_bk["ports"], _bk["ports"][1:]))
    check(min(d_sp, d_se, d_pe, d_pp) >= 1.2, "block of %d: supply / pilot / exhaust / pilot-to-pilot walls >= %.1f mm"
          " (%.1f / %.1f / %.1f / %.1f)" % (_n, min(d_sp, d_se, d_pe, d_pp), d_sp, d_se, d_pe, d_pp))
    inside = G.fuse_all([_ns["supply"], _ns["exhaust"], _pa] + _bk["holes"])
    d_bolt = wall(_bk["bolt_tool"](4.5, -1, BLOCK_T + 1), inside)
    check(d_bolt >= 1.2, "block of %d: bolts %.1f mm clear of every channel and core" % (_n, d_bolt))
    d_core = min(wall(_bk["holes"][2 * k + i], _bk["holes"][2 * k + 2 + i]) for k in range(_n - 1) for i in (0, 1))
    check(d_core >= 2.0, "block of %d: %.1f mm between the next ports' core"
          " holes (vent circle R%.0f, pitch %.1f mm)" % (_n, d_core, VENT_R, 2 * VENT_R * math.sin(math.radians(P_ANG / 2))))
    outside = cyl(2 * BLOCK_R[1] + 20, 0.5, BLOCK_T - 0.5).cut(sector(BLOCK_R[0], BLOCK_R[1], -1, BLOCK_T + 1, *_bk["sector"]))
    d_side = wall(outside, inside)
    check(d_side >= 2.0, "block of %d (%.1f deg): every channel and core %.1f mm inside its sides and R%.0f..%.0f"
          % (_n, _bk["sector"][1], d_side, BLOCK_R[0], BLOCK_R[1]))
gap_f = 2 * VENT_R * math.sin(math.radians(P_ANG / 2)) - max(HB["FOLLOWER_D"], HB["SPRING"][0])
check(gap_f >= 2.0, "pushers on the vent circle: followers Ø%.0f and springs Ø%.0f %.1f mm apart"
      % (HB["FOLLOWER_D"], HB["SPRING"][0], gap_f))
check(sum(BLOCK_PORTS) == N and abs(sum(n for n, _ in GUN["block_at"]) * P_ANG - 360.0) < 1e-6,
      "the gun's head: blocks of %s ports, %d in all, round the stator; %d posts"
      % (" + ".join(str(n) for n in BLOCK_PORTS), N, len(GUN["post_xy"])))
ok_links = True
for j in PORTS:
    a = port_ang(j)
    c, v = polar(CHARGE_R, a), polar(VENT_R, a)
    ok_links &= net["supply"].common(cyl(HB["CORE_BORE_D"], HB["z_seat1"], zb1, *c)).Volume > 0.5
    ok_links &= pil[j].common(cyl(HB["CAV_D"], HB["GLAND"][1], HB["CAV_TOP"], *c)).Volume > 0.5
    ok_links &= pil[j].common(cyl(HB["CORE_BORE_D"], HB["z_seat1"], zb1, *v)).Volume > 0.5
    ok_links &= net["exhaust"].common(cyl(HB["CAV_D"], 0, HB["CAV_TOP"], *v)).Volume > 0.5
check(ok_links, "block: per port, supply -> charge core, charge cavity -> pilot -> vent core, vent cavity -> exhaust")
printed = tuple(("block of %d" % n, bk["blk"]) for n, bk in BLOCKS.items()) + tuple(
    ("guide plate of %d" % n, bk["pl"]) for n, bk in BLOCKS.items()) + ( ("rotor", rotor), ("gear", gear), ("pinion", pinion),
           ("stop disc", stop_disc), ("housing", housing), ("bevel", bevel_print), ("crank", crank),
           ("lever", lever), ("base", base), ("bevel box", box))
bad = [nm for nm, s in printed if not G.single_solid(s)]
check(not bad, "every printed part one solid%s" % (" (not: " + ", ".join(bad) + ")" if bad else ""))
still = (("base", base), ("housing", housing), ("plate", plate), ("lever", lever), ("bevel box", box),
         ("bearings", brgs), ("stop pin", stop_pin))
turning = (("rotor", rotor, ()), ("gear", gear, ("pinion",)), ("stop disc", stop_disc, ("stop pin",)),
           ("pinion", pinion, ("gear",)), ("slip", slip, ("bearings",)), ("bevel L", bev_lay, ("bevel C", "bearings")),
           ("bevel C", bev_crank, ("bevel L", "bearings")), ("crank", crank, ("bearings",)))
others = dict(still)
others.update({"rotor": rotor, "gear": gear, "pinion": pinion, "bevel L": bev_lay, "bevel C": bev_crank})
clash = []
for nm, s, ok_with in turning:
    for on, o in others.items():
        if on != nm and on not in ok_with and s.common(o).Volume > 0.5:
            clash.append(nm + "/" + on)
check(not clash, "nothing turning runs into a fixed part or another turning one%s"
      % (" (" + ", ".join(sorted(set(clash))) + ")" if clash else ""))
d_post = min(math.hypot(*p) for p in posts_xy) - POST_D / 2 - ROTOR_R
d_lay = c_gear - SLIP_SPRING[0] / 2 - ROTOR_R
check(d_post >= 1.5 and d_lay >= 1.5, "rotor R%.0f: %.1f mm to the posts, %.1f to the slip clutch's spring"
      % (ROTOR_R, d_post, d_lay))
d_knob = z_knob - 8.0
check(d_knob > 0 and crank.common(box).Volume < 0.01, "crank R%.0f on a shaft at z %.1f: knob %.0f mm over the base"
      " at the bottom" % (CRANK_R, z_apex, d_knob))
mesh = gear.common(pinion).Volume
check(mesh < 1.0, "gears %d / %d m%.2f mesh at %.2f mm, no overlap (%.2f mm3)" % (GEAR_Z + (GEAR_M, c_gear, mesh)))
bmesh = bev_lay.common(bev_crank).Volume
check(bmesh < 1.0, "bevels %d / %d m%.0f, apex on the layshaft at z %.1f, no overlap (%.2f mm3)"
      % (P.BEVEL_TEETH, P.BEVEL_TEETH, P.BEVEL_MODULE, z_apex, bmesh))
# stops: rotor parked at psi = k steps, each port at x = j + 0.5 - k
rows, ok_stops = [], True
for k in range(5):
    cells = []
    for j in PORTS:
        x = j + 0.5 - k
        pc = max(0.0, lift(x, TOP_C) - HB["REST_GAP"])
        pv = max(0.0, lift(x, TOP_V) - HB["REST_GAP"])
        ramp_on = 0 < _rt["height"](x, TOP_C) < 1 or 0 < _rt["height"](x, TOP_V) < 1
        ok_stops &= not ramp_on and (pc == 0 or _rt["PIN_OPEN"] <= pc <= _rt["PIN_MAX"]) and (
            pv == 0 or _rt["PIN_OPEN"] <= pv <= _rt["PIN_MAX"])
        cells.append("%s" % ("заряд" if pc else ("СБРОС" if pv else "-")))
    rows.append("    step %d: ports 0/1/2/3  %s" % (k, " / ".join(cells)))
check(ok_stops, "every step: each port off the ramps, a pressed pin %.1f mm" % (TRAVEL - HB["REST_GAP"]))
# the stop's play against the ramps: the pin stops the disc on its low face, up to the notch's play the other way
play_deg = w_notch - 2 * d_pin
margin = 99.0
for xp in [j + 0.5 for j in range(-3, 4)]:
    for a_, b_ in (TOP_C, TOP_V):
        edges = (a_, b_) if a_ <= xp <= b_ else (a_ - RAMP, b_ + RAMP)
        margin = min(margin, min(abs(xp - e) for e in edges) * P_ANG)
check(margin >= play_deg + 1.0, "parked: the nearest ramp %.1f deg away; the pin holds the low face, play back %.1f deg"
      % (margin, play_deg))
# loads
kk = _rt["cams"](N)
t_rotor = kk["t_rotor"]
t_slip = SLIP * t_rotor / (GEAR_Z[1] / GEAR_Z[0])
f_slip = t_slip / (MU_RUBBER * 2 * ((SLIP_WASHER[0] + SLIP_WASHER[1]) / 4) / 1000)
f_pin = SLIP * t_rotor / (PIN[1] / 1000)
f_trig = 0.2 * f_pin * LEVER[0] / LEVER[1]
check(f_trig <= 8.0, "stopped: the pin holds %.0f N (slip %.2f N m at the layshaft, spring ~%.0f N on the washers);"
      " the trigger lets it out with ~%.1f N (steel pin, greased, lever %.0f:%.0f)"
      % (f_pin, t_slip, f_slip, f_trig, LEVER[1], LEVER[0]))
travel_trig = (PIN[2] - PIN[1]) * LEVER[1] / LEVER[0]
check(PIN[2] - PIN[0] / 2 >= STOP[0] + 0.3 and PIN[1] - PIN[0] / 2 >= STOP[1],
      "stop pin: in a notch %.1f mm deep, %.1f clear of the rim when pressed; trigger travel %.0f mm"
      % (STOP[0] - (PIN[1] - PIN[0] / 2), PIN[2] - PIN[0] / 2 - STOP[0], travel_trig))
f_knob = t_slip / (CRANK_R / 1000)
check(True, "crank: <= %.1f N on the knob turning (%d barrels' pushers, %.2f N m at the rotor), %.1f N slipping"
      % (kk["f_crank"], N, t_rotor, f_knob))
bb = base.BoundBox
check(bb.XLength <= 250 and bb.YLength <= 250, "base %.0f x %.0f mm fits a 256 bed" % (bb.XLength, bb.YLength))

report = [
    "Mitrailleuse head, bench C v2: the %d's rotor under a block of four, from a crank through the head's drive" % N,
    "  rotor R%.0f, arcs on R%.0f (charge) and R%.0f (vent), ramps lofted; stack on a Ø8 shaft in a housing with"
    " 2 x 608: stop disc R%.0f, gear %d T, rotor" % (ROTOR_R, CHARGE_R, VENT_R, STOP[0], GEAR_Z[1]),
    "  layshaft M8 at %.2f mm: pinion %d T free on it between rubber washers Ø%.0f/%.0f, spring and nut;"
    " bevels %d:%d m%.0f to a crank R%.0f" % (c_gear, GEAR_Z[0], SLIP_WASHER[0], SLIP_WASHER[1], P.BEVEL_TEETH,
                                             P.BEVEL_TEETH, P.BEVEL_MODULE, CRANK_R),
    "  bench block %.1f..%.1f deg, R%.0f..%.0f, %.0f thick; ports at %s deg; supply G1/8 on top at %.0f deg,"
    " a pilot G1/8 on top per port" % (QUARTER + BLOCK_R + (BLOCK_T, " / ".join("%.2f" % port_ang(j) for j in PORTS),
                                                            SUP_IN_ANG)),
    "  levels: housing 0..%.0f, stop disc %.0f, gear %.0f, rotor %.0f, cam %.0f, plate %.0f, block %.0f..%.0f;"
    " layshaft 608s at %.0f and %.0f, bevel apex %.1f" % (z_hs, z_stop0, z_gear0, z_rotor0, z_cam0, z_plate0,
                                                          z_block0, z_top, Z_BOSS - BRG[2], z_lb, z_apex),
] + rows + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
if not ROTOR_BENCH_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- document and exports
if not ROTOR_BENCH_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    undo = FV.VIEW_ROT.inverse()

    def add(group, name, shape, style):
        s = shape.copy()
        s.Placement = undo.multiply(s.Placement)
        sc.add(group, name, s, style)

    for n, s, st in (("Block", block, "stator"), ("Guide_plate", plate, "plate"), ("Followers", followers, "printed"),
                     ("Rotor", rotor, "rotor"), ("Gear", gear, "drive"), ("Pinion", pinion, "drive"),
                     ("Stop_disc", stop_disc, "printed"), ("Shaft_housing", housing, "stator"),
                     ("Bevel_gears", bev_lay.fuse(bev_crank), "drive"), ("Crank", crank, "printed")):
        add("Head", n, s, st)
    for n, s, st in (("Lever", lever, "printed"), ("Base", base, "frame"), ("Bevel_box", box, "frame")):
        add("Bench", n, s, st)
    for n, s, st in (("Valve_cores", cores, "steel"), ("Pins", pins, "steel"), ("Return_springs", springs, "steel"),
                     ("Shaft", shaft, "steel"), ("Layshaft", layshaft, "steel"), ("Crank_shaft", crank_shaft, "steel"),
                     ("Bearings", brgs, "steel"), ("Slip_clutch", slip, "oring"), ("Stop_pin", stop_pin, "steel"),
                     ("Fittings", fittings, "steel")):
        add("Bought", n, s, st)
    add("Channels", "Supply", net["supply"].translated(V(0, 0, z_block0)), "flow")
    add("Channels", "Pilots", pil_all.translated(V(0, 0, z_block0)), "hose")
    add("Channels", "Exhaust", net["exhaust"].translated(V(0, 0, z_block0)), "drive")
    sc.finish(hidden_groups=("Channels",))
    sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, rot=None):
        s = shape.copy()
        if rot:
            s.rotate(O, rot[0], rot[1])
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for f in os.listdir(OUT_DIR):                         # v1's parts are gone
        if f.endswith((".stl", ".step")):
            os.remove(os.path.join(OUT_DIR, f))
    if N == 16:
        blocks_out = (("head_block_quarter", block, None), ("head_guide_plate_quarter", plate, None))
    else:                                                 # x BLOCK_PORTS.count(n) for the gun, block4 also the bench's
        blocks_out = tuple(x for n, bk in BLOCKS.items() for x in (("head_block%d" % n, bk["blk"], None),
                                                                  ("head_guide_plate%d" % n, bk["pl"], None)))
    for n, s, rot in blocks_out + (
                      ("head_rotor%d" % N, rotor, None), ("head_gear75", gear, None), ("head_pinion15", pinion, None),
                      ("head_stop_disc%d" % N, stop_disc, None), ("head_shaft_housing", housing, None),
                      ("head_bevel20_x2", bevel_print, None), ("head_crank", crank, (Y, 90)),
                      ("head_follower", follower(0, 0, 0), (X, 180)),
                      ("bench_base", base, None), ("bench_lever", lever, None), ("bench_bevel_box", box, (X, 90))):
        write(s, n, rot)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
