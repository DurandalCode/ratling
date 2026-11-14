# -*- coding: utf-8 -*-
"""Render gatling_labeled_2.png with PIL callouts.

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        freecad tools/render_gatling_callouts.py

Writes media paths under the agent store; tips found by one-marker image diff.

Find each tip by differencing a one-marker frame against a clean plate —
avoids colour collisions with the model.
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
OUT = os.path.join(MEDIA, "gatling_labeled_2.png")
META = os.path.join(MEDIA, "gatling_labeled_2.json")
LOG = OUT + ".log"

PRIORITY = [
    "Бункер", "Шнек ×6", "Обойма", "Подшипники", "MQR", "Муфта",
    "Рукоять", "Буфер", "Пакет", "Ручка", "Ремень", "Дедмен",
    "Кулачок", "Станция", "Стоп подачи",
]

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
    _on = ns["_on"]
    V = ns["V"]
    hopper = ns["hopper"]
    feed_guard = ns["feed_guard"]
    brg_f = ns["brg_f"]
    mqr_rotor = ns["mqr_rotor"]
    soft_coup = ns["soft_coup"]
    r_case_od = ns["r_case_od"]
    z_feed = ns["z_feed"]
    BRG_OD = ns["BRG_OD"]
    ROTOR_OD = ns["ROTOR_OD"]
    SOFT_OD = ns["SOFT_OD"]

    hb = hopper.BoundBox
    overrides = {
        "Бункер": _on(hopper, V(hb.XMax, 0.0, hb.Center.z + 8.0)),
        "Шнек ×6": _on(hopper, V(r_case_od + 6.0, 28.0, z_feed)),
        "Подшипники": _on(brg_f, V(r_case_od - 2.5, 0.0, brg_f.BoundBox.Center.z)),
        "MQR": _on(mqr_rotor, V(ROTOR_OD / 2.0, 0.0, mqr_rotor.BoundBox.Center.z)),
        "Муфта": _on(soft_coup, V(SOFT_OD / 2.0, 0.0, soft_coup.BoundBox.Center.z)),
    }
    lab_off = {
        "Бункер": (-160.0, -80.0),
        "Шнек ×6": (150.0, -90.0),
        "Обойма": (80.0, -150.0),
        "Подшипники": (160.0, -100.0),
        "MQR": (140.0, -80.0),
        "Муфта": (100.0, 80.0),
        "Рукоять": (-100.0, 60.0),
        "Буфер": (-120.0, -40.0),
        "Пакет": (30.0, 140.0),
        "Ручка": (60.0, 120.0),
        "Ремень": (-50.0, 130.0),
        "Дедмен": (-100.0, 90.0),
        "Кулачок": (110.0, -30.0),
        "Станция": (120.0, 50.0),
        "Стоп подачи": (-120.0, 80.0),
    }
    rebuilt = []
    for txt, tip, dy, dz in callouts:
        tip2 = overrides.get(txt, tip)
        dy2, dz2 = lab_off.get(txt, (dy, dz))
        rebuilt.append((txt, tip2, dy2, dz2))
    callouts = rebuilt

    targets = {
        "Бункер": hopper, "Шнек ×6": hopper, "Обойма": feed_guard,
        "Подшипники": brg_f, "MQR": mqr_rotor, "Муфта": soft_coup,
    }
    for txt, tip, _, _ in callouts:
        if txt in targets:
            d = targets[txt].distToShape(Part.Vertex(tip))[0]
            log.write("snap %s dist=%.2f tip=(%.1f,%.1f,%.1f)\n" % (
                txt, d, tip.x, tip.y, tip.z))

    doc = App.ActiveDocument
    # Buried tips (inside frame / small) need a longer outward marker.
    PUSH = {
        "Подшипники": 14.0,
        "Дедмен": 26.0,
        "Кулачок": 24.0,
        "Муфта": 20.0,
        "MQR": 18.0,
        "Шнек ×6": 28.0,
    }
    RAD = {
        "Подшипники": 16.0,
        "Дедмен": 16.0,
        "Кулачок": 16.0,
        "Шнек ×6": 16.0,
    }
    markers = []
    for i, (txt, tip, dy, dz) in enumerate(callouts):
        lab = lab_xy(tip, dy, dz)
        vx, vy, vz = lab.x - tip.x, lab.y - tip.y, lab.z - tip.z
        vn = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
        push = PUSH.get(txt, 12.0)
        # Bearings tip already on +X rim — push further +X so the marker clears.
        if txt == "Подшипники":
            mark = App.Vector(tip.x + push, tip.y, tip.z)
        elif txt == "Шнек ×6":
            # Tube cheek toward +Y — outside the bin/guard clutter.
            mark = App.Vector(tip.x, tip.y + push, tip.z)
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
        o.ViewObject.Visibility = True
        Gui.updateGui()
        time.sleep(0.05)
        path = "/tmp/gatling_mark.png"
        view.saveImage(path, int(sw), int(sh), "White")
        o.ViewObject.Visibility = False
        marked = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
        diff = np.abs(marked - clean).sum(axis=2)
        # Strong differences = marker pixels.
        ys, xs = np.where(diff > 80)
        if len(xs) < 5:
            log.write("MISS %s (diff pixels=%d)\n" % (txt, len(xs)))
            continue
        # Use the brightest-diff cluster centroid.
        weights = diff[ys, xs].astype(np.float64)
        cx = float(np.average(xs, weights=weights))
        cy = float(np.average(ys, weights=weights))
        tip_px[txt] = (cx, cy)
        log.write("hit %s px=(%.1f,%.1f) n=%d\n" % (txt, cx, cy, len(xs)))

    Gui.updateGui()
    time.sleep(0.1)
    # Final clean plate (markers already hidden).
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

    cx0, cy0 = im.size[0] / 2.0, im.size[1] / 2.0
    items = []
    for txt, tip, dy, dz, o in markers:
        if txt not in tip_px:
            continue
        tx, ty = tip_px[txt][0] - ox, tip_px[txt][1] - oy
        vx, vy = tx - cx0, ty - cy0
        vn = math.hypot(vx, vy) or 1.0
        bx, by = -dy, -dz
        bn = math.hypot(bx, by) or 1.0
        wx = 0.4 * vx / vn + 0.6 * bx / bn
        wy = 0.4 * vy / vn + 0.6 * by / bn
        wn = math.hypot(wx, wy) or 1.0
        items.append({
            "txt": txt,
            "tip": (tx, ty),
            "dir": (wx / wn, wy / wn),
            "world": (tip.x, tip.y, tip.z),
        })

    placed = []
    order = {n: i for i, n in enumerate(PRIORITY)}
    items.sort(key=lambda it: order.get(it["txt"], 99))
    for it in items:
        tx, ty = it["tip"]
        dx, dy = it["dir"]
        dist = 125.0
        ang0 = math.atan2(dy, dx)
        best = None
        for k in range(24):
            ang = ang0 + (k // 2) * (0.28 if k % 2 == 0 else -0.28) * ((k + 1) // 2)
            d = dist + 10.0 * (k // 4)
            lx = tx + d * math.cos(ang)
            ly = ty + d * math.sin(ang)
            ok = all(math.hypot(lx - px, ly - py) >= 54.0 for px, py in placed)
            if not (48 < lx < im.size[0] - 48 and 36 < ly < im.size[1] - 36):
                ok = False
            if ok:
                best = (lx, ly)
                break
        if best is None:
            best = (tx + dist * math.cos(ang0), ty + dist * math.sin(ang0))
        it["lab"] = best
        placed.append(best)

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
        bbox = draw.textbbox((0, 0), txt, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        vx, vy = lx - tx, ly - ty
        vn = math.hypot(vx, vy) or 1.0
        px_ = lx + 10.0 * vx / vn - tw / 2.0
        py_ = ly + 10.0 * vy / vn - th / 2.0
        for ddx, ddy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)):
            draw.text((px_ + ddx, py_ + ddy), txt, font=font, fill=(255, 255, 255))
        draw.text((px_, py_), txt, font=font, fill=(10, 10, 10))
        meta["items"].append({
            "txt": txt, "tip_px": [tx, ty], "lab_px": [lx, ly],
            "world": list(it["world"]),
        })
        log.write("final %s tip_px=(%.0f,%.0f)\n" % (txt, tx, ty))

    im.save(OUT, optimize=True)
    with open(META, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log.write("saved %s size=%sx%s hits=%d/%d\n" % (
        OUT, im.size[0], im.size[1], len(tip_px), len(markers)))
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
