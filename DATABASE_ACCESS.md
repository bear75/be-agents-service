# Database Access Guide 🗄️

## Quick Answer

**Is the DB running?** There is no separate database process. SQLite is file-based. When you run `yarn workspace server start`, the Node server opens the DB file and keeps it in use.

**Database Locations** (two SQLite files):

| Used by | Path |
|---------|------|
| apps/server (sessions, teams, metrics, marketing, commands) | `data/agent-service.db` |
| lib/ (agents, integrations, gamification, tasks) | `.compound-state/agent-service.db` |

```bash
cd ~/HomeCare/be-agents-service
# apps/server DB:
ls -la data/agent-service.db
# lib/ DB:
ls -la .compound-state/agent-service.db
```

**Type:** SQLite3

**Dashboard URL:** http://localhost:3030 (or PORT/DASHBOARD_PORT env)

---

## 🔍 How to Access the Database

### Option 1: TablePlus (Recommended GUI) ✅

1. **Open TablePlus**
2. **Create New Connection** → Select **SQLite**
3. **Configure Connection:**
   - **Name:** Agent Service DB
   - **Database Path:** `{REPO_ROOT}/data/agent-service.db` (e.g. `~/HomeCare/be-agent-service/data/agent-service.db`)
   - Click **Connect**

**Features in TablePlus:**
- Browse all 24 tables visually
- Run SQL queries
- Edit data directly
- Export data
- View table relationships
- Create indexes

---

### Option 2: Command Line (SQLite CLI)

**Direct Access:**
```bash
cd ~/HomeCare/be-agent-service
sqlite3 data/agent-service.db
```

**Useful Commands:**
```sql
-- List all tables
.tables

-- Show table schema
.schema agents

-- View all agents
SELECT * FROM agents;

-- View leaderboard
SELECT * FROM v_leaderboard LIMIT 10;

-- View agent gamification
SELECT * FROM v_agent_gamification;

-- Exit
.quit
```

---

### Option 3: Web Dashboard (Visual)

**Already Running:** http://localhost:3030

**Pages:**
- **Management Team:** http://localhost:3030/management-team.html
- **Engineering:** http://localhost:3030/engineering.html
- **Marketing:** http://localhost:3030/sales-marketing.html
- **RL Dashboard:** http://localhost:3030/rl-dashboard.html

---

## 📋 Database Structure

### Core Tables (16)
```
teams                    -- Engineering, Marketing
agents                   -- 20 specialists
sessions                 -- Job runs
tasks                    -- Individual agent tasks
experiments              -- RL experiments
patterns                 -- Success/failure patterns
metrics                  -- Performance metrics
rewards                  -- RL rewards
user_commands            -- User command tracking
automation_candidates    -- 3+ repetitions
lessons_learned          -- Knowledge base
campaigns                -- Marketing campaigns
leads                    -- Marketing leads
content                  -- Content pieces
repositories             -- Multi-repo tracking
llm_usage                -- LLM cost tracking
```

### Gamification Tables (8)
```
agent_levels             -- XP, level, title
xp_transactions          -- XP earning history
achievement_definitions  -- Available achievements (15 seeded)
agent_achievements       -- Unlocked achievements
agent_streaks            -- Consecutive day tracking
leaderboard_cache        -- Leaderboard rankings
level_thresholds         -- XP per level (12 levels)
```

### Views (4)
```
v_agent_performance      -- Success rates, tasks, duration
v_experiment_status      -- Experiment summaries
v_user_command_patterns  -- Command repetition detection
v_active_sessions        -- Current job sessions
v_agent_gamification     -- XP, level, streaks, achievements
v_leaderboard            -- Global rankings
```

---

## 🔐 Environment Variables (.env file)

### Do You Need a .env File?

**Currently: NO** - The system works without it.

**But you CAN create one for:**
- Custom database path
- Dashboard port
- API keys (if needed later)
- Environment-specific settings

### Create .env File (Optional)

```bash
# Navigate to project root
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service

# Copy template
cp .env.template .env

# Edit .env
nano .env
```

### Example .env Contents

```bash
# Dashboard Configuration
DASHBOARD_PORT=3030

# Database Configuration
DB_PATH=.compound-state/agent-service.db

# LLM Configuration (if needed)
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here

# Environment
NODE_ENV=development
```

### Loading .env in Code

If you create a `.env` file, add this to `dashboard/server.js`:

```javascript
// At the top of server.js
require('dotenv').config();

const PORT = process.env.DASHBOARD_PORT || 3030;
const DB_PATH = process.env.DB_PATH || '.compound-state/agent-service.db';
```

---

## 📊 Common SQL Queries

