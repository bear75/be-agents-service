#!/usr/bin/env node
/**
 * Learning Controller - Reinforcement Learning System
 * Implements "keep/kill/double-down" logic based on metrics
 *
 * Core Principles:
 * 1. If it's working (success rate ≥ 90%) → double down
 * 2. If it's failing (3+ consecutive failures) → kill
 * 3. If improving → keep/continue
 */

const db = require('./database');

// ============================================
// REWARD VALUES (from plan)
// ============================================

const REWARDS = {
  TASK_COMPLETED: 10,
  SESSION_PR_MERGED: 25,
  EXPERIMENT_SUCCESS: 50,
  USER_PRAISE: 100,

  TASK_FAILED: -5,
  SESSION_BLOCKED: -20,
  EXPERIMENT_KILLED: -50,
  USER_REJECTION: -100
};

// ============================================
// DECISION THRESHOLDS
// ============================================

const THRESHOLDS = {
  CONSECUTIVE_FAILURES_TO_KILL: 3,
  MIN_SUCCESS_RATE_FOR_DOUBLE_DOWN: 0.9,
  MIN_SAMPLE_SIZE_FOR_DECISION: 5,
  STAGNANT_ATTEMPTS_TO_KILL: 5,
  USER_REPETITION_TO_AUTOMATE: 3
};

// ============================================
// TASK REWARDS
// ============================================

/**
 * Issue reward for task completion
 */
function rewardTaskCompletion(taskId) {
  const task = db.getTask(taskId);

  if (!task) {
    console.error(`Task ${taskId} not found`);
    return null;
  }

  let rewardValue;
  let reason;

  if (task.status === 'completed') {
    rewardValue = REWARDS.TASK_COMPLETED;
    reason = 'Task completed successfully';
  } else if (task.status === 'failed') {
    rewardValue = REWARDS.TASK_FAILED;
    reason = 'Task failed';
  } else {
    console.error(`Task ${taskId} is not in terminal state (${task.status})`);
    return null;
  }

  const reward = db.issueReward({
    entityType: 'task',
    entityId: taskId,
    rewardValue,
    reason
  });

  // Record metrics
  db.recordMetric({
    entityType: 'task',
    entityId: taskId,
    metricName: 'reward',
    metricValue: rewardValue
  });

  return reward;
}

/**
 * Issue reward for session completion
 */
function rewardSessionCompletion(sessionId, prMerged = false) {
  const session = db.getSession(sessionId);

  if (!session) {
    console.error(`Session ${sessionId} not found`);
    return null;
  }

  let rewardValue;
  let reason;

  if (session.status === 'completed' && prMerged) {
    rewardValue = REWARDS.SESSION_PR_MERGED;
    reason = 'Session completed with PR merged';
  } else if (session.status === 'blocked') {
    rewardValue = REWARDS.SESSION_BLOCKED;
    reason = 'Session blocked';
  } else if (session.status === 'failed') {
    rewardValue = REWARDS.TASK_FAILED * 2; // Double penalty for session failure
    reason = 'Session failed';
  } else {
    console.error(`Session ${sessionId} is not in terminal state (${session.status})`);
    return null;
  }

  const reward = db.issueReward({
    entityType: 'session',
    entityId: sessionId,
    rewardValue,
    reason
  });

  // Record metrics
  db.recordMetric({
    entityType: 'session',
    entityId: sessionId,
    metricName: 'reward',
    metricValue: rewardValue
  });

  return reward;
}

/**
 * Issue user feedback reward (explicit praise or rejection)
 */
function rewardUserFeedback(entityType, entityId, isPositive, comment = '') {
  const rewardValue = isPositive ? REWARDS.USER_PRAISE : REWARDS.USER_REJECTION;
  const reason = isPositive
    ? `User praised: ${comment}`
    : `User rejected: ${comment}`;

  const reward = db.issueReward({
    entityType,
    entityId,
    rewardValue,
    reason
  });

  // Record metrics
  db.recordMetric({
    entityType,
    entityId,
    metricName: 'user_feedback',
    metricValue: isPositive ? 1 : -1,
    context: comment
  });

  return reward;
}

// ============================================
// EXPERIMENT EVALUATION
// ============================================

/**
 * Evaluate experiment and make keep/kill/double-down decision
 */
