# -*- coding: utf-8 -*-
"""
Two orthographic side sections of QEV v1.3 / v1.5 with dimension arrows.

Takes a thin slab through the valve (-2 < y < 2), rotates tubes to run
left→right, shoots both with the same camera, annotates what changed.

Needs FreeCAD GUI. Env: OUT, SIZE=WxH.
"""
import math
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.environ.get("OUT", "exports/compare_v13_v15/dims.png")
if not os.path.isabs(out):
    out = os.path.join(REPO, out)
log = open(out + ".log", "w")


def build(script):
    ns = {"REPO": REPO, "STAGE3_LIBRARY": True, "__name__": "__main__"}
    exec(open(os.path.join(REPO, script)).read(), ns)
    stack = ns["body"].fuse(ns["cap_a"]).fuse(ns["dia_a"]).fuse(ns["breech_a"]).removeSplitter()
    return stack, ns


def side_section(shape):
    # thin slab on the symmetry plane so cavities read as holes
    slab = Part.makeBox(120, 4, 100, App.Vector(-50, -2, -40))
    s = shape.common(slab)
    # tubes along +Z → rotate to +X (left→right on Front view)
    s.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), -90)
    return s


def shoot(doc, shape, path, w, h, cam=None):
    for o in list(doc.Objects):
        doc.removeObject(o.Name)
    o = doc.addObject("Part::Feature", "Part")
    o.Shape = shape
    o.ViewObject.ShapeColor = (0.93, 0.60, 0.28)
    o.ViewObject.Transparency = 0
    try:
        o.ViewObject.DisplayMode = "Flat Lines"
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
        o.ViewObject.LineWidth = 2.0
    except Exception:
        pass
    doc.recompute()
    Gui.updateGui()
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    if cam is None:
        view.viewFront()
        Gui.updateGui()
        view.fitAll()
        Gui.updateGui()
        cam = view.getCamera()
    else:
        view.setCamera(cam)
        Gui.updateGui()
    view.saveImage(path, w, h, "White")
    return cam


