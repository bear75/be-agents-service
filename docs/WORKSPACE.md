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

## Quick Start

### 1. Initialize workspace

```bash
cd ~/HomeCare/be-agents-service
./scripts/workspace/init-workspace.sh beta-appcaire
```

This creates the full directory structure at the path configured in `config/repos.yaml`.

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

```
~/iCloud/AgentWorkspace/beta-appcaire/
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

In `config/repos.yaml`:

```yaml
repos:
  beta-appcaire:
    path: ~/HomeCare/beta-appcaire
    workspace:
      path: ~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire
      enabled: true
```

The workspace path can be:
- **iCloud**: `~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/...`
- **Local**: `~/HomeCare/workspaces/beta-appcaire`
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
| `init-workspace.sh` | Create workspace structure | `./scripts/workspace/init-workspace.sh beta-appcaire` |
| `generate-checkin.sh` | Create check-in from template | `./scripts/workspace/generate-checkin.sh beta-appcaire daily` |
| `sync-to-workspace.sh` | Sync agent state → markdown | `./scripts/workspace/sync-to-workspace.sh beta-appcaire` |
| `process-inbox.sh` | Triage inbox with Claude | `./scripts/workspace/process-inbox.sh beta-appcaire` |
| `morning-briefing.sh` | Send morning Telegram briefing | `./scripts/notifications/morning-briefing.sh beta-appcaire` |
| `session-complete.sh` | Notify after agent session | `./scripts/notifications/session-complete.sh beta-appcaire completed` |
| `weekly-review.sh` | Send weekly Telegram review | `./scripts/notifications/weekly-review.sh beta-appcaire` |

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

1. **Mac mini**: Pull this branch, run `./scripts/workspace/init-workspace.sh beta-appcaire`
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
