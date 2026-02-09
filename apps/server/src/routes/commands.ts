/**
 * Commands & Automation API routes
 * User command tracking and automation candidate detection.
 */

import { Router } from 'express';
import {
  trackUserCommand,
  getAutomationCandidates,
  getUserCommandPatterns,
} from '../lib/database.js';

const router = Router();

/**
 * POST /api/commands
 * Track a user command for pattern detection
 */
router.post('/', (req, res) => {
  try {
    const { commandText, normalizedIntent, team, model, priorityFile, branchName } = req.body;
    if (!commandText) {
      return res.status(400).json({
        success: false,
        error: 'commandText is required',
      });
    }
    trackUserCommand({ commandText, normalizedIntent, team, model, priorityFile, branchName });
    res.status(201).json({ success: true });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/commands/patterns
 * Get detected command patterns (3+ repetitions in 7 days)
 */
router.get('/patterns', (_req, res) => {
  try {
    const patterns = getUserCommandPatterns();
    res.json({ success: true, data: patterns });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/commands/automation
 * Get automation candidates (repetitive tasks ready for automation)
 */
router.get('/automation', (_req, res) => {
  try {
    const candidates = getAutomationCandidates();
    res.json({ success: true, data: candidates });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
