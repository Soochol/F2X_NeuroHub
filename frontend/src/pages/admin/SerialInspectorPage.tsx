/**
 * Serial Inspector Page
 * Detect and manage problematic serials that require admin attention
 */

import { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { Card, Button, Select, Modal } from '@/components/common';
import { serialsApi } from '@/api';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole, SerialStatus, type Serial, getErrorMessage } from '@/types/api';
import { AlertTriangle } from 'lucide-react';

interface ProblemSerial {
    serial: Serial;
    issue: string;
    severity: 'high' | 'medium' | 'low';
}

const identifyProblemSerials = (serialsList: Serial[]): ProblemSerial[] => {
    const problems: ProblemSerial[] = [];
    const now = new Date();

    serialsList.forEach((serial) => {
        // Check for stuck serials (24+ hours)
        if (serial.status === SerialStatus.IN_PROGRESS && serial.created_at) {
            const hoursSinceCreation = (now.getTime() - new Date(serial.created_at).getTime()) / (1000 * 60 * 60);
            if (hoursSinceCreation > 24) {
                problems.push({
                    serial,
                    issue: `Stuck in process for ${Math.floor(hoursSinceCreation)} hours`,
                    severity: 'high',
                });
            }
        }

        // Check for excessive rework
        if (serial.rework_count && serial.rework_count >= 3) {
            problems.push({
                serial,
                issue: `Rework count: ${serial.rework_count} (maximum reached)`,
                severity: 'high',
            });
        }

        // Check for failed serials
        if (serial.status === SerialStatus.FAIL) {
            problems.push({
                serial,
                issue: 'Failed - requires action',
                severity: 'medium',
            });
        }
    });

    return problems;
};

