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
   four aluminium rails. Behind it a firing head on tyre valve cores only
   (worked out in rotor_timing.py and docs/rotor.md). Per barrel the pilot
   line (a hose from the module's pilot fitting) meets two cores in a fixed
   core block: a charge core from the supply ring and a vent core to the
   air, both pressed from behind through printed buttons. The rotor is a cam
   disc with two arc rails: a long one holds the charge buttons of the next
   AHEAD (2) barrels down, a short one behind it presses the vent button of
   the barrel to fire. So two barrels charge at once and nothing else is
   ever charged; between the two, both cores are shut. A charged chamber can
   only be emptied by firing it, or slowly back through the bleed and its
   charge core (a check valve that way) by the dump valve (below). The cores
   are evenly spaced, so the shots are; the core block, rotor and detent are
   per pack (16 or 19).
   Drive: side crank -> 1:1 bevel -> layshaft -> 5:1 spur pair -> dog
   clutch -> rotor shaft: a crank turn fires 1/5 of the volley (3.2 or 3.8
   shots). The trigger on the rear grip pushes the clutch in; let go, a
   spring parts it and the crank turns idle, so it fires only with the
   crank turning and the trigger held. A ratchet detent on the rotor shaft
   parks the rotor with the band's edges between ports, so every charged
   barrel sits under the slot, and lets it turn forward only. A dump valve
   with a key on the inlet shuts the supply and vents the head through a Ø0.5 jet: the charged chambers empty
   back through their bleeds without firing, since the pilot never falls
   far enough below the chamber to lift the diaphragm (checked in the
   report; to be confirmed on the bench). The rate is set by the chamber's
   charge through the module's Ø1.0 bleed (~0.5 s on the v1.1 bench) and by
   how many barrels charge at once (CHARGE_AHEAD, 2: ~3.9 shots/s), printed
   in the report. Carried at its centre of
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
   (19, R 99; 16 is R 96.3), so the rails, head body, gears, clutch, bevel
   box, crank, flexible shaft input, rear frame, grip, trigger, supply and
   casing are the same parts. Per pack only its plates (front, rear, sleeve
   band), the hoses, and the distributor's stator and rotor change; both
   sit in the head body's bore on the same R 45 port circle. All hoses are
   cut to one length (the longest + 20, ~110 mm). Prints [OK ] / [FAIL]
   checks for this.

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
# so the rails, head body, gears, clutch, crank, grip, trigger and casing are the same parts at 16 and 19.
# Per pack (style "swap"): its plates, the hoses, and the distributor's stator and rotor, so that the
# shots stay evenly spaced at either count.
A_KEYS = ("j_rings_4_12", "g_hex_19")
REAR_R = max(_ns["shroud_r"](LAYOUT[k]) for k in A_KEYS)
HEAD = (68.0, 78.0)                         # head body: bore (the core block's rim), outside
HOSE_SLACK = 20.0                           # one hose length for every barrel at 16 and 19: the longest + this
FITTING_D = 10.0                            # push-in fitting for the 4 mm hose on the stator's face
GEAR_C = 45.0                               # layshaft (crank side) above the rotor shaft
BLEED_D = 1.0                               # module v4.4's bleed hole (stage3v4_coaxial_chamber.py), as v1.1's
# the rotor, worked out in rotor_timing.py (plain Python): core circles, cams, ahead, gear, charge time
_rt = {"__file__": os.path.join(REPO, "mitrailleuse", "rotor_timing.py")}
exec(open(_rt["__file__"], encoding="utf-8").read().rsplit("\nif __name__", 1)[0], _rt)
VENT_R, CHARGE_R, GEAR, CHARGE_AHEAD, T_FILL = (_rt[k] for k in ("VENT_R", "CHARGE_R", "GEAR", "AHEAD", "T_FILL"))
CHAMBER_CM3, P_WORK = 100.0, 2.0            # module chamber, working pressure (bar gauge)
POCKET_D, SEAT_D = 31.0, 16.0               # module v4.4: pilot acts on the diaphragm, chamber outside the seat
DUMP_JET = 0.5                              # the dump valve vents the head through this: slow enough not to fire
COMMON_A = ("Rails", "Head_body", "Head_spider", "Rotor_shaft", "Reduction_gears", "Layshaft", "Clutch",
            "Gear_plate", "Bevel_box", "Crank_shaft", "Crank_arm", "Crank_knob", "Rear_frame", "Rear_grip",
            "Supply_hose", "Flex_shaft_input", "Trigger", "Trigger_rod", "Rear_casing", "Dump_valve", "Dump_key",
            "Detent_plunger")
FV.STYLES["swap"] = ((0.85, 0.30, 0.50), 30)


def arc_stadium(r, width, arc_len, z0, z1, a_mid):
    """A stadium bent along the circle r: arc_len between its end centres, at angle a_mid (deg)."""
    da = math.degrees(arc_len / r)
    body = Part.makeCylinder(r + width / 2, z1 - z0, V(0, 0, z0), Z, da).cut(
        Part.makeCylinder(r - width / 2, z1 - z0 + 2, V(0, 0, z0 - 1), Z, da))
    body.rotate(V(0, 0, 0), Z, a_mid - da / 2)
    ends = [cyl(width, z0, z1, *polar(r, a_mid + sx * da / 2)) for sx in (-1, 1)]
    return body.fuse(ends)


def firing_head(n, z_face):
    """Core block and cam rotor for n barrels (rotor_timing.py), barrel 0 at 0 deg, the block's rear face z_face.

    Core block: a printed disc, per barrel a vent core on VENT_R and a charge core on CHARGE_R on the same
    radius line, both pin-out to the rear under a printed button; the pilot fitting in front, on CHARGE_R.
    Rotor: a cam disc behind it with a long rail on CHARGE_R (AHEAD charge buttons) and a short one on
    VENT_R, drawn parked at a detent (ports at x = j + 0.5, the rotor turning towards +angle).
    """
    k = _rt["cams"](n)
    pitch_a = 360.0 / n
    out = {}
    block = cyl(2 * HEAD[0] - 0.4, z_face, z_face + 23)
    cores, buttons = [], []
    for i in range(n):
        for r in (VENT_R, CHARGE_R):
            xy = polar(r, pitch_a * i)
            block = block.cut(cyl(_rt["CORE_CB"], z_face - 1, z_face + 5, *xy))
            cores.append(cyl(5.2, z_face + 4, z_face + 9, *xy).fuse(cyl(3.0, z_face + 9, z_face + 18, *xy)))
            buttons.append(cyl(_rt["CORE_CB"] - 0.4, z_face - 0.5, z_face + 4, *xy)
                           .fuse(cyl(_rt["BUTTON_D"], z_face - 3, z_face - 0.5, *xy)))
    out["Port_stator"], out["Valve_cores"], out["Core_buttons"] = block, G.fuse_all(cores), G.fuse_all(buttons)
    # x (pitches) -> angle: a port at x sits x pitches ahead (+angle) of the zero point; port 0 parks at 0.5
    ang = lambda x: (x - 0.5) * pitch_a
    disc = cyl(2 * CHARGE_R + 20, z_face - 14, z_face - 8).fuse(cyl(30, z_face - 20, z_face - 8))
    rails = []
    for (a0, a1), r in ((k["top_c"], CHARGE_R), (_rt["VENT_TOP"], VENT_R)):
        r0, r1 = a0 - _rt["RAMP"], a1 + _rt["RAMP"]
        arc = (r1 - r0) * 2 * math.pi * r / n
        rails.append(arc_stadium(r, 6.0, arc - 6.0, z_face - 8, z_face - 3 - _rt["TRAVEL"] + 0.5, ang((r0 + r1) / 2)))
    out["Rotor"] = disc.fuse(rails)
    # ratchet detent: n saw teeth, the steep face backwards
    r_o, r_i, pts = 25.0, 21.0, []
    for i in range(n):
        a0 = pitch_a * i
        pts += [V(*polar(r_o, a0), 0), V(*polar(r_i, a0 + 0.12 * pitch_a), 0)]
    wheel = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, 6))
    wheel.translate(V(0, 0, z_face - 28))
    out["Detent_wheel"] = wheel.cut(cyl(10, z_face - 29, z_face - 21))
    return out, k


