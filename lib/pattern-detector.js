#!/usr/bin/env node
/**
 * Pattern Detector - User Repetition & Automation Discovery
 * Detects when user repeats tasks 3+ times and proposes automation
 */

const db = require('./database');

// ============================================
// USER COMMAND PATTERN DETECTION
// ============================================

/**
 * Normalize command text to detect intent
 * @param {Object} command - User command object
 * @returns {string} Normalized intent
 */
function normalizeCommandIntent(command) {
  const { team, model, priorityFile, branchName } = command;

  // Extract priority type (e.g., "blog-post", "feature", "bug-fix")
  let priorityType = 'general';

  if (priorityFile) {
    // Extract from filename
    const filename = priorityFile.split('/').pop().toLowerCase();

    if (filename.includes('blog')) {
      priorityType = 'blog-post';
    } else if (filename.includes('feature')) {
      priorityType = 'feature';
    } else if (filename.includes('bug')) {
      priorityType = 'bug-fix';
    } else if (filename.includes('refactor')) {
      priorityType = 'refactor';
    } else if (filename.includes('seo')) {
      priorityType = 'seo-optimization';
    } else if (filename.includes('email')) {
      priorityType = 'email-campaign';
    } else if (filename.includes('social')) {
      priorityType = 'social-media';
    } else if (filename.includes('landing')) {
      priorityType = 'landing-page';
    }
  }

  // Normalize intent: team + priority type
  return `${team}-${priorityType}`;
}

/**
 * Analyze recent user commands for patterns
 * @param {number} days - Number of days to look back
 * @returns {Array} Detected patterns
 */
function analyzeUserCommands(days = 7) {
  // Get user command patterns from view
  const patterns = db.getUserCommandPatterns();

  const automationCandidates = [];

  for (const pattern of patterns) {
    if (pattern.occurrence_count >= 3) {
      // Check if already automated
      const existing = db.getAutomationCandidates().find(
        c => c.pattern_description === pattern.normalized_intent
      );

      if (!existing || !existing.is_automated) {
        automationCandidates.push({
          intent: pattern.normalized_intent,
          occurrences: pattern.occurrence_count,
          teams: pattern.teams_used,
          models: pattern.models_used,
          lastExecuted: pattern.last_executed,
          recommendation: 'create_dedicated_agent'
        });
      }
    }
  }

  return automationCandidates;
}

/**
 * Create automation candidate in database
 * @param {Object} candidate - Automation candidate details
 */
function createAutomationCandidate(candidate) {
  const patternId = `auto-${candidate.intent.replace(/\s+/g, '-').toLowerCase()}`;

  // Get sample commands for this pattern
  const recentCommands = db.db.prepare(`
    SELECT command_text, team, model, priority_file, branch_name, executed_at
    FROM user_commands
    WHERE normalized_intent = ?
    ORDER BY executed_at DESC
    LIMIT 5
  `).all(candidate.intent);

  db.updateAutomationCandidate({
    patternId,
    description: `Automated ${candidate.intent} workflow`,
    sampleCommands: recentCommands,
    confidenceScore: Math.min(0.5 + (candidate.occurrences * 0.1), 0.95)
  });

  // Record pattern in patterns table
  db.recordPattern({
    patternId,
    patternType: 'user_repetition',
    description: `User repeatedly executes: ${candidate.intent}`,
    confidenceScore: Math.min(0.5 + (candidate.occurrences * 0.1), 0.95)
  });

  return patternId;
}

/**
 * Get automation candidates requiring approval
 */
function getAutomationCandidatesForApproval() {
  const candidates = db.getAutomationCandidates();

  return candidates.map(c => {
    const samples = JSON.parse(c.sample_commands || '[]');

    return {
      id: c.id,
      description: c.pattern_description,
      occurrences: c.occurrence_count,
      confidence: (c.confidence_score * 100).toFixed(1) + '%',
      samples: samples.slice(0, 3), // Show top 3 examples
      needsApproval: !c.approved_by_user,
      status: c.is_automated ? 'automated' : 'pending'
    };
  });
}

/**
 * Approve automation candidate
 * @param {string} candidateId - Automation candidate ID
 * @returns {Object} Approval result with agent creation instructions
 */
function approveAutomationCandidate(candidateId) {
  const candidate = db.db.prepare(
    'SELECT * FROM automation_candidates WHERE id = ?'
  ).get(candidateId);

  if (!candidate) {
    throw new Error(`Automation candidate ${candidateId} not found`);
  }

  // Mark as approved
  db.db.prepare(`
    UPDATE automation_candidates
    SET approved_by_user = TRUE,
        approved_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `).run(candidateId);

  // Extract team from pattern
  const samples = JSON.parse(candidate.sample_commands || '[]');
  const team = samples[0]?.team || 'engineering';

  return {
    candidateId,
    approved: true,
    nextStep: 'create_agent',
    agentSpec: {
      name: candidate.pattern_description.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      team,
      purpose: `Automate ${candidate.pattern_description} workflow`,
      sampleCommands: samples
    }
  };
}

