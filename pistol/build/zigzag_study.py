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

# ---------------------------------------------------------------- document
os.makedirs(OUT_DIR, exist_ok=True)
if NAME in App.listDocuments():
    App.closeDocument(NAME)
doc = App.newDocument(NAME)
a_, al_ = state(0.5)
y, z = polar_yz(STUD_ANGLE, HUB_R - GROOVE_DEPTH + 0.05)
rad = V(0, -math.sin(math.radians(STUD_ANGLE)), math.cos(math.radians(STUD_ANGLE)))
for n, s, c, t in (("Disc_with_groove", turned(disc, al_), (0.3, 0.7, 0.35), 40),
                   ("Stud", Part.makeCylinder(STUD_D / 2, 6.0, V(X_LOW + a_, y, z), rad), (0.9, 0.6, 0.2), 0)):
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = t
doc.recompute()
doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
print("written to", OUT_DIR)
