# -*- coding: utf-8 -*-
"""
Straight bevel gear for printing. Needs FreeCAD.

The tooth form is an involute laid out in the plane of the big end and
scaled towards the cone apex, so every tooth line runs through the apex as
on a real bevel gear. Addendum and dedendum are taken along the back cone and
projected into that plane (x cos delta), which gives the usual bevel outside
diameter d + 2 m cos delta. Tredgold's virtual-gear correction is left out:
for a 20-tooth 1:1 pair that is good enough for a hand crank, and the mesh is
checked geometrically by the caller.
"""

import math

import FreeCAD as App
import Part


def inv(a):
    return math.tan(a) - a


def tooth_outline(z, m, cos_d, backlash, alpha_deg=20.0, n_flank=8, n_tip=3, n_root=4):
    """Closed 2D outline (list of (x, y)) of a gear with z teeth, pitch radius m z / 2."""
    alpha = math.radians(alpha_deg)
    r = m * z / 2
    rb = r * math.cos(alpha)
    ra = r + m * cos_d
    rf = r - 1.25 * m * cos_d
    # half tooth angle at the pitch circle, thinned by half the backlash
    half_pitch = math.pi / (2 * z) - backlash / (2 * r)

    def half_angle(rho):
        if rho <= rb:
            return half_pitch + inv(alpha)
        return half_pitch + inv(alpha) - inv(math.acos(rb / rho))

    r_start = max(rf, rb)
    flank = [r_start + (ra - r_start) * i / n_flank for i in range(n_flank + 1)]
    pts = []
    step = 2 * math.pi / z
    for k in range(z):
        c = k * step
        one = []
        if rf < rb:
            one.append((rf, c - half_angle(rb)))
        one += [(rho, c - half_angle(rho)) for rho in flank]
        a_tip = half_angle(ra)
        one += [(ra, c - a_tip + 2 * a_tip * i / n_tip) for i in range(1, n_tip)]
        one += [(rho, c + half_angle(rho)) for rho in reversed(flank)]
        if rf < rb:
            one.append((rf, c + half_angle(rb)))
        # root arc to the next tooth
        a0 = c + half_angle(rb if rf < rb else rf)
        a1 = c + step - half_angle(rb if rf < rb else rf)
        one += [(rf, a0 + (a1 - a0) * i / n_root) for i in range(1, n_root)]
        pts += one
    return [(rho * math.cos(a), rho * math.sin(a)) for rho, a in pts]


def bevel_gear(m, z, face, hub_d, hub_l, bore, backlash=0.15, delta_deg=45.0, phase_deg=0.0):
    """Bevel gear with its apex at the origin and axis +Z.

    Teeth run from the small end to the big end (towards +Z); the hub sits
    behind the big end. Returns (shape, info dict).
    """
    delta = math.radians(delta_deg)
    d = m * z
    Re = d / (2 * math.sin(delta))                 # cone distance
    a_e = Re * math.cos(delta)                     # apex to big-end plane, axial
    k = (Re - face) / Re
    outline = tooth_outline(z, m, math.cos(delta), backlash)

    def wire(scale, zpos):
        pts = [App.Vector(x * scale, y * scale, zpos) for x, y in outline]
        pts.append(pts[0])
        return Part.makePolygon(pts)

    teeth = Part.makeLoft([wire(k, a_e * k), wire(1.0, a_e)], True, True)
    hub = Part.makeCylinder(hub_d / 2, hub_l + 0.01, App.Vector(0, 0, a_e - 0.01))
    g = teeth.fuse(hub)
    g = g.cut(Part.makeCylinder(bore / 2, a_e + hub_l + 2, App.Vector(0, 0, a_e * k - 1)))
    if phase_deg:
        g.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), phase_deg)
    info = {
        "pitch_d": d, "cone_distance": Re, "big_end_z": a_e, "small_end_z": a_e * k,
        "od": d + 2 * m * math.cos(delta), "mount": a_e + hub_l,
        "root_d": d - 2 * 1.25 * m * math.cos(delta),
    }
    return g.removeSplitter(), info
