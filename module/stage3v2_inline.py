# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v2: inline barrel module, the valve inside the tube.

Stage 3 put chamber and barrel side by side behind a Ø62 diaphragm valve,
which set the pack pitch to 74 x 64. Here everything sits on one axis and
nothing but screw heads is wider than the tube:

    rear plug ── chamber tube ──[cartridge]── barrel tube ──> muzzle
       │  pilot G1/8 out          │
       └── pilot tube 6/4 (PA) ───┘  inside the chamber

    cartridge .... printed, one part. A collar Ø = tube OD between two
                   spigots (the tube plug gland): the rear one into the
                   chamber tube ends in the seat, the front one into the
                   barrel ends in the ball stop. Behind the seat four struts
                   hold the piston housing in the chamber; chamber air runs
                   round the housing and in between the struts to the seat.
                   The housing is open at the back: the piston goes in there.
    housing cap .. printed, closes the housing behind the piston: a spigot
                   with the piston's O-ring into the housing bore, the pilot
                   tube socket behind. Three ST2.9 screws through the
                   housing wall, behind the O-ring, hold it against the
                   pilot pressure.
    piston ....... Ø PISTON_D on an O-ring in the housing, rubber pad on its
                   face against the seat. Pilot pressure behind it holds it
                   shut; vented, the chamber pressure on the annulus outside
                   the seat drives it back LIFT mm and the chamber dumps into
                   the barrel. The chamber charges from the pilot through a
                   bleed hole in the housing wall.
    pilot tube ... rigid PA 6/4 (a PU hose may collapse when the pilot is
                   vented under chamber pressure), sliding in an O-ring
                   socket at each end, so its length is not critical.
    rear plug .... closes the chamber; socket for the pilot tube inside,
                   G1/8 pilot port outside (bench: M3R110 A; later the
                   firing head).

