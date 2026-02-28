# OpenClaw configuration (Mac mini + Telegram)

Template and instructions for running OpenClaw with the **shared be-agents-service folder** as the agent workspace, so all agent work is saved in the repo and under version control.

**Telegram only.** WhatsApp was removed; do not re-enable.

---

## 1. Use the correct shared folder (Mac mini)

To avoid work being split between `~/.openclaw/workspace` (default) and the shared repo:

1. Copy the template to your OpenClaw config:
   ```bash
   mkdir -p ~/.openclaw
   cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json
   ```

2. Edit `~/.openclaw/openclaw.json`:
   - **Workspace (Mac mini):** The template uses:
     ```json
     "workspace": "/Users/be-agent-service/.openclaw/workspace/be-agents-service"
     ```
     That is the shared folder on the Mac mini. If your Mac mini user is different, replace with your actual path (e.g. `/Users/YOUR_USER/.openclaw/workspace/be-agents-service`).
   - **Other machines:** If the repo is elsewhere (e.g. `~/HomeCare/be-agents-service`), set `agent.workspace` to that path so the agent writes into the repo.

3. Replace placeholders:
   - `YOUR_TELEGRAM_BOT_TOKEN` → token from @BotFather
   - `YOUR_TELEGRAM_USER_ID` → your numeric ID from @userinfobot

   Or use the helper script:
   ```bash
   ./scripts/setup-telegram-openclaw.sh YOUR_TELEGRAM_USER_ID
   ```

4. Restart OpenClaw:
   ```bash
   openclaw gateway restart
   ```

After this, the main agent uses the shared folder and all future work is saved there.

---

## 2. Migrate existing files to the shared folder

If the agent previously used the default workspace (`~/.openclaw/workspace`), migrate those files into the shared folder once:

```bash
cd ~/HomeCare/be-agents-service
./scripts/openclaw-migrate-workspace.sh
```

The script:

- Copies contents from `~/.openclaw/workspace` into the shared folder (see script for the exact target path).
- Skips overwriting existing files in the destination.
- Does not delete the default workspace (you can archive or remove it yourself after verifying).

Then set `agent.workspace` to the shared folder as in step 1 and restart OpenClaw.

---

## 3. Verify

- Send `status` or `overview` to your Telegram bot; it should report the workspace that matches your shared folder.
- Create a small file via the agent and confirm it appears in the shared repo (e.g. under `docs/` or `memory/` in the workspace).

---

## Reference

- OpenClaw config examples: https://docs.openclaw.ai/gateway/configuration-examples  
- Agent workspace: https://docs.openclaw.ai/concepts/agent-workspace  
- Telegram setup in this repo: `scripts/setup-telegram-openclaw.sh`  
- Full Mac mini setup: `docs/MAC_MINI_COMPLETE_SETUP.md`
