#!/usr/bin/env node
/**
 * Sync session state from filesystem to SQLite database
 * Called by orchestrator.sh to persist session and task data
 */

const fs = require('fs');
const path = require('path');
const db = require('../lib/database');

const SERVICE_ROOT = path.join(__dirname, '..');
const STATE_DIR = path.join(SERVICE_ROOT, '.compound-state');

/**
 * Sync a session and its tasks to the database
 * @param {string} sessionId - Session ID (e.g., "session-1770537842")
 */
function syncSession(sessionId) {
  const sessionDir = path.join(STATE_DIR, sessionId);

  if (!fs.existsSync(sessionDir)) {
    console.error(`❌ Session directory not found: ${sessionDir}`);
    process.exit(1);
  }

  // Read orchestrator state
  const orchestratorFile = path.join(sessionDir, 'orchestrator.json');
  if (!fs.existsSync(orchestratorFile)) {
    console.error(`❌ Orchestrator state not found: ${orchestratorFile}`);
    process.exit(1);
  }

  const orchestratorState = JSON.parse(fs.readFileSync(orchestratorFile, 'utf-8'));

  // Extract session info
  const teamId = orchestratorState.team || 'team-engineering';
  const targetRepo = orchestratorState.targetRepo || '';
  const branchName = orchestratorState.branchName || '';
  const priorityFile = orchestratorState.priorityFile || '';
  const status = orchestratorState.status || 'in_progress';
  const startedAt = orchestratorState.startedAt || new Date().toISOString();

  console.log(`📝 Syncing session ${sessionId} to database...`);

  // Create or update session in database
  try {
    const existingSession = db.getSession(sessionId);

    if (!existingSession) {
      db.createSession({
        sessionId,
        teamId,
        targetRepo,
        branchName,
        priorityFile
      });
      console.log(`✅ Created session ${sessionId}`);
    } else {
      db.updateSessionStatus(sessionId, status);
      console.log(`✅ Updated session ${sessionId} status: ${status}`);
    }
  } catch (error) {
    console.error(`❌ Error syncing session: ${error.message}`);
    process.exit(1);
  }

  // Find job log file to detect failed specialists
  const jobLogPattern = /job-\d+-\w+\.log$/;
  const logsDir = path.join(SERVICE_ROOT, 'logs/running-jobs');
  let failedSpecialists = [];

  if (fs.existsSync(logsDir)) {
    const logFiles = fs.readdirSync(logsDir).filter(f => jobLogPattern.test(f));

    // Find the log file that contains this session
    for (const logFile of logFiles) {
      const logPath = path.join(logsDir, logFile);
      const logContent = fs.readFileSync(logPath, 'utf-8');

      if (logContent.includes(sessionId)) {
        // Parse spawned specialists and their PIDs
        const spawnedMap = {}; // PID -> agent name
        const spawnRegex = /Spawning (\w+) specialist\.\.\.\n.*spawned \(PID: (\d+)\)/g;
        let match;

        while ((match = spawnRegex.exec(logContent)) !== null) {
          const agentName = match[1];
          const pid = match[2];
          spawnedMap[pid] = agentName;
        }

        // Parse failed PIDs
        const failRegex = /Specialist (\d+) failed \(exit code: \d+\)/g;
        while ((match = failRegex.exec(logContent)) !== null) {
          const pid = match[1];
          if (spawnedMap[pid]) {
            failedSpecialists.push(spawnedMap[pid]);
          }
        }

        console.log(`📋 Found ${failedSpecialists.length} failed specialists: ${failedSpecialists.join(', ')}`);
        break;
      }
    }
  }

  // Sync tasks from specialist state files
  const stateFiles = fs.readdirSync(sessionDir).filter(f => f.endsWith('.json') && f !== 'orchestrator.json' && f !== 'session.json');

  let taskCount = 0;

  // Create tasks for failed specialists that have no state file
  for (const failedAgent of failedSpecialists) {
    if (!stateFiles.includes(`${failedAgent}.json`)) {
      const agentId = mapAgentNameToId(failedAgent);
      if (!agentId) {
        console.log(`  ⚠️  Unknown failed agent: ${failedAgent}, skipping...`);
        continue;
      }

      const taskId = `task-${sessionId}-${failedAgent}`;
      const description = `${failedAgent} task (failed before completion)`;
      const taskStatus = 'failed';
      const priority = 'medium';
      const llmUsed = 'sonnet';
      const errorMessage = 'Agent failed before writing state file';

      try {
        const existingTask = db.getTask(taskId);
        if (!existingTask) {
          db.createTask({
            taskId,
            sessionId,
            agentId,
            description,
            priority
          });

          db.updateTaskStatus(taskId, taskStatus, llmUsed, errorMessage);
          console.log(`  ✅ Created failed task: ${taskId} (no state file found)`);
          taskCount++;
        }
      } catch (error) {
        console.error(`  ❌ Error creating failed task for ${failedAgent}: ${error.message}`);
      }
    }
  }

  for (const stateFile of stateFiles) {
    const agentName = stateFile.replace('.json', '');
    const statePath = path.join(sessionDir, stateFile);

    try {
      const agentState = JSON.parse(fs.readFileSync(statePath, 'utf-8'));

      // Map agent name to agent_id
      const agentId = mapAgentNameToId(agentName);
      if (!agentId) {
        console.log(`⚠️  Unknown agent: ${agentName}, skipping...`);
        continue;
      }

      // Extract task info from agent state
      const taskId = `task-${sessionId}-${agentName}`;
      const description = agentState.task || agentState.description || `${agentName} task`;
      const taskStatus = mapAgentStatusToTaskStatus(agentState.status || status);
      const priority = agentState.priority || 'medium';

      // Normalize LLM value to match CHECK constraint
      let llmUsed = agentState.llm_used || process.env.CLAUDE_MODEL || 'sonnet';
      const validLLMs = ['opus-4.6', 'opus', 'sonnet', 'haiku', 'pi'];
      if (!validLLMs.includes(llmUsed)) {
        // Map common variations
        if (llmUsed.includes('opus')) llmUsed = 'opus';
        else if (llmUsed.includes('sonnet')) llmUsed = 'sonnet';
        else if (llmUsed.includes('haiku')) llmUsed = 'haiku';
        else llmUsed = 'sonnet'; // default
      }

      const errorMessage = agentState.error || null;
      const startTime = agentState.startedAt || startedAt;
      const endTime = agentState.completedAt || (taskStatus === 'completed' ? new Date().toISOString() : null);

      // Calculate duration
      let durationSeconds = null;
      if (startTime && endTime) {
        durationSeconds = Math.floor((new Date(endTime) - new Date(startTime)) / 1000);
      }

      // Create or update task
      const existingTask = db.getTask(taskId);

      console.log(`  📝 Creating task ${taskId} for agent ${agentId}, llm=${llmUsed}, status=${taskStatus}`);

      if (!existingTask) {
        db.createTask({
          taskId,
          sessionId,
          agentId,
          description,
          priority
        });

        // Update additional fields - signature: updateTaskStatus(taskId, status, llmUsed, errorMessage)
        console.log(`  📝 Updating task status and metadata...`);
        db.updateTaskStatus(taskId, taskStatus, llmUsed, errorMessage);

        console.log(`  ✅ Created task: ${taskId} (${taskStatus})`);
        taskCount++;
      } else {
        db.updateTaskStatus(taskId, taskStatus, llmUsed, errorMessage);
        console.log(`  ✅ Updated task: ${taskId} (${taskStatus})`);
        taskCount++;
      }
    } catch (error) {
      console.error(`  ❌ Error syncing ${stateFile}: ${error.message}`);
      console.error(`     Agent: ${agentName}, AgentID: ${agentId}, LLM: ${llmUsed}`);
    }
  }

  console.log(`✅ Synced ${taskCount} tasks for session ${sessionId}`);
}

