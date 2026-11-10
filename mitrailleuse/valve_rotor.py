# -*- coding: utf-8 -*-
"""
Mitrailleuse concept A after bench B: a rotor around bought 3/2 push-button valves, on paper
(plain Python, no FreeCAD).

Bench B (head_bench.py, tyre-valve cores) failed on 2026-11-10: the cores leak badly. The
nipple head is not the gun. Twenty valves are on order, drawing in hand, parts not yet, so
normally-open vs normally-closed is unmeasured. The drawing matches Koganei TAC2-31P (3-port,
spring-return push button, Rc1/8, NC and NO by piping). Catalog numbers below are that
valve's; a clone can differ, and nothing here is drawn in FreeCAD until the real parts are
measured (docs/human-todo.md).

One valve per barrel. The button faces the rotor. The order drawing and the body photo put
the ports on opposite ends of the 31.8 mm length: 1(P) and 3(R) on one 16 mm face, 2(A)
alone on the other. The wide faces carry the Ø5.2 mounting holes and no ports. Turned with
16 mm tangential and 31.8 radial, A points out to the module and P+R point into the hole
of the plate. The other way round points the ports at the neighbours and does not fit the
plate; that ring is only printed as a check. A face cam
presses a small pusher into the button and lets go. Pressed, supply feeds the pilot and the
chamber fills through the module's Ø1.0 bleed. Released, the pilot vents and the module
fires. At rest the pilot is open to exhaust, so a barrel is under pressure only while its
button is down.

Two cams, same ring:

  hold   the lobe keeps ~1.5 valves switched (two charging, as the nipple rotor did).
         A barrel is pressed for the fill time, ~0.5 s, then released and fires. The lobe
         is longer than the pitch, so a parked rotor still holds a button down. The trigger
         therefore has its own cock, not one of the twenty valves: held, supply is on;
         released, the manifold vents through a Ø0.5 jet and those chambers drain back
         without firing (the nipple head's quiet dump, still to be repeated on this valve).
  gap    the lobe is shorter than the pitch, so the rotor can park with every button up
         and the supply can stay connected. The fill still takes ~0.5 s, and the ramps eat
         most of the pitch, so the volley is slow. Printed so the trade is visible.

The gun drawn here has 19 barrels. Twenty valves were bought, so one is a spare.

Run:  python3 mitrailleuse/valve_rotor.py
Writes docs/img/valve_rotor.svg, a sketch of the 19-barrel head. rotor_timing.py remains
the nipple rotor's numbers.
"""

import math
import os
import sys

# Drawing the owner ordered (mm). 2.4 sits by the button; on the TAC2 sheet that callout is the
# stroke, not a body edge: 0.8 pre-travel, 0.8 main, 0.8 overtravel.
BODY_W, BODY_T = 31.8, 16.0          # mounting-face width, thickness along the screw axis
OVERALL_H = 45.8                     # button tip to the far face, from the drawing
BUTTON_D = 10.6
STEM_THREAD = "M12x1"
MOUNT_D, MOUNT_OFF = 5.2, 9.2        # 2 holes, offset from the mounting-face centreline
STROKE = 2.4
PRE, MAIN, OVER = 0.8, 0.8, 0.8
SWITCH = PRE + MAIN                  # fully switched at 1.6; do not pass 2.4
PRESS = 2.0                          # the cam's rise at the button: past the switch, inside the overtravel
PRESS_TOL = 0.3                      # the stack has to land inside 1.6..2.4; the nipple stack's ±0.4 does not

# TAC2-31P catalog (Koganei). The ordered part is identified by the drawing, not by a box in hand.
AREA = 5.5                           # mm2 effective area
CV = 0.27
MASS_G = 55.0
P_MIN, P_MAX = 0.05, 0.9             # MPa operating range
F_HZ = 5.0                           # catalog max operating frequency
BLEED_D = 1.0                        # module v4.4, mm; charge time is this hole's, measured ~0.5 s
T_FILL = 0.5                         # s, v1.1 bench, Ø1.0, chamber 100 cm3, 2 bar
CHAMBER_V = 100.0                    # cm3

# Ring. Port faces are the ends of the 31.8 mm length, so that length is radial:
# A outward, P and R inward. 16 mm is tangential.
# WALL is the plastic between neighbouring inner corners (a pocket; the M5 holes are not
# used). SCREW_WALL is the same ring if those holes take an M5 into the wall.
TANGENTIAL, RADIAL = BODY_T, BODY_W
WALL = 3.0
SCREW_WALL = 8.0
HEAD_PLATE_R = 98.0                  # rear_frame.py HP_R, the current disc
RAIL_R = 104.0                       # pack_frame.py, four tubes; they end at the head plate

