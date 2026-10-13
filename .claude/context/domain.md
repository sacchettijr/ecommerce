# Domain & Business Rules

Only rules actually verified in source code are documented here.

## User lifecycle (app_account, Django label `account`)

1. `SignUpViewSet.create()` validates `app_account/forms/SignUpForm.py`, saves
   a `UserModel` with `is_active=True` (default) and `is_email_verified=False`
   (default), then dispatches the verification email via Celery
   (`app_account/emails/send_verification_email.py` → task
   `app_account.tasks.send_email_verification_email`, dispatched **by task name**
   via `current_app.send_task(...)` rather than a direct `.delay()` import —
   intentional, so a worker/name mismatch drops the task silently instead of
   raising an import error at dispatch time).
2. The verification link encodes `uid`/`token`. `EmailVerificationViewSet.confirm`
   validates the token with a custom `EmailVerificationTokenGenerator` whose
   hash includes `is_email_verified`, so the token **self-invalidates** once
   used. Invalid, expired, and already-used tokens all return the same
   `{"code": "invalid_link"}` / 400 — this is intentional (no information
   leak about *why* a link failed).
3. Login is gated by **both** `is_active` and `is_email_verified`:
   `app_account/backends/EmailVerifiedModelBackend.user_can_authenticate()`
   requires both to be true, so Django's standard backend returns `None`
   (as if the password were wrong) when either is false.
4. `app_account/forms/LoginForm.py` then re-checks manually to produce a
   *specific* error when the password is actually correct:
   - correct password, `is_active=False` → `ValidationError(code="inactive", ...)`,
     message: "This account has been deactivated."
   - correct password, `is_email_verified=False` → `ValidationError(code="email_not_verified", ...)`,
     message explains verification is required; `self.unverified_user` is
     set so the frontend can offer a resend-verification action.
   - wrong email or wrong password → the same generic invalid-login message
     in both cases (no account-enumeration leak).
   - **No documented rule exists for the case where both `is_active=False`
     and `is_email_verified=False` simultaneously** — confirm actual
     precedence in `LoginForm.clean()`/`__get_login_error()` before relying
     on a specific order if this matters for a change.
5. `EmailVerificationViewSet.resend` and `PasswordResetViewSet.create`
   (backed by a custom `PasswordResetForm`) both return an **identical
   response whether or not the account/email exists** — explicit,
   commented anti-enumeration behavior. Do not change this without
   understanding the security tradeoff (see `security.md`).

### Rate limiting (confirmed, `PROJECT/settings/rest_framework.py`)

Per-scope `ScopedRateThrottle` rates: `signup` 10/hour, `login` 10/minute,
`email_verification` 5/hour (resend action), `password_reset` 5/hour
(create action; `validate`/`confirm` use `token_check` 60/hour), `contact`
5/hour.

## Addresses (`account.UserAddressModel`, app_address, Django label `address`)

- `app_address/models/{CountryModel,StateModel,CityModel}.py` form a strict
  hierarchy (`Country ← State ← City`), each normalizing its `name` on
  `save()`. No public API — admin-only (`app_address/admin/`).
