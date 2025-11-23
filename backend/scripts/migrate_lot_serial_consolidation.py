#!/usr/bin/env python3
"""
Migration Script: LOT Consolidation and Format Conversion
=========================================================

This script consolidates multiple old LOTs with the same production parameters
into single new LOTs, following the original design where 1 LOT = up to 100 products.

Key Features:
- Groups LOTs by (production_line_id, product_model_id, production_month)
- Consolidates each group into ONE representative LOT
- Renumbers all serials sequentially within the consolidated LOT
- Deletes empty LOTs after consolidation

Old LOT Format: WF-KR-YYMMDD{D|N}-nnn (e.g., "WF-KR-251118D-001")
New LOT Format: {Country 2}{Line 2}{Model 3}{Month 4} = 11 chars (e.g., "KR01PSA2511")

Old Serial Format: Independent generation (various formats)
New Serial Format: {LOT 11}{Sequence 3} = 14 chars (e.g., "KR01PSA2511001")

Usage:
    python migrate_lot_serial_consolidation.py [--dry-run] [--rollback]

Options:
    --dry-run   Show what would be changed without modifying database
    --rollback  Revert to old format (requires backup)

Author: F2X Development Team
Date: 2025-11-21
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    # dotenv not installed, environment variables should be set manually
    pass

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import json

from app.database import get_db
from app.models.lot import Lot
from app.models.serial import Serial
from app.models.product_model import ProductModel
from app.models.production_line import ProductionLine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_lot_serial.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LotSerialMigrator:
    """Handles migration of LOT and Serial numbers to new format."""

    def __init__(self, db_session: Session, dry_run: bool = False):
        """
        Initialize migrator.

        Args:
            db_session: Database session
            dry_run: If True, only simulate changes without committing
        """
        self.db = db_session
        self.dry_run = dry_run
        self.backup_data = {}
        self.migration_stats = {
            'lots_processed': 0,
            'lots_updated': 0,
            'serials_processed': 0,
            'serials_updated': 0,
            'errors': []
        }

    def parse_old_lot_format(self, old_lot: str) -> Optional[Dict]:
        """
        Parse old LOT format to extract components.

        Args:
            old_lot: Old format LOT (e.g., "WF-KR-251118D-001")

        Returns:
            Dictionary with parsed components or None if invalid
        """
        try:
            parts = old_lot.split('-')
            if len(parts) != 4:
                return None

            model_code = parts[0]  # "WF"
            country = parts[1]  # "KR"
            date_shift = parts[2]  # "251118D"
            sequence = parts[3]  # "001"

            # Extract date and shift
            date_str = date_shift[:-1]  # "251118"
            shift = date_shift[-1]  # "D" or "N"

            # Parse date (YYMMDD to YYMM)
            year_month = date_str[:4]  # "2511"

            return {
                'model_code': model_code,
                'country': country,
                'year_month': year_month,
                'date': date_str,
                'shift': shift,
                'sequence': sequence
            }
        except Exception as e:
            logger.error(f"Error parsing old LOT format '{old_lot}': {e}")
            return None

    def generate_new_lot_format(
        self,
        lot: Lot,
        production_line: ProductionLine,
        product_model: ProductModel
    ) -> str:
        """
        Generate new LOT format.

        Args:
            lot: LOT object
            production_line: Production line object
            product_model: Product model object

        Returns:
            New format LOT number (11 chars)
        """
        # Country code (hardcoded for Korea)
        country_code = "KR"

        # Line number mapping based on line code or ID
        # LINE-A (ID 13) -> 01, LINE-B (ID 14) -> 02
        line_code = production_line.line_code
        if "LINE-A" in line_code or production_line.id == 13:
            line_number = 1
        elif "LINE-B" in line_code or production_line.id == 14:
            line_number = 2
        else:
            # Fallback: use last digit of line ID
            line_number = production_line.id % 100
            logger.warning(f"Unknown line_code '{line_code}' (ID {production_line.id}), using line_number={line_number}")

        # Model code extraction from model_code like "PSA-1000" -> "P10", "PSA-2000" -> "P20", "PSA-3000" -> "P30"
        model_code_str = product_model.model_code
        if "PSA-1000" in model_code_str or product_model.id == 19:
            model_code = "P10"
        elif "PSA-2000" in model_code_str or product_model.id == 20:
            model_code = "P20"
        elif "PSA-3000" in model_code_str or product_model.id == 21:
            model_code = "P30"
        else:
            # Fallback: use first 3 chars
            model_code = model_code_str[:3].upper()
            logger.warning(f"Unknown model_code '{model_code_str}' (ID {product_model.id}), using '{model_code}'")

        # Production month (YYMM)
        production_month = lot.production_date.strftime('%y%m')

        # Generate new LOT number: Country(2) + Line(2) + Model(3) + Month(4) = 11 chars
        new_lot = f"{country_code}{line_number:02d}{model_code}{production_month}"

        return new_lot

    def group_lots_by_key(self) -> Dict[Tuple, List[Lot]]:
        """
        Group LOTs by (production_line_id, product_model_id, production_month).

        Returns:
            Dictionary mapping group key to list of LOTs
        """
        lots = self.db.query(Lot).all()
        grouped = defaultdict(list)

        for lot in lots:
            # Skip if already new format
            if len(lot.lot_number) == 11 and '-' not in lot.lot_number:
                logger.info(f"Skipping LOT {lot.lot_number} - already in new format")
                continue

            if not lot.production_line_id or not lot.product_model_id:
                logger.warning(f"LOT {lot.lot_number} missing production_line_id or product_model_id")
                continue

            # Extract production month
            production_month = lot.production_date.strftime('%y%m')

            # Group key
            key = (lot.production_line_id, lot.product_model_id, production_month)
            grouped[key].append(lot)

        return grouped

    def consolidate_lot_group(
        self,
        lots: List[Lot],
        production_line: ProductionLine,
        product_model: ProductModel
    ) -> bool:
        """
        Consolidate multiple LOTs into one.

        Args:
            lots: List of LOTs to consolidate (already sorted by ID)
            production_line: Production line object
            product_model: Product model object

        Returns:
            True if successful
        """
        if not lots:
            return False

        # Sort by ID to get consistent representative
        lots.sort(key=lambda x: x.id)

        # Representative LOT (keep the first one)
        representative = lots[0]

        # Generate new LOT number for representative
        new_lot_number = self.generate_new_lot_format(
            representative,
            production_line,
            product_model
        )

        logger.info(f"Consolidating {len(lots)} LOTs into: {new_lot_number}")
        logger.info(f"  Representative LOT ID: {representative.id}")

        # Store backup data for representative LOT
        self.backup_data[representative.id] = {
            'old_lot_number': representative.lot_number,
            'new_lot_number': new_lot_number,
            'consolidated_from': [lot.lot_number for lot in lots]
        }

        # Collect all serials from all LOTs in group
        all_serials = []
        for lot in lots:
            serials = self.db.query(Serial).filter(Serial.lot_id == lot.id).order_by(Serial.sequence_in_lot).all()
            all_serials.extend(serials)
            logger.info(f"  LOT {lot.id} ({lot.lot_number}): {len(serials)} serials")

        # Sort serials for consistent ordering (by original LOT ID, then sequence)
        all_serials.sort(key=lambda x: (x.lot_id, x.sequence_in_lot))

        # Update representative LOT
        old_lot_number = representative.lot_number

        if not self.dry_run:
            representative.lot_number = new_lot_number
            self.db.flush()

        logger.info(f"  Updated representative LOT: {old_lot_number} → {new_lot_number}")

        # Store serial backup data
        if 'serials' not in self.backup_data[representative.id]:
            self.backup_data[representative.id]['serials'] = []

        # Renumber all serials and assign to representative LOT
        for idx, serial in enumerate(all_serials, start=1):
            old_serial_number = serial.serial_number
            old_lot_id = serial.lot_id

            # New serial number: LOT(11) + Sequence(3)
            new_serial_number = f"{new_lot_number}{idx:03d}"

            # Store backup
            self.backup_data[representative.id]['serials'].append({
                'serial_id': serial.id,
                'old_serial': old_serial_number,
                'new_serial': new_serial_number,
                'old_lot_id': old_lot_id,
                'old_sequence': serial.sequence_in_lot
            })

            # Update serial
            if not self.dry_run:
                serial.lot_id = representative.id
                serial.serial_number = new_serial_number
                serial.sequence_in_lot = idx

            # Log first 5 and last 2 serials for visibility
            if idx <= 5 or idx > len(all_serials) - 2:
                logger.info(f"    Serial {old_serial_number} → {new_serial_number} (seq: {idx})")
            elif idx == 6:
                logger.info(f"    ... {len(all_serials) - 7} more serials ...")

        if not self.dry_run:
            self.db.flush()

        # Delete non-representative LOTs
        for lot in lots[1:]:
            logger.info(f"  Deleting empty LOT {lot.id} ({lot.lot_number})")
            if not self.dry_run:
                self.db.delete(lot)

        self.migration_stats['lots_updated'] += 1
        self.migration_stats['serials_updated'] += len(all_serials)

        return True

    def migrate_lot(self, lot: Lot) -> bool:
        """
        Migrate a single LOT to new format.

        Args:
            lot: LOT object to migrate

        Returns:
            True if successful, False otherwise
        """
        try:
            old_lot_number = lot.lot_number

            # Check if already in new format (11 chars, no hyphens)
            if len(old_lot_number) == 11 and '-' not in old_lot_number:
                logger.info(f"LOT {old_lot_number} already in new format")
                return True

            # Get related objects
            if not lot.production_line_id:
                logger.warning(f"LOT {old_lot_number} has no production_line_id")
                return False

            production_line = self.db.query(ProductionLine).filter(
                ProductionLine.id == lot.production_line_id
            ).first()

            if not production_line:
                logger.error(f"Production line {lot.production_line_id} not found")
                return False

            product_model = self.db.query(ProductModel).filter(
                ProductModel.id == lot.product_model_id
            ).first()

            if not product_model:
                logger.error(f"Product model {lot.product_model_id} not found")
                return False

            # Generate new LOT number
            new_lot_number = self.generate_new_lot_format(lot, production_line, product_model)

            # Store backup
            self.backup_data[lot.id] = {
                'old_lot_number': old_lot_number,
                'new_lot_number': new_lot_number
            }

            logger.info(f"Migrating LOT: {old_lot_number} -> {new_lot_number}")

            if not self.dry_run:
                lot.lot_number = new_lot_number
                self.db.add(lot)

            self.migration_stats['lots_updated'] += 1
            return True

        except Exception as e:
            logger.error(f"Error migrating LOT {lot.id}: {e}")
            self.migration_stats['errors'].append(f"LOT {lot.id}: {e}")
            return False

    def migrate_serial(self, serial: Serial, lot_mapping: Dict[int, str]) -> bool:
        """
        Migrate a single Serial to new format.

        Args:
            serial: Serial object to migrate
            lot_mapping: Mapping of lot_id to new LOT numbers

        Returns:
            True if successful, False otherwise
        """
        try:
            old_serial_number = serial.serial_number

            # Check if already in new format (14 chars)
            if len(old_serial_number) == 14:
                logger.info(f"Serial {old_serial_number} already in new format")
                return True

            # Get new LOT number
            if serial.lot_id not in lot_mapping:
                logger.error(f"Serial {old_serial_number} has unmapped lot_id {serial.lot_id}")
                return False

            new_lot_number = lot_mapping[serial.lot_id]

            # Generate new serial (LOT + sequence)
            new_serial_number = f"{new_lot_number}{serial.sequence_in_lot:03d}"

            # Store backup
            if serial.lot_id not in self.backup_data:
                self.backup_data[serial.lot_id] = {}

            if 'serials' not in self.backup_data[serial.lot_id]:
                self.backup_data[serial.lot_id]['serials'] = []

            self.backup_data[serial.lot_id]['serials'].append({
                'serial_id': serial.id,
                'old_serial': old_serial_number,
                'new_serial': new_serial_number
            })

            logger.info(f"Migrating Serial: {old_serial_number} -> {new_serial_number}")

            if not self.dry_run:
                serial.serial_number = new_serial_number
                self.db.add(serial)

            self.migration_stats['serials_updated'] += 1
            return True

        except Exception as e:
            logger.error(f"Error migrating Serial {serial.id}: {e}")
            self.migration_stats['errors'].append(f"Serial {serial.id}: {e}")
            return False

    def run_migration(self) -> bool:
        """
        Execute the complete migration with LOT consolidation.

        Returns:
            True if successful
        """
        try:
            logger.info("Starting LOT and Serial number migration with consolidation...")
            logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")

            # Step 1: Group LOTs
            logger.info("=" * 60)
            logger.info("Step 1: Grouping LOTs by production parameters...")
            grouped_lots = self.group_lots_by_key()

            logger.info(f"Found {len(grouped_lots)} unique LOT groups")

            # Step 2: Process each group
            logger.info("=" * 60)
            logger.info("Step 2: Consolidating and migrating LOTs...")

            for (line_id, model_id, month), lots in grouped_lots.items():
                self.migration_stats['lots_processed'] += len(lots)

                # Get production line and model
                production_line = self.db.query(ProductionLine).filter(
                    ProductionLine.id == line_id
                ).first()
                product_model = self.db.query(ProductModel).filter(
                    ProductModel.id == model_id
                ).first()

                if not production_line or not product_model:
                    logger.warning(f"Missing line or model for group: line_id={line_id}, model_id={model_id}")
                    self.migration_stats['errors'].append(
                        f"Missing production_line or product_model for group: ({line_id}, {model_id}, {month})"
                    )
                    continue

                logger.info(f"\nProcessing group: Line={production_line.line_code}, Model={product_model.model_code}, Month={month}")

                # If only one LOT in group, just migrate it normally
                if len(lots) == 1:
                    lot = lots[0]
                    logger.info(f"  Single LOT in group: {lot.lot_number} (ID: {lot.id})")
                    if not self.migrate_lot(lot):
                        self.migration_stats['errors'].append(f"Failed to migrate LOT {lot.id}")
                    else:
                        # Also migrate its serials
                        serials = self.db.query(Serial).filter(Serial.lot_id == lot.id).all()
                        self.migration_stats['serials_processed'] += len(serials)
                        if lot.id in self.backup_data:
                            new_lot_number = self.backup_data[lot.id]['new_lot_number']
                            for serial in serials:
                                if not self.migrate_serial(serial, {lot.id: new_lot_number}):
                                    self.migration_stats['errors'].append(f"Failed to migrate Serial {serial.id}")
                else:
                    # Consolidate multiple LOTs
                    logger.info(f"  Group has {len(lots)} LOTs - consolidating...")
                    try:
                        if not self.consolidate_lot_group(lots, production_line, product_model):
                            self.migration_stats['errors'].append(
                                f"Failed to consolidate group: ({line_id}, {model_id}, {month})"
                            )
                    except Exception as e:
                        logger.error(f"Error consolidating group: {e}")
                        self.migration_stats['errors'].append(
                            f"Error consolidating group ({line_id}, {model_id}, {month}): {e}"
                        )

            # Save backup data
            if self.backup_data:
                backup_file = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w') as f:
                    json.dump(self.backup_data, f, indent=2, default=str)
                logger.info(f"\nBackup saved to {backup_file}")

            # Commit or rollback
            if not self.dry_run:
                self.db.commit()
                logger.info("Changes committed to database")
            else:
                self.db.rollback()
                logger.info("Dry run completed - no changes made to database")

            # Print summary
            self.print_summary()

            return len(self.migration_stats['errors']) == 0

        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            self.db.rollback()
            logger.info("Rolled back all changes")
            return False

    def print_summary(self):
        """Print migration summary."""
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"LOTs processed: {self.migration_stats['lots_processed']}")
        print(f"LOTs updated: {self.migration_stats['lots_updated']}")
        print(f"Serials processed: {self.migration_stats['serials_processed']}")
        print(f"Serials updated: {self.migration_stats['serials_updated']}")

        if self.migration_stats['errors']:
            print(f"\nErrors ({len(self.migration_stats['errors'])}):")
            for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.migration_stats['errors']) > 10:
                print(f"  ... and {len(self.migration_stats['errors']) - 10} more")

        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate LOT and Serial numbers to new format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying database"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback to previous format (requires backup file)"
    )
    parser.add_argument(
        "--backup-file",
        type=str,
        help="Backup file for rollback operation"
    )

    args = parser.parse_args()

    # Get database connection
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost/f2x_neurohub"
    )

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        if args.rollback:
            logger.error("Rollback not yet implemented")
            return 1

        migrator = LotSerialMigrator(db, dry_run=args.dry_run)
        success = migrator.run_migration()

        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())