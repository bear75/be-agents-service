-- Add schedule_runs table to an existing agent-service DB (e.g. created before schedule feature).
-- Run: sqlite3 .compound-state/agent-service.db < scripts/migrate-add-schedule-runs-table.sql

CREATE TABLE IF NOT EXISTS schedule_runs (
    id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    batch TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    strategy TEXT NOT NULL,
    hypothesis TEXT,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK(status IN ('queued', 'running', 'completed', 'cancelled', 'failed')),
    decision TEXT
        CHECK(decision IN ('keep', 'kill', 'double_down', 'continue')),
    decision_reason TEXT,
    timefold_score TEXT,
    routing_efficiency_pct REAL,
    unassigned_visits INTEGER,
    total_visits INTEGER,
    unassigned_pct REAL,
    continuity_avg REAL,
    continuity_max INTEGER,
    continuity_over_target INTEGER,
    continuity_target INTEGER DEFAULT 11,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    cancelled_at DATETIME,
    duration_seconds INTEGER,
    output_path TEXT,
    notes TEXT,
    iteration INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_schedule_runs_dataset ON schedule_runs(dataset);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_status ON schedule_runs(status);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_submitted ON schedule_runs(submitted_at DESC);
