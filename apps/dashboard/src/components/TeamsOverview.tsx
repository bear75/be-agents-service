/**
 * TeamsOverview - Display teams and their agents from SQLite
 * Shows team cards with agent lists and performance stats.
 */
import { useEffect, useState } from 'react';
import { Users, Cpu, BarChart3 } from 'lucide-react';
import { getTeams, getTeam } from '../lib/api';
import type { Team } from '../types';

const DOMAIN_COLORS: Record<string, string> = {
  engineering: 'border-blue-200 bg-blue-50',
  marketing: 'border-purple-200 bg-purple-50',
  management: 'border-amber-200 bg-amber-50',
  operations: 'border-green-200 bg-green-50',
  'schedule-optimization': 'border-teal-200 bg-teal-50',
};

const DOMAIN_BADGES: Record<string, string> = {
  engineering: 'bg-blue-100 text-blue-800',
  marketing: 'bg-purple-100 text-purple-800',
  management: 'bg-amber-100 text-amber-800',
  operations: 'bg-green-100 text-green-800',
  'schedule-optimization': 'bg-teal-100 text-teal-800',
};

const DOMAIN_ICONS: Record<string, string> = {
  engineering: '⚙️',
  marketing: '📊',
  management: '👔',
  operations: '🔗',
  'schedule-optimization': '🕐',
};

export function TeamsOverview() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [expandedTeam, setExpandedTeam] = useState<string | null>(null);
  const [teamDetail, setTeamDetail] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTeams()
      .then(setTeams)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function toggleTeam(teamId: string) {
    if (expandedTeam === teamId) {
      setExpandedTeam(null);
      setTeamDetail(null);
      return;
    }
    setExpandedTeam(teamId);
    try {
      const d = await getTeam(teamId);
      setTeamDetail(d);
    } catch (e) {
      console.error(e);
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading teams...</div>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
        <Users className="w-5 h-5" /> Teams & Agents
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {teams.map((team) => (
          <div
            key={team.id}
            className={`rounded-lg border-2 cursor-pointer transition-shadow hover:shadow-md ${DOMAIN_COLORS[team.domain] || 'border-gray-200 bg-gray-50'}`}
            onClick={() => toggleTeam(team.id)}
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-gray-900">
                  {DOMAIN_ICONS[team.domain] || '📋'} {team.name}
                </h3>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${DOMAIN_BADGES[team.domain] || ''}`}>
                  {team.domain}
                </span>
              </div>
              <p className="text-sm text-gray-600">{team.description}</p>
            </div>

            {expandedTeam === team.id && teamDetail && teamDetail.agents && (
              <div className="border-t border-gray-200 p-4 bg-white/70">
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Agents ({teamDetail.agents.length})
                </h4>
                <div className="space-y-2">
                  {teamDetail.agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{agent.emoji || '🤖'}</span>
                        <div>
                          <span className="font-medium text-gray-900">{agent.name}</span>
                          <span className="text-gray-500 ml-2">{agent.role}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1" title="LLM preference">
                          <Cpu className="w-3 h-3" /> {agent.llm_preference}
                        </span>
                        <span className="flex items-center gap-1" title="Success rate">
                          <BarChart3 className="w-3 h-3" /> {(agent.success_rate * 100).toFixed(0)}%
                        </span>
                        <span>{agent.total_tasks_completed} done</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
