-- ============================================================================
-- Function: prevent_user_deletion()
-- Description: Prevents deletion of user if process execution records exist
-- Usage: Attach as BEFORE DELETE trigger to users table
-- PostgreSQL Version: 14+
-- ============================================================================
--
-- Purpose:
--   - Enforces referential integrity for historical operator data
--   - Prevents accidental deletion of users with production activity history
--   - Provides clear error message with username and record count
--   - Maintains accountability trail for quality and compliance
--
-- Business Rules:
--   - User can only be deleted if NO process execution records exist
--   - If execution records exist, deletion is blocked with descriptive error
--   - Ensures operator accountability for all produced units
--   - Critical for traceability: "Who produced this serial?"
--   - Soft delete (is_active flag) should be used instead of hard delete
--
-- Error Message Format:
--   "Cannot delete user <username>: <count> process execution records exist"
--   Example: "Cannot delete user kim.operator: 1250 process execution records exist"
--
-- Trigger Definition:
--   CREATE TRIGGER trg_users_prevent_delete
--   BEFORE DELETE ON users
--   FOR EACH ROW
--   EXECUTE FUNCTION prevent_user_deletion();
--
-- Alternative Approach:
--   Instead of deleting, use soft delete:
--   UPDATE users SET is_active = false WHERE id = <user_id>;
--
-- Dependencies:
--   - users table (with columns: id, username, is_active)
--   - process_data table (with column: operator_id referencing users.id)
--
-- Performance Considerations:
--   - COUNT(*) query on process_data is fast with proper indexing
--   - Index on process_data(operator_id) is essential
--   - Trigger only fires on DELETE, no overhead on INSERT/UPDATE
--
-- Compliance & Quality:
--   - ISO 9001 requires operator traceability for manufactured products
--   - Deleting operator records breaks audit trail
--   - Historical data must reference valid operator for compliance
--
-- Related Constraints:
--   - Foreign key: process_data.operator_id -> users.id
--   - ON DELETE RESTRICT: Database-level constraint (backup protection)
--   - This trigger provides user-friendly error before FK constraint fires
-- ============================================================================

CREATE OR REPLACE FUNCTION prevent_user_deletion()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER -- Ensures query succeeds even if user lacks SELECT privilege
AS $$
DECLARE
    v_data_count INTEGER;
    v_username VARCHAR(50);
BEGIN
    -- ========================================================================
    -- Step 1: Count process execution records for this user
    -- ========================================================================
    -- Query process_data to check if user has any production activity history
    -- This includes all operations performed by this operator
    SELECT COUNT(*) INTO v_data_count
    FROM process_data
    WHERE operator_id = OLD.id;

    -- ========================================================================
    -- Step 2: Store username for error message
    -- ========================================================================
    -- Use username for user-friendly error message
    -- This is more meaningful than numeric user ID
    v_username := COALESCE(OLD.username, 'Unknown');

    -- ========================================================================
    -- Step 3: Block deletion if execution records exist
    -- ========================================================================
    -- RAISE EXCEPTION aborts the transaction and returns error to client
    -- Error code: 23503 (foreign_key_violation) for application handling
    IF v_data_count > 0 THEN
        RAISE EXCEPTION 'Cannot delete user "%": % process execution records exist',
            v_username,
            v_data_count
        USING
            HINT = 'Use soft delete (SET is_active = false) instead of deleting the user. Historical data requires operator traceability.',
            DETAIL = format('User %s has operated %s process steps across production history.',
                v_username, v_data_count),
            ERRCODE = '23503'; -- foreign_key_violation (standard PostgreSQL error code)
    END IF;

    -- ========================================================================
    -- Step 4: Allow deletion if no execution records exist
    -- ========================================================================
    -- Returning OLD allows the DELETE operation to proceed
    RETURN OLD;
END;
$$;

