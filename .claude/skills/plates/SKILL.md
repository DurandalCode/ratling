---
name: plates
description: Lay a ratling module's printed parts on Bambu P2S plates and slice them into .3mf projects. Use when the user asks to put a module "on the bed / на стол", make print plates, slice, or get print time/filament for a part set.
argument-hint: <module, e.g. stage3v4 | pistol | pack plates>
---

# Print plates for a ratling module

Goal: sliced Bambu Studio projects in `exports/print/`, one per print profile, plus a small committed shell
script that rebuilds them. Reply to the user in Russian.

## 1. Find the generator and its exports

- Modules: `module/<name>.py` writes `exports/<NAME>/*.stl` (NAME is the script's `NAME`).
- Pistol: `pistol/build/export_parts.py` writes `exports/pistol_build/parts.json` + STLs.
- Pack plates: `mitrailleuse/pack_plate.py` writes `exports/pack_layouts/stl/`.

If a plates script already exists, use it (step 4): `module/<name>_plates.sh`, `module/stage3v4_plates.sh`,
`pistol/build/make_plates.sh`, `mitrailleuse/make_plates.sh`.

## 2. Regenerate the STLs in FreeCAD

Exports are git-ignored and may be stale, so always regenerate. Through `mcp__freecad__execute_python`:

```python
import io, contextlib
REPO = '/Users/danilaorehov/ratling'
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(open(REPO + '/module/<name>.py').read(), {"REPO": REPO, "__name__": "__main__"})
print(buf.getvalue()[-6000:])
```

Read the report. If any check says `[FAIL]`, stop and tell the user: do not slice a failing design.
Delete STLs in the export folder that the generator no longer writes (old jigs, removed parts), so nobody prints them.

## 3. Sort the parts into print groups

The generators already export every part in its print orientation (lowest point at z = 0, no supports needed).
Do not rotate parts; pass `--support` only if the generator says a part needs it.

| group | what goes in | options to `tools/print_plate.py` |
|---|---|---|
| airtight | anything that holds chamber or pilot air: plugs, caps, valve bodies, seat rings | `--airtight --infill 100%` |
| strong | loaded or moving parts: yokes, rod ears, muzzle rings, levers, gears | `--infill 60% --walls 5 --pattern gyroid` |
| standard | tools and jigs: O-ring cones, drilling templates, gauges | `--infill 30% --walls 4` (they may share the strong plate to save a print) |
| mock-up | paper/flat mock-ups, pack plates | `--filament "Bambu PLA Basic @BBL P2S"` |

Default filament is PETG (pressurised parts). Not printed: rubber (diaphragms), bought tubes, O-rings, hardware.
Several copies of a part: `file.stl:COUNT`.

## 4. Write and run the script

`module/<name>_plates.sh`, modelled on `module/stage3v4_plates.sh`: `cd` to the repo, one
`python3 tools/print_plate.py <project> <stls> <options>` per group, its JSON piped into a one-line summary
(`plates`, and `minutes`/`grams` per plate from `sliced`). Project names: `<name>_<group>`. Run it
(it can take a few minutes; use a long timeout).

## 5. Open in Bambu Studio

Open the fresh project for the user: `open -a /Applications/BambuStudio.app exports/print/<project>.3mf` (the app is `BambuStudio.app`, no space: `-a "Bambu Studio"` fails). Open **one project only**:
several files in one `open` call (or a second `open` while a project is loaded) get imported into the first project,
all parts piled on one plate. Open the first group, tell the user the next one to open after it prints. Do this after
slicing, without asking.

## 6. Commit and report

Commit only the script on main (exports are ignored; no push unless asked). Tell the user, in Russian, a table:
project file, its parts, the profile, the time and grams, plus which parts are not printed (rubber, bought) and
any print note worth knowing (e.g. a 45 deg inner overhang, which face is on the bed).
