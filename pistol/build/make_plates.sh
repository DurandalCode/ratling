#!/bin/sh
# Ratling pistol: lay every print group from exports/pistol_build/parts.json.
# Run pistol/build/export_parts.py in FreeCAD first.
#   sh pistol/build/make_plates.sh
set -e
cd "$(dirname "$0")/../.."
exec python3 tools/make_plates.py pistol
