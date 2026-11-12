#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot sync daemon: GPT work folder ↔ pistol/mask_overlays.

Polls shell .brep on both sides and copies changes. Tiny HTTP control plane
on 127.0.0.1 (default :8765). Stdlib only — no FreeCAD in the watcher.

  python3 experiments/gpt-mask/mask_sync.py out --rebuild   # once → ../mechanismus
  python3 experiments/gpt-mask/mask_hot.py                  # watches that folder

  curl -X POST http://127.0.0.1:8765/in
  curl -X POST http://127.0.0.1:8765/out
  curl -X POST http://127.0.0.1:8765/rebuild
  curl -X POST http://127.0.0.1:8765/build-live
  curl http://127.0.0.1:8765/status

Sentinels in the work folder (touch to trigger): .mask_in  .mask_out  .mask_rebuild

Do not put this script in the GPT workspace.
"""

from __future__ import print_function

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
sys.path.insert(0, HERE)
from mask_map import (  # noqa: E402
    D_NAME_TO_LIVE,
    LIVE_TO_D_STEM,
    SHELL_OVERLAY_VARS,
    default_mask_dir,
)

OVERLAY_DIR = os.path.join(REPO, "pistol", "mask_overlays")
SYNC = os.path.join(HERE, "mask_sync.py")


def log(msg):
    print("mask_hot: %s" % msg, flush=True)


def run_sync(args):
    cmd = [sys.executable, SYNC] + list(args)
    r = subprocess.call(cmd, cwd=REPO)
    if r != 0:
        log("mask_sync %s failed (%d)" % (" ".join(args), r))
    return r


def fingerprint(path):
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def same_file(a, b):
    fa, fb = fingerprint(a), fingerprint(b)
    if not fa or not fb:
        return False
    if fa[1] != fb[1]:
        return False
    # cheap content check for equal size
    with open(a, "rb") as fa_, open(b, "rb") as fb_:
        return fa_.read() == fb_.read()


class HotState(object):
    def __init__(self, work, interval, quiet_in):
        self.work = os.path.abspath(work)
        self.interval = interval
        self.quiet_in = quiet_in
        self.lock = threading.Lock()
        self.ignore_until = {}  # path -> monotonic deadline
        self.last_work = {}
        self.last_overlay = {}
        self.stats = {"in": 0, "out_overlay": 0, "errors": 0}
        self._seed()

    def _ignore(self, path, seconds=2.0):
        self.ignore_until[path] = time.monotonic() + seconds

    def _ignored(self, path):
        until = self.ignore_until.get(path)
        if until is None:
            return False
        if time.monotonic() >= until:
            self.ignore_until.pop(path, None)
            return False
        return True

    def work_shell_paths(self):
        """Map live_var → best source path currently in the work folder."""
        out = {}
        parts = os.path.join(self.work, "parts")
        exports = os.path.join(self.work, "exports")
        for live, stem in LIVE_TO_D_STEM.items():
            names = [n for n, v in D_NAME_TO_LIVE.items() if v == live]
            cands = []
            for n in names:
                cands.append(os.path.join(exports, n + ".brep"))
                cands.append(os.path.join(self.work, n + ".brep"))
            cands.append(os.path.join(parts, stem + ".brep"))
            for p in cands:
                if os.path.isfile(p):
                    out[live] = p
                    break
        return out

    def overlay_paths(self):
        out = {}
        if not os.path.isdir(OVERLAY_DIR):
            return out
        for live in SHELL_OVERLAY_VARS:
            p = os.path.join(OVERLAY_DIR, live + ".brep")
            if os.path.isfile(p):
                out[live] = p
        return out

    def _seed(self):
        for live, path in self.work_shell_paths().items():
            self.last_work[live] = fingerprint(path)
        for live, path in self.overlay_paths().items():
            self.last_overlay[live] = fingerprint(path)

    def copy_to_overlay(self, live, src):
        os.makedirs(OVERLAY_DIR, exist_ok=True)
        dst = os.path.join(OVERLAY_DIR, live + ".brep")
        if same_file(src, dst):
            self.last_work[live] = fingerprint(src)
            self.last_overlay[live] = fingerprint(dst)
            return False
        shutil.copy2(src, dst)
        self._ignore(dst)
        self._ignore(src)
        self.last_work[live] = fingerprint(src)
        self.last_overlay[live] = fingerprint(dst)
        self.stats["in"] += 1
        log("in  %s ← %s" % (live + ".brep", src))
        return True

    def copy_to_work(self, live, src):
        stem = LIVE_TO_D_STEM[live]
        parts = os.path.join(self.work, "parts")
        os.makedirs(parts, exist_ok=True)
        dst = os.path.join(parts, stem + ".brep")
        if same_file(src, dst):
            self.last_overlay[live] = fingerprint(src)
            self.last_work[live] = fingerprint(dst)
            return False
        shutil.copy2(src, dst)
        # also mirror FreeCAD export name if exports/ exists
        exports = os.path.join(self.work, "exports")
        for n, v in D_NAME_TO_LIVE.items():
            if v == live:
                os.makedirs(exports, exist_ok=True)
                exp = os.path.join(exports, n + ".brep")
                shutil.copy2(src, exp)
                self._ignore(exp)
        self._ignore(dst)
        self._ignore(src)
        self.last_overlay[live] = fingerprint(src)
        self.last_work[live] = fingerprint(dst)
        self.stats["out_overlay"] += 1
        log("out %s → parts/%s.brep" % (live + ".brep", stem))
        return True

    def poll_once(self):
        with self.lock:
            # work → overlays
            for live, path in self.work_shell_paths().items():
                if self._ignored(path):
                    continue
                fp = fingerprint(path)
                if fp and fp != self.last_work.get(live):
                    try:
                        self.copy_to_overlay(live, path)
                    except Exception as e:
                        self.stats["errors"] += 1
                        log("in error %s: %s" % (live, e))

            # overlays → work
            for live, path in self.overlay_paths().items():
                if self._ignored(path):
                    continue
                fp = fingerprint(path)
                if fp and fp != self.last_overlay.get(live):
                    try:
                        self.copy_to_work(live, path)
                    except Exception as e:
                        self.stats["errors"] += 1
                        log("out error %s: %s" % (live, e))

            self._check_sentinels()

    def _check_sentinels(self):
        for name, action in (
            (".mask_in", self.force_in),
            (".mask_out", self.force_out),
            (".mask_rebuild", self.force_rebuild),
        ):
            p = os.path.join(self.work, name)
            if os.path.isfile(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
                action()

    def force_in(self):
        log("force in")
        if self.quiet_in:
            # only copy changed/present shell files without dying on partial
            for live, path in self.work_shell_paths().items():
                try:
                    self.copy_to_overlay(live, path)
                except Exception as e:
                    self.stats["errors"] += 1
                    log("in error %s: %s" % (live, e))
        else:
            run_sync(["in", self.work])
            self._seed()

    def force_out(self):
        log("force out (no rebuild)")
        run_sync(["out", self.work])
        self._seed()

    def force_rebuild(self):
        log("force rebuild + out")
        run_sync(["out", self.work, "--rebuild"])
        self._seed()

    def build_live(self):
        log("build live hammer_assembly")
        env = os.environ.copy()
        env.setdefault("LANG", "C.UTF-8")
        env.setdefault("LC_ALL", "C.UTF-8")
        cmd = [
            "freecadcmd",
            "-c",
            "REPO=%r; CHECKS=False; exec(open(%r).read())"
            % (REPO, os.path.join(REPO, "pistol", "hammer_assembly.py")),
        ]
        return subprocess.call(cmd, cwd=REPO, env=env)

    def status(self):
        return {
            "work": self.work,
            "overlays": OVERLAY_DIR,
            "interval": self.interval,
            "stats": self.stats,
            "shell_in_work": sorted(self.work_shell_paths().keys()),
            "shell_overlays": sorted(self.overlay_paths().keys()),
        }


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, code, obj):
            body = json.dumps(obj, indent=2).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _text(self, code, text):
            body = text.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.rstrip("/") in ("", "/help"):
                self._text(
                    200,
                    "mask_hot\n"
                    "GET  /status\n"
                    "POST /in | /out | /rebuild | /build-live\n",
                )
            elif self.path.rstrip("/") == "/status":
                self._json(200, state.status())
            else:
                self._text(404, "not found\n")

        def do_POST(self):
            path = self.path.rstrip("/")
            with state.lock:
                if path == "/in":
                    state.force_in()
                    self._json(200, {"ok": True, "action": "in", "stats": state.stats})
                elif path == "/out":
                    state.force_out()
                    self._json(200, {"ok": True, "action": "out"})
                elif path == "/rebuild":
                    state.force_rebuild()
                    self._json(200, {"ok": True, "action": "rebuild"})
                elif path == "/build-live":
                    code = state.build_live()
                    self._json(200 if code == 0 else 500, {"ok": code == 0, "exit": code})
                else:
                    self._text(404, "not found\n")

        def log_message(self, fmt, *args):
            log("http " + (fmt % args))

    return Handler


def poll_loop(state, stop):
    while not stop.is_set():
        try:
            state.poll_once()
        except Exception as e:
            state.stats["errors"] += 1
            log("poll error: %s" % e)
        stop.wait(state.interval)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "work",
        nargs="?",
        default=None,
        help="work folder (default: $MECHANISMUS or <repo-parent>/mechanismus)",
    )
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--interval", type=float, default=1.0, help="poll seconds")
    p.add_argument("--bootstrap", action="store_true", help="mask_sync out if work/parts missing")
    p.add_argument("--rebuild", action="store_true", help="with --bootstrap, also rebuild parts")
    args = p.parse_args(argv)

    work = os.path.abspath(args.work or default_mask_dir())
    if work == os.path.abspath(REPO) or work.startswith(os.path.abspath(REPO) + os.sep):
        log("refusing to use a work folder inside the live repo")
        sys.exit(1)
    parts = os.path.join(work, "parts")
    if args.bootstrap or not os.path.isdir(parts):
        sync_args = ["out", work]
        if args.rebuild:
            sync_args.append("--rebuild")
        if run_sync(sync_args) != 0:
            sys.exit(1)

    state = HotState(work, args.interval, quiet_in=True)
    stop = threading.Event()
    t = threading.Thread(target=poll_loop, args=(state, stop), daemon=True)
    t.start()

    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    log("watching %s ↔ %s" % (work, OVERLAY_DIR))
    log("http://%s:%d/status" % (args.host, args.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("stop")
    finally:
        stop.set()
        httpd.server_close()


if __name__ == "__main__":
    main()
