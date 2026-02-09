# Mac Mini Complete Setup — February 2026

Everything you need, in order. Assumes Mac mini already has macOS, Homebrew, Git, Node.js 22+, Yarn, `gh` CLI, and Claude Code CLI installed (see `MAC_MINI_SETUP.md` Phases 1-3 if starting from scratch).

---

## Step 1: Pull the Agent Service (2 min)

```bash
cd ~/HomeCare/be-agents-service

# Pull the new branch with all workspace features
git fetch origin
git checkout cursor/shared-markdown-data-storage-d333
git pull

# Or if you already merged to main:
git checkout main && git pull
```

Verify the new files exist:
```bash
ls scripts/workspace/          # Should see init-workspace.sh, etc.
ls config/openclaw/            # Should see openclaw.json, system-prompt.md
ls apps/openclaw-bridge/       # Should see src/index.ts
ls docs/PRD-MOBILE-APP.md      # Should exist
```

---

## Step 2: Initialize the Shared Workspace (1 min)

This creates the markdown workspace on iCloud (or local disk).

```bash
cd ~/HomeCare/be-agents-service

# Option A: iCloud (access from iPhone/iPad)
./scripts/workspace/init-workspace.sh beta-appcaire

# Option B: Local only (if you prefer)
./scripts/workspace/init-workspace.sh beta-appcaire ~/HomeCare/workspaces/beta-appcaire
```

If using iCloud, the path in `config/repos.yaml` is:
```
~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire
```

**Edit it if your path is different:**
```bash
vim config/repos.yaml
# Update the workspace.path under beta-appcaire
```

Verify:
```bash
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/
# Should see: inbox.md  priorities.md  tasks.md  follow-ups.md  check-ins/  memory/
```

---

## Step 3: Edit Your Priorities (2 min)

Open the priorities file and add your real priorities:

```bash
open ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/priorities.md
```

The template already has P1 (workspace setup), P2 (mobile app), P3 (TimeFold). Edit to match your current focus.

Also update the context file so agents understand your project:

```bash
open ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/memory/context.md
```

---

## Step 4: Install the Agent Server + Dashboard (3 min)

```bash
cd ~/HomeCare/be-agents-service

# Install dependencies
yarn install

# Build the server
cd apps/server
yarn build

# Test it runs
node dist/index.js
# Should see: 🤖 Agent Service API running on http://localhost:4010
# Press Ctrl+C to stop
```

---

## Step 5: Set Up Telegram Bot (5 min)

### 5a: Create the bot

1. Open Telegram on your phone
2. Search for **@BotFather**
3. Send `/newbot`
4. Name: `AppCaire Agent` (or anything you like)
5. Username: `appcaire_agent_bot` (must be unique, end with `bot`)
6. **Copy the token** — looks like `7123456789:AAF_abcdef...`

### 5b: Get your chat ID

1. Search for **@userinfobot** on Telegram
2. Send it any message
3. **Copy your numeric ID** — looks like `123456789`

### 5c: Save credentials

```bash
# Create or edit the env file
mkdir -p ~/.config/caire
cat >> ~/.config/caire/env << 'EOF'
export TELEGRAM_BOT_TOKEN="PASTE_YOUR_BOT_TOKEN_HERE"
export TELEGRAM_CHAT_ID="PASTE_YOUR_CHAT_ID_HERE"
EOF

# Secure the file
chmod 600 ~/.config/caire/env

# Load it in your current session
source ~/.config/caire/env
```

### 5d: Test sending a message

```bash
source ~/.config/caire/env
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=🤖 Agent service connected!" \
  -d "parse_mode=Markdown"
```

You should receive the message on Telegram!

---

## Step 6: Install OpenClaw (5 min)

```bash
# Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Run the onboarding wizard
openclaw onboard --install-daemon
```

### 6a: Build the MCP bridge

```bash
cd ~/HomeCare/be-agents-service/apps/openclaw-bridge
npm install
# Note: TypeScript build is slow due to MCP SDK types.
# Use tsx for runtime instead:
npx tsx src/index.ts  # Quick test — should print "MCP server running on stdio"
# Ctrl+C to stop
```

### 6b: Configure OpenClaw

```bash
# Create config directory if needed
mkdir -p ~/.openclaw

# Copy template
cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json

# Edit with your actual values
vim ~/.openclaw/openclaw.json
```

