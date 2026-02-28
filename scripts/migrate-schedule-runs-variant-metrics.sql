-- Add variant1/variant2 efficiency and idle metrics (METRICS_VARIANTER.md).
-- Run: sqlite3 .compound-state/agent-service.db < scripts/migrate-schedule-runs-variant-metrics.sql

ALTER TABLE schedule_runs ADD COLUMN eff_v1_pct REAL;
ALTER TABLE schedule_runs ADD COLUMN idle_shifts_v1 INTEGER;
ALTER TABLE schedule_runs ADD COLUMN idle_shift_hours_v1 REAL;
ALTER TABLE schedule_runs ADD COLUMN eff_v2_pct REAL;
ALTER TABLE schedule_runs ADD COLUMN idle_shifts_v2 INTEGER;
ALTER TABLE schedule_runs ADD COLUMN idle_shift_hours_v2 REAL;
