/**
 * Roster - Agents + Teams in one surface (no overlap)
 * Purpose: Configure who does what
 */
import { useState } from 'react';
import { Users, Target } from 'lucide-react';
import { PagePurpose } from '../components/PagePurpose';
import { AgentsPage } from './AgentsPage';
import { TeamsPage } from './TeamsPage';

const TABS = [
  { id: 'agents', label: 'Agents', icon: Users, desc: 'Hire, fire, manage' },
  { id: 'teams', label: 'Teams', icon: Target, desc: 'Team config & members' },
] as const;

export function RosterPage() {
  const [activeTab, setActiveTab] = useState<'agents' | 'teams'>('agents');

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Configure who does what."
        how="Agents: hire, fire, assign to teams. Teams: view team config, members, and stats."
        tip="Same roster, two views — no duplication."
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
      {activeTab === 'agents' && <AgentsPage />}
      {activeTab === 'teams' && (
        <div className="pt-2">
          <TeamsPage />
        </div>
      )}
    </div>
  );
}
