# Changelog

Historical entries below are reconstructed only from `git log` (9 commits
total at the time of writing — this is confirmed, not an abbreviated
sample) plus this session's own configuration work. Where git history
doesn't provide enough detail to describe *what* changed, that limitation
is stated explicitly rather than guessed.

## From git history (oldest → newest, by commit message only)

- `ff5919b` — Reworking the project to adapt it for deployment to Render.
- `9e5fd39` — The project has been adapted for rendering with Docker.
- `0d5f3b9` — Render adaptation test.
- `13d7c01` — Removed "backend" from the path (the repo was restructured
  from a `backend/`-prefixed layout to Django living at the repo root;
  this is the change that later made `README.md`/`docs/render.md`'s
  `backend/`-prefixed instructions stale — see `known_issues.md`).
- `513382b` — Testing with Nginx paused due to conflicts with the public
  IP address.
- `6d3bbb1` — Website communication via public IP working with HTTP;
  verified to function securely (HTTPS).
- `bf2fa80` — HTTPS connection working with certificate generation.
- `2304b49` — Added the model and forms related to user addresses
  (`UserAddressModel` + `UserAddress*Form`s — later found to be unwired,
  see `known_issues.md`).
- `2e0dc88` (HEAD at analysis time) — Bypassed a Docker build permission
  issue; removed an SSL-permission check from the `DEBUG` gate.

## 2026-10-11 — Full repository analysis and `.claude/` configuration rewrite

Performed a comprehensive, verified (not assumed) analysis of the entire
repository — backend (Django apps, settings, API, auth lifecycle, Celery),
frontend (React/TS structure, routing, API integration, i18n, styling),
infrastructure (Docker Compose, Dockerfiles, Nginx, Render, service
configs), testing/quality tooling, and the pre-existing `.claude/`
configuration, dependencies, and git history — using 5 parallel read-only
investigations, then synthesized the findings into this `.claude/`
directory.

**What was found:** the entire `.claude/commands/`, `.claude/context/`,
and `.claude/memory/` trees were empty placeholder files (0 bytes each);
`.claude/CLAUDE.md` (609 lines, uncommitted) was substantially accurate
but repeated a `backend/`-subdirectory path error in 4 places, matching
the same error already present in `README.md`/`docs/render.md`.
`.claude/settings.json` was accurate and was left unchanged.

**What changed:**
- Rewrote `.claude/CLAUDE.md`: fixed every `backend/`-prefixed path
  reference, trimmed detailed content out to the new `.claude/context/`
  files it now points to, kept the essential project-wide rules.
- Wrote all 13 `.claude/context/*.md` files from scratch, grounded in the
  verified findings (see each file for specifics).
- Wrote all 8 `.claude/commands/*.md` files from scratch.
- Wrote this file, `current_task.md`, and `known_issues.md` from scratch.
- Did not modify any application source code, `README.md`,
  `docs/render.md`, dependency manifests, Docker/deployment configuration,
  or `.claude/settings.json` — all out of scope for this task (fixing the
  `backend/`-path error in `README.md`/`docs/render.md` is recorded as a
  recommendation in `current_task.md`, not performed).

No code, tests, dependencies, or Docker/Git state were modified as part
of this task — it was configuration/documentation only.

## 2026-10-11 — Wired `UserAddressModel` admin + model-level exclusivity

Found `account/admin/UserAddressAdmin.py` and `UserAddressInlineAdmin.py`
had drifted to reference fields that don't exist on the model (`address`,
`zip_code`, `is_primary` instead of the real `street`/`postal_code`/
`primary`) — `manage.py check` was failing outright (`admin.E108`).

- `account/models/UserAddressModel.py`: added `save()` (locks the parent
  user row, demotes any other `primary=True` address for the same user —
  mirrors `ProductImageModel.save()`), plus `validate_constraints`/
  `_get_unique_checks` overrides so admin inline formsets tolerate a
  transient multi-primary submission before the model reorganizes it.
- `account/forms/UserAddressBaseForm.py`: simplified — removed the
  custom `save()`/`__init__` (admin never actually invoked
  `form.save(commit=True)`, so that logic was silently dead in the admin
  path; the model now owns the rule for every caller). `user` added to
  `Meta.fields` for the standalone admin.
- `account/admin/UserAddressAdmin.py`: fixed `list_display`/`list_filter`/
  `search_fields` to real fields; added `get_form()` to use
  `UserAddressCreateForm`/`UserAddressUpdateForm` for add vs change.
- `account/admin/UserAddressInlineAdmin.py`: fixed `fields`; wired to
  `UserAddressBaseForm`.
- `account/admin/UserAdmin.py`: added `inlines = (UserAddressInlineAdmin,)`.

Verified: `manage.py check`/`makemigrations --check` clean, full `pytest`
(104 passed), ruff/mypy/basedpyright clean, and a real end-to-end HTTP
test against the running admin (login, open a user's change page,
submit two inline address rows both marked `primary=True` in one
request) confirmed exactly one ends up primary. No migration was needed
(pure behavior change, the DB constraint already existed). Updated
`.claude/memory/known_issues.md` to mark the "dead address forms" entry
resolved.

## 2026-10-13 — Completed the `app_` prefix rename for all 4 Django apps

Directories had already been renamed (`core→app_core`, `account→app_account`,
`product→app_product`, `address→app_address`) and `INSTALLED_APPS` updated
before this task started, but every app's `AppConfig.name` still said the
old bare name — Django failed to boot (`ImproperlyConfigured: Cannot
import 'core'`). Fixed `name =` on all 4 `AppConfig`s to the new package
path and added an explicit `label =` set to the **old** short name on
each, preserving `AUTH_USER_MODEL = "account.UserModel"`, `ContentType`/
`Permission` rows, and the pre-existing (locally-present, still
git-ignored per the known migrations issue) migration files' `dependencies`
tuples — confirmed via `makemigrations --check --dry-run` reporting "No
changes detected" against those same files after the rename.

