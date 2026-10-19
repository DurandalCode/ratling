#!/bin/sh
# Mitrailleuse pack frame -> Bambu Studio projects (PETG, sliced): the rear and front plate, one project per pack.
# Run mitrailleuse/pack_frame.py in FreeCAD first (it writes exports/pack_frame/*.stl).
# The plates are mostly 1.4 mm webs between the tube holes, so they print as walls: 5 walls, 60 % gyroid, as the
# module's yokes.
#   sh mitrailleuse/pack_frame_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/pack_frame
for n in a16 a19; do
  python3 tools/print_plate.py pack_frame_$n $S/${n}_rear_plate.stl $S/${n}_front_plate.stl \
    --infill 60% --walls 5 --pattern gyroid |
    python3 -c "import sys,json;r=json.load(sys.stdin);print('$n:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
done