All frames: z along the axis, +z towards the muzzle, z = 0 at the seat (the
pad's face when shut). Print the cartridge front tip down, the piston back
face down, the housing cap socket mouth down, the plug flange down; PETG 100 %.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3v2_inline.py').read())
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
    STAGE3V2_LIBRARY
except NameError:
    STAGE3V2_LIBRARY = False
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

OUT_DIR = os.path.join(REPO, "exports", "stage3v2_inline")
NAME = "stage3v2_inline"

# ---------------------------------------------------------------- parameters
P_WORK_BAR, P_MAX_BAR = 2.0, 5.0

TUBE_ID = 23.8
TUBE_WALL = 0.59
TUBE_OD = TUBE_ID + 2 * TUBE_WALL
BARREL_LEN = 300.0
CHAMBER_V = 100.0           # cm3 target

# Tube gland = connectors/tube_plug_v1 (fit confirmed)
RADIAL_CLEAR = 0.20
ORING_ID, ORING_CS = 11 / 16 * 25.4, 1 / 8 * 25.4
ORING_SQUEEZE = 0.12
GROOVE_ROOT_W = 1.1 * ORING_CS
GROOVE_WALL_FROM_TIP = 9.0
LEAD_CHAMFER = 1.0
SCREW_PILOT_D, SCREW_DEPTH, SCREW_L = 2.5, 3.8, 4.5   # ST2.9 x 4.5
SCREW_FROM_TUBE_END = 6.0

# Cartridge
BORE_D = 13.0               # through both spigots
SEAT_D = 11.0
SEAT_LAND = 0.8             # lip wall at its root
# Knife edge: the flat 0.8 land sank only ~0.2 mm into the pad, less than the
# piston's tilt in its 0.2 mm clearance (~0.4 across the seat), and the shut
# valve leaked into the barrel. The 45 deg chamfer outside narrows the tip.
SEAT_TIP = 0.3
LIP_H = 1.0
REAR_SPIGOT_LEN = 24.0
COLLAR_W = 6.0
COLLAR_D = 25.0
FRONT_SPIGOT_LEN = 26.0
WINDOW_H = 6.0              # housing front edge behind the seat plane
STRUT_N = 4
STRUT_W = 3.0
STRUT_R = (8.3, 11.3)
ARCH_R = 5.5                # windows between the struts: arch radius (half width)

# Piston and housing
PISTON_D = 16.0             # housing bore
PISTON_CLEAR = 0.2          # radial
PISTON_L = 12.0
PISTON_ORING = (12.0, 2.0)  # ID x CS
# Groove roots picked on stage3v2_oring_gauge in the printed housing bore: the
# nominal 10 % squeeze (root 12.4) barely moved; the 12.00 plug is right.
PISTON_ORING_ROOT = 12.00
CAP_ORING_ROOT = 12.15      # static: one gauge step tighter
PISTON_ORING_FROM_BACK = 3.5
PISTON_POCKET = 9.0         # lightening pocket in the back: Ø, 45 deg cone
PAD = (14.0, 1.5)           # rubber pad Ø x t (diaphragm sheet)
PAD_RECESS = 1.2
LIFT = 3.0
CAVITY = 3.0                # pilot space behind the piston when open
HOUSING_WALL = 1.5
BLEED_D = 0.8
CAP_SPIGOT = 10.5           # housing cap: spigot into the bore (piston's O-ring)
CAP_FLANGE_T = 2.5
CAP_SCREW_FROM_END = 3.0    # ST2.9 x 4.5 (as on the tubes) through the housing wall
CAP_SCREW_HOLE = 3.2        # clearance in the housing wall
CAP_SCREW_ANGLES = (60.0, 180.0, 300.0)

# Pilot tube sockets (PA 6/4, O-ring 6 x 1.5 in an internal groove)
PILOT_TUBE = (6.0, 4.0)
SOCKET_D = 6.2
SOCKET_DEPTH = 10.5
SOCKET_ORING = (6.0, 1.5)
SOCKET_ORING_SQUEEZE = 0.20
SOCKET_GROOVE_FROM_MOUTH = 3.0
SOCKET_WALL = 2.0
PILOT_CH_D = 3.0
TUBE_PLAY = 1.0             # each end, tube short of the socket floor

# Rear plug
PLUG_FLANGE_T = 5.0
PLUG_INSERT_LEN = 30.0
PLUG_FUNNEL = (12.0, 3.0)   # mouth Ø, depth: catches the pilot tube
G18_TAP_D, G18_TAP_DEPTH = 8.8, 8.0

PACK_PITCH = 30.0           # tube OD + screw heads

# ---------------------------------------------------------------- derived
X, Y, Z = App.Vector(1, 0, 0), App.Vector(0, 1, 0), App.Vector(0, 0, 1)
V = App.Vector
spigot_r = TUBE_ID / 2 - RADIAL_CLEAR
groove_depth = ORING_CS * (1 - ORING_SQUEEZE)
root_r = TUBE_ID / 2 - groove_depth
oring_stretch = 2 * root_r / ORING_ID - 1
z_rs0 = LIP_H                                  # rear spigot tip face
z_c0 = z_rs0 + REAR_SPIGOT_LEN                 # collar
z_c1 = z_c0 + COLLAR_W
z_tip = z_c1 + FRONT_SPIGOT_LEN                # ball stop
housing_r = PISTON_D / 2 + HOUSING_WALL
z_h0 = -WINDOW_H                               # housing front edge
z_bore_end = -(PISTON_L + LIFT + CAVITY)
z_split = z_bore_end - CAP_SPIGOT              # housing back end / cap flange face
z_hback = z_split - CAP_FLANGE_T
sock_r = SOCKET_D / 2 + (SOCKET_ORING[1] * (1 - SOCKET_ORING_SQUEEZE)) + SOCKET_WALL
z_sock_mouth = z_hback - SOCKET_DEPTH - 1.5
z_sock_floor = z_sock_mouth + SOCKET_DEPTH
pist_oring_root = PISTON_ORING_ROOT
cap_oring_root = CAP_ORING_ROOT
pist_groove_w = 1.35 * PISTON_ORING[1]
sock_groove_r = SOCKET_D / 2 + SOCKET_ORING[1] * (1 - SOCKET_ORING_SQUEEZE)   # tube Ø6 + ring
sock_groove_w = 1.35 * SOCKET_ORING[1]


def P2(r, z):
    return V(r, 0, z)


def revolve(rz):
    pts = [P2(r, z) for r, z in rz]
    s = Part.Face(Part.makePolygon(pts + [pts[0]])).revolve(V(0, 0, 0), Z, 360)
    return Part.Solid(s) if s.ShapeType != "Solid" else s


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def cone(d0, z0, d1, z1):
    return Part.makeCone(d0 / 2, d1 / 2, z1 - z0, V(0, 0, z0))


def gland(z_tip, z_root, toward):
    """Spigot from z_root to z_tip (toward = +1: tip at larger z). The groove's
    square wall faces the root (pressure side); 'ceiling45' puts the 45 deg
    wall on the larger-z side instead, for spigots printed tip down."""
    s = toward
    zt = z_tip
    g0 = zt - s * GROOVE_WALL_FROM_TIP              # square wall
    g1 = g0 + s * GROOVE_ROOT_W
    g2 = g1 + s * (spigot_r - root_r)
    rz = [(0, z_root), (spigot_r, z_root), (spigot_r, g0), (root_r, g0), (root_r, g1), (spigot_r, g2),
          (spigot_r, zt - s * LEAD_CHAMFER), (spigot_r - LEAD_CHAMFER, zt), (0, zt)]
    return revolve(rz if s > 0 else rz[::-1]), (min(g0, g2), max(g0, g2))


def gland_flipped(z_tip, z_root):
    """Tip at larger z, printed tip down: 45 deg wall on the root side."""
    g_sq = z_tip - GROOVE_WALL_FROM_TIP             # square wall, tip side of the groove
    g1 = g_sq - GROOVE_ROOT_W
    g2 = g1 - (spigot_r - root_r)
    rz = [(0, z_root), (spigot_r, z_root), (spigot_r, g2), (root_r, g1), (root_r, g_sq), (spigot_r, g_sq),
          (spigot_r, z_tip - LEAD_CHAMFER), (spigot_r - LEAD_CHAMFER, z_tip), (0, z_tip)]
    return revolve(rz), (g2, g_sq)


def screw_pilots(z, angles):
    out = []
    for a in angles:
        d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        out.append(Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_DEPTH + 1, V(d.x * (spigot_r + 1), d.y * (spigot_r + 1), z), -d))
    return out


