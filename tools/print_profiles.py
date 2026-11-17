"""Canonical print groups for tools/make_plates.py and tools/print_plate.py.

Each group is a print profile: the flags passed to print_plate.py, plus the
default filament family (petg for pressurised parts, pla for mock-ups and
indoor benches). Part manifests pick a group; same-group parts share a .3mf
and Bambu packs them onto plates that fill as the set grows.

Do not invent new groups in a one-off shell script: add them here so every
module and the /plates skill speak the same names.
"""

# Filament shortcuts -> Bambu system preset names (print_plate.py rewrites the
# 0.4 suffix when --nozzle is not 0.4).
FILAMENTS = {
    "petg": "Bambu PETG Basic @BBL P2S 0.4 nozzle",
    "pla": "Bambu PLA Basic @BBL P2S",
}

# group -> default flags and filament family. Part/job overrides may add
# --support, --brim, a different infill, etc.; they never rename the group.
PROFILES = {
    # Holds chamber or pilot air. Proven at 2 bar on 0.4 / 6 walls / 60 % gyroid.
    "airtight": {
        "opts": ["--airtight", "--infill", "60%", "--pattern", "gyroid"],
        "filament": "petg",
        "what": "plugs, caps, valve bodies, seat rings, anything that holds air",
    },
    # Loaded or moving parts.
    "strong": {
        "opts": ["--infill", "60%", "--walls", "5", "--pattern", "gyroid"],
        "filament": "petg",
        "what": "yokes, clamps, levers, gears, loaded frames",
    },
    "strong_supports": {
        "opts": ["--infill", "60%", "--walls", "5", "--pattern", "gyroid", "--support"],
        "filament": "petg",
        "what": "strong parts that need supports",
    },
    # Tools, jigs, light fixtures.
    "standard": {
        "opts": ["--infill", "30%", "--walls", "4"],
        "filament": "petg",
        "what": "O-ring cones, drilling templates, gauges, light fixtures",
    },
    "supports": {
        "opts": ["--infill", "40%", "--walls", "4", "--support"],
        "filament": "petg",
        "what": "body shells and other parts that need supports",
    },
    # Impact / hammer: thicker walls, on supports.
    "impact": {
        "opts": ["--infill", "40%", "--walls", "6", "--support"],
        "filament": "petg",
        "what": "hammers and other impact parts",
    },
    # Paper/flat mock-ups, pack plates, PLA benches.
    "mockup": {
        "opts": ["--infill", "30%", "--walls", "4"],
        "filament": "pla",
        "what": "paper mock-ups, pack plates, PLA fit checks",
    },
}


def profile_opts(group, filament=None, nozzle="0.4", extra=None):
    """CLI flag list for print_plate.py for this group (+ optional overrides)."""
    if group not in PROFILES:
        raise KeyError("unknown print group %r (known: %s)" % (group, ", ".join(sorted(PROFILES))))
    prof = PROFILES[group]
    fam = filament or prof["filament"]
    if fam not in FILAMENTS:
        raise KeyError("unknown filament family %r (known: %s)" % (fam, ", ".join(sorted(FILAMENTS))))
    opts = list(prof["opts"])
    # PETG is print_plate.py's default; only pass --filament when it differs or
    # when the nozzle forces a rewrite of the preset name.
    if fam != "petg" or nozzle != "0.4":
        opts = ["--filament", FILAMENTS[fam]] + opts
    if nozzle != "0.4":
        opts = ["--nozzle", nozzle] + opts
    if extra:
        opts = opts + list(extra)
    return opts
