/**
 * F2X NeuroHub MES - Main Application
 */

import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App as AntApp, ConfigProvider, theme as antTheme, Spin } from 'antd';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import { ErrorBoundary } from './components/common';

// Lazy load pages
const LoginPage = lazy(() => import('./pages/LoginPage').then(module => ({ default: module.LoginPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })));
const LotsPage = lazy(() => import('./pages/LotsPage').then(module => ({ default: module.LotsPage })));

// WIP Pages
const WipTrackingPage = lazy(() => import('./pages/WipTrackingPage').then(module => ({ default: module.WipTrackingPage })));
const WipByLotPage = lazy(() => import('./pages/WipByLotPage').then(module => ({ default: module.WipByLotPage })));
const WipGenerationPage = lazy(() => import('./pages/WipGenerationPage').then(module => ({ default: module.WipGenerationPage })));

// Serial Pages
const SerialsPage = lazy(() => import('./pages/SerialsPage').then(module => ({ default: module.SerialsPage })));
const SerialGenerationPage = lazy(() => import('./pages/SerialGenerationPage').then(module => ({ default: module.SerialGenerationPage })));
const SerialByLotPage = lazy(() => import('./pages/SerialByLotPage').then(module => ({ default: module.SerialByLotPage })));

// Admin Pages - Direct imports from AdminPage (removes unnecessary wrapper files)
const AdminPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.AdminPage })));
const AdminEquipmentPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.EquipmentManagement })));
const AdminUsersPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.UserManagement })));
const AdminProcessesPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.ProcessManagement })));
const AdminProductsPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.ProductModelManagement })));
const AdminProductionLinesPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.ProductionLineManagement })));
const SerialInspectorPage = lazy(() => import('./pages/admin/SerialInspectorPage').then(module => ({ default: module.SerialInspectorPage })));
const LotMonitorPage = lazy(() => import('./pages/admin/LotMonitorPage').then(module => ({ default: module.LotMonitorPage })));
const AdminSequencesPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.SequenceManagement })));

// Quality Pages
const ProcessDefectRatePage = lazy(() => import('./pages/ProcessDefectRatePage').then(module => ({ default: module.ProcessDefectRatePage })));
const MeasurementAnalysisPage = lazy(() => import('./pages/MeasurementAnalysisPage').then(module => ({ default: module.MeasurementAnalysisPage })));

// Station Monitor Pages
const StationMonitorPage = lazy(() => import('./pages/stations/StationMonitorPage').then(module => ({ default: module.StationMonitorPage })));
const StationDetailPage = lazy(() => import('./pages/stations/StationDetailPage').then(module => ({ default: module.StationDetailPage })));

// Other Pages
const AlertsPage = lazy(() => import('./pages/AlertsPage').then(module => ({ default: module.AlertsPage })));

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

// Inner app component that has access to theme context
function AppContent() {
  const { isDark } = useTheme();

  return (
    <ErrorBoundary>
      <ConfigProvider
        theme={{
          algorithm: isDark ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
          token: {
          // Brand colors
          colorPrimary: '#3ecf8e',
          colorSuccess: isDark ? '#3ecf8e' : '#22c55e',
          colorError: isDark ? '#f56565' : '#ef4444',
          colorWarning: isDark ? '#f5a623' : '#f59e0b',
          colorInfo: '#3b82f6',

          // Background colors (matching theme.css)
          colorBgBase: isDark ? '#1c1c1c' : '#ffffff',
          colorBgContainer: isDark ? '#232323' : '#ffffff',
          colorBgElevated: isDark ? '#323232' : '#ffffff',
          colorBgLayout: isDark ? '#1c1c1c' : '#f8f9fa',

          // Text colors
          colorText: isDark ? '#ededed' : '#1f2937',
          colorTextSecondary: isDark ? '#a1a1a1' : '#6b7280',
          colorTextTertiary: isDark ? '#6b6b6b' : '#9ca3af',
          colorTextQuaternary: isDark ? '#4a4a4a' : '#d1d5db',

          // Border colors
          colorBorder: isDark ? '#2e2e2e' : '#e3e5e8',
          colorBorderSecondary: isDark ? '#252525' : '#f1f3f5',

          // Border radius
          borderRadius: 6,
          borderRadiusLG: 12,
          borderRadiusSM: 4,
        },
      }}
    >
      <AntApp>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={
                <Suspense fallback={<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spin size="large" /></div>}>
                  <LoginPage />
                </Suspense>
              } />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route element={<MainLayout />}>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/lots" element={<LotsPage />} />

                  {/* WIP Routes */}
                  <Route path="/wip/tracking" element={<WipTrackingPage />} />
                  <Route path="/wip/list" element={<WipByLotPage />} />
                  <Route path="/wip/generate" element={<WipGenerationPage />} />

                  {/* Serial Routes */}
                  <Route path="/serials/tracking" element={<SerialsPage />} />
                  <Route path="/serials/generate" element={<SerialGenerationPage />} />
                  <Route path="/serials/list" element={<SerialByLotPage />} />

                  {/* Admin Routes */}
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="/admin/users" element={<AdminUsersPage />} />
                  <Route path="/admin/processes" element={<AdminProcessesPage />} />
                  <Route path="/admin/products" element={<AdminProductsPage />} />
                  <Route path="/admin/production-lines" element={<AdminProductionLinesPage />} />
                  <Route path="/admin/equipment" element={<AdminEquipmentPage />} />
                  <Route path="/admin/sequences" element={<AdminSequencesPage />} />
                  <Route path="/admin/serial-inspector" element={<SerialInspectorPage />} />
                  <Route path="/admin/lot-monitor" element={<LotMonitorPage />} />

                  {/* Quality Routes */}
                  <Route path="/quality/defect-rate" element={<ProcessDefectRatePage />} />
                  <Route path="/quality/measurements" element={<MeasurementAnalysisPage />} />

                  {/* Station Monitor Routes */}
                  <Route path="/stations" element={<StationMonitorPage />} />
                  <Route path="/stations/:stationId" element={<StationDetailPage />} />

                  {/* Alerts */}
                  <Route path="/alerts" element={<AlertsPage />} />
                </Route>
              </Route>

              {/* Catch all - redirect to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </AntApp>
    </ConfigProvider>
  </ErrorBoundary>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
