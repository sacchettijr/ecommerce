# Project State

Verified as of this writing (git history: 9 commits total — this is a
young, actively-evolving prototype, not a mature codebase).

## Implemented and verified

- User registration, email verification, login/logout, password reset —
  full flow, specific error codes, rate-limited, anti-enumeration where
  it matters. See `domain.md`.
- Public product catalog: list (search/filter/sort/pagination), detail,
  categories — real API, real frontend pages wired to it. Default listing
  order is a daily-seeded deterministic shuffle (2026-10-16), not
  recency — see `domain.md`. Detail page breadcrumb truncates a long
  product name (full name preserved elsewhere) and the description is
  collapsible past a length threshold; prices display with USD
  formatting (`$1,234.56`) everywhere — presentation only, no currency
  conversion, no stored-value change.
- Product image management: ordering + single-primary-image invariants
  (now including auto-primary-on-first-image, added 2026-10-16),
  enforced at both the model and DB-constraint level, with admin inline
  support and dynamic JS for the primary checkbox/order auto-fill. The
  project's best-executed feature architecturally.
- Address reference data (Country/State/City) — admin-manageable,
  hierarchical, `PROTECT`-on-delete. The admin's address form now has a
  real country→state→city cascading filter (2026-10-16, backed by two
  new staff-only `app_address` endpoints) plus server-side cross-field
  validation — see `domain.md`.
- `UserAddressModel`: admin-manageable (standalone `UserAddressAdmin`
  plus an inline under `UserAdmin`), with the full primary-address
  invariant (at most one; a user's first address is always primary;
  deleting the primary promotes another) enforced at the model/signal
  level — mirrors `ProductImageModel`'s pattern, see `domain.md`. Has a
  **read-only** API now: `/api/account/addresses/` (list, own addresses
  only) and its `set-primary` action — still no create/update/delete
  endpoint.
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
  reusable `AccountLayout` (sidebar + message/alert area).
- `/profile/edit` (also route-guarded): self-service profile editing
  (`name`/`date_birth`/`phone`; `email` deliberately not editable — see
  `security.md`), backed by `/api/account/profile/`. On success,
  refreshes `AuthContext` via `setUser()` so the navbar/profile home
  reflect the change immediately, with no reload and no second current-user
  fetch.
- `/profile/password` (also route-guarded): self-service password change,
  backed by `/api/account/password-change/` (see `api.md`/`domain.md`).
  Rejects a new password identical to the current one (`password_unchanged`
  code) with a `warning`-styled notification, not a success.
- `/profile/addresses` (also route-guarded): lists the authenticated
  user's own addresses, each field shown only when non-blank, with a
  radio group to switch the primary address (immediate request on
  selection, no Save button — see `domain.md`/`architecture.md` for how
  rapid/overlapping selections and failures are reconciled against the
  backend's authoritative state). Add/Edit/Delete are rendered but
  intentionally inert (`aria-disabled`, no handlers, accessible tooltips)
  — no create/edit/delete workflow exists yet. Remaining sidebar/dropdown
  destinations (orders, wishlist) stay inert placeholders — no pages
  exist for them yet.
- `UserWishlistModel`/`UserWishlistItemModel` (2026-10-15): backend only —
  one wishlist per user (auto-created on signup via signal), unlimited
  items with no duplicate product per list (DB constraint + clear form
  error), gap-free `position` with insertion/reorganization/deletion all
  handled consistently, mirroring `ProductImageModel`'s established
  pattern. Admin-manageable (`UserWishlistAdmin` with an items inline,
  `UserWishlistItemAdmin`). No API endpoint and no frontend wiring yet —
  see `domain.md`.

## Partially implemented

- `django-guardian` is installed and backend-registered but has no actual
  per-object permission usage anywhere.
- Backend i18n: infrastructure (catalogs for all 5 languages) exists, but
  only 3 strings are actually marked for translation, and `LANGUAGES`
  itself only activates 3 of the 5 locales. `LANGUAGE_CODE` (backend) and
  the frontend's `DEFAULT_LANGUAGE` fallback are both `"en"` now
  (2026-10-16, were `"pt-br"`/inconsistently `"en-us"` in `.env`) — all 5
  languages and the switcher are otherwise unchanged.
- Frontend type-checking/linting: hygiene flags are on, but neither full
  TypeScript `strict` mode nor type-checked ESLint rules are enabled,
  despite the frontend's own (otherwise unedited, stale) `README.md`
  suggesting they should be.

## Confirmed not implemented

- **Shopping cart / checkout / orders** — no model, API, or functional UI
  exists anywhere. UI copy/icons/dead buttons exist on the frontend only.
- **Address create/edit/delete** — `/api/account/addresses/` only
  supports listing and switching the primary; there is still no
  endpoint or frontend workflow to create, edit, or delete an address
  (admin remains the only way).
- **Automated CI** — no GitHub Actions, no pre-commit hooks, no Makefile.
- **Frontend tests** — Vitest + React Testing Library installed
  2026-10-13 (see `testing.md`), but only the authenticated account area
  (`AccountLayout`/`ProfilePage`/`ProfileEditPage`/`ProtectedRoute`/
  `PasswordChangePage`/`AddressListPage`/`useMessages`) plus one
  standalone utility (`sanitizePhoneInput`), 59 tests total, is covered;
  everything else in the frontend (including `SignupPage.tsx`/`ContactPage.tsx`)
  still has zero tests.
- **Route guarding** on the frontend — now exists (`ProtectedRoute.tsx`),
  used by `/profile`, `/profile/edit`, `/profile/password`, and
  `/profile/addresses`.

## Immediate priorities (if asked "what's next," ground the answer here)

1. Decide what to do about migrations not being committed to git (see
   `database.md`/`../memory/known_issues.md`) — this blocks a clean clone/CI from
   ever working.
2. Reconcile the two divergent superuser-bootstrap mechanisms (weak
   fallback vs. strict) before this is ever deployed somewhere the
   `post_migrate` signal's fallback could fire unnoticed.
3. Decide whether `UserAddressModel` gets create/edit/delete API +
   frontend support (list + set-primary already exist, see `domain.md`),
   or whether admin remains the only way to add/remove an address.
4. Fix the stale `backend/`-prefixed paths in `README.md` and
   `docs/render.md` (confirmed wrong — see `../memory/known_issues.md`).
5. Decide whether the wishlist gets an API + frontend (model/admin layer
   is done, see `domain.md`) — same shape of decision as item 3 above.
5. Nothing beyond this list is a "confirmed plan" — see `roadmap.md` for
   the distinction between documented intent and open suggestions.
