/**
 * Schedule optimization API — pipeline of Timefold FSR runs
 * GET /api/schedule-runs — list runs (optional ?dataset=)
 * GET /api/schedule-runs/import-from-appcaire — import from shared huddinge-datasets only:
 *   scans HUDDINGE_DATASETS_PATH (or AgentWorkspace/huddinge-datasets), reads manifest.json
 *   and each run folder’s metrics/*.json and *continuity*.csv. Algorithm/strategy from manifest or run id.
 * POST /api/schedule-runs/:id/cancel — cancel run (Timefold DELETE + DB update)
 */
import { Router, type Request, type Response } from 'express';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawn, type ChildProcess } from 'child_process';
import {
  getAllScheduleRuns,
  getScheduleRunById,
  cancelScheduleRun,
  upsertScheduleRun,
  deleteAllScheduleRuns,
  getResearchState,
  createResearchState,
  updateResearchState,
  getResearchHistory,
  getResearchLearnings,
} from '../lib/database.js';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { parseRunFromFolder, getThreeEfficiencies } from '../lib/run-folder-parser.js';
import type { ResearchState, ScheduleRun } from '../types/index.js';

const router = Router();

/** Delete all schedule runs — must be registered before any /:id route so POST /clear is not matched as /:id. */
router.post('/clear', (_req: Request, res: Response) => {
  try {
    const deleted = deleteAllScheduleRuns();
    res.json({ success: true, data: { deleted } });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to clear schedule runs',
    });
  }
});

const HUDDINGE_DATASETS_DIR = 'huddinge-datasets';

/** Only this batch folder is imported; old batches (e.g. 28-feb) are ignored so the dashboard shows only new runs. */
const IMPORT_BATCH_NAME = process.env.SCHEDULE_IMPORT_BATCH || 'current';

/** Repo-local datasets path: from this file (routes/schedules) up to repo root, then recurring-visits/... */
const REPO_LOCAL_DATASETS = (() => {
  try {
    const __dirname = dirname(fileURLToPath(import.meta.url));
    return resolve(__dirname, '..', '..', '..', '..', 'recurring-visits', 'huddinge-package', 'huddinge-datasets');
  } catch {
    return '';
  }
})();
const DEFAULT_DATASET = 'huddinge-2w-expanded';
const CONTINUITY_TARGET = 11;

/** Shared folder: AgentWorkspace/huddinge-datasets (e.g. .../huddinge-datasets/28-feb). Import uses this only, not appcaire. */
function getHuddingeDatasetsPath(): string | null {
  const envPath = process.env.HUDDINGE_DATASETS_PATH;
  if (envPath && existsSync(envPath)) return envPath;
  try {
    const darwin = getRepoConfig('darwin');
    const workspacePath = darwin?.workspace?.path ?? darwin?.path;
    if (workspacePath) {
      const p = resolve(workspacePath, '..', HUDDINGE_DATASETS_DIR);
      if (existsSync(p)) return p;
    }
  } catch {
    // config not found
  }
  const home = process.env.HOME || '';
  if (home) {
    const p = resolve(home, 'Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace', HUDDINGE_DATASETS_DIR);
    if (existsSync(p)) return p;
  }
  try {
    const root = getServiceRoot();
    const localDatasets = resolve(root, 'recurring-visits', 'huddinge-package', 'huddinge-datasets');
    if (existsSync(localDatasets)) return localDatasets;
  } catch {
    // ignore
  }
  return null;
}

/** Manifest run entry: optional algorithm, strategy, hypothesis per run id */
interface ManifestRun {
  id: string;
  algorithm?: string;
  strategy?: string;
  hypothesis?: string;
  [key: string]: unknown;
}

/**
 * Import runs from a batch dir: read manifest.json for run list and metadata,
 * then for each run read metrics from run_folder/metrics/*.json and
 * continuity from run_folder/*continuity*.csv. Algorithm/strategy from manifest or run folder name.
 */
