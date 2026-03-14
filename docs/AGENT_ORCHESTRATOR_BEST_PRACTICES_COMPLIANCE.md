# Do we follow agent-orchestrator-service-best-practices?

Short compliance checklist: [agent-orchestrator-service-best-practices.md](agent-orchestrator-service-best-practices.md) and [agent-orchestrator-service-best-practices.json](agent-orchestrator-service-best-practices.json) vs this repo.

---

## Summary

| Area | Follow? | Notes |
|------|--------|--------|
| **Core principles** (simplicity, single-responsibility, plan-and-execute) | ✅ Partial | We use supervisor/worker; compound is plan-and-execute (PRD → loop). Not all flows use strict validation gates. |
| **State persistence** | ✅ Yes | `.compound-state/session-*` (orchestrator.json, backend.json, etc.); sync to DARWIN machine/agent-reports. |
| **Hierarchical supervisor/worker** | ✅ Yes | Orchestrator → specialists (backend, frontend, verification, etc.); Jarvis → marketing squad. |
| **Deterministic orchestration vs LLM** | ✅ Partial | Scripts drive steps (loop.sh, orchestrator.sh); LLM does task content. No formal graph/checkpointing. |
| **Reliability (timeouts, retries, validation)** | ⚠️ Partial | Some timeouts (Telegram API, state-manager poll). No retries/backoff/circuit breakers on agent runs; loop has max iterations. |
| **Observability / audit trail** | ✅ Partial | Session logs, orchestrator.log, sync to agent-reports; no OpenTelemetry/GenAI spans. |
| **Security (least privilege, HITL, sandbox)** | ⚠️ Partial | Env/secrets from config; no formal HITL for high-risk actions; agents run in repo context (no sandbox). |
| **When confused rule** | ✅ Yes | 1) Repo 2) DARWIN 3) Telegram — documented and linked. |

---

## What we follow

- **State externalized:** Orchestration state in `.compound-state/` (JSON per session); written by orchestrator and specialists; sync-to-workspace writes reports to DARWIN machine/agent-reports.
- **Single-responsibility agents:** Backend, frontend, verification, senior-code-reviewer, etc.; marketing has Shuri, Fury, Vision, Loki, etc., each with a clear role.
- **Plan-and-execute style:** Compound: priority → strategy (optional) → PRD → loop over tasks; orchestrator: priority → backend → frontend → verification → PR.
- **Input validation:** Orchestrator validates target_repo, priority_file, prd_file, branch_name before running.
- **Max iterations:** loop.sh has `MAX_ITERATIONS` (default 25) to avoid infinite loops.
- **Logging:** Orchestrator and compound write to logs (orchestrator-sessions, compound-commits.log, etc.).
- **When confused:** 1) Repo 2) DARWIN (memory + reports) 3) Ask over Telegram — in CLAUDE.md, README, and AGENTS_WHEN_CONFUSED.md.

---

## Gaps (we do not fully follow)

- **Retries / backoff / circuit breakers:** No retry with backoff on agent or LLM calls; no circuit breaker. (Only Telegram API has a timeout.)
- **Validation gates between agents:** No strict schema validation of one agent’s output before passing to the next; handoff is file/state based.
- **OpenTelemetry / GenAI spans:** No OTel instrumentation; no standard “Thought → Tool Call → Observation” trace.
- **HITL for high-risk actions:** No explicit approval step for e.g. code execution or destructive ops; agents run with repo access.
- **Sandboxing:** Agents run in repo directory with normal user permissions; no isolated runtime for code execution.
- **Formal red teaming / golden datasets:** No documented adversarial tests or golden-dataset evals in CI.

---

## How to use this

- **Product / ops:** We mostly follow structure and state; reliability and security are partially there; observability is log-based, not OTel.
- **Improvements:** Add retries/backoff for agent invocations; optional validation of PRD/task outputs; document HITL for any high-risk triggers; consider OTel or structured trace IDs for sessions.

Reference: [agent-orchestrator-service-best-practices.md](agent-orchestrator-service-best-practices.md).
