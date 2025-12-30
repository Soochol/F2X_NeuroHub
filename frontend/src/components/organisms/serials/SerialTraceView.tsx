/**
 * Serial Trace View Component
 *
 * Displays complete process history for a serial number
 */

import { Card } from '@/components/molecules';
import { ProcessResult, type SerialTrace } from '@/types/api';
import { format } from 'date-fns';
import { formatSerialNumber } from '@/utils/serialNumber';

interface SerialTraceViewProps {
  trace: SerialTrace;
}

export const SerialTraceView = ({ trace }: SerialTraceViewProps) => {
  const getResultColor = (result: ProcessResult | string) => {
    switch (result) {
      case ProcessResult.PASS:
      case 'PASS':
        return { bg: 'var(--color-success-bg)', color: 'var(--color-success)' };
      case ProcessResult.FAIL:
      case 'FAIL':
        return { bg: 'var(--color-error-bg)', color: 'var(--color-error)' };
      case ProcessResult.REWORK:
      case 'REWORK':
        return { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)' };
      default:
        return { bg: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' };
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}min ${secs}sec`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Summary Card */}
      <Card title="Summary">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Serial Number</div>
            <div style={{
              fontWeight: 'bold',
              fontSize: '18px',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.5px'
            }}>
              {formatSerialNumber(trace.serial_number)}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>LOT Number</div>
            <div style={{ fontWeight: 'bold' }}>{trace.lot_number}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Status</div>
            <div>
              <span
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '500',
                  ...getResultColor(trace.status as unknown as ProcessResult),
                }}
              >
                {trace.status}
              </span>
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Rework Count</div>
            <div style={{ fontWeight: 'bold', color: trace.rework_count > 0 ? 'var(--color-warning)' : 'var(--color-success)' }}>
              {trace.rework_count} times
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Total Cycle Time</div>
            <div style={{ fontWeight: 'bold' }}>{formatDuration(trace.total_cycle_time_seconds)}</div>
          </div>
        </div>
      </Card>

      {/* LOT Info Card */}
      <Card title="LOT Information">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Product Model</div>
            <div>{trace.lot_info.product_model}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Production Date</div>
            <div>{trace.lot_info.production_date}</div>
          </div>
        </div>

        {/* Component LOTs */}
        {(trace.component_lots.busbar_lot ||
          trace.component_lots.sma_spring_lot ||
          trace.component_lots.pin_lot ||
          trace.component_lots.hsg_lot) && (
          <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid var(--color-border)' }}>
            <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '10px' }}>Component LOTs</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
              {trace.component_lots.busbar_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Busbar: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.busbar_lot}</span>
                </div>
              )}
              {trace.component_lots.sma_spring_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>SMA Spring: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.sma_spring_lot}</span>
                </div>
              )}
              {trace.component_lots.pin_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Pin: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.pin_lot}</span>
                </div>
              )}
              {trace.component_lots.hsg_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Housing: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.hsg_lot}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Process History */}
      <Card title="Process History (Chronological)">
        <div style={{ position: 'relative' }}>
          {trace.process_history.map((process, index) => (
            <div
              key={index}
              style={{
                position: 'relative',
                paddingLeft: '40px',
                paddingBottom: '30px',
              }}
            >
              {/* Timeline dot */}
              <div
                style={{
                  position: 'absolute',
                  left: '15px',
                  top: '5px',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  ...getResultColor(process.result),
                  border: '2px solid var(--color-bg-primary)',
                  boxShadow: '0 0 0 2px ' + getResultColor(process.result).color,
                }}
              />

              {/* Timeline line */}
              {index < trace.process_history.length - 1 && (
                <div
                  style={{
                    position: 'absolute',
                    left: '19px',
                    top: '15px',
                    width: '2px',
                    height: 'calc(100% - 15px)',
                    backgroundColor: 'var(--color-border)',
                  }}
                />
              )}

              {/* Process content */}
              <div
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid var(--color-border)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '5px' }}>
                      P{process.process_number}. {process.process_name}
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                      Worker: {process.worker_name}
                    </div>
                  </div>
                  <span
                    style={{
                      padding: '4px 12px',
                      borderRadius: '4px',
                      fontSize: '13px',
                      fontWeight: '500',
                      ...getResultColor(process.result),
                    }}
                  >
                    {process.result}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', fontSize: '13px', marginTop: '10px' }}>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Started: </span>
                    {process.start_time ? format(new Date(process.start_time), 'MM/dd HH:mm:ss') : '-'}
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Completed: </span>
                    {process.complete_time ? format(new Date(process.complete_time), 'MM/dd HH:mm:ss') : '-'}
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Duration: </span>
                    <span style={{ fontWeight: '500' }}>{process.duration_seconds ? formatDuration(process.duration_seconds) : '-'}</span>
                  </div>
                </div>

                {/* Measurements */}
                {process.process_data && Object.keys(process.process_data).length > 0 && (
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: 'var(--color-text-secondary)' }}>
                      Measurement Data
                    </div>
                    <div style={{ fontSize: '13px', display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
                      {Object.entries(process.process_data!).map(([key, value]) => (
                        <div key={key}>
                          <span style={{ color: 'var(--color-text-secondary)' }}>{key}: </span>
                          <span style={{ fontWeight: '500' }}>{JSON.stringify(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Defect codes */}
                {process.defects && process.defects.length > 0 && (
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: 'var(--color-error)' }}>
                      Defect Codes
                    </div>
                    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                      {process.defects!.map((code, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '3px 8px',
                            backgroundColor: 'var(--color-error-bg)',
                            color: 'var(--color-error)',
                            borderRadius: '4px',
                            fontSize: '12px',
                          }}
                        >
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Notes */}
                {process.notes && (
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: 'var(--color-text-secondary)' }}>
                      Notes
                    </div>
                    <div style={{ fontSize: '13px', fontStyle: 'italic' }}>{process.notes}</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Rework History (if any) */}
      {trace.rework_history.length > 0 && (
        <Card title="Rework History">
          <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '15px' }}>
            Total of {trace.rework_history.length} rework(s) occurred.
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {trace.rework_history.map((rework, index) => (
              <div
                key={index}
                style={{
                  padding: '15px',
                  backgroundColor: 'var(--color-warning-bg)',
                  borderRadius: '8px',
                  border: '1px solid var(--color-warning)',
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>
                  P{rework.process_number}. {rework.process_name} - {rework.worker_name}
                </div>
                <div style={{ fontSize: '13px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Started: </span>
                    {rework.start_time ? format(new Date(rework.start_time), 'yyyy-MM-dd HH:mm:ss') : '-'}
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Completed: </span>
                    {rework.complete_time ? format(new Date(rework.complete_time), 'yyyy-MM-dd HH:mm:ss') : '-'}
                  </div>
                </div>
                {rework.defects && rework.defects.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Defect Codes: </span>
                    {rework.defects.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
