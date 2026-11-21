# -*- coding: utf-8 -*-
"""
Full-turn clearance sweep of the gatling breech mechanism (separate from the build).

Builds gatling/breech_mechanism.py once as a library (build + fast checks, no
scene, no export), writes every pose to BREP and hands the poses to parallel
freecadcmd workers (one OCC distance query runs on one core; the poses are
independent):

- every 3 deg of pack turn over a station pitch (the stations are identical):
  each station's moving parts, fixed parts, plunger and line R against every
  fixed part - star in its pose, guard, feed head, TPU lip, cup, the star train
  and its box, the ramp's mount block, the fixed ramp (it stays in the press
  position; bodies and lines only: the plungers are meant to touch it), the
  front bearing disk, the rear plate and its struts, the feed gate and its
  cable, the pack drive
  (crank bracket, bevel pair, shafts, bearings; the room for the hand; the crank
  arm and knob in all their poses over a crank turn, so every pose of the crank
  meets every pose of the pack), carry handle, strap rings, the fist on the
  handle, the tripod pad and the tripod's ball; the gears that mesh the rim (star train gear A, crank gear 60)
  against the stations; the hub (rim, lower clamp halves, bearing seat and its
  retainer bolts) against the fixed parts; since 2026-11-21 the fasteners too: the
  stations' bolts move with them, the frame's M6 studs and the fixed parts' M3 bolts stand;
- every 5 deg of phase: whole stations (valve group and lines included)
  against their neighbours, and the valve group and line R against their own
  station.

    freecadcmd -c "REPO='$PWD'; exec(open('gatling/breech_mechanism_sweep.py').read())"

SWEEP_WORKERS (environment) sets the number of workers, default cores - 2.
Report: exports/gatling_breech_mechanism/gatling_breech_mechanism_sweep_report.txt
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import FreeCAD as App
import Part

_WORKER = os.environ.get("BREECH_SWEEP_TASK")


def _near(ba, bb_, pad):
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad,
                       ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    return ba2.intersect(bb_)


def _gap(a, b, pad=2.0):
    if not _near(a.BoundBox, b.BoundBox, pad):
        return 99.0
    g = 99.0
    for x in (a.Solids or [a]):
        bx = x.BoundBox
        if not _near(bx, b.BoundBox, pad):
            continue
        for y in (b.Solids or [b]):
            if _near(bx, y.BoundBox, pad):
                g = min(g, x.distToShape(y)[0])
    return g


def _read(path):
    s = Part.Shape()
    s.read(path)
    return s


if _WORKER:
    # ------------------------------------------------------------ worker: one batch of poses
    task = json.load(open(_WORKER))
    fixed = _read(task["fixed"]).childShapes()
    names = task["fixed_names"]
    out = {}

    def low(key, v):
        out[key] = min(out.get(key, 99.0), v)

    for pose in task["turn"]:
        sh = _read(pose["brep"]).childShapes()
        star, rim, gear_a, ramp_fire, pinion = sh[0], sh[1], sh[2], sh[3], sh[4]
        st = sh[5:]
        for k, near_fire in enumerate(pose["near_fire"]):
            mv, fx, pl, lr = st[4 * k:4 * k + 4]
            for n, f in zip(names, fixed):
                for g_ in (mv, fx, pl, lr):
                    low(n, _gap(g_, f))
            for g_ in (mv, fx, pl, lr):
                low("star", _gap(g_, star))
            low("gear A (meshes the rim)", min(_gap(fx, gear_a), _gap(mv, gear_a)))
            low("crank gear (meshes the rim)", min(_gap(fx, pinion), _gap(mv, pinion)))
            if near_fire:
                low("fixed ramp (bodies and lines, not plungers)", min(_gap(mv, ramp_fire), _gap(lr, ramp_fire)))
        for f in fixed:
            low("hub (rim, lower clamp halves, bearing seat, retainer bolts) vs fixed parts", _gap(rim, f))
    for ph in task["phase"]:
        a, b, valve, own_fx, line, own_qev = _read(ph).childShapes()
        low("neighbours", _gap(a, b))
        low("own", min(_gap(valve, own_fx), _gap(line, own_qev)))
    json.dump(out, open(task["out"], "w"))
    raise SystemExit(0)

# ---------------------------------------------------------------- parent
try:
    REPO
except NameError:
    try:
        REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        REPO = os.path.expanduser("~/ratling")

_t0 = time.time()
BREECH_MECH_LIBRARY = True
_mech_ok = True
try:
    exec(open(os.path.join(REPO, "gatling", "breech_mechanism.py")).read(), globals())
except SystemExit as _e:
    _mech_ok = _e.code in (0, None)
BREECH_MECH_LIBRARY = False
print("sweep: mechanism built in %.0f s (fast checks %s)" % (time.time() - _t0, "OK" if _mech_ok else "FAIL"), flush=True)

SWEEP_STEP = 3.0
PHASE_STEP = 5.0
WORK = tempfile.mkdtemp(prefix="breech_sweep_")
fixed_list = ([("guard", feed_guard), ("feed head", feed_head), ("TPU lip", feed_lip), ("cup", feed_cup),
               ("ramp mount block", guide_block), ("front bearing disk", brg_f),
               ("rear plate and struts", Part.makeCompound([mqr_plate, rear_struts])),
               ("feed gate and its cable", Part.makeCompound([gate_housing, gate_pin, gate_pin_open, gate_cable])),
               ("carry handle", carry_handle), ("strap rings", sling), ("room for the hand", hand_space),
               ("crank arm and knob, every %.0f deg of a crank turn" % CK_STEP,
                Part.makeCompound([s_ for pose_ in crank_poses for s_ in pose_])),
               ("fist on the carry handle", carry_hand), ("tripod pad", tripod_pad), ("tripod ball and post", tripod_ball),
               ("frame M6 studs and nuts", frame_studs),
               ("fixed M3 bolts (feed, ramp, liner, carry, keel, crank brackets)",
                Part.makeCompound([f_.body for f_ in FEED_FAST + RAMP_FAST + LINER_FAST + CARRY_FAST + TRIPOD_FAST + CRANK_FAST])),
               ("front bearing housing and its rear retainer", Part.makeCompound([brg_housing, brg_ret_out])),
               ("star shaft collar", star_collar)]
              + [(n, s) for n, s in train_parts if not n.startswith("gear A")]
              + [(n, s) for n, s in drive_parts if not n.startswith("crank gear")])
fixed_path = os.path.join(WORK, "fixed.brep")
Part.makeCompound([s for _, s in fixed_list]).exportBrep(fixed_path)

turn_poses = []
for _i in range(int(round(60.0 / SWEEP_STEP))):
    th = _i * SWEEP_STEP
    d = ((th + 30.0) % 60.0) - 30.0
    parts = [star_at(d), rot(Part.makeCompound([pack_hub, brg_ret_in] + [f_.body for f_ in HUB_FAST]), th), gear_a, ramp_fire,
             crank_gear]
    near_fire = []
    for k in range(N):
        phi = k * 60.0 + th
        parts += list(station(phi))
        near_fire.append(abs(((phi + 180.0) % 360.0) - 180.0) < 65.0)
    path = os.path.join(WORK, "turn_%02d.brep" % _i)
    Part.makeCompound(parts).exportBrep(path)
    turn_poses.append({"brep": path, "near_fire": near_fire})
phase_files = []
for _i in range(int(round(360.0 / PHASE_STEP))):
    p = _i * PHASE_STEP
    path = os.path.join(WORK, "phase_%02d.brep" % _i)
    Part.makeCompound([Part.makeCompound(list(station(p))), Part.makeCompound(list(station(p + 60.0))),
                       place(valve_group, p, cam_dz(p)), place(fixed0, p),
                       place(line_r(cam_dz(p)), p), place(Part.makeCompound(qev_slide), p, cam_dz(p))]).exportBrep(path)
    phase_files.append(path)
print("sweep: %d turn poses + %d phases written in %.0f s" % (len(turn_poses), len(phase_files), time.time() - _t0), flush=True)

n_workers = int(os.environ.get("SWEEP_WORKERS", max(1, (os.cpu_count() or 4) - 2)))
batches = [{"turn": [], "phase": []} for _ in range(n_workers)]
for i, t in enumerate(turn_poses):
    batches[i % n_workers]["turn"].append(t)
for i, f in enumerate(phase_files):
    batches[(len(turn_poses) + i) % n_workers]["phase"].append(f)
exe = os.path.join(App.getHomePath(), "bin", "freecadcmd")
if not os.path.exists(exe):
    exe = shutil.which("freecadcmd") or exe
me = os.path.join(REPO, "gatling", "breech_mechanism_sweep.py")
procs = []
for i, b in enumerate(batches):
    if not b["turn"] and not b["phase"]:
        continue
    task_path = os.path.join(WORK, "task_%02d.json" % i)
    b.update({"fixed": fixed_path, "fixed_names": [n for n, _ in fixed_list],
              "out": os.path.join(WORK, "out_%02d.json" % i)})
    json.dump(b, open(task_path, "w"))
    env = dict(os.environ, BREECH_SWEEP_TASK=task_path)
    log = open(os.path.join(WORK, "worker_%02d.log" % i), "w")
    procs.append((i, subprocess.Popen([exe, me], env=env, stdout=log, stderr=subprocess.STDOUT), b["out"]))
print("sweep: %d workers started" % len(procs), flush=True)
results, failed = {}, []
for i, pr, outp in procs:
    pr.wait()
    if pr.returncode not in (0, None) or not os.path.exists(outp):
        failed.append(i)
        continue
    for k, v in json.load(open(outp)).items():
        results[k] = min(results.get(k, 99.0), v)
print("sweep: workers done in %.0f s total" % (time.time() - _t0), flush=True)

sweep_checks = [("mechanism build and fast checks", _mech_ok),
                ("all %d workers finished%s" % (len(procs), (" (failed: %s, logs in %s)" % (failed, WORK)) if failed else ""),
                 not failed)]
for n in [n for n, _ in fixed_list] + ["star", "gear A (meshes the rim)", "crank gear (meshes the rim)",
                                        "fixed ramp (bodies and lines, not plungers)",
                                        "hub (rim, lower clamp halves, bearing seat, retainer bolts) vs fixed parts"]:
    v = results.get(n, 99.0)
    # The pressed ramp sits PL_L - RAMP_PRESS (0.5) off the valve bodies by design.
    lim = (PL_L - RAMP_PRESS - 0.05) if n.startswith("fixed ramp") else CLEAR - 1e-3
    sweep_checks.append(("full turn: stations vs %s %.2f >= %.2f" % (n, v, lim), v >= lim))
sweep_checks += [
    ("every %.0f deg of phase: whole stations vs neighbours %.2f" % (PHASE_STEP, results.get("neighbours", -1)),
     results.get("neighbours", -1) >= CLEAR - 1e-6),
    ("every %.0f deg of phase: valve group and line R vs own station %.2f" % (PHASE_STEP, results.get("own", -1)),
     results.get("own", -1) >= CLEAR - 1e-6),
]
sweep_report = [NAME + " — full-turn sweep",
                "  step                  : %.0f deg of pack turn over a station pitch; %.0f deg of phase"
                % (SWEEP_STEP, PHASE_STEP),
                "  workers               : %d (freecadcmd processes)" % len(procs),
                "  time                  : %.0f s" % (time.time() - _t0)]
sweep_report += ["  [%s] %s" % ("OK " if ok else "FAIL", n) for n, ok in sweep_checks]
print("\n".join(sweep_report))
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, NAME + "_sweep_report.txt"), "w") as f:
    f.write("\n".join(sweep_report) + "\n")
if not failed:
    shutil.rmtree(WORK, ignore_errors=True)
if not all(ok for _, ok in sweep_checks):
    raise SystemExit("gatling breech mechanism sweep has [FAIL] checks")
