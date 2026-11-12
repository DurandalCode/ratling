# Frame and hammer cover (fixture B)

Printed frame halves around a thumb-hammer drive: lower/upper frame, side
plates, grip, trigger guard. Same outer envelope as fixture A; names follow
the mechanism (Frame, Hammer clearance, Trigger_guard).

Parts: `Frame_lower`, `Frame_upper`, `Frame_side`, `Frame_right`, `Grip_left`,
`Grip_right`, `Trigger_guard`. Generator: `build.py` (+ `geometry.py`).

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

## Task for the model under test

Use `PROMPT.txt`. Open **only this folder** as the workspace.
