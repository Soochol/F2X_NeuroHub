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
  Clock,
  History,
  Settings,
  RefreshCw,
  QrCode,
  Loader2,
  CheckCircle,
  AlertCircle,
  Play,
  ChevronRight,
} from 'lucide-react';
import { ScannerModal } from '@/components/scanner';
import { PageContainer, Header, BottomSheet } from '@/components/layout';
import { Card, FloatingActionButton, StatusBadge } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FadeIn, SlideUp } from '@/components/animations';
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

// Work Page Components
import { QuickWorkPanel } from '@/components/work';

export const WorkPage: React.FC = () => {
  const {
    user,
    settings,
    processes,
    setProcesses,
    addScanResult,
    scanHistory,
  } = useAppStore();

  const { theme, toggleTheme } = useUIStore();

  // Network & sync state
  const [networkStatus, setNetworkStatus] = useState<'online' | 'offline'>(
    isOnline() ? 'online' : 'offline'
  );
  const [queueCount, setQueueCount] = useState(0);
  const [syncProgress, setSyncProgress] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);

  // Scan state
  const [showScannerModal, setShowScannerModal] = useState(false);
  const [wipInput, setWipInput] = useState('');
  const [isLoadingWip, setIsLoadingWip] = useState(false);

  // Quick Work Modal state
  const [currentTrace, setCurrentTrace] = useState<WIPTrace | null>(null);

  // UI state
  const [showHistorySheet, setShowHistorySheet] = useState(false);

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
    const interval = setInterval(updateQueueCount, 5000);
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
        console.error('Failed to load processes:', err);
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

  const getSyncStatus = () => {
    if (!networkStatus || networkStatus === 'offline') return 'offline';
    if (isSyncing) return 'syncing';
    if (queueCount > 0) return 'pending';
    return 'synced';
  };

  // ====================================
  // WIP Scan Handler
  // ====================================
  const handleWipScan = useCallback(
    async (wipId: string) => {
      if (processingRef.current) return;
      processingRef.current = true;

      // WIP ID 검증
      const wipPattern = /^WIP-[A-Z0-9-]{10,20}-\d{3}$/;
      if (!wipPattern.test(wipId)) {
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
          console.error('Failed to sync processes on scan:', syncErr);
        }

        // 바로 착공 시작 로직 (Auto-Start)
        // 1. 이미 진행 중인 공정이 있는지 확인
        const inProgress = trace.process_history.find(h => h.start_time && !h.complete_time);

        if (!inProgress) {
          // 2. 다음 공정 번호 찾기 (1~8 중 PASS가 아닌 첫 번째)
          const completedNumbers = new Set(
            trace.process_history
              .filter(h => h.complete_time && h.result === 'PASS')
              .map(h => h.process_number)
          );

          let nextNum = null;
          for (let i = 1; i <= 8; i++) {
            if (!completedNumbers.has(i)) {
              nextNum = i;
              break;
            }
          }

          if (nextNum !== null) {
            const nextProcess = currentProcesses.find(p => p.process_number === nextNum);
            if (nextProcess) {
              // 약간의 지연 후 자동 착공 (UI 업데이트 보장)
              setTimeout(async () => {
                await handleStart(nextProcess.id, trace);
              }, 300);
            }
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
    setTimeout(() => setShowScannerModal(true), 300);
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
  // FAB Actions
  // ====================================
  const fabActions = [
    {
      id: 'history',
      icon: <History className="w-5 h-5" />,
      label: '최근 기록',
      onClick: () => setShowHistorySheet(true),
      color: 'neutral' as const,
    },
    {
      id: 'sync',
      icon: <RefreshCw className="w-5 h-5" />,
      label: `동기화 (${queueCount})`,
      onClick: syncOfflineQueue,
      color: queueCount > 0 ? ('warning' as const) : ('neutral' as const),
    },
    {
      id: 'settings',
      icon: <Settings className="w-5 h-5" />,
      label: '설정',
      onClick: () => toast.info('설정', '설정 기능 준비 중', 2000),
      color: 'neutral' as const,
    },
  ];

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
          isOnline={networkStatus === 'online'}
          soundEnabled={soundEnabled}
          onToggleSound={toggleSound}
          queueCount={queueCount}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </div>

      <div className="flex-1 overflow-auto px-6 pb-20 lg:px-0 lg:pb-0">
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
                            ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed shadow-none'
                            : [
                              'bg-gradient-to-r from-primary-600 to-primary-400',
                              'text-white shadow-[0_20px_50px_rgba(30,58,95,0.5)]',
                              'hover:scale-[1.02] hover:shadow-[0_0_40px_rgba(30,58,95,0.6)]',
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

          {/* Operations Center Area (Stacked Below) */}
          <div className="w-full space-y-6">
            <SlideUp delay={200}>
              <div className="flex flex-col h-full space-y-6">
                {/* 1. Statistics Summary Badge Row */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="glass-card p-5 border-primary-500/20 bg-primary-500/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-primary-500/10 blur-2xl rounded-full opacity-50" />
                    <p className="text-[10px] font-black text-primary-400 uppercase tracking-widest mb-1 opacity-70">Today Started</p>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-black text-dynamic">{scanHistory.filter(h => h.action === 'start').length}</span>
                      <span className="text-xs font-bold text-muted mb-1.5 uppercase">Jobs</span>
                    </div>
                  </div>
                  <div className="glass-card p-5 border-success-500/20 bg-success-500/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-success-500/10 blur-2xl rounded-full opacity-50" />
                    <p className="text-[10px] font-black text-success-400 uppercase tracking-widest mb-1 opacity-70">Today Passed</p>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-black text-dynamic">{scanHistory.filter(h => h.success).length}</span>
                      <span className="text-xs font-bold text-muted mb-1.5 uppercase">Units</span>
                    </div>
                  </div>
                </div>

                {/* 2. Unified History & Status Card */}
                <Card variant="glass" className="flex-1 flex flex-col min-h-0 border-main shadow-2xl overflow-hidden">
                  <div className="p-6 border-b border-main bg-sub">
                    <div className="flex items-center justify-between">
                      <h3 className="font-black text-dynamic text-lg uppercase tracking-wider flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20">
                          <History className="w-5 h-5 text-primary-400" />
                        </div>
                        Operations Center
                      </h3>
                      <button
                        onClick={() => setShowHistorySheet(true)}
                        className="text-[11px] font-black text-primary-400 hover:text-dynamic uppercase tracking-widest transition-colors flex items-center gap-1 group"
                      >
                        See All
                        <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                      </button>
                    </div>
                  </div>

                  <div className="flex-1 overflow-auto p-4 custom-scrollbar">
                    <div className="space-y-3">
                      {scanHistory.length === 0 ? (
                        <div className="text-center py-20 text-dim">
                          <div className="w-20 h-20 rounded-full bg-sub border border-dashed border-main flex items-center justify-center mx-auto mb-4 opacity-30">
                            <History className="w-10 h-10" />
                          </div>
                          <p className="font-bold uppercase tracking-widest text-xs">Waiting for first scan...</p>
                        </div>
                      ) : (
                        scanHistory.slice(0, 10).map((item, idx) => (
                          <div
                            key={idx}
                            className={cn(
                              'group flex items-center gap-4 p-4 rounded-2xl transition-all duration-300',
                              'bg-sub border border-main hover:bg-sub/80 hover:border-main hover:translate-x-1',
                              item.success ? 'hover:border-success-500/30' : 'hover:border-danger-500/30'
                            )}
                          >
                            <div className={cn(
                              'w-12 h-12 rounded-xl flex items-center justify-center border-2 shrink-0',
                              item.success
                                ? 'bg-success-500/10 border-success-500/20 text-success-500'
                                : 'bg-danger-500/10 border-danger-500/20 text-danger-500'
                            )}>
                              {item.action === 'start' ? <Play className="w-6 h-6" fill="currentColor" /> : <CheckCircle className="w-6 h-6" />}
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-0.5">
                                <p className="font-mono font-black text-dynamic truncate text-base tracking-tighter">
                                  {item.wipId}
                                </p>
                                <span className="text-[10px] text-neutral-600 font-black">
                                  {new Date(item.timestamp).toLocaleTimeString('ko-KR', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={cn(
                                  'text-[9px] px-2 py-0.5 rounded-md font-black uppercase tracking-wider',
                                  item.action === 'start' ? 'bg-primary-500/20 text-primary-400' : 'bg-violet-500/20 text-violet-400'
                                )}>
                                  {item.action === 'start' ? 'Start' : 'Finish'}
                                </span>
                                <span className="text-[10px] font-bold text-muted uppercase tracking-widest">
                                  {item.processNumber ? `Process ${item.processNumber}` : 'Syncing...'}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Smart Guide Footer Tooltip */}
                  <div className="p-5 mt-auto bg-gradient-to-t from-primary-900/10 to-transparent border-t border-main">
                    <div className="bg-sub p-4 rounded-2xl border border-main flex gap-4">
                      <div className="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center shrink-0 border border-primary-500/20">
                        <AlertCircle className="w-5 h-5 text-primary-400" />
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-black text-dynamic uppercase tracking-widest">Operator Tip</p>
                        <p className="text-[11px] font-medium text-muted leading-relaxed">Verify scan results after operation and maintain 'Access System' log.</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            </SlideUp>
          </div>
        </div>
      </div>

      {/* Floating Action Button - Tablet optimized position */}
      <div className="hidden lg:block">
        <FloatingActionButton actions={fabActions} position="bottom-right" color="primary" />
      </div>

      {/* Mobile-only Bottom FAB */}
      <div className="lg:hidden">
        <FloatingActionButton actions={fabActions} position="bottom-right" color="primary" />
      </div>

      {/* Scanner Modal */}
      <ScannerModal
        isOpen={showScannerModal}
        onClose={() => setShowScannerModal(false)}
        onScan={handleWipScan}
        title="WIP Precision Scan"
        autoCloseDelay={500}
      />

      {/* History Bottom Sheet */}
      <BottomSheet
        isOpen={showHistorySheet}
        onClose={() => setShowHistorySheet(false)}
        title="Full Operation History"
        height="half"
      >
        <div className="p-4">
          {scanHistory.length === 0 ? (
            <div className="text-center py-12 text-neutral-400">
              <Clock className="w-16 h-16 mx-auto mb-4 opacity-10" />
              <p>No recent activity found</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {scanHistory.map((item, idx) => (
                <div
                  key={idx}
                  className={cn(
                    'flex items-center justify-between p-4 rounded-2xl border transition-all',
                    'bg-neutral-50/50 border-neutral-100'
                  )}
                >
                  <div>
                    <p className="font-mono font-bold text-neutral-800">{item.wipId}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={cn(
                        'text-[10px] px-1.5 py-0.5 rounded font-bold uppercase',
                        item.action === 'start' ? 'bg-primary-100 text-primary-700' : 'bg-violet-100 text-violet-700'
                      )}>
                        {item.action === 'start' ? 'START' : 'FINISH'}
                      </span>
                      <span className="text-xs text-neutral-500">
                        {item.processNumber ? `Process ${item.processNumber}` : ''}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <StatusBadge
                      status={item.success ? 'completed' : 'fail'}
                    />
                    <p className="text-[10px] text-neutral-400 mt-1">
                      {new Date(item.timestamp).toLocaleString('en-US')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </BottomSheet>

      {/* Bottom Status Bar - Slim & Integrated */}
      <footer className="fixed bottom-0 left-0 right-0 h-10 bg-sub/80 backdrop-blur-xl border-t border-main flex items-center justify-between px-8 z-40">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2.5">
            <div className={cn(
              "w-2 h-2 rounded-full transition-all duration-500",
              networkStatus === 'online'
                ? "bg-success-500 shadow-[0_0_12px_rgba(16,185,129,0.5)]"
                : "bg-danger-500 shadow-[0_0_12px_rgba(239,68,68,0.5)]"
            )} />
            <span className="text-[10px] font-black text-dim uppercase tracking-[0.2em]">
              {networkStatus === 'online' ? 'System Online' : 'Offline Mode'}
            </span>
          </div>

          <div className="h-4 w-[1px] border-l border-main" />

          <div className="flex items-center gap-3">
            <div className="relative">
              <RefreshCw className={cn(
                "w-3.5 h-3.5 transition-colors",
                getSyncStatus() === 'syncing' ? "text-primary-400 animate-spin" : "text-dim"
              )} />
              {queueCount > 0 && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-warning-500 rounded-full animate-pulse" />
              )}
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] font-black text-muted uppercase tracking-widest leading-none">
                {getSyncStatus() === 'synced' ? 'Data Synced' : 'Syncing Data...'}
              </span>
              {syncProgress > 0 && syncProgress < 100 && (
                <div className="w-16 h-0.5 bg-main/20 rounded-full mt-1 overflow-hidden">
                  <div className="h-full bg-primary-500" style={{ width: `${syncProgress}%` }} />
                </div>
              )}
            </div>
          </div>

          {queueCount > 0 && (
            <span className="text-[9px] font-black text-warning-400 bg-warning-500/10 px-2 py-0.5 rounded border border-warning-500/20 uppercase tracking-tighter">
              {queueCount} Pending
            </span>
          )}
        </div>

        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-black text-dim uppercase tracking-widest">Active Operator</span>
            <div className="flex items-center gap-2 bg-primary-500/5 px-3 py-1 rounded-lg border border-primary-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
              <span className="text-[10px] font-black text-primary-400 uppercase tracking-widest">
                {settings.workerId || user?.username || 'Guest'}
              </span>
            </div>
          </div>

          {settings.equipmentId && (
            <div className="flex items-center gap-3">
              <span className="text-[10px] font-black text-dim uppercase tracking-widest">EQP</span>
              <span className="text-[10px] font-black text-muted uppercase tracking-widest bg-sub px-3 py-1 rounded-lg border border-main">
                {settings.equipmentId}
              </span>
            </div>
          )}

          <div className="h-4 w-[1px] border-l border-main" />

          <div className="flex items-center gap-2 text-dim">
            <span className="text-[9px] font-black uppercase tracking-[0.3em]">v1.0.4</span>
          </div>
        </div>
      </footer>
    </PageContainer >
  );
};
