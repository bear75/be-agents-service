import { Router } from 'express';
import { spawn } from 'child_process';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { resolve } from 'path';
import { db } from '../lib/services.js';

const router = Router();

// Track running agents
const runningAgents: Map<string, { process: any; startTime: Date }> = new Map();

/**
 * POST /api/agents/trigger/:name
 * Manually trigger an agent run
 */
router.post('/trigger/:name', async (req, res) => {
  try {
    const { name } = req.params;
    const { workflow = 'compound' } = req.body; // 'compound' or 'review'

    const config = getRepoConfig(name);
    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Repository '${name}' not found`,
      });
    }

    if (!config.enabled) {
      return res.status(400).json({
        success: false,
        error: `Repository '${name}' is disabled`,
      });
    }

    // Check if already running
    if (runningAgents.has(name)) {
      return res.status(409).json({
        success: false,
        error: `Agent for '${name}' is already running`,
      });
    }

    // Determine which script to run
    const scriptName =
      workflow === 'review'
        ? 'daily-compound-review.sh'
        : 'auto-compound.sh';
    const scriptPath = resolve(
      getServiceRoot(),
      'scripts',
      'compound',
      scriptName
    );

    // Spawn the agent process
    const agentProcess = spawn(scriptPath, [name], {
      detached: false,
      stdio: 'pipe',
    });

    runningAgents.set(name, {
      process: agentProcess,
      startTime: new Date(),
    });

    // Handle process completion
    agentProcess.on('exit', (code) => {
      console.log(`Agent for ${name} exited with code ${code}`);
      runningAgents.delete(name);
    });

    // Stream output to console
    agentProcess.stdout.on('data', (data) => {
      console.log(`[${name}] ${data.toString()}`);
    });

    agentProcess.stderr.on('data', (data) => {
      console.error(`[${name}] ERROR: ${data.toString()}`);
    });

    res.json({
      success: true,
      message: `Agent triggered for repository '${name}'`,
      data: {
        workflow,
        startTime: new Date(),
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * POST /api/agents/cancel/:name
 * Cancel a running agent
 */
router.post('/cancel/:name', (req, res) => {
  try {
    const { name } = req.params;
    const agent = runningAgents.get(name);

    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `No running agent found for '${name}'`,
      });
    }

    // Kill the process
    agent.process.kill('SIGTERM');
    runningAgents.delete(name);

    res.json({
      success: true,
      message: `Agent for '${name}' cancelled`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

/**
 * GET /api/agents/running
 * List all running agents
 */
router.get('/running', (req, res) => {
  try {
    const running = Array.from(runningAgents.entries()).map(([name, agent]) => ({
      name,
      startTime: agent.startTime,
      uptime: Date.now() - agent.startTime.getTime(),
    }));

    res.json({
      success: true,
      data: running,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// --- HR Agent Management (database) ---

router.get('/', (req, res) => {
  try {
    const agents = db.getAllAgents();
    res.json(agents);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/create', (req, res) => {
  try {
    const { teamId, name, role, llmPreference, emoji } = req.body;

    if (!teamId || !name || !role) {
      return res.status(400).json({
        error: 'Missing required fields: teamId, name, role',
      });
    }

    const agentId = `agent-${teamId}-${name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`;

    const agent = db.createAgent({
      id: agentId,
      teamId,
      name,
      role,
      llmPreference: llmPreference || 'sonnet',
      emoji: emoji || '🤖',
    });

    res.json({
      success: true,
      message: `Agent ${name} hired successfully`,
      agent,
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/:id/fire', (req, res) => {
  try {
    const { id } = req.params;
    db.deactivateAgent(id);
    res.json({
      success: true,
      message: 'Agent deactivated successfully',
      agentId: id,
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.post('/:id/rehire', (req, res) => {
  try {
    const { id } = req.params;
    const agent = db.reactivateAgent(id);
    res.json({
      success: true,
      message: 'Agent reactivated successfully',
      agent,
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/:id/evaluation', (req, res) => {
  try {
    const { id } = req.params;
    const evaluation = db.getAgentEvaluation(id);
    if (!evaluation) {
      return res.status(404).json({ error: 'Agent not found' });
    }
    res.json(evaluation);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.get('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const agent = db.getAgentById(id);
    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }
    res.json(agent);
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

router.patch('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const agent = db.updateAgent(id, req.body);
    res.json({
      success: true,
      message: 'Agent updated successfully',
      agent,
    });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

export default router;
