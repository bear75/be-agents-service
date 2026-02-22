# Data Flow: Filesystem → Database → UI

> **Evergreen.** Describes current architecture.

---

## Overview

The agent service uses a **hybrid architecture** where:
1. **Filesystem** = Source of truth for operational data (logs, state snapshots)
2. **Database** = Query interface for structured data (tasks, sessions, metrics)
3. **UI** = Control panel for triggering jobs and viewing results

Data flows in **one direction**: Files → Database → UI

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                             │
│  Dashboard UI / CLI Commands / LaunchAgent Scheduler             │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ (1) Trigger Job
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXECUTION LAYER                              │
│  Bash Scripts: orchestrator.sh, agents/*.sh                      │
├──────────────────────────────────────────────────────────────────┤
│  • Spawns LLM calls (Claude API)                                 │
│  • Writes to: .compound-state/session-*/agent.json (STATE)       │
│  • Writes to: logs/running-jobs/job-*.log (LOGS)                 │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ (2) Write State Files
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FILESYSTEM STORAGE                          │
│  .compound-state/                                                │
│    ├─ session-1770537842/                                        │
│    │  ├─ orchestrator.json        (Session metadata)             │
│    │  ├─ backend.json              (Task state)                  │
│    │  ├─ frontend.json             (Task state)                  │
│    │  └─ infrastructure.json       (Task state)                  │
│    └─ agent-service.db             (SQLite database)             │
│                                                                  │
│  logs/                                                           │
│    ├─ running-jobs/job-*.log       (Real-time execution logs)   │
│    └─ orchestrator-sessions/       (Per-agent logs)              │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ (3) Sync to Database
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNC PROCESS (scripts/sync-to-db.js)          │
│  • Reads: .compound-state/session-*/agent.json                   │
│  • Writes: SQLite tables (sessions, tasks, metrics)              │
│  • Enriches: Joins agent data, calculates stats                  │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ (4) Database Write
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SQLITE DATABASE                              │
│  .compound-state/agent-service.db                                │
├──────────────────────────────────────────────────────────────────┤
│  Tables:                                                         │
│    • teams          (Engineering, Marketing, Management)         │
│    • agents         (24 agents with stats, roles, emojis)        │
│    • sessions       (Orchestrator runs with status, PR URLs)     │
│    • tasks          (Individual agent work units)                │
│    • metrics        (Performance tracking)                       │
│    • patterns       (RL pattern detection)                       │
│    • experiments    (Keep/Kill/Double-down decisions)            │
│    • integrations   (Email, social, OpenClaw connections)        │
│    • campaigns      (Marketing campaign data)                    │
│    • leads          (Sales leads from scraping)                  │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ (5) API Query
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API SERVER (dashboard/server.js)              │
│  Express-like HTTP server on port 3030                           │
├──────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                      │
│    GET  /api/tasks          → db.getAllTasks()                   │
│    GET  /api/sessions       → db.getRecentSessions()             │
│    GET  /api/agents         → db.getAllAgents()                  │
│    GET  /api/logs/:id       → fs.readFileSync(logPath)           │
│    POST /api/jobs/start     → spawn orchestrator.sh             │
│    POST /api/agents/create  → db.createAgent()                   │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ (6) HTTP Response (JSON)
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DASHBOARD UI                                │
│  Browser rendering HTML + JavaScript                             │
├──────────────────────────────────────────────────────────────────┤
│  Pages:                                                          │
│    • management-team.html   (CEO dashboard)                      │
│    • engineering.html       (Start jobs, view agents)            │
│    • sales-marketing.html   (Campaigns, leads)                   │
│    • kanban.html            (Task board: Pending → Completed)    │
│    • rl-dashboard.html      (Experiments, patterns)              │
│    • settings.html          (Integrations, config)               │
└──────────────────────────────────────────────────────────────────┘
```

---

## LLM Model Selection (Cost vs Performance)

Darwin uses **two systems** that choose models differently:

### 1. Agent Service (llm-invoke.sh, compound scripts)

| Task Type | Model | Cost | When |
|-----------|-------|------|------|
| **analyze, convert, triage** | Ollama (qwen2.5:14b) | $0 | Short text, JSON, inbox triage |
| **prd, implement, review** | Claude (Sonnet/Opus) | Paid | Long docs, code, complex work |

- **OLLAMA_MODEL** env var (default: `qwen2.5:14b`) — set in `~/.config/caire/env`
- **llm-router.js** — logical names: opus, sonnet, haiku, pi (pi = local/free)

### 2. OpenClaw (Telegram/Darwin chat)

- **~/.openclaw/openclaw.json** → `agents.defaults.model.primary` (default: `ollama/qwen2.5:14b`), `fallbacks` (Claude Sonnet, Opus)
- Primary: Qwen via Ollama (local, free). Fallbacks: Claude Sonnet → Opus when Qwen can't handle it.
- **User override:** `/model claude` or "use Claude" → force Claude for that request/session
- **When unsure:** Darwin asks: "This might need Claude — use Claude, or try Qwen first?"
- **PRD/implement/review (compound):** Always use Claude — controlled by llm-invoke.sh, not Darwin

### Override

```bash
# Use a different Ollama model
export OLLAMA_MODEL=qwen2.5:14b
./scripts/compound/llm-invoke.sh analyze "Extract priority from: ..."
```

---

## Detailed Data Flow Examples

### Example 1: Engineering Job Execution

**User clicks "Start Engineering Job" in UI:**

```
1. USER ACTION
   Browser:  POST /api/jobs/start
   Payload:  { type: 'engineering', model: 'sonnet', priorityFile: 'reports/priorities-2026-02-08.md' }

