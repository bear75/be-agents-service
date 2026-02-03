# Agent Service

Agent automation orchestration system for managing Claude Code agents across multiple repositories.

## Overview

This service provides centralized orchestration for compound agent workflows across multiple repositories. It includes:

- **Automated Workflows**: Nightly review and implementation of prioritized tasks
- **API Server**: REST API for monitoring and controlling agents
- **Web Dashboard**: Real-time status, logs, and priority management
- **Multi-Repo Support**: Manage agents for multiple repositories from one place

## Architecture

```
be-agents-service/
├── apps/
│   ├── server/         # API server (port 4010)
│   └── dashboard/      # Web UI (port 3010)
├── scripts/
│   └── compound/       # Agent automation scripts
├── config/
│   └── repos.yaml      # Repository configuration
├── data/
│   └── state/          # Runtime state
└── launchd/            # macOS scheduled jobs
```

## Quick Start

### Prerequisites

- Node.js 20+ with Volta
- Yarn 1.22+
- Claude Code CLI installed and configured
- gh CLI authenticated

### Installation

```bash
# Clone repository
cd ~/HomeCare
git clone git@github.com:bear75/be-agents-service.git
cd be-agents-service

# Install dependencies
yarn install

# Configure repositories
cp config/repos.yaml config/repos.local.yaml
vim config/repos.local.yaml
```

### Configuration

Edit `config/repos.yaml` to add repositories:

```yaml
repos:
  your-repo:
    path: ~/path/to/repo
    schedule:
      review: "22:30"
      compound: "23:00"
    priorities_dir: reports/
    logs_dir: logs/
    enabled: true
```

### Manual Usage

Run agent workflows manually:

```bash
# Run daily review
./scripts/compound/daily-compound-review.sh <repo-name>

# Run auto-compound
./scripts/compound/auto-compound.sh <repo-name>

# Check status
./scripts/compound/check-status.sh <repo-name>
```

### Automated Scheduling (macOS)

The service uses launchd for automated scheduling:

```bash
# Install launchd jobs
cp launchd/*.plist ~/Library/LaunchAgents/

# Update paths in plist files to match your installation
# Then load the jobs:
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Verify jobs are loaded
launchctl list | grep appcaire
```

## Development

### Start API Server

```bash
yarn dev:server
# Server runs on http://localhost:4010
```

### Start Dashboard

```bash
yarn dev:dashboard
# Dashboard runs on http://localhost:3010
```

### Run Both

```bash
yarn dev:server &
yarn dev:dashboard &
```

## API Endpoints

### Repositories

- `GET /api/repos` - List all configured repositories
- `GET /api/repos/:name/status` - Get agent status for a repository
- `GET /api/repos/:name/priorities` - Get priorities from repository
- `GET /api/repos/:name/logs` - Get logs from repository

### Agent Control

- `POST /api/agents/trigger/:name` - Manually trigger agent run
- `POST /api/agents/cancel/:name` - Cancel running agent

## How It Works

### Daily Workflow

1. **10:30 PM** - `daily-compound-review.sh` runs
   - Reviews Claude Code threads from last 24h
   - Extracts learnings
   - Updates CLAUDE.md files in target repository
   - Commits directly to main

2. **11:00 PM** - `auto-compound.sh` runs
   - Reads priorities from target repository's `reports/` directory
   - Picks priority #1
   - Creates feature branch in target repository
   - Implements using Claude Code
   - Creates PR (never pushes directly to main)

3. **Morning** - Review generated PR

### Multi-Repo Pattern

- **Scripts live here** (be-agents-service)
- **Data lives there** (target repositories)
- Scripts accept repo name as argument
- Read configuration from `config/repos.yaml`
- Write logs and PRDs to target repository

### Safety Mechanisms

- **Branch check**: Must be on main branch
- **Auto-stash**: Stashes uncommitted work before starting
- **PR creation**: Creates PR, never pushes directly to main
- **Safety commits**: Auto-commits if Claude forgets

## Troubleshooting

### Scripts fail with "repo not found"

Check that the repo is configured in `config/repos.yaml` and the path exists:

```bash
cat config/repos.yaml
ls -la ~/HomeCare/your-repo
```

### launchd jobs not running

Check job status and logs:

```bash
launchctl list | grep appcaire
tail -f ~/Library/Logs/appcaire-*.log
```

Verify plist paths are correct:

```bash
plutil -lint ~/Library/LaunchAgents/com.appcaire.*.plist
```

### Agent can't find priorities

Ensure priorities file exists in target repo:

```bash
ls -la ~/HomeCare/your-repo/reports/priorities-*.md
```

## Documentation

- See `docs/` for detailed workflow documentation
- See `CLAUDE.md` for development learnings
- See target repository documentation for repository-specific details

## Contributing

This is an internal service. For issues or improvements:

1. Create issue describing the problem
2. Create feature branch
3. Implement and test
4. Create PR for review

## License

Private - Internal use only
