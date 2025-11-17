-- =============================================================================
-- Function: prevent_audit_modification()
-- Description: Prevents UPDATE and DELETE operations on audit_logs table
-- Usage: Called by BEFORE UPDATE OR DELETE trigger on audit_logs
-- Returns: Never returns (always raises exception)
-- Database: PostgreSQL 14+
-- =============================================================================

CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Raise an exception to prevent any modification or deletion
    -- Audit logs are immutable for compliance and security requirements
    -- This ensures a trustworthy audit trail that cannot be tampered with
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';

    -- This line will never execute due to the exception above
    -- But is required for proper function syntax
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Function Comments
-- =============================================================================
COMMENT ON FUNCTION prevent_audit_modification() IS
'Trigger function that enforces immutability of audit_logs table.
Prevents UPDATE and DELETE operations to maintain audit trail integrity.
Ensures compliance with regulatory requirements for audit log retention.';

-- =============================================================================
-- Usage Example:
--
-- CREATE TRIGGER trg_audit_logs_immutable
-- BEFORE UPDATE OR DELETE ON audit_logs
-- FOR EACH ROW
-- EXECUTE FUNCTION prevent_audit_modification();
--
-- This trigger ensures that audit logs are append-only and cannot be:
-- - Modified (UPDATE blocked)
-- - Deleted (DELETE blocked)
-- - Only INSERT operations are allowed
-- =============================================================================
