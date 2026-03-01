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
- `scripts/manage-hannes-dashboard-launchd.sh`
- `scripts/openclaw/manage-gateway-launchd.sh`
- `scripts/openclaw/setup-dual-launchd.sh`

Also added env-aware config/DB support:

- `REPOS_CONFIG_PATH` for config source override
- `AGENT_DB_PATH` for isolated SQLite file
- `AGENT_JOBS_DIR` for isolated job metadata/log files
- `PLAN_DOCS_ROOT` + `FILE_ACCESS_ALLOWED_PATHS` to prevent reading DARWIN plans/docs

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
- install dedicated launchd gateway services with separate labels:
  - `com.appcaire.openclaw-darwin` (you)
  - `com.appcaire.openclaw-hannes` (Hannes)
- send Telegram test (unless `--no-test`)

### 2) Start isolated Hannes dashboard/API

```bash
./scripts/restart-hannes-dashboard.sh
```

Or install as persistent launchd service:

```bash
./scripts/manage-hannes-dashboard-launchd.sh install
```

Runs with:
- `PORT=3011`
- `REPOS_CONFIG_PATH=config/repos.hannes.yaml`
- `AGENT_DB_PATH=.compound-state/agent-service-hannes.db`
- `AGENT_JOBS_DIR=.compound-state/running-jobs-hannes`
- `OPENCLAW_CONFIG_PATH=~/.openclaw-hannes/openclaw.json`
- `OPENCLAW_LAUNCHD_LABEL=com.appcaire.openclaw-hannes`
- `DISABLED_DASHBOARD_MODULES=plans,schedules,settings`
- `APP_DISPLAY_NAME=Hannes AI`

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

## Managing gateways without cross-stop risk

Use profile-specific commands only:

```bash
./scripts/openclaw/manage-gateway-launchd.sh darwin status
./scripts/openclaw/manage-gateway-launchd.sh darwin restart

./scripts/openclaw/manage-gateway-launchd.sh hannes status
./scripts/openclaw/manage-gateway-launchd.sh hannes restart
```

Install both in one command:

```bash
./scripts/openclaw/setup-dual-launchd.sh
```

Do **not** use generic `openclaw gateway restart` for dual-stack mode, because it targets shared legacy labels and can switch the wrong config.

---

## Reboot behavior (Mac mini)

If services are installed once via launchd, they auto-start after reboot:

- `com.appcaire.agent-server` (Darwin dashboard/API on `3010`)
- `com.appcaire.hannes-dashboard` (Hannes dashboard/API on `3011`)
- `com.appcaire.openclaw-darwin` (Darwin gateway on `18789`)
- `com.appcaire.openclaw-hannes` (Hannes gateway on `19001`)

Install/repair all boot services:

```bash
yarn stack:boot:install
```

---

## Yarn runtime commands (recommended)

```bash
# 1) Restart ALL (both gateways + both dashboards)
yarn stack:all

# 2) Restart Darwin only (gateway + dashboard)
yarn stack:darwin

# 3) Restart Hannes only (gateway + dashboard)
yarn stack:hannes

# Status (terminal)
yarn stack:status
yarn stack:status:darwin
yarn stack:status:hannes

# Status via Telegram (uses TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)
yarn stack:status:telegram
```

---

## Notes

- Primary DARWIN stack remains unchanged on port `3010`.
- Hannes stack is intentionally separate on port `3011`.
- Both stacks share the same repository code and prompts.
- Hannes dashboard data isolation is enforced by separate repo config, DB, jobs dir, OpenClaw config path, and docs/file access scope.
- In Hannes mode, Plans/Schedules/Settings are disabled in both UI and API (`403`) to avoid cross-workspace leakage.
- In Hannes mode, job start API is restricted to `hannes-projects` only.
