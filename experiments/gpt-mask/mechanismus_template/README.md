# Mechanismus

Printed shell and drive for a handheld rotary actuator / pack frame.

FreeCAD groups: `Shell` (edit these) and `Drive` (leave alone).

- `parts/<stem>.brep` (+ `.step` twin): the parts as they are now. Read-only reference; do not edit.
- `manifest.json`: part list (`stem`, `label`, `group`) and, per part, `sees`: the stems that
  `ctx` can hold for that part.
- `edits/<stem>.py`: your changes, one file per Shell part. This is the only place to edit.
- `edit_runner.py`: runs the edits; do not change.

## Edit format

```python
import Part
import FreeCAD as App


def edit(part, ctx):
    # part: Part.Shape of this part; ctx: {stem: Part.Shape} of its neighbours (read-only)
    return part.makeFillet(2.0, [e for e in part.Edges if e.Length > 20][:6])
```

Any FreeCAD `Part` operations. The result must be a valid shape with the same number of solids
and a volume within 50%..150% of the original. Pick edges and faces by geometry (position, length, normal), never by
index: the base shape is regenerated and indices change.

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

Prints `[edit] ...` with the volume change per edited part, `[FAIL]` and stops if an edit is invalid.

## Task

See `PROMPT.txt`.