def socket_cut(z_mouth, z_floor, groove_at_mouth_side_45):
    """Pilot tube socket: bore, internal O-ring groove (45 deg ceiling), mouth chamfer."""
    s = 1 if z_floor > z_mouth else -1
    out = [cyl(SOCKET_D, min(z_mouth, z_floor) - 0.01 * s, max(z_mouth, z_floor))]
    za = z_mouth + s * SOCKET_GROOVE_FROM_MOUTH
    zb = za + s * sock_groove_w
    # 45 deg wall on the side that prints as a ceiling
    if groove_at_mouth_side_45:
        rz = [(SOCKET_D / 2 - 0.5, za - s * (sock_groove_r - SOCKET_D / 2)), (sock_groove_r, za),
              (sock_groove_r, zb), (SOCKET_D / 2 - 0.5, zb)]
    else:
        rz = [(SOCKET_D / 2 - 0.5, za), (sock_groove_r, za), (sock_groove_r, zb),
              (SOCKET_D / 2 - 0.5, zb + s * (sock_groove_r - SOCKET_D / 2))]
    out.append(revolve(rz))
    out.append(Part.makeCone(SOCKET_D / 2 + 1.0, SOCKET_D / 2, 1.0, V(0, 0, z_mouth), V(0, 0, s)))
    return out, (min(za, zb), max(za, zb))


# ---------------------------------------------------------------- cartridge
rear_sp, rear_groove = gland(z_rs0, z_c0 + 0.5, -1)          # tip towards -z, printed tip up
front_sp, front_groove = gland_flipped(z_tip, z_c1 - 0.5)
cart = rear_sp.fuse(cyl(COLLAR_D, z_c0, z_c1)).fuse(front_sp)
cart = cart.fuse(revolve([(SEAT_D / 2, 0), (SEAT_D / 2 + SEAT_TIP, 0), (SEAT_D / 2 + SEAT_LAND, SEAT_LAND - SEAT_TIP),
                          (SEAT_D / 2 + SEAT_LAND, z_rs0 + 0.01),
                          (SEAT_D / 2, z_rs0 + 0.01)]))                                           # seat lip
housing = cyl(2 * housing_r, z_split, z_h0)
# The housing wall runs on down to the spigot face, and the windows between
# the struts end in round arches at z_h0: printed tip down, the housing front
# edge is a ceiling, and a flat one would span the struts in mid-air.
arcade = cyl(2 * housing_r, z_h0 - 0.01, z_rs0).cut(cyl(PISTON_D, z_h0 - 1, z_rs0 + 1))
for i in range(STRUT_N):
    win = Part.makeBox(2 * ARCH_R, housing_r + 2, z_rs0 + 1 - (z_h0 + ARCH_R), V(-ARCH_R, 0, z_h0 + ARCH_R))
    win = win.fuse(Part.makeCylinder(ARCH_R, housing_r + 2, V(0, 0, z_h0 + ARCH_R), Y))
    win.rotate(V(0, 0, 0), Z, 360.0 / STRUT_N * i)
    arcade = arcade.cut(win)
