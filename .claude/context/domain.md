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
6. **Self-service password change** (`PasswordChangeViewSet`, mounted at
   `/api/account/password-change/`) is separate from the password-reset
   flow above — it's for an already-authenticated user changing their own
   password, not a forgotten-password recovery. Uses the global default
   `IsAuthenticated` permission (no `AllowAny`) and
   `app_account/forms/PasswordChangeForm.py` (a subclass of
   `django.contrib.auth.forms.PasswordChangeForm`, with one added rule —
   see point 7 below), constructed with
   `request.user` — **no user identifier is ever read from the request
   body**, so a client cannot change another account's password by
   supplying an id/email in the payload (verified by a test that
   deliberately smuggles another user's id/email into the request and
   asserts only `request.user`'s password changes). Requires the correct
   current password (`old_password`, field-level `password_incorrect`
   error otherwise) and validates the new one against
   `AUTH_PASSWORD_VALIDATORS` (above). On success, calls
   `update_session_auth_hash()` so the current session stays valid instead
   of being silently logged out mid-request — this is a deliberate
   difference from the password-reset-via-email flow, which happens
   outside any existing session.
7. **The new password must differ from the current one.**
   `PasswordChangeForm.clean()` compares the submitted `new_password1`
   against the user's *stored* hash via `self.user.check_password(...)`
   (never a raw string comparison against `old_password`), and only once
   `old_password` itself already cleaned successfully — so an incorrect
   current password still produces only its own field error, never also
   this one. A match raises a **non-field** `ValidationError` with
   `code="password_unchanged"`, which `form_errors_payload` surfaces as
   `{"non_field_errors": [...], "code": "password_unchanged"}` — same
   400 response shape as every other account error, reusing the
   established `code` convention rather than inventing a new response
   format. The frontend (`PasswordChangePage.tsx`) recognizes this
   specific code and renders it as a `warning`-variant notification
   through the shared `useMessages` mechanism, not as a success and not
   as a generic red error.
8. **Self-service profile editing** (`ProfileUpdateViewSet`, mounted at
   `/api/account/profile/`) — same `IsAuthenticated`-only, `request.user`-only
   pattern as password change. Uses
   `app_account/forms/UserUpdateForm.py` (a `ModelForm` over `UserModel`,
   `Meta.fields = ("name", "date_birth", "phone")` — **`email` is
   deliberately not editable here**: changing the login identifier would
   need its own re-verification flow, analogous to signup's email
   confirmation, which doesn't exist for an *existing* account today;
   treat adding that as a separate feature, not a trivial field
   addition). Because the form's `fields` only lists those three names,
   any other submitted key (`is_staff`, `is_superuser`, `is_active`,
   `email`, a client-supplied `id`, ...) is simply ignored by Django's
   `ModelForm` machinery — no extra filtering code was needed, only a
   test proving it. Skips the actual `.save()` call (and so leaves
   `updated_at` untouched) when `form.has_changed()` is `False`. Returns
   `{"user": serialize_user(user)}` on success, same shape as
   login/signup, so the frontend can feed the response straight into
   `AuthContext`'s `setUser()` and keep the navbar/profile home in sync
   without a second request or a reload.

### Rate limiting (confirmed, `PROJECT/settings/rest_framework.py`)

Per-scope `ScopedRateThrottle` rates: `signup` 10/hour, `login` 10/minute,
`email_verification` 5/hour (resend action), `password_reset` 5/hour
(create action; `validate`/`confirm` use `token_check` 60/hour),
`password_change` 10/hour, `contact` 5/hour. **`profile` (the profile-edit
endpoint) is deliberately not throttled** — unlike the other account
mutation endpoints, it has no credential-guessing or abuse surface
(no secret being verified), consistent with how an ordinary authenticated
CRUD endpoint in this project is not throttled by default.

## Addresses (`account.UserAddressModel`, app_address, Django label `address`)

- `app_address/models/{CountryModel,StateModel,CityModel}.py` form a strict
  hierarchy (`Country ← State ← City`), each normalizing its `name` on
  `save()`. These three have no standalone API of their own (still
  admin-only, `app_address/admin/`) but each has a small read-only
  nested serializer under `app_address/api/serializers/` (`CitySimpleSerializer`,
  `StateSimpleSerializer`, `CountrySimpleSerializer` — `id`/`name` plus
  `code`/`iso_code` respectively), consumed by `UserAddressSerializer`
  (below) to show human-readable city/state/country names instead of
  raw FK ids.
- `UserAddressModel` extends `app_address.models.BaseAddressModel`, adds `user` (FK,
  `CASCADE`) and `primary` (bool). **The full invariant — zero addresses
  ⇒ zero primary; one or more addresses ⇒ exactly one primary — is
  enforced entirely at the model/signal level, not in the API layer**,
  so it holds for every caller (admin today, the read/set-primary API,
  any future caller):
  - **At most one primary** (the half that existed before this task):
    `UserAddressModel.save()` locks the parent user row and demotes any
    other primary address for that user before saving, backed by
    `UniqueConstraint(fields=["user"], condition=Q(primary=True), name="unique_primary_address_per_user")`
    at the DB level regardless of caller.
  - **A user's first address is always primary**, even if the caller
    explicitly submits `primary=False` — `save()` forces it when
    `self.pk is None` (a genuine insert) and the user has no other
    address yet. This is what keeps "has addresses ⇒ exactly one
    primary" self-enforcing for a future creation workflow without that
    workflow having to know or care about the rule itself.
  - **Deleting the primary address promotes another one** (the oldest
    remaining, by `created_at`) if any addresses are left — a
    `post_delete` signal, `app_account/signals/promote_primary_address_after_delete.py`,
    wired up in `AccountConfig.ready()` exactly like
    `app_product.signals.product_image`'s analogous image-primary-promotion
    signal. Covers both `instance.delete()` and `QuerySet.delete()` (checked
    via the signal's `origin` argument, same technique as the product
    precedent) and no-ops safely if the user itself was deleted too
    (CASCADE).
  - `validate_constraints`/`_get_unique_checks` are overridden so admin
    inline formsets tolerate a transient multi-primary submission (the
    `save()` reorganization resolves it row by row).
  - This task implemented the **listing and primary-selection** surface
    only — there is still no create/update/delete endpoint or UI for
    addresses (see below); the model/signal hardening above exists so
    that whenever creation/deletion *are* eventually built, the invariant
    doesn't need to be re-implemented or re-verified there.
- **Read/primary-selection API** (`UserAddressViewSet`, mounted at
  `/api/account/addresses/` — see `api.md` for the exact endpoints):
  `get_queryset()` is always `UserAddressModel.objects.filter(user=request.user)`
  — no address id or user id from the client can ever surface another
  user's addresses; `set_primary` uses `self.get_object()` against that
  same scoped queryset, so targeting another user's address id 404s
  (indistinguishable from a nonexistent id — no enumeration leak) rather
  than succeeding or revealing ownership. `pagination_class = None`
  (a plain JSON array) — a handful of addresses per user doesn't need
  the project's default page-based pagination, and `set-primary` returns
  the user's full, freshly-queried address list (not just the one
  address) so the frontend can replace its entire local state with one
  authoritative response instead of reimplementing the demote-the-others
  logic itself. List ordering is `-primary, created_at` (primary first)
  — deliberately overriding the model's own `Meta.ordering`, which sorts
  primary *last* (`False < True`).
