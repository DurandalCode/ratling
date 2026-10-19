# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse concept A: one barrel's cycle on the rotor, as an animated GIF (plain Python + Pillow).

The rotor's cam is unrolled flat under the barrel's two pushers (charge core on CHARGE_R above, vent core
on VENT_R below), its neighbours drawn faint. The cam is rotor_timing.height(), the pushers' stroke,
CLEAR and the return springs are rotor_timing's numbers; the rotor turns at the fastest rate the bench
charge time allows (rotor_timing.cams()["shot"] a pitch). Pressures are a sketch, not a model: the pilot
follows its open core in ~20 ms, the chamber fills through the bleed in T_FILL, the module's valve opens
when the pilot drops below 0.73 of the chamber (stage3v4) and the chamber empties in ~15 ms.

Run:  python3 mitrailleuse/rotor_cycle_gif.py [16|19]   -> exports/rotor_cycle/one_barrel_<n>.gif
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_rt = {"__name__": "rotor_timing"}
exec(open(os.path.join(HERE, "mitrailleuse", "rotor_timing.py"), encoding="utf-8").read(), _rt)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
K = _rt["cams"](N)
TOP_C, TOP_V = K["top_c"], _rt["VENT_TOP"]
TRAVEL, CLEAR, PIN_MAX = _rt["TRAVEL"], _rt["CLEAR"], _rt["PIN_MAX"]
OPENS = 0.4                     # mm of pin travel before a core passes air (sketch)
OPEN_RATIO = 1 - (16 / 31) ** 2  # stage3v4: valve opens when pilot < 0.73 of the chamber
X0, X1, DX = 3.2, -1.6, 0.02    # the port's x (pitches), start to end, a frame
T_PITCH = K["shot"]             # s a pitch
W, H = 1000, 640
INK, INK2, GRID, BG = (11, 11, 11), (82, 81, 78), (228, 227, 223), (252, 252, 251)
BLUE, ORANGE, GREEN, GREY, STEEL = (42, 120, 214), (235, 104, 52), (40, 150, 90), (200, 198, 192), (150, 160, 170)
PRINT = (226, 205, 140)


