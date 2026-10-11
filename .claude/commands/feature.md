---
description: Implement a feature with appropriate tests, translations, typing, and documentation
---

Implement the following feature: $ARGUMENTS

Follow the project's root instructions (`CLAUDE.md` / `.claude/CLAUDE.md`)
and these steps:

1. Read `.claude/context/project_state.md`, `architecture.md`, `domain.md`,
   and `conventions.md` first — confirm the feature doesn't already exist
   (partially or fully) before building it, and confirm which existing
   patterns to follow (e.g. model-level invariants via `Meta.constraints`
   + `save()`, per-field form mixins, the `TYPE_CHECKING` generic-base
   pattern for admin/forms).
2. Inspect the actual relevant source files — do not assume a context
   file is exhaustive or fully current.
3. Implement the smallest complete solution consistent with existing
   architecture. Keep API serializers/views/permissions/models/business
   logic properly separated (see `architecture.md`).
4. Add translations for any new user-facing string, backend and frontend,
   per `conventions.md`'s i18n section — remember the backend's
   `LANGUAGES` setting currently only activates pt-br/en/es even though
   the frontend supports 5 languages; check which side you're adding to.
5. Add tests (backend: pytest + factory-boy, matching the app's
   `tests/{api,models,views}/` layout; frontend: note that no test
   framework is installed yet — raise this rather than silently skipping
   tests or silently picking one).
6. Add/verify type annotations; run the relevant checks (ruff, mypy,
   basedpyright, pytest, tsc, eslint) and report their actual results —
   never claim a check passed without running it.
7. Update `.claude/context/` files that the feature changes (e.g.
   `api.md` for a new endpoint, `domain.md` for a new business rule) and
   add a `.claude/memory/changelog.md` entry.
8. Review the final diff for unrelated changes or accidental secrets
   before reporting the task complete.
