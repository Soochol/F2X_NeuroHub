# Manual Control Page Enhancement Design

## 1. Executive Summary

This document outlines the design for enhancing the Manual Control page (`/ui/manual`) and defining how sequence files should be structured to support manual operation mode.

### Goals
1. Transform raw JSON command interface into intuitive device-specific UI
2. Enable step-by-step manual sequence execution
3. Provide real-time device monitoring and status
4. Support command presets and templates
5. Define sequence file structure for manual mode compatibility

---

## 2. Current State Analysis

### Current ManualControlPage Features
```
Location: station_ui/src/pages/ManualControlPage.tsx
```

| Feature | Status | Limitation |
|---------|--------|------------|
| Batch Selection | Implemented | No filtering by status |
| Hardware Selection | Implemented | No device info display |
| Command Input | Raw text input | Requires exact method names |
| Parameters | Raw JSON textarea | Error-prone, no validation |
| Result Display | JSON output | No formatted visualization |
| Command History | 20 entries | No persistence, no search |

### Current Manual Control API Flow
```
ManualControlPage -> useManualControl hook -> POST /api/batches/{id}/manual
                                                    |
                                                    v
                                            BatchManager.manual_control()
                                                    |
                                                    v
                                            BatchWorker._cmd_manual_control()
                                                    |
                                                    v
                                            driver.{command}(**params)
```

---

## 3. Enhanced Architecture

### 3.1 Component Hierarchy

```
ManualControlPage (Enhanced)
├── DevicePanel
│   ├── DeviceSelector
│   │   ├── BatchFilter (idle only)
│   │   └── HardwareList (with status indicators)
│   ├── DeviceInfo
│   │   ├── DriverInfo (name, version, capabilities)
│   │   ├── ConnectionStatus (live indicator)
│   │   └── DeviceProperties (IDN, config)
│   └── QuickActions
│       ├── Connect/Disconnect
│       ├── Reset
│       └── Identify
│
├── CommandPanel
│   ├── CommandSelector
│   │   ├── CategoryTabs (Measurement, Control, Configuration)
│   │   └── CommandList (auto-discovered from driver)
│   ├── ParameterForm
│   │   ├── SmartInputs (type-aware: number, string, select)
│   │   ├── UnitDisplay
│   │   └── ValidationFeedback
│   ├── PresetManager
│   │   ├── SavePreset
│   │   ├── LoadPreset
│   │   └── PresetList
│   └── ExecuteButton (with loading state)
│
├── ResultPanel
│   ├── LiveResult
│   │   ├── FormattedValue (with unit)
│   │   ├── Timestamp
│   │   └── ExecutionTime
│   ├── ResultHistory
│   │   ├── ChartView (for numeric values)
│   │   ├── TableView (for structured data)
│   │   └── RawView (JSON fallback)
│   └── ExportOptions
│
└── ManualSequencePanel (New)
    ├── SequenceStepList
    │   ├── StepCard (draggable for reorder)
    │   ├── StepStatus (pending, running, completed, skipped)
    │   └── StepActions (run, skip, retry)
    ├── ParameterOverrides
    │   └── StepParameterEditor
    └── ExecutionControls
        ├── RunNextStep
        ├── RunAllRemaining
        └── Reset
```

### 3.2 State Management

```typescript
// New store: station_ui/src/stores/manualControlStore.ts

interface ManualControlState {
  // Device selection
  selectedBatchId: string | null;
  selectedHardwareId: string | null;

  // Command state
  selectedCommand: CommandDefinition | null;
  parameterValues: Record<string, unknown>;

  // Presets
  presets: CommandPreset[];

  // Results
  lastResult: ManualControlResponse | null;
  resultHistory: ResultHistoryEntry[];

  // Manual sequence mode
  manualSequenceMode: boolean;
  sequenceSteps: ManualStep[];
  currentStepIndex: number;
  stepOverrides: Record<string, Record<string, unknown>>;

  // Actions
  selectDevice: (batchId: string, hardwareId: string) => void;
  executeCommand: (command: string, params: Record<string, unknown>) => Promise<void>;
  runStep: (stepIndex: number) => Promise<void>;
  skipStep: (stepIndex: number) => void;
  resetSequence: () => void;
}

interface CommandDefinition {
  name: string;
  displayName: string;
  description: string;
  category: 'measurement' | 'control' | 'configuration' | 'diagnostic';
  parameters: ParameterDefinition[];
  returnType: string;
  async: boolean;
}

interface ParameterDefinition {
  name: string;
  displayName: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'range';
  required: boolean;
  default?: unknown;
  unit?: string;
  min?: number;
  max?: number;
  options?: Array<{ value: unknown; label: string }>;
  description?: string;
}

interface CommandPreset {
  id: string;
  name: string;
  hardwareType: string;
  command: string;
  params: Record<string, unknown>;
  createdAt: Date;
}

interface ManualStep {
  name: string;
  displayName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result?: StepResult;
  duration?: number;
  canRetry: boolean;
}
```

