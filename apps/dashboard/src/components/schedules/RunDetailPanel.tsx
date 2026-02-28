/**
 * Detail panel for a single schedule run (metrics, insights, actions)
 */
import type { ScheduleRun } from '../../types';
import { GoalBadge, unassignedStatus, efficiencyStatus, continuityStatus } from './GoalBadge';
import { cancelScheduleRun } from '../../lib/api';
import { useState } from 'react';

interface RunDetailPanelProps {
  run: ScheduleRun;
  onClose: () => void;
  onCancel?: () => void;
}

export function RunDetailPanel({ run, onClose, onCancel }: RunDetailPanelProps) {
  const [cancelling, setCancelling] = useState(false);

  const handleCancel = async () => {
    if (run.status !== 'running' && run.status !== 'queued') return;
    setCancelling(true);
    try {
      await cancelScheduleRun(run.id, 'Cancelled from dashboard');
      onCancel?.();
    } finally {
      setCancelling(false);
    }
  };

  const canCancel = run.status === 'running' || run.status === 'queued';

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm p-4 text-sm">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-mono font-semibold">{run.id}</h3>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
          aria-label="Close"
        >
          ×
        </button>
      </div>
      <div className="space-y-2">
        <p><span className="text-gray-500">Status:</span> {run.status}</p>
        <p><span className="text-gray-500">Algorithm:</span> {run.algorithm}</p>
        <p><span className="text-gray-500">Strategy:</span> {run.strategy}</p>
        {run.hypothesis && (
          <p><span className="text-gray-500">Hypothesis:</span> {run.hypothesis}</p>
        )}
      </div>
      {(run.routing_efficiency_pct != null || run.unassigned_pct != null || run.continuity_avg != null) && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <h4 className="font-medium text-gray-700 mb-2">Metrics</h4>
          <ul className="space-y-1">
            {run.routing_efficiency_pct != null && (
              <li>
                Routing efficiency: {run.routing_efficiency_pct.toFixed(2)}%{' '}
                <GoalBadge status={efficiencyStatus(run.routing_efficiency_pct)} />
              </li>
            )}
            {run.unassigned_visits != null && run.total_visits != null && (
              <li>
                Unassigned: {run.unassigned_visits} ({run.unassigned_pct?.toFixed(2)}%){' '}
                <GoalBadge status={unassignedStatus(run.unassigned_pct)} />
              </li>
            )}
            {run.continuity_avg != null && (
              <li>
                Continuity avg: {run.continuity_avg.toFixed(1)} (target ≤{run.continuity_target ?? 11}){' '}
                <GoalBadge status={continuityStatus(run.continuity_avg, run.continuity_target ?? 11)} />
              </li>
            )}
            {run.timefold_score && (
              <li><span className="text-gray-500">Score:</span> {run.timefold_score}</li>
            )}
          </ul>
        </div>
      )}
      <div className="mt-4 pt-3 border-t border-gray-100 flex gap-2">
        {canCancel && (
          <button
            type="button"
            onClick={handleCancel}
            disabled={cancelling}
            className="px-3 py-1.5 text-xs rounded border border-red-200 text-red-700 hover:bg-red-50 disabled:opacity-50"
          >
            {cancelling ? 'Cancelling…' : 'Cancel run'}
          </button>
        )}
        <button
          type="button"
          onClick={onClose}
          className="px-3 py-1.5 text-xs rounded border border-gray-200 text-gray-700 hover:bg-gray-50"
        >
          Close
        </button>
      </div>
    </div>
  );
}
