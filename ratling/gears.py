# -*- coding: utf-8 -*-
"""
Straight bevel gear for printing. Needs FreeCAD.

The tooth form is an involute laid out in the plane of the big end and
scaled towards the cone apex, so every tooth line runs through the apex as
on a real bevel gear. Addendum and dedendum are taken along the back cone and
projected into that plane (x cos delta), which gives the usual bevel outside
diameter d + 2 m cos delta. Tredgold's virtual-gear correction is left out:
for a 20-tooth 1:1 pair that is good enough for a hand crank, and the mesh is
checked geometrically by the caller. The planar heights are only m cos^2 delta
normal to the pitch cone, so a pair far from 1:1 needs bevel_gear(...,
back_cone=True): the tooth on the back cone, virtual-gear profile, full height.
"""

import math

import FreeCAD as App
import Part


def inv(a):
    return math.tan(a) - a


def _tooth(z, m, h_scale, backlash, alpha, n_flank, n_tip):
    """One tooth centred on angle 0, as (rho, angle) points from root to root.

    z may be fractional (a virtual gear). Heights from the pitch circle are
    m * h_scale (addendum) and 1.25 m * h_scale (dedendum).
    """
    r = m * z / 2
    rb = r * math.cos(alpha)
    ra = r + m * h_scale
    rf = r - 1.25 * m * h_scale
    # half tooth angle at the pitch circle, thinned by half the backlash
    half_pitch = math.pi / (2 * z) - backlash / (2 * r)

    def half_angle(rho):
        if rho <= rb:
            return half_pitch + inv(alpha)
        return half_pitch + inv(alpha) - inv(math.acos(rb / rho))

    r_start = max(rf, rb)
    flank = [r_start + (ra - r_start) * i / n_flank for i in range(n_flank + 1)]
    one = []
    if rf < rb:
        one.append((rf, -half_angle(rb)))
    one += [(rho, -half_angle(rho)) for rho in flank]
    a_tip = half_angle(ra)
    one += [(ra, -a_tip + 2 * a_tip * i / n_tip) for i in range(1, n_tip)]
    one += [(rho, half_angle(rho)) for rho in reversed(flank)]
    if rf < rb:
        one.append((rf, half_angle(rb)))
    return one


def tooth_outline(z, m, cos_d, backlash, alpha_deg=20.0, n_flank=8, n_tip=3, n_root=4):
    """Closed 2D outline (list of (x, y)) of a gear with z teeth, pitch radius m z / 2."""
    tooth = _tooth(z, m, cos_d, backlash, math.radians(alpha_deg), n_flank, n_tip)
    return _ring(z, tooth, m * z / 2 - 1.25 * m * cos_d, n_root)


def _ring(z, tooth, rf, n_root):
    """z copies of one tooth ((rho, angle) points) joined by root arcs at rf, as (x, y)."""
    pts = []
    step = 2 * math.pi / z
    for k in range(z):
        c = k * step
        pts += [(rho, c + a) for rho, a in tooth]
        # root arc to the next tooth
        a0 = c + tooth[-1][1]
        a1 = c + step + tooth[0][1]
        pts += [(rf, a0 + (a1 - a0) * i / n_root) for i in range(1, n_root)]
    return [(rho * math.cos(a), rho * math.sin(a)) for rho, a in pts]


def _back_cone_outline(z, m, delta, a_e, z_p, backlash, alpha_deg=20.0, n_flank=8, n_tip=3, n_root=4):
    """Outline in the plane z = z_p of a bevel tooth laid out on the big-end back cone.

    The tooth is that of the virtual gear (Tredgold: z / cos delta teeth, radius
    r / cos delta) on the back cone: a point h above the pitch line and t along
    it sits at radius r + h cos delta, z = a_e - h sin delta, angle t / radius.
    It is projected from the apex onto the plane (the angle is kept), so a loft
    of scaled copies through the apex carries it on every back cone.
    """
    sd, cd = math.sin(delta), math.cos(delta)
    r = m * z / 2.0
    zv = z / cd
    rv = m * zv / 2.0

    def proj(h, t):
        rad = r + h * cd
        return rad * z_p / (a_e - h * sd), t / rad

    tooth = [proj(rho_v - rv, a_v * rho_v)
             for rho_v, a_v in _tooth(zv, m, 1.0, backlash, math.radians(alpha_deg), n_flank, n_tip)]
    rf = proj(-1.25 * m, 0.0)[0]
    return _ring(z, tooth, rf, n_root)


