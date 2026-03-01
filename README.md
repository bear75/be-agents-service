# BE Agent Service

Multi-agent autonomous service for software development and marketing automation.

## Quick Start

```bash
# Start the dashboard (API + UI on port 3010)
yarn start
# or with hot reload:
yarn dev

# Verify dashboard + OpenClaw + Telegram + launchd setup
./scripts/verify-all-services.sh --send-telegram-test

# macOS only: (re)load all launchd services + run verification
./scripts/start-all-services.sh --send-telegram-test
```

**Dashboard:** http://localhost:3010

## What This Repo Does

- **Dashboard (port 3010):** Web UI for workspace, repos, plans, agents, logs
- **Agent orchestration:** 27 agents across 4 teams (engineering, marketing, management, schedule-optimization)
- **Compound automation:** Nightly learnings (10:30 PM), auto-implement (11:00 PM)

## How the agent service runs: Telegram + compound learning

The agent service uses **Telegram** as the primary human interface and **compound learning** for continuous improvement. **There can only be one shared folder:** Cursor, compound, and Telegram must all use the same iCloud/AgentWorkspace path; if OpenClaw uses a different path, you get two folders and split state. Data lives in three places:

| Where | What it holds |
|-------|----------------|
| **This repo** (`be-agents-service`) | Code, config (`config/repos.yaml`, `config/openclaw/`), agents, scripts, docs. Read by the service; you edit here. |
| **`.compound-state/`** (inside this repo) | Session state (JSON per run), SQLite DB (`agent-service.db`), marketing/data JSON. Written by the service only. |
| **iCloud/AgentWorkspace/** | Shared markdown workspace. **darwin** is the name for the Telegram agent, the folder `AgentWorkspace/DARWIN/`, and the dashboard workspace — not a code repo. That folder holds `inbox.md`, `priorities.md`, `tasks.md`, `check-ins/`, `memory/`, `agent-reports/`. You and agents read/write here; compound scripts read priorities and write reports. |

- **Telegram:** Add to inbox, get session summaries, morning briefing (8 AM), weekly review. Configure via OpenClaw: [config/openclaw/README.md](config/openclaw/README.md).
- **Compound learning:** At **10:30 PM** `daily-compound-review.sh` extracts learnings from Claude threads and updates repo docs. At **11:00 PM** `auto-compound.sh` reads priority #1 from the repo’s workspace (e.g. `AgentWorkspace/beta-appcaire/priorities.md`), implements it, and creates a PR. No direct push to main.

See [docs/AGENT_WORKSPACE_STRUCTURE.md](docs/AGENT_WORKSPACE_STRUCTURE.md) for the full read/write contract and [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) for the full folder and file list.

## Overview

**Four agent teams (27 agents total):**
- **Engineering (10):** Orchestrator, Backend, Frontend, Infrastructure, Verification, Senior Reviewer, DB Architect, UX Designer, Documentation Expert, Agent Levelup
- **Marketing (10):** Jarvis, Shuri, Fury, Vision, Loki, Quill, Wanda, Pepper, Friday, Wong
- **Management (5):** CEO, CPO/CTO, CMO/CSO, HR Agent Lead, Interface Agent
- **Schedule optimization (2):** Timefold Specialist, Optimization Mathematician

**Human–agent interface:**
- **Telegram (primary):** Inbox, session summaries, morning briefing, weekly review
- **Dashboard:** http://localhost:3010 — workspace, plans, agents, logs

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

## Start, stop, restart: gateways and dashboards

All commands from repo root: `~/HomeCare/be-agents-service`.

### Gateways (OpenClaw)

Use **profile-specific** commands so Darwin and Hannes don’t affect each other. Do **not** use generic `openclaw gateway restart` in dual-stack mode.

| Action | Darwin | Hannes |
|--------|--------|--------|
| Start | `./scripts/openclaw/manage-gateway-launchd.sh darwin start` | `./scripts/openclaw/manage-gateway-launchd.sh hannes start` |
| Stop | `./scripts/openclaw/manage-gateway-launchd.sh darwin stop` | `./scripts/openclaw/manage-gateway-launchd.sh hannes stop` |
| Restart | `./scripts/openclaw/manage-gateway-launchd.sh darwin restart` | `./scripts/openclaw/manage-gateway-launchd.sh hannes restart` |
| Status | `./scripts/openclaw/manage-gateway-launchd.sh darwin status` | `./scripts/openclaw/manage-gateway-launchd.sh hannes status` |

Install both gateways once: `./scripts/openclaw/setup-dual-launchd.sh`

### Main dashboard (Darwin, port 3010)

| Action | Command |
|--------|--------|
| Start (foreground) | `yarn start` |
| Restart (kill + build + start) | `./scripts/restart-darwin.sh` or `yarn restart` |
| Via launchd: stop | `launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist` |
| Via launchd: start | `launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist` |

### Hannes dashboard (isolated, port 3011)

| Action | Command |
|--------|--------|
| Start (foreground) | `./scripts/start-hannes-dashboard.sh` |
| Restart | `./scripts/restart-hannes-dashboard.sh` |
| Via launchd | `./scripts/manage-hannes-dashboard-launchd.sh start \| stop \| restart \| status` |

### Start everything (Darwin stack)

```bash
./scripts/start-all-services.sh
# optional: ./scripts/start-all-services.sh --send-telegram-test
```

See [docs/HANNES_ISOLATED_STACK.md](docs/HANNES_ISOLATED_STACK.md) for the full Hannes setup.

## Documentation

**All docs live in `docs/`.** Start with [docs/README.md](docs/README.md) for the full index.

| Need | Doc |
|------|-----|
| **Closed-loop integration** | [docs/CLOSED_LOOP_INTEGRATION.md](docs/CLOSED_LOOP_INTEGRATION.md) ⭐ |
| **Workspace setup** | [docs/WORKSPACE.md](docs/WORKSPACE.md) |
| Quick commands | [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) — start commands, schedules |
| Mac mini setup | [docs/FRESH_MAC_MINI_SETUP.md](docs/FRESH_MAC_MINI_SETUP.md) |
| Mac mini recovery | [docs/MAC_MINI_RECOVERY.md](docs/MAC_MINI_RECOVERY.md) |
| OpenClaw (workspace + migration) | [config/openclaw/README.md](config/openclaw/README.md) |
| **API keys (env)** | [config/caire/README.md](config/caire/README.md) — `~/.config/caire/env` from [config/caire/env.example](config/caire/env.example) |
| **Auto-deploy main → Mac mini** | [docs/AUTO_DEPLOY_MAIN_MAC_MINI.md](docs/AUTO_DEPLOY_MAIN_MAC_MINI.md) |
| Agent folders & read/write contract | [docs/AGENT_WORKSPACE_STRUCTURE.md](docs/AGENT_WORKSPACE_STRUCTURE.md) |
| Folder structure (repo, .compound-state, AgentWorkspace) | [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) |
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Data flow | [docs/DATA_FLOW.md](docs/DATA_FLOW.md) |
| Database access | [docs/DATABASE_ACCESS.md](docs/DATABASE_ACCESS.md) |
| API reference | [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md) |
| Agents & teams (DB vs disk) | [docs/AGENTS_AND_TEAMS_DATA.md](docs/AGENTS_AND_TEAMS_DATA.md) |

## Run latest agent code on the Mac mini

On the Mac mini (where agents and OpenClaw run):

1. **Pull latest main**
   ```bash
   cd ~/HomeCare/be-agents-service
   git checkout main && git pull origin main
   ```

2. **If you changed server code** (`apps/server/`):
   ```bash
   cd apps/server && yarn build
   ```
   If the dashboard is run via launchd, unload/reload the server plist so it uses the new build.

3. **If you changed launchd plists** (`launchd/*.plist`):
   ```bash
   cp launchd/*.plist ~/Library/LaunchAgents/
   launchctl unload ~/Library/LaunchAgents/com.appcaire.<job>.plist
   launchctl load ~/Library/LaunchAgents/com.appcaire.<job>.plist
   ```
   Repeat for each plist you changed (e.g. `com.appcaire.auto-compound`, `com.appcaire.daily-compound-review`, `com.appcaire.dashboard`).

4. **If you only changed scripts or config** (e.g. `config/repos.yaml`, `scripts/`, `config/openclaw/`):
   No restart needed — scripts and config are read on each run.

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
│   ├── verification-specialist.sh   # Engineering: Quality gate
│   ├── timefold-specialist.sh       # Schedule optimization: FSR jobs, metrics
│   └── ... (see agents/prompts/README.md for all 27 agents)
├── scripts/
│   ├── compound/                    # Auto-compound, daily review, loop (see docs/AGENT_WORKSPACE_STRUCTURE.md)
│   │   ├── auto-compound.sh         # 11:00 PM - Auto-implement
│   │   ├── daily-compound-review.sh # 10:30 PM - Extract learnings
│   │   ├── loop.sh                  # Task execution loop
│   │   ├── analyze-report.sh        # Parse priorities report
│   │   ├── check-status.sh          # Status monitoring
│   │   └── test-safety.sh           # Safety mechanism tests
│   ├── workspace/                   # init, sync, process-inbox
│   ├── notifications/
│   ├── orchestrator.sh              # Multi-repo coordinator
│   ├── db-api.sh                    # DB API helper (sourced by compound)
│   └── openclaw-migrate-workspace.sh
├── lib/
│   ├── state-manager.sh             # JSON state coordination
│   ├── feedback-schema.json         # Agent communication schema
│   └── parallel-executor.sh         # Parallel agent spawning
├── apps/
│   ├── server/                      # Unified server (port 3010): API + static in public/
│   └── dashboard/                   # React workspace UI (build → server/public)
├── launchd/
│   ├── com.appcaire.auto-compound.plist
│   ├── com.appcaire.caffeinate.plist
│   ├── com.appcaire.daily-compound-review.plist
│   └── com.appcaire.dashboard.plist
├── .compound-state/                 # Session state (JSON), SQLite agent-service.db; service write-only
├── data/                            # Deprecated — use .compound-state (see data/README.md)
├── docs/                            # All documentation
├── config/
│   ├── repos.yaml                   # Multi-repo config
│   └── openclaw/                    # OpenClaw template (Mac mini shared folder + Telegram)
│       ├── openclaw.json            # Copy to ~/.openclaw/openclaw.json
│       └── README.md                # Workspace path + migration steps
└── scripts/openclaw-migrate-workspace.sh  # One-time: default workspace → shared folder
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
./scripts/compound/daily-compound-review.sh

# Run auto-compound manually
./scripts/compound/auto-compound.sh
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
# Start dashboard (from repo root)
cd ~/HomeCare/be-agents-service
yarn start
# or: yarn dev  (with hot reload)

# Auto-starts on boot via LaunchAgent (com.appcaire.dashboard)
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
../be-agents-service/scripts/compound/daily-compound-review.sh

# Run auto-compound
cd ~/HomeCare/beta-appcaire
../be-agents-service/scripts/compound/auto-compound.sh

# Run orchestrator manually
cd ~/HomeCare/be-agents-service
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-07.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/test-branch

# Check status
../be-agents-service/scripts/compound/check-status.sh

# Test safety mechanisms
../be-agents-service/scripts/compound/test-safety.sh
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

### Priority Reports – var agenterna plockar upp jobb

**Auto-compound (23:00)** läser prioriteringar i denna ordning:

1. **Workspace (först):** `AgentWorkspace/DARWIN/priorities.md` (iCloud).
2. **Fallback – repo:** Om repo har **priorities_dir** i `config/repos.yaml` används den katalogen, annars **reports/** i repo-roten (nyaste `*.md`).

**För att agenterna ska plocka upp jobb:**

| Repo | Plats för prio |
|------|-----------------|
| **appcaire** (caire-platform/appcaire, FSR/Timefold) | **`appcaire/docs_2.0/recurring-visits/huddinge-package/*.md`** (priorities_dir i config). Lägg t.ex. `priorities-2026-02-28.md` där. |
| **beta-appcaire** | `beta-appcaire/reports/*.md` (filer direkt i `reports/`) eller workspace `priorities.md`. |

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
./scripts/compound/daily-compound-review.sh --dry-run

# Test auto-compound (dry run)
./scripts/compound/auto-compound.sh --dry-run

# Run safety tests
./scripts/compound/test-safety.sh
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
