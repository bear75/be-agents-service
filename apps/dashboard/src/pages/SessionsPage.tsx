/**
 * Sessions overview - orchestrator runs with status and PR links
 */
import { useEffect, useState } from 'react';
import { LayoutDashboard, ExternalLink, Clock } from 'lucide-react';
import { getSessions } from '../lib/api';
import type { DbSession } from '../types';

export function SessionsPage() {
  const [sessions, setSessions] = useState<DbSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSessions()
      .then((data) => {
        // Handle both array and wrapped response
        const sessionsArray = Array.isArray(data) ? data : (data.sessions || []);
        setSessions(sessionsArray);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-700">
        Failed to load sessions: {error}
      </div>
    );
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <LayoutDashboard className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Sessions</h2>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Session</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Team</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Branch</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">PR</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sessions.map((s) => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-mono text-gray-900">{s.id}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{s.team_name || s.team_id}</td>
                <td>
                  <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${statusColor(s.status)}`}>
                    {s.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{s.branch_name || '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-600 flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {s.started_at ? new Date(s.started_at).toLocaleString() : '—'}
                </td>
                <td>
                  {s.pr_url ? (
                    <a
                      href={s.pr_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-blue-600 hover:underline"
                    >
                      View PR <ExternalLink className="w-4 h-4" />
                    </a>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {sessions.length === 0 && (
          <div className="py-12 text-center text-gray-500">No sessions yet</div>
        )}
      </div>
    </div>
  );
}
