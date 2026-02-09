/**
 * RL Dashboard - Reinforcement Learning Experiments & Patterns
 */
import { useEffect, useState } from 'react';
import { Brain, TrendingUp, Activity } from 'lucide-react';
import { getExperiments, getPatterns } from '../lib/api';
import type { DbExperiment } from '../types';

interface Pattern {
  id: string;
  pattern_type: string;
  description: string;
  detection_count: number;
  confidence_score: number;
  status?: string;
}

export function RLDashboardPage() {
  const [experiments, setExperiments] = useState<DbExperiment[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'experiments' | 'patterns'>('experiments');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [experimentsData, patternsData] = await Promise.all([
        getExperiments(),
        getPatterns() as Promise<Pattern[]>
      ]);
      // Handle both array and wrapped response
      const experimentsArray = Array.isArray(experimentsData) ? experimentsData : (experimentsData.experiments || []);
      const patternsArray = Array.isArray(patternsData) ? patternsData : (patternsData.patterns || []);
      setExperiments(experimentsArray);
      setPatterns(patternsArray);
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Active Experiments</div>
          <div className="text-2xl font-bold text-gray-900">
            {experiments.filter(e => e.status === 'active').length}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Total Experiments</div>
          <div className="text-2xl font-bold text-blue-600">{experiments.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Patterns Detected</div>
          <div className="text-2xl font-bold text-green-600">{patterns.length}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-4">
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
