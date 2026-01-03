/**
 * Sequence Management Component
 *
 * Handles CRUD operations for test sequences including:
 * - Sequence listing
 * - ZIP package upload (collapsible)
 * - Metadata editing
 * - Deployment to stations
 */

import { sequencesApi, type Sequence, type SequenceDetail } from '@/api/endpoints/sequences';
import { Button, Card, Modal, StatusBadge } from '@/components/common';
import { useAsyncData, useModalState } from '@/hooks';
import { getErrorMessage } from '@/types/api';
import { App } from 'antd';
import JSZip from 'jszip';
import { useCallback, useEffect, useRef, useState } from 'react';

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

// Create ZIP from folder files
const createZipFromFiles = async (files: FileList): Promise<File> => {
  const zip = new JSZip();

  // Find common root folder name
  const firstFilePath = files[0].webkitRelativePath;
  const rootFolder = firstFilePath.split('/')[0];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const relativePath = file.webkitRelativePath;
    // Remove the root folder from the path to avoid double nesting
    const pathWithoutRoot = relativePath.substring(rootFolder.length + 1);
    const content = await file.arrayBuffer();
    zip.file(pathWithoutRoot, content);
  }

  const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
  return new File([blob], `${rootFolder}.zip`, { type: 'application/zip' });
};

