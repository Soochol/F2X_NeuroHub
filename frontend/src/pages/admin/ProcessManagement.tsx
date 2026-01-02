/**
 * Process Management Component
 *
 * Handles CRUD operations for manufacturing processes including:
 * - Process creation with numbering
 * - Defect item management with suggestions
 * - Auto label printing configuration
 * - Quality criteria JSON editing
 */

import { processesApi } from '@/api';
import { Button, Card, Input, Modal, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { Process } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';
import { useState } from 'react';

import { defaultProcessFormData, getRowStyle, styles, type ProcessFormData } from './shared';

// Categorized defect suggestions
const CATEGORIZED_SUGGESTIONS: Record<string, string[]> = {
  Appearance: ['Scratch', 'Dent', 'Contamination', 'Discoloration', 'Burr', 'Crack', 'Housing damage'],
  Assembly: ['Missing Part', 'Loose Screw', 'Alignment Error', 'Gap Issue', 'Poor Fit', 'Incorrect Part'],
  Functional: ['Power Failure', 'Sensor Error', 'Connection Error', 'Noise Issue', 'Signal Weak'],
  'Marking/Label': ['Unreadable QR', 'Blurry Printing', 'Wrong Label', 'Misplaced Label', 'Duplicate Serial'],
  Packaging: ['Box Damage', 'Missing Manual', 'Wrong Quantity', 'Sealing Issue', 'Missing Accessory'],
};

// Legacy mapping for auto-load on new process
const getSuggestedDefects = (processNumber: number): string[] => {
  const legacy: Record<number, string[]> = {
    1: ['Blurry marking', 'Incorrect marking position', 'QR code unreadable'],
    2: ['Housing scratch', 'Foreign object inclusion', 'Assembly gap'],
    3: ['Bent pin', 'Poor press-fit depth', 'Missing pin'],
    4: ['Spring deformation', 'Missing spring', 'Assembly detachment'],
    5: ['Insufficient weld', 'Excessive weld (burr)', 'Weld crack'],
    6: ['Appearance defect', 'Functional test failed', 'Dimension under spec'],
    7: ['Duplicate serial', 'Poor label attachment'],
    8: ['Packaging damage', 'Insufficient quantity', 'Incorrect attachment'],
  };
  return legacy[processNumber] || [];
};

export const ProcessManagement = () => {
  const { message } = App.useApp();
  const { data: processes, isLoading, error, refetch } = useAsyncData<Process[]>({
    fetchFn: async () => (await processesApi.getProcesses()).sort((a, b) => a.sort_order - b.sort_order),
    initialData: [],
    errorMessage: 'Failed to load processes',
  });
  const modal = useModalState<Process>();
  const form = useFormState<ProcessFormData>(defaultProcessFormData);

  const suggestionModal = useModalState<void>();
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([]);

  const toggleSuggestion = (item: string) => {
    setSelectedSuggestions((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  const openSuggestionModal = (e: React.MouseEvent) => {
    e.preventDefault();
    setSelectedSuggestions([]);
    suggestionModal.open();
  };

  const addSelectedSuggestions = () => {
    const combined = Array.from(new Set([...form.formData.defect_items, ...selectedSuggestions]));
    form.setField('defect_items', combined);
    suggestionModal.close();
    if (selectedSuggestions.length > 0) {
      message.success(`${selectedSuggestions.length} suggested items added.`);
    }
  };

  const addDefectItem = (item: string) => {
    if (!item.trim()) return;
    if (form.formData.defect_items.includes(item.trim())) {
      message.warning('Item already exists.');
      return;
    }
    form.setField('defect_items', [...form.formData.defect_items, item.trim()]);
  };

  const removeDefectItem = (index: number) => {
    const newItems = [...form.formData.defect_items];
    newItems.splice(index, 1);
    form.setField('defect_items', newItems);
  };

  const handleOpenModal = (process?: Process) => {
    if (process) {
      form.setFormData({
        process_number: process.process_number,
        process_code: process.process_code,
        process_name_ko: process.process_name_ko,
        process_name_en: process.process_name_en,
        description: process.description || '',
        sort_order: process.sort_order,
        is_active: process.is_active,
        estimated_duration_seconds: process.estimated_duration_seconds ?? '',
        quality_criteria: JSON.stringify(process.quality_criteria || {}, null, 2),
        defect_items: process.defect_items || [],
        auto_print_label: process.auto_print_label ?? false,
        label_template_type: process.label_template_type ?? null,
        process_type: process.process_type || 'MANUFACTURING',
      });
    } else {
      // Find max process_number from existing processes to avoid duplicates
      const maxProcessNumber =
        processes && processes.length > 0 ? Math.max(...processes.map((p) => p.process_number)) : 0;
      const nextNum = maxProcessNumber + 1;
      const maxSortOrder =
        processes && processes.length > 0 ? Math.max(...processes.map((p) => p.sort_order)) : 0;
      const nextSortOrder = maxSortOrder + 1;
      form.setFormData({
        process_number: nextNum,
        process_code: '',
        process_name_ko: '',
        process_name_en: '',
        description: '',
        sort_order: nextSortOrder,
        is_active: true,
        estimated_duration_seconds: '',
        quality_criteria: '{}',
        defect_items: getSuggestedDefects(nextNum),
        auto_print_label: false,
        label_template_type: null,
        process_type: 'MANUFACTURING',
      });
    }
    modal.open(process);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        process_number: form.formData.process_number,
        process_code: form.formData.process_code,
        process_name_ko: form.formData.process_name_ko,
        process_name_en: form.formData.process_name_en,
        description: form.formData.description || undefined,
        sort_order: form.formData.sort_order,
        is_active: form.formData.is_active,
        estimated_duration_seconds: form.formData.estimated_duration_seconds || undefined,
        quality_criteria: form.formData.quality_criteria
          ? JSON.parse(form.formData.quality_criteria)
          : undefined,
        defect_items: form.formData.defect_items,
        auto_print_label: form.formData.auto_print_label,
        label_template_type: form.formData.label_template_type || undefined,
        process_type: form.formData.process_type,
      };
      modal.editingItem
        ? await processesApi.updateProcess(modal.editingItem.id, submitData)
        : await processesApi.createProcess(submitData);
      modal.close();
      refetch();
      message.success('Process saved successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save process');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (processId: number) => {
    if (!confirm('Are you sure you want to delete this process?')) return;
    try {
      await processesApi.deleteProcess(processId);
      refetch();
      message.success('Process deleted successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to delete process');
      // Show user-friendly error for dependent data constraint
      if (errorMsg.includes('dependent data') || errorMsg.includes('CONF_002')) {
        message.error(
          'Cannot delete: This process has associated work history (process_data). Please deactivate instead.',
          8
        );
      } else {
        message.error(errorMsg, 5);
      }
    }
  };

  return (
    <>
      <div style={styles.header}>
        <div style={styles.title}>Total Processes: {processes?.length || 0}</div>
        <Button onClick={() => handleOpenModal()}>+ Add Process</Button>
      </div>
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading processes...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Process #</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Description</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Sequence</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {processes?.map((process, idx) => (
                  <tr key={process.id} style={getRowStyle(idx)}>
                    <td
                      style={{ ...styles.td, textAlign: 'center', fontWeight: '600', fontSize: '16px' }}
                    >
                      {process.process_number}
                    </td>
                    <td style={{ ...styles.td, fontWeight: '500' }}>{process.process_name_en}</td>
                    <td
                      style={{
                        ...styles.td,
                        color: 'var(--color-text-secondary)',
                        fontSize: '13px',
                      }}
                    >
                      {process.description || '-'}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>{process.sort_order}</td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={process.is_active} />
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleOpenModal(process)}
                        >
                          Edit
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(process.id)}>
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

      {/* Main Process Modal */}
      <Modal
        isOpen={modal.isOpen}
        onClose={modal.close}
        title={modal.editingItem ? 'Edit Process' : 'Add New Process'}
        footer={
          <div style={styles.modalFooter}>
            <Button variant="secondary" onClick={modal.close}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Save</Button>
          </div>
        }
      >
        <form
          onSubmit={handleSubmit}
          style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}
        >
          <div style={{ gridColumn: 'span 1' }}>
            <Input
              label="Process Number"
              type="number"
              value={form.formData.process_number}
              onChange={(e) => form.setField('process_number', parseInt(e.target.value))}
              required
            />
          </div>
          <div style={{ gridColumn: 'span 1' }}>
            <Input
              label="Process Code"
              value={form.formData.process_code}
              onChange={(e) => form.setField('process_code', e.target.value)}
              required
              placeholder="e.g., LASER_MARKING"
            />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'var(--color-text-primary)',
              }}
            >
              Process Type
            </label>
            <select
              value={form.formData.process_type}
              onChange={(e) => form.setField('process_type', e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
                cursor: 'pointer',
              }}
            >
              <option value="MANUFACTURING">Manufacturing (General)</option>
              <option value="SERIAL_CONVERSION">Serial Conversion</option>
            </select>
            <div
              style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }}
            >
              Manufacturing: General production process. Serial Conversion: Process for assigning
              serial numbers (only one allowed as the final step).
            </div>
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <Input
              label="Process Name (Korean)"
              value={form.formData.process_name_ko}
              onChange={(e) => form.setField('process_name_ko', e.target.value)}
              required
            />
          </div>
          <div style={{ gridColumn: 'span 2' }}>
            <Input
              label="Process Name (English)"
              value={form.formData.process_name_en}
              onChange={(e) => form.setField('process_name_en', e.target.value)}
              required
            />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <Input
              label="Description"
              value={form.formData.description}
              onChange={(e) => form.setField('description', e.target.value)}
            />
          </div>

          <div style={{ gridColumn: 'span 1' }}>
            <Input
              label="Estimated Duration (sec)"
              type="number"
              value={form.formData.estimated_duration_seconds}
              onChange={(e) =>
                form.setField(
                  'estimated_duration_seconds',
                  e.target.value ? parseInt(e.target.value) : ''
                )
              }
              placeholder="Optional"
            />
          </div>
          <div style={{ gridColumn: 'span 1' }}>
            <Input
              label="Sort Order"
              type="number"
              value={form.formData.sort_order}
              onChange={(e) => form.setField('sort_order', parseInt(e.target.value))}
              required
            />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'var(--color-text-primary)',
              }}
            >
              Quality Criteria (JSON)
            </label>
            <textarea
              value={form.formData.quality_criteria}
              onChange={(e) => form.setField('quality_criteria', e.target.value)}
              placeholder='{"key": "value"}'
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '10px',
                border: '1px solid var(--color-border)',
                borderRadius: '6px',
                fontSize: '14px',
                fontFamily: 'monospace',
                resize: 'vertical',
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>

          {/* Defect Items Management */}
          <div
            style={{
              gridColumn: 'span 2',
              padding: '15px',
              backgroundColor: 'var(--color-bg-tertiary, var(--color-bg-secondary))',
              borderRadius: '12px',
              border: '1px solid var(--color-border)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '15px',
              }}
            >
              <div>
                <label
                  style={{
                    fontSize: '15px',
                    fontWeight: '600',
                    color: 'var(--color-text-primary)',
                    display: 'block',
                  }}
                >
                  Defect Items Management
                </label>
                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Pre-defined defects for failure reports
                </span>
              </div>
              <Button
                size="sm"
                variant="secondary"
                onClick={openSuggestionModal}
                style={{ fontSize: '12px' }}
              >
                Load Suggested Defaults
              </Button>
            </div>

            <div
              style={{
                display: 'flex',
                gap: '8px',
                marginBottom: '15px',
                alignItems: 'flex-start',
              }}
            >
              <Input
                placeholder="Enter new defect item"
                onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const target = e.currentTarget;
                    if (target.value.trim()) {
                      addDefectItem(target.value);
                      target.value = '';
                    }
                  }
                }}
                wrapperStyle={{ flex: 1, marginBottom: 0 }}
              />
              <Button
                size="md"
                style={{ height: '38px', minWidth: '80px', marginTop: '0' }}
                onClick={(e: React.MouseEvent<HTMLButtonElement>) => {
                  e.preventDefault();
                  const input = e.currentTarget.parentElement?.querySelector(
                    'input'
                  ) as HTMLInputElement | null;
                  if (input && input.value.trim()) {
                    addDefectItem(input.value);
                    input.value = '';
                  }
                }}
              >
                Add
              </Button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', minHeight: '40px' }}>
              {form.formData.defect_items.length === 0 ? (
                <div
                  style={{
                    fontSize: '13px',
                    color: 'var(--color-text-secondary)',
                    padding: '10px',
                    textAlign: 'center',
                    width: '100%',
                    border: '1px dashed var(--color-border)',
                    borderRadius: '8px',
                  }}
                >
                  No defect items registered.
                </div>
              ) : (
                form.formData.defect_items.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '6px 12px',
                      backgroundColor: 'var(--color-bg-primary)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: '500',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                      transition: 'all 0.2s',
                    }}
                  >
                    {item}
                    <span
                      onClick={() => removeDefectItem(idx)}
                      style={{
                        cursor: 'pointer',
                        color: 'var(--color-text-secondary)',
                        fontSize: '18px',
                        lineHeight: 1,
                        marginLeft: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '16px',
                        height: '16px',
                        borderRadius: '50%',
                        transition: 'background 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
                        e.currentTarget.style.color = 'var(--color-error)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = 'var(--color-text-secondary)';
                      }}
                    >
                      ×
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Auto Print Label Settings */}
          <div
            style={{
              gridColumn: 'span 2',
              padding: '15px',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: '12px',
              border: '1px solid var(--color-border)',
            }}
          >
            <h4
              style={{
                marginBottom: '15px',
                fontSize: '15px',
                fontWeight: '600',
                color: 'var(--color-text-primary)',
              }}
            >
              Auto Print Label Settings
            </h4>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.formData.auto_print_label}
                  onChange={(e) => form.setField('auto_print_label', e.target.checked)}
                  style={{ marginRight: '8px', width: '16px', height: '16px', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '14px', fontWeight: '500' }}>
                  Auto print label on completion
                </span>
              </label>
            </div>

            {form.formData.auto_print_label && (
              <div style={{ marginBottom: '0' }}>
                <label
                  style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'var(--color-text-primary)',
                  }}
                >
                  Label Type
                </label>
                <select
                  value={form.formData.label_template_type || ''}
                  onChange={(e) => form.setField('label_template_type', e.target.value || null)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    fontSize: '14px',
                    backgroundColor: 'var(--color-bg-primary)',
                    color: 'var(--color-text-primary)',
                    cursor: 'pointer',
                  }}
                >
                  <option value="">Select label type</option>
                  <option value="WIP_LABEL">WIP Label (60x30mm, QR code)</option>
                  <option value="SERIAL_LABEL">Serial Label (60x30mm, QR code)</option>
                  <option value="LOT_LABEL">LOT Label (60x30mm, QR code)</option>
                </select>
              </div>
            )}
          </div>

          <div style={{ gridColumn: 'span 2' }}>
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
          </div>
        </form>
      </Modal>

      {/* Suggested Defects Selection Modal */}
      <Modal
        isOpen={suggestionModal.isOpen}
        onClose={suggestionModal.close}
        title="Select Suggested Defects"
        footer={
          <div style={styles.modalFooter}>
            <Button variant="secondary" onClick={suggestionModal.close}>
              Cancel
            </Button>
            <Button onClick={addSelectedSuggestions} disabled={selectedSuggestions.length === 0}>
              Add Selected ({selectedSuggestions.length})
            </Button>
          </div>
        }
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '8px' }}>
          <p
            style={{
              fontSize: '14px',
              color: 'var(--color-text-secondary)',
              marginBottom: '20px',
            }}
          >
            Choose common defects from the categories below to add them to this process.
          </p>

          {Object.entries(CATEGORIZED_SUGGESTIONS).map(([category, items]) => (
            <div key={category} style={{ marginBottom: '25px' }}>
              <h4
                style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'var(--color-brand-400)',
                  marginBottom: '12px',
                  paddingBottom: '6px',
                  borderBottom: '1px solid var(--color-border)',
                }}
              >
                {category}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {items.map((item) => (
                  <label
                    key={item}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '8px 12px',
                      backgroundColor: selectedSuggestions.includes(item)
                        ? 'var(--color-bg-secondary)'
                        : 'transparent',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'background 0.2s',
                      fontSize: '13px',
                      border: selectedSuggestions.includes(item)
                        ? '1px solid var(--color-brand-400)'
                        : '1px solid transparent',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSuggestions.includes(item)}
                      onChange={() => toggleSuggestion(item)}
                      style={{
                        width: '16px',
                        height: '16px',
                        accentColor: 'var(--color-brand-400)',
                      }}
                    />
                    <span
                      style={{
                        color: selectedSuggestions.includes(item)
                          ? 'var(--color-text-primary)'
                          : 'var(--color-text-secondary)',
                      }}
                    >
                      {item}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Modal>
    </>
  );
};
