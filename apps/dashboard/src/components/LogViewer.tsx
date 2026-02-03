/**
 * Log Viewer Component
 * Displays recent log entries from a repository
 */
import { useEffect, useState } from 'react';
import { AlertCircle, Info, AlertTriangle, XCircle } from 'lucide-react';
import { getRepositoryLogs } from '../lib/api';
import type { LogEntry } from '../types';

interface LogViewerProps {
  repoName: string;
  limit?: number;
}

export function LogViewer({ repoName, limit = 50 }: LogViewerProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadLogs = async () => {
    try {
      setError(null);
      const data = await getRepositoryLogs(repoName, limit);
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();

    if (autoRefresh) {
      const interval = setInterval(loadLogs, 10000); // Refresh every 10 seconds
      return () => clearInterval(interval);
    }
  }, [repoName, limit, autoRefresh]);

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warn':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'debug':
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return 'text-red-700 bg-red-50';
      case 'warn':
        return 'text-yellow-700 bg-yellow-50';
      case 'info':
        return 'text-blue-700 bg-blue-50';
      case 'debug':
        return 'text-gray-700 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-2">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600 mb-2">
          <XCircle className="w-5 h-5" />
          <p className="font-medium">Error</p>
        </div>
        <p className="text-sm text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Logs</h3>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
        </div>

        {logs.length === 0 ? (
          <p className="text-sm text-gray-600">No logs found</p>
        ) : (
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {logs.map((log, index) => (
              <div
                key={index}
                className={`flex items-start gap-2 p-2 rounded text-xs font-mono ${getLevelColor(log.level)}`}
              >
                <div className="flex-shrink-0 mt-0.5">{getLevelIcon(log.level)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium uppercase">{log.level}</span>
                    <span className="text-xs text-gray-500">{log.timestamp}</span>
                    <span className="text-xs text-gray-500">({log.source})</span>
                  </div>
                  <p className="break-words whitespace-pre-wrap">{log.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
