# -*- coding: utf-8 -*-
"""
Standalone printed cover geometry for a handheld rotary actuator.

No pneumatics, no fluid ports, no valve bodies. Numbers match a real
silhouette used elsewhere, but this file builds only the outer shell,
handle, and bail. Import FreeCAD Part API; run via freecadcmd or the
fixture's build.py.

Part keys returned in PARTS:
  shell_lower, shell_upper, side_left, side_right, grip_left, grip_right, bail
Optional (WITH_ROTOR): rotor_hub
"""

from __future__ import print_function

import math
import os

import FreeCAD as App
import Part

V = App.Vector
XA, YA, ZA = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y=0.0, z=0.0):
    L = x1 - x0
    if L < 0:
        x0, x1, L = x1, x0, -L
    return Part.makeCylinder(d / 2.0, L, V(x0, y, z), XA)


def polar(r, a_deg):
    a = math.radians(a_deg)
    return r * math.cos(a), r * math.sin(a)


def biggest(shape, vmin=1.0):
    solids = [s for s in shape.Solids if s.Volume > vmin]
    if not solids:
        return shape
    if len(solids) == 1:
        return solids[0]
    return max(solids, key=lambda s: s.Volume)


# --- envelope (mm) -----------------------------------------------------------
PIVOT = V(-85.0, 0, -8.0)
HUB_OF_LEVER = 10.0
FRAME = dict(x=(PIVOT.x - HUB_OF_LEVER - 8.0, -1.0), y=(-45.0, 45.0), z=(-76.0, 31.0))
DRUM_R, DRUM_X0 = 42.5, -65.5
SLAB = dict(x=(-108.0, -1.0), y=23.0, z=(-70.0, -5.0))
CHEEK = dict(x=(-96.0, -5.0), y=(23.0, 43.0), z=(-70.0, 18.5))
WALL = 3.0
SPLIT_Z = -45.0
WHEEL_R = 22.5

GRIP_START = V(-92.0, 0, -62.0)
GRIP_ANGLE = 36.0
GRIP_LEN = 118.0
GRIP_SECTIONS = ((0.0, 48, 34), (0.4, 40, 31), (0.8, 44, 33), (1.0, 48, 36))

BAIL_PTS = [V(-7, 0, -71), V(-11, 0, -87), V(-20, 0, -104), V(-38, 0, -114),
            V(-58, 0, -113), V(-76, 0, -100), V(-90, 0, -90), V(-97, 0, -85)]
BAIL_SECTION = (3.2, 2.2)
BAIL_TAB = dict(x=(-9.0, -5.0), y=5.0, t=11.0)

# lever clearance through the crown (pie slot); names stay mechanism-neutral
SPUR_A0, SPUR_A1, SPUR_R, SPUR_Y = 58.0, 210.0, 42.0, 6.5
LEVER_SLOT = dict(x=(-95.0, -40.5), y=(-4.5, 4.5), z=(-71.0, -56.0))

# six-seat rotor blank (fixture C only)
HUB_R, HUB_X0, HUB_T = 42.5, 0.5, 14.0
RING_R = 27.0
BORE_D = 25.0
BORE_ID = 23.8
STUB = 200.0
FRONT_T = 6.0

try:
    WITH_ROTOR
except NameError:
    WITH_ROTOR = False


