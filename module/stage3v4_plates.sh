#!/bin/sh
# Stage 3 v4.4 -> Bambu Studio projects. Manifest: plates/stage3v4.json.
# Run module/stage3v4_coaxial_chamber.py in FreeCAD first.
#   sh module/stage3v4_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py stage3v4
