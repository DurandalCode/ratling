# -*- coding: utf-8 -*-
"""
Joint audit of the gatling breech mechanism (separate run, like the sweep).

Builds gatling/breech_mechanism.py once as a library (BREECH_MECH_LIBRARY), splits the
model into named bodies (two stations broken into their parts: the one at FIRE on the
ramp and the one at LOAD under the feed; every fixed and pack part; the gear trains and
the crank in their rest pose), and measures every pair: contact (closer than CONTACT)
and overlap (common volume). Each contact must be either

- fastened: a fastener of the model (M3 bolt, M6 stud, the QEV tie studs, a bought
  part's M4) runs through both parts (it is within FAST_NEAR of each), or
- declared in JOINTS below: what holds the pair or why nothing has to (a slide, a
  bearing, a mesh, a D-flat, a socket, a push-in fitting, the QEV stack, ...).

An undeclared contact is a part that only "stands on" its neighbour: [FAIL]. So is an
overlap (common volume) that is not declared as a press fit or a squeeze, and a body that
touches nothing and is not in FREE (2026-11-21: the feed head had dropped out of the model and
the cup and the TPU lip floated, listed but not failed).

AXIAL (2026-11-21): the parts on shafts and pins, the shafts and pins themselves and a few
captured parts are pushed along their axes both ways until they meet another body; the play
must stay within AXIAL_MAX (the owner: "about 1 mm").

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_joints.py').read())"

JOINTS_CACHE (environment) = a directory: the bodies and fasteners are written there once
(BREP + names) and read back on the next run, so the table can be reworked without
rebuilding the mechanism (~3 min). Report:
exports/gatling_breech_mechanism/gatling_breech_mechanism_joints.txt
"""
import fnmatch
import json
import os
import re
import time

import FreeCAD as App
import Part

try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")

CONTACT = 0.2          # mm: closer than this is a contact (a seat, not a running gap)
OVERLAP = 0.05         # mm3: more common volume than this is an overlap
FAST_NEAR = 0.35       # mm: a fastener this close to both parts runs through both
CACHE = os.environ.get("JOINTS_CACHE", "")
_t0 = time.time()

