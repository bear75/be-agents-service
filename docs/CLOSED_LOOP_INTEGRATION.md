# Closed-Loop Human-AI Integration

Complete documentation for the bi-directional Telegram ↔ Agent Service integration.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        YOU (Human)                          │
│                 Telegram                         │
└────────────────────┬───────────────────▲────────────────────┘
                     │                   │
              [conversational]      [proactive notifications]
                     │                   │
┌────────────────────▼───────────────────┴────────────────────┐
│              OpenClaw Gateway (Darwin)                      │
│        Messaging interface + MCP bridge                     │
│  Tools: add_to_inbox, get_overview, trigger_agent, etc.   │
└────────────────────┬───────────────────▲────────────────────┘
                     │                   │
              [reads/writes]        [reads reports]
                     │                   │
┌────────────────────▼───────────────────┴────────────────────┐
│         Shared Markdown Workspace (iCloud)                  │
│   📥 inbox.md  🎯 priorities.md  📝 tasks.md               │
│   📄 agent-reports/  📅 check-ins/  🧠 memory/            │
└────────────────────┬───────────────────▲────────────────────┘
                     │                   │
              [reads priority#1]   [writes results]
                     │                   │
┌────────────────────▼───────────────────┴────────────────────┐
│           Agent Service Orchestrator (port 3030)            │
│   ⚙️ Engineering Team (9 specialists)                      │
│   📢 Marketing Team (10 Marvel agents)                     │
│   👔 Management Team (4 executives)                        │
│   🔄 Compound loops + Multi-agent workflows                │
│   🎮 Gamification (XP, levels, achievements)               │
│   📊 Dashboard UI (React SPA)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## The Complete Flow

### 1. You Add a Priority (Telegram → Workspace)

**Telegram:**
```
You: "add priority: Fix the scheduling overlap bug"
Darwin: "✅ Added to priorities.md. Run now or wait for tonight (11 PM)?"
You: "run now"
Darwin: "✅ Agent triggered! Check dashboard for progress."
```

**Behind the scenes:**
- OpenClaw receives message
- Calls `add_to_inbox` MCP tool
- Writes to `workspace/priorities.md` on iCloud
- You choose "now" → OpenClaw calls `trigger_agent` tool
- Trigger API: `POST /api/agents/trigger/beta-appcaire`

### 2. Agent Service Executes (Workspace → Agent → Workspace)

**Auto-compound workflow:**
1. Reads `workspace/priorities.md` → picks Priority #1
2. Creates feature branch: `feature/auto-<timestamp>`
3. Orchestrates specialist agents (Backend, Frontend, Infrastructure, etc.)
4. Compound loop: iterates until task complete
5. Creates PR: `gh pr create --draft`
6. Writes session report to `workspace/agent-reports/latest-session.md`
7. **NEW:** Sends completion notification via Telegram

**Agent service components:**
- `scripts/compound/auto-compound.sh` - Main orchestration
- `scripts/compound/loop.sh` - Task execution loop
- `agents/*-specialist.sh` - Individual specialist agents
- `lib/gamification.js` - XP, levels, achievements
- `lib/database.js` - SQLite persistence

### 3. You Get Notified (Workspace → Telegram)

**Immediate notification (when agent completes):**
```
✅ Agent session completed

📋 Repository: beta-appcaire
🔀 PR: https://github.com/.../pull/456
⏰ Time: 23:47
```

**Morning briefing (8:00 AM daily):**
```
☀️ Good morning!

🤖 Last night's agent activity:
• Fixed scheduling overlap bug
• Created PR #456 (draft)

🎯 Today's Priority #1: Mobile app navigation
📥 Inbox: 3 items need triage

What's on your mind today?
```

**Weekly review (Monday 8:00 AM):**
```
📊 Week 6 Review

Sessions: 5 | PRs merged: 3 | Blockers: 0

Highlights:
• Scheduling bug fixed
• Mobile navigation improved
• Dashboard redesigned

What were your wins this week?
What should we focus on next?
```

---

## Integration Points

### OpenClaw MCP Bridge (`apps/openclaw-bridge`)

**Purpose:** Exposes workspace as tools that OpenClaw can call.

**Tools available:**
| Tool | Function |
|------|----------|
| `get_overview` | Full workspace summary |
| `get_inbox` | List inbox items |
| `add_to_inbox` | Add task to inbox |
| `get_priorities` | Show priorities list |
| `get_tasks` | Show active tasks |
| `get_agent_status` | Latest session report |
| `get_checkin` | Read daily/weekly/monthly check-in |
| `add_checkin_notes` | Add notes to today's check-in |
| `get_follow_ups` | Show follow-up items |
| `add_follow_up` | Add follow-up |
| `get_memory` | Read decisions/learnings/context |
| **`trigger_agent`** | Start agent immediately |

**Configuration:** `~/.openclaw/openclaw.json`
```json
{
  "mcpServers": {
    "agent-workspace": {
      "command": "npx",
      "args": ["tsx", "/path/to/openclaw-bridge/src/index.ts"],
      "env": {
        "WORKSPACE_REPO": "beta-appcaire",
        "WORKSPACE_CONFIG": "/path/to/config/repos.yaml"
      }
    }
  }
}
```

### Notification Scripts (`scripts/notifications/`)

**session-complete.sh:**
- Called at end of `auto-compound.sh`
- Sends Telegram message when agent finishes
- Parameters: repo name, status, PR URL

**morning-briefing.sh:**
- Scheduled via launchd (8:00 AM daily)
- Reads workspace state
- Summarizes last night's activity
- Shows today's priority and inbox count

**weekly-review.sh:**
- Scheduled via launchd (Monday 8:00 AM)
- Weekly summary with highlights
- Prompts for reflection

### LaunchD Jobs

**Active jobs:**
```bash
com.appcaire.agent-server          # Dashboard server (port 3030)
com.appcaire.auto-compound         # Nightly automation (11:00 PM)
com.appcaire.daily-compound-review # Learning extraction (10:30 PM)
com.appcaire.morning-briefing      # Morning summary (8:00 AM)
com.appcaire.weekly-review         # Monday review (8:00 AM)
com.appcaire.caffeinate            # Keep Mac awake
```

**Check status:**
```bash
launchctl list | grep appcaire
```

### Dashboard UI (`apps/dashboard`)

**Unified React SPA at http://localhost:3030**

**Navigation structure:**
```
├─ 📊 Workspace (overview, priorities, trigger button)
├─ 🤖 Teams
│   ├─ Teams overview
│   ├─ Management (CEO dashboard + leaderboard)
│   ├─ Marketing (campaigns, leads)
│   └─ Engineering (job control)
├─ 📋 Operations
│   ├─ Agents (hire/fire, HR management)
│   └─ Tasks (Kanban board)
└─ ⚙️ System
    ├─ Analytics (RL dashboard)
    ├─ Docs (markdown viewer)
    └─ Settings (integrations CRUD)
```

**Key features:**
- **Run Agent button** - Trigger with "Now or Tonight?" modal
- **Real-time status** - Shows running agents, sessions, tasks
- **Kanban board** - Drag & drop task status updates
- **Gamification** - Agent XP, levels, leaderboards
- **Team management** - View 23 agents across 3 teams

---

## Setup Instructions

### Prerequisites

- Mac mini running macOS
- Node.js 22+ installed
- OpenClaw installed and configured
- Telegram bot token and user ID

### Step 1: Initialize Workspace

```bash
cd ~/HomeCare/be-agents-service
./scripts/workspace/init-workspace.sh beta-appcaire
```

This creates workspace structure on iCloud:
```
~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/
├── inbox.md
├── priorities.md
├── tasks.md
├── follow-ups.md
├── check-ins/
│   ├── daily/
│   ├── weekly/
│   └── monthly/
├── memory/
│   ├── decisions.md
│   ├── learnings.md
│   └── context.md
└── agent-reports/
```

### Step 2: Configure OpenClaw

```bash
# Edit OpenClaw config
vim ~/.openclaw/openclaw.json
```

Add MCP server configuration:
```json
{
  "mcpServers": {
    "agent-workspace": {
      "command": "npx",
      "args": [
        "tsx",
        "/Users/be-agent-service/HomeCare/be-agents-service/apps/openclaw-bridge/src/index.ts"
      ],
      "env": {
        "WORKSPACE_REPO": "beta-appcaire",
        "WORKSPACE_CONFIG": "/Users/be-agent-service/HomeCare/be-agents-service/config/repos.yaml"
      }
    }
  },
  "channels": {
    "telegram": {
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": [YOUR_USER_ID]
    }
  }
}
```

### Step 3: Set Environment Variables

```bash
# Create env file
mkdir -p ~/.config/caire
cat > ~/.config/caire/env << 'ENVEOF'
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-user-id"
export ANTHROPIC_API_KEY="your-api-key"
export GITHUB_TOKEN="your-github-token"
ENVEOF
chmod 600 ~/.config/caire/env
```

### Step 4: Load LaunchD Jobs

```bash
cd ~/HomeCare/be-agents-service

# Copy plists
cp launchd/*.plist ~/Library/LaunchAgents/

# Load jobs
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.appcaire.morning-briefing.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.appcaire.weekly-review.plist

# Verify
launchctl list | grep appcaire
```

### Step 5: Restart OpenClaw

```bash
openclaw restart
```

### Step 6: Test the Loop

**In Telegram:**
```
You: "status"
Darwin: [Shows workspace overview]

You: "add to inbox: test the integration"
Darwin: "✅ Added to inbox"

You: "what's in my inbox?"
Darwin: "📥 Inbox (1 pending): test the integration"

You: "add priority: test agent trigger"
Darwin: "✅ Added. Run now or wait for tonight?"

You: "run now"
Darwin: "✅ Agent triggered for beta-appcaire!"
```

**Check dashboard:**
```bash
open http://localhost:3030
```

**Wait for completion notification:**
```
✅ Agent session completed
📋 Repository: beta-appcaire
🔀 PR: https://github.com/.../pull/X
```

---

## Troubleshooting

### OpenClaw not responding

```bash
# Check OpenClaw status
openclaw gateway status

# View logs
openclaw logs

# Restart
openclaw restart
```

### Notifications not sending

```bash
# Check env vars
cat ~/.config/caire/env

# Test notification script directly
./scripts/notifications/morning-briefing.sh beta-appcaire

# Check Telegram bot token
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### Workspace not found

```bash
# Verify workspace exists
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/

# Check config
cat ~/HomeCare/be-agents-service/config/repos.yaml | grep workspace

# Reinitialize if needed
./scripts/workspace/init-workspace.sh beta-appcaire
```

### Dashboard not loading

```bash
# Check server status
curl http://localhost:3030/health

# Rebuild dashboard
cd ~/HomeCare/be-agents-service
yarn build:unified

# Restart server
launchctl bootout gui/$(id -u)/com.appcaire.agent-server
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

### Agent not triggering

```bash
# Check agent service logs
tail -f ~/Library/Logs/agent-server.log

# Check workspace priorities
cat ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/priorities.md

# Trigger manually via API
curl -X POST http://localhost:3030/api/agents/trigger/beta-appcaire \
  -H "Content-Type: application/json" \
  -d '{"workflow": "compound"}'
```

---

## Key Files

### Configuration
- `config/repos.yaml` - Repository and workspace paths
- `config/openclaw/openclaw.json` - OpenClaw configuration template
- `config/openclaw/system-prompt.md` - OpenClaw personality and instructions
- `~/.openclaw/openclaw.json` - User's OpenClaw config (on Mac mini)
- `~/.config/caire/env` - Environment variables

### Scripts
- `scripts/compound/auto-compound.sh` - Main automation workflow
- `scripts/compound/loop.sh` - Task execution loop
- `scripts/workspace/init-workspace.sh` - Initialize workspace structure
- `scripts/workspace/sync-to-workspace.sh` - Sync results to workspace
- `scripts/notifications/session-complete.sh` - Completion notification
- `scripts/notifications/morning-briefing.sh` - Daily summary
- `scripts/notifications/weekly-review.sh` - Weekly review

### Dashboard
- `apps/dashboard/src/App.tsx` - Main React app
- `apps/dashboard/src/components/Layout.tsx` - Navigation structure
- `apps/dashboard/src/components/WorkspaceOverview.tsx` - Workspace view with trigger button
- `apps/dashboard/src/pages/` - All page components

### OpenClaw Bridge
- `apps/openclaw-bridge/src/index.ts` - MCP server entry
- `apps/openclaw-bridge/src/tools.ts` - All workspace tools (12 tools)
- `apps/openclaw-bridge/src/workspace-bridge.ts` - Workspace path resolver

### Database
- `.compound-state/agent-service.db` - SQLite database
- `lib/database.js` - Database operations
- `lib/gamification.js` - XP, levels, achievements

---

## Architecture Decisions

### Why Markdown Files?

- **Human-readable** - You can edit with any text editor
- **Git-friendly** - Easy to version control and diff
- **AI-native** - LLMs handle markdown naturally
- **Portable** - Works on iCloud, GitHub, anywhere
- **No database lock-in** - Simple flat files

### Why OpenClaw?

- **Multi-channel** - Telegram
- **MCP support** - Extensible with tools
- **Conversational** - Natural language interface
- **Daemon mode** - Runs 24/7 on Mac mini
- **Production-ready** - Used by real companies

### Why LaunchD?

- **Native macOS** - No cron, no systemd
- **Reliable** - Restarts on crash
- **Scheduled tasks** - Calendar-based timing
- **Environment control** - Proper PATH and env vars

### Why SQLite?

- **Serverless** - No database daemon
- **Fast** - Embedded, local
- **Reliable** - ACID transactions
- **Simple** - One file, easy backup
- **Portable** - Works everywhere

---

## Success Criteria

✅ **Bi-directional communication working**
- You → Telegram → OpenClaw → Workspace ✓
- Workspace → OpenClaw → Telegram → You ✓

✅ **Agent orchestration working**
- Reads priorities from workspace ✓
- Orchestrates specialist teams ✓
- Creates PRs automatically ✓
- Tracks gamification (XP, levels) ✓

✅ **Notifications working**
- Session complete ✓
- Morning briefing (8 AM) ✓
- Weekly review (Monday 8 AM) ✓

✅ **Dashboard working**
- Workspace overview ✓
- Trigger agent button ✓
- Kanban board ✓
- Team management ✓
- Analytics ✓

✅ **Closed loop complete**
- Human → AI → Agent Service → AI → Human ✓

---

## Related Documentation

- `CLAUDE.md` - Service overview and learnings
- `docs/WORKSPACE.md` - Workspace structure and usage
- `docs-archive/DASHBOARD_MIGRATION.md` - Dashboard migration (archived)
- `docs/API_ENDPOINTS.md` - Complete API reference
- `config/openclaw/README.md` - OpenClaw setup guide
- `config/openclaw/SIMPLE_SETUP.md` - Quick 2-step integration

---

**Last Updated:** 2026-02-09
**Status:** ✅ Production Ready
