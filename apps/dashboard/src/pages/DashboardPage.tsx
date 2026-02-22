/**
 * Workspace Page (/) — inbox, priorities, check-ins, memory, follow-ups
 * Uses Layout nav for all other pages (Sessions, Teams, Control Tower, etc.)
 */
import { useOutletContext } from 'react-router-dom';
import { Bot } from 'lucide-react';
import { WorkspaceOverview } from '../components/WorkspaceOverview';
import { InboxView } from '../components/InboxView';
import { CheckInTimeline } from '../components/CheckInTimeline';
import { PriorityBoard } from '../components/PriorityBoard';
import { MemoryViewer } from '../components/MemoryViewer';

export function DashboardPage() {
  const { selectedRepo = '' } = useOutletContext<{ selectedRepo?: string }>() ?? {};

  if (!selectedRepo) {
    return (
      <div className="text-center py-12">
        <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Select a Repository</h2>
        <p className="text-gray-600">
          Choose a repository from the dropdown above to view its workspace.
        </p>
      </div>
    );
  }

  return (
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
  );
}
