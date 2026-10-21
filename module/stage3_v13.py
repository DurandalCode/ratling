# -*- coding: utf-8 -*-
"""
Ratling Stage 3 v1.3: the v1.1/v1.2 valve (module/stage3_qev.py) with a Ø16 seat instead of Ø13 (+51 % flow area).

What lets the seat grow: the self-tapping screws through the tubes are gone (their pilots ate the spigot wall), and
the spigot O-rings are 19 x 2.5 (was 11/16" x 1/8") so the groove is shallower. The chamber plug's push is
carried instead by a yoke on the plug's end and two long M4 rods (the cap rods at 45 / 315 deg, run on past the
body along the chamber tube). The barrel tube needs no retention of its own (open at the muzzle, no axial load):
in the pistol the block holds it, on the bench the clip does. The breech face ring is 22 x 2.5.

The body and cap are the pistol's too (pistol/ with VALVE = "v13" builds the same two shapes, checked to the
volume): print them once, test them here, then move them into the pistol (pistol/build/README.md).

Buy: O-rings 19 x 2.5 (x3: body spigot, plug, breech spigot), 22 x 2.5 (x1, breech face); 2 x M4 threaded rod to
the length in the report, 2 x M4 nut + washer; no ST2.9 screws.

Run inside FreeCAD (writes exports/stage3_qev_v13/):
    REPO = '/Users/<you>/ratling'
    exec(open(REPO + '/module/stage3_v13.py').read())
"""
import os

try:
    REPO
except NameError:
    REPO = os.path.expanduser("~/ratling")
OVERRIDE = {"NAME": "stage3_qev_v13", "TUBE_SCREWS": False, "PLUG_YOKE": True, "SEAT_D": 16.0,
            "ORING_ID": 19.0, "ORING_CS": 2.5, "FACE_ORING_ID": 22.0, "FACE_ORING_CS": 2.5, "GROOVE_WALL_MIN": 1.5}
exec(open(REPO + "/module/stage3_qev.py").read())
