/**
 * Equipment Management Component
 *
 * Handles CRUD operations for equipment including:
 * - Equipment registration with codes and details
 * - Process and production line assignment
 * - Status management (Available, In Use, Maintenance, etc.)
 * - Manufacturer and serial number tracking
 */

import { equipmentApi, processesApi, productionLinesApi } from '@/api';
import { Button, Card, Input, Modal, Select, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { Equipment, Process, ProductionLine } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';

import { defaultEquipmentFormData, getRowStyle, styles, type EquipmentFormData } from './shared';

export const EquipmentManagement = () => {
  const { message } = App.useApp();
  const { data: equipment, isLoading, error, refetch } = useAsyncData<Equipment[]>({
    fetchFn: () => equipmentApi.getEquipment(),
    initialData: [],
    errorMessage: 'Failed to load equipment',
  });
  const { data: processes } = useAsyncData<Process[]>({
    fetchFn: () => processesApi.getProcesses(),
    initialData: [],
    errorMessage: 'Failed to load processes',
  });
  const { data: productionLines } = useAsyncData<ProductionLine[]>({
    fetchFn: () => productionLinesApi.getProductionLines(),
    initialData: [],
    errorMessage: 'Failed to load production lines',
  });
  const modal = useModalState<Equipment>();
  const form = useFormState<EquipmentFormData>(defaultEquipmentFormData);

  const handleOpenModal = (equip?: Equipment) => {
    if (equip) {
      form.setFormData({
        equipment_code: equip.equipment_code,
        equipment_name: equip.equipment_name,
        equipment_type: equip.equipment_type,
        description: equip.description || '',
        process_id: equip.process_id || '',
        production_line_id: equip.production_line_id || '',
        manufacturer: equip.manufacturer || '',
        model_number: equip.model_number || '',
        serial_number: equip.serial_number || '',
        status: equip.status || 'AVAILABLE',
        is_active: equip.is_active,
      });
    } else {
      form.resetForm();
    }
    modal.open(equip);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        equipment_code: form.formData.equipment_code,
        equipment_name: form.formData.equipment_name,
        equipment_type: form.formData.equipment_type,
        description: form.formData.description || undefined,
        process_id: form.formData.process_id || undefined,
        production_line_id: form.formData.production_line_id || undefined,
        manufacturer: form.formData.manufacturer || undefined,
        model_number: form.formData.model_number || undefined,
        serial_number: form.formData.serial_number || undefined,
        status: form.formData.status,
        is_active: form.formData.is_active,
      };
      modal.editingItem
        ? await equipmentApi.updateEquipment(modal.editingItem.id, submitData)
        : await equipmentApi.createEquipment(submitData);
      modal.close();
      refetch();
      message.success('Equipment saved successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save equipment');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (equipmentId: number) => {
    if (!confirm('Are you sure you want to delete this equipment?')) return;
    try {
      await equipmentApi.deleteEquipment(equipmentId);
      refetch();
      message.success('Equipment deleted successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to delete equipment');
      message.error(errorMsg, 5);
    }
  };

  const getLineName = (lineId?: number) =>
    productionLines?.find((l) => l.id === lineId)?.line_name || '-';

  return (
    <>
      <div style={styles.header}>
        <div style={styles.title}>Total Equipment: {equipment?.length || 0}</div>
        <Button onClick={() => handleOpenModal()}>+ Add Equipment</Button>
      </div>
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading equipment...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Code</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Type</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Line</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {equipment?.map((equip, idx) => (
                  <tr key={equip.id} style={getRowStyle(idx)}>
                    <td style={{ ...styles.td, fontWeight: '600' }}>{equip.equipment_code}</td>
                    <td style={{ ...styles.td, fontWeight: '500' }}>{equip.equipment_name}</td>
                    <td style={{ ...styles.td, fontSize: '13px' }}>{equip.equipment_type}</td>
                    <td
                      style={{
                        ...styles.td,
                        color: 'var(--color-text-secondary)',
                        fontSize: '13px',
                      }}
                    >
                      {getLineName(equip.production_line_id)}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={equip.is_active} />
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleOpenModal(equip)}
                        >
                          Edit
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(equip.id)}>
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
        title={modal.editingItem ? 'Edit Equipment' : 'Add New Equipment'}
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
            label="Equipment Code"
            value={form.formData.equipment_code}
            onChange={(e) => form.setField('equipment_code', e.target.value)}
            required
            disabled={!!modal.editingItem}
            placeholder="e.g., EQ_LASER_001"
          />
          <Input
            label="Equipment Name"
            value={form.formData.equipment_name}
            onChange={(e) => form.setField('equipment_name', e.target.value)}
            required
            placeholder="e.g., Laser Marker 001"
          />
          <Input
            label="Equipment Type"
            value={form.formData.equipment_type}
            onChange={(e) => form.setField('equipment_type', e.target.value)}
            required
            placeholder="e.g., LASER_MARKER"
          />
          <Input
            label="Description"
            value={form.formData.description}
            onChange={(e) => form.setField('description', e.target.value)}
            placeholder="Equipment description"
          />
          <Select
            label="Production Line"
            value={form.formData.production_line_id}
            onChange={(e) =>
              form.setField('production_line_id', e.target.value ? parseInt(e.target.value) : '')
            }
            options={productionLines?.map((l) => ({ value: String(l.id), label: l.line_name })) || []}
          />
          <Select
            label="Process"
            value={form.formData.process_id}
            onChange={(e) =>
              form.setField('process_id', e.target.value ? parseInt(e.target.value) : '')
            }
            options={processes?.map((p) => ({ value: String(p.id), label: p.process_name_en })) || []}
          />
          <Input
            label="Manufacturer"
            value={form.formData.manufacturer}
            onChange={(e) => form.setField('manufacturer', e.target.value)}
            placeholder="e.g., KEYENCE"
          />
          <Input
            label="Model Number"
            value={form.formData.model_number}
            onChange={(e) => form.setField('model_number', e.target.value)}
            placeholder="e.g., MD-X1000"
          />
          <Input
            label="Serial Number"
            value={form.formData.serial_number}
            onChange={(e) => form.setField('serial_number', e.target.value)}
            placeholder="Equipment S/N (e.g., LASER01-2024-001)"
          />
          <Select
            label="Status"
            value={form.formData.status}
            onChange={(e) => form.setField('status', e.target.value)}
            options={[
              { value: 'AVAILABLE', label: 'Available' },
              { value: 'IN_USE', label: 'In Use' },
              { value: 'MAINTENANCE', label: 'Maintenance' },
              { value: 'OUT_OF_SERVICE', label: 'Out of Service' },
              { value: 'RETIRED', label: 'Retired' },
            ]}
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
