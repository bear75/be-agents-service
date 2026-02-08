#!/usr/bin/env node
/**
 * Migration Script - JSON to SQLite
 * Migrates existing JSON state files to SQLite database
 */

const fs = require('fs');
const path = require('path');
const db = require('../lib/database');

const SERVICE_ROOT = path.join(__dirname, '..');
const STATE_DIR = path.join(SERVICE_ROOT, '.compound-state');
const DATA_DIR = path.join(STATE_DIR, 'data');

let stats = {
  sessions: 0,
  tasks: 0,
  leads: 0,
  campaigns: 0,
  errors: []
};

/**
 * Migrate session directories to database
 */
function migrateSessions() {
  console.log('📦 Migrating sessions...');

  if (!fs.existsSync(STATE_DIR)) {
    console.log('⚠️  No .compound-state directory found, skipping sessions');
    return;
  }

  const sessionDirs = fs.readdirSync(STATE_DIR)
    .filter(name => name.startsWith('session-'));

  for (const sessionId of sessionDirs) {
    try {
      const sessionPath = path.join(STATE_DIR, sessionId);

      // Read orchestrator state
      const orchestratorFile = path.join(sessionPath, 'orchestrator.json');
      if (!fs.existsSync(orchestratorFile)) {
        continue;
      }

      const orchestratorState = JSON.parse(fs.readFileSync(orchestratorFile, 'utf8'));

      // Determine team based on target repo or default to engineering
      const teamId = 'team-engineering'; // Default, could be enhanced

      // Check if session already exists
      const existing = db.getSession(sessionId);
      if (existing) {
        console.log(`   ⏭️  Session ${sessionId} already exists, skipping`);
        continue;
      }

      // Create session
      db.createSession({
        sessionId,
        teamId,
        targetRepo: orchestratorState.target_repo || orchestratorState.targetRepo || 'unknown',
        priorityFile: orchestratorState.priority || null,
        branchName: orchestratorState.branch || null
      });

      // Update session status and metadata
      const status = orchestratorState.status || 'completed';
      const prUrl = orchestratorState.pr_url || orchestratorState.prUrl || null;

      db.updateSessionStatus(sessionId, status, prUrl);

      stats.sessions++;

      // Migrate tasks from agent states
      const agentFiles = fs.readdirSync(sessionPath).filter(f => f.endsWith('.json') && f !== 'orchestrator.json');

      for (const agentFile of agentFiles) {
        const agentName = agentFile.replace('.json', '');
        const agentPath = path.join(sessionPath, agentFile);
        const agentState = JSON.parse(fs.readFileSync(agentPath, 'utf8'));

        // Find agent in database
        const agent = db.getAgentByName(teamId, agentName.charAt(0).toUpperCase() + agentName.slice(1));

        if (!agent) {
          console.log(`   ⚠️  Agent ${agentName} not found in database, skipping tasks`);
          continue;
        }

        // Migrate completed tasks
        if (agentState.completedTasks && Array.isArray(agentState.completedTasks)) {
          for (let i = 0; i < agentState.completedTasks.length; i++) {
            const task = agentState.completedTasks[i];
            const taskId = `${sessionId}-${agent.id}-${i}`;

            // Check if task already exists
            const existingTask = db.getTask(taskId);
            if (existingTask) {
              continue;
            }

            db.createTask({
              taskId,
              sessionId,
              agentId: agent.id,
              description: task.description || task.task || 'Completed task',
              priority: 'medium'
            });

            db.updateTaskStatus(taskId, 'completed');
            stats.tasks++;
          }
        }

        // Migrate current task if in progress
        if (agentState.currentTask) {
          const taskId = `${sessionId}-${agent.id}-current`;

          const existingTask = db.getTask(taskId);
          if (!existingTask) {
            db.createTask({
              taskId,
              sessionId,
              agentId: agent.id,
              description: agentState.currentTask.description || agentState.currentTask.task || 'Current task',
              priority: 'high'
            });

            const taskStatus = agentState.status === 'in_progress' ? 'in_progress' : 'completed';
            db.updateTaskStatus(taskId, taskStatus);
            stats.tasks++;
          }
        }
      }

      console.log(`   ✅ Migrated session ${sessionId} with ${stats.tasks} tasks`);
    } catch (error) {
      console.error(`   ❌ Error migrating session ${sessionId}:`, error.message);
      stats.errors.push({ sessionId, error: error.message });
    }
  }
}

/**
 * Migrate marketing data (leads, campaigns)
 */
