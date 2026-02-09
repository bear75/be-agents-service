/**
 * Inbox View Component
 * Displays inbox items with checkboxes and a quick-add form
 */
import { useEffect, useState, useCallback } from 'react';
import { Inbox, Plus, AlertCircle, Tag } from 'lucide-react';
import { getWorkspaceInbox, addToInbox } from '../lib/api';
import type { InboxItem } from '../types';

interface InboxViewProps {
  repoName: string;
}

export function InboxView({ repoName }: InboxViewProps) {
  const [items, setItems] = useState<InboxItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newItemText, setNewItemText] = useState('');
  const [adding, setAdding] = useState(false);

  const loadItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getWorkspaceInbox(repoName);
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load inbox');
    } finally {
      setLoading(false);
    }
  }, [repoName]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemText.trim() || adding) return;

    try {
      setAdding(true);
      await addToInbox(repoName, newItemText.trim());
      setNewItemText('');
      await loadItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add item');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
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
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">Error</p>
        </div>
        <p className="text-sm text-gray-600">{error}</p>
      </div>
    );
  }

  const pendingItems = items.filter((i) => !i.done);
  const doneItems = items.filter((i) => i.done);

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Inbox className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Inbox</h3>
            {pendingItems.length > 0 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {pendingItems.length}
              </span>
            )}
          </div>
        </div>

        {/* Quick-add form */}
        <form onSubmit={handleAdd} className="flex gap-2 mb-4">
          <input
            type="text"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            placeholder="Add idea, task, or thought..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={adding}
          />
          <button
            type="submit"
            disabled={!newItemText.trim() || adding}
            className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
          </button>
        </form>

        {/* Pending items */}
        {pendingItems.length === 0 && doneItems.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            Inbox is empty. Drop ideas here!
          </p>
        ) : (
          <div className="space-y-1">
            {pendingItems.map((item) => (
              <div
                key={item.id}
                className="flex items-start gap-2 p-2 rounded hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={false}
                  readOnly
                  className="mt-1 w-4 h-4 text-blue-600 rounded"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{item.text}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {item.date && (
                      <span className="text-xs text-gray-400">{item.date}</span>
                    )}
                    {item.tags?.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-0.5 text-xs text-gray-500"
                      >
                        <Tag className="w-3 h-3" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            {/* Done items (collapsed) */}
            {doneItems.length > 0 && (
              <div className="pt-2 mt-2 border-t border-gray-100">
                <p className="text-xs text-gray-400 mb-1">
                  Done ({doneItems.length})
                </p>
                {doneItems.slice(0, 3).map((item) => (
                  <div
                    key={item.id}
                    className="flex items-start gap-2 p-1"
                  >
                    <input
                      type="checkbox"
                      checked
                      readOnly
                      className="mt-1 w-4 h-4 text-gray-400 rounded"
                    />
                    <p className="text-xs text-gray-400 line-through">
                      {item.text}
                    </p>
                  </div>
                ))}
                {doneItems.length > 3 && (
                  <p className="text-xs text-gray-400 pl-6">
                    +{doneItems.length - 3} more
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
