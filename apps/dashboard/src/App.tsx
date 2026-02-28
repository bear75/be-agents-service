import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { RunPage } from './pages/RunPage';
import { WorkPage } from './pages/WorkPage';
import { RosterPage } from './pages/RosterPage';
import { PlansPage } from './pages/PlansPage';
import { InsightsPage } from './pages/InsightsPage';
import { MarketingPage } from './pages/MarketingPage';
import { SchedulesPage } from './pages/SchedulesPage';
import { SettingsWithDocsPage } from './pages/SettingsWithDocsPage';
import './App.css';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="run" element={<RunPage />} />
          <Route path="work" element={<WorkPage />} />
          <Route path="roster" element={<RosterPage />} />
          <Route path="plans" element={<PlansPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="schedules" element={<SchedulesPage />} />
          <Route path="marketing" element={<MarketingPage />} />
          <Route path="settings" element={<SettingsWithDocsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
