#!/bin/sh
# Mitrailleuse rear frame -> Bambu Studio project. Manifest: plates/rear_frame.json.
#   sh mitrailleuse/rear_frame_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py rear_frame
