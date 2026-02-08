# ESS + FSR Integration: Agent Workflow Guide

> **Project:** CAIRE dual-model scheduling (ESS + FSR)  
> **Branch:** `feature/ess-fsr-integration`  
> **Config:** `config/repos.yaml` → `feature_projects.ess-fsr-integration`

---

## Overview

ESS+FSR work uses a **long-lived feature branch**. PRs merge into `feature/ess-fsr-integration`, not `main`. Merge to `main` happens only when the full project is ready for release.

---

## Quick Start

### Manual Job (Dashboard)

1. Go to **Engineering** page: http://localhost:3030/engineering.html
2. **Priority File:** `reports/ess-fsr/priorities-2026-02-10.md` (or today's date)
3. **Branch Name:** `feature/ess-fsr-sprint1-night1` (unique per task)
4. **Base Branch:** `feature/ess-fsr-integration` ← **Required for ESS+FSR**
5. Click **Start Engineering Job**

### Branch Naming

- **Task branch:** `feature/ess-fsr-sprint{N}-night{N}` or `feature/ess-fsr-{date}`
- **Base branch:** Always `feature/ess-fsr-integration` for this project

---

## Daily Workflow (7-day sprints)

| Day | Priority File | Task Branch | Base Branch |
|-----|---------------|-------------|-------------|
| Mon | reports/ess-fsr/priorities-2026-02-10.md | feature/ess-fsr-sprint1-night1 | feature/ess-fsr-integration |
| Tue | reports/ess-fsr/priorities-2026-02-11.md | feature/ess-fsr-sprint1-night2 | feature/ess-fsr-integration |
| ... | ... | ... | ... |

**PO morning routine:**
1. Review overnight PR (target: `feature/ess-fsr-integration`)
2. Merge if approved: `gh pr merge <number> --squash`
3. Next night's agent will pull latest `feature/ess-fsr-integration` before creating task branch

---

## Configuration

### config/repos.yaml

```yaml
feature_projects:
  ess-fsr-integration:
    base_branch: feature/ess-fsr-integration
```

### Orchestrator

When `BASE_BRANCH` env is set:
- Checkout base branch (or create from main if first run)
- Create task branch from base
- PR targets base branch, not main

---

## Priority File Location

```
beta-appcaire/reports/ess-fsr/
├── priorities-2026-02-10.md  # Sprint 1 Night 1
├── priorities-2026-02-11.md  # Sprint 1 Night 2
├── priorities-2026-02-12.md
├── ...
└── priorities-2026-02-16.md  # Sprint 1 Night 7
```

---

## Reference

- **Project Plan:** `beta-appcaire/docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md`
- **Architecture:** `beta-appcaire/docs/docs_2.0/09-scheduling/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md`
- **PO Workflow:** `docs/guides/po-workflow.md`