2. API SERVER
   server.js: Receives POST request
   → Calls: jobExecutor.startJob(params)
   → Spawns: ./scripts/orchestrator.sh repo priorityFile prdFile branch

3. ORCHESTRATOR EXECUTION
   orchestrator.sh:
   → Creates session: session-1770537842
   → Writes: .compound-state/session-1770537842/orchestrator.json
     {
       "sessionId": "session-1770537842",
       "status": "in_progress",
       "team": "team-engineering",
       "targetRepo": "/Users/.../beta-appcaire",
       "startedAt": "2026-02-08T11:20:29.000Z"
     }
   → Spawns specialists in parallel:
     - backend-specialist.sh session-1770537842
     - infrastructure-specialist.sh session-1770537842
     - frontend-specialist.sh session-1770537842

4. SPECIALIST EXECUTION
   backend-specialist.sh:
   → Calls Claude API (LLM)
   → Makes code changes
   → Writes: .compound-state/session-1770537842/backend.json
     {
       "agentId": "agent-backend",
       "status": "completed",
       "description": "backend task",
       "startedAt": "2026-02-08T11:20:29.000Z",
       "completedAt": "2026-02-08T11:20:30.770Z",
       "durationSeconds": 0.77
     }
   → Writes logs: logs/orchestrator-sessions/session-1770537842/backend.log

5. SYNC TO DATABASE
   orchestrator.sh (on completion):
   → Calls: node scripts/sync-to-db.js session-1770537842

   sync-to-db.js:
   → Reads: .compound-state/session-1770537842/orchestrator.json
   → Reads: .compound-state/session-1770537842/backend.json
   → Reads: .compound-state/session-1770537842/infrastructure.json
   → Writes to DB:
     INSERT INTO sessions (id, team_id, status, target_repo) VALUES (...)
     INSERT INTO tasks (id, session_id, agent_id, status, duration_seconds) VALUES (...)
     UPDATE agents SET total_tasks_completed = total_tasks_completed + 1 WHERE id = 'agent-backend'

