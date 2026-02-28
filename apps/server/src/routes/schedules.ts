/**
 * Schedule optimization API — pipeline of Timefold FSR runs
 * GET /api/schedule-runs — list runs (optional ?dataset=)
 * GET /api/schedule-runs/import-from-appcaire — import from appcaire/huddinge-datasets:
 *   reads manifest.json for run list and metadata, then for each run folder reads
 *   metrics/*.json (efficiency, unassigned) and *continuity*.csv (continuity_avg, continuity_max).
 *   Algorithm/strategy come from manifest or run folder name, never hardcoded.
 * POST /api/schedule-runs/:id/cancel — cancel run (Timefold DELETE + DB update)
 */
import { Router, type Request, type Response } from 'express';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve } from 'path';
import {
  getAllScheduleRuns,
  getScheduleRunById,
  cancelScheduleRun,
  upsertScheduleRun,
  runSeedScheduleRunsIfEmpty,
} from '../lib/database.js';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import { parseRunFromFolder } from '../lib/run-folder-parser.js';
import type { ScheduleRun } from '../types/index.js';

const router = Router();

const SOLVE_SUBPATH = 'docs_2.0/recurring-visits/huddinge-package/solve';
const HUDDINGE_DATASETS_DIR = 'huddinge-datasets';
const DEFAULT_DATASET = 'huddinge-2w-expanded';
const CONTINUITY_TARGET = 11;

function getAppcairePath(): string | null {
  const home = process.env.HOME || '';
  const root = getServiceRoot();
  const candidates: string[] = [];
  try {
    const appcaire = getRepoConfig('appcaire');
    if (appcaire?.path) candidates.push(appcaire.path);
  } catch {
    // config not found
  }
  if (home) {
    candidates.push(resolve(home, 'HomeCare/caire-platform/appcaire'));
    candidates.push(resolve(home, 'HomeCare/appcaire'));
  }
  candidates.push(resolve(root, '../caire-platform/appcaire'));
  candidates.push(resolve(root, '../../caire-platform/appcaire'));
  for (const p of candidates) {
    if (p && existsSync(p)) return p;
  }
  return null;
}

/** Shared folder: AgentWorkspace/huddinge-datasets (e.g. .../huddinge-datasets/28-feb). */
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
      continuity_max: null,
      continuity_over_target: null,
      continuity_target: CONTINUITY_TARGET,
      submitted_at: new Date().toISOString(),
      started_at: null,
      completed_at: null,
      cancelled_at: null,
      duration_seconds: null,
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

    // 1) Shared folder: AgentWorkspace/huddinge-datasets (e.g. .../huddinge-datasets/28-feb)
    const huddingePath = getHuddingeDatasetsPath();
    if (huddingePath) {
      sources.push(`huddinge-datasets: ${huddingePath}`);
      const entries = readdirSync(huddingePath, { withFileTypes: true });
      for (const ent of entries) {
        if (!ent.isDirectory()) continue;
        const batch = ent.name;
        if (batch.startsWith('.')) continue;
        const batchDir = resolve(huddingePath, batch);
        batchesScanned.push(`${batch} (shared)`);
        imported += importRunsFromBatchDir(batchDir, batch);
      }
    }

    // 2) Appcaire repo: .../solve/{batch}/manifest.json
    const appcairePath = process.env.APPCAIRE_PATH || getAppcairePath();
    if (appcairePath && existsSync(appcairePath)) {
      const solveDir = resolve(appcairePath, SOLVE_SUBPATH);
      if (existsSync(solveDir)) {
        sources.push(`appcaire solve: ${solveDir}`);
        const entries = readdirSync(solveDir, { withFileTypes: true });
        for (const ent of entries) {
          if (!ent.isDirectory()) continue;
          const batch = ent.name;
          if (batch.startsWith('.')) continue;
          const batchDir = resolve(solveDir, batch);
          if (!batchesScanned.includes(batch)) batchesScanned.push(batch);
          imported += importRunsFromBatchDir(batchDir, batch);
        }
      }
    }

    if (imported === 0 && sources.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'No dataset folder found. Use shared AgentWorkspace/huddinge-datasets (e.g. 28-feb/manifest.json), or set APPCAIRE_PATH / appcaire in config.',
        hint: 'HUDDINGE_DATASETS_PATH can point to the shared huddinge-datasets folder.',
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

router.get('/', (req: Request, res: Response) => {
  try {
    const dataset = req.query.dataset as string | undefined;
    let runs = getAllScheduleRuns(dataset);
    if (runs.length === 0) {
      runSeedScheduleRunsIfEmpty();
      runs = getAllScheduleRuns(dataset);
    }
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
