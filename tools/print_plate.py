#!/usr/bin/env python3
"""Lay printed parts out on Bambu Studio plates and slice them.

    tools/print_plate.py NAME STL[:COUNT] [STL[:COUNT] ...] [options]

The STLs are taken as they are: the generators already export every printed
part in its print orientation, lowest point at z = 0. Bambu Studio's own
command line clones each to its count, packs the plates and slices, so the
project opens as the GUI would have arranged it, with print time and filament
already estimated. Output: exports/print/NAME.3mf.

The printer, process and filament are Bambu system presets, by name, with the
`inherits` chain folded in (the command line does not do that itself and
falls back to a default plate). On top go the overrides given here.

    tools/print_plate.py tube_plug_v1 exports/tube_plug_v1/tube_plug_v1.stl:2 --infill 100%

Plain Python, no FreeCAD. Adapted from star-dome's tools/print_plates.py.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "exports", "print")
BAMBU = os.environ.get("BAMBU_STUDIO", "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
PROFILES = os.environ.get(
    "BAMBU_PROFILES", os.path.expanduser("~/Library/Application Support/BambuStudio/system/BBL"))

# --airtight: for parts that hold air. The stock profile (flow 0.98, walls at
# 200-300 mm/s, full fan) left the Stage 3 v1 cap breathing through its layers
# at 2 bar. Slower, hotter, a little over-extruded, less fan: fused layers.
AIRTIGHT_PROCESS = {"wall_loops": "6", "infill_wall_overlap": "30%"}
AIRTIGHT_FILAMENT = {"filament_flow_ratio": "1.05", "nozzle_temperature": "+10",
                     "nozzle_temperature_initial_layer": "+10", "filament_max_volumetric_speed": "6",
                     "fan_max_speed": "50", "fan_min_speed": "30"}

PRINTER = "Bambu Lab P2S 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL P2S"
FILAMENT = "Bambu PETG Basic @BBL P2S 0.4 nozzle"   # pressurized parts: PETG


def preset(kind, name):
    """A system preset with its `inherits` chain folded in."""
    path = os.path.join(PROFILES, kind, name + ".json")
    if not os.path.exists(path):
        raise SystemExit("no Bambu Studio %s preset %r in %s" % (kind, name, os.path.dirname(path)))
    with open(path) as f:
        values = json.load(f)
    parent = values.pop("inherits", None)
    if parent:
        folded = preset(kind, parent)
        folded.update(values)
        values = folded
    return values


def apply(values, changes):
    """Set preset values keeping their shape (Bambu keeps many as per-variant
    lists); "+N" adds to the current number."""
    out = dict(values)
    for k, v in changes.items():
        cur = out.get(k)
        def one(c):
            return str(int(float(c)) + int(v[1:])) if v.startswith("+") else v
        out[k] = [one(c) for c in cur] if isinstance(cur, list) else one(cur if cur is not None else "0")
    return out


def mark_changes(project, process_keys, filament_keys):
    """List the changed keys in the project's different_settings_to_system
    ([process, filament..., printer], ";"-joined). The command line leaves it
    empty, and then the GUI reopens the project on the plain system presets
    (15 % grid infill, 2 walls) and re-slices with those."""
    name = "Metadata/project_settings.config"
    with zipfile.ZipFile(project) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    for idx, (info, data) in enumerate(items):
        if info.filename == name:
            cfg = json.loads(data)
            diff = list(cfg.get("different_settings_to_system") or ["", "", ""])
            diff[0] = ";".join(sorted(set(filter(None, diff[0].split(";"))) | set(process_keys)))
            for i in range(1, len(diff) - 1):
                diff[i] = ";".join(sorted(set(filter(None, diff[i].split(";"))) | set(filament_keys)))
            cfg["different_settings_to_system"] = diff
            items[idx] = (info, json.dumps(cfg, indent=4).encode())
    tmp = project + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in items:
            z.writestr(info, data)
    os.replace(tmp, project)


def slice_info(project):
    """(plates, [(plate, minutes, grams)]) from the sliced project."""
    with zipfile.ZipFile(project) as z:
        plates = z.read("Metadata/model_settings.config").decode().count("<plate>")
        info = z.read("Metadata/slice_info.config").decode() if "Metadata/slice_info.config" in z.namelist() else ""
    out = []
    for block in re.findall(r"<plate>(.*?)</plate>", info, re.S):
        get = lambda key: (re.search(r'key="%s" value="([^"]*)"' % key, block) or [None, "0"])[1]
        out.append((int(get("index")), float(get("prediction")) / 60, float(get("weight"))))
    return plates, out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name")
    ap.add_argument("parts", nargs="+", help="STL[:COUNT]")
    ap.add_argument("--printer", default=PRINTER)
    ap.add_argument("--process", default=PROCESS)
    ap.add_argument("--filament", default=FILAMENT)
    ap.add_argument("--infill", default="35%", help="sparse infill density, e.g. 100%%")
    ap.add_argument("--walls", default="4")
    ap.add_argument("--plate", default="Textured PEI Plate", help="build plate type (PETG: not Cool Plate)")
    ap.add_argument("--support", action="store_true", help="enable supports (parts are drawn not to need them)")
    ap.add_argument("--airtight", action="store_true",
                    help="slow, hot, over-extruded, 6+ walls: for parts that hold air")
    ap.add_argument("--no-slice", action="store_true")
    args = ap.parse_args(argv)

    stls, counts = [], []
    for p in args.parts:
        path, _, count = p.partition(":")
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise SystemExit("no such STL: %s (run its generator first)" % path)
        stls.append(path)
        counts.append(int(count or 1))

    overrides = {"sparse_infill_density": args.infill, "wall_loops": args.walls,
                 "enable_support": "1" if args.support else "0", "curr_bed_type": args.plate}
    if float(args.infill.rstrip("%")) >= 100:
        overrides["sparse_infill_pattern"] = "zig-zag"      # grid is refused at 100 %
    filament = preset("filament", args.filament)
    if args.airtight:
        overrides.update(AIRTIGHT_PROCESS)
        overrides["wall_loops"] = str(max(int(args.walls), int(AIRTIGHT_PROCESS["wall_loops"])))
        filament = apply(filament, AIRTIGHT_FILAMENT)
    work = tempfile.mkdtemp(prefix="print_plate_")
    settings = {}
    for kind, values in (("machine", preset("machine", args.printer)),
                         ("process", apply(preset("process", args.process), overrides)),
                         ("filament", filament)):
        settings[kind] = os.path.join(work, kind + ".json")
        with open(settings[kind], "w") as f:
            json.dump(values, f, indent=1)

    os.makedirs(OUT_DIR, exist_ok=True)
    project = os.path.join(OUT_DIR, args.name + ".3mf")
    if os.path.exists(project):
        os.remove(project)
    cmd = [BAMBU, "--orient", "0", "--arrange", "1",
           "--clone-objects", ",".join(str(c) for c in counts),
           "--load-settings", "%s;%s" % (settings["machine"], settings["process"]),
           "--load-filaments", settings["filament"]]
    if not args.no_slice:
        cmd += ["--slice", "0"]
    cmd += ["--export-3mf", project] + stls
    # It writes result.json into the working directory; run it somewhere disposable.
    run = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
    result = {}
    if os.path.exists(os.path.join(work, "result.json")):
        with open(os.path.join(work, "result.json")) as f:
            result = json.load(f)
    if run.returncode != 0 or result.get("return_code", 0) != 0 or not os.path.exists(project):
        tail = "\n".join(run.stdout.splitlines()[-15:] + run.stderr.splitlines()[-15:])
        raise SystemExit("Bambu Studio failed: %s\n%s" % (result.get("error_string", run.returncode), tail))

    mark_changes(project, [k for k in overrides if k != "curr_bed_type"], AIRTIGHT_FILAMENT.keys() if args.airtight else ())
    plates, sliced = slice_info(project)
    report = {"project": os.path.relpath(project, REPO), "printer": args.printer,
              "process": args.process, "filament": args.filament, "overrides": overrides,
              "airtight": AIRTIGHT_FILAMENT if args.airtight else None,
              "parts": [{"stl": os.path.relpath(s, REPO), "count": c} for s, c in zip(stls, counts)],
              "plates": plates,
              "sliced": [{"plate": i, "minutes": round(m), "grams": round(g, 1)} for i, m, g in sliced]}
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