---

## 4. API Enhancements

### 4.1 New Endpoints

```python
# station_service/api/routes/manual.py

@router.get("/api/hardware/{hardware_id}/commands")
async def get_hardware_commands(hardware_id: str) -> List[CommandDefinition]:
    """
    Get available commands for a hardware device.
    Auto-discovers methods from driver class with their signatures.
    """
    pass

@router.get("/api/hardware/{hardware_id}/status")
async def get_hardware_status(hardware_id: str) -> HardwareDetailedStatus:
    """
    Get detailed real-time status of hardware device.
    Includes connection state, last reading, error state.
    """
    pass

@router.post("/api/batches/{batch_id}/manual/preset")
async def save_command_preset(preset: CommandPreset) -> CommandPreset:
    """Save a command preset for quick access."""
    pass

@router.get("/api/batches/{batch_id}/manual/presets")
async def list_command_presets(batch_id: str) -> List[CommandPreset]:
    """List all saved command presets."""
    pass
```

### 4.2 Command Discovery Implementation

```python
# station_service/hardware/introspection.py

import inspect
from typing import get_type_hints

def discover_driver_commands(driver_class) -> List[CommandDefinition]:
    """
    Introspect driver class to discover available commands.
    Uses type hints, docstrings, and decorators for metadata.
    """
    commands = []

    for name, method in inspect.getmembers(driver_class, predicate=inspect.isfunction):
        # Skip private methods
        if name.startswith('_'):
            continue

        # Get type hints
        hints = get_type_hints(method)

        # Parse docstring for description
        doc = inspect.getdoc(method) or ""

        # Get parameters
        sig = inspect.signature(method)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            params.append(ParameterDefinition(
                name=param_name,
                type=_infer_type(hints.get(param_name)),
                required=param.default is inspect.Parameter.empty,
                default=None if param.default is inspect.Parameter.empty else param.default,
            ))

        commands.append(CommandDefinition(
            name=name,
            displayName=_to_display_name(name),
            description=doc.split('\n')[0] if doc else "",
            category=_infer_category(name),
            parameters=params,
            returnType=str(hints.get('return', 'Any')),
            async=asyncio.iscoroutinefunction(method),
        ))

    return commands

def _infer_category(method_name: str) -> str:
    """Infer command category from method name."""
    if any(kw in method_name for kw in ['measure', 'read', 'get']):
        return 'measurement'
    elif any(kw in method_name for kw in ['set', 'write', 'move', 'trigger']):
        return 'control'
    elif any(kw in method_name for kw in ['config', 'range', 'mode']):
        return 'configuration'
    else:
        return 'diagnostic'
```

---

## 5. UI Components Design

### 5.1 DevicePanel Component

