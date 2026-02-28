-- Add shift hour breakdown and efficiency columns.
-- Run: sqlite3 .compound-state/agent-service.db < scripts/migrate-schedule-runs-shift-hours-eff.sql

ALTER TABLE schedule_runs ADD COLUMN shift_hours_total REAL;
ALTER TABLE schedule_runs ADD COLUMN shift_hours_idle REAL;
ALTER TABLE schedule_runs ADD COLUMN efficiency_total_pct REAL;
ALTER TABLE schedule_runs ADD COLUMN efficiency_trimmed_pct REAL;
