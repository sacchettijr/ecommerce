# Project Instructions — E-Commerce

## 1. Project Overview

A generic e-commerce application: Django REST Framework backend, React +
TypeScript frontend. Prioritize clean architecture, readability,
reusability, maintainability, security, internationalization, automated
testing, and strict type checking.

For the verified current state of the project — what's implemented,
partial, or missing — see `.claude/context/project.md` and
`project_state.md`. Do not assume a feature exists because it's listed as
a goal here; verify in source first.

### Main goals

- Allow visitors to browse the store and view products without
  authentication.
- Require authentication before users can add products to their shopping
  carts. **Note:** no cart currently exists anywhere in the codebase —
  see `.claude/context/domain.md`. Treat any cart-related task as
  building from scratch.
- Support user registration, email verification, and account activation.
- Provide clear, specific authentication errors based on the actual
  account state.
- Maintain a reusable architecture that can grow as new features are
  introduced.
- Keep frontend, backend, infrastructure, and development tooling
  organized.

## 2. Repository Structure

**The repository root is the Django project root.** There is no
`backend/` subdirectory — Django settings live at `PROJECT/settings/`,
apps at the root (`account/`, `address/`, `core/`, `product/`), and
`requirements.txt`/`requirements-dev.txt`/`manage.py`/`pyproject.toml` are
all at the repo root. (An earlier project layout did use a `backend/`
prefix; it was removed — see `.claude/memory/known_issues.md` for the
confirmed git evidence. If you see a `backend/`-prefixed path anywhere
outside `.claude/`, it is stale documentation, not the real structure —
flag it, don't follow it.)

See `.claude/context/structure.md` for the full, verified directory tree
and the responsibility of every top-level directory and every file under
`PROJECT/settings/`.

**Important:** `frontend.old/` is a legacy directory and must remain
untouched unless the user explicitly requests changes to it.

Do not move, rename, or reorganize major directories without first
evaluating the impact and explaining the reason.

## 3. Technology Stack

See `.claude/context/dependencies.md` for the exact, verified package
list and versions (backend and frontend), and `.claude/context/project.md`
for the high-level stack summary. Use the existing stack unless a change
is justified by a concrete requirement. Do not introduce new dependencies
merely to solve problems that can be addressed with existing tools.

## 4. Language and Internationalization

All source code — identifiers, comments, docstrings, test names, commit
messages — must be written in English, unless the user requests
otherwise for commit messages/documentation.

The application must support English (default), Portuguese, Spanish,
French, and Italian. **Current state** (see `.claude/context/domain.md`
and `conventions.md` for detail): the frontend's custom i18n system fully
supports all five; the backend's Django `LANGUAGES` setting currently only
activates pt-br/en/es, and the gettext catalogs under `locale/` are very
sparsely populated. Do not assume backend localization already works for
French/Italian.

Reuse the existing translation mechanisms (`gettext_lazy` on the backend,
the custom `Translations`-interface system on the frontend) — do not
introduce a second i18n library on either side. Whenever user-facing text
is introduced, add it to every catalog/locale file the relevant side
requires.

## 5. General Coding Principles

### Clean Code

Write simple, readable, explicit, maintainable code. Prefer
straightforward implementations over clever or unnecessarily abstract
ones. Avoid deep nesting and long functions. Use descriptive names. Keep
responsibilities focused. Avoid duplicated business logic. Follow each
app's existing conventions — see `.claude/context/conventions.md` for the
concrete, verified patterns already established in this codebase (the
per-field form-mixin style, the `TYPE_CHECKING` generic-base pattern for
admin/forms, database-constraint-first invariants). Do not introduce
abstractions without a meaningful, present benefit. Avoid unrelated
changes when implementing a feature or fixing a bug.

### Code Reusability

Design reusable functions, classes, validators, and components when there
is a realistic opportunity for reuse — but do not build generic frameworks
to anticipate hypothetical future requirements. Note: this project
deliberately tolerates some near-identical small mixins repeated across
apps (e.g. three separate "normalize this name field" mixins for
`account`/`product`/`address`) rather than sharing one generic
implementation across app boundaries — that's an established convention
here, not an oversight to "fix."

### Documentation

Every class and function created or substantially modified needs a brief
docstring explaining its purpose — communicate intent, not just repeat the
name. Use accurate type annotations alongside docstrings, not instead of
clear code.

### Error Handling

Handle expected errors explicitly with meaningful messages. Do not
silently swallow exceptions without a concrete, stated reason — the one
deliberate, documented exception in this codebase is
`utils/dispatch_task.py`, which intentionally logs and swallows Celery
dispatch failures so email-sending problems never turn into a failed HTTP
response (see `.claude/context/architecture.md`). Do not add a second
such swallow elsewhere without equally clear justification. Never expose
internal details, secrets, or stack traces to end users.

## 6. Backend Guidelines

Follow Django/DRF conventions while preserving the architecture verified
in `.claude/context/architecture.md`, `api.md`, and `database.md`:

- Keep settings modularized under `PROJECT/settings/`.
- Keep serializers/views/permissions/models/business logic separated —
  invariants that must hold regardless of caller belong in models
  (`save()` overrides, `Meta.constraints`), not viewsets or serializers.
- Reuse existing validators (`utils/validator.py`) and normalizers
  (`utils/normalize.py`).
- Use `transaction.atomic()` when multiple database operations must
  succeed or fail together; use `select_related()`/`prefetch_related()`
  to avoid N+1 queries.
- Prefer database constraints for invariants — see `ProductImageModel`
  for the project's best example of this pattern (DB constraint +
  `save()` auto-correction + excluding the auto-corrected fields from
  form-level unique validation).
