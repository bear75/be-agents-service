# Autonomous Compound Workflow

An autonomous AI agent system that learns from your work and ships features while you sleep.

## Overview

This workflow runs two automated jobs every night:

1. **10:30 PM - Compound Review**: Reviews all work from the last 24 hours, extracts learnings, and updates CLAUDE.md files
2. **11:00 PM - Auto-Compound**: Picks the #1 priority from your reports, implements it via the **multi-agent orchestrator** (backend, frontend, verification, etc.), and creates a **draft PR**. It never merges to main — you review and merge manually.

**Safe workflow:** Branch → implement → draft PR → you review & approve → you merge. Payment and sensitive code always go through this review; compound does not auto-merge.

The agent gets smarter every day by reading its own updated instructions before each implementation run.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Daily Cycle                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  10:30 PM: Compound Review                                   │
│  ├── Read all threads from last 24h                          │
│  ├── Extract learnings (patterns, gotchas, context)          │
│  ├── Update CLAUDE.md files                                  │
│  └── Commit & push to main                                   │
│                                                               │
│  11:00 PM: Auto-Compound                                     │
│  ├── Pull latest (with fresh CLAUDE.md)                      │
│  ├── Analyze latest report → pick #1 priority               │
│  ├── Create PRD for priority item                            │
│  ├── Convert PRD to task list (JSON)                         │
│  ├── Run orchestrator (specialist agents: backend, frontend,  │
│  │   verification, db-architect, etc.)                       │
│  └── Create PR with implementation                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools

1. **Claude Code CLI**

   ```bash
   # Install and configure Claude Code
   claude configure
   ```

2. **GitHub CLI**

   ```bash
   brew install gh
   gh auth login
   ```

3. **jq** (for JSON parsing)
   ```bash
   brew install jq
   ```

### Required Setup

1. **Compound Engineering Plugin**
   - Install the compound-engineering plugin for Claude Code
   - This enables the agent to extract and persist learnings

2. **Reports Directory**
   - Create prioritized reports in `reports/` directory
   - Reports should list features/tasks by priority
   - Latest report is automatically picked each night

3. **CLAUDE.md Files**
   - Create CLAUDE.md files in relevant directories
   - These store persistent learnings and patterns
   - Agent updates these files with new knowledge

## Installation

### 1. Set Up Environment

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` if you need custom configuration (optional).

### 2. Test Scripts Manually

Test the compound review:

```bash
./scripts/compound/daily-compound-review.sh
```

Test the auto-compound (requires a report in `reports/`):

```bash
./scripts/compound/auto-compound.sh
```

### 3. Install launchd Jobs

Copy the plist files to your LaunchAgents directory:

```bash
cp launchd/com.appcaire.daily-compound-review.plist ~/Library/LaunchAgents/
cp launchd/com.appcaire.auto-compound.plist ~/Library/LaunchAgents/
cp launchd/com.appcaire.caffeinate.plist ~/Library/LaunchAgents/
```

Load the jobs:

```bash
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
```

Verify they're loaded:

```bash
launchctl list | grep appcaire
```

You should see three jobs listed:

- `com.appcaire.caffeinate`
- `com.appcaire.auto-compound`
- `com.appcaire.daily-compound-review`

## Usage

### Creating Reports

Create prioritized reports in the `reports/` directory:

```markdown
# Product Priorities - 2026-01-30

## High Priority

1. Add user authentication with JWT
2. Implement caching layer for API responses
3. Add error tracking with Sentry

## Medium Priority

4. Refactor database queries for performance
5. Add unit tests for core services

## Low Priority

6. Update documentation
7. Add dark mode support
```

The auto-compound script will automatically pick the #1 priority item.

### Manual Execution

You can manually trigger the jobs for testing:

```bash
# Test compound review
launchctl start com.appcaire.daily-compound-review

# Test auto-compound
launchctl start com.appcaire.auto-compound
```

### Monitoring

Check the logs:

```bash
# View compound review logs
tail -f logs/compound-review.log

# View auto-compound logs
tail -f logs/auto-compound.log

# View caffeinate logs
tail -f logs/caffeinate.log
```

### What to Expect Each Morning

When you wake up, you should see:

1. **Updated CLAUDE.md files** with learnings from yesterday's work
2. **A new draft PR** implementing your #1 priority item
3. **Logs** showing exactly what the agent did
4. **A new feature branch** with the implementation

Review the PR, make any needed adjustments, and merge when ready.

## Configuration

### Adjusting Schedule

Edit the plist files to change when jobs run:

```xml
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key>
  <integer>22</integer>  <!-- Change this -->
  <key>Minute</key>
  <integer>30</integer>  <!-- And this -->
