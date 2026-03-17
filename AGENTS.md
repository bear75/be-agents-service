# AGENTS.md

## Cursor Cloud specific instructions

### Services

This repo has one required service: the **Darwin dashboard** (Express API + React SPA), served on port 3010.

- **Server** (`apps/server/`): Express.js with TypeScript, SQLite via `better-sqlite3` (auto-initialized on startup from `apps/server/src/lib/database.ts`).
- **Dashboard** (`apps/dashboard/`): React 19 + Vite + Tailwind CSS. Built output is copied into `apps/server/public/` for unified serving.

No external databases, Docker, or third-party API keys are needed to run the dashboard.

### How to run

See `README.md` for full commands. Key commands from repo root:

- **Dev mode (hot-reload server):** `yarn dev` — builds dashboard, copies to `public/`, runs server with `tsx watch`.
- **Production-like:** `yarn start` — builds dashboard + server, runs compiled JS.
- **Dashboard only (Vite dev server):** `yarn dev:dashboard` — runs on port 3010 with API proxy.
- **Server only (hot-reload):** `yarn dev:server` — runs server with `tsx watch`.

### Lint / type-check

- `yarn workspace dashboard lint` — ESLint for dashboard (has pre-existing errors as of March 2026).
- `yarn workspace server type-check` — TypeScript `--noEmit` for server.
- `yarn workspace dashboard type-check` — TypeScript `--noEmit` for dashboard.
- There is no lint script for the server workspace, only `type-check`.

### Non-obvious caveats

- The `yarn dev` script builds the dashboard first (`yarn build:unified`), then starts the server with `tsx watch`. If you change only dashboard code, you need to rebuild the dashboard (`yarn build:unified`) for changes to appear when served through the unified server. Alternatively, run `yarn dev:dashboard` for Vite's HMR during dashboard-only development.
- SQLite database is auto-created at `.compound-state/agent-service.db` on first server start. Seed data (teams, agents) is automatically inserted.
- The `yarn.lock` exists alongside a `package-lock.json` in the repo. Use `yarn` as the package manager (lockfile: `yarn.lock`, `packageManager` field in `package.json`). Yarn will warn about the `package-lock.json` — this is harmless.
- The dashboard Vite config (`apps/dashboard/vite.config.ts`) proxies `/api` to `localhost:3010`, but the proxy target is the same port as the dev server, which can cause loops if both Vite and Express try to bind port 3010 simultaneously. For dashboard HMR development, start the Express server on a different port first, or use the unified `yarn dev` approach.
