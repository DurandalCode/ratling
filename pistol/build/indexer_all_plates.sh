#!/bin/sh
# Ratling pistol: the indexer stand and the parts that changed (the sector, the pawl plunger, two plugs) on ONE PLA plate.
# Supports and a 3 mm brim for all of it (only the sector needs the supports; the jig and the plunger do not mind them).
# Run pistol/build/export_parts.py and pistol/build/indexer_test.py in FreeCAD first.
#   sh pistol/build/indexer_all_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_build/stl
python3 tools/print_plate.py pistol_indexer_all_pla exports/pistol_indexer_test/stl/indexer_jig.stl $d/sector.stl $d/pawl.stl $d/pawl_plug.stl:2 \
    --filament "Bambu PLA Basic @BBL P2S" --infill 40% --walls 4 --pattern gyroid --support --brim 3 | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
