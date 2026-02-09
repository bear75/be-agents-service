/**
 * SessionsBoard - Kanban-style session list from SQLite
 * Shows recent sessions with status, team, repo, and tasks.
 */
import { useEffect, useState } from 'react';
import { Clock, GitBranch, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { getSessions, getSessionDetail } from '../lib/api';
import type { Session } from '../types';

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  blocked: 'bg-gray-100 text-gray-800',
};

export function SessionsBoard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSessions(30)
      .then(setSessions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function toggleExpand(sessionId: string) {
    if (expandedId === sessionId) {
      setExpandedId(null);
      setDetail(null);
      return;
    }
    setExpandedId(sessionId);
    try {
      const d = await getSessionDetail(sessionId);
      setDetail(d);
    } catch (e) {
      console.error(e);
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading sessions...</div>;
  }

  if (sessions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-gray-700">No Sessions Yet</h3>
        <p className="text-sm text-gray-500 mt-1">
          Sessions will appear here when agents run via auto-compound or the Control Tower.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-gray-900">Recent Sessions</h2>
      {sessions.map((s) => (
        <div key={s.id} className="bg-white rounded-lg border border-gray-200">
          <button
            onClick={() => toggleExpand(s.id)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[s.status] || 'bg-gray-100'}`}>
                {s.status.replace('_', ' ')}
              </span>
              <span className="font-medium text-gray-900">{s.team_name || s.team_id}</span>
              <span className="text-sm text-gray-500">{s.target_repo}</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              {s.branch_name && (
                <span className="flex items-center gap-1">
                  <GitBranch className="w-3.5 h-3.5" />
                  {s.branch_name}
                </span>
              )}
              <span>{new Date(s.started_at).toLocaleString()}</span>
              {expandedId === s.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </div>
          </button>

          {expandedId === s.id && detail && (
            <div className="border-t border-gray-100 p-4 bg-gray-50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                <div>
                  <span className="text-gray-500">Duration:</span>{' '}
                  {detail.duration_seconds ? `${Math.round(detail.duration_seconds / 60)} min` : 'N/A'}
                </div>
                <div>
                  <span className="text-gray-500">Iterations:</span> {detail.iteration_count}
                </div>
                <div>
                  <span className="text-gray-500">Exit Code:</span> {detail.exit_code ?? 'N/A'}
                </div>
                {detail.pr_url && (
                  <div>
                    <a href={detail.pr_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                      <ExternalLink className="w-3.5 h-3.5" /> View PR
                    </a>
                  </div>
                )}
              </div>

              {detail.tasks && detail.tasks.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Tasks ({detail.tasks.length})</h4>
                  <div className="space-y-1">
                    {detail.tasks.map((t) => (
                      <div key={t.id} className="flex items-center gap-2 text-sm">
                        <span className={`px-1.5 py-0.5 rounded text-xs ${STATUS_COLORS[t.status] || 'bg-gray-100'}`}>
                          {t.status}
                        </span>
                        <span>{t.agent_emoji} {t.agent_name}</span>
                        <span className="text-gray-500 truncate">{t.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
