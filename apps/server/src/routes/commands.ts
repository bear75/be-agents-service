import { Router } from 'express';
import { db } from '../lib/services.js';

const router = Router();

router.post('/', (req, res) => {
  try {
    const { text, normalizedIntent, team, model, priorityFile, branchName } = req.body;

    db.trackUserCommand({
      commandText: text || '',
      normalizedIntent: normalizedIntent || '',
      team: team || null,
      model: model || null,
      priorityFile: priorityFile || null,
      branchName: branchName || null,
    });
    console.log('✅ User command recorded in database');

    res.json({ success: true });
  } catch (error) {
    console.error('⚠️  Failed to record command:', (error as Error).message);
    res.json({ success: true });
  }
});

export default router;
