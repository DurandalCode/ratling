# -*- coding: utf-8 -*-
"""
Concept of the 19-barrel valve head, in FreeCAD. Not a print file: the valves are not in hand yet,
and the 12.5 mm button stack is read off the order drawing.

The ring numbers come from valve_rotor.py. Ports, from the order drawing and the body photo:
1(P) and 3(R) on the inner 16 mm face, 2(A) alone on the outer one. Wide faces carry the mounting
holes and no ports.

Stack, muzzle at z = 0, breech toward +z. The head plate is the existing disc (R 98, 10 mm). On its
breech face a cage of ribs holds the bodies and a retainer clamps them. The face cam bears on the
buttons themselves: its face sits 0.3 mm off a free button and the lobe presses 2.0 mm, short of
the valve's own 2.4 mm stop. No separate pushers.

A leaves the outer face as a straight tube, past the plate rim. P and R face the bore. R is a
short open stub into the well: the exhaust is not collected. P drops through the plate on a ray
that misses the rail lugs, climbs outside the cam and ends on a barbed header. There is no ring
manifold. The header is an ordinary hose barb.

  freecadcmd -c "REPO='$PWD'; exec(open('mitrailleuse/valve_head.py').read())"
"""

import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    REPO = os.environ.get("REPO") or REPO
VR = {"__name__": "valve_rotor"}
exec(open(os.path.join(REPO, "mitrailleuse", "valve_rotor.py")).read(), VR)

N = VR["GUN_N"]
R = None  # set from the ring
RADIAL, TANGENTIAL = VR["RADIAL"], VR["TANGENTIAL"]
BODY_W, BODY_T = RADIAL, TANGENTIAL
OVERALL = VR["OVERALL_H"]
BUTTON_D = VR["BUTTON_D"]
NUT_AF = 14.0
BUTTON_STACK = 12.5          # order drawing: body top to button tip, including the nut
BODY_H = OVERALL - BUTTON_STACK
PLATE_R, PLATE_T = VR["HEAD_PLATE_R"], 10.0
PLATE_BORE = 12.0
SHAFT_D = 8.0
DEPRESS = VR["PRESS"]        # button travel under the lobe
APPROACH = 0.3               # disc face stays this clear of a free button
LOBE_H = DEPRESS + APPROACH  # 2.3; the valve's own stop is 2.4
PORT_D = 8.0                 # Rc1/8, shown as a plain hole; the thread is not modelled
PORT_PITCH = 9.5             # order drawing, P to R along the button axis
A_OD = 8.0                   # straight tube on A
A_STICKOUT = 22.0            # past the outer face; the plate rim is inside this
HOSE_OD = 4.0                # PU 4 x 2.5, the tube already used for pilot hoses
BEND = 8.0                   # under the catalogue 10 mm, so the drop still fits inside the well
VENT_LEN = 6.0               # open stub on R; it stops short of the supply bend
DROP = 44.0                  # supply comes down here, inside the valve face at r 57
JOG = 40.0                   # a short turn, only when the ray shifts off the port
Z_RUN = 5.0                  # one tunnel through the 10 mm plate
RISE = 114.0                 # outside the cam, then up to the header
LANE0, LANE = 34.0, 6.0      # outside the cam, one level per hose on a side
# rail lugs are not on this disc (they stay on the frame). The rays still have to miss them.
LUGS = ((86.0, 16.5), (104.0, 12.5))   # pack_frame hull: r of centre, radius
LUG_ANG = tuple(math.radians(a) for a in (45.0, 135.0, 225.0, 315.0))
LUG_PAD = 2.4                # hose radius 2.0 plus a little, centreline to the lug solid
POCKET_CLEAR = 0.4           # valve drops into the cage
RIB_T = 2.2                  # thinner than the 3 mm inner-corner gap
RETAINER_T = 3.0
RETAINER_HOLE = 18.0         # clears the nut's corners (14 mm across flats is 16.2 across corners)
CAM_T = 8.0
FITS = []


def check(ok, text):
    FITS.append(ok)
    print("[%s] %s" % ("OK " if ok else "FAIL", text))
    return ok


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2.0, z1 - z0, App.Vector(x, y, z0), App.Vector(0, 0, 1))


def tube(d_out, d_in, z0, z1):
    return cyl(d_out, z0, z1).cut(cyl(d_in, z0 - 0.2, z1 + 0.2))


