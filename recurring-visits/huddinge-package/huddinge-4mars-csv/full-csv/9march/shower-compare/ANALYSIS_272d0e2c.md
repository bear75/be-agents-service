# Analysis: 272d0e2c solution (new logic, 2 delay=0)

**Status: run failed.** Solver resumed after unexpected shutdown and hit `Expected dataset status DATASET_VALIDATED, but was SOLVING_ACTIVE` (resume/state mismatch). The balanced run (46 vehicles, 448 shifts) is the one to use.

## Supply vs demand

| Metric | 272d0e2c (current) | cece06c0 (balanced ref) |
|--------|--------------------|-------------------------|
| Vehicles | 299 | 46 |
| Shifts | 4,086 | 448 |
| Empty shifts | 159 | — |
| Shifts with ≥1 stop | 3,927 | — |
| Unassigned | 16 | 2 |
| Status | SOLVING_ACTIVE | SOLVING_COMPLETED |

The current run uses ~9× more shifts (4086 vs 448). Most shifts are used (3927 with stops) but the fleet is heavily over-supplied vs the balanced 46-vehicle / 448-shift setup.

## Unassigned (16)

- **H034** (4): r39_3, r39_6, r41_1, r41_6 — client with the 2 delay=0 dusch-after-morgon deps.
- **H239** (4): r469_5, r469_6, r469_11, r469_12
- **H145** (4): r302_5, r302_6, r302_11, r302_12
- **H290** (2): r597_3, r597_4
- **H293** (2): r613_3, r613_4

## Next step (done)

Created balanced input: same visits + 2 delay=0 deps as new logic, **vehicles/shifts from cece06c0** (46 vehicles, 448 shifts).

- **Balanced input:** `fsr_balanced_46v_448s_input.json` (46 vehicles, 448 shifts, 3457 visits, 116 groups, 2 PT0M deps).
- **New solve (balanced) submitted:** Route plan ID `9945ccf2-b36d-4470-be63-d73ceee42822` (46 vehicles, 448 shifts). This run is in progress; 272d0e2c failed on resume. Check status: `python3 fetch_timefold_solution.py 9945ccf2-b36d-4470-be63-d73ceee42822`.
