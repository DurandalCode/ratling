#!/bin/sh
# Stage 3 v1.3 -> Bambu Studio projects. Manifest: plates/stage3_v13.json.
#   freecadcmd -c "REPO='$PWD'; exec(open('module/stage3_v13.py').read())"
#   sh module/stage3_v13_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py stage3_v13
