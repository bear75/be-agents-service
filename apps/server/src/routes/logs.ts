import { Router } from 'express';
import { getSessionLogs } from '../lib/services.js';

const router = Router();

router.get('/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  const logs = getSessionLogs(sessionId);
  res.json(logs);
});

export default router;