- Never discard existing data or reset a database as a shortcut without
  explicit authorization.
- Create and test migrations whenever model changes require them —
  **and be aware migrations are not currently committed to version
  control at all** (see `.claude/memory/known_issues.md`); do not assume
  a fresh clone or CI environment has a working database.

For API design conventions (pagination, ordering, filtering, permissions,
throttling, error-code conventions), see `.claude/context/api.md`. For the
authentication/account-lifecycle rules (activation vs. email verification,
specific error codes per failure case, anti-enumeration behavior), see
`.claude/context/domain.md` — do not guess this flow; it has specific,
already-implemented, tested behavior that must be preserved.

## 7. Frontend Guidelines

Use React and TypeScript, function components and hooks, explicit types
(avoid `any`), focused components. Follow the existing React Compiler and
Vite configuration. See `.claude/context/architecture.md` for the
frontend's actual data-fetching approach (a single `useAsync` hook, no
external state/data library — do not introduce one without discussing it
first) and `.claude/context/conventions.md` for i18n conventions.

Unauthenticated users must be able to browse public products (already the
case for all existing routes). There is currently no route-guarding
abstraction because nothing needs one yet — build one when the first
account-only page is added, rather than assuming it already exists.
Protected operations must be enforced by the backend, never only the
frontend.

Use the existing Tailwind CSS v4 (CSS-first config, no
`tailwind.config.*` file) and established component conventions. Avoid
introducing another styling framework.

## 8. Type Checking and Static Analysis

Treat type checking as part of normal development. See
`.claude/context/dependencies.md` for the exact current ruff/mypy/
basedpyright/ESLint/tsconfig configuration — check it before assuming a
rule is or isn't enabled (notably: the frontend does **not** currently
have TypeScript `strict` mode or type-checked ESLint rules on, despite its
own stale README suggesting otherwise).

- Annotate parameters and return types; use concrete types.
- Use `typing.TYPE_CHECKING` for imports needed only for static analysis
  (this project's standard pattern for generic Django/DRF base classes —
  see `conventions.md`).
- Use `typing.cast` only when justified; avoid unnecessary casts and
  broad suppressions.
- When a type checker reports an error, determine whether it's a real
  defect, an incomplete annotation, a stub limitation, or a tooling
  limitation before changing the code.
- Preserve strict TypeScript checking where it exists; do not weaken
  compiler settings to hide errors.

## 9. Testing Requirements

