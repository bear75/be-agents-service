/**
 * Teams & Agents API routes
 * CRUD operations for teams and agents stored in SQLite.
 */

import { Router } from 'express';
import {
  getAllTeams,
  getTeamById,
  createTeam,
  getAgentsByTeam,
  getAllAgents,
  getAgentById,
  createAgent,
  updateAgent,
  deactivateAgent,
  reactivateAgent,
  getAgentPerformance,
} from '../lib/database.js';

const router = Router();

// ─── Teams ────────────────────────────────────────────────────────────────────

/**
 * GET /api/teams
 * List all teams
 */
router.get('/', (_req, res) => {
  try {
    const teams = getAllTeams();
    res.json({ success: true, data: teams });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/teams
 * Create a new team
 */
router.post('/', (req, res) => {
  try {
    const { id, name, domain, description } = req.body;
    if (!id || !name || !domain) {
      return res.status(400).json({
        success: false,
        error: 'id, name, and domain are required',
      });
    }
    const team = createTeam({ id, name, domain, description });
    res.status(201).json({ success: true, data: team });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── All Agents (static routes BEFORE parametric /:id) ──────────────────────

/**
 * GET /api/teams/agents/all
 * List all active agents across all teams
 */
router.get('/agents/all', (_req, res) => {
  try {
    const agents = getAllAgents();
    res.json({ success: true, data: agents });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/teams/agents/performance
 * Get agent performance view
 */
router.get('/agents/performance', (_req, res) => {
  try {
    const performance = getAgentPerformance();
    res.json({ success: true, data: performance });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/teams/agents/:agentId
 * Get single agent by ID
 */
router.get('/agents/:agentId', (req, res) => {
  try {
    const agent = getAgentById(req.params.agentId);
    if (!agent) {
      return res.status(404).json({ success: false, error: 'Agent not found' });
    }
    res.json({ success: true, data: agent });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/teams/agents
 * Create a new agent
 */
router.post('/agents', (req, res) => {
  try {
    const { id, teamId, name, role, llmPreference, emoji } = req.body;
    if (!id || !teamId || !name || !role) {
      return res.status(400).json({
        success: false,
        error: 'id, teamId, name, and role are required',
      });
    }
    const agent = createAgent({ id, teamId, name, role, llmPreference, emoji });
    res.status(201).json({ success: true, data: agent });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * PATCH /api/teams/agents/:agentId
 * Update agent fields
 */
router.patch('/agents/:agentId', (req, res) => {
  try {
    const agent = updateAgent(req.params.agentId, req.body);
    res.json({ success: true, data: agent });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/teams/agents/:agentId/deactivate
 * Soft-delete (fire) an agent
 */
router.post('/agents/:agentId/deactivate', (req, res) => {
  try {
    const result = deactivateAgent(req.params.agentId);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/teams/agents/:agentId/reactivate
 * Re-hire an agent
 */
router.post('/agents/:agentId/reactivate', (req, res) => {
  try {
    const agent = reactivateAgent(req.params.agentId);
    res.json({ success: true, data: agent });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// ─── Parametric Team Routes (MUST come AFTER /agents/* routes) ───────────────

/**
 * GET /api/teams/:id
 * Get team by ID with its agents
 */
router.get('/:id', (req, res) => {
  try {
    const team = getTeamById(req.params.id);
    if (!team) {
      return res.status(404).json({ success: false, error: 'Team not found' });
    }
    const agents = getAgentsByTeam(req.params.id);
    res.json({ success: true, data: { ...team, agents } });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/teams/:id/agents
 * List agents for a team
 */
router.get('/:id/agents', (req, res) => {
  try {
    const agents = getAgentsByTeam(req.params.id);
    res.json({ success: true, data: agents });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
