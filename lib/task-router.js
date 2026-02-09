#!/usr/bin/env node
/**
 * Task Router - Intelligent Task Assignment
 * Uses Opus 4.6 "brain" to analyze complexity and route tasks appropriately
 */

const db = require('./database');

// ============================================
// TASK COMPLEXITY ANALYSIS
// ============================================

/**
 * Analyze task complexity based on description
 * @param {string} description - Task description
 * @returns {Object} Complexity analysis
 */
function analyzeComplexity(description) {
  const lower = description.toLowerCase();

  // Keyword-based complexity detection (can be enhanced with LLM later)
  const complexityIndicators = {
    architecture: ['architecture', 'system design', 'refactor entire', 'redesign'],
    high: ['security', 'authentication', 'authorization', 'database migration', 'breaking change'],
    medium: ['implement', 'feature', 'integration', 'api', 'component'],
    simple: ['fix typo', 'update docs', 'add comment', 'format code', 'rename variable']
  };

  let complexity = 'medium'; // Default
  let reasoning = [];

  // Check for architecture-level tasks
  for (const keyword of complexityIndicators.architecture) {
    if (lower.includes(keyword)) {
      complexity = 'architecture';
      reasoning.push(`Contains architecture keyword: "${keyword}"`);
      break;
    }
  }

  // Check for high complexity
  if (complexity === 'medium') {
    for (const keyword of complexityIndicators.high) {
      if (lower.includes(keyword)) {
        complexity = 'high';
        reasoning.push(`Contains high-complexity keyword: "${keyword}"`);
        break;
      }
    }
  }

  // Check for simple tasks
  if (complexity === 'medium') {
    for (const keyword of complexityIndicators.simple) {
      if (lower.includes(keyword)) {
        complexity = 'simple';
        reasoning.push(`Contains simple-task keyword: "${keyword}"`);
        break;
      }
    }
  }

  // Token requirements estimation
  let tokenRequirements = 'medium';
  const wordCount = description.split(/\s+/).length;

  if (wordCount < 20) {
    tokenRequirements = 'low';
  } else if (wordCount > 100) {
    tokenRequirements = 'high';
  }

  // Creativity requirements
  const creativityKeywords = ['design', 'innovative', 'creative', 'blog', 'content', 'landing page'];
  const needsCreativity = creativityKeywords.some(kw => lower.includes(kw));

  return {
    complexity,
    tokenRequirements,
    needsCreativity,
    reasoning: reasoning.length > 0 ? reasoning : ['Default medium complexity']
  };
}

/**
 * Determine team assignment based on task description
 * @param {string} description - Task description
 * @returns {string} Team ID
 */
function determineTeam(description) {
  const lower = description.toLowerCase();

  // Marketing keywords
  const marketingKeywords = [
    'blog', 'content', 'seo', 'email', 'campaign', 'social media',
    'landing page', 'marketing', 'lead', 'conversion', 'analytics',
    'copywriting', 'branding', 'design', 'notion'
  ];

  // Engineering keywords
  const engineeringKeywords = [
    'api', 'database', 'backend', 'frontend', 'infrastructure',
    'deploy', 'ci/cd', 'test', 'bug', 'feature', 'refactor',
    'authentication', 'authorization', 'graphql', 'react'
  ];

  const marketingScore = marketingKeywords.filter(kw => lower.includes(kw)).length;
  const engineeringScore = engineeringKeywords.filter(kw => lower.includes(kw)).length;

  if (marketingScore > engineeringScore) {
    return 'team-marketing';
  } else {
    return 'team-engineering'; // Default to engineering
  }
}

/**
 * Select best agent for task within a team
 * @param {string} teamId - Team ID
 * @param {string} description - Task description
 * @returns {Object} Selected agent
 */
