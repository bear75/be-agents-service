# Agent Data Sources

## Where agent info lives

### Database (SQLite)

**File:** `.compound-state/agent-service.db` (lib/database.js, gamification)  
**File:** `.compound-state/agent-service.db` (apps/server database.ts — teams/agents API)

**DB schema (agents table):**
- `id`, `team_id`, `name`, `role`, `emoji`, `llm_preference`
- `success_rate`, `total_tasks_completed`, `is_active`, etc.

**What the DB has:** short description in `role` (e.g. "Handles database schema, migrations, GraphQL"). No full prompt, no competence doc.

### Files

**Prompts (full system prompt):**
- Target repo: `<target_repo>/.claude/prompts/backend-specialist.md`, etc.
- One prompt file per specialist in the target repo

**Scripts (entry point, config):**
- `agents/backend-specialist.sh`, `agents/levelup-specialist.sh`, etc.
- Defines: session_id, target_repo, priority_file, PROMPT_FILE path

**Competence / description:**
- Short: DB `role` column
- Long: prompt file in target repo (same file as system prompt)

**What compound uses:** See [COMPOUND_USES.md](COMPOUND_USES.md) for how compound uses agents, teams, prompts (soul), and gamification.

---

## Leaderboard shows 0 agents

Leaderboard uses gamification, which reads from `.compound-state/agent-service.db` via `lib/gamification.js`.

Likely causes:
1. Gamification schema (`gamification-schema.sql`) not applied to that DB
2. Different DB path than teams API (teams use `.compound-state/agent-service.db` via apps/server)
3. No XP transactions yet → leaderboard needs `agent_levels` / `v_leaderboard` populated

---

## Work started from Run?

Mostly yes, but not only:
- **Run → Compound** starts compound (and records session for Work)
- **Terminal:** `./scripts/compound/auto-compound.sh beta-appcaire`
- **Launchd:** nightly at 23:00

Sessions in Work can come from any of these.
