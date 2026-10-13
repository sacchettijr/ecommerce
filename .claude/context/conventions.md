# Conventions

## Naming and code style (Python)

- Models: `XxxModel` suffix (`UserModel`, `ProductImageModel`). Abstract
  bases: `BaseModel`, `BaseAddressModel`.
- One class per file, filename matches the class name
  (`app_account/models/UserModel.py` → `class UserModel`). Apps re-export
  everything through `__init__.py` (`from .UserModel import UserModel`,
  with `__all__`).
- Forms: `XxxForm`, small per-field **mixins** for reusable validation
  (`NormalizedNameFieldMixin`, `NormalizedStreetFieldMixin`, etc.), one
  mixin per field even when the logic is nearly identical across apps
  (e.g. three separate near-identical "name" mixins exist for `app_account`,
  `app_product`, and `app_address` — this duplication is a deliberate, consistent
  project style, not an oversight to "DRY up" uninvited).
- Admin classes and inlines follow the `TYPE_CHECKING` generic-base pattern
  throughout:
  ```python
  if TYPE_CHECKING:
      BaseXAdmin = admin.ModelAdmin[XModel]
  else:
      BaseXAdmin = admin.ModelAdmin
  ```
  Use the same pattern for `forms.ModelForm[Model]` and
  `admin.TabularInline[Child, Parent]`. This exists because
  `django-stubs`' generics aren't subscriptable at runtime — don't "fix"
  it by removing the `TYPE_CHECKING` branch.
- Keep using `cast(Any, instance).field_id` (not `.field.pk`) when you need
  an FK's raw id without triggering a query or when django-stubs can't
  infer the type — this is the established pattern in `ProductImageModel.save()`
  and elsewhere, not a one-off hack.

## Error handling

- Model-level invariants: prefer a DB `Meta.constraint` as the ultimate
  guard, with a `save()` override doing the "friendly" auto-correction
  (see `ProductImageModel`). When a model's `save()` normalizes/reorganizes
  fields that a `Meta.constraint` also covers, override
  `validate_constraints`/`_get_unique_checks` to exclude those fields from
  form-level validation — the DB constraint is still the real guard; the
  form shouldn't double-guess it and produce a confusing validation error
  during admin inline-formset submission. See `ProductImageModel` for the
  exact pattern.
- Account-related errors use stable `code` values in the response body
  (`"inactive"`, `"email_not_verified"`, `"invalid_link"`) so the frontend
  can branch without parsing message text. Follow this when adding new
  account error cases.
- Celery dispatch failures are deliberately swallowed
  (`utils/dispatch_task.py`) — do not change this to propagate exceptions
  without discussing the tradeoff (signup/password-reset/contact would
  start failing outright whenever RabbitMQ is briefly unavailable).
- Do not introduce a second insecure-fallback bootstrap path like
  `app_account/signals/create_default_superuser.py`'s hard-coded admin
  credentials — see `../memory/known_issues.md`. If you touch superuser bootstrapping,
  reconcile it with `create_admin`'s stricter (raise-if-missing) behavior
  instead of adding a third variant.

## Internationalization

- **Backend**: wrap every user-facing string in
  `django.utils.translation.gettext_lazy as _`, called with the
  `message=` keyword (the project's consistent style — see any model's
  `verbose_name=_(message="...")`). Run `makemigrations`/`makemessages`
  as needed and keep `.po` catalogs under `locale/` in sync. Current
  catalogs are very sparse (3 real strings total across all 5 languages,
  see `domain.md`) — this is a known gap, not a sign that most strings
  don't need translation.
- **`LANGUAGES` currently only includes pt-br/en/es** on the backend
  (`PROJECT/settings/internationalization.py`) even though the frontend
  fully supports fr/it — see `domain.md`. If a task requires backend
  localization in French/Italian, that setting needs to change too; don't
  assume it already matches the frontend's language list.
- **Frontend**: a custom i18n system, not a library. Every translatable
  string is a key on one canonical `Translations` interface
  (`frontend/src/i18n/types.ts`), implemented once per language under
  `frontend/src/i18n/locales/{en,es,fr,it,pt-br}.ts`. Interpolated strings
  are typed as functions (e.g. `userMenu.hello: (name: string) => string`),
  not template placeholders — follow this when adding a new translatable
  string: add the key to `Translations`, then provide it in **all five**
  locale files (missing one will be a type error, which is the intended
  safety net). Do not introduce a second i18n library.

## Testing conventions

- Backend: function-based pytest, `pytestmark = pytest.mark.django_db` at
  module level, `factory-boy` + `Faker` for fixtures, heavy use of small
  local helper functions and `@pytest.mark.parametrize`. See `testing.md`
  for the full picture (including real, current coverage gaps).
- Keep new tests in the matching app's `tests/{api,models,views}/` and
  `tests/factories/` subfolders, matching the existing per-app layout —
  don't put a new test file directly under `tests/` the way
  `app_account/tests/test_frontend_url.py` currently does (an existing
  inconsistency to avoid repeating, not a pattern to copy).

## Docker / infra

- Don't add a Dockerfile for a service that just needs the official image
  plus a mounted config file (`redis/redis.conf`, `rabbitmq/rabbitmq.conf`)
  — `database/` and `cloudbeaver/` deliberately have neither a Dockerfile
  nor a config file, just the bare official image. This is a conscious
  project decision, not an oversight.
- When a service should stay internal to the Docker network, use `expose`
  with the `ports:` line commented out (and an explanatory comment), as
  done for `backend`/`frontend` — don't just delete the `ports:` line
  silently; future readers need to know how to re-enable it for direct
  testing.
