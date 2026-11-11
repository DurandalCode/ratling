#!/bin/sh
# Ratling pistol (hammer variant): the body shell the v12 rounds changed - the tray, the lid, the left
# wall and band, the right cover, both grip halves - as ONE Bambu project in PLA on the 0.8 nozzle
# (the fit-check round; the final body is PETG later). Bambu's arrange splits the parts over the
# project's plates by itself. The shell is all supports-group except frame_side_wall, whose standard
# profile differs only by the infill share; 40 % just makes the wall stiffer. Brim 5: the tray, the
# lid and the band stand tall on a small bed area (orient_check WARNs). The guard, the strap, the
# nose and the axle plug are not this round; the mechanism parts come separately.
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/body_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json, shlex, subprocess, sys
NAMES = {"frame_lower", "frame_upper", "frame_side_wall", "frame_side_band", "frame_right",
         "grip_left", "grip_right"}
spec = json.load(open("exports/pistol_build/parts.json"))
stls = [p["stl"] for p in spec["parts"] if p["name"] in NAMES]
missing = NAMES - {p["name"] for p in spec["parts"]}
if missing:
    sys.exit("parts.json is missing: %s (run pistol/build/export_parts.py in FreeCAD first)"
             % ", ".join(sorted(missing)))
cmd = [sys.executable, "tools/print_plate.py", "pistol_body_08_pla"] + stls
cmd += shlex.split("--nozzle 0.8 --filament 'Bambu PLA Basic @BBL P2S' --infill 40% --walls 4 "
                   "--support --brim 5")
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
