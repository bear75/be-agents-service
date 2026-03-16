# Using ESS (Employee Shift Scheduling)

This document explains **when** ESS is used, **how to enable it** (staging), and how it interacts with FSR and **continuity**.

## When ESS is used

- **ESS is used when staffing is unknown:** unplanned schedules, new slinga creation, pre-planning movable visits. ESS decides who works when; FSR then routes visits to those shifts.
- **FSR-only when shifts are known:** e.g. schedules from an existing slinga. Only route optimization runs; no ESS call.

## Enabling ESS (staging)

Set the following in `apps/dashboard-server/.env`:

- `TIMEFOLD_ESS_BASE_URL` — optional; defaults to `https://app.timefold.ai/api/models/employee-shift-scheduling/v1`
- `TIMEFOLD_ESS_API_KEY` — required when any code path invokes ESS

For the staging API key and full env table, see **[docs/TIMEFOLD_ESS_FSR_ENV.md](../../../TIMEFOLD_ESS_FSR_ENV.md)**.

## Flow

1. **Demand curve** — Travel-adjusted hourly demand from visits (and optional learned/geographic overhead).
2. **ESS** — Shift assignments (who works when).
3. **ESS→FSR bridge** — Map ESS shifts to FSR vehicles (with locations, breaks).
4. **FSR** — Route optimization for those vehicles and visits.
5. **Convergence check** — Compare actual efficiency vs target, unassigned count; if not converged and iteration &lt; 3, adjust demand and repeat from step 1.

For the full iterative loop and architecture, see **[ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ESS_FSR_DUAL_MODEL_ARCHITECTURE.md)**. For implementation todos and phases, see **[ESS_FSR_PROJECT_PLAN.md](./ESS_FSR_PROJECT_PLAN.md)**. For how Timefold roadmap items (demand-curve shift creation, unassigned visualization, what-if, hyper-tuning) relate to this flow, see **[TIMEFOLD_ROADMAP_RELEVANCE.md](./TIMEFOLD_ROADMAP_RELEVANCE.md)**. For how each CAIRE feature is delivered via ESS and FSR, see **[CAIRE_FEATURE_ROADMAP.md](./CAIRE_FEATURE_ROADMAP.md)**. Multi-area schedules (one solve spanning 2+ nearby service areas for shared employees) are in **[SCHEDULING_ADVANCED_PLANNING_PRD.md](../../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md)** US-2 and **[TIMEFOLD_GUIDES_ALIGNMENT.md](../TIMEFOLD_GUIDES_ALIGNMENT.md)**.

## Continuity with ESS

- **Cross-iteration:** After each FSR run, the assignment (which employee visited which client) is fed back as **`preferredVehicles`** on visits in the next FSR run. Target: &lt;10–15 different caregivers per client per 14 days.
- **Hard cap of 15 in FSR today:** FSR has no native “max distinct vehicles per client” constraint. To enforce a hard cap, use a **precomputed pool** (manual, first-run, or area-based) and set **`requiredVehicles`** on all visits of each client to that pool (size ≤ 15). ESS+FSR then refines who serves whom **inside** that pool via preferences.

See **[CONTINUITY_AND_PRIORITIES.md](./CONTINUITY_AND_PRIORITIES.md)** for the priority order and continuity goal. For pool strategies (manual, first-run, area-based), see the FSR prototype doc `docs_2.0/recurring-visits/docs/CONTINUITY_STRATEGIES.md` in the appcaire repo.

## Code

- **ESS client:** `createESSClient()` from `apps/dashboard-server/src/services/timefold/`. Requires `TIMEFOLD_ESS_API_KEY` when ESS is invoked (constructor throws if key is missing).
- **Exports:** `ESSClient`, `createESSClient`, and types from `ess.types.ts` are exported from the timefold service index.
