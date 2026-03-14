# DARWIN: what every file and folder is for

Plain list of every file and folder in the DARWIN setup (best-practice: my/ + machine/; see DARWIN_STRUCTURE.md) and what it’s for.

---

## Root (top level of DARWIN)

| File or folder | Purpose |
|----------------|---------|
| **inbox.md** | Current ideas and to-dos only. Use checkboxes `- [ ]` and `- [x]`. Done items are moved to `archive/inbox-archive-YYYY-MM.md` by the Darwin manager so inbox stays short. You and Telegram add here; agents triage into priorities/tasks/follow-ups. |
| **priorities.md** | The one priority list. Compound reads this every night and implements **item #1**. You edit this; don’t create `priorities-2026-03-01.md` etc. at root — use only this file. |
| **tasks.md** | Active tasks and their status. Things that are already “in progress” or assigned, not just ideas. |
| **follow-ups.md** | Things to revisit later. You can add `(due: YYYY-MM-DD)` if you want. |
| **README.md** | Short “what lives where” for humans opening the folder. Optional. |
| **INSTR.md** | Copy of the canonical structure (from `docs/DARWIN_STRUCTURE.md`). The Darwin manager can put it here so the folder is self-explanatory. Optional. |
| **MEMORY.md** | OpenClaw **long-term memory**. The Telegram agent reads and updates this so it “remembers” across sessions. Keep at root; don’t move to research/. |
| **AGENTS.md, USER.md, SOUL.md, IDENTITY.md, BOOTSTRAP.md, HEARTBEAT.md, TOOLS.md** | OpenClaw/Telegram: agent instructions (AGENTS.md), who you are (USER.md), who the agent is (SOUL.md, IDENTITY.md), first-run (BOOTSTRAP.md), heartbeat tasks (HEARTBEAT.md), local notes (TOOLS.md). **Fill USER.md** so the bot has a “memory of you”; otherwise it has no idea who you are. See docs/DARWIN_OPENCLAW_IDENTITY_FILES.md. |

---

## memory/

**Purpose:** The small set of context that agents read every time (project, decisions, learnings). Nothing else goes here — no run outputs, no dated notes.

| File | Purpose |
|------|---------|
| **context.md** | You edit this. Short project background: what the project is, current focus, constraints, team, important links. Agents use it to stay aligned. |
| **context.json** | Same content as `context.md` in a fixed structure (project, focus, constraints, team, links). Generated from `context.md` by the Darwin manager; agents can read this for parsing. Don’t edit by hand. |
| **decisions.md** | You (and agents) edit this. Log of important decisions: date, title, why, what was decided, consequences. Format: `## YYYY-MM-DD: Title` then **Context:**, **Decision:**, **Consequences:**. |
| **decisions.json** | Same as `decisions.md` but as a list of objects. Generated from `decisions.md`; don’t edit by hand. |
| **learnings.md** | You (and agents) edit this. Bullet list of things we learned. Can add `(tags: x, y)` at the end of a line. |
| **learnings.json** | Same as `learnings.md` but as a list of objects. Generated from `learnings.md`; don’t edit by hand. |

**Rule:** Only these six files belong in `memory/`. Dated notes, run outputs, and methodology docs go in `archive/notes/` or `research/`.

---

## check-ins/

**Purpose:** Time-based notes: daily, weekly, monthly. Scripts create and append; you can edit. Used for morning briefing and weekly review.

| Folder | Purpose | File names |
|--------|---------|------------|
| **check-ins/daily/** | One file per day. | `YYYY-MM-DD.md` (e.g. `2026-03-02.md`). No spaces, no `2026-03-02 2.md`. |
| **check-ins/weekly/** | One file per week. | `YYYY-Www.md` (e.g. `2026-W09.md`). |
| **check-ins/monthly/** | One file per month. | `YYYY-MM.md`. |

Duplicate names (e.g. `2026-03-01 2.md`) are moved to `archive/check-ins-duplicates/` by the Darwin manager.

---

## agent-reports/

**Purpose:** Where compound and agents write session summaries. Telegram and morning briefing read from here.

| File | Purpose |
|------|---------|
| **latest-session.md** | Most recent session summary (overwritten each time). |
| **session-*.md** | Older session reports (e.g. `session-1234567890.md`). |

Only agents and sync scripts write here; you read.

---

## input/ and input/read/

**Purpose:** You drop documents (e.g. PRDs, briefs) for agents to process. Processed ones move to `read/` so agents know they’re done.

| Folder / file | Purpose |
|----------------|---------|
| **input/** | Folder where you put new docs (e.g. `.md` or `.pdf`) for agents to turn into inbox items, priorities, or tasks. |
| **input/read/** | After processing, scripts move docs here. “Already read” reference; agents can use them but don’t re-process. |

---

## research/

**Purpose:** Run outputs, methodology docs, handoffs (Timefold, continuity, Pareto, etc.). Reference only — agents don’t load all of this every time; they use `memory/` for daily context.

| Contents | Purpose |
|-----------|---------|
| Subfolders like `sweep/`, `pareto/`, `first-run-top15/`, `approach-0/` | Outputs from specific runs or experiments. |
| Files like `TIMEFOLD_*.md`, `continuity_*.md`, `*_METHODOLOGY_*.md` | Handoffs and methodology. |
| Anything that used to sit in `memory/` but isn’t “current context” | Moved here so `memory/` stays small. |

You and agents can read when a task needs it; no strict naming. Nothing here is auto-generated by the Darwin manager.

---

## archive/

**Purpose:** Old or “done” stuff so the rest of DARWIN stays current. The Darwin manager moves things here; you can browse when you need history.

| Folder / file | Purpose |
|----------------|---------|
| **archive/notes/** | Dated one-off notes (e.g. `2026-02-22.md`) that were in `memory/`. Moved out so `memory/` only has context, decisions, learnings. |
| **archive/inbox-archive-YYYY-MM.md** | Completed inbox items (checkboxes that were `[x]`) for that month. The manager appends to this and removes those lines from `inbox.md`. |
| **archive/check-ins-duplicates/** | Check-in files with duplicate names (e.g. `2026-03-01 2.md`). Moved so daily/weekly only have one file per date/week. |
| **archive/priorities-run-config.md**, **archive/priorities-2026-03-01.md**, etc. | Old or dated priority lists. Kept for history; only `priorities.md` at root is used. |

Agents don’t read `archive/` by default; it’s for humans and optional lookups.

---

## What does *not* live in DARWIN

- **Code repos** (e.g. be-agents-service, appcaire) — they live in `~/HomeCare/...` or similar.
- **Heavy datasets** (e.g. huddinge-datasets with run data) — keep in the appcaire repo or another data path, not in DARWIN.
- **Config or code** — no `config/`, `agents/`, or app code inside DARWIN. Only markdown (and the optional identity files) and the structure above.

---

## Quick map

| I want to… | Use (best-practice: my/ or machine/) |
|------------|-------------------------------------|
| Add an idea or to-do | my/inbox.md (or inbox.md flat) |
| Set what gets built next | my/priorities.md |
| Track active work | my/tasks.md |
| Defer something | my/follow-ups.md |
| Give agents project context | my/memory/context.md |
| Record a decision | my/memory/decisions.md |
| Record a learning | my/memory/learnings.md |
| See what agents did | machine/agent-reports/ |
| Give agents a doc to process | my/input/ → my/input/read/ when done |
| Keep run outputs / methodology | my/research/ |
| Find old inbox or check-ins | machine/archive/ |

One place per purpose; Darwin manager and house-clean keep structure in shape.
