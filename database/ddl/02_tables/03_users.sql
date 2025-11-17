-- =============================================================================
-- DDL Script: users (사용자)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: User authentication and authorization table for system access control
-- Dependencies: None (independent table)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS users CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE users (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Core columns
    username VARCHAR(50) NOT NULL,         -- Unique login username
    email VARCHAR(255) NOT NULL,           -- Unique email address
    password_hash VARCHAR(255) NOT NULL,   -- Bcrypt hashed password
    full_name VARCHAR(255) NOT NULL,       -- User's full name (Korean or English)
    role VARCHAR(20) NOT NULL,             -- User role: ADMIN, MANAGER, WORKER
    department VARCHAR(100),               -- Department or team
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- Account active status

    -- Activity tracking
    last_login_at TIMESTAMP WITH TIME ZONE, -- Last successful login timestamp

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE users
ADD CONSTRAINT pk_users PRIMARY KEY (id);

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
ALTER TABLE users
ADD CONSTRAINT uk_users_username UNIQUE (username);

ALTER TABLE users
ADD CONSTRAINT uk_users_email UNIQUE (email);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Role must be one of the allowed values
ALTER TABLE users
ADD CONSTRAINT chk_users_role
CHECK (role IN ('ADMIN', 'MANAGER', 'WORKER'));

-- Email format validation
ALTER TABLE users
ADD CONSTRAINT chk_users_email_format
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Username minimum length
ALTER TABLE users
ADD CONSTRAINT chk_users_username_length
CHECK (LENGTH(username) >= 3);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Active users lookup
CREATE INDEX idx_users_active
ON users(is_active, role)
WHERE is_active = TRUE;

-- Role-based queries
CREATE INDEX idx_users_role
ON users(role);

-- Department filtering
CREATE INDEX idx_users_department
ON users(department)
WHERE department IS NOT NULL;

-- Last login analysis
CREATE INDEX idx_users_last_login
ON users(last_login_at DESC)
WHERE last_login_at IS NOT NULL;

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- Prevent deletion if user has process data
CREATE TRIGGER trg_users_prevent_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION prevent_user_deletion();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE users IS 'User authentication and authorization table for system access control';
COMMENT ON COLUMN users.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN users.username IS 'Unique login username (minimum 3 characters)';
COMMENT ON COLUMN users.email IS 'Unique email address with format validation';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password (cost factor 12)';
COMMENT ON COLUMN users.full_name IS 'User''s full name (Korean or English)';
COMMENT ON COLUMN users.role IS 'User role: ADMIN (full access), MANAGER (production management), WORKER (operators)';
COMMENT ON COLUMN users.department IS 'Department or team';
COMMENT ON COLUMN users.is_active IS 'Account active status (false for disabled accounts)';
COMMENT ON COLUMN users.last_login_at IS 'Last successful login timestamp';
COMMENT ON COLUMN users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN users.updated_at IS 'Last update timestamp';

-- =============================================================================
-- ROLE DESCRIPTIONS
-- =============================================================================
/*
Role Permissions:
----------------
ADMIN:
  - Full system access
  - Create/modify users
  - Modify master data
  - Access all features
  - View audit logs

MANAGER:
  - Approve rework
  - View all reports
  - Manage LOTs
  - Production oversight
  - Cannot modify master data

WORKER:
  - Execute processes
  - Record process data
  - View assigned work
  - Cannot approve rework
  - Limited report access
*/

-- =============================================================================
-- INITIAL DATA (Optional)
-- =============================================================================
-- Default admin account (password: admin123)
-- IMPORTANT: Change password immediately after first login
/*
INSERT INTO users (username, email, password_hash, full_name, role, department) VALUES
('admin', 'admin@neurohub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', 'System Administrator', 'ADMIN', 'IT'),
('manager1', 'manager1@neurohub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', '김영수', 'MANAGER', 'Production'),
('worker1', 'worker1@neurohub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', '이철민', 'WORKER', 'Assembly'),
('worker2', 'worker2@neurohub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', '박미영', 'WORKER', 'Quality'),
('worker3', 'worker3@neurohub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', '최준호', 'WORKER', 'Testing');
*/

-- =============================================================================
-- PASSWORD HASHING EXAMPLE
-- =============================================================================
/*
-- Python example for generating bcrypt hash:
import bcrypt

password = "admin123"
salt = bcrypt.gensalt(rounds=12)  # Cost factor 12
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
print(password_hash.decode('utf-8'))

-- Verify password:
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2"
bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================