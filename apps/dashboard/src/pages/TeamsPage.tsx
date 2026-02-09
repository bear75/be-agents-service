/**
 * Teams Page - View all teams and their performance
 */
import { useEffect, useState } from 'react';
import { Users } from 'lucide-react';
import { getTeams, getTeam } from '../lib/api';
import type { DbTeam, DbTeamWithDetails } from '../types';

export function TeamsPage() {
  const [teams, setTeams] = useState<DbTeam[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<DbTeamWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      const response = await getTeams();
      // Handle response format
      const data = Array.isArray(response) ? response : response.teams || [];
      setTeams(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const loadTeamDetails = async (teamId: string) => {
    setDetailsLoading(true);
    try {
      const response = await getTeam(teamId);
      // Handle response format
      const teamData = response.team || response;
      setSelectedTeam(teamData);
    } catch (e) {
      console.error('Failed to load team details:', e);
    } finally {
      setDetailsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Users className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Teams</h2>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Teams Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {teams.map((team) => (
          <button
            key={team.id}
            onClick={() => loadTeamDetails(team.id)}
            className={`bg-white rounded-lg border-2 p-6 text-left transition-all hover:shadow-md ${
              selectedTeam?.id === team.id
                ? 'border-blue-600'
                : 'border-gray-200'
            } ${
              team.domain === 'engineering'
                ? 'hover:border-blue-400'
                : team.domain === 'marketing'
                ? 'hover:border-green-400'
                : 'hover:border-orange-400'
            }`}
          >
            <div
              className={`text-3xl mb-3 ${
                team.domain === 'engineering'
                  ? 'text-blue-600'
                  : team.domain === 'marketing'
                  ? 'text-green-600'
                  : 'text-orange-600'
              }`}
            >
              {team.domain === 'engineering' ? '⚙️' : team.domain === 'marketing' ? '📢' : '👔'}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{team.name}</h3>
            <p className="text-sm text-gray-500 capitalize">{team.domain}</p>
            {team.description && (
              <p className="text-sm text-gray-600 mt-2 line-clamp-2">{team.description}</p>
            )}
          </button>
        ))}
      </div>

      {/* Team Details */}
      {selectedTeam && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900">{selectedTeam.name}</h3>
            <p className="text-sm text-gray-500 capitalize">{selectedTeam.domain}</p>
          </div>

          {detailsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          ) : (
            <>
              {/* Stats */}
              {selectedTeam.stats && (
                <div className="px-6 py-4 border-b bg-gray-50">
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Total Tasks</div>
                      <div className="text-xl font-bold text-gray-900">
                        {selectedTeam.stats.total_tasks}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Completed</div>
                      <div className="text-xl font-bold text-green-600">
                        {selectedTeam.stats.completed_tasks}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">In Progress</div>
                      <div className="text-xl font-bold text-blue-600">
                        {selectedTeam.stats.in_progress_tasks}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Failed</div>
                      <div className="text-xl font-bold text-red-600">
                        {selectedTeam.stats.failed_tasks}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase">Success Rate</div>
                      <div className="text-xl font-bold text-gray-900">
                        {selectedTeam.stats.success_rate}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Agents */}
              <div className="px-6 py-4">
                <h4 className="font-medium text-gray-900 mb-4">
                  Team Members ({selectedTeam.agents?.length || 0})
                </h4>
                {selectedTeam.agents && selectedTeam.agents.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedTeam.agents.map((agent) => (
                      <div
                        key={agent.id}
                        className="border border-gray-200 rounded-lg p-4"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">{agent.emoji || '🤖'}</span>
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{agent.name}</div>
                            <div className="text-sm text-gray-600">{agent.role}</div>
                            {agent.llm_preference && (
                              <div className="mt-1 text-xs text-blue-600 font-mono">
                                {agent.llm_preference}
                              </div>
                            )}
                            {agent.is_active === false && (
                              <div className="mt-1 text-xs text-red-600">Inactive</div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">No agents in this team</div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {teams.length === 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No teams found</h3>
          <p className="text-gray-500">Teams will appear here once they're created.</p>
        </div>
      )}
    </div>
  );
}
