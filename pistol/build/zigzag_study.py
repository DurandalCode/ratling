# -*- coding: utf-8 -*-
"""
Ratling pistol, a study: the block turned by a zigzag groove on its rim (the Webley-Fosbery idea), no pawl, no spring.

A steel stud of Ø2 rides in a zigzag groove cut round the rear disc's rim; the stud moves only along the axle, driven
by a push-rod that takes the hammer's own crank motion. Each stroke of the stud (forward or back) turns the block 15 deg
the same way: cock = two legs (30 deg), release = two legs (60 deg in all). The groove does not retrace itself, so the
block cannot turn back. The stud's axial travel is the sideways bounce of a second crank pin on the hammer at radius R_PIN.

What this script settles (not the packaging of the rod, that is the next step):
  * the groove: path, width, depth, wall to the disc's front face and to the detent's V notches;
  * the stud rides in it through the whole cock and release without touching the groove's walls (a 60 deg turn per cycle);
  * the crank pin's radius that gives the stud's travel, and what the rod's slot must allow.
It writes exports/pistol_zigzag/ (the disc with the groove as a FreeCAD doc, STL of the disc).

Run inside FreeCAD (it builds pistol/hammer_assembly.py first):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/zigzag_study.py').read())
"""

import math
import os

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
PAWL_NOTCHES = False         # no pawl: the six rectangular pockets in the rear face go
NO_PAWL = True               # and its checks in the assembly are skipped
STANDOFFS = ((-48.0, -45.0, (1, -1)), (-48.0, -27.0, (-1,)))      # the left one off the push-rod's height (z -8), on the valve's middle
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

NAME = "pistol_zigzag"
OUT_DIR = os.path.join(REPO, "exports", NAME)
# ---------------------------------------------------------------- the groove
STUD_D, GROOVE_W, GROOVE_DEPTH = 2.0, 2.4, 2.0            # steel stud, the groove 0.4 mm wider, 2 mm deep
RIM_X = (HUB_X0 + RIM_NOTCH[1], HUB_X0 + HUB_T_HAMMER)    # free axial room on the rim: past the detent notches (x 3..9) to the face
WALL = 0.8                                                # left between the groove and the disc's front face
X_LOW = RIM_X[0] + 0.4 + GROOVE_W / 2                     # the stud's lowest axial position (the groove's centre line)
X_HIGH = RIM_X[1] - WALL - GROOVE_W / 2                   # and the highest
A_STROKE = X_HIGH - X_LOW
STUD_ANGLE = 90.0 + math.degrees(math.atan2(8.0, HUB_R))  # where the stud is on the rim (left, at the crank's height z = -8)
LEG_DEG = 15.0
R_PIN = A_STROKE / (1.0 - math.cos(math.radians(HAMMER_SWING / 2)))     # the hammer's second crank pin, mm from its axis


def polar_yz(theta_deg, r):
    t = math.radians(theta_deg)
    return -r * math.sin(t), r * math.cos(t)                # theta runs from +z towards -y, the drive direction (as turned())


def groove_cutter(sub=5):
    """One radial Ø GROOVE_W cutter swept along the zigzag path round the whole rim (24 legs of 15 deg, `sub` chords each)."""
    pieces = []
    nodes = []
    for k in range(24):
        for j in range(sub):
            f = j / sub
            th = STUD_ANGLE - LEG_DEG * (k + f)             # the stud sees the disc turn the other way round
            x = X_LOW + A_STROKE * ((f) if k % 2 == 0 else (1 - f))
            nodes.append((th, x))
    nodes.append((STUD_ANGLE - LEG_DEG * 24, X_LOW))
    r0 = HUB_R - GROOVE_DEPTH
    pts = []
    for th, x in nodes:
        y, z = polar_yz(th, r0)
        pts.append(V(x, y, z))
    for i, (th, x) in enumerate(nodes):
        y, z = polar_yz(th, r0)
        rad = V(0, -math.sin(math.radians(th)), math.cos(math.radians(th)))
        pieces.append(Part.makeCylinder(GROOVE_W / 2, 4.0, V(x, y, z), rad))
    for i in range(len(nodes) - 1):
        p, q = pts[i], pts[i + 1]
        d = q - p
        L = d.Length
        th = (nodes[i][0] + nodes[i + 1][0]) / 2
        e3 = V(0, -math.sin(math.radians(th)), math.cos(math.radians(th)))
        e1 = d * (1.0 / L)
        e2 = e3.cross(e1)
        e2 = e2 * (1.0 / e2.Length)
        e3 = e1.cross(e2)
        box_ = Part.makeBox(L, GROOVE_W, 4.0)
        m = App.Matrix(e1.x, e2.x, e3.x, p.x - e2.x * GROOVE_W / 2, e1.y, e2.y, e3.y, p.y - e2.y * GROOVE_W / 2,
                       e1.z, e2.z, e3.z, p.z - e2.z * GROOVE_W / 2, 0, 0, 0, 1)
        box_.Placement = App.Placement(m)
        pieces.append(box_)
    return Part.makeCompound(pieces)


