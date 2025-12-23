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
} from 'lucide-react';
import { ScannerModal } from '@/components/scanner';
import { PageContainer, Header, BottomSheet } from '@/components/layout';
import { Card, FloatingActionButton } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { SyncStatusBar } from '@/components/sync';
import { FadeIn, SlideUp } from '@/components/animations';
import { useToast } from '@/components/feedback';
import { useFeedback } from '@/hooks';
import { useAppStore } from '@/store/appStore';
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
import { QuickWorkModal } from '@/components/work';

export const WorkPage: React.FC = () => {
  const {
    user,
    settings,
    processes,
    setProcesses,
    addScanResult,
    scanHistory,
  } = useAppStore();

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
  const [showQuickModal, setShowQuickModal] = useState(false);
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
        toast.error('공정 로드 실패', getErrorMessage(err), 4000);
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
        toast.warning('동기화 완료', `${result.success}건 성공, ${result.failed}건 실패`, 4000);
      } else {
        toast.success('동기화 완료', `${result.success}건 처리됨`, 4000);
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
        toast.error('잘못된 형식', 'WIP ID 형식이 올바르지 않습니다', 3000);
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
        setShowQuickModal(true);
        toast.success('WIP 로드 완료', wipId, 2000);
      } catch (err) {
        const errorMsg = getErrorMessage(err);
        toast.error('WIP 조회 실패', errorMsg, 4000);
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
  const handleStart = async (processId: number): Promise<boolean> => {
    if (!currentTrace || !user) return false;

    const startData: ProcessStartRequest = {
      wip_id: currentTrace.wip_id,
      process_id: String(processId),
      worker_id: settings.workerId || user.username,
      equipment_id: settings.equipmentId || undefined,
      line_id: settings.lineId || undefined,
    };

    try {
      if (!isOnline()) {
        await addToQueue('start', startData);
        const count = await getQueueCount();
        setQueueCount(count);
        toast.warning('오프라인 저장', `대기 중: ${count}건`, 3000);
        await feedbackWarning();
      } else {
        await processOperationsApi.start(startData);
        toast.success('착공 완료', currentTrace.wip_id, 2000);
        await feedbackSuccess();
      }

      // Trace 새로고침
      const updatedTrace = await wipApi.getTrace(currentTrace.wip_id);
      setCurrentTrace(updatedTrace);

      const process = processes.find((p) => p.id === processId);
      addScanResult({
        wipId: currentTrace.wip_id,
        timestamp: new Date(),
        action: 'start',
        success: true,
        message: '착공 완료',
        processNumber: process?.process_number,
      });

      return true;
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      toast.error('착공 실패', errorMsg, 4000);
      await feedbackError();
      return false;
    }
  };

  const handleComplete = async (
    processId: number,
    result: ProcessResult,
    measurements: Record<string, unknown>
  ): Promise<boolean> => {
    if (!currentTrace || !user) return false;

    const completeData: ProcessCompleteRequest = {
      wip_id: currentTrace.wip_id,
      process_id: String(processId),
      worker_id: settings.workerId || user.username,
      result,
      measurements: Object.keys(measurements).length > 0 ? measurements : undefined,
    };

    try {
      if (!isOnline()) {
        await addToQueue('complete', completeData);
        const count = await getQueueCount();
        setQueueCount(count);
        const resultText = result === 'PASS' ? '합격' : '불량';
        toast.warning(`완공(${resultText}) 저장됨`, `대기 중: ${count}건`, 3000);
        await feedbackWarning();
      } else {
        await processOperationsApi.complete(completeData);
        const resultText = result === 'PASS' ? '합격' : '불량';
        if (result === 'PASS') {
          toast.success(`완공 (${resultText})`, currentTrace.wip_id, 2000);
          await feedbackSuccess();
        } else {
          toast.error(`완공 (${resultText})`, currentTrace.wip_id, 2000);
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
        message: `완공 (${result})`,
        processNumber: process?.process_number,
      });

      return true;
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      toast.error('완공 실패', errorMsg, 4000);
      await feedbackError();
      return false;
    }
  };

  const handleScanNext = () => {
    setCurrentTrace(null);
    setShowQuickModal(false);
    // 바로 스캔 모달 열기
    setTimeout(() => setShowScannerModal(true), 300);
  };

  const handleQuickModalClose = () => {
    setShowQuickModal(false);
    setCurrentTrace(null);
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
    <PageContainer>
      {/* Header */}
      <Header
        title="착공 / 완공"
        subtitle={user?.full_name || user?.username}
        isOnline={networkStatus === 'online'}
        soundEnabled={soundEnabled}
        onToggleSound={toggleSound}
        queueCount={queueCount}
      />

      {/* Sync Status Bar */}
      <SyncStatusBar
        isOnline={networkStatus === 'online'}
        syncStatus={getSyncStatus()}
        pendingCount={queueCount}
        progress={syncProgress}
        className="mb-6"
      />

      {/* Main Scan Area */}
      <FadeIn>
        <Card className="mb-6">
          <div className="text-center py-6">
            {/* Icon */}
            <div className="w-20 h-20 rounded-3xl bg-primary-100 mx-auto mb-4 flex items-center justify-center">
              <QrCode className="w-10 h-10 text-primary-600" />
            </div>

            {/* Title */}
            <h2 className="text-xl font-bold text-neutral-800 mb-2">
              WIP 바코드 스캔
            </h2>
            <p className="text-neutral-500 mb-6">
              작업할 WIP의 바코드를 스캔하세요
            </p>

            {/* Camera Scan Button */}
            <button
              type="button"
              onClick={() => setShowScannerModal(true)}
              disabled={isLoadingWip}
              className={cn(
                'w-full flex items-center justify-center gap-3',
                'py-5 px-6 rounded-2xl',
                'font-bold text-xl',
                'transition-all duration-200',
                'shadow-lg',
                isLoadingWip
                  ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
                  : [
                      'bg-gradient-to-r from-primary-500 to-primary-600',
                      'text-white',
                      'hover:from-primary-600 hover:to-primary-700',
                      'active:scale-[0.98] active:shadow-md',
                    ]
              )}
            >
              {isLoadingWip ? (
                <Loader2 className="w-7 h-7 animate-spin" />
              ) : (
                <Camera className="w-7 h-7" />
              )}
              <span>카메라로 스캔</span>
            </button>

            {/* Divider */}
            <div className="relative my-5">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-neutral-200" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-4 bg-white text-sm text-neutral-400">또는</span>
              </div>
            </div>

            {/* Manual Input */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 justify-center text-sm text-neutral-500">
                <Keyboard className="w-4 h-4" />
                <span>직접 입력</span>
              </div>
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  type="text"
                  value={wipInput}
                  onChange={(e) => setWipInput(e.target.value.toUpperCase())}
                  onKeyDown={handleInputKeyDown}
                  placeholder="WIP-XXXXXXXX-XXX"
                  className="flex-1 font-mono text-center text-lg"
                  disabled={isLoadingWip}
                />
                <Button
                  variant="primary"
                  onClick={handleManualSubmit}
                  disabled={!wipInput.trim() || isLoadingWip}
                  isLoading={isLoadingWip}
                  className="px-6"
                >
                  확인
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </FadeIn>

      {/* Recent Scans Preview */}
      {scanHistory.length > 0 && (
        <SlideUp delay={100}>
          <Card className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-neutral-700 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                최근 작업
              </h3>
              <button
                type="button"
                onClick={() => setShowHistorySheet(true)}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                전체보기
              </button>
            </div>
            <div className="space-y-2">
              {scanHistory.slice(0, 3).map((item, idx) => (
                <div
                  key={idx}
                  className={cn(
                    'flex items-center justify-between py-2 px-3 rounded-lg',
                    item.success ? 'bg-success-50' : 'bg-danger-50'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        'w-2 h-2 rounded-full',
                        item.success ? 'bg-success-500' : 'bg-danger-500'
                      )}
                    />
                    <span className="font-mono text-sm text-neutral-700">{item.wipId}</span>
                  </div>
                  <span className="text-xs text-neutral-500">
                    {item.action === 'start' ? '착공' : '완공'}
                    {item.processNumber && ` (${item.processNumber})`}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </SlideUp>
      )}

      {/* Instructions */}
      <FadeIn delay={200}>
        <Card className="bg-neutral-50 border-neutral-200">
          <h3 className="font-semibold text-neutral-700 mb-3">사용 방법</h3>
          <ol className="space-y-2 text-sm text-neutral-600">
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                1
              </span>
              <span>WIP 바코드를 스캔하세요</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                2
              </span>
              <span>공정 현황을 확인하고 작업할 공정을 선택하세요</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
                3
              </span>
              <span>착공 또는 완공 버튼을 눌러 작업을 처리하세요</span>
            </li>
          </ol>
        </Card>
      </FadeIn>

      {/* Scanner Modal */}
      <ScannerModal
        isOpen={showScannerModal}
        onClose={() => setShowScannerModal(false)}
        onScan={handleWipScan}
        title="WIP 스캔"
        autoCloseDelay={500}
      />

      {/* Quick Work Modal */}
      <QuickWorkModal
        isOpen={showQuickModal}
        onClose={handleQuickModalClose}
        trace={currentTrace}
        processes={processes}
        isLoading={isLoadingWip}
        onStart={handleStart}
        onComplete={handleComplete}
        onScanNext={handleScanNext}
      />

      {/* History Bottom Sheet */}
      <BottomSheet
        isOpen={showHistorySheet}
        onClose={() => setShowHistorySheet(false)}
        title="최근 작업"
        height="half"
      >
        {scanHistory.length === 0 ? (
          <div className="text-center py-8 text-neutral-400">
            <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>최근 작업 기록이 없습니다</p>
          </div>
        ) : (
          <div className="space-y-2">
            {scanHistory.map((item, idx) => (
              <div
                key={idx}
                className={cn(
                  'flex items-center justify-between py-3 px-4 rounded-xl',
                  item.success ? 'bg-success-50' : 'bg-danger-50'
                )}
              >
                <div>
                  <p className="font-mono font-medium text-neutral-800">{item.wipId}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">
                    {item.action === 'start' ? '착공' : '완공'}
                    {item.processNumber && ` - 공정 ${item.processNumber}`}
                  </p>
                </div>
                <div className="text-right">
                  <span
                    className={cn(
                      'text-xs font-medium px-2 py-1 rounded-full',
                      item.success
                        ? 'bg-success-100 text-success-700'
                        : 'bg-danger-100 text-danger-700'
                    )}
                  >
                    {item.success ? '성공' : '실패'}
                  </span>
                  <p className="text-xs text-neutral-400 mt-1">
                    {new Date(item.timestamp).toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </BottomSheet>

      {/* Floating Action Button */}
      <FloatingActionButton actions={fabActions} position="bottom-right" color="primary" />
    </PageContainer>
  );
};