def fill_time(frac=0.9, d=BLEED_D, v=CHAMBER_CM3, pg=P_WORK, cd=0.65):
    """s to fill a module's chamber to frac of pg through its bleed hole (isothermal, orifice flow)."""
    R, T, k = 287.0, 293.0, 1.4
    A, V, p0, p = math.pi * (d / 1000) ** 2 / 4, v * 1e-6, 1.013e5 + pg * 1e5, 1.013e5
    t, dt = 0.0, 1e-4
    while p < 1.013e5 + frac * pg * 1e5:
        r = p / p0
        if r <= (2 / (k + 1)) ** (k / (k - 1)):
            m = cd * A * p0 * math.sqrt(k / (R * T)) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
        else:
            m = cd * A * p0 * math.sqrt(2 * k / ((k - 1) * R * T) * (r ** (2 / k) - r ** ((k + 1) / k)))
        p += m * R * T / V * dt
        t += dt
    return t


def orifice(p0, p1, d, cd=0.65):
    """kg/s of air through an orifice of d mm, p0 -> p1 Pa absolute."""
    R, T, k = 287.0, 293.0, 1.4
    A, r = math.pi * (d / 1000) ** 2 / 4, p1 / p0
    if r <= (2 / (k + 1)) ** (k / (k - 1)):
        return cd * A * p0 * math.sqrt(k / (R * T)) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
    return cd * A * p0 * math.sqrt(2 * k / ((k - 1) * R * T) * (r ** (2 / k) - r ** ((k + 1) / k)))


