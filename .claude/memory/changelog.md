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

## 2026-10-16 — Mid-session hotfix: two circular imports reintroduced the migration-incident crash loop

Between the wishlist task above and the next one, the user reported
breaking something while "testing a configuration." Diagnosed and fixed
two real circular imports, both the same shape: a `from __future__ import
annotations`-eligible, `TYPE_CHECKING`-only import had been changed to an
unconditional runtime import, which is circular because the other side
of each pair imports back for a real (non-type-only) reason:
- `app_account/models/UserManagerModel.py` — `UserModel` import moved out
  of `TYPE_CHECKING`; `UserModel.py` itself imports `UserManagerModel`
  for real (`objects: ClassVar[UserManagerModel] = UserManagerModel()`).
- `app_account/models/organize_wishlist_items.py` — same shape with
  `UserWishlistItemModel`, compounded by `app_account/models/__init__.py`
  now exporting `organize_wishlist_items` (it was never meant to be
  public — mirrors `organize_product_images` not being exported from
  `app_product/models/__init__.py` either).

Both put `ecommerce_django` back into the exact same `entrypoint.sh`
crash-loop mechanism as the earlier migration incident (`ImportError`
during Django's own app-loading `import_models()`, fatal under `set -e`,
retried forever by `restart: unless-stopped`). Fixed by restoring the
`TYPE_CHECKING` guards and removing the stray export; verified
`manage.py check` passes and the container reaches `Health=healthy`
with `RestartCount` no longer climbing.

## 2026-10-16 — Product pages, catalog randomization, i18n default, admin, images, addresses

Eight-part task across the React storefront and Django backend/admin,
executed in the order given, each stage verified before moving on
(`manage.py check`/full `pytest`/`ruff`/`mypy`/`basedpyright` on the
backend; `tsc -b`/`eslint`/full Vitest/`npm run build` on the frontend —
all genuinely run, not assumed; final counts: 202 backend tests, 82
frontend tests, both suites fully green, no migrations needed anywhere
in this task).

**1-2. Breadcrumb truncation + expandable description**
(`frontend/src/pages/ProductDetailPage.tsx`): the breadcrumb was inline
JSX with no reusable component anywhere in the codebase — extracted into
new `components/product/ProductBreadcrumb.tsx`, truncating only the
product-name segment via Tailwind `truncate`+`max-w` plus a `title`
attribute (full name stays in the DOM, `<h1>`, and `<title>` tag
untouched). New `components/product/ExpandableDescription.tsx` wraps the
existing `<Markdown>` component unchanged (no sanitization behavior
touched) with a 320-character threshold on the raw description deciding
whether to show a `Read more`/`Show less` toggle (`aria-expanded`/
`aria-controls`), CSS `max-height` clamping for the collapsed state so
markdown structure is never string-truncated mid-token.

**3. Randomized catalog ordering** (`app_product/api/viewsets/
ProductSimpleListViewSet.py`): root cause confirmed first — the view's
`ordering = ("-created_at",)` default, sent explicitly by the frontend's
sort dropdown on `/products` and implicitly inherited by `/` (same
endpoint, no `ordering` param). Chosen fix: a deterministic,
**daily-seeded** pseudo-random order, `MD5(Concat(Cast("id", CharField()),
Value(seed)))` with `seed = timezone.now().date().isoformat()`, annotated
in `get_queryset()` and set as `ordering = ("_shuffle",)` — not in
`ordering_fields`, so an explicit `?ordering=` still overrides it exactly
as before (`StableOrderingFilter`'s `pk` tie-breaker still applies). No
model field, no migration, no new dependency. Rejected alternatives:
per-request `order_by("?")` (breaks pagination — reshuffles every
request) and a per-session seed (adds real state for a catalog this
small). Frontend: `productSort.ts` gained a `"featured"` sentinel
(now `DEFAULT_PRODUCT_SORT`) meaning "send no `ordering` param," visible
in the sort dropdown per the user's own clarification, with
`ProductListPage.tsx` omitting the param for it. New tests prove
stability-across-requests and no-duplicates-across-pages without
asserting any specific sequence, per the task's own warning against
fragile randomness-based tests.

**4. English default language**: `PROJECT/settings/
internationalization.py`'s `LANGUAGE_CODE` default `"pt-br"` → `"en"`;
`.env`'s already-inconsistent `LANGUAGE_CODE=en-us` normalized to `en` to
match the `LANGUAGES` tuple's `"en"` entry. Frontend:
`frontend/src/i18n/languages.ts`'s `DEFAULT_LANGUAGE` → `"en"`. Both are
just the final fallback — `LANGUAGES`, the switcher, and all 5 locale
catalogs are untouched. Extracted `detectInitialLanguage` out of
`LanguageProvider.tsx` into its own file (new
`i18n/detectInitialLanguage.ts`) purely so it could be unit-tested
without violating the project's `react-refresh/only-export-components`
ESLint rule (a component file must export only the component).

**5. USD price display, presentation only**:
`components/product/formatPrice.ts`'s `Intl.NumberFormat("pt-BR", {currency:
"BRL"})` → `Intl.NumberFormat("en-US", {currency: "USD"})` — the single
function already shared by `ProductPrice.tsx` (detail) and
`ProductCard.tsx` (grid/listing), so one change covered every
customer-facing price. No conversion, no backend/numeric change,
confirmed by tests asserting the formatter's output for known inputs,
not any exchange behavior.

**6. Product admin field reorder**
(`app_product/admin/ProductAdmin.py`, `forms/ProductForm.py`): per the
user's clarification, final order is `active, category, name, slug,
price, thumbnail, description` (the task's own list omitted `active`;
user chose to keep it first rather than move it to the end). Added an
explicit `ProductAdmin.fields` tuple so `slug` (`readonly_fields`) is
interleaved at the right spot instead of Django's default of appending
every readonly field after all editable ones. Verified the *rendered*
order via `ModelAdmin.get_form()`/`get_fieldsets()` directly (not just
source order), per the task's explicit instruction to do so. List page
config untouched — confirmed via a dedicated test, not just by not
touching those lines.

**7. ProductImage primary/ordering + dynamic admin JS**: most of the
server-side invariants already existed (DB constraints, `save()`
locking/demotion/reorg, a `post_delete` promotion signal) — the one real
gap was that a product's first image didn't auto-become primary (added,
mirrors `UserAddressModel`'s equivalent rule). Writing the "add + delete
in the same submission" test required by the task surfaced a real,
separate bug: Django's admin formset binds submitted field data
(including an *unchecked* `is_primary` checkbox) onto `form.instance`
*before* calling `.delete()` on a row marked for deletion, so the
`post_delete` signal's `instance.is_primary` can be stale/wrong —
fixed by checking the actual invariant ("images remain but none is
primary") instead of trusting that attribute. New admin JS,
`static/src/js/admin/product_image_inline.js` (loaded via
`ProductImageInlineAdmin.Media.js`, which had none before): mutual
exclusivity for the `is_primary` checkboxes and `max(order)+1` auto-fill
for a new row (via Django's native `formset:added` `CustomEvent`,
confirmed as a real DOM event in this Django version, not jQuery),
narrowly scoped to the inline's own `#images-group` container, never
reordering DOM rows or auto-submitting.

