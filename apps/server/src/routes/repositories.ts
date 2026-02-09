import { Router } from 'express';
import { repositoryManager } from '../lib/services.js';

const router = Router();

router.get('/', (req, res) => {
  try {
    const repos = repositoryManager.getActiveRepositories();
    res.json(repos);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/:id/status', (req, res) => {
  try {
    const { id } = req.params;
    const status = repositoryManager.getRepositoryStatus(id);
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
