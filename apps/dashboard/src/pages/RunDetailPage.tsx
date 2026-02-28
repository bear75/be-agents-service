/**
 * Run detail page: metrics JSON charts, metrics report text, continuity table, PDF link.
 * Reads from shared huddinge-datasets via API (run folder metrics + continuity.csv).
 */
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getScheduleRun,
  getRunMetricsJson,
  getRunMetricsReport,
  getRunContinuity,
  getDatasetAssetUrl,
} from '../lib/api';
import type { ScheduleRun } from '../types';

interface MetricsJson {
  shift_time_h?: number;
  visit_time_h?: number;
  travel_time_h?: number;
  wait_time_h?: number;
  break_time_h?: number;
  inactive_time_h?: number;
  shift_hours_min_visit?: number;
  idle_hours_min_visit?: number;
  shift_hours_visit_span?: number;
  idle_hours_visit_span?: number;
  routing_efficiency_pct?: number;
  field_efficiency_pct?: number;
  unassigned_visits?: number;
  total_visits_assigned?: number;
  visit_revenue_kr?: number;
  shift_cost_kr?: number;
  margin_kr?: number;
  margin_pct?: number;
  score?: string;
  [key: string]: unknown;
}

const TIME_SEGMENTS = [
  { key: 'visit_time_h' as const, label: 'Visit', color: 'bg-emerald-500' },
  { key: 'travel_time_h' as const, label: 'Travel', color: 'bg-amber-500' },
  { key: 'wait_time_h' as const, label: 'Wait', color: 'bg-amber-300' },
  { key: 'idle', label: 'Idle', color: 'bg-slate-300' },
];

function parseContinuityCsv(csv: string): { client: string; nr_visits: number; continuity: number }[] {
  const lines = csv.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());
  const ci = headers.findIndex((h) => h === 'client' || h === 'client_id');
  const ni = headers.findIndex((h) => h === 'nr_visits' || h === 'visits');
  const conti = headers.findIndex((h) => h === 'continuity' || h === 'distinct_caregivers' || h === 'n_vehicles');
  if (ci < 0 || conti < 0) return [];
  const rows: { client: string; nr_visits: number; continuity: number }[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = lines[i].split(',');
    const continuity = parseFloat(cells[conti]?.trim() ?? '');
    if (!Number.isFinite(continuity)) continue;
    rows.push({
      client: cells[ci]?.trim() ?? '',
      nr_visits: ni >= 0 ? parseInt(cells[ni]?.trim() ?? '0', 10) : 0,
      continuity,
    });
  }
  return rows;
}

