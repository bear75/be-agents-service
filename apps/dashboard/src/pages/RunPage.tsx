/**
 * Run - start compound, control tower sessions
 * Purpose: Launch automation (no overlap)
 */
import { useState } from 'react';
import { Cpu, Rocket, GitCommit } from 'lucide-react';
import { StatsBar } from '../components/StatsBar';
import { PagePurpose } from '../components/PagePurpose';
import { EngineeringPage } from './EngineeringPage';
import { ControlTower } from '../components/ControlTower';

const TABS = [
  { id: 'compound', label: 'Compound', icon: Cpu, desc: 'Start auto-compound' },
  { id: 'control', label: 'Control Tower', icon: Rocket, desc: 'Launch sessions' },
  { id: 'commit', label: 'Commit & push all', icon: GitCommit, desc: 'Git add, commit, push' },
] as const;

export function RunPage() {
  const [activeTab, setActiveTab] = useState<'compound' | 'control' | 'commit'>('compound');

  return (
    <div className="space-y-6">
      <StatsBar />
      <PagePurpose
        purpose="Launch automation."
        how="Compound: start auto-compound (priority → PRD → PR). Control Tower: launch sessions by team and repo."
        tip="Nightly at 23:00 or start manually from here or terminal."
      />
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Run</h2>
        <p className="text-sm text-gray-500 mt-1">
          Start compound workflows or launch sessions via Control Tower
        </p>
      </div>
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
      {activeTab === 'compound' && <EngineeringPage />}
      {activeTab === 'control' && (
        <div className="pt-2">
          <ControlTower />
        </div>
      )}
      {activeTab === 'commit' && (
        <div className="pt-2 space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-medium text-gray-900 mb-2">Commit & push all</h3>
            <p className="text-sm text-gray-500 mb-4">
              Run from each repo you changed (e.g. be-agents-service, beta-appcaire). Stage all, commit, push.
            </p>
            <pre className="space-y-1 font-mono text-sm bg-gray-50 p-4 rounded-lg border border-gray-200 overflow-x-auto">
              {`git add -A && git status
git commit -m "your message"
git push`}
            </pre>
            <p className="text-xs text-gray-500 mt-3">
              One-liner: <code className="bg-gray-100 px-1 rounded">git add -A && git commit -m "chore: update" && git push</code>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
