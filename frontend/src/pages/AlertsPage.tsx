/**
 * Alerts Page
 */

import { useState, useEffect, useRef } from 'react';
import { Card, Button, Select } from '@/components/common';
import { alertsApi } from '@/api';
import { AlertSeverity, AlertStatus, type Alert } from '@/types/api';
import { format } from 'date-fns';
import { formatSerialNumber } from '@/utils/serialNumber';

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | ''>('');
  const [statusFilter, setStatusFilter] = useState<AlertStatus | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const alertsPerPage = 20;

  // Bulk selection
  const [selectedAlertIds, setSelectedAlertIds] = useState<Set<number>>(new Set());
  const [expandedAlertIds, setExpandedAlertIds] = useState<Set<number>>(new Set());

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter, currentPage]);

  const fetchAlerts = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params: any = {
        skip: currentPage * alertsPerPage,
        limit: alertsPerPage,
      };
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.status = statusFilter;

      const response = await alertsApi.getAlerts(params);
      setAlerts(response.alerts);
      setTotalAlerts(response.total);
      setUnreadCount(response.unread_count);
    } catch (err: any) {
      setError(err.message || 'Failed to load alerts');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async (alertId: number) => {
    try {
      await alertsApi.markAsRead(alertId);
      fetchAlerts();
    } catch (err: any) {
      console.error('Failed to mark as read:', err);
    }
  };

  const handleBulkMarkAsRead = async () => {
    try {
      const ids = Array.from(selectedAlertIds);
      await alertsApi.bulkMarkAsRead(ids);
      setSelectedAlertIds(new Set());
      fetchAlerts();
    } catch (err: any) {
      console.error('Failed to bulk mark as read:', err);
    }
  };

  const handleSelectAll = () => {
    if (selectedAlertIds.size === filteredAlerts.length) {
      setSelectedAlertIds(new Set());
    } else {
      setSelectedAlertIds(new Set(filteredAlerts.map((a) => a.id)));
    }
  };

  const toggleExpand = (alertId: number) => {
    const newExpanded = new Set(expandedAlertIds);
    if (newExpanded.has(alertId)) {
      newExpanded.delete(alertId);
    } else {
      newExpanded.add(alertId);
    }
    setExpandedAlertIds(newExpanded);
  };

  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case AlertSeverity.HIGH:
        return { bg: 'var(--color-error)', color: 'var(--color-error)', icon: '=', label: 'High' };
      case AlertSeverity.MEDIUM:
        return { bg: 'var(--color-warning)', color: 'var(--color-warning)', icon: ' ', label: 'Medium' };
      case AlertSeverity.LOW:
        return { bg: 'var(--color-bg-tertiary)', color: 'var(--color-brand)', icon: '9 ', label: 'Low' };
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        alert.title.toLowerCase().includes(query) ||
        alert.message.toLowerCase().includes(query) ||
        alert.serial_number?.toLowerCase().includes(query) ||
        alert.lot_number?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const totalPages = Math.ceil(totalAlerts / alertsPerPage);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>System Alerts & Notifications</h1>
        {unreadCount > 0 && (
          <span
            style={{
              padding: '6px 12px',
              backgroundColor: 'var(--color-error)',
              color: 'var(--color-text-inverse)',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            {unreadCount} Unread
          </span>
        )}
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label
              htmlFor="searchQuery"
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'var(--color-text-primary)'
              }}
            >
              Search
            </label>
            <div style={{ position: 'relative' }}>
              <span
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--color-text-secondary)',
                  fontSize: '18px'
                }}
              >
                🔍
              </span>
              <input
                ref={inputRef}
                id="searchQuery"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, serial, or lot number..."
                style={{
                  width: '100%',
                  padding: '12px 12px 12px 40px',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  fontSize: '15px',
                  backgroundColor: 'var(--color-bg-primary)',
                  color: 'var(--color-text-primary)',
                }}
              />
            </div>
          </div>
          <div style={{ width: '150px' }}>
            <Select
              label="Severity"
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value as AlertSeverity | '');
                setCurrentPage(0);
              }}
              options={[
                { value: '', label: 'All' },
                { value: AlertSeverity.HIGH, label: 'High' },
                { value: AlertSeverity.MEDIUM, label: 'Medium' },
                { value: AlertSeverity.LOW, label: 'Low' },
              ]}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ width: '150px' }}>
            <Select
              label="Status"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as AlertStatus | '');
                setCurrentPage(0);
              }}
              options={[
                { value: '', label: 'All' },
                { value: AlertStatus.UNREAD, label: 'Unread' },
                { value: AlertStatus.READ, label: 'Read' },
              ]}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <Button
            variant="secondary"
            onClick={() => {
              setSearchQuery('');
              setSeverityFilter('');
              setStatusFilter('');
              setCurrentPage(0);
              fetchAlerts();
            }}
          >
            Reset
          </Button>
        </div>
      </Card>

      {/* Bulk Actions Bar */}
      {selectedAlertIds.size > 0 && (
        <Card style={{ marginBottom: '20px', backgroundColor: 'var(--color-bg-tertiary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>
              {selectedAlertIds.size} alert(s) selected
            </span>
            <div style={{ display: 'flex', gap: '10px' }}>
              <Button size="small" onClick={handleBulkMarkAsRead}>
                Mark as Read
              </Button>
              <Button size="small" variant="secondary" onClick={() => setSelectedAlertIds(new Set())}>
                Clear Selection
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Alerts List */}
      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>Loading alerts...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>{error}</div>
        ) : filteredAlerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            No alerts found. System is running smoothly!
          </div>
        ) : (
          <>
            {/* Select All Header */}
            <div
              style={{
                padding: '12px 20px',
                borderBottom: `2px solid var(--color-border)`,
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                backgroundColor: 'var(--color-bg-secondary)',
              }}
            >
              <input
                type="checkbox"
                checked={selectedAlertIds.size === filteredAlerts.length && filteredAlerts.length > 0}
                onChange={handleSelectAll}
                style={{ cursor: 'pointer', width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--color-text-secondary)' }}>Select All</span>
            </div>

            {/* Alerts */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1px' }}>
              {filteredAlerts.map((alert) => {
                const severityStyle = getSeverityColor(alert.severity);
                const isUnread = alert.status === AlertStatus.UNREAD;
                const isExpanded = expandedAlertIds.has(alert.id);

                return (
                  <div
                    key={alert.id}
                    style={{
                      padding: '15px 20px',
                      borderBottom: `1px solid var(--color-border)`,
                      backgroundColor: isUnread ? 'var(--color-bg-secondary)' : 'var(--color-bg-primary)',
                      opacity: isUnread ? 1 : 0.85,
                    }}
                  >
                    <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
                      {/* Checkbox */}
                      <input
                        type="checkbox"
                        checked={selectedAlertIds.has(alert.id)}
                        onChange={(e) => {
                          const newSelected = new Set(selectedAlertIds);
                          if (e.target.checked) {
                            newSelected.add(alert.id);
                          } else {
                            newSelected.delete(alert.id);
                          }
                          setSelectedAlertIds(newSelected);
                        }}
                        style={{ marginTop: '3px', cursor: 'pointer', width: '16px', height: '16px' }}
                      />

                      {/* Content */}
                      <div style={{ flex: 1 }}>
                        {/* Header Row */}
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                            marginBottom: '8px',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
                            {/* Unread Indicator */}
                            {isUnread && (
                              <div
                                style={{
                                  width: '8px',
                                  height: '8px',
                                  borderRadius: '50%',
                                  backgroundColor: 'var(--color-brand)',
                                }}
                              />
                            )}

                            {/* Severity Badge */}
                            <span
                              style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px',
                                fontWeight: '500',
                                backgroundColor: severityStyle.bg,
                                color: severityStyle.color,
                              }}
                            >
                              {severityStyle.icon} {severityStyle.label}
                            </span>

                            {/* Title */}
                            <span
                              style={{
                                fontWeight: isUnread ? 'bold' : '500',
                                fontSize: '15px',
                                cursor: 'pointer',
                                color: isUnread ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                              }}
                              onClick={() => toggleExpand(alert.id)}
                            >
                              {alert.title}
                            </span>

                            {/* Expand/Collapse Icon */}
                            <button
                              onClick={() => toggleExpand(alert.id)}
                              style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '12px',
                                color: 'var(--color-text-secondary)',
                              }}
                            >
                              {isExpanded ? '�' : '�'}
                            </button>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            {/* Timestamp */}
                            <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)', whiteSpace: 'nowrap' }}>
                              {format(new Date(alert.created_at), 'MMM dd, HH:mm')}
                            </span>

                            {/* Mark as Read Button */}
                            {isUnread && (
                              <Button size="small" variant="success" onClick={() => handleMarkAsRead(alert.id)}>
                                Mark Read
                              </Button>
                            )}
                          </div>
                        </div>

                        {/* Message Preview */}
                        {!isExpanded && (
                          <div
                            style={{
                              fontSize: '14px',
                              color: 'var(--color-text-secondary)',
                              marginLeft: isUnread ? '18px' : '0',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {alert.message}
                          </div>
                        )}

                        {/* Expanded Details */}
                        {isExpanded && (
                          <div
                            style={{
                              marginTop: '10px',
                              marginLeft: isUnread ? '18px' : '0',
                              padding: '15px',
                              backgroundColor: 'var(--color-bg-secondary)',
                              borderRadius: '6px',
                              fontSize: '14px',
                            }}
                          >
                            <div style={{ marginBottom: '10px', lineHeight: '1.6', color: 'var(--color-text-primary)' }}>{alert.message}</div>

                            {/* Metadata */}
                            <div
                              style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                                gap: '10px',
                                marginTop: '15px',
                                paddingTop: '15px',
                                borderTop: `1px solid var(--color-border)`,
                              }}
                            >
                              <div>
                                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Type: </span>
                                <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{alert.alert_type}</span>
                              </div>
                              {alert.serial_number && (
                                <div>
                                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Serial: </span>
                                  <span style={{
                                    fontSize: '14px',
                                    fontWeight: '500',
                                    fontFamily: 'var(--font-mono)',
                                    color: 'var(--color-text-primary)'
                                  }}>
                                    {formatSerialNumber(alert.serial_number)}
                                  </span>
                                </div>
                              )}
                              {alert.lot_number && (
                                <div>
                                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>LOT: </span>
                                  <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{alert.lot_number}</span>
                                </div>
                              )}
                              {alert.process_name && (
                                <div>
                                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Process: </span>
                                  <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--color-text-primary)' }}>{alert.process_name}</span>
                                </div>
                              )}
                              {alert.read_at && (
                                <div>
                                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Read at: </span>
                                  <span style={{ fontSize: '13px', color: 'var(--color-text-primary)' }}>
                                    {format(new Date(alert.read_at), 'yyyy-MM-dd HH:mm:ss')}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div
                style={{
                  marginTop: '20px',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 0}
                >
                  Previous
                </Button>
                <span style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                  {currentPage + 1} / {totalPages}
                </span>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage >= totalPages - 1}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
};
