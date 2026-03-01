# Gap: Compound Job vs Heavy Backend

The **compound job** (what actually runs when you start from Run → Compound or nightly) is a thin path. The **backend** (apps/server, lib/, SQLite, dashboard) has a lot more that is **not** in that path. This doc spells out the gap.

---

## What compound actually uses

| Layer | Used by compound? | How |
|-------|-------------------|-----|
| **Bash** | Yes | auto-compound.sh → orchestrator.sh → specialist scripts. Priority from repo files, state in .compound-state/. |
| **sync-to-db.js** | Yes | Runs on orchestrator exit (trap). Writes session + tasks to SQLite via **lib/database.js**. |
| **lib/database.js** | Yes (from sync-to-db) | Sessions, tasks, updateTaskStatus → gamification.onTaskCompleted. Same DB file as server. |
| **lib/gamification.js** | Yes (indirect) | Called by lib/database.js when tasks are updated. XP, achievements. |
| **lib/job-executor.js** | Yes | Dashboard/API start job → spawns auto-compound.sh; creates a **second** session row (see below). |
| **apps/server** | Partial | Serves API (sessions, jobs, teams, gamification, etc.). Dashboard creates a session when you click Start; **orchestrator never sees that session ID**. |

So the **only** backend the compound execution path touches is: **lib/database.js** (and gamification) via sync-to-db.js, plus job-executor when you start from the UI.

---

## What the backend has that compound does *not* use

| Piece | Purpose | Used by compound? |
|-------|---------|-------------------|
| **apps/server (TypeScript)** | API, dashboard, sessions/tasks/teams CRUD | Dashboard creates session; **API session and orchestrator session are different IDs** (gap below). |
| **Roster (teams/agents from DB)** | Who runs, display, task→agent mapping | Orchestrator does **not** read DB to decide which agents to run; it uses hardcoded script names + keyword heuristics. Roster is for display and for sync-to-db task→agent_id mapping. |
| **lib/task-router.js** | Route tasks to agents by keyword | Used by llm-router; **not** called by compound. Compound uses orchestrator’s own heuristic. |
| **lib/pattern-detector.js** | Pattern analysis, automation candidates | Used by RL/Insights API only. **Not** in compound path. |
| **lib/learning-controller.js** | Experiments, agent insights | Used by RL/Insights API only. **Not** in compound path. |
| **lib/repository-manager.js** | Repo list/status | Used by repos API / dashboard. **Not** by compound (compound gets repo from config/args). |
| **lib/llm-router.js** | LLM choice, task routing | Used when something calls it (e.g. Telegram?); compound scripts call Claude/Ollama directly. **Not** in compound path. |
| **Campaigns, leads, content (DB)** | Marketing data | Separate from compound. Marketing uses Jarvis + campaign file. |

So: **compound is a thin pipeline** (bash + sync-to-db + lib/database + gamification). The rest of the backend is for dashboard, RL/Insights, repos, marketing data, and future features—**not** for the actual compound run.

---

## Session ID mismatch (real bug)

When you start from **Run → Compound**:

1. **Dashboard** creates a session via POST /api/sessions: `session-{Date.now()}` (e.g. `session-1730123456789`).
2. **job-executor.js** (when startEngineeringJob runs) creates **another** session with `sessionId: jobId` = `job-{timestamp}-{random}`.
3. **orchestrator.sh** generates its **own** `SESSION_ID="session-$(date +%s)"` (e.g. `session-1730123456`). It never receives the dashboard or job-executor session ID.
4. **sync-to-db.js** syncs **only** the orchestrator’s session (and its tasks) to the DB.

Result:

- The **dashboard-created** session and the **job-executor-created** session are never updated by the run. They stay “in progress” with no tasks.
- The **orchestrator-created** session is the one that gets tasks and real status after sync.

So Work / Active Sessions can show a “ghost” session (the one you thought you started) and a different session that actually ran. That’s a **gap between the compound job and the backend**: the backend creates sessions the orchestrator doesn’t know about, and the orchestrator creates a session the dashboard didn’t “start.”

---

## How to close the gap (options)

1. **Pass session ID into the compound run**  
   Dashboard (or job-executor) creates **one** session and passes its ID to the job (e.g. env `SESSION_ID=session-xxx`). Orchestrator uses that instead of generating its own. Then sync-to-db updates that same session. No duplicate sessions.

2. **Stop creating sessions in the dashboard for compound**  
   Only job-executor or only orchestrator creates the session. Dashboard just starts the job; Work shows whatever sync-to-db writes. Simpler, but the “session” you see is not the one the UI “created.”

3. **Wire more backend into compound** (optional, bigger lift)  
   e.g. Orchestrator (or a wrapper) calls task-router / pattern-detector / learning-controller so the same logic and data the dashboard uses also drive or analyze the run. Right now they’re separate.

---

## Summary

- **Compound job** = bash + sync-to-db + lib/database (sessions, tasks, gamification). It does **not** use Roster for execution, task-router, pattern-detector, learning-controller, repository-manager, or llm-router.
- **Heavy backend** = all of the above + apps/server + dashboard. Much of it is for UI, RL/Insights, repos, and marketing—**not** in the compound execution path.
- **Session ID mismatch**: Dashboard and job-executor create sessions that the orchestrator never uses; the run creates a different session. Fix by passing one session ID through the pipeline or by having only one place create the session.
