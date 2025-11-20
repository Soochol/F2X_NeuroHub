/**
 * LOT History Tabs Component
 * Displays LOT history in different views with tab switching
 */

import { useState } from 'react';
import { CheckCircle, AlertTriangle, Clock, XCircle } from 'lucide-react';

interface LotSummary {
  lot_number: string;
  product_model_name?: string;
  status: string;
  progress?: number;
  progress_percentage?: number;
  started_count?: number;
  target_quantity?: number;
  completed_count: number;
  defective_count?: number;
  failed_count?: number;
  passed_count?: number;
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

type TabType = 'recent' | 'lots' | 'defects';

export const LotHistoryTabs = ({ lots }: LotHistoryTabsProps) => {
  const [activeTab, setActiveTab] = useState<TabType>('recent');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'recent', label: '최근 이력' },
    { id: 'lots', label: 'LOT별 현황' },
    { id: 'defects', label: '불량 이력' },
  ];

  // Generate recent history from lots data
  const recentHistory = lots.flatMap((lot) => {
    const events = [];
    const startedCount = getStartedCount(lot);
    const defectiveCount = getDefectiveCount(lot);

    if (startedCount > 0) {
      events.push({
        time: 'Recent',
        lotNumber: lot.lot_number,
        content: `생산 진행중 (${lot.completed_count}/${startedCount})`,
        status: lot.status === 'COMPLETED' ? 'completed' : 'progress',
        result: `${getProgress(lot).toFixed(0)}%`,
      });
    }
    if (defectiveCount > 0) {
      events.push({
        time: 'Recent',
        lotNumber: lot.lot_number,
        content: `불량 발생`,
        status: 'defect',
        result: `${defectiveCount}건`,
      });
    }
    return events;
  }).slice(0, 10);

  // Filter defects only
  const defectHistory = lots
    .filter((lot) => getDefectiveCount(lot) > 0)
    .map((lot) => ({
      lotNumber: lot.lot_number,
      process: '-',
      defectType: '불량',
      count: getDefectiveCount(lot),
    }));

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={14} color="var(--color-success)" />;
      case 'progress':
        return <Clock size={14} color="var(--color-info)" />;
      case 'defect':
        return <AlertTriangle size={14} color="var(--color-error)" />;
      default:
        return <Clock size={14} color="var(--color-text-secondary)" />;
    }
  };

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
            완료
          </span>
        );
      case 'IN_PROGRESS':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-info-light)', color: 'var(--color-info)' }}>
            진행중
          </span>
        );
      case 'CREATED':
        return (
          <span style={{ ...baseStyle, backgroundColor: 'var(--color-warning-light)', color: 'var(--color-warning)' }}>
            생성됨
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
      case 'recent':
        return (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>시간</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>LOT 번호</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>내용</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>상태</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)', fontSize: '13px' }}>결과</th>
              </tr>
            </thead>
            <tbody>
              {recentHistory.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    최근 이력이 없습니다
                  </td>
                </tr>
              ) : (
                recentHistory.map((item, index) => (
                  <tr
                    key={index}
                    style={{
                      borderBottom: '1px solid var(--color-border)',
                      backgroundColor: index % 2 === 0 ? 'transparent' : 'var(--color-bg-tertiary)',
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>{item.time}</td>
                    <td style={{ padding: '12px', fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{item.lotNumber}</td>
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-primary)' }}>{item.content}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{getStatusIcon(item.status)}</td>
                    <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{item.result}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        );

      case 'lots':
        return (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>LOT 번호</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>제품</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>진행률</th>
                <th style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '13px' }}>상태</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)', fontSize: '13px' }}>완료/시작</th>
              </tr>
            </thead>
            <tbody>
              {lots.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    LOT 데이터가 없습니다
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
                    <td style={{ padding: '12px', fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{lot.lot_number}</td>
                    <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-primary)' }}>{lot.product_model_name}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
                        <div
                          style={{
                            width: '60px',
                            height: '6px',
                            backgroundColor: 'var(--color-border)',
                            borderRadius: '3px',
                            overflow: 'hidden',
                          }}
                        >
                          <div
                            style={{
                              width: `${getProgress(lot)}%`,
                              height: '100%',
                              backgroundColor: getProgress(lot) >= 100 ? 'var(--color-success)' : 'var(--color-brand-500)',
                              borderRadius: '3px',
                            }}
                          />
                        </div>
                        <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{getProgress(lot).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{getStatusBadge(lot.status)}</td>
                    <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', color: 'var(--color-text-primary)' }}>
                      {lot.completed_count}/{getStartedCount(lot)}
                    </td>
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
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>LOT 번호</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>공정</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)', fontSize: '13px' }}>불량 유형</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)', fontSize: '13px' }}>수량</th>
              </tr>
            </thead>
            <tbody>
              {defectHistory.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <CheckCircle size={16} color="var(--color-success)" />
                      불량 이력이 없습니다
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
