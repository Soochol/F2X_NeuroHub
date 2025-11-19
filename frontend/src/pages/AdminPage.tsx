/**
 * Admin Page - System Administration
 */

import { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { Modal } from '@/components/common/Modal';
import { usersApi, processesApi, productModelsApi } from '@/api';
import type { User, Process, ProductModel, UserRole } from '@/types/api';
import { UserRole as UserRoleEnum } from '@/types/api';
import { format } from 'date-fns';

type TabType = 'users' | 'processes' | 'products';

export const AdminPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('users');

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>Administration</h1>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e0e0e0' }}>
        <button
          onClick={() => setActiveTab('users')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'users' ? '#3498db' : 'transparent',
            color: activeTab === 'users' ? 'white' : '#7f8c8d',
            border: 'none',
            borderBottom: activeTab === 'users' ? '3px solid #2980b9' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'users' ? 'bold' : 'normal',
            fontSize: '15px',
            transition: 'all 0.2s',
          }}
        >
          👥 User Management
        </button>
        <button
          onClick={() => setActiveTab('processes')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'processes' ? '#3498db' : 'transparent',
            color: activeTab === 'processes' ? 'white' : '#7f8c8d',
            border: 'none',
            borderBottom: activeTab === 'processes' ? '3px solid #2980b9' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'processes' ? 'bold' : 'normal',
            fontSize: '15px',
            transition: 'all 0.2s',
          }}
        >
          ⚙️ Process Management
        </button>
        <button
          onClick={() => setActiveTab('products')}
          style={{
            padding: '12px 24px',
            backgroundColor: activeTab === 'products' ? '#3498db' : 'transparent',
            color: activeTab === 'products' ? 'white' : '#7f8c8d',
            border: 'none',
            borderBottom: activeTab === 'products' ? '3px solid #2980b9' : 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'products' ? 'bold' : 'normal',
            fontSize: '15px',
            transition: 'all 0.2s',
          }}
        >
          📦 Product Models
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && <UserManagement />}
      {activeTab === 'processes' && <ProcessManagement />}
      {activeTab === 'products' && <ProductModelManagement />}
    </div>
  );
};

