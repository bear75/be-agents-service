/**
 * Parse metrics JSON and continuity CSV from a schedule run folder (batch/run_id/).
 * Used by import-from-appcaire to fill efficiency, unassigned, continuity from dataset files
 * instead of hardcoded or manifest-only data.
 */
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve } from 'path';

const DEFAULT_CONTINUITY_TARGET = 11;

export interface ParsedMetrics {
  routing_efficiency_pct: number | null;
  unassigned_visits: number | null;
  total_visits: number | null;
  unassigned_pct: number | null;
  timefold_score: string | null;
}

export interface ParsedContinuity {
  continuity_avg: number | null;
  continuity_max: number | null;
  continuity_over_target: number | null;
  continuity_target: number;
}

/**
 * Find first metrics JSON in run dir: metrics/*.json or metrics_*.json in run root.
 */
function findMetricsJson(runDir: string): string | null {
  if (!existsSync(runDir)) return null;
  const metricsDir = resolve(runDir, 'metrics');
  if (existsSync(metricsDir)) {
    const files = readdirSync(metricsDir);
    const json = files.find((f) => f.endsWith('.json') && (f.startsWith('metrics_') || f.startsWith('metrics.')));
    if (json) return resolve(metricsDir, json);
    const anyJson = files.find((f) => f.endsWith('.json'));
    if (anyJson) return resolve(metricsDir, anyJson);
  }
  const entries = readdirSync(runDir);
  const rootJson = entries.find((f) => f.startsWith('metrics_') && f.endsWith('.json'));
  if (rootJson) return resolve(runDir, rootJson);
  return null;
}

/**
 * Parse metrics from appcaire metrics.py output JSON.
 * Fields: routing_efficiency_pct, unassigned_visits, total_visits_assigned, total_visits, unassigned_pct, score.
 */
export function parseMetricsFromRunDir(runDir: string): ParsedMetrics | null {
  const path = findMetricsJson(runDir);
  if (!path) return null;
  try {
    const raw = JSON.parse(readFileSync(path, 'utf8'));
    const unassigned = Number(raw.unassigned_visits) ?? 0;
    const totalAssigned = Number(raw.total_visits_assigned) ?? 0;
    const totalVisits = totalAssigned + unassigned;
    const unassignedPct = totalVisits > 0 ? (unassigned / totalVisits) * 100 : null;
    const score = raw.score;
    const timefold_score =
      score != null && String(score).trim() !== '' && String(score) !== 'N/A'
        ? String(score)
        : null;
    return {
      routing_efficiency_pct: raw.routing_efficiency_pct != null ? Number(raw.routing_efficiency_pct) : null,
      unassigned_visits: Number.isFinite(unassigned) ? unassigned : null,
      total_visits: totalVisits > 0 ? totalVisits : null,
      unassigned_pct: unassignedPct != null && Number.isFinite(unassignedPct) ? unassignedPct : null,
      timefold_score,
    };
  } catch {
    return null;
  }
}

/**
 * Find first continuity CSV in run dir: *continuity*.csv in run root or run_dir/metrics/.
 */
function findContinuityCsv(runDir: string): string | null {
  if (!existsSync(runDir)) return null;
  const check = (dir: string): string | null => {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      if (e.isFile() && e.name.toLowerCase().includes('continuity') && e.name.endsWith('.csv'))
        return resolve(dir, e.name);
    }
    return null;
  };
  const inRoot = check(runDir);
  if (inRoot) return inRoot;
  const metricsDir = resolve(runDir, 'metrics');
  if (existsSync(metricsDir)) return check(metricsDir);
  return null;
}

/**
 * Parse continuity CSV. Supports:
 * - Summary row: header contains continuity_avg, continuity_max (or avg, max)
 * - Per-client: one numeric column (distinct_caregivers, n_vehicles, continuity, count) — we compute avg/max
 */
