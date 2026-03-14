# DARWIN workspace

Shared markdown workspace for you and the agents. Two main areas.

**When confused:** MEMORY and REPORT are key. 1) Use repo. 2) Use DARWIN (memory, priorities, machine/agent-reports). 3) Ask me over Telegram.

---

## My files (you edit)

| Path | Purpose |
|------|---------|
| **my/inbox.md** | Open items only (checkboxes). Done items get archived. |
| **my/priorities.md** | Single priority list; compound picks #1 nightly. |
| **my/tasks.md** | Active tasks with status. |
| **my/follow-ups.md** | Revisit later. |
| **my/memory/** | context.md, decisions.md, learnings.md (+ generated .json). |
| **my/input/** | Drop docs here; agents process → inbox/priorities. Processed → my/input/read/. |
| **my/research/** | Run outputs, methodology (reference). |

---

## Machine folders (agents/scripts write)

| Path | Purpose |
|------|---------|
| **machine/agent-reports/** | Session summaries (latest-session.md, session-*.md). |
| **machine/check-ins/** | daily/, weekly/, monthly/ — scripts append agent activity. |
| **machine/archive/** | Completed inbox, duplicate check-ins, orphaned files. |

---

**Root:** README.md (this file), INSTR.md, MEMORY.md (OpenClaw memory), and optional identity files (AGENTS.md, USER.md, SOUL.md, etc.).

**House-clean:** From be-agents-service run `./scripts/darwin/house-clean.sh` to validate, archive, and sync. Use `--migrate` once to move a flat layout into my/ and machine/.

See **INSTR.md** (or repo docs/DARWIN_STRUCTURE.md) for the full layout.
