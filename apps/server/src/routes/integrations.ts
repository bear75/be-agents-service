import { Router } from 'express';
import { db } from '../lib/services.js';

const router = Router();

router.get('/', (req, res) => {
  try {
    const integrations = db.getAllIntegrations();
    res.json(integrations);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/type/:type', (req, res) => {
  try {
    const { type } = req.params;
    const integrations = db.getIntegrationsByType(type);
    res.json(integrations);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.patch('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const integration = db.updateIntegration(id, req.body);
    res.json({ success: true, integration });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
