# Priority Files → Agent Model → Kanban Integration

## Overview

How `beta-appcaire/reports/priorities-*.md` flows into the agent system and Kanban board.

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  beta-appcaire/reports/                                          │
│    priorities-YYYY-MM-DD.md    (Product backlog items)          │
│    ess-fsr/priorities-*.md      (Project-specific)               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ (1) Orchestrator reads at start
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  orchestrator.sh <target_repo> <priority_file> <prd_file> <branch>│
│  • Keyword detection → spawns specialists                       │
│  • Writes: .compound-state/session-*/orchestrator.json            │
│    → priorityFile path stored in orchestrator state              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ (2) Specialists run, write state
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  .compound-state/session-*/                                      │
│    orchestrator.json  (priorityFile, status, phase)              │
│    backend.json       (completedTasks → tasks)                   │
│    docs-expert.json   (completedTasks → tasks)                   │
│    ...                                                           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ (3) trap EXIT → sync-to-db.js
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  sync-to-db.js session-XXX                                       │
│  • Creates/updates sessions row (priority_file, target_repo)      │
│  • Creates tasks from specialist completedTasks → agent_id       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ (4) SQLite write
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent-service.db                                                │
│    sessions.priority_file  (path only, not content)              │
│    tasks                    (from agent completedTasks)         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ (5) API
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Kanban Board (GET /api/tasks, /api/sessions)                    │
│  • Tasks visible with agent, session, status                     │
│  • Session filter shows priority_file path                       │
└─────────────────────────────────────────────────────────────────┘
```

## Key Points

| What | Where | Notes |
|------|-------|-------|
| **Priority file path** | `sessions.priority_file` | Stored when sync-to-db runs |
| **Priority content** | Not stored in DB | Read by orchestrator at runtime |
| **Tasks** | `tasks` table | From agent `completedTasks` in state JSON |
| **Sync trigger** | `trap EXIT` in orchestrator.sh | Runs on every orchestrator exit (success or failure) |
| **Nightly run** | auto-compound.sh | Uses `reports/*.md`; runs orchestrator; sync via trap |

## What IS Visible in Kanban

- **Tasks** — Agent work units (from specialist completedTasks)
- **Sessions** — Orchestrator runs with `priority_file` path
- **Agents** — All 24 agents

## What Is NOT Stored

- **Priority items** (Priority 1, 2, 3…) — Not parsed into separate DB rows
- **Priority file content** — Only the path is stored

## Manual Sync

If a session was created before the trap was added:

```bash
cd ~/HomeCare/be-agents-service
node scripts/sync-to-db.js session-XXXXXXXX
```

## Configuration

- **Target repo priority path**: `config/repos.yaml` → `priorities_dir: reports/`
- **Default priority pattern**: `reports/priorities-YYYY-MM-DD.md`
- **Engineering UI**: User enters path in "Start Engineering Job" form
