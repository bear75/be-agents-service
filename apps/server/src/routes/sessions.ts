/**
 * Sessions API routes
 * CRUD operations for orchestrator sessions stored in SQLite.
 */

import { Router } from 'express';
import {
  createSession,
  getSession,
  getRecentSessions,
  getActiveSessions,
  updateSessionStatus,
  getSessionTasks,
} from '../lib/database.js';

const router = Router();

/**
 * GET /api/sessions
 * List recent sessions (default limit 50)
 */
router.get('/', (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const sessions = getRecentSessions(limit);
    res.json({ success: true, data: sessions });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/sessions/active
 * List active/pending sessions (from view)
 */
router.get('/active', (_req, res) => {
  try {
    const sessions = getActiveSessions();
    res.json({ success: true, data: sessions });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/sessions/:id
 * Get a single session with its tasks
 */
router.get('/:id', (req, res) => {
  try {
    const session = getSession(req.params.id);
    if (!session) {
      return res.status(404).json({ success: false, error: 'Session not found' });
    }
    const tasks = getSessionTasks(req.params.id);
    res.json({ success: true, data: { ...session, tasks } });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/sessions
 * Create a new session
 */
router.post('/', (req, res) => {
  try {
    const { sessionId, teamId, targetRepo, priorityFile, branchName } = req.body;
    if (!sessionId || !teamId || !targetRepo) {
      return res.status(400).json({
        success: false,
        error: 'sessionId, teamId, and targetRepo are required',
      });
    }
    const session = createSession({ sessionId, teamId, targetRepo, priorityFile, branchName });
    res.status(201).json({ success: true, data: session });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * PATCH /api/sessions/:id
 * Update session status
 */
router.patch('/:id', (req, res) => {
  try {
    const { status, prUrl, exitCode } = req.body;
    if (!status) {
      return res.status(400).json({ success: false, error: 'status is required' });
    }
    updateSessionStatus(req.params.id, status, prUrl, exitCode);
    const session = getSession(req.params.id);
    res.json({ success: true, data: session });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