# (pattern a, pattern b, how the pair is held). Names: station parts as "st.Name",
# multi-solid bodies without their ".N". "press" in the text allows an overlap.
JOINTS = [
    # --- station: the QEV stack on its two M3 tie studs (counted as fasteners), what sits in it
    ("st.Diaphragm", "st.*", "diaphragm squeezed in the QEV stack (press)"),
    ("st.Barrel_stub", "st.*", "stub captured in the QEV stack"),
    ("st.Chamber_tube", "st.*", "chamber tube captured in the QEV stack"),
    ("st.Pilot_fitting", "st.Rear_plug", "G1/8 thread (press)"),
    ("st.Front_yoke", "st.Front_cover", "QEV stack: the tie studs pull the yoke onto the cover"),
    ("st.Seat_ring", "st.Rear_plug", "QEV stack: the seat ring in the plug, the tie studs hold it"),
    ("st.Pilot_fitting", "st.Line_A", "push-in fitting (press)"),
    ("st.AirTAC_fittings", "st.AirTAC", "R1/8 thread"),
    ("st.AirTAC_fittings", "st.Line_*", "push-in fitting (press)"),
    ("st.Line_*", "st.Line_*", "one hose (press)"),
    ("st.Line_R", "Lines_in_axle", "the line runs on inside the axle (press)"),
    ("st.Line_R", "Pack_axle", "through its window"),
    ("st.AirTAC_plunger", "st.AirTAC", "its plunger"),
    ("st.AirTAC_plunger", "Firing_ramp", "the fixed ramp presses it (press)"),
    ("st.Finger", "st.Valve_bracket", "Ø5 pin pressed in a blind hole, the groove floor 0.3 past its tip (press)"),
    ("st.Finger", "Liner_half_*", "finger in the groove"),
    ("st.Carriage", "st.Rails", "slides on the rails"),
    ("st.Nose_clamp", "st.Rails", "slides on the rails"),
    ("st.Nose_clamp", "st.Nose_clamp", "the halves: 2 x M3 x 20"),
    ("st.Front_cover", "st.Barrel", "fitting in the barrel, closed"),
    ("st.Front_cover", "Pack_hub", "QEV on the breech clamp's stop face, closed"),
    ("st.Front_cover", "st.Breech_clamp_upper", "QEV on the stop face, closed"),
    ("st.Barrel", "st.Breech_clamp_upper", "clamped in the split clamp"),
    ("st.Barrel", "Pack_hub", "clamped (the lower halves are in the hub)"),
    ("st.Barrel", "Muzzle_plate", "pinched (M3 x 20 across a slit)"),
    ("st.Rails", "Pack_hub", "blind sockets in the clamp feet"),
    ("st.Rails", "Rear_rail_disk", "blind sockets"),
    # --- pack: bearings, the axle, the air
    ("Front_bearing_61836", "Pack_hub", "inner race on its seat and shoulder"),
    ("Front_bearing_61836", "Inner_race_retainer", "inner race under the retainer"),
    ("Front_bearing_61836", "Bearing_housing", "outer race in the housing, under its lip"),
    ("Front_bearing_61836", "Outer_race_retainer", "outer race on the retainer"),
    ("Bearings_6808", "Bearing_*", "outer race in its disk's seat between the disk's lip and the retainer's spigot (press)"),
    ("Bearings_6808", "*_6808_retainer", "the retainer's spigot on the outer race"),
    ("Bearings_6808", "Axle_collars", "collar lips on the front 6808's inner race"),
    ("Axle_collars", "Pack_axle", "split collars clamped, an M3 x 20 across each slit"),
    ("Rear_rail_disk", "Pack_axle", "split hub clamped, an M3 x 20 across its slit"),
    ("Soft_coupling", "Pack_axle", "clamped, an M3 x 20 across its slit; the axle's end on its neck (press)"),
    ("Lines_in_axle", "Soft_coupling", "the lines pass it"),
    ("Lines_in_axle", "Lines_in_axle", "one hose each (press)"),
    ("Lines_in_axle", "Pack_axle", "inside the axle, out through its windows"),
    ("Lines_in_axle", "MQR_rotor", "M5 push-in fittings"),
    ("MQR_rotor", "MQR_stator", "the rotary union (bought)"),
    ("Collector_1to6", "Supply_stub", "push-in fitting from below (press)"),
    ("Rear_plate", "Supply_stub", "through its hole"),
    ("Collector_fittings", "Collector_1to6", "M5 thread"),
    ("Collector_fittings", "MQR_stator", "M5 thread in the stator's ports (press)"),
    ("Collector_fittings", "Collector_hoses", "push-in fitting (press)"),
    ("Collector_hoses", "Collector_hoses", "one hose (press)"),
    ("Collector_fittings", "Collector_fittings", "side by side in the manifold's row (draft pitch 7)"),
    # --- frame
    ("Lip_TPU", "Feed_head", "TPU strip in its pocket"),
    ("Liner_half_right", "Liner_half_left", "the split: M3 x 20 lug pairs, the carry base, the keel, the ramp block"),
    # --- trains: meshes, keys, pins, journals
    ("Pack_hub", "Gears_A_B", "mesh (rim 120 / gear A)"),
    ("Pack_hub", "Crank_rim_gear_60", "mesh (rim 120 / gear 60)"),
    ("Gears_A_B", "Idler", "mesh"),
    ("Idler", "Star_gear", "mesh"),
    ("Bevel_lay", "Bevel_crank", "mesh"),
    ("Star_gear", "Star_shaft", "D-flat; between the floor of the box's 608 pocket and the front plate (AXIAL)"),
    ("Star_bearings_608", "Star_shaft", "the shaft in the 608s' inner races"),
    ("Star_bearings_608", "Front_ring", "locating 608 in the pad's pocket on its floor, under the cover (press)"),
    ("Star_bearings_608", "Gearbox", "floating 608 in the rear plate's pocket on its floor: no axial load (press)"),
    ("Star_bearings_608", "Star_bearing_cover", "the cover on the outer race"),
    ("Star_bearings_608", "Star_spacer", "the spacer on the inner race"),
    ("Star_bearings_608", "Star", "the hub's spigot on the inner race"),
    ("Star_spacer", "Star_shaft", "on the shaft"),
    ("Star_spacer", "Star_collar", "clamped by the collar"),
    ("Gears_A_B", "Layshaft", "cluster turns on a fixed pin"),
    ("Layshaft", "Gearbox", "pin in a blind hole of the rear plate, its front end 0.5 under the 61836's retainer (press)"),
    ("Idler", "Idler_shaft", "turns on its tube"),
    ("Idler_shaft", "Gearbox", "the tube clamped on the box's front plate by the M3 x 20 inside it (0.5 round the bolt)"),
    ("Bevel_lay", "Lay_shaft", "D-flat; its thrust on plate A's 608 through its spigot, the mesh ahead (AXIAL)"),
    ("Crank_spacer", "Crank_bearings_608", "the spacer's spigot on the outer 608's inner race"),
    ("Crank_spacer", "Crank_arm", "the arm's hub holds the spacer"),
    ("Crank_spacer", "Crank_shaft", "on the shaft"),
    ("Crank_bearings_608", "Bevel_*", "the bevel's spigot on its 608's inner race"),
    ("Crank_bearings_608", "Crank_rim_gear_60", "gear 60's spigot on the rim boss's 608"),
    ("Crank_bearings_608", "Lay_shaft_collar", "the collar's spigot on plate A's 608"),
    ("Crank_bracket", "Bevel_*", "the spigot through the 608's lip (0.2)"),
    ("Crank_bracket", "Crank_rim_gear_60", "the spigot through the 608's lip (0.2)"),
    ("Crank_bracket", "Lay_shaft_collar", "the spigot through the 608's lip (0.2)"),
    ("Crank_bracket", "Crank_spacer", "the spigot through the 608's lip (0.2)"),
    ("Crank_bearings_608", "Crank_*", "608 trapped in its pocket by 1 mm lips (press)"),
    ("Crank_bearings_608", "Lay_shaft", "608 on the shaft"),
    ("Crank_knob", "Crank_knob_pin", "knob turns on its pin (an M6 bolt)"),
    ("Crank_arm", "Crank_knob_pin", "the knob's pin: head and nut on the arm"),
    # --- controls
    ("Grip", "Pommel", "cast brass cap pressed on (press)"),
    ("Grip", "Deadman_valve", "in its pocket between the grip's halves, shoulders at both ends (AXIAL)"),
    ("Grip", "Supply_*", "hoses in their channels"),
    ("Deadman_valve", "Supply_*", "push-in fittings (press)"),
    ("Deadman_valve", "Deadman_pusher", "the pusher (press)"),
    ("Pommel", "Supply_hose_end", "the receiver hose through the pommel (press)"),
    ("Supply_*", "Supply_*", "one hose (press)"),
    ("Lever", "Lever_pin", "pivot"),
    ("Grip", "Lever_pin", "the tube's ends in the lugs' counterbores, clamped by the pivot's M3 x 50 (0.55 round the bolt)"),
    ("Grip", "Deadman_pusher", "the pusher in its bore"),
    ("Grip", "Gate_wire", "the wire in its channel"),
    ("Lever", "Deadman_pusher", "presses it"),
    ("Lever", "Gate_wire", "the wire's barrel nipple in the tail's cross hole (press)"),
    ("Gate_housing", "Gate_pin", "the gate pin in its bore"),
    ("Gate_housing", "Gate_spring", "the gate spring"),
    ("Gate_pin", "Gate_spring", "the gate spring"),
    ("Gate_pin", "Feed_head", "through its bore"),
    ("Gate_cable", "Gate_cable", "one Bowden housing (press)"),
    ("Gate_cable", "Gate_housing", "the housing's end 5 mm deep in its seat"),
    ("Gate_cable", "Rear_plate", "Bowden through the plate (press)"),
    ("Gate_cable", "Grip", "Bowden in its channel, its end on the shoulder at the stop"),
    ("Gate_cable", "Gate_wire", "the wire inside it (press)"),
    ("Carry_handle", "Sling_loops", "steel rings round the posts"),
    # --- EVA skin (2026-11-22): contact glue, no fixing points (owner 2026-11-21)
    ("EVA_skin", "Liner_half_*", "contact glue on the liner's glue lands"),
    ("EVA_skin", "Front_ring", "contact glue on the front ring's glue land"),
    ("EVA_skin", "Bearing_housing", "contact glue on the bearing housing"),
    ("EVA_skin", "Outer_race_retainer", "contact glue on the retainer's rim"),
    ("EVA_skin", "Crank_bracket", "rests on the tip of plate A's stud boss (r 127)"),
    ("EVA_skin", "Gearbox", "rests on the tips of the box's tie bosses (r 127)"),
    ("EVA_skin", "Bearing_front", "contact glue on the front 6808 disk's glue land"),
    ("EVA_skin", "Bearing_rear", "contact glue on the rear 6808 disk's glue land"),
    ("EVA_skin", "Rear_plate", "contact glue on the rear plate's rim"),
    ("EVA_end_cap", "Rear_plate", "contact glue on the rear plate's aft face"),
    ("EVA_end_cap", "EVA_skin", "EVA glued edge to edge"),
]

