#!/bin/sh
# Stage 3 v1.1 -> Bambu Studio projects. Manifest: plates/stage3_qev.json.
#   freecadcmd -c "REPO='$PWD'; exec(open('module/stage3_qev.py').read())"
#   sh module/stage3_qev_plates.sh
set -e
cd "$(dirname "$0")/.."
exec python3 tools/make_plates.py stage3_qev
