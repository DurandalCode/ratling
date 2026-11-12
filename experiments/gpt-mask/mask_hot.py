#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot sync: external Mechanismus folder ↔ product mask_overlays.

  python3 experiments/gpt-mask/mask_sync.py out -p pistol --rebuild
  python3 experiments/gpt-mask/mask_hot.py -p pistol

  curl http://127.0.0.1:8765/status
  curl -X POST http://127.0.0.1:8765/in|out|rebuild|build-live
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
from exchange import edit_files, find_work_shell, is_brep, record, to_brep  # noqa: E402
from product_lib import label_to_live, list_products, live_to_stem, load_product  # noqa: E402

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
    if not fa or not fb or fa[1] != fb[1]:
        return False
    with open(a, "rb") as fa_, open(b, "rb") as fb_:
        return fa_.read() == fb_.read()


class HotState(object):
    def __init__(self, product, interval):
        self.product = product
        self.product_id = product["id"]
        self.work = product["work_dir"]
        self.cache_dir = os.path.join(HERE, "cache", self.product_id)
        self.overlay_dir = product["overlay_dir"]
        self.live_stem = live_to_stem(product)
        self.label_live = label_to_live(product)
        self.lives = tuple(self.live_stem.keys())
        self.interval = interval
        self.lock = threading.Lock()
        self.ignore_until = {}
        self.last_work = {}
        self.last_overlay = {}
        self.stats = {"in": 0, "out_overlay": 0, "errors": 0}
        self.shell_stems = {p["stem"] for p in product["shell"]}
        self.last_edit_work = {}
        self.last_edit_repo = {}
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
        out = {}
        for live in self.live_stem:
            p = find_work_shell(self.work, self.product, live)
            if p:
                out[live] = p
        return out

    def overlay_paths(self):
        out = {}
        if not os.path.isdir(self.overlay_dir):
            return out
        for live in self.lives:
            p = os.path.join(self.overlay_dir, live + ".brep")
            if os.path.isfile(p):
                out[live] = p
        return out

    def _seed(self):
        for live, path in self.work_shell_paths().items():
            self.last_work[live] = fingerprint(path)
        for live, path in self.overlay_paths().items():
            self.last_overlay[live] = fingerprint(path)
        self.last_edit_work = {k: fingerprint(p) for k, p in self.work_edits().items()}
        self.last_edit_repo = {k: fingerprint(p) for k, p in self.repo_edits().items()}

    def work_edits(self):
        found = edit_files(os.path.join(self.work, "edits"))
        return {k: v for k, v in found.items() if k in self.shell_stems}

    def repo_edits(self):
        return {k: v for k, v in edit_files(self.product["edits_dir"]).items() if k in self.shell_stems}

    def sync_edits(self):
        work = self.work_edits()
        if any(fingerprint(p) != self.last_edit_work.get(k) for k, p in work.items()):
            if run_sync(["in", "--product", self.product_id, self.work, "--edits-only"]) == 0:
                self.stats["in"] += 1
            else:
                self.stats["errors"] += 1
            self.last_edit_work = {k: fingerprint(p) for k, p in self.work_edits().items()}
            self.last_edit_repo = {k: fingerprint(p) for k, p in self.repo_edits().items()}
        for stem, path in self.repo_edits().items():
            fp = fingerprint(path)
            if fp == self.last_edit_repo.get(stem):
                continue
            dst = os.path.join(self.work, "edits", stem + ".py")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not same_file(path, dst):
                shutil.copy2(path, dst)
                self.stats["out_overlay"] += 1
                log("out edits/%s.py ← %s" % (stem, path))
            record(self.cache_dir, "edit:" + stem, dst)
            self.last_edit_repo[stem] = fp
            self.last_edit_work[stem] = fingerprint(dst)

    def copy_to_overlay(self, live, src):
        os.makedirs(self.overlay_dir, exist_ok=True)
        dst = os.path.join(self.overlay_dir, live + ".brep")
        if is_brep(src) and same_file(src, dst):
            self.last_work[live] = fingerprint(src)
            self.last_overlay[live] = fingerprint(dst)
            record(self.cache_dir, live, src)
            return False
        to_brep([(src, dst)])
        record(self.cache_dir, live, src)
        self._ignore(dst)
        self._ignore(src)
        self.last_work[live] = fingerprint(src)
        self.last_overlay[live] = fingerprint(dst)
        self.stats["in"] += 1
        log("in  %s ← %s" % (live + ".brep", src))
        return True

    def copy_to_work(self, live, src):
        stem = self.live_stem[live]
        parts = os.path.join(self.work, "parts")
        os.makedirs(parts, exist_ok=True)
        dst = os.path.join(parts, stem + ".brep")
        if same_file(src, dst):
            self.last_overlay[live] = fingerprint(src)
            self.last_work[live] = fingerprint(dst)
            record(self.cache_dir, live, dst)
            return False
        shutil.copy2(src, dst)
        exports = os.path.join(self.work, "exports")
        for lab, lv in self.label_live.items():
            if lv == live:
                os.makedirs(exports, exist_ok=True)
                exp = os.path.join(exports, lab + ".brep")
                shutil.copy2(src, exp)
                self._ignore(exp)
        self._ignore(dst)
        self._ignore(src)
        self.last_overlay[live] = fingerprint(src)
        self.last_work[live] = fingerprint(dst)
        record(self.cache_dir, live, dst)
        self.stats["out_overlay"] += 1
        log("out %s → parts/%s.brep" % (live + ".brep", stem))
        return True

    def poll_once(self):
        with self.lock:
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
            self.sync_edits()
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
        for live, path in self.work_shell_paths().items():
            try:
                self.copy_to_overlay(live, path)
            except Exception as e:
                self.stats["errors"] += 1
                log("in error %s: %s" % (live, e))

    def force_out(self):
        log("force out")
        run_sync(["out", "--product", self.product_id, self.work])
        self._seed()

    def force_rebuild(self):
        log("force rebuild + out")
        run_sync(["out", "--product", self.product_id, self.work, "--rebuild"])
        self._seed()

    def build_live(self):
        log("build live %s" % self.product["build_script"])
        env = os.environ.copy()
        env.setdefault("LANG", "C.UTF-8")
        env.setdefault("LC_ALL", "C.UTF-8")
        env["MASK_PRODUCT"] = self.product_id
        pre = dict(self.product.get("build_pre") or {})
        assigns = "; ".join("%s=%r" % (k, v) for k, v in pre.items())
        prefix = ("REPO=%r; MASK_PRODUCT=%r; " % (REPO, self.product_id)) + (assigns + "; " if assigns else "")
        cmd = [
            "freecadcmd",
            "-c",
            prefix + "exec(open(%r).read())" % self.product["build_script"],
        ]
        return subprocess.call(cmd, cwd=REPO, env=env)

    def status(self):
        return {
            "product": self.product_id,
            "work": self.work,
            "overlays": self.overlay_dir,
            "interval": self.interval,
            "stats": self.stats,
            "shell_in_work": sorted(self.work_shell_paths().keys()),
            "shell_overlays": sorted(self.overlay_paths().keys()),
            "edits_in_work": sorted(self.work_edits().keys()),
            "edits_in_repo": sorted(self.repo_edits().keys()),
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
                self._text(200, "mask_hot\nGET /status\nPOST /in|/out|/rebuild|/build-live\n")
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
    p.add_argument("--product", "-p", default=os.environ.get("MASK_PRODUCT", "pistol"),
                   choices=list_products() or ["pistol", "mitrailleuse", "gatling"])
    p.add_argument("work", nargs="?", default=None, help="override work folder")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--bootstrap", action="store_true")
    p.add_argument("--rebuild", action="store_true")
    args = p.parse_args(argv)

    product = load_product(args.product)
    if args.work:
        product = dict(product)
        product["work_dir"] = os.path.abspath(args.work)
    work = product["work_dir"]
    if work == REPO or work.startswith(REPO + os.sep):
        log("refusing to use a work folder inside the live repo")
        sys.exit(1)

    parts = os.path.join(work, "parts")
    if args.bootstrap or not os.path.isdir(parts):
        sync_args = ["out", "--product", args.product, work]
        if args.rebuild:
            sync_args.append("--rebuild")
        if run_sync(sync_args) != 0:
            sys.exit(1)

    state = HotState(product, args.interval)
    stop = threading.Event()
    threading.Thread(target=poll_loop, args=(state, stop), daemon=True).start()
    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    log("product %s" % args.product)
    log("watching %s ↔ %s" % (work, product["overlay_dir"]))
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