function importRunsFromBatchDir(batchDir: string, batch: string): number {
  const manifestPath = resolve(batchDir, 'manifest.json');
  const manifestRuns: Record<string, { algorithm?: string; strategy?: string; hypothesis?: string }> = {};
  if (existsSync(manifestPath)) {
    try {
      const raw = JSON.parse(readFileSync(manifestPath, 'utf8'));
      const runs: ManifestRun[] = Array.isArray(raw.runs)
        ? raw.runs
        : raw.runs && typeof raw.runs === 'object'
          ? Object.entries(raw.runs).map(([id, r]) => ({ ...(r as object), id } as ManifestRun))
          : [];
      for (const r of runs) {
        if (r.id) {
          manifestRuns[r.id] = {
            algorithm: r.algorithm,
            strategy: r.strategy,
            hypothesis: r.hypothesis,
          };
        }
      }
    } catch {
      // ignore malformed manifest
    }
  }

  const runIds = new Set<string>(Object.keys(manifestRuns));
  if (!existsSync(batchDir)) return runIds.size ? importRunsFromManifestOnly(batchDir, batch, manifestRuns) : 0;

  try {
    const entries = readdirSync(batchDir, { withFileTypes: true });
    for (const e of entries) {
      if (e.isDirectory() && !e.name.startsWith('.')) {
        const runDir = resolve(batchDir, e.name);
        try {
          const files = readdirSync(runDir, { withFileTypes: true });
          const hasMetrics =
            files.some((f) => f.name === 'metrics' && f.isDirectory()) ||
            files.some((f) => f.isFile() && f.name.startsWith('metrics_') && f.name.endsWith('.json'));
          const hasOutput = existsSync(resolve(runDir, 'output.json'));
          const hasContinuity = files.some(
            (f) => f.isFile() && f.name.toLowerCase().includes('continuity') && f.name.endsWith('.csv'),
          );
          const inMetrics = existsSync(resolve(runDir, 'metrics'))
            ? readdirSync(resolve(runDir, 'metrics')).some((f) => f.toLowerCase().includes('continuity') && f.endsWith('.csv'))
            : false;
          if (hasMetrics || hasOutput || hasContinuity || inMetrics) runIds.add(e.name);
        } catch {
          // skip unreadable run dir
        }
      }
    }
  } catch {
    // batch dir not listable
  }

  let n = 0;
  for (const runId of runIds) {
    const manifestEntry = manifestRuns[runId];
    const parsed = parseRunFromFolder(
      batchDir,
      runId,
      batch,
      DEFAULT_DATASET,
      manifestEntry ?? null,
      CONTINUITY_TARGET,
    );
    const existing = getScheduleRunById(runId);
    const now = new Date().toISOString();
    upsertScheduleRun({
      ...parsed,
      decision: null,
      decision_reason: null,
      submitted_at: existing?.submitted_at ?? now,
      started_at: existing?.started_at ?? null,
      completed_at: existing?.completed_at ?? null,
      cancelled_at: existing?.cancelled_at ?? null,
      duration_seconds: existing?.duration_seconds ?? null,
      notes: null,
      iteration: 1,
    });
    n += 1;
  }

  if (n === 0 && Object.keys(manifestRuns).length > 0) {
    return importRunsFromManifestOnly(batchDir, batch, manifestRuns);
  }
  return n;
}

function importRunsFromManifestOnly(
  batchDir: string,
  batch: string,
  manifestRuns: Record<string, { algorithm?: string; strategy?: string; hypothesis?: string }>,
): number {
  let n = 0;
  for (const [id, meta] of Object.entries(manifestRuns)) {
    upsertScheduleRun({
      id,
      dataset: DEFAULT_DATASET,
      batch,
      algorithm: meta.algorithm ?? id,
      strategy: meta.strategy ?? id,
      hypothesis: meta.hypothesis ?? null,
      status: 'completed',
      decision: null,
      decision_reason: null,
      timefold_score: null,
      routing_efficiency_pct: null,
      unassigned_visits: null,
      total_visits: null,
      unassigned_pct: null,
      continuity_avg: null,
      continuity_median: null,
      continuity_visit_weighted_avg: null,
      continuity_max: null,
      continuity_over_target: null,
      continuity_target: CONTINUITY_TARGET,
      input_shifts: null,
      input_shift_hours: null,
      output_shifts_trimmed: null,
      output_shift_hours_trimmed: null,
      output_path: null,
      notes: null,
      iteration: 1,
    });
    n += 1;
  }
  return n;
}

