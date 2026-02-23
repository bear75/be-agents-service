# BE Agent Service

Multi-agent autonomous service for software development and marketing automation with closed-loop WhatsApp/Telegram integration.

## Quick Start

```bash
# Start the dashboard (API + UI on port 3010)
yarn start
# or with hot reload:
yarn dev

# Start OpenClaw gateway (WhatsApp + Telegram)
openclaw gateway start      # Foreground (or use restart if launchd is configured)
openclaw gateway restart    # Restart via launchd (when plist is loaded)
openclaw gateway status     # Check if running
```

**Dashboard:** http://localhost:3010  
**OpenClaw gateway:** Port 18789 (receives WhatsApp/Telegram → routes to agents)

> **Note:** If chats stop responding, the OpenClaw daemon (`com.appcaire.openclaw`) may be conflicting with the gateway. Stop it: `launchctl bootout gui/501/com.appcaire.openclaw` and start the gateway via launchd instead.

## What This Repo Does

- **Dashboard (port 3010):** Web UI for workspace, repos, plans, agents, logs
- **OpenClaw integration:** WhatsApp/Telegram → shared workspace → agents
- **Agent orchestration:** 23 specialists (engineering, marketing, management)
- **Compound automation:** Nightly learnings (10:30 PM), auto-implement (11:00 PM)

## Overview

**Three agent teams (23 agents total):**
- **Engineering (9 specialists):** Backend, Frontend, Infrastructure, Verification, DB Architect, UX Designer, Documentation Expert, Agent Levelup, Orchestrator
- **Marketing (10 Marvel agents):** Jarvis, Shuri, Fury, Vision, Loki, Quill, Wanda, Pepper, Friday, Wong
- **Management (4 executives):** CEO, CPO/CTO, CMO/CSO, HR Agent Lead

**Human-AI Interface:**
- **WhatsApp/Telegram** → OpenClaw → Shared Workspace → Agent Service → Notifications back to you
- **Dashboard:** http://localhost:3010

**Automation:**
- **Nightly:** 10:30 PM learnings extraction, 11:00 PM auto-implementation
- **On-demand:** Trigger via Telegram or dashboard
- **Notifications:** Session complete, morning briefing (8 AM), weekly review (Monday 8 AM)

## Unified Dashboard (port 3010)

Single entry point at **http://localhost:3010**:

| URL | Content |
|-----|---------|
| `/` | React workspace UI (repo selector, workspace, plans, agents, logs) |

**How to run:**
```bash
yarn start          # Build + start (single server on 3010)
yarn dev            # Build + dev with hot reload
```

**Architecture:** One Express server (`apps/server`) on port 3010 serves API + static. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

**All docs live in `docs/`.** Start with [docs/README.md](docs/README.md) for the full index.

| Need | Doc |
|------|-----|
| **Closed-loop integration** | [docs/CLOSED_LOOP_INTEGRATION.md](docs/CLOSED_LOOP_INTEGRATION.md) ⭐ |
| **Workspace setup** | [docs/WORKSPACE.md](docs/WORKSPACE.md) |
| **OpenClaw setup** | [config/openclaw/SIMPLE_SETUP.md](config/openclaw/SIMPLE_SETUP.md), [docs/SANDBOX_SETUP.md](docs/SANDBOX_SETUP.md) |
| Quick commands | [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) — start commands, schedules |
| Mac mini setup | [docs/FRESH_MAC_MINI_SETUP.md](docs/FRESH_MAC_MINI_SETUP.md) |
| Mac mini recovery | [docs/MAC_MINI_RECOVERY.md](docs/MAC_MINI_RECOVERY.md) |
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Data flow | [docs/DATA_FLOW.md](docs/DATA_FLOW.md) |
| Database access | [docs/DATABASE_ACCESS.md](docs/DATABASE_ACCESS.md) |
| API reference | [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md) |

## Repository Structure

