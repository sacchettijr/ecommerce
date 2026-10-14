# Project State

Verified as of this writing (git history: 9 commits total — this is a
young, actively-evolving prototype, not a mature codebase).

## Implemented and verified

- User registration, email verification, login/logout, password reset —
  full flow, specific error codes, rate-limited, anti-enumeration where
  it matters. See `domain.md`.
- Public product catalog: list (search/filter/sort/pagination), detail,
  categories — real API, real frontend pages wired to it.
- Product image management: ordering + single-primary-image invariants,
  enforced at both the model and DB-constraint level, with admin inline
  support. The project's best-executed feature architecturally.
- Address reference data (Country/State/City) — admin-manageable,
  hierarchical, `PROTECT`-on-delete.
- `UserAddressModel`: admin-manageable (standalone `UserAddressAdmin`
  plus an inline under `UserAdmin`), with "at most one primary address
  per user" enforced in `save()` (DB constraint as backstop) —
  mirrors `ProductImageModel`'s pattern. No public API yet.
- Local Docker Compose stack: Postgres, Redis, RabbitMQ, Celery worker,
  Django, Vite dev server, Nginx (reverse proxy), CloudBeaver, Certbot
  (profile-gated). Nginx currently serves HTTP (redirects to HTTPS) and
  HTTPS (self-signed certificate, pinned to one deployed IP).
- Render Blueprint (`render.yaml`) for a hosted public prototype — Django
  + Postgres + a static-site frontend whose `routes:` do Nginx's job;
  deliberately without Redis/RabbitMQ/Celery/CloudBeaver.
- Frontend i18n: 5 languages, genuinely translated (not stubs), with a
  working language switcher.
- Authenticated user area: `/profile` (route-guarded by
  `ProtectedRoute.tsx`) renders the real logged-in user's `name`/`email`/
  `date_birth`/`phone`/account-creation date, and `is_staff` only when
  `true` — via the extended `/api/account/session/` payload, inside the
  new reusable `AccountLayout` (sidebar + message/alert area). Other
  sidebar/dropdown destinations (edit profile, change password, orders,
  addresses, wishlist) remain inert placeholders — no pages exist for
  them yet.

## Partially implemented

- `django-guardian` is installed and backend-registered but has no actual
  per-object permission usage anywhere.
- Backend i18n: infrastructure (catalogs for all 5 languages) exists, but
  only 3 strings are actually marked for translation, and `LANGUAGES`
  itself only activates 3 of the 5 locales.
- Frontend type-checking/linting: hygiene flags are on, but neither full
  TypeScript `strict` mode nor type-checked ESLint rules are enabled,
  despite the frontend's own (otherwise unedited, stale) `README.md`
  suggesting they should be.

## Confirmed not implemented

- **Shopping cart / checkout / orders** — no model, API, or functional UI
  exists anywhere. UI copy/icons/dead buttons exist on the frontend only.
- **Address API** — no endpoint exists; addresses are currently only
  reachable by direct ORM/shell access (not even via Django admin, since
  there's no `UserAddressAdmin`).
- **Automated CI** — no GitHub Actions, no pre-commit hooks, no Makefile.
- **Frontend tests** — Vitest + React Testing Library installed
  2026-10-13 (see `testing.md`), but only the authenticated account area
  (`AccountLayout`/`ProfilePage`/`ProtectedRoute`, 14 tests) is covered;
  everything else in the frontend still has zero tests.
- **Route guarding** on the frontend — now exists (`ProtectedRoute.tsx`,
  used by `/profile`), but only one real account page exists behind it.

## Immediate priorities (if asked "what's next," ground the answer here)

1. Decide what to do about migrations not being committed to git (see
   `database.md`/`../memory/known_issues.md`) — this blocks a clean clone/CI from
   ever working.
2. Reconcile the two divergent superuser-bootstrap mechanisms (weak
   fallback vs. strict) before this is ever deployed somewhere the
   `post_migrate` signal's fallback could fire unnoticed.
3. Decide whether `app_address`/`UserAddressModel` get a real API + admin
   wiring, or whether the existing dead forms should be removed.
4. Fix the stale `backend/`-prefixed paths in `README.md` and
   `docs/render.md` (confirmed wrong — see `../memory/known_issues.md`).
5. Nothing beyond this list is a "confirmed plan" — see `roadmap.md` for
   the distinction between documented intent and open suggestions.
