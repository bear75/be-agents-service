# Hannes Simple Setup (90% DARWIN, 10% Hannes)

Use this runbook when you want to keep your main DARWIN flow untouched, while enabling a lightweight Hannes flow on the same Mac mini.

This is the **simple mode**:
- One Mac mini
- One be-agents-service
- Main setup remains DARWIN-first
- Hannes gets his own markdown workspace and repo mapping
- Compound for Hannes is triggered manually by you

---

## What this setup solves

- Hannes can maintain his own:
  - `priorities.md`
  - `input/`
  - `memory/`
  - `tasks.md`, `follow-ups.md`, check-ins
- Hannes code target is his repo: `hannes453/strength-stride-coach`
- Your primary DARWIN setup remains the default for daily operations

---

## What this setup does NOT do

- It does **not** provide hard Telegram runtime isolation between users on one shared default gateway.
- It does **not** create a second server.

If later needed, move to "isolated mode" with a separate Telegram bot/profile for Hannes.

---

## Configuration used

In `config/repos.yaml`:

- repo key: `hannes-projects`
- path: `~/HomeCare/strength-stride-coach`
- workspace: `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/hannes-space`
- github: `hannes453/strength-stride-coach`

---

## Step-by-step (Mac mini local terminal)

Run all commands on the Mac mini inside `~/HomeCare/be-agents-service`.

### 1) Pull latest config/scripts

```bash
cd ~/HomeCare/be-agents-service
git checkout main
git pull origin main
```

### 2) Bootstrap Hannes repo + workspace

```bash
./scripts/setup-hannes-simple.sh
```

What this does:
- clones `hannes453/strength-stride-coach` to `~/HomeCare/strength-stride-coach` (if missing)
- ensures `reports/`, `logs/`, `tasks/` exist in that repo
- initializes `AgentWorkspace/hannes-space` structure and templates

### 3) (Optional) update allowFrom + send Telegram tests to both users

```bash
./scripts/setup-hannes-simple.sh \
  --owner-id 8399128208 \
  --hannes-id 7604480012 \
  --send-telegram-test
```

This will:
- merge both IDs into `~/.openclaw/openclaw.json` `channels.telegram.allowFrom`
- send a test message to each provided ID

### 4) Verify workspace mapping

```bash
curl -s http://localhost:3010/api/workspace/hannes-projects/status | jq .
```

Expected path:
- `.../AgentWorkspace/hannes-space`

### 5) Add Hannes priorities

Edit:

```bash
open "$HOME/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/hannes-space/priorities.md"
```

### 6) Trigger coding for Hannes (manual, recommended in simple mode)

```bash
cd ~/HomeCare/be-agents-service
./scripts/compound/auto-compound.sh hannes-projects
```

---

## Telegram in simple mode

You may keep one shared bot and include both IDs in `allowFrom`.

However, with one shared default gateway/workspace, Telegram context is not fully hard-isolated per user. For strict isolation later:
- create a second bot/profile for Hannes
- bind that profile to `hannes-space`

---

## Operator checklist

- [ ] `config/repos.yaml` has `hannes-projects` pointing to `strength-stride-coach` + `hannes-space`
- [ ] `~/HomeCare/strength-stride-coach` exists and is accessible
- [ ] `AgentWorkspace/hannes-space` exists and contains workspace files
- [ ] `api/workspace/hannes-projects/status` resolves to `hannes-space`
- [ ] Hannes priorities are in `hannes-space/priorities.md`
- [ ] You can run `auto-compound.sh hannes-projects` successfully

