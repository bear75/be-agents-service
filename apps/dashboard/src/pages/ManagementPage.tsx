/**
 * Management Page - CEO Dashboard & Leaderboard
 */
import { useEffect, useState } from 'react';
import { Trophy, TrendingUp, Users, Target, Award } from 'lucide-react';
import { getTeams } from '../lib/api';
import type { DbTeam } from '../types';

interface LeaderboardEntry {
  agent_id: string;
  agent_name: string;
  agent_emoji: string;
  team_name: string;
  level: number;
  title: string;
  level_emoji: string;
  total_xp: number;
  achievements_count: number;
  current_streak: number;
  tasks_completed: number;
  success_rate_pct: number;
  xp_rank: number;
  tasks_rank: number;
  success_rank: number;
}

export function ManagementPage() {
  const [teams, setTeams] = useState<DbTeam[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [leaderboardMetric, setLeaderboardMetric] = useState<'xp' | 'tasks' | 'success'>('xp');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [teamsData, leaderboardData] = await Promise.all([
        getTeams(),
        fetch('/api/gamification/leaderboard').then(r => r.json())
      ]);

      const teamsArray = Array.isArray(teamsData) ? teamsData : (teamsData.teams || []);
      setTeams(teamsArray);
      setLeaderboard(Array.isArray(leaderboardData) ? leaderboardData : []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load management data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const sortedLeaderboard = [...leaderboard].sort((a, b) => {
    if (leaderboardMetric === 'xp') return a.xp_rank - b.xp_rank;
    if (leaderboardMetric === 'tasks') return a.tasks_rank - b.tasks_rank;
    return a.success_rank - b.success_rank;
  });

  const topPerformers = sortedLeaderboard.slice(0, 10);
  const totalXP = leaderboard.reduce((sum, agent) => sum + agent.total_xp, 0);
  const totalTasks = leaderboard.reduce((sum, agent) => sum + agent.tasks_completed, 0);
  const avgSuccessRate = leaderboard.length > 0
    ? leaderboard.reduce((sum, agent) => sum + agent.success_rate_pct, 0) / leaderboard.length
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Trophy className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Management Dashboard</h2>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Executive Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Users className="w-4 h-4" />
            Total Teams
          </div>
          <div className="text-2xl font-bold text-gray-900">{teams.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Target className="w-4 h-4" />
            Active Agents
          </div>
          <div className="text-2xl font-bold text-blue-600">{leaderboard.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Award className="w-4 h-4" />
            Total XP
          </div>
          <div className="text-2xl font-bold text-purple-600">{totalXP.toLocaleString()}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <TrendingUp className="w-4 h-4" />
            Avg Success Rate
          </div>
          <div className="text-2xl font-bold text-green-600">{avgSuccessRate.toFixed(0)}%</div>
        </div>
      </div>

      {/* Teams Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {teams.map((team) => {
          const teamAgents = leaderboard.filter(a =>
            a.team_name?.toLowerCase().includes(team.name.toLowerCase().split(' ')[0])
          );
          const teamXP = teamAgents.reduce((sum, a) => sum + a.total_xp, 0);
          const teamTasks = teamAgents.reduce((sum, a) => sum + a.tasks_completed, 0);

          return (
            <div
              key={team.id}
              className={`bg-white rounded-lg border-2 p-4 ${
                team.domain === 'engineering'
                  ? 'border-blue-200'
                  : team.domain === 'marketing'
                  ? 'border-green-200'
                  : 'border-orange-200'
              }`}
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">
                  {team.domain === 'engineering' ? '⚙️' : team.domain === 'marketing' ? '📢' : '👔'}
                </span>
                <div>
                  <h3 className="font-semibold text-gray-900">{team.name}</h3>
                  <p className="text-sm text-gray-500 capitalize">{team.domain}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <div className="text-gray-500">Agents</div>
                  <div className="font-bold text-gray-900">{teamAgents.length}</div>
                </div>
                <div>
                  <div className="text-gray-500">Total XP</div>
                  <div className="font-bold text-purple-600">{teamXP}</div>
                </div>
                <div>
                  <div className="text-gray-500">Tasks</div>
                  <div className="font-bold text-blue-600">{teamTasks}</div>
                </div>
                <div>
                  <div className="text-gray-500">Active</div>
                  <div className="font-bold text-green-600">
                    {teamAgents.filter(a => a.tasks_completed > 0).length}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Leaderboard */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h3 className="font-medium text-gray-900 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            Agent Leaderboard
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setLeaderboardMetric('xp')}
              className={`px-3 py-1 text-sm rounded ${
                leaderboardMetric === 'xp'
                  ? 'bg-purple-100 text-purple-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              XP
            </button>
            <button
              onClick={() => setLeaderboardMetric('tasks')}
              className={`px-3 py-1 text-sm rounded ${
                leaderboardMetric === 'tasks'
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Tasks
            </button>
            <button
              onClick={() => setLeaderboardMetric('success')}
              className={`px-3 py-1 text-sm rounded ${
                leaderboardMetric === 'success'
                  ? 'bg-green-100 text-green-700 font-medium'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Success Rate
            </button>
          </div>
        </div>

        <div className="divide-y">
          {topPerformers.map((agent, index) => {
            const rank = index + 1;
            const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : null;

            return (
              <div
                key={agent.agent_id}
                className={`px-4 py-3 flex items-center gap-4 ${
                  rank <= 3 ? 'bg-yellow-50' : 'hover:bg-gray-50'
                }`}
              >
                {/* Rank */}
                <div className="w-12 text-center">
                  {medal ? (
                    <span className="text-2xl">{medal}</span>
                  ) : (
                    <span className="text-lg font-bold text-gray-400">#{rank}</span>
                  )}
                </div>

                {/* Agent Info */}
                <div className="flex-1 flex items-center gap-3">
                  <span className="text-2xl">{agent.agent_emoji}</span>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{agent.agent_name}</div>
                    <div className="text-sm text-gray-500">{agent.team_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <span>{agent.level_emoji}</span>
                      <span>Level {agent.level}</span>
                      <span className="text-xs">({agent.title})</span>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="flex gap-6 text-sm">
                  <div className="text-center">
                    <div className="text-gray-500 text-xs">XP</div>
                    <div className="font-bold text-purple-600">{agent.total_xp}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-500 text-xs">Tasks</div>
                    <div className="font-bold text-blue-600">{agent.tasks_completed}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-500 text-xs">Success</div>
                    <div className="font-bold text-green-600">{agent.success_rate_pct}%</div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-500 text-xs">Streak</div>
                    <div className="font-bold text-orange-600">{agent.current_streak}</div>
                  </div>
                </div>
              </div>
            );
          })}

          {topPerformers.length === 0 && (
            <div className="py-12 text-center text-gray-500">
              No agent performance data yet
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
