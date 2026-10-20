#!/bin/sh
# Mitrailleuse pack frame and its CG supports -> Bambu Studio projects (PETG, sliced), one project per pack plus the handle and pad.
# Run mitrailleuse/pack_frame.py and carry_mount.py in FreeCAD first (they write exports/pack_frame/ and
# exports/carry_mount/): two CG plates a pack, the handle and the tripod pad on their sides.
# The plates are mostly 1.4 mm webs between the tube holes, so they print as walls: 5 walls, 60 % gyroid, as the
# module's yokes.
#   sh mitrailleuse/pack_frame_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/pack_frame
C=exports/carry_mount
for n in a16 a19; do
  python3 tools/print_plate.py pack_frame_$n $S/${n}_rear_plate.stl $S/${n}_front_plate.stl $C/${n}_cg_plate.stl:2 \
    --infill 60% --walls 5 --pattern gyroid |
    python3 -c "import sys,json;r=json.load(sys.stdin);print('$n:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
done
python3 tools/print_plate.py carry_mount $C/handle.stl $C/tripod_pad.stl --infill 60% --walls 5 --pattern gyroid |
  python3 -c "import sys,json;r=json.load(sys.stdin);print('carry:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
