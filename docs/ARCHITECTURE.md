# Agent Service Architecture

**One server. One dashboard. Port 3030.**

> **Naming:** This repo uses `apps/server`. Do not confuse with `apps/dashboard-server` in the **beta-appcaire** repo (different project — AppCaire scheduling/GraphQL).

---

## Overview

```
http://localhost:3030
├── /                    → React SPA (workspace, plans, agents, logs)
└── /api/*               → All API routes
```

---

## Single Server (`apps/server`)

**Express app on port 3030** — serves everything:

| Responsibility | Location |
|----------------|----------|
| API routes | `apps/server/src/routes/*.ts` |
| Static files | `apps/server/public/` |
| DB/lib access | `lib/` (root) |

### Route Modules

| Route | Purpose |
|-------|---------|
| `repos` | Repository config (repos.yaml) |
| `agents` | Compound automation + HR agents |
| `workspace` | Workspace markdown files |
| `plans` | Plans & roadmap |
| `sessions` | Session history (DB) |
| `logs` | Session logs (filesystem) |
| `stats` | System statistics |
| `jobs` | Job control (engineering/marketing) |
| `commands` | User command tracking (RL) |
| `data` | Campaigns, leads, content |
| `rl` | RL experiments, patterns, agent performance |
| `repositories` | Repository manager |
| `tasks` | Task filtering |
| `integrations` | Integrations DB |
| `gamification` | XP, leaderboard, achievements |
| `file` | Doc file reader |

---

## Frontend

| Source | Output | Served at |
|-------|--------|-----------|
| `apps/dashboard` (React) | `apps/server/public/index.html` + assets | `/` |

**Build:** `yarn build:unified` → React build copied to `apps/server/public/`

---

## Startup

```bash
yarn start          # Build + run (production)
yarn dev            # Build + run with tsx watch
yarn dev:server     # Server only (port 3030)
```

**LaunchD:** `scripts/start-dashboard.sh` → `yarn workspace server start` (PORT=3030)

---

## Data Flow

```
Browser
   │
   ▼
apps/server (Express, port 3030)
   │
   ├── Static → apps/server/public/
   └── API → lib/
              ├── database.js
              ├── job-executor.js
              ├── learning-controller.js
              ├── pattern-detector.js
              ├── llm-router.js
              ├── repository-manager.js
              ├── gamification.js
              └── config/repos.yaml
```

---

## Migration (Feb 2026)

**Before:** `dashboard/server.js` (Node http, 800+ lines) + `apps/server` (Express, proxy target)  
**After:** Single Express app in `apps/server` with modular routes

Deleted: `dashboard/server.js`, `dashboard/start-unified.js`
