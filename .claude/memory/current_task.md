# Current Task

## Objective

Fix bugs reported in the previous task's address country/state/city
cascade and Product admin field reorder/image-ordering JS; add a
primary-address selection UX (the address equivalent of the ProductImage
one, which genuinely didn't exist yet); reorder User Address fields to
Country/State/City; make the address inline responsive.

## Status: Complete

See `changelog.md` (2026-10-16 entry, second one that day) for the full
file list and verification results. Highlights:

- **Confirmed root causes before touching anything** (not guessed): the
  `state` field had no widget stamping `data-country` onto its options
  (unlike `city`'s `CityLocationSelect`); `CitySimpleSerializer` didn't
  return `state`/`country`, so AJAX-rebuilt city options lost their
  sync data; `product_image_inline.js` excluded deleted rows via
  `.closest(".dynamic-images")`, a class Django's own `inlines.js` only
  adds to *newly-added* rows, never existing ones — confirmed directly
  against the installed Django's template and JS source.
- **New `StateLocationSelect` widget** (mirrors `CityLocationSelect`)
  plus a generalized `rebuildOptions()` in `city_location_select.js`
  fixed the cascade in both directions; a per-field request-token guards
  against a stale fetch response winning over a newer one.
- **A real, separate bug surfaced while testing the fix**:
  `UserAddressFactory` picked `city`/`state`/`country` from three
  independent sub-factories — harmless until the new form-level
  consistency validation (from the previous task) made a formset test
  using real factory data fail. Fixed the factory to derive `state`/
  `country` from the chosen `city`.
- **Primary-address JS is new**, not a fix — `user_address_inline.js`,
  mirroring `product_image_inline.js`'s checkbox-exclusivity listener.
  Also fixed the *address* equivalent of last task's ProductImage signal
  bug: `promote_primary_address_after_delete.py` trusted a deleted
  instance's stale `primary` attribute the same way.
- **New jsdom-based tests for all three admin JS files** (14 tests,
  `frontend/src/admin-js/`) — genuinely execute the real shipped source,
  not a reimplementation. Required a small, deliberate infrastructure
  change (user-approved): `docker-compose.yml`'s `frontend` service now
  also mounts the repo root's `static/` read-only, since that's where
  these files actually live and the container didn't have access to it
  before.

## Verification

Backend: `manage.py check`, `makemigrations --check --dry-run` (none
needed), full `pytest` — 207 passed, `ruff`/`mypy`/`basedpyright` clean.
Frontend: `tsc -b`, `eslint .`, full Vitest — 96 passed, `npm run build`.
Live-verified: all 5 new/changed static assets served correctly;
rendered admin field order checked via `get_form`/`get_fieldsets`
directly for both the standalone address admin and the inline.

## Not verified live

No real browser click-through this session either (Chrome DevTools MCP
still fails to connect) — the jsdom tests substitute genuine, if
synthetic-DOM, coverage for the three JS files; the responsive CSS
layout (section 4) has no automated check at all and needs a manual
look at narrow viewport widths — exact steps in the final report.