```
be-agents-service/
├── agents/
│   ├── marketing/                   # Marketing agent team (10 Marvel characters)
│   │   ├── jarvis-orchestrator.sh   # Squad lead
│   │   ├── vision-seo-analyst.sh    # SEO specialist
│   │   └── ... (8 more agents)
│   ├── backend-specialist.sh        # Engineering: Database, GraphQL, resolvers
│   ├── frontend-specialist.sh       # Engineering: UI, codegen, operations
│   ├── infrastructure-specialist.sh # Engineering: Packages, configs, docs
│   └── verification-specialist.sh   # Engineering: Quality gate
├── scripts/
│   ├── orchestrator.sh              # Multi-repo coordinator
│   ├── daily-compound-review.sh     # 10:30 PM - Extract learnings
│   ├── auto-compound.sh             # 11:00 PM - Auto-implement
│   ├── loop.sh                      # Task execution loop
│   ├── analyze-report.sh            # Parse priorities report
│   ├── check-status.sh              # Status monitoring
│   └── test-safety.sh               # Safety mechanism tests
├── lib/
│   ├── state-manager.sh             # JSON state coordination
│   ├── feedback-schema.json         # Agent communication schema
│   └── parallel-executor.sh         # Parallel agent spawning
├── apps/
│   ├── server/                      # Unified server (port 3010): API + static in public/
│   └── dashboard/                   # React workspace UI (build → server/public)
├── scripts/
│   └── start-dashboard.sh           # LaunchD: yarn workspace server start
├── launchd/
│   ├── com.appcaire.auto-compound.plist
│   ├── com.appcaire.caffeinate.plist
│   ├── com.appcaire.daily-compound-review.plist
│   └── com.appcaire.dashboard.plist
├── .compound-state/                 # Agent session states (JSON)
├── data/                            # SQLite database
├── docs/                            # All documentation
└── config/repos.yaml                # Multi-repo config
```

## Installation

### 1. Clone Repository

```bash
cd ~/HomeCare
git clone https://github.com/bear75/be-agents-service.git
cd be-agents-service
```

### 2. Configure LaunchAgents

```bash
# Copy plist files to LaunchAgents directory
cp launchd/*.plist ~/Library/LaunchAgents/

# Load the agents
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
```

### 3. Configure Paths

Edit plist files to update paths:
```bash
# Update WorkingDirectory and ProgramArguments paths
vim ~/Library/LaunchAgents/com.appcaire.*.plist
```

### 4. Test Installation

```bash
# Run daily review manually
./scripts/daily-compound-review.sh

# Run auto-compound manually
./scripts/auto-compound.sh
```

## Schedules

| Script | Schedule | Purpose |
|--------|----------|---------|
| daily-compound-review.sh | 10:30 PM daily | Extract learnings from Claude threads |
| auto-compound.sh | 11:00 PM daily | Auto-implement priority #1 task |
| caffeinate | Always | Keep Mac awake for automation |

## Safety Mechanisms

### 1. Branch Check
✅ Must be on `main` branch before starting

### 2. Auto-Stash
✅ Automatically stashes uncommitted work

### 3. PR Creation
✅ Creates PR instead of direct main push

### 4. Safety Commit
✅ Auto-commits if Claude forgets

### 5. Error Handling
✅ Stops on errors, logs failures

## Dashboard

**Real-time monitoring at http://localhost:3010**

```bash
# Start dashboard
cd ~/HomeCare/be-agents-service
./dashboard/start.sh

# Auto-starts on boot via LaunchAgent
```

Features:
- Live session monitoring (3s refresh)
- Agent status tracking
- Session logs viewer
- System statistics
- Command center (all commands in one place)
- Documentation browser

## Usage

### Engineering Agents (Automatic)

```bash
# Run daily review
cd ~/HomeCare/beta-appcaire
../be-agents-service/scripts/daily-compound-review.sh

# Run auto-compound
cd ~/HomeCare/beta-appcaire
../be-agents-service/scripts/auto-compound.sh

# Run orchestrator manually
cd ~/HomeCare/be-agents-service
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-07.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/test-branch

# Check status
../be-agents-service/scripts/check-status.sh

# Test safety mechanisms
../be-agents-service/scripts/test-safety.sh
```

### Marketing Agents (Manual)

