/**
 * Gamification System - Agent Levelup
 *
 * Manages XP, levels, achievements, streaks, and leaderboards for agents.
 * Setup and managed by HR Agent using Agent Levelup expert.
 */

const db = require('./database').db;

// XP Rewards Configuration
const XP_REWARDS = {
  TASK_COMPLETED: 10,
  TASK_FAILED: -5,
  SESSION_COMPLETED: 25,
  SESSION_FAILED: -10,
  PR_MERGED: 50,
  PR_REJECTED: -20,
  USER_PRAISE: 100,
  FIRST_TASK_OF_DAY: 5,
  QUICK_COMPLETION: 15, // < 2 min
  PERFECT_SESSION: 75,  // 100% success rate
};

/**
 * Award XP to an agent
 */
function awardXP(agentId, amount, reason, sourceType, sourceId = null) {
  try {
    // Record transaction
    const transactionStmt = db.prepare(`
      INSERT INTO xp_transactions (agent_id, amount, reason, source_type, source_id)
      VALUES (?, ?, ?, ?, ?)
    `);
    transactionStmt.run(agentId, amount, reason, sourceType, sourceId);

    // Update agent level
    const levelStmt = db.prepare(`
      INSERT INTO agent_levels (agent_id, level, current_xp, total_xp, title)
      VALUES (?, 1, ?, ?, 'Rookie')
      ON CONFLICT(agent_id) DO UPDATE SET
        current_xp = current_xp + ?,
        total_xp = total_xp + ?,
        updated_at = CURRENT_TIMESTAMP
    `);
    levelStmt.run(agentId, amount, amount, amount, amount);

    // Check for level up
    checkLevelUp(agentId);

    // Check for achievements
    checkAchievements(agentId);

    console.log(`✅ [Gamification] ${agentId} earned ${amount} XP: ${reason}`);

    return { success: true, amount, reason };
  } catch (error) {
    console.error(`❌ [Gamification] Error awarding XP:`, error);
    return { success: false, error: error.message };
  }
}

/**
 * Check if agent should level up
 */
function checkLevelUp(agentId) {
  try {
    const agentLevel = db.prepare(`
      SELECT al.*, lt.xp_required as current_level_xp
      FROM agent_levels al
      JOIN level_thresholds lt ON al.level = lt.level
      WHERE al.agent_id = ?
    `).get(agentId);

    if (!agentLevel) return;

    // Get next level threshold
    const nextLevel = db.prepare(`
      SELECT * FROM level_thresholds WHERE level = ?
    `).get(agentLevel.level + 1);

    if (!nextLevel) return; // Max level reached

    // Check if agent has enough XP for next level
    if (agentLevel.total_xp >= nextLevel.xp_required) {
      const updateStmt = db.prepare(`
        UPDATE agent_levels
        SET level = ?,
            title = ?,
            current_xp = total_xp - ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE agent_id = ?
      `);
      updateStmt.run(nextLevel.level, nextLevel.title, nextLevel.xp_required, agentId);

      console.log(`🎉 [Gamification] ${agentId} leveled up to Level ${nextLevel.level} ${nextLevel.emoji} ${nextLevel.title}!`);

      // Award bonus XP for leveling up
      const bonusXP = nextLevel.level * 10;
      const bonusStmt = db.prepare(`
        INSERT INTO xp_transactions (agent_id, amount, reason, source_type)
        VALUES (?, ?, ?, ?)
      `);
      bonusStmt.run(agentId, bonusXP, `Level ${nextLevel.level} bonus`, 'level_up');

      // Recursively check for multiple level ups
      checkLevelUp(agentId);
    }
  } catch (error) {
    console.error(`❌ [Gamification] Error checking level up:`, error);
  }
}

/**
 * Check for achievement unlocks
 */
