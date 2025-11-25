/**
 * LOT History Tabs Component
 * Displays LOT history in different views with tab switching
 */

import { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

interface LotSummary {
  lot_number: string;
  product_model_name?: string;
  status: string;
  progress?: number;
  progress_percentage?: number;
  started_count?: number;
  created_count?: number;
  in_progress_count?: number;
  converted_count?: number;
  target_quantity?: number;
  completed_count: number;
  defective_count?: number;
  failed_count?: number;
  passed_count?: number;
  created_at?: string;
}

// Calculate progress safely
const getProgress = (lot: LotSummary): number => {
  // Check progress_percentage first (from API)
  if (lot.progress_percentage !== undefined && !isNaN(lot.progress_percentage)) return lot.progress_percentage;
  if (lot.progress !== undefined && !isNaN(lot.progress)) return lot.progress;

  const started = lot.started_count ?? lot.target_quantity ?? 0;
  const completed = lot.completed_count ?? 0;
  if (started === 0) return 0;
  const result = (completed / started) * 100;
  return isNaN(result) ? 0 : result;
};

// Get started count (supports both field names)
const getStartedCount = (lot: LotSummary): number => {
  return lot.started_count ?? lot.target_quantity ?? 0;
};

// Get defective count (supports both field names)
const getDefectiveCount = (lot: LotSummary): number => {
  return lot.defective_count ?? lot.failed_count ?? 0;
};

interface LotHistoryTabsProps {
  lots: LotSummary[];
}

type TabType = 'lots' | 'defects';

export const LotHistoryTabs = ({ lots }: LotHistoryTabsProps) => {
  const [activeTab, setActiveTab] = useState<TabType>('lots');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'lots', label: 'LOT Status' },
    { id: 'defects', label: 'Defect History' },
  ];



  // Filter defects only
  const defectHistory = lots
    .filter((lot) => getDefectiveCount(lot) > 0)
    .map((lot) => ({
      lotNumber: lot.lot_number,
      process: '-',
      defectType: 'Defect',
      count: getDefectiveCount(lot),
    }));



  const getStatusBadge = (status: string) => {
    const baseStyle = {
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: '500',
    };

    switch (status) {
      case 'COMPLETED':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-success-light)', color: 'var(--color-success)' }}>
            Completed
          </span>
        );
      case 'IN_PROGRESS':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-info-light)', color: 'var(--color-info)' }}>
            In Progress
          </span>
        );
      case 'CREATED':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-warning-light)', color: 'var(--color-warning)' }}>
            Created
          </span>
        );
      case 'CLOSED':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)' }}>
            Closed
          </span>
        );
      default:
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}>
            {status}
          </span>
        );
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {


      case 'lots':
        return (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Time</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>LOT Number</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Product</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Target</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Started</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>In Progress</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Converted</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Completion Rate</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {lots.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    No LOT data available
                  </td>
                </tr>
              ) : (
                lots.map((lot, index) => (
                  <tr
                    key={lot.lot_number}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      backgroundColor: index % 2 === 0 ? 'transparent' : 'var(--color-bg-tertiary)',
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                      {lot.created_at ? new Date(lot.created_at).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' }) + ' ' + new Date(lot.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false }) : '-'}
                    </td>
                    <td style={{ padding: '12px', fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{lot.lot_number}</td>
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-primary)' }}>{lot.product_model_name}</td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px', fontWeight: '600', color: 'var(--color-text-primary)' }}>
                      {lot.target_quantity ?? 0}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px', color: 'var(--color-info)' }}>
                      {lot.created_count ?? lot.started_count ?? 0}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px', color: 'var(--color-warning)' }}>
                      {lot.in_progress_count ?? 0}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px', color: 'var(--color-success)' }}>
                      {lot.converted_count ?? 0}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-brand)' }}>
                          {lot.converted_count ?? 0} / {lot.target_quantity ?? 0}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                          ({lot.target_quantity ? (((lot.converted_count ?? 0) / lot.target_quantity) * 100).toFixed(1) : 0}%)
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{getStatusBadge(lot.status)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        );

      case 'defects':
        return (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>LOT Number</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Process</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Defect Type</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)', fontSize: '13px' }}>Quantity</th>
              </tr>
            </thead>
            <tbody>
              {defectHistory.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <CheckCircle size={16} color="var(--color-success)" />
                      No defect history
                    </div>
                  </td>
                </tr>
              ) : (
                defectHistory.map((item, index) => (
                  <tr
                    key={index}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      backgroundColor: index % 2 === 0 ? 'transparent' : 'var(--color-bg-tertiary)',
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{item.lotNumber}</td>
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-primary)' }}>{item.process}</td>
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-primary)' }}>{item.defectType}</td>
                    <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontWeight: '500', color: 'var(--color-error)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' }}>
                        <XCircle size={14} />
                        {item.count}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        );
    }
  };

  return (
    <div>
      {/* Tab Navigation */}
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid var(--color-border)',
          marginBottom: '16px',
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 20px',
              fontSize: '14px',
              fontWeight: activeTab === tab.id ? '600' : '400',
              color: activeTab === tab.id ? 'var(--color-brand-500)' : 'var(--color-text-secondary)',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid var(--color-brand-500)' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ overflowX: 'auto' }}>
        {renderTabContent()}
      </div>
    </div>
  );
};
