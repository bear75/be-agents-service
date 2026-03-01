#!/usr/bin/env node
/**
 * Job Executor - Spawns and manages orchestrator processes
 * Handles job lifecycle: start, stop, monitor status
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const db = require('./database');

const SERVICE_ROOT = path.join(__dirname, '..');
const JOBS_DIR = (() => {
  const override = (process.env.AGENT_JOBS_DIR || '').trim();
  if (!override) {
    return path.join(SERVICE_ROOT, 'logs/running-jobs');
  }
  return path.isAbsolute(override)
    ? override
    : path.join(SERVICE_ROOT, override);
})();

// Ensure jobs directory exists
if (!fs.existsSync(JOBS_DIR)) {
  fs.mkdirSync(JOBS_DIR, { recursive: true });
}

// In-memory job registry
const runningJobs = new Map();

/**
 * Load env vars from ~/.config/caire/env (export KEY=value) so spawned jobs get ANTHROPIC_API_KEY
 * even when the server is started by launchd without sourcing that file.
 * @returns {Object} Key-value pairs to merge into process env
 */
function loadCaireEnv() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) return {};
  const envPath = path.join(home, '.config', 'caire', 'env');
  if (!fs.existsSync(envPath)) return {};
  const out = {};
  try {
    const content = fs.readFileSync(envPath, 'utf8');
    content.split('\n').forEach((line) => {
      const m = line.match(/^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
      if (m) {
        let val = m[2].trim();
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'")))
          val = val.slice(1, -1).replace(/\\"/g, '"');
        out[m[1]] = val;
      }
    });
  } catch (e) {
    console.error('job-executor: could not load caire env:', e.message);
  }
  return out;
}

/**
 * Generate unique job ID
 */
function generateJobId() {
  return `job-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Start a new engineering job (runs auto-compound.sh: find priority → PRD → orchestrator → PR)
 * @param {Object} config - Job configuration
 * @param {string} config.model - LLM model to use (sonnet, opus, haiku)
 * @param {string} config.targetRepo - Repo name (e.g. appcaire) or path; auto-compound uses name
 * @returns {Object} Job info
 */
function startEngineeringJob(config) {
  const jobId = generateJobId();
  const {
    model = 'sonnet',
    targetRepo = 'appcaire',
    sessionId: configSessionId
  } = config;

  // Use repo name for auto-compound (e.g. "appcaire"); if path given, extract name from basename
  const repoName = path.isAbsolute(targetRepo)
    ? path.basename(targetRepo)
    : targetRepo.trim();

  // Run auto-compound.sh (same as nightly) - it finds priorities, creates PRD, runs orchestrator
  const scriptPath = path.join(SERVICE_ROOT, 'scripts/compound/auto-compound.sh');
  const args = [repoName];

  const caireEnv = loadCaireEnv();
  const env = {
    ...process.env,
    ...caireEnv,
    CLAUDE_MODEL: model,
    JOB_ID: jobId,
    ...(configSessionId && { SESSION_ID: configSessionId }),
  };

  // Spawn process
  const childProcess = spawn(scriptPath, args, {
    env,
    cwd: SERVICE_ROOT,
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  // Create job log file
  const logFile = path.join(JOBS_DIR, `${jobId}.log`);
  const logStream = fs.createWriteStream(logFile, { flags: 'a' });

  // Capture stdout and stderr
  childProcess.stdout.on('data', (data) => {
    logStream.write(`[STDOUT] ${data}`);
  });

  childProcess.stderr.on('data', (data) => {
    logStream.write(`[STDERR] ${data}`);
  });

  childProcess.on('close', (code) => {
    logStream.write(`\n[EXIT] Process exited with code ${code}\n`);
    logStream.end();

    // Update job status
    if (runningJobs.has(jobId)) {
      const job = runningJobs.get(jobId);
      job.status = code === 0 ? 'completed' : 'failed';
      job.exitCode = code;
      job.endTime = new Date();
    }
  });

  // Register job
  const job = {
    jobId,
    type: 'engineering',
    model,
    targetRepo: repoName,
    pid: childProcess.pid,
    status: 'running',
    startTime: new Date(),
    logFile
  };

  runningJobs.set(jobId, job);

  // Save job metadata
  fs.writeFileSync(
    path.join(JOBS_DIR, `${jobId}.json`),
    JSON.stringify(job, null, 2)
  );

  // Create session in database only when dashboard did not pass sessionId (e.g. nightly, CLI)
  if (!configSessionId) {
    try {
      db.createSession({
        sessionId: jobId,
        teamId: 'team-engineering',
        targetRepo: repoName,
        priorityFile: '(auto-compound discovers)',
        branchName: '(auto-compound generates)'
      });
      console.log(`✅ Created database session: ${jobId}`);
    } catch (error) {
      console.error(`⚠️  Failed to create database session: ${error.message}`);
    }
  }

  return job;
}

/**
 * Start a new marketing job
 * @param {Object} config - Job configuration
 * @param {string} config.model - LLM model to use
 * @param {string} config.priorityFile - Path to priority file
 * @param {string} config.branchName - Git branch name
 * @returns {Object} Job info
 */
function startMarketingJob(config) {
  const jobId = generateJobId();
  const {
    model = 'sonnet',
    priorityFile,
    branchName,
    targetRepo = path.join(SERVICE_ROOT, '../beta-appcaire')
  } = config;

  // Construct command
  const scriptPath = path.join(SERVICE_ROOT, 'agents/marketing/jarvis-orchestrator.sh');
  const args = [
    targetRepo,
    priorityFile,
    'tasks/marketing-prd.json',
    branchName
  ];

  const caireEnv = loadCaireEnv();
  const env = {
    ...process.env,
    ...caireEnv,
    CLAUDE_MODEL: model,
    JOB_ID: jobId
  };

  // Spawn process
  const childProcess = spawn(scriptPath, args, {
    env,
    cwd: SERVICE_ROOT,
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  // Create job log file
  const logFile = path.join(JOBS_DIR, `${jobId}.log`);
  const logStream = fs.createWriteStream(logFile, { flags: 'a' });

  // Capture stdout and stderr
  childProcess.stdout.on('data', (data) => {
    logStream.write(`[STDOUT] ${data}`);
  });

  childProcess.stderr.on('data', (data) => {
    logStream.write(`[STDERR] ${data}`);
  });

  childProcess.on('close', (code) => {
    logStream.write(`\n[EXIT] Process exited with code ${code}\n`);
    logStream.end();

    // Update job status
    if (runningJobs.has(jobId)) {
      const job = runningJobs.get(jobId);
      job.status = code === 0 ? 'completed' : 'failed';
      job.exitCode = code;
      job.endTime = new Date();
    }
  });

  // Register job
  const job = {
    jobId,
    type: 'marketing',
    model,
    priorityFile,
    branchName,
    targetRepo,
    pid: childProcess.pid,
    status: 'running',
    startTime: new Date(),
    logFile
  };

  runningJobs.set(jobId, job);

  // Save job metadata
  fs.writeFileSync(
    path.join(JOBS_DIR, `${jobId}.json`),
    JSON.stringify(job, null, 2)
  );

  // Create session in database
  try {
    db.createSession({
      sessionId: jobId,
      teamId: 'team-marketing',
      targetRepo,
      priorityFile,
      branchName
    });
    console.log(`✅ Created database session: ${jobId}`);
  } catch (error) {
    console.error(`⚠️  Failed to create database session: ${error.message}`);
  }

  return job;
}

/**
 * Stop a running job
 * @param {string} jobId - Job ID to stop
 * @returns {boolean} Success status
 */
function stopJob(jobId) {
  const job = runningJobs.get(jobId);

  if (!job) {
    return false;
  }

  if (job.status !== 'running') {
    return false; // Already stopped
  }

  try {
    // Kill process group (negative PID)
    process.kill(-job.pid, 'SIGTERM');

    // Update job status
    job.status = 'stopped';
    job.endTime = new Date();

    // Update metadata file
    fs.writeFileSync(
      path.join(JOBS_DIR, `${jobId}.json`),
      JSON.stringify(job, null, 2)
    );

    return true;
  } catch (error) {
    console.error(`Error stopping job ${jobId}:`, error);
    return false;
  }
}

/**
 * Get job status
 * @param {string} jobId - Job ID
 * @returns {Object|null} Job info or null if not found
 */
function getJobStatus(jobId) {
  // Check in-memory registry first
  if (runningJobs.has(jobId)) {
    return runningJobs.get(jobId);
  }

  // Check saved metadata
  const metadataFile = path.join(JOBS_DIR, `${jobId}.json`);
  if (fs.existsSync(metadataFile)) {
    return JSON.parse(fs.readFileSync(metadataFile, 'utf8'));
  }

  return null;
}

/**
 * Get all jobs (running and completed)
 * @returns {Array} List of all jobs
 */
function getAllJobs() {
  const jobs = [];

  // Add in-memory jobs
  runningJobs.forEach((job) => {
    jobs.push(job);
  });

  // Add jobs from metadata files (not in memory)
  try {
    const files = fs.readdirSync(JOBS_DIR);
    files.forEach((file) => {
      if (file.endsWith('.json')) {
        const jobId = file.replace('.json', '');
        if (!runningJobs.has(jobId)) {
          const metadata = JSON.parse(
            fs.readFileSync(path.join(JOBS_DIR, file), 'utf8')
          );
          jobs.push(metadata);
        }
      }
    });
  } catch (error) {
    console.error('Error reading job metadata files:', error);
  }

  // Sort by start time (newest first)
  jobs.sort((a, b) => new Date(b.startTime) - new Date(a.startTime));

  return jobs;
}

/**
 * Get job logs
 * @param {string} jobId - Job ID
 * @param {number} tailLines - Number of lines to tail (0 = all)
 * @returns {string|null} Log content or null if not found
 */
function getJobLogs(jobId, tailLines = 100) {
  const logFile = path.join(JOBS_DIR, `${jobId}.log`);

  if (!fs.existsSync(logFile)) {
    return null;
  }

  const content = fs.readFileSync(logFile, 'utf8');

  if (tailLines === 0) {
    return content;
  }

  const lines = content.split('\n');
  return lines.slice(-tailLines).join('\n');
}

/**
 * Trigger nightly job via launchctl
 * @returns {Object} Result
 */
function triggerNightlyJob() {
  const { execSync } = require('child_process');
  const label = (process.env.AUTO_COMPOUND_LAUNCHD_LABEL || 'com.appcaire.auto-compound').trim();

  try {
    // Trigger the learning extraction job
    execSync(`launchctl start ${label}`, {
      stdio: 'inherit'
    });

    return {
      success: true,
      message: `Nightly job triggered successfully (${label})`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error triggering nightly job (${label}): ${error.message}`
    };
  }
}