6. UI POLLING
   kanban.html (auto-refresh every 10s):
   → Fetches: GET /api/tasks
   → Receives JSON:
     [
       {
         "id": "task-session-1770537842-backend",
         "status": "completed",
         "agent_name": "Backend",
         "agent_emoji": "⚙️",
         "duration_seconds": 0.77,
         "started_at": "2026-02-08 11:20:29"
       }
     ]
   → Renders task card in "Completed" column
   → User clicks card → Modal shows full details
```

**Timeline:**
- **T+0s**: User clicks "Start Job" → API spawns orchestrator
- **T+1s**: Orchestrator spawns specialists → State files written
- **T+30s**: Specialists complete → State files updated
- **T+31s**: Sync-to-db runs → Database updated
- **T+40s**: UI auto-refresh → Fetches from database → Renders cards

**Key Point:** The UI **never reads filesystem directly**. It only queries the database via API.

---

### Example 2: Viewing Task Details in Kanban

**User clicks a task card:**

```
1. USER ACTION
   Browser: Click on task card
   → JavaScript: viewTask('task-session-1770537842-backend')

2. DATA ALREADY IN MEMORY
   kanban.html:
   → allTasks array populated from: GET /api/tasks (initial load)
   → Finds task by ID: const task = allTasks.find(t => t.id === taskId)
   → Task object contains:
     {
       "id": "task-session-1770537842-backend",
       "session_id": "session-1770537842",
       "agent_id": "agent-backend",
       "description": "backend task (failed before completion)",
       "status": "failed",
       "priority": "medium",
       "llm_used": "sonnet",
       "started_at": "2026-02-08 11:20:29",
       "completed_at": "2026-02-08T11:20:29.767Z",
       "duration_seconds": 0.767,
       "error_message": "Agent failed before writing state file",
       "agent_name": "Backend",      // Joined from agents table
       "agent_emoji": "⚙️",          // Joined from agents table
       "team_name": "Engineering"    // Joined from teams table
     }

3. MODAL RENDERING
   → Creates modal div with task details
   → Formats timestamps: "3 hours ago" from started_at
   → Displays error message if failed
   → Adds "View Session" button linking to: /engineering.html?session=session-1770537842
```

**Key Point:** All data comes from a **single API call** (`GET /api/tasks`). The database query joins 3 tables:

```sql
SELECT
  t.*,
  a.name as agent_name,
  a.emoji as agent_emoji,
  team.name as team_name
FROM tasks t
JOIN agents a ON t.agent_id = a.id
JOIN teams team ON a.team_id = team.id
ORDER BY t.started_at DESC
```

---

### Example 3: Viewing Logs

**User clicks "View Logs" for a job:**

```
1. USER ACTION
   Browser: GET /api/logs/job-1770537842593-mfn5pu4

2. API SERVER
   server.js:
   → Parses job ID from URL
   → Constructs file path: logs/running-jobs/job-1770537842593-mfn5pu4.log
   → Reads file: fs.readFileSync(logPath, 'utf-8')
   → Returns raw log content as text/plain

3. UI DISPLAY
   engineering.html:
   → Renders logs in <pre> tag
   → Auto-scrolls to bottom
   → Updates every 2s if job still running
