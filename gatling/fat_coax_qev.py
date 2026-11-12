# -*- coding: utf-8 -*-
"""
Gatling fat-coaxial QEV sketch: v4.4 stack in a short fat chamber tube.

Intermediate decision (2026-11-12, docs/gatling.md): for a chamber-per-barrel
Gatling at ~2 bar prefer a coaxial dump (proven on v4.4) with a thicker
shorter chamber than the mitrailleuse's 38 x 1.5, not an external side bottle.

This file does not fork the geometry code. It sets OVERRIDE and execs
module/stage3v4_coaxial_chamber.py so seat ring, diaphragm, spigot-in-barrel
seal, tie rods and muzzle clamp stay the v4.4 design that already dumps well.
Only the bought chamber tube and the pack pitch for a 6-around Gatling change:

    CH_OD x CH_WALL = 50 x 1.5 aluminium (nominal ID 47 until a tube is measured)
    CHAMBER_V       = 100 cm3 → tube length falls to ~80 mm of annulus
    TIE_R           = 29 (clears Ø50)
    PACK_PITCH      = 68 (six modules; ears clear)

Not yet: revolver stub + bushing into a separate long barrel (variant 2 joint).
This sketch keeps a full barrel through the chamber like v4.4, to lock the
valve envelope first.

Run inside FreeCAD / freecadcmd:
    REPO = '/path/to/ratling'
    exec(open(REPO + '/gatling/fat_coax_qev.py').read())

Exports: exports/gatling_fat_coax_qev/
Library: set GATLING_FAT_COAX_LIBRARY = True before exec (forwards STAGE3V4_LIBRARY).
"""
import os

try:
    REPO
except NameError:
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    GATLING_FAT_COAX_LIBRARY
except NameError:
    GATLING_FAT_COAX_LIBRARY = False

# Nominal bought tube until a bore is measured (same habit as v4.4's CH_ID).
CH_OD, CH_WALL = 50.0, 1.5
CH_ID = CH_OD - 2 * CH_WALL          # 47.0

# Chamber O-ring: scale the v4.4 29 x 3 @ ID 34.6 up for ID 47 at ~18 % squeeze.
# Root ≈ ID/2 - CS*(1-0.18) = 21.04 → ID 42 gives ~0.2 % stretch (0..6 % check).
CH_ORING = (42.0, 3.0)

TIE_R = 29.0                         # > CH_OD/2 + clearance for M3 holes
PACK_PITCH = 68.0                    # N=6 ring: footprint ~Ø66 with ears at R 33

OVERRIDE = {
    "NAME": "gatling_fat_coax_qev",
    "CH_OD": CH_OD,
    "CH_WALL": CH_WALL,
    "CH_ID": CH_ID,
    "CH_ORING": CH_ORING,
    "TIE_R": TIE_R,
    "PACK_PITCH": PACK_PITCH,
    # Same dump as v4.4; keep seat Ø16 / bleed Ø1 / 100 cm3.
    "CHAMBER_V": 100.0,
    "SEAT_D": 16.0,
    "MUZZLE_CLAMP": True,
}

STAGE3V4_LIBRARY = GATLING_FAT_COAX_LIBRARY
exec(open(os.path.join(REPO, "module", "stage3v4_coaxial_chamber.py"), encoding="utf-8").read())
