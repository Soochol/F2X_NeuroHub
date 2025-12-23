/**
 * Main App Component
 *
 * Handles routing and authentication
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from '@/store/appStore';
import { LoginPage } from '@/pages/LoginPage';
import { WorkPage } from '@/pages/WorkPage';
import { ToastProvider } from '@/components/feedback';

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
  return (
    <ToastProvider>
      <BrowserRouter>
        <div
          className="w-full h-full max-w-[600px] mx-auto bg-neutral-100"
        >
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <WorkPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;
