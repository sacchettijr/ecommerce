# Security

## Authentication & authorization

- Session + CSRF cookie auth (not token-based). See `api.md`/`domain.md`
  for the login/verification flow and its specific, non-leaking error
  codes.
- Global DRF default is `IsAuthenticated`; public endpoints explicitly opt
  out with `AllowAny`. Verify this stays true for any new endpoint — the
  secure default is "authenticated," not "public."
- `django-guardian` is installed and registered in
  `AUTHENTICATION_BACKENDS`/`INSTALLED_APPS` but has **zero actual usage**
  (no `assign_perm`, no per-object permission checks anywhere). It does not
  currently provide any real protection — don't assume object-level
  permissions exist just because the package is present.
- Account enumeration is deliberately prevented on resend-verification and
  password-reset (identical response regardless of whether the account
  exists) — preserve this if you touch those flows.

## Secrets

- `.env` is gitignored and must **never** be read into chat, logs,
  commits, or documentation. `.env-example` holds placeholder values only
  and should stay that way.
- `render.yaml` has no inlined secrets: `SECRET_KEY` uses
  `generateValue: true`; `DATABASE_URL` uses `fromDatabase`; email/
  frontend-URL values use `sync: false` (set manually in the Render
  dashboard).
- `.env-example` is missing one real, currently-used variable:
  `INTERNAL_IP` (consumed by `PROJECT/settings/debug_toolbar.py` for
  Django Debug Toolbar's `INTERNAL_IPS`). Low-severity documentation gap,
  not a secret leak — see `../memory/known_issues.md`.

## Confirmed security-relevant issues

1. **Weak hard-coded fallback superuser.**
   `account/signals/create_default_superuser.py` creates a superuser with
   `admin@example.com` / `admin123` whenever no superuser exists and
   `DJANGO_SUPERUSER_*` env vars are unset, triggered automatically on
   every `post_migrate`. The separate `create_admin` management command
   does the equivalent job correctly (raises instead of a weak fallback).
   Running `migrate` without the env vars set, in **any** environment,
   silently creates a guessable admin account. Treat this as a real
   finding to raise with the user, not something to "work around" quietly.
2. **Database, Redis, RabbitMQ, and CloudBeaver ports are published to the
   host** in `docker-compose.yml` (5432, 6379, 5672+15672, 8978), unlike
   `backend`/`frontend` which are deliberately internal-only. This is
   presumably fine on an isolated local dev machine, but if this compose
   file is ever run on a non-isolated host (e.g. the same VPS whose public
   IP is hard-coded into `nginx/nginx.conf`), those four services become
   reachable from the public internet with no reverse-proxy/firewall layer
   in front of them. Flag this before any non-local deployment using this
   compose file as-is.
3. **Django migrations are not committed to version control** (see
   `database.md`) — not a runtime vulnerability, but a real operational
   risk: a fresh clone/CI run cannot build a working database at all.
4. **`nginx/nginx.conf` currently serves HTTPS with a self-signed
   certificate**, not a real Let's Encrypt certificate — Let's Encrypt
   refuses to issue certificates for a bare IP address (confirmed by
   running `certbot` against the real ACME endpoint, not assumed), and the
   server is identified by IP (`177.222.210.50`), not a domain name.
   Browsers will show a trust warning. This was a deliberate interim
   choice (see `roadmap.md`) — getting a real certificate requires a real
   domain name pointed at that IP first.
5. **`SECURE_SSL_REDIRECT`/`SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE`
   are only enabled when `DEBUG=False`**, and `DEBUG=True` is currently
   set in both local dev and the Render deployment, by explicit earlier
   project decision for this prototype phase. This is intentional, not an
   oversight — but it means none of those three protections are active
   anywhere right now. Don't "fix" this unilaterally by flipping `DEBUG`;
   that's a decision for the user to make when the project leaves the
   prototype phase. `SECURE_PROXY_SSL_HEADER`, by contrast, is always on
   (not gated by `DEBUG`) because it only affects how Django infers the
   original scheme behind Nginx, not an enforcement mechanism.

## Uploads

Product images/thumbnails go through `Pillow`-backed `ImageField`s. Check
`utils/validator.py` and `utils/upload.py` for existing file-type/size
validation and upload-path generation before adding a new upload field —
reuse these rather than writing new validation from scratch.

## Before weakening anything

Per root project instructions: do not weaken CSRF/CORS/session/cookie/
HTTPS protections, or disable a security check, to make a tool or test
pass, without an explicit, justified decision — and say so explicitly if
you do.