function evaluateExperiment(experimentId) {
  const experiment = db.getExperiment(experimentId);

  if (!experiment || experiment.status !== 'active') {
    return null;
  }

  const metrics = db.getMetrics('experiment', experimentId);

  // Calculate statistics
  const successCount = metrics.filter(m => m.metric_name === 'success').length;
  const failureCount = metrics.filter(m => m.metric_name === 'failure').length;
  const totalAttempts = successCount + failureCount;

  const successRate = totalAttempts > 0 ? successCount / totalAttempts : 0;
  const consecutiveFailures = countConsecutiveFailures(metrics);

  // Decision logic
  let decision = 'continue';
  let decisionReason = '';

  // KILL: 3+ consecutive failures (conservative - from plan)
  if (consecutiveFailures >= THRESHOLDS.CONSECUTIVE_FAILURES_TO_KILL) {
    decision = 'kill';
    decisionReason = `${consecutiveFailures} consecutive failures - killing experiment`;

    // Issue negative reward
    db.issueReward({
      entityType: 'experiment',
      entityId: experimentId,
      rewardValue: REWARDS.EXPERIMENT_KILLED,
      reason: decisionReason
    });
  }
  // DOUBLE DOWN: Success rate ≥ 90% with sufficient sample size
  else if (
    successRate >= THRESHOLDS.MIN_SUCCESS_RATE_FOR_DOUBLE_DOWN &&
    totalAttempts >= THRESHOLDS.MIN_SAMPLE_SIZE_FOR_DECISION
  ) {
    decision = 'double_down';
    decisionReason = `Success rate ${(successRate * 100).toFixed(1)}% with ${totalAttempts} attempts - doubling down`;

    // Issue positive reward
    db.issueReward({
      entityType: 'experiment',
      entityId: experimentId,
      rewardValue: REWARDS.EXPERIMENT_SUCCESS,
      reason: decisionReason
    });
  }
  // KILL: Stagnant for 5+ attempts
  else if (totalAttempts >= THRESHOLDS.STAGNANT_ATTEMPTS_TO_KILL && successRate < 0.3) {
    decision = 'kill';
    decisionReason = `Stagnant after ${totalAttempts} attempts with ${(successRate * 100).toFixed(1)}% success rate`;

    db.issueReward({
      entityType: 'experiment',
      entityId: experimentId,
      rewardValue: REWARDS.EXPERIMENT_KILLED,
      reason: decisionReason
    });
  }
  // CONTINUE: Improving or insufficient data
  else {
    decisionReason = `Continuing - ${totalAttempts} attempts, ${(successRate * 100).toFixed(1)}% success rate`;
  }

  // Update experiment in database
  db.updateExperiment(experimentId, {
    currentValue: successRate,
    consecutiveFailures,
    decision,
    decisionReason
  });

  return {
    experimentId,
    decision,
    decisionReason,
    stats: {
      totalAttempts,
      successCount,
      failureCount,
      successRate: (successRate * 100).toFixed(1) + '%',
      consecutiveFailures
    }
  };
}

/**
 * Count consecutive failures in metrics
 */
function countConsecutiveFailures(metrics) {
  // Sort by recorded_at descending (most recent first)
  const sorted = metrics
    .filter(m => m.metric_name === 'success' || m.metric_name === 'failure')
    .sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at));

  let count = 0;
  for (const metric of sorted) {
    if (metric.metric_name === 'failure') {
      count++;
    } else {
      break; // Stop at first success
    }
  }

  return count;
}

/**
 * Evaluate all active experiments
 */
function evaluateAllExperiments() {
  const experiments = db.getActiveExperiments();
  const results = [];

  for (const exp of experiments) {
    const result = evaluateExperiment(exp.id);
    if (result) {
      results.push(result);
    }
  }

  return results;
}

// ============================================
// PATTERN-BASED LEARNING
// ============================================

/**
 * Detect success patterns (things that work consistently)
 */
function detectSuccessPattern(description, entityType, entityId) {
  const patternId = `success-${entityType}-${description.replace(/\s+/g, '-').toLowerCase()}`;

  db.recordPattern({
    patternId,
    patternType: 'success',
    description,
    confidenceScore: 0.8
  });

  // Record metric
  db.recordMetric({
    entityType,
    entityId,
    metricName: 'pattern_detected',
    metricValue: 1,
    context: JSON.stringify({ pattern: 'success', description })
  });

  return patternId;
}

/**
 * Detect failure patterns (things that consistently fail)
 */
