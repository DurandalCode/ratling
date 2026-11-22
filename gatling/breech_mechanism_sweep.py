# -*- coding: utf-8 -*-
"""
Full-turn clearance sweep of the gatling breech mechanism (separate from the build).

Reads the poses from the mechanism's body cache (gatling/breech_cache.py: written by
breech_mechanism.py, keyed by the sources; without it the mechanism is built here once as a
library, which writes it) and hands them to parallel freecadcmd workers (one OCC distance
query runs on one core; the poses are independent):

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

SWEEP_WORKERS (environment) sets the number of workers, default cores - 2. 2026-11-22: a task
is one station in one pose (or the hub in one pose, or one phase); the workers take the next
free task as they finish (a pose per worker left most of them idle at the end), and a solid
pair whose bounding boxes are farther apart than the nearest gap found so far for its line is
not measured (it cannot lower the minimum: the boxes come from triangulations of at most
0.5 mm deflection, both may sit inside: BOX_MARGIN = 1.5 mm); a radial bound does the same for
a part inside a ring's bore. The hub's lines share one bound (the report keeps their minimum and
its name) and a solid of more than FACE_MANY faces is measured by its faces near the other one
(the hub took 138 s a pose). Results are remembered by the hashes of the two shapes' BREP
(exports/gatling_breech_mechanism/memo/), so a repeat or a run after an edit measures only the
pairs with a changed part. The reported minima are the same (diffed: 791 -> 162 s from
scratch, ~3 s again).
Report: exports/gatling_breech_mechanism/gatling_breech_mechanism_sweep_report.txt
"""
import json
import math
import os
import resource
import shutil
import subprocess
import sys
import tempfile
import time

import FreeCAD as App
import Part

_WORKER = os.environ.get("BREECH_SWEEP_TASK")
BOX_MARGIN = 1.5        # mm: two boxes from 0.5 mm triangulations may each sit 0.5 inside their shapes


def _near(ba, bb_, pad):
    ba2 = App.BoundBox(ba.XMin - pad, ba.YMin - pad, ba.ZMin - pad,
                       ba.XMax + pad, ba.YMax + pad, ba.ZMax + pad)
    return ba2.intersect(bb_)