# Bodies allowed to touch nothing (closer than CONTACT): (pattern, why).
FREE = [
    ("Muzzle_plate", "pinched on the barrels by an M3 x 20 across each slit (bores 0.35 over)"),
    ("st.Nose_clamp", "the halves clamp the rails by their 2 x M3 x 20 (bores 0.15 over)"),
    ("Sling_loops", "steel rings round the carry posts, 0.5 loose"),
    ("Crank_knob", "turns on its pin, 0.25 a side"),
]

# Axial play: (label, the moving group, axis key in AXES, bodies it slides along, limit).
AXIAL_MAX = 1.0
AXIAL = [
    ("star shaft with the star, its collar and spacer", [r"Star_shaft", r"Star", r"Star_collar", r"Star_spacer",
                                                         r"F:star on its shaft \(hub\)", r"F:star shaft collar"],
     "Z", [r"Star_gear"]),
    ("star gear", [r"Star_gear"], "Z", [r"Star_shaft"]),
    ("gears A + B", [r"Gears_A_B"], "Z", [r"Layshaft"]),
    ("A + B pin", [r"Layshaft"], "Z", [r"Gears_A_B"]),
    ("idler", [r"Idler"], "Z", []),
    ("idler tube", [r"Idler_shaft"], "Z", [r"Idler"]),
    ("lay shaft with gear 60 and its collar", [r"Lay_shaft", r"Crank_rim_gear_60", r"Lay_shaft_collar",
                                               r"F:gear 60 on the lay shaft \(hub\)", r"F:lay shaft collar behind plate A"],
     "Z", [r"Bevel_lay"]),
    ("lay bevel", [r"Bevel_lay"], "Z", [r"Lay_shaft"]),
    ("crank shaft with its bevel, spacer, arm and knob", [r"Crank_shaft", r"Bevel_crank", r"Crank_spacer", r"Crank_arm",
                                                         r"Crank_knob", r"Crank_knob_pin", r"F:crank arm on its shaft",
                                                         r"F:crank bevel on its shaft \(hub\)"],
     "Y", []),
    ("lever", [r"Lever"], "Y", [r"Lever_pin", r"Gate_wire"]),
    ("lever pivot tube", [r"Lever_pin"], "Y", [r"Lever"]),
    ("dead-man valve", [r"Deadman_valve"], "DM", [r"Deadman_pusher", r"Supply_.*"]),
    ("front 6808 race", [r"Bearings_6808\.1"], "Z", [r"Pack_axle", r"Axle_collars.*"]),
    ("rear 6808 race", [r"Bearings_6808\.2"], "Z", [r"Pack_axle"]),
]
AXIAL_EPS = 0.02        # mm3 of common volume that counts as a stop


