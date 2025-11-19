/**
 * F2X NeuroHub MES - Main Application
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { LotsPage } from './pages/LotsPage';
import { SerialsPage } from './pages/SerialsPage';
import { QualityPage } from './pages/QualityPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AlertsPage } from './pages/AlertsPage';
import { AdminPage } from './pages/AdminPage';

// Create QueryClient for react-query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/lots" element={<LotsPage />} />
                <Route path="/serials" element={<SerialsPage />} />
                <Route path="/quality" element={<QualityPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/admin" element={<AdminPage />} />
              </Route>
            </Route>

            {/* Catch all - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
