/**
 * Schedule optimization — single runs table (status + metrics) and scatter plot.
 * Target: unassigned <1%, continuity ≤11, routing efficiency ≥70%
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PagePurpose } from '../components/PagePurpose';
import { getScheduleRuns, importScheduleRunsFromAppcaire } from '../lib/api';
import type { ScheduleRun } from '../types';
import { ScatterPlot } from '../components/schedules/ScatterPlot';
import { RunDetailPanel } from '../components/schedules/RunDetailPanel';

const STATUS_STYLE: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-800',
};

const DATASET = 'huddinge-2w-expanded';

function toNum(v: unknown): number | null {
  if (v == null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

/** Format for table: show number or — (handles API strings) */
function fmtNum(v: unknown, decimals: number): string {
  const n = toNum(v);
  return n != null ? (decimals === 0 ? String(Math.round(n)) : n.toFixed(decimals)) : '—';
}

/** Ensure metric fields are numbers (API may send strings from SQLite) */
function normalizeRun(r: ScheduleRun): ScheduleRun {
  return {
    ...r,
    routing_efficiency_pct: toNum(r.routing_efficiency_pct) ?? r.routing_efficiency_pct,
    unassigned_visits: toNum(r.unassigned_visits) ?? r.unassigned_visits,
    total_visits: toNum(r.total_visits) ?? r.total_visits,
    unassigned_pct: toNum(r.unassigned_pct) ?? r.unassigned_pct,
    continuity_avg: toNum(r.continuity_avg) ?? r.continuity_avg,
    continuity_median: toNum(r.continuity_median) ?? r.continuity_median,
    continuity_visit_weighted_avg: toNum(r.continuity_visit_weighted_avg) ?? r.continuity_visit_weighted_avg,
    continuity_max: toNum(r.continuity_max) ?? r.continuity_max,
    continuity_over_target: toNum(r.continuity_over_target) ?? r.continuity_over_target,
    continuity_target: toNum(r.continuity_target) ?? r.continuity_target,
    input_shifts: toNum(r.input_shifts) ?? r.input_shifts,
    input_shift_hours: toNum(r.input_shift_hours) ?? r.input_shift_hours,
    output_shifts_trimmed: toNum(r.output_shifts_trimmed) ?? r.output_shifts_trimmed,
    output_shift_hours_trimmed: toNum(r.output_shift_hours_trimmed) ?? r.output_shift_hours_trimmed,
    shift_hours_total: toNum(r.shift_hours_total) ?? r.shift_hours_total,
    shift_hours_idle: toNum(r.shift_hours_idle) ?? r.shift_hours_idle,
    efficiency_all_pct: toNum(r.efficiency_all_pct) ?? r.efficiency_all_pct,
    efficiency_min_visit_pct: toNum(r.efficiency_min_visit_pct) ?? r.efficiency_min_visit_pct,
    efficiency_visit_span_pct: toNum(r.efficiency_visit_span_pct) ?? r.efficiency_visit_span_pct,
  };
}

