import { Router } from 'express';
import { gamification } from '../lib/services.js';

const router = Router();

router.get('/agent/:agentId', (req, res) => {
  try {
    const { agentId } = req.params;
    const summary = gamification.getAgentGamification(agentId);
    res.json(summary);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/leaderboard', (req, res) => {
  try {
    const metric = (req.query.metric as string) || 'xp';
    const limit = parseInt((req.query.limit as string) || '20');
    const leaderboard = gamification.getLeaderboard(metric, limit);
    res.json(leaderboard);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/achievements/:agentId', (req, res) => {
  try {
    const { agentId } = req.params;
    const achievements = gamification.getAllAchievements(agentId);
    res.json(achievements);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/award-xp', (req, res) => {
  try {
    const { agentId, amount, reason } = req.body;

    if (!agentId || !amount || !reason) {
      return res.status(400).json({
        error: 'Missing required fields: agentId, amount, reason',
      });
    }

    const result = gamification.awardXP(agentId, amount, reason, 'manual', null);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
