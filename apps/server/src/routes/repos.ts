import { Router } from 'express';
import { getRepoConfig, listRepos } from '../lib/config.js';
import { readPriorities, readLogs, isRepoValid } from '../lib/repo-reader.js';
import type { AgentStatus } from '../types/index.js';

const router = Router();

/**
 * GET /api/repos
 * List all configured repositories
 */
router.get('/', (req, res) => {
  try {
    const repoNames = listRepos();
    const repos = repoNames.map((name) => {
      const config = getRepoConfig(name);
      if (!config) return null;

      return {
        name,
        enabled: config.enabled,
        path: config.path,
        valid: isRepoValid(config),
        schedule: config.schedule,
        github: config.github,
      };
    }).filter(Boolean);

    res.json({
      success: true,
      data: repos,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/repos/:name
 * Get details for a specific repository
 */
router.get('/:name', (req, res) => {
  try {
    const { name } = req.params;
    const config = getRepoConfig(name);

    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Repository '${name}' not found`,
      });
    }

    res.json({
      success: true,
      data: {
        name,
        enabled: config.enabled,
        path: config.path,
        valid: isRepoValid(config),
        schedule: config.schedule,
        github: config.github,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/repos/:name/status
 * Get agent status for a repository
 */
router.get('/:name/status', (req, res) => {
  try {
    const { name } = req.params;
    const config = getRepoConfig(name);

    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Repository '${name}' not found`,
      });
    }

    // TODO: Implement actual status tracking
    // For now, return basic status
    const status: AgentStatus = {
      name,
      enabled: config.enabled,
      running: false, // TODO: Check if actually running
      nextScheduledRun: {
        review: config.schedule.review,
        compound: config.schedule.compound,
      },
    };

    res.json({
      success: true,
      data: status,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/repos/:name/priorities
 * Get priorities from a repository
 */
router.get('/:name/priorities', (req, res) => {
  try {
    const { name } = req.params;
    const config = getRepoConfig(name);

    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Repository '${name}' not found`,
      });
    }

    const priorities = readPriorities(config);

    res.json({
      success: true,
      data: priorities,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/repos/:name/logs
 * Get logs from a repository
 */
router.get('/:name/logs', (req, res) => {
  try {
    const { name } = req.params;
    const limit = parseInt(req.query.limit as string) || 100;
    const config = getRepoConfig(name);

    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Repository '${name}' not found`,
      });
    }

    const logs = readLogs(config, limit);

    res.json({
      success: true,
      data: logs,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
