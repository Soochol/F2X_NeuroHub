/**
 * Printer Settings Page
 *
 * Configure Zebra printer IP, port, and test connection
 */

import React, { useState, useEffect } from 'react';
import { Card, Button } from '@/components/common';
import { printerApi, type PrinterSettings } from '@/api/endpoints/printer';
import { useAsyncData } from '@/hooks/useAsyncData';
import { Printer, CheckCircle, XCircle, Loader2, Save, RotateCcw } from 'lucide-react';

export const PrinterSettingsPage: React.FC = () => {
    // Form state
    const [ip, setIp] = useState('');
    const [port, setPort] = useState(9100);
    const [isTesting, setIsTesting] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [testResult, setTestResult] = useState<{
        success: boolean;
        message: string;
        responseTime?: number;
    } | null>(null);
    const [saveMessage, setSaveMessage] = useState<{
        type: 'success' | 'error';
        text: string;
    } | null>(null);

    // Fetch current settings
    const {
        data: settings,
        isLoading,
        refetch
    } = useAsyncData<PrinterSettings>({
        fetchFn: printerApi.getSettings,
        autoFetch: true,
        errorMessage: 'Failed to load printer settings'
    });

    // Update form when settings load
    useEffect(() => {
        if (settings) {
            setIp(settings.ip);
            setPort(settings.port);
        }
    }, [settings]);

    // Test connection
    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);
        setSaveMessage(null);

        try {
            const result = await printerApi.testConnection(ip, port);
            setTestResult({
                success: result.success,
                message: result.success
                    ? `Connected successfully (${result.response_time_ms}ms)`
                    : result.error || 'Connection failed',
                responseTime: result.response_time_ms
            });
        } catch (error) {
            setTestResult({
                success: false,
                message: error instanceof Error ? error.message : 'Connection test failed'
            });
        } finally {
            setIsTesting(false);
        }
    };

    // Save settings
    const handleSave = async () => {
        setIsSaving(true);
        setSaveMessage(null);

        try {
            await printerApi.updateSettings({ ip, port });
            setSaveMessage({
                type: 'success',
                text: 'Settings saved successfully'
            });
            refetch();
        } catch (error) {
            setSaveMessage({
                type: 'error',
                text: error instanceof Error ? error.message : 'Failed to save settings'
            });
        } finally {
            setIsSaving(false);
        }
    };

    // Reset to saved values
    const handleReset = () => {
        if (settings) {
            setIp(settings.ip);
            setPort(settings.port);
        }
        setTestResult(null);
        setSaveMessage(null);
    };

    // Check if form has changes
    const hasChanges = settings && (ip !== settings.ip || port !== settings.port);

    if (isLoading) {
        return (
            <div style={styles.container}>
                <div style={styles.loading}>
                    <Loader2 size={32} className="animate-spin" />
                    <p>Loading settings...</p>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <div style={{ marginBottom: '24px' }}>
                <h1 style={styles.title}>Printer Settings</h1>
                <p style={styles.subtitle}>Configure Zebra label printer connection</p>
            </div>

            <div style={styles.grid}>
                {/* Settings Card */}
                <Card title="Connection Settings" style={{ flex: 2 }}>
                    <div style={styles.form}>
                        {/* IP Address */}
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Printer IP Address</label>
                            <input
                                type="text"
                                value={ip}
                                onChange={(e) => setIp(e.target.value)}
                                placeholder="192.168.35.79"
                                style={styles.input}
                            />
                            <p style={styles.hint}>Enter the IP address of your Zebra printer</p>
                        </div>

                        {/* Port */}
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Port</label>
                            <input
                                type="number"
                                value={port}
                                onChange={(e) => setPort(parseInt(e.target.value) || 9100)}
                                min={1}
                                max={65535}
                                style={styles.input}
                            />
                            <p style={styles.hint}>Default port for Zebra printers is 9100 (Raw TCP)</p>
                        </div>

                        {/* Test Result */}
                        {testResult && (
                            <div style={{
                                ...styles.alert,
                                backgroundColor: testResult.success ? 'rgba(62, 207, 142, 0.1)' : 'rgba(245, 101, 101, 0.1)',
                                borderColor: testResult.success ? '#3ecf8e' : '#f56565',
                            }}>
                                {testResult.success ? (
                                    <CheckCircle size={20} color="#3ecf8e" />
                                ) : (
                                    <XCircle size={20} color="#f56565" />
                                )}
                                <span style={{ color: testResult.success ? '#3ecf8e' : '#f56565' }}>
                                    {testResult.message}
                                </span>
                            </div>
                        )}

                        {/* Save Message */}
                        {saveMessage && (
                            <div style={{
                                ...styles.alert,
                                backgroundColor: saveMessage.type === 'success' ? 'rgba(62, 207, 142, 0.1)' : 'rgba(245, 101, 101, 0.1)',
                                borderColor: saveMessage.type === 'success' ? '#3ecf8e' : '#f56565',
                            }}>
                                {saveMessage.type === 'success' ? (
                                    <CheckCircle size={20} color="#3ecf8e" />
                                ) : (
                                    <XCircle size={20} color="#f56565" />
                                )}
                                <span style={{ color: saveMessage.type === 'success' ? '#3ecf8e' : '#f56565' }}>
                                    {saveMessage.text}
                                </span>
                            </div>
                        )}

                        {/* Actions */}
                        <div style={styles.actions}>
                            <Button
                                variant="secondary"
                                onClick={handleTestConnection}
                                disabled={isTesting || !ip}
                            >
                                {isTesting ? (
                                    <>
                                        <Loader2 size={16} className="animate-spin" style={{ marginRight: '8px' }} />
                                        Testing...
                                    </>
                                ) : (
                                    'Test Connection'
                                )}
                            </Button>

                            <div style={{ display: 'flex', gap: '8px' }}>
                                <Button
                                    variant="secondary"
                                    onClick={handleReset}
                                    disabled={!hasChanges}
                                >
                                    <RotateCcw size={16} style={{ marginRight: '6px' }} />
                                    Reset
                                </Button>

                                <Button
                                    onClick={handleSave}
                                    disabled={isSaving || !hasChanges}
                                >
                                    {isSaving ? (
                                        <>
                                            <Loader2 size={16} className="animate-spin" style={{ marginRight: '8px' }} />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save size={16} style={{ marginRight: '6px' }} />
                                            Save Settings
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Info Card */}
                <Card title="Printer Information" style={{ flex: 1 }}>
                    <div style={styles.infoSection}>
                        <div style={styles.printerIcon}>
                            <Printer size={48} color="var(--color-brand)" />
                        </div>

                        <div style={styles.infoItem}>
                            <span style={styles.infoLabel}>Printer Type</span>
                            <span style={styles.infoValue}>Zebra ZPL Compatible</span>
                        </div>

                        <div style={styles.infoItem}>
                            <span style={styles.infoLabel}>Protocol</span>
                            <span style={styles.infoValue}>Raw TCP (Port 9100)</span>
                        </div>

                        <div style={styles.infoItem}>
                            <span style={styles.infoLabel}>Label Size</span>
                            <span style={styles.infoValue}>60mm x 30mm</span>
                        </div>

                        <div style={styles.infoItem}>
                            <span style={styles.infoLabel}>Current IP</span>
                            <span style={styles.infoValue}>{settings?.ip || '-'}</span>
                        </div>

                        <div style={styles.infoItem}>
                            <span style={styles.infoLabel}>Current Port</span>
                            <span style={styles.infoValue}>{settings?.port || '-'}</span>
                        </div>
                    </div>

                    <div style={styles.helpText}>
                        <strong>Note:</strong> Changes are applied immediately to the running server.
                        For permanent changes across restarts, set the <code>PRINTER_IP</code> and{' '}
                        <code>PRINTER_PORT</code> environment variables.
                    </div>
                </Card>
            </div>
        </div>
    );
};

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        padding: '20px',
        maxWidth: '1200px',
        margin: '0 auto',
    },
    title: {
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: '5px',
        color: 'var(--color-text-primary)',
    },
    subtitle: {
        color: 'var(--color-text-secondary)',
        fontSize: '14px',
    },
    loading: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '300px',
        gap: '16px',
        color: 'var(--color-text-secondary)',
    },
    grid: {
        display: 'flex',
        gap: '24px',
        flexWrap: 'wrap',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
    formGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
    },
    label: {
        fontSize: '14px',
        fontWeight: '500',
        color: 'var(--color-text-primary)',
    },
    input: {
        padding: '10px 12px',
        borderRadius: '6px',
        border: '1px solid var(--color-border)',
        fontSize: '14px',
        backgroundColor: 'var(--color-bg-secondary)',
        color: 'var(--color-text-primary)',
        outline: 'none',
        transition: 'border-color 0.2s',
    },
    hint: {
        fontSize: '12px',
        color: 'var(--color-text-tertiary)',
    },
    alert: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px 16px',
        borderRadius: '6px',
        border: '1px solid',
    },
    actions: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '10px',
        paddingTop: '20px',
        borderTop: '1px solid var(--color-border)',
    },
    infoSection: {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
    },
    printerIcon: {
        display: 'flex',
        justifyContent: 'center',
        padding: '20px',
        backgroundColor: 'var(--color-bg-secondary)',
        borderRadius: '12px',
        marginBottom: '10px',
    },
    infoItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 0',
        borderBottom: '1px solid var(--color-border)',
    },
    infoLabel: {
        fontSize: '13px',
        color: 'var(--color-text-secondary)',
    },
    infoValue: {
        fontSize: '14px',
        fontWeight: '500',
        color: 'var(--color-text-primary)',
    },
    helpText: {
        marginTop: '20px',
        padding: '12px',
        backgroundColor: 'var(--color-bg-secondary)',
        borderRadius: '6px',
        fontSize: '12px',
        color: 'var(--color-text-secondary)',
        lineHeight: '1.5',
    },
};

export default PrinterSettingsPage;
