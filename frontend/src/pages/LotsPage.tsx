import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Button, Select, Input, Card } from '@/components/common';
import { LotCreateModal } from '@/components/lots';
import { LotStatus, SerialStatus, type Lot } from '@/types/api';
import { format } from 'date-fns';
import { AlertCircle, Plus } from 'lucide-react';
import styles from './LotsPage.module.css';
import { useLots, useProductModels, useProductionLines, useSerials } from '@/hooks';

export const LotsPage = () => {
  const queryClient = useQueryClient();

  // Filters
  const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const lotsPerPage = 20;

  // Sorting
  type SortColumn = 'lot_number' | 'status' | 'target_quantity' | 'passed_quantity' | 'production_date' | 'created_at' | null;
  type SortDirection = 'asc' | 'desc';
  const [sortColumn, setSortColumn] = useState<SortColumn>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Data Fetching
  const { data, isLoading: isLotsLoading, error: lotsError } = useLots({
    skip: currentPage * lotsPerPage,
    limit: lotsPerPage,
    status: statusFilter,
  });

  const { data: productModels = [] } = useProductModels();
  const { data: productionLines = [] } = useProductionLines();
  const { data: serialsResponse } = useSerials({ limit: 500 });

  const lots = data?.lots || [];
  const totalLots = data?.total || 0;
  const serials = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse?.items || [];

  const isLoading = isLotsLoading;
  const error = lotsError ? 'Failed to load LOT list' : '';

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
    queryClient.invalidateQueries({ queryKey: ['lots'] });
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
    <div className={styles.pageContainer}>
      {/* Fixed Header Section - Page Header and Filters */}
      <div className={styles.headerSection}>
        {/* Page Header */}
        <div className={styles.headerContent}>
          <div>
            <h1 className={styles.pageTitle}>
              LOT Issuance
            </h1>
            <p className={styles.pageSubtitle}>
              Create and manage production LOTs
            </p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus size={16} className={styles.createButtonIcon} />
            Create LOT
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <div className={styles.filterContainer}>
            <div className={styles.filterInput}>
              <Input
                label="Search"
                placeholder="LOT number, product model..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                wrapperStyle={{ marginBottom: 0 }}
              />
            </div>
            <div className={styles.filterSelect}>
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
            <div className={styles.filterSelect}>
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
            <div className={styles.filterSelectSmall}>
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
            <Button variant="secondary" onClick={() => { setSearchQuery(''); setStatusFilter(''); setCurrentPage(0); }}>
              Reset
            </Button>
          </div>
        </Card>
      </div>

      {/* Scrollable Content Section - LOT Cards */}
      <div>
        <Card>
          <div className={styles.contentPadding}>
            {isLoading ? (
              <div className={styles.loadingContainer}>
                Loading...
              </div>
            ) : error ? (
              <div className={styles.errorContainer}>
                {error}
              </div>
            ) : filteredAndSortedLots.length === 0 ? (
              <div className={styles.emptyContainer}>
                No LOTs found
              </div>
            ) : (
              <>
                <div className={styles.gridContainer}>
                  {filteredAndSortedLots.map((lot) => {
                    const stats = getLotSerialStats(lot);
                    const hasMissing = stats.missing > 0;
                    const completionRate = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0;

                    const isCompleted = lot.status === LotStatus.COMPLETED || lot.status === LotStatus.CLOSED;

                    let cardClassName = styles.lotCard;
                    if (isCompleted) {
                      cardClassName += ` ${styles.lotCardCompleted}`;
                    } else if (hasMissing) {
                      cardClassName += ` ${styles.lotCardMissing}`;
                    }

                    return (
                      <div
                        key={lot.id}
                        className={cardClassName}
                      >
                        <div className={styles.lotHeader}>
                          <div className={styles.lotHeaderContent}>
                            <div className={styles.lotTitleRow}>
                              <span className={styles.lotNumber}>
                                {lot.lot_number}
                              </span>
                              <span
                                className={`${styles.statusBadge} ${lot.status === LotStatus.COMPLETED
                                    ? styles.statusBadgeSuccess
                                    : lot.status === LotStatus.IN_PROGRESS
                                      ? styles.statusBadgeInfo
                                      : styles.statusBadgeWarning
                                  }`}
                              >
                                {lot.status}
                              </span>
                              {hasMissing && (
                                <span className={styles.missingBadge}>
                                  <AlertCircle size={12} />
                                  Missing {stats.missing} serials
                                </span>
                              )}
                            </div>
                            {lot.product_model && (
                              <div className={styles.lotInfo}>
                                {lot.product_model.model_code} - {lot.product_model.model_name}
                              </div>
                            )}
                            <div className={styles.lotDate}>
                              Created: {format(new Date(lot.created_at), 'yyyy-MM-dd HH:mm')}
                            </div>
                          </div>
                        </div>

                        <div className={styles.statsGrid}>
                          <div>
                            <div className={styles.statLabel}>
                              Generated
                            </div>
                            <div className={styles.statValue}>
                              {stats.total} / {lot.target_quantity}
                            </div>
                          </div>
                          <div>
                            <div className={styles.statLabel}>
                              Passed
                            </div>
                            <div className={`${styles.statValue} ${styles.statValueSuccess}`}>
                              {stats.passed}
                            </div>
                          </div>
                          <div>
                            <div className={styles.statLabel}>
                              Failed
                            </div>
                            <div className={`${styles.statValue} ${styles.statValueError}`}>
                              {stats.failed}
                            </div>
                          </div>
                          <div>
                            <div className={styles.statLabel}>
                              Completion
                            </div>
                            <div className={`${styles.statValue} ${styles.statValueBrand}`}>
                              {completionRate.toFixed(0)}%
                            </div>
                          </div>
                        </div>

                        <div className={styles.progressBarContainer}>
                          <div
                            className={`${styles.progressBar} ${completionRate === 100 ? styles.progressBarSuccess : styles.progressBarBrand
                              }`}
                            style={{
                              width: `${completionRate}%`,
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {totalPages > 1 && (
                  <div className={styles.paginationContainer}>
                    <Button
                      variant="secondary"
                      onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                      disabled={currentPage === 0}
                    >
                      Previous
                    </Button>
                    <span className={styles.paginationText}>
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
