/**
 * Main layout component with sidebar navigation.
 */

import { useState } from 'react';
import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StatusBar } from './StatusBar';
import { ToastContainer } from '../atoms';
import { useSystemInfo } from '../../hooks';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { data: systemInfo, isLoading } = useSystemInfo();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    const stored = localStorage.getItem('station-sidebar-collapsed');
    return stored ? JSON.parse(stored) : false;
  });

  // Default values while loading
  const stationId = systemInfo?.stationId ?? '...';
  const stationName = systemInfo?.stationName ?? (isLoading ? 'Loading...' : 'Station');

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div
      className="flex h-screen overflow-hidden transition-colors"
      style={{ backgroundColor: 'var(--color-bg-primary)' }}
    >
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={toggleSidebar}
        stationId={stationId}
        stationName={stationName}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main
          className="flex-1 p-4 overflow-auto"
          style={{ backgroundColor: 'var(--color-bg-primary)' }}
        >
          {children}
        </main>
        <StatusBar />
      </div>
      <ToastContainer />
    </div>
  );
}
