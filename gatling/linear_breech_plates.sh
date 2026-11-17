#!/bin/sh
# Gatling linear-breech station parts. Manifest: plates/gatling_breech_carriage.json.
# Regenerate STLs first, then:
#   sh gatling/linear_breech_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py gatling_breech_carriage
