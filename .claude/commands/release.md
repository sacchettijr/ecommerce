---
description: Check tests, linting, typing, dependencies, configuration, and deployment readiness before a release
---

Prepare a release readiness check: $ARGUMENTS

There is no CI in this project (`.claude/context/dependencies.md`) — this
command is the manual equivalent. Run and report actual results for each:

1. **Backend**: `ruff check`, `ruff format --check`, `mypy
   --config-file=pyproject.toml .`, `basedpyright`, `python manage.py
   check`, `python manage.py makemigrations --check --dry-run`, the full
   `pytest` suite.
2. **Frontend**: `tsc -b` (via `npm run build`), `npm run lint`. Note that
   no test suite exists to run (`.claude/context/testing.md`) — don't
   claim frontend tests ran.
3. **Migrations**: cross-check against
   `.claude/memory/known_issues.md` — migrations are currently **not**
   committed to git; confirm with the user whether this is still the
   intended state before any deployment that relies on a fresh clone/CI.
4. **Dependencies**: confirm `requirements.txt`/`requirements-dev.txt`/
   `frontend/package.json` + lockfiles are consistent with what's actually
   imported/used; flag anything unpinned or clearly unused.
5. **Configuration**: confirm `.env-example` still matches the variables
   actually read by the code (see `.claude/context/security.md` for the
   known `INTERNAL_IP` gap); confirm no secret value is about to be
   committed (`git status`/`git diff`, scanning for anything that looks
   like a credential).
6. **Deployment target** (if Render): re-read `render.yaml` and
   `docs/render.md` fresh, don't assume they still match — flag any drift
   immediately rather than treating cached context as current.
7. Report a clear PASS/FAIL per check, never a blanket "looks good."
   If a check cannot be run in the current environment, say so explicitly.