**Replace these values:**
- `${TELEGRAM_BOT_TOKEN}` → your bot token from Step 5
- `YOUR_TELEGRAM_USER_ID` → your numeric ID from Step 5
- `+46XXXXXXXXX` → your WhatsApp number (or remove whatsapp section)
- Verify the MCP server path points to your actual directory

### 6c: Start OpenClaw

```bash
openclaw start
```

### 6d: Test via Telegram

Open Telegram, find your bot, send:
- `status` — should show workspace overview
- `add to inbox: test item` — should confirm added

---

## Step 7: Load LaunchD Jobs (2 min)

```bash
cd ~/HomeCare/be-agents-service

# Copy all plists
cp launchd/*.plist ~/Library/LaunchAgents/

# Load them
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.morning-briefing.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.weekly-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist

# Verify all loaded
launchctl list | grep appcaire
```

**⚠️ Important:** Update the `HOME` path in plist files if your username differs:
```bash
# Check your username
whoami
# If not "bjornevers_MacPro", update all plists:
sed -i '' 's/bjornevers_MacPro/YOUR_USERNAME/g' ~/Library/LaunchAgents/com.appcaire.*.plist
```

---

## Step 8: Verify Everything (3 min)

### Health checks:

```bash
# Server API
curl -s http://localhost:4010/health | python3 -m json.tool

# Workspace status
curl -s http://localhost:4010/api/workspace/beta-appcaire/status | python3 -m json.tool

# Plans
curl -s http://localhost:4010/api/plans | python3 -m json.tool

# Setup status
curl -s http://localhost:4010/api/plans/setup-status?repo=beta-appcaire | python3 -m json.tool
```

### Dashboard:
```bash
open http://localhost:3010
# Or the old dashboard:
open http://localhost:3030
```

### Test morning briefing:
```bash
./scripts/notifications/morning-briefing.sh beta-appcaire
# Check Telegram for the message
```

### Test workspace sync:
```bash
./scripts/workspace/sync-to-workspace.sh beta-appcaire
# Check agent-reports/ in your workspace
```

---

## Step 9: WhatsApp (Optional, later)

WhatsApp requires additional phone number verification through OpenClaw. See:
- OpenClaw docs: https://docs.clawd.bot/
- Config template: `config/openclaw/openclaw.json` (whatsapp section)

---

## Schedule Summary

| Time | What | Telegram? |
|------|------|-----------|
| **8:00 AM** | Morning briefing | ✅ Pushed to you |
| **Mon 8:00 AM** | Weekly review | ✅ Pushed to you |
| **10:30 PM** | Daily review (extract learnings) | — |
| **11:00 PM** | Auto-compound (implement P1) | ✅ Session complete notification |
| **Always** | OpenClaw bot | ✅ You text anytime |
| **Always** | Caffeinate (keep awake) | — |
| **Always** | API server (port 4010) | — |

---

## Quick Reference

```bash
# Add to inbox from terminal
curl -X POST http://localhost:4010/api/workspace/beta-appcaire/inbox \
  -H 'Content-Type: application/json' \
  -d '{"text": "your idea here"}'

# View workspace overview
curl -s http://localhost:4010/api/workspace/beta-appcaire/overview | python3 -m json.tool

# Generate today's check-in
./scripts/workspace/generate-checkin.sh beta-appcaire daily

# Process inbox (triage with Claude)
./scripts/workspace/process-inbox.sh beta-appcaire

# Manual agent run
./scripts/compound/auto-compound.sh beta-appcaire

# Check agent status
./scripts/compound/check-status.sh beta-appcaire
```

---

## Troubleshooting

**Workspace not found?**
```bash
./scripts/workspace/init-workspace.sh beta-appcaire
```

**Telegram not sending?**
```bash
source ~/.config/caire/env
echo "TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "TELEGRAM_CHAT_ID: $TELEGRAM_CHAT_ID"
```

**OpenClaw not connecting?**
```bash
openclaw gateway status
openclaw logs
```

**LaunchD job failed?**
```bash
launchctl list | grep appcaire
# Look for non-zero exit codes
# Check /tmp/*.log for errors
```

**Dashboard blank?**
```bash
cd ~/HomeCare/be-agents-service/apps/server
yarn build && node dist/index.js
```
