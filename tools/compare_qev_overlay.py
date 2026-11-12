# -*- coding: utf-8 -*-
"""
Orthographic cut-face overlay of two stage3_qev OVERRIDE variants (default v1.3 vs v1.5).

Builds both with STAGE3_LIBRARY, keeps y >= 0, crops to the valve head, then:
  grey  = common (very transparent)
  red   = only in A (v1.3)
  green = only in B (v1.5)

Also writes a pixel-diff plate (same camera, A then B) so 1 mm changes read clearly.

Needs FreeCAD GUI. Env: OUT, SCRIPT_A, SCRIPT_B, SIZE=WxH.
"""
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.environ.get("OUT", "exports/compare_v13_v15/overlay.png")
if not os.path.isabs(out):
    out = os.path.join(REPO, out)
log = open(out + ".log", "w")


def build(script):
    ns = {"REPO": REPO, "STAGE3_LIBRARY": True, "__name__": "__main__"}
    exec(open(os.path.join(REPO, script)).read(), ns)
    stack = ns["body"].fuse(ns["cap_a"]).fuse(ns["dia_a"]).fuse(ns["breech_a"]).removeSplitter()
    return stack, ns


def half_cut(shape):
    return shape.cut(Part.makeBox(400, 200, 800, App.Vector(-200, -200, -100)))


def add(doc, name, shape, color, transp=0):
    if shape is None or shape.isNull() or getattr(shape, "Volume", 0) < 1e-6:
        log.write("skip empty %s\n" % name)
        return None
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.ViewObject.ShapeColor = color
    o.ViewObject.Transparency = transp
    return o


