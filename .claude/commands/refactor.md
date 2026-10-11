---
description: Improve implementation while preserving behavior, adding regression coverage where appropriate
---

Refactor the following, preserving existing behavior: $ARGUMENTS

Rules for this command:

- Confirm current behavior first — read the actual code, and run any
  existing tests that cover it before changing anything, so you have a
  baseline.
- If the target has no test coverage today (check
  `.claude/context/testing.md` — `address/` and `core/` currently have
  none at all), add characterization tests for the current behavior
  *before* refactoring, so the refactor is provably behavior-preserving.
- Keep the change scoped to the refactor itself — do not mix in unrelated
  feature changes (per root `CLAUDE.md`: "avoid unrelated changes when
  implementing a feature or fixing a bug").
- Preserve established conventions documented in
  `.claude/context/conventions.md` (e.g. the per-field mixin pattern, the
  `TYPE_CHECKING` generic-base pattern) even if a more "generic" structure
  seems tempting — this project deliberately avoids speculative
  abstraction.
- Re-run the full relevant test/type-check suite after the refactor and
  report actual results.
- If the refactor touches a file documented in
  `.claude/memory/known_issues.md`, note whether it resolves, partially
  resolves, or is unrelated to that issue — update the entry accordingly.