# Cam. A pusher with a small dome, so the follower is treated as a point. Ramps are mm of arc,
# not a fraction of the pitch: the slope is what the (still unmeasured) button force climbs.
RAMP_MM = 6.0
HOLD_PITCHES = 1.5                   # "hold": valves switched at once, so the fill spans 1.5 shots
PARK_GAP = 8.0                       # "gap": mm of arc the Ø3 tip must fit in, clear of both ramps
TIP_D = 3.0                          # pusher nose, mm; small so the point-follower timing is close
GEAR = 5.0
CRANK_R = 70.0                       # mm, same crank as the nipple rotor, so the forces compare
MU = 0.2                             # greased printed dome on a printed cam, as rotor_timing.py
FORCES = (15.0, 25.0, 40.0)          # N, a sensitivity sweep: the button force is not measured
BOUGHT = 20
GUN_N = 19                           # the head being drawn; 16 stays in the tables
JET_D = 0.5                          # quiet-dump jet, the nipple head's

PACKS = (16, 19, 20)


def bleed_area():
    return math.pi * BLEED_D ** 2 / 4.0


def point_seg(p, a, b):
    """Distance from point p to segment ab."""
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0.0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def rect(R, tangential, radial):
    """Body corners, centre on +x at radius R, inner face toward the origin."""
    hx, hy = radial / 2.0, tangential / 2.0
    return ((R - hx, -hy), (R - hx, hy), (R + hx, hy), (R + hx, -hy))


def spin(poly, ang):
    c, s = math.cos(ang), math.sin(ang)
    return tuple((x * c - y * s, x * s + y * c) for x, y in poly)


def poly_gap(a, b):
    """Euclidean gap between two convex polygons; negative when they overlap."""
    def axes(poly):
        out = []
        for i, (x0, y0) in enumerate(poly):
            x1, y1 = poly[(i + 1) % len(poly)]
            L = math.hypot(x1 - x0, y1 - y0)
            out.append((-(y1 - y0) / L, (x1 - x0) / L))
        return out

    def project(poly, ax):
        dots = [x * ax[0] + y * ax[1] for x, y in poly]
        return min(dots), max(dots)

    separated = False
    pen = 1e9
    for ax in axes(a) + axes(b):
        a0, a1 = project(a, ax)
        b0, b1 = project(b, ax)
        sep = max(b0 - a1, a0 - b1)
        if sep > 0.0:
            separated = True
        else:
            pen = min(pen, -sep)
    if not separated:
        return -pen

    def vertex_edge(poly, other):
        best = 1e9
        for p in poly:
            for i, q in enumerate(other):
                best = min(best, point_seg(p, q, other[(i + 1) % len(other)]))
        return best

    return min(vertex_edge(a, b), vertex_edge(b, a))


def ring(n, tangential, radial, wall):
    """Smallest button-circle radius whose neighbouring bodies stay `wall` mm apart."""
    lo, hi = radial / 2.0 + 1.0, radial / 2.0 + 1.0
    step = 2 * math.pi / n

    def gap(R):
        body = rect(R, tangential, radial)
        return poly_gap(body, spin(body, step))

    while gap(hi) < wall:
        hi += 20.0
        if hi > 2000.0:
            raise RuntimeError("no ring radius for n=%d" % n)
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if gap(mid) >= wall:
            hi = mid
        else:
            lo = mid
    R = hi
    pitch = step * R
    return dict(n=n, R=R, pitch=pitch, wall=wall, tangential=tangential, radial=radial,
                r_in=R - radial / 2.0, r_out=R + radial / 2.0, gap=gap(R),
                plate=R + radial / 2.0 <= HEAD_PLATE_R)


def height(x, lobe):
    """Cam rise (mm) at arc position x (mm). Plateau [0, Lp]; ramps of Lr outside it.

    A valve's x falls as the rotor turns: it climbs the ramp above Lp, rides the plateau,
    and releases down the ramp below 0.
    """
    lp, lr, h = lobe["lp"], lobe["lr"], lobe["h"]
    if 0.0 <= x <= lp:
        return h
    if lp < x < lp + lr:
        return h * (lp + lr - x) / lr
    if -lr < x < 0.0:
        return h * (x + lr) / lr
    return 0.0


