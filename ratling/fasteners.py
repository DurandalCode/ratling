# -*- coding: utf-8 -*-
"""
Fasteners for printed parts: M3 socket-head bolts with nuts, M6 studs with nuts.

Only three M3 lengths are stocked: 6, 20 and 50 mm. A joint is a stack of parts
along one axis; the bolt's grip (material between its head and its nut) must lie
in the window L - NUT_T - (0 .. PROTRUDE): the nut is fully engaged and the end
sticks out at most PROTRUDE. When the stack is thicker than that, the head and
the nut are sunk in wells so the grip lands in the window, keeping FLOOR_MIN of
material under each. No printed thread, no inserts, no glue (the pistol's seats,
pistol/hammer_assembly.py SHELL_BOLT_SEATS): the head sits on the flat bottom of
a round well, the nut in an AF 5.9 hex socket at the bottom of its round well.

    import ratling.fasteners as FA
    b = FA.m3("rim to clamp", p, d, [rim, clamp])      # parts in order from the head side
    rim, clamp = rim.cut(b.cutter), clamp.cut(b.cutter)
    b.body        # bolt + nut solids (display, mass, clearances); b.access: key and nut room

FreeCAD only (Part). M6 studs (the frame's spars) are `m6_stud`.
"""
import math

import FreeCAD as App
import Part

V = App.Vector

M3_LENGTHS = (6.0, 20.0, 50.0)
M3_D, M3_HOLE = 3.0, 3.4
HEAD_D, HEAD_T = 5.5, 3.0                 # DIN 912
NUT_AF, NUT_T = 5.5, 2.4                  # DIN 934
SOCKET_AF, SOCKET_T = 5.9, 2.8            # anti-rotation hex socket for the nut
HEAD_WELL_D = 6.4                         # head + 0.45 a side; the key goes in the head
NUT_WELL_D = 7.2                          # over the socket's corners (6.81): the nut drops in
PROTRUDE = 2.0                            # bolt end past the nut, at most
FLOOR_MIN = 3.0                           # material under a head or a nut
ACCESS_L = 30.0                           # free run for the key / the nut beyond a seat
STEEL = 7.85                              # g/cm3

M6_D, M6_HOLE = 6.0, 6.4
M6_NUT_AF, M6_NUT_T = 10.0, 5.0
M6_WASHER_D, M6_WASHER_T = 12.0, 1.6


def _unit(d):
    d = V(d)
    d.normalize()
    return d


def _cyl(r, s0, s1, p, d):
    return Part.makeCylinder(r, s1 - s0, p + d * s0, d)


def _hex(af, s0, s1, p, d):
    """Hex prism across flats af on the axis (p, d) from s0 to s1."""
    rr = af / math.sqrt(3.0)
    pts = [V(rr * math.cos(math.radians(30 + 60 * k)), rr * math.sin(math.radians(30 + 60 * k)), 0) for k in range(6)]
    h = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, s1 - s0))
    rot = App.Rotation(V(0, 0, 1), d)
    h.Placement = App.Placement(p + d * s0, rot)
    return h


def intervals(shape, p, d, reach=400.0):
    """Material intervals (s0, s1) of shape along the line p + s d, s in [-reach, reach]."""
    seg = Part.LineSegment(p - d * reach, p + d * reach).toShape()
    out = []
    for so in (shape.Solids or [shape]):
        bb = so.BoundBox
        if not bb.isValid() or bb.DiagonalLength <= 0:
            continue
        try:
            com = seg.common(so)
            edges = com.Edges
        except Exception:
            edges = []
        if not edges:
            # fall back on the section points: entry and exit pairs along the line
            try:
                pts = sorted((v.Point - p).dot(d) for v in seg.section(so).Vertexes)
            except Exception:
                pts = []
            for a, b in zip(pts[0::2], pts[1::2]):
                if so.isInside(p + d * (0.5 * (a + b)), 1e-6, True):
                    out.append((a, b))
            continue
        for e in edges:
            a, b = [(v.Point - p).dot(d) for v in e.Vertexes]
            out.append((min(a, b), max(a, b)))
    merged = []
    for a, b in sorted(out):
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


