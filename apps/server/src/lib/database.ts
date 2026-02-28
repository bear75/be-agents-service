/**
 * SQLite Database Manager (TypeScript)
 * Provides typed access to the agent service database.
 *
 * Ported from lib/database.js (CommonJS) to ESM TypeScript.
 * DB file: .compound-state/agent-service.db (single source of truth for state; see docs/AGENT_WORKSPACE_STRUCTURE.md)
 * Schema: schema.sql
 */

import Database, { type Database as DatabaseType } from 'better-sqlite3';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import type {
  Team,
  Agent,
  Session,
  Task,
  Experiment,
  MetricRecord,
  Pattern,
  Reward,
  UserCommand,
  AutomationCandidate,
  Campaign,
  Lead,
  ContentPiece,
  LessonLearned,
  AgentPerformanceView,
  ActiveSessionView,
  ScheduleRun,
} from '../types/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Service root is four levels up: apps/server/src/lib → repo root
const SERVICE_ROOT = resolve(__dirname, '..', '..', '..', '..');
const DB_PATH = resolve(SERVICE_ROOT, '.compound-state', 'agent-service.db');
const SCHEMA_PATH = resolve(SERVICE_ROOT, 'schema.sql');

// Ensure .compound-state directory exists (service write area; see docs/AGENT_WORKSPACE_STRUCTURE.md)
const stateDir = dirname(DB_PATH);
if (!existsSync(stateDir)) {
  mkdirSync(stateDir, { recursive: true });
}

const needsInit = !existsSync(DB_PATH);

const db: DatabaseType = new Database(DB_PATH);

// Enable foreign keys and WAL mode
db.pragma('foreign_keys = ON');
db.pragma('journal_mode = WAL');

/**
 * Initialize database from schema.sql
 */
function initializeSchema(): void {
  console.log('Initializing database schema...');
  if (!existsSync(SCHEMA_PATH)) {
    throw new Error(`Schema file not found: ${SCHEMA_PATH}`);
  }
  const schema = readFileSync(SCHEMA_PATH, 'utf8');
  const cleanSchema = schema
    .split('\n')
    .filter((line) => !line.trim().startsWith('--'))
    .join('\n');
  try {
    db.exec(cleanSchema);
    console.log('Database schema initialized');
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error);
    console.error('Error initializing schema:', msg);
    throw error;
  }
}

if (needsInit) {
  initializeSchema();
} else {
  const tables = db
    .prepare("SELECT name FROM sqlite_master WHERE type='table'")
    .all() as { name: string }[];
  if (tables.length === 0) {
    console.log('Database exists but empty, reinitializing...');
    initializeSchema();
  }
}

// ─── Teams ────────────────────────────────────────────────────────────────────

export function getAllTeams(): Team[] {
  return db.prepare('SELECT * FROM teams ORDER BY name').all() as Team[];
}

export function getTeamById(teamId: string): Team | undefined {
  return db.prepare('SELECT * FROM teams WHERE id = ?').get(teamId) as
    | Team
    | undefined;
}

export function createTeam(team: {
  id: string;
  name: string;
  domain: string;
  description?: string;
}): Team | undefined {
  db.prepare(
    'INSERT INTO teams (id, name, domain, description) VALUES (?, ?, ?, ?)',
  ).run(team.id, team.name, team.domain, team.description ?? null);
  return getTeamById(team.id);
}

// ─── Sessions ─────────────────────────────────────────────────────────────────

export function createSession(params: {
  sessionId: string;
  teamId: string;
  targetRepo: string;
  priorityFile?: string;
  branchName?: string;
}): Session | undefined {
  db.prepare(
    `INSERT INTO sessions (id, team_id, status, target_repo, priority_file, branch_name)
     VALUES (?, ?, 'in_progress', ?, ?, ?)`,
  ).run(
    params.sessionId,
    params.teamId,
    params.targetRepo,
    params.priorityFile ?? null,
    params.branchName ?? null,
  );
  return getSession(params.sessionId);
}

export function getSession(sessionId: string): Session | undefined {
  return db.prepare('SELECT * FROM sessions WHERE id = ?').get(sessionId) as
    | Session
    | undefined;
}

