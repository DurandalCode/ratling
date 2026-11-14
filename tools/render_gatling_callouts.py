# -*- coding: utf-8 -*-
"""Render gatling labeled overview PNG with PIL callouts.

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        freecad tools/render_gatling_callouts.py

OUT defaults to media/gatling_labeled_3.png (override with OUT=...).
Tips found by one-marker image diff against a clean plate.
"""
import json
import math
import os
import time
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = "/agent/repos/ratling"
MEDIA = "/cursor/stores/bc-37ec12ef-74f8-49b4-8b5c-cc5e0599ca97/media"
OUT = os.environ.get(
    "OUT", os.path.join(MEDIA, "gatling_labeled_3.png"))
META = OUT.rsplit(".", 1)[0] + ".json"
LOG = OUT + ".log"

# Keep previous tip pixels for labels the owner said are already OK, when the
# prior meta exists and world tips match. Otherwise re-find.
KEEP = {
    "Пакет", "Станция", "Ручка", "Бункер", "Стоп подачи",
    "Рукоять", "Муфта", "Буфер",
}
PRIOR_META = os.path.join(MEDIA, "gatling_labeled_2.json")

PRIORITY = [
    "Бункер", "Шнек ×6", "Обойма", "Подшипники", "Кулачок", "MQR", "Муфта",
    "Рукоять", "Буфер", "Пакет", "Ручка", "Ремень", "Дедмен",
    "Станция", "Стоп подачи",
]

# Preferred label direction in image space (radians from +X right, +Y down).
LAB_ANG = {
    "Шнек ×6": math.radians(200),      # left-down from tube
    "Обойма": math.radians(100),       # down from +Y arc
    "Ремень": math.radians(-100),      # up from strap bar
    "Кулачок": math.radians(110),      # down from cam (away from bearings text)
    "Подшипники": math.radians(-40),   # up-right of bearing disk
    "MQR": math.radians(-20),          # up-right of rotor
}

os.chdir(REPO)
os.environ["CHECKS"] = "0"
os.environ["SHOW_LABELS"] = "0"

