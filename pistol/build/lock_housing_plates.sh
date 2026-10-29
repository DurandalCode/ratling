#!/bin/sh
# Ratling pistol: the chosen lock housing (no lock, the sleeve's nose printed in), airtight profile, alone on its plate.
# Run pistol/build/bench_fixed_nose.py in FreeCAD first (it writes the STL).
#   sh pistol/build/lock_housing_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 tools/print_plate.py pistol_lock_housing exports/pistol_bench_fixed_nose/stl/lock_housing_nose.stl \
    --airtight --infill 60% --pattern gyroid | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