Fixed every real Python import path found via systematic repo-wide grep:
`app_account/models/UserAddressModel.py`, `app_address/models/*.py`,
`app_account/models/UserModel.py` (cross-app imports),
`app_product/apps.py`'s `import_module()`, `PROJECT/urls.py`'s
`include()` calls, `PROJECT/settings/authentication.py`'s
`AUTHENTICATION_BACKENDS`, `PROJECT/settings/middleware.py`'s
`MIDDLEWARE`, `PROJECT/settings/rest_framework.py`'s
`DEFAULT_PAGINATION_CLASS`, `pyproject.toml`'s `[tool.pyright] include`,
and a `unittest.mock.patch()` target string plus two task-name
assertions in `app_account/tests/api/test_auth_api.py`. Updated the
Celery task-name strings in `app_account/emails/send_verification_email.py`
and `app_account/tasks/send_email_verification_email.py` to match (an
arbitrary dispatch-by-name string, not an app-label reference, so no
compatibility reason to keep the old value). Left `AUTH_USER_MODEL`,
`UserAddressModel.user`'s `to="account.UserModel"`, and
`data/init_data_*.json`'s `"address.*"` fixture-model keys unchanged —
confirmed these are `app_label.ModelName` references, not Python import
paths.

Verified: `manage.py check`, `makemigrations --check --dry-run`, full
`pytest` (104 passed, unchanged count), `ruff`, `mypy`, `basedpyright` —
all clean. Live HTTP checks through Nginx confirmed all 4 apps' routes
respond correctly. Updated every affected `.claude/context/*.md` file,
`.claude/CLAUDE.md`, and two `.claude/commands/*.md` files to the new
package names with the label-preservation note. Fixed one incidental
documentation inaccuracy in `README.md`'s structure tree.

## 2026-10-13 — Verified `data/init_data_*.json` fixtures need no change

Checked, on request, whether the `app_` rename required updating the
`"model": "address.countrymodel"` / `"address.statemodel"` /
`"address.citymodel"` keys in `data/init_data_{Country,State,City}Model.json`.
Confirmed via `apps.get_app_config("address")` that the label `address`
still resolves to the `app_address` package (as designed — see the
previous entry), then actually ran `manage.py loaddata` with all three
files against the running database: all 5,650 objects installed with no
error, counts matched (2 countries, 77 states, 5,571 cities), and
`manage.py check` stayed clean. No fixture changes were needed or made.

## 2026-10-13 — Authenticated user layout + profile home page

Migrated the legacy Django-template authenticated-user experience
(`frontend.old/accounts/profile_base.html`/`profile_detail.html`, read
only, not modified) to the current React frontend, reusing existing
architecture rather than inventing a new one.

