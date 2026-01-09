/**
 * WIP Utility Functions
 * =====================
 *
 * Handles WIP ID validation and formatting.
 * Format: WIP-{LOT}-{SEQ} (e.g., WIP-KR01PSA2511-001)
 */

// WIP ID format regex: WIP-{LOT}-{SEQ} where LOT is 11-15 chars, SEQ is 3 digits
const WIP_ID_PATTERN = /^WIP-[A-Z0-9]{11,15}-\d{3}$/;

/**
 * Validate WIP ID format
 */
export const validateWipId = (wipId: string): boolean => {
    if (!wipId || typeof wipId !== 'string') {
        return false;
    }
    return WIP_ID_PATTERN.test(wipId);
};

/**
 * Parse WIP ID into components
 */
export const parseWipId = (wipId: string) => {
    if (!validateWipId(wipId)) {
        throw new Error(`Invalid WIP ID format: ${wipId}`);
    }

    // Extract LOT and sequence using regex groups
    const match = wipId.match(/^WIP-([A-Z0-9]+)-(\d{3})$/);
    if (!match) {
        throw new Error(`Failed to parse WIP ID: ${wipId}`);
    }

    const lotNumber = match[1]; // e.g., KR02PSA251101
    const sequence = match[2];  // e.g., 002

    return {
        lotNumber,
        sequence,
    };
};

/**
 * Get current process display text for WIP item
 * Handles all WIP status cases correctly
 *
 * @param wip - WIP item with status and current_process_id
 * @returns Human-readable process status text
 */
export const getWipProcessDisplayText = (wip: {
    status: string;
    current_process_id?: number;
}): string => {
    // Active process - show process number
    if (wip.current_process_id) {
        return `Process #${wip.current_process_id}`;
    }

    // No active process - check status
    switch (wip.status) {
        case 'CONVERTED':
            return 'Converted';

        case 'COMPLETED':
            return 'All Processes Completed, Awaiting Conversion';

        case 'FAILED':
            return 'Failed';

        case 'IN_PROGRESS':
            return 'Between Processes';

        case 'CREATED':
        default:
            return 'Not Started';
    }
};
