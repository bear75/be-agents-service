# Auto-deploy `main` to Mac mini

This repo now includes a GitHub Actions workflow that deploys to the Mac mini whenever `main` is updated:

- Workflow: `.github/workflows/deploy-main-mac-mini.yml`
- Trigger: `push` to `main` (and manual `workflow_dispatch`)
- Remote deploy script: `scripts/deploy-main.sh`

---

## What the deploy script does

On the Mac mini, `scripts/deploy-main.sh`:

1. Fetches `origin/main`
2. Hard-resets local `main` to `origin/main`
3. Runs `./scripts/restart-darwin.sh`
4. Waits for `http://localhost:3010/health` to respond

This ensures the running service is always exactly what is on `main`.

---

## Required GitHub repository secrets

Set these in GitHub → **Settings → Secrets and variables → Actions**:

| Secret | Required | Example |
|---|---|---|
| `MAC_MINI_HOST` | yes | `192.168.50.77` |
| `MAC_MINI_USER` | yes | `be-agent-service` |
| `MAC_MINI_SSH_KEY` | yes | Private key content (ed25519) |
| `MAC_MINI_SSH_PORT` | no | `22` |
| `MAC_MINI_REPO_DIR` | no | `/Users/be-agent-service/HomeCare/be-agents-service` |
| `MAC_MINI_KNOWN_HOSTS` | no (recommended) | Output of `ssh-keyscan -H <host>` |

> If `MAC_MINI_KNOWN_HOSTS` is not set, workflow falls back to `ssh-keyscan` at runtime.

---

## One-time Mac mini setup

1. Ensure repo exists at the path you use (`MAC_MINI_REPO_DIR` or default path).
2. Ensure `scripts/deploy-main.sh` is present (after pull).
3. Ensure these commands work on Mac mini:
   - `git`
   - `yarn`
   - `launchctl`
4. Ensure `com.appcaire.agent-server.plist` is installed if you use launchd restarts.

---

## Test the pipeline

1. Merge/push a commit to `main`.
2. Open GitHub Actions and verify **Deploy main to Mac mini** succeeds.
3. Verify Mac mini service:
   - `curl http://localhost:3010/health`
   - open dashboard on `http://<mac-mini-ip>:3010`

---

## Manual fallback

If Actions is unavailable, run this directly on the Mac mini:

```bash
REPO_DIR=/Users/be-agent-service/HomeCare/be-agents-service \
DEPLOY_BRANCH=main \
/Users/be-agent-service/HomeCare/be-agents-service/scripts/deploy-main.sh
```