def _near(ba, bb_, pad):
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad,
                       ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    return ba2.intersect(bb_)


def _read(path):
    s = Part.Shape()
    s.read(path)
    return s


def key(name):
    """'st0.Line_R.3' -> 'st.Line_R'."""
    n = re.sub(r"\.\d+$", "", name)
    return re.sub(r"^st\d\.", "st.", n)


def declared(a, b):
    ka, kb = key(a), key(b)
    for pa, pb, why in JOINTS:
        if (fnmatch.fnmatch(ka, pa) and fnmatch.fnmatch(kb, pb)) or (fnmatch.fnmatch(kb, pa) and fnmatch.fnmatch(ka, pb)):
            return why
    return None


# ---------------------------------------------------------------- bodies and fasteners
_cached = CACHE and os.path.exists(os.path.join(CACHE, "bodies.json"))
if _cached:
    _meta = json.load(open(os.path.join(CACHE, "bodies.json")))
    _shapes = _read(os.path.join(CACHE, "bodies.brep")).childShapes()
    BODIES = [(m[0], s, m[1]) for m, s in zip(_meta["bodies"], _shapes[:len(_meta["bodies"])])]
    FAST = list(zip(_meta["fasteners"], _shapes[len(_meta["bodies"]):]))
    AXES = _meta["axes"]
    print("joints: %d bodies, %d fasteners from the cache %s" % (len(BODIES), len(FAST), CACHE), flush=True)