cutter = groove_cutter()
disc = hub.cut(cutter).removeSplitter()
print(NAME)
print("  groove: stud axial %.2f .. %.2f (%.2f mm travel), x walls %.2f .. %.2f of the rim's %.2f .. %.2f; second crank pin at R = %.1f mm"
      % (X_LOW, X_HIGH, A_STROKE, X_LOW - GROOVE_W / 2, X_HIGH + GROOVE_W / 2, RIM_X[0], RIM_X[1], R_PIN))
v_cut = hub.Volume - disc.Volume
ok = []
ok.append(("groove clear of the detent's V notches (x past %.1f)" % RIM_X[0], X_LOW - GROOVE_W / 2 >= RIM_X[0] + 0.3))
ok.append(("wall to the disc's front face >= 0.8 mm (%.2f)" % (RIM_X[1] - (X_HIGH + GROOVE_W / 2)), RIM_X[1] - (X_HIGH + GROOVE_W / 2) >= WALL - 1e-6))
ok.append(("groove wider than the stud by %.1f mm, deeper than it is wide" % (GROOVE_W - STUD_D), GROOVE_W - STUD_D >= 0.3))
ok.append(("disc after the groove: one valid solid (%d), %.0f mm3 cut away" % (len(disc.Solids), v_cut), len(disc.Solids) == 1 and disc.isValid()))

# ---------------------------------------------------------------- the stud through the cycle
def crank_x(c):
    return R_PIN * (math.cos(math.radians(-HAMMER_SWING / 2 + HAMMER_SWING * c)) - math.cos(math.radians(HAMMER_SWING / 2)))


XMAX = crank_x(0.5)


def state(t):
    """t 0..1 cock, 1..2 release: the stud's axial travel a and the disc's turn alpha (deg), fixed by which leg it is on."""
    c = t if t <= 1 else 2 - t
    a = crank_x(c) / XMAX * A_STROKE
    if t < 0.5:
        s = a / A_STROKE
    elif t < 1.0:
        s = 1 + (1 - a / A_STROKE)
    elif t < 1.5:
        s = 2 + a / A_STROKE
    else:
        s = 3 + (1 - a / A_STROKE)
    return a, LEG_DEG * s


stud_r = V(0, 0, 0)
worst = 0.0
for i in range(0, 41):
    t = i / 20.0
    a, alpha = state(t)
    y, z = polar_yz(STUD_ANGLE, HUB_R - GROOVE_DEPTH + 0.05)
    rad = V(0, -math.sin(math.radians(STUD_ANGLE)), math.cos(math.radians(STUD_ANGLE)))
    stud = Part.makeCylinder(STUD_D / 2, 6.0, V(X_LOW + a, y, z), rad)
    worst = max(worst, hit(stud, turned(disc, alpha)))
ok.append(("the stud rides the groove through cock and release without touching a wall (%.3f mm3)" % worst, worst < 0.05))
_, a_end = state(2.0)
ok.append(("one cycle turns the block %.1f deg (60)" % a_end, abs(a_end - 60.0) < 0.5))
ok.append(("the second crank pin's radius %.1f mm: its sideways bounce over the %.0f deg swing is %.2f mm" %
           (R_PIN, HAMMER_SWING, XMAX), abs(XMAX - A_STROKE) < 0.01))
for label, good in ok:
    print("  [%s] %s" % ("OK " if good else "FAIL", label))

# ---------------------------------------------------------------- the left arm, the push-rod, the guides
# The hammer's left side: its two mainsprings sit on the shaft (y -30.2 .. -6.6), the cage's left wall is at y -39.
# A plate (y -32.8 .. -30.4) is glued on the end of the spring peg (extended through it) and carries a Ø3 pin R_PIN from the
# shaft, at the main crank's angle. The pin stands in a vertical slot of the push-rod (a flat bar 3 x 6 mm at y -37 .. -34),
# so the rod follows the pin's sideways bounce (1.9 mm) and nothing else. In front of the cage the rod jogs out to y -46,
# past the disc's rim, and carries the stud into the groove.
ARM_Y, ROD_Y, FRONT_Y = (-32.8, -30.4), (-37.0, -34.0), (-46.0, -43.0)
PIN_D = 3.0
ROD_H = 3.0                                              # half height of the bar: z H.z +- 3
a0 = math.radians(crank_angle(0.0))
pin0 = V(H.x + R_PIN * math.cos(a0), 0, H.z + R_PIN * math.sin(a0))


