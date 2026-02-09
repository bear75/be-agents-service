#!/usr/bin/env node
/**
 * Unified Dashboard Startup
 * Starts API server (4010) and dashboard (3030) together.
 * Run: yarn dev:dashboard-unified or yarn start
 *
 * Prerequisites: yarn build:unified (builds React app into dashboard/public)
 */

const { spawn } = require('child_process');
const path = require('path');

const ROOT = path.join(__dirname, '..');
// Use 4011 for dev API to avoid conflict with launchd agent-server (4010)
const API_PORT = process.env.API_SERVER_PORT || 4011;
const DASHBOARD_PORT = process.env.DASHBOARD_PORT || 3030;

let apiProcess;

process.env.DASHBOARD_PORT = DASHBOARD_PORT;
process.env.API_SERVER_PORT = API_PORT;
process.env.PORT = API_PORT; // apps/server uses PORT

// Start API server in background
apiProcess = spawn('yarn', ['workspace', 'server', 'dev'], {
  cwd: ROOT,
  stdio: ['ignore', 'pipe', 'pipe'],
  shell: true,
  env: { ...process.env, PORT: API_PORT, API_SERVER_PORT: API_PORT },
});
apiProcess.stdout?.on('data', (d) => process.stdout.write(`[API] ${d}`));
apiProcess.stderr?.on('data', (d) => process.stderr.write(`[API] ${d}`));
apiProcess.on('error', (err) => console.error('API server failed:', err.message));

process.on('SIGINT', () => {
  apiProcess?.kill();
  process.exit(0);
});

// Start dashboard (foreground)
console.log('========================================');
console.log('Unified Dashboard');
console.log('========================================');
console.log('API server starting on port', API_PORT);
console.log('Dashboard starting on port', DASHBOARD_PORT);
console.log('');
console.log('Open: http://localhost:' + DASHBOARD_PORT + '/');
console.log('========================================');
console.log('');

require('./server.js');
