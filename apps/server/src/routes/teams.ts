/**
 * Teams API Routes
 *
 * RESTful endpoints for team management
 */

import { Router, Request, Response } from 'express';
import { db } from '../lib/services.js';

const router = Router();

// Type definitions
interface Team {
  id: string;
  name: string;
  domain: 'engineering' | 'marketing' | 'management';
  description?: string;
  created_at?: string;
  updated_at?: string;
}

interface UpdateTeamRequest {
  name?: string;
  description?: string;
}

/**
 * GET /api/teams
 * List all teams
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const teams = db.getAllTeams();

    res.json({
      success: true,
      teams,
      count: teams.length
    });
  } catch (error) {
    console.error('Error fetching teams:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch teams',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/teams/:id
 * Get team by ID
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const team = db.getTeamById(id);

    if (!team) {
      return res.status(404).json({
        success: false,
        error: 'Team not found'
      });
    }

    // Get team agents
    const agents = db.getAgentsByTeam(id);

    // Get team statistics
    const stats = db.db.prepare(`
      SELECT
        COUNT(DISTINCT t.id) as total_tasks,
        SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
        SUM(CASE WHEN t.status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
        SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
        AVG(CASE WHEN t.duration_seconds IS NOT NULL THEN t.duration_seconds ELSE 0 END) as avg_duration
      FROM tasks t
      JOIN agents a ON t.agent_id = a.id
      WHERE a.team_id = ?
    `).get(id);

    res.json({
      success: true,
      team: {
        ...team,
        agents,
        stats: {
          total_tasks: stats.total_tasks || 0,
          completed_tasks: stats.completed_tasks || 0,
          failed_tasks: stats.failed_tasks || 0,
          in_progress_tasks: stats.in_progress_tasks || 0,
          avg_duration_seconds: stats.avg_duration || 0,
          success_rate: stats.total_tasks > 0
            ? ((stats.completed_tasks / stats.total_tasks) * 100).toFixed(1) + '%'
            : '0%'
        }
      }
    });
  } catch (error) {
    console.error('Error fetching team:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch team',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/teams
 * Create a new team
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { id, name, domain, description } = req.body;

    // Validation
    if (!id || !name || !domain) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: id, name, domain'
      });
    }

    if (!['engineering', 'marketing', 'management'].includes(domain)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid domain. Must be: engineering, marketing, or management'
      });
    }

    // Check if team already exists
    const existing = db.getTeamById(id);
    if (existing) {
      return res.status(409).json({
        success: false,
        error: 'Team with this ID already exists'
      });
    }

    const team = db.createTeam({
      id,
      name,
      domain,
      description: description || null
    });

    res.status(201).json({
      success: true,
      team
    });
  } catch (error) {
    console.error('Error creating team:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create team',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * PATCH /api/teams/:id
 * Update a team
 */
router.patch('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updates: UpdateTeamRequest = req.body;

    // Check if team exists
    const existing = db.getTeamById(id);
    if (!existing) {
      return res.status(404).json({
        success: false,
        error: 'Team not found'
      });
    }

    // Validate updates
    if (Object.keys(updates).length === 0) {
      return res.status(400).json({
        success: false,
        error: 'No update fields provided'
      });
    }

    const team = db.updateTeam(id, updates);

    res.json({
      success: true,
      team
    });
  } catch (error) {
    console.error('Error updating team:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update team',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * DELETE /api/teams/:id
 * Delete a team (soft delete - deactivate all agents)
 *
 * Note: This doesn't actually delete the team from the database,
 * but deactivates all agents associated with it
 */
router.delete('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    // Check if team exists
    const team = db.getTeamById(id);
    if (!team) {
      return res.status(404).json({
        success: false,
        error: 'Team not found'
      });
    }

    // Get all agents for this team
    const agents = db.getAgentsByTeam(id);

    // Deactivate all agents (soft delete)
    for (const agent of agents) {
      db.deactivateAgent(agent.id);
    }

    res.json({
      success: true,
      message: `Team ${team.name} deactivated. ${agents.length} agent(s) deactivated.`,
      deactivated_agents: agents.length
    });
  } catch (error) {
    console.error('Error deleting team:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete team',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
