# LOT Consolidation Migration Script

## Overview
This migration script consolidates multiple old LOTs with the same production parameters into single new LOTs, following the original system design where 1 LOT = up to 100 products.

## Problem Solved
**Old System Issue:**
- Multiple LOTs with same (line, model, month) were created separately
- Example: WF-KR-251120N-003, WF-KR-251120N-004, WF-KR-251120N-005
- All would convert to the same new LOT number: LI14PSA2511
- This caused unique constraint violations

**Solution: Consolidation Strategy**
- Groups all LOTs by (production_line_id, product_model_id, production_month)
- Consolidates each group into ONE representative LOT
- Renumbers all serials sequentially within the consolidated LOT
- Deletes empty LOTs after consolidation

## Consolidation Example

### Before Migration:
```
Group: (line=LI14, model=PSA, month=2511)

LOT 63: WF-KR-251120N-003 (100 serials: 001-100)
LOT 64: WF-KR-251120N-004 (100 serials: 001-100)
LOT 65: WF-KR-251120N-005 (50 serials: 001-050)
```

### After Consolidation:
```
LOT 63: LI14PSA2511 (250 serials total)
- Serials from LOT 63: LI14PSA2511001 to LI14PSA2511100
- Serials from LOT 64: LI14PSA2511101 to LI14PSA2511200
- Serials from LOT 65: LI14PSA2511201 to LI14PSA2511250

LOT 64: DELETED (serials moved to LOT 63)
LOT 65: DELETED (serials moved to LOT 63)
```

## Usage

### 1. Test with Dry Run (RECOMMENDED FIRST)
```bash
python migrate_lot_serial_consolidation.py --dry-run
```
This will:
- Show what changes would be made
- Not modify the database
- Generate a report of consolidations

### 2. Execute Migration
```bash
python migrate_lot_serial_consolidation.py
```
This will:
- Consolidate LOTs with same production parameters
- Update all serial numbers
- Delete empty LOTs
- Create backup file: `migration_backup_YYYYMMDD_HHMMSS.json`

### 3. Verify Results
After migration, verify:
- Each production group has only ONE LOT
- Serial numbers are sequential within each LOT
- Total serial count matches original

## Format Changes

### LOT Number Format:
- **Old:** `WF-KR-YYMMDD{D|N}-nnn` (e.g., "WF-KR-251118D-001")
- **New:** `{Country 2}{Line 2}{Model 3}{Month 4}` = 11 chars (e.g., "KR01PSA2511")

### Serial Number Format:
- **Old:** Various independent formats
- **New:** `{LOT 11}{Sequence 3}` = 14 chars (e.g., "KR01PSA2511001")

## Backup and Recovery

### Backup File
The script creates a backup JSON file containing:
- Original LOT numbers
- New LOT numbers
- List of consolidated LOTs
- All serial number mappings (old -> new)
- Original LOT assignments for serials

### Rollback (if needed)
```bash
python migrate_lot_serial_consolidation.py --rollback --backup-file migration_backup_YYYYMMDD_HHMMSS.json
```
*Note: Rollback functionality needs to be implemented if required*

## Key Features

1. **Smart Grouping**: Groups LOTs by production parameters automatically
2. **Representative Selection**: Keeps the LOT with smallest ID as representative
3. **Sequential Renumbering**: Renumbers all serials in order (001, 002, 003...)
4. **Cleanup**: Removes empty LOTs after consolidation
5. **Comprehensive Backup**: Full backup of all changes for recovery
6. **Dry Run Mode**: Test before executing actual changes

## Requirements

- Python 3.8+
- PostgreSQL database
- SQLAlchemy
- Environment variables configured in `.env`

## Logging

The script creates detailed logs in `migration_lot_serial.log` including:
- Each consolidation operation
- Serial number updates
- Deleted LOTs
- Any errors encountered

## Error Handling

The script handles:
- Missing production line or model data
- LOTs already in new format (skipped)
- Database transaction rollback on failure
- Comprehensive error reporting

## Performance Considerations

- Uses batch operations where possible
- Flushes changes periodically to avoid memory issues
- Logs only first 5 and last 2 serials per LOT to reduce log size

## Contact

For issues or questions about this migration, contact the F2X Development Team.