housing = housing.fuse(arcade)
for i in range(STRUT_N):
    st = Part.makeBox(STRUT_R[1] - STRUT_R[0], STRUT_W, z_rs0 - z_h0 + 1.0, V(STRUT_R[0], -STRUT_W / 2, z_h0 - 0.5))
    st.rotate(V(0, 0, 0), Z, 45 + 360.0 / STRUT_N * i)
    housing = housing.fuse(st)
cart = cart.fuse(housing)
cuts = [revolve([(0, -0.01), (SEAT_D / 2, -0.01), (SEAT_D / 2, z_rs0 + 0.5), (BORE_D / 2, z_rs0 + 0.5 + (BORE_D - SEAT_D) / 2),
                 (BORE_D / 2, z_tip + 1), (0, z_tip + 1)]),                                        # seat + bore
        cyl(PISTON_D, z_split - 1, z_h0 + 0.01),                                           # open back
        Part.makeCylinder(BLEED_D / 2, HOUSING_WALL + 2, V(PISTON_D / 2 - 1, 0, (z_bore_end + z_bore_end + CAVITY) / 2 - 0.0), X)]
cuts += screw_pilots(z_c0 - SCREW_FROM_TUBE_END, (0.0, 120.0, 240.0))
cuts += screw_pilots(z_c1 + SCREW_FROM_TUBE_END, (60.0, 180.0, 300.0))
for c in cuts:
    cart = cart.cut(c)
cart = cart.removeSplitter()
bleed_z = z_bore_end + CAVITY / 2

# ---------------------------------------------------------------- housing cap
pr = PISTON_D / 2 - PISTON_CLEAR
# Printed socket mouth down: the flange stands on the socket boss on a 45 deg
# cone (its back face mates with nothing), the spigot stands on the flange,
# the socket floor and the socket groove are 45 deg ceilings. The O-ring
# groove is square, as on the piston. Unheld, the pilot pressure blew the cap
# out: screws through the housing wall behind the O-ring (no pilot leak).
z_cs = z_split + CAP_SCREW_FROM_END              # cap screw axis
cg0 = z_cs + CAP_SCREW_HOLE / 2 + 1.4           # O-ring groove
cg1 = cg0 + pist_groove_w
cg2 = cg1
cz = (cg0 + cg1) / 2                             # O-ring centre
cap = revolve([(0, z_split), (pr, z_split), (pr, cg0), (cap_oring_root / 2, cg0), (cap_oring_root / 2, cg1),
               (pr, cg1), (pr, z_bore_end - 0.5), (pr - 0.5, z_bore_end), (0, z_bore_end)])
cap = cap.fuse(cyl(2 * housing_r, z_hback, z_split)).fuse(cyl(2 * sock_r, z_sock_mouth, z_hback + 0.01))
cap = cap.fuse(cone(2 * sock_r, z_hback - (housing_r - sock_r), 2 * housing_r, z_hback + 0.01))
sock_cuts, sock_groove = socket_cut(z_sock_mouth, z_sock_floor, groove_at_mouth_side_45=False)
sock_cuts.append(cone(SOCKET_D, z_sock_floor - 0.01, PILOT_CH_D, z_sock_floor + (SOCKET_D - PILOT_CH_D) / 2))
cap_screws, cap_holes, cap_pilots = [], [], []
for a in CAP_SCREW_ANGLES:
    d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
    o = V(d.x * housing_r, d.y * housing_r, z_cs)
    cap_holes.append(Part.makeCylinder(CAP_SCREW_HOLE / 2, HOUSING_WALL + 2, o + d * 1.0, -d))
    cap_pilots.append(Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_L + 0.5, o, -d))
    cap_screws += [Part.makeCylinder(1.45, SCREW_L, o, -d), Part.makeCylinder(2.8, 2.0, o, d)]
for c in sock_cuts + [cyl(PILOT_CH_D, z_sock_floor - 0.01, z_bore_end + 1)] + cap_pilots:
    cap = cap.cut(c)
cap = cap.removeSplitter()
for c in cap_holes:
    cart = cart.cut(c)
cart = cart.removeSplitter()

