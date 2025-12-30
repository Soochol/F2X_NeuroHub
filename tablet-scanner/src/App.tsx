/**
 * Main App Component
 *
 * Handles routing and authentication
 */
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from '@/store/appStore';
import { useUIStore } from '@/store/slices/uiSlice';
import { LoginPage } from '@/pages/LoginPage';
import { WorkPage } from '@/pages/WorkPage';
import { ToastProvider, ErrorBoundary } from '@/components/feedback';

// Import animations
import '@/styles/animations.css';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppStore();
  const token = localStorage.getItem('access_token');

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// App Component
function App() {
  const { theme } = useUIStore();

  // Apply theme to document root
  useEffect(() => {
    const html = window.document.documentElement;
    html.classList.remove('light', 'dark');
    html.classList.add(theme);
    html.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ErrorBoundary componentName="App">
      <ToastProvider>
        <BrowserRouter>
          <div
            className="w-full h-full min-h-screen"
          >
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <ErrorBoundary componentName="WorkPage">
                      <WorkPage />
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </BrowserRouter>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
