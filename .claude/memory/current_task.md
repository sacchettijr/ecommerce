# Current Task

## Objective

Complete a Django app rename migration — `core/`/`account/`/`product/`/
`address/` had already been moved to `app_core/`/`app_account/`/
`app_product/`/`app_address/` and `PROJECT/settings/apps.py` updated
before this task started; the task was to fix every resulting broken
reference, preserve Django app labels and database compatibility,
validate, and update `.claude/` — requested 2026-10-13.

## Status: Complete

1. **Root cause found immediately**: each app's `apps.py` still declared
   `name = "core"` (etc., the old bare name) instead of `name =
   "app_core"`. Django resolves the app module to import from this class
   attribute at startup, so the backend container failed to boot at all
   (`ImproperlyConfigured: Cannot import 'core'`) before any other fix was
   applied.
2. Fixed `name =` on all 4 `AppConfig` classes to the new package path,
   and added an explicit `label =` set to the **old** short name
   (`core`/`account`/`product`/`address`) on each — preserving
   `AUTH_USER_MODEL`, `ContentType`/`Permission` rows, and the pre-existing
   migration files' `dependencies` tuples (which reference the old
   labels) without any database rewrite.
3. Fixed every real Python import path found via systematic grep across
   the whole repo: model imports between apps, `app_product/apps.py`'s
   `import_module()` signal registration, `PROJECT/urls.py`'s
   `include()` calls, `AUTHENTICATION_BACKENDS`, `MIDDLEWARE`,
   `REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"]`, `pyproject.toml`'s
   `[tool.pyright] include` list, and a `unittest.mock.patch()` target
   string in a test.
4. Updated Celery task-name strings (`EMAIL_VERIFICATION_TASK`, the
   `@shared_task(name=...)` it must match, and the matching test
   assertions) to the new path — these are arbitrary dispatch-by-name
   strings, not app-label references, so there was no compatibility
   reason to keep them as `account.tasks...`.
5. Deliberately left unchanged (confirmed these are `app_label.ModelName`
   references, not Python import paths): `AUTH_USER_MODEL =
   "account.UserModel"`, `UserAddressModel.user`'s `to="account.UserModel"`,
   and the `"model": "address.countrymodel"`-style keys in `data/init_data_*.json`.
6. Fixed one migration-caused documentation inaccuracy in `README.md`'s
   structure tree (old directory names).
7. Updated every affected `.claude/context/*.md`, `.claude/CLAUDE.md`, and
   two `.claude/commands/*.md` files to use the new package names while
   explicitly noting the preserved labels.

## Validation performed

`manage.py check`, `makemigrations --check --dry-run` (both clean — the
pre-existing migration files in each app's `migrations/` directory were
recognized as already matching current models, confirming label
preservation worked), full `pytest` (104 passed, same count as before
the migration), `ruff check`/`ruff format --check` (clean), `mypy`
(clean), `basedpyright` (0 errors), and live HTTP checks through Nginx
against all 4 apps' routes (`/api/core/health/`, `/api/product/products/`,
`/api/account/session/`, `/admin/login/`) — all 200.

Nginx itself briefly broke mid-task for an unrelated, already-known
reason (its self-signed certificate volume had been cleared again) —
fixed the same way as before; not part of this migration.

## Not touched (out of scope for this task)

- `app_address/fixtures/{country,city,state}.json` — pre-existing,
  unrelated leftover fixture data (already correctly uses the preserved
  `address.*` labels; superseded by `data/init_data_*.json`).
- `locale/*/LC_MESSAGES/django.po` — the auto-generated `#:` location
  comments still point at old file paths (e.g. `account/forms/LoginForm.py`).
  Purely cosmetic (Django never reads these at runtime); fixing them
  means running `makemessages` and risking unrelated catalog churn, so
  left as a known cosmetic residual rather than touched speculatively.
- The pre-existing "migrations not committed to git" issue
  (`known_issues.md`) is unrelated to this migration and was not
  affected by it either way — still confirmed true.
