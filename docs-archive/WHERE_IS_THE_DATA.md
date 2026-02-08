# WHERE IS THE DATA? 📊

**Quick Answer:** Data is stored in **SQLite database** + **JSON files** for session state + **file artifacts**.

---

## 🗂️ Current Data Architecture (Hybrid)

### SQLite Database (Primary)

**Location:** `.compound-state/agent-service.db`

**What's stored:**
- ✅ Teams (Engineering, Marketing)
- ✅ Agents (16 specialists + any custom agents)
- ✅ Sessions (job runs with status, timestamps)
- ✅ Tasks (individual agent work items)
- ✅ Experiments (RL keep/kill/double-down)
- ✅ Patterns (success/failure/repetition detection)
- ✅ Metrics (performance data)
- ✅ Rewards (RL feedback)
- ✅ User commands (for automation detection)
- ✅ Automation candidates (3+ repetitions)
- ✅ Lessons learned
- ✅ Campaigns, leads, content
- ✅ Repositories

**Database Schema:** `schema.sql` (400+ lines, 16 tables, 4 views)

**Access:**
```bash
# Direct SQL access
sqlite3 /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db

# View all agents
SELECT name, role, team_id, is_active FROM agents;

# View sessions
SELECT id, status, target_repo, started_at FROM sessions ORDER BY started_at DESC;

# View agent performance
SELECT * FROM v_agent_performance;
```

### JSON Files (Session State - Legacy)

**Location:** `.compound-state/session-*/`

Still used for detailed session state during job execution:
- orchestrator.json
- backend.json
- frontend.json
- infrastructure.json
- verification.json
- (marketing agents similarly)

### File Artifacts

**Location:** Target repo + `reports/`

- Code changes in target repo
- Marketing deliverables in `reports/`
- Logs in `logs/`

---

## 📊 Database Tables Overview

### Core Tables

**Teams:**
```sql
- id: team-engineering, team-marketing
- name: Engineering, Marketing
- domain: engineering, marketing
```

**Agents:** (6 Engineering + 10 Marketing + custom)
```sql
- id: agent-backend, agent-jarvis, etc.
- team_id: References teams
- name: Backend, Jarvis, etc.
- role: Description of specialty
- emoji: Visual identifier
- llm_preference: sonnet/opus/haiku
- success_rate: Performance metric (0-1)
- total_tasks_completed: Count
- is_active: TRUE/FALSE
```

**Sessions:** (Job runs)
```sql
- id: job-{timestamp}-{random}
- team_id: Which team ran this
- status: pending/in_progress/completed/failed/blocked
- target_repo: Path to repo
- priority_file: Input file
- branch_name: Git branch
- pr_url: Pull request URL
- started_at: Timestamp
- completed_at: Timestamp
```

**Tasks:** (Individual agent work)
```sql
- id: task-{uuid}
- session_id: Parent session
- agent_id: Which agent
- task_description: What to do
- status: pending/in_progress/completed/failed
- llm_used: Which model
- duration_seconds: How long
```

### RL Learning Tables

**Experiments:** (Keep/Kill/Double-down)
```sql
- id: exp-{uuid}
- name: Experiment name
- status: active/successful/failed/killed
- success_metric: What we're measuring
- current_value: Current performance
- decision: keep/kill/double_down
- decision_reason: Why this decision
```

**Patterns:** (Success/Failure/Repetition)
```sql
- id: pattern-{uuid}
- pattern_type: success/failure/user_repetition
- title: Human-readable name
- description: What this pattern is
- detection_count: How many times seen
- confidence_score: 0-1
- action_taken: What we did
```

**Metrics:**
```sql
- entity_type: session/task/agent/experiment
- entity_id: Which entity
- metric_name: What metric
- metric_value: Value
- recorded_at: Timestamp
```

**Rewards:**
```sql
- entity_type: task/session/experiment
- entity_id: Which entity
- reward_value: +/- points
- reason: Why this reward
```

### Automation Tables

**User Commands:**
```sql
- command_text: Raw command
- normalized_intent: Cleaned intent
- executed_at: When run
```