- Admin-manageable: `UserAddressAdmin` (standalone, `get_form()` picks
  `UserAddressCreateForm`/`UserAddressUpdateForm` for add vs change) and
  `UserAddressInlineAdmin` (attached to `UserAdmin.inlines`) — still the
  only way to create or delete an address; no frontend or API path does
  either yet.

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

## Wishlist (`account.UserWishlistModel`/`UserWishlistItemModel`, app_account)

Backend-only as of 2026-10-15 — no API endpoint, no frontend wiring; the
`UserMenu.tsx` wishlist link is still the same inert placeholder described
below. Admin (`UserWishlistAdmin`/`UserWishlistItemAdmin`, with an inline
for items) is the only way to operate on it today.

- **One wishlist per user**: `UserWishlistModel.user` is a plain
  `OneToOneField(CASCADE)` — the DB unique index on `user_id` is the whole
  invariant, no custom `save()` logic needed (unlike addresses, there's no
  "exactly one flagged row among several" problem here).
- **Auto-created on signup**: `app_account/signals/
  create_wishlist_for_new_user.py`, a `post_save` receiver on `UserModel`
  guarded by `created=True`, calls `UserWishlistModel.objects.get_or_create(
  user=instance)`. Chosen over a service function specifically because it
  must fire for *every* user-creation path (signup, admin, factories,
  future management commands) without each one remembering to call it — a
  signal registered once in `AccountConfig.ready()` (same `import_module`
  pattern as `promote_primary_address_after_delete`) covers all of them
  uniformly. `get_or_create` keeps it idempotent against a double-fire.
- **Items**: unlimited per list, but **no duplicate product in the same
  list** — `UniqueConstraint(wishlist, product)`, a real user error
  surfaced as a clear `ModelForm` validation error (not auto-corrected).
  The same product can appear in different users' lists.
- **`position`** (`PositiveIntegerField`, default `0`, 0-based): deliberately
  *not* the task's literal "1 = first" suggestion — `ProductImageModel.order`
  already established an equivalent, 0-based, gap-free pattern in this
  codebase, and reusing that pattern (not inventing a second convention)
  was judged more valuable than matching the literal suggestion. New items
  always append to the end (there is no form field for `position` yet —
  admin shows it read-only — so there is currently no sanctioned way to
  request a specific position on create). Repositioning an existing item
  (`item.position = N; item.save()`) re-flows all siblings gap-free via
  `organize_wishlist_items()`, a per-app copy of
  `organize_product_images()`'s anchor-insert algorithm (deliberately not
  shared across apps — see `conventions.md`). `UniqueConstraint(wishlist,
  position)` is `Deferrable.DEFERRED` so a multi-row reorder inside one
  transaction doesn't trip it mid-flight. `save()` locks the parent
  wishlist row (`select_for_update`) first, so concurrent inserts can't
  both compute the same "next" position. A `post_delete` signal
  (`reorganize_wishlist_items_after_delete.py`) closes the gap after a
  deletion — mirroring `app_product.signals.product_image` exactly.

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
