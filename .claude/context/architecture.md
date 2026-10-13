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
  this pattern. `UserAddressModel.save()` follows the same pattern (see
  `domain.md`) — if you add an address API, reuse the model's rule rather
  than duplicating it in a new serializer.
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
- There is currently **no route-guarding abstraction** (no
  `ProtectedRoute`/`RequireAuth` component) because there is currently
  nothing that needs one — every existing route is public. If/when an
  account-only page is added (profile, addresses, orders), build this
  abstraction then; do not assume one already exists.

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