else:
    BREECH_MECH_LIBRARY = True
    _mech_ok = True
    try:
        exec(open(os.path.join(REPO, "gatling", "breech_mechanism.py")).read(), globals())
    except SystemExit as _e:
        _mech_ok = _e.code in (0, None)
    BREECH_MECH_LIBRARY = False
    print("joints: mechanism built in %.0f s (fast checks %s)" % (time.time() - _t0, "OK" if _mech_ok else "FAIL"),
          flush=True)
    QEV_MATS = {"Rear_plug": "print", "Seat_ring": "print", "Front_cover": "print", "Diaphragm": "rubber",
                "Front_yoke": "print", "Barrel_stub": "steel", "Chamber_tube": "Al", "Pilot_fitting": "bought",
                "Carriage": "print", "Nose_clamp": "print"}
    BODIES, FAST = [], []

    def body(name, shape, mat):
        sols = shape.Solids
        if len(sols) > 1:
            for i, s in enumerate(sols):
                BODIES.append(("%s.%d" % (name, i + 1), s, mat))
        else:
            BODIES.append((name, shape, mat))

    for _k in (0, 3):                       # FIRE (on the ramp), LOAD (under the feed)
        _p = _k * 60.0
        _dz = cam_dz(_p)
        _s = "st%d." % _k
        for _n, _sh in qev_closed.items():
            if _n == "Tie_rods":
                FAST += [("%sTie_studs.%d" % (_s, i + 1), s_) for i, s_ in enumerate(place(_sh, _p, _dz).Solids)]
                continue
            body(_s + _n, place(_sh, _p, _dz), QEV_MATS[_n])
        body(_s + "AirTAC", place(valve_body, _p, _dz), "bought")
        body(_s + "AirTAC_plunger", place(valve_plunger, _p, _dz), "bought")
        body(_s + "AirTAC_fittings", place(valve_fit, _p, _dz), "bought")
        body(_s + "Valve_bracket", place(valve_bracket, _p, _dz), "print")
        body(_s + "Line_A", place(line_a, _p, _dz), "hose")
        body(_s + "Line_R", place(line_r(_dz), _p), "hose")
        body(_s + "Finger", place(follower, _p, _dz), "steel")
        body(_s + "Rails", place(rails_pack, _p), "Al")
        body(_s + "Breech_clamp_upper", place(clamp_upper, _p), "print")
        body(_s + "Barrel", place(fixed_barrel, _p), "steel")
    for _n, _sh, _m in (
            ("Pack_hub", pack_hub, "print"), ("Front_bearing_61836", front_bearing, "bought"),
            ("Inner_race_retainer", brg_ret_in, "print"), ("Muzzle_plate", front_plate, "print"),
            ("Rear_rail_disk", rear_disk, "print"), ("Pack_axle", pack_axle, "Al"), ("Axle_collars", axle_collars, "print"),
            ("Lines_in_axle", lines_inner, "hose"), ("Soft_coupling", soft_coup, "TPU"), ("MQR_rotor", mqr_rotor, "bought"),
            ("Liner_half_right", cam_r, "print"), ("Liner_half_left", cam_l, "print"), ("Front_ring", pack_frame, "print"),
            ("Bearing_front", brg_f, "print"), ("Bearing_rear", brg_r, "print"), ("Front_6808_retainer", brg6808_ret, "print"),
            ("Bearing_housing", brg_housing, "print"), ("Outer_race_retainer", brg_ret_out, "print"),
            ("Firing_ramp", ramp_body, "print"), ("Ramp_mount_block", guide_block, "print"),
            ("Rear_plate", mqr_plate, "print"), ("MQR_stator", mqr_stator, "bought"), ("Gearbox", gearbox, "print"),
            ("Feed_head", feed_head, "print"), ("Lip_TPU", feed_lip, "TPU"), ("Cup", feed_cup, "print"),
            ("Feed_guard", feed_guard, "print"), ("Gate_housing", gate_housing, "print"), ("Gate_pin", gate_pin, "steel"),
            ("Gate_spring", gate_spring, "steel"), ("Gate_cable", gate_cable, "hose"), ("Gate_wire", gate_wire, "steel"),
            ("Carry_handle", carry_handle, "print"), ("Sling_loops", sling, "steel"), ("Tripod_pad", tripod_pad, "print"),
            ("Crank_bracket", crank_bracket, "print"), ("Crank_bearings_608", crank_bearings, "bought"),
            ("Grip", grip, "wood"), ("Pommel", pommel, "brass"), ("Deadman_valve", deadman, "bought"),
            ("Supply_stub", air_supply, "hose"), ("Supply_hose_end", supply_hose, "hose"),
            ("Lever", lever, "print"), ("Lever_pin", lever_pin, "steel"), ("Deadman_pusher", dm_pusher, "steel"),
            ("Star", star0, "print"), ("Star_gear", gear_s, "print"), ("Star_shaft", star_shaft, "steel"),
            ("Star_collar", star_collar, "print"), ("Gears_A_B", gear_ab, "print"), ("Layshaft", lay_shaft, "steel"),
            ("Idler", gear_i, "print"), ("Idler_shaft", idl_shaft, "steel"),
            ("Crank_rim_gear_60", crank_gear, "print"), ("Lay_shaft", pin_shaft, "steel"), ("Bevel_lay", bevel_small, "print"),
            ("Bevel_crank", bevel_big, "print"), ("Crank_shaft", crank_shaft, "steel"), ("Crank_arm", crank_arm, "print"),
            ("Crank_knob", crank_knob, "print"), ("Crank_knob_pin", crank_knob_pin, "steel"),
            ("Bearings_6808", races_6808, "bought"), ("Rear_6808_retainer", brg6808_ret_r, "print"),
            ("Star_bearings_608", star_bearings, "bought"), ("Star_bearing_cover", star_cover, "print"),
            ("Star_spacer", star_spacer, "steel"), ("Lay_shaft_collar", lay_collar, "print"),
            ("Crank_spacer", crank_spacer, "print"), ("Collector_1to6", collector, "bought"),
            ("Collector_fittings", coll_fittings, "bought"), ("Collector_hoses", coll_hoses, "hose"),
            ("EVA_skin", skin, "EVA"), ("EVA_end_cap", skin_cap, "EVA")):
        body(_n, _sh, _m)
    FAST += [(f_.name, f_.body) for f_ in FASTENERS] + [(n_, b_) for n_, b_ in M4_EXC]
    AXES = {"Z": [0.0, 0.0, 1.0], "Y": [0.0, 1.0, 0.0], "DM": [_face_n0.x, _face_n0.y, _face_n0.z]}
    if CACHE:
        os.makedirs(CACHE, exist_ok=True)
        Part.makeCompound([b[1] for b in BODIES] + [f[1] for f in FAST]).exportBrep(os.path.join(CACHE, "bodies.brep"))
        json.dump({"bodies": [[b[0], b[2]] for b in BODIES], "fasteners": [f[0] for f in FAST], "axes": AXES},
                  open(os.path.join(CACHE, "bodies.json"), "w"))
        print("joints: %d bodies, %d fasteners written to %s" % (len(BODIES), len(FAST), CACHE), flush=True)

