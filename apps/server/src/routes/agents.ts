import { Router } from 'express';
import { spawn } from 'child_process';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { resolve } from 'path';

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

export default router;
