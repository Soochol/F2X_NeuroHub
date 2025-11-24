/**
 * WIP List by LOT Page
 * Search for a LOT by number and list all associated WIP items
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/common';
import { Search, Package, ArrowRight, AlertCircle, QrCode, Calendar, CheckCircle, XCircle, Clock } from 'lucide-react';
import { lotsApi, wipItemsApi } from '@/api';
import type { Lot, WIPItem } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { format } from 'date-fns';

export const WipByLotPage = () => {
    const navigate = useNavigate();
    const [lotNumber, setLotNumber] = useState('');
    const [lot, setLot] = useState<Lot | null>(null);
    const [wipItems, setWipItems] = useState<WIPItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSearch = async () => {
        if (!lotNumber.trim()) return;

        setIsLoading(true);
        setError('');
        setLot(null);
        setWipItems([]);

        try {
            // Parse LOT number from input (supports both LOT number and WIP ID)
            // WIP ID format: WIP-{LOT}-{SEQ} (e.g., WIP-DT01A10251101-001)
            let parsedLotNumber = lotNumber.trim();

            if (parsedLotNumber.startsWith('WIP-')) {
                // Extract LOT number from WIP ID
                // Remove "WIP-" prefix and the last "-XXX" sequence
                const parts = parsedLotNumber.substring(4).split('-');
                if (parts.length >= 2) {
                    // Join all parts except the last one (which is the sequence number)
                    parsedLotNumber = parts.slice(0, -1).join('-');
                }
            }

            // 1. Get LOT by number
            const lotData = await lotsApi.getLotByNumber(parsedLotNumber);
            setLot(lotData);

            // 2. Get WIP items for this LOT
            const wips = await wipItemsApi.getWIPItems({ lot_id: lotData.id });
            setWipItems(wips);
        } catch (err: unknown) {
            setError(getErrorMessage(err, `LOT "${lotNumber}" not found`));
        } finally {
            setIsLoading(false);
        }
    };

    const handleWipClick = (wipId: string) => {
        navigate(`/wip/tracking?wip_id=${wipId}`);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 'var(--color-success)';
            case 'FAILED': return 'var(--color-error)';
            case 'IN_PROGRESS': return 'var(--color-info)';
            case 'CREATED': return 'var(--color-warning)';
            default: return 'var(--color-text-secondary)';
        }
    };

    const getStatusBgColor = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 'var(--color-bg-success)';
            case 'FAILED': return 'var(--color-bg-error)';
            case 'IN_PROGRESS': return 'var(--color-bg-info)';
            case 'CREATED': return 'var(--color-warning-bg)';
            default: return 'var(--color-bg-secondary)';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'COMPLETED': return <CheckCircle size={14} />;
            case 'FAILED': return <XCircle size={14} />;
            case 'IN_PROGRESS': return <Clock size={14} />;
            default: return <Package size={14} />;
        }
    };

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100%'
        }}>
            {/* Fixed Header Section - Title and Search */}
            <div style={{
                flexShrink: 0,
                marginBottom: '20px',
                backgroundColor: 'var(--color-bg-secondary)',
                position: 'sticky',
                top: '-20px',
                zIndex: 10,
                paddingTop: '20px',
                paddingBottom: '20px',
                marginTop: '-20px',
                paddingLeft: '20px',
                paddingRight: '20px',
                marginLeft: '-20px',
                marginRight: '-20px',
                borderBottom: '2px solid var(--color-border)'
            }}>
                <div style={{ marginBottom: '20px' }}>
                    <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: 'var(--color-text-primary)' }}>
                        WIP List by LOT
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                        Search for a LOT to view all associated WIP items and their status
                    </p>
                </div>

                {/* Search Filter */}
                <Card>
                    <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
                        <div style={{ flex: 1 }}>
                            <label
                                htmlFor="lotNumber"
                                style={{
                                    display: 'block',
                                    marginBottom: '8px',
                                    fontSize: '14px',
                                    fontWeight: '500',
                                    color: 'var(--color-text-primary)'
                                }}
                            >
                                LOT Number or WIP ID
                            </label>
                            <div style={{ position: 'relative' }}>
                                <QrCode
                                    size={18}
                                    style={{
                                        position: 'absolute',
                                        left: '12px',
                                        top: '50%',
                                        transform: 'translateY(-50%)',
                                        color: 'var(--color-text-secondary)'
                                    }}
                                />
                                <input
                                    ref={inputRef}
                                    id="lotNumber"
                                    type="text"
                                    placeholder="Enter LOT Number or WIP ID (e.g., DT01A10251101 or WIP-DT01A10251101-001)"
                                    value={lotNumber}
                                    onChange={(e) => setLotNumber(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                    style={{
                                        width: '100%',
                                        padding: '12px 12px 12px 40px',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '6px',
                                        fontSize: '15px',
                                        backgroundColor: 'var(--color-bg-primary)',
                                        color: 'var(--color-text-primary)',
                                    }}
                                />
                            </div>
                        </div>
                        <Button
                            onClick={handleSearch}
                            disabled={!lotNumber.trim() || isLoading}
                            style={{ minWidth: '100px' }}
                        >
                            {isLoading ? 'Searching...' : 'Search'}
                        </Button>
                    </div>

                    {error && (
                        <div style={{
                            marginTop: '15px',
                            padding: '12px',
                            backgroundColor: 'var(--color-bg-error)',
                            color: 'var(--color-error)',
                            borderRadius: '6px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            fontSize: '14px'
                        }}>
                            <AlertCircle size={18} />
                            {error}
                        </div>
                    )}
                </Card>
            </div>

            {/* Scrollable Content Section */}
            <div>
                {lot && (
                    <div style={{ animation: 'fadeIn 0.3s ease-in-out' }}>
                        {/* LOT Info Header */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '20px',
                            padding: '0 5px'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <h2 style={{ fontSize: '18px', fontWeight: '600', margin: 0, color: 'var(--color-text-primary)' }}>
                                    Items in LOT: <span style={{ fontFamily: 'monospace', color: 'var(--color-brand)', fontSize: '20px' }}>{lot.lot_number}</span>
                                </h2>
                                {lot.product_model && (
                                    <span style={{
                                        padding: '4px 10px',
                                        backgroundColor: 'var(--color-bg-secondary)',
                                        borderRadius: '12px',
                                        fontSize: '13px',
                                        color: 'var(--color-text-secondary)',
                                        border: '1px solid var(--color-border)'
                                    }}>
                                        {lot.product_model.model_code}
                                    </span>
                                )}
                            </div>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                color: 'var(--color-text-secondary)',
                                fontSize: '14px',
                                backgroundColor: 'var(--color-bg-secondary)',
                                padding: '6px 12px',
                                borderRadius: '6px'
                            }}>
                                <Package size={16} />
                                <span>Total Items: <strong>{wipItems.length}</strong></span>
                            </div>
                        </div>

                        {wipItems.length === 0 ? (
                            <Card>
                                <div style={{ textAlign: 'center', padding: '60px', color: 'var(--color-text-secondary)' }}>
                                    <Package size={48} style={{ marginBottom: '15px', opacity: 0.5 }} />
                                    <div style={{ fontSize: '16px' }}>No WIP items found for this LOT.</div>
                                </div>
                            </Card>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                {wipItems.map((wip) => (
                                    <div
                                        key={wip.id}
                                        onClick={() => handleWipClick(wip.wip_id)}
                                        style={{
                                            backgroundColor: 'var(--color-bg-container)',
                                            border: '1px solid var(--color-border)',
                                            borderRadius: '8px',
                                            padding: '20px',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s',
                                            position: 'relative',
                                            boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.transform = 'translateY(-2px)';
                                            e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
                                            e.currentTarget.style.borderColor = 'var(--color-brand)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                                            e.currentTarget.style.borderColor = 'var(--color-border)';
                                        }}
                                    >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
                                            <div style={{ fontWeight: 'bold', fontSize: '16px', color: 'var(--color-text-primary)', fontFamily: 'monospace' }}>
                                                {wip.wip_id}
                                            </div>
                                            <div style={{
                                                fontSize: '12px',
                                                padding: '4px 10px',
                                                borderRadius: '12px',
                                                backgroundColor: getStatusBgColor(wip.status),
                                                color: getStatusColor(wip.status),
                                                fontWeight: '600',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '4px'
                                            }}>
                                                {getStatusIcon(wip.status)}
                                                {wip.status}
                                            </div>
                                        </div>

                                        <div style={{ marginBottom: '15px' }}>
                                            <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                                                Current Process
                                            </div>
                                            <div style={{ fontSize: '15px', fontWeight: '500', color: 'var(--color-text-primary)' }}>
                                                {wip.current_process_id ? `Process #${wip.current_process_id}` : 'Not Started'}
                                            </div>
                                        </div>

                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            paddingTop: '15px',
                                            borderTop: '1px solid var(--color-border)'
                                        }}>
                                            <div style={{ fontSize: '12px', color: 'var(--color-text-tertiary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                <Calendar size={12} />
                                                {format(new Date(wip.created_at), 'yyyy-MM-dd')}
                                            </div>
                                            <div style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                color: 'var(--color-brand)',
                                                fontSize: '13px',
                                                fontWeight: '500'
                                            }}>
                                                View Trace <ArrowRight size={14} style={{ marginLeft: '4px' }} />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
