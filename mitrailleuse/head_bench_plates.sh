#!/bin/sh
# Mitrailleuse head, bench B (mitrailleuse/head_bench.py): one port on a hand slider, on Bambu plates (sliced).
# The head block holds supply and pilot air: PETG, airtight (6 walls, 60 % gyroid, as Stage 3 v1.1 held 2 bar).
# The rest stays on the bench, indoors: PLA, stiffer (~3.3 vs 1.9 GPa) and truer than PETG, 4 walls, 25 % gyroid.
# Two followers (charge and vent) from one STL.
#   (FreeCAD) exec(open(REPO + '/mitrailleuse/head_bench.py').read())
#   sh mitrailleuse/head_bench_plates.sh
set -e
cd "$(dirname "$0")/.."
B=exports/head_bench
report() {
  python3 -c "import sys,json;r=json.load(sys.stdin);print('$1:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
}
python3 tools/print_plate.py head_bench_airtight $B/head_block.stl \
  --airtight --infill 60% --pattern gyroid | report airtight
python3 tools/print_plate.py head_bench_frame $B/base.stl $B/guide_plate.stl $B/slider.stl $B/follower.stl:2 \
  --filament "Bambu PLA Basic @BBL P2S 0.4 nozzle" --infill 25% --walls 4 --pattern gyroid | report frame
