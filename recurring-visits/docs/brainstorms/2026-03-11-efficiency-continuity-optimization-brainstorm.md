---
date: 2026-03-11
topic: efficiency-continuity-optimization
sources: parallel deep research (HHCRSP literature), timefold-specialist, optimization-mathematician, CONTINUITY_STRATEGIES, optimization-research-scripts
---

# Optimize efficiency and continuity (science-backed)

Brainstorm on how to improve **efficiency** (visit/(visit+travel+wait), fewer unassigned) and **continuity** (fewer distinct caregivers per client, KOLADA-aligned) in our home-care FSR pipeline using findings from operations research and our existing Timefold FSR setup.

## What we're building toward

- **Efficiency:** Higher wait efficiency; fewer unassigned visits; optional travel reduction.
- **Continuity:** Lower average distinct caregivers per client over the planning horizon (e.g. ≤11 or KOLADA target); stable assignments where possible.
- **Constraint:** Keep using Timefold FSR (and optionally ESS) and our current input/output pipeline; no full replacement of the solver.

## Scientific grounding (deep research summary)

The literature on the **Home Health Care Routing and Scheduling Problem (HHCRSP)** treats our setting: routing and assigning caregivers to patients with **two main objectives**—operational efficiency (travel, overtime, staff count) and **continuity of care** (consistent caregiver–patient assignments).

- **Continuity metrics:** Besides “count of unique nurses per client,” research uses the **Continuity of Care Index (CCI)**, which accounts for visit frequency and distribution across caregivers. We currently use unique-count (KOLADA-style); adding CCI or a CCI-inspired metric is a possible enhancement.
- **Modeling continuity:** Continuity is often modeled as a **soft constraint** (penalty for caregiver switches or deviation from preferred assignments) rather than only hard caps. Our `preferredVehicles` + `preferVisitVehicleMatchPreferredVehiclesWeight` align with this; we can tune weights and pool design.
- **Multi-objective:** Trade-offs are handled via weighted-sum, epsilon-constraint, or Pareto methods (e.g. NSGA-II). Our config weights (prefer visit vehicle, minimize wait, minimize travel) are a weighted-sum; we can systematically explore the curve (e.g. continuity vs efficiency).
- **Integrated routing and rostering:** Studies show that **integrated** routing and rostering can improve continuity with only a **marginal cost increase**. That supports combining FSR with shift-level decisions (ESS or pre-assignment) rather than optimizing routing in isolation.
- **Multi-period and blueprints:** Multi-period planning and “blueprint routes” (master plans that daily routes align to) help continuity across days. Our 2-week horizon and first-run → pool → re-solve pattern are steps in that direction; we can make pool construction and re-solve strategy more explicit.
- **Solution methods:** Metaheuristics (ALNS, VNS, Tabu Search) and matheuristics are standard for large instances. Timefold’s solver fits this picture; we optimize by **input design** (pools, weights, constraints) and **strategy sequencing** (e.g. first-run → preferred/required pools → weight tuning).

Full report: `recurring-visits/efficiency-continuity-optimization.md` (and `.json`).

## Approaches (2–3 options)

### Approach A: Weight and pool tuning (within current FSR)

**Description:** Keep current pipeline (first-run → build pools → preferred/required vehicles). Systematically tune **config weights** (e.g. `preferVisitVehicleMatchPreferredVehiclesWeight` 2 → 10 → 20) and **pool size/capping** (e.g. 15 → 10 → 8 per client). Run multiple strategies (preferred-only, wait-min, combo, requiredVehicles with smaller pools) and compare efficiency vs continuity (Pareto-style comparison). Optionally introduce a **CCI-like metric** alongside unique-count for reporting.

**Pros:** Uses existing scripts and Timefold; no new services; aligns with literature’s soft-constraint and weighted-sum practice.  
**Cons:** FSR still has no native “max distinct vehicles per client”; we only approximate via pools and weights.

**Best when:** We want quick, comparable experiments and clearer Pareto trade-offs with minimal new code.

---

### Approach B: Integrated rostering + routing (ESS then FSR)

