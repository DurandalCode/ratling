#!/bin/sh
# Ratling pistol (hammer variant): the grip halves and the trigger guard - the FINAL PETG round
# for the hand - as ONE Bambu project on the 0.8 nozzle, all three parts on one plate: they fit
# together and none is worth a plate of its own. Grip halves: cut face on the bed; the nut pockets
# (left) and the head seats (right) open on the top of the print; supports under the four tray
# tongues, brim 5 - the halves stand 18 mm tall on a small bed otherwise. The guard prints flat,
# its own tab under the floor on supports. The supply channel runs straight along the seam
# (2026-11-13): the halves close on it, no printed groove to file. Run
# pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/grip_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json, shlex, subprocess, sys
NAMES = ["grip_left", "grip_right", "trigger_guard"]
spec = json.load(open("exports/pistol_build/parts.json"))
by_name = {p["name"]: p for p in spec["parts"]}
missing = [n for n in NAMES if n not in by_name]
if missing:
    sys.exit("parts.json is missing: %s (run pistol/build/export_parts.py in FreeCAD first)" % ", ".join(missing))
cmd = [sys.executable, "tools/print_plate.py", "pistol_grip_08"]
cmd += [by_name[n]["stl"] for n in NAMES]
cmd += shlex.split("--nozzle 0.8 --infill 40% --walls 4 --support --brim 5")
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
