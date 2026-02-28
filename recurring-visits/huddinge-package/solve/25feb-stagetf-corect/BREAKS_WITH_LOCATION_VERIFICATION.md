# Floating breaks with location — verification

## Summary

Breaks are now emitted with **location** (office coordinates) and **time window** (maxStartTime 13:00, duration 30m, maxEndTime 13:30 — start + duration = end) so Timefold FSR computes travel to/from the break like for visits. LEGACY `type` / `costImpact` have been removed in favour of the standard Break API.

## Changes made

1. **Source CSV** (`huddinge-package/source/Huddinge_recurring_v2.csv`)
   - Added columns: `break_lat`, `break_lon`, `shift_break_maxStart`.
   - Break window: `shift_break_maxEnd` = 13:30, `shift_break_maxStart` = 13:00 (start + duration = end).
   - Break location: office `59.2368721, 17.9942601` (same as service area) so travel to/from break is modelled.

2. **Script** `docs_2.0/recurring-visits/scripts/generate_employees.py`
   - Breaks use standard API: `id`, `location` (nullable), `minStartTime`, `maxStartTime` (nullable), `maxEndTime`, `duration`.
   - `maxStartTime` emitted when CSV has `shift_break_maxStart` (or default 13:00); invalid values (e.g. text in wrong column) fall back to 13:00.
   - Removed `type` and `costImpact` (LEGACY).
   - `location` set from CSV `break_lat`/`break_lon` or from shift start location when missing.

3. **Regenerated input JSON**
   - Path: `huddinge-package/solve/25feb-stagetf-corect/input_breaks_25feb.json`
   - Sample break in payload:
     - `minStartTime`: 10:00, `maxStartTime`: 13:00, `maxEndTime`: 13:30, `duration`: PT30M, `location`: [59.2368721, 17.9942601].

## How to run a solve (Timefold production)

1. **Input JSON**: `docs_2.0/recurring-visits/huddinge-package/solve/25feb-stagetf-corect/input_breaks_25feb.json`  
   Or regenerate with:
   ```bash
   cd docs_2.0/recurring-visits
   python3 huddinge-package/process_huddinge.py --expanded-csv huddinge-package/expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2
   ```
   (Output JSON will be under `huddinge-package/solve/` with a timestamp.)

2. **Quick config ID**: `8f3ffcc6-1cb4-4ef9-a4c4-770191a23834`

3. **Submit** (e.g. from Timefold Dashboard or API):
   - POST the regenerated input to Timefold FSR with configuration ID `8f3ffcc6-1cb4-4ef9-a4c4-770191a23834`.
   - Or run: `python3 huddinge-package/process_huddinge.py --expanded-csv huddinge-package/expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --send`

## Verifying travel to/from break

- In the **solve output**, each shift’s `itinerary` can contain:
  - `kind: "TRAVEL"` — travel segments.
  - `kind: "BREAK"` — break with `startTime` / `endTime`.
- When the break has a **location** and the driver has visits before/after the break, the solver should schedule **travel to the break location** and **travel from the break location** to the next stop, so you should see TRAVEL events adjacent to BREAK in the itinerary.
- If the break location equals the depot and the shift has no visits, travel may be zero; to see non-zero travel to/from break, use a shift that has at least one visit and a break at the office (different from visit locations), or set a distinct break location in the CSV.

## Dataset reference

- Original input used for this folder: `1-c87d58dd-5200-41a9-a334-e075c54a7d94-input.json`
- New input with breaks-with-location (maxStart 13:00, maxEnd 13:30, 30m duration): `input_breaks_25feb.json`
