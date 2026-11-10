# -*- coding: utf-8 -*-
"""
Ratling six-barrel pistol (hammer variant): every printed part, laid for the bed.

Builds pistol/hammer_assembly.py and writes each printed part as an STL in
its print orientation (the face named in PARTS on the bed, lowest point at
z = 0) to exports/pistol_build/stl/, and exports/pistol_build/parts.json:
name, file, print group, nozzle, size, volume, note. The groups are print
profiles; pistol/build/make_plates.sh lays each group on Bambu plates with
tools/print_plate.py, one project per group and nozzle.

The valve body and cap are Stage 3's own prints, listed here by reference:
v1.3's (module/stage3_v13.py, exports/stage3_qev_v13/) by default, the very
parts the v1.3 bench uses; v1.1's (exports/stage3_qev/) with VALVE = "v11".

Run inside FreeCAD:
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/pistol/build/export_parts.py').read())
"""

import json
import os
import sys

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
    "strong_supports": "--infill 60% --walls 5 --pattern gyroid --support",
    "standard": "--infill 30% --walls 4",
}

# Big plain parts go on the 0.8 nozzle (0.32 mm layer, half the walls): the grip, cage, side plate and strap print in
# about half the time and are no weaker. The rest stays on 0.4: airtight parts (the seal is proven there only), small
# moving parts and anything with a fit under ~0.5 mm (the detent bolt's 0.25 mm a side, the block's V-notches, the
# barrel bores).
NOZZLE_08 = {"frame_lower", "frame_upper", "frame_side_wall", "frame_side_band", "frame_right", "grip_left", "grip_right", "trigger_guard", "top_strap"}

# Parts whose pockets are bridged on the bed and print fine: the overhang limit in mm2 (the disc's six ramped notches)
BRIDGED = {"block_rear_disc": 600.0}

# name, shape, the part's direction that goes down onto the bed, group, note
PARTS = [
    ("lock_housing", lock_housing_h, -X_, "standard", "the lock's housing, no lock (only the shot's impulse passes, no standing pressure): a plain Ø16 through bore ending in the sleeve's nose, 0.3 mm off the hub; flat on the valve body, 2 x M3 x 30 self-tapping into its breech pilots (90 / 180 deg)"),
    ("block_rear_disc", hub, -X_, "standard", "breech seats on the bed; barrels glued 5 mm into it"),
    ("block_front_disc", front_plate, X_, "standard", "barrels glued into it"),
    ("sector", sector_base, -X_, "strong", "rear face on the bed (the tongue is its first layer), the ramped pawl tooth up, 6 mm tall; on the axle in front of the lock housing; the slider's pin in its arm"),
    ("slider", SLIDER_H, Y_, "strong_supports", "the bracket's outer face on the bed, 15 mm tall, on supports under the plate and the rod boss (on its x face it stood 54 mm tall and peeled off); runs"),
    ("detent_bolt", detent_bolt_print, X_, "strong", "V tip; a Ø4 pen spring behind it; flat on its x face; %.2f mm smaller than its channel a side (the first print would not go in)" % BOLT_CLEAR),
    ("detent_housing", detent_box, Y_, "strong", "with its bracket: 2 x M3 x 20 + nuts to the side plate"),
    ("hammer", hammer_body, Y_, "impact", "one part: hub, spur, sleeve, crank; turns on the Ø8 axle; crank pin Ø3 steel"),
    ("sector_spacer", sector_spacer, X_, "strong", "the ring on the tube between the sector and the QEV body; bore Ø25.6, the wedge is the pawl boss's road; file to fit the stack"),
    ("trigger", TRIGGER, Y_, "strong_supports", "pivot: M3 x 16 + nylock nut between the cage's cheeks; supports under the pad and the lug"),
    ("frame_lower", frame_lower, -X_, "supports", "the lower half: the slab (the QEV socket, the vent, the lock, the trigger) and the tail, on the bed; the tongues to the upper half"),
    ("frame_upper", frame_upper, -X_, "supports", "the upper half: the drum's top (the gauge, the vial, the strap's foot); the grooves to the lower half's tongues"),
    ("frame_side_wall", side_wall, -Y_, "standard", "joint face on the bed, no raft; the dovetail grooves open on the bed and widen upward; the band slides in from the rear"),
    ("frame_side_band", side_band, X_, "supports", "front end on the bed (the rear face is only the ball's tip): the cylinder's walls are vertical; supports only under the 5 bosses; 5 x ST2.9 x 16; slides onto the wall from the rear"),
    ("frame_right", side_plate_r, Y_, "supports", "cheek face down (0.5 proud of the drum, flat); the tunnels and the socket's mouth open sideways; Ø8 axle + 2 x M3 x 10 rear"),
    ("grip_left", grip_left, Y_, "supports", "cut face on the bed; the valve box's left half"),
    ("grip_right", grip_right, -Y_, "supports", "cut face on the bed; glued to the left on 3 x Ø3 x 12 dowels"),
    ("trigger_guard", guard, Y_, "supports", "flat; ST2.9 x 13 into its tab through the floor"),
    ("top_strap", top_strap, Z_, "strong", "top face down (on its side it stood on the nose disc, the bar 9 mm up); 2 x ST2.9 into the cage's top, the M6 stud through its foot"),
    ("nose_sleeve", nose, X_, "strong", "on the axle, front disc to the strap, with the washer"),
    ("axle_plug", axle_plug, X_, "airtight", "flange on the bed; in the axle's front end on a 19 x 2.5 O-ring; an M6 nut epoxied in its pocket"),
]
if FLEX_PAWL:                   # the pawl is a flexure tongue: the sector as it is, and one with a square tooth to file
    _i = [i_ for i_, p_ in enumerate(PARTS) if p_[0] == "sector"][0]
    PARTS[_i:_i + 1] = [
        ("sector", sector_base, -X_, "strong", "rear face on the bed (the tongue is its first layer), the ramped pawl tooth up (tip 2.7 mm past the hub face), 6 mm tall; on the axle in front of the lock housing; the slider's pin in its arm"),
        ("sector_blank", sector_base_blank, -X_, "strong", "the same with a SQUARE pawl tooth to file the ramp on by hand: the leading face (towards the drive) stays flat, the ramp goes on the other side")]
