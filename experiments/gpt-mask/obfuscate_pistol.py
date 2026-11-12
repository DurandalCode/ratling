# -*- coding: utf-8 -*-
"""
Pistol-only geometry obfuscation for the Mechanismus work tree. Pure Python text transforms.

Applied on `out` after the live→neutral rename. GPT must not see a quick-exhaust stack, six
barrel tubes or an internal hose network; the housing generators stay editable. Files listed as
context are rewritten freely and never taken back by `in`.
"""

from __future__ import print_function

import re

# Live-repo paths (before rename).
CONTEXT = (
    "module/stage3_qev.py",
    "pistol/mech_layout.py",
    "pistol/hammer_layout.py",
)
EDITABLE = (
    "pistol/hammer_assembly.py",
)

_STAGE3_SOLID = """
# --- solid stack, no passages ---------------------------------
body = cyl(BODY_R, 0, BODY_H).fuse(cyl(r2, 0, BODY_H, C)).fuse(hull).removeSplitter()
cap = cyl(BODY_R, 0, CAP_T).removeSplitter()
cap_flat = cap
cap_a = cap.copy()
cap_a.translate(V(0, 0, -CAP_T))
# --- end solid stub -------------------------------------------------------
"""

_BLOCK_SOLID = """
# --- solid drum ---------------------------
barrels = cyl_x(2 * HUB_R, HUB_X0 + HUB_SEAT, HUB_X0 + HUB_T + STUB).cut(
    cyl_x(BARREL_OD + 0.6, HUB_X0 + HUB_SEAT - 1, HUB_X0 + HUB_T + STUB + 1))
oring_faces = Part.makeCompound([])
front_plate = cyl_x(2 * HUB_R - 6, HUB_X0 + HUB_T + STUB - FRONT_T, HUB_X0 + HUB_T + STUB).cut(
    cyl_x(BARREL_OD + 0.6, 0, 300))
hub = cyl_x(2 * HUB_R, HUB_X0, HUB_X0 + HUB_T).cut(cyl_x(BARREL_OD + 0.6, HUB_X0 - 1, HUB_X0 + HUB_T + 1))
block = Part.makeCompound([hub, barrels, front_plate])
# --- end solid stub -------------------------------------------------------
"""

_AIR_WIRES = """
# --- external wires only --------------
r_end, r_dir = vent_port("R")
a_end, a_dir = vent_port("A")
pilot_exit = Part.makeCylinder(2.5, 20.0, a_end - a_dir * 0.5, a_dir)
frame = frame.cut(pilot_exit)
hose = Part.makeCylinder(1.5, 45.0, r_end + r_dir * 4.0, r_dir)
pilot_line = Part.makeCylinder(1.0, 40.0, a_end + a_dir * 4.0, a_dir)
gauge_line = Part.makeCylinder(1.0, 35.0, V(-30.0, -42.0, 15.0), -YA)
tee = Part.makeSphere(0.01, V(0, 0, 0))
supply_line = hose
air_cut = Part.makeBox(0.1, 0.1, 0.1, V(900, 900, 900))
TEE = V(-86, 0, -27.3)
# --- end solid stub -------------------------------------------------------
"""


def _replace_once(text, pattern, repl, label):
    new, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        raise ValueError("obfuscate_pistol: %s: expected 1 match, got %d" % (label, n))
    return new


def obfuscate_stage3(text):
    """Overwrite hollow body/cap with a solid envelope right after they are built."""
    return _replace_once(
        text,
        r"(cap_a\.translate\(V\(0, 0, -CAP_T\)[^\n]*\n)",
        r"\1" + _STAGE3_SOLID.lstrip("\n"),
        "stage3 solid stack",
    )


def obfuscate_mech_layout(text):
    """Replace the six-tube block with one solid drum."""
    return _replace_once(
        text,
        r"\nhub = cyl_x\(2 \* HUB_R, HUB_X0, HUB_X0 \+ HUB_T\).*?\nblock = Part\.makeCompound\(\[hub, barrels, front_plate\]\)\n",
        "\n" + _BLOCK_SOLID.lstrip("\n") + "\n",
        "mech_layout solid drum",
    )


def obfuscate_air(text):
    """Drop internal hose routing; leave short wires outside the shell."""
    return _replace_once(
        text,
        r"\n# -+ air:.*?\nair_cut = pipe_along\(supply_pts, 3\.6\).*?\n",
        "\n" + _AIR_WIRES.lstrip("\n") + "\n",
        "hammer_assembly external wires",
    )


def apply(rel, text):
    """Return obfuscated text for a live-repo relative path, or text unchanged."""
    if rel == "module/stage3_qev.py":
        return obfuscate_stage3(text)
    if rel == "pistol/mech_layout.py":
        return obfuscate_mech_layout(text)
    if rel == "pistol/hammer_assembly.py":
        return obfuscate_air(text)
    return text


def is_context(rel):
    return rel in CONTEXT


def is_editable(rel):
    return rel in EDITABLE
