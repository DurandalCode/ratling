#!/bin/sh
# Ratling pistol: the pistol's own parts the indexer stand needs, each on its own plate (together their brims and supports
# ran into each other): the sector (boss with the pawl's channel), the pawl plunger and its plug, and the slider (it lies on its bracket face, on supports).
# Strong profile, PETG, and the same two in PLA for the fits.
# The rear disc and the detent bolt are on pistol_detent_parts (pistol/build/detent_parts_plates.sh).
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/indexer_parts_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_build/stl
summary='import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
pla='--filament "Bambu PLA Basic @BBL P2S"'
strong='--infill 60% --walls 5 --pattern gyroid'
python3 tools/print_plate.py pistol_indexer_sector $d/sector.stl $strong --support --brim 5 | python3 -c "$summary"
python3 tools/print_plate.py pistol_indexer_sector_pla $d/sector.stl --filament "Bambu PLA Basic @BBL P2S" $strong --support --brim 5 | python3 -c "$summary"
python3 tools/print_plate.py pistol_indexer_pawl $d/pawl.stl $d/pawl_plug.stl $strong --brim 3 | python3 -c "$summary"
python3 tools/print_plate.py pistol_indexer_pawl_pla $d/pawl.stl $d/pawl_plug.stl --filament "Bambu PLA Basic @BBL P2S" $strong --brim 3 | python3 -c "$summary"
python3 tools/print_plate.py pistol_indexer_slider $d/slider.stl $strong --support --brim 5 | python3 -c "$summary"
python3 tools/print_plate.py pistol_indexer_slider_pla $d/slider.stl --filament "Bambu PLA Basic @BBL P2S" $strong --support --brim 5 | python3 -c "$summary"
