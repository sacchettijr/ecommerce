# Repository Structure

Verified against the actual filesystem. The repository root **is** the Django
project root — there is no `backend/` subdirectory. (Earlier project
documentation, and an earlier draft of `.claude/CLAUDE.md`, claimed a
`backend/` prefix; this was removed in commit `13d7c01 "Removed 'backend'
from the path"` and the docs were never fully updated. See
`project_state.md` and `../memory/known_issues.md`.)

```text
ecommerce/
├── .claude/                 Claude Code configuration (this directory)
├── PROJECT/                 Django project package (settings, urls, celery app)
│   └── settings/            modularized settings — see below
├── app_account/             users, auth, email verification, user addresses
├── app_address/             Country/State/City reference data — mostly
│                             admin-managed, but now has a small staff-only
│                             API too (api/viewsets/, api/serializers/,
│                             urls.py) backing the admin's own cascading
│                             dropdowns — not "admin-only" in the sense of
│                             having no API at all. See `api.md`/`domain.md`.
├── app_core/                shared BaseModel, contact form/API, health check
├── app_product/             catalog: categories, products, product images
├── utils/                   cross-app helper functions (no Django app of its own)
├── static/, staticfiles/    source static assets / collectstatic output —
│                             static/src/js/admin/ and static/src/css/admin/
│                             hold the Django Admin's own vanilla-JS/CSS
│                             (city_location_select.js, product_image_inline.js,
│                             user_address_inline.js, product_slug_preview.js,
│                             markdown_editor.js/.css, user_address_inline.css);
│                             static/src/js/slugify.js is a plain (non-admin)
│                             sibling, not under admin/
├── templates/                Django templates (email only — see note below)
├── locale/                  gettext catalogs: en, es, fr, it, pt_BR
├── data/                    Django fixture JSON for `loaddata`/`dumpdata`
│                             (country/state/city reference data, product/
│                             category/image seed data) — paired with
│                             dev_dump_data.cmd/dev_load_data.cmd below
├── frontend/                 React + TypeScript + Vite app (independent project)
├── frontend.old/             legacy Django-template frontend — DO NOT TOUCH
├── database/, redis/, rabbitmq/, cloudbeaver/   per-service config (no Dockerfile;
│                             official images with a mounted config file, or nothing)
├── nginx/                    nginx.conf (reverse proxy for local dev and the
│                             currently-deployed IP-based host)
├── docker-compose.yml         local development orchestration
├── Dockerfile                 Django/Celery image (shared by backend + celery services)
├── entrypoint.sh               container startup: collectstatic, migrate, create_admin, gunicorn
├── render.yaml                 Render Blueprint (hosted prototype deployment)
├── docs/render.md              Render deployment guide
├── requirements.txt / requirements-dev.txt   Python dependencies
├── pyproject.toml              ruff / mypy / pyright / pytest / djlint config
├── manage.py
├── dev_build.cmd                Windows helper: docker compose build/up
├── dev_load_data.cmd             Windows helper: loaddata the data/*.json fixtures
├── dev_dump_data.cmd              Windows helper: dumpdata into data/*.json (the inverse)
├── dev_reset.cmd                 Windows helper: local dev reset (see the script
│                                 itself before relying on it — not independently
│                                 audited here)
├── README.md / CLAUDE.md          repo-root docs — CLAUDE.md `@`-includes
│                                 `.claude/CLAUDE.md`, the real instructions file
├── .env / .env-example          environment variables (`.env` is gitignored)
└── media/, mediafiles/          uploaded media (dev) / collected media volume
```

**Important:** `frontend.old/` is a legacy directory and must remain
untouched unless the user explicitly requests changes to it.

**Important:** `.env` must never be read into chat, logs, or documentation.
`.env-example` is safe to read (placeholder values only).

## Django settings (`PROJECT/settings/`)

Modular, one concern per file. Aggregated via `from .X import *` in
`PROJECT/settings/__init__.py`. The apparent import order in `__init__.py`
is **not** what guarantees `.env` is loaded before it's needed — each
module's own explicit intra-package imports do that (e.g. `authentication.py`
imports `from .templates import FRONTEND_URL`, and `templates.py` imports
`from .base import BASE_DIR`, which transitively runs `base.py`'s
`load_dotenv()` the first time any of this chain is imported). Python only
executes a module once, so as long as a module's own imports pull in its
real dependencies, the list order in `__init__.py` is cosmetic. This is not
documented in code comments — keep it in mind before reordering that list.

