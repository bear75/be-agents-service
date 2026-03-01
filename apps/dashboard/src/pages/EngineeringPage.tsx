/**
 * Compound - start jobs, no duplicate agents (Roster = single source)
 */
import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Cpu, Play, Square, RefreshCw, Users } from 'lucide-react';
import { getJobs, startJob, stopJob, getJobLogs, clearAllJobs, listRepositories, getTeams, createSession } from '../lib/api';
import type { JobInfo } from '../types';

const DEFAULT_REPO = 'appcaire';

export function EngineeringPage() {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [repos, setRepos] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [form, setForm] = useState({
    team: 'engineering' as const,
    targetRepo: DEFAULT_REPO,
    model: 'sonnet',
  });
  const [selectedJobLogs, setSelectedJobLogs] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([getJobs(), listRepositories()])
      .then(([jobsData, reposData]) => {
        setJobs(Array.isArray(jobsData) ? jobsData : []);
        setRepos((reposData ?? []).map((r) => r.name).filter(Boolean));
      })
      .catch((e) => setError(String(e.message)))
      .finally(() => setLoading(false));
  };

  /** Find engineering team id for session creation */
  const getEngineeringTeamId = async (): Promise<string | null> => {
    const teamList = await getTeams();
    const eng = teamList.find((t) => t.domain === 'engineering');
    return eng?.id ?? null;
  };

  useEffect(() => {
    load();
  }, []);

  const handleStart = async () => {
    setStarting(true);
    setError(null);
    try {
      const sessionId = `session-${Date.now()}`;
      const teamId = await getEngineeringTeamId();
      if (teamId) {
        await createSession({ sessionId, teamId, targetRepo: form.targetRepo });
      }
      await startJob({
        team: form.team,
        targetRepo: form.targetRepo,
        model: form.model,
        sessionId,
      });
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setStarting(false);
    }
  };

  const handleStop = (jobId: string) => {
    stopJob(jobId).then(load);
  };

  const handleViewLogs = (jobId: string) => {
    getJobLogs(jobId).then(setSelectedJobLogs);
  };

  const handleClearAll = () => {
    if (!confirm('Ta bort alla jobb från listan (loggar raderas)?')) return;
    setClearing(true);
    clearAllJobs()
      .then(() => load())
      .catch((e) => setError(String(e.message)))
      .finally(() => setClearing(false));
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
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Cpu className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Compound</h2>
        </div>
        <p className="text-sm text-gray-500">
          Picks priority #1 from repo, creates PRD, runs engineering specialists (agents + target-repo prompts + gamification), opens draft PR. Nightly 23:00 or start here / terminal: <code className="bg-gray-100 px-1 rounded text-xs">./scripts/compound/auto-compound.sh &lt;repo-name&gt;</code>
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:underline">Dismiss</button>
        </div>
      )}

      {/* Start job form */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4">Start Compound Workflow</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label>
            <span className="block text-sm text-gray-600 mb-1">Repo</span>
            <select
              value={form.targetRepo}
              onChange={(e) => setForm({ ...form, targetRepo: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
            >
              {repos.length > 0 ? (
                repos.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))
              ) : (
                <option value={DEFAULT_REPO}>{DEFAULT_REPO}</option>
              )}
            </select>
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
        <p className="text-xs text-gray-500 mt-2">
          Uses all engineering agents, target-repo prompts (soul), and records session + tasks for Work and Leaderboard.
        </p>
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
        <div className="px-4 py-3 border-b flex items-center justify-between gap-2">
          <h3 className="font-medium text-gray-900">Running Jobs</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleClearAll}
              disabled={clearing || jobs.length === 0}
              className="text-sm text-amber-600 hover:text-amber-700 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Rensa alla jobb från listan"
            >
              {clearing ? 'Rensar…' : 'Rensa alla jobb'}
            </button>
            <button onClick={load} className="text-gray-500 hover:text-gray-700" title="Uppdatera">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
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

      {/* Agents: single source = Roster */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <Link
          to="/roster"
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 hover:underline"
        >
          <Users className="w-5 h-5" />
          View agents & teams in Roster
        </Link>
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