# ---------------------------------------------------------------- piston (shut position)
pz0, pz1 = -PISTON_L, 0.0
gz = pz0 + PISTON_ORING_FROM_BACK
piston = revolve([(0, pz0), (pr - 0.5, pz0), (pr, pz0 + 0.5), (pr, gz - pist_groove_w / 2),
                  (pist_oring_root / 2, gz - pist_groove_w / 2), (pist_oring_root / 2, gz + pist_groove_w / 2),
                  (pr, gz + pist_groove_w / 2), (pr, pz1 - 0.5), (pr - 0.5, pz1), (0, pz1)])
# Printed back face down: the pocket is a 45 deg ceiling and the pad recess
# opens upwards. (Face down, the recess floor was a Ø14 bridge and came out
# as spaghetti.) The O-ring groove keeps both walls square, as on the gauge
# plugs: on a sloped wall the ring climbs and wedges when the piston opens.
piston = piston.cut(cyl(PAD[0] + 0.2, pz1 - PAD_RECESS, pz1 + 1))
piston = piston.cut(Part.makeCone(PISTON_POCKET / 2 + 0.01, 0, PISTON_POCKET / 2 + 0.01, V(0, 0, pz0 - 0.01)))
piston = piston.removeSplitter()
pad = cyl(PAD[0], pz1 - PAD_RECESS, pz1 - PAD_RECESS + PAD[1])
pad.translate(V(0, 0, -(PAD[1] - PAD_RECESS)))          # pad face at z = 0 when shut
piston.translate(V(0, 0, -(PAD[1] - PAD_RECESS)))
piston_open = piston.copy()
piston_open.translate(V(0, 0, -LIFT))

# ---------------------------------------------------------------- rear plug (its own frame: outer face z = 0)
plug_sp, plug_groove = gland(PLUG_FLANGE_T + PLUG_INSERT_LEN, PLUG_FLANGE_T - 0.5, +1)
plug_p = cyl(COLLAR_D, 0, PLUG_FLANGE_T).fuse(plug_sp)
pt = PLUG_FLANGE_T + PLUG_INSERT_LEN
p_floor = pt - SOCKET_DEPTH - PLUG_FUNNEL[1]
pcuts, plug_sock_groove = socket_cut(pt - PLUG_FUNNEL[1], p_floor, groove_at_mouth_side_45=True)
pcuts += [Part.makeCone(SOCKET_D / 2, PLUG_FUNNEL[0] / 2, PLUG_FUNNEL[1] + 0.01, V(0, 0, pt - PLUG_FUNNEL[1])),
          cyl(G18_TAP_D, -1, G18_TAP_DEPTH),
          cone(G18_TAP_D, G18_TAP_DEPTH - 0.01, 4.0, G18_TAP_DEPTH + (G18_TAP_D - 4) / 2),
          cyl(4.0, G18_TAP_DEPTH, p_floor + 0.01)]
pcuts += screw_pilots(PLUG_FLANGE_T + SCREW_FROM_TUBE_END, (60.0, 180.0, 300.0))
for c in pcuts:
    plug_p = plug_p.cut(c)
plug_p = plug_p.removeSplitter()

# ---------------------------------------------------------------- module assembly
area = lambda d: math.pi * d * d / 4
A_tube = area(TUBE_ID)
tube_wall = lambda z0, z1: cyl(TUBE_OD, z0, z1).cut(cyl(TUBE_ID, z0 - 1, z1 + 1))
# Chamber air: tube bore from the plug tip to the rear spigot tip, less the
# housing, struts, socket, piston and the pilot tube (its bore is pilot).
probe = cyl(TUBE_ID, z_rs0 - 400.0, z_rs0)
v_fixed = probe.common(cart).Volume + probe.common(cap).Volume + probe.common(piston).Volume + probe.common(pad).Volume
L_air = (CHAMBER_V * 1000 + v_fixed) / A_tube
for _ in range(4):                       # the pilot tube grows with the chamber
    L_air = (CHAMBER_V * 1000 + v_fixed + area(PILOT_TUBE[0]) * L_air) / A_tube
chamber_len = (z_c0 - z_rs0) + L_air + PLUG_INSERT_LEN      # tube: collar to plug flange
z_end = z_c0 - chamber_len                                   # chamber tube's rear end
plug_dz = z_end - PLUG_FLANGE_T                              # plug frame -> module frame
plug = plug_p.copy()
plug.translate(V(0, 0, plug_dz))
pilot_tube_z = (p_floor + plug_dz + TUBE_PLAY, z_sock_floor - TUBE_PLAY)
pilot_tube_len = pilot_tube_z[1] - pilot_tube_z[0]
pilot_tube = cyl(PILOT_TUBE[0], *pilot_tube_z).cut(cyl(PILOT_TUBE[1], pilot_tube_z[0] - 1, pilot_tube_z[1] + 1))
barrel = tube_wall(z_c1, z_c1 + BARREL_LEN)
chamber = tube_wall(z_end, z_c0)
chamber_air = (cyl(TUBE_ID, z_end + PLUG_INSERT_LEN, z_rs0)
               .cut(cart).cut(cap).cut(piston).cut(pad).cut(cyl(PILOT_TUBE[0], *pilot_tube_z)))
