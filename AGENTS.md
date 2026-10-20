# Ratling — заметки для ИИ-агентов

Пневматика низкого давления, напечатанная на 3D-принтере, плюс покупные трубы и фитинги. Начиналось
как поворотный селектор 1 → 25 (`README.md`), сейчас делаются два изделия на общем стволе
(стальная трубка 25 × 0.6): **митральеза** из модулей v4.4 (16 или 19 стволов) и шестиствольный
**пистолет**.

**Сначала прочитай [`docs/status.md`](docs/status.md)**: какие файлы живые, какие ждут теста,
какие заморожены или выброшены. В репо много версий одного и того же (`stage3_qev`, `stage3v2`,
`stage3v3`, `stage3v4` …), и правка не того файла — самая частая потеря времени.

**Задача трогает геометрию, STL или картинки модели?** Тогда понадобится FreeCAD 1.0.2. На
облачной ВМ его нет: `sh tools/install_freecad.sh`, подробности в разделе «FreeCAD на облачной ВМ».

## Куда смотреть по теме

| Тема | Живые файлы | Документ |
|---|---|---|
| Модуль ствола митральезы | `module/stage3v4_coaxial_chamber.py` (v4.4), `module/stage3v4_plates.sh` | докстринг файла |
| Пакет, плита и каркас митральезы | `mitrailleuse/pack_layouts.py`, `mitrailleuse/pack_plate.py`, `mitrailleuse/make_plates.sh`, `mitrailleuse/pack_frame.py`, `mitrailleuse/carry_mount.py`, `mitrailleuse/rear_frame.py`, `mitrailleuse/pilot_hoses.py` | `docs/pack.md` |
| Эскиз митральезы, ротор | `mitrailleuse/mitrailleuse_concepts.py`, `mitrailleuse/rotor_timing.py`, стенды `mitrailleuse/head_bench.py`, `mitrailleuse/rotor_bench.py` | `docs/rotor.md` |
| Скин «ратлинг» (внешний вид, не детали) | `mitrailleuse/skin/ratling_skin.py`, `mitrailleuse/skin/run_skin.py` | `docs/skin.md` |
| Вес | `tools/print_mass.py` | `docs/weights.md` |
| Клапан v1.1 и стенд | `module/stage3_qev.py`, `stage3_floating_seal.py`, `stage3_vent_head.py`, `stage3_v13.py` | докстринги |
| Пистолет | `pistol/hammer_assembly.py`, `pistol/hammer_layout.py`, `pistol/build/` | `pistol/build/README.md` |
| Печать | `tools/print_plate.py`, `*_plates.sh` | `.claude/skills/plates/SKILL.md` |
| Трубка 25 мм, пробка, селектор | `connectors/`, `selector/`, `ratling/params.py` | `docs/requirements.md` |

## Как устроен код

- Почти всё — скрипты FreeCAD 1.0 (`import FreeCAD as App`, `Part`). Обычным `python3` они не
  запускаются. Запуск — в консоли FreeCAD или через FreeCAD MCP:
  ```python
  REPO = '/Users/danilaorehov/ratling'      # путь у владельца; в облаке — путь клона
  exec(open(REPO + '/module/stage3v4_coaxial_chamber.py').read())
  ```
  Без FreeCAD работают: `python3 -m ratling.params`, `python3 mitrailleuse/pack_layouts.py`,
  `python3 mitrailleuse/rotor_timing.py`, `python3 mitrailleuse/rotor_cycle_gif.py` (нужен Pillow),
  `tools/print_plate.py` (ему нужен Bambu Studio на macOS). На облачной ВМ FreeCAD надо поставить: раздел
  «FreeCAD на облачной ВМ» ниже.
- Генератор печатает отчёт с проверками `[OK ]` / `[FAIL]`, открывает модель (группы: печать,
  покупное, справка, разрез) и пишет `exports/<NAME>/` (STEP, STL, FCStd). Есть `[FAIL]` —
  не печатать и не слайсить.
