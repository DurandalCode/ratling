# -*- coding: utf-8 -*-
"""
Shared body cache of the gatling breech mechanism for its separate checks (2026-11-22).

The full-turn sweep (breech_mechanism_sweep.py) and the joint audit (breech_joints.py) used to
build the mechanism again each (~3.5 min apiece). Now gatling/breech_mechanism.py writes what
they need once, after its checks, in the run itself and as a library:

- sweep/: the fixed parts (fixed.brep and their names), every 3 deg of pack turn one BREP per
  station (moving, fixed, plunger, line R) and one with the star, the hub, gear A, the ramp and
  gear 60; every 5 deg of phase one BREP (two neighbours, the valve group and its own parts);
- joints/: the named bodies and fasteners (bodies.brep + bodies.json), as breech_joints.py
  splits them (two stations broken into their parts, every fixed and pack part);
- done.json: the key, the build's fast checks, the constants the reports print.

The key is a hash of the sources (gatling/*.py, ratling/*.py, without the two readers, whose
tables and reports do not change the bodies) and the FreeCAD version: a changed file means a
rebuild. Only the newest key is kept. BREECH_CACHE (environment) = another root directory
(default exports/gatling_breech_mechanism/cache).

Exec'd into the caller's globals: breech_mechanism.py calls bc_write() at the end of its
checks, the readers call bc_load(): the cache, or without one the mechanism built as a library
in a namespace of its own (which writes it).
"""
import glob as _bc_glob
import hashlib as _bc_hashlib
import json as _bc_json
import os as _bc_os
import shutil as _bc_shutil

import FreeCAD as _bc_App
import Part as _bc_Part

BC_READERS = ("breech_mechanism_sweep.py", "breech_joints.py")


def bc_key(repo):
    h = _bc_hashlib.sha256()
    files = sorted(_bc_glob.glob(_bc_os.path.join(repo, "gatling", "*.py"))
                   + _bc_glob.glob(_bc_os.path.join(repo, "ratling", "*.py")))
    for f in files:
        if _bc_os.path.basename(f) in BC_READERS:
            continue
        h.update(_bc_os.path.relpath(f, repo).encode())
        h.update(open(f, "rb").read())
    h.update(repr(_bc_App.Version()[:4]).encode())
    return h.hexdigest()[:16]


def bc_root(repo):
    return _bc_os.environ.get("BREECH_CACHE") or _bc_os.path.join(repo, "exports", "gatling_breech_mechanism", "cache")


def bc_dir(repo, key=None):
    """The cache directory for the sources as they are now, or None if it has not been written."""
    d = _bc_os.path.join(bc_root(repo), key or bc_key(repo))
    return d if _bc_os.path.exists(_bc_os.path.join(d, "done.json")) else None


def bc_load(repo):
    """The cache directory; without one, build the mechanism as a library in a namespace of its
    own (it writes the cache). Returns (directory, build seconds or 0)."""
    import time as _t
    d = bc_dir(repo)
    if d:
        return d, 0.0
    t0 = _t.time()
    ns = {"REPO": repo, "BREECH_MECH_LIBRARY": True, "__name__": "__main__"}
    try:
        exec(open(_bc_os.path.join(repo, "gatling", "breech_mechanism.py")).read(), ns)
    except SystemExit:
        pass
    d = ns.get("BC_WRITTEN")
    if not d or not _bc_os.path.exists(_bc_os.path.join(d, "done.json")):
        raise SystemExit("breech cache: the mechanism build did not write the cache")
    return d, _t.time() - t0


# ------------------------------------------------------------------ writer (mechanism globals)
BC_SWEEP_STEP = 3.0
BC_PHASE_STEP = 5.0


