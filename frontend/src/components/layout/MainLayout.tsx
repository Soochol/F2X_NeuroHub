/**
 * Main Layout Component
 *
 * Top-level layout with sidebar, header, and content area
 */

import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const MainLayout = () => {
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <main style={{ flex: 1, overflow: 'auto', padding: '20px', backgroundColor: '#f5f5f5' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
