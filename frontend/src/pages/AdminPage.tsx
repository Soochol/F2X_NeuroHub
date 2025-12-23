/**
 * Admin Page - System Administration
 */

import { equipmentApi, processesApi, productModelsApi, productionLinesApi, usersApi } from '@/api';
import { Button, Card, Input, Modal, RoleBadge, Select, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { Equipment, Process, ProductModel, ProductionLine, User, UserRole } from '@/types/api';
import { UserRole as UserRoleEnum, getErrorMessage } from '@/types/api';
import { App } from 'antd';
import { format } from 'date-fns';
import { useState } from 'react';

type TabType = 'users' | 'processes' | 'products' | 'productionLines' | 'equipment';

interface UserFormData { username: string; full_name: string; email: string; password: string; role: UserRole; is_active: boolean; }
interface ProcessFormData { process_number: number; process_code: string; process_name_ko: string; process_name_en: string; description: string; sort_order: number; is_active: boolean; estimated_duration_seconds: number | ''; quality_criteria: string; defect_items: string[]; auto_print_label: boolean; label_template_type: string | null; process_type: string; }
interface ProductFormData { model_code: string; model_name: string; category: string; status: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED'; }
interface ProductionLineFormData { line_code: string; line_name: string; description: string; cycle_time_sec: number | ''; location: string; is_active: boolean; }
interface EquipmentFormData { equipment_code: string; equipment_name: string; equipment_type: string; description: string; process_id: number | ''; production_line_id: number | ''; manufacturer: string; model_number: string; serial_number: string; status: string; is_active: boolean; }

// Shared styles with CSS variables for theming
const styles = {
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '20px' },
  title: { fontSize: '18px', fontWeight: '600', color: 'var(--color-text-primary)' },
  loading: { textAlign: 'center' as const, padding: '40px', color: 'var(--color-text-secondary)' },
  error: { textAlign: 'center' as const, padding: '40px', color: 'var(--color-error)' },
  th: { padding: '12px', fontWeight: '600', color: 'var(--color-text-primary)' },
  td: { padding: '12px', color: 'var(--color-text-primary)' },
  actions: { display: 'flex', gap: '8px', justifyContent: 'center' },
  checkbox: { marginBottom: '15px' },
  checkboxLabel: { display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' },
  checkboxInput: { width: '16px', height: '16px', accentColor: 'var(--color-brand)' },
  checkboxText: { fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' },
  modalFooter: { display: 'flex', gap: '10px', justifyContent: 'flex-end' },
};

const getTabStyle = (isActive: boolean) => ({
  padding: '12px 24px',
  backgroundColor: isActive ? 'var(--color-brand)' : 'var(--color-bg-secondary)',
  color: isActive ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
  border: 'none',
  borderBottom: isActive ? '3px solid var(--color-brand-500)' : '3px solid transparent',
  borderRadius: '6px 6px 0 0',
  cursor: 'pointer',
  fontWeight: isActive ? 'bold' : '500',
  fontSize: '15px',
  transition: 'all 0.2s',
});

const getRowStyle = (idx: number) => ({
  borderBottom: '1px solid var(--color-border)',
  backgroundColor: idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)'
});

export const AdminPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('users');
  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px', color: 'var(--color-text-primary)' }}>Administration</h1>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid var(--color-border)' }}>
        <button onClick={() => setActiveTab('users')} style={getTabStyle(activeTab === 'users')}>User Management</button>
        <button onClick={() => setActiveTab('processes')} style={getTabStyle(activeTab === 'processes')}>Process Management</button>
        <button onClick={() => setActiveTab('products')} style={getTabStyle(activeTab === 'products')}>Product Models</button>
        <button onClick={() => setActiveTab('productionLines')} style={getTabStyle(activeTab === 'productionLines')}>Production Sites</button>
        <button onClick={() => setActiveTab('equipment')} style={getTabStyle(activeTab === 'equipment')}>Equipment</button>
      </div>
      {activeTab === 'users' && <UserManagement />}
      {activeTab === 'processes' && <ProcessManagement />}
      {activeTab === 'products' && <ProductModelManagement />}
      {activeTab === 'productionLines' && <ProductionLineManagement />}
      {activeTab === 'equipment' && <EquipmentManagement />}
    </div>
  );
};

