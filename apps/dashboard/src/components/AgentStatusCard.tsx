/**
 * Agent Status Card Component
 * Displays the current status of an agent for a specific repository
 */
import { useEffect, useState } from 'react';
import { Clock, Play, Square, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { getRepositoryStatus, triggerAgent, cancelAgent } from '../lib/api';
import type { AgentStatus } from '../types';

interface AgentStatusCardProps {
  repoName: string;
}

export function AgentStatusCard({ repoName }: AgentStatusCardProps) {
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggering, setTriggering] = useState(false);

  const loadStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRepositoryStatus(repoName);
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    // Refresh every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, [repoName]);

  const handleTriggerReview = async () => {
    try {
      setTriggering(true);
      await triggerAgent(repoName, 'review');
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger review');
    } finally {
      setTriggering(false);
    }
  };

  const handleTriggerCompound = async () => {
    try {
      setTriggering(true);
      await triggerAgent(repoName, 'compound');
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger compound');
    } finally {
      setTriggering(false);
    }
  };

  const handleCancel = async () => {
    try {
      setTriggering(true);
      await cancelAgent(repoName);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel');
    } finally {
      setTriggering(false);
    }
  };

  if (loading && !status) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600">
          <XCircle className="w-5 h-5" />
          <p className="font-medium">Error</p>
        </div>
        <p className="text-sm text-gray-600 mt-2">{error}</p>
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              status.running
                ? 'bg-blue-100 text-blue-800'
                : status.enabled
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
            }`}
          >
            {status.running ? 'Running' : status.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>

        {/* Status Info */}
        <div className="space-y-3 mb-6">
          {status.lastRun && (
            <div className="flex items-center gap-2 text-sm">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">Last run:</span>
              <span className="text-gray-900">{new Date(status.lastRun).toLocaleString()}</span>
            </div>
          )}

          {status.lastSuccess && (
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-gray-600">Last success:</span>
              <span className="text-gray-900">
                {new Date(status.lastSuccess).toLocaleString()}
              </span>
            </div>
          )}

          {status.lastError && (
            <div className="flex items-center gap-2 text-sm">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <span className="text-gray-600">Last error:</span>
              <span className="text-red-600">{status.lastError}</span>
            </div>
          )}

          {status.nextScheduledRun && (
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <p className="text-sm font-medium text-gray-700 mb-2">Next Scheduled</p>
              <div className="space-y-1">
                <p className="text-sm text-gray-600">
                  Review: <span className="font-medium">{status.nextScheduledRun.review}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Compound: <span className="font-medium">{status.nextScheduledRun.compound}</span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          {status.running ? (
            <button
              onClick={handleCancel}
              disabled={triggering}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Square className="w-4 h-4" />
              Cancel
            </button>
          ) : (
            <>
              <button
                onClick={handleTriggerReview}
                disabled={triggering || !status.enabled}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-4 h-4" />
                Trigger Review
              </button>
              <button
                onClick={handleTriggerCompound}
                disabled={triggering || !status.enabled}
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-4 h-4" />
                Trigger Compound
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
