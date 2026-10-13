# Testing

## Backend

Function-based pytest (`pytest` + `pytest-django`), `pytestmark =
pytest.mark.django_db` at module level, `factory-boy` + `Faker` for test
data. Each app follows `tests/{api,models,views}/` + `tests/factories/`.

### Coverage by app (verified, not estimated)

| App | Coverage |
|---|---|
| `app_account/` (label `account`) | Partial. Well covered: login/logout/session/signup/email-verification/password-reset flows, `is_staff` admin gate, `safe_next_path`, `frontend_scheme_and_domain` (`app_account/tests/api/test_auth_api.py`, `app_account/tests/test_frontend_url.py`). **Not covered**: `UserAddressModel`, `UserManagerModel` edge cases, every form except the auth ones exercised via the API tests, `app_account/signals/create_default_superuser.py`, `app_account/management/commands/create_admin.py`. |
| `app_address/` (label `address`) | **Zero tests.** No model, form, or admin tests at all. |
| `app_core/` (label `core`) | **Zero tests.** `BaseModel`, `ContactForm`, `ContactSerializer`, `ContactViewSet`, `StableOrderingFilter`, `StandardPagination`, the health-check view — none tested. |
| `app_product/` (label `product`) | Partial, concentrated on image ordering/upload paths (`app_product/tests/models/test_product_image_rules.py`, `test_upload_paths.py`). **Not covered**: `ProductCategoryModel`/`ProductModel` core logic beyond incidental factory use, `ProductForm`/`ProductCategoryForm`, `ProductFilterSet`, the list/category viewsets (only the detail viewset is indirectly touched), most serializers. |

No app has any `tests/views/*.py` content — every `views/__init__.py`
across every app is empty.

### Factories (only 4 exist, repo-wide)

`app_account.tests.factories.UserFactory`,
`app_product.tests.factories.{ProductCategoryFactory,ProductFactory,ProductImageFactory}`.
No factories exist for `app_address` (`Country`/`State`/`City`) or `app_core` —
consistent with those apps having zero tests. If you add tests for those
apps, you will need to write factories first.

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

**Zero test infrastructure exists** — confirmed definitively: no
`vitest`/`jest`/`@testing-library/*`/`cypress`/`playwright` in
`frontend/package.json`, no `.test.`/`.spec.` files anywhere under
`frontend/src/`, no `test` script. Before adding frontend tests, you must
choose and install a framework (Vitest + React Testing Library is the
natural fit for this Vite + React stack, but this has not been decided by
the project — raise it rather than assuming).

## CI

**None.** No `.github/workflows/`, no `Makefile`, no pre-commit hooks.
Every check above is run by hand. Never claim a check ran in CI.

## When fixing a bug

Per root project instructions: add a regression test that reproduces the
defect when practical, and run the relevant checks before declaring the
task complete. If a check cannot be run in the current environment
(e.g. no running containers), say so explicitly rather than assuming it
would pass.
