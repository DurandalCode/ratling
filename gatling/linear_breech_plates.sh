#!/bin/sh
# Gatling linear-breech station parts -> Bambu Studio project (PLA, sliced).
#
# The one station part the bench plates do not carry: the moving carriage
# (rear + nose rail bushings, thumb, bridge). The hand bench drives its own
# carriage_handle; this carriage is the one the cam rail of the real mechanism
# pushes. 0.4 nozzle: the rail bushings are running fits, no drill-out wanted;
# stands on its bushing end as exported (best of the six faces), brim + supports.
#
# Not printed: Al chamber tube, Al rails 8x1, steel barrel, AirTAC, hardware.
#
# Regenerate STLs first (FreeCAD):
#   export LANG=C.UTF-8 LC_ALL=C.UTF-8
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/fat_coax_qev.py').read())"
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech.py').read())"
# Then:
#   sh gatling/linear_breech_plates.sh
set -e
cd "$(dirname "$0")/.."
python3 tools/print_plate.py gatling_breech_carriage \
  exports/gatling_linear_breech/carriage.stl \
  --filament "Bambu PLA Basic @BBL P2S" --infill 60% --walls 5 --pattern gyroid \
  --support --brim 5 \
  | python3 -c 'import sys,json;r=json.load(sys.stdin);print("carriage:",r["plates"],"plate(s),",", ".join("%d min %.0f g"%(s["minutes"],s["grams"]) for s in r["sliced"]))'
