/**
 * Compact card for pipeline board (queued / running / completed)
 */
import type { ScheduleRun } from '../../types';
import { GoalBadge, unassignedStatus, efficiencyStatus, continuityStatus } from './GoalBadge';

interface RunCardProps {
  run: ScheduleRun;
  onSelect?: () => void;
}

export function RunCard({ run, onSelect }: RunCardProps) {
  const isComplete = run.status === 'completed';
  const isCancelled = run.status === 'cancelled' || run.status === 'failed';
  const isRunning = run.status === 'running';
  const isQueued = run.status === 'queued';

  return (
    <div
      className={`rounded border p-2 text-sm ${
        isCancelled ? 'border-red-200 bg-red-50' : isRunning ? 'border-blue-200 bg-blue-50' : isQueued ? 'border-gray-200 bg-gray-50' : 'border-gray-200 bg-white'
      } ${onSelect ? 'cursor-pointer hover:ring-1 hover:ring-blue-300' : ''}`}
      onClick={onSelect}
      role={onSelect ? 'button' : undefined}
    >
      <div className="font-mono text-xs font-medium">
        {isComplete && '✅'}
        {isCancelled && '✗'}
        {isRunning && '◉'}
        {isQueued && '►'} {run.id}
      </div>
      <div className="mt-0.5 text-gray-600 truncate" title={run.strategy}>
        {run.algorithm}
      </div>
      {isComplete && run.routing_efficiency_pct != null && (
        <div className="mt-1 flex gap-2 flex-wrap">
          <GoalBadge status={efficiencyStatus(run.routing_efficiency_pct)} />
          {run.unassigned_pct != null && (
            <GoalBadge status={unassignedStatus(run.unassigned_pct)} />
          )}
          {run.continuity_avg != null && (
            <GoalBadge status={continuityStatus(run.continuity_avg, run.continuity_target ?? 11)} />
          )}
          <span className="text-gray-500">
            eff {run.routing_efficiency_pct.toFixed(1)}% · u {run.unassigned_pct?.toFixed(2)}% · c {run.continuity_avg?.toFixed(1)}
          </span>
        </div>
      )}
      {isRunning && run.timefold_score && (
        <div className="mt-1 text-gray-500 text-xs truncate">{run.timefold_score}</div>
      )}
    </div>
  );
}