// ============================================================================
// User Management Component
// ============================================================================
const UserManagement = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    email: '',
    password: '',
    role: UserRoleEnum.OPERATOR as UserRole,
    is_active: true,
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await usersApi.getUsers();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        full_name: user.full_name,
        email: '',
        password: '',
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        full_name: '',
        email: '',
        password: '',
        role: UserRoleEnum.OPERATOR,
        is_active: true,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingUser(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await usersApi.updateUser(editingUser.id, {
          full_name: formData.full_name,
          role: formData.role,
          is_active: formData.is_active,
        });
      } else {
        await usersApi.createUser({
          username: formData.username,
          full_name: formData.full_name,
          email: formData.email,
          password: formData.password,
          role: formData.role,
          is_active: formData.is_active,
        });
      }
      handleCloseModal();
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to save user');
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await usersApi.deleteUser(userId);
      fetchUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to delete user');
    }
  };

  const getRoleBadgeColor = (role: UserRole) => {
    switch (role) {
      case UserRoleEnum.ADMIN:
        return { bg: '#e74c3c', color: 'white' };
      case UserRoleEnum.MANAGER:
        return { bg: '#f39c12', color: 'white' };
      case UserRoleEnum.OPERATOR:
        return { bg: '#3498db', color: 'white' };
      default:
        return { bg: '#95a5a6', color: 'white' };
    }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#2c3e50' }}>
          Total Users: {users.length}
        </div>
        <Button onClick={() => handleOpenModal()}>+ Add User</Button>
      </div>

      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading users...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Username</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Full Name</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Role</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Created</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, idx) => {
                  const roleBadge = getRoleBadgeColor(user.role);
                  return (
                    <tr
                      key={user.id}
                      style={{
                        borderBottom: '1px solid #f0f0f0',
                        backgroundColor: idx % 2 === 0 ? 'white' : '#f9f9f9',
                      }}
                    >
                      <td style={{ padding: '12px', fontWeight: '500' }}>{user.username}</td>
                      <td style={{ padding: '12px' }}>{user.full_name}</td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span
                          style={{
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '500',
                            ...roleBadge,
                          }}
                        >
                          {user.role}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span
                          style={{
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '500',
                            backgroundColor: user.is_active ? '#d5f4e6' : '#fee',
                            color: user.is_active ? '#27ae60' : '#e74c3c',
                          }}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px', color: '#7f8c8d' }}>
                        {format(new Date(user.created_at), 'yyyy-MM-dd')}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                          <Button size="small" variant="secondary" onClick={() => handleOpenModal(user)}>
                            Edit
                          </Button>
                          <Button size="small" variant="danger" onClick={() => handleDelete(user.id)}>
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* User Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingUser ? 'Edit User' : 'Add New User'}
        footer={
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Save</Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit}>
          <Input
            label="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            required
            disabled={!!editingUser}
          />
          <Input
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
          />
          {!editingUser && (
            <>
              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
              <Input
                label="Password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </>
          )}
          <Select
            label="Role"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
            options={[
              { value: UserRoleEnum.ADMIN, label: 'Admin' },
              { value: UserRoleEnum.MANAGER, label: 'Manager' },
              { value: UserRoleEnum.OPERATOR, label: 'Operator' },
            ]}
          />
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                style={{ width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Active</span>
            </label>
          </div>
        </form>
      </Modal>
    </>
  );
};

// ============================================================================
// Process Management Component
// ============================================================================
const ProcessManagement = () => {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProcess, setEditingProcess] = useState<Process | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    process_number: 1,
    name: '',
    description: '',
    sequence_order: 1,
    is_active: true,
  });

  useEffect(() => {
    fetchProcesses();
  }, []);

  const fetchProcesses = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await processesApi.getProcesses();
      setProcesses(data.sort((a, b) => a.sequence_order - b.sequence_order));
    } catch (err: any) {
      setError(err.message || 'Failed to load processes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = (process?: Process) => {
    if (process) {
      setEditingProcess(process);
      setFormData({
        process_number: process.process_number,
        name: process.name,
        description: process.description || '',
        sequence_order: process.sequence_order,
        is_active: process.is_active,
      });
    } else {
      setEditingProcess(null);
      setFormData({
        process_number: processes.length + 1,
        name: '',
        description: '',
        sequence_order: processes.length + 1,
        is_active: true,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProcess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingProcess) {
        await processesApi.updateProcess(editingProcess.id, formData);
      } else {
        await processesApi.createProcess(formData);
      }
      handleCloseModal();
      fetchProcesses();
    } catch (err: any) {
      alert(err.message || 'Failed to save process');
    }
  };

  const handleDelete = async (processId: number) => {
    if (!confirm('Are you sure you want to delete this process?')) return;
    try {
      await processesApi.deleteProcess(processId);
      fetchProcesses();
    } catch (err: any) {
      alert(err.message || 'Failed to delete process');
    }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#2c3e50' }}>
          Total Processes: {processes.length}
        </div>
        <Button onClick={() => handleOpenModal()}>+ Add Process</Button>
      </div>

      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading processes...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Process #</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Name</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Description</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Sequence</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {processes.map((process, idx) => (
                  <tr
                    key={process.id}
                    style={{
                      borderBottom: '1px solid #f0f0f0',
                      backgroundColor: idx % 2 === 0 ? 'white' : '#f9f9f9',
                    }}
                  >
                    <td style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '16px' }}>
                      {process.process_number}
                    </td>
                    <td style={{ padding: '12px', fontWeight: '500' }}>{process.name}</td>
                    <td style={{ padding: '12px', color: '#7f8c8d', fontSize: '13px' }}>
                      {process.description || '-'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>{process.sequence_order}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span
                        style={{
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '500',
                          backgroundColor: process.is_active ? '#d5f4e6' : '#fee',
                          color: process.is_active ? '#27ae60' : '#e74c3c',
                        }}
                      >
                        {process.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <Button size="small" variant="secondary" onClick={() => handleOpenModal(process)}>
                          Edit
                        </Button>
                        <Button size="small" variant="danger" onClick={() => handleDelete(process.id)}>
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

      {/* Process Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingProcess ? 'Edit Process' : 'Add New Process'}
        footer={
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Save</Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit}>
          <Input
            label="Process Number"
            type="number"
            value={formData.process_number}
            onChange={(e) => setFormData({ ...formData, process_number: parseInt(e.target.value) })}
            required
          />
          <Input
            label="Process Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <Input
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <Input
            label="Sequence Order"
            type="number"
            value={formData.sequence_order}
            onChange={(e) => setFormData({ ...formData, sequence_order: parseInt(e.target.value) })}
            required
          />
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                style={{ width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Active</span>
            </label>
          </div>
        </form>
      </Modal>
    </>
  );
};

// ============================================================================
// Product Model Management Component
// ============================================================================
const ProductModelManagement = () => {
  const [products, setProducts] = useState<ProductModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ProductModel | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    version: '',
    is_active: true,
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await productModelsApi.getProductModels();
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load product models');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = (product?: ProductModel) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        code: product.code,
        name: product.name,
        description: product.description || '',
        version: product.version,
        is_active: product.is_active,
      });
    } else {
      setEditingProduct(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        version: '1.0',
        is_active: true,
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        await productModelsApi.updateProductModel(editingProduct.id, formData);
      } else {
        await productModelsApi.createProductModel(formData);
      }
      handleCloseModal();
      fetchProducts();
    } catch (err: any) {
      alert(err.message || 'Failed to save product model');
    }
  };

  const handleDelete = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product model?')) return;
    try {
      await productModelsApi.deleteProductModel(productId);
      fetchProducts();
    } catch (err: any) {
      alert(err.message || 'Failed to delete product model');
    }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#2c3e50' }}>
          Total Product Models: {products.length}
        </div>
        <Button onClick={() => handleOpenModal()}>+ Add Product Model</Button>
      </div>

      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading product models...</div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Code</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Name</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Description</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Version</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product, idx) => (
                  <tr
                    key={product.id}
                    style={{
                      borderBottom: '1px solid #f0f0f0',
                      backgroundColor: idx % 2 === 0 ? 'white' : '#f9f9f9',
                    }}
                  >
                    <td style={{ padding: '12px', fontWeight: '600' }}>{product.code}</td>
                    <td style={{ padding: '12px', fontWeight: '500' }}>{product.name}</td>
                    <td style={{ padding: '12px', color: '#7f8c8d', fontSize: '13px' }}>
                      {product.description || '-'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontWeight: '500' }}>{product.version}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span
                        style={{
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '500',
                          backgroundColor: product.is_active ? '#d5f4e6' : '#fee',
                          color: product.is_active ? '#27ae60' : '#e74c3c',
                        }}
                      >
                        {product.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <Button size="small" variant="secondary" onClick={() => handleOpenModal(product)}>
                          Edit
                        </Button>
                        <Button size="small" variant="danger" onClick={() => handleDelete(product.id)}>
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

      {/* Product Model Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingProduct ? 'Edit Product Model' : 'Add New Product Model'}
        footer={
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Save</Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit}>
          <Input
            label="Product Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            required
            disabled={!!editingProduct}
          />
          <Input
            label="Product Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <Input
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <Input
            label="Version"
            value={formData.version}
            onChange={(e) => setFormData({ ...formData, version: e.target.value })}
            required
          />
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                style={{ width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Active</span>
            </label>
          </div>
        </form>
      </Modal>
    </>
  );
};
