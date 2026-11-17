#!/bin/sh
# Pack frame and carry mount -> Bambu Studio projects. Manifest: plates/pack_frame.json.
#   sh mitrailleuse/pack_frame_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py pack_frame
