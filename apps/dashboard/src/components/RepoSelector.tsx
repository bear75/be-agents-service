/**
 * Repository Selector Component
 * Dropdown to switch between repositories.
 * Overlay is portaled to document.body so it is not clipped by the header and always visible above other content.
 */
import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
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
  const triggerRef = useRef<HTMLButtonElement>(null);
  const [dropdownRect, setDropdownRect] = useState<{ top: number; left: number; width: number } | null>(null);

  useEffect(() => {
    const loadRepos = async () => {
      try {
        setLoading(true);
        const data = await listRepositories();
        setRepos(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load repositories');
      } finally {
        setLoading(false);
      }
    };

    loadRepos();
  }, []);

  useEffect(() => {
    if (!isOpen || !triggerRef.current) {
      setDropdownRect(null);
      return;
    }
    const el = triggerRef.current;
    const rect = el.getBoundingClientRect();
    setDropdownRect({
      top: rect.bottom + 8,
      left: rect.left,
      width: Math.max(rect.width, 200),
    });
  }, [isOpen]);

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

  const overlay =
    isOpen && typeof document !== 'undefined' ? (
      createPortal(
        <>
          {/* Backdrop: above layout (z-50), subtle so page is still visible */}
          <div
            className="fixed inset-0 z-50 bg-black/20"
            onClick={() => setIsOpen(false)}
            aria-hidden
          />
          {/* Dropdown: positioned under the trigger, above backdrop */}
          {dropdownRect && (
            <div
              className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto min-w-[200px]"
              style={{
                top: dropdownRect.top,
                left: dropdownRect.left,
                width: dropdownRect.width,
              }}
              role="listbox"
              aria-label="Select repository"
            >
              <button
                type="button"
                onClick={() => {
                  onChange('');
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 ${
                  !value ? 'bg-blue-50' : ''
                }`}
              >
                <GitBranch className={`w-5 h-5 shrink-0 ${!value ? 'text-blue-600' : 'text-gray-400'}`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${!value ? 'text-blue-900' : 'text-gray-900'}`}>Overview</p>
                  <p className="text-xs text-gray-500">Quick start, how to get things done</p>
                </div>
              </button>
              {repos.map((repo) => (
                <button
                  type="button"
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
          )}
        </>,
        document.body,
      )
    ) : null;

  return (
    <div className="relative">
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <GitBranch className="w-5 h-5 text-gray-600" />
        <div className="flex flex-col items-start">
          <span className="text-sm font-medium text-gray-900">
            {selectedRepo ? selectedRepo.name : 'Overview'}
          </span>
          {selectedRepo && (
            <span className="text-xs text-gray-500">
              {selectedRepo.github.owner}/{selectedRepo.github.repo}
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>
      {overlay}
    </div>
  );
}
