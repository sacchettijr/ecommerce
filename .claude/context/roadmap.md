# Roadmap

## Documented plans (explicitly stated somewhere in the repo)

- **Render as the hosted prototype target** — `render.yaml` and
  `docs/render.md` are real, current, and consistent with each other
  (modulo the `backend/`-path errors noted in `../memory/known_issues.md`). The
  documented limitations (ephemeral media on the free tier, no Celery/
  Redis/RabbitMQ on Render, service sleep, Postgres free-tier limits) are
  accepted tradeoffs, not bugs to fix.
- **HTTPS via a real domain, eventually** — `docs/render.md`/`nginx.conf`
  history shows HTTPS work was deliberately staged: HTTP first, then a
  self-signed certificate as an interim step (Let's Encrypt cannot issue
  for a bare IP), with the explicit understanding that a real certificate
  requires registering a domain name pointed at the deployed IP. This is
  the clearest "next step" actually written down anywhere in the project.
- **`.claude/CLAUDE.md` section 14** lists plugins/integrations the user
  *intends to evaluate*: `claude-mem`, "Claude Code Setup", "Omni Route",
  `security-guidance`, `code-review`, Context7, `typescript-lsp`,
  Playwright, `claude-md-management`, Supabase, Chrome DevTools. Of these,
  `.claude/settings.json`'s `enabledPlugins` confirms 7 are actually
  enabled today: `security-guidance`, `code-review`, `claude-code-setup`,
  `claude-md-management`, `context7`, `typescript-lsp`,
  `chrome-devtools-mcp`. `claude-mem`, "Omni Route", Playwright, and
  Supabase remain intent-only, not installed. Do not assume any of these
  provide capabilities beyond what's actually enabled.

## Suggested next steps (this review's own suggestions, not project commitments)

These are findings from this analysis task, not pre-existing project
decisions — present them to the user as suggestions, not facts about
planned work:

- `UserAddressModel` now has admin support (2026-10-11); a public API for
  it is still a reasonable next step if user-facing address management is
  needed.
- Commit migrations to git, or make a deliberate, documented decision not
  to (and fix the contradictory `.gitignore` comments either way).
- ~~Add a frontend test framework...~~ **Done** — Vitest + React Testing
  Library has been in active use since 2026-10-13, with 96+ tests across
  pages/components/hooks/the admin-JS jsdom harness as of 2026-10-16 (see
  `testing.md`). The safety net exists now; the open question is
  coverage *breadth* (most pages/components still have none), not
  framework adoption.
- If/when a cart is actually built, it is a from-scratch feature, not an
  extension of anything that exists today.

## What this is not

This file does not represent a committed backlog or sprint plan — none
exists in the repository. Do not present anything in the "suggested next
steps" section as already decided or scheduled.
