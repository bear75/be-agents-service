# Data quality: Dependencies and visit groups (81-client CSV)

The 81-client CSV produces far fewer **visit groups** and **dependencies** per visit than the small test CSV. That matches the data: the new CSV has a much lower fill rate for the columns that drive groups and same-day dependencies.

## How the pipeline uses the CSV

| CSV column | Used for | Effect when empty |
|------------|----------|--------------------|
| **Dubbel** | Visit groups | Rows with same non-empty `Dubbel` value on the same date → one visit group (VG). Pairs/triples that must be done together. | Empty → visit is standalone, no group. |
| **Antal tim mellan besöken** | Same-day dependency (e.g. frukost→lunch 3,5 h) and spread (e.g. 48 h dusch) | For same client, same date: if this visit has a **short** delay (≤ 12 h), it gets `precedingVisit` = previous visit that day (by slot order). Also used for flexible_day spread. | Empty → no same-day chain from this row; spread uses 18 h default. |

So:

- **Visit groups** come only from rows where **Dubbel** is filled; same Dubbel id + same date = one group.
- **Same-day dependencies** (e.g. meals: frukost then lunch 3,5 h later) come from **Antal tim mellan besöken** with a short value (e.g. `3,5timmar`, `2 timmar`). Long values (48 h, 36 h) are used only for spread over days, not for same-day ordering.

## Comparison: small vs 81-client CSV

| Metric | Small CSV | 81-client CSV | Scale (81 / small) |
|--------|-----------|----------------|--------------------|
| Rows | 107 | 614 | **5.7×** |
| Visits (2w) | 744 | 3746 | **5.0×** ✓ |
| Rows with **Dubbel** filled | 28 | 42 | **1.5×** |
| Rows with **Antal tim mellan** filled | 39 | 74 | **1.9×** |
| Visit groups (output) | ~116 | 152 | **1.3×** |
| Dependencies (output) | ~112 | 145 | **1.3×** |

So visits scale with rows, but **Dubbel** and **Antal tim mellan besöken** are filled in many fewer rows in the 81-client file (per row: ~26% vs ~7% Dubbel, ~36% vs ~12% Antal tim). That is why groups and dependencies barely scale.

## Value distribution (81-client CSV)

- **Dubbel:** 42 rows with values like 1–22 (group ids).
- **Antal tim mellan besöken:** 74 rows filled. Counts: `48 timmar` (33), `3,5timmar` (24), `36 timmar` (12), `2 timmar` (4), `Fredag` (1). Only short values (e.g. 3,5 h, 2 h) create **same-day** dependencies; 48 h / 36 h are for spread only.

## Conclusion and recommendation

The CSV is not 100% complete for modelling:

1. **Dubbel** is missing on many rows that likely belong to a double-visit (samma dag, samma kund, ska utföras tillsammans). Filling Dubbel for those rows would increase visit groups and better match reality.
2. **Same-day dependency** (e.g. frukost → lunch 3,5 h) is missing where **Antal tim mellan besöken** is empty on the later visit in the chain. Filling it (e.g. `3,5timmar` for lunch after morgon) for all relevant meal/insats chains would make dependency count scale with visits.

**Recommendation:** Have the data source (Attendo/export) or a pre-step fill:

- **Dubbel** for every row that is part of a dubbel (pair/group) on the same day.
- **Antal tim mellan besöken** for every row that must follow another visit the same day (e.g. lunch after frukost with 3,5 h), with the correct short delay value.

The pipeline logic in `attendo_4mars_to_fsr.py` already supports both; it just needs these columns populated in the 81-client CSV.
