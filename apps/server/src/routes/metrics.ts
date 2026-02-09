/**
 * Metrics & Experiments API routes
 * RL metrics, patterns, experiments, rewards, and dashboard stats.
 */

import { Router } from 'express';
import {
  recordMetric,
  getMetrics,
  issueReward,
  getEntityRewards,
  recordPattern,
  getPatterns,
  createExperiment,
  getExperiment,
  getActiveExperiments,
  getDashboardStats,
  getLessonsLearned,
  getAllTasks,
} from '../lib/database.js';

const router = Router();

// ─── Dashboard Stats ──────────────────────────────────────────────────────────

/**
 * GET /api/metrics/stats
 * Get high-level dashboard statistics
 */
router.get('/stats', (_req, res) => {
  try {
    const stats = getDashboardStats();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Metrics ──────────────────────────────────────────────────────────────────

/**
 * POST /api/metrics
 * Record a new metric
 */
router.post('/', (req, res) => {
  try {
    const { entityType, entityId, metricName, metricValue, context } = req.body;
    if (!entityType || !entityId || !metricName || metricValue === undefined) {
      return res.status(400).json({
        success: false,
        error: 'entityType, entityId, metricName, and metricValue are required',
      });
    }
    recordMetric({ entityType, entityId, metricName, metricValue, context });
    res.status(201).json({ success: true });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/metrics/:entityType/:entityId
 * Get metrics for a specific entity
 */
router.get('/:entityType/:entityId', (req, res) => {
  try {
    const { entityType, entityId } = req.params;
    const metricName = req.query.metric as string | undefined;
    const metrics = getMetrics(entityType, entityId, metricName);
    res.json({ success: true, data: metrics });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Rewards ──────────────────────────────────────────────────────────────────

/**
 * POST /api/metrics/rewards
 * Issue a reward signal
 */
router.post('/rewards', (req, res) => {
  try {
    const { entityType, entityId, rewardValue, reason } = req.body;
    if (!entityType || !entityId || rewardValue === undefined || !reason) {
      return res.status(400).json({
        success: false,
        error: 'entityType, entityId, rewardValue, and reason are required',
      });
    }
    const reward = issueReward({ entityType, entityId, rewardValue, reason });
    res.status(201).json({ success: true, data: reward });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/metrics/rewards/:entityType/:entityId
 * Get reward summary for an entity
 */
router.get('/rewards/:entityType/:entityId', (req, res) => {
  try {
    const { entityType, entityId } = req.params;
    const rewards = getEntityRewards(entityType, entityId);
    res.json({ success: true, data: rewards });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Patterns ─────────────────────────────────────────────────────────────────

/**
 * POST /api/metrics/patterns
 * Record a detected pattern
 */
router.post('/patterns', (req, res) => {
  try {
    const { patternId, patternType, description, confidenceScore } = req.body;
    if (!patternId || !patternType || !description) {
      return res.status(400).json({
        success: false,
        error: 'patternId, patternType, and description are required',
      });
    }
    recordPattern({ patternId, patternType, description, confidenceScore });
    res.status(201).json({ success: true });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/metrics/patterns
 * Get patterns, optionally filtered by type
 */
router.get('/patterns', (req, res) => {
  try {
    const patternType = req.query.type as string | undefined;
    const status = (req.query.status as string) || 'active';
    const patterns = getPatterns(patternType, status);
    res.json({ success: true, data: patterns });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Experiments ──────────────────────────────────────────────────────────────

/**
 * POST /api/metrics/experiments
 * Create a new experiment
 */
router.post('/experiments', (req, res) => {
  try {
    const { experimentId, name, description, successMetric, targetValue } = req.body;
    if (!experimentId || !name || !successMetric) {
      return res.status(400).json({
        success: false,
        error: 'experimentId, name, and successMetric are required',
      });
    }
    const experiment = createExperiment({ experimentId, name, description, successMetric, targetValue });
    res.status(201).json({ success: true, data: experiment });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/metrics/experiments/active
 * Get active experiments
 */
router.get('/experiments/active', (_req, res) => {
  try {
    const experiments = getActiveExperiments();
    res.json({ success: true, data: experiments });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/metrics/experiments/:id
 * Get experiment by ID
 */
router.get('/experiments/:id', (req, res) => {
  try {
    const experiment = getExperiment(req.params.id);
    if (!experiment) {
      return res.status(404).json({ success: false, error: 'Experiment not found' });
    }
    res.json({ success: true, data: experiment });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Lessons Learned ──────────────────────────────────────────────────────────

/**
 * GET /api/metrics/lessons
 * Get recent lessons learned
 */
router.get('/lessons', (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 20;
    const lessons = getLessonsLearned(limit);
    res.json({ success: true, data: lessons });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Tasks (all) ──────────────────────────────────────────────────────────────

/**
 * GET /api/metrics/tasks
 * Get all tasks with agent and team info (for Kanban board)
 */
router.get('/tasks', (_req, res) => {
  try {
    const tasks = getAllTasks();
    res.json({ success: true, data: tasks });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
