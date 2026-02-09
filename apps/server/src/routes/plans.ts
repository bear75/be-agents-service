/**
 * Plans & Setup API Routes
 *
 * Serves PRD documents from docs/ and reports setup readiness status.
 * These are service-level (not per-repo) since PRDs live in the agent service.
 */

import { Router, Request, Response } from 'express';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { readPlans, readPlan, checkSetupStatus } from '../lib/plans-reader.js';

const router = Router();

/**
 * GET /api/plans/setup-status
 * Check workspace, OpenClaw, Telegram, and LaunchD readiness
 * NOTE: Must be before /:slug to avoid matching "setup-status" as a slug
 */
router.get('/setup-status', (req: Request, res: Response) => {
  try {
    const serviceRoot = getServiceRoot();
    const repoName = (req.query.repo as string) || 'beta-appcaire';
    const config = getRepoConfig(repoName);
    const workspacePath = config?.workspace?.enabled ? config.workspace.path : undefined;

    const status = checkSetupStatus(serviceRoot, workspacePath);

    res.json({
      success: true,
      data: status,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to check setup status',
    });
  }
});

/**
 * GET /api/plans
 * List all PRD/plan documents
 */
router.get('/', (req: Request, res: Response) => {
  try {
    const serviceRoot = getServiceRoot();
    const plans = readPlans(serviceRoot);

    res.json({
      success: true,
      data: plans.map((p) => ({
        slug: p.slug,
        filename: p.filename,
        title: p.title,
        priority: p.priority,
        status: p.status,
        summary: p.summary,
        limitations: p.limitations,
        lastModified: p.lastModified,
      })),
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read plans',
    });
  }
});

/**
 * GET /api/plans/:slug
 * Get a single plan document with full content
 */
router.get('/:slug', (req: Request, res: Response) => {
  try {
    const { slug } = req.params;
    const serviceRoot = getServiceRoot();
    const plan = readPlan(serviceRoot, slug);

    if (!plan) {
      res.status(404).json({
        success: false,
        error: `Plan not found: ${slug}`,
      });
      return;
    }

    res.json({
      success: true,
      data: plan,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read plan',
    });
  }
});

export default router;
