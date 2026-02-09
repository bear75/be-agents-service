/**
 * Workspace API Routes
 *
 * REST endpoints for reading and writing to the shared markdown workspace.
 * These endpoints serve data from workspace files (inbox, priorities, tasks,
 * check-ins, memory, follow-ups) and allow adding items via POST.
 *
 * All routes are prefixed with /api/workspace/:repo
 */

import { Router, Request, Response } from 'express';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { resolve } from 'path';
import {
  readInbox,
  readPrioritiesFromWorkspace,
  readTasks,
  readCheckIns,
  readCheckIn,
  readMemory,
  readMemoryEntry,
  readFollowUps,
  readWorkspaceOverview,
  readLatestAgentReport,
  isWorkspaceValid,
} from '../lib/workspace-reader.js';
import {
  appendToInbox,
  appendToFollowUps,
  addTask,
  createCheckIn,
  updatePriorities,
} from '../lib/workspace-writer.js';

const router = Router();

// ─── Middleware: resolve workspace path ─────────────────────────────────────

/**
 * Extract and validate workspace path from repo config.
 * Sets req.workspacePath for downstream handlers.
 */
function resolveWorkspace(req: Request, res: Response, next: () => void): void {
  const { repo } = req.params;
  const config = getRepoConfig(repo);

  if (!config) {
    res.status(404).json({
      success: false,
      error: `Repository '${repo}' not found`,
    });
    return;
  }

  if (!config.workspace?.enabled || !config.workspace?.path) {
    res.status(404).json({
      success: false,
      error: `No workspace configured for '${repo}'. Add workspace config to repos.yaml.`,
    });
    return;
  }

  // Store workspace path on request for handlers
  (req as any).workspacePath = config.workspace.path;
  next();
}

// Apply middleware to all routes
router.use('/:repo', resolveWorkspace);

// ─── GET /api/workspace/:repo/overview ──────────────────────────────────────

/**
 * Combined overview of the entire workspace
 */
router.get('/:repo/overview', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const overview = readWorkspaceOverview(workspacePath);

    res.json({
      success: true,
      data: overview,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read workspace overview',
    });
  }
});

// ─── GET /api/workspace/:repo/inbox ─────────────────────────────────────────

/**
 * List all inbox items
 */
router.get('/:repo/inbox', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const items = readInbox(workspacePath);

    res.json({
      success: true,
      data: items,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read inbox',
    });
  }
});

/**
 * Add an item to inbox
 */
router.post('/:repo/inbox', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { text } = req.body;

    if (!text || typeof text !== 'string') {
      res.status(400).json({
        success: false,
        error: 'Missing required field: text (string)',
      });
      return;
    }

    appendToInbox(workspacePath, text.trim());

    res.json({
      success: true,
      message: `Added to inbox: ${text.trim()}`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add to inbox',
    });
  }
});

// ─── GET /api/workspace/:repo/priorities ────────────────────────────────────

/**
 * List current priorities
 */
router.get('/:repo/priorities', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const priorities = readPrioritiesFromWorkspace(workspacePath);

    res.json({
      success: true,
      data: priorities,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read priorities',
    });
  }
});

/**
 * Reorder priorities
 */
router.post('/:repo/priorities/reorder', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { high, medium, low, parkingLot } = req.body;

    if (!high || !medium || !low) {
      res.status(400).json({
        success: false,
        error: 'Missing required fields: high, medium, low (arrays of {title, description?})',
      });
      return;
    }

    updatePriorities(workspacePath, high, medium, low, parkingLot);

    res.json({
      success: true,
      message: 'Priorities updated',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to update priorities',
    });
  }
});

// ─── GET /api/workspace/:repo/tasks ─────────────────────────────────────────

/**
 * List all workspace tasks
 */
router.get('/:repo/tasks', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const tasks = readTasks(workspacePath);

    res.json({
      success: true,
      data: tasks,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read tasks',
    });
  }
});

/**
 * Add a new task
 */
router.post('/:repo/tasks', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { title, priority, notes } = req.body;

    if (!title || typeof title !== 'string') {
      res.status(400).json({
        success: false,
        error: 'Missing required field: title (string)',
      });
      return;
    }

    addTask(workspacePath, title.trim(), priority, notes);

    res.json({
      success: true,
      message: `Task added: ${title.trim()}`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add task',
    });
  }
});

// ─── GET /api/workspace/:repo/check-ins ─────────────────────────────────────

/**
 * List check-ins, optionally filtered by type
 */
