/**
 * Schedule Research Page - AI-powered autonomous optimization
 *
 * Orchestrates mathematician + specialist agents to explore optimization strategies,
 * evaluate results, and converge toward goal metrics.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PagePurpose } from '../components/PagePurpose';
import { getResearchState, getRunningResearchJobs, triggerResearchLoop, getAvailableDatasets } from '../lib/api';
import type { ResearchStateResponse, Dataset } from '../types';
import { Play, Square, RefreshCw, X, ExternalLink } from 'lucide-react';

const POLL_INTERVAL = 5000; // 5 seconds

export function ScheduleResearchPage() {
  const [state, setState] = useState<ResearchStateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggerDialogOpen, setTriggerDialogOpen] = useState(false);
  const [maxIterations, setMaxIterations] = useState(50);
  const [dryRun, setDryRun] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState('huddinge-v3');

  const loadDatasets = async () => {
    try {
      const data = await getAvailableDatasets();
      setDatasets(data);
    } catch (e) {
      console.error('Failed to load datasets:', e);
    }
  };

  const loadState = async () => {
    try {
      const data = await getResearchState(selectedDataset);
      setState(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load research state');
    } finally {
      setLoading(false);
    }
  };

  const handleTrigger = async () => {
    try {
      setTriggering(true);
      const result = await triggerResearchLoop({
        dataset: selectedDataset,
        max_iterations: maxIterations,
        dry_run: dryRun,
      });
      setTriggerDialogOpen(false);
      setSuccessMessage(`Research started! Job ID: ${result.job_id}${dryRun ? ' (DRY RUN)' : ''}`);

      // Optimistic update: immediately set status to running
      if (state) {
        setState({
          ...state,
          state: {
            ...state.state,
            current_status: 'running',
            current_job_id: result.job_id,
          },
        });
      }

      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
      // Reload state to sync with server
      setTimeout(loadState, 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to trigger research');
    } finally {
      setTriggering(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    loadState();
  }, [selectedDataset]);

  // Poll for status updates when research is running
  useEffect(() => {
    if (state?.state.current_status === 'running') {
      const interval = setInterval(() => {
        loadState();
      }, POLL_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [state?.state.current_status]);

  const isRunning = state?.state.current_status === 'running';

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="AI-powered schedule research - autonomous optimization loop."
        how="Mathematician agent proposes strategies → Specialist executes → Evaluate results → Learn & iterate."
        tip="Goals: continuity ≤11, unassigned <1%, efficiency ≥70%. Loop stops when goals met or max iterations reached."
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Schedule Research
          </h2>
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {datasets.map((ds) => (
              <option key={ds.id} value={ds.id} disabled={!ds.has_data}>
                {ds.name} {!ds.has_data ? '(no data)' : ''}
              </option>
            ))}
          </select>
          <Link
            to={`/schedules?dataset=${selectedDataset}`}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
          >
            View All Runs <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={loadState}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {!isRunning && (
            <button
              type="button"
              onClick={() => setTriggerDialogOpen(true)}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
            >
              <Play className="w-4 h-4" />
              Start Research
            </button>
          )}
          {isRunning && (
            <button
              type="button"
              onClick={() => {/* TODO: Cancel research */}}
              className="flex items-center gap-1.5 px-4 py-1.5 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700"
            >
              <Square className="w-4 h-4" />
              Cancel
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">
          ✓ {successMessage}
        </div>
      )}

      {loading && !state ? (
        <div className="text-gray-500">Loading research state…</div>
      ) : !state ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-6 text-center text-sm text-amber-900">
          <p className="font-medium">No research state found.</p>
          <p className="mt-1 text-amber-800">
            Click <strong>Start Research</strong> to initialize the research loop.
          </p>
        </div>
      ) : (
        <>
          {/* Status Card */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Current Status</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-500">Status</div>
                <div className={`mt-1 inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                  state.state.current_status === 'running' ? 'bg-blue-100 text-blue-800' :
                  state.state.current_status === 'completed' ? 'bg-green-100 text-green-800' :
                  state.state.current_status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {state.state.current_status}
                </div>
              </div>
              <div>
                <div className="text-gray-500">Iteration</div>
                <div className="mt-1 font-medium">{state.state.iteration_count}</div>
              </div>
              <div>
                <div className="text-gray-500">Phase</div>
                <div className="mt-1 font-medium">{state.state.research_phase}</div>
              </div>
              <div>
                <div className="text-gray-500">Plateau Count</div>
                <div className="mt-1 font-medium">{state.state.plateau_count}</div>
              </div>
            </div>
            {state.state.current_job_id && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="text-gray-500 text-xs">Current Job ID</div>
                <div className="mt-1 font-mono text-xs">{state.state.current_job_id}</div>
              </div>
            )}
          </div>

          {/* Best Result Card */}
          {state.state.best_job_id && (
            <div className="rounded-lg border border-green-200 bg-green-50 p-4">
              <h3 className="text-sm font-medium text-green-900 mb-3">Best Result</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-green-700">Continuity (avg)</div>
                  <div className="mt-1 font-medium text-green-900">{state.state.best_continuity_avg?.toFixed(2) ?? '—'}</div>
                </div>
                <div>
                  <div className="text-green-700">Continuity (max)</div>
                  <div className="mt-1 font-medium text-green-900">{state.state.best_continuity_max ?? '—'}</div>
                </div>
                <div>
                  <div className="text-green-700">Unassigned</div>
                  <div className="mt-1 font-medium text-green-900">{state.state.best_unassigned_pct?.toFixed(2) ?? '—'}%</div>
                </div>
                <div>
                  <div className="text-green-700">Efficiency</div>
                  <div className="mt-1 font-medium text-green-900">{state.state.best_efficiency_pct?.toFixed(1) ?? '—'}%</div>
                </div>
              </div>
              {state.state.best_achieved_at && (
                <div className="mt-3 pt-3 border-t border-green-200">
                  <div className="text-green-700 text-xs">Achieved at</div>
                  <div className="mt-1 text-xs">{new Date(state.state.best_achieved_at).toLocaleString()}</div>
                </div>
              )}
            </div>
          )}

          {/* Goal Progress */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Goal Progress</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Continuity (avg ≤ {state.state.goal_continuity_avg})</span>
                  <span className={`font-medium ${(state.state.best_continuity_avg ?? 999) <= state.state.goal_continuity_avg ? 'text-green-600' : 'text-gray-900'}`}>
                    {state.state.best_continuity_avg?.toFixed(2) ?? '—'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${(state.state.best_continuity_avg ?? 999) <= state.state.goal_continuity_avg ? 'bg-green-500' : 'bg-blue-500'}`}
                    style={{ width: `${Math.min(100, ((state.state.goal_continuity_avg / (state.state.best_continuity_avg ?? 999)) * 100))}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Unassigned (&lt; {state.state.goal_unassigned_pct}%)</span>
                  <span className={`font-medium ${(state.state.best_unassigned_pct ?? 999) < state.state.goal_unassigned_pct ? 'text-green-600' : 'text-gray-900'}`}>
                    {state.state.best_unassigned_pct?.toFixed(2) ?? '—'}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${(state.state.best_unassigned_pct ?? 999) < state.state.goal_unassigned_pct ? 'bg-green-500' : 'bg-blue-500'}`}
                    style={{ width: `${Math.min(100, ((state.state.goal_unassigned_pct / (state.state.best_unassigned_pct ?? 999)) * 100))}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Efficiency (≥ {state.state.goal_efficiency_pct}%)</span>
                  <span className={`font-medium ${(state.state.best_efficiency_pct ?? 0) >= state.state.goal_efficiency_pct ? 'text-green-600' : 'text-gray-900'}`}>
                    {state.state.best_efficiency_pct?.toFixed(1) ?? '—'}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${(state.state.best_efficiency_pct ?? 0) >= state.state.goal_efficiency_pct ? 'bg-green-500' : 'bg-blue-500'}`}
                    style={{ width: `${Math.min(100, ((state.state.best_efficiency_pct ?? 0) / state.state.goal_efficiency_pct) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
            {state.state.goals_met && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <div className="text-green-600 font-medium text-sm">✅ All goals achieved!</div>
              </div>
            )}
          </div>

          {/* Recent History */}
          {state.history.length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Recent History (Last 10)</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs border-t border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left p-2 font-medium">Iteration</th>
                      <th className="text-left p-2 font-medium">Strategy</th>
                      <th className="text-right p-2 font-medium">Cont.</th>
                      <th className="text-right p-2 font-medium">Unassigned</th>
                      <th className="text-right p-2 font-medium">Eff</th>
                      <th className="text-left p-2 font-medium">Decision</th>
                    </tr>
                  </thead>
                  <tbody>
                    {state.history.slice(-10).reverse().map((entry, idx) => (
                      <tr key={idx} className="border-t border-gray-100">
                        <td className="p-2">{entry.iteration}</td>
                        <td className="p-2 font-mono text-xs">{entry.strategy}</td>
                        <td className="p-2 text-right">{entry.metrics.continuity_avg.toFixed(2)}</td>
                        <td className="p-2 text-right">{entry.metrics.unassigned_pct.toFixed(2)}%</td>
                        <td className="p-2 text-right">{entry.metrics.efficiency.toFixed(1)}%</td>
                        <td className="p-2">
                          <span className={`inline-flex px-1.5 py-0.5 rounded text-xs font-medium ${
                            entry.decision === 'keep' || entry.decision === 'double_down' ? 'bg-green-100 text-green-800' :
                            entry.decision === 'kill' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {entry.decision}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Learnings */}
          {state.learnings.length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Research Learnings</h3>
              <ul className="space-y-2">
                {state.learnings.slice(-5).map((learning, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex gap-2">
                    <span className="text-gray-400">•</span>
                    <span>{learning.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {/* Trigger Research Dialog */}
      {triggerDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Start Research Loop</h3>
              <button
                type="button"
                onClick={() => setTriggerDialogOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Iterations
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={maxIterations}
                  onChange={(e) => setMaxIterations(parseInt(e.target.value) || 50)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Maximum number of optimization iterations (default: 50)
                </p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="dry-run"
                  checked={dryRun}
                  onChange={(e) => setDryRun(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="dry-run" className="text-sm text-gray-700">
                  Dry run (simulate without actual Timefold API calls)
                </label>
              </div>

              <div className="rounded bg-blue-50 border border-blue-200 px-3 py-2 text-sm text-blue-800">
                <strong>Dataset:</strong> {selectedDataset}<br />
                <strong>Goals:</strong> Continuity ≤11, Unassigned &lt;1%, Efficiency ≥70%
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                type="button"
                onClick={() => setTriggerDialogOpen(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleTrigger}
                disabled={triggering}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {triggering ? 'Starting…' : 'Start Research'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
