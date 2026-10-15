# -*- coding: utf-8 -*-
"""
Ratling Stage 3 floating seal: a test add-on for the v1.1 valve face.

For the six-barrel pistol (pistol/), with the barrel block standing still
along its axis and turning at a small gap in front of the valve: a short
sleeve in the valve face is thrown forward onto the barrel's breech by the
shot itself and drawn back by springs at rest, so the block turns free.

    v1.1 body ║ housing: inlet Ø13 ─> sleeve bore (11/16" O-ring, sliding)
              ║ sleeve ══════════════╗ flange │ springs (4, pen springs) │ collar
              ║          rubber washer Ø17/13 on its nose ─> breech face

    pressure on the sleeve's rear annulus (inside its sliding O-ring, Ø
    SLEEVE_BORE) outweighs that inside the washer on its nose, so the shot
    drives it onto the breech and holds it there; a leak past the sliding
    ring vents round the flange through the collar.

Stack on the v1.1 body's top face, three M3 through all of it into the
body's pilots: housing, collar, washers (the gap under test), barrel breech
(v1.1's, without the O-ring on its face: the washer seals on the flat
inside its groove).

Parts, each exported in its print orientation (lowest point at z = 0):
    housing ... body side on the bed.
    sleeve .... rear end on the bed (groove ceiling at 45 deg).
    collar .... spring pockets up (printed upside down).

Frame: v1.1's body frame shifted, z = 0 at the body's top face, the seat on
the z axis, the chamber tube towards +x.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_floating_seal.py').read())
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
STAGE3_LIBRARY = True
exec(open(os.path.join(REPO, "module", "stage3_qev.py")).read())      # v1.1 shapes and numbers
STAGE3_LIBRARY = False

NAME = "stage3_floating_seal"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- parameters
PLATE_D = BREECH_FLANGE_D           # housing and collar outline = the breech's
FLAT_X = BREECH_FLAT_X              # cut flat clear of the chamber tube
INLET_D = SEAT_D
SLEEVE_BORE = 23.5                  # sliding O-ring 11/16" x 1/8" (in hand)
SLEEVE_CLEAR = 0.1                  # radial
SLIDE_SQUEEZE = 0.12
FLANGE_D, FLANGE_T = 35.0, 3.0
TRAVEL_ROOM = 1.5                   # flange travel above its rest
NOSE_D = 19.0
NOSE_CLEAR = 0.3                    # radial, nose in the collar hole
WASHER = (17.0, 13.0, 1.5)          # rubber, from the diaphragm sheet: OD, ID, t
WASHER_RECESS = 1.0                 # 0.5 proud
NOSE_BELOW_COLLAR = 0.2             # nose face under the collar's top at rest
H_INLET = 2.0
H_SLIDE = 10.0                      # straight sliding bore, below the 45 deg flange seat
COLLAR_T = 6.0
SPRING_POCKET = (5.5, 5.0)          # Ø, depth, in the collar's underside
SPRING_R = 13.8
SPRING_ANGLES = (45.0, 135.0, 225.0, 315.0)
GAPS = (0.5, 1.0)                   # M3 washer stacks under the breech to try

# ---------------------------------------------------------------- derived
slide_root = SLEEVE_BORE - 2 * ORING_CS * (1 - SLIDE_SQUEEZE)
slide_stretch = slide_root / ORING_ID - 1
cone_h = FLANGE_D / 2 - (SLEEVE_BORE / 2 - SLEEVE_CLEAR)   # 45 deg underside of the flange (printed upward)
z1 = H_INLET
z2 = z1 + H_SLIDE + cone_h          # flange's top of cone: it rests on a matching 45 deg seat
h_housing = z2 + FLANGE_T + TRAVEL_ROOM
z_collar_top = h_housing + COLLAR_T
z_nose = z_collar_top - NOSE_BELOW_COLLAR
sleeve_r = SLEEVE_BORE / 2 - SLEEVE_CLEAR
groove_w = 1.3 * ORING_CS
z_rear = z1 + 1.0                   # sleeve's rear end at rest, clear of the inlet floor
area = lambda d: math.pi * d * d / 4


def d_plate(d, z0, z1_):
    """Disc cut flat at FLAT_X (towards the chamber tube)."""
    return cyl(d / 2, z0, z1_).common(Part.makeBox(FLAT_X + d / 2, d, z1_ - z0 + 2, V(-d / 2, -d / 2, z0 - 1)))


def bolt_holes(z0, z1_, d=BREECH_BOLT_HOLE):
    return [cyl(d / 2, z0, z1_, p) for p in breech_bolts]


# ---------------------------------------------------------------- housing
housing = d_plate(PLATE_D, 0, h_housing)
seat = revolve([(0, z2 - cone_h), (SLEEVE_BORE / 2, z2 - cone_h), (FLANGE_D / 2 + 0.2, z2 + 0.2), (0, z2 + 0.2)])
cuts = [cyl(INLET_D / 2, -1, z1 + 0.01), cyl(SLEEVE_BORE / 2, z1, z2 - cone_h + 0.01),
        seat.common(d_plate(FLANGE_D + 0.4, z2 - cone_h - 1, z2 + 1)),
        d_plate(FLANGE_D + 0.4, z2, h_housing + 1)] + bolt_holes(-1, h_housing + 1)
for c in cuts:
    housing = housing.cut(c)
housing = housing.removeSplitter()

# ---------------------------------------------------------------- sleeve (rest position)
g0 = z_rear + 2.0
g1 = g0 + groove_w
sleeve = revolve([(INLET_D / 2, z_rear), (sleeve_r, z_rear), (sleeve_r, g0), (slide_root / 2, g0),
                  (slide_root / 2, g1), (sleeve_r, g1 + (sleeve_r - slide_root / 2)), (sleeve_r, z2 - cone_h),
                  (NOSE_D / 2, z2 - cone_h), (NOSE_D / 2, z_nose), (INLET_D / 2, z_nose)])
flange = d_plate(FLANGE_D, z2, z2 + FLANGE_T).fuse(
    revolve([(sleeve_r - 0.01, z2 - cone_h), (FLANGE_D / 2, z2 + 0.01), (0, z2 + 0.01), (0, z2 - cone_h)])
    .common(d_plate(FLANGE_D, z2 - cone_h, z2 + 0.02)))
sleeve = sleeve.fuse(flange.cut(cyl(INLET_D / 2, z2 - cone_h - 1, z2 + FLANGE_T + 1)))
sleeve = sleeve.cut(cyl(WASHER[0] / 2 + 0.2, z_nose - WASHER_RECESS, z_nose + 1).cut(cyl(INLET_D / 2 + 0.6, z_nose - 2, z_nose + 2)))
sleeve = sleeve.removeSplitter()

# ---------------------------------------------------------------- collar
collar = d_plate(PLATE_D, h_housing, z_collar_top)
cuts = [cyl(NOSE_D / 2 + NOSE_CLEAR, h_housing - 1, z_collar_top + 1)] + bolt_holes(h_housing - 1, z_collar_top + 1)
cuts += [cyl(SPRING_POCKET[0] / 2, h_housing - 0.01, h_housing + SPRING_POCKET[1],
             V(SPRING_R * math.cos(math.radians(a)), SPRING_R * math.sin(math.radians(a)))) for a in SPRING_ANGLES]
for c in cuts:
    collar = collar.cut(c)
collar = collar.removeSplitter()

# ---------------------------------------------------------------- numbers
A_fwd = area(SLEEVE_BORE) - area(INLET_D)
A_back = area(WASHER[0]) - area(INLET_D)
F_net = P_WORK_BAR * 0.1 * (A_fwd - A_back)
washer_proud = WASHER[2] - WASHER_RECESS
bolt_len = BREECH_FLANGE_T + max(GAPS) + COLLAR_T + h_housing + BREECH_PILOT_DEPTH - 2.0

checks = {
    "housing, sleeve, collar valid single solids": all(G.single_solid(s) for s in (housing, sleeve, collar)),
    "sleeve clear of housing and collar at rest": G.no_overlap(sleeve, housing) and G.no_overlap(sleeve, collar),
    "net push on the sleeve forward (%.0f N at %.0f bar)" % (F_net, P_WORK_BAR): F_net >= 20.0,
    "sliding O-ring stretch 0..6 %% (%.1f %%)" % (slide_stretch * 100): 0 <= slide_stretch <= 0.06,
    "sleeve wall under its groove >= 2 mm": (slide_root - INLET_D) / 2 >= 2.0,
    "sliding O-ring stays in the straight bore over the stroke": g1 + TRAVEL_ROOM + 0.5 <= z2 - cone_h,
    "washer bears >= 1.2 mm wide on the breech's flat inside its face groove":
        min(WASHER[0] / 2, face_groove_in) - INLET_D / 2 >= 1.2,
    "nose stroke to the breech covered by the flange's room, every gap":
        all(g + NOSE_BELOW_COLLAR - washer_proud <= TRAVEL_ROOM - 0.3 for g in GAPS),
    "washer clears the breech at rest (smallest gap)": min(GAPS) + NOSE_BELOW_COLLAR - washer_proud > 0,
    "spring pockets clear of the bolts, the nose hole and the flat":
        all(math.hypot(SPRING_R * math.cos(math.radians(a)) - p.x, SPRING_R * math.sin(math.radians(a)) - p.y)
            >= SPRING_POCKET[0] / 2 + BREECH_BOLT_HOLE / 2 + 1.0 for a in SPRING_ANGLES for p in breech_bolts)
        and SPRING_R - SPRING_POCKET[0] / 2 >= NOSE_D / 2 + NOSE_CLEAR + 1.0
        and all(SPRING_R * math.cos(math.radians(a)) + SPRING_POCKET[0] / 2 <= FLAT_X - 0.5 for a in SPRING_ANGLES),
    "springs bear on the flange": SPRING_R + SPRING_POCKET[0] / 2 <= FLANGE_D / 2 - 0.5,
    "flange clear of the bolts": BREECH_BOLT_R - BREECH_BOLT_HOLE / 2 - FLANGE_D / 2 >= 0.8,
}
print(NAME)
print("  sleeve: slides Ø%.1f on an 11/16 x 1/8 O-ring, nose Ø%.0f with a rubber washer %g/%g x %g (%.1f proud)"
      % (SLEEVE_BORE, NOSE_D, WASHER[0], WASHER[1], WASHER[2], washer_proud))
print("  push: forward %.0f mm2, back %.0f mm2 -> %.0f N at %.0f bar; stroke to the breech %s mm"
      % (A_fwd, A_back, F_net, P_WORK_BAR, " / ".join("%.1f" % (g + NOSE_BELOW_COLLAR - washer_proud) for g in GAPS)))
print("  stack on the body: housing %.1f + collar %.0f + washers (%s) + breech flange %.0f; 3 x M3 x %.0f"
      % (h_housing, COLLAR_T, " / ".join("%g" % g for g in GAPS), BREECH_FLANGE_T, 5 * math.ceil(bolt_len / 5)))
for k, v in checks.items():
    print("  [%s] %s" % ("OK " if v else "FAIL", k))

# ---------------------------------------------------------------- export
os.makedirs(OUT_DIR, exist_ok=True)
import MeshPart
collar_print = collar.copy()
collar_print.rotate(V(0, 0), X, 180)
for n, s in (("housing", housing), ("sleeve", sleeve), ("collar", collar_print)):
    s = s.copy()
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    s.exportStep(os.path.join(OUT_DIR, n + ".step"))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(os.path.join(OUT_DIR, n + ".stl"))
print("written to", OUT_DIR)
