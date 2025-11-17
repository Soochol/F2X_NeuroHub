-- ============================================================================
-- Function: log_audit_event()
-- Description: Automatically logs all CREATE/UPDATE/DELETE operations to audit_logs table
-- Usage: Attach as AFTER trigger to tables requiring audit trail
-- PostgreSQL Version: 14+
-- ============================================================================
--
-- Purpose:
--   - Provides comprehensive audit trail for compliance and security
--   - Captures complete before/after snapshots as JSONB
--   - Reads session variables for user context and client metadata
--   - Supports all DML operations: INSERT, UPDATE, DELETE
--
-- Session Variables (set by application layer):
--   - app.current_user_id (BIGINT): ID of authenticated user
--   - app.client_ip (VARCHAR): Client IP address (IPv4/IPv6)
--   - app.user_agent (TEXT): Client user agent string
--
-- Behavior:
--   - INSERT: Maps to 'CREATE' action, captures new_values only
--   - UPDATE: Maps to 'UPDATE' action, captures old_values and new_values
--   - DELETE: Maps to 'DELETE' action, captures old_values only
--   - Returns NEW for INSERT/UPDATE, OLD for DELETE
--   - Defaults to user_id = 1 (system user) if session variable not set
--
-- Example Trigger Definition:
--   CREATE TRIGGER trg_lots_audit
--   AFTER INSERT OR UPDATE OR DELETE ON lots
--   FOR EACH ROW
--   EXECUTE FUNCTION log_audit_event();
--
-- Example Session Setup:
--   SET app.current_user_id = '123';
--   SET app.client_ip = '192.168.1.100';
--   SET app.user_agent = 'Mozilla/5.0...';
--
-- Dependencies:
--   - audit_logs table (with columns: user_id, entity_type, entity_id,
--     action, old_values, new_values, ip_address, user_agent, created_at)
--   - users table (referenced by user_id)
--
-- Performance Considerations:
--   - row_to_json() conversion is efficient for moderate-sized records
--   - JSONB storage provides compact storage with indexing capability
--   - Consider partitioning audit_logs by created_at for large datasets
--
-- Security Notes:
--   - Audit logs should be restricted to ADMIN role only
--   - Consider excluding sensitive fields from JSONB snapshots
--   - IP and user_agent captured for security forensics
-- ============================================================================

CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER -- Ensures audit insertion succeeds even if user lacks direct INSERT privilege
AS $$
DECLARE
    v_user_id BIGINT;
    v_action VARCHAR(10);
    v_old_values JSONB;
    v_new_values JSONB;
BEGIN
    -- ========================================================================
    -- Step 1: Get current user ID from session variable
    -- ========================================================================
    -- The application layer must set this via: SET app.current_user_id = '<user_id>'
    -- current_setting with 'true' flag returns empty string (not error) if not set
    -- NULLIF converts empty string to NULL, then cast to BIGINT
    BEGIN
        v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;
    EXCEPTION
        WHEN OTHERS THEN
            v_user_id := NULL;
    END;

    -- ========================================================================
    -- Step 2: Determine action type and capture data snapshots
    -- ========================================================================
    CASE TG_OP
        WHEN 'INSERT' THEN
            v_action := 'CREATE';
            v_old_values := NULL;
            v_new_values := row_to_json(NEW)::JSONB;

        WHEN 'UPDATE' THEN
            v_action := 'UPDATE';
            v_old_values := row_to_json(OLD)::JSONB;
            v_new_values := row_to_json(NEW)::JSONB;

        WHEN 'DELETE' THEN
            v_action := 'DELETE';
            v_old_values := row_to_json(OLD)::JSONB;
            v_new_values := NULL;

        ELSE
            -- This should never happen, but handle gracefully
            RAISE WARNING 'Unexpected trigger operation: %', TG_OP;
            RETURN COALESCE(NEW, OLD);
    END CASE;

    -- ========================================================================
    -- Step 3: Insert audit log entry
    -- ========================================================================
    -- COALESCE(v_user_id, 1): Default to system user (id=1) if not set
    -- TG_TABLE_NAME: Built-in trigger variable containing table name
    -- COALESCE(NEW.id, OLD.id): Get entity_id from whichever record exists
    -- current_setting with 'true': Returns empty string if not set (graceful)
    BEGIN
        INSERT INTO audit_logs (
            user_id,
            entity_type,
            entity_id,
            action,
            old_values,
            new_values,
            ip_address,
            user_agent,
            created_at
        ) VALUES (
            COALESCE(v_user_id, 1), -- Default to system user if not authenticated
            TG_TABLE_NAME,           -- e.g., 'lots', 'serials', 'process_data'
            COALESCE(NEW.id, OLD.id), -- Primary key of affected record
            v_action,                 -- 'CREATE', 'UPDATE', or 'DELETE'
            v_old_values,             -- JSONB snapshot before change (NULL for CREATE)
            v_new_values,             -- JSONB snapshot after change (NULL for DELETE)
            NULLIF(current_setting('app.client_ip', true), ''), -- Client IP
            NULLIF(current_setting('app.user_agent', true), ''), -- User agent
            NOW()                     -- Explicit timestamp for audit log
        );
    EXCEPTION
        WHEN OTHERS THEN
            -- Log error but don't fail the main operation
            -- This ensures data operations succeed even if audit logging fails
            RAISE WARNING 'Failed to insert audit log for %.%: %',
                TG_TABLE_NAME, COALESCE(NEW.id, OLD.id), SQLERRM;
    END;

    -- ========================================================================
    -- Step 4: Return appropriate record
    -- ========================================================================
    -- For DELETE, return OLD (required by PostgreSQL)
    -- For INSERT/UPDATE, return NEW (allows trigger chain to continue)
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;

-- ============================================================================
-- Function Metadata
-- ============================================================================
COMMENT ON FUNCTION log_audit_event() IS
'Audit logging trigger function that captures CREATE/UPDATE/DELETE operations with complete before/after snapshots. Reads session variables: app.current_user_id, app.client_ip, app.user_agent. Designed for AFTER triggers on all critical tables requiring audit trail.';

-- ============================================================================
-- Usage Examples
-- ============================================================================
/*

-- 1. Create audit trigger on lots table
CREATE TRIGGER trg_lots_audit
AFTER INSERT OR UPDATE OR DELETE ON lots
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- 2. Create audit trigger on serials table
CREATE TRIGGER trg_serials_audit
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- 3. Create audit trigger on process_data table
CREATE TRIGGER trg_process_data_audit
AFTER INSERT OR UPDATE OR DELETE ON process_data
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- 4. Set session variables before DML operations (application layer)
BEGIN;
    SET LOCAL app.current_user_id = '123';
    SET LOCAL app.client_ip = '192.168.1.100';
    SET LOCAL app.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';

    -- Perform data operations (automatically logged)
    UPDATE lots SET status = 'COMPLETED' WHERE id = 456;
COMMIT;

-- 5. Query audit history for a specific LOT
SELECT
    al.id,
    u.username,
    al.action,
    al.created_at,
    al.old_values->>'status' AS old_status,
    al.new_values->>'status' AS new_status
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'lots'
  AND al.entity_id = 456
ORDER BY al.created_at DESC;

-- 6. Find who changed a serial's status to FAILED
SELECT
    u.username,
    al.created_at,
    al.ip_address,
    al.old_values->>'status' AS old_status,
    al.new_values->>'status' AS new_status
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'serials'
  AND al.entity_id = 789
  AND al.action = 'UPDATE'
  AND al.new_values->>'status' = 'FAILED';

*/