**8. Country/state/city cascade, admin-only**: confirmed scope first —
there is no customer-facing address create/edit form at all (list +
set-primary only), so this only touches `UserAddressBaseForm`/the admin.
New `app_address/api/viewsets/{StateListViewSet,CityListViewSet}.py`
(`IsAdminUser`, unpaginated — `app_address` had zero API routes before
this) plus `app_address/urls.py`, registered in `PROJECT/urls.py`.
Extended the existing `city_location_select.js` (which already
auto-filled state/country from a chosen city — kept as-is) with two more
`change` listeners fetching the new endpoints and rebuilding the
`<option>` lists for country→state and state→city, clearing
incompatible selections. New `UserAddressBaseForm.clean()` rejects a
`state`/`country` or `city`/`state` mismatch server-side regardless of
what the JS did. `app_address` has its first tests of its own
(`tests/api/test_geo_filters.py`).

**Not verified live**: the two pieces of dynamic admin JS (section 7 and
8) were not click-tested in a real browser — no Chrome DevTools MCP
connection was available this session (confirmed failed/unavailable, not
skipped). JS syntax was checked (`node --check`) and the server-side
behavior each depends on is fully covered by automated tests; the admin
field order (section 6) *was* verified against Django's real rendering
machinery (`get_form`/`get_fieldsets`), which is the authoritative
mechanism the template renders from, so that one doesn't carry the same
caveat.

## 2026-10-16 — Fix address dependencies, add primary-address selection, responsive layout, image ordering fix

Follow-up to the same day's earlier task, fixing real bugs it introduced
and adding one genuinely new piece. Root causes confirmed by reading the
actual files and, for the two JS bugs, the *installed Django's own*
template/JS source — not guessed.

**1. Country → State → City synchronization, two real bugs fixed.**
Bug 1: `UserAddressBaseForm.state` used a plain `forms.Select` (unlike
`city`'s `CityLocationSelect`), so a freshly-rendered state `<option>`
never had `data-country` to read — picking a state before any AJAX
rebuild had happened did nothing. Fixed with a new
`app_address/forms/widgets/StateLocationSelect.py` (mirrors
`CityLocationSelect`), applied to the `state` field. Bug 2: rebuilding
the city list after a state change replaced its options with ones
lacking `data-state`/`data-country` entirely, since
`CitySimpleSerializer` didn't return `state`/`country` — this is
precisely why state-first interfered with the previously-working
city-first sync, confirmed by reading `city_location_select.js`'s own
`rebuildOptions()`. Fixed by adding `state` (plus `country` via
`source="state.country_id"`) to `CitySimpleSerializer`, and
generalizing `rebuildOptions()` to stamp both attributes on every
rebuilt option. Rewrote `city_location_select.js`'s cascade logic:
picking a state now also refreshes the state list itself (scoped to
the derived country, keeping the selection) and the city list; picking
a country refreshes the state list then the city list for whatever
state survives; a per-field request-token discards a stale response
that resolves after a newer one for the same field.

**2. Primary-address selection — new, not a fix.** The previous task
only built the cascade; nothing existed yet for primary selection. New
`static/src/js/admin/user_address_inline.js` (loaded via
`UserAddressInlineAdmin.Media.js`), mirroring
`product_image_inline.js`'s `is_primary` exclusivity listener, scoped to
`#user_addresses-group`. Also fixed the address equivalent of last
task's ProductImage signal bug:
`app_account/signals/promote_primary_address_after_delete.py` gated
promotion on `instance.primary`, the same Django-formset-binding
staleness issue already found and fixed for
`app_product.signals.product_image`. `UserAddressModel.save()`'s
existing invariant (locking, demotion, DB constraint,
first-is-primary) needed no changes — confirmed correct, not rebuilt.

**3. Field order → Country, State, City**: reordered both
`UserAddressBaseForm.Meta.fields` (covers the standalone
`UserAddressAdmin`) and `UserAddressInlineAdmin.fields` (overrides it
for the inline) independently — same two-places lesson as the previous
task's `ProductAdmin.fields`/`ProductForm`. Verified via
`get_form`/`get_fieldsets()` directly for both, add and change.

**4. Responsive inline layout**: new scoped CSS,
`static/src/css/admin/user_address_inline.css`, loaded via
`UserAddressInlineAdmin`'s own `class Media` (mirrors
`markdown_editor.css`'s loading pattern). Caps the widest free-text
columns' width, keeps short fields narrow, and makes the inline's own
table scroll horizontally within its card at narrow viewports instead
of widening the page. Kept `TabularInline` — a scoped CSS fix was
enough, no justification to replace it with `StackedInline`.

**5. Product Images real-time ordering — one-line fix, confirmed root
cause**: `product_image_inline.js`'s "exclude deleted rows from the
max-order computation" used `.closest(".dynamic-images")` — confirmed
directly in the *installed* Django's own
`admin/edit_inline/tabular.html` and `inlines.js` that this class is
added only to rows cloned via "Add another"; an existing, already-saved
row's `<tr>` only ever gets `"form-row"` (Django's
`addInlineClickHandler` removes `"empty-form"` from the clone but never
removes `"form-row"`, so that class is present on *every* row either
way). This meant a pre-existing row marked for deletion was never
actually excluded — wrong next position whenever editing a product
that already had images, which is the common case. Fixed by matching
`.form-row` instead.

