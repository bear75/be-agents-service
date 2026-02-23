/**
 * ControlTower - Sprint launch and agent control panel
 * Start new sessions, select team & model, view running agents.
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Rocket, RefreshCw } from 'lucide-react';
import { getTeams, listRepositories, createSession, getActiveSessions } from '../lib/api';
import type { Team, Session } from '../types';

export function ControlTower() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [repos, setRepos] = useState<string[]>([]);
  const [activeSessions, setActiveSessions] = useState<Session[]>([]);

  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedRepo, setSelectedRepo] = useState('');
  const [branchName, setBranchName] = useState('');
  const [launching, setLaunching] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    getTeams().then(setTeams).catch(console.error);
    listRepositories()
      .then((r) => setRepos(r.map((repo) => repo.name)))
      .catch(console.error);
    refreshActive();
  }, []);

  function refreshActive() {
    getActiveSessions().then(setActiveSessions).catch(console.error);
  }

  async function handleLaunch() {
    if (!selectedTeam || !selectedRepo) {
      setMessage('Please select a team and repository.');
      return;
    }
    setLaunching(true);
    setMessage('');
    try {
      const sessionId = `session-${Date.now()}`;
      await createSession({
        sessionId,
        teamId: selectedTeam,
        targetRepo: selectedRepo,
        branchName: branchName || undefined,
      });
      setMessage(`Session ${sessionId} created successfully.`);
      refreshActive();
    } catch (e) {
      setMessage(`Error: ${e instanceof Error ? e.message : 'Unknown error'}`);
    } finally {
      setLaunching(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Rocket className="w-5 h-5" /> Control Tower
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Launch sessions (DB records). For compound, use <Link to="/run" className="text-blue-600 hover:underline">Compound</Link> or terminal: <code className="bg-gray-100 px-1 rounded text-xs">auto-compound.sh beta-appcaire</code>
        </p>
      </div>

      {/* Launch form */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4">Launch New Session</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Team</label>
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">Select team...</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Repository</label>
            <select
              value={selectedRepo}
              onChange={(e) => setSelectedRepo(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">Select repo...</option>
              {repos.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Branch (optional)</label>
            <input
              type="text"
              value={branchName}
              onChange={(e) => setBranchName(e.target.value)}
              placeholder="feature/my-branch"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={handleLaunch}
            disabled={launching}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Rocket className="w-4 h-4" />
            {launching ? 'Launching...' : 'Launch Session'}
          </button>
          {message && (
            <span className={`text-sm ${message.startsWith('Error') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </span>
          )}
        </div>
      </div>

      {/* Active sessions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-gray-900">Active Sessions</h3>
          <button
            onClick={refreshActive}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>
        {activeSessions.length === 0 ? (
          <p className="text-sm text-gray-500">No active sessions.</p>
        ) : (
          <div className="space-y-2">
            {activeSessions.map((s) => (
              <div key={s.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <span className="font-medium">{s.team_name || s.team_id}</span>
                  <span className="text-gray-500 ml-2">{s.target_repo}</span>
                </div>
                <span className="px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-800">
                  {s.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
