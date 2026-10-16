# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: full-cycle animation of the dressed assembly.

Six shots, the block one full turn, as pistol/mech_anim.py, but with the
Skaven frame, grip and lever: the whole pistol from the side on the left,
the ratchet from behind on the right (frame and grip hidden there).

Writes exports/pistol_assembly_cycle.gif. Run inside FreeCAD (GUI); a few
minutes:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/assembly_anim.py').read())
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
exec(open(os.path.join(REPO, "pistol", "pistol_assembly.py")).read())

OUT = os.path.join(REPO, "exports", "pistol_assembly_cycle.gif")
TMP = os.path.join(REPO, "exports", "_anim_tmp")
OPEN_F, CLOSE_F, PULL_F, HOLD_F, LET_F = 8, 12, 6, 2, 5
FRAME_MS = 85
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
ON_BLOCK = ("Straps", "Strap_rivets", "Spikes")         # dress that turns with the block


def frames_for_shot(k):
    b0 = 60.0 * k
    out = []
    for i in range(OPEN_F):
        u = i / (OPEN_F - 1)
        bend = ramp(u, 0.05, 0.15) * (1 - ramp(u, 0.85, 0.97))
        out.append((dict(lever=1 - u, block=b0, bend=bend, trig=0.0),
                    "рычаг вниз: собачка идёт к следующему вырезу, фиксатор держит блок"))
    for i in range(CLOSE_F):
        lv = i / (CLOSE_F - 1)
        out.append((dict(lever=lv, block=b0 + block_drive(lv), bend=0.0, trig=0.0),
                    "рычаг вверх: поворот блока %.0f°%s" % (block_drive(lv), ", щелчок" if lv > 0.95 else "")))
    for i in range(PULL_F):
        tg = i / (PULL_F - 1)
        out.append((dict(lever=1.0, block=b0 + 60, bend=0.0, trig=tg),
                    "ВЫСТРЕЛ: ствол %d" % (k + 1) if fire(tg) > 0.5 else "спуск: запор прижат" if lock(tg) > 0.5 else "спуск"))
    out += [(dict(lever=1.0, block=b0 + 60, bend=0.0, trig=1.0), "ВЫСТРЕЛ: ствол %d" % (k + 1))] * HOLD_F
    for i in range(LET_F):
        out.append((dict(lever=1.0, block=b0 + 60, bend=0.0, trig=1 - i / (LET_F - 1)),
                    "спуск отпущен: запор отходит, камера заряжается"))
    return out


doc = App.getDocument(NAME)
base = {n: doc.getObject(n).Shape.copy() for n in ON_BLOCK}
mv = {n: doc.getObject(n) for n in STYLE}
REAR_SHOW = {"Block", "Sector", "Pawl", "Slider", "Pin", "Bolt", "Sleeve", "Lock_housing", "Chamber_axle",
             "Detent_housing"}


def put(st):
    for n, s_ in pose(st).items():
        mv[n].Shape = s_
    for n in ON_BLOCK:
        doc.getObject(n).Shape = turned(base[n], st["block"])
    doc.recompute()


def rear_mode(on):
    for o in doc.Objects:
        if o.TypeId == "Part::Feature":
            o.ViewObject.Visibility = (o.Name in REAR_SHOW) if on else True
    doc.getObject("Block").ViewObject.Transparency = 45 if on else 0


Gui.ActiveDocument = Gui.getDocument(NAME)
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
    rear_mode(True)
    view.viewLeft(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_back = view.getCamera()
    rear_mode(False)
    view.viewRear(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_side = view.getCamera()
    for k in range(6):
        for st, text in frames_for_shot(k):
            put(st)
            rear_mode(False); view.setCamera(cam_side); Gui.updateGui()
            view.saveImage(os.path.join(TMP, "s.png"), 1000, 700, "White")
            rear_mode(True); view.setCamera(cam_back); Gui.updateGui()
            view.saveImage(os.path.join(TMP, "b.png"), 600, 600, "White")
            im = Image.new("RGB", (1600, 780), "white")
            im.paste(Image.open(os.path.join(TMP, "s.png")).convert("RGB"), (0, 20))
            im.paste(Image.open(os.path.join(TMP, "b.png")).convert("RGB"), (1000, 70))
            dr = ImageDraw.Draw(im)
            dr.text((20, 10), "пистолет сбоку", fill=(80, 80, 80), font=font)
            dr.text((1020, 40), "храповик (вид сзади)", fill=(80, 80, 80), font=font)
            dr.text((20, 730), "выстрел %d/6   |   %s" % (k + 1, text), fill=(0, 0, 0), font=font)
            images.append(im.quantize(colors=128))
    images[0].save(OUT, save_all=True, append_images=images[1:], duration=FRAME_MS, loop=0)
finally:
    pv.SetBool("UseNavigationAnimations", anim_old)
    rear_mode(False)
print(OUT, len(images), "frames")
