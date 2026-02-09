import { Router } from 'express';
import { db } from '../lib/services.js';

const router = Router();

router.get('/', (req, res) => {
  try {
    const recentSessions = db.getRecentSessions(100);
    const allTasks = db.getAllTasks();
    const allAgents = db.getAllAgents();

    res.json({
      totalSessions: recentSessions.length,
      activeSessions: recentSessions.filter((s: { status: string }) => s.status === 'in_progress').length,
      completedSessions: recentSessions.filter((s: { status: string }) => s.status === 'completed').length,
      failedSessions: recentSessions.filter((s: { status: string }) => s.status === 'failed').length,
      totalTasks: allTasks.length,
      completedTasks: allTasks.filter((t: { status: string }) => t.status === 'completed').length,
      failedTasks: allTasks.filter((t: { status: string }) => t.status === 'failed').length,
      inProgressTasks: allTasks.filter((t: { status: string }) => t.status === 'in_progress').length,
      totalAgents: allAgents.length,
      activeAgents: allAgents.filter((a: { is_active: boolean }) => a.is_active).length,
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
