/**
 * Schedule Research Page - AI-powered autonomous optimization
 *
 * Orchestrates mathematician + specialist agents to explore optimization strategies,
 * evaluate results, and converge toward goal metrics.
 */
import { useEffect, useState } from 'react';
import { PagePurpose } from '../components/PagePurpose';
import { getResearchState, getRunningResearchJobs } from '../lib/api';
import type { ResearchStateResponse } from '../types';
import { Play, Square, RefreshCw } from 'lucide-react';

const DATASET = 'huddinge-v3';
const POLL_INTERVAL = 5000; // 5 seconds

export function ScheduleResearchPage() {
  const [state, setState] = useState<ResearchStateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggerDialogOpen, setTriggerDialogOpen] = useState(false);

  const loadState = async () => {
    try {
      const data = await getResearchState(DATASET);
      setState(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load research state');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadState();
  }, []);

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
        <h2 className="text-lg font-semibold text-gray-900">
          Schedule Research — {DATASET}
        </h2>
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

      {/* TODO: Add TriggerResearchDialog modal */}
    </div>
  );
}