router.get('/:repo/check-ins', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const type = req.query.type as 'daily' | 'weekly' | 'monthly' | undefined;
    const limit = parseInt(req.query.limit as string) || 10;

    if (type && !['daily', 'weekly', 'monthly'].includes(type)) {
      res.status(400).json({
        success: false,
        error: 'Invalid type. Must be: daily, weekly, or monthly',
      });
      return;
    }

    let checkIns;
    if (type) {
      checkIns = readCheckIns(workspacePath, type).slice(0, limit);
    } else {
      // Return all types, merged and sorted by date
      const daily = readCheckIns(workspacePath, 'daily');
      const weekly = readCheckIns(workspacePath, 'weekly');
      const monthly = readCheckIns(workspacePath, 'monthly');
      checkIns = [...daily, ...weekly, ...monthly]
        .sort((a, b) => b.date.localeCompare(a.date))
        .slice(0, limit);
    }

    res.json({
      success: true,
      data: checkIns,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read check-ins',
    });
  }
});

/**
 * Get a specific check-in by date
 */
router.get('/:repo/check-ins/:type/:date', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { type, date } = req.params;

    if (!['daily', 'weekly', 'monthly'].includes(type)) {
      res.status(400).json({
        success: false,
        error: 'Invalid type. Must be: daily, weekly, or monthly',
      });
      return;
    }

    const checkIn = readCheckIn(workspacePath, type as 'daily' | 'weekly' | 'monthly', date);

    if (!checkIn) {
      res.status(404).json({
        success: false,
        error: `Check-in not found: ${type}/${date}`,
      });
      return;
    }

    res.json({
      success: true,
      data: checkIn,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read check-in',
    });
  }
});

/**
 * Create a new check-in from template
 */
router.post('/:repo/check-in', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { type = 'daily' } = req.body;

    if (!['daily', 'weekly', 'monthly'].includes(type)) {
      res.status(400).json({
        success: false,
        error: 'Invalid type. Must be: daily, weekly, or monthly',
      });
      return;
    }

    const templateDir = resolve(getServiceRoot(), 'scripts', 'workspace', 'templates');
    const filePath = createCheckIn(workspacePath, type, templateDir);

    if (!filePath) {
      res.json({
        success: true,
        message: `${type} check-in already exists for current period`,
      });
      return;
    }

    res.json({
      success: true,
      message: `${type} check-in created`,
      data: { path: filePath },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create check-in',
    });
  }
});

// ─── GET /api/workspace/:repo/memory ────────────────────────────────────────

/**
 * List all memory files
 */
router.get('/:repo/memory', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const memory = readMemory(workspacePath);

    res.json({
      success: true,
      data: memory,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read memory',
    });
  }
});

/**
 * Read a specific memory file
 */
router.get('/:repo/memory/:name', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { name } = req.params;
    const entry = readMemoryEntry(workspacePath, name);

    if (!entry) {
      res.status(404).json({
        success: false,
        error: `Memory file not found: ${name}`,
      });
      return;
    }

    res.json({
      success: true,
      data: entry,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read memory file',
    });
  }
});

// ─── GET /api/workspace/:repo/follow-ups ────────────────────────────────────

/**
 * List all follow-up items
 */
router.get('/:repo/follow-ups', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const followUps = readFollowUps(workspacePath);

    res.json({
      success: true,
      data: followUps,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read follow-ups',
    });
  }
});

/**
 * Add a follow-up item
 */
router.post('/:repo/follow-ups', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const { text, dueDate } = req.body;

    if (!text || typeof text !== 'string') {
      res.status(400).json({
        success: false,
        error: 'Missing required field: text (string)',
      });
      return;
    }

    appendToFollowUps(workspacePath, text.trim(), dueDate);

    res.json({
      success: true,
      message: `Follow-up added: ${text.trim()}`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add follow-up',
    });
  }
});

// ─── GET /api/workspace/:repo/agent-report ──────────────────────────────────

/**
 * Get the latest agent session report
 */
router.get('/:repo/agent-report', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const report = readLatestAgentReport(workspacePath);

    if (!report) {
      res.status(404).json({
        success: false,
        error: 'No agent report found',
      });
      return;
    }

    res.json({
      success: true,
      data: { content: report },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to read agent report',
    });
  }
});

// ─── GET /api/workspace/:repo/status ────────────────────────────────────────

/**
 * Quick workspace health/status check
 */
router.get('/:repo/status', (req: Request, res: Response) => {
  try {
    const workspacePath = (req as any).workspacePath;
    const valid = isWorkspaceValid(workspacePath);

    res.json({
      success: true,
      data: {
        path: workspacePath,
        valid,
        configured: true,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to check workspace status',
    });
  }
});

export default router;
