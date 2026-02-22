#!/usr/bin/env node
/**
 * LLM Router - Intelligent Model Selection
 * Opus 4.6 "brain" analyzes tasks and delegates to appropriate models
 *
 * Strategy:
 * - Opus 4.6: Architecture decisions, security, RL analysis, complex problems
 * - Sonnet: Feature implementation, bug fixes, most specialist work (default)
 * - Haiku: Quick queries, simple tasks, fast responses
 * - pi-mono: Token-heavy simple tasks (free local model)
 */

const db = require('./database');
const taskRouter = require('./task-router');

// ============================================
// MODEL PRICING (per 1M tokens)
// ============================================

const MODEL_PRICING = {
  'opus-4.6': { input: 15.00, output: 75.00 },
  'opus': { input: 15.00, output: 75.00 },
  'sonnet': { input: 3.00, output: 15.00 },
  'haiku': { input: 0.25, output: 1.25 },
  'pi': { input: 0.00, output: 0.00 } // Free local model
};

// ============================================
// LLM SELECTION LOGIC
// ============================================

/**
 * Select appropriate LLM for task
 * @param {Object} taskSpec - Task specification
 * @returns {Object} LLM routing decision
 */
function selectLLM(taskSpec) {
  const {
    complexity,
    tokenRequirements,
    needsCreativity,
    critical,
    description
  } = taskSpec;

  let brain = 'opus-4.6'; // Always use Opus 4.6 for initial analysis
  let execution = 'sonnet'; // Default execution model
  let reason = '';

  // OPUS 4.6 EXECUTION: Critical or architecture-level tasks
  if (critical || complexity === 'architecture') {
    execution = 'opus-4.6';
    reason = 'Critical decision or architecture-level task - requires Opus 4.6';
  }
  // PI-MONO: Token-heavy simple tasks (free local)
  else if (tokenRequirements === 'high' && complexity === 'simple') {
    execution = 'pi';
    reason = 'Token-heavy simple task - use free local pi-mono model';
  }
  // HAIKU: Simple, fast tasks
  else if (complexity === 'simple' && !needsCreativity) {
    execution = 'haiku';
    reason = 'Simple task - use fast and cheap Haiku';
  }
  // OPUS 4.6: Creative or complex tasks
  else if (needsCreativity || complexity === 'high') {
    execution = 'opus-4.6';
    reason = needsCreativity
      ? 'Creative task requires Opus 4.6 quality'
      : 'High complexity requires Opus 4.6';
  }
  // SONNET: Default for medium complexity
  else {
    execution = 'sonnet';
    reason = 'Medium complexity - Sonnet provides good balance of cost and quality';
  }

  return {
    brain,
    execution,
    reason,
    costSensitive: execution !== 'opus-4.6',
    estimatedCost: estimateCost(execution, tokenRequirements)
  };
}

/**
 * Estimate cost for task
 * @param {string} model - Model name
 * @param {string} tokenRequirements - low/medium/high
 * @returns {number} Estimated cost in USD
 */
function estimateCost(model, tokenRequirements) {
  const pricing = MODEL_PRICING[model] || MODEL_PRICING['sonnet'];

  // Rough token estimates
  const tokenEstimates = {
    low: { input: 1000, output: 500 },
    medium: { input: 5000, output: 2000 },
    high: { input: 20000, output: 10000 }
  };

  const tokens = tokenEstimates[tokenRequirements] || tokenEstimates['medium'];

  const inputCost = (tokens.input / 1000000) * pricing.input;
  const outputCost = (tokens.output / 1000000) * pricing.output;

  return +(inputCost + outputCost).toFixed(4);
}

/**
 * Route task with full complexity analysis and LLM selection
 * @param {Object} taskSpec - Task specification
 * @returns {Object} Complete routing decision
 */
