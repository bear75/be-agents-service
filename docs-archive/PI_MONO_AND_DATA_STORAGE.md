# Pi-Mono & Data Storage Clarification

**Date:** 2026-02-08
**Updated:** Architecture now uses SQLite Database + JSON hybrid storage

---

## 📋 Quick Answers

### 1. Pi-Mono Status: PLANNED, NOT IMPLEMENTED

**What is pi-mono?**
https://github.com/badlogic/pi-mono/ - A local LLM framework for running CodeLlama, DeepSeek Coder, and other open-source models locally.

**Status:** Documented in roadmap as "Future: Local LLM Specialist" but not yet implemented.

**Where documented:** `/Users/bjornevers_MacPro/HomeCare/be-agent-service/AGENTS.md` lines 635-682

### 2. Data Storage: SQLITE DATABASE + JSON FILES

**Storage Method:** SQLite database (`.compound-state/agent-service.db`) + JSON files for session state
**Database:** SQLite with 16 tables, 4 views
**Why hybrid?** SQLite for queryable relational data, JSON for detailed session state during execution

---

## Data Storage Architecture (UPDATED 2026-02-08)

### Current Architecture

```
~/HomeCare/be-agent-service/
├── .compound-state/              # DATA STORAGE
│   ├── agent-service.db          # SQLite DATABASE (PRIMARY)
│   │                             # - 16 tables (teams, agents, sessions, tasks, etc.)
│   │                             # - 4 views (performance, leaderboard, etc.)
│   │                             # - Gamification system (XP, levels, achievements)
│   │                             # - RL learning (experiments, patterns, metrics)
│   │
│   └── session-{timestamp}/      # SESSION STATE (JSON files during execution)
│       ├── orchestrator.json     # Orchestrator status, phase
│       ├── backend.json          # Backend specialist state
│       ├── frontend.json         # Frontend specialist state
│       ├── infrastructure.json   # Infrastructure specialist state
│       └── verification.json     # Verification results
│
├── logs/                         # LOG FILES
│   ├── orchestrator-sessions/
│   │   └── session-{timestamp}/
│   │       ├── orchestrator.log
│   │       ├── backend.log
│   │       ├── frontend.log
│   │       └── verification.log
│   ├── auto-compound.log
│   └── compound-review.log
│
└── dashboard/
    ├── server.js                 # Reads from SQLite DB + JSON files
    └── lib/database.js           # SQLite operations wrapper
```

### Why SQLite + JSON Hybrid?

**SQLite Database (Primary):**
- ✅ Queryable data (SQL queries for analytics)
- ✅ Relationships (foreign keys between entities)
- ✅ ACID transactions
- ✅ Views for complex aggregations
- ✅ Single file (easy backup)
- ✅ No hosting required (local)
- ✅ Perfect for single-user automation

**What's Stored in SQLite:**
- Teams (Engineering, Marketing)
- Agents (20 specialists + custom agents)
- Sessions (job runs with status, timestamps)
- Tasks (individual agent work items)
- Experiments (RL keep/kill/double-down)
- Patterns (success/failure/repetition detection)
- Metrics (performance data)
- Rewards (RL feedback)
- User commands (for automation detection)
- Automation candidates (3+ repetitions)
- Lessons learned
- Campaigns, leads, content
- Repositories
- **Gamification:** XP, levels, achievements, streaks, leaderboards

**JSON Files (Session State):**
- ✅ Flexible schema
- ✅ Detailed state during execution
- ✅ Agent conversations/reasoning
- ✅ Easy to debug (cat file)
- ✅ Git-friendly (diffs visible)

**What's Stored in JSON:**
- Detailed session state during job execution
- Agent-specific context and reasoning
- Temporary data that gets summarized into DB

### Database Schema

**Core Tables:**
```sql
teams                    -- Engineering, Marketing
agents                   -- 20 specialists (10 eng + 10 marketing)
sessions                 -- Job runs (status, timestamps, PR URLs)
tasks                    -- Individual agent work items
experiments              -- RL experiments (keep/kill/double_down)
patterns                 -- Success/failure/repetition patterns
metrics                  -- Performance metrics
rewards                  -- RL reward signals
user_commands            -- User command tracking
automation_candidates    -- Repeated tasks (3+ → new agent)
lessons_learned          -- Accumulated knowledge
campaigns                -- Marketing campaigns
leads                    -- Marketing leads
content                  -- Content pieces
repositories             -- Multi-repo tracking
llm_usage                -- LLM cost tracking
```

**Gamification Tables (New!):**
```sql
agent_levels             -- XP, level, title per agent
xp_transactions          -- XP earning history
achievement_definitions  -- Available achievements
agent_achievements       -- Unlocked achievements
agent_streaks            -- Consecutive task completion streaks
leaderboard_cache        -- Leaderboard rankings
level_thresholds         -- XP required per level (1-12)
```

**Views:**
```sql
v_agent_performance      -- Success rates, task counts, avg duration
v_experiment_status      -- Experiment summaries
v_user_command_patterns  -- Command repetition detection
v_active_sessions        -- Current job sessions
v_agent_gamification     -- XP, level, streaks, achievements per agent
v_leaderboard            -- Global rankings (XP, tasks, success rate)
```

### Database Access

**Direct SQL:**
```bash
sqlite3 .compound-state/agent-service.db
```

**Via Dashboard API:**
```bash
curl http://localhost:3030/api/agents
curl http://localhost:3030/api/sessions
curl http://localhost:3030/api/rl/agent-performance
curl http://localhost:3030/api/gamification/leaderboard
```

