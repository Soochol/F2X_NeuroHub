import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { DashboardPage } from '../DashboardPage';
import { dashboardApi } from '@/api';

// Mock the API
vi.mock('@/api', () => ({
    dashboardApi: {
        getSummary: vi.fn(),
    },
}));

// Mock child components
vi.mock('@/components/charts', () => ({
    ProcessFlowDiagram: () => <div data-testid="process-flow-diagram">Process Flow Diagram</div>,
}));

vi.mock('@/components/organisms/dashboard/LotHistoryTabs', () => ({
    LotHistoryTabs: () => <div data-testid="lot-history-tabs">Lot History Tabs</div>,
}));

describe('DashboardPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('shows loading state initially', () => {
        // Return a promise that never resolves immediately to test loading state
        (dashboardApi.getSummary as any).mockReturnValue(new Promise(() => { }));
        render(<DashboardPage />);
        expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
    });

    it('shows error state when API fails', async () => {
        (dashboardApi.getSummary as any).mockRejectedValue(new Error('API Error'));
        render(<DashboardPage />);

        await waitFor(() => {
            expect(screen.getByText(/Error:/)).toBeInTheDocument();
        });
    });

    it('renders dashboard summary data', async () => {
        const mockSummary = {
            total_started: 100,
            total_in_progress: 50,
            total_completed: 40,
            total_defective: 5,
            defect_rate: 12.5,
            process_wip: {},
            lots: [],
        };

        (dashboardApi.getSummary as any).mockResolvedValue(mockSummary);
        render(<DashboardPage />);

        await waitFor(() => {
            expect(screen.getByText('Production Dashboard')).toBeInTheDocument();
        });

        // Check KPI cards
        expect(screen.getByText('100')).toBeInTheDocument(); // Started
        expect(screen.getByText('50')).toBeInTheDocument();  // In Progress
        expect(screen.getByText('40')).toBeInTheDocument();  // Completed

        // Check calculated rates
        // Completion Rate: 40/100 = 40.0%
        expect(screen.getByText('(40.0%)')).toBeInTheDocument();

        // Defect Rate: 12.5%
        expect(screen.getByText('(12.5%)')).toBeInTheDocument();
    });

    it('renders child components', async () => {
        const mockSummary = {
            total_started: 0,
            total_in_progress: 0,
            total_completed: 0,
            total_defective: 0,
            defect_rate: 0,
            process_wip: {},
            lots: [],
        };

        (dashboardApi.getSummary as any).mockResolvedValue(mockSummary);
        render(<DashboardPage />);

        await waitFor(() => {
            expect(screen.getByTestId('process-flow-diagram')).toBeInTheDocument();
            expect(screen.getByTestId('lot-history-tabs')).toBeInTheDocument();
        });
    });
});