export function updateSessionStatus(
  sessionId: string,
  status: string,
  prUrl?: string,
  exitCode?: number,
): void {
  const now = new Date().toISOString();
  db.prepare(
    `UPDATE sessions
     SET status = ?,
         pr_url = COALESCE(?, pr_url),
         exit_code = COALESCE(?, exit_code),
         completed_at = CASE WHEN ? IN ('completed', 'failed') THEN ? ELSE completed_at END,
         duration_seconds = CASE
           WHEN ? IN ('completed', 'failed') THEN
             (julianday(?) - julianday(started_at)) * 86400
           ELSE duration_seconds
         END
     WHERE id = ?`,
  ).run(status, prUrl ?? null, exitCode ?? null, status, now, status, now, sessionId);
}

export function getRecentSessions(limit = 10): (Session & { team_name: string })[] {
  return db
    .prepare(
      `SELECT s.*, t.name as team_name
       FROM sessions s
       JOIN teams t ON s.team_id = t.id
       ORDER BY s.started_at DESC
       LIMIT ?`,
    )
    .all(limit) as (Session & { team_name: string })[];
}

export function getActiveSessions(): ActiveSessionView[] {
  return db.prepare('SELECT * FROM v_active_sessions').all() as ActiveSessionView[];
}

// ─── Tasks ────────────────────────────────────────────────────────────────────

export function createTask(params: {
  taskId: string;
  sessionId: string;
  agentId: string;
  description: string;
  priority?: string;
}): Task | undefined {
  db.prepare(
    `INSERT INTO tasks (id, session_id, agent_id, description, status, priority)
     VALUES (?, ?, ?, ?, 'pending', ?)`,
  ).run(
    params.taskId,
    params.sessionId,
    params.agentId,
    params.description,
    params.priority ?? 'medium',
  );
  return getTask(params.taskId);
}

export function getTask(taskId: string): Task | undefined {
  return db.prepare('SELECT * FROM tasks WHERE id = ?').get(taskId) as
    | Task
    | undefined;
}

export function updateTaskStatus(
  taskId: string,
  status: string,
  llmUsed?: string,
  errorMessage?: string,
): void {
  const now = new Date().toISOString();
  db.prepare(
    `UPDATE tasks
     SET status = ?,
         llm_used = COALESCE(?, llm_used),
         error_message = ?,
         completed_at = CASE WHEN ? IN ('completed', 'failed') THEN ? ELSE completed_at END,
         duration_seconds = CASE
           WHEN ? IN ('completed', 'failed') THEN
             (julianday(?) - julianday(started_at)) * 86400
           ELSE duration_seconds
         END
     WHERE id = ?`,
  ).run(status, llmUsed ?? null, errorMessage ?? null, status, now, status, now, taskId);
}

export function getSessionTasks(
  sessionId: string,
): (Task & { agent_name: string; agent_emoji: string })[] {
  return db
    .prepare(
      `SELECT t.*, a.name as agent_name, a.emoji as agent_emoji
       FROM tasks t
       JOIN agents a ON t.agent_id = a.id
       WHERE t.session_id = ?
       ORDER BY t.started_at DESC`,
    )
    .all(sessionId) as (Task & { agent_name: string; agent_emoji: string })[];
}

export function getAllTasks(): (Task & {
  agent_name: string;
  agent_emoji: string;
  team_name: string;
})[] {
  return db
    .prepare(
      `SELECT t.*, a.name as agent_name, a.emoji as agent_emoji, te.name as team_name
       FROM tasks t
       LEFT JOIN agents a ON t.agent_id = a.id
       LEFT JOIN teams te ON a.team_id = te.id
       ORDER BY t.started_at DESC`,
    )
    .all() as (Task & { agent_name: string; agent_emoji: string; team_name: string })[];
}

// ─── Agents ───────────────────────────────────────────────────────────────────