def switched_band(lobe):
    """Arc length (mm) where the button is past SWITCH, and the arc where the cam touches it."""
    frac = (lobe["h"] - SWITCH) / lobe["h"]
    hold = lobe["lp"] + 2.0 * lobe["lr"] * frac
    touch = lobe["lp"] + 2.0 * lobe["lr"]
    return hold, touch


def lobe_hold(pitch):
    """Lobe that keeps HOLD_PITCHES valves past the switch point."""
    lr = RAMP_MM
    hold = HOLD_PITCHES * pitch
    lp = hold - 2.0 * lr * (PRESS - SWITCH) / PRESS
    return dict(lp=lp, lr=lr, h=PRESS, kind="hold")


def lobe_gap(pitch):
    """Longest lobe that still leaves PARK_GAP mm where the follower touches nothing."""
    lr = RAMP_MM
    touch = pitch - PARK_GAP
    lp = touch - 2.0 * lr
    return dict(lp=lp, lr=lr, h=PRESS, kind="gap")


def rate_of(lobe, pitch):
    """Shots/s when the switched band lasts T_FILL. None if the lobe does not fit."""
    hold, touch = switched_band(lobe)
    if lobe["lp"] <= 0.0 or hold <= 0.0:
        return None
    return hold / (pitch * T_FILL), hold, touch


def cam_x(x, circ):
    """Arc position folded next to the lobe, which sits at [-lr, lp+lr] around 0."""
    x = x % circ
    if x > circ / 2.0:
        x -= circ
    return x


def detent(lobe, pitch, n, empty=False):
    """Park phase (mm) with no button on a ramp, the most clearance, and how many are fully down.

    Clearance is the smallest arc from any button centre to a ramp. `empty` keeps only phases
    where every button is up (the gap cam). None if nothing qualifies with clearance over 1 mm.
    """
    lr, lp = lobe["lr"], lobe["lp"]
    circ = n * pitch
    best = None
    steps = 800
    for s in range(steps):
        phase = pitch * s / steps
        down = 0
        partial = False
        clear = 1e9
        for j in range(n):
            x = cam_x(phase + j * pitch, circ)
            h = height(x, lobe)
            if h >= PRESS - 1e-6:
                down += 1
                clear = min(clear, min(x, lp - x))
            elif h > 1e-6:
                partial = True
                break
            else:
                if x < 0.0:
                    clear = min(clear, -lr - x)
                else:
                    clear = min(clear, x - (lp + lr))
        if partial or clear < 1.0 or (empty and down != 0):
            continue
        if best is None or clear > best["clear"]:
            best = dict(phase=phase, down=down, clear=clear)
    return best


def torque(lobe, pitch, n, force):
    """Peak resisting torque (N·m) and the axial load (N) over one pitch.

    Full button force wherever the cam touches, which overstates the ramps (the real force
    grows along the stroke). Down the release ramp the button spring helps and is taken as
    nothing, as in rotor_timing.py. Friction under every pusher that is touching.
    """
    lr = lobe["lr"]
    worst_t, worst_a = 0.0, 0.0
    steps = 360
    for s in range(steps):
        shift = pitch * s / steps
        tq, axial = 0.0, 0.0
        for j in range(n):
            x = j * pitch - shift
            h = height(x, lobe)
            if h <= 0.0:
                continue
            slope = (height(x + 1e-3, lobe) - height(x - 1e-3, lobe)) / 2e-3
            # x falls as the rotor turns, so a positive slope (rising as x rises) is the
            # release ramp; the climb is a negative slope and opposes the turn
            tq += force * max(-slope, 0.0) + MU * force
            axial += force
        worst_t = max(worst_t, tq)
        worst_a = max(worst_a, axial)
    R = pitch * n / (2.0 * math.pi)
    return worst_t * R / 1000.0, worst_a


def crank_force(torque_nm):
    return torque_nm / (GEAR * CRANK_R / 1000.0)


def pilot_ms(volume_cm3=1.0):
    """Order-of-magnitude dump time through AREA mm2 from 2 bar gauge, choked, Cd 0.8.

    An estimate of how fast the pilot's air mass can leave, not a measured snap. The chamber
    itself still fills through the Ø1.0 bleed.
    """
    cd, gamma, r_air, temp = 0.8, 1.4, 287.0, 293.0
    p = 3.0e5
    crit = (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))
    mdot = cd * (AREA * 1e-6) * p * math.sqrt(gamma / (r_air * temp)) * crit
    mass = p * (volume_cm3 * 1e-6) / (r_air * temp)
    return 1000.0 * mass / mdot


