# -*- coding: utf-8 -*-
"""
Name maps for the external Mechanismus work tree. Pure Python — no FreeCAD.

Shell parts are the only ones pushed back into the live assembly (overlays).
"""

from __future__ import print_function

import os

_MAP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_MAP_DIR, os.pardir, os.pardir))


def default_mask_dir():
    """External work folder: $MECHANISMUS, else <repo-parent>/mechanismus."""
    env = os.environ.get("MECHANISMUS", "").strip()
    if env:
        return os.path.abspath(os.path.expanduser(env))
    return os.path.abspath(os.path.join(REPO_ROOT, os.pardir, "mechanismus"))


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

# Files copied into the external Mechanismus folder (no ratling / mask wording)
MECHANISMUS_TEMPLATE_FILES = ("build.py", "PROMPT.txt", "README.md", "export_edits.py")
