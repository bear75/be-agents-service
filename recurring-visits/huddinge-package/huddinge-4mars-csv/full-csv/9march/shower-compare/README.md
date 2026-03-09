# Shower-compare: dusch-after-morgon logic and balanced input

**Where things are**


| What                                                                         | Location                           |
| ---------------------------------------------------------------------------- | ---------------------------------- |
| **Logic doc** (why dusch after morgon, correct pairing)                      | `DUSCH_AFTER_MORGON_LOGIC.md`      |
| **Balanced input** (46 vehicles, 448 shifts, 2 delay=0 deps) — use for solve | `fsr_balanced_46v_448s_input.json` |
| **Analysis** (272d0e2c failed; balanced run ID)                              | `ANALYSIS_272d0e2c.md`             |
| **Input diff** (old vs fsr_input_81_2w, why 34 deps caused 1340 unassigned)  | `INPUT_DIFF_old_vs_81_2w.md`       |


**Baseline (cece06c0) input/output**  
`../old-shower-bug-dataset/` — `export-field-service-routing-v1-cece06c0-...-input.json` (46v, 448s), `...-output.json` (2 unassigned).

**Balanced run**  
Route plan ID: `9945ccf2-b36d-4470-be63-d73ceee42822`.  
Check: `python3 fetch_timefold_solution.py 9945ccf2-b36d-4470-be63-d73ceee42822` (from `recurring-visits/scripts/`).

**Pipeline**  

- New logic (narrow dusch–morgon pairing): `attendo_4mars_to_fsr.py` with same CSV; use `--no-supplementary-vehicles` for fewer vehicles or merge with cece06c0 vehicles for 46/448.
- Compare two inputs: `compare_fsr_inputs.py` in `recurring-visits/scripts/`.

