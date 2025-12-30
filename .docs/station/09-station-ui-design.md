# 09. Station UI 상세 설계

## 구현 체크리스트

> Phase 5.2 ~ 5.5 - Station UI 핵심 구현

### 5.2 API 클라이언트 구현
- [x] `station_ui/src/api/client.ts` - Axios 인스턴스
- [x] `station_ui/src/api/endpoints/system.ts` - System API
- [x] `station_ui/src/api/endpoints/batches.ts` - Batch API
- [x] `station_ui/src/api/endpoints/sequences.ts` - Sequence API
- [x] `station_ui/src/api/endpoints/results.ts` - Result API
- [x] `station_ui/src/hooks/useWebSocket.ts` - WebSocket 훅

### 5.3 대시보드 페이지
- [x] `station_ui/src/pages/DashboardPage.tsx`
- [x] `station_ui/src/components/molecules/BatchCard.tsx` - Batch 상태 카드
- [x] `station_ui/src/components/atoms/ProgressBar.tsx` - 스텝 진행률
- [x] `station_ui/src/components/organisms/system/SystemStatus.tsx` - 시스템 상태

### 5.4 Batch 제어 UI
- [x] `station_ui/src/pages/BatchesPage.tsx` - Batch 상세 페이지
- [x] `station_ui/src/components/organisms/batches/BatchDetail.tsx` - Batch 상세 (시작/정지 포함)
- [x] `station_ui/src/components/organisms/sequences/ParameterForm.tsx` - 파라미터 입력
- [x] `station_ui/src/components/organisms/hardware/HardwareStatus.tsx` - 하드웨어 상태
- [x] `station_ui/src/components/organisms/logs/ExecutionLog.tsx` - 실행 로그

### 5.5 실시간 업데이트
- [x] `station_ui/src/stores/batchStore.ts` - Zustand 스토어
- [x] `station_ui/src/contexts/WebSocketContext.tsx` - WebSocket 컨텍스트 (Batch 구독 포함)
- [x] WebSocket 이벤트 핸들러 (batch_status, step_start, step_complete)
- [x] `station_ui/src/hooks/usePollingFallback.ts` - 연결 끊김 시 폴링 폴백

### 레이아웃 및 네비게이션
- [x] `station_ui/src/components/layout/Layout.tsx` - 앱 쉘
- [x] `station_ui/src/components/layout/Navigation.tsx` - 탭 네비게이션
- [x] `station_ui/src/components/layout/StatusBar.tsx` - 하단 상태바

---

## 1. Executive Summary

This document provides a comprehensive component design specification for the Station UI, a local web-based interface for monitoring and controlling Station Services in the F2X NeuroHub ecosystem. The design follows established patterns from the existing frontend codebase while introducing station-specific optimizations.

---

## 2. Design Principles

### 2.1 Core Principles

| Principle | Description |
|-----------|-------------|
| **Consistency** | Follow existing F2X NeuroHub frontend patterns (atomic design, hooks, CSS variables) |
| **Real-time First** | WebSocket-based updates with intelligent fallback to polling |
| **Offline Resilient** | Graceful degradation when backend connection is lost |
| **Operator Focused** | Optimized for factory floor operators using touch screens |
| **Theme Aware** | Full dark/light mode support using CSS variables |

### 2.2 Technology Stack Alignment

