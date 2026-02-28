/**
 * SVG scatter plot: X = continuity (avg), Y = efficiency %
 * Goal zone: X ≤ 11, Y ≥ 70%
 */
import type { ScheduleRun } from '../../types';

const W = 400;
const H = 280;
const PAD = { left: 44, right: 24, top: 24, bottom: 40 };
const X_MAX = 25;
const Y_MIN = 0;
const Y_MAX = 100;
const TARGET_X = 11;
const TARGET_Y = 70;

interface ScatterPlotProps {
  runs: ScheduleRun[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

function scaleX(x: number) {
  return PAD.left + (x / X_MAX) * (W - PAD.left - PAD.right);
}

/** Y axis: efficiency 0–100%; screen y increases downward so high efficiency = top */
function scaleY(y: number) {
  return PAD.top + (1 - (y - Y_MIN) / (Y_MAX - Y_MIN)) * (H - PAD.top - PAD.bottom);
}

function getContinuity(r: ScheduleRun): number | null {
  return r.continuity_visit_weighted_avg ?? r.continuity_avg ?? null;
}

function getEfficiency(r: ScheduleRun): number | null {
  return r.efficiency_min_visit_pct ?? r.routing_efficiency_pct ?? null;
}

export function ScatterPlot({ runs, selectedId, onSelect }: ScatterPlotProps) {
  const completed = runs.filter(
    (r) => r.status === 'completed' && getContinuity(r) != null && getEfficiency(r) != null
  );
  const running = runs.filter((r) => r.status === 'running');

  const goalZoneX2 = scaleX(TARGET_X);
  const goalZoneYTop = scaleY(Y_MAX);      // top of chart (100%)
  const goalZoneYBottom = scaleY(TARGET_Y); // Y=70% line

  return (
    <div className="border border-gray-200 rounded-lg bg-white p-2">
      <div className="text-xs text-gray-500 mb-1 font-medium">Efficiency % (Y) vs Continuity (X) — goal: top-left (eff ≥70%, continuity ≤11)</div>
      <svg width={W} height={H} className="overflow-visible">
        {/* Goal zone: top-left — X ≤ 11, Y ≥ 70% */}
        <rect
          x={PAD.left}
          y={goalZoneYTop}
          width={goalZoneX2 - PAD.left}
          height={Math.max(0, goalZoneYBottom - goalZoneYTop)}
          fill="rgba(34,197,94,0.15)"
          stroke="rgba(34,197,94,0.5)"
          strokeWidth={1}
        />
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
          y1={goalZoneYBottom}
          x2={W - PAD.right}
          y2={goalZoneYBottom}
          stroke="rgba(34,197,94,0.6)"
          strokeWidth={1}
          strokeDasharray="4,2"
        />
        <line x1={PAD.left} y1={H - PAD.bottom} x2={W - PAD.right} y2={H - PAD.bottom} stroke="#e5e7eb" strokeWidth={1} />
        <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={H - PAD.bottom} stroke="#e5e7eb" strokeWidth={1} />
        <text x={PAD.left - 8} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">0</text>
        <text x={scaleX(TARGET_X) - 6} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">11</text>
        <text x={W - PAD.right - 20} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">25</text>
        <text x={PAD.left - 28} y={PAD.top + 4} className="fill-gray-500 text-[10px]">100%</text>
        <text x={PAD.left - 28} y={goalZoneYBottom + 4} className="fill-gray-500 text-[10px]">70%</text>
        <text x={PAD.left - 28} y={H - PAD.bottom + 4} className="fill-gray-500 text-[10px]">0%</text>
        {completed.map((r) => {
          const cont = getContinuity(r) ?? 0;
          const eff = getEfficiency(r) ?? 0;
          const x = scaleX(Math.min(cont, X_MAX));
          const y = scaleY(Math.max(Y_MIN, Math.min(Y_MAX, eff)));
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
                {r.id} — eff {eff.toFixed(1)}% continuity {cont.toFixed(1)} unassigned {r.unassigned_pct?.toFixed(2)}%
              </title>
            </g>
          );
        })}
        {running.map((r) => {
          const cont = getContinuity(r) ?? 0;
          const eff = getEfficiency(r) ?? 0;
          const x = scaleX(Math.min(cont, X_MAX));
          const y = scaleY(Math.max(Y_MIN, Math.min(Y_MAX, eff)));
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
