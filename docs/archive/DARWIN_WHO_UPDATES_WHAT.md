# DARWIN: what is updated by the agent vs by you

Short reference: **updated by me** vs **updated by the agent** (Telegram/OpenClaw, compound, Darwin manager, scripts).

**Best-practice layout:** Your paths under **my/** (e.g. my/inbox.md, my/priorities.md); agent output under **machine/** (e.g. machine/agent-reports/, machine/check-ins/). Scripts support flat layout too; see DARWIN_STRUCTURE.md.

---

## Updated by you (human)

You own and edit these. Agents read them; they only add or append when the action is clearly “add one item” (e.g. “add to inbox”).

| Path | You |
|------|-----|
| **inbox.md** | Add/remove/edit items; triage. Agent may append when you say “add to inbox” via Telegram. |
| **priorities.md** | Set and reorder the list. Compound only reads (picks #1). |
| **tasks.md** | Create and update tasks, status. |
| **follow-ups.md** | Add/remove “revisit later” items. |
| **memory/context.md** | Project context, focus, constraints, team, links. |
| **memory/decisions.md** | Log decisions (date, title, context, decision, consequences). |
| **memory/learnings.md** | Add learnings. |
| **check-ins/daily\|weekly\|monthly/** | Can edit; scripts create and append. |
| **USER.md** | Who you are (name, what to call you, timezone, notes). **Fill this so the bot has a memory of you.** |
| **SOUL.md** | Agent personality/boundaries (you can tune). |
| **IDENTITY.md** | Agent name, vibe, emoji (often filled during bootstrap). |
| **HEARTBEAT.md** | What the agent should check on heartbeat (or leave empty). |
| **TOOLS.md** | Your local notes (cameras, SSH, TTS, etc.). |
| **input/** | You drop files here for the agent to process. |

---

## Updated by the agent (and scripts)

Agents and scripts write here. You read; don’t rely on editing these by hand (they get overwritten or appended).

### Telegram / OpenClaw agent

| Path | Agent |
|------|--------|
| **inbox.md** | May **append** when you say “add to inbox” or similar. |
| **agent-reports/** | Writes session summaries (e.g. `latest-session.md`). |
| **MEMORY.md** | Reads and **updates** in main session (long-term memory). |
| **memory/YYYY-MM-DD.md** | Creates/updates daily notes. |

### Compound (nightly / on-demand)

| Path | Compound |
|------|----------|
| **agent-reports/** | Writes session report after a run. |
| **check-ins/daily** | Scripts **append** agent activity to today’s check-in. |
| **priorities.md** | Only **reads** (picks #1); does not overwrite your list. |

### Darwin manager (scripts)

| Path | Darwin manager |
|------|----------------|
| **my/memory/*.json** | **Generated** from the `.md` files (do not edit by hand). |
| **machine/archive/** | Moves completed inbox items, duplicate check-ins, etc. here. |
| **INSTR.md** | Can copy here from repo (ensure-structure). |

### Other scripts (sync, init)

| Path | Scripts |
|------|--------|
| **machine/agent-reports/** | Sync script writes `latest-session.md`, `session-*.md`. |
| **machine/check-ins/** | Generate new daily/weekly/monthly files; append activity. |

---

## Summary table

| Path | Updated by you | Updated by agent/scripts |
|------|----------------|---------------------------|
| inbox.md | ✓ Main editor | Append when “add to inbox” |
| priorities.md | ✓ Only you | Read only (compound picks #1) |
| tasks.md | ✓ | Optional: when moving from inbox |
| follow-ups.md | ✓ | Optional: when deferring |
| memory/context.md, decisions.md, learnings.md | ✓ | Only when “save to memory” / explicit |
| memory/*.json | — | Darwin manager (generated) |
| MEMORY.md | Can edit | Telegram agent reads/updates |
| USER.md, SOUL.md, IDENTITY.md, HEARTBEAT.md, TOOLS.md | ✓ | Bootstrap/first run can fill |
| check-ins/* | Can edit | Scripts create + append |
| agent-reports/* | Read only | Agents + sync script only |
| input/ | You drop files | Agent moves processed → input/read/ |
| archive/* | Read only | Darwin manager (moves here) |

So: **you** own priorities, tasks, follow-ups, and the main content of memory and identity files; **the agent** updates MEMORY.md, agent-reports, daily notes, and append-only bits (inbox appends, check-in appends); **scripts** generate memory JSON, create/append check-ins, and manage archive.
