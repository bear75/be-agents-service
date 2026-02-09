-- Gamification System Schema
-- Managed by HR Agent using Agent Levelup expert

-- Agent Levels and XP
CREATE TABLE IF NOT EXISTS agent_levels (
    agent_id TEXT PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 1,
    current_xp INTEGER NOT NULL DEFAULT 0,
    total_xp INTEGER NOT NULL DEFAULT 0,
    title TEXT DEFAULT 'Rookie',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- XP Transactions (track how XP is earned)
CREATE TABLE IF NOT EXISTS xp_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    reason TEXT NOT NULL,
    source_type TEXT NOT NULL, -- 'task_completion', 'session_success', 'achievement', 'bonus', 'penalty'
    source_id TEXT, -- task_id, session_id, achievement_id, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Achievement Definitions
CREATE TABLE IF NOT EXISTS achievement_definitions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    emoji TEXT NOT NULL,
    category TEXT NOT NULL, -- 'performance', 'streak', 'milestone', 'special'
    tier TEXT NOT NULL, -- 'bronze', 'silver', 'gold', 'platinum', 'legendary'
    xp_reward INTEGER NOT NULL DEFAULT 0,
    criteria TEXT NOT NULL, -- JSON criteria for unlocking
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agent Achievements (unlocked achievements)
CREATE TABLE IF NOT EXISTS agent_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    achievement_id TEXT NOT NULL REFERENCES achievement_definitions(id),
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, achievement_id)
);

-- Streaks (consecutive task completions)
CREATE TABLE IF NOT EXISTS agent_streaks (
    agent_id TEXT PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_activity_date DATE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Leaderboard Cache (updated periodically)
CREATE TABLE IF NOT EXISTS leaderboard_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL, -- 'daily', 'weekly', 'monthly', 'all_time'
    agent_id TEXT NOT NULL REFERENCES agents(id),
    rank INTEGER NOT NULL,
    score INTEGER NOT NULL,
    metric_type TEXT NOT NULL, -- 'xp', 'tasks_completed', 'success_rate', 'streak'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period, agent_id, metric_type, period_start)
);