def _box_dist(a, b):
    dx = max(0.0, a.XMin - b.XMax, b.XMin - a.XMax)
    dy = max(0.0, a.YMin - b.YMax, b.YMin - a.YMax)
    dz = max(0.0, a.ZMin - b.ZMax, b.ZMin - a.ZMax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _r_box(b):
    """(lower bound of the radius from the pack axis, upper bound) over a box."""
    dx = max(0.0, b.XMin, -b.XMax)
    dy = max(0.0, b.YMin, -b.YMax)
    rx, ry = max(abs(b.XMin), abs(b.XMax)), max(abs(b.YMin), abs(b.YMax))
    return math.sqrt(dx * dx + dy * dy), math.sqrt(rx * rx + ry * ry)


_AXIS = None


class _Sh:
    """A shape with its solids, their boxes and radial bounds about the pack axis, taken once.
    exact_r: the solid's distance from the axis by distToShape (the fixed parts; a ring's box
    holds the whole pack, its bore does not), else from its box."""

    def __init__(self, s, exact_r=False):
        global _AXIS
        self.s, self.bb = s, s.BoundBox
        self.sol = []
        for x in (s.Solids or [s]):
            bx = x.BoundBox
            r0, r1 = _r_box(bx)
            if exact_r and r0 == 0.0:
                if _AXIS is None:
                    _AXIS = Part.makeLine(App.Vector(0, 0, -1e4), App.Vector(0, 0, 1e4))
                r0 = _AXIS.distToShape(x)[0]
            self.sol.append(_Solid(x, bx, r0, r1))


class _Solid:
    __slots__ = ("s", "bb", "r0", "r1", "_faces", "_fine")

    def __init__(self, s, bb, r0, r1):
        self.s, self.bb, self.r0, self.r1, self._faces, self._fine = s, bb, r0, r1, None, False

    def faces(self):
        if self._faces is None:
            self._faces = [(f_, f_.BoundBox) for f_ in self.s.Faces]
        return self._faces

    def fine_r1(self):
        """Upper radius from a 0.5 mm triangulation, its nodes + 1 mm (a round part's box corners
        sit at 1.41 times its radius; the surface strays at most the deflection from the mesh)."""
        if not self._fine and self.s.Faces:
            pts = self.s.tessellate(0.5)[0]
            if pts:
                self.r1 = min(self.r1, max(math.hypot(p_.x, p_.y) for p_ in pts) + 1.0)
            self._fine = True
        return self.r1


FACE_MANY = 300         # a solid with more faces is measured by its faces near the other one


def _box_of(faces):
    b = App.BoundBox()
    for _, fb in faces:
        b.add(fb)
    return b


def _dist(x, y, r):
    """x.distToShape(y) where it is below r (exact there; >= r otherwise). A solid with many faces
    (the rim's 120 teeth) is measured by its faces whose boxes come within r + BOX_MARGIN of the
    other's box, and the other's faces by the same test against those; one solid wholly inside
    the other still gives 0."""
    if r >= 99.0 or max(len(x.faces()), len(y.faces())) <= FACE_MANY or not x.s.Faces or not y.s.Faces:
        return x.s.distToShape(y.s)[0]
    lim = r + BOX_MARGIN
    nx = [fx for fx in x.faces() if _box_dist(fx[1], y.bb) <= lim]
    ny = [fy for fy in y.faces() if nx and _box_dist(fy[1], _box_of(nx)) <= lim] if nx else []
    nx = [fx for fx in nx if ny and _box_dist(fx[1], _box_of(ny)) <= lim] if ny else []
    d = Part.makeCompound([f_ for f_, _ in nx]).distToShape(Part.makeCompound([f_ for f_, _ in ny]))[0] \
        if nx and ny else 99.0
    if d > 0.0 and x.s.ShapeType == "Solid" and y.s.ShapeType == "Solid" and (
            x.s.isInside(y.s.Vertexes[0].Point, 1e-7, True) or y.s.isInside(x.s.Vertexes[0].Point, 1e-7, True)):
        d = 0.0
    return d


def _lb(x, y):
    return max(_box_dist(x.bb, y.bb), y.r0 - x.r1, x.r0 - y.r1)


def _gap(a, b, pad=2.0, bound=99.0):
    """Min distance solid by solid (99 = farther than pad), as the build's gap(). A pair is
    skipped when a lower bound of its distance (box to box, or radial: one solid inside the
    other's bore) is past the best so far, or past `bound` (the line's minimum), by BOX_MARGIN:
    the result is exact below `bound` and >= `bound` otherwise."""
    if not _near(a.bb, b.bb, pad):
        return 99.0
    cand = []
    for x in a.sol:
        if not _near(x.bb, b.bb, pad):
            continue
        for y in b.sol:
            if _near(x.bb, y.bb, pad):
                cand.append((_lb(x, y), x, y))
    cand.sort(key=lambda c_: c_[0])
    g = 99.0
    for lb, x, y in cand:
        r = min(g, bound)
        if lb - BOX_MARGIN >= r:
            break
        if r < 99.0 and max(len(x.s.Faces), len(y.s.Faces)) > FACE_MANY:
            x.fine_r1()
            y.fine_r1()
            if _lb(x, y) - BOX_MARGIN >= r:
                continue
        g = min(g, _dist(x, y, r))
    return g


def _read(path):
    s = Part.Shape()
    s.read(path)
    return s


def _claim(work, i):
    try:
        os.close(os.open(os.path.join(work, "claim_%04d" % i), os.O_CREAT | os.O_EXCL))
        return True
    except FileExistsError:
        return False


if _WORKER:
    # ------------------------------------------------------------ worker: free tasks until none is left
    _w0 = time.time()
    task = json.load(open(_WORKER))
    cdir = task["cache"]
    fixed = [_Sh(s_, exact_r=True) for s_ in _read(os.path.join(cdir, "fixed.brep")).childShapes()]
    for f_, h_ in zip(fixed, task["fixed_hashes"]):
        f_.h = h_
    names = task["fixed_names"]
    memo = json.load(open(task["memo"])) if os.path.exists(task["memo"]) else {}
    used, fresh = set(), {}
    out = dict(task["seed"])
    print("worker: fixed read in %.1f s, %d remembered gaps" % (time.time() - _w0, len(memo)), flush=True)

    spent = {}

    def measure(a, b, bound, line):
        """_gap(a, b, bound=bound), or the remembered one for the same two shapes (by the hash of
        their BREP): [value, bound it was measured with] is exact below that bound and only a
        floor above it, so it serves when it is exact or its bound is at least this one."""
        mk = a.h + "|" + b.h + "|" + line
        m = fresh.get(mk) or memo.get(mk)
        if m is not None and (m[0] < m[1] or m[1] >= bound):
            used.add(mk)
            return m[0]
        v = _gap(a, b, bound=bound)
        fresh[mk] = [v, bound, line]
        return v

    def low(key, a, b):
        t_ = time.time()
        out[key] = min(out.get(key, 99.0), measure(a, b, out.get(key, 99.0), key))
        spent[key] = spent.get(key, 0.0) + time.time() - t_

    _common = {}

    def read_hashed(path):
        sh_ = [_Sh(s_) for s_ in _read(os.path.join(cdir, path)).childShapes()]
        for i_, x_ in enumerate(sh_):
            x_.h = "%s:%d" % (task["file_hashes"][path], i_)
        return sh_

    def common_pose(path):
        if path not in _common:
            _common.clear()
            _common[path] = read_hashed(path)
        return _common[path]

    n_done = 0
    for ti, t in enumerate(task["tasks"]):
        if not _claim(task["work"], ti):
            continue
        t0 = time.time()
        if t["kind"] == "station":
            star, rim, gear_a, ramp_fire, pinion = common_pose(t["common"])
            mv, fx, pl, lr = read_hashed(t["brep"])
            for n, f in zip(names, fixed):
                for g_ in (mv, fx, pl, lr):
                    low(n, g_, f)
            for g_ in (mv, fx, pl, lr):
                low("star", g_, star)
            low("gear A (meshes the rim)", fx, gear_a)
            low("gear A (meshes the rim)", mv, gear_a)
            low("crank gear (meshes the rim)", fx, pinion)
            low("crank gear (meshes the rim)", mv, pinion)
            if t["near_fire"]:
                low("fixed ramp (bodies and lines, not plungers)", mv, ramp_fire)
                low("fixed ramp (bodies and lines, not plungers)", lr, ramp_fire)
        elif t["kind"] == "hub":
            # The report keeps only the nearest fixed part to the hub (value and name), so one
            # bound serves all the hub's lines: a part farther than the nearest so far is not
            # measured to the end (its own line may stay above its true gap).
            rim = common_pose(t["common"])[1]
            hb = min([v_ for k_, v_ in out.items() if k_.startswith("hub vs ")] + [99.0])
            order = sorted(zip(names, fixed), key=lambda nf_: min(
                [_lb(x_, y_) for x_ in rim.sol for y_ in nf_[1].sol] + [99.0]))
            for n, f in order:
                t_ = time.time()
                v_ = measure(rim, f, hb, "hub vs " + n)
                out["hub vs " + n] = min(out.get("hub vs " + n, 99.0), v_)
                hb = min(hb, v_)
                spent["hub vs " + n] = spent.get("hub vs " + n, 0.0) + time.time() - t_
        else:
            a, b, valve, own_fx, line, own_qev = read_hashed(t["brep"])
            low("neighbours", a, b)
            low("own", valve, own_fx)
            low("own", line, own_qev)
        n_done += 1
        print("task %3d %-7s %-22s %6.1f s" % (ti, t["kind"], t.get("brep") or t.get("common"), time.time() - t0),
              flush=True)
    for k_, v_ in sorted(spent.items(), key=lambda kv: -kv[1])[:6]:
        print("  %6.1f s  %s" % (v_, k_), flush=True)
    print("worker: %d tasks in %.0f s, %d gaps remembered, %d measured, peak RSS %.0f MB" % (
        n_done, time.time() - _w0, len(used), len(fresh),
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20 if sys.platform == "darwin" else 1 << 10)),
        flush=True)
    json.dump({"res": out, "spent": spent, "memo": dict({k_: memo[k_] for k_ in used}, **fresh)},
              open(task["out"], "w"))
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
exec(open(os.path.join(REPO, "gatling", "breech_cache.py")).read(), globals())
_cdir, _built = bc_load(REPO)
_meta = json.load(open(os.path.join(_cdir, "done.json")))
_mech_ok = _meta["mech_ok"]
NAME, CLEAR, PL_L, RAMP_PRESS = _meta["NAME"], _meta["CLEAR"], _meta["PL_L"], _meta["RAMP_PRESS"]
OUT_DIR = os.path.join(REPO, "exports", "gatling_breech_mechanism")
_sw_dir = os.path.join(_cdir, "sweep")
_sw = json.load(open(os.path.join(_sw_dir, "sweep.json")))
SWEEP_STEP, PHASE_STEP = _sw["SWEEP_STEP"], _sw["PHASE_STEP"]
fixed_names = _sw["fixed_names"]
print("sweep: %s (%s, fast checks %s)" % (_cdir, ("built in %.0f s" % _built) if _built else "cached",
                                          "OK" if _mech_ok else "FAIL"), flush=True)

