# Known Issues

Populated from a full repository analysis on 2026-10-11 (5 parallel
Explore agents covering backend, frontend, infrastructure, testing, and
the existing `.claude/`/dependency/git state). Each entry marks whether it
is a confirmed fact (verified directly in source/config) or a hypothesis
needing further runtime verification.

## Confirmed

1. **Migrations are not committed to git.** `git ls-files | grep
   migrations` shows only each app's `migrations/__init__.py` is tracked;
   real migration files exist on local disks but not in version control.
   `.gitignore` has a bare `migrations/` rule (with a comment marking it
   "temporary, remove closer to production") that directly contradicts a
   later comment in the same file saying migrations must never be
   ignored. **Impact**: a fresh clone cannot run `manage.py migrate`
   successfully for any app. Unresolved — needs a user decision (commit
   them now, or keep ignoring deliberately and fix the contradictory
   comments). Re-confirmed 2026-10-13 during the `app_` rename migration —
   unaffected by that rename either way (the `.gitignore` rule still
   applies regardless of package name).
2. **Weak hard-coded fallback superuser.**
   `app_account/signals/create_default_superuser.py` creates
   `admin@example.com` / `admin123` on `post_migrate` whenever no
   superuser exists and `DJANGO_SUPERUSER_*` env vars are unset. The
   separate `create_admin` management command (run by `entrypoint.sh` on
   every container start) does the same job but raises instead. Running
   `migrate` without the env vars set, anywhere, silently creates a
   guessable admin account. Unresolved.
3. ~~**`UserAddressModel`'s address forms are dead code.**~~ **Resolved
   2026-10-11.** `UserAddressModel.save()` now enforces "at most one
   primary address per user" directly on the model (mirroring
   `ProductImageModel`'s pattern exactly: lock the parent user row,
   demote siblings, plus `validate_constraints`/`_get_unique_checks`
   overrides so admin inline formsets don't choke on transient
   multi-primary submissions). `UserAddressAdmin` (standalone, with a
   `get_form()` create/update split) and `UserAddressInlineAdmin`
   (attached to `UserAdmin.inlines`) both exist and were verified against
   the real admin over HTTP, including submitting two inline rows marked
   primary in the same request. The exclusivity logic that used to live
   in the form's `save()` was removed — the model is now the single
   source of truth, reusable by a future API too, per the project's own
   stated preference. `UserAddressAdmin`/`UserAddressInlineAdmin` had
   also drifted to reference nonexistent fields (`address`, `zip_code`,
   `is_primary`) before this fix — `manage.py check` was failing with
   `admin.E108` until corrected.