# ---------------------------------------------------------------- pairs
print("joints: %d bodies, %d fasteners, measuring pairs…" % (len(BODIES), len(FAST)), flush=True)
_bbs = [b[1].BoundBox for b in BODIES]
_fbb = [f[1].BoundBox for f in FAST]
rows = []                                        # (a, b, dist, overlap, how, ok)
_n_pairs = 0
for i in range(len(BODIES)):
    for j in range(i + 1, len(BODIES)):
        if not _near(_bbs[i], _bbs[j], CONTACT):
            continue
        _n_pairs += 1
        a, b = BODIES[i], BODIES[j]
        d = a[1].distToShape(b[1])[0]
        if d >= CONTACT:
            continue
        ov = 0.0
        if d < 1e-6:
            try:
                ov = a[1].common(b[1]).Volume
            except Exception:
                ov = -1.0
        how = declared(a[0], b[0])
        if how is None:
            for (fn, fs), fb in zip(FAST, _fbb):
                if _near(fb, _bbs[i], FAST_NEAR) and _near(fb, _bbs[j], FAST_NEAR) \
                        and fs.distToShape(a[1])[0] < FAST_NEAR and fs.distToShape(b[1])[0] < FAST_NEAR:
                    how = "fastened: " + re.sub(r", st \d+$", "", fn)
                    break
        ok = how is not None and (ov <= OVERLAP or "press" in how)
        rows.append((a[0], b[0], d, ov, how or "NOT DECLARED", ok))
