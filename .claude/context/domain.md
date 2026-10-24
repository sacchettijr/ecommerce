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
1a. **The `name` field requires a full name (first and last), not a single
   word** (added 2026-10-17, per direct user feedback — it was previously
   letting a single-word name through). Enforced in
   `utils/validator.py`'s `validate_name()`: non-empty, at least one
   letter, **and at least two whitespace-separated parts that each
   contain a letter** (a stray punctuation-only "part" left over from
   normalization doesn't count toward the two required). This one shared
   function is the single source of truth for the rule, consumed from
   two independent places that must both apply it — not duplicated
   logic: `NormalizedNameFieldMixin.clean_name()` (`app_account/forms/mixins/`,
   used by `SignUpForm`, `UserUpdateForm`, and the Django Admin's
   `UserAdminCreationForm`/`UserAdminChangeForm` — so this covers
   signup, profile-edit, and admin user creation/editing alike) calls it
   *in addition to* its own pre-existing `len(name) < 3` check (kept,
   not replaced — the two checks aren't fully redundant for pathological
   edge cases, and removing it had no upside); `ContactSerializer`
   (`app_core/api/serializers/`) already had `validators=[validate_name]`
   wired in from the start, so extending the shared function fixed the
   contact form with no code change there at all. The frontend has a
   matching (non-authoritative) client-side check only on
   `ContactPage.tsx` (`hasFullName()`, mirroring the same "≥2
   letter-containing parts" rule) — `SignupPage.tsx` has no equivalent
   new client-side gate, matching this project's existing pattern of not
   touching the shared `useApiForm` hook for a new per-field check;
   backend validation is unchanged as the real enforcement point either
   way.
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

`"NUM_PROXIES": 1` (added 2026-10-17) in the same `REST_FRAMEWORK` dict —
nginx is the sole proxy in front of Django everywhere this app runs
(confirmed via `nginx/nginx.conf`), and it honestly sets
`X-Forwarded-For $proxy_add_x_forwarded_for`. Without this setting, DRF's
`BaseThrottle.get_ident()` falls back to `REMOTE_ADDR`, which behind
nginx is nginx's own container IP for every request — this had silently
made every IP-based throttle above (most importantly `contact`, the only
fully `AllowAny` one) shared across all anonymous visitors. Confirmed
fixed by a dedicated test (`app_core/tests/test_rate_limit.py`) proving a
forged leading `X-Forwarded-For` entry doesn't change the computed
identity, while the real entry nginx itself appended still does.

**Contact also has a second, more precise limit on top of the 5/hour one
above**: exactly 60 seconds must elapse between *accepted* sends (not
merely attempted ones — an invalid submission never starts or consumes
it). This is deliberately a separate mechanism, not a replacement:
`ScopedRateThrottle`'s own `wait()` is an *averaged* distribution over
the remaining hourly quota, which can't express "exact seconds since the
last accepted send." Implemented via `utils/rate_limit.py`'s
`seconds_until_next_allowed(key, interval_seconds)` — a single
`cache.add(key, next_allowed_at, timeout=interval_seconds)` call (Redis
`SET NX EX` under the hood through Django's cache API) as the atomic
"first writer in the window wins" primitive, avoiding a separate
check-then-write race under concurrent requests. `ContactViewSet.create()`
calls this only *after* `ContactSerializer.is_valid()` succeeds, then
`raise Throttled(wait=remaining, code="contact_cooldown")` — reusing
DRF's own exception class so both this and the automatic 5/hour throttle
flow through one `handle_exception()` override (scoped to
`ContactViewSet` only) that reshapes *either* mechanism's resulting 429
into this project's stable-`code` convention:
`{"code", "detail", "retry_after"}`, with `Retry-After` also set
explicitly. Client identity: `utils/rate_limit.get_client_identifier()` —
`"user:<pk>"` for an authenticated request, `"ip:<addr>"` (via
`BaseThrottle().get_ident()`, reusing the `NUM_PROXIES` fix above)
otherwise; never a client-supplied identifier. **If Redis is down, both
mechanisms fail loud** (an unhandled exception, surfacing as a 500) —
deliberately not given new fail-open/fail-closed handling, since they'd
otherwise behave inconsistently with each other under the same outage;
this project's cache-dependent code already has this characteristic
everywhere, not something newly introduced here.

## Addresses (`account.UserAddressModel`, app_address, Django label `address`)

- `app_address/models/{CountryModel,StateModel,CityModel}.py` form a strict
  hierarchy (`Country ← State ← City`), each normalizing its `name` on
  `save()`. Each has a small read-only serializer under
  `app_address/api/serializers/`: `CountrySimpleSerializer` (`id`,
  `name`, `iso_code`), `StateSimpleSerializer` (`id`, `name`, `code`,
  `country`), `CitySimpleSerializer` (`id`, `name`, `state`, `country`
  — the latter resolved via `source="state.country_id"`, not a direct
  field). Two uses: nested inside `UserAddressSerializer` (below) to
  show human-readable names instead of raw FK ids, and — **no longer
  admin-only as of 2026-10-16** — as the response for the small
  staff-only `/api/address/states/`/`/api/address/cities/` endpoints
  that back the admin's own cascading dropdowns (see "Country/state/city
  cascade" below and `api.md`). Country/State/City themselves are still
  only *created/edited* via Django Admin — there is no create/update/
  delete API for the reference data itself, only this read-only
  filtering.
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
    (CASCADE). **Fixed 2026-10-16**: the promotion check used to gate on
    `instance.primary` (the just-deleted Python object's attribute) —
    but Django's admin ModelForm binds submitted field data onto
    `form.instance` *before* calling `.delete()` on a row marked for
    deletion, so an unchecked/omitted `primary` checkbox on the deleted
    row's own form made `instance.primary` read `False` even when it
    really was primary, silently skipping promotion. Now checks the
    actual invariant ("addresses remain but none is primary") instead —
    same fix already applied to `app_product.signals.product_image`.
  - `validate_constraints`/`_get_unique_checks` are overridden so admin
    inline formsets tolerate a transient multi-primary submission (the
    `save()` reorganization resolves it row by row).
  - **Primary-selection admin JS (added 2026-10-16)**:
    `static/src/js/admin/user_address_inline.js`, loaded via
    `UserAddressInlineAdmin.Media.js`, mirrors
    `product_image_inline.js`'s `is_primary` exclusivity listener —
    checking one `primary` checkbox in `#user_addresses-group`
    immediately unchecks every other one in the same group (no reload,
    no submit; persisted only on a real Save). This is UX only — the
    invariant above is what actually enforces it, including with
    JavaScript disabled.
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
- **Country/state/city cascade, admin-only** — scope is deliberately
  narrow since there is no customer-facing address create/edit form to
  extend (see above): the admin form (`UserAddressBaseForm`, shared by
  both `UserAddressAdmin` and `UserAddressInlineAdmin`) is the only
  place this applies. Field order is **Country, State, City** (changed
  2026-10-16 from City/State/Country) — set independently in both
  `UserAddressBaseForm.Meta.fields` (covers the standalone admin, which
  has no `fields` of its own) and `UserAddressInlineAdmin.fields`
  (overrides it for the inline) — same two-places lesson as
  `ProductAdmin.fields`/`ProductForm`.
  - City unambiguously implies state/country via FK
    (`city.state.country`) — no uniqueness constraint on `name` anywhere
    in `CountryModel`/`StateModel`/`CityModel`, so a name-based lookup
    would be ambiguous, but the row's FK chain never is.
  - **Two real bugs fixed 2026-10-16** in the original cascade: (1) the
    `state` field used a plain `forms.Select`, so a freshly-rendered
    state `<option>` had no `data-country` to read — picking a state
    before any AJAX rebuild had happened silently did nothing. Fixed
    with a new `StateLocationSelect` widget
    (`app_address/forms/widgets/StateLocationSelect.py`, mirrors
    `CityLocationSelect`), applied to `UserAddressBaseForm.state`. (2)
    Rebuilding the city list after a state change replaced its
    `<option>`s with ones carrying no `data-state`/`data-country` at
    all (`CitySimpleSerializer` didn't return `state`/`country`), so
    picking one of those rebuilt cities silently stopped syncing its
    state/country — this is why state-first interfered with the
    previously-working city-first flow. Fixed by adding `state` (plus a
    derived `country`, via `source="state.country_id"`) to
    `CitySimpleSerializer`, and generalizing the JS's option-rebuilding
    helper to stamp both attributes on every rebuilt `<option>`
    regardless of whether it's a state or a city row.
  - Current flow, all in `static/src/js/admin/city_location_select.js`:
    picking a **city** reads `data-state`/`data-country` straight off
    its selected `<option>` (now always present, from either widget) and
    sets both parent fields — no request needed. Picking a **state**
    sets its country the same way, then re-fetches the state list for
    that country (keeping the just-picked state selected — it's
    guaranteed to be in that list) and the city list for that state.
    Picking a **country** re-fetches the state list for it, clearing
    state/city if they're no longer compatible, then the city list for
    whatever the (possibly-cleared) state ends up being. A per-field
    request counter discards a response if a newer request for the same
    field has already started, so a fast double-change can't let a
    stale response win — the only ordering hazard that exists, since
    nothing here ever dispatches a synthetic `change` event (so there's
    no event-loop risk to guard against).
  - `app_address/api/viewsets/{StateListViewSet,CityListViewSet}.py`,
    mounted at `/api/address/states/` and `/api/address/cities/`
    (`app_address/urls.py`, registered in `PROJECT/urls.py` — `app_address`
    had no API URLs at all before this). `permission_classes =
    (IsAdminUser,)` (not `AllowAny` like the public product endpoints) —
    these exist solely to back the admin's own dropdowns today, and
    there's no other caller yet. `pagination_class = None`: a cascading
    dropdown needs every matching row at once, not a paginated subset.
  - Server-side validation: `UserAddressBaseForm.clean()` rejects a
    `state` whose `country_id` doesn't match the submitted `country`,
    and a `city` whose `state_id` doesn't match the submitted `state`,
    as field-level errors — so the JS cascade is a UX convenience only,
    never the actual enforcement, per a manually crafted or stale POST.
    `UserAddressFactory` (test fixtures) used to pick `city`/`state`/
    `country` from three *independent* sub-factories — harmless for
    model-level tests, but it meant no factory-created address was
    guaranteed to satisfy this validation; fixed to derive `state`/
    `country` from the chosen `city` via `LazyAttribute`, so fixtures
    are always internally consistent like a real address would be.
- **Responsive inline layout (added 2026-10-16)**: the address inline
  has 10 columns, which made the `TabularInline` row push the whole
  admin page wider than necessary. Fixed with scoped CSS,
  `static/src/css/admin/user_address_inline.css` (loaded via
  `UserAddressInlineAdmin`'s own `class Media`, mirroring
  `markdown_editor.css`'s loading pattern) — caps the widest free-text
  columns' input width, keeps short fields (`number`/`postal_code`)
  narrow, and makes the inline's own table scroll horizontally within
  its card (`overflow-x: auto`, scoped to `#user_addresses-group`) at
  narrow viewports instead of widening the page. Stayed with
  `TabularInline` rather than switching to `StackedInline` — a smaller,
  scoped CSS fix was enough.

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
  doesn't trip the constraint mid-flight). `save()` auto-selects a
  product's **first** image as primary regardless of what was submitted
  (added 2026-10-16, mirrors `UserAddressModel`'s "first address is
  primary" rule — before this, a product could have images with none
  marked primary), locks the parent product row, demotes any other
  primary image if this one is marked primary, then calls
  `organize_product_images()` to renumber `order` with no gaps/duplicates
  — including moving an image to a *different* product (closes the gap on
  the source product too). A `post_delete` signal
  (`app_product/signals/product_image.py`) re-runs the same renumbering
  after deletion and promotes the image now at `order=0` to primary if
  none remains primary. That promotion check is against the *current*
  state of the remaining images (`images.exists() and not
  images.filter(is_primary=True).exists()`), deliberately not against the
  deleted `instance.is_primary` attribute: a discovered, real bug during
  this work was that Django's admin inline formset binds submitted field
  data (including an unchecked/omitted `is_primary` checkbox) onto
  `form.instance` *before* calling `.delete()` on a row marked for
  deletion, so `instance.is_primary` can be stale/wrong at the moment the
  signal fires if that row's own form didn't resubmit a checked box.
- **Product Images admin (`ProductImageInlineAdmin`)**: dynamic JS,
  `static/src/js/admin/product_image_inline.js`, loaded via the inline's
  `Media.js`. Scoped to `#images-group`: checking one `is_primary`
  checkbox client-side unchecks every other one in the same formset
  immediately (no reload); adding a new inline row pre-fills its
  `order` input with `max(visible, non-deleted rows' order) + 1`, not a
  row count, so it stays correct even with mid-formset gaps. Nothing
  here persists anything — the actual invariants are still enforced
  server-side as above, only on a real Save. **Bug fixed 2026-10-16**:
  the "exclude deleted rows from the max" check used
  `row.closest(".dynamic-images")` to find a row's container — but
  confirmed directly against Django's own template
  (`admin/edit_inline/tabular.html`) and `inlines.js`, that class is
  only added to rows *cloned* via "Add another"; an existing,
  already-saved row only ever has class `"form-row"`. So a pre-existing
  row marked for deletion was never actually excluded, giving a wrong
  next position whenever editing a product that already had images
  (the common case). Fixed by matching `.form-row` instead, which is
  present on both existing and newly-added rows.
- **Product admin field order**: `ProductAdmin.fields` (explicit, both
  add and change forms) is `active, category, name, slug, price,
  thumbnail, description` — `slug` is `readonly_fields`, interleaved via
  this explicit tuple rather than left to Django's default of appending
  readonly fields after every editable one. The list page configuration
  (`list_display`/`list_filter`/`search_fields`) is untouched.

## Catalog ordering and randomization (added 2026-10-16)

`ProductSimpleListViewSet` (backs both `/` and `/products` on the frontend —
same endpoint, the homepage just sends no `ordering` param) defaults to a
**deterministic, daily-seeded pseudo-random order**, not `-created_at`
anymore. `get_queryset()` annotates every row with
`MD5(Concat(Cast("id", CharField()), Value(seed)))` where
`seed = timezone.now().date().isoformat()`, and `ordering = ("_shuffle",)`
is the view's default (`StableOrderingFilter` still appends a `pk`
tie-breaker). `_shuffle` is **not** in `ordering_fields`, so an explicit
`?ordering=name|price|created_at|...` from the frontend's sort dropdown
still overrides it exactly as before.

- **Why a daily seed, not per-request or per-session**: `order_by("?")`
  reshuffles every request, breaking pagination (page 2 can repeat/skip
  products relative to page 1) — ruled out. A per-visitor session seed
  gives the same stability but adds real state (session writes, cache
  invalidation) for a catalog this size — not worth it yet. A seed fixed
  per calendar day is stateless, cheap at this scale (no index needed for
  `ORDER BY md5(...)` with a catalog in the tens-to-low-thousands), and
  solves the actual complaint ("a bulk-imported category dominates page 1
  because it's most recent") immediately: a newly-imported batch gets an
  uncorrelated hash the moment it's inserted, not after `created_at` ages
  out. Trade-off: everyone sees the same order on a given day, and it
  fully reshuffles at midnight UTC — revisit with a per-visitor seed only
  if "different shuffle per visitor" becomes an actual requirement.
- Frontend: `frontend/src/components/product/productSort.ts` has a
  `"featured"` sentinel (now `DEFAULT_PRODUCT_SORT`) meaning "send no
  `ordering` param at all" — `ProductListPage.tsx` omits the query param
  entirely for it, letting the backend default apply. It's a real,
  visible option in the sort dropdown (`t.product.sortFeatured`), not just
  an implicit default — existing options (Newest/Price/Name, both
  directions) are unchanged and still explicit overrides.

## Wishlist (`account.UserWishlistModel`/`UserWishlistItemModel`, app_account)

Full-stack as of 2026-10-16: `/api/account/wishlist/` (own list, add,
remove, toggle-privacy, move, check, share-link) and
`/api/account/wishlist/public/<public_id>/` (third-party view, `AllowAny`),
plus `/profile/wishlist` (own page) and `/wishlist/:publicId` (public page)
on the frontend. Admin (`UserWishlistAdmin`/`UserWishlistItemAdmin`, with
an inline for items) still exists as a secondary way to inspect/manage it,
but is no longer the only way.

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
  uniformly. `get_or_create` keeps it idempotent against a double-fire; the
  viewset layer also calls `get_or_create` defensively before add/share-link
  (race-safe: Django retries the `get()` once on a concurrent
  `IntegrityError`), so a legacy/edge-case user without a wishlist row still
  gets one safely on first use.
- **`public_id`** (`UUIDField`, `default=uuid4`, `unique=True`,
  `editable=False`, on `UserWishlistModel`): the opaque handle used in the
  public URL/endpoint. Chosen over the raw numeric `user.id` (would let
  anyone enumerate accounts by incrementing it) and over a name-derived
  slug (`UserModel` has no public-facing identifier at all — no
  username/slug exists anywhere in `app_account`, confirmed by a full grep
  — adding one would have been new, larger scope than this feature needed).
  Added via a hand-written 3-step migration (`0004_...`): nullable column
  → `RunPython` backfill with one fresh UUID per existing row → `AlterField`
  to enforce `unique=True`. A single-step `AddField` would have given every
  pre-existing row the *same* generated UUID (Django computes a callable
  default once for the backfill SQL), which breaks uniqueness on any table
  with more than one row — see Django's own docs on adding a unique field
  with a callable default.
- **`private`** (`BooleanField`, default `False`, on
  `UserWishlistItemModel`): `False` = visible on the public endpoint,
  `True` = owner-only. Enforced at the queryset layer, before
  serialization — `WishlistItemViewSet.get_queryset()` (owner's own view)
  filters only by `wishlist__user=request.user` (includes both), while
  `PublicWishlistSerializer.get_items()` explicitly filters
  `private=False` before handing rows to `PublicWishlistItemSerializer`,
  which has no `private` field at all in its `Meta.fields` — there is no
  field to accidentally leak even if the filter were ever removed.
- **Items**: unlimited per list, but **no duplicate product in the same
  list** — `UniqueConstraint(wishlist, product)`, a real user error
  surfaced as a clear `ModelForm`/`WishlistItemCreateSerializer` validation
  error (not auto-corrected). The same product can appear in different
  users' lists.
- **`position`** (`PositiveIntegerField`, default `0`, 0-based): deliberately
  *not* the task's literal "1 = first" suggestion — `ProductImageModel.order`
  already established an equivalent, 0-based, gap-free pattern in this
  codebase, and reusing that pattern (not inventing a second convention)
  was judged more valuable than matching the literal suggestion (the
  frontend displays `position + 1` as the human-facing "Priority N").
  New items always append to the end (there is no form field for
  `position` on create — admin shows it read-only, and
  `WishlistItemCreateSerializer` doesn't expose it either). Repositioning
  an existing item on create-adjacent paths (`item.position = N;
  item.save()`, e.g. moving it to another wishlist) re-flows all siblings
  gap-free via `organize_wishlist_items()`, a per-app copy of
  `organize_product_images()`'s anchor-insert algorithm (deliberately not
  shared across apps — see `conventions.md`).
  **The `move` (up/down) API action deliberately does NOT reuse
  `organize_wishlist_items()`/`.save()`**: that anchor-insert algorithm
  assumes the *other* items are already gap-free once the anchor is
  excluded, which only holds when the anchor is being freshly inserted
  (create, or moving to a different wishlist). For an in-place move,
  excluding the anchor from an already-contiguous range leaves a gap at
  its *old* slot, and re-inserting it by "first sibling position ≥
  target" silently recomputes the anchor back to its original position for
  an adjacent swap — confirmed by a failing test before this was corrected
  (see `app_account/tests/api/test_wishlist_item_api.py`). `move` instead
  does a plain, explicit two-row position swap with the adjacent sibling,
  inside `transaction.atomic()` with the wishlist row locked
  (`select_for_update`) first — the same locking granularity as every
  other reorganizer in this codebase, just not routed through `.save()`.
  `UniqueConstraint(wishlist, position)` is `Deferrable.DEFERRED` so the
  two-row swap doesn't trip it mid-transaction. A `post_delete` signal
  (`reorganize_wishlist_items_after_delete.py`) closes the gap after a
  deletion — mirroring `app_product.signals.product_image` exactly; this
  signal already existed before this feature and needed no changes.
- **Frontend**: `/profile/wishlist` (`WishlistPage.tsx`) shows the owner's
  full list (public + private), move up/down buttons (showing a plain
  position number, `item.position + 1`, with the "Priority N" text only
  as an `aria-label` — not visible text, per user feedback 2026-10-16), a
  public/private toggle, delete, an inert "Add to cart" button, and a
  "copy my wishlist link" action (`/account/wishlist/share-link/`).
  `/wishlist/:publicId` (`PublicWishlistPage.tsx`) shows only public
  items, no edit/delete/privacy controls, and an inert "Give as a gift"
  button — **for anyone anonymous or not the owner**. Its priority number
  is **re-derived from the visible items' own order (array index + 1),
  not `item.position + 1`** (changed 2026-10-17, per user feedback) —
  `position` lives in the same numbering space as the owner's hidden
  private items, so once those are filtered out server-side the public
  list's positions can have gaps (e.g. 0, 2, 3); showing those raw
  numbers would look broken to a non-owner. `WishlistPage.tsx` (the
  owner's own view) still uses `item.position + 1` directly, since that
  list always includes every item and genuinely has no gaps. **If the
  signed-in visitor turns out to own this exact `public_id`** (checked in
  the background via `/account/wishlist/share-link/`, compared against
  the URL param — added 2026-10-16 per user feedback), `PublicWishlistPage`
  swaps to rendering `WishlistPage`
  directly instead, so the owner visiting their own share link gets the
  full editable view with private items, not the restricted public one.
  This check starts as `false` and only flips in the background — an
  anonymous or different-user visitor sees the public view immediately,
  with no added request and no behavior change, and the real data
  boundary is still the backend: `/account/wishlist/public/...` itself
  never returns private items to anyone regardless of this check, so a
  wrong/bypassed frontend decision here can't leak anything — it would
  just show the wrong *view*, not wrong *data*. **Both wishlist pages
  have a "Sort by" dropdown** (added 2026-10-17, per user feedback asking
  for something "semelhante à lista de produtos" — the product list's
  sort, `ProductSortSelect.tsx`/`productSort.ts`): name A-Z/Z-A, price
  low-high/high-low, date added oldest/newest-first, plus a `"priority"`
  default meaning "no secondary sort — show the stored order as-is."
  **This is a pure client-side sort**
  (`frontend/src/components/wishlist/wishlistSort.ts`'s `sortWishlistItems`),
  deliberately *not* mirroring the product list's server-side `ordering`
  query param — the whole wishlist is already fetched in one request (no
  pagination), so there's nothing to gain from a round trip, and no
  backend changes were needed. While any sort other than `"priority"` is
  active on the owner's own page, the move up/down buttons are disabled
  (`moveDisabled` prop on `WishlistItemRow`) — moving an item by priority
  only makes sense while the list is actually displayed in priority
  order, and the owner's `index === 0`/`isLast` boundary checks are
  computed against the *unsorted* array (`sortWishlistItems` returns the
  same array, same reference, for `"priority"`), so they stay correct
  once sorting is switched back. `ProductDetailPage.tsx`'s
  wishlist button checks real membership via `/account/wishlist/check/`
  on load (only when authenticated) and toggles between "Add to
  wishlist"/"Remove from wishlist" after a successful backend response;
  guests see a link to `/login?next=...` instead of a dead button. "Add
  to cart" and "Give as a gift" are explicitly visual-only per the
  original task's scope — no cart/order/payment logic exists.

## Shopping cart / checkout — confirmed absent

A repository-wide search (backend and frontend) found **no cart, order, or
checkout implementation anywhere**:

- Backend: no `Cart`/`CartItem`/`Order` model, serializer, viewset, or URL.
- Frontend: the cart link in `Navbar.tsx` is a dead `<a href="#">` with no
  handler; the "Add to cart" button on `ProductDetailPage.tsx` and the
  wishlist page both have inert "Add to cart" buttons; `UserMenu.tsx`'s
  "orders" item is still an inert button with an explicit code comment
  acknowledging it's "reserved for when it exists" — **addresses and
  wishlist are no longer in this category** (both have real pages/API now,
  see the Wishlist section above and `../memory/changelog.md`). Translation
  strings for cart exist in every locale, but there is zero state, API, or
  routing behind it.

Treat any task that assumes a working cart as requiring that feature to be
built from scratch, not extended.

## Internationalization — backend/frontend status

The frontend's custom i18n (`frontend/src/i18n/`) has genuine, idiomatic
translations for all five required languages (English, Portuguese,
Spanish, French, Italian — confirmed by distinct content, not
copy-pasted stubs). The backend's Django `LANGUAGES` setting
(`PROJECT/settings/internationalization.py`) **as of 2026-10-18 declares
all five** (`pt-br`, `en`, `es`, `fr`, `it`) — previously it only declared
`pt-br`/`en`/`es`, which silently made French/Italian backend requests
fall back to `LANGUAGE_CODE` (English) regardless of `Accept-Language`,
confirmed via a direct HTTP request (even Django's own built-in messages,
e.g. password validators, stayed in English for `fr`/`it` before this
fix — proof it was `LocaleMiddleware` never activating those locales at
all, not a catalog-content problem). `locale/fr/` and `locale/it/`
gettext catalog directories already existed on disk with real content;
only the `LANGUAGES` declaration was missing. Additionally, the actual
`.po` catalogs remain very sparse — only 7 real translatable strings are
marked for translation across all five languages combined (confirmed by
reading `locale/en/LC_MESSAGES/django.po` in full). Most user-facing
backend strings have not yet been wrapped for translation — any such
string will render in English for every locale until it's added to all
5 catalogs (see `conventions.md` for the i18n convention to follow when
adding new translatable strings). Note also: Django's own shipped `it`
translation catalog is itself incomplete for at least one built-in
password-validator message (confirmed: "This password is too short..."
stayed in English for `Accept-Language: it` even after enabling the
locale) — this is an upstream Django/library gap, not something fixable
in this project's own catalogs.

## Calculations

No business calculations beyond straightforward field validation were
found. `ProductModel.price` is a plain `DecimalField` validated by
`validate_positive_decimal` (must be `> 0`); there is no tax, discount,
shipping, or total computation anywhere in the codebase (consistent with
there being no cart/checkout). If pricing logic is added later, document it
here.