class Fastener(object):
    """One fastener: where it is, its solids, its seats and how it fits its length."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return "<%s %s %s>" % (self.kind, self.name, getattr(self, "L", ""))


def solve_m3(T, t_head, t_nut, head_on_face=False, nut_on_face=False, lengths=M3_LENGTHS):
    """Choose L and the well depths for a stack T thick (head part t_head, nut part t_nut).

    Returns (L, head_well, nut_well) with the least total well depth (the most
    material in the grip), or None. A sunk nut sits in its hex socket
    (nut_well >= SOCKET_T); *_on_face keeps the head or the nut on the surface
    (nut_on_face: a plain nut on a thin plate, held by a key while tightening).
    """
    best = None
    hw_max = 0.0 if head_on_face else max(0.0, t_head - FLOOR_MIN)
    nw_min, nw_max = (0.0, 0.0) if nut_on_face else (SOCKET_T, t_nut - FLOOR_MIN)
    if nw_max < nw_min - 1e-9:
        return None
    for L in lengths:
        # grip window for L, and the grips the wells allow; aim at the end 1 mm past the nut
        lo = max(L - NUT_T - PROTRUDE, T - hw_max - nw_max)
        hi = min(L - NUT_T, T - nw_min)
        if lo > hi + 1e-9:
            continue
        g = min(max(L - NUT_T - 0.5 * PROTRUDE, lo), hi)
        W = T - g
        nw = max(nw_min, W - hw_max)
        hw = W - nw
        if best is None or W < best[3]:
            best = (L, max(0.0, hw), nw, W)
    return None if best is None else best[:3]


def m3(name, p, d, parts, L=None, head_on_face=False, nut_on_face=False, reach=400.0, clip=None):
    """M3 bolt along (p, d), d from the head to the nut, through parts (in order from the head side).

    p is any point on the axis; the stack is measured on the axis line itself, within
    clip = (s0, s1) along d from p when given (another part of the same body further on).
    Raises if the stack does not fit 6/20/50 with FLOOR_MIN under the head and the nut.
    """
    d = _unit(d)
    p = V(p)
    iv_a = intervals(parts[0], p, d, reach)
    iv_b = intervals(parts[-1], p, d, reach)
    if clip is not None:
        iv_a = [(max(a, clip[0]), min(b, clip[1])) for a, b in iv_a if b > clip[0] and a < clip[1]]
        iv_b = [(max(a, clip[0]), min(b, clip[1])) for a, b in iv_b if b > clip[0] and a < clip[1]]
    if not iv_a or not iv_b:
        _miss = parts[0] if not iv_a else parts[-1]
        raise ValueError("%s: the axis (%.1f, %.1f, %.1f) dir (%.2f, %.2f, %.2f) misses the %s part, bbox %s"
                         % (name, p.x, p.y, p.z, d.x, d.y, d.z, "head" if not iv_a else "nut", _miss.BoundBox))
    # The head seats in the head part's first run of material on the axis, the nut in the
    # nut part's last run (a ring or a fork is met twice).
    s_a0, s_a1 = iv_a[0]
    s_b0, s_b1 = iv_b[-1]
    T = s_b1 - s_a0
    t_a, t_b = s_a1 - s_a0, s_b1 - s_b0
    sol = solve_m3(T, t_a, t_b, head_on_face, nut_on_face, (L,) if L else M3_LENGTHS)
    if sol is None:
        raise ValueError("%s: stack %.1f (head part %.1f, nut part %.1f) fits no M3 x %s"
                         % (name, T, t_a, t_b, "/".join("%.0f" % x for x in ((L,) if L else M3_LENGTHS))))
    L_, hw, nw = sol
    return m3_at(name, p + d * s_a0, d, hw, T - nw, L_, T=T, socket=not nut_on_face,
                 nut_well_to=T + 1.0 if (not nut_on_face and nw > SOCKET_T + 1e-6) else None,
                 floor_head=t_a - hw, floor_nut=t_b - nw, nut_on_face=nut_on_face)


def m3_at(name, o, d, s_head, s_nut, L, T=None, socket=True, nut_well_to=None, nut_slot=None,
          floor_head=None, floor_nut=None, nut_on_face=False, exception=None):
    """M3 x L on the axis (o, d): head bearing face at s_head, nut bearing face at s_nut.

    The cutter: Ø3.4 hole from s_head - 1 to past the bolt end, a head well from s = -1
    to s_head when s_head > 0, the nut's hex socket (socket=True) and a round nut well
    beyond it to nut_well_to; nut_slot = a direction: the socket opens sideways to the
    surface that way (the nut slides in across the axis), slot length nut_slot[1].
    exception: a string, when the fastener knowingly misses the grip window.
    """
    d = _unit(d)
    o = V(o)
    grip = s_nut - s_head
    end_s = s_head + L
    cut = [_cyl(M3_HOLE / 2, min(-1.0, s_head - 1.0), max(end_s, s_nut + NUT_T) + PROTRUDE + 1.0, o, d)]
    if s_head > 1e-6:
        cut.append(_cyl(HEAD_WELL_D / 2, -1.0, s_head, o, d))
    if socket:
        cut.append(_hex(SOCKET_AF, s_nut, s_nut + SOCKET_T, o, d))
        if nut_well_to is not None:
            cut.append(_cyl(NUT_WELL_D / 2, s_nut + SOCKET_T - 0.01, nut_well_to, o, d))
        if nut_slot is not None:
            sd, sl = _unit(nut_slot[0]), nut_slot[1]
            for k in range(1, int(math.ceil(sl / 2.0)) + 1):
                cut.append(_hex(SOCKET_AF, s_nut, s_nut + SOCKET_T, o + sd * min(sl, 2.0 * k), d))
    cutter = cut[0]
    for c in cut[1:]:
        cutter = cutter.fuse(c)
    bolt = _cyl(HEAD_D / 2, s_head - HEAD_T, s_head, o, d).fuse(_cyl(M3_D / 2, s_head - 0.01, end_s, o, d))
    nut = _hex(NUT_AF, s_nut, s_nut + NUT_T, o, d).cut(_cyl(M3_D / 2, s_nut - 1, s_nut + NUT_T + 1, o, d))
    access = Part.makeCompound([_cyl(HEAD_WELL_D / 2, s_head - HEAD_T - ACCESS_L, s_head - HEAD_T, o, d)])
    return Fastener(kind="M3", name=name, L=L, p=o, d=d, T=T if T is not None else grip, grip=grip,
                    head_well=s_head, nut_well=(T - s_nut) if T is not None else 0.0,
                    floor_head=floor_head if floor_head is not None else 99.0,
                    floor_nut=floor_nut if floor_nut is not None else 99.0,
                    end=end_s - (s_nut + NUT_T), nut_on_face=nut_on_face or not socket, exception=exception,
                    bolt=bolt, nut=nut, body=Part.makeCompound([bolt, nut]), cutter=cutter.removeSplitter(),
                    access=access, mass=STEEL * (bolt.Volume + nut.Volume) / 1000.0)


def m3_ok(f):
    """The fastener fits its stocked length: grip window, nut engaged, floors kept."""
    if f.kind != "M3":
        return True
    if getattr(f, "exception", None):
        return f.L in M3_LENGTHS
    return (f.L in M3_LENGTHS and f.L - NUT_T - PROTRUDE - 1e-6 <= f.grip <= f.L - NUT_T + 1e-6
            and -1e-6 <= f.end <= PROTRUDE + 1e-6 and f.floor_head >= FLOOR_MIN - 1e-6
            and (f.nut_on_face or f.floor_nut >= FLOOR_MIN - 1e-6))


def m6_stud(name, p0, p1, nuts, hole_parts=()):
    """M6 stud from p0 to p1; nuts: list of (s, side) along it, side -1 / +1 = the nut on the
    p0 / p1 side of the face at s (a washer under each). Cutter: Ø6.4 the whole length."""
    p0, p1 = V(p0), V(p1)
    d = _unit(p1 - p0)
    L = (p1 - p0).Length
    rod = _cyl(M6_D / 2, 0.0, L, p0, d)
    hw = []
    for s, side in nuts:
        if side < 0:
            w0, w1, n0, n1 = s - M6_WASHER_T, s, s - M6_WASHER_T - M6_NUT_T, s - M6_WASHER_T
        else:
            w0, w1, n0, n1 = s, s + M6_WASHER_T, s + M6_WASHER_T, s + M6_WASHER_T + M6_NUT_T
        hw.append(_cyl(M6_WASHER_D / 2, w0, w1, p0, d).cut(_cyl(M6_HOLE / 2, w0 - 1, w1 + 1, p0, d)))
        hw.append(_hex(M6_NUT_AF, n0, n1, p0, d).cut(_cyl(M6_D / 2, n0 - 1, n1 + 1, p0, d)))
    body = Part.makeCompound([rod] + hw)
    return Fastener(kind="M6 stud", name=name, L=L, p=p0, d=d, nuts=len(nuts), body=body, rod=rod,
                    hardware=Part.makeCompound(hw), cutter=_cyl(M6_HOLE / 2, -1.0, L + 1.0, p0, d),
                    mass=STEEL * (rod.Volume + sum(h.Volume for h in hw)) / 1000.0)


def bom(fasteners):
    """Counts by kind and length: {'M3 x 20': n, ..., 'M3 nuts': n, 'M6 stud mm': total, 'M6 nuts': n}."""
    out = {}
    for f in fasteners:
        if f.kind == "M3":
            k = "M3 x %.0f" % f.L
            out[k] = out.get(k, 0) + 1
            out["M3 nuts"] = out.get("M3 nuts", 0) + 1
        elif f.kind == "M6 stud":
            out["M6 stud mm"] = out.get("M6 stud mm", 0.0) + f.L
            out["M6 studs"] = out.get("M6 studs", 0) + 1
            out["M6 nuts"] = out.get("M6 nuts", 0) + f.nuts
            out["M6 washers"] = out.get("M6 washers", 0) + f.nuts
    return out


def moved(f, fn, name=None):
    """A copy of f with its solids passed through fn (a placement: fn(shape) -> shape)."""
    g = Fastener(**dict(f.__dict__))
    for k in ("bolt", "nut", "body", "cutter", "access", "rod", "hardware"):
        if hasattr(f, k):
            setattr(g, k, fn(getattr(f, k)))
    if name:
        g.name = name
    return g
