import { Router } from 'express';
import { db } from '../lib/services.js';

const router = Router();

router.get('/campaigns', (req, res) => {
  try {
    const campaigns = db.getAllCampaigns();
    res.json(campaigns || []);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/leads', (req, res) => {
  try {
    const leads = db.getAllLeads();
    res.json(leads || []);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/content', (req, res) => {
  try {
    const content = db.getAllContent();
    res.json(content || []);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/social', (req, res) => {
  try {
    const socialPosts = db.getContentByType('social');
    res.json(socialPosts || []);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
