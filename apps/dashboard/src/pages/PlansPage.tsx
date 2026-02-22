/**
 * Plans - PRDs, agent status, logs
 */
import { useOutletContext } from 'react-router-dom';
import { PlansBoard } from '../components/PlansBoard';
import { AgentStatusCard } from '../components/AgentStatusCard';
import { LogViewer } from '../components/LogViewer';

export function PlansPage() {
  const { selectedRepo = '' } = useOutletContext<{ selectedRepo?: string }>() ?? {};

  return (
    <div className="space-y-6">
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