print("joints: %d bbox pairs, %d contacts in %.0f s" % (_n_pairs, len(rows), time.time() - _t0), flush=True)

# One line per pair of part kinds (station parts of the two stations and multi-solid pieces merged).
_merged = {}
for a, b, d, ov, how, ok in rows:
    k = tuple(sorted((key(a), key(b))))
    m = _merged.setdefault(k, [99.0, 0.0, set(), True])
    m[0] = min(m[0], d)
    m[1] += max(ov, 0.0)
    m[2].add(how)
    m[3] = m[3] and ok
bad = [k for k, m in _merged.items() if not m[3]]
lines = ["%-28s %-28s %6s %9s  %s" % ("part", "part", "dist", "overlap", "held by")]
for k in sorted(_merged, key=lambda k_: (_merged[k_][3], k_)):
    d, ov, hows, ok = _merged[k]
    lines.append("%-28s %-28s %6.2f %9.2f  %s%s" % (k[0], k[1], d, ov, "" if ok else "[FAIL] ", " | ".join(sorted(hows))))
touch_nothing = [b[0] for b in BODIES if not any(b[0] in (r[0], r[1]) for r in rows)]


def _free(n):
    return next((why for pat, why in FREE if fnmatch.fnmatch(key(n), pat)), None)


free_bad = sorted(set(key(n) for n in touch_nothing if _free(n) is None))
lines += ["", "bodies touching nothing (closer than %.1f): %s" % (CONTACT, ", ".join(
    "%s (%s)" % (n, _free(n) or "[FAIL] not in FREE") for n in touch_nothing) or "none"), ""]
lines.append("  [%s] every contact fastened or declared, no undeclared overlap (%d pairs of part kinds, %d not)"
             % ("OK " if not bad else "FAIL", len(_merged), len(bad)))