function checkAchievements(agentId) {
  try {
    // Get agent stats
    const agent = db.prepare(`
      SELECT
        a.*,
        al.level,
        al.total_xp,
        ast.current_streak
      FROM agents a
      LEFT JOIN agent_levels al ON a.id = al.agent_id
      LEFT JOIN agent_streaks ast ON a.id = ast.agent_id
      WHERE a.id = ?
    `).get(agentId);

    if (!agent) return;

    // Get all achievement definitions
    const achievements = db.prepare(`
      SELECT * FROM achievement_definitions WHERE is_active = TRUE
    `).all();

    // Get already unlocked achievements
    const unlockedIds = db.prepare(`
      SELECT achievement_id FROM agent_achievements WHERE agent_id = ?
    `).all(agentId).map(a => a.achievement_id);

    // Check each achievement
    for (const achievement of achievements) {
      // Skip if already unlocked
      if (unlockedIds.includes(achievement.id)) continue;

      const criteria = JSON.parse(achievement.criteria);
      let unlocked = false;

      // Check criteria
      if (criteria.tasks_completed && agent.total_tasks_completed >= criteria.tasks_completed) {
        unlocked = true;
      }

      if (criteria.success_rate && criteria.min_tasks) {
        if (agent.total_tasks_completed >= criteria.min_tasks &&
            agent.success_rate >= criteria.success_rate) {
          unlocked = true;
        }
      }

      if (criteria.streak_days && agent.current_streak >= criteria.streak_days) {
        unlocked = true;
      }

      // Unlock achievement
      if (unlocked) {
        const unlockStmt = db.prepare(`
          INSERT INTO agent_achievements (agent_id, achievement_id)
          VALUES (?, ?)
        `);
        unlockStmt.run(agentId, achievement.id);

        // Award XP
        if (achievement.xp_reward > 0) {
          awardXP(agentId, achievement.xp_reward,
                  `Achievement unlocked: ${achievement.name}`,
                  'achievement', achievement.id);
        }

        console.log(`🏆 [Gamification] ${agentId} unlocked achievement: ${achievement.emoji} ${achievement.name} (+${achievement.xp_reward} XP)`);
      }
    }
  } catch (error) {
    console.error(`❌ [Gamification] Error checking achievements:`, error);
  }
}

/**
 * Update agent streak
 */
function updateStreak(agentId, success = true) {
  try {
    const today = new Date().toISOString().split('T')[0];

    const streak = db.prepare(`
      SELECT * FROM agent_streaks WHERE agent_id = ?
    `).get(agentId);

    if (!streak) {
      // Create new streak
      db.prepare(`
        INSERT INTO agent_streaks (agent_id, current_streak, longest_streak, last_activity_date)
        VALUES (?, 1, 1, ?)
      `).run(agentId, today);
      return;
    }

    const lastDate = new Date(streak.last_activity_date);
    const todayDate = new Date(today);
    const diffDays = Math.floor((todayDate - lastDate) / (1000 * 60 * 60 * 24));

    if (success) {
      if (diffDays === 0) {
        // Same day, no change
        return;
      } else if (diffDays === 1) {
        // Consecutive day
        const newStreak = streak.current_streak + 1;
        const longestStreak = Math.max(newStreak, streak.longest_streak);

        db.prepare(`
          UPDATE agent_streaks
          SET current_streak = ?,
              longest_streak = ?,
              last_activity_date = ?,
              updated_at = CURRENT_TIMESTAMP
          WHERE agent_id = ?
        `).run(newStreak, longestStreak, today, agentId);

        console.log(`🔥 [Gamification] ${agentId} streak: ${newStreak} days`);

        // Check for streak achievements
        checkAchievements(agentId);
      } else {
        // Streak broken, reset
        db.prepare(`
          UPDATE agent_streaks
          SET current_streak = 1,
              last_activity_date = ?,
              updated_at = CURRENT_TIMESTAMP
          WHERE agent_id = ?
        `).run(today, agentId);

        console.log(`💔 [Gamification] ${agentId} streak broken. Starting fresh.`);
      }
    }
  } catch (error) {
    console.error(`❌ [Gamification] Error updating streak:`, error);
  }
}

/**
 * Handle task completion (called by task completion logic)
 */
function onTaskCompleted(agentId, taskId, success = true, durationSeconds = null) {
  try {
    const baseXP = success ? XP_REWARDS.TASK_COMPLETED : XP_REWARDS.TASK_FAILED;
    let totalXP = baseXP;
    let reasons = [];

    if (success) {
      reasons.push('Task completed');

      // Quick completion bonus
      if (durationSeconds && durationSeconds < 120) {
        totalXP += XP_REWARDS.QUICK_COMPLETION;
        reasons.push('Quick completion bonus');
      }

      // First task of day bonus
      const today = new Date().toISOString().split('T')[0];
      const firstToday = db.prepare(`
        SELECT COUNT(*) as count
        FROM xp_transactions
        WHERE agent_id = ?
          AND source_type = 'task_completion'
          AND DATE(created_at) = ?
      `).get(agentId, today);

      if (firstToday.count === 0) {
        totalXP += XP_REWARDS.FIRST_TASK_OF_DAY;
        reasons.push('First task of the day');
      }

      // Update streak
      updateStreak(agentId, true);
    } else {
      reasons.push('Task failed');
    }

    // Award XP
    awardXP(agentId, totalXP, reasons.join(', '), 'task_completion', taskId);

    return { success: true, xp: totalXP };
  } catch (error) {
    console.error(`❌ [Gamification] Error handling task completion:`, error);
    return { success: false, error: error.message };
  }
}

