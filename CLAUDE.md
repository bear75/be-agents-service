# CLAUDE.md - Agent Service

Last updated: 2026-02-03
Times updated: 1

This file contains learnings about the agent automation service that orchestrates Claude Code agents across multiple repositories.

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Configuration](#configuration)
5. [Common Workflows](#common-workflows)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Common Mistakes](#common-mistakes)

---

## Service Overview

### Purpose

The agent service orchestrates Claude Code automation workflows across multiple repositories. It provides:

- **Centralized Scripts**: Config-driven automation scripts that work across repos
- **API Server**: REST API for monitoring and controlling agents (port 4010)
- **Web Dashboard**: Real-time UI for agent status and logs (port 3010)
- **Scheduled Automation**: LaunchD integration for nightly workflows

### Key Principle: Separation of Concerns

**Scripts live here** (be-agents-service)
**Data lives there** (target repositories)

- Priorities defined in target repo's `reports/` directory
- Logs written to target repo's `logs/` directory
- Scripts read configuration from `config/repos.yaml`
- No data duplication - target repos are source of truth

---

## Architecture

```
be-agents-service/
├── apps/
│   ├── server/         # API server (port 4010)
│   │   ├── src/
│   │   │   ├── routes/ # REST endpoints
│   │   │   ├── lib/    # Configuration & file readers
│   │   │   └── types/  # TypeScript types
│   │   └── dist/       # Built server (for launchd)
│   │
│   └── dashboard/      # Web UI (port 3010)
│       └── src/
│           ├── components/ # React components
│           ├── pages/      # Dashboard pages
│           └── lib/        # API client
│
├── agents/              # Engineering specialist scripts (orchestrator spawns)
│   ├── backend-specialist.sh
│   ├── frontend-specialist.sh
│   ├── infrastructure-specialist.sh
│   ├── verification-specialist.sh
│   ├── senior-code-reviewer.sh
│   ├── db-architect-specialist.sh
│   ├── ux-designer-specialist.sh
│   ├── documentation-expert.sh
│   ├── levelup-specialist.sh
│   └── marketing/       # Marketing team agents
│
├── scripts/
│   └── compound/       # Agent automation scripts
│       ├── auto-compound.sh              # Main automation
│       ├── daily-compound-review.sh      # Learning extraction
│       ├── loop.sh                       # Task execution
│       ├── analyze-report.sh             # Priority parsing
│       └── check-status.sh               # Status monitoring
│
├── config/
│   └── repos.yaml      # Multi-repo configuration
│
├── data/
│   └── state/          # Runtime state (future use)
│
├── launchd/            # macOS scheduled jobs
│   ├── com.appcaire.agent-server.plist          # Keep server running
│   ├── com.appcaire.auto-compound.plist         # 11:00 PM automation
│   ├── com.appcaire.daily-compound-review.plist # 10:30 PM review
│   └── com.appcaire.caffeinate.plist            # Keep Mac awake
│
└── docs/               # Documentation
    ├── COMPOUND_WORKFLOW.md
    ├── COMPOUND_SETUP_GUIDE.md
    ├── PRODUCTIVITY_SYSTEM.md
    └── QUICK_REFERENCE.md
```

---

## Directory Structure

### apps/server - API Server

**Purpose:** REST API for agent monitoring and control

**Port:** 4010

**Key Files:**
- `src/index.ts` - Express server setup
- `src/routes/repos.ts` - Repository endpoints
- `src/routes/agents.ts` - Agent control endpoints
- `src/lib/config.ts` - YAML configuration loader
- `src/lib/repo-reader.ts` - Read priorities/logs from target repos

**Endpoints:**
```
GET  /health                        - Health check
GET  /api/repos                     - List all configured repos
GET  /api/repos/:name               - Get repo details
GET  /api/repos/:name/status        - Get agent status
GET  /api/repos/:name/priorities    - Read priorities from repo
GET  /api/repos/:name/logs          - Read logs from repo
POST /api/agents/trigger/:name      - Trigger agent run
POST /api/agents/cancel/:name       - Cancel running agent
GET  /api/agents/running            - List running agents
```

### apps/dashboard - Web UI

**Purpose:** Web interface for agent monitoring

**Port:** 3010

**Key Components:**
- `DashboardPage.tsx` - Main dashboard layout
- `AgentStatusCard.tsx` - Agent status display
- `PriorityBoard.tsx` - Priority viewer
- `LogViewer.tsx` - Log streaming
- `RepoSelector.tsx` - Repository switcher

**Tech Stack:**
- React 19 + TypeScript
- Vite (dev server + build tool)
- Tailwind CSS 3
- Lucide React (icons)

### scripts/compound - Automation Scripts

**auto-compound.sh**
- Main automation pipeline
- Runs at 11:00 PM via launchd
- Picks priority #1 from target repo
- Creates feature branch and implements
- Creates PR (never pushes to main)
- **Usage:** `./auto-compound.sh <repo-name>`

**daily-compound-review.sh**
- Learning extraction workflow
- Runs at 10:30 PM via launchd
- Reviews Claude Code threads from last 24h
- Updates CLAUDE.md files in target repo
- Commits directly to main
- **Usage:** `./daily-compound-review.sh <repo-name>`

**loop.sh**
- Task execution loop
- Called by auto-compound.sh
- Executes tasks from PRD JSON
- Max iterations to prevent infinite loops

**analyze-report.sh**
- Parses priorities markdown file
- Extracts priority #1
- Generates branch name
- Returns JSON for consumption by other scripts

**check-status.sh**
- Manual status check tool
- Shows current branch, uncommitted changes
- Displays recent PRs
- **Usage:** `./check-status.sh <repo-name>`

---

## Configuration

### config/repos.yaml

Multi-repository configuration file:

```yaml
repos:
  repo-name:
    # Absolute path to repository
    path: ~/path/to/repo

    # Schedule for automated runs
    schedule:
      review: "22:30"    # Daily review time
      compound: "23:00"  # Daily automation time

    # Directory paths within repository
    priorities_dir: reports/
    logs_dir: logs/
    tasks_dir: tasks/

    # Enable/disable agent for this repo
    enabled: true

    # GitHub configuration
    github:
      owner: username
      repo: repository
      default_branch: main
```

**Adding a New Repository:**

1. Add entry to `config/repos.yaml`
2. Ensure target repo has `reports/` directory
3. Create initial priorities file: `reports/priorities-YYYY-MM-DD.md`
4. Scripts will automatically work with new repo

**Example:**
```yaml
repos:
  my-new-repo:
    path: ~/projects/my-new-repo
    schedule:
      review: "22:30"
      compound: "23:00"
    priorities_dir: reports/
    logs_dir: logs/
    tasks_dir: tasks/
    enabled: true
    github:
      owner: myusername
      repo: my-new-repo
      default_branch: main
```

---

## Common Workflows

### 1. Manual Agent Trigger

```bash
cd ~/HomeCare/be-agents-service

# Trigger compound workflow for a repo
./scripts/compound/auto-compound.sh beta-appcaire

# Trigger review workflow
./scripts/compound/daily-compound-review.sh beta-appcaire

# Check status
./scripts/compound/check-status.sh beta-appcaire
```

### 2. Update Priorities

Priorities are defined in the **target repository**:

```bash
cd ~/HomeCare/beta-appcaire

# Edit priorities
vim reports/priorities-$(date +%Y-%m-%d).md

# Commit to main
git add reports/
git commit -m "docs: update priorities"
git push origin main
```

**Priority File Format:**
```markdown
# Product Priorities - 2026-02-03

## High Priority

1. First priority item (agent will pick this one)
2. Second priority item
3. Third priority item

## Medium Priority

1. Medium priority item
...
```

### 3. Monitor Agent Activity

**Via Dashboard:**
```bash
# Server should already be running via launchd
open http://localhost:3010
```

**Via API:**
```bash
# Check server health
curl http://localhost:4010/health

# List repositories
curl http://localhost:4010/api/repos

# Get repo status
curl http://localhost:4010/api/repos/beta-appcaire/status

# View priorities
curl http://localhost:4010/api/repos/beta-appcaire/priorities

# View logs
curl http://localhost:4010/api/repos/beta-appcaire/logs?limit=50
```

**Via Logs:**
```bash
# Agent server logs
tail -f ~/Library/Logs/agent-server.log

# Compound automation logs (in target repo)
tail -f ~/HomeCare/beta-appcaire/logs/auto-compound.log
tail -f ~/HomeCare/beta-appcaire/logs/compound-review.log
```

### 4. Review Generated PRs

```bash
cd ~/HomeCare/beta-appcaire

# List PRs
gh pr list

# View specific PR
gh pr view <number>

# Check CI status
gh pr checks <number>

# Merge PR
gh pr merge <number>
```

---

## Deployment

### Prerequisites

- macOS with launchd
- Homebrew installed
- Node.js 20+ (via nvm)
- Yarn 1.22+
- Claude Code CLI installed and configured
- gh CLI authenticated

### Initial Setup

```bash
# Clone repository
cd ~/HomeCare
git clone git@github.com:bear75/be-agents-service.git
cd be-agents-service

# Install dependencies
yarn install

# Build server
cd apps/server
yarn build

# Verify build
ls -la dist/
```

### LaunchD Configuration

```bash
# Copy plist files to LaunchAgents
cp launchd/*.plist ~/Library/LaunchAgents/

# Update paths in plist files if needed
# Verify Node.js path matches your system:
which yarn  # Use this path in agent-server.plist

# Load jobs
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Verify jobs are loaded
launchctl list | grep appcaire
```

### Verify Deployment

```bash
# Check server is running
curl http://localhost:4010/health

# Check dashboard
open http://localhost:3010

# Test script execution
./scripts/compound/check-status.sh beta-appcaire

# View scheduled jobs
launchctl list | grep appcaire
```

### Environment Setup

Create `~/.config/caire/env` for API keys:

```bash
mkdir -p ~/.config/caire
cat > ~/.config/caire/env << 'EOF'
export ANTHROPIC_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"
EOF
chmod 600 ~/.config/caire/env
```

Scripts will source this file automatically.

---

## Troubleshooting

### Server Not Starting

**Symptom:** `launchctl list` shows exit code 78 for agent-server

**Check:**
```bash
# View error logs
tail -f ~/Library/Logs/agent-server-error.log

# Check yarn path in plist
cat ~/Library/LaunchAgents/com.appcaire.agent-server.plist | grep -A 5 ProgramArguments

# Verify Node.js path
which yarn
which node
```

**Fix:** Update plist with correct Node.js/yarn path:
```xml
<key>ProgramArguments</key>
<array>
    <string>/Users/USERNAME/.nvm/versions/node/vXX.XX.X/bin/yarn</string>
    <string>workspace</string>
    <string>server</string>
    <string>start</string>
</array>
```

### Scripts Not Executing

**Symptom:** LaunchD job runs but scripts fail

**Check:**
```bash
# View script logs (in target repo)
tail -f ~/HomeCare/beta-appcaire/logs/auto-compound.log

# Verify PATH in plist
cat ~/Library/LaunchAgents/com.appcaire.auto-compound.plist | grep -A 3 PATH
```

**Common Issues:**
- Claude CLI not in PATH
- gh CLI not authenticated
- Missing environment variables

**Fix:** Add full paths to plist:
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
</dict>
```

### Config Not Found

**Symptom:** Scripts fail with "Config file not found"

**Check:**
```bash
# Verify config exists
cat ~/HomeCare/be-agents-service/config/repos.yaml

# Check working directory in plist
cat ~/Library/LaunchAgents/com.appcaire.auto-compound.plist | grep WorkingDirectory
```

**Fix:** Ensure WorkingDirectory points to be-agents-service root.

### Priority Not Picked

**Symptom:** Script runs but says "No reports found"

**Check:**
```bash
# Verify priorities file exists in target repo
ls -la ~/HomeCare/beta-appcaire/reports/

# Check file format
cat ~/HomeCare/beta-appcaire/reports/priorities-*.md | head -20
```

**Fix:** Create priorities file with correct format (see Common Workflows).

---

## Common Mistakes

### 1. Wrong Repository Path

**❌ Wrong:**
```yaml
repos:
  beta-appcaire:
    path: ~/HomeCare/beta-appcaire/  # Trailing slash
```

**✅ Correct:**
```yaml
repos:
  beta-appcaire:
    path: ~/HomeCare/beta-appcaire
```

### 2. Hardcoded Paths in Scripts

**❌ Wrong:**
```bash
cd ~/HomeCare/beta-appcaire  # Hardcoded
```

**✅ Correct:**
```bash
cd "$REPO_PATH"  # From config
```

Scripts already implement this pattern - don't modify them to hardcode paths.

### 3. Running Scripts Without Repo Argument

**❌ Wrong:**
```bash
./scripts/compound/auto-compound.sh  # No argument
```

**✅ Correct:**
```bash
./scripts/compound/auto-compound.sh beta-appcaire
```

### 4. Modifying Server Code Without Rebuilding

**❌ Wrong:**
```bash
# Edit apps/server/src/index.ts
# Restart launchd without rebuilding
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

**✅ Correct:**
```bash
# Edit apps/server/src/index.ts
cd apps/server
yarn build  # Rebuild!
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

### 5. Forgetting to Update LaunchD After Plist Changes

**❌ Wrong:**
```bash
# Edit plist file
vim launchd/com.appcaire.agent-server.plist
# Don't reload
```

**✅ Correct:**
```bash
# Edit plist
vim launchd/com.appcaire.agent-server.plist
# Copy and reload
cp launchd/com.appcaire.agent-server.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

---

## Summary: Quick Reference

**Start/Stop Server:**
```bash
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

**Manual Agent Run:**
```bash
cd ~/HomeCare/be-agents-service
./scripts/compound/auto-compound.sh <repo-name>
```

**Check Status:**
```bash
curl http://localhost:4010/health
launchctl list | grep appcaire
./scripts/compound/check-status.sh <repo-name>
```

**View Logs:**
```bash
# Server logs
tail -f ~/Library/Logs/agent-server.log

# Agent logs (in target repo)
tail -f ~/HomeCare/<repo>/logs/auto-compound.log
```

**Update Configuration:**
```bash
vim ~/HomeCare/be-agents-service/config/repos.yaml
# No restart needed - scripts read config each run
```

---

## Boris Productivity Workflow

The Boris productivity system (worktrees + subagents) is available when working on target repositories.

**Location:** Target repo's `.claude/prompts/boris-workflow.md`

**Example:** In beta-appcaire:
- `.claude/prompts/boris-workflow.md` - Full Boris workflow guide
- `.claude/prompts/subagents.md` - Parallel execution patterns
- `scripts/worktree-setup.sh` - Create parallel worktrees
- `scripts/sessions/dashboard-stack.sh` - Pre-configured sessions

**Usage in target repo:**
```
Use Boris workflow with worktrees and subagents for [feature]
```

See target repository's `.claude/prompts/` for full documentation.

---

**Related Documentation:**

- See `docs/COMPOUND_WORKFLOW.md` for detailed workflow documentation
- See `docs/COMPOUND_SETUP_GUIDE.md` for setup instructions
- See `docs/PRODUCTIVITY_SYSTEM.md` for Boris productivity patterns
- See `docs/QUICK_REFERENCE.md` for command reference
- See target repository's `/CLAUDE.md` for repo-specific learnings
- See target repository's `.claude/prompts/boris-workflow.md` for Boris patterns