def _bc_sweep(dst):
    _bc_os.makedirs(dst)
    fixed_list = ([("guard", feed_guard), ("feed head", feed_head), ("TPU lip", feed_lip), ("cup", feed_cup),
                   ("ramp mount block", guide_block), ("front bearing disk", brg_f),
                   ("rear plate and struts", Part.makeCompound([mqr_plate, rear_struts])),
                   ("feed gate and its cable", Part.makeCompound([gate_housing, gate_pin, gate_pin_open, gate_cable])),
                   ("carry handle", carry_handle), ("strap rings", sling), ("room for the hand", hand_space),
                   ("crank arm and knob, every %.0f deg of a crank turn" % CK_STEP,
                    Part.makeCompound([s_ for pose_ in crank_poses for s_ in pose_])),
                   ("fist on the carry handle", carry_hand), ("tripod pad", tripod_pad),
                   ("tripod ball and post", tripod_ball),
                   ("frame M6 studs and nuts", frame_studs),
                   ("fixed M3 bolts (feed, ramp, liner, carry, keel, crank brackets)",
                    Part.makeCompound([f_.body for f_ in FEED_FAST + RAMP_FAST + LINER_FAST + CARRY_FAST
                                       + TRIPOD_FAST + CRANK_FAST])),
                   ("front bearing housing and its rear retainer", Part.makeCompound([brg_housing, brg_ret_out])),
                   ("star shaft collar", star_collar),
                   ("front ring with its top pad (the star shaft's 608)", pack_frame),
                   ("star shaft: 608s, cover, spacer", Part.makeCompound([star_bearings, star_cover, star_spacer])),
                   ("EVA skin and its end cap", Part.makeCompound([skin, skin_cap]))]
                  + [(n, s) for n, s in train_parts if not n.startswith("gear A")]
                  + [(n, s) for n, s in drive_parts if not n.startswith("crank gear")])
    Part.makeCompound([s for _, s in fixed_list]).exportBrep(_bc_os.path.join(dst, "fixed.brep"))
    hub = Part.makeCompound([pack_hub, brg_ret_in] + [f_.body for f_ in HUB_FAST])
    turn = []
    for i in range(int(round(60.0 / BC_SWEEP_STEP))):
        th = i * BC_SWEEP_STEP
        d = ((th + 30.0) % 60.0) - 30.0
        common = "turn_%02d.brep" % i
        Part.makeCompound([star_at(d), rot(hub, th), gear_a, ramp_fire, crank_gear]).exportBrep(
            _bc_os.path.join(dst, common))
        st_ = []
        for k in range(N):
            phi = k * 60.0 + th
            p_ = "turn_%02d_st%d.brep" % (i, k)
            Part.makeCompound(list(station(phi))).exportBrep(_bc_os.path.join(dst, p_))
            st_.append({"brep": p_, "near_fire": abs(((phi + 180.0) % 360.0) - 180.0) < 65.0})
        turn.append({"brep": common, "stations": st_})
    phase = []
    for i in range(int(round(360.0 / BC_PHASE_STEP))):
        p = i * BC_PHASE_STEP
        p_ = "phase_%02d.brep" % i
        Part.makeCompound([Part.makeCompound(list(station(p))), Part.makeCompound(list(station(p + 60.0))),
                           place(valve_group, p, cam_dz(p)), place(fixed0, p),
                           place(line_r(cam_dz(p)), p), place(Part.makeCompound(qev_slide), p, cam_dz(p))]).exportBrep(
            _bc_os.path.join(dst, p_))
        phase.append(p_)
    _bc_json.dump({"fixed_names": [n for n, _ in fixed_list], "turn": turn, "phase": phase,
               "SWEEP_STEP": BC_SWEEP_STEP, "PHASE_STEP": BC_PHASE_STEP},
              open(_bc_os.path.join(dst, "sweep.json"), "w"))


