# Data Storage Strategy - Files vs Database

**Date:** 2026-02-08
**Status:** ✅ Defined

---

## Overview

The agent-service uses a **hybrid storage approach**: SQLite database for structured queryable data, and filesystem for operational files (logs, user inputs, state snapshots).

---

## Storage Decision Matrix

| Data Type | Storage | Reason | Location |
|-----------|---------|--------|----------|
| **Tasks** | ✅ Database | Queryable, relationships, filtering | `tasks` table |
| **Sessions** | ✅ Database | Queryable, relationships, metrics | `sessions` table |
| **Agents** | ✅ Database | CRUD operations, performance tracking | `agents` table |
| **Integrations** | ✅ Database | Configuration, credentials, status | `integrations` table |
| **Metrics** | ✅ Database | Time-series queries, aggregations | `metrics` table |
| **Rewards** | ✅ Database | RL calculations, agent performance | `rewards` table |
| **Patterns** | ✅ Database | RL pattern detection | `patterns` table |
| **Campaigns** | ✅ Database | Marketing data, queryable | `campaigns` table |
| **Leads** | ✅ Database | Marketing data, queryable | `leads` table |
| **Logs** | ❌ Files | Streaming output, large text, debugging | `logs/*` |
| **Priority Files** | ❌ Files | User input, human-editable markdown | `reports/*.md` |
| **Task Definitions** | ❌ Files | User input, JSON task configs | `tasks/*.json` |
| **State Snapshots** | ❌ Files | Debugging, recovery, filesystem sync | `.compound-state/session-*/*.json` |
| **Documentation** | ❌ Files | Human-readable, version-controlled | `docs/**/*.md` |

---

## Database Storage (Structured Data)

### What Goes in Database

**Core Entities:**
- Tasks, Sessions, Agents, Teams
- User commands, automation candidates
- Experiments, patterns, lessons learned
- Gamification (XP, levels, achievements)
- Integrations, repositories

**Why Database:**
- ✅ **Queryable:** Complex filters (status, date range, agent)
- ✅ **Relational:** JOIN tasks with agents, sessions with teams
- ✅ **Aggregations:** COUNT, SUM, AVG for dashboards
- ✅ **ACID:** Transactions, concurrent access
- ✅ **Performance:** Indexed queries, fast lookups
- ✅ **API-Ready:** Direct SQL to JSON responses

**Example Queries:**
```sql
-- All failed tasks by agent
SELECT * FROM tasks WHERE status = 'failed' AND agent_id = 'agent-backend';

-- Agent performance
SELECT agent_id, COUNT(*) as total,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
FROM tasks GROUP BY agent_id;

-- Tasks by session with agent names
SELECT t.*, a.name, a.emoji
FROM tasks t JOIN agents a ON t.agent_id = a.id
WHERE t.session_id = 'session-123';
```

---

## File Storage (Operational Data)

### What Stays as Files

#### 1. Logs (`/logs/`)

**Location:**
```
logs/
  running-jobs/
    job-1770537842593-mfn5pu4.log       # Job execution logs
    job-1770537842593-mfn5pu4.json      # Job metadata
  orchestrator-sessions/
    session-*/orchestrator.log          # Orchestrator logs
    session-*/backend-orchestrated.log  # Specialist logs
  infrastructure-sessions/
    session-*/infrastructure.log        # Infrastructure logs
```

**Why Files:**
- ✅ **Streaming:** Real-time `tail -f` monitoring
- ✅ **Large Text:** Logs can be megabytes, impractical in DB
- ✅ **Standard Practice:** Industry standard (ELK stack, Splunk expect files)
- ✅ **Rotation:** Easy to rotate, compress, archive old logs
- ✅ **Debugging:** Engineers expect `grep`, `awk`, `tail` on logs

**Access:**
- API: `GET /api/logs/:sessionId` (reads from files)
- CLI: `tail -f logs/running-jobs/job-*.log`
- Dashboard: Job logs view (streams from files)

#### 2. Priority Files (`/reports/*.md`)

**Location:**
```
reports/
  priorities-2026-02-08.md              # Daily priorities (user-created)
  marketing-priority-20260207.md        # Marketing campaigns (user-created)
```

**Why Files:**
- ✅ **User Input:** CEO/PO creates these in text editor
- ✅ **Human-Editable:** Markdown format, version-controlled
- ✅ **Git-Tracked:** PRs reference these files
- ✅ **Historical Record:** Git history shows priority evolution

**Workflow:**
1. CEO creates `reports/priorities-2026-02-08.md` in text editor
2. Saves to git: `git add reports/ && git commit -m "Add priorities"`
3. Dashboard: Select file from dropdown → Start job
4. Orchestrator reads file → Creates tasks in database

