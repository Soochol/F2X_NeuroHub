// LOT Creation Modal Component

import { useState, useMemo, type FormEvent } from 'react';
import { Input, Select, Button } from '../../atoms';
import { Modal } from '../../molecules';
import { lotsApi } from '@/api';
import { type LotCreate, type ProductModel, type ProductionLine, getErrorMessage } from '@/types/api';

interface LotCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  productModels: ProductModel[];
  productionLines: ProductionLine[];
}

export const LotCreateModal = ({ isOpen, onClose, onSuccess, productModels, productionLines }: LotCreateModalProps) => {
  const [formData, setFormData] = useState<LotCreate>({
    product_model_id: 0,
    production_line_id: 0,
    target_quantity: 100,
    production_date: new Date().toISOString().split('T')[0],
    sma_spring_lot: '',
    parent_spring_lot: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // LOT number preview calculation
  const previewLotNumber = useMemo(() => {
    const model = productModels.find(pm => pm.id === formData.product_model_id);
    const line = productionLines.find(pl => pl.id === formData.production_line_id);
    if (!model || !line) {
      return 'Select model and production line';
    }
    const modelPrefix = model.model_code.split('-')[0];
    const lineCode = line.line_code;
    const dateStr = formData.production_date.replace(/-/g, '').substring(2);
    return `${modelPrefix}-${lineCode}-${dateStr}-xxx`;
  }, [formData.product_model_id, formData.production_line_id, formData.production_date, productModels, productionLines]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsSubmitting(true);
    try {
      const newErrors: Record<string, string> = {};
      if (!formData.product_model_id) newErrors.product_model_id = 'Please select a product model';
      if (!formData.production_line_id) newErrors.production_line_id = 'Please select a production line';
      if (formData.target_quantity < 1 || formData.target_quantity > 100) newErrors.target_quantity = 'Target quantity must be between 1-100';
      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return;
      }
      await lotsApi.createLot(formData);
      onSuccess();
      onClose();
      // Reset form
      setFormData({
        product_model_id: 0,
        production_line_id: 0,
        target_quantity: 100,
        production_date: new Date().toISOString().split('T')[0],
        sma_spring_lot: '',
        parent_spring_lot: '',
      });
    } catch (error: unknown) {
      setErrors({ submit: getErrorMessage(error, 'Failed to create LOT') });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New LOT"
      width="700px"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create LOT'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        {/* LOT Number Preview */}
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: formData.product_model_id && formData.production_line_id ? 'var(--color-brand)' : 'var(--color-text-tertiary)' }}>
            {previewLotNumber}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-tertiary)', marginTop: '5px' }}>
            * Sequence number (xxx) will be auto-generated
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <Select
            label="Product Model"
            value={formData.product_model_id === 0 ? '' : formData.product_model_id.toString()}
            onChange={e => setFormData({ ...formData, product_model_id: e.target.value ? parseInt(e.target.value) : 0 })}
            options={productModels.map(pm => ({ value: pm.id.toString(), label: `${pm.model_code} - ${pm.model_name}` }))}
            required
            error={errors.product_model_id}
          />

          <Select
            label="Production Line"
            value={formData.production_line_id === 0 ? '' : formData.production_line_id.toString()}
            onChange={e => setFormData({ ...formData, production_line_id: e.target.value ? parseInt(e.target.value) : 0 })}
            options={productionLines.map(pl => ({ value: pl.id.toString(), label: `${pl.line_code} - ${pl.line_name}` }))}
            required
            error={errors.production_line_id}
          />

          <Input
            label="Target Quantity"
            type="number"
            value={formData.target_quantity}
            onChange={e => setFormData({ ...formData, target_quantity: parseInt(e.target.value) })}
            min={1}
            max={100}
            required
            error={errors.target_quantity}
          />

          <Input
            label="Production Date"
            type="date"
            value={formData.production_date}
            onChange={e => setFormData({ ...formData, production_date: e.target.value })}
            required
          />

          <Input
            label="SMA Spring Lot"
            value={formData.sma_spring_lot || ''}
            onChange={e => setFormData({ ...formData, sma_spring_lot: e.target.value })}
            placeholder="Optional"
          />

          <Input
            label="Mother Lot"
            value={formData.parent_spring_lot || ''}
            onChange={e => setFormData({ ...formData, parent_spring_lot: e.target.value })}
            placeholder="Optional"
          />
        </div>

        {errors.submit && (
          <div style={{ marginTop: '15px', padding: '10px', backgroundColor: 'var(--color-error-bg)', color: 'var(--color-error)', borderRadius: '4px', fontSize: '14px' }}>
            {errors.submit}
          </div>
        )}
      </form>
    </Modal>
  );
};
