@AGENTS.md

## Claude Code

- Скилл `/plates` (`.claude/skills/plates/SKILL.md`) — перегенерировать STL модуля, разложить по
  столам Bambu и нарезать. Он рассчитан на Mac владельца (FreeCAD MCP, Bambu Studio).
- FreeCAD у владельца вызывается через `mcp__freecad__execute_python`. В облаке MCP нет:
  FreeCAD 1.0.2 ставит окружение (`sh tools/install_freecad.sh`), запуск — `freecadcmd`.