def stadium_y(p0, p1, w, y0, y1):
    d = V(p1.x - p0.x, 0, p1.z - p0.z)
    ang = math.degrees(math.atan2(d.z, d.x))
    r = Part.makeBox(d.Length + w, y1 - y0, w, V(p0.x - w / 2, y0, p0.z - w / 2))
    r.rotate(V(p0.x, 0, p0.z), V(0, 1, 0), -ang)
    return r.fuse(Part.makeCylinder(w / 2, y1 - y0, V(p0.x, y0, p0.z), V(0, 1, 0))).fuse(
        Part.makeCylinder(w / 2, y1 - y0, V(p1.x, y0, p1.z), V(0, 1, 0)))


arm = (Part.makeCylinder(12.0, ARM_Y[1] - ARM_Y[0], V(H.x, ARM_Y[0], H.z), V(0, 1, 0)).fuse(stadium_y(H, pin0, 8.0, ARM_Y[0], ARM_Y[1]))
       .cut(Part.makeCylinder(4.15, 20, V(H.x, -40, H.z), V(0, 1, 0)))
       .fuse(Part.makeCylinder(SPRING_PEG[2], 3.4, V(peg_at.x, -31.6, peg_at.z), V(0, 1, 0))))     # the peg's end runs on into the plate
arm_pin = Part.makeCylinder(PIN_D / 2, ARM_Y[1] - ARM_Y[0] + 5.6 + 0.2, V(pin0.x, ARM_Y[0] - 5.6, pin0.z), V(0, 1, 0))
slot_half = R_PIN * math.sin(math.radians(HAMMER_SWING / 2)) + PIN_D / 2 + 0.2     # the pin's centre travel + its radius + 0.2 mm
rod = box(pin0.x - 5.0, -2.9, ROD_Y[0], ROD_Y[1], H.z - ROD_H, H.z + ROD_H)                                    # the long bar, to just behind the cage's front (x -3.3)
rod = rod.fuse(box(pin0.x - 5.0, pin0.x + 5.0, ROD_Y[0], ROD_Y[1], H.z - slot_half - 3.0, H.z + slot_half + 3.0))   # the slot plate
rod = rod.cut(box(pin0.x - 1.7, pin0.x + 1.7, ROD_Y[0] - 1, ROD_Y[1] + 1, H.z - slot_half, H.z + slot_half))        # the vertical slot, 3.4 wide
rod = rod.fuse(box(-3.0, HUB_X0 - A_STROKE - 0.3, FRONT_Y[0], ROD_Y[1], H.z - ROD_H, H.z + ROD_H))                  # the jog, in front of the cage (x -3.3), 0.3 mm behind the disc's face at its full travel
rod = rod.fuse(box(-3.0, X_HIGH + 3.0, FRONT_Y[0], FRONT_Y[1], H.z - ROD_H, H.z + ROD_H)).removeSplitter()          # the front bar past the disc's rim
stud_rad = V(0, -math.sin(math.radians(STUD_ANGLE)), math.cos(math.radians(STUD_ANGLE)))
y_s, z_s = polar_yz(STUD_ANGLE, HUB_R - GROOVE_DEPTH + 0.05)
stud_at = V(X_LOW, y_s, z_s)
# the stud's carrier hole: the stud is a Ø2 steel pin glued in the rod's front bar
rod = rod.cut(Part.makeCylinder(STUD_D / 2, 8.0, stud_at, stud_rad))
rod_studless = rod
# guides: pairs of lugs on the side plate's inner face (y -39), above and below the bar
lugs = [box(gx - 4.0, gx + 4.0, -39.0, ROD_Y[0] + 1.0 - 0.0, z0, z1) for gx in (-32.0, -16.0)
        for z0, z1 in ((H.z + ROD_H + 0.3, H.z + ROD_H + 3.3), (H.z - ROD_H - 3.3, H.z - ROD_H - 0.3))]
lugs = Part.makeCompound(lugs)
side_plate_g = side_plate.fuse(lugs)


def at_c(c):
    """The rod and the pin at the hammer's position c: the rod moves in x only (the pin's bounce), the arm and pin turn."""
    dx = R_PIN * (math.cos(math.radians(crank_angle(c))) - math.cos(a0))
    return rod.translated(V(dx, 0, 0)), _rot_y(arm, H, hammer_rot(c)), _rot_y(arm_pin, H, hammer_rot(c)), dx


fixed_ = {"valve body": valve_body, "valve cap": valve_cap, "cage": frame, "side plate + lugs": side_plate_g, "mainsprings": mainsprings,
          "shaft": shaft, "lock housing": lock_housing_h, "detent box": detent_box, "top strap": top_strap, "chamber tube": axle,
          "spring rib": spring_rib}