**Description:** Use **Employee Shift Scheduling (ESS)** to assign caregivers to “client zones” or shift templates first; then run **FSR** with those assignments as strong preferences (or required vehicles per client). Iterate: FSR output → continuity/metrics → feed back into next ESS/FSR run (e.g. preferred vehicles from last solution). This mirrors the literature’s “integrated routing and rostering” and “blueprint” ideas.

**Pros:** Aligns with research showing that integration improves continuity with small cost impact; uses Timefold ESS + FSR.  
**Cons:** Requires ESS model design, data mapping, and an orchestration layer (e.g. in `optimization-research-scripts` or a small service).

**Best when:** We are ready to invest in a two-stage (roster → route) pipeline and want structural improvement in continuity.

---

### Approach C: Continuity-first pool design and metrics

**Description:** Focus on **how we build and update pools** and **how we measure** continuity. (1) Pool design: try area-based, first-run top-K, and “blueprint” (fix a small set of preferred caregivers per client from a reference solution and re-solve). (2) Metrics: add **CCI** (or a simplified proportion-of-visits-by-primary-caregiver) next to unique-count; report both in `continuity_report.py` and in the optimization-mathematician’s goals. (3) Keep running multiple FSR strategies but with clearer continuity targets (e.g. CCI ≥ X, unique-count ≤ Y).

**Pros:** Better alignment with literature (CCI); more informed pool strategies; clearer success criteria for the mathematician.  
**Cons:** CCI implementation and target-setting require definition; pool strategies need documentation and comparison runs.

**Best when:** We want to improve both the *definition* of continuity and the *pool logic* before or in parallel to heavier weight/orchestration work.

---

## Recommendation

- **Short term:** **Approach A** (weight and pool tuning) — lowest friction, uses existing variants and scripts; run a small “Pareto” campaign (e.g. preferred weight 2, 10, 20; wait-min; combo; required with smaller pool) and record efficiency vs continuity.
- **Next:** Add **Approach C** (CCI or CCI-like metric + pool design doc) so we measure and compare strategies in a science-backed way.
- **Later:** **Approach B** (ESS + FSR) when we are ready to design shifts/zones and an orchestration loop.

## Key decisions

- Treat **efficiency** as wait efficiency (visit/(visit+travel+wait)); **continuity** as unique caregivers per client (KOLADA) and optionally CCI.
- Keep **multiple strategies** (preferred, wait-min, combo, required with different pool sizes) and compare them on the same dataset.
- Use **deep research report** as reference for metrics (CCI), modeling (soft continuity), and integration (routing+rostering).
- Keep **optimization-mathematician** goals (unassigned &lt;1%, continuity ≤11, efficiency &gt;70%) as targets; add CCI as optional target once defined.

## Open questions

*(None; see Resolved below.)*

## Resolved questions

1. **CCI:** Add CCI (or simplified version). Start with **scripts and metrics only** for quick prototyping and strategy finding; dashboard code flow later. User can upload optimized JSONs to dashboard and show key metrics for now.
2. **Pool size:** Test **max 10** per client; Huddinge manual schedules are single digits; slinga can be different caregivers (sickness, shift swaps) so real continuity is often higher. Try **5–10 range** in campaigns.
3. **ESS scope:** ESS (and ESS+FSR integration) **later**; not in current implementation scope.
4. **Execution:** Run **Approach A** and **Approach B** in parallel with subagents. Implementation plan created from this brainstorm.

**Implementation plan:** [2026-03-11-efficiency-continuity-implementation-plan.md](../plans/2026-03-11-efficiency-continuity-implementation-plan.md)

## References

- `recurring-visits/efficiency-continuity-optimization.md` — full deep research report.
- `docs/CONTINUITY_STRATEGIES.md` — pool strategies (manual, first-run, area-based, ESS+FSR).
- `docs/CONTINUITY_TIMEFOLD_FSR.md` — FSR required/preferred vehicles and 15-vehicle cap.
- `docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md` — weights and preferred/required combo.
- `agents/prompts/timefold-specialist.md`, `optimization-mathematician.md` — FSR/ESS and strategy goals.
- `recurring-visits/optimization-research-scripts/` — strategic runs, Pareto, campaigns.