export function SchedulesPage() {
  const [runs, setRuns] = useState<ScheduleRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getScheduleRuns(DATASET);
      setRuns(data.map(normalizeRun));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load runs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  /** Sync from shared dataset (huddinge-datasets) then reload list — single action for "latest data". */
  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await importScheduleRunsFromAppcaire();
      if (result?.success === false) setError(result?.error ?? 'Sync failed');
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Refresh failed');
    } finally {
      setLoading(false);
    }
  };

  const selectedRun = selectedId ? runs.find((r) => r.id === selectedId) : null;

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Schedule optimization pipeline."
        how="Single table: all runs with status. Scatter: efficiency % (Y) vs continuity (X). Goal: top-left (eff ≥70%, continuity ≤11)."
        tip="Use the loop script to dispatch parallel runs and cancel non-promising ones early."
      />
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Schedule optimization — {DATASET}
        </h2>
        <button
          type="button"
          onClick={refresh}
          disabled={loading}
          className="text-sm text-blue-600 hover:underline disabled:opacity-50"
        >
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading && runs.length === 0 ? (
        <div className="text-gray-500">Loading runs…</div>
      ) : runs.length === 0 ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-6 text-center text-sm text-amber-900">
          <p className="font-medium">No runs in this dataset.</p>
          <p className="mt-1 text-amber-800">
            Click <strong>Refresh</strong> above to import from the shared huddinge-datasets folder (or seed sample runs).
          </p>
        </div>
      ) : (
        <>
          {runs.filter((r) => r.status === 'completed' && r.routing_efficiency_pct != null).length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-gray-50/80 p-3 text-sm">
              <h3 className="font-medium text-gray-700 mb-2">Metrics summary (completed runs)</h3>
              {(() => {
                const withMetrics = runs.filter(
                  (r) => r.status === 'completed' && r.routing_efficiency_pct != null && r.continuity_avg != null && r.unassigned_pct != null
                );
                const n = withMetrics.length;
                const avgEff = withMetrics.reduce((s, r) => s + (r.routing_efficiency_pct ?? 0), 0) / n;
                const avgCont = withMetrics.reduce((s, r) => s + (r.continuity_avg ?? 0), 0) / n;
                const avgUn = withMetrics.reduce((s, r) => s + (r.unassigned_pct ?? 0), 0) / n;
                const meeting = withMetrics.filter(
                  (r) => (r.unassigned_pct ?? 99) < 1 && (r.continuity_avg ?? 99) <= 11 && (r.routing_efficiency_pct ?? 0) >= 70
                ).length;
                return (
                  <p className="text-gray-600">
                    <span className="font-medium text-gray-800">{n}</span> runs with metrics —
                    efficiency avg <span className="font-medium">{avgEff.toFixed(1)}%</span>,
                    continuity avg <span className="font-medium">{avgCont.toFixed(1)}</span>,
                    unassigned avg <span className="font-medium">{avgUn.toFixed(2)}%</span>
                    {meeting > 0 && (
                      <> · <span className="text-green-700 font-medium">{meeting} meeting goal</span> (unassigned &lt;1%, continuity ≤11, eff ≥70%)</>
                    )}
                  </p>
                );
              })()}
            </div>
          )}

          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Scatter (efficiency % vs continuity)</h3>
            <ScatterPlot
              runs={runs}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>

          {selectedRun && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Run detail</h3>
              <RunDetailPanel
                run={selectedRun}
                onClose={() => setSelectedId(null)}
                onCancel={load}
              />
            </div>
          )}

          <div className="overflow-x-auto">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Runs</h3>
            <table className="min-w-full text-sm border border-gray-200 rounded-lg">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-2 font-medium">ID</th>
                  <th className="text-left p-2 font-medium">Status</th>
                  <th className="text-right p-2 font-medium">In shifts</th>
                  <th className="text-right p-2 font-medium" title="Before trim (incl idle)">Shift h total</th>
                  <th className="text-right p-2 font-medium" title="Idle / empty shift hours">Shift h idle</th>
                  <th className="text-right p-2 font-medium" title="Removed all idle, early end">Shift h trimmed</th>
                  <th className="text-right p-2 font-medium" title="Visit / (shift − break). All shifts.">Eff all %</th>
                  <th className="text-right p-2 font-medium" title="Exclude empty shifts only">Eff min visit %</th>
                  <th className="text-right p-2 font-medium" title="Visit-span only (shift = first→last visit)">Eff visit span %</th>
                  <th className="text-right p-2 font-medium">Unassigned %</th>
                  <th className="text-right p-2 font-medium" title="Visit-weighted continuity">Cont.</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr
                    key={r.id}
                    className="border-t border-gray-100 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedId(selectedId === r.id ? null : r.id)}
                  >
                    <td className="p-2 font-mono">
                      <Link to={`/schedules/run/${r.id}`} className="text-blue-600 hover:underline" onClick={(e) => e.stopPropagation()}>
                        {r.id}
                      </Link>
                    </td>
                    <td className="p-2">
                      <span className={`inline-flex px-1.5 py-0.5 rounded text-xs font-medium ${STATUS_STYLE[r.status] ?? 'bg-gray-100 text-gray-600'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="p-2 text-right">{fmtNum(r.input_shifts, 0)}</td>
                    <td className="p-2 text-right">{fmtNum(r.shift_hours_total, 0)}</td>
                    <td className="p-2 text-right">{fmtNum(r.shift_hours_idle, 0)}</td>
                    <td className="p-2 text-right">{fmtNum(r.output_shift_hours_trimmed, 0)}</td>
                    <td className="p-2 text-right">{fmtNum(r.efficiency_all_pct, 1)}</td>
                    <td className="p-2 text-right">{fmtNum(r.efficiency_min_visit_pct, 1)}</td>
                    <td className="p-2 text-right">{fmtNum(r.efficiency_visit_span_pct, 1)}</td>
                    <td className="p-2 text-right">{fmtNum(r.unassigned_pct, 2)}</td>
                    <td className="p-2 text-right">{fmtNum(r.continuity_visit_weighted_avg, 1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
