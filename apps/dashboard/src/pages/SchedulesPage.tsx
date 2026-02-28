/**
 * Schedule optimization — pipeline, scatter plot, runs table
 * Target: unassigned <1%, continuity ≤11, routing efficiency ≥70%
 */
import { useEffect, useState } from 'react';
import { PagePurpose } from '../components/PagePurpose';
import { getScheduleRuns, importScheduleRunsFromAppcaire } from '../lib/api';
import type { ScheduleRun } from '../types';
import { PipelineBoard } from '../components/schedules/PipelineBoard';
import { ScatterPlot } from '../components/schedules/ScatterPlot';
import { RunDetailPanel } from '../components/schedules/RunDetailPanel';

const DATASET = 'huddinge-2w-expanded';

function toNum(v: unknown): number | null {
  if (v == null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
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
    continuity_max: toNum(r.continuity_max) ?? r.continuity_max,
    continuity_over_target: toNum(r.continuity_over_target) ?? r.continuity_over_target,
    continuity_target: toNum(r.continuity_target) ?? r.continuity_target,
  };
}

export function SchedulesPage() {
  const [runs, setRuns] = useState<ScheduleRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

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

  const syncFromAppcaire = async () => {
    setSyncing(true);
    setError(null);
    try {
      const result = await importScheduleRunsFromAppcaire();
      if (result?.success) {
        await load();
      } else {
        setError(result?.error ?? 'Sync failed');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const selectedRun = selectedId ? runs.find((r) => r.id === selectedId) : null;

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Schedule optimization pipeline."
        how="Timefold FSR runs: queued → running → completed/cancelled. Scatter: continuity vs unassigned %. Goal: unassigned &lt;1%, continuity ≤11, efficiency ≥70%."
        tip="Use the loop script to dispatch parallel runs and cancel non-promising ones early."
      />
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Schedule optimization — {DATASET}
        </h2>
        <span className="flex items-center gap-2">
          <button
            type="button"
            onClick={syncFromAppcaire}
            disabled={syncing || loading}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50"
          >
            {syncing ? 'Syncing…' : 'Sync from appcaire'}
          </button>
          <button
            type="button"
            onClick={load}
            disabled={loading}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50"
          >
            {loading ? 'Loading…' : 'Refresh'}
          </button>
        </span>
      </div>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading && runs.length === 0 ? (
        <div className="text-gray-500">Loading runs…</div>
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Pipeline</h3>
              <PipelineBoard
                runs={runs}
                selectedId={selectedId}
                onSelectRun={setSelectedId}
              />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Scatter (continuity vs unassigned %)</h3>
              <ScatterPlot
                runs={runs}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            </div>
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
            <h3 className="text-sm font-medium text-gray-700 mb-2">Runs table</h3>
            <table className="min-w-full text-sm border border-gray-200 rounded-lg">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-2 font-medium">ID</th>
                  <th className="text-left p-2 font-medium">Algorithm</th>
                  <th className="text-left p-2 font-medium">Status</th>
                  <th className="text-right p-2 font-medium">Eff %</th>
                  <th className="text-right p-2 font-medium">Unassigned %</th>
                  <th className="text-right p-2 font-medium">Continuity</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr
                    key={r.id}
                    className="border-t border-gray-100 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedId(selectedId === r.id ? null : r.id)}
                  >
                    <td className="p-2 font-mono">{r.id}</td>
                    <td className="p-2">{r.algorithm}</td>
                    <td className="p-2">{r.status}</td>
                    <td className="p-2 text-right">
                      {r.routing_efficiency_pct != null ? r.routing_efficiency_pct.toFixed(1) : '—'}
                    </td>
                    <td className="p-2 text-right">
                      {r.unassigned_pct != null ? r.unassigned_pct.toFixed(2) : '—'}
                    </td>
                    <td className="p-2 text-right">
                      {r.continuity_avg != null ? r.continuity_avg.toFixed(1) : '—'}
                    </td>
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
