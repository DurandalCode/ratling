# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: full-cycle animation of the hammer layout.

Six shots, one from each barrel, the block one full turn. Each shot: the
thumb pulls the hammer back (lock off, then the block turns 60 deg), lets
it go (the pawl skips back, the lock closes), the trigger vents the pilot
(the shot) and is let go.

Uses pistol/hammer_layout.py's pose(). Writes exports/pistol_hammer_cycle.gif:
the rear view (ratchet) left, the side view right, the phase below.

Run inside FreeCAD (GUI); it takes a few minutes:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/hammer_anim.py').read())
"""

import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PIL import Image, ImageDraw, ImageFont

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "pistol", "hammer_layout.py")).read())

OUT = os.path.join(REPO, "exports", "pistol_hammer_cycle.gif")
TMP = os.path.join(REPO, "exports", "_anim_tmp")
COCK_F, BACK_F, FALL_F, PULL_F, HOLD_F, LET_F = 14, 2, 6, 6, 3, 6
FRAME_MS = 80
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BACK_HIDE = ("Valve_body", "Valve_cap", "Valves", "Trigger", "Hammer")


def frames_for_shot(k):
    b0 = 60.0 * k
    out = []
    for i in range(COCK_F):                         # thumb pulls the hammer back
        c = i / (COCK_F - 1)
        if lock_h(c) > 0.0:
            text = "курок назад: запор отходит"
        elif block_drive(c) <= 0.0:
            text = "курок назад: запор открыт, собачка ещё не взялась"
        else:
            text = "курок назад: поворот блока %.0f°%s" % (block_drive(c), ", щелчок фиксатора" if c > 0.97 else "")
        out.append((dict(cock=c, block=b0 + block_drive(c), bend=0.0, trig=0.0), text))
    b1 = b0 + 60
    out += [(dict(cock=1.0, block=b1, bend=0.0, trig=0.0), "палец отпускает курок")] * BACK_F
    for i in range(FALL_F):                         # the spring brings it forward: pawl skips back, lock shuts
        u = (i + 1) / FALL_F
        bend = ramp(u, 0.0, 0.15) * (1 - ramp(u, 0.8, 0.95))
        out.append((dict(cock=1 - u, block=b1, bend=bend, trig=0.0),
                    "курок возвращается: запор закрывается" if lock_h(1 - u) > 0 else
                    "курок возвращается: собачка идёт к следующему вырезу"))
    for i in range(PULL_F):
        tg = (i + 1) / PULL_F
        out.append((dict(cock=0.0, block=b1, bend=0.0, trig=tg), "ВЫСТРЕЛ: ствол %d" % (k + 1) if fire(tg) > 0.5 else "спуск"))
    out += [(dict(cock=0.0, block=b1, bend=0.0, trig=1.0), "ВЫСТРЕЛ: ствол %d" % (k + 1))] * HOLD_F
    for i in range(LET_F):
        out.append((dict(cock=0.0, block=b1, bend=0.0, trig=1 - (i + 1) / LET_F), "спуск отпущен: сброс закрыт, камера заряжается"))
    return out


# ---------------------------------------------------------------- document and cameras
if "hammer_cycle" in App.listDocuments():
    App.closeDocument("hammer_cycle")
ad = App.newDocument("hammer_cycle")


def addo(name, shape, col, tr=0):
    o = ad.addObject("Part::Feature", name)
    o.Shape = shape
    o.ViewObject.ShapeColor = col
    o.ViewObject.Transparency = tr
    return o


for n, s_, c, tr in (("Valve_body", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap", valve_cap, (0.45, 0.65, 0.85), 0),
                     ("Lock_housing", lock_housing_h, (0.5, 0.7, 0.5), 55), ("Axle", axle, (0.7, 0.7, 0.7), 40),
                     ("Valves", valves, (0.3, 0.3, 0.8), 30)):
    addo(n, s_, c, tr)
mv = {n: addo(n, Part.Shape(), *STYLE[n]) for n in STYLE}


def show(names, on):
    for o in ad.Objects:
        if o.Name in names:
            o.ViewObject.Visibility = on


def put(st):
    for n, s_ in pose(st).items():
        mv[n].Shape = s_
    ad.recompute()


Gui.ActiveDocument = Gui.getDocument("hammer_cycle")
view = Gui.ActiveDocument.activeView()
view.setCameraType("Orthographic")
pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
anim_old = pv.GetBool("UseNavigationAnimations", True)
pv.SetBool("UseNavigationAnimations", False)
os.makedirs(TMP, exist_ok=True)
font = ImageFont.truetype(FONT, 24)
images = []
try:
    put(dict(cock=1.0, block=0.0, bend=0.0, trig=0.0))
    show(BACK_HIDE, False)
    view.viewLeft(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_back = view.getCamera()
    show(BACK_HIDE, True)
    view.viewRear(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_side = view.getCamera()
    for k in range(6):
        for st, text in frames_for_shot(k):
            put(st)
            show(BACK_HIDE, False); view.setCamera(cam_back); Gui.updateGui()
            view.saveImage(os.path.join(TMP, "b.png"), 700, 700, "White")
            show(BACK_HIDE, True); view.setCamera(cam_side); Gui.updateGui()
            view.saveImage(os.path.join(TMP, "s.png"), 900, 700, "White")
            im = Image.new("RGB", (1600, 780), "white")
            im.paste(Image.open(os.path.join(TMP, "b.png")).convert("RGB"), (0, 0))
            im.paste(Image.open(os.path.join(TMP, "s.png")).convert("RGB"), (700, 0))
            dr = ImageDraw.Draw(im)
            dr.text((20, 10), "вид сзади (храповик)", fill=(80, 80, 80), font=font)
            dr.text((720, 10), "вид сбоку (курок, спуск)", fill=(80, 80, 80), font=font)
            dr.text((20, 725), "выстрел %d/6   |   %s" % (k + 1, text), fill=(0, 0, 0), font=font)
            images.append(im.quantize(colors=96))
    images[0].save(OUT, save_all=True, append_images=images[1:], duration=FRAME_MS, loop=0)
finally:
    pv.SetBool("UseNavigationAnimations", anim_old)
print(OUT, len(images), "frames")