const UserManagement = () => {
  const { message } = App.useApp();
  const { data: users, isLoading, error, refetch, setError } = useAsyncData<User[]>({
    fetchFn: () => usersApi.getUsers(), initialData: [], errorMessage: 'Failed to load users'
  });
  const modal = useModalState<User>();
  const form = useFormState<UserFormData>({ username: '', full_name: '', email: '', password: '', role: UserRoleEnum.OPERATOR, is_active: true });

  const handleOpenModal = (user?: User) => {
    user ? form.setFormData({ username: user.username, full_name: user.full_name, email: '', password: '', role: user.role, is_active: user.is_active }) : form.resetForm();
    modal.open(user);
  };

  // Frontend validation for user form
  const validateUserForm = (): string | null => {
    const { username, full_name, email, password } = form.formData;
    const isNewUser = !modal.editingItem;

    // Username validation (3-50 chars, alphanumeric, underscore, Korean)
    if (isNewUser) {
      if (username.length < 3 || username.length > 50) {
        return 'Username must be 3-50 characters';
      }
      if (!/^[a-zA-Z0-9_가-힣]+$/.test(username)) {
        return 'Username: letters, numbers, underscores, Korean only';
      }
    }

    // Full name validation (required, max 100 chars)
    if (!full_name || full_name.length < 1) {
      return 'Full name is required';
    }
    if (full_name.length > 100) {
      return 'Full name max 100 characters';
    }

    // Email validation (optional, but must be valid format if provided)
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Invalid email format';
    }

    // Password validation (only for new users, min 4 chars)
    if (isNewUser) {
      if (password.length < 4) {
        return 'Password must be at least 4 characters';
      }
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Frontend validation
    const validationError = validateUserForm();
    if (validationError) {
      message.error(validationError, 5);
      return;
    }

    try {
      modal.editingItem
        ? await usersApi.updateUser(modal.editingItem.id, { full_name: form.formData.full_name, role: form.formData.role, is_active: form.formData.is_active })
        : await usersApi.createUser(form.formData);
      modal.close(); form.resetForm(); refetch();
      message.success(modal.editingItem ? 'User updated successfully' : 'User created successfully');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save user');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try { await usersApi.deleteUser(userId); refetch(); } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to delete user')); }
  };

  return (
    <>
      <div style={styles.header}><div style={styles.title}>Total Users: {users?.length || 0}</div><Button onClick={() => handleOpenModal()}>+ Add User</Button></div>
      <Card>
        {isLoading ? <div style={styles.loading}>Loading users...</div> : error ? <div style={styles.error}>{error}</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ ...styles.th, textAlign: 'left' }}>Username</th><th style={{ ...styles.th, textAlign: 'left' }}>Full Name</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Role</th><th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Created</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{users?.map((user, idx) => (
                <tr key={user.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, fontWeight: '500' }}>{user.username}</td><td style={styles.td}>{user.full_name}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><RoleBadge role={user.role} /></td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={user.is_active} /></td>
                  <td style={{ ...styles.td, textAlign: 'center', fontSize: '13px', color: 'var(--color-text-secondary)' }}>{format(new Date(user.created_at), 'yyyy-MM-dd')}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><div style={styles.actions}>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(user)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(user.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit User' : 'Add New User'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit}>
          <Input label="User ID" value={form.formData.username} onChange={(e) => form.setField('username', e.target.value)} required disabled={!!modal.editingItem} />
          {!modal.editingItem && <>
            <Input label="Password" type="password" value={form.formData.password} onChange={(e) => form.setField('password', e.target.value)} required />
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '-10px', marginBottom: '15px' }}>
              Min 4 characters
            </div>
          </>}
          <Input label="Full Name" value={form.formData.full_name} onChange={(e) => form.setField('full_name', e.target.value)} required />
          {!modal.editingItem && <Input label="Email (optional)" type="email" value={form.formData.email} onChange={(e) => form.setField('email', e.target.value)} />}
          <Select label="Role" value={form.formData.role} onChange={(e) => form.setField('role', e.target.value as UserRole)}
            options={[{ value: UserRoleEnum.ADMIN, label: 'Admin' }, { value: UserRoleEnum.MANAGER, label: 'Manager' }, { value: UserRoleEnum.OPERATOR, label: 'Operator' }]} />
          <div style={styles.checkbox}><label style={styles.checkboxLabel}>
            <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
            <span style={styles.checkboxText}>Active</span>
          </label></div>
        </form>
      </Modal>
    </>
  );
};

