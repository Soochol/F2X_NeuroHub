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
      showCloseButton={step !== 'complete'}
      closeOnBackdrop={!actionLoading}
    >
      {/* Flow View Step */}
      {step === 'flow-view' && (
        <div className="space-y-5">
          {/* WIP 정보 헤더 */}
          {wipInfo && (
            <div className="bg-neutral-50 rounded-2xl p-4 border border-neutral-200">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Package className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-lg font-bold text-neutral-800 font-mono truncate">
                    {wipInfo.wipId}
                  </p>
                  <div className="flex items-center gap-2 mt-1 text-sm text-neutral-500">
                    <span>{wipInfo.lotNumber}</span>
                    <span className="text-neutral-300">|</span>
                    <span>{wipInfo.model}</span>
                    <span className="text-neutral-300">|</span>
                    <span className="font-medium text-primary-600">{wipInfo.sequence}</span>
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
            <div className="bg-success-50 rounded-2xl p-4 border border-success-200 text-center">
              <CheckCircle className="w-12 h-12 text-success-500 mx-auto mb-2" />
              <p className="text-lg font-bold text-success-700">모든 공정 완료!</p>
              <p className="text-sm text-success-600 mt-1">
                이 WIP의 모든 공정이 완료되었습니다.
              </p>
            </div>
          )}

          {/* 진행 중 공정 표시 */}
          {inProgressProcess && (
            <div className="bg-primary-50 rounded-2xl p-4 border border-primary-200">
              <div className="flex items-center gap-2 mb-2">
                <Timer className="w-5 h-5 text-primary-600" />
                <span className="font-semibold text-primary-700">진행 중인 작업</span>
              </div>
              <p className="text-neutral-700">
                <span className="font-bold">{inProgressProcess.process_number}. {inProgressProcess.process_name}</span>
                {' '}공정이 착공되어 있습니다.
              </p>
              <p className="text-sm text-neutral-500 mt-1">
                완공 버튼을 눌러 작업을 완료하세요.
              </p>
            </div>
          )}

          {/* 액션 버튼들 */}
          {!allCompleted && (
            <div className="space-y-3 pt-2">
              {/* 착공 버튼 */}
              <button
                type="button"
                onClick={handleStart}
                disabled={!canStart || actionLoading}
                className={cn(
                  'w-full flex items-center justify-center gap-3',
                  'py-5 px-6 rounded-2xl',
                  'font-bold text-xl',
                  'transition-all duration-200',
                  'shadow-lg',
                  !canStart || actionLoading
                    ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
                    : [
                        'bg-gradient-to-r from-primary-500 to-primary-600',
                        'text-white',
                        'hover:from-primary-600 hover:to-primary-700',
                        'active:scale-[0.98] active:shadow-md',
                      ]
                )}
              >
                {actionLoading ? (
                  <Loader2 className="w-7 h-7 animate-spin" />
                ) : (
                  <Play className="w-7 h-7" fill="currentColor" />
                )}
                <span>착공</span>
                {selectedProcess && (
                  <ChevronRight className="w-5 h-5 opacity-70" />
                )}
              </button>

              {/* 완공 버튼들 */}
              <div className="grid grid-cols-2 gap-3">
                {/* 합격 */}
                <button
                  type="button"
                  onClick={() => handleCompleteClick('PASS')}
                  disabled={!canComplete || actionLoading}
                  className={cn(
                    'flex items-center justify-center gap-2',
                    'py-5 px-4 rounded-2xl',
                    'font-bold text-lg',
                    'transition-all duration-200',
                    'shadow-lg',
                    !canComplete || actionLoading
                      ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
                      : [
                          'bg-gradient-to-r from-success-500 to-success-600',
                          'text-white',
                          'hover:from-success-600 hover:to-success-700',
                          'active:scale-[0.98] active:shadow-md',
                        ]
                  )}
                >
                  <CheckCircle className="w-6 h-6" />
                  <div className="text-left">
                    <div>완공</div>
                    <div className="text-sm font-normal opacity-80">합격</div>
                  </div>
                </button>

                {/* 불량 */}
                <button
                  type="button"
                  onClick={() => handleCompleteClick('FAIL')}
                  disabled={!canComplete || actionLoading}
                  className={cn(
                    'flex items-center justify-center gap-2',
                    'py-5 px-4 rounded-2xl',
                    'font-bold text-lg',
                    'transition-all duration-200',
                    'shadow-lg',
                    !canComplete || actionLoading
                      ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
                      : [
                          'bg-gradient-to-r from-danger-500 to-danger-600',
                          'text-white',
                          'hover:from-danger-600 hover:to-danger-700',
                          'active:scale-[0.98] active:shadow-md',
                        ]
                  )}
                >
                  <XCircle className="w-6 h-6" />
                  <div className="text-left">
                    <div>완공</div>
                    <div className="text-sm font-normal opacity-80">불량</div>
                  </div>
                </button>
              </div>

              {/* 안내 메시지 */}
              {!canStart && !canComplete && !allCompleted && (
                <div className="flex items-center justify-center gap-2 text-sm text-neutral-500 py-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>공정을 선택하세요</span>
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
              className="mt-4"
            >
              <Camera className="w-5 h-5" />
              다음 WIP 스캔
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
                완공 ({pendingResult === 'PASS' ? '합격' : '불량'})
              </span>
            </div>
            <p className="text-sm text-neutral-600 mt-1 font-mono">
              {wipInfo?.wipId}
            </p>
          </div>

          {/* 측정값 폼 */}
          <MeasurementForm
            process={selectedProcess}
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
          <h3 className="text-2xl font-bold text-neutral-800 mb-2">
            {lastResult.action === 'complete' ? '완공 완료!' : '착공 완료!'}
          </h3>
          <p className="text-neutral-600 mb-2 font-mono">{wipInfo?.wipId}</p>
          {selectedProcess && (
            <p className="text-neutral-500">
              {selectedProcess.process_number}. {selectedProcess.process_name_ko}
              {lastResult.result && (
                <span
                  className={cn(
                    'ml-2 font-semibold',
                    lastResult.result === 'PASS' ? 'text-success-600' : 'text-danger-600'
                  )}
                >
                  {lastResult.result === 'PASS' ? '합격' : '불량'}
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
              다음 WIP 스캔
            </Button>
            <Button variant="ghost" size="lg" fullWidth onClick={onClose}>
              닫기
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
