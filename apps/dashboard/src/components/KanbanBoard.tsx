/**
 * KanbanBoard - Task board across sessions
 * Displays all tasks grouped by status in a kanban layout.
 */
import { useEffect, useState } from 'react';
import { LayoutGrid } from 'lucide-react';
import { getAllDbTasks } from '../lib/api';
import type { DbTask } from '../types';

const COLUMNS: { key: DbTask['status']; label: string; color: string }[] = [
  { key: 'pending', label: 'Pending', color: 'border-yellow-300' },
  { key: 'in_progress', label: 'In Progress', color: 'border-blue-300' },
  { key: 'completed', label: 'Completed', color: 'border-green-300' },
  { key: 'failed', label: 'Failed', color: 'border-red-300' },
  { key: 'blocked', label: 'Blocked', color: 'border-gray-300' },
];

const PRIORITY_BADGE: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
};

export function KanbanBoard() {
  const [tasks, setTasks] = useState<DbTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllDbTasks()
      .then(setTasks)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading tasks...</div>;
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <LayoutGrid className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-gray-700">No Tasks Yet</h3>
        <p className="text-sm text-gray-500 mt-1">
          Tasks will appear here when sessions assign work to agents.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <LayoutGrid className="w-5 h-5" /> Task Board
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {COLUMNS.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.key);
          return (
            <div key={col.key} className={`bg-white rounded-lg border-t-4 ${col.color} border border-gray-200 p-3`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-700">{col.label}</h3>
                <span className="text-xs bg-gray-100 text-gray-600 rounded-full px-2 py-0.5">
                  {colTasks.length}
                </span>
              </div>
              <div className="space-y-2 min-h-[100px]">
                {colTasks.map((task) => (
                  <div key={task.id} className="bg-gray-50 rounded-md p-2.5 text-sm border border-gray-100">
                    <div className="flex items-center gap-1.5 mb-1">
                      <span>{task.agent_emoji || '🤖'}</span>
                      <span className="font-medium text-gray-800">{task.agent_name || 'Unknown'}</span>
                    </div>
                    <p className="text-gray-600 text-xs line-clamp-2">{task.description}</p>
                    <div className="flex items-center gap-2 mt-1.5">
                      {task.priority && (
                        <span className={`text-xs px-1.5 py-0.5 rounded ${PRIORITY_BADGE[task.priority] || ''}`}>
                          {task.priority}
                        </span>
                      )}
                      {task.team_name && (
                        <span className="text-xs text-gray-400">{task.team_name}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
