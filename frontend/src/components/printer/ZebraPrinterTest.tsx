/**
 * Zebra Printer Test Component
 * Test Zebra Browser Print functionality
 */

import { useState } from 'react';
import { Card, Button } from '@/components/common';
import {
    isBrowserPrintAvailable,
    getDefaultPrinter,
    printTestLabel,
    printWIPLabel,
    printSerialLabel
} from '@/utils/zebraPrint';
import { CheckCircle, XCircle, Printer, AlertCircle } from 'lucide-react';

export const ZebraPrinterTest = () => {
    const [status, setStatus] = useState<'idle' | 'checking' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');
    const [printerName, setPrinterName] = useState('');

    const checkBrowserPrint = async () => {
        setStatus('checking');
        setMessage('Checking Zebra Browser Print...');

        try {
            if (!isBrowserPrintAvailable()) {
                throw new Error('Zebra Browser Print is not installed');
            }

            const printer = await getDefaultPrinter();
            setPrinterName(printer.name);
            setMessage(`Connected to: ${printer.name}`);
            setStatus('success');
        } catch (error: unknown) {
            setMessage(error instanceof Error ? error.message : 'Unknown error');
            setStatus('error');
        }
    };

    const handlePrintTest = async () => {
        setStatus('checking');
        setMessage('Printing test label...');

        try {
            await printTestLabel();
            setMessage('Test label sent to printer!');
            setStatus('success');
        } catch (error: unknown) {
            setMessage(`Print failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setStatus('error');
        }
    };

    const handlePrintWIP = async () => {
        setStatus('checking');
        setMessage('Printing WIP label...');

        try {
            await printWIPLabel('WIP-KR01PSA2511-001');
            setMessage('WIP label sent to printer!');
            setStatus('success');
        } catch (error: unknown) {
            setMessage(`Print failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setStatus('error');
        }
    };

    const handlePrintSerial = async () => {
        setStatus('checking');
        setMessage('Printing Serial label...');

        try {
            await printSerialLabel(
                'SN-KR01PSA2511-001-001',
                'LOT-2024-001',
                'PSA-2511'
            );
            setMessage('Serial label sent to printer!');
            setStatus('success');
        } catch (error: unknown) {
            setMessage(`Print failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setStatus('error');
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'success':
                return <CheckCircle size={24} style={{ color: 'var(--color-success)' }} />;
            case 'error':
                return <XCircle size={24} style={{ color: 'var(--color-error)' }} />;
            case 'checking':
                return <div className="spinner" style={{ width: '24px', height: '24px' }} />;
            default:
                return <Printer size={24} style={{ color: 'var(--color-text-secondary)' }} />;
        }
    };

    return (
        <Card title="Zebra Printer Test">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Status Display */}
                <div
                    style={{
                        padding: '20px',
                        backgroundColor: 'var(--color-bg-tertiary)',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '15px',
                    }}
                >
                    {getStatusIcon()}
                    <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
                            {status === 'idle' && 'Ready to test'}
                            {status === 'checking' && 'Processing...'}
                            {status === 'success' && 'Success!'}
                            {status === 'error' && 'Error'}
                        </div>
                        {message && (
                            <div
                                style={{
                                    fontSize: '13px',
                                    color: status === 'error' ? 'var(--color-error)' : 'var(--color-text-secondary)',
                                }}
                            >
                                {message}
                            </div>
                        )}
                        {printerName && status === 'success' && (
                            <div
                                style={{
                                    fontSize: '12px',
                                    color: 'var(--color-text-secondary)',
                                    marginTop: '4px',
                                    fontFamily: 'monospace',
                                }}
                            >
                                Printer: {printerName}
                            </div>
                        )}
                    </div>
                </div>

                {/* Installation Notice */}
                {!isBrowserPrintAvailable() && (
                    <div
                        style={{
                            padding: '15px',
                            backgroundColor: 'var(--color-warning-bg)',
                            borderLeft: '4px solid var(--color-warning)',
                            borderRadius: '4px',
                            display: 'flex',
                            gap: '10px',
                        }}
                    >
                        <AlertCircle size={20} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
                        <div style={{ fontSize: '13px' }}>
                            <strong>Zebra Browser Print not detected.</strong>
                            <br />
                            Please install it from:{' '}
                            <a
                                href="https://www.zebra.com/browserprint"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: 'var(--color-brand)', textDecoration: 'underline' }}
                            >
                                zebra.com/browserprint
                            </a>
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                    <Button onClick={checkBrowserPrint} variant="secondary" disabled={status === 'checking'}>
                        Check Connection
                    </Button>
                    <Button onClick={handlePrintTest} disabled={status === 'checking'}>
                        Print Test Label
                    </Button>
                    <Button onClick={handlePrintWIP} variant="secondary" disabled={status === 'checking'}>
                        Print WIP Sample
                    </Button>
                    <Button onClick={handlePrintSerial} variant="secondary" disabled={status === 'checking'}>
                        Print Serial Sample
                    </Button>
                </div>

                {/* Instructions */}
                <div
                    style={{
                        padding: '15px',
                        backgroundColor: 'var(--color-bg-tertiary)',
                        borderRadius: '6px',
                        fontSize: '13px',
                        color: 'var(--color-text-secondary)',
                    }}
                >
                    <strong>Instructions:</strong>
                    <ol style={{ marginTop: '8px', marginLeft: '20px' }}>
                        <li>Ensure Zebra Browser Print is installed and running</li>
                        <li>Connect your Zebra printer (ZT231-203dpi at 192.168.35.79)</li>
                        <li>Click "Check Connection" to verify</li>
                        <li>Test printing with sample labels</li>
                    </ol>
                </div>
            </div>
        </Card>
    );
};