### View All Agents with Stats
```sql
SELECT
  name,
  emoji,
  team_id,
  success_rate,
  total_tasks_completed,
  total_tasks_failed,
  is_active
FROM agents
ORDER BY success_rate DESC;
```

### View Leaderboard (Top 10 by XP)
```sql
SELECT
  agent_name,
  agent_emoji,
  team_name,
  level,
  total_xp,
  achievements_count,
  current_streak
FROM v_leaderboard
ORDER BY total_xp DESC
LIMIT 10;
```

### View Agent Gamification Details
```sql
SELECT
  agent_name,
  level,
  title,
  level_emoji,
  current_xp,
  total_xp,
  xp_to_next_level,
  current_streak,
  achievements_unlocked
FROM v_agent_gamification
WHERE agent_id = 'agent-backend';
```

### View Recent XP Transactions
```sql
SELECT
  agent_id,
  amount,
  reason,
  source_type,
  created_at
FROM xp_transactions
ORDER BY created_at DESC
LIMIT 20;
```

### View Unlocked Achievements
```sql
SELECT
  a.agent_id,
  ag.name as agent_name,
  ad.name as achievement_name,
  ad.emoji,
  ad.tier,
  ad.xp_reward,
  a.unlocked_at
FROM agent_achievements a
JOIN agents ag ON a.agent_id = ag.id
JOIN achievement_definitions ad ON a.achievement_id = ad.id
ORDER BY a.unlocked_at DESC;
```

---

## 🛠️ Database Maintenance

### Backup Database
```bash
# Create backup
cp .compound-state/agent-service.db .compound-state/agent-service.db.backup-$(date +%Y%m%d)

# Verify backup
ls -lh .compound-state/*.backup-*
```

### Check Database Size
```bash
ls -lh .compound-state/agent-service.db
```

### Vacuum Database (Optimize)
```bash
sqlite3 .compound-state/agent-service.db "VACUUM;"
```

### Verify Database Integrity
```bash
sqlite3 .compound-state/agent-service.db "PRAGMA integrity_check;"
```

---

## 🔄 API Access (Programmatic)

### Node.js Access
```javascript
const db = require('./lib/database');

// Get all agents
const agents = db.getAllAgents();

// Get leaderboard
const gamification = require('./lib/gamification');
const leaderboard = gamification.getLeaderboard('xp', 10);

// Award XP
gamification.awardXP('agent-backend', 50, 'Manual bonus', 'manual');
```

### HTTP API Access
```bash
# Get all agents
curl http://localhost:3030/api/agents

# Get leaderboard
curl "http://localhost:3030/api/gamification/leaderboard?metric=xp&limit=10"

# Get agent gamification
curl http://localhost:3030/api/gamification/agent/agent-backend

# Award XP
curl -X POST http://localhost:3030/api/gamification/award-xp \
  -H 'Content-Type: application/json' \
  -d '{"agentId": "agent-backend", "amount": 50, "reason": "Bonus"}'
```

---

## 🚨 Troubleshooting

### Database Locked Error
```bash
# Find processes using the database
lsof .compound-state/agent-service.db

# Kill if needed
kill -9 <PID>
```

### Database Corrupted
```bash
# Restore from backup
cp .compound-state/agent-service.db.backup-YYYYMMDD .compound-state/agent-service.db
```

### Reset Database (Nuclear Option)
```bash
# Backup first!
cp .compound-state/agent-service.db .compound-state/agent-service.db.backup

# Delete and reinitialize
rm .compound-state/agent-service.db
sqlite3 .compound-state/agent-service.db < schema.sql
sqlite3 .compound-state/agent-service.db < gamification-schema.sql
sqlite3 .compound-state/agent-service.db < seed.sql
```

---

## 📖 Related Documentation

- **WHERE_IS_THE_DATA.md** - Complete data architecture guide
- **GAMIFICATION_IMPLEMENTATION.md** - Gamification system details
- **TESTING-GUIDE.md** - How to test HR system
- **schema.sql** - Core database schema
- **gamification-schema.sql** - Gamification schema
- **seed.sql** - Seed data (teams, agents, levels, achievements)

---

## 🎯 Quick Start

**1. View Database in TablePlus:**
```
File > New Connection > SQLite
Path: /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db
```

**2. View Dashboard:**
```
http://localhost:3030/management-team.html
```

**3. Query via CLI:**
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service
sqlite3 .compound-state/agent-service.db "SELECT * FROM v_leaderboard LIMIT 5;"
```

---

**Last Updated:** 2026-02-08
**Database Version:** SQLite 3
**Size:** ~336 KB (20 agents + gamification data)
