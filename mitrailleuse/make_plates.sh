#!/bin/sh
# Pack-layout negative plates -> Bambu Studio projects (PLA, one project per layout, sliced).
# Run mitrailleuse/pack_plate.py in FreeCAD first (it writes exports/pack_layouts/stl/plate_*.stl).
#   sh mitrailleuse/make_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/pack_layouts/stl
for n in g_hex_19 h_hex_37 i_square_5x5_round; do
  set -- $S/plate_$n.stl
  [ -f "$1" ] || set -- $S/plate_${n}_left.stl $S/plate_${n}_right.stl $S/plate_${n}_straps.stl
  python3 tools/print_plate.py plate_$n "$@" --filament "Bambu PLA Basic @BBL P2S" --plate "Textured PEI Plate" |
    python3 -c "import sys,json;r=json.load(sys.stdin);print('$n:',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
done
