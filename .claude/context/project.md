# Project Overview

A generic e-commerce application: Django REST Framework backend, React +
TypeScript frontend, Dockerized local development, with a Render-hosted
public prototype.

## Goals (verified against actual implementation)

| Goal | Status |
|---|---|
| Visitors browse the store and view products without authentication | **Implemented.** Product list/detail and category list are public (`AllowAny`), fully wired frontend-to-backend. |
| Require authentication before adding products to a cart | **Not applicable yet — there is no cart.** See `project_state.md`. |
| User registration, email verification, account activation | **Implemented.** Signup → Celery-dispatched verification email → `EmailVerificationViewSet.confirm`. See `domain.md`. |
| Clear, specific authentication errors based on account state | **Implemented.** Distinct `inactive` vs `email_not_verified` error codes. See `domain.md`. |
| Reusable architecture that can grow | Mostly followed (shared `BaseModel`, per-field form mixins, shared pagination/filter/throttle infra in `core/`), with a few unrelated dead forms still lingering — see `../memory/known_issues.md`. |
| Keep frontend, backend, infrastructure, and tooling organized | Mostly followed; a few stale docs (not code) describe a `backend/` subdirectory that was removed — see `../memory/known_issues.md`. |

## Technology stack (verified versions)

**Backend** (`requirements.txt`, `requirements-dev.txt`, `pyproject.toml`):
Python (targeting 3.14), Django 6.1.1, Django REST Framework 3.18.1,
PostgreSQL (via `psycopg2-binary`), Redis 8.1.0 client, Celery 5.6.3,
RabbitMQ (broker, via `celery`), Gunicorn 26.2.0, `django-filter` 26.1,
`django-guardian` 3.5.0 (installed, not actually used — see
`../memory/known_issues.md`), `drf-spectacular` 0.30.0, `django-phonenumber-field`
8.5.0, Pillow 12.3.0, `dj-database-url`, `whitenoise[brotli]`.

Dev tooling: `basedpyright`, `mypy` + `django-stubs`/`django-stubs-ext`/
`djangorestframework-stubs`, `ruff`, `pytest` + `pytest-django`,
`factory-boy` + `Faker`, `django-debug-toolbar`, `django-browser-reload`,
`djlint`.

**Frontend** (`frontend/package.json`): React 19.2.8, TypeScript ~6.0.2,
Vite 8.3.0, React Router 8.4.0 (unified `react-router` package, no
`react-router-dom`), Tailwind CSS 4.3.3 (CSS-first config, no
`tailwind.config.*` file), React Compiler (via `babel-plugin-react-compiler`
+ `@rolldown/plugin-babel`), ESLint 10. No state-management or
data-fetching library — see `conventions.md`.

**Infrastructure**: Docker, Docker Compose, Nginx (reverse proxy),
PostgreSQL, Redis, RabbitMQ, Celery worker, CloudBeaver (DB admin UI),
Certbot (Let's Encrypt, profile-gated — see `infrastructure` notes in
`database.md`/`security.md`), Render (hosted prototype).

## Scope clarification

This is a **prototype-stage** project, not a finished production store.
Confirmed from the actual implementation and git history (only 9 commits
total as of this writing):

- There is no shopping cart, checkout, or order model anywhere in the
  codebase (backend or frontend) — confirmed by repo-wide search.
- `address/` has no public API; Country/State/City are managed via Django
  admin only.
- `DEBUG=True` in both local and the current Render deployment, by explicit
  earlier project decision (not a bug) — production hardening
  (`SECURE_SSL_REDIRECT`, secure cookies) is deliberately deferred.
- `nginx/nginx.conf` is currently pinned to one deployed IP address with a
  real (self-signed, as of this writing — Let's Encrypt refuses bare-IP
  certificates) TLS certificate, not a portable template.

See `project_state.md` for a full implemented/partial/planned breakdown and
`roadmap.md` for documented next steps.
