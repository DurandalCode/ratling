# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse concept A: the firing head's rotor, worked out on paper (plain Python, no FreeCAD).

Valve cores only (tyre valve cores, 5V1, as in stage4v2_schrader.py): each barrel's pilot line meets two
cores in the fixed head, both pressed through printed buttons from behind.

    charge core (CHARGE_R) .. supply ring on its inner (tyre) side, the pilot line on its pin side, under
                              the button, which seals on an O-ring. Pressed: the pilot (and through the
                              bleed the chamber) charges. Let go: the supply holds it shut.
    vent core (VENT_R) ...... the pilot line on its inner side, open air at the pin. Pressed: the pilot
                              vents and the module fires. Let go: the pilot holds it shut.

Every pusher has its own return spring: a pusher is a sprung nose, a stem in a guide bore behind the
core and a domed head that rides the rotor's face, with a coil spring between the block and the head. The
rotor is a plain face cam: a raised arc with a ramp up and a ramp down. The ramp up pushes the pusher in;
on the ramp down the return spring (preload well over the charge pusher's O-ring drag) takes it back onto
its stop, so a button is never left down. Once the pusher is off the pin the core shuts by its own spring
and, as soon as there is pressure on its inner side, by the pressure. Parked off the arcs the head stands
CLEAR off the cam's base on its stop, so the springs do not drag on the rotor. The pusher's nose is sprung
inside its stem (preload over the core's force), so the cam's stroke can be generous for the cores'
scatter without crushing a core that bottoms early. (A desmodromic T-slot track that pulled the pushers
back was drawn first; a spring is simpler, the core closes itself anyway.)

The rotor is a cam disc behind the head with two raised arcs: a long one on CHARGE_R that holds AHEAD
charge buttons down, and a short one on VENT_R just behind it. A barrel's port meets them in turn, in
shot intervals: its charge button is held for ~AHEAD intervals, let go, both cores shut for a moment,
then its vent button is pressed and it fires. Nothing but the AHEAD barrels under the long rail is ever
charged. The rails' edges sit between ports when the rotor is parked (a ratchet detent), so no button is
left on a ramp, and it turns forward only.

A charge core is a check valve the other way: if the supply is vented (the dump valve, through a small
jet), the charged pilots and chambers flow back through their charge cores into the ring and out
through the jet, slowly, without firing: the rotor's position does not matter.

Cam profiles are in pitches along the core circles: x is how far a port is ahead of the point half-way
between the two rails (CHARGE_TOP and VENT_TOP are the rails' flat tops in x); the rotor turns so that x
falls, and at the detent the ports sit at x = j + 0.5.

Core numbers are typical, not measured (as in stage4v2_schrader.py): check them on the cores.
Run:  python3 mitrailleuse/rotor_timing.py      -> the numbers, and docs/img/rotor_timing.svg
mitrailleuse_concepts.py reads the constants and cams() from here.
"""

import math
import os

VENT_R, CHARGE_R = 42.0, 60.0   # core circles; vent inside, charge outside (the supply ring is there)
CORE_CB = 6.6                   # core counterbore Ø (stage4v2), the button's collar fits it
BUTTON_D = 9.0                  # pusher's guide boss / the charge pusher's O-ring land
HEAD_D, STEM_D = 7.0, 3.0       # pusher's domed head on the cam, its stem in the guide bore
CLEAR = 0.2                     # head off the cam's base with the pusher on its stop
RETURN = (5.0, 1.0)             # return spring: preload N on the stop, rate N/mm
AHEAD = 2                       # barrels charging at once
CHARGE_TOP = (0.35, AHEAD - 0.35)  # x range where the cam holds a charge pusher fully in
VENT_TOP = (-0.65, -0.35)           # and a vent pusher
RAMP = 0.25                     # pitches of ramp at each end
TRAVEL = 2.0                    # the cam's rise
PIN_OPEN, PIN_MAX = 1.2, 1.8    # core pin: pressed this far it is fully open; this far it bottoms (typical)
TOL = 0.4                       # +- in the chain rotor - pusher - core seat (print, core seating)
NOSE = (12.0, 10.0, 1.0)        # sprung nose: preload N (> the core's force), rate N/mm, free stroke mm
CORE_SPRING = 3.0               # N, a core's spring (typical)
CORE_SEAL_D = 3.4               # its seat bore: pressure on it adds to the button force
BUTTON_ORING_N = 2.0            # drag of the charge button's O-ring
MU_RAIL = 0.2                   # printed rail on a printed button dome, greased
DETENT = (25.0, 10.0, 15.0)     # ratchet radius, plunger force N, ramp angle deg
GEAR = 5.0                      # crank turns per rotor turn
CRANK_R = 70.0
T_FILL = 0.5                    # s, a chamber charged on the v1.1 bench (Ø1.0 bleed, 100 cm3, 2 bar)
P_DESIGN = 0.5                  # MPa gauge
PACKS = ((16, "16 стволов (кольца 4 + 12)"), (19, "19 стволов (соты)"))


def height(x, top):
    """Rail height (0..1 of TRAVEL) under a port at x pitches; ramps of RAMP outside top."""
    a, b = top
    if a <= x <= b:
        return 1.0
    if a - RAMP < x < a:
        return (x - (a - RAMP)) / RAMP
    if b < x < b + RAMP:
        return ((b + RAMP) - x) / RAMP
    return 0.0


def cams(n, ahead=AHEAD):
    """The rotor for n barrels: pitches, rail lengths, ramp angles, timing, torque, rate."""
    top_c = (CHARGE_TOP[0], ahead - CHARGE_TOP[0])
    pc, pv = 2 * math.pi * CHARGE_R / n, 2 * math.pi * VENT_R / n     # pitch along each circle, mm
    f_core = CORE_SPRING + P_DESIGN * math.pi * CORE_SEAL_D ** 2 / 4
    short = TRAVEL - CLEAR - TOL                            # the least the pin is pressed
    over = max(0.0, TRAVEL - CLEAR + TOL - PIN_MAX)         # the most the nose has to give
    f_ret = RETURN[0] + RETURN[1] * (TRAVEL - CLEAR)        # return spring, pusher fully in
    f_top = max(f_core, NOSE[0] + NOSE[1] * over) if over else f_core
    # torque over one pitch of turning: buttons climbing the ramps, and rail friction on those held down
    worst, steps = 0.0, 200
    for s in range(steps + 1):
        t = s / steps
        tq = DETENT[1] * math.tan(math.radians(DETENT[2])) * DETENT[0]
        for j in range(-3, ahead + 3):
            x = j + 0.5 - t
            for top, r, p, extra in ((top_c, CHARGE_R, pc, BUTTON_ORING_N), (VENT_TOP, VENT_R, pv, 0.0)):
                h = height(x, top)
                slope = (height(x + 1e-3, top) - height(x - 1e-3, top)) / 2e-3 * TRAVEL / p   # dh/ds
                if h <= 0.0:
                    continue                                # on its stop, off the cam
                f = f_core * h + f_ret * h + extra
                # up a ramp: the cam pushes core, return spring and O-ring; down: the spring pushes the rotor
                # on (taken as nothing); friction under every head on the cam
                tq += r * (f * max(slope, 0.0) + MU_RAIL * (f_top * h + f_ret * h + extra))
        worst = max(worst, tq)
    charge = (top_c[1] - top_c[0]) + RAMP                   # intervals: top plus half of each ramp
    shut = (top_c[0] - RAMP) - (VENT_TOP[1] + RAMP)          # pitches with both cores shut
    shot = T_FILL / charge
    parked = [j + 0.5 for j in range(-3, ahead + 3)]
    on_ramp = any(0.0 < height(x, tp) < 1.0 for x in parked for tp in (top_c, VENT_TOP))
    return dict(n=n, pc=pc, pv=pv, rail_c=(top_c[1] - top_c[0] + 2 * RAMP) * pc, rail_v=(VENT_TOP[1] - VENT_TOP[0]
                + 2 * RAMP) * pv, ramp_c=math.degrees(math.atan(TRAVEL / (RAMP * pc))),
                ramp_v=math.degrees(math.atan(TRAVEL / (RAMP * pv))), clear_v=pv - BUTTON_D,
                clear_c=pc - BUTTON_D, charge=charge, shut=shut, shut_mm=shut * pv, on_ramp=on_ramp,
                f_core=f_core, f_top=f_top, f_ret=f_ret, short=short, over=over, t_rotor=worst / 1000, f_crank=worst / 1000 / GEAR / CRANK_R * 1000,
                shot=shot, rate=1 / shot, volley=n * shot, per_turn=n / GEAR, crank_rate=1 / shot / (n / GEAR),
                top_c=top_c)


def events(n, ahead=AHEAD):
    """(barrel, charge from, charge to, fires at) in shot intervals: barrel j fires j-th; t = 0 a detent.

    A port at x = j + 0.5 - t; charged while the charge button is past half its ramp, fires when the
    vent button is half way down its ramp.
    """
    k = cams(n, ahead)
    a, b = k["top_c"]
    out = []
    for j in range(-ahead, n + ahead):
        x0 = j + 0.5
        out.append((j, x0 - (b + RAMP / 2), x0 - (a - RAMP / 2), x0 - (VENT_TOP[1] + RAMP / 2)))
    return out


def svg(path):
    """Timing diagram: a row per barrel, charging bars and shots against crank turns, both packs."""
    W, left, right, row, top, gap = 980, 150, 30, 15, 70, 70
    turns = 6.0
    panels, h = [], top
    for n, title in PACKS:
        panels.append((n, title, h))
        h += 30 + n * row + gap
    H = h
    blue, orange, ink, ink2, grid, surf = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    sx = lambda t: left + (W - left - right) * t / turns
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="Helvetica, Arial, sans-serif" font-size="12">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % surf,
         '<text x="%d" y="26" font-size="16" fill="%s">Ротор на ниппелях: зарядка на %d ствола вперёд, '
         '%.0f оборотов ручки = залп</text>' % (left, ink, AHEAD, GEAR),
         '<rect x="%d" y="38" width="22" height="8" rx="2" fill="%s"/>' % (left, blue),
         '<text x="%d" y="46" fill="%s">заряжается (зарядный ниппель нажат)</text>' % (left + 28, ink2),
         '<circle cx="%d" cy="42" r="5" fill="%s" stroke="%s" stroke-width="2"/>' % (left + 290, orange, surf),
         '<text x="%d" y="46" fill="%s">выстрел (нажат ниппель сброса)</text>' % (left + 302, ink2),
         '<line x1="%d" y1="36" x2="%d" y2="48" stroke="%s" stroke-width="1"/>' % (left + 530, left + 530, ink2),
         '<text x="%d" y="46" fill="%s">остановка храповика</text>' % (left + 538, ink2)]
    for n, title, y0 in panels:
        k = cams(n)
        step = GEAR / n                              # crank turns per shot interval
        o.append('<text x="%d" y="%d" font-size="14" fill="%s">%s: %.1f выстрела за оборот ручки; '
                 'каждый ствол заряжается %.2f интервала</text>' % (left, y0 + 18, ink, title, n / GEAR, k["charge"]))
        yb = y0 + 30
        for i in range(int(turns / step) + 1):
            x = sx(i * step)
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>'
                     % (x, yb, x, yb + n * row, grid))
        for t in range(int(turns) + 1):
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>'
                     % (sx(t), yb + n * row, sx(t), yb + n * row + 5, ink2))
            o.append('<text x="%.1f" y="%d" text-anchor="middle" fill="%s">%d</text>'
                     % (sx(t), yb + n * row + 18, ink2, t))
        o.append('<text x="%d" y="%d" text-anchor="end" fill="%s">обороты ручки</text>'
                 % (W - right, yb + n * row + 34, ink2))
        for j in range(n):
            y = yb + j * row + row / 2
            o.append('<text x="%d" y="%.1f" text-anchor="end" fill="%s">ствол %d</text>' % (left - 8, y + 4, ink2, j + 1))
        for j, t_in, t_out, t_fire in events(n):
            for rep in range(-1, 3):                   # the next rotor turns: the same barrels again
                a, b, f = ((t + rep * n) * step for t in (t_in, t_out, t_fire))
                if f < 0 or a > turns:
                    continue
                y = yb + (j % n) * row + row / 2
                xa, xb = sx(max(a, 0)), sx(min(b, turns))
                if xb > xa:
                    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="6" rx="2" fill="%s"/>'
                             % (xa, y - 3, max(xb - xa, 1), blue))
                if 0 <= f <= turns:
                    o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" stroke-width="2"/>'
                             % (sx(f), y, orange, surf))
    o.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


CORE_PRICE = (0.9, 1.8)         # rub a core, in 100-packs (Ozon, 2026-10: 88-177 rub / 100)
PUSHER_PARTS = (("пружина носика", 3.0), ("возвратная пружина", 3.0), ("кольцо толкателя зарядки", 2.0))
                                # rub each, typical
SPARES = 1.0                    # a full spare set per gun


def economics(n):
    """Cores and the bits round them for n barrels: count, money, actuations."""
    cores = 2 * n
    bought = math.ceil(cores * (1 + SPARES) / 100.0) * 100
    rub = [bought * c for c in CORE_PRICE]
    extra = n * 2 * (PUSHER_PARTS[0][1] + PUSHER_PARTS[1][1]) + n * PUSHER_PARTS[2][1]
    return dict(cores=cores, bought=bought, rub=rub, extra=extra, per_volley=cores)


def report():
    print("rotor: vent cores on R%.0f, charge cores on R%.0f, %d ahead, gear %.0f:1, charge %.2f s (bench)"
          % (VENT_R, CHARGE_R, AHEAD, GEAR, T_FILL))
    for n, _ in PACKS:
        k = cams(n)
        print("  %d barrels: pitch %.1f (vent) / %.1f (charge) mm, %.1f / %.1f mm between buttons Ø%.0f"
              % (n, k["pv"], k["pc"], k["clear_v"], k["clear_c"], BUTTON_D))
        print("     rails: charge %.1f mm, vent %.1f mm; ramps %.0f / %.0f deg for a %.1f mm stroke"
              % (k["rail_c"], k["rail_v"], k["ramp_c"], k["ramp_v"], TRAVEL))
        print("     each barrel charges %.2f intervals; both cores shut %.2f pitch (%.1f mm at the vent rail);"
              " parked on a ramp: %s" % (k["charge"], k["shut"], k["shut_mm"], k["on_ramp"]))
        print("     pushers: pin pressed %.1f-%.1f mm (opens fully at %.1f, bottoms at %.1f); nose gives <= %.1f mm,"
              " <= %.0f N on a core" % (k["short"], TRAVEL - CLEAR + TOL, PIN_OPEN, PIN_MAX, k["over"], k["f_top"]))
        print("     return spring %.0f-%.0f N (O-ring drag %.0f N)" % (RETURN[0], k["f_ret"], BUTTON_ORING_N))
        print("     button %.1f N at 5 bar; rotor torque <= %.2f N m, %.1f N on the crank knob (R%.0f), before gear"
              " losses" % (k["f_core"], k["t_rotor"], k["f_crank"], CRANK_R))
        print("     <= %.1f shots/s, volley %.1f s, %.1f shots a crank turn, crank <= %.2f turns/s"
              % (k["rate"], k["volley"], k["per_turn"], k["crank_rate"]))
        e = economics(n)
        print("     cores: %d in the gun, buy %d (%.0f-%.0f rub); springs and O-rings ~%.0f rub; each core works once"
              " a volley" % (e["cores"], e["bought"], e["rub"][0], e["rub"][1], e["extra"]))


if __name__ == "__main__":
    report()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg(os.path.join(here, "docs", "img", "rotor_timing.svg"))
    print("docs/img/rotor_timing.svg written")
