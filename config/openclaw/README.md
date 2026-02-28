# OpenClaw configuration (Telegram + shared human–AI workspace)

**There can only be ONE shared folder** for Cursor, compound learning, and Telegram. OpenClaw **must** use that same folder. If Telegram/OpenClaw writes to a different path, you get two folders: human instructions and agent memory in one place, compound priorities and learnings in another — split state and confusion.

**OpenClaw’s `agent.workspace` must point at the SAME path** that compound uses (`config/repos.yaml` → `repos.<name>.workspace.path`) and that you use with Cursor. Not the be-agents-service repo; not a second “OpenClaw workspace”.

**Telegram only.** WhatsApp was removed; do not re-enable.

---

## 1. Set workspace to THE shared folder (one folder for everything)

Under **iCloud/AgentWorkspace/** you have one folder per context (e.g. **default**, or a repo/project name). That folder is the **single source of truth**: inbox, memory, priorities, agent-reports. Cursor, compound scripts, and Telegram/OpenClaw all read and write there.

**Wrong:** OpenClaw using a different path (e.g. `~/.openclaw/workspace` or the be-agents-service repo) — then Telegram updates “its” memory in one place and compound uses another. Two folders = broken.

**Right:** Set `agent.workspace` to the **exact same** AgentWorkspace path that `config/repos.yaml` uses for that context (e.g. `repos.beta-appcaire.workspace.path`), or `AgentWorkspace/default` if you use one generic workspace.

1. Copy the template:
   ```bash
   mkdir -p ~/.openclaw
   cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json
   ```

2. Edit `~/.openclaw/openclaw.json` and set `agent.workspace` to the **same** path used by compound and Cursor. For example, copy the path from `config/repos.yaml` for your repo (`repos.<name>.workspace.path`), or:
   - **Generic:** `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/default`
   - **Per-repo/project:** same as in `repos.yaml` (e.g. `.../AgentWorkspace/beta-appcaire`).
   - **Mac mini:** Same iCloud path if synced; or the same local path that compound uses.

3. Replace Telegram placeholders:
   - `YOUR_TELEGRAM_BOT_TOKEN` → from @BotFather  
   - `YOUR_TELEGRAM_USER_ID` → from @userinfobot  

   Or run: `./scripts/setup-telegram-openclaw.sh YOUR_TELEGRAM_USER_ID`

4. Restart OpenClaw: `openclaw gateway restart`

---

## 2. Migrate if the agent was writing into the repo

If you previously had `agent.workspace` pointing at be-agents-service, the agent may have created or changed files under that repo (e.g. docs, memory). To fix:

1. Set `agent.workspace` to the shared folder (step 1 above).
2. If you want to keep any of the agent-created content from the repo, copy it into the correct place in the shared folder (e.g. `memory/`, `agent-reports/`) and then remove or revert the copies from the repo.
3. Do **not** use `scripts/openclaw-migrate-workspace.sh` to move *from* the default `~/.openclaw/workspace` *into* the repo — that script was for an old setup. Use it only to copy from `~/.openclaw/workspace` **into** your AgentWorkspace folder (e.g. `AgentWorkspace/default` or any project folder) if that’s where you want the files.

---

## 3. Verify

- Send `status` or `overview` to the Telegram bot; it should report the workspace path that is your **AgentWorkspace** folder (e.g. default or your project name).
- Add something via the agent and confirm it appears in that folder (e.g. `inbox.md`, `memory/`, or `agent-reports/`), not inside be-agents-service.

---

## Reference

- OpenClaw: https://docs.openclaw.ai/gateway/configuration-examples  
- Workspace layout: `docs/WORKSPACE.md` and `docs/FOLDER_STRUCTURE.md`