```
┌────────────────────────────────────────────────────────────┐
│                    Station UI Stack                         │
├────────────────────────────────────────────────────────────┤
│  Framework       │  React 18+ with TypeScript 5+           │
│  Build Tool      │  Vite 5+                                │
│  State Mgmt      │  Zustand (local) + React Query (server) │
│  Styling         │  CSS Variables + Tailwind CSS           │
│  WebSocket       │  socket.io-client                       │
│  Charts          │  Recharts                               │
│  Icons           │  Lucide React                           │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture Overview

### 3.1 High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Station UI Application                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        App Shell (Layout)                        │    │
│  │  ┌──────────┐  ┌────────────────────────────────────────────┐   │    │
│  │  │  Header  │  │              Navigation Tabs               │   │    │
│  │  └──────────┘  └────────────────────────────────────────────┘   │    │
│  │                                                                  │    │
│  │  ┌────────────────────────────────────────────────────────────┐ │    │
│  │  │                     Router / Page Content                   │ │    │
│  │  │                                                             │ │    │
│  │  │   Dashboard │ Batches │ Sequences │ Manual │ Logs │ Settings │    │
│  │  │                                                             │ │    │
│  │  └────────────────────────────────────────────────────────────┘ │    │
│  │                                                                  │    │
│  │  ┌────────────────────────────────────────────────────────────┐ │    │
│  │  │                        Status Bar                          │ │    │
│  │  └────────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      Global Providers                            │    │
│  │  ThemeProvider │ WebSocketProvider │ QueryClientProvider         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Flow Diagram                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐     │
│  │  Station     │     │  WebSocket   │     │     Zustand Store    │     │
│  │  Service     │────>│  Connection  │────>│                      │     │
│  │  (Backend)   │     │  Manager     │     │  - batchStore        │     │
│  └──────────────┘     └──────────────┘     │  - sequenceStore     │     │
│         │                    │              │  - logStore          │     │
│         │                    │              │  - settingsStore     │     │
│         ▼                    │              └──────────────────────┘     │
│  ┌──────────────┐           │                        │                  │
│  │  REST API    │           │                        │                  │
│  │  Client      │           │                        ▼                  │
│  └──────────────┘           │              ┌──────────────────────┐     │
│         │                    │              │    React Components  │     │
│         │                    │              │                      │     │
│         ▼                    └─────────────>│  useSelector hooks   │     │
│  ┌──────────────┐                          │  dispatch actions    │     │
│  │ React Query  │                          └──────────────────────┘     │
│  │ Cache        │────────────────────────────────────│                  │
│  └──────────────┘                                    │                  │
│         │                                            ▼                  │
│         └───────────────────────────────────> UI Render                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Folder Structure

```
station-ui/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── main.tsx                 # Application entry point
│   ├── App.tsx                  # Root component with routing
│   ├── index.css                # Global styles
│   │
│   ├── components/
│   │   ├── atoms/               # Basic building blocks
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── StatusIndicator.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── molecules/           # Composite components
│   │   │   ├── StatsCard.tsx
│   │   │   ├── BatchCard.tsx
│   │   │   ├── StepItem.tsx
│   │   │   ├── LogEntry.tsx
│   │   │   ├── ParameterField.tsx
│   │   │   ├── HardwareStatusCard.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── organisms/           # Complex feature components
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── BatchOverview.tsx
│   │   │   │   ├── RecentActivity.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── batches/
│   │   │   │   ├── BatchList.tsx
│   │   │   │   ├── BatchDetail.tsx
│   │   │   │   ├── BatchControls.tsx
│   │   │   │   ├── StepProgress.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── sequences/
│   │   │   │   ├── SequenceList.tsx
│   │   │   │   ├── SequenceEditor.tsx
│   │   │   │   ├── StepFlow.tsx
│   │   │   │   ├── ParameterEditor.tsx
│   │   │   │   ├── HardwareConfig.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── manual/
│   │   │   │   ├── ManualControl.tsx
│   │   │   │   ├── DevicePanel.tsx
│   │   │   │   ├── CommandExecutor.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── logs/
│   │   │   │   ├── LogViewer.tsx
│   │   │   │   ├── LogTable.tsx
│   │   │   │   ├── ExecutionHistory.tsx
│   │   │   │   ├── LogFilter.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── settings/
│   │   │   │   ├── Settings.tsx
│   │   │   │   ├── StationInfo.tsx
│   │   │   │   ├── BackendConnection.tsx
│   │   │   │   ├── BatchConfig.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── StatusBar.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── common/
│   │       ├── ErrorBoundary.tsx
│   │       ├── Modal.tsx
│   │       ├── ConfirmDialog.tsx
│   │       ├── Toast.tsx
│   │       └── index.ts
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── BatchesPage.tsx
│   │   ├── SequencesPage.tsx
│   │   ├── ManualControlPage.tsx
│   │   ├── LogsPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── index.ts
│   │
│   ├── hooks/
│   │   ├── useWebSocket.ts      # WebSocket connection management
│   │   ├── useBatches.ts        # Batch data operations
│   │   ├── useSequences.ts      # Sequence data operations
│   │   ├── useLogs.ts           # Log data operations
│   │   ├── useManualControl.ts  # Manual control operations
│   │   ├── useSystemInfo.ts     # System information
│   │   └── index.ts
│   │
│   ├── stores/
│   │   ├── batchStore.ts        # Batch state management
│   │   ├── sequenceStore.ts     # Sequence state management
│   │   ├── logStore.ts          # Log state management
│   │   ├── settingsStore.ts     # Settings state management
│   │   ├── connectionStore.ts   # Connection status
│   │   └── index.ts
│   │
│   ├── api/
│   │   ├── client.ts            # Axios client configuration
│   │   ├── batches.ts           # Batch API endpoints
│   │   ├── sequences.ts         # Sequence API endpoints
│   │   ├── results.ts           # Results API endpoints
│   │   ├── logs.ts              # Logs API endpoints
│   │   ├── system.ts            # System API endpoints
│   │   └── index.ts
│   │
│   ├── types/
│   │   ├── batch.ts             # Batch type definitions
│   │   ├── sequence.ts          # Sequence type definitions
│   │   ├── execution.ts         # Execution type definitions
│   │   ├── log.ts               # Log type definitions
│   │   ├── hardware.ts          # Hardware type definitions
│   │   ├── websocket.ts         # WebSocket message types
│   │   ├── api.ts               # API response types
│   │   └── index.ts
│   │
│   ├── contexts/
│   │   ├── ThemeContext.tsx     # Theme provider
│   │   ├── WebSocketContext.tsx # WebSocket provider
│   │   └── index.ts
│   │
│   ├── styles/
│   │   ├── theme.css            # CSS variables (dark/light themes)
│   │   ├── components.css       # Component-specific styles
│   │   └── utilities.css        # Utility classes
│   │
│   └── utils/
│       ├── format.ts            # Formatting utilities
│       ├── validation.ts        # Validation utilities
│       ├── time.ts              # Time-related utilities
│       ├── logger.ts            # Logging utility
│       └── index.ts
│
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── README.md
```

---

## 5. Component Specifications

### 5.1 Atoms (Basic Components)

#### 5.1.1 StatusBadge

```typescript
/**
 * StatusBadge - Displays batch/execution status with appropriate styling
 *
 * @example
 * <StatusBadge status="running" />
 * <StatusBadge status="error" size="lg" />
 */
interface StatusBadgeProps {
  status: 'idle' | 'starting' | 'running' | 'stopping' | 'completed' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

// Color mapping using CSS variables
const statusColors = {
  idle: 'var(--color-gray-400)',
  starting: 'var(--color-info)',
  running: 'var(--color-brand-500)',
  stopping: 'var(--color-warning)',
  completed: 'var(--color-success)',
  error: 'var(--color-error)',
};
```

#### 5.1.2 ProgressBar

```typescript
/**
 * ProgressBar - Visual progress indicator with optional label
 *
 * @example
 * <ProgressBar value={0.75} showLabel />
 * <ProgressBar value={0.5} variant="success" />
 */
interface ProgressBarProps {
  value: number;           // 0.0 - 1.0
  variant?: 'default' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;          // Custom label (e.g., "Step 3/5")
  animated?: boolean;
  className?: string;
}
```

#### 5.1.3 StatusIndicator

```typescript
/**
 * StatusIndicator - Connection/health status dot indicator
 *
 * @example
 * <StatusIndicator status="connected" label="Backend" />
 */
interface StatusIndicatorProps {
  status: 'connected' | 'disconnected' | 'error' | 'loading';
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  pulse?: boolean;         // Animated pulse for active states
}
```

### 5.2 Molecules (Composite Components)

#### 5.2.1 StatsCard

```typescript
/**
 * StatsCard - Dashboard statistics display card
 *
 * @example
 * <StatsCard
 *   title="Running Sequences"
 *   value={3}
 *   icon={<PlayIcon />}
 *   trend={{ direction: 'up', value: 12 }}
 * />
 */
interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  subtitle?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: number;
  };
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error';
  onClick?: () => void;
}
```

#### 5.2.2 BatchCard

```typescript
/**
 * BatchCard - Compact batch status display for list views
 *
 * @example
 * <BatchCard
 *   batch={batchData}
 *   isSelected={selectedId === batch.id}
 *   onSelect={handleSelect}
 * />
 */