def spun(shape, deg):
    s = shape.copy()
    s.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), deg)
    return s


def polar(r, ang):
    return r * math.cos(ang), r * math.sin(ang)


def hex_prism(af, h, z, x, y):
    r = af / math.sqrt(3.0)
    pts = [App.Vector(x + r * math.cos(i * math.pi / 3.0), y + r * math.sin(i * math.pi / 3.0), z)
           for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, h))


def sector(r0, r1, a0, a1, z0, z1, n=None):
    n = n or max(2, int(abs(a1 - a0) / math.radians(4.0)) + 1)
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / float(n)
        pts.append(App.Vector(r1 * math.cos(a), r1 * math.sin(a), z0))
    for i in range(n + 1):
        a = a1 - (a1 - a0) * i / float(n)
        pts.append(App.Vector(r0 * math.cos(a), r0 * math.sin(a), z0))
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, 0, z1 - z0))


def ramp(r0, r1, a0, a1, z_back, h0, h1, n=8):
    """Stepped solid whose valve-side face goes from h0 to h1, proud of z_back toward -z."""
    parts = []
    for i in range(n):
        a = a0 + (a1 - a0) * i / float(n)
        b = a0 + (a1 - a0) * (i + 1) / float(n)
        h = h0 + (h1 - h0) * (i + 0.5) / float(n)
        if h < 0.05:
            continue
        parts.append(sector(r0, r1, a, b, z_back - h, z_back + 0.02, n=1))
    return parts[0].fuse(parts[1:])


# ---------------------------------------------------------------- ring and cam angles
rg = VR["ring"](N, TANGENTIAL, RADIAL, VR["WALL"])
R = rg["R"]
lobe = VR["lobe_hold"](rg["pitch"])
lobe = dict(lobe, h=LOBE_H)
step = 2.0 * math.pi / N

z_body0 = PLATE_T
z_body1 = z_body0 + BODY_H
z_tip = z_body0 + OVERALL          # free button tip
z_ret0 = z_body1
z_ret1 = z_body1 + RETAINER_T
z_mid = z_body0 + BODY_H / 2.0
z_port_r = z_mid - PORT_PITCH / 2.0          # R, toward the muzzle, as on the sketch
z_port_p = z_mid + PORT_PITCH / 2.0          # P, toward the button
# disc face clears a free button by APPROACH; the lobe reaches the pressed tip
z_cam_base = z_tip + APPROACH
z_cam_back = z_cam_base + CAM_T


def valve_angle(j):
    return math.pi / 2.0 - j * step


def cam_rise(ang):
    """Lobe height proud of the base, at this angle. x = 0 is the release edge, on +Y."""
    x = (math.pi / 2.0 - ang) * R
    # fold into one turn so the ramps on either side of the plateau both count
    circ = N * rg["pitch"]
    x = (x + circ / 2.0) % circ - circ / 2.0
    return VR["height"](x, lobe)


def depressed(j):
    return cam_rise(valve_angle(j)) >= LOBE_H - 1e-6


# ---------------------------------------------------------------- parts
def valve_shape(j):
    ang = valve_angle(j)
    down = DEPRESS if depressed(j) else 0.0
    y0 = R - RADIAL / 2.0
    body = Part.makeBox(BODY_T, RADIAL, BODY_H, App.Vector(-BODY_T / 2.0, y0, z_body0))
    z_mid = z_body0 + BODY_H / 2.0
    holes = []
    # A, outer face, one hole. The cylinder starts outside and drills in.
    holes.append(Part.makeCylinder(PORT_D / 2.0, 14.0, App.Vector(0, y0 + RADIAL + 1.0, z_mid),
                                   App.Vector(0, -1, 0)))
    for dz in (-PORT_PITCH / 2.0, PORT_PITCH / 2.0):
        holes.append(Part.makeCylinder(PORT_D / 2.0, 14.0, App.Vector(0, y0 - 1.0, z_mid + dz),
                                       App.Vector(0, 1, 0)))
    body = body.cut(holes)
    # Tall nut, short cap. A 6 mm pin above a thin nut read as a pusher; the cap is the
    # valve's own button, Ø10.6, and it sinks into the nut's bore when the cam presses.
    nut_h = 6.4
    nut_z = z_ret1 + 0.2
    nut = hex_prism(NUT_AF, nut_h, nut_z, 0, R).cut(cyl(11.0, nut_z - 0.2, nut_z + nut_h + 0.4, 0, R))
    button = cyl(BUTTON_D, nut_z + nut_h + 0.15 - down, z_tip - down, 0, R)
    shape = body.fuse(nut).fuse(button)
    return spun(shape, math.degrees(ang - math.pi / 2.0))


