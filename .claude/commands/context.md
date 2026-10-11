---
description: Update .claude/context/ documents based on verified findings from recent work
---

Update the relevant `.claude/context/*.md` file(s) to reflect verified
changes: $ARGUMENTS

Rules for this command:

- Only record what has actually been verified in this session (a file you
  read, a command you ran, a test result you observed) — never copy a
  claim from a previous conversation turn without re-checking it if the
  underlying file could plausibly have changed since.
- Update the single most relevant context file(s) rather than
  duplicating the same fact across several. Context files cross-reference
  each other by name (e.g. "see `domain.md`") instead of repeating
  content — follow that pattern.
- Do not touch `.claude/CLAUDE.md`'s project-wide rules for this —
  `context.md` is for factual project state, not for changing workflow
  rules (use a direct request for that instead).
- If a finding reveals a defect or risk rather than a simple fact, put it
  in `.claude/memory/known_issues.md`, not in a `context/` file.
- If you find an existing context file describing something that no
  longer matches the repository, correct it and note what changed and
  why in `.claude/memory/changelog.md`.
- Keep entries concise, in English, and grounded in file paths.