**Automation Candidates:** (3+ repetitions → new agent)
```sql
- id: auto-{uuid}
- pattern_description: What user keeps doing
- occurrence_count: How many times
- confidence_score: How sure we are
- is_automated: Created agent or not
- proposed_agent_name: Suggested name
- agent_id: Created agent if automated
```

### Marketing Tables

**Leads:**
```sql
- id: lead-{uuid}
- source: Where from
- email, name, company, phone
- status: new/contacted/qualified/converted
- score: Lead quality (0-100)
- assigned_to: Agent handling
```

**Campaigns:**
```sql
- id: campaign-{uuid}
- name: Campaign name
- type: email/social/seo/content
- status: planning/active/completed
- owner: Agent responsible
- metrics: JSON performance data
```

### Views (Analytics)

**v_agent_performance:**
```sql
SELECT
  a.id as agent_id,
  a.name,
  t.name as team_name,
  ROUND(a.success_rate * 100, 1) as success_rate_pct,
  a.total_tasks_completed,
  a.total_tasks_failed,
  ROUND(a.avg_duration_seconds / 60.0, 1) as avg_duration_minutes
FROM agents a
JOIN teams t ON a.team_id = t.id
WHERE a.is_active = TRUE
ORDER BY t.domain, a.name;
```

---

## 🎯 How Dashboard Accesses Data

### Via Database Queries (Primary)

```javascript
// dashboard/server.js
const db = require('./lib/database');

// Get all agents
app.get('/api/agents', (req, res) => {
  const agents = db.getAllAgents();
  res.json(agents);
});

// Get sessions
app.get('/api/sessions', (req, res) => {
  const sessions = db.getRecentSessions(50);
  res.json(sessions);
});

// Get agent performance
app.get('/api/rl/agent-performance', (req, res) => {
  const insights = learningController.getAgentInsights();
  res.json(insights);
});
```

### Via File Reads (Session State)

```javascript
// For detailed session logs
app.get('/api/logs/:sessionId', (req, res) => {
  const logFile = path.join(LOGS_DIR, `${sessionId}.log`);
  const logs = fs.readFileSync(logFile, 'utf8');
  res.send(logs);
});
```

---

## 📱 Dashboard API Endpoints

### Agent Management
```
GET  /api/agents                    - List all agents
POST /api/agents/create             - Hire new agent
POST /api/agents/:id/fire           - Fire agent
POST /api/agents/:id/rehire         - Rehire agent
GET  /api/agents/:id                - Get agent details
GET  /api/agents/:id/evaluation     - Get RL evaluation
PATCH /api/agents/:id               - Update agent
```

### Job Control
```
POST /api/jobs/start                - Start engineering/marketing job
POST /api/jobs/:id/stop             - Stop running job
GET  /api/jobs/:id/status           - Get job status
GET  /api/jobs/:id/logs             - Get job logs
GET  /api/jobs                      - List all jobs
```

### RL Dashboard
```
GET  /api/rl/experiments            - Get experiments
POST /api/rl/experiments/evaluate   - Evaluate all experiments
GET  /api/rl/patterns               - Get detected patterns
POST /api/rl/patterns/detect        - Run pattern detection
GET  /api/rl/automation-candidates  - Get automation candidates
POST /api/rl/automation-candidates/:id/approve - Approve candidate
GET  /api/rl/agent-performance      - Get agent insights
GET  /api/rl/llm-stats              - Get LLM usage stats
```

### Data APIs (Marketing)
```
GET  /api/data/leads                - Get leads
GET  /api/data/campaigns            - Get campaigns
GET  /api/data/content              - Get content pieces
GET  /api/data/social               - Get social posts
```

---

## 💾 Data Flow

### Engineering Job Flow

```
1. User clicks "Start Engineering Job" in dashboard
   ↓
2. POST /api/jobs/start
   ↓
3. job-executor.js spawns orchestrator.sh
   ↓
4. Orchestrator creates session in database:
   db.createSession({
     sessionId, teamId, targetRepo, priorityFile, branchName
   })
   ↓
5. Each specialist agent:
   - Creates task in database: db.createTask(...)
   - Updates task status as it works
   - Records metrics: db.recordMetric(...)
   - Writes detailed state to JSON files
   ↓
6. On completion:
   - Session status updated to 'completed'
   - Rewards issued: db.issueReward(...)
   - RL evaluation runs: learningController.analyzeSession(...)
   ↓
7. Dashboard queries database and displays results
```

