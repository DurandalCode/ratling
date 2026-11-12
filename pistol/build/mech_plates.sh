#!/bin/sh
# Ratling pistol (hammer variant), PROTOTYPE round: the parts that bolt onto the printed body
# shell - the hammer, the trigger, the detent housing - as ONE Bambu project in PLA on the 0.4
# nozzle, all three on one plate, light (3 walls, 15 %): fit and function only, the final parts
# print in PETG per their groups (make_plates.sh). Supports on - the hammer's spur and the
# detent housing's overhangs need them, the trigger (flat on its blade side, 454 mm2) grows none -
# and a brim 5: the hammer and the trigger stand tall on a small bed. The supports' marks stay
# in the housing's wedge channel (it lies flat): file it before the wedge goes in.
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/mech_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json, shlex, subprocess, sys
NAMES = ["hammer", "trigger", "detent_housing"]
spec = json.load(open("exports/pistol_build/parts.json"))
by_name = {p["name"]: p for p in spec["parts"]}
missing = [n for n in NAMES if n not in by_name]
if missing:
    sys.exit("parts.json is missing: %s (run pistol/build/export_parts.py in FreeCAD first)" % ", ".join(missing))
cmd = [sys.executable, "tools/print_plate.py", "pistol_mech_pla"]
cmd += [by_name[n]["stl"] for n in NAMES]
cmd += shlex.split("--filament 'Bambu PLA Basic @BBL P2S' --infill 15% --walls 3 --support --brim 5")
print(">", " ".join(cmd), flush=True)
out = subprocess.run(cmd, capture_output=True, text=True)
if out.returncode:
    print(out.stdout[-1500:], out.stderr[-1500:])
    sys.exit(out.returncode)
r = json.loads(out.stdout)
print(out.stderr.strip())          # the orient_check verdicts, one line a part
print("  %s: %d plate(s), %s" % (r["project"], r["plates"],
      ", ".join("plate %d: %d min %.0f g" % (s["plate"], s["minutes"], s["grams"]) for s in r["sliced"])),
      flush=True)
PY
