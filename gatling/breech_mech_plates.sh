#!/bin/sh
# Gatling linear breech: EVERYTHING EXCEPT THE QEV in one Bambu Studio project (PLA, 0.8).
#
# One .3mf for a full print run of the mechanical set: bench feet + stops, both
# carriages (the bench pusher with its T-handle and the station pusher without),
# the nose clamp, barrel clamps + collar, AirTAC cradle, front yoke, and the two
# QEV assembly tools (jig, O-ring cone). The QEV's own seal parts (rear plug,
# seat ring, front cover with the gutter) stay in gatling_breech_bench_airtight.
# 0.8 nozzle, the bench profile; rail bores and M3 holes will need a drill-out.
#
# Regenerate STLs first (FreeCAD):
#   export LANG=C.UTF-8 LC_ALL=C.UTF-8
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/fat_coax_qev.py').read())"
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech.py').read())"
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech_bench.py').read())"
# Then:
#   sh gatling/breech_mech_plates.sh
set -e
cd "$(dirname "$0")/.."
Q=exports/gatling_fat_coax_qev
B=exports/gatling_linear_breech
S=exports/gatling_linear_breech_bench
PLA='Bambu PLA Basic @BBL P2S'
python3 tools/print_plate.py gatling_breech_mech_08 \
  "$S/foot_front.stl" "$S/foot_rear.stl" \
  "$S/carriage_handle.stl" "$B/carriage.stl" "$B/nose_clamp.stl" \
  "$S/rail_stop.stl:4" \
  "$S/barrel_clamp.stl" "$S/barrel_collar.stl" "$S/airtac_cradle.stl" \
  "$Q/front_yoke.stl" "$Q/jig_guide.stl" "$Q/oring_cone.stl" \
  --nozzle 0.8 --filament "$PLA" --infill 30% --walls 4 --pattern gyroid \
  --support --brim 5 \
  | python3 -c 'import sys,json;r=json.load(sys.stdin);print("mech_08:",r["plates"],"plate(s),",", ".join("%d min %.0f g"%(s["minutes"],s["grams"]) for s in r["sliced"]))'
