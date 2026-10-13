# Changelog

Historical entries below are reconstructed only from `git log` (9 commits
total at the time of writing — this is confirmed, not an abbreviated
sample) plus this session's own configuration work. Where git history
doesn't provide enough detail to describe *what* changed, that limitation
is stated explicitly rather than guessed.

## From git history (oldest → newest, by commit message only)

- `ff5919b` — Reworking the project to adapt it for deployment to Render.
- `9e5fd39` — The project has been adapted for rendering with Docker.
- `0d5f3b9` — Render adaptation test.
- `13d7c01` — Removed "backend" from the path (the repo was restructured
  from a `backend/`-prefixed layout to Django living at the repo root;
  this is the change that later made `README.md`/`docs/render.md`'s
  `backend/`-prefixed instructions stale — see `known_issues.md`).
- `513382b` — Testing with Nginx paused due to conflicts with the public
  IP address.
- `6d3bbb1` — Website communication via public IP working with HTTP;
  verified to function securely (HTTPS).
- `bf2fa80` — HTTPS connection working with certificate generation.
- `2304b49` — Added the model and forms related to user addresses
  (`UserAddressModel` + `UserAddress*Form`s — later found to be unwired,
  see `known_issues.md`).
- `2e0dc88` (HEAD at analysis time) — Bypassed a Docker build permission
  issue; removed an SSL-permission check from the `DEBUG` gate.

## 2026-10-11 — Full repository analysis and `.claude/` configuration rewrite

Performed a comprehensive, verified (not assumed) analysis of the entire
repository — backend (Django apps, settings, API, auth lifecycle, Celery),
frontend (React/TS structure, routing, API integration, i18n, styling),
infrastructure (Docker Compose, Dockerfiles, Nginx, Render, service
configs), testing/quality tooling, and the pre-existing `.claude/`
configuration, dependencies, and git history — using 5 parallel read-only
investigations, then synthesized the findings into this `.claude/`
directory.

**What was found:** the entire `.claude/commands/`, `.claude/context/`,
and `.claude/memory/` trees were empty placeholder files (0 bytes each);
`.claude/CLAUDE.md` (609 lines, uncommitted) was substantially accurate
but repeated a `backend/`-subdirectory path error in 4 places, matching
the same error already present in `README.md`/`docs/render.md`.
`.claude/settings.json` was accurate and was left unchanged.

**What changed:**
- Rewrote `.claude/CLAUDE.md`: fixed every `backend/`-prefixed path
  reference, trimmed detailed content out to the new `.claude/context/`
  files it now points to, kept the essential project-wide rules.
- Wrote all 13 `.claude/context/*.md` files from scratch, grounded in the
  verified findings (see each file for specifics).
- Wrote all 8 `.claude/commands/*.md` files from scratch.
- Wrote this file, `current_task.md`, and `known_issues.md` from scratch.
- Did not modify any application source code, `README.md`,
  `docs/render.md`, dependency manifests, Docker/deployment configuration,
  or `.claude/settings.json` — all out of scope for this task (fixing the
  `backend/`-path error in `README.md`/`docs/render.md` is recorded as a
  recommendation in `current_task.md`, not performed).

No code, tests, dependencies, or Docker/Git state were modified as part
of this task — it was configuration/documentation only.

## 2026-10-11 — Wired `UserAddressModel` admin + model-level exclusivity

Found `account/admin/UserAddressAdmin.py` and `UserAddressInlineAdmin.py`
had drifted to reference fields that don't exist on the model (`address`,
`zip_code`, `is_primary` instead of the real `street`/`postal_code`/
`primary`) — `manage.py check` was failing outright (`admin.E108`).

- `account/models/UserAddressModel.py`: added `save()` (locks the parent
  user row, demotes any other `primary=True` address for the same user —
  mirrors `ProductImageModel.save()`), plus `validate_constraints`/
  `_get_unique_checks` overrides so admin inline formsets tolerate a
  transient multi-primary submission before the model reorganizes it.
- `account/forms/UserAddressBaseForm.py`: simplified — removed the
  custom `save()`/`__init__` (admin never actually invoked
  `form.save(commit=True)`, so that logic was silently dead in the admin
  path; the model now owns the rule for every caller). `user` added to
  `Meta.fields` for the standalone admin.
