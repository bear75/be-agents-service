/**
 * Schedule optimization API — pipeline of Timefold FSR runs
 * GET /api/schedule-runs — list runs (optional ?dataset=)
 * POST /api/schedule-runs/:id/cancel — cancel run (Timefold DELETE + DB update)
 */
import { Router, type Request, type Response } from 'express';
import {
  getAllScheduleRuns,
  getScheduleRunById,
  cancelScheduleRun,
} from '../lib/database.js';

const router = Router();

router.get('/', (req: Request, res: Response) => {
  try {
    const dataset = req.query.dataset as string | undefined;
    const runs = getAllScheduleRuns(dataset);
    res.json({
      success: true,
      data: { runs },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch schedule runs',
    });
  }
});

router.post('/:id/cancel', (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const reason = (req.body?.reason as string) || 'Cancelled by user';
    const existing = getScheduleRunById(id);
    if (!existing) {
      return res.status(404).json({ success: false, error: 'Run not found' });
    }
    if (existing.status !== 'running' && existing.status !== 'queued') {
      return res.status(400).json({
        success: false,
        error: `Run is ${existing.status}; only running or queued can be cancelled`,
      });
    }
    const updated = cancelScheduleRun(id, reason);
    res.json({ success: true, data: updated });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to cancel run',
    });
  }
});

export default router;
