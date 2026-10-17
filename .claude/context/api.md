# API

All endpoints are mounted under `/api/` by `PROJECT/urls.py`. DRF
`DefaultRouter` is used per app; `drf-spectacular` is wired and serves
live schema/docs (not just installed — confirmed: `SpectacularAPIView`/
`SpectacularSwaggerView`/`SpectacularRedocView` are registered).

| Path | Purpose |
|---|---|
| `/api/schema/`, `/api/schema/swagger/`, `/api/schema/redoc/` | OpenAPI schema and interactive docs (drf-spectacular) |
| `/api/account/session/` | current session user (`id`, `name`, `email`, `date_birth`, `phone`, `created_at`, `is_staff`) + forces the CSRF cookie to be set |
| `/api/account/login/`, `/api/account/logout/` | session login/logout |
| `/api/account/signup/` | registration |
| `/api/account/email-verification/confirm/`, `/api/account/email-verification/resend/` | email verification flow |
| `/api/account/password-reset/`, `/password-reset/validate/`, `/password-reset/confirm/` | password reset flow (unauthenticated, via emailed link) |
| `/api/account/password-change/` | self-service password change for the authenticated session's own user (`IsAuthenticated`, no user id accepted — see `domain.md`); rejects a new password identical to the current one with `{"code": "password_unchanged"}` |
| `/api/account/profile/` | self-service profile update (`name`/`date_birth`/`phone` only — `email` is not editable) for the authenticated session's own user (`IsAuthenticated`, no user id accepted — see `domain.md`); returns `{"user": {...}}`, same shape as login/signup |
| `/api/account/addresses/` | list the authenticated session's own addresses (`IsAuthenticated`, no user/address id from the client can surface another user's data — see `domain.md`); plain JSON array, not paginated; primary first |
| `/api/account/addresses/{id}/set-primary/` | POST, makes that address primary and unsets the user's other addresses atomically; 404 (not 403) if `{id}` doesn't belong to the requester, so it can't be used to probe whether an id exists; returns the user's full, fresh address list |
| `/api/account/wishlist/` | GET lists the authenticated session's own wishlist items (public **and** private, `IsAuthenticated`); POST `{"product": <id>}` adds a product (400 if already present or inactive); not paginated. Added 2026-10-16 |
| `/api/account/wishlist/{id}/` | DELETE removes that item; 404 (not 403) if it doesn't belong to the requester; returns the user's full, fresh item list |
| `/api/account/wishlist/{id}/toggle-privacy/` | POST, flips that item's `private` flag; returns the full list |
| `/api/account/wishlist/{id}/move/` | POST `{"direction": "up"\|"down"}`, swaps the item's position with its adjacent sibling (a no-op at either end of the list); returns the full list |
| `/api/account/wishlist/check/?product=<id>` | GET, `{"in_wishlist": bool, "item_id": int\|null}` for the authenticated session's own wishlist — backs the product-page button's initial state |
| `/api/account/wishlist/share-link/` | GET, `{"public_id": "<uuid>"}` — the authenticated session's own wishlist's public identifier |
| `/api/account/wishlist/public/{public_id}/` | GET, `AllowAny` — a third party's wishlist by its opaque `public_id` (see `domain.md`); returns only `private=False` items, and the item shape has no `private` key at all |
| `/api/product/products/`, `/api/product/products/{slug}/` | public product list/detail (`active=True` only); default order is a daily-seeded deterministic shuffle, not recency — see `domain.md`'s "Catalog ordering and randomization" |
| `/api/product/categories/` | public category list (`active=True` only) |
| `/api/core/contact/` | contact form submission (throttled, dispatches an email via Celery) |
| `/api/core/health/` | health check (used by the Docker/Render healthcheck) |
| `/api/address/states/?country=<id>` | states for a country (`IsAdminUser`, no pagination — plain array) — backs the Django Admin's country→state cascade only, added 2026-10-16 |
| `/api/address/cities/?state=<id>` | cities for a state (`IsAdminUser`, no pagination) — backs the admin's state→city cascade only, added 2026-10-16 |

`app_address` now has its own routes (`app_address/urls.py`, added
2026-10-16) — the two read-only, staff-only endpoints above. Country/State/City
are still otherwise admin-managed only; they also remain reachable as small
read-only nested objects inside `/api/account/addresses/`'s response
(see `domain.md`).

## Conventions actually in use

- **Auth**: Django session + CSRF cookie, not token auth. The frontend
  always sends `credentials: "include"`; non-GET requests attach
  `X-CSRFToken` read from the `csrftoken` cookie (fetching
  `/api/account/session/` first if the cookie isn't set yet, since that's
  the one endpoint guaranteed to set it). See `security.md`.
- **Pagination**: `app_core.api.pagination.StandardPagination` — adds
  `count`/`total_pages`/`current_page`/`next`/`previous`/`results`.
- **Ordering**: `app_core.api.filters.StableOrderingFilter` adds a `pk`
  tie-breaker to any ordering so paginated results don't reshuffle between
  pages.
- **Filtering**: `django-filter`'s `DjangoFilterBackend` (e.g.
  `ProductFilterSet` filters by `category__slug`) plus DRF's `SearchFilter`
  where applicable.
- **Permissions**: global default is `IsAuthenticated`
  (`PROJECT/settings/rest_framework.py`); public endpoints (product/category
  list/detail, contact, session, signup, login) explicitly set
  `permission_classes = [AllowAny]` at the viewset level. `IsAdminUser`
  (DRF's built-in staff-only permission) is now used too, for the two new
  `app_address` geo endpoints that exist solely to back a Django Admin
  widget — the first precedent for a staff-gated DRF endpoint in this
  project. There is no object-level permission system in active use
  despite `django-guardian` being installed and backend-registered — see
  `../memory/known_issues.md`.
- **Throttling**: per-scope `ScopedRateThrottle`, rates centralized in
  `PROJECT/settings/rest_framework.py` (`DEFAULT_THROTTLE_RATES`), applied
  per-viewset via `throttle_scope`. See `domain.md` for the actual rates.
- **Error responses**: form/serializer validation errors use DRF's default
  shape. The account app additionally uses stable `code` values (e.g.
  `"invalid_link"`, `"inactive"`, `"email_not_verified"`) so the frontend
  can branch on a specific reason rather than parsing message text — follow
  this pattern for new account-related errors rather than inventing a new
  error shape.
- **Dispatch-and-forget emails**: Celery dispatch failures (e.g. broker
  unreachable) are logged and swallowed by `utils/dispatch_task.py` — the
  HTTP response still reports success. This is intentional (see
  `PROJECT/settings/celery.py` comments), not a bug to "fix" by letting the
  exception propagate, but be aware of it when debugging "the email never
  arrived" reports — check Celery/RabbitMQ health, not just the API
  response.

## Known gaps

- `core/forms/ContactForm.py` exists but is unused; `ContactSerializer`
  duplicates its validation independently. If you touch contact-form
  validation, check both files or consolidate them (see `../memory/known_issues.md`).
- No cart/checkout/order endpoints exist (see `domain.md`).
- The address API only supports **reading the list and switching which
  one is primary** — there is still no create/update/delete endpoint for
  addresses (admin is still the only way to add or remove one). If asked
  to build those, the primary-address invariant (at-most-one, first-is-primary,
  promote-on-delete) already lives entirely in `UserAddressModel.save()`
  and `app_account/signals/promote_primary_address_after_delete.py` —
  reuse them as-is rather than duplicating the rules in a new
  serializer/viewset.
