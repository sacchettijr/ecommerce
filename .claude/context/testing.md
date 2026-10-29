# Testing

## Backend

Function-based pytest (`pytest` + `pytest-django`), `pytestmark =
pytest.mark.django_db` at module level, `factory-boy` + `Faker` for test
data. **As of 2026-10-28, every app's `tests/` package uses the richer
subdirectory set the project standardized on**:
`{api,admin,models,views,factories}/` everywhere, plus
`{middleware,signals,backends}/` on `app_account` and `signals/` on
`app_checkout` (only where that app actually has one), and a shared
`utils/` subdirectory under `app_core/tests/` for every utility module in
`utils/` regardless of which app happens to exercise it first (continuing
the pre-existing convention of `test_rate_limit.py`/`test_validators.py`,
just relocated out of the `tests/` root into `tests/utils/`). A handful of
genuinely cross-cutting checks stay at an app's `tests/` root by design,
not oversight: `app_account/tests/test_migrations.py` (a project-wide
migration-graph check, not owned by any one layer).
`app_core/tests/i18n/` is new — the project's first dedicated
internationalization/translation tests (see "Internationalization
testing" below). No app has a standalone `test.py`/`tests.py` file
outside a `tests/` package, and none ever did (re-confirmed 2026-10-28).

**Baseline before the 2026-10-28 test audit**: 320 passed, 0 failed, 231
warnings, ~9 min runtime, no `conftest.py` anywhere, no coverage tooling
installed (`pytest-cov`/`coverage` are not in either requirements file,
and no `[tool.coverage.*]`/`.coveragerc` exists). **After**: 441 passed, 0
failed, 268 warnings, ~8 min runtime — same zero-conftest/zero-coverage-
tooling facts still hold; the audit only added tests, it didn't change
the test-running infrastructure itself.

### Coverage by app (verified, not estimated)

| App | Coverage |
|---|---|
| `app_account/` (label `account`) | Well covered: login/logout/session/signup/email-verification/password-reset/password-change (including the unchanged-password rejection)/profile-update flows, `is_staff` admin gate, `safe_next_path`, `frontend_scheme_and_domain` (`tests/api/test_auth_api.py`, `tests/utils/test_frontend_url.py`); `UserAddressModel`'s primary-address invariant and the `/api/account/addresses/` endpoints (`tests/models/test_user_address_rules.py`, `tests/api/test_user_address_api.py`); the address admin's field order (`tests/admin/test_user_address_admin.py`); `UserWishlistModel`/`UserWishlistItemModel` and the full `/api/account/wishlist/...` surface, including the public endpoint (`tests/models/test_user_wishlist_rules.py`, `test_user_wishlist_item_rules.py`, `tests/api/test_wishlist_item_api.py`, `test_public_wishlist_api.py`); the migration graph (`tests/test_migrations.py`). **Added 2026-10-28**: `CurrentUserMiddleware`/`BaseModel`'s `created_by`/`updated_by` stamping — previously zero coverage anywhere, direct or incidental (`tests/middleware/test_current_user_middleware.py`); `app_account/signals/create_default_superuser.py` — the weak-fallback-credentials path, the `DJANGO_SUPERUSER_*`-env-var path, the already-exists no-op, idempotency (`tests/signals/test_create_default_superuser.py`); `UserManagerModel.create_user`/`create_superuser`'s `ValueError` guard branches, `UserModel.get_full_name`/`get_short_name`/`__str__`/`user_email_confirmation`/the name-and-email normalization on save (`tests/models/test_user_manager.py`, `test_user_model.py`); `EmailVerifiedModelBackend`'s `isinstance` guard and active/verified branches, previously only exercised indirectly via login (`tests/backends/test_email_verified_backend.py`). **Still not covered**: `app_account/management/commands/create_admin.py`/`seed_users.py`, the wishlist admin classes and `UserWishlistBaseForm`/`Create`/`UpdateForm`, `UserAdminChangeForm`/`UserAdminCreationForm`, the email tasks' retry branch. |
| `app_address/` (label `address`) | **Substantially expanded 2026-10-28** (previously only `tests/api/test_geo_filters.py`, added 2026-10-16): added `tests/models/test_protect_delete.py` — every `on_delete=models.PROTECT` edge in the Country→State→City hierarchy and in `UserAddressModel`'s direct city/state/country FKs, confirmed via `ProtectedError`; also **documents a genuine, confirmed finding**: none of `CountryModel`/`StateModel`/`CityModel` has any uniqueness constraint (no `unique_together`, no `UniqueConstraint`, no field-level `unique=True`) on name/code within their parent — two tests pin down today's actual (unconstrained) behavior as a regression guard, not as an endorsement; this is flagged for the user, not fixed, since adding a constraint is a production-behavior change outside a testing task's scope. Extended `tests/api/test_geo_filters.py` with the `CityListViewSet` non-staff-rejection case (parity with `StateListViewSet`, which already had it) and the non-integer-query-param → empty-list branch for both endpoints. Added `tests/admin/test_geo_admin.py` (Country/State/City admin config) and `tests/forms/test_geo_forms.py` (the shared `NormalizedAddressNameFieldMixin`'s <3-character rejection, `StateForm`'s `validate_alpha` code field). **Still not covered**: `CityLocationSelect`/`StateLocationSelect` widgets (the frontend-cascading-dropdown data attributes). |
| `app_checkout/` (label `checkout`) | Added 2026-10-24 alongside the cart feature: `CartItemManagerModel` and the full `/api/checkout/items/` surface (`tests/models/test_cart_item_manager.py`, `tests/api/test_cart_api.py`). **Added 2026-10-28**: `CartItemAdmin`'s list/search/filter config and add/change form split (`tests/admin/test_cart_item_admin.py`); an isolated, direct signal-level test of `remove_product_from_carts_when_deactivated` — deactivate removes, re-activate/no-op leaves alone, re-saving an already-inactive product doesn't error, scoped to only that product's rows across every cart (`tests/signals/test_remove_product_from_carts_when_deactivated.py`) — previously this signal was only exercised indirectly through the API test file. **Still not covered**: the two legacy, unreachable template views (`CartItemCreateView`/`CartItemTemplateView` — confirmed still dead code), `CartItemBaseForm`/`CartItemCreateForm`/`CartItemUpdateForm` (empty passthrough forms, low risk). |
| `app_core/` (label `core`) | Added 2026-10-17: the `/api/core/contact/` surface and `utils/rate_limit.py` (`tests/api/test_contact_api.py`, `tests/utils/test_rate_limit.py`). **Added 2026-10-28**: the remaining 7 of 8 functions in `utils/validator.py` that had zero coverage (`validate_positive_decimal`, `validate_non_negative_decimal`, `validate_min_length`, `validate_max_length`, `validate_alpha`, `validate_image_max_size`, `validate_image_dimensions`, `validate_image_extension` — only `validate_name` had a dedicated test before; extended `tests/utils/test_validators.py` in place); the health-check view (`tests/views/test_api_health_check.py` — previously zero test hit `/api/core/health/` at all); four previously-zero-coverage shared `utils/` modules that don't belong to any one app — `utils/slug.py`'s `generate_slug`/`generate_unique_slug` (used by every `ProductBaseModel.save()`, never tested before), `utils/normalize.py`, `utils/dispatch_task.py` (the documented, intentional swallow-and-log pattern — now has a direct test confirming it actually swallows and logs rather than propagating), `utils/current_user.py` (all in `tests/utils/`); and the project's first dedicated i18n test suite, `tests/i18n/test_translation.py` (see below). **Still not covered**: `BaseModel`'s own fields in isolation (its stamping behavior is tested from `app_account`'s middleware test, since `BaseModel` itself has no concrete subclass to instantiate directly), `ContactForm` (confirmed still dead/unused), `StableOrderingFilter`, `StandardPagination`, `utils/email.py`, `utils/image.py`. |
| `app_product/` (label `product`) | Concentrated on image ordering/upload paths plus admin field order and randomized ordering (`tests/models/test_product_image_rules.py`, `test_upload_paths.py`, `tests/admin/test_product_admin.py`, `tests/api/test_product_randomized_ordering.py`). **Added 2026-10-28**: `tests/api/test_product_visibility.py` — the business-critical "browse without authentication" goal end-to-end (anonymous list/detail/category access all `200`), and the inactive-product exclusion rule for both the list and detail viewsets, confirmed uniform for anonymous *and* staff alike (no staff carve-out exists here, unlike the wishlist) — previously untested despite being core to the project's stated goals. **Still not covered**: `ProductForm`/`ProductCategoryForm`/`ProductImageForm` and their 5 `Normalized*FieldMixin`s' validation branches, `ProductCategoryAdmin`/`ProductImageAdmin`/`ProductImageInlineAdmin`, `ProductFilterSet` beyond the category-slug filter already covered, `seed_products` management command. |

No app has any `tests/views/*.py` content beyond the new
`app_core/tests/views/test_api_health_check.py` — every other
`views/__init__.py` across every app is still empty (consistent with no
other app having a reachable Django view outside its DRF viewsets).

### Internationalization testing (new 2026-10-28)

The backend had **zero** i18n-specific tests before this date — no test
anywhere activated a non-default language, overrode translation context,
read `get_language()`, or sent an `Accept-Language` header to assert a
localized response (confirmed by a repo-wide grep across every `tests/`
tree). `app_core/tests/i18n/test_translation.py` closes this:
- A settings-level regression guard pinning `LANGUAGES` to exactly the 5
  required locales (`pt-br`, `en`, `es`, `fr`, `it`) — guards against the
  2026-10-18 regression recurring (see `known_issues.md`).
- Direct `translation.override(...)` + `gettext(...)` checks for one real,
  already-catalogued string (`LoginForm`'s "This account has been
  deactivated.") across en/pt-br/fr/it, plus a `utils/validator.py`
  message under `pt-br`.
- Full-stack: a real `Accept-Language` header through `LocaleMiddleware`
  into a real `/api/account/login/` 400 response, confirmed for en and
  pt-br with the same `code` but different message text; an explicit
  regression test that `fr` no longer falls back to English (the exact
  bug fixed 2026-10-18); an unsupported language (`de`) falling back to
  the default (`en`) rather than erroring.
Still true: the gettext catalogs remain very sparse (7 real custom
strings per locale) — these tests exercise the handful that exist and the
activation mechanism itself; they don't (and can't) cover strings that
have no catalog entry yet.

### Factories

`app_account.tests.factories.{UserFactory,UserAddressFactory,UserWishlistFactory,UserWishlistItemFactory}`,
`app_address.tests.factories.{CountryFactory,StateFactory,CityFactory}`,
`app_checkout.tests.factories.CartItemFactory`,
`app_product.tests.factories.{ProductCategoryFactory,ProductFactory,ProductImageFactory}`.
`UserWishlistFactory` uses `django_get_or_create = ("user",)` — every user
already gets a wishlist via `create_wishlist_for_new_user` (see
`domain.md`), so a plain `create()` would collide with the `OneToOneField`.
No factories exist for `app_core` — consistent with it having zero tests.
**Import gotcha**: `app_address`'s three factories depend on each other
(`City → State → Country`) in an order that isn't alphabetical, so each
one imports its dependency directly from the sibling *module*
(`from app_address.tests.factories.CountryFactory import CountryFactory`),
never from the *package* (`from app_address.tests.factories import
CountryFactory`) — importing through the package's own `__init__.py`
while that same `__init__.py` is still mid-import raises `ImportError`
for a partially-initialized module. `app_account.tests.factories.UserAddressFactory`
has the same issue against `UserFactory` and uses the same fix. This
also keeps `ruff`'s alphabetical-import-sort check satisfied in each
`__init__.py` without fighting the real dependency order.
`UserAddressFactory.state`/`.country` are derived from the chosen `city`
via `LazyAttribute` (fixed 2026-10-16, were three independent
`SubFactory`s before) — a factory-created address must satisfy
`UserAddressBaseForm.clean()`'s country/state/city consistency check the
same way a real one would, so tests building a formset from one (e.g.
`row_from()` in `test_user_address_rules.py`) don't hit spurious
validation errors.

### Configuration

`pyproject.toml`'s `[tool.pytest.ini_options]` is minimal:
`DJANGO_SETTINGS_MODULE = "PROJECT.settings"`, `python_files = ["test_*.py"]`.
No markers, no `addopts`, no coverage reporting configured. No skipped or
`xfail` tests exist anywhere; no TODO/FIXME comments found in any `.py`
file (both confirmed by grep, not estimated).

### Running tests

```bash
docker exec ecommerce_django python -m pytest
docker exec ecommerce_django python -m pytest path/to/test_file.py -q
docker exec ecommerce_django python manage.py check
docker exec ecommerce_django python manage.py makemigrations --check --dry-run
```

Or, on the host, using `venv-ecommerce` (do not read/modify files inside
that directory, just invoke its interpreter):
```bash
./venv-ecommerce/Scripts/python -m pytest
```

## Frontend

**Vitest + React Testing Library**, installed 2026-10-13 (confirmed in
`frontend/package.json`'s devDependencies: `vitest`, `jsdom`,
`@testing-library/react`, `@testing-library/jest-dom`,
`@testing-library/user-event`). Config lives in `vite.config.ts`'s `test`
block (`environment: "jsdom"`, `setupFiles: ["./src/setupTests.ts"]`).
`src/setupTests.ts` imports `@testing-library/jest-dom/vitest` (DOM
matchers) and registers `afterEach(cleanup)` explicitly — `test.globals`
is **not** enabled, so every test file imports `describe`/`it`/`expect`/
etc. from `"vitest"` itself rather than relying on globals; keep doing
that for new test files rather than turning `globals` on.

- **Coverage so far**: the authenticated account area —
  `src/components/account/AccountLayout.test.tsx`,
  `src/pages/ProfilePage.test.tsx`, `src/pages/ProfileEditPage.test.tsx`,
  `src/pages/PasswordChangePage.test.tsx`, `src/pages/AddressListPage.test.tsx`,
  `src/auth/ProtectedRoute.test.tsx`, `src/hooks/useMessages.test.ts`
  (59 tests total at the time). Added 2026-10-16: the public product pages' new pieces —
  `src/components/product/ProductBreadcrumb.test.tsx`,
  `ExpandableDescription.test.tsx`, `formatPrice.test.ts`,
  `productSort.test.ts`, `src/pages/ProductListPage.test.tsx` (ordering
  query-building only), and `src/i18n/detectInitialLanguage.test.ts`
  (82 tests total). Added 2026-10-16 (wishlist feature):
  `src/pages/WishlistPage.test.tsx` (own list rendering, move/remove/
  toggle-privacy interactions, the inert "Add to cart" button, copying
  the share link), `src/pages/PublicWishlistPage.test.tsx` (404 for an
  unknown id, empty state, no edit/delete/privacy controls, inert gift
  button), `src/pages/ProductDetailPage.test.tsx` (the wishlist toggle
  button's initial state, add/remove, guest-sees-a-login-link, a failed
  request not producing a false visual state, and the button staying
  disabled until the initial `check` call resolves — this is also the
  project's first test of `ProductDetailPage.tsx` as a whole, previously
  untested), and `src/components/layout/UserMenu.test.tsx` (new file —
  `UserMenu.tsx` had no tests at all before; covers the wishlist/addresses
  navigation and orders staying inert) (117 tests total). Added 2026-10-17
  (phone input + contact rate-limit countdown feature): the now-deleted
  `sanitizePhoneInput.ts`/its test were superseded by
  `src/components/ui/PhoneInput.test.tsx` (country switch preserving
  digits, digit-only extraction, per-country mask, E.164 normalization
  for both a BR and a non-BR number, re-syncing from an externally-changed
  `value` prop); `src/pages/SignupPage.test.tsx` (new — that page had no
  tests at all before: the country selector renders, a normalized E.164
  phone is submitted, other fields survive a server-side field error);
  `src/pages/ContactPage.test.tsx` (new — same page's first tests ever:
  the phone field, the library-based client-side validity check replacing
  the old ad-hoc digit-count one, the 429-driven countdown ticking down
  and re-enabling the submit button via `vi.useFakeTimers()`, and the
  countdown resuming correctly from `localStorage` after a simulated
  reload); `ProfileEditPage.test.tsx` updated in place (the masked
  display value, normalized submitted payload) rather than extended (130
  tests total at the time). Several further small fixes between
  2026-10-17 and 2026-10-24 (not individually itemized here) brought the
  count to 155 before the cart feature below. Added 2026-10-24 (shopping
  cart feature): `src/pages/CartPage.test.tsx` (new — loading/error states,
  empty state with the products link, item rendering, quantity +/-
  calling the API and reflecting the fresh summary, remove + success
  message, the coupon field/button confirmed to do nothing); extended
  `src/components/product/ProductCard.test.tsx` and
  `src/pages/ProductDetailPage.test.tsx` for the add-to-cart flow
  (logged-in adds + navigates to `/cart`, logged-out redirects to
  `/login?next=/product/<slug>?addToCart=1`, the resume effect firing
  exactly once and stripping the query flag, an inactive-product error
  not navigating); new `src/components/layout/Navbar.test.tsx` (the cart
  link's live item count from `CartContext`); extended
  `src/pages/WishlistPage.test.tsx`/`PublicWishlistPage.test.tsx` for the
  new inactive-product red label (shown only when the fixture's
  `product.active` is `false`, matching the backend's staff-only
  visibility rule) (177 tests total now). Nothing else in the frontend
  has tests yet, and no
  test touches `HomePage.tsx` as a whole, only its extracted pieces — this
  is still a start, not full coverage; don't assume other components/pages
  are tested.
- **Testing a page whose component calls `useParams()`**
  (`ProductDetailPage.tsx`, `PublicWishlistPage.tsx`):
  `renderWithProviders` (`src/test/renderWithProviders.tsx`) takes an
  optional `path` option (e.g. `path: "wishlist/:publicId"`) alongside
  `route` — without it, `ui` renders directly inside the `MemoryRouter`
  with no `<Route>` match, so `useParams()` always returns `{}` regardless
  of `route`. Added 2026-10-16 when the first test for a param-based page
  was written; reuse `path` for any future page under `App.tsx` that reads
  a route param, rather than re-deriving this.
- **Django Admin static JS (new 2026-10-16)**: `static/src/js/admin/*.js`
  (served by Django, no build step of its own) now has real automated
  coverage too, not just manual-step documentation — `src/admin-js/`
  (`cityLocationSelect.test.ts`, `userAddressInline.test.ts`,
  `productImageInline.test.ts`, 14 tests), using the shared harness
  `src/admin-js/loadAdminScript.ts`. That harness `fs.readFileSync`s the
  actual shipped source and `window.eval`s it inside a `JSDOM` instance
  built with `runScripts: "dangerously"` (needed for `document` to
  resolve as a bare global the way a real `<script>` tag sees it) and
  markup matching what Django actually renders, then dispatches real
  `change`/`formset:added` events — this exercises the exact code that
  ships, not a reimplementation of its logic. **Infrastructure
  prerequisite**: the frontend container only mounts `./frontend:/app`
  by default, and these static files live in the repo root's `static/`
  — `docker-compose.yml`'s `frontend` service now also mounts
  `./static:/repo-static:ro` so `npm run test`/`vitest` can read them
  from inside the normal running container. `tsconfig.admin-js.json` is
  a separate project reference (mirrors the existing `tsconfig.node.json`
  split) giving just `src/admin-js/**` Node types (`fs`/`path`/
  `import.meta.dirname`) without exposing them to the rest of `src/`,
  which stays browser-only. `@types/jsdom` was added as a devDependency
  (type-only, no runtime addition) since `jsdom` itself doesn't ship its
  own types. Reuse this pattern for any *future* admin JS — don't fall
  back to manual-only verification when it's avoidable.
- **Testing a race between overlapping requests**: `AddressListPage.test.tsx`'s
  "ignores a stale response once a newer selection has started" test is
  the reference for this — mock the API function with
  `.mockImplementationOnce()` chained per call, each returning a promise
  whose `resolve` is captured into an outer variable, trigger both
  actions, then resolve them out of order and assert only the *logically
  newer* one's result survives. Don't rely on timers/delays to simulate
  "slow" responses; controlling the promise resolution directly is
  deterministic.
- **Two `render()` calls in the same `it()` block will collide.**
  `renderWithProviders`'s automatic cleanup (`afterEach(cleanup)` in
  `setupTests.ts`) only runs *between* tests, not between two `render()`
  calls inside the *same* test — doing that leaves both trees mounted at
  once, so a `findByRole`/`getByRole` query that matched a unique element
  in each render individually fails with "found multiple elements" once
  both are live together. Split into two separate `it()` blocks instead
  (as `AddressListPage.test.tsx` does for its empty-state vs.
  populated-state "Add address" visibility checks).
- **Testing a plain hook** (not a component): `useMessages.test.ts` uses
  `renderHook`/`act` from `@testing-library/react` — follow this pattern
  for a future hook-level test rather than wrapping the hook in a
  throwaway component.
- **Mocking API calls**: `PasswordChangePage.test.tsx` mocks
  `../api/auth.ts` wholesale with `vi.mock(...)` since the page only
  imports one named export (`changePassword`) from it — follow the same
  approach for a new page test that needs to control an API call's
  resolution/rejection without hitting the network.
- **`getByLabelText` and required fields**: `FormField.tsx` appends a
  visible `*` to the `<label>`'s text content for `required` fields, so
  an exact-string `getByLabelText("Some label")` query will never match —
  use a regex anchored at the start (e.g. `/^Current password/`) instead.
- **Test helpers**: `src/test/renderWithProviders.tsx` (wraps a component
  in `MemoryRouter` + `LanguageContext` + `AuthContext`, with a default
  English `t` and an overridable `{ user, loading, route, setUser }` —
  pass a `vi.fn()` as `setUser` to assert a page called it with the
  right value, e.g. after a profile update) and `src/test/fixtures.ts`
  (`makeSessionUser()`, `makeUserAddress()`). Both `AuthContext` and
  `LanguageContext` have real default values (not `null`), so tests
  provide context directly via `<SomeContext value={...}>` rather than
  mocking modules or rendering the real `AuthProvider`/`LanguageProvider`
  (which do real async/localStorage work) — follow this pattern for new
  component tests that need auth/language state.
- **Run with**: `docker exec ecommerce_frontend npx vitest run` (or
  `npm run test` inside the container). Co-locate new test files next to
  the component/page they cover (`Thing.tsx` → `Thing.test.tsx`) — no
  separate `__tests__/` directory convention exists yet.

## CI

**None.** No `.github/workflows/`, no `Makefile`, no pre-commit hooks.
Every check above is run by hand. Never claim a check ran in CI.

## When fixing a bug

Per root project instructions: add a regression test that reproduces the
defect when practical, and run the relevant checks before declaring the
task complete. If a check cannot be run in the current environment
(e.g. no running containers), say so explicitly rather than assuming it
would pass.