def radial_tube(r0, r1, z, od):
    """Straight tube along +Y from r0 to r1. r1 may be inside r0."""
    lo, hi = (r0, r1) if r1 > r0 else (r1, r0)
    return Part.makeCylinder(od / 2.0, hi - lo, App.Vector(0, lo, z), App.Vector(0, 1, 0))


def spun_at(shape, j):
    return spun(shape, math.degrees(valve_angle(j) - math.pi / 2.0))


def outlet_shape(j):
    """Straight tube on A, radially out, past the plate rim. No turn toward the muzzle."""
    face = R + RADIAL / 2.0
    tube = radial_tube(face, face + A_STICKOUT, z_mid, A_OD)
    return spun_at(tube, j)


def _unit(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / n, v[1] / n, v[2] / n)


def _add(a, b, s=1.0):
    return (a[0] + s * b[0], a[1] + s * b[1], a[2] + s * b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _rod(v, k, th):
    ct, st = math.cos(th), math.sin(th)
    kd = _dot(k, v)
    cr = _cross(k, v)
    return tuple(v[i] * ct + cr[i] * st + k[i] * kd * (1.0 - ct) for i in range(3))


def _wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def _at(r, ang, z):
    return (r * math.cos(ang), r * math.sin(ang), z)


def _radial(ang):
    return (math.cos(ang), math.sin(ang), 0.0)


def _tangent(ang, sign):
    return (-sign * math.sin(ang), sign * math.cos(ang), 0.0)


def in_lug(r, ang):
    x, y = r * math.cos(ang), r * math.sin(ang)
    for a in LUG_ANG:
        for cr, rad in LUGS:
            if math.hypot(x - cr * math.cos(a), y - cr * math.sin(a)) < rad + LUG_PAD:
                return True
    return False


def ray_clear(ang, r0, r1):
    r = r0
    while r <= r1 + 1e-6:
        if in_lug(r, ang):
            return False
        r += 1.0
    return True


def bend_points(p, u, target, n=4):
    """Quarter-bend points after p, and the direction at the end."""
    u, target = _unit(u), _unit(target)
    w = _unit(_cross(u, target))
    center = _add(p, _cross(w, u), BEND)
    arm = _add(p, center, -1.0)
    pts = []
    for i in range(1, n + 1):
        pts.append(_add(center, _rod(arm, w, (math.pi / 2.0) * i / n)))
    return pts, _rod(u, w, math.pi / 2.0)


def _dedupe(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 0.3:
            out.append(p)
    return out


def _assign_rays():
    """One ray per valve for the supply hose, the nearest that misses the rail lugs."""
    rays = []
    for j in range(N):
        pref = valve_angle(j)
        ang = None
        for k in range(0, 90):
            for s in (1.0, -1.0):
                a = pref + s * math.radians(0.5 * k)
                if ray_clear(a, DROP, RISE):
                    ang = a
                    break
            if ang is not None:
                break
        if ang is None:
            raise RuntimeError("no lug-clear ray for valve %d" % j)
        rays.append(ang)
    for i in range(N):
        for k in range(i + 1, N):
            gap = abs(_wrap(rays[i] - rays[k]))
            if gap < math.radians(8.0):
                raise RuntimeError("rays %d and %d are %.1f deg apart"
                                   % (i, k, math.degrees(gap)))
    return rays


def vent_shape(j):
    """Open stub on R, into the well. Exhaust is not collected."""
    face = R - RADIAL / 2.0
    tube = radial_tube(face + 2.0, face - VENT_LEN, z_port_r, HOSE_OD)
    return spun_at(tube, j)


def hose_paths():
    """Supply centre lines only. One ray per valve, out through the plate, up outside the cam."""
    rays = _assign_rays()
    man = math.pi / 2.0
    raw = []
    for j in range(N):
        raw.append({"j": j, "port": valve_angle(j), "exit": rays[j], "zp": z_port_p, "zr": Z_RUN})
    for sign in (1.0, -1.0):
        side = [h for h in raw if sign * _wrap(h["exit"] - man) > 1e-9]
        if sign > 0:
            side += [h for h in raw if abs(_wrap(h["exit"] - man)) <= 1e-9]
        side.sort(key=lambda h: abs(_wrap(h["exit"] - man)))
        for k, h in enumerate(side):
            h["lane"] = k
            h["z_lane"] = LANE0 + k * LANE
            h["side"] = sign
    for sign in (1.0, -1.0):
        side = [h for h in raw if h["side"] == sign]
        if not side:
            continue
        head = min(side, key=lambda h: h["lane"])
        for h in side:
            h["header"] = head["exit"]
    for h in raw:
        pts, segs = _hose_points(h)
        h["pts"] = pts
        h["segs"] = segs
        h["end"] = pts[-1]
    return raw


def _push_line(pts, segs, p):
    if math.dist(pts[-1], p) < 0.4:
        return
    segs.append(("L", pts[-1], p))
    pts.append(p)


def _push_bend(pts, segs, u, target):
    samples, u2 = bend_points(pts[-1], u, target, n=8)
    segs.append(("A", pts[-1], samples[3], samples[-1]))
    pts.extend(samples)
    return u2


def _add_arc(pts, segs, r, z, a0, a1):
    sweep = _wrap(a1 - a0)
    if abs(sweep) < math.radians(1.0):
        return
    n_arc = max(3, int(abs(sweep) * r / 6.0))
    prev = pts[-1]
    for s in range(1, n_arc + 1):
        end = _at(r, a0 + sweep * s / float(n_arc), z)
        if s == n_arc:
            segs.append(("A", prev, _at(r, a0 + sweep / 2.0, z), end))
        pts.append(end)


def _hose_points(h):
    ang = h["port"]
    ex = h["exit"]
    z = h["zp"]
    face = R - RADIAL / 2.0
    pts = [_at(face + 3.0, ang, z)]
    segs = []
    if abs(_wrap(ex - ang)) > math.radians(1.0):
        _push_line(pts, segs, _at(JOG, ang, z))
        _add_arc(pts, segs, JOG, z, ang, ex)
    _push_line(pts, segs, _at(DROP + BEND, ex, z))
    u = _push_bend(pts, segs, (-math.cos(ex), -math.sin(ex), 0.0), (0.0, 0.0, -1.0))
    _push_line(pts, segs, _at(DROP, ex, h["zr"] + BEND))
    _push_bend(pts, segs, u, _radial(ex))
    if RISE - BEND > DROP + BEND + 1.0:
        _push_line(pts, segs, _at(RISE - BEND, ex, h["zr"]))
    out = _radial(ex)
    _push_bend(pts, segs, out, (0.0, 0.0, 1.0))
    _push_line(pts, segs, _at(RISE, ex, h["z_lane"] - BEND))
    u = _push_bend(pts, segs, (0.0, 0.0, 1.0), out)
    if abs(_wrap(h["header"] - ex)) > math.radians(2.0):
        sign = 1.0 if _wrap(h["header"] - ex) > 0 else -1.0
        u = _push_bend(pts, segs, u, _tangent(ex, sign))
        r_arc = math.hypot(pts[-1][0], pts[-1][1])
        a_arc = math.atan2(pts[-1][1], pts[-1][0])
        a_stop = h["header"] - sign * (BEND / r_arc)
        sweep = _wrap(a_stop - a_arc)
        if sweep * sign > math.radians(2.0):
            cuts = 2 if abs(sweep) > math.radians(150.0) else 1
            a = a_arc
            for _c in range(cuts):
                a2 = a + sweep / cuts
                n_arc = max(4, int(abs(sweep / cuts) * r_arc / 8.0))
                prev = pts[-1]
                for s in range(1, n_arc + 1):
                    aa = a + _wrap(a2 - a) * s / n_arc
                    end = _at(r_arc, aa, h["z_lane"])
                    if s == n_arc:
                        segs.append(("A", prev, _at(r_arc, a + _wrap(a2 - a) / 2.0, h["z_lane"]), end))
                    pts.append(end)
                a = a2
            u = _tangent(a_stop, sign)
        _push_bend(pts, segs, u, _radial(h["header"]))
    r_end = RISE + 2.0 * BEND + 14.0
    r_here = math.hypot(pts[-1][0], pts[-1][1])
    a_here = math.atan2(pts[-1][1], pts[-1][0])
    if r_end > r_here + 1.0:
        _push_line(pts, segs, _at(r_end, a_here, pts[-1][2]))
    h["header_r"] = r_end + 8.0
    return _dedupe(pts), segs


def _solid_line(p, q, od):
    v = _add(q, p, -1.0)
    length = math.dist(p, q)
    if length < 0.4:
        return None
    return Part.makeCylinder(od / 2.0, length, App.Vector(*p), App.Vector(*v))


def _solid_arc(p0, mid, p1, od):
    edge = Part.Arc(App.Vector(*p0), App.Vector(*mid), App.Vector(*p1)).toShape()
    tangent = edge.tangentAt(edge.FirstParameter)
    face = Part.Face(Part.Wire([Part.makeCircle(od / 2.0, App.Vector(*p0), tangent)]))
    return Part.Wire([edge]).makePipe(face)


def pipe_along(segments, od):
    parts = []
    for seg in segments:
        if seg[0] == "L":
            solid = _solid_line(seg[1], seg[2], od)
        else:
            solid = _solid_arc(seg[1], seg[2], seg[3], od)
        if solid is not None:
            parts.append(solid)
    if len(parts) == 1:
        return parts[0]
    return parts[0].multiFuse(parts[1:])


def nipple(base, direction, length, od):
    """Barbed stem. direction points from the header toward the hose."""
    d = _unit(direction)
    shaft = Part.makeCylinder(od / 2.0, length, App.Vector(*base), App.Vector(*d))
    rings = []
    for t in (0.35, 0.55, 0.75):
        c = _add(base, d, length * t)
        ring = Part.makeTorus(od / 2.0 + 0.6, 0.55, App.Vector(*c), App.Vector(*d))
        rings.append(ring)
    return shaft.fuse(rings)


def manifold_shape(paths):
    """Two barbed headers, one each side of the gun, bridged, with one outlet nipple."""
    group = paths
    parts = []
    z0 = min(h["z_lane"] for h in group) - 8.0
    z1 = max(h["z_lane"] for h in group) + 12.0
    headers = []
    for sign in (1.0, -1.0):
        side = [h for h in group if h["side"] == sign]
        if not side:
            continue
        ang = side[0]["header"]
        hr = side[0]["header_r"]
        headers.append((ang, hr))
        parts.append(cyl(10.0, z0, z1, hr * math.cos(ang), hr * math.sin(ang)))
        for h in side:
            base = _at(hr, ang, h["z_lane"])
            parts.append(nipple(base, _radial(ang + math.pi), 12.0, 3.2))
    # bridge over the top and one outlet barb, the single hose off the gun
    if len(headers) == 2:
        a0, r0 = headers[0]
        a1, r1 = headers[1]
        bridge_z = z1 - 4.0
        p0 = _at(r0, a0, bridge_z)
        p1 = _at(r1, a1, bridge_z)
        parts.append(Part.makeCylinder(4.0, math.dist(p0, p1), App.Vector(*p0),
                                       App.Vector(*( _add(p1, p0, -1.0)))))
        mid = _add(p0, _add(p1, p0, -1.0), 0.5)
        parts.append(nipple(mid, _radial(math.pi / 2.0), 22.0, 8.0))
    return parts[0].fuse(parts[1:])


def cage():
    ribs = []
    for j in range(N):
        mid = valve_angle(j) + step / 2.0
        rib = Part.makeBox(RIB_T, RADIAL + 6.0, BODY_H,
                           App.Vector(-RIB_T / 2.0, R - RADIAL / 2.0 - 3.0, z_body0))
        ribs.append(spun(rib, math.degrees(mid - math.pi / 2.0)))
    return ribs[0].fuse(ribs[1:]) if len(ribs) > 1 else ribs[0]


def retainer():
    # lands on the body's inner and outer ends; the hole clears the nut
    s = tube(2 * (rg["r_out"] - 1.0), 2 * (rg["r_in"] + 1.0), z_ret0, z_ret1)
    for j in range(N):
        x, y = polar(R, valve_angle(j))
        s = s.cut(cyl(RETAINER_HOLE, z_ret0 - 0.5, z_ret1 + 0.5, x, y))
    return s


def cam():
    # disc is the rotor; the lobe is only as wide as the button it presses
    r0, r1 = R - 8.0, R + 10.0
    b0, b1 = R - 6.0, R + 6.0
    disc = tube(2 * r1, SHAFT_D + 0.4, z_cam_base, z_cam_back)
    # angles: x = (pi/2 - ang) * R, plateau x in [0, lp]
    a_rel = math.pi / 2.0                       # release edge, x = 0
    a_hold = math.pi / 2.0 - lobe["lp"] / R     # far end of the plateau
    a_climb = a_hold - lobe["lr"] / R
    a_fire = a_rel + lobe["lr"] / R
    pad = sector(b0, b1, a_hold, a_rel, z_cam_base - LOBE_H, z_cam_base + 0.05)
    climb = ramp(b0, b1, a_climb, a_hold, z_cam_base, 0.0, LOBE_H, n=16)
    fire = ramp(b0, b1, a_rel, a_fire, z_cam_base, LOBE_H, 0.0, n=16)
    return disc, pad.fuse(climb).fuse(fire), (b0, b1, a_hold, a_fire)


def shift(obj, vec):
    s = obj.Shape.copy()
    s.translate(App.Vector(*vec))
    obj.Shape = s


def ghost():
    """See through the disc, the clamp and the plate. Valves, hoses and the lobe stay solid."""
    fade = {"Cam": 82, "Retainer": 68, "Head_plate": 72, "Cage": 40}
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None or not hasattr(vo, "Transparency"):
            continue
        if o.Name in fade:
            vo.Transparency = fade[o.Name]


def explode():
    """Pull the stack apart along the bore axis.

    Hoses and the open exhaust stubs lift with the valves, so they leave the plate tunnels.
    The supply header steps out.
    The shaft stays on the axis and is lengthened so it still reaches the cam. The disc is
    transparent here: the blue lobe is on its underside.
    """
    valve_z, retainer_z, cam_z = 108.0, 150.0, 188.0
    for o in list(doc.Objects):
        name = o.Name
        if name in ("Cage",) or name.startswith(("Valve_", "Hose", "Vent_")):
            shift(o, (0, 0, valve_z))
        elif name.startswith("Outlet_"):
            bb = o.Shape.BoundBox
            cx = (bb.XMin + bb.XMax) / 2.0
            cy = (bb.YMin + bb.YMax) / 2.0
            r = math.hypot(cx, cy) or 1.0
            shift(o, (18.0 * cx / r, 18.0 * cy / r, valve_z))
        elif name.startswith("Manifold_"):
            bb = o.Shape.BoundBox
            cx = (bb.XMin + bb.XMax) / 2.0
            cy = (bb.YMin + bb.YMax) / 2.0
            r = math.hypot(cx, cy) or 1.0
            shift(o, (28.0 * cx / r, 28.0 * cy / r, 0.0))
        elif name == "Retainer":
            shift(o, (0, 0, retainer_z))
        elif name in ("Cam", "Cam_lobe"):
            shift(o, (0, 0, cam_z))
        elif name == "Shaft":
            o.Shape = cyl(SHAFT_D, -4.0, z_cam_back + 18.0 + cam_z)
    cam_obj = doc.getObject("Cam")
    if cam_obj is not None and getattr(cam_obj, "ViewObject", None) is not None:
        cam_obj.ViewObject.Transparency = 72


def head_plate(cutters):
    s = tube(2 * PLATE_R, PLATE_BORE, 0.0, PLATE_T)
    block = Part.makeBox(2 * PLATE_R + 40.0, 2 * PLATE_R + 40.0, PLATE_T + 4.0,
                         App.Vector(-PLATE_R - 20.0, -PLATE_R - 20.0, -2.0))
    holes = [c.common(block) for c in cutters]
    holes = [h for h in holes if h.Volume > 1.0]
    if holes:
        s = s.cut(holes[0].fuse(holes[1:]) if len(holes) > 1 else holes[0])
    return s


ribs = cage()
hold = retainer()
disc, pad, cam_win = cam()
shaft = cyl(SHAFT_D, -4.0, z_cam_back + 18.0)
valves = [valve_shape(j) for j in range(N)]
outlets = [outlet_shape(j) for j in range(N)]
paths = hose_paths()
vents = [vent_shape(j) for j in range(N)]
hoses = [pipe_along(h["segs"], HOSE_OD) for h in paths]
cutters = [pipe_along(h["segs"], HOSE_OD + 0.6) for h in paths]
plate = head_plate(cutters)
man_p = manifold_shape(paths)


# ---------------------------------------------------------------- checks
check(abs(BODY_H + BUTTON_STACK - OVERALL) < 1e-9, "body %.1f + button stack %.1f = overall %.1f"
      % (BODY_H, BUTTON_STACK, OVERALL))
check(rg["r_out"] < PLATE_R - 5.0, "bodies stay inside the plate: outer R %.1f, plate R %.0f"
      % (rg["r_out"], PLATE_R))
check(rg["gap"] >= VR["WALL"] - 0.05, "inner-corner gap %.2f mm" % rg["gap"])
check(sum(1 for j in range(N) if depressed(j)) == 2, "the parked hold cam keeps two buttons down")

gap01 = valves[0].distToShape(valves[1])[0]
check(gap01 > 0.3, "neighbouring valves clear by %.2f mm" % gap01)
rib_gap = min(valves[j].distToShape(ribs)[0] for j in (0, 1, 5))
check(rib_gap > 0.1, "cage rib clears the bodies by %.2f mm" % rib_gap)
check(valves[0].common(plate).Volume < 1.0, "valves sit on the plate, common volume %.1f mm3"
      % valves[0].common(plate).Volume)
check(outlets[0].distToShape(plate)[0] > 2.0, "the straight A tube clears the plate by %.1f mm"
      % outlets[0].distToShape(plate)[0])
check(outlets[0].distToShape(outlets[1])[0] > 2.0, "neighbouring A tubes clear by %.1f mm"
      % outlets[0].distToShape(outlets[1])[0])
check(outlets[0].BoundBox.YMax > PLATE_R + 8.0, "A tube ends at R %.0f, past the plate"
      % outlets[0].BoundBox.YMax)


def _samples(pts, step_mm=3.0):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step_mm))
        for i in range(1, n + 1):
            t = i / float(n)
            out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    return out


