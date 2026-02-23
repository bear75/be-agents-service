# OpenClaw Setup Guide

This guide walks you through setting up OpenClaw as the messaging gateway for your agent workspace.

## Prerequisites

- Mac mini (or any Mac/Linux) with Node.js 22+
- Telegram account (for bot creation)
- Agent service repo cloned to `~/HomeCare/be-agents-service`

## Step 1: Install OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## Step 2: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Name it something like "Agent Workspace"
4. Copy the bot token (looks like `123456:ABC-DEF...`)
5. Get your Telegram user ID:
   - Search for `@userinfobot` on Telegram
   - Send it any message
   - Copy your numeric user ID

## Step 3: Build the MCP Bridge

```bash
cd ~/HomeCare/be-agents-service/apps/openclaw-bridge
yarn install
yarn build   # or use tsx for dev: yarn dev
```

## Step 4: Configure OpenClaw

```bash
# Copy the template config
cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json

# Edit with your values
vim ~/.openclaw/openclaw.json
```

Update these values:
- `TELEGRAM_BOT_TOKEN` → your bot token from Step 2
- `YOUR_TELEGRAM_USER_ID` → your numeric user ID
- Verify all paths point to your actual directories

## Step 5: Set Environment Variables

```bash
# Add to ~/.config/caire/env or ~/.zshrc
export TELEGRAM_BOT_TOKEN="your-bot-token-here"
```

## Step 6: Initialize the Workspace

```bash
cd ~/HomeCare/be-agents-service
./scripts/workspace/init-workspace.sh beta-appcaire
```

## Step 7: Start OpenClaw

```bash
# Run the onboarding wizard
openclaw onboard --install-daemon

# Or start manually
openclaw start
```

## Step 8: Test

1. Open Telegram
2. Find your bot
3. Send "status" or "overview"
4. You should get a workspace overview!

## Step 9: Set Up LaunchD (Auto-start)

Create a launchd plist to keep OpenClaw running:

```bash
cp ~/HomeCare/be-agents-service/launchd/com.appcaire.openclaw.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

## Troubleshooting

### Bot not responding

```bash
# Check OpenClaw status
openclaw gateway status

# Check logs
openclaw logs

# Verify MCP bridge works
echo '{}' | node ~/HomeCare/be-agents-service/apps/openclaw-bridge/dist/index.js
```

### Workspace not found

```bash
# Verify workspace exists
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/

# Or check config
cat ~/HomeCare/be-agents-service/config/repos.yaml | grep workspace
```

### iCloud files not syncing

```bash
# Force iCloud sync
brctl monitor ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/
```

## Messaging: Telegram only

OpenClaw is configured for **Telegram only**. WhatsApp is not enabled. Using WhatsApp with a personal number would send bot/pairing messages to everyone who messages you; do not add a WhatsApp channel unless you use a dedicated number and `dmPolicy: "allowlist"`.

**If OpenClaw is already running** (e.g. on the Mac mini), remove WhatsApp from the live config so it never sends messages to your contacts:

```bash
# On the machine where OpenClaw runs (e.g. Mac mini)
vim ~/.openclaw/openclaw.json
# Delete the entire "whatsapp" key from "channels", then save.

openclaw gateway restart
```
