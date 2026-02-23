#!/usr/bin/env node
/**
 * Repository Manager - Multi-Repo Orchestration
 * Manages all eirtech.ai and caire repositories
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const db = require('./database');

// ============================================
// REPOSITORY REGISTRY
// ============================================

const REPOSITORIES = [
  {
    id: 'beta-appcaire',
    name: 'AppCaire Beta',
    path: '/Users/be-agent-service/HomeCare/beta-appcaire',
    github_url: 'https://github.com/eirtech-ai/beta-appcaire',
    team_id: 'team-engineering',
    description: 'Main AppCaire application'
  },
  {
    id: 'be-agent-service',
    name: 'Agent Service',
    path: '/Users/be-agent-service/HomeCare/be-agents-service',
    github_url: 'https://github.com/eirtech-ai/be-agent-service',
    team_id: 'team-engineering',
    description: 'Multi-agent orchestration system'
  },
  {
    id: 'caire-landing',
    name: 'Caire Landing Page',
    path: '/Users/be-agent-service/HomeCare/caire-landing',
    github_url: 'https://github.com/caire/landing',
    team_id: 'team-marketing',
    description: 'Marketing landing page'
  },
  {
    id: 'caire-blog',
    name: 'Caire Blog',
    path: '/Users/be-agent-service/HomeCare/caire-blog',
    github_url: 'https://github.com/caire/blog',
    team_id: 'team-marketing',
    description: 'Content marketing blog'
  }
  // Add more repositories as needed
];

/**
 * Initialize repositories in database
 */
function initializeRepositories() {
  for (const repo of REPOSITORIES) {
    // Check if repo already exists
    const existing = db.db.prepare(
      'SELECT id FROM repositories WHERE id = ?'
    ).get(repo.id);

    if (existing) {
      // Update existing
      db.db.prepare(`
        UPDATE repositories
        SET name = ?, path = ?, github_url = ?, team_id = ?
        WHERE id = ?
      `).run(repo.name, repo.path, repo.github_url, repo.team_id, repo.id);
    } else {
      // Insert new
      db.db.prepare(`
        INSERT INTO repositories (id, name, path, github_url, team_id, is_active)
        VALUES (?, ?, ?, ?, ?, TRUE)
      `).run(repo.id, repo.name, repo.path, repo.github_url, repo.team_id);
    }
  }

  console.log(`✅ Initialized ${REPOSITORIES.length} repositories`);
}

/**
 * Get all active repositories
 */
function getActiveRepositories() {
  return db.db.prepare(`
    SELECT r.*, t.name as team_name
    FROM repositories r
    JOIN teams t ON r.team_id = t.id
    WHERE r.is_active = TRUE
    ORDER BY r.name
  `).all();
}

/**
 * Get repositories by team
 */
function getRepositoriesByTeam(teamId) {
  return db.db.prepare(`
    SELECT * FROM repositories
    WHERE team_id = ? AND is_active = TRUE
    ORDER BY name
  `).all(teamId);
}

/**
 * Get repository by ID
 */
function getRepository(repoId) {
  return db.db.prepare('SELECT * FROM repositories WHERE id = ?').get(repoId);
}

/**
 * Check if repository exists and is accessible
 */
function verifyRepository(repoId) {
  const repo = getRepository(repoId);

  if (!repo) {
    return { valid: false, error: 'Repository not found in registry' };
  }

  if (!fs.existsSync(repo.path)) {
    return { valid: false, error: `Path does not exist: ${repo.path}` };
  }

  // Check if it's a git repository
  const gitDir = path.join(repo.path, '.git');
  if (!fs.existsSync(gitDir)) {
    return { valid: false, error: 'Not a git repository' };
  }

  return { valid: true, repo };
}

/**
 * Get repository status (git status, branch, etc.)
 */
