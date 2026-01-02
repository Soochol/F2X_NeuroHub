/**
 * User Management Component
 *
 * Handles CRUD operations for system users including:
 * - User creation with validation
 * - Role assignment (Admin, Manager, Operator)
 * - Active/Inactive status management
 */

import { usersApi } from '@/api';
import { Button, Card, Input, Modal, RoleBadge, Select, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { User, UserRole } from '@/types/api';
import { UserRole as UserRoleEnum, getErrorMessage } from '@/types/api';
import { App } from 'antd';
import { format } from 'date-fns';

import { defaultUserFormData, getRowStyle, styles, type UserFormData } from './shared';

export const UserManagement = () => {
  const { message } = App.useApp();
  const { data: users, isLoading, error, refetch } = useAsyncData<User[]>({
    fetchFn: () => usersApi.getUsers(),
    initialData: [],
    errorMessage: 'Failed to load users',
  });
  const modal = useModalState<User>();
  const form = useFormState<UserFormData>(defaultUserFormData);

  const handleOpenModal = (user?: User) => {
    if (user) {
      form.setFormData({
        username: user.username,
        full_name: user.full_name,
        email: '',
        password: '',
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      form.resetForm();
    }
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
        ? await usersApi.updateUser(modal.editingItem.id, {
            full_name: form.formData.full_name,
            role: form.formData.role,
            is_active: form.formData.is_active,
          })
        : await usersApi.createUser(form.formData);
      modal.close();
      form.resetForm();
      refetch();
      message.success(modal.editingItem ? 'User updated successfully' : 'User created successfully');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save user');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await usersApi.deleteUser(userId);
      refetch();
      message.success('User deleted successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to delete user');
      message.error(errorMsg, 5);
    }
  };

  return (
    <>
      <div style={styles.header}>
        <div style={styles.title}>Total Users: {users?.length || 0}</div>
        <Button onClick={() => handleOpenModal()}>+ Add User</Button>
      </div>
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading users...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Username</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Full Name</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Role</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Created</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users?.map((user, idx) => (
                  <tr key={user.id} style={getRowStyle(idx)}>
                    <td style={{ ...styles.td, fontWeight: '500' }}>{user.username}</td>
                    <td style={styles.td}>{user.full_name}</td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <RoleBadge role={user.role} />
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={user.is_active} />
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        textAlign: 'center',
                        fontSize: '13px',
                        color: 'var(--color-text-secondary)',
                      }}
                    >
                      {format(new Date(user.created_at), 'yyyy-MM-dd')}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button size="sm" variant="secondary" onClick={() => handleOpenModal(user)}>
                          Edit
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(user.id)}>
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
        title={modal.editingItem ? 'Edit User' : 'Add New User'}
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
            label="User ID"
            value={form.formData.username}
            onChange={(e) => form.setField('username', e.target.value)}
            required
            disabled={!!modal.editingItem}
          />
          {!modal.editingItem && (
            <>
              <Input
                label="Password"
                type="password"
                value={form.formData.password}
                onChange={(e) => form.setField('password', e.target.value)}
                required
              />
              <div
                style={{
                  fontSize: '12px',
                  color: 'var(--color-text-secondary)',
                  marginTop: '-10px',
                  marginBottom: '15px',
                }}
              >
                Min 4 characters
              </div>
            </>
          )}
          <Input
            label="Full Name"
            value={form.formData.full_name}
            onChange={(e) => form.setField('full_name', e.target.value)}
            required
          />
          {!modal.editingItem && (
            <Input
              label="Email (optional)"
              type="email"
              value={form.formData.email}
              onChange={(e) => form.setField('email', e.target.value)}
            />
          )}
          <Select
            label="Role"
            value={form.formData.role}
            onChange={(e) => form.setField('role', e.target.value as UserRole)}
            options={[
              { value: UserRoleEnum.ADMIN, label: 'Admin' },
              { value: UserRoleEnum.MANAGER, label: 'Manager' },
              { value: UserRoleEnum.OPERATOR, label: 'Operator' },
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
