# -*- coding: utf-8 -*-
"""
Gatling export: the imported coax module is replaced by a solid envelope.

The station still execs this file and needs the same outer stations (rear face,
tube, stop, nose). The copy GPT reads has none of the internal stack. Context
only: `in` does not take the file back.
"""

from __future__ import print_function

# Live names, so the later rename stays in step with the station file.
# Z stations measured on the current module (mm). Outer diameters only.
_PACK = '''# -*- coding: utf-8 -*-
"""Solid drive pack for one station. Outer envelope, no internal stack."""
import math

import FreeCAD as App
import Part

V = App.Vector

CH_OD = 50.0
BARREL_ID, BARREL_WALL = 23.8, 0.59
BARREL_OD = BARREL_ID + 2 * BARREL_WALL
FIT_INSERT = 30.0
FIT_BORE = 18.0
TIE_R, TIE_ANGLES = 29.0, (30.0, 210.0)
TIE_HOLE = 3.4
EAR_R = 4.0
PACK_PITCH = 68.0

z_ry, z_rp, z_te = -37.2, -29.2, -25.2
z_tf, z_fs = 104.953, 106.953
z_stop = 134.563
z_fit1 = z_stop + FIT_INSERT
NOSE_D = BARREL_ID - 0.5


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0))


def at(r, a_deg, z=0.0):
    a = math.radians(a_deg)
    return V(r * math.cos(a), r * math.sin(a), z)


def _ears(shape, z0, z1):
    for ang in TIE_ANGLES:
        p = at(TIE_R, ang)
        shape = shape.fuse(cyl(2 * EAR_R, z0, z1, p.x, p.y))
    return shape.removeSplitter()


chamber = cyl(CH_OD, z_te, z_tf)
rp = _ears(cyl(CH_OD, z_ry, z_te), z_ry, z_rp)
front_cover = cyl(CH_OD, z_tf - 20.0, z_stop).fuse(
    cyl(NOSE_D, z_stop - 1.0, z_fit1)).removeSplitter()
front_yoke = _ears(cyl(CH_OD, z_fs, z_fs + 8.0), z_fs, z_fs + 8.0)
barrel_stub = cyl(BARREL_OD, 10.69, z_stop - 7.0)
rods = []
for ang in TIE_ANGLES:
    p = at(TIE_R, ang)
    rods.append(cyl(3.0, z_ry - 4.9, z_fs + 13.0, p.x, p.y))
hardware = rods[0].fuse(rods[1]).removeSplitter()
diaphragm = cyl(20.0, -1.2, 0.0)
sr = cyl(30.0, -1.2, 20.0)
fitting = cyl(12.0, z_ry - 18.0, z_ry + 6.0)
'''


def apply(rel, text):
    """Return the solid pack for the coax module; leave every other file unchanged."""
    if rel == "gatling/fat_coax_qev.py":
        return _PACK
    return text
