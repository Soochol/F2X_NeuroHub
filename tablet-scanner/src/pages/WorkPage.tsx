/**
 * Main Work Page - 착공/완공 페이지 (원스캔 퀵모드)
 *
 * 새로운 워크플로우:
 * 1. WIP 바코드 스캔 (먼저)
 * 2. Flow UI 표시 + 다음 공정 자동 선택
 * 3. 착공 또는 완공 처리
 * 4. 다음 WIP 스캔 유도
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Camera,
  Keyboard,
  QrCode,
  Loader2,
} from 'lucide-react';
import { ScannerModal } from '@/components/scanner';
import { PageContainer, Header } from '@/components/layout';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FadeIn } from '@/components/animations';
import { useToast } from '@/components/feedback';
import { useFeedback } from '@/hooks';
import { useAppStore } from '@/store/appStore';
import { useUIStore } from '@/store/slices/uiSlice';
import { wipApi, processApi, processOperationsApi, getErrorMessage } from '@/api/client';
import {
  addToQueue,
  getQueueCount,
  processQueue,
  isOnline,
  setupNetworkListeners,
} from '@/services/offlineQueue';
import { cn } from '@/lib/cn';
import type {
  WIPTrace,
  ProcessResult,
  ProcessStartRequest,
  ProcessCompleteRequest,
} from '@/types';
import {
  WIP_ID_PATTERN,
  QUEUE_CHECK_INTERVAL_MS,
  AUTO_START_DELAY_MS,
} from '@/constants';
import { logger } from '@/services/logger';

// Work Page Components
import { QuickWorkPanel } from '@/components/work';

export const WorkPage: React.FC = () => {
  const {
    user,
    settings,
    processes,
    setProcesses,
    addScanResult,
  } = useAppStore();

  const { theme, toggleTheme } = useUIStore();

  // Network & sync state (used for future sync status UI)
  const [_networkStatus, setNetworkStatus] = useState<'online' | 'offline'>(
    isOnline() ? 'online' : 'offline'
  );
  const [_queueCount, setQueueCount] = useState(0);
  const [_syncProgress, setSyncProgress] = useState(0);
  const [_isSyncing, setIsSyncing] = useState(false);

  // Suppress unused variable warnings - these are for future sync UI
  void _networkStatus;
  void _queueCount;
  void _syncProgress;
  void _isSyncing;

  // Scan state
  const [showScannerModal, setShowScannerModal] = useState(false);
  const [wipInput, setWipInput] = useState('');
  const [isLoadingWip, setIsLoadingWip] = useState(false);

  // Quick Work Modal state
  const [currentTrace, setCurrentTrace] = useState<WIPTrace | null>(null);


  // Refs
  const processingRef = useRef(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const toast = useToast();
  const {
    success: feedbackSuccess,
    error: feedbackError,
    warning: feedbackWarning,
    scan: feedbackScan,
    soundEnabled,
    toggleSound,
  } = useFeedback();

  // ====================================
  // Network & Queue Effects
  // ====================================
  useEffect(() => {
    const cleanup = setupNetworkListeners(
      async () => {
        setNetworkStatus('online');
        toast.success('네트워크 연결됨', '대기 중인 작업을 처리합니다', 3000);
        await syncOfflineQueue();
      },
      () => {
        setNetworkStatus('offline');
        toast.warning('오프라인 모드', '작업은 저장 후 연결 시 전송됩니다', 5000);
        feedbackWarning();
      }
    );
    return cleanup;
  }, []);

  useEffect(() => {
    const updateQueueCount = async () => {
      const count = await getQueueCount();
      setQueueCount(count);
    };
    updateQueueCount();
    const interval = setInterval(updateQueueCount, QUEUE_CHECK_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  // ====================================
  // Load Processes
  // ====================================
  useEffect(() => {
    const loadProcesses = async () => {
      try {
        const data = await processApi.getAll();
        setProcesses(data);
      } catch (err) {
        logger.error('Failed to load processes', err);
        toast.error('Process Load Failed', getErrorMessage(err), 4000);
      }
    };
    if (processes.length === 0) {
      loadProcesses();
    }
  }, [processes.length, setProcesses, toast]);

  // ====================================
  // Sync Functions
  // ====================================
  const syncOfflineQueue = async () => {
    setIsSyncing(true);
    setSyncProgress(0);

    const result = await processQueue(
      async (data: ProcessStartRequest) => {
        try {
          await processOperationsApi.start(data);
          return true;
        } catch {
          return false;
        }
      },
      async (data: ProcessCompleteRequest) => {
        try {
          await processOperationsApi.complete(data);
          return true;
        } catch {
          return false;
        }
      }
    );

    setSyncProgress(100);
    setIsSyncing(false);

    if (result.success > 0 || result.failed > 0) {
      if (result.failed > 0) {
        toast.warning('Offline Syncing', `${result.success} success, ${result.failed} failed`, 4000);
      } else {
        toast.success('Sync Complete', `${result.success} items processed`, 4000);
      }
    }

    const count = await getQueueCount();
    setQueueCount(count);
  };

  // ====================================
  // WIP Scan Handler
  // ====================================
  const handleWipScan = useCallback(
    async (wipId: string) => {
      if (processingRef.current) return;
      processingRef.current = true;

      // WIP ID 검증
      if (!WIP_ID_PATTERN.test(wipId)) {
        toast.error('Invalid Format', 'WIP ID format is invalid', 3000);
        await feedbackError();
        processingRef.current = false;
        return;
      }

      await feedbackScan();
      setIsLoadingWip(true);
      setShowScannerModal(false);
      setWipInput('');

      try {
        // WIP Trace 조회
        const trace = await wipApi.getTrace(wipId);
        setCurrentTrace(trace);
        toast.success('WIP Loaded', wipId, 2000);

        // Refresh process definitions to sync defect items from Admin
        let currentProcesses = processes;
        try {
          const freshProcesses = await processApi.getAll();
          setProcesses(freshProcesses);
          currentProcesses = freshProcesses;
        } catch (syncErr) {
          logger.error('Failed to sync processes on scan', syncErr);
        }

        // 바로 착공 시작 로직 (Auto-Start)
        // 1. 이미 진행 중인 공정이 있는지 확인
        const inProgress = trace.process_history.find(h => h.start_time && !h.complete_time);

        if (!inProgress) {
          // 2. 다음 공정 찾기 - API에서 가져온 공정 목록 사용 (동적)
          const completedNumbers = new Set(
            trace.process_history
              .filter(h => h.complete_time && h.result === 'PASS')
              .map(h => h.process_number)
          );

          // 공정 번호로 정렬된 목록에서 미완료 공정 찾기
          const sortedProcesses = [...currentProcesses].sort((a, b) => a.process_number - b.process_number);
          const nextProcess = sortedProcesses.find(p => !completedNumbers.has(p.process_number));

          if (nextProcess) {
            // 약간의 지연 후 자동 착공 (UI 업데이트 보장)
            setTimeout(async () => {
              await handleStart(nextProcess.id, trace);
            }, AUTO_START_DELAY_MS);
          }
        }
      } catch (err) {
        const errorMsg = getErrorMessage(err);
        toast.error('WIP Load Failed', errorMsg, 4000);
        await feedbackError();
      } finally {
        setIsLoadingWip(false);
        processingRef.current = false;
      }
    },
    [toast, feedbackScan, feedbackError]
  );

  // ====================================
  // Quick Work Modal Handlers
  // ====================================
  const handleStart = async (processId: number, traceOverride?: WIPTrace): Promise<boolean> => {
    const workerId = settings.workerId || user?.username;
    const targetTrace = traceOverride || currentTrace;

    if (!targetTrace) {
      toast.error('No WIP Loaded', 'Please scan a WIP first', 3000);
      return false;
    }
    if (!workerId) {
      toast.error('No Worker identified', 'Please login or set Operator ID', 3000);
      return false;
    }

    const startData: ProcessStartRequest = {
      wip_id: targetTrace.wip_id,
      process_id: String(processId),
      worker_id: workerId,
      equipment_id: settings.equipmentId || undefined,
      line_id: settings.lineId || undefined,
    };

    try {
      if (!isOnline()) {
        await addToQueue('start', startData);
        const count = await getQueueCount();
        setQueueCount(count);
        toast.warning('Offline Save', `Pending: ${count} items`, 3000);
        await feedbackWarning();
      } else {
        await processOperationsApi.start(startData);
        toast.success('Operation Started', targetTrace.wip_id, 2000);
        await feedbackSuccess();
      }

      // Trace 새로고침
      const updatedTrace = await wipApi.getTrace(targetTrace.wip_id);
      setCurrentTrace(updatedTrace);

      const process = processes.find((p) => p.id === processId);
      addScanResult({
        wipId: targetTrace.wip_id,
        timestamp: new Date(),
        action: 'start',
        success: true,
        message: 'Started',
        processNumber: process?.process_number,
      });

      return true;
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      toast.error('Start Failed', errorMsg, 4000);
      await feedbackError();
      return false;
    }
  };

  const handleComplete = async (
    processId: number,
    result: ProcessResult,
    measurements: Record<string, unknown>,
    defectData?: { defect_codes: string[], notes?: string }
  ): Promise<boolean> => {
    const workerId = settings.workerId || user?.username;
    if (!currentTrace) {
      toast.error('No WIP Loaded', 'Please scan a WIP first', 3000);
      return false;
    }
    if (!workerId) {
      toast.error('No Worker identified', 'Please login or set Operator ID', 3000);
      return false;
    }

    const completeData: ProcessCompleteRequest = {
      wip_id: currentTrace.wip_id,
      process_id: String(processId),
      worker_id: workerId,
      result,
      measurements: Object.keys(measurements).length > 0 ? measurements : undefined,
      defect_data: defectData,
    };

    try {
      if (!isOnline()) {
        await addToQueue('complete', completeData);
        const count = await getQueueCount();
        setQueueCount(count);
        const resultText = result === 'PASS' ? 'PASS' : 'FAIL';
        toast.warning(`Finish (${resultText}) Saved`, `Pending: ${count} items`, 3000);
        await feedbackWarning();
      } else {
        await processOperationsApi.complete(completeData);
        const resultText = result === 'PASS' ? 'PASS' : 'FAIL';
        if (result === 'PASS') {
          toast.success(`Finished (${resultText})`, currentTrace?.wip_id || '', 2000);
          await feedbackSuccess();
        } else {
          toast.error(`Finished (${resultText})`, currentTrace?.wip_id || '', 2000);
          await feedbackError();
        }
      }

      // Trace 새로고침
      const updatedTrace = await wipApi.getTrace(currentTrace.wip_id);
      setCurrentTrace(updatedTrace);

      const process = processes.find((p) => p.id === processId);
      addScanResult({
        wipId: currentTrace.wip_id,
        timestamp: new Date(),
        action: 'complete',
        success: true,
        message: `Finished (${result})`,
        processNumber: process?.process_number,
      });

      return true;
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      toast.error('Finish Failed', errorMsg, 4000);
      await feedbackError();
      return false;
    }
  };

  const handleScanNext = () => {
    setCurrentTrace(null);
    // 바로 스캔 모달 열기
    setTimeout(() => setShowScannerModal(true), AUTO_START_DELAY_MS);
  };


  // ====================================
  // Manual Input Handler
  // ====================================
  const handleManualSubmit = () => {
    if (wipInput.trim()) {
      handleWipScan(wipInput.trim());
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && wipInput.trim()) {
      handleManualSubmit();
    }
  };

  // ====================================
  // Render
  // ====================================
  return (
    <PageContainer className="p-0 lg:p-6 overflow-hidden flex flex-col h-screen">
      {/* Header */}
      <div className="px-6 pt-6 lg:px-0 lg:pt-0">
        <Header
          title="F2X NEUROHUB"
          subtitle={user?.full_name || user?.username}
          soundEnabled={soundEnabled}
          onToggleSound={toggleSound}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </div>

      <div className="flex-1 overflow-auto px-6 pb-6 lg:px-0 lg:pb-0">
        <div className="flex flex-col gap-8">
          {/* Main Action Area: Scan Area or Active Job Panel */}
          <div className="w-full space-y-6">
            {/* Removed top-level SyncStatusBar to save space */}

            {/* Conditional Rendering: Scan Mode vs. Active Job Mode */}
            {currentTrace ? (
              <FadeIn>
                <QuickWorkPanel
                  trace={currentTrace}
                  processes={processes}
                  onStart={handleStart}
                  onComplete={handleComplete}
                  onScanNext={handleScanNext}
                  onCancel={() => setCurrentTrace(null)}
                />
              </FadeIn>
            ) : (
              <FadeIn>
                <Card variant="glass" className="relative overflow-hidden group border-white/10 shadow-2xl">
                  {/* Decorative Background Glow */}
                  <div className="absolute -top-32 -right-32 w-80 h-80 bg-primary-500/10 rounded-full blur-[100px] group-hover:bg-primary-500/20 transition-all duration-700" />
                  <div className="absolute -bottom-32 -left-32 w-80 h-80 bg-violet-500/5 rounded-full blur-[100px]" />

                  <div className="relative text-center py-12 lg:py-24">
                    {/* Icon with Ring */}
                    <div className="relative w-32 h-32 mx-auto mb-8">
                      <div className="absolute inset-0 bg-primary-500/20 rounded-[2.5rem] animate-pulse" />
                      <div className="relative w-full h-full rounded-[2.5rem] bg-primary-900/40 flex items-center justify-center border border-primary-500/30 shadow-[0_0_40px_rgba(30,58,95,0.4)]">
                        <QrCode className="w-16 h-16 text-primary-400" />
                      </div>
                    </div>

                    {/* Title */}
                    <h2 className="text-3xl lg:text-5xl font-black text-dynamic mb-4 tracking-tighter">
                      READY TO SCAN
                    </h2>
                    <p className="text-neutral-500 mb-12 lg:text-xl font-medium max-w-lg mx-auto leading-relaxed">
                      Scan WIP barcode or enter ID<br />
                      to start production process control.
                    </p>

                    {/* Camera Scan Button */}
                    <div className="max-w-md mx-auto px-6">
                      <button
                        type="button"
                        onClick={() => setShowScannerModal(true)}
                        disabled={isLoadingWip}
                        className={cn(
                          'w-full flex items-center justify-center gap-5',
                          'py-8 px-10 rounded-[2.5rem]',
                          'font-black text-3xl tracking-tight',
                          'transition-all duration-300 relative overflow-hidden group/btn',
                          isLoadingWip
                            ? 'bg-neutral-300 dark:bg-neutral-800 text-neutral-500 cursor-not-allowed shadow-none'
                            : [
                              'btn-action-primary',
                              'shadow-[0_20px_50px_rgba(30,58,95,0.3)]',
                              'hover:scale-[1.02] hover:shadow-[0_0_40px_rgba(30,58,95,0.4)]',
                              'active:scale-[0.96]',
                            ]
                        )}
                      >
                        <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover/btn:translate-x-[100%] transition-transform duration-1000" />
                        {isLoadingWip ? (
                          <Loader2 className="w-10 h-10 animate-spin" />
                        ) : (
                          <Camera className="w-10 h-10" />
                        )}
                        <span>SCAN START</span>
                      </button>
                    </div>

                    {/* Manual Input Section */}
                    <div className="mt-16 lg:mt-32 pt-12 border-t border-dynamic max-w-md mx-auto px-6">
                      <div className="flex items-center gap-3 justify-center text-[10px] text-neutral-500 mb-6 font-black uppercase tracking-[0.3em]">
                        <Keyboard className="w-4 h-4 opacity-70" />
                        <span className="opacity-70">Manual Identifier Entry</span>
                      </div>
                      <div className="flex flex-col gap-4">
                        <Input
                          ref={inputRef}
                          type="text"
                          value={wipInput}
                          onChange={(e) => setWipInput(e.target.value.toUpperCase())}
                          onKeyDown={handleInputKeyDown}
                          placeholder="WIP ID ENTER..."
                          className="w-full font-mono text-center text-2xl rounded-2xl py-6 h-auto transition-all"
                          disabled={isLoadingWip}
                        />
                        <Button
                          variant="ghost"
                          onClick={handleManualSubmit}
                          disabled={!wipInput.trim() || isLoadingWip}
                          isLoading={isLoadingWip}
                          className="w-full rounded-2xl h-auto py-5 font-black text-lg border-main hover:bg-sub"
                        >
                          Verify & Load
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              </FadeIn>
            )}
          </div>

        </div>
      </div>

      {/* Scanner Modal */}
      <ScannerModal
        isOpen={showScannerModal}
        onClose={() => setShowScannerModal(false)}
        onScan={handleWipScan}
        title="WIP Precision Scan"
        autoCloseDelay={500}
      />

    </PageContainer >
  );
};
