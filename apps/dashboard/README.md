# Agent Service Dashboard

React UI for the agent service: workspace, plans, sessions, agents, and run controls.

- **Dev:** `yarn dev` → Vite on **http://localhost:3010**
- **Production:** Dashboard is built and served by `apps/server` (same port 3010). Run from repo root: `yarn start` or `yarn dev` (see main [README](../../README.md)).

## What the dashboard shows

- **Workspace** — Repo selector, workspace status, plans, inbox/priorities (when API is configured)
- **Run / Engineering** — Start compound: `./scripts/compound/auto-compound.sh <repo>`
- **Agents / Teams** — Agents and teams from `.compound-state/agent-service.db` (via API)
- **Management / Insights** — Gamification, experiments, lessons learned
- **Settings** — Setup status (workspace, OpenClaw, Telegram); links to `scripts/workspace/init-workspace.sh`, `config/openclaw/README.md`

## Paths and structure

The UI references the canonical layout (see [docs/AGENT_WORKSPACE_STRUCTURE.md](../../docs/AGENT_WORKSPACE_STRUCTURE.md)):

- **Compound scripts:** `scripts/compound/` (auto-compound, daily-compound-review, loop, check-status, test-safety)
- **Workspace scripts:** `scripts/workspace/` (init-workspace, sync-to-workspace, process-inbox)
- **State and DB:** `.compound-state/` (session JSON + `agent-service.db`); agents and scripts must not write elsewhere for state

## Tech

- React 19, TypeScript, Vite 7, React Router, Tailwind, Lucide, react-markdown
- No direct DB access — all data via `apps/server` API (same origin when served by server)

## Build

```bash
cd apps/dashboard
yarn build
```

Output goes to `apps/dashboard/dist` and is served by `apps/server` from `apps/server/public` (build may copy into server public; see server config).
