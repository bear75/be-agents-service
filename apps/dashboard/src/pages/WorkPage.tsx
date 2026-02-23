/**
 * Work - unified sessions + tasks (single purpose: show work status)
 * Sessions as primary cards, expandable to show tasks. No tabs.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  Info,
  AlertCircle,
} from 'lucide-react';
import { StatsBar } from '../components/StatsBar';
import { PagePurpose } from '../components/PagePurpose';
import { getSessions, getTasks } from '../lib/api';
import type { DbSession, DbTask } from '../types';

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

interface SessionCardProps {
  session: DbSession;
  tasks: DbTask[];
  expanded: boolean;
  onToggle: () => void;
}

function SessionCard({ session, tasks, expanded, onToggle }: SessionCardProps) {
  const sessionTasks = tasks.filter((t) => t.session_id === session.id);
  const hasTasks = sessionTasks.length > 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50"
      >
        {expanded ? (
          <ChevronDown className="w-5 h-5 text-gray-500 shrink-0" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-500 shrink-0" />
        )}
        <span className="font-mono text-sm text-gray-900 flex-1 truncate">
          {session.id}
        </span>
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full shrink-0 ${statusColor(session.status)}`}>
          {session.status}
        </span>
        <span className="text-sm text-gray-500 shrink-0">
          {session.started_at ? new Date(session.started_at).toLocaleString() : '—'}
        </span>
        {session.pr_url && (
          <a
            href={session.pr_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-1 text-blue-600 hover:underline shrink-0"
          >
            PR <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </button>
      {expanded && (
        <div className="px-4 pb-4 pt-2 border-t bg-gray-50">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600 mb-4">
            <div>
              <span className="text-gray-500">Team</span> {session.team_name || session.team_id || '—'}
            </div>
            <div>
              <span className="text-gray-500">Branch</span> {session.branch_name || '—'}
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
              <Clock className="w-4 h-4" /> Tasks ({sessionTasks.length})
            </h4>
            {hasTasks ? (
              <div className="space-y-2">
                {sessionTasks.map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center gap-3 p-2 bg-white rounded border border-gray-200"
                  >
                    <span className="text-lg">{t.emoji || '🤖'}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 text-sm">
                        {t.agent_name || t.agent_id}
                      </div>
                      <p className="text-xs text-gray-600 truncate">{t.description || '—'}</p>
                    </div>
                    <span className={`px-2 py-0.5 text-xs rounded shrink-0 ${statusColor(t.status)}`}>
                      {t.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-700 rounded p-4 bg-white border border-gray-200 space-y-2">
                <p className="font-medium text-gray-900">Compound progress</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  <li>Compound writes tasks to target repo <code className="bg-gray-100 px-1 rounded">scripts/compound/prd.json</code></li>
                  <li>Tasks sync here after prd.json is created and after each loop run</li>
                  <li>0 tasks = prd.json not created yet, or compound still on branch/PRD step</li>
                  <li>See progress: target repo <code className="bg-gray-100 px-1 rounded">logs/</code> folder</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function WorkPage() {
  const [sessions, setSessions] = useState<DbSession[]>([]);
  const [tasks, setTasks] = useState<DbTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getSessions().then((d) => (Array.isArray(d) ? d : (d.sessions || []))),
      getTasks().then((d) => (Array.isArray(d) ? d : (d.tasks || []))),
    ])
      .then(([s, t]) => {
        setSessions(s);
        setTasks(t);
        setError(null);
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
      <div className="rounded-lg bg-red-50 p-4 text-red-700 flex items-center gap-2">
        <AlertCircle className="w-5 h-5 shrink-0" />
        Failed to load: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <StatsBar />
      <PagePurpose
        purpose="Sessions and tasks."
        how="Click a session to expand. Tasks sync from target repo prd.json when compound creates it and after each task loop."
      />
      <div className="space-y-3">
        {sessions.map((s) => (
          <SessionCard
            key={s.id}
            session={s}
            tasks={tasks}
            expanded={expandedId === s.id}
            onToggle={() => setExpandedId((id) => (id === s.id ? null : s.id))}
          />
        ))}
        {sessions.length === 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">No sessions yet</p>
            <p className="text-sm text-gray-500">
              Start compound from <Link to="/run" className="text-blue-600 hover:underline">Run → Compound</Link> or
              terminal: <code className="bg-gray-100 px-1 rounded text-xs">./scripts/compound/auto-compound.sh beta-appcaire</code>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
