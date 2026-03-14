# DARWIN workspace structure (canonical INSTR)

**Single source of truth** for the DARWIN shared workspace. Scripts and the Darwin manager agent enforce this layout and keep content in the right place. All paths are relative to the workspace root (e.g. `AgentWorkspace/DARWIN`).

---

## 1. Directory and file layout

**Best-practice layout:** Root = README, INSTR, MEMORY, identity only. **my/** = your files (inbox, priorities, tasks, follow-ups, memory/, input/, research/). **machine/** = agent output (agent-reports/, check-ins/, archive/). Scripts support both this and legacy flat layout; use `house-clean.sh --migrate` once to migrate. See §2 table for allowed paths.

```
DARWIN/
├── INSTR.md                    ← Copy of this structure (optional; for humans opening the folder)
├── README.md                   ← Short “what lives where” (optional)
│
├── inbox.md                    ← Current open items only (checkboxes; archive done elsewhere)
├── priorities.md               ← Single canonical list; compound picks #1 nightly
├── tasks.md                    ← Active tasks with status
├── follow-ups.md               ← Revisit later (optional due dates)
│
├── memory/                     ← Agent-facing context only; machine-readable + human .md
│   ├── context.md              ← Human-editable project context
│   ├── context.json            ← Machine-readable (generated from context.md or vice versa)
│   ├── decisions.md            ← Human-editable decisions log
│   ├── decisions.json          ← Machine-readable list (generated)
│   ├── learnings.md            ← Human-editable learnings
│   └── learnings.json          ← Machine-readable list (generated)
│
├── check-ins/
│   ├── daily/                  ← YYYY-MM-DD.md only (no spaces, no " 2" duplicates)
│   ├── weekly/                 ← YYYY-Www.md only
│   └── monthly/                ← YYYY-MM.md only
│
├── agent-reports/              ← Session summaries (latest-session.md, session-*.md)
├── input/                      ← Drop docs for agents to process
│   └── read/                   ← Processed docs (moved here after handling)
│
├── research/                   ← Run outputs, methodology, handoffs (not for every agent read)
├── archive/                    ← Old/done: completed inbox, duplicate check-ins, dated notes
│   ├── notes/                  ← Dated one-off notes moved out of memory/
│   ├── inbox-archive-*.md      ← Completed inbox items by month
│   └── check-ins-duplicates/   ← Duplicate-named check-ins (e.g. "2026-03-01 2.md")
│
├── MEMORY.md                    ← OpenClaw long-term memory (agent reads/updates; keep at root)
└── (optional at root)           ← OpenClaw/identity: AGENTS.md, USER.md, SOUL.md, IDENTITY.md, BOOTSTRAP.md, HEARTBEAT.md, TOOLS.md
```

**Not in DARWIN:** Code repos, `agents/` copies, heavy datasets (e.g. huddinge-datasets). Those live in repo or external paths.

---

## 2. Allowed file names and rules

| Path | Allowed | Not allowed |
|------|---------|-------------|
| Root | `README.md`, `INSTR.md`, `MEMORY.md`, identity `*.md` | `inbox.md`, `priorities.md` (use my/); code/config dirs |
| my/ | `inbox.md`, `priorities.md`, `tasks.md`, `follow-ups.md` | `priorities-*.md` (use single priorities.md) |
| my/memory/ | `context.md`, `context.json`, `decisions.md`, `decisions.json`, `learnings.md`, `learnings.json` | Any other files; run outputs; dated notes |
| machine/check-ins/daily | `YYYY-MM-DD.md` | Spaces in name; `YYYY-MM-DD 2.md` |
| machine/check-ins/weekly | `YYYY-Www.md` | Same as daily |
| machine/check-ins/monthly | `YYYY-MM.md` | Same as daily |
| machine/agent-reports/ | `latest-session.md`, `session-*.md` | — |
| machine/archive/ | Any; subdirs `notes/`, `inbox-archive-*.md`, `check-ins-duplicates/`, `orphaned/` | — |

---

## 3. Structured memory (machine-readable)

Important memory for agents is stored in **both** human-editable `.md` and machine-readable `.json`. Scripts keep them in sync (see §5).

- **context.json** — Single object: `{ "project", "focus", "constraints", "team", "links" }`. See `docs/DARWIN_MEMORY_SCHEMA.md`.
- **decisions.json** — Array of `{ "id", "date", "title", "context", "decision", "consequences" }`.
- **learnings.json** — Array of `{ "id", "date", "summary", "detail", "tags" }`.

Agents and compound should **read** `my/memory/*.json` when they need structured context; they can still read `.md` for display or when JSON is missing. The Darwin manager (or a scheduled script) regenerates `.json` from `.md` so the canonical source for editing remains markdown.

---

## 3.5 When confused (repo teams and agents)

**MEMORY and REPORT are key.** Resolution order:

1. **Use repo** — CLAUDE.md, repo docs, code (single source of truth for that repo).
2. **Use DARWIN** — my/memory (context, decisions, learnings), my/priorities.md, and **machine/agent-reports/** (latest-session.md, session-*.md).
3. **Ask me over Telegram** — human clarification when 1 and 2 are not enough.

Do not guess. 1 → 2 → 3. See repo [docs/AGENTS_WHEN_CONFUSED.md](AGENTS_WHEN_CONFUSED.md).

---

## 4. Who does what

| Actor | Reads | Writes |
|-------|--------|--------|
| Human | All | my/inbox, my/priorities, my/tasks, my/follow-ups, my/memory/*.md, machine/check-ins |
| Telegram / OpenClaw | my/inbox, my/priorities, my/memory (and .json when available) | my/inbox, machine/agent-reports (session summary) |
| Compound | my/priorities, my/memory (and .json), my/input/read | machine/agent-reports, machine/check-in appends |
| Darwin manager | INSTR (this doc), workspace files | machine/archive/, my/memory/*.json, structure fixes (duplicate check-ins, missing dirs) |
| Scripts (sync, init) | .compound-state, templates | machine/agent-reports, machine/check-ins, my/memory if generating from templates |

---

## 5. Scripts that maintain structure

- **ensure-structure** — Create missing dirs (my/, machine/, subdirs) and template files in my/; do not overwrite existing. Idempotent.
- **validate-structure** — Check workspace matches this layout (my/ + machine/) and naming; report violations (e.g. priorities-*.md in my/, extra files in my/memory/, duplicate check-in names in machine/check-ins).
- **archive-completed** — Move completed items from my/inbox.md to machine/archive/inbox-archive-YYYY-MM.md; move duplicate-named check-ins to machine/archive/check-ins-duplicates/.
- **memory-to-structured** — Parse my/memory/context.md, decisions.md, learnings.md and write my/memory/*.json per schema. Idempotent; only overwrites .json.
- **house-clean** — Run validate → archive-completed → ensure-structure → memory-to-structured. Use `--migrate` once to move a flat workspace into my/ and machine/.

The **Darwin manager agent** runs: validate → archive-completed → ensure-structure → memory-to-structured. For a one-time migration from flat layout, use **house-clean.sh --migrate**.

---

## 6. Reference docs

- **Every file and folder explained:** [DARWIN_FILES_AND_FOLDERS.md](DARWIN_FILES_AND_FOLDERS.md) — purpose of each path in the new setup
- **Restructure rationale:** [DARWIN_WORKSPACE_RESTRUCTURE.md](DARWIN_WORKSPACE_RESTRUCTURE.md)
- **Memory JSON schema:** [DARWIN_MEMORY_SCHEMA.md](DARWIN_MEMORY_SCHEMA.md)
- **When confused (agents/teams):** [AGENTS_WHEN_CONFUSED.md](AGENTS_WHEN_CONFUSED.md) — 1) repo, 2) DARWIN, 3) ask over Telegram
- **Orchestrator best practices:** [agent-orchestrator-service-best-practices.md](agent-orchestrator-service-best-practices.md) (for manager agent design)
- **Workspace contract:** [AGENT_WORKSPACE_STRUCTURE.md](AGENT_WORKSPACE_STRUCTURE.md)