```tsx
// station_ui/src/components/manual/DevicePanel.tsx

interface DevicePanelProps {
  onDeviceSelect: (batchId: string, hardwareId: string) => void;
  selectedBatchId: string | null;
  selectedHardwareId: string | null;
}

export function DevicePanel({ onDeviceSelect, selectedBatchId, selectedHardwareId }: DevicePanelProps) {
  const { data: batches } = useBatchList();

  // Filter to show only idle batches (manual control not allowed during execution)
  const idleBatches = batches?.filter(b => b.status === 'idle') ?? [];

  const { data: batchDetail } = useBatch(selectedBatchId);

  return (
    <div className="p-4 border rounded-lg bg-secondary">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Cpu className="w-5 h-5" />
        Device Selection
      </h3>

      {/* Batch Selection */}
      <Select
        label="Test Station (Batch)"
        options={idleBatches.map(b => ({
          value: b.id,
          label: `${b.name} - ${b.sequenceName}`,
          icon: b.status === 'idle' ? CheckCircle : AlertTriangle,
        }))}
        value={selectedBatchId ?? ''}
        onChange={(v) => onDeviceSelect(v, '')}
        placeholder="Select idle batch..."
      />

      {/* Hardware Device List */}
      {batchDetail?.hardwareStatus && (
        <div className="mt-4 space-y-2">
          <label className="text-sm font-medium text-secondary">Hardware Devices</label>
          {Object.entries(batchDetail.hardwareStatus).map(([id, status]) => (
            <HardwareCard
              key={id}
              id={id}
              status={status}
              isSelected={selectedHardwareId === id}
              onClick={() => onDeviceSelect(selectedBatchId!, id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function HardwareCard({ id, status, isSelected, onClick }: HardwareCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full p-3 rounded-lg border transition-all text-left",
        isSelected
          ? "border-brand-500 bg-brand-500/10"
          : "border-default hover:border-brand-300"
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <span className="font-medium">{id}</span>
          <span className="ml-2 text-xs text-tertiary">{status.driver}</span>
        </div>
        <StatusIndicator status={status.status} />
      </div>
      {status.info?.idn && (
        <div className="mt-1 text-xs text-tertiary truncate">
          {status.info.idn}
        </div>
      )}
    </button>
  );
}
```

### 5.2 CommandPanel with Smart Form

```tsx
// station_ui/src/components/manual/CommandPanel.tsx

export function CommandPanel({ batchId, hardwareId }: CommandPanelProps) {
  const { data: commands } = useHardwareCommands(batchId, hardwareId);
  const [selectedCommand, setSelectedCommand] = useState<CommandDefinition | null>(null);
  const [paramValues, setParamValues] = useState<Record<string, unknown>>({});
  const manualControl = useManualControl();

  // Group commands by category
  const groupedCommands = useMemo(() => {
    if (!commands) return {};
    return groupBy(commands, 'category');
  }, [commands]);

  const handleExecute = async () => {
    if (!selectedCommand) return;

    await manualControl.mutateAsync({
      batchId,
      request: {
        hardware: hardwareId,
        command: selectedCommand.name,
        params: paramValues,
      },
    });
  };

  return (
    <div className="space-y-4">
      {/* Command Category Tabs */}
      <Tabs defaultValue="measurement">
        {Object.entries(groupedCommands).map(([category, cmds]) => (
          <TabsTrigger key={category} value={category}>
            {getCategoryIcon(category)}
            {category}
            <Badge variant="secondary">{cmds.length}</Badge>
          </TabsTrigger>
        ))}
      </Tabs>

      {/* Command Selection */}
      <CommandList
        commands={groupedCommands[activeCategory] ?? []}
        selectedCommand={selectedCommand}
        onSelect={setSelectedCommand}
      />

      {/* Smart Parameter Form */}
      {selectedCommand && (
        <ParameterForm
          parameters={selectedCommand.parameters}
          values={paramValues}
          onChange={setParamValues}
        />
      )}

      {/* Execute Button */}
      <Button
        onClick={handleExecute}
        disabled={!selectedCommand || manualControl.isPending}
        className="w-full"
      >
        {manualControl.isPending ? <Loader2 className="animate-spin" /> : <Play />}
        Execute {selectedCommand?.displayName ?? 'Command'}
      </Button>
    </div>
  );
}

function ParameterForm({ parameters, values, onChange }: ParameterFormProps) {
  return (
    <div className="space-y-3 p-4 bg-tertiary rounded-lg">
      {parameters.map(param => (
        <SmartInput
          key={param.name}
          parameter={param}
          value={values[param.name]}
          onChange={(v) => onChange({ ...values, [param.name]: v })}
        />
      ))}
    </div>
  );
}

function SmartInput({ parameter, value, onChange }: SmartInputProps) {
  switch (parameter.type) {
    case 'number':
      return (
        <NumberInput
          label={parameter.displayName}
          value={value as number}
          onChange={onChange}
          min={parameter.min}
          max={parameter.max}
          unit={parameter.unit}
          step={parameter.step ?? 1}
        />
      );

    case 'select':
      return (
        <Select
          label={parameter.displayName}
          value={value as string}
          onChange={onChange}
          options={parameter.options ?? []}
        />
      );

    case 'range':
      return (
        <Slider
          label={parameter.displayName}
          value={value as number}
          onChange={onChange}
          min={parameter.min!}
          max={parameter.max!}
          unit={parameter.unit}
        />
      );

    case 'boolean':
      return (
        <Toggle
          label={parameter.displayName}
          checked={value as boolean}
          onChange={onChange}
        />
      );

    default:
      return (
        <Input
          label={parameter.displayName}
          value={value as string}
          onChange={(e) => onChange(e.target.value)}
          placeholder={parameter.description}
        />
      );
  }
}
```

