# Testing

## Backend

Function-based pytest (`pytest` + `pytest-django`), `pytestmark =
pytest.mark.django_db` at module level, `factory-boy` + `Faker` for test
data. Each app follows `tests/{api,models,views}/` + `tests/factories/`.

### Coverage by app (verified, not estimated)

| App | Coverage |
|---|---|
| `app_account/` (label `account`) | Partial. Well covered: login/logout/session/signup/email-verification/password-reset/password-change (including the unchanged-password rejection)/profile-update flows, `is_staff` admin gate, `safe_next_path`, `frontend_scheme_and_domain` (`app_account/tests/api/test_auth_api.py`, `app_account/tests/test_frontend_url.py`); `UserAddressModel`'s primary-address invariant (first-is-primary, demote-on-set, promote-on-delete including the admin-formset-deletion edge case, DB constraint, cross-user isolation via the actual inline formset) and the `/api/account/addresses/` list/set-primary endpoints, including cross-user access attempts (`app_account/tests/models/test_user_address_rules.py`, `app_account/tests/api/test_user_address_api.py`); the country/state/city cross-field validation (`app_account/tests/models/test_user_address_form.py`); the address admin's rendered field order, standalone and inline (`app_account/tests/test_user_address_admin.py`); `UserWishlistModel`/`UserWishlistItemModel` — auto-creation on every user-creation path, one-wishlist-per-user, duplicate-product rejection (DB + form error message), `position` append/reorg/gap-closing/cross-wishlist isolation, DB constraints (`app_account/tests/models/test_user_wishlist_rules.py`, `test_user_wishlist_item_rules.py`); the migration graph loads and matches model state (`app_account/tests/test_migrations.py`, written after the `NodeNotFoundError` incident — see `../memory/known_issues.md`). **Not covered**: `UserManagerModel` edge cases, every form except the auth/address/wishlist ones exercised via the API tests, `app_account/signals/create_default_superuser.py`, `app_account/management/commands/create_admin.py`, the wishlist admin inline formset (no API/UI exists yet to drive it). |
| `app_address/` (label `address`) | Has its first tests of its own now (`app_address/tests/api/test_geo_filters.py`, added 2026-10-16: the country-filtered-states/state-filtered-cities endpoints, staff-only access). Everything else exercising `CityModel`/`StateModel`/`CountryModel` still does so indirectly through `app_account`'s address tests, including the new cross-field validation (`app_account/tests/models/test_user_address_form.py`). |
| `app_core/` (label `core`) | **Zero tests.** `BaseModel`, `ContactForm`, `ContactSerializer`, `ContactViewSet`, `StableOrderingFilter`, `StandardPagination`, the health-check view — none tested. |
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
  `src/auth/ProtectedRoute.test.tsx`, `src/hooks/useMessages.test.ts` —
  plus one standalone pure-function test,
  `src/components/ui/sanitizePhoneInput.test.ts` (59 tests total).
  Added 2026-10-16: the public product pages' new pieces —
  `src/components/product/ProductBreadcrumb.test.tsx`,
  `ExpandableDescription.test.tsx`, `formatPrice.test.ts`,
  `productSort.test.ts`, `src/pages/ProductListPage.test.tsx` (ordering
  query-building only), and `src/i18n/detectInitialLanguage.test.ts`
  (82 tests total now). Nothing else in the frontend has tests yet
  (notably not `SignupPage.tsx` or `ContactPage.tsx`, despite one of them
  also having a phone field, and no test touches `ProductDetailPage.tsx`
  or `HomePage.tsx` as a whole, only their extracted pieces) — this is
  still a start, not full coverage; don't assume other components/pages
  are tested.
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