**Via Node.js:**
```javascript
const db = require('./lib/database');
const agents = db.getAllAgents();
const performance = db.getAgentPerformance();
```

### Why Not Convex DB or PostgreSQL?

**Our Use Case:**
- Single user (Product Owner)
- Mac mini automation
- Overnight jobs
- Local execution
- No multi-user collaboration needed

**SQLite Advantages:**
- Zero setup (no server required)
- Single file (easy backup/restore)
- ACID transactions
- Full SQL support
- Extremely fast for read-heavy workloads
- Perfect for embedded use cases
- No network latency
- No authentication/authorization overhead

**When to Upgrade to PostgreSQL/Convex:**
- Multi-user collaboration
- Remote team access
- Real-time agent-to-agent chat
- Cloud deployment
- Multi-device sync
- Advanced analytics with BI tools

**For now:** SQLite is perfect for single-user automation.

---

## Gamification System (New!)

### Overview

**Managed by:** HR Agent using Agent Levelup expert (agent-levelup)

**Features:**
- XP earning from task completions
- 12 levels (Rookie → Divine)
- 15+ achievements (Bronze → Legendary)
- Streak tracking (consecutive days)
- Leaderboards (XP, tasks, success rate)

### XP Rewards

```
Task completed:         +10 XP
Quick completion (<2m): +15 XP bonus
First task of day:      +5 XP bonus
Session completed:      +25 XP
Perfect session (0 fails): +75 XP bonus
PR merged:              +50 XP
User praise:            +100 XP
Level up:               +level*10 XP bonus
Achievement unlocked:   +varies (50-1000 XP)
```

### Level System

```
Level 1:  Rookie        🌱 (0 XP)
Level 2:  Apprentice    📚 (100 XP)
Level 3:  Junior        👶 (250 XP)
Level 4:  Associate     🎓 (500 XP)
Level 5:  Specialist    💼 (1,000 XP)
Level 6:  Senior        🎯 (2,000 XP)
Level 7:  Expert        ⭐ (4,000 XP)
Level 8:  Master        🏆 (8,000 XP)
Level 9:  Grandmaster   👑 (16,000 XP)
Level 10: Legend        🔮 (32,000 XP)
Level 11: Mythic        🌟 (64,000 XP)
Level 12: Divine        ✨ (100,000 XP)
```

### Sample Achievements

- 🎯 First Steps (Complete 1 task) - 50 XP
- ⭐ Excellence (90%+ success rate) - 300 XP
- 🔥 On a Roll (3-day streak) - 50 XP
- 🏆 Flawless (100% success, 10+ tasks) - 1000 XP
- ⚡ Speed Demon (5 tasks <2 min avg) - 400 XP

### Dashboard Integration

```
http://localhost:3030/management-team.html
- View agent levels, XP, achievements
- Leaderboards (top agents by XP/tasks/success)

API Endpoints:
GET  /api/gamification/agent/:id      - Agent XP summary
GET  /api/gamification/leaderboard    - Global rankings
GET  /api/gamification/achievements   - All achievements
POST /api/gamification/award-xp       - Manually award XP
```

---

## Pi-Mono Deep Dive

### What Was Planned

From `AGENTS.md`:

```markdown
## Future: Local LLM Specialist (Simple Tasks)

**Location:** TBD (agents/local-llm-specialist.sh)
**Prompt:** TBD
**Model:** Local LLM via pi-mono or ollama (CodeLlama, DeepSeek Coder)

### Ideal Tasks For Local LLM

- ✅ Package updates (yarn workspace add)
- ✅ Documentation formatting
- ✅ Log summarization
- ✅ Error message parsing
- ✅ CLAUDE.md updates
- ✅ Simple config changes
- ✅ Test file generation (basic)

### Benefits

- **Cost**: Free (local inference)
- **Speed**: No API latency (~500ms vs ~2s)
- **Privacy**: Documentation stays local
- **Availability**: Works offline
```

### Why Not Implemented Yet

**Current Focus:** Core functionality is now working (SQLite DB, RL learning, gamification).

**Priority:** Functionality > Cost optimization (for now)

**Roadmap Position:** Phase 4-5

### When It Should Be Implemented

**Best time:** After gamification and RL learning are fully operational and tested.

**Estimated effort:** 1-2 weeks

---

## Summary

### Data Storage (UPDATED)
- **Method:** SQLite database + JSON files (hybrid)
- **Location:** `.compound-state/agent-service.db` + `.compound-state/session-*/` + `logs/`
- **Database:** SQLite with 16 core tables + 8 gamification tables + 4 views
- **Why:** Perfect for single-user automation with queryable data + flexible session state

### Pi-Mono
- **Status:** Planned for future (Phase 4-5)
- **Purpose:** Run simple tasks locally to reduce API costs
- **Implementation:** 1-2 weeks when we're ready

### Gamification System (NEW!)
- **Status:** ✅ Implemented
- **Features:** XP, levels (1-12), achievements, streaks, leaderboards
- **Managed by:** HR Agent + Agent Levelup expert

### When to Add PostgreSQL/Convex?

**If you later want to:**
- Multi-user collaboration
- Remote team access
- Cloud deployment
- Real-time agent chat
- Multi-device sync

**Then:** Migrate from SQLite to PostgreSQL or Convex DB.

**For now:** SQLite is simpler, faster, and perfect for single-Mac-mini automation.

---

**Questions?** See:
- `WHERE_IS_THE_DATA.md` - Complete data architecture guide
- `TESTING-GUIDE.md` - How to test HR system and gamification
- `MAC_MINI_SETUP.md` - Setup guide (includes SQLite initialization)