chamber_v = chamber_air.Volume / 1000

# ---------------------------------------------------------------- numbers
A_seat = area(SEAT_D)
A_seat_eff = area(SEAT_D + SEAT_TIP)
A_piston = area(PISTON_D)
A_curtain = math.pi * SEAT_D * LIFT
A_annulus = A_tube - area(2 * housing_r)
A_window = STRUT_N * (2 * ARCH_R * (z_rs0 - z_h0 - ARCH_R) + math.pi * ARCH_R ** 2 / 2)   # arched windows
open_ratio = 1 - A_seat_eff / A_piston
pilot_v = (A_piston * CAVITY + area(PILOT_CH_D) * (z_bore_end - z_sock_floor)
           + area(PILOT_TUBE[1]) * pilot_tube_len + area(4.0) * (p_floor - G18_TAP_DEPTH)) / 1000
dead_v = (area(SEAT_D) * (z_rs0 + 0.5) + area(BORE_D) * (z_tip - z_rs0)) / 1000
F_cart = P_MAX_BAR * 0.1 * (A_tube - A_seat)       # chamber side pushes the cartridge forward
F_plug = P_MAX_BAR * 0.1 * A_tube
pin_oring_stretch = pist_oring_root / PISTON_ORING[0] - 1
cap_oring_stretch = cap_oring_root / PISTON_ORING[0] - 1


def wall_between(a, b):
    return a.distToShape(b)[0]


checks = [
    ("cartridge, housing cap, piston, plug valid single solids",
     all(G.single_solid(s) for s in (cart, cap, piston, plug_p))),
    ("piston (shut and open) clear of the cartridge and the cap",
     all(G.no_overlap(a, b) for a in (piston, piston_open, pad) for b in (cart, cap))),
    ("housing cap clear of the cartridge", G.no_overlap(cap, cart)),
    ("cap O-ring groove behind the bleed hole", cg2 < bleed_z - BLEED_D / 2 - 1.0),
    ("cap spigot land ahead of the groove >= 1.5 mm", z_bore_end - cg2 >= 1.5),
    ("cap screws behind the cap O-ring", z_cs + CAP_SCREW_HOLE / 2 + 1.0 <= cg0),
    ("cap screw hole >= 1.2 mm from the housing end", z_cs - CAP_SCREW_HOLE / 2 - z_split >= 1.2),
    ("cap screw heads clear of the chamber tube", housing_r + 2.0 <= TUBE_ID / 2 - 0.2),
    ("cap screw tips clear of the pilot channel", housing_r - SCREW_L - 0.5 - SCREW_PILOT_D / 2 >= PILOT_CH_D / 2 + 1.0),
    ("pad face on the seat when shut", abs(pad.BoundBox.ZMax) < 1e-6),
    ("piston O-ring inside the housing bore when shut", gz + pist_groove_w / 2 - (PAD[1] - PAD_RECESS) <= z_h0 - 1.0),
    ("bleed hole never covered by the piston",
     bleed_z + BLEED_D / 2 < piston_open.BoundBox.ZMin - 0.3),
    ("seat curtain >= seat area (lift %.1f)" % LIFT, A_curtain >= A_seat),
    ("annulus round the housing >= 1.5 x seat (%.0f mm2)" % A_annulus, A_annulus >= 1.5 * A_seat),
    ("window between the struts >= 2 x seat (%.0f mm2)" % A_window, A_window >= 2 * A_seat),
    ("spigot bore >= seat", area(BORE_D) >= A_seat),
    ("struts clear of the piston", STRUT_R[0] >= pr + 0.3),
    ("opens once the pilot is down to >= 35 %% of the chamber (%.0f %%)" % (open_ratio * 100), open_ratio >= 0.35),
    ("nothing wider than the collar but screw heads",
     max(cart.BoundBox.XMax, cap.BoundBox.XMax, plug_p.BoundBox.XMax) <= COLLAR_D / 2 + 1e-6),
    ("cartridge and plug clear of the tubes",
     all(G.no_overlap(a, b) for a in (cart, cap, plug) for b in (barrel, chamber))),
    ("pilot tube clear of cartridge, cap and plug", all(G.no_overlap(pilot_tube, s) for s in (cart, cap, plug))),
    ("wall groove root -> bore >= 2 mm", root_r - BORE_D / 2 >= 2.0),
    ("wall screw pilot -> bore >= 1.4 mm", spigot_r - SCREW_DEPTH - BORE_D / 2 >= 1.4 - 1e-9),
    ("screw tip inside its pilot", TUBE_OD / 2 - SCREW_L >= spigot_r - SCREW_DEPTH),
    ("rear screws outboard of the rear O-ring", z_c0 - SCREW_FROM_TUBE_END - SCREW_PILOT_D / 2 > rear_groove[1] + 1.0),
    ("front screws outboard of the front O-ring", z_c1 + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < front_groove[0] - 1.0),
    ("plug screws outboard of its O-ring", PLUG_FLANGE_T + SCREW_FROM_TUBE_END + SCREW_PILOT_D / 2 < plug_groove[0] - 1.0),
    ("socket wall at the groove >= 1.5 mm", sock_r - sock_groove_r >= 1.5),
    ("tube O-ring stretch 0..6 %", 0 <= oring_stretch <= 0.06),
    ("piston and cap O-ring stretch 0..6 %", all(0 <= x <= 0.06 for x in (pin_oring_stretch, cap_oring_stretch))),
    ("chamber volume %.0f cm3 within 3 %% of target" % chamber_v, abs(chamber_v - CHAMBER_V) <= 0.03 * CHAMBER_V),
]