router.get('/import-from-appcaire', (req: Request, res: Response) => {
  try {
    let imported = 0;
    const batchesScanned: string[] = [];
    const sources: string[] = [];

    // Only import from huddinge-datasets/current (or SCHEDULE_IMPORT_BATCH); old batches like 28-feb are ignored.
    const huddingePath = getHuddingeDatasetsPath();
    if (huddingePath) {
      const batchDir = resolve(huddingePath, IMPORT_BATCH_NAME);
      if (existsSync(batchDir)) {
        sources.push(`huddinge-datasets/${IMPORT_BATCH_NAME}: ${batchDir}`);
        batchesScanned.push(IMPORT_BATCH_NAME);
        imported += importRunsFromBatchDir(batchDir, IMPORT_BATCH_NAME);
      } else {
        sources.push(`huddinge-datasets: ${huddingePath} (import batch "${IMPORT_BATCH_NAME}" not found)`);
      }
    }

    if (imported === 0 && sources.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'No shared dataset folder found. Use huddinge-datasets/current/ for new runs (see docs/SCHEDULE_RUNS_DATA_SOURCE.md).',
        hint: 'Set HUDDINGE_DATASETS_PATH to the huddinge-datasets root, or use repo recurring-visits/huddinge-package/huddinge-datasets/current/.',
      });
    }

    if (imported === 0) {
      return res.json({
        success: true,
        data: {
          success: true,
          imported: 0,
          sources,
          batchesScanned,
          message: `No runs in ${IMPORT_BATCH_NAME}/. Add run folders (and manifest.json) to huddinge-datasets/${IMPORT_BATCH_NAME}/, or trigger a run from Schedule Research.`,
        },
      });
    }

    res.json({
      success: true,
      data: {
        success: true,
        imported,
        sources,
        batchesScanned,
        message: imported > 0 ? `Imported ${imported} run(s).` : 'No manifest.json with runs in batch folders. Add manifest or run seed script.',
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Import failed',
    });
  }
});

/**
 * Register or update a run row directly (used by live submit/poll scripts).
 * This allows in-progress runs to appear before folder-based import.
 */
