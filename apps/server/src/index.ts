/**
 * Darwin - Unified Dashboard & API
 *
 * Single server on port 3010:
 * - Serves React app (/) as SPA
 * - All API routes consolidated (/api/*)
 *
 * Run: yarn start
 */
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import { fileURLToPath } from 'url';
import { config } from 'dotenv';

import reposRouter from './routes/repos.js';
import agentsRouter from './routes/agents.js';
import workspaceRouter from './routes/workspace.js';
import plansRouter from './routes/plans.js';
import sessionsRouter from './routes/sessions.js';
import teamsRouter from './routes/teams.js';
import commandsRouter from './routes/commands.js';
import marketingRouter from './routes/marketing.js';
import metricsRouter from './routes/metrics.js';
import jobsRouter from './routes/jobs.js';
import integrationsRouter from './routes/integrations.js';
import gamificationRouter from './routes/gamification.js';
import rlRouter from './routes/rl.js';
import schedulesRouter from './routes/schedules.js';
import systemRouter from './routes/system.js';
import fileRouter, { handleDocsRequest } from './routes/file.js';
import { closeDatabase } from './lib/database.js';

config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..', '..');
const STATIC_DIR = path.join(__dirname, '..', 'public');

const PORT = process.env.PORT || process.env.DASHBOARD_PORT || 3010;
const APP_DISPLAY_NAME = process.env.APP_DISPLAY_NAME || 'Darwin';
const DISABLED_DASHBOARD_MODULES = new Set(
  (process.env.DISABLED_DASHBOARD_MODULES || '')
    .split(',')
    .map((value) => value.trim().toLowerCase())
    .filter(Boolean),
);

function isModuleDisabled(moduleName: string): boolean {
  return DISABLED_DASHBOARD_MODULES.has(moduleName.toLowerCase());
}

function disabledModuleHandler(moduleName: string) {
  return (_req: express.Request, res: express.Response) => {
    res.status(403).json({
      success: false,
      error: `${moduleName} module is disabled for this dashboard instance`,
    });
  };
}

const app = express();

// Middleware
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});

// Health
app.get('/health', (req, res) => {
  const features = ['workspace', 'sessions', 'teams', 'marketing', 'metrics']
    .filter((feature) => !DISABLED_DASHBOARD_MODULES.has(feature))
    .filter((feature) => {
      if (feature === 'workspace') return !isModuleDisabled('workspace');
      if (feature === 'sessions') return !isModuleDisabled('work');
      return true;
    });
  res.json({
    success: true,
    service: 'agent-service',
    displayName: APP_DISPLAY_NAME,
    disabledModules: Array.from(DISABLED_DASHBOARD_MODULES),
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    features,
  });
});

// API Routes — file-based (workspace, repos)
app.use('/api/repos', reposRouter);
app.use('/api/agents', agentsRouter);
app.use('/api/workspace', workspaceRouter);
app.use('/api/plans', isModuleDisabled('plans') ? disabledModuleHandler('plans') : plansRouter);

// API Routes — SQLite-backed (sessions, teams, commands, marketing, metrics)
app.use('/api/sessions', sessionsRouter);
app.use('/api/teams', teamsRouter);
app.use('/api/commands', commandsRouter);
app.use('/api/marketing', marketingRouter);
app.use('/api/metrics', metricsRouter);
app.use('/api/jobs', jobsRouter);
app.use('/api/integrations', integrationsRouter);
app.use('/api/gamification', gamificationRouter);
app.use('/api/rl', rlRouter);
app.use(
  '/api/schedule-runs',
  isModuleDisabled('schedules') ? disabledModuleHandler('schedules') : schedulesRouter,
);
app.use('/api/system', systemRouter);
// Direct route for /api/file/docs (mounted router can miss in some setups)
app.get('/api/file/docs', handleDocsRequest);
app.use('/api/file', fileRouter);

// Static files (React build + classic HTML)
app.use(express.static(STATIC_DIR));

// SPA fallback: serve index.html for non-API GET requests (client-side routing)
app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api/')) return next();
  res.sendFile(path.join(STATIC_DIR, 'index.html'));
});

// 404
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Not Found', path: req.url });
});

// Error handler
app.use(
  (err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error('Server error:', err);
    res.status(500).json({
      success: false,
      error: 'Internal Server Error',
      message: err.message,
    });
  }
);

const HOST = process.env.HOST || '0.0.0.0';
app.listen(Number(PORT), HOST, () => {
  console.log('');
  console.log('════════════════════════════════════════');
  console.log(`  ${APP_DISPLAY_NAME} — Unified Dashboard`);
  console.log('════════════════════════════════════════');
  console.log(`  Dashboard:  http://localhost:${PORT}/`);
  console.log(`  API:        http://localhost:${PORT}/api/`);
  console.log(`  Health:     http://localhost:${PORT}/health`);
  if (HOST === '0.0.0.0') {
    console.log(`  Same WiFi:  http://<this-machine-ip>:${PORT}/  (see ipconfig/ifconfig)`);
  }
  console.log('════════════════════════════════════════');
  console.log('');
});

// Graceful shutdown — close SQLite connection
function shutdown(signal: string): void {
  console.log(`${signal} received, shutting down gracefully...`);
  try {
    closeDatabase();
    console.log('Database connection closed.');
  } catch {
    // DB may already be closed
  }
  process.exit(0);
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
