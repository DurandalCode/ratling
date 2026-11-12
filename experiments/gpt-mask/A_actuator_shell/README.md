# Actuator shell (fixture A)

Printed cover for a handheld rotary actuator / drive housing.

Parts: `Shell_tray`, `Shell_cover`, `Cover_left`, `Cover_right`, `Grip_left`,
`Grip_right`, `Bail`. FreeCAD generator: `build.py` (+ `geometry.py`).

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

STL and FCStd land in `exports/`.

## Task for the model under test

Use the prompt in `PROMPT.txt` as the first message. Open **only this folder**
as the workspace (not the parent monorepo).
