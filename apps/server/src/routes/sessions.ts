import { Router } from 'express';
import { db, getSessionLogs } from '../lib/services.js';

const router = Router();

router.get('/', (req, res) => {
  try {
    const sessions = db.getRecentSessions(50);
    res.json(sessions);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    const session = db.getSession(sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }
    const tasks = db.getSessionTasks(sessionId);
    res.json({ ...session, tasks });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
