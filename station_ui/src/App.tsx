/**
 * Main application component with route configuration.
 */

import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { DashboardPage } from './pages/DashboardPage';
import { BatchesPage } from './pages/BatchesPage';
import { BatchDetailPage } from './pages/BatchDetailPage';
import { SequencesPage } from './pages/SequencesPage';
import { ManualControlPage } from './pages/ManualControlPage';
import { ResultsPage } from './pages/ResultsPage';
import { LogsPage } from './pages/LogsPage';
import { SettingsPage } from './pages/SettingsPage';
import { MonitorPage } from './pages/MonitorPage';
import { LoginPage } from './pages/LoginPage';
import { ROUTES } from './constants';
import { usePollingFallback, useOperatorSession } from './hooks';
import { useUIStore } from './stores/uiStore';
import { LoadingSpinner } from './components/atoms/LoadingSpinner';

/**
 * Inner app component that uses hooks requiring providers.
 */
function AppContent() {
  // Activate polling fallback when WebSocket is disconnected
  usePollingFallback();

  // Check login status
  const { data: operatorSession, isLoading: sessionLoading, refetch: refetchSession } = useOperatorSession();

  // Initialize theme on mount
  const theme = useUIStore((state) => state.theme);
  useEffect(() => {
    document.documentElement.classList.remove('dark', 'light');
    document.documentElement.classList.add(theme);
  }, [theme]);

  // Show loading while checking session
  if (sessionLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--color-bg-primary)' }}
      >
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Show login page if not logged in
  if (!operatorSession?.loggedIn) {
    return <LoginPage onLoginSuccess={() => refetchSession()} />;
  }

  return (
    <ErrorBoundary>
      <Layout>
        <Routes>
          <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
          <Route path={ROUTES.BATCHES} element={<BatchesPage />} />
          <Route path={ROUTES.BATCH_DETAIL} element={<BatchDetailPage />} />
          <Route path={ROUTES.SEQUENCES} element={<SequencesPage />} />
          <Route path={ROUTES.SEQUENCE_DETAIL} element={<SequencesPage />} />
          <Route path={ROUTES.MANUAL} element={<ManualControlPage />} />
          <Route path={ROUTES.RESULTS} element={<ResultsPage />} />
          <Route path={ROUTES.LOGS} element={<LogsPage />} />
          <Route path={ROUTES.MONITOR} element={<MonitorPage />} />
          <Route path={ROUTES.SETTINGS} element={<SettingsPage />} />
        </Routes>
      </Layout>
    </ErrorBoundary>
  );
}

function App() {
  return <AppContent />;
}

export default App;
