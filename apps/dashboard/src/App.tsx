import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { SessionsPage } from './pages/SessionsPage';
import { KanbanPage } from './pages/KanbanPage';
import { EngineeringPage } from './pages/EngineeringPage';
import { CommandsPage } from './pages/CommandsPage';
import { SettingsPage } from './pages/SettingsPage';
import { AgentsPage } from './pages/AgentsPage';
import { TeamsPage } from './pages/TeamsPage';
import { MarketingPage } from './pages/MarketingPage';
import { RLDashboardPage } from './pages/RLDashboardPage';
import { ManagementPage } from './pages/ManagementPage';
import { ControlPage } from './pages/ControlPage';
import { PlansPage } from './pages/PlansPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="management" element={<ManagementPage />} />
          <Route path="sessions" element={<SessionsPage />} />
          <Route path="control" element={<ControlPage />} />
          <Route path="plans" element={<PlansPage />} />
          <Route path="kanban" element={<KanbanPage />} />
          <Route path="engineering" element={<EngineeringPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="teams" element={<TeamsPage />} />
          <Route path="marketing" element={<MarketingPage />} />
          <Route path="rl" element={<RLDashboardPage />} />
          <Route path="commands" element={<CommandsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