export const SequenceManagement = () => {
  const { message } = App.useApp();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);
  const [showUploadMenu, setShowUploadMenu] = useState(false);
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

  // Global drag event listeners for visual feedback
  useEffect(() => {
    const handleDragEnter = (e: DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer?.types.includes('Files')) {
        setDragActive(true);
      }
    };

    const handleDragLeave = (e: DragEvent) => {
      e.preventDefault();
      if (e.relatedTarget === null) {
        setDragActive(false);
      }
    };

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      setDragActive(false);
    };

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('drop', handleDrop);
    };
  }, []);

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.endsWith('.zip')) {
        message.error('Only ZIP files are allowed');
        return;
      }

      setUploading(true);
      setUploadStatus('Uploading...');
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
        setUploadStatus('');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        if (folderInputRef.current) {
          folderInputRef.current.value = '';
        }
      }
    },
    [message, refetch]
  );

  const handleFolderSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (!files || files.length === 0) return;

      setUploading(true);
      setUploadStatus('Creating ZIP from folder...');
      try {
        const zipFile = await createZipFromFiles(files);
        setUploadStatus('Uploading...');
        await handleUpload(zipFile);
      } catch (err: unknown) {
        message.error(getErrorMessage(err, 'Failed to create ZIP from folder'));
        setUploading(false);
        setUploadStatus('');
      }
    },
    [handleUpload, message]
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
    <div ref={containerRef}>
      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".zip"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      <input
        ref={folderInputRef}
        type="file"
        // @ts-expect-error webkitdirectory is not in React types but works in browsers
        webkitdirectory=""
        directory=""
        multiple
        onChange={handleFolderSelect}
        style={{ display: 'none' }}
      />

      {/* Header with Upload Button */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h2
            style={{
              fontSize: '18px',
              fontWeight: '600',
              color: 'var(--color-text-primary)',
              margin: 0,
            }}
          >
            Test Sequences
          </h2>
          <span
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              color: 'var(--color-text-secondary)',
              padding: '2px 10px',
              borderRadius: '12px',
              fontSize: '13px',
              fontWeight: '500',
            }}
          >
            {sequences?.length || 0}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <Button onClick={refetch} variant="secondary" size="sm">
            ⟳ Refresh
          </Button>
        </div>
      </div>

      {/* Upload Area */}
      <div
        style={{
          marginBottom: '16px',
        }}
      >
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? 'var(--color-brand)' : 'var(--color-border)'}`,
            borderRadius: '12px',
            padding: '24px',
            textAlign: 'center',
            backgroundColor: dragActive ? 'var(--color-bg-secondary)' : 'var(--color-bg-primary)',
            transition: 'all 0.2s',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
            <span style={{ fontSize: '36px' }}>📦</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ color: 'var(--color-text-primary)', fontWeight: '500', marginBottom: '4px' }}>
                Drag & Drop sequence package here
              </div>
              <div style={{ color: 'var(--color-text-tertiary)', fontSize: '13px' }}>
                Supports ZIP files or folders (auto-compressed)
              </div>
            </div>
            <div style={{ borderLeft: '1px solid var(--color-border)', height: '40px', margin: '0 8px' }} />

            {uploading && uploadStatus ? (
              <div style={{ color: 'var(--color-brand)', fontWeight: '500', minWidth: '150px' }}>
                {uploadStatus}
              </div>
            ) : (
              <div style={{ position: 'relative' }}>
                <Button
                  onClick={() => setShowUploadMenu(!showUploadMenu)}
                  disabled={uploading}
                  style={{ minWidth: '150px' }}
                >
                  Select File / Folder ▾
                </Button>

                {showUploadMenu && !uploading && (
                  <>
                    {/* Backdrop */}
                    <div
                      onClick={() => setShowUploadMenu(false)}
                      style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        zIndex: 99,
                      }}
                    />
                    {/* Dropdown menu */}
                    <div
                      style={{
                        position: 'absolute',
                        top: '100%',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        marginTop: '4px',
                        backgroundColor: 'var(--color-bg-primary)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        zIndex: 100,
                        minWidth: '180px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        onClick={() => {
                          fileInputRef.current?.click();
                          setShowUploadMenu(false);
                        }}
                        style={{
                          padding: '12px 16px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          borderBottom: '1px solid var(--color-border)',
                          transition: 'background-color 0.15s',
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)')
                        }
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                      >
                        <span style={{ fontSize: '18px' }}>📄</span>
                        <div>
                          <div style={{ fontWeight: '500', color: 'var(--color-text-primary)' }}>
                            ZIP File
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-text-tertiary)' }}>
                            Select .zip package
                          </div>
                        </div>
                      </div>
                      <div
                        onClick={() => {
                          folderInputRef.current?.click();
                          setShowUploadMenu(false);
                        }}
                        style={{
                          padding: '12px 16px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          transition: 'background-color 0.15s',
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)')
                        }
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                      >
                        <span style={{ fontSize: '18px' }}>📁</span>
                        <div>
                          <div style={{ fontWeight: '500', color: 'var(--color-text-primary)' }}>
                            Folder
                          </div>
                          <div style={{ fontSize: '11px', color: 'var(--color-text-tertiary)' }}>
                            Auto-compress to ZIP
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sequence List */}
      <Card>
        {isLoading ? (
          <div style={styles.loading}>Loading sequences...</div>
        ) : error ? (
          <div style={styles.error}>{error}</div>
        ) : sequences?.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              color: 'var(--color-text-secondary)',
            }}
          >
            <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: '8px' }}>
              No sequences uploaded yet
            </div>
            <div style={{ fontSize: '14px' }}>
              Use the upload area above to add your first sequence
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Name</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '80px' }}>Version</th>
                  <th style={{ ...styles.th, textAlign: 'left' }}>Description</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '80px' }}>Size</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '100px' }}>Status</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '140px' }}>Created</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '140px' }}>Updated</th>
                  <th style={{ ...styles.th, textAlign: 'center', width: '200px' }}>Actions</th>
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
                        maxWidth: '300px',
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
                      {formatDate(seq.created_at)}
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
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Created</label>
                <div style={{ fontSize: '13px' }}>{formatDate(selectedSequence.created_at)}</div>
              </div>
              <div>
                <label style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Updated</label>
                <div style={{ fontSize: '13px' }}>{formatDate(selectedSequence.updated_at)}</div>
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
                        backgroundColor:
                          idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)',
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
    </div>
  );
};
