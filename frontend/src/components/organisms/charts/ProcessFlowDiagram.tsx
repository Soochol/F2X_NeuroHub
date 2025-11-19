/**
 * Process Flow Diagram Component
 * Visualizes the production process flow with WIP counts and bottleneck detection
 */

import { ArrowRight, AlertTriangle } from 'lucide-react';

interface ProcessWipData {
  process_name: string;
  wip_count: number;
}

interface ProcessFlowDiagramProps {
  data: ProcessWipData[];
}

export const ProcessFlowDiagram = ({ data }: ProcessFlowDiagramProps) => {
  // Ensure data is an array
  const processes = Array.isArray(data) ? data : [];

  if (processes.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-text-secondary)' }}>
        No process data available
      </div>
    );
  }

  // Calculate max WIP for bottleneck detection
  const maxWip = Math.max(...processes.map((p) => p.wip_count), 1);
  const avgWip = processes.reduce((sum, p) => sum + p.wip_count, 0) / processes.length;

  // Determine if a process is a bottleneck (WIP significantly higher than average)
  const isBottleneck = (wipCount: number) => wipCount > avgWip * 1.5 && wipCount === maxWip;

  return (
    <div style={{ padding: '20px 0' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '10px',
        }}
      >
        {processes.map((process, index) => {
          const bottleneck = isBottleneck(process.wip_count);
          const intensity = process.wip_count / maxWip;

          // Determine color based on WIP intensity
          let bgColor = 'var(--color-success-light)';
          let borderColor = 'var(--color-success)';
          let textColor = 'var(--color-success)';

          if (bottleneck) {
            bgColor = 'var(--color-error-light)';
            borderColor = 'var(--color-error)';
            textColor = 'var(--color-error)';
          } else if (intensity > 0.7) {
            bgColor = 'var(--color-warning-light)';
            borderColor = 'var(--color-warning)';
            textColor = 'var(--color-warning)';
          } else if (intensity > 0.4) {
            bgColor = 'var(--color-info-light)';
            borderColor = 'var(--color-info)';
            textColor = 'var(--color-info)';
          }

          return (
            <div key={process.process_name} style={{ display: 'flex', alignItems: 'center' }}>
              {/* Process Box */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  minWidth: '100px',
                }}
              >
                <div
                  style={{
                    backgroundColor: bgColor,
                    border: `2px solid ${borderColor}`,
                    borderRadius: '8px',
                    padding: '12px 16px',
                    textAlign: 'center',
                    position: 'relative',
                    minWidth: '90px',
                  }}
                >
                  {bottleneck && (
                    <div
                      style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '-10px',
                        backgroundColor: 'var(--color-error)',
                        borderRadius: '50%',
                        padding: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <AlertTriangle size={12} color="white" />
                    </div>
                  )}
                  <div
                    style={{
                      fontSize: '12px',
                      fontWeight: '500',
                      color: 'var(--color-text-primary)',
                      marginBottom: '4px',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {process.process_name}
                  </div>
                  <div
                    style={{
                      fontSize: '20px',
                      fontWeight: '700',
                      color: textColor,
                    }}
                  >
                    {process.wip_count}
                  </div>
                </div>
                {bottleneck && (
                  <div
                    style={{
                      marginTop: '6px',
                      fontSize: '10px',
                      fontWeight: '600',
                      color: 'var(--color-error)',
                      textTransform: 'uppercase',
                    }}
                  >
                    Bottleneck
                  </div>
                )}
              </div>

              {/* Arrow between processes */}
              {index < processes.length - 1 && (
                <div style={{ padding: '0 8px', color: 'var(--color-text-tertiary)' }}>
                  <ArrowRight size={20} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
