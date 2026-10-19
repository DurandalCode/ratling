# -*- coding: utf-8 -*-
"""
Ratling mitrailleuse concepts: pictures of mitrailleuse_concepts.py.

Builds the four variants, then saves for each one a view from behind on the
right (firing head or breech disc, crank), one from the front on the left,
one from the muzzle and one from the right, plus all four side by side. Writes
exports/mitrailleuse_concepts/<tag>_<view>.jpg.

Run inside FreeCAD (GUI):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/mitrailleuse/concepts_renders.py').read())
"""

import os

import FreeCAD as App
import FreeCADGui as Gui
from PIL import Image, ImageChops

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "mitrailleuse", "mitrailleuse_concepts.py"), encoding="utf-8").read())

OUT = os.path.join(REPO, "exports", NAME)
os.makedirs(OUT, exist_ok=True)
# The pictures are taken in the gun's own frame, not fcview's: X forward (muzzle), Y to the gunner's left, Z up.
SHOT = App.Placement(App.Matrix(0, 0, 1, 0,
                                0, -1, 0, 0,
                                1, 0, 0, 0,
                                0, 0, 0, 1))
for o in doc.Objects:
    if o.Name in sc.src:
        s = sc.src[o.Name].copy()
        s.Placement = SHOT.multiply(s.Placement)
        o.Shape = s
doc.recompute()
# camera looking along these directions, Z up
VIEWS = {"rear": (0.62, 0.62, -0.48), "front": (-0.62, -0.62, -0.42), "muzzle": (-1.0, 0.0, 0.0),
         "side": (0.0, 1.0, 0.0)}


def camera(direction):
    d = App.Vector(*direction).normalize()
    zc = d.negative()
    up = App.Vector(0, 0, 1)
    if abs(zc.dot(up)) > 0.99:
        up = App.Vector(0, 1, 0)
    xc = up.cross(zc).normalize()
    yc = zc.cross(xc)
    m = App.Matrix(xc.x, yc.x, zc.x, 0, xc.y, yc.y, zc.y, 0, xc.z, yc.z, zc.z, 0, 0, 0, 0, 1)
    return App.Rotation(m)


def snap(file, view, width=1100):
    v = Gui.getDocument(doc.Name).activeView()
    v.setCameraType("Orthographic")
    v.setCameraOrientation(camera(view))
    Gui.updateGui()
    v.fitAll()
    Gui.updateGui()
    tmp = os.path.join(OUT, "_tmp.png")
    v.saveImage(tmp, 1600, 1200, "White")
    im = Image.open(tmp).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    bb = (max(bb[0] - 24, 0), max(bb[1] - 24, 0), min(bb[2] + 24, im.width), min(bb[3] + 24, im.height))
    c = im.crop(bb)
    if c.width > width:
        c = c.resize((width, int(c.height * width / c.width)), Image.LANCZOS)
    c.save(os.path.join(OUT, file + ".jpg"), quality=86)
    os.remove(tmp)


for tag, group, _, _ in VARIANTS:
    sc.show_only([group])
    for vn in ("rear", "front", "muzzle", "side"):
        snap("%s_%s" % (tag, vn), VIEWS[vn])
sc.show_only([g for _, g, _, _ in VARIANTS])
snap("all_rear", VIEWS["rear"], 1600)
print("renders written to", OUT)