def scheme(name, rg, lobe, empty_park=False):
    rated = rate_of(lobe, rg["pitch"])
    if rated is None:
        return dict(name=name, ok=False, reason="lobe does not fit the pitch")
    shots, hold, touch = rated
    interval = 1.0 / shots
    park = detent(lobe, rg["pitch"], rg["n"], empty=empty_park)
    forces = []
    for f in FORCES:
        tq, axial = torque(lobe, rg["pitch"], rg["n"], f)
        forces.append(dict(f=f, tq=tq, axial=axial, crank=crank_force(tq)))
    return dict(name=name, ok=True, lobe=lobe, shots=shots, interval=interval, hold=hold,
                touch=touch, volley=rg["n"] * interval, per_turn=rg["n"] / GEAR,
                crank_hz=shots * GEAR / rg["n"], park=park, forces=forces,
                on_ramp=park is None)


def report_ring(rg, label):
    print("  %s  n=%d  button R %.1f  pitch %.1f mm  body R %.1f..%.1f  corner gap %.2f mm%s"
          % (label, rg["n"], rg["R"], rg["pitch"], rg["r_in"], rg["r_out"], rg["gap"],
             "  (inside the R%.0f plate)" % HEAD_PLATE_R if rg["plate"] else
             "  (body outside the R%.0f plate)" % HEAD_PLATE_R))


def report():
    print("valve rotor: TAC2-31P pattern, %d bought, one per barrel" % BOUGHT)
    print("  body %.1f x %.1f x %.1f mm overall, button Ø%.1f, stroke %.1f (switch %.1f, stop %.1f),"
          " cam presses %.1f" % (BODY_W, BODY_T, OVERALL_H, BUTTON_D, STROKE, SWITCH, STROKE, PRESS))
    print("  catalog: area %.1f mm2 (bleed Ø%.1f is %.2f mm2, %.1f x smaller), %.0f g, %.2f..%.1f MPa, %.0f Hz"
          % (AREA, BLEED_D, bleed_area(), AREA / bleed_area(), MASS_G, P_MIN, P_MAX, F_HZ))
    print("  pilot dump estimate: %.2f ms per cm3 through the valve at 2 bar (not a bench number)"
          % pilot_ms(1.0))
    print("rings, A outward and P+R inward, %.1f mm between inner corners:" % WALL)
    rings = []
    for n in PACKS:
        rg = ring(n, TANGENTIAL, RADIAL, WALL)
        rings.append(rg)
        report_ring(rg, "pocket")
    print("same ring with an M5 wall of %.0f mm (the drawing's Ø%.1f holes):" % (SCREW_WALL, MOUNT_D))
    for n in PACKS:
        report_ring(ring(n, TANGENTIAL, RADIAL, SCREW_WALL), "screwed")
    print("turned so the ports face the neighbours, pocket wall %.0f mm, 31.8 tangential:" % WALL)
    for n in PACKS:
        report_ring(ring(n, BODY_W, BODY_T, WALL), "flipped")
    print("cams on the pocket ring (ramp %.0f mm, fill %.2f s):" % (RAMP_MM, T_FILL))
    built = []
    for rg in rings:
        for name, lobe, empty in (("hold", lobe_hold(rg["pitch"]), False),
                                  ("gap", lobe_gap(rg["pitch"]), True)):
            sc = scheme(name, rg, lobe, empty_park=empty)
            built.append((rg, sc))
            if not sc["ok"]:
                print("  n=%d %s: %s" % (rg["n"], name, sc["reason"]))
                continue
            park = sc["park"]
            where = "no park with every button off a ramp" if park is None else \
                "park holds %d fully down, %.1f mm clear of a ramp" % (park["down"], park["clear"])
            print("  n=%d %s: plateau %.1f + ramps 2x%.0f mm, switched %.1f mm, touch %.1f mm"
                  % (rg["n"], name, lobe["lp"], lobe["lr"], sc["hold"], sc["touch"]))
            print("     %.2f shots/s, volley %.1f s, %.1f shots a crank turn, crank %.2f turns/s; %s"
                  % (sc["shots"], sc["volley"], sc["per_turn"], sc["crank_hz"], where))
            for row in sc["forces"]:
                print("     button %.0f N -> rotor %.2f N·m, crank %.1f N, axial %.0f N"
                      % (row["f"], row["tq"], row["crank"], row["axial"]))
    print("the head is %d barrels; %d valves bought, %d spare. The trigger's supply valve is separate."
          % (GUN_N, BOUGHT, BOUGHT - GUN_N))
    return rings, built


