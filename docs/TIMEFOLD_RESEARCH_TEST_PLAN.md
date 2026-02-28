# Research → Test Plan (from handoff analysis)

**Date:** 2026-02-28  
**Source:** Handoff `memory/TIMEFOLD_RESEARCH_HANDOFF_2026-02-28.md` + report `timefold-ess-fsr-best-practices.md`  
**Owner:** Timefold Specialist + Optimization Mathematician

---

## Adopted recommendations (test first)

| # | Recommendation | Owner | Test approach |
|---|----------------|-------|---------------|
| 1 | **Shift-then-route** (ESS then FSR) | Timefold Specialist | Run ESS for Huddinge 2w to get rosters; use output as fixed shifts into one FSR run. Compare: same dataset FSR-only vs ESS+FSR on unassigned %, continuity, efficiency. |
| 2 | **Pinning/locking** for re-optimization | Timefold Specialist | Use existing from-patch + pin assigned visits; add one run that “locks” 80% of assignments and re-solves. Validate no regression in metrics. |
| 3 | **Hard vs soft policy** (work rules vs weighted objectives) | Optimization Mathematician | Document current vehicleGroup/requiredVehicle as “hard” and preferred-vehicle as “soft”; propose one strategy that tightens soft weight only. Compare continuity vs baseline 82a338b9. |
| 4 | **Continuous benchmarking** | Both | Ensure every run is recorded in Darwin (POST /api/schedule-runs) with full metrics; use `docs/SCHEDULE_OPTIMIZATION_TESTING.md` seed + loop so we can replay. |

---

## Concrete test steps

1. **Regression (before any new strategy)**  
   - Run `./scripts/compound/schedule-optimization-loop.sh huddinge-2w-expanded --dry-run` → must complete, mathematician returns strategies.  
   - `curl -s http://localhost:3010/api/schedule-runs?dataset=huddinge-2w-expanded` → returns 200 and JSON.  
   - Seed DB, open http://localhost:3010/schedules → pipeline, scatter, table render.

2. **Baseline vs “best practice” run**  
   - One FSR run with current best config (from-patch trim-empty, 82a338b9-style).  
   - One FSR run with one change from report (e.g. double preferred-vehicle weight).  
   - Compare: unassigned_pct, continuity_avg, routing_efficiency_pct. Success = same or better on all three goals.

3. **Shift-then-route (when ESS ready)**  
   - Export ESS roster (who works when) for Huddinge 2w.  
   - Build FSR input that only uses those shifts as vehicles.  
   - Run FSR; compare to FSR-only baseline. Success = unassigned <1%, continuity ≤11, efficiency ≥70%.

4. **Dynamic re-optimization (later)**  
   - Take a completed run; pin 80% of visits; add 5 “new” visits; re-solve.  
   - Check: pinned visits unchanged, new visits assigned, score feasible.

---

## Success criteria (unchanged)

- **Unassigned:** <1% (≤36 of 3622)  
- **Continuity:** ≤11 avg distinct caregivers per client  
- **Routing efficiency:** >70% (Wait efficiency = visit/(visit+travel+wait))

---

## Where this lives

- **Repo:** `be-agents-service/docs/TIMEFOLD_RESEARCH_TEST_PLAN.md`  
- **Darwin:** `memory/TIMEFOLD_RESEARCH_TEST_PLAN_2026-02-28.md` (same content for shared-folder execution)