**NOT in Database Because:**
- ❌ No need to query "all priorities" (they're dated, one-time use)
- ❌ Markdown formatting better in files than DB text fields
- ❌ Git is better version control than DB audit logs

#### 3. Task Definitions (`/tasks/*.json`)

**Location:**
```
tasks/
  marketing-prd.json                    # Campaign definitions (user-created)
```

**Why Files:**
- ✅ **User Input:** Marketing team creates campaign JSON
- ✅ **Template-Based:** Can be copied, modified, reused
- ✅ **Git-Tracked:** Campaign definitions version-controlled

**Example:**
```json
{
  "type": "marketing-campaign",
  "priority": "high",
  "deliverables": ["blog-post", "social-media", "email"],
  "target_audience": "enterprise-healthcare"
}
```

**NOT in Database Because:**
- ❌ These are input templates, not execution results
- ❌ Better to track in git than duplicate in DB

#### 4. State Snapshots (`.compound-state/session-*/*.json`)

**Location:**
```
.compound-state/
  session-1770537842/
    orchestrator.json                   # Orchestrator state
    backend.json                        # Backend specialist state
    infrastructure.json                 # Infrastructure state
```

**Why Files:**
- ✅ **Debugging:** Engineers can inspect exact state
- ✅ **Recovery:** Can restart from last known state
- ✅ **Sync Source:** Used by `sync-to-db.js` to populate database

**Flow:**
```
Orchestrator runs
    ↓ Writes state to
.compound-state/session-*/agent.json
    ↓ Synced via
scripts/sync-to-db.js
    ↓ Writes to
Database (tasks, sessions tables)
    ↓ Read by
API endpoints (/api/tasks, /api/sessions)
    ↓ Displayed in
Dashboard (kanban, engineering page)
```

**Why Both Files AND Database:**
- ✅ Files = source of truth for debugging, recovery
- ✅ Database = optimized for queries, dashboards, APIs

#### 5. Documentation (`/docs/**/*.md`)

**Location:**
```
docs/
  guides/
    quick-start.md
    po-workflow.md
    engineering-guide.md
  reference/
    agents.md
    api-reference.md
  setup/
    openclaw-setup.md
    email-setup.md
```

**Why Files:**
- ✅ **Human-Readable:** Markdown for developers, users
- ✅ **Version-Controlled:** Track documentation changes in git
- ✅ **Standard Practice:** All projects have docs in files
- ✅ **Easy Editing:** Any text editor, no DB schema changes

**NOT in Database Because:**
- ❌ Documentation isn't operational data
- ❌ Git provides better version control for text
- ❌ Engineers expect `README.md`, not SQL tables

---

## Data Flow Examples

### 1. Engineering Job Execution

```
User Action (Dashboard):
  "Start Engineering Job"
      ↓
Job Executor (Node.js):
  Spawns orchestrator.sh
      ↓
Orchestrator:
  Writes logs → logs/running-jobs/job-*.log (FILES)
  Writes state → .compound-state/session-*/orchestrator.json (FILES)
  Spawns specialists (Backend, Frontend, etc.)
      ↓
Specialists:
  Write logs → logs/orchestrator-sessions/session-*/agent.log (FILES)
  Write state → .compound-state/session-*/agent.json (FILES)
  Exit with status code
      ↓
Sync Script (scripts/sync-to-db.js):
  Reads .compound-state/session-*/agent.json (FILES)
  Writes to tasks table (DATABASE)
  Writes to sessions table (DATABASE)
      ↓
API Endpoints:
  GET /api/tasks → Reads from tasks table (DATABASE)
  GET /api/sessions → Reads from sessions table (DATABASE)
  GET /api/logs/:id → Reads from logs/running-jobs/*.log (FILES)
      ↓
Dashboard (Kanban):
  Fetches /api/tasks → Displays in kanban columns
  Clicks task → Modal with full details from database
```

### 2. Marketing Campaign

```
User Action (File):
  Creates tasks/marketing-prd.json (FILE)
  Commits to git
      ↓
Dashboard:
  Select campaign file from dropdown
  Click "Start Marketing Campaign"
      ↓
Jarvis Orchestrator:
  Reads tasks/marketing-prd.json (FILE)
  Spawns marketing agents
  Writes logs → logs/orchestrator-sessions/session-*/jarvis.log (FILES)
  Writes state → .compound-state/session-*/jarvis.json (FILES)
      ↓
Specialists (Vision, Loki, Pepper, etc.):
  Write logs → logs/orchestrator-sessions/session-*/agent.log (FILES)
  Write state → .compound-state/session-*/agent.json (FILES)
  Create campaigns → campaigns table (DATABASE)
  Create content → content table (DATABASE)
      ↓
Sync Script:
  Syncs session/tasks to database (DATABASE)
      ↓
Dashboard:
  Displays tasks in kanban (DATABASE)
  Displays campaigns list (DATABASE)
  Displays campaign logs (FILES via API)
```

---

## Rationale: Why Not Everything in Database?

### Files Are Better For:

**1. Logs**
- Logs are append-only streams (perfect for files)
- Gigabytes of logs = slow database queries
- Standard tooling expects files (`tail`, `grep`, ELK stack)

**2. User Input**
- Priority files are human-written markdown
- Better to edit `priorities.md` than insert SQL
- Git tracks changes better than DB audit logs

**3. Debugging**
- Engineers want to `cat .compound-state/session-*/backend.json`
- Easier than `SELECT * FROM sessions WHERE id = '...'`
- Files can be copied, emailed, inspected offline

**4. Historical Snapshots**
- State files = point-in-time snapshots for recovery
- Database = current state only (unless you add versioning)

### Database Is Better For:

**1. Queries**
```sql
-- Show all failed tasks this week
SELECT * FROM tasks
WHERE status = 'failed'
  AND started_at > datetime('now', '-7 days');
```
- Can't do this with grep on JSON files

**2. Relationships**
```sql
-- Tasks with agent details and team names
SELECT t.*, a.name, a.emoji, team.name as team_name
FROM tasks t
JOIN agents a ON t.agent_id = a.id
JOIN teams team ON a.team_id = team.id;
```
- Would require multiple file reads + manual joins

**3. Dashboards**
- Kanban board needs filtered, sorted, joined data
- API endpoints need fast JSON responses
- Database indexes make this instant

---

## Migration Strategy (Files → Database)

### When to Sync

**Automatic (Future):**
Add to end of `orchestrator.sh`:
```bash
# After session completes
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

### What Gets Synced

**FROM** `.compound-state/session-*/agent.json` (FILES)
**TO** `tasks` and `sessions` tables (DATABASE)

**Synced Data:**
- Session metadata (status, repo, branch, PR URL)
- Task records (description, status, agent, duration)
- Error messages, retry counts

**NOT Synced:**
- Logs (stay as files)
- Detailed state (stays in JSON for debugging)

---

## Summary

| Question | Answer |
|----------|--------|
| Where are tasks stored? | ✅ Database (`tasks` table) |
| Where are sessions stored? | ✅ Database (`sessions` table) |
| Where are commands stored? | ❌ Files (`docs/` + commands.html) |
| Where are logs stored? | ❌ Files (`logs/`) |
| Where are priority files? | ❌ Files (`reports/*.md`) - user input |
| Where is task metadata? | ❌ Files (`tasks/*.json`) - user input |
| Where is state? | ❌ Files (`.compound-state/`) + Database (synced) |

**Golden Rule:**
- **Structured, queryable data** → Database
- **Operational files (logs, inputs, state)** → Files

---

## Questions Answered

### Q: "Shouldn't commands be in the database?"

**A:** No, because:
- Commands are **documentation**, not **operational data**
- No need to query "show me all commands from last week"
- Better to version-control in markdown + display in UI
- commands.html now loads content from `docs/` files dynamically

### Q: "Shouldn't priority files be in database?"

**A:** No, because:
- Priority files are **user input** (CEO writes them)
- Human-editable markdown is better than DB text fields
- Git provides version control (see priority evolution)
- These are one-time inputs, not queryable data

### Q: "Why are logs in files, not database?"

**A:** Industry standard:
- Logs are **append-only streams** (perfect for files)
- Gigabytes of logs would slow database
- Standard tooling expects files (`tail -f`, `grep`, ELK)
- Can archive/compress/rotate files easily

### Q: "Why is state in both files AND database?"

**A:** Complementary:
- **Files** = source of truth for debugging, recovery
- **Database** = optimized for queries, dashboards, APIs
- Files persist full state for inspection
- Database gets synced subset for fast queries

---

## Accessing Data

### From Dashboard

| Data | How to Access |
|------|---------------|
| Tasks | Kanban board → fetches `/api/tasks` → reads from `tasks` table |
| Sessions | Engineering page → fetches `/api/sessions` → reads from `sessions` table |
| Agents | Management page → fetches `/api/agents` → reads from `agents` table |
| Logs | Job logs view → fetches `/api/logs/:id` → reads from `logs/running-jobs/*.log` |
| Campaigns | Marketing page → fetches `/api/data/campaigns` → reads from `campaigns` table |

### From CLI

| Data | How to Access |
|------|---------------|
| Tasks | `sqlite3 .compound-state/agent-service.db "SELECT * FROM tasks;"` |
| Sessions | `sqlite3 .compound-state/agent-service.db "SELECT * FROM sessions;"` |
| Logs | `tail -f logs/running-jobs/job-*.log` |
| State | `cat .compound-state/session-*/orchestrator.json` |
| Priority Files | `cat reports/priorities-2026-02-08.md` |

---

## Best Practices

### For Developers

✅ **DO:**
- Query database for task lists, metrics, dashboards
- Read logs from files for debugging
- Keep user input files (priority.md, task.json) in git
- Sync state files to database after jobs complete

❌ **DON'T:**
- Put logs in database (use files)
- Put user input in database (use files + git)
- Query JSON files directly (sync to DB first)
- Store large text in database (use files)

### For Users

✅ **DO:**
- Create priority files as markdown in `reports/`
- Create campaign definitions as JSON in `tasks/`
- Use dashboard to view tasks, sessions, metrics (database)
- Use dashboard logs view to see job output (files via API)

❌ **DON'T:**
- Manually edit database (use dashboard or API)
- Manually edit state files (orchestrator writes these)
- Expect to query logs via SQL (use `grep` on files)

---

**Result:** Clean separation of concerns, optimal performance, standard practices. 🎯
