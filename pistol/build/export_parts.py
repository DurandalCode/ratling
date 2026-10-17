# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol (hammer variant): every printed part, laid for the bed.

Builds pistol/hammer_assembly.py and writes each printed part as an STL in
its print orientation (the face named in PARTS on the bed, lowest point at
z = 0) to exports/pistol_build/stl/, and exports/pistol_build/parts.json:
name, file, print group, size, volume, note. The groups are print profiles;
pistol/build/make_plates.sh lays each group on Bambu plates with
tools/print_plate.py.

The v1.1 valve body and cap are Stage 3's own prints (module/stage3_qev.py,
exports/stage3_qev/); they are listed here by reference.

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/export_parts.py').read())
"""

import json
import os

import FreeCAD as App
import MeshPart

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

BUILD = os.path.join(REPO, "exports", "pistol_build")
STL = os.path.join(BUILD, "stl")
X_, Y_, Z_ = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

# Print groups (profiles): airtight = holds the shot's air; strong = moving and loaded parts; supports = parts
# with overhangs that need them; standard = the rest.
GROUPS = {
    "airtight": "--airtight --infill 100%",
    "strong": "--infill 60% --walls 5 --pattern gyroid",
    "supports": "--infill 40% --walls 4 --support",
    "standard": "--infill 30% --walls 4",
}

# name, shape, the part's direction that goes down onto the bed, group, note
PARTS = [
    ("lock_housing", lock_housing_h, -X_, "airtight", "the lock's housing: 3 x M3 to the v1.1 body, O-ring face"),
    ("lock_sleeve", lock_sleeve(1.0), -X_, "airtight", "11/16 x 1/8 O-ring on it; the pusher glued to its flange"),
    ("lock_pusher", pusher_shape(1.0), -X_, "strong", "ring behind the sleeve's flange; its cam pin: a Ø3 steel pin"),
    ("block_rear_disc", hub, -X_, "standard", "breech seats on the bed; barrels glued 5 mm into it"),
    ("block_front_disc", front_plate, X_, "standard", "barrels glued into it"),
    ("sector", sector_base, -X_, "strong", "on the axle in front of the lock housing; the slider's pin in its arm"),
    ("pawl", pawl_tooth, -X_, "strong", "the sector's sprung tooth (a Ø3 pen spring behind it)"),
    ("slider", SLIDER_H, -Y_, "strong", "runs on the Ø3 guide rod; its pin (Ø3 steel) in the sector's arm"),
    ("detent_bolt", bolt_shape(0.0), Z_, "strong", "V tip; a Ø4 pen spring behind it"),
    ("detent_housing", detent_box, Y_, "strong", "with its bracket: 2 x M3 x 12 + nuts to the side plate"),
    ("hammer", hammer_body, Y_, "supports", "one part: hub, spur, sleeve, crank; turns on the Ø8 axle; crank pin Ø3 steel"),
    ("trigger", TRIGGER, Y_, "strong", "pivot: M3 x 16 + nylock nut between the cage's cheeks"),
    ("frame_cage", frame, Y_, "supports", "right wall on the bed; supports under the cheeks and the spring rib"),
    ("frame_side_plate", side_plate, -Y_, "standard", "outer face on the bed; 6 x ST2.9 x 13 into the cage"),
    ("grip_left", grip_left, Y_, "standard", "cut face on the bed; the valve box's left half"),
    ("grip_right", grip_right, -Y_, "standard", "cut face on the bed; glued to the left on 3 x Ø3 x 12 dowels"),
    ("trigger_guard", guard, Y_, "standard", "flat; ST2.9 x 13 into its tab through the floor"),
    ("top_strap", top_strap, Y_, "strong", "on its side; 2 x ST2.9 into the cage's top, the M6 stud through its foot"),
    ("nose_sleeve", nose, X_, "strong", "on the axle, front disc to the strap, with the washer"),
    ("axle_plug", axle_plug, -X_, "strong", "epoxied flush into the axle's front end; an M6 nut epoxied in its pocket"),
]
REFERENCE = [("v1.1_body", "exports/stage3_qev/body.stl", "airtight", "Stage 3 v1.1 body (module/stage3_qev.py)"),
             ("v1.1_cap", "exports/stage3_qev/cap.stl", "airtight", "Stage 3 v1.1 cap")]


def laid(shape, down):
    s = shape.copy()
    s.rotate(V(0, 0, 0), App.Rotation(V(down), -Z_).Axis, math.degrees(App.Rotation(V(down), -Z_).Angle))
    bb = s.BoundBox
    s.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, -bb.ZMin))
    return s


os.makedirs(STL, exist_ok=True)
rows = []
for name, shape, down, group, note in PARTS:
    s = laid(shape, down)
    path = os.path.join(STL, name + ".stl")
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1).write(path)
    bb = s.BoundBox
    rows.append(dict(name=name, stl=os.path.relpath(path, REPO), group=group, note=note,
                     size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                     volume_cm3=round(s.Volume / 1000, 1), valid=s.isValid()))
for name, path, group, note in REFERENCE:
    rows.append(dict(name=name, stl=path, group=group, note=note, size=None, volume_cm3=None, valid=True))
with open(os.path.join(BUILD, "parts.json"), "w") as f:
    json.dump(dict(groups=GROUPS, parts=rows), f, indent=1, ensure_ascii=False)
print("pistol build: %d parts" % len(rows))
for r in rows:
    print("  %-18s %-9s %-22s %s" % (r["name"], r["group"], "x".join("%.0f" % v_ for v_ in r["size"]) if r["size"] else "(ref)",
                                     "" if r["valid"] else "INVALID"))
big = [r["name"] for r in rows if r["size"] and max(r["size"][:2]) > 250]
print("  over 250 mm on the bed: %s" % (", ".join(big) if big else "none"))
