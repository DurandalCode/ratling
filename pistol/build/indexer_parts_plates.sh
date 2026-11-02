#!/bin/sh
# Ratling pistol: the pistol's own parts the indexer stand needs, each on its own plate (together their brims and supports
# ran into each other): the sector (boss with the pawl's channel) together with the pawl plunger (the tooth) and two plugs, and the slider (it lies
# on its bracket face, on supports). Strong profile, PETG, and the same in PLA for the fits.
# The rear disc (ramped notches) and the detent bolt are on pistol_detent_parts (pistol/build/detent_parts_plates.sh).
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/indexer_parts_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_build/stl
summary='import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
strong='--infill 60% --walls 5 --pattern gyroid'
for m in "" "_pla"; do
    f=""
    [ -n "$m" ] && f="--filament"
    if [ -n "$m" ]; then
        python3 tools/print_plate.py pistol_indexer_sector$m $d/sector.stl $d/pawl.stl $d/pawl_plug.stl:2 --filament "Bambu PLA Basic @BBL P2S" $strong --support --brim 5 | python3 -c "$summary"
        python3 tools/print_plate.py pistol_indexer_slider$m $d/slider.stl --filament "Bambu PLA Basic @BBL P2S" $strong --support --brim 5 | python3 -c "$summary"
    else
        # one combined plate (the PETG copies to print): all four brims and their supports fit without
        # touching when the packer spaces them apart -- checked in pistol_indexer.3mf, plate_1.png
        # brim 5, not 3: the export report warns the sector, the pawl and the plugs sit too small on the bed
        python3 tools/print_plate.py pistol_indexer $d/sector.stl $d/pawl.stl $d/pawl_plug.stl:2 $d/slider.stl $strong --support --brim 5 | python3 -c "$summary"
    fi
done
