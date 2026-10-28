#!/bin/sh
# Ratling pistol: PLA plate for the detent test (pistol/build/detent_test.py writes the STLs).
#   sh pistol/build/detent_test_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_detent_test/stl
python3 tools/print_plate.py pistol_detent_test $d/sector_a.stl $d/sector_b.stl $d/jig.stl $d/detent_bolt.stl \
    --filament "Bambu PLA Basic @BBL P2S" --infill 15% --walls 3 | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
