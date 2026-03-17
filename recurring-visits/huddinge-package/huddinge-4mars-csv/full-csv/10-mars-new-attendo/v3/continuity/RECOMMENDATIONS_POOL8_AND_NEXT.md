# Recommendations: Use Pool 8 and Optimize Further

**Context:** v3 campaign results show **pool8_required** is the best trade-off: 2.1% unassigned, 73.82% field efficiency, 3.69 continuity (all goals met). This doc gives concrete steps to use it as the base and run new solutions.

---

## 1. Why use Pool 8 as the base?

| Variant           | Unassigned % | Field eff. | Continuity | Empty shifts (approx) |
|-------------------|--------------|------------|------------|------------------------|
| baseline          | 1.2%         | 65.88%     | 21.32      | 2430                   |
| pool3_required    | 12.6%        | 73.32%     | **1.74**   | ~105                   |
| pool5_required    | 4.8%         | 73.25%     | 2.56       | ~77                    |
| **pool8_required** | **2.1%**   | **73.82%** | 3.69       | ~78                    |

- **Pool 8** has the best coverage among continuity variants (162 unassigned), best field efficiency (73.82%), and still strong continuity (3.69).
- Pool 3 is too strict (967 unassigned). Pool 5 is good but pool 8 is strictly better on coverage and efficiency.

**Recommendation:** Treat **pool8_required** (route plan `5e55bf3a-9768-4ac8-9a98-d38b857926e4`) as the primary solution and optimize from it.

---

## 2. Improvement path A: From-patch on Pool 8 (trim empty shifts)

Pool 8 output has ~78 empty shifts. From-patch pins assigned visits, trims shift times to visit span, and removes empty shifts/vehicles. Past runs showed **100% empty-shift removal** and **unchanged or slightly better** continuity and assignment.

**Steps (run from `be-agent-service` root):**

```bash
# Path prefix (be-agent-service root)
V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3

# 1. Fetch pool8 output if you don't have it locally (run from be-agent-service, then cd to scripts)
cd recurring-visits/scripts
export TIMEFOLD_API_KEY="<test-tenant-key>"
python3 fetch_timefold_solution.py 5e55bf3a-9768-4ac8-9a98-d38b857926e4 \
  --save "../huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool8_required/pool8_output.json"

# 2. Build from-patch payload (from be-agent-service root)
mkdir -p "$V3/continuity/results/pool8_from_patch"
python3 scripts/continuity/build_from_patch.py \
  --output "$V3/continuity/results/pool8_required/pool8_output.json" \
  --input "$V3/input_v3_from_Data_final_no_tags.json" \
  --out "$V3/continuity/results/pool8_from_patch/patch.json"

# 3. Submit from-patch (creates new route plan)
python3 scripts/timefold/submit.py from-patch "$V3/continuity/results/pool8_from_patch/patch.json" \
  --route-plan-id 5e55bf3a-9768-4ac8-9a98-d38b857926e4 \
  --configuration-id "" \
  --wait \
  --save "$V3/continuity/results/pool8_from_patch/output.json" \
  --strategy "pool8_from_patch" --dataset huddinge-v3
```

**Expected:** 0 empty shifts, same or better field efficiency, continuity ~3.69. Then fetch the new route plan and run metrics + continuity (same as campaign fetch) to confirm.

---

## 3. Improvement path B: New solves (pool8 preferred, pool10 required)

- **Pool 8 preferred** (softer constraint): may reduce unassigned vs pool8_required while keeping continuity in the 3–5 range. Variant input already exists: `v3/continuity/variants/input_pool8_preferred.json`.
- **Pool 10 required**: slightly larger pool per client → potentially fewer unassigned, continuity ~4–5. Variant input: `v3/continuity/variants/input_pool10_required.json`.

**Submit new solves (from `be-agent-service` root):**

```bash
V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3

# Pool 8 preferred (softer continuity)
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/input_pool8_preferred.json" \
  --configuration-id "" --strategy "pool8_preferred" --dataset huddinge-v3 \
  --save "$V3/continuity/results/pool8_preferred" --no-wait

# Pool 10 required (more flexibility)
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/input_pool10_required.json" \
  --configuration-id "" --strategy "pool10_required" --dataset huddinge-v3 \
  --save "$V3/continuity/results/pool10_required" --no-wait
```

After they complete, fetch and analyze as in the campaign (fetch script + `--metrics-dir`), then add rows to `scripts/analytics/campaign_analysis/SUMMARY.md` or run `build_campaign_summary.py` if you add the new variant dirs.

---

## 4. Suggested order of operations

1. **From-patch on pool 8** (path A) — quick win: same solution, fewer shifts, 0 empty. Use this as the “production” schedule from pool 8.
2. **Run pool8_preferred** (path B) — one extra solve to see if softer constraint improves unassigned without hurting continuity.
3. **Run pool10_required** (path B) — optional; try if you want even lower unassigned and can accept slightly higher continuity (e.g. 4–5).
4. **Compare** — fetch all new route plans, run metrics + continuity, and update SUMMARY (or campaign_analysis) so you have one table: pool8_required, pool8_from_patch, pool8_preferred, pool10_required.

---

## 5. Paths reference

- Pool 8 output (current): `v3/continuity/results/pool8_required/` (or campaign_analysis `pool8_required/`).
- Variant inputs: `v3/continuity/variants/input_pool8_required.json`, `input_pool8_preferred.json`, `input_pool10_required.json`.
- Submit script: `be-agent-service/scripts/timefold/submit.py`.
- From-patch builder: `be-agent-service/scripts/continuity/build_from_patch.py`.
- Fetch + metrics: `be-agent-service/scripts/analytics/campaign_analysis/fetch_all_campaign_runs.sh` (or single-job fetch with `--metrics-dir`).

---

## 6. Success criteria (reminder)

- **Field efficiency:** ≥70% (stretch 73%+).
- **Continuity:** avg ≤11 (stretch 2–4).
- **Unassigned:** <5%.
- **Empty shifts:** 0 (after from-patch).

Pool 8 already meets the first three; from-patch addresses the fourth.
