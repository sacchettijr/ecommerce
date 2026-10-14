# Current Task

## Objective

Migrate the legacy Django-template authenticated-user experience
(`frontend.old/accounts/profile_base.html`/`profile_detail.html`,
reference only) to the current React frontend: a reusable authenticated
layout, a profile home page showing real user data, route protection,
and nav wiring — requested 2026-10-13.

## Status: Complete, including frontend tests and a follow-up live bug fix

1. Extended `/api/account/session/` (via `UserSerializer`) to expose
   `date_birth`, `phone`, `created_at` — the only backend change,
   reusing the existing single current-user endpoint instead of creating
   a new one.
2. Built `AccountLayout.tsx` (sidebar + content + message/alert area),
   `ProfilePage.tsx` (consumes `useAuth().user` only), `ProtectedRoute.tsx`
   (route guard), and `useMessages.ts` (reusable dismissible-message
   queue), plus a small `Alert.tsx` extension and 4 new icons.
3. Registered `/profile` in `App.tsx` behind `ProtectedRoute`; wired
   `UserMenu.tsx`'s "Perfil" item to it.
4. Added full translations (5 locales) for all new user-facing strings.
5. Updated the one backend test whose exact session-payload assertion
   needed the 3 new fields (plus a timezone-conversion fix to match
   DRF's serialized offset).

## Validation performed

Frontend: `tsc -b`, `eslint .`, `npm run build` — all clean.
Backend: `manage.py check`, `makemigrations --check --dry-run` (no
changes needed), full `pytest` (104 passed), `ruff check`/`ruff format
--check`, `mypy`, `basedpyright` — all clean.

## Frontend tests (installed after an initial "skip for now")

Asked the user whether to install a frontend test framework (project had
none) to cover the new `AccountLayout`/`ProfilePage`. The user initially
chose to skip it, then asked for it to be added after all (same
conversation, while reporting the live bug below). Installed Vitest +
React Testing Library and wrote 14 tests covering `AccountLayout`,
`ProfilePage`, and `ProtectedRoute` — see `changelog.md`/`testing.md`.
Frontend test coverage elsewhere in the app is still zero.

## Live bug found and fixed: blank `/profile` page

User reported `https://177.222.210.50/profile` showing the navbar
briefly then going blank. Root cause: `ecommerce_django` runs Gunicorn
with no autoreload, so it kept serving the pre-extension `UserSerializer`
(missing the 3 new fields) even though the source file was already
correct — the long-running workers never picked up the earlier edit.
`ProfilePage.tsx` assumed those fields always exist and threw rendering
them, crashing the whole React tree (no error boundary). Fixed with
`docker compose restart backend`; reproduced and verified the fix with a
real Playwright/Edge session against the live site (throwaway test user,
created and deleted via Django shell). See `known_issues.md` for the
standing process gap this revealed (no backend autoreload).

## Not touched (out of scope for this task)

- `frontend.old/` — read as reference only, never modified.
- No new account pages were built for edit profile/change
  password/orders/addresses/wishlist — those sidebar/dropdown items stay
  inert, matching the project's existing treatment of the same items
  elsewhere, since none of those pages exist yet.
- No cart/checkout/order work — unrelated to this task.
