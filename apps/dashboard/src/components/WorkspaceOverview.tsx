/**
 * Workspace Overview Component
 * Shows a combined summary card of the entire workspace
 */
import { useEffect, useState } from 'react';
import {
  LayoutDashboard,
  Inbox,
  Target,
  ListTodo,
  CalendarDays,
  BookOpen,
  AlertCircle,
} from 'lucide-react';
import { getWorkspaceOverview } from '../lib/api';
import type { WorkspaceOverview as WorkspaceOverviewType } from '../types';

interface WorkspaceOverviewProps {
  repoName: string;
}

export function WorkspaceOverview({ repoName }: WorkspaceOverviewProps) {
  const [overview, setOverview] = useState<WorkspaceOverviewType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOverview = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getWorkspaceOverview(repoName);
        setOverview(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workspace');
      } finally {
        setLoading(false);
      }
    };

    loadOverview();
  }, [repoName]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-4 gap-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-amber-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">Workspace not available</p>
        </div>
        <p className="text-sm text-gray-600">
          {error.includes('not configured')
            ? 'No workspace configured for this repository. Add workspace config to repos.yaml.'
            : error}
        </p>
      </div>
    );
  }

  if (!overview) return null;

  const priority1 = overview.priorities.find((p) => p.priority === 'high');

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <LayoutDashboard className="w-5 h-5 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">Workspace</h3>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            icon={<Inbox className="w-5 h-5 text-blue-600" />}
            label="Inbox"
            value={overview.inbox.pending}
            detail={`${overview.inbox.total} total`}
            color="blue"
          />
          <MetricCard
            icon={<Target className="w-5 h-5 text-red-600" />}
            label="Priority #1"
            value={priority1?.title || 'None'}
            isText
            color="red"
          />
          <MetricCard
            icon={<ListTodo className="w-5 h-5 text-green-600" />}
            label="Active Tasks"
            value={overview.tasks.inProgress.length}
            detail={`${overview.tasks.pending.length} pending`}
            color="green"
          />
          <MetricCard
            icon={<CalendarDays className="w-5 h-5 text-purple-600" />}
            label="Follow-ups"
            value={overview.followUps.pending}
            detail={`${overview.followUps.total} total`}
            color="purple"
          />
        </div>

        {/* Active tasks list */}
        {overview.tasks.inProgress.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">In Progress</h4>
            <div className="space-y-2">
              {overview.tasks.inProgress.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-2 bg-green-50 rounded border-l-4 border-green-500"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{task.title}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {task.branch && (
                        <span className="text-xs text-gray-500 font-mono">
                          {task.branch}
                        </span>
                      )}
                      {task.agent && (
                        <span className="text-xs text-gray-500">
                          [{task.agent}]
                        </span>
                      )}
                    </div>
                  </div>
                  {task.pr && (
                    <span className="text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded">
                      {task.pr}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Latest agent report preview */}
        {overview.agentReport && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-4 h-4 text-gray-500" />
              <h4 className="text-sm font-medium text-gray-700">Latest Agent Report</h4>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <p className="text-xs text-gray-600 font-mono whitespace-pre-wrap line-clamp-4">
                {overview.agentReport.slice(0, 300)}
                {overview.agentReport.length > 300 ? '...' : ''}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Metric Card ────────────────────────────────────────────────────────────

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  detail?: string;
  isText?: boolean;
  color: 'blue' | 'red' | 'green' | 'purple';
}

function MetricCard({ icon, label, value, detail, isText, color }: MetricCardProps) {
  const bgColors = {
    blue: 'bg-blue-50',
    red: 'bg-red-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50',
  };

  return (
    <div className={`${bgColors[color]} rounded-lg p-3`}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs font-medium text-gray-600">{label}</span>
      </div>
      {isText ? (
        <p className="text-sm font-semibold text-gray-900 truncate">{value}</p>
      ) : (
        <>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {detail && <p className="text-xs text-gray-500">{detail}</p>}
        </>
      )}
    </div>
  );
}