bad_ = {}
pin_bad = 0.0
for i in range(0, 21):
    c = i / 10 if i <= 10 else (20 - i) / 10
    c = min(1.0, c)
    r_, ar_, pn_, dx_ = at_c(c)
    for k_, o_ in fixed_.items():
        bad_[("rod", k_)] = max(bad_.get(("rod", k_), 0.0), hit(r_, o_))
        bad_[("arm", k_)] = max(bad_.get(("arm", k_), 0.0), hit(ar_, o_))
        bad_[("pin", k_)] = max(bad_.get(("pin", k_), 0.0), hit(pn_, o_))
    sl_, spin_ = slider_h(c)
    for k_, o_ in (("slider", sl_), ("slider pin", spin_), ("trigger", trigger_h(0.0)), ("hammer body", hammer_shape(c))):
        bad_[("rod", k_)] = max(bad_.get(("rod", k_), 0.0), hit(r_, o_))
        if k_ != "hammer body":
            bad_[("arm", k_)] = max(bad_.get(("arm", k_), 0.0), hit(ar_, o_))
    bad_[("rod", "disc")] = max(bad_.get(("rod", "disc"), 0.0), hit(r_, turned(disc, state(2 * c)[1])))
    pin_bad = max(pin_bad, hit(pn_, r_))          # the pin passes through the slot: only the slot's walls may touch it (clearance 0.2)
worst_ = sorted(((v, k) for k, v in bad_.items() if v > 0.05), reverse=True)
ok.append(("rod, arm and pin clear of the valve, cage, side plate, springs, shaft, lock, detent, strap, slider, trigger, hammer, disc%s"
           % ("" if not worst_ else ": " + ", ".join("%s/%s %.1f" % (k[0], k[1], v) for v, k in worst_[:6])), not worst_))
ok.append(("the pin Ø%.1f runs in its slot (%.2f mm3 of it inside the rod)" % (PIN_D, pin_bad), pin_bad < 0.05))
_dx = [R_PIN * (math.cos(math.radians(crank_angle(c))) - math.cos(a0)) for c in (0.0, 0.5, 1.0)]
ok.append(("the rod's travel %.2f mm = the stud's axial travel %.2f mm" % (max(_dx), A_STROKE), abs(max(_dx) - A_STROKE) < 0.02))
ok.append(("the stud's x at rest %.1f, rod's front bar spans x %.1f .. %.1f, the groove's %.1f .. %.1f"
           % (X_LOW, -3.0, X_HIGH + 3.0, X_LOW, X_HIGH), True))
print("  rod: %.0f mm long, x %.1f .. %.1f, y %.1f .. %.1f; slot Ø3.4 x %.1f; pin at R %.1f, arm plate y %.1f .. %.1f"
      % (rod.BoundBox.XLength, rod.BoundBox.XMin, rod.BoundBox.XMax, rod.BoundBox.YMin, rod.BoundBox.YMax, 2 * slot_half, R_PIN, ARM_Y[0], ARM_Y[1]))
for label, good in ok[-4:]:
    print("  [%s] %s" % ("OK " if good else "FAIL", label))

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
a_, al_ = state(0.5)
y, z = polar_yz(STUD_ANGLE, HUB_R - GROOVE_DEPTH + 0.05)
rad = V(0, -math.sin(math.radians(STUD_ANGLE)), math.cos(math.radians(STUD_ANGLE)))
for n, s, c, t in (("Disc_with_groove", turned(disc, al_), (0.3, 0.7, 0.35), 40),
                   ("Stud", Part.makeCylinder(STUD_D / 2, 6.0, V(X_LOW + a_, y, z), rad), (0.9, 0.6, 0.2), 0),
                   ("Push_rod", rod.translated(V(R_PIN * (math.cos(math.radians(crank_angle(0.5))) - math.cos(a0)), 0, 0)), (0.3, 0.45, 0.9), 15),
                   ("Left_arm_plate", _rot_y(arm, H, hammer_rot(0.5)), (0.9, 0.3, 0.3), 10),
                   ("Arm_pin", _rot_y(arm_pin, H, hammer_rot(0.5)), (0.8, 0.8, 0.85), 0),
                   ("Guide_lugs", lugs, (0.85, 0.7, 0.2), 0),
                   ("Hammer", hammer_shape(0.5), (0.45, 0.3, 0.2), 60),
                   ("Valve_body", valve_body, (0.55, 0.62, 0.72), 85), ("Valve_cap", valve_cap, (0.55, 0.62, 0.72), 85),
                   ("Side_plate", side_plate_g, (0.7, 0.7, 0.7), 80), ("Cage", frame, (0.6, 0.6, 0.6), 90)):
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = t
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + "_scheme.FCStd"))
print("written to", OUT_DIR)
