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

The pairs are measured by JOINTS_WORKERS (environment, default cores - 2) freecadcmd
processes, like the sweep: each worker takes a share of the bounding-box pairs (2026-11-22: one
process took ~12 of the ~19 min). Since 2026-11-22 the axial pushes run there too, one task per
group and direction (they took ~3 min in one process), the workers taking the next free task.

The bodies and fasteners come from the mechanism's body cache (gatling/breech_cache.py: written
by breech_mechanism.py, keyed by the sources), so the tables here can be reworked without a
rebuild; without a cache the mechanism is built once as a library (~3.5 min), which writes it.
The pairs and pushes are remembered by the hashes of their bodies' BREP
(exports/gatling_breech_mechanism/memo/): a repeat or a run after an edit measures only what a
changed body takes part in (393 -> 87 s from scratch, ~5-13 s again; the report is the same).
Report:
exports/gatling_breech_mechanism/gatling_breech_mechanism_joints.txt
"""
import fnmatch
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
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
_WORKER = os.environ.get("BREECH_JOINTS_TASK")
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


def measure(a, b, fast, need_fast):
    """(distance, common volume or -1, first fastener index within FAST_NEAR of both or -1)."""
    d = a.distToShape(b)[0]
    if d >= CONTACT:
        return d, 0.0, -1
    ov = 0.0
    if d < 1e-6:
        try:
            ov = a.common(b).Volume
        except Exception:
            ov = -1.0
    fi = -1
    if need_fast:
        ba, bb_ = a.BoundBox, b.BoundBox
        for k, fs in enumerate(fast):
            fb = fs.BoundBox
            if _near(fb, ba, FAST_NEAR) and _near(fb, bb_, FAST_NEAR) \
                    and fs.distToShape(a)[0] < FAST_NEAR and fs.distToShape(b)[0] < FAST_NEAR:
                fi = k
                break
    return d, ov, fi


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



def _claim(work, i):
    try:
        os.close(os.open(os.path.join(work, "claim_%04d" % i), os.O_CREAT | os.O_EXCL))
        return True
    except FileExistsError:
        return False


def _load(cdir):
    """(bodies [(name, shape, material)], fasteners [(name, shape)], axes) from the cache."""
    meta = json.load(open(os.path.join(cdir, "bodies.json")))
    shapes = _read(os.path.join(cdir, "bodies.brep")).childShapes()
    nb = len(meta["bodies"])
    return ([(m[0], s_, m[1]) for m, s_ in zip(meta["bodies"], shapes[:nb])],
            list(zip(meta["fasteners"], shapes[nb:])), meta["axes"])


if _WORKER:
    # ------------------------------------------------------------ worker: free tasks until none is left
    _w0 = time.time()
    _task = json.load(open(_WORKER))
    BODIES, FAST, AXES = _load(_task["cache"])
    _ALL = [(b[0], b[1]) for b in BODIES] + [("F:" + n, s_) for n, s_ in FAST]
    _fs = [f[1] for f in FAST]
    _res = {"pairs": [], "axial": {}}
    for _ti, _t in enumerate(_task["tasks"]):
        if not _claim(_task["work"], _ti):
            continue
        _t1 = time.time()
        if _t["kind"] == "pairs":
            _res["pairs"] += [[i, j] + list(measure(BODIES[i][1], BODIES[j][1], _fs, nf)) for i, j, nf in _t["pairs"]]
            _lab = "%d pairs" % len(_t["pairs"])
        else:
            _lab_, _gp, _ax, _skip = AXIAL[_t["group"]]
            _grp = _pick(_gp)
            _gn = set(n for n, _ in _grp)
            _obst = [(n, s_) for n, s_ in _ALL if n not in _gn and not any(re.fullmatch(p_, n) for p_ in _skip)]
            _res["axial"]["%d %+d" % (_t["group"], _t["sign"])] = list(
                _travel(_grp, _obst, App.Vector(*AXES[_ax]) * float(_t["sign"])))
            _lab = "axial %s %+d" % (_lab_, _t["sign"])
        print("task %3d %-60s %6.1f s" % (_ti, _lab, time.time() - _t1), flush=True)
    print("worker: done in %.0f s, peak RSS %.0f MB" % (
        time.time() - _w0, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20 if sys.platform == "darwin" else 1 << 10)),
        flush=True)
    json.dump(_res, open(_task["out"], "w"))
    raise SystemExit(0)

# ---------------------------------------------------------------- bodies and fasteners
exec(open(os.path.join(REPO, "gatling", "breech_cache.py")).read(), globals())
_cdir, _built = bc_load(REPO)
_jdir = os.path.join(_cdir, "joints")
BODIES, FAST, AXES = _load(_jdir)
_ALL = [(b[0], b[1]) for b in BODIES] + [("F:" + n, s_) for n, s_ in FAST]
print("joints: %d bodies, %d fasteners from %s (%s)" % (len(BODIES), len(FAST), _cdir,
                                                     ("built in %.0f s" % _built) if _built else "cached"), flush=True)

# ---------------------------------------------------------------- pairs
print("joints: %d bodies, %d fasteners, measuring pairs…" % (len(BODIES), len(FAST)), flush=True)
_bbs = [b[1].BoundBox for b in BODIES]
_pairs = [(i, j, declared(BODIES[i][0], BODIES[j][0]) is None)
          for i in range(len(BODIES)) for j in range(i + 1, len(BODIES)) if _near(_bbs[i], _bbs[j], CONTACT)]
_n_pairs = len(_pairs)
_n_workers = int(os.environ.get("JOINTS_WORKERS", max(1, (os.cpu_count() or 4) - 2)))
_faces = [len(b[1].Faces) for b in BODIES]
# Heaviest pairs first, dealt round the workers so each gets a like share of the work.
_pairs.sort(key=lambda p_: -_faces[p_[0]] * _faces[p_[1]])
# Remembered results (2026-11-22): a pair by the hashes of its two bodies' BREP (and of all the
# fasteners when it needs one), an axial push by its group, the bodies near it and the way; kept
# across rebuilds, so after an edit only what a changed part takes part in is measured again.
import hashlib
MEMO_VERSION = "joints 1: contact %.3f, near %.3f, axial eps %.3f" % (CONTACT, FAST_NEAR, AXIAL_EPS)
MEMO = os.path.join(REPO, "exports", "gatling_breech_mechanism", "memo", "gatling_breech_mechanism_joints_memo.json")


def _sha(b_):
    return hashlib.sha1(b_).hexdigest()[:20]


_bh = [_sha(b[1].exportBrepToString().encode()) for b in BODIES]
_fh = _sha("".join(_sha(f[1].exportBrepToString().encode()) for f in FAST).encode())


def _pair_key(i, j, nf):
    return "%s|%s|%d%s" % (_bh[i], _bh[j], nf, ("|" + _fh) if nf else "")


_hash_of = dict(zip([b[0] for b in BODIES], _bh))
_hash_of.update({"F:" + f[0]: _sha(f[1].exportBrepToString().encode()) for f in FAST})


def _axial_key(gi, sg, maxt=6.0):
    lab, gp, ax, skip = AXIAL[gi]
    grp = _pick(gp)
    gn = set(n for n, _ in grp)
    g = Part.makeCompound([s_ for _, s_ in grp])
    near = [n for n, s_ in _ALL if n not in gn and not any(re.fullmatch(p_, n) for p_ in skip)
            and _bb_pad(g.BoundBox, maxt + 0.5).intersect(s_.BoundBox)]
    return _sha(json.dumps([[(n, _hash_of[n]) for n, _ in grp], [(n, _hash_of[n]) for n in near], AXES[ax], sg]).encode())


_bh_nf = {(i, j): nf for i, j, nf in _pairs}
_memo = {}
if os.path.exists(MEMO):
    _m = json.load(open(MEMO))
    _memo = _m["memo"] if _m.get("version") == MEMO_VERSION else {}
_memo_new = {}
_meas, _axial = [], {}                           # _meas: [i, j, dist, overlap, fastener index]
_todo = []
for i, j, nf in _pairs:
    k_ = _pair_key(i, j, nf)
    if k_ in _memo:
        _meas.append([i, j] + _memo[k_])
        _memo_new[k_] = _memo[k_]
    else:
        _todo.append((i, j, nf))
_ax_keys = {}
for gi, (_l, gp, _a, _s) in enumerate(AXIAL):
    if not _pick(gp):
        continue
    for sg in (1, -1):
        k_ = _ax_keys["%d %+d" % (gi, sg)] = _axial_key(gi, sg)
        if k_ in _memo:
            _axial["%d %+d" % (gi, sg)] = _memo[k_]
            _memo_new[k_] = _memo[k_]
# Tasks: the axial pushes (one group, one way: the longest single tasks) first, then the pairs
# in runs of PAIR_RUN, heaviest first; each worker takes the next free one.
PAIR_RUN = 10
_tasks = [{"kind": "axial", "group": int(k_.split()[0]), "sign": int(k_.split()[1])}
          for k_ in _ax_keys if k_ not in _axial]
_tasks += [{"kind": "pairs", "pairs": _todo[k:k + PAIR_RUN]} for k in range(0, len(_todo), PAIR_RUN)]
print("joints: %d of %d pairs and %d of %d axial pushes remembered, %d tasks left"
      % (len(_pairs) - len(_todo), len(_pairs), len(_axial), len(_ax_keys), len(_tasks)), flush=True)
_n_workers = max(1, min(_n_workers, len(_tasks)))
_procs, _failed, _work = [], [], None
if _tasks:
    _work = tempfile.mkdtemp(prefix="breech_joints_")
    _exe = os.path.join(App.getHomePath(), "bin", "freecadcmd")
    if not os.path.exists(_exe):
        _exe = shutil.which("freecadcmd") or _exe
    for _w in range(_n_workers):
        _tp, _op = os.path.join(_work, "task_%02d.json" % _w), os.path.join(_work, "out_%02d.json" % _w)
        json.dump({"cache": _jdir, "work": _work, "tasks": _tasks, "out": _op}, open(_tp, "w"))
        _log = open(os.path.join(_work, "worker_%02d.log" % _w), "w")
        _procs.append((_w, subprocess.Popen([_exe, os.path.join(REPO, "gatling", "breech_joints.py")],
                                            env=dict(os.environ, BREECH_JOINTS_TASK=_tp, REPO=REPO),
                                            stdout=_log, stderr=subprocess.STDOUT), _op))
    print("joints: %d tasks on %d workers (logs in %s)" % (len(_tasks), len(_procs), _work), flush=True)
    for _w, _pr, _op in _procs:
        _pr.wait()
        if _pr.returncode not in (0, None) or not os.path.exists(_op):
            _failed.append(_w)
            continue
        _r = json.load(open(_op))
        for m_ in _r["pairs"]:
            _meas.append(m_)
            _memo_new[_pair_key(m_[0], m_[1], _bh_nf[(m_[0], m_[1])])] = m_[2:]
        for k_, v_ in _r["axial"].items():
            _axial[k_] = v_
            _memo_new[_ax_keys[k_]] = v_
    _claimed = len([f_ for f_ in os.listdir(_work) if f_.startswith("claim_")])
    if _failed or _claimed != len(_tasks):
        raise SystemExit("gatling joints: workers %s failed, %d of %d tasks claimed, logs in %s"
                         % (_failed, _claimed, len(_tasks), _work))
    for _w, _, _ in _procs:
        _wl = open(os.path.join(_work, "worker_%02d.log" % _w)).read().strip().splitlines()
        print("  worker %02d: %s" % (_w, next((l_ for l_ in reversed(_wl) if l_.startswith("worker:")), "no summary")),
              flush=True)
    shutil.rmtree(_work, ignore_errors=True)
os.makedirs(os.path.dirname(MEMO), exist_ok=True)
json.dump({"version": MEMO_VERSION, "memo": _memo_new}, open(MEMO + ".tmp", "w"))
os.replace(MEMO + ".tmp", MEMO)
_meas.sort(key=lambda m_: (m_[0], m_[1]))
rows = []                                        # (a, b, dist, overlap, how, ok)
for i, j, d, ov, fi in _meas:
    if d >= CONTACT:
        continue
    a, b = BODIES[i], BODIES[j]
    how = declared(a[0], b[0])
    if how is None and fi >= 0:
        how = "fastened: " + re.sub(r", st \d+$", "", FAST[fi][0])
    ok = how is not None and (ov <= OVERLAP or "press" in how)
    rows.append((a[0], b[0], d, ov, how or "NOT DECLARED", ok))
print("joints: %d bbox pairs on %d workers, %d contacts in %.0f s" % (_n_pairs, max(1, _n_workers), len(rows),
                                                                      time.time() - _t0), flush=True)

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
axial_bad = []
lines += ["", "axial play (pushed both ways along the axis until a body is met; limit %.1f):" % AXIAL_MAX]
for gi, (lab, gp, ax, skip) in enumerate(AXIAL):
    if not _pick(gp):
        axial_bad.append(lab)
        lines.append("  [FAIL] %s: no such bodies %s" % (lab, gp))
        continue
    a_, wa = _axial["%d +1" % gi]
    b_, wb = _axial["%d -1" % gi]
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
