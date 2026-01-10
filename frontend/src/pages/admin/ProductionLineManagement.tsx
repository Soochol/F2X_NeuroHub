/**
 * Production Line Management Component
 *
 * Handles CRUD operations for production lines including:
 * - Line creation with code and name
 * - Cycle time configuration
 * - Location assignment
 * - Active/Inactive status management
 */

import { productionLinesApi } from '@/api';
import { Button, Card, Input, Modal, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { ProductionLine } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';

import {
  defaultProductionLineFormData,
  getRowStyle,
  styles,
  type ProductionLineFormData,
} from './shared';

export const ProductionLineManagement = () => {
  const { message } = App.useApp();
  const { data: productionLines, isLoading, error, refetch } = useAsyncData<ProductionLine[]>({
    fetchFn: () => productionLinesApi.getProductionLines(),
    initialData: [],
    errorMessage: 'Failed to load production lines',
  });
  const modal = useModalState<ProductionLine>();
  const form = useFormState<ProductionLineFormData>(defaultProductionLineFormData);

  const handleOpenModal = (productionLine?: ProductionLine) => {
    if (productionLine) {
      form.setFormData({
        line_code: productionLine.line_code,
        line_name: productionLine.line_name,
        description: productionLine.description || '',
        cycle_time_sec: productionLine.cycle_time_sec ?? '',
        location: productionLine.location || '',
        is_active: productionLine.is_active,
      });
    } else {
      form.resetForm();
    }
    modal.open(productionLine);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        line_code: form.formData.line_code,
        line_name: form.formData.line_name,
        description: form.formData.description || undefined,
        cycle_time_sec: form.formData.cycle_time_sec || undefined,
        location: form.formData.location || undefined,
        is_active: form.formData.is_active,
      };
      modal.editingItem
        ? await productionLinesApi.updateProductionLine(modal.editingItem.id, submitData)
        : await productionLinesApi.createProductionLine(submitData);
      modal.close();
      refetch();
      message.success('Production line saved successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save production line');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (productionLineId: number) => {
    if (!confirm('Are you sure you want to delete this production line?')) return;
    try {
      await productionLinesApi.deleteProductionLine(productionLineId);
      refetch();
      message.success('Production line deleted successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to delete production line');
      message.error(errorMsg, 5);
    }
  };

  return (
    <>
      <div style={styles.header}>
        <div style={styles.title}>Total Production Lines: {productionLines?.length || 0}</div>
        <Button onClick={() => handleOpenModal()}>+ Add Production Line</Button>
      </div>
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading production lines...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Code</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Cycle Time (sec)</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Location</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {productionLines?.map((line, idx) => (
                  <tr key={line.id} style={getRowStyle(idx)}>
                    <td style={{ ...styles.td, fontWeight: '600' }}>{line.line_code}</td>
                    <td style={{ ...styles.td, fontWeight: '500' }}>{line.line_name}</td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      {line.cycle_time_sec ?? '-'}
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        color: 'var(--color-text-secondary)',
                        fontSize: '13px',
                      }}
                    >
                      {line.location || '-'}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={line.is_active} />
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button size="sm" variant="secondary" onClick={() => handleOpenModal(line)}>
                          Edit
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(line.id)}>
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal
        isOpen={modal.isOpen}
        onClose={modal.close}
        title={modal.editingItem ? 'Edit Production Line' : 'Add New Production Line'}
        footer={
          <div style={styles.modalFooter}>
            <Button variant="secondary" onClick={modal.close}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Save</Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit}>
          <Input
            label="Line Code"
            value={form.formData.line_code}
            onChange={(e) => form.setField('line_code', e.target.value)}
            required
            disabled={!!modal.editingItem}
            placeholder="e.g., LINEA, LINE01, KR001"
          />
          {/* Line Code Validation Rules */}
          <div style={{
            marginTop: '-12px',
            marginBottom: '15px',
            padding: '12px 15px',
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: '6px',
            border: '1px solid var(--color-border)',
            fontSize: '13px'
          }}>
            <div style={{ fontWeight: '600', marginBottom: '6px', color: 'var(--color-text-primary)' }}>
              ✓ Allowed:
            </div>
            <ul style={{ margin: '0 0 8px 0', paddingLeft: '20px', color: 'var(--color-text-secondary)' }}>
              <li>Letters (A-Z), Numbers (0-9)</li>
              <li>Alphanumeric characters only (no hyphens or underscores)</li>
              <li>Automatically converted to UPPERCASE</li>
            </ul>
            <div style={{ fontWeight: '600', marginBottom: '6px', color: 'var(--color-error)' }}>
              ✗ Not Allowed:
            </div>
            <ul style={{ margin: '0', paddingLeft: '20px', color: 'var(--color-text-secondary)' }}>
              <li>Hyphens (-), Underscores (_), Spaces, or special characters</li>
            </ul>
          </div>
          <Input
            label="Line Name"
            value={form.formData.line_name}
            onChange={(e) => form.setField('line_name', e.target.value)}
            required
            placeholder="e.g., Assembly Line A"
          />
          <Input
            label="Cycle Time (sec)"
            type="number"
            value={form.formData.cycle_time_sec}
            onChange={(e) =>
              form.setField('cycle_time_sec', e.target.value ? parseInt(e.target.value) : '')
            }
            placeholder="Optional"
          />
          <Input
            label="Location"
            value={form.formData.location}
            onChange={(e) => form.setField('location', e.target.value)}
            placeholder="e.g., Building 1, Zone A"
          />
          <Input
            label="Description"
            value={form.formData.description}
            onChange={(e) => form.setField('description', e.target.value)}
          />
          <div style={styles.checkbox}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={form.formData.is_active}
                onChange={(e) => form.setField('is_active', e.target.checked)}
                style={styles.checkboxInput}
              />
              <span style={styles.checkboxText}>Active</span>
            </label>
          </div>
        </form>
      </Modal>
    </>
  );
};