# Heaviest first: the hub (its rim's 120 teeth), then the stations, then the phases.
tasks = ([{"kind": "hub", "common": t["brep"]} for t in _sw["turn"]]
         + [{"kind": "station", "common": t["brep"], "brep": s["brep"], "near_fire": s["near_fire"]}
            for t in _sw["turn"] for s in t["stations"]]
         + [{"kind": "phase", "brep": p} for p in _sw["phase"]])
# Remembered gaps (2026-11-22): keyed by the hashes of the two shapes' BREP, kept across
# rebuilds, so after an edit only the pairs with a changed part are measured again.
import hashlib
MEMO_VERSION = "sweep 3: pad 2.0"
MEMO = os.path.join(OUT_DIR, "memo", NAME + "_sweep_memo.json")


def _sha(b_):
    return hashlib.sha1(b_).hexdigest()[:20]


fixed_hashes = [_sha(c_.exportBrepToString().encode()) for c_ in _read(os.path.join(_sw_dir, "fixed.brep")).childShapes()]
file_hashes = {}
for t_ in tasks:
    for k_ in ("common", "brep"):
        if k_ in t_ and t_[k_] not in file_hashes:
            file_hashes[t_[k_]] = _sha(open(os.path.join(_sw_dir, t_[k_]), "rb").read())
