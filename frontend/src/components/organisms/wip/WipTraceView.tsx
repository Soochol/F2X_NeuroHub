/**
 * WIP Trace View Component
 *
 * Displays complete process history for a WIP item
 */

import { Card } from '@/components/molecules';
import { ProcessResult, type WipTrace } from '@/types/api';
import { format } from 'date-fns';

interface WipTraceViewProps {
    trace: WipTrace;
}

export const WipTraceView = ({ trace }: WipTraceViewProps) => {
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

    // Timeline dot color based on process state
    // - PENDING (투입전): gray - no process data yet
    // - IN_PROGRESS (진행중): blue - started but not completed
    // - PASS: green - completed successfully
    // - FAIL: red - completed with failure
    type ProcessHistoryItem = typeof trace.process_history[0];
    const getTimelineDotColor = (latestAttempt: ProcessHistoryItem | null) => {
        // No process data = 투입전 (PENDING)
        if (!latestAttempt) {
            return { bg: 'var(--color-bg-tertiary)', color: 'var(--color-text-tertiary)' };
        }

        // Started but not completed = 진행중 (IN_PROGRESS)
        if (latestAttempt.start_time && !latestAttempt.complete_time) {
            return { bg: 'var(--color-info-bg)', color: 'var(--color-info)' };
        }

        // Completed with result
        switch (latestAttempt.result) {
            case ProcessResult.PASS:
                return { bg: 'var(--color-success-bg)', color: 'var(--color-success)' };
            case ProcessResult.FAIL:
                return { bg: 'var(--color-error-bg)', color: 'var(--color-error)' };
            default:
                return { bg: 'var(--color-bg-tertiary)', color: 'var(--color-text-tertiary)' };
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
                        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>WIP ID</div>
                        <div style={{
                            fontWeight: 'bold',
                            fontSize: '18px',
                            fontFamily: 'var(--font-mono)',
                            letterSpacing: '0.5px'
                        }}>
                            {trace.wip_id}
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
                                    ...getResultColor(trace.status as unknown as ProcessResult), // Status might not match ProcessResult exactly but using same colors
                                }}
                            >
                                {trace.status}
                            </span>
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
                    <div>
                        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Target Quantity</div>
                        <div>{trace.lot_info.target_quantity}</div>
                    </div>
                </div>

                {/* Component LOTs */}
                {(trace.component_lots.busbar_lot ||
                    trace.component_lots.sma_spring_lot) && (
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
                            </div>
                        </div>
                    )}
            </Card>

            {/* Process History */}
            <Card title="Process History (Chronological)">
                <div style={{ position: 'relative' }}>
                    {(() => {
                        // Group process history by process_number
                        const groupedByProcess = trace.process_history.reduce((acc, process) => {
                            const key = process.process_number;
                            if (!acc[key]) {
                                acc[key] = [];
                            }
                            acc[key].push(process);
                            return acc;
                        }, {} as Record<number, typeof trace.process_history>);

                        // Get unique process numbers in order
                        const processNumbers = Object.keys(groupedByProcess)
                            .map(Number)
                            .sort((a, b) => a - b);

                        return processNumbers.map((processNum, groupIndex) => {
                            const processGroup = groupedByProcess[processNum];
                            const latestAttempt = processGroup[processGroup.length - 1];
                            const hasMultipleAttempts = processGroup.length > 1;
                            const hasFails = processGroup.some(p => p.result === 'FAIL');

                            return (
                                <div
                                    key={processNum}
                                    style={{
                                        position: 'relative',
                                        paddingLeft: '40px',
                                        paddingBottom: '30px',
                                    }}
                                >
                                    {/* Timeline dot - color based on process state */}
                                    <div
                                        style={{
                                            position: 'absolute',
                                            left: '15px',
                                            top: '5px',
                                            width: '10px',
                                            height: '10px',
                                            borderRadius: '50%',
                                            ...getTimelineDotColor(latestAttempt),
                                            border: '2px solid var(--color-bg-primary)',
                                            boxShadow: '0 0 0 2px ' + getTimelineDotColor(latestAttempt).color,
                                        }}
                                    />

                                    {/* Timeline line */}
                                    {groupIndex < processNumbers.length - 1 && (
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

                                    {/* Process Card */}
                                    <div
                                        style={{
                                            backgroundColor: 'var(--color-bg-tertiary)',
                                            padding: '15px',
                                            borderRadius: '8px',
                                            border: hasFails ? '1px solid var(--color-warning)' : '1px solid var(--color-border)',
                                        }}
                                    >
                                        {/* Header */}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                                            <div>
                                                <div style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '5px' }}>
                                                    P{latestAttempt.process_number}. {latestAttempt.process_name}
                                                    {hasMultipleAttempts && (
                                                        <span style={{
                                                            marginLeft: '8px',
                                                            fontSize: '12px',
                                                            color: 'var(--color-warning)',
                                                            fontWeight: 'normal'
                                                        }}>
                                                            ({processGroup.length} attempts)
                                                        </span>
                                                    )}
                                                </div>
                                                <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                                                    Worker: {latestAttempt.worker_name}
                                                </div>
                                            </div>
                                            <span
                                                style={{
                                                    padding: '4px 12px',
                                                    borderRadius: '4px',
                                                    fontSize: '13px',
                                                    fontWeight: '500',
                                                    ...getResultColor(latestAttempt.result),
                                                }}
                                            >
                                                {latestAttempt.result}
                                            </span>
                                        </div>

                                        {/* Latest attempt info */}
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', fontSize: '13px', marginTop: '10px' }}>
                                            <div>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>Started: </span>
                                                {latestAttempt.start_time ? format(new Date(latestAttempt.start_time), 'MM/dd HH:mm:ss') : '-'}
                                            </div>
                                            <div>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>Completed: </span>
                                                {latestAttempt.complete_time ? format(new Date(latestAttempt.complete_time), 'MM/dd HH:mm:ss') : '-'}
                                            </div>
                                            <div>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>Duration: </span>
                                                <span style={{ fontWeight: '500' }}>{latestAttempt.duration_seconds ? formatDuration(latestAttempt.duration_seconds) : '-'}</span>
                                            </div>
                                        </div>

                                        {/* History Panel for multiple attempts */}
                                        {hasMultipleAttempts && (
                                            <div style={{
                                                marginTop: '15px',
                                                paddingTop: '15px',
                                                borderTop: '1px solid var(--color-border)',
                                                backgroundColor: 'var(--color-bg-secondary)',
                                                padding: '10px',
                                                borderRadius: '6px'
                                            }}>
                                                <div style={{
                                                    fontSize: '12px',
                                                    fontWeight: '600',
                                                    marginBottom: '10px',
                                                    color: 'var(--color-text-secondary)'
                                                }}>
                                                    📋 Attempt History ({processGroup.length})
                                                </div>

                                                {processGroup.map((attempt, attemptIndex) => (
                                                    <div
                                                        key={attemptIndex}
                                                        style={{
                                                            padding: '8px',
                                                            marginBottom: attemptIndex < processGroup.length - 1 ? '8px' : '0',
                                                            backgroundColor: 'var(--color-bg-tertiary)',
                                                            borderRadius: '4px',
                                                            borderLeft: `3px solid ${getResultColor(attempt.result).color}`,
                                                        }}
                                                    >
                                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                                                            <span style={{ fontSize: '12px', fontWeight: '600' }}>
                                                                Attempt {attemptIndex + 1}
                                                            </span>
                                                            <span
                                                                style={{
                                                                    padding: '2px 8px',
                                                                    borderRadius: '3px',
                                                                    fontSize: '11px',
                                                                    fontWeight: '500',
                                                                    ...getResultColor(attempt.result),
                                                                }}
                                                            >
                                                                {attempt.result}
                                                            </span>
                                                        </div>
                                                        <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', display: 'flex', gap: '10px' }}>
                                                            <span>
                                                                {attempt.start_time ? format(new Date(attempt.start_time), 'MM/dd HH:mm:ss') : '-'}
                                                            </span>
                                                            <span>→</span>
                                                            <span>
                                                                {attempt.complete_time ? format(new Date(attempt.complete_time), 'MM/dd HH:mm:ss') : '-'}
                                                            </span>
                                                            <span>
                                                                ({attempt.duration_seconds ? formatDuration(attempt.duration_seconds) : '-'})
                                                            </span>
                                                        </div>

                                                        {/* Defects for failed attempts */}
                                                        {attempt.result === 'FAIL' && attempt.defects && attempt.defects.length > 0 && (
                                                            <div style={{ marginTop: '5px', fontSize: '11px' }}>
                                                                <span style={{ color: 'var(--color-error)' }}>Defects: </span>
                                                                {attempt.defects.join(', ')}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {/* Measurements - only for latest */}
                                        {latestAttempt.process_data && Object.keys(latestAttempt.process_data).length > 0 && (
                                            <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
                                                <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: 'var(--color-text-secondary)' }}>
                                                    Measurement Data
                                                </div>
                                                <div style={{ fontSize: '13px', display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
                                                    {Object.entries(latestAttempt.process_data).map(([key, value]) => (
                                                        <div key={key}>
                                                            <span style={{ color: 'var(--color-text-secondary)' }}>{key}: </span>
                                                            <span style={{ fontWeight: '500' }}>{JSON.stringify(value)}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Notes */}
                                        {latestAttempt.notes && (
                                            <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--color-border)' }}>
                                                <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '5px', color: 'var(--color-text-secondary)' }}>
                                                    Notes
                                                </div>
                                                <div style={{ fontSize: '13px', fontStyle: 'italic' }}>{latestAttempt.notes}</div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        });
                    })()}
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