export function parseContinuityFromRunDir(
  runDir: string,
  continuityTarget: number = DEFAULT_CONTINUITY_TARGET,
): ParsedContinuity | null {
  const path = findContinuityCsv(runDir);
  if (!path) return null;
  try {
    const text = readFileSync(path, 'utf8').trim();
    const lines = text.split(/\r?\n/).filter((l) => l.trim());
    if (lines.length < 2) return null;
    const header = lines[0].split(',').map((h) => h.trim().toLowerCase());
    const dataRows = lines.slice(1);

    const idxAvg = header.findIndex((h) => h === 'continuity_avg' || h === 'avg' || h === 'average');
    const idxMax = header.findIndex((h) => h === 'continuity_max' || h === 'max');
    if (idxAvg >= 0 && idxMax >= 0) {
      const first = dataRows[0].split(',').map((c) => c.trim());
      const avg = parseFloat(first[idxAvg]);
      const max = parseFloat(first[idxMax]);
      if (!Number.isFinite(avg) || !Number.isFinite(max)) return null;
      let overTarget = 0;
      const overIdx = header.findIndex((h) => h === 'continuity_over_target' || h === 'over_target');
      if (overIdx >= 0 && first[overIdx] !== undefined) overTarget = parseInt(first[overIdx], 10) || 0;
      else if (dataRows.length > 1) {
        const countCol = header.findIndex((h) => h === 'distinct_caregivers' || h === 'n_vehicles' || h === 'continuity' || h === 'count');
        if (countCol >= 0) {
          overTarget = dataRows.filter((r) => {
            const v = parseFloat(r.split(',')[countCol]);
            return Number.isFinite(v) && v > continuityTarget;
          }).length;
        }
      }
      return {
        continuity_avg: avg,
        continuity_max: Math.round(max),
        continuity_over_target: overTarget,
        continuity_target: continuityTarget,
      };
    }

    const countCol = header.findIndex(
      (h) =>
        h === 'distinct_caregivers' ||
        h === 'n_vehicles' ||
        h === 'continuity' ||
        h === 'count' ||
        h === 'vehicles',
    );
    if (countCol < 0) return null;
    const values: number[] = [];
    for (const row of dataRows) {
      const cells = row.split(',');
      const v = parseFloat(cells[countCol]?.trim() ?? '');
      if (Number.isFinite(v)) values.push(v);
    }
    if (values.length === 0) return null;
    const sum = values.reduce((a, b) => a + b, 0);
    const continuity_avg = sum / values.length;
    const continuity_max = Math.round(Math.max(...values));
    const continuity_over_target = values.filter((v) => v > continuityTarget).length;
    return {
      continuity_avg,
      continuity_max,
      continuity_over_target,
      continuity_target: continuityTarget,
    };
  } catch {
    return null;
  }
}

/**
 * Build run record from run folder: id = dir name, metrics + continuity from files,
 * algorithm/strategy from manifest entry or fallback to run_id / "imported".
 */
export function parseRunFromFolder(
  batchDir: string,
  runId: string,
  batch: string,
  dataset: string,
  manifestEntry?: { algorithm?: string; strategy?: string; hypothesis?: string } | null,
  continuityTarget: number = DEFAULT_CONTINUITY_TARGET,
): {
  id: string;
  dataset: string;
  batch: string;
  algorithm: string;
  strategy: string;
  hypothesis: string | null;
  status: 'completed';
  routing_efficiency_pct: number | null;
  unassigned_visits: number | null;
  total_visits: number | null;
  unassigned_pct: number | null;
  timefold_score: string | null;
  continuity_avg: number | null;
  continuity_max: number | null;
  continuity_over_target: number | null;
  continuity_target: number;
  output_path: string | null;
} {
  const runDir = resolve(batchDir, runId);
  const metrics = parseMetricsFromRunDir(runDir);
  const continuity = parseContinuityFromRunDir(runDir, continuityTarget);

  const algorithm = manifestEntry?.algorithm ?? runId ?? 'imported';
  const strategy = manifestEntry?.strategy ?? runId ?? 'imported';
  const hypothesis = manifestEntry?.hypothesis ?? null;

  let output_path: string | null = null;
  if (existsSync(runDir)) {
    if (existsSync(resolve(runDir, 'output.json'))) output_path = resolve(runDir, 'output.json');
    else if (existsSync(resolve(runDir, 'metrics'))) output_path = resolve(runDir, 'metrics');
  }

  return {
    id: runId,
    dataset,
    batch,
    algorithm,
    strategy,
    hypothesis,
    status: 'completed',
    routing_efficiency_pct: metrics?.routing_efficiency_pct ?? null,
    unassigned_visits: metrics?.unassigned_visits ?? null,
    total_visits: metrics?.total_visits ?? null,
    unassigned_pct: metrics?.unassigned_pct ?? null,
    timefold_score: metrics?.timefold_score ?? null,
    continuity_avg: continuity?.continuity_avg ?? null,
    continuity_max: continuity?.continuity_max ?? null,
    continuity_over_target: continuity?.continuity_over_target ?? null,
    continuity_target: continuity?.continuity_target ?? continuityTarget,
    output_path,
  };
}