function routeTaskWithLLM(taskSpec) {
  // Step 1: Analyze task complexity and assign team/agent
  const taskRouting = taskRouter.routeTask(taskSpec);

  // Step 2: Select appropriate LLM
  const llmDecision = selectLLM({
    ...taskSpec,
    ...taskRouting
  });

  return {
    ...taskRouting,
    llm: llmDecision,
    fullReasoning: [
      ...taskRouting.reasoning,
      `LLM Selection: ${llmDecision.execution} (${llmDecision.reason})`,
      `Estimated cost: $${llmDecision.estimatedCost}`
    ]
  };
}

/**
 * Get agent's preferred LLM or default
 * @param {string} agentId - Agent ID
 * @returns {string} Model name
 */
function getAgentPreference(agentId) {
  const agent = db.db.prepare('SELECT llm_preference FROM agents WHERE id = ?').get(agentId);
  return agent?.llm_preference || 'sonnet';
}

/**
 * Override LLM selection with agent preference
 * @param {Object} routing - Routing decision
 * @param {boolean} respectPreference - Whether to respect agent's preference
 * @returns {Object} Updated routing
 */
function applyAgentPreference(routing, respectPreference = true) {
  if (!respectPreference) {
    return routing;
  }

  const agentPreference = getAgentPreference(routing.agentId);

  // Only override if preference is stronger than current selection
  const modelStrength = {
    'opus-4.6': 4,
    'opus': 4,
    'sonnet': 3,
    'haiku': 2,
    'pi': 1
  };

  const currentStrength = modelStrength[routing.llm.execution] || 3;
  const preferredStrength = modelStrength[agentPreference] || 3;

  if (preferredStrength >= currentStrength) {
    return {
      ...routing,
      llm: {
        ...routing.llm,
        execution: agentPreference,
        reason: `Agent ${routing.agentName} prefers ${agentPreference} - overriding selection`
      }
    };
  }

  return routing;
}

/**
 * Record LLM usage for cost tracking
 * @param {string} taskId - Task ID
 * @param {string} model - Model used
 * @param {number} inputTokens - Input tokens
 * @param {number} outputTokens - Output tokens
 * @param {number} durationMs - Duration in milliseconds
 */
