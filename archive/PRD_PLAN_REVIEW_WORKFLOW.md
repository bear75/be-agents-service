# PRD and Plan Review Workflow

> **Purpose:** How to get expert multi-agent review of new PRDs and implementation plans (feasibility, external systems, codebase fit, architecture compliance).  
> **Last updated:** 2026-02-25

---

## 1. Why only one plan in `docs/plans/`?

You have **two** plan locations:

| Location             | Contents                                                                                  | Source                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`docs/plans/`**    | Single “official” implementation plan (e.g. `2026-02-25-ai-chat-schedule-integration.md`) | Output of **writing-plans** skill / **write-plan** command; intended as the canonical plan for a feature, saved under `docs/` per monorepo rules. |
| **`.cursor/plans/`** | Many plans (scheduling, timefold, mobile, merged PRD, etc.)                               | Cursor/IDE–generated plans from Composer, agent mode, or ad‑hoc sessions; often UUID-suffixed.                                                    |

So: **`docs/plans/`** is “one current plan per feature” by design (writing-plans says _Save plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`_). The **volume** of plans lives in `.cursor/plans/`. If you want more plans under `docs/plans/`, run **write-plan** (or equivalent) for each feature and save there; optionally copy or promote selected `.cursor/plans/*` into `docs/plans/` and archive the rest.

---

## 2. What you already have (Cursor + be-agent-service)

### In Cursor (beta-appcaire)

- **`/write-plan`** — Invokes **writing-plans** skill; produces a bite-sized implementation plan. Saves to `docs/plans/YYYY-MM-DD-<feature>.md`.
- **`/deepen-plan`** (compound-engineering) — Takes a plan path, runs **parallel research** (skills, learnings, per-section explore agents, then all review agents), and adds “Research Insights” to each section. Does **not** run feasibility vs external systems by name; you can point it at Timefold/Bryntum by mentioning them in the plan.
- **`work-breakdown`** command — Breaks a spec into sprints/tasks and **hands the output to a “reviewer sub-agent”** for critique, then incorporates feedback. Single reviewer; no external research or arch check.
- **Code-reviewer agent** (superpowers) — Reviews **implemented** work against the plan and coding standards. Use after implementation, not for PRD/plan review.
- **Architecture rules** — `.cursor/rules/appcaire-monorepo.mdc` (and branch-safety, etc.) are applied automatically; no separate “arch review agent” in Cursor by default.

### In be-agent-service

- **Orchestrator** — Engineering Scrum Master; reads priorities, spawns Backend/Frontend/Infrastructure/Verification/Senior Reviewer; does **not** take a PRD/plan as primary input or run external-feasibility research.
- **CPO/CTO** — Product/tech direction and architecture approval; high-level; does **not** run a structured PRD review pipeline.
- **Jarvis** — Marketing squad lead; creates marketing PRD and coordinates marketing agents; **not** for product/engineering PRD review.

So today: **no single command or agent** in your stack is “review this PRD/plan with expert agents + external research + codebase verification + arch compliance.” You can **compose** that from Cursor’s **mcp_task** (subagents) plus **deepen-plan** and a custom command.

---

## 3. What exists online you can use

| Tool / approach                        | What it does                                                                                                                | How you can use it                                                                                                                                                                                   |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MetaGPT** (multi-agent PRD)          | Multi-agent framework: roles (research, planning, review); often used with Ollama/DeepSeek for PRD generation and critique. | Run outside Cursor (e.g. script that calls MetaGPT with your PRD, then paste results into Cursor). [Ref](https://www.ibm.com/think/tutorials/multi-agent-prd-ai-automation-metagpt-ollama-deepseek). |
| **“Agentic PRD”** (ProdMoh, 2024–25)   | PRDs designed for AI: declarative acceptance criteria, I/O examples, semantic metadata, versioned snapshots.                | Improve **structure** of your PRDs so agents (and reviewers) have clearer, machine-friendly criteria. [Ref](https://prodmoh.com/blog/agentic-prd).                                                   |
| **Cursor 2.0 parallel agents**         | Up to 8 agents in parallel (e.g. different worktrees). Plan mode: one model plans, another builds.                          | Use **multiple MCP task subagents in parallel** in one turn (research + arch + codebase) then merge findings. [Ref](https://cursor.com/changelog/2-0).                                               |
| **Compound-engineering deepen-plan**   | Enhances a plan with skills, learnings, per-section research, and **all** review agents in parallel.                        | Run **`/deepen-plan docs/plans/<your-plan>.md`**; optionally extend the command to add “external feasibility” steps (Timefold/Bryntum) explicitly.                                                   |
| **OpenCode-style autonomous workflow** | Plan → review → implement → PR from an issue; TDD default.                                                                  | Inspiration for a **single orchestrator prompt** that runs plan review → research → verify code → verify arch. [Ref](https://gist.github.com/ppries/f07fd6316bbd45807dd7a1896555b05b).               |

---

## 4. Recommended: PRD/plan review pipeline in Cursor

Use **one Cursor session** (or one command) that:

1. **Input:** Path to a PRD or implementation plan (e.g. `docs/docs_2.0/05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md` or `docs/plans/2026-02-25-ai-chat-schedule-integration.md`).
2. **Expert review (optional):** One **code-reviewer** or **architecture-strategist** subagent to critique the plan/PRD for gaps, risks, and clarity.
3. **External feasibility:** Run **parallel** subagents:
   - **framework-docs-researcher** or **best-practices-researcher** for **Timefold** (guides, API, from-patch, recommendations).
   - **framework-docs-researcher** or **explore** for **Bryntum** (Scheduler Pro, AI integration, ChatPanel).
   - Add more (e.g. GraphQL, Prisma) if the plan touches them.
4. **Verify with code:** One **explore** or **generalPurpose** subagent with prompt: “Given this plan [paste section], list the exact files and symbols in repo beta-appcaire that would be created or modified; confirm they match the plan and our architecture (apps/ vs packages/, resolver layout, etc.).”
5. **Verify architecture:** One **architecture-strategist** subagent: “Review this plan against appcaire-monorepo rules: resolver structure, package purity, GraphQL direct hooks, docs in docs/, no config changes without approval. List violations and suggestions.”
6. **Synthesis:** You (or a final agent) merge findings into a short report: feasibility, risks, arch compliance, and recommended plan changes.

### How to run it today (no new plugin)

- **Option A — Ad hoc in Cursor:**  
  Paste the plan/PRD and say: “Run a PRD review: (1) Spawn framework-docs-researcher for Timefold and Bryntum feasibility, (2) Spawn architecture-strategist to check this plan against our monorepo rules, (3) Spawn one agent to verify the plan’s file paths and components exist or are correctly proposed. Summarize findings.”
- **Option B — Command:**  
  Add a Cursor command (e.g. `.cursor/commands/prd-plan-review.md`) that encodes the steps above and asks for a plan/PRD path, then invokes **mcp_task** for each subagent type (explore, framework-docs-researcher, architecture-strategist) in parallel and tells you to synthesize.
- **Option C — After deepen-plan:**  
  Run **`/deepen-plan docs/plans/<plan>.md`** first, then in a follow-up say: “Spawn framework-docs-researcher for Timefold and Bryntum against this deepened plan and list feasibility and version/API risks.”

---

## 5. Be-agent-service: optional “PRD review” orchestrator

If you want this in **be-agent-service** (e.g. nightly or on-demand):

- Add a **new orchestrator prompt** (e.g. `agents/prompts/prd-review-orchestrator.md`) that:
  - Reads a **path to a PRD or plan** (from a priority file or env).
  - Spawns in parallel: research agents (Timefold, Bryntum), verification specialist (codebase fit), and a reviewer that checks against `docs/ARCHITECT_PROMPT.md` / appcaire-monorepo.
  - Writes a **review report** to `reports/prd-review-YYYY-MM-DD-<name>.md`.
- Keep **Orchestrator** and **CPO/CTO** as-is; the PRD-review flow is a **separate pipeline** triggered when the priority is “review PRD X” rather than “implement priority 1.”

---

## 6. Summary

| Question                                           | Answer                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Why only one plan in `docs/plans/`?                | By convention, writing-plans saves one canonical plan per feature there; many other plans live in `.cursor/plans/`.                                                                                                                                                                           |
| Better plugin/skill/agent/command for PRD review?  | **deepen-plan** is the closest; add explicit “external feasibility” (Timefold, Bryntum) and “verify with code” / “verify arch” via **mcp_task** subagents (see section 4).                                                                                                                    |
| What exists online?                                | MetaGPT (multi-agent PRD), agentic PRD structure, Cursor 2.0 parallel agents, compound deepen-plan, OpenCode-style workflows.                                                                                                                                                                 |
| How to get expert agents + research + code + arch? | Use **mcp_task** in Cursor to run in parallel: **framework-docs-researcher** (Timefold, Bryntum), **architecture-strategist** (arch rules), **explore** (codebase verification), then synthesize. Optionally add a **prd-plan-review** command or a be-agent-service PRD-review orchestrator. |
