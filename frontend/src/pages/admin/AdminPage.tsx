/**
 * Admin Page - System Administration
 *
 * Main administration page with tab navigation to:
 * - User Management
 * - Process Management
 * - Product Models
 * - Production Sites
 * - Equipment
 *
 * Each management section is implemented as a separate component
 * for better maintainability and code organization.
 */

import { useState } from 'react';

import { EquipmentManagement } from './EquipmentManagement';
import { ProcessManagement } from './ProcessManagement';
import { ProductionLineManagement } from './ProductionLineManagement';
import { ProductModelManagement } from './ProductModelManagement';
import { SequenceManagement } from './SequenceManagement';
import { getTabStyle, type TabType } from './shared';
import { UserManagement } from './UserManagement';

export const AdminPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('users');

  return (
    <div>
      <h1
        style={{
          fontSize: '24px',
          fontWeight: 'bold',
          marginBottom: '20px',
          color: 'var(--color-text-primary)',
        }}
      >
        Administration
      </h1>
      <div
        style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '20px',
          borderBottom: '2px solid var(--color-border)',
        }}
      >
        <button onClick={() => setActiveTab('users')} style={getTabStyle(activeTab === 'users')}>
          User Management
        </button>
        <button
          onClick={() => setActiveTab('processes')}
          style={getTabStyle(activeTab === 'processes')}
        >
          Process Management
        </button>
        <button
          onClick={() => setActiveTab('products')}
          style={getTabStyle(activeTab === 'products')}
        >
          Product Models
        </button>
        <button
          onClick={() => setActiveTab('productionLines')}
          style={getTabStyle(activeTab === 'productionLines')}
        >
          Production Sites
        </button>
        <button
          onClick={() => setActiveTab('equipment')}
          style={getTabStyle(activeTab === 'equipment')}
        >
          Equipment
        </button>
        <button
          onClick={() => setActiveTab('sequences')}
          style={getTabStyle(activeTab === 'sequences')}
        >
          Test Sequences
        </button>
      </div>
      {activeTab === 'users' && <UserManagement />}
      {activeTab === 'processes' && <ProcessManagement />}
      {activeTab === 'products' && <ProductModelManagement />}
      {activeTab === 'productionLines' && <ProductionLineManagement />}
      {activeTab === 'equipment' && <EquipmentManagement />}
      {activeTab === 'sequences' && <SequenceManagement />}
    </div>
  );
};
