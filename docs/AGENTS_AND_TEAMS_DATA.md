# Agents and Teams: What’s in the DB vs on Disk

Quick reference for where agent/team data lives and how it’s used.

---

## Database (SQLite)

**Initialized from:** `schema.sql` only. The server runs this file on first run; it creates tables and runs the `INSERT OR IGNORE` blocks at the bottom.

**Not used by the server:** `seed.sql` is a legacy standalone seed (different structure, hardcoded paths). The app does **not** load it. For a fresh DB, only `schema.sql` is applied.

### Tables

| Table | Purpose |
|-------|--------|
| **teams** | Teams: Engineering, Marketing, Management, Schedule optimization. Fields: id, name, domain, description. |
| **agents** | One row per specialist. Linked to `teams` via `team_id`. Fields: id, name, role, emoji, llm_preference, success_rate, task counts, is_active, etc. |

**Seed data in schema.sql:** 4 teams and all agents (engineering, marketing, management, schedule-optimization) are inserted with `INSERT OR IGNORE`, so they appear in a new DB without running `seed.sql`.

### Used for

- **Roster UI** – list teams and agents (`GET /api/teams`, `GET /api/teams/:id/agents`, `GET /api/teams/agents/all`).
- **Sessions & tasks** – `sessions.team_id`, `tasks.agent_id` reference these tables.
- **Performance** – agent stats (success_rate, total_tasks_completed, etc.) and views like `v_agent_performance`.
- **Other** – leads, campaigns, content, integrations, automation_candidates can reference `agents(id)`.

---

## Disk (`agents/`)

**Location:** `be-agents-service/agents/` (scripts and prompts only; no DB data stored here).

### Structure

| On disk | Purpose |
|--------|--------|
| **agents/*.sh** | Executable scripts for engineering and schedule-optimization (e.g. `backend-specialist.sh`, `timefold-specialist.sh`). |
| **agents/marketing/*.sh** | Marketing agent scripts (e.g. `jarvis-orchestrator.sh`). |
| **agents/management/*.sh** | Management agent scripts (e.g. `ceo.sh`, `interface-agent.sh`). |
| **agents/prompts/*.md** | Prompt files; name matches the “prompt” in the server map (e.g. `backend-specialist.md`, `timefold-specialist.md`). |

### Link: agent ID → files

The server maps **agent IDs** (same as in the DB) to script and prompt **file names** in code:

- **File:** `apps/server/src/routes/file.ts`
- **Map:** `AGENT_TO_FILES`: e.g. `'agent-backend'` → `{ script: 'backend-specialist', prompt: 'backend-specialist' }`.
- **Paths:** script = `agents/${script}.sh`, prompt = `agents/prompts/${prompt}.md` (with optional override from target repo `.claude/prompts/`).

So:

- **DB** holds: which agents exist, their team, name, role, emoji, LLM, stats.
- **Disk** holds: the actual `.sh` and `.md` files; the server uses `AGENT_TO_FILES` to serve them when the UI asks for script/prompt by agent ID.

If you add a new agent:

1. **DB:** add a row to `agents` (via API or by adding an `INSERT OR IGNORE` in `schema.sql` for next init).
2. **Disk:** add `agents/<script>.sh` and `agents/prompts/<prompt>.md`.
3. **Server:** add an entry in `AGENT_TO_FILES` in `apps/server/src/routes/file.ts` so the UI can resolve that agent ID to script and prompt.

---

## Summary

| What | Where | Used by |
|------|--------|--------|
| Team/agent list, roles, stats, active flag | **DB** (schema.sql) | Roster, sessions, tasks, metrics |
| Script and prompt content | **Disk** (`agents/`) | Execution, `/api/file/agent-script`, `/api/file/agent-prompt` |
| Agent ID → script/prompt filename | **Code** (`AGENT_TO_FILES` in file.ts) | Resolving which file to serve for a given agent |

**Note:** `POST /api/agents/trigger/:name` uses `name` as a **repo name** (e.g. `beta-appcaire`), not an agent ID. It runs the compound workflow (`auto-compound.sh` or `daily-compound-review.sh`) for that repo, not a single specialist script from `agents/*.sh`.
