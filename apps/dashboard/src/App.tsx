import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { RunPage } from './pages/RunPage';
import { WorkPage } from './pages/WorkPage';
import { RosterPage } from './pages/RosterPage';
import { PlansPage } from './pages/PlansPage';
import { InsightsPage } from './pages/InsightsPage';
import { MarketingPage } from './pages/MarketingPage';
import { SchedulesPage } from './pages/SchedulesPage';
import { RunDetailPage } from './pages/RunDetailPage';
import { SettingsWithDocsPage } from './pages/SettingsWithDocsPage';
import './App.css';

function parseDisabledModules(value: unknown): Set<string> {
  if (!Array.isArray(value)) return new Set<string>();
  return new Set(
    value
      .map((item) => (typeof item === 'string' ? item.trim().toLowerCase() : ''))
      .filter(Boolean),
  );
}

function App() {
  const [disabledModules, setDisabledModules] = useState<Set<string>>(new Set());
  const [healthLoaded, setHealthLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch('/health')
      .then((response) => response.json())
      .then((data) => {
        if (!cancelled) {
          setDisabledModules(parseDisabledModules(data?.disabledModules));
        }
      })
      .catch(() => {
        // Keep defaults when health endpoint is unavailable.
      })
      .finally(() => {
        if (!cancelled) setHealthLoaded(true);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (!healthLoaded) {
    return null;
  }

  const plansEnabled = !disabledModules.has('plans');
  const schedulesEnabled = !disabledModules.has('schedules');
  const settingsEnabled = !disabledModules.has('settings');

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="run" element={<RunPage />} />
          <Route path="work" element={<WorkPage />} />
          <Route path="roster" element={<RosterPage />} />
          <Route path="plans" element={plansEnabled ? <PlansPage /> : <Navigate to="/" replace />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="schedules" element={schedulesEnabled ? <SchedulesPage /> : <Navigate to="/" replace />} />
          <Route path="schedules/run/:id" element={schedulesEnabled ? <RunDetailPage /> : <Navigate to="/" replace />} />
          <Route path="marketing" element={<MarketingPage />} />
          <Route path="settings" element={settingsEnabled ? <SettingsWithDocsPage /> : <Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
