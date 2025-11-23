/**
 * WIP Generation Page
 * Generate WIP IDs for CREATED status LOTs
 */

import { useState, useEffect } from 'react';
import { Card, Button, Modal } from '@/components/common';
import { lotsApi } from '@/api';
import { LotStatus, type Lot, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';
import { Calendar, TrendingUp, CheckCircle, Layers, QrCode } from 'lucide-react';
import { notify } from '@/utils/toast';

export const WipGenerationPage = () => {
    const [lots, setLots] = useState<Lot[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedLot, setSelectedLot] = useState<Lot | null>(null);
    const [searchQuery, setSearchQuery] = useState('');

    // Generation state
    const [isGenerating, setIsGenerating] = useState(false);
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [generatedCount, setGeneratedCount] = useState(0);
    const [generatedTotal, setGeneratedTotal] = useState(0);

    const [lastGeneratedWipIds, setLastGeneratedWipIds] = useState<any[]>([]);

    useEffect(() => {
        fetchCreatedLots();
    }, []);

    const fetchCreatedLots = async () => {
        setIsLoading(true);
        setError('');
        try {
            const response = await lotsApi.getActiveLots();
            setLots(response);
        } catch (err: unknown) {
            setError(getErrorMessage(err, 'Failed to load active LOTs'));
        } finally {
            setIsLoading(false);
        }
    };

    const handleGenerateWip = async (quantity: number) => {
        if (!selectedLot) return;

        setIsGenerating(true);
        setError('');

        try {
            const result = await lotsApi.startWipGeneration(selectedLot.id, quantity);
            setLastGeneratedWipIds(result);

            // Refresh the LOT list
            await fetchCreatedLots();

            // Get updated LOT info to show total WIP count
            const updatedLot = await lotsApi.getLot(selectedLot.id);

            setGeneratedCount(updatedLot.wip_count || 0);
            setGeneratedTotal(selectedLot.target_quantity);
            setShowSuccessModal(true);
            setSelectedLot(null);

            notify.success({
                title: 'WIP Generation Successful',
                description: `Generated ${result.length} WIP items`
            });
        } catch (err: unknown) {
            const errorMsg = getErrorMessage(err, 'Failed to generate WIP items');
            setError(errorMsg);
            notify.error({
                title: 'Generation Failed',
                description: errorMsg
            });
        } finally {
            setIsGenerating(false);
        }
    };

    const filteredLots = lots.filter((lot) => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            lot.lot_number.toLowerCase().includes(query) ||
            (lot.product_model?.model_name && lot.product_model.model_name.toLowerCase().includes(query)) ||
            (lot.product_model?.model_code && lot.product_model.model_code.toLowerCase().includes(query))
        );
    });

    return (
        <div>
            <div style={{ marginBottom: '20px' }}>
                <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: 'var(--color-text-primary)' }}>
                    WIP Generation
                </h1>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                    Generate WIP IDs for LOTs with CREATED or IN_PROGRESS status
                </p>
            </div>

            {/* Search Filter */}
            <Card style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
                    <div style={{ flex: 1 }}>
                        <label
                            htmlFor="searchQuery"
                            style={{
                                display: 'block',
                                marginBottom: '8px',
                                fontSize: '14px',
                                fontWeight: '500',
                                color: 'var(--color-text-primary)'
                            }}
                        >
                            Search LOT
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
                                id="searchQuery"
                                type="text"
                                placeholder="Search LOT number or product model..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
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
                    <Button variant="secondary" onClick={fetchCreatedLots}>
                        Refresh
                    </Button>
                </div>
            </Card>

            {/* LOT List */}
            <Card>
                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                        Loading LOTs...
                    </div>
                ) : error ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
                        {error}
                    </div>
                ) : filteredLots.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                        No active LOTs found.
                    </div>
                ) : (
                    <div style={{ display: 'grid', gap: '15px' }}>
                        {filteredLots.map((lot) => (
                            <div
                                key={lot.id}
                                onClick={() => setSelectedLot(lot)}
                                style={{
                                    padding: '20px',
                                    border: selectedLot?.id === lot.id
                                        ? '2px solid var(--color-brand)'
                                        : '1px solid var(--color-border)',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                    backgroundColor: selectedLot?.id === lot.id
                                        ? 'var(--color-bg-tertiary)'
                                        : 'var(--color-bg-secondary)',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                            <span style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
                                                {lot.lot_number}
                                            </span>
                                            <span
                                                style={{
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    backgroundColor: 'var(--color-warning-bg)',
                                                    color: 'var(--color-warning)',
                                                }}
                                            >
                                                {lot.status}
                                            </span>
                                        </div>
                                        {lot.product_model && (
                                            <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                                                <strong>{lot.product_model.model_code}</strong> - {lot.product_model.model_name}
                                            </div>
                                        )}
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{
                                            fontSize: '16px',
                                            fontWeight: 'bold',
                                            color: 'var(--color-brand)',
                                            marginBottom: '4px'
                                        }}>
                                            {lot.target_quantity} Units
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                                            Target
                                        </div>
                                    </div>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginTop: '12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                                        <Calendar size={14} />
                                        {format(new Date(lot.production_date), 'yyyy-MM-dd')}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </Card>

            {/* Confirmation Modal */}
            <Modal
                isOpen={!!selectedLot && !isGenerating && !showSuccessModal}
                onClose={() => setSelectedLot(null)}
                title="WIP Generation"
                width="550px"
            >
                {selectedLot && (
                    <div>
                        {/* LOT Info */}
                        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'var(--color-bg-secondary)', borderRadius: '8px' }}>
                            <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px', fontFamily: 'monospace', color: 'var(--color-brand)' }}>
                                {selectedLot.lot_number}
                            </div>
                            {selectedLot.product_model && (
                                <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                                    {selectedLot.product_model.model_code} - {selectedLot.product_model.model_name}
                                </div>
                            )}
                        </div>

                        {/* Action Buttons */}
                        <div style={{ display: 'flex', gap: '12px', flexDirection: 'column' }}>
                            <Button
                                onClick={() => handleGenerateWip(1)}
                                size="lg"
                                style={{
                                    width: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px',
                                }}
                            >
                                <Layers size={18} />
                                Generate Single WIP Item
                            </Button>

                            <Button
                                onClick={() => handleGenerateWip(selectedLot.target_quantity)}
                                variant="secondary"
                                size="lg"
                                disabled={true}
                                style={{
                                    width: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px',
                                }}
                            >
                                <TrendingUp size={18} />
                                Generate All ({selectedLot.target_quantity} items)
                            </Button>

                            <Button
                                onClick={() => setSelectedLot(null)}
                                variant="ghost"
                                size="lg"
                                style={{ width: '100%' }}
                            >
                                Cancel
                            </Button>
                        </div>
                    </div>
                )}
            </Modal>

            {/* Progress Modal */}
            <Modal
                isOpen={isGenerating}
                onClose={() => { }}
                title="Generating WIP Items..."
                width="500px"
            >
                <div>
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
                        <div style={{ fontSize: '16px', color: 'var(--color-text-primary)' }}>
                            Processing request...
                        </div>
                    </div>
                </div>
            </Modal>

            {/* Success Modal */}
            <Modal
                isOpen={showSuccessModal}
                onClose={() => setShowSuccessModal(false)}
                title="WIP Generation Complete"
                width="600px"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setShowSuccessModal(false)}>
                            Close
                        </Button>
                    </>
                }
            >
                <div>
                    <div
                        style={{
                            textAlign: 'center',
                            padding: '30px',
                            backgroundColor: 'var(--color-success-bg)',
                            borderRadius: '12px',
                            marginBottom: '20px',
                        }}
                    >
                        <CheckCircle size={64} style={{ color: 'var(--color-success)', marginBottom: '15px' }} />
                        {lastGeneratedWipIds.length === 1 ? (
                            <>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: 'var(--color-text-primary)', fontFamily: 'monospace' }}>
                                    {(lastGeneratedWipIds[0] as any).wip_id}
                                </div>
                                <div style={{ fontSize: '16px', color: 'var(--color-text-secondary)' }}>
                                    generated successfully
                                </div>
                            </>
                        ) : (
                            <>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: 'var(--color-text-primary)' }}>
                                    {generatedCount} / {generatedTotal}
                                </div>
                                <div style={{ fontSize: '16px', color: 'var(--color-text-secondary)' }}>
                                    generated
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </Modal>
        </div>
    );
};
