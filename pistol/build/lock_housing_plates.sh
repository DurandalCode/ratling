#!/bin/sh
# Ratling pistol: the chosen lock housing (no lock, the sleeve's nose printed in) with the sector's
# support ring printed in (12th Mechanismus round, was the separate Sector_spacer): the ring is the
# sector's seat, so the part moved from the standard profile to strong + supports (5 walls, 60 %
# gyroid; supports grow under the raised rear rim). Alone on its plate: the housing body itself only
# passes the shot's impulse, no standing pressure.
# Run pistol/build/export_parts.py in FreeCAD first (it writes the STL).
#   sh pistol/build/lock_housing_plates.sh
set -e
cd "$(dirname "$0")/../.."
python3 tools/print_plate.py pistol_lock_housing exports/pistol_build/stl/lock_housing.stl \
    --infill 60% --walls 5 --pattern gyroid --support | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  %s: %d plate(s), %s" % (r["project"], r["plates"], ", ".join("%d min %.0f g" % (s["minutes"], s["grams"]) for s in r["sliced"])))'
