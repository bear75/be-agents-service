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

OpenClaw is configured for **Telegram only**.

### Stop OpenClaw replying on WhatsApp

If the gateway is still replying on WhatsApp ("OpenClaw: access not configured", pairing codes), remove WhatsApp from the live config and restart:

```bash
cd ~/HomeCare/be-agents-service
git pull
./scripts/openclaw-remove-whatsapp-channel.sh
openclaw gateway restart
```

Use `OPENCLAW_HOME=/Users/bjornevers_MacPro` if the config lives in another user's home. After this, WhatsApp gets no reply.

### Telegram not replying after removing WhatsApp

If Telegram stopped replying after you ran the remove-WhatsApp steps:

1. **Ensure the gateway uses `~/.openclaw` and that Telegram is in that config**
   - If you ran `remove-clawdbot-agent-dir.sh`, the gateway now uses only `~/.openclaw`. Check:
   ```bash
   cat ~/.openclaw/openclaw.json | grep -A5 '"channels"'
   ```
   You should see a `"telegram"` block with `botToken` and `allowFrom`. If `channels` is missing or empty, restore from the template and add your Telegram bot token and user ID:
   ```bash
   cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json
   # Edit: set TELEGRAM_BOT_TOKEN / allowFrom (your user ID from @userinfobot)
   ```

2. **Ensure auth is in `~/.openclaw`** (so the bot can call Claude)
   - After removing `~/.clawdbot`, the gateway uses only `~/.openclaw`. Auth must be in `~/.openclaw/agents/main/agent/` (e.g. `auth-profiles.json` or `auth.json`). If that directory is missing or empty, copy auth from your `.clawdbot` backup:
   ```bash
   mkdir -p ~/.openclaw/agents/main/agent
   cp ~/.clawdbot.bak.*/agents/main/agent/auth-profiles.json ~/.openclaw/agents/main/agent/
   # or auth.json if that's what you have
   ```
   If you never had auth under `~/.openclaw` and don't have a backup, set up the agent again (e.g. `openclaw agents add main` and add your API keys).

3. **Restart the gateway** after any config or auth change:
   ```bash
   openclaw gateway restart
   # If using launchd:
   launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist
   launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist
   ```

4. **Check logs** for errors:
   ```bash
   openclaw logs
   ```

**If OpenClaw is managed by launchd** (e.g. `com.appcaire.openclaw.plist`), it has `KeepAlive true`, so killing the process just makes launchd restart it. To stop it and keep it stopped:

```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

Then run the scripts above (remove WhatsApp channel, remove `.clawdbot` if you want to stop the [clawdbot] error), then either leave it unloaded or start again with:

```bash
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

If you see **[clawdbot]** error replies (e.g. "No API key found"), the gateway may be using the legacy config under `~/.clawdbot/`. To make that channel dead (no reply, no error):

**On the Mac mini**, as the user in the error path (or with `OPENCLAW_HOME=/Users/bjornevers_MacPro`):

```bash
cd ~/HomeCare/be-agents-service
git pull
./scripts/remove-clawdbot-agent-dir.sh
openclaw gateway stop
rm -rf ~/.openclaw/agents/main/agent/.channel-state 2>/dev/null
openclaw gateway start
```

Use `OPENCLAW_HOME=/Users/bjornevers_MacPro` before the script if you're not logged in as that user.

### Optional: fix the error and allow replies

If you **want** the bot to reply, copy auth into `.clawdbot` instead of removing it:

```bash
OPENCLAW_HOME=/Users/bjornevers_MacPro ./scripts/sync-openclaw-auth-to-clawdbot.sh
openclaw gateway restart
```
