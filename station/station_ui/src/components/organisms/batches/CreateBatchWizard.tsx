/**
 * Create Batch Wizard Modal.
 * Multi-step wizard for creating and configuring batches.
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import {
  X,
  ChevronLeft,
  ChevronRight,
  Check,
  GripVertical,
  Plus,
  Minus,
  AlertCircle,
} from 'lucide-react';
import { Button } from '../../atoms/Button';
import { Input } from '../../atoms/Input';
import { Select } from '../../atoms/Select';
import { useWorkflowConfig, useProcesses } from '../../../hooks';
import type {
  SequenceSummary,
  SequencePackage,
  ParameterSchema,
  StepSchema,
  CreateBatchRequest,
} from '../../../types';
import type { ProcessInfo } from '../../../api/endpoints/system';

export interface CreateBatchWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (request: CreateBatchRequest) => void;
  sequences: SequenceSummary[];
  getSequenceDetail: (name: string) => Promise<SequencePackage>;
  isSubmitting?: boolean;
}

type WizardStep = 'sequence' | 'steps' | 'parameters' | 'quantity' | 'review';

const WIZARD_STEPS: { key: WizardStep; label: string }[] = [
  { key: 'sequence', label: 'Select Sequence' },
  { key: 'steps', label: 'Configure Steps' },
  { key: 'parameters', label: 'Set Parameters' },
  { key: 'quantity', label: 'Batch Quantity' },
  { key: 'review', label: 'Review & Create' },
];

export function CreateBatchWizard({
  isOpen,
  onClose,
  onSubmit,
  sequences,
  getSequenceDetail,
  isSubmitting,
}: CreateBatchWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>('sequence');
  const [selectedSequence, setSelectedSequence] = useState<string>('');
  const [sequenceDetail, setSequenceDetail] = useState<SequencePackage | null>(null);
  const [isLoadingSequence, setIsLoadingSequence] = useState(false);
  const [stepOrder, setStepOrder] = useState<Array<{ name: string; displayName?: string; order: number; enabled: boolean }>>([]);
  const [parameters, setParameters] = useState<Record<string, unknown>>({});
  const [quantity, setQuantity] = useState(1);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [selectedProcessId, setSelectedProcessId] = useState<number | undefined>(undefined);

  // Workflow and MES process hooks
  const { data: workflowConfig } = useWorkflowConfig();
  const { data: processes = [] } = useProcesses();
  const isWorkflowEnabled = workflowConfig?.enabled ?? false;

  const currentStepIndex = WIZARD_STEPS.findIndex((s) => s.key === currentStep);
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === WIZARD_STEPS.length - 1;

  // Reset wizard state when opened
  useEffect(() => {
    if (isOpen) {
      setCurrentStep('sequence');
      setSelectedSequence('');
      setSequenceDetail(null);
      setIsLoadingSequence(false);
      setStepOrder([]);
      setParameters({});
      setQuantity(1);
      setDraggedIndex(null);
      setSelectedProcessId(undefined);
    }
  }, [isOpen]);

  // Load sequence details when selected
  const handleSequenceSelect = useCallback(
    async (sequenceName: string) => {
      console.log('[CreateBatchWizard] handleSequenceSelect called with:', sequenceName);
      setSelectedSequence(sequenceName);
      if (!sequenceName) {
        setSequenceDetail(null);
        setStepOrder([]);
        setParameters({});
        return;
      }

      setIsLoadingSequence(true);
      try {
        console.log('[CreateBatchWizard] Fetching sequence detail for:', sequenceName);
        const detail = await getSequenceDetail(sequenceName);
        console.log('[CreateBatchWizard] Received sequence detail:', detail);

        if (!detail) {
          console.error('[CreateBatchWizard] Received null/undefined detail');
          return;
        }

        setSequenceDetail(detail);

        // Initialize step order from sequence (include displayName for UI)
        const steps = detail.steps || [];
        console.log('[CreateBatchWizard] Steps count:', steps.length);
        setStepOrder(
          steps.map((step) => ({
            name: step.name,
            displayName: step.displayName,
            order: step.order,
            enabled: true,
          }))
        );

        // Initialize parameters with defaults
        const defaultParams: Record<string, unknown> = {};
        const params = detail.parameters || [];
        params.forEach((param) => {
          defaultParams[param.name] = param.default;
        });
        setParameters(defaultParams);
      } catch (error) {
        console.error('[CreateBatchWizard] Failed to load sequence:', error);
        // Reset sequence detail on error
        setSequenceDetail(null);
      } finally {
        setIsLoadingSequence(false);
      }
    },
    [getSequenceDetail]
  );

  // Step navigation
  const goNext = () => {
    const nextIndex = currentStepIndex + 1;
    const nextStep = WIZARD_STEPS[nextIndex];
    if (nextStep) {
      setCurrentStep(nextStep.key);
    }
  };

  const goBack = () => {
    const prevIndex = currentStepIndex - 1;
    const prevStep = WIZARD_STEPS[prevIndex];
    if (prevStep) {
      setCurrentStep(prevStep.key);
    }
  };

  // Drag and drop for step reordering
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newOrder = [...stepOrder];
    const draggedItem = newOrder[draggedIndex];
    if (!draggedItem) return;

    newOrder.splice(draggedIndex, 1);
    newOrder.splice(index, 0, draggedItem);

    // Update order numbers
    newOrder.forEach((item, i) => {
      item.order = i + 1;
    });

    setStepOrder(newOrder);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const toggleStepEnabled = (index: number) => {
    setStepOrder((prev) =>
      prev.map((item, i) => (i === index ? { ...item, enabled: !item.enabled } : item))
    );
  };

  // Parameter handling
  const handleParamChange = (name: string, value: unknown) => {
    setParameters((prev) => ({ ...prev, [name]: value }));
  };

  // Submit
  const handleSubmit = () => {
    const request: CreateBatchRequest = {
      quantity,
      sequenceName: selectedSequence,
      stepOrder: stepOrder.filter((s) => s.enabled),
      parameters,
      processId: selectedProcessId,
    };
    onSubmit(request);
  };

  // Validation
  const canProceed = useMemo(() => {
    switch (currentStep) {
      case 'sequence': {
        const baseValid = !!selectedSequence && !!sequenceDetail;
        // If workflow is enabled, MES Process selection is required
        return isWorkflowEnabled ? (baseValid && !!selectedProcessId) : baseValid;
      }
      case 'steps':
        return stepOrder.filter((s) => s.enabled).length > 0;
      case 'parameters':
        return true; // Parameters are optional
      case 'quantity':
        return quantity >= 1 && quantity <= 100;
      case 'review':
        return true;
      default:
        return false;
    }
  }, [currentStep, selectedSequence, sequenceDetail, stepOrder, quantity, isWorkflowEnabled, selectedProcessId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-5xl rounded-xl border flex flex-col overflow-hidden" style={{ height: '700px', minHeight: '700px', maxHeight: '700px', backgroundColor: 'var(--color-bg-primary)', borderColor: 'var(--color-border-default)' }}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
          <h2 className="text-xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Create Batch</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--color-border-default)', backgroundColor: 'var(--color-bg-secondary)' }}>
          <div className="flex items-center justify-between">
            {WIZARD_STEPS.map((step, index) => (
              <div key={step.key} className="flex items-center flex-shrink-0">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium flex-shrink-0 ${
                    index < currentStepIndex
                      ? 'bg-brand-500 text-white'
                      : index === currentStepIndex
                        ? 'bg-brand-500/20 text-brand-500 border-2 border-brand-500'
                        : ''
                  }`}
                  style={index >= currentStepIndex && index !== currentStepIndex ? { backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-tertiary)' } : undefined}
                >
                  {index < currentStepIndex ? <Check className="w-4 h-4" /> : index + 1}
                </div>
                <span
                  className="ml-2 text-sm whitespace-nowrap"
                  style={{ color: index === currentStepIndex ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)' }}
                >
                  {step.label}
                </span>
                {index < WIZARD_STEPS.length - 1 && (
                  <div
                    className={`w-8 lg:w-12 h-0.5 mx-2 flex-shrink-0 ${
                      index < currentStepIndex ? 'bg-brand-500' : ''
                    }`}
                    style={index >= currentStepIndex ? { backgroundColor: 'var(--color-border-default)' } : undefined}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content - fixed height to prevent modal resize between steps */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6">
          {currentStep === 'sequence' && (
            <SequenceSelectStep
              sequences={sequences}
              selectedSequence={selectedSequence}
              onSelect={handleSequenceSelect}
              sequenceDetail={sequenceDetail}
              isLoading={isLoadingSequence}
              isWorkflowEnabled={isWorkflowEnabled}
              processes={processes}
              selectedProcessId={selectedProcessId}
              onProcessSelect={setSelectedProcessId}
            />
          )}

          {currentStep === 'steps' && sequenceDetail && (
            <StepConfigStep
              steps={sequenceDetail.steps}
              stepOrder={stepOrder}
              onDragStart={handleDragStart}
              onDragOver={handleDragOver}
              onDragEnd={handleDragEnd}
              onToggleEnabled={toggleStepEnabled}
              draggedIndex={draggedIndex}
            />
          )}

          {currentStep === 'parameters' && sequenceDetail && (
            <ParameterConfigStep
              parameterSchemas={sequenceDetail.parameters}
              parameters={parameters}
              onChange={handleParamChange}
            />
          )}

          {currentStep === 'quantity' && (
            <QuantityStep quantity={quantity} onChange={setQuantity} />
          )}

          {currentStep === 'review' && (
            <ReviewStep
              sequenceName={selectedSequence}
              sequenceDetail={sequenceDetail}
              stepOrder={stepOrder}
              parameters={parameters}
              quantity={quantity}
              isWorkflowEnabled={isWorkflowEnabled}
              selectedProcessId={selectedProcessId}
              processes={processes}
            />
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t" style={{ borderColor: 'var(--color-border-default)', backgroundColor: 'var(--color-bg-secondary)' }}>
          <Button variant="ghost" onClick={goBack} disabled={isFirstStep}>
            <ChevronLeft className="w-4 h-4 mr-1" />
            Back
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            {isLastStep ? (
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={!canProceed}
                isLoading={isSubmitting}
              >
                <Check className="w-4 h-4 mr-1" />
                Create Batches
              </Button>
            ) : (
              <Button variant="primary" onClick={goNext} disabled={!canProceed}>
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 1: Sequence Selection
function SequenceSelectStep({
  sequences,
  selectedSequence,
  onSelect,
  sequenceDetail,
  isLoading,
  isWorkflowEnabled,
  processes,
  selectedProcessId,
  onProcessSelect,
}: {
  sequences: SequenceSummary[];
  selectedSequence: string;
  onSelect: (name: string) => void;
  sequenceDetail: SequencePackage | null;
  isLoading: boolean;
  isWorkflowEnabled: boolean;
  processes: ProcessInfo[];
  selectedProcessId: number | undefined;
  onProcessSelect: (id: number | undefined) => void;
}) {
  const sequenceOptions = [
    { value: '', label: 'Select a sequence...' },
    ...sequences.map((s) => ({
      value: s.name,
      label: `${s.displayName || s.name} (v${s.version})`,
    })),
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Select Deployed Sequence</h3>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          Choose a deployed sequence to use for this batch. Each batch can use a different sequence.
        </p>
        <Select
          options={sequenceOptions}
          value={selectedSequence}
          onChange={(e) => onSelect(e.target.value)}
          className="w-full"
        />
      </div>

      {/* MES Process Selection - Only shown when workflow is enabled */}
      {isWorkflowEnabled && (
        <div>
          <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>
            MES Process <span className="text-red-500">*</span>
          </h3>
          <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
            WIP 연동이 활성화되어 있습니다. 이 배치에서 실행할 MES 공정을 선택하세요.
          </p>
          <select
            value={selectedProcessId ?? ''}
            onChange={(e) => {
              const value = e.target.value;
              onProcessSelect(value ? parseInt(value, 10) : undefined);
            }}
            className="w-full px-3 py-2 rounded-lg border outline-none transition-colors text-sm"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: selectedProcessId ? 'var(--color-border-default)' : 'var(--color-status-fail)',
              color: 'var(--color-text-primary)',
            }}
          >
            <option value="" disabled>-- Select MES Process --</option>
            {processes.map((process) => (
              <option key={process.id} value={process.id}>
                {process.processNumber}. {process.processNameEn}
              </option>
            ))}
          </select>
          {!selectedProcessId && (
            <div className="flex items-center gap-2 mt-2 text-xs" style={{ color: 'var(--color-status-fail)' }}>
              <AlertCircle className="w-3.5 h-3.5" />
              <span>MES Process 선택이 필요합니다</span>
            </div>
          )}
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full" />
        </div>
      )}

      {sequenceDetail && !isLoading && (
        <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <h4 className="font-medium mb-3" style={{ color: 'var(--color-text-primary)' }}>Sequence Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Name:</span>
              <span className="ml-2" style={{ color: 'var(--color-text-primary)' }}>{sequenceDetail.displayName || sequenceDetail.name}</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Version:</span>
              <span className="ml-2" style={{ color: 'var(--color-text-primary)' }}>{sequenceDetail.version}</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Steps:</span>
              <span className="ml-2" style={{ color: 'var(--color-text-primary)' }}>{sequenceDetail.steps.length}</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-tertiary)' }}>Parameters:</span>
              <span className="ml-2" style={{ color: 'var(--color-text-primary)' }}>{sequenceDetail.parameters.length}</span>
            </div>
            {sequenceDetail.description && (
              <div className="col-span-2">
                <span style={{ color: 'var(--color-text-tertiary)' }}>Description:</span>
                <p className="mt-1" style={{ color: 'var(--color-text-primary)' }}>{sequenceDetail.description}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Step 2: Step Configuration
function StepConfigStep({
  steps,
  stepOrder,
  onDragStart,
  onDragOver,
  onDragEnd,
  onToggleEnabled,
  draggedIndex,
}: {
  steps: StepSchema[];
  stepOrder: Array<{ name: string; displayName?: string; order: number; enabled: boolean }>;
  onDragStart: (index: number) => void;
  onDragOver: (e: React.DragEvent, index: number) => void;
  onDragEnd: () => void;
  onToggleEnabled: (index: number) => void;
  draggedIndex: number | null;
}) {
  // Get step details by name
  const getStepInfo = (name: string) => steps.find((s) => s.name === name);

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Configure Steps</h3>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          Drag to reorder steps or toggle to enable/disable them.
        </p>
      </div>

      <div className="space-y-2">
        {stepOrder.map((item, index) => {
          const stepInfo = getStepInfo(item.name);
          return (
            <div
              key={item.name}
              draggable
              onDragStart={() => onDragStart(index)}
              onDragOver={(e) => onDragOver(e, index)}
              onDragEnd={onDragEnd}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                draggedIndex === index
                  ? 'bg-brand-500/20 border-brand-500'
                  : item.enabled
                    ? 'hover:opacity-90'
                    : 'opacity-60'
              }`}
              style={{
                backgroundColor: draggedIndex === index ? undefined : 'var(--color-bg-secondary)',
                borderColor: draggedIndex === index ? undefined : 'var(--color-border-default)',
              }}
            >
              <div className="cursor-grab">
                <GripVertical className="w-5 h-5" style={{ color: 'var(--color-text-tertiary)' }} />
              </div>
              <div className="w-8 h-8 flex items-center justify-center rounded-full text-sm font-medium" style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-primary)' }}>
                {index + 1}
              </div>
              <div className="flex-1">
                <p className="font-medium" style={{ color: item.enabled ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)' }}>
                  {stepInfo?.displayName || item.name}
                </p>
                {stepInfo?.description && (
                  <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>{stepInfo.description}</p>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                <span>Timeout: {stepInfo?.timeout || 0}s</span>
                {stepInfo?.retry && stepInfo.retry > 0 && <span>Retry: {stepInfo.retry}</span>}
              </div>
              <Button
                variant={item.enabled ? 'ghost' : 'secondary'}
                size="sm"
                onClick={() => onToggleEnabled(index)}
              >
                {item.enabled ? 'Enabled' : 'Disabled'}
              </Button>
            </div>
          );
        })}
      </div>

      {stepOrder.filter((s) => s.enabled).length === 0 && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">At least one step must be enabled</span>
        </div>
      )}
    </div>
  );
}

// Step 3: Parameter Configuration
function ParameterConfigStep({
  parameterSchemas,
  parameters,
  onChange,
}: {
  parameterSchemas: ParameterSchema[];
  parameters: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
}) {
  if (parameterSchemas.length === 0) {
    return (
      <div className="text-center py-8">
        <p style={{ color: 'var(--color-text-tertiary)' }}>This sequence has no configurable parameters</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Set Parameters</h3>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          Configure the sequence parameters. Default values are pre-filled.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {parameterSchemas.map((param) => (
          <div key={param.name} className="p-3 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
            <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-primary)' }}>
              {param.displayName || param.name}
              {param.unit && <span className="ml-1" style={{ color: 'var(--color-text-tertiary)' }}>({param.unit})</span>}
            </label>
            {param.description && (
              <p className="text-xs mb-2" style={{ color: 'var(--color-text-tertiary)' }}>{param.description}</p>
            )}
            {param.type === 'boolean' ? (
              <Select
                options={[
                  { value: 'true', label: 'True' },
                  { value: 'false', label: 'False' },
                ]}
                value={String(parameters[param.name])}
                onChange={(e) => onChange(param.name, e.target.value === 'true')}
              />
            ) : param.options ? (
              <Select
                options={param.options.map((opt) => ({ value: opt, label: opt }))}
                value={String(parameters[param.name])}
                onChange={(e) => onChange(param.name, e.target.value)}
              />
            ) : (
              <Input
                type={param.type === 'integer' || param.type === 'float' ? 'number' : 'text'}
                value={String(parameters[param.name] ?? '')}
                onChange={(e) => {
                  const val = e.target.value;
                  if (param.type === 'integer') {
                    onChange(param.name, parseInt(val, 10) || 0);
                  } else if (param.type === 'float') {
                    onChange(param.name, parseFloat(val) || 0);
                  } else {
                    onChange(param.name, val);
                  }
                }}
                min={param.min}
                max={param.max}
              />
            )}
            {(param.min !== undefined || param.max !== undefined) && (
              <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                Range: {param.min ?? '-∞'} ~ {param.max ?? '∞'}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Step 4: Quantity Selection
function QuantityStep({
  quantity,
  onChange,
}: {
  quantity: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Batch Quantity</h3>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          Select the number of batches to create. Each batch will be configured with the same
          sequence and parameters.
        </p>
      </div>

      <div className="flex items-center justify-center gap-6">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => onChange(Math.max(1, quantity - 1))}
          disabled={quantity <= 1}
        >
          <Minus className="w-5 h-5" />
        </Button>
        <div className="w-24">
          <Input
            type="number"
            value={quantity}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              if (!isNaN(val) && val >= 1 && val <= 100) {
                onChange(val);
              }
            }}
            min={1}
            max={100}
            className="text-center text-2xl font-bold"
          />
        </div>
        <Button
          variant="secondary"
          size="lg"
          onClick={() => onChange(Math.min(100, quantity + 1))}
          disabled={quantity >= 100}
        >
          <Plus className="w-5 h-5" />
        </Button>
      </div>

      <p className="text-center text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
        {quantity} batch{quantity > 1 ? 'es' : ''} will be created
      </p>
    </div>
  );
}

// Step 5: Review
function ReviewStep({
  sequenceName,
  sequenceDetail,
  stepOrder,
  parameters,
  quantity,
  isWorkflowEnabled,
  selectedProcessId,
  processes,
}: {
  sequenceName: string;
  sequenceDetail: SequencePackage | null;
  stepOrder: Array<{ name: string; displayName?: string; order: number; enabled: boolean }>;
  parameters: Record<string, unknown>;
  quantity: number;
  isWorkflowEnabled: boolean;
  selectedProcessId: number | undefined;
  processes: ProcessInfo[];
}) {
  const enabledSteps = stepOrder.filter((s) => s.enabled);
  const selectedProcess = processes.find((p) => p.id === selectedProcessId);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>Review Configuration</h3>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          Please review the batch configuration before creating.
        </p>
      </div>

      <div className="space-y-4">
        {/* Sequence */}
        <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>Sequence</h4>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
            {sequenceDetail?.displayName || sequenceName} (v{sequenceDetail?.version})
          </p>
        </div>

        {/* MES Process - Only shown when workflow is enabled */}
        {isWorkflowEnabled && selectedProcess && (
          <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
            <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>MES Process</h4>
            <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {selectedProcess.processNumber}. {selectedProcess.processNameEn}
            </p>
          </div>
        )}

        {/* Steps */}
        <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
            Steps ({enabledSteps.length} enabled)
          </h4>
          <div className="flex flex-wrap gap-2">
            {enabledSteps.map((step, index) => (
              <span
                key={step.name}
                className="px-2 py-1 rounded text-sm"
                style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-primary)' }}
              >
                {index + 1}. {step.displayName || step.name}
              </span>
            ))}
          </div>
        </div>

        {/* Parameters */}
        <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>Parameters</h4>
          {Object.keys(parameters).length === 0 ? (
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No parameters configured</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
              {Object.entries(parameters).map(([key, value]) => (
                <div key={key}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>{key}:</span>
                  <span className="ml-1 font-mono" style={{ color: 'var(--color-text-primary)' }}>{String(value)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quantity */}
        <div className="p-4 bg-brand-500/10 rounded-lg border border-brand-500/30">
          <h4 className="text-sm font-medium text-brand-400 mb-2">Batch Quantity</h4>
          <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {quantity} <span className="text-base font-normal" style={{ color: 'var(--color-text-secondary)' }}>batch{quantity > 1 ? 'es' : ''}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
