---
id: 000
title: Short imperative title, like a commit subject
status: open                      # open | done | blocked
allowed:                          # only these files may change (globs ok)
  - pistol/hammer_assembly.py
read:                             # extra files worth reading, not editing (optional)
  - pistol/hammer_layout.py
run: pistol/hammer_assembly.py    # generator verify.py executes in freecadcmd
pre:                              # Python set before the generator (optional)
  - CHECKS = False
expect:                           # text that must appear in the output (optional)
  - "[OK ] example check name"
measure:                          # bodies (object Name) to measure; 'Name: lo..hi' = volume, mm3
  - Frame_upper: 36500..38500
  - Frame_lower
solids:                           # solid count per body (optional)
  - Frame_upper: 1
---

## Зачем

Одна-две фразы: что не так сейчас и что должно стать (для исполнителя, без истории проекта).

## Что сделать

1. В `pistol/hammer_assembly.py` найди константу `EXAMPLE_WALL` (≈ строка 120) и поменяй
   `2.0` → `3.0`.
2. ...

Каждый шаг — конкретное место (имя константы / функции / строка для поиска) и конкретное число.
Если правка — новая геометрия, дай готовый фрагмент кода или точные размеры и где он вычитается
или прибавляется.

## Готово, когда

- `python3 tools/verify.py tasks/000-example.md` → `VERDICT: PASS`;
- объём `Frame_upper` вырос на ~1–2 см³ (сейчас 36332 мм³), один солид;
- остальное без изменений.

## Не трогать

- всё, что не в `allowed`; в частности ...