**Discovered mid-fix, not part of the original bug list**:
`app_account/tests/factories/UserAddressFactory.py` picked
`city`/`state`/`country` from three *independent* sub-factories — this
had always been possible, just invisible until a new formset-level test
built from real factory data tripped the previous task's
`UserAddressBaseForm.clean()` consistency check. Fixed the factory to
derive `state`/`country` from the chosen `city` via `LazyAttribute`.

**Testing infrastructure, user-approved**: real automated coverage for
all three admin JS files, not just manual steps — new `frontend/src/
admin-js/` (`cityLocationSelect.test.ts`, `userAddressInline.test.ts`,
`productImageInline.test.ts`, 14 tests), via a shared harness
(`loadAdminScript.ts`) that `fs.readFileSync`s the actual shipped source
and executes it inside a `JSDOM` window (`runScripts: "dangerously"`,
needed for `document` to resolve as a bare global) built to match
Django's real markup, then dispatches real `change`/`formset:added`
events. This needed one small infrastructure change, confirmed with the
user before making it: `docker-compose.yml`'s `frontend` service didn't
have the repo root's `static/` directory accessible at all (only
`./frontend:/app` was mounted) — added a read-only `./static:/repo-static:ro`
mount so the tests can read the real files via the normal `npm run
test` workflow going forward, not just a one-off invocation. Also added
`tsconfig.admin-js.json` (a new project reference, mirroring the
existing `tsconfig.app.json`/`tsconfig.node.json` split) scoping Node
types to just `src/admin-js/**`, and `@types/jsdom` as a type-only
devDependency (`jsdom` itself ships no types).

**Verification**: `manage.py check`, `makemigrations --check --dry-run`
(none needed), full `pytest` — 207 passed (no regressions), `ruff
check`/`ruff format --check`/`mypy`/`basedpyright` all clean. `tsc -b`,
`eslint .`, full Vitest — 96 passed, `npm run build`. Rendered admin
field order re-verified live via `get_form`/`get_fieldsets()`; all 5
new/changed static assets confirmed served correctly over the live
Nginx/Django stack. **Not verified**: an actual browser click-through —
no Chrome DevTools MCP connection was available this session either;
the jsdom tests are real but synthetic-DOM coverage, and the responsive
CSS layout has no automated check, documented as a manual-verification
item instead.

## 2026-10-16 — Wishlist made real end-to-end (privacy, reorder, public view, product-page integration)

The backend models/signals already existed (see the entries above) but
were wired to nothing — no API, no migration for the new fields, three
inert frontend placeholders. This task built the full feature:

**Backend**: `UserWishlistItemModel.private` (`BooleanField`, default
`False`) and `UserWishlistModel.public_id` (`UUIDField`, `default=uuid4`,
`unique=True`) — the opaque handle for "view a third party's wishlist",
chosen over the numeric user id (enumeration) and over a new slug field
(no public identifier exists anywhere in `app_account` today, confirmed
by a full grep; building one would have been new, larger scope).
Migration `0004_userwishlistitemmodel_private_and_more.py` hand-adjusted
into Django's documented 3-step pattern for adding a unique field with a
callable default (nullable column → `RunPython` per-row backfill →
`AlterField` to enforce uniqueness) — a plain single-step `AddField`
would have given every pre-existing row the identical UUID. Applied and
confirmed (`showmigrations`, then a direct DB check that the existing
row got a real, non-null, distinct `public_id`).

New `WishlistItemViewSet` (list/create/destroy own items +
`toggle-privacy`/`move`/`check`/`share-link` actions, all scoped to
`request.user`, 404 not 403 for another user's item — mirrors
`UserAddressViewSet`) and `PublicWishlistViewSet` (`AllowAny`, looked up
by `public_id`, serializes only `private=False` items through a
serializer that has no `private` field at all). Registered at
`/api/account/wishlist/...` and `/api/account/wishlist/public/...`.

**The `move` action does not reuse `organize_wishlist_items()`** — traced
and proved (via a failing test, written before the fix) that its
anchor-insert algorithm silently undoes an adjacent-swap move, because
excluding the anchor from an already-contiguous list leaves a gap at its
*old* slot rather than a gap-free remainder. `move` instead does a direct
two-row position swap under `select_for_update()`, relying on the
existing `Deferrable.DEFERRED` constraint — see `domain.md` for the full
trace, since this is the kind of thing worth not re-deriving later.

**Frontend**: new `WishlistPage.tsx` (`/profile/wishlist`) and
`PublicWishlistPage.tsx` (`/wishlist/:publicId`), both following
`AddressListPage.tsx`'s override/request-token/abort-controller pattern.
Wired the three previously-inert placeholders:
`AccountLayout.tsx`/`UserMenu.tsx`'s wishlist links now navigate for
real, and `ProductDetailPage.tsx`'s wishlist button now checks real
membership on load and toggles add/remove, with a login link for guests.
"Add to cart" and "Give as a gift" stay inert per the task's explicit
scope — no cart/order logic added. Three new icons
(`ArrowUpIcon`/`ArrowDownIcon`/`GiftIcon`) added to `icons.tsx`, same
hand-inlined-path convention as every existing one. New `wishlist` i18n
section plus `product.removeFromWishlist`, translated into all five
locales (not just English). `apiDelete` added to `client.ts` (the first
DELETE-verb endpoint in this frontend) for the remove action.

