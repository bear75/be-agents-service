/**
 * Agents Page - HR Dashboard
 * Hire, fire, and manage agents
 */
import { useEffect, useState } from 'react';
import { Users, UserPlus, UserMinus, TrendingUp } from 'lucide-react';
import { getHrAgents, createAgent, fireAgent, rehireAgent } from '../lib/api';
import type { DbAgent } from '../types';

export function AgentsPage() {
  const [agents, setAgents] = useState<DbAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHireModal, setShowHireModal] = useState(false);
  const [showFireModal, setShowFireModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<DbAgent | null>(null);

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

  const loadAgents = async () => {
    try {
      const data = await getHrAgents();
      // Handle both array and wrapped response
      const agentsArray = Array.isArray(data) ? data : (data.agents || []);
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
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{agent.emoji || '🤖'}</span>
                      <div>
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
                      onClick={() => {
                        setSelectedAgent(agent);
                        setShowFireModal(true);
                      }}
                      className="text-red-600 hover:text-red-700 p-1"
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
