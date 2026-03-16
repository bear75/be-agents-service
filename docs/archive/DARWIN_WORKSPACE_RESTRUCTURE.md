# DARWIN workspace restructure – focus for Telegram and compound learning

Review of the shared workspace at `AgentWorkspace/DARWIN` (iCloud) with suggestions so Telegram and compound learning stay focused and effective.

**Restructure applied:** 2026-03-02. The live DARWIN folder was updated: `archive/` created, `memory/` trimmed to 3 files, run outputs removed from memory, duplicate check-ins and completed inbox items archived, single `priorities.md` as canonical. To refill `memory/context.md`, `decisions.md`, and `learnings.md` from the moved content, run `node scripts/darwin/summarize-archive-to-memory.js` from be-agents-service (on a machine where DARWIN is on disk).

**Canonical structure (INSTR):** [DARWIN_STRUCTURE.md](DARWIN_STRUCTURE.md) — single source of truth; scripts and the Darwin manager agent enforce it. Memory has machine-readable `.json` per [DARWIN_MEMORY_SCHEMA.md](DARWIN_MEMORY_SCHEMA.md). Run `./agents/darwin-manager.sh` to validate, archive, ensure structure, and regenerate `memory/*.json`.

**Other refs:** [WORKSPACE.md](WORKSPACE.md), [AGENT_WORKSPACE_STRUCTURE.md](AGENT_WORKSPACE_STRUCTURE.md).

---

## Current state (summary)

