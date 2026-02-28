import { Router } from 'express';
import path from 'path';
import { jobExecutor } from '../lib/services.js';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';

const router = Router();

const DEFAULT_REPO_NAME = 'appcaire';

/** Resolve targetRepo: repo name → config path; else absolute path as-is; else default path. */
function resolveTargetRepoPath(targetRepo: string | undefined): string {
  if (!targetRepo || typeof targetRepo !== 'string') {
    const config = getRepoConfig(DEFAULT_REPO_NAME);
    return config?.path ?? path.join(getServiceRoot(), '..', DEFAULT_REPO_NAME);
  }
  if (path.isAbsolute(targetRepo)) return targetRepo;
  const config = getRepoConfig(targetRepo.trim());
  if (config?.path) return config.path;
  return path.join(getServiceRoot(), '..', targetRepo);
}

router.get('/', (req, res) => {
  try {
    const jobs = jobExecutor.getAllJobs();
    res.json(jobs);
  } catch (err) {
    console.error('GET /jobs error:', err);
    res.json([]);
  }
});

router.post('/nightly/trigger', (req, res) => {
  const result = jobExecutor.triggerNightlyJob();
  res.status(result.success ? 200 : 500).json(result);
});

router.post('/start', (req, res) => {
  try {
    const { team, model, priorityFile, branchName, baseBranch, targetRepo } = req.body;

    if (!team) {
      return res.status(400).json({
        error: 'Missing required field: team',
      });
    }

    const targetRepoPath = resolveTargetRepoPath(targetRepo);

    let job;
    if (team === 'engineering') {
      // Engineering: runs auto-compound.sh (finds priority, creates PRD, runs orchestrator)
      if (!targetRepo) {
        return res.status(400).json({
          error: 'Missing required field: targetRepo for engineering job',
        });
      }
      job = jobExecutor.startEngineeringJob({
        model,
        targetRepo: targetRepo.trim(),
      });
    } else if (team === 'marketing') {
      if (!priorityFile || !branchName) {
        return res.status(400).json({
          error: 'Missing required fields: priorityFile, branchName for marketing job',
        });
      }
      job = jobExecutor.startMarketingJob({
        model,
        priorityFile,
        branchName,
        targetRepo: targetRepoPath,
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
