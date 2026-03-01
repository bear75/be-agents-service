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
