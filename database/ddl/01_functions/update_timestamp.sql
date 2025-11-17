-- =============================================================================
-- Function: update_timestamp()
-- Description: Automatically updates the updated_at column to NOW()
-- Usage: Called by BEFORE UPDATE triggers on all entities with updated_at
-- Returns: NEW record with updated timestamp
-- Database: PostgreSQL 14+
-- =============================================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Set the updated_at column to the current timestamp
    -- This ensures accurate tracking of when records are modified
    NEW.updated_at := NOW();

    -- Return the modified NEW record
    -- This allows the UPDATE operation to proceed with the new timestamp
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Function Comments
-- =============================================================================
COMMENT ON FUNCTION update_timestamp() IS
'Trigger function that automatically sets updated_at to NOW() on UPDATE operations.
Used across all entities: product_models, lots, serials, processes, users.';

-- =============================================================================
-- Usage Example:
--
-- CREATE TRIGGER trg_product_models_updated_at
-- BEFORE UPDATE ON product_models
-- FOR EACH ROW
-- EXECUTE FUNCTION update_timestamp();
-- =============================================================================