clouds = [_samples(h["pts"]) for h in paths]
nearest = (1e9, None)
for i in range(len(clouds)):
    for j in range(i + 1, len(clouds)):
        # a coarse pass, then the neighbourhood of the closest point
        best = 1e9
        bi = 0
        for ia, a in enumerate(clouds[i][::3]):
            for b in clouds[j][::3]:
                d = math.dist(a, b)
                if d < best:
                    best = d
                    bi = ia * 3
        if best < nearest[0]:
            nearest = (best, (i, j))
check(nearest[0] > HOSE_OD + 0.6, "hose centre lines clear by %.1f mm" % nearest[0])
lug_hit = 0
for cloud in clouds:
    for q in cloud:
        if q[2] < 12.0 and in_lug(math.hypot(q[0], q[1]), math.atan2(q[1], q[0])):
            lug_hit += 1
            break
check(lug_hit == 0, "hoses under the lug height miss the rail lugs (%d hit)" % lug_hit)
moved = len({h["j"] for h in paths
              if abs(_wrap(h["exit"] - h["port"])) > math.radians(0.5)})
check(moved <= 8, "only %d valves shift their ray to miss a lug" % moved)
# the end of each hose meets its header ray
off_header = 0
for h in paths:
    end = h["pts"][-1]
    ang = math.atan2(end[1], end[0])
    if abs(_wrap(ang - h["header"])) > math.radians(4.0):
        off_header += 1