// ============================================
// FAILURE PATTERN DETECTION
// ============================================

/**
 * Detect recurring failure patterns across sessions
 * @returns {Array} Detected failure patterns
 */
function detectRecurringFailures() {
  // Query tasks for common failure messages
  const failedTasks = db.db.prepare(`
    SELECT
      agent_id,
      error_message,
      COUNT(*) as failure_count,
      MAX(completed_at) as last_failure
    FROM tasks
    WHERE status = 'failed'
      AND error_message IS NOT NULL
      AND completed_at >= datetime('now', '-7 days')
    GROUP BY agent_id, error_message
    HAVING failure_count >= 2
    ORDER BY failure_count DESC
  `).all();

  const patterns = [];

  for (const failure of failedTasks) {
    const agent = db.db.prepare('SELECT name, team_id FROM agents WHERE id = ?').get(failure.agent_id);

    const patternId = `failure-${failure.agent_id}-${failure.error_message.substring(0, 50).replace(/\s+/g, '-').toLowerCase()}`;

    patterns.push({
      id: patternId,
      agent: agent?.name || 'Unknown',
      errorMessage: failure.error_message,
      occurrences: failure.failure_count,
      lastOccurrence: failure.last_failure,
      recommendation: failure.failure_count >= 3 ? 'fix_or_disable' : 'investigate'
    });

    // Record in database
    db.recordPattern({
      patternId,
      patternType: 'failure',
      description: `${agent?.name || 'Unknown'} repeatedly fails with: ${failure.error_message.substring(0, 100)}`,
      confidenceScore: Math.min(0.4 + (failure.failure_count * 0.15), 0.9)
    });
  }

  return patterns;
}

/**
 * Detect success patterns (things that consistently work)
 * @returns {Array} Detected success patterns
 */
function detectSuccessPatterns() {
  // Query for agents with high success rates
  const successfulAgents = db.db.prepare(`
    SELECT
      a.id,
      a.name,
      a.team_id,
      COUNT(t.id) as total_tasks,
      SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
      AVG(t.duration_seconds) as avg_duration
    FROM agents a
    JOIN tasks t ON a.id = t.agent_id
    WHERE t.completed_at >= datetime('now', '-14 days')
    GROUP BY a.id
    HAVING total_tasks >= 5 AND (completed_tasks * 1.0 / total_tasks) >= 0.9
    ORDER BY (completed_tasks * 1.0 / total_tasks) DESC
  `).all();

  const patterns = [];

  for (const agent of successfulAgents) {
    const successRate = agent.completed_tasks / agent.total_tasks;
    const patternId = `success-${agent.id}-high-performance`;

    patterns.push({
      id: patternId,
      agent: agent.name,
      successRate: (successRate * 100).toFixed(1) + '%',
      totalTasks: agent.total_tasks,
      avgDuration: `${Math.floor(agent.avg_duration / 60)}m`,
      recommendation: 'double_down'
    });

    // Record in database
    db.recordPattern({
      patternId,
      patternType: 'success',
      description: `${agent.name} consistently succeeds with ${(successRate * 100).toFixed(1)}% success rate`,
      confidenceScore: Math.min(0.7 + (successRate * 0.3), 0.99)
    });
  }

  return patterns;
}

// ============================================
// PATTERN SUMMARY
// ============================================

/**
 * Get comprehensive pattern analysis
 */
function getPatternAnalysis() {
  return {
    userRepetitions: analyzeUserCommands(7),
    recurringFailures: detectRecurringFailures(),
    successPatterns: detectSuccessPatterns(),
    automationCandidates: getAutomationCandidatesForApproval()
  };
}

/**
 * Run pattern detection and update database
 */
function runPatternDetection() {
  console.log('🔍 Running pattern detection...');

  const analysis = getPatternAnalysis();

  // Create automation candidates for user repetitions
  let candidatesCreated = 0;
  for (const repetition of analysis.userRepetitions) {
    createAutomationCandidate(repetition);
    candidatesCreated++;
  }

  console.log(`✅ Pattern detection complete:`);
  console.log(`   - User repetitions: ${analysis.userRepetitions.length}`);
  console.log(`   - Recurring failures: ${analysis.recurringFailures.length}`);
  console.log(`   - Success patterns: ${analysis.successPatterns.length}`);
  console.log(`   - Automation candidates created: ${candidatesCreated}`);

  return analysis;
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  // Command analysis
  normalizeCommandIntent,
  analyzeUserCommands,
  createAutomationCandidate,
  getAutomationCandidatesForApproval,
  approveAutomationCandidate,

  // Failure detection
  detectRecurringFailures,
  detectSuccessPatterns,

  // Summary
  getPatternAnalysis,
  runPatternDetection
};
