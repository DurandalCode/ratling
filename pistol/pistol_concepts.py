# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: two concepts side by side, as plain masses.

Not parts: blocks and tubes at their rough sizes, to compare the two layouts
before one is drawn properly. Drawn with z along the barrels (+z towards the
muzzle), y up, x to the side; the firing barrel is the top one. fcview shows
the model's +x as up, so everything is turned into that frame when added.

A. "Nagant": the Stage 3 v1.1 valve as it is, firing the bottom barrel of a
   turning block of six bare barrels. v1's chamber tube sits 27 mm from its
   seat, the same radius as the barrel ring, so it runs through the middle
   of the block (free Ø29 there) and is the block's axle: the block turns and
   slides on it. A spacer on v1.1's three M3 pilots brings the valve face
   forward past the chamber tube's screws. The trigger first frees the block
   and turns it 60 deg (pawl and ratchet), then a cam pushes it back onto
   the valve face, where the O-ring on that barrel's breech seals, and at
   the end of the pull the pilot is vented. The chamber recharges through
   the bleed between shots; the grip only holds the trigger valve.

B. "Six valves": six modules of the v4 kind (barrel inside its own 38 x 1.2
   chamber tube) in the turning block. Their pilots are fed through an
   O-ring rotary union on the fixed axle and a restrictor each; a striker at
   the top position presses the pilot vent (Schrader core) of the module in
   front of it. Six shots without waiting.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/pistol_concepts.py').read())
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
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)

NAME = "pistol_concepts"
V = App.Vector
Z = V(0, 0, 1)