### RL Learning Flow

```
1. Tasks complete with success/failure
   ↓
2. Rewards issued (+10 success, -5 fail)
   ↓
3. Metrics recorded (duration, status, etc.)
   ↓
4. Pattern detector analyzes:
   - Success patterns (90%+ success → double down)
   - Failure patterns (3+ consecutive → kill)
   - User repetitions (3+ same task → automation candidate)
   ↓
5. Experiments evaluated:
   - Keep: Continue if improving
   - Kill: 3+ consecutive failures
   - Double Down: 90%+ success, 5+ attempts
   ↓
6. Automation candidates created:
   - User repeats task 3+ times
   - System proposes new dedicated agent
   - Awaits CEO approval
   ↓
7. Agent performance tracked:
   - Success rate updated
   - RL recommendation: Monitor/Continue/Double Down/Investigate/Fire
```

---

## 🔍 Finding Specific Data

### Where are agents?
```bash
sqlite3 .compound-state/agent-service.db "SELECT * FROM agents;"
```

### Where are sessions?
```bash
sqlite3 .compound-state/agent-service.db "SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;"
```

### Where is agent performance?
```bash
sqlite3 .compound-state/agent-service.db "SELECT * FROM v_agent_performance;"
```

### Where are experiments?
```bash
sqlite3 .compound-state/agent-service.db "SELECT * FROM experiments WHERE status = 'active';"
```

### Where are automation candidates?
```bash
sqlite3 .compound-state/agent-service.db "SELECT * FROM automation_candidates WHERE is_automated = FALSE;"
```

### Where are detailed session logs?
```bash
cat logs/running-jobs/job-{timestamp}-{random}.log
```

---

## 💡 Why SQLite + JSON Hybrid?

### SQLite (Queryable Data)

**Pros:**
- ✅ SQL queries for analytics
- ✅ Relationships (foreign keys)
- ✅ Views for complex aggregations
- ✅ ACID transactions
- ✅ Single file (easy backup)
- ✅ No hosting required (local)
- ✅ Git-friendly (small size)

**Use for:**
- Agent metadata
- Session tracking
- Performance metrics
- RL learning data
- Relationships between entities

### JSON Files (Detailed State)

**Pros:**
- ✅ Flexible schema
- ✅ Easy to debug (cat file)
- ✅ Git-friendly (diffs visible)
- ✅ No schema migrations

**Use for:**
- Detailed session state during execution
- Agent conversations/reasoning
- Temporary data that gets summarized into DB

---

## 📝 Summary

### Data Locations:

| Data Type | Storage | Location | Access |
|-----------|---------|----------|--------|
| **Agents** | SQLite | `.compound-state/agent-service.db` → agents table | `db.getAllAgents()` |
| **Sessions** | SQLite | `.compound-state/agent-service.db` → sessions table | `db.getRecentSessions()` |
| **Tasks** | SQLite | `.compound-state/agent-service.db` → tasks table | `db.getSessionTasks()` |
| **Performance** | SQLite View | `.compound-state/agent-service.db` → v_agent_performance | `db.getAgentPerformance()` |
| **Experiments** | SQLite | `.compound-state/agent-service.db` → experiments table | `db.getActiveExperiments()` |
| **Patterns** | SQLite | `.compound-state/agent-service.db` → patterns table | `db.getPatterns()` |
| **Session State** | JSON | `.compound-state/session-*/*.json` | `fs.readFileSync()` |
| **Job Logs** | Text | `logs/running-jobs/*.log` | `fs.readFileSync()` |
| **Code Changes** | Git | Target repo | Git commands |
| **Marketing Reports** | Files | `reports/` | File system |

### Quick Access:

**Database:**
```bash
sqlite3 /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db
```

**Dashboard:**
```
http://localhost:3030
```

**API Examples:**
```bash
curl http://localhost:3030/api/agents
curl http://localhost:3030/api/sessions
curl http://localhost:3030/api/rl/agent-performance
```

---

**TL;DR:** We use **SQLite database** for queryable, relational data (agents, sessions, RL metrics) + **JSON files** for detailed session state + **file system** for artifacts. Best of both worlds! 🎉
