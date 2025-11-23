/**
 * LOT Issuance Page
 * Create and manage LOTs
 */

import { useState, useEffect } from 'react';
import { Button, Select, Input, Card } from '@/components/common';
import { LotCreateModal } from '@/components/lots';
import { lotsApi, productionLinesApi, serialsApi } from '@/api';
import apiClient from '@/api/client';
import { LotStatus, SerialStatus, type Lot, type ProductModel, type ProductionLine, type Serial, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';
import { AlertCircle, Plus } from 'lucide-react';

export const LotsPage = () => {
  const [lots, setLots] = useState<Lot[]>([]);
  const [serials, setSerials] = useState<Serial[]>([]);
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [productionLines, setProductionLines] = useState<ProductionLine[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const [totalLots, setTotalLots] = useState(0);
  const lotsPerPage = 20;
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Sorting
  type SortColumn = 'lot_number' | 'status' | 'target_quantity' | 'passed_quantity' | 'production_date' | 'created_at' | null;
  type SortDirection = 'asc' | 'desc';
  const [sortColumn, setSortColumn] = useState<SortColumn>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    fetchProductModels();
    fetchProductionLines();
    fetchData();
  }, [statusFilter, currentPage, refreshTrigger, sortColumn, sortDirection]);

  const fetchProductModels = async () => {
    try {
      const response = await apiClient.get<ProductModel[]>('/product-models/');
      setProductModels(response.data);
    } catch (err: unknown) {
      console.error('Failed to fetch product models:', err);
    }
  };

  const fetchProductionLines = async () => {
    try {
      const lines = await productionLinesApi.getActiveProductionLines();
      setProductionLines(lines);
    } catch (err: unknown) {
      console.error('Failed to fetch production lines:', err);
    }
  };

  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params: { skip?: number; limit?: number; status?: LotStatus } = {
        skip: currentPage * lotsPerPage,
        limit: lotsPerPage,
      };
      if (statusFilter) {
        params.status = statusFilter;
      }

      const response = await lotsApi.getLots(params);
      if (Array.isArray(response)) {
        setLots(response);
        setTotalLots(response.length);
      } else {
        setLots(response.items);
        setTotalLots(response.total);
      }

      const serialsResponse = await serialsApi.getSerials({ limit: 500 });
      const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
      setSerials(serialsList);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load LOT list'));
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

  const handleCreateSuccess = () => {
    setIsCreateModalOpen(false);
    setCurrentPage(0);
    setRefreshTrigger(prev => prev + 1);
  };

  const filteredAndSortedLots = lots
    .filter((lot) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          lot.lot_number.toLowerCase().includes(query) ||
          (lot.product_model?.model_name && lot.product_model.model_name.toLowerCase().includes(query)) ||
          (lot.product_model?.model_code && lot.product_model.model_code.toLowerCase().includes(query))
        );
      }
      return true;
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

  const totalPages = Math.ceil(totalLots / lotsPerPage);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Fixed Header Section - Page Header and Filters */}
      <div style={{
        flexShrink: 0,
        marginBottom: '20px',
        backgroundColor: 'var(--color-bg-secondary)',
        position: 'sticky',
        top: '-20px',
        zIndex: 10,
        paddingTop: '20px',
        paddingBottom: '20px',
        marginTop: '-20px',
        paddingLeft: '20px',
        paddingRight: '20px',
        marginLeft: '-20px',
        marginRight: '-20px',
        borderBottom: '2px solid var(--color-border)'
      }}>
        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px' }}>
              LOT Issuance
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
              Create and manage production LOTs
            </p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus size={16} style={{ marginRight: '6px' }} />
            Create LOT
          </Button>
        </div>

        {/* Filters */}
        <Card>
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
                onChange={(e) => {
                  setStatusFilter(e.target.value as LotStatus | '');
                  setCurrentPage(0);
                }}
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
            <Button variant="secondary" onClick={() => { setSearchQuery(''); setStatusFilter(''); setCurrentPage(0); setRefreshTrigger(prev => prev + 1); }}>
              Reset
            </Button>
          </div>
        </Card>
      </div>

      {/* Scrollable Content Section - LOT Cards */}
      <div>
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
              <>
                <div style={{ display: 'grid', gap: '15px', marginBottom: '20px' }}>
                  {filteredAndSortedLots.map((lot) => {
                    const stats = getLotSerialStats(lot);
                    const hasMissing = stats.missing > 0;
                    const completionRate = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0;

                    const isCompleted = lot.status === LotStatus.COMPLETED || lot.status === LotStatus.CLOSED;
                    const borderColor = isCompleted
                      ? '2px solid var(--color-success)'
                      : hasMissing
                        ? '2px solid var(--color-warning)'
                        : '1px solid var(--color-border)';

                    return (
                      <div
                        key={lot.id}
                        style={{
                          padding: '20px',
                          border: borderColor,
                          borderRadius: '8px',
                          backgroundColor: 'var(--color-bg-secondary)',
                          transition: 'all 0.2s',
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
                            <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                              Created: {format(new Date(lot.created_at), 'yyyy-MM-dd HH:mm')}
                            </div>
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

                {totalPages > 1 && (
                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px', marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--color-border)' }}>
                    <Button
                      variant="secondary"
                      onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                      disabled={currentPage === 0}
                    >
                      Previous
                    </Button>
                    <span style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                      Page {currentPage + 1} of {totalPages} ({totalLots} total LOTs)
                    </span>
                    <Button
                      variant="secondary"
                      onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                      disabled={currentPage >= totalPages - 1}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </Card>
      </div>

      <LotCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleCreateSuccess}
        productModels={productModels}
        productionLines={productionLines}
      />
    </div>
  );
};