interface BatchCardProps {
  batch: Batch;
  isSelected?: boolean;
  onSelect?: (batchId: string) => void;
  onAction?: (action: 'start' | 'stop' | 'pause') => void;
  showControls?: boolean;
  compact?: boolean;
}
```

#### 5.2.3 StepItem

```typescript
/**
 * StepItem - Individual step display in sequence flow
 *
 * @example
 * <StepItem
 *   step={stepData}
 *   status="completed"
 *   duration={2.3}
 * />
 */
interface StepItemProps {
  step: StepSchema;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  duration?: number;
  progress?: number;       // For running steps
  result?: Record<string, any>;
  error?: string;
  isExpanded?: boolean;
  onToggle?: () => void;
}
```

#### 5.2.4 HardwareStatusCard

```typescript
/**
 * HardwareStatusCard - Hardware device status and controls
 *
 * @example
 * <HardwareStatusCard
 *   hardware={hardwareStatus}
 *   onReconnect={handleReconnect}
 * />
 */
interface HardwareStatusCardProps {
  hardware: HardwareStatus;
  showDetails?: boolean;
  onReconnect?: () => void;
  onConfigure?: () => void;
}
```

### 5.3 Organisms (Feature Components)

#### 5.3.1 Dashboard Components

```typescript
/**
 * BatchOverview - Real-time batch status overview with progress bars
 */
interface BatchOverviewProps {
  batches: Batch[];
  onBatchSelect?: (batchId: string) => void;
  maxVisible?: number;     // Limit displayed batches
}

/**
 * RecentActivity - Live activity feed with auto-scroll
 */
interface RecentActivityProps {
  logs: LogEntry[];
  maxItems?: number;
  autoScroll?: boolean;
  onLogClick?: (log: LogEntry) => void;
}
```

#### 5.3.2 Batch Management Components

```typescript
/**
 * BatchList - Selectable list of all batches
 */
interface BatchListProps {
  batches: Batch[];
  selectedId?: string;
  onSelect: (batchId: string) => void;
  filter?: {
    status?: BatchStatus[];
    search?: string;
  };
}

/**
 * BatchDetail - Detailed batch view with execution info
 */
interface BatchDetailProps {
  batchId: string;
  showControls?: boolean;
  showParameters?: boolean;
  showHardware?: boolean;
}

/**
 * BatchControls - Batch control buttons (Start/Stop/Pause)
 */
interface BatchControlsProps {
  batch: Batch;
  onStart: () => void;
  onStop: () => void;
  onPause?: () => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * StepProgress - Visual step execution progress
 */
interface StepProgressProps {
  steps: StepResult[];
  currentIndex: number;
  orientation?: 'horizontal' | 'vertical';
  showDetails?: boolean;
}
```

#### 5.3.3 Sequence Editor Components

```typescript
/**
 * SequenceList - Hierarchical sequence package browser
 */
interface SequenceListProps {
  sequences: SequencePackage[];
  selectedName?: string;
  onSelect: (name: string) => void;
  onRefresh?: () => void;
}

/**
 * SequenceEditor - Full sequence package editor
 */
interface SequenceEditorProps {
  sequence: SequencePackage;
  onSave: (updates: Partial<SequencePackage>) => void;
  onRun?: (batchId: string, parameters: Record<string, any>) => void;
  readOnly?: boolean;
}

/**
 * StepFlow - Visual step flow diagram
 */
interface StepFlowProps {
  steps: StepSchema[];
  onStepSelect?: (stepName: string) => void;
  onReorder?: (steps: StepSchema[]) => void;
  editable?: boolean;
}

/**
 * ParameterEditor - Dynamic parameter form
 */
interface ParameterEditorProps {
  parameters: ParameterSchema[];
  values: Record<string, any>;
  onChange: (values: Record<string, any>) => void;
  errors?: Record<string, string>;
}

/**
 * HardwareConfig - Hardware configuration panel
 */
interface HardwareConfigProps {
  hardware: HardwareSchema[];
  config: Record<string, Record<string, any>>;
  status?: Record<string, HardwareStatus>;
  onChange: (config: Record<string, Record<string, any>>) => void;
}
```

#### 5.3.4 Manual Control Components

```typescript
/**
 * ManualControl - Main manual control interface
 */
interface ManualControlProps {
  batchId: string;
  hardware: HardwareStatus[];
  onCommand: (hardware: string, command: string, params: Record<string, any>) => Promise<any>;
  disabled?: boolean;
}

/**
 * DevicePanel - Individual device control panel
 */
interface DevicePanelProps {
  hardware: HardwareStatus;
  commands: CommandDefinition[];
  onExecute: (command: string, params: Record<string, any>) => Promise<any>;
  recentResults?: CommandResult[];
}

/**
 * CommandExecutor - Single command execution form
 */
interface CommandExecutorProps {
  command: CommandDefinition;
  onExecute: (params: Record<string, any>) => Promise<any>;
  lastResult?: any;
  isLoading?: boolean;
}
```

#### 5.3.5 Log Viewer Components

```typescript
/**
 * LogViewer - Full-featured log viewing interface
 */
interface LogViewerProps {
  initialFilters?: LogFilter;
  onExport?: (format: 'csv' | 'json') => void;
}

/**
 * LogTable - Virtualized log table with filtering
 */
interface LogTableProps {
  logs: LogEntry[];
  filters: LogFilter;
  onFilterChange: (filters: LogFilter) => void;
  onRowClick?: (log: LogEntry) => void;
  isLoading?: boolean;
}

/**
 * LogFilter - Log filtering controls
 */
interface LogFilterProps {
  value: LogFilter;
  batches: { id: string; name: string }[];
  onChange: (filters: LogFilter) => void;
}

interface LogFilter {
  batchId?: string;
  level?: LogLevel[];
  from?: Date;
  to?: Date;
  search?: string;
}

/**
 * ExecutionHistory - Historical execution results table
 */
interface ExecutionHistoryProps {
  results: ExecutionSummary[];
  onSelect: (resultId: string) => void;
  onExport?: (resultId: string) => void;
  isLoading?: boolean;
}
```

#### 5.3.6 Settings Components

```typescript
/**
 * Settings - Main settings page container
 */
interface SettingsProps {
  onSave: () => void;
  onRestart?: () => void;
}

/**
 * StationInfo - Station identification settings
 */
interface StationInfoProps {
  station: Station;
  onChange: (updates: Partial<Station>) => void;
  readOnly?: boolean;
}

/**
 * BackendConnection - Backend connection settings
 */
interface BackendConnectionProps {
  config: BackendConfig;
  status: 'connected' | 'disconnected' | 'error';
  onChange: (config: BackendConfig) => void;
  onTest: () => Promise<boolean>;
}

/**
 * BatchConfig - Batch configuration editor
 */
interface BatchConfigProps {
  batches: BatchConfig[];
  sequences: SequencePackage[];
  onChange: (batches: BatchConfig[]) => void;
  onAdd: () => void;
  onRemove: (batchId: string) => void;
}
```

### 5.4 Layout Components

#### 5.4.1 Layout

```typescript
/**
 * Layout - Main application layout wrapper
 */
interface LayoutProps {
  children: ReactNode;
}

// Layout structure:
// ┌─────────────────────────────────────┐
// │ Header                               │
// ├─────────────────────────────────────┤
// │ Navigation Tabs                      │
// ├─────────────────────────────────────┤
// │                                      │
// │ Main Content (children)              │
// │                                      │
// ├─────────────────────────────────────┤
// │ Status Bar                           │
// └─────────────────────────────────────┘
```

#### 5.4.2 Header

```typescript
/**
 * Header - Application header with station info
 */
interface HeaderProps {
  stationId: string;
  stationName: string;
}
```

#### 5.4.3 Navigation

```typescript
/**
 * Navigation - Tab-based navigation
 */
interface NavigationProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/batches', label: 'Batches', icon: Layers },
  { path: '/sequences', label: 'Sequences', icon: GitBranch },
  { path: '/manual', label: 'Manual', icon: Wrench },
  { path: '/logs', label: 'Logs', icon: FileText },
  { path: '/settings', label: 'Settings', icon: Settings },
];
```

#### 5.4.4 StatusBar

```typescript
/**
 * StatusBar - Bottom status bar with connection info
 */