**Backend**: extended `app_account/api/serializers/UserSerializer.py`
(the single current-user serializer, used by `SessionViewSet` at
`/api/account/session/`) to also expose `date_birth`, `phone`,
`created_at` (all read-only) — no new endpoint was created, per the
explicit instruction to avoid duplicate user-state sources. Verified the
exact serialized shape via Django shell (`phone` is always `""` when
unset, never `null`; `created_at` can be `null` on old rows per the
model's `null=True`).

**Frontend**, all new unless noted:
- `frontend/src/api/types.ts` (modified): `SessionUser` extended to match.
- `frontend/src/components/ui/icons.tsx` (modified): added `UserIcon`,
  `PencilIcon`, `LockClosedIcon`, `ArchiveBoxIcon`.
- `frontend/src/components/ui/Alert.tsx` (modified): optional
  `onDismiss`/`dismissLabel` pair (discriminated union, both-or-neither)
  for dismissible alerts; existing callers unaffected.
- `frontend/src/hooks/useMessages.ts`: small reusable per-page message
  queue hook (`{ messages, addMessage, dismissMessage }`).
- `frontend/src/auth/ProtectedRoute.tsx`: route guard reusing the
  existing `withNext`/`safeNext` redirect-preservation convention;
  redirects unauthenticated users to `/login?next=...`. The real
  enforcement remains the backend requiring a session.
- `frontend/src/components/account/AccountLayout.tsx`: reusable
  authenticated-area layout — sidebar nav (reuses `userMenu.*`
  translation keys/icons, only "Profile" is a real link; edit
  profile/change password/orders/addresses/wishlist render as inert
  items since no pages exist for them, matching `UserMenu.tsx`'s own
  existing treatment of the same items) + content region + message/alert
  area.
- `frontend/src/pages/ProfilePage.tsx`: profile home page, rendered
  inside `AccountLayout`, sourced only from `useAuth().user` (never a
  client-supplied id). Shows name/email/date of birth/phone (or "not
  provided")/account-creation date; `is_staff` renders a badge only when
  `true` (nothing rendered when `false`). Handles the auth-loading state
  and the defensive "no user" state (shouldn't normally occur, since the
  route is guarded) without fabricating data.
- `frontend/src/App.tsx` (modified): registered `path="profile"` wrapped
  in `ProtectedRoute`.
- `frontend/src/components/layout/UserMenu.tsx` (modified): wired the
  "Perfil" dropdown item to navigate to `/profile` (previously inert);
  the other items remain inert, unchanged.
- `frontend/src/i18n/types.ts` + all 5 locale files (modified): added
  `common.dismiss`, `account.navAriaLabel`, and the full `profile.*`
  section — all 5 languages fully translated, not stubs.

**Tests**: updated the one existing backend test asserting the exact
`/api/account/session/` payload shape
(`app_account/tests/api/test_auth_api.py::test_session_returns_the_logged_in_user`)
to include the 3 new fields, converting `created_at` through
`django.utils.timezone.localtime()` to match DRF's serialized offset
(the in-memory model instance holds it in UTC; the API serializes it in
the configured local timezone). No frontend tests were added —
explicitly asked and the user chose to defer installing a frontend test
framework rather than do so as part of this task (see
`known_issues.md`).

**Validation**: `tsc -b`, `eslint .`, `npm run build` (frontend);
`manage.py check`, `makemigrations --check --dry-run` (no changes
needed), full `pytest` (104 passed), `ruff check`/`ruff format --check`,
`mypy`, `basedpyright` (backend) — all clean.

## 2026-10-13 — Fixed a live blank-screen bug on `/profile`

The user reported `https://177.222.210.50/profile` showing the navbar
briefly, then going blank. Root cause: `ecommerce_django` runs Gunicorn
with no autoreload (see `architecture.md`), so it kept serving the
pre-extension `UserSerializer` (missing `date_birth`/`phone`/`created_at`)
even though the source file on disk was already correct — `docker exec
... pytest`/shell checks run fresh processes and didn't surface this,
since only the long-running Gunicorn workers were stale. The frontend
trusted those fields to always be present (per the `SessionUser` type)
and threw inside `ProfilePage.tsx`'s `parseDateBirth` when they were
silently absent, crashing the whole React tree (no error boundary
exists) into a blank page. Fixed with `docker compose restart backend`.
Reproduced the failure and verified the fix end-to-end with a real
Playwright (Edge) browser session against the live `https://177.222.210.50`
site, logging in as a throwaway test user (created and deleted via
Django shell) and confirming `/profile` now renders every field with no
console/page errors. See `known_issues.md` for the standing process gap
(no automatic reload — any future backend change needs an explicit
restart).

## 2026-10-13 — Installed Vitest + React Testing Library, tests for the account area

Asked the user whether to install a frontend test framework for the new
`AccountLayout`/`ProfilePage` (the project had none); the user initially
said to skip it, then asked for it after all once the blank-screen bug
above was being investigated.

Installed `vitest`/`jsdom`/`@testing-library/{react,jest-dom,user-event}`
as frontend devDependencies (`npm install`, then `npm audit fix` for an
unrelated pre-existing transitive `source-map-js` advisory shared by
`vite`/`@tailwindcss/vite` — a safe patch bump, no major-version change).
Added a `test` script (`vitest run`) and a `test` block to
`vite.config.ts` (`environment: "jsdom"`, `setupFiles:
["./src/setupTests.ts"]`). `src/setupTests.ts` wires up
`@testing-library/jest-dom`'s matchers and an explicit
`afterEach(cleanup)` — `test.globals` was deliberately left off, so every
test file imports `describe`/`it`/`expect` from `"vitest"` directly.

Added `src/test/renderWithProviders.tsx` and `src/test/fixtures.ts`
(`makeSessionUser()`) as reusable test helpers — they provide
`AuthContext`/`LanguageContext` values directly (both have real default
context values, not `null`) rather than mocking modules or rendering the
real providers.

Wrote 14 tests: `AccountLayout.test.tsx` (nav items present, inert
sidebar entries have no destination yet, admin link only for staff,
children render, message display + dismiss), `ProfilePage.test.tsx`
(loading state, defensive no-user error state without fabricated data,
all required fields render with the authenticated user's own values,
phone "not provided" vs. set, `is_staff` badge shown only when `true`,
no other user's data ever rendered), `ProtectedRoute.test.tsx` (loading
renders nothing, unauthenticated redirects to login, authenticated
renders the protected children).

Verified: all 14 tests pass, `tsc -b` clean, `eslint .` clean, `npm run
build` output size unchanged (test files correctly excluded from the
production bundle).

## 2026-10-13 — Self-service password change page + API endpoint

Migrated `frontend.old/accounts/profile_password_edit.html` (read-only
reference) to a React page nested in the authenticated account area, and
built the backend endpoint it needed (none existed before).

**Backend**: `app_account/api/viewsets/PasswordChangeViewSet.py` (new),
mounted at `/api/account/password-change/` (`app_account/urls.py`).
Uses the project's default `IsAuthenticated` permission (no `AllowAny`),
constructs the already-existing-but-unused
`app_account/forms/PasswordChangeForm.py` (a plain subclass of Django's
own `PasswordChangeForm`) with `request.user` — never a client-supplied
identifier — so a request can only ever change the authenticated
session's own password. On success, calls `update_session_auth_hash()`
so the session stays valid instead of silently logging the user out.
Added a `password_change` throttle scope (10/hour,
`PROJECT/settings/rest_framework.py`), matching the project's existing
per-endpoint `ScopedRateThrottle` convention.

**Frontend**: `frontend/src/pages/PasswordChangePage.tsx` (new, nested in
`AccountLayout` at `/profile/password`, registered in `App.tsx` behind
`ProtectedRoute`); `api/auth.ts` gained `changePassword()`; `useApiForm.ts`
now also returns `setValues` (needed to clear the three password fields
after a successful change, per the task's explicit security requirement
not to linger sensitive values in form state after success — values are
still preserved on a validation *failure*, matching every other form on
the site). `AccountLayout.tsx`'s "Change password" sidebar item and
`UserMenu.tsx`'s dropdown item (both previously inert) now link to
`/profile/password`. Field-level errors (e.g. `old_password` for an
incorrect current password) render next to their inputs via the existing
`parseFormErrors`/`useApiForm` convention with no changes needed to
either; form-level errors use the shared `Alert` component; the
post-success message goes through `AccountLayout`'s shared
`useMessages`/`Alert` mechanism. No show/hide-password toggle was added
— no existing page in the project has one.

Added full translations (5 locales) for `passwordChange.*` and
`auth.currentPasswordLabel`.

**Tests**: 9 new backend tests (authentication required, success keeps
the session valid, wrong current password is a field error, invalid new
password is rejected per `AUTH_PASSWORD_VALIDATORS`, a request cannot
target another user even when one's id/email is smuggled into the
payload, CSRF is enforced, the endpoint is throttled) plus 1 regression
test confirming `/api/account/session/` ignores a client-supplied user id
query param — all in `app_account/tests/api/test_auth_api.py`. 11 new
frontend tests in `src/pages/PasswordChangePage.test.tsx` (fields render,
success clears fields and shows feedback, field-level error preserves
other values, form-level error via the shared alert, submit button
disabled while in flight) plus `AccountLayout.test.tsx` updated for the
no-longer-inert "Change password" link.

**Validation**: backend — `manage.py check`, `makemigrations --check
--dry-run` (no changes needed), full `pytest` (114 passed, up from 104),
`ruff check`/`ruff format --check`, `mypy`, `basedpyright` — all clean.
Frontend — full Vitest suite (20 → with this page, 25 tests across 4
files, all passing — see `testing.md`), `tsc -b`, `eslint .`, `npm run
build` — all clean.

**Live verification**: `ecommerce_django` runs Gunicorn with no
autoreload (see the known process gap above), so restarted it
(`docker compose restart backend`) before testing the live site, then
used a real Playwright/Edge session against `https://177.222.210.50`
with a throwaway test user (created and deleted via Django shell) to
confirm end-to-end: login → `/profile/password` → submit → `200 {}` →
success message shown → fields cleared → session still authenticated
afterward (screenshot captured, matches the design).

## 2026-10-14 — Fixed stacking success notifications + added the unchanged-password rule

User reported (with a screenshot) that `/profile/password` kept showing
multiple stacked "password changed" success boxes, that submitting the
*same* password as the current one wrongly showed success, and that
messages from previous attempts never got replaced.

**Root causes, both confirmed by reading the code (not assumed):**
1. `useMessages.ts`'s `addMessage` only ever appended — nothing ever
   cleared a previous action's messages, so every submission (success or
   not) piled another box on top of whatever was already there.
2. `PasswordChangeForm` (`app_account/forms/PasswordChangeForm.py`) had
   no rule against the new password being identical to the current one —
   Django's own `PasswordChangeForm` doesn't enforce that by default — so
   that case genuinely succeeded (200) and correctly triggered a success
   message; the "bug" there was the missing validation, not a false
   positive in the notification code.

**Backend**: `PasswordChangeForm.clean()` now rejects a `new_password1`
that matches the user's current stored hash
(`self.user.check_password(...)`, never a raw string compare), checked
only after `old_password` itself cleaned successfully, as a **non-field**
`ValidationError` with `code="password_unchanged"` — reuses the existing
`form_errors_payload`/`code` response convention (same 400 shape as every
other account error), no new response format introduced.

**Frontend**:
- `hooks/useMessages.ts` rewritten: `addMessage` replaced with
  `beginAction()` (clears previous messages, returns a token) +
  `replaceMessages(token, [...])` (sets the current action's full message
  set — zero, one, or several of different variants — ignored if `token`
  is no longer the current action, guarding against a late response from
  a superseded submission). `ProfilePage.tsx` didn't need changes (it
  never called the old `addMessage`).
