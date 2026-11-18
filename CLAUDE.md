@AGENTS.md

## Claude Code

- Скилл `/plates` (`.claude/skills/plates/SKILL.md`) — перегенерировать STL модуля, разложить по
  столам Bambu и нарезать. Он рассчитан на Mac владельца (FreeCAD MCP, Bambu Studio).
- FreeCAD у владельца вызывается через `mcp__freecad__execute_python`. В облаке MCP нет:
  FreeCAD 1.0.2 ставит окружение (`sh tools/install_freecad.sh`), запуск — `freecadcmd`.
- Если инструментов `mcp__freecad__*` в сессии нет, а FreeCAD у владельца открыт, говори с ним
  тем же сокетом: `python3 tools/fc_exec.py --list` (живые окна и их pid), затем
  `python3 tools/fc_exec.py --pid N -f script.py` или `-c "..."`. Окон бывает несколько, и в
  другом может быть чужой проект (marble_machine): сначала смотри `App.listDocuments()`.
- Показать владельцу модель — значит перегенерировать её в его GUI и открыть **основной проект
  целиком, все тела видимые**, а не отдельный документ с выборкой. Порядок: закрыть открытые
  документы `pistol_*` (`App.closeDocument`, иначе автосохранение затрёт файл), выполнить
  генератор в GUI, закрыть побочный `pistol_hammer_layout`, всем объектам
  `ViewObject.Visibility = True`, `doc.saveAs('exports/pistol_hammer_assembly.FCStd')`. Файл из
  `freecadcmd` открывается с группами скрытыми и серым (нет `GuiDocument.xml`), запасной путь —
  `tools/save_pistol_fcstd.py`.
