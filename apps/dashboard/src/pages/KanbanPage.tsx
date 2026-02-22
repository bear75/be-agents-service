/**
 * Kanban task board - Pending → In Progress → Completed
 */
import { useEffect, useState } from 'react';
import { Kanban, AlertCircle } from 'lucide-react';
import { StatsBar } from '../components/StatsBar';
import { getTasks, updateTaskStatus } from '../lib/api';
import type { DbTask } from '../types';

const COLUMNS = ['pending', 'in_progress', 'completed', 'failed'] as const;

interface TaskCardProps {
  task: DbTask;
  onDragStart: (taskId: string) => void;
}

function TaskCard({ task, onDragStart }: TaskCardProps) {
  const priorityColor =
    task.priority === 'high' ? 'border-l-red-500' :
    task.priority === 'medium' ? 'border-l-orange-500' :
    'border-l-green-500';

  return (
    <div
      draggable
      onDragStart={() => onDragStart(task.id)}
      className={`bg-white rounded-lg border border-gray-200 p-3 border-l-4 ${priorityColor} hover:shadow-md transition-shadow cursor-move`}
    >
      <div className="flex items-start gap-2">
        <span className="text-2xl">{task.emoji || '🤖'}</span>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900">{task.agent_name || task.agent_id}</div>
          <div className="text-xs text-gray-500 uppercase">{task.team_name || ''}</div>
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-600 line-clamp-3">{task.description || '—'}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {task.llm_model && (
          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">{task.llm_model}</span>
        )}
        {task.session_id && (
          <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded font-mono truncate max-w-[120px]">
            {task.session_id}
          </span>
        )}
        {task.duration_seconds != null && (
          <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded">
            ⏱ {task.duration_seconds}s
          </span>
        )}
      </div>
      <div className="mt-2 pt-2 border-t flex justify-between text-xs text-gray-500">
        <span>{task.started_at ? new Date(task.started_at).toLocaleString() : '—'}</span>
        {task.status === 'failed' && (
          <span className="text-red-600 flex items-center gap-1">
            <AlertCircle className="w-4 h-4" /> Error
          </span>
        )}
      </div>
    </div>
  );
}

export function KanbanPage() {
  const [tasks, setTasks] = useState<DbTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);

  useEffect(() => {
    getTasks()
      .then((data) => {
        // Handle both array and wrapped response
        const tasksArray = Array.isArray(data) ? data : (data.tasks || []);
        setTasks(tasksArray);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleDragStart = (taskId: string) => {
    setDraggedTaskId(taskId);
    setUpdateError(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault(); // Allow drop
  };

  const handleDrop = async (e: React.DragEvent, newStatus: string) => {
    e.preventDefault();

    if (!draggedTaskId) return;

    const task = tasks.find((t) => t.id === draggedTaskId);
    if (!task) return;

    // Don't update if status is the same
    if (task.status === newStatus) {
      setDraggedTaskId(null);
      return;
    }

    // Store old status for rollback
    const oldStatus = task.status;

    // Optimistic update
    setTasks((prevTasks) =>
      prevTasks.map((t) =>
        t.id === draggedTaskId ? { ...t, status: newStatus } : t
      )
    );

    try {
      // Update on server
      await updateTaskStatus(draggedTaskId, newStatus);
      setUpdateError(null);
    } catch (error) {
      // Revert on error
      setTasks((prevTasks) =>
        prevTasks.map((t) =>
          t.id === draggedTaskId ? { ...t, status: oldStatus } : t
        )
      );
      setUpdateError(
        `Failed to update task: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    } finally {
      setDraggedTaskId(null);
    }
  };

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
        Failed to load tasks: {error}
      </div>
    );
  }

  const byStatus = (status: string) => tasks.filter((t) => t.status === status);
  const columnLabels: Record<string, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    failed: 'Failed',
  };

  return (
    <div className="space-y-6">
      <StatsBar />
      <div className="flex items-center gap-2">
        <Kanban className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Task Board</h2>
      </div>

      {updateError && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {updateError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map((status) => (
          <div
            key={status}
            className="bg-gray-50 rounded-lg p-4 min-h-[200px]"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, status)}
          >
            <h3 className="font-medium text-gray-700 mb-3">{columnLabels[status]}</h3>
            <div className="space-y-3">
              {byStatus(status).map((task) => (
                <TaskCard key={task.id} task={task} onDragStart={handleDragStart} />
              ))}
              {byStatus(status).length === 0 && (
                <div className="text-center py-8 text-gray-400 text-sm">No tasks</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
