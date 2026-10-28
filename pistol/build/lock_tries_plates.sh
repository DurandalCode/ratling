#!/bin/sh
# Ratling pistol bench: plates for the two lock tries. Run pistol/build/bench_fixed_nose.py and bench_two_lugs.py in
# FreeCAD first (they write the STLs).
#   sh pistol/build/lock_tries_plates.sh
set -e
cd "$(dirname "$0")/../.."
summary='import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
python3 tools/print_plate.py pistol_lock_tries_airtight \
    exports/pistol_bench_fixed_nose/stl/lock_housing_nose.stl exports/pistol_bench_two_lugs/stl/lock_housing.stl \
    --airtight --infill 60% --pattern gyroid | python3 -c "$summary"
python3 tools/print_plate.py pistol_lock_tries_strong exports/pistol_bench_two_lugs/stl/lock_pusher.stl \
    --infill 60% --walls 5 --pattern gyroid | python3 -c "$summary"
