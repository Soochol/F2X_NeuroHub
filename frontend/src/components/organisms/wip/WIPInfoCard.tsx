/**
 * WIP Info Card Component
 *
 * Displays serial/WIP information including:
 * - Serial number and status
 * - LOT information
 * - Current process progress
 * - Rework count
 */

import { Card } from '@/components/common';
import { formatSerialNumberV1 } from '@/utils/serialNumber';
import { format } from 'date-fns';
import type { Serial } from '@/types/api';

interface WIPInfoCardProps {
  serial: Serial;
}

const statusColors: Record<string, { bg: string; text: string }> = {
  CREATED: {
    bg: 'var(--color-gray-200)',
    text: 'var(--color-gray-700)',
  },
  IN_PROGRESS: {
    bg: 'var(--color-info-bg, rgba(52, 152, 219, 0.15))',
    text: 'var(--color-info, var(--color-brand))',
  },
  PASSED: {
    bg: 'var(--color-success-bg, rgba(39, 174, 96, 0.15))',
    text: 'var(--color-success)',
  },
  FAILED: {
    bg: 'var(--color-error-bg, rgba(245, 101, 101, 0.15))',
    text: 'var(--color-error)',
  },
};

export const WIPInfoCard: React.FC<WIPInfoCardProps> = ({ serial }) => {
  const statusStyle = statusColors[serial.status] || statusColors.CREATED;

  return (
    <Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)' }}>
        {/* Header: Serial Number */}
        <div
          style={{
            paddingBottom: 'var(--spacing-3)',
            borderBottom: '1px solid var(--color-border-default)',
          }}
        >
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-1)' }}>
            Serial Number
          </div>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '20px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              letterSpacing: '0.5px',
            }}
          >
            {formatSerialNumberV1(serial.serial_number)}
          </div>
        </div>

        {/* Status Badge */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>Status</span>
          <span
            style={{
              padding: '4px 12px',
              borderRadius: 'var(--radius-base)',
              fontSize: '13px',
              fontWeight: '500',
              backgroundColor: statusStyle.bg,
              color: statusStyle.text,
            }}
          >
            {serial.status}
          </span>
        </div>

        {/* LOT Information */}
        {serial.lot && (
          <div
            style={{
              padding: 'var(--spacing-3)',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: 'var(--radius-base)',
              border: '1px solid var(--color-border-subtle)',
            }}
          >
            <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: 'var(--spacing-2)' }}>LOT Information</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>LOT Number</span>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  {serial.lot.lot_number}
                </span>
              </div>
              {serial.lot.product_model && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                  <span style={{ color: 'var(--color-text-secondary)' }}>Product Model</span>
                  <span style={{ color: 'var(--color-text-primary)' }}>{serial.lot.product_model.model_name}</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Production Date</span>
                <span style={{ color: 'var(--color-text-primary)' }}>
                  {format(new Date(serial.lot.production_date), 'yyyy-MM-dd')}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Shift</span>
                <span style={{ color: 'var(--color-text-primary)' }}>{serial.lot.shift}</span>
              </div>
            </div>
          </div>
        )}

        {/* Rework Information */}
        {serial.rework_count > 0 && (
          <div
            style={{
              padding: 'var(--spacing-3)',
              backgroundColor: 'var(--color-warning-bg, rgba(243, 156, 18, 0.1))',
              borderRadius: 'var(--radius-base)',
              border: '1px solid var(--color-warning)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ flexShrink: 0 }}
              >
                <path
                  d="M8 1.5L1.5 14.5H14.5L8 1.5Z"
                  stroke="var(--color-warning)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M8 6V9"
                  stroke="var(--color-warning)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
                <circle cx="8" cy="11.5" r="0.5" fill="var(--color-warning)" />
              </svg>
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-warning)' }}>
                  Rework Count: {serial.rework_count}/3
                </div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                  This serial has been reworked {serial.rework_count} time{serial.rework_count > 1 ? 's' : ''}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div
          style={{
            paddingTop: 'var(--spacing-3)',
            borderTop: '1px solid var(--color-border-default)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-1)',
            fontSize: '12px',
            color: 'var(--color-text-secondary)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Created</span>
            <span>{format(new Date(serial.created_at), 'yyyy-MM-dd HH:mm')}</span>
          </div>
          {serial.completed_at && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Completed</span>
              <span>{format(new Date(serial.completed_at), 'yyyy-MM-dd HH:mm')}</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};