```

**Key Point:** Logs are **always read from filesystem**, never stored in database. They're too large and append-only.

---

## Data Sources

### Always from Database (via API)

| Data | Endpoint | Database Tables | Purpose |
|------|----------|-----------------|---------|
| Tasks | `GET /api/tasks` | `tasks`, `agents`, `teams` | Kanban board, task tracking |
| Sessions | `GET /api/sessions` | `sessions`, `teams` | Job history, PR links |
| Agents | `GET /api/agents` | `agents`, `teams` | Agent registry, stats, HR management |
| Metrics | `GET /api/rl/agent-performance` | `metrics`, `agents` | RL dashboard, performance tracking |
| Patterns | `GET /api/rl/patterns` | `patterns` | RL pattern detection |
| Experiments | `GET /api/rl/experiments` | `experiments` | Keep/Kill/Double-down decisions |
| Integrations | `GET /api/integrations` | `integrations` | Settings page, email/social config |
| Campaigns | `GET /api/data/campaigns` | `campaigns` | Marketing dashboard |
| Leads | `GET /api/data/leads` | `leads` | Sales dashboard |

### Always from Filesystem (never in DB)

| Data | Endpoint | File Location | Purpose |
|------|----------|---------------|---------|
| Logs | `GET /api/logs/:id` | `logs/running-jobs/*.log` | Real-time execution logs |
| State Snapshots | N/A (debugging only) | `.compound-state/session-*/agent.json` | Debugging, recovery, sync source |
| Priority Files | User-created | `reports/priorities-*.md` | User input, git-tracked |
| Task Definitions | User-created | `tasks/*.json` | User input, git-tracked |
| Documentation | User-created | `docs/**/*.md` | Human-readable, git-tracked |

### Hybrid (Files + Database)

| Data | Source | Sync Mechanism | Notes |
|------|--------|----------------|-------|
| Session State | Filesystem | `scripts/sync-to-db.js` | Files = debugging, DB = queries |
| Task State | Filesystem | `scripts/sync-to-db.js` | Files = recovery, DB = UI |

---

## Sync Process Details

### When Does Sync Happen?

**Automatic (Future):**
```bash
# At end of orchestrator.sh:
node scripts/sync-to-db.js "$SESSION_ID"
```

**Manual (Current):**
```bash
# Sync specific session
node scripts/sync-to-db.js session-1770537842

# Sync all sessions
for session in .compound-state/session-*; do
  session_id=$(basename "$session")
  node scripts/sync-to-db.js "$session_id"
done
```

### What Gets Synced?

**FROM Filesystem (.compound-state/session-*/agent.json):**
- Session metadata (status, repo, branch, PR URL)
- Task records (description, status, agent, duration)
- Error messages, retry counts

**TO Database (SQLite):**
```sql
-- Session record
INSERT INTO sessions (id, team_id, status, target_repo, branch_name, pr_url) VALUES (...)

-- Task records (one per specialist)
INSERT INTO tasks (id, session_id, agent_id, description, status, duration_seconds, error_message) VALUES (...)

-- Agent stats update
UPDATE agents SET
  total_tasks_completed = total_tasks_completed + 1,
  success_rate = (successful_tasks / total_tasks)
WHERE id = 'agent-backend'
```

**NOT Synced:**
- Logs (stay as files, too large)
- Detailed state (stays in JSON for debugging)

---

## API Endpoints Reference

### Read Operations (GET)

```bash
# Tasks
curl http://localhost:3030/api/tasks
# Returns: Array of all tasks with joined agent/team data

# Sessions
curl http://localhost:3030/api/sessions
# Returns: Array of recent sessions (last 50)

# Agents
curl http://localhost:3030/api/agents
# Returns: Array of all agents with stats

# Logs (from filesystem)
curl http://localhost:3030/api/logs/job-1770537842593-mfn5pu4
# Returns: Raw log file content as text

# Stats
curl http://localhost:3030/api/stats
# Returns: Aggregated counts (total tasks, completed, failed, etc.)
```

### Write Operations (POST)

```bash
# Start Job
curl -X POST http://localhost:3030/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{
    "type": "engineering",
    "model": "sonnet",
    "priorityFile": "reports/priorities-2026-02-08.md",
    "branch": "feature/new-feature"
  }'
# Action: Spawns orchestrator.sh

# Hire Agent
curl -X POST http://localhost:3030/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "id": "agent-new-specialist",
    "name": "New Specialist",
    "role": "Special tasks",
    "teamId": "team-engineering",
    "emoji": "🚀"
  }'
# Action: INSERT INTO agents (...)

# Track User Command (RL)
curl -X POST http://localhost:3030/api/commands \
  -H "Content-Type: application/json" \
  -d '{
    "commandText": "Start engineering job",
    "normalizedIntent": "start_engineering_job"
  }'
