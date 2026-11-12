# Mechanismus

Printed shell and drive for a handheld rotary actuator / pack frame.

FreeCAD groups: `Shell` (edit these) and `Drive` (leave alone).
Part list: `manifest.json`. Each part is `parts/<stem>.brep` with a `.step` twin; the newest
file wins when building, so edits can be written back in either format.

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

After editing shell solids:

```sh
freecadcmd -c "HERE='$PWD'; exec(open('export_edits.py').read())"
```

## Task

See `PROMPT.txt`.
