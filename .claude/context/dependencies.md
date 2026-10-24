# Dependencies

Manifests are the source of truth — check them before assuming a package
version or before adding anything new.

## Backend (`requirements.txt`)

```
celery==5.6.3
dj-database-url==3.1.2
Django==6.1.1
django-cors-headers==4.9.0
django-filter==26.1
django-guardian==3.5.0          # installed + backend-registered, NOT actually used — see known_issues.md
django-phonenumber-field[phonenumbers]==8.5.0
djangorestframework==3.18.1
drf-spectacular==0.30.0
gunicorn==26.2.0
Markdown==3.10.3
pillow==12.3.0
psycopg2-binary==2.9.12
python-dotenv==1.2.3
redis==8.1.0
uritemplate==4.2.0
whitenoise[brotli]==6.12.0
```

## Backend dev-only (`requirements-dev.txt`, includes the above via `-r requirements.txt`)

```
basedpyright==1.40.1
celery-types==0.26.0
django-browser-reload==1.21.0
django-debug-toolbar==8.0.0
django-filter-stubs==0.1.3
django-stubs==6.1.0
django-stubs-ext==6.1.0
djangorestframework-stubs==3.18.1
djlint==1.46.0
factory-boy==3.3.3
Faker==40.38.0
mypy==2.3.1
Pygments==2.21.0
pytest==9.1.1
pytest-django==4.14.0
PyYAML==6.0.3
ruff==0.16.6
```

## Frontend (`frontend/package.json`)

Dependencies: `@tailwindcss/vite` ^4.3.3, `libphonenumber-js` ^1.13.15
(added 2026-10-17 — the phone country-selector/mask feature; imported
only from its `/min` entry point for reduced metadata size, and only for
its data/formatting/validation logic, not any UI — this project hand-rolls
every input rather than pulling in a styled phone-input widget; see
`domain.md`/`architecture.md`), `react`/`react-dom` ^19.2.8,
`react-markdown` ^10.1.0, `react-router` ^8.4.0 (unified package — not
`react-router-dom`), `remark-gfm` ^4.0.1, `tailwindcss` ^4.3.3.

Dev dependencies: `@babel/core`, `@eslint/js`, `@rolldown/plugin-babel`
(runs the React Compiler Babel preset through Vite's Rolldown pipeline),
`@testing-library/jest-dom` ^7.0.1, `@testing-library/react` ^16.3.3,
`@testing-library/user-event` ^14.6.8, `@types/*`, `@vitejs/plugin-react`
^6.1.1, `babel-plugin-react-compiler` ^1.0.0, `eslint` ^10.10.0,
`eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `globals`,
`jsdom` ^30.1.2, `typescript` ~6.0.2, `typescript-eslint`, `vite` ^8.3.0,
`vitest` ^5.0.4 (added 2026-10-13 — see `testing.md`).

**No state-management library, no data-fetching library** are installed
on the frontend — confirmed absent, not an oversight to silently "fix" by
adding one without being asked.

## Dependency-management conventions

Per root project instructions: check the existing stack before adding
anything; evaluate maintenance/compatibility/security/licensing; decide
prod vs dev manifest; update the correct `requirements*.txt` /
`package.json` + lockfile; add tests; explain the reason for the addition.
Do not upgrade/downgrade major versions without checking compatibility
across the whole toolchain (Python 3.14 / Django 6.1 / Node / React 19 /
Vite 8 are all fairly new — verify against what's actually installed
before assuming an API from an older version).

## Tooling configuration (`pyproject.toml`)

- **Ruff**: `line-length = 100`, `target-version = "py314"`; lint
  `select = ["E","F","I","B","UP","RUF"]` (not `"ALL"`; no `D`/`S`/`N`
  rule groups). Per-file-ignores for `admin.py` (`RUF012`, `F401`),
  `models.py` (`F401`), `migrations/*.py` (`RUF012`, `E501`, with an
  explanatory comment about Django-generated code), `**/tests.py`
  (`F401`), and `PROJECT/settings/__init__.py` (`F403`, `F405`).
- **mypy**: `mypy_django_plugin.main` plugin, `django_settings_module =
  "PROJECT.settings"`; `disallow_untyped_defs`/`check_untyped_defs`/
  `no_implicit_optional` on (strict-ish, not full `strict = true`);
  per-module `ignore_missing_imports` for `django_browser_reload`,
  `phonenumber_field`, `whitenoise`; migrations excluded.
- **basedpyright**: `typeCheckingMode = "strict"` over
  `PROJECT, app_core, app_account, app_product, app_address, manage.py, utils`
  (repo-root-relative paths — no `backend/` prefix).
- **pytest**: minimal config — `DJANGO_SETTINGS_MODULE = "PROJECT.settings"`,
  `python_files = ["test_*.py"]`. No markers, no `addopts`, no coverage
  config.
- **Frontend**: `eslint.config.js` (flat config) extends
  `tseslint.configs.recommended` (not the type-checked variant) +
  `reactHooks`/`reactRefresh` recommended configs — no custom rules added.
  `tsconfig.app.json` does **not** set `"strict": true` (only individual
  hygiene flags: `noUnusedLocals`, `noUnusedParameters`,
  `erasableSyntaxOnly`, `noFallthroughCasesInSwitch`). See
  `../memory/known_issues.md` — the frontend's own stale `README.md` suggests
  adopting the stricter configs, but this was never done.
  **`tsconfig.json` is a references-only root** (no `compilerOptions` of
  its own) pointing at three separate project configs, each with a
  different `types` array for a different kind of file: `tsconfig.app.json`
  (`types: ["vite/client"]`, browser app code, `include: ["src"]`,
  `exclude: ["src/admin-js"]`), `tsconfig.node.json` (`types: ["node"]`,
  just `vite.config.ts`), and `tsconfig.admin-js.json` (added 2026-10-16,
  `types: ["node"]`, `module`/`moduleResolution: "nodenext"`,
  `include: ["src/admin-js"]`) — the last one exists because
  `src/admin-js/`'s jsdom-based tests use Node built-ins
  (`fs`/`path`/`import.meta.dirname`) that don't belong in the
  browser-only `app` config. `@types/jsdom` is a devDependency purely for
  this (`jsdom` itself ships no types).

## CI / automation

**None exists.** No `.github/workflows/`, no `Makefile`, no
`.pre-commit-config.yaml`. All checks (ruff/mypy/basedpyright/pytest/
tsc/eslint) are run manually per the commands in the root `README.md`.
Do not claim a check "passed in CI" — there is no CI.
