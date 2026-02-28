/**
 * Schedule optimization — pipeline, scatter plot, runs table
 * Target: unassigned <1%, continuity ≤11, routing efficiency ≥70%
 */
import { useEffect, useState } from 'react';
import { PagePurpose } from '../components/PagePurpose';
import { getScheduleRuns } from '../lib/api';
import type { ScheduleRun } from '../types';
import { PipelineBoard } from '../components/schedules/PipelineBoard';
import { ScatterPlot } from '../components/schedules/ScatterPlot';
import { RunDetailPanel } from '../components/schedules/RunDetailPanel';

const DATASET = 'huddinge-2w-expanded';

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
      setRuns(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load runs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

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
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="text-sm text-blue-600 hover:underline disabled:opacity-50"
        >
          {loading ? 'Loading…' : 'Refresh'}
        </button>
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
