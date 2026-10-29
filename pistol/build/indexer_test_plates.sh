#!/bin/sh
# Ratling pistol: PLA plate for the indexer stand (pistol/build/indexer_test.py writes the STL).
#   sh pistol/build/indexer_test_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 tools/print_plate.py pistol_indexer_test exports/pistol_indexer_test/stl/indexer_jig.stl \
    --filament "Bambu PLA Basic @BBL P2S" --infill 15% --walls 3 | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
