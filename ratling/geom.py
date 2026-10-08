# -*- coding: utf-8 -*-
"""
Ratling selector geometry shared by the stage generators. Needs FreeCAD.

Everything is built in the machine frame of ratling/params.py: Z is the rotor
axis, +Z the front, z = 0 the stator sealing face, the aligned port on +X.
Functions return Part shapes; the stage scripts decide outlines, fixings and
what to export.
"""

import math

import FreeCAD as App
import Part

import ratling.params as P

O = App.Vector(0, 0, 0)
X = App.Vector(1, 0, 0)
Y = App.Vector(0, 1, 0)
Z = App.Vector(0, 0, 1)


# ---------------------------------------------------------------- primitives
def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, App.Vector(x, y, z0), Z)


def cone(d0, z0, d1, z1, x=0.0, y=0.0):
    """Cone from Ø d0 at z0 to Ø d1 at z1 (z1 > z0)."""
    return Part.makeCone(d0 / 2, d1 / 2, z1 - z0, App.Vector(x, y, z0), Z)


def fuse_all(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s


def hex_prism(af, z0, z1, x=0.0, y=0.0):
    r = af / math.sqrt(3)
    pts = [App.Vector(x + r * math.cos(math.radians(60 * i)),
                      y + r * math.sin(math.radians(60 * i)), z0) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, z1 - z0))


def teardrop_x(d, x0, x1, z):
    """Horizontal channel along X, 45 deg roof pointing +Z (prints unsupported)."""
    r = d / 2
    c = Part.makeCylinder(r, x1 - x0, App.Vector(x0, 0, z), X)
    roof = Part.makeBox(x1 - x0, r, r, App.Vector(x0, 0, 0))
    roof.rotate(O, X, 45)
    roof.translate(App.Vector(0, 0, z))
    return c.fuse(roof)


def port_xy(a_deg, r=None):
    a = math.radians(a_deg)
    r = P.PORT_R if r is None else r
    return r * math.cos(a), r * math.sin(a)


# ---------------------------------------------------------------- stator
def centre_inlet_tools(face_z, t):
    """Centre of the stator: lead chamfer, spigot bore, 45 deg roof, inlet, tap.

    face_z is where printed material starts (0, or the plate thickness when a
    face plate is used); t is the stator front face.
    """
    return fuse_all([
        cone(P.spigot_bore_d + 2 * P.LEAD_CHAMFER, face_z - 0.01,
             P.spigot_bore_d, face_z + P.LEAD_CHAMFER),
        cyl(P.spigot_bore_d, face_z - 1, P.spigot_bore_depth),
        cone(P.spigot_bore_d, P.spigot_bore_depth,
             P.PORT_D, P.spigot_bore_depth + P.spigot_cone_h),
        cyl(P.PORT_D, 0, t + 1),
        cyl(P.G18_TAP_DRILL, t - P.G18_TAP_DEPTH, t + 1),
    ])


def port_tools(angles, t):
    """Straight port passages with a G1/8 tap hole from the front face t."""
    tools = []
    for a in angles:
        x, y = port_xy(a)
        tools += [cyl(P.PORT_D, -1, t + 1, x, y),
                  cyl(P.G18_TAP_DRILL, t - P.G18_TAP_DEPTH, t + 1, x, y)]
    return fuse_all(tools)


def port_chamfers(angles, z=0.0):
    """Chamfer on the sealing face at z, so the shoe does not catch."""
    c = P.PORT_CHAMFER
    return fuse_all([cone(P.PORT_D + 2 * c + 0.02, z - 0.01, P.PORT_D, z + c, *port_xy(a))
                     for a in angles])


# ---------------------------------------------------------------- rotor
def spigot():
    """Centre spigot from the rotor face to its tip, O-ring groove cut."""
    tip, lc = P.SPIGOT_TIP_Z, P.LEAD_CHAMFER
    s = cyl(P.spigot_d, P.rotor_face_z - 0.01, tip - lc).fuse(
        cone(P.spigot_d, tip - lc, P.spigot_d - 2 * lc, tip))
    g0, g1 = P.SPIGOT_GROOVE_Z - P.groove_w / 2, P.SPIGOT_GROOVE_Z + P.groove_w / 2
    groove = cyl(P.spigot_d + 2, g0, g1).cut(cyl(P.oring_root_d, g0 - 1, g1 + 1))
    return s.cut(groove)


def rotor_passages():
    """Air path inside the rotor: spigot axis, radial channel, shoe bore."""
    r, sx, zf = P.PORT_D / 2, P.PORT_R, P.rotor_face_z
    return fuse_all([
        cyl(P.PORT_D, P.channel_z - r, P.SPIGOT_TIP_Z + 1),                 # spigot axis
        teardrop_x(P.CHANNEL_D, 0, sx, P.channel_z),                        # radial channel
        cyl(P.PORT_D, P.channel_z - r, P.shoe_floor_z + 0.01, sx),          # down from shoe bore
        cyl(P.shoe_bore_d, P.shoe_floor_z, zf + 1, sx),                     # shoe bore
        cone(P.shoe_bore_d, zf - 0.5, P.shoe_bore_d + 1.0, zf + 0.01, sx),  # mouth chamfer
    ])