- `UserAddressModel` extends `app_address.models.BaseAddressModel`, adds `user` (FK,
  `CASCADE`) and `primary` (bool). **At most one primary address per
  user** is enforced both at the model level and the database level
  (belt and suspenders, mirroring `ProductImageModel`'s pattern):
  `UserAddressModel.save()` locks the parent user row and demotes any
  other primary address for that user before saving, and
  `UniqueConstraint(fields=["user"], condition=Q(primary=True), name="unique_primary_address_per_user")`
  guards the invariant at the DB level regardless of caller.
  `validate_constraints`/`_get_unique_checks` are overridden so admin
  inline formsets tolerate a transient multi-primary submission (the
  `save()` reorganization resolves it row by row). This does **not**
  guarantee at least one primary exists — a user with zero addresses, or
  with addresses but none marked primary, is a valid state (same
  tolerance as `ProductImageModel`'s `is_primary`).
- Admin-manageable: `UserAddressAdmin` (standalone, `get_form()` picks
  `UserAddressCreateForm`/`UserAddressUpdateForm` for add vs change) and
  `UserAddressInlineAdmin` (attached to `UserAdmin.inlines`). No public
  API exists yet — see `api.md`.

## Product catalog (app_product, Django label `product`)

- `ProductCategoryModel` / `ProductModel` share `ProductBaseModel`
  (`active`, `name`, auto-generated unique `slug`). Public API only returns
  `active=True` rows (`ProductSimpleListViewSet`, `ProductDetailViewSet`,
  `ProductCategorySimpleListViewSet`, all `AllowAny`).
- `ProductModel.save()` does a two-phase insert for new rows (save once to
  get a PK, then re-save) because the thumbnail's `upload_to` path needs
  the PK.
- `ProductImageModel` enforces, per product: **at most one primary image**
  (`UniqueConstraint(product, condition=Q(is_primary=True))`) and
  **gapless, unique `order`** (`UniqueConstraint(product, order)`,
  `Deferrable.DEFERRED` so a multi-row reorder inside one transaction
  doesn't trip the constraint mid-flight). `save()` locks the parent
  product row, demotes any other primary image if this one is marked
  primary, then calls `organize_product_images()` to renumber `order` with
  no gaps/duplicates — including moving an image to a *different* product
  (closes the gap on the source product too). A `post_delete` signal
  (`app_product/signals/product_image.py`) re-runs the same renumbering after
  deletion and promotes `order=0` to primary if the deleted image was
  primary and none remains.

## Shopping cart / checkout — confirmed absent

A repository-wide search (backend and frontend) found **no cart, order, or
checkout implementation anywhere**:

- Backend: no `Cart`/`CartItem`/`Order` model, serializer, viewset, or URL.
- Frontend: the cart link in `Navbar.tsx` is a dead `<a href="#">` with no
  handler; the "Add to cart" button on `ProductDetailPage.tsx` has no
  `onClick`; `UserMenu.tsx`'s profile/orders/addresses/wishlist items are
  all inert buttons with an explicit code comment acknowledging they're
  "reserved for when they exist." Translation strings for all of the above
  exist in every locale, but there is zero state, API, or routing behind
  them.

Treat any task that assumes a working cart as requiring that feature to be
built from scratch, not extended.

## Internationalization — backend/frontend mismatch

The frontend's custom i18n (`frontend/src/i18n/`) has genuine, idiomatic
translations for all five required languages (English, Portuguese,
Spanish, French, Italian — confirmed by distinct content, not
copy-pasted stubs). The backend's Django `LANGUAGES` setting
(`PROJECT/settings/internationalization.py`) **currently only declares
`pt-br`, `en`, `es`** — French and Italian are not active backend locales,
even though `locale/fr/` and `locale/it/` gettext catalog directories exist
on disk. This mismatch is explicitly called out in a code comment in
`frontend/src/i18n/languages.ts`. Practical effect: French/Italian users
get a fully translated UI, but backend-generated text (validation errors,
email bodies) sent with `Accept-Language: fr`/`it` will not be localized by
Django today. Additionally, the actual `.po` catalogs are very sparse —
only 3 real translatable strings are marked for translation across all
five languages combined (confirmed by reading `locale/en/LC_MESSAGES/django.po`
in full). Most user-facing backend strings have not yet been wrapped for
translation. See `conventions.md` for the i18n convention to follow when
adding new translatable strings.

## Calculations

No business calculations beyond straightforward field validation were
found. `ProductModel.price` is a plain `DecimalField` validated by
`validate_positive_decimal` (must be `> 0`); there is no tax, discount,
shipping, or total computation anywhere in the codebase (consistent with
there being no cart/checkout). If pricing logic is added later, document it
here.
