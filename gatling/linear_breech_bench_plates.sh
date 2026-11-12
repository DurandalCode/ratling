#!/bin/sh
# Gatling linear-breech hand bench -> Bambu Studio projects (PLA, sliced).
#
# Two projects:
#   gatling_breech_bench_airtight — chamber/pilot seal parts, 0.4 nozzle, airtight PLA
#   gatling_breech_bench_08       — the rest, 0.8 nozzle, PLA (drill rail/barrel holes after)
#
# Not printed: diaphragm (rubber), Al chamber tube, Al rails Ø8×1, steel barrel 25×0.6,
# AirTAC M3R110 + fittings, M3/M4 hardware.
#
# Regenerate STLs first (FreeCAD):
#   export LANG=C.UTF-8 LC_ALL=C.UTF-8
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/fat_coax_qev.py').read())"
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech.py').read())"
#   freecadcmd -c "REPO='$PWD'; exec(open('gatling/linear_breech_bench.py').read())"
# Then:
#   sh gatling/linear_breech_bench_plates.sh
set -e
cd "$(dirname "$0")/.."
Q=exports/gatling_fat_coax_qev
B=exports/gatling_linear_breech
S=exports/gatling_linear_breech_bench
PLA='Bambu PLA Basic @BBL P2S'
report() {
  python3 -c "import sys,json;r=json.load(sys.stdin);print('$1:',r['plates'],'plate(s),',', '.join('%d min %.0f g'%(s['minutes'],s['grams']) for s in r['sliced']))"
}

# Chamber end + seat + front cover with pellet gutter (holds air at 2 bar).
# Supports: seat cone and cover tip/gutter overhang past the 0.4 bed check.
python3 tools/print_plate.py gatling_breech_bench_airtight \
  "$Q/rear_plug.stl" "$Q/seat_ring.stl" "$B/front_cover_feed.stl" \
  --filament "$PLA" --airtight --infill 60% --pattern gyroid --support --brim 5 \
  | report airtight

# Feet, carriage+T-handle, rail stops, barrel clamps, AirTAC cradle, yoke + tools.
# 0.8: bushing and barrel holes will need a drill-out (same as pistol body_08).
python3 tools/print_plate.py gatling_breech_bench_08 \
  "$S/foot_front.stl" "$S/foot_rear.stl" "$S/carriage_handle.stl" "$S/rail_stop.stl:4" \
  "$S/barrel_clamp.stl" "$S/barrel_collar.stl" "$S/airtac_cradle.stl" \
  "$Q/front_yoke.stl" "$Q/jig_guide.stl" "$Q/oring_cone.stl" \
  --nozzle 0.8 --filament "$PLA" --infill 30% --walls 4 --pattern gyroid \
  --support --brim 5 \
  | report rest_08