| File | Responsibility |
|---|---|
| `apps.py` | `INSTALLED_APPS` |
| `authentication.py` | password validators, `LOGIN_URL`/redirects, `AUTH_USER_MODEL`, `AUTHENTICATION_BACKENDS` (guardian + custom email-verified backend) |
| `base.py` | `BASE_DIR`, `load_dotenv()`, `ROOT_URLCONF`, `WSGI_APPLICATION` |
| `cache.py` | Redis cache backend (falls back to `locmem` when the `RENDER` env var is set); has a second, redundant `load_dotenv()` call — see `../memory/known_issues.md` |
| `celery.py` | `CELERY_BROKER_URL` (RabbitMQ), `CELERY_RESULT_BACKEND` (Redis), serializers, timezone |
| `cors.py` | `CORS_ALLOWED_ORIGINS = [FRONTEND_URL]`, `CORS_ALLOW_CREDENTIALS` |
| `database.py` | `DATABASES["default"]` — `DATABASE_URL` (Render) if present, else discrete `POSTGRES_*` vars (local) |
| `debug_toolbar.py` | conditionally adds `debug_toolbar` / removes `django_browser_reload` based on `DEBUG`/`TESTING` |
| `drf_spectacular.py` | `SPECTACULAR_SETTINGS` |
| `email.py` | SMTP settings |
| `internationalization.py` | `LANGUAGE_CODE`, `LANGUAGES` (**currently only pt-br/en/es** — see `domain.md`), `LOCALE_PATHS`, `TIME_ZONE`, phone-number default region |
| `media.py` | `MEDIA_URL`, `MEDIA_ROOT` |
| `messages.py` | `MESSAGE_TAGS` |
| `middleware.py` | `MIDDLEWARE` list |
| `rest_framework.py` | DRF defaults: `IsAuthenticated`, filter backends, `StandardPagination`, per-scope throttle rates, `AutoSchema` |
| `security.py` | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, Render hostname handling, `CSRF_TRUSTED_ORIGINS`, `SECURE_PROXY_SSL_HEADER` (always on — trusts Nginx's `X-Forwarded-Proto`), `SECURE_SSL_REDIRECT`/cookie-secure flags (only when not `DEBUG`) |
| `static.py` | `STATIC_URL`/`STATICFILES_DIRS`/`STATIC_ROOT`, Whitenoise storage when not `DEBUG` |
| `templates.py` | `TEMPLATES` (email templates only — React renders every page; Django templates are not used for app UI), `FRONTEND_URL`, `SITE_NAME` |
| `test.py` | `TESTING` flag (`"test" in sys.argv or "PYTEST_VERSION" in os.environ`) |

## Django apps

Each app's Python package is now `app_`-prefixed (e.g. `app_account`), but
its Django **app label** was deliberately preserved as the short original
name (`account`, `address`, `core`, `product`) via an explicit `label =`
on each app's `AppConfig`, alongside `name = "app_account"` etc. This keeps
existing migrations, `AUTH_USER_MODEL = "account.UserModel"`,
`ContentType`/`Permission` rows, and FK `to="account.UserModel"`-style
string references valid without any database rewrite — only real Python
import paths (`from app_account.models import ...`,
`include(arg="app_account.urls")`, `AUTHENTICATION_BACKENDS`,
`MIDDLEWARE`, Celery task name strings, `pyproject.toml`'s pyright
`include`) needed to change. See `../memory/changelog.md`.

| App | Package | Label (unchanged) | Has API? | Has Admin? | Responsibility |
|---|---|---|---|---|---|
| `app_account/` | `app_account` | `account` | Yes, full | Yes (`UserAdmin` only) | `UserModel`, email verification, login/logout/session, password reset, `UserAddressModel` |
| `app_address/` | `app_address` | `address` | **No** (admin-only) | Yes (Country/State/City) | Hierarchical reference data: `CountryModel` → `StateModel` → `CityModel` |
| `app_core/` | `app_core` | `core` | Yes, full | — (no concrete models) | Shared `BaseModel` (audit fields), contact form/API, health check, shared pagination/filter/throttle infra |
| `app_product/` | `app_product` | `product` | Yes, full | Yes | `ProductCategoryModel`, `ProductModel`, `ProductImageModel` |

There is **no shopping-cart app or model anywhere** in the backend —
see `domain.md` and `project_state.md`.

## `utils/`

Shared, reusable helpers with no Django app of their own: `normalize.py`
(whitespace/email normalization), `validator.py` (shared field validators),
`dispatch_task.py` (Celery dispatch that logs and swallows broker errors
instead of failing the HTTP request), `current_user.py` (thread-local user
used by `app_core.models.BaseModel.save()` to populate `created_by`/`updated_by`),
`env.py` (typed `.env` accessors), `image.py`, `upload.py`.

## Frontend (`frontend/`)

Independent Vite project; see `conventions.md` and `dependencies.md` for
stack details. Key subdirectories under `frontend/src/`:

| Directory | Responsibility |
|---|---|
| `admin-js/` | **Not** React/browser code — Node-side jsdom tests (`loadAdminScript.ts` harness + `*.test.ts`) that execute the real `static/src/js/admin/*.js` files Django serves, to cover the Admin's own vanilla JS. Has its own `tsconfig.admin-js.json` (Node types) excluded from `tsconfig.app.json`; needs `docker-compose.yml`'s `frontend` service's `./static:/repo-static:ro` mount to read those files. See `testing.md`. |
| `api/` | All backend I/O (`client.ts` fetch wrapper + `ApiError`, `auth.ts`, `products.ts`, `contact.ts`) |
| `auth/` | Small routing helpers for the auth flow (`?next=` redirect preservation) |
| `components/auth/`, `components/layout/`, `components/product/`, `components/ui/` | UI, grouped by concern |
| `config/` | `company.ts` — company contact info, overridable via undocumented `VITE_COMPANY_*` env vars (see `../memory/known_issues.md`) |
| `context/` | Plain React context: `AuthProvider` (session user), `CategoriesProvider` (category list) — no external state library |
| `hooks/` | `useAsync` (generic fetch-on-arg-change hook, used instead of a data-fetching library), `useApiForm` |
| `i18n/` | Custom i18n implementation — see `domain.md` for the pt-br/en/es/fr/it status split between frontend and backend |
| `pages/` | One component per route |

`frontend.old/` is a separate, legacy Django-template-based frontend.
Do not touch it.
