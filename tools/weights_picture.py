# -*- coding: utf-8 -*-
"""
The picture for docs/weights.md: concept A as it is weighed, coloured by material (printed, metal, other).

Builds carry_mount.py (pack, carry plates, handle, pad at 16 and 19) and rear_frame.py (head plate, bench C's
head, bevel box) and puts one gun of BARRELS in a fresh document, every part coloured by what it is made of:
PETG print orange; steel, aluminium and brass in greys; rubber black. The muzzle rings are drawn, not the
sleeves (an option, they would hide the steel barrels).
Needs the GUI (xvfb-run on a VM):

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        BARRELS=16 OUT=exports/weights/a16.png freecad tools/weights_picture.py

The table beside the views is drawn by tools/weights_sheet.py from the numbers in docs/weights.md.
"""

import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(REPO, os.environ["OUT"])
os.makedirs(os.path.dirname(out), exist_ok=True)
log = open(out + ".log", "w")

COLORS = {
    "print": (0.93, 0.55, 0.15),        # PETG
    "steel": (0.30, 0.32, 0.36),
    "alu": (0.78, 0.80, 0.84),
    "brass": (0.62, 0.58, 0.42),
    "rubber": (0.08, 0.08, 0.08),
}

try:
    C = {"REPO": REPO, "__name__": "__main__"}
    exec(open(os.path.join(REPO, "mitrailleuse", "carry_mount.py"), encoding="utf-8").read(), C)
    R = {"REPO": REPO, "__name__": "__main__"}
    exec(open(os.path.join(REPO, "mitrailleuse", "rear_frame.py"), encoding="utf-8").read(), R)
    tag = "A%s" % os.environ.get("BARRELS", "16")
    key, mods, plates = C["built"][tag]
    M, RB, head, drive = C["M"], R["RB"], R["head"], R["drive"]
    T = App.Vector(0, 0, R["Z0"])
    P = C["FV"].VIEW_ROT.multiply(R["SHOW"])

    doc = App.newDocument("weights_" + tag)
    shown = []

    def add(name, shape, mat, offset=None):
        s = shape.copy()
        if offset is not None:
            s.translate(offset)
        s.Placement = P.multiply(s.Placement)
        o = doc.addObject("Part::Feature", name)
        o.Shape = s
        shown.append((o, mat))

    # pack: modules, plates, rails
    pts = C["LAYOUT"][key]
    angs = C["rod_angles"](key, pts)
    orings = [C["place"](M["orings"], x, y, a) for (x, y), a in zip(pts, angs)]
    for mat, names in (("print", ("rp", "fp", "sr", "rear_yoke", "front_yoke", "muzzle_ring")), ("alu", ("chamber",)),
                       ("steel", ("barrel", "hardware")), ("brass", ("fitting",))):
        add("Mod_" + "_".join(names), Part.makeCompound([m[n] for m in mods for n in names]), mat)
    add("ORings", Part.makeCompound(orings), "rubber")
    for side in ("rear", "front"):
        add("Plate_" + side, C["plate"](key, side)[0], "print")
    add("Rails", Part.makeCompound(R["rail_parts"]), "alu")
    # carried at the CG
    for side, (s, _) in plates.items():
        add("CG_" + side, s, "print")
    add("Handle", C["grip_part"], "print")
    add("Tripod_pad", C["pad_part"], "print")
    # head and rear frame (rear_frame.py's local frame, shifted by Z0)
    for n, s in (("Head_plate", R["hp"]), ("Stop_lever", R["lev"]), ("Bevel_box", drive["box"]),
                 ("Bevel_gears", drive["bevel_lay"].fuse(drive["bevel_crank"])), ("Crank", drive["crank"])):
        add(n, s, "print", T)
    for n in ("housing", "blocks", "guide_plates", "followers", "rotor", "gear", "pinion", "stop_disc"):
        add("Head_" + n, head[n], "print", T)
    for n, s in (("Pull_rod", R["rod_off"]), ("Stop_pin", RB["stop_pin"]), ("Shaft", RB["shaft"]),
                 ("Layshaft", R["layshaft"]), ("Crank_shaft", drive["crank_shaft"]),
                 ("Bearings", R["head_brgs"].fuse(drive["bearings"])), ("Slip_clutch", RB["slip"]),
                 ("Valve_cores", head["cores"]), ("Pins", head["pins"])):
        add(n, s, "steel", T)
    add("Fittings", head["fittings"], "brass", T)

    doc.recompute()
    for d in list(App.listDocuments()):
        if d != doc.Name:
            App.closeDocument(d)
    Gui.updateGui()
    for o, mat in shown:
        o.ViewObject.ShapeColor = COLORS[mat]
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
    Gui.updateGui()
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    view.viewIsometric()
    view.fitAll()
    Gui.updateGui()
    view.saveImage(out, 2400, 1500, "White")
    from PIL import Image, ImageChops
    im = Image.open(out).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb:
        im = im.crop((max(bb[0] - 40, 0), max(bb[1] - 40, 0), min(bb[2] + 40, im.size[0]), min(bb[3] + 40, im.size[1])))
    im.save(out, optimize=True)
    log.write("saved %s\n" % out)
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
