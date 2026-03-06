# Deploy workflow: self-hosted runner on Mac mini

The **Deploy main to Mac mini** workflow runs on a **self-hosted runner** on the Mac mini (no SSH, no public IP).

## 1. Install the runner on the Mac mini

1. Open the repo on GitHub → **Settings** → **Actions** → **Runners**.
2. Click **New self-hosted runner**.
3. Choose **macOS** and the architecture (e.g. **ARM64** for M1/M2).
4. Copy and run the commands shown (download, configure, install, start) in Terminal on the Mac mini.

Example (replace with the token and URL from GitHub):

```bash
mkdir actions-runner && cd actions-runner
curl -o actions-runner-osx-arm64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-arm64-2.311.0.tar.gz
tar xzf ./actions-runner-osx-arm64-2.311.0.tar.gz
./config.sh --url https://github.com/YOUR_ORG/be-agents-service --token YOUR_TOKEN
./run.sh
```

To run as a service so it survives logout:

```bash
./svc.sh install
./svc.sh start
```

5. When asked for runner group, press Enter (default). When asked for name, e.g. `mac-mini` or leave default.
6. The runner will show under **Settings → Actions → Runners** with labels like `self-hosted`, `macOS`, `ARM64` (or `X64`).

## 2. GitHub secrets (optional)

- **MAC_MINI_REPO_DIR** – Only if the repo is not at `/Users/be-agent-service/HomeCare/be-agents-service`. Otherwise leave unset.

You do **not** need `MAC_MINI_HOST`, `MAC_MINI_USER`, or `MAC_MINI_SSH_KEY` for this workflow.

## 3. Trigger

- **Automatic:** push to `main`.
- **Manual:** Actions → **Deploy main to Mac mini** → **Run workflow**.

---

## 4. Troubleshooting: runner not working

### Workflow never runs / “No runner available”

- **Runner offline:** On the Mac mini, the runner process must be running.
  - If you used the service: `cd ~/actions-runner && ./svc.sh status` (or `sudo ./svc.sh status`). If stopped: `./svc.sh start`.
  - If you run manually: `./run.sh` must be running in a Terminal (or under `screen`/`tmux`).
- **Wrong repo or token:** The runner was configured with `./config.sh --url https://github.com/OWNER/REPO --token TOKEN`. It only picks up jobs for that repo. Re-run config (or add a new runner) from **Settings → Actions → Runners** for the correct repo.
- **Labels:** The workflow uses `runs-on: [self-hosted, macOS]`. In **Settings → Actions → Runners**, the runner must show labels including `self-hosted` and `macOS` (and usually `ARM64` or `X64`). If you created a different runner group, either add the same labels or change the workflow to use that group.

### Workflow runs but job fails

- **Check the Actions run:** Open the failed run and read the **Deploy latest main** step log.
- **Common causes:**
  - **“Repository not found at $REPO_DIR”** – Set secret **MAC_MINI_REPO_DIR** to the repo path on the Mac mini (e.g. `/Users/be-agent-service/HomeCare/be-agents-service`), or ensure the default path exists and has a `.git` directory.
  - **“git is required” / “yarn is required”** – The runner’s `PATH` may not include git/yarn. `deploy-main.sh` prepends Homebrew paths; if installs are elsewhere, set `PATH` in the runner’s environment (e.g. in the service or a wrapper script).
  - **“Service did not become healthy”** – The script runs `restart-darwin.sh` then polls `HEALTH_URL` (default `http://localhost:3010/health`). If the server listens on another port, set the **HEALTH_URL** secret (e.g. `http://localhost:3030/health`). On the Mac mini, run `curl -s http://localhost:3010/health` after a manual deploy to confirm the server responds.

### Quick checks on the Mac mini

```bash
# Runner process (if using svc)
~/actions-runner/svc.sh status

# Repo and deploy script
ls -la /Users/be-agent-service/HomeCare/be-agents-service/.git
ls -la /Users/be-agent-service/HomeCare/be-agents-service/scripts/deploy-main.sh

# Manual deploy (same as the workflow step)
export REPO_DIR=/Users/be-agent-service/HomeCare/be-agents-service
"$REPO_DIR/scripts/deploy-main.sh"

# Health after deploy
curl -s http://localhost:3010/health
```
