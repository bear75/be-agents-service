/**
 * StatsBar - Top-level dashboard statistics
 * Shows session, task, agent, and experiment counts from SQLite.
 */
import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, Users, FlaskConical } from 'lucide-react';
import { getDashboardStats } from '../lib/api';
import type { DashboardStats } from '../types';

export function StatsBar() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(console.error);
  }, []);

  if (!stats) return null;

  const cards = [
    { label: 'Sessions', value: stats.totalSessions, sub: `${stats.activeSessions ?? 0} active`, icon: Activity, color: 'text-blue-600 bg-blue-50' },
    { label: 'Tasks Done', value: stats.completedTasks ?? 0, sub: `${stats.totalTasks} total`, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: 'Tasks Failed', value: stats.failedTasks ?? 0, sub: '', icon: XCircle, color: 'text-red-600 bg-red-50' },
    { label: 'Agents', value: stats.activeAgents ?? 0, sub: `${stats.totalAgents} total`, icon: Users, color: 'text-purple-600 bg-purple-50' },
    { label: 'Experiments', value: stats.activeExperiments ?? 0, sub: `${stats.totalExperiments} total`, icon: FlaskConical, color: 'text-amber-600 bg-amber-50' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className={`p-1.5 rounded-md ${c.color}`}>
              <c.icon className="w-4 h-4" />
            </div>
            <span className="text-xs font-medium text-gray-500 uppercase">{c.label}</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{c.value}</div>
          {c.sub && <div className="text-xs text-gray-500 mt-1">{c.sub}</div>}
        </div>
      ))}
    </div>
  );
}
