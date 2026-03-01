import { useEffect, useState } from 'react';
import { Activity, RefreshCw } from 'lucide-react';
import { getSystemHealth } from '../lib/api';
import type { SystemHealth } from '../types';

const OVERALL_STYLE: Record<SystemHealth['overall'], string> = {
  healthy: 'bg-green-100 text-green-800 border-green-200',
  degraded: 'bg-amber-100 text-amber-800 border-amber-200',
  unhealthy: 'bg-red-100 text-red-800 border-red-200',
};

interface Props {
  defaultDeep?: boolean;
}

function BoolPill({ value, label }: { value: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
        value ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}
    >
      {label}: {value ? 'OK' : 'Fail'}
    </span>
  );
}

export function SystemHealthCard({ defaultDeep = false }: Props) {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deep, setDeep] = useState(defaultDeep);

  const load = async (useDeep: boolean, showSpinner = false) => {
    try {
      if (showSpinner) setRefreshing(true);
      setError(null);
      const data = await getSystemHealth(useDeep);
      setHealth(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load system health');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void load(deep, false);
  }, [deep]);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">System Health</h3>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-600 flex items-center gap-1">
            <input
              type="checkbox"
              checked={deep}
              onChange={(e) => setDeep(e.target.checked)}
              className="rounded border-gray-300"
            />
            Deep
          </label>
          <button
            type="button"
            onClick={() => void load(deep, true)}
            className="inline-flex items-center gap-1 rounded border border-gray-300 px-2 py-1 text-xs hover:bg-gray-50"
          >
            <RefreshCw className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Loading health checks…</div>
      ) : error ? (
        <div className="text-sm rounded border border-red-200 bg-red-50 px-3 py-2 text-red-700">
          {error}
        </div>
      ) : health ? (
        <>
          <div className={`inline-flex items-center rounded border px-2.5 py-1 text-sm font-medium ${OVERALL_STYLE[health.overall]}`}>
            Overall: {health.overall}
          </div>
          <div className="text-xs text-gray-500">
            Checked: {new Date(health.checkedAt).toLocaleString()} {health.deep ? '(deep)' : '(quick)'}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <BoolPill value={health.checks.workspace.ok} label="Workspace" />
            <BoolPill value={health.checks.openclaw.ok} label="OpenClaw" />
            <BoolPill value={health.checks.telegram.ok} label="Telegram" />
            <BoolPill value={health.checks.launchd.ok} label="Launchd" />
            <BoolPill value={health.checks.scripts.ok} label="Scripts" />
          </div>

          <div className="text-xs text-gray-600 space-y-1">
            <div>
              Workspace: {health.checks.workspace.path ?? 'not configured'}
            </div>
            <div>
              OpenClaw config: {health.checks.openclaw.configPath}
            </div>
            <div>
              Telegram env: token={health.checks.telegram.tokenPresent ? 'yes' : 'no'}, chat={health.checks.telegram.chatIdPresent ? 'yes' : 'no'}
            </div>
            {health.checks.scripts.missing.length > 0 && (
              <div className="text-red-600">
                Missing scripts: {health.checks.scripts.missing.join(', ')}
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
