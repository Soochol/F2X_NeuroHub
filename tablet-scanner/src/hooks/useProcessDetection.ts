/**
 * Hook for automatic process detection based on WIP status
 *
 * Analyzes WIP trace to recommend the next process
 */
import { useMemo } from 'react';
import type { WIPTrace, Process, NextProcessRecommendation } from '@/types';

// Total number of processes
const TOTAL_PROCESSES = 8;

interface UseProcessDetectionResult {
  recommendation: NextProcessRecommendation | null;
  completedProcesses: number[];
  inProgressProcess: number | null;
  canStart: boolean;
  canComplete: boolean;
  allCompleted: boolean;
}

export const useProcessDetection = (
  trace: WIPTrace | null,
  processes: Process[]
): UseProcessDetectionResult => {
  return useMemo(() => {
    if (!trace || processes.length === 0) {
      return {
        recommendation: null,
        completedProcesses: [],
        inProgressProcess: null,
        canStart: false,
        canComplete: false,
        allCompleted: false,
      };
    }

    // Analyze process history
    const processStatusMap = new Map<number, { started: boolean; completed: boolean; result: string | null }>();

    // Initialize all processes as not started
    for (let i = 1; i <= TOTAL_PROCESSES; i++) {
      processStatusMap.set(i, { started: false, completed: false, result: null });
    }

    // Parse history to find process status
    trace.process_history.forEach((item) => {
      const processNum = item.process_number;
      const existing = processStatusMap.get(processNum);

      if (existing) {
        if (item.start_time) {
          existing.started = true;
        }
        if (item.complete_time && item.result) {
          existing.completed = true;
          existing.result = item.result;
        }
      }
    });

    // Find completed processes (with PASS result)
    const completedProcesses: number[] = [];
    let inProgressProcess: number | null = null;

    processStatusMap.forEach((status, processNum) => {
      if (status.completed && status.result === 'PASS') {
        completedProcesses.push(processNum);
      } else if (status.started && !status.completed) {
        inProgressProcess = processNum;
      }
    });

    // Sort completed processes
    completedProcesses.sort((a, b) => a - b);

    // Determine next process
    let nextProcessNumber: number | null = null;
    let reason = '';

    if (inProgressProcess !== null) {
      // If there's an in-progress process, recommend completing it
      nextProcessNumber = inProgressProcess;
      reason = `공정 ${inProgressProcess}이(가) 진행 중입니다. 완공 처리가 필요합니다.`;
    } else {
      // Find next process in sequence
      for (let i = 1; i <= TOTAL_PROCESSES; i++) {
        const status = processStatusMap.get(i);
        if (!status?.completed || status.result !== 'PASS') {
          // Check if previous process is completed (except for process 1)
          if (i === 1 || completedProcesses.includes(i - 1)) {
            nextProcessNumber = i;
            reason = completedProcesses.length === 0
              ? '첫 번째 공정부터 시작합니다.'
              : `공정 ${i - 1} 완료. 다음 공정 ${i}을(를) 시작하세요.`;
            break;
          }
        }
      }
    }

    // Check if all processes are completed
    const allCompleted = completedProcesses.length === TOTAL_PROCESSES;

    // Build recommendation
    let recommendation: NextProcessRecommendation | null = null;

    if (nextProcessNumber !== null && !allCompleted) {
      const process = processes.find((p) => p.process_number === nextProcessNumber);
      if (process) {
        recommendation = {
          processId: process.id,
          processNumber: process.process_number,
          processName: process.process_name_ko,
          reason,
        };
      }
    }

    return {
      recommendation,
      completedProcesses,
      inProgressProcess,
      canStart: inProgressProcess === null && !allCompleted,
      canComplete: inProgressProcess !== null,
      allCompleted,
    };
  }, [trace, processes]);
};

/**
 * Determine action type based on WIP state
 */
export const determineAction = (
  inProgressProcess: number | null,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- Reserved for future logic
  _completedProcesses: number[]
): 'start' | 'complete' | 'none' => {
  if (inProgressProcess !== null) {
    return 'complete';
  }
  return 'start';
};