router.post('/register', (req: Request, res: Response) => {
  try {
    const body = (req.body ?? {}) as Partial<ScheduleRun> & {
      route_plan_id?: string;
      batch?: string;
      algorithm?: string;
      strategy?: string;
      notes?: string;
      timefold_score?: string;
    };

    const rawId = String(body.id ?? '').trim();
    if (!rawId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: id',
      });
    }

    const id = rawId.includes('-') ? rawId.split('-')[0] : rawId;
    const now = new Date().toISOString();
    const allowedStatuses = new Set(['queued', 'running', 'completed', 'cancelled', 'failed']);
    const status = String(body.status ?? 'queued');
    if (!allowedStatuses.has(status)) {
      return res.status(400).json({
        success: false,
        error: `Invalid status '${status}'. Allowed: ${Array.from(allowedStatuses).join(', ')}`,
      });
    }

    const existing = getScheduleRunById(id);
    const routePlanId = String(body.route_plan_id ?? rawId).trim();
    const noteParts = [
      String(body.notes ?? '').trim(),
      routePlanId && routePlanId !== id ? `route_plan_id=${routePlanId}` : '',
    ].filter(Boolean);

    upsertScheduleRun({
      id,
      dataset: body.dataset ?? existing?.dataset ?? DEFAULT_DATASET,
      batch: body.batch ?? existing?.batch ?? new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }).replace(' ', '-').toLowerCase(),
      algorithm: body.algorithm ?? existing?.algorithm ?? id,
      strategy: body.strategy ?? existing?.strategy ?? 'manual-submit',
      hypothesis: body.hypothesis ?? existing?.hypothesis ?? null,
      status: status as ScheduleRun['status'],
      decision: body.decision ?? existing?.decision ?? null,
      decision_reason: body.decision_reason ?? existing?.decision_reason ?? null,
      timefold_score: body.timefold_score ?? existing?.timefold_score ?? null,
      routing_efficiency_pct: body.routing_efficiency_pct ?? existing?.routing_efficiency_pct ?? null,
      unassigned_visits: body.unassigned_visits ?? existing?.unassigned_visits ?? null,
      total_visits: body.total_visits ?? existing?.total_visits ?? null,
      unassigned_pct: body.unassigned_pct ?? existing?.unassigned_pct ?? null,
      continuity_avg: body.continuity_avg ?? existing?.continuity_avg ?? null,
      continuity_median: body.continuity_median ?? existing?.continuity_median ?? null,
      continuity_visit_weighted_avg: body.continuity_visit_weighted_avg ?? existing?.continuity_visit_weighted_avg ?? null,
      continuity_max: body.continuity_max ?? existing?.continuity_max ?? null,
      continuity_over_target: body.continuity_over_target ?? existing?.continuity_over_target ?? null,
      continuity_target: body.continuity_target ?? existing?.continuity_target ?? CONTINUITY_TARGET,
      input_shifts: body.input_shifts ?? existing?.input_shifts ?? null,
      input_shift_hours: body.input_shift_hours ?? existing?.input_shift_hours ?? null,
      output_shifts_trimmed: body.output_shifts_trimmed ?? existing?.output_shifts_trimmed ?? null,
      output_shift_hours_trimmed: body.output_shift_hours_trimmed ?? existing?.output_shift_hours_trimmed ?? null,
      shift_hours_total: body.shift_hours_total ?? existing?.shift_hours_total ?? null,
      shift_hours_idle: body.shift_hours_idle ?? existing?.shift_hours_idle ?? null,
      efficiency_total_pct: body.efficiency_total_pct ?? existing?.efficiency_total_pct ?? null,
      efficiency_trimmed_pct: body.efficiency_trimmed_pct ?? existing?.efficiency_trimmed_pct ?? null,
      submitted_at: body.submitted_at ?? existing?.submitted_at ?? now,
      started_at:
        body.started_at
        ?? existing?.started_at
        ?? (status === 'running' ? now : null),
      completed_at:
        body.completed_at
        ?? existing?.completed_at
        ?? (status === 'completed' || status === 'failed' ? now : null),
      cancelled_at:
        body.cancelled_at
        ?? existing?.cancelled_at
        ?? (status === 'cancelled' ? now : null),
      duration_seconds: body.duration_seconds ?? existing?.duration_seconds ?? null,
      output_path: body.output_path ?? existing?.output_path ?? null,
      notes: noteParts.length > 0 ? noteParts.join(' | ') : (existing?.notes ?? null),
      iteration: body.iteration ?? existing?.iteration ?? 1,
    });

    const run = getScheduleRunById(id);
    res.json({
      success: true,
      data: { run },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to register run',
    });
  }
});

router.get('/', (req: Request, res: Response) => {
  try {
    const dataset = req.query.dataset as string | undefined;
    let runs = getAllScheduleRuns(dataset);
    runs = runs.map(augmentRunWithVariantMetrics);
    res.json({
      success: true,
      data: { runs },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch schedule runs',
    });
  }
});

/**
 * Research state routes MUST be registered before /:id so that
 * GET/POST /research/state are not matched by /:id (id="research").
 */
router.get('/research/datasets', (req: Request, res: Response) => {
  try {
    const dataDir = resolve(getServiceRoot(), 'recurring-visits/data');
    const entries = readdirSync(dataDir, { withFileTypes: true });

    const datasets = entries
      .filter(e => e.isDirectory() && !e.name.startsWith('.') && e.name !== 'archive')
      .map(e => {
        const datasetDir = resolve(dataDir, e.name);
        const rawDir = resolve(datasetDir, 'raw');
        const inputDir = resolve(datasetDir, 'input');

        let csvFile: string | null = null;
        if (existsSync(rawDir)) {
          const files = readdirSync(rawDir);
          csvFile = files.find((f: string) => f.endsWith('.csv')) || null;
        }

        let hasInputJson = false;
        if (existsSync(inputDir)) {
          const files = readdirSync(inputDir);
          hasInputJson = files.some((f: string) => f.endsWith('.json'));
        }

        const hasData = csvFile !== null || hasInputJson;

        return {
          id: e.name,
          name: e.name.charAt(0).toUpperCase() + e.name.slice(1),
          path: datasetDir,
          csv_file: csvFile,
          has_data: hasData,
        };
      });

    res.json({
      success: true,
      data: datasets,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to list datasets',
    });
  }
});

