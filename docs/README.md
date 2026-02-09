# Agent Service Documentation

**Start here.** All documentation lives under `docs/`. Keep this index evergreen.

---

## Quick Links

| Need | Document |
|------|----------|
| **First-time setup** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| **Mac mini setup** | [FRESH_MAC_MINI_SETUP.md](FRESH_MAC_MINI_SETUP.md) |
| **Mac mini recovery** | [MAC_MINI_RECOVERY.md](MAC_MINI_RECOVERY.md) |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) — one server, one port |
| **Dashboard usage** | [guides/quick-start.md](guides/quick-start.md) |

---

## Document Map

### Setup & Operations

| Doc | Purpose |
|-----|---------|
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Commands, schedules, one-pager |
| [COMPOUND_SETUP_GUIDE.md](COMPOUND_SETUP_GUIDE.md) | Compound workflow setup |
| [FRESH_MAC_MINI_SETUP.md](FRESH_MAC_MINI_SETUP.md) | New Mac mini: zero → running |
| [setup/openclaw-setup.md](setup/openclaw-setup.md) | Telegram/WhatsApp bot via OpenClaw |
| [setup/email-setup.md](setup/email-setup.md) | Email integration |

### Architecture & Reference

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | One server, one dashboard, port 3030 |
| [DASHBOARD_MIGRATION.md](DASHBOARD_MIGRATION.md) | HTML → React migration, troubleshooting |
| [API_ENDPOINTS.md](API_ENDPOINTS.md) | Complete REST API reference |
| [reference/agents.md](reference/agents.md) | All agents, roles, keywords |
| [reference/workflow.md](reference/workflow.md) | Session flow, orchestrator |
| [reference/api-reference.md](reference/api-reference.md) | API endpoints |

### Guides (by role)

| Doc | Purpose |
|-----|---------|
| [guides/quick-start.md](guides/quick-start.md) | Dashboard, first run |
| [guides/po-workflow.md](guides/po-workflow.md) | Product Owner |
| [guides/engineering-guide.md](guides/engineering-guide.md) | Engineering team |
| [guides/marketing-guide.md](guides/marketing-guide.md) | Marketing team |

### Workspace & Integrations

| Doc | Purpose |
|-----|---------|
| [WORKSPACE.md](WORKSPACE.md) | Shared markdown workspace |
| [config/openclaw/README.md](../config/openclaw/README.md) | OpenClaw config |

### Technical Deep-Dives

| Doc | Purpose |
|-----|---------|
| [DATA_FLOW.md](DATA_FLOW.md) | Files → DB → UI flow |
| [DATA_STORAGE_STRATEGY.md](DATA_STORAGE_STRATEGY.md) | What goes in DB vs files |
| [DATABASE_ACCESS.md](DATABASE_ACCESS.md) | DB location, TablePlus, CLI |
| [KANBAN_UX_IMPROVEMENTS.md](KANBAN_UX_IMPROVEMENTS.md) | Kanban board UX design |

---

## Dashboard & Docs

The React dashboard at **http://localhost:3030** is the main UI. All docs live in `docs/`:

- **Quick Start** — Dashboard and first run
- **PO Guide** — Product Owner workflow
- **Engineering** — Engineering commands
- **Marketing** — Campaign management
- **Documentation** — This index

---

## Principles

- **Single source of truth:** One doc per topic. No duplicates.
- **Evergreen:** Avoid dates, "status: complete," implementation logs. Write what *is*, not what *was done*.
- **Dashboard-first:** Docs shown in the dashboard should match what exists.
