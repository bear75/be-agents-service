#!/usr/bin/env node
/**
 * Multi-Agent Dashboard Server
 * Real-time monitoring for agent orchestration sessions
 *
 * Port: 3030
 * Access: http://localhost:3030
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.DASHBOARD_PORT || 3030;
const SERVICE_ROOT = path.join(__dirname, '..');
const STATE_DIR = path.join(SERVICE_ROOT, '.compound-state');
const LOGS_DIR = path.join(SERVICE_ROOT, 'logs/orchestrator-sessions');

// Import modules
const jobExecutor = require(path.join(SERVICE_ROOT, 'lib/job-executor'));
const db = require(path.join(SERVICE_ROOT, 'lib/database'));
const learningController = require(path.join(SERVICE_ROOT, 'lib/learning-controller'));
const patternDetector = require(path.join(SERVICE_ROOT, 'lib/pattern-detector'));
const llmRouter = require(path.join(SERVICE_ROOT, 'lib/llm-router'));
const repositoryManager = require(path.join(SERVICE_ROOT, 'lib/repository-manager'));
const gamification = require(path.join(SERVICE_ROOT, 'lib/gamification'));

/**
 * Get all sessions from state directory
 */
function getSessions() {
  try {
    if (!fs.existsSync(STATE_DIR)) {
      return [];
    }

    const sessionDirs = fs.readdirSync(STATE_DIR)
      .filter(name => name.startsWith('session-'))
      .map(sessionId => {
        const sessionPath = path.join(STATE_DIR, sessionId);
        const stats = fs.statSync(sessionPath);

        // Read orchestrator state
        const orchestratorFile = path.join(sessionPath, 'orchestrator.json');
        let orchestratorState = {};
        if (fs.existsSync(orchestratorFile)) {
          orchestratorState = JSON.parse(fs.readFileSync(orchestratorFile, 'utf8'));
        }

        // Read verification state
        const verificationFile = path.join(sessionPath, 'verification.json');
        let verificationState = {};
        if (fs.existsSync(verificationFile)) {
          verificationState = JSON.parse(fs.readFileSync(verificationFile, 'utf8'));
        }

        // Read backend state
        const backendFile = path.join(sessionPath, 'backend.json');
        let backendState = {};
        if (fs.existsSync(backendFile)) {
          backendState = JSON.parse(fs.readFileSync(backendFile, 'utf8'));
        }

        // Read frontend state
        const frontendFile = path.join(sessionPath, 'frontend.json');
        let frontendState = {};
        if (fs.existsSync(frontendFile)) {
          frontendState = JSON.parse(fs.readFileSync(frontendFile, 'utf8'));
        }

        // Read infrastructure state
        const infraFile = path.join(sessionPath, 'infrastructure.json');
        let infraState = {};
        if (fs.existsSync(infraFile)) {
          infraState = JSON.parse(fs.readFileSync(infraFile, 'utf8'));
        }

        return {
          sessionId,
          createdAt: stats.birthtime,
          orchestrator: orchestratorState,
          verification: verificationState,
          backend: backendState,
          frontend: frontendState,
          infrastructure: infraState
        };
      })
      .sort((a, b) => b.createdAt - a.createdAt); // Newest first

    return sessionDirs;
  } catch (error) {
    console.error('Error getting sessions:', error);
    return [];
  }
}

/**
 * Get session details
 */
function getSession(sessionId) {
  try {
    const sessionPath = path.join(STATE_DIR, sessionId);
    if (!fs.existsSync(sessionPath)) {
      return null;
    }

    const session = {
      sessionId,
      agents: {}
    };

    // Read all JSON files in session directory
    const files = fs.readdirSync(sessionPath);
    files.forEach(file => {
      if (file.endsWith('.json')) {
        const agentName = file.replace('.json', '');
        const filePath = path.join(sessionPath, file);
        session.agents[agentName] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      }
    });

    return session;
  } catch (error) {
    console.error(`Error getting session ${sessionId}:`, error);
    return null;
  }
}

/**
 * Get session logs
 */