def hub_screws(d, z0, z1):
    """The three M3 screws that hold the hub to the rotor back."""
    return fuse_all([cyl(d, z0, z1, *port_xy(a, P.HUB_SCREW_R)) for a in (60, 180, 300)])


# ---------------------------------------------------------------- shoe
def shoe():
    """Shoe in its installed position: face at z = 0, on the aligned port."""
    L, ch = P.SHOE_LEN, P.SHOE_FACE_CHAMFER
    zb = -L
    s = fuse_all([
        cone(P.shoe_d - 2 * ch, zb, P.shoe_d, zb + ch),
        cyl(P.shoe_d, zb + ch, -ch),
        cone(P.shoe_d, -ch, P.shoe_land_d, 0),
    ])
    gz = zb + P.SHOE_GROOVE_FROM_BACK
    groove = cyl(P.shoe_d + 2, gz - P.groove_w / 2, gz + P.groove_w / 2).cut(
        cyl(P.oring_root_d, gz - P.groove_w / 2 - 1, gz + P.groove_w / 2 + 1))
    s = s.cut(groove).cut(cyl(P.PORT_D, zb - 1, 1)).cut(
        cyl(P.SHOE_SPRING_SEAT_D, zb - 1, zb + P.SHOE_SPRING_SEAT_DEPTH))
    s.translate(App.Vector(P.PORT_R, 0, 0))
    return s.removeSplitter()


# ---------------------------------------------------------------- references
# Bought parts and annotations, for the FreeCAD document only.
HOSE_D = 6.0


def push_in_fitting(x, y, t):
    """Generic G1/8 - 6 mm straight push-in: thread in the tap, hex, body, collet."""
    return fuse_all([cyl(9.7, t - 6, t, x, y), hex_prism(P.FITTING_HEX, t, t + 5, x, y),
                     cyl(12.0, t + 5, t + 15, x, y), cyl(10.0, t + 15, t + 18, x, y)])


def hose(x, y, t, length):
    return cyl(HOSE_D, t + 6, t + length, x, y)


def oring(d_root, cs, z, x=0.0, y=0.0):
    """Torus seated on a groove root Ø d_root (radial gland)."""
    return Part.makeTorus(d_root / 2 + cs / 2, cs / 2, App.Vector(x, y, z), Z)


def rotor_orings():
    """The spigot and shoe O-rings in place."""
    gz = -P.SHOE_LEN + P.SHOE_GROOVE_FROM_BACK
    return oring(P.oring_root_d, P.ORING_CS, P.SPIGOT_GROOVE_Z).fuse(
        oring(P.oring_root_d, P.ORING_CS, gz, P.PORT_R))


def spring(x, z0, z1, od=6.0, wire=0.5, coils=5):
    r = od / 2 - wire / 2
    try:
        helix = Part.makeHelix((z1 - z0) / coils, z1 - z0, r)
        helix.translate(App.Vector(x, 0, z0))
        prof = Part.Wire(Part.makeCircle(wire / 2, App.Vector(x + r, 0, z0), Y))
        return Part.Wire(helix.Edges).makePipeShell([prof], True, True)
    except Exception:
        return cyl(od, z0, z1, x).cut(cyl(od - 2 * wire, z0 - 1, z1 + 1, x))


def shoe_spring():
    return spring(P.PORT_R, P.shoe_floor_z, -P.SHOE_LEN + P.SHOE_SPRING_SEAT_DEPTH)


def flow_path(t, hose_len):
    """Air path as a red line with arrow heads: in at the centre, out at the port."""
    cz, sx = P.channel_z, P.PORT_R
    top = t + hose_len
    pts = [App.Vector(0, 0, top), App.Vector(0, 0, cz), App.Vector(sx, 0, cz), App.Vector(sx, 0, top)]
    segs = []
    for a, b in zip(pts, pts[1:]):
        d = b - a
        segs.append(Part.makeCylinder(1.0, d.Length, a, d))
        segs.append(Part.makeCone(3.0, 0, 7.0, a + d * 0.5, d))
    segs += [Part.makeSphere(1.0, p) for p in pts[1:-1]]
    return fuse_all(segs)


# ---------------------------------------------------------------- checks
def single_solid(s):
    return s.isValid() and len(s.Solids) == 1


def no_overlap(a, b):
    return a.common(b).Volume < 1e-3


def open_along(solid, pts):
    """True if none of the points lies inside the solid (air path is open)."""
    return not any(solid.isInside(App.Vector(*p), 1e-4, True) for p in pts)
