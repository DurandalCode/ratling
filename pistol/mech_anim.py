# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol: full-cycle animation of the mechanism layout.

Six trigger pulls, one shot from each barrel, the block one full turn. Each
pull: bolt down, block turned 60 deg by the pawl, bolt in, lock on, fire.
Each release: vent shut, lock off, then the pawl sector swings back with
its tooth bent back out of the notch while the bolt holds the block, and
drops into the next notch.

Uses pistol/mech_layout.py's shapes. Writes exports/pistol_mech_cycle.gif:
the rear view (ratchet) left, the side view right, the phase below.

Run inside FreeCAD (GUI):
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
PRESS_FRAMES, HOLD_FRAMES, RELEASE_FRAMES = 16, 3, 12
FRAME_MS = 80
PAWL_BACK = HUB_X0 + 2.6                 # tooth bent back this far: clear of the hub's face
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

sector_base = cyl_x(2 * SECTOR_R[1], *SECTOR_X).cut(cyl_x(2 * SECTOR_R[0], SECTOR_X[0] - 1, SECTOR_X[1] + 1)).fuse(
    turned(arm, ARM_A0))
pawl_tooth = turned(pawl, PAWL_A0 - 90)


def state_press(t, shot):
    return dict(block=-60 * (shot + turn(t)), sector=-60 * turn(t), pawl_back=0.0, bolt=bolt_down(t),
                lock=lock(t), fire=fire(t), slider_t=turn(t))


def state_release(r, shot):
    back = ramp(r, 0.30, 0.85)                      # sector returns
    bent = ramp(r, 0.28, 0.36) * (1 - ramp(r, 0.80, 0.90))
    return dict(block=-60 * (shot + 1), sector=-60 * (1 - back), pawl_back=bent, bolt=0.0,
                lock=lock(1 - ramp(r, 0.08, 0.25)), fire=fire(1) * (1 - ramp(r, 0.0, 0.08)), slider_t=1 - back)


def phase_text(st, pressing, shot):
    if pressing:
        if st["fire"] > 0.5:
            return "ВЫСТРЕЛ: ствол %d" % (shot + 1)
        if st["lock"] > 0.5:
            return "запор прижат"
        if st["bolt"] > 0.5 and st["sector"] > -1:
            return "засов вниз"
        if st["bolt"] > 0.5:
            return "поворот блока %.0f°" % -st["sector"]
        return "засов в вырез" if st["sector"] < -59 else "покой"
    if st["lock"] > 0.5 or st["fire"] > 0.1:
        return "сброс закрыт, запор отходит"
    if st["pawl_back"] > 0.1:
        return "собачка отогнута, возвращается (засов держит блок)"
    if st["sector"] < -59:
        return "собачка ещё в прежнем вырезе"
    return "собачка в следующем вырезе"


def slider_for(st):
    a = ARM_A0 + st["sector"]
    y = PIN_R0 * math.cos(math.radians(ARM_A0))
    p = V((SLIDER_X[0] + SLIDER_X[1]) / 2, y, y * math.tan(math.radians(a)))
    s = box(SLIDER_X[0], SLIDER_X[1], SLIDER_Y[0], SLIDER_Y[1], p.z - 70, p.z + 6)
    return s, cyl_x(3.0, SLIDER_X[0], SECTOR_X[1], p.y, p.z)


def shapes(st, trig_t):
    sl, pin = slider_for(st)
    tooth = pawl_tooth.translated(V(-PAWL_BACK * st["pawl_back"], 0, 0))
    top = -HUB_R + BOLT_DEPTH - st["bolt"] * (BOLT_DEPTH + 1)
    x_nose = -GAP + 0.2 + st["lock"] * (GAP + HUB_X0 - 0.3)
    sleeve = cyl_x(LOCK_PISTON_D - 0.4, x_nose - 9, x_nose - 6, 0, Z_FIRE).fuse(
        cyl_x(SLEEVE_BORE - 0.2, x_nose - 16, x_nose - 6, 0, Z_FIRE)).fuse(
        cyl_x(NOSE_D, x_nose - 6, x_nose, 0, Z_FIRE)).cut(cyl_x(SEAT_D, x_nose - 20, x_nose + 1, 0, Z_FIRE))
    return {"Block": turned(block, st["block"]), "Sector": turned(sector_base, st["sector"]),
            "Pawl": turned(tooth, st["sector"]), "Slider": sl, "Pin": pin,
            "Bolt": box(HUB_X0 + BOLT_X0, HUB_X0 + BOLT_X0 + BOLT[0], -BOLT[1] / 2, BOLT[1] / 2, top - 22, top),
            "Sleeve": sleeve, "Trigger": trigger_at(trig_t)}


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