check(off_header == 0, "every hose arrives at its header (%d do not)" % off_header)
check(hoses[0].distToShape(valves[paths[0]["j"]])[0] < 2.5,
      "hose reaches its port, gap %.1f mm" % hoses[0].distToShape(valves[paths[0]["j"]])[0])
check(hoses[0].distToShape(disc)[0] > 1.0, "a hose clears the cam by %.1f mm" % hoses[0].distToShape(disc)[0])
check(min(h.distToShape(shaft)[0] for h in hoses[::8]) > 2.0, "hoses clear the shaft")
check(hoses[0].common(plate).Volume < 30.0, "hose stays in its plate tunnel, common %.0f mm3"
      % hoses[0].common(plate).Volume)
vent_gap = min(vents[j].distToShape(vents[(j + 1) % N])[0] for j in range(N))
check(vent_gap > 2.0, "open exhaust stubs clear by %.1f mm" % vent_gap)
own_vent = min(vents[h["j"]].distToShape(solid)[0] for h, solid in zip(paths, hoses))
check(own_vent > 1.0, "an exhaust stub clears its own supply hose by %.1f mm" % own_vent)
check(man_p.distToShape(plate)[0] > 2.0, "the supply header clears the plate by %.1f mm"
      % man_p.distToShape(plate)[0])
