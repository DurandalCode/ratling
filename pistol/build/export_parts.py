# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol (hammer variant): every printed part, laid for the bed.

Builds pistol/hammer_assembly.py and writes each printed part as an STL in
its print orientation (the face named in PARTS on the bed, lowest point at
z = 0) to exports/pistol_build/stl/, and exports/pistol_build/parts.json:
name, file, print group, size, volume, note. The groups are print profiles;
pistol/build/make_plates.sh lays each group on Bambu plates with
tools/print_plate.py.

The valve body and cap are Stage 3's own prints, listed here by reference:
v1.3's (module/stage3_v13.py, exports/stage3_qev_v13/) by default, the very
parts the v1.3 bench uses; v1.1's (exports/stage3_qev/) with VALVE = "v11".

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
try:
    VALVE                       # set before exec ("v11") to export the build round the old valve
except NameError:
    VALVE = "v13"               # the same body and cap as module/stage3_v13.py: one print serves the bench and the pistol
exec(open(os.path.join(REPO, "pistol", "hammer_assembly.py")).read())

BUILD = os.path.join(REPO, "exports", "pistol_build")
STL = os.path.join(BUILD, "stl")
X_, Y_, Z_ = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

# Print groups (profiles): airtight = holds the shot's air (6 walls seal it; 60 % gyroid is what Stage 3 v1.1
# held 2 bar on, 100 % adds nothing at ~1 MPa wall stress); strong = moving and loaded parts; impact = the hammer:
# 6 walls, on supports; supports = parts with overhangs that need them; standard = the rest.
GROUPS = {
    "airtight": "--airtight --infill 60% --pattern gyroid",
    "strong": "--infill 60% --walls 5 --pattern gyroid",
    "impact": "--infill 40% --walls 6 --support",
    "supports": "--infill 40% --walls 4 --support",
    "standard": "--infill 30% --walls 4",
}

# name, shape, the part's direction that goes down onto the bed, group, note
PARTS = [
    ("lock_housing", lock_housing_h, -X_, "airtight", "the lock's housing: flat on the valve body, 2 x M3 x 30 self-tapping into its breech pilots (90 / 180 deg)"),
    ("lock_sleeve", lock_sleeve(1.0), X_, "airtight", "nose down (the sealing face on the bed, the flange chamfered over it); plain, no O-ring; the pusher glued to its flange"),
    ("lock_pusher", pusher_shape(1.0), -X_, "strong", "ring behind the sleeve's flange; its cam pin: a Ø3 steel pin"),
    ("block_rear_disc", hub, -X_, "standard", "breech seats on the bed; barrels glued 5 mm into it"),
    ("block_front_disc", front_plate, X_, "standard", "barrels glued into it"),
    ("sector", sector_base, -X_, "strong", "on the axle in front of the lock housing; the slider's pin in its arm"),
    ("pawl", pawl_tooth, -X_, "strong", "the sector's sprung tooth (a Ø3 pen spring behind it)"),
    ("slider", SLIDER_H, -Y_, "strong", "runs on the Ø3 guide rod; its pin (Ø3 steel) in the sector's arm"),
    ("detent_bolt", turned(bolt_shape(0.0), -(DETENT_ANGLE + 90)), Y_, "strong", "V tip; a Ø4 pen spring behind it; on its side (it is drawn turned to the detent's angle)"),
    ("detent_housing", detent_box, Y_, "strong", "with its bracket: 2 x M3 x 12 + nuts to the side plate"),
    ("hammer", hammer_body, Y_, "impact", "one part: hub, spur, sleeve, crank; turns on the Ø8 axle; crank pin Ø3 steel"),
    ("trigger", TRIGGER, Y_, "strong", "pivot: M3 x 16 + nylock nut between the cage's cheeks"),
    ("frame_cage", frame, Y_, "supports", "right wall on the bed; supports under the cheeks and the spring rib"),
    ("frame_side_plate", side_plate, -Y_, "standard", "outer face on the bed; 6 x ST2.9 x 13 into the cage"),
    ("grip_left", grip_left, Y_, "standard", "cut face on the bed; the valve box's left half"),
    ("grip_right", grip_right, -Y_, "standard", "cut face on the bed; glued to the left on 3 x Ø3 x 12 dowels"),
    ("trigger_guard", guard, Y_, "standard", "flat; ST2.9 x 13 into its tab through the floor"),
    ("top_strap", top_strap, Z_, "strong", "top face down (on its side it stood on the nose disc, the bar 9 mm up); 2 x ST2.9 into the cage's top, the M6 stud through its foot"),
    ("nose_sleeve", nose, X_, "strong", "on the axle, front disc to the strap, with the washer"),
    ("axle_plug", axle_plug, -X_, "strong", "epoxied flush into the axle's front end; an M6 nut epoxied in its pocket"),
]
_ref = "exports/stage3_qev_v13" if VALVE == "v13" else "exports/stage3_qev"
REFERENCE = [(VALVE + "_body", _ref + "/body.stl", "airtight", "Stage 3 %s body (module/stage3_qev.py)" % VALVE),
             (VALVE + "_cap", _ref + "/cap.stl", "airtight", "Stage 3 %s cap" % VALVE)]


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
