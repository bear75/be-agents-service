# HR Agent Management System - Testing Guide

## Quick Start

Dashboard is running at: **http://localhost:3030**

## 🧪 Option 1: Test via Web UI (Easiest)

### 1. Open Management Dashboard
```bash
open http://localhost:3030
```

### 2. Hire a New Agent
1. Scroll to the **HR - Agent Lead** card
2. Click **"➕ Hire Agent"** button
3. Enter:
   - Team: `team-engineering` or `team-marketing`
   - Name: `Your Agent Name`
   - Role: `What this agent does`
   - LLM: `sonnet` (or opus/haiku)
4. Click OK
5. You should see "✅ Agent hired successfully"
6. Scroll down - your new agent appears in "All Agents" section

### 3. View Agent Details
1. Scroll to "All Agents" section
2. Click **"View Details"** on any agent card
3. See complete profile with:
   - Performance stats
   - RL recommendation
   - Active/inactive status

### 4. View RL Evaluations
1. In HR card, click **"📊 Evaluations"**
2. See all agents with recommendations:
   - ⭐ **Double Down** (90%+ success)
   - ✅ **Continue** (normal)
   - ⚠️ **Investigate** (<50% success)
   - 🔴 **Consider Firing** (<30% success)

### 5. Fire an Agent
1. Click **"❌ Fire Agent"** in HR card
2. Select agent number from the list
3. Review performance and confirm
4. Agent is deactivated (can be rehired later)

## 🔧 Option 2: Test via API (Technical)

### Run Automated Test Suite
```bash
/tmp/test-hr-system.sh
```

This runs 10 comprehensive tests covering:
- List agents
- Create agent
- Get details
- Evaluation
- Fire/rehire cycle
- Updates
- Performance metrics

### Manual API Tests

**List all agents:**
```bash
curl http://localhost:3030/api/agents | jq
```

**Create new agent:**
```bash
curl -X POST http://localhost:3030/api/agents/create \
  -H 'Content-Type: application/json' \
  -d '{
    "teamId": "team-engineering",
    "name": "Security Specialist",
    "role": "Security audits and penetration testing",
    "llmPreference": "opus",
    "emoji": "🔒"
  }'
```

**Get agent details:**
```bash
curl http://localhost:3030/api/agents/agent-backend | jq
```

**Get agent RL evaluation:**
```bash
curl http://localhost:3030/api/agents/agent-backend/evaluation | jq
```

**Fire agent:**
```bash
curl -X POST http://localhost:3030/api/agents/agent-backend/fire
```

**Rehire agent:**
```bash
curl -X POST http://localhost:3030/api/agents/agent-backend/rehire
```

**Update agent:**
```bash
curl -X PATCH http://localhost:3030/api/agents/agent-backend \
  -H 'Content-Type: application/json' \
  -d '{"role": "Updated role", "emoji": "🎯"}'
```

## 📊 Option 3: Check Database Directly

**View all agents:**
```bash
sqlite3 /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db \
  "SELECT name, role, team_id, is_active FROM agents ORDER BY team_id, name;"
```

**View agent performance:**
```bash
sqlite3 /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db \
  "SELECT * FROM v_agent_performance;"
```

**Count active agents:**
```bash
sqlite3 /Users/bjornevers_MacPro/HomeCare/be-agent-service/.compound-state/agent-service.db \
  "SELECT team_id, COUNT(*) as active_agents FROM agents WHERE is_active = 1 GROUP BY team_id;"
```

## 🎯 What to Look For

### Success Indicators:
- ✅ Agent appears in "All Agents" section after creation
- ✅ Agent count updates in HR card
- ✅ Agent details show correct information
- ✅ `is_active` changes from 1 to 0 when fired
- ✅ `is_active` changes back to 1 when rehired
- ✅ RL evaluation shows recommendation based on performance

### Performance Metrics (After Running Jobs):
When you start jobs via Engineering or Marketing pages:
- Success rate updates based on task completion
- RL recommendations change:
  - **Monitor**: No tasks yet (0 tasks)
  - **Continue**: Normal performance
  - **Double Down**: 90%+ success, 5+ tasks
  - **Investigate**: <50% success, 5+ tasks
  - **Consider Firing**: <30% success, 10+ tasks

## 🚀 Test Full Workflow

1. **Hire Agent** → Check it appears in All Agents
2. **Start Engineering Job** → Go to Engineering page, start a job
3. **Wait for Job** → Monitor Active Jobs section
4. **Check Performance** → Agent success rate updates
5. **View Evaluation** → See RL recommendation
6. **Fire Low Performers** → Remove agents with <50% success
7. **Double Down** → Assign more work to 90%+ performers

## 📱 Navigation Test

Verify all 5 pages load:
```bash
open http://localhost:3030/management-team.html
open http://localhost:3030/engineering.html
open http://localhost:3030/sales-marketing.html
open http://localhost:3030/rl-dashboard.html
open http://localhost:3030/commands.html
```

All pages should have working navigation tabs at the top.

## 🐛 Troubleshooting

**"Not Found" error:**
- Server may have stopped. Restart: `node /Users/bjornevers_MacPro/HomeCare/be-agent-service/dashboard/server.js &`

**No agents showing:**
- Check database: `sqlite3 .../.compound-state/agent-service.db "SELECT COUNT(*) FROM agents;"`
- Should show 16+ agents

**Can't create agent:**
- Check server logs: `tail -50 /tmp/dashboard-test2.log`
- Verify team ID is `team-engineering` or `team-marketing`

**Agent creation works but can't retrieve:**
- Restart server to reload code changes
- Check agent ID format returned in creation response

## ✅ Expected Results

After running all tests:
- **Hire**: New agent appears with unique ID
- **Details**: Full profile with team, role, LLM, status
- **Fire**: `is_active` = 0, agent hidden from active lists
- **Rehire**: `is_active` = 1, agent shows in active lists again
- **Evaluation**: Shows success rate, tasks, recommendation, reason
- **Performance**: All 16+ agents listed with metrics

Everything should complete in <10 seconds per test.
