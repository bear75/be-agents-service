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
- **`auto-compound.sh`** - Main automation pipeline (runs at 11:00 PM)
- **`loop.sh`** - Iterative task execution engine
- **`daily-compound-review.sh`** - Reviews threads and extracts learnings (runs at 10:30 PM)

## How It Works

Every night:

1. **10:30 PM**: `daily-compound-review.sh` reviews last 24h of work, extracts learnings, updates CLAUDE.md files
2. **11:00 PM**: `auto-compound.sh` picks priority #1, creates PRD, implements it, opens draft PR

## Quick Start

See the main setup guide: `SETUP.md` or `QUICK_START.md`

## File Dependencies

The scripts read/write these files:

**Input:**

- `../../reports/*.md` - Priority reports (latest file is used)
- `../../.env.local` - Optional environment config

**Output:**

- `../../tasks/prd-*.md` - Generated PRDs
- `prd.json` - Task list for current implementation
- `../../logs/compound-review.log` - Review job logs
- `../../logs/auto-compound.log` - Implementation job logs

## Manual Testing

```bash
# Test compound review
../daily-compound-review.sh

# Test analyze report
./analyze-report.sh ../../reports/priorities-2026-01-30.md

# Test auto-compound (WARNING: creates real branch and PR!)
./auto-compound.sh

# Test execution loop
./loop.sh 25
```

## Automation

Runs via launchd (macOS):

- `~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist`
- `~/Library/LaunchAgents/com.appcaire.auto-compound.plist`
- `~/Library/LaunchAgents/com.appcaire.caffeinate.plist`

## Documentation

- **Setup Guide**: `SETUP.md` - Installation and configuration
- **Quick Start**: `QUICK_START.md` - Daily workflow and commands
- **Full Workflow**: `WORKFLOW.md` - Priorities, sessions, tasks, learnings
- **Dashboard**: http://localhost:3030 - Real-time monitoring

## Troubleshooting

Check logs:

```bash
tail -f ../../logs/compound-review.log
tail -f ../../logs/auto-compound.log
```

Verify launchd jobs:

```bash
launchctl list | grep appcaire
```

Manual trigger:

```bash
launchctl start com.appcaire.daily-compound-review
launchctl start com.appcaire.auto-compound
```