_memo = {}
if os.path.exists(MEMO):
    _m = json.load(open(MEMO))
    _memo = _m["gaps"] if _m.get("version") == MEMO_VERSION else {}
# Seed each line with the exact remembered gaps of pairs that are in this run (same hashes):
# the line's minimum is at most that, and the pair itself is looked up exact, so the minimum
# is the same; the remembered floors then serve too (a first measure ran with no bound).
_ids = set(fixed_hashes) | set(file_hashes.values())
seed = {}
for k_, m_ in _memo.items():
    if len(m_) > 2 and m_[0] < m_[1] and all(h_.split(":")[0] in _ids for h_ in k_.split("|")[:2]):
        seed[m_[2]] = min(seed.get(m_[2], 99.0), m_[0])
WORK = tempfile.mkdtemp(prefix="breech_sweep_")
_memo_in = os.path.join(WORK, "memo.json")
json.dump(_memo, open(_memo_in, "w"))
n_workers = int(os.environ.get("SWEEP_WORKERS", max(1, (os.cpu_count() or 4) - 2)))
n_workers = max(1, min(n_workers, len(tasks)))
exe = os.path.join(App.getHomePath(), "bin", "freecadcmd")
if not os.path.exists(exe):
    exe = shutil.which("freecadcmd") or exe
