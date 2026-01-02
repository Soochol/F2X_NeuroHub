/**
 * Sequence Management Component
 *
 * Handles CRUD operations for test sequences including:
 * - Sequence listing
 * - ZIP package upload
 * - Metadata editing
 * - Deployment to stations
 */

import { sequencesApi, type Sequence, type SequenceDetail } from '@/api/endpoints/sequences';
import { Button, Card, Modal, StatusBadge } from '@/components/common';
import { useAsyncData, useModalState } from '@/hooks';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';
import { useCallback, useRef, useState } from 'react';

import { getRowStyle, styles } from './shared';

// Format bytes to human readable
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Format date to localized string
const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const SequenceManagement = () => {
  const { message } = App.useApp();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const detailModal = useModalState<SequenceDetail>();
  const [selectedSequence, setSelectedSequence] = useState<SequenceDetail | null>(null);

  const {
    data: sequences,
    isLoading,
    error,
    refetch,
  } = useAsyncData<Sequence[]>({
    fetchFn: async () => {
      const response = await sequencesApi.getSequences();
      return response.items || [];
    },
    initialData: [],
    errorMessage: 'Failed to load sequences',
  });

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.endsWith('.zip')) {
        message.error('Only ZIP files are allowed');
        return;
      }

      setUploading(true);
      try {
        const result = await sequencesApi.uploadSequence(file, false);
        message.success(result.message || `Sequence "${result.name}" v${result.version} uploaded`);
        refetch();
      } catch (err: unknown) {
        const errorMsg = getErrorMessage(err, 'Failed to upload sequence');
        if (errorMsg.includes('already exists')) {
          // Ask user if they want to force update
          if (confirm(`Sequence already exists. Do you want to overwrite it?`)) {
            try {
              const result = await sequencesApi.uploadSequence(file, true);
              message.success(
                result.message || `Sequence "${result.name}" updated to v${result.version}`
              );
              refetch();
            } catch (forceErr: unknown) {
              message.error(getErrorMessage(forceErr, 'Failed to overwrite sequence'));
            }
          }
        } else {
          message.error(errorMsg);
        }
      } finally {
        setUploading(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    },
    [message, refetch]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleViewDetail = async (name: string) => {
    try {
      const detail = await sequencesApi.getSequence(name);
      setSelectedSequence(detail);
      detailModal.open(detail);
    } catch (err: unknown) {
      message.error(getErrorMessage(err, 'Failed to load sequence details'));
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete sequence "${name}"?`)) return;
    try {
      await sequencesApi.deleteSequence(name);
      refetch();
      message.success(`Sequence "${name}" deleted successfully`);
    } catch (err: unknown) {
      message.error(getErrorMessage(err, 'Failed to delete sequence'));
    }
  };

  const handleToggleActive = async (seq: Sequence) => {
    try {
      await sequencesApi.updateSequence(seq.name, { is_active: !seq.is_active });
      refetch();
      message.success(`Sequence "${seq.name}" ${!seq.is_active ? 'activated' : 'deactivated'}`);
    } catch (err: unknown) {
      message.error(getErrorMessage(err, 'Failed to update sequence'));
    }
  };

  return (
    <>
      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragActive ? 'var(--color-brand)' : 'var(--color-border)'}`,
          borderRadius: '12px',
          padding: '30px',
          textAlign: 'center',
          marginBottom: '20px',
          backgroundColor: dragActive ? 'var(--color-bg-secondary)' : 'transparent',
          transition: 'all 0.2s',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        <div style={{ marginBottom: '15px' }}>
          <span style={{ fontSize: '40px' }}>📦</span>
        </div>
        <div style={{ marginBottom: '10px', color: 'var(--color-text-primary)', fontWeight: '500' }}>
          Drag & Drop sequence ZIP file here
        </div>
        <div style={{ marginBottom: '15px', color: 'var(--color-text-secondary)', fontSize: '13px' }}>
          or
        </div>
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          style={{ minWidth: '150px' }}
        >
          {uploading ? 'Uploading...' : 'Select ZIP File'}
        </Button>
      </div>

      {/* Sequence List */}
      <div style={styles.header}>
        <div style={styles.title}>
          Total Sequences: {sequences?.length || 0}
        </div>
        <Button onClick={refetch} variant="secondary" size="sm">
          Refresh
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading sequences...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : sequences?.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            No sequences uploaded yet. Upload a ZIP package to get started.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Version</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Description</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Size</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Updated</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sequences?.map((seq, idx) => (
                  <tr key={seq.id} style={getRowStyle(idx)}>
                    <td style={{ ...styles.td, fontWeight: '600' }}>
                      {seq.display_name || seq.name}
                      {seq.display_name && (
                        <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                          {seq.name}
                        </div>
                      )}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <span
                        style={{
                          backgroundColor: 'var(--color-bg-secondary)',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '13px',
                          fontFamily: 'monospace',
                        }}
                      >
                        v{seq.version}
                      </span>
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        color: 'var(--color-text-secondary)',
                        fontSize: '13px',
                        maxWidth: '250px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {seq.description || '-'}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center', fontSize: '13px' }}>
                      {formatBytes(seq.package_size)}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <StatusBadge isActive={seq.is_active} />
                      {seq.is_deprecated && (
                        <span
                          style={{
                            marginLeft: '6px',
                            backgroundColor: 'var(--color-warning-bg, #fef3c7)',
                            color: 'var(--color-warning, #d97706)',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '11px',
                          }}
                        >
                          Deprecated
                        </span>
                      )}
                    </td>
                    <td
                      style={{
                        ...styles.td,
                        textAlign: 'center',
                        fontSize: '12px',
                        color: 'var(--color-text-secondary)',
                      }}
                    >
                      {formatDate(seq.updated_at)}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <div style={styles.actions}>
                        <Button size="sm" variant="secondary" onClick={() => handleViewDetail(seq.name)}>
                          View
                        </Button>
                        <Button
                          size="sm"
                          variant={seq.is_active ? 'secondary' : 'primary'}
                          onClick={() => handleToggleActive(seq)}
                        >
                          {seq.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => handleDelete(seq.name)}>
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

      {/* Detail Modal */}
      <Modal
        isOpen={detailModal.isOpen}
        onClose={() => {
          detailModal.close();
          setSelectedSequence(null);
        }}
        title={`Sequence: ${selectedSequence?.display_name || selectedSequence?.name || ''}`}
        footer={
          <div style={styles.modalFooter}>
            <Button variant="secondary" onClick={detailModal.close}>
              Close
            </Button>
          </div>
        }
      >
        {selectedSequence && (
          <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
            {/* Basic Info */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '15px',
                marginBottom: '20px',
              }}
            >
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Name</label>
                <div style={{ fontWeight: '500' }}>{selectedSequence.name}</div>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Version</label>
                <div style={{ fontWeight: '500' }}>v{selectedSequence.version}</div>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Checksum</label>
                <div
                  style={{
                    fontFamily: 'monospace',
                    fontSize: '11px',
                    wordBreak: 'break-all',
                  }}
                >
                  {selectedSequence.checksum}
                </div>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Package Size
                </label>
                <div>{formatBytes(selectedSequence.package_size)}</div>
              </div>
            </div>

            {/* Description */}
            {selectedSequence.description && (
              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Description
                </label>
                <div
                  style={{
                    padding: '10px',
                    backgroundColor: 'var(--color-bg-secondary)',
                    borderRadius: '6px',
                    marginTop: '4px',
                  }}
                >
                  {selectedSequence.description}
                </div>
              </div>
            )}

            {/* Steps */}
            {selectedSequence.steps && selectedSequence.steps.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Steps ({selectedSequence.steps.length})
                </label>
                <div
                  style={{
                    marginTop: '8px',
                    border: '1px solid var(--color-border)',
                    borderRadius: '8px',
                    overflow: 'hidden',
                  }}
                >
                  {selectedSequence.steps.map((step, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '10px 15px',
                        borderBottom:
                          idx < selectedSequence.steps!.length - 1
                            ? '1px solid var(--color-border)'
                            : 'none',
                        backgroundColor: idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span
                          style={{
                            backgroundColor: 'var(--color-brand)',
                            color: 'white',
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            fontWeight: '600',
                          }}
                        >
                          {idx + 1}
                        </span>
                        <span style={{ fontWeight: '500' }}>{String(step.name || `Step ${idx + 1}`)}</span>
                        {step.timeout != null && (
                          <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                            (timeout: {String(step.timeout)}s)
                          </span>
                        )}
                      </div>
                      {step.description != null && (
                        <div
                          style={{
                            marginLeft: '34px',
                            fontSize: '13px',
                            color: 'var(--color-text-secondary)',
                          }}
                        >
                          {String(step.description)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Hardware Requirements */}
            {selectedSequence.hardware && Object.keys(selectedSequence.hardware).length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Hardware Requirements
                </label>
                <pre
                  style={{
                    marginTop: '8px',
                    padding: '10px',
                    backgroundColor: 'var(--color-bg-secondary)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    overflow: 'auto',
                  }}
                >
                  {JSON.stringify(selectedSequence.hardware, null, 2)}
                </pre>
              </div>
            )}

            {/* Parameters */}
            {selectedSequence.parameters && Object.keys(selectedSequence.parameters).length > 0 && (
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  Parameters
                </label>
                <pre
                  style={{
                    marginTop: '8px',
                    padding: '10px',
                    backgroundColor: 'var(--color-bg-secondary)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    overflow: 'auto',
                  }}
                >
                  {JSON.stringify(selectedSequence.parameters, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </>
  );
};
