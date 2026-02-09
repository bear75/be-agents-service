/**
 * Engineering - start jobs, view agents, sessions
 */
import { useEffect, useState } from 'react';
import { Cpu, Play, Square, RefreshCw } from 'lucide-react';
import {
  getJobs,
  startJob,
  stopJob,
  getJobLogs,
  getHrAgents,
} from '../lib/api';
import type { JobInfo, DbAgent } from '../types';

export function EngineeringPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [agents, setAgents] = useState<DbAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [form, setForm] = useState({
    team: 'engineering' as const,
    priorityFile: 'reports/priorities-' + new Date().toISOString().slice(0, 10) + '.md',
    branchName: 'feature/auto-' + Date.now(),
    model: 'sonnet',
  });
  const [selectedJobLogs, setSelectedJobLogs] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([getJobs(), getHrAgents()])
      .then(([j, a]) => {
        setJobs(Array.isArray(j) ? j : []);
        setAgents((Array.isArray(a) ? a : []).filter((x) => x.team_id?.includes('engineering') || x.is_active !== false));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleStart = () => {
    setStarting(true);
    startJob(form)
      .then(() => {
        load();
        setStarting(false);
      })
      .catch((e) => {
        setError(e.message);
        setStarting(false);
      });
  };

  const handleStop = (jobId: string) => {
    stopJob(jobId).then(load);
  };

  const handleViewLogs = (jobId: string) => {
    getJobLogs(jobId).then(setSelectedJobLogs);
  };

  if (loading && jobs.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-2">
        <Cpu className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Engineering</h2>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:underline">Dismiss</button>
        </div>
      )}

      {/* Start job form */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4">Start Engineering Job</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label>
            <span className="block text-sm text-gray-600 mb-1">Priority file</span>
            <input
              type="text"
              value={form.priorityFile}
              onChange={(e) => setForm({ ...form, priorityFile: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
              placeholder="reports/priorities-2026-02-09.md"
            />
          </label>
          <label>
            <span className="block text-sm text-gray-600 mb-1">Branch name</span>
            <input
              type="text"
              value={form.branchName}
              onChange={(e) => setForm({ ...form, branchName: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
              placeholder="feature/auto-123"
            />
          </label>
          <label>
            <span className="block text-sm text-gray-600 mb-1">Model</span>
            <select
              value={form.model}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="sonnet">Sonnet</option>
              <option value="opus">Opus</option>
            </select>
          </label>
        </div>
        <button
          onClick={handleStart}
          disabled={starting}
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Play className="w-4 h-4" /> {starting ? 'Starting…' : 'Start Job'}
        </button>
      </div>

      {/* Jobs list */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h3 className="font-medium text-gray-900">Running Jobs</h3>
          <button onClick={load} className="text-gray-500 hover:text-gray-700">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <div className="divide-y">
          {jobs.map((job) => (
            <div key={job.jobId} className="px-4 py-3 flex items-center justify-between">
              <div>
                <span className="font-mono text-sm">{job.jobId}</span>
                <span className={`ml-2 px-2 py-0.5 text-xs rounded ${
                  job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  job.status === 'completed' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {job.status}
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleViewLogs(job.jobId)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Logs
                </button>
                {job.status === 'running' && (
                  <button
                    onClick={() => handleStop(job.jobId)}
                    className="inline-flex items-center gap-1 text-red-600 hover:underline"
                  >
                    <Square className="w-4 h-4" /> Stop
                  </button>
                )}
              </div>
            </div>
          ))}
          {jobs.length === 0 && (
            <div className="py-8 text-center text-gray-500 text-sm">No jobs</div>
          )}
        </div>
      </div>

      {/* Agents */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <h3 className="px-4 py-3 border-b font-medium text-gray-900">Agents</h3>
        <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          {agents.map((a) => (
            <div key={a.id} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
              <span className="text-2xl">{a.emoji || '🤖'}</span>
              <div>
                <div className="font-medium text-sm">{a.name}</div>
                <div className="text-xs text-gray-500">{a.role}</div>
              </div>
            </div>
          ))}
          {agents.length === 0 && (
            <div className="col-span-full py-4 text-center text-gray-500 text-sm">No agents</div>
          )}
        </div>
      </div>

      {/* Logs modal */}
      {selectedJobLogs !== null && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedJobLogs(null)}
        >
          <div
            className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-4 py-2 border-b flex justify-between">
              <span className="font-medium">Job Logs</span>
              <button onClick={() => setSelectedJobLogs(null)} className="text-gray-500 hover:text-gray-700">
                Close
              </button>
            </div>
            <pre className="p-4 overflow-auto text-xs font-mono bg-gray-900 text-gray-100 flex-1 whitespace-pre-wrap">
              {selectedJobLogs}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
