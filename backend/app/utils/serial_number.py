"""
Serial Number Format Utility
=============================

Serial number format (14 characters):
- Format: KR01PSA2511001
- Structure: [Country 2][Line 2][Model 3][Month 4][Sequence 3]
- Display: KR01-PSA-2511-001
- Example: KR01PSA2511001
  - KR: Country code (Korea)
  - 01: Production line number (Line 1)
  - PSA: Model code (PSA10 → PSA)
  - 2511: Production month (Nov 2025)
  - 001: Sequence number within LOT
"""

import re
from datetime import datetime
from typing import Dict


class SerialNumber:
    """Serial number format handler"""

    # Regex pattern: KR01PSA2511001 (14 chars)
    PATTERN = r'^[A-Z]{2}\d{2}[A-Z]{3}\d{4}\d{3}$'

    # Component lengths
    COUNTRY_LEN = 2
    LINE_LEN = 2
    MODEL_LEN = 3
    MONTH_LEN = 4
    SEQ_LEN = 3

    TOTAL_LEN = 14

    @staticmethod
    def validate(serial: str) -> bool:
        """
        Validate serial number format

        Args:
            serial: Serial number string (14 chars)

        Returns:
            True if valid format, False otherwise

        Example:
            >>> SerialNumber.validate("KR01PSA2511001")
            True
            >>> SerialNumber.validate("INVALID")
            False
        """
        if not serial or not isinstance(serial, str):
            return False
        return bool(re.match(SerialNumber.PATTERN, serial))

    @staticmethod
    def extract_lot_number(serial: str) -> str:
        """
        Extract LOT number from serial number

        Args:
            serial: Serial number string (14 chars)

        Returns:
            LOT number (first 11 characters)

        Raises:
            ValueError: If serial format is invalid

        Example:
            >>> SerialNumber.extract_lot_number("KR01PSA2511001")
            "KR01PSA2511"
        """
        if not SerialNumber.validate(serial):
            raise ValueError(
                f"Invalid serial format: {serial}. "
                f"Expected format: KR01PSA2511001 (14 characters)"
            )

        return serial[:11]  # First 11 chars are the LOT number

    @staticmethod
    def parse(serial: str) -> Dict[str, str]:
        """
        Parse serial number into components

        Args:
            serial: Serial number string (14 chars)

        Returns:
            Dictionary with components:
                - lot_number: LOT number (11 chars)
                - country_code: Country code (2 chars)
                - line_number: Production line (2 chars)
                - model_code: Model abbreviation (3 chars)
                - production_month: YYMM format (4 chars)
                - sequence: Sequence number (3 chars)

        Raises:
            ValueError: If serial format is invalid

        Example:
            >>> SerialNumber.parse("KR01PSA2511001")
            {
                "lot_number": "KR01PSA2511",
                "country_code": "KR",
                "line_number": "01",
                "model_code": "PSA",
                "production_month": "2511",
                "sequence": "001"
            }
        """
        if not SerialNumber.validate(serial):
            raise ValueError(
                f"Invalid serial format: {serial}. "
                f"Expected format: KR01PSA2511001 (14 characters)"
            )

        return {
            "lot_number": serial[0:11],  # First 11 chars are the LOT
            "country_code": serial[0:2],
            "line_number": serial[2:4],
            "model_code": serial[4:7],
            "production_month": serial[7:11],
            "sequence": serial[11:14]
        }

    @staticmethod
    def format_display(serial: str, separator: str = "-") -> str:
        """
        Format serial number for human-readable display

        Args:
            serial: Serial number string (14 chars)
            separator: Separator character (default: "-")

        Returns:
            Formatted string: KR01-PSA-2511-001

        Example:
            >>> SerialNumber.format_display("KR01PSA2511001")
            "KR01-PSA-2511-001"
            >>> SerialNumber.format_display("KR01PSA2511001", separator=" ")
            "KR01 PSA 2511 001"
        """
        if not SerialNumber.validate(serial):
            return serial  # Return as-is if invalid

        parts = [
            serial[0:4],   # KR01
            serial[4:7],   # PSA
            serial[7:11],  # 2511
            serial[11:14]  # 001
        ]

        return separator.join(parts)

    @staticmethod
    def parse_month(month_str: str) -> datetime:
        """
        Parse production month string to datetime

        Args:
            month_str: Month string in YYMM format (e.g., "2511")

        Returns:
            datetime object (first day of the month)

        Raises:
            ValueError: If month string is invalid

        Example:
            >>> SerialNumber.parse_month("2511")
            datetime(2025, 11, 1, 0, 0)
        """
        if not month_str or len(month_str) != 4:
            raise ValueError(f"Invalid month format: {month_str}. Expected YYMM (4 digits)")

        try:
            year = int("20" + month_str[0:2])
            month = int(month_str[2:4])

            if month < 1 or month > 12:
                raise ValueError(f"Invalid month value: {month}. Must be 01-12")

            return datetime(year, month, 1)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid month format: {month_str}") from e

    @staticmethod
    def format_month(dt: datetime) -> str:
        """
        Format datetime to production month string

        Args:
            dt: datetime object

        Returns:
            Month string in YYMM format (e.g., "2511")

        Example:
            >>> SerialNumber.format_month(datetime(2025, 11, 15))
            "2511"
        """
        return dt.strftime("%y%m")

    @staticmethod
    def generate(
        country_code: str,
        line_number: int,
        model_code: str,
        production_month: datetime,
        sequence: int
    ) -> str:
        """
        Generate serial number

        Args:
            country_code: 2-char country code (e.g., "KR")
            line_number: Line number integer (e.g., 1)
            model_code: 3-char model abbreviation (e.g., "PSA")
            production_month: Production month datetime
            sequence: Sequence number (1-999)

        Returns:
            Serial number (14 chars)

        Raises:
            ValueError: If generated serial is invalid

        Example:
            >>> SerialNumber.generate("KR", 1, "PSA", datetime(2025, 11, 1), 1)
            "KR01PSA2511001"
        """
        # Validate inputs
        if not country_code or len(country_code) != 2:
            raise ValueError(f"Invalid country_code: {country_code}. Must be 2 chars")

        if not model_code or len(model_code) != 3:
            raise ValueError(f"Invalid model_code: {model_code}. Must be 3 chars")

        if not isinstance(line_number, int) or line_number < 0 or line_number > 99:
            raise ValueError(f"Invalid line_number: {line_number}. Must be 0-99")

        if not isinstance(sequence, int) or sequence < 1 or sequence > 999:
            raise ValueError(f"Invalid sequence: {sequence}. Must be 1-999")

        # Build serial number
        line_part = f"{country_code.upper()}{line_number:02d}"
        model_part = model_code.upper()
        month_part = production_month.strftime("%y%m")
        seq_part = f"{sequence:03d}"

        serial = f"{line_part}{model_part}{month_part}{seq_part}"

        # Validate generated serial
        if not SerialNumber.validate(serial):
            raise ValueError(f"Generated invalid serial: {serial}")

        return serial

    @staticmethod
    def get_full_info(serial: str) -> Dict[str, any]:
        """
        Get complete information about serial number

        Args:
            serial: Serial number string

        Returns:
            Dictionary with full parsed information including datetime

        Example:
            >>> SerialNumber.get_full_info("KR01PSA2511001")
            {
                "serial_number": "KR01PSA2511001",
                "formatted": "KR01-PSA-2511-001",
                "valid": True,
                "components": {
                    "lot_number": "KR01PSA2511",
                    "country_code": "KR",
                    "line_number": "01",
                    "model_code": "PSA",
                    "production_month": "2511",
                    "sequence": "001"
                },
                "production_date": datetime(2025, 11, 1)
            }
        """
        is_valid = SerialNumber.validate(serial)

        if not is_valid:
            return {
                "serial_number": serial,
                "formatted": serial,
                "valid": False,
                "error": "Invalid serial number format"
            }

        components = SerialNumber.parse(serial)
        production_date = SerialNumber.parse_month(components["production_month"])

        return {
            "serial_number": serial,
            "formatted": SerialNumber.format_display(serial),
            "valid": True,
            "components": components,
            "production_date": production_date
        }
