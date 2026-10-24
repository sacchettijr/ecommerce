# Current Task

## Objective

Fix: the full-name validation error (added in the previous phase) always
displayed in English on signup, regardless of the selected site language.

## Status: Complete

See `changelog.md` (2026-10-18 entry) for full detail. Highlights:

- Root cause: not a `LocaleMiddleware` bug — confirmed via a real HTTP
  request that Django's own built-in messages (e.g. password validators)
  already translate correctly. Only this project's own custom
  `gettext_lazy()` strings were affected, because the backend's
  `locale/*/LC_MESSAGES/django.po` catalogs are almost entirely empty
  (only 3 real translated strings existed per file, project-wide, before
  this fix).
- Fix: added the 4 full-name-validation messages to all 5 locale `.po`
  files (`en` as identity translations), then ran `manage.py
  compilemessages -l en -l es -l fr -l it -l pt_BR` (scoped — the no-args
  form needlessly recompiles every third-party package's own bundled
  catalogs across dozens of unrelated languages and is very slow).
- Scope deliberately limited to these 4 messages. The broader gap —
  this project's custom backend strings being largely untranslated
  elsewhere too — was not fixed project-wide, since that's a much larger,
  separate undertaking; flagged in the changelog for future awareness.

## Verification

Reran the diagnostic HTTP request with `Accept-Language: pt-br`: `name`
error now returns translated text. Deleted the temporary diagnostic test
file used to confirm this. Full backend suite re-run after the
catalog/compile change: 283 passed, no regressions.

## Not verified live

No real browser click-through (no Chrome binary installed in this
environment) — verification above is the automated test suite plus one
direct HTTP-level check, not a manual UI click-through.
