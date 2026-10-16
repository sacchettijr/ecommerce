# Current Task

## Objective

Implement and review the wishlist system (backend only, `app_account`):
one wishlist per user, items with no duplicate product per list, a
gap-free `position` field with safe insertion/reorganization, admin
support, tests. Explicitly out of scope: any frontend work, any API
endpoint, touching `frontend.old/`.

## Status: Complete

See `changelog.md` (2026-10-15 entry) for the full account of files
changed, the migration-graph incident and its fix, and the verification
results. Highlights for picking up related work:

- **Blocking migration incident, fixed first**: `app_address/migrations/
  0001_initial.py` and `app_product/migrations/0001_initial.py` were
  missing from disk (migrations aren't committed to git — see
  `../memory/known_issues.md`), which left `app_account/migrations/
  0002_initial.py` depending on nonexistent nodes (`NodeNotFoundError`)
  and, via `entrypoint.sh`'s unconditional `makemigrations` under `set -e`,
  put `ecommerce_django` in a live crash-loop (233+ restarts). Fixed by
  regenerating real migrations for both apps (Django's own autodetector,
  not hand-written) and correcting `account.0002_initial`'s dependencies
  to point at the migrations that actually create the referenced tables
  — no `--fake`, no manual `django_migrations` edits, no data loss (the
  affected tables were confirmed empty throughout). See `database.md`'s
  "Migrations — confirmed risk" section for the exact mechanics.
- **Models**: `UserWishlistModel` (`OneToOneField`, no custom `save()`
  needed) and `UserWishlistItemModel` (`position` field +
  `organize_wishlist_items()`, a per-app copy of `ProductImageModel`'s
  `order`/`organize_product_images()` pattern — deliberately not shared
  across apps). See `database.md`/`domain.md`.
- **Auto-creation**: `app_account/signals/create_wishlist_for_new_user.py`,
  a `post_save` signal on `UserModel` — chosen over a service function so
  every creation path (signup, admin, factories, future commands) is
  covered uniformly without each one remembering to call it.
- **Admin**: `UserWishlistAdmin` (with an items inline) and
  `UserWishlistItemAdmin`, both wired with `select_related`/
  `prefetch_related` and `autocomplete_fields` for `product`. Fixed a
  pre-existing bug in the drafted admin files: `search_fields` referenced
  `user__username`, a field `UserModel` doesn't have (it uses `email` as
  `USERNAME_FIELD`) — corrected to `user__email`/`user__name`.
- **Tests**: `app_account/tests/models/test_user_wishlist_rules.py`,
  `test_user_wishlist_item_rules.py`, `app_account/tests/test_migrations.py`
  (regression test for the `NodeNotFoundError` incident) — 30 new tests,
  181 passed overall (no regressions). `ruff`/`mypy`/`basedpyright` all
  clean. See `testing.md`.

## Not touched (out of scope, by task instruction)

- No frontend changes of any kind; `frontend.old/` untouched.
- No API endpoint for the wishlist (admin is the only interface today —
  see `project_state.md`'s "Immediate priorities").
- The underlying "migrations not committed to git" policy itself — only
  the specific broken state it caused this time was repaired.
