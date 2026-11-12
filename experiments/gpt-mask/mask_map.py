# -*- coding: utf-8 -*-
"""
Name maps for the GPT-mask pipe. Pure Python — no FreeCAD.

Shell parts are the only ones pushed back into the live assembly (overlays).
Drive parts stay rename-only in the mask folder.
"""

# Live variable → D parts/*.brep stem
LIVE_TO_D_STEM = {
    "frame_lower": "tray",
    "frame_upper": "lid",
    "side_wall": "left_wall",
    "side_band": "left_band",
    "side_plate_r": "right_cover",
    "grip_left": "grip_l",
    "grip_right": "grip_r",
    "guard": "bail",
    "detent_box": "index_box",
}

# D FreeCAD object name (build.py) → live variable
D_NAME_TO_LIVE = {
    "Shell_tray": "frame_lower",
    "Shell_cover": "frame_upper",
    "Cover_left_wall": "side_wall",
    "Cover_left_band": "side_band",
    "Cover_right": "side_plate_r",
    "Grip_left": "grip_left",
    "Grip_right": "grip_right",
    "Bail": "guard",
    "Index_box": "detent_box",
}

# Which live vars accept overlays from the mask
SHELL_OVERLAY_VARS = tuple(LIVE_TO_D_STEM.keys())

# Files to copy when staging a GPT work folder from D_full_mech
D_TEMPLATE_FILES = ("build.py", "PROMPT.txt", "README.md", "export_edits.py")
