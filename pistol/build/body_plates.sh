#!/bin/sh
# Ratling pistol (hammer variant): the body shell the v12 rounds changed - the tray, the lid and the
# left band, the right cover - as ONE Bambu project in PLA on the 0.8 nozzle, each part alone on
# its own plate (--plate-each; plate order = the list below), so a failed print costs one part.
# The slab's left wall is no longer a separate part (2026-11-12, the Mechanismus round): it belongs
# to the tray and the lid, four printed shell parts in total. The grip halves are NOT in this round
# (the plan of 2026-11-05): they print with the final PETG body, after #35's bolted halves are
# checked against the real tray. The supports profile covers every part. Brim 5: the lid
# and the band still stand tall on a small bed area (orient_check WARNs); the tray
# now lies on its -Y face (~40 mm). Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/body_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json, shlex, subprocess, sys
NAMES = ["frame_lower", "frame_upper", "frame_side_band", "frame_right"]
spec = json.load(open("exports/pistol_build/parts.json"))
by_name = {p["name"]: p for p in spec["parts"]}
missing = [n for n in NAMES if n not in by_name]
if missing:
    sys.exit("parts.json is missing: %s (run pistol/build/export_parts.py in FreeCAD first)" % ", ".join(missing))
cmd = [sys.executable, "tools/print_plate.py", "pistol_body_08_pla"]
cmd += [by_name[n]["stl"] for n in NAMES]
cmd += shlex.split("--nozzle 0.8 --filament 'Bambu PLA Basic @BBL P2S' --infill 40% --walls 4 "
                   "--support --brim 5 --plate-each")
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
