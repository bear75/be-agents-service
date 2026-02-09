/**
 * Agent Service - Unified Dashboard & API
 *
 * Single server on port 3030:
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
import teamsRouter from './routes/teams.js';
import workspaceRouter from './routes/workspace.js';
import plansRouter from './routes/plans.js';
import sessionsRouter from './routes/sessions.js';
import logsRouter from './routes/logs.js';
import statsRouter from './routes/stats.js';
import jobsRouter from './routes/jobs.js';
import commandsRouter from './routes/commands.js';
import dataRouter from './routes/data.js';
import rlRouter from './routes/rl.js';
import repositoriesRouter from './routes/repositories.js';
import tasksRouter from './routes/tasks.js';
import integrationsRouter from './routes/integrations.js';
import gamificationRouter from './routes/gamification.js';
import fileRouter from './routes/file.js';

config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..', '..');
const STATIC_DIR = path.join(__dirname, '..', 'public');

const PORT = process.env.PORT || process.env.DASHBOARD_PORT || 3030;

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
  res.json({
    success: true,
    service: 'agent-service',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// API routes
app.use('/api/repos', reposRouter);
app.use('/api/agents', agentsRouter);
app.use('/api/teams', teamsRouter);
app.use('/api/workspace', workspaceRouter);
app.use('/api/plans', plansRouter);
app.use('/api/sessions', sessionsRouter);
app.use('/api/logs', logsRouter);
app.use('/api/stats', statsRouter);
app.use('/api/jobs', jobsRouter);
app.use('/api/commands', commandsRouter);
app.use('/api/data', dataRouter);
app.use('/api/rl', rlRouter);
app.use('/api/repositories', repositoriesRouter);
app.use('/api/tasks', tasksRouter);
app.use('/api/integrations', integrationsRouter);
app.use('/api/gamification', gamificationRouter);
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

const server = app.listen(PORT, () => {
  console.log('');
  console.log('════════════════════════════════════════');
  console.log('  Agent Service — Unified Dashboard');
  console.log('════════════════════════════════════════');
  console.log(`  Dashboard:  http://localhost:${PORT}/`);
  console.log(`  API:        http://localhost:${PORT}/api/`);
  console.log(`  Health:     http://localhost:${PORT}/health`);
  console.log('════════════════════════════════════════');
  console.log('');
});

process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down...');
  server.close(() => process.exit(0));
});
