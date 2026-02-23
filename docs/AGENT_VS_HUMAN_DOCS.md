# Docs: Agents vs Humans

> Which docs are read by agents/scripts, and which are for humans.

---

## Used by Agents / Scripts

| Doc | Used by |
|-----|---------|
| `LLM_ROUTING.md` | `process-inbox.sh`, `analyze-report.sh` |
| `COMPOUND_SETUP_GUIDE.md` | `scripts/README.md`, `scripts/compound/README.md` |
| `COMPOUND_WORKFLOW.md` | `scripts/compound/README.md` |
| `PRD-MOBILE-APP.md` | Workspace templates (priorities, tasks, inbox) |
| `PRD-TIMEFOLD-INTEGRATION.md` | Workspace templates |
| `reports/*.md` (target repo) | `auto-compound.sh` — reads priorities |
| `CLAUDE.md` (target repos) | `daily-compound-review.sh` — updates learnings |

---

## For Humans

| Doc | Purpose |
|-----|---------|
| `guides/quick-start.md` | Dashboard and first run |
| `guides/engineering-guide.md` | Engineering commands |
| `guides/marketing-guide.md` | Marketing campaigns |
| `guides/po-workflow.md` | Product Owner workflow |
| `guides/ess-fsr-workflow.md` | ESS+FSR feature branch workflow |
| `reference/architecture.md` | System architecture |
| `reference/agents.md` | All agents, roles, keywords |
| `reference/workflow.md` | Session flow, orchestrator |
| `reference/api-reference.md` | API endpoints |
| `reference/priority-integration.md` | Priority integration |
| `QUICK_REFERENCE.md` | Commands, schedules |
| `ARCHITECTURE.md` | One server, one dashboard |
| `DATA_FLOW.md` | Files → DB → UI |
| `API_ENDPOINTS.md` | REST API |
| Setup guides | Mac mini, OpenClaw, email, etc. |

---

## Doc Links in Dashboard (Settings → Commands & Docs)

Links go to `GET /api/file/docs?path=...`. **Requires server on port 3010.**

Paths are relative to `docs/`:
- `guides/ess-fsr-workflow.md` → `docs/guides/ess-fsr-workflow.md`
- `ARCHITECTURE.md` → `docs/ARCHITECTURE.md`

If 404: ensure `yarn workspace server start` is running on 3010.