### 5.3 Result Panel with Visualization

```tsx
// station_ui/src/components/manual/ResultPanel.tsx

export function ResultPanel({ history }: ResultPanelProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table' | 'raw'>('chart');

  // Extract numeric values for charting
  const chartData = useMemo(() => {
    return history
      .filter(h => typeof h.result === 'number')
      .map(h => ({
        timestamp: h.timestamp,
        value: h.result as number,
        command: h.command,
      }))
      .slice(-20); // Last 20 readings
  }, [history]);

  return (
    <div className="space-y-4">
      {/* View Mode Toggle */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Results</h3>
        <SegmentedControl
          value={viewMode}
          onChange={setViewMode}
          options={[
            { value: 'chart', icon: LineChart },
            { value: 'table', icon: Table },
            { value: 'raw', icon: Code },
          ]}
        />
      </div>

      {/* Last Result Card */}
      {history[0] && (
        <LastResultCard result={history[0]} />
      )}

      {/* History View */}
      {viewMode === 'chart' && chartData.length > 0 && (
        <ResultChart data={chartData} />
      )}

      {viewMode === 'table' && (
        <ResultTable history={history} />
      )}

      {viewMode === 'raw' && (
        <ResultRawView history={history} />
      )}
    </div>
  );
}

function LastResultCard({ result }: { result: ResultHistoryEntry }) {
  const formattedValue = formatValue(result.result, result.unit);

  return (
    <div className="p-4 bg-brand-500/10 border border-brand-500/30 rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-sm text-tertiary">{result.hardware}.{result.command}</span>
          <div className="text-2xl font-bold text-brand-500">
            {formattedValue.value}
            <span className="text-sm ml-1">{formattedValue.unit}</span>
          </div>
        </div>
        <StatusBadge status={result.success ? 'pass' : 'fail'} />
      </div>
      <div className="mt-2 text-xs text-tertiary">
        {formatDistanceToNow(result.timestamp)} ago | {result.duration}ms
      </div>
    </div>
  );
}
```

---

## 6. Manual Sequence Mode

### 6.1 ManualSequencePanel Component

