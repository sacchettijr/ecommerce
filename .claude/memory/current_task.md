# Current Task

## Objective

Implement the Wishlist feature end-to-end (frontend + backend): per-item
privacy (public/private), owner-controlled reordering, a page to view
one's own wishlist and a third party's, add/remove from the product
detail page, and the required tests — building on the existing but
entirely unwired `UserWishlistModel`/`UserWishlistItemModel`.

## Status: Complete

See `changelog.md` (2026-10-16, "Wishlist made real end-to-end" entry)
for the full file list and verification results. Highlights:

- User resolved the one genuine open design question (no existing public
  user identifier anywhere in the app) by choosing an opaque `public_id`
  (UUID) on `UserWishlistModel` over the numeric user id or a new slug
  field.
- Found and fixed a real bug in the plan before shipping it: the `move`
  (up/down) action can't correctly reuse `organize_wishlist_items()` —
  proved via a failing test, then replaced with a direct two-row position
  swap under `select_for_update()`. See `domain.md`.
- Migration needed a hand-written 3-step backfill (not a plain
  `AddField`) because `public_id` is both unique and has a callable
  default — see `database.md`.

## Verification

Backend: `manage.py check`, `makemigrations --check --dry-run`, full
`pytest` — 251 passed, `ruff`/`mypy`/`basedpyright` clean. Frontend:
`tsc -b`, `eslint .`, full Vitest — 117 passed, `npm run build`.
Migration applied and confirmed via a direct DB read (existing row got a
real, distinct `public_id`; `private` defaulted correctly).

## Not verified live

No real browser click-through this session (Chrome DevTools MCP still
fails to connect) — all verification above is automated tests + direct
backend introspection, not a manual click-through of the new pages.