/**
 * Map agent name from state file to agent_id in database
 */
function mapAgentNameToId(agentName) {
  const agentMap = {
    'orchestrator': 'agent-orchestrator',
    'backend': 'agent-backend',
    'frontend': 'agent-frontend',
    'infrastructure': 'agent-infrastructure',
    'verification': 'agent-verification',
    'senior-reviewer': 'agent-senior-reviewer',
    'db-architect': 'agent-db-architect',
    'ux-designer': 'agent-ux-designer',
    'docs-expert': 'agent-docs-expert',
    'levelup': 'agent-levelup',
    'jarvis': 'agent-jarvis',
    'vision': 'agent-vision',
    'loki': 'agent-loki',
    'shuri': 'agent-shuri',
    'fury': 'agent-fury',
    'wanda': 'agent-wanda',
    'quill': 'agent-quill',
    'pepper': 'agent-pepper',
    'friday': 'agent-friday',
    'wong': 'agent-wong'
  };

  return agentMap[agentName] || null;
}

/**
 * Map agent state status to task status
 */
function mapAgentStatusToTaskStatus(status) {
  const statusMap = {
    'in_progress': 'in_progress',
    'running': 'in_progress',
    'completed': 'completed',
    'success': 'completed',
    'failed': 'failed',
    'error': 'failed',
    'blocked': 'blocked',
    'pending': 'pending',
    'waiting': 'pending'
  };

  return statusMap[status] || 'in_progress';
}

// Main execution
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node sync-to-db.js <session-id>');
    console.error('Example: node sync-to-db.js session-1770537842');
    process.exit(1);
  }

  const sessionId = args[0];
  syncSession(sessionId);
}

module.exports = { syncSession };
