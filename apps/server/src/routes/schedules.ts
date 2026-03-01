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
import {
  getAllScheduleRuns,
  getScheduleRunById,
  cancelScheduleRun,
  upsertScheduleRun,
  runSeedScheduleRunsIfEmpty,
} from '../lib/database.js';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { parseRunFromFolder, getThreeEfficiencies } from '../lib/run-folder-parser.js';
import type { ScheduleRun } from '../types/index.js';

const router = Router();

const HUDDINGE_DATASETS_DIR = 'huddinge-datasets';

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
    upsertScheduleRun({
      ...parsed,
      decision: null,
      decision_reason: null,
      submitted_at: new Date().toISOString(),
      started_at: null,
      completed_at: null,
      cancelled_at: null,
      duration_seconds: null,
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

    // Shared folder only: AgentWorkspace/huddinge-datasets (e.g. .../huddinge-datasets/28-feb)
    const huddingePath = getHuddingeDatasetsPath();
    if (huddingePath) {
      sources.push(`huddinge-datasets: ${huddingePath}`);
      const entries = readdirSync(huddingePath, { withFileTypes: true });
      for (const ent of entries) {
        if (!ent.isDirectory()) continue;
        const batch = ent.name;
        if (batch.startsWith('.')) continue;
        const batchDir = resolve(huddingePath, batch);
        batchesScanned.push(batch);
        imported += importRunsFromBatchDir(batchDir, batch);
      }
    }

    if (imported === 0 && sources.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'No shared dataset folder found. Use AgentWorkspace/huddinge-datasets (e.g. 28-feb/ with run subdirs and metrics/continuity files).',
        hint: 'Set HUDDINGE_DATASETS_PATH to the shared huddinge-datasets folder, or configure darwin.workspace.path in config/repos.yaml.',
      });
    }

    if (imported === 0) {
      const seeded = runSeedScheduleRunsIfEmpty(true);
      if (seeded > 0) {
        return res.json({
          success: true,
          data: {
            success: true,
            imported: 0,
            seeded,
            sources,
            batchesScanned,
            message: `No manifest.json with runs in scanned folders; seeded ${seeded} sample run(s). Refresh the page.`,
          },
        });
      }
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
    if (runs.length === 0) {
      runSeedScheduleRunsIfEmpty();
      runs = getAllScheduleRuns(dataset);
    }
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

export default router;