-- Level Thresholds (XP required for each level)
CREATE TABLE IF NOT EXISTS level_thresholds (
    level INTEGER PRIMARY KEY,
    xp_required INTEGER NOT NULL,
    title TEXT NOT NULL,
    emoji TEXT NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_xp_transactions_agent ON xp_transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_xp_transactions_created ON xp_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_achievements_agent ON agent_achievements(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_achievements_achievement ON agent_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_period ON leaderboard_cache(period, period_start, period_end);

-- Seed Level Thresholds (Exponential curve)
INSERT INTO level_thresholds (level, xp_required, title, emoji) VALUES
(1, 0, 'Rookie', '🌱'),
(2, 100, 'Apprentice', '📚'),
(3, 250, 'Junior', '👶'),
(4, 500, 'Associate', '🎓'),
(5, 1000, 'Specialist', '💼'),
(6, 2000, 'Senior', '🎯'),
(7, 4000, 'Expert', '⭐'),
(8, 8000, 'Master', '🏆'),
(9, 16000, 'Grandmaster', '👑'),
(10, 32000, 'Legend', '🔮'),
(11, 64000, 'Mythic', '🌟'),
(12, 100000, 'Divine', '✨')
ON CONFLICT(level) DO NOTHING;

-- Seed Achievement Definitions
INSERT INTO achievement_definitions (id, name, description, emoji, category, tier, xp_reward, criteria) VALUES
('ach-first-task', 'First Steps', 'Complete your first task', '🎯', 'milestone', 'bronze', 50, '{"tasks_completed": 1}'),
('ach-10-tasks', 'Getting Started', 'Complete 10 tasks', '📊', 'milestone', 'bronze', 100, '{"tasks_completed": 10}'),
('ach-50-tasks', 'Productive', 'Complete 50 tasks', '💪', 'milestone', 'silver', 250, '{"tasks_completed": 50}'),
('ach-100-tasks', 'Workhorse', 'Complete 100 tasks', '🐎', 'milestone', 'gold', 500, '{"tasks_completed": 100}'),
('ach-500-tasks', 'Elite Performer', 'Complete 500 tasks', '🚀', 'milestone', 'platinum', 1000, '{"tasks_completed": 500}'),
('ach-90-success', 'Excellence', '90%+ success rate (min 10 tasks)', '⭐', 'performance', 'gold', 300, '{"success_rate": 0.9, "min_tasks": 10}'),
('ach-95-success', 'Near Perfect', '95%+ success rate (min 20 tasks)', '💎', 'performance', 'platinum', 600, '{"success_rate": 0.95, "min_tasks": 20}'),
('ach-100-success', 'Flawless', '100% success rate (min 10 tasks)', '🏆', 'performance', 'legendary', 1000, '{"success_rate": 1.0, "min_tasks": 10}'),
('ach-streak-3', 'On a Roll', '3-day streak', '🔥', 'streak', 'bronze', 50, '{"streak_days": 3}'),
('ach-streak-7', 'Consistent', '7-day streak', '🔥🔥', 'streak', 'silver', 150, '{"streak_days": 7}'),
('ach-streak-14', 'Dedicated', '14-day streak', '🔥🔥🔥', 'streak', 'gold', 300, '{"streak_days": 14}'),
('ach-streak-30', 'Unstoppable', '30-day streak', '🔥🔥🔥🔥', 'streak', 'platinum', 750, '{"streak_days": 30}'),
('ach-speed-demon', 'Speed Demon', 'Complete 5 tasks in under 2 min avg', '⚡', 'performance', 'gold', 400, '{"tasks": 5, "avg_duration": 120}'),
('ach-team-player', 'Team Player', 'Collaborate on 10 sessions', '🤝', 'milestone', 'silver', 200, '{"sessions_collaborated": 10}'),
('ach-comeback', 'Comeback King', 'Succeed after 3 consecutive failures', '💪', 'special', 'gold', 500, '{"comeback": true}')
ON CONFLICT(id) DO NOTHING;

-- Views for gamification analytics

-- Agent Gamification Overview
CREATE VIEW IF NOT EXISTS v_agent_gamification AS
SELECT
    a.id as agent_id,
    a.name as agent_name,
    a.team_id,
    t.name as team_name,
    COALESCE(al.level, 1) as level,
    COALESCE(al.current_xp, 0) as current_xp,
    COALESCE(al.total_xp, 0) as total_xp,
    COALESCE(al.title, 'Rookie') as title,
    COALESCE(lt_current.emoji, '🌱') as level_emoji,
    COALESCE(lt_current.xp_required, 0) as current_level_xp,
    COALESCE(lt_next.xp_required, 999999) as next_level_xp,
    COALESCE(lt_next.xp_required, 999999) - COALESCE(al.current_xp, 0) as xp_to_next_level,
    COALESCE(ast.current_streak, 0) as current_streak,
    COALESCE(ast.longest_streak, 0) as longest_streak,
    COUNT(DISTINCT aa.achievement_id) as achievements_unlocked
FROM agents a
LEFT JOIN teams t ON a.team_id = t.id
LEFT JOIN agent_levels al ON a.id = al.agent_id
LEFT JOIN level_thresholds lt_current ON al.level = lt_current.level
LEFT JOIN level_thresholds lt_next ON (COALESCE(al.level, 1) + 1) = lt_next.level
LEFT JOIN agent_streaks ast ON a.id = ast.agent_id
LEFT JOIN agent_achievements aa ON a.id = aa.agent_id
WHERE a.is_active = TRUE
GROUP BY a.id;

-- Leaderboard View
CREATE VIEW IF NOT EXISTS v_leaderboard AS
SELECT
    a.id as agent_id,
    a.name as agent_name,
    a.emoji as agent_emoji,
    t.name as team_name,
    COALESCE(al.level, 1) as level,
    COALESCE(lt.title, 'Rookie') as title,
    COALESCE(lt.emoji, '🌱') as level_emoji,
    COALESCE(al.total_xp, 0) as total_xp,
    COUNT(DISTINCT aa.achievement_id) as achievements_count,
    COALESCE(ast.current_streak, 0) as current_streak,
    COALESCE(a.total_tasks_completed, 0) as tasks_completed,
    ROUND(COALESCE(a.success_rate, 0.0) * 100, 1) as success_rate_pct,
    ROW_NUMBER() OVER (ORDER BY COALESCE(al.total_xp, 0) DESC) as xp_rank,
    ROW_NUMBER() OVER (ORDER BY COALESCE(a.total_tasks_completed, 0) DESC) as tasks_rank,
    ROW_NUMBER() OVER (ORDER BY COALESCE(a.success_rate, 0.0) DESC) as success_rank
FROM agents a
LEFT JOIN teams t ON a.team_id = t.id
LEFT JOIN agent_levels al ON a.id = al.agent_id
LEFT JOIN level_thresholds lt ON COALESCE(al.level, 1) = lt.level
LEFT JOIN agent_streaks ast ON a.id = ast.agent_id
LEFT JOIN agent_achievements aa ON a.id = aa.agent_id
WHERE a.is_active = TRUE
GROUP BY a.id
ORDER BY total_xp DESC;
