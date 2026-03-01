# Hannes Isolated Stack (repo + workspace + dashboard + telegram)

This setup gives Hannes a fully isolated runtime on the same Mac mini while reusing the same `be-agents-service` codebase (workflows, prompts, agents, scripts).

## Isolation goals

- **Repo:** `~/HomeCare/strength-stride-coach`
- **Workspace:** `AgentWorkspace/hannes-space`
- **Dashboard/API:** `http://localhost:3011`
- **Telegram runtime:** separate OpenClaw config/state (`~/.openclaw-hannes`)
- **Shared codebase:** still uses `~/HomeCare/be-agents-service`

---

## New components added

- `config/repos.hannes.yaml` (isolated repo/workspace map)
- `scripts/start-hannes-dashboard.sh`
- `scripts/restart-hannes-dashboard.sh`
- `scripts/verify-hannes-stack.sh`
- `scripts/setup-hannes-isolated-openclaw.sh`
- `scripts/setup-hannes-isolated-stack.sh`

Also added env-aware config/DB support:

- `REPOS_CONFIG_PATH` for config source override
- `AGENT_DB_PATH` for isolated SQLite file

---

## Step-by-step (Mac mini)

From `~/HomeCare/be-agents-service`:

```bash
git checkout main
git pull origin main
```

### 1) Bootstrap isolated Hannes stack

```bash
source ~/.config/caire/env
./scripts/setup-hannes-isolated-stack.sh \
  --hannes-id 7604480012 \
  --bot-token "<HANNES_TELEGRAM_BOT_TOKEN>"
```

This will:
- initialize/verify Hannes repo + workspace
- configure isolated OpenClaw runtime at `~/.openclaw-hannes`
- send Telegram test (unless `--no-test`)

### 2) Start isolated Hannes dashboard/API

```bash
./scripts/restart-hannes-dashboard.sh
```

Runs with:
- `PORT=3011`
- `REPOS_CONFIG_PATH=config/repos.hannes.yaml`
- `AGENT_DB_PATH=.compound-state/agent-service-hannes.db`

### 3) Verify isolated stack

```bash
./scripts/verify-hannes-stack.sh --send-telegram-test
```

If test says `chat not found`, Hannes must open the new bot once and press `/start`, then rerun verification.

### 4) Open Hannes dashboard

- `http://localhost:3011`

---

## Running workflows in isolated mode

Use same workflow scripts, but with Hannes config:

```bash
REPOS_CONFIG_PATH=config/repos.hannes.yaml ./scripts/compound/auto-compound.sh hannes-projects
REPOS_CONFIG_PATH=config/repos.hannes.yaml ./scripts/compound/check-status.sh hannes-projects
```

If triggered via the isolated dashboard API on port `3011`, those env vars are inherited automatically.

---

## Notes

- Primary DARWIN stack remains unchanged on port `3010`.
- Hannes stack is intentionally separate on port `3011`.
- Both stacks share the same repository code and prompts.
