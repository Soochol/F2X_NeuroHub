/**
 * Quick Work Modal Component
 *
 * 원스캔 퀵모드 - WIP 스캔 후 Flow 표시 + 착공/완공 통합 모달
 * 터치 최적화 UI
 */
import { useState, useEffect, useCallback } from 'react';
import {
  Play,
  CheckCircle,
  XCircle,
  Camera,
  Loader2,
  Package,
  Timer,
  ChevronRight,
  AlertCircle,
} from 'lucide-react';
import { Modal } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { MeasurementForm } from '@/components/MeasurementForm';
import { WipFlowTimeline } from './WipFlowTimeline';
import { cn } from '@/lib/cn';
import type { WIPTrace, Process, ProcessResult } from '@/types';

// 모달 단계
type ModalStep =
  | 'flow-view'      // Flow 확인 + 착공/완공 선택
  | 'measurement'    // 측정값 입력
  | 'complete';      // 완료 피드백

interface QuickWorkModalProps {
  isOpen: boolean;
  onClose: () => void;
  trace: WIPTrace | null;
  processes: Process[];
  isLoading?: boolean;
  // 액션 핸들러
  onStart: (processId: number) => Promise<boolean>;
  onComplete: (processId: number, result: ProcessResult, measurements: Record<string, unknown>) => Promise<boolean>;
  onScanNext: () => void;
}