interface StatusBarProps {
  backendStatus: 'connected' | 'disconnected' | 'error';
  runningBatches: number;
  currentTime?: Date;
}
```

---

## 6. State Management

### 6.1 Zustand Store Design

#### 6.1.1 Batch Store

```typescript
// stores/batchStore.ts

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type { Batch, BatchStatus, StepResult } from '@/types';

interface BatchState {
  // Data
  batches: Map<string, Batch>;
  selectedBatchId: string | null;

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Actions
  setBatches: (batches: Batch[]) => void;
  updateBatch: (batchId: string, updates: Partial<Batch>) => void;
  updateBatchStatus: (batchId: string, status: BatchStatus) => void;
  updateStepProgress: (batchId: string, stepIndex: number, progress: number) => void;
  updateStepResult: (batchId: string, stepResult: StepResult) => void;
  selectBatch: (batchId: string | null) => void;

  // Selectors
  getBatch: (batchId: string) => Batch | undefined;
  getRunningBatches: () => Batch[];
  getSelectedBatch: () => Batch | undefined;
}

export const useBatchStore = create<BatchState>()(
  immer((set, get) => ({
    batches: new Map(),
    selectedBatchId: null,
    isLoading: false,
    error: null,

    setBatches: (batches) => set((state) => {
      state.batches = new Map(batches.map(b => [b.id, b]));
    }),

    updateBatch: (batchId, updates) => set((state) => {
      const batch = state.batches.get(batchId);
      if (batch) {
        state.batches.set(batchId, { ...batch, ...updates });
      }
    }),

    updateBatchStatus: (batchId, status) => set((state) => {
      const batch = state.batches.get(batchId);
      if (batch) {
        batch.status = status;
      }
    }),

    updateStepProgress: (batchId, stepIndex, progress) => set((state) => {
      const batch = state.batches.get(batchId);
      if (batch) {
        batch.stepIndex = stepIndex;
        batch.progress = progress;
      }
    }),

    updateStepResult: (batchId, stepResult) => set((state) => {
      const batch = state.batches.get(batchId);
      if (batch?.execution) {
        batch.execution.steps[stepResult.order - 1] = stepResult;
      }
    }),

    selectBatch: (batchId) => set({ selectedBatchId: batchId }),

    getBatch: (batchId) => get().batches.get(batchId),

    getRunningBatches: () =>
      Array.from(get().batches.values()).filter(b => b.status === 'running'),

    getSelectedBatch: () => {
      const { selectedBatchId, batches } = get();
      return selectedBatchId ? batches.get(selectedBatchId) : undefined;
    },
  }))
);
```

#### 6.1.2 Sequence Store

```typescript
// stores/sequenceStore.ts

interface SequenceState {
  sequences: Map<string, SequencePackage>;
  selectedSequenceName: string | null;
  isLoading: boolean;
  error: string | null;

  setSequences: (sequences: SequencePackage[]) => void;
  updateSequence: (name: string, updates: Partial<SequencePackage>) => void;
  selectSequence: (name: string | null) => void;

  getSequence: (name: string) => SequencePackage | undefined;
  getSelectedSequence: () => SequencePackage | undefined;
}
```

#### 6.1.3 Log Store

```typescript
// stores/logStore.ts

interface LogState {
  logs: LogEntry[];
  maxLogs: number;           // Buffer size limit
  filters: LogFilter;

  addLog: (log: LogEntry) => void;
  addLogs: (logs: LogEntry[]) => void;
  clearLogs: () => void;
  setFilters: (filters: Partial<LogFilter>) => void;

  getFilteredLogs: () => LogEntry[];
}
```

#### 6.1.4 Connection Store

```typescript
// stores/connectionStore.ts

interface ConnectionState {
  websocketStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  backendStatus: 'connected' | 'disconnected' | 'error';
  lastHeartbeat: Date | null;
  reconnectAttempts: number;

  setWebSocketStatus: (status: ConnectionState['websocketStatus']) => void;
  setBackendStatus: (status: ConnectionState['backendStatus']) => void;
  updateHeartbeat: () => void;
  incrementReconnectAttempts: () => void;
  resetReconnectAttempts: () => void;
}
```

### 6.2 React Query Configuration

```typescript
// api/queryClient.ts

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,        // 30 seconds
      gcTime: 5 * 60 * 1000,       // 5 minutes
      retry: 2,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query keys
