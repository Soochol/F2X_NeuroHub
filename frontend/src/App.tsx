/**
 * F2X NeuroHub MES - Main Application
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App as AntApp, ConfigProvider, theme as antTheme } from 'antd';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
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
import ErrorDashboardPage from './pages/ErrorDashboardPage';

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
                  <Route path="/error-dashboard" element={<ErrorDashboardPage />} />
                </Route>
              </Route>

              {/* Catch all - redirect to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </AntApp>
    </ConfigProvider>
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
