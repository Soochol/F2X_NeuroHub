/**
 * Admin Serial Management Page
 * Comprehensive serial and LOT management for administrators
 */

import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Card, Button, Input, Select, Modal } from '@/components/common';
import { lotsApi, serialsApi } from '@/api';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole, LotStatus, SerialStatus, type Lot, type Serial, type LotQueryParams, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';
import { AlertTriangle, Download, AlertCircle } from 'lucide-react';

interface ProblemSerial {
  serial: Serial;
  issue: string;
  severity: 'high' | 'medium' | 'low';
}

export const AdminSerialManagement = () => {
  const { user } = useAuth();

  // Permission check
  if (user?.role !== UserRole.ADMIN && user?.role !== UserRole.MANAGER) {
    return <Navigate to="/" replace />;
  }

  const [lots, setLots] = useState<Lot[]>([]);
  const [serials, setSerials] = useState<Serial[]>([]);
  const [problemSerials, setProblemSerials] = useState<ProblemSerial[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal states
  const [showStatusChangeModal, setShowStatusChangeModal] = useState(false);
  const [selectedSerial, setSelectedSerial] = useState<Serial | null>(null);
  const [newStatus, setNewStatus] = useState<SerialStatus>(SerialStatus.PASS);
  const [changeReason, setChangeReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Fetch LOTs
      const params: Partial<LotQueryParams> = { limit: 100 };
      if (statusFilter) params.status = statusFilter;

      const lotsResponse = await lotsApi.getLots(params);
      setLots(lotsResponse);

      // Fetch all serials for analysis
      const serialsResponse = await serialsApi.getSerials({ limit: 500 });
      const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
      setSerials(serialsList);

      // Identify problem serials
      const problems = identifyProblemSerials(serialsList);
      setProblemSerials(problems);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load data'));
    } finally {
      setIsLoading(false);
    }
  };

  const identifyProblemSerials = (serialsList: Serial[]): ProblemSerial[] => {
    const problems: ProblemSerial[] = [];
    const now = new Date();

    serialsList.forEach((serial) => {
      // Check for stuck serials (24+ hours)
      if (serial.status === SerialStatus.IN_PROGRESS && serial.created_at) {
        const hoursSinceCreation = (now.getTime() - new Date(serial.created_at).getTime()) / (1000 * 60 * 60);
        if (hoursSinceCreation > 24) {
          problems.push({
            serial,
            issue: `Stuck in process for ${Math.floor(hoursSinceCreation)} hours`,
            severity: 'high',
          });
        }
      }

      // Check for excessive rework
      if (serial.rework_count && serial.rework_count >= 3) {
        problems.push({
          serial,
          issue: `Rework count: ${serial.rework_count} (maximum reached)`,
          severity: 'high',
        });
      }

      // Check for failed serials
      if (serial.status === SerialStatus.FAIL) {
        problems.push({
          serial,
          issue: 'Failed - requires action',
          severity: 'medium',
        });
      }
    });

    return problems;
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

  const handleForceStatusChange = async () => {
    if (!selectedSerial || !changeReason.trim()) {
      alert('Please provide a reason for this change');
      return;
    }

    setIsSubmitting(true);
    try {
      await serialsApi.updateSerialStatus(selectedSerial.id, {
        status: newStatus,
        failure_reason: changeReason,
      });

      alert('Status changed successfully');
      setShowStatusChangeModal(false);
      setSelectedSerial(null);
      setChangeReason('');
      await fetchData();
    } catch (err: unknown) {
      alert(getErrorMessage(err, 'Failed to change status'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExportCSV = () => {
    // Generate CSV content
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

    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lot-serial-report-${format(new Date(), 'yyyyMMdd-HHmmss')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const filteredLots = lots.filter((lot) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      lot.lot_number.toLowerCase().includes(query) ||
      (lot.product_model?.model_name && lot.product_model.model_name.toLowerCase().includes(query))
    );
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px', color: 'var(--color-text-primary)' }}>
            Admin - Serial & LOT Management
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
            Comprehensive management and troubleshooting
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
            {lots.filter((l) => l.status === LotStatus.IN_PROGRESS).length}
          </div>
        </Card>

        <Card style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
            Problem Serials
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-error)' }}>
            {problemSerials.length}
          </div>
        </Card>
      </div>

      {/* Problem Serials Section */}
      {problemSerials.length > 0 && (
        <Card style={{ marginBottom: '24px' }}>
          <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)' }}>
            <h2 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={20} style={{ color: 'var(--color-error)' }} />
              Serials Requiring Attention
            </h2>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ display: 'grid', gap: '12px' }}>
              {problemSerials.slice(0, 10).map((problem) => (
                <div
                  key={problem.serial.id}
                  style={{
                    padding: '15px',
                    border: `2px solid ${
                      problem.severity === 'high'
                        ? 'var(--color-error)'
                        : problem.severity === 'medium'
                        ? 'var(--color-warning)'
                        : 'var(--color-info)'
                    }`,
                    borderRadius: '6px',
                    backgroundColor: 'var(--color-bg-secondary)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace', marginBottom: '8px', color: 'var(--color-text-primary)' }}>
                        {problem.serial.serial_number}
                      </div>
                      <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                        {problem.issue}
                      </div>
                      {problem.serial.lot && (
                        <div style={{ fontSize: '13px', color: 'var(--color-text-tertiary)' }}>
                          LOT: {problem.serial.lot.lot_number}
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => {
                          setSelectedSerial(problem.serial);
                          setNewStatus(SerialStatus.PASS);
                          setShowStatusChangeModal(true);
                        }}
                      >
                        Force Complete
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => {
                          setSelectedSerial(problem.serial);
                          setNewStatus(SerialStatus.CREATED);
                          setShowStatusChangeModal(true);
                        }}
                      >
                        Reset
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* LOT List with Serial Status */}
      <Card>
        <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: 'var(--color-text-primary)' }}>
            LOT List with Serial Status
          </h2>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ flex: 1 }}>
              <Input
                placeholder="Search LOT number or product..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                wrapperStyle={{ marginBottom: 0 }}
              />
            </div>
            <div style={{ width: '200px' }}>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as LotStatus | '')}
                options={[
                  { value: '', label: 'All Status' },
                  { value: LotStatus.CREATED, label: 'Created' },
                  { value: LotStatus.IN_PROGRESS, label: 'In Progress' },
                  { value: LotStatus.COMPLETED, label: 'Completed' },
                  { value: LotStatus.CLOSED, label: 'Closed' },
                ]}
                wrapperStyle={{ marginBottom: 0 }}
              />
            </div>
          </div>
        </div>

        <div style={{ padding: '20px' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              Loading...
            </div>
          ) : error ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
              {error}
            </div>
          ) : filteredLots.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              No LOTs found
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {filteredLots.map((lot) => {
                const stats = getLotSerialStats(lot);
                const hasMissing = stats.missing > 0;
                const completionRate = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0;

                return (
                  <div
                    key={lot.id}
                    style={{
                      padding: '20px',
                      border: hasMissing ? '2px solid var(--color-warning)' : '1px solid var(--color-border)',
                      borderRadius: '8px',
                      backgroundColor: 'var(--color-bg-secondary)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                          <span style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
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
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
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

      {/* Force Status Change Modal */}
      <Modal
        isOpen={showStatusChangeModal}
        onClose={() => {
          setShowStatusChangeModal(false);
          setSelectedSerial(null);
          setChangeReason('');
        }}
        title="Force Status Change - DANGER"
        width="600px"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                setShowStatusChangeModal(false);
                setSelectedSerial(null);
                setChangeReason('');
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleForceStatusChange} disabled={isSubmitting || !changeReason.trim()}>
              {isSubmitting ? 'Changing...' : 'Confirm & Change'}
            </Button>
          </>
        }
      >
        {selectedSerial && (
          <div>
            <div
              style={{
                padding: '15px',
                backgroundColor: 'var(--color-error-bg)',
                borderLeft: '4px solid var(--color-error)',
                borderRadius: '6px',
                marginBottom: '20px',
              }}
            >
              <div style={{ display: 'flex', gap: '10px', alignItems: 'start' }}>
                <AlertTriangle size={20} style={{ color: 'var(--color-error)', flexShrink: 0 }} />
                <div style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                  <strong>Warning:</strong> This bypasses normal workflow rules! Use only for emergency situations.
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '8px' }}>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>
                Serial Number:
              </div>
              <div style={{ fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
                {selectedSerial.serial_number}
              </div>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginTop: '10px' }}>
                Current Status: <strong>{selectedSerial.status}</strong>
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <Select
                label="New Status"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as SerialStatus)}
                options={[
                  { value: SerialStatus.CREATED, label: 'Created' },
                  { value: SerialStatus.IN_PROGRESS, label: 'In Progress' },
                  { value: SerialStatus.PASS, label: 'Pass' },
                  { value: SerialStatus.FAIL, label: 'Fail' },
                ]}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>
                Reason (Required) <span style={{ color: 'var(--color-error)' }}>*</span>
              </label>
              <textarea
                value={changeReason}
                onChange={(e) => setChangeReason(e.target.value)}
                placeholder="Explain why this status change is necessary..."
                required
                style={{
                  width: '100%',
                  minHeight: '100px',
                  padding: '10px',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  fontSize: '14px',
                  resize: 'vertical',
                  backgroundColor: 'var(--color-bg-primary)',
                  color: 'var(--color-text-primary)',
                }}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
