-- ============================================================================
-- Function: prevent_process_deletion()
-- Description: Prevents deletion of process if execution data exists
-- Usage: Attach as BEFORE DELETE trigger to processes table
-- PostgreSQL Version: 14+
-- ============================================================================
--
-- Purpose:
--   - Enforces referential integrity for historical process execution data
--   - Prevents accidental deletion of processes with production history
--   - Provides clear error message with process name and execution count
--   - Complements ON DELETE RESTRICT constraint with better user feedback
--
-- Business Rules:
--   - Process can only be deleted if NO execution records exist in process_data
--   - If execution records exist, deletion is blocked with descriptive error
--   - This ensures historical traceability of production data
--   - Soft delete (is_active flag) should be used instead of hard delete
--
-- Error Message Format:
--   "Cannot delete process <process_name_ko>: <count> execution records exist"
--   Example: "Cannot delete process 웨이퍼 연마: 150 execution records exist"
--
-- Trigger Definition:
--   CREATE TRIGGER trg_processes_prevent_delete
--   BEFORE DELETE ON processes
--   FOR EACH ROW
--   EXECUTE FUNCTION prevent_process_deletion();
--
-- Alternative Approach:
--   Instead of deleting, use soft delete:
--   UPDATE processes SET is_active = false WHERE id = <process_id>;
--
-- Dependencies:
--   - processes table (with columns: id, process_name_ko, is_active)
--   - process_data table (with column: process_id referencing processes.id)
--
-- Performance Considerations:
--   - COUNT(*) query on process_data is fast with proper indexing
--   - Index on process_data(process_id) is essential
--   - Trigger only fires on DELETE, no overhead on INSERT/UPDATE
--
-- Related Constraints:
--   - Foreign key: process_data.process_id -> processes.id
--   - ON DELETE RESTRICT: Database-level constraint (backup protection)
--   - This trigger provides user-friendly error before FK constraint fires
-- ============================================================================

CREATE OR REPLACE FUNCTION prevent_process_deletion()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER -- Ensures query succeeds even if user lacks SELECT privilege
AS $$
DECLARE
    v_data_count INTEGER;
    v_process_name VARCHAR(200);
BEGIN
    -- ========================================================================
    -- Step 1: Count execution records for this process
    -- ========================================================================
    -- Query process_data to check if any production execution records exist
    -- This includes historical data that must be preserved for compliance
    SELECT COUNT(*) INTO v_data_count
    FROM process_data
    WHERE process_id = OLD.id;

    -- ========================================================================
    -- Step 2: Store process name for error message
    -- ========================================================================
    -- Use process_name_ko (Korean name) for user-friendly error message
    -- Fallback to process_name_en if Korean name is NULL
    v_process_name := COALESCE(OLD.process_name_ko, OLD.process_name_en, 'Unknown');

    -- ========================================================================
    -- Step 3: Block deletion if execution data exists
    -- ========================================================================
    -- RAISE EXCEPTION aborts the transaction and returns error to client
    -- Error code: 23503 (foreign_key_violation) for application handling
    IF v_data_count > 0 THEN
        RAISE EXCEPTION 'Cannot delete process "%": % execution records exist',
            v_process_name,
            v_data_count
        USING
            HINT = 'Use soft delete (SET is_active = false) instead of deleting the process.',
            ERRCODE = '23503'; -- foreign_key_violation (standard PostgreSQL error code)
    END IF;

    -- ========================================================================
    -- Step 4: Allow deletion if no execution data exists
    -- ========================================================================
    -- Returning OLD allows the DELETE operation to proceed
    RETURN OLD;
END;
$$;

-- ============================================================================
-- Function Metadata
-- ============================================================================
COMMENT ON FUNCTION prevent_process_deletion() IS
'Prevents deletion of process record if any execution data exists in process_data table. Returns descriptive error message with process name and record count. Use soft delete (is_active=false) for processes with historical data.';

-- ============================================================================
-- Trigger Definition
-- ============================================================================
/*

-- Attach trigger to processes table
CREATE TRIGGER trg_processes_prevent_delete
BEFORE DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION prevent_process_deletion();

-- Add comment to trigger
COMMENT ON TRIGGER trg_processes_prevent_delete ON processes IS
'Prevents hard deletion of processes that have execution history. Enforces data integrity for compliance and traceability.';

*/

-- ============================================================================
-- Usage Examples
-- ============================================================================
/*

-- ============================================================================
-- Example 1: Attempt to delete process with execution data (BLOCKED)
-- ============================================================================
DELETE FROM processes WHERE id = 1;
-- ERROR: Cannot delete process "웨이퍼 연마": 150 execution records exist
-- HINT: Use soft delete (SET is_active = false) instead of deleting the process.

-- ============================================================================
-- Example 2: Soft delete process instead (RECOMMENDED)
-- ============================================================================
UPDATE processes
SET is_active = false,
    updated_at = NOW()
WHERE id = 1;
-- SUCCESS: Process marked as inactive but historical data preserved

-- ============================================================================
-- Example 3: Delete process with no execution data (ALLOWED)
-- ============================================================================
DELETE FROM processes WHERE id = 999;
-- SUCCESS: Process deleted (no execution records exist)

-- ============================================================================
-- Example 4: Check execution count before attempting deletion
-- ============================================================================
SELECT
    p.id,
    p.process_name_ko,
    p.process_name_en,
    p.is_active,
    COUNT(pd.id) AS execution_count
FROM processes p
LEFT JOIN process_data pd ON p.id = pd.process_id
WHERE p.id = 1
GROUP BY p.id, p.process_name_ko, p.process_name_en, p.is_active;

-- Result:
-- id | process_name_ko | process_name_en      | is_active | execution_count
-- ---+-----------------+---------------------+-----------+-----------------
-- 1  | 웨이퍼 연마      | Wafer Lapping       | true      | 150
--
-- Decision: Use soft delete since execution_count > 0

-- ============================================================================
-- Example 5: Query inactive processes (soft deleted)
-- ============================================================================
SELECT
    id,
    process_name_ko,
    process_name_en,
    is_active,
    updated_at
FROM processes
WHERE is_active = false
ORDER BY updated_at DESC;

-- ============================================================================
-- Example 6: Application-level error handling (Python with psycopg2)
-- ============================================================================
import psycopg2

try:
    cursor.execute("DELETE FROM processes WHERE id = %s", (process_id,))
    conn.commit()
    print("Process deleted successfully")
except psycopg2.Error as e:
    if e.pgcode == '23503':  # foreign_key_violation
        print(f"Cannot delete process: {e.pgerror}")
        print("Suggestion: Use soft delete instead")
    else:
        print(f"Unexpected error: {e}")
    conn.rollback()

-- ============================================================================
-- Example 7: Cascading soft delete for related entities
-- ============================================================================
-- If a process is soft-deleted, you may want to hide related process_parameters
UPDATE process_parameters
SET is_active = false
WHERE process_id IN (
    SELECT id FROM processes WHERE is_active = false
);

*/

-- ============================================================================
-- Index Recommendation
-- ============================================================================
/*

-- Ensure fast execution count query
CREATE INDEX IF NOT EXISTS idx_process_data_process_id
ON process_data(process_id);

-- Composite index for soft delete queries
CREATE INDEX IF NOT EXISTS idx_processes_active
ON processes(is_active, updated_at DESC)
WHERE is_active = false;

*/