const ProcessManagement = () => {
  const { message } = App.useApp();
  const { data: processes, isLoading, error, refetch, setError } = useAsyncData<Process[]>({
    fetchFn: async () => (await processesApi.getProcesses()).sort((a, b) => a.sort_order - b.sort_order),
    initialData: [], errorMessage: 'Failed to load processes'
  });
  const modal = useModalState<Process>();
  const form = useFormState<ProcessFormData>({ process_number: 1, process_code: '', process_name_ko: '', process_name_en: '', description: '', sort_order: 1, is_active: true, estimated_duration_seconds: '', quality_criteria: '{}', defect_items: [], auto_print_label: false, label_template_type: null, process_type: 'MANUFACTURING' });

  const CATEGORIZED_SUGGESTIONS: Record<string, string[]> = {
    'Appearance': ['Scratch', 'Dent', 'Contamination', 'Discoloration', 'Burr', 'Crack', 'Housing damage'],
    'Assembly': ['Missing Part', 'Loose Screw', 'Alignment Error', 'Gap Issue', 'Poor Fit', 'Incorrect Part'],
    'Functional': ['Power Failure', 'Sensor Error', 'Connection Error', 'Noise Issue', 'Signal Weak'],
    'Marking/Label': ['Unreadable QR', 'Blurry Printing', 'Wrong Label', 'Misplaced Label', 'Duplicate Serial'],
    'Packaging': ['Box Damage', 'Missing Manual', 'Wrong Quantity', 'Sealing Issue', 'Missing Accessory']
  };

  const suggestionModal = useModalState<void>();
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([]);

  const toggleSuggestion = (item: string) => {
    setSelectedSuggestions(prev =>
      prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item]
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

  const getSuggestedDefects = (processNumber: number) => {
    // Legacy mapping for auto-load on new process
    const legacy: Record<number, string[]> = {
      1: ['Blurry marking', 'Incorrect marking position', 'QR code unreadable'],
      2: ['Housing scratch', 'Foreign object inclusion', 'Assembly gap'],
      3: ['Bent pin', 'Poor press-fit depth', 'Missing pin'],
      4: ['Spring deformation', 'Missing spring', 'Assembly detachment'],
      5: ['Insufficient weld', 'Excessive weld (burr)', 'Weld crack'],
      6: ['Appearance defect', 'Functional test failed', 'Dimension under spec'],
      7: ['Duplicate serial', 'Poor label attachment'],
      8: ['Packaging damage', 'Insufficient quantity', 'Incorrect attachment']
    };
    return legacy[processNumber] || [];
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
        estimated_duration_seconds: (process as any).estimated_duration_seconds ?? '',
        quality_criteria: JSON.stringify((process as any).quality_criteria || {}, null, 2),
        defect_items: (process as any).defect_items || [],
        auto_print_label: process.auto_print_label ?? false,
        label_template_type: process.label_template_type ?? null,
        process_type: (process as any).process_type || 'MANUFACTURING'
      });
    } else {
      const nextNum = (processes?.length || 0) + 1;
      form.setFormData({
        process_number: nextNum,
        process_code: '',
        process_name_ko: '',
        process_name_en: '',
        description: '',
        sort_order: nextNum,
        is_active: true,
        estimated_duration_seconds: '',
        quality_criteria: '{}',
        defect_items: getSuggestedDefects(nextNum),
        auto_print_label: false,
        label_template_type: null,
        process_type: 'MANUFACTURING'
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
        quality_criteria: form.formData.quality_criteria ? JSON.parse(form.formData.quality_criteria) : undefined,
        defect_items: form.formData.defect_items,
        auto_print_label: form.formData.auto_print_label,
        label_template_type: form.formData.label_template_type || undefined,
        process_type: form.formData.process_type,
      };
      modal.editingItem ? await processesApi.updateProcess(modal.editingItem.id, submitData) : await processesApi.createProcess(submitData);
      modal.close(); refetch();
      message.success('Process saved successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save process');
      message.error(errorMsg, 5);
      // 모달은 유지하고 토스트만 표시 (setError 호출하지 않음)
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
      message.error(errorMsg, 5);
      setError(errorMsg);
    }
  };

  return (
    <>
      <div style={styles.header}><div style={styles.title}>Total Processes: {processes?.length || 0}</div><Button onClick={() => handleOpenModal()}>+ Add Process</Button></div>
      <Card>
        {isLoading ? <div style={styles.loading}>Loading processes...</div> : error ? <div style={styles.error}>{error}</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ ...styles.th, textAlign: 'center' }}>Process #</th><th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                <th style={{ ...styles.th, textAlign: 'left' }}>Description</th><th style={{ ...styles.th, textAlign: 'center' }}>Sequence</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Status</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{processes?.map((process, idx) => (
                <tr key={process.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, textAlign: 'center', fontWeight: '600', fontSize: '16px' }}>{process.process_number}</td>
                  <td style={{ ...styles.td, fontWeight: '500' }}>{process.process_name_en}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{process.description || '-'}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}>{process.sort_order}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={process.is_active} /></td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><div style={styles.actions}>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(process)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(process.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit Process' : 'Add New Process'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <div style={{ gridColumn: 'span 1' }}>
            <Input label="Process Number" type="number" value={form.formData.process_number} onChange={(e) => form.setField('process_number', parseInt(e.target.value))} required />
          </div>
          <div style={{ gridColumn: 'span 1' }}>
            <Input label="Process Code" value={form.formData.process_code} onChange={(e) => form.setField('process_code', e.target.value)} required placeholder="e.g., LASER_MARKING" />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>Process Type</label>
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
                cursor: 'pointer'
              }}
            >
              <option value="MANUFACTURING">Manufacturing (General)</option>
              <option value="SERIAL_CONVERSION">Serial Conversion</option>
            </select>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
              Manufacturing: General production process. Serial Conversion: Process for assigning serial numbers (only one allowed as the final step).
            </div>
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <Input label="Process Name (Korean)" value={form.formData.process_name_ko} onChange={(e) => form.setField('process_name_ko', e.target.value)} required />
          </div>
          <div style={{ gridColumn: 'span 2' }}>
            <Input label="Process Name (English)" value={form.formData.process_name_en} onChange={(e) => form.setField('process_name_en', e.target.value)} required />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} />
          </div>

          <div style={{ gridColumn: 'span 1' }}>
            <Input label="Estimated Duration (sec)" type="number" value={form.formData.estimated_duration_seconds} onChange={(e) => form.setField('estimated_duration_seconds', e.target.value ? parseInt(e.target.value) : '')} placeholder="Optional" />
          </div>
          <div style={{ gridColumn: 'span 1' }}>
            <Input label="Sort Order" type="number" value={form.formData.sort_order} onChange={(e) => form.setField('sort_order', parseInt(e.target.value))} required />
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>Quality Criteria (JSON)</label>
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
                color: 'var(--color-text-primary)'
              }}
            />
          </div>

          {/* Defect Items Management */}
          <div style={{ gridColumn: 'span 2', padding: '15px', backgroundColor: 'var(--color-bg-tertiary, var(--color-bg-secondary))', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <div>
                <label style={{ fontSize: '15px', fontWeight: '600', color: 'var(--color-text-primary)', display: 'block' }}>Defect Items Management</label>
                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Pre-defined defects for failure reports</span>
              </div>
              <Button size="sm" variant="secondary" onClick={openSuggestionModal} style={{ fontSize: '12px' }}>Load Suggested Defaults</Button>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '15px', alignItems: 'flex-start' }}>
              <Input
                placeholder="Enter new defect item"
                onKeyDown={(e: any) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    if (e.currentTarget.value.trim()) {
                      addDefectItem(e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }
                }}
                wrapperStyle={{ flex: 1, marginBottom: 0 }}
              />
              <Button
                size="md"
                style={{ height: '38px', minWidth: '80px', marginTop: '0' }}
                onClick={(e: any) => {
                  e.preventDefault();
                  const input = (e.currentTarget.parentElement?.querySelector('input')) as HTMLInputElement;
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
                <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', padding: '10px', textAlign: 'center', width: '100%', border: '1px dashed var(--color-border)', borderRadius: '8px' }}>
                  No defect items registered.
                </div>
              ) : (
                form.formData.defect_items.map((item, idx) => (
                  <div key={idx} style={{
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
                    transition: 'all 0.2s'
                  }}>
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
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)'; e.currentTarget.style.color = 'var(--color-error)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
                    >×</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Auto Print Label Settings */}
          <div style={{ gridColumn: 'span 2', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
            <h4 style={{ marginBottom: '15px', fontSize: '15px', fontWeight: '600', color: 'var(--color-text-primary)' }}>Auto Print Label Settings</h4>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.formData.auto_print_label}
                  onChange={(e) => form.setField('auto_print_label', e.target.checked)}
                  style={{ marginRight: '8px', width: '16px', height: '16px', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '14px', fontWeight: '500' }}>Auto print label on completion</span>
              </label>
            </div>

            {form.formData.auto_print_label && (
              <div style={{ marginBottom: '0' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>Label Type</label>
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
                    cursor: 'pointer'
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
            <div style={styles.checkbox}><label style={styles.checkboxLabel}>
              <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
              <span style={styles.checkboxText}>Active</span>
            </label></div>
          </div>
        </form>
      </Modal>

      {/* Suggested Defects Selection Modal */}
      <Modal
        isOpen={suggestionModal.isOpen}
        onClose={suggestionModal.close}
        title="Select Suggested Defects"
        footer={(
          <div style={styles.modalFooter}>
            <Button variant="secondary" onClick={suggestionModal.close}>Cancel</Button>
            <Button onClick={addSelectedSuggestions} disabled={selectedSuggestions.length === 0}>
              Add Selected ({selectedSuggestions.length})
            </Button>
          </div>
        )}
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '8px' }}>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '20px' }}>
            Choose common defects from the categories below to add them to this process.
          </p>

          {Object.entries(CATEGORIZED_SUGGESTIONS).map(([category, items]) => (
            <div key={category} style={{ marginBottom: '25px' }}>
              <h4 style={{
                fontSize: '14px',
                fontWeight: '600',
                color: 'var(--color-brand-400)',
                marginBottom: '12px',
                paddingBottom: '6px',
                borderBottom: '1px solid var(--color-border)'
              }}>
                {category}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {items.map(item => (
                  <label
                    key={item}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '8px 12px',
                      backgroundColor: selectedSuggestions.includes(item) ? 'var(--color-bg-secondary)' : 'transparent',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'background 0.2s',
                      fontSize: '13px',
                      border: selectedSuggestions.includes(item) ? '1px solid var(--color-brand-400)' : '1px solid transparent'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSuggestions.includes(item)}
                      onChange={() => toggleSuggestion(item)}
                      style={{ width: '16px', height: '16px', accentColor: 'var(--color-brand-400)' }}
                    />
                    <span style={{ color: selectedSuggestions.includes(item) ? 'var(--color-text-primary)' : 'var(--color-text-secondary)' }}>
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

const ProductModelManagement = () => {
  const { data: products, isLoading, error, refetch, setError } = useAsyncData<ProductModel[]>({
    fetchFn: () => productModelsApi.getProductModels(), initialData: [], errorMessage: 'Failed to load product models'
  });
  const modal = useModalState<ProductModel>();
  const form = useFormState<ProductFormData>({ model_code: '', model_name: '', category: '', status: 'ACTIVE' });

  const handleOpenModal = (product?: ProductModel) => {
    product ? form.setFormData({ model_code: product.model_code, model_name: product.model_name, category: product.category || '', status: product.status }) : form.resetForm();
    modal.open(product);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        model_code: form.formData.model_code,
        model_name: form.formData.model_name,
        category: form.formData.category || undefined,
        status: form.formData.status,
      };
      modal.editingItem ? await productModelsApi.updateProductModel(modal.editingItem.id, submitData) : await productModelsApi.createProductModel(submitData);
      modal.close(); refetch();
    } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to save product model')); }
  };

  const handleDelete = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product model?')) return;
    try { await productModelsApi.deleteProductModel(productId); refetch(); } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to delete product model')); }
  };

  return (
    <>
      <div style={styles.header}><div style={styles.title}>Total Product Models: {products?.length || 0}</div><Button onClick={() => handleOpenModal()}>+ Add Product Model</Button></div>
      <Card>
        {isLoading ? <div style={styles.loading}>Loading product models...</div> : error ? <div style={styles.error}>{error}</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ ...styles.th, textAlign: 'left' }}>Code</th><th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                <th style={{ ...styles.th, textAlign: 'left' }}>Category</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Status</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{products?.map((product, idx) => (
                <tr key={product.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, fontWeight: '600' }}>{product.model_code}</td><td style={{ ...styles.td, fontWeight: '500' }}>{product.model_name}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{product.category || '-'}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={product.status === 'ACTIVE'} /></td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><div style={styles.actions}>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(product)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(product.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit Product Model' : 'Add New Product Model'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit}>
          <Input label="Model Code" value={form.formData.model_code} onChange={(e) => form.setField('model_code', e.target.value)} required disabled={!!modal.editingItem} placeholder="e.g., NH-F2X-001" />
          <Input label="Model Name" value={form.formData.model_name} onChange={(e) => form.setField('model_name', e.target.value)} required />
          <Input label="Category" value={form.formData.category} onChange={(e) => form.setField('category', e.target.value)} placeholder="e.g., Standard, Premium" />
          <Select label="Status" value={form.formData.status} onChange={(e) => form.setField('status', e.target.value as 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED')}
            options={[{ value: 'ACTIVE', label: 'Active' }, { value: 'INACTIVE', label: 'Inactive' }, { value: 'DISCONTINUED', label: 'Discontinued' }]} />
        </form>
      </Modal>
    </>
  );
};

const ProductionLineManagement = () => {
  const { data: productionLines, isLoading, error, refetch, setError } = useAsyncData<ProductionLine[]>({
    fetchFn: () => productionLinesApi.getProductionLines(), initialData: [], errorMessage: 'Failed to load production lines'
  });
  const modal = useModalState<ProductionLine>();
  const form = useFormState<ProductionLineFormData>({ line_code: '', line_name: '', description: '', cycle_time_sec: '', location: '', is_active: true });

  const handleOpenModal = (productionLine?: ProductionLine) => {
    productionLine ? form.setFormData({ line_code: productionLine.line_code, line_name: productionLine.line_name, description: productionLine.description || '', cycle_time_sec: productionLine.cycle_time_sec ?? '', location: productionLine.location || '', is_active: productionLine.is_active }) : form.resetForm();
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
      modal.editingItem ? await productionLinesApi.updateProductionLine(modal.editingItem.id, submitData) : await productionLinesApi.createProductionLine(submitData);
      modal.close(); refetch();
    } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to save production line')); }
  };

  const handleDelete = async (productionLineId: number) => {
    if (!confirm('Are you sure you want to delete this production line?')) return;
    try { await productionLinesApi.deleteProductionLine(productionLineId); refetch(); } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to delete production line')); }
  };

  return (
    <>
      <div style={styles.header}><div style={styles.title}>Total Production Lines: {productionLines?.length || 0}</div><Button onClick={() => handleOpenModal()}>+ Add Production Line</Button></div>
      <Card>
        {isLoading ? <div style={styles.loading}>Loading production lines...</div> : error ? <div style={styles.error}>{error}</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ ...styles.th, textAlign: 'left' }}>Code</th><th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Cycle Time (sec)</th><th style={{ ...styles.th, textAlign: 'left' }}>Location</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Status</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{productionLines?.map((line, idx) => (
                <tr key={line.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, fontWeight: '600' }}>{line.line_code}</td><td style={{ ...styles.td, fontWeight: '500' }}>{line.line_name}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}>{line.cycle_time_sec ?? '-'}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{line.location || '-'}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={line.is_active} /></td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><div style={styles.actions}>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(line)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(line.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit Production Line' : 'Add New Production Line'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit}>
          <Input label="Line Code" value={form.formData.line_code} onChange={(e) => form.setField('line_code', e.target.value)} required disabled={!!modal.editingItem} placeholder="e.g., LINE-A" />
          <Input label="Line Name" value={form.formData.line_name} onChange={(e) => form.setField('line_name', e.target.value)} required placeholder="e.g., Assembly Line A" />
          <Input label="Cycle Time (sec)" type="number" value={form.formData.cycle_time_sec} onChange={(e) => form.setField('cycle_time_sec', e.target.value ? parseInt(e.target.value) : '')} placeholder="Optional" />
          <Input label="Location" value={form.formData.location} onChange={(e) => form.setField('location', e.target.value)} placeholder="e.g., Building 1, Zone A" />
          <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} />
          <div style={styles.checkbox}><label style={styles.checkboxLabel}>
            <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
            <span style={styles.checkboxText}>Active</span>
          </label></div>
        </form>
      </Modal>
    </>
  );
};

const EquipmentManagement = () => {
  const { data: equipment, isLoading, error, refetch, setError } = useAsyncData<Equipment[]>({
    fetchFn: () => equipmentApi.getEquipment(), initialData: [], errorMessage: 'Failed to load equipment'
  });
  const { data: processes } = useAsyncData<Process[]>({
    fetchFn: () => processesApi.getProcesses(), initialData: [], errorMessage: 'Failed to load processes'
  });
  const { data: productionLines } = useAsyncData<ProductionLine[]>({
    fetchFn: () => productionLinesApi.getProductionLines(), initialData: [], errorMessage: 'Failed to load production lines'
  });
  const modal = useModalState<Equipment>();
  const form = useFormState<EquipmentFormData>({ equipment_code: '', equipment_name: '', equipment_type: '', description: '', process_id: '', production_line_id: '', manufacturer: '', model_number: '', serial_number: '', status: 'AVAILABLE', is_active: true });

  const handleOpenModal = (equip?: Equipment) => {
    equip ? form.setFormData({
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
      is_active: equip.is_active
    }) : form.resetForm();
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
      modal.editingItem ? await equipmentApi.updateEquipment(modal.editingItem.id, submitData) : await equipmentApi.createEquipment(submitData);
      modal.close(); refetch();
    } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to save equipment')); }
  };

  const handleDelete = async (equipmentId: number) => {
    if (!confirm('Are you sure you want to delete this equipment?')) return;
    try { await equipmentApi.deleteEquipment(equipmentId); refetch(); } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to delete equipment')); }
  };

  const getLineName = (lineId?: number) => productionLines?.find(l => l.id === lineId)?.line_name || '-';

  return (
    <>
      <div style={styles.header}><div style={styles.title}>Total Equipment: {equipment?.length || 0}</div><Button onClick={() => handleOpenModal()}>+ Add Equipment</Button></div>
      <Card>
        {isLoading ? <div style={styles.loading}>Loading equipment...</div> : error ? <div style={styles.error}>{error}</div> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ ...styles.th, textAlign: 'left' }}>Code</th><th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                <th style={{ ...styles.th, textAlign: 'left' }}>Type</th><th style={{ ...styles.th, textAlign: 'left' }}>Line</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Status</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{equipment?.map((equip, idx) => (
                <tr key={equip.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, fontWeight: '600' }}>{equip.equipment_code}</td>
                  <td style={{ ...styles.td, fontWeight: '500' }}>{equip.equipment_name}</td>
                  <td style={{ ...styles.td, fontSize: '13px' }}>{equip.equipment_type}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{getLineName(equip.production_line_id)}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={equip.is_active} /></td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><div style={styles.actions}>
                    <Button size="sm" variant="secondary" onClick={() => handleOpenModal(equip)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(equip.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit Equipment' : 'Add New Equipment'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit}>
          <Input label="Equipment Code" value={form.formData.equipment_code} onChange={(e) => form.setField('equipment_code', e.target.value)} required disabled={!!modal.editingItem} placeholder="e.g., EQ_LASER_001" />
          <Input label="Equipment Name" value={form.formData.equipment_name} onChange={(e) => form.setField('equipment_name', e.target.value)} required placeholder="e.g., Laser Marker 001" />
          <Input label="Equipment Type" value={form.formData.equipment_type} onChange={(e) => form.setField('equipment_type', e.target.value)} required placeholder="e.g., LASER_MARKER" />
          <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} placeholder="Equipment description" />
          <Select label="Production Line" value={form.formData.production_line_id} onChange={(e) => form.setField('production_line_id', e.target.value ? parseInt(e.target.value) : '')}
            options={productionLines?.map(l => ({ value: String(l.id), label: l.line_name })) || []} />
          <Select label="Process" value={form.formData.process_id} onChange={(e) => form.setField('process_id', e.target.value ? parseInt(e.target.value) : '')}
            options={processes?.map(p => ({ value: String(p.id), label: p.process_name_en })) || []} />
          <Input label="Manufacturer" value={form.formData.manufacturer} onChange={(e) => form.setField('manufacturer', e.target.value)} placeholder="e.g., KEYENCE" />
          <Input label="Model Number" value={form.formData.model_number} onChange={(e) => form.setField('model_number', e.target.value)} placeholder="e.g., MD-X1000" />
          <Input label="Serial Number" value={form.formData.serial_number} onChange={(e) => form.setField('serial_number', e.target.value)} placeholder="Equipment S/N (e.g., LASER01-2024-001)" />
          <Select label="Status" value={form.formData.status} onChange={(e) => form.setField('status', e.target.value)}
            options={[{ value: 'AVAILABLE', label: 'Available' }, { value: 'IN_USE', label: 'In Use' }, { value: 'MAINTENANCE', label: 'Maintenance' }, { value: 'OUT_OF_SERVICE', label: 'Out of Service' }, { value: 'RETIRED', label: 'Retired' }]} />
          <div style={styles.checkbox}><label style={styles.checkboxLabel}>
            <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
            <span style={styles.checkboxText}>Active</span>
          </label></div>
        </form>
      </Modal>
    </>
  );
};

// Export individual components for use in separate routes
export { EquipmentManagement, ProcessManagement, ProductModelManagement, ProductionLineManagement, UserManagement };

