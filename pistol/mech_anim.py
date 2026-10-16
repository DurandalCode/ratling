# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: full-cycle animation of the lever-action layout.

Six shots, one from each barrel, the block one full turn. Each shot: lever
open (the pawl sector swings back, its tooth bent out of the notch, while
the detent holds the block), lever closed (the block turns 60 deg, the
detent clicks into the next notch), trigger pulled (lock on, fire) and let
go (vent shut, lock off).

Uses pistol/mech_layout.py's pose(). Writes exports/pistol_mech_cycle.gif:
the rear view (ratchet) left, the side view right, the phase below.

Run inside FreeCAD (GUI); it takes a few minutes:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/mech_anim.py').read())
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
exec(open(os.path.join(REPO, "pistol", "mech_layout.py")).read())

OUT = os.path.join(REPO, "exports", "pistol_mech_cycle.gif")
TMP = os.path.join(REPO, "exports", "_anim_tmp")
OPEN_F, CLOSE_F, PULL_F, HOLD_F, LET_F = 10, 14, 8, 3, 6
FRAME_MS = 80
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BACK_HIDE = ("Valve_body", "Valve_cap", "Valves", "Trigger", "Lever")


def frames_for_shot(k):
    b0 = 60.0 * k
    out = []
    for i in range(OPEN_F):                         # lever open: pawl back, block held
        u = i / (OPEN_F - 1)
        lv = 1 - u
        bend = ramp(u, 0.05, 0.15) * (1 - ramp(u, 0.85, 0.97))
        out.append((dict(lever=lv, block=b0, bend=bend, trig=0.0),
                    "рычаг вниз: собачка отогнута, идёт к следующему вырезу (фиксатор держит блок)"
                    if bend > 0.1 else "рычаг вниз"))
    for i in range(CLOSE_F):                        # lever closed: block turns
        lv = i / (CLOSE_F - 1)
        st = dict(lever=lv, block=b0 + block_drive(lv), bend=0.0, trig=0.0)
        out.append((st, "рычаг вверх: поворот блока %.0f°%s"
                    % (block_drive(lv), ", щелчок фиксатора" if lv > 0.95 else "")))
    for i in range(PULL_F):                         # trigger pulled
        tg = i / (PULL_F - 1)
        st = dict(lever=1.0, block=b0 + 60, bend=0.0, trig=tg)
        out.append((st, "ВЫСТРЕЛ: ствол %d" % (k + 1) if fire(tg) > 0.5 else
                    "спуск: запор прижат" if lock(tg) > 0.5 else "спуск"))
    out += [(dict(lever=1.0, block=b0 + 60, bend=0.0, trig=1.0), "ВЫСТРЕЛ: ствол %d" % (k + 1))] * HOLD_F
    for i in range(LET_F):                          # trigger let go
        tg = 1 - i / (LET_F - 1)
        out.append((dict(lever=1.0, block=b0 + 60, bend=0.0, trig=tg),
                    "спуск отпущен: сброс закрыт, запор отходит, камера заряжается"))
    return out


# ---------------------------------------------------------------- document and cameras
if "mech_cycle" in App.listDocuments():
    App.closeDocument("mech_cycle")
ad = App.newDocument("mech_cycle")


def addo(name, shape, col, tr=0):
    o = ad.addObject("Part::Feature", name)
    o.Shape = shape
    o.ViewObject.ShapeColor = col
    o.ViewObject.Transparency = tr
    return o


for n, s_, c, tr in (("Valve_body", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap", valve_cap, (0.45, 0.65, 0.85), 0),
                     ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 55), ("Axle", axle, (0.7, 0.7, 0.7), 40),
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


Gui.ActiveDocument = Gui.getDocument("mech_cycle")
view = Gui.ActiveDocument.activeView()
view.setCameraType("Orthographic")
pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
anim_old = pv.GetBool("UseNavigationAnimations", True)
pv.SetBool("UseNavigationAnimations", False)
os.makedirs(TMP, exist_ok=True)
font = ImageFont.truetype(FONT, 24)
images = []
try:
    put(dict(lever=0.0, block=0.0, bend=0.0, trig=0.0))
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
            dr.text((720, 10), "вид сбоку (рычаг, спуск)", fill=(80, 80, 80), font=font)
            dr.text((20, 725), "выстрел %d/6   |   %s" % (k + 1, text), fill=(0, 0, 0), font=font)
            images.append(im.quantize(colors=96))
    images[0].save(OUT, save_all=True, append_images=images[1:], duration=FRAME_MS, loop=0)
finally:
    pv.SetBool("UseNavigationAnimations", anim_old)
print(OUT, len(images), "frames")
