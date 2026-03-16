# Timefold Roadmap Relevance for ESS-FSR

> **Purpose:** Map Timefold product roadmap items to CAIRE ESS+FSR architecture and priorities.  
> **Source:** Timefold community/roadmap (as of 2025). Status and timelines are Timefold’s.  
> **Related:** [USING_ESS.md](./USING_ESS.md), [CONTINUITY_AND_PRIORITIES.md](./CONTINUITY_AND_PRIORITIES.md), [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ESS_FSR_DUAL_MODEL_ARCHITECTURE.md)

---

## 1. Demand-curve based shift creation

**Timefold:** Solver would create shifts from demand curve + employees/contracts (instead of user creating shifts; solver only assigns). Input: employees, contracts, demand curve per day. Output: created shifts + assignments.

**Relevance for CAIRE:**

- **High.** Our flow today: we generate a demand curve from visits → we (or a separate step) create candidate shifts → ESS assigns employees to those shifts → FSR routes. If Timefold ESS could create shifts from demand + employees/contracts, we could:
  - Simplify the pipeline: send demand + employees/contracts, get shifts + assignments.
  - Align with “planner says schedule all visits, CAIRE handles everything” (see [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ESS_FSR_DUAL_MODEL_ARCHITECTURE.md)).
- **Architecture impact:** Could reduce or replace our “demand curve → shift generation” logic; ESS would own shift creation. We’d still need ESS→FSR bridge (shifts → vehicles) and convergence loop.

**Use when:** Planning long-term simplification of the ESS integration or discussing “shift creation” with Timefold.

---

## 2. Overview of unassigned shifts in the visualization

**Timefold:** In solved ESS, show which shifts (or demand) remain unassigned in the UI.

**Relevance for CAIRE:**

- **High for operations and tuning.** Our first priority is **0 unassigned** ([CONTINUITY_AND_PRIORITIES.md](./CONTINUITY_AND_PRIORITIES.md)). Seeing exactly which shifts/demand are unassigned would:
  - Help planners and support fix understaffing (add shifts, adjust input).
  - Make convergence debugging easier (unassigned after ESS vs after FSR).
- **Where it fits:** Dashboard/visualization that consumes ESS (and optionally FSR) results; also relevant for “0 empty shifts” and metrics validity.

**Use when:** Defining dashboard requirements for ESS results or discussing visualization with Timefold.

---

## 3. What-if scenarios (e.g. via Copilot)

**Timefold:** Easily tweak the problem (e.g. +20% workload, +3 employees, longer breaks), run experiments, compare results (ideally with no-code tools / Copilot).

**Relevance for CAIRE:**

- **High for product and sales.** The dual-model doc already calls out **Manager: “efficiency X-ray, what-if scenarios”** ([ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ESS_FSR_DUAL_MODEL_ARCHITECTURE.md)). What-if would support:
  - Capacity planning: “What if we have 3 more employees?”
  - Demand sensitivity: “What if visit volume grows 20%?”
  - Policy: “What if lunch breaks were 10 minutes longer?”
- **Implementation:** Could align with a future “scenario” or “simulation” feature that re-runs ESS (and optionally FSR) with modified inputs and compares KPIs.

**Use when:** Roadmapping planner/manager features or discussing Copilot/Platform with Timefold.

---

## 4. Automated hyper-tuning of constraint weights / target metrics

**Timefold:** Instead of manually tuning constraint weights, define target values for output metrics and let Timefold find suitable weights (e.g. via hyper-tuning).

**Relevance for CAIRE:**

- **High for tuning and benchmarks.** We today “test different Timefold config profiles to see how weights affect results” to approach **field efficiency > 67.5%** ([CONTINUITY_AND_PRIORITIES.md](./CONTINUITY_AND_PRIORITIES.md)). Multi-objective trade-offs (unassigned vs efficiency vs continuity) are hard to tune by hand; target-based tuning would:
  - Reduce trial-and-error when optimizing for efficiency, continuity, and labor law.
  - Make it easier to hit and explain target metrics (e.g. “67.5% efficiency, &lt;15 caregivers per client”).
- **Scope:** Applies to ESS and potentially FSR; our iterative ESS+FSR loop would still need a single set of “targets” or per-model targets and a clear mapping to our KPIs.

**Use when:** Defining tuning strategy, benchmarking, or discussing constraint/metrics APIs with Timefold.

---

## Summary

| Roadmap item                       | CAIRE impact                          | Primary doc to align with             |
| ---------------------------------- | ------------------------------------- | ------------------------------------- |
| Demand-curve based shift creation  | Simplify pipeline; ESS creates shifts | ESS_FSR_DUAL_MODEL_ARCHITECTURE, flow |
| Unassigned shifts in visualization | 0 unassigned priority; debugging      | CONTINUITY_AND_PRIORITIES, dashboard  |
| What-if scenarios (Copilot)        | Manager scenarios; capacity planning  | ESS_FSR_DUAL_MODEL_ARCHITECTURE       |
| Hyper-tuning / target metrics      | Hit efficiency/continuity targets     | CONTINUITY_AND_PRIORITIES, metrics    |

When discussing roadmap with Timefold or prioritizing our own work, this mapping helps keep ESS-FSR and Timefold evolution aligned.

**CAIRE feature roadmap:** For how each CAIRE product feature is achieved with ESS and FSR, see [CAIRE_FEATURE_ROADMAP.md](./CAIRE_FEATURE_ROADMAP.md).
