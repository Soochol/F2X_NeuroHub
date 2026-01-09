"""
Cleanup script to fix ProcessData records that should be marked as completed.

This script finds ProcessData records with completed_at=NULL that have matching
completed WIPProcessHistory records, and updates the ProcessData to match.

This fixes the duplicate attempt count issue where completed processes appeared
as both completed (in WIPProcessHistory) and in-progress (in ProcessData).

Usage:
    python scripts/cleanup_duplicate_process_data.py [--dry-run] [--verbose]

Options:
    --dry-run: Show what would be updated without making changes
    --verbose: Show detailed information for each record
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.process_data import ProcessData
from app.models.wip_process_history import WIPProcessHistory
from app.config import settings


def cleanup_duplicate_process_data(dry_run: bool = False, verbose: bool = False):
    """
    Find and fix ProcessData records that should be marked as completed.

    Args:
        dry_run: If True, show what would be updated without making changes
        verbose: If True, show detailed information for each record
    """
    engine = create_engine(str(settings.DATABASE_URL))

    with Session(engine) as db:
        # Find incomplete ProcessData with matching completed WIPProcessHistory
        incomplete_records = (
            db.query(ProcessData)
            .filter(
                ProcessData.wip_id.isnot(None),
                ProcessData.completed_at.is_(None)
            )
            .all()
        )

        print(f"Found {len(incomplete_records)} incomplete ProcessData records")
        print()

        updated_count = 0
        skipped_count = 0

        for pd in incomplete_records:
            # Find the latest WIPProcessHistory for this WIP+process
            history = (
                db.query(WIPProcessHistory)
                .filter(
                    WIPProcessHistory.wip_item_id == pd.wip_id,
                    WIPProcessHistory.process_id == pd.process_id,
                    WIPProcessHistory.completed_at.isnot(None)
                )
                .order_by(WIPProcessHistory.completed_at.desc())
                .first()
            )

            if history:
                if verbose:
                    print(f"ProcessData {pd.id}:")
                    print(f"  WIP ID: {pd.wip_id}")
                    print(f"  Process ID: {pd.process_id}")
                    print(f"  Started: {pd.started_at}")
                    print(f"  Current result: {pd.result}")
                    print(f"  Will update to:")
                    print(f"    Completed: {history.completed_at}")
                    print(f"    Result: {history.result}")
                    print(f"    Duration: {history.duration_seconds}s")
                    print()

                if not dry_run:
                    pd.completed_at = history.completed_at
                    pd.result = history.result
                    pd.measurements = history.measurements
                    pd.defects = history.defects
                    pd.duration_seconds = history.duration_seconds
                    # Note: We don't update notes as it might be different between the two

                updated_count += 1
                if not verbose:
                    print(f"✓ {'[DRY RUN] Would update' if dry_run else 'Updated'} ProcessData {pd.id}: WIP {pd.wip_id}, Process {pd.process_id}")
            else:
                skipped_count += 1
                if verbose:
                    print(f"⊘ Skipped ProcessData {pd.id}: No matching WIPProcessHistory found")
                    print(f"  WIP ID: {pd.wip_id}")
                    print(f"  Process ID: {pd.process_id}")
                    print(f"  This is a truly in-progress record")
                    print()

        if not dry_run:
            db.commit()
            print()
            print(f"✅ Successfully updated {updated_count} records")
        else:
            print()
            print(f"[DRY RUN] Would update {updated_count} records")

        print(f"Skipped {skipped_count} truly in-progress records")

        # Verify no duplicates remain after cleanup
        if not dry_run:
            print()
            print("Verifying no duplicates remain...")

            duplicates = db.execute(text("""
                SELECT wip_id, process_id, COUNT(*) as count
                FROM process_data
                WHERE wip_id IS NOT NULL AND completed_at IS NULL
                GROUP BY wip_id, process_id
                HAVING COUNT(*) > 1
            """)).fetchall()

            if duplicates:
                print(f"⚠️  WARNING: {len(duplicates)} duplicate incomplete records still exist!")
                for dup in duplicates:
                    print(f"  WIP {dup[0]}, Process {dup[1]}: {dup[2]} records")
            else:
                print("✅ No duplicate incomplete records found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cleanup duplicate ProcessData records"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information for each record"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("ProcessData Cleanup Script")
    print("=" * 80)
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print()

    try:
        cleanup_duplicate_process_data(dry_run=args.dry_run, verbose=args.verbose)
        print()
        print("=" * 80)
        print("Cleanup completed successfully")
        print("=" * 80)
    except Exception as e:
        print()
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
