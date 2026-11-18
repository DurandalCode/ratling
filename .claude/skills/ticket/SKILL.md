---
name: ticket
description: Write a closed ticket in tasks/ that a cheaper model (GLM, Kimi, Grok in opencode or Cursor) can execute with tools/verify.py as the judge, or review a finished ticket. Use only when the owner asks for a ticket / "отдай слабой модели" / "проверь тикет"; otherwise just do the work directly.
argument-hint: <what to change> | review tasks/NNN-*.md
---

# Ticket for a worker model

Claude normally works directly by AGENTS.md. This skill is for handing a change to a weaker
model. Reply to the owner in Russian.

## Write a ticket

1. Decide the design yourself: which live file (`docs/status.md`), which constants or code,
   exact numbers. The worker cannot design; every step must be "find X, change A → B" or a
   ready code fragment with the place it goes.
2. Copy `tasks/TEMPLATE.md` to `tasks/NNN-short-name.md` (next free number). Fill `allowed`
   with the minimum set of files, `run` with the generator, `measure` with the bodies the
   change touches (object `Name`, see the generator's `add(...)` calls).
3. Run `python3 tools/verify.py tasks/NNN-*.md` once **before** the edit: it prints current
   volumes. Set the `measure` bounds from them and the expected change (it will FAIL on the
   bounds now; that is fine). Pistol: keep `CHECKS = False` in `pre`.
4. "Зачем", "Что сделать", "Готово, когда" in Russian, plain words, no project history.
5. Tell the owner the path and the command for the worker:
   `opencode` → agent `worker`, message `tasks/NNN-*.md`; Cursor → open the ticket and say
   "сделай тикет".

## Review a ticket

`python3 tools/verify.py tasks/NNN-*.md --baseline`, then `git diff` against "Что сделать".
ACCEPT → set `status: done`, commit by AGENTS.md rules if the owner agrees. RETURN → say what
to fix; sharpen the ticket rather than fixing the code yourself, unless the owner says so.