if not FLEX_PAWL:               # the pawl is a plunger in a boss on the sector, on a steel spring, closed by a plug
    _i = [i_ for i_, p_ in enumerate(PARTS) if p_[0] == "sector"][0]
    PARTS[_i:_i + 1] = [
        ("sector", sector_base, X_, "strong_supports", "front ring on the bed, the boss (with the pawl's channel, a tab of the ring's full thickness under it) up, on supports; on the axle in front of the lock housing; the slider's pin in its arm"),
        ("pawl", pawl_tooth, -X_, "strong", "the plunger: Ø6 body, a rigid 4.0 x 3.4 mm tooth (the ramp is in the disc's notch); its back face on the bed, the tooth up; in the sector's boss on a 0.5 x 6 x 10 mm steel spring (8 coils, from the 304 kit)"),
        ("pawl_plug", PAWL_PLUG, -X_, "strong", "closes the boss's rear behind the spring: pressed in and glued with CA")]
if not LOCKLESS:                # the old lock: a sleeve with a pusher behind its flange
    PARTS[0:1] = [("lock_housing", lock_housing_h, -X_, "airtight", "the lock's housing: flat on the valve body, 2 x M3 x 30 self-tapping into its breech pilots (90 / 180 deg)"),
                  ("lock_sleeve", lock_sleeve(1.0), X_, "airtight", "nose down (the sealing face on the bed, the flange chamfered over it); plain, no O-ring; the pusher glued to its flange"),
                  ("lock_pusher", pusher_shape(1.0), -X_, "strong", "ring behind the sleeve's flange; its cam pin: a Ø3 steel pin")]
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
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import orient_check
    native = os.path.join(BUILD, "native.stl")                  # the part as drawn: a better face to put down, named in its own axes
    MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.3).write(native)
    ranked = orient_check.search(native)
    cur_name = [k_ for k_, d_ in orient_check.AXES.items() if abs(d_[0] - down.x) + abs(d_[1] - down.y) + abs(d_[2] - down.z) < 1e-6][0]
    cur_score, cur_h = [(sc_, m_["height"]) for sc_, n_, m_ in ranked if n_ == cur_name][0]
    hint = None
    cand = [r_ for r_ in ranked if r_[2]["height"] <= 1.5 * cur_h]          # not a taller, thinner stand than now
    if cand and cand[0][0] < cur_score - 50 and cand[0][1] != cur_name:
        hint = "a better face down: %s (score %.0f, now %.0f)" % (cand[0][1], cand[0][0], cur_score)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.1)
    mesh.translate(0, 0, -mesh.BoundBox.ZMin)           # the shape's own bounding box is loose on curved faces: lay the mesh itself
    mesh.write(path)
    bb = s.BoundBox
    rows.append(dict(name=name, stl=os.path.relpath(path, REPO), group=group,
                     nozzle="0.8" if name in NOZZLE_08 else "0.4", note=note,
                     size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                     volume_cm3=round(s.Volume / 1000, 1), valid=s.isValid(), hint=hint))
for name, path, group, note in REFERENCE:
    rows.append(dict(name=name, stl=path, group=group, nozzle="0.4", note=note, size=None, volume_cm3=None, valid=True))
sys.path.insert(0, os.path.join(REPO, "tools"))
import orient_check                                     # the same check print_plate.py makes before it slices
for r in rows:
    if r["size"]:
        r["orientation"], r["orientation_note"] = orient_check.verdict(orient_check.measure(os.path.join(REPO, r["stl"])),
                                                                         "--support" in GROUPS[r["group"]], BRIDGED.get(r["name"]))
with open(os.path.join(BUILD, "parts.json"), "w") as f:
    json.dump(dict(groups=GROUPS, parts=rows), f, indent=1, ensure_ascii=False)
print("pistol build: %d parts" % len(rows))
for r in rows:
    print("  [%s] %-18s %-9s %s %-12s %s%s" % ({"OK": "OK ", "WARN": "WARN", "FAIL": "FAIL"}[r["orientation"]] if r.get("orientation") else "    ",
                                              r["name"], r["group"], r["nozzle"], "x".join("%.0f" % v_ for v_ in r["size"]) if r["size"] else "(ref)",
                                              "INVALID " if not r["valid"] else "", r.get("orientation_note", "") + ("  | HINT " + r["hint"] if r.get("hint") else "")))
big = [r["name"] for r in rows if r["size"] and max(r["size"][:2]) > 250]
print("  over 250 mm on the bed: %s" % (", ".join(big) if big else "none"))
