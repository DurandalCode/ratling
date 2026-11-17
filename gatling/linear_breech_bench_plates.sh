#!/bin/sh
# Gatling linear-breech hand bench. Manifest: plates/gatling_breech_bench.json.
#
# Regenerate STLs first (FreeCAD), then:
#   sh gatling/linear_breech_bench_plates.sh
set -e
cd "$(dirname "$0")/.."
S=exports/gatling_linear_breech_bench
if [ -f "$S/feeder_frame.stl" ]; then
  echo "Refusing to slice: this plate layout predates the 2026-11-16 feeder/stop import; update plates/gatling_breech_bench.json first." >&2
  exit 1
fi
exec python3 tools/make_plates.py gatling_breech_bench
