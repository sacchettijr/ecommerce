# Current Task

## Objective

Audit, organize, and expand the backend's automated test suite across
all 5 Django apps — standardize the `tests/` directory structure,
implement meaningful new tests prioritizing business-critical behavior,
security, data integrity, and previously untested branches, including
dedicated internationalization/translation tests.

## Status: Complete

See `changelog.md` (2026-10-28 entry) for full detail. Highlights:

- Baseline: 320 passed, 0 failed. All 5 apps already used a `tests/`
  package (no standalone `test.py`/`tests.py` anywhere) — the
  reorganization need was smaller than the task anticipated.
- Moved a handful of standalone test files into proper subpackages
  (`tests/admin/`, `tests/utils/`) across `app_account`/`app_core`;
  `app_product`'s one such move had already been done (found
  uncommitted, in progress, at the start).
- Added 121 new tests (441 passed, 0 failed, final) across all 5 apps:
  `CurrentUserMiddleware`/`created_by`/`updated_by` stamping,
  `create_default_superuser`, `UserManagerModel`/`UserModel`,
  `EmailVerifiedModelBackend`, `app_address`'s `PROTECT`-delete behavior,
  `CityListViewSet` permission parity, `app_product`'s public-browsing/
  inactive-product-visibility rule, `app_checkout`'s admin + deactivation
  signal, the health-check view, 5 shared `utils/` modules, and a new
  dedicated i18n test suite (zero existed before).
- Documented, not fixed: `app_address`'s missing uniqueness constraints
  on Country/State/City (`known_issues.md` #19) and a pre-existing,
  unrelated mypy error in `app_checkout/models/CartItemModel.py`
  (`known_issues.md` #20) — both flagged for a user decision/separate
  investigation rather than acted on unilaterally.

## Verification

Full `pytest` — 441 passed, 0 failed, 268 warnings, ~8 min; `manage.py
check` clean; `makemigrations --check --dry-run` clean (no model changes
— tests-only task); project-wide `ruff check`/`format --check` clean;
project-wide `mypy` clean except the one pre-existing, unrelated error
above; project-wide `basedpyright` clean (0 errors).

## Not done / out of scope

No DB constraints added for the app_address uniqueness gap (would be a
production-behavior change needing a migration and a decision on
existing-duplicate handling — out of scope for a testing task). No fix
attempted for the pre-existing `CartItemModel.py` mypy error. Frontend
untouched entirely (`frontend.old/` untouched, React tests untouched),
per the task's explicit scope boundary. Did not attempt literal 100%
branch coverage of every form/admin/mixin in every app — prioritized by
business-criticality/security/data-integrity per the task's own
instructions; several lower-risk gaps remain and are listed per-app in
`../context/testing.md`'s coverage table.
