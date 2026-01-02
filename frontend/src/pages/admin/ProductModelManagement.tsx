/**
 * Product Model Management Component
 *
 * Handles CRUD operations for product models including:
 * - Model creation with code and name
 * - Category assignment
 * - Status management (Active, Inactive, Discontinued)
 */

import { productModelsApi } from '@/api';
import { Button, Card, Input, Modal, Select, StatusBadge } from '@/components/common';
import { useAsyncData, useFormState, useModalState } from '@/hooks';
import type { ProductModel } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';

import { defaultProductFormData, getRowStyle, styles, type ProductFormData } from './shared';

export const ProductModelManagement = () => {
  const { message } = App.useApp();
  const { data: products, isLoading, error, refetch } = useAsyncData<ProductModel[]>({
    fetchFn: () => productModelsApi.getProductModels(),
    initialData: [],
    errorMessage: 'Failed to load product models',
  });
  const modal = useModalState<ProductModel>();
  const form = useFormState<ProductFormData>(defaultProductFormData);

  const handleOpenModal = (product?: ProductModel) => {
    if (product) {
      form.setFormData({
        model_code: product.model_code,
        model_name: product.model_name,
        category: product.category || '',
        status: product.status,
      });
    } else {
      form.resetForm();
    }
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
      modal.editingItem
        ? await productModelsApi.updateProductModel(modal.editingItem.id, submitData)
        : await productModelsApi.createProductModel(submitData);
      modal.close();
      refetch();
      message.success('Product model saved successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to save product model');
      message.error(errorMsg, 5);
    }
  };

  const handleDelete = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product model?')) return;
    try {
      await productModelsApi.deleteProductModel(productId);
      refetch();
      message.success('Product model deleted successfully.');
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to delete product model');
      message.error(errorMsg, 5);
    }
  };

  return (
    <>
      <div style={styles.header}>
        <div style={styles.title}>Total Product Models: {products?.length || 0}</div>
        <Button onClick={() => handleOpenModal()}>+ Add Product Model</Button>
      </div>
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading product models...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Code</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Category</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products?.map((product, idx) => (
                  <tr key={product.id} style={getRowStyle(idx)}>
                    <td style={{ ...styles.td, fontWeight: '600' }}>{product.model_code}</td>
                    <td style={{ ...styles.td, fontWeight: '500' }}>{product.model_name}</td>
                    <td
                      style={{
                        ...styles.td,
                        color: 'var(--color-text-secondary)',
                        fontSize: '13px',
                      }}
                    >
                      {product.category || '-'}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={product.status === 'ACTIVE'} />
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleOpenModal(product)}
                        >
                          Edit
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(product.id)}>
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
        title={modal.editingItem ? 'Edit Product Model' : 'Add New Product Model'}
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
            label="Model Code"
            value={form.formData.model_code}
            onChange={(e) => form.setField('model_code', e.target.value)}
            required
            disabled={!!modal.editingItem}
            placeholder="e.g., NH-F2X-001"
          />
          <Input
            label="Model Name"
            value={form.formData.model_name}
            onChange={(e) => form.setField('model_name', e.target.value)}
            required
          />
          <Input
            label="Category"
            value={form.formData.category}
            onChange={(e) => form.setField('category', e.target.value)}
            placeholder="e.g., Standard, Premium"
          />
          <Select
            label="Status"
            value={form.formData.status}
            onChange={(e) =>
              form.setField('status', e.target.value as 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED')
            }
            options={[
              { value: 'ACTIVE', label: 'Active' },
              { value: 'INACTIVE', label: 'Inactive' },
              { value: 'DISCONTINUED', label: 'Discontinued' },
            ]}
          />
        </form>
      </Modal>
    </>
  );
};
