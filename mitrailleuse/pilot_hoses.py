# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A: the pilot hoses, one per barrel from the head's pilot fitting to the module's (FreeCAD 1.0).

Every port of the firing head (rear_frame.py, bench C's head) has its pilot fitting on the block's top, at
R (CHARGE_R + RISER_DR), facing the pack; every v4.4 module has its own in the rear plug, facing the head. A PU
tube 4 x 2.5 joins the two: straight out of each collet for STRAIGHT, and between them an S of two equal arcs in
the plane through both fittings' axes (the tube's own way of lying when pushed into two facing fittings). The
gap between the collets is the same for every hose, so the S's radius only depends on how far apart the two
fittings are across the axis.

    which port .. ports and modules matched for the least total hose length (Hungarian): a matching of least
                  total length in the plane never crosses, so the hoses' plan views do not cross either. The
                  rotor fires the ports in turn, so this also sets the barrels' firing order (listed).
    room ........ hoses clear of each other, of the other modules' rear plugs, yokes, rods, nuts and fittings,
                  of the head's other fittings, of the rails, and of a corridor straight up from each quarter's
                  supply fitting (the supply hoses are not drawn yet; they keep their way out).
    length ...... each hose's cut length: its centre line plus HOSE_IN in each collet.

At 16 the head is the real one. At 19 there is no head yet (bench C is the 16's): its ports are taken on the same
circle and level, (j + 0.5) x 360 / 19, so the 19's numbers are a forecast until its head is drawn.

Run inside FreeCAD (or freecadcmd):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/pilot_hoses.py').read())
Prints a report with [OK ] / [FAIL] checks and writes exports/pilot_hoses/ (FCStd, the hose table).
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
# the rear frame's build (head, plate, drive) and through it the pack frame's, without checks and export
exec(open(os.path.join(REPO, "mitrailleuse", "rear_frame.py"), encoding="utf-8").read()
     .split("\n# ---------------------------------------------------------------- checks")[0])

NAME = "pilot_hoses"
OUT_DIR = os.path.join(REPO, "exports", NAME)

# ---------------------------------------------------------------- parameters
HOSE = (4.0, 2.5)           # PU tube, OD x ID
R_MIN = 10.0                # its least bend radius (catalogue, PU 4 x 2.5 at 20 C)
STRAIGHT = 6.0              # straight out of each collet before it bends
HOSE_IN = 12.0              # tube pushed into each fitting (typical G1/8 - 4 push-in; check on the bought ones)
GAP = 0.5                   # hose to hose and to anything else
NEAR = 10.0                 # look for the closest thing within this of a hose (a farther one reads as "> NEAR")
BENCH_B_HOSE = 110.0        # the hose head_bench.py counts in the pilot's volume (rotor_timing.py's charge times)
SUP_CORRIDOR = 12.0         # Ø straight up from each supply fitting

z_head = Z0 + head["fittings"].BoundBox.ZMax                     # the head's collets
r_port = RB["CHARGE_R"] + RB["RISER_DR"]


def head_ports(n):
    """Pilot fittings' centres (x, y) on the head, port j at (j + 0.5) x 360 / n."""
    return [polar(r_port, (j + 0.5) * 360.0 / n) for j in range(n)]


def hungarian(c):
    """Least-cost assignment, rows to columns, of a square cost matrix: column of each row."""
    n = len(c)
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [1e18] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, d, j1 = p[j0], 1e18, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = c[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < d:
                        d, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += d
                    v[j] -= d
                else:
                    minv[j] -= d
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    a = [0] * n
    for j in range(1, n + 1):
        a[p[j] - 1] = j - 1
    return a


def hose_path(p, z0, m, z1):
    """Centre line from the head's collet (p, z0) to the module's (m, z1): straight, two arcs, straight.
    Returns (wire, bend radius, length)."""
    a0, b0 = V(p[0], p[1], z0), V(m[0], m[1], z1)
    a, b = a0 + V(0, 0, STRAIGHT), b0 - V(0, 0, STRAIGHT)
    d, L = math.hypot(m[0] - p[0], m[1] - p[1]), b.z - a.z
    if d < 0.5:
        return Part.Wire([Part.LineSegment(a0, b0).toShape()]), 1e9, (b0 - a0).Length
    e = V((m[0] - p[0]) / d, (m[1] - p[1]) / d, 0)
    th = 2 * math.atan2(d, L)
    r = L / (2 * math.sin(th))
    c1, c2 = a + e * r, b - e * r

    def on1(f):
        return c1 - e * (r * math.cos(f)) + V(0, 0, r * math.sin(f))

    def on2(f):
        return c2 + e * (r * math.cos(f)) - V(0, 0, r * math.sin(f))

    mid = on1(th)
    edges = [Part.LineSegment(a0, a).toShape(), Part.Arc(a, on1(th / 2), mid).toShape(),
             Part.Arc(mid, on2(th / 2), b).toShape(), Part.LineSegment(b, b0).toShape()]
    return Part.Wire(edges), r, 2 * STRAIGHT + 2 * r * th


def tube(wire, z0):
    start = wire.Edges[0].Vertexes[0].Point
    prof = Part.Wire(Part.makeCircle(HOSE[0] / 2, start, Z))
    s = wire.makePipeShell([prof], True, True)
    return s


# ---------------------------------------------------------------- build
checks = []
check = lambda ok, text: checks.append((text, bool(ok)))
built = {}
sup_xy = [RB["sup_in"]]
sup_xy = [(math.cos(math.radians(q)) * sup_xy[0][0] - math.sin(math.radians(q)) * sup_xy[0][1],
           math.sin(math.radians(q)) * sup_xy[0][0] + math.cos(math.radians(q)) * sup_xy[0][1]) for q in (0, 90, 180, 270)]
for tag, key in KEYS:
    pts = LAYOUT[key]
    n = len(pts)
    mods = module_parts(key)
    ports = head_ports(n)
    a = hungarian([[math.dist(p, q) for q in pts] for p in ports])
    z_mod = mods[0]["fitting"].BoundBox.ZMin                     # the modules' collets
    hoses = []
    for j, p in enumerate(ports):
        w, r, length = hose_path(p, z_head, pts[a[j]], z_mod)
        hoses.append({"port": j, "module": a[j], "wire": w, "r": r, "len": length, "solid": tube(w, z_head),
                      "d": math.dist(p, pts[a[j]])})
    built[tag] = (key, mods, ports, hoses, z_mod)

# ---------------------------------------------------------------- checks
wall = lambda s, o: s.distToShape(o)[0]


def near(a, b):
    bb = a.BoundBox
    bb.enlarge(NEAR)
    return bb.intersect(b.BoundBox)


fmt = lambda d: "> %.0f" % NEAR if d >= 1e8 else "%.1f" % d
rails_all = G.fuse_all(rail_parts)
head_fit = head["fittings"].translated(V(0, 0, Z0))
lines = []
for tag, (key, mods, ports, hoses, z_mod) in built.items():
    n = len(hoses)
    forecast = "" if tag == "A16" else " (ports forecast, no 19 head yet)"
    check(sorted(h["module"] for h in hoses) == list(range(n)), "%s: %d ports, %d modules, one hose each" % (tag, n, n))
    r_min = min(h["r"] for h in hoses)
    check(r_min >= R_MIN, "%s: tightest bend R %.1f (>= %.0f, PU %g x %g)%s" % (tag, r_min, R_MIN, HOSE[0], HOSE[1], forecast))
    d_hh = 1e9
    for i, h in enumerate(hoses):
        for g in hoses[i + 1:]:
            if near(h["solid"], g["solid"]):
                d_hh = min(d_hh, wall(h["solid"], g["solid"]))
    check(d_hh >= GAP, "%s: hoses %s mm apart at the closest%s" % (tag, fmt(d_hh), forecast))
    # everything else: the other modules' rear parts, the head's other fittings (16 only), rails, supply corridors
    d_mod = 1e9
    for h in hoses:
        for k, m in enumerate(mods):
            for part in ("rp", "rear_yoke", "hardware", "fitting"):
                if k == h["module"] and part in ("fitting", "rear_yoke", "rp"):
                    continue
                if near(h["solid"], m[part]):
                    d_mod = min(d_mod, wall(h["solid"], m[part]))
    d_rail = min(wall(h["solid"], rails_all) for h in hoses)
    if tag == "A16":
        d_head = 1e9
        for h in hoses:
            px, py = ports[h["port"]]
            others = head_fit.cut(cyl(13.0, z_head - 30, z_head + 1, px, py))
            d_head = min(d_head, wall(h["solid"], others))
        corridors = G.fuse_all([cyl(SUP_CORRIDOR, z_head, z_mod, x, y) for x, y in sup_xy])
        d_sup = min(wall(h["solid"], corridors) for h in hoses)
    else:
        d_head, d_sup = 99.0, 99.0
    check(min(d_mod, d_rail, d_head, d_sup) >= GAP, "%s: hoses clear of the other modules' plugs, yokes, rods and fittings by"
          " %s, the rails %.1f, the head's other fittings %s, the supply's way up %s%s"
          % (tag, fmt(d_mod), d_rail, "%.1f" % d_head if tag == "A16" else "-", "%.1f" % d_sup if tag == "A16" else "-", forecast))
    cut = [h["len"] + 2 * HOSE_IN for h in hoses]
    if tag == "A16":
        check(max(cut) <= BENCH_B_HOSE, "%s: longest hose %.0f mm, within the %.0f mm bench B's pilot volume counts"
              % (tag, max(cut), BENCH_B_HOSE))
    else:                   # a forecast: noted, not checked, until the 19's head is drawn
        over = [c for c in cut if c > BENCH_B_HOSE]
        lines.append("  %s: %d hose(s) longer than bench B's %.0f mm (longest %.0f: +%.2f cm3 in that pilot), to count"
                     " with the 19's head" % (tag, len(over), BENCH_B_HOSE, max(cut),
                                              math.pi / 4 * HOSE[1] ** 2 * (max(cut) - BENCH_B_HOSE) / 1000))
    lines.append("  %s: hoses %.0f..%.0f mm cut, %.2f m in all; fittings %.1f mm apart across the axis at most"
                 % (tag, min(cut), max(cut), sum(cut) / 1000, max(h["d"] for h in hoses)))

report = [
    "Mitrailleuse concept A: pilot hoses, the head's fittings (z %.1f) to the modules' (z %.1f)" % (z_head, built["A16"][4]),
    "  PU %g x %g, %.0f straight out of each collet, an S of two arcs between, %.0f in each fitting; ports matched to"
    " modules for the least total length" % (HOSE[0], HOSE[1], STRAIGHT, HOSE_IN),
] + lines + ["  [%s] %s" % ("OK " if ok else "FAIL", t) for t, ok in checks]
print("\n".join(report))

# ---------------------------------------------------------------- the hose table
os.makedirs(OUT_DIR, exist_ok=True)
table = []
for tag, (key, mods, ports, hoses, z_mod) in built.items():
    pts = LAYOUT[key]
    table.append("%s (%s)%s" % (tag, key, "" if tag == "A16" else ", ports forecast"))
    table.append("  port  at deg  ->  module  at (x, y)        R bend  cut mm")
    for h in hoses:
        x, y = pts[h["module"]]
        table.append("  %4d  %6.2f  ->  %6d  (%6.1f, %6.1f)  %6.1f  %6.0f"
                     % (h["port"], (h["port"] + 0.5) * 360.0 / len(hoses), h["module"], x, y,
                        min(h["r"], 999.0), h["len"] + 2 * HOSE_IN))
    order = [h["module"] for h in hoses]
    table.append("  firing order (modules, as the rotor turns): " + " ".join(str(k) for k in order))
with open(os.path.join(OUT_DIR, "hose_table.txt"), "w") as f:
    f.write("\n".join(table) + "\n")
with open(os.path.join(OUT_DIR, NAME + "_report.txt"), "w") as f:
    f.write("\n".join(report) + "\n")
print("\n".join(table))

# ---------------------------------------------------------------- document
sc = FV.Scene(NAME)
FV.STYLES.setdefault("alu", ((0.80, 0.82, 0.86), 0))
FV.STYLES.setdefault("barrel", ((0.45, 0.46, 0.50), 0))
SHOW = FV.VIEW_ROT.inverse().multiply(App.Placement(App.Matrix(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)))


def add(group, name, shape, style, offset=None):
    s = shape.copy()
    if offset is not None:
        s.translate(offset)
    s.Placement = SHOW.multiply(s.Placement)
    sc.add(group, name, s, style)


T = V(0, 0, Z0)
key, mods, ports, hoses, z_mod = built["A16"]
add("Hoses", "A16_pilot_hoses", G.fuse_all([h["solid"] for h in hoses]), "hose")
for n_, st in (("blocks", "stator"), ("guide_plates", "plate"), ("rotor", "rotor"), ("gear", "drive")):
    add("Head", "Head_" + n_, head[n_], st, offset=T)
add("Head", "Head_fittings", head["fittings"], "steel", offset=T)
add("Head", "Head_plate", hp, "frame", offset=T)
add("Pack", "A16_rails", Part.makeCompound(rail_parts), "alu")
add("Pack", "A16_rear_plate", plate(key, "rear")[0], "frame")
add("Pack", "A16_chambers", Part.makeCompound([m["chamber"] for m in mods]), "ghost")
for style, names in (("stator", ("rp", "rear_yoke")), ("steel", ("hardware", "fitting"))):
    add("Module_rears", "A16_" + "_".join(names), Part.makeCompound([m[nm] for m in mods for nm in names]), style)
sc.finish()
sc.doc.saveAs(os.path.join(OUT_DIR, NAME + ".FCStd"))
print("written to", OUT_DIR)
