/**
 * LOT Creation Modal Component
 */

import { useState, type FormEvent } from 'react';
import { Input, Select, Button } from '../../atoms';
import { Modal } from '../../molecules';
import { lotsApi } from '@/api';
import { Shift, type LotCreate, type ProductModel, getErrorMessage } from '@/types/api';

interface LotCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  productModels: ProductModel[];
}

export const LotCreateModal = ({ isOpen, onClose, onSuccess, productModels }: LotCreateModalProps) => {
  const [formData, setFormData] = useState<LotCreate>({
    lot_number: '',
    product_model_id: 0,
    target_quantity: 100,
    production_date: new Date().toISOString().split('T')[0],
    shift: Shift.DAY,
    busbar_lot: '',
    sma_spring_lot: '',
    pin_lot: '',
    hsg_lot: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsSubmitting(true);

    try {
      // Validation
      const newErrors: Record<string, string> = {};

      if (!formData.lot_number) {
        newErrors.lot_number = 'LOT 번호를 입력하세요';
      }
      if (!formData.product_model_id) {
        newErrors.product_model_id = '제품 모델을 선택하세요';
      }
      if (formData.target_quantity < 1 || formData.target_quantity > 100) {
        newErrors.target_quantity = '목표 수량은 1-100 사이여야 합니다';
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        setIsSubmitting(false);
        return;
      }

      await lotsApi.createLot(formData);
      onSuccess();
      onClose();

      // Reset form
      setFormData({
        lot_number: '',
        product_model_id: 0,
        target_quantity: 100,
        production_date: new Date().toISOString().split('T')[0],
        shift: Shift.DAY,
        busbar_lot: '',
        sma_spring_lot: '',
        pin_lot: '',
        hsg_lot: '',
      });
    } catch (error: unknown) {
      setErrors({ submit: getErrorMessage(error, 'LOT 생성 실패') });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="새 LOT 생성"
      width="700px"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            취소
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? '생성 중...' : 'LOT 생성'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <Input
            label="LOT 번호"
            value={formData.lot_number}
            onChange={(e) => setFormData({ ...formData, lot_number: e.target.value })}
            placeholder="WF-KR-YYMMDDX-nnn"
            required
            error={errors.lot_number}
          />

          <Select
            label="제품 모델"
            value={formData.product_model_id.toString()}
            onChange={(e) => setFormData({ ...formData, product_model_id: parseInt(e.target.value) })}
            options={productModels.map((pm) => ({
              value: pm.id.toString(),
              label: `${pm.model_code} - ${pm.model_name}`,
            }))}
            required
            error={errors.product_model_id}
          />

          <Input
            label="목표 수량"
            type="number"
            value={formData.target_quantity}
            onChange={(e) => setFormData({ ...formData, target_quantity: parseInt(e.target.value) })}
            min={1}
            max={100}
            required
            error={errors.target_quantity}
          />

          <Input
            label="생산 날짜"
            type="date"
            value={formData.production_date}
            onChange={(e) => setFormData({ ...formData, production_date: e.target.value })}
            required
          />

          <Select
            label="작업 시프트"
            value={formData.shift}
            onChange={(e) => setFormData({ ...formData, shift: e.target.value as Shift })}
            options={[
              { value: Shift.DAY, label: '주간 (Day)' },
              { value: Shift.EVENING, label: '저녁 (Evening)' },
              { value: Shift.NIGHT, label: '야간 (Night)' },
            ]}
            required
          />
        </div>

        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--color-border)' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '15px' }}>
            구성품 LOT 번호 (선택사항)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <Input
              label="Busbar LOT"
              value={formData.busbar_lot || ''}
              onChange={(e) => setFormData({ ...formData, busbar_lot: e.target.value })}
              placeholder="예: BB-20250118-001"
            />

            <Input
              label="SMA Spring LOT"
              value={formData.sma_spring_lot || ''}
              onChange={(e) => setFormData({ ...formData, sma_spring_lot: e.target.value })}
              placeholder="예: SP-20250118-001"
            />

            <Input
              label="Pin LOT"
              value={formData.pin_lot || ''}
              onChange={(e) => setFormData({ ...formData, pin_lot: e.target.value })}
              placeholder="예: PN-20250118-001"
            />

            <Input
              label="Housing LOT"
              value={formData.hsg_lot || ''}
              onChange={(e) => setFormData({ ...formData, hsg_lot: e.target.value })}
              placeholder="예: HS-20250118-001"
            />
          </div>
        </div>

        {errors.submit && (
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
            {errors.submit}
          </div>
        )}
      </form>
    </Modal>
  );
};