report = [
    NAME,
    "  flow path              : seat Ø%.0f (%.0f mm2), curtain %.0f at lift %.1f, annulus %.0f, window %.0f, bore Ø%.0f"
    % (SEAT_D, A_seat, A_curtain, LIFT, A_annulus, A_window, BORE_D),
    "  piston                 : Ø%.0f, O-ring %g x %g, pad Ø%g x %g; opens when pilot < %.0f %% of chamber"
    % (PISTON_D, PISTON_ORING[0], PISTON_ORING[1], PAD[0], PAD[1], open_ratio * 100),
    "  pilot                  : %.1f cm3 in the module (PA tube 6/4 x %.0f mm), bleed Ø%.1f in the housing"
    % (pilot_v, pilot_tube_len, BLEED_D),
    "  chamber                : %.0f cm3, tube %.0f mm (collar to plug flange)" % (chamber_v, chamber_len),
    "  dead volume behind ball: %.1f cm3" % dead_v,
    "  module                 : Ø%.0f (screw heads +2 each side), length %.0f mm with a %.0f mm barrel; pack pitch %.0f"
    % (COLLAR_D, z_c1 + BARREL_LEN - z_end, BARREL_LEN, PACK_PITCH),
    "  @ %.0f bar               : cartridge pushed %.0f N forward, plug %.0f N back (3 screws each)"
    % (P_MAX_BAR, F_cart, F_plug),
    "  cartridge / cap / piston / plug: %.1f / %.1f / %.1f / %.1f cm3"
    % (cart.Volume / 1000, cap.Volume / 1000, piston.Volume / 1000, plug_p.Volume / 1000),
]
report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in checks]
if not STAGE3V2_LIBRARY:
    print("\n".join(report))

# ---------------------------------------------------------------- references
def torus(d_root, cs, z, r_center=None):
    rc = r_center if r_center is not None else d_root / 2 + cs / 2
    return Part.makeTorus(rc, cs / 2, V(0, 0, z), Z)


