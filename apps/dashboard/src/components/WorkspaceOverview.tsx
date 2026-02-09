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
  Play,
  Clock,
} from 'lucide-react';
import { getWorkspaceOverview, triggerAgent } from '../lib/api';
import type { WorkspaceOverview as WorkspaceOverviewType } from '../types';

interface WorkspaceOverviewProps {
  repoName: string;
}

export function WorkspaceOverview({ repoName }: WorkspaceOverviewProps) {
  const [overview, setOverview] = useState<WorkspaceOverviewType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [triggerSuccess, setTriggerSuccess] = useState(false);

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

  const handleTriggerNow = async () => {
    try {
      setTriggering(true);
      await triggerAgent(repoName, 'compound');
      setTriggerSuccess(true);
      setShowTriggerModal(false);
      setTimeout(() => setTriggerSuccess(false), 3000);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to trigger agent');
    } finally {
      setTriggering(false);
    }
  };

  const handleTriggerTonight = () => {
    setShowTriggerModal(false);
    alert('✅ Agent will run tonight at 11:00 PM as scheduled');
  };

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
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="w-5 h-5 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900">Workspace</h3>
          </div>
          <button
            onClick={() => setShowTriggerModal(true)}
            disabled={triggering}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            {triggering ? 'Starting...' : 'Run Agent'}
          </button>
        </div>
        {triggerSuccess && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 text-sm">
            ✅ Agent started successfully! Check the "Agents & Logs" tab for progress.
          </div>
        )}

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

      {/* Trigger Modal */}
      {showTriggerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Run Agent Now or Tonight?</h3>
            <p className="text-gray-600 mb-6">
              Choose when to run the agent for <span className="font-mono text-sm">{repoName}</span>
            </p>
            <div className="space-y-3">
              <button
                onClick={handleTriggerNow}
                disabled={triggering}
                className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Play className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Run Now</div>
                  <div className="text-sm opacity-90">Start agent immediately</div>
                </div>
              </button>
              <button
                onClick={handleTriggerTonight}
                disabled={triggering}
                className="w-full flex items-center gap-3 px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                <Clock className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Wait for Tonight</div>
                  <div className="text-sm opacity-90">Run at 11:00 PM (scheduled)</div>
                </div>
              </button>
              <button
                onClick={() => setShowTriggerModal(false)}
                disabled={triggering}
                className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
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