router.get('/research/state', (req: Request, res: Response) => {
  try {
    const dataset = (req.query.dataset as string) || 'huddinge-v3';

    let state = getResearchState(dataset);

    if (!state) {
      state = createResearchState({
        dataset,
        programVersion: process.env.GIT_HASH || 'dev',
      });
    }

    const history = getResearchHistory(dataset, 50);
    const learnings = getResearchLearnings(dataset);

    res.json({
      success: true,
      data: {
        state,
        history,
        learnings,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get research state',
    });
  }
});

/**
 * POST /api/schedule-runs/research/state
 * Body: { dataset, updates } — updates are merged into research_state (e.g. iteration_count, best_*).
 */
router.post('/research/state', (req: Request, res: Response) => {
  try {
    const dataset = String((req.body?.dataset as string) || 'huddinge-v3').trim();
    const updates = (req.body?.updates as Record<string, unknown>) || {};

    if (Object.keys(updates).length === 0) {
      return res.json({ success: true, data: { updated: false } });
    }

    let state = getResearchState(dataset);
    if (!state) {
      state = createResearchState({
        dataset,
        programVersion: process.env.GIT_HASH || 'dev',
      });
    }

    updateResearchState(dataset, updates as Partial<ResearchState>);
    const updated = getResearchState(dataset);
    res.json({ success: true, data: { state: updated, updated: true } });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to update research state',
    });
  }
});

/** Resolve run folder path from shared huddinge-datasets (batch/run_id). Returns null if run not in DB or folder missing. */
function getRunFolderPath(runId: string): { basePath: string; run: ScheduleRun } | null {
  const run = getScheduleRunById(runId);
  if (!run?.batch) return null;
  const base = getHuddingeDatasetsPath();
  if (!base) return null;
  const basePath = resolve(base, run.batch, runId);
  return existsSync(basePath) ? { basePath, run } : null;
}

const DATASETS_RELATIVE = ['recurring-visits', 'huddinge-package', 'huddinge-datasets'] as const;

/** All candidate base paths for huddinge-datasets (try cwd first, then __dirname, then config). */
function getDatasetsBaseCandidates(): string[] {
  const seen = new Set<string>();
  const add = (p: string) => {
    const norm = resolve(p);
    if (norm && existsSync(norm) && !seen.has(norm)) {
      seen.add(norm);
      return norm;
    }
    return null;
  };
  const bases: string[] = [];
  const cwd = process.cwd();
  const fromCwd = add(resolve(cwd, ...DATASETS_RELATIVE));
  if (fromCwd) bases.push(fromCwd);
  const fromCwdUp = add(resolve(cwd, '..', ...DATASETS_RELATIVE));
  if (fromCwdUp) bases.push(fromCwdUp);
  const fromCwdUp2 = add(resolve(cwd, '..', '..', ...DATASETS_RELATIVE));
  if (fromCwdUp2) bases.push(fromCwdUp2);
  if (REPO_LOCAL_DATASETS) {
    const fromDirname = add(REPO_LOCAL_DATASETS);
    if (fromDirname) bases.push(fromDirname);
  }
  const primary = getHuddingeDatasetsPath();
  if (primary) {
    const p = add(primary);
    if (p) bases.push(p);
  }
  try {
    const local = resolve(getServiceRoot(), ...DATASETS_RELATIVE);
    const l = add(local);
    if (l) bases.push(l);
  } catch {
    // ignore
  }
  return bases;
}

