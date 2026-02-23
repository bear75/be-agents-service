/**
 * Plans - PRDs, agent status, logs
 * Purpose: What to build (no overlap)
 */
import { useOutletContext } from 'react-router-dom';
import { PagePurpose } from '../components/PagePurpose';
import { PlansBoard } from '../components/PlansBoard';
import { AgentStatusCard } from '../components/AgentStatusCard';
import { LogViewer } from '../components/LogViewer';

export function PlansPage() {
  const { selectedRepo = '' } = useOutletContext<{ selectedRepo?: string }>() ?? {};

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="What to build."
        how="PRDs and roadmaps. When a repo is selected: agent status and logs."
        tip="Planning + repo context in one place."
      />
      <PlansBoard />
      {selectedRepo && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AgentStatusCard repoName={selectedRepo} />
          <LogViewer repoName={selectedRepo} limit={50} />
        </div>
      )}
    </div>
  );
}