log = open(LOG, "w")
try:
    src = open(os.path.join(REPO, "gatling", "breech_mechanism.py")).read()
    anchor = "for _i, (_txt, _tip, _dy, _dz) in enumerate(_callouts):"
    if anchor not in src:
        raise RuntimeError("callouts loop anchor missing")
    src2 = src.replace(
        anchor,
        "_DRAW = False\n"
        "for _i, (_txt, _tip, _dy, _dz) in enumerate(_callouts):\n"
        "    if not _DRAW:\n"
        "        continue\n",
        1,
    )
    ns = {"REPO": REPO, "__name__": "__main__"}
    exec(compile(src2, "breech_mechanism.py", "exec"), ns)

    callouts = list(ns["_callouts"])
    lab_xy = ns["_lab_xy"]
    VIEW_ROT = ns["FV"].VIEW_ROT

    targets = {
        "Бункер": ns["hopper"],
        "Шнек ×6": ns["hopper"],
        "Обойма": ns["feed_guard"],
        "Подшипники": ns["brg_f"],
        "MQR": ns["mqr_rotor"],
        "Муфта": ns["soft_coup"],
        "Кулачок": ns["cam"],
        "Ремень": ns["sling"],
    }
    for txt, tip, _, _ in callouts:
        if txt in targets:
            d = targets[txt].distToShape(Part.Vertex(tip))[0]
            log.write("snap %s dist=%.2f tip=(%.1f,%.1f,%.1f)\n" % (
                txt, d, tip.x, tip.y, tip.z))

    prior = {}
    if os.path.isfile(PRIOR_META):
        with open(PRIOR_META) as f:
            prior_data = json.load(f)
        for it in prior_data.get("items", []):
            prior[it["txt"]] = it

    doc = App.ActiveDocument
    # Keep markers centred on the tip so the arrow ends on the part, not 15 mm out.
    # Slight outward nudge only for tips that otherwise disappear inside solids.
    PUSH = {
        "Подшипники": 4.0,
        "Дедмен": 8.0,
        "Кулачок": 14.0,  # cam OD buried in iso — nudge out along +Y
        "Муфта": 4.0,
        "MQR": 5.0,
        "Шнек ×6": 5.0,
        "Обойма": 5.0,
        "Ремень": 4.0,
    }
    RAD = {
        "Подшипники": 16.0,
        "Шнек ×6": 16.0,
        "Обойма": 16.0,
        "Ремень": 15.0,
        "Кулачок": 16.0,
        "MQR": 16.0,
        "Дедмен": 16.0,
    }
    markers = []
    for i, (txt, tip, dy, dz) in enumerate(callouts):
        lab = lab_xy(tip, dy, dz)
        vx, vy, vz = lab.x - tip.x, lab.y - tip.y, lab.z - tip.z
        vn = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
        push = PUSH.get(txt, 3.0)
        if txt == "Подшипники":
            mark = App.Vector(tip.x + push, tip.y, tip.z)
        elif txt == "Шнек ×6":
            mark = App.Vector(tip.x, tip.y - push, tip.z)
        elif txt == "Обойма":
            mark = App.Vector(tip.x, tip.y + push, tip.z)
        elif txt == "Кулачок":
            # Nudge along the same −Y cheek as the tip.
            mark = App.Vector(tip.x, tip.y - push, tip.z)
        elif txt == "MQR":
            mark = App.Vector(tip.x, tip.y - push, tip.z)
        elif txt == "Ремень":
            mark = App.Vector(tip.x + push, tip.y, tip.z)
        else:
            mark = App.Vector(
                tip.x + push * vx / vn,
                tip.y + push * vy / vn,
                tip.z + push * vz / vn)
        sph = Part.makeSphere(RAD.get(txt, 14.0), mark)
        shown = sph.copy()
        shown.Placement = VIEW_ROT.multiply(shown.Placement)
        o = doc.addObject("Part::Feature", "TipMark_%d" % i)
        o.Shape = shown
        o.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
        o.ViewObject.Transparency = 0
        o.ViewObject.Visibility = False
        markers.append((txt, tip, dy, dz, o))

    Gui.updateGui()
    mw = Gui.getMainWindow()
    mw.resize(1920, 1200)
    Gui.updateGui()
    time.sleep(0.2)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    view.viewIsometric()
    view.fitAll()
    Gui.updateGui()
    time.sleep(0.35)

    sw, sh = view.getSize()
    from PIL import Image, ImageDraw, ImageFont, ImageChops
    import numpy as np

    clean_path = "/tmp/gatling_clean.png"
    view.saveImage(clean_path, int(sw), int(sh), "White")
    clean = np.asarray(Image.open(clean_path).convert("RGB"), dtype=np.int16)
    log.write("viewer %sx%s\n" % (sw, sh))

    tip_px = {}
    for txt, tip, dy, dz, o in markers:
        # Always re-find tips for fixed labels too — world tips for KEEP are
        # unchanged, so pixels should land the same; REFIND ensures consistency
        # with this camera. (Pinning old crop coords breaks if fitAll drifts.)
        o.ViewObject.Visibility = True
        Gui.updateGui()
        time.sleep(0.05)
        path = "/tmp/gatling_mark.png"
        view.saveImage(path, int(sw), int(sh), "White")
        o.ViewObject.Visibility = False
        marked = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
        diff = np.abs(marked - clean).sum(axis=2)
        ys, xs = np.where(diff > 80)
        if len(xs) < 5:
            log.write("MISS %s (diff pixels=%d)\n" % (txt, len(xs)))
            continue
        weights = diff[ys, xs].astype(np.float64)
        cx = float(np.average(xs, weights=weights))
        cy = float(np.average(ys, weights=weights))
        tip_px[txt] = (cx, cy)
        log.write("hit %s px=(%.1f,%.1f) n=%d world=(%.1f,%.1f,%.1f)\n" % (
            txt, cx, cy, len(xs), tip.x, tip.y, tip.z))

    Gui.updateGui()
    time.sleep(0.1)
    view.saveImage(clean_path, int(sw), int(sh), "White")
    im_full = Image.open(clean_path).convert("RGB")
    bb = ImageChops.difference(
        im_full, Image.new("RGB", im_full.size, (255, 255, 255))).getbbox()
    margin = 50
    crop = (
        max(bb[0] - margin, 0),
        max(bb[1] - margin, 0),
        min(bb[2] + margin, im_full.size[0]),
        min(bb[3] + margin, im_full.size[1]),
    )
    ox, oy = crop[0], crop[1]
    im = im_full.crop(crop)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)

    items = []
    for txt, tip, dy, dz, o in markers:
        if txt not in tip_px:
            continue
        tx, ty = tip_px[txt][0] - ox, tip_px[txt][1] - oy
        items.append({
            "txt": txt,
            "tip": (tx, ty),
            "dy": dy,
            "dz": dz,
            "world": (tip.x, tip.y, tip.z),
            "keep": txt in KEEP,
        })

    def text_size(txt):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def text_rect(lx, ly, tx, ty, txt):
        tw, th = text_size(txt)
        vx, vy = lx - tx, ly - ty
        vn = math.hypot(vx, vy) or 1.0
        px = lx + 10.0 * vx / vn - tw / 2.0
        py = ly + 10.0 * vy / vn - th / 2.0
        return (px - 4, py - 4, px + tw + 4, py + th + 4)

    def overlaps(r1, r2, pad=8):
        return not (
            r1[2] + pad < r2[0] or r2[2] + pad < r1[0]
            or r1[3] + pad < r2[1] or r2[3] + pad < r1[1])

    placed_labs = []  # (lx, ly)
    placed_rects = []
    order = {n: i for i, n in enumerate(PRIORITY)}
    items.sort(key=lambda it: order.get(it["txt"], 99))

    for it in items:
        tx, ty = it["tip"]
        txt = it["txt"]
        if txt in LAB_ANG:
            ang0 = LAB_ANG[txt]
            dist0 = 140.0
        else:
            # Default: outward from image centre, biased by machine dy/dz.
            cx0, cy0 = im.size[0] / 2.0, im.size[1] / 2.0
            vx, vy = tx - cx0, ty - cy0
            vn = math.hypot(vx, vy) or 1.0
            bx, by = -it["dy"], -it["dz"]
            bn = math.hypot(bx, by) or 1.0
            wx = 0.35 * vx / vn + 0.65 * bx / bn
            wy = 0.35 * vy / vn + 0.65 * by / bn
            ang0 = math.atan2(wy, wx)
            dist0 = 125.0
        best = None
        for k in range(36):
            ang = ang0 + (k // 2) * (0.22 if k % 2 == 0 else -0.22) * ((k + 1) // 2)
            d = dist0 + 8.0 * (k // 3)
            lx = tx + d * math.cos(ang)
            ly = ty + d * math.sin(ang)
            if not (55 < lx < im.size[0] - 55 and 40 < ly < im.size[1] - 40):
                continue
            if any(math.hypot(lx - px, ly - py) < 70.0 for px, py in placed_labs):
                continue
            rect = text_rect(lx, ly, tx, ty, txt)
            if any(overlaps(rect, r) for r in placed_rects):
                continue
            best = (lx, ly, rect)
            break
        if best is None:
            lx = tx + dist0 * math.cos(ang0)
            ly = ty + dist0 * math.sin(ang0)
            best = (lx, ly, text_rect(lx, ly, tx, ty, txt))
        it["lab"] = (best[0], best[1])
        placed_labs.append((best[0], best[1]))
        placed_rects.append(best[2])

    meta = {"crop": crop, "size": list(im.size), "items": []}
    for it in items:
        tx, ty = it["tip"]
        lx, ly = it["lab"]
        txt = it["txt"]
        draw.line([(lx, ly), (tx, ty)], fill=(20, 20, 20), width=3)
        ang = math.atan2(ty - ly, tx - lx)
        ah = 14.0
        a1 = (tx - ah * math.cos(ang - 0.4), ty - ah * math.sin(ang - 0.4))
        a2 = (tx - ah * math.cos(ang + 0.4), ty - ah * math.sin(ang + 0.4))
        draw.polygon([(tx, ty), a1, a2], fill=(20, 20, 20))
        r = 4
        draw.ellipse((tx - r, ty - r, tx + r, ty + r), fill=(15, 15, 15))
        tw, th = text_size(txt)
        vx, vy = lx - tx, ly - ty
        vn = math.hypot(vx, vy) or 1.0
        px_ = lx + 10.0 * vx / vn - tw / 2.0
        py_ = ly + 10.0 * vy / vn - th / 2.0
        for ddx, ddy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)):
            draw.text((px_ + ddx, py_ + ddy), txt, font=font, fill=(255, 255, 255))
        draw.text((px_, py_), txt, font=font, fill=(10, 10, 10))
        meta["items"].append({
            "txt": txt, "tip_px": [tx, ty], "lab_px": [lx, ly],
            "world": list(it["world"]), "keep": it["keep"],
        })
        log.write("final %s tip_px=(%.0f,%.0f) lab_px=(%.0f,%.0f)\n" % (
            txt, tx, ty, lx, ly))

    im.save(OUT, optimize=True)
    with open(META, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log.write("saved %s size=%sx%s hits=%d/%d\n" % (
        OUT, im.size[0], im.size[1], len(tip_px), len(markers)))
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
