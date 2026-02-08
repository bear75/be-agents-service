#!/usr/bin/env node
/**
 * SQLite Database Manager
 * Initializes and provides access to the agent service database
 */

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

const SERVICE_ROOT = path.join(__dirname, '..');
const DB_PATH = path.join(SERVICE_ROOT, '.compound-state/agent-service.db');
const SCHEMA_PATH = path.join(SERVICE_ROOT, 'schema.sql');

// Ensure data directory exists
const dataDir = path.dirname(DB_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Check if database needs initialization (before opening)
const needsInit = !fs.existsSync(DB_PATH);

// Initialize database
const db = new Database(DB_PATH);

// Enable foreign keys
db.pragma('foreign_keys = ON');

// Enable WAL mode for better concurrency
db.pragma('journal_mode = WAL');

/**
 * Initialize database schema
 */
function initializeSchema() {
  console.log('Initializing database schema...');

  const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');

  // Remove comments and split by semicolon
  const cleanSchema = schema
    .split('\n')
    .filter(line => !line.trim().startsWith('--'))
    .join('\n');

  // Use exec to run the entire schema at once (better-sqlite3 supports this)
  try {
    db.exec(cleanSchema);
    console.log('✅ Database schema initialized');
  } catch (error) {
    console.error('Error initializing schema:', error.message);
    throw error;
  }
}

// Initialize on first load
if (needsInit) {
  initializeSchema();
} else {
  // Check if tables exist
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
  if (tables.length === 0) {
    console.log('Database exists but empty, reinitializing...');
    initializeSchema();
  }
}

// ============================================
// TEAM OPERATIONS
// ============================================

/**
 * Get all teams
 */
function getAllTeams() {
  const stmt = db.prepare('SELECT * FROM teams ORDER BY name');
  return stmt.all();
}

/**
 * Get team by ID
 */
function getTeamById(teamId) {
  const stmt = db.prepare('SELECT * FROM teams WHERE id = ?');
  return stmt.get(teamId);
}

/**
 * Create a new team
 */
function createTeam({ id, name, domain, description }) {
  const stmt = db.prepare(`
    INSERT INTO teams (id, name, domain, description)
    VALUES (?, ?, ?, ?)
  `);

  stmt.run(id, name, domain, description);

  return getTeamById(id);
}

// ============================================
// SESSION OPERATIONS
// ============================================

/**
 * Create a new session
 */
function createSession({ sessionId, teamId, targetRepo, priorityFile, branchName }) {
  const stmt = db.prepare(`
    INSERT INTO sessions (id, team_id, status, target_repo, priority_file, branch_name)
    VALUES (?, ?, 'in_progress', ?, ?, ?)
  `);

  stmt.run(sessionId, teamId, targetRepo, priorityFile, branchName);

  return getSession(sessionId);
}

/**
 * Get session by ID
 */
function getSession(sessionId) {
  const stmt = db.prepare('SELECT * FROM sessions WHERE id = ?');
  return stmt.get(sessionId);
}

/**
 * Update session status
 */
function updateSessionStatus(sessionId, status, prUrl = null, exitCode = null) {
  const now = new Date().toISOString();

  const stmt = db.prepare(`
    UPDATE sessions
    SET status = ?,
        pr_url = COALESCE(?, pr_url),
        exit_code = COALESCE(?, exit_code),
        completed_at = CASE WHEN ? IN ('completed', 'failed') THEN ? ELSE completed_at END,
        duration_seconds = CASE
          WHEN ? IN ('completed', 'failed') THEN
            (julianday(?) - julianday(started_at)) * 86400
          ELSE duration_seconds
        END
    WHERE id = ?
  `);

  stmt.run(status, prUrl, exitCode, status, now, status, now, sessionId);
}

/**
 * Get recent sessions
 */
function getRecentSessions(limit = 10) {
  const stmt = db.prepare(`
    SELECT s.*, t.name as team_name
    FROM sessions s
    JOIN teams t ON s.team_id = t.id
    ORDER BY s.started_at DESC
    LIMIT ?
  `);

  return stmt.all(limit);
}

// ============================================
// TASK OPERATIONS
// ============================================

/**
 * Create a new task
 */
function createTask({ taskId, sessionId, agentId, description, priority = 'medium' }) {
  const stmt = db.prepare(`
    INSERT INTO tasks (id, session_id, agent_id, description, status, priority)
    VALUES (?, ?, ?, ?, 'pending', ?)
  `);

  stmt.run(taskId, sessionId, agentId, description, priority);

  return getTask(taskId);
}

/**
 * Get task by ID
 */
function getTask(taskId) {
  const stmt = db.prepare('SELECT * FROM tasks WHERE id = ?');
  return stmt.get(taskId);
}

/**
 * Update task status
 */
function updateTaskStatus(taskId, status, llmUsed = null, errorMessage = null) {
  const now = new Date().toISOString();

  const stmt = db.prepare(`
    UPDATE tasks
    SET status = ?,
        llm_used = COALESCE(?, llm_used),
        error_message = ?,
        completed_at = CASE WHEN ? IN ('completed', 'failed') THEN ? ELSE completed_at END,
        duration_seconds = CASE
          WHEN ? IN ('completed', 'failed') THEN
            (julianday(?) - julianday(started_at)) * 86400
          ELSE duration_seconds
        END
    WHERE id = ?
  `);

  stmt.run(status, llmUsed, errorMessage, status, now, status, now, taskId);

  // Update agent stats
  if (status === 'completed' || status === 'failed') {
    updateAgentStats(taskId);
  }
}

/**
 * Update agent statistics based on task completion
 */
function updateAgentStats(taskId) {
  const task = getTask(taskId);
  if (!task) return;

  const agentStats = db.prepare(`
    SELECT
      agent_id,
      COUNT(*) as total_tasks,
      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
      SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
      AVG(CASE WHEN duration_seconds IS NOT NULL THEN duration_seconds ELSE 0 END) as avg_duration
    FROM tasks
    WHERE agent_id = ?
    GROUP BY agent_id
  `).get(task.agent_id);

  if (agentStats) {
    const successRate = agentStats.completed / agentStats.total_tasks;

    db.prepare(`
      UPDATE agents
      SET total_tasks_completed = ?,
          total_tasks_failed = ?,
          success_rate = ?,
          avg_duration_seconds = ?,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(
      agentStats.completed,
      agentStats.failed,
      successRate,
      agentStats.avg_duration,
      task.agent_id
    );

    // Award XP for task completion (gamification)
    try {
      // Lazy-load gamification to avoid circular dependency
      const gamification = require('./gamification');
      const success = task.status === 'completed';
      gamification.onTaskCompleted(
        task.agent_id,
        task.id,
        success,
        task.duration_seconds
      );
    } catch (error) {
      console.error('⚠️  Gamification error:', error.message);
      // Don't fail task completion if gamification fails
    }
  }
}

/**
 * Get tasks for a session
 */
function getSessionTasks(sessionId) {
  const stmt = db.prepare(`
    SELECT t.*, a.name as agent_name, a.emoji as agent_emoji
    FROM tasks t
    JOIN agents a ON t.agent_id = a.id
    WHERE t.session_id = ?
    ORDER BY t.started_at DESC
  `);

  return stmt.all(sessionId);
}

// ============================================
// AGENT OPERATIONS
// ============================================

/**
 * Get all agents
 */
function getAllAgents() {
  const stmt = db.prepare(`
    SELECT a.*, t.name as team_name
    FROM agents a
    JOIN teams t ON a.team_id = t.id
    WHERE a.is_active = TRUE
    ORDER BY t.domain, a.name
  `);

  return stmt.all();
}

/**
 * Get agents by team
 */
function getAgentsByTeam(teamId) {
  const stmt = db.prepare(`
    SELECT * FROM agents
    WHERE team_id = ? AND is_active = TRUE
    ORDER BY name
  `);

  return stmt.all(teamId);
}

/**
 * Get agent by name
 */
function getAgentByName(teamId, name) {
  const stmt = db.prepare(`
    SELECT * FROM agents
    WHERE team_id = ? AND name = ?
  `);

  return stmt.get(teamId, name);
}

/**
 * Get agent by ID
 */
function getAgentById(agentId) {
  const stmt = db.prepare(`
    SELECT a.*, t.name as team_name, t.domain as team_domain
    FROM agents a
    LEFT JOIN teams t ON a.team_id = t.id
    WHERE a.id = ?
  `);

  return stmt.get(agentId);
}

/**
 * Create new agent
 */
function createAgent({ id, teamId, name, role, llmPreference = 'sonnet', emoji = '🤖' }) {
  const stmt = db.prepare(`
    INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active)
    VALUES (?, ?, ?, ?, ?, ?, TRUE)
  `);

  stmt.run(
    id,
    teamId,
    name,
    role,
    emoji,
    llmPreference
  );

  return getAgentById(id);
}

/**
 * Update agent
 */
function updateAgent(agentId, updates) {
  const allowedFields = ['name', 'role', 'emoji', 'llm_preference'];
  const fields = [];
  const values = [];

  for (const [key, value] of Object.entries(updates)) {
    if (allowedFields.includes(key)) {
      fields.push(`${key} = ?`);
      values.push(value);
    }
  }

  if (fields.length === 0) {
    return getAgentById(agentId);
  }

  values.push(agentId);

  const stmt = db.prepare(`
    UPDATE agents
    SET ${fields.join(', ')}
    WHERE id = ?
  `);

  stmt.run(...values);
  return getAgentById(agentId);
}

/**
 * Deactivate agent (soft delete / "fire")
 */
function deactivateAgent(agentId) {
  const stmt = db.prepare(`
    UPDATE agents
    SET is_active = FALSE
    WHERE id = ?
  `);

  stmt.run(agentId);
  return { success: true, agentId };
}

/**
 * Reactivate agent (rehire)
 */
function reactivateAgent(agentId) {
  const stmt = db.prepare(`
    UPDATE agents
    SET is_active = TRUE
    WHERE id = ?
  `);

  stmt.run(agentId);
  return getAgentById(agentId);
}

/**
 * Get agent evaluation metrics (comprehensive agent details)
 */
function getAgentEvaluation(agentId) {
  const agent = getAgentById(agentId);
  if (!agent) {
    return null;
  }

  // Get performance stats
  const perfStmt = db.prepare(`
    SELECT * FROM v_agent_performance
    WHERE id = ?
  `);
  const performance = perfStmt.get(agentId);

  // Get task stats by status
  const tasksStmt = db.prepare(`
    SELECT status, COUNT(*) as count
    FROM tasks
    WHERE agent_id = ?
    GROUP BY status
  `);
  const taskStats = tasksStmt.all(agentId);

  // Get recent tasks with details
  const recentTasksStmt = db.prepare(`
    SELECT id, description, status, started_at, completed_at, duration_seconds, llm_used
    FROM tasks
    WHERE agent_id = ?
    ORDER BY started_at DESC
    LIMIT 20
  `);
  const recentTasks = recentTasksStmt.all(agentId);

  // Get recent metrics
  const metricsStmt = db.prepare(`
    SELECT metric_name, metric_value, recorded_at
    FROM metrics
    WHERE entity_type = 'agent' AND entity_id = ?
    ORDER BY recorded_at DESC
    LIMIT 10
  `);
  const recentMetrics = metricsStmt.all(agentId);

  // Get lessons learned related to this agent
  const lessonsStmt = db.prepare(`
    SELECT id, category, title, description, times_encountered, is_automated, last_encountered_at
    FROM lessons_learned
    ORDER BY last_encountered_at DESC
    LIMIT 10
  `);
  const lessonsLearned = lessonsStmt.all();

  // Get gamification data
  let gamificationData = null;
  try {
    const gamification = require('./gamification');
    gamificationData = gamification.getAgentGamification(agentId);
  } catch (error) {
    console.error('⚠️  Error loading gamification:', error.message);
  }

  // Calculate RL evaluation
  const successRate = performance ? performance.success_rate_pct / 100 : 0;
  const totalTasks = performance ? performance.total_tasks_completed + performance.total_tasks_failed : 0;

  let recommendation = 'continue';
  let reason = 'Agent is performing normally';

  if (totalTasks === 0) {
    recommendation = 'monitor';
    reason = 'No tasks completed yet - monitor initial performance';
  } else if (successRate >= 0.9 && totalTasks >= 5) {
    recommendation = 'double_down';
    reason = `High performer: ${(successRate * 100).toFixed(0)}% success rate over ${totalTasks} tasks`;
  } else if (successRate < 0.5 && totalTasks >= 5) {
    recommendation = 'investigate';
    reason = `Struggling: ${(successRate * 100).toFixed(0)}% success rate - needs improvement`;
  } else if (successRate < 0.3 && totalTasks >= 10) {
    recommendation = 'consider_firing';
    reason = `Underperforming: ${(successRate * 100).toFixed(0)}% success rate over ${totalTasks} tasks`;
  }

  return {
    agent,
    performance,
    taskStats,
    recentTasks,
    recentMetrics,
    lessonsLearned,
    gamification: gamificationData,
    evaluation: {
      successRate: (successRate * 100).toFixed(1) + '%',
      totalTasks,
      recommendation,
      reason
    }
  };
}

// ============================================
// METRICS OPERATIONS
// ============================================

/**
 * Record a metric
 */
function recordMetric({ entityType, entityId, metricName, metricValue, context = null }) {
  const stmt = db.prepare(`
    INSERT INTO metrics (entity_type, entity_id, metric_name, metric_value, context)
    VALUES (?, ?, ?, ?, ?)
  `);

  stmt.run(entityType, entityId, metricName, metricValue, context ? JSON.stringify(context) : null);
}

/**
 * Get metrics for entity
 */
function getMetrics(entityType, entityId, metricName = null) {
  let stmt;

  if (metricName) {
    stmt = db.prepare(`
      SELECT * FROM metrics
      WHERE entity_type = ? AND entity_id = ? AND metric_name = ?
      ORDER BY recorded_at DESC
    `);
    return stmt.all(entityType, entityId, metricName);
  } else {
    stmt = db.prepare(`
      SELECT * FROM metrics
      WHERE entity_type = ? AND entity_id = ?
      ORDER BY recorded_at DESC
    `);
    return stmt.all(entityType, entityId);
  }
}

// ============================================
// REWARD OPERATIONS (RL)
// ============================================

/**
 * Issue a reward
 */
function issueReward({ entityType, entityId, rewardValue, reason }) {
  const stmt = db.prepare(`
    INSERT INTO rewards (entity_type, entity_id, reward_value, reason)
    VALUES (?, ?, ?, ?)
  `);

  stmt.run(entityType, entityId, rewardValue, reason);

  return { entityType, entityId, rewardValue, reason };
}

/**
 * Get total rewards for entity
 */
function getEntityRewards(entityType, entityId) {
  const stmt = db.prepare(`
    SELECT
      SUM(reward_value) as total_reward,
      COUNT(*) as reward_count,
      AVG(reward_value) as avg_reward
    FROM rewards
    WHERE entity_type = ? AND entity_id = ?
  `);

  return stmt.get(entityType, entityId);
}

// ============================================
// PATTERN OPERATIONS
// ============================================

/**
 * Record a detected pattern
 */
function recordPattern({ patternId, patternType, description, confidenceScore = 0.5 }) {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO patterns (id, pattern_type, description, detection_count, confidence_score, last_detected_at)
    VALUES (
      ?,
      ?,
      ?,
      COALESCE((SELECT detection_count FROM patterns WHERE id = ?), 0) + 1,
      ?,
      CURRENT_TIMESTAMP
    )
  `);

  stmt.run(patternId, patternType, description, patternId, confidenceScore);
}

/**
 * Get patterns by type
 */
function getPatterns(patternType = null, status = 'active') {
  let stmt;

  if (patternType) {
    stmt = db.prepare(`
      SELECT * FROM patterns
      WHERE pattern_type = ? AND status = ?
      ORDER BY detection_count DESC, confidence_score DESC
    `);
    return stmt.all(patternType, status);
  } else {
    stmt = db.prepare(`
      SELECT * FROM patterns
      WHERE status = ?
      ORDER BY detection_count DESC, confidence_score DESC
    `);
    return stmt.all(status);
  }
}

/**
 * Update pattern status
 */
function updatePatternStatus(patternId, status, actionTaken = null) {
  const stmt = db.prepare(`
    UPDATE patterns
    SET status = ?,
        action_taken = COALESCE(?, action_taken),
        actioned_at = CASE WHEN ? IS NOT NULL THEN CURRENT_TIMESTAMP ELSE actioned_at END
    WHERE id = ?
  `);

  stmt.run(status, actionTaken, actionTaken, patternId);
}

// ============================================
// USER COMMAND TRACKING
// ============================================

/**
 * Track user command
 */
function trackUserCommand({ commandText, normalizedIntent, team, model, priorityFile, branchName }) {
  const stmt = db.prepare(`
    INSERT INTO user_commands (command_text, normalized_intent, team, model, priority_file, branch_name)
    VALUES (?, ?, ?, ?, ?, ?)
  `);

  stmt.run(commandText, normalizedIntent, team, model, priorityFile, branchName);
}

/**
 * Get automation candidates (3+ repetitions)
 */
function getAutomationCandidates() {
  const stmt = db.prepare(`
    SELECT * FROM automation_candidates
    WHERE occurrence_count >= 3
      AND is_automated = FALSE
    ORDER BY occurrence_count DESC, confidence_score DESC
  `);

  return stmt.all();
}

/**
 * Create or update automation candidate
 */
function updateAutomationCandidate({ patternId, description, sampleCommands, confidenceScore }) {
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO automation_candidates
      (id, pattern_description, occurrence_count, sample_commands, confidence_score, last_occurrence_at)
    VALUES (
      ?,
      ?,
      COALESCE((SELECT occurrence_count FROM automation_candidates WHERE id = ?), 0) + 1,
      ?,
      ?,
      CURRENT_TIMESTAMP
    )
  `);

  stmt.run(patternId, description, patternId, JSON.stringify(sampleCommands), confidenceScore);
}

// ============================================
// EXPERIMENT OPERATIONS
// ============================================

/**
 * Create experiment
 */
function createExperiment({ experimentId, name, description, successMetric, targetValue }) {
  const stmt = db.prepare(`
    INSERT INTO experiments (id, name, description, success_metric, target_value)
    VALUES (?, ?, ?, ?, ?)
  `);

  stmt.run(experimentId, name, description, successMetric, targetValue);

  return getExperiment(experimentId);
}

/**
 * Get experiment
 */
function getExperiment(experimentId) {
  const stmt = db.prepare('SELECT * FROM experiments WHERE id = ?');
  return stmt.get(experimentId);
}

/**
 * Update experiment
 */
function updateExperiment(experimentId, { currentValue, consecutiveFailures, decision, decisionReason }) {
  const stmt = db.prepare(`
    UPDATE experiments
    SET current_value = COALESCE(?, current_value),
        consecutive_failures = COALESCE(?, consecutive_failures),
        sample_size = sample_size + 1,
        decision = COALESCE(?, decision),
        decision_reason = COALESCE(?, decision_reason),
        decided_at = CASE WHEN ? IS NOT NULL THEN CURRENT_TIMESTAMP ELSE decided_at END,
        status = CASE
          WHEN ? = 'kill' THEN 'killed'
          WHEN ? = 'double_down' THEN 'successful'
          ELSE status
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `);

  stmt.run(
    currentValue,
    consecutiveFailures,
    decision,
    decisionReason,
    decision,
    decision,
    decision,
    experimentId
  );
}

/**
 * Get active experiments
 */
function getActiveExperiments() {
  const stmt = db.prepare(`
    SELECT * FROM experiments
    WHERE status = 'active'
    ORDER BY created_at DESC
  `);

  return stmt.all();
}

// ============================================
// VIEWS & ANALYTICS
// ============================================

/**
 * Get active sessions view
 */
function getActiveSessions() {
  const stmt = db.prepare('SELECT * FROM v_active_sessions');
  return stmt.all();
}

/**
 * Get agent performance view
 */
function getAgentPerformance() {
  const stmt = db.prepare('SELECT * FROM v_agent_performance');
  return stmt.all();
}

/**
 * Get user command patterns (for automation)
 */
function getUserCommandPatterns() {
  const stmt = db.prepare('SELECT * FROM v_user_command_patterns');
  return stmt.all();
}

/**
 * Get experiment status summary
 */
function getExperimentStatusSummary() {
  const stmt = db.prepare('SELECT * FROM v_experiment_status');
  return stmt.all();
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Run a transaction
 */
function transaction(fn) {
  return db.transaction(fn);
}

/**
 * Close database connection
 */
function close() {
  db.close();
}

// ============================================
// INTEGRATIONS OPERATIONS
// ============================================

/**
 * Get all integrations
 */
function getAllIntegrations() {
  const stmt = db.prepare(`
    SELECT * FROM integrations
    ORDER BY type, platform
  `);
  return stmt.all();
}

/**
 * Get integrations by type
 */
function getIntegrationsByType(type) {
  const stmt = db.prepare(`
    SELECT * FROM integrations
    WHERE type = ?
    ORDER BY platform
  `);
  return stmt.all(type);
}

/**
 * Get single integration
 */
function getIntegration(id) {
  const stmt = db.prepare(`
    SELECT * FROM integrations
    WHERE id = ?
  `);
  return stmt.get(id);
}

/**
 * Update integration
 */
function updateIntegration(id, updates) {
  const { is_active, credentials, config, last_connected_at } = updates;

  const stmt = db.prepare(`
    UPDATE integrations
    SET is_active = COALESCE(?, is_active),
        credentials = COALESCE(?, credentials),
        config = COALESCE(?, config),
        last_connected_at = COALESCE(?, last_connected_at),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `);

  stmt.run(is_active, credentials, config, last_connected_at, id);
  return getIntegration(id);
}

/**
 * Create integration
 */
function createIntegration({ id, type, platform, name, is_active, credentials, config }) {
  const stmt = db.prepare(`
    INSERT INTO integrations (id, type, platform, name, is_active, credentials, config)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  // Convert boolean to integer for SQLite (0 or 1)
  const isActiveInt = (is_active !== undefined && is_active !== null) ? (is_active ? 1 : 0) : 0;

  stmt.run(id, type, platform, name, isActiveInt, credentials || null, config || null);
  return getIntegration(id);
}

// ============================================
// MARKETING DATA OPERATIONS
// ============================================

/**
 * Get all campaigns from database
 */
function getAllCampaigns() {
  const stmt = db.prepare(`
    SELECT
      c.*,
      a.name as owner_name,
      a.emoji as owner_emoji
    FROM campaigns c
    LEFT JOIN agents a ON c.owner = a.id
    ORDER BY c.created_at DESC
  `);
  return stmt.all();
}

/**
 * Get all leads from database
 */
function getAllLeads() {
  const stmt = db.prepare(`
    SELECT
      l.*,
      a.name as assigned_to_name,
      a.emoji as assigned_to_emoji
    FROM leads l
    LEFT JOIN agents a ON l.assigned_to = a.id
    ORDER BY l.created_at DESC
  `);
  return stmt.all();
}

/**
 * Get all content from database
 */
function getAllContent() {
  const stmt = db.prepare(`
    SELECT
      c.*,
      a.name as author_name,
      a.emoji as author_emoji,
      camp.name as campaign_name
    FROM content c
    LEFT JOIN agents a ON c.author = a.id
    LEFT JOIN campaigns camp ON c.campaign_id = camp.id
    ORDER BY c.created_at DESC
  `);
  return stmt.all();
}

/**
 * Get content by type
 */
function getContentByType(type) {
  const stmt = db.prepare(`
    SELECT
      c.*,
      a.name as author_name,
      a.emoji as author_emoji,
      camp.name as campaign_name
    FROM content c
    LEFT JOIN agents a ON c.author = a.id
    LEFT JOIN campaigns camp ON c.campaign_id = camp.id
    WHERE c.type = ?
    ORDER BY c.created_at DESC
  `);
  return stmt.all(type);
}

/**
 * Get all tasks
 */
function getAllTasks() {
  const stmt = db.prepare(`
    SELECT
      t.*,
      a.name as agent_name,
      a.emoji as agent_emoji,
      te.name as team_name
    FROM tasks t
    LEFT JOIN agents a ON t.agent_id = a.id
    LEFT JOIN teams te ON a.team_id = te.id
    ORDER BY t.started_at DESC
  `);
  return stmt.all();
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  db,

  // Schema
  initializeSchema,

  // Teams
  getAllTeams,
  getTeamById,
  createTeam,

  // Sessions
  createSession,
  getSession,
  updateSessionStatus,
  getRecentSessions,
  getActiveSessions,

  // Tasks
  createTask,
  getTask,
  updateTaskStatus,
  getSessionTasks,
  getAllTasks,

  // Agents
  getAllAgents,
  getAgentsByTeam,
  getAgentByName,
  getAgentById,
  createAgent,
  updateAgent,
  deactivateAgent,
  reactivateAgent,
  getAgentEvaluation,
  getAgentPerformance,

  // Metrics
  recordMetric,
  getMetrics,

  // Rewards
  issueReward,
  getEntityRewards,

  // Patterns
  recordPattern,
  getPatterns,
  updatePatternStatus,

  // User Commands
  trackUserCommand,
  getAutomationCandidates,
  updateAutomationCandidate,
  getUserCommandPatterns,

  // Experiments
  createExperiment,
  getExperiment,
  updateExperiment,
  getActiveExperiments,
  getExperimentStatusSummary,

  // Marketing Data
  getAllCampaigns,
  getAllLeads,
  getAllContent,
  getContentByType,

  // Integrations
  getAllIntegrations,
  getIntegrationsByType,
  getIntegration,
  updateIntegration,
  createIntegration,

  // Utility
  transaction,
  close
};