def drain(k, d_jet=DUMP_JET):
    """k charged chambers emptied through their bleeds into the head, vented through d_jet (quasi-steady).

    Returns (s to 0.05 bar, the lowest pilot / chamber gauge ratio): the valve stays shut while that ratio
    stays over 1 - (seat / pocket)^2.
    """
    pa, pc, t, worst, V = 1.013e5, 1.013e5 + P_WORK * 1e5, 0.0, 1.0, CHAMBER_CM3 * 1e-6
    while pc - pa > 0.05e5:
        lo, hi = pa, pc
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if k * orifice(pc, mid, BLEED_D) > orifice(mid, pa, d_jet) else (lo, mid)
        worst = min(worst, (lo - pa) / (pc - pa))
        pc -= orifice(pc, lo, BLEED_D) * 287.0 * 293.0 / V * 0.02
        t += 0.02
    return t, worst


def concept_a(key):
    pts, m = modules(key)
    n = len(pts)
    R = REAR_R
    r_rail = R + 10
    p = {}
    p["Front_plate"] = (plate(key, 2 * R + 12, 25.4, 268, 276), "swap")
    p["Rear_plate"] = (plate(key, 2 * R + 12, 38.4, 2, 10), "swap")
    p["Rails"] = (rails(r_rail, -150, 290), "alu")
    z_face, z_h1 = -143.0, -120.0
    z_h0 = z_face
    # head: a fixed body (inlet, mounts) round the distributor; the supply comes in through the body and a
    # radial hole in the stator to its centre, where the rotor's spigot picks it up
    p["Head_body"] = (tube(2 * HEAD[1], HEAD[1] - HEAD[0], z_h0, z_h1)
                      .fuse(rod(16, (HEAD[1] - 2, 0, z_h0 + 15), (HEAD[1] + 12, 0, z_h0 + 15))), "rotor")
    spider = G.fuse_all([rod(14, polar(HEAD[1] - 2, a) + (z_h0 + 12,), polar(r_rail, a) + (z_h0 + 12,))
                         for a in (45, 135, 225, 315)])
    p["Head_spider"] = (spider, "frame")
    # stator ports in the modules' angular order, one hose each to its pilot fitting
    dist, _ = firing_head(n, z_face)
    ang = [math.degrees(math.atan2(y, x)) % 360.0 for x, y in pts]
    order = sorted(range(n), key=lambda i: (ang[i], math.hypot(*pts[i])))
    a_first = ang[order[0]]
    fittings, hoses, lengths = [], [], []
    for k, i in enumerate(order):
        cx, cy = polar(CHARGE_R, a_first + 360.0 / n * k)
        fittings.append(cyl(FITTING_D, z_h1, z_h1 + 8, cx, cy))
        a, b = V(pts[i][0], pts[i][1], -47.2), V(cx, cy, z_h1 + 8)
        hoses.append(rod(4, a, b))
        lengths.append((a - b).Length)
    for s in dist.values():
        s.rotate(V(0, 0, 0), Z, a_first)
    DETAIL[key] = {nm: s.copy() for nm, s in dist.items()}
    dist["Port_stator"] = dist["Port_stator"].fuse(G.fuse_all(fittings))
    for nm, s in dist.items():
        p[nm] = (s, {"Valve_cores": "steel", "Core_buttons": "printed"}.get(nm, "swap"))
    p["Pilot_hoses"] = (G.fuse_all(hoses), "hose")
    # drive: crank -> 1:1 bevel -> layshaft -> 5:1 spur pair -> dog clutch (trigger) -> rotor shaft
    p["Rotor_shaft"] = (cyl(10, -200, z_face - 20), "steel")
    p["Reduction_gears"] = (cyl(75, -186, -180).fuse(cyl(15, -186, -180, 0, GEAR_C)), "printed")
    p["Layshaft"] = (cyl(10, -215, -176, 0, GEAR_C), "steel")
    p["Clutch"] = (cyl(26, -179, -171), "steel")
    p["Gear_plate"] = (box(-50, 50, -30, GEAR_C + 15, -192, -188), "frame")
    p["Bevel_box"] = (box(-42, 22, GEAR_C - 22, GEAR_C + 22, -225, -195), "frame")
    sh, ca, kn = crank(-210, 42, GEAR_C)
    p["Crank_shaft"], p["Crank_arm"], p["Crank_knob"] = (sh, "steel"), (ca, "steel"), (kn, "printed")
    y_low = -r_rail * 0.72
    p["Rear_frame"] = (box(-r_rail * 0.72, r_rail * 0.72, y_low - 6, y_low + 6, -215, z_h0)
                       .fuse(box(-14, 14, y_low, -30, -192, -188)), "frame")
    p["Rear_grip"] = (rear_grip(y_low, -200), "printed")
    # dump valve on the inlet, turned by a key: shuts the supply and vents the head through DUMP_JET, so the
    # charged chambers (all under the charge slot, see the detent) empty back through their bleeds, unfired
    xv = HEAD[1] + 12
    p["Dump_valve"] = (box(xv, xv + 24, -9, 9, z_h0 + 6, z_h0 + 24), "steel")          # a small brass ball valve
    p["Dump_key"] = (cyl(8, z_h0 - 12, z_h0 + 6, xv + 12, 0).fuse(box(xv + 2, xv + 22, -3, 3, z_h0 - 22, z_h0 - 12)),
                     "oring")
    p["Supply_hose"] = (rod(8, (xv + 24, 0, z_h0 + 15), (xv + 89, -60, z_h0 - 60)), "hose")
    # ratchet detent (in distributor()): parks the rotor with the band's edges between ports, forward only
    p["Detent_plunger"] = (cyl(6, z_face - 28, z_face - 22, 0, 31).fuse(cyl(10, z_face - 29, z_face - 21, 0, 40)),
                           "steel")
    z_tip = 310.7 + SLEEVE[2]
    p["Muzzle_sleeves"] = (G.fuse_all([tube(SLEEVE[0], SLEEVE[1], 314.7, z_tip, x, y) for x, y in pts]), "sleeve")
    p["Sleeve_band"] = (plate(key, 2 * R + 4, SLEEVE[0] + 0.4, z_tip - 30, z_tip - 26), "swap")
    # the second crew member may crank it instead, through a flexible shaft into the back of the bevel box
    p["Flex_shaft_input"] = (cyl(12, -245, -225, 0, GEAR_C).fuse(cyl(22, -260, -245, 0, GEAR_C)), "steel")
    # trigger: pulled, it pushes the clutch's dogs into the big gear; released, a spring parts them
    p["Trigger"] = (box(-3, 3, y_low - 30, y_low - 8, -179, -171), "steel")
    p["Trigger_rod"] = (box(-2, 2, y_low - 8, -13, -177, -173).fuse(box(-15, 15, -17, -13, -177, -173)), "steel")
    p["Rear_casing"] = (tube(2 * r_rail + 20, 2.0, -230, -45), "casing")
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
DETAIL = {}                                 # the distributor's parts, per pack, for an exploded picture


