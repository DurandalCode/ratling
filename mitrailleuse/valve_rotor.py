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

One valve per barrel. The button faces the rotor. The body is turned so the port column
faces outward: 16 mm tangential, 31.8 mm radial (the drawing's port face is the 16 mm one;
the other way round is computed too, in case the column is on the wide face). A face cam
presses a small pusher into the button and lets go. Pressed, supply feeds the pilot and the
chamber fills through the module's Ø1.0 bleed. Released, the pilot vents and the module
fires. At rest the pilot is open to exhaust, so a barrel is under pressure only while its
button is down.

Two cams, same ring:

  hold   the lobe keeps ~1.5 valves switched (two charging, as the nipple rotor did).
         A barrel is pressed for the fill time, ~0.5 s, then released and fires. The lobe
         is longer than the pitch, so a parked rotor still holds a button down. The trigger
         therefore owns a master valve: held, supply is on; released, the manifold vents
         through a Ø0.5 jet and those chambers drain back without firing (the nipple head's
         quiet dump, still to be repeated on this valve).
  gap    the lobe is shorter than the pitch, so the rotor can park with every button up
         and the supply can stay connected. The fill still takes ~0.5 s, and the ramps eat
         most of the pitch, so the volley is slow. Printed so the trade is visible.

Run:  python3 mitrailleuse/valve_rotor.py
Writes docs/img/valve_rotor.svg. rotor_timing.py remains the nipple rotor's numbers.
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

