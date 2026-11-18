#!/bin/sh
# Gatling linear-breech hand bench. Manifest: plates/gatling_breech_bench.json.
#
# Regenerate STLs first (FreeCAD), then:
#   sh gatling/linear_breech_bench_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py gatling_breech_bench