/** Augment run with 3 efficiency values from single metrics.json (merged format). */
function augmentRunWithVariantMetrics(run: ScheduleRun): ScheduleRun {
  if (!run.batch) return run;
  const tryEff = (runDir: string) => {
    if (!existsSync(runDir)) return null;
    const v = getThreeEfficiencies(runDir);
    const hasAny =
      v.efficiency_all_pct != null ||
      v.efficiency_min_visit_pct != null ||
      v.efficiency_visit_span_pct != null;
    if (!hasAny) return null;
    return {
      ...run,
      efficiency_all_pct: v.efficiency_all_pct,
      efficiency_min_visit_pct: v.efficiency_min_visit_pct,
      efficiency_visit_span_pct: v.efficiency_visit_span_pct,
    };
  };
  const cwd = process.cwd();
  for (const base of [
    resolve(cwd, ...DATASETS_RELATIVE),
    resolve(cwd, '..', ...DATASETS_RELATIVE),
    resolve(cwd, '..', '..', ...DATASETS_RELATIVE),
    REPO_LOCAL_DATASETS,
  ]) {
    if (!base || !existsSync(base)) continue;
    const runDir = resolve(base, run.batch, run.id);
    const out = tryEff(runDir);
    if (out) return out;
  }
  try {
    const root = getServiceRoot();
    const runDir = resolve(root, ...DATASETS_RELATIVE, run.batch, run.id);
    const out = tryEff(runDir);
    if (out) return out;
  } catch {
    // ignore
  }
  for (const base of getDatasetsBaseCandidates()) {
    const runDir = resolve(base, run.batch, run.id);
    const out = tryEff(runDir);
    if (out) return out;
  }
  return run;
}

function findFirstFile(dir: string, predicate: (name: string) => boolean): string | null {
  if (!existsSync(dir)) return null;
  const name = readdirSync(dir).find(predicate);
  return name ? resolve(dir, name) : null;
}

/** GET run metrics JSON (from run folder metrics/metrics_*.json) */
router.get('/:id/files/metrics-json', (req: Request, res: Response) => {
  try {
    const resolved = getRunFolderPath(req.params.id);
    if (!resolved) {
      return res.status(404).json({ success: false, error: 'Run or run folder not found' });
    }
    const metricsDir = resolve(resolved.basePath, 'metrics');
    const path = findFirstFile(metricsDir, (f) => f.endsWith('.json') && (f.startsWith('metrics_') || f.startsWith('metrics.')))
      ?? findFirstFile(metricsDir, (f) => f.endsWith('.json'));
    if (!path) return res.status(404).json({ success: false, error: 'No metrics JSON in run folder' });
    const raw = readFileSync(path, 'utf8');
    const data = JSON.parse(raw);
    res.setHeader('Content-Type', 'application/json');
    res.send(raw);
  } catch (e) {
    res.status(500).json({ success: false, error: e instanceof Error ? e.message : 'Failed to read metrics JSON' });
  }
});

/** GET run metrics report text (metrics_report_*.txt) */
router.get('/:id/files/metrics-report', (req: Request, res: Response) => {
  try {
    const resolved = getRunFolderPath(req.params.id);
    if (!resolved) return res.status(404).json({ success: false, error: 'Run or run folder not found' });
    const metricsDir = resolve(resolved.basePath, 'metrics');
    const path = findFirstFile(metricsDir, (f) => f.startsWith('metrics_report_') && f.endsWith('.txt'));
    if (!path) return res.status(404).json({ success: false, error: 'No metrics report in run folder' });
    const text = readFileSync(path, 'utf8');
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.send(text);
  } catch (e) {
    res.status(500).json({ success: false, error: e instanceof Error ? e.message : 'Failed to read report' });
  }
});

/** GET run continuity CSV */
router.get('/:id/files/continuity', (req: Request, res: Response) => {
  try {
    const resolved = getRunFolderPath(req.params.id);
    if (!resolved) return res.status(404).json({ success: false, error: 'Run or run folder not found' });
    const check = (d: string) => {
      if (!existsSync(d)) return null;
      const name = readdirSync(d).find((f) => f.toLowerCase().includes('continuity') && f.endsWith('.csv'));
      return name ? resolve(d, name) : null;
    };
    const path = check(resolved.basePath) ?? check(resolve(resolved.basePath, 'metrics'));
    if (!path) return res.status(404).json({ success: false, error: 'No continuity CSV in run folder' });
    const text = readFileSync(path, 'utf8');
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.send(text);
  } catch (e) {
    res.status(500).json({ success: false, error: e instanceof Error ? e.message : 'Failed to read continuity CSV' });
  }
});

