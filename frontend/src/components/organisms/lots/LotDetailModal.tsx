/**
 * LOT Detail Modal Component
 */

import { useState, useEffect } from 'react';
import { Button, Select } from '@/components/atoms';
import { Modal } from '@/components/molecules';
import { lotsApi } from '@/api';
import { LotStatus, UserRole, type Lot, type LotUpdate, getErrorMessage } from '@/types/api';
import { useAuth } from '@/contexts/AuthContext';
import { format } from 'date-fns';

interface LotDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  lotId: number;
  onUpdate: () => void;
}

export const LotDetailModal = ({ isOpen, onClose, lotId, onUpdate }: LotDetailModalProps) => {
  const { user } = useAuth();
  const canEdit = user?.role === UserRole.ADMIN || user?.role === UserRole.MANAGER;

  const [lot, setLot] = useState<Lot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<LotUpdate>({});
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && lotId) {
      fetchLot();
    }
  }, [isOpen, lotId]);

  const fetchLot = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await lotsApi.getLot(lotId);
      setLot(data);
      setEditData({
        status: data.status,
      });
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load LOT information'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await lotsApi.updateLot(lotId, editData);
      setIsEditing(false);
      await fetchLot();
      onUpdate();
      onClose(); // 저장 완료 후 모달 닫기
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to update LOT'));
    }
  };

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="LOT Details">
        <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
      </Modal>
    );
  }

  if (error && !lot) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="LOT Details">
        <div style={{ color: 'var(--color-error)', padding: '20px' }}>{error}</div>
      </Modal>
    );
  }

  if (!lot) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`LOT Details: ${lot.lot_number}`}
      width="800px"
      footer={
        <>
          {isEditing ? (
            <>
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleUpdate}>Save</Button>
            </>
          ) : (
            <>
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
              {canEdit && <Button onClick={() => setIsEditing(true)}>Edit</Button>}
            </>
          )}
        </>
      }
    >
      <div>
        {/* Basic Info */}
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '15px' }}>Basic Information</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>LOT Number</div>
              <div style={{ fontWeight: 'bold' }}>{lot.lot_number}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Product Model</div>
              <div style={{ fontWeight: 'bold' }}>
                {lot.product_model ? `${lot.product_model.model_code} - ${lot.product_model.model_name}` : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Target Quantity</div>
              <div style={{ fontWeight: 'bold' }}>{lot.target_quantity}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Production Date</div>
              <div style={{ fontWeight: 'bold' }}>
                {format(new Date(lot.production_date), 'yyyy-MM-dd')}
              </div>
            </div>
            <div>
              {isEditing ? (
                <Select
                  label="Status"
                  value={editData.status || lot.status}
                  onChange={(e) => setEditData({ ...editData, status: e.target.value as LotStatus })}
                  options={[
                    { value: LotStatus.CREATED, label: 'Created' },
                    { value: LotStatus.IN_PROGRESS, label: 'In Progress' },
                    { value: LotStatus.COMPLETED, label: 'Completed' },
                    { value: LotStatus.CLOSED, label: 'Closed' },
                  ]}
                />
              ) : (
                <>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Status</div>
                  <div>
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
                              : 'var(--color-bg-tertiary)',
                        color:
                          lot.status === LotStatus.COMPLETED
                            ? 'var(--color-success)'
                            : lot.status === LotStatus.IN_PROGRESS
                              ? 'var(--color-info)'
                              : 'var(--color-text-secondary)',
                      }}
                    >
                      {lot.status}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Timestamps */}
        <div style={{ paddingTop: '20px', borderTop: '1px solid var(--color-border)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '15px' }}>Timestamps</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', fontSize: '13px' }}>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Created At</div>
              <div>{format(new Date(lot.created_at), 'yyyy-MM-dd HH:mm:ss')}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Updated At</div>
              <div>{format(new Date(lot.updated_at), 'yyyy-MM-dd HH:mm:ss')}</div>
            </div>
            {lot.completed_at && (
              <div>
                <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Completed At</div>
                <div>{format(new Date(lot.completed_at), 'yyyy-MM-dd HH:mm:ss')}</div>
              </div>
            )}
            {lot.closed_at && (
              <div>
                <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Closed At</div>
                <div>{format(new Date(lot.closed_at), 'yyyy-MM-dd HH:mm:ss')}</div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div
            style={{
              marginTop: '15px',
              padding: '10px',
              backgroundColor: 'var(--color-error-bg)',
              color: 'var(--color-error)',
              borderRadius: '4px',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
};