check(man_p.BoundBox.YMax > PLATE_R + 30.0, "the supply header sits outside the plate")

free_j = next(j for j in range(N) if not depressed(j))
press_j = next(j for j in range(N) if depressed(j))
free_disc = valves[free_j].distToShape(disc)[0]
check(abs(free_disc - APPROACH) < 0.05, "free button clears the disc face by %.2f mm" % free_disc)
press_d = valves[press_j].distToShape(pad)[0]
press_hit = valves[press_j].common(pad).Volume
check(press_d < 0.05 and press_hit < 20.0,
      "pressed button meets the lobe, common volume %.1f mm3" % press_hit)
free_lobe = min(valves[j].distToShape(pad)[0] for j in range(N) if not depressed(j))
check(free_lobe > 0.05, "free buttons stay off the lobe, closest %.2f mm" % free_lobe)
nut_top = z_ret1 + 0.2 + 6.4
check(z_cam_base - LOBE_H > nut_top + 0.4, "lobe stays %.1f mm above the nut"
      % (z_cam_base - LOBE_H - nut_top))
check(VR["STROKE"] - DEPRESS > 0.3, "press %.1f mm leaves %.1f mm to the valve stop"
      % (DEPRESS, VR["STROKE"] - DEPRESS))
check(shaft.distToShape(disc)[0] > 0.1, "shaft clears the cam bore")
check(hold.distToShape(valves[free_j])[0] < 0.2, "retainer lands on the body")
check(hold.common(valves[free_j]).Volume < 1.0, "retainer does not cut the valve")
check(all(v.Volume > 10000 for v in valves), "each valve is one solid, %.0f mm3" % valves[0].Volume)


