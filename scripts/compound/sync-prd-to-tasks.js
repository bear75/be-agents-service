#!/usr/bin/env node
/**
 * Sync tasks from scripts/compound/prd.json (target repo) to agent service DB.
 * Called by auto-compound.sh after prd.json is created and after loop completes.
 *
 * Usage: node scripts/compound/sync-prd-to-tasks.js <sessionId> <prdPath>
 * Example: node scripts/compound/sync-prd-to-tasks.js session-1771813048-30977 /path/to/repo/scripts/compound/prd.json
 */

const fs = require('fs');
const path = require('path');
const db = require('../../lib/database');

const AGENT_ID = 'agent-orchestrator'; // Compound tasks are orchestrated

/**
 * Map prd.json status to task status (DB CHECK constraint allows: pending, in_progress, completed, failed, blocked)
 * @param {string} prdStatus - Status from prd.json
 * @returns {string}
 */
function mapPrdStatusToTaskStatus(prdStatus) {
  const map = {
    pending: 'pending',
    in_progress: 'in_progress',
    completed: 'completed',
    blocked: 'blocked',
    failed: 'failed',
  };
  return map[prdStatus] || 'pending';
}

/**
 * Sync prd.json tasks to the tasks table
 * @param {string} sessionId - Session ID (e.g., session-1771813048-30977)
 * @param {string} prdPath - Absolute path to prd.json
 */
function syncPrdToTasks(sessionId, prdPath) {
  const resolvedPath = path.resolve(prdPath);

  if (!fs.existsSync(resolvedPath)) {
    console.error(`❌ prd.json not found at ${resolvedPath}`);
    process.exit(1);
  }

  let prd;
  try {
    prd = JSON.parse(fs.readFileSync(resolvedPath, 'utf-8'));
  } catch (err) {
    console.error(`❌ Invalid JSON in prd.json: ${err.message}`);
    process.exit(1);
  }

  const tasks = prd.tasks;
  if (!Array.isArray(tasks) || tasks.length === 0) {
    console.log('📋 No tasks in prd.json, skipping sync');
    return;
  }

  let created = 0;
  let updated = 0;

  for (const t of tasks) {
    const taskId = `task-${sessionId}-${t.id}`;
    const status = mapPrdStatusToTaskStatus(t.status || 'pending');
    const description = t.description || `Task ${t.id}`;
    const priority = t.priority || 'medium';
    const errorMessage = t.comment || null; // blocked tasks often have comment explaining why

    const existing = db.getTask(taskId);

    if (!existing) {
      db.createTask({
        taskId,
        sessionId,
        agentId: AGENT_ID,
        description,
        priority,
      });
      db.updateTaskStatus(taskId, status, 'sonnet', errorMessage);
      created++;
    } else {
      db.updateTaskStatus(taskId, status, 'sonnet', errorMessage);
      updated++;
    }
  }

  console.log(`📋 Synced prd.json → tasks: ${created} created, ${updated} updated`);
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node sync-prd-to-tasks.js <sessionId> <prdPath>');
    console.error('Example: node sync-prd-to-tasks.js session-1771813048-30977 /path/to/repo/scripts/compound/prd.json');
    process.exit(1);
  }

  const [sessionId, prdPath] = args;
  syncPrdToTasks(sessionId, prdPath);
}

module.exports = { syncPrdToTasks };
