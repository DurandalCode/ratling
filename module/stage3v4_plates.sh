#!/bin/sh
# Stage 3 v4.4 -> Bambu Studio projects (PETG, sliced): the airtight parts, and the loaded ones with the tools.
# Run module/stage3v4_coaxial_chamber.py in FreeCAD first (it writes exports/stage3v4_coaxial_chamber/*.stl).
#   sh module/stage3v4_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/stage3v4_coaxial_chamber
report() {
  python3 -c "import sys,json;r=json.load(sys.stdin);print('$1:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
}
python3 tools/print_plate.py stage3v44_airtight $S/rear_plug.stl $S/seat_ring.stl $S/front_plug.stl \
  --airtight --infill 100% | report airtight
python3 tools/print_plate.py stage3v44_strong $S/rear_yoke.stl $S/front_yoke.stl $S/muzzle_clamp_half.stl:2 \
  $S/oring_cone.stl $S/jig_guide.stl --infill 60% --walls 5 --pattern gyroid | report strong
