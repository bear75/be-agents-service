/**
 * Pipeline view: Queued | Running | Completed | Cancelled
 */
import type { ScheduleRun } from '../../types';
import { RunCard } from './RunCard';

interface PipelineBoardProps {
  runs: ScheduleRun[];
  selectedId: string | null;
  onSelectRun: (id: string | null) => void;
}

export function PipelineBoard({ runs, selectedId, onSelectRun }: PipelineBoardProps) {
  const queued = runs.filter((r) => r.status === 'queued');
  const running = runs.filter((r) => r.status === 'running');
  const completed = runs.filter((r) => r.status === 'completed');
  const cancelled = runs.filter((r) => r.status === 'cancelled' || r.status === 'failed');

  const col = (title: string, list: ScheduleRun[]) => (
    <div className="flex-1 min-w-0 rounded border border-gray-200 bg-gray-50/50 p-2">
      <div className="text-xs font-semibold text-gray-600 mb-2">
        {title} ({list.length})
      </div>
      <div className="space-y-2">
        {list.length === 0 && <div className="text-xs text-gray-400">—</div>}
        {list.map((r) => (
          <RunCard
            key={r.id}
            run={r}
            onSelect={() => onSelectRun(selectedId === r.id ? null : r.id)}
          />
        ))}
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {col('Queued', queued)}
      {col('Running', running)}
      {col('Completed', completed)}
      {col('Cancelled', cancelled)}
    </div>
  );
}
