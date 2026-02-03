# Agent Service Deployment Guide

Complete guide for deploying the agent service on macOS with launchd.

---

## Prerequisites

Before deploying, ensure you have:

- [ ] macOS system with launchd support
- [ ] Homebrew installed (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- [ ] Node.js 20+ via nvm (`brew install nvm`, then follow setup instructions)
- [ ] Yarn 1.22+ (`npm install -g yarn`)
- [ ] Claude Code CLI installed and configured
- [ ] GitHub CLI installed and authenticated (`brew install gh && gh auth login`)
- [ ] Target repository cloned (e.g., `~/HomeCare/beta-appcaire`)

---

## Step 1: Clone and Setup

```bash
# Navigate to projects directory
cd ~/HomeCare

# Clone the agent service repository
git clone git@github.com:bear75/be-agents-service.git
cd be-agents-service

# Install all dependencies
yarn install

# Build the server application
cd apps/server
yarn build

# Verify build succeeded
ls -la dist/
# Should see index.js and other compiled files
```

---

## Step 2: Configure Repositories

Edit `config/repos.yaml` to add your target repositories:

```bash
vim config/repos.yaml
```

Example configuration:

```yaml
repos:
  beta-appcaire:
    path: ~/HomeCare/beta-appcaire
    schedule:
      review: "22:30"
      compound: "23:00"
    priorities_dir: reports/
    logs_dir: logs/
    tasks_dir: tasks/
    enabled: true
    github:
      owner: bear75
      repo: beta-appcaire
      default_branch: main
```

**Required fields:**
- `path`: Absolute path to repository (use `~` for home directory)
- `schedule.review`: Time for daily review (HH:MM in 24-hour format)
- `schedule.compound`: Time for automated implementation (HH:MM)
- `priorities_dir`: Directory containing priorities files
- `logs_dir`: Directory for agent logs
- `enabled`: Set to `true` to enable agent for this repo

---

## Step 3: Setup Environment Variables

Create environment file for API keys:

```bash
# Create config directory
mkdir -p ~/.config/caire

# Create environment file
cat > ~/.config/caire/env << 'EOF'
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
export GITHUB_TOKEN="your-github-token-here"
EOF

# Secure the file
chmod 600 ~/.config/caire/env

# Verify
cat ~/.config/caire/env
```

**Getting API Keys:**

- **Anthropic API Key**: https://console.anthropic.com/settings/keys
- **GitHub Token**: `gh auth token` (after running `gh auth login`)

---

## Step 4: Update LaunchD Plist Files

The plist files need to reference your actual Node.js installation path.

### Find Your Node.js Path

```bash
which yarn
# Example output: /Users/USERNAME/.nvm/versions/node/v22.15.1/bin/yarn
```

### Update agent-server.plist

Edit `launchd/com.appcaire.agent-server.plist`:

```bash
vim launchd/com.appcaire.agent-server.plist
```

Update the paths (replace USERNAME and Node version):

```xml
<key>ProgramArguments</key>
<array>
    <string>/Users/USERNAME/.nvm/versions/node/vXX.XX.X/bin/yarn</string>
    <string>workspace</string>
    <string>server</string>
    <string>start</string>
</array>

<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/Users/USERNAME/.nvm/versions/node/vXX.XX.X/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>PORT</key>
    <string>4010</string>
</dict>
```

### Verify Plist Syntax

```bash
cd launchd
plutil -lint *.plist
# All should return "OK"
```

---

## Step 5: Install LaunchD Jobs

```bash
# Copy plist files to LaunchAgents
cp launchd/*.plist ~/Library/LaunchAgents/

# Load all jobs
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Verify all jobs are loaded
launchctl list | grep appcaire
```

**Expected output:**
```
12481  0  com.appcaire.agent-server
-      0  com.appcaire.auto-compound
-      0  com.appcaire.caffeinate
-      0  com.appcaire.daily-compound-review
```

The number (PID) for agent-server indicates it's running. The `-` for others means they're scheduled but not currently running.

---

## Step 6: Verify Deployment

### Check Server is Running

```bash
# Health check
curl http://localhost:4010/health

# Expected output:
# {
#   "success": true,
#   "service": "agent-service",
#   "version": "1.0.0",
#   "timestamp": "2026-02-03T..."
# }
```

### Check API Endpoints

```bash
# List configured repositories
curl http://localhost:4010/api/repos | jq

# Get repository status
curl http://localhost:4010/api/repos/beta-appcaire/status | jq

# View priorities
curl http://localhost:4010/api/repos/beta-appcaire/priorities | jq
```

### Check Dashboard

```bash
# Open dashboard in browser
open http://localhost:3010
```

You should see:
- Repository selector
- Agent status card
- Priority board
- Log viewer

### Test Script Execution

```bash
cd ~/HomeCare/be-agents-service

# Check status (should show target repo status)
./scripts/compound/check-status.sh beta-appcaire

# Expected output:
# - Current branch
# - Uncommitted changes
# - Recent PRs
```

### Check LaunchD Logs

```bash
# Server logs
tail -f ~/Library/Logs/agent-server.log

# Error logs (should be empty if working)
tail -f ~/Library/Logs/agent-server-error.log
```

---

## Step 7: Setup Target Repository

Ensure your target repository has the required structure:

```bash
cd ~/HomeCare/beta-appcaire  # Or your target repo

# Create directories if they don't exist
mkdir -p reports logs tasks

# Create initial priorities file
cat > reports/priorities-$(date +%Y-%m-%d).md << 'EOF'
# Product Priorities - $(date +%Y-%m-%d)

## High Priority

1. Your first priority item here
2. Your second priority item

## Medium Priority

1. Medium priority task

## Low Priority

1. Low priority task
EOF

# Commit priorities
git add reports/
git commit -m "docs: add initial priorities"
git push origin main
```

---

## Step 8: Test End-to-End Workflow

### Manual Test Run

```bash
cd ~/HomeCare/be-agents-service

# Trigger review workflow manually
./scripts/compound/daily-compound-review.sh beta-appcaire

# Check logs
tail -50 ~/HomeCare/beta-appcaire/logs/compound-review.log
```

**Expected behavior:**
- Script reads from target repo
- Reviews recent Claude threads
- Updates CLAUDE.md if changes found
- Commits to main branch

### Schedule Test

Wait for scheduled times or temporarily modify schedule:

```bash
# Edit plist to run sooner (e.g., 2 minutes from now)
vim ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist

# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist

# Watch logs
tail -f ~/HomeCare/beta-appcaire/logs/compound-review.log
```

---

## Scheduled Workflow Timeline

Once deployed, the agent runs on this schedule:

| Time | Job | Action |
|------|-----|--------|
| 5:00 PM | caffeinate | Mac stays awake for 9 hours |
| 10:30 PM | daily-review | Extract learnings, update CLAUDE.md |
| 11:00 PM | auto-compound | Pick priority #1, implement, create PR |
| 2:00 AM | caffeinate ends | Mac can sleep |

### Next Morning Review

Check the results:

```bash
cd ~/HomeCare/beta-appcaire

# View generated PR
gh pr list

# Check logs
tail -100 logs/auto-compound.log
tail -100 logs/compound-review.log

# View dashboard
open http://localhost:3010
```

---

## Maintenance

### Updating the Service

```bash
cd ~/HomeCare/be-agents-service

# Pull latest changes
git pull origin main

# Reinstall dependencies if needed
yarn install

# Rebuild server
cd apps/server
yarn build

# Restart server
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

### Updating Configuration

```bash
# Edit configuration
vim ~/HomeCare/be-agents-service/config/repos.yaml

# No restart needed - scripts read config each run
```

### Viewing Logs

```bash
# Server logs
tail -f ~/Library/Logs/agent-server.log
tail -f ~/Library/Logs/agent-server-error.log

# Agent workflow logs (in target repo)
tail -f ~/HomeCare/beta-appcaire/logs/auto-compound.log
tail -f ~/HomeCare/beta-appcaire/logs/compound-review.log

# Caffeinate log
tail -f ~/HomeCare/beta-appcaire/logs/caffeinate.log
```

### Troubleshooting

See `CLAUDE.md` Troubleshooting section for common issues and solutions.

---

## Uninstalling

If you need to remove the service:

```bash
# Unload all jobs
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Remove plist files
rm ~/Library/LaunchAgents/com.appcaire.*.plist

# Remove environment file
rm ~/.config/caire/env

# Optionally remove repository
rm -rf ~/HomeCare/be-agents-service
```

---

## Security Considerations

1. **API Keys**: Store in `~/.config/caire/env` with permissions `600`
2. **LaunchD**: Runs as your user (not root) for security
3. **Logs**: May contain sensitive information - secure log directories
4. **GitHub Token**: Use fine-grained token with minimum required scopes

---

## Support

For issues or questions:

1. Check `CLAUDE.md` Troubleshooting section
2. Review logs for error messages
3. Create issue at https://github.com/bear75/be-agents-service/issues

---

## Quick Reference Card

**Start Service:**
```bash
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

**Stop Service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
```

**Check Status:**
```bash
launchctl list | grep appcaire
curl http://localhost:4010/health
```

**View Dashboard:**
```bash
open http://localhost:3010
```

**Manual Trigger:**
```bash
cd ~/HomeCare/be-agents-service
./scripts/compound/auto-compound.sh <repo-name>
```

**Check Logs:**
```bash
tail -f ~/Library/Logs/agent-server.log
tail -f ~/HomeCare/<repo>/logs/auto-compound.log
```
