/**
 * Unified Dashboard Page
 * Combines workspace (markdown), sessions/teams (SQLite), and agent control
 * into a single React dashboard.
 *
 * Tab structure:
 *   Workspace   — inbox, priorities, check-ins, memory, follow-ups (markdown)
 *   Sessions    — recent/active sessions, session details + tasks (SQLite)
 *   Teams       — team cards, agent lists, performance (SQLite)
 *   Control Tower — launch sessions, manage agents
 *   Kanban      — tasks across sessions
 *   Plans       — PRDs, setup status (file-based)
 *   Settings    — health, architecture, API reference
 */
import { useState } from 'react';
import {
  Bot,
  Layers,
  Clock,
  Users,
  Rocket,
  LayoutGrid,
  Map,
  Settings,
} from 'lucide-react';
import { RepoSelector } from '../components/RepoSelector';
import { StatsBar } from '../components/StatsBar';
import { WorkspaceOverview } from '../components/WorkspaceOverview';
import { InboxView } from '../components/InboxView';
import { CheckInTimeline } from '../components/CheckInTimeline';
import { PriorityBoard } from '../components/PriorityBoard';
import { MemoryViewer } from '../components/MemoryViewer';
import { SessionsBoard } from '../components/SessionsBoard';
import { TeamsOverview } from '../components/TeamsOverview';
import { ControlTower } from '../components/ControlTower';
import { KanbanBoard } from '../components/KanbanBoard';
import { PlansBoard } from '../components/PlansBoard';
import { SetupStatus } from '../components/SetupStatus';
import { SettingsPanel } from '../components/SettingsPanel';
import { AgentStatusCard } from '../components/AgentStatusCard';
import { LogViewer } from '../components/LogViewer';

type Tab =
  | 'workspace'
  | 'sessions'
  | 'teams'
  | 'control'
  | 'kanban'
  | 'plans'
  | 'settings';

const TABS: { id: Tab; label: string; icon: React.ReactNode; needsRepo: boolean }[] = [
  { id: 'workspace', label: 'Workspace', icon: <Layers className="w-4 h-4" />, needsRepo: true },
  { id: 'sessions', label: 'Sessions', icon: <Clock className="w-4 h-4" />, needsRepo: false },
  { id: 'teams', label: 'Teams', icon: <Users className="w-4 h-4" />, needsRepo: false },
  { id: 'control', label: 'Control Tower', icon: <Rocket className="w-4 h-4" />, needsRepo: false },
  { id: 'kanban', label: 'Kanban', icon: <LayoutGrid className="w-4 h-4" />, needsRepo: false },
  { id: 'plans', label: 'Plans', icon: <Map className="w-4 h-4" />, needsRepo: false },
  { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" />, needsRepo: false },
];

export function DashboardPage() {
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [activeTab, setActiveTab] = useState<Tab>('sessions');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Agent Service</h1>
                <p className="text-sm text-gray-600">
                  Unified workspace, teams & automation dashboard
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <RepoSelector value={selectedRepo} onChange={setSelectedRepo} />
            </div>
          </div>

          {/* Tab navigation */}
          <div className="flex mt-4 -mb-px overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats bar — visible on most tabs */}
        {['sessions', 'teams', 'control', 'kanban'].includes(activeTab) && (
          <div className="mb-6">
            <StatsBar />
          </div>
        )}

        {/* Workspace tab — requires repo selection */}
        {activeTab === 'workspace' && !selectedRepo && (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Select a Repository
            </h2>
            <p className="text-gray-600">
              Choose a repository from the dropdown above to view its workspace.
            </p>
          </div>
        )}

        {activeTab === 'workspace' && selectedRepo && (
          <div className="space-y-6">
            <WorkspaceOverview repoName={selectedRepo} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <InboxView repoName={selectedRepo} />
              <CheckInTimeline repoName={selectedRepo} />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PriorityBoard repoName={selectedRepo} />
              <MemoryViewer repoName={selectedRepo} />
            </div>
          </div>
        )}

        {/* Sessions tab */}
        {activeTab === 'sessions' && <SessionsBoard />}

        {/* Teams tab */}
        {activeTab === 'teams' && <TeamsOverview />}

        {/* Control Tower tab */}
        {activeTab === 'control' && <ControlTower />}

        {/* Kanban tab */}
        {activeTab === 'kanban' && <KanbanBoard />}

        {/* Plans tab */}
        {activeTab === 'plans' && (
          <div className="space-y-6">
            {selectedRepo && <SetupStatus repoName={selectedRepo} />}
            <PlansBoard />
            {selectedRepo && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AgentStatusCard repoName={selectedRepo} />
                <LogViewer repoName={selectedRepo} limit={50} />
              </div>
            )}
          </div>
        )}

        {/* Settings tab */}
        {activeTab === 'settings' && <SettingsPanel />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Agent Service v2.0.0 — Unified Dashboard — Powered by Claude Code
          </p>
        </div>
      ) : activeTab === 'workspace' ? (
        <div className="space-y-6">
          <WorkspaceOverview repoName={selectedRepo} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <InboxView repoName={selectedRepo} />
            <CheckInTimeline repoName={selectedRepo} />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PriorityBoard repoName={selectedRepo} />
            <MemoryViewer repoName={selectedRepo} />
          </div>
        </div>
      ) : activeTab === 'plans' ? (
          <div className="space-y-6">
            {/* Setup Readiness */}
            <SetupStatus repoName={selectedRepo} />

            {/* Plans & PRDs */}
            <PlansBoard />
          </div>
      ) : (
        <div className="space-y-6">
          <AgentStatusCard repoName={selectedRepo} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PriorityBoard repoName={selectedRepo} />
            <LogViewer repoName={selectedRepo} limit={50} />
          </div>
        </div>
      )}
    </div>
  );
}
