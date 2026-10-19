@AGENTS.md

## Claude Code

- Скилл `/plates` (`.claude/skills/plates/SKILL.md`) — перегенерировать STL модуля, разложить по
  столам Bambu и нарезать. Он рассчитан на Mac владельца (FreeCAD MCP, Bambu Studio).
- FreeCAD у владельца вызывается через `mcp__freecad__execute_python`; в облачной сессии его
  обычно нет.
