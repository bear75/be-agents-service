# AGENTS.md

## Cursor Cloud specific instructions

### Services overview

This is the **be-agents-service** ("Darwin") monorepo — an agent automation orchestration system. It has two workspace packages:

| Service | Description | Port | Dev command |
|---------|-------------|------|-------------|
| `server` | Express REST API + static dashboard (SQLite via better-sqlite3) | 3010 | `yarn dev` (from root) |
| `dashboard` | React 19 + Vite SPA (built and copied into server's `public/` dir) | served by server | built as part of `yarn dev` |

### Running the dev server

From the repo root, `yarn dev` builds the dashboard, copies assets to `apps/server/public/`, and starts the server with `tsx watch` on port 3010. The SQLite database at `.compound-state/agent-service.db` is auto-created on first start — no external database setup is needed.

### Lint and type-check

- `yarn lint` — runs ESLint in dashboard workspace only (server has no lint script). There are pre-existing lint errors (7 errors, 3 warnings as of March 2026).
- `yarn type-check` — runs `tsc --noEmit` in both server and dashboard workspaces.

### Key gotchas

- The `better-sqlite3` package requires native compilation. If `yarn install` fails on it, ensure C/C++ build tools (`build-essential`, `python3`) are available.
- `yarn.lock` is authoritative; ignore `package-lock.json` (Yarn Classic 1.22 is the package manager).
- The dashboard build output is copied to `apps/server/public/` — the server serves it statically. There is no separate dashboard port in production/dev mode when using `yarn dev`.
- No Docker, no PostgreSQL, no external services required. Everything runs on Node.js + SQLite.
- API endpoints are at `/api/*`, health check at `/health`, dashboard at `/`.
