# Current Task

## Objective

Comprehensive repository analysis followed by a full review/rewrite of
`.claude/` configuration (commands, context docs, memory) so it accurately
reflects the real project — requested 2026-10-11.

## Status: Complete

1. Analyzed the repository via 5 parallel read-only investigations
   (backend, frontend, infrastructure, testing/quality, existing
   `.claude`/dependencies/git history). No application code, dependency
   manifests, Docker/deployment config, or Git state were touched.
2. Wrote/rewrote every file under `.claude/context/` (13 files),
   `.claude/commands/` (8 files), and `.claude/memory/` (this file,
   `changelog.md`, `known_issues.md`) — all were empty before this task.
3. Rewrote `.claude/CLAUDE.md` to fix the `backend/`-path error and to
   point to the new context files instead of duplicating their content.
4. Left `.claude/settings.json`, the root `CLAUDE.md` (the one-line
   `@.claude/CLAUDE.md` import), and all application/infra files
   unchanged.

## Recommendations for the user (not acted on — outside this task's scope)

- `README.md` and `docs/render.md` both describe a `backend/`
  subdirectory that was removed from the real repo (confirmed by git
  commit `13d7c01`). They should be corrected — same error this task just
  fixed in `.claude/CLAUDE.md`.
- See `.claude/memory/known_issues.md` for the full list of confirmed
  issues surfaced during the analysis (migrations not in git, weak
  fallback superuser credentials, dead address forms, etc.) — none of
  these were fixed, since this task was documentation-only.
- `.gitignore` was found modified in the working tree (adds a
  `migrations/` ignore rule) in a way that contradicts another comment in
  the same file. This predates this task and was not touched by it; flag
  it to the user if migrations come up.

## Next steps (if the user wants to act on the findings)

Pick one finding from `known_issues.md` and work it as its own task —
this analysis intentionally did not fix anything outside `.claude/`.
