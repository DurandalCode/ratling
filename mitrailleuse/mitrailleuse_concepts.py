# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse: two concepts, each at 16 barrels (rings 4 + 12, layout J)
and 19 barrels (hex, layout G), as plain masses.

Not parts: blocks and tubes at their rough sizes, to compare the layouts
before one is drawn properly. The modules are v4.4 (module/stage3v4_coaxial_chamber.py)
at their real lengths: pilot fitting at z = -47, rear yoke, chamber tube
38 x 1.5 from -25 to 238, barrel 25 x 0.6 from 11 to 311, muzzle ring at 315,
two M3 rods at R 21.5 turned as in docs/pack.md. Drawn with z along the
barrels (+z towards the muzzle), y up, x to the gunner's left (-x right); fcview shows
the model's +x as up, so everything is turned into that frame when added.

The gun is carried and cranked by one (top handle, rear grip, a sling); the
receiver goes separately with the second crew member, on a hose into the back.
Each module fires when its pilot is vented; the pilots are fed all the time
through jets (as in stage4v2_schrader.py).

A. "Montigny": the pack stands still between a front and a rear plate on
   four aluminium rails. Behind it a firing head, a disc with one valve core
   per barrel on one circle; a hose from each module's pilot fitting to its
   core. A striker arm turns behind the head (side crank, 1:1 bevel): one
   crank turn = one round of N shots. The supply goes into the head's ring
   manifold, so nothing turns under pressure. Carried at its centre of
   gravity (mid-pack, ~280 mm ahead of the rear grip): the top handle sits
   over it, with sling eyes either side on a band round the rails and a
   tripod pad under it, so longer barrels move the supports, not a
   counterweight. The rear grip carries the trigger and only aims; a printed
   casing covers the head and the hoses. The crank may go to the second crew
   member through a flexible shaft into the back of the bevel box. Printed
   sleeves on the muzzles (Ø32, bore Ø30, 215 mm ahead of the barrels; the
   module's muzzle sleeve option), tied by a thin band near their tips,
   bring it to ~780 mm for the look.
   One rear block for 16 and 19: the frame is drawn round the larger pack
   (19, R 99; 16 is R 96.3), so the rails, head body, striker, bevel box,
   crank, flexible shaft input, rear frame, grip, trigger, supply and casing
   are the same parts. Per pack only its plates (front, rear, sleeve band),
   the hoses and a core cartridge change: a disc with N cores and N push-in
   fittings that slides into the head body's bore on two O-rings, each core
   fed by a radial jet from the body's ring channel. The striker runs on
   the same circle (R 45) either way: 16 or 19 shots per crank turn. All
   hoses are cut to one length (the longest + 20, ~110 mm). Prints [OK ] /
   [FAIL] checks for this.

B. "Gatling": the pack itself turns. Front and rear rotor plates; the rear
   one is the breech disc: each pilot goes straight into it (no hoses), with
   its valve core behind and its jet off a manifold in the disc. The disc sits
   on a stub axle in the rear frame, the supply comes in through a rotary
   union on the axle's end, the front plate runs on three 608 rollers in a
   fixed front ring. Fixed rollers at the top press the cores as they pass,
   one roller per ring radius (16: two, 19: three). 19's centre module is on
   the axis and never passes a roller: here it is fired by a push rod down
   the hollow axle (a separate button).

Prints a mass estimate for each variant: modules at 350 g (docs/weights.md),
the rest from the volumes drawn here (printed parts as solid volume x 0.6 g/cm3
for walls and infill, aluminium, steel, hoses).

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/mitrailleuse_concepts.py').read())
"""

import importlib
import math
import os
import sys

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import ratling.geom as G
import ratling.fcview as FV
for _m in (G, FV):
    importlib.reload(_m)
_ns = {"__file__": os.path.join(REPO, "mitrailleuse", "pack_layouts.py")}
exec(open(_ns["__file__"], encoding="utf-8").read().rsplit("\nmain()", 1)[0], _ns)
LAYOUT = {k: pts for k, _, _, pts, _ in _ns["LAYOUTS"]}

NAME = "mitrailleuse_concepts"
V = App.Vector
Z = V(0, 0, 1)
FV.STYLES.update({"alu": ((0.80, 0.82, 0.86), 0), "barrel": ((0.45, 0.46, 0.50), 0),
                  "chamber": ((0.80, 0.82, 0.86), 45), "casing": ((0.55, 0.45, 0.35), 70),
                  "sleeve": ((0.35, 0.33, 0.30), 0)})

MODULE_G = 350.0                    # v4.4 with a steel barrel, docs/weights.md
DENSITY = {"printed": 0.6, "frame": 0.6, "rotor": 0.6, "stator": 0.6, "printed_solid": 1.27,
           "alu": 2.70, "steel": 7.85, "hose": 0.73, "oring": 1.3,
           "casing": 1.0, "sleeve": 1.27}   # g/cm3; hose: 4/2.5 PU as a solid Ø4; casing: a 2 mm printed shell
# A: printed muzzle sleeves for the look (no steel), as in the module (stage3v4_coaxial_chamber.py's option)
SLEEVE = (32.0, 1.0, 215.0)         # OD, wall, length ahead of the barrel's end (310.7): bore Ø30, 3.1 mm round the ball
# one v4.4 module along z (docs/weights.md): (g, z of its centre)
MODULE_PARTS = ((106.5, 160.7), (122.3, 106.5), (31.8, 138.8), (31.9, -15.0), (9.0, 15.0), (17.2, 236.7),
                (8.4, -33.2), (3.5, 244.2), (4.1, 310.7), (8.0, -38.2), (3.1, 140.0), (4.2, 100.0))
TIE_R = 21.5
TURNS = {"j_rings_4_12": ((4, 0.0), (12, 40.0))}    # rods per ring, off the module's radius (docs/pack.md)
RAIL = (12.0, 1.0)                  # aluminium tube
CORE_R_A = 45.0                     # A: cores on one circle in the firing head
CRANK_R = 70.0
X_OFF = 420.0                       # variants side by side along x


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def tube(od, wall, z0, z1, x=0.0, y=0.0):
    return cyl(od, z0, z1, x, y).cut(cyl(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rod(d, p, q):
    """A cylinder from point p to point q."""
    p, q = V(*p), V(*q)
    return Part.makeCylinder(d / 2, (q - p).Length, p, q - p)


def polar(r, a):
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


def rod_angles(key, pts):
    if key not in TURNS:
        return [(30.0, 210.0)] * len(pts)
    out, i = [], 0
    for n, turn in TURNS[key]:
        for x, y in pts[i:i + n]:
            a = math.degrees(math.atan2(y, x)) + turn
            out.append((a, a + 180.0))
        i += n
    return out


def modules(key, fitting=True):
    """v4.4 modules of a layout as masses, by style."""
    pts = LAYOUT[key]
    parts = {"barrel": [], "chamber": [], "printed": [], "steel": []}
    for (x, y), angs in zip(pts, rod_angles(key, pts)):
        parts["barrel"].append(tube(25.0, 0.6, 10.7, 310.7, x, y))
        parts["chamber"].append(tube(38.0, 1.5, -25.2, 238.2, x, y))
        parts["printed"] += [cyl(38, -29.2, -0.8, x, y), cyl(38, 218.2, 255.3, x, y),     # rear, front plug
                             cyl(45, -37.2, -29.2, x, y), cyl(45, 240.2, 248.2, x, y),    # yokes
                             cyl(30, 306.7, 314.7, x, y)]                                 # muzzle ring
        for a in angs:
            rx, ry = polar(TIE_R, a)
            parts["steel"].append(cyl(3, -42.1, 319.6, x + rx, y + ry))
        if fitting:
            parts["steel"].append(cyl(13, -47.2, -29.2, x, y))
    return pts, {k: G.fuse_all(v) for k, v in parts.items()}


def plate(key, d_out, hole, z0, z1):
    s = cyl(d_out, z0, z1)
    for x, y in LAYOUT[key]:
        s = s.cut(cyl(hole, z0 - 1, z1 + 1, x, y))
    return s


def rails(r, z0, z1, angles=(45, 135, 225, 315)):
    return G.fuse_all([tube(RAIL[0], RAIL[1], z0, z1, *polar(r, a)) for a in angles])


def carry_handle(r_top, z0, z1):
    """An arch over the top rails."""
    y0 = r_top
    posts = [box(-6, 6, y0 - 6, y0 + 45, z, z + 12) for z in (z0, z1 - 12)]
    grip = cyl(28, z0 + 12, z1 - 12, 0, y0 + 45)
    return G.fuse_all(posts), grip


def rear_grip(y_top, z_at, length=110.0, angle=20.0):
    g = cyl(32, 0, length)
    g.rotate(V(0, 0, 0), V(1, 0, 0), 90 + angle)
    g.translate(V(0, y_top, z_at))
    return g


def crank(z_c, x0, y_c=0.0):
    """Side crank on the gunner's right (-x): shaft, arm (down), knob."""
    shaft = rod(10, (-x0, y_c, z_c), (-x0 - 40, y_c, z_c))
    arm = box(-x0 - 48, -x0 - 40, y_c - CRANK_R - 6, y_c + 6, z_c - 6, z_c + 6)
    knob = rod(20, (-x0 - 48, y_c - CRANK_R, z_c), (-x0 - 88, y_c - CRANK_R, z_c))
    return shaft, arm, knob


def bevel_box(z0, z1, half):
    return box(-half - 20, half, -half, half, z0, z1)


# ---------------------------------------------------------------- A: Montigny
# One rear block for both packs: the frame is drawn round the larger pack (19, R 99; 16 is R 96.3),
# so the rails, rear plate's rim, head, casing, grip and crank are the same parts at 16 and 19.
# Only the pack's own plates, the hoses and the core cartridge in the head change (style "swap").
A_KEYS = ("j_rings_4_12", "g_hex_19")
REAR_R = max(_ns["shroud_r"](LAYOUT[k]) for k in A_KEYS)
HEAD = (CORE_R_A + 12.0, CORE_R_A + 22.0)   # head body: bore (the cartridge's rim), outside
HOSE_SLACK = 20.0                           # one hose length for every barrel at 16 and 19: the longest + this
FITTING_D = 10.0                            # push-in fitting for the 4 mm hose on the cartridge's face
COMMON_A = ("Rails", "Head_body", "Head_spider", "Striker_arm", "Striker_shaft", "Bevel_box", "Crank_shaft",
            "Crank_arm", "Crank_knob", "Rear_frame", "Rear_grip", "Supply_hose", "Flex_shaft_input", "Trigger",
            "Rear_casing")
FV.STYLES["swap"] = ((0.85, 0.30, 0.50), 30)


def concept_a(key):
    pts, m = modules(key)
    R = REAR_R
    r_rail = R + 10
    p = {}
    p["Front_plate"] = (plate(key, 2 * R + 12, 25.4, 268, 276), "swap")
    p["Rear_plate"] = (plate(key, 2 * R + 12, 38.4, 2, 10), "swap")
    p["Rails"] = (rails(r_rail, -150, 290), "alu")
    z_h0, z_h1 = -150.0, -120.0
    # head: a fixed body (supply ring channel, inlet, mounts) round a core cartridge, one per pack, that
    # slides into its bore on two O-rings; each core's jet is a radial hole from the body's ring channel
    p["Head_body"] = (tube(2 * HEAD[1], HEAD[1] - HEAD[0], z_h0, z_h1)
                      .fuse(rod(16, (HEAD[1] - 2, 0, z_h0 + 15), (HEAD[1] + 12, 0, z_h0 + 15))), "rotor")
    spider = G.fuse_all([rod(14, polar(HEAD[1] - 2, a) + (z_h0 + 12,), polar(r_rail, a) + (z_h0 + 12,))
                         for a in (45, 135, 225, 315)])
    p["Head_spider"] = (spider, "frame")
    # cores on one circle, in the modules' angular order
    ang = [math.degrees(math.atan2(y, x)) % 360.0 for x, y in pts]
    order = sorted(range(len(pts)), key=lambda i: (ang[i], math.hypot(*pts[i])))
    cores, fittings, hoses, lengths = [], [], [], []
    for k, i in enumerate(order):
        cx, cy = polar(CORE_R_A, ang[order[0]] + 360.0 / len(pts) * k)
        cores.append(cyl(6, z_h0 - 6, z_h0, cx, cy))
        fittings.append(cyl(FITTING_D, z_h1, z_h1 + 8, cx, cy))
        a, b = V(pts[i][0], pts[i][1], -47.2), V(cx, cy, z_h1 + 8)
        hoses.append(rod(4, a, b))
        lengths.append((a - b).Length)
    p["Core_cartridge"] = (cyl(2 * HEAD[0] - 0.4, z_h0, z_h1).fuse(G.fuse_all(fittings)), "swap")
    p["Valve_cores"] = (G.fuse_all(cores), "steel")
    p["Pilot_hoses"] = (G.fuse_all(hoses), "hose")
    arm = box(-6, 6, 0, CORE_R_A + 8, z_h0 - 16, z_h0 - 8).fuse(cyl(10, z_h0 - 16, z_h0 - 8, 0, CORE_R_A))
    p["Striker_arm"] = (arm, "steel")
    p["Striker_shaft"] = (cyl(8, -200, z_h0), "steel")
    p["Bevel_box"] = (bevel_box(-205, -170, 22), "frame")
    sh, ca, kn = crank(-188, 42)
    p["Crank_shaft"], p["Crank_arm"], p["Crank_knob"] = (sh, "steel"), (ca, "steel"), (kn, "printed")
    p["Rear_frame"] = (box(-r_rail * 0.72, r_rail * 0.72, -r_rail * 0.72 - 6, -r_rail * 0.72 + 6, -205, z_h0)
                       .fuse(box(-14, 14, -r_rail * 0.72, -20, -205, -195)), "frame")
    p["Rear_grip"] = (rear_grip(-r_rail * 0.72, -190), "printed")
    p["Supply_hose"] = (rod(8, (HEAD[1] + 12, 0, z_h0 + 15), (HEAD[1] + 87, -60, z_h0 - 60)), "hose")
    z_tip = 310.7 + SLEEVE[2]
    p["Muzzle_sleeves"] = (G.fuse_all([tube(SLEEVE[0], SLEEVE[1], 314.7, z_tip, x, y) for x, y in pts]), "sleeve")
    p["Sleeve_band"] = (plate(key, 2 * R + 4, SLEEVE[0] + 0.4, z_tip - 30, z_tip - 26), "swap")
    # the second crew member may crank it instead, through a flexible shaft into the back of the bevel box
    p["Flex_shaft_input"] = (cyl(12, -235, -205).fuse(cyl(22, -250, -235)), "steel")
    y_low = -r_rail * 0.72
    p["Trigger"] = (box(-3, 3, y_low - 30, y_low - 8, -168, -160), "steel")
    p["Rear_casing"] = (tube(2 * r_rail + 20, 2.0, -215, -45), "casing")
    # carried at the centre of gravity: top handle over it, sling eyes either side, tripod pad under it
    zc = cog(pts, p)
    pc, hg = carry_handle(r_rail * 0.72, zc - 80, zc + 80)
    p["Carry_posts"], p["Carry_handle"] = (pc, "frame"), (hg, "printed")
    xe = r_rail + 20                                                   # eyes outside a band on the rails
    p["Sling_eyes"] = (G.fuse_all([Part.makeTorus(9, 2.5, V(sx * xe, 0, zc), Z) for sx in (-1, 1)]), "steel")
    p["Eye_band"] = (tube(2 * r_rail + 12, 6.0, zc - 6, zc + 6).fuse(G.fuse_all(
        [box(min(sx * (r_rail + 2), sx * (xe - 9)), max(sx * (r_rail + 2), sx * (xe - 9)), -5, 5, zc - 6, zc + 6)
         for sx in (-1, 1)])), "frame")
    p["Tripod_pad"] = (box(-r_rail * 0.72, r_rail * 0.72, y_low - 12, y_low, zc - 40, zc + 40)
                       .fuse(rod(20, (0, y_low - 12, zc), (0, y_low - 42, zc))), "frame")
    HOSES[key] = lengths
    return pts, m, p, R


HOSES = {}


def check(ok, text):
    print("[%s] %s" % ("OK " if ok else "FAIL", text))
    return ok


def rear_report(built):
    """The A rear block is one set of parts for 16 and 19; what changes is listed."""
    a16, a19 = built["A16"], built["A19"]
    same = [n for n in COMMON_A if abs(a16[n][0].Volume - a19[n][0].Volume) < 1e-3
            and (a16[n][0].BoundBox.Center - a19[n][0].BoundBox.Center).Length < 1e-3]
    rear_g = sum(a16[n][0].Volume / 1000 * (DENSITY["alu"] if n == "Rails" else DENSITY.get(a16[n][1], 0.6))
                 for n in COMMON_A)
    check(len(same) == len(COMMON_A), "A rear block: %d of %d parts the same at 16 and 19 (%s), %.0f g"
          % (len(same), len(COMMON_A), ", ".join(sorted(set(COMMON_A) - set(same))) or "all", rear_g))
    cut = math.ceil((max(max(L) for L in HOSES.values()) + HOSE_SLACK) / 10.0) * 10.0
    for tag, key in (("A16", "j_rings_4_12"), ("A19", "g_hex_19")):
        n = len(LAYOUT[key])
        L = HOSES[key]
        pitch = 2 * CORE_R_A * math.sin(math.pi / n)
        check(pitch >= FITTING_D + 2.0, "%s: %d cores on R %.0f, pitch %.1f mm (push-in fitting Ø%.0f + 2)"
              % (tag, n, CORE_R_A, pitch, FITTING_D))
        print("      %s: hoses %.0f-%.0f mm straight, all cut to %.0f mm (%.1f m of 4 mm hose)"
              % (tag, min(L), max(L), cut, n * cut / 1000))
        r_out = _ns["shroud_r"](LAYOUT[key])
        check(r_out <= REAR_R, "%s: pack R %.1f inside the common frame's R %.1f" % (tag, r_out, REAR_R))


def cog(pts, p):
    """z of the centre of gravity: modules from MODULE_PARTS, the rest from the masses drawn."""
    items = [(len(pts) * g, z) for g, z in MODULE_PARTS]
    for n, (s, style) in p.items():
        d = DENSITY["alu"] if n == "Rails" else DENSITY.get(style, 0.6)
        items += [(so.Volume / 1000 * d, so.CenterOfMass.z) for so in s.Solids]
    return sum(g * z for g, z in items) / sum(g for g, _ in items)


# ---------------------------------------------------------------- B: Gatling
STRIKE_ANG = {"j_rings_4_12": ((77.3, 90.0), (28.3, 45.0)),
              "g_hex_19": ((69.3, 90.0), (40.0, 60.0), (80.0, 60.0))}


def concept_b(key):
    pts, m = modules(key)
    R = _ns["shroud_r"](pts)
    p = {}
    d_rot = 2 * R + 8
    p["Front_rotor_plate"] = (plate(key, d_rot, 25.4, 268, 280), "rotor")
    p["Breech_disc"] = (cyl(d_rot, -62, -45), "rotor")
    cores = [cyl(6, -68, -62, x, y) for x, y in pts]
    p["Valve_cores"] = (G.fuse_all(cores), "steel")
    hollow = key == "g_hex_19"
    axle = tube(16, 3, -200, -62) if hollow else cyl(14, -200, -62)
    p["Stub_axle"] = (axle, "steel")
    if hollow:
        p["Centre_push_rod"] = (cyl(6, -235, -68), "steel")
        p["Centre_button"] = (cyl(16, -245, -235), "oring")
    p["Rotary_union"] = (cyl(30, -225, -200), "stator")
    p["Supply_hose"] = (rod(8, (0, -15, -212), (0, -110, -260)), "hose")
    r_rail = d_rot / 2 + 18
    p["Rails"] = (rails(r_rail, -150, 292), "alu")
    ring = cyl(2 * r_rail + 16, 281, 292).cut(cyl(d_rot + 6, 280, 293))
    p["Front_ring"] = (ring, "frame")
    rollers = []
    for a in (90, 210, 330):
        x, y = polar(d_rot / 2 + 11, a)
        rollers.append(cyl(22, 270, 277, x, y))
        rollers.append(cyl(8, 277, 286, x, y))
    p["Front_rollers"] = (G.fuse_all(rollers), "steel")
    p["Rear_frame"] = (cyl(2 * r_rail + 16, -150, -138).cut(G.fuse_all(
        [cyl(70, -151, -137, *polar(r_rail * 0.55, a)) for a in (0, 90, 180, 270)])), "frame")
    p["Bearing_housing"] = (cyl(40, -150, -110), "frame")
    # striker bracket: fixed arm from the top rails down behind the disc, one roller per ring radius
    br = [box(-8, 8, 0, r_rail, -88, -80)]
    rl = []
    for r, a in STRIKE_ANG[key]:
        x, y = polar(r, a)
        br.append(rod(10, (x, y, -84), (0, r_rail * 0.72, -84)))
        rl.append(cyl(10, -75, -71, x, y))
    br.append(rod(14, (0, r_rail * 0.72, -84), (0, r_rail * 0.72, -138)))
    p["Striker_bracket"] = (G.fuse_all(br), "frame")
    p["Striker_rollers"] = (G.fuse_all(rl), "steel")
    p["Bevel_box"] = (bevel_box(-190, -155, 22), "frame")
    sh, ca, kn = crank(-172, 42)
    p["Crank_shaft"], p["Crank_arm"], p["Crank_knob"] = (sh, "steel"), (ca, "steel"), (kn, "printed")
    pc, hg = carry_handle(r_rail * 0.72, 30, 190)
    p["Carry_posts"], p["Carry_handle"] = (pc, "frame"), (hg, "printed")
    p["Rear_grip"] = (rear_grip(-r_rail * 0.72, -150), "printed")
    return pts, m, p, R


# ---------------------------------------------------------------- masses
def mass_report(tag, pts, p):
    rest = {}
    for n, (s, style) in p.items():
        mat = style if style in ("alu", "steel", "hose", "casing", "sleeve") else "printed"
        if n == "Rails":                      # tubes, already hollow
            mat = "alu"
        rest[mat] = rest.get(mat, 0.0) + s.Volume / 1000 * DENSITY[mat]
    mods = len(pts) * MODULE_G
    other = sum(rest.values())
    print("%-6s modules %2d x %.0f = %5.0f g | printed %4.0f, casing %3.0f, sleeves %3.0f, alu %3.0f, steel %4.0f, hoses %3.0f"
          " | total %.2f kg, CoG at z %.0f"
          % (tag, len(pts), MODULE_G, mods, rest.get("printed", 0), rest.get("casing", 0), rest.get("sleeve", 0), rest.get("alu", 0),
             rest.get("steel", 0), rest.get("hose", 0), (mods + other) / 1000, cog(pts, p)))
    return mods, rest


def to_view(shape):
    """Sketch frame (x side, y up, z forward) -> fcview's model frame (+x up)."""
    s = shape.copy()
    s.rotate(V(0, 0, 0), Z, -90)
    return s


VARIANTS = [("A16", "A_Montigny_16", concept_a, "j_rings_4_12"),
            ("A19", "A_Montigny_19", concept_a, "g_hex_19"),
            ("B16", "B_Gatling_16", concept_b, "j_rings_4_12"),
            ("B19", "B_Gatling_19", concept_b, "g_hex_19")]

sc = FV.Scene(NAME)
doc = sc.doc
MASSES = {}
BUILT = {}
for i, (tag, group, fn, key) in enumerate(VARIANTS):
    pts, m, p, R = fn(key)
    BUILT[tag] = p
    off = V(0, -X_OFF * i, 0)                      # sketch +x is the view's -y
    for n, s in m.items():
        sc.add(group, "%s_Modules_%s" % (tag, n), to_view(s), n if n in ("barrel", "chamber") else
               ("printed" if n == "printed" else "steel"), offset=off)
    for n, (s, style) in p.items():
        sc.add(group, "%s_%s" % (tag, n), to_view(s), style, offset=off)
    MASSES[tag] = mass_report(tag, pts, p)
rear_report(BUILT)
labels = [
    ("A16: МОНТИНЬИ, 4+12 — пакет стоит, головка с 16 ниппелями, шланги", 0),
    ("A19: МОНТИНЬИ, соты 19", 1),
    ("B16: ГАТЛИНГ, 4+12 — крутится пакет, ниппели в казённом диске", 2),
    ("B19: ГАТЛИНГ, соты 19 — центральный ствол толкателем через ось", 3),
]
for text, i in labels:
    sc.label("Labels", text, (160, -X_OFF * i, 340))
sc.finish()