# Action: INSERT INTO user_commands (...) + check for automation patterns
```

---

## Database Schema Highlights

### Key Relationships

```
teams (3)
  └── agents (24)
       └── tasks (many)
            └── sessions (many)
```

### Important Columns

**sessions table:**
- `id`: session-1770537842
- `team_id`: team-engineering
- `status`: in_progress | completed | failed | blocked
- `pr_url`: https://github.com/owner/repo/pull/123
- `started_at`, `completed_at`: Timestamps

**tasks table:**
- `id`: task-session-1770537842-backend
- `session_id`: session-1770537842 (FK)
- `agent_id`: agent-backend (FK)
- `status`: completed | failed
- `duration_seconds`: 0.77
- `error_message`: Text or null

**agents table:**
- `id`: agent-backend
- `team_id`: team-engineering (FK)
- `name`: "Backend"
- `emoji`: "⚙️"
- `success_rate`: 0.95 (calculated)
- `total_tasks_completed`: 42

---

## Performance Considerations

### Why Database?
- ✅ **Fast queries**: Indexed lookups by session_id, agent_id
- ✅ **Joins**: Link tasks → agents → teams in one query
- ✅ **Aggregations**: COUNT, SUM, AVG for dashboards
- ✅ **Concurrent access**: Multiple UI users querying simultaneously

### Why Files?
- ✅ **Append-only logs**: Perfect for streaming writes
- ✅ **Large text**: Gigabytes of logs would slow DB
- ✅ **Standard tooling**: `tail -f`, `grep`, ELK expect files
- ✅ **Recovery**: Point-in-time snapshots for debugging

### Best Practices

**For Developers:**
- ✅ Query database for UI display, dashboards, metrics
- ✅ Read logs from files for debugging
- ✅ Keep user input files (priority.md, task.json) in git
- ✅ Sync state files to database after jobs complete
- ❌ Don't query JSON files directly (sync to DB first)
- ❌ Don't store large text in database (use files)

**For Users:**
- ✅ Use dashboard to view tasks, sessions, metrics
- ✅ Use dashboard logs view to see job output (files via API)
- ❌ Don't manually edit database (use dashboard or API)
- ❌ Don't manually edit state files (orchestrator writes these)

---

## Troubleshooting Data Issues

### Problem: Kanban board empty despite state files existing

**Diagnosis:**
```bash
# Check if state files exist
ls .compound-state/session-*/

# Check if database has tasks
sqlite3 .compound-state/agent-service.db "SELECT * FROM tasks;"

# Check API response
curl http://localhost:3030/api/tasks
```

**Solution:** Sync files to database
```bash
node scripts/sync-to-db.js session-1770537842
```

### Problem: Task shows wrong agent name

**Diagnosis:** Database query isn't joining agents table

**Solution:** Check API endpoint uses proper JOIN:
```sql
SELECT t.*, a.name as agent_name, a.emoji as agent_emoji
FROM tasks t
JOIN agents a ON t.agent_id = a.id
```

### Problem: Logs not showing in UI

**Diagnosis:** Log files might be in wrong location or API can't read them

**Solution:**
```bash
# Check log file exists
ls -la logs/running-jobs/job-*.log

# Check file permissions
chmod 644 logs/running-jobs/*.log

# Check API endpoint path construction
curl http://localhost:3030/api/logs/job-1770537842593-mfn5pu4
```

---

## Summary

### Data Flow in One Sentence
**Shell scripts write to files → Sync script populates database → API queries database → UI displays results.**

### Key Principles
1. **Filesystem** = Source of truth for operational data
2. **Database** = Query interface for structured data
3. **UI** = View layer (never writes to filesystem or DB directly)
4. **API** = Single source of data for UI (abstracts storage)
5. **Sync** = One-way bridge from files to database

### Golden Rule
**If you need to query it → Database**
**If you need to stream it → Files**
**If a user created it → Files (git-tracked)**

---

**Result:** Clean separation of concerns, optimal performance, easy debugging! 🎯