def checks(rings, built):
    """Geometry the picture and the doc rely on. A failure is a bad ring, not a close fit."""
    bad = []
    by_n = {rg["n"]: rg for rg in rings}
    if not by_n[20]["plate"]:
        bad.append("20-valve pocket ring does not fit the R%.0f plate" % HEAD_PLATE_R)
    for rg in rings:
        if rg["gap"] < WALL - 0.05:
            bad.append("n=%d corner gap %.2f < wall %.1f" % (rg["n"], rg["gap"], WALL))
        if PRESS - PRESS_TOL < SWITCH or PRESS + PRESS_TOL > STROKE:
            bad.append("press %.2f ± %.2f leaves the switch/stop window" % (PRESS, PRESS_TOL))
    for rg, sc in built:
        if rg["n"] == 20 and sc["name"] == "hold" and (not sc["ok"] or sc["park"] is None
                                                        or sc["park"]["down"] < 1
                                                        or sc["park"]["clear"] < TIP_D / 2.0 + 0.5):
            bad.append("hold cam has no detent clear of the ramps for a Ø%.0f tip" % TIP_D)
        if rg["n"] == 20 and sc["name"] == "gap":
            if not sc["ok"] or sc["park"] is None or sc["park"]["down"] != 0:
                bad.append("gap cam does not park with every button up")
            elif sc["park"]["clear"] < TIP_D / 2.0 + 0.5:
                bad.append("gap park clearance %.2f does not clear a Ø%.0f tip" % (sc["park"]["clear"], TIP_D))
    for line in bad:
        print("FAIL", line)
    if not bad:
        print("checks: OK")
    return not bad


