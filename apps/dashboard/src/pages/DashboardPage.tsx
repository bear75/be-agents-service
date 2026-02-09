/**
 * Main Dashboard Page
 * Displays agent status, workspace overview, and logs for selected repository
 */
import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Bot, Layers, Settings, Map } from 'lucide-react';
import { AgentStatusCard } from '../components/AgentStatusCard';
import { PriorityBoard } from '../components/PriorityBoard';
import { LogViewer } from '../components/LogViewer';
import { WorkspaceOverview } from '../components/WorkspaceOverview';
import { InboxView } from '../components/InboxView';
import { CheckInTimeline } from '../components/CheckInTimeline';
import { MemoryViewer } from '../components/MemoryViewer';
import { PlansBoard } from '../components/PlansBoard';
import { SetupStatus } from '../components/SetupStatus';

type Tab = 'workspace' | 'plans' | 'agents';

export function DashboardPage() {
  const { selectedRepo } = useOutletContext<{ selectedRepo: string }>();
  const [activeTab, setActiveTab] = useState<Tab>('workspace');

  return (
    <div>
      {/* Tab navigation */}
      {selectedRepo && (
        <div className="flex mb-6 -mb-px">
          {([
            { id: 'workspace' as Tab, label: 'Workspace', icon: <Layers className="w-4 h-4" /> },
            { id: 'plans' as Tab, label: 'Plans & Roadmap', icon: <Map className="w-4 h-4" /> },
            { id: 'agents' as Tab, label: 'Agents & Logs', icon: <Settings className="w-4 h-4" /> },
          ]).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
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
      )}

      {!selectedRepo ? (
        <div className="text-center py-12">
          <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Repository Selected</h2>
          <p className="text-gray-600">
            Select a repository from the dropdown above to view its workspace and agent status
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
