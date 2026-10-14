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
| `/api/account/password-reset/`, `/password-reset/validate/`, `/password-reset/confirm/` | password reset flow |
| `/api/product/products/`, `/api/product/products/{slug}/` | public product list/detail (`active=True` only) |
| `/api/product/categories/` | public category list (`active=True` only) |
| `/api/core/contact/` | contact form submission (throttled, dispatches an email via Celery) |
| `/api/core/health/` | health check (used by the Docker/Render healthcheck) |

`app_address` has **no API** — no `app_address/urls.py` exists and it is
not included in `PROJECT/urls.py`. Country/State/City are admin-managed
only.

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
  `permission_classes = [AllowAny]` at the viewset level. There is no
  object-level permission system in active use despite `django-guardian`
  being installed and backend-registered — see `../memory/known_issues.md`.
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
- No address API exists yet — `UserAddressModel` is admin-manageable
  (standalone + inline under `UserAdmin`, see `domain.md`) but has no
  DRF serializer/viewset. If asked to build one, the primary-address
  exclusivity rule already lives in `UserAddressModel.save()` — reuse it
  as-is rather than duplicating the check in a serializer.