**Testing**: `app_account/tests/api/test_wishlist_item_api.py` (34
tests) and `test_public_wishlist_api.py` (8 tests), plus two new model
tests for `private`'s default and isolation. Frontend:
`WishlistPage.test.tsx`, `PublicWishlistPage.test.tsx`,
`ProductDetailPage.test.tsx` (the project's first test of that page as a
whole), `UserMenu.test.tsx` (new file — that component had no tests at
all before). `renderWithProviders` gained an optional `path` option to
support testing any page that calls `useParams()`, which no prior test
needed.

**Verification**: `manage.py check`, `makemigrations --check --dry-run`
(exactly the two expected field additions, nothing swept in),
`showmigrations` before/after `migrate`, full `pytest` — 251 passed (no
regressions), `ruff check`/`ruff format --check`/`mypy`/`basedpyright`
all clean. `tsc -b`, `eslint .`, full Vitest — 117 passed, `npm run
build`. **Not verified**: an actual browser click-through (no Chrome
DevTools MCP connection available this session); all backend/frontend
checks above were run directly against the live containers, and the new
migration was actually applied (not just generated), confirmed via a
direct DB read.

## 2026-10-16 (same day, follow-up) — UserMenu icons, priority display, owner-aware public wishlist link

Three small user-requested adjustments to the wishlist feature above:

- `UserMenu.tsx` (the navbar's "Hello, {name}" dropdown) had no icons at
  all next to its items — added the same icons `AccountLayout.tsx` already
  uses for the same destinations (`UserIcon`/`PencilIcon`/
  `LockClosedIcon`/`ArchiveBoxIcon`/`MapPinIcon`/`HeartIcon`/
  `ShieldCheckIcon`), plus one new icon, `ArrowRightOnRectangleIcon`, for
  logout (no existing icon fit; same hand-inlined-Heroicons-path
  convention as every other icon in `icons.tsx`).
- The "Priority N" label on both wishlist pages showed the word
  "Priority"/"Prioridade" — changed to show just the plain number
  (`item.position + 1`), with the translated label moved to `aria-label`
  for accessibility rather than removed outright.
- `PublicWishlistPage.tsx` always rendered the restricted public-only view
  before, even for the owner visiting their own share link — now checks
  (in the background, via `/account/wishlist/share-link/`) whether the
  signed-in visitor's own `public_id` matches the URL's, and if so swaps
  to rendering `WishlistPage` directly (full own list, private items,
  edit controls) instead. Anonymous/different-user visitors are
  unaffected — the check starts `false` and only flips after confirming
  ownership, so the public view still renders immediately with no added
  request for the common case. See `domain.md`'s Wishlist section.

Verified: `tsc -b`, `eslint .`, full Vitest — 119 passed (two new tests
added for the owner-detection swap, two existing tests updated for the
priority-number change).

## 2026-10-17 — Phone country selector/mask, and precise 60s contact rate limiting

**Root cause of the task's "contact form blocks repeated sends" starting
point, confirmed by reading the real code, not guessed**: DRF's built-in
`ScopedRateThrottle` (`"contact": "5/hour"`), keyed by client IP via
`BaseThrottle.get_ident()`, backed by Django's default cache (which is
genuinely Redis in this Dockerized setup — `CACHES["default"]` →
`django.core.cache.backends.redis.RedisCache`). Already emitted
`Retry-After` automatically. **Found along the way**: this project had
no `NUM_PROXIES` setting anywhere, so `get_ident()` fell back to
`REMOTE_ADDR` — nginx's own container IP behind the reverse proxy for
every request — silently sharing that 5/hour limit across every
anonymous visitor. Fixed with `"NUM_PROXIES": 1` in `REST_FRAMEWORK`
(`PROJECT/settings/rest_framework.py`): nginx is the sole, always-present
proxy (confirmed via `nginx/nginx.conf`), and it honestly sets
`X-Forwarded-For $proxy_add_x_forwarded_for`, so `NUM_PROXIES=1` trusts
only the entry nginx itself appended — this fixes the shared-IP bug for
both the pre-existing throttle and the new one below, for free.

**New 60s-between-accepted-sends cooldown** (`utils/rate_limit.py`,
new): `get_client_identifier(request)` (user pk if authenticated, else
the `NUM_PROXIES`-aware IP — never a client-supplied id) and
`seconds_until_next_allowed(key, interval_seconds)`, built on a single
`cache.add(key, next_allowed_at, timeout=interval_seconds)` call — Redis
`SET NX EX` under Django's cache API — as the atomic "first writer in
the window wins" primitive, closing the check-then-write race a naive
get-then-set would have under concurrent requests. `ContactViewSet.create()`
(`app_core/api/viewsets/ContactViewSet.py`) calls this only *after*
`ContactSerializer.is_valid()` succeeds, so an invalid submission never
starts or consumes the cooldown; a blocked attempt `raise
Throttled(wait=remaining, code="contact_cooldown")`, reusing DRF's own
exception class. A new `handle_exception()` override, scoped to
`ContactViewSet` only, unifies *either* throttle mechanism's resulting
429 into this project's stable-`code` convention:
`{"code", "detail", "retry_after"}`, with `Retry-After` set explicitly —
`login`/`signup`/`password-reset`'s existing 429 shape is untouched.
**Redis-down behavior is deliberately left as-is** (an unhandled
exception, surfacing as a 500) — the same characteristic the pre-existing
5/hour throttle already has via the identical cache backend; giving only
the new piece bespoke fail-open/fail-closed handling would make the two
mechanisms behave inconsistently under the same outage.

