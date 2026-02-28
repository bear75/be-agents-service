/**
 * Pipeline view: focus on Completed; Queued / Running / Cancelled are collapsible.
 */
import { useState } from 'react';
import type { ScheduleRun } from '../../types';
import { RunCard } from './RunCard';

interface PipelineBoardProps {
  runs: ScheduleRun[];
  selectedId: string | null;
  onSelectRun: (id: string | null) => void;
}

export function PipelineBoard({ runs, selectedId, onSelectRun }: PipelineBoardProps) {
  const [showQueued, setShowQueued] = useState(false);
  const [showRunning, setShowRunning] = useState(false);
  const [showCancelled, setShowCancelled] = useState(false);

  const queued = runs.filter((r) => r.status === 'queued');
  const running = runs.filter((r) => r.status === 'running');
  const completed = runs.filter((r) => r.status === 'completed');
  const cancelled = runs.filter((r) => r.status === 'cancelled' || r.status === 'failed');

  const collapsible = (
    title: string,
    list: ScheduleRun[],
    expanded: boolean,
    onToggle: () => void,
  ) => (
    <div className="min-w-0 rounded border border-gray-200 bg-gray-50/50 overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full text-left text-xs font-semibold text-gray-600 px-2 py-1.5 hover:bg-gray-100 flex items-center justify-between"
      >
        <span>
          {title} ({list.length})
        </span>
        <span className="text-gray-400">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="px-2 pb-2 space-y-2 border-t border-gray-100">
          {list.length === 0 && <div className="text-xs text-gray-400 pt-2">—</div>}
          {list.map((r) => (
            <RunCard
              key={r.id}
              run={r}
              onSelect={() => onSelectRun(selectedId === r.id ? null : r.id)}
            />
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-3">
      {/* Collapsed: Queued, Running, Cancelled — single row of toggles */}
      <div className="grid grid-cols-3 gap-2">
        {collapsible('Queued', queued, showQueued, () => setShowQueued((v) => !v))}
        {collapsible('Running', running, showRunning, () => setShowRunning((v) => !v))}
        {collapsible('Cancelled', cancelled, showCancelled, () => setShowCancelled((v) => !v))}
      </div>

      {/* Focus: Completed — full width */}
      <div className="rounded border border-gray-200 bg-gray-50/50 p-3">
        <div className="text-xs font-semibold text-gray-600 mb-2">
          Completed ({completed.length})
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
          {completed.length === 0 && <div className="text-xs text-gray-400 col-span-full">—</div>}
          {completed.map((r) => (
            <RunCard
              key={r.id}
              run={r}
              onSelect={() => onSelectRun(selectedId === r.id ? null : r.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
