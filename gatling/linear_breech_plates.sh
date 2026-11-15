#!/bin/sh
# Gatling linear-breech station parts -> Bambu Studio project (PLA, sliced).
#
# The two station parts the bench plates do not carry in station form:
#   carriage  - the rear pusher (bridge on the QEV tie studs, plain rail bores
#               in its plate; the hand bench drives its own carriage_handle)
#   nose_clamp- the front rail guide, its own part now: a clamp on the Al
#               chamber tube (split at Y=0, 2 x M3), bores in its skirt
# 0.4 nozzle: the rail bores are running fits, no drill-out wanted.
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
  exports/gatling_linear_breech/nose_clamp.stl \
  --filament "Bambu PLA Basic @BBL P2S" --infill 60% --walls 5 --pattern gyroid \
  --support --brim 5 \
  | python3 -c 'import sys,json;r=json.load(sys.stdin);print("station parts:",r["plates"],"plate(s),",", ".join("%d min %.0f g"%(s["minutes"],s["grams"]) for s in r["sliced"]))'
