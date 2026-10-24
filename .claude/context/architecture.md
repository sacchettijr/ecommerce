# Architecture

## High-level shape

```
Browser
   │
   ▼
Nginx (reverse proxy, TLS termination)
   ├── /              → React/Vite dev server (frontend container)
   ├── /api/, /admin/, /__debug__/   → Django (Gunicorn, backend container)
   ├── /static/        → collected static files (named volume, read directly)
   └── /media/         → uploaded media (named volume, read directly)

Django ── PostgreSQL (data)
       ── Redis (cache + Celery result backend)
       ── RabbitMQ (Celery broker) ── Celery worker (3 background email tasks)
```

**Backend has no autoreload.** `ecommerce_django` runs
`gunicorn PROJECT.wsgi:application --workers 3` (confirmed via the
container's actual process, not `manage.py runserver`) — it does **not**
pick up Python source changes on its own, even though the source
directory is bind-mounted. After any backend code change, `docker compose
restart backend` (or `docker restart ecommerce_django`) is required
before the change is live; forgetting this is a real, already-hit
failure mode (see `../memory/known_issues.md`). The frontend container
(`ecommerce_frontend`) is the opposite — a Vite dev server with HMR, so
frontend edits apply immediately with no restart.

Locally, this is `docker-compose.yml`. On Render, Nginx's job is done by the
static site's `routes:` rewrites in `render.yaml`, and there is no
Redis/RabbitMQ/Celery/CloudBeaver/Nginx service at all (see
`dependencies.md` and `docs/render.md`) — emails silently don't send on
Render today, by explicit documented tradeoff, not by accident.

## Request/response boundaries

- **Frontend never talks to Postgres/Redis/RabbitMQ directly** — all data
  access goes through the DRF API.
- **Django views/viewsets stay thin.** Business logic that must hold
  regardless of caller lives in models (`save()` overrides, `Meta.constraints`)
  or signals, not in viewsets/serializers — see `ProductImageModel`
  (`app_product/models/ProductImageModel.py`) as the project's best example of
  this pattern. `UserAddressModel.save()` plus
  `app_account/signals/promote_primary_address_after_delete.py` follow the
  same pattern for the primary-address invariant (see `domain.md`) —
  `UserAddressViewSet.set_primary` is a thin wrapper that just calls
  `.save()`, with zero invariant logic of its own.
  `UserWishlistItemModel.save()` plus `app_account/signals/
  reorganize_wishlist_items_after_delete.py` follow the same `save()`+
  `post_delete`-signal split for its gap-free `position` field, mirroring
  `ProductImageModel`'s `order`/`app_product.signals.product_image.py`
  pair directly (see `domain.md`). `app_account/signals/
  create_wishlist_for_new_user.py` (a `post_save` receiver on `UserModel`)
  is the reference example for "must happen on every creation path
  regardless of caller" — a signal connected once in `AppConfig.ready()`,
  not a service function every call site would need to remember to invoke.
- **Celery tasks are dispatch-and-forget from the caller's perspective.**
  `utils/dispatch_task.py` wraps every Celery dispatch in a try/except that
  logs and swallows broker-connection failures — callers (viewsets) always
  get a success response regardless of whether the task was actually
  queued. This is intentional, documented in `PROJECT/settings/celery.py`'s
  comments, and lets the app run (with silently-unsent email) even without
  RabbitMQ configured — e.g. on Render today.
- **Audit fields are populated via middleware + thread-local, not explicit
  passing.** `app_core.models.BaseModel.save()` reads the current user from
  `utils.current_user.get_current_user()`, which
  `app_account/middleware/CurrentUserMiddleware.py` sets per-request. Keep this
  in mind if you ever run model `save()` outside a normal request (e.g. a
  management command or Celery task) — `created_by`/`updated_by` will be
  `None` there unless you set the thread-local yourself.

## Frontend architecture

- No global state-management or data-fetching library. Data fetching is
  hand-rolled via a single generic hook, `useAsync` (`frontend/src/hooks/useAsync.ts`),
  used by every page that calls the API. Two small React Contexts
  (`AuthProvider`, `CategoriesProvider`) hold the only genuinely global
  client state (session user, category list).
- `frontend/src/api/client.ts` is the single chokepoint for all HTTP calls
  — a `request<T>()` wrapper handles credentials, CSRF, `Accept-Language`,
  and error normalization into a typed `ApiError`. New API calls should go
  through this wrapper (via small per-domain modules like `products.ts`,
  `auth.ts`), not ad-hoc `fetch()` calls in components.
- **Route guarding**: `frontend/src/auth/ProtectedRoute.tsx` wraps
  account-only routes (`/profile`, `/profile/edit`, `/profile/password`,
  `/profile/addresses` in `App.tsx`).
  It only blocks the authenticated page from flashing before a redirect
  to `/login?next=...` (reusing the existing `withNext`/`safeNext`
  convention) — the real enforcement is still the backend requiring a
  valid session for any endpoint that returns private data. Add new
  account-only routes by wrapping them the same way, not by inventing a
  second guard mechanism.
- **Authenticated account area**: `frontend/src/components/account/AccountLayout.tsx`
  is the shared layout for account-only pages
  (`frontend/src/pages/ProfilePage.tsx` at `/profile`,
  `frontend/src/pages/ProfileEditPage.tsx` at `/profile/edit`,
  `frontend/src/pages/PasswordChangePage.tsx` at `/profile/password`,
  `frontend/src/pages/AddressListPage.tsx` at `/profile/addresses`,
  `frontend/src/pages/WishlistPage.tsx` at `/profile/wishlist`) — a
  sidebar nav (reusing `userMenu.*` translation keys, mirroring
  `UserMenu.tsx`'s dropdown items) plus a content region and a
  message/alert area. A future "orders" page (doesn't exist yet) should
  nest inside this layout the same way, rather than duplicating its
  sidebar or message handling.
- **Local-override pattern for a fetched list the UI also mutates**:
  `AddressListPage.tsx` is the reference — `useAsync(fetchUserAddresses, undefined)`
  supplies the initial load, and a local `override` state (same shape as
  `AuthProvider`'s own `override`) takes precedence once the user
  switches their primary address, set directly from the mutation
  endpoint's response rather than re-fetching. Combined with a
  `requestTokenRef` (incremented per selection, compared on response —
  a response whose token no longer matches the latest is discarded) and
  an `AbortController` (the previous in-flight request is aborted when a
  new one starts, reusing `apiPost`'s existing optional `AbortSignal`
  parameter), this is how a rapid "select A, then immediately select B"
  sequence resolves to B's authoritative result without A's late
  response corrupting it — see `domain.md` for how the backend's own
  locking makes the *data* consistent regardless of request arrival
  order; this is what keeps the *frontend* from displaying something
  inconsistent with whatever the backend ends up persisting.
- **Accessible tooltip for icon-only controls**: `frontend/src/components/ui/Tooltip.tsx`
  wraps a single trigger element, injecting `aria-describedby` onto it
  (via `cloneElement`) and showing a floating label on both
  `group-hover` and `group-focus-within` (so it works for mouse and
  keyboard alike). First introduced for `AddressListPage.tsx`'s
  Add/Edit/Delete icon buttons — reuse it for any future icon-only
  control rather than a one-off implementation.
- **Inert-but-focusable controls use `aria-disabled`, never the native
  `disabled` attribute.** A natively `disabled` button cannot receive
  keyboard focus, which would make it impossible for a keyboard user to
  ever see its tooltip — `aria-disabled="true"` keeps it focusable while
  still being unambiguously non-interactive (no `onClick` is attached at
  all, rather than attaching a no-op one). See `AddressListPage.tsx`'s
  Add/Edit/Delete buttons.
- **Refreshing the current-user state after a write**: `ProfileEditPage.tsx`
  is the reference for this — on success it calls `setUser(freshUser)`
  (from `useAuth()`) with the backend's response, which is the *same*
  `AuthContext` state `AuthProvider`/`LoginPage`/`UserMenu`'s logout
  already mutate. This propagates everywhere reactively (navbar greeting,
  `ProfilePage`) with no second fetch, no reload, and no second source of
  truth for the current user's data. Follow this pattern for any future
  page that mutates the current user.
- **Action-scoped message/alert state**: `frontend/src/hooks/useMessages.ts`
  returns `{ messages, beginAction, replaceMessages, dismissMessage }` —
  the closest equivalent to Django's `messages` framework this project
  has, but scoped to one user action at a time rather than accumulating
  forever. Call `beginAction()` when a new attempt starts (e.g. a form
  submit) — it clears whatever the previous action left on screen and
  returns a token — then call `replaceMessages(token, [...])` once that
  attempt's outcome is known, with every message it produced (zero, one,
  or several of different variants, all shown together). A
  `replaceMessages` call carrying a token from an action that's no longer
  current is silently ignored, so a late response from a superseded
  submission can never resurrect a stale notification. See
  `PasswordChangePage.tsx` for the reference usage, including reacting to
  `useApiForm`'s own general-error state via a `useEffect` (necessary
  because reading that state synchronously right after `await
  form.submit(...)` would be stale — React hasn't re-rendered yet at that
  point in the same event handler). `components/ui/Alert.tsx` supports an
  optional `onDismiss`/`dismissLabel` pair (discriminated union: both or
  neither) for the dismiss button these render with.
- **Phone input has a country/DDI selector and a dynamic per-country mask**
  (added 2026-10-17, replacing the old letter-stripping-only
  `sanitizePhoneInput.ts`, now deleted). `frontend/src/components/ui/PhoneInput.tsx`
  is shared by `SignupPage.tsx`, `ProfileEditPage.tsx`, and `ContactPage.tsx`
  — all three previously had independent, inconsistent phone handling
  (Contact didn't even sanitize). Built on `libphonenumber-js/min` (the JS
  port of the same canonical metadata `django-phonenumber-field`/
  `phonenumbers` already uses server-side) rather than a prebuilt UI
  widget, keeping with this project's hand-rolled-input convention
  (`TextField`/`FormField`). Internally tracks `country`/national-digits
  as its own state (seeded from the incoming E.164 `value`, defaulting to
  `"BR"` when empty — matching the backend's `PHONENUMBER_DEFAULT_REGION`
  default); the displayed mask comes from `AsYouType(country).input(digits)`,
  and the value emitted to the parent is that same formatter's
  `.getNumber()?.number` (falling back to a plain concatenation while
  there aren't yet enough digits). Country names use `Intl.DisplayNames`
  keyed to the current UI language — no static country-name list to
  maintain. The backend's `PhoneNumberField`/validators remain the real
  format authority regardless of this frontend formatting.
- **The country selector only offers the countries this site currently
  serves** (updated 2026-10-17, same day as the above, per direct user
  feedback): a fixed `SUPPORTED_COUNTRIES = ["BR", "US", "FR", "IT"]` in
  `PhoneInput.tsx`, not the full ITU list `getCountries()` would return —
  display names are still derived via `Intl.DisplayNames`, just restricted
  to these four codes. If an existing stored `value` ever parses to a
  country outside this set, the component falls back to `"BR"`.
  **Per-country max length is enforced while typing** via
  `libphonenumber-js/min`'s own `validatePhoneNumberLength(digits,
  country)` (trimming trailing digits until it stops returning
  `"TOO_LONG"`) — not a hand-maintained max-digits table, so it stays
  correct even for a country like Italy whose national numbers vary in
  length by type. Confirmed one pre-existing, out-of-scope cosmetic quirk
  while verifying this: France's `AsYouType` mask only groups into
  "XX XX XX XX XX" when fed a leading national trunk `0`, which this
  component doesn't add — so the French display shows ungrouped digits
  (still a correct, valid number) rather than a spaced mask. Not fixed,
  since it wasn't reported; flagged for a future task if wanted.
- **The country picker is a flag-only `Dropdown`, not a native `<select>`**
  (changed 2026-10-17, later the same day, per direct user feedback — a
  native `<select>`'s own collapsed display can only ever show its
  selected `<option>`'s plain text, never an `<img>`, so showing just a
  flag instead of the full country name requires a custom trigger).
  Mirrors `LanguagePicker.tsx` exactly: a button showing just the current
  country's flag (`<img alt="Country code: <name> (+<code>)">`, so the
  accessible name still carries the full context even though only the
  flag is visible), opening a menu of the 4 supported countries with
  flag + name + calling code each. Reuses the **exact same flag image
  files** the language switcher already ships
  (`frontend/src/i18n/languages.ts`'s `/img/locale/*.png`) via a small
  `COUNTRY_FLAGS` map in `PhoneInput.tsx` — `BR→pt-br.png`, `US→en.png`,
  `FR→fr.png`, `IT→it.png` — not a second flag asset set and not emoji
  (flag emoji render as plain two-letter codes on some platforms,
  notably Windows, which was the reason emoji were dropped). Required
  one small, backward-compatible change to the shared `Dropdown.tsx`:
  a new optional `buttonClassName` prop (defaulting to the exact
  hardcoded classes `UserMenu.tsx`/`LanguagePicker.tsx` already relied
  on, so neither needed to change) — `PhoneInput.tsx` passes a
  light-background-appropriate className instead, since `Dropdown`'s
  default styling (`text-gray-300`/`hover:text-white`) assumes the
  navbar's dark background and would be nearly invisible on a form.
  **Selecting a country now always clears the phone number field**
  (changed from the original "preserve and re-clamp the digits"
  behavior, same user feedback) — a different country's number isn't a
  truncated/extended version of the old one, and carrying over stale
  digits was producing confusing, hard-to-predict results; the user must
  retype after switching.
- **Responsive layout fix** (same feedback): the old native `<select>`
  inherited `inputClassName()`'s own `w-full` — which, depending on
  Tailwind's internal utility ordering in the generated stylesheet, could
  outrank the `w-32`/`sm:w-44` override meant to constrain it, making the
  select expand to fill the entire row and push the phone number input
  off-screen on narrow viewports. The new Dropdown-button trigger doesn't
  use `inputClassName` at all (sized to its own content — just the flag),
  removing that conflict outright; the phone `<input>` also gained
  `min-w-0` alongside its existing `flex-1`, since a flex item's default
  `min-width: auto` prevents it from ever shrinking below its own
  intrinsic content width, which is the other half of what let the row
  overflow a narrow screen.
- **The phone field's placeholder changes with the selected country**
  (same day, third follow-up). `PhoneInput.tsx` no longer accepts a
  `placeholder` prop at all — the old static, BR-formatted i18n strings
  (`auth.phonePlaceholder`/`contact.phonePlaceholder`) were deleted from
  `i18n/types.ts` and all 5 locales as genuinely dead once every call
  site stopped passing them. Instead, a small internal
  `PLACEHOLDER_DIGITS` map (one representative national number per
  supported country) is run through the *same* `AsYouType(country)`
  formatter the real mask uses, so the example shown always matches the
  actual mask rather than a hand-typed format string that could drift
  from it — e.g. Brazil shows `(69) 99123-4567`, the US shows
  `(202) 555-1234`. These are placeholder digit patterns, not translated
  text, so they don't need an i18n entry.
- **`useApiForm.generalErrors` is memoized** (`frontend/src/hooks/useApiForm.ts`,
  `useMemo` keyed on the underlying `generalMessages` state and the
  current language) — its reference only changes when the error state
  genuinely changes. This matters if you ever put it in a `useEffect`
  dependency array: before this was memoized, a naive effect depending on
  it looped forever (new array reference every render → effect refires →
  triggers another render → ad infinitum), a real bug hit and fixed while
  building the password-change notification flow.

## Design decisions worth preserving

- **IDs, not slugs, for FKs; slugs for public URLs.** Products/categories
  expose `slug` publicly but are still looked up and related by integer PK
  internally.
- **`FRONTEND_URL` is the single source of truth for "where the React app
  is reachable right now."** Used for CORS, email links, and
  `get_absolute_url()` on `ProductModel`/`ProductCategoryModel`. There is
  deliberately no separate `BACKEND_URL` variable — Django never needs to
  know its own public URL; it uses `request.build_absolute_uri()`, and the
  frontend has `VITE_API_URL` for the same purpose from its side. Keep this
  single-variable-per-concern approach rather than reintroducing a second
  "public URL" setting.
- **Nginx is the only service meant to be publicly reachable** once it's
  active — `backend`/`frontend` ports are intentionally `expose`-only
  (internal to the Docker network) with commented-out `ports:` entries and
  an explanatory comment for how to re-enable direct-port testing. Several
  *other* services (Postgres, Redis, RabbitMQ, CloudBeaver) are currently
  still host-published — see `security.md` for why that's worth revisiting
  before this is ever run on a non-isolated host.
- **Deterministic pseudo-random ordering via a date-seeded SQL hash, not
  `order_by("?")` or a stored random column.** `ProductSimpleListViewSet`
  (2026-10-16) is the reference example — see `domain.md`'s "Catalog
  ordering and randomization." Reuse this `MD5(Concat(Cast(...), Value(seed)))`
  pattern for any future "varied but pagination-stable" ordering need
  instead of reaching for per-request randomness or a new persisted field.
- **Django Admin JS in this project is plain vanilla JS (no jQuery), using
  Django's native `CustomEvent`s** (`formset:added`/`formset:removed`,
  confirmed dispatched as real DOM events, not jQuery events, in this
  project's installed Django 6.1.1) **for dynamic inline-formset behavior** —
  see `static/src/js/admin/product_image_inline.js` (2026-10-16) and the
  pre-existing `city_location_select.js`/`product_slug_preview.js`. Don't
  introduce jQuery or `django.jQuery` for new admin JS; match this style.
