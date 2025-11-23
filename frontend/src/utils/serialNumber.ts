/**
 * Serial Number Utility Functions
 * =================================
 *
 * Handles both V0 (legacy) and V1 (new standard) serial number formats:
 * - V1 (New Standard): KR01PSA251101001 (16 chars, no hyphens)
 * - V0 (Legacy): WF-KR-251119D-003-0038 (22-24 chars with hyphens)
 */

export interface SerialNumberV1Components {
  countryCode: string;
  lineNumber: string;
  modelCode: string;
  productionMonth: string;
  lotSequence: string;
  sequence: string;
}

export interface SerialNumberV0Components {
  modelCode: string;
  countryCode: string;
  productionDate: string;
  shift: string;
  lotSequence: string;
  serialSequence: string;
}

// V1 format regex: KR01PSA251101001 (16 chars)
const SERIAL_NUMBER_V1_PATTERN = /^[A-Z]{2}\d{2}[A-Z]{3}\d{4}\d{2}\d{3}$/;

// V0 format regex: WF-KR-251119D-003-0038
const SERIAL_NUMBER_V0_PATTERN = /^[A-Z]{2,}-[A-Z]{2}-\d{6}[DN]-\d{3}-\d{4}$/;

/**
 * Validate V1 serial number format (new standard)
 */
export const validateSerialNumberV1 = (serial: string): boolean => {
  if (!serial || typeof serial !== 'string') {
    return false;
  }
  return SERIAL_NUMBER_V1_PATTERN.test(serial);
};

/**
 * Validate V0 serial number format (legacy)
 */
export const validateSerialNumberV0 = (serial: string): boolean => {
  if (!serial || typeof serial !== 'string') {
    return false;
  }
  return SERIAL_NUMBER_V0_PATTERN.test(serial);
};

/**
 * Auto-detect serial number version
 *
 * @param serial Serial number string
 * @returns 1 for V1, 0 for V0, null if invalid
 */
export const detectSerialVersion = (serial: string): 0 | 1 | null => {
  if (validateSerialNumberV1(serial)) {
    return 1;
  }
  if (validateSerialNumberV0(serial)) {
    return 0;
  }
  return null;
};

/**
 * Parse V1 format serial number into components (new standard)
 *
 * @param serial Serial number (16 chars): KR01PSA251101001
 * @returns Parsed components or throws error if invalid
 *
 * @example
 * parseSerialNumberV1("KR01PSA251101001")
 * // => {
 * //   countryCode: "KR",
 * //   lineNumber: "01",
 * //   modelCode: "PSA",
 * //   productionMonth: "2511",
 * //   lotSequence: "01",
 * //   sequence: "001"
 * // }
 */
export const parseSerialNumberV1 = (serial: string): SerialNumberV1Components => {
  if (!validateSerialNumberV1(serial)) {
    throw new Error(
      `Invalid V1 serial number format: ${serial}. Expected format: KR01PSA251101001 (16 characters)`
    );
  }

  return {
    countryCode: serial.slice(0, 2),
    lineNumber: serial.slice(2, 4),
    modelCode: serial.slice(4, 7),
    productionMonth: serial.slice(7, 11),
    lotSequence: serial.slice(11, 13),
    sequence: serial.slice(13, 16),
  };
};

/**
 * Parse V0 format serial number into components (legacy)
 *
 * @param serial Serial number: WF-KR-251119D-003-0038
 * @returns Parsed components or throws error if invalid
 */
export const parseSerialNumberV0 = (serial: string): SerialNumberV0Components => {
  if (!validateSerialNumberV0(serial)) {
    throw new Error(
      `Invalid V0 serial number format: ${serial}. Expected format: WF-KR-251119D-003-0038`
    );
  }

  const parts = serial.split('-');
  return {
    modelCode: parts[0],
    countryCode: parts[1],
    productionDate: parts[2].slice(0, 6),
    shift: parts[2].slice(6),
    lotSequence: parts[3],
    serialSequence: parts[4],
  };
};

