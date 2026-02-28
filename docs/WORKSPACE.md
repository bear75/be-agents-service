# Shared Markdown Workspace

A human-agent shared surface for unstructured data — tasks, priorities, check-ins, memory, and follow-ups. Both you and your agents read and write to the same flat markdown files.

---

## Architecture: Three Layers

```
┌──────────────────────────────────────────────────┐
│  INTERACTION LAYER                                │
│  📱 Telegram only — primary (WhatsApp removed)    │
│  🌐 Dashboard (http://localhost:3010) — visual    │
│  📁 Direct file edit (iCloud) — flexible          │
│  🔌 API (curl) — programmatic                     │
├──────────────────────────────────────────────────┤
│  STORAGE LAYER                                    │
│  📝 Markdown workspace on iCloud / Mac mini       │
│  ⚙️ repos.yaml + .compound-state/ (structured)    │
├──────────────────────────────────────────────────┤
│  EXECUTION LAYER                                  │
│  🤖 auto-compound.sh → reads priorities.md        │
│  🔄 sync-to-workspace.sh → writes agent reports   │
│  ⏰ LaunchD → morning briefing, weekly review      │
└──────────────────────────────────────────────────┘
```

---

**Agent read/write rules:** Agents read priorities, inbox, and **memory/** (every `.md` in `memory/` is listed and readable — put valuable unstructured .md there so agents get smarter). They write only to `agent-reports/` and check-in appends. See [AGENT_WORKSPACE_STRUCTURE.md](AGENT_WORKSPACE_STRUCTURE.md) and the section [Memory: how agents read it and how to add unstructured .md](#memory-how-agents-read-it-and-how-to-add-unstructured-md) below.

---

## Quick Start

### 1. Initialize workspace

```bash
cd ~/HomeCare/be-agents-service
./scripts/workspace/init-workspace.sh darwin
```

Use **darwin** (or **be-agent-service**) as the workspace name — non-repo. This creates the full directory structure at the path you use for the single shared folder (e.g. configure that path in `config/repos.yaml` or OpenClaw’s `agent.workspace`).

### 2. Edit your priorities

Open `priorities.md` in your workspace and add your actual priorities:

```markdown
## High Priority

1. **Employee Certifications** — Add cert tracking to dashboard
2. **Scheduling Fix** — Prevent double-booking
```

The agent picks #1 each night.

### 3. Drop ideas in inbox

Edit `inbox.md` or text your Telegram bot:

```
You: "add to inbox: investigate caching for API"
Bot: ✅ Added to inbox
```

### 4. Set up Telegram (optional but recommended)

See `config/openclaw/README.md` for OpenClaw + Telegram setup.

---

## Workspace Structure

**The single shared folder** used by Cursor, compound learning, and Telegram is named **darwin** or **be-agent-service** (non-repo). Path: `AgentWorkspace/darwin` or `AgentWorkspace/be-agent-service`. That folder contains only the markdown workspace below — no repo, no code. Do **not** put the be-agents-service repo or an `agents` folder inside it. If you already have that, see [Workspace cleanup](#workspace-cleanup) below.

```
iCloud Drive/AgentWorkspace/darwin/   (or AgentWorkspace/be-agent-service — the one shared folder, non-repo)
├── inbox.md              ← Quick-drop ideas, tasks, thoughts
├── priorities.md         ← Agent picks #1 nightly
├── input/                ← Drop .md docs (ideas, features, tasks, marketing); agent converts → inbox/priorities/tasks
│   └── read/             ← Processed docs (handled)
├── tasks.md              ← Active task tracking with status
├── follow-ups.md         ← Things to revisit later
├── check-ins/
│   ├── daily/            ← YYYY-MM-DD.md (auto-generated 8AM)
│   ├── weekly/           ← YYYY-Www.md (auto-generated Mondays)
│   └── monthly/          ← YYYY-MM.md (auto-generated 1st of month)
├── memory/
│   ├── decisions.md      ← Key decisions and why
│   ├── learnings.md      ← Accumulated learnings
│   └── context.md        ← Project background for agents
└── agent-reports/
    ├── latest-session.md ← Most recent agent activity
    └── session-*.md      ← Historical reports
```

**Nothing else.** No `be-agents-service/`, no `agents/`, no `apps/`, no `config/`, no code — only the markdown workspace above.

If DARWIN is currently a **combo of repo files and workspace files**, see [Structure DARWIN folder now](#structure-darwin-folder-now-combo-of-repo--workspace) below.

### Workspace cleanup (if you see duplication)

If your shared folder (e.g. `AgentWorkspace/darwin/` or `AgentWorkspace/be-agent-service/`) contains a nested **be-agents-service** repo or a standalone **agents** folder, that’s code — it doesn’t belong here and makes things confusing.

**Fix:**

1. **Move the repo out** (don’t leave a copy inside the workspace):
   - Move the nested repo to e.g. `~/HomeCare/be-agents-service`. Use Finder “Move” or `mv`; ensure the real repo lives in one place only.
2. **Remove duplicate `agents`** at workspace root:
   - If `agents/` is a copy of the specialist scripts, delete it. Scripts live in the repo at `be-agents-service/agents/`, not in the workspace.
3. **Keep only the markdown workspace** in **darwin** (or **be-agent-service**):
   - Keep: `inbox.md`, `priorities.md`, `tasks.md`, `follow-ups.md`, `check-ins/`, `memory/`, `agent-reports/`, `input/`.
   - Optional: keep other files you deliberately put here (e.g. reference PDFs); the important part is to not have the whole repo or an `agents` copy.

After cleanup, the path `AgentWorkspace/darwin/` (or `AgentWorkspace/be-agent-service/`) should list only the items in the structure diagram above (plus any extra docs you chose to store there).

### Structure DARWIN folder now (combo of repo + workspace)

If DARWIN currently has **both** repo/code files and workspace files, use this to get to the correct structure.

**1. What DARWIN must contain (only this):**

| Item | Type | Purpose |
|------|------|---------|
| `inbox.md` | file | Quick-drop ideas |
| `priorities.md` | file | Agent picks #1 |
| `tasks.md` | file | Active tasks |
| `follow-ups.md` | file | Revisit later |
| `input/` | folder | Drop docs; `input/read/` for processed |
| `check-ins/` | folder | `daily/`, `weekly/`, `monthly/` |
| `memory/` | folder | `decisions.md`, `learnings.md`, `context.md` |
| `agent-reports/` | folder | `latest-session.md`, `session-*.md` |

**2. Move out of DARWIN (repo/code — do not keep here):**

| In DARWIN now | Action |
|---------------|--------|
| `.git`, `.gitignore`, `.gitignore.local` | DARWIN is non-repo. Delete `.git` (or move the whole repo clone to e.g. `~/HomeCare/some-project` and leave DARWIN as workspace only). |
| `agents/` | Remove. Scripts live in `be-agents-service/agents/`. |
| `apps/` | Move to the repo that owns that code (e.g. be-agents-service or beta-appcaire). |
| `config/` | Move to the repo that owns it (e.g. be-agents-service). |
| `.openclaw/` | Move to `~/.openclaw/` on the machine where OpenClaw runs; do not keep inside DARWIN. |
| `__pycache__/` | Delete (Python cache). |
| `*.py` scripts | Move to the repo/project that owns them (e.g. caire-platform/appcaire or a dedicated script repo). |
| `*.json` (baseline_input, c_vehicle_constraint_*, etc.) | Move to the repo or project that uses them (e.g. appcaire or a data folder in a repo). |

**3. Markdown files already in DARWIN:**

- **Workspace files to keep in place:** `inbox.md`, `priorities.md`, `tasks.md`, `follow-ups.md`. If missing, create from `scripts/workspace/templates/` in be-agents-service.
- **Agent/session docs** (e.g. `AGENTS.md`, `BOOTSTRAP.md`, `CLAUDE.md`, `COMPOUND_SESSION_SUMMARY.md`, `continuity_*.md`, `CAMPAIGN_STATUS_*.md`): move into `memory/` (if you want them as long-term context) or into `input/read/` (if processed), or move to a repo’s `docs/` if they belong to a project. Then DARWIN root has no loose .md except the four workspace files above.
- **Check-ins:** Keep only inside `check-ins/daily/`, `check-ins/weekly/`, `check-ins/monthly/`. Any check-in .md at root → move into the right subfolder by date.

**4. Create missing workspace structure (if needed):**

From the be-agents-service repo:

```bash
cd ~/HomeCare/be-agents-service
./scripts/workspace/init-workspace.sh darwin
```

Point the script at your DARWIN path (e.g. set in `config/repos.yaml` for `darwin` or pass the path). The script creates the folders and template files; it won’t overwrite existing ones.

**5. Result:**

`AgentWorkspace/DARWIN/` should contain only: `inbox.md`, `priorities.md`, `tasks.md`, `follow-ups.md`, `input/` (with `read/`), `check-ins/` (daily, weekly, monthly), `memory/` (decisions.md, learnings.md, context.md), `agent-reports/`. No `.git`, no `agents/`, no `apps/`, no `config/`, no `.openclaw/`, no `.py`, no loose `.json` or repo files.

---

## How It Works

### You → Workspace → Agent

1. You add a priority to `priorities.md` (via Telegram, iCloud, or dashboard)
2. At 11 PM, `auto-compound.sh` reads `priorities.md`
3. Agent implements Priority #1, creates a PR
4. `sync-to-workspace.sh` writes results to `agent-reports/latest-session.md`
5. Activity is appended to today's `check-ins/daily/` file

### Agent → Workspace → You

1. At 8 AM, `morning-briefing.sh` reads the workspace
2. Sends you a Telegram message with: what the agent did, priority #1, inbox count
3. You reply with your thoughts → saved to today's check-in
4. On Monday 8 AM, `weekly-review.sh` sends the week summary

---

## Configuration

The single shared folder is **darwin** (or **be-agent-service**), non-repo. In `config/repos.yaml` point the workspace path at that folder, e.g.:

```yaml
repos:
  darwin:
    path: ~/HomeCare/be-agents-service
    workspace:
      path: ~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/darwin
      enabled: true
```

Or use `AgentWorkspace/be-agent-service` instead of `darwin` if you prefer that name. The workspace path can be:
- **iCloud**: `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/darwin` (or `.../be-agent-service`)
- **Local**: `~/HomeCare/workspaces/darwin`
- **Any shared directory**

---

## File Formats

### inbox.md

```markdown
# Inbox

## 2026-02-08
- [ ] Add employee certifications tracking
- [ ] Fix the scheduling overlap bug #bug
- [x] Set up compound workflow → moved to tasks
```

Tags: Add `#tag` to items. They're extracted by the parser.

### priorities.md

```markdown
# Current Priorities

## High Priority

1. **Employee Certifications** — Cert tracking with types, expiry, reminders.
2. **Scheduling Overlap Fix** — Prevent double-booking.

## Medium Priority

1. Performance optimization for schedule loading

## Low Priority

1. Dark mode support

## Parking Lot

- Multi-language support
```

### tasks.md

```markdown
# Active Tasks

## In Progress

### Employee Certifications
- **Status:** In Progress
- **Priority:** High
- **Branch:** feature/certifications
- **Agent:** Backend Specialist
- **Started:** 2026-02-07
- **PR:** #146 (draft)

Schema and migration done.

## Pending

### Scheduling Fix
- **Status:** Pending
- **Priority:** High

## Done

### Auth Setup
- **Completed:** 2026-02-05
- **PR:** #142 (merged)
```

### follow-ups.md

```markdown
# Follow-ups

- [ ] Review auth flow (due: 2026-02-15) #security
- [ ] Check Bryntum alternatives
- [x] Set up CI pipeline
```

---

## Memory: how agents read it and how to add unstructured .md

Agents (Cursor, compound, OpenClaw) get smarter by reading your workspace **memory/** folder. The dashboard API lists and serves **every** `.md` file in `memory/` — not only `context.md`, `learnings.md`, and `decisions.md`. So any valuable .md you put in `memory/` can be read by agents.

**How agents use memory**

- **Compound / dashboard:** Scripts and API read `memory/` when building context (e.g. overview, morning briefing). The API returns all memory files; tools that consume it can pass them to the agent.
- **Cursor / OpenClaw:** When the workspace path points at DARWIN, agents are instructed to read workspace `priorities.md`, `inbox.md`, and **memory/** (see agent prompts and MCP workspace tools). Putting structured memory in `memory/` makes that context available every session.
- **Convention:** The first `# Title` in each file is used as the display title; the rest is content. No special format required — plain markdown is fine.

**Turning unstructured .md into memory so agents get smarter**

You have many loose .md files with valuable context (e.g. AGENTS.md, BOOTSTRAP.md, continuity_*.md, CAMPAIGN_STATUS_*.md). Two ways to make them count:

**Option A — Keep as separate files in `memory/` (simplest)**  
Move each valuable .md into `memory/`. The API and any agent that reads workspace memory will see **all** of them. Use a clear `# Title` at the top so the file is identifiable. Example:

- `memory/context.md` — project background (canonical)
- `memory/learnings.md` — accumulated learnings (canonical)
- `memory/decisions.md` — decisions log (canonical)
- `memory/continuity-analysis.md` — your continuity doc
- `memory/campaign-status.md` — campaign summary
- `memory/compound-session-summary.md` — session notes

Agents that are told “read workspace memory” will then have access to all of these. No need to merge into one file.

**Option B — Merge or summarize into the three canonical files**  
If you prefer a single place per type of content:

- **context.md** — Project background, current focus, constraints, team, links. Merge or paste the “what is this project / how does X work” bits from your loose .md here.
- **learnings.md** — One entry per learning (date + short note). Copy in the “we learned that…” parts from session summaries and analyses.
- **decisions.md** — One entry per decision (date, context, decision, consequences). Copy in the “we decided to…” parts from your docs.

Then you can archive or delete the original loose .md, or keep them in `memory/` as extra reference (agents still read them).

**Recommendation**  
Use **Option A** first: put every valuable .md into `memory/` with a clear `# Title`. That way agents immediately get the full set of context. Later you can optionally merge duplicates or refactor into context/learnings/decisions if you want fewer, longer files.

---

### Daily check-in

```markdown
# Daily Check-in — Saturday, Feb 8, 2026

## What happened today
- Reviewed PR 146

## What's next
- Scheduling overlap investigation

## Blockers
- None

---

## Agent Activity
_Auto-populated_

- **22:30** Daily review completed
- **23:00** Started: Employee Certifications
- **23:52** PR #146 created (draft)
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `init-workspace.sh` | Create workspace structure | `./scripts/workspace/init-workspace.sh darwin` |
| `generate-checkin.sh` | Create check-in from template | `./scripts/workspace/generate-checkin.sh darwin daily` |
| `sync-to-workspace.sh` | Sync agent state → markdown | `./scripts/workspace/sync-to-workspace.sh darwin` |
| `process-inbox.sh` | Triage inbox with Claude | `./scripts/workspace/process-inbox.sh darwin` |
| `morning-briefing.sh` | Send morning Telegram briefing | `./scripts/notifications/morning-briefing.sh darwin` |
| `session-complete.sh` | Notify after agent session | `./scripts/notifications/session-complete.sh darwin completed` |
| `weekly-review.sh` | Send weekly Telegram review | `./scripts/notifications/weekly-review.sh darwin` |

---

## API Endpoints

All endpoints: `GET/POST http://localhost:4010/api/workspace/:repo/...`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/overview` | GET | Combined workspace summary |
| `/inbox` | GET | List inbox items |
| `/inbox` | POST | Add item (`{"text": "..."}`) |
| `/priorities` | GET | List priorities |
| `/priorities/reorder` | POST | Update priority order |
| `/tasks` | GET | List tasks |
| `/tasks` | POST | Add task (`{"title": "...", "priority": "high"}`) |
| `/check-ins` | GET | List check-ins (`?type=daily`) |
| `/check-ins/:type/:date` | GET | Specific check-in |
| `/check-in` | POST | Create from template (`{"type": "daily"}`) |
| `/memory` | GET | List memory files |
| `/memory/:name` | GET | Read specific memory file |
| `/follow-ups` | GET | List follow-ups |
| `/follow-ups` | POST | Add follow-up (`{"text": "...", "dueDate": "2026-02-15"}`) |
| `/agent-report` | GET | Latest agent session report |
| `/status` | GET | Workspace health check |

---

## LaunchD Schedule

| Job | Time | What it does |
|-----|------|-------------|
| Morning briefing | Daily 8:00 AM | Sends workspace summary via Telegram |
| Weekly review | Monday 8:00 AM | Sends weekly stats via Telegram |
| Daily review | Daily 10:30 PM | Extracts learnings → syncs workspace |
| Auto-compound | Daily 11:00 PM | Implements priority #1 → syncs workspace |
| Gateway | When used | Telegram-only bot (WhatsApp removed) |

---

## Telegram Interactions

| You say | What happens |
|---------|-------------|
| "add X to inbox" | Appends to inbox.md |
| "status" / "overview" | Shows workspace summary |
| "priorities" | Lists current priorities |
| "tasks" | Shows active tasks |
| "swap priority 1 and 2" | Updates priorities.md |
| "what did the agent do" | Shows latest session report |
| (any thoughts) | Saved to today's check-in |

---

## Tomorrow's Setup Tasks

1. **Mac mini**: Pull this branch, run `./scripts/workspace/init-workspace.sh darwin`
2. **Telegram**: Create bot via @BotFather, get token + chat ID (WhatsApp bot removed — do not re-enable)
3. **iCloud**: Verify workspace syncs to your devices
4. **LaunchD**: Copy plists, load jobs (see CLAUDE.md)
5. **Email**: Set up notification fallback (optional)

---

## Design Principles

1. **Push, don't pull** — The service sends you check-ins and status updates
2. **Text is the interface** — Quick Telegram messages, no apps to open
3. **Markdown is the storage** — Human-readable, agent-readable, sync-able
4. **Three input paths** — Telegram (fastest), iCloud (flexible), dashboard (visual)
5. **Agents write to marked sections** — Human and agent content clearly separated
6. **Backward compatible** — Workspace is optional, existing workflows still work
