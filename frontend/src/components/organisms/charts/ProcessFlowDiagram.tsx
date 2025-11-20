/**
 * Process Flow Diagram Component - Pipeline Style
 * Visualizes the production process flow with WIP counts and bottleneck detection
 */

import { AlertTriangle } from 'lucide-react';

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
    <div style={{ padding: '20px 0' }}>
      {/* Pipeline Container */}
      <div style={{ position: 'relative', paddingBottom: '120px' }}>
        {/* Nodes and Lines Row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexWrap: 'wrap',
            gap: '90px 20px',
            paddingBottom: '10px',
          }}
        >
          {processes.flatMap((process, index) => {
            const bottleneck = isBottleneck(process.wip_count);
            const nodeColor = getNodeColor(process.wip_count, bottleneck);
            const isFirst = index === 0;
            const isLast = index === processes.length - 1;

            const elements = [];

            // Add node
            elements.push(
              <div
                key={`node-${index}`}
                style={{
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                {/* Node Circle */}
                <div
                  style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    backgroundColor: isLast ? 'transparent' : nodeColor,
                    border: `3px solid ${nodeColor}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    boxShadow: bottleneck ? `0 0 8px ${nodeColor}` : 'none',
                    zIndex: 2,
                  }}
                >
                  {/* Inner dot for filled nodes */}
                  {!isLast && (
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--color-bg-primary)',
                      }}
                    />
                  )}
                </div>

                {/* Process Info Below Node */}
                <div
                  style={{
                    position: 'absolute',
                    top: '32px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    minWidth: '70px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {/* Process Name */}
                  <div
                    style={{
                      fontSize: '11px',
                      fontWeight: '500',
                      color: bottleneck ? nodeColor : 'var(--color-text-primary)',
                      marginBottom: '4px',
                    }}
                  >
                    {process.process_name}
                  </div>

                  {/* WIP Count */}
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: '700',
                      color: nodeColor,
                    }}
                  >
                    ({process.wip_count})
                  </div>

                  {/* Bottleneck Indicator */}
                  {bottleneck && (
                    <div
                      style={{
                        marginTop: '6px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '2px',
                      }}
                    >
                      <AlertTriangle size={14} color={nodeColor} />
                      <span
                        style={{
                          fontSize: '9px',
                          fontWeight: '600',
                          color: nodeColor,
                          textTransform: 'uppercase',
                        }}
                      >
                        Bottleneck
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );

            // Add connecting line after node (except for last)
            if (!isLast) {
              elements.push(
                <div
                  key={`line-${index}`}
                  style={{
                    flex: '1 1 auto',
                    minWidth: '30px',
                    maxWidth: '80px',
                    height: '3px',
                    backgroundColor: 'var(--color-border)',
                  }}
                />
              );
            }

            return elements;
          })}
        </div>
      </div>

      {/* Legend */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '20px',
          marginTop: '15px',
          fontSize: '10px',
          color: 'var(--color-text-secondary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
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
