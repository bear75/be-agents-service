import { Router } from 'express';
import {
  db,
  learningController,
  patternDetector,
  llmRouter,
} from '../lib/services.js';

const router = Router();

router.get('/experiments', (req, res) => {
  const experiments = db.getActiveExperiments();
  res.json(experiments);
});

router.post('/experiments/evaluate', (req, res) => {
  try {
    const results = learningController.evaluateAllExperiments();
    res.json({ success: true, results });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/patterns', (req, res) => {
  try {
    const analysis = patternDetector.getPatternAnalysis();
    res.json(analysis);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/patterns/detect', (req, res) => {
  try {
    const analysis = patternDetector.runPatternDetection();
    res.json({ success: true, analysis });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/automation-candidates', (req, res) => {
  try {
    const candidates = patternDetector.getAutomationCandidatesForApproval();
    res.json(candidates);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/automation-candidates/:id/approve', (req, res) => {
  try {
    const { id } = req.params;
    const result = patternDetector.approveAutomationCandidate(id);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/automation-candidates/:id/dismiss', (req, res) => {
  try {
    const { id } = req.params;
    db.updateAutomationCandidate(id, {
      approved_by_user: false,
      is_automated: false,
    });
    res.json({ success: true, message: 'Automation candidate dismissed' });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/agent-performance', (req, res) => {
  try {
    const insights = learningController.getAgentInsights();
    res.json(insights);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/llm-stats', (req, res) => {
  try {
    const stats = llmRouter.getLLMStats(7);
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/llm-cost-by-agent', (req, res) => {
  try {
    const costs = llmRouter.getCostByAgent(7);
    res.json(costs);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