```tsx
// station_ui/src/components/manual/ManualSequencePanel.tsx

export function ManualSequencePanel({ batchId }: { batchId: string }) {
  const { data: batchDetail } = useBatch(batchId);
  const [steps, setSteps] = useState<ManualStep[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [stepOverrides, setStepOverrides] = useState<Record<string, Record<string, unknown>>>({});

  const runStep = useManualStepExecution();

  // Initialize steps from sequence definition
  useEffect(() => {
    if (batchDetail?.execution?.steps) {
      setSteps(batchDetail.execution.steps.map(s => ({
        name: s.name,
        displayName: s.name,
        status: 'pending',
        canRetry: true,
      })));
    }
  }, [batchDetail]);

  const handleRunStep = async (index: number) => {
    const step = steps[index];

    // Update status to running
    setSteps(prev => prev.map((s, i) =>
      i === index ? { ...s, status: 'running' } : s
    ));

    try {
      const result = await runStep.mutateAsync({
        batchId,
        stepName: step.name,
        parameters: stepOverrides[step.name] ?? {},
      });

      setSteps(prev => prev.map((s, i) =>
        i === index ? {
          ...s,
          status: result.passed ? 'completed' : 'failed',
          result,
          duration: result.duration,
        } : s
      ));

      if (result.passed) {
        setCurrentStepIndex(index + 1);
      }
    } catch (error) {
      setSteps(prev => prev.map((s, i) =>
        i === index ? { ...s, status: 'failed' } : s
      ));
    }
  };

  const handleSkipStep = (index: number) => {
    setSteps(prev => prev.map((s, i) =>
      i === index ? { ...s, status: 'skipped' } : s
    ));
    setCurrentStepIndex(index + 1);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <ListOrdered className="w-5 h-5" />
          Manual Sequence Execution
        </h3>
        <Button variant="ghost" size="sm" onClick={() => {
          setSteps(prev => prev.map(s => ({ ...s, status: 'pending' })));
          setCurrentStepIndex(0);
        }}>
          <RotateCcw className="w-4 h-4 mr-1" />
          Reset
        </Button>
      </div>

      {/* Step List */}
      <div className="space-y-2">
        {steps.map((step, index) => (
          <StepCard
            key={step.name}
            step={step}
            index={index}
            isCurrent={index === currentStepIndex}
            onRun={() => handleRunStep(index)}
            onSkip={() => handleSkipStep(index)}
            onRetry={() => handleRunStep(index)}
            onEditParams={(params) => setStepOverrides(prev => ({
              ...prev,
              [step.name]: params,
            }))}
            paramOverrides={stepOverrides[step.name]}
          />
        ))}
      </div>

      {/* Bulk Actions */}
      <div className="flex gap-2">
        <Button
          className="flex-1"
          onClick={() => {
            // Run all remaining steps
            for (let i = currentStepIndex; i < steps.length; i++) {
              if (steps[i].status === 'pending') {
                handleRunStep(i);
                break;
              }
            }
          }}
          disabled={currentStepIndex >= steps.length}
        >
          <Play className="w-4 h-4 mr-1" />
          Run Next Step
        </Button>
        <Button
          variant="secondary"
          onClick={() => {
            // Run all remaining
          }}
        >
          <FastForward className="w-4 h-4 mr-1" />
          Run All Remaining
        </Button>
      </div>
    </div>
  );
}

function StepCard({
  step,
  index,
  isCurrent,
  onRun,
  onSkip,
  onRetry,
  onEditParams,
  paramOverrides,
}: StepCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors = {
    pending: 'border-default',
    running: 'border-blue-500 bg-blue-500/10',
    completed: 'border-green-500 bg-green-500/10',
    failed: 'border-red-500 bg-red-500/10',
    skipped: 'border-gray-500 bg-gray-500/10',
  };

  return (
    <div className={cn(
      "p-3 rounded-lg border transition-all",
      statusColors[step.status],
      isCurrent && "ring-2 ring-brand-500"
    )}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StepStatusIcon status={step.status} />
          <div>
            <span className="font-medium">{index + 1}. {step.displayName}</span>
            {step.duration && (
              <span className="ml-2 text-xs text-tertiary">{step.duration.toFixed(1)}s</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {step.status === 'pending' && isCurrent && (
            <>
              <Button size="sm" onClick={onRun}>
                <Play className="w-3 h-3" />
              </Button>
              <Button size="sm" variant="ghost" onClick={onSkip}>
                Skip
              </Button>
            </>
          )}
          {step.status === 'failed' && step.canRetry && (
            <Button size="sm" variant="secondary" onClick={onRetry}>
              <RotateCcw className="w-3 h-3 mr-1" />
              Retry
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={() => setIsExpanded(!isExpanded)}>
            {isExpanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-default">
          <h4 className="text-sm font-medium mb-2">Parameter Overrides</h4>
          <ParameterOverrideForm
            stepName={step.name}
            overrides={paramOverrides ?? {}}
            onChange={onEditParams}
          />

          {step.result && (
            <div className="mt-3">
              <h4 className="text-sm font-medium mb-2">Result</h4>
              <pre className="text-xs bg-tertiary p-2 rounded overflow-auto max-h-32">
                {JSON.stringify(step.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 7. Sequence File Structure for Manual Mode

### 7.1 Enhanced Manifest Schema

```yaml
# sequences/{package_name}/manifest.yaml

name: pcb_voltage_test
version: "1.0.0"
author: "NeuroHub Team"
description: "PCB voltage measurement test sequence"

# Execution modes
modes:
  automatic: true        # Standard sequential execution
  manual: true           # Step-by-step manual execution
  interactive: false     # Prompt-based execution (future)

entry_point:
  module: sequence
  class: PCBVoltageTestSequence

