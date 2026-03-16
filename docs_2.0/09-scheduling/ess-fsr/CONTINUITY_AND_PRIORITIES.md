# Continuity and scheduling priorities

This document states the **priority order** for scheduling optimization and the **continuity goal** used in the platform and in the FSR prototype. It aligns beta-appcaire with the prototype’s mandatory order and links to strategy details.

## Priority order (mandatory first)

1. **0 unassigned** — Every visit must be assigned. From-patch does **not** add capacity; fix by updating input (add shifts, regenerate input, solve again).
2. **0 empty shifts** — After 0 unassigned, use from-patch to trim empty shifts or tune Timefold config.
3. **Metrics and efficiency** — Only then run metrics; target **field efficiency > 67.5%** (Slingor benchmark). Test different Timefold config profiles to see how weights affect results.
4. **Continuity** — High-priority goal: at most **15 distinct caregivers (vehicles) per client** over the 2-week window.

Metrics from runs with unassigned visits or empty shifts are **not valid** for benchmarking.

## Continuity goal

- **Target:** At most 15 distinct caregivers per client per 14 days.
- **In FSR:** FSR has no built-in “max distinct vehicles per client” constraint. Continuity is enforced by setting a **precomputed pool** of up to 15 vehicle IDs per client and using **`requiredVehicles`** on every visit of that client. The solver has full flexibility **within** that pool.
- **In ESS+FSR:** Across iterations, previous FSR assignment is fed back as **`preferredVehicles`** in the next FSR run to refine who serves whom. For a hard cap of 15 today, a pool (manual / first-run / area-based) + `requiredVehicles` is still used; ESS+FSR improves continuity **inside** that pool.

## Prototype references (FSR-only strategies)

Pool selection and comparison are documented in the **FSR prototype** (caire-platform/appcaire):

- **Continuity strategies:** `docs_2.0/recurring-visits/docs/CONTINUITY_STRATEGIES.md` — Manual, first-run, area-based, and ESS+FSR strategies; how to build and compare pools.
- **FSR model details:** `docs_2.0/recurring-visits/docs/CONTINUITY_TIMEFOLD_FSR.md` — `requiredVehicles` vs `preferredVehicles`; why “max 15” requires a precomputed pool; workaround and limits.
- **Pipeline priorities:** `docs_2.0/recurring-visits/huddinge-package/docs/PRIORITIES.md` — Input correctness, FSR config, rebalance demand/supply, metrics accuracy; from-patch does not add capacity.

Platform implementation of the iterative ESS+FSR loop and continuity is described in [USING_ESS.md](./USING_ESS.md) and [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ESS_FSR_DUAL_MODEL_ARCHITECTURE.md). For Timefold roadmap items that affect unassigned handling and metric tuning, see [TIMEFOLD_ROADMAP_RELEVANCE.md](./TIMEFOLD_ROADMAP_RELEVANCE.md). For how all CAIRE features map to ESS and FSR, see [CAIRE_FEATURE_ROADMAP.md](./CAIRE_FEATURE_ROADMAP.md). For unassigned visits: time-window recommendations (planner offers client alternative slots) are in [SCHEDULING_ADVANCED_PLANNING_PRD.md](../../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-1. Multi-area scheduling (one schedule spanning nearby areas) is in US-2 and [TIMEFOLD_GUIDES_ALIGNMENT.md](../TIMEFOLD_GUIDES_ALIGNMENT.md).