-- ============================================================================
-- Function Metadata
-- ============================================================================
COMMENT ON FUNCTION prevent_user_deletion() IS
'Prevents deletion of user record if any process execution records exist in process_data table. Returns descriptive error message with username and record count. Use soft delete (is_active=false) for users with production history.';

-- ============================================================================
-- Trigger Definition
-- ============================================================================
/*

-- Attach trigger to users table
CREATE TRIGGER trg_users_prevent_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION prevent_user_deletion();

-- Add comment to trigger
COMMENT ON TRIGGER trg_users_prevent_delete ON users IS
'Prevents hard deletion of users that have process execution history. Enforces operator traceability for compliance and quality management.';

*/

-- ============================================================================
-- Usage Examples
-- ============================================================================
/*

-- ============================================================================
-- Example 1: Attempt to delete user with execution history (BLOCKED)
-- ============================================================================
DELETE FROM users WHERE id = 5;
-- ERROR: Cannot delete user "kim.operator": 1250 process execution records exist
-- HINT: Use soft delete (SET is_active = false) instead of deleting the user. Historical data requires operator traceability.
-- DETAIL: User kim.operator has operated 1250 process steps across production history.

-- ============================================================================
-- Example 2: Soft delete user instead (RECOMMENDED)
-- ============================================================================
UPDATE users
SET is_active = false,
    updated_at = NOW()
WHERE id = 5;
-- SUCCESS: User marked as inactive but production history preserved

-- ============================================================================
-- Example 3: Delete user with no execution history (ALLOWED)
-- ============================================================================
-- Example: Deleting a test account created by mistake
DELETE FROM users WHERE id = 999;
-- SUCCESS: User deleted (no process execution records exist)

-- ============================================================================
-- Example 4: Check execution count before attempting deletion
-- ============================================================================
SELECT
    u.id,
    u.username,
    u.full_name,
    u.role,
    u.is_active,
    COUNT(pd.id) AS execution_count,
    MIN(pd.created_at) AS first_operation,
    MAX(pd.created_at) AS last_operation
FROM users u
LEFT JOIN process_data pd ON u.id = pd.operator_id
WHERE u.id = 5
GROUP BY u.id, u.username, u.full_name, u.role, u.is_active;

-- Result:
-- id | username      | full_name    | role   | is_active | execution_count | first_operation      | last_operation
-- ---+---------------+--------------+--------+-----------+-----------------+---------------------+---------------------
-- 5  | kim.operator  | Kim Young-ho | WORKER | true      | 1250            | 2023-01-15 08:30:00 | 2025-11-17 16:45:00
--
-- Decision: Use soft delete since execution_count > 0

-- ============================================================================
-- Example 5: Query inactive users (soft deleted)
-- ============================================================================
SELECT
    id,
    username,
    full_name,
    role,
    is_active,
    updated_at
FROM users
WHERE is_active = false
ORDER BY updated_at DESC;

-- ============================================================================
-- Example 6: Operator production summary for departing employee
-- ============================================================================
-- Before soft-deleting user, generate production summary report
SELECT
    u.username,
    u.full_name,
    p.process_name_ko,
    COUNT(pd.id) AS operation_count,
    MIN(pd.created_at) AS first_operation,
    MAX(pd.created_at) AS last_operation
FROM users u
JOIN process_data pd ON u.id = pd.operator_id
JOIN processes p ON pd.process_id = p.id
WHERE u.id = 5
GROUP BY u.username, u.full_name, p.process_name_ko
ORDER BY operation_count DESC;

-- ============================================================================
-- Example 7: Application-level error handling (Python with psycopg2)
-- ============================================================================
import psycopg2

def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        print("User deleted successfully")
    except psycopg2.Error as e:
        if e.pgcode == '23503':  # foreign_key_violation
            print(f"Cannot delete user: {e.pgerror}")
            print("Suggestion: Use soft delete instead")

            # Attempt soft delete
            cursor.execute(
                "UPDATE users SET is_active = false WHERE id = %s",
                (user_id,)
            )
            conn.commit()
            print("User soft-deleted successfully")
        else:
            print(f"Unexpected error: {e}")
        conn.rollback()

-- ============================================================================
-- Example 8: Re-activate soft-deleted user (if needed)
-- ============================================================================
-- If a departed employee returns to company
UPDATE users
SET is_active = true,
    updated_at = NOW()
WHERE id = 5;

-- ============================================================================
-- Example 9: Operator traceability query (Quality investigation)
-- ============================================================================
-- "Which operator processed serial ABC123 at the polishing step?"
SELECT
    s.serial_number,
    p.process_name_ko,
    u.username,
    u.full_name,
    pd.created_at AS operation_time,
    pd.result_value,
    pd.result_status
FROM serials s
JOIN process_data pd ON s.id = pd.serial_id
JOIN processes p ON pd.process_id = p.id
JOIN users u ON pd.operator_id = u.id
WHERE s.serial_number = 'ABC123'
  AND p.process_name_en = 'Wafer Lapping'
ORDER BY pd.created_at;

-- Result:
-- serial_number | process_name_ko | username      | full_name    | operation_time      | result_value | result_status
-- --------------+-----------------+---------------+--------------+--------------------+--------------+---------------
-- ABC123        | 웨이퍼 연마      | kim.operator  | Kim Young-ho | 2025-11-10 10:30:00 | 5.2          | PASS
--
-- This query REQUIRES operator record to exist (cannot delete kim.operator)

-- ============================================================================
-- Example 10: Audit query - Find users safe to delete
-- ============================================================================
-- Users with no production history can be safely hard-deleted
SELECT
    u.id,
    u.username,
    u.full_name,
    u.role,
    u.is_active,
    u.created_at,
    COUNT(pd.id) AS execution_count
FROM users u
LEFT JOIN process_data pd ON u.id = pd.operator_id
GROUP BY u.id, u.username, u.full_name, u.role, u.is_active, u.created_at
HAVING COUNT(pd.id) = 0
ORDER BY u.created_at DESC;

-- Users in this result can be safely hard-deleted (but soft delete is still recommended)

*/