**Phone country selector + dynamic mask** (`frontend/src/components/ui/PhoneInput.tsx`,
new): replaces three independent, inconsistent phone implementations —
`SignupPage.tsx`/`ProfileEditPage.tsx` shared a letter-stripping-only
sanitizer (`sanitizePhoneInput.ts`, now deleted along with its test, no
callers left), `ContactPage.tsx` had no sanitization at all. Built on
`libphonenumber-js/min` (chosen specifically because it's the JS port of
the same canonical Google libphonenumber metadata
`django-phonenumber-field`/`phonenumbers` already uses server-side —
front and back end share one ground truth; `/min` for reduced metadata
size, since this project is bundle-size-conscious) — no prebuilt phone
UI widget, consistent with this project's hand-rolled-input convention.
Tracks `country`/national-digits as internal state (seeded from the
incoming E.164 value, defaulting to `"BR"` when empty — matching the
backend's own `PHONENUMBER_DEFAULT_REGION` default); the display mask and
the emitted E.164 value both come from one shared `AsYouType` formatter
pass per change. Country names use `Intl.DisplayNames` keyed to the
current UI language — no static name list. `ContactPage.tsx`'s ad-hoc
`phone.replace(/\D/g,"").length < 10` client check was replaced with the
library's own `isValidPhoneNumber()`. No backend phone-model/validator
code needed changing at all — `PhoneNumberField` already parses a
leading-`+` international string correctly regardless of its configured
region fallback, which is now what every form always sends.

**Contact countdown** (`ContactPage.tsx`): on a 429, reads the body's
`retry_after` (not the header — avoids any cross-origin header-exposure
question) and ticks a `setInterval`-driven countdown, disabling just the
submit button; the deadline is also mirrored into `localStorage` so a
reload mid-cooldown resumes the countdown instead of showing a falsely
enabled button — a client-side convenience only, since the backend
re-checks for real on every actual submit attempt regardless of what the
client remembers. All field values already survived a 429 before this
change and still do.

**Verification**: `manage.py check`, full `pytest` — 270 passed (no
regressions), `ruff check`/`ruff format --check`/`mypy`/`basedpyright`
all clean. `tsc -b`, `eslint .`, full Vitest — 130 passed, run twice to
confirm stability after bumping two tests' timeouts (CPU-contention
flakiness under the full 23-file parallel run, not a logic bug — each
test passed individually before the bump), `npm run build` succeeds
(bundle size grew by the inherent, accepted cost of
`libphonenumber-js/min`'s full per-country metadata). **Not verified**:
an actual browser click-through — no Chrome DevTools MCP connection was
available this session either.

## 2026-10-17 (same day, follow-up) — restrict phone country list, cap length per country

Two adjustments to `PhoneInput.tsx` per direct user feedback:

- The country `<select>` now offers only `["BR", "US", "FR", "IT"]` (a
  fixed `SUPPORTED_COUNTRIES` list) instead of every ITU-assigned region
  — these are the only countries the site currently serves. Display
  names still come from `Intl.DisplayNames`, just restricted to these
  codes; an existing stored value for a country outside this set falls
  back to `"BR"` rather than leaving the `<select>` with an orphaned
  value.
- Typing or switching country now clamps the national number to that
  country's own valid length via `libphonenumber-js/min`'s
  `validatePhoneNumberLength()` — trimming trailing digits until it's no
  longer `"TOO_LONG"` — rather than a hand-maintained max-digits table,
  so it's correct even for Italy's variable-length numbers. Confirmed
  against the user's own example: Brazil now caps at `(69) 99123-4567`
  exactly (11 digits).
- Found, not fixed (out of scope — unrelated to what was asked): France's
  `AsYouType` mask only groups into "XX XX XX XX XX" when fed a leading
  national trunk `0`, which this component never adds, so French numbers
  display as ungrouped (but still correct/valid) digits. See
  `architecture.md`.

Verified: `tsc -b`, `eslint .`, full Vitest — 134 passed (4 new
`PhoneInput.test.tsx` cases: the restricted option list, length clamping
for Brazil and the US while typing, and re-clamping on a country switch
to a shorter-max-length country), `npm run build` succeeds.

## 2026-10-17 (same day, second follow-up) — phone country picker: real flags, clear-on-change, responsive fix

Three more `PhoneInput.tsx` adjustments per direct user feedback (a
reported failure when changing country after typing a number; the
country control taking 100% width on mobile and pushing the phone input
off-screen; wanting to reuse the site's existing flag images instead of
the country name text):

- **Country picker rebuilt as a `Dropdown` (`frontend/src/components/ui/Dropdown.tsx`)
  instead of a native `<select>`**, since a native select's collapsed
  display can only show plain text, never an `<img>`. Mirrors
  `LanguagePicker.tsx` exactly — a flag-only trigger button, a menu with
  flag + name + calling code per option — and reuses the *exact same*
  flag image files the language switcher already ships
  (`/img/locale/{pt-br,en,fr,it}.png`), not a new asset set and not
  emoji (flag emoji render as two-letter codes on some platforms,
  notably Windows). Required one small, fully backward-compatible
  addition to the shared `Dropdown.tsx`: an optional `buttonClassName`
  prop, defaulting to the exact classes `UserMenu.tsx`/`LanguagePicker.tsx`
  already relied on (both left untouched, confirmed by their own tests
  still passing unmodified) — `PhoneInput.tsx` passes its own
  light-background-appropriate classes instead of Dropdown's
  navbar-dark default.
- **Selecting a country now always clears the phone field**, rather than
  preserving and re-clamping the previously-typed digits (the behavior
  from two tasks ago) — a different country's number isn't a
  truncated/extended version of the old one, and the carry-over logic
  was producing the failure the user reported. The user must retype
  after switching.
- **Root cause of the mobile overflow, confirmed**: the old native
  `<select>` reused `inputClassName()`, which bakes in `w-full` —
  depending on Tailwind's own internal utility ordering in the generated
  stylesheet (not the order classes are written in the JSX), that could
  outrank the `w-32`/`sm:w-44` override meant to constrain the select,
  letting it expand to fill the whole row and push the phone number input
  off-screen on narrow viewports. The new Dropdown trigger doesn't use
  `inputClassName` at all (sized to its own content, just the flag),
  removing the conflict outright. The phone `<input>` also gained
  `min-w-0` alongside its existing `flex-1`, since a flex item's default
  `min-width: auto` otherwise refuses to let it shrink below its own
  intrinsic width — the other half of what let the row overflow.

Verified: `tsc -b`, `eslint .`, full Vitest — 133 passed (one obsolete
test describing the old preserve-and-clamp-on-switch behavior replaced
with one asserting the field now clears; `UserMenu.test.tsx` — the only
other `Dropdown` consumer with its own test coverage — still passes
unmodified, confirming the new `buttonClassName` prop didn't change its
behavior), `npm run build` succeeds. **Not verified**: an actual mobile
viewport/browser check — no Chrome DevTools MCP connection was available
this session; the responsive fix is reasoned from the CSS mechanics
(`min-width: auto` on flex items, Tailwind's generated-stylesheet
ordering) and from removing `inputClassName`'s `w-full` from the
equation entirely, not from a visual confirmation.

## 2026-10-17 (same day, third follow-up) — phone placeholder now follows the selected country

`PhoneInput.tsx`'s `placeholder` prop is gone entirely; the old static,
Brazil-formatted i18n strings it took (`auth.phonePlaceholder`,
`contact.phonePlaceholder`) were deleted from `i18n/types.ts` and all 5
locales — genuinely dead once the three call sites (Signup, ProfileEdit,
Contact) stopped passing them. Replaced with a small internal
`PLACEHOLDER_DIGITS` map (one representative national number per
supported country) run through the exact same `AsYouType(country)`
formatter the live mask uses, so the shown example always matches the
real mask instead of a hand-typed string that could drift from it:
Brazil → `(69) 99123-4567`, US → `(202) 555-1234`, France →
`06 12 34 56 78`, Italy → `312 345 6789`. Changing the country swaps the
placeholder immediately, same as every other per-country behavior now.

Verified: `tsc -b`, `eslint .`, full Vitest — 134 passed (one new
`PhoneInput.test.tsx` case confirming the placeholder for the initial
country and after switching to the US), `npm run build` succeeds.

## 2026-10-17 (same day, fourth follow-up) — wishlist: silent privacy toggle, public priority renumbering

Two small, unrelated fixes to the wishlist feature, both per direct user
feedback:

- Toggling an item's privacy on `WishlistPage.tsx` no longer shows a
  success alert — it just updates, matching how move-up/move-down already
  behave. The now-unused `wishlist.privacyUpdated` i18n key was removed
  from `types.ts` and all 5 locales.
- `PublicWishlistPage.tsx`'s displayed priority number is now the item's
  index within the *visible* (public-only) array (`index + 1`), not
  `item.position + 1`. Root cause: `position` lives in the same numbering
  space as the owner's hidden private items, so once the backend filters
  those out, the public list's stored positions can have gaps (e.g.
  0, 2, 3) — showing those raw numbers to a non-owner looked broken.
  `WishlistPage.tsx` (the owner's own view, which always sees every item)
  is unaffected and still uses `item.position + 1` directly.

Verified: `tsc -b`, `eslint .`, full Vitest — 135 passed (one new
`PublicWishlistPage.test.tsx` case feeding items with gapped stored
positions and asserting the displayed priority is still sequential
1/2/3; `WishlistPage.test.tsx`'s privacy-toggle test extended to assert
no `alert`/`status` message appears).

## 2026-10-17 (same day, fifth follow-up) — wishlist sorting (name/price/date added, both directions)

New `frontend/src/components/wishlist/` directory (first use — the row
components for both wishlist pages previously lived inline in their page
files, with no shared wishlist-specific component folder yet):
`wishlistSort.ts` (`WISHLIST_SORT_OPTIONS`, `sortWishlistItems`) and
`WishlistSortSelect.tsx`, added to both `WishlistPage.tsx` and
`PublicWishlistPage.tsx` per the user's explicit request for something
"semelhante à lista de produtos."

Deliberately **not** a port of the product list's server-side `ordering`
query param: the wishlist is always fetched whole in one request (no
pagination), so sorting it is a pure client-side array sort with no
round trip and no backend change at all. Options: name A-Z/Z-A, price
low-high/high-low, date added oldest/newest-first, plus a `"priority"`
default (no secondary sort — shows the stored `position` order as-is,
same array reference returned unchanged).

On the owner's own page, selecting any sort other than `"priority"`
disables the move up/down buttons — reordering by priority only makes
sense while the list is actually *displayed* in priority order, so
letting a click "move" an item while sorted by price would jump it to a
visually unrelated spot. Verified the boundary-button logic (`isFirst`/
`isLast`) stays correct once switching back to priority, since
`sortWishlistItems` returns the untouched array (not a new one) for that
case.

Verified: `tsc -b`, `eslint .`, full Vitest — 148 passed (10 new
`wishlistSort.test.ts` unit tests for all 7 sort values plus a
no-mutation check; 2 new `WishlistPage.test.tsx` cases — sort reorders
the list and disables move buttons, switching back to priority
re-enables them; 1 new `PublicWishlistPage.test.tsx` case confirming
sorting also renumbers the displayed priority column), `npm run build`
succeeds.

## 2026-10-17 (same day, sixth follow-up) — full name now requires first and last name

**Root cause, confirmed by reading both validation paths directly**: the
`name` field was validated in two independent places that had drifted
apart. `ContactSerializer` already used `utils/validator.py`'s
`validate_name()` — but that function only checked "non-empty" and "has
at least one letter," never word count. `NormalizedNameFieldMixin`
(signup/profile-edit/admin forms) didn't call `validate_name()` at all —
it had its own separate `len(name) < 3` **character**-count check,
which a single short name like "Ana" (3 characters) sails through. Fixed
by extending `validate_name()` itself (the one place both paths can
share) to also require at least two whitespace-separated parts that each
contain a letter, then wiring `NormalizedNameFieldMixin.clean_name()` to
actually call it (kept its existing length check too — not fully
redundant, no reason to remove it). `ContactSerializer` needed zero code
changes, since it was already calling the now-fixed shared function.

This one shared fix covers signup, profile-edit, and the Django Admin's
user-creation/edit forms (all three use `NormalizedNameFieldMixin`) plus
the contact form — confirmed each path independently with a real HTTP
request in the tests, not just reasoned about. Frontend: `ContactPage.tsx`
gained a matching client-side `hasFullName()` check (replacing its old
`length < 3` one) in its existing bespoke `validate()` function;
`SignupPage.tsx` got no new client-side gate, matching this session's
established pattern of not touching the shared `useApiForm` hook for a
single new per-field rule — the (now-correct) backend remains the real
enforcement point regardless. All 5 locales' `contact.nameError` string
updated to describe the actual rule instead of a character count.

Verified: `manage.py check`, full `pytest` — 283 passed including 8 new
direct unit tests for `validate_name()` (`app_core/tests/test_validators.py`,
first direct tests for anything in `utils/validator.py`) and new
integration tests on signup/profile-update/contact, no regressions;
`ruff`/`mypy`/`basedpyright` clean. `tsc -b`, `eslint .`, full Vitest —
150 passed, `npm run build` succeeds. Attempted an actual live
browser check now that the Chrome DevTools MCP connection succeeded for
the first time this session — still blocked, but by a different, more
fundamental cause than before: no Chrome binary is installed in this
environment at all (`new_page` failed looking for `chrome.exe` in every
standard install path), not a connection/config issue. Noted for
whoever reads this later: a working live-browser check needs Chrome
actually installed, not just the MCP server reachable.

## 2026-10-18 — fixed the new full-name error always showing in English

**User report**: "no cadastro do usuário independente do idioma
selecionado, está retornando o erro em inglês" (the signup error comes
back in English no matter which language is selected) — referring
specifically to the four messages added in the previous entry above.