# ---------------------------------------------------------------- document
doc = App.newDocument("valve_head")


def add(name, shape, color, group):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
    group.addObject(o)
    return o


printed = doc.addObject("App::DocumentObjectGroup", "Printed")
bought = doc.addObject("App::DocumentObjectGroup", "Bought")
steel = doc.addObject("App::DocumentObjectGroup", "Steel")
add("Head_plate", plate, (0.62, 0.60, 0.55), printed)
add("Cage", ribs, (0.78, 0.74, 0.66), printed)
add("Retainer", hold, (0.55, 0.62, 0.70), printed)
add("Cam", disc, (0.55, 0.62, 0.72), printed)
add("Cam_lobe", pad, (0.16, 0.45, 0.78), printed)
add("Manifold_P", man_p, (0.78, 0.62, 0.28), bought)
for j, v in enumerate(valves):
    color = (0.45, 0.62, 0.82) if depressed(j) else (0.72, 0.74, 0.76)
    add("Valve_%02d" % j, v, color, bought)
for j, tube_a in enumerate(outlets):
    add("Outlet_%02d" % j, tube_a, (0.72, 0.55, 0.28), bought)
for j, stub in enumerate(vents):
    add("Vent_%02d" % j, stub, (0.45, 0.38, 0.30), bought)
