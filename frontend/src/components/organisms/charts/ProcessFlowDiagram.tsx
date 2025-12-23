/**
 * Process Flow Diagram Component - Vertical Pipeline Style
 * Visualizes the production process flow with WIP counts and bottleneck detection
 */

import { AlertTriangle, ArrowDown } from 'lucide-react';

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

  // Get node color based on WIP intensity
  const getNodeColor = (wipCount: number, bottleneck: boolean) => {
    if (bottleneck) return 'var(--color-error)';
    const intensity = wipCount / maxWip;
    if (intensity > 0.7) return 'var(--color-warning)';
    if (intensity > 0.4) return 'var(--color-info)';
    return 'var(--color-success)';
  };

  return (
    <div style={{ padding: '12px 0' }}>
      {/* Vertical Pipeline Container */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0',
        }}
      >
        {processes.map((process, index) => {
          const bottleneck = isBottleneck(process.wip_count);
          const nodeColor = getNodeColor(process.wip_count, bottleneck);
          const isLast = index === processes.length - 1;

          return (
            <div key={`process-${index}`}>
              {/* Process Row */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '8px 12px',
                  backgroundColor: bottleneck ? 'rgba(255, 77, 79, 0.08)' : 'transparent',
                  borderRadius: '8px',
                  transition: 'background-color 0.2s',
                }}
              >
                {/* Step Number with Node */}
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    backgroundColor: nodeColor,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: '13px',
                    fontWeight: '700',
                    flexShrink: 0,
                    boxShadow: bottleneck ? `0 0 10px ${nodeColor}` : 'none',
                  }}
                >
                  {index + 1}
                </div>

                {/* Process Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: '600',
                      color: bottleneck ? nodeColor : 'var(--color-text-primary)',
                      marginBottom: '2px',
                    }}
                  >
                    {process.process_name}
                  </div>
                </div>

                {/* WIP Count Badge */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {bottleneck && (
                    <AlertTriangle size={16} color={nodeColor} />
                  )}
                  <div
                    style={{
                      minWidth: '48px',
                      padding: '4px 10px',
                      borderRadius: '12px',
                      backgroundColor: `${nodeColor}20`,
                      color: nodeColor,
                      fontSize: '13px',
                      fontWeight: '700',
                      textAlign: 'center',
                    }}
                  >
                    {process.wip_count}
                  </div>
                </div>
              </div>

              {/* Connecting Arrow (except for last) */}
              {!isLast && (
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'flex-start',
                    paddingLeft: '20px',
                    height: '20px',
                    alignItems: 'center',
                  }}
                >
                  <ArrowDown size={16} color="var(--color-border)" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'flex-start',
          gap: '16px',
          marginTop: '16px',
          paddingTop: '12px',
          borderTop: '1px solid var(--color-border)',
          fontSize: '11px',
          color: 'var(--color-text-secondary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-success)',
            }}
          />
          <span>Normal</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-warning)',
            }}
          />
          <span>High</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-error)',
            }}
          />
          <span>Bottleneck</span>
        </div>
      </div>
    </div>
  );
};
