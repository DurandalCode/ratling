# -*- coding: utf-8 -*-
"""
Ratling Stage 3 joint test: can the barrel meet the valve at a flat face?

For a six-barrel pistol with one valve and a turning barrel block, each barrel
would meet the valve's outlet at a flat face with an O-ring on the barrel's
end, and slide over it between shots (no pressure there while the valve is
shut). This pair puts that joint between the Stage 3 v1 body and its barrel:

    v1 barrel spigot ──> valve face (A) ║ barrel breech (B) ──> barrel tube
                         sleeve, flange ║ flange with a face O-ring groove,
                                        ║ spigot into the tube (v1's gland)

    3 x M3 through both flanges set the gap with washers:
      O-ring in, flanges touching ......... the joint at best
      O-ring in, 0.3 mm gap ............... a block that turns
      no O-ring, 0.3 mm gap ............... what a bare gap costs
    and compare each with the barrel straight on the v1 spigot.

Parts, each exported in its print orientation (lowest point at z = 0):

    valve_face .... flange on the bed, sleeve up; slides over the v1 barrel
                    spigot (its O-ring seals in the sleeve), held by three
                    ST2.9 x 6.5 through the sleeve into v1's screw pilots.
    barrel_breech . flange face (O-ring groove) on the bed, spigot up.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_joint_test.py').read())
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
STAGE3_LIBRARY = True
exec(open(os.path.join(REPO, "module", "stage3_qev.py")).read())      # v1 shapes and numbers
STAGE3_LIBRARY = False

NAME = "stage3_joint_test"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- parameters
FLANGE_D = 44.0
FLANGE_T = 5.0
SLEEVE_BORE = TUBE_ID + 0.1         # printed bores come out a touch small
SLEEVE_WALL = 2.5
JT_BOLT_R = 18.5                    # M3 through both flanges
JT_BOLT_D = 3.4
JT_BOLT_ANGLES = (90.0, 210.0, 330.0)
FACE_ORING = (ORING_ID, ORING_CS)   # the 11/16" x 1/8" in hand
FACE_SQUEEZE = 0.20                 # with the flanges touching
FACE_GROOVE_W = 1.2                 # x CS
SLEEVE_SCREW_L = 6.5                # ST2.9 x 6.5: sleeve wall + v1's pilot depth

# ---------------------------------------------------------------- derived
face_groove_depth = FACE_ORING[1] * (1 - FACE_SQUEEZE)
face_groove_out = FACE_ORING[0] / 2 + FACE_ORING[1]  # pressure inside: the ring bears on the outer wall
face_groove_in = face_groove_out - FACE_GROOVE_W * FACE_ORING[1]
sleeve_len = BARREL_SPIGOT_LEN
sleeve_out_r = SLEEVE_BORE / 2 + SLEEVE_WALL


def bolt_holes(z0, z1):
    return [cyl(JT_BOLT_D / 2, z0, z1, V(JT_BOLT_R * math.cos(math.radians(a)),
                                         JT_BOLT_R * math.sin(math.radians(a)))) for a in JT_BOLT_ANGLES]


# ---------------------------------------------------------------- valve face (A), print frame: face at z = 0
vf = cyl(FLANGE_D / 2, 0, FLANGE_T).fuse(cyl(sleeve_out_r, FLANGE_T - 0.01, FLANGE_T + sleeve_len))
cuts = [cyl(seat_r, -1, FLANGE_T + 1), cyl(SLEEVE_BORE / 2, FLANGE_T, FLANGE_T + sleeve_len + 1)]
cuts += bolt_holes(-1, FLANGE_T + 1)
# v1's spigot: tip at the flange, screw pilots SCREW_FROM_TUBE_END from its root (the sleeve's open end)
z_screw = FLANGE_T + sleeve_len - SCREW_FROM_TUBE_END
for a in barrel_screw_angles:
    d = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
    cuts.append(Part.makeCylinder(1.6, SLEEVE_WALL + 2, V(d.x * (sleeve_out_r + 1), d.y * (sleeve_out_r + 1), z_screw), -d))
for c in cuts:
    vf = vf.cut(c)
vf = vf.removeSplitter()

# ---------------------------------------------------------------- barrel breech (B), print frame: face at z = 0
bb = cyl(FLANGE_D / 2, 0, FLANGE_T)
bsp, bsp_g0, _ = spigot(FLANGE_T, BARREL_SPIGOT_LEN, V(0, 0))
bb = bb.fuse(bsp)
cuts = [cyl(seat_r, -1, FLANGE_T + BARREL_SPIGOT_LEN + 1),
        cyl(face_groove_out, -1, face_groove_depth).cut(cyl(face_groove_in, -2, face_groove_depth + 1))]
cuts += bolt_holes(-1, FLANGE_T + 1)
cuts += screw_pilots(V(0, 0), FLANGE_T + SCREW_FROM_TUBE_END, barrel_screw_angles)
for c in cuts:
    bb = bb.cut(c)
bb = bb.removeSplitter()

# ---------------------------------------------------------------- checks
fill = (math.pi * FACE_ORING[1] ** 2 / 4) / ((face_groove_out - face_groove_in) * face_groove_depth)
checks = {
    "valve face and barrel breech valid single solids": G.single_solid(vf) and G.single_solid(bb),
    "face groove clear of the bore and the bolts":
        face_groove_in - seat_r >= 1.5 and JT_BOLT_R - JT_BOLT_D / 2 - face_groove_out >= 1.5,
    "face O-ring stands %.2f mm proud (>= 0.5 for the 0.3 mm gap)" % (FACE_ORING[1] - face_groove_depth):
        FACE_ORING[1] - face_groove_depth >= 0.5,
    "face groove fill <= 85 %%: %.0f %%" % (fill * 100): fill <= 0.85,
    "bolts outside the sleeve": JT_BOLT_R - JT_BOLT_D / 2 >= sleeve_out_r + 0.5,
    "sleeve screw bites v1's pilot, tip not past it":
        SLEEVE_SCREW_L >= sleeve_out_r - spigot_r + 2.0 and sleeve_out_r - SLEEVE_SCREW_L >= spigot_r - SCREW_DEPTH - 0.1,
}
print(NAME)
print("  face O-ring %g x %g, proud %.2f mm; flanges Ø%.0f, 3 x M3 on R%.1f; sleeve screws ST2.9 x %.1f"
      % (FACE_ORING[0], FACE_ORING[1], FACE_ORING[1] - face_groove_depth, FLANGE_D, JT_BOLT_R, SLEEVE_SCREW_L))
for k, v in checks.items():
    print("  [%s] %s" % ("OK " if v else "FAIL", k))

# ---------------------------------------------------------------- export
os.makedirs(OUT_DIR, exist_ok=True)
import MeshPart
for n, s in (("valve_face", vf), ("barrel_breech", bb)):
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, n + ".stl"))
print("written to", OUT_DIR)
