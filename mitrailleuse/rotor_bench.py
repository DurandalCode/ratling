# -*- coding: utf-8 -*-
"""
Mitrailleuse firing head, bench C: the real 16-barrel rotor on three ports, cranked by hand (FreeCAD 1.0).

Bench B (head_bench.py) tries the pneumatics of one port on a flat slider. This one turns the gun's own
rotor (rotor_timing.py, 16 barrels) under a three-port sector of the core block, through a 5:1 spur pair
from a crank, to try what B cannot: the crank force, the rotor's thrust, and stopping it on a step when
the trigger is let go. Frame: z up along the rotor's axis, z = 0 the base's top; stator angle from +x.

    base ......... printed plate: the rotor shaft's lower 608, the layshaft's lower 608 and a column with
                   its upper one, four posts under the block, the stop lever's pivot.
    rotor stack .. on a Ø8 steel shaft with a flat, each part on it keyed by a D bore, stacked hub on hub on
                   the lower 608's inner race (the pushers push the rotor down, the stack carries it there):
                   stop disc (16 notches), 75-tooth gear, rotor (the gun's, both cam arcs, ramps lofted).
                   The shaft's top runs in a 608 in the block's hub.
    stop ......... the trigger's lever pivots on the base; a steel pin Ø4 in its tip drops into the stop
                   disc's notches under a spring. Trigger pressed: the pin is out, the rotor turns. Let go:
                   the pin rides the disc's rim and drops into the next notch, which stops the rotor on the
                   step, every pusher off the ramps. The tip's load runs through the lever's pivot.
    slip clutch .. the layshaft is an M8 stud: the crank arm on its top, the 15-tooth pinion free on it,
                   squeezed between two rubber washers by a spring and a nut. Stopped by the pin, the
                   rotor holds and the crank slips (SLIP x the rotor's torque); the nut sets it.
    block sector . three ports of the 16's core block (stator 0, 22.5, 45 deg), each as in bench B: charge
                   core on R60, vent core on R42, pins down; a supply gallery over the charge cores (G1/8
                   on top), each pilot on its own G1/8 on top (to a module, a gauge or a plug) and across
                   to its vent core, each vent core's exhaust inwards and down through the guide plate.
    pushers ...... bench B's: Ø3 pin in a printed follower, set by a grub screw, return spring.

This replaces concept A's dog clutch and ratchet detent for the bench: the detent is far too weak to finish
a step against the pushers (docs/rotor.md), and a dog clutch that only lets go on a step either jams or
lets go anywhere. If the stop and slip clutch work here, the gun takes them.

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
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
import ratling.gears as GR
for _m in (G, FV, GR):
    importlib.reload(_m)

_rt = {"__name__": "rotor_timing"}
exec(open(os.path.join(REPO, "mitrailleuse", "rotor_timing.py"), encoding="utf-8").read(), _rt)
HB = {"REPO": REPO, "HEAD_BENCH_LIBRARY": True}
exec(open(os.path.join(REPO, "mitrailleuse", "head_bench.py"), encoding="utf-8").read(), HB)

NAME = "rotor_bench"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
cyl = G.cyl

# ---------------------------------------------------------------- parameters
N = 16
P_ANG = 360.0 / N
PORTS = (0, 1, 2)                    # stator angles j * P_ANG
VENT_R, CHARGE_R = _rt["VENT_R"], _rt["CHARGE_R"]
TOP_C, TOP_V = _rt["cams"](N)["top_c"], _rt["VENT_TOP"]
TRAVEL, RAMP = _rt["TRAVEL"], _rt["RAMP"]
STRIP_W = 10.0
RISER_DR = 7.0                       # pilot riser outside the charge core
Z_SUP, Z_PIL, Z_LINK, Z_EXH = 20.0, 25.0, 3.2, 3.0
EXH_R = 33.0                         # exhaust goes in to here, then down through the plate
SUP_IN_ANG = 0.5 * P_ANG             # supply inlet between ports 0 and 1

SHAFT_D = 8.0
BRG = (22.0, 8.0, 7.0)               # 608: OD, bore, width
D_FLAT = 7.2                         # the shaft's flat: 0.8 off
Z_BOSS = 9.0                         # base boss top = lower bearing's top
STOP = (30.0, 25.0, 6.0)             # stop disc: rim R, notch floor R, thickness
NOTCH_W = 4.8                        # mm at the pin's radius: the pin + room to drop in at full speed
PIN = (4.0, 27.0, 33.0)              # stop pin Ø, centre R in a notch, centre R on the rim
LEVER = (30.0, 70.0, 8.0, 6.0)       # pivot to pin, pivot to trigger, width, thickness
GEAR_M, GEAR_Z = 1.75, (15, 75)
GEAR_FACE = 8.0
ROTOR_R, ROTOR_T = 70.0, 8.0
BLOCK_T, PLATE_T = 34.0, 6.0
SPRING_REST, FOLLOWER_H = HB["SPRING_REST"], HB["FOLLOWER_H"]
SECTOR = (-20.0, 65.0, 86.0)         # block sector: from, to (deg), outer R
POST_R, POST_D = 78.0, 12.0
POST_ANGS = (-11.25, 11.25, 33.75, 56.25)
CRANK_R = _rt["CRANK_R"]
SLIP = 1.3                           # slip torque over the most the rotor needs
MU_RUBBER = 0.4
SLIP_WASHER = (9.0, 22.0)            # rubber washers: ID, OD

# ---------------------------------------------------------------- levels
z_stop0 = Z_BOSS + 2.0
z_gear0 = z_stop0 + STOP[2] + 3.0
z_rotor0 = z_gear0 + GEAR_FACE + 4.0
z_cam0 = z_rotor0 + ROTOR_T                           # followers' feet at rest
z_ftop = z_cam0 + FOLLOWER_H
z_plate0 = z_ftop + SPRING_REST
z_block0 = z_plate0 + PLATE_T
z_top = z_block0 + BLOCK_T
c_gear = GEAR_M * sum(GEAR_Z) / 2                     # layshaft distance
LAY = (-c_gear, 0.0)                                  # layshaft at 180 deg


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


def spur(z, z0, bore_d, phase=0.0):
    pts = GR.tooth_outline(z, GEAR_M, 1.0, 0.15)
    w = Part.makePolygon([V(x, y, 0) for x, y in pts] + [V(pts[0][0], pts[0][1], 0)])
    g = Part.Face(w).extrude(V(0, 0, GEAR_FACE))
    g.rotate(V(0, 0, 0), Z, phase)
    g.translate(V(0, 0, z0))
    return g


# ---------------------------------------------------------------- rotor (x -> rotor angle (x - 0.5) * P_ANG)
ang = lambda x: (x - 0.5) * P_ANG


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
stop_disc = cyl(2 * STOP[0], z_stop0, z_stop0 + STOP[2]).fuse(cyl(16.0, Z_BOSS, z_gear0))
for i in range(N):
    lo = pin_ang - d_pin + i * P_ANG                 # the trailing (low) face catches the pin
    stop_disc = stop_disc.cut(sector(STOP[1], STOP[0] + 1, z_stop0 - 1, z_stop0 + STOP[2] + 1, lo, lo + w_notch))
stop_disc = stop_disc.cut(d_tool(Z_BOSS - 1, z_gear0 + 1)).removeSplitter()

gear = spur(GEAR_Z[1], z_gear0, SHAFT_D).fuse(cyl(24.0, z_gear0 - 2.0, z_rotor0)).cut(d_tool(z_gear0 - 3, z_rotor0 + 1))
pinion = spur(GEAR_Z[0], z_gear0, 8.4).cut(cyl(8.4, z_gear0 - 1, z_gear0 + GEAR_FACE + 1))
pinion.translate(V(LAY[0], LAY[1], 0))

# ---------------------------------------------------------------- block sector, plate
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


CH, SUP, EXH = HB["CH_D"], HB["SUP_D"], HB["EXH_D"]
zb1 = HB["z_bore1"]
net = {"supply": [], "exhaust": []}
pil = {}
holes = []
for j in PORTS:
    a = j * P_ANG
    c, v, rr = polar(CHARGE_R, a), polar(VENT_R, a), polar(CHARGE_R + RISER_DR, a)
    holes += [core_hole(c[0], c[1], True), core_hole(v[0], v[1], False)]
    net["supply"].append(cyl(HB["CORE_BORE_D"], zb1 - 0.1, Z_SUP + SUP / 2, *c))
    pil[j] = G.fuse_all([rod(CH, polar(CHARGE_R + 1.5, a) + (Z_LINK,), rr + (Z_LINK,)),
                         cyl(CH, Z_LINK - CH / 2, BLOCK_T - HB["G18_TAP_DEPTH"] + 0.5, *rr), g18(*rr),
                         rod(CH, rr + (Z_PIL,), v + (Z_PIL,)),
                         cyl(HB["CORE_BORE_D"], zb1 - 0.1, Z_PIL + CH / 2, *v)])
    net["exhaust"].append(G.fuse_all([rod(EXH, v + (Z_EXH,), polar(EXH_R, a) + (Z_EXH,)),
                                      cyl(EXH, -1, Z_EXH + EXH / 2, *polar(EXH_R, a))]))
for j0, j1 in zip(PORTS, PORTS[1:]):
    net["supply"].append(rod(SUP, polar(CHARGE_R, j0 * P_ANG) + (Z_SUP,), polar(CHARGE_R, j1 * P_ANG) + (Z_SUP,)))
sup_in = polar(CHARGE_R * math.cos(math.radians(P_ANG / 2)), SUP_IN_ANG)
net["supply"] += [cyl(SUP, Z_SUP - SUP / 2, BLOCK_T - HB["G18_TAP_DEPTH"] + 0.5, *sup_in), g18(*sup_in)]
net["supply"] = G.fuse_all(net["supply"])
net["exhaust"] = G.fuse_all(net["exhaust"])
posts_xy = [polar(POST_R, a) for a in POST_ANGS]
bolt_tool = lambda d, z0, z1: G.fuse_all([cyl(d, z0, z1, *p) for p in posts_xy])

blk = sector(0, SECTOR[2], 0, BLOCK_T, SECTOR[0], SECTOR[1]).fuse(cyl(34.0, 0, BLOCK_T))
for s in holes + [net["supply"], net["exhaust"]] + list(pil.values()):
    blk = blk.cut(s)
blk = blk.cut(bolt_tool(4.5, -1, BLOCK_T + 1)).cut(cyl(SHAFT_D + 1.0, -1, BLOCK_T + 1))
blk = blk.cut(cyl(BRG[0] + 0.2, BLOCK_T - BRG[2], BLOCK_T + 1))       # the shaft's upper 608, from the top
block = blk.copy()
block.translate(V(0, 0, z_block0))

pl = sector(0, SECTOR[2], -PLATE_T, 0, SECTOR[0], SECTOR[1]).fuse(cyl(34.0, -PLATE_T, 0))
for j in PORTS:
    for r in (CHARGE_R, VENT_R):
        pl = pl.cut(cyl(HB["PIN_HOLE"], -PLATE_T - 1, 1, *polar(r, j * P_ANG)))
    pl = pl.cut(cyl(EXH, -PLATE_T - 1, 1, *polar(EXH_R, j * P_ANG)))
pl = pl.cut(bolt_tool(4.5, -PLATE_T - 1, 1)).cut(cyl(SHAFT_D + 2.0, -PLATE_T - 1, 1))
plate = pl.copy()
plate.translate(V(0, 0, z_block0))


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


followers, pins, springs = [], [], []
z_core_pin = z_block0 + HB["z_pin"]
for j in PORTS:
    for r, top in ((CHARGE_R, TOP_C), (VENT_R, TOP_V)):
        x_port = j + 0.5
        up = lift(x_port, top)
        xy = polar(r, j * P_ANG)
        followers.append(follower(xy[0], xy[1], up))
        pins.append(cyl(HB["PIN_D"], z_ftop + up - HB["PIN_IN_FOLLOWER"], z_core_pin - HB["REST_GAP"] + up, *xy))
        s = G.spring(0, z_ftop + up, z_plate0, HB["SPRING"][0], HB["SPRING"][1], 4)
        s.translate(V(xy[0], xy[1], 0))
        springs.append(s)
followers, pins, springs = G.fuse_all(followers), G.fuse_all(pins), G.fuse_all(springs)

# ---------------------------------------------------------------- stop lever, trigger
pin_xy = polar(PIN[1], pin_ang)                  # (0, -27) engaged
pivot = (pin_xy[0] + LEVER[0], pin_xy[1])
z_lev0, z_lev1 = 2.0, 2.0 + LEVER[3]
lever = G.fuse_all([Part.makeBox(LEVER[0] + LEVER[1] + 6, LEVER[2], LEVER[3],
                                 V(pin_xy[0] - 4, pin_xy[1] - LEVER[2] / 2, z_lev0)),
                    cyl(12.0, z_lev0, z_lev1, *pivot), cyl(10.0, z_lev0, z_lev1, *pin_xy)])
lever = lever.cut(cyl(4.3, z_lev0 - 1, z_lev1 + 1, *pivot)).cut(cyl(PIN[0] - 0.1, z_lev0 - 1, z_lev1 + 1, *pin_xy))
stop_pin = cyl(PIN[0], z_lev0, z_stop0 + STOP[2], *pin_xy)
trig_xy = (pivot[0] + LEVER[1], pivot[1])
lever = lever.fuse(Part.makeBox(10, 4, 22, V(trig_xy[0] - 5, trig_xy[1] - LEVER[2] / 2 - 4, z_lev0)))   # finger pad

# ---------------------------------------------------------------- base, posts, layshaft column
X0, X1, Y0, Y1 = -112.0, trig_xy[0] + 18.0, -76.0, 80.0
base = Part.makeBox(X1 - X0, Y1 - Y0, 6.0, V(X0, Y0, -6.0))
base = base.fuse(cyl(32.0, 0, Z_BOSS)).cut(cyl(BRG[0] + 0.2, Z_BOSS - BRG[2], Z_BOSS + 1)).cut(cyl(12.0, -7, 1))
base = base.fuse(cyl(32.0, 0, Z_BOSS, *LAY)).cut(cyl(BRG[0] + 0.2, Z_BOSS - BRG[2], Z_BOSS + 1, *LAY)).cut(
    cyl(12.0, -7, 1, *LAY))
for p in posts_xy:
    base = base.fuse(cyl(POST_D, 0, z_plate0, *p))
base = base.cut(bolt_tool(3.6, z_plate0 - 16, z_plate0 + 1))
base = base.cut(cyl(3.4, -7, 2, *pivot))                    # pivot: M4 from below, lever on a washer
# spring post: the lever's spring pushes it towards the disc (-y at the trigger)
sp_xy = (pivot[0] + 40.0, pivot[1] + LEVER[2] / 2 + 14.0)
base = base.fuse(Part.makeBox(10, 6, z_lev1 + 4, V(sp_xy[0] - 5, sp_xy[1], 0)))
# layshaft column: an arm over the layshaft with its upper 608
z_lay_brg = z_rotor0 + 16.0
col_xy = (LAY[0] - 22.0, 0.0)
column = Part.makeBox(12, 30, z_lay_brg + 9, V(col_xy[0] - 6, -15, 0)).fuse(
    Part.makeBox(28, 30, 9, V(col_xy[0], -15, z_lay_brg)))
column = column.fuse(cyl(32, z_lay_brg, z_lay_brg + 9, *LAY)).cut(cyl(BRG[0] + 0.2, z_lay_brg + 2, z_lay_brg + 10, *LAY))
column = column.cut(cyl(12.0, z_lay_brg - 1, z_lay_brg + 3, *LAY))
base = base.fuse(column).removeSplitter()

# ---------------------------------------------------------------- bought / steel, for the picture
shaft = cyl(SHAFT_D, 2.0, z_top - 1.0)
layshaft = cyl(8.0, 2.0, z_lay_brg + 30.0, *LAY)
brgs = G.fuse_all([cyl(BRG[0], Z_BOSS - BRG[2], Z_BOSS), cyl(BRG[0], Z_BOSS - BRG[2], Z_BOSS, *LAY),
                   cyl(BRG[0], z_lay_brg + 2, z_lay_brg + 9, *LAY),
                   cyl(BRG[0], z_top - BRG[2], z_top)]).cut(G.fuse_all([
                       cyl(BRG[1], -1, z_top + 1), cyl(BRG[1], -1, z_top + 1, *LAY)]))
z_p1 = z_gear0 + GEAR_FACE
slip = G.fuse_all([cyl(13.0, z_gear0 - 6.5, z_gear0 - 1.5, *LAY),                      # lock nut under it
                   cyl(SLIP_WASHER[1], z_gear0 - 1.5, z_gear0, *LAY),
                   cyl(SLIP_WASHER[1], z_p1, z_p1 + 1.5, *LAY),
                   cyl(16.0, z_p1 + 1.5, z_p1 + 2.5, *LAY),
                   cyl(14.0, z_p1 + 2.5, z_p1 + 14.5, *LAY).cut(cyl(10.0, z_p1 + 2, z_p1 + 15, *LAY)),
                   cyl(16.0, z_p1 + 14.5, z_p1 + 15.5, *LAY), cyl(13.0, z_p1 + 15.5, z_p1 + 22.0, *LAY)])
z_arm = z_lay_brg + 12.0
crank = G.fuse_all([Part.makeBox(CRANK_R + 10, 18, 8, V(LAY[0] - CRANK_R, -9, z_arm)),
                    cyl(18, z_arm, z_arm + 8, *LAY),
                    cyl(16, z_arm + 8, z_arm + 45, LAY[0] - CRANK_R, 0)])         # printed: arm and knob
crank = crank.cut(cyl(8.4, z_arm - 1, z_arm + 9, *LAY)).cut(G.hex_prism(13.2, z_arm + 3, z_arm + 9, *LAY))
cores = []
for j in PORTS:
    for r in (CHARGE_R, VENT_R):
        x, y = polar(r, j * P_ANG)
        zc = z_block0
        cores.append(G.fuse_all([cyl(HB["CORE_THREAD_D"], zc + HB["CAV_TOP"], zc + HB["z_tap1"], x, y),
                                 cyl(4.4, zc + HB["z_tap1"], zc + HB["z_seat1"] + 1, x, y),
                                 cyl(2.6, zc + HB["z_seat1"] + 1, zc + zb1 - 1, x, y),
                                 cyl(1.0, zc + HB["z_pin"], zc + HB["CAV_TOP"], x, y)]))
cores = G.fuse_all(cores)
fittings = []
for xy in [polar(CHARGE_R + RISER_DR, j * P_ANG) for j in PORTS] + [sup_in]:
    fittings.append(G.push_in_fitting(xy[0], xy[1], z_top))
fittings = G.fuse_all(fittings)

# ---------------------------------------------------------------- checks
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
wall = lambda a, b: a.distToShape(b)[0]
pil_all = G.fuse_all(list(pil.values()))
d_sp = wall(net["supply"], pil_all)
d_se = wall(net["supply"], net["exhaust"])
d_pe = wall(pil_all, net["exhaust"])
d_pp = min(wall(pil[a], pil[b]) for a, b in ((0, 1), (1, 2)))
check(min(d_sp, d_se, d_pe, d_pp) >= 1.2, "block: supply / pilot / exhaust / pilot-to-pilot walls >= %.1f mm"
      " (%.1f / %.1f / %.1f / %.1f)" % (min(d_sp, d_se, d_pe, d_pp), d_sp, d_se, d_pe, d_pp))
d_bolt = wall(bolt_tool(4.5, -1, BLOCK_T + 1), G.fuse_all([net["supply"], net["exhaust"], pil_all] + holes))
check(d_bolt >= 1.2, "block: bolts %.1f mm clear of every channel and core" % d_bolt)
ok_links = True
for j in PORTS:
    a = j * P_ANG
    c, v = polar(CHARGE_R, a), polar(VENT_R, a)
    ok_links &= net["supply"].common(cyl(HB["CORE_BORE_D"], HB["z_seat1"], zb1, *c)).Volume > 0.5
    ok_links &= pil[j].common(cyl(HB["CAV_D"], HB["GLAND"][1], HB["CAV_TOP"], *c)).Volume > 0.5
    ok_links &= pil[j].common(cyl(HB["CORE_BORE_D"], HB["z_seat1"], zb1, *v)).Volume > 0.5
    ok_links &= net["exhaust"].common(cyl(HB["CAV_D"], 0, HB["CAV_TOP"], *v)).Volume > 0.5
check(ok_links, "block: per port, supply -> charge core, charge cavity -> pilot -> vent core, vent cavity -> exhaust")
for nm, s in (("block", block), ("plate", plate), ("rotor", rotor), ("gear", gear), ("pinion", pinion),
              ("stop disc", stop_disc), ("lever", lever), ("base", base), ("crank", crank)):
    check(G.single_solid(s), "%s one solid" % nm)
moving = {"rotor": rotor, "gear": gear, "stop disc": stop_disc}
clash = []
for nm, s in moving.items():
    for on, o in (("base", base), ("plate", plate), ("lever", lever)):
        if s.common(o).Volume > 0.5:
            clash.append(nm + "/" + on)
if pinion.common(base).Volume > 0.5 or pinion.common(rotor).Volume > 0.5:
    clash.append("pinion")
check(not clash, "nothing turning runs into the base, posts, column, plate or lever%s"
      % (" (" + ", ".join(clash) + ")" if clash else ""))
d_post = min(math.hypot(*p) for p in posts_xy) - POST_D / 2 - ROTOR_R
d_lay = c_gear - 4.0 - ROTOR_R
check(d_post >= 1.5 and d_lay >= 1.5, "rotor R%.0f: %.1f mm to the posts, %.1f to the layshaft" % (ROTOR_R, d_post,
                                                                                                    d_lay))
mesh = gear.common(pinion).Volume
check(mesh < 1.0, "gears %d / %d m%.2f mesh at %.2f mm, no overlap (%.2f mm3)" % (GEAR_Z + (GEAR_M, c_gear, mesh)))
# stops: rotor parked at psi = k steps, each port at x = j + 0.5 - k
rows, ok_stops = [], True
for k in range(4):
    cells = []
    for j in PORTS:
        x = j + 0.5 - k
        pc = max(0.0, lift(x, TOP_C) - HB["REST_GAP"])
        pv = max(0.0, lift(x, TOP_V) - HB["REST_GAP"])
        ramp_on = 0 < _rt["height"](x, TOP_C) < 1 or 0 < _rt["height"](x, TOP_V) < 1
        ok_stops &= not ramp_on and (pc == 0 or _rt["PIN_OPEN"] <= pc <= _rt["PIN_MAX"]) and (
            pv == 0 or _rt["PIN_OPEN"] <= pv <= _rt["PIN_MAX"])
        cells.append("%s" % ("заряд" if pc else ("СБРОС" if pv else "-")))
    rows.append("    step %d: ports 0/1/2  %s" % (k, " / ".join(cells)))
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
check(True, "crank: <= %.1f N on the knob turning (16 pushers' worth, %.2f N m at the rotor), %.1f N slipping"
      % (kk["f_crank"], t_rotor, f_knob))

report = [
    "Mitrailleuse head, bench C: the 16's rotor on three ports, by crank",
    "  rotor R%.0f, arcs on R%.0f (charge) and R%.0f (vent), ramps lofted; stack on a Ø8 shaft: stop disc R%.0f,"
    " gear %d T, rotor" % (ROTOR_R, CHARGE_R, VENT_R, STOP[0], GEAR_Z[1]),
    "  layshaft M8 at %.2f mm: pinion %d T free on it between rubber washers Ø%.0f/%.0f, spring and nut; crank R%.0f"
    % (c_gear, GEAR_Z[0], SLIP_WASHER[0], SLIP_WASHER[1], CRANK_R),
    "  block sector %.0f..%.0f deg, R%.0f, %.0f thick; ports at 0 / %.1f / %.1f deg; supply G1/8 on top at %.2f deg,"
    " a pilot G1/8 on top per port" % (SECTOR + (BLOCK_T, P_ANG, 2 * P_ANG, SUP_IN_ANG)),
    "  levels: base boss %.0f, stop disc %.0f, gear %.0f, rotor %.0f, cam %.0f, plate %.0f, block %.0f..%.0f"
    % (Z_BOSS, z_stop0, z_gear0, z_rotor0, z_cam0, z_plate0, z_block0, z_top),
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
                     ("Stop_disc", stop_disc, "printed"), ("Lever", lever, "printed"), ("Base", base, "frame"),
                     ("Crank", crank, "printed")):
        add("Printed", n, s, st)
    for n, s, st in (("Valve_cores", cores, "steel"), ("Pins", pins, "steel"), ("Return_springs", springs, "steel"),
                     ("Shaft", shaft, "steel"), ("Layshaft", layshaft, "steel"), ("Bearings", brgs, "steel"),
                     ("Slip_clutch", slip, "oring"), ("Stop_pin", stop_pin, "steel"),
                     ("Fittings", fittings, "steel")):
        add("Bought", n, s, st)
    add("Channels", "Supply", net["supply"].translated(V(0, 0, z_block0)), "flow")
    add("Channels", "Pilots", pil_all.translated(V(0, 0, z_block0)), "hose")
    add("Channels", "Exhaust", net["exhaust"].translated(V(0, 0, z_block0)), "drive")
    sc.finish(hidden_groups=("Channels",))
    sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    import MeshPart

    def write(shape, name, flip=False):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(
            os.path.join(OUT_DIR, name + ".stl"))

    for n, s, flip in (("block", block, False), ("guide_plate", plate, False), ("rotor", rotor, False),
                       ("gear75", gear, False), ("pinion15", pinion, False), ("stop_disc", stop_disc, False),
                       ("lever", lever, False), ("base", base, False), ("crank", crank, False),
                       ("follower", follower(0, 0, 0), True)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
