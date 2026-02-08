/**
 * Memory Viewer Component
 * Displays memory files (decisions, learnings, context) as tabs
 */
import { useEffect, useState } from 'react';
import { Brain, Clock, AlertCircle } from 'lucide-react';
import { getWorkspaceMemory } from '../lib/api';
import type { MemoryEntry } from '../types';

interface MemoryViewerProps {
  repoName: string;
}

export function MemoryViewer({ repoName }: MemoryViewerProps) {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFile, setActiveFile] = useState<string>('');

  useEffect(() => {
    const loadMemory = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getWorkspaceMemory(repoName);
        setEntries(data);
        if (data.length > 0) {
          setActiveFile(data[0].filename);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load memory');
      } finally {
        setLoading(false);
      }
    };

    loadMemory();
  }, [repoName]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
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

  const activeEntry = entries.find((e) => e.filename === activeFile);

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-amber-600" />
          <h3 className="text-lg font-semibold text-gray-900">Memory</h3>
        </div>

        {entries.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No memory files found
          </p>
        ) : (
          <>
            {/* File tabs */}
            <div className="flex border-b border-gray-200 mb-4">
              {entries.map((entry) => (
                <button
                  key={entry.filename}
                  onClick={() => setActiveFile(entry.filename)}
                  className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeFile === entry.filename
                      ? 'border-amber-500 text-amber-700'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {entry.title}
                </button>
              ))}
            </div>

            {/* Content */}
            {activeEntry && (
              <div>
                <div className="flex items-center gap-1 mb-2">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-400">
                    Last modified: {new Date(activeEntry.lastModified).toLocaleDateString()}
                  </span>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                    {activeEntry.content.replace(/^#.*\n+/, '')}
                  </pre>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
