# OpenClaw config (Mac mini / shared workspace)

Template for `~/.openclaw/openclaw.json`. Uses the **newer OpenClaw schema** (`agents.list`, `bindings`, etc.) and Telegram-only (no WhatsApp).

## Important: workspace is per-agent

The live config uses **`agents.list`**, not a top-level `agent.workspace`. The **main** agent must have a `workspace` field in `agents.list` for new work to go to the shared folder.

In the template, the main agent already has:
```json
"workspace": "/Users/be-agent-service/.openclaw/workspace/be-agents-service"
```
If you copy an existing config that has no `workspace` for the default agent, add it to that agent in `agents.list`, e.g.:
```json
{
  "id": "main",
  "default": true,
  "name": "Main Agent",
  "workspace": "/Users/be-agent-service/.openclaw/workspace/be-agents-service",
  "agentDir": "~/.openclaw/agents/main/agent"
}
```

## Quick setup

1. **Copy the config**
   ```bash
   mkdir -p ~/.openclaw
   cp /path/to/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json
   ```

2. **Set the workspace** (if different)
   - Edit `~/.openclaw/openclaw.json` and set the **main** agent's `workspace` in `agents.list` to your shared folder (e.g. `/Users/be-agent-service/.openclaw/workspace/be-agents-service`).

3. **Replace placeholders**
   - `YOUR_TELEGRAM_USER_ID` → your numeric Telegram ID (from @userinfobot).
   - `${TELEGRAM_BOT_TOKEN}` → your bot token, or rely on `TELEGRAM_BOT_TOKEN` in `~/.config/caire/env` and the gateway plist.

4. **Optional: migration script**
   - If you need to move an existing workspace into the shared folder, run:
     ```bash
     ./scripts/openclaw-migrate-workspace.sh
     ```
   - You can skip this if you've already moved everything.

5. **Apply and restart**
   ```bash
   openclaw gateway restart
   ```
   New agent work will use the workspace path set on the main agent in `agents.list`.

---

## On the Mac mini (after moving to shared folder)

- Ensure **`~/.openclaw/openclaw.json`** has the **main** agent's `workspace` in `agents.list` pointing to your shared folder (or use this template).
- Run: **`openclaw gateway restart`**.
- After that, new agent work will go into the shared folder.

See also: `scripts/setup-telegram-openclaw.sh` for Telegram user ID and token setup.