for n, s, c, tr in (("Valve_body", valve_body, (0.8, 0.5, 0.2), 0), ("Valve_cap", valve_cap, (0.45, 0.65, 0.85), 0),
                    ("Lock_housing", lock_housing, (0.5, 0.7, 0.5), 55), ("Axle", axle, (0.7, 0.7, 0.7), 40),
                    ("Valves", valves, (0.3, 0.3, 0.8), 30)):
    addo(n, s, c, tr)
STYLE = {"Block": ((0.55, 0.55, 0.6), 45), "Sector": ((0.9, 0.6, 0.1), 0), "Pawl": ((0.95, 0.35, 0.05), 0),
         "Slider": ((0.9, 0.8, 0.2), 0), "Pin": ((0.15, 0.15, 0.15), 0), "Bolt": ((0.85, 0.15, 0.15), 0),
         "Sleeve": ((0.15, 0.75, 0.3), 0), "Trigger": ((0.25, 0.25, 0.25), 0)}
mv = {n: addo(n, Part.Shape(), *STYLE[n]) for n in STYLE}
BACK_HIDE = ("Valve_body", "Valve_cap", "Valves", "Trigger")


def show(names, on):
    for o in ad.Objects:
        if o.Name in names:
            o.ViewObject.Visibility = on


def pose(st, trig_t):
    for n, s in shapes(st, trig_t).items():
        mv[n].Shape = s
    ad.recompute()


Gui.ActiveDocument = Gui.getDocument("mech_cycle")
view = Gui.ActiveDocument.activeView()
view.setCameraType("Orthographic")
pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
anim_old = pv.GetBool("UseNavigationAnimations", True)
pv.SetBool("UseNavigationAnimations", False)
os.makedirs(TMP, exist_ok=True)
font = ImageFont.truetype(FONT, 26)
frames = []
try:
    pose(state_press(0.5, 0), 0.5)
    show(BACK_HIDE, False)
    view.viewLeft(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_back = view.getCamera()
    show(BACK_HIDE, True)
    view.viewRear(); Gui.updateGui(); view.fitAll(); Gui.updateGui(); cam_side = view.getCamera()
    seq = []
    for shot in range(6):
        seq += [(state_press(i / (PRESS_FRAMES - 1), shot), i / (PRESS_FRAMES - 1), True, shot) for i in range(PRESS_FRAMES)]
        seq += [(state_press(1.0, shot), 1.0, True, shot)] * HOLD_FRAMES
        seq += [(state_release(i / (RELEASE_FRAMES - 1), shot), 1 - i / (RELEASE_FRAMES - 1), False, shot)
                for i in range(RELEASE_FRAMES)]
    for st, trig_t, pressing, shot in seq:
        pose(st, trig_t)
        show(BACK_HIDE, False); view.setCamera(cam_back); Gui.updateGui()
        view.saveImage(os.path.join(TMP, "b.png"), 700, 700, "White")
        show(BACK_HIDE, True); view.setCamera(cam_side); Gui.updateGui()
        view.saveImage(os.path.join(TMP, "s.png"), 900, 700, "White")
        im = Image.new("RGB", (1600, 780), "white")
        im.paste(Image.open(os.path.join(TMP, "b.png")).convert("RGB"), (0, 0))
        im.paste(Image.open(os.path.join(TMP, "s.png")).convert("RGB"), (700, 0))
        dr = ImageDraw.Draw(im)
        dr.text((20, 10), "вид сзади (храповик)", fill=(80, 80, 80), font=font)
        dr.text((720, 10), "вид сбоку", fill=(80, 80, 80), font=font)
        dr.text((20, 720), "выстрел %d/6   спуск %3.0f%% %s   |   %s"
                % (shot + 1, trig_t * 100, "▼ нажатие" if pressing else "▲ возврат", phase_text(st, pressing, shot)),
                fill=(0, 0, 0), font=font)
        frames.append(im.quantize(colors=96))
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0)
finally:
    pv.SetBool("UseNavigationAnimations", anim_old)
print(OUT, len(frames), "frames")
