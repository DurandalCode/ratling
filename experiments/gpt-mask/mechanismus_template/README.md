# Mechanismus

Printed shell and drive for a handheld rotary actuator.

FreeCAD groups: `Shell` (edit these) and `Drive` (leave alone).

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

After editing shell solids, write them back:

```sh
freecadcmd -c "HERE='$PWD'; exec(open('export_edits.py').read())"
```

## Task

See `PROMPT.txt`.
