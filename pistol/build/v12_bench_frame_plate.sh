#!/bin/sh
# The first v12 bench round in one project: the frame and the side plate, PLA, 0.8 nozzle.
# Run pistol/build/export_parts.py in FreeCAD first (it writes exports/pistol_build/stl/).
#   sh pistol/build/v12_bench_frame_plate.sh
set -e
cd "$(dirname "$0")/../.."
exec python3 tools/print_plate.py pistol_v12_bench_frame_08 \
    exports/pistol_build/stl/frame_cage.stl exports/pistol_build/stl/frame_side_plate.stl \
    exports/pistol_build/stl/frame_right.stl \
    --infill 40% --walls 4 --support --nozzle 0.8 --brim 5 --filament "Bambu PLA Basic @BBL P2S"
