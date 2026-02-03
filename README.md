# BE Agent Service

Autonomous agent service for beta-appcaire development automation running on Mac Mini.

## Overview

This service automates nightly development tasks:
- **10:30 PM**: Reviews Claude Code threads, updates CLAUDE.md files
- **11:00 PM**: Auto-implements priority #1 from daily reports, creates PR

## Repository Structure

```
be-agent-service/
├── scripts/
│   ├── daily-compound-review.sh    # 10:30 PM - Extract learnings
│   ├── auto-compound.sh            # 11:00 PM - Auto-implement
│   ├── loop.sh                     # Task execution loop
│   ├── analyze-report.sh           # Parse priorities report
│   ├── check-status.sh             # Status monitoring
│   └── test-safety.sh              # Safety mechanism tests
├── launchd/
│   ├── com.appcaire.auto-compound.plist
│   ├── com.appcaire.caffeinate.plist
│   └── com.appcaire.daily-compound-review.plist
├── README.md                       # This file
├── SAFETY.md                       # Safety mechanisms
└── .gitignore
```

## Installation

### 1. Clone Repository

```bash
cd ~/HomeCare
git clone https://github.com/bear75/be-agent-service.git
cd be-agent-service
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

## Usage

### Manual Execution

```bash
# Run daily review
cd ~/HomeCare/beta-appcaire
../be-agent-service/scripts/daily-compound-review.sh

# Run auto-compound
cd ~/HomeCare/beta-appcaire
../be-agent-service/scripts/auto-compound.sh

# Check status
../be-agent-service/scripts/check-status.sh

# Test safety mechanisms
../be-agent-service/scripts/test-safety.sh
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
chmod +x ~/HomeCare/be-agent-service/scripts/*.sh
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

Issues: https://github.com/bear75/be-agent-service/issues
