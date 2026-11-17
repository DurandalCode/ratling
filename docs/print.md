# Печать: манифесты и столы Bambu

Как из STL генераторов получаются проекты `.3mf` для Bambu Lab P2S. Слайсинг
только на macOS владельца (Bambu Studio); на облачной ВМ можно проверить план
(`--dry-run`) и ориентацию (`--check`), но не нарезать.

## Коротко

1. Генератор FreeCAD пишет STL в `exports/<имя>/` (уже в ориентации печати).
2. В `plates/<id>.json` у каждой детали указана **группа печати** (`airtight`,
   `strong`, `standard`, …) — см. `tools/print_profiles.py`.
3. `python3 tools/make_plates.py <id>` собирает один `.3mf` на группу: Bambu
   раскладывает детали по столам и заполняет стол по мере роста набора.
4. `--pool` склеивает одинаковые группы из нескольких манифестов в
   `pool_<group>.3mf` — один стол на тип, а не по модулю.

Старые `*_plates.sh` остаются тонкими обёртками над тем же драйвером.

## Команды

```sh
python3 tools/make_plates.py --list
python3 tools/make_plates.py --dry-run stage3v4          # план без Bambu
python3 tools/make_plates.py --check stage3v4            # STL на месте + orient_check
python3 tools/make_plates.py stage3v4                    # нарезка (нужен Bambu Studio)
python3 tools/make_plates.py --pool stage3v4 stage3_qev  # общий стол на группу
python3 tools/make_plates.py pistol                      # exports/pistol_build/parts.json
sh module/stage3v4_plates.sh                             # то же, что make_plates stage3v4
```

Выход: `exports/print/<project>.3mf` и JSON-отчёт (минуты/граммы по столам).

## Группы

| группа | что класть | профиль |
|---|---|---|
| `airtight` | держит воздух камеры/пилота | `--airtight`, 60 % gyroid, PETG, сопло 0.4 |
| `strong` | нагруженные и подвижные | 60 % gyroid, 5 стенок, PETG |
| `strong_supports` | strong + поддержки | как strong + `--support` |
| `standard` | оснастка, лёгкие детали | 30 %, 4 стенки |
| `supports` | корпуса с нависаниями | 40 %, 4 стенки, `--support` |
| `impact` | ударные (курок) | 40 %, 6 стенок, `--support` |
| `mockup` | макеты, плиты пакета, PLA-стенды | 30 %, 4 стенки, PLA |

Новую группу добавляй в `tools/print_profiles.py`, не в одноразовый shell.
Крупные простые детали — `"nozzle": "0.8"` (отдельный проект `…_08`); герметичные
и посадки тоньше ~0.5 мм на 0.8 не класть.

## Манифест `plates/<id>.json`

```json
{
  "id": "stage3v4",
  "title": "…",
  "generator": "module/stage3v4_coaxial_chamber.py",
  "export": "exports/stage3v4_coaxial_chamber",
  "parts": [
    {"file": "rear_plug.stl", "group": "airtight", "infill": "100%"},
    {"file": "muzzle_clamp_half.stl", "group": "strong", "count": 2},
    {"file": "muzzle_sleeve.stl", "group": "mockup", "project": "stage3v44_sleeve_pla"}
  ]
}
```

- `file` — имя в `export/`, либо путь от корня репо (`exports/…`), либо `file:COUNT`.
- `group` — обязательно, из таблицы выше.
- `count`, `nozzle`, `filament` (`petg` / `pla`), `support`, `brim`, `infill`,
  `walls`, `pattern`, `process`, `allow_overhang`, `plate_each` — по нужде.
- `project` — зафиксировать имя `.3mf` (как в старых скриптах). Без поля имя
  будет `<id>_<group>`; с `--pool` поле игнорируется и группы сливаются.

Пистолет: `pistol/build/export_parts.py` уже пишет `parts.json` с группами —
`make_plates.py pistol` читает его напрямую, отдельный манифест не нужен.

## Когда что делать агенту

- Появилась новая печатная деталь → допиши её в манифест (или в `PARTS` /
  `export_parts.py` у пистолета), не сочиняй новый `*_plates.sh` с ручным списком STL.
- Пользователь просит «на стол / plates» → перегенерируй STL, затем
  `make_plates.py` (или существующую обёртку). Есть `[FAIL]` в отчёте генератора
  или в `orient_check` — не слайсить.
- Нужен один общий комплект на тип детали из нескольких модулей → `--pool`.
