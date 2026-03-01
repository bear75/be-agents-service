# Folder structure and every file

Three **separate roots** — nothing is nested inside the other:

| Root | What it is | Typical path |
|------|------------|--------------|
| **be-agents-service** | Agent service repo (scripts, config, dashboard, server) | `~/HomeCare/be-agents-service` |
| **AgentWorkspace** | Shared folder (iCloud/local): markdown workspaces only | `iCloud Drive/AgentWorkspace` or `~/Library/Mobile Documents/.../AgentWorkspace` |
| **beta-appcaire** | AppCaire monorepo (apps, packages, code) | `~/HomeCare/beta-appcaire` |

---

## 1. be-agents-service (repo)

**Path:** e.g. `~/HomeCare/be-agents-service`

Source and config only (no `node_modules/`, no `dist/`, no `.compound-state/session-*`). Runtime adds: `.compound-state/` (DB + session JSON), `logs/`, `apps/*/dist`, `apps/server/public/`.

```
be-agents-service/
├── .gitignore
├── .compound-state/                    # runtime: DB + session state (do not commit)
│   ├── agent-service.db
│   ├── agent-service.db-shm
│   ├── agent-service.db-wal
│   ├── data/                           # campaigns.json, content.json, leads.json, social-posts.json
│   └── session-*/                      # session-<id>/*.json per run
│
├── agents/
│   ├── backend-specialist.sh
│   ├── db-architect-specialist.sh
│   ├── documentation-expert.sh
│   ├── frontend-specialist.sh
│   ├── infrastructure-specialist.sh
│   ├── levelup-specialist.sh
│   ├── orchestrator.sh
│   ├── senior-code-reviewer.sh
│   ├── ux-designer-specialist.sh
│   ├── verification-specialist.sh
│   ├── management/
│   │   ├── ceo.sh
│   │   ├── cmo-cso.sh
│   │   ├── cpo-cto.sh
│   │   ├── hr-agent-lead.sh
│   │   └── interface-agent.sh
│   ├── marketing/
│   │   ├── AGENTS_REGISTRY.md
│   │   ├── README.md
│   │   ├── friday-developer.sh
│   │   ├── fury-customer-researcher.sh
│   │   ├── jarvis-orchestrator.sh
│   │   ├── loki-content-writer.sh
│   │   ├── pepper-email-marketing.sh
│   │   ├── quill-social-media.sh
│   │   ├── shuri-product-analyst.sh
│   │   ├── vision-seo-analyst.sh
│   │   ├── wanda-designer.sh
│   │   └── wong-notion-agent.sh
│   └── prompts/
│       ├── README.md
│       ├── backend-specialist.md
│       ├── ceo.md
│       ├── cmo-cso.md
│       ├── cpo-cto.md
│       ├── db-architect-specialist.md
│       ├── documentation-expert.md
│       ├── friday-developer.md
│       ├── frontend-specialist.md
│       ├── fury-customer-researcher.md
│       ├── hr-agent-lead.md
│       ├── infrastructure-specialist.md
│       ├── interface-agent.md
│       ├── jarvis-orchestrator.md
│       ├── levelup-specialist.md
│       ├── loki-content-writer.md
│       ├── orchestrator.md
│       ├── pepper-email-marketing.md
│       ├── quill-social-media.md
│       ├── senior-code-reviewer.md
│       ├── shuri-product-analyst.md
│       ├── ux-designer-specialist.md
│       ├── verification-specialist.md
│       ├── vision-seo-analyst.md
│       ├── wanda-designer.md
│       └── wong-notion-agent.md
│
├── apps/
│   ├── dashboard/
│   │   ├── .gitignore
│   │   ├── index.html
│   │   ├── package.json
│   │   ├── postcss.config.js
│   │   ├── public/vite.svg
│   │   ├── README.md
│   │   ├── eslint.config.js
│   │   ├── tailwind.config.js
│   │   ├── tsconfig.app.json
│   │   ├── tsconfig.json
│   │   ├── tsconfig.node.json
│   │   ├── vite.config.ts
│   │   ├── dist/                          # build output (index.html, assets/*)
│   │   └── src/
│   │       ├── App.css
│   │       ├── App.tsx
│   │       ├── main.tsx
│   │       ├── index.css
│   │       ├── types/index.ts
│   │       ├── lib/api.ts
│   │       ├── components/
│   │       │   ├── AgentStatusCard.tsx
│   │       │   ├── CheckInTimeline.tsx
│   │       │   ├── DocViewer.tsx
│   │       │   ├── InboxView.tsx
│   │       │   ├── Layout.tsx
│   │       │   ├── LogViewer.tsx
│   │       │   ├── MemoryViewer.tsx
│   │       │   ├── PagePurpose.tsx
│   │       │   ├── PlansBoard.tsx
│   │       │   ├── PriorityBoard.tsx
│   │       │   ├── RepoSelector.tsx
│   │       │   ├── SetupStatus.tsx
│   │       │   ├── StatsBar.tsx
│   │       │   ├── TeamsOverview.tsx
│   │       │   └── WorkspaceOverview.tsx
│   │       └── pages/
│   │           ├── AgentsPage.tsx
│   │           ├── CommandsPage.tsx
│   │           ├── DashboardPage.tsx
│   │           ├── EngineeringPage.tsx
│   │           ├── InsightsPage.tsx
│   │           ├── ManagementPage.tsx
│   │           ├── MarketingPage.tsx
│   │           ├── PlansPage.tsx
│   │           ├── RLDashboardPage.tsx
│   │           ├── RosterPage.tsx
│   │           ├── RunPage.tsx
│   │           ├── SettingsPage.tsx
│   │           ├── SettingsWithDocsPage.tsx
│   │           ├── TeamsPage.tsx
│   │           └── WorkPage.tsx
│   │
│   └── server/
│       ├── package.json
│       ├── tsconfig.json
│       ├── dist/                          # build output
│       ├── public/                        # built dashboard + index.html
│       └── src/
│           ├── index.ts
│           ├── types/index.ts
│           ├── lib/
│           │   ├── config.ts
│           │   ├── database.ts
│           │   ├── plans-reader.ts
│           │   ├── repo-reader.ts
│           │   ├── services.ts
│           │   ├── workspace-reader.ts
│           │   └── workspace-writer.ts
│           └── routes/
│               ├── agents.ts
│               ├── commands.ts
│               ├── data.ts
│               ├── file.ts
│               ├── gamification.ts
│               ├── integrations.ts
│               ├── jobs.ts
│               ├── logs.ts
│               ├── marketing.ts
│               ├── metrics.ts
│               ├── plans.ts
│               ├── repos.ts
│               ├── repositories.ts
│               ├── rl.ts
│               ├── sessions.ts
│               ├── stats.ts
│               ├── tasks.ts
│               ├── teams.ts
│               └── workspace.ts
│
├── config/
│   ├── repos.yaml
│   └── openclaw/
│       ├── openclaw.json
│       └── README.md
│
├── data/                                 # deprecated; use .compound-state/
│   ├── README.md
│   └── (legacy agent-service.db* if present)
│
├── docs/
│   ├── AGENT_DATA_SOURCES.md
│   ├── AGENT_VS_HUMAN_DOCS.md
│   ├── AGENT_WORKSPACE_STRUCTURE.md
│   ├── API_ENDPOINTS.md
│   ├── ARCHITECTURE.md
│   ├── CLOSED_LOOP_INTEGRATION.md
│   ├── COMPOUND_SETUP_GUIDE.md
│   ├── COMPOUND_WORKFLOW.md
│   ├── DASHBOARD_BEST_PRACTICES.md
│   ├── DATA_FLOW.md
│   ├── DATABASE_ACCESS.md
│   ├── FOLDER_STRUCTURE.md               # this file
│   ├── FRESH_MAC_MINI_SETUP.md
│   ├── HANNES_WORKSPACE_GUIDE.md
│   ├── LLM_ROUTING.md
│   ├── MAC_MINI_COMPLETE_SETUP.md
│   ├── MAC_MINI_RECOVERY.md
│   ├── PRD-MOBILE-APP.md
│   ├── PRD-TIMEFOLD-INTEGRATION.md
│   ├── QUICK_REFERENCE.md
│   ├── README.md
│   ├── SANDBOX_SETUP.md
│   ├── WORKSPACE.md
│   ├── guides/
│   │   ├── engineering-guide.md
│   │   ├── ess-fsr-workflow.md
│   │   ├── marketing-guide.md
│   │   ├── po-workflow.md
│   │   └── quick-start.md
│   ├── reference/
│   │   ├── agents.md
│   │   ├── api-reference.md
│   │   ├── architecture.md
│   │   ├── priority-integration.md
│   │   └── workflow.md
│   └── setup/
│       ├── email-setup.md
│       ├── mac-mini-setup.md
│
├── docs-archive/                         # old docs (many .md files)
│
├── launchd/
│   ├── com.appcaire.agent-server.plist
│   ├── com.appcaire.auto-compound.plist
│   ├── com.appcaire.caffeinate.plist
│   ├── com.appcaire.daily-compound-review.plist
│   ├── com.appcaire.dashboard.plist
│   ├── com.appcaire.morning-briefing.plist
│   ├── com.appcaire.ollama.plist
│   ├── com.appcaire.ollama.plist.template
│   └── com.appcaire.weekly-review.plist
│
├── lib/
│   ├── database.js
│   ├── feedback-schema.json
│   ├── gamification.js
│   ├── job-executor.js
│   ├── learning-controller.js
│   ├── llm-router.js
│   ├── parallel-executor.sh
│   ├── pattern-detector.js
│   ├── repository-manager.js
│   ├── state-manager.sh
│   └── task-router.js
│
├── logs/                                 # runtime: agent/orchestrator logs
│   ├── docs-expert-sessions/
│   ├── infrastructure-sessions/
│   ├── levelup-sessions/
│   ├── orchestrator-sessions/
│   └── running-jobs/
│
├── scripts/
│   ├── README.md
│   ├── SAFETY.md
│   ├── ci-monitor.sh
│   ├── db-api.sh
│   ├── kill-all-claw.sh
│   ├── migrate-to-sqlite.js
│   ├── onboard-claude.sh
│   ├── openclaw-migrate-workspace.sh
│   ├── orchestrator.sh
│   ├── seed-agents.js
│   ├── setup-email-integrations.js
│   ├── setup-ollama-macos-fix.sh
│   ├── setup-social-integrations.js
│   ├── setup-telegram-openclaw.sh
│   ├── start-dashboard.sh
│   ├── sync-state-to-db.sh
│   ├── sync-to-db.js
│   ├── update-claude-md.sh
│   ├── compound/
│   │   ├── README.md
│   │   ├── SAFETY.md
│   │   ├── analyze-report.sh
│   │   ├── auto-compound.sh
│   │   ├── check-status.sh
│   │   ├── daily-compound-review.sh
│   │   ├── llm-invoke.sh
│   │   ├── loop.sh
│   │   ├── sync-prd-to-tasks.js
│   │   └── test-safety.sh
│   ├── notifications/
│   │   ├── morning-briefing.sh
│   │   ├── session-complete.sh
│   │   └── weekly-review.sh
│   ├── sandbox/
│   │   └── build-bridge-for-sandbox.sh
│   ├── timefold-optimization/
│   │   ├── build_c_vehicle_constraint_dataset.py
│   │   ├── build_slinga_geo_dataset.py
│   │   └── build_tunable_continuity_dataset.py
│   └── workspace/
│       ├── generate-checkin.sh
│       ├── init-workspace.sh
│       ├── process-inbox.sh
│       ├── process-input-docs.sh
│       ├── resolve-workspace.sh
│       ├── sync-to-workspace.sh
│       └── templates/
│           ├── context.md
│           ├── daily-checkin.md
│           ├── decisions.md
│           ├── follow-ups.md
│           ├── inbox.md
│           ├── input-readme.md
│           ├── learnings.md
│           ├── monthly-checkin.md
│           ├── priorities.md
│           ├── tasks.md
│           └── weekly-checkin.md
│
├── CLAUDE.md
├── package.json
├── package-lock.json
├── yarn.lock
├── README.md
├── schema.sql
├── gamification-schema.sql
├── reset-gamification.sql
├── seed.sql
├── test-task-completion.sql
├── test-xp-earning.js
└── TIMEFOLD_MAC_MINI_SETUP.md
```