def build_parts():
    fx, fy, fz = FRAME["x"], FRAME["y"], FRAME["z"]
    heel_x = fx[0] - 7.0

    drum = Part.makeCylinder(DRUM_R, fx[1] - DRUM_X0, V(DRUM_X0, 0, 0), XA)
    ball = Part.makeSphere(DRUM_R, V(DRUM_X0, 0, 0))
    bore = Part.makeCylinder(DRUM_R - WALL, fx[1] - DRUM_X0, V(DRUM_X0, 0, 0), XA)
    ball_bore = Part.makeSphere(DRUM_R - WALL, V(DRUM_X0, 0, 0))
    slab = box(SLAB["x"][0], SLAB["x"][1], -SLAB["y"], SLAB["y"], SLAB["z"][0], SLAB["z"][1])
    cheek = box(CHEEK["x"][0], CHEEK["x"][1], CHEEK["y"][0], CHEEK["y"][1], CHEEK["z"][0], CHEEK["z"][1])
    disc_l = Part.makeCylinder(WHEEL_R, 3.0, V(PIVOT.x, -42.5, PIVOT.z), YA)
    disc_r = Part.makeCylinder(WHEEL_R, 3.0, V(PIVOT.x, 39.5, PIVOT.z), YA)
    cage = disc_l.fuse(disc_r).common(drum.fuse(ball)).common(
        Part.makeCylinder(41.3, 200.0, V(-200, 0, 0), XA))
    fin = box(DRUM_X0 - DRUM_R + 2.5, fx[0] + 4.3, -14.0, 14.0, PIVOT.z - 6.0, PIVOT.z + 18.0)
    room = bore.fuse(ball_bore)
    outer = (drum.fuse(ball).fuse(slab).fuse(cheek).fuse(cage).fuse(fin)).cut(room).removeSplitter()

    # travel tunnels for an internal slider / crank (geometry only)
    outer = outer.cut(box(-64.0, CHEEK["x"][1], 22.4, 38.8, -65.1, 15.2))
    outer = outer.cut(box(-93.5, -44.0, 25.5, 39.0, -26.0, 15.2))
    lip = box(CHEEK["x"][1] - 0.4, SLAB["x"][1], CHEEK["y"][0], CHEEK["y"][1], CHEEK["z"][0], SLAB["z"][1])
    outer = outer.fuse(lip)

    shell = outer

    # lever slots
    shell = shell.cut(box(LEVER_SLOT["x"][0], LEVER_SLOT["x"][1],
                          LEVER_SLOT["y"][0], LEVER_SLOT["y"][1],
                          LEVER_SLOT["z"][0], LEVER_SLOT["z"][1]))
    pie = [V(PIVOT.x, -SPUR_Y, PIVOT.z)]
    for k in range(13):
        q = SPUR_A0 + (SPUR_A1 - SPUR_A0) * k / 12.0
        pie.append(V(PIVOT.x + SPUR_R * math.cos(math.radians(q)),
                     -SPUR_Y,
                     PIVOT.z + SPUR_R * math.sin(math.radians(q))))
    spur = Part.Face(Part.makePolygon(pie + [pie[0]])).extrude(V(0, 2 * SPUR_Y, 0))
    shell = shell.cut(spur)

    # axle bore through the cheek discs
    shell = shell.cut(Part.makeCylinder(4.0, 2 * fy[1], V(PIVOT.x, -fy[1], PIVOT.z), YA))

    # side covers: left flank + right cheek band
    side_cut_l = box(heel_x - 1, fx[1] + 1, -fy[1] - 1, -(SLAB["y"] - 3.0), SLAB["z"][0] - 1, fz[1] + 1)
    side_left = shell.common(side_cut_l)
    if len(side_left.Solids) > 1:
        side_left = Part.makeCompound([s for s in side_left.Solids if s.Volume > 50.0])
    shell = shell.cut(side_cut_l)
    shell = biggest(shell, vmin=1000.0)

    side_cut_r = box(heel_x - 1, SLAB["x"][1] + 0.1, SLAB["y"] - 3.0, fy[1] + 3.0, SLAB["z"][0] - 1, fz[1] + 1)
    side_right = shell.common(side_cut_r)
    if len(side_right.Solids) > 1:
        side_right = Part.makeCompound([s for s in side_right.Solids if s.Volume > 50.0])
    shell = shell.cut(side_cut_r)
    shell = biggest(shell, vmin=1000.0)

    shell_lower = biggest(shell.common(box(-400, 100, -100, 100, -400, SPLIT_Z)), vmin=500.0)
    shell_upper = biggest(shell.common(box(-400, 100, -100, 100, SPLIT_Z, 400)), vmin=500.0)

    # handle
    a = math.radians(GRIP_ANGLE)
    gd = V(-math.cos(a), 0, -math.sin(a))
    gn = V(-math.sin(a), 0, math.cos(a))
    grip = Part.makeLoft(
        [Part.Wire(Part.Ellipse(GRIP_START + gd * (GRIP_LEN * t) + gn * (h / 2),
                                GRIP_START + gd * (GRIP_LEN * t) + YA * (w / 2),
                                GRIP_START + gd * (GRIP_LEN * t)).toShape())
         for t, h, w in GRIP_SECTIONS],
        True, False)
    grip = grip.cut(outer)
    grip_left = biggest(grip.common(box(-400, 100, -100, 0, -400, 100)))
    grip_right = biggest(grip.common(box(-400, 100, 0, 100, -400, 100)))

    # bail under the tray
    gc = Part.BSplineCurve()
    gc.interpolate(BAIL_PTS)
    t0 = gc.tangent(gc.FirstParameter)[0]
    n0 = t0.cross(YA).normalize()
    prof = Part.Ellipse(BAIL_PTS[0] + YA * BAIL_SECTION[0], BAIL_PTS[0] + n0 * BAIL_SECTION[1], BAIL_PTS[0])
    bail = Part.Wire(gc.toShape()).makePipeShell([Part.Wire(prof.toShape())], True, True)
    if bail.ShapeType != "Solid":
        bail = Part.Solid(bail)
    bail = bail.cut(outer)
    gt = BAIL_TAB
    bail = bail.fuse(box(gt["x"][0], gt["x"][1], -gt["y"], gt["y"], SLAB["z"][0] - gt["t"], SLAB["z"][0]))
    bail = bail.cut(Part.makeCylinder(1.25, gt["t"] + 1,
                                      V(sum(gt["x"]) / 2, 0, SLAB["z"][0] - gt["t"] - 0.5), ZA)).removeSplitter()

    parts = {
        "shell_lower": shell_lower,
        "shell_upper": shell_upper,
        "side_left": side_left,
        "side_right": side_right,
        "grip_left": grip_left,
        "grip_right": grip_right,
        "bail": bail,
    }

    if WITH_ROTOR:
        hub = cyl_x(2 * HUB_R, HUB_X0, HUB_X0 + HUB_T)
        front = cyl_x(2 * HUB_R - 6, HUB_X0 + HUB_T + STUB - FRONT_T, HUB_X0 + HUB_T + STUB)
        rotor = hub.fuse(front)
        for i in range(6):
            y, z = polar(RING_R, -90 + 60 * i)
            rotor = rotor.cut(cyl_x(BORE_D + 0.3, HUB_X0 - 1, HUB_X0 + HUB_T + STUB + 1, y, z))
            # keep tubes as hollow solids of odd outline for the silhouette test
            tube = cyl_x(BORE_D, HUB_X0 + 5.0, HUB_X0 + HUB_T + STUB, y, z).cut(
                cyl_x(BORE_ID, HUB_X0 + 4.0, HUB_X0 + HUB_T + STUB + 1, y, z))
            rotor = rotor.fuse(tube)
        rotor = rotor.cut(cyl_x(BORE_D + 0.6, HUB_X0 - 1, HUB_X0 + HUB_T + 1))
        parts["rotor_hub"] = rotor.removeSplitter()

    return parts


# library mode: caller set GEOM_LIBRARY = True before exec
try:
    GEOM_LIBRARY
except NameError:
    GEOM_LIBRARY = False

if not GEOM_LIBRARY:
    PARTS = build_parts()
    print("geometry.py: built %d parts" % len(PARTS))
    for k, sh in PARTS.items():
        vol = sum(s.Volume for s in sh.Solids) if sh.Solids else 0.0
        print("  %-14s solids=%d vol=%.0f" % (k, len(sh.Solids), vol))
