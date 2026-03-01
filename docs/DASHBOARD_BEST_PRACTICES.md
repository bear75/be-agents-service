# Dashboard Best Practices (OpenClaw, SwarmClaw, Compound AI)

Reference for Darwin dashboard design. Sources: OpenClaw, SwarmClaw, AgenticFlow, Compound AI patterns.

---

## What's Working Well Today

### SwarmClaw (OpenClaw control plane)

- **4–5 surfaces**: Dashboard, Agent Builder, Task Board, Providers, Scheduling
- **Single control center** — orchestrate remote agents from one place
- **Task Board** — Kanban for agent work, audit trail, result diffs
- **Agent Builder** — personalities, system prompts, skills, MCP
- **Multi-provider** — 15+ providers (Claude Code, Anthropic, OpenAI, Ollama, etc.)

### OpenClaw Best Practices

- **Memory**: daily logs vs long-term curated memory; `memory_search` before full load
- **Automation**: heartbeats vs cron; isolated sessions for heavy tasks
- **Multi-agent**: hub-and-spoke coordinator; specialized `SOUL.md` personas
- **Workspace**: standardized structure (`workspace/projects/`), coordinator pattern

### Compound AI Production Patterns

- **5 dashboard types**: Executive value, Ops SLO, Risk & compliance, Cost, Product learning
- **Tripwires** per agent type: RAG accuracy, tool error rates, escalation, loops
- **Feedback loops** — human review, LLM-as-judge, iterative prompt refinement
- **Observability** — full traces (identity → retrieval → tool calls → outputs)

### AgenticFlow

- **Visual orchestration** — React Flow, left-to-right flows
- **Color by function** — research=blue, analysis=green, output=orange
- **Placement**: control top, output right, input left

---

## Darwin Structure (No Overlap)

| Page | Purpose | What it does |
|------|---------|--------------|
| **Overview** | Entry point & context | Quick start, workspace (inbox, priorities, check-ins) when repo selected |
| **Run** | Launch automation | Compound: start auto-compound (records session for Work). Commit & push all. |
| **Work** | Show work status | Sessions and tasks in one view. Click session to expand. Tasks sync from prd.json when compound runs. |
| **Roster** | Configure who does what | Agents: hire/fire. Teams: config & members. One surface. |
| **Plans** | What to build | PRDs, roadmaps. Repo status & logs when repo selected |
| **Insights** | Observability & gamification | Analytics (RL). Leaderboard (XP, tasks, success rate) |
| **Marketing** | Marketing domain | Campaigns & leads (if used) |
| **Settings** | Setup & reference | Config, integrations. Docs (commands, API) |

---

## Why No Tasks After Compound Ran?

Compound writes tasks to `scripts/compound/prd.json` in the target repo. `sync-prd-to-tasks.js` syncs them to the tasks API when auto-compound runs (after prd.json is created and after loop completes). The dashboard reads tasks from the tasks API.

---

## Consolidation Rationale

| Merged | Was | Why |
|--------|-----|-----|
| **Roster** | Agents + Teams | Same roster, different views. One "who does what" surface. |
| **Insights** | Management + Analytics | Both metrics/gamification. Executive value + learning. |
| **Settings** | Settings + Docs | Both "how to set up & use". Reference lives with config. |

---

## Alignment Checklist

- [x] Single control center (OpenClaw)
- [x] Clear Task Board (SwarmClaw)
- [x] Agent/Team config in one place (SwarmClaw Agent Builder)
- [x] Executive + Ops views (Compound AI)
- [x] No overlap — each page has one purpose
