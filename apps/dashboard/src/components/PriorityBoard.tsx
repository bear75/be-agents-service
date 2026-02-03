/**
 * Priority Board Component
 * Displays prioritized tasks from a repository
 */
import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { getRepositoryPriorities } from '../lib/api';
import type { Priority } from '../types';

interface PriorityBoardProps {
  repoName: string;
}

export function PriorityBoard({ repoName }: PriorityBoardProps) {
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPriorities = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getRepositoryPriorities(repoName);
        setPriorities(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load priorities');
      } finally {
        setLoading(false);
      }
    };

    loadPriorities();
  }, [repoName]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">Error</p>
        </div>
        <p className="text-sm text-gray-600">{error}</p>
      </div>
    );
  }

  const getPriorityColor = (priority: Priority['priority']) => {
    switch (priority) {
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-gray-500 bg-gray-50';
    }
  };

  const getPriorityBadge = (priority: Priority['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: Priority['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'in-progress':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const highPriorities = priorities.filter((p) => p.priority === 'high');
  const mediumPriorities = priorities.filter((p) => p.priority === 'medium');
  const lowPriorities = priorities.filter((p) => p.priority === 'low');

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Priorities</h3>

        {priorities.length === 0 ? (
          <p className="text-sm text-gray-600">No priorities found</p>
        ) : (
          <div className="space-y-6">
            {/* High Priority */}
            {highPriorities.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">High Priority</h4>
                <div className="space-y-2">
                  {highPriorities.map((priority) => (
                    <div
                      key={priority.id}
                      className={`border-l-4 p-3 rounded ${getPriorityColor(priority.priority)}`}
                    >
                      <div className="flex items-start gap-2">
                        <div className="flex-shrink-0 mt-0.5">{getStatusIcon(priority.status)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500">#{priority.id}</span>
                            <span
                              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getPriorityBadge(priority.priority)}`}
                            >
                              {priority.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-900 break-words">{priority.title}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Medium Priority */}
            {mediumPriorities.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Medium Priority</h4>
                <div className="space-y-2">
                  {mediumPriorities.slice(0, 3).map((priority) => (
                    <div
                      key={priority.id}
                      className={`border-l-4 p-3 rounded ${getPriorityColor(priority.priority)}`}
                    >
                      <div className="flex items-start gap-2">
                        <div className="flex-shrink-0 mt-0.5">{getStatusIcon(priority.status)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500">#{priority.id}</span>
                            <span
                              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getPriorityBadge(priority.priority)}`}
                            >
                              {priority.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-900 break-words">{priority.title}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {mediumPriorities.length > 3 && (
                    <p className="text-xs text-gray-500 text-center py-2">
                      +{mediumPriorities.length - 3} more
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Low Priority - collapsed */}
            {lowPriorities.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Low Priority ({lowPriorities.length})
                </h4>
                <p className="text-xs text-gray-500">
                  {lowPriorities.length} low priority items (collapsed)
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
