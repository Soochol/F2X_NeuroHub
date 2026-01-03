/**
 * Results page - View and manage execution results with reports.
 */

import { useState, useCallback } from 'react';
import { ClipboardList, List, BarChart2 } from 'lucide-react';
import { useBatchList, useResultList, useResult, useExportResultsBulk } from '../hooks';
import { Select } from '../components/atoms/Select';
import {
  ResultsFilter,
  ResultsTable,
  ResultDetailModal,
  ReportTypeSelector,
  BatchSummaryReport,
  PeriodStatsReport,
  StepAnalysisReport,
  ExportButton,
} from '../components/organisms/results';
import type { ExecutionStatus, ExecutionSummary, ReportType, ExportFormat } from '../types';

type ViewMode = 'list' | 'reports';

export function ResultsPage() {
  // View mode
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  // Filters state
  const [batchFilter, setBatchFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<ExecutionStatus | ''>('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [searchFilter, setSearchFilter] = useState('');

  // Sort state
  const [sortField, setSortField] = useState('startedAt');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Selection state
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedResult, setSelectedResult] = useState<ExecutionSummary | null>(null);
  const [detailResultId, setDetailResultId] = useState<string | null>(null);

  // Report state
  const [reportType, setReportType] = useState<ReportType>('batch_summary');
  const [reportBatchId, setReportBatchId] = useState<string | null>(null);

  // Data fetching
  const { data: batches } = useBatchList();
  const { data: resultsData, isLoading: resultsLoading } = useResultList(
    {
      batchId: batchFilter || undefined,
      status: statusFilter === 'completed' || statusFilter === 'failed' ? statusFilter : undefined,
      from: fromDate || undefined,
      to: toDate || undefined,
    }
  );

  const { data: detailResult } = useResult(detailResultId ?? '');
  const bulkExportMutation = useExportResultsBulk();

  // Handlers
  const handleClearFilters = useCallback(() => {
    setBatchFilter('');
    setStatusFilter('');
    setFromDate('');
    setToDate('');
    setSearchFilter('');
  }, []);

  const handleSort = useCallback((field: string) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  }, [sortField]);

  const handleViewDetail = useCallback((result: ExecutionSummary) => {
    setSelectedResult(result);
    setDetailResultId(result.id);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedResult(null);
    setDetailResultId(null);
  }, []);

  const handleBulkExport = useCallback((format: ExportFormat) => {
    if (selectedIds.length === 0) return;
    bulkExportMutation.mutate({
      resultIds: selectedIds,
      format,
      includeStepDetails: true,
    });
  }, [selectedIds, bulkExportMutation]);

  // Filter and sort results
  const filteredResults = (resultsData?.items ?? [])
    .filter((result) => {
      if (searchFilter) {
        return result.sequenceName.toLowerCase().includes(searchFilter.toLowerCase());
      }
      return true;
    })
    .sort((a, b) => {
      let aVal: string | number | Date = '';
      let bVal: string | number | Date = '';

      switch (sortField) {
        case 'status':
          aVal = a.status;
          bVal = b.status;
          break;
        case 'sequenceName':
          aVal = a.sequenceName;
          bVal = b.sequenceName;
          break;
        case 'batchId':
          aVal = a.batchId || '';
          bVal = b.batchId || '';
          break;
        case 'startedAt':
          aVal = new Date(a.startedAt).getTime();
          bVal = new Date(b.startedAt).getTime();
          break;
        case 'duration':
          aVal = a.duration ?? 0;
          bVal = b.duration ?? 0;
          break;
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      return sortDirection === 'asc'
        ? Number(aVal) - Number(bVal)
        : Number(bVal) - Number(aVal);
    });

  // Batch options for report selector
  const batchOptions = [
    { value: '', label: 'Select a batch...' },
    ...(batches?.map((b) => ({ value: b.id, label: b.name })) ?? []),
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ClipboardList className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Results
          </h2>
        </div>

        {/* View Mode Toggle */}
        <div
          className="flex rounded-lg p-1"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <button
            onClick={() => setViewMode('list')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              viewMode === 'list' ? 'shadow-sm' : ''
            }`}
            style={{
              backgroundColor: viewMode === 'list' ? 'var(--color-bg-elevated)' : 'transparent',
              color: viewMode === 'list' ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
            }}
          >
            <List className="w-4 h-4" />
            List
          </button>
          <button
            onClick={() => setViewMode('reports')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              viewMode === 'reports' ? 'shadow-sm' : ''
            }`}
            style={{
              backgroundColor: viewMode === 'reports' ? 'var(--color-bg-elevated)' : 'transparent',
              color: viewMode === 'reports' ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
            }}
          >
            <BarChart2 className="w-4 h-4" />
            Reports
          </button>
        </div>
      </div>

      {viewMode === 'list' ? (
        <>
          {/* Filters */}
          <ResultsFilter
            batchId={batchFilter}
            onBatchChange={setBatchFilter}
            status={statusFilter}
            onStatusChange={setStatusFilter}
            fromDate={fromDate}
            onFromDateChange={setFromDate}
            toDate={toDate}
            onToDateChange={setToDate}
            search={searchFilter}
            onSearchChange={setSearchFilter}
            onClear={handleClearFilters}
            batches={batches?.map((b) => ({ id: b.id, name: b.name })) ?? []}
          />

          {/* Actions Bar */}
          {selectedIds.length > 0 && (
            <div
              className="flex items-center justify-between p-3 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            >
              <span className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                {selectedIds.length} result(s) selected
              </span>
              <ExportButton
                onExport={handleBulkExport}
                isLoading={bulkExportMutation.isPending}
              />
            </div>
          )}

          {/* Results Table */}
          <ResultsTable
            results={filteredResults}
            isLoading={resultsLoading}
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            onViewDetail={handleViewDetail}
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />

          {/* Pagination Info */}
          {resultsData && (
            <div className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              Showing {filteredResults.length} of {resultsData.total} results
            </div>
          )}
        </>
      ) : (
        <div className="space-y-6">
          {/* Report Type Selector */}
          <ReportTypeSelector
            selectedType={reportType}
            onSelect={setReportType}
          />

          {/* Report Content */}
          <div
            className="p-6 rounded-lg border"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border-default)',
            }}
          >
            {reportType === 'batch_summary' && (
              <div className="space-y-4">
                <div className="max-w-xs">
                  <label className="block text-xs mb-1" style={{ color: 'var(--color-text-tertiary)' }}>
                    Select Batch
                  </label>
                  <Select
                    options={batchOptions}
                    value={reportBatchId ?? ''}
                    onChange={(e) => setReportBatchId(e.target.value || null)}
                  />
                </div>
                <BatchSummaryReport
                  batchId={reportBatchId}
                  batchName={batches?.find((b) => b.id === reportBatchId)?.name}
                />
              </div>
            )}

            {reportType === 'period_stats' && (
              <PeriodStatsReport batchId={reportBatchId ?? undefined} />
            )}

            {reportType === 'step_analysis' && (
              <StepAnalysisReport batchId={reportBatchId ?? undefined} />
            )}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedResult && detailResult && (
        <ResultDetailModal
          result={detailResult}
          onClose={handleCloseDetail}
        />
      )}
    </div>
  );
}
