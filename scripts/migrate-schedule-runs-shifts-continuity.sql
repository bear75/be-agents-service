-- Add shifts and continuity (median, visit-weighted avg) columns to schedule_runs.
-- Run: sqlite3 .compound-state/agent-service.db < scripts/migrate-schedule-runs-shifts-continuity.sql

ALTER TABLE schedule_runs ADD COLUMN input_shifts INTEGER;
ALTER TABLE schedule_runs ADD COLUMN input_shift_hours REAL;
ALTER TABLE schedule_runs ADD COLUMN output_shifts_trimmed INTEGER;
ALTER TABLE schedule_runs ADD COLUMN output_shift_hours_trimmed REAL;
ALTER TABLE schedule_runs ADD COLUMN continuity_median REAL;
ALTER TABLE schedule_runs ADD COLUMN continuity_visit_weighted_avg REAL;
