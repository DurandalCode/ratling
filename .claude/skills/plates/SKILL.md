---
name: plates
description: Lay a ratling module's printed parts on Bambu P2S plates and slice them into .3mf projects. Use when the user asks to put a module "on the bed / на стол", make print plates, slice, or get print time/filament for a part set.
argument-hint: <module, e.g. stage3v4 | pistol | --pool stage3v4 stage3_qev>
---

# Print plates for a ratling module

Goal: sliced Bambu Studio projects in `exports/print/`. Classification lives in
`plates/*.json` (or pistol `parts.json`); the driver is `tools/make_plates.py`.
Do **not** invent a one-off layout in chat or a new shell script that lists STLs
by hand — edit the manifest, then run the driver. Reply to the user in Russian.
Details: `docs/print.md`.

## 1. Find the generator and its manifest

```sh
python3 tools/make_plates.py --list
```

| module | generator | manifest / parts list |
|---|---|---|
| Stage 3 v4.4 | `module/stage3v4_coaxial_chamber.py` | `plates/stage3v4.json` |
| Stage 3 v1.1 / v1.3 | `module/stage3_qev.py`, `stage3_v13.py` | `plates/stage3_qev.json`, `stage3_v13.json` |
| Pack plates / frame | `mitrailleuse/pack_plate.py`, `pack_frame.py` | `plates/pack_layouts.json`, `pack_frame.json` |
| Gatling bench | `gatling/linear_breech_bench.py` (+ deps) | `plates/gatling_breech_bench.json` |
| Pistol | `pistol/build/export_parts.py` | `exports/pistol_build/parts.json` (`make_plates.py pistol`) |

Thin wrappers still work: `sh module/stage3v4_plates.sh`, `sh pistol/build/make_plates.sh`, …

## 2. Regenerate the STLs in FreeCAD

Exports are git-ignored and may be stale, so always regenerate. Through
`mcp__freecad__execute_python` (Mac) or `freecadcmd` (cloud VM):

```python
import io, contextlib
REPO = '/Users/danilaorehov/ratling'
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(open(REPO + '/module/<name>.py').read(), {"REPO": REPO, "__name__": "__main__"})
print(buf.getvalue()[-6000:])
```

If any check says `[FAIL]`, stop: do not slice a failing design.
Delete STLs the generator no longer writes.

## 3. Sort new parts into print groups (manifest only)

Groups and flags: `tools/print_profiles.py` / table in `docs/print.md`.
Add or edit a row in `plates/<id>.json` (or `PARTS` in `export_parts.py`):

| group | what goes in |
|---|---|
| `airtight` | holds chamber or pilot air |
| `strong` / `strong_supports` | loaded or moving |
| `standard` / `supports` / `impact` | tools, shells, hammer |
| `mockup` | PLA mock-ups and pack plates |

Optional per part: `count`, `nozzle` (`0.8` for big plain parts → own `…_08` project),
`filament` (`pla` / `petg`), `support`, `brim`, `infill`, `project` (legacy .3mf name).
Never put airtight or sub-0.5 mm fits on 0.8. Several copies: `"count": N`.

Preview without Bambu:

```sh
python3 tools/make_plates.py --dry-run <id>
python3 tools/make_plates.py --check <id>
```

`--pool` merges the same group across manifests into `pool_<group>.3mf` so one
bed fills as more modules are added.

## 3a. Orientation

`tools/print_plate.py` runs `tools/orient_check.py` on every STL (`[OK ]` /
`[WARN]` / `[FAIL]`). A `FAIL` without `--support` stops the slice. Fix the
`down` face in the generator (or move the part to a supports group), regenerate.
After slicing, peek at `Metadata/plate_1.png` inside the `.3mf`.

## 4. Slice

```sh
python3 tools/make_plates.py <id>
# or, one bed per print type across modules:
python3 tools/make_plates.py --pool stage3v4 stage3_qev stage3_v13
```

Needs Bambu Studio on macOS. Takes a few minutes; use a long timeout.

## 5. Open in Bambu Studio

`open -a /Applications/BambuStudio.app exports/print/<project>.3mf`
(app name is `BambuStudio.app`, no space). **One project only** per `open`:
several files in one call pile onto the first plate. Open the first group, tell
the user the next after it prints.

## 6. Commit and report

Commit the manifest (and driver changes if any) on the working branch; exports
are ignored. Tell the user, in Russian: project file, parts, profile, time and
grams; what is not printed (rubber, bought); any print note (overhang, bed face).