orings = G.fuse_all([
    torus(2 * root_r, ORING_CS, z_rs0 + GROOVE_WALL_FROM_TIP - GROOVE_ROOT_W / 2),
    torus(2 * root_r, ORING_CS, z_tip - GROOVE_WALL_FROM_TIP - GROOVE_ROOT_W / 2),
    torus(2 * root_r, ORING_CS, plug_dz + PLUG_FLANGE_T + PLUG_INSERT_LEN - GROOVE_WALL_FROM_TIP + GROOVE_ROOT_W / 2),
    torus(pist_oring_root, PISTON_ORING[1], gz - (PAD[1] - PAD_RECESS)),
    torus(cap_oring_root, PISTON_ORING[1], cz),
    torus(0, SOCKET_ORING[1], sum(sock_groove) / 2, PILOT_TUBE[0] / 2 + SOCKET_ORING[1] / 2),
    torus(0, SOCKET_ORING[1], sum(plug_sock_groove) / 2 + plug_dz, PILOT_TUBE[0] / 2 + SOCKET_ORING[1] / 2),
])
fitting = G.push_in_fitting(0, 0, 0)
fitting.rotate(V(0, 0, 0), X, 180)
fitting.translate(V(0, 0, plug_dz))
screws = []
for z, angles in ((z_c0 - SCREW_FROM_TUBE_END, (0, 120, 240)), (z_c1 + SCREW_FROM_TUBE_END, (60, 180, 300)),
                  (z_end + SCREW_FROM_TUBE_END, (60, 180, 300))):
    for a in angles:
        d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        o = V(d.x * TUBE_OD / 2, d.y * TUBE_OD / 2, z)
        screws += [Part.makeCylinder(1.45, SCREW_L, o, -d), Part.makeCylinder(2.8, 2.0, o, d)]
ball = Part.makeSphere(TUBE_ID / 2, V(0, 0, z_tip + TUBE_ID / 2))

# ---------------------------------------------------------------- document
# Skipped when another script loads this file for its shapes (STAGE3V2_LIBRARY).
if not STAGE3V2_LIBRARY:
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = FV.Scene(NAME)
    doc = sc.doc
    for n, s, style in (("Cartridge", cart, "rotor"), ("Housing_cap", cap, "rotor"), ("Piston", piston, "stator"),
                        ("Pad", pad, "shoe"),
                        ("Rear_plug", plug, "rotor")):
        sc.add("Printed", n, s, style)
    for n, s, style in (("Barrel_tube", barrel, "ghost"), ("Chamber_tube", chamber, "ghost"),
                        ("Pilot_tube", pilot_tube, "hose"), ("ORings", orings, "oring"),
                        ("Tube_screws", G.fuse_all(screws), "steel"), ("Cap_screws", G.fuse_all(cap_screws), "steel"), ("Pilot_fitting", fitting, "steel"),
                        ("Ball", ball, "flow")):
        sc.add("Bought", n, s, style)
    sc.add("Open", "Piston_open", piston_open, "stator")
    half = Part.makeBox(100, 50, 1200, V(-50, -50, -800))
    for n in ("Cartridge", "Housing_cap", "Piston", "Pad", "Rear_plug", "Barrel_tube", "Chamber_tube", "Pilot_tube", "ORings", "Ball"):
        style = dict(Cartridge="rotor", Housing_cap="rotor", Piston="stator", Pad="shoe", Rear_plug="rotor", ORings="oring",
                     Pilot_tube="hose", Ball="flow").get(n, "ghost")
        sc.add("Section", "Sec_" + n, sc.src[n].cut(half), style)
    for text, pos in [
        ("СТВОЛ %.0f мм" % BARREL_LEN, (-25, 0, z_c1 + BARREL_LEN * 0.7)),
        ("ШАРИК на упоре картриджа", (-25, 0, z_tip + 15)),
        ("КАРТРИДЖ: седло Ø%.0f, поршень Ø%.0f" % (SEAT_D, PISTON_D), (30, 0, 10)),
        ("КАМЕРА %.0f см3: труба %.0f мм" % (chamber_v, chamber_len), (30, 0, (z_end + z_c0) / 2)),
        ("ПИЛОТНАЯ ТРУБКА PA 6/4", (-30, 0, (z_end + z_c0) / 2 - 30)),
        ("ЗАДНЯЯ ПРОБКА: пилот G1/8 -> M3R110 A", (30, 0, z_end - 10)),
    ]:
        sc.label("Labels", text, pos)
    sc.finish(hidden_groups=("Section", "Open"), opaque_groups=("Section",))
    doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))

    # ---------------------------------------------------------------- exports
    import MeshPart


    def write(shape, name, flip):
        s = shape.copy()
        if flip:
            s.rotate(V(0, 0, 0), X, 180)
        s.translate(V(0, 0, -s.BoundBox.ZMin))
        s.exportStep(os.path.join(OUT_DIR, name + ".step"))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, name + ".stl"))


    for n, s, flip in (("cartridge", cart, True), ("housing_cap", cap, False), ("piston", piston, False), ("rear_plug", plug_p, False),
                       ("pad", cyl(PAD[0], 0, PAD[1]), False)):
        write(s, n, flip)
    with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("written to", OUT_DIR)