function detectFailurePattern(description, entityType, entityId) {
  const patternId = `failure-${entityType}-${description.replace(/\s+/g, '-').toLowerCase()}`;

  db.recordPattern({
    patternId,
    patternType: 'failure',
    description,
    confidenceScore: 0.7
  });

  // Record metric
  db.recordMetric({
    entityType,
    entityId,
    metricName: 'pattern_detected',
    metricValue: -1,
    context: JSON.stringify({ pattern: 'failure', description })
  });

  return patternId;
}

/**
 * Get patterns that should be acted upon
 */
function getActionablePatterns() {
  const successPatterns = db.getPatterns('success', 'active')
    .filter(p => p.detection_count >= 3 && p.confidence_score >= 0.7);

  const failurePatterns = db.getPatterns('failure', 'active')
    .filter(p => p.detection_count >= 3 && p.confidence_score >= 0.6);

  return {
    successes: successPatterns.map(p => ({
      id: p.id,
      description: p.description,
      detections: p.detection_count,
      confidence: (p.confidence_score * 100).toFixed(1) + '%',
      action: 'double_down'
    })),
    failures: failurePatterns.map(p => ({
      id: p.id,
      description: p.description,
      detections: p.detection_count,
      confidence: (p.confidence_score * 100).toFixed(1) + '%',
      action: 'kill'
    }))
  };
}

// ============================================
// SESSION ANALYSIS
// ============================================

/**
 * Analyze session and extract learnings
 */
function analyzeSession(sessionId) {
  const session = db.getSession(sessionId);
  const tasks = db.getSessionTasks(sessionId);

  if (!session || !tasks.length) {
    return null;
  }

  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');
  const totalDuration = tasks.reduce((sum, t) => sum + (t.duration_seconds || 0), 0);

  const successRate = tasks.length > 0 ? completedTasks.length / tasks.length : 0;

  // Detect patterns
  if (successRate >= 0.9) {
    detectSuccessPattern(
      `Session completed successfully with ${(successRate * 100).toFixed(0)}% task success`,
      'session',
      sessionId
    );
  } else if (successRate < 0.5) {
    detectFailurePattern(
      `Session struggled with ${(successRate * 100).toFixed(0)}% task success`,
      'session',
      sessionId
    );
  }

  // Record session metrics
  db.recordMetric({
    entityType: 'session',
    entityId: sessionId,
    metricName: 'success_rate',
    metricValue: successRate
  });

  db.recordMetric({
    entityType: 'session',
    entityId: sessionId,
    metricName: 'total_duration_seconds',
    metricValue: totalDuration
  });

  db.recordMetric({
    entityType: 'session',
    entityId: sessionId,
    metricName: 'iteration_count',
    metricValue: session.iteration_count || 0
  });

  return {
    sessionId,
    successRate: (successRate * 100).toFixed(1) + '%',
    completedTasks: completedTasks.length,
    failedTasks: failedTasks.length,
    totalDuration: `${Math.floor(totalDuration / 60)}m ${totalDuration % 60}s`,
    iterationCount: session.iteration_count || 0
  };
}

// ============================================
// AGENT PERFORMANCE ANALYSIS
// ============================================

/**
 * Get agent performance insights
 */
function getAgentInsights() {
  const agents = db.getAgentPerformance();

  return agents.map(agent => {
    const isHighPerformer = agent.success_rate_pct >= 90;
    const isStruggling = agent.success_rate_pct < 50 && agent.total_tasks_completed >= 5;

    let recommendation = 'continue';

    if (isHighPerformer) {
      recommendation = 'double_down';
    } else if (isStruggling) {
      recommendation = 'investigate';
    }

    return {
      name: agent.name,
      team: agent.team_name,
      successRate: agent.success_rate_pct + '%',
      tasksCompleted: agent.total_tasks_completed,
      tasksFailed: agent.total_tasks_failed,
      avgDuration: agent.avg_duration_minutes + ' min',
      recommendation
    };
  });
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  // Rewards
  REWARDS,
  THRESHOLDS,
  rewardTaskCompletion,
  rewardSessionCompletion,
  rewardUserFeedback,

  // Experiments
  evaluateExperiment,
  evaluateAllExperiments,

  // Patterns
  detectSuccessPattern,
  detectFailurePattern,
  getActionablePatterns,

  // Analysis
  analyzeSession,
  getAgentInsights
};
