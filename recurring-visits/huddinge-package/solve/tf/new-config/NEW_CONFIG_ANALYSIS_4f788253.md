# New config run analysis (4f788253)

**Profile:** huddinge-test-long-update (recommended “Huddinge-assign-evening” weights)  
**Input:** Same as 9789141a — `solve/input_20260214_171612.json` (38 vehicles, 340 shifts)  
**Output:** `export-field-service-routing-4f788253-ce51-4cbd-b372-55c8b45b1019-output.json`

## Result: solution got worse

| Metric           | Original (9789141a) | New config (4f788253)                    |
| ---------------- | ------------------- | ---------------------------------------- |
| Unassigned       | 19                  | **88**                                   |
| Assigned         | 3603                | 3534                                     |
| Travel time      | 479h                | 497h                                     |
| Score (medium)   | -190000             | -880000                                  |
| Field efficiency | 75.9%               | lower (more unassigned, less visit time) |

The updated profile (balance time 1, prefer earliest day 1, travel 2, max soft shift travel 0, visit completion risk 2) increased unassigned and travel. Revert to **original config** for the next run.

## Next run: add shifts (original config)

1. **Use original profile:** Huddinge-test-long (not huddinge-test-long-update).
2. **Add evening capacity:** Run `add_evening_vehicles.py` to create an input with 1 (or 2) extra evening vehicles.
3. **Re-solve** with the new input and **Huddinge-test-long** profile.

### Commands (from package root)

```bash
cd docs_2.0/recurring-visits/huddinge-package

# Create input with 1 extra evening vehicle (14 shifts)
python3 scripts/add_evening_vehicles.py solve/input_20260214_171612.json --count 1 --out solve/input_evening.json --no-timestamp

# Then in Timefold Dashboard:
# - Select profile: Huddinge-test-long (original)
# - Upload solve/input_evening.json (or the path where the script wrote it)
# - Solve and save output to solve/tf/add-shifts/
```

After solve, run:

```bash
python3 scripts/solve_report.py solve/tf/add-shifts/export-field-service-routing-<run-id>-output.json --input solve/input_evening.json --save metrics/
```

If unassigned drops to 0, run from-patch to trim empty shifts, then metrics for efficiency.
