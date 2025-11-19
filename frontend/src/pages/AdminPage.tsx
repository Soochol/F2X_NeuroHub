/**
 * Admin Page - System Administration
 */

import { useState } from 'react';
import { Card, Button, Input, Select, Modal, StatusBadge, RoleBadge } from '@/components/common';
import { useModalState, useFormState, useAsyncData } from '@/hooks';
import { usersApi, processesApi, productModelsApi } from '@/api';
import type { User, Process, ProductModel, UserRole } from '@/types/api';
import { UserRole as UserRoleEnum, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';

type TabType = 'users' | 'processes' | 'products';

interface UserFormData { username: string; full_name: string; email: string; password: string; role: UserRole; is_active: boolean; }
interface ProcessFormData { process_number: number; name: string; description: string; sequence_order: number; is_active: boolean; }
interface ProductFormData { code: string; name: string; description: string; version: string; is_active: boolean; }

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
      </div>
      {activeTab === 'users' && <UserManagement />}
      {activeTab === 'processes' && <ProcessManagement />}
      {activeTab === 'products' && <ProductModelManagement />}
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
    fetchFn: async () => (await processesApi.getProcesses()).sort((a, b) => a.sequence_order - b.sequence_order),
    initialData: [], errorMessage: 'Failed to load processes'
  });
  const modal = useModalState<Process>();
  const form = useFormState<ProcessFormData>({ process_number: 1, name: '', description: '', sequence_order: 1, is_active: true });

  const handleOpenModal = (process?: Process) => {
    process ? form.setFormData({ process_number: process.process_number, name: process.name, description: process.description || '', sequence_order: process.sequence_order, is_active: process.is_active })
      : form.setFormData({ process_number: (processes?.length || 0) + 1, name: '', description: '', sequence_order: (processes?.length || 0) + 1, is_active: true });
    modal.open(process);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      modal.editingItem ? await processesApi.updateProcess(modal.editingItem.id, form.formData) : await processesApi.createProcess(form.formData);
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
                  <td style={{ ...styles.td, fontWeight: '500' }}>{process.name}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{process.description || '-'}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}>{process.sequence_order}</td>
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
          <Input label="Process Name" value={form.formData.name} onChange={(e) => form.setField('name', e.target.value)} required />
          <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} />
          <Input label="Sequence Order" type="number" value={form.formData.sequence_order} onChange={(e) => form.setField('sequence_order', parseInt(e.target.value))} required />
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
  const form = useFormState<ProductFormData>({ code: '', name: '', description: '', version: '1.0', is_active: true });

  const handleOpenModal = (product?: ProductModel) => {
    product ? form.setFormData({ code: product.code, name: product.name, description: product.description || '', version: product.version, is_active: product.is_active }) : form.resetForm();
    modal.open(product);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      modal.editingItem ? await productModelsApi.updateProductModel(modal.editingItem.id, form.formData) : await productModelsApi.createProductModel(form.formData);
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
                <th style={{ ...styles.th, textAlign: 'left' }}>Description</th><th style={{ ...styles.th, textAlign: 'center' }}>Version</th>
                <th style={{ ...styles.th, textAlign: 'center' }}>Status</th><th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
              </tr></thead>
              <tbody>{products?.map((product, idx) => (
                <tr key={product.id} style={getRowStyle(idx)}>
                  <td style={{ ...styles.td, fontWeight: '600' }}>{product.code}</td><td style={{ ...styles.td, fontWeight: '500' }}>{product.name}</td>
                  <td style={{ ...styles.td, color: 'var(--color-text-secondary)', fontSize: '13px' }}>{product.description || '-'}</td>
                  <td style={{ ...styles.td, textAlign: 'center', fontWeight: '500' }}>{product.version}</td>
                  <td style={{ ...styles.td, textAlign: 'center' }}><StatusBadge isActive={product.is_active} /></td>
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
          <Input label="Product Code" value={form.formData.code} onChange={(e) => form.setField('code', e.target.value)} required disabled={!!modal.editingItem} />
          <Input label="Product Name" value={form.formData.name} onChange={(e) => form.setField('name', e.target.value)} required />
          <Input label="Description" value={form.formData.description} onChange={(e) => form.setField('description', e.target.value)} />
          <Input label="Version" value={form.formData.version} onChange={(e) => form.setField('version', e.target.value)} required />
          <div style={styles.checkbox}><label style={styles.checkboxLabel}>
            <input type="checkbox" checked={form.formData.is_active} onChange={(e) => form.setField('is_active', e.target.checked)} style={styles.checkboxInput} />
            <span style={styles.checkboxText}>Active</span>
          </label></div>
        </form>
      </Modal>
    </>
  );
};
