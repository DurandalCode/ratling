#!/bin/sh
# Ratling pistol: the block's rear disc (V notches) and the wedge detent bolt on one plate, strong profile.
# Run pistol/build/export_parts.py in FreeCAD first (it writes the STLs).
#   sh pistol/build/detent_parts_plates.sh
set -e
cd "$(dirname "$0")/../.."
d=exports/pistol_build/stl
python3 tools/print_plate.py pistol_detent_parts $d/block_rear_disc.stl $d/detent_bolt.stl \
    --infill 60% --walls 5 --pattern gyroid | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
