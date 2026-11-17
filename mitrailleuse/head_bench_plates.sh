#!/bin/sh
# Mitrailleuse head bench B -> Bambu Studio projects. Manifest: plates/head_bench.json.
#   sh mitrailleuse/head_bench_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py head_bench