Every new feature must include automated tests. See
`.claude/context/testing.md` for the verified current state — in short:
`address/` and `core/` have zero backend tests today, the frontend has
zero test infrastructure at all, and there is no CI. Do not assume
coverage exists where that file says it doesn't.

- Backend: pytest + pytest-django, factory-boy + Faker, matching the
  existing per-app `tests/{api,models,views}/` + `tests/factories/`
  layout.
- Frontend: no framework is installed yet — raise this with the user
  rather than silently picking one or silently skipping tests.
- Cover normal behavior, invalid input, boundaries, expected exceptions,
  auth/permissions, relevant database constraints, and side effects
  (emails, Celery tasks).
- When fixing a bug, add a regression test when practical.
- Run the relevant checks before declaring a task complete. If a check
  cannot be run in the current environment, state that explicitly — never
  claim a test passed without running it.

## 10. Infrastructure and Docker

Docker Compose is the foundation of local development. See
`.claude/context/architecture.md` for the current service topology and
`.claude/context/security.md` for confirmed, unresolved infra-security
findings (several ports published to the host beyond what's necessary,
a self-signed TLS certificate, etc.) — do not silently "fix" these;
surface them and let the user decide, since some are deliberate tradeoffs
for a local/prototype environment.

- Inspect `docker-compose.yml` and the relevant Dockerfiles before
  changing build/runtime configuration — don't assume they match any
  cached description of them.
- Preserve named volumes for persistent data. Never run
  `docker compose down -v` unless volume deletion is explicitly
  authorized.
- Do not disable BuildKit/Bake permanently without understanding the
  underlying cause.
- Keep environment-specific values out of source code; never commit real
  secrets. `.env` must stay out of version control; `.env-example` must
  stay placeholder-only.

Nginx routes `/` to the frontend, `/api/` to the backend API, `/admin/`
to Django admin, `/static/`/`/media/` to collected files — inspect
`nginx/nginx.conf` directly before changing routing, TLS, or forwarded
headers; it is currently pinned to one deployed IP address, not a
portable template (see `security.md`).

Render is the planned hosted environment. Inspect `render.yaml` and
`docs/render.md` directly before changing deployment configuration — note
that `docs/render.md` itself currently contains stale `backend/`-prefixed
paths (see `.claude/memory/known_issues.md`); don't propagate that error
into new work.

## 11. Security Requirements