/**
 * Load jobs from disk on startup
 */
function loadJobsFromDisk() {
  try {
    const files = fs.readdirSync(JOBS_DIR);
    files.forEach((file) => {
      if (file.endsWith('.json')) {
        const metadata = JSON.parse(
          fs.readFileSync(path.join(JOBS_DIR, file), 'utf8')
        );

        // Only load running jobs to memory (completed jobs loaded on-demand)
        if (metadata.status === 'running') {
          runningJobs.set(metadata.jobId, metadata);
        }
      }
    });

    console.log(`Loaded ${runningJobs.size} running jobs from disk`);
  } catch (error) {
    console.error('Error loading jobs from disk:', error);
  }
}

// Load jobs on startup
loadJobsFromDisk();

/**
 * Clear all jobs from memory and delete all job metadata/log files.
 * Use to remove failed or stale job entries from the dashboard.
 * @returns {{ cleared: number, message: string }}
 */
function clearAllJobs() {
  let cleared = 0;
  try {
    runningJobs.clear();
    const files = fs.readdirSync(JOBS_DIR);
    files.forEach((file) => {
      if (file.endsWith('.json') || file.endsWith('.log')) {
        fs.unlinkSync(path.join(JOBS_DIR, file));
        cleared++;
      }
    });
    return { cleared, message: `Cleared ${cleared} job file(s). List will be empty after refresh.` };
  } catch (error) {
    console.error('Error clearing jobs:', error);
    return { cleared: 0, message: `Error: ${error.message}` };
  }
}

module.exports = {
  startEngineeringJob,
  startMarketingJob,
  stopJob,
  getJobStatus,
  getAllJobs,
  getJobLogs,
  triggerNightlyJob,
  clearAllJobs
};