export const QuickWorkModal: React.FC<QuickWorkModalProps> = ({
  isOpen,
  onClose,
  trace,
  processes,
  isLoading: _isLoading = false,
  onStart,
  onComplete,
  onScanNext,
}) => {
  // _isLoading은 외부 로딩 상태를 위해 예약됨 (현재 actionLoading 사용)
  // 상태
  const [step, setStep] = useState<ModalStep>('flow-view');
  const [selectedProcessNumber, setSelectedProcessNumber] = useState<number | null>(null);
  const [selectedProcessId, setSelectedProcessId] = useState<number | null>(null);
  const [pendingResult, setPendingResult] = useState<ProcessResult | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [lastResult, setLastResult] = useState<{
    success: boolean;
    action: 'start' | 'complete';
    result?: ProcessResult;
  } | null>(null);

  // 진행 중인 공정 찾기
  const inProgressProcess = trace?.process_history.find(
    (h) => h.start_time && !h.complete_time
  );

  // 다음 해야 할 공정 계산
  const getNextProcessNumber = useCallback((): number | null => {
    if (!trace) return 1;

    // 진행 중인 공정이 있으면 해당 공정
    if (inProgressProcess) {
      return inProgressProcess.process_number;
    }

    // 완료된 공정들 확인
    const completedNumbers = new Set(
      trace.process_history
        .filter((h) => h.complete_time && h.result === 'PASS')
        .map((h) => h.process_number)
    );

    // 첫 번째 미완료 공정 찾기
    for (let i = 1; i <= 8; i++) {
      if (!completedNumbers.has(i)) {
        return i;
      }
    }

    return null; // 모든 공정 완료
  }, [trace, inProgressProcess]);

  // 모달 열릴 때 초기화
  useEffect(() => {
    if (isOpen && trace) {
      setStep('flow-view');
      setLastResult(null);

      const nextNum = getNextProcessNumber();
      setSelectedProcessNumber(nextNum);

      if (nextNum) {
        const process = processes.find((p) => p.process_number === nextNum);
        setSelectedProcessId(process?.id || null);
      }
    }
  }, [isOpen, trace, processes, getNextProcessNumber]);

  // 공정 선택 핸들러
  const handleProcessSelect = (processNumber: number, processId: number) => {
    setSelectedProcessNumber(processNumber);
    setSelectedProcessId(processId);
  };

  // 착공 핸들러
  const handleStart = async () => {
    if (!selectedProcessId) return;

    setActionLoading(true);
    try {
      const success = await onStart(selectedProcessId);
      if (success) {
        setLastResult({ success: true, action: 'start' });
        // 착공 후 바로 완공 버튼 표시 (같은 화면에서)
      }
    } finally {
      setActionLoading(false);
    }
  };

  // 완공 버튼 클릭 (결과 선택)
  const handleCompleteClick = (result: ProcessResult) => {
    setPendingResult(result);
    setStep('measurement');
  };

  // 측정값 제출 핸들러
  const handleMeasurementSubmit = async (measurements: Record<string, unknown>) => {
    if (!selectedProcessId || !pendingResult) return;

    setActionLoading(true);
    try {
      const success = await onComplete(selectedProcessId, pendingResult, measurements);
      if (success) {
        setLastResult({ success: true, action: 'complete', result: pendingResult });
        setStep('complete');
      }
    } finally {
      setActionLoading(false);
      setPendingResult(null);
    }
  };

  // 측정값 취소
  const handleMeasurementCancel = () => {
    setPendingResult(null);
    setStep('flow-view');
  };

  // 다음 스캔
  const handleScanNext = () => {
    onClose();
    onScanNext();
  };

  // 선택된 Process 객체
  const selectedProcess = processes.find((p) => p.id === selectedProcessId) || null;

  // 착공 가능 여부 (진행 중인 공정이 없을 때)
  const canStart = !inProgressProcess && selectedProcessNumber !== null;

  // 완공 가능 여부 (진행 중인 공정이 현재 선택된 공정일 때)
  const canComplete = inProgressProcess?.process_number === selectedProcessNumber;

  // WIP 정보
  const wipInfo = trace
    ? {
      wipId: trace.wip_id,
      lotNumber: trace.lot_number,
      model: trace.lot_info?.product_model || '-',
      sequence: `#${trace.sequence_in_lot}`,
    }
    : null;

  // 모든 공정 완료 여부
  const allCompleted = trace?.process_history.filter(
    (h) => h.complete_time && h.result === 'PASS'
  ).length === 8;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      size="lg"
      variant="glass"
      showCloseButton={step !== 'complete'}
      closeOnBackdrop={!actionLoading}
    >
      {/* Flow View Step */}
      {step === 'flow-view' && (
        <div className="space-y-6">
          {/* WIP 정보 헤더 */}
          {wipInfo && (
            <div className="bg-sub rounded-3xl p-6 border border-main relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 blur-3xl rounded-full -mr-16 -mt-16 opacity-50" />
              <div className="flex items-start gap-5 relative text-dynamic">
                <div className="w-14 h-14 rounded-2xl bg-primary-500/10 flex items-center justify-center flex-shrink-0 border border-primary-500/20">
                  <Package className="w-7 h-7 text-primary-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-primary-400">Target WIP</span>
                    {allCompleted && (
                      <span className="bg-success-500/10 text-success-500 text-[10px] px-2 py-0.5 rounded font-black border border-success-500/20">FINISHED</span>
                    )}
                  </div>
                  <p className="text-2xl font-black text-dynamic font-mono truncate tracking-tight">
                    {wipInfo.wipId}
                  </p>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs font-bold text-muted">
                    <span className="bg-sub px-2 py-1 rounded-md border border-main">{wipInfo.lotNumber}</span>
                    <span className="text-dim">/</span>
                    <span className="bg-sub px-2 py-1 rounded-md border border-main">{wipInfo.model}</span>
                    <span className="text-dim">/</span>
                    <span className="text-primary-400">{wipInfo.sequence}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Flow Timeline */}
          <div className="py-2">
            <WipFlowTimeline
              trace={trace}
              processes={processes}
              selectedProcessNumber={selectedProcessNumber}
              onProcessSelect={handleProcessSelect}
              disabled={actionLoading}
            />
          </div>

          {/* 모든 공정 완료 시 */}
          {allCompleted && (
            <div className="bg-success-500/5 rounded-3xl p-6 border border-success-500/20 text-center animate-in zoom-in duration-500">
              <div className="w-16 h-16 bg-success-500/10 rounded-full flex items-center justify-center mx-auto mb-3 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                <CheckCircle className="w-10 h-10 text-success-500" />
              </div>
              <p className="text-xl font-black text-success-500 tracking-tight text-dynamic">All Processes Completed</p>
              <p className="text-sm text-muted mt-2 font-medium">
                All manufacturing processes for this WIP have been completed successfully.
              </p>
            </div>
          )}

          {/* 진행 중 공정 표시 */}
          {inProgressProcess && !allCompleted && (
            <div className="bg-primary-500/5 rounded-2xl p-4 border border-primary-500/10 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center animate-pulse">
                <Timer className="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p className="text-sm font-bold text-dynamic">
                  {inProgressProcess.process_number}. {inProgressProcess.process_name} In Progress
                </p>
                <p className="text-[10px] text-muted uppercase tracking-wider font-bold">Completion Required</p>
              </div>
            </div>
          )}

          {/* 액션 버튼들 */}
          {!allCompleted && (
            <div className="space-y-4 pt-2">
              {/* 착공 버튼 */}
              <button
                type="button"
                onClick={handleStart}
                disabled={!canStart || actionLoading}
                className={cn(
                  'w-full flex items-center justify-center gap-4',
                  'py-6 px-8 rounded-[2rem]',
                  'font-black text-2xl tracking-tight transition-all duration-300',
                  !canStart || actionLoading
                    ? 'bg-sub text-dim border border-main cursor-not-allowed'
                    : [
                      'bg-gradient-to-r from-primary-600 to-primary-400',
                      'text-white shadow-[0_10px_30px_rgba(30,58,95,0.4)]',
                      'hover:from-primary-500 hover:to-primary-300',
                      'active:scale-95 active:shadow-inner',
                    ]
                )}
              >
                {actionLoading ? (
                  <Loader2 className="w-8 h-8 animate-spin" />
                ) : (
                  <Play className="w-8 h-8" fill="currentColor" />
                )}
                <span>START OPERATION</span>
                {selectedProcess && (
                  <ChevronRight className="w-6 h-6 opacity-30 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                )}
              </button>

              {/* 완공 버튼들 */}
              <div className="grid grid-cols-2 gap-4">
                {/* 합격 */}
                <button
                  type="button"
                  onClick={() => handleCompleteClick('PASS')}
                  disabled={!canComplete || actionLoading}
                  className={cn(
                    'flex items-center justify-center gap-3',
                    'py-6 px-4 rounded-3xl',
                    'font-black text-xl transition-all duration-300',
                    !canComplete || actionLoading
                      ? 'bg-sub text-dim border border-main cursor-not-allowed'
                      : [
                        'bg-gradient-to-br from-success-600 to-success-400',
                        'text-white shadow-[0_8px_25px_rgba(16,185,129,0.3)]',
                        'hover:scale-[1.03] active:scale-95',
                      ]
                  )}
                >
                  <CheckCircle className="w-7 h-7" />
                  <div className="text-left">
                    <div className="leading-tight">COMPLETE</div>
                    <div className="text-xs font-black opacity-60 uppercase tracking-widest">Pass</div>
                  </div>
                </button>

                {/* 불량 */}
                <button
                  type="button"
                  onClick={() => handleCompleteClick('FAIL')}
                  disabled={!canComplete || actionLoading}
                  className={cn(
                    'flex items-center justify-center gap-3',
                    'py-6 px-4 rounded-3xl',
                    'font-black text-xl transition-all duration-300',
                    !canComplete || actionLoading
                      ? 'bg-sub text-dim border border-main cursor-not-allowed'
                      : [
                        'bg-gradient-to-br from-danger-600 to-danger-400',
                        'text-white shadow-[0_8px_25px_rgba(239,68,68,0.3)]',
                        'hover:scale-[1.03] active:scale-95',
                      ]
                  )}
                >
                  <XCircle className="w-7 h-7" />
                  <div className="text-left">
                    <div className="leading-tight">COMPLETE</div>
                    <div className="text-xs font-black opacity-60 uppercase tracking-widest">Fail</div>
                  </div>
                </button>
              </div>

              {/* 안내 메시지 */}
              {!canStart && !canComplete && !allCompleted && (
                <div className="flex items-center justify-center gap-2 text-xs font-bold text-muted uppercase tracking-widest py-2 bg-sub rounded-full border border-dashed border-main animate-pulse">
                  <AlertCircle className="w-4 h-4" />
                  <span>Select a process to proceed</span>
                </div>
              )}
            </div>
          )}

          {/* 모든 공정 완료 시 닫기 버튼 */}
          {allCompleted && (
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handleScanNext}
              className="mt-6 py-6 rounded-3xl font-black text-xl"
            >
              <Camera className="w-6 h-6 mr-3" />
              SCAN NEXT WIP
            </Button>
          )}
        </div>
      )}

      {/* Measurement Step */}
      {step === 'measurement' && (
        <div>
          {/* 헤더 */}
          <div
            className={cn(
              'mb-4 py-3 px-4 rounded-xl',
              pendingResult === 'PASS'
                ? 'bg-success-50 border border-success-200'
                : 'bg-danger-50 border border-danger-200'
            )}
          >
            <div className="flex items-center gap-2">
              {pendingResult === 'PASS' ? (
                <CheckCircle className="w-5 h-5 text-success-600" />
              ) : (
                <XCircle className="w-5 h-5 text-danger-600" />
              )}
              <span
                className={cn(
                  'font-semibold',
                  pendingResult === 'PASS' ? 'text-success-700' : 'text-danger-700'
                )}
              >
                Completion ({pendingResult === 'PASS' ? 'Pass' : 'Fail'})
              </span>
            </div>
            <p className="text-sm text-neutral-600 mt-1 font-mono">
              {wipInfo?.wipId}
            </p>
          </div>

          {/* 측정값 폼 */}
          <MeasurementForm
            process={selectedProcess}
            result={pendingResult!}
            onSubmit={handleMeasurementSubmit}
            onCancel={handleMeasurementCancel}
            isLoading={actionLoading}
          />
        </div>
      )}

      {/* Complete Step */}
      {step === 'complete' && lastResult && (
        <div className="text-center py-6">
          {/* 성공 아이콘 */}
          <div
            className={cn(
              'w-20 h-20 rounded-full mx-auto mb-4',
              'flex items-center justify-center',
              lastResult.result === 'PASS'
                ? 'bg-success-100'
                : lastResult.result === 'FAIL'
                  ? 'bg-danger-100'
                  : 'bg-primary-100'
            )}
          >
            {lastResult.action === 'complete' && lastResult.result === 'PASS' && (
              <CheckCircle className="w-10 h-10 text-success-600" />
            )}
            {lastResult.action === 'complete' && lastResult.result === 'FAIL' && (
              <XCircle className="w-10 h-10 text-danger-600" />
            )}
            {lastResult.action === 'start' && (
              <Play className="w-10 h-10 text-primary-600" fill="currentColor" />
            )}
          </div>

          {/* 메시지 */}
          <h3 className="text-2xl font-bold text-dynamic mb-2">
            {lastResult.action === 'complete' ? 'Operation Finished!' : 'Operation Started!'}
          </h3>
          <p className="text-neutral-600 mb-2 font-mono">{wipInfo?.wipId}</p>
          {selectedProcess && (
            <p className="text-neutral-500">
              {selectedProcess.process_number}. {selectedProcess.process_name_en}
              {lastResult.result && (
                <span
                  className={cn(
                    'ml-2 font-semibold',
                    lastResult.result === 'PASS' ? 'text-success-600' : 'text-danger-600'
                  )}
                >
                  {lastResult.result === 'PASS' ? 'Pass' : 'Fail'}
                </span>
              )}
            </p>
          )}

          {/* Flow Timeline 미리보기 */}
          <div className="my-6 opacity-60">
            <WipFlowTimeline
              trace={trace}
              processes={processes}
              disabled
            />
          </div>

          {/* 버튼들 */}
          <div className="space-y-3">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handleScanNext}
              leftIcon={<Camera className="w-5 h-5" />}
            >
              SCAN NEXT WIP
            </Button>
            <Button variant="ghost" size="lg" fullWidth onClick={onClose}>
              CLOSE
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
