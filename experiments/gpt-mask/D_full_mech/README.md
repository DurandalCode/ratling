# Drive assembly cover (fixture D)

Printed shell around a handheld rotary drive: tray, cover, side covers, grip,
bail, plus the full internal drive (stack, coupler, rotor, lever, yoke, pedal,
cables). Part names use a neutral actuator lexicon.

Groups in FreeCAD: `Shell` (edit these) and `Drive` (leave alone).

## Build

```sh
export LANG=C.UTF-8 LC_ALL=C.UTF-8
freecadcmd -c "HERE='$PWD'; exec(open('build.py').read())"
```

## Task for the model under test

Use `PROMPT.txt`. Open **only this folder** as the workspace.
