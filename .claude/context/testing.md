# Testing

## Backend

Function-based pytest (`pytest` + `pytest-django`), `pytestmark =
pytest.mark.django_db` at module level, `factory-boy` + `Faker` for test
data. Each app follows `tests/{api,models,views}/` + `tests/factories/`.

### Coverage by app (verified, not estimated)

| App | Coverage |
|---|---|
| `app_account/` (label `account`) | Partial. Well covered: login/logout/session/signup/email-verification/password-reset/password-change (including the unchanged-password rejection)/profile-update flows, `is_staff` admin gate, `safe_next_path`, `frontend_scheme_and_domain` (`app_account/tests/api/test_auth_api.py`, `app_account/tests/test_frontend_url.py`); `UserAddressModel`'s primary-address invariant (first-is-primary, demote-on-set, promote-on-delete including the admin-formset-deletion edge case, DB constraint, cross-user isolation via the actual inline formset) and the `/api/account/addresses/` list/set-primary endpoints, including cross-user access attempts (`app_account/tests/models/test_user_address_rules.py`, `app_account/tests/api/test_user_address_api.py`); the country/state/city cross-field validation (`app_account/tests/models/test_user_address_form.py`); the address admin's rendered field order, standalone and inline (`app_account/tests/test_user_address_admin.py`); `UserWishlistModel`/`UserWishlistItemModel` — auto-creation on every user-creation path, one-wishlist-per-user, duplicate-product rejection (DB + form error message), `private` defaults to `False`, `position` append/reorg/gap-closing/cross-wishlist isolation, DB constraints (`app_account/tests/models/test_user_wishlist_rules.py`, `test_user_wishlist_item_rules.py`); the full `/api/account/wishlist/...` surface — own list (public+private), add (incl. duplicate/inactive rejection, ignoring any client-sent wishlist/user id), remove/toggle-privacy/move all scoped to the owner (404, not 403, for another user's item id, mirroring the address pattern), `check`, `share-link` (`app_account/tests/api/test_wishlist_item_api.py`); the public `/api/account/wishlist/public/{public_id}/` endpoint — works unauthenticated, only public items, response never contains a `private` key, bad/unknown id is 404, no cross-user leakage (`app_account/tests/api/test_public_wishlist_api.py`); the migration graph loads and matches model state (`app_account/tests/test_migrations.py`, written after the `NodeNotFoundError` incident — see `../memory/known_issues.md`); signup/profile-update reject a single-word `name` (`test_signup_rejects_a_single_word_name`, `test_profile_update_field_errors_for_invalid_values[name-Maria]`, added 2026-10-17 alongside the shared `validate_name()` fix — see `domain.md`). **Not covered**: `UserManagerModel` edge cases, every form except the auth/address/wishlist ones exercised via the API tests, `app_account/signals/create_default_superuser.py`, `app_account/management/commands/create_admin.py`, the wishlist admin inline formset. |
| `app_address/` (label `address`) | Has its first tests of its own now (`app_address/tests/api/test_geo_filters.py`, added 2026-10-16: the country-filtered-states/state-filtered-cities endpoints, staff-only access). Everything else exercising `CityModel`/`StateModel`/`CountryModel` still does so indirectly through `app_account`'s address tests, including the new cross-field validation (`app_account/tests/models/test_user_address_form.py`). |
| `app_core/` (label `core`) | Has its first tests now (added 2026-10-17): the full `/api/core/contact/` surface — valid submission accepted, invalid phone rejected and doesn't consume the cooldown, a single-word name rejected (`test_a_single_word_name_is_rejected`), the new 60s cooldown (blocked within the window with correct `retry_after`/`Retry-After`, allowed again once elapsed, independent per user/IP), and the pre-existing 5/hour cap confirmed still independently enforced (`app_core/tests/api/test_contact_api.py`); the cross-app `utils/rate_limit.py` helpers — atomic allow-and-record semantics under concurrency, user-vs-IP identification, a forged `X-Forwarded-For` entry not changing the computed identity (`app_core/tests/test_rate_limit.py`); the cross-app `utils/validator.py`'s `validate_name()` directly — every branch (empty, no letters, single word, punctuation-only second "part" not counting, 2+ parts accepted) (`app_core/tests/test_validators.py`, added 2026-10-17 — the first direct unit tests for anything in `utils/validator.py`). **Still not covered**: `BaseModel`, `ContactForm` (confirmed still dead/unused), `StableOrderingFilter`, `StandardPagination`, the health-check view, every other function in `utils/validator.py`. |
| `app_product/` (label `product`) | Partial, concentrated on image ordering/upload paths (`app_product/tests/models/test_product_image_rules.py`, `test_upload_paths.py`) plus, added 2026-10-16: the admin field order (`app_product/tests/test_product_admin.py`) and the randomized default/explicit-override catalog ordering (`app_product/tests/api/test_product_randomized_ordering.py`). **Not covered**: `ProductCategoryModel`/`ProductModel` core logic beyond incidental factory use, `ProductForm`/`ProductCategoryForm`, `ProductFilterSet`, the list/category viewsets' other behavior (only ordering and the detail viewset are touched), most serializers. |

No app has any `tests/views/*.py` content — every `views/__init__.py`
across every app is empty.

### Factories

`app_account.tests.factories.{UserFactory,UserAddressFactory,UserWishlistFactory,UserWishlistItemFactory}`,
`app_address.tests.factories.{CountryFactory,StateFactory,CityFactory}`,
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
  tests total now). Nothing else in the frontend has tests yet, and no
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
