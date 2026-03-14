/**
 * Schedule optimization — single runs table (status + metrics) and scatter plot.
 * Target: unassigned <1%, continuity ≤11, routing efficiency ≥70%
 */
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { PagePurpose } from '../components/PagePurpose';
import { getScheduleRuns, importScheduleRunsFromAppcaire, getAvailableDatasets, clearScheduleRuns } from '../lib/api';
import type { ScheduleRun, Dataset } from '../types';
import { ScatterPlot } from '../components/schedules/ScatterPlot';
import { RunDetailPanel } from '../components/schedules/RunDetailPanel';
import { ArrowUpDown } from 'lucide-react';

const STATUS_STYLE: Record<string, string> = {
  queued: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-800',
};

const SOURCE_STYLE: Record<string, string> = {
  manual: 'bg-gray-100 text-gray-700',
  research_loop: 'bg-purple-100 text-purple-800',
};

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

/** Format date for table: show time or — */
function fmtDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
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

type SortField = 'submitted_at' | 'status' | 'continuity_avg' | 'unassigned_pct' | 'efficiency';
type SortDirection = 'asc' | 'desc';

export function SchedulesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [runs, setRuns] = useState<ScheduleRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState(searchParams.get('dataset') || 'huddinge-2w-expanded');
  const [sortField, setSortField] = useState<SortField>('submitted_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [clearedMessage, setClearedMessage] = useState<string | null>(null);

  const loadDatasets = async () => {
    try {
      const data = await getAvailableDatasets();
      setDatasets(data);
    } catch (e) {
      console.error('Failed to load datasets:', e);
    }
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getScheduleRuns(selectedDataset);
      setRuns(data.map(normalizeRun));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load runs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    load();
  }, [selectedDataset]);

  // Update URL when dataset changes
  useEffect(() => {
    if (selectedDataset !== (searchParams.get('dataset') || 'huddinge-2w-expanded')) {
      setSearchParams({ dataset: selectedDataset });
    }
  }, [selectedDataset]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedRuns = [...runs].sort((a, b) => {
    let aVal: any;
    let bVal: any;

    switch (sortField) {
      case 'submitted_at':
        aVal = new Date(a.submitted_at).getTime();
        bVal = new Date(b.submitted_at).getTime();
        break;
      case 'status':
        aVal = a.status;
        bVal = b.status;
        break;
      case 'continuity_avg':
        aVal = a.continuity_avg ?? 999;
        bVal = b.continuity_avg ?? 999;
        break;
      case 'unassigned_pct':
        aVal = a.unassigned_pct ?? 999;
        bVal = b.unassigned_pct ?? 999;
        break;
      case 'efficiency':
        aVal = a.routing_efficiency_pct ?? 0;
        bVal = b.routing_efficiency_pct ?? 0;
        break;
    }

    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

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

  /** Delete all runs (start fresh with new formats/schedules). */
  const clearAll = async () => {
    if (!window.confirm('Delete all schedule runs? This cannot be undone.')) return;
    setLoading(true);
    setError(null);
    setClearedMessage(null);
    try {
      const { deleted } = await clearScheduleRuns();
      setSelectedId(null);
      setRuns([]);
      setClearedMessage(deleted > 0 ? `Cleared ${deleted} run(s).` : 'No runs to clear.');
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to clear runs');
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
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Schedule Optimization
          </h2>
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {datasets.length > 0 ? (
              datasets.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  {ds.name}
                </option>
              ))
            ) : (
              <option value={selectedDataset}>{selectedDataset}</option>
            )}
          </select>
        </div>
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={refresh}
            disabled={loading}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50"
          >
            {loading ? 'Refreshing…' : 'Refresh'}
          </button>
          <button
            type="button"
            onClick={clearAll}
            disabled={loading}
            className="text-sm text-red-600 hover:underline disabled:opacity-50"
          >
            Clear all runs
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {clearedMessage && (
        <div className="rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">
          {clearedMessage}
        </div>
      )}

      {loading && runs.length === 0 ? (
        <div className="text-gray-500">Loading runs…</div>
      ) : runs.length === 0 ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-6 text-center text-sm text-amber-900">
          <p className="font-medium">No runs yet.</p>
          <p className="mt-1 text-amber-800">
            Trigger a run from Schedule Research, or click Refresh to import from the shared huddinge-datasets folder.
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
                  <th className="text-left p-2 font-medium">
                    <button
                      onClick={() => handleSort('submitted_at')}
                      className="flex items-center gap-1 hover:text-blue-600"
                    >
                      ID <ArrowUpDown className="w-3 h-3" />
                    </button>
                  </th>
                  <th className="text-left p-2 font-medium">
                    <button
                      onClick={() => handleSort('status')}
                      className="flex items-center gap-1 hover:text-blue-600"
                    >
                      Status <ArrowUpDown className="w-3 h-3" />
                    </button>
                  </th>
                  <th className="text-left p-2 font-medium">Source</th>
                  <th className="text-left p-2 font-medium text-xs">Submitted</th>
                  <th className="text-left p-2 font-medium text-xs">Started</th>
                  <th className="text-left p-2 font-medium text-xs">Completed</th>
                  <th className="text-right p-2 font-medium">In shifts</th>
                  <th className="text-right p-2 font-medium" title="Before trim (incl idle)">Shift h total</th>
                  <th className="text-right p-2 font-medium" title="Idle / empty shift hours">Shift h idle</th>
                  <th className="text-right p-2 font-medium" title="Removed all idle, early end">Shift h trimmed</th>
                  <th className="text-right p-2 font-medium" title="Visit / (shift − break). All shifts.">
                    <button
                      onClick={() => handleSort('efficiency')}
                      className="flex items-center gap-1 hover:text-blue-600 ml-auto"
                    >
                      Eff all % <ArrowUpDown className="w-3 h-3" />
                    </button>
                  </th>
                  <th className="text-right p-2 font-medium" title="Exclude empty shifts only">Eff min visit %</th>
                  <th className="text-right p-2 font-medium" title="Visit-span only (shift = first→last visit)">Eff visit span %</th>
                  <th className="text-right p-2 font-medium">
                    <button
                      onClick={() => handleSort('unassigned_pct')}
                      className="flex items-center gap-1 hover:text-blue-600 ml-auto"
                    >
                      Unassigned % <ArrowUpDown className="w-3 h-3" />
                    </button>
                  </th>
                  <th className="text-right p-2 font-medium" title="Visit-weighted continuity">
                    <button
                      onClick={() => handleSort('continuity_avg')}
                      className="flex items-center gap-1 hover:text-blue-600 ml-auto"
                    >
                      Cont. <ArrowUpDown className="w-3 h-3" />
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedRuns.map((r) => (
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
                    <td className="p-2">
                      <span className={`inline-flex px-1.5 py-0.5 rounded text-xs font-medium ${SOURCE_STYLE[r.source || 'manual']}`}>
                        {r.source === 'research_loop' ? '🔬 AI' : '👤 Manual'}
                      </span>
                    </td>
                    <td className="p-2 text-xs text-gray-600">{fmtDate(r.submitted_at)}</td>
                    <td className="p-2 text-xs text-gray-600">{fmtDate(r.started_at)}</td>
                    <td className="p-2 text-xs text-gray-600">{fmtDate(r.completed_at)}</td>
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
