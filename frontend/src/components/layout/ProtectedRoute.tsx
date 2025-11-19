/**
 * Protected Route Component
 *
 * Restricts access to authenticated users only
 */

import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // TODO: Remove this bypass after testing
  const BYPASS_AUTH = false;

  if (isLoading && !BYPASS_AUTH) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (isAuthenticated || BYPASS_AUTH) ? <Outlet /> : <Navigate to="/login" replace />;
};
