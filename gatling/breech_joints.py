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
overlap (common volume) that is not declared as a press fit or a squeeze.

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
    ("Pack_axle", "Bearing_*", "6808 on a 1 mm shim"),
    ("Axle_collars", "Pack_axle", "split collars clamped, an M3 x 20 across each slit"),
    ("Rear_rail_disk", "Pack_axle", "split hub clamped, an M3 x 20 across its slit"),
    ("Soft_coupling", "Pack_axle", "clamped, an M3 x 20 across its slit; the axle's end on its neck (press)"),
    ("Lines_in_axle", "Soft_coupling", "the lines pass it"),
    ("Axle_collars", "Bearing_front", "collar lips on the front 6808's inner race"),
    ("Lines_in_axle", "Lines_in_axle", "one hose each (press)"),
    ("Lines_in_axle", "Pack_axle", "inside the axle, out through its windows"),
    ("Lines_in_axle", "MQR_rotor", "M5 push-in fittings"),
    ("MQR_rotor", "MQR_stator", "the rotary union (bought)"),
    ("MQR_stator", "Supply_stub", "push-in fitting (press)"),
    # --- frame
    ("Lip_TPU", "Feed_head", "TPU strip in its pocket"),
    ("Liner_half_right", "Liner_half_left", "the split: M3 x 20 lug pairs, the carry base, the keel, the ramp block"),
    # --- trains: meshes, keys, pins, journals
    ("Pack_hub", "Gears_A_B", "mesh (rim 120 / gear A)"),
    ("Pack_hub", "Crank_rim_gear_60", "mesh (rim 120 / gear 60)"),
    ("Gears_A_B", "Idler", "mesh"),
    ("Idler", "Star_gear", "mesh"),
    ("Bevel_lay", "Bevel_crank", "mesh"),
    ("Star", "Star_shaft", "D-flat; the star between the shroud's walls"),
    ("Star_gear", "Star_shaft", "D-flat; between the box's plates"),
    ("Star_collar", "Star_shaft", "M3 x 20 across the drilled shaft"),
    ("Star_collar", "Front_ring", "thrust face"),
    ("Star_shaft", "Front_ring", "journal"),
    ("Star_shaft", "Gearbox", "journal"),
    ("Star_shaft", "Outer_race_retainer", "front end stop"),
    ("Gears_A_B", "Layshaft", "cluster turns on a fixed pin"),
    ("Layshaft", "Gearbox", "pin pressed in the box's plates"),
    ("Idler", "Idler_shaft", "turns on its pin"),
    ("Idler_shaft", "Gearbox", "pin pressed in the box's front plate"),
    ("Crank_rim_gear_60", "Lay_shaft", "D-flat"),
    ("Bevel_lay", "Lay_shaft", "D-flat; the bevel on plate A's 608"),
    ("Bevel_crank", "Crank_shaft", "D-flat; on the boss's 608"),
    ("Crank_bearings_608", "Crank_*", "608 press fit (press)"),
    ("Crank_bearings_608", "Lay_shaft", "608 on the shaft"),
    ("Crank_knob", "Crank_knob_pin", "knob turns on its pin (an M6 bolt)"),
    ("Crank_arm", "Crank_knob_pin", "the knob's pin: head and nut on the arm"),
    # --- controls
    ("Grip", "Pommel", "cast brass cap pressed on (press)"),
    ("Grip", "Deadman_valve", "in its pocket, the hoses hold it"),
    ("Grip", "Lever_pin", "pivot pin in the grip's lugs (press)"),
    ("Grip", "Supply_*", "hoses in their channels"),
    ("Deadman_valve", "Supply_*", "push-in fittings (press)"),
    ("Deadman_valve", "Deadman_pusher", "the pusher (press)"),
    ("Pommel", "Supply_hose_end", "the receiver hose through the pommel (press)"),
    ("Supply_*", "Supply_*", "one hose (press)"),
    ("Lever", "Lever_pin", "pivot"),
    ("Grip", "Deadman_pusher", "the pusher in its bore"),
    ("Grip", "Gate_wire", "the wire in its channel"),
    ("Lever", "Deadman_pusher", "presses it"),
    ("Lever", "Gate_wire", "the wire's end in the tail (press)"),
    ("Gate_housing", "Gate_pin", "the gate pin in its bore"),
    ("Gate_housing", "Gate_spring", "the gate spring"),
    ("Gate_pin", "Gate_spring", "the gate spring"),
    ("Gate_pin", "Feed_head", "through its bore"),
    ("Gate_cable", "Gate_cable", "one Bowden housing (press)"),
    ("Gate_cable", "Gate_housing", "Bowden ferrule"),
    ("Gate_cable", "Rear_plate", "Bowden through the plate (press)"),
    ("Gate_cable", "Grip", "Bowden in its channel"),
    ("Gate_cable", "Gate_wire", "the wire inside it (press)"),
    ("Carry_handle", "Sling_loops", "steel rings round the posts"),
]


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
            ("Crank_knob", crank_knob, "print"), ("Crank_knob_pin", crank_knob_pin, "steel")):
        body(_n, _sh, _m)
    FAST += [(f_.name, f_.body) for f_ in FASTENERS] + [(n_, b_) for n_, b_ in M4_EXC]
    if CACHE:
        os.makedirs(CACHE, exist_ok=True)
        Part.makeCompound([b[1] for b in BODIES] + [f[1] for f in FAST]).exportBrep(os.path.join(CACHE, "bodies.brep"))
        json.dump({"bodies": [[b[0], b[2]] for b in BODIES], "fasteners": [f[0] for f in FAST]},
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
lines += ["", "bodies touching nothing (closer than %.1f): %s" % (CONTACT, ", ".join(touch_nothing) or "none"), ""]
lines.append("  [%s] every contact fastened or declared, no undeclared overlap (%d pairs of part kinds, %d not)"
             % ("OK " if not bad else "FAIL", len(_merged), len(bad)))
print("\n".join(lines))
_out = os.path.join(REPO, "exports", "gatling_breech_mechanism")
os.makedirs(_out, exist_ok=True)
with open(os.path.join(_out, "gatling_breech_mechanism_joints.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("joints: done in %.0f s" % (time.time() - _t0), flush=True)
if bad:
    raise SystemExit("gatling joints: %d undeclared contacts" % len(bad))