# Hardware definitions with manual control commands
hardware:
  multimeter:
    display_name: "Digital Multimeter"
    driver: mock_multimeter
    class: MockMultimeter
    description: "High-precision digital multimeter"

    # Manual control command definitions
    manual_commands:
      - name: measure_voltage
        display_name: "Measure Voltage"
        category: measurement
        description: "Measure DC/AC voltage at a test point"
        parameters:
          - name: mode
            type: select
            options: ["DC", "AC"]
            default: "DC"
          - name: test_point
            type: integer
            min: 1
            max: 20
            default: 1
        returns:
          type: float
          unit: "V"

      - name: set_range
        display_name: "Set Range"
        category: configuration
        parameters:
          - name: range_val
            type: select
            options: ["AUTO", "2V", "20V", "200V"]
            default: "AUTO"

      - name: reset
        display_name: "Reset"
        category: control
        description: "Reset multimeter to default state"

    config_schema:
      port:
        type: string
        default: "/dev/ttyUSB0"

# Step definitions with manual mode metadata
steps:
  - name: initialize
    display_name: "Initialize Hardware"
    order: 1
    timeout: 30.0
    manual:
      skippable: false      # Cannot skip in manual mode
      auto_only: false      # Available in both modes
      prompt: null          # No confirmation needed

  - name: measure_voltage
    display_name: "Measure Voltage Points"
    order: 2
    timeout: 120.0
    retry: 1
    manual:
      skippable: true       # Can skip in manual mode
      auto_only: false
      prompt: "Ready to measure voltage at test points?"
      pause_before: true    # Pause before execution
      parameter_overrides:
        - test_points        # Allow runtime override

  - name: validate_results
    display_name: "Validate Results"
    order: 3
    timeout: 30.0
    manual:
      skippable: true
      auto_only: false
      pause_after: true     # Pause after to review results

  - name: finalize
    display_name: "Finalize & Cleanup"
    order: 99
    cleanup: true
    timeout: 30.0
    manual:
      skippable: false      # Cleanup always runs
      auto_only: false

# Sequence parameters
parameters:
  voltage_threshold:
    display_name: "Voltage Threshold"
    type: float
    default: 5.0
    min: 0.0
    max: 24.0
    unit: "V"
    manual_override: true   # Can be changed in manual mode

dependencies:
  python: []
```

### 7.2 Step Decorator Enhancements

```python
# station_service/sequence/decorators.py

from dataclasses import dataclass, field
from typing import Optional, List, Callable

@dataclass
class ManualStepConfig:
    """Configuration for manual mode execution."""
    skippable: bool = True
    auto_only: bool = False
    prompt: Optional[str] = None
    pause_before: bool = False
    pause_after: bool = False
    parameter_overrides: List[str] = field(default_factory=list)

@dataclass
class StepMeta:
    """Enhanced step metadata."""
    name: Optional[str] = None
    order: int = 0
    timeout: float = 60.0
    retry: int = 0
    cleanup: bool = False
    manual: ManualStepConfig = field(default_factory=ManualStepConfig)

def step(
    order: int,
    name: Optional[str] = None,
    timeout: float = 60.0,
    retry: int = 0,
    cleanup: bool = False,
    # Manual mode options
    skippable: bool = True,
    auto_only: bool = False,
    prompt: Optional[str] = None,
    pause_before: bool = False,
    pause_after: bool = False,
    parameter_overrides: Optional[List[str]] = None,
) -> Callable:
    """
    Enhanced step decorator with manual mode support.

    Args:
        order: Execution order (lower runs first)
        name: Optional display name
        timeout: Maximum execution time in seconds
        retry: Number of retry attempts on failure
        cleanup: If True, always runs even if previous steps fail
        skippable: Can be skipped in manual mode
        auto_only: Only runs in automatic mode
        prompt: Confirmation prompt for manual mode
        pause_before: Pause before execution in manual mode
        pause_after: Pause after execution in manual mode
        parameter_overrides: Parameters that can be modified at runtime
    """
    def decorator(func: Callable) -> Callable:
        func._step_meta = StepMeta(
            name=name or func.__name__,
            order=order,
            timeout=timeout,
            retry=retry,
            cleanup=cleanup,
            manual=ManualStepConfig(
                skippable=skippable,
                auto_only=auto_only,
                prompt=prompt,
                pause_before=pause_before,
                pause_after=pause_after,
                parameter_overrides=parameter_overrides or [],
            ),
        )
        return func
    return decorator
```

### 7.3 Manual Mode Executor

```python
# station_service/sequence/manual_executor.py