/** GET dataset-level asset (e.g. pilot report PDF) from shared folder root */
router.get('/dataset-assets/:filename', (req: Request, res: Response) => {
  try {
    const base = getHuddingeDatasetsPath();
    if (!base) return res.status(404).json({ success: false, error: 'Shared dataset folder not configured' });
    const filename = req.params.filename.replace(/[^a-zA-Z0-9._-]/g, '');
    const path = resolve(base, filename);
    const baseResolved = resolve(base);
    if (!existsSync(path) || !path.startsWith(baseResolved)) return res.status(404).json({ success: false, error: 'File not found' });
    res.sendFile(path, { maxAge: 3600 }, (err) => {
      if (err && !res.headersSent) res.status(500).json({ success: false, error: 'Failed to send file' });
    });
  } catch (e) {
    res.status(500).json({ success: false, error: e instanceof Error ? e.message : 'Failed to serve asset' });
  }
});

/** GET single run by id (variant metrics read from run folder JSON, not DB) */
router.get('/:id', (req: Request, res: Response) => {
  try {
    const run = getScheduleRunById(req.params.id);
    if (!run) return res.status(404).json({ success: false, error: 'Run not found' });
    const augmented = augmentRunWithVariantMetrics(run);
    res.json({ success: true, data: { run: augmented } });
  } catch (e) {
    res.status(500).json({ success: false, error: e instanceof Error ? e.message : 'Failed to fetch run' });
  }
});

router.post('/:id/cancel', (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const reason = (req.body?.reason as string) || 'Cancelled by user';
    const existing = getScheduleRunById(id);
    if (!existing) {
      return res.status(404).json({ success: false, error: 'Run not found' });
    }
    if (existing.status !== 'running' && existing.status !== 'queued') {
      return res.status(400).json({
        success: false,
        error: `Run is ${existing.status}; only running or queued can be cancelled`,
      });
    }
    const updated = cancelScheduleRun(id, reason);
    res.json({ success: true, data: updated });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to cancel run',
    });
  }
});

// ============================================================================
// RESEARCH API ENDPOINTS (Schedule Research Loop)
// ============================================================================

// Track running research jobs
const runningJobs = new Map<string, { process: ChildProcess; dataset: string; startedAt: string }>();

/**
 * POST /api/research/trigger
 * Start research loop in background
 * Body: { dataset, max_iterations?, strategies? }
 */
router.post('/research/trigger', (req: Request, res: Response) => {
  try {
    const { dataset = 'huddinge-v3', max_iterations = 50, strategies, dry_run = false } = req.body as {
      dataset?: string;
      max_iterations?: number;
      strategies?: string[];
      dry_run?: boolean;
    };

    // Check if already running
    const existingJob = Array.from(runningJobs.values()).find(j => j.dataset === dataset);
    if (existingJob) {
      return res.status(409).json({
        success: false,
        error: `Research already running for dataset: ${dataset}`,
        job_id: Array.from(runningJobs.entries()).find(([, v]) => v === existingJob)?.[0],
      });
    }

    // Initialize or get research state
    let state = getResearchState(dataset);
    if (!state) {
      state = createResearchState({
        dataset,
        programVersion: process.env.GIT_HASH || 'dev',
      });
    }

    // Update state to running
    updateResearchState(dataset, {
      current_status: 'running',
      current_job_id: null,
      current_experiment_id: null,
    });

    // Spawn research loop script
    const scriptPath = resolve(getServiceRoot(), 'scripts/compound/schedule-research-loop.sh');
    const logPath = resolve(getServiceRoot(), 'logs/research', `${dataset}_${Date.now()}.log`);

    const args = [dataset, max_iterations.toString()];
    if (strategies && strategies.length > 0) {
      args.push(strategies.join(','));
    }

    const childProcess = spawn(scriptPath, args, {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        DATASET: dataset,
        MAX_ITERATIONS: max_iterations.toString(),
        DRY_RUN: dry_run ? 'true' : 'false',
      },
    });

    const job_id = `research_${dataset}_${Date.now()}`;

    // Track job
    runningJobs.set(job_id, {
      process: childProcess,
      dataset,
      startedAt: new Date().toISOString(),
    });

    // Handle process completion
    childProcess.on('close', (code: number | null) => {
      runningJobs.delete(job_id);
      const finalStatus = code === 0 ? 'completed' : 'failed';
      updateResearchState(dataset, {
        current_status: finalStatus,
      });
    });

    // Don't wait for process
    childProcess.unref();

    res.status(202).json({
      success: true,
      data: {
        job_id,
        dataset,
        max_iterations,
        status_url: `/api/research/status/${job_id}`,
        logs_url: `/api/research/logs/${job_id}`,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to trigger research',
    });
  }
});