```bash
# Create marketing priority
cat > ~/HomeCare/beta-appcaire/reports/marketing-blog.md <<EOF
# Priority: SEO Blog Post
**Description:** Create SEO-optimized blog about employee scheduling
**Expected outcome:**
- Keyword research
- Blog post written (1500+ words)
- Header image created
- Published to website
- Promoted on social media
EOF

# Run Jarvis marketing orchestrator
cd ~/HomeCare/be-agents-service
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-blog.md \
  ~/HomeCare/beta-appcaire/tasks/marketing-prd.json \
  feature/blog-post-scheduling

# Run individual marketing agent
./agents/marketing/vision-seo-analyst.sh \
  "session-test-$(date +%s)" \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-blog.md
```

### Scheduled Execution

LaunchAgents handle automatic execution:

```bash
# Check if agents are loaded
launchctl list | grep appcaire

# View logs
tail -f ~/Library/Logs/appcaire-compound.log
tail -f ~/Library/Logs/appcaire-daily-review.log

# Manually trigger
launchctl start com.appcaire.auto-compound
launchctl start com.appcaire.daily-compound-review
```

## Configuration

### Repository Location

The service expects beta-appcaire at:
```
~/HomeCare/beta-appcaire
```

Update plist files if location differs.

### Priority Reports

Daily priorities should be in:
```
~/HomeCare/beta-appcaire/reports/priorities-YYYY-MM-DD.md
```

Format:
```markdown
# Priority 1

**Description:** Clear task description
**Expected outcome:** What should be achieved
**Files:** Relevant file paths
```

## Logs

Logs are stored in:
```
~/Library/Logs/appcaire-compound.log
~/Library/Logs/appcaire-daily-review.log
```

View recent logs:
```bash
tail -f ~/Library/Logs/appcaire-*.log
```

## Troubleshooting

### WhatsApp/Telegram Chats Not Responding

The gateway may be in a crash loop if the OpenClaw daemon conflicts with it:

```bash
# Stop the daemon (stops killing the gateway)
launchctl bootout gui/501/com.appcaire.openclaw

# Start the gateway via launchd
launchctl bootstrap gui/501 ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# Verify it's running
lsof -i :18789
tail -20 ~/.openclaw/logs/gateway.log
```

### Agent Not Running

```bash
# Check if loaded
launchctl list | grep appcaire

# Reload if needed
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

### Wrong Branch Error

```bash
# Ensure on main branch
cd ~/HomeCare/beta-appcaire
git checkout main
git pull origin main
```

### Permission Errors

```bash
# Make scripts executable
chmod +x ~/HomeCare/be-agents-service/scripts/*.sh
```

## Development

### Testing Scripts

```bash
# Test daily review (dry run)
./scripts/daily-compound-review.sh --dry-run

# Test auto-compound (dry run)
./scripts/auto-compound.sh --dry-run

# Run safety tests
./scripts/test-safety.sh
```

### Modifying Schedules

Edit plist files:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>22</integer>  <!-- 10 PM -->
    <key>Minute</key>
    <integer>30</integer>
</dict>
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Mac Mini (Agent Host)                  │
│                                         │
│  LaunchAgent (10:30 PM)                │
│         ↓                               │
│  daily-compound-review.sh              │
│         ↓                               │
│  Reviews Claude threads                │
│  Updates CLAUDE.md files               │
│  Commits to main                        │
│                                         │
│  LaunchAgent (11:00 PM)                │
│         ↓                               │
│  auto-compound.sh                      │
│         ↓                               │
│  analyze-report.sh                     │
│         ↓                               │
│  loop.sh (Claude Code API)            │
│         ↓                               │
│  Creates feature branch                │
│  Implements task                        │
│  Creates PR                             │
│                                         │
└─────────────────────────────────────────┘
                 ↓
         GitHub Pull Request
                 ↓
         Human Review & Merge
```

## Related Repositories

- **beta-appcaire**: Main application repository
  - https://github.com/[org]/beta-appcaire

## License

Private - Internal use only

## Contact

Issues: https://github.com/bear75/be-agents-service/issues