function getSessionLogs(sessionId) {
  try {
    const logPath = path.join(LOGS_DIR, sessionId);
    if (!fs.existsSync(logPath)) {
      return {};
    }

    const logs = {};
    const files = fs.readdirSync(logPath);

    files.forEach(file => {
      if (file.endsWith('.log')) {
        const logName = file.replace('.log', '');
        const logFile = path.join(logPath, file);
        const content = fs.readFileSync(logFile, 'utf8');

        // Get last 100 lines
        const lines = content.split('\n');
        logs[logName] = lines.slice(-100).join('\n');
      }
    });

    return logs;
  } catch (error) {
    console.error(`Error getting logs for ${sessionId}:`, error);
    return {};
  }
}

/**
 * Get system stats
 */
function getSystemStats() {
  const sessions = getSessions();
  const total = sessions.length;
  const running = sessions.filter(s => s.orchestrator.status === 'in_progress' || s.orchestrator.phase).length;
  const completed = sessions.filter(s => s.orchestrator.status === 'completed').length;
  const failed = sessions.filter(s => s.orchestrator.status === 'failed').length;
  const blocked = sessions.filter(s => s.verification.status === 'blocked').length;

  return {
    total,
    running,
    completed,
    failed,
    blocked,
    lastSession: sessions[0] || null
  };
}

/**
 * Simple router
 */
