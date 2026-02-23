# OpenClaw Sandbox Setup

Guide for setting up an isolated OpenClaw + Telegram sandbox for someone who should **not** have access to the be-agents-service repo. Example: a family member (e.g. son) with their own workspace, bot, and iCloud/GitHub folder. Telegram only.

## Overview

- **Isolated:** Own bot, own workspace, no repo access
- **Same MCP bridge:** Shared executable (no source code needed)
- **Tools that work:** inbox, priorities, tasks, check-ins, follow-ups, process_input_docs
- **Tools that degrade:** get_teams, get_sessions, get_stats (return "could not fetch")
- **Tools that fail safely:** trigger_compound (script not present in sandbox)

## Prerequisites

- Mac with Node.js 22+
- OpenClaw installed: `curl -fsSL https://openclaw.ai/install.sh | bash`
- iCloud Drive (or any folder for workspace)

## Setup Steps

### 1. Create workspace folder

```bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/son-sandbox
```

Or use a shared Family iCloud folder if the sandbox user has their own device.

### 2. Initialize workspace (parent runs once)

From be-agents-service:

```bash
./scripts/workspace/init-workspace.sh son-sandbox "/full/path/to/AgentWorkspace/son-sandbox"
```

Replace the path with the actual full path to the sandbox folder.

### 3. Build and copy bridge (parent runs)

```bash
./scripts/sandbox/build-bridge-for-sandbox.sh
# Or custom destination:
./scripts/sandbox/build-bridge-for-sandbox.sh /path/to/destination
# Skip build (use existing dist if build OOMs):
./scripts/sandbox/build-bridge-for-sandbox.sh --skip-build /path/to/destination
```

Default destination: `~/Shared/agent-workspace-bridge`

### 4. Sandbox user: Create Telegram bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, name it (e.g. "My Workspace Bot")
3. Copy the bot token
4. Search for `@userinfobot`, send any message, copy your numeric user ID

### 5. Sandbox user: Create OpenClaw config

1. Copy the template:
   ```bash
   mkdir -p ~/.openclaw
   cp /path/to/be-agents-service/config/openclaw/sandbox-openclaw.json ~/.openclaw/openclaw.json
   ```

2. Edit `~/.openclaw/openclaw.json`:
   - Replace `REPLACE_WITH_TELEGRAM_USER_ID` with your numeric ID
   - Remove any non-Telegram channel section if present (Telegram only)
   - Set `systemPromptFile` to full path of `config/openclaw/son-system-prompt.md`
   - Set `args` to the full path of the bridge: `["/full/path/to/Shared/agent-workspace-bridge/dist/index.js"]`
   - Set `WORKSPACE_PATH` to your sandbox workspace path

3. Set environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   # Add to ~/.zshrc or ~/.config/caire/env
   ```

### 6. Start OpenClaw

```bash
openclaw start
```

Or use launchd for auto-start (see config/openclaw/README.md).

## Shared Gateway (Parent Runs OpenClaw)

Parent uses **Telegram only**. Sandbox user (e.g. Hannes) uses Telegram:

- **default** (parent): Main agent via Telegram only.
- **hannes**: Hannes agent (Darwin) via Telegram. Hannes talks to Darwin on his bot.

**Compound:** Hannes kan säga "run compound" — Darwin kör **endast** på `hannes-projects`. Se `config/repos.yaml`.

**Restart efter ändringar:** `openclaw gateway restart`

## Config Template Reference

See [config/openclaw/sandbox-openclaw.json](../config/openclaw/sandbox-openclaw.json).

**Important:** Use `WORKSPACE_PATH` only. Omit `WORKSPACE_CONFIG`, `WORKSPACE_REPO`, and `AGENT_API_URL`. That isolates the sandbox from the main setup.

For compound access to Hannes's own repos, add `WORKSPACE_ALLOWED_REPOS` (comma-separated repo names). The bridge restricts `trigger_compound` to those repos only.

## GitHub (optional)

The sandbox user can create their own GitHub repo, put their workspace folder in it, and push for versioning and backup. iCloud sync is sufficient for a prototype.