---

## 2. AgentWorkspace (shared folder root)

**Path:** `iCloud Drive/AgentWorkspace` (or `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace` on disk)

One subfolder **per repo**, named after the repo. Each subfolder contains **only** the markdown workspace — no repo clone, no `be-agents-service`, no `agents/`.

### 2.1 AgentWorkspace root

```
AgentWorkspace/
├── beta-appcaire/          # workspace for repo "beta-appcaire" (repo lives at ~/HomeCare/beta-appcaire)
├── hannes-space/           # optional: another repo’s workspace
└── ...                     # one folder per repo
```

### 2.2 One repo’s workspace: every file (e.g. AgentWorkspace/beta-appcaire/)

```
AgentWorkspace/beta-appcaire/
├── inbox.md
├── priorities.md
├── tasks.md
├── follow-ups.md
├── input/
│   └── read/
├── check-ins/
│   ├── daily/              # YYYY-MM-DD.md
│   ├── weekly/             # YYYY-Www.md
│   └── monthly/            # YYYY-MM.md
├── memory/
│   ├── decisions.md
│   ├── learnings.md
│   └── context.md
└── agent-reports/
    ├── latest-session.md
    └── session-*.md
```

**No other files or folders.** No `be-agents-service/`, no `agents/`, no code.

---

## 3. beta-appcaire (repo)

**Path:** e.g. `~/HomeCare/beta-appcaire`

This is the AppCaire monorepo: `apps/` (dashboard, dashboard-server, stats-server, SEO sites, etc.), `packages/` (graphql, ui, shared), `docs/`, etc. Its **workspace** (inbox, priorities, check-ins, memory, agent-reports) lives under **AgentWorkspace/beta-appcaire/** as above, not inside this repo.

---

## Quick reference

| You want… | Look here |
|-----------|-----------|
| Agent scripts, compound, config | `be-agents-service/` |
| Priorities, inbox, check-ins, memory for a repo | `AgentWorkspace/<repo-name>/` |
| AppCaire app code | `beta-appcaire/` (repo) |
| Shared folder root | **AgentWorkspace** |
