/**
 * Serial Trace View Component
 *
 * Displays complete process history for a serial number
 */

import { Card } from '../common/Card';
import { ProcessResult, type SerialTrace } from '@/types/api';
import { format } from 'date-fns';

interface SerialTraceViewProps {
  trace: SerialTrace;
}

export const SerialTraceView = ({ trace }: SerialTraceViewProps) => {
  const getResultColor = (result: ProcessResult) => {
    switch (result) {
      case ProcessResult.PASS:
        return { bg: '#d5f4e6', color: '#27ae60' };
      case ProcessResult.FAIL:
        return { bg: '#fee', color: '#e74c3c' };
      case ProcessResult.REWORK:
        return { bg: '#fff3cd', color: '#f39c12' };
      default:
        return { bg: '#f5f5f5', color: '#7f8c8d' };
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}분 ${secs}초`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Summary Card */}
      <Card title="요약 정보">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>Serial 번호</div>
            <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{trace.serial_number}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>LOT 번호</div>
            <div style={{ fontWeight: 'bold' }}>{trace.lot_number}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>상태</div>
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
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>재작업 횟수</div>
            <div style={{ fontWeight: 'bold', color: trace.rework_count > 0 ? '#f39c12' : '#27ae60' }}>
              {trace.rework_count}회
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>총 사이클 타임</div>
            <div style={{ fontWeight: 'bold' }}>{formatDuration(trace.total_cycle_time_seconds)}</div>
          </div>
        </div>
      </Card>

      {/* LOT Info Card */}
      <Card title="LOT 정보">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>제품 모델</div>
            <div>{trace.lot_info.product_model_name}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>생산 날짜</div>
            <div>{trace.lot_info.production_date}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>시프트</div>
            <div>{trace.lot_info.shift}</div>
          </div>
        </div>

        {/* Component LOTs */}
        {(trace.component_lots.busbar_lot ||
          trace.component_lots.sma_spring_lot ||
          trace.component_lots.pin_lot ||
          trace.component_lots.hsg_lot) && (
          <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #e0e0e0' }}>
            <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '10px' }}>구성품 LOT</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
              {trace.component_lots.busbar_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Busbar: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.busbar_lot}</span>
                </div>
              )}
              {trace.component_lots.sma_spring_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>SMA Spring: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.sma_spring_lot}</span>
                </div>
              )}
              {trace.component_lots.pin_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Pin: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.pin_lot}</span>
                </div>
              )}
              {trace.component_lots.hsg_lot && (
                <div>
                  <span style={{ fontSize: '12px', color: '#7f8c8d' }}>Housing: </span>
                  <span style={{ fontSize: '13px' }}>{trace.component_lots.hsg_lot}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Process History */}
      <Card title="공정 이력 (시간순)">
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
                  border: '2px solid white',
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
                    backgroundColor: '#e0e0e0',
                  }}
                />
              )}

              {/* Process content */}
              <div
                style={{
                  backgroundColor: '#f8f9fa',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid #e0e0e0',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '5px' }}>
                      P{process.process_number}. {process.process_name}
                    </div>
                    <div style={{ fontSize: '13px', color: '#7f8c8d' }}>
                      작업자: {process.worker_name}
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
                    <span style={{ color: '#7f8c8d' }}>시작: </span>
                    {format(new Date(process.started_at), 'MM/dd HH:mm:ss')}
                  </div>
                  <div>
                    <span style={{ color: '#7f8c8d' }}>완료: </span>
                    {format(new Date(process.completed_at), 'MM/dd HH:mm:ss')}
                  </div>
                  <div>
                    <span style={{ color: '#7f8c8d' }}>소요시간: </span>
                    <span style={{ fontWeight: '500' }}>{formatDuration(process.cycle_time_seconds)}</span>
                  </div>
                </div>

                {/* Measurements */}
                {process.measurements && Object.keys(process.measurements).length > 0 && (
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e0e0e0' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: '#7f8c8d' }}>
                      측정 데이터
                    </div>
                    <div style={{ fontSize: '13px', display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
                      {Object.entries(process.measurements).map(([key, value]) => (
                        <div key={key}>
                          <span style={{ color: '#7f8c8d' }}>{key}: </span>
                          <span style={{ fontWeight: '500' }}>{JSON.stringify(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Defect codes */}
                {process.defect_codes && process.defect_codes.length > 0 && (
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e0e0e0' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: '#e74c3c' }}>
                      불량 코드
                    </div>
                    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                      {process.defect_codes.map((code, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '3px 8px',
                            backgroundColor: '#fee',
                            color: '#e74c3c',
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
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e0e0e0' }}>
                    <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: '#7f8c8d' }}>
                      비고
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
        <Card title="재작업 이력">
          <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '15px' }}>
            총 {trace.rework_history.length}건의 재작업이 발생했습니다.
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {trace.rework_history.map((rework, index) => (
              <div
                key={index}
                style={{
                  padding: '15px',
                  backgroundColor: '#fff3cd',
                  borderRadius: '8px',
                  border: '1px solid #f39c12',
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>
                  P{rework.process_number}. {rework.process_name} - {rework.worker_name}
                </div>
                <div style={{ fontSize: '13px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <span style={{ color: '#7f8c8d' }}>시작: </span>
                    {format(new Date(rework.started_at), 'yyyy-MM-dd HH:mm:ss')}
                  </div>
                  <div>
                    <span style={{ color: '#7f8c8d' }}>완료: </span>
                    {format(new Date(rework.completed_at), 'yyyy-MM-dd HH:mm:ss')}
                  </div>
                </div>
                {rework.defect_codes && rework.defect_codes.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <span style={{ fontSize: '12px', color: '#7f8c8d' }}>불량 코드: </span>
                    {rework.defect_codes.join(', ')}
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