def _apex_prism(outline, k, z_p):
    """Solid between the outline at z_p and its copy scaled by k about the apex.

    Each side quad holds two points and their scaled copies, so it is planar:
    built from plane faces it is the same solid as a ruled loft, but booleans
    and distances on it run several times faster than on the loft's B-splines.
    """
    big = [App.Vector(x, y, z_p) for x, y in outline]
    small = [App.Vector(x * k, y * k, z_p * k) for x, y in outline]
    n = len(big)
    faces = [Part.Face(Part.makePolygon(big + [big[0]])), Part.Face(Part.makePolygon(small + [small[0]]))]
    for i in range(n):
        j = (i + 1) % n
        faces.append(Part.Face(Part.makePolygon([big[i], big[j], small[j], small[i], big[i]])))
    solid = Part.Solid(Part.Shell(faces))
    if solid.Volume < 0:
        solid.reverse()
    return solid


def bevel_gear(m, z, face, hub_d, hub_l, bore, backlash=0.15, delta_deg=45.0, phase_deg=0.0,
               back_cone=False):
    """Bevel gear with its apex at the origin and axis +Z.

    Teeth run from the small end to the big end (towards +Z); the hub sits
    behind the big end. Returns (shape, info dict).

    back_cone=True: full-height teeth (m above, 1.25 m below the pitch cone,
    measured on the back cone), Tredgold profile, trimmed by the big-end back
    cone; the body below the roots reaches 0.5 mm past the big-end root. Needed
    for a pair far from 1:1: the plain form gives the 48-tooth gear of a 16:48
    pair (cone 71.6 deg) teeth 0.2 mm high and the mate jams in them.
    """
    delta = math.radians(delta_deg)
    d = m * z
    Re = d / (2 * math.sin(delta))                 # cone distance
    a_e = Re * math.cos(delta)                     # apex to big-end plane, axial
    k = (Re - face) / Re

    def wire(outline, scale, zpos):
        pts = [App.Vector(x * scale, y * scale, zpos) for x, y in outline]
        pts.append(pts[0])
        return Part.makePolygon(pts)

    if back_cone:
        sd = math.sin(delta)
        z_tip = a_e - m * sd                       # big-end tip on the back cone
        z_p = a_e + 1.25 * m * sd + 0.5            # plane past the big-end root
        outline = _back_cone_outline(z, m, delta, a_e, z_p, backlash)
        k_s = k * z_tip / z_p                      # small end: its tip on the small back cone
        teeth = _apex_prism(outline, k_s, z_p)
        z_bc = a_e + (d / 2) * math.tan(delta)     # back-cone apex on the axis
        z_base = z_p * k_s - 1.0
        teeth = teeth.common(Part.makeCone((z_bc - z_base) / math.tan(delta), 0.0, z_bc - z_base,
                                           App.Vector(0, 0, z_base)))
        z_small = z_p * k_s
    else:
        outline = tooth_outline(z, m, math.cos(delta), backlash)
        teeth = Part.makeLoft([wire(outline, k, a_e * k), wire(outline, 1.0, a_e)], True, True)
        z_small = a_e * k
    hub = Part.makeCylinder(hub_d / 2, hub_l + 0.01, App.Vector(0, 0, a_e - 0.01))
    g = teeth.fuse(hub)
    g = g.cut(Part.makeCylinder(bore / 2, a_e + hub_l + 2, App.Vector(0, 0, z_small - 1)))
    if phase_deg:
        g.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), phase_deg)
    info = {
        "pitch_d": d, "cone_distance": Re, "big_end_z": a_e, "small_end_z": a_e * k,
        "od": d + 2 * m * math.cos(delta), "mount": a_e + hub_l,
        "root_d": d - 2 * 1.25 * m * math.cos(delta),
    }
    return g.removeSplitter(), info
