# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: two concepts side by side, as plain masses.

Not parts: blocks and tubes at their rough sizes, to compare the two layouts
before one is drawn properly. Drawn with z along the barrels (+z towards the
muzzle), y up, x to the side; the firing barrel is the top one. fcview shows
the model's +x as up, so everything is turned into that frame when added.

A. "Nagant": one Stage 3 v1-type valve, a turning block of six bare barrels.
   The trigger first turns the block 60 deg (pawl and ratchet) while it
   stands clear of the valve, then a cam pushes the block back onto the
   valve face, where a rubber gasket on each barrel's breech seals it, and
   at the end of the pull the pilot is vented. One chamber (38 x 1.2 tube)
   in the grip, recharged through the bleed between shots.

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
R_A = 27.0
block_d_A = 2 * R_A + BARREL[0] + 6
a_barrels = G.fuse_all([tube(BARREL[0], BARREL[1], 0, BARREL[2], x, y) for x, y in ring_pts(R_A)])
a_plates = cyl(block_d_A, 0, 10).fuse(cyl(block_d_A, BARREL[2] - 10, BARREL[2] - 4))
for x, y in ring_pts(R_A):
    a_plates = a_plates.cut(cyl(BARREL[1] * 2 + 23.8, -1, BARREL[2] + 1, x, y))
a_gaskets = G.fuse_all([cyl(30, -1.5, 0, x, y).cut(cyl(13, -2, 1, x, y)) for x, y in ring_pts(R_A)])
a_axle = cyl(8, -12, BARREL[2] + 6)
a_valve = cyl(58, -42, -4, 0, R_A)                   # v1 body + cap, on the top barrel's axis
a_frame = (box(-12, 12, -R_A - 22, -R_A - 14, -42, BARREL[2] + 6)     # lower strap under the block
           .fuse(box(-12, 12, -R_A - 22, 4, BARREL[2] - 4, BARREL[2] + 6))   # front axle bracket
           .fuse(box(-14, 14, -R_A - 22, R_A - 10, -42, -4)))           # rear frame: axle, valve seat
a_cam = box(-3, 3, -R_A - 14, -R_A - 6, BARREL[2] - 4, BARREL[2] + 2)   # pushes the block back
a_chamber = grip(True, 100, CHAMBER_TUBE[0], -R_A - 10, -30)
a_grip_shell = grip(True, 115, CHAMBER_TUBE[0] + 8, -R_A - 8, -30).cut(a_chamber)
a_guard, a_trig = trigger_set(-R_A - 22, 10)

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
                    ("A_Gaskets", a_gaskets, "shoe"), ("A_Axle", a_axle, "steel"),
                    ("A_Valve_v1", a_valve, "stator"), ("A_Frame", a_frame, "frame"), ("A_Cam", a_cam, "steel"),
                    ("A_Chamber_tube", a_chamber, "ghost"), ("A_Grip", a_grip_shell, "printed"),
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
    ("A: НАГАН — 1 клапан v1, блок 6 стволов Ø%.0f, поджим к прокладке" % block_d_A, (0, R_A + 50, 60)),
    ("A: камера 100 см3 в рукоятке (труба 38x1,2)", (0, -R_A - 130, -40)),
    ("B: 6 КЛАПАНОВ — блок Ø%.0f, камера вокруг каждого ствола" % block_d_B, (B_OFFSET, R_B + 50, 60)),
    ("B: ось с поворотным стыком подачи, боёк по ниппелю", (B_OFFSET, -R_B - 140, -60)),
]:
    sc.label("Labels", text, (pos[1], -pos[0], pos[2]))
sc.finish()
print(NAME, ": A block Ø%.0f, B block Ø%.0f" % (block_d_A, block_d_B))
