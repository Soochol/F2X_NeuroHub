/**
 * Process Timeline Component
 *
 * Visualizes the manufacturing process progress:
 * - Completed processes (green checkmark)
 * - Current/active process (highlighted)
 * - Pending processes (gray)
 */

import { Card } from '@/components/common';
import type { Process, ProcessData } from '@/types/api';

interface ProcessTimelineProps {
  processes: Process[];
  completedProcesses: ProcessData[];
  currentProcessId?: number;
}

export const ProcessTimeline: React.FC<ProcessTimelineProps> = ({
  processes,
  completedProcesses,
  currentProcessId,
}) => {
  const completedProcessIds = new Set(completedProcesses.map((pd) => pd.process_id));

  const getProcessStatus = (process: Process): 'completed' | 'current' | 'pending' => {
    if (completedProcessIds.has(process.id)) {
      return 'completed';
    }
    if (currentProcessId === process.id) {
      return 'current';
    }
    return 'pending';
  };

  const sortedProcesses = [...processes].sort((a, b) => a.process_number - b.process_number);

  return (
    <Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: 'var(--spacing-2)' }}>Process Progress</h3>

        <div style={{ position: 'relative' }}>
          {/* Vertical line connector */}
          <div
            style={{
              position: 'absolute',
              left: '15px',
              top: '20px',
              bottom: '20px',
              width: '2px',
              backgroundColor: 'var(--color-border-strong)',
            }}
          />

          {/* Process Steps */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
            {sortedProcesses.map((process) => {
              const status = getProcessStatus(process);

              return (
                <div
                  key={process.id}
                  style={{
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-3)',
                    padding: 'var(--spacing-2)',
                    borderRadius: 'var(--radius-base)',
                    backgroundColor:
                      status === 'current'
                        ? 'var(--color-info-bg, rgba(52, 152, 219, 0.1))'
                        : 'transparent',
                    border:
                      status === 'current'
                        ? '1px solid var(--color-brand-400)'
                        : '1px solid transparent',
                  }}
                >
                  {/* Status Icon */}
                  <div
                    style={{
                      position: 'relative',
                      zIndex: 1,
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor:
                        status === 'completed'
                          ? 'var(--color-success)'
                          : status === 'current'
                          ? 'var(--color-brand-400)'
                          : 'var(--color-bg-tertiary)',
                      border: `2px solid ${
                        status === 'completed'
                          ? 'var(--color-success)'
                          : status === 'current'
                          ? 'var(--color-brand-400)'
                          : 'var(--color-border-strong)'
                      }`,
                    }}
                  >
                    {status === 'completed' ? (
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 16 16"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M3 8L6.5 11.5L13 5"
                          stroke="white"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    ) : status === 'current' ? (
                      <div
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: 'white',
                          animation: 'pulse 2s infinite',
                        }}
                      />
                    ) : (
                      <div
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--color-border-strong)',
                        }}
                      />
                    )}
                  </div>

                  {/* Process Information */}
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: '14px',
                        fontWeight: status === 'current' ? '600' : '500',
                        color:
                          status === 'completed' || status === 'current'
                            ? 'var(--color-text-primary)'
                            : 'var(--color-text-secondary)',
                      }}
                    >
                      {process.process_number}. {process.process_name_ko}
                    </div>
                    <div
                      style={{
                        fontSize: '12px',
                        color: 'var(--color-text-secondary)',
                        marginTop: '2px',
                      }}
                    >
                      {process.process_name_en}
                    </div>

                    {/* Show completed process data if available */}
                    {status === 'completed' && (() => {
                      const processData = completedProcesses.find((pd) => pd.process_id === process.id);
                      if (processData) {
                        return (
                          <div
                            style={{
                              marginTop: 'var(--spacing-1)',
                              fontSize: '11px',
                              color: 'var(--color-text-tertiary)',
                            }}
                          >
                            Completed: {new Date(processData.completed_at).toLocaleString()}
                            {processData.cycle_time_seconds && (
                              <span> • {processData.cycle_time_seconds}s</span>
                            )}
                          </div>
                        );
                      }
                      return null;
                    })()}
                  </div>

                  {/* Status Label */}
                  <div>
                    <span
                      style={{
                        fontSize: '11px',
                        fontWeight: '500',
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-base)',
                        backgroundColor:
                          status === 'completed'
                            ? 'var(--color-success-bg, rgba(39, 174, 96, 0.15))'
                            : status === 'current'
                            ? 'var(--color-info-bg, rgba(52, 152, 219, 0.15))'
                            : 'var(--color-bg-tertiary)',
                        color:
                          status === 'completed'
                            ? 'var(--color-success)'
                            : status === 'current'
                            ? 'var(--color-brand-400)'
                            : 'var(--color-text-tertiary)',
                      }}
                    >
                      {status === 'completed' ? 'Done' : status === 'current' ? 'In Progress' : 'Pending'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Inline CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.3;
          }
        }
      `}</style>
    </Card>
  );
};
