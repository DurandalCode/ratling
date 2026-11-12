# -*- coding: utf-8 -*-
"""
Run part edits: edits/<stem>.py, each defining

    def edit(part, ctx):
        # part: Part.Shape of this part; ctx: {stem: Part.Shape} of the parts around it (read-only)
        return part.makeFillet(2.0, part.Edges[:4])        # any FreeCAD Part operations

The same runner builds the work folder's model and the real assembly, so an edit means the same
thing on both sides. Parts are copied before the call; ctx holds the unedited neighbours.
Every result is checked: a valid shape, the same number of solids, and a volume between half and
one and a half times the original (an edit reshapes a part; it does not replace it).
"""

from __future__ import print_function

import os

import Part


class EditError(Exception):
    pass


def load(path):
    g = {"__name__": "part_edit", "__file__": path}
    with open(path, "r", encoding="utf-8") as f:
        code = compile(f.read(), path, "exec")
    exec(code, g)
    fn = g.get("edit")
    if not callable(fn):
        raise EditError("%s: no edit(part, ctx) function" % path)
    return fn


def volume(shape):
    return sum(s.Volume for s in shape.Solids)


def check(stem, before, after):
    if not isinstance(after, Part.Shape) or after.isNull():
        raise EditError("%s: edit() must return a Part.Shape" % stem)
    if not after.isValid():
        raise EditError("%s: result is not a valid shape" % stem)
    if len(after.Solids) != len(before.Solids):
        raise EditError("%s: %d solid(s) before, %d after" % (stem, len(before.Solids), len(after.Solids)))
    v0, v1 = volume(before), volume(after)
    if v1 <= 0:
        raise EditError("%s: result has no volume" % stem)
    if not 0.5 * v0 <= v1 <= 1.5 * v0:
        raise EditError("%s: volume %.0f -> %.0f is outside 50%%..150%% of the original" % (stem, v0, v1))


def apply(edits_dir, parts, sees=None, editable=None):
    """Apply every edits/<stem>.py to parts[stem]; return ({stem: new shape}, [report lines]).

    sees maps a stem to the stems its ctx may hold (None: every other part).
    editable limits which stems may be edited (None: all).
    """
    out, report = {}, []
    if not edits_dir or not os.path.isdir(edits_dir):
        return out, report
    for name in sorted(os.listdir(edits_dir)):
        if not name.endswith(".py"):
            continue
        stem = name[:-3]
        path = os.path.join(edits_dir, name)
        if stem not in parts or (editable is not None and stem not in editable):
            report.append("skip %s: no such editable part here" % name)
            continue
        names = None if sees is None else sees.get(stem)
        ctx = {k: v.copy() for k, v in parts.items() if k != stem and (names is None or k in names)}
        before = parts[stem]
        try:
            after = load(path)(before.copy(), ctx)
        except EditError:
            raise
        except Exception as e:
            raise EditError("%s: %s: %s" % (name, type(e).__name__, e))
        check(stem, before, after)
        out[stem] = after
        report.append("edit %s: volume %.0f -> %.0f" % (stem, volume(before), volume(after)))
    return out, report
