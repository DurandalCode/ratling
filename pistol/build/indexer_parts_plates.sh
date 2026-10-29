#!/bin/sh
# Ratling pistol: the pistol's own parts the indexer stand needs (sector, pawl, slider), strong profile.
# The rear disc and the detent bolt are on pistol_detent_parts (pistol/build/detent_parts_plates.sh).
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/indexer_parts_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_build/stl
python3 tools/print_plate.py pistol_indexer_parts $d/sector.stl $d/pawl.stl $d/slider.stl \
    --infill 60% --walls 5 --pattern gyroid | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
# The same three in PLA (stiffer, truer to size): to try the tight fits (the pawl's channel, the guide rod hole) cheaply.
python3 tools/print_plate.py pistol_indexer_parts_pla $d/sector.stl $d/pawl.stl $d/slider.stl \
    --filament "Bambu PLA Basic @BBL P2S" --infill 60% --walls 5 --pattern gyroid | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