export const SerialInspectorPage = () => {
    const { user } = useAuth();

    const [serials, setSerials] = useState<Serial[]>([]);
    const [problemSerials, setProblemSerials] = useState<ProblemSerial[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // Modal states
    const [showStatusChangeModal, setShowStatusChangeModal] = useState(false);
    const [selectedSerial, setSelectedSerial] = useState<Serial | null>(null);
    const [newStatus, setNewStatus] = useState<SerialStatus>(SerialStatus.PASS);
    const [changeReason, setChangeReason] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchData = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const serialsResponse = await serialsApi.getSerials({ limit: 500 });
            const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
            setSerials(serialsList);

            const problems = identifyProblemSerials(serialsList);
            setProblemSerials(problems);
        } catch (err: unknown) {
            setError(getErrorMessage(err, 'Failed to load serials'));
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    if (user?.role !== UserRole.ADMIN && user?.role !== UserRole.MANAGER) {
        return <Navigate to="/" replace />;
    }

    const handleForceStatusChange = async () => {
        if (!selectedSerial || !changeReason.trim()) {
            alert('Please provide a reason for this change');
            return;
        }

        setIsSubmitting(true);
        try {
            await serialsApi.updateSerialStatus(selectedSerial.id, {
                status: newStatus,
                failure_reason: changeReason,
            });

            alert('Status changed successfully');
            setShowStatusChangeModal(false);
            setSelectedSerial(null);
            setChangeReason('');
            await fetchData();
        } catch (err: unknown) {
            alert(getErrorMessage(err, 'Failed to change status'));
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                    <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px' }}>
                        Serial Inspector
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                        Detect and manage problematic serials requiring attention
                    </p>
                </div>
                <Button variant="secondary" onClick={fetchData}>
                    Refresh
                </Button>
            </div>

            {/* Quick Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <Card style={{ padding: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                        Total Serials
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                        {serials.length}
                    </div>
                </Card>

                <Card style={{ padding: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                        Problem Serials
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-error)' }}>
                        {problemSerials.length}
                    </div>
                </Card>
            </div>

            {/* Problem Serials Section */}
            <Card>
                <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)' }}>
                    <h2 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <AlertTriangle size={20} style={{ color: 'var(--color-error)' }} />
                        Serials Requiring Attention
                    </h2>
                </div>
                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                        Loading...
                    </div>
                ) : error ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
                        {error}
                    </div>
                ) : problemSerials.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                        No problem serials found. System is running smoothly!
                    </div>
                ) : (
                    <div style={{ padding: '20px' }}>
                        <div style={{ display: 'grid', gap: '12px' }}>
                            {problemSerials.map((problem) => (
                                <div
                                    key={problem.serial.id}
                                    style={{
                                        padding: '15px',
                                        border: `2px solid ${problem.severity === 'high'
                                                ? 'var(--color-error)'
                                                : problem.severity === 'medium'
                                                    ? 'var(--color-warning)'
                                                    : 'var(--color-info)'
                                            }`,
                                        borderRadius: '6px',
                                        backgroundColor: 'var(--color-bg-secondary)',
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace', marginBottom: '8px', color: 'var(--color-text-primary)' }}>
                                                {problem.serial.serial_number}
                                            </div>
                                            <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                                                {problem.issue}
                                            </div>
                                            {problem.serial.lot && (
                                                <div style={{ fontSize: '13px', color: 'var(--color-text-tertiary)' }}>
                                                    LOT: {problem.serial.lot.lot_number}
                                                </div>
                                            )}
                                        </div>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <Button
                                                size="sm"
                                                variant="danger"
                                                onClick={() => {
                                                    setSelectedSerial(problem.serial);
                                                    setNewStatus(SerialStatus.PASS);
                                                    setShowStatusChangeModal(true);
                                                }}
                                            >
                                                Force Complete
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="secondary"
                                                onClick={() => {
                                                    setSelectedSerial(problem.serial);
                                                    setNewStatus(SerialStatus.CREATED);
                                                    setShowStatusChangeModal(true);
                                                }}
                                            >
                                                Reset
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </Card>

            {/* Force Status Change Modal */}
            <Modal
                isOpen={showStatusChangeModal}
                onClose={() => {
                    setShowStatusChangeModal(false);
                    setSelectedSerial(null);
                    setChangeReason('');
                }}
                title="Force Status Change - DANGER"
                width="600px"
                footer={
                    <>
                        <Button
                            variant="secondary"
                            onClick={() => {
                                setShowStatusChangeModal(false);
                                setSelectedSerial(null);
                                setChangeReason('');
                            }}
                        >
                            Cancel
                        </Button>
                        <Button onClick={handleForceStatusChange} disabled={isSubmitting || !changeReason.trim()}>
                            {isSubmitting ? 'Changing...' : 'Confirm & Change'}
                        </Button>
                    </>
                }
            >
                {selectedSerial && (
                    <div>
                        <div
                            style={{
                                padding: '15px',
                                backgroundColor: 'var(--color-error-bg)',
                                borderLeft: '4px solid var(--color-error)',
                                borderRadius: '6px',
                                marginBottom: '20px',
                            }}
                        >
                            <div style={{ display: 'flex', gap: '10px', alignItems: 'start' }}>
                                <AlertTriangle size={20} style={{ color: 'var(--color-error)', flexShrink: 0 }} />
                                <div style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                                    <strong>Warning:</strong> This bypasses normal workflow rules! Use only for emergency situations.
                                </div>
                            </div>
                        </div>

                        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>
                                Serial Number:
                            </div>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
                                {selectedSerial.serial_number}
                            </div>
                            <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginTop: '10px' }}>
                                Current Status: <strong>{selectedSerial.status}</strong>
                            </div>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <Select
                                label="New Status"
                                value={newStatus}
                                onChange={(e) => setNewStatus(e.target.value as SerialStatus)}
                                options={[
                                    { value: SerialStatus.CREATED, label: 'Created' },
                                    { value: SerialStatus.IN_PROGRESS, label: 'In Progress' },
                                    { value: SerialStatus.PASS, label: 'Pass' },
                                    { value: SerialStatus.FAIL, label: 'Fail' },
                                ]}
                            />
                        </div>

                        <div>
                            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>
                                Reason (Required) <span style={{ color: 'var(--color-error)' }}>*</span>
                            </label>
                            <textarea
                                value={changeReason}
                                onChange={(e) => setChangeReason(e.target.value)}
                                placeholder="Explain why this status change is necessary..."
                                required
                                style={{
                                    width: '100%',
                                    minHeight: '100px',
                                    padding: '10px',
                                    border: '1px solid var(--color-border)',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    resize: 'vertical',
                                    backgroundColor: 'var(--color-bg-primary)',
                                    color: 'var(--color-text-primary)',
                                }}
                            />
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};
