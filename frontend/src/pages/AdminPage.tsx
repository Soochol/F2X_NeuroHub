/**
 * Admin Page - System Administration
 */

import { useState } from 'react';
import { Card, Button, Input, Select, Modal, StatusBadge, RoleBadge } from '@/components/common';
import { useModalState, useFormState, useAsyncData } from '@/hooks';
import { usersApi, processesApi, productModelsApi, productionLinesApi, equipmentApi } from '@/api';
import type { User, Process, ProductModel, ProductionLine, Equipment, UserRole } from '@/types/api';
import { UserRole as UserRoleEnum, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';

type TabType = 'users' | 'processes' | 'products' | 'productionLines' | 'equipment';

interface UserFormData { username: string; full_name: string; email: string; password: string; role: UserRole; is_active: boolean; }
interface ProcessFormData { process_number: number; process_code: string; process_name_ko: string; process_name_en: string; description: string; sort_order: number; is_active: boolean; estimated_duration_seconds: number | ''; quality_criteria: string; auto_print_label: boolean; label_template_type: string | null; }
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
  const { data: users, isLoading, error, refetch, setError } = useAsyncData<User[]>({
    fetchFn: () => usersApi.getUsers(), initialData: [], errorMessage: 'Failed to load users'
  });
  const modal = useModalState<User>();
  const form = useFormState<UserFormData>({ username: '', full_name: '', email: '', password: '', role: UserRoleEnum.OPERATOR, is_active: true });

  const handleOpenModal = (user?: User) => {
    user ? form.setFormData({ username: user.username, full_name: user.full_name, email: '', password: '', role: user.role, is_active: user.is_active }) : form.resetForm();
    modal.open(user);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      modal.editingItem
        ? await usersApi.updateUser(modal.editingItem.id, { full_name: form.formData.full_name, role: form.formData.role, is_active: form.formData.is_active })
        : await usersApi.createUser(form.formData);
      modal.close(); form.resetForm(); refetch();
    } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to save user')); }
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
                    <Button size="small" variant="secondary" onClick={() => handleOpenModal(user)}>Edit</Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(user.id)}>Delete</Button>
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
          <Input label="Username" value={form.formData.username} onChange={(e) => form.setField('username', e.target.value)} required disabled={!!modal.editingItem} />
          <Input label="Full Name" value={form.formData.full_name} onChange={(e) => form.setField('full_name', e.target.value)} required />
          {!modal.editingItem && <>
            <Input label="Email" type="email" value={form.formData.email} onChange={(e) => form.setField('email', e.target.value)} required />
            <Input label="Password" type="password" value={form.formData.password} onChange={(e) => form.setField('password', e.target.value)} required />
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '-10px', marginBottom: '15px' }}>
              Min 8 chars, uppercase, lowercase, and digit required
            </div>
          </>}
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
  const { data: processes, isLoading, error, refetch, setError } = useAsyncData<Process[]>({
    fetchFn: async () => (await processesApi.getProcesses()).sort((a, b) => a.sort_order - b.sort_order),
    initialData: [], errorMessage: 'Failed to load processes'
  });
  const modal = useModalState<Process>();
  const form = useFormState<ProcessFormData>({ process_number: 1, process_code: '', process_name_ko: '', process_name_en: '', description: '', sort_order: 1, is_active: true, estimated_duration_seconds: '', quality_criteria: '{}', auto_print_label: false, label_template_type: null });

  const handleOpenModal = (process?: Process) => {
    process ? form.setFormData({ process_number: process.process_number, process_code: process.process_code, process_name_ko: process.process_name_ko, process_name_en: process.process_name_en, description: process.description || '', sort_order: process.sort_order, is_active: process.is_active, estimated_duration_seconds: process.estimated_duration_seconds ?? '', quality_criteria: JSON.stringify(process.quality_criteria || {}, null, 2), auto_print_label: (process as any).auto_print_label || false, label_template_type: (process as any).label_template_type || null })
      : form.setFormData({ process_number: (processes?.length || 0) + 1, process_code: '', process_name_ko: '', process_name_en: '', description: '', sort_order: (processes?.length || 0) + 1, is_active: true, estimated_duration_seconds: '', quality_criteria: '{}', auto_print_label: false, label_template_type: null });
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
        auto_print_label: form.formData.auto_print_label,
        label_template_type: form.formData.label_template_type || undefined,
      };
      modal.editingItem ? await processesApi.updateProcess(modal.editingItem.id, submitData) : await processesApi.createProcess(submitData);
      modal.close(); refetch();
    } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to save process')); }
  };

  const handleDelete = async (processId: number) => {
    if (!confirm('Are you sure you want to delete this process?')) return;
    try { await processesApi.deleteProcess(processId); refetch(); } catch (err: unknown) { setError(getErrorMessage(err, 'Failed to delete process')); }
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
                    <Button size="small" variant="secondary" onClick={() => handleOpenModal(process)}>Edit</Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(process.id)}>Delete</Button>
                  </div></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </Card>
      <Modal isOpen={modal.isOpen} onClose={modal.close} title={modal.editingItem ? 'Edit Process' : 'Add New Process'}
        footer={<div style={styles.modalFooter}><Button variant="secondary" onClick={modal.close}>Cancel</Button><Button onClick={handleSubmit}>Save</Button></div>}>
        <form onSubmit={handleSubmit}>
          <Input label="Process Number" type="number" value={form.formData.process_number} onChange={(e) => form.setField('process_number', parseInt(e.target.value))} required />
          <Input label="Process Code" value={form.formData.process_code} onChange={(e) => form.setField('process_code', e.target.value)} required placeholder="e.g., LASER_MARKING" />
          <Input label="Process Name (Korean)" value={form.formData.process_name_ko} onChange={(e) => form.setField('process_name_ko', e.target.value)} required />
          <Input label="Process Name (English)" value={form.formData.process_name_en} onChange={(e) => form.setField('process_name_en', e.target.value)} required />
          <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} />
          <Input label="Estimated Duration (sec)" type="number" value={form.formData.estimated_duration_seconds} onChange={(e) => form.setField('estimated_duration_seconds', e.target.value ? parseInt(e.target.value) : '')} placeholder="Optional" />
          <Input label="Sort Order" type="number" value={form.formData.sort_order} onChange={(e) => form.setField('sort_order', parseInt(e.target.value))} required />
          <div style={{ marginBottom: '15px' }}>
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

          {/* Auto Print Label Settings */}
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
            <h4 style={{ marginBottom: '15px', fontSize: '15px', fontWeight: '600', color: 'var(--color-text-primary)' }}>🖨️ 라벨 자동 출력 설정</h4>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.formData.auto_print_label}
                  onChange={(e) => form.setField('auto_print_label', e.target.checked)}
                  style={{ marginRight: '8px', width: '16px', height: '16px', cursor: 'pointer' }}
                />
                <span style={{ fontSize: '14px', fontWeight: '500' }}>완공 시 자동 라벨 출력</span>
              </label>
              <p style={{ marginTop: '5px', marginLeft: '24px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                ✅ 활성화 시: 모든 이전 공정이 PASS인 경우 자동으로 라벨 출력
              </p>
            </div>

            {form.formData.auto_print_label && (
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>라벨 종류</label>
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
                  <option value="">선택하세요</option>
                  <option value="WIP_LABEL">WIP 라벨 (60x30mm, QR코드)</option>
                  <option value="SERIAL_LABEL">Serial 라벨 (60x30mm, QR코드)</option>
                  <option value="LOT_LABEL">LOT 라벨 (60x30mm, QR코드)</option>
                </select>
              </div>
            )}
          </div>

          <div style={styles.checkbox}><label style={styles.checkboxLabel}>
            <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
            <span style={styles.checkboxText}>Active</span>
          </label></div>
        </form>
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
                    <Button size="small" variant="secondary" onClick={() => handleOpenModal(product)}>Edit</Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(product.id)}>Delete</Button>
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
                    <Button size="small" variant="secondary" onClick={() => handleOpenModal(line)}>Edit</Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(line.id)}>Delete</Button>
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
                    <Button size="small" variant="secondary" onClick={() => handleOpenModal(equip)}>Edit</Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(equip.id)}>Delete</Button>
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
            options={[{ value: '', label: '- Select Line -' }, ...productionLines?.map(l => ({ value: l.id, label: l.line_name })) || []]} />
          <Select label="Process" value={form.formData.process_id} onChange={(e) => form.setField('process_id', e.target.value ? parseInt(e.target.value) : '')}
            options={[{ value: '', label: '- Select Process -' }, ...processes?.map(p => ({ value: p.id, label: p.process_name_en })) || []]} />
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
export { UserManagement, ProcessManagement, ProductModelManagement, ProductionLineManagement, EquipmentManagement };
