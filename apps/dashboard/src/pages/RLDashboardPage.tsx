/**
 * RL Dashboard - Experiments, Patterns, and LLM Usage
 */
import { useEffect, useState } from 'react';
import { Brain, TrendingUp, Activity, Cpu, Zap, Clock } from 'lucide-react';
import {
  getExperiments,
  getPatterns,
  getLLMStats,
  getLLMUsage,
} from '../lib/api';
import type { LLMStatsResponse, LLMUsageRecord } from '../lib/api';
import type { DbExperiment as DbExperimentType } from '../types';

interface Pattern {
  id: string;
  pattern_type: string;
  description: string;
  detection_count: number;
  confidence_score: number;
  status?: string;
}

/** Categorize model as Ollama (local) vs Claude */
function getModelCategory(model: string): 'ollama' | 'claude' | 'other' {
  const m = model.toLowerCase();
  if (m.includes('ollama') || m.includes('pi') || m.includes('qwen') || m.includes('local')) {
    return 'ollama';
  }
  if (m.includes('claude') || m.includes('opus') || m.includes('sonnet') || m.includes('haiku')) {
    return 'claude';
  }
  return 'other';
}

export function RLDashboardPage() {
  const [experiments, setExperiments] = useState<DbExperimentType[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [llmStats, setLLMStats] = useState<LLMStatsResponse | null>(null);
  const [llmUsage, setLLMUsage] = useState<LLMUsageRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'experiments' | 'patterns' | 'llm'>('llm');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [experimentsData, patternsData, statsData, usageData] = await Promise.all([
        getExperiments(),
        getPatterns() as Promise<Pattern[]>,
        getLLMStats(7).catch(() => null),
        getLLMUsage(7, 200).catch(() => []),
      ]);
      const experimentsArray = Array.isArray(experimentsData) ? experimentsData : ((experimentsData as { experiments?: unknown[] })?.experiments || []);
      const patternsArray = Array.isArray(patternsData) ? patternsData : ((patternsData as { patterns?: unknown[] })?.patterns || []);
      setExperiments(experimentsArray as DbExperimentType[]);
      setPatterns(patternsArray);
      setLLMStats(statsData);
      setLLMUsage(Array.isArray(usageData) ? usageData : []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load RL data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Brain className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">RL Dashboard</h2>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">LLM Cost (7d)</div>
          <div className="text-2xl font-bold text-gray-900">
            {llmStats ? `$${llmStats.totalCost}` : '—'}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">LLM Calls</div>
          <div className="text-2xl font-bold text-blue-600">
            {llmUsage.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Experiments</div>
          <div className="text-2xl font-bold text-indigo-600">{experiments.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Patterns</div>
          <div className="text-2xl font-bold text-green-600">{patterns.length}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('llm')}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'llm'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              LLM Usage ({llmUsage.length})
            </div>
          </button>
          <button
            onClick={() => setActiveTab('experiments')}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'experiments'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Experiments ({experiments.length})
            </div>
          </button>
          <button
            onClick={() => setActiveTab('patterns')}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'patterns'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Patterns ({patterns.length})
            </div>
          </button>
        </div>
      </div>

      {/* LLM Usage Tab */}
      {activeTab === 'llm' && (
        <div className="space-y-4">
          {llmStats && llmStats.byModel?.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <h3 className="px-4 py-3 border-b font-medium text-gray-900 flex items-center gap-2">
                <Cpu className="w-4 h-4" />
                Usage by Model (Ollama vs Claude)
              </h3>
              <div className="divide-y">
                {llmStats.byModel.map((m) => {
                  const cat = getModelCategory(m.model);
                  return (
                    <div key={m.model} className="px-4 py-3 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded ${
                            cat === 'ollama' ? 'bg-emerald-100 text-emerald-800' : cat === 'claude' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {cat === 'ollama' ? 'Ollama' : cat === 'claude' ? 'Claude' : 'Other'}
                        </span>
                        <span className="font-mono text-sm">{m.model}</span>
                      </div>
                      <div className="flex items-center gap-6 text-sm">
                        <span className="text-gray-500">
                          {(m.totalInputTokens ?? 0).toLocaleString()} in / {(m.totalOutputTokens ?? 0).toLocaleString()} out
                        </span>
                        <span className="font-medium">${m.totalCost ?? 0}</span>
                        <span className="text-gray-400">{m.usageCount} calls</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <h3 className="px-4 py-3 border-b font-medium text-gray-900 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Recent LLM Calls (timestamp, model, tokens)
            </h3>
            {llmUsage.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                No LLM usage recorded yet. Usage is recorded when agents run (compound workflow, llm-invoke, etc.).
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="px-4 py-2 text-left font-medium text-gray-700">Timestamp</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-700">Model</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-700">In / Out</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-700">Cost</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-700">Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {llmUsage.map((r) => {
                      const cat = getModelCategory(r.model);
                      return (
                        <tr key={r.id} className="border-b hover:bg-gray-50">
                          <td className="px-4 py-2 text-gray-600">
                            {r.usedAt ? new Date(r.usedAt).toLocaleString() : '—'}
                          </td>
                          <td className="px-4 py-2">
                            <span
                              className={`inline-flex px-2 py-0.5 text-xs font-medium rounded ${
                                cat === 'ollama' ? 'bg-emerald-100 text-emerald-800' : cat === 'claude' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {r.model}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {r.inputTokens?.toLocaleString()} / {r.outputTokens?.toLocaleString()}
                          </td>
                          <td className="px-4 py-2 text-right">${(r.costUsd ?? 0).toFixed(4)}</td>
                          <td className="px-4 py-2 text-right">
                            {r.durationMs != null ? `${(r.durationMs / 1000).toFixed(1)}s` : '—'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Experiments Tab */}
      {activeTab === 'experiments' && (
        <div className="space-y-4">
          {experiments.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No experiments yet</h3>
              <p className="text-gray-500">
                RL experiments will appear here once they're created.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {experiments.map((exp) => (
                <div
                  key={exp.id}
                  className="bg-white rounded-lg border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900">{exp.name || exp.id}</h3>
                      {exp.description && (
                        <p className="text-sm text-gray-600 mt-1">{exp.description}</p>
                      )}
                    </div>
                    {exp.status && (
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          exp.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : exp.status === 'successful'
                            ? 'bg-blue-100 text-blue-800'
                            : exp.status === 'killed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {exp.status}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {exp.success_metric && (
                      <div>
                        <div className="text-gray-500">Metric</div>
                        <div className="font-mono text-gray-900">{exp.success_metric}</div>
                      </div>
                    )}
                    {exp.target_value !== undefined && (
                      <div>
                        <div className="text-gray-500">Target</div>
                        <div className="font-mono text-gray-900">{exp.target_value}</div>
                      </div>
                    )}
                    {exp.current_value !== undefined && (
                      <div>
                        <div className="text-gray-500">Current</div>
                        <div className="font-mono text-gray-900">{exp.current_value}</div>
                      </div>
                    )}
                    {exp.sample_size !== undefined && (
                      <div>
                        <div className="text-gray-500">Samples</div>
                        <div className="font-mono text-gray-900">{exp.sample_size}</div>
                      </div>
                    )}
                  </div>
                  {exp.decision && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">Decision:</span>{' '}
                        <span
                          className={`font-medium ${
                            exp.decision === 'double_down'
                              ? 'text-green-600'
                              : exp.decision === 'kill'
                              ? 'text-red-600'
                              : 'text-gray-600'
                          }`}
                        >
                          {exp.decision}
                        </span>
                      </div>
                      {exp.decision_reason && (
                        <div className="text-sm text-gray-600 mt-1">{exp.decision_reason}</div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Patterns Tab */}
      {activeTab === 'patterns' && (
        <div className="space-y-4">
          {patterns.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No patterns detected yet</h3>
              <p className="text-gray-500">
                Patterns will be detected automatically as agents work.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {patterns.map((pattern) => (
                <div
                  key={pattern.id}
                  className="bg-white rounded-lg border border-gray-200 p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-gray-900">{pattern.pattern_type}</h3>
                        <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
                          {(pattern.confidence_score * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{pattern.description}</p>
                    </div>
                    {pattern.status && (
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          pattern.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {pattern.status}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div>
                      Detected <span className="font-medium text-gray-900">{pattern.detection_count}</span> times
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
