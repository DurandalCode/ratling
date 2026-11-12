# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v1.5: v1.3 side-by-side QEV with the flow path grown to match the Ø16 seat.

v1.3 kept GALLERY_R=18 / LIFT=4 / DIA_D=46 from v1.1 while SEAT_D went 13→16. Bench 2026-11-12:
dumps, but at ~2 bar exhaust feels weak vs coaxial v4.4 — curtain landed at 1.00× seat and
gallery at 1.11×. open_ratio (78 %) was not the limiter.

v1.5 keeps v1.3's mechanics (no tube screws, yoke, O-rings 19×2.5 / face 22×2.5, two breech
M3) and restores approach margins for the same seat:

    GALLERY_R 18→19, LIFT 4→5, SEAT_LAND 2→1.5 (as v4.4)
    DIA_D 46→48 and BEAD_R 21→22 so the clamp strip stays 4 mm with free Ø40
    ROD_R 26.5→28 so the M4 rods stay outside the bigger disc
    CAP_T 16→17 (deeper pocket must clear the G1/8 tap roof)
    BLEED_R 13→14, JIG_BLANK 48→50 (disc + ≥1 mm blank margin)

Target from the report (paper, before freecadcmd): curtain ~1.25× seat, gallery ~1.32×,
open_ratio ~81 %, dead volume still ~11.3 cm³ (seat bore unchanged — shorten the breech
path later if needed). BODY_R stays 31: pistol socket envelope unchanged; body/cap still
need a reprint, and VALVE=v13 must not be swapped blindly (rod circle and disc differ).

Not the pistol default. Print and bench against v1.3 / v4.4 at 2 bar before any assembly
hookup.

Run inside FreeCAD (writes exports/stage3_qev_v15/):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_v15.py').read())
"""
import os

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
OVERRIDE = {
    "NAME": "stage3_qev_v15",
    "TUBE_SCREWS": False,
    "PLUG_YOKE": True,
    "SEAT_D": 16.0,
    "SEAT_LAND": 1.5,
    "GALLERY_R": 19.0,
    "LIFT": 5.0,
    "CAP_T": 17.0,
    "DIA_D": 48.0,
    "BEAD_R": 22.0,
    "ROD_R": 28.0,
    "BLEED_R": 14.0,
    "JIG_BLANK": 50.0,
    "ORING_ID": 19.0,
    "ORING_CS": 2.5,
    "FACE_ORING_ID": 22.0,
    "FACE_ORING_CS": 2.5,
    "GROOVE_WALL_MIN": 1.5,
    "BREECH_BOLT_ANGLES": (90.0, 180.0),
}
exec(open(REPO + "/module/stage3_qev.py").read())
