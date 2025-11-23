-- ============================================================================
-- Database Migration: Remove Shift Column from lots Table
-- ============================================================================
-- Date: 2025-01-21
-- Priority: HIGH
-- Breaking Change: YES
-- Impact: All existing shift data will be permanently deleted
--
-- Description:
--   Removes the shift column from the lots table as shift tracking has been
--   removed from the system. This migration drops the shift column, its
--   check constraint, and the composite index that includes shift.
--
-- Rollback:
--   To rollback this migration, you would need to:
--   1. Add shift column back: ALTER TABLE lots ADD COLUMN shift VARCHAR(1) NOT NULL DEFAULT 'D';
--   2. Recreate check constraint
--   3. Recreate idx_lots_model_date_shift index
--   WARNING: Original shift data will NOT be recoverable after this migration!
--
-- Prerequisites:
--   - Backup database before running this migration
--   - Ensure backend code has been updated to remove shift field
--   - Ensure frontend code has been updated to remove shift field
--
-- Usage:
--   psql -h localhost -U postgres -d f2x_neurohub -f remove_shift_from_lots.sql
-- ============================================================================

\echo '============================================================================'
\echo 'Starting migration: Remove shift column from lots table'
\echo '============================================================================'

-- Set error handling
\set ON_ERROR_STOP on
\timing on

-- Begin transaction
BEGIN;

\echo ''
\echo 'Step 1: Drop composite index idx_lots_model_date_shift...'
DROP INDEX IF EXISTS idx_lots_model_date_shift;
\echo '✓ Index idx_lots_model_date_shift dropped'

\echo ''
\echo 'Step 2: Create new composite index idx_lots_model_date (without shift)...'
CREATE INDEX IF NOT EXISTS idx_lots_model_date ON lots(product_model_id, production_date);
\echo '✓ Index idx_lots_model_date created'

\echo ''
\echo 'Step 3: Drop check constraint chk_lots_shift...'
ALTER TABLE lots DROP CONSTRAINT IF EXISTS chk_lots_shift;
\echo '✓ Constraint chk_lots_shift dropped'

\echo ''
\echo 'Step 4: Drop shift column from lots table...'
ALTER TABLE lots DROP COLUMN IF EXISTS shift;
\echo '✓ Column shift dropped'

\echo ''
\echo 'Step 5: Update column comments for clarity...'
COMMENT ON COLUMN lots.lot_number IS 'Auto-generated LOT identifier';
\echo '✓ Column comments updated'

-- Commit transaction
COMMIT;

\echo ''
\echo '============================================================================'
\echo 'Migration completed successfully!'
\echo '============================================================================'
\echo 'Changes applied:'
\echo '  - Dropped index: idx_lots_model_date_shift'
\echo '  - Created index: idx_lots_model_date (product_model_id, production_date)'
\echo '  - Dropped constraint: chk_lots_shift'
\echo '  - Dropped column: lots.shift'
\echo '  - Updated column comments'
\echo ''
\echo 'IMPORTANT:'
\echo '  - All shift data has been permanently deleted'
\echo '  - Verify backend server starts without errors'
\echo '  - Verify frontend works correctly'
\echo '  - Run integration tests'
\echo '============================================================================'

-- Verification queries
\echo ''
\echo 'Verification: Checking lots table structure...'
\d+ lots

\echo ''
\echo 'Verification: Checking indexes on lots table...'
\di+ idx_lots*