export function getAllAgents(): (Agent & { team_name: string })[] {
  return db
    .prepare(
      `SELECT a.*, t.name as team_name
       FROM agents a
       JOIN teams t ON a.team_id = t.id
       WHERE a.is_active = 1
       ORDER BY t.domain, a.name`,
    )
    .all() as (Agent & { team_name: string })[];
}

export function getAgentsByTeam(teamId: string): Agent[] {
  return db
    .prepare(
      `SELECT * FROM agents WHERE team_id = ? AND is_active = 1 ORDER BY name`,
    )
    .all(teamId) as Agent[];
}

export function getAgentById(agentId: string): (Agent & { team_name?: string; team_domain?: string }) | undefined {
  return db
    .prepare(
      `SELECT a.*, t.name as team_name, t.domain as team_domain
       FROM agents a
       LEFT JOIN teams t ON a.team_id = t.id
       WHERE a.id = ?`,
    )
    .get(agentId) as (Agent & { team_name?: string; team_domain?: string }) | undefined;
}

export function createAgent(params: {
  id: string;
  teamId: string;
  name: string;
  role: string;
  llmPreference?: string;
  emoji?: string;
}): (Agent & { team_name?: string; team_domain?: string }) | undefined {
  db.prepare(
    `INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active)
     VALUES (?, ?, ?, ?, ?, ?, 1)`,
  ).run(
    params.id,
    params.teamId,
    params.name,
    params.role,
    params.emoji ?? '🤖',
    params.llmPreference ?? 'sonnet',
  );
  return getAgentById(params.id);
}

