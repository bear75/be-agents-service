/**
 * Marketing API routes
 * Campaigns, leads, and content management from SQLite.
 */

import { Router } from 'express';
import {
  getAllCampaigns,
  getAllLeads,
  getAllContent,
} from '../lib/database.js';

const router = Router();

/**
 * GET /api/marketing/campaigns
 * List all campaigns with owner info
 */
router.get('/campaigns', (_req, res) => {
  try {
    const campaigns = getAllCampaigns();
    res.json({ success: true, data: campaigns });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/marketing/leads
 * List all leads with assigned agent info
 */
router.get('/leads', (_req, res) => {
  try {
    const leads = getAllLeads();
    res.json({ success: true, data: leads });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/marketing/content
 * List all content pieces with author info
 */
router.get('/content', (_req, res) => {
  try {
    const content = getAllContent();
    res.json({ success: true, data: content });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