function getRepositoryStatus(repoId) {
  const verification = verifyRepository(repoId);

  if (!verification.valid) {
    return verification;
  }

  const repo = verification.repo;

  try {
    // Get current branch
    const branch = execSync('git rev-parse --abbrev-ref HEAD', {
      cwd: repo.path,
      encoding: 'utf8'
    }).trim();

    // Get remote URL
    let remoteUrl = '';
    try {
      remoteUrl = execSync('git config --get remote.origin.url', {
        cwd: repo.path,
        encoding: 'utf8'
      }).trim();
    } catch (e) {
      remoteUrl = 'No remote configured';
    }

    // Get status summary
    const statusOutput = execSync('git status --porcelain', {
      cwd: repo.path,
      encoding: 'utf8'
    });

    const isDirty = statusOutput.length > 0;
    const modifiedFiles = statusOutput.split('\n').filter(l => l.trim()).length;

    // Get last commit
    const lastCommit = execSync('git log -1 --format="%h - %s (%ar)"', {
      cwd: repo.path,
      encoding: 'utf8'
    }).trim();

    return {
      valid: true,
      repo,
      git: {
        branch,
        remoteUrl,
        isDirty,
        modifiedFiles,
        lastCommit
      }
    };
  } catch (error) {
    return {
      valid: false,
      error: `Git error: ${error.message}`
    };
  }
}

/**
 * Sync repository (git pull)
 */
function syncRepository(repoId) {
  const verification = verifyRepository(repoId);

  if (!verification.valid) {
    return verification;
  }

  const repo = verification.repo;

  try {
    // Stash local changes if any
    const status = execSync('git status --porcelain', {
      cwd: repo.path,
      encoding: 'utf8'
    });

    let stashed = false;
    if (status.length > 0) {
      execSync('git stash', { cwd: repo.path });
      stashed = true;
    }

    // Pull latest changes
    const pullOutput = execSync('git pull --rebase', {
      cwd: repo.path,
      encoding: 'utf8'
    });

    // Pop stash if we stashed
    if (stashed) {
      execSync('git stash pop', { cwd: repo.path });
    }

    // Update last synced timestamp
    db.db.prepare(
      'UPDATE repositories SET last_synced_at = CURRENT_TIMESTAMP WHERE id = ?'
    ).run(repoId);

    return {
      success: true,
      message: pullOutput.trim(),
      stashed
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Get multi-repo orchestration targets
 * @param {Object} criteria - Selection criteria
 * @returns {Array} List of repositories to target
 */
function getOrchestrationTargets(criteria = {}) {
  const { teamId, tags, excludeIds = [] } = criteria;

  let query = 'SELECT * FROM repositories WHERE is_active = TRUE';
  const params = [];

  if (teamId) {
    query += ' AND team_id = ?';
    params.push(teamId);
  }

  if (excludeIds.length > 0) {
    query += ` AND id NOT IN (${excludeIds.map(() => '?').join(',')})`;
    params.push(...excludeIds);
  }

  query += ' ORDER BY name';

  return db.db.prepare(query).all(...params);
}

/**
 * Create multi-repo orchestration plan
 * @param {string} taskDescription - Task description
 * @param {Object} criteria - Repository selection criteria
 * @returns {Object} Orchestration plan
 */
function createOrchestrationPlan(taskDescription, criteria = {}) {
  const targets = getOrchestrationTargets(criteria);

  const plan = {
    taskDescription,
    repositories: targets.map(repo => ({
      id: repo.id,
      name: repo.name,
      path: repo.path,
      team: repo.team_id
    })),
    totalRepos: targets.length,
    estimatedDuration: `${targets.length * 15}m`, // Rough estimate
    parallelizable: true
  };

  return plan;
}

/**
 * Get repository statistics
 */
function getRepositoryStats() {
  const stats = db.db.prepare(`
    SELECT
      r.id,
      r.name,
      r.team_id,
      COUNT(DISTINCT s.id) as session_count,
      MAX(s.started_at) as last_session,
      SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) as completed_sessions
    FROM repositories r
    LEFT JOIN sessions s ON r.path = s.target_repo
    WHERE r.is_active = TRUE
    GROUP BY r.id
    ORDER BY session_count DESC
  `).all();

  return stats.map(s => ({
    repository: s.name,
    teamId: s.team_id,
    totalSessions: s.session_count,
    completedSessions: s.completed_sessions,
    lastSession: s.last_session || 'Never',
    successRate: s.session_count > 0
      ? `${((s.completed_sessions / s.session_count) * 100).toFixed(1)}%`
      : 'N/A'
  }));
}

// ============================================
// EXPORTS
// ============================================

module.exports = {
  REPOSITORIES,
  initializeRepositories,
  getActiveRepositories,
  getRepositoriesByTeam,
  getRepository,
  verifyRepository,
  getRepositoryStatus,
  syncRepository,
  getOrchestrationTargets,
  createOrchestrationPlan,
  getRepositoryStats
};
