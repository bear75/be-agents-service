/**
 * SVG scatter plot: X = continuity avg, Y = unassigned%
 * Goal zone: X ≤ 11, Y < 1%
 */
import type { ScheduleRun } from '../../types';

const W = 400;
const H = 280;
const PAD = { left: 48, right: 24, top: 24, bottom: 40 };
const X_MAX = 25;
const Y_MAX = 5;
const TARGET_X = 11;
const TARGET_Y = 1;

interface ScatterPlotProps {
  runs: ScheduleRun[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

function scaleX(x: number) {
  return PAD.left + (x / X_MAX) * (W - PAD.left - PAD.right);
}

function scaleY(y: number) {
  return PAD.top + (1 - y / Y_MAX) * (H - PAD.top - PAD.bottom);
}

export function ScatterPlot({ runs, selectedId, onSelect }: ScatterPlotProps) {
  const completed = runs.filter(
    (r) => r.status === 'completed' && r.continuity_avg != null && r.unassigned_pct != null
  );
  const running = runs.filter((r) => r.status === 'running');

  const goalZoneX1 = scaleX(0);
  const goalZoneX2 = scaleX(TARGET_X);
  const goalZoneY1 = scaleY(TARGET_Y);
  const goalZoneY2 = scaleY(0);

  return (
    <div className="border border-gray-200 rounded-lg bg-white p-2">
      <div className="text-xs text-gray-500 mb-1 font-medium">Unassigned % (Y) vs Continuity avg (X) — goal: bottom-left</div>
      <svg width={W} height={H} className="overflow-visible">
        {/* Goal zone */}
        <rect
          x={PAD.left}
          y={goalZoneY2}
          width={goalZoneX2 - PAD.left}
          height={goalZoneY1 - goalZoneY2}
          fill="rgba(34,197,94,0.15)"
          stroke="rgba(34,197,94,0.5)"
          strokeWidth={1}
        />
        {/* Target lines */}
        <line
          x1={scaleX(TARGET_X)}
          y1={PAD.top}
          x2={scaleX(TARGET_X)}
          y2={H - PAD.bottom}
          stroke="rgba(34,197,94,0.6)"
          strokeWidth={1}
          strokeDasharray="4,2"
        />
        <line
          x1={PAD.left}
          y1={goalZoneY1}
          x2={W - PAD.right}
          y2={goalZoneY1}
          stroke="rgba(34,197,94,0.6)"
          strokeWidth={1}
          strokeDasharray="4,2"
        />
        {/* Axes */}
        <line x1={PAD.left} y1={H - PAD.bottom} x2={W - PAD.right} y2={H - PAD.bottom} stroke="#e5e7eb" strokeWidth={1} />
        <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={H - PAD.bottom} stroke="#e5e7eb" strokeWidth={1} />
        <text x={PAD.left - 8} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">0</text>
        <text x={scaleX(TARGET_X) - 6} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">11</text>
        <text x={W - PAD.right - 16} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">25</text>
        <text x={PAD.left - 4} y={PAD.top + 4} className="fill-gray-500 text-[10px]">5%</text>
        <text x={PAD.left - 4} y={goalZoneY1 + 4} className="fill-gray-500 text-[10px]">1%</text>
        {/* Points: completed */}
        {completed.map((r) => {
          const x = scaleX(r.continuity_avg ?? 0);
          const y = scaleY(Math.min(r.unassigned_pct ?? 0, Y_MAX));
          const eff = r.routing_efficiency_pct ?? 0;
          const green = Math.round(128 + (eff / 100) * 127);
          const isSelected = selectedId === r.id;
          return (
            <g
              key={r.id}
              onClick={() => onSelect(selectedId === r.id ? null : r.id)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={x}
                cy={y}
                r={isSelected ? 8 : 6}
                fill={`rgb(34,${green},94)`}
                stroke={isSelected ? '#111' : '#fff'}
                strokeWidth={isSelected ? 2 : 1}
              />
              <title>
                {r.id} — eff {eff.toFixed(1)}% unassigned {r.unassigned_pct?.toFixed(2)}% continuity {r.continuity_avg?.toFixed(1)}
              </title>
            </g>
          );
        })}
        {/* Running (grey) */}
        {running.map((r) => {
          const x = scaleX(r.continuity_avg ?? 0);
          const y = scaleY(Math.min(r.unassigned_pct ?? 0, Y_MAX));
          return (
            <circle
              key={r.id}
              cx={x}
              cy={y}
              r={6}
              fill="#9ca3af"
              stroke="#6b7280"
              strokeWidth={1}
              className="animate-pulse"
            />
          );
        })}
      </svg>
    </div>
  );
}
