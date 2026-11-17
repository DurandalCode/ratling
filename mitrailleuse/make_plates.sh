#!/bin/sh
# Pack-layout negative plates -> Bambu Studio projects. Manifest: plates/pack_layouts.json.
# Run mitrailleuse/pack_plate.py in FreeCAD first.
#   sh mitrailleuse/make_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py pack_layouts
