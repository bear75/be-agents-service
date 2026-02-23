/**
 * Agents Page - HR Dashboard
 * Hire, fire, and manage agents
 */
import { useEffect, useState } from 'react';
import { Users, UserPlus, UserMinus, ChevronDown, ChevronRight, FileCode, FileText } from 'lucide-react';
import { getHrAgents, createAgent, fireAgent, rehireAgent, getAgentScript, getAgentPrompt, listRepositories } from '../lib/api';
import type { DbAgent } from '../types';

export function AgentsPage() {
  const [agents, setAgents] = useState<DbAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHireModal, setShowHireModal] = useState(false);
  const [showFireModal, setShowFireModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<DbAgent | null>(null);
  const [agentScript, setAgentScript] = useState<string | null>(null);
  const [agentPrompt, setAgentPrompt] = useState<string | null>(null);
  const [agentContentError, setAgentContentError] = useState<string | null>(null);
  const [repos, setRepos] = useState<string[]>([]);
  const [promptRepo, setPromptRepo] = useState('beta-appcaire');
  const [showScript, setShowScript] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);

  // Hire form state
  const [hireForm, setHireForm] = useState({
    teamId: 'team-engineering',
    name: '',
    role: '',
    llmPreference: 'sonnet',
    emoji: '🤖'
  });

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    listRepositories().then((r) => setRepos(r.map((x) => x.name))).catch(() => {});
  }, []);

  useEffect(() => {
    if (!showDetailModal || !selectedAgent) {
      setAgentScript(null);
      setAgentPrompt(null);
      setAgentContentError(null);
      return;
    }
    setAgentContentError(null);
    getAgentScript(selectedAgent.id)
      .then(setAgentScript)
      .catch((e) => setAgentContentError((s) => (s ? `${s}; ` : '') + `Script: ${e.message}`));
    getAgentPrompt(selectedAgent.id, promptRepo)
      .then(setAgentPrompt)
      .catch((e) => setAgentContentError((s) => (s ? `${s}; ` : '') + `Prompt: ${e.message}`));
  }, [showDetailModal, selectedAgent?.id, promptRepo]);

  const loadAgents = async () => {
    try {
      const data = await getHrAgents();
      // Handle both array and wrapped response
      const agentsArray = Array.isArray(data) ? data : ((data as { agents?: DbAgent[] }).agents ?? []);
      setAgents(agentsArray);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleHire = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createAgent(hireForm);
      setShowHireModal(false);
      setHireForm({
        teamId: 'team-engineering',
        name: '',
        role: '',
        llmPreference: 'sonnet',
        emoji: '🤖'
      });
      await loadAgents();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to hire agent');
    }
  };

  const handleFire = async () => {
    if (!selectedAgent) return;
    try {
      await fireAgent(selectedAgent.id);
      setShowFireModal(false);
      setSelectedAgent(null);
      await loadAgents();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to fire agent');
    }
  };

  const handleRehire = async (agentId: string) => {
    try {
      await rehireAgent(agentId);
      await loadAgents();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to rehire agent');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const activeAgents = agents.filter(a => a.is_active);
  const inactiveAgents = agents.filter(a => !a.is_active);
  const engineeringAgents = activeAgents.filter(a => a.team_name?.includes('Engineering'));
  const marketingAgents = activeAgents.filter(a => a.team_name?.includes('Marketing'));
  const managementAgents = activeAgents.filter(a => a.team_name?.includes('Management'));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Agent Management</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHireModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            Hire Agent
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Where prompts & scripts live (inline info, no links) */}
      <div className="rounded-lg bg-gray-50 border border-gray-200 p-4 text-sm">
        <div className="font-medium text-gray-900 mb-1">Where agent content lives</div>
        <div className="text-gray-700 font-mono text-xs">
          Prompts: target repo <code className="bg-gray-200 px-1 rounded">.claude/prompts/*.md</code> · Scripts: <code className="bg-gray-200 px-1 rounded">agents/*.sh</code>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Total Active</div>
          <div className="text-2xl font-bold text-gray-900">{activeAgents.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Engineering</div>
          <div className="text-2xl font-bold text-blue-600">{engineeringAgents.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Marketing</div>
          <div className="text-2xl font-bold text-green-600">{marketingAgents.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Management</div>
          <div className="text-2xl font-bold text-orange-600">{managementAgents.length}</div>
        </div>
      </div>

      {/* Active Agents by Team */}
      <div className="space-y-6">
        {[
          { title: 'Engineering Team', agents: engineeringAgents, color: 'blue' },
          { title: 'Marketing Team', agents: marketingAgents, color: 'green' },
          { title: 'Management Team', agents: managementAgents, color: 'orange' }
        ].map(({ title, agents: teamAgents, color }) => (
          <div key={title} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <h3 className="px-4 py-3 border-b font-medium text-gray-900 flex items-center gap-2">
              {title}
              <span className={`text-${color}-600 font-bold`}>({teamAgents.length})</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
              {teamAgents.map((agent) => (
                <div
                  key={agent.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  role="button"
                  tabIndex={0}
                  onClick={() => {
                    setSelectedAgent(agent);
                    setShowDetailModal(true);
                  }}
                  onKeyDown={(e) => e.key === 'Enter' && (setSelectedAgent(agent), setShowDetailModal(true))}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <span className="text-3xl">{agent.emoji || '🤖'}</span>
                      <div className="min-w-0">
                        <div className="font-medium text-gray-900">{agent.name}</div>
                        <div className="text-sm text-gray-500">{agent.role}</div>
                        {agent.llm_preference && (
                          <div className="mt-1 text-xs text-blue-600 font-mono">
                            {agent.llm_preference}
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedAgent(agent);
                        setShowFireModal(true);
                      }}
                      className="text-red-600 hover:text-red-700 p-1 shrink-0"
                      title="Fire agent"
                    >
                      <UserMinus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
              {teamAgents.length === 0 && (
                <div className="col-span-full text-center py-8 text-gray-400">
                  No agents in this team
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Inactive Agents */}
      {inactiveAgents.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <h3 className="px-4 py-3 border-b font-medium text-gray-900 flex items-center gap-2">
            Inactive Agents
            <span className="text-gray-600">({inactiveAgents.length})</span>
          </h3>
          <div className="divide-y">
            {inactiveAgents.map((agent) => (
              <div
                key={agent.id}
                className="px-4 py-3 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl opacity-50">{agent.emoji || '🤖'}</span>
                  <div>
                    <div className="font-medium text-gray-700">{agent.name}</div>
                    <div className="text-sm text-gray-500">{agent.role}</div>
                  </div>
                </div>
                <button
                  onClick={() => handleRehire(agent.id)}
                  className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                >
                  Rehire
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hire Modal */}
      {showHireModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Hire New Agent</h3>
            <form onSubmit={handleHire} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team
                </label>
                <select
                  value={hireForm.teamId}
                  onChange={(e) => setHireForm({ ...hireForm, teamId: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  required
                >
                  <option value="team-engineering">Engineering</option>
                  <option value="team-marketing">Marketing</option>
                  <option value="team-management">Management</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={hireForm.name}
                  onChange={(e) => setHireForm({ ...hireForm, name: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="e.g., API Specialist"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <input
                  type="text"
                  value={hireForm.role}
                  onChange={(e) => setHireForm({ ...hireForm, role: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="e.g., Develop REST APIs"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LLM Preference
                </label>
                <select
                  value={hireForm.llmPreference}
                  onChange={(e) => setHireForm({ ...hireForm, llmPreference: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  <option value="sonnet">Sonnet</option>
                  <option value="opus">Opus</option>
                  <option value="haiku">Haiku</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Emoji
                </label>
                <input
                  type="text"
                  value={hireForm.emoji}
                  onChange={(e) => setHireForm({ ...hireForm, emoji: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="🤖"
                  maxLength={2}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowHireModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Hire Agent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Agent Details</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{selectedAgent.emoji || '🤖'}</span>
                <div>
                  <div className="font-medium text-gray-900">{selectedAgent.name}</div>
                  <div className="text-gray-500">{selectedAgent.role}</div>
                </div>
              </div>
              {selectedAgent.role && (
                <div>
                  <div className="text-gray-500 font-medium mb-1">Description / competence</div>
                  <p className="text-gray-700">{selectedAgent.role}</p>
                </div>
              )}
              <div><span className="text-gray-500">Team:</span> {selectedAgent.team_name || '—'}</div>
              <div><span className="text-gray-500">LLM:</span> {selectedAgent.llm_preference || '—'}</div>
              <div><span className="text-gray-500">Active:</span> {selectedAgent.is_active ? 'Yes' : 'No'}</div>
              {selectedAgent.created_at != null && (
                <div><span className="text-gray-500">Created:</span> {new Date(selectedAgent.created_at).toLocaleString()}</div>
              )}
              {agentContentError && (
                <p className="text-amber-700 bg-amber-50 rounded p-2 text-xs">{agentContentError}</p>
              )}
              <div className="mt-4 pt-4 border-t space-y-3">
                <div>
                  <button
                    type="button"
                    onClick={() => setShowScript((v) => !v)}
                    className="flex items-center gap-2 w-full text-left font-medium text-gray-900 hover:text-blue-600"
                  >
                    {showScript ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    <FileCode className="w-4 h-4" /> Script (agents/*.sh)
                  </button>
                  {showScript && (
                    <pre className="mt-2 p-3 bg-gray-900 text-gray-100 text-xs rounded overflow-x-auto max-h-48 overflow-y-auto">
                      {agentScript ?? 'Loading…'}
                    </pre>
                  )}
                </div>
                <div>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <button
                      type="button"
                      onClick={() => setShowPrompt((v) => !v)}
                      className="flex items-center gap-2 text-left font-medium text-gray-900 hover:text-blue-600"
                    >
                      {showPrompt ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                      <FileText className="w-4 h-4" /> Prompt (.claude/prompts/*.md)
                    </button>
                    {repos.length > 0 && (
                      <select
                        value={promptRepo}
                        onChange={(e) => setPromptRepo(e.target.value)}
                        className="text-xs border rounded px-2 py-1"
                      >
                        {repos.map((r) => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    )}
                  </div>
                  {showPrompt && (
                    <pre className="mt-2 p-3 bg-gray-50 text-gray-800 text-xs rounded overflow-x-auto max-h-64 overflow-y-auto whitespace-pre-wrap">
                      {agentPrompt ?? 'Loading…'}
                    </pre>
                  )}
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => {
                  setSelectedAgent(selectedAgent);
                  setShowDetailModal(false);
                  setShowFireModal(true);
                }}
                className="flex-1 px-4 py-2 text-red-600 border border-red-200 rounded hover:bg-red-50"
              >
                Fire agent
              </button>
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedAgent(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fire Modal */}
      {showFireModal && selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Fire Agent</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to fire <strong>{selectedAgent.name}</strong>?
              They can be rehired later from the inactive agents list.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowFireModal(false);
                  setSelectedAgent(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleFire}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Fire Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
