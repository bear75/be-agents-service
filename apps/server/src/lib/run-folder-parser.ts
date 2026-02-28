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
  input_shifts: number | null;
  input_shift_hours: number | null;
  output_shifts_trimmed: number | null;
  output_shift_hours_trimmed: number | null;
  shift_hours_total: number | null;
  shift_hours_idle: number | null;
  efficiency_total_pct: number | null;
  efficiency_trimmed_pct: number | null;
}

export interface ParsedContinuity {
  continuity_avg: number | null;
  continuity_median: number | null;
  continuity_visit_weighted_avg: number | null;
  continuity_max: number | null;
  continuity_over_target: number | null;
  continuity_target: number;
}

/**
 * Compute total scheduled shift hours from run_dir/input.json (modelInput.vehicles[].shifts[].minStartTime/maxEndTime).
 */
function getInputShiftHours(runDir: string): number | null {
  const path = resolve(runDir, 'input.json');
  if (!existsSync(path)) return null;
  try {
    const raw = JSON.parse(readFileSync(path, 'utf8'));
    const vehicles = (raw.modelInput ?? raw).vehicles ?? [];
    let totalMs = 0;
    for (const v of vehicles) {
      for (const s of v.shifts ?? []) {
        const start = s.minStartTime ? new Date(s.minStartTime).getTime() : NaN;
        const end = s.maxEndTime ? new Date(s.maxEndTime).getTime() : NaN;
        if (Number.isFinite(start) && Number.isFinite(end) && end >= start) totalMs += end - start;
      }
    }
    if (totalMs <= 0) return null;
    return totalMs / (1000 * 3600);
  } catch {
    return null;
  }
}

/**
 * Find metrics JSON in run dir. Prefers file with efficiency_all_pct (merged format).
 */
function findMetricsJson(runDir: string): string | null {
  if (!existsSync(runDir)) return null;
  const metricsDir = resolve(runDir, 'metrics');
  if (existsSync(metricsDir)) {
    const files = readdirSync(metricsDir)
      .filter((f) => f.endsWith('.json') && (f.startsWith('metrics_') || f.startsWith('metrics.')))
      .sort();
    for (const f of files) {
      const p = resolve(metricsDir, f);
      try {
        const raw = JSON.parse(readFileSync(p, 'utf8'));
        if (raw.efficiency_all_pct != null || raw.system_efficiency_pct != null) return p;
      } catch {
        // skip
      }
    }
    if (files.length > 0) return resolve(metricsDir, files[0]);
    const anyJson = readdirSync(metricsDir).find((f) => f.endsWith('.json'));
    if (anyJson) return resolve(metricsDir, anyJson);
  }
  const entries = readdirSync(runDir);
  const rootJson = entries.find((f) => f.startsWith('metrics_') && f.endsWith('.json'));
  if (rootJson) return resolve(runDir, rootJson);
  return null;
}

/**
 * Read 3 efficiency values from single metrics.json (merged format).
 * 1. All shifts and hours (base)
 * 2. Min 1 visit (exclude empty shifts only)
 * 3. Visit-span only (shift = first visit start → last visit end)
 */
