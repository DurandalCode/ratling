#!/bin/sh
# Mitrailleuse rear frame -> a Bambu Studio project (PETG, sliced): head plate, trigger arm, bevel box (no grip yet).
# Run mitrailleuse/rear_frame.py in FreeCAD first (it writes exports/rear_frame/, every part in print orientation).
# The head's own parts come from exports/rotor_bench/ (four quarter blocks and guide plates, the stop lever, trip cam).
#   sh mitrailleuse/rear_frame_plates.sh
set -e
cd "$(dirname "$0")/.."
R=exports/rear_frame
python3 tools/print_plate.py rear_frame $R/head_plate.stl $R/trigger_arm.stl $R/bevel_box.stl \
  --infill 60% --walls 5 --pattern gyroid |
  python3 -c "import sys,json;r=json.load(sys.stdin);print('rear frame:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
