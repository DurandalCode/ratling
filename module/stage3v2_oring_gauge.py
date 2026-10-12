# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v2: O-ring groove gauge for the piston and the housing cap.

Short plugs of the piston's diameter, each with the piston's 12 x 2 O-ring
groove at a different root diameter, to try in the printed housing bore and
pick the squeeze that seals and still slides. Notches on the top face count
the plug (1 = shallowest groove, most squeeze). Printed like the piston,
bottom face down; PLA is fine.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3v2_oring_gauge.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")

M = {"REPO": REPO, "STAGE3V2_LIBRARY": True}
exec(open(os.path.join(REPO, "module", "stage3v2_inline.py")).read(), M)

NAME = "stage3v2_oring_gauge"
OUT_DIR = os.path.join(REPO, "exports", NAME)
V = App.Vector

ROOTS = (12.60, 12.45, 12.30, 12.15, 12.00)     # groove root Ø, plug 1..5
PLUG_L = 8.0
HOLE_D = 5.0                                    # push it out with a pin
NOTCH = (1.0, 0.6)                              # width, depth

bore = M["PISTON_D"]
cs = M["PISTON_ORING"][1]
r = bore / 2 - M["PISTON_CLEAR"]
w = M["pist_groove_w"]
z0, z1 = PLUG_L / 2 - w / 2, PLUG_L / 2 + w / 2


def plug(n, root):
    rz = [(HOLE_D / 2, 0), (r - 0.5, 0), (r, 0.5), (r, z0), (root / 2, z0), (root / 2, z1), (r, z1),
          (r, PLUG_L - 0.5), (r - 0.5, PLUG_L), (HOLE_D / 2, PLUG_L)]
    pts = [V(x, 0, z) for x, z in rz]
    s = Part.Face(Part.makePolygon(pts + [pts[0]])).revolve(V(0, 0, 0), V(0, 0, 1), 360)
    s = Part.Solid(s) if s.ShapeType != "Solid" else s
    for i in range(n):
        a = 360.0 / 5 * i
        cut = Part.makeBox(4.0, NOTCH[0], NOTCH[1] + 1, V(r - 3.0, -NOTCH[0] / 2, PLUG_L - NOTCH[1]))
        cut.rotate(V(0, 0, 0), V(0, 0, 1), a)
        s = s.cut(cut)
    return s.removeSplitter()


plugs = [plug(i + 1, d) for i, d in enumerate(ROOTS)]
report = [NAME, "  bore Ø%.1f, O-ring %g x %g, plug Ø%.1f; piston now: root Ø%.2f, cap Ø%.2f"
          % (bore, M["PISTON_ORING"][0], cs, 2 * r, M["pist_oring_root"], M["cap_oring_root"])]
for i, d in enumerate(ROOTS):
    report.append("  plug %d (%d notch%s): root Ø%.2f, squeeze %4.1f %% in Ø%.1f, ring stretch %.1f %%"
                  % (i + 1, i + 1, "" if i == 0 else "es", d, (1 - (bore - d) / 2 / cs) * 100, bore,
                     (d / M["PISTON_ORING"][0] - 1) * 100))
print("\n".join(report))

os.makedirs(OUT_DIR, exist_ok=True)
import MeshPart
for i, s in enumerate(plugs):
    name = "plug_%d" % (i + 1)
    s.exportStep(os.path.join(OUT_DIR, name + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, name + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
