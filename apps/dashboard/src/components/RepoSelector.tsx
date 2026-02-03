/**
 * Repository Selector Component
 * Dropdown to switch between repositories
 */
import { useEffect, useState } from 'react';
import { ChevronDown, GitBranch } from 'lucide-react';
import { listRepositories } from '../lib/api';
import type { Repository } from '../types';

interface RepoSelectorProps {
  value: string;
  onChange: (repoName: string) => void;
}

export function RepoSelector({ value, onChange }: RepoSelectorProps) {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const loadRepos = async () => {
      try {
        setLoading(true);
        const data = await listRepositories();
        setRepos(data);

        // If no value set and repos loaded, select first one
        if (!value && data.length > 0) {
          onChange(data[0].name);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load repositories');
      } finally {
        setLoading(false);
      }
    };

    loadRepos();
  }, []);

  const selectedRepo = repos.find((r) => r.name === value);

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
        <GitBranch className="w-5 h-5 text-gray-400" />
        <span className="text-sm text-gray-600">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-lg">
        <span className="text-sm text-red-600">{error}</span>
      </div>
    );
  }

  if (repos.length === 0) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-yellow-50 rounded-lg">
        <span className="text-sm text-yellow-600">No repositories configured</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <GitBranch className="w-5 h-5 text-gray-600" />
        <div className="flex flex-col items-start">
          <span className="text-sm font-medium text-gray-900">
            {selectedRepo?.name || 'Select Repository'}
          </span>
          {selectedRepo && (
            <span className="text-xs text-gray-500">{selectedRepo.github.owner}/{selectedRepo.github.repo}</span>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute top-full mt-2 left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-64 overflow-y-auto">
            {repos.map((repo) => (
              <button
                key={repo.name}
                onClick={() => {
                  onChange(repo.name);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                  repo.name === value ? 'bg-blue-50' : ''
                }`}
              >
                <GitBranch
                  className={`w-5 h-5 ${repo.name === value ? 'text-blue-600' : 'text-gray-400'}`}
                />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${repo.name === value ? 'text-blue-900' : 'text-gray-900'}`}>
                    {repo.name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {repo.github.owner}/{repo.github.repo}
                  </p>
                </div>
                {repo.enabled ? (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    Enabled
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    Disabled
                  </span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
