# What compound uses

One place to see what the compound job (priority #1 → PR) actually uses: agents, teams, prompts, gamification.

---

## Single job type: compound is the only run

**The only jobs started from the dashboard (Run → Compound) or nightly are compound jobs.** There is no separate “marketing job” or “management job” to start. Instead, **one compound run = all domains**:

- **Management** (strategy) runs as phase 0 inside that same run.
- **Engineering** runs as phase 1 (orchestrator + all specialists).
- **Marketing** runs as phase 2 (Jarvis + all specialists) after engineering.

So **all teams and agents are used** every time you start a compound job. The Roster (teams/agents in the DB) is the single source of truth for who those agents are; the run doesn’t “choose” a team—it runs strategy, then engineering, then marketing in one session. If something isn’t part of compound, it is never run from the dashboard or nightly; by design, everything that should run is part of compound.

---

## Run phases (all domains)

Each compound run uses **three phases**:

1. **Strategy (management)** – Optional. `agents/management/strategy-brief.sh` reads the priority and produces a one-page strategy/alignment brief (`.compound-state/<session>/strategy-brief.md`) for product, tech, and marketing alignment.
2. **Engineering** – `scripts/orchestrator.sh` runs **all** engineering specialists: backend, frontend, infrastructure, db-architect, ux-designer, documentation-expert, levelup, verification. No keyword gating; every run invokes the full set.
3. **Marketing** – After engineering succeeds, `agents/marketing/jarvis-orchestrator.sh` runs **all** marketing specialists for SEO and web: Vision (SEO), Shuri (product), Fury (customer), Loki (content), Wanda (design), Pepper (email), Friday (developer), Quill (social), Wong (Notion). Same session, same branch, same priority file.

---

## Agents

- **Orchestrator** runs all engineering specialist **scripts** in `agents/`: backend, frontend, infrastructure, db-architect, ux-designer, documentation-expert, levelup, verification.
- **Jarvis** runs all marketing specialist scripts in `agents/marketing/`: vision-seo-analyst, shuri-product-analyst, fury-customer-researcher, loki-content-writer, wanda-designer, pepper-email-marketing, friday-developer, quill-social-media, wong-notion-agent.
- **Strategy brief** (management) is produced by `agents/management/strategy-brief.sh`; management delegates (ceo, cpo-cto, cmo-cso) are available for manual or future use.
- The same roles exist in the **Roster** (DB) for display and for mapping: when `sync-to-db.js` runs, it maps specialist names to `agent_id` so tasks and gamification line up with the Roster.

So: compound uses **all engineering agents**, **all marketing agents**, and a **strategy (management) phase**; the DB is the source of truth for **who** they are (names, XP, leaderboard).

---

## Teams

- Session is stored as `team-engineering` so Work and sessions list show the right team. Engineering, marketing, and strategy all run in the **same** compound run and **same** session.

---

## Prompts (soul)

- Each specialist script loads its **system prompt** from:
  1. **Target repo** `<target_repo>/.claude/prompts/<specialist>.md` if it exists
  2. Else **be-agent-service** `agents/prompts/<specialist>.md`
- So target-repo prompts (soul) **are** used when present.

---

## Gamification

- When the orchestrator exits, **sync-to-db.js** runs (trap in `orchestrator.sh`). It writes session and tasks to the SQLite DB via **lib/database.js**.
- **lib/database.js** `updateTaskStatus` calls **gamification.onTaskCompleted** (XP, achievements). So compound **does** feed gamification when tasks are synced.
- Leaderboard and Insights read from the same DB; XP from compound runs will show there once sync has run and gamification schema is applied.

---

## Summary

| Thing        | Used by compound? | How |
|-------------|--------------------|-----|
| Agents      | Yes (all)         | Engineering: all specialists in `agents/`. Marketing: all in `agents/marketing/` (Jarvis). Management: strategy-brief.sh. Roster used for task→agent_id and display. |
| Teams       | Yes (one)         | Session stored as team-engineering; one run covers strategy + engineering + marketing. |
| Prompts/soul| Yes               | Target repo `.claude/prompts/*.md` override `agents/prompts/*.md`. |
| Gamification| Yes               | sync-to-db → lib/database.js → gamification.onTaskCompleted. |

**Gap with the rest of the backend:** Compound is a thin path (bash + sync-to-db + lib/database + gamification). The rest (task-router, pattern-detector, learning-controller, Roster-as-execution-source, dashboard-created session ID) is not used by the run. See [COMPOUND_VS_BACKEND_GAP.md](COMPOUND_VS_BACKEND_GAP.md).