/**
 * POST /api/research/cancel
 * Cancel running research loop
 * Body: { job_id }
 */
router.post('/research/cancel', (req: Request, res: Response) => {
  try {
    const { job_id } = req.body as { job_id: string };

    const job = runningJobs.get(job_id);
    if (!job) {
      return res.status(404).json({
        success: false,
        error: `Research job not found: ${job_id}`,
      });
    }

    // Kill process
    job.process.kill('SIGTERM');

    // Update state
    updateResearchState(job.dataset, {
      current_status: 'cancelled',
    });

    runningJobs.delete(job_id);

    res.json({
      success: true,
      message: `Research job cancelled: ${job_id}`,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to cancel research',
    });
  }
});

/**
 * GET /api/research/status/:job_id
 * Get status of running research job
 */
router.get('/research/status/:job_id', (req: Request, res: Response) => {
  try {
    const { job_id } = req.params;

    const job = runningJobs.get(job_id);
    if (!job) {
      return res.status(404).json({
        success: false,
        error: `Research job not found: ${job_id}`,
        message: 'Job may have completed or been cancelled',
      });
    }

    const state = getResearchState(job.dataset);

    res.json({
      success: true,
      data: {
        job_id,
        dataset: job.dataset,
        status: state?.current_status || 'running',
        started_at: job.startedAt,
        current_iteration: state?.iteration_count || 0,
        current_experiment: state?.current_experiment_id,
        current_job: state?.current_job_id,
        research_phase: state?.research_phase,
        plateau_count: state?.plateau_count || 0,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get research status',
    });
  }
});

/**
 * GET /api/research/logs/:job_id?tail=N
 * Get logs for research job
 */
router.get('/research/logs/:job_id', (req: Request, res: Response) => {
  try {
    const { job_id } = req.params;
    const tail = parseInt(req.query.tail as string) || 100;

    const job = runningJobs.get(job_id);
    if (!job) {
      return res.status(404).json({
        success: false,
        error: `Research job not found: ${job_id}`,
      });
    }

    const logPath = resolve(
      getServiceRoot(),
      'logs/research',
      `${job.dataset}_${job_id.split('_').pop()}.log`
    );

    if (!existsSync(logPath)) {
      return res.json({
        success: true,
        data: {
          logs: 'Log file not yet created',
          lines: 0,
        },
      });
    }

    const logContent = readFileSync(logPath, 'utf-8');
    const lines = logContent.split('\n');
    const tailedLines = lines.slice(-tail);

    res.json({
      success: true,
      data: {
        logs: tailedLines.join('\n'),
        lines: tailedLines.length,
        total_lines: lines.length,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get research logs',
    });
  }
});

/**
 * GET /api/research/running
 * Get all running research jobs
 */
router.get('/research/running', (req: Request, res: Response) => {
  try {
    const jobs = Array.from(runningJobs.entries()).map(([job_id, job]) => {
      const state = getResearchState(job.dataset);
      return {
        job_id,
        dataset: job.dataset,
        started_at: job.startedAt,
        current_iteration: state?.iteration_count || 0,
        status: state?.current_status || 'running',
      };
    });

    res.json({
      success: true,
      data: jobs,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get running jobs',
    });
  }
});

export default router;
