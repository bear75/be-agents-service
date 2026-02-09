import { Router } from 'express';
import { jobExecutor } from '../lib/services.js';

const router = Router();

router.get('/', (req, res) => {
  const jobs = jobExecutor.getAllJobs();
  res.json(jobs);
});

router.post('/nightly/trigger', (req, res) => {
  const result = jobExecutor.triggerNightlyJob();
  res.status(result.success ? 200 : 500).json(result);
});

router.post('/start', (req, res) => {
  try {
    const { team, model, priorityFile, branchName, baseBranch, targetRepo } = req.body;

    if (!team || !priorityFile || !branchName) {
      return res.status(400).json({
        error: 'Missing required fields: team, priorityFile, branchName',
      });
    }

    let job;
    if (team === 'engineering') {
      job = jobExecutor.startEngineeringJob({
        model,
        priorityFile,
        branchName,
        baseBranch,
        targetRepo,
      });
    } else if (team === 'marketing') {
      job = jobExecutor.startMarketingJob({
        model,
        priorityFile,
        branchName,
        targetRepo,
      });
    } else {
      return res.status(400).json({
        error: 'Invalid team. Must be "engineering" or "marketing"',
      });
    }

    res.json(job);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/:jobId/stop', (req, res) => {
  const { jobId } = req.params;
  const success = jobExecutor.stopJob(jobId);

  if (success) {
    res.json({ success: true, message: 'Job stopped' });
  } else {
    res.status(404).json({ success: false, error: 'Job not found or already stopped' });
  }
});

router.get('/:jobId/status', (req, res) => {
  const { jobId } = req.params;
  const status = jobExecutor.getJobStatus(jobId);

  if (status) {
    res.json(status);
  } else {
    res.status(404).json({ error: 'Job not found' });
  }
});

router.get('/:jobId/logs', (req, res) => {
  const { jobId } = req.params;
  const logs = jobExecutor.getJobLogs(jobId, 200);

  if (logs !== null) {
    res.type('text/plain').send(logs);
  } else {
    res.status(404).json({ error: 'Logs not found' });
  }
});

export default router;
