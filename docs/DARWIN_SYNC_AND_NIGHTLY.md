# Darwin Sync and Nightly Compound

How session results get from the nightly compound run into the Darwin workspace (AgentWorkspace/DARWIN), and how to find out why they didn’t.

---

## Flow: compound → Darwin

1. **Nightly run (Mac mini)**  
   LaunchD runs `auto-compound.sh <repo>` at 23:00. The plist uses repo **appcaire** and writes stdout/stderr to the **target repo’s** `logs/auto-compound.log` (e.g. `appcaire/logs/auto-compound.log` on the Mac mini).

2. **Priorities**  
   Compound reads the latest priority report from the **target repo** (for appcaire: `docs_2.0/recurring-visits/huddinge-package/*.md` or workspace/reports). If none found, script exits **before** any session state or sync.

3. **Session state**  
   Session state is created only after the **orchestrator** runs (it uses `state-manager.sh` and writes under `be-agent-service/.compound-state/<SESSION_ID>/` with `orchestrator.json`, etc.). If the run exits earlier (no priority, PRD not created, orchestrator not started, or crash), there is no session directory.

4. **Sync to workspace**  
   At the **end** of `auto-compound.sh` (after PR creation), the script calls:
   - `sync-to-workspace.sh <REPO_NAME>`
   Sync does:
   - Resolves workspace path from `config/repos.yaml` for that repo (appcaire → DARWIN).
   - Looks for the **latest** session in `be-agent-service/.compound-state/session-*`.
   - If none, exits with “No session state found” (no write to Darwin).
   - Otherwise writes:
     - `agent-reports/latest-session.md` and `agent-reports/session-<timestamp>.md`
     - Appends one line to `check-ins/daily/<YYYY-MM-DD>.md` (today in the **runner’s** timezone).

5. **Where Darwin is**  
   The workspace path in config is `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/DARWIN`. On the **Mac mini** that path must exist and be the same iCloud folder so that what sync writes there appears in your Darwin folder after iCloud sync.

So **Darwin gets updated only if**:

- Compound actually runs on the Mac mini.
- It finds a priority and gets at least to the point where the orchestrator creates session state.
- The script reaches the sync call at the end (after PR creation).
- `sync-to-workspace.sh` finds a session in `be-agent-service/.compound-state/`.
- The workspace path for the repo points to the DARWIN folder that iCloud syncs to your Mac.

---

## Why Darwin might have no update

| Cause | What to check on the Mac mini |
|-------|-------------------------------|
| Nightly didn’t run | LaunchD loaded? `launchctl list \| grep appcaire`. Plist paths correct (WorkingDirectory, ProgramArguments, StandardOutPath)? |
| No priority found | Target repo has a report where compound looks? (e.g. appcaire: `docs_2.0/recurring-visits/huddinge-package/*.md` or workspace). Check `logs/auto-compound.log` for “No priorities found”. |
| Exited before orchestrator | Log for errors after “Priority:” / “Branch:” (e.g. PRD step, branch creation). No session state → sync has nothing to send. |
| Session state missing | `ls -la be-agent-service/.compound-state/session-*` — if empty, orchestrator never created state or run failed before that. |
| Sync not run or failed | Sync is called with `2>/dev/null`; errors are hidden. Run by hand: `sync-to-workspace.sh appcaire` and check for “[sync]” messages and that `agent-reports/` and `check-ins/daily/` are updated. |
| Wrong workspace path | On the Mac mini, does `config/repos.yaml` have the same DARWIN path and is that path the iCloud-synced folder? If the path is wrong or different account, sync writes somewhere that doesn’t match your Darwin. |

---

## Checklist on the Mac mini (find out what happened)

Run from the **be-agent-service** root (adjust paths if your clone lives elsewhere):

```bash
# 1. LaunchD
launchctl list | grep appcaire
# If com.appcaire.auto-compound is missing, load the plist.

# 2. Last run log (target repo; plist uses appcaire)
tail -200 /Users/be-agent-service/HomeCare/appcaire/logs/auto-compound.log
# Or wherever your appcaire repo and logs_dir point.

# 3. Session state (must exist for sync to write anything)
ls -la .compound-state/session-*/
# If empty: run never reached orchestrator or state wasn’t written.

# 4. Manual sync (see if Darwin would get updated from current state)
./scripts/workspace/sync-to-workspace.sh appcaire
# Then check AgentWorkspace/DARWIN/agent-reports/ and check-ins/daily/ on that machine (and after iCloud sync, on your Mac).
```

---

## Reference: where sync writes

- **Script:** `scripts/workspace/sync-to-workspace.sh`
- **Resolves workspace:** `scripts/workspace/resolve-workspace.sh` (uses `config/repos.yaml` → `workspace.path` for the repo, e.g. appcaire → DARWIN).
- **Writes:**  
  - `$WORKSPACE_PATH/agent-reports/latest-session.md`  
  - `$WORKSPACE_PATH/agent-reports/session-<timestamp>.md`  
  - Append to `$WORKSPACE_PATH/check-ins/daily/$(date +%Y-%m-%d).md`
- **Requires:** At least one directory under `be-agent-service/.compound-state/session-*` (with orchestrator state from a completed or partial run).
