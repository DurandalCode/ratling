#!/bin/sh
# Ratling pistol bench (pistol/build/bench_frame.py): only the parts the bench needs, on Bambu plates (PETG, sliced).
# The pistol's parts are the pistol's own STLs; they go into the pistol after the bench.
#   (FreeCAD) exec(open(REPO + '/pistol/build/export_parts.py').read())   # the pistol's STLs
#   (FreeCAD) exec(open(REPO + '/pistol/build/bench_frame.py').read())    # the frame
#   sh pistol/build/bench_plates.sh
set -e
cd "$(dirname "$0")/../.."
P=exports/pistol_build/stl
V=exports/stage3_qev_v13
report() {
  python3 -c "import sys,json;r=json.load(sys.stdin);print('$1:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
}
python3 tools/print_plate.py pistol_bench_airtight $V/body.stl $V/cap.stl $P/lock_housing.stl $P/lock_sleeve.stl \
  --airtight --infill 100% | report airtight
python3 tools/print_plate.py pistol_bench_strong exports/pistol_bench/bench_frame.stl $P/lock_pusher.stl $P/top_strap.stl \
  $P/nose_sleeve.stl $P/axle_plug.stl $P/detent_bolt.stl --infill 60% --walls 5 --pattern gyroid | report strong
python3 tools/print_plate.py pistol_bench_standard $P/block_rear_disc.stl $P/block_front_disc.stl \
  --infill 30% --walls 4 | report standard
