import { Router } from 'express';
import { db } from '../lib/services.js';
import { nanoid } from 'nanoid';

const router = Router();

/**
 * GET /api/tasks
 * List all tasks with optional filters
 */
router.get('/', (req, res) => {
  try {
    const { team_id, agent_id, session_id, status } = req.query;

    let tasks = db.getAllTasks();

    if (team_id) {
      const agents = db.getAgentsByTeam(team_id as string);
      const agentIds = agents.map((a: { id: string }) => a.id);
      tasks = tasks.filter((t: { agent_id: string }) => agentIds.includes(t.agent_id));
    }
    if (agent_id) {
      tasks = tasks.filter((t: { agent_id: string }) => t.agent_id === agent_id);
    }
    if (session_id) {
      tasks = tasks.filter((t: { session_id: string }) => t.session_id === session_id);
    }
    if (status) {
      tasks = tasks.filter((t: { status: string }) => t.status === status);
    }

    res.json({
      success: true,
      tasks,
      count: tasks.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: (error as Error).message
    });
  }
});

/**
 * GET /api/tasks/:id
 * Get a single task by ID
 */
router.get('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const task = db.getTask(id);

    if (!task) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }

    res.json({
      success: true,
      task
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: (error as Error).message
    });
  }
});

/**
 * POST /api/tasks
 * Create a new task
 */
router.post('/', (req, res) => {
  try {
    const { sessionId, agentId, description, priority } = req.body;

    if (!sessionId || !agentId || !description) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: sessionId, agentId, description'
      });
    }

    const taskId = nanoid();

    const task = db.createTask({
      taskId,
      sessionId,
      agentId,
      description,
      priority: priority || 'medium'
    });

    res.status(201).json({
      success: true,
      task
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: (error as Error).message
    });
  }
});

/**
 * PATCH /api/tasks/:id
 * Update a task's description or priority
 */
router.patch('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    // Check if task exists
    const existing = db.getTask(id);
    if (!existing) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }

    if (Object.keys(updates).length === 0) {
      return res.status(400).json({
        success: false,
        error: 'No update fields provided'
      });
    }

    const task = db.updateTask(id, updates);

    res.json({
      success: true,
      task
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: (error as Error).message
    });
  }
});

/**
 * PATCH /api/tasks/:id/status
 * Update a task's status (for Kanban drag & drop)
 */
router.patch('/:id/status', (req, res) => {
  try {
    const { id } = req.params;
    const { status, llmUsed, errorMessage } = req.body;

    if (!status) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: status'
      });
    }

    // Check if task exists
    const existing = db.getTask(id);
    if (!existing) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }

    // Validate status
    const validStatuses = ['pending', 'in_progress', 'completed', 'failed'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        error: `Invalid status. Must be one of: ${validStatuses.join(', ')}`
      });
    }

    db.updateTaskStatus(id, status, llmUsed || null, errorMessage || null);
    const task = db.getTask(id);

    res.json({
      success: true,
      task
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: (error as Error).message
    });
  }
});

/**
 * DELETE /api/tasks/:id
 * Delete a task (not implemented - tasks are kept for historical record)
 */
router.delete('/:id', (req, res) => {
  res.status(501).json({
    success: false,
    error: 'Task deletion not implemented. Tasks are kept for historical records.'
  });
});

export default router;