function recordLLMUsage(taskId, model, inputTokens, outputTokens, durationMs) {
  const pricing = MODEL_PRICING[model] || MODEL_PRICING['sonnet'];

  const inputCost = (inputTokens / 1000000) * pricing.input;
  const outputCost = (outputTokens / 1000000) * pricing.output;
  const totalCost = inputCost + outputCost;

  db.db.prepare(`
    INSERT INTO llm_usage (task_id, model, input_tokens, output_tokens, cost_usd, duration_ms)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(taskId, model, inputTokens, outputTokens, totalCost, durationMs);

  return {
    model,
    inputTokens,
    outputTokens,
    cost: totalCost,
    durationMs
  };
}

/**
 * Get LLM usage statistics
 * @param {number} days - Number of days to look back
 * @returns {Object} Usage statistics
 */
function getLLMStats(days = 7) {
  const stats = db.db.prepare(`
    SELECT
      model,
      COUNT(*) as usage_count,
      SUM(input_tokens) as total_input_tokens,
      SUM(output_tokens) as total_output_tokens,
      SUM(cost_usd) as total_cost,
      AVG(duration_ms) as avg_duration_ms
    FROM llm_usage
    WHERE used_at >= datetime('now', '-' || ? || ' days')
    GROUP BY model
    ORDER BY total_cost DESC
  `).all(days);

  const totalCost = stats.reduce((sum, s) => sum + s.total_cost, 0);

  return {
    period: `Last ${days} days`,
    totalCost: totalCost.toFixed(2),
    byModel: stats.map(s => ({
      model: s.model,
      usageCount: s.usage_count,
      totalInputTokens: s.total_input_tokens,
      totalOutputTokens: s.total_output_tokens,
      totalCost: s.total_cost.toFixed(4),
      avgDuration: `${Math.floor(s.avg_duration_ms / 1000)}s`,
      costPercentage: ((s.total_cost / totalCost) * 100).toFixed(1) + '%'
    }))
  };
}

/**
 * Get raw LLM usage records (for dashboard timeline)
 * @param {number} days - Number of days to look back
 * @param {number} limit - Max records to return
 * @returns {Array<{id, task_id, model, input_tokens, output_tokens, cost_usd, duration_ms, used_at}>}
 */
function getLLMUsageRecent(days = 7, limit = 200) {
  const rows = db.db.prepare(`
    SELECT id, task_id, model, input_tokens, output_tokens, cost_usd, duration_ms, used_at
    FROM llm_usage
    WHERE used_at >= datetime('now', '-' || ? || ' days')
    ORDER BY used_at DESC
    LIMIT ?
  `).all(days, limit);

  return rows.map(r => ({
    id: r.id,
    taskId: r.task_id,
    model: r.model,
    inputTokens: r.input_tokens ?? 0,
    outputTokens: r.output_tokens ?? 0,
    costUsd: r.cost_usd ?? 0,
    durationMs: r.duration_ms ?? null,
    usedAt: r.used_at,
  }));
}

/**
 * Get cost breakdown by agent
 */
function getCostByAgent(days = 7) {
  const stats = db.db.prepare(`
    SELECT
      a.name as agent_name,
      l.model,
      COUNT(*) as usage_count,
      SUM(l.cost_usd) as total_cost
    FROM llm_usage l
    JOIN tasks t ON l.task_id = t.id
    JOIN agents a ON t.agent_id = a.id
    WHERE l.used_at >= datetime('now', '-' || ? || ' days')
    GROUP BY a.name, l.model
    ORDER BY total_cost DESC
  `).all(days);

  return stats.map(s => ({
    agent: s.agent_name,
    model: s.model,
    usageCount: s.usage_count,
    totalCost: '$' + s.total_cost.toFixed(4)
  }));
}

/**
 * Optimize LLM selection based on historical performance
 * @param {string} agentId - Agent ID
 * @returns {Object} Optimization recommendations
 */
function optimizeLLMForAgent(agentId) {
  const agent = db.db.prepare('SELECT * FROM agents WHERE id = ?').get(agentId);

  if (!agent) {
    return null;
  }

  // Get tasks by model for this agent
  const performance = db.db.prepare(`
    SELECT
      t.llm_used as model,
      COUNT(*) as total_tasks,
      SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed,
      AVG(t.duration_seconds) as avg_duration,
      SUM(l.cost_usd) as total_cost
    FROM tasks t
    LEFT JOIN llm_usage l ON t.id = l.task_id
    WHERE t.agent_id = ?
      AND t.llm_used IS NOT NULL
      AND t.completed_at >= datetime('now', '-30 days')
    GROUP BY t.llm_used
  `).all(agentId);

  if (performance.length === 0) {
    return {
      agent: agent.name,
      recommendation: 'Insufficient data',
      currentPreference: agent.llm_preference
    };
  }

  // Find best model by success rate and cost
  const analyzed = performance.map(p => {
    const successRate = p.completed / p.total_tasks;
    const costPerTask = p.total_cost / p.total_tasks;

    return {
      model: p.model,
      successRate,
      costPerTask: costPerTask || 0,
      avgDuration: p.avg_duration,
      totalTasks: p.total_tasks,
      score: successRate * 100 - (costPerTask * 10) // Weighted score
    };
  }).sort((a, b) => b.score - a.score);

  const recommended = analyzed[0];

  return {
    agent: agent.name,
    currentPreference: agent.llm_preference,
    recommendation: recommended.model,
    reasoning: `${(recommended.successRate * 100).toFixed(1)}% success rate with $${recommended.costPerTask.toFixed(4)} cost per task`,
    allModels: analyzed
  };
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  selectLLM,
  estimateCost,
  routeTaskWithLLM,
  getAgentPreference,
  applyAgentPreference,
  recordLLMUsage,
  getLLMStats,
  getLLMUsageRecent,
  getCostByAgent,
  optimizeLLMForAgent,
  MODEL_PRICING
};
