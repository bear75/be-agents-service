# Viewing Huddinge Solve Output on the Schedule Page

This document describes where the Timefold solve outputs are stored and how they can be used for schedule page visualization on the Caire platform.

## Output artifact locations

After running the pipeline (solve, optional from-patch), outputs are under `docs_2.0/huddinge-package/`:

| Artifact                              | Location                                       | Description                                                                     |
| ------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| **Best solve output (41 vehicles)**   | `solve/tf/output_evening_20260214_120118.json` | Supply-rerun with 3 extra evening vehicles; 3,614 assigned, 8 unassigned.       |
| **Config-rerun output (38 vehicles)** | `solve/tf/output_testing_20260214_115047.json` | Testing profile; 3,530 assigned, 92 unassigned.                                 |
| **From-patch output**                 | `from-patch/output_*.json`                     | Trimmed schedule (pinned visits, empty shifts removed), when run has completed. |
| **Input (evening)**                   | `solve/input_evening.json`                     | Input used for supply-rerun (41 vehicles, 382 shifts).                          |
| **Metrics**                           | `metrics/metrics_*.json`                       | Efficiency and cost/revenue per run.                                            |

Paths are relative to the **appcaire** repo root when using `./scripts/run-timefold.sh`.

## Viewing the schedule

### Option 1: Timefold Dashboard

- Open [Timefold Dashboard](https://app.timefold.ai), go to your route plan.
- Use the run IDs: e.g. `a7091ab5-d55c-475f-aa87-a9c3b6c7eb8b` (supply-rerun), `655212f0-298a-4f04-a125-1a2d2e7b1f89` (config-rerun).
- The dashboard shows routes, map, and KPIs.

### Option 2: Caire platform schedule page

The Caire schedule page (Bryntum SchedulerPro) loads data via **GraphQL** (schedules, employees, visits). To show Timefold results there:

1. **Import path**: Timefold output JSON must be transformed into the platform’s data model (schedules, visits, employees/shifts) and persisted (e.g. via GraphQL mutations or a backend import API).
2. **Mapping**: Map `modelOutput.vehicles` → employees/shifts, itinerary items → visits with assigned employee and time windows.
3. **Reference**: See `docs_2.0/09-scheduling/FRONTEND_INTEGRATION.md` and `docs_2.0/09-scheduling/TIMEFOLD_INTEGRATION.md` for data flow and API design.

A dedicated “import Timefold output” script or UI is not part of this package; use the artifact paths above as input for such an importer when it exists.