</dict>
```

After editing, reload the job:

```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
```

### Adjusting Caffeinate Window

The caffeinate job keeps your Mac awake from 5 PM to 2 AM (9 hours). To adjust:

```xml
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key>
  <integer>17</integer>  <!-- Start time -->
  <key>Minute</key>
  <integer>0</integer>
</dict>
```

And adjust the duration (in seconds):

```xml
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/caffeinate</string>
  <string>-i</string>
  <string>-t</string>
  <string>32400</string>  <!-- 9 hours = 32400 seconds -->
</array>
```

### Adjusting Max Iterations

Edit `scripts/compound/auto-compound.sh` and change the iteration limit:

```bash
./scripts/compound/loop.sh 25  # Change 25 to your desired limit
```

## Troubleshooting

### Jobs Not Running

1. Check if jobs are loaded:

   ```bash
   launchctl list | grep appcaire
   ```

2. Check for errors in logs:

   ```bash
   tail -f logs/compound-review.log
   tail -f logs/auto-compound.log
   ```

3. Verify paths in plist files are absolute and correct

4. Ensure your Mac is awake during the scheduled time (caffeinate should handle this)

### Agent Not Finding Reports

1. Ensure reports exist in `reports/` directory
2. Check report filename format (should be `.md` files)
3. Verify the `LATEST_REPORT` logic in `auto-compound.sh`

### Agent Not Creating PRs

1. Verify GitHub CLI is authenticated:

   ```bash
   gh auth status
   ```

2. Check if the agent has permissions to push branches

3. Review logs for specific error messages

### Agent Not Updating CLAUDE.md

1. Ensure CLAUDE.md files exist in relevant directories
2. Verify the compound-engineering plugin is installed
3. Check that Claude Code can access and modify files

## Uninstalling

To stop the automated workflow:

```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.caffeinate.plist

rm ~/Library/LaunchAgents/com.appcaire.*.plist
```

## Advanced Usage

### Slack Notifications

Add Slack webhook to `.env.local`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Then modify scripts to send notifications:

```bash
# In auto-compound.sh, after PR creation:
if [ -n "$SLACK_WEBHOOK_URL" ]; then
  curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"✓ Compound PR created: $PRIORITY_ITEM\"}"
fi
```

### Multiple Priority Tracks

Create multiple report files and run different jobs on different nights:

- `reports/features.md` - Features (Monday, Wednesday, Friday)
- `reports/bugs.md` - Bug fixes (Tuesday, Thursday)
- `reports/refactoring.md` - Technical debt (Saturday)

Adjust plist files to run on specific days:

```xml
<key>StartCalendarInterval</key>
<array>
  <dict>
    <key>Weekday</key>
    <integer>1</integer>  <!-- Monday -->
    <key>Hour</key>
    <integer>23</integer>
  </dict>
  <dict>
    <key>Weekday</key>
    <integer>3</integer>  <!-- Wednesday -->
    <key>Hour</key>
    <integer>23</integer>
  </dict>
</array>
```

### Auto-Merge Small PRs

Add automatic merge logic for low-risk changes:

```bash
# In auto-compound.sh, after PR creation:
PR_URL=$(gh pr view --json url -q .url)
FILES_CHANGED=$(gh pr view --json changedFiles -q '.changedFiles | length')

if [ "$FILES_CHANGED" -lt 3 ]; then
  echo "Small PR detected. Waiting for CI..."
  gh pr checks "$PR_URL" --watch
  gh pr merge "$PR_URL" --auto --squash
fi
```

## The Compound Effect

Every night, your agent:

- Learns from mistakes and patterns
- Updates its own instructions (CLAUDE.md)
- Implements the next priority with accumulated knowledge

Over time:

- CLAUDE.md files become a rich knowledge base
- The agent handles edge cases it previously encountered
- Implementation quality improves as patterns emerge
- Your codebase evolves consistently while you sleep

The key insight: **Knowledge compounds**. Yesterday's learnings inform today's implementation, making tomorrow's work even better.

## Credits

Based on the workflow by [@ryancarson](https://x.com/ryancarson/status/2016520542723924279), adapted for Claude Code.

Original inspiration from:

- [Compound Engineering Plugin](https://github.com/kieranklaassen/compound-engineering) by @kieranklaassen
- Compound Product automation layer
- Ralph autonomous agent loop