# Ring. Ports face out, so the 16 mm thickness is tangential and 31.8 is radial.
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
    print("rings, ports outward, %.1f mm between inner corners:" % WALL)
    rings = []
    for n in PACKS:
        rg = ring(n, TANGENTIAL, RADIAL, WALL)
        rings.append(rg)
        report_ring(rg, "pocket")
    print("same ring with an M5 wall of %.0f mm (the drawing's Ø%.1f holes):" % (SCREW_WALL, MOUNT_D))
    for n in PACKS:
        report_ring(ring(n, TANGENTIAL, RADIAL, SCREW_WALL), "screwed")
    print("if the port column is on the wide face instead, pocket wall %.0f mm, 31.8 tangential:" % WALL)
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
    print("spares out of %d, one master valve on the trigger (hold scheme):" % BOUGHT)
    for n in (16, 19):
        print("  %d barrels: %d valves + 1 master, %d spare" % (n, n, BOUGHT - n - 1))
    print("  20 on the ring and no master: the supply stays on, only the gap cam parks empty")
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
    """Top view of the 20-valve ring and a side of one valve under the cam."""
    W, H = 980, 640
    ink, ink2, grid, surf = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    blue, orange, body, plate = "#2a78d6", "#eb6834", "#d9d6cf", "#c8c4ba"
    cx, cy, sc = 330.0, 330.0, 2.55
    lobe = sc_hold["lobe"]

    def X(x, y):
        return cx + sc * x, cy - sc * y

    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="Helvetica, Arial, sans-serif" font-size="13">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % surf,
         '<text x="28" y="32" font-size="18" fill="%s">Ротор на 20 клапанах</text>' % ink,
         '<text x="28" y="52" fill="%s">кнопки на R %.0f, корпуса внутри плиты R %.0f, '
         'полоса переключения %.1f шага — на остановке нажаты два</text>'
         % (ink2, rg["R"], HEAD_PLATE_R, HOLD_PITCHES)]

    def circle(r, color, width, dash=None):
        extra = "" if dash is None else ' stroke-dasharray="%s"' % dash
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%s"%s/>'
                 % (cx, cy, sc * r, color, width, extra))

    circle(HEAD_PLATE_R, plate, 1.5, "4 3")
    circle(rg["R"], blue, 1.2)
    # the lobe, along the button circle, sitting at the top (angle 90 deg, x up in the math frame)
    # cam coordinate x=0 is the trailing edge of the plateau. Draw from -lr to lp+lr.
    def arc(x0, x1, color, width):
        pts = []
        for i in range(48):
            x = x0 + (x1 - x0) * i / 47.0
            ang = math.pi / 2.0 - x / rg["R"]
            pts.append("%.1f,%.1f" % (cx + sc * rg["R"] * math.cos(ang), cy - sc * rg["R"] * math.sin(ang)))
        o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" '
                 'stroke-linecap="round"/>' % (" ".join(pts), color, width))

    arc(-lobe["lr"], 0.0, orange, 6)          # release: the barrel fires
    arc(0.0, lobe["lp"], blue, 6)             # plateau: charging
    arc(lobe["lp"], lobe["lp"] + lobe["lr"], ink2, 4)

    step = 2.0 * math.pi / rg["n"]
    for j in range(rg["n"]):
        ang = math.pi / 2.0 - j * step
        poly = spin(rect(rg["R"], rg["tangential"], rg["radial"]), ang)
        # a valve is "down" when its cam coordinate (0 at the top, falling clockwise) is on the plateau
        x = j * rg["pitch"]
        down = 0.0 <= x <= lobe["lp"] or 0.0 <= x - rg["n"] * rg["pitch"] <= lobe["lp"]
        fill = "#c5d9f2" if down else body
        pts = " ".join("%.1f,%.1f" % X(px, py) for px, py in poly)
        o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (pts, fill, ink2))
        bx, by = X(rg["R"] * math.cos(ang), rg["R"] * math.sin(ang))
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (bx, by, sc * 1.6, orange if down else ink2))

    # callouts
    o.append('<text x="28" y="600" fill="%s">Пунктир — нынешняя плита головки R %.0f. '
             'Синие корпуса кулачок держит нажатыми, оранжевая точка — кнопка.</text>'
             % (ink2, HEAD_PLATE_R))
    o.append('<text x="28" y="620" fill="%s">Сход с синей дуги (оранжевый скос) — выстрел. '
             'В покое гашетка стравливает подачу: нажатый клапан не остаётся под давлением.</text>' % ink2)

    # side view
    x0, y0 = 690, 150
    o.append('<text x="%d" y="%d" font-size="15" fill="%s">Один клапан, сбоку</text>' % (x0, y0 - 28, ink))
    # body
    bw, bh = 78, 120
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s"/>' % (x0, y0, bw, bh, body, ink))
    o.append('<text x="%d" y="%d" fill="%s">Rc1/8</text>' % (x0 + 8, y0 + 28, ink2))
    for i, lab in enumerate(("1 P", "2 A", "3 R")):
        yy = y0 + 48 + i * 22
        o.append('<circle cx="%d" cy="%d" r="7" fill="none" stroke="%s"/>' % (x0 + bw - 16, yy, ink))
        o.append('<text x="%d" y="%d" fill="%s">%s</text>' % (x0 + 8, yy + 4, ink2, lab))
    # button
    o.append('<rect x="%d" y="%d" width="28" height="16" fill="%s" stroke="%s"/>' % (x0 + 25, y0 - 16, orange, ink))
    o.append('<text x="%d" y="%d" fill="%s">кнопка, ход %.1f</text>' % (x0 + 58, y0 - 4, ink2, STROKE))
    # pusher and cam to the left of the button (the rotor is behind, -z; drawn to the left)
    o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3"/>' % (x0 - 36, y0 - 8, x0 + 25, y0 - 8, ink))
    o.append('<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (x0 - 36, y0 - 8, ink))
    o.append('<path d="M %d %d l 18 -14 l 36 0 l 18 14" fill="none" stroke="%s" stroke-width="3"/>'
             % (x0 - 108, y0 - 4, blue))
    o.append('<text x="%d" y="%d" fill="%s">кулачок %.1f мм</text>' % (x0 - 108, y0 + 18, ink2, PRESS))
    o.append('<text x="%d" y="%d" fill="%s">толкатель</text>' % (x0 - 70, y0 - 16, ink2))
    o.append('<text x="%d" y="%d" fill="%s">Покой: P закрыт, A–R.</text>' % (x0, y0 + bh + 28, ink))
    o.append('<text x="%d" y="%d" fill="%s">Нажат: P–A, камера</text>' % (x0, y0 + bh + 46, ink))
    o.append('<text x="%d" y="%d" fill="%s">набирает %.1f с.</text>' % (x0, y0 + bh + 64, ink, T_FILL))
    o.append('<text x="%d" y="%d" fill="%s">Отпущен — выстрел.</text>' % (x0, y0 + bh + 82, ink))
    o.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o) + "\n")


if __name__ == "__main__":
    rings, built = report()
    ok = checks(rings, built)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "docs", "img", "valve_rotor.svg")
    hold20 = next(sc for rg, sc in built if rg["n"] == 20 and sc["name"] == "hold")
    ring20 = next(rg for rg in rings if rg["n"] == 20)
    svg(out, ring20, hold20)
    print(out)
    sys.exit(0 if ok else 1)