export const queryKeys = {
  batches: ['batches'] as const,
  batch: (id: string) => ['batches', id] as const,
  sequences: ['sequences'] as const,
  sequence: (name: string) => ['sequences', name] as const,
  results: (filters?: ResultFilter) => ['results', filters] as const,
  result: (id: string) => ['results', id] as const,
  logs: (filters?: LogFilter) => ['logs', filters] as const,
  systemInfo: ['system', 'info'] as const,
  systemHealth: ['system', 'health'] as const,
};
```

---

## 7. WebSocket Integration

### 7.1 WebSocket Context

```typescript
// contexts/WebSocketContext.tsx

interface WebSocketContextValue {
  isConnected: boolean;
  subscribe: (batchIds: string[]) => void;
  unsubscribe: (batchIds: string[]) => void;
}

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const updateBatch = useBatchStore((s) => s.updateBatch);
  const updateBatchStatus = useBatchStore((s) => s.updateBatchStatus);
  const updateStepProgress = useBatchStore((s) => s.updateStepProgress);
  const addLog = useLogStore((s) => s.addLog);
  const setWebSocketStatus = useConnectionStore((s) => s.setWebSocketStatus);

  useEffect(() => {
    const socket = io('/', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 30000,
    });

    socketRef.current = socket;

    // Connection events
    socket.on('connect', () => {
      setIsConnected(true);
      setWebSocketStatus('connected');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      setWebSocketStatus('disconnected');
    });

    socket.on('connect_error', () => {
      setWebSocketStatus('error');
    });

    // Business events
    socket.on('batch_status', (data: BatchStatusMessage) => {
      updateBatch(data.batchId, data.data);
    });

    socket.on('step_start', (data: StepStartMessage) => {
      updateBatch(data.batchId, {
        currentStep: data.data.step,
        stepIndex: data.data.index,
      });
    });

    socket.on('step_complete', (data: StepCompleteMessage) => {
      updateStepProgress(
        data.batchId,
        data.data.index + 1,
        (data.data.index + 1) / data.data.total
      );
    });

    socket.on('sequence_complete', (data: SequenceCompleteMessage) => {
      updateBatch(data.batchId, {
        status: data.data.overallPass ? 'completed' : 'error',
      });
    });

    socket.on('log', (data: LogMessage) => {
      addLog({
        id: Date.now(),
        batchId: data.batchId,
        level: data.data.level,
        message: data.data.message,
        timestamp: new Date(data.data.timestamp),
      });
    });

    socket.on('error', (data: ErrorMessage) => {
      addLog({
        id: Date.now(),
        batchId: data.batchId,
        level: 'error',
        message: `[${data.data.code}] ${data.data.message}`,
        timestamp: new Date(data.data.timestamp),
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const subscribe = useCallback((batchIds: string[]) => {
    socketRef.current?.emit('subscribe', { batch_ids: batchIds });
  }, []);

  const unsubscribe = useCallback((batchIds: string[]) => {
    socketRef.current?.emit('unsubscribe', { batch_ids: batchIds });
  }, []);

  return (
    <WebSocketContext.Provider value={{ isConnected, subscribe, unsubscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
};
```

### 7.2 WebSocket Hook

```typescript
// hooks/useWebSocket.ts

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
}

// Batch-specific subscription hook
export function useBatchSubscription(batchIds: string[]) {
  const { subscribe, unsubscribe, isConnected } = useWebSocket();

  useEffect(() => {
    if (isConnected && batchIds.length > 0) {
      subscribe(batchIds);

      return () => {
        unsubscribe(batchIds);
      };
    }
  }, [isConnected, batchIds.join(',')]);
}
```

---

## 8. API Client Design

### 8.1 Base Client Configuration

```typescript
// api/client.ts

import axios, { AxiosInstance, AxiosError } from 'axios';
import { logger } from '@/utils/logger';

const BASE_URL = '/api';

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Unwrap success response
    if (response.data?.success) {
      return response.data.data;
    }
    return response.data;
  },
  (error: AxiosError<ApiErrorResponse>) => {
    const errorResponse = error.response?.data;

    logger.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      code: errorResponse?.error?.code,
      message: errorResponse?.error?.message,
    });

    // Transform to standardized error
    const apiError: ApiError = {
      code: errorResponse?.error?.code || 'UNKNOWN_ERROR',
      message: errorResponse?.error?.message || error.message,
      status: error.response?.status || 500,
    };

    return Promise.reject(apiError);
  }
);
```

### 8.2 API Endpoint Modules

```typescript
// api/batches.ts

export const batchesApi = {
  getAll: async (): Promise<Batch[]> => {
    return apiClient.get('/batches');
  },

  getById: async (batchId: string): Promise<BatchDetail> => {
    return apiClient.get(`/batches/${batchId}`);
  },

  start: async (batchId: string): Promise<{ batchId: string; status: string; pid: number }> => {
    return apiClient.post(`/batches/${batchId}/start`);
  },

  stop: async (batchId: string): Promise<{ batchId: string; status: string }> => {
    return apiClient.post(`/batches/${batchId}/stop`);
  },

  startSequence: async (
    batchId: string,
    parameters: Record<string, any>
  ): Promise<{ batchId: string; executionId: string; status: string }> => {
    return apiClient.post(`/batches/${batchId}/sequence/start`, { parameters });
  },

  stopSequence: async (batchId: string): Promise<{ batchId: string; status: string }> => {
    return apiClient.post(`/batches/${batchId}/sequence/stop`);
  },

  executeManualCommand: async (
    batchId: string,
    hardware: string,
    command: string,
    params: Record<string, any>
  ): Promise<ManualCommandResult> => {
    return apiClient.post(`/batches/${batchId}/manual`, {
      hardware,
      command,
      params,
    });
  },
};
```

```typescript
// api/sequences.ts

export const sequencesApi = {
  getAll: async (): Promise<SequencePackage[]> => {
    return apiClient.get('/sequences');
  },

  getByName: async (name: string): Promise<SequencePackage> => {
    return apiClient.get(`/sequences/${name}`);
  },

  update: async (
    name: string,
    updates: SequenceUpdateRequest
  ): Promise<{ name: string; version: string; updatedAt: string }> => {
    return apiClient.put(`/sequences/${name}`, updates);
  },
};
```

```typescript
// api/results.ts

export const resultsApi = {
  getAll: async (params?: ResultQueryParams): Promise<PaginatedResponse<ExecutionSummary>> => {
    return apiClient.get('/results', { params });
  },

  getById: async (resultId: string): Promise<ExecutionResult> => {
    return apiClient.get(`/results/${resultId}`);
  },

  export: async (resultId: string, format: 'json' | 'csv'): Promise<Blob> => {
    const response = await apiClient.get(`/results/${resultId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response;
  },
};
```

```typescript
// api/system.ts

export const systemApi = {
  getInfo: async (): Promise<SystemInfo> => {
    return apiClient.get('/system/info');
  },

  getHealth: async (): Promise<SystemHealth> => {
    return apiClient.get('/system/health');
  },
};
```

---

## 9. Type Definitions

### 9.1 Core Types

```typescript
// types/batch.ts

export type BatchStatus = 'idle' | 'starting' | 'running' | 'stopping' | 'completed' | 'error';

export interface Batch {
  id: string;
  name: string;
  status: BatchStatus;
  sequenceName?: string;
  sequenceVersion?: string;
  sequencePackage: string;
  currentStep?: string;
  stepIndex: number;
  totalSteps: number;
  progress: number;
  startedAt?: Date;
  elapsed: number;
  hardwareConfig: Record<string, Record<string, any>>;
  autoStart: boolean;
  pid?: number;
}

export interface BatchDetail extends Batch {
  parameters: Record<string, any>;
  hardwareStatus: Record<string, HardwareStatus>;
  execution?: ExecutionStatus;
}
```

```typescript
// types/sequence.ts

export interface ParameterSchema {
  name: string;
  displayName: string;
  type: 'float' | 'integer' | 'string' | 'boolean';
  default: any;
  min?: number;
  max?: number;
  options?: string[];
  unit?: string;
  description?: string;
}

export interface HardwareSchema {
  id: string;
  displayName: string;
  driver: string;
  className: string;
  description?: string;
  configSchema: Record<string, ConfigFieldSchema>;
}

export interface StepSchema {
  order: number;
  name: string;
  displayName: string;
  description: string;
  timeout: number;
  retry: number;
  cleanup: boolean;
  condition?: string;
}

export interface SequencePackage {
  name: string;
  version: string;
  displayName: string;
  description: string;
  author?: string;
  createdAt?: string;
  updatedAt?: string;
  path: string;
  hardware: HardwareSchema[];
  parameters: ParameterSchema[];
  steps: StepSchema[];
}
```

```typescript
// types/execution.ts

export type ExecutionStatus = 'running' | 'completed' | 'failed' | 'stopped';
export type StepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

export interface StepResult {
  name: string;
  order: number;
  status: StepStatus;
  pass: boolean;
  duration?: number;
  startedAt?: Date;
  completedAt?: Date;
  result?: Record<string, any>;
  error?: string;
}

export interface ExecutionResult {
  id: string;
  batchId: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ExecutionStatus;
  overallPass: boolean;
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  parameters: Record<string, any>;
  steps: StepResult[];
  syncedAt?: Date;
}

export interface ExecutionSummary {
  id: string;
  batchId: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ExecutionStatus;
  overallPass: boolean;
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  synced: boolean;
}
```

```typescript
// types/hardware.ts

export type HardwareConnectionStatus = 'connected' | 'disconnected' | 'error';

export interface HardwareStatus {
  id: string;
  driver: string;
  status: HardwareConnectionStatus;
  connected: boolean;
  lastError?: string;
  config: Record<string, any>;
  info?: Record<string, any>;
}

export interface CommandDefinition {
  name: string;
  displayName: string;
  description?: string;
  params: ParameterSchema[];
}

export interface ManualCommandResult {
  hardware: string;
  command: string;
  result: Record<string, any>;
}
```

```typescript
// types/log.ts

export type LogLevel = 'debug' | 'info' | 'warning' | 'error';

export interface LogEntry {
  id: number;
  batchId: string;
  executionId?: string;
  level: LogLevel;
  message: string;
  timestamp: Date;
}

export interface LogFilter {
  batchId?: string;
  level?: LogLevel[];
  from?: Date;
  to?: Date;
  search?: string;
}
```

```typescript
// types/websocket.ts

export interface BatchStatusMessage {
  type: 'batch_status';
  batchId: string;
  data: {
    status: BatchStatus;
    currentStep?: string;
    stepIndex: number;
    progress: number;
  };
}

export interface StepStartMessage {
  type: 'step_start';
  batchId: string;
  data: {
    step: string;
    index: number;
    total: number;
  };
}

export interface StepCompleteMessage {
  type: 'step_complete';
  batchId: string;
  data: {
    step: string;
    index: number;
    duration: number;
    pass: boolean;
    result?: Record<string, any>;
  };
}

export interface SequenceCompleteMessage {
  type: 'sequence_complete';
  batchId: string;
  data: {
    executionId: string;
    overallPass: boolean;
    duration: number;
    steps: StepResult[];
  };
}

export interface LogMessage {
  type: 'log';
  batchId: string;
  data: {
    level: LogLevel;
    message: string;
    timestamp: string;
  };
}

export interface ErrorMessage {
  type: 'error';
  batchId: string;
  data: {
    code: string;
    message: string;
    step?: string;
    timestamp: string;
  };
}

export type ServerMessage =
  | BatchStatusMessage
  | StepStartMessage
  | StepCompleteMessage
  | SequenceCompleteMessage
  | LogMessage
  | ErrorMessage;
```

---

## 10. Custom Hooks

### 10.1 Data Fetching Hooks

```typescript
// hooks/useBatches.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { batchesApi } from '@/api/batches';
import { useBatchStore } from '@/stores/batchStore';
import { queryKeys } from '@/api/queryClient';

export function useBatches() {
  const setBatches = useBatchStore((s) => s.setBatches);

  return useQuery({
    queryKey: queryKeys.batches,
    queryFn: batchesApi.getAll,
    onSuccess: (data) => {
      setBatches(data);
    },
  });
}

export function useBatch(batchId: string) {
  return useQuery({
    queryKey: queryKeys.batch(batchId),
    queryFn: () => batchesApi.getById(batchId),
    enabled: !!batchId,
  });
}

export function useBatchActions(batchId: string) {
  const queryClient = useQueryClient();

  const startMutation = useMutation({
    mutationFn: () => batchesApi.start(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => batchesApi.stop(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batches });
    },
  });

  const startSequenceMutation = useMutation({
    mutationFn: (parameters: Record<string, any>) =>
      batchesApi.startSequence(batchId, parameters),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
    },
  });

  const stopSequenceMutation = useMutation({
    mutationFn: () => batchesApi.stopSequence(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.batch(batchId) });
    },
  });

  return {
    start: startMutation.mutate,
    stop: stopMutation.mutate,
    startSequence: startSequenceMutation.mutate,
    stopSequence: stopSequenceMutation.mutate,
    isStarting: startMutation.isPending,
    isStopping: stopMutation.isPending,
    isStartingSequence: startSequenceMutation.isPending,
    isStoppingSequence: stopSequenceMutation.isPending,
  };
}
```

```typescript
// hooks/useSequences.ts

export function useSequences() {
  const setSequences = useSequenceStore((s) => s.setSequences);

  return useQuery({
    queryKey: queryKeys.sequences,
    queryFn: sequencesApi.getAll,
    onSuccess: (data) => {
      setSequences(data);
    },
  });
}

export function useSequence(name: string) {
  return useQuery({
    queryKey: queryKeys.sequence(name),
    queryFn: () => sequencesApi.getByName(name),
    enabled: !!name,
  });
}

export function useSequenceUpdate(name: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (updates: SequenceUpdateRequest) =>
      sequencesApi.update(name, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sequences });
      queryClient.invalidateQueries({ queryKey: queryKeys.sequence(name) });
    },
  });
}
```

```typescript
// hooks/useLogs.ts

export function useLogs(filters?: LogFilter) {
  const addLogs = useLogStore((s) => s.addLogs);

  return useQuery({
    queryKey: queryKeys.logs(filters),
    queryFn: () => logsApi.getAll(filters),
    onSuccess: (data) => {
      addLogs(data.items);
    },
  });
}

export function useLogStream() {
  const logs = useLogStore((s) => s.logs);
  const filters = useLogStore((s) => s.filters);
  const getFilteredLogs = useLogStore((s) => s.getFilteredLogs);

  return {
    logs: getFilteredLogs(),
    filters,
    allLogs: logs,
  };
}
```

### 10.2 Manual Control Hook

```typescript
// hooks/useManualControl.ts

interface ManualControlState {
  isEnabled: boolean;
  selectedBatchId: string | null;
  recentCommands: CommandResult[];
  isExecuting: boolean;
}

export function useManualControl() {
  const [state, setState] = useState<ManualControlState>({
    isEnabled: false,
    selectedBatchId: null,
    recentCommands: [],
    isExecuting: false,
  });

  const executeMutation = useMutation({
    mutationFn: async ({
      batchId,
      hardware,
      command,
      params,
    }: {
      batchId: string;
      hardware: string;
      command: string;
      params: Record<string, any>;
    }) => {
      return batchesApi.executeManualCommand(batchId, hardware, command, params);
    },
    onMutate: () => {
      setState((s) => ({ ...s, isExecuting: true }));
    },
    onSettled: () => {
      setState((s) => ({ ...s, isExecuting: false }));
    },
    onSuccess: (result) => {
      setState((s) => ({
        ...s,
        recentCommands: [
          { ...result, timestamp: new Date() },
          ...s.recentCommands.slice(0, 9),
        ],
      }));
    },
  });

  const enableManualControl = useCallback((batchId: string) => {
    setState((s) => ({ ...s, isEnabled: true, selectedBatchId: batchId }));
  }, []);

  const disableManualControl = useCallback(() => {
    setState((s) => ({ ...s, isEnabled: false, selectedBatchId: null }));
  }, []);

  const executeCommand = useCallback(
    (hardware: string, command: string, params: Record<string, any>) => {
      if (state.selectedBatchId) {
        executeMutation.mutate({
          batchId: state.selectedBatchId,
          hardware,
          command,
          params,
        });
      }
    },
    [state.selectedBatchId, executeMutation]
  );

  return {
    ...state,
    enableManualControl,
    disableManualControl,
    executeCommand,
    error: executeMutation.error,
  };
}
```

### 10.3 System Info Hook

```typescript
// hooks/useSystemInfo.ts

export function useSystemInfo() {
  return useQuery({
    queryKey: queryKeys.systemInfo,
    queryFn: systemApi.getInfo,
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: queryKeys.systemHealth,
    queryFn: systemApi.getHealth,
    refetchInterval: 10 * 1000, // Poll every 10 seconds
  });
}
```

---

## 11. Styling System

### 11.1 CSS Variables (Theme)

```css
/* styles/theme.css */

:root {
  /* Brand Colors (Inherit from NeuroHub) */
  --color-brand-50: #e8faf2;
  --color-brand-100: #c4f2de;
  --color-brand-200: #9de9c7;
  --color-brand-300: #6fdead;
  --color-brand-400: #4ed499;
  --color-brand-500: #3ecf8e;
  --color-brand-600: #38b87f;
  --color-brand-700: #2f9e6d;
  --color-brand-800: #27835a;
  --color-brand-900: #1a5c3f;

  /* Semantic Colors */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Status Colors */
  --color-status-idle: var(--color-gray-400);
  --color-status-starting: var(--color-info);
  --color-status-running: var(--color-brand-500);
  --color-status-stopping: var(--color-warning);
  --color-status-completed: var(--color-success);
  --color-status-error: var(--color-error);
}

/* Dark Theme (Default) */
[data-theme="dark"] {
  /* Backgrounds */
  --color-bg-primary: #0a0a0a;
  --color-bg-secondary: #111111;
  --color-bg-tertiary: #1a1a1a;
  --color-bg-elevated: #222222;
  --color-bg-overlay: rgba(0, 0, 0, 0.8);

  /* Text */
  --color-text-primary: #ffffff;
  --color-text-secondary: #a1a1aa;
  --color-text-tertiary: #71717a;
  --color-text-disabled: #52525b;

  /* Borders */
  --color-border-default: #27272a;
  --color-border-subtle: #1f1f23;
  --color-border-strong: #3f3f46;

  /* Gray Scale */
  --color-gray-50: #fafafa;
  --color-gray-100: #f4f4f5;
  --color-gray-200: #e4e4e7;
  --color-gray-300: #d4d4d8;
  --color-gray-400: #a1a1aa;
  --color-gray-500: #71717a;
  --color-gray-600: #52525b;
  --color-gray-700: #3f3f46;
  --color-gray-800: #27272a;
  --color-gray-900: #18181b;
}

/* Light Theme */
[data-theme="light"] {
  /* Backgrounds */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f4f4f5;
  --color-bg-tertiary: #e4e4e7;
  --color-bg-elevated: #ffffff;
  --color-bg-overlay: rgba(255, 255, 255, 0.9);

  /* Text */
  --color-text-primary: #18181b;
  --color-text-secondary: #52525b;
  --color-text-tertiary: #71717a;
  --color-text-disabled: #a1a1aa;

  /* Borders */
  --color-border-default: #e4e4e7;
  --color-border-subtle: #f4f4f5;
  --color-border-strong: #d4d4d8;
}

/* Component Tokens */
:root {
  /* Border Radius */
  --radius-sm: 4px;
  --radius-base: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### 11.2 Component Styling Patterns

```typescript
// Inline styles with CSS variables (for atoms)
const buttonStyles: CSSProperties = {
  backgroundColor: 'var(--color-brand-500)',
  color: 'var(--color-text-inverse)',
  padding: '8px 16px',
  borderRadius: 'var(--radius-base)',
  transition: 'var(--transition-base)',
};

// CSS Modules (for complex organisms)
// BatchDetail.module.css
.container {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stepList {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
```

---

## 12. Routing Configuration

```typescript
// App.tsx

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { WebSocketProvider } from '@/contexts/WebSocketContext';
import { queryClient } from '@/api/queryClient';
import { Layout } from '@/components/layout';
import {
  DashboardPage,
  BatchesPage,
  SequencesPage,
  ManualControlPage,
  LogsPage,
  SettingsPage,
} from '@/pages';

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <WebSocketProvider>
          <BrowserRouter>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/batches" element={<BatchesPage />} />
                <Route path="/batches/:batchId" element={<BatchesPage />} />
                <Route path="/sequences" element={<SequencesPage />} />
                <Route path="/sequences/:sequenceName" element={<SequencesPage />} />
                <Route path="/manual" element={<ManualControlPage />} />
                <Route path="/logs" element={<LogsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </BrowserRouter>
        </WebSocketProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

---

## 13. Build Configuration

### 13.1 Vite Configuration

```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  build: {
    outDir: '../station-service/static',
    emptyOutDir: true,
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          query: ['@tanstack/react-query'],
          state: ['zustand'],
          charts: ['recharts'],
        },
      },
    },
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
});
```

### 13.2 TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 14. Testing Strategy

### 14.1 Test Structure

```
station-ui/
├── src/
│   ├── components/
│   │   └── atoms/
│   │       ├── Button.tsx
│   │       └── __tests__/
│   │           └── Button.test.tsx
│   ├── hooks/
│   │   └── __tests__/
│   │       └── useBatches.test.ts
│   └── stores/
│       └── __tests__/
│           └── batchStore.test.ts
├── tests/
│   ├── setup.ts
│   └── e2e/
│       ├── dashboard.spec.ts
│       └── batches.spec.ts
```

### 14.2 Testing Guidelines

| Test Type | Tool | Focus |
|-----------|------|-------|
| Unit Tests | Vitest + Testing Library | Components, Hooks, Stores |
| Integration Tests | Vitest + MSW | API interactions |
| E2E Tests | Playwright | Critical user flows |
| Visual Tests | Storybook | Component documentation |

---

## 15. Performance Considerations

### 15.1 Optimization Strategies

| Area | Strategy |
|------|----------|
| **Bundle Size** | Code splitting with React.lazy, tree shaking |
| **Rendering** | React.memo for list items, virtualization for logs |
| **State** | Zustand selectors to prevent unnecessary re-renders |
| **Network** | React Query caching, WebSocket for real-time |
| **Images** | SVG icons (Lucide), lazy loading |

### 15.2 Bundle Size Budget

| Chunk | Target Size |
|-------|-------------|
| Main bundle | < 100KB gzipped |
| Vendor chunk | < 150KB gzipped |
| Total initial | < 300KB gzipped |

---

## 16. Accessibility (A11y)

### 16.1 Requirements

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Readers**: Proper ARIA labels and roles
- **Color Contrast**: WCAG 2.1 AA compliance
- **Focus Management**: Visible focus indicators
- **Responsive**: Support for 150%+ zoom

### 16.2 Implementation Checklist

- [ ] Use semantic HTML elements
- [ ] Add aria-label to icon-only buttons
- [ ] Implement focus trapping in modals
- [ ] Provide skip navigation links
- [ ] Test with screen reader (VoiceOver/NVDA)

---

## 17. Implementation Phases

### Phase 1: Foundation
- Project setup (Vite, TypeScript, Tailwind)
- Theme system and CSS variables
- Core atoms (Button, Input, Select, StatusBadge)
- API client and type definitions
- WebSocket connection manager

### Phase 2: Core Features
- Zustand stores (batch, sequence, log)
- Layout components (Header, Navigation, StatusBar)
- Dashboard page with BatchOverview
- Batch list and detail views
- Real-time updates integration

### Phase 3: Advanced Features
- Sequence editor with StepFlow
- Manual control interface
- Log viewer with filtering
- Settings page

### Phase 4: Polish
- Error boundaries and error states
- Loading states and skeletons
- Accessibility improvements
- Performance optimization
- E2E testing

---

## 18. Appendix

### A. File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `BatchCard.tsx` |
| Hooks | camelCase with `use` | `useBatches.ts` |
| Stores | camelCase with `Store` | `batchStore.ts` |
| Types | PascalCase | `Batch.ts` |
| Utils | camelCase | `format.ts` |
| CSS Modules | `ComponentName.module.css` | `BatchCard.module.css` |

### B. Component Documentation Standard

```typescript
/**
 * ComponentName - Brief description of what this component does
 *
 * Detailed description if needed, including:
 * - Key behaviors
 * - State management notes
 * - Performance considerations
 *
 * @example
 * ```tsx
 * <ComponentName
 *   prop1="value"
 *   prop2={123}
 *   onAction={handleAction}
 * />
 * ```
 */
```

### C. Related Documentation

- [01-architecture-overview.md](./01-architecture-overview.md) - System architecture
- [04-station-ui.md](./04-station-ui.md) - Original UI specification
- [05-api-specification.md](./05-api-specification.md) - API documentation
- [06-data-models.md](./06-data-models.md) - Data model definitions
