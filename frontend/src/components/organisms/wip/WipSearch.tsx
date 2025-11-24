/**
 * WIP Search Component
 */

import { useState, type FormEvent, useRef, useEffect } from 'react';
import { Button } from '../../atoms';
import { Card } from '../../molecules';
import { QrCode, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { validateWipId } from '@/utils/wip';

interface WipSearchProps {
    onSearch: (wipId: string) => void;
    isLoading?: boolean;
}

export const WipSearch = ({ onSearch, isLoading }: WipSearchProps) => {
    const [wipId, setWipId] = useState('');
    const [error, setError] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (!wipId.trim()) {
            setError('Please enter a WIP ID');
            return;
        }
        setError('');
        onSearch(wipId.trim());
    };

    const isValid = wipId.trim() ? validateWipId(wipId) : null;

    return (
        <Card>
            <form onSubmit={handleSubmit}>
                <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
                    <div style={{ flex: 1 }}>
                        <label
                            htmlFor="wipId"
                            style={{
                                display: 'block',
                                marginBottom: '8px',
                                fontSize: '14px',
                                fontWeight: '500',
                                color: 'var(--color-text-primary)'
                            }}
                        >
                            Search WIP ID
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
                                id="wipId"
                                type="text"
                                value={wipId}
                                onChange={(e) => {
                                    setWipId(e.target.value);
                                    setError('');
                                }}
                                placeholder="e.g., WIP-KR01PSA2511-001"
                                disabled={isLoading}
                                style={{
                                    width: '100%',
                                    padding: '12px 12px 12px 40px',
                                    border: error ? '1px solid var(--color-error)' : '1px solid var(--color-border)',
                                    borderRadius: '6px',
                                    fontSize: '15px',
                                    backgroundColor: 'var(--color-bg-primary)',
                                    color: 'var(--color-text-primary)',
                                }}
                            />
                        </div>
                        {/* Absolute positioned container to prevent layout shift */}
                        <div style={{ position: 'relative' }}>
                            {(isValid !== null || error) && (
                                <div style={{
                                    position: 'absolute',
                                    top: '6px',
                                    left: 0,
                                    right: 0,
                                    fontSize: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    color: error ? 'var(--color-error)' : (isValid ? 'var(--color-success)' : 'var(--color-error)')
                                }}>
                                    {error ? (
                                        <>
                                            <AlertCircle size={14} />
                                            {error}
                                        </>
                                    ) : isValid ? (
                                        <>
                                            <CheckCircle2 size={14} />
                                            <span>Valid WIP ID format</span>
                                        </>
                                    ) : (
                                        <>
                                            <XCircle size={14} />
                                            <span>Invalid WIP ID format</span>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                    <Button
                        type="submit"
                        disabled={isLoading || !wipId.trim()}
                        style={{ minWidth: '100px' }}
                    >
                        {isLoading ? 'Searching...' : 'Search'}
                    </Button>
                </div>
            </form>
        </Card>
    );
};
