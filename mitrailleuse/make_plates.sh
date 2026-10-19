#!/bin/sh
# Pack-layout negative plates -> Bambu Studio projects (PLA, one project per layout, sliced).
# Run mitrailleuse/pack_plate.py in FreeCAD first (it writes exports/pack_layouts/stl/plate_*.stl).
# The plates are thin and nearly all solid, so time goes with layers: 0.24 mm layers, 2 walls round the holes.
# g_hex_19 is drawn at LAYERS = 6 (1.2 mm): 46 min instead of 67 at 1.6 mm / 0.20 / 4 walls.
#   sh mitrailleuse/make_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/pack_layouts/stl
for n in g_hex_19 h_hex_37 i_square_5x5_round j_rings_4_12; do
  set -- $S/plate_$n.stl
  [ -f "$1" ] || set -- $S/plate_${n}_left.stl $S/plate_${n}_right.stl $S/plate_${n}_straps.stl
  python3 tools/print_plate.py plate_$n "$@" --filament "Bambu PLA Basic @BBL P2S" --plate "Textured PEI Plate" \
    --process "0.24mm Standard @BBL P2S" --walls 2 |
    python3 -c "import sys,json;r=json.load(sys.stdin);print('$n:',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
done