- `account/admin/UserAddressAdmin.py`: fixed `list_display`/`list_filter`/
  `search_fields` to real fields; added `get_form()` to use
  `UserAddressCreateForm`/`UserAddressUpdateForm` for add vs change.
- `account/admin/UserAddressInlineAdmin.py`: fixed `fields`; wired to
  `UserAddressBaseForm`.
- `account/admin/UserAdmin.py`: added `inlines = (UserAddressInlineAdmin,)`.

Verified: `manage.py check`/`makemigrations --check` clean, full `pytest`
(104 passed), ruff/mypy/basedpyright clean, and a real end-to-end HTTP
test against the running admin (login, open a user's change page,
submit two inline address rows both marked `primary=True` in one
request) confirmed exactly one ends up primary. No migration was needed
(pure behavior change, the DB constraint already existed). Updated
`.claude/memory/known_issues.md` to mark the "dead address forms" entry
resolved.

## 2026-10-13 — Completed the `app_` prefix rename for all 4 Django apps

Directories had already been renamed (`core→app_core`, `account→app_account`,
`product→app_product`, `address→app_address`) and `INSTALLED_APPS` updated
before this task started, but every app's `AppConfig.name` still said the
old bare name — Django failed to boot (`ImproperlyConfigured: Cannot
import 'core'`). Fixed `name =` on all 4 `AppConfig`s to the new package
path and added an explicit `label =` set to the **old** short name on
each, preserving `AUTH_USER_MODEL = "account.UserModel"`, `ContentType`/
`Permission` rows, and the pre-existing (locally-present, still
git-ignored per the known migrations issue) migration files' `dependencies`
tuples — confirmed via `makemigrations --check --dry-run` reporting "No
changes detected" against those same files after the rename.

Fixed every real Python import path found via systematic repo-wide grep:
`app_account/models/UserAddressModel.py`, `app_address/models/*.py`,
`app_account/models/UserModel.py` (cross-app imports),
`app_product/apps.py`'s `import_module()`, `PROJECT/urls.py`'s
`include()` calls, `PROJECT/settings/authentication.py`'s
`AUTHENTICATION_BACKENDS`, `PROJECT/settings/middleware.py`'s
`MIDDLEWARE`, `PROJECT/settings/rest_framework.py`'s
`DEFAULT_PAGINATION_CLASS`, `pyproject.toml`'s `[tool.pyright] include`,
and a `unittest.mock.patch()` target string plus two task-name
assertions in `app_account/tests/api/test_auth_api.py`. Updated the
Celery task-name strings in `app_account/emails/send_verification_email.py`
and `app_account/tasks/send_email_verification_email.py` to match (an
arbitrary dispatch-by-name string, not an app-label reference, so no
compatibility reason to keep the old value). Left `AUTH_USER_MODEL`,
`UserAddressModel.user`'s `to="account.UserModel"`, and
`data/init_data_*.json`'s `"address.*"` fixture-model keys unchanged —
confirmed these are `app_label.ModelName` references, not Python import
paths.

Verified: `manage.py check`, `makemigrations --check --dry-run`, full
`pytest` (104 passed, unchanged count), `ruff`, `mypy`, `basedpyright` —
all clean. Live HTTP checks through Nginx confirmed all 4 apps' routes
respond correctly. Updated every affected `.claude/context/*.md` file,
`.claude/CLAUDE.md`, and two `.claude/commands/*.md` files to the new
package names with the label-preservation note. Fixed one incidental
documentation inaccuracy in `README.md`'s structure tree.

## 2026-10-13 — Verified `data/init_data_*.json` fixtures need no change

Checked, on request, whether the `app_` rename required updating the
`"model": "address.countrymodel"` / `"address.statemodel"` /
`"address.citymodel"` keys in `data/init_data_{Country,State,City}Model.json`.
Confirmed via `apps.get_app_config("address")` that the label `address`
still resolves to the `app_address` package (as designed — see the
previous entry), then actually ran `manage.py loaddata` with all three
files against the running database: all 5,650 objects installed with no
error, counts matched (2 countries, 77 states, 5,571 cities), and
`manage.py check` stayed clean. No fixture changes were needed or made.
