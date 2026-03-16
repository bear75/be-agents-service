# Timefold Research Handoff — For Agent Team Analysis & How to Test

**Date:** 2026-02-28  
**Audience:** Timefold Specialist, Optimization Mathematician (Schedule optimization team)  
**Ask:** Analyze the deep-research report below and **propose how to test** its recommendations against our Huddinge FSR/ESS pipeline. Do not reinvent the wheel; align with industry best practices where they fit.

---

## 1. Where the research lives

| Asset | Location |
|-------|----------|
| **Full report (Markdown)** | `be-agents-service/timefold-ess-fsr-best-practices.md` (repo root) |
| **Metadata + basis (JSON)** | `be-agents-service/timefold-ess-fsr-best-practices.json` |
| **This handoff** | `be-agents-service/docs/TIMEFOLD_RESEARCH_HANDOFF.md` |
| **Existing testing guide** | `be-agents-service/docs/SCHEDULE_OPTIMIZATION_TESTING.md` |

---

## 2. Executive summary (from Parallel deep research)

The landscape for home care and field service scheduling is a **demand–supply matching problem**: assign caregivers (skills, time windows), meet compliance (breaks, hours), balance fairness, optimize routes, and handle cancellations/emergencies.

**Three main approaches:**

1. **Commercial platforms (e.g. Timefold)** — Off-the-shelf ESS and FSR models, pre-built constraints; faster to implement.
2. **Open source solvers** — e.g. **Google OR-Tools** (CP-SAT + routing), **VROOM** (vehicle routing). Strong for sub-problems; more DIY to integrate.
3. **Custom builds** — Following patterns from Dynamics 365 RSO / Salesforce Field Service: hard constraints (work rules) vs tunable soft objectives.

**Timefold** (open-source, OptaPlanner lineage) provides both a strong solver and standardized ESS/FSR models — a good fit for our stack.

**Recommended pattern:** **Hybrid “shift-then-route”**: first build compliant rosters (shifts/coverage), then optimize daily routes. Aligns with our FSR + ESS split and scales well.

---

## 3. Ask for the Timefold agent team

1. **Analyze** the full report (`timefold-ess-fsr-best-practices.md`) and extract:
   - Recommendations that map directly to our current pipeline (Huddinge 2w, continuity vs efficiency, FSR + optional ESS).
   - Gaps: what we are not yet doing that the report recommends (e.g. pinning/locking, dynamic re-optimization, shift-then-route as a formal two stage).
   - Any references to open source alternatives (OR-Tools, VROOM) that we should compare or prototype.

2. **Propose how to test:**
   - **Which best practices** to adopt first and how to validate them (e.g. one baseline run vs one “with new practice” run).
   - **Concrete test plan**: steps, datasets, success criteria (aligned with existing goals: unassigned &lt;1%, continuity ≤11 avg, routing efficiency &gt;70%).
   - **Shift-then-route**: if we introduce ESS as Stage 1, how do we test that the resulting FSR (Stage 2) improves or at least matches current FSR-only metrics?
   - **Regression checks**: how to ensure new strategies don’t break existing loop/dashboard (dry-run, then one live run with a small batch).

3. **Output** the team can produce:
   - A short **“Research → test plan”** note (in `docs/` or Darwin `memory/`) listing: adopted recommendations, test steps, and owner (Timefold Specialist vs Optimization Mathematician).
   - Optional: updated strategy families or cancellation heuristics in the Optimization Mathematician prompt if the report suggests new exploration directions.

---

## 4. How you (agents) are invoked

- **Timefold Specialist:** Submits/monitors/cancels FSR jobs, records metrics. Prompt: `agents/prompts/timefold-specialist.md`.
- **Optimization Mathematician:** Analyses runs, proposes next strategies. Prompt: `agents/prompts/optimization-mathematician.md`.
- **Loop:** `./scripts/compound/schedule-optimization-loop.sh huddinge-2w-expanded [--dry-run]` — fetches strategies from the mathematician and (in production) dispatches via appcaire Timefold scripts.
- **Testing doc:** All manual and API test steps: `docs/SCHEDULE_OPTIMIZATION_TESTING.md`.

When you analyze and propose tests, use this handoff and the full report; then add your “how to test” plan to docs or memory so the next run has a clear checklist.
