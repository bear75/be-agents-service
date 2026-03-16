# ESS-FSR vs pricing branch split

**Purpose:** Separate mixed changes on `feature/ess-fsr-integration` so that:

- **`feature/ess-fsr-integration`** contains only: plans, docs, scripts, and Timefold-related env for **research/testing Timefold** (no billing, Clerk sync, Stripe, dashboard scheduler UI, or handbook deploy).
- **`feature/pricing-and-billing-only`** (PR [#67](https://github.com/CairePlatform/beta-appcaire/pull/67)) contains: pricing, billing, products, Stripe, Clerk sync, and related app changes. Those changes currently on ess-fsr should be **cherry-picked to the pricing branch** and will merge to main when that PR is ready.

---

## 1. What’s from main

- Both branches share history with `main` up to their merge bases.
- **Merge bases (as of analysis):**
  - `main` ↔ `feature/ess-fsr-integration`: `b09eea37`
  - `main` ↔ `feature/pricing-and-billing-only`: `90dbcfcd`
- Everything in `main` up to those points is “from main.” Current `main` may be ahead (e.g. `4909b8d3`); neither branch should assume they have the very latest main until they rebase/merge.

---

## 2. What’s on ess-fsr that should **not** merge to main (→ cherry-pick to pricing)

These are changes that belong in **feature/pricing-and-billing-only** and should be cherry-picked there (or already exist there). They should **not** be merged to main via the ess-fsr branch.

| Area                                                       | Files / topics                                                                                                                                                                                                                                                                                   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Billing / Stripe / products**                            | `apps/dashboard-server` billing resolvers (`createPortalSession`, `subscription`), `stripe-webhooks`, env constants for Stripe/Timefold used by dashboard-server billing; dashboard Billing/Products UI if present on ess-fsr.                                                                   |
| **Clerk sync**                                             | `apps/dashboard-server/src/scripts/sync-clerk-to-db.ts`, `apps/dashboard-server/src/services/clerk/`, `ensureOrganizationsFromClerk.ts`, `auth.ts` changes for Clerk.                                                                                                                            |
| **Dashboard scheduler UI** (product feature, not research) | Scheduler theme, event renderers, `SchedulerContainer`, `useResourceHistogramConfig`, `useResourceUtilizationConfig`, `useSchedulerConfig`, `useUnplannedSchedulerConfig`, `UploadCsvModal` – when these are for “shipping” scheduler/billing, not for Timefold research scripts.                |
| **Handbook**                                               | `apps/handbook-server/` Dockerfile, package.json, seed/align scripts (`align-migration-history.sh`, `seed-prod-db.sh`, etc.), and handbook-related docs (e.g. `HANDBOOK_DB_DEVOPS_SEED_HANDOFF.md`, `HANDBOOK_SERVER_MIGRATION_RECOVERY.md`) that support deploy/billing, not Timefold research. |
| **Misc**                                                   | `.github/PR_BODY_push-from-main.md` if it’s just workflow draft; any other one-off fixes that are clearly pricing/billing/product/deploy.                                                                                                                                                        |

**Action:** Cherry-pick the commit below onto `feature/pricing-and-billing-only`. Do **not** merge ess-fsr into main with these changes.

**Commit to cherry-pick onto `feature/pricing-and-billing-only`:**

- **`d322154a`** — `feat(dashboard): integrate Clerk service and add sync script`  
  Adds: `sync-clerk-to-db.ts`, `services/clerk/`, billing resolver updates (`createPortalSession`, `subscription`), `stripe-webhooks`, `auth.ts`, `ensureOrganizationsFromClerk.ts`.  
  The pricing branch currently does **not** have the Clerk sync script or clerk service; this commit brings them in.

```bash
git checkout feature/pricing-and-billing-only
git pull origin feature/pricing-and-billing-only
git cherry-pick d322154a
# Resolve conflicts if any (e.g. package.json, resolver imports), then:
git push origin feature/pricing-and-billing-only
```

**Note:** The other commits on ess-fsr (`0d1f6d4a`, `481fc78f`, `ec5110e9`, `d3b31fed`) are mixed: they contain ESS-FSR plans/docs plus some handbook scripts and consistency docs. If you need those handbook/consistency bits on the pricing branch too, either cherry-pick selected file changes from those commits or add them manually; the cleanest long-term is to keep ess-fsr as “ESS-FSR only” and have pricing own all billing/Clerk/handbook deploy content.

---

## 3. What **should** stay on ess-fsr (plans, docs, scripts, Timefold env)

These are the only things that should remain on **feature/ess-fsr-integration** and eventually merge to main as “ESS-FSR research / Timefold support” (or stay on a long-lived research branch).

| Category                            | Paths / content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cursor agents / commands**        | `.cursor/agents/tf-fsr-prototype.md`, `.cursor/commands/continuity-compare.md`, `.cursor/commands/fetchtimefoldsolution.md`, `.cursor/commands/prd-plan-review.md`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Cursor plans** (Timefold/ESS-FSR) | `.cursor/plans/` – continuity, timefold, ESS-FSR, prd tasks/timefold, timefold guides, yarn generate and ESS continuity docs. (Drop plans that are only about products-access gate, billing, or non–Timefold work.)                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Docs – Timefold / ESS-FSR**       | `docs/TIMEFOLD_ESS_FSR_ENV.md`, `docs/timefold.env.example`, `docs/docs_2.0/09-scheduling/` (README, TIMEFOLD*GUIDES_ALIGNMENT, `ess-fsr/` folder: CAIRE_FEATURE_ROADMAP, CONTINUITY_AND_PRIORITIES, ESS_FSR*\*, USING_ESS, etc.), `docs/docs_2.0/05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md`, `docs/docs_2.0/10-consistency/` (PRD_PLAN_REVIEW_WORKFLOW, PRE_JIRA_SYNC_REVIEW_AND_DEV_HANDOFF), `docs/plans/2026-02-25-ai-chat-schedule-integration.md`, `docs/brainstorms/2026-02-25-ai-chat-schedule-brainstorm.md`, `docs/solutions/logic-errors/timefold-fsr-shift-deduplication-source-csv.md`, `docs/UPLOAD_SCHEDULE_CODEX_ANALYSIS.md`. |
| **Scripts for research**            | Scripts under `docs_2.0/recurring-visits/` or elsewhere that are **only** for running Timefold (fetch, submit, continuity compare, etc.) and research – not for handbook seed or deploy.                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Env / example**                   | `docs/timefold.env.example` and any doc references to `.env.timefold` / `~/.config/caire/env` for agent service (so the agent can run Timefold research). No real keys in repo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

**Dashboard-server Timefold client for research:** If `apps/dashboard-server/src/services/timefold/ESSClient.ts`, `ess.types.ts`, and `index.ts` exist **only** to support research/scripts (e.g. run from compound/agent), they can stay on ess-fsr. If they are required for the “shipping” dashboard billing/scheduler feature, they belong with pricing/billing and should be on the pricing branch instead; clarify per your product boundary.

---

## 4. Summary table

| Destination                                     | Content                                                                                                                                                                                                              |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **From main**                                   | Already in main; both branches should rebase/merge main when appropriate.                                                                                                                                            |
| **→ feature/pricing-and-billing-only (PR #67)** | Billing, Clerk sync, Stripe, products, handbook deploy/seed, dashboard scheduler UI and dashboard-server code that serves production billing/scheduling. Cherry-pick from ess-fsr; do not merge to main via ess-fsr. |
| **→ feature/ess-fsr-integration only**          | Plans, docs, scripts, and Timefold env for research; optional dashboard-server Timefold client if research-only. This branch can merge to main when you want “ESS-FSR research / Timefold env” in main.              |

---

## 5. Suggested git workflow

1. **On your machine (or agent runner):**
   - Ensure you have `feature/pricing-and-billing-only` and `feature/ess-fsr-integration` and latest `main`.
2. **Cherry-pick onto pricing:**
   - From `feature/ess-fsr-integration`, identify commits that **only** touch billing/Clerk/Stripe/handbook/dashboard UI (or the minimal set that contains those changes). Cherry-pick them onto `feature/pricing-and-billing-only` and fix conflicts. Push to update PR #67.
3. **Trim ess-fsr branch:**
   - Option A (cleanest): Create a new branch from current `main`, then add only the ESS-FSR-only files (plans, docs, scripts, `timefold.env.example`, TIMEFOLD_ESS_FSR_ENV.md, etc.) via new commits or cherry-pick of the “research-only” commits. Force-push to `feature/ess-fsr-integration` (coordinate with team).
   - Option B: Revert or drop the “pricing/billing/Clerk” commits on ess-fsr so the branch only contains the ESS-FSR research commits, then force-push.
4. **PR #77 (ess-fsr):** After the trim, PR #77 should show only the ESS-FSR research-related changes. Update the PR description to match.

---

## 6. References

- PR pricing/billing: [beta-appcaire #67](https://github.com/CairePlatform/beta-appcaire/pull/67)
- PR ess-fsr: [beta-appcaire #77](https://github.com/CairePlatform/beta-appcaire/pull/77)
- Timefold env: `docs/TIMEFOLD_ESS_FSR_ENV.md`, `docs/timefold.env.example`