See `.claude/context/security.md` for the full, verified picture,
including confirmed issues already found (a weak hard-coded fallback
superuser path, ports published beyond what's necessary, etc.) — these
are tracked in `.claude/memory/known_issues.md` and are not yet fixed;
don't assume they've been addressed just because they're documented.

- Never hardcode or log secrets, credentials, tokens, or private keys.
- Keep `.env` out of version control; keep `.env-example` placeholder-only.
- Validate and authorize all sensitive operations on the backend — the
  frontend has no route guards today, so backend enforcement is the only
  real protection for anything sensitive.
- Validate uploaded files (reuse `utils/validator.py`).
- Preserve CSRF/CORS/session/cookie/HTTPS protections appropriate to the
  environment; do not weaken them to make a tool or test pass without an
  explicit, justified decision.
- Do not expose whether an arbitrary email is registered — the existing
  resend-verification and password-reset flows are already anti-
  enumeration by design; preserve that if you touch them.

## 12. Dependencies and Version Management

Backend manifests: `requirements.txt`, `requirements-dev.txt`,
`pyproject.toml` (repo root — no `backend/` prefix). Frontend manifests:
`frontend/package.json`, `frontend/package-lock.json`. See
`.claude/context/dependencies.md` for the exact current contents.

Before adding a dependency: check whether the existing stack already
covers it; evaluate maintenance/compatibility/security/licensing; pick
the correct manifest (prod vs. dev); update lockfiles; add tests; explain
the reason. Do not upgrade/downgrade major dependencies without checking
compatibility across the whole toolchain.

## 13. Claude Code Workflow

`.claude/` holds project-specific instructions, commands, context, and
memory:

```text
.claude/
├── CLAUDE.md            this file
├── settings.json        permissions, hooks, enabled plugins
├── commands/            analyze, context, feature, refactor, release,
│                        review, sync, tests
├── context/             verified, navigable project facts (see table below)
└── memory/              changelog, current_task, known_issues
```

### When to consult which context file

| Need to know about... | Read |
|---|---|
| What exists, what doesn't, what's partial | `context/project_state.md` |
| Directory/file layout, settings module responsibilities | `context/structure.md` |
| Request flow, service topology, design decisions | `context/architecture.md` |
| Auth lifecycle, addresses, catalog rules, cart status, i18n status | `context/domain.md` |
| Endpoints, pagination/filtering/throttling conventions | `context/api.md` |
| Models, constraints, migrations status | `context/database.md` |
| Naming/style/error-handling/i18n/testing patterns to follow | `context/conventions.md` |
| Exact package versions, tool configuration, CI status | `context/dependencies.md` |
| Auth/authz posture, confirmed security findings | `context/security.md` |
| Test coverage by app, factories, how to run checks | `context/testing.md` |
| Business-rule math (there is currently none of substance) | `context/calculations.md` |
| High-level purpose/stack/goals | `context/project.md` |
| Documented plans vs. open suggestions | `context/roadmap.md` |

### General workflow

Before implementing a change: understand the request, inspect the
relevant source files directly (treat `.claude/context/` as a verified
starting point, not a substitute for reading real code that could have
changed), read relevant commands/context, identify affected
modules/tests/dependencies/security implications, prefer the smallest
complete solution that preserves conventions, implement, add/update
tests, run relevant checks, inspect the final diff for unrelated changes
or secrets, and summarize what changed, what was tested, and what remains.

Ask for clarification when ambiguity could materially change
implementation, data integrity, security, or architecture. Otherwise make
reasonable assumptions, state them, and proceed.

Do not claim to have inspected files, run commands, installed plugins, or
executed tests unless those actions actually occurred.

### Memory management

Update `.claude/memory/` after meaningful work:

- `changelog.md` — meaningful completed changes.
- `current_task.md` — current objective, progress, next steps, blockers.
- `known_issues.md` — confirmed issues, reproducible failures,
  workarounds, unresolved risks. Distinguish confirmed facts from
  hypotheses; remove or update entries once resolved.

Keep memory concise and factual. Never store secrets or unnecessary
personal data in memory. Do not overwrite unrelated memory or discard
previous findings without reason.

## 14. Claude Code Plugins

`.claude/settings.json`'s `enabledPlugins` currently enables:
`security-guidance`, `code-review`, `claude-code-setup`,
`claude-md-management`, `context7`, `typescript-lsp`, and
`chrome-devtools-mcp` (all `@claude-plugins-official`). The user has also
expressed intent to evaluate `claude-mem`, "Omni Route", Playwright, and
Supabase, but those are **not** currently enabled — do not assume their
commands, agents, or MCP servers exist. Supabase-specific tooling, if ever
adopted, must not replace the existing Django/PostgreSQL architecture
without an explicit architectural decision. Review any new plugin's
source, permissions, hooks, and dependencies before installation.

## 15. Git and Change Management

Keep changes focused on the requested task. Avoid modifying generated
files or unrelated configuration unnecessarily. Never commit secrets or
local-only configuration. Inspect `git diff`/`git status` before
completing significant work. Do not rewrite history, force-push, or
discard user changes without explicit authorization. Do not commit or
push unless asked. Note: `.claude/settings.json` already denies
`git push*`, `git reset --hard*`, `git clean -f*`, and
`docker compose down -v*`/`docker system prune*` at the permission layer
— respect that even if a task seems to need one of them, and surface the
conflict to the user instead of trying to route around it.

## 16. Completion Criteria

A task is complete when: the requested behavior is implemented; code
follows existing conventions (`context/conventions.md`); relevant
translations are provided on the correct side(s); tests are added/updated;
relevant checks are run or their limitations stated; security and data
integrity are preserved; relevant `.claude/memory/` files are updated; and
the final response explains what changed, what was tested, and any
outstanding concerns.

Prioritize correctness, clarity, security, and maintainability over
unnecessary complexity or speed.