def _bc_joints(dst):
    _bc_os.makedirs(dst)
    qev_mats = {"Rear_plug": "print", "Seat_ring": "print", "Front_cover": "print", "Diaphragm": "rubber",
                "Front_yoke": "print", "Barrel_stub": "steel", "Chamber_tube": "Al", "Pilot_fitting": "bought",
                "Carriage": "print", "Nose_clamp": "print"}
    bodies, fast = [], []

    def body(name, shape, mat):
        sols = shape.Solids
        if len(sols) > 1:
            for i, s in enumerate(sols):
                bodies.append(("%s.%d" % (name, i + 1), s, mat))
        else:
            bodies.append((name, shape, mat))

    for k in (0, 3):                       # FIRE (on the ramp), LOAD (under the feed)
        p = k * 60.0
        dz = cam_dz(p)
        s = "st%d." % k
        for n, sh in qev_closed.items():
            if n == "Tie_rods":
                fast += [("%sTie_studs.%d" % (s, i + 1), s_) for i, s_ in enumerate(place(sh, p, dz).Solids)]
                continue
            body(s + n, place(sh, p, dz), qev_mats[n])
        body(s + "AirTAC", place(valve_body, p, dz), "bought")
        body(s + "AirTAC_plunger", place(valve_plunger, p, dz), "bought")
        body(s + "AirTAC_fittings", place(valve_fit, p, dz), "bought")
        body(s + "Valve_bracket", place(valve_bracket, p, dz), "print")
        body(s + "Line_A", place(line_a, p, dz), "hose")
        body(s + "Line_R", place(line_r(dz), p), "hose")
        body(s + "Finger", place(follower, p, dz), "steel")
        body(s + "Rails", place(rails_pack, p), "Al")
        body(s + "Breech_clamp_upper", place(clamp_upper, p), "print")
        body(s + "Barrel", place(fixed_barrel, p), "steel")
    for n, sh, m in (
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
        body(n, sh, m)
    fast += [(f_.name, f_.body) for f_ in FASTENERS] + [(n_, b_) for n_, b_ in M4_EXC]
    axes = {"Z": [0.0, 0.0, 1.0], "Y": [0.0, 1.0, 0.0], "DM": [_face_n0.x, _face_n0.y, _face_n0.z]}
    Part.makeCompound([b[1] for b in bodies] + [f[1] for f in fast]).exportBrep(_bc_os.path.join(dst, "bodies.brep"))
    _bc_json.dump({"bodies": [[b[0], b[2]] for b in bodies], "fasteners": [f[0] for f in fast], "axes": axes},
              open(_bc_os.path.join(dst, "bodies.json"), "w"))


def bc_write(mech_ok):
    """Write the cache for the current sources (mechanism globals); sets BC_WRITTEN."""
    global BC_WRITTEN
    key = bc_key(REPO)
    root = bc_root(REPO)
    final = _bc_os.path.join(root, key)
    if not bc_dir(REPO, key):
        tmp = _bc_os.path.join(root, ".tmp_%s_%d" % (key, _bc_os.getpid()))
        _bc_shutil.rmtree(tmp, ignore_errors=True)
        _bc_sweep(_bc_os.path.join(tmp, "sweep"))
        _bc_joints(_bc_os.path.join(tmp, "joints"))
        _bc_json.dump({"key": key, "mech_ok": bool(mech_ok), "NAME": NAME, "CLEAR": CLEAR, "PL_L": PL_L,
                   "RAMP_PRESS": RAMP_PRESS, "CK_STEP": CK_STEP},
                  open(_bc_os.path.join(tmp, "done.json"), "w"))
        try:
            _bc_os.rename(tmp, final)
        except OSError:                 # another run wrote the same key meanwhile
            _bc_shutil.rmtree(tmp, ignore_errors=True)
    for d in _bc_glob.glob(_bc_os.path.join(root, "*")):
        if _bc_os.path.basename(d) != key and not _bc_os.path.basename(d).startswith(".tmp_"):
            _bc_shutil.rmtree(d, ignore_errors=True)
    BC_WRITTEN = final
    return final
