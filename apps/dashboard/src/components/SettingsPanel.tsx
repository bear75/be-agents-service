/**
 * SettingsPanel - Configuration and system info
 * Shows service health, LaunchD status, and config overview.
 */
import { useEffect, useState } from 'react';
import { Settings, Server, Database, Clock } from 'lucide-react';

interface HealthStatus {
  success: boolean;
  service: string;
  version: string;
  timestamp: string;
  features?: string[];
}

export function SettingsPanel() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/../health')
      .then((r) => {
        // The proxy routes /api to 4010, but /health is at root
        // Use /api route for consistency
        return fetch('/health');
      })
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {
        // Try directly
        fetch('http://localhost:4010/health')
          .then((r) => r.json())
          .then(setHealth)
          .catch((e) => setError(e.message));
      });
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <Settings className="w-5 h-5" /> Settings & System
      </h2>

      {/* Service Health */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
          <Server className="w-4 h-4" /> API Server
        </h3>
        {error ? (
          <p className="text-red-600 text-sm">Error connecting: {error}</p>
        ) : health ? (
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              <span className="font-medium">{health.service}</span>
              <span className="text-gray-500">v{health.version}</span>
            </div>
            <div className="text-gray-500">
              <Clock className="inline w-3.5 h-3.5 mr-1" />
              {new Date(health.timestamp).toLocaleString()}
            </div>
            {health.features && (
              <div className="flex flex-wrap gap-1 mt-2">
                {health.features.map((f) => (
                  <span key={f} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{f}</span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Checking health...</p>
        )}
      </div>

      {/* Architecture Overview */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
          <Database className="w-4 h-4" /> Architecture
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="p-3 bg-blue-50 rounded-md">
            <h4 className="font-medium text-blue-900 mb-1">Structured Data (SQLite)</h4>
            <ul className="text-blue-700 space-y-0.5 text-xs">
              <li>Teams, Agents, Commands</li>
              <li>Sessions, Tasks, Metrics</li>
              <li>RL Experiments, Patterns</li>
              <li>Leads, Campaigns, Content</li>
              <li>LLM Usage, Costs</li>
            </ul>
          </div>
          <div className="p-3 bg-green-50 rounded-md">
            <h4 className="font-medium text-green-900 mb-1">Unstructured Data (Markdown)</h4>
            <ul className="text-green-700 space-y-0.5 text-xs">
              <li>Ideas, Brainstorms, Notes</li>
              <li>Priorities (human input)</li>
              <li>Check-ins, Follow-ups</li>
              <li>Memory (decisions, learnings)</li>
              <li>Agent Reports</li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Endpoints Reference */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4">API Endpoints</h3>
        <div className="font-mono text-xs space-y-1 text-gray-600">
          <p><span className="text-green-600">GET</span> /api/repos — Configured repositories</p>
          <p><span className="text-green-600">GET</span> /api/workspace/:repo/overview — Workspace data</p>
          <p><span className="text-green-600">GET</span> /api/sessions — Session history</p>
          <p><span className="text-green-600">GET</span> /api/teams — Teams and agents</p>
          <p><span className="text-green-600">GET</span> /api/metrics/stats — Dashboard stats</p>
          <p><span className="text-green-600">GET</span> /api/metrics/tasks — All tasks (Kanban)</p>
          <p><span className="text-green-600">GET</span> /api/marketing/campaigns — Marketing data</p>
          <p><span className="text-blue-600">POST</span> /api/sessions — Create session</p>
          <p><span className="text-blue-600">POST</span> /api/commands — Track command</p>
        </div>
      </div>
    </div>
  );
}
