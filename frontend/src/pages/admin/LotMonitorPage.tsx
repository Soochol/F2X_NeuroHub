/**
 * LOT Management Page (formerly LOT Monitor)
 * Manage and monitor LOT status
 */

import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Card, Button, Input, Select } from '@/components/common';
import { LotDetailModal } from '@/components/lots';
import { lotsApi, serialsApi } from '@/api';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole, LotStatus, SerialStatus, type Lot, type Serial, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';
import { Download, AlertCircle } from 'lucide-react';

export const LotMonitorPage = () => {
    const { user } = useAuth();

    if (user?.role !== UserRole.ADMIN && user?.role !== UserRole.MANAGER) {
        return <Navigate to="/" replace />;
    }

    const [lots, setLots] = useState<Lot[]>([]);
    const [serials, setSerials] = useState<Serial[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedLotId, setSelectedLotId] = useState<number | null>(null);

    // Sorting
    type SortColumn = 'lot_number' | 'status' | 'target_quantity' | 'passed_quantity' | 'production_date' | 'created_at' | null;
    type SortDirection = 'asc' | 'desc';
    const [sortColumn, setSortColumn] = useState<SortColumn>('created_at');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

    useEffect(() => {
        fetchData();
    }, [statusFilter, sortColumn, sortDirection]);

    const fetchData = async () => {
        setIsLoading(true);
        setError('');
        try {
            const params: any = { limit: 100 };
            if (statusFilter) params.status = statusFilter;

            const lotsResponse = await lotsApi.getLots(params);
            setLots(lotsResponse);

            const serialsResponse = await serialsApi.getSerials({ limit: 500 });
            const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
            setSerials(serialsList);
        } catch (err: unknown) {
            setError(getErrorMessage(err, 'Failed to load data'));
        } finally {
            setIsLoading(false);
        }
    };

    const getLotSerialStats = (lot: Lot) => {
        const lotSerials = serials.filter((s) => s.lot_id === lot.id);
        const passed = lotSerials.filter((s) => s.status === SerialStatus.PASS).length;
        const failed = lotSerials.filter((s) => s.status === SerialStatus.FAIL).length;
        const inProgress = lotSerials.filter((s) => s.status === SerialStatus.IN_PROGRESS).length;
        const total = lotSerials.length;
        const missing = lot.target_quantity - total;

        return { total, passed, failed, inProgress, missing };
    };

    const handleExportCSV = () => {
        const headers = ['LOT Number', 'Status', 'Target Qty', 'Generated', 'Passed', 'Failed', 'Missing'];
        const rows = lots.map((lot) => {
            const stats = getLotSerialStats(lot);
            return [
                lot.lot_number,
                lot.status,
                lot.target_quantity,
                stats.total,
                stats.passed,
                stats.failed,
                stats.missing,
            ];
        });

        const csvContent = [
            headers.join(','),
            ...rows.map((row) => row.join(',')),
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lot-serial-report-${format(new Date(), 'yyyyMMdd-HHmmss')}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    const filteredAndSortedLots = lots
        .filter((lot) => {
            if (!searchQuery) return true;
            const query = searchQuery.toLowerCase();
            return (
                lot.lot_number.toLowerCase().includes(query) ||
                (lot.product_model?.model_name && lot.product_model.model_name.toLowerCase().includes(query)) ||
                (lot.product_model?.model_code && lot.product_model.model_code.toLowerCase().includes(query))
            );
        })
        .sort((a, b) => {
            if (!sortColumn) return 0;

            let comparison = 0;
            switch (sortColumn) {
                case 'lot_number':
                    comparison = a.lot_number.localeCompare(b.lot_number);
                    break;
                case 'status':
                    comparison = a.status.localeCompare(b.status);
                    break;
                case 'target_quantity':
                    comparison = a.target_quantity - b.target_quantity;
                    break;
                case 'passed_quantity':
                    comparison = (a.passed_quantity || 0) - (b.passed_quantity || 0);
                    break;
                case 'production_date':
                    comparison = new Date(a.production_date).getTime() - new Date(b.production_date).getTime();
                    break;
                case 'created_at':
                    comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
                    break;
            }

            return sortDirection === 'asc' ? comparison : -comparison;
        });

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                    <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px' }}>
                        LOT Management
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                        Manage and monitor LOT status
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <Button variant="secondary" onClick={handleExportCSV}>
                        <Download size={16} style={{ marginRight: '6px' }} />
                        Export CSV
                    </Button>
                    <Button variant="secondary" onClick={fetchData}>
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Quick Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <Card style={{ padding: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                        Total LOTs
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                        {lots.length}
                    </div>
                </Card>

                <Card style={{ padding: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                        Active LOTs
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-brand)' }}>
                        {lots.filter((l) => l.status === LotStatus.CREATED || l.status === LotStatus.IN_PROGRESS).length}
                    </div>
                </Card>
            </div>

            {/* Filters */}
            <Card style={{ marginBottom: '20px', padding: '20px' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                    <div style={{ flex: '1', minWidth: '200px' }}>
                        <Input
                            label="Search"
                            placeholder="LOT number, product model..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            wrapperStyle={{ marginBottom: 0 }}
                        />
                    </div>
                    <div style={{ width: '180px' }}>
                        <Select
                            label="Status"
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value as LotStatus | '')}
                            options={[
                                { value: '', label: 'All' },
                                { value: LotStatus.CREATED, label: 'Created' },
                                { value: LotStatus.IN_PROGRESS, label: 'In Progress' },
                                { value: LotStatus.COMPLETED, label: 'Completed' },
                                { value: LotStatus.CLOSED, label: 'Closed' },
                            ]}
                            wrapperStyle={{ marginBottom: 0 }}
                        />
                    </div>
                    <div style={{ width: '180px' }}>
                        <Select
                            label="Sort By"
                            value={sortColumn || ''}
                            onChange={(e) => setSortColumn(e.target.value as SortColumn)}
                            options={[
                                { value: 'created_at', label: 'Created Date' },
                                { value: 'lot_number', label: 'LOT Number' },
                                { value: 'status', label: 'Status' },
                                { value: 'target_quantity', label: 'Target Qty' },
                                { value: 'production_date', label: 'Production Date' },
                            ]}
                            wrapperStyle={{ marginBottom: 0 }}
                        />
                    </div>
                    <div style={{ width: '120px' }}>
                        <Select
                            label="Direction"
                            value={sortDirection}
                            onChange={(e) => setSortDirection(e.target.value as SortDirection)}
                            options={[
                                { value: 'desc', label: 'Descending' },
                                { value: 'asc', label: 'Ascending' },
                            ]}
                            wrapperStyle={{ marginBottom: 0 }}
                        />
                    </div>
                    <Button
                        variant="secondary"
                        onClick={() => {
                            setSearchQuery('');
                            setStatusFilter('');
                            setSortColumn('created_at');
                            setSortDirection('desc');
                            fetchData();
                        }}
                    >
                        Reset
                    </Button>
                </div>
            </Card>

            {/* LOT List */}
            <Card>

                <div style={{ padding: '20px' }}>
                    {isLoading ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                            Loading...
                        </div>
                    ) : error ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
                            {error}
                        </div>
                    ) : filteredAndSortedLots.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                            No LOTs found
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '15px' }}>
                            {filteredAndSortedLots.map((lot) => {
                                const stats = getLotSerialStats(lot);
                                const hasMissing = stats.missing > 0;
                                // Use LOT's passed_quantity from backend, not frontend serial filtering
                                const completionRate = lot.target_quantity > 0
                                    ? ((lot.passed_quantity || 0) / lot.target_quantity) * 100
                                    : 0;

                                // 테두리 색상 결정 로직
                                const isCompleted = lot.status === LotStatus.COMPLETED || lot.status === LotStatus.CLOSED;
                                const borderColor = isCompleted
                                    ? '2px solid var(--color-success)'
                                    : hasMissing
                                        ? '2px solid var(--color-warning)'
                                        : '1px solid var(--color-border)';

                                return (
                                    <div
                                        key={lot.id}
                                        onClick={() => setSelectedLotId(lot.id)}
                                        style={{
                                            padding: '20px',
                                            border: borderColor,
                                            borderRadius: '8px',
                                            backgroundColor: 'var(--color-bg-secondary)',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s',
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                                            e.currentTarget.style.transform = 'translateY(-2px)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.boxShadow = 'none';
                                            e.currentTarget.style.transform = 'translateY(0)';
                                        }}
                                    >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                                    <span style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace' }}>
                                                        {lot.lot_number}
                                                    </span>
                                                    <span
                                                        style={{
                                                            padding: '4px 8px',
                                                            borderRadius: '4px',
                                                            fontSize: '12px',
                                                            backgroundColor:
                                                                lot.status === LotStatus.COMPLETED
                                                                    ? 'var(--color-success-bg)'
                                                                    : lot.status === LotStatus.IN_PROGRESS
                                                                        ? 'var(--color-info-bg)'
                                                                        : 'var(--color-warning-bg)',
                                                            color:
                                                                lot.status === LotStatus.COMPLETED
                                                                    ? 'var(--color-success)'
                                                                    : lot.status === LotStatus.IN_PROGRESS
                                                                        ? 'var(--color-info)'
                                                                        : 'var(--color-warning)',
                                                        }}
                                                    >
                                                        {lot.status}
                                                    </span>
                                                    {hasMissing && (
                                                        <span
                                                            style={{
                                                                padding: '4px 8px',
                                                                borderRadius: '4px',
                                                                fontSize: '12px',
                                                                backgroundColor: 'var(--color-warning-bg)',
                                                                color: 'var(--color-warning)',
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                gap: '4px',
                                                            }}
                                                        >
                                                            <AlertCircle size={12} />
                                                            Missing {stats.missing} serials
                                                        </span>
                                                    )}
                                                </div>
                                                {lot.product_model && (
                                                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                                                        {lot.product_model.model_code} - {lot.product_model.model_name}
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', marginBottom: '15px' }}>
                                            <div>
                                                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                                    Generated
                                                </div>
                                                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                                    {stats.total} / {lot.target_quantity}
                                                </div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                                    Passed
                                                </div>
                                                <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--color-success)' }}>
                                                    {stats.passed}
                                                </div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                                    Failed
                                                </div>
                                                <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--color-error)' }}>
                                                    {stats.failed}
                                                </div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                                    Completion
                                                </div>
                                                <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--color-brand)' }}>
                                                    {completionRate.toFixed(0)}%
                                                </div>
                                            </div>
                                        </div>

                                        {/* Progress bar */}
                                        <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--color-bg-tertiary)', borderRadius: '4px', overflow: 'hidden' }}>
                                            <div
                                                style={{
                                                    width: `${completionRate}%`,
                                                    height: '100%',
                                                    backgroundColor: completionRate === 100 ? 'var(--color-success)' : 'var(--color-brand)',
                                                    transition: 'width 0.3s',
                                                }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </Card>

            {/* LOT Detail Modal */}
            {selectedLotId && (
                <LotDetailModal
                    isOpen={!!selectedLotId}
                    onClose={() => setSelectedLotId(null)}
                    lotId={selectedLotId}
                    onUpdate={fetchData}
                />
            )}
        </div>
    );
};
