#!/bin/sh
# Ratling pistol (hammer variant): lay the printed parts on Bambu plates, one project per print profile.
# Run pistol/build/export_parts.py in FreeCAD first (it writes exports/pistol_build/parts.json and the STLs).
#   sh pistol/build/make_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 - <<'EOF'
import json, shlex, subprocess, sys
spec = json.load(open("exports/pistol_build/parts.json"))
for group, opts in spec["groups"].items():
    stls = [p["stl"] for p in spec["parts"] if p["group"] == group]
    if not stls:
        continue
    cmd = [sys.executable, "tools/print_plate.py", "pistol_build_" + group] + stls + shlex.split(opts)
    print(">", " ".join(cmd), flush=True)
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode:
        print(out.stdout[-1500:], out.stderr[-1500:])
        sys.exit(out.returncode)
    r = json.loads(out.stdout)
    print("  %s: %d plate(s), %s" % (r["project"], r["plates"],
          ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])), flush=True)
EOF