/**
 * Format V1 serial number for display (add hyphens)
 *
 * @param serial Serial number (16 chars): KR01PSA251101001
 * @param separator Separator character (default: "-")
 * @returns Formatted string: KR01-PSA-2511-01-001
 *
 * @example
 * formatSerialNumberV1("KR01PSA251101001")
 * // => "KR01-PSA-2511-01-001"
 *
 * formatSerialNumberV1("KR01PSA251101001", " ")
 * // => "KR01 PSA 2511 01 001"
 */
export const formatSerialNumberV1 = (serial: string, separator: string = '-'): string => {
  if (!validateSerialNumberV1(serial)) {
    return serial; // Return as-is if invalid
  }

  const parts = [
    serial.slice(0, 4),   // KR01
    serial.slice(4, 7),   // PSA
    serial.slice(7, 11),  // 2511
    serial.slice(11, 13), // 01 (LOT sequence)
    serial.slice(13, 16), // 001 (Serial sequence)
  ];

  return parts.join(separator);
};

/**
 * Format serial number (auto-detects version)
 *
 * @param serial Serial number (any format)
 * @param separator Separator for V1 format (default: "-")
 * @returns Formatted serial number
 *
 * @example
 * formatSerialNumber("KR01PSA251101001")
 * // => "KR01-PSA-2511-01-001"
 *
 * formatSerialNumber("WF-KR-251119D-003-0038")
 * // => "WF-KR-251119D-003-0038" (unchanged)
 */
export const formatSerialNumber = (serial: string, separator: string = '-'): string => {
  const version = detectSerialVersion(serial);

  if (version === 1) {
    return formatSerialNumberV1(serial, separator);
  }

  // V0 or invalid - return as-is
  return serial;
};

/**
 * Parse production month from V1 format (YYMM)
 *
 * @param monthStr Month string: "2511" (Nov 2025)
 * @returns Date object (first day of the month)
 *
 * @example
 * parseProductionMonth("2511")
 * // => Date(2025, 10, 1) // November 1, 2025 (month is 0-indexed)
 */
export const parseProductionMonth = (monthStr: string): Date => {
  if (monthStr.length !== 4) {
    throw new Error(`Invalid month format: ${monthStr}. Expected YYMM (4 digits)`);
  }

  const year = 2000 + parseInt(monthStr.slice(0, 2), 10);
  const month = parseInt(monthStr.slice(2, 4), 10);

  if (month < 1 || month > 12) {
    throw new Error(`Invalid month value: ${month}. Must be 01-12`);
  }

  // Note: JavaScript Date month is 0-indexed (0 = January, 11 = December)
  return new Date(year, month - 1, 1);
};

/**
 * Validate serial number (any version)
 *
 * @param serial Serial number string
 * @returns true if valid V0 or V1 format
 */
export const validateSerialNumber = (serial: string): boolean => {
  return validateSerialNumberV1(serial) || validateSerialNumberV0(serial);
};

/**
 * Get detailed serial number information
 *
 * @param serial Serial number string
 * @returns Object with parsed data and metadata
 */
export const getSerialInfo = (serial: string) => {
  const version = detectSerialVersion(serial);

  if (version === null) {
    return {
      serial,
      valid: false,
      version: null,
      formatted: serial,
      error: 'Invalid serial number format',
    };
  }

  if (version === 1) {
    const components = parseSerialNumberV1(serial);
    const productionDate = parseProductionMonth(components.productionMonth);

    return {
      serial,
      valid: true,
      version: 1,
      formatted: formatSerialNumberV1(serial),
      components,
      productionDate: productionDate.toISOString(),
    };
  } else {
    const components = parseSerialNumberV0(serial);

    return {
      serial,
      valid: true,
      version: 0,
      formatted: serial, // V0 already has hyphens
      components,
    };
  }
};

// Export all validation patterns for use in form validation
export const PATTERNS = {
  V0: SERIAL_NUMBER_V0_PATTERN,
  V1: SERIAL_NUMBER_V1_PATTERN,
} as const;