4. **`README.md` and `docs/render.md` describe a `backend/` subdirectory
   that does not exist.** Both repeatedly reference `backend/Dockerfile`,
   `backend/PROJECT/settings/...`, `backend/venv-ecommerce`, etc. The real
   repo has Django at the root with no `backend/` prefix — confirmed by
   directory listing and by `pyproject.toml`'s own `[tool.pyright]
   include` list (root-relative paths). Git history confirms this is a
   genuine regression in the docs, not a misunderstanding: commit
   `13d7c01 "Removed 'backend' from the path"` shows the prefix used to be
   real and was deliberately removed; the docs were never updated after
   that. The earlier draft of `.claude/CLAUDE.md` had the exact same
   error (fixed as part of this task — see `changelog.md`).
5. **`docs/render.md` disagrees with the actual `render.yaml`.** The doc
   claims `render.yaml` sets `dockerfilePath`/`dockerContext` to
   `./backend`; the real file sets `./Dockerfile` / `.` (root).
6. **`app_account/forms/UserUpdateForm.py`'s `Meta.model` is a type
   annotation, not an assignment** (`model: UserModel` instead of
   `model = UserModel`). Currently latent/undetected because the form is
   never instantiated anywhere in the codebase. Will raise
   Django's "class Meta ... must have a model attribute" the moment
   someone tries to use it.
7. **Several other forms/helpers are dead code**: `PasswordChangeForm`,
   `UserUpdateForm` (zero usages beyond their own `__init__.py` export),
   `app_core/forms/ContactForm.py` (unused — `ContactSerializer` duplicates its
   validation independently, risk of the two drifting apart),
   `app_product/context_processors.py:context_processors_product_categories`
   (never registered in `TEMPLATES["OPTIONS"]["context_processors"]`).
8. **`django-guardian` is installed and backend-registered but has zero
   actual usage** (no `assign_perm`, no object-level permission checks
   anywhere). Does not currently provide any real protection.
9. **Database/Redis/RabbitMQ/CloudBeaver ports are published to the host**
   in `docker-compose.yml` (5432, 6379, 5672+15672, 8978) while
   `backend`/`frontend` are deliberately internal-only. Fine on an
   isolated dev machine; a real exposure risk if this compose file is
   ever run on a non-isolated host (the same VPS whose IP is hard-coded
   into `nginx/nginx.conf`, for instance).
10. **`nginx/nginx.conf` uses a self-signed TLS certificate**, not a real
    one — confirmed by actually running `certbot` against production
    Let's Encrypt, which refused with "will not issue certificates for a
    bare IP address." The server is identified by IP
    (`177.222.210.50`), not a domain. Browsers show a trust warning.
    Getting a real certificate requires a domain name pointed at that IP.
11. **`.env-example` is missing `INTERNAL_IP`**, a real variable present
    in the actual `.env` and consumed by
    `PROJECT/settings/debug_toolbar.py`.
12. **No shopping cart/checkout/order implementation exists anywhere** —
    backend and frontend both confirmed via repo-wide search. Frontend
    cart/wishlist/orders/profile UI elements are inert placeholders.
13. **No CI/automation exists** (no `.github/workflows/`, no `Makefile`,
    no pre-commit hooks). All checks are run by hand.
14. ~~**Zero frontend test infrastructure.**~~ **Partially resolved
    2026-10-13.** Vitest + React Testing Library installed (see
    `../context/testing.md`/`dependencies.md`), with 14 passing tests
    covering `AccountLayout`/`ProfilePage`/`ProtectedRoute`. The project
    had initially deferred this when asked during the same task, then
    asked for it to be added after all. Everything else in the frontend
    (every other page/component) still has zero test coverage — the
    infrastructure exists now, but adoption is just starting.
15. **`app_address/` and `app_core/` apps have zero backend tests.**
16. **`.claude/commands/`, `.claude/context/`, `.claude/memory/` were all
    completely empty (0 bytes)** before this task — fixed as part of this
    documentation pass (see `changelog.md`).
17. ~~**Each app's `AppConfig.name` still said the old bare package name
    after the directory rename to `app_`.**~~ **Resolved 2026-10-13.**
    `app_core/apps.py`, `app_account/apps.py`, `app_product/apps.py`, and
    `app_address/apps.py` all still had `name = "core"` (etc.) after their
    directories moved to `app_core` (etc.) — Django resolves the app
    module to import from this exact attribute at startup, so the backend
    container failed to boot at all
    (`django.core.exceptions.ImproperlyConfigured: Cannot import 'core'`).
    Fixed by setting `name = "app_core"` (etc.) and adding an explicit
    `label = "core"` (etc., the old short name) on each — see
    `changelog.md` and `structure.md`'s "Django apps" section for the
    full name/label table and why the label was deliberately not
    renamed.

18. **Backend container needs a manual restart after code changes —
    forgetting this caused a real production-visible crash.** `ecommerce_django`
    runs Gunicorn (`--workers 3`, no `--reload`), not `manage.py runserver`,
    so editing Python source under the bind-mounted `/app` does **not**
    take effect until the container is restarted. During the 2026-10-13
    profile-page task, `UserSerializer.py` was extended to add
    `date_birth`/`phone`/`created_at`, validated thoroughly via `docker exec
    ... pytest`/shell (which run fresh processes and did pick up the
    change) — but the long-running Gunicorn workers kept serving the old
    3-field serializer. The frontend's new `ProfilePage.tsx` assumed those
    fields always exist (per the `SessionUser` TS type) and threw
    (`undefined.split(...)` in `parseDateBirth`) when they were silently
    missing from the real `/api/account/session/` response, crashing the
    whole React tree (no error boundary exists) into a blank white page
    after the navbar briefly flashed — reported live at
    `https://177.222.210.50/profile`. Fixed by `docker compose restart
    backend`. Resolved for this specific incident, but the underlying
    gap — no automatic reload, nothing enforces "restart after backend
    edits" — is unresolved and will bite again for any future backend
    change that isn't followed by an explicit restart. See
    `architecture.md`.

## Lower-severity / cosmetic

- `.gitignore`'s `!.env.example` negation line references a filename
  (`.env.example`, with a dot) that doesn't match the project's actual
  `.env-example` (with a hyphen) — likely dead/ineffective, though
  harmless.
- `frontend/src/App.css` is a 0-byte file, not imported anywhere — a
  leftover from the Vite starter template.
- `frontend/README.md` is still the generic, unedited Vite+React+TS
  template text.
- `frontend/src/config/company.ts` reads several `VITE_COMPANY_*` env vars
  that are undocumented in `.env-example`/`.env` (all have hardcoded
  fallbacks, so nothing breaks — just undiscoverable).
- Only 3 real translatable strings exist across all 5 backend locale
  catalogs combined — i18n infrastructure is wired correctly but very
  sparsely populated.

## Needs further verification (not yet confirmed at runtime)

- Whether `manage.py migrate` actually succeeds from a genuinely fresh
  clone today, given the missing migrations (strong circumstantial
  evidence it would not, but not executed as part of this analysis).
- Exact precedence when a user account has **both** `is_active=False` and
  `is_email_verified=False` simultaneously at login — not traced in
  `LoginForm.clean()`/`__get_login_error()` during this pass.
