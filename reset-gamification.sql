-- Reset Gamification Data to Clean State
-- This removes all XP, achievements, and streaks but keeps agent definitions

-- Reset agent levels back to Level 1, 0 XP
UPDATE agent_levels SET
  level = 1,
  current_xp = 0,
  total_xp = 0,
  title = 'Rookie',
  updated_at = CURRENT_TIMESTAMP;

-- Clear all XP transactions
DELETE FROM xp_transactions;

-- Clear all unlocked achievements
DELETE FROM agent_achievements;

-- Reset all streaks
UPDATE agent_streaks SET
  current_streak = 0,
  longest_streak = 0,
  last_activity_date = NULL,
  updated_at = CURRENT_TIMESTAMP;

-- Clear leaderboard cache
DELETE FROM leaderboard_cache;

SELECT 'Gamification data reset complete!' as result;
SELECT 'All agents back to Level 1 Rookie with 0 XP' as status;
