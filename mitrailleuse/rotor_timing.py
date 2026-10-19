# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse concept A: the distributor's rotor, worked out on paper (plain Python, no FreeCAD).

The firing head is a face distributor (as the selector's Stage 1/2, selector/stage1_interface.py):

    stator ... a printed body (one push-in fitting per barrel on its front) with a flat wear plate on
               its rear face (3 mm PMMA or aluminium), N ports Ø PORT_D on R_PORT.
    rotor .... an arm on the rotor shaft; a spigot in the stator's centre, sealed by a radial O-ring,
               takes the supply into a channel along the arm to a floating shoe at R_PORT.
    shoe ..... a piston (Ø from BALANCE, radial O-ring in the arm) with a flat head on the wear plate.
               The head's face has an arc slot SLOT_W wide, ringed by a raised sealing band BAND wide;
               the rest of the head is relieved. Supply pressure behind the piston holds it on the plate,
               a light spring seals it at no pressure; the reaction goes into the shaft's bearings.

Everything outside the band is open air, so a port is in one of three states: under the slot (its pilot,
and through the bleed its chamber, charges), under the band (shut: PORT_D < BAND, so a port is never
open to the slot and the air at once), or outside (its pilot vents and the module fires). There is no
separate vent port: the band's trailing edge is the hammer. The slot spans AHEAD pitches, so AHEAD barrels
charge at once and each charges for ~AHEAD shot intervals: the rate is AHEAD / T_FILL shots/s.

A ratchet detent (N teeth on the rotor shaft, a spring plunger) parks the rotor with the band's edges
half-way between ports: then exactly AHEAD barrels are charged, none sits under the band, and the dump
valve (through the slot) reaches every charged one. The teeth only let it turn forward; let go between
teeth (trigger released mid-step), it snaps on to the next one, firing at most that one shot.

Run:  python3 mitrailleuse/rotor_timing.py      -> the numbers, and docs/img/rotor_timing.svg
mitrailleuse_concepts.py reads shoe() and the constants from here.
"""

import math
import os

R_PORT = 45.0               # port circle
PORT_D = 2.5                # = the 4/2.5 hose's bore
BAND = 3.0                  # sealing band round the slot; > PORT_D, so a port is never open both ways
SLOT_W = 3.0                # slot width (radial)
AHEAD = 2                   # barrels charging at once
BALANCE = 1.3               # piston area / the head's pressed area
SPRING_N = 8.0              # light spring behind the shoe
MU_SHOE = 0.15              # POM head on PMMA / aluminium, greased
SPIGOT = (10.0, 5.0)        # centre spigot Ø, its O-ring's drag N (radial, 8 x 1.5)
DETENT = (25.0, 10.0, 15.0)  # ratchet radius, plunger force N, ramp angle deg
GEAR = 5.0                  # crank turns per rotor turn
CRANK_R = 70.0
T_FILL = 0.5                # s, a chamber charged on the v1.1 bench (Ø1.0 bleed, 100 cm3, 2 bar)
P_WORK, P_DESIGN = 0.2, 0.5  # MPa gauge
PACKS = ((16, "16 стволов (кольца 4 + 12)"), (19, "19 стволов (соты)"))


def shoe(n, ahead=AHEAD):
    """The shoe for n barrels: slot, pressed area, piston, forces, drag and the rate."""
    pa = 2 * math.pi * R_PORT / n                     # pitch along the port circle
    S = ahead * pa - BAND                             # slot, end to end: the band's centre lines sit on
    A_slot = (S - SLOT_W) * SLOT_W + math.pi * SLOT_W ** 2 / 4        # the mid-points at the detent
    perim = 2 * (S - SLOT_W) + math.pi * SLOT_W
    A_sep = A_slot + perim * BAND / 2                 # pressure falls across the band
    A_p = BALANCE * A_sep
    D_p = math.sqrt(4 * A_p / math.pi)
    hold = {p: p * (A_p - A_sep) + SPRING_N for p in (P_WORK, P_DESIGN)}
    t_rotor = (MU_SHOE * hold[P_DESIGN] * R_PORT + SPIGOT[1] * SPIGOT[0] / 2
               + DETENT[1] * math.tan(math.radians(DETENT[2])) * DETENT[0]) / 1000      # N m
    t_crank = t_rotor / GEAR
    rp = PORT_D / 2
    charge = (ahead * pa - BAND + 2 * rp) / pa        # shot intervals a barrel spends under the slot
    dwell = BAND - PORT_D                             # mm of travel shut, between slot and air
    park = (pa - PORT_D - BAND) / 2                   # port edge to band edge at the detent
    shot = T_FILL / charge
    return dict(n=n, pa=pa, S=S, A_sep=A_sep, D_p=D_p, head=(S + 2 * BAND, SLOT_W + 2 * BAND),
                hold=hold, axial=P_DESIGN * A_p, t_rotor=t_rotor, t_crank=t_crank,
                f_crank=t_crank / CRANK_R * 1000, charge=charge, dwell=dwell, park=park, shot=shot,
                rate=1 / shot, volley=n * shot, per_turn=n / GEAR, crank_rate=1 / shot / (n / GEAR),
                ring=(perim + 2 * math.pi * BAND / 2) / math.pi)


def events(n, ahead=AHEAD, t_max=None):
    """(barrel, charge from, fires at) in shot intervals: barrel j fires j-th; t = 0 is a detent."""
    pa, rp, b = 2 * math.pi * R_PORT / n, PORT_D / 2, BAND
    out = []
    for j in range(-ahead, n + ahead):
        x0 = (j + 0.5) * pa                           # its port's place ahead of the trailing band edge
        t_in = (x0 - (ahead * pa - b / 2 + rp)) / pa
        t_fire = (x0 - (rp - b / 2)) / pa
        out.append((j, t_in, t_fire))
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
         '<text x="%d" y="26" font-size="16" fill="%s">Ротор митральезы: зарядка на %d ствола вперёд, '
         '%.0f оборотов ручки = залп</text>' % (left, ink, AHEAD, GEAR),
         '<rect x="%d" y="38" width="22" height="8" rx="2" fill="%s"/>' % (left, blue),
         '<text x="%d" y="46" fill="%s">заряжается (под пазом башмака)</text>' % (left + 28, ink2),
         '<circle cx="%d" cy="42" r="5" fill="%s" stroke="%s" stroke-width="2"/>' % (left + 260, orange, surf),
         '<text x="%d" y="46" fill="%s">выстрел (порт вышел из-под пояска)</text>' % (left + 272, ink2),
         '<line x1="%d" y1="36" x2="%d" y2="48" stroke="%s" stroke-width="1"/>' % (left + 520, left + 520, ink2),
         '<text x="%d" y="46" fill="%s">остановка фиксатора</text>' % (left + 528, ink2)]
    for n, title, y0 in panels:
        k = shoe(n)
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
        for j, t_in, t_fire in events(n, t_max=turns / step):
            for rep in range(-1, 3):                   # the next rotor turns: the same barrels again
                a, b = (t_in + rep * n) * step, (t_fire + rep * n) * step
                if b < 0 or a > turns:
                    continue
                row_i = j % n
                y = yb + row_i * row + row / 2
                xa, xb = sx(max(a, 0)), sx(min(b, turns))
                o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="6" rx="2" fill="%s"/>'
                         % (xa, y - 3, max(xb - xa - 2, 1), blue))
                if 0 <= b <= turns:
                    o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" stroke-width="2"/>'
                             % (sx(b), y, orange, surf))
    o.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def report():
    print("rotor: ports Ø%.1f on R%.0f, band %.1f, slot %.1f wide, %d ahead, gear %.0f:1, charge %.2f s (bench)"
          % (PORT_D, R_PORT, BAND, SLOT_W, AHEAD, GEAR, T_FILL))
    for n, _ in PACKS:
        k = shoe(n)
        print("  %d barrels: pitch %.1f mm, slot %.1f mm, head %.0f x %.0f,"
              " piston Ø%.1f" % (n, k["pa"], k["S"], k["head"][0], k["head"][1], k["D_p"]))
        print("     shoe held by %.0f N at 2 bar, %.0f N at 5 bar; %.0f N into the bearings at 5 bar"
              % (k["hold"][P_WORK], k["hold"][P_DESIGN], k["axial"]))
        print("     drag %.2f N m at the rotor, %.3f N m at the crank = %.1f N on the knob (R%.0f), before gear losses"
              % (k["t_rotor"], k["t_crank"], k["f_crank"], CRANK_R))
        print("     each barrel charges %.2f intervals; shut %.1f mm between slot and air; %.1f mm port to band at the"
              " detent" % (k["charge"], k["dwell"], k["park"]))
        print("     <= %.1f shots/s, volley %.1f s, %.1f shots a crank turn, crank <= %.2f turns/s"
              % (k["rate"], k["volley"], k["per_turn"], k["crank_rate"]))


if __name__ == "__main__":
    report()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg(os.path.join(here, "docs", "img", "rotor_timing.svg"))
    print("docs/img/rotor_timing.svg written")
