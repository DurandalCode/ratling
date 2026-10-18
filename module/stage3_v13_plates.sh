#!/bin/sh
# Stage 3 v1.3 -> Bambu Studio projects (PETG, sliced): the pressure parts airtight, the yoke and clips strong.
#   freecadcmd -c "REPO='$PWD'; exec(open('module/stage3_v13.py').read())"   # writes the STLs
#   sh module/stage3_v13_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/stage3_qev_v13
report() {
  python3 -c "import sys,json;r=json.load(sys.stdin);print('$1:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
}
python3 tools/print_plate.py stage3v13_airtight $S/body.stl $S/cap.stl $S/chamber_plug.stl $S/barrel_breech.stl \
  --airtight --infill 100% | report airtight
python3 tools/print_plate.py stage3v13_strong $S/plug_yoke.stl $S/tube_clip.stl $S/jig_base.stl $S/jig_ring.stl $S/jig_puck.stl \
  --infill 60% --walls 5 --pattern gyroid | report strong
