/**
 * Sequence Upload component with drag-and-drop support.
 */

import { useState, useCallback, useRef } from 'react';
import {
  Upload,
  FileArchive,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  X,
  RefreshCw,
} from 'lucide-react';
import { Button } from '../../atoms/Button';
import { ProgressBar } from '../../atoms/ProgressBar';
import { useUploadSequence, useValidateSequence } from '../../../hooks/useSequences';
import type { ValidationResult, UploadProgress } from '../../../types';

interface SequenceUploadProps {
  onSuccess?: () => void;
  onClose?: () => void;
}

export function SequenceUpload({ onSuccess, onClose }: SequenceUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [forceOverwrite, setForceOverwrite] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateMutation = useValidateSequence();
  const { mutate: upload, progress, isPending, resetProgress } = useUploadSequence();

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const files = e.dataTransfer.files;
      const file = files[0];
      if (file) {
        await handleFileSelect(file);
      }
    },
    []
  );

  const handleFileInputChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      const file = files?.[0];
      if (file) {
        await handleFileSelect(file);
      }
    },
    []
  );

  const handleFileSelect = useCallback(
    async (file: File) => {
      // Validate file type
      if (!file.name.endsWith('.zip')) {
        setValidationResult({
          valid: false,
          errors: [{ field: 'file', message: 'Only .zip files are supported' }],
        });
        return;
      }

      setSelectedFile(file);
      setValidationResult(null);
      resetProgress();

      // Validate the package
      try {
        const result = await validateMutation.mutateAsync(file);
        setValidationResult(result);
      } catch (error) {
        setValidationResult({
          valid: false,
          errors: [
            {
              field: 'validation',
              message: error instanceof Error ? error.message : 'Validation failed',
            },
          ],
        });
      }
    },
    [validateMutation, resetProgress]
  );

  const handleUpload = useCallback(() => {
    if (!selectedFile || !validationResult?.valid) return;

    upload(
      { file: selectedFile, force: forceOverwrite },
      {
        onSuccess: () => {
          onSuccess?.();
        },
      }
    );
  }, [selectedFile, validationResult, forceOverwrite, upload, onSuccess]);

  const handleReset = useCallback(() => {
    setSelectedFile(null);
    setValidationResult(null);
    setForceOverwrite(false);
    resetProgress();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [resetProgress]);

  const handleBrowse = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Upload Sequence Package</h3>
        {onClose && (
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Drop Zone */}
      {!selectedFile && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
            isDragOver
              ? 'border-brand-500 bg-brand-500/10'
              : 'border-zinc-600 hover:border-zinc-500'
          }`}
          onClick={handleBrowse}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={handleFileInputChange}
            className="hidden"
          />
          <Upload className="w-12 h-12 mx-auto text-zinc-500 mb-4" />
          <p className="text-zinc-300 mb-2">Drag and drop a sequence package here</p>
          <p className="text-sm text-zinc-500">or click to browse</p>
          <p className="text-xs text-zinc-600 mt-4">Supported format: .zip</p>
        </div>
      )}

      {/* Selected File Info */}
      {selectedFile && (
        <div className="bg-zinc-900/50 rounded-lg p-4 space-y-4">
          {/* File Info */}
          <div className="flex items-center gap-3">
            <FileArchive className="w-8 h-8 text-brand-500" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-white truncate">{selectedFile.name}</p>
              <p className="text-sm text-zinc-500">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            {progress.stage === 'idle' && (
              <Button variant="ghost" size="sm" onClick={handleReset}>
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Validation Status */}
          {validateMutation.isPending && (
            <div className="flex items-center gap-2 text-zinc-400">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Validating package...</span>
            </div>
          )}

          {validationResult && (
            <ValidationStatus
              result={validationResult}
              onOverwriteChange={setForceOverwrite}
              forceOverwrite={forceOverwrite}
            />
          )}

          {/* Upload Progress */}
          {progress.stage !== 'idle' && (
            <UploadProgressDisplay progress={progress} />
          )}

          {/* Actions */}
          {validationResult?.valid && progress.stage === 'idle' && (
            <div className="flex gap-2 pt-2">
              <Button
                variant="primary"
                onClick={handleUpload}
                disabled={isPending}
                className="flex-1"
              >
                <Upload className="w-4 h-4 mr-2" />
                Install Package
              </Button>
              <Button variant="ghost" onClick={handleReset}>
                Cancel
              </Button>
            </div>
          )}

          {/* Success Actions */}
          {progress.stage === 'complete' && (
            <div className="flex gap-2 pt-2">
              <Button variant="primary" onClick={handleReset} className="flex-1">
                Upload Another
              </Button>
              {onClose && (
                <Button variant="ghost" onClick={onClose}>
                  Close
                </Button>
              )}
            </div>
          )}

          {/* Error Actions */}
          {progress.stage === 'error' && (
            <div className="flex gap-2 pt-2">
              <Button variant="primary" onClick={handleReset} className="flex-1">
                Try Again
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Package Requirements */}
      <div className="text-xs text-zinc-500 space-y-1">
        <p className="font-medium text-zinc-400">Package Requirements:</p>
        <ul className="list-disc list-inside space-y-0.5">
          <li>Must be a valid ZIP archive</li>
          <li>Must contain manifest.yaml with name, version, entry_point</li>
          <li>Must contain the entry_point Python module</li>
          <li>Optional: drivers/, requirements.txt</li>
        </ul>
      </div>
    </div>
  );
}

interface ValidationStatusProps {
  result: ValidationResult;
  forceOverwrite: boolean;
  onOverwriteChange: (value: boolean) => void;
}

function ValidationStatus({ result, forceOverwrite, onOverwriteChange }: ValidationStatusProps) {
  if (result.valid) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-green-400">
          <CheckCircle2 className="w-4 h-4" />
          <span>Package validation passed</span>
        </div>

        {result.manifest && (
          <div className="bg-zinc-800 rounded p-3 space-y-1">
            <p className="text-white font-medium">{result.manifest.displayName || result.manifest.name}</p>
            <p className="text-sm text-zinc-400">
              {result.manifest.name} v{result.manifest.version}
            </p>
            {result.manifest.description && (
              <p className="text-sm text-zinc-500 mt-2">{result.manifest.description}</p>
            )}
          </div>
        )}

        {result.warnings && result.warnings.length > 0 && (
          <div className="space-y-1">
            {result.warnings.map((warning, i) => (
              <div key={i} className="flex items-center gap-2 text-yellow-400 text-sm">
                <AlertTriangle className="w-4 h-4" />
                <span>{warning}</span>
              </div>
            ))}

            {result.warnings.some((w) => w.includes('already exists')) && (
              <label className="flex items-center gap-2 mt-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={forceOverwrite}
                  onChange={(e) => onOverwriteChange(e.target.checked)}
                  className="rounded border-zinc-600 bg-zinc-800 text-brand-500 focus:ring-brand-500"
                />
                <span className="text-sm text-zinc-300">Overwrite existing package</span>
              </label>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-red-400">
        <XCircle className="w-4 h-4" />
        <span>Package validation failed</span>
      </div>

      {result.errors && result.errors.length > 0 && (
        <div className="bg-red-900/20 border border-red-800/50 rounded p-3 space-y-1">
          {result.errors.map((error, i) => (
            <p key={i} className="text-sm text-red-400">
              <span className="font-medium">{error.field}:</span> {error.message}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

interface UploadProgressDisplayProps {
  progress: UploadProgress;
}

function UploadProgressDisplay({ progress }: UploadProgressDisplayProps) {
  const stageIcon = {
    idle: null,
    validating: <RefreshCw className="w-4 h-4 animate-spin" />,
    uploading: <Upload className="w-4 h-4" />,
    complete: <CheckCircle2 className="w-4 h-4 text-green-400" />,
    error: <XCircle className="w-4 h-4 text-red-400" />,
  };

  const stageColor = {
    idle: 'text-zinc-400',
    validating: 'text-zinc-400',
    uploading: 'text-brand-400',
    complete: 'text-green-400',
    error: 'text-red-400',
  };

  return (
    <div className="space-y-2">
      <div className={`flex items-center gap-2 ${stageColor[progress.stage]}`}>
        {stageIcon[progress.stage]}
        <span>{progress.message}</span>
      </div>

      {(progress.stage === 'uploading' || progress.stage === 'validating') && (
        <ProgressBar
          value={progress.progress}
          max={100}
          variant="default"
        />
      )}

      {progress.error && (
        <p className="text-sm text-red-400">{progress.error}</p>
      )}
    </div>
  );
}