**Root cause, confirmed with a real HTTP request, not guessed**: it was
never a `LocaleMiddleware`/language-activation bug. A POST to
`/api/account/signup/` with `Accept-Language: pt-br` and an invalid
`password2` correctly returned Django's own built-in password-validator
errors already translated to Portuguese — proving language activation
itself works. Only this project's **own** `gettext_lazy()` strings
stayed in English, because the backend's gettext catalogs
(`locale/{en,es,fr,it,pt_BR}/LC_MESSAGES/django.po`) are almost entirely
empty: only 3 real translated strings existed in each file, project-wide,
before this fix — Django's and third-party packages' own shipped
catalogs cover their own messages regardless, which is why this gap had
never been noticed before. This also means the original, pre-existing
"The name must be 3 characters." message was *always* untranslated too,
not something this specific bug introduced.

**Fix**: added the 4 messages from the full-name validation chain
(`"The name must be 3 characters."` from `NormalizedNameFieldMixin.py`;
`"The name cannot be empty."`, `"The name must contain at least one
letter."`, `"Enter your full name (first and last name)."`, all three
from `utils/validator.py`) to **all 5** `locale/*/LC_MESSAGES/django.po`
files, including `en` as identity translations (msgstr == msgid, matching
this file's own existing convention), then ran `manage.py
compilemessages -l en -l es -l fr -l it -l pt_BR` to regenerate the `.mo`
binaries Django actually reads at runtime (scoping to just these 5
locales, rather than the default no-args form, which also needlessly
re-walks and recompiles every third-party package's own bundled catalogs
across dozens of unrelated languages).

**Scope decision**: deliberately limited to these 4 messages — confirmed
via inspection that no other custom-string messages exist in the
email/date_birth/phone form mixins this session touched. The broader
finding that this project's backend custom-string catalogs are
essentially empty everywhere else is a real, larger pre-existing gap,
flagged here rather than silently fixed in full, since auditing and
translating every custom backend string project-wide was not what was
asked and is a much bigger, separate undertaking.

**Verified**: reran the diagnostic request with `Accept-Language: pt-br`
— `name` error now returns `"Informe seu nome completo (nome e
sobrenome)."` (previously the English string), `password2` unaffected.
Deleted the temporary diagnostic test file
(`app_account/tests/test_zzz_lang_debug.py`) used to reproduce/confirm
this. Full backend suite re-run after the catalog/compile change: 283
passed, no regressions (translation-only change, as expected).