BARREL = (25.0, 0.6, 150.0)         # OD, wall, length
CHAMBER_TUBE = (38.0, 1.2)
GRIP_ANGLE = 15.0                   # from vertical, leaning back
B_OFFSET = 200.0                    # concept B drawn this far along x


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def tube(od, wall, z0, z1, x=0.0, y=0.0):
    return cyl(od, z0, z1, x, y).cut(cyl(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def ring_pts(r, n=6, a0=90.0):
    return [(r * math.cos(math.radians(a0 + 360.0 / n * i)), r * math.sin(math.radians(a0 + 360.0 / n * i)))
            for i in range(n)]


def grip(top, length, d, y_at, z_at):
    """A tube-like grip hanging down from (y_at, z_at), leaning back."""
    g = cyl(d, 0, length)
    g.rotate(V(0, 0, 0), V(1, 0, 0), 90 + GRIP_ANGLE)
    g.translate(V(0, y_at, z_at))
    return g


def trigger_set(y_top, z_front):
    guard = box(-4, 4, y_top - 32, y_top - 28, z_front - 40, z_front).fuse(
        box(-4, 4, y_top - 32, y_top, z_front - 4, z_front))
    trig = box(-3, 3, y_top - 22, y_top, z_front - 22, z_front - 16)
    return guard, trig


# ---------------------------------------------------------------- A: Nagant
R_A = 27.0                          # = v1's chamber-to-seat distance
A_BARREL = 180.0
A_CHAMBER = 200.0                   # chamber tube, from the body's top face
A_SPACER = 12.0                     # valve face ahead of the body: clears the chamber tube's screws
block_d_A = 2 * R_A + BARREL[0] + 6
y_fire = -R_A                       # bottom barrel
z_body = -A_SPACER                  # v1.1 body top face
a_barrels = G.fuse_all([tube(BARREL[0], BARREL[1], 0, A_BARREL, x, y) for x, y in ring_pts(R_A, a0=270.0)])
a_plates = cyl(block_d_A, 0, 10).fuse(cyl(block_d_A, A_BARREL - 10, A_BARREL - 4))
for x, y in ring_pts(R_A, a0=270.0):
    a_plates = a_plates.cut(cyl(23.8 + 2 * BARREL[1], -1, A_BARREL + 1, x, y))
a_plates = a_plates.cut(cyl(BARREL[0] + 0.5, -1, A_BARREL + 1))           # bushing on the chamber tube
a_orings = G.fuse_all([cyl(24, -0.6, 0, x, y).cut(cyl(17.5, -1, 1, x, y)) for x, y in ring_pts(R_A, a0=270.0)])
a_chamber = tube(BARREL[0], BARREL[1], z_body, z_body + A_CHAMBER)          # the axle
a_plug = cyl(27, z_body + A_CHAMBER, z_body + A_CHAMBER + 5)
a_body = (cyl(62, z_body - 27, z_body, 0, y_fire).fuse(cyl(28, z_body - 27, z_body))
          .fuse(box(-14, 14, y_fire, 0, z_body - 27, z_body)))               # v1.1 body
a_cap = cyl(62, z_body - 43, z_body - 27, 0, y_fire)                        # v1.1 cap, pilot G1/8 behind
a_spacer = cyl(46, z_body, 0, 0, y_fire).cut(box(-30, 30, y_fire + 14, 30, z_body - 1, 1))
a_frame = (box(-12, 12, y_fire - 22, y_fire - 14, z_body - 43, A_BARREL + 10)   # rail under the block
           .fuse(box(-12, 12, y_fire - 22, 14, z_body + A_CHAMBER - 2, z_body + A_CHAMBER + 10)))  # front bracket
a_cam = box(-3, 3, y_fire - 14, y_fire - 6, A_BARREL - 4, A_BARREL + 4)     # pushes the block back
a_grip = grip(True, 105, 34, y_fire - 24, z_body - 30)
a_trigger_valve = cyl(16, 0, 20)
a_trigger_valve.rotate(V(0, 0, 0), V(1, 0, 0), 90 + GRIP_ANGLE)
a_trigger_valve.translate(V(0, y_fire - 30, z_body - 26))
a_guard, a_trig = trigger_set(y_fire - 22, 10)

# ---------------------------------------------------------------- B: six valves
R_B = 40.0
block_d_B = 2 * R_B + CHAMBER_TUBE[0] + 6
L_CH = 130.0
b_barrels = G.fuse_all([tube(BARREL[0], BARREL[1], -10, BARREL[2], x, y) for x, y in ring_pts(R_B)])
b_chambers = G.fuse_all([tube(CHAMBER_TUBE[0], CHAMBER_TUBE[1], 0, L_CH, x, y) for x, y in ring_pts(R_B)])
b_plugs = G.fuse_all([cyl(CHAMBER_TUBE[0], -24, 0, x, y) for x, y in ring_pts(R_B)])
b_cores = G.fuse_all([cyl(8, -34, -24, x, y) for x, y in ring_pts(R_B)])
b_plates = cyl(block_d_B, L_CH + 2, L_CH + 8).cut(G.fuse_all([cyl(26, L_CH, L_CH + 10, x, y) for x, y in ring_pts(R_B)]))
b_axle = cyl(10, -62, BARREL[2] + 6)
b_union = cyl(22, -62, -40)
b_striker = cyl(5, -48, -34, 0, R_B)
b_frame = (box(-16, 16, -R_B - 28, R_B + 6, -62, -40)            # rear frame: axle, union, striker
           .fuse(box(-12, 12, -R_B - 28, -R_B - 20, -62, BARREL[2] + 6))
           .fuse(box(-12, 12, -R_B - 28, 4, BARREL[2] - 4, BARREL[2] + 6)))
b_grip = grip(True, 105, 34, -R_B - 24, -50)
b_hose = cyl(8, 0, 40)
b_hose.rotate(V(0, 0, 0), V(1, 0, 0), 90 + GRIP_ANGLE)
b_hose.translate(V(0, -R_B - 24 - 100 * math.cos(math.radians(GRIP_ANGLE)), -50 - 100 * math.sin(math.radians(GRIP_ANGLE))))
b_guard, b_trig = trigger_set(-R_B - 28, 0)

# ---------------------------------------------------------------- document
def to_view(shape):
    """Sketch frame (x side, y up, z forward) -> fcview's model frame (+x up)."""
    s = shape.copy()
    s.rotate(V(0, 0, 0), Z, -90)
    return s


sc = FV.Scene(NAME)
doc = sc.doc
for n, s, style in (("A_Barrels", a_barrels, "ghost"), ("A_Block_plates", a_plates, "rotor"),
                    ("A_Breech_orings", a_orings, "oring"), ("A_Chamber_axle", a_chamber, "ghost"),
                    ("A_Chamber_plug", a_plug, "rotor"), ("A_Valve_body_v11", a_body, "rotor"),
                    ("A_Valve_cap_v11", a_cap, "stator"), ("A_Face_spacer", a_spacer, "stator"),
                    ("A_Frame", a_frame, "frame"), ("A_Cam", a_cam, "steel"), ("A_Grip", a_grip, "printed"),
                    ("A_Trigger_valve", a_trigger_valve, "steel"),
                    ("A_Guard", a_guard, "frame"), ("A_Trigger", a_trig, "steel")):
    sc.add("A_Nagant", n, to_view(s), style)
off = V(0, -B_OFFSET, 0)
for n, s, style in (("B_Barrels", b_barrels, "ghost"), ("B_Chambers", b_chambers, "ghost"),
                    ("B_Rear_plugs", b_plugs, "stator"), ("B_Pilot_vents", b_cores, "steel"),
                    ("B_Front_plate", b_plates, "rotor"), ("B_Axle", b_axle, "steel"),
                    ("B_Rotary_union", b_union, "oring"), ("B_Striker", b_striker, "steel"),
                    ("B_Frame", b_frame, "frame"), ("B_Grip", b_grip, "printed"), ("B_Hose", b_hose, "hose"),
                    ("B_Guard", b_guard, "frame"), ("B_Trigger", b_trig, "steel")):
    sc.add("B_Six_valves", n, to_view(s), style, offset=off)
for text, pos in [
    ("A: НАГАН — клапан v1.1 как есть, блок 6 стволов Ø%.0f, стреляет нижний" % block_d_A, (0, R_A + 50, 60)),
    ("A: камера = ось блока (труба 25, %.0f мм)" % A_CHAMBER, (0, 20, A_CHAMBER + 20)),
    ("A: в рукоятке только клапан спуска", (0, -R_A - 140, -40)),
    ("B: 6 КЛАПАНОВ — блок Ø%.0f, камера вокруг каждого ствола" % block_d_B, (B_OFFSET, R_B + 50, 60)),
    ("B: ось с поворотным стыком подачи, боёк по ниппелю", (B_OFFSET, -R_B - 140, -60)),
]:
    sc.label("Labels", text, (pos[1], -pos[0], pos[2]))
sc.finish()
print(NAME, ": A block Ø%.0f, B block Ø%.0f" % (block_d_A, block_d_B))
