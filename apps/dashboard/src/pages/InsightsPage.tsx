/**
 * Insights - Analytics + Leaderboard (no overlap)
 * Purpose: Observability & gamification
 */
import { useState } from 'react';
import { Brain, Trophy } from 'lucide-react';
import { PagePurpose } from '../components/PagePurpose';
import { RLDashboardPage } from './RLDashboardPage';
import { ManagementPage } from './ManagementPage';

const TABS = [
  { id: 'analytics', label: 'Analytics', icon: Brain, desc: 'Experiments, LLM usage' },
  { id: 'leaderboard', label: 'Leaderboard', icon: Trophy, desc: 'Agent XP, tasks, success' },
] as const;

export function InsightsPage() {
  const [activeTab, setActiveTab] = useState<'analytics' | 'leaderboard'>('analytics');

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Observability & gamification."
        how="Analytics: experiments, patterns, LLM stats. Leaderboard: agent XP, tasks, success rate."
        tip="Compound AI pattern: Executive value + Product learning."
      />
      <div className="border-b border-gray-200">
        <nav className="flex gap-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors -mb-px ${
                  isActive
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
      {activeTab === 'analytics' && <RLDashboardPage />}
      {activeTab === 'leaderboard' && (
        <div className="pt-2">
          <ManagementPage />
        </div>
      )}
    </div>
  );
}