def font(sz, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(path, sz)


F, FB, FS, FT = font(15), font(15, True), font(12), font(20, True)


def pin(x, top):
    """Pin travel (mm) of the core under a pusher at x; the nose takes anything past PIN_MAX."""
    return min(PIN_MAX, max(0.0, _rt["height"](x, top) * TRAVEL - CLEAR))


def simulate():
    """Frames: (x, pilot, chamber, fired) with pressures as fractions of the supply."""
    out, pilot, cham, fired, firing = [], 0.0, 0.0, False, False
    steps = int(round((X0 - X1) / DX))
    sub = 20
    dt = T_PITCH * DX / sub
    for i in range(steps + 1):
        x = X0 - i * DX
        for _ in range(sub):
            xs = x + DX * _ / sub
            c_open = pin(xs, TOP_C) > OPENS
            v_open = pin(xs, TOP_V) > OPENS
            target = 1.0 if c_open else (0.0 if v_open else pilot)
            pilot += (target - pilot) * min(1.0, dt / 0.02)
            if not firing and cham > 0.3 and pilot < OPEN_RATIO * cham:
                firing = True
            if firing:
                cham += (0.0 - cham) * min(1.0, dt / 0.015)
                if cham < 0.02:
                    firing, fired = False, True
            else:
                cham += (pilot - cham) * min(1.0, dt / (_rt["T_FILL"] / 3.0)) if pilot > cham else 0.0
        out.append((x, pilot, cham, firing, fired))
    return out


def phase(x, fr):
    c, v = pin(x, TOP_C) > OPENS, pin(x, TOP_V) > OPENS
    if fr[3]:
        return "ВЫСТРЕЛ: пилот ниже 0.73 камеры, клапан модуля открылся", ORANGE
    if c:
        return "Зарядка: толкатель нажал ниппель зарядки, пилот и камера наполняются", BLUE
    if v:
        return "Сброс: толкатель нажал ниппель сброса, пилот стравливается", ORANGE
    if fr[4]:
        return "Выстрелил, пустой: оба ниппеля закрыты, пружины отвели толкатели", INK2
    if fr[2] > 0.3:
        return "Заряжен: оба ниппеля закрыты, ждёт короткую дугу", GREEN
    return "Ждёт: пустой, толкатели на упорах, кулачок их не касается", INK2


def draw_row(d, y, x, top, label, core_r, col):
    """One core circle unrolled: block, cores, pushers, return springs, cam; the port at screen centre."""
    cx, pp, mm = 300, 150.0, 12.0                 # port's screen x, px a pitch, px a mm (vertical)
    d.text((20, y - 30), label, font=FB, fill=INK)
    # block
    d.rectangle((20, y, 580, y + 70), fill=GREY, outline=INK2)
    y_face = y + 70                              # block's rear face; the cam is below it
    y_base = y_face + 34 + CLEAR * mm            # the cam's base
    for k in range(-2, 3):
        px = cx + k * pp
        xx = x + k
        if px < 30 or px > 570:
            continue
        p_mm = pin(xx, top)
        lift = min(TRAVEL, _rt["height"](xx, top) * TRAVEL)
        lift_pusher = max(0.0, lift - CLEAR)
        main = k == 0
        steel = STEEL if main else (205, 208, 212)
        printed = PRINT if main else (238, 230, 205)
        # core in its bore: body, seat (open = gap), pin down
        d.rectangle((px - 10, y + 8, px + 10, y + 40), fill=steel, outline=INK2)
        opened = p_mm > OPENS
        seat_col = (col if opened else INK2) if main else (180, 180, 180)
        d.rectangle((px - 12, y + 40, px + 12, y + 44), fill=seat_col)
        pin_top = y + 44
        d.rectangle((px - 2, pin_top, px + 2, y + 58 - p_mm * 4), fill=steel)
        # pusher: nose, stem through the block's face, head on the cam
        head_y = y_base - CLEAR * mm - lift_pusher * mm
        nose_top = y + 58 - p_mm * 4
        d.rectangle((px - 6, nose_top, px + 6, nose_top + 6), fill=printed, outline=INK2)
        d.rectangle((px - 3, nose_top + 6, px + 3, head_y - 8), fill=printed, outline=INK2)
        d.rounded_rectangle((px - 14, head_y - 8, px + 14, head_y), radius=4, fill=printed, outline=INK2)
        # return spring: zigzag between the block's face and the head
        sy0, sy1 = y_face, head_y - 8
        pts, nz = [], 8
        for z in range(nz + 1):
            pts.append((px + (9 if z % 2 else -9), sy0 + (sy1 - sy0) * z / nz))
        d.line(pts, fill=(INK2 if main else (190, 190, 190)), width=2)
    # cam, unrolled: x on screen -> port x
    pts = []
    for sx in range(20, 581, 2):
        xx = x + (sx - cx) / pp
        pts.append((sx, y_base - _rt["height"](xx, top) * TRAVEL * mm))
    poly = pts + [(580, y_base + 22), (20, y_base + 22)]
    d.polygon(poly, fill=(214, 188, 196), outline=INK2)
    d.text((24, y_base + 4), "ротор (развёртка по R%.0f), едет →" % core_r, font=FS, fill=INK2)
    p_mm = pin(x, top)
    d.text((cx + 20, y + 14), "шток утоплен %.1f мм" % p_mm, font=FS, fill=INK if p_mm > 0 else INK2)


def gauge(d, x0, y0, label, v, col):
    d.text((x0, y0), label, font=F, fill=INK)
    d.rectangle((x0, y0 + 22, x0 + 200, y0 + 40), outline=INK2, fill=BG)
    d.rectangle((x0, y0 + 22, x0 + 200 * max(0.0, min(1.0, v)), y0 + 40), fill=col)
    d.text((x0 + 208, y0 + 22), "%.1f бар" % (2.0 * v), font=F, fill=INK)


def frame(fr, frames, idx):
    x, pilot, cham, firing, fired = fr
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((20, 12), "Митральеза, %d стволов: цикл одного ствола" % N,
           font=FT, fill=INK)
    text, col = phase(x, fr)
    d.text((20, 44), text, font=FB, fill=col)
    draw_row(d, 110, x, TOP_C, "Ниппель зарядки (R60): длинная дуга, %d ствола вперёд" % _rt["AHEAD"], 60, BLUE)
    draw_row(d, 345, x, TOP_V, "Ниппель сброса (R42): короткая дуга", 42, ORANGE)
    # right: gauges and the module
    gx = 620
    gauge(d, gx, 100, "Пилот модуля", pilot, BLUE if pilot > 0.05 else GREY)
    gauge(d, gx, 160, "Камера 100 см³", cham, GREEN if not firing else ORANGE)
    d.text((gx, 220), "Клапан модуля:", font=F, fill=INK)
    d.text((gx + 130, 220), "ОТКРЫТ, выстрел" if firing else "закрыт", font=FB, fill=ORANGE if firing else INK2)
    if firing:
        d.polygon([(gx + 300, 250), (gx + 360, 236), (gx + 340, 262), (gx + 375, 280), (gx + 330, 278),
                   (gx + 320, 300), (gx + 305, 274)], fill=ORANGE)
    t = (X0 - x) * T_PITCH
    d.text((gx, 250), "время %.2f с" % t, font=F, fill=INK2)
    d.text((gx, 272), "1 шаг ротора = %.2f с (темп %.1f выстр/с)" % (T_PITCH, 1 / T_PITCH), font=FS, fill=INK2)
    # bottom right: pressure trace with a cursor
    px0, py0, pw, ph = 620, 330, 360, 150
    d.rectangle((px0, py0, px0 + pw, py0 + ph), outline=GRID)
    n = len(frames)
    for key, c in ((1, BLUE), (2, GREEN)):
        pts = [(px0 + pw * i / (n - 1), py0 + ph - ph * frames[i][key]) for i in range(n)]
        d.line(pts, fill=c, width=2)
    cxp = px0 + pw * idx / (n - 1)
    d.line((cxp, py0, cxp, py0 + ph), fill=INK, width=1)
    d.text((px0, py0 + ph + 6), "пилот", font=FS, fill=BLUE)
    d.text((px0 + 60, py0 + ph + 6), "камера", font=FS, fill=GREEN)
    d.text((px0 + pw - 230, py0 + ph + 6), "%.1f с всего, замедлено в 3 раза" % ((X0 - X1) * T_PITCH), font=FS, fill=INK2)
    d.text((620, 520), "Толкатели соседних стволов бледные.\nВозвратная пружина 5–7 Н уводит толкатель\n"
                       "на упор на скосе вниз, ниппель закрывается\nсам: своей пружиной и давлением.",
           font=FS, fill=INK2)
    return im


def main():
    frames = simulate()
    ims = [frame(fr, frames, i) for i, fr in enumerate(frames)]
    out = os.path.join(HERE, "exports", "rotor_cycle")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "one_barrel_%d.gif" % N)
    # real time slowed ~3x; hold the first and last frame
    ms = max(20, int(round(T_PITCH * DX * 1000 * 3 / 10.0)) * 10)
    dur = [ms] * len(ims)
    dur[0], dur[-1] = 1200, 1500
    for i, fr in enumerate(frames):                # the shot lasts ~15 ms: hold it so it can be seen
        if fr[3]:
            dur[i] = 80
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=dur, loop=0, optimize=True)
    print(path, len(ims), "frames,", ms, "ms each")


if __name__ == "__main__":
    main()
