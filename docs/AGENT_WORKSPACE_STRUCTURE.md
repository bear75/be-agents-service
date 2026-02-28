# Agent workspace structure and read/write contract

Canonical layout for the agent service and where agents (OpenClaw, compound scripts, specialists) **read** vs **write**. Follow this so work is predictable and not scattered.

**One shared folder only.** Cursor, compound learning, and Telegram/OpenClaw must all use the **same** AgentWorkspace path. The folder name is **darwin** (or **be-agent-service**) — non-repo, one place for all human–agent shared state. If OpenClaw uses a different folder, you get two sources of truth: Telegram updates memory in one place, compound priorities and learnings in another. OpenClaw’s `agent.workspace` must be set to that path (e.g. `AgentWorkspace/darwin` or `AgentWorkspace/be-agent-service`). See [config/openclaw/README.md](../config/openclaw/README.md).

---

## 1. be-agent-service repo layout

```
be-agents-service/
├── config/                    # READ — Agents read; humans edit
│   ├── repos.yaml             # Repo paths, workspace paths, schedules
│   └── openclaw/               # OpenClaw template (copy to ~/.openclaw/)
│       ├── openclaw.json
│       └── README.md
│
├── agents/                     # READ — Invoked by orchestrator; agents don’t write here
│   ├── backend-specialist.sh
│   ├── frontend-specialist.sh
│   ├── marketing/
│   ├── management/
│   └── prompts/
│
├── scripts/                   # READ — Scripts run; agents don’t edit these
│   ├── compound/               # Auto-compound, daily review, loop
│   ├── workspace/             # init, sync, process-inbox, resolve-workspace
│   │   └── templates/          # READ — Seed content for new workspaces
│   ├── notifications/
│   └── openclaw-migrate-workspace.sh
│
├── lib/                        # READ — Shared shell/JS helpers
├── launchd/                    # READ — Plist templates
├── docs/                       # READ — Humans + agents read; agents write only to allowed paths below
│   ├── guides/
│   ├── reference/
│   └── setup/
│
├── .compound-state/           # WRITE (service only) — Session state, SQLite, agent task state
│   ├── session-*/              # Per-session JSON
│   └── agent-service.db        # SQLite (server and sync scripts use this only)
│
├── logs/                       # WRITE (service only) — Execution logs
│   ├── running-jobs/
│   └── *-sessions/
│
├── data/                       # DEPRECATED — See data/README.md; use .compound-state only
│
└── apps/                       # READ — Server and dashboard code
    ├── server/
    └── dashboard/
```

**Rules for agents (OpenClaw, compound, specialists):**

| Area | Agents may | Agents must not |
|------|------------|------------------|
| `config/`, `agents/`, `scripts/`, `lib/`, `docs/` (except output dirs) | Read | Write or modify |
| `.compound-state/`, `logs/` | — | Only service scripts write here; agents do not touch |
| Per-repo workspace (see below) | Read priorities, inbox, memory; write reports, check-in updates | Overwrite human-only files without contract |

---

## 2. Shared markdown workspace (iCloud or local) — darwin or be-agent-service (non-repo)

The single shared folder for Cursor, compound, and Telegram is under **AgentWorkspace** and is named **darwin** or **be-agent-service** (non-repo; not named after a code repo). Full layout: [WORKSPACE.md](WORKSPACE.md). For repos that have their own workspace in `config/repos.yaml`, compound may also use a per-repo folder (e.g. `AgentWorkspace/beta-appcaire`); the **one** folder that must be shared by Cursor, compound, and Telegram is **AgentWorkspace/darwin** (or **AgentWorkspace/be-agent-service**).

**Do not put the repo or an `agents` folder inside the workspace path.** The shared folder holds only the markdown structure (inbox, memory, priorities, agent-reports, etc.). Code and the agent service live in their own repos (e.g. `~/HomeCare/be-agents-service`).

**Agent read/write contract:**

| Path | Who reads | Who writes |
|------|-----------|------------|
| `inbox.md` | Agent (triage, process) | Human, Telegram, dashboard; agent may append when adding from message |
| `priorities.md` | Agent (picks #1), scripts | Human, Telegram, dashboard |
| `tasks.md` | Agent, scripts | Human, agent (when moving from inbox/priorities) |
| `follow-ups.md` | Agent | Human, agent (when deferring) |
| `memory/` (decisions, learnings, context) | Agent (every session) | Human; agent only when explicitly “save to memory” |
| `check-ins/daily|weekly|monthly/` | Scripts (morning briefing, weekly review) | Scripts (generate), human (edit), agent (append activity only) |
| `agent-reports/` | Human, scripts, Telegram | **Agents and sync script only** — `latest-session.md`, `session-*.md` |
| `input/` | Agent (process-input-docs) | Human (drop files); agent moves processed to `input/read/` |

**Best practice:** Agents write session output only under `agent-reports/` and append to check-ins; they do not overwrite `priorities.md`, `memory/*.md`, or `inbox.md` unless the action is clearly “add/update one item” (e.g. add to inbox, reorder priorities).

---

## 3. When OpenClaw workspace is this repo

When `agent.workspace` points at the be-agents-service repo root (e.g. Mac mini shared folder):

- **OpenClaw bootstrap files** (AGENTS.md, SOUL.md, USER.md, memory/YYYY-MM-DD.md, etc.) live in that root; the agent may read/write them per OpenClaw’s own rules.
- **Repo-owned content** (config, scripts, docs) is **read-only** for the agent; the agent must not edit it unless the task is explicitly “change repo code/docs” and the change is committed.
- **Structured output** (session reports, learnings to keep) should go to:
  - **Per-repo workspace** `agent-reports/` when sync runs for a repo, or
  - A single **output** area inside the repo, e.g. `docs/agent-reports/` or `workspace/agent-reports/`, so new files are not scattered in the repo root.

Prefer writing session summaries and “saved learnings” into the per-repo workspace’s `agent-reports/` and `memory/` (via the sync script or MCP) rather than creating one-off files in the repo root.

---

## 4. Single source of truth

- **State:** Session and task state lives under `.compound-state/`. Scripts and DB use this; avoid writing the same state under `data/` or elsewhere.
- **Logs:** All execution logs under `logs/` (running-jobs, *-sessions).
- **Priorities:** One place per repo — either the repo’s markdown workspace `priorities.md` or (fallback) the repo’s `reports/`; compound reads from workspace first, then reports.

---

## 5. Quick reference for agent authors

1. **Read** from: `config/repos.yaml`, workspace `priorities.md` / `inbox.md` / `memory/`, target repo code.
2. **Write** to: workspace `agent-reports/` and check-in appends; do not write under `config/`, `scripts/`, or repo root unless the task is an explicit code/docs change.
3. **Do not** write session state or logs; the service scripts own `.compound-state/` and `logs/`.
4. **Do not** overwrite human-owned workspace files (e.g. full `memory/context.md`) unless the user asked for that update.

See also: [WORKSPACE.md](WORKSPACE.md), [DATA_FLOW.md](DATA_FLOW.md), [config/openclaw/README.md](../config/openclaw/README.md).