- `pages/PasswordChangePage.tsx` rewritten around the new API: a
  `useEffect` reacts to `useApiForm`'s own `code`/`generalErrors` state
  (recognizing `password_unchanged` specifically → `warning` variant,
  anything else → `error` variant) and routes it through
  `replaceMessages`; the success path calls `replaceMessages` directly
  with the awaited result (not hook state, so no staleness risk there).
  The previous inline `form.generalErrors` `<Alert>` block was removed —
  all page-level feedback now goes through the one shared mechanism.
- `hooks/useApiForm.ts`: `generalErrors` is now `useMemo`-ed (was
  recomputed as a brand-new array every render). **This was a real bug
  found while building the above**: an unmemoized array used as a
  `useEffect` dependency caused an infinite render loop (new reference →
  effect refires → `replaceMessages` triggers a render → new reference
  again...), which surfaced as `PasswordChangePage.test.tsx`'s form-error
  test timing out intermittently. Fixed by memoizing on
  `[generalMessages, t]`; no other consumer of `generalErrors` is
  affected (LoginPage/SignupPage/PasswordResetPage/PasswordResetConfirmPage
  all just render the array, never diff its identity).
- Added `passwordChange.unchangedWarning` to all 5 locales.

**Tests**: 3 new backend tests (`password_unchanged` rejected with the
right code, the check doesn't fire when the current password is itself
wrong, a valid submission succeeds right after a rejected one) — 117
backend tests total. New `hooks/useMessages.test.ts` (8 tests, hook-level,
via `renderHook`/`act`) covering: multiple simultaneous variants in one
action, a new action replacing a previous one's messages (including when
the new action has no general message of its own), two consecutive
successes never leaving a duplicate, a warning replacing a stale success,
dismissing one message leaving siblings alone, and a stale/superseded
action's late response being ignored. 4 new `PasswordChangePage.test.tsx`
scenarios reproducing the exact reported bug end-to-end (unchanged
password → warning not success; two successes in a row → exactly one
message; success → field error removes the stale success; success →
warning removes the stale success) — 32 frontend tests total.

**Validation**: backend — `manage.py check`, `makemigrations --check
--dry-run` (no changes needed), full `pytest` (117 passed), `ruff
check`/`ruff format --check`, `mypy`, `basedpyright` — all clean.
Frontend — full Vitest suite (32 passed), `tsc -b`, `eslint .`, `npm run
build` — all clean. Restarted `ecommerce_django` (Gunicorn, no
autoreload) and reproduced the exact reported sequence live via
Playwright/Edge against `https://177.222.210.50` with a throwaway test
user (created and deleted via Django shell): success → unchanged-password
warning → wrong-current-password field error → success again, confirming
exactly one notification visible at each step with no stacking
(screenshot captured).

