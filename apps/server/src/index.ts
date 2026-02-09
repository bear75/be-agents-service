import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
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
import { closeDatabase } from './lib/database.js';

// Load environment variables
config();

const app = express();
const PORT = process.env.PORT || 4010;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    success: true,
    service: 'agent-service',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    features: ['workspace', 'sessions', 'teams', 'marketing', 'metrics'],
  });
});

// API Routes — file-based (workspace, repos)
app.use('/api/repos', reposRouter);
app.use('/api/agents', agentsRouter);
app.use('/api/workspace', workspaceRouter);
app.use('/api/plans', plansRouter);

// API Routes — SQLite-backed (sessions, teams, commands, marketing, metrics)
app.use('/api/sessions', sessionsRouter);
app.use('/api/teams', teamsRouter);
app.use('/api/commands', commandsRouter);
app.use('/api/marketing', marketingRouter);
app.use('/api/metrics', metricsRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Not Found',
    path: req.url,
  });
});

// Error handler
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal Server Error',
    message: err.message,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Agent Service API v2.0 running on http://localhost:${PORT}`);
  console.log(`  Health:     http://localhost:${PORT}/health`);
  console.log(`  Repos:      http://localhost:${PORT}/api/repos`);
  console.log(`  Workspace:  http://localhost:${PORT}/api/workspace`);
  console.log(`  Sessions:   http://localhost:${PORT}/api/sessions`);
  console.log(`  Teams:      http://localhost:${PORT}/api/teams`);
  console.log(`  Commands:   http://localhost:${PORT}/api/commands`);
  console.log(`  Marketing:  http://localhost:${PORT}/api/marketing`);
  console.log(`  Metrics:    http://localhost:${PORT}/api/metrics`);
  console.log(`  Plans:      http://localhost:${PORT}/api/plans`);
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
