# -*- coding: utf-8 -*-
"""
Render a generator's model to a PNG, headless: for README pictures and for an agent to look at its own model.

Runs a generator in the FreeCAD GUI (it needs a display; on a VM use xvfb-run), hides the groups named in
HIDE, or keeps only the solids named in PARTS, sets the view, saves the picture and crops the white margin.

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        SCRIPT=module/stage3v4_coaxial_chamber.py OUT=docs/img/module_v44.png VIEW=iso HIDE=Labels,Jig,Section \
        freecad tools/render_view.py

    xvfb-run -a -s "-screen 0 1600x1000x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        SCRIPT=pistol/hammer_assembly.py OUT=/tmp/side.png VIEW=front \
        PARTS=Frame_side,Frame_side_band CHECKS=0 \
        freecad tools/render_view.py

SCRIPT ... generator, relative to the repo
OUT ...... PNG to write (relative to the repo, or absolute)
VIEW ..... iso (default), front, rear, top, bottom, left, right
HIDE ..... comma-separated group names (Name, not Label) to hide, e.g. Labels,Section
PARTS .... comma-separated solid names to keep. Other solids are hidden; their groups stay visible,
           because hiding a group hides its children and the frame comes out white
CHECKS ... passed into the generator when set (0 or 1). The pistol's sweep stays off for a picture
SIZE ..... WxH before cropping, default 2400x1500
FreeCAD stays open in the GUI unless the script ends it, so this one ends it itself; errors go to OUT + ".log".
"""

import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(REPO, os.environ["OUT"])
log = open(out + ".log", "w")
try:
    ns = {"REPO": REPO, "__name__": "__main__"}
    if "CHECKS" in os.environ:
        ns["CHECKS"] = os.environ["CHECKS"].strip().lower() in ("1", "true", "yes")
    exec(open(os.path.join(REPO, os.environ["SCRIPT"])).read(), ns)
    doc = App.ActiveDocument
    for name in filter(None, os.environ.get("HIDE", "").split(",")):
        g = doc.getObject(name)
        if g is None:
            log.write("no group %s\n" % name)
            continue
        for o in g.Group:
            o.ViewObject.Visibility = False
        g.ViewObject.Visibility = False
    wanted = [n.strip() for n in os.environ.get("PARTS", "").split(",") if n.strip()]
    if wanted:
        found = set()
        for o in doc.Objects:
            if getattr(o, "TypeId", "") != "Part::Feature":
                continue
            vo = getattr(o, "ViewObject", None)
            if vo is None:
                continue
            show = o.Name in wanted
            vo.Visibility = show
            if not show:
                continue
            found.add(o.Name)
            parent = o
            while True:
                groups = [q for q in parent.InList if getattr(q, "TypeId", "") == "App::DocumentObjectGroup"]
                if not groups:
                    break
                parent = groups[0]
                pv = getattr(parent, "ViewObject", None)
                if pv is not None:
                    pv.Visibility = True
        for name in wanted:
            if name not in found:
                log.write("no part %s\n" % name)
        log.write("parts %s\n" % ", ".join(sorted(found)))
    Gui.updateGui()
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    {"iso": view.viewIsometric, "front": view.viewFront, "rear": view.viewRear, "top": view.viewTop,
     "bottom": view.viewBottom, "left": view.viewLeft, "right": view.viewRight}[os.environ.get("VIEW", "iso")]()
    view.fitAll()
    Gui.updateGui()
    w, h = map(int, os.environ.get("SIZE", "2400x1500").split("x"))
    view.saveImage(out, w, h, "White")
    from PIL import Image, ImageChops
    im = Image.open(out).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb:
        m = 40
        im = im.crop((max(bb[0] - m, 0), max(bb[1] - m, 0), min(bb[2] + m, w), min(bb[3] + m, h)))
    im.save(out, optimize=True)
    log.write("saved %s\n" % out)
except Exception:
    log.write(traceback.format_exc())
log.close()
os._exit(0)
