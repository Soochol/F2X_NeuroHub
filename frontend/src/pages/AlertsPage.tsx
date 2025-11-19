/**
 * Alerts Page
 */

import { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { alertsApi } from '@/api';
import { AlertSeverity, AlertStatus, type Alert } from '@/types/api';
import { format } from 'date-fns';

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
        return { bg: '#fee', color: '#c33', icon: '🚨', label: 'High' };
      case AlertSeverity.MEDIUM:
        return { bg: '#fff3cd', color: '#e67e22', icon: '⚠️', label: 'Medium' };
      case AlertSeverity.LOW:
        return { bg: '#e3f2fd', color: '#3498db', icon: 'ℹ️', label: 'Low' };
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
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>System Alerts & Notifications</h1>
        {unreadCount > 0 && (
          <span
            style={{
              padding: '6px 12px',
              backgroundColor: '#e74c3c',
              color: 'white',
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
            <Input
              label="Search"
              placeholder="Search by title, serial, or lot number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
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
        <Card style={{ marginBottom: '20px', backgroundColor: '#e3f2fd' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', fontWeight: '500' }}>
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
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading alerts...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
        ) : filteredAlerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
            No alerts found. System is running smoothly! 🎉
          </div>
        ) : (
          <>
            {/* Select All Header */}
            <div
              style={{
                padding: '12px 20px',
                borderBottom: '2px solid #e0e0e0',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                backgroundColor: '#f8f9fa',
              }}
            >
              <input
                type="checkbox"
                checked={selectedAlertIds.size === filteredAlerts.length && filteredAlerts.length > 0}
                onChange={handleSelectAll}
                style={{ cursor: 'pointer', width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#7f8c8d' }}>Select All</span>
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
                      borderBottom: '1px solid #f0f0f0',
                      backgroundColor: isUnread ? '#f9f9f9' : 'white',
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
                                  backgroundColor: '#3498db',
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
                                color: isUnread ? '#2c3e50' : '#7f8c8d',
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
                                color: '#7f8c8d',
                              }}
                            >
                              {isExpanded ? '▼' : '▶'}
                            </button>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            {/* Timestamp */}
                            <span style={{ fontSize: '13px', color: '#7f8c8d', whiteSpace: 'nowrap' }}>
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
                              color: '#7f8c8d',
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
                              backgroundColor: '#f8f9fa',
                              borderRadius: '6px',
                              fontSize: '14px',
                            }}
                          >
                            <div style={{ marginBottom: '10px', lineHeight: '1.6' }}>{alert.message}</div>

                            {/* Metadata */}
                            <div
                              style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                                gap: '10px',
                                marginTop: '15px',
                                paddingTop: '15px',
                                borderTop: '1px solid #e0e0e0',
                              }}
                            >
                              <div>
                                <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Type: </span>
                                <span style={{ fontSize: '13px', fontWeight: '500' }}>{alert.alert_type}</span>
                              </div>
                              {alert.serial_number && (
                                <div>
                                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Serial: </span>
                                  <span style={{ fontSize: '13px', fontWeight: '500' }}>{alert.serial_number}</span>
                                </div>
                              )}
                              {alert.lot_number && (
                                <div>
                                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>LOT: </span>
                                  <span style={{ fontSize: '13px', fontWeight: '500' }}>{alert.lot_number}</span>
                                </div>
                              )}
                              {alert.process_name && (
                                <div>
                                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Process: </span>
                                  <span style={{ fontSize: '13px', fontWeight: '500' }}>{alert.process_name}</span>
                                </div>
                              )}
                              {alert.read_at && (
                                <div>
                                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Read at: </span>
                                  <span style={{ fontSize: '13px' }}>
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
                <span style={{ fontSize: '14px', color: '#7f8c8d' }}>
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
