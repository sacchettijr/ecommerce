# Testing

## Backend

Function-based pytest (`pytest` + `pytest-django`), `pytestmark =
pytest.mark.django_db` at module level, `factory-boy` + `Faker` for test
data. Each app follows `tests/{api,models,views}/` + `tests/factories/`.

### Coverage by app (verified, not estimated)

| App | Coverage |
|---|---|
| `app_account/` (label `account`) | Partial. Well covered: login/logout/session/signup/email-verification/password-reset/password-change (including the unchanged-password rejection)/profile-update flows, `is_staff` admin gate, `safe_next_path`, `frontend_scheme_and_domain` (`app_account/tests/api/test_auth_api.py`, `app_account/tests/test_frontend_url.py`); `UserAddressModel`'s primary-address invariant (first-is-primary, demote-on-set, promote-on-delete, DB constraint) and the `/api/account/addresses/` list/set-primary endpoints, including cross-user access attempts (`app_account/tests/models/test_user_address_rules.py`, `app_account/tests/api/test_user_address_api.py`); `UserWishlistModel`/`UserWishlistItemModel` — auto-creation on every user-creation path, one-wishlist-per-user, duplicate-product rejection (DB + form error message), `position` append/reorg/gap-closing/cross-wishlist isolation, DB constraints (`app_account/tests/models/test_user_wishlist_rules.py`, `test_user_wishlist_item_rules.py`); the migration graph loads and matches model state (`app_account/tests/test_migrations.py`, written after the `NodeNotFoundError` incident — see `../memory/known_issues.md`). **Not covered**: `UserManagerModel` edge cases, every form except the auth/address/wishlist ones exercised via the API tests, `app_account/signals/create_default_superuser.py`, `app_account/management/commands/create_admin.py`, the wishlist admin inline formset (no API/UI exists yet to drive it). |
| `app_address/` (label `address`) | Has factories now (`CountryFactory`/`StateFactory`/`CityFactory`, written for the address tests above) but still **no tests of its own** — no model, form, admin, or serializer test for this app directly; everything that exercises `CityModel`/`StateModel`/`CountryModel` today does so indirectly through `app_account`'s address tests. |
| `app_core/` (label `core`) | **Zero tests.** `BaseModel`, `ContactForm`, `ContactSerializer`, `ContactViewSet`, `StableOrderingFilter`, `StandardPagination`, the health-check view — none tested. |
| `app_product/` (label `product`) | Partial, concentrated on image ordering/upload paths (`app_product/tests/models/test_product_image_rules.py`, `test_upload_paths.py`). **Not covered**: `ProductCategoryModel`/`ProductModel` core logic beyond incidental factory use, `ProductForm`/`ProductCategoryForm`, `ProductFilterSet`, the list/category viewsets (only the detail viewset is indirectly touched), most serializers. |

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
  Nothing else in the frontend has tests yet (notably not `SignupPage.tsx`
  or `ContactPage.tsx`, despite one of them also having a phone field) —
  this is a start, not full coverage; don't assume other components/pages
  are tested.
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