function selectAgent(teamId, description) {
  const agents = db.getAgentsByTeam(teamId);
  const lower = description.toLowerCase();

  // Agent specialty keywords
  const specialties = {
    'Backend': ['database', 'api', 'graphql', 'resolver', 'schema', 'migration'],
    'Frontend': ['react', 'ui', 'component', 'interface', 'apollo', 'client'],
    'Infrastructure': ['deploy', 'ci/cd', 'docker', 'kubernetes', 'devops', 'cloud'],
    'Verification': ['test', 'qa', 'verify', 'validation'],
    'Senior Reviewer': ['review', 'architecture', 'security', 'compliance'],

    // Marketing agents
    'Vision': ['seo', 'search', 'ranking', 'keywords', 'analytics'],
    'Loki': ['blog', 'content', 'article', 'writing', 'copywriting'],
    'Pepper': ['email', 'newsletter', 'drip', 'automation'],
    'Quill': ['social', 'twitter', 'linkedin', 'facebook', 'instagram'],
    'Wanda': ['design', 'visual', 'graphics', 'branding'],
    'Wong': ['notion', 'documentation', 'knowledge base'],
    'Shuri': ['product', 'feature', 'launch', 'positioning'],
    'Fury': ['research', 'market', 'competitor', 'analysis']
  };

  // Score each agent based on specialty match
  let bestAgent = agents[0]; // Default to first agent
  let bestScore = 0;

  for (const agent of agents) {
    const agentKeywords = specialties[agent.name] || [];
    const score = agentKeywords.filter(kw => lower.includes(kw)).length;

    if (score > bestScore) {
      bestScore = score;
      bestAgent = agent;
    }
  }

  return bestAgent;
}

/**
 * Route task to appropriate team and agent
 * @param {Object} taskSpec - Task specification
 * @returns {Object} Routing decision
 */
function routeTask(taskSpec) {
  const { description, priorityFile = '' } = taskSpec;

  // Analyze complexity
  const complexityAnalysis = analyzeComplexity(description);

  // Determine team
  const teamId = determineTeam(description + ' ' + priorityFile);

  // Select agent
  const agent = selectAgent(teamId, description);

  // Determine criticality
  const critical = complexityAnalysis.complexity === 'architecture' ||
                   description.toLowerCase().includes('critical') ||
                   description.toLowerCase().includes('security');

  return {
    teamId,
    agentId: agent.id,
    agentName: agent.name,
    complexity: complexityAnalysis.complexity,
    tokenRequirements: complexityAnalysis.tokenRequirements,
    needsCreativity: complexityAnalysis.needsCreativity,
    critical,
    reasoning: [
      ...complexityAnalysis.reasoning,
      `Assigned to ${agent.name} (${agent.role}) on ${teamId === 'team-engineering' ? 'Engineering' : 'Marketing'} team`
    ]
  };
}

/**
 * Analyze priority file and extract tasks
 * @param {string} priorityFilePath - Path to priority file
 * @returns {Array} List of tasks with routing
 */
function analyzePriorityFile(priorityFilePath) {
  const fs = require('fs');
  const path = require('path');

  if (!fs.existsSync(priorityFilePath)) {
    throw new Error(`Priority file not found: ${priorityFilePath}`);
  }

  const content = fs.readFileSync(priorityFilePath, 'utf8');

  // Parse markdown checkboxes and headings as tasks
  const tasks = [];
  const lines = content.split('\n');

  let currentSection = 'General';

  for (const line of lines) {
    // Detect headings
    if (line.startsWith('#')) {
      currentSection = line.replace(/^#+\s*/, '').trim();
      continue;
    }

    // Detect tasks (checkboxes)
    const taskMatch = line.match(/^[-*]\s*\[[ x]\]\s*(.+)$/);
    if (taskMatch) {
      const description = taskMatch[1].trim();
      const routing = routeTask({
        description,
        priorityFile: path.basename(priorityFilePath)
      });

      tasks.push({
        description,
        section: currentSection,
        ...routing
      });
    }
  }

  return tasks;
}

/**
 * Get routing statistics
 */
function getRoutingStats() {
  const sessions = db.getRecentSessions(50);
  const tasks = [];

  for (const session of sessions) {
    const sessionTasks = db.getSessionTasks(session.id);
    tasks.push(...sessionTasks);
  }

  const byTeam = {};
  const byAgent = {};
  const byComplexity = {};

  for (const task of tasks) {
    // Count by agent
    if (!byAgent[task.agent_name]) {
      byAgent[task.agent_name] = { total: 0, completed: 0, failed: 0 };
    }
    byAgent[task.agent_name].total++;
    if (task.status === 'completed') byAgent[task.agent_name].completed++;
    if (task.status === 'failed') byAgent[task.agent_name].failed++;
  }

  return {
    totalTasks: tasks.length,
    byAgent,
    summary: {
      mostUtilized: Object.entries(byAgent)
        .sort((a, b) => b[1].total - a[1].total)
        .slice(0, 5)
        .map(([name, stats]) => ({ name, ...stats }))
    }
  };
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  analyzeComplexity,
  determineTeam,
  selectAgent,
  routeTask,
  analyzePriorityFile,
  getRoutingStats
};