lines.append("  [%s] every body touches a neighbour or is declared free (%s)"
             % ("OK " if not free_bad else "FAIL", ", ".join(free_bad) or "all"))

# ---------------------------------------------------------------- axial play
_ALL = BODIES and [(b[0], b[1]) for b in BODIES] + [("F:" + n, s_) for n, s_ in FAST]


def _pick(pats):
    return [(n, s_) for n, s_ in _ALL if any(re.fullmatch(p_, n) for p_ in pats)]


def _bb_pad(bb, pad):
    return App.BoundBox(bb.XMin - pad, bb.YMin - pad, bb.ZMin - pad, bb.XMax + pad, bb.YMax + pad, bb.ZMax + pad)


def _travel(group, obst, d, maxt=6.0):
    """How far the group goes along d before it meets an obstacle (its common volume grows by
    AXIAL_EPS over the start: a press fit across the axis is no stop): (t, name)."""
    g = Part.makeCompound([s_ for _, s_ in group])
    near = [(n, s_) for n, s_ in obst if _bb_pad(g.BoundBox, maxt + 0.5).intersect(s_.BoundBox)]

    def vol(m, s_):
        if not _bb_pad(m.BoundBox, 0.01).intersect(s_.BoundBox):
            return 0.0
        try:
            return m.common(s_).Volume
        except Exception:
            return 0.0
    base = [vol(g, s_) for _, s_ in near]

    def hit(t):
        m = g.copy()
        m.translate(d * t)
        for (n, s_), v0 in zip(near, base):
            if vol(m, s_) > v0 + AXIAL_EPS:
                return n
        return None
    lo, hi, who, t = 0.0, None, None, 0.1
    while t <= maxt + 1e-9:
        w = hit(t)
        if w:
            hi, who = t, w
            break
        lo, t = t, t + (0.1 if t < 1.0 else 0.5)
    if hi is None:
        return maxt, "nothing within %.0f" % maxt
    for _ in range(5):
        mid = 0.5 * (lo + hi)
        w = hit(mid)
        if w:
            hi, who = mid, w
        else:
            lo = mid
    return lo, who


axial_bad = []
lines += ["", "axial play (pushed both ways along the axis until a body is met; limit %.1f):" % AXIAL_MAX]
for lab, gp, ax, skip in AXIAL:
    grp = _pick(gp)
    if not grp:
        axial_bad.append(lab)
        lines.append("  [FAIL] %s: no such bodies %s" % (lab, gp))
        continue
    gn = set(n for n, _ in grp)
    obst = [(n, s_) for n, s_ in _ALL if n not in gn and not any(re.fullmatch(p_, n) for p_ in skip)]
    d = App.Vector(*AXES[ax])
    a_, wa = _travel(grp, obst, d)
    b_, wb = _travel(grp, obst, d * -1.0)
    ok = a_ + b_ <= AXIAL_MAX + 1e-6
    if not ok:
        axial_bad.append(lab)
    lines.append("  [%s] %-48s %5.2f  (+ %.2f to %s, - %.2f to %s)" % ("OK " if ok else "FAIL", lab, a_ + b_, a_, wa, b_, wb))
    print(lines[-1], flush=True)
lines.append("  [%s] axial play within %.1f mm (%d groups, %s)" % ("OK " if not axial_bad else "FAIL", AXIAL_MAX, len(AXIAL),
                                                                   ", ".join(axial_bad) or "all"))
print("\n".join(lines))
_out = os.path.join(REPO, "exports", "gatling_breech_mechanism")
os.makedirs(_out, exist_ok=True)
with open(os.path.join(_out, "gatling_breech_mechanism_joints.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("joints: done in %.0f s" % (time.time() - _t0), flush=True)
if bad or free_bad or axial_bad:
    raise SystemExit("gatling joints: %d undeclared contacts, %d undeclared free bodies, %d axial plays over %.1f"
                     % (len(bad), len(free_bad), len(axial_bad), AXIAL_MAX))
