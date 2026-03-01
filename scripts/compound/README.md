# Compound Workflow Scripts

Autonomous AI agent scripts that learn from your work and ship features while you sleep.

## Agent on hold (2026-01-31)

Scheduled runs are **disabled** until priorities (and optionally the reports directory) are merged to `main`. The agent reads `reports/*.md` from `main`; with nothing on main it exits without creating a branch or PR.

**To resume after merging to main:**

```bash
# Reload launchd jobs (from repo root or launchd/)
cp launchd/com.appcaire.*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

Verify: `launchctl list | grep appcaire` should show all three loaded.

## Scripts

- **`analyze-report.sh`** - Analyzes priority reports and picks #1 item
- **`auto-compound.sh`** - Main automation pipeline (runs at 11:00 PM); pass repo name (e.g. `beta-appcaire`)
- **`loop.sh`** - Iterative task execution engine
- **`daily-compound-review.sh`** - Reviews threads and extracts learnings (runs at 10:30 PM)
- **`check-status.sh`** - Status monitoring (branch, changes, recent PRs)
- **`test-safety.sh`** - Run safety mechanism tests

## How It Works

Every night:

1. **10:30 PM**: `daily-compound-review.sh` reviews last 24h of work, extracts learnings, updates CLAUDE.md files
2. **11:00 PM**: `auto-compound.sh` picks priority #1, creates PRD, implements it, opens draft PR

## Quick Start

From repo root: see [docs/COMPOUND_SETUP_GUIDE.md](../../docs/COMPOUND_SETUP_GUIDE.md) (or `docs/COMPOUND_SETUP_GUIDE.md` if it exists). For safety checks and nightly schedule, see [SAFETY.md](SAFETY.md).

## File Dependencies

Paths below are relative to the **target repo** (e.g. beta-appcaire) when you run the scripts with a repo argument. Config is read from `config/repos.yaml` in be-agents-service.

**Input:**

- Target repo `reports/*.md` or workspace `priorities.md` - Priority reports (see root README "Priority Reports")
- Optional: target repo `.env` / env from `~/.config/caire/env`

**Output:**

- Target repo `tasks/prd-*.json` - Task list for implementation
- Target repo `logs/compound-review.log`, `logs/auto-compound.log` - Job logs

## Manual Testing

Run from repo root (`be-agents-service`) so script paths and target repos resolve correctly:

```bash
# From be-agents-service root
./scripts/compound/daily-compound-review.sh <repo-name>
./scripts/compound/auto-compound.sh <repo-name>

# Test analyze report (path = target repo's report file)
./scripts/compound/analyze-report.sh /path/to/repo/reports/priorities-2026-01-30.md

# Test safety mechanisms (no branch/PR created)
./scripts/compound/test-safety.sh
```

**WARNING:** `auto-compound.sh` creates a real feature branch and draft PR. Use a test repo or dry-run if available.

## Automation

Runs via launchd (macOS):

- `~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist`
- `~/Library/LaunchAgents/com.appcaire.auto-compound.plist`
- `~/Library/LaunchAgents/com.appcaire.caffeinate.plist`

## Documentation

- **Safety**: [SAFETY.md](SAFETY.md) - Mandatory checks (uncommitted changes, branch), how to disable nightly jobs
- **Setup Guide**: [docs/COMPOUND_SETUP_GUIDE.md](../../docs/COMPOUND_SETUP_GUIDE.md) - Quick setup (from repo root: `docs/COMPOUND_SETUP_GUIDE.md`)
- **Full Workflow**: [docs/COMPOUND_WORKFLOW.md](../../docs/COMPOUND_WORKFLOW.md) - Comprehensive guide
- **Dashboard**: Root [README.md](../../README.md) - Dashboard on port 3010, agent teams (4 teams, 27 agents)

## Troubleshooting

Check logs (in **target repo** `logs/`):

```bash
tail -f <repo-path>/logs/compound-review.log
tail -f <repo-path>/logs/auto-compound.log
```

If safety checks abort the run, see [SAFETY.md](SAFETY.md).

Verify launchd jobs:

```bash
launchctl list | grep appcaire
```

Manual trigger:

```bash
launchctl start com.appcaire.daily-compound-review
launchctl start com.appcaire.auto-compound
```
