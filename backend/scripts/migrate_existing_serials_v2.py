"""
Optional Migration Script: Convert Existing V1 Serials to V2 Format
====================================================================

WARNING: This script is OPTIONAL and DESTRUCTIVE!

This script converts existing V1 format serial numbers to V2 format.
Only use this if you want to standardize all historical data to V2 format.

V1 Format: PSA10-KR001-251110D-001-0001 (24 chars)
V2 Format: KR01PSA2511001 (14 chars)

IMPORTANT NOTES:
1. Serial numbers are permanent identifiers - changing them affects traceability
2. External systems may reference old serial numbers
3. Printed labels will show old format
4. This operation cannot be easily reversed

RECOMMENDED: Keep V1 serials as-is and only generate new serials in V2 format.

Usage:
    python backend/scripts/migrate_existing_serials_v2.py --dry-run
    python backend/scripts/migrate_existing_serials_v2.py --execute --batch-size 100

Author: F2X Development Team
Date: 2025-11-20
"""

import argparse
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


class SerialMigrationV2:
    """Migrate V1 serial numbers to V2 format"""

    def __init__(self, conn_string: str):
        """
        Initialize migration

        Args:
            conn_string: PostgreSQL connection string
                Example: "postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes"
        """
        self.conn_string = conn_string
        self.conn = None
        self.model_mapping = {}

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.conn_string)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)

    def load_model_mapping(self):
        """Load model code mappings"""
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT model_code, short_code FROM model_code_mapping")

        self.model_mapping = {row['model_code']: row['short_code'] for row in cursor.fetchall()}
        print(f"✅ Loaded {len(self.model_mapping)} model mappings:")
        for full, short in self.model_mapping.items():
            print(f"   {full} → {short}")

    def parse_v1_serial(self, serial: str) -> Optional[Dict[str, str]]:
        """
        Parse V1 format serial number

        Args:
            serial: V1 serial (e.g., "PSA10-KR001-251110D-001-0001")

        Returns:
            Dict with components or None if invalid
        """
        # V1 pattern: MODEL-LINE-YYMMDDSHIFT-LOT-SEQ
        pattern = r'^([A-Z0-9]+)-([A-Z]{2}\d{3})-(\d{6})([DN])-(\d{3})-(\d{4})$'
        match = re.match(pattern, serial)

        if not match:
            return None

        return {
            'model_code': match.group(1),
            'line_code': match.group(2),
            'date': match.group(3),
            'shift': match.group(4),
            'lot_seq': match.group(5),
            'serial_seq': match.group(6),
        }

    def convert_to_v2(self, v1_serial: str) -> Optional[str]:
        """
        Convert V1 serial to V2 format

        Args:
            v1_serial: V1 format serial

        Returns:
            V2 format serial or None if conversion fails

        Example:
            PSA10-KR001-251110D-001-0001 → KR01PSA2511001
        """
        components = self.parse_v1_serial(v1_serial)
        if not components:
            print(f"⚠️  Could not parse V1 serial: {v1_serial}")
            return None

        # Get model short code
        model_short = self.model_mapping.get(components['model_code'])
        if not model_short:
            print(f"⚠️  No mapping for model: {components['model_code']}")
            return None

        # Extract line number (KR001 → 01)
        line_code = components['line_code']
        country = line_code[:2]  # KR
        line_num = line_code[2:].lstrip('0') or '0'  # 001 → 1
        line_formatted = f"{int(line_num):02d}"  # 1 → 01

        # Convert date (YYMMDD → YYMM)
        date = components['date']
        month_part = date[:4]  # 251110 → 2511

        # Sequence (use LOT sequence as base, add serial offset)
        # V1: LOT-001, Serial-0001 → V2: sequence 001
        # Note: This might need adjustment based on business rules
        sequence = components['serial_seq'][-3:]  # Last 3 digits

        # Build V2 serial: KR01PSA2511001
        v2_serial = f"{country}{line_formatted}{model_short}{month_part}{sequence}"

        # Validate length
        if len(v2_serial) != 14:
            print(f"⚠️  Invalid V2 length: {v2_serial} (expected 14 chars)")
            return None

        return v2_serial

    def get_serials_to_migrate(self, batch_size: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get batch of V1 serials to migrate

        Args:
            batch_size: Number of serials per batch
            offset: Offset for pagination

        Returns:
            List of serial records
        """
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, serial_number, lot_id, sequence_in_lot, format_version
            FROM serials
            WHERE format_version = 1 OR format_version IS NULL
            ORDER BY id
            LIMIT %s OFFSET %s
        """

        cursor.execute(query, (batch_size, offset))
        return cursor.fetchall()

    def migrate_batch(self, serials: List[Dict], dry_run: bool = True) -> Tuple[int, int, int]:
        """
        Migrate a batch of serials

        Args:
            serials: List of serial records
            dry_run: If True, only simulate (no DB changes)

        Returns:
            Tuple of (success_count, skip_count, error_count)
        """
        success_count = 0
        skip_count = 0
        error_count = 0

        for serial in serials:
            v1_serial = serial['serial_number']
            v2_serial = self.convert_to_v2(v1_serial)

            if not v2_serial:
                error_count += 1
                continue

            # Check for conflicts
            if self.check_conflict(v2_serial, serial['id']):
                print(f"⚠️  Conflict: {v2_serial} already exists, skipping {v1_serial}")
                skip_count += 1
                continue

            # Log conversion
            print(f"{'[DRY RUN] ' if dry_run else ''}Converting:")
            print(f"  ID: {serial['id']}")
            print(f"  V1: {v1_serial}")
            print(f"  V2: {v2_serial}")

            if not dry_run:
                try:
                    self.update_serial(serial['id'], v2_serial)
                    success_count += 1
                except Exception as e:
                    print(f"❌ Error updating serial {serial['id']}: {e}")
                    error_count += 1
            else:
                success_count += 1

        return success_count, skip_count, error_count

    def check_conflict(self, v2_serial: str, current_id: int) -> bool:
        """
        Check if V2 serial already exists

        Args:
            v2_serial: V2 serial number to check
            current_id: Current serial ID (to exclude self)

        Returns:
            True if conflict exists
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM serials WHERE serial_number = %s AND id != %s",
            (v2_serial, current_id)
        )
        return cursor.fetchone() is not None

    def update_serial(self, serial_id: int, v2_serial: str):
        """
        Update serial number to V2 format

        Args:
            serial_id: Serial ID
            v2_serial: New V2 serial number
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE serials
            SET serial_number = %s,
                format_version = 2,
                updated_at = NOW()
            WHERE id = %s
            """,
            (v2_serial, serial_id)
        )
        self.conn.commit()

    def run_migration(self, batch_size: int = 100, dry_run: bool = True):
        """
        Run full migration process

        Args:
            batch_size: Number of serials per batch
            dry_run: If True, only simulate
        """
        print("\n" + "=" * 80)
        print("Serial Number V1 → V2 Migration")
        print("=" * 80)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE (PERMANENT CHANGES)'}")
        print(f"Batch size: {batch_size}")
        print("=" * 80 + "\n")

        self.connect()
        self.load_model_mapping()

        offset = 0
        total_success = 0
        total_skip = 0
        total_error = 0

        while True:
            serials = self.get_serials_to_migrate(batch_size, offset)

            if not serials:
                break

            print(f"\n📦 Processing batch (offset {offset}, count {len(serials)})...")

            success, skip, error = self.migrate_batch(serials, dry_run)

            total_success += success
            total_skip += skip
            total_error += error

            offset += batch_size

        # Summary
        print("\n" + "=" * 80)
        print("Migration Summary")
        print("=" * 80)
        print(f"✅ Successful: {total_success}")
        print(f"⏭️  Skipped: {total_skip}")
        print(f"❌ Errors: {total_error}")
        print(f"📊 Total: {total_success + total_skip + total_error}")

        if dry_run:
            print("\n⚠️  This was a DRY RUN - no changes were made")
            print("   Run with --execute to apply changes")

        self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate existing V1 serial numbers to V2 format"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute migration (default is dry-run only)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of serials per batch (default: 100)'
    )
    parser.add_argument(
        '--db-url',
        type=str,
        default='postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes',
        help='PostgreSQL connection string'
    )

    args = parser.parse_args()

    # Confirmation for execute mode
    if args.execute:
        print("\n" + "!" * 80)
        print("⚠️  WARNING: You are about to PERMANENTLY modify serial numbers!")
        print("!" * 80)
        print("\nThis will:")
        print("  - Change all V1 serial numbers to V2 format")
        print("  - Update the serials table")
        print("  - This operation CANNOT be easily reversed")
        print("\nExternal systems may still reference old serial numbers.")
        print("Printed labels will show the old format.")
        print("\n" + "!" * 80)

        confirm = input("\nType 'CONFIRM MIGRATION' to proceed: ")

        if confirm != "CONFIRM MIGRATION":
            print("❌ Migration cancelled")
            sys.exit(0)

    migrator = SerialMigrationV2(args.db_url)
    migrator.run_migration(
        batch_size=args.batch_size,
        dry_run=not args.execute
    )


if __name__ == '__main__':
    main()
