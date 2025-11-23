import React, { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { printerApi } from '../api/endpoints/printer';
import useAsyncData from '../hooks/useAsyncData';
import { PrinterStatus, PrintLog, PrintStatistics } from '../types/api';

const PrinterMonitoringPage: React.FC = () => {
    // State for filters
    const [labelType, setLabelType] = useState<string>('');
    const [status, setStatus] = useState<string>('');
    const [page, setPage] = useState(1);
    const limit = 20;

    // Fetch Printer Status
    const {
        data: printerStatus,
        isLoading: statusLoading,
        refetch: refetchStatus
    } = useAsyncData<PrinterStatus>({
        fetchFn: printerApi.getStatus,
        autoFetch: true,
        errorMessage: 'Failed to check printer status'
    });

    // Fetch Statistics
    const {
        data: statistics,
        isLoading: statsLoading,
        refetch: refetchStats
    } = useAsyncData<PrintStatistics>({
        fetchFn: () => printerApi.getStatistics(),
        autoFetch: true,
        errorMessage: 'Failed to load statistics'
    });

    // Fetch Logs
    const {
        data: logsData,
        isLoading: logsLoading,
        refetch: refetchLogs
    } = useAsyncData<{ total: number; logs: PrintLog[] }>({
        fetchFn: () => printerApi.getLogs({
            skip: (page - 1) * limit,
            limit,
            label_type: labelType || undefined,
            status: status || undefined
        }),
        dependencies: [page, labelType, status],
        errorMessage: 'Failed to load print logs'
    });

    const handleRefresh = () => {
        refetchStatus();
        refetchStats();
        refetchLogs();
    };

    const handleTestPrint = async (type: string) => {
        if (!confirm(`${type} 테스트 출력을 하시겠습니까?`)) return;
        try {
            const result = await printerApi.testPrint(type);
            if (result.success) {
                alert('테스트 출력 성공!');
                handleRefresh();
            } else {
                alert(`테스트 출력 실패: ${result.message}`);
            }
        } catch (err) {
            alert('테스트 출력 중 오류가 발생했습니다.');
        }
    };

    return (
        <MainLayout title="Printer Monitoring">
            <div style={styles.container}>
                {/* Header Actions */}
                <div style={styles.header}>
                    <div style={styles.lastCheck}>
                        Last check: {printerStatus?.last_check ? new Date(printerStatus.last_check).toLocaleString() : '-'}
                    </div>
                    <Button onClick={handleRefresh}>🔄 Refresh</Button>
                </div>

                {/* Status & Statistics Row */}
                <div style={styles.statsRow}>
                    {/* Printer Status Card */}
                    <Card title="Printer Status" style={{ flex: 1 }}>
                        {statusLoading ? (
                            <div>Checking status...</div>
                        ) : (
                            <div style={styles.statusContent}>
                                <div style={{
                                    ...styles.statusIndicator,
                                    backgroundColor: printerStatus?.online ? '#4CAF50' : '#F44336'
                                }}>
                                    {printerStatus?.online ? 'ONLINE' : 'OFFLINE'}
                                </div>
                                <div style={styles.statusDetails}>
                                    <div><strong>IP:</strong> {printerStatus?.ip}:{printerStatus?.port}</div>
                                    <div><strong>Response:</strong> {printerStatus?.response_time_ms}ms</div>
                                    {printerStatus?.error && (
                                        <div style={{ color: '#F44336', marginTop: '5px' }}>
                                            Error: {printerStatus.error}
                                        </div>
                                    )}
                                </div>
                                <div style={styles.testActions}>
                                    <div style={styles.testTitle}>Test Print:</div>
                                    <div style={styles.testButtons}>
                                        <Button size="small" variant="secondary" onClick={() => handleTestPrint('WIP_LABEL')}>WIP</Button>
                                        <Button size="small" variant="secondary" onClick={() => handleTestPrint('SERIAL_LABEL')}>Serial</Button>
                                        <Button size="small" variant="secondary" onClick={() => handleTestPrint('LOT_LABEL')}>LOT</Button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </Card>

                    {/* Statistics Card */}
                    <Card title="Today's Statistics" style={{ flex: 2 }}>
                        {statsLoading ? (
                            <div>Loading statistics...</div>
                        ) : (
                            <div style={styles.statsGrid}>
                                <div style={styles.statItem}>
                                    <div style={styles.statLabel}>Total Prints</div>
                                    <div style={styles.statValue}>{statistics?.total_prints || 0}</div>
                                </div>
                                <div style={styles.statItem}>
                                    <div style={styles.statLabel}>Success</div>
                                    <div style={{ ...styles.statValue, color: '#4CAF50' }}>{statistics?.success_count || 0}</div>
                                </div>
                                <div style={styles.statItem}>
                                    <div style={styles.statLabel}>Failed</div>
                                    <div style={{ ...styles.statValue, color: '#F44336' }}>{statistics?.failed_count || 0}</div>
                                </div>
                                <div style={styles.statItem}>
                                    <div style={styles.statLabel}>Success Rate</div>
                                    <div style={styles.statValue}>{statistics?.success_rate || 0}%</div>
                                </div>
                            </div>
                        )}
                    </Card>
                </div>

                {/* Logs Section */}
                <Card title="Print History">
                    {/* Filters */}
                    <div style={styles.filters}>
                        <select
                            value={labelType}
                            onChange={(e) => { setLabelType(e.target.value); setPage(1); }}
                            style={styles.select}
                        >
                            <option value="">All Label Types</option>
                            <option value="WIP_LABEL">WIP Label</option>
                            <option value="SERIAL_LABEL">Serial Label</option>
                            <option value="LOT_LABEL">LOT Label</option>
                        </select>

                        <select
                            value={status}
                            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
                            style={styles.select}
                        >
                            <option value="">All Status</option>
                            <option value="SUCCESS">Success</option>
                            <option value="FAILED">Failed</option>
                        </select>
                    </div>

                    {/* Table */}
                    {logsLoading ? (
                        <div style={{ padding: '20px', textAlign: 'center' }}>Loading logs...</div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={styles.table}>
                                <thead>
                                    <tr>
                                        <th style={styles.th}>Time</th>
                                        <th style={styles.th}>Label Type</th>
                                        <th style={styles.th}>Label ID</th>
                                        <th style={styles.th}>Status</th>
                                        <th style={styles.th}>Printer</th>
                                        <th style={styles.th}>Message</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logsData?.logs.map((log) => (
                                        <tr key={log.id} style={styles.tr}>
                                            <td style={styles.td}>{new Date(log.created_at).toLocaleString()}</td>
                                            <td style={styles.td}>
                                                <span style={getLabelTypeStyle(log.label_type)}>{log.label_type}</span>
                                            </td>
                                            <td style={styles.td}>{log.label_id}</td>
                                            <td style={styles.td}>
                                                <span style={{
                                                    ...styles.badge,
                                                    backgroundColor: log.status === 'SUCCESS' ? '#E8F5E9' : '#FFEBEE',
                                                    color: log.status === 'SUCCESS' ? '#2E7D32' : '#C62828'
                                                }}>
                                                    {log.status}
                                                </span>
                                            </td>
                                            <td style={styles.td}>{log.printer_ip}</td>
                                            <td style={{ ...styles.td, color: log.error_message ? '#C62828' : 'inherit' }}>
                                                {log.error_message || '-'}
                                            </td>
                                        </tr>
                                    ))}
                                    {(!logsData?.logs || logsData.logs.length === 0) && (
                                        <tr>
                                            <td colSpan={6} style={{ ...styles.td, textAlign: 'center', padding: '30px' }}>
                                                No print logs found
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Pagination */}
                    <div style={styles.pagination}>
                        <Button
                            variant="secondary"
                            disabled={page === 1}
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                        >
                            Previous
                        </Button>
                        <span style={{ margin: '0 15px' }}>
                            Page {page} of {Math.ceil((logsData?.total || 0) / limit) || 1}
                        </span>
                        <Button
                            variant="secondary"
                            disabled={page >= (Math.ceil((logsData?.total || 0) / limit) || 1)}
                            onClick={() => setPage(p => p + 1)}
                        >
                            Next
                        </Button>
                    </div>
                </Card>
            </div>
        </MainLayout>
    );
};

const getLabelTypeStyle = (type: string) => {
    const baseStyle = {
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: '500',
    };

    switch (type) {
        case 'WIP_LABEL':
            return { ...baseStyle, backgroundColor: '#E3F2FD', color: '#1565C0' };
        case 'SERIAL_LABEL':
            return { ...baseStyle, backgroundColor: '#F3E5F5', color: '#7B1FA2' };
        case 'LOT_LABEL':
            return { ...baseStyle, backgroundColor: '#FFF3E0', color: '#EF6C00' };
        default:
            return baseStyle;
    }
};

const styles = {
    container: {
        padding: '20px',
        maxWidth: '1200px',
        margin: '0 auto',
    },
    header: {
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        marginBottom: '20px',
        gap: '15px',
    },
    lastCheck: {
        fontSize: '14px',
        color: '#666',
    },
    statsRow: {
        display: 'flex',
        gap: '20px',
        marginBottom: '20px',
        flexWrap: 'wrap' as const,
    },
    statusContent: {
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '15px',
    },
    statusIndicator: {
        padding: '10px',
        borderRadius: '6px',
        color: 'white',
        fontWeight: 'bold',
        textAlign: 'center' as const,
        fontSize: '18px',
    },
    statusDetails: {
        fontSize: '14px',
        lineHeight: '1.6',
    },
    testActions: {
        marginTop: '10px',
        padding: '15px',
        backgroundColor: '#f5f5f5',
        borderRadius: '6px',
    },
    testTitle: {
        fontSize: '13px',
        fontWeight: '600',
        marginBottom: '10px',
        color: '#555',
    },
    testButtons: {
        display: 'flex',
        gap: '8px',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '20px',
        padding: '10px 0',
    },
    statItem: {
        textAlign: 'center' as const,
        padding: '15px',
        backgroundColor: '#f9f9f9',
        borderRadius: '8px',
    },
    statLabel: {
        fontSize: '14px',
        color: '#666',
        marginBottom: '8px',
    },
    statValue: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333',
    },
    filters: {
        display: 'flex',
        gap: '15px',
        marginBottom: '20px',
    },
    select: {
        padding: '8px 12px',
        borderRadius: '4px',
        border: '1px solid #ddd',
        fontSize: '14px',
        minWidth: '150px',
    },
    table: {
        width: '100%',
        borderCollapse: 'collapse' as const,
        fontSize: '14px',
    },
    th: {
        textAlign: 'left' as const,
        padding: '12px',
        borderBottom: '2px solid #eee',
        color: '#666',
        fontWeight: '600',
    },
    tr: {
        borderBottom: '1px solid #eee',
    },
    td: {
        padding: '12px',
        verticalAlign: 'middle',
    },
    badge: {
        padding: '4px 8px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '500',
    },
    pagination: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: '20px',
    },
};

export default PrinterMonitoringPage;