class ManualSequenceExecutor:
    """
    Executor for manual step-by-step sequence execution.

    Unlike automatic execution, this allows:
    - Individual step execution
    - Step skipping
    - Parameter override at runtime
    - Pause/resume between steps
    - Step retry after failure
    """

    def __init__(
        self,
        sequence_instance: Any,
        on_step_prompt: Callable[[str, str], Awaitable[bool]] = None,
        on_pause: Callable[[str, StepResult], Awaitable[None]] = None,
    ):
        self._sequence = sequence_instance
        self._steps = self._collect_manual_steps()
        self._current_index = 0
        self._step_results: Dict[str, StepResult] = {}
        self._on_step_prompt = on_step_prompt
        self._on_pause = on_pause

    def _collect_manual_steps(self) -> List[Tuple[str, Callable, StepMeta]]:
        """Collect steps that are available in manual mode."""
        steps = collect_steps(self._sequence.__class__)
        return [
            (name, method, meta)
            for name, method, meta in steps
            if not meta.manual.auto_only
        ]

    async def run_step(
        self,
        step_name: str,
        parameter_overrides: Optional[Dict[str, Any]] = None,
    ) -> StepResult:
        """
        Execute a single step with optional parameter overrides.

        Args:
            step_name: Name of the step to execute
            parameter_overrides: Runtime parameter overrides

        Returns:
            StepResult from execution
        """
        step_info = self._get_step_by_name(step_name)
        if not step_info:
            raise ValueError(f"Step not found: {step_name}")

        name, method, meta = step_info

        # Handle pre-execution prompt
        if meta.manual.prompt and self._on_step_prompt:
            confirmed = await self._on_step_prompt(name, meta.manual.prompt)
            if not confirmed:
                return StepResult(
                    name=name,
                    passed=False,
                    error="User cancelled",
                )

        # Handle pause_before
        if meta.manual.pause_before and self._on_pause:
            await self._on_pause(name, None)

        # Apply parameter overrides
        if parameter_overrides:
            self._apply_overrides(parameter_overrides, meta.manual.parameter_overrides)

        # Execute step
        result = await self._execute_step(method, meta)
        self._step_results[name] = result

        # Handle pause_after
        if meta.manual.pause_after and self._on_pause:
            await self._on_pause(name, result)

        return result

    async def skip_step(self, step_name: str) -> StepResult:
        """
        Skip a step in manual mode.

        Args:
            step_name: Name of the step to skip

        Returns:
            StepResult with skipped status
        """
        step_info = self._get_step_by_name(step_name)
        if not step_info:
            raise ValueError(f"Step not found: {step_name}")

        name, _, meta = step_info

        if not meta.manual.skippable:
            raise ValueError(f"Step '{name}' cannot be skipped")

        result = StepResult(
            name=name,
            passed=True,
            skipped=True,
        )
        self._step_results[name] = result
        return result

    def get_available_steps(self) -> List[Dict[str, Any]]:
        """Get list of available steps with their manual config."""
        return [
            {
                "name": name,
                "displayName": meta.name or name,
                "order": meta.order,
                "skippable": meta.manual.skippable,
                "prompt": meta.manual.prompt,
                "parameterOverrides": meta.manual.parameter_overrides,
                "executed": name in self._step_results,
                "result": self._step_results.get(name),
            }
            for name, _, meta in self._steps
        ]
```

---

## 8. API for Manual Step Execution

### 8.1 New Endpoints

```python
# station_service/api/routes/batches.py (additions)

