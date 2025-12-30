/**
 * Main application component with route configuration.
 */

import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { BatchesPage } from './pages/BatchesPage';
import { BatchDetailPage } from './pages/BatchDetailPage';
import { SequencesPage } from './pages/SequencesPage';
import { ManualControlPage } from './pages/ManualControlPage';
import { LogsPage } from './pages/LogsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ROUTES } from './constants';
import { usePollingFallback } from './hooks';
import { useUIStore } from './stores/uiStore';

/**
 * Inner app component that uses hooks requiring providers.
 */
function AppContent() {
  // Activate polling fallback when WebSocket is disconnected
  usePollingFallback();

  // Initialize theme on mount
  const theme = useUIStore((state) => state.theme);
  useEffect(() => {
    document.documentElement.classList.remove('dark', 'light');
    document.documentElement.classList.add(theme);
  }, [theme]);

  return (
    <Layout>
      <Routes>
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.BATCHES} element={<BatchesPage />} />
        <Route path={ROUTES.BATCH_DETAIL} element={<BatchDetailPage />} />
        <Route path={ROUTES.SEQUENCES} element={<SequencesPage />} />
        <Route path={ROUTES.SEQUENCE_DETAIL} element={<SequencesPage />} />
        <Route path={ROUTES.MANUAL} element={<ManualControlPage />} />
        <Route path={ROUTES.LOGS} element={<LogsPage />} />
        <Route path={ROUTES.SETTINGS} element={<SettingsPage />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return <AppContent />;
}

export default App;