function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // API Routes
  if (pathname === '/api/sessions') {
    try {
      // Get sessions from database (not filesystem)
      const sessions = db.getRecentSessions(50);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(sessions));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/sessions/')) {
    const sessionId = pathname.split('/api/sessions/')[1];

    try {
      // Get session from database
      const session = db.getSession(sessionId);

      if (session) {
        // Also get tasks for this session
        const tasks = db.getSessionTasks(sessionId);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ...session, tasks }));
      } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Session not found' }));
      }
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/logs/')) {
    const sessionId = pathname.split('/api/logs/')[1];
    const logs = getSessionLogs(sessionId);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(logs));
    return;
  }

  if (pathname === '/api/stats') {
    try {
      // Get stats from database instead of filesystem
      const recentSessions = db.getRecentSessions(100);
      const allTasks = db.getAllTasks();
      const allAgents = db.getAllAgents();

      const stats = {
        totalSessions: recentSessions.length,
        activeSessions: recentSessions.filter(s => s.status === 'in_progress').length,
        completedSessions: recentSessions.filter(s => s.status === 'completed').length,
        failedSessions: recentSessions.filter(s => s.status === 'failed').length,
        totalTasks: allTasks.length,
        completedTasks: allTasks.filter(t => t.status === 'completed').length,
        failedTasks: allTasks.filter(t => t.status === 'failed').length,
        inProgressTasks: allTasks.filter(t => t.status === 'in_progress').length,
        totalAgents: allAgents.length,
        activeAgents: allAgents.filter(a => a.is_active).length
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(stats));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Marketing Data API endpoints (DATABASE ONLY - NO MOCKUP DATA)
  if (pathname === '/api/data/campaigns') {
    try {
      const campaigns = db.getAllCampaigns();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(campaigns || []));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/data/leads') {
    try {
      const leads = db.getAllLeads();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(leads || []));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/data/content') {
    try {
      const content = db.getAllContent();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(content || []));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/data/social') {
    try {
      // Social posts are content type 'social'
      const socialPosts = db.getContentByType('social');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(socialPosts || []));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Job Control API endpoints
  if (pathname === '/api/jobs/start' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const config = JSON.parse(body);
        const { team, model, priorityFile, branchName, targetRepo } = config;

        if (!team || !priorityFile || !branchName) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            error: 'Missing required fields: team, priorityFile, branchName'
          }));
          return;
        }

        let job;
        if (team === 'engineering') {
          job = jobExecutor.startEngineeringJob({
            model,
            priorityFile,
            branchName,
            targetRepo
          });
        } else if (team === 'marketing') {
          job = jobExecutor.startMarketingJob({
            model,
            priorityFile,
            branchName,
            targetRepo
          });
        } else {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid team. Must be "engineering" or "marketing"' }));
          return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(job));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  if (pathname.startsWith('/api/jobs/') && pathname.endsWith('/stop') && req.method === 'POST') {
    const jobId = pathname.split('/api/jobs/')[1].replace('/stop', '');
    const success = jobExecutor.stopJob(jobId);

    if (success) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, message: 'Job stopped' }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Job not found or already stopped' }));
    }
    return;
  }

  if (pathname.startsWith('/api/jobs/') && pathname.endsWith('/status')) {
    const jobId = pathname.split('/api/jobs/')[1].replace('/status', '');
    const status = jobExecutor.getJobStatus(jobId);

    if (status) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(status));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Job not found' }));
    }
    return;
  }

  if (pathname.startsWith('/api/jobs/') && pathname.endsWith('/logs')) {
    const jobId = pathname.split('/api/jobs/')[1].replace('/logs', '');
    const logs = jobExecutor.getJobLogs(jobId, 200);

    if (logs !== null) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(logs);
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Logs not found' }));
    }
    return;
  }

  if (pathname === '/api/jobs') {
    const jobs = jobExecutor.getAllJobs();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(jobs));
    return;
  }

  if (pathname === '/api/nightly/trigger' && req.method === 'POST') {
    const result = jobExecutor.triggerNightlyJob();
    res.writeHead(result.success ? 200 : 500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result));
    return;
  }

  // User command tracking (for RL pattern detection)
  if (pathname === '/api/commands' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const command = JSON.parse(body);

        // Save to SQLite database (user_commands table)
        try {
          db.trackUserCommand({
            commandText: command.text || '',
            normalizedIntent: command.normalizedIntent || '',
            team: command.team || null,
            model: command.model || null,
            priorityFile: command.priorityFile || null,
            branchName: command.branchName || null
          });
          console.log('✅ User command recorded in database');
        } catch (dbError) {
          console.error('⚠️  Failed to record command in database:', dbError.message);
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  // HR Agent Management API endpoints
  if (pathname === '/api/agents' && req.method === 'GET') {
    try {
      const agents = db.getAllAgents();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(agents));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/agents/create' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const agentData = JSON.parse(body);
        const { teamId, name, role, llmPreference, emoji } = agentData;

        if (!teamId || !name || !role) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            error: 'Missing required fields: teamId, name, role'
          }));
          return;
        }

        // Generate agent ID
        const agentId = `agent-${teamId}-${name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`;

        const agent = db.createAgent({
          id: agentId,
          teamId,
          name,
          role,
          llmPreference: llmPreference || 'sonnet',
          emoji: emoji || '🤖'
        });

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          message: `Agent ${name} hired successfully`,
          agent
        }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  if (pathname.startsWith('/api/agents/') && pathname.endsWith('/fire') && req.method === 'POST') {
    const agentId = pathname.split('/api/agents/')[1].replace('/fire', '');

    try {
      const result = db.deactivateAgent(agentId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        message: 'Agent deactivated successfully',
        agentId
      }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/agents/') && pathname.endsWith('/rehire') && req.method === 'POST') {
    const agentId = pathname.split('/api/agents/')[1].replace('/rehire', '');

    try {
      const agent = db.reactivateAgent(agentId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        message: 'Agent reactivated successfully',
        agent
      }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/agents/') && pathname.endsWith('/evaluation') && req.method === 'GET') {
    const agentId = pathname.split('/api/agents/')[1].replace('/evaluation', '');

    try {
      const evaluation = db.getAgentEvaluation(agentId);
      if (!evaluation) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Agent not found' }));
        return;
      }

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(evaluation));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/agents/') && req.method === 'GET') {
    const parts = pathname.split('/');
    // /api/agents/{id} - parts = ['', 'api', 'agents', '{id}']
    if (parts.length === 4 && parts[3]) {
      const agentId = parts[3];

      try {
        const agent = db.getAgentById(agentId);
        if (!agent) {
          res.writeHead(404, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Agent not found' }));
          return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(agent));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
      return;
    }
  }

  if (pathname.startsWith('/api/agents/') && req.method === 'PATCH') {
    const agentId = pathname.split('/api/agents/')[1];

    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const updates = JSON.parse(body);
        const agent = db.updateAgent(agentId, updates);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          message: 'Agent updated successfully',
          agent
        }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  // RL Dashboard API endpoints
  if (pathname === '/api/rl/experiments') {
    const experiments = db.getActiveExperiments();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(experiments));
    return;
  }

  if (pathname === '/api/rl/experiments/evaluate' && req.method === 'POST') {
    try {
      const results = learningController.evaluateAllExperiments();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, results }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/patterns') {
    try {
      const analysis = patternDetector.getPatternAnalysis();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(analysis));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/patterns/detect' && req.method === 'POST') {
    try {
      const analysis = patternDetector.runPatternDetection();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, analysis }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/automation-candidates') {
    try {
      const candidates = patternDetector.getAutomationCandidatesForApproval();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(candidates));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/rl/automation-candidates/') && pathname.endsWith('/approve') && req.method === 'POST') {
    const candidateId = pathname.split('/api/rl/automation-candidates/')[1].replace('/approve', '');

    try {
      const result = patternDetector.approveAutomationCandidate(candidateId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(result));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/rl/automation-candidates/') && pathname.endsWith('/dismiss') && req.method === 'POST') {
    const candidateId = pathname.split('/api/rl/automation-candidates/')[1].replace('/dismiss', '');

    try {
      // Update automation candidate status to dismissed
      db.updateAutomationCandidate(candidateId, { approved_by_user: false, is_automated: false });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, message: 'Automation candidate dismissed' }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/agent-performance') {
    try {
      const insights = learningController.getAgentInsights();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(insights));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/llm-stats') {
    try {
      const stats = llmRouter.getLLMStats(7);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(stats));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/rl/llm-cost-by-agent') {
    try {
      const costs = llmRouter.getCostByAgent(7);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(costs));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname === '/api/repositories') {
    try {
      const repos = repositoryManager.getActiveRepositories();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(repos));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  if (pathname.startsWith('/api/repositories/') && pathname.endsWith('/status')) {
    const repoId = pathname.split('/api/repositories/')[1].replace('/status', '');

    try {
      const status = repositoryManager.getRepositoryStatus(repoId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(status));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // ============================================
  // TASKS API ENDPOINTS
  // ============================================

  // Get all tasks (with optional filters)
  if (pathname.startsWith('/api/tasks')) {
    try {
      const url = new URL(req.url, `http://${req.headers.host}`);
      const teamId = url.searchParams.get('team_id');
      const agentId = url.searchParams.get('agent_id');
      const sessionId = url.searchParams.get('session_id');
      const status = url.searchParams.get('status');

      let tasks = db.getAllTasks();

      // Apply filters
      if (teamId) {
        const agents = db.getAgentsByTeam(teamId);
        const agentIds = agents.map(a => a.id);
        tasks = tasks.filter(t => agentIds.includes(t.agent_id));
      }
      if (agentId) {
        tasks = tasks.filter(t => t.agent_id === agentId);
      }
      if (sessionId) {
        tasks = tasks.filter(t => t.session_id === sessionId);
      }
      if (status) {
        tasks = tasks.filter(t => t.status === status);
      }

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(tasks));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // ============================================
  // INTEGRATIONS API ENDPOINTS
  // ============================================

  // Get all integrations
  if (pathname === '/api/integrations' && req.method === 'GET') {
    try {
      const integrations = db.getAllIntegrations();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(integrations));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Get integrations by type
  if (pathname.startsWith('/api/integrations/type/') && req.method === 'GET') {
    const type = pathname.split('/api/integrations/type/')[1];
    try {
      const integrations = db.getIntegrationsByType(type);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(integrations));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Update integration
  if (pathname.startsWith('/api/integrations/') && req.method === 'PATCH') {
    const integrationId = pathname.split('/api/integrations/')[1];

    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const updates = JSON.parse(body);
        const integration = db.updateIntegration(integrationId, updates);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, integration }));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  // ============================================
  // GAMIFICATION API ENDPOINTS
  // ============================================

  // Get agent gamification summary
  if (pathname.startsWith('/api/gamification/agent/')) {
    const agentId = pathname.split('/api/gamification/agent/')[1];

    try {
      const summary = gamification.getAgentGamification(agentId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(summary));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Get global leaderboard
  if (pathname === '/api/gamification/leaderboard') {
    const metric = parsedUrl.query.metric || 'xp';
    const limit = parseInt(parsedUrl.query.limit || '20');

    try {
      const leaderboard = gamification.getLeaderboard(metric, limit);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(leaderboard));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Get all achievements for agent
  if (pathname.startsWith('/api/gamification/achievements/')) {
    const agentId = pathname.split('/api/gamification/achievements/')[1];

    try {
      const achievements = gamification.getAllAchievements(agentId);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(achievements));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // Manually award XP (for testing/admin)
  if (pathname === '/api/gamification/award-xp' && req.method === 'POST') {
    let body = '';

    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const { agentId, amount, reason } = JSON.parse(body);

        if (!agentId || !amount || !reason) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Missing required fields: agentId, amount, reason' }));
          return;
        }

        const result = gamification.awardXP(agentId, amount, reason, 'manual', null);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  // Read file from disk (for documentation viewer)
  if (pathname === '/api/file') {
    const filePath = parsedUrl.query.path;

    if (!filePath) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing path parameter' }));
      return;
    }

    // Security: Only allow reading from specific directories
    const allowedPaths = [
      '/Users/bjornevers_MacPro/HomeCare/be-agent-service',
      '/Users/bjornevers_MacPro/HomeCare/beta-appcaire'
    ];

    const isAllowed = allowedPaths.some(allowed => filePath.startsWith(allowed));

    if (!isAllowed) {
      res.writeHead(403, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Access denied to this path' }));
      return;
    }

    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'File not found' }));
        return;
      }

      res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(data);
    });
    return;
  }

  // Serve static files
  let filePath = path.join(__dirname, 'public', pathname === '/' ? 'management-team.html' : pathname);

  // Security: prevent directory traversal
  if (!filePath.startsWith(path.join(__dirname, 'public'))) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
      return;
    }

    // Set content type based on file extension
    const ext = path.extname(filePath);
    const contentTypes = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json'
    };

    res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'text/plain' });
    res.end(data);
  });
}

