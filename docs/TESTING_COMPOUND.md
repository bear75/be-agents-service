# Testing the compound run (strategy + engineering + marketing)

## Quick test with the SEO blog priority

A ready-made priority is in **beta-appcaire**: it asks for an SEO blog page on www.caire.se about algorithms and maths for optimal efficiency and continuity, using input/memory from the darwin folder.

### 1. Ensure beta-appcaire is in config

`config/repos.yaml` includes **beta-appcaire** with path `~/HomeCare/beta-appcaire`, `priorities_dir: reports/`, and optional workspace (DARWIN) for shared input/memory.

### 2. Priority file used

- **Stored in darwin folder:** `AgentWorkspace/DARWIN/priorities-2026-03-01.md`  
- **#1 item:** SEO blog page for www.caire.se (apps/website) about algorithms and maths for optimal efficiency and continuity; use darwin workspace `input/` and `memory/` when drafting.

When the repo (e.g. beta-appcaire) has its workspace set to DARWIN, compound looks for priorities in the workspace: it uses the **latest** `priorities-*.md` (by modification time) if present, otherwise `priorities.md`. So `priorities-2026-03-01.md` in DARWIN is used automatically when you run compound for beta-appcaire.

### 3. Run compound

**From the dashboard**

1. Open the agent dashboard (e.g. http://localhost:3030).
2. Go to **Run** → **Compound**.
3. Choose **Target repo:** `beta-appcaire`.
4. Click **Start** (or equivalent).

**From the terminal**

```bash
cd ~/HomeCare/be-agent-service
./scripts/compound/auto-compound.sh beta-appcaire
```

### 4. What runs

1. **Strategy** – Strategy brief from the priority (optional).
2. **Engineering** – Orchestrator + all specialists (backend, frontend, infra, db-architect, docs, levelup, ux, verification). They will create PRD, implement the new page in `apps/website`, and run verification.
3. **Marketing** – Jarvis + all marketing agents (SEO, content, design, etc.) on the same priority for SEO and copy.

When a workspace is configured for the repo, `WORKSPACE_PATH`, `WORKSPACE_INPUT`, and `WORKSPACE_MEMORY` are exported so agents can use the darwin `input/` and `memory/` folders.

### 5. Where to look for results

- **Session and tasks:** Dashboard → **Work** (same session for strategy, engineering, marketing).
- **Logs:** `be-agent-service/logs/orchestrator-sessions/<session_id>/`.
- **PR:** Created in beta-appcaire from the feature branch (e.g. `feature/seo-blog-...`).
- **Strategy brief:** `be-agent-service/.compound-state/<session_id>/strategy-brief.md` (if strategy phase ran).

### 6. Priority in darwin folder

The SEO blog priority is stored in **darwin** only: `AgentWorkspace/DARWIN/priorities-2026-03-01.md`. Compound uses the latest `priorities-*.md` in the workspace when the repo has workspace enabled, so no copy in `beta-appcaire/reports/` is needed.