## 2026-10-18 (same day, follow-up) — French/Italian still showed English; `LANGUAGES` itself was missing them

**User report**: "Está corrigido para português, mas ainda apresentando
falha em outros idiomas." (fixed for Portuguese, but still failing in
other languages) — reported immediately after the entry above.

**Root cause, confirmed with a second real HTTP request per locale**: a
POST with `Accept-Language: es` came back fully translated (both the
custom `name` message and Django's own `password2` messages), but `fr`
and `it` came back **entirely** in English — including Django's own
built-in `password2` messages, which proved this wasn't a catalog-content
issue at all (those two locales' catalogs on disk were already correct —
see the previous entry). The actual cause: `PROJECT/settings/
internationalization.py`'s `LANGUAGES` tuple only declared `("pt-br",
"en"), ("es", ...)` — `fr`/`it` were never in Django's own list of active
locales, so `LocaleMiddleware` silently fell back to `LANGUAGE_CODE`
("en") for any `Accept-Language: fr`/`it` request, regardless of what the
catalogs contained. This is the same gap already flagged as a known,
pre-existing limitation in `.claude/context/domain.md` before today, now
actually fixed rather than just documented.

**Fix**: added `("fr", "Français")` and `("it", "Italiano")` to
`LANGUAGES`. Confirmed no other backend code hardcodes the 3-language
list (grepped for `LANGUAGE_CODE`/`get_language()`/language-tuple
patterns project-wide — only this one setting controls which locales
`LocaleMiddleware` will activate). Restarted the `backend` container
(Gunicorn workers don't reload on a bind-mounted source change) and
re-verified: `fr` and `it` now both return their own translated `name`
message; `fr`'s `password2` messages are also now fully translated by
Django's own shipped `fr` catalog. One exception found and left as-is:
Italian's `password2` "too short" message stays in English even now —
confirmed this is Django's own upstream `it` catalog being incomplete
for that one specific built-in string, not something fixable in this
project's own `.po` files, and out of scope to patch around.

Also removed a now-stale explanatory comment in `frontend/src/i18n/
languages.ts` that described this exact mismatch (frontend fully
supporting fr/it, backend not) — no longer true. Updated
`.claude/context/domain.md`, `conventions.md`, `project_state.md`,
`structure.md`, `.claude/CLAUDE.md`, and `.claude/commands/
{feature,review}.md`, all of which had explicitly documented "`LANGUAGES`
currently only activates pt-br/en/es" as a known, accepted limitation —
that limitation no longer holds, though the broader "most backend
strings aren't in the catalogs at all" gap remains and is still flagged.

**Verified**: `manage.py check` clean. Full `pytest` re-run after the
settings change — 283 passed, no regressions. Deleted the second
temporary diagnostic test file
(`app_account/tests/test_zzz_lang_debug2.py`) used to confirm the fix
across `es`/`fr`/`it` in one parametrized run.

## 2026-10-18 (same day, second follow-up) — `PhoneInput`: backspace next to a mask literal did nothing

**User report**: typing a wrong Brazilian area code (DDD) and trying to
backspace it out got stuck — pressing Backspace right after the area
code's `)` didn't remove anything, "o ) não some". Same symptom reported
for US numbers.

**Root cause**: `PhoneInput.tsx`'s `onDigitsChange` rebuilds `digits` by
stripping all non-digit characters out of the raw `<input>` value on every
keystroke. When the caret sits right after a mask literal (the `)` after
an area code, a `-`, etc.) and the browser's native Backspace removes
that one literal character, the digit sequence underneath is completely
unchanged — so the very next render re-masks the identical digits back
into the identical display string, including re-inserting the same `)`.
Visually indistinguishable from Backspace doing nothing.

**Fix**: added an `onKeyDown` handler on the phone `<input>` that, only
for a collapsed-caret Backspace/Delete landing on a mask literal (not a
real digit, and not an actual text selection — both of those still fall
through to the existing, already-correct `onChange` path unchanged),
`preventDefault()`s the native edit and instead removes the adjacent
digit directly from the `digits` state itself (the nearest digit before
the caret for Backspace, the nearest one at/after it for Delete) — then
restores the caret to just after that digit's new position via a
`useLayoutEffect` keyed on the recomputed mask, so repeated Backspace
presses keep working naturally instead of getting stuck or jumping to the
end. Two small pure helpers (`digitsBefore`, `positionAfterDigit`) do the
display-string-index ↔ digit-index mapping; no new dependency, no change
to the already-correct typing/paste path.

**Verified**: added 2 regression tests (`PhoneInput.test.tsx`) — Backspace
right after the BR and US area codes' `)` now actually removes a digit
(confirmed against `libphonenumber-js`'s real `AsYouType` output run
directly in the frontend container, not guessed) instead of leaving the
value unchanged. Full frontend suite: `tsc -b` clean, `eslint .` clean,
full Vitest — 152 passed (was 150), no regressions.

## 2026-10-18 (same day, third follow-up) — product card: title and image now link to the details page too

**Request**: on the product listing, make the title and image act like the
existing "Details view" button — clicking either should also navigate to
the product's detail page.

**Change** (`frontend/src/components/product/ProductCard.tsx`): wrapped
the thumbnail image (and the no-thumbnail placeholder, which occupies the
same visual slot) and the `<h3>` title text each in their own
`<Link to={`/product/${product.slug}`}>`, reusing the exact same
destination the "Details view" button already links to. The "Add to
cart" button is untouched (still its own separate control; cart itself
remains unimplemented — see `domain.md`'s Wishlist/cart section).

**Verified**: new `ProductCard.test.tsx` (first dedicated test file for
this component) — image, no-image placeholder, and title all link to
`/product/<slug>`. Full frontend suite: `tsc -b` clean, `eslint .` clean,
full Vitest — 155 passed (was 152, +3 new), no regressions.

## 2026-10-18 (same day, fourth follow-up) — removed the redundant "Categories" heading from the navbar's category dropdown

**Request**: remove "Categories" from the top navbar's category dropdown.

**Change** (`frontend/src/components/layout/Navbar.tsx`): the dropdown's
trigger button is already labeled with `t.nav.category` ("Category"); the
open menu additionally repeated an uppercase "Categories" heading above
the list of actual category links — removed that heading `<p>`, since the
button label already identifies what the menu is. Confirmed via grep that
`t.nav.categories` had no other callers, so removed the now-dead key from
`i18n/types.ts` and all 5 locale files rather than leaving an unused
translation behind (this project's convention). Left the unrelated
`product.categoriesTitle` key (a different dropdown, used by the product
list's category filter) untouched — same English word, different
component, not part of this request.

**Verified**: `tsc -b` clean, `eslint .` clean, full Vitest — 155 passed,
no regressions (no test asserted the removed heading, backend untouched).
