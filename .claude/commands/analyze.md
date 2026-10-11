---
description: Inspect code, architecture, or a specific issue without modifying files unless explicitly asked
---

Investigate the following in this repository: $ARGUMENTS

Rules for this command:

- Read-only by default. Do not edit, create, or delete files unless the
  request explicitly asks for a change.
- Verify claims against actual source files — do not rely on
  `.claude/context/*.md` alone; those are a starting point, not a
  substitute for reading the real code. If something in those files turns
  out to be stale, say so.
- For anything touching more than 2-3 files, use the `Explore` agent
  (or several in parallel for independent areas) rather than reading
  everything into your own context.
- Distinguish explicitly between: confirmed facts (cite the file/line),
  reasonable inferences, and open questions you could not resolve from
  the repository alone.
- If the investigation surfaces a defect, inconsistency, or risk worth
  remembering, record it in `.claude/memory/known_issues.md` — but do not
  fix it unless asked to.
- Finish with a concise summary: what was found, where, and what (if
  anything) should happen next.