## 2026-10-14 — Profile editing page + endpoint

Migrated `frontend.old/accounts/profile_edit.html` (read-only reference)
to a React page reusing the registration form's field components,
nested in the authenticated account area.

**Backend**: fixed a real, previously-latent bug —
`app_account/forms/UserUpdateForm.py`'s `Meta.model: UserModel` was a
type annotation, not an assignment, which would have raised "class Meta
... must have a model attribute" the moment the form was ever
instantiated; it never had been, until now. Changed to `model =
UserModel`. New `app_account/api/viewsets/ProfileUpdateViewSet.py`,
mounted at `/api/account/profile/` (`app_account/urls.py`) — same
`IsAuthenticated`-only, `request.user`-only pattern as
`PasswordChangeViewSet`. `UserUpdateForm.Meta.fields` only lists
`name`/`date_birth`/`phone`, so Django's `ModelForm` machinery simply
never reads any other submitted key — `is_staff`/`is_superuser`/
`is_active`/`email`/a client-supplied `id` are all silently ignored, no
extra filtering code needed, only a test proving it. Skips `.save()`
(and so leaves `updated_at` untouched) when `form.has_changed()` is
`False`. Returns `{"user": serialize_user(user)}`, the same shape as
login/signup. **`email` was deliberately left non-editable** — it's the
`USERNAME_FIELD` and its `is_email_verified` status is tied to the
specific address a token was sent to; a silent email change here would
let a user "verify" an address without proving ownership of it. Adding
email-change support would need its own re-verification flow, not a
one-line addition to this form — flagged as a conscious scope decision,
not an oversight.

