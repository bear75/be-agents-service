-- Simulate Real Task Completion with Automatic XP Award
-- This shows how agents earn XP through actual work

-- 1. Create a test session
INSERT INTO sessions (id, team_id, status, target_repo, started_at)
VALUES ('session-test-001', 'team-engineering', 'in_progress', '/Users/bjornevers_MacPro/HomeCare/beta-appcaire', CURRENT_TIMESTAMP);

-- 2. Create a test task for Backend agent
INSERT INTO tasks (
  id, session_id, agent_id, task_description,
  status, started_at, completed_at, duration_seconds
)
VALUES (
  'task-test-001',
  'session-test-001',
  'agent-backend',
  'Test task: Update Prisma schema',
  'completed',
  datetime('now', '-5 minutes'),
  datetime('now'),
  300  -- 5 minutes = 300 seconds
);

-- 3. Update agent stats (this would normally trigger XP award in code)
-- Note: XP award happens in lib/database.js updateAgentStats() function
-- This just updates the task count

SELECT 'Task created! Backend agent should earn ~10 XP' as result;
SELECT 'Refresh dashboard to see updated stats' as action;
