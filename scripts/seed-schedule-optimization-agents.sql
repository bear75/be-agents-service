-- Add Schedule optimization team and agents so they appear in the dashboard (Agents page).
-- Run on existing DB if you added the agents after initial setup:
--   sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-optimization-agents.sql

INSERT OR IGNORE INTO teams (id, name, domain, description) VALUES
    ('team-schedule-optimization', 'Schedule optimization', 'schedule-optimization', 'Timefold FSR pipeline: submit, monitor, cancel runs; propose strategies (spaghetti sort)');

INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-timefold-specialist', 'team-schedule-optimization', 'Timefold Specialist', 'Submit/monitor/cancel FSR jobs, run metrics and continuity scripts, write results to Darwin DB', '🕐', 'sonnet'),
    ('agent-optimization-mathematician', 'team-schedule-optimization', 'Optimization Mathematician', 'Analyse completed runs, propose N strategies (exploitation + exploration), spaghetti sort cancellation heuristics', '📐', 'sonnet');