export function updateAgent(
  agentId: string,
  updates: Record<string, string>,
): (Agent & { team_name?: string; team_domain?: string }) | undefined {
  const allowedFields = ['name', 'role', 'emoji', 'llm_preference'];
  const fields: string[] = [];
  const values: string[] = [];
  for (const [key, value] of Object.entries(updates)) {
    if (allowedFields.includes(key)) {
      fields.push(`${key} = ?`);
      values.push(value);
    }
  }
  if (fields.length === 0) return getAgentById(agentId);
  values.push(agentId);
  db.prepare(
    `UPDATE agents SET ${fields.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
  ).run(...values);
  return getAgentById(agentId);
}

export function deactivateAgent(agentId: string): { success: boolean; agentId: string } {
  db.prepare('UPDATE agents SET is_active = 0 WHERE id = ?').run(agentId);
  return { success: true, agentId };
}

export function reactivateAgent(agentId: string): (Agent & { team_name?: string; team_domain?: string }) | undefined {
  db.prepare('UPDATE agents SET is_active = 1 WHERE id = ?').run(agentId);
  return getAgentById(agentId);
}

export function getAgentPerformance(): AgentPerformanceView[] {
  return db.prepare('SELECT * FROM v_agent_performance').all() as AgentPerformanceView[];
}

// ─── Metrics ──────────────────────────────────────────────────────────────────

export function recordMetric(params: {
  entityType: string;
  entityId: string;
  metricName: string;
  metricValue: number;
  context?: Record<string, unknown>;
}): void {
  db.prepare(
    `INSERT INTO metrics (entity_type, entity_id, metric_name, metric_value, context)
     VALUES (?, ?, ?, ?, ?)`,
  ).run(
    params.entityType,
    params.entityId,
    params.metricName,
    params.metricValue,
    params.context ? JSON.stringify(params.context) : null,
  );
}

export function getMetrics(
  entityType: string,
  entityId: string,
  metricName?: string,
): MetricRecord[] {
  if (metricName) {
    return db
      .prepare(
        `SELECT * FROM metrics
         WHERE entity_type = ? AND entity_id = ? AND metric_name = ?
         ORDER BY recorded_at DESC`,
      )
      .all(entityType, entityId, metricName) as MetricRecord[];
  }
  return db
    .prepare(
      `SELECT * FROM metrics
       WHERE entity_type = ? AND entity_id = ?
       ORDER BY recorded_at DESC`,
    )
    .all(entityType, entityId) as MetricRecord[];
}

// ─── Rewards ──────────────────────────────────────────────────────────────────

export function issueReward(params: {
  entityType: string;
  entityId: string;
  rewardValue: number;
  reason: string;
}): Reward {
  db.prepare(
    `INSERT INTO rewards (entity_type, entity_id, reward_value, reason)
     VALUES (?, ?, ?, ?)`,
  ).run(params.entityType, params.entityId, params.rewardValue, params.reason);
  return params as Reward;
}

export function getEntityRewards(
  entityType: string,
  entityId: string,
): { total_reward: number | null; reward_count: number; avg_reward: number | null } {
  return db
    .prepare(
      `SELECT SUM(reward_value) as total_reward, COUNT(*) as reward_count, AVG(reward_value) as avg_reward
       FROM rewards WHERE entity_type = ? AND entity_id = ?`,
    )
    .get(entityType, entityId) as {
    total_reward: number | null;
    reward_count: number;
    avg_reward: number | null;
  };
}

// ─── Patterns ─────────────────────────────────────────────────────────────────

export function recordPattern(params: {
  patternId: string;
  patternType: string;
  description: string;
  confidenceScore?: number;
}): void {
  db.prepare(
    `INSERT OR REPLACE INTO patterns (id, pattern_type, description, detection_count, confidence_score, last_detected_at)
     VALUES (?, ?, ?,
       COALESCE((SELECT detection_count FROM patterns WHERE id = ?), 0) + 1,
       ?, CURRENT_TIMESTAMP)`,
  ).run(
    params.patternId,
    params.patternType,
    params.description,
    params.patternId,
    params.confidenceScore ?? 0.5,
  );
}

export function getPatterns(
  patternType?: string,
  status = 'active',
): Pattern[] {
  if (patternType) {
    return db
      .prepare(
        `SELECT * FROM patterns WHERE pattern_type = ? AND status = ?
         ORDER BY detection_count DESC, confidence_score DESC`,
      )
      .all(patternType, status) as Pattern[];
  }
  return db
    .prepare(
      `SELECT * FROM patterns WHERE status = ?
       ORDER BY detection_count DESC, confidence_score DESC`,
    )
    .all(status) as Pattern[];
}

// ─── User Commands ────────────────────────────────────────────────────────────

export function trackUserCommand(params: {
  commandText: string;
  normalizedIntent?: string;
  team?: string;
  model?: string;
  priorityFile?: string;
  branchName?: string;
}): void {
  db.prepare(
    `INSERT INTO user_commands (command_text, normalized_intent, team, model, priority_file, branch_name)
     VALUES (?, ?, ?, ?, ?, ?)`,
  ).run(
    params.commandText,
    params.normalizedIntent ?? null,
    params.team ?? null,
    params.model ?? null,
    params.priorityFile ?? null,
    params.branchName ?? null,
  );
}

export function getAutomationCandidates(): AutomationCandidate[] {
  return db
    .prepare(
      `SELECT * FROM automation_candidates
       WHERE occurrence_count >= 3 AND is_automated = 0
       ORDER BY occurrence_count DESC, confidence_score DESC`,
    )
    .all() as AutomationCandidate[];
}

export function getUserCommandPatterns(): UserCommand[] {
  return db.prepare('SELECT * FROM v_user_command_patterns').all() as UserCommand[];
}

// ─── Experiments ──────────────────────────────────────────────────────────────

export function createExperiment(params: {
  experimentId: string;
  name: string;
  description?: string;
  successMetric: string;
  targetValue?: number;
}): Experiment | undefined {
  db.prepare(
    `INSERT INTO experiments (id, name, description, success_metric, target_value)
     VALUES (?, ?, ?, ?, ?)`,
  ).run(
    params.experimentId,
    params.name,
    params.description ?? null,
    params.successMetric,
    params.targetValue ?? null,
  );
  return getExperiment(params.experimentId);
}

export function getExperiment(experimentId: string): Experiment | undefined {
  return db.prepare('SELECT * FROM experiments WHERE id = ?').get(experimentId) as
    | Experiment
    | undefined;
}

export function getActiveExperiments(): Experiment[] {
  return db
    .prepare("SELECT * FROM experiments WHERE status = 'active' ORDER BY created_at DESC")
    .all() as Experiment[];
}

// ─── Schedule runs (Timefold FSR pipeline) ────────────────────────────────────

export function getAllScheduleRuns(dataset?: string): ScheduleRun[] {
  if (dataset) {
    return db
      .prepare(
        'SELECT * FROM schedule_runs WHERE dataset = ? ORDER BY submitted_at DESC',
      )
      .all(dataset) as ScheduleRun[];
  }
  return db
    .prepare('SELECT * FROM schedule_runs ORDER BY submitted_at DESC')
    .all() as ScheduleRun[];
}

export function getScheduleRunById(id: string): ScheduleRun | undefined {
  return db.prepare('SELECT * FROM schedule_runs WHERE id = ?').get(id) as
    | ScheduleRun
    | undefined;
}

export function cancelScheduleRun(
  id: string,
  reason: string,
): ScheduleRun | undefined {
  const now = new Date().toISOString();
  db.prepare(
    `UPDATE schedule_runs SET status = 'cancelled', decision = 'kill', decision_reason = ?, cancelled_at = ? WHERE id = ?`,
  ).run(reason, now, id);
  return getScheduleRunById(id);
}

/**
 * Run seed SQL for schedule_runs so dashboard has sample 28-feb runs with full metrics.
 * When force is false: only runs if table is empty.
 * When force is true: always runs (REPLACE overwrites the 11 sample runs with full metrics).
 */
export function runSeedScheduleRunsIfEmpty(force = false): number {
  const count = db.prepare('SELECT COUNT(*) as n FROM schedule_runs').get() as { n: number };
  if (!force && count.n > 0) return count.n;
  const seedPath = resolve(SERVICE_ROOT, 'scripts', 'seed-schedule-runs.sql');
  if (!existsSync(seedPath)) return 0;
  const sql = readFileSync(seedPath, 'utf8').replace(/^--.*$/gm, '').trim();
  if (!sql) return 0;
  try {
    db.exec(sql);
    const r = db.prepare('SELECT COUNT(*) as n FROM schedule_runs').get() as { n: number };
    return r?.n ?? 0;
  } catch {
    return 0;
  }
}

/**
 * Insert or replace a schedule run (for import from appcaire solve folder).
 */
export function upsertScheduleRun(run: Partial<ScheduleRun> & { id: string }): void {
  const stmt = db.prepare(`
    INSERT INTO schedule_runs (
      id, dataset, batch, algorithm, strategy, hypothesis, status,
      decision, decision_reason, timefold_score, routing_efficiency_pct,
      unassigned_visits, total_visits, unassigned_pct, continuity_avg, continuity_max,
      continuity_over_target, continuity_target, output_path, notes, iteration
    ) VALUES (
      @id, @dataset, @batch, @algorithm, @strategy, @hypothesis, @status,
      @decision, @decision_reason, @timefold_score, @routing_efficiency_pct,
      @unassigned_visits, @total_visits, @unassigned_pct, @continuity_avg, @continuity_max,
      @continuity_over_target, @continuity_target, @output_path, @notes, @iteration
    )
    ON CONFLICT(id) DO UPDATE SET
      dataset=excluded.dataset, batch=excluded.batch, algorithm=excluded.algorithm,
      strategy=excluded.strategy, hypothesis=excluded.hypothesis, status=excluded.status,
      decision=excluded.decision, decision_reason=excluded.decision_reason,
      timefold_score=excluded.timefold_score, routing_efficiency_pct=excluded.routing_efficiency_pct,
      unassigned_visits=excluded.unassigned_visits, total_visits=excluded.total_visits,
      unassigned_pct=excluded.unassigned_pct, continuity_avg=excluded.continuity_avg,
      continuity_max=excluded.continuity_max, continuity_over_target=excluded.continuity_over_target,
      continuity_target=excluded.continuity_target, output_path=excluded.output_path,
      notes=excluded.notes, iteration=excluded.iteration
  `);
  stmt.run({
    id: run.id,
    dataset: run.dataset ?? 'huddinge-2w-expanded',
    batch: run.batch ?? 'unknown',
    algorithm: run.algorithm ?? '',
    strategy: run.strategy ?? '',
    hypothesis: run.hypothesis ?? null,
    status: run.status ?? 'completed',
    decision: run.decision ?? null,
    decision_reason: run.decision_reason ?? null,
    timefold_score: run.timefold_score ?? null,
    routing_efficiency_pct: run.routing_efficiency_pct ?? null,
    unassigned_visits: run.unassigned_visits ?? null,
    total_visits: run.total_visits ?? null,
    unassigned_pct: run.unassigned_pct ?? null,
    continuity_avg: run.continuity_avg ?? null,
    continuity_max: run.continuity_max ?? null,
    continuity_over_target: run.continuity_over_target ?? null,
    continuity_target: run.continuity_target ?? 11,
    output_path: run.output_path ?? null,
    notes: run.notes ?? null,
    iteration: run.iteration ?? 1,
  });
}

// ─── Marketing ────────────────────────────────────────────────────────────────

export function getAllCampaigns(): (Campaign & { owner_name?: string; owner_emoji?: string })[] {
  return db
    .prepare(
      `SELECT c.*, a.name as owner_name, a.emoji as owner_emoji
       FROM campaigns c
       LEFT JOIN agents a ON c.owner = a.id
       ORDER BY c.created_at DESC`,
    )
    .all() as (Campaign & { owner_name?: string; owner_emoji?: string })[];
}

export function getAllLeads(): (Lead & { assigned_to_name?: string; assigned_to_emoji?: string })[] {
  return db
    .prepare(
      `SELECT l.*, a.name as assigned_to_name, a.emoji as assigned_to_emoji
       FROM leads l
       LEFT JOIN agents a ON l.assigned_to = a.id
       ORDER BY l.created_at DESC`,
    )
    .all() as (Lead & { assigned_to_name?: string; assigned_to_emoji?: string })[];
}

export function getAllContent(): (ContentPiece & {
  author_name?: string;
  author_emoji?: string;
  campaign_name?: string;
})[] {
  return db
    .prepare(
      `SELECT c.*, a.name as author_name, a.emoji as author_emoji, camp.name as campaign_name
       FROM content c
       LEFT JOIN agents a ON c.author = a.id
       LEFT JOIN campaigns camp ON c.campaign_id = camp.id
       ORDER BY c.created_at DESC`,
    )
    .all() as (ContentPiece & {
    author_name?: string;
    author_emoji?: string;
    campaign_name?: string;
  })[];
}

// ─── Lessons Learned ──────────────────────────────────────────────────────────

export function getLessonsLearned(limit = 20): LessonLearned[] {
  return db
    .prepare(
      `SELECT * FROM lessons_learned ORDER BY last_encountered_at DESC LIMIT ?`,
    )
    .all(limit) as LessonLearned[];
}

// ─── Dashboard Stats ──────────────────────────────────────────────────────────

export function getDashboardStats(): {
  totalSessions: number;
  activeSessions: number;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  totalAgents: number;
  activeAgents: number;
  totalExperiments: number;
  activeExperiments: number;
} {
  const sessions = db
    .prepare(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN status IN ('pending','in_progress') THEN 1 ELSE 0 END) as active
       FROM sessions`,
    )
    .get() as { total: number; active: number };

  const tasks = db
    .prepare(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
              SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
       FROM tasks`,
    )
    .get() as { total: number; completed: number; failed: number };

  const agents = db
    .prepare(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
       FROM agents`,
    )
    .get() as { total: number; active: number };

  const experiments = db
    .prepare(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
       FROM experiments`,
    )
    .get() as { total: number; active: number };

  return {
    totalSessions: sessions.total,
    activeSessions: sessions.active,
    totalTasks: tasks.total,
    completedTasks: tasks.completed,
    failedTasks: tasks.failed,
    totalAgents: agents.total,
    activeAgents: agents.active,
    totalExperiments: experiments.total,
    activeExperiments: experiments.active,
  };
}

// ─── Cleanup ──────────────────────────────────────────────────────────────────

export function closeDatabase(): void {
  db.close();
}

export { db };
