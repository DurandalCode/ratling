#!/bin/sh
# Ratling pistol (hammer variant): plates for the body and the hand mechanism only, to try the grip, the hammer and the
# trigger before printing the rest (valve, lock housing, block, axle plug, strap, nose). One project per print profile.
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/body_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json, shlex, subprocess, sys
NAMES = {"frame_cage", "frame_side_plate", "grip_left", "grip_right", "trigger_guard", "trigger", "hammer", "slider",
         "sector", "pawl", "detent_housing", "detent_bolt"}
spec = json.load(open("exports/pistol_build/parts.json"))
for group, opts in spec["groups"].items():
    for nozzle in ("0.4", "0.8"):           # parts on the 0.8 nozzle get their own projects, <group>_08
        stls = [p["stl"] for p in spec["parts"]
                if p["group"] == group and p.get("nozzle", "0.4") == nozzle and p["name"] in NAMES]
        if not stls:
            continue
        cmd = [sys.executable, "tools/print_plate.py", "pistol_body_" + group + ("_08" if nozzle == "0.8" else "")] + stls
        cmd += shlex.split(opts) + (["--nozzle", nozzle] if nozzle != "0.4" else [])
        print(">", " ".join(cmd), flush=True)
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode:
            print(out.stdout[-1500:], out.stderr[-1500:])
            sys.exit(out.returncode)
        r = json.loads(out.stdout)
        print("  %s: %d plate(s), %s" % (r["project"], r["plates"],
              ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])), flush=True)
PY