me = os.path.join(REPO, "gatling", "breech_mechanism_sweep.py")
procs = []
for i in range(n_workers):
    task_path = os.path.join(WORK, "task_%02d.json" % i)
    json.dump({"cache": _sw_dir, "work": WORK, "tasks": tasks, "fixed_names": fixed_names,
               "fixed_hashes": fixed_hashes, "file_hashes": file_hashes, "memo": _memo_in, "seed": seed,
               "out": os.path.join(WORK, "out_%02d.json" % i)}, open(task_path, "w"))
    env = dict(os.environ, BREECH_SWEEP_TASK=task_path)
    log = open(os.path.join(WORK, "worker_%02d.log" % i), "w")
    procs.append((i, subprocess.Popen([exe, me], env=env, stdout=log, stderr=subprocess.STDOUT),
                  os.path.join(WORK, "out_%02d.json" % i)))
print("sweep: %d tasks on %d workers (logs in %s)" % (len(tasks), len(procs), WORK), flush=True)
results, failed, spent, memo_new = {}, [], {}, {}
for i, pr, outp in procs:
    pr.wait()
    if pr.returncode not in (0, None) or not os.path.exists(outp):
        failed.append(i)
        continue
    _o = json.load(open(outp))
    for k, v in _o["res"].items():
        results[k] = min(results.get(k, 99.0), v)
    for k, v in _o["spent"].items():
        spent[k] = spent.get(k, 0.0) + v
    for k, v in _o["memo"].items():
        # Two workers may hold the same pair: keep the exact one, else the higher bound.
        o_ = memo_new.get(k)
        if o_ is None or (o_[0] >= o_[1] and (v[0] < v[1] or v[1] > o_[1])):
            memo_new[k] = v
_claimed = len([f for f in os.listdir(WORK) if f.startswith("claim_")])
if _claimed != len(tasks):
    failed.append("%d of %d tasks claimed" % (_claimed, len(tasks)))
for i, _, _ in procs:
    _wl = open(os.path.join(WORK, "worker_%02d.log" % i)).read().strip().splitlines()
    print("  worker %02d: %s" % (i, next((l_ for l_ in reversed(_wl) if l_.startswith("worker:")), "no summary")), flush=True)
print("sweep: workers done in %.0f s total; worker time by line (s):" % (time.time() - _t0), flush=True)
for k, v in sorted(spent.items(), key=lambda kv: -kv[1])[:10]:
    print("  %7.1f  %s" % (v, k), flush=True)
if not failed:
    os.makedirs(os.path.dirname(MEMO), exist_ok=True)
    json.dump({"version": MEMO_VERSION, "gaps": memo_new}, open(MEMO + ".tmp", "w"))
    os.replace(MEMO + ".tmp", MEMO)

sweep_checks = [("mechanism build and fast checks", _mech_ok),
                ("all %d workers finished%s" % (len(procs), (" (failed: %s, logs in %s)" % (failed, WORK)) if failed else ""),
                 not failed)]
# The hub against every fixed part, by name (2026-11-22: one min over all hid which part it met).
_hub_v, _hub_n = min((v, k[len("hub vs "):]) for k, v in list(results.items()) + [("hub vs nothing", 99.0)]
                     if k.startswith("hub vs "))
results["hub (rim, lower clamp halves, bearing seat, retainer bolts) vs fixed parts (nearest: %s)" % _hub_n] = _hub_v
for n in fixed_names + ["star", "gear A (meshes the rim)", "crank gear (meshes the rim)",
                                        "fixed ramp (bodies and lines, not plungers)",
                                        "hub (rim, lower clamp halves, bearing seat, retainer bolts) vs fixed parts"
                                        " (nearest: %s)" % _hub_n]:
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