| Area | What’s there | Issue |
|------|----------------|------|
| **Root** | `inbox.md`, `priorities-2026-03-01.md`, `priorities.md`, `tasks.md`, `follow-ups.md` | Both dated and undated priorities; compound uses dated first. Inbox is long and mixes done/todo. |
| **memory/** | 48+ files: identity (USER, SOUL, IDENTITY), project docs (Timefold, continuity, Pareto), dated notes (2026-02-*.md), run outputs (sweep/N*, pareto, first-run-top15) | Agents read *all* of `memory/`; run outputs and research copies dilute focus. Duplication with `research/`. |
| **research/** | Pareto, sweep, iter findings, READMEs | Overlaps with `memory/`; some files exist in both. |
| **check-ins/daily\|weekly** | Many daily/weekly files; some duplicates (`2026-02-23 2.md`, `2026-03-01 2.md`) | Duplicate filenames suggest sync or copy noise; one naming scheme would help. |
| **agent-reports/** | Empty | Session summaries not written here (or go elsewhere); compound/Telegram expect session output here. |
| **input/read** | A few processed docs | Underused; good place for “already read” reference. |
| **huddinge-datasets/** | Run-specific data (28-feb, hash dirs) | Fits repo or a data volume better than the shared “focus” workspace. |

---

## Goals

1. **Telegram** – Inbox and priorities are the main surface; keep them small and current so the bot and triage stay useful.
2. **Compound learning** – Nightly run reads **one** clear priorities source, and **memory/** should contain only what agents need for context and learnings (not run artifacts).
3. **Single source of truth** – No duplicate “priorities” flows; minimal duplication between `memory/` and `research/`.

---

## Suggested restructure

### 1. Priorities: one canonical source

- **Option A (recommended):** Use **only** `priorities.md` at root and keep it current. Remove or archive `priorities-*.md` so compound and scripts always use `priorities.md`.
- **Option B:** Use **only** dated files (e.g. `priorities-YYYY-MM-DD.md`) and create today’s file when you set priorities; stop maintaining a separate `priorities.md`.

Scripts already support both; pick one and stick to it so “what’s priority #1” is unambiguous.

### 2. Inbox: keep it current

- **Archive completed items** – Move done items from `inbox.md` into a monthly check-in or `check-ins/daily/YYYY-MM-DD.md` (or an `archive/` section at the bottom). Leave in inbox only: open loops, un triaged items, and “to decide”.
- **Triage regularly** – Use `process-inbox.sh` or Telegram (“triage my inbox”) so items move to priorities/tasks/follow-ups and inbox stays short (e.g. &lt; 20 items).

This keeps Telegram and “add to inbox” focused on what’s actually next.

### 3. Memory: split “agent context” from “run/research outputs”

**Agents (and compound) should read only a focused subset of memory.**

- **Keep in `memory/` (agent-facing):**
  - `context.md` – product/positioning context.
  - `decisions.md`, `learnings.md` – durable decisions and learnings.
  - `USER.md`, `SOUL.md`, `IDENTITY.md` (or equivalent) if used by OpenClaw/Telegram.
  - A small set of **current** strategy/status files (e.g. one “current strategy” doc, one “current campaign status” if needed).

- **Move out of `memory/`:**
  - **Run/output artifacts** – e.g. `memory/sweep/`, `memory/pareto/`, `memory/first-run-top15/`, `memory/approach-0/` → move to `research/` or to a repo (e.g. `appcaire` or `be-agents-service`) under a `docs/` or `data/` path.
  - **Dated one-off notes** – e.g. `2026-02-22.md` … `2026-02-28.md` → move to `check-ins/daily/` or an `archive/notes/` folder so they don’t clutter the main memory list.
  - **Research handoffs and methodology docs** – e.g. `TIMEFOLD_*`, `continuity_*`, `*_METHODOLOGY_*` → move to `research/` or repo `docs/`; keep in `memory/` only a short “current research status” summary if needed.

Result: `memory/` has ~10–15 files that are clearly “context and learnings”. Compound and Telegram get a consistent, focused context.

### 4. Research: single home for run outputs

- Keep **one** place for research outputs: either `research/` in the workspace or a repo path (e.g. `appcaire/docs/` or `be-agents-service/docs/`).
- Remove duplicates: if a file exists in both `memory/` and `research/`, keep it only in `research/` (or repo) and optionally link to it from `memory/context.md` or `memory/learnings.md`.

### 5. Agent-reports: ensure session output lands here

- Confirm that compound and any session-summary scripts write to `DARWIN/agent-reports/` (e.g. `latest-session.md`, `session-*.md`). If they currently write elsewhere (e.g. repo only), point them at this folder so Telegram and morning briefing can use the same place.
- See [AGENT_WORKSPACE_STRUCTURE.md](AGENT_WORKSPACE_STRUCTURE.md): agents should write session output only under `agent-reports/` and check-in appends.

### 6. Huddinge-datasets and heavy data

- Move `huddinge-datasets/` (e.g. `28-feb/` with hash dirs) to the appcaire repo (e.g. `docs_2.0/recurring-visits/huddinge-package/` or a dedicated `data/` path) or keep outside the shared workspace. This keeps DARWIN a “markdown + light reference” workspace and avoids iCloud syncing large run data.

### 7. Check-ins: canonical naming

- Resolve duplicates like `2026-02-23 2.md` and `2026-03-01 2.md` (merge into `2026-02-23.md` and `2026-03-01.md` or delete the duplicate). Use a single naming scheme: `YYYY-MM-DD.md` for daily, `YYYY-Www.md` for weekly, so scripts and briefing don’t see duplicate dates.

---

## Suggested target layout (after restructure)

```
DARWIN/
├── inbox.md                    ← Current items only; archive done elsewhere
├── priorities.md               ← Single canonical (or only priorities-YYYY-MM-DD.md)
├── tasks.md
├── follow-ups.md
├── check-ins/
│   ├── daily/                 ← YYYY-MM-DD.md only; no " 2" duplicates
│   ├── weekly/
│   └── monthly/
├── memory/                     ← Agent-facing only (~10–15 files)
│   ├── context.md
│   ├── decisions.md
│   ├── learnings.md
│   ├── USER.md, SOUL.md, IDENTITY.md (if used)
│   └── (optional) 1–2 current strategy/status docs
├── research/                   ← All run outputs, methodology, handoffs
│   ├── sweep/, pareto/, first-run-top15/, approach-0/
│   ├── TIMEFOLD_*, continuity_*, etc.
│   └── (no duplicate copies in memory/)
├── input/
│   └── read/                  ← Processed reference docs
├── agent-reports/              ← Session summaries (latest-session.md, session-*.md)
└── (optional) archive/         ← Old inbox items or dated notes moved out of memory
```

`huddinge-datasets/` and heavy data live in repo or elsewhere; `.openclaw`/`.pi` stay as-is.

---

## Implementation order

1. **Quick wins:** Choose one priorities source; thin inbox (archive done items); fix check-in duplicate names.
2. **Memory focus:** Move run/output and research duplicates out of `memory/` into `research/` or repo; leave in `memory/` only context, decisions, learnings, identity.
3. **Session output:** Point compound/session scripts at `agent-reports/` and confirm Telegram/briefing use it.
4. **Data:** Move `huddinge-datasets/` to repo or external path.

This keeps Telegram and compound learning aligned on a small, clear set of files while preserving history in check-ins and research.