try:
    script_a = os.environ.get("SCRIPT_A", "module/stage3_v13.py")
    script_b = os.environ.get("SCRIPT_B", "module/stage3_v15.py")
    log.write("A=%s B=%s\n" % (script_a, script_b))
    stack_a, _ = build(script_a)
    stack_b, _ = build(script_b)
    box = Part.makeBox(90, 80, 80, App.Vector(-45, -5, -35))
    a = half_cut(stack_a).common(box)
    b = half_cut(stack_b).common(box)
    common = a.common(b).removeSplitter()
    only_a = a.cut(b).removeSplitter()
    only_b = b.cut(a).removeSplitter()
    log.write("vols common=%.1f only_a=%.1f only_b=%.1f\n" % (
        common.Volume, only_a.Volume, only_b.Volume))

    if "qev_overlay" in App.listDocuments():
        App.closeDocument("qev_overlay")
    doc = App.newDocument("qev_overlay")
    o_common = add(doc, "Common", common, (0.62, 0.62, 0.66), 80)
    o_a = add(doc, "Only_v13", only_a, (0.92, 0.12, 0.10), 0)
    o_b = add(doc, "Only_v15", only_b, (0.10, 0.72, 0.28), 0)
    # faint full outlines so the eye has context
    add(doc, "Outline_v13", a, (0.75, 0.45, 0.45), 88)
    add(doc, "Outline_v15", b, (0.45, 0.75, 0.50), 88)
    doc.recompute()
    Gui.updateGui()

    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    view.viewRear()  # cut face: looking from -Y toward +Y, machine frame
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    cam = view.getCamera()

    w, h = map(int, os.environ.get("SIZE", "2400x1600").split("x"))
    view.saveImage(out, w, h, "White")

    # --- pixel plate: same camera, A alone then B alone ---
    for o in doc.Objects:
        if getattr(o, "ViewObject", None):
            o.ViewObject.Visibility = False
    oa = add(doc, "Full_A", a, (0.85, 0.35, 0.25), 20)
    ob = add(doc, "Full_B", b, (0.25, 0.70, 0.35), 20)
    doc.recompute()
    Gui.updateGui()
    view.setCamera(cam)

    def shoot(path, show, hide):
        show.ViewObject.Visibility = True
        hide.ViewObject.Visibility = False
        Gui.updateGui()
        view.setCamera(cam)
        Gui.updateGui()
        view.saveImage(path, w, h, "White")

    path_a = out.replace(".png", "_A.png")
    path_b = out.replace(".png", "_B.png")
    shoot(path_a, oa, ob)
    shoot(path_b, ob, oa)

    from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageEnhance
    def load_crop(path):
        im = Image.open(path).convert("RGB")
        bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        return im, bb

    im_a, _ = load_crop(path_a)
    im_b, _ = load_crop(path_b)
    # shared crop from union bbox
    bb = ImageChops.difference(
        ImageChops.lighter(
            ImageChops.difference(im_a, Image.new("RGB", im_a.size, (255, 255, 255))),
            ImageChops.difference(im_b, Image.new("RGB", im_b.size, (255, 255, 255))),
        ),
        Image.new("RGB", im_a.size, (0, 0, 0)),
    ).getbbox()
    if bb:
        m = 40
        boxc = (max(bb[0] - m, 0), max(bb[1] - m, 0), min(bb[2] + m, w), min(bb[3] + m, h))
        im_a = im_a.crop(boxc)
        im_b = im_b.crop(boxc)

    # pixel overlay: grey base = average, red where A darker/different, green where B
    diff = ImageChops.difference(im_a, im_b).convert("L")
    diff = ImageEnhance.Contrast(diff).enhance(3.0)
    # mask of meaningful change
    mask = diff.point(lambda p: 255 if p > 18 else 0)
    base = ImageChops.blend(im_a, im_b, 0.5).convert("RGBA")
    red = Image.new("RGBA", base.size, (220, 30, 20, 0))
    green = Image.new("RGBA", base.size, (20, 180, 50, 0))
    # A-only pixels roughly: where A is darker in diff regions vs white-ish B
    import numpy as np
    a = np.asarray(im_a).astype("int16")
    b = np.asarray(im_b).astype("int16")
    m = np.asarray(mask)
    # luminance
    la = a.mean(axis=2)
    lb = b.mean(axis=2)
    only_a_m = (m > 0) & (la + 8 < lb)   # A has more solid (darker) → removed in v15
    only_b_m = (m > 0) & (lb + 8 < la)   # B has more solid → added in v15
    ra = np.zeros((base.size[1], base.size[0], 4), dtype="uint8")
    ga = np.zeros_like(ra)
    ra[only_a_m] = (220, 40, 30, 200)
    ga[only_b_m] = (30, 180, 60, 200)
    overlay = Image.alpha_composite(base, Image.fromarray(ra, "RGBA"))
    overlay = Image.alpha_composite(overlay, Image.fromarray(ga, "RGBA"))
    overlay = overlay.convert("RGB")

    # also crop the solid overlay render
    solid = Image.open(out).convert("RGB")
    sbb = ImageChops.difference(solid, Image.new("RGB", solid.size, (255, 255, 255))).getbbox()
    if sbb:
        m = 36
        solid = solid.crop((max(sbb[0] - m, 0), max(sbb[1] - m, 0),
                            min(sbb[2] + m, w), min(sbb[3] + m, h)))

    # stack: solid boolean overlay on top, pixel overlay below, shared legend
    gap = 20
    legend_h = 72
    width = max(solid.size[0], overlay.size[0])
    plate = Image.new("RGB", (width, solid.size[1] + gap + overlay.size[1] + legend_h), (255, 255, 255))
    plate.paste(solid, ((width - solid.size[0]) // 2, 0))
    plate.paste(overlay, ((width - overlay.size[0]) // 2, solid.size[1] + gap))
    draw = ImageDraw.Draw(plate)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except Exception:
        font = font_b = ImageFont.load_default()
    draw.text((16, 8), "boolean: общее / только v1.3 / только v1.5", fill=(30, 30, 30), font=font_b)
    draw.text((16, solid.size[1] + gap + 8), "пиксельный дифф той же камеры (усилен)", fill=(30, 30, 30), font=font_b)
    y = solid.size[1] + gap + overlay.size[1] + 20
    draw.rectangle([16, y, 40, y + 24], fill=(150, 150, 155))
    draw.text((48, y), "общее", fill=(60, 60, 60), font=font)
    draw.rectangle([160, y, 184, y + 24], fill=(220, 40, 30))
    draw.text((192, y), "только v1.3 (убрано в v1.5)", fill=(140, 30, 20), font=font)
    draw.rectangle([520, y, 544, y + 24], fill=(30, 180, 60))
    draw.text((552, y), "только v1.5 (LIFT/gallery/диск/крышка/ROD)", fill=(20, 90, 30), font=font)
    plate.save(out, optimize=True)
    # publish helpers
    overlay.save(out.replace(".png", "_pixel.png"), optimize=True)
    solid.save(out.replace(".png", "_bool.png"), optimize=True)
    log.write("saved %s\n" % out)
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