- Печатные детали выгружаются уже в ориентации печати (нижняя точка z = 0). Не поворачивать.
- `exports/`, `*.stl`, `*.3mf`, `*.step` в git не идут, их всегда можно перегенерировать.
- Файлы исполняют друг друга через `exec(open(...).read())`. Флаг `*_LIBRARY = True`
  (`STAGE3_LIBRARY`, `STAGE3V4_LIBRARY`, `MECH_LIBRARY` …) перед `exec` значит «только построй
  детали, без отчёта и экспорта». Цепочки, которые легко сломать:
  - `pistol/hammer_assembly.py` → `hammer_layout.py` → `mech_layout.py` → `module/stage3_qev.py`;
  - `module/stage3_v13.py` → `stage3_qev.py` с `OVERRIDE = {...}`;
  - `mitrailleuse/pack_plate.py` и `pack_mockup.py` → `pack_layouts.py` (берут `LAYOUTS`);
  - `mitrailleuse/pack_frame.py` → `pack_layouts.py` и `module/stage3v4_coaxial_chamber.py` с `STAGE3V4_LIBRARY = True`
    (берёт детали и размеры модуля, `TURNS` повторяет `TIE_TURNS` из `pack_plate.py`);
  - `mitrailleuse/carry_mount.py` → `pack_frame.py` до строки `# --- build` (берёт плиты, направляющие, модули).
  - `mitrailleuse/rear_frame.py` → `pack_frame.py` до `# --- build` и `rotor_bench.py` с `ROTOR_BENCH_LIBRARY = True`
    (берёт головку стенда как есть). `RAIL_Z0` в `pack_frame.py` — задний торец плиты головки, `Z0 - HP_T` в
    `rear_frame.py`: меняешь одно — поправь другое.
  - `mitrailleuse/pilot_hoses.py` → `rear_frame.py` до `# --- checks` (берёт головку, её фитинги, модули в пакете).
- Параметры — константы в начале каждого генератора, а не в `ratling/params.py` (тот только для
  селектора). Некоторые переменные можно задать до `exec` (`VALVE`, `BARREL_TUBE`, `LAYERS`,
  `OVERRIDE`): смотри `try: X / except NameError` в начале файла.
- Числа модуля продублированы в плите: `TIE_R`, `TIE_ANGLES` в `pack_plate.py`, шаг 40 и Ø38 в
  `pack_layouts.py`. Меняешь шпильки или трубу камеры в v4.4 — поправь и их, и `docs/pack.md`.
- Новая версия модуля обычно правит живой файл, а прошлые версии остаются абзацами в его
  докстринге («vX (kept below for history)»). Действует только верхняя версия.

## FreeCAD на облачной ВМ

На ВМ FreeCAD заранее не стоит, но ставится за минуту. Нужен он, если задача меняет геометрию
(любой `.py` в `module/`, `mitrailleuse/pack_plate.py`, `pistol/`, `selector/`, `connectors/`),
выгружает STL или рисует картинку. Для правок документов, `pack_layouts.py` и расчётов на
бумаге он не нужен — не ставь его зря.

```sh
sh tools/install_freecad.sh          # FreeCAD 1.0.2 AppImage → /opt/freecad, ссылки в /usr/local/bin
export LANG=C.UTF-8 LC_ALL=C.UTF-8    # обязательно: без UTF-8 падает на первом «Ø» в отчёте
freecadcmd -c "REPO='$PWD'; exec(open('module/stage3v4_coaxial_chamber.py').read())"
```

- `freecadcmd` — без экрана: отчёт с проверками и `exports/<NAME>/` (STEP, STL, FCStd).
  Модуль v4.4 собирается за ~5 с.
- Картинка: генератору нужен GUI, на ВМ — через `xvfb-run` (стоит) и `tools/render_view.py`:
  ```sh
  xvfb-run -a -s "-screen 0 2560x1600x24" env LANG=C.UTF-8 LC_ALL=C.UTF-8 \
      SCRIPT=pistol/hammer_assembly.py OUT=exports/pistol.png VIEW=iso freecad tools/render_view.py
  ```
  Ошибки пишутся в `OUT.log`. Получившийся PNG смотри сам (инструмент Read показывает картинки),
  прежде чем показывать пользователю.
- Слайсинга на ВМ нет (Bambu Studio только у владельца на Mac): STL выгрузить можно, `.3mf` — нет.
- Если FreeCAD не ставится (нет сети до github.com), проверяй геометрию отдельным расчётом на
  чистом Python и прямо пиши, что модель не собиралась.

## Правила

- С пользователем — по-русски. Документы в `docs/` новые пишутся по-русски, коммиты и
  докстринги — по-английски, в стиле существующих (повелительное наклонение, что сделано и зачем,
  с числами).
- Файлы со статусом «история» и «заморожено» в `docs/status.md` не правь без прямой просьбы и не
  бери за основу нового. Ничего не удаляй: на старые версии ссылаются докстринги и коммиты.
- Решения из `docs/status.md` («Принятые решения») не переоткрывай: стальной ствол, низкое
  давление (2 бар рабочее, 5 бар расчётное), 16 и 19 стволов параллельно.
- Сменился статус модуля (новая версия, тест прошёл, ветку бросили) — обнови `docs/status.md`
  в том же коммите. Изменил числа, которые есть в `docs/*.md`, — поправь документ.
- Работа требует рук владельца (стендовый тест, покупка, печать или слайсинг на Mac, замер)?
  Допиши пункт в [`docs/human-todo.md`](docs/human-todo.md) в том же коммите и продолжай, если
  он не блокирует. Отметить пункт сделанным — тоже там, с результатом.
- Проверяй геометрию в модели (отчёт генератора) или явным расчётом; не выдавай прикидку за
  проверенное.
