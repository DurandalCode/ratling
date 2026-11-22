# -*- coding: utf-8 -*-
"""
Jezzail: adapter sleeve that seats the printed v1.2 muzzle bell on the 63 mm tube.

The v1.2 bell (commit 0d3a70a, Ø140 x 168, printed 2026-11-22) was drawn for a
misread 80 mm barrel: socket Ø80.5 x 35 deep, a 40 deg stop cone into a Ø75
throat, then six straight rails, tip circle Ø64.2. The real barrel is a 63 mm
tube, and it would slide straight through those rails. This sleeve fills the
socket and gives the tube an end stop:

    z = 0 ........ tube end of the sleeve (top of the print, socket mouth).
    sleeve ....... OD 80.0 in the Ø80.5 socket, ID 63.5 over the tube; full
                   socket depth, its top edge rests on the bell's stop cone.
    lip .......... inward flange at the bell end, LIP_T thick, Ø LIP_ID: the
                   tube end stops on it; the plunger and the seated ball's
                   lower cap pass through it.

The bell's 3 screw pilots (Ø2.5 at 15 mm from its socket end) stay: drive the
ST2.9 through them into the sleeve, it self-taps; no hole here, so the angle
does not matter.

Print lip down (exported so): a plain ring, no supports. Fits of 0.25 mm per
side: 0.4 nozzle, not 0.8 (docs/print.md).

Overrides are prefixed, a FreeCAD session shares globals between generators:
    JEZZAIL_TUBE_OD = 63.0; JEZZAIL_TUBE_ID = 58.0
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

# ---------------------------------------------------------------- the printed v1.2 bell (0d3a70a)
V12_SOCKET_D = 80.5            # 80.0 guessed barrel + 2 x 0.25
V12_SOCKET_LEN = 35.0
V12_THROAT_D = 75.0
V12_CONE_K = 1.0 / math.tan(math.radians(40))   # stop cone: dz per dr
V12_RAIL_TIP_D = 64.21
V12_BALL_SEAT_Z = 61.71        # ball centre on the rails, from the socket end
V12_SCREW_Z = 15.0

# ---------------------------------------------------------------- parameters
try:
    TUBE_OD = JEZZAIL_TUBE_OD
except NameError:
    TUBE_OD = 63.0             # owner 2026-11-22
try:
    TUBE_ID = JEZZAIL_TUBE_ID
except NameError:
    TUBE_ID = 59.0             # GUESS (63 x 2); measure

FIT = 0.25                     # per side, both fits
LIP_T = 3.0
LIP_ID = 60.0                  # over the tube bore guess: the plunger passes; under the OD: the tube stops
CHAMFER = 0.6                  # lead-in on the sleeve's outer top edge and the bore mouth
BALLS = (65.41, 68.58)         # ITF tennis, seated on the v1.2 rails

NAME = "jezzail_bell_v12_adapter"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- derived (model: z = 0 at the socket mouth, up into the bell)
r_o = V12_SOCKET_D / 2 - FIT
r_i = TUBE_OD / 2 + FIT
r_lip = LIP_ID / 2
L = V12_SOCKET_LEN             # top edge r_o meets the stop cone FIT * K above this
z_lip = L - LIP_T


def V(r, z):
    return App.Vector(r, 0, z)


profile = [V(r_i + CHAMFER, 0), V(r_o - CHAMFER, 0), V(r_o, CHAMFER), V(r_o, L - CHAMFER),
           V(r_o - CHAMFER, L), V(r_lip, L), V(r_lip, z_lip), V(r_i, z_lip), V(r_i, CHAMFER),
           V(r_i + CHAMFER, 0)]
sleeve = Part.Face(Part.makePolygon(profile)).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
sleeve = Part.Solid(Part.Shell(sleeve.Faces)) if sleeve.ShapeType != "Solid" else sleeve

# ---------------------------------------------------------------- reference: v1.2 bell bore, tube, balls
r_sock = V12_SOCKET_D / 2
r_thr = V12_THROAT_D / 2
z_cone = V12_SOCKET_LEN + V12_CONE_K * (r_sock - r_thr)
bell_bore = Part.Face(Part.makePolygon([
    V(0, -1), V(r_sock, -1), V(r_sock, V12_SOCKET_LEN), V(r_thr, z_cone), V(r_thr, z_cone + 40),
    V(0, z_cone + 40), V(0, -1)])).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
bell_wall = Part.makeCylinder(r_sock + 3.0, z_cone + 39, App.Vector(0, 0, 0)).cut(bell_bore)
tube = Part.makeCylinder(TUBE_OD / 2, 300, App.Vector(0, 0, z_lip - 300)).cut(
    Part.makeCylinder(TUBE_ID / 2, 302, App.Vector(0, 0, z_lip - 301)))
balls = [Part.makeSphere(d / 2, App.Vector(0, 0, V12_BALL_SEAT_Z)) for d in BALLS]


def ball_r_at(d, z):
    dz = V12_BALL_SEAT_Z - z
    return math.sqrt(max((d / 2) ** 2 - dz ** 2, 0.0)) if dz < d / 2 else 0.0


# ---------------------------------------------------------------- checks
sb = sleeve.BoundBox
checks = {
    "sleeve valid single solid": sleeve.isValid() and len(sleeve.Solids) == 1,
    "sleeve inside the v1.2 socket (no overlap with the bell wall)": sleeve.common(bell_wall).Volume < 1e-3,
    "sleeve top rests on the stop cone, not the throat": r_o > r_thr,
    "sleeve / tube no interference": sleeve.common(tube).Volume < 1e-3,
    "tube end stops on the lip (>= 1 mm of lip over the tube wall)": r_lip <= TUBE_OD / 2 - 1.0,
    "plunger passes the lip (lip bore >= tube bore)": LIP_ID >= TUBE_ID,
    "the v1.2 rails would not stop the tube on their own": V12_RAIL_TIP_D > TUBE_OD,
    "seated tennis balls clear the lip": all(sleeve.common(b).Volume < 1e-3 for b in balls),
    "seated tennis balls clear the tube end": all(ball_r_at(d, z_lip) < TUBE_ID / 2 - 0.5 for d in BALLS),
    "sleeve wall >= 3 mm": r_o - r_i >= 3.0,
    "screw pilots of the bell land in the sleeve wall": V12_SCREW_Z < z_lip - 3,
}
report = [
    NAME,
    "  v1.2 socket            : Ø%.2f x %.1f; rails tip Ø%.2f" % (V12_SOCKET_D, V12_SOCKET_LEN, V12_RAIL_TIP_D),
    "  tube OD / ID           : %.2f / %.2f   (ID: GUESS until measured)" % (TUBE_OD, TUBE_ID),
    "  sleeve OD / ID / length: %.2f / %.2f / %.1f, wall %.2f" % (2 * r_o, 2 * r_i, L, r_o - r_i),
    "  lip                    : Ø%.1f, %.1f thick; tube end %.1f mm under the socket floor" % (LIP_ID, LIP_T, LIP_T),
    "  ball caps at the lip   : %s" % ", ".join("Ø%.2f -> Ø%.1f" % (d, 2 * ball_r_at(d, z_lip)) for d in BALLS),
    "  volume                 : %.1f cm3 (~%.0f g PLA solid)" % (sleeve.Volume / 1000, sleeve.Volume / 1000 * 1.24),
]
for k, v in checks.items():
    report.append("  [%s] %s" % ("OK " if v else "FAIL", k))
print("\n".join(report))

# ---------------------------------------------------------------- output
sleeve_print = sleeve.copy()
sleeve_print.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
sleeve_print.translate(App.Vector(0, 0, -sleeve_print.BoundBox.ZMin))

os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
g_print = doc.addObject("App::DocumentObjectGroup", "Print")
g_ref = doc.addObject("App::DocumentObjectGroup", "Reference")
p = doc.addObject("Part::Feature", "Adapter_sleeve")
p.Shape = sleeve
g_print.addObject(p)
refs = []
for nm, shp in [("Ref_v12_socket_wall", bell_wall), ("Ref_tube", tube)] + \
        [("Ref_ball_%d" % round(d * 100), b) for d, b in zip(BALLS, balls)]:
    o = doc.addObject("Part::Feature", nm)
    o.Shape = shp
    g_ref.addObject(o)
    refs.append(o)
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    p.ViewObject.ShapeColor = (0.85, 0.45, 0.15)
    refs[0].ViewObject.ShapeColor = (0.45, 0.42, 0.38)
    refs[0].ViewObject.Transparency = 60
    refs[1].ViewObject.ShapeColor = (0.33, 0.40, 0.22)
    refs[1].ViewObject.Transparency = 50
    for o in refs[2:]:
        o.ViewObject.ShapeColor = (0.80, 0.90, 0.20)
        o.ViewObject.Transparency = 60
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")

doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
Part.export([p], os.path.join(OUT_DIR, NAME + ".step"))
import MeshPart
mesh = MeshPart.meshFromShape(Shape=sleeve_print, LinearDeflection=0.02, AngularDeflection=0.1)
mesh.write(os.path.join(OUT_DIR, NAME + ".stl"))
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("written to", OUT_DIR)