// Create server
const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log('========================================');
  console.log('Multi-Agent Dashboard Server');
  console.log('========================================');
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log(`API available at http://localhost:${PORT}/api/`);
  console.log('');
  console.log('Endpoints:');
  console.log('  GET  /api/sessions           - List all sessions');
  console.log('  GET  /api/sessions/:id       - Get session details');
  console.log('  GET  /api/logs/:id           - Get session logs');
  console.log('  GET  /api/stats              - Get system statistics');
  console.log('  GET  /api/data/campaigns     - Get marketing campaigns');
  console.log('  GET  /api/data/leads         - Get marketing leads');
  console.log('  GET  /api/data/content       - Get content pieces');
  console.log('  GET  /api/data/social        - Get social posts');
  console.log('  GET  /api/file?path=...      - Read documentation file');
  console.log('');
  console.log('Job Control:');
  console.log('  POST /api/jobs/start         - Start new job');
  console.log('  POST /api/jobs/:id/stop      - Stop running job');
  console.log('  GET  /api/jobs/:id/status    - Get job status');
  console.log('  GET  /api/jobs/:id/logs      - Get job logs');
  console.log('  GET  /api/jobs               - List all jobs');
  console.log('  POST /api/nightly/trigger    - Trigger nightly job');
  console.log('  POST /api/commands           - Track user command (RL)');
  console.log('');
  console.log('HR Agent Management:');
  console.log('  GET  /api/agents             - List all agents');
  console.log('  POST /api/agents/create      - Create (hire) new agent');
  console.log('  POST /api/agents/:id/fire    - Deactivate (fire) agent');
  console.log('  POST /api/agents/:id/rehire  - Reactivate agent');
  console.log('  GET  /api/agents/:id         - Get agent details');
  console.log('  GET  /api/agents/:id/evaluation - Get RL evaluation');
  console.log('  PATCH /api/agents/:id        - Update agent');
  console.log('');
  console.log('RL Dashboard:');
  console.log('  GET  /api/rl/experiments         - Get experiments');
  console.log('  POST /api/rl/experiments/evaluate - Evaluate all experiments');
  console.log('  GET  /api/rl/patterns            - Get detected patterns');
  console.log('  POST /api/rl/patterns/detect     - Run pattern detection');
  console.log('  GET  /api/rl/automation-candidates - Get automation candidates');
  console.log('  POST /api/rl/automation-candidates/:id/approve - Approve candidate');
  console.log('  GET  /api/rl/agent-performance   - Get agent insights');
  console.log('  GET  /api/rl/llm-stats           - Get LLM usage stats');
  console.log('  GET  /api/rl/llm-cost-by-agent   - Get cost breakdown');
  console.log('  GET  /api/repositories           - List repositories');
  console.log('  GET  /api/repositories/:id/status - Get repo status');
  console.log('========================================');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