export function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<ScheduleRun | null>(null);
  const [metrics, setMetrics] = useState<MetricsJson | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [continuityCsv, setContinuityCsv] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportOpen, setReportOpen] = useState(false);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      getScheduleRun(id),
      getRunMetricsJson(id),
      getRunMetricsReport(id),
      getRunContinuity(id),
    ])
      .then(([r, m, rep, csv]) => {
        if (cancelled) return;
        setRun(r ?? null);
        setMetrics(m ?? null);
        setReport(rep ?? null);
        setContinuityCsv(csv ?? null);
        if (!r) setError('Run not found');
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load run');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  if (loading && !run) {
    return (
      <div className="p-6 text-gray-500">Loading run…</div>
    );
  }
  if (error && !run) {
    return (
      <div className="p-6">
        <p className="text-red-600">{error}</p>
        <Link to="/schedules" className="text-blue-600 hover:underline mt-2 inline-block">← Back to Schedules</Link>
      </div>
    );
  }
  if (!run) return null;

  const continuityRows = continuityCsv ? parseContinuityCsv(continuityCsv) : [];
  const breakH = metrics?.break_time_h ?? 0;
  const visitH = metrics?.visit_time_h ?? 0;
  const travelH = metrics?.travel_time_h ?? 0;
  const waitH = metrics?.wait_time_h ?? 0;

  // Same visit, travel, wait for all three. Only total and idle differ:
  // 1 = all shifts: total = shift − break, idle = lots (idle_hours_all)
  // 2 = min 1 visit: total = shift_hours_min_visit − break, idle = less (idle_hours_min_visit)
  // 3 = visit span: total = shift_hours_visit_span, idle = 0
  const shiftHoursAll = metrics?.shift_hours_all ?? metrics?.shift_time_h;
  const shiftHoursMinVisit = metrics?.shift_hours_min_visit;
  const shiftHoursVisitSpan = metrics?.shift_hours_visit_span;
  const idleAll = metrics?.idle_hours_all ?? metrics?.inactive_time_h ?? 0;
  const idleMinVisit = metrics?.idle_hours_min_visit ?? 0;

  const total1 = (metrics?.shift_time_h ?? shiftHoursAll ?? 0) - breakH;
  const total2 = (shiftHoursMinVisit ?? 0) - breakH;
  const total3 = shiftHoursVisitSpan ?? 0;

  const threeCharts = metrics
    ? [
        {
          label: 'Eff 3: Visit span',
          pct: run.efficiency_visit_span_pct ?? undefined,
          activeShiftHours: shiftHoursVisitSpan ?? undefined,
          total: total3,
          segments: [visitH, travelH, waitH, 0],
          desc: 'First visit → last visit per shift. No idle.',
        },
        {
          label: 'Eff 1: All shifts',
          pct: run.efficiency_all_pct ?? undefined,
          activeShiftHours: shiftHoursAll ?? undefined,
          total: total1,
          segments: [visitH, travelH, waitH, idleAll],
          desc: 'All shift hours (excl. break). Idle: lots.',
        },
        {
          label: 'Eff 2: Min 1 visit',
          pct: run.efficiency_min_visit_pct ?? undefined,
          activeShiftHours: shiftHoursMinVisit ?? undefined,
          total: total2,
          segments: [visitH, travelH, waitH, idleMinVisit],
          desc: 'Shifts with ≥1 visit (excl. break). Idle: less.',
        },
      ].filter((c) => c.total > 0)
    : [];

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/schedules" className="text-sm text-gray-500 hover:text-gray-700">← Schedules</Link>
          <h1 className="text-xl font-semibold text-gray-900 mt-1 font-mono">{run.id}</h1>
          <p className="text-sm text-gray-600 mt-0.5">
            {run.algorithm ? <span className="font-medium">Algorithm: {run.algorithm}</span> : null}
            {run.algorithm && run.strategy ? ' · ' : null}
            {run.strategy}
          </p>
          {run.hypothesis && <p className="text-sm text-gray-500 italic mt-1">{run.hypothesis}</p>}
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          run.status === 'completed' ? 'bg-green-100 text-green-800' :
          run.status === 'running' ? 'bg-blue-100 text-blue-800' :
          run.status === 'queued' ? 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-600'
        }`}>
          {run.status}
        </span>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {run.routing_efficiency_pct != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Routing efficiency</p>
            <p className="text-2xl font-semibold text-gray-900">{run.routing_efficiency_pct.toFixed(1)}%</p>
            <p className="text-xs text-gray-500 mt-1">Target ≥70%</p>
          </div>
        )}
        {run.unassigned_pct != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Unassigned</p>
            <p className="text-2xl font-semibold text-gray-900">{run.unassigned_pct.toFixed(2)}%</p>
            <p className="text-xs text-gray-500 mt-1">{run.unassigned_visits ?? 0} / {run.total_visits ?? 0} visits</p>
          </div>
        )}
        {run.continuity_avg != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Continuity (mean)</p>
            <p className="text-2xl font-semibold text-gray-900">{run.continuity_avg.toFixed(1)}</p>
            <p className="text-xs text-gray-500 mt-1">Per-client average · target ≤{run.continuity_target ?? 11}</p>
          </div>
        )}
        {run.continuity_median != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Continuity (median)</p>
            <p className="text-2xl font-semibold text-gray-900">{run.continuity_median.toFixed(1)}</p>
            <p className="text-xs text-gray-500 mt-1">Middle value</p>
          </div>
        )}
        {run.continuity_visit_weighted_avg != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Continuity (% avg)</p>
            <p className="text-2xl font-semibold text-gray-900">{run.continuity_visit_weighted_avg.toFixed(1)}</p>
            <p className="text-xs text-gray-500 mt-1">Visit-weighted: 10 visits × 10 = 1:10 vs 100 visits × 10</p>
          </div>
        )}
        {metrics?.margin_pct != null && (
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Margin</p>
            <p className="text-2xl font-semibold text-gray-900">{metrics.margin_pct.toFixed(1)}%</p>
            <p className="text-xs text-gray-500 mt-1">{metrics.margin_kr != null ? `${(metrics.margin_kr / 1000).toFixed(0)}k kr` : ''}</p>
          </div>
        )}
      </div>

      {/* Shifts: input vs output; shift hours total / idle / trimmed; efficiency */}
      {(run.input_shifts != null || run.output_shifts_trimmed != null || run.shift_hours_total != null) && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-800 mb-4">Shifts & efficiency</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Input shifts</p>
              <p className="font-semibold text-gray-900">{run.input_shifts ?? '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Input shift hours</p>
              <p className="font-semibold text-gray-900">{run.input_shift_hours != null ? run.input_shift_hours.toFixed(0) : '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Shift h total (incl idle)</p>
              <p className="font-semibold text-gray-900">{run.shift_hours_total != null ? run.shift_hours_total.toFixed(0) : '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Shift h idle</p>
              <p className="font-semibold text-gray-900">{run.shift_hours_idle != null ? run.shift_hours_idle.toFixed(0) : '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Shift h trimmed</p>
              <p className="font-semibold text-gray-900">{run.output_shift_hours_trimmed != null ? run.output_shift_hours_trimmed.toFixed(0) : '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Output shifts (trimmed)</p>
              <p className="font-semibold text-gray-900">{run.output_shifts_trimmed ?? '—'}</p>
            </div>
          </div>
        </section>
      )}

      {/* 3 efficiency charts: Visit, Travel, Wait, Idle (break excl.) */}
      {threeCharts.length > 0 && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-800 mb-1">3 efficiency definitions</h2>
          <p className="text-xs text-gray-500 mb-4">Visit, Travel, Wait, Idle. Break excluded (non-assignable). Target ≥70%.</p>
          <div className="space-y-6">
            {threeCharts.map(({ label, pct, activeShiftHours, total, segments: segs, desc }) => {
              const segments = [
                { h: segs[0], ...TIME_SEGMENTS[0] },
                { h: segs[1], ...TIME_SEGMENTS[1] },
                { h: segs[2], ...TIME_SEGMENTS[2] },
                { h: segs[3], ...TIME_SEGMENTS[3] },
              ].filter((s) => s.h > 0);
              return (
                <div key={label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-800">{label}</span>
                    <span className="text-sm text-gray-900 tabular-nums flex items-center gap-2">
                      {activeShiftHours != null && (
                        <span className="text-gray-500 font-normal">{activeShiftHours.toFixed(0)} h</span>
                      )}
                      <span className="font-semibold">{pct != null ? `${pct.toFixed(1)}%` : '—'}</span>
                    </span>
                  </div>
                  <div className="flex h-7 rounded-md overflow-hidden bg-gray-100">
                    {segments.map((s) => (
                      <div
                        key={s.label}
                        className={`${s.color} flex items-center justify-center min-w-0 text-white text-xs font-medium`}
                        style={{ width: `${(s.h / total) * 100}%` }}
                        title={`${s.label}: ${s.h.toFixed(0)}h`}
                      >
                        {(s.h / total) * 100 >= 8 ? s.label : ''}
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{desc}</p>
                </div>
              );
            })}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-4 pt-4 border-t border-gray-100 text-xs text-gray-600">
            {TIME_SEGMENTS.map((s) => (
              <span key={s.label}>
                <span className={`inline-block w-3 h-3 rounded ${s.color} align-middle mr-1`} />
                {s.label}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Continuity distribution */}
      {continuityRows.length > 0 && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-800 mb-4">Continuity per client (distinct caregivers)</h2>
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-50">
                <tr>
                  <th className="text-left py-2 px-2 font-medium text-gray-700">Client</th>
                  <th className="text-right py-2 px-2 font-medium text-gray-700">Visits</th>
                  <th className="text-right py-2 px-2 font-medium text-gray-700">Continuity</th>
                </tr>
              </thead>
              <tbody>
                {continuityRows.slice(0, 100).map((row, i) => (
                  <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="py-1.5 px-2 font-mono text-gray-800">{row.client}</td>
                    <td className="py-1.5 px-2 text-right text-gray-600">{row.nr_visits}</td>
                    <td className="py-1.5 px-2 text-right">
                      <span className={row.continuity > (run.continuity_target ?? 11) ? 'text-amber-600 font-medium' : 'text-gray-800'}>
                        {row.continuity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {continuityRows.length > 100 && (
            <p className="text-xs text-gray-500 mt-2">Showing first 100 of {continuityRows.length} clients</p>
          )}
        </section>
      )}

      {/* Metrics report (collapsible) */}
      {report && (
        <section className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          <button
            type="button"
            onClick={() => setReportOpen(!reportOpen)}
            className="w-full px-6 py-3 text-left text-sm font-semibold text-gray-800 bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
          >
            Full metrics report
            <span className="text-gray-500">{reportOpen ? '▼' : '▶'}</span>
          </button>
          {reportOpen && (
            <pre className="p-6 text-xs text-gray-700 whitespace-pre-wrap font-mono max-h-96 overflow-auto bg-white border-t border-gray-100">
              {report}
            </pre>
          )}
        </section>
      )}

      {/* PDF link */}
      <div className="flex flex-wrap gap-4 items-center text-sm">
        <a
          href={getDatasetAssetUrl('Attendo_Schedule_Pilot_Report.pdf')}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline font-medium"
        >
          Attendo Schedule Pilot Report (PDF) →
        </a>
      </div>
    </div>
  );
}
