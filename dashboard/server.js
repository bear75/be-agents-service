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
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // API Routes
  if (pathname === '/api/sessions') {
    const sessions = getSessions();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(sessions));
    return;
  }

  if (pathname.startsWith('/api/sessions/')) {
    const sessionId = pathname.split('/api/sessions/')[1];
    const session = getSession(sessionId);

    if (session) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(session));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Session not found' }));
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
    const stats = getSystemStats();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(stats));
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
  let filePath = path.join(__dirname, 'public', pathname === '/' ? 'index.html' : pathname);

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
  console.log('  GET /api/sessions       - List all sessions');
  console.log('  GET /api/sessions/:id   - Get session details');
  console.log('  GET /api/logs/:id       - Get session logs');
  console.log('  GET /api/stats          - Get system statistics');
  console.log('  GET /api/file?path=...  - Read documentation file');
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