export function getThreeEfficiencies(runDir: string): {
  efficiency_all_pct: number | null;
  efficiency_min_visit_pct: number | null;
  efficiency_visit_span_pct: number | null;
} {
  const path = findMetricsJson(runDir);
  if (!path) return { efficiency_all_pct: null, efficiency_min_visit_pct: null, efficiency_visit_span_pct: null };
  try {
    const raw = JSON.parse(readFileSync(path, 'utf8'));
    const n = (v: unknown) => (v != null && Number.isFinite(Number(v)) ? Number(v) : null);
    return {
      efficiency_all_pct: n(raw.efficiency_all_pct ?? raw.system_efficiency_pct),
      efficiency_min_visit_pct: n(raw.efficiency_min_visit_pct),
      efficiency_visit_span_pct: n(raw.efficiency_visit_span_pct),
    };
  } catch {
    return { efficiency_all_pct: null, efficiency_min_visit_pct: null, efficiency_visit_span_pct: null };
  }
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
    const inputSummary = raw.input_summary as { shifts?: number } | undefined;
    const inputShifts = inputSummary?.shifts != null ? Number(inputSummary.shifts) : null;
    const shiftTimeH = raw.shift_time_h != null ? Number(raw.shift_time_h) : null;
    const inactiveTimeH = raw.inactive_time_h != null ? Number(raw.inactive_time_h) : null;
    const shiftsWithVisits = raw.shifts_with_visits != null ? Number(raw.shifts_with_visits) : null;
    const outputShiftHoursTrimmed =
      shiftTimeH != null && inactiveTimeH != null && Number.isFinite(shiftTimeH) && Number.isFinite(inactiveTimeH)
        ? shiftTimeH - inactiveTimeH
        : null;
    const visitTimeH = raw.visit_time_h != null ? Number(raw.visit_time_h) : null;
    const efficiencyTotalPct =
      shiftTimeH != null && visitTimeH != null && shiftTimeH > 0 && Number.isFinite(visitTimeH)
        ? (visitTimeH / shiftTimeH) * 100
        : null;
    const efficiencyTrimmedPct =
      outputShiftHoursTrimmed != null && visitTimeH != null && outputShiftHoursTrimmed > 0 && Number.isFinite(visitTimeH)
        ? (visitTimeH / outputShiftHoursTrimmed) * 100
        : null;
    return {
      routing_efficiency_pct: raw.routing_efficiency_pct != null ? Number(raw.routing_efficiency_pct) : null,
      unassigned_visits: Number.isFinite(unassigned) ? unassigned : null,
      total_visits: totalVisits > 0 ? totalVisits : null,
      unassigned_pct: unassignedPct != null && Number.isFinite(unassignedPct) ? unassignedPct : null,
      timefold_score,
      input_shifts: Number.isFinite(inputShifts) ? inputShifts : null,
      input_shift_hours: null,
      output_shifts_trimmed: Number.isFinite(shiftsWithVisits) ? shiftsWithVisits : null,
      output_shift_hours_trimmed: outputShiftHoursTrimmed != null && Number.isFinite(outputShiftHoursTrimmed) ? outputShiftHoursTrimmed : null,
      shift_hours_total: shiftTimeH != null && Number.isFinite(shiftTimeH) ? shiftTimeH : null,
      shift_hours_idle: inactiveTimeH != null && Number.isFinite(inactiveTimeH) ? inactiveTimeH : null,
      efficiency_total_pct: efficiencyTotalPct,
      efficiency_trimmed_pct: efficiencyTrimmedPct,
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
        continuity_median: null,
        continuity_visit_weighted_avg: null,
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
    const visitsCol = header.findIndex((h) => h === 'nr_visits' || h === 'visits' || h === 'n_visits');
    if (countCol < 0) return null;
    const pairs: { c: number; visits: number }[] = [];
    for (const row of dataRows) {
      const cells = row.split(',');
      const c = parseFloat(cells[countCol]?.trim() ?? '');
      if (!Number.isFinite(c)) continue;
      const visits = visitsCol >= 0 ? parseInt(cells[visitsCol]?.trim() ?? '1', 10) : 1;
      pairs.push({ c, visits: Number.isFinite(visits) && visits > 0 ? visits : 1 });
    }
    if (pairs.length === 0) return null;
    const values = pairs.map((p) => p.c);
    const sum = values.reduce((a, b) => a + b, 0);
    const continuity_avg = sum / values.length;
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    const continuity_median = sorted.length % 2 === 1 ? sorted[mid]! : (sorted[mid - 1]! + sorted[mid]!) / 2;
    const totalWeight = pairs.reduce((a, p) => a + p.visits, 0);
    const weightedSum = pairs.reduce((a, p) => a + p.c * p.visits, 0);
    const continuity_visit_weighted_avg = totalWeight > 0 ? weightedSum / totalWeight : continuity_avg;
    const continuity_max = Math.round(Math.max(...values));
    const continuity_over_target = values.filter((v) => v > continuityTarget).length;
    return {
      continuity_avg,
      continuity_median,
      continuity_visit_weighted_avg,
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
  continuity_median: number | null;
  continuity_visit_weighted_avg: number | null;
  continuity_max: number | null;
  continuity_over_target: number | null;
  continuity_target: number;
  input_shifts: number | null;
  input_shift_hours: number | null;
  output_shifts_trimmed: number | null;
  output_shift_hours_trimmed: number | null;
  shift_hours_total: number | null;
  shift_hours_idle: number | null;
  efficiency_total_pct: number | null;
  efficiency_trimmed_pct: number | null;
  output_path: string | null;
} {
  const runDir = resolve(batchDir, runId);
  const metrics = parseMetricsFromRunDir(runDir);
  const continuity = parseContinuityFromRunDir(runDir, continuityTarget);
  const inputShiftHours = getInputShiftHours(runDir);

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
    continuity_median: continuity?.continuity_median ?? null,
    continuity_visit_weighted_avg: continuity?.continuity_visit_weighted_avg ?? null,
    continuity_max: continuity?.continuity_max ?? null,
    continuity_over_target: continuity?.continuity_over_target ?? null,
    continuity_target: continuity?.continuity_target ?? continuityTarget,
    input_shifts: metrics?.input_shifts ?? null,
    input_shift_hours: inputShiftHours ?? metrics?.input_shift_hours ?? null,
    output_shifts_trimmed: metrics?.output_shifts_trimmed ?? null,
    output_shift_hours_trimmed: metrics?.output_shift_hours_trimmed ?? null,
    shift_hours_total: metrics?.shift_hours_total ?? null,
    shift_hours_idle: metrics?.shift_hours_idle ?? null,
    efficiency_total_pct: metrics?.efficiency_total_pct ?? null,
    efficiency_trimmed_pct: metrics?.efficiency_trimmed_pct ?? null,
    output_path,
  };
}