**Frontend**: `frontend/src/pages/ProfileEditPage.tsx` (new, nested in
`AccountLayout` at `/profile/edit`, registered in `App.tsx` behind
`ProtectedRoute`) — reuses `TextField`/`SubmitButton` and the exact
`t.auth.nameLabel`/`dateBirthLabel`/`phoneLabel`/`phonePlaceholder`
translation keys `SignupPage.tsx` already uses, so no new field-label
translations were needed (only a new `profileEdit.*` section for the
page's own title/heading/submit/success/cancel strings, all 5 locales).
Prefills from `useAuth().user` (no second fetch — `ProtectedRoute`
already guarantees it's populated by the time this page mounts).
`api/auth.ts` gained `updateProfile()`. On success, calls `setUser()`
(from `useAuth()`) with the backend's response — the same `AuthContext`
state every other auth action already mutates — so the navbar greeting
and `ProfilePage` reflect the change immediately with no reload and no
second source of truth for the current user; verified live (see below).
Uses the same action-scoped `useMessages`/`useEffect`-over-`useApiForm`-state
pattern as `PasswordChangePage.tsx` for consistent notification
lifecycle. `AccountLayout.tsx`'s "Edit profile" sidebar item and
`UserMenu.tsx`'s dropdown item (both previously inert) now link to
`/profile/edit`. `src/test/renderWithProviders.tsx` gained an optional
`setUser` param (a test can pass a `vi.fn()` to assert a page called it
with the right value) — purely additive, no existing test changed.

**Tests**: 9 new backend tests (auth required, a real update persists
and is reflected in the response, field validation errors, protected
fields silently ignored even when submitted, a client-supplied id/other
user's data can't be touched, the write is skipped — `updated_at`
unchanged — when nothing actually changed, CSRF enforced) — 126 backend
tests total. 8 new `ProfileEditPage.test.tsx` tests (loading/error
states without fabricated data, prefilled with the real user's own data,
no staff/permission controls rendered, success updates `AuthContext` and
shows feedback, field-level error preserves other values, form-level
error via the shared alert with no false success, submit disabled while
in flight) plus `AccountLayout.test.tsx` updated for the no-longer-inert
"Edit profile" link (and a pre-existing test's `/profile/i` regex
selector fixed — it had started matching "Edit profile" too) — 41
frontend tests total.

**Validation**: backend — `manage.py check`, `makemigrations --check
--dry-run` (no changes needed), full `pytest` (126 passed), `ruff
check`/`ruff format --check`, `mypy`, `basedpyright` — all clean.
Frontend — full Vitest suite (41 passed), `tsc -b`, `eslint .`, `npm run
build` — all clean. Restarted `ecommerce_django` (Gunicorn, no
autoreload) and verified live via Playwright/Edge against
`https://177.222.210.50` with a throwaway test user (created and deleted
via Django shell): edited name/date of birth/phone → `200` with the
normalized values in the response → success message → navbar greeting
updated immediately (no reload) → confirmed in the database directly
that the new values persisted → a raw `fetch()` smuggling `is_staff:
true` into the payload confirmed the response still reported
`is_staff: false` (screenshot captured).

## 2026-10-14 — Phone fields ignore letters while typing

Requested: when a user types a letter character into the phone field on
signup or profile edit, it should simply be ignored (not inserted).

New `frontend/src/components/ui/sanitizePhoneInput.ts`
(`value.replace(/\p{L}/gu, "")`, Unicode-aware so accented letters are
also stripped, not just `a-zA-Z`) — digits, spaces, and symbols
(`+`, `-`, parentheses) are left untouched. Wired into `SignupPage.tsx`
and `ProfileEditPage.tsx`'s phone `TextField` via a small dedicated
`onChange` handler (`form.setValues` directly) instead of the generic
`form.onChange` every other field uses. `ContactPage.tsx` also has a
phone field but was deliberately left untouched — not part of the
request. The backend's `PhoneNumberField`/validators remain the actual
format authority; this is purely a typing-experience filter, not a new
validation rule, so no backend change was needed or made.

Tests: `sanitizePhoneInput.test.ts` (4 cases: strips letters, strips
accented letters, leaves a letter-free value untouched, empty string) +
one new `ProfileEditPage.test.tsx` case typing a mixed
letters/digits/symbols string and asserting only the letters were
dropped — 46 frontend tests total. Validation: full Vitest suite (46
passed), `tsc -b`, `eslint .`, `npm run build` — all clean. Live-verified
on the real `/signup` page via Playwright/Edge against
`https://177.222.210.50` (no backend restart needed — this is a
frontend-only, Vite-HMR-applied change).

## 2026-10-14 — Authenticated user address list + primary-address selection

Built the first address-facing API and page: a read-only list of the
authenticated user's own addresses, with a radio group to switch which
one is primary. No `frontend.old/` reference existed for this (no
address-related legacy template) — designed from scratch following the
project's own established conventions (`ProductImageModel`'s invariant
pattern, `ProductCategorySimpleListViewSet`'s naming, the account area's
existing layout/notification/route-guard pieces).

**Backend — hardened the primary-address invariant at the model/signal
level** (not just "at most one," now also "a user's first address is
always primary" and "deleting the primary promotes another"), confirmed
there was no existing address data to migrate (0 rows) before touching
anything:
- `app_account/models/UserAddressModel.py`: `save()` now forces
  `primary = True` when `self.pk is None` (a genuine insert) and the
  user has no other address yet — regardless of what the caller
  submitted. Verified empirically via shell before writing tests.
- New `app_account/signals/promote_primary_address_after_delete.py`
  (`post_delete`, wired into `AccountConfig.ready()` via `import_module`,
  exactly like `app_product.signals.product_image`'s analogous
  image-primary-promotion signal): if the deleted address was primary
  and others remain, promotes the oldest remaining one. Handles both
  `instance.delete()` and `QuerySet.delete()` (via the signal's `origin`
  argument) and no-ops safely when the user itself was deleted too.
- New read-only nested serializers for reference data:
  `app_address/api/serializers/{CitySimpleSerializer,StateSimpleSerializer,CountrySimpleSerializer}.py`
  (`id`/`name` plus `code`/`iso_code` respectively) — `app_address` still
  has no routes of its own; these are only ever nested inside the
  address response below.
- New `app_account/api/serializers/UserAddressSerializer.py` and
  `app_account/api/viewsets/UserAddressViewSet.py`
  (`ListModelMixin` + a `set-primary` `@action`), mounted at
  `/api/account/addresses/`. `get_queryset()` is always scoped to
  `request.user`; `set_primary` uses `self.get_object()` against that
  same scoped queryset, so another user's address id 404s (not 403 —
  indistinguishable from a nonexistent id, no enumeration leak).
  `pagination_class = None` (plain JSON array — a handful of addresses
  per user doesn't need page-based pagination); list ordering is
  `-primary, created_at` (primary first), deliberately overriding the
  model's own `Meta.ordering` (which sorts primary *last*). `set-primary`
  returns the user's full, fresh address list, not just the one address,
  so the frontend never has to reimplement the demote-the-others logic
  itself.
- New factories: `app_address/tests/factories/{CountryFactory,StateFactory,CityFactory}.py`,
  `app_account/tests/factories/UserAddressFactory.py` — none existed
  before. Hit and fixed a real import-order problem (see `testing.md`)
  where ruff's alphabetical-import-sort conflicts with the factories'
  actual dependency order; fixed by importing each dependency from its
  sibling *module* directly rather than through the package `__init__.py`.

**Frontend**: `frontend/src/pages/AddressListPage.tsx` (new, nested in
`AccountLayout` at `/profile/addresses`, registered in `App.tsx` behind
`ProtectedRoute`) — reads via `useAsync(fetchUserAddresses, undefined)`
for the initial load, with a local `override` state (same pattern as
`AuthProvider`'s own `override`) taking precedence after a successful
primary switch. Each of the 9 address fields
(street/number/complement/reference/district/postal_code/city/state/country)
renders only when non-blank (trim-checked, so a literal `"0"` is
preserved and whitespace-only is treated as blank) via a small
`AddressField` component mirroring `ProfilePage.tsx`'s existing
`ProfileField` pattern. Radio inputs share one native `name` (one
logical group), each with a distinct `aria-label` (not just the generic
visible "Primary address" text, which would be identical and
undistinguishable for every row to a screen reader). Selecting a
non-primary radio fires the request immediately (no Save button);
rapid/overlapping selections are handled with a `requestTokenRef`
(incremented per click, compared on response — a stale one is silently
discarded) plus an `AbortController` (the previous in-flight request is
aborted via `apiPost`'s existing optional `AbortSignal` parameter); a
failed update re-fetches the authoritative list rather than trusting
whatever was on screen before the attempt. Add/Edit/Delete are rendered
with real icons (`PlusIcon`, `PencilIcon`, `TrashIcon` — the first two
new, added to `components/ui/icons.tsx`) and a new
`components/ui/Tooltip.tsx` (works on both mouse hover and keyboard
focus via `group-hover`/`group-focus-within`, injects `aria-describedby`
via `cloneElement`) but have **no `onClick` at all** — genuinely inert,
not just visually disabled — and use `aria-disabled="true"` rather than
the native `disabled` attribute specifically so they stay
keyboard-focusable (a natively `disabled` button can't receive focus,
which would make its tooltip unreachable by keyboard). New
`frontend/src/api/addresses.ts` (`fetchUserAddresses`,
`setPrimaryAddress`), new `UserAddress`/`AddressLocation`/`AddressState`/`AddressCountry`
types in `api/types.ts`. `AccountLayout.tsx`'s "My addresses" sidebar
item and `UserMenu.tsx`'s dropdown item (both previously inert) now link
to `/profile/addresses`. Added a `makeUserAddress()` fixture to
`src/test/fixtures.ts`. Full `addressList.*` translations in all 5
locales, with the required exact Portuguese empty-state string
`"Nenhum endereço cadastrado."` verified directly against the locale
file in a test (not just rendered and eyeballed).

**Tests**: 25 new backend tests — `app_account/tests/models/test_user_address_rules.py`
(first-is-primary including when explicitly submitted as not-primary,
independent per user, demote-on-set, delete-promotion including
`QuerySet.delete()`, cascading user deletion, the DB constraint rejecting
a bypass-the-model write) and `app_account/tests/api/test_user_address_api.py`
(auth required for both list and set-primary, list scoped to the
requester only, primary-first ordering, nested city/state/country names
present, set-primary demotes/promotes correctly and is a no-op when
already primary, a cross-user set-primary attempt 404s without touching
either user's data, a nonexistent id 404s) — 151 backend tests total.
13 new `AddressListPage.test.tsx` tests (loading vs. error vs. empty
states kept distinct, the exact required Portuguese string, Add address
visible in both empty and populated states — as two separate `it()`
blocks, since two `render()` calls in one test collide, see `testing.md`
— blank/whitespace fields hidden while `"0"` survives, radios reflect
the authoritative `primary` flag, a selection calls the API with the
right id and shows success, a failed selection reconciles with a
re-fetch and shows the error notification, a stale response from a
superseded selection is proven to be discarded, Edit/Delete proven
inert with no API call, and the tooltip's `aria-describedby` wiring) —
59 frontend tests total.

**Validation**: backend — `manage.py check`, `makemigrations --check
--dry-run` (no changes needed — no model fields changed, only
`save()`/signal logic), full `pytest` (151 passed), `ruff check`/`ruff
format --check`, `mypy`, `basedpyright` — all clean (basedpyright caught
a few things mypy didn't: an unnecessary `cast`, an untyped `.data` on a
many=True serializer needing an explicit `cast(list[dict[str, Any]],
...)`, and the factory lambdas needing to become named, annotated
functions — same fix already used by `ProductImageFactory.generate_order`).
Frontend — full Vitest suite (59 passed), `tsc -b`, `eslint .`, `npm run
build` — all clean. Restarted `ecommerce_django` (Gunicorn, no
autoreload) and verified live via Playwright/Edge against
`https://177.222.210.50` with a throwaway test user and two real
addresses (created against real Country/State/City reference data, not
fabricated): first address auto-became primary on creation, selecting
the second as primary returned `200` with the correct authoritative
list, the success message appeared, the database was independently
queried and confirmed the persisted state matched the API response
exactly, and Edit/Delete were confirmed inert (click produced no
navigation, no request) — screenshot captured. Cleaned up the test user
and its addresses afterward; confirmed the database was back to 0
addresses.

## 2026-10-14 — Small visual polish on `/profile`: admin icon, staff badge placement

Two small, requested UI tweaks, frontend-only:
- `AccountLayout.tsx`'s "Admin access" sidebar link had no icon, unlike
  every other sidebar item — added a new `ShieldCheckIcon`
  (`components/ui/icons.tsx`, same Heroicons-outline style as the rest)
  to match.
- `ProfilePage.tsx`'s "Staff account" badge moved from a quiet pill below
  the data card to sit directly beside the "My profile" heading, and was
  given more visual weight (`bg-blue-100`/`ring-blue-300`/`font-semibold`
  instead of the previous plain `bg-blue-50`/`font-medium`, plus the same
  `ShieldCheckIcon` for consistency with the sidebar). Still conditional
  on `user.is_staff` only — the condition itself wasn't touched.

No backend changes, no new tests (existing `ProfilePage.test.tsx`/
`AccountLayout.test.tsx` assertions are text-based, so the reposition
needed no test updates — all 59 frontend tests still pass). Validation:
`tsc -b`, `eslint .`, full Vitest suite, `npm run build` — all clean.
Live-verified via Playwright/Edge against `https://177.222.210.50` with
a throwaway staff test user (created and deleted via Django shell) —
screenshot captured confirming both changes.

## 2026-10-15 — Wishlist system (backend only) + a live migration-graph incident

Backend-only, as instructed (`app_account`): one wishlist per user,
unlimited items with no duplicate product per list, a gap-free `position`
field, admin support, tests. No frontend work, no API endpoint,
`frontend.old/` untouched.

**Blocking incident, diagnosed and fixed first** (the task's own mandated
order: fix the migration graph before touching the feature). Reproduced
`docker exec ecommerce_django python manage.py showmigrations` and got
`NodeNotFoundError: Migration account.0002_initial dependencies reference
nonexistent parent node ('address', '0001_initial')`. Root cause, confirmed
by reading the actual files (not assumed): `app_address/migrations/
0001_initial.py` **and** `app_product/migrations/0001_initial.py` (a
second, independently-missing app the original report didn't mention)
were both absent from disk — migrations aren't committed to git in this
project (pre-existing, see `known_issues.md`), and these two had been
lost. `app_account/migrations/0002_initial.py` (regenerated the same
morning, consolidating all current models) still declared hard
dependencies on both. Checked `docker inspect ecommerce_django`:
`RestartCount` was climbing continuously — `entrypoint.sh` runs
`makemigrations` unconditionally under `set -e`, so this error crashed the
whole container on every boot, and `restart: unless-stopped` kept retrying
every few seconds (233 restarts observed, then 294 by the time it was
fixed). Direct `psql` inspection confirmed the affected tables held zero
rows — no data at risk.

Fix (no `--fake`/`--fake-initial`, no manual `django_migrations` edits, no
deleted migration history): temporarily renamed `app_account/migrations/
0002_initial.py` aside to confirm it was genuinely the address/product
files that were missing (not a label mismatch — re-verified all four
`AppConfig.label`s fresh) and to see what the autodetector actually
needed; restored it immediately afterward once that was confirmed — this
was read-only diagnosis, not part of the fix. Created minimal empty
`0001_initial.py` placeholders for `app_address`/`app_product` (so the
loader has a node to find), then ran `makemigrations address`/
`makemigrations product` for real, letting Django's own autodetector
generate the actual `CreateModel` operations for `CityModel`/
`CountryModel`/`StateModel`/`ProductModel`/etc. into fresh
`0002_initial.py` files — not hand-written, to avoid any field-definition
mismatch. Then corrected `app_account/migrations/0002_initial.py`'s
`dependencies` from `("address"/"product", "0001_initial")` (the
now-empty placeholders) to `("address"/"product", "0002_initial")` (the
migrations that actually create the referenced tables) — account's own
`AddField`s need those tables to exist first; this was the one real
content edit, made before the migration had ever been applied (confirmed
via `django_migrations` — zero rows for it beforehand). `manage.py
migrate` then ran clean; `RestartCount` stopped climbing and the
container reached `Health=healthy`. Full detail and the exact commands
are in `database.md`'s "Migrations — confirmed risk" section and
`known_issues.md` item 1.

**Models** (`app_account/models/UserWishlistModel.py`,
`UserWishlistItemModel.py`, new `organize_wishlist_items.py`):
`UserWishlistModel.user` is a plain `OneToOneField(CASCADE)` — the DB
unique index is the whole "one wishlist per user" invariant, no custom
`save()` needed (unlike addresses, there's no "one flagged row among
several" problem). `UserWishlistItemModel` already had
`UniqueConstraint(wishlist, product)` from an earlier pass; added
`position` (`PositiveIntegerField`, default `0`, 0-based — deliberately
not the task's literal "1 = first" suggestion, since `ProductImageModel.
order` already established an equivalent 0-based pattern in this
codebase and reusing it was judged more valuable than matching the
suggestion verbatim) plus a second, `Deferrable.DEFERRED`
`UniqueConstraint(wishlist, position)`. `save()` locks the parent
wishlist (`select_for_update`), always appends new items at the end (no
form field exposes `position` yet, so there's no sanctioned way to
request a specific one on create), and re-flows siblings gap-free via
`organize_wishlist_items()` — a per-app copy of `ProductImageModel`'s
`organize_product_images()` anchor-insert algorithm, deliberately not
shared across apps per the project's own stated convention. A new
`post_delete` signal (`reorganize_wishlist_items_after_delete.py`) closes
the gap after a deletion, mirroring `app_product.signals.product_image.py`
exactly. Also fixed a pre-existing i18n gap: both models' `verbose_name`/
`verbose_name_plural` were plain strings instead of `gettext_lazy`.

**Auto-creation** (`app_account/signals/create_wishlist_for_new_user.py`):
a `post_save` receiver on `UserModel`, guarded by `created=True`, calling
`UserWishlistModel.objects.get_or_create(user=instance)`. Chosen over a
service function specifically because it must fire for every
user-creation path (signup, admin, factories, future commands) without
each one remembering to call it — registered once in `AccountConfig.
ready()`, same `import_module` pattern as the existing
`promote_primary_address_after_delete`.

**Forms**: `UserWishlistBaseForm`/`CreateForm`/`UpdateForm`,
`UserWishlistItemBaseForm`/`CreateForm`/`UpdateForm` were already drafted
in an earlier pass — reviewed, found already correct (reuse the base-form
split, don't expose `position`), only needed exporting the two `*BaseForm`
classes from `app_account/forms/__init__.py` (they were missing, which
made `from app_account.forms import UserWishlistItemBaseForm` silently
resolve to the submodule instead of the class — `admin.E016` at
registration time).

**Admin**: `UserWishlistAdmin` (`search_fields`/`list_filter` on `user`,
`select_related("user")` + `prefetch_related("items__product")`, a new
`UserWishlistItemInlineAdmin` showing `product`/`position`/`added_at`)
and `UserWishlistItemAdmin` (`autocomplete_fields = ("product",)`,
`select_related("wishlist__user", "product")`). Fixed a real bug in the
already-drafted files: `search_fields` referenced `user__username` —
`UserModel` has no `username` field (`email` is its `USERNAME_FIELD`) —
corrected to `user__email`/`user__name`, matching `UserAddressAdmin`'s
own convention.

**Tests** (`app_account/tests/models/test_user_wishlist_rules.py`,
`test_user_wishlist_item_rules.py`, new factories `UserWishlistFactory`
— `django_get_or_create = ("user",)`, since the signal already creates
one — and `UserWishlistItemFactory`, plus `app_account/tests/
test_migrations.py` as a regression test for the `NodeNotFoundError`
incident): 30 new tests, closely mirroring `test_product_image_rules.py`'s
structure (inclusion, duplicate rejection, position create/reorg/delete/
cross-wishlist isolation, DB constraints incl. the deferred one via
`connection.check_constraints()`). Full suite: 181 passed, no regressions.
`ruff check`/`ruff format --check`/`mypy`/`basedpyright` all clean on
`app_account/` — fixed a couple of real typing gaps surfaced along the
way (the FK fields on `UserWishlistItemModel` needed explicit
`ForeignKey[Model, Model]` annotations for their string `to=` references
to resolve under basedpyright, matching `UserAddressModel.user`'s
existing convention; `added_at` needed the same `cast("datetime", ...)`
pattern already used for `BaseModel.created_at` elsewhere in the test
suite).

**Could not be run**: none — Docker was available throughout, and the
one-off `docker compose run --rm --no-deps --entrypoint "..." backend`
pattern (bypassing the crash-looping main container) made every
diagnostic and fix command reproducible without racing the restart loop.
