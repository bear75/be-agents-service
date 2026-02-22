/**
 * Control Tower - launch sessions, manage agents
 */
import { ControlTower } from '../components/ControlTower';
import { StatsBar } from '../components/StatsBar';

export function ControlPage() {
  return (
    <div className="space-y-6">
      <StatsBar />
      <ControlTower />
    </div>
  );
}
