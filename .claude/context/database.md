# Database

PostgreSQL (`postgres:17-bookworm` locally, Render-managed Postgres in the
hosted prototype). `PROJECT/settings/database.py` parses `DATABASE_URL`
(Render) when present, else falls back to discrete `POSTGRES_*` env vars
(local Docker Compose) via `dj-database-url`.

## Models by app

- `app_core.models.BaseModel` (abstract, used by every other model):
  `created_at`/`updated_at` (`auto_now_add`/`auto_now`), `created_by`/
  `updated_by` (FK to `AUTH_USER_MODEL`, `SET_NULL`), auto-populated in
  `save()` from `utils.current_user.get_current_user()` (a thread-local
  set per-request by `app_account/middleware/CurrentUserMiddleware.py`).
- `app_account.models.UserModel` — Django app label `account`
  (`AbstractBaseUser` + `PermissionsMixin` + `app_core.models.BaseModel`):
  `email` is the `USERNAME_FIELD` (unique, indexed); `REQUIRED_FIELDS =
  ["name", "date_birth"]`; `is_active`/`is_staff`/`is_email_verified`
  flags. `db_table = "user"`.
- `app_account.models.UserAddressModel` (extends
  `app_address.models.BaseAddressModel`): adds `user` (FK, `CASCADE`,
  `related_name="user_addresses"`) and `primary` (bool). `save()` demotes
  other primaries for the same user (mirrors `ProductImageModel`);
  `UniqueConstraint(fields=["user"], condition=Q(primary=True))` backs it
  at the DB level. The FK itself is still written as `to="account.UserModel"`
  (app-label form, not a Python import) — see the label-preservation note
  in `structure.md`. See `domain.md`.
- `app_address.models.{CountryModel,StateModel,CityModel}` — Django app
  label `address`: strict FK hierarchy, `on_delete=PROTECT` throughout
  (deleting a Country/State/City that's still referenced is blocked, not
  cascaded) — intentional for reference data.
- `app_product.models.ProductCategoryModel` / `ProductModel` — Django app
  label `product` (`ProductBaseModel` base: `active`, `name`, auto-slug).
- `app_product.models.ProductImageModel`: see `domain.md` for its two `UniqueConstraint`s
  (single primary image per product; gapless per-product `order`, the
  latter `Deferrable.DEFERRED`) and the `save()`/signal logic that maintains
  them.
- `app_account.models.UserWishlistModel` — `user` (`OneToOneField`,
  `CASCADE`): one wishlist per user, enforced by the field itself (unique
  index), no extra `save()` logic needed (unlike `UserAddressModel`, there
  is no "one flag among many rows" invariant to maintain here). Auto-created
  by a `post_save` signal on `UserModel` — see `domain.md`.
- `app_account.models.UserWishlistItemModel` — `wishlist` (FK, `CASCADE`,
  `related_name="items"`), `product` (FK, `CASCADE`), `added_at`
  (`auto_now_add`), `position` (`PositiveIntegerField`, default `0`). Two
  `UniqueConstraint`s: `unique_product_per_wishlist` (plain — a real user
  error, surfaced as a clear form error) and `unique_position_per_wishlist`
  (`Deferrable.DEFERRED`, mirrors `ProductImageModel.order`). `save()` locks
  the parent wishlist (`select_for_update`), always appends new items at the
  end, and re-flows positions gap-free via `organize_wishlist_items()`
  (a per-app copy of `organize_product_images()`'s anchor-insert algorithm —
  deliberately not shared across apps, per project convention). A
  `post_delete` signal closes the gap after a deletion, mirroring
  `app_product.signals.product_image`. See `domain.md`.

## Migrations — confirmed risk

`git ls-files | grep migrations` shows that **only each app's
`migrations/__init__.py` is actually committed** — real migration files
(e.g. `app_account/migrations/0001_initial.py`) exist on local disks but are
**not tracked in git**. `.gitignore` contains a bare `migrations/` ignore
rule (line 9) with a comment marking it temporary ("remove from this list
closer to production"), which directly contradicts a *later* comment in
the same file stating migrations must never be ignored because they are
part of the application source code. As it stands today, **a fresh clone
of this repository cannot run `manage.py migrate` successfully** — there
are no migrations to apply for any app. Treat this as a live, confirmed
problem (see `../memory/known_issues.md`), not a style preference: do not assume
migrations exist in version control when reasoning about deployment or
onboarding, and flag it to the user before relying on a fresh clone/CI
environment having a working database.

Verified during the `app_` rename (2026-10-13): with the old app labels
preserved via explicit `label =` on each `AppConfig`, `makemigrations
--check --dry-run` reports "No changes detected" against these same
pre-existing migration files — confirming the label-preservation strategy
kept the migration graph and `dependencies` tuples (which reference the
old labels, e.g. `("account", "0001_initial")`) fully valid.

**Confirmed incident (2026-10-15, wishlist task):** exactly the risk above
materialized. `app_address/migrations/0001_initial.py` and
`app_product/migrations/0001_initial.py` were both missing from disk
(not git-tracked, as above) while `app_account/migrations/0002_initial.py`
(regenerated the same day) still declared hard dependencies on both —
`NodeNotFoundError` on every `manage.py` invocation, and `entrypoint.sh`'s
unconditional `makemigrations` step (under `set -e`) turned that into a
live container crash-loop (`ecommerce_django`, 233+ restarts before being
caught). The live database itself had partial, inconsistent schema: its
`django_migrations` bookkeeping and tables only covered what had been
migrated before the files disappeared (confirmed via direct `psql`
inspection — zero rows anywhere, so no real data was at risk). Fixed
without `--fake`/`--fake-initial` and without touching `django_migrations`
by hand: regenerated real `0002_initial.py` files for both apps (Django's
own autodetector, not hand-written) and corrected
`app_account/migrations/0002_initial.py`'s dependencies from
`("address"/"product", "0001_initial")` (now-empty bookkeeping-only
migrations) to `("address"/"product", "0002_initial")` (the migrations
that actually create `CityModel`/`CountryModel`/`StateModel`/`ProductModel`
etc.) — account's FK fields need those tables to exist first. This is a
one-off repair of a specific broken state, not a fix for the underlying
"migrations aren't in git" policy, which is still open — see
`../memory/known_issues.md`.

## Indexes and constraints

Beyond Django's automatic PK/FK indexes: `UserModel.email` has
`db_index=True` (plus the implicit unique index from `unique=True`).
Constraint usage is otherwise concentrated on `ProductImageModel` and
`UserAddressModel` (see above and `domain.md`) — both are good reference
examples of "prefer database constraints for invariants that must hold
regardless of the calling code," per project convention.

## Seed / admin bootstrap — two divergent mechanisms (see `../memory/known_issues.md`)

- `entrypoint.sh` runs `python manage.py create_admin` on every container
  start — a custom management command that creates the superuser from
  `DJANGO_SUPERUSER_*` env vars and **raises if they're missing** (no
  insecure fallback).
- Independently, `app_account/signals/create_default_superuser.py` is wired to
  Django's `post_migrate` signal (via `AccountConfig.ready()`) and creates
  a superuser with **hard-coded weak fallback credentials**
  (`admin@example.com` / `admin123`) if no superuser exists and the env
  vars are absent. Running `migrate` without those env vars set — in any
  environment — silently creates a guessable admin account. This is a
  genuine security-relevant inconsistency; see `security.md` and
  `../memory/known_issues.md` before changing superuser-bootstrap behavior.
