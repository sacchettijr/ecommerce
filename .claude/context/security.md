# Security

## Authentication & authorization

- Session + CSRF cookie auth (not token-based). See `api.md`/`domain.md`
  for the login/verification flow and its specific, non-leaking error
  codes.
- Global DRF default is `IsAuthenticated`; public endpoints explicitly opt
  out with `AllowAny`. Verify this stays true for any new endpoint — the
  secure default is "authenticated," not "public." `PublicWishlistViewSet`
  (added 2026-10-16, `/api/account/wishlist/public/{public_id}/`) is the
  first `AllowAny` endpoint under `app_account` that serves one user's
  data to an arbitrary, possibly-unauthenticated visitor — it's safe only
  because the data it serves is deliberately scoped (public items only,
  looked up by an unguessable id) rather than because the endpoint itself
  is "read-only."
- A third tier, `IsAdminUser` (DRF's built-in staff-only permission), is
  now in use too — `app_address/api/viewsets/{StateListViewSet,
  CityListViewSet}.py`, added 2026-10-16 to back the Django Admin's own
  country→state→city cascading dropdowns (`/api/address/states/`,
  `/api/address/cities/`). Not public, not just "any authenticated
  user" — staff only, since these exist solely for an admin-only UI
  with no other caller. First precedent for this tier in the project;
  use it (not `IsAuthenticated`) for any future endpoint that only an
  admin page should ever call.
- `django-guardian` is installed and registered in
  `AUTHENTICATION_BACKENDS`/`INSTALLED_APPS` but has **zero actual usage**
  (no `assign_perm`, no per-object permission checks anywhere). It does not
  currently provide any real protection — don't assume object-level
  permissions exist just because the package is present.
- Account enumeration is deliberately prevented on resend-verification and
  password-reset (identical response regardless of whether the account
  exists) — preserve this if you touch those flows.
- **A new password must differ from the current one**, enforced
  server-side (`PasswordChangeForm.clean()`, see `domain.md`) via
  `user.check_password()` against the stored hash — never a raw string
  comparison — so this can't be bypassed by a client that skips the
  frontend's own warning. The frontend cannot weaken this: it only
  decides how the resulting `password_unchanged` code is displayed, not
  whether the change is allowed.
- **No endpoint that returns or mutates personal account data accepts a
  client-supplied user identifier.** `/api/account/session/`,
  `/api/account/password-change/`, `/api/account/profile/`,
  `/api/account/addresses/` (list + `set-primary`), and
  `/api/account/wishlist/...` (list/add/remove/toggle-privacy/move/check/
  share-link) all resolve the target user/wishlist exclusively from
  `request.user` (the authenticated session) — confirmed by reading every
  viewset and by tests that deliberately try to smuggle another user's
  id/email, or another user's address/wishlist-item id, into the request
  and assert it has no effect. If a future endpoint needs to look up a
  user, keep following this pattern (resolve from the session, never
  from a request parameter) rather than trusting an id and checking it
  against `request.user` afterward.
- **`UserAddressViewSet.set_primary` and every owner-scoped
  `WishlistItemViewSet` action (`destroy`/`toggle-privacy`/`move`) 404,
  not 403, on another user's address/item id.** `get_object()` is called
  against a queryset already filtered to `request.user`'s own rows, so an
  id belonging to someone else looks identical to an id that doesn't
  exist at all — an attacker can't use the response to tell "exists but
  isn't yours" apart from "doesn't exist," consistent with this project's
  anti-enumeration posture elsewhere (resend-verification, password-reset).
- **Wishlist item privacy is enforced at the queryset layer, before
  serialization, not by a serializer field filter alone.**
  `PublicWishlistViewSet`/`PublicWishlistSerializer` explicitly filter to
  `private=False` when building the list handed to
  `PublicWishlistItemSerializer`, and that serializer's `Meta.fields` has
  no `private` key at all — there is no field left to leak even if the
  queryset filter were ever accidentally removed. Confirmed by a test
  that asserts the word `"private"` never appears as a key anywhere in
  the public endpoint's response. The public wishlist lookup itself uses
  an unguessable opaque `public_id` (UUID), not the sequential numeric
  user id, specifically so a visitor can't enumerate accounts by
  incrementing an id in the URL — see `domain.md`.
- **Protected/administrative fields can't be set through the profile-edit
  endpoint**, not because of explicit filtering code but because
  `UserUpdateForm.Meta.fields` only lists `name`/`date_birth`/`phone` —
  Django's `ModelForm` simply never reads any other submitted key
  (`is_staff`, `is_superuser`, `is_active`, `email`, ...). Confirmed by a
  test that submits all of those alongside a valid update and asserts
  none of them changed. If a field is ever added to that form, re-check
  this guarantee still holds for it.
- **`email` is intentionally not editable via `/api/account/profile/`.**
  It's the `USERNAME_FIELD` and its verification status
  (`is_email_verified`) is tied to the specific address a token was sent
  to; allowing a silent email change here would let a user "verify" an
  address without ever proving they own it. Adding email-change support
  would need its own re-verification flow (like signup's), not a one-line
  addition to this form.

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
   `app_account/signals/create_default_superuser.py` creates a superuser with
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
