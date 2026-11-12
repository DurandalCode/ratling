# Frame with six-seat cylinder (fixture C)

Same frame/grip/trigger-guard as fixture B, plus a front `Cylinder` hub:
six parallel through-bores on a ring with tubes. No valves, no hoses, no
pressure ports — solids only.

Parts: `Frame_lower`, `Frame_upper`, `Frame_side`, `Frame_right`, `Grip_left`,
`Grip_right`, `Trigger_guard`, `Cylinder`. Generator: `build.py` (+ `geometry.py`).

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

## Task for the model under test

Use `PROMPT.txt`. Open **only this folder** as the workspace.
