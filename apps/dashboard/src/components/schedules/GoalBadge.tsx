/**
 * Goal badge: ✅ / ⚠️ / ❌ for unassigned%, efficiency%, continuity
 */
type Status = 'ok' | 'warn' | 'fail';

interface GoalBadgeProps {
  status: Status;
  label?: string;
  title?: string;
}

const statusMap: Record<Status, { char: string; className: string }> = {
  ok: { char: '✅', className: 'text-green-600' },
  warn: { char: '⚠️', className: 'text-amber-600' },
  fail: { char: '❌', className: 'text-red-600' },
};

export function GoalBadge({ status, label, title }: GoalBadgeProps) {
  const { char, className } = statusMap[status];
  return (
    <span className={className} title={title}>
      {char}
      {label != null && <span className="ml-0.5">{label}</span>}
    </span>
  );
}

/** Unassigned: ✅ <1% | ⚠️ 1–5% | ❌ >5% */
export function unassignedStatus(pct: number | null | undefined): Status {
  if (pct == null) return 'fail';
  if (pct < 1) return 'ok';
  if (pct <= 5) return 'warn';
  return 'fail';
}

/** Efficiency: ✅ ≥75% | ⚠️ 70–75% | ❌ <70% */
export function efficiencyStatus(pct: number | null | undefined): Status {
  if (pct == null) return 'fail';
  if (pct >= 75) return 'ok';
  if (pct >= 70) return 'warn';
  return 'fail';
}

/** Continuity avg: ✅ ≤11 | ⚠️ 11–15 | ❌ >15 */
export function continuityStatus(avg: number | null | undefined, target = 11): Status {
  if (avg == null) return 'fail';
  if (avg <= target) return 'ok';
  if (avg <= 15) return 'warn';
  return 'fail';
}