-- ============================================================================
-- Index Recommendations
-- ============================================================================
/*

-- Ensure fast execution count query
CREATE INDEX IF NOT EXISTS idx_process_data_operator_id
ON process_data(operator_id);

-- Composite index for operator activity analysis
CREATE INDEX IF NOT EXISTS idx_process_data_operator_created
ON process_data(operator_id, created_at DESC);

-- Index for soft delete queries
CREATE INDEX IF NOT EXISTS idx_users_active
ON users(is_active, updated_at DESC)
WHERE is_active = false;

-- Composite index for user role queries
CREATE INDEX IF NOT EXISTS idx_users_role_active
ON users(role, is_active);

*/

-- ============================================================================
-- Related Business Rules
-- ============================================================================
/*

1. User Lifecycle Management:
   - CREATE: New employee onboarding
   - ACTIVE: Current employee (is_active = true)
   - INACTIVE: Departed employee (is_active = false, CANNOT hard delete)
   - DELETE: Only allowed for test accounts with no production history

2. Role-Based Access Control (RBAC):
   - ADMIN: Can soft-delete users, cannot hard-delete users with history
   - SUPERVISOR: Can deactivate workers in their department
   - WORKER: Cannot delete any users
   - SYSTEM: Can perform cleanup of test accounts (execution_count = 0)

3. Compliance Requirements:
   - ISO 9001: Operator traceability for all manufactured products
   - FDA 21 CFR Part 11: Electronic records must identify operator
   - GDPR: User data can be anonymized but production records must remain

4. Data Retention Policy:
   - Production records: Retain for 10 years (or product lifetime)
   - User records: Retain as long as production records reference them
   - Audit logs: Retain for 3 years minimum

*/