/**
 * Handle session completion
 */
function onSessionCompleted(agentId, sessionId, success = true, tasksCompleted = 0, tasksFailed = 0) {
  try {
    const baseXP = success ? XP_REWARDS.SESSION_COMPLETED : XP_REWARDS.SESSION_FAILED;
    let totalXP = baseXP;
    let reasons = ['Session ' + (success ? 'completed' : 'failed')];

    // Perfect session bonus
    if (success && tasksFailed === 0 && tasksCompleted > 0) {
      totalXP += XP_REWARDS.PERFECT_SESSION;
      reasons.push('Perfect session (0 failures)');
    }

    awardXP(agentId, totalXP, reasons.join(', '), 'session_completion', sessionId);

    return { success: true, xp: totalXP };
  } catch (error) {
    console.error(`❌ [Gamification] Error handling session completion:`, error);
    return { success: false, error: error.message };
  }
}

/**
 * Get agent gamification summary
 */
function getAgentGamification(agentId) {
  try {
    const summary = db.prepare(`
      SELECT * FROM v_agent_gamification WHERE agent_id = ?
    `).get(agentId);

    if (!summary) {
      return { error: 'Agent not found' };
    }

    // Get recent achievements
    const achievements = db.prepare(`
      SELECT aa.*, ad.name, ad.description, ad.emoji, ad.tier
      FROM agent_achievements aa
      JOIN achievement_definitions ad ON aa.achievement_id = ad.id
      WHERE aa.agent_id = ?
      ORDER BY aa.unlocked_at DESC
      LIMIT 10
    `).all(agentId);

    // Get recent XP transactions
    const recentXP = db.prepare(`
      SELECT * FROM xp_transactions
      WHERE agent_id = ?
      ORDER BY created_at DESC
      LIMIT 10
    `).all(agentId);

    return {
      ...summary,
      achievements,
      recentXP,
      progressToNextLevel: summary.xp_to_next_level > 0 ?
        ((summary.current_xp / summary.next_level_xp) * 100).toFixed(1) : 100
    };
  } catch (error) {
    console.error(`❌ [Gamification] Error getting agent gamification:`, error);
    return { error: error.message };
  }
}

/**
 * Get global leaderboard
 */
function getLeaderboard(metric = 'xp', limit = 20) {
  try {
    const validMetrics = ['xp', 'tasks', 'success'];
    if (!validMetrics.includes(metric)) {
      metric = 'xp';
    }

    const rankColumn = metric === 'xp' ? 'xp_rank' :
                      metric === 'tasks' ? 'tasks_rank' : 'success_rank';

    const leaderboard = db.prepare(`
      SELECT * FROM v_leaderboard
      ORDER BY ${rankColumn}
      LIMIT ?
    `).all(limit);

    return leaderboard;
  } catch (error) {
    console.error(`❌ [Gamification] Error getting leaderboard:`, error);
    return [];
  }
}

/**
 * Get all achievements (unlocked + locked)
 */
function getAllAchievements(agentId) {
  try {
    const allAchievements = db.prepare(`
      SELECT
        ad.*,
        CASE WHEN aa.agent_id IS NOT NULL THEN 1 ELSE 0 END as unlocked,
        aa.unlocked_at
      FROM achievement_definitions ad
      LEFT JOIN agent_achievements aa ON ad.id = aa.achievement_id AND aa.agent_id = ?
      WHERE ad.is_active = TRUE
      ORDER BY ad.tier, ad.category, ad.name
    `).all(agentId);

    return allAchievements;
  } catch (error) {
    console.error(`❌ [Gamification] Error getting achievements:`, error);
    return [];
  }
}

module.exports = {
  awardXP,
  checkLevelUp,
  checkAchievements,
  updateStreak,
  onTaskCompleted,
  onSessionCompleted,
  getAgentGamification,
  getLeaderboard,
  getAllAchievements,
  XP_REWARDS
};
