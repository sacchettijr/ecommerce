---
description: Review changes for correctness, security, maintainability, typing, testing, and regressions
---

Review the following changes: $ARGUMENTS

If no specific diff/PR/branch is named, review the current uncommitted
changes (`git status` / `git diff`).

Check for:

- **Correctness**: does the change do what it claims? Trace through the
  actual logic rather than trusting a docstring or commit message.
- **Security**: secrets, CSRF/CORS/session/cookie handling, authorization
  (global DRF default is `IsAuthenticated` — confirm any new `AllowAny`
  is actually intended), upload validation. Cross-check
  `.claude/context/security.md` for issues already known to exist in this
  area.
- **Conventions**: does it follow `.claude/context/conventions.md` (naming,
  the `TYPE_CHECKING` generic-base pattern, per-field form mixins,
  database-constraint-first invariants)? Flag deviations rather than
  silently accepting them.
- **Typing**: are new functions/methods fully annotated? Would `mypy`/
  `basedpyright` actually pass — check, don't guess.
- **Tests**: is the new/changed behavior covered? Is a regression test
  present for a bug fix?
- **i18n**: is every new user-facing string translatable, and translated
  in all languages that need it on that side (backend: pt-br/en/es
  currently active; frontend: all 5)?
- **Scope**: does the diff contain unrelated changes, accidental
  deletions, or stray debug code?

Report findings ranked by severity, with file:line citations. Do not
state that something "works" unless you actually ran it or its test.