def check(ok, text):
    print("[%s] %s" % ("OK " if ok else "FAIL", text))
    return ok


def rear_report(built):
    """The A rear block is one set of parts for 16 and 19; what changes is listed; the firing rate."""
    a16, a19 = built["A16"], built["A19"]
    same = [n for n in COMMON_A if abs(a16[n][0].Volume - a19[n][0].Volume) < 1e-3
            and (a16[n][0].BoundBox.Center - a19[n][0].BoundBox.Center).Length < 1e-3]
    rear_g = sum(a16[n][0].Volume / 1000 * (DENSITY["alu"] if n == "Rails" else DENSITY.get(a16[n][1], 0.6))
                 for n in COMMON_A)
    check(len(same) == len(COMMON_A), "A rear block: %d of %d parts the same at 16 and 19 (%s), %.0f g"
          % (len(same), len(COMMON_A), ", ".join(sorted(set(COMMON_A) - set(same))) or "all", rear_g))
    cut = math.ceil((max(max(L) for L in HOSES.values()) + HOSE_SLACK) / 10.0) * 10.0
    t_model = fill_time(0.9)
    t90 = T_FILL
    print("      chamber %.0f cm3 charged in %.2f s (%s); the orifice model, to 90 %% of %.0f bar through Ø%.1f: %.2f s"
          " (Ø0.8: %.2f s; isothermal, Cd 0.65, so on the slow side)"
          % (CHAMBER_CM3, t90, "bench", P_WORK, BLEED_D, t_model, fill_time(0.9, 0.8)))
    shut = 1 - (SEAT_D / POCKET_D) ** 2
    for k in range(1, CHARGE_AHEAD + 1):
        t, worst = drain(k)
        check(worst >= shut + 0.1, "dump through Ø%.1f, %d chamber(s) charged: pilot keeps >= %.2f of the chamber's"
              " pressure (opens below %.2f), empty in %.0f s" % (DUMP_JET, k, worst, shut, t))
    for tag, key in (("A16", "j_rings_4_12"), ("A19", "g_hex_19")):
        n = len(LAYOUT[key])
        L = HOSES[key]
        k = _rt["cams"](n)
        check(k["pc"] >= FITTING_D + 2.0, "%s: %d pilot fittings on R %.0f, pitch %.1f mm (push-in Ø%.0f + 2)"
              % (tag, n, CHARGE_R, k["pc"], FITTING_D))
        check(k["clear_v"] >= 3.0, "%s: buttons Ø%.0f, %.1f mm apart on the vent circle (%.1f on the charge one)"
              % (tag, _rt["BUTTON_D"], k["clear_v"], k["clear_c"]))
        check(max(k["ramp_c"], k["ramp_v"]) <= 32.0, "%s: rail ramps %.0f / %.0f deg (charge / vent)"
              % (tag, k["ramp_c"], k["ramp_v"]))
        check(k["shut"] > 0 and not k["on_ramp"], "%s: both cores shut %.2f pitch between charge and vent; parked"
              " off the ramps" % (tag, k["shut"]))
        check(k["charge"] >= CHARGE_AHEAD - 0.5, "%s: %d ahead: each barrel charges %.2f shot intervals"
              % (tag, CHARGE_AHEAD, k["charge"]))
        print("      %s: rails %.0f / %.0f mm; button %.1f N at 5 bar; rotor torque <= %.2f N m, %.1f N on the"
              " crank knob" % (tag, k["rail_c"], k["rail_v"], k["f_core"], k["t_rotor"], k["f_crank"]))
        print("      %s: <= %.1f shots/s, %.1f s a volley; %.1f shots a crank turn, crank <= %.2f turns/s"
              % (tag, k["rate"], k["volley"], k["per_turn"], k["crank_rate"]))
        for a in sorted({1, 2, 3} - {CHARGE_AHEAD}):
            ka = _rt["cams"](n, a)
            print("      %s with %d ahead: <= %.1f shots/s, %.1f s a volley" % (tag, a, ka["rate"], ka["volley"]))
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
    if key in DETAIL:                              # the distributor pulled apart along its axis, behind the gun
        for j, nm in enumerate(("Port_stator", "Valve_cores", "Core_buttons", "Rotor", "Detent_wheel")):
            s = DETAIL[key][nm].copy()
            s.translate(V(0, 0, -400 - 25 * j))
            sc.add(tag + "_rotor", "%s_rotor_%s" % (tag, nm), to_view(s),
                   {"Valve_cores": "steel", "Core_buttons": "printed"}.get(nm, "swap"), offset=off)
rear_report(BUILT)
labels = [
    ("A16: МОНТИНЬИ, 4+12 — пакет стоит, головка-распределитель, шланги", 0),
    ("A19: МОНТИНЬИ, соты 19", 1),
    ("B16: ГАТЛИНГ, 4+12 — крутится пакет, ниппели в казённом диске", 2),
    ("B19: ГАТЛИНГ, соты 19 — центральный ствол толкателем через ось", 3),
]
for text, i in labels:
    sc.label("Labels", text, (160, -X_OFF * i, 340))
sc.finish()
