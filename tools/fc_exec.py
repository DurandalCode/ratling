#!/usr/bin/env python3
"""Run Python inside the owner's running FreeCAD GUI, the way the FreeCAD MCP does.

The MCP bridge (~/.freecad-mcp/freecad_mcp_server.py) talks to a socket served inside each GUI
instance; live instances are listed in ~/.cache/freecad-mcp/instances/*.json. This script speaks
the same protocol (length-prefixed JSON, execute_python_async + poll_job), for sessions where the
mcp__freecad__* tools are not connected.

    python3 tools/fc_exec.py --list
    python3 tools/fc_exec.py [--pid N] -c "print(App.listDocuments())"
    python3 tools/fc_exec.py [--pid N] -f script.py
"""
import argparse
import glob
import json
import os
import socket
import struct
import sys
import time


def instances():
    out = []
    for p in glob.glob(os.path.expanduser("~/.cache/freecad-mcp/instances/*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(0.5)
            s.connect(d["socket_path"])
            out.append(d)
        except Exception:
            pass
        finally:
            s.close()
    return sorted(out, key=lambda d: d.get("started_at", 0))


def call(sock_path, tool, args, timeout=30.0):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout + 5)
    s.connect(sock_path)
    try:
        b = json.dumps({"tool": tool, "args": args}).encode()
        s.sendall(struct.pack(">I", len(b)) + b)
        n = struct.unpack(">I", _recv(s, 4))[0]
        return json.loads(_recv(s, n).decode())
    finally:
        s.close()


def _recv(s, n):
    buf = b""
    while len(buf) < n:
        c = s.recv(n - len(buf))
        if not c:
            raise ConnectionError("socket closed")
        buf += c
    return buf


def run(sock_path, code, timeout=600.0):
    r = call(sock_path, "execute_python_async", {"code": code})
    if "job_id" not in r:
        return r
    t0 = time.time()
    while time.time() - t0 < timeout:
        p = call(sock_path, "poll_job", {"job_id": r["job_id"]})
        if p.get("status") in ("done", "error"):
            return p
        time.sleep(0.5)
    return {"status": "timeout", "job_id": r["job_id"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pid", type=int)
    ap.add_argument("-c")
    ap.add_argument("-f")
    a = ap.parse_args()
    live = instances()
    if a.list or not (a.c or a.f):
        for d in live:
            print(d["pid"], d["socket_path"], d.get("label"))
        sys.exit(0)
    pick = [d for d in live if a.pid is None or d["pid"] == a.pid]
    if not pick:
        sys.exit("no live FreeCAD GUI instance")
    code = a.c if a.c else open(a.f).read()
    r = run(pick[-1]["socket_path"], code)
    print(r.get("result") if r.get("status") == "done" else json.dumps(r, ensure_ascii=False))