def svg(path, rg, sc_hold):
    """Sketch sheet of the 19-barrel head: plan from the rotor, section along the axis.

    Radii, the body and the cam rise are the calculated ones. The axial gap, the pusher
    length and the cam-disc thickness are only there so the stack can be read; they are
    not a design yet.
    """
    W, H = 1180, 820
    ink, ink2, surf = "#0b0b0b", "#52514e", "#fcfcfb"
    blue, orange, body_c, plate_c, down_c = "#2a78d6", "#eb6834", "#d9d6cf", "#c8c4ba", "#c5d9f2"
    cx, cy, sc = 340.0, 430.0, 2.05
    lobe = sc_hold["lobe"]

    def P(x, y):
        return cx + sc * x, cy - sc * y

    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="Helvetica, Arial, sans-serif" font-size="13">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % surf,
         '<text x="28" y="34" font-size="20" fill="%s">Головка на 19 клапанов, эскиз</text>' % ink,
         '<text x="28" y="56" fill="%s">Куплено 20, один запасной. Снаружи один порт A, внутри два — P и R. '
         'Зазоры, толкатель и толщина диска условные.</text>' % ink2]

    def circle(r, color, width, dash=None):
        extra = "" if dash is None else ' stroke-dasharray="%s"' % dash
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%s"%s/>'
                 % (cx, cy, sc * r, color, width, extra))

    circle(HEAD_PLATE_R, plate_c, 1.4, "5 4")
    circle(rg["R"], "#c5d4ea", 0.8)

    step = 2.0 * math.pi / rg["n"]
    for j in range(rg["n"]):
        ang = math.pi / 2.0 - j * step
        poly = spin(rect(rg["R"], rg["tangential"], rg["radial"]), ang)
        x = j * rg["pitch"]
        down = 0.0 <= x <= lobe["lp"]
        pts = " ".join("%.1f,%.1f" % P(px, py) for px, py in poly)
        o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (pts, down_c if down else body_c, ink))
        bx, by = P(rg["R"] * math.cos(ang), rg["R"] * math.sin(ang))
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                 % (bx, by, max(2.4, sc * 1.6), orange if down else ink2))

    # lobe outside the bodies, so the release ramp is not hidden under a valve
    def arc(x0, x1, color, width, rad):
        pts = []
        for i in range(80):
            x = x0 + (x1 - x0) * i / 79.0
            ang = math.pi / 2.0 - x / rg["R"]
            px, py = P(rad * math.cos(ang), rad * math.sin(ang))
            pts.append("%.1f,%.1f" % (px, py))
        o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>'
                 % (" ".join(pts), color, width))

    arc_r = rg["r_out"] + 4.0
    arc(-lobe["lr"], 0.0, orange, 5, arc_r)
    arc(0.0, lobe["lp"], blue, 5, arc_r)
    arc(lobe["lp"], lobe["lp"] + lobe["lr"], ink2, 3, arc_r)

    # radius line along +x, through the gap between two bodies; labels sit in the hole
    x0, y0 = P(42.0, 0)
    x1, y1 = P(HEAD_PLATE_R, 0)
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.7"/>' % (x0, y0, x1, y1, ink2))
    for r in (rg["R"], rg["r_out"], HEAD_PLATE_R):
        xt, yt = P(r, 0)
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (xt, yt - 4, xt, yt + 4, ink))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">R %.0f  кнопки</text>'
             % (cx, cy - 40, ink, rg["R"]))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">R %.0f  корпус</text>'
             % (cx, cy - 24, ink, rg["r_out"]))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">R %.0f  плита</text>'
             % (cx, cy - 8, ink, HEAD_PLATE_R))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">шаг %.1f</text>'
             % (cx, cy + 18, ink, rg["pitch"]))
    # names for the two arcs, outside the plate
    def arc_name(x_cam, text, anchor):
        ang = math.pi / 2.0 - x_cam / rg["R"]
        rad = HEAD_PLATE_R + 14.0
        px, py = P(rad * math.cos(ang), rad * math.sin(ang))
        o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="%s">%s</text>'
                 % (px, py, ink, anchor, text))

    arc_name(-lobe["lr"], "выстрел", "end")
    arc_name(lobe["lp"] * 0.55, "набор", "start")
    o.append('<text x="28" y="78" fill="%s" font-size="15">А — со стороны ротора</text>' % ink)
    o.append('<text x="28" y="786" fill="%s">Синие корпуса нажаты. Дуга: синяя — набор, оранжевая — выстрел. '
             'Пунктир — плита. На корпусе снаружи A, внутри P и R.</text>' % ink2)

    # --- local section of the pressed valve. The shaft is on the axis, off this view. ---
    s = 4.0
    ox, by = 700.0, 430.0
    plate_t, gap, pusher_l, cam_t = 10.0, 4.0, 12.0, 14.0
    valve_s0 = plate_t + gap
    valve_s1 = valve_s0 + OVERALL_H
    cam_s = valve_s1 + pusher_l
    btn = BUTTON_D / 2.0
    rad_lo = rg["r_in"] - 8.0
    rad_hi = HEAD_PLATE_R

    def S(along, rad):
        return ox + s * along, by - s * (rad - rg["R"])

    o.append('<text x="%.0f" y="168" fill="%s" font-size="15">Б — нажатый клапан, к стволам слева</text>' % (ox, ink))
    o.append('<text x="%.0f" y="188" fill="%s" font-size="12">обрыв к оси. Зазор, толкатель и толщина диска '
             'условные.</text>' % (ox, ink2))

    def block(along, rad_top, along_w, rad_h, fill):
        x, y = S(along, rad_top)
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s"/>'
                 % (x, y, s * along_w, s * rad_h, fill, ink))

    block(0, rad_hi, plate_t, rad_hi - rad_lo, "#eeeae4")
    px, py = S(0, rad_hi)
    o.append('<clipPath id="plate"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>'
             % (px, py, s * plate_t, s * (rad_hi - rad_lo)))
    for i in range(16):
        y = py + i * 16
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.6" clip-path="url(#plate)"/>'
                 % (px - 10, y, px + s * plate_t + 24, y - 22, plate_c))
    # break toward the axis
    br = S(0, rad_lo)
    o.append('<path d="M %.1f %.1f l 6 -5 l 6 10 l 6 -10 l 6 10 l 6 -5" fill="none" stroke="%s"/>'
             % (br[0], br[1], ink))

    block(valve_s0, rg["r_out"], OVERALL_H, rg["r_out"] - rg["r_in"], down_c)
    block(valve_s1 - 6.0, rg["R"] + btn, 6.0, BUTTON_D, orange)
    # A alone on the outer face; P and R on the inner face, stacked along the button axis
    def port_mark(along, rad, lab, below):
        x, y = S(along, rad)
        o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s"/>' % (x, y, surf, ink))
        o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">%s</text>'
                 % (x, y + (16 if below else -8), ink, lab))

    a_along = valve_s0 + OVERALL_H * 0.48
    port_mark(a_along, rg["r_out"] - 1.0, "A", True)
    port_mark(valve_s0 + 12.0, rg["r_in"] + 1.0, "R", True)
    port_mark(valve_s1 - 14.0, rg["r_in"] + 1.0, "P", True)
    ax, ay = S(a_along, rg["r_out"] - 1.0)
    up = S(a_along, HEAD_PLATE_R + 4.0)
    left = S(plate_t, HEAD_PLATE_R + 4.0)
    o.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ax, ay, up[0], up[1], left[0], left[1], blue))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12">пилот к модулю</text>'
             % (left[0], left[1] - 6, blue))

    # cam disc at this radius, with the 2 mm pad in contact
    block(cam_s, rg["R"] + 12.0, cam_t, (rg["R"] + 12.0) - rad_lo, "#d6e4f4")
    br2 = S(cam_s, rad_lo)
    o.append('<path d="M %.1f %.1f l 8 -5 l 8 10 l 8 -10 l 8 10 l 8 -5" fill="none" stroke="%s"/>'
             % (br2[0], br2[1], ink))
    block(cam_s - PRESS, rg["R"] + 8.0, PRESS, 16.0, blue)
    btip = S(valve_s1, rg["R"])
    tip = S(cam_s - PRESS, rg["R"])
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>'
             % (btip[0], btip[1], tip[0], tip[1], ink))
    o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (tip[0], tip[1], ink))
    # button centerline
    c0, c1 = S(valve_s0, rg["R"]), S(cam_s + cam_t + 6.0, rg["R"])
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.6" stroke-dasharray="7 3 1.5 3"/>'
             % (c0[0], c0[1], c1[0], c1[1], ink2))
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12">R %.0f</text>' % (c1[0] + 4, c1[1] + 4, ink, rg["R"]))

    def dim_along(s0, s1, rad, label):
        x0, y0 = S(s0, rad)
        x1, _ = S(s1, rad)
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x0, y0, x1, y0, ink))
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x0, y0 - 4, x0, y0 + 4, ink))
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x1, y0 - 4, x1, y0 + 4, ink))
        o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12" text-anchor="middle">%s</text>'
                 % ((x0 + x1) / 2.0, y0 - 6, ink, label))

    dim_along(0, plate_t, HEAD_PLATE_R + 18.0, "10")
    dim_along(valve_s0, valve_s1, HEAD_PLATE_R + 18.0, "%.1f" % OVERALL_H)
    pad_top = S(cam_s - PRESS, rg["R"] + 14.0)
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12">2.0</text>' % (pad_top[0] - 4, pad_top[1] - 2, blue))
    kn = S(valve_s1 - 22.0, rg["R"] - btn - 5.0)
    o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="12">кнопка</text>' % (kn[0], kn[1], ink2))
    o.append('<text x="%.0f" y="582" fill="%s">плита 10 — размер нынешней. 45.8 и ход 2.4 — с чертежа заказа.</text>'
             % (ox, ink2))
    o.append('<text x="%.0f" y="602" fill="%s">синяя площадка 2.0 мм держит кнопку. У свободного её нет —</text>'
             % (ox, ink))
    o.append('<text x="%.0f" y="620" fill="%s">между кнопкой и диском зазор 2 мм. Диск сидит на валу Ø8.</text>'
             % (ox, ink))
    o.append('<text x="%.0f" y="646" fill="%s">Покой: P закрыт, пилот в R. Нажали — P в A, камера %.1f с.</text>'
             % (ox, ink, T_FILL))
    o.append('<text x="%.0f" y="666" fill="%s">Отпустили — выстрел. P и R смотрят внутрь кольца, A одно наружу.</text>'
             % (ox, ink))
    o.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o) + "\n")


if __name__ == "__main__":
    rings, built = report()
    ok = checks(rings, built)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "docs", "img", "valve_rotor.svg")
    hold = next(sc for rg, sc in built if rg["n"] == GUN_N and sc["name"] == "hold")
    ring = next(rg for rg in rings if rg["n"] == GUN_N)
    svg(out, ring, hold)
    print(out)
    sys.exit(0 if ok else 1)
