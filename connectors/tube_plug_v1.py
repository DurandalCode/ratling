# -*- coding: utf-8 -*-
"""
Ratling tube plug, V1.

Permanent adapter from a 6 mm push-in fitting to a 25 x 1 mm metal tube.
See docs/requirements.md, "Output connector".

    z = 0 ........ hose end (print bed). G1/8 tapped hole for the push-in
                   fitting; the bed face is the fitting's sealing face.
    boss ......... round, Ø BOSS_D.
    cone ......... 45 deg underside of the flange, so it prints without
                   supports.
    flange ....... tube end stops against its flat top face.
    insert ....... goes into the tube; carries the O-ring groove near the
                   pressurized end and radial pilot holes for self-tapping
                   screws between the O-ring and the tube end
                   (unpressurized side).

Print as generated: hose end down, no supports, 100 % infill.

Run inside FreeCAD (Python console):
    exec(open('/Users/<you>/ratling/connectors/tube_plug_v1.py').read())
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

# ---------------------------------------------------------------- parameters
TUBE_ID = 23.8          # measured
TUBE_WALL = 0.59        # measured
TUBE_OD = TUBE_ID + 2 * TUBE_WALL
TUBE_SHOW_LEN = 60.0    # reference tube length shown in the model

RADIAL_CLEAR = 0.20     # plug body vs tube bore, per side (PLA: prints to size; 0.25 went in loose)
INSERT_LEN = 30.0       # depth of the plug inside the tube
LEAD_CHAMFER = 1.0

# The ring in hand: 11/16" x 1/8" at face value (fit confirmed in PLA). An
# AS568-212 with the same label is really 15.5 x 3.5 and does not suit this tube.
ORING_ID = 11 / 16 * 25.4   # 17.46
ORING_CS = 1 / 8 * 25.4     # 3.18
ORING_SQUEEZE = 0.12    # static seal at 0.5-2 bar; 0.20 would not go in by hand
# Trapezoid groove: square wall on the flange side, where pressure from the
# tip pushes the ring; 45 deg wall on the tip side, so nothing overhangs when
# printed tip up (a square ceiling there sagged into the groove).
GROOVE_ROOT_W = 1.1 * ORING_CS   # flat bottom
GROOVE_WALL_FROM_TIP = 9.0   # square wall, measured from the pressurized tip
GROOVE_MAX_FILL = 0.85  # O-ring section / groove section

SCREW_N = 3
SCREW_PILOT_D = 2.5     # for ST2.9 / M3 self-tapping into plastic
SCREW_DEPTH = 6.0       # radial depth into the plug
SCREW_FROM_TUBE_END = 8.0
TUBE_SCREW_HOLE_D = 3.0 # drill through the metal tube wall

FLANGE_D = TUBE_OD + 4.0
FLANGE_FLAT = 2.0       # flat part of the flange (the stop face side)

BOSS_D = 18.0
BOSS_LEN = 11.0
TAP_DRILL_D = 8.8       # G1/8 tap drill
TAP_DEPTH = 8.0
BORE_D = 4.0            # air passage

DESIGN_PRESSURE_BAR = 2.0

OUT_DIR = os.path.join(REPO, "exports", "tube_plug_v1")
NAME = "tube_plug_v1"

# ---------------------------------------------------------------- derived
body_r = TUBE_ID / 2 - RADIAL_CLEAR
groove_depth = ORING_CS * (1 - ORING_SQUEEZE)
root_r = TUBE_ID / 2 - groove_depth
boss_r = BOSS_D / 2
flange_r = FLANGE_D / 2
cone_h = flange_r - boss_r              # 45 deg

z_boss = BOSS_LEN
z_flange = z_boss + cone_h + FLANGE_FLAT   # stop face = tube end
z_tip = z_flange + INSERT_LEN
g0 = z_tip - GROOVE_WALL_FROM_TIP         # square wall
g1 = g0 + GROOVE_ROOT_W                   # end of the flat bottom
g2 = g1 + (body_r - root_r)               # top of the 45 deg wall
groove_area = GROOVE_ROOT_W * (body_r - root_r) + (body_r - root_r) ** 2 / 2 \
    + (g2 - g0) * (TUBE_ID / 2 - body_r)  # plus the clearance band above it
groove_fill = math.pi * (ORING_CS / 2) ** 2 / groove_area
z_screw = z_flange + SCREW_FROM_TUBE_END
oring_stretch = 2 * root_r / ORING_ID - 1


def V(r, z):
    return App.Vector(r, 0, z)


profile = [
    V(0, 0), V(boss_r, 0), V(boss_r, z_boss),
    V(flange_r, z_boss + cone_h), V(flange_r, z_flange),
    V(body_r, z_flange),
    V(body_r, g0), V(root_r, g0), V(root_r, g1), V(body_r, g2),
    V(body_r, z_tip - LEAD_CHAMFER), V(body_r - LEAD_CHAMFER, z_tip),
    V(0, z_tip), V(0, 0),
]
face = Part.Face(Part.makePolygon(profile))
plug = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
plug = Part.Solid(plug) if plug.ShapeType != "Solid" else plug

bore = Part.makeCylinder(BORE_D / 2, z_tip + 2, App.Vector(0, 0, -1))
tap = Part.makeCylinder(TAP_DRILL_D / 2, TAP_DEPTH + 1, App.Vector(0, 0, -1)).fuse(
    Part.makeCone(TAP_DRILL_D / 2, BORE_D / 2, (TAP_DRILL_D - BORE_D) / 2,
                  App.Vector(0, 0, TAP_DEPTH)))      # 45 deg roof instead of a flat ceiling
plug = plug.cut(bore).cut(tap)

for i in range(SCREW_N):
    a = 2 * math.pi * i / SCREW_N
    d = App.Vector(math.cos(a), math.sin(a), 0)
    start = App.Vector(d.x * (body_r + 1), d.y * (body_r + 1), z_screw)
    hole = Part.makeCylinder(SCREW_PILOT_D / 2, SCREW_DEPTH + 1, start, -d)
    plug = plug.cut(hole)

plug = plug.removeSplitter()

# reference tube with its screw holes
tube = Part.makeCylinder(TUBE_OD / 2, TUBE_SHOW_LEN, App.Vector(0, 0, z_flange)).cut(
    Part.makeCylinder(TUBE_ID / 2, TUBE_SHOW_LEN + 2, App.Vector(0, 0, z_flange - 1)))
for i in range(SCREW_N):
    a = 2 * math.pi * i / SCREW_N
    d = App.Vector(math.cos(a), math.sin(a), 0)
    start = App.Vector(d.x * (TUBE_OD / 2 + 1), d.y * (TUBE_OD / 2 + 1), z_screw)
    tube = tube.cut(Part.makeCylinder(TUBE_SCREW_HOLE_D / 2, 4, start, -d))

# ---------------------------------------------------------------- checks
area = math.pi * (TUBE_ID / 2) ** 2
checks = {
    "plug valid solid": plug.isValid() and len(plug.Solids) == 1,
    "plug/tube no interference": plug.common(tube).Volume < 1e-6,
    "screws outboard of O-ring": z_screw + SCREW_PILOT_D / 2 < g0 - 1.0,
    "wall screw hole -> bore >= 2.5 mm": body_r - SCREW_DEPTH - BORE_D / 2 >= 2.5,
    "wall groove root -> bore >= 3 mm": root_r - BORE_D / 2 >= 3.0,
    "wall tap hole -> boss >= 3 mm": boss_r - TAP_DRILL_D / 2 >= 3.0,
    "O-ring stretch on the groove root 0..6 %": 0 <= oring_stretch <= 0.06,
    "groove fill <= %.0f %%" % (GROOVE_MAX_FILL * 100): groove_fill <= GROOVE_MAX_FILL,
    "O-ring squeeze 8..25 %": 0.08 <= ORING_SQUEEZE <= 0.25,
    "45 deg groove wall ends below the tip chamfer": g2 <= z_tip - LEAD_CHAMFER - 1.0,
}
report = [
    "%s" % NAME,
    "  tube ID / OD           : %.2f / %.2f" % (TUBE_ID, TUBE_OD),
    "  plug body Ø            : %.2f" % (2 * body_r),
    "  O-ring groove root Ø   : %.2f  depth %.2f  bottom %.2f + 45 deg wall, fill %.0f %%"
    % (2 * root_r, groove_depth, GROOVE_ROOT_W, groove_fill * 100),
    "  O-ring                 : %.2f x %.2f, stretch %.1f %%, squeeze %.0f %%"
    % (ORING_ID, ORING_CS, oring_stretch * 100, ORING_SQUEEZE * 100),
    "  screw pilots           : %d x Ø%.1f, %.1f mm from tube end; tube holes Ø%.1f"
    % (SCREW_N, SCREW_PILOT_D, SCREW_FROM_TUBE_END, TUBE_SCREW_HOLE_D),
    "  overall length         : %.1f" % z_tip,
    "  blow-off force @ %.1f bar: %.0f N" % (DESIGN_PRESSURE_BAR, area * DESIGN_PRESSURE_BAR * 0.1),
    "  plug volume            : %.1f cm3" % (plug.Volume / 1000),
]
for k, v in checks.items():
    report.append("  [%s] %s" % ("OK " if v else "FAIL", k))
print("\n".join(report))

# ---------------------------------------------------------------- output
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
p = doc.addObject("Part::Feature", "Plug")
p.Shape = plug
t = doc.addObject("Part::Feature", "Ref_Tube")
t.Shape = tube
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    t.ViewObject.Transparency = 70
    t.ViewObject.ShapeColor = (0.6, 0.6, 0.65)
    p.ViewObject.ShapeColor = (0.95, 0.55, 0.15)
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
Part.export([p], os.path.join(OUT_DIR, NAME + ".step"))
import MeshPart
mesh = MeshPart.meshFromShape(Shape=plug, LinearDeflection=0.02, AngularDeflection=0.1)
mesh.write(os.path.join(OUT_DIR, NAME + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