function migrateMarketingData() {
  console.log('📦 Migrating marketing data...');

  if (!fs.existsSync(DATA_DIR)) {
    console.log('⚠️  No data directory found, skipping marketing data');
    return;
  }

  // Migrate leads
  const leadsFile = path.join(DATA_DIR, 'leads.json');
  if (fs.existsSync(leadsFile)) {
    try {
      const leads = JSON.parse(fs.readFileSync(leadsFile, 'utf8'));

      for (const lead of leads) {
        // Check if lead already exists
        const existing = db.db.prepare('SELECT id FROM leads WHERE id = ?').get(lead.id);
        if (existing) {
          continue;
        }

        db.db.prepare(`
          INSERT INTO leads (id, source, contact_name, contact_email, company, status, score, assigned_to, notes)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
          lead.id,
          lead.source || 'unknown',
          lead.contactName || lead.name || null,
          lead.contactEmail || lead.email || null,
          lead.company || null,
          lead.status || 'new',
          lead.score || 50,
          lead.assignedTo || null,
          lead.notes || null
        );

        stats.leads++;
      }

      console.log(`   ✅ Migrated ${stats.leads} leads`);
    } catch (error) {
      console.error('   ❌ Error migrating leads:', error.message);
      stats.errors.push({ type: 'leads', error: error.message });
    }
  }

  // Migrate campaigns
  const campaignsFile = path.join(DATA_DIR, 'campaigns.json');
  if (fs.existsSync(campaignsFile)) {
    try {
      const campaigns = JSON.parse(fs.readFileSync(campaignsFile, 'utf8'));

      for (const campaign of campaigns) {
        // Check if campaign already exists
        const existing = db.db.prepare('SELECT id FROM campaigns WHERE id = ?').get(campaign.id);
        if (existing) {
          continue;
        }

        db.db.prepare(`
          INSERT INTO campaigns (id, name, type, owner, status, channels, deliverables, metrics, start_date, end_date)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
          campaign.id,
          campaign.name,
          campaign.type,
          campaign.owner || null,
          campaign.status || 'draft',
          JSON.stringify(campaign.channels || []),
          JSON.stringify(campaign.deliverables || []),
          JSON.stringify(campaign.metrics || {}),
          campaign.startDate || null,
          campaign.endDate || null
        );

        stats.campaigns++;
      }

      console.log(`   ✅ Migrated ${stats.campaigns} campaigns`);
    } catch (error) {
      console.error('   ❌ Error migrating campaigns:', error.message);
      stats.errors.push({ type: 'campaigns', error: error.message });
    }
  }
}

/**
 * Migrate user commands from tracking file
 */
function migrateUserCommands() {
  console.log('📦 Migrating user commands...');

  const commandsFile = path.join(DATA_DIR, 'user-commands.json');
  if (!fs.existsSync(commandsFile)) {
    console.log('⚠️  No user commands file found, skipping');
    return;
  }

  try {
    const commands = JSON.parse(fs.readFileSync(commandsFile, 'utf8'));
    let migrated = 0;

    for (const cmd of commands) {
      const normalizedIntent = cmd.normalized_intent ||
        `${cmd.team || 'unknown'}-${cmd.priority_file ? 'task' : 'general'}`;

      db.db.prepare(`
        INSERT INTO user_commands (command_text, normalized_intent, team, model, priority_file, branch_name, executed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(
        cmd.command_text || JSON.stringify(cmd),
        normalizedIntent,
        cmd.team || null,
        cmd.model || null,
        cmd.priorityFile || cmd.priority_file || null,
        cmd.branchName || cmd.branch_name || null,
        cmd.timestamp || cmd.executed_at || new Date().toISOString()
      );

      migrated++;
    }

    console.log(`   ✅ Migrated ${migrated} user commands`);
  } catch (error) {
    console.error('   ❌ Error migrating user commands:', error.message);
    stats.errors.push({ type: 'user_commands', error: error.message });
  }
}

/**
 * Main migration function
 */
function runMigration() {
  console.log('========================================');
  console.log('SQLite Migration - JSON to Database');
  console.log('========================================\n');

  migrateSessions();
  migrateMarketingData();
  migrateUserCommands();

  console.log('\n========================================');
  console.log('Migration Summary');
  console.log('========================================');
  console.log(`Sessions migrated: ${stats.sessions}`);
  console.log(`Tasks migrated: ${stats.tasks}`);
  console.log(`Leads migrated: ${stats.leads}`);
  console.log(`Campaigns migrated: ${stats.campaigns}`);
  console.log(`Errors: ${stats.errors.length}`);

  if (stats.errors.length > 0) {
    console.log('\nErrors:');
    stats.errors.forEach(err => {
      console.log(`  - ${err.sessionId || err.type}: ${err.error}`);
    });
  }

  console.log('\n✅ Migration complete!');
  console.log('========================================\n');

  db.close();
}

// Run migration if executed directly
if (require.main === module) {
  runMigration();
}

module.exports = { runMigration };
