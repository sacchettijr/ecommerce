# Database

PostgreSQL (`postgres:17-bookworm` locally, Render-managed Postgres in the
hosted prototype). `PROJECT/settings/database.py` parses `DATABASE_URL`
(Render) when present, else falls back to discrete `POSTGRES_*` env vars
(local Docker Compose) via `dj-database-url`.

## Models by app

- `core.BaseModel` (abstract, used by every other model): `created_at`/
  `updated_at` (`auto_now_add`/`auto_now`), `created_by`/`updated_by` (FK to
  `AUTH_USER_MODEL`, `SET_NULL`), auto-populated in `save()` from
  `utils.current_user.get_current_user()` (a thread-local set per-request
  by `account/middleware/CurrentUserMiddleware.py`).
- `account.UserModel` (`AbstractBaseUser` + `PermissionsMixin` +
  `core.BaseModel`): `email` is the `USERNAME_FIELD` (unique, indexed);
  `REQUIRED_FIELDS = ["name", "date_birth"]`; `is_active`/`is_staff`/
  `is_email_verified` flags. `db_table = "user"`.
- `account.UserAddressModel` (extends `address.BaseAddressModel`): adds
  `user` (FK, `CASCADE`, `related_name="user_addresses"`) and `primary`
  (bool). `save()` demotes other primaries for the same user (mirrors
  `ProductImageModel`); `UniqueConstraint(fields=["user"],
  condition=Q(primary=True))` backs it at the DB level. See `domain.md`.
- `address.{CountryModel,StateModel,CityModel}`: strict FK hierarchy,
  `on_delete=PROTECT` throughout (deleting a Country/State/City that's
  still referenced is blocked, not cascaded) — intentional for reference
  data.
- `product.ProductCategoryModel` / `product.ProductModel`
  (`ProductBaseModel` base: `active`, `name`, auto-slug).
- `product.ProductImageModel`: see `domain.md` for its two `UniqueConstraint`s
  (single primary image per product; gapless per-product `order`, the
  latter `Deferrable.DEFERRED`) and the `save()`/signal logic that maintains
  them.

## Migrations — confirmed risk

`git ls-files | grep migrations` shows that **only each app's
`migrations/__init__.py` is actually committed** — real migration files
(e.g. `account/migrations/0001_initial.py`) exist on local disks but are
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
- Independently, `account/signals/create_default_superuser.py` is wired to
  Django's `post_migrate` signal (via `AccountConfig.ready()`) and creates
  a superuser with **hard-coded weak fallback credentials**
  (`admin@example.com` / `admin123`) if no superuser exists and the env
  vars are absent. Running `migrate` without those env vars set — in any
  environment — silently creates a guessable admin account. This is a
  genuine security-relevant inconsistency; see `security.md` and
  `../memory/known_issues.md` before changing superuser-bootstrap behavior.