try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont

    stack_a, na = build("module/stage3_v13.py")
    stack_b, nb = build("module/stage3_v15.py")
    a = side_section(stack_a)
    b = side_section(stack_b)
    log.write("section vols A=%.0f B=%.0f\n" % (a.Volume, b.Volume))
    log.write("A: LIFT=%.1f GALLERY_R=%.1f DIA_D=%.1f CAP_T=%.1f SEAT_LAND=%.1f ROD_R=%.1f\n" % (
        na["LIFT"], na["GALLERY_R"], na["DIA_D"], na["CAP_T"], na["SEAT_LAND"], na["ROD_R"]))
    log.write("B: LIFT=%.1f GALLERY_R=%.1f DIA_D=%.1f CAP_T=%.1f SEAT_LAND=%.1f ROD_R=%.1f\n" % (
        nb["LIFT"], nb["GALLERY_R"], nb["DIA_D"], nb["CAP_T"], nb["SEAT_LAND"], nb["ROD_R"]))

    if "qev_dims" in App.listDocuments():
        App.closeDocument("qev_dims")
    doc = App.newDocument("qev_dims")
    w, h = map(int, os.environ.get("SIZE", "2000x1200").split("x"))
    path_a = out.replace(".png", "_A.png")
    path_b = out.replace(".png", "_B.png")
    cam = shoot(doc, a.fuse(b), out.replace(".png", "_fit.png"), w, h, None)
    shoot(doc, a, path_a, w, h, cam)
    shoot(doc, b, path_b, w, h, cam)

    def crop_white(im):
        bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        if not bb:
            return im
        m = 24
        return im.crop((max(bb[0] - m, 0), max(bb[1] - m, 0),
                        min(bb[2] + m, im.size[0]), min(bb[3] + m, im.size[1])))

    im_a = crop_white(Image.open(path_a).convert("RGB"))
    im_b = crop_white(Image.open(path_b).convert("RGB"))
    th = max(im_a.size[1], im_b.size[1])

    def fit_h(im, th):
        if im.size[1] == th:
            return im
        nw = int(im.size[0] * th / im.size[1])
        return im.resize((nw, th), Image.Resampling.LANCZOS)

    im_a, im_b = fit_h(im_a, th), fit_h(im_b, th)
    tw = max(im_a.size[0], im_b.size[0])

    def pad_w(im, tw):
        if im.size[0] == tw:
            return im
        c = Image.new("RGB", (tw, im.size[1]), (255, 255, 255))
        c.paste(im, ((tw - im.size[0]) // 2, 0))
        return c

    im_a, im_b = pad_w(im_a, tw), pad_w(im_b, tw)

    gap, header, footer, gutter = 36, 64, 36, 240
    plate_w = gutter + tw + gap + tw + gutter
    plate_h = header + th + footer + 90
    plate = Image.new("RGB", (plate_w, plate_h), (255, 255, 255))
    x0 = gutter
    x1 = gutter + tw + gap
    plate.paste(im_a, (x0, header))
    plate.paste(im_b, (x1, header))
    draw = ImageDraw.Draw(plate)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:
        font = font_s = font_b = ImageFont.load_default()

    draw.text((x0 + 8, 14), "v1.3  (стенд)", fill=(170, 40, 35), font=font_b)
    draw.text((x1 + 8, 14), "v1.5  (кандидат)", fill=(25, 110, 40), font=font_b)
    draw.line([(x0 + tw + gap // 2, header - 4), (x0 + tw + gap // 2, header + th + 4)],
              fill=(200, 200, 200), width=2)

    def arrow(p1, p2, color, width=3):
        draw.line([p1, p2], fill=color, width=width)
        ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        for da in (0.35, -0.35):
            draw.line([p2, (p2[0] - 14 * math.cos(ang + da),
                            p2[1] - 14 * math.sin(ang + da))], fill=color, width=width)

    def dim_v(x, y0, y1, text, color, left=True):
        draw.line([(x - 7, y0), (x + 7, y0)], fill=color, width=2)
        draw.line([(x - 7, y1), (x + 7, y1)], fill=color, width=2)
        draw.line([(x, y0), (x, y1)], fill=color, width=3)
        # arrowheads
        for y, s in ((y0, 1), (y1, -1)):
            draw.line([(x, y), (x - 6, y + s * 10)], fill=color, width=2)
            draw.line([(x, y), (x + 6, y + s * 10)], fill=color, width=2)
        bb = draw.textbbox((0, 0), text, font=font_s)
        tx = x - (bb[2] - bb[0]) - 12 if left else x + 12
        ty = (y0 + y1) // 2 - (bb[3] - bb[1]) // 2
        draw.text((tx, ty), text, fill=color, font=font_s)

    def dim_h(x0_, x1_, y, text, color, above=True):
        draw.line([(x0_, y - 7), (x0_, y + 7)], fill=color, width=2)
        draw.line([(x1_, y - 7), (x1_, y + 7)], fill=color, width=2)
        draw.line([(x0_, y), (x1_, y)], fill=color, width=3)
        for x, s in ((x0_, 1), (x1_, -1)):
            draw.line([(x, y), (x + s * 10, y - 6)], fill=color, width=2)
            draw.line([(x, y), (x + s * 10, y + 6)], fill=color, width=2)
        bb = draw.textbbox((0, 0), text, font=font_s)
        tx = (x0_ + x1_) // 2 - (bb[2] - bb[0]) // 2
        ty = y - (bb[3] - bb[1]) - 8 if above else y + 8
        draw.text((tx, ty), text, fill=color, font=font_s)

    def leader(text_xy, tip_xy, text, color, lines=None):
        arrow(text_xy, tip_xy, color)
        lines = lines or [text]
        for i, line in enumerate(lines):
            draw.text((text_xy[0], text_xy[1] - 10 + i * 20), line, fill=color, font=font_s)

    red, green, grey = (175, 35, 30), (20, 115, 40), (55, 55, 55)

    # After rotation: machine Z → image X (right), machine X → image -Y? 
    # rotate -90 around Y: (x,y,z) → (z, y, -x)
    # Front view: looking -Z_display... FreeCAD Front looks from +Z toward -Z of displayed shape?
    # Empirically: tubes go right, cap is on the left after our -90° rot (cap was z<0 → x<0).
    # Layout fractions for a typical head section (left=cap, right=breech/tubes):
    #   cap band: u≈0.08..0.22
    #   diaphragm/clamp: u≈0.22..0.28
    #   gallery: u≈0.28..0.55, vertical span around barrel axis
    #   seat bore: near horizontal mid
    #   tubes: u≈0.70..1.0

    def U(base, u):
        return base + int(u * tw)

    def V(v):
        return header + int(v * th)

    # ---- v1.3 ----
    # LIFT = pocket depth under diaphragm (vertical at clamp)
    dim_v(U(x0, 0.30), V(0.38), V(0.55), "LIFT 4", red, left=True)
    # GALLERY diameter (free mouth ≈ 2*GALLERY_R across, vertical through gallery)
    dim_v(U(x0, 0.42), V(0.28), V(0.72), "GALLERY Ø36", red, left=True)
    # CAP_T
    dim_h(U(x0, 0.06), U(x0, 0.22), V(0.88), "CAP 16", red, above=False)
    # DIA
    leader((x0 - gutter + 16, V(0.78)), (U(x0, 0.25), V(0.50)), "", red,
           lines=["диск Ø46"])
    # SEAT
    leader((x0 - gutter + 16, V(0.48)), (U(x0, 0.48), V(0.50)), "", grey,
           lines=["седло Ø16"])
    # LAND
    leader((x0 - gutter + 16, V(0.62)), (U(x0, 0.45), V(0.46)), "", red,
           lines=["LAND 2.0"])

    # ---- v1.5 ----
    dim_v(U(x1, 0.30), V(0.36), V(0.56), "LIFT 5  ▲", green, left=False)
    dim_v(U(x1, 0.42), V(0.26), V(0.74), "GALLERY Ø38  ▲", green, left=False)
    dim_h(U(x1, 0.05), U(x1, 0.23), V(0.90), "CAP 17  ▲", green, above=False)
    leader((x1 + tw + 12, V(0.78)), (U(x1, 0.25), V(0.50)), "", green,
           lines=["диск Ø48  ▲"])
    leader((x1 + tw + 12, V(0.48)), (U(x1, 0.48), V(0.50)), "", grey,
           lines=["седло Ø16", "(без изменений)"])
    leader((x1 + tw + 12, V(0.62)), (U(x1, 0.45), V(0.46)), "", green,
           lines=["LAND 1.5  ▼"])
    leader((x1 + tw + 12, V(0.30)), (U(x1, 0.62), V(0.22)), "", green,
           lines=["ROD_R 28  ▲", "(было 26.5)"])

    # legend / summary under figures
    y = header + th + 16
    summary = (
        "Итог v1.5: тот же Ø16, но LIFT 4→5, GALLERY R18→19 (Ø36→Ø38), LAND 2→1.5, "
        "диск Ø46→Ø48, CAP 16→17, ROD_R 26.5→28.  Curtain 1.00×→1.25×, gallery 1.11×→1.32× seat."
    )
    # wrap
    words = summary.split()
    line, lines = "", []
    for w_ in words:
        trial = (line + " " + w_).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] < plate_w - 40:
            line = trial
        else:
            lines.append(line)
            line = w_
    if line:
        lines.append(line)
    for i, line in enumerate(lines):
        draw.text((20, y + i * 24), line, fill=(40, 40, 40), font=font)

    plate.save(out, optimize=True)
    log.write("saved %s %dx%d\n" % (out, plate.size[0], plate.size[1]))
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
