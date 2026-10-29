#!/bin/sh
# Ratling pistol: the chosen lock housing (no lock, the sleeve's nose printed in), standard profile, alone on its plate: only the shot's impulse passes through it, no standing pressure, so 4 walls and 30 % do.
# Run pistol/build/export_parts.py in FreeCAD first (it writes the STL).
#   sh pistol/build/lock_housing_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 tools/print_plate.py pistol_lock_housing exports/pistol_build/stl/lock_housing.stl \
    --infill 30% --walls 4 | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
