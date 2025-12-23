/**
 * Quick Work Panel Component
 * 
 * 원스캔 퀵모드 - WIP 스캔 후 Flow 표시 + 착공/완공 통합 패널 (인라인 전개용)
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
    ArrowLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { MeasurementForm } from '@/components/MeasurementForm';
import { WipFlowTimeline } from './WipFlowTimeline';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/cn';
import type { WIPTrace, Process, ProcessResult } from '@/types';

interface QuickWorkPanelProps {
    trace: WIPTrace | null;
    processes: Process[];
    isLoading?: boolean;
    onStart: (processId: number) => Promise<boolean>;
    onComplete: (processId: number, result: ProcessResult, measurements: Record<string, unknown>, defectData?: { defect_codes: string[], notes?: string }) => Promise<boolean>;
    onScanNext: () => void;
    onCancel: () => void;
}

type PanelStep = 'flow-view' | 'measurement' | 'complete';

export const QuickWorkPanel: React.FC<QuickWorkPanelProps> = ({
    trace,
    processes,
    onStart,
    onComplete,
    onScanNext,
    onCancel,
}) => {
    const [step, setStep] = useState<PanelStep>('flow-view');
    const [selectedProcessNumber, setSelectedProcessNumber] = useState<number | null>(null);
    const [selectedProcessId, setSelectedProcessId] = useState<number | null>(null);
    const [pendingResult, setPendingResult] = useState<ProcessResult | null>(null);
    const [actionLoading, setActionLoading] = useState(false);

    const inProgressProcess = trace?.process_history.find(
        (h) => h.start_time && !h.complete_time
    );

    const getNextProcessNumber = useCallback((): number | null => {
        if (!trace) return 1;
        if (inProgressProcess) return inProgressProcess.process_number;
        const completedNumbers = new Set(
            trace.process_history
                .filter((h) => h.complete_time && h.result === 'PASS')
                .map((h) => h.process_number)
        );
        for (let i = 1; i <= 8; i++) {
            if (!completedNumbers.has(i)) return i;
        }
        return null;
    }, [trace, inProgressProcess]);

    // 효과적으로 다음 공정 번호를 계산하고 ID를 동기화
    useEffect(() => {
        if (trace && processes.length > 0) {
            const nextNum = getNextProcessNumber();
            if (nextNum !== null) {
                // 현재 진행중인 공정이 있거나, 다음 공정을 자동으로 선택해야 할 때
                setSelectedProcessNumber(nextNum);
                const process = processes.find((p) => p.process_number === nextNum);
                if (process) {
                    setSelectedProcessId(process.id);
                }
            }
        }
    }, [trace, processes, getNextProcessNumber]);

    // 선택된 번호가 바뀔 때 ID 자동 동기화
    useEffect(() => {
        if (selectedProcessNumber !== null && processes.length > 0) {
            const process = processes.find((p) => p.process_number === selectedProcessNumber);
            if (process) {
                setSelectedProcessId(process.id);
            }
        }
    }, [selectedProcessNumber, processes]);

    const handleProcessSelect = (processNumber: number, processId: number) => {
        setSelectedProcessNumber(processNumber);
        setSelectedProcessId(processId);
    };

    const handleStart = async () => {
        // ID가 아직 매핑되지 않았으면 번호로 다시 찾기 시도
        let finalId = selectedProcessId;
        if (!finalId && selectedProcessNumber !== null) {
            const process = processes.find(p => p.process_number === selectedProcessNumber);
            finalId = process?.id || null;
        }

        if (!finalId) {
            console.error('No process ID found for start');
            return;
        }

        setActionLoading(true);
        try {
            const success = await onStart(finalId);
            if (success) {
                // 성공 시 부모가 주는 trace 업데이트를 대기하거나, 
                // 필요하다면 여기서 추가 상태 변화를 줄 수 있음
            }
        } finally {
            setActionLoading(false);
        }
    };

    const handleCompleteClick = (result: ProcessResult) => {
        setPendingResult(result);
        setStep('measurement');
    };

    const handleMeasurementSubmit = async (data: { measurements: Record<string, unknown>, defects?: string[], notes?: string }) => {
        if (!selectedProcessId || !pendingResult) return;
        setActionLoading(true);
        try {
            const defectData = data.defects || data.notes
                ? { defect_codes: data.defects || [], notes: data.notes }
                : undefined;

            const success = await onComplete(selectedProcessId, pendingResult, data.measurements, defectData);
            if (success) {
                setStep('complete');
            }
        } finally {
            setActionLoading(false);
        }
    };

    const { isAuthenticated, settings } = useAppStore();
    const isAuthorized = isAuthenticated || !!settings.workerId;

    const selectedProcess = processes.find((p) => p.id === selectedProcessId) || null;

    // 현재 선택된 공정의 결과 확인
    const selectedHistory = trace?.process_history.find(h => h.process_number === selectedProcessNumber);

    // 착공 가능 여부: 
    // 1. 진행 중인 공정이 없을 때
    // 2. 공정이 선택되었을 때
    // 3. 현재 공정이 아직 PASS가 아닐 때 (FAIL인 경우는 다시 착공 가능하도록 유도)
    // 4. 유저가 인증되어 있거나 Worker ID가 설정되어 있을 때
    const canStart = isAuthorized &&
        !inProgressProcess &&
        selectedProcessNumber !== null &&
        processes.length > 0 &&
        selectedHistory?.result !== 'PASS';

    // 완공 가능 여부: 진행 중인 공정이 현재 선택된 공정일 때
    const canComplete = isAuthorized &&
        inProgressProcess?.process_number === selectedProcessNumber &&
        processes.length > 0;

    const wipInfo = trace ? {
        wipId: trace.wip_id,
        lotNumber: trace.lot_number,
        model: trace.lot_info?.product_model || '-',
        sequence: `#${trace.sequence_in_lot}`,
    } : null;

    const allCompleted = trace?.process_history.filter(
        (h) => h.complete_time && h.result === 'PASS'
    ).length === 8;

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header with Back Button */}
            <div className="flex items-center justify-between">
                <button
                    onClick={onCancel}
                    className="flex items-center gap-2 text-neutral-500 hover:text-dynamic transition-colors group"
                >
                    <div className="p-2 rounded-xl bg-sub border border-main group-hover:border-primary-500/50">
                        <ArrowLeft className="w-5 h-5 text-main" />
                    </div>
                    <span className="font-bold text-sm uppercase tracking-widest text-muted group-hover:text-main">Back to Scan</span>
                </button>

                {wipInfo && (
                    <div className="text-right">
                        <p className="text-[10px] font-black text-primary-400 uppercase tracking-[0.2em]">Active Session</p>
                        <p className="text-sm font-mono font-bold text-dynamic opacity-80">{wipInfo.wipId}</p>
                    </div>
                )}
            </div>

            {step === 'flow-view' && (
                <div className="space-y-8 w-full">
                    {/* WIP Info & Action Buttons Integrated */}
                    <div className="space-y-6">
                        {wipInfo && (
                            <div className="glass-card p-8 lg:p-12 relative overflow-hidden group border-dynamic shadow-2xl">
                                {/* Decorative Glow */}
                                <div className="absolute top-0 right-0 w-96 h-96 bg-primary-500/10 blur-[120px] rounded-full -mr-48 -mt-48 opacity-50" />

                                <div className="relative flex flex-col gap-10">
                                    {/* Top: WIP ID & Overall Status */}
                                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 w-full border-b border-dynamic pb-8">
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20">
                                                    <Package className="w-5 h-5 text-primary-400" />
                                                </div>
                                                <span className="text-xs font-black uppercase tracking-[0.4em] text-primary-400">Target Cargo</span>
                                            </div>
                                            <h2 className="text-4xl lg:text-6xl font-black text-dynamic font-mono tracking-tighter break-all">
                                                {wipInfo.wipId}
                                            </h2>
                                        </div>

                                        {/* Status Badge */}
                                        <div className="shrink-0">
                                            {allCompleted ? (
                                                <div className="bg-success-500/10 text-success-500 px-6 py-3 rounded-2xl font-black border border-success-500/20 animate-pulse flex items-center gap-3">
                                                    <CheckCircle className="w-5 h-5" />
                                                    <span className="text-sm tracking-widest font-black uppercase">Operation Finished</span>
                                                </div>
                                            ) : (
                                                <div className="bg-primary-500/10 text-primary-400 px-6 py-3 rounded-2xl font-black border border-primary-500/20 flex items-center gap-3">
                                                    <div className="w-2 h-2 rounded-full bg-primary-400 animate-ping" />
                                                    <span className="text-sm tracking-widest font-black uppercase">Live Session</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Middle: Details Grid */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        <div className="bg-primary-500/5 p-5 rounded-3xl border border-dynamic group-hover:border-primary-500/20 transition-colors">
                                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] mb-2">Lot Number</p>
                                            <p className="text-xl font-mono font-bold text-dynamic">{wipInfo.lotNumber}</p>
                                        </div>
                                        <div className="bg-primary-500/5 p-5 rounded-3xl border border-dynamic group-hover:border-primary-500/20 transition-colors">
                                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] mb-2">Product Model</p>
                                            <p className="text-xl font-mono font-bold text-dynamic">{wipInfo.model}</p>
                                        </div>
                                        <div className="bg-primary-500/5 p-5 rounded-3xl border border-dynamic group-hover:border-primary-500/20 transition-colors">
                                            <p className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em] mb-2">Batch Seq</p>
                                            <p className="text-xl font-mono font-bold text-primary-400">{wipInfo.sequence}</p>
                                        </div>
                                    </div>

                                    {/* Bottom: Active Operation Banner (if in progress) */}
                                    {inProgressProcess && (
                                        <div className="bg-primary-500/15 border border-primary-500/30 p-8 rounded-[2rem] flex items-center justify-between gap-6 animate-in slide-in-from-top-4 duration-700">
                                            <div className="flex items-center gap-6">
                                                <div className="w-16 h-16 rounded-2xl bg-primary-500/30 flex items-center justify-center animate-pulse shadow-inner">
                                                    <Timer className="w-8 h-8 text-primary-400" />
                                                </div>
                                                <div>
                                                    <p className="text-[11px] font-black text-primary-400 uppercase tracking-[0.3em] mb-1">Active Site Operation</p>
                                                    <h3 className="text-3xl font-black text-dynamic tracking-tight">
                                                        <span className="opacity-50 mr-3">{inProgressProcess.process_number}</span>
                                                        {inProgressProcess.process_name}
                                                    </h3>
                                                </div>
                                            </div>
                                            <div className="hidden lg:flex items-center gap-2 px-4 py-2 bg-primary-500/20 rounded-xl border border-primary-400/20">
                                                <span className="text-[10px] font-black text-primary-400 uppercase tracking-widest">In Progress</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Integrated Action Area */}
                        <div className="space-y-6">
                            {allCompleted ? (
                                <div className="glass-card p-12 border-success-500/20 text-center animate-in zoom-in duration-700">
                                    <div className="w-24 h-24 bg-success-500/20 rounded-full flex items-center justify-center mx-auto mb-8 shadow-[0_0_50px_rgba(16,185,129,0.4)]">
                                        <CheckCircle className="w-14 h-14 text-success-400" />
                                    </div>
                                    <h3 className="text-3xl font-black text-dynamic tracking-tight">All Manufacturing Processes Completed</h3>
                                    <p className="text-neutral-400 mt-4 text-lg">
                                        Quality calibration and production processes for this WIP have been fully finalized.
                                    </p>
                                    <Button variant="primary" size="lg" onClick={onScanNext} className="mt-12 py-8 px-12 rounded-[3rem] font-black text-2xl w-full h-auto">
                                        <Camera className="w-8 h-8 mr-4" />
                                        NEXT SCAN
                                    </Button>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <button
                                        onClick={handleStart}
                                        disabled={!canStart || actionLoading}
                                        className={cn(
                                            'relative flex items-center justify-between px-10 py-12 rounded-[3.5rem] transition-all duration-500 overflow-hidden group',
                                            'font-black text-4xl tracking-tighter shadow-2xl h-full',
                                            !canStart || actionLoading
                                                ? 'btn-action-disabled'
                                                : 'btn-action-primary hover:scale-[1.02] active:scale-95 shadow-primary-500/20'
                                        )}
                                    >
                                        <div className="flex items-center gap-6 relative z-10">
                                            {actionLoading ? <Loader2 className="w-12 h-12 animate-spin text-white/50" /> : <Play className="w-12 h-12 fill-white animate-pulse" />}
                                            <div className="text-left">
                                                <span className="block italic">Start Operation</span>
                                                <span className="text-sm font-bold text-white/50 uppercase tracking-widest block mt-1 leading-none">CHECK-IN</span>
                                            </div>
                                        </div>
                                        <ChevronRight className="w-10 h-10 opacity-20 group-hover:opacity-100 group-hover:translate-x-2 transition-all" />

                                        {/* Premium Glow Effect */}
                                        {!actionLoading && canStart && (
                                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-[100%] group-hover:translate-x-[100%] transition-transform duration-1000 ease-in-out" />
                                        )}
                                    </button>

                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            onClick={() => handleCompleteClick('PASS')}
                                            disabled={!canComplete || actionLoading}
                                            className={cn(
                                                'group relative py-10 rounded-[3rem] font-black text-3xl flex flex-col items-center justify-center gap-3 transition-all duration-500 border-2',
                                                !canComplete || actionLoading
                                                    ? 'btn-action-disabled'
                                                    : 'btn-action-success border-success-400/30 shadow-[0_20px_40px_rgba(16,185,129,0.3)] hover:scale-[1.02] active:scale-95'
                                            )}
                                        >
                                            <CheckCircle className="w-12 h-12 group-hover:scale-110 transition-transform" />
                                            <span>Pass</span>
                                            <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-50">FINALIZE</span>
                                        </button>
                                        <button
                                            onClick={() => handleCompleteClick('FAIL')}
                                            disabled={!canComplete || actionLoading}
                                            className={cn(
                                                'group relative py-10 rounded-[3rem] font-black text-3xl flex flex-col items-center justify-center gap-3 transition-all duration-500 border-2',
                                                !canComplete || actionLoading
                                                    ? 'btn-action-disabled'
                                                    : 'btn-action-danger border-danger-400/30 shadow-[0_20px_40px_rgba(239,68,68,0.3)] hover:scale-[1.02] active:scale-95'
                                            )}
                                        >
                                            <XCircle className="w-12 h-12 group-hover:scale-110 transition-transform" />
                                            <span>Fail</span>
                                            <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-50">REJECT</span>
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Help Guidance Case */}
                            {!canStart && !canComplete && !allCompleted && (
                                <div className="flex items-center justify-center gap-4 text-xs font-black text-muted uppercase tracking-[0.4em] py-6 bg-sub rounded-3xl border-2 border-dashed border-main animate-pulse text-center px-6">
                                    <AlertCircle className="w-5 h-5" />
                                    <span>Select a process from the flow timeline below to proceed</span>
                                </div>
                            )}
                        </div>

                        {/* Timeline Area (Below Actions) */}
                        <div className="glass-card p-8 lg:p-10 border-main">
                            <div className="flex items-center justify-between mb-8 px-2">
                                <h4 className="text-sm font-black text-neutral-500 uppercase tracking-[0.4em] flex items-center gap-3">
                                    <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                                    Manufacturing Flow Status
                                </h4>
                                <span className="text-[10px] font-black text-primary-400 bg-primary-500/10 px-3 py-1 rounded-full border border-primary-500/20 uppercase tracking-widest">
                                    Real-time Sync
                                </span>
                            </div>
                            <WipFlowTimeline
                                trace={trace}
                                processes={processes}
                                selectedProcessNumber={selectedProcessNumber}
                                onProcessSelect={handleProcessSelect}
                                disabled={actionLoading}
                            />
                        </div>
                    </div>
                </div>
            )}

            {step === 'measurement' && (
                <div className="glass-card p-6 sm:p-10 w-full border-main overflow-visible">
                    <div className="flex items-center gap-4 mb-6 pb-6 border-b border-main">
                        <div className={cn(
                            'w-12 h-12 sm:w-14 sm:h-14 rounded-2xl flex items-center justify-center border shrink-0',
                            pendingResult === 'PASS' ? 'bg-success-500/10 border-success-500/20' : 'bg-danger-500/10 border-danger-500/20'
                        )}>
                            {pendingResult === 'PASS' ? <CheckCircle className="w-7 h-7 sm:w-8 sm:h-8 text-success-500" /> : <XCircle className="w-7 h-7 sm:w-8 sm:h-8 text-danger-500" />}
                        </div>
                        <div className="min-w-0">
                            <h3 className="text-xl sm:text-2xl font-black text-dynamic truncate">Quality Inspection Report</h3>
                            <p className="text-xs sm:text-sm font-bold text-muted uppercase tracking-widest">
                                {pendingResult === 'PASS' ? 'Quality Pass Confirmation' : 'Defect Report Entry'}
                            </p>
                        </div>
                    </div>
                    <MeasurementForm
                        process={selectedProcess}
                        result={pendingResult || 'PASS'}
                        onSubmit={handleMeasurementSubmit}
                        onCancel={() => setStep('flow-view')}
                        isLoading={actionLoading}
                    />
                </div>
            )}

            {step === 'complete' && (
                <div className="text-center py-20 animate-in zoom-in duration-500">
                    <div className="w-32 h-32 bg-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-8 border border-primary-500/30 shadow-[0_0_50px_rgba(30,58,95,0.4)]">
                        <CheckCircle className="w-16 h-16 text-primary-400" />
                    </div>
                    <h2 className="text-4xl font-black text-dynamic tracking-tighter mb-4">Operation Successful</h2>
                    <p className="text-neutral-500 text-lg mb-12">Data has been successfully transmitted to the server.</p>
                    <Button size="lg" onClick={onScanNext} className="py-8 px-16 rounded-[3rem] font-black text-2xl shadow-2xl">
                        NEXT SCAN
                    </Button>
                </div>
            )}
        </div>
    );
};