for h, solid in zip(paths, hoses):
    add("Hose_%02d" % h["j"], solid, (0.86, 0.72, 0.36), bought)
add("Shaft", shaft, (0.35, 0.38, 0.42), steel)

sys.stdout.flush()
try:
    doc.recompute()
    out_dir = os.path.join(REPO, "exports", "valve_head")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    doc.saveAs(os.path.join(out_dir, "valve_head.FCStd"))
    if App.GuiUp:
        show = os.environ.get("SHOW", "")
        if show == "ghost":
            ghost()
        elif show == "explode":
            explode()
        if show:
            doc.recompute()
except Exception:
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    raise

print("valve head, %d barrels, buttons on R %.1f" % (N, R))
print("  plate R %.0f x %.0f, cage ribs %.1f mm, retainer clamps the body top" % (PLATE_R, PLATE_T, RIB_T))
print("  disc on the buttons, lobe %.1f mm = %.1f clearance + %.1f press, %.1f left to the stop"
      % (LOBE_H, APPROACH, DEPRESS, VR["STROKE"] - DEPRESS))
print("  A tubes straight out; R vents in the well; P hoses leave through the plate to one barbed header")
print("  %d valves shift their ray to miss a rail lug" % moved)
print("concept only: valves are not measured, do not slice")
ok = all(FITS)
print("checks: %s" % ("OK" if ok else "FAIL"))
if __name__ == "__main__" and not os.environ.get("OUT"):
    sys.exit(0 if ok else 1)
