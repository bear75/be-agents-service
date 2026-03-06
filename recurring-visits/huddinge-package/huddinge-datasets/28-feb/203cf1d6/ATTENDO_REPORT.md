# Attendo – Huddinge Schedule Analytics (203cf1d6)

**Report date:** 3 March 2026 · **Schedule period:** 2 weeks (16 Feb – 1 Mar 2026) · **Solver:** Timefold FSR (prod)

**Dataset:** `huddinge-datasets/28-feb/203cf1d6` · **Route plan:** `203cf1d6-03e9-42a7-82ca-46b011dd7ed3`

---

## 1. Executive summary

Analytics and metrics run on the Huddinge 2-week FSR solve (Caire prod config):

- **98.1% assignment** — 3,554 of 3,622 visits assigned
- **68 unassigned** — all classified as config (overlapping shift exists; tune solver / movable distribution)
- **40 empty shifts** — trimmed via from-patch (trim to visit span + remove empty); from-patch submitted
- **Field efficiency 89.9%** — above 67.5% manual benchmark (Slingor) ✓
- **Continuity** — 81 clients, avg 2.5 distinct caregivers, max 6 (target ≤15) ✓

*Investor access:* [CAIRE AI OS Business Roadmap](https://app.caire.se/platform/en/investor-access.html)

---

## 2. Assignment at a glance

| Metric | Value |
|--------|--------|
| **Visits assigned** | 3,554 / 3,622 |
| **Unassigned** | 68 (config: 68, supply: 0) |
| **Shifts with visits** | 300 |
| **Empty shifts** | 40 |
| **Employees (vehicles)** | 38 (empty: 0) |

---

## 3. Efficiency metrics (base solve, incl. empty shifts)

| Efficiency | Result | Benchmark / note |
|------------|--------|-------------------|
| **Staffing** (visit / paid time) | **62.39%** | Share of paid time that is visit |
| **Field** (visit / visit+travel) | **89.91%** | Target >67.5% (Slingor) ✓ |
| **Wait** (visit / visit+travel+wait) | 87.15% | Includes waiting at client |
| **System** (incl. 40 empty shifts) | 62.39% | Will improve after from-patch |

### Time breakdown

| Category | Time (h:min) | % of shift |
|----------|--------------|------------|
| **Shift total** | 2,502h 0min | 100% |
| Visit (care delivery) | 1,502h 36min | **60.06%** |
| Travel | 168h 34min | 6.74% |
| Wait | 53h 4min | 2.12% |
| Break | 93h 30min | 3.74% |
| Inactive (idle + empty) | 684h 16min | 27.35% |

### Cost and revenue (base)

| Item | Amount (SEK) |
|------|----------------|
| **Revenue** (visit × 550 kr/h) | 826,430 |
| **Cost** (shift × 230 kr/h) | 575,460 |
| **Margin** | **250,970 (30.37%)** |

---

## 4. From-patch (trim empty + visit-span)

**Why can from-patch assign more visits?** The patch only **pins** the 3,554 already-assigned visits and **removes** the 40 empty shifts; it does **not** remove the 68 unassigned visits from the problem. We call the API with `operation: SOLVE`, so Timefold **re-solves** on the patched dataset. That dataset still has all 3,622 visits (including the 68 unassigned) and now 300 shifts with pinned itineraries and trimmed time windows. The solver then tries to place the 68 unassigned into those 300 shifts (e.g. in gaps or by extending within constraints). So more visits can be assigned because we run a full solve after applying the patch — the unassigned are still in the problem and the solver gets another chance to fit them.

Completed steps:

1. **Fetch** — Solution re-fetched from Timefold (route plan `203cf1d6-03e9-42a7-82ca-46b011dd7ed3`).
2. **Metrics + analyse** — solve_report run (unassigned + empty-shifts analysis).
3. **Trim** — From-patch payload built:
   - **Pin visits:** 3,554 (3,334 solo + 220 in visit groups)
   - **Trim shift to visit span:** 300 shifts (minStartTime/maxEndTime = first visit start → last visit end; idle and breaks removed)
   - **Remove empty shifts:** 40
   - **Remove empty vehicles:** 0
4. **Submit from-patch** — New route plan: **`83ce2c13-239c-4953-97f8-c8b46a643c6f`**.

When the from-patch solve completes (SOLVING_COMPLETED), the same pipeline will:

- Fetch the patch solution and save to `from_patch_output.json`
- Run solve_report with `--exclude-inactive` (efficiency without idle/empty)
- Write metrics to `metrics/`

**To run post–from-patch metrics manually** (if the background run has already finished):

```bash
cd be-agent-service/recurring-visits/scripts

# Fetch patch solution (use ID from from_patch_route_plan_id.txt)
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 python3 fetch_timefold_solution.py 83ce2c13-239c-4953-97f8-c8b46a643c6f \
  --save ../huddinge-package/huddinge-datasets/28-feb/203cf1d6/from_patch_output.json

# Un-metrics (exclude inactive)
cd ../huddinge-package
python3 scripts/solve_report.py huddinge-datasets/28-feb/203cf1d6/from_patch_output.json \
  --input huddinge-datasets/28-feb/203cf1d6/input.json \
  --save huddinge-datasets/28-feb/203cf1d6/metrics --exclude-inactive
```

---

## 5. Continuity

| Metric | Value |
|--------|--------|
| **Clients** | 81 |
| **Avg distinct caregivers** | 2.5 |
| **Max** | 6 |
| **Over 15** | 0 ✓ |

Full CSV: `continuity.csv` in this folder.

---

## 6. Artifacts in this folder

| File | Description |
|------|-------------|
| `input.json` | Timefold FSR input (modelInput) |
| `output.json` | Timefold FSR solution (current solve) |
| `from_patch_payload.json` | Trimmed model (visit-span + no empty shifts) sent to from-patch |
| `from_patch_route_plan_id.txt` | New route plan ID after from-patch |
| `from_patch_output.json` | *(Created when patch solve completes and fetch runs)* |
| `metrics/metrics_report_203cf1d6.txt` | Full metrics report (base solve) |
| `metrics/metrics_*.json` | Timestamped metrics JSON |
| `continuity.csv` | Per-client continuity (distinct caregivers) |
| `verification_report.txt` | Verification summary |

---

*Generated for Attendo review. Timefold API: prod key; config: Huddinge 2-week (a43d4eec-9f53-40b3-82ad-f135adc8c7e3).*
