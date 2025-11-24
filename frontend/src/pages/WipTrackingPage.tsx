/**
 * WIP Tracking Page
 */

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { WipSearch } from '@/components/organisms/wip/WipSearch';
import { WipTraceView } from '@/components/organisms/wip/WipTraceView';
import { Card } from '@/components/common';
import { wipItemsApi } from '@/api';
import type { WipTrace } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { Search, XCircle } from 'lucide-react';

export const WipTrackingPage = () => {
    const [trace, setTrace] = useState<WipTrace | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const [searchParams] = useSearchParams();

    useEffect(() => {
        const wipId = searchParams.get('wip_id');
        if (wipId) {
            handleSearch(wipId);
        }
    }, [searchParams]);

    const handleSearch = async (wipId: string) => {
        setIsLoading(true);
        setError('');
        setTrace(null);

        try {
            const data = await wipItemsApi.getTrace(wipId);
            setTrace(data);
        } catch (err: unknown) {
            setError(getErrorMessage(err, `WIP ID "${wipId}" not found`));
        } finally {
            setIsLoading(false);
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
                        WIP Tracking & Traceability
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                        Track WIP status and view process history
                    </p>
                </div>

                <WipSearch onSearch={handleSearch} isLoading={isLoading} />
            </div>

            {/* Scrollable Content Section */}
            <div>
                {/* Loading State */}
                {isLoading && (
                    <Card>
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                            <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                <Search size={18} /> Searching...
                            </div>
                            <div style={{ fontSize: '14px' }}>Looking up WIP ID.</div>
                        </div>
                    </Card>
                )}

                {/* Error State */}
                {error && !isLoading && (
                    <Card>
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
                            <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                <XCircle size={18} /> {error}
                            </div>
                            <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                                Please verify the WIP ID and try again.
                            </div>
                        </div>
                    </Card>
                )}

                {/* Trace Results */}
                {trace && !isLoading && !error && (
                    <div>
                        <WipTraceView trace={trace} />
                    </div>
                )}

                {/* Empty State (Initial) */}
                {!trace && !isLoading && !error && (
                    <Card>
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                            <div style={{ marginBottom: '15px' }}>
                                <Search size={48} />
                            </div>
                            <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                                Enter a WIP ID to view process history
                            </div>
                            <div style={{ fontSize: '14px' }}>
                                View complete process history, measurement data, and defect codes for each WIP item.
                            </div>
                        </div>
                    </Card>
                )}
            </div>
        </div>
    );
};