@router.get(
    "/{batch_id}/sequence/steps",
    response_model=ApiResponse[List[ManualStepInfo]],
    summary="Get sequence steps for manual execution",
)
async def get_manual_steps(
    batch_id: str = Path(...),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[List[ManualStepInfo]]:
    """
    Get the list of steps available for manual execution.

    Returns step metadata including:
    - Step name and display name
    - Whether it can be skipped
    - Parameters that can be overridden
    - Current execution status
    """
    steps = await batch_manager.get_manual_steps(batch_id)
    return ApiResponse(success=True, data=steps)


@router.post(
    "/{batch_id}/sequence/steps/{step_name}/run",
    response_model=ApiResponse[StepResult],
    summary="Execute a single step manually",
)
async def run_manual_step(
    batch_id: str = Path(...),
    step_name: str = Path(...),
    request: Optional[ManualStepRequest] = None,
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[StepResult]:
    """
    Execute a single step in manual mode.

    Allows parameter overrides for supported parameters.
    """
    result = await batch_manager.run_manual_step(
        batch_id=batch_id,
        step_name=step_name,
        parameter_overrides=request.parameters if request else None,
    )
    return ApiResponse(success=True, data=result)


@router.post(
    "/{batch_id}/sequence/steps/{step_name}/skip",
    response_model=ApiResponse[StepResult],
    summary="Skip a step in manual mode",
)
async def skip_manual_step(
    batch_id: str = Path(...),
    step_name: str = Path(...),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[StepResult]:
    """
    Skip a step in manual mode.

    Only works for steps marked as skippable.
    """
    result = await batch_manager.skip_manual_step(batch_id, step_name)
    return ApiResponse(success=True, data=result)


@router.post(
    "/{batch_id}/sequence/manual/reset",
    response_model=ApiResponse[Dict[str, str]],
    summary="Reset manual sequence execution",
)
async def reset_manual_sequence(
    batch_id: str = Path(...),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[Dict[str, str]]:
    """
    Reset manual sequence execution state.

    Clears all step results and resets to initial state.
    """
    await batch_manager.reset_manual_sequence(batch_id)
    return ApiResponse(success=True, data={"status": "reset"})
```

### 8.2 Schema Definitions

```python
# station_service/api/schemas/manual.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ManualCommandParameter(BaseModel):
    """Parameter definition for manual command."""
    name: str
    display_name: str
    type: str  # string, number, boolean, select, range
    required: bool = False
    default: Optional[Any] = None
    unit: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None

class ManualCommand(BaseModel):
    """Manual control command definition."""
    name: str
    display_name: str
    category: str  # measurement, control, configuration, diagnostic
    description: str
    parameters: List[ManualCommandParameter]
    return_type: Optional[str] = None
    return_unit: Optional[str] = None
    async_method: bool = True

class HardwareCommands(BaseModel):
    """Commands available for a hardware device."""
    hardware_id: str
    driver: str
    commands: List[ManualCommand]

class ManualStepConfig(BaseModel):
    """Manual mode configuration for a step."""
    skippable: bool
    auto_only: bool
    prompt: Optional[str]
    pause_before: bool
    pause_after: bool
    parameter_overrides: List[str]

class ManualStepInfo(BaseModel):
    """Step information for manual execution."""
    name: str
    display_name: str
    order: int
    timeout: float
    manual: ManualStepConfig
    status: str  # pending, running, completed, failed, skipped
    result: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None

class ManualStepRequest(BaseModel):
    """Request body for manual step execution."""
    parameters: Optional[Dict[str, Any]] = None
```

---

## 9. Implementation Phases

### Phase 1: Device Panel & Command Discovery (Week 1)
- [ ] Implement `useHardwareCommands` hook
- [ ] Create command introspection in backend
- [ ] Build DevicePanel component
- [ ] Add hardware status polling

### Phase 2: Smart Command Panel (Week 2)
- [ ] Build CommandPanel with category tabs
- [ ] Implement SmartInput components
- [ ] Add parameter validation
- [ ] Create PresetManager

### Phase 3: Result Visualization (Week 3)
- [ ] Build ResultPanel with chart/table/raw views
- [ ] Implement result history storage
- [ ] Add export functionality
- [ ] Create real-time value display

### Phase 4: Manual Sequence Mode (Week 4)
- [ ] Enhance manifest schema
- [ ] Implement ManualSequenceExecutor
- [ ] Build ManualSequencePanel
- [ ] Add step-level API endpoints

### Phase 5: Integration & Polish (Week 5)
- [ ] Integrate all components
- [ ] Add WebSocket updates for manual mode
- [ ] Implement preset persistence
- [ ] Add keyboard shortcuts
- [ ] Testing & bug fixes

---

## 10. Migration Notes

### Backward Compatibility
- Existing `ManualControlPage` will be replaced
- Current JSON-based control will remain as "Advanced Mode"
- Existing sequences work without modification
- New `manual` section in manifest is optional

### Breaking Changes
None - all changes are additive.

---

## 11. Future Enhancements

1. **Interactive Mode**: Add support for operator prompts during sequence execution
2. **Recording Mode**: Record manual operations and convert to sequence
3. **Script Generation**: Generate Python scripts from manual command history
4. **Remote Control**: WebSocket-based real-time control for remote debugging
5. **Multi-Device Coordination**: Execute commands on multiple devices simultaneously
