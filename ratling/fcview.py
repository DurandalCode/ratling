# -*- coding: utf-8 -*-
"""
Showing Ratling parts in a FreeCAD document. Needs FreeCAD.

The document shows the unit as it stands: FreeCAD "Front" looks at the
machine's front (machine +Z towards the viewer), machine +X points up and
machine +Y to the left, where the crank is. Only the document objects are
turned; shapes, exports and checks stay in the machine frame of
ratling/params.py.
"""

import FreeCAD as App

VIEW_ROT = App.Placement(App.Matrix(0, -1, 0, 0,
                                    0, 0, -1, 0,
                                    1, 0, 0, 0,
                                    0, 0, 0, 1))

STEEL = (0.7, 0.7, 0.72)
# style name: (colour, transparency)
STYLES = {
    "stator": ((0.55, 0.75, 0.95), 65),
    "plate": ((0.85, 0.9, 0.95), 55),
    "rotor": ((0.95, 0.55, 0.15), 40),
    "shoe": ((0.15, 0.15, 0.15), 0),
    "frame": ((0.55, 0.8, 0.55), 30),
    "printed": ((0.9, 0.85, 0.6), 0),
    "steel": (STEEL, 0),
    "steel_ghost": (STEEL, 50),
    "hose": ((0.3, 0.55, 0.9), 30),
    "oring": ((0.85, 0.1, 0.1), 0),
    "flow": ((1.0, 0.0, 0.0), 0),
    "ghost": ((0.6, 0.6, 0.6), 88),
    "drive": ((0.5, 0.5, 0.55), 40),
}


class Scene:
    """A fresh document with groups of styled objects and labels."""

    def __init__(self, name):
        if name in App.listDocuments():
            App.closeDocument(name)
        self.doc = App.newDocument(name)
        self.groups = {}
        self.src = {}          # machine-frame shapes of the objects
        self._styles = []

    def group(self, name):
        if name not in self.groups:
            self.groups[name] = self.doc.addObject("App::DocumentObjectGroup", name)
        return self.groups[name]

    def add(self, group, name, shape, style, offset=None):
        if offset is not None:
            shape = shape.copy()
            shape.translate(offset)
        self.src[name] = shape
        shown = shape.copy()
        shown.Placement = VIEW_ROT.multiply(shown.Placement)
        o = self.doc.addObject("Part::Feature", name)
        o.Shape = shown
        self.group(group).addObject(o)
        self._styles.append((o, style))
        return o

    def label(self, group, text, pos):
        a = self.doc.addObject("App::Annotation", "Label")
        a.LabelText = [text]
        a.Position = VIEW_ROT.multVec(App.Vector(*pos))
        self.group(group).addObject(a)
        return a

    def finish(self, hidden_groups=(), opaque_groups=()):
        self.doc.recompute()
        if not App.GuiUp:
            return
        import FreeCADGui as Gui
        for o, style in self._styles:
            colour, transp = STYLES[style]
            o.ViewObject.ShapeColor = colour
            o.ViewObject.Transparency = transp
        for g in self.groups.values():
            for o in g.Group:
                if o.TypeId == "App::Annotation":
                    o.ViewObject.FontSize = 14
                    o.ViewObject.TextColor = (0.1, 0.1, 0.1)
                if g.Name in opaque_groups and hasattr(o.ViewObject, "Transparency"):
                    o.ViewObject.Transparency = 0
                if g.Name in hidden_groups:
                    o.ViewObject.Visibility = False
        Gui.activeDocument().activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")

    def show_only(self, groups, hide=()):
        for g in self.groups.values():
            for o in g.Group:
                o.ViewObject.Visibility = g.Name in groups
        for n in hide:
            self.doc.getObject(n).ViewObject.Visibility = False

    def snapshot(self, path, view="viewIsometric", w=1600, h=1200):
        """Save a screenshot; navigation animation is off while the camera moves."""
        import FreeCADGui as Gui
        pv = App.ParamGet("User parameter:BaseApp/Preferences/View")
        anim = pv.GetBool("UseNavigationAnimations", True)
        pv.SetBool("UseNavigationAnimations", False)
        try:
            v = Gui.getDocument(self.doc.Name).activeView()
            getattr(v, view)()
            Gui.updateGui()
            v.fitAll()
            Gui.updateGui()
            v.saveImage(path, w, h, "White")
        finally:
            pv.SetBool("UseNavigationAnimations", anim)
