# -*- coding: utf-8 -*-
"""
Render a generator's model to a PNG, headless: for README pictures and for an agent to look at its own model.

Runs a generator in the FreeCAD GUI (it needs a display; on a VM use xvfb-run), hides the groups named in
HIDE, sets the view, saves the picture and crops the white margin.

    xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
        SCRIPT=module/stage3v4_coaxial_chamber.py OUT=docs/img/module_v44.png VIEW=iso HIDE=Labels,Jig,Section \
        freecad tools/render_view.py

SCRIPT ... generator, relative to the repo
OUT ...... PNG to write (relative to the repo, or absolute)
VIEW ..... iso (default), front, rear, top, bottom, left, right
HIDE ..... comma-separated group names (Name, not Label) to hide, e.g. Labels,Section
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
    exec(open(os.path.join(REPO, os.environ["SCRIPT"])).read(), {"REPO": REPO, "__name__": "__main__"})
    doc = App.ActiveDocument
    for name in filter(None, os.environ.get("HIDE", "").split(",")):
        g = doc.getObject(name)
        if g is None:
            log.write("no group %s\n" % name)
            continue
        for o in g.Group:
            o.ViewObject.Visibility = False
        g.ViewObject.Visibility = False
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
