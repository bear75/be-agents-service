/**
 * Overview Page (/) — Workspace for default repo (darwin): inbox, priorities, check-ins, memory.
 */
import { useOutletContext } from 'react-router-dom';
import { PagePurpose } from '../components/PagePurpose';
import { WorkspaceOverview } from '../components/WorkspaceOverview';
import { InboxView } from '../components/InboxView';
import { CheckInTimeline } from '../components/CheckInTimeline';
import { PriorityBoard } from '../components/PriorityBoard';
import { MemoryViewer } from '../components/MemoryViewer';

export function DashboardPage() {
  const { selectedRepo = 'darwin' } = useOutletContext<{ selectedRepo?: string }>() ?? {};

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Entry point & context."
        how="Workspace: inbox, priorities, check-ins, memory (darwin)."
        tip="Run, Work, Roster, Plans, Settings in the nav."
      />
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
