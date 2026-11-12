# -*- coding: utf-8 -*-
"""
Build the live pistol assembly once and dump solids into GPT-mask fixtures:

  A/B/C  — housing-only .brep (real cutouts)
  D      — full mechanism + housing, filenames already obfuscated

Monorepo only. Do not put this file in a GPT extract.

    export LANG=C.UTF-8 LC_ALL=C.UTF-8
    freecadcmd -c "REPO='$PWD'; exec(open('experiments/gpt-mask/pull_real_shell.py').read())"
"""

from __future__ import print_function

import os
import shutil

import FreeCAD as App

try:
    REPO
except NameError:
    REPO = os.getcwd()

MASK = os.path.join(REPO, "experiments", "gpt-mask")
SHELL_FIXTURES = ("A_actuator_shell", "B_frame_hammer", "C_six_rotor")

# variable in hammer_assembly namespace → brep stem for A/B/C
SHELL_PARTS = (
    ("frame_lower", "shell_lower"),
    ("frame_upper", "shell_upper"),
    ("side_wall", "side_left_wall"),
    ("side_band", "side_left_band"),
    ("side_plate_r", "side_right"),
    ("grip_left", "grip_left"),
    ("grip_right", "grip_right"),
    ("guard", "bail"),
    ("detent_box", "detent_box"),
)

# Full mechanism for D: (source, brep stem). source is a name in ns, or
# ("rest", "Key") to take rest["Key"] after pose(REST).
D_PARTS = (
    ("frame_lower", "tray"),
    ("frame_upper", "lid"),
    ("side_wall", "left_wall"),
    ("side_band", "left_band"),
    ("side_plate_r", "right_cover"),
    ("grip_left", "grip_l"),
    ("grip_right", "grip_r"),
    ("guard", "bail"),
    ("detent_box", "index_box"),
    ("valve_body", "stack_body"),
    ("valve_cap", "stack_cap"),
    ("lock_housing_h", "coupler"),
    ("axle", "spindle"),
    ("block", "rotor"),
    (("rest", "Sector"), "sector"),
    (("rest", "Slider"), "yoke"),
    (("rest", "Hammer"), "lever"),
    (("rest", "Trigger"), "pedal"),
    (("rest", "Pawl"), "click_tooth"),  # may be absent if FLEX_PAWL
    (("rest", "Pin"), "yoke_pin"),
    (("rest", "Bolt"), "index_bolt"),
    ("mini_valves", "limit_switch"),
    ("mainsprings", "return_springs"),
    ("shaft", "lever_axle"),
    ("guide_rod", "yoke_rod"),
    ("hose", "cable"),
    ("pilot_line", "signal_wire"),
    ("gauge_line", "sense_wire"),
    ("tee", "wire_tee"),
    ("valve_rods", "stack_ties"),
    ("lock_bolts", "coupler_screws"),
    ("sector_spacer", "sector_ring"),
    ("top_strap", "rotor_strap"),
    ("nose", "spindle_nose"),
    ("axle_plug", "spindle_plug"),
    ("washer", "thrust_washer"),
)

CHECKS = False
VALVE = "v13"
print("pull_real_shell: building pistol/hammer_assembly.py (CHECKS=False)…", flush=True)
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())
ns = globals()


def resolve(src):
    if isinstance(src, tuple):
        bag, key = src
        d = ns[bag]
        if key not in d:
            return None
        return d[key]
    if src not in ns:
        return None
    return ns[src]


def write_brep(shape, path):
    shape.exportBrep(path)
    vol = sum(s.Volume for s in shape.Solids) if shape.Solids else 0.0
    print("  %s  vol=%.0f" % (os.path.basename(path), vol), flush=True)


missing = [src for src, _ in SHELL_PARTS if resolve(src) is None]
if missing:
    raise SystemExit("missing shell shapes: %s" % ", ".join(str(m) for m in missing))
if resolve("block") is None:
    raise SystemExit("missing block")

tmp = os.path.join(MASK, "_parts_tmp")
if os.path.isdir(tmp):
    shutil.rmtree(tmp)
os.makedirs(tmp)

for src, stem in SHELL_PARTS:
    write_brep(resolve(src), os.path.join(tmp, stem + ".brep"))
write_brep(resolve("block"), os.path.join(tmp, "rotor_hub.brep"))

for fix in SHELL_FIXTURES:
    dest = os.path.join(MASK, fix, "parts")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for _, stem in SHELL_PARTS:
        shutil.copy2(os.path.join(tmp, stem + ".brep"), os.path.join(dest, stem + ".brep"))
    if fix == "C_six_rotor":
        shutil.copy2(os.path.join(tmp, "rotor_hub.brep"), os.path.join(dest, "rotor_hub.brep"))
    print("wrote %s/parts/" % fix, flush=True)

# --- fixture D: full mechanism, obfuscated stems --------------------------------
d_dir = os.path.join(MASK, "D_full_mech", "parts")
if os.path.isdir(d_dir):
    shutil.rmtree(d_dir)
os.makedirs(d_dir)
for src, stem in D_PARTS:
    shape = resolve(src)
    if shape is None:
        print("  skip %s (not in this build)" % stem, flush=True)
        continue
    write_brep(shape, os.path.join(d_dir, stem + ".brep"))
print("wrote D_full_mech/parts/", flush=True)

shutil.rmtree(tmp)
if "pistol_hammer_assembly" in App.listDocuments():
    App.closeDocument("pistol_hammer_assembly")
print("pull_real_shell: done")